"""
build_candles.py — Ticks ghafi -> Candles (OHLC) kwa kila timeframe. SEHEMU 1.

Inafanya kazi kwa DuckDB (inastream Parquet ya 26GB bila kujaza RAM):
  1. Inasoma raw ticks za symbol (Hive: symbol=*/year=*/month=*/day=*/ticks.parquet)
  2. Ina-convert timestamp -> UTC (timestamp tayari ni tz-aware = instant kamili)
  3. Inasafisha INLINE: dump bid<=0, ask<=0, ask<bid, na duplicates za timestamp
  4. Ina-bucket kwa kila TF (15m/30m/H1/H4/D1), aligned kwa UTC midnight
  5. OHLC kutoka bid (au mid), + spread_mean/max, tick_count, volume
  6. Inaandika Parquet: data/processed/candles/symbol=X/tf=Y.parquet

Bar inawekewa muda wa KUFUNGUKA (bar_open). Kanuni ya no-lookahead:
  candle yenye bar_open = T inajulikana tu baada ya T + interval. Watumiaji
  (Model 1/2) lazima wasitumie bar inayoendelea kuunda.

Endesha kwenye PC ya Japhet (pale data ilipo):
  python src\\data\\build_candles.py --symbol EURUSD --tf 15m   # jaribio (1 pair, 1 TF)
  python src\\data\\build_candles.py                            # pairs zote, TF zote
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import duckdb
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config" / "data_config.yaml"

# TF -> kipimo cha DuckDB INTERVAL
TF_INTERVAL = {
    "1m":  "INTERVAL 1 MINUTE",
    "5m":  "INTERVAL 5 MINUTE",
    "15m": "INTERVAL 15 MINUTE",
    "30m": "INTERVAL 30 MINUTE",
    "H1":  "INTERVAL 1 HOUR",
    "H2":  "INTERVAL 2 HOUR",
    "H4":  "INTERVAL 4 HOUR",
    "D1":  "INTERVAL 1 DAY",
}


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def pip_size(symbol: str) -> float:
    """JPY pairs: pip = 0.01; nyingine: pip = 0.0001."""
    return 0.01 if "JPY" in symbol.upper() else 0.0001


def price_expr(price_for_ohlc: str) -> str:
    """Bei ya kujenga OHLC: 'bid' (default) au 'mid' = (bid+ask)/2."""
    if price_for_ohlc == "mid":
        return "((bid + ask) / 2.0)"
    return "bid"


def build_sql(symbol: str, tf: str, cfg: dict) -> str:
    raw_glob = (REPO_ROOT / cfg["paths"]["raw_ticks"] /
                f"symbol={symbol}" / "**" / "*.parquet")
    src = str(raw_glob).replace("\\", "/")
    interval = TF_INTERVAL[tf]
    px = price_expr(cfg["resample"].get("price_for_ohlc", "bid"))
    pip = pip_size(symbol)

    # ts_utc: instant -> naive TIMESTAMP katika UTC (kwa bucketing UTC-aligned).
    # time_bucket origin = epoch (1970-01-01) -> buckets 00:00,00:15,... UTC.
    return f"""
    WITH clean AS (
        SELECT
            (timestamp AT TIME ZONE 'UTC')   AS ts_utc,
            bid, ask,
            (ask - bid)                      AS spread_px,
            COALESCE(bid_vol, 0)             AS bid_vol,
            COALESCE(ask_vol, 0)             AS ask_vol
        FROM read_parquet('{src}', union_by_name => true)
        WHERE bid > 0 AND ask > 0 AND ask >= bid          -- safisha bei mbovu
    ),
    dedup AS (
        -- ondoa duplicates kamili: tick moja kwa kila (timestamp,bid,ask,vols)
        SELECT DISTINCT ts_utc, bid, ask, spread_px, bid_vol, ask_vol FROM clean
    )
    SELECT
        '{symbol}'                                   AS symbol,
        '{tf}'                                       AS tf,
        time_bucket({interval}, ts_utc, TIMESTAMP '1970-01-01') AS bar_open,
        arg_min({px}, ts_utc)                        AS open,
        max({px})                                    AS high,
        min({px})                                    AS low,
        arg_max({px}, ts_utc)                        AS close,
        COUNT(*)                                     AS tick_count,
        SUM(bid_vol) + SUM(ask_vol)                  AS volume,
        SUM(bid_vol)                                 AS bid_volume,
        SUM(ask_vol)                                 AS ask_volume,
        -- order-flow pressure: +1 = ununuzi, -1 = uuzaji (feature, sio rule)
        (SUM(ask_vol) - SUM(bid_vol))
            / NULLIF(SUM(ask_vol) + SUM(bid_vol), 0)  AS volume_imbalance,
        AVG(spread_px)                               AS spread_mean,
        MAX(spread_px)                               AS spread_max,
        AVG(spread_px) / {pip}                       AS spread_mean_pips,
        MAX(spread_px) / {pip}                       AS spread_max_pips
    FROM dedup
    GROUP BY bar_open
    ORDER BY bar_open
    """


def build_one(con: duckdb.DuckDBPyConnection, symbol: str, tf: str, cfg: dict) -> int:
    out_dir = REPO_ROOT / cfg["paths"]["processed"] / "candles" / f"symbol={symbol}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"tf={tf}.parquet"
    sql = build_sql(symbol, tf, cfg)

    t0 = time.time()
    con.execute(
        f"COPY ({sql}) TO '{str(out_path).replace(chr(92), '/')}' "
        f"(FORMAT PARQUET, COMPRESSION ZSTD)"
    )
    n = con.execute(
        f"SELECT COUNT(*) FROM read_parquet('{str(out_path).replace(chr(92), '/')}')"
    ).fetchone()[0]
    dt = time.time() - t0
    print(f"  [{symbol} {tf}] candles={n:,}  ({dt:.1f}s)  -> {out_path.relative_to(REPO_ROOT)}")
    return n


def main() -> int:
    ap = argparse.ArgumentParser(description="Jenga candles kutoka ticks ghafi")
    ap.add_argument("--symbol", default=None, help="pair moja (default: zote kwenye config)")
    ap.add_argument("--tf", default=None, choices=list(TF_INTERVAL), help="TF moja (default: zote)")
    ap.add_argument("--threads", type=int, default=0, help="DuckDB threads (0 = auto)")
    args = ap.parse_args()

    cfg = load_config()
    raw_root = REPO_ROOT / cfg["paths"]["raw_ticks"]
    if not raw_root.exists():
        print(f"HITILAFU: '{raw_root}' haipo. Endesha kutoka root ya repo.", file=sys.stderr)
        return 1

    symbols = [args.symbol] if args.symbol else cfg["pairs"]
    tfs = [args.tf] if args.tf else cfg["timeframes"]

    con = duckdb.connect()
    if args.threads > 0:
        con.execute(f"PRAGMA threads={args.threads}")

    print(f"Symbols: {symbols}\nTimeframes: {tfs}\n")
    total = 0
    for sym in symbols:
        if not (raw_root / f"symbol={sym}").exists():
            print(f"  ONYO: symbol={sym} haipo kwenye raw — naruka.", file=sys.stderr)
            continue
        for tf in tfs:
            total += build_one(con, sym, tf, cfg)
    print(f"\nJumla ya candles zilizoandikwa: {total:,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
