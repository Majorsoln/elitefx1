"""
build_candles.py — Ticks ghafi -> Candles (OHLC) kwa kila timeframe. SEHEMU 1.

DESIGN (cascade — kwa kasi):
  1. Jenga 1m kutoka ticks (scan MOJA ya raw 26GB; ndiyo hatua ghali).
  2. Jenga 5m/15m/30m/H1/H2/H4/D1 kwa kuROLLUP 1m candles (haraka sana).
  Timeframes zote ni multiples za 1m na zime-align kwa UTC epoch, kwa hiyo 1m
  candles zinanest ndani yake kikamilifu -> rollup = sawa kabisa na from-ticks.

USAHIHI wa rollup:
  open = ya kwanza, close = ya mwisho, high = max, low = min,
  volume/tick_count/bid/ask_volume = sum, volume_imbalance = recompute,
  spread_mean = WEIGHTED kwa tick_count, spread_max = max.

Bar inawekewa muda wa KUFUNGUKA (bar_open, UTC). No-lookahead: candle yenye
bar_open = T inajulikana tu baada ya T + interval.

Endesha kwenye PC ya Japhet (pale data ilipo):
  python src\\data\\build_candles.py --symbol EURUSD            # pair moja, TF zote
  python src\\data\\build_candles.py                            # pairs zote, TF zote
  python src\\data\\build_candles.py --symbol EURUSD --force-1m # jenga upya 1m
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

BASE_TF = "1m"  # base inajengwa kutoka ticks; zingine zinarollup kutoka hapa

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
    return "((bid + ask) / 2.0)" if price_for_ohlc == "mid" else "bid"


def candle_path(symbol: str, tf: str, cfg: dict) -> Path:
    return (REPO_ROOT / cfg["paths"]["processed"] / "candles" /
            f"symbol={symbol}" / f"tf={tf}.parquet")


def _posix(p: Path) -> str:
    return str(p).replace("\\", "/")


# ---------- Hatua 1: 1m kutoka ticks ----------
def build_1m_sql(symbol: str, cfg: dict) -> str:
    raw_glob = (REPO_ROOT / cfg["paths"]["raw_ticks"] /
                f"symbol={symbol}" / "**" / "*.parquet")
    src = _posix(raw_glob)
    px = price_expr(cfg["resample"].get("price_for_ohlc", "bid"))
    pip = pip_size(symbol)
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
    )
    -- HAKUNA DISTINCT: duplicates kamili haziathiri OHLC; DISTINCT juu ya
    -- ~200M rows ilikuwa inajaza temp-disk (OOM). Aggregation inatosha.
    SELECT
        '{symbol}'                                   AS symbol,
        '{BASE_TF}'                                  AS tf,
        time_bucket(INTERVAL 1 MINUTE, ts_utc, TIMESTAMP '1970-01-01') AS bar_open,
        arg_min({px}, ts_utc)                        AS open,
        max({px})                                    AS high,
        min({px})                                    AS low,
        arg_max({px}, ts_utc)                        AS close,
        COUNT(*)                                     AS tick_count,
        SUM(bid_vol) + SUM(ask_vol)                  AS volume,
        SUM(bid_vol)                                 AS bid_volume,
        SUM(ask_vol)                                 AS ask_volume,
        (SUM(ask_vol) - SUM(bid_vol))
            / NULLIF(SUM(ask_vol) + SUM(bid_vol), 0)  AS volume_imbalance,
        AVG(spread_px)                               AS spread_mean,
        MAX(spread_px)                               AS spread_max,
        AVG(spread_px) / {pip}                       AS spread_mean_pips,
        MAX(spread_px) / {pip}                       AS spread_max_pips
    FROM clean
    GROUP BY bar_open
    ORDER BY bar_open
    """


# ---------- Hatua 2: rollup kutoka 1m ----------
def build_rollup_sql(symbol: str, tf: str, cfg: dict) -> str:
    src = _posix(candle_path(symbol, BASE_TF, cfg))
    interval = TF_INTERVAL[tf]
    return f"""
    WITH base AS (
        SELECT *,
            time_bucket({interval}, bar_open, TIMESTAMP '1970-01-01') AS nb
        FROM read_parquet('{src}')
    )
    SELECT
        '{symbol}'                                   AS symbol,
        '{tf}'                                        AS tf,
        nb                                           AS bar_open,
        arg_min(open,  bar_open)                      AS open,
        max(high)                                    AS high,
        min(low)                                     AS low,
        arg_max(close, bar_open)                      AS close,
        SUM(tick_count)                              AS tick_count,
        SUM(volume)                                  AS volume,
        SUM(bid_volume)                              AS bid_volume,
        SUM(ask_volume)                              AS ask_volume,
        (SUM(ask_volume) - SUM(bid_volume))
            / NULLIF(SUM(ask_volume) + SUM(bid_volume), 0) AS volume_imbalance,
        -- spread_mean: weighted kwa tick_count (mean ya means isiyo na uzito = makosa)
        SUM(spread_mean * tick_count)      / NULLIF(SUM(tick_count), 0) AS spread_mean,
        MAX(spread_max)                              AS spread_max,
        SUM(spread_mean_pips * tick_count) / NULLIF(SUM(tick_count), 0) AS spread_mean_pips,
        MAX(spread_max_pips)                         AS spread_max_pips
    FROM base
    GROUP BY nb
    ORDER BY nb
    """


def _write(con: duckdb.DuckDBPyConnection, sql: str, out_path: Path, label: str) -> int:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    con.execute(
        f"COPY ({sql}) TO '{_posix(out_path)}' (FORMAT PARQUET, COMPRESSION ZSTD)"
    )
    n = con.execute(f"SELECT COUNT(*) FROM read_parquet('{_posix(out_path)}')").fetchone()[0]
    print(f"  [{label}] candles={n:,}  ({time.time() - t0:.1f}s)  -> {out_path.relative_to(REPO_ROOT)}")
    return n


def assert_raw_tz(con, symbol: str, cfg: dict) -> None:
    """Hakikisha column ya `timestamp` ya raw ni TIMESTAMP WITH TIME ZONE (instant
    kamili). build inategemea hii: `timestamp AT TIME ZONE 'UTC'` inatoa UTC sahihi.
    Kama raw ingekuwa naive (bila tz), conversion ingekosea KIMYA. Tunazuia hapo."""
    raw_glob = (REPO_ROOT / cfg["paths"]["raw_ticks"] /
                f"symbol={symbol}" / "**" / "*.parquet")
    t = con.execute(
        f"SELECT typeof(timestamp) FROM read_parquet('{_posix(raw_glob)}', "
        f"union_by_name => true) LIMIT 1"
    ).fetchone()
    if t and "TIME ZONE" not in t[0].upper() and "TZ" not in t[0].upper():
        raise SystemExit(
            f"HITILAFU TZ: {symbol} 'timestamp' ni '{t[0]}' (si tz-aware). build "
            f"inatarajia TIMESTAMPTZ. Rekebisha ingest kutumia source_tz="
            f"'{cfg['timezone']['source_tz']}' kabla ya kuendelea."
        )


def ensure_1m(con, symbol, cfg, force: bool) -> int:
    out = candle_path(symbol, BASE_TF, cfg)
    if out.exists() and not force:
        n = con.execute(f"SELECT COUNT(*) FROM read_parquet('{_posix(out)}')").fetchone()[0]
        print(f"  [{symbol} 1m] ipo tayari ({n:,}) — natumia upya (--force-1m kujenga upya)")
        return n
    assert_raw_tz(con, symbol, cfg)   # zuia tz mislabel kabla ya kujenga
    return _write(con, build_1m_sql(symbol, cfg), out, f"{symbol} 1m (kutoka ticks)")


def main() -> int:
    ap = argparse.ArgumentParser(description="Jenga candles kutoka ticks (cascade kupitia 1m)")
    ap.add_argument("--symbol", default=None, help="pair moja (default: zote)")
    ap.add_argument("--tf", default=None, choices=list(TF_INTERVAL), help="TF moja (default: zote)")
    ap.add_argument("--force-1m", action="store_true", help="jenga upya 1m hata kama ipo")
    ap.add_argument("--threads", type=int, default=0, help="DuckDB threads (0 = auto)")
    ap.add_argument("--memory-limit", default=None, help="k.m. '8GB' (punguza spill)")
    ap.add_argument("--temp-dir", default=None, help="folda ya temp (drive yenye nafasi)")
    args = ap.parse_args()

    cfg = load_config()
    raw_root = REPO_ROOT / cfg["paths"]["raw_ticks"]
    if not raw_root.exists():
        print(f"HITILAFU: '{raw_root}' haipo. Endesha kutoka root ya repo.", file=sys.stderr)
        return 1

    symbols = [args.symbol] if args.symbol else cfg["pairs"]
    tfs = [args.tf] if args.tf else cfg["timeframes"]

    con = duckdb.connect()
    # preserve_insertion_order=false: hupunguza memory/spill kwenye GROUP BY+COPY kubwa
    con.execute("SET preserve_insertion_order=false")
    if args.threads > 0:
        con.execute(f"SET threads={args.threads}")
    if args.memory_limit:
        con.execute(f"SET memory_limit='{args.memory_limit}'")
    if args.temp_dir:
        con.execute(f"SET temp_directory='{args.temp_dir}'")

    print(f"Symbols: {symbols}\nTimeframes: {tfs}\n")
    total = 0
    for sym in symbols:
        if not (raw_root / f"symbol={sym}").exists():
            print(f"  ONYO: symbol={sym} haipo kwenye raw — naruka.", file=sys.stderr)
            continue
        # 1m daima inahitajika (rollup zinaitegemea). Jenga au tumia upya.
        n1m = ensure_1m(con, sym, cfg, args.force_1m)
        if BASE_TF in tfs:
            total += n1m
        for tf in tfs:
            if tf == BASE_TF:
                continue
            total += _write(con, build_rollup_sql(sym, tf, cfg),
                            candle_path(sym, tf, cfg), f"{sym} {tf} (rollup)")
    print(f"\nJumla ya candles zilizoandikwa (bila 1m za reuse): {total:,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
