"""
inspect_raw.py — Kichunguzi cha schema ya tick data ghafi (SEHEMU 1, hatua 0).

Kusudi: KABLA ya kuandika ingest/resample, tunahitaji kuona UMBO HALISI la
faili za Parquet — majina ya columns, types, format ya timestamp, na sample.
Hatukisi; tunathibitisha.

Endesha kwenye PC ya Japhet (pale data ilipo):
    python src/data/inspect_raw.py
    python src/data/inspect_raw.py --symbol EURUSD       # pair fulani
    python src/data/inspect_raw.py --out reports/raw_schema.txt   # hifadhi output

Kisha tuma output kwa Claude ili tukamilishe ingest.py kwa usahihi.
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


def find_one_leaf(raw_ticks: Path, symbol: str) -> Path | None:
    """Tafuta faili moja ya .parquet (au jina 'ticks') kwa symbol uliyopewa,
    ya mwanzo kabisa kwa mpangilio (year/month/day)."""
    base = raw_ticks / f"symbol={symbol}"
    if not base.exists():
        return None
    # jaribu .parquet, kisha jina lolote (Dukascopy huandika faili 'ticks')
    candidates = sorted(base.rglob("*.parquet")) or sorted(
        p for p in base.rglob("*") if p.is_file()
    )
    return candidates[0] if candidates else None


def inspect(leaf: Path, con: duckdb.DuckDBPyConnection, out=sys.stdout) -> None:
    src = str(leaf).replace("\\", "/")
    p = lambda *a: print(*a, file=out)

    p("=" * 70)
    p(f"FAILI: {leaf}")
    p(f"Ukubwa: {leaf.stat().st_size / 1024:.1f} KB")
    p("=" * 70)

    # 1. Schema (majina + types)
    p("\n--- SCHEMA (columns + types) ---")
    schema = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{src}')").fetchall()
    for col_name, col_type, *_ in schema:
        p(f"  {col_name:<24} {col_type}")
    cols = [row[0] for row in schema]

    # 2. Idadi ya rows
    n = con.execute(f"SELECT COUNT(*) FROM read_parquet('{src}')").fetchone()[0]
    p(f"\n--- ROWS: {n:,} (siku moja, pair moja) ---")

    # 3. Sample rows 5 za kwanza
    p("\n--- SAMPLE (rows 5 za kwanza) ---")
    sample = con.execute(f"SELECT * FROM read_parquet('{src}') LIMIT 5").fetchdf()
    p(sample.to_string())

    # 4. Tafuta column ya muda, onyesha min/max + format
    p("\n--- TIMESTAMP (tafuta column ya muda) ---")
    time_like = [c for c in cols if any(
        k in c.lower() for k in ("time", "date", "ts", "stamp")
    )]
    if time_like:
        for c in time_like:
            mn, mx = con.execute(
                f'SELECT MIN("{c}"), MAX("{c}") FROM read_parquet(\'{src}\')'
            ).fetchone()
            p(f"  {c}: min={mn!r}  max={mx!r}")
        p("  -> Kama ni nambari kubwa (~1e12), ni epoch-millis. Kama ni tarehe, ni datetime.")
    else:
        p("  (Hakuna column yenye jina la muda dhahiri — angalia schema hapo juu.)")

    # 5. Null counts kwa kila column
    p("\n--- NULLS kwa kila column ---")
    null_expr = ", ".join(
        f'SUM(CASE WHEN "{c}" IS NULL THEN 1 ELSE 0 END) AS "{c}"' for c in cols
    )
    nulls = con.execute(
        f"SELECT {null_expr} FROM read_parquet('{src}')"
    ).fetchdf()
    p(nulls.to_string(index=False))
    p("")


def main() -> int:
    ap = argparse.ArgumentParser(description="Chunguza schema ya tick data ghafi")
    ap.add_argument("--symbol", default=None, help="pair moja (default: wa kwanza kwenye config)")
    ap.add_argument("--out", default=None, help="hifadhi output kwenye faili (k.m. reports/raw_schema.txt)")
    args = ap.parse_args()

    cfg = load_config()
    raw_ticks = REPO_ROOT / cfg["paths"]["raw_ticks"]
    if not raw_ticks.exists():
        print(f"HITILAFU: '{raw_ticks}' haipo. Hakikisha unaendesha kutoka root ya repo,\n"
              f"na data iko {cfg['paths']['raw_ticks']}/symbol=.../", file=sys.stderr)
        return 1

    symbol = args.symbol or cfg["pairs"][0]
    leaf = find_one_leaf(raw_ticks, symbol)
    if leaf is None:
        print(f"HITILAFU: sijapata faili yoyote chini ya symbol={symbol}", file=sys.stderr)
        return 1

    con = duckdb.connect()
    out = open(args.out, "w", encoding="utf-8") if args.out else sys.stdout
    try:
        inspect(leaf, con, out=out)
    finally:
        if args.out:
            out.close()
            print(f"Imeandikwa: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
