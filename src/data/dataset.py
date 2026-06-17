"""
dataset.py — API ya KUPATA candles kwa usahihi (SEHEMU 1 -> watumiaji wote).

Hii ndiyo "how to get data": kila eneo (Model 1, Model 2, Sizing, Compliance)
linapaswa kupata data KUPITIA hapa, ili kanuni za usalama zitekelezwe mahali pamoja:

  - NO-LOOKAHEAD: bar ina label ya bar_open (muda wa kufunguka). Bar yenye
    bar_open = T inajulikana tu baada ya T+interval. `shift_for_decision()`
    inahakikisha unatumia bar iliyOFUNGWA tu kwenye uamuzi wa wakati T.
  - NO-TRADE WINDOW: rollover (23:00 CET, DST-aware) huchujwa kwa `drop_no_trade`.
  - LIQUIDITY FILTER: bars zenye tick_count ndogo huchujwa kwa `min_tick_count`.
  - TRAIN/OOS SPLIT: 2016–2024 train, 2025+ OOS (kutoka config).

Inarudisha polars.DataFrame. DuckDB inastream Parquet (haijai RAM).

Mfano:
    from data.dataset import load_candles, train_oos_split
    df = load_candles("EURUSD", "H1", drop_no_trade=True)
    train, oos = train_oos_split(df)
"""
from __future__ import annotations

from pathlib import Path

import duckdb
import polars as pl
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config" / "data_config.yaml"

_CFG: dict | None = None


def config() -> dict:
    global _CFG
    if _CFG is None:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            _CFG = yaml.safe_load(f)
    return _CFG


def candle_path(symbol: str, tf: str) -> Path:
    cfg = config()
    return (REPO_ROOT / cfg["paths"]["processed"] / "candles" /
            f"symbol={symbol}" / f"tf={tf}.parquet")


def pip_size(symbol: str) -> float:
    """Ukubwa wa pip: JPY pairs = 0.01; nyingine = 0.0001."""
    return 0.01 if "JPY" in symbol.upper() else 0.0001


def load_candles(
    symbol: str,
    tf: str,
    start: str | None = None,
    end: str | None = None,
    drop_no_trade: bool = False,
    min_tick_count: int | None = None,
    columns: list[str] | None = None,
) -> pl.DataFrame:
    """Pata candles za (symbol, tf) zikiwa safi na zilizochujwa.

    start/end : "YYYY-MM-DD" (UTC) — chuja muda.
    drop_no_trade : ondoa bars za rollover (no_trade_window, CE(S)T DST-aware).
    min_tick_count : ondoa bars zenye tick_count < hii (liquidity filter).
                     None (default) = USICHUJE. Mtumiaji aombe wazi (k.m. Model 2
                     entry: weka cfg['quality']['min_tick_count']).
    columns : chagua columns (default = zote). bar_open daima inarudishwa.
    """
    cfg = config()
    path = candle_path(symbol, tf)
    if not path.exists():
        raise FileNotFoundError(f"Candles hazipo: {path} — endesha build_candles.py")
    src = str(path).replace("\\", "/")

    where = ["TRUE"]
    if start:
        where.append(f"bar_open >= TIMESTAMP '{start} 00:00:00'")
    if end:
        where.append(f"bar_open <= TIMESTAMP '{end} 23:59:59'")

    if min_tick_count and min_tick_count > 0:   # None/0 = usichuje (wazi, si siri)
        where.append(f"tick_count >= {min_tick_count}")

    if drop_no_trade:
        ntw = cfg.get("no_trade_window", {})
        tz = ntw.get("tz", "Europe/Berlin")
        hours = ntw.get("hours", [])
        if hours:
            hrs = ", ".join(str(int(h)) for h in hours)
            # bar_open ni naive UTC -> tafsiri UTC -> badilisha kwa broker local
            where.append(
                f"EXTRACT(hour FROM (bar_open AT TIME ZONE 'UTC') "
                f"AT TIME ZONE '{tz}') NOT IN ({hrs})"
            )

    sel = "*" if not columns else "bar_open, " + ", ".join(
        f'"{c}"' for c in columns if c != "bar_open"
    )
    con = duckdb.connect()
    try:
        con.execute("SET preserve_insertion_order=false")
        return con.execute(
            f"SELECT {sel} FROM read_parquet('{src}') "
            f"WHERE {' AND '.join(where)} ORDER BY bar_open"
        ).pl()
    finally:
        con.close()   # funga connection (load_candles huitwa maelfu ya mara - epuka leak)


def train_oos_split(
    df: pl.DataFrame, train_end: str | None = None
) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Gawanya kwa train (≤ train_end) na OOS (> train_end). Default kutoka config
    (2024-12-31): OOS = 2025+ ni HOLDOUT YA MWISHO. Kwa walk-forward ya Sehemu 7
    (train 2016–2022, test 2023–2024), pitisha train_end="2022-12-31"."""
    if train_end is None:
        train_end = config()["date_range"]["train_end"]
    end_date = pl.lit(train_end).str.to_date("%Y-%m-%d")   # siku NZIMA inajumuishwa
    train = df.filter(pl.col("bar_open").dt.date() <= end_date)
    oos = df.filter(pl.col("bar_open").dt.date() > end_date)
    return train, oos


def shift_for_decision(df: pl.DataFrame, by: int = 1) -> pl.DataFrame:
    """KINGA YA NO-LOOKAHEAD: kwa uamuzi unaotumia bar zilizofungwa, hamisha
    OHLCV mbele kwa `by` bars. Baada ya hapo, row ya wakati T ina data ya bar
    iliyofungwa KABLA ya T (salama kabisa dhidi ya lookahead).
    Tumia kwa features zinazoamua entry/regime kwa wakati halisi."""
    cols = [c for c in df.columns if c != "bar_open"]
    return df.with_columns([pl.col(c).shift(by).alias(c) for c in cols])


def add_returns(df: pl.DataFrame, price: str = "close", log: bool = False) -> pl.DataFrame:
    """Ongeza column ya return (close-to-close). log=True kwa log-returns."""
    prev = pl.col(price).shift(1)
    ret = (pl.col(price) / prev).log() if log else (pl.col(price) / prev - 1)
    return df.with_columns(ret.alias("log_ret" if log else "ret"))
