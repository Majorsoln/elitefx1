"""
download_dukascopy_direct.py — kushusha tick data MOJA KWA MOJA kutoka Dukascopy
(datafeed.dukascopy.com, faili za .bi5) bila tools za nje — stdlib + pyarrow tu.

Inaandika Parquet kwenye muundo uleule wa repo (Hive partitions, rejea
config/data_config.yaml -> paths.raw_ticks):

  data/raw/ticks/symbol=SYM/year=YYYY/month=MM/ticks-YYYY-MM.parquet

Columns: ts (TIMESTAMP UTC), bid, ask, bid_volume, ask_volume — zinasomeka na
src/data/* zote (zinatafuta column ya muda kwa jina + bid/ask). Timestamps za
.bi5 tayari ziko UTC (GMT) — hakuna kubadilisha timezone.

Endesha (kutoka root ya repo, kwenye PC yenye internet isiyozuiliwa):
  python scripts/download_dukascopy_direct.py --pairs XAUUSD GBPJPY EURCHF \\
         --start 2016-01 --end 2026-04
  python scripts/download_dukascopy_direct.py --pairs EURUSD --start 2024-01 \\
         --end 2024-02 --workers 4
RESUME: mwezi wenye parquet tayari unarukwa (tumia --force kushusha upya).
Mtandao wa polepole / timeouts: --workers 2 --timeout 60. Script ina preflight
(inasimama mapema mtandao usipofika Dukascopy) na inasimama baada ya miezi 3
mfululizo kufeli — endesha tena tu, resume itaendelea pale ilipoishia.
Self-test (offline, hakuna mtandao): python scripts/download_dukascopy_direct.py --self-test

Muundo wa .bi5 (kwa kila saa, LZMA): rekodi za bytes 20 big-endian —
  uint32 ms (offset ndani ya saa), uint32 ask_points, uint32 bid_points,
  float32 ask_volume, float32 bid_volume.
Bei halisi = points / point_factor (JPY & metali = 1e3, pairs nyingine = 1e5).
Faili tupu (bytes 0) au 404 = hakuna data (weekend/sikukuu) — si hitilafu.
"""
from __future__ import annotations

import argparse
import lzma
import struct
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://datafeed.dukascopy.com/datafeed"
REC = struct.Struct(">IIIff")          # ms, ask_pts, bid_pts, ask_vol, bid_vol
RETRIES = 5                            # backoff 2s, 4s, 8s, 15s, 15s (cap 15s)
TIMEOUT = 30                           # sekunde kwa kila ombi (connect + read)
UA = "Mozilla/5.0 (EliteFX data pipeline)"

# point_factor: bei = points / factor. Rejea metadata ya Dukascopy.
POINT_FACTOR = {
    "XAUUSD": 1_000, "XAGUSD": 1_000, "GBPJPY": 1_000, "USDJPY": 1_000,
    "EURJPY": 1_000, "EURCHF": 100_000, "EURUSD": 100_000, "GBPUSD": 100_000,
    "USDCAD": 100_000, "USDCHF": 100_000, "AUDUSD": 100_000,
    "NZDUSD": 100_000, "EURGBP": 100_000,
}


def point_factor(symbol: str) -> int:
    s = symbol.upper()
    if s in POINT_FACTOR:
        return POINT_FACTOR[s]
    if s.endswith("JPY") or s.startswith(("XAU", "XAG")):
        return 1_000
    return 100_000


def hour_url(symbol: str, dt: datetime) -> str:
    """URL ya saa moja. TAHADHARI: mwezi wa Dukascopy ni 0-based (Jan=00)."""
    return (f"{BASE_URL}/{symbol.upper()}/{dt.year:04d}/{dt.month - 1:02d}/"
            f"{dt.day:02d}/{dt.hour:02d}h_ticks.bi5")


def fetch(url: str, timeout: int = TIMEOUT, retries: int = RETRIES) -> bytes:
    """Shusha URL moja; 404 = hakuna data (b''). Retry na exponential backoff (cap 15s)."""
    last: Exception | None = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
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


def parse_bi5(raw: bytes, hour_start: datetime, factor: int) -> list[tuple]:
    """Rudisha [(ts_epoch_ms, bid, ask, bid_vol, ask_vol), ...] kutoka bytes za .bi5."""
    if not raw:
        return []
    data = lzma.decompress(raw)
    base_ms = int(hour_start.timestamp() * 1000)
    out = []
    for ms, ask_p, bid_p, ask_v, bid_v in REC.iter_unpack(data):
        out.append((base_ms + ms, bid_p / factor, ask_p / factor, bid_v, ask_v))
    return out


def month_hours(year: int, month: int):
    """Datetime (UTC) za kila saa ya mwezi husika."""
    dt = datetime(year, month, 1, tzinfo=timezone.utc)
    while dt.year == year and dt.month == month:
        yield dt
        dt += timedelta(hours=1)


def month_range(start: str, end: str):
    """'2016-01'..'2016-03' -> [(2016,1),(2016,2),(2016,3)]. Inclusive."""
    (y0, m0), (y1, m1) = (map(int, s.split("-")) for s in (start, end))
    if (y0, m0) > (y1, m1):
        raise ValueError(f"--start {start} iko baada ya --end {end}")
    out = []
    y, m = y0, m0
    while (y, m) <= (y1, m1):
        out.append((y, m))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def write_parquet(rows: list[tuple], path: Path) -> None:
    """Andika rows (zilizopangwa kwa ts) kama Parquet — atomically (tmp -> rename)."""
    import pyarrow as pa
    import pyarrow.parquet as pq
    rows.sort(key=lambda r: r[0])
    cols = list(zip(*rows)) if rows else ([], [], [], [], [])
    table = pa.table({
        "ts": pa.array(cols[0], pa.timestamp("ms", tz="UTC")),
        "bid": pa.array(cols[1], pa.float64()),
        "ask": pa.array(cols[2], pa.float64()),
        "bid_volume": pa.array(cols[3], pa.float32()),
        "ask_volume": pa.array(cols[4], pa.float32()),
    })
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".parquet.tmp")
    pq.write_table(table, tmp, compression="zstd")
    tmp.replace(path)


def download_month(symbol: str, year: int, month: int, out_root: Path,
                   workers: int, force: bool, fetcher=fetch) -> tuple[str, int]:
    """Shusha mwezi mmoja wa symbol moja. Rudisha (status, ticks)."""
    path = (out_root / f"symbol={symbol.upper()}" / f"year={year:04d}"
            / f"month={month:02d}" / f"ticks-{year:04d}-{month:02d}.parquet")
    if path.exists() and not force:
        return "SKIP", -1
    now = datetime.now(timezone.utc)
    factor = point_factor(symbol)
    hours = [h for h in month_hours(year, month) if h < now]
    if not hours:
        return "FUTURE", 0
    rows: list[tuple] = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for h, raw in zip(hours, ex.map(lambda h: fetcher(hour_url(symbol, h)), hours)):
            rows.extend(parse_bi5(raw, h, factor))
    write_parquet(rows, path)
    return "OK", len(rows)


def preflight(symbol: str, timeout: int) -> None:
    """Jaribio moja la haraka la mtandao kabla ya kazi 300+: Jumatatu ya zamani
    inayojulikana. Ikishindikana mara 2, inua hitilafu — usisage kazi zote bure."""
    url = hour_url(symbol, datetime(2020, 1, 6, 10, tzinfo=timezone.utc))
    fetch(url, timeout=timeout, retries=1)


def run(pairs, start, end, out_root: Path, workers: int, force: bool,
        timeout: int = TIMEOUT, retries: int = RETRIES) -> int:
    months = month_range(start, end)
    total = len(pairs) * len(months)
    print(f"Dukascopy direct: pairs={','.join(pairs)} | miezi {start}..{end} "
          f"({len(months)}) | kazi {total} | -> {out_root}")
    try:
        preflight(pairs[0], timeout)
    except Exception as e:
        print(f"\nPREFLIGHT IMESHINDIKANA — mtandao haufiki datafeed.dukascopy.com:\n  {e}\n"
              f"Angalia internet/firewall/VPN yako kisha ujaribu tena "
              f"(au ongeza --timeout, mf. --timeout 60).")
        return 2
    fetcher = lambda u: fetch(u, timeout=timeout, retries=retries)
    done = failed = streak = 0
    t0 = time.time()
    for symbol in pairs:
        for (y, m) in months:
            done += 1
            tag = f"[{done:>4d}/{total}] {symbol} {y:04d}-{m:02d}"
            try:
                status, n = download_month(symbol, y, m, out_root, workers, force,
                                           fetcher=fetcher)
            except Exception as e:
                failed += 1
                streak += 1
                print(f"{tag}: HITILAFU — {e}", flush=True)
                if streak >= 3:
                    print(f"\nNIMESIMAMA: miezi {streak} mfululizo imeshindikana — "
                          f"mtandao una tatizo. Endesha tena baadaye (resume itaruka "
                          f"miezi iliyokamilika); jaribu --workers 2 --timeout 60.")
                    return 1
                continue
            streak = 0
            if status == "SKIP":
                print(f"{tag}: ipo tayari (ruka; --force kushusha upya)", flush=True)
            elif status == "FUTURE":
                print(f"{tag}: mwezi ujao — hakuna data bado", flush=True)
            else:
                print(f"{tag}: ticks {n:,} | dakika {(time.time() - t0) / 60:.1f}",
                      flush=True)
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

    # 1) URL: mwezi 0-based
    u = hour_url("xauusd", datetime(2024, 1, 5, 10, tzinfo=timezone.utc))
    check("URL mwezi 0-based + uppercase",
          u == f"{BASE_URL}/XAUUSD/2024/00/05/10h_ticks.bi5")

    # 2) point factors
    check("point_factor XAUUSD=1e3", point_factor("XAUUSD") == 1_000)
    check("point_factor GBPJPY=1e3 (rule ya JPY)", point_factor("CADJPY") == 1_000
          and point_factor("GBPJPY") == 1_000)
    check("point_factor EURCHF=1e5", point_factor("EURCHF") == 100_000)

    # 3) parse_bi5: rekodi 2 za kutengeneza — ask kabla ya bid ndani ya .bi5
    h0 = datetime(2024, 1, 5, 10, tzinfo=timezone.utc)
    payload = REC.pack(250, 2035123, 2035013, 1.5, 2.25) + \
              REC.pack(1000, 2035200, 2035100, 0.5, 0.75)
    ticks = parse_bi5(lzma.compress(payload), h0, 1_000)
    base = int(h0.timestamp() * 1000)
    check("parse_bi5: rekodi 2", len(ticks) == 2)
    check("parse_bi5: ts=hour_start+ms", ticks[0][0] == base + 250
          and ticks[1][0] == base + 1000)
    check("parse_bi5: bid<ask + scaling ya 1e3",
          ticks[0][1] == 2035.013 and ticks[0][2] == 2035.123)
    check("parse_bi5: volumes (bid_vol,ask_vol)",
          ticks[0][3] == 2.25 and ticks[0][4] == 1.5)
    check("parse_bi5: bytes tupu = hakuna ticks", parse_bi5(b"", h0, 1_000) == [])

    # 4) fetch: retries zikiisha -> RuntimeError yenye URL (bila mtandao halisi)
    real_urlopen = urllib.request.urlopen
    urllib.request.urlopen = lambda *a, **k: (_ for _ in ()).throw(OSError("mock down"))
    try:
        fetch("https://example.invalid/x.bi5", timeout=1, retries=0)
        check("fetch: inainua hitilafu retries zikiisha", False)
    except RuntimeError as e:
        check("fetch: inainua hitilafu retries zikiisha",
              "x.bi5" in str(e) and "mock down" in str(e))
    finally:
        urllib.request.urlopen = real_urlopen

    # 5) month_range inclusive + kuvuka mwaka
    check("month_range 2016-11..2017-02",
          month_range("2016-11", "2017-02") == [(2016, 11), (2016, 12), (2017, 1), (2017, 2)])

    # 6) end-to-end ya mwezi mmoja na fetcher bandia (hakuna mtandao) + resume
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        fake = lzma.compress(REC.pack(0, 108500, 108450, 1.0, 1.0))
        calls = []

        def fake_fetch(url):
            calls.append(url)
            return fake if url.endswith("00h_ticks.bi5") else b""

        st, n = download_month("EURCHF", 2016, 1, root, workers=4,
                               force=False, fetcher=fake_fetch)
        p = root / "symbol=EURCHF/year=2016/month=01/ticks-2016-01.parquet"
        check("download_month: OK + parquet ipo", st == "OK" and p.exists())
        check("download_month: masaa 744 ya Jan yameombwa", len(calls) == 744)
        check("download_month: ticks 31 (siku 31 x saa 00)", n == 31)
        import pyarrow.parquet as pq
        # schema ya faili lenyewe (read_table ingeongeza partition cols za Hive)
        t = pq.ParquetFile(p).read()
        check("parquet: columns sahihi",
              t.column_names == ["ts", "bid", "ask", "bid_volume", "ask_volume"])
        check("parquet: scaling ya 1e5 (EURCHF)",
              t.column("bid")[0].as_py() == 1.0845)
        st2, _ = download_month("EURCHF", 2016, 1, root, workers=4,
                                force=False, fetcher=fake_fetch)
        check("resume: mwezi uliopo unarukwa", st2 == "SKIP")

    print(f"\nSELF-TEST: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Shusha ticks za Dukascopy (bi5 -> Parquet)")
    ap.add_argument("--pairs", nargs="+", metavar="SYM", help="mf. XAUUSD GBPJPY EURCHF")
    ap.add_argument("--start", metavar="YYYY-MM", help="mwezi wa kwanza (inclusive)")
    ap.add_argument("--end", metavar="YYYY-MM", help="mwezi wa mwisho (inclusive)")
    ap.add_argument("--out", default=None,
                    help="root ya output (default: paths.raw_ticks ya data_config.yaml)")
    ap.add_argument("--workers", type=int, default=8, help="threads za kushusha (default 8)")
    ap.add_argument("--timeout", type=int, default=TIMEOUT,
                    help=f"sekunde kwa kila ombi (default {TIMEOUT}; mtandao wa polepole: 60)")
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
               a.workers, a.force, timeout=a.timeout, retries=a.retries)


if __name__ == "__main__":
    sys.exit(main())
