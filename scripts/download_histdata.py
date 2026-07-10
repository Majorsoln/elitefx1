"""
download_histdata.py — PROVIDER MBADALA: kushusha tick data kutoka HistData.com
(bure, hakuna account) pale Dukascopy isipofikika (ISP/firewall).

Inaandika Parquet kwenye muundo ULEULE wa scripts/download_dukascopy_direct.py
(Hive partitions za config/data_config.yaml -> paths.raw_ticks):

  data/raw/ticks/symbol=SYM/year=YYYY/month=MM/ticks-YYYY-MM.parquet

Columns zilezile: ts (TIMESTAMP UTC), bid, ask, bid_volume, ask_volume.
TOFAUTI MUHIMU na Dukascopy:
  • HistData HAINA tick volume — bid_volume/ask_volume zinaandikwa 0.0.
    Tools zinazotumia volume kama proxy (check_tick_volume, volume_information,
    adaptive_volume_bars) hazitafanya kazi na data hii; bei (bid/ask) ziko sawa.
  • Timestamps za HistData ziko EST (UTC-5, BILA DST) — tunaconvert UTC (+5h).
  • ZIP moja kwa mwezi (nyepesi/haraka kuliko masaa 744 ya Dukascopy).

Endesha (kutoka root ya repo):
  python scripts/download_histdata.py --pairs XAUUSD GBPJPY EURCHF \\
         --start 2016-01 --end 2026-04
RESUME: mwezi wenye parquet tayari unarukwa (miezi iliyoshushwa na script ya
Dukascopy pia inarukwa — muundo ni mmoja). --force kushusha upya.
Self-test (offline): python scripts/download_histdata.py --self-test
"""
from __future__ import annotations

import argparse
import io
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from download_dukascopy_direct import (  # noqa: E402 — schema/muundo mmoja
    REPO_ROOT, RETRIES, TIMEOUT, UA, month_range, write_parquet)

SITE = "https://www.histdata.com"
PAGE = SITE + "/download-free-forex-historical-data/?/ascii/tick-data-quotes/{pair}/{year}/{month}"
GET_PHP = SITE + "/get.php"
EST_OFFSET_MS = 5 * 3600 * 1000        # EST (UTC-5, hakuna DST) -> UTC
_INPUT_RE = re.compile(r"<input\b[^>]*>", re.I)
_ATTR_RE = re.compile(r'(\w+)\s*=\s*"([^"]*)"')


def month_page_url(symbol: str, year: int, month: int) -> str:
    """URL ya ukurasa wa mwezi. TAHADHARI: mwezi BILA sifuri mbele (Jan=1)."""
    return PAGE.format(pair=symbol.lower(), year=year, month=month)


def http(url: str, data: dict | None = None, referer: str | None = None,
         timeout: int = TIMEOUT, retries: int = RETRIES) -> bytes:
    """GET (data=None) au POST (form-encoded). 404 = b''. Retry + backoff (cap 15s)."""
    headers = {"User-Agent": UA}
    if referer:
        headers["Referer"] = referer
    body = urllib.parse.urlencode(data).encode() if data else None
    last: Exception | None = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, data=body, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return b""
            last = e
        except Exception as e:
            last = e
        if attempt < retries:
            time.sleep(min(2 ** (attempt + 1), 15))
    raise RuntimeError(f"{url}: imeshindikana baada ya majaribio {retries + 1} — {last}")


def parse_form(html: str) -> dict | None:
    """Chukua hidden inputs za form ya download (tk, date, datemonth, platform,
    timeframe, fxpair). None = form haipo (mwezi haupatikani kwenye HistData)."""
    fields = {}
    for tag in _INPUT_RE.findall(html):
        attrs = dict(_ATTR_RE.findall(tag))
        if "name" in attrs:
            fields[attrs["name"]] = attrs.get("value", "")
    return fields if "tk" in fields else None


def parse_csv(raw: bytes) -> list[tuple]:
    """Rudisha [(ts_epoch_ms UTC, bid, ask, 0.0, 0.0), ...] kutoka CSV ya HistData.
    Line: '20160103 170014237,1060.43,1060.93,0' — datetime EST, bid, ask, vol(0)."""
    rows: list[tuple] = []
    day_cache: dict[bytes, int] = {}
    for line in raw.split(b"\n"):
        line = line.strip()
        if not line:
            continue
        dt_s, bid_s, ask_s = line.split(b",")[:3]
        d, t = dt_s.split(b" ")
        base = day_cache.get(d)
        if base is None:
            base = int(datetime(int(d[:4]), int(d[4:6]), int(d[6:8]),
                                tzinfo=timezone.utc).timestamp() * 1000)
            day_cache[d] = base
        ms = ((int(t[:2]) * 60 + int(t[2:4])) * 60 + int(t[4:6])) * 1000 + int(t[6:9])
        rows.append((base + ms + EST_OFFSET_MS, float(bid_s), float(ask_s), 0.0, 0.0))
    return rows


def unzip_csv(blob: bytes) -> bytes:
    """Toa CSV ya kwanza ndani ya ZIP ya HistData."""
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        names = [n for n in z.namelist() if n.lower().endswith(".csv")]
        if not names:
            raise RuntimeError(f"ZIP haina CSV (ina: {z.namelist()})")
        return z.read(names[0])


def download_month(symbol: str, year: int, month: int, out_root: Path,
                   force: bool, fetcher=http) -> tuple[str, int]:
    """Shusha mwezi mmoja (ZIP moja). Rudisha (status, ticks)."""
    path = (out_root / f"symbol={symbol.upper()}" / f"year={year:04d}"
            / f"month={month:02d}" / f"ticks-{year:04d}-{month:02d}.parquet")
    if path.exists() and not force:
        return "SKIP", -1
    page_url = month_page_url(symbol, year, month)
    fields = parse_form(fetcher(page_url).decode("utf-8", errors="ignore"))
    if fields is None:
        return "HAKUNA", 0                 # HistData haina mwezi huu (bado/kabisa)
    blob = fetcher(GET_PHP, data=fields, referer=page_url)
    if not blob.startswith(b"PK"):
        raise RuntimeError(f"{symbol} {year}-{month:02d}: jibu si ZIP "
                           f"(bytes {len(blob)}) — tovuti imebadilika au throttling")
    rows = parse_csv(unzip_csv(blob))
    write_parquet(rows, path)
    return "OK", len(rows)


def preflight(timeout: int, fetcher=http) -> None:
    """Ukurasa mmoja unaojulikana — usisage kazi zote mtandao ukiwa umefungwa."""
    html = fetcher(month_page_url("EURUSD", 2020, 1), timeout=timeout,
                   retries=1).decode("utf-8", errors="ignore")
    if parse_form(html) is None:
        raise RuntimeError("ukurasa umefunguka lakini form ya download haipo — "
                           "tovuti imebadilika au IP imezuiliwa")


def run(pairs, start, end, out_root: Path, force: bool,
        timeout: int = TIMEOUT, retries: int = RETRIES) -> int:
    months = month_range(start, end)
    total = len(pairs) * len(months)
    print(f"HistData: pairs={','.join(pairs)} | miezi {start}..{end} "
          f"({len(months)}) | kazi {total} | -> {out_root}\n"
          f"KUMBUKA: HistData haina tick volume (bid/ask_volume=0) — tools za "
          f"volume-proxy hazitatumika na data hii.")
    try:
        preflight(timeout)
    except Exception as e:
        print(f"\nPREFLIGHT IMESHINDIKANA — mtandao haufiki www.histdata.com:\n  {e}\n"
              f"Hatua: fungua www.histdata.com kwenye browser; jaribu VPN/hotspot; "
              f"--timeout 90.")
        return 2
    fetcher = lambda url, **kw: http(url, timeout=kw.pop("timeout", timeout),
                                     retries=kw.pop("retries", retries), **kw)
    done = failed = streak = 0
    t0 = time.time()
    for symbol in pairs:
        for (y, m) in months:
            done += 1
            tag = f"[{done:>4d}/{total}] {symbol} {y:04d}-{m:02d}"
            try:
                status, n = download_month(symbol, y, m, out_root, force,
                                           fetcher=fetcher)
            except Exception as e:
                failed += 1
                streak += 1
                print(f"{tag}: HITILAFU — {e}", flush=True)
                if streak >= 3:
                    print(f"\nNIMESIMAMA: miezi {streak} mfululizo imeshindikana — "
                          f"mtandao/tovuti ina tatizo. Endesha tena baadaye "
                          f"(resume itaruka miezi iliyokamilika).")
                    return 1
                time.sleep(5)
                continue
            streak = 0
            if status == "SKIP":
                print(f"{tag}: ipo tayari (ruka; --force kushusha upya)", flush=True)
            elif status == "HAKUNA":
                print(f"{tag}: HistData haina mwezi huu (bado haujatolewa?)", flush=True)
            else:
                print(f"{tag}: ticks {n:,} | dakika {(time.time() - t0) / 60:.1f}",
                      flush=True)
                time.sleep(1)              # adabu kwa server — ZIP moja/sekunde
    if failed:
        print(f"\nIMEKAMILIKA NA HITILAFU: miezi {failed}/{total} imeshindikana — "
              f"endesha tena (resume itaruka iliyokamilika).")
        return 1
    print(f"\nIMEKAMILIKA: kazi {total} | dakika {(time.time() - t0) / 60:.1f}")
    return 0


# ----------------------------- self-test (offline) -----------------------------
def self_test() -> int:
    import tempfile
    ok = True

    def check(name, cond):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        ok = ok and cond

    # 1) URL ya ukurasa: mwezi BILA sifuri mbele, pair lowercase
    check("month_page_url: Jan=1, lowercase",
          month_page_url("XAUUSD", 2016, 1).endswith("/xauusd/2016/1"))

    # 2) parse_form: attrs kwa mpangilio wowote; bila tk -> None
    html = ('<form id="file_down" action="get.php" method="post">'
            '<input value="abc123" id="tk" name="tk" type="hidden">'
            '<input type="hidden" name="date" value="2016">'
            '<input name="datemonth" value="201601" type="hidden">'
            '<input name="platform" value="ASCII" type="hidden">'
            '<input name="timeframe" value="T" type="hidden">'
            '<input name="fxpair" value="XAUUSD" type="hidden"></form>')
    f = parse_form(html)
    check("parse_form: fields 6 + tk", f is not None and f["tk"] == "abc123"
          and f["datemonth"] == "201601" and f["timeframe"] == "T")
    check("parse_form: bila tk -> None", parse_form("<html>hakuna</html>") is None)

    # 3) parse_csv: EST(UTC-5) -> UTC (+5h), bid/ask, volume 0
    csv = b"20160103 170014237,1060.43,1060.93,0\r\n20160104 000000000,1061.00,1061.50,0\n"
    rows = parse_csv(csv)
    exp0 = int(datetime(2016, 1, 3, 22, 0, 14, 237000, tzinfo=timezone.utc)
               .timestamp() * 1000)                       # 17:00 EST = 22:00 UTC
    exp1 = int(datetime(2016, 1, 4, 5, 0, tzinfo=timezone.utc).timestamp() * 1000)
    check("parse_csv: rekodi 2", len(rows) == 2)
    check("parse_csv: EST->UTC (+5h) na ms", rows[0][0] == exp0 and rows[1][0] == exp1)
    check("parse_csv: bid/ask + volume 0",
          rows[0][1] == 1060.43 and rows[0][2] == 1060.93
          and rows[0][3] == 0.0 and rows[0][4] == 0.0)

    # 4) unzip_csv
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("DAT_ASCII_XAUUSD_T_201601.csv", csv)
    check("unzip_csv: inatoa CSV", unzip_csv(buf.getvalue()) == csv)

    # 5) end-to-end ya mwezi mmoja na fetcher bandia (page -> zip) + resume
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        posts = []

        def fake_fetch(url, data=None, referer=None, **kw):
            if data is None:
                return html.encode()
            posts.append((url, data, referer))
            return buf.getvalue()

        st, n = download_month("XAUUSD", 2016, 1, root, force=False,
                               fetcher=fake_fetch)
        p = root / "symbol=XAUUSD/year=2016/month=01/ticks-2016-01.parquet"
        check("download_month: OK + parquet ipo", st == "OK" and n == 2 and p.exists())
        check("download_month: POST get.php na tk + Referer",
              posts and posts[0][0] == GET_PHP and posts[0][1]["tk"] == "abc123"
              and posts[0][2] is not None)
        import pyarrow.parquet as pq
        t = pq.ParquetFile(p).read()
        check("parquet: columns zilezile za dukascopy",
              t.column_names == ["ts", "bid", "ask", "bid_volume", "ask_volume"])
        st2, _ = download_month("XAUUSD", 2016, 1, root, force=False,
                                fetcher=fake_fetch)
        check("resume: mwezi uliopo unarukwa", st2 == "SKIP")

        def no_form_fetch(url, data=None, **kw):
            return b"<html>launch page tu</html>"

        st3, _ = download_month("XAUUSD", 2030, 1, root, force=False,
                                fetcher=no_form_fetch)
        check("mwezi usiopo HistData -> HAKUNA (si hitilafu)", st3 == "HAKUNA")

    print(f"\nSELF-TEST: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Shusha ticks za HistData.com (ZIP/mwezi -> Parquet) — mbadala wa Dukascopy")
    ap.add_argument("--pairs", nargs="+", metavar="SYM", help="mf. XAUUSD GBPJPY EURCHF")
    ap.add_argument("--start", metavar="YYYY-MM", help="mwezi wa kwanza (inclusive)")
    ap.add_argument("--end", metavar="YYYY-MM", help="mwezi wa mwisho (inclusive)")
    ap.add_argument("--out", default=None,
                    help="root ya output (default: paths.raw_ticks ya data_config.yaml)")
    ap.add_argument("--timeout", type=int, default=TIMEOUT,
                    help=f"sekunde kwa kila ombi (default {TIMEOUT})")
    ap.add_argument("--retries", type=int, default=RETRIES,
                    help=f"majaribio ya ziada kwa kila URL (default {RETRIES})")
    ap.add_argument("--force", action="store_true", help="shusha upya hata kama parquet ipo")
    ap.add_argument("--self-test", action="store_true", help="test za offline, hakuna mtandao")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if not (a.pairs and a.start and a.end):
        ap.error("--pairs, --start na --end zinahitajika (au --self-test)")
    if a.out:
        out_root = Path(a.out)
    else:
        try:
            import yaml
            with open(REPO_ROOT / "config" / "data_config.yaml", encoding="utf-8") as f:
                out_root = REPO_ROOT / yaml.safe_load(f)["paths"]["raw_ticks"]
        except ModuleNotFoundError:
            out_root = REPO_ROOT / "data" / "raw" / "ticks"
    return run([p.upper() for p in a.pairs], a.start, a.end, out_root,
               a.force, timeout=a.timeout, retries=a.retries)


if __name__ == "__main__":
    sys.exit(main())
