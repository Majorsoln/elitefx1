"""
data_inventory.py — ukaguzi wa data zilizopo (Chief direct, 2026-07-09).

Inaonyesha kwa kila symbol iliyopo data/raw/ticks: files, ticks, tarehe ya kwanza/mwisho,
na miezi inayokosekana (--months). Pia inakagua states (data/processed/state) na kuorodhesha
pairs ZINAZOTAKIWA ambazo hazipo (wanted: upanuzi wa CYCLE-2 — XAUUSD/GBPJPY/EURCHF).

Endesha (root ya repo au src/data):
  python data_inventory.py                 # muhtasari wa haraka (metadata — sekunde chache)
  python data_inventory.py --months        # + miezi inayokosekana kwa kila symbol (inasoma ts — polepole kidogo)
  python data_inventory.py --symbol XAUUSD # symbol moja
Self-test: python data_inventory.py --self-test
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WANTED_NEW = ["XAUUSD", "GBPJPY", "EURCHF"]     # upanuzi wa CYCLE-2 (ombi la Chief kwa PD)


def _cfg():
    import yaml
    with open(REPO_ROOT / "config" / "data_config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _time_col(con, src):
    sch = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{src}', union_by_name=>true)").fetchall()
    cols = [r[0] for r in sch]
    return next((c for c in cols if any(k in c.lower() for k in ("time", "date", "ts", "stamp"))), None)


def inventory(raw_root: Path, months=False, only=None):
    """Rudisha list ya dict(symbol, files, ticks, start, end, missing_months)."""
    import duckdb
    rows = []
    sym_dirs = sorted(d for d in raw_root.glob("symbol=*") if d.is_dir())
    if only:
        sym_dirs = [d for d in sym_dirs if d.name.split("=", 1)[1].upper() == only.upper()]
    con = duckdb.connect()
    for d in sym_dirs:
        sym = d.name.split("=", 1)[1]
        files = list(d.rglob("*.parquet"))
        if not files:
            rows.append(dict(symbol=sym, files=0, ticks=0, start=None, end=None, missing=None))
            continue
        src = str(d / "**" / "*.parquet").replace("\\", "/")
        t = _time_col(con, src)
        q = f"""SELECT COUNT(*) AS n, MIN(CAST("{t}" AS TIMESTAMP)) AS a,
                       MAX(CAST("{t}" AS TIMESTAMP)) AS b
                FROM read_parquet('{src}', union_by_name=>true)"""
        n, a, b = con.execute(q).fetchone()
        missing = None
        if months and a is not None:
            got = {r[0] for r in con.execute(
                f"""SELECT DISTINCT strftime(CAST("{t}" AS TIMESTAMP), '%Y-%m')
                    FROM read_parquet('{src}', union_by_name=>true)""").fetchall()}
            missing = []
            y, m = a.year, a.month
            while (y, m) <= (b.year, b.month):
                key = f"{y:04d}-{m:02d}"
                if key not in got:
                    missing.append(key)
                m += 1
                if m == 13:
                    y += 1; m = 1
        rows.append(dict(symbol=sym, files=len(files), ticks=int(n),
                         start=str(a)[:10] if a else None, end=str(b)[:10] if b else None,
                         missing=missing))
    return rows


def states_summary(processed: Path):
    """Muhtasari wa states zilizojengwa (symbol × tf, min/max ts)."""
    import polars as pl
    out = []
    for p in sorted((processed / "state").glob("symbol=*/tf=*.parquet")):
        sym = p.parent.name.split("=", 1)[1]; tf = p.stem.split("=", 1)[1]
        df = pl.read_parquet(p, columns=["ts"])
        out.append((sym, tf, str(df["ts"].min())[:10], str(df["ts"].max())[:10], df.height))
    return out


def run(months=False, only=None):
    c = _cfg()
    raw_root = REPO_ROOT / c["paths"]["raw_ticks"]
    if not raw_root.exists():
        print(f"HITILAFU: {raw_root} haipo — uko kwenye PC yenye data?")
        return 1
    rows = inventory(raw_root, months=months, only=only)
    print(f"\n=== RAW TICKS ({raw_root.relative_to(REPO_ROOT)}) ===")
    print(f"{'symbol':8s} {'files':>6s} {'ticks':>14s} {'kuanzia':>11s} {'hadi':>11s}")
    for r in rows:
        print(f"{r['symbol']:8s} {r['files']:>6d} {r['ticks']:>14,d} {str(r['start']):>11s} {str(r['end']):>11s}")
        if r["missing"]:
            print(f"         miezi inayokosekana ({len(r['missing'])}): {', '.join(r['missing'][:12])}"
                  + (" ..." if len(r["missing"]) > 12 else ""))
        elif r["missing"] is not None:
            print("         miezi: KAMILI (hakuna pengo)")

    # config-vs-disk daima inalinganisha na DISK NZIMA (sio filter ya --symbol)
    have = {d.name.split("=", 1)[1].upper() for d in raw_root.glob("symbol=*") if d.is_dir()}
    cfg_pairs = [p.upper() for p in c["pairs"]]
    print("\n=== CONFIG vs DISK ===")
    miss_disk = [p for p in cfg_pairs if p not in have]
    print(f"pairs za config zisizo na ticks: {miss_disk if miss_disk else 'HAKUNA (zote zipo)'}")
    print(f"WANTED (upanuzi wa C2) ambazo HAZIPO bado: {[w for w in WANTED_NEW if w not in have] or 'zote zipo!'}")
    extra = sorted(have - set(cfg_pairs))
    if extra:
        print(f"zipo DISK lakini SIO kwenye config bado: {extra}")

    if not only:
        st = states_summary(REPO_ROOT / c["paths"]["processed"])
        if st:
            print("\n=== STATES (processed) ===")
            for sym, tf, a, b, n in st:
                print(f"  {sym:8s} {tf:3s}  {a} -> {b}  (bars {n:,})")
    return 0


def self_test():
    """Fixtures ndogo kwenye temp dir: inventory + missing months + wanted check."""
    import tempfile
    from datetime import datetime
    import polars as pl
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        d = root / "symbol=TESTUSD" / "year=2024"
        d.mkdir(parents=True)
        # miezi 01 na 03 (02 inakosekana)
        for mo in (1, 3):
            df = pl.DataFrame({"timestamp": [datetime(2024, mo, 5, 10), datetime(2024, mo, 6, 11)],
                               "bid": [1.1000, 1.1010], "ask": [1.1002, 1.1012]})
            df.write_parquet(d / f"m{mo}.parquet")
        rows = inventory(root, months=True)
        r = rows[0]
        ok &= r["symbol"] == "TESTUSD" and r["files"] == 2 and r["ticks"] == 4
        ok &= r["start"] == "2024-01-05" and r["end"] == "2024-03-06"
        ok &= r["missing"] == ["2024-02"]
        print(f"  inventory: files={r['files']} ticks={r['ticks']} missing={r['missing']} -> {ok}")
        ok &= all(w not in {"TESTUSD"} for w in WANTED_NEW)   # wanted logic sanity
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--months", action="store_true", help="onyesha miezi inayokosekana (polepole kidogo)")
    ap.add_argument("--symbol", default=None)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    return run(months=a.months, only=a.symbol)


if __name__ == "__main__":
    raise SystemExit(main())
