"""
check_tick_volume.py — Kagua kama TICK VOLUME ipo kwenye raw ticks (mwezi mmoja).

Kusudi: kuthibitisha kama `bid_vol`/`ask_vol` (tick volume) zipo NA zina thamani
(sio null/sifuri) kwa pair + mwezi uliochaguliwa. Inasoma raw Parquet moja kwa
moja (Hive: symbol=*/year=*/.../*.parquet) kwa DuckDB, haina haja ya candles.

Endesha (PC ya Japhet, root ya repo):
  python src/data/check_tick_volume.py --symbol EURUSD --month 2024-01
  python src/data/check_tick_volume.py --month 2024-01            # pair ya kwanza
  python src/data/check_tick_volume.py --symbol EURUSD --month 2024-01 --out reports/vol_check.txt

Self-test (popote, bila data — hujenga parquet ndogo ya majaribio):
  python src/data/check_tick_volume.py --self-test
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import duckdb
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config" / "data_config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _posix(p: Path) -> str:
    return str(p).replace("\\", "/")


def detect(con, src):
    """Rudisha (cols, time_col, vol_cols). vol_cols = columns za volume (bila imbalance)."""
    schema = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{src}', union_by_name => true)").fetchall()
    cols = [r[0] for r in schema]
    time_col = next((c for c in cols if any(k in c.lower() for k in ("time", "date", "ts", "stamp"))), None)
    vol_cols = [c for c in cols if "vol" in c.lower() and "imbalance" not in c.lower()]
    return cols, time_col, vol_cols


def summarize(con, src, month, time_col, vol_cols, out=sys.stdout):
    """Onyesha breakdown ya kila siku + muhtasari. Rudisha (n_ticks, n_with_vol)."""
    p = lambda *a: print(*a, file=out)
    con.execute("SET TimeZone='UTC'")
    # jumla ya volume kwa kila tick (coalesce -> 0), na vol per-column
    total_vol = " + ".join(f'COALESCE("{c}", 0)' for c in vol_cols) if vol_cols else "0"
    per_col = ", ".join(f'SUM(COALESCE("{c}",0)) AS "sum_{c}"' for c in vol_cols)
    sel_extra = (", " + per_col) if vol_cols else ""
    # NB: raw ina partition columns (year/month/day); tunatumia GROUP BY 1 (ordinal)
    # na alias 'dt' ili kuepuka mgongano na column halisi 'day'.
    q = f"""
        SELECT strftime("{time_col}", '%Y-%m-%d')                       AS dt,
               COUNT(*)                                                 AS ticks,
               SUM(CASE WHEN ({total_vol}) > 0 THEN 1 ELSE 0 END)       AS ticks_with_vol
               {sel_extra}
        FROM read_parquet('{src}', union_by_name => true)
        WHERE strftime("{time_col}", '%Y-%m') = '{month}'
        GROUP BY 1 ORDER BY 1
    """
    rows = con.execute(q).fetchall()
    if not rows:
        p(f"  (Hakuna ticks kwa {month} kwenye faili hizi — angalia mwezi/njia.)")
        return 0, 0

    hdr = ["day", "ticks", "ticks_w/vol", "%vol"] + [f"Σ{c}" for c in vol_cols]
    p("  " + " | ".join(f"{h:>12}" for h in hdr))
    n_ticks = n_vol = 0
    for r in rows:
        day, ticks, tw = r[0], int(r[1]), int(r[2])
        n_ticks += ticks; n_vol += tw
        pct = (tw / ticks * 100) if ticks else 0
        cells = [f"{day:>12}", f"{ticks:>12,}", f"{tw:>12,}", f"{pct:>11.1f}%"]
        for k in range(len(vol_cols)):
            cells.append(f"{int(r[3+k]):>12,}")
        p("  " + " | ".join(cells))
    return n_ticks, n_vol


def find_src(base: Path, year: str):
    """Glob ya parquet — jaribu year= kwanza (kasi), kisha symbol nzima."""
    if (base / f"year={year}").exists():
        g = base / f"year={year}" / "**" / "*.parquet"
        if list((base / f"year={year}").rglob("*.parquet")):
            return _posix(g)
    if list(base.rglob("*.parquet")):
        return _posix(base / "**" / "*.parquet")
    return None


def run(symbol, month, out_path):
    cfg = load_config()
    raw = REPO_ROOT / cfg["paths"]["raw_ticks"]
    base = raw / f"symbol={symbol}"
    out = open(out_path, "w", encoding="utf-8") if out_path else sys.stdout
    p = lambda *a: print(*a, file=out)
    try:
        if not base.exists():
            p(f"HITILAFU: '{base}' haipo. Endesha kutoka root ya repo; data iko "
              f"{cfg['paths']['raw_ticks']}/symbol={symbol}/"); return 1
        year = month.split("-")[0]
        src = find_src(base, year)
        if not src:
            p(f"HITILAFU: sijapata faili .parquet chini ya symbol={symbol}"); return 1
        con = duckdb.connect()
        cols, time_col, vol_cols = detect(con, src)
        p("=" * 64)
        p(f"TICK VOLUME CHECK — {symbol}  |  mwezi {month}")
        p("=" * 64)
        p(f"Columns: {', '.join(cols)}")
        p(f"Time column: {time_col!r}")
        p(f"Volume columns zilizopatikana: {vol_cols if vol_cols else '(HAKUNA!)'}")
        if not time_col:
            p("HITILAFU: sijapata column ya muda — siwezi kuchuja mwezi."); return 1
        p("")
        n_ticks, n_vol = summarize(con, src, month, time_col, vol_cols, out=out)
        p("")
        if not vol_cols:
            p("⛔ HITIMISHO: Hakuna column ya volume kabisa kwenye raw -> TICK VOLUME HAIPO.")
        elif n_ticks == 0:
            p("⚪ HITIMISHO: Hakuna ticks kwa mwezi huu (haiwezekani kuhukumu volume).")
        elif n_vol == 0:
            p(f"⛔ HITIMISHO: Volume columns zipo {vol_cols} LAKINI zote ni 0/null kwa "
              f"{month} -> tick volume HAIPO kivitendo.")
        else:
            pct = n_vol / n_ticks * 100
            verdict = "✅ TICK VOLUME IPO" if pct >= 50 else "⚠️ TICK VOLUME PUNGUFU"
            p(f"{verdict}: ticks {n_ticks:,} | zenye volume {n_vol:,} ({pct:.1f}%) kwa {month}.")
        if out_path:
            print(f"Imeandikwa: {out_path}")
        return 0
    finally:
        if out_path:
            out.close()


def self_test():
    """Jenga parquet ndogo yenye bid_vol/ask_vol -> thibitisha detect + summarize."""
    import tempfile, datetime as dt
    con = duckdb.connect()
    con.execute("SET TimeZone='UTC'")
    d = Path(tempfile.mkdtemp()) / "ticks.parquet"
    # siku 2 za 2024-03, ticks 3/siku; bid_vol/ask_vol > 0.
    # NB: tunaweka partition columns (day/month/year) kama data halisi ya Hive
    # ili kunasa mgongano wa GROUP BY (column 'day' dhidi ya alias).
    con.execute(f"""
        COPY (
          SELECT * FROM (VALUES
            (TIMESTAMPTZ '2024-03-01 10:00:00+00', 1.10, 1.11, 2.0, 3.0, 1, 3, 2024),
            (TIMESTAMPTZ '2024-03-01 10:01:00+00', 1.10, 1.11, 1.0, 1.0, 1, 3, 2024),
            (TIMESTAMPTZ '2024-03-01 10:02:00+00', 1.10, 1.11, 0.0, 0.0, 1, 3, 2024),
            (TIMESTAMPTZ '2024-03-02 09:00:00+00', 1.12, 1.13, 4.0, 5.0, 2, 3, 2024),
            (TIMESTAMPTZ '2024-04-01 09:00:00+00', 1.12, 1.13, 9.0, 9.0, 1, 4, 2024)
          ) t(timestamp, bid, ask, bid_vol, ask_vol, day, month, year)
        ) TO '{_posix(d)}' (FORMAT PARQUET)
    """)
    src = _posix(d)
    cols, time_col, vol_cols = detect(con, src)
    print(f"detected: time={time_col!r} vol={vol_cols}")
    n_ticks, n_vol = summarize(con, src, "2024-03", time_col, vol_cols)
    ok = (time_col == "timestamp" and set(vol_cols) == {"bid_vol", "ask_vol"}
          and n_ticks == 4 and n_vol == 3)   # mwezi 03: ticks 4, zenye vol>0 = 3
    print(f"n_ticks={n_ticks} (tarajio 4) | n_with_vol={n_vol} (tarajio 3)")
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="Kagua tick volume kwa mwezi mmoja")
    ap.add_argument("--symbol", default=None, help="pair (default: ya kwanza kwenye config)")
    ap.add_argument("--month", default=None, help="YYYY-MM (mfano 2024-01)")
    ap.add_argument("--out", default=None, help="hifadhi output kwenye faili")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    cfg = load_config()
    symbol = args.symbol or cfg["pairs"][0]
    month = args.month or cfg["date_range"]["train_start"][:7]
    return run(symbol, month, args.out)


if __name__ == "__main__":
    raise SystemExit(main())
