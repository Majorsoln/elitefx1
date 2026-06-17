"""
eda.py — Exploratory Data Analysis ya candles (SEHEMU 1). Ripoti ya Kiswahili.

Inajibu maswali yaliyoibuka kwenye quality report:
  1. Spread kwa saa ya UTC  -> kuthibitisha rollover/edge spikes (saa gani?)
  2. Tarehe za gaps         -> kuthibitisha = sikukuu (sio data mbovu)
  3. Returns & volatility   -> msingi wa Model 1 (regime)
  4. Correlation matrix     -> kuthibitisha CORRELATION_GROUPS (Compliance, Sehemu 5)
  5. Volume imbalance       -> sanity (wastani ukaribie 0)

DuckDB pekee — hakuna pandas/numpy/matplotlib. Inatoa reports/eda_report.md

Endesha kwenye PC ya Japhet:
    python src\\data\\eda.py
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import duckdb
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config" / "data_config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _glob(cfg: dict, tf: str) -> str:
    p = REPO_ROOT / cfg["paths"]["processed"] / "candles" / "symbol=*" / f"tf={tf}.parquet"
    return str(p).replace("\\", "/")


def sec_spread_by_hour(con, cfg, pairs) -> list[str]:
    """Spread (pips) kwa saa ya UTC — kupata saa za rollover/edge."""
    L = ["## 1. Spread kwa saa ya UTC (H1, pips) — kutafuta rollover spike\n"]
    # wastani wa pairs zote kwa kila saa
    rows = con.execute(f"""
        SELECT EXTRACT(hour FROM bar_open) AS hr,
               ROUND(AVG(spread_mean_pips), 3) AS avg_spr,
               ROUND(MAX(spread_max_pips), 1) AS max_spr
        FROM read_parquet('{_glob(cfg, "H1")}')
        GROUP BY hr ORDER BY hr
    """).fetchall()
    L.append("**Wastani wa pairs zote 9 kwa kila saa:**\n")
    L.append("| Saa (UTC) | Avg spread | Max spread |")
    L.append("|-----------|------------|------------|")
    overall = sorted(r[1] for r in rows)
    med = overall[len(overall) // 2]
    for hr, avg_spr, max_spr in rows:
        flag = "  ⬅️ SPIKE" if avg_spr > 2 * med else ""
        L.append(f"| {int(hr):02d}:00 | {avg_spr} | {max_spr} |{flag}")
    L.append(f"\n*Median ya saa zote: {med} pips. Saa zenye avg > 2× median "
             f"({2*med:.2f}) zimewekwa SPIKE — ndizo za kuepuka kufanya biashara.*\n")
    return L


def sec_gaps(con, cfg, ref_pair="EURUSD") -> list[str]:
    """Orodha ya gaps (bila weekend) na tarehe — kuthibitisha = sikukuu."""
    L = [f"## 2. Gaps (bila weekend) — tarehe halisi (rejea: {ref_pair} H1)\n"]
    path = (REPO_ROOT / cfg["paths"]["processed"] / "candles" /
            f"symbol={ref_pair}" / "tf=H1.parquet")
    src = str(path).replace("\\", "/")
    gap_limit = cfg["quality"].get("max_gap_minutes", 60)
    rows = con.execute(f"""
        WITH g AS (
            SELECT bar_open, lag(bar_open) OVER (ORDER BY bar_open) AS prev
            FROM read_parquet('{src}'))
        SELECT prev AS gap_anza, bar_open AS gap_isha,
               date_diff('minute', prev, bar_open) AS dakika,
               ROUND(date_diff('minute', prev, bar_open) / 1440.0, 2) AS siku
        FROM g
        WHERE prev IS NOT NULL
          AND date_diff('minute', prev, bar_open) > 60 + {gap_limit}
          AND dayofweek(prev) NOT IN (5, 6)
        ORDER BY dakika DESC
    """).fetchall()
    L.append("| Gap inaanza | Gap inaisha | Dakika | Siku |")
    L.append("|-------------|-------------|--------|------|")
    for anza, isha, dk, sk in rows:
        L.append(f"| {anza} | {isha} | {dk:,} | {sk} |")
    L.append(f"\n*Jumla: {len(rows)} gaps. Linganisha tarehe na sikukuu zinazojulikana "
             "(Christmas, New Year, Good Friday). Zikilingana = data ni sahihi.*\n")
    return L


def sec_returns(con, cfg, pairs) -> list[str]:
    """Returns & volatility (D1, close-to-close) kwa kila pair."""
    L = ["## 3. Returns & Volatility (D1 close-to-close) — msingi wa Model 1\n"]
    L.append("| Pair | Mean daily % | Std (vol) % | Ann. vol % | Min % | Max % |")
    L.append("|------|--------------|-------------|------------|-------|-------|")
    for sym in pairs:
        path = (REPO_ROOT / cfg["paths"]["processed"] / "candles" /
                f"symbol={sym}" / "tf=D1.parquet")
        src = str(path).replace("\\", "/")
        r = con.execute(f"""
            WITH r AS (
                SELECT (close / lag(close) OVER (ORDER BY bar_open) - 1) * 100 AS ret
                FROM read_parquet('{src}'))
            SELECT ROUND(AVG(ret), 4), ROUND(STDDEV_SAMP(ret), 4),
                   ROUND(STDDEV_SAMP(ret) * sqrt(252), 2),
                   ROUND(MIN(ret), 2), ROUND(MAX(ret), 2)
            FROM r WHERE ret IS NOT NULL
        """).fetchone()
        L.append(f"| {sym} | {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} |")
    L.append("\n*Ann. vol = std × √252. JPY/commodity pairs huwa na vol kubwa zaidi.*\n")
    return L


def sec_correlation(con, cfg, pairs) -> list[str]:
    """Correlation matrix ya D1 returns — kuthibitisha CORRELATION_GROUPS."""
    L = ["## 4. Correlation Matrix (D1 returns) — kuthibitisha CORRELATION_GROUPS\n"]
    # jenga wide table: tarehe x pair -> return
    cols = ", ".join(
        f"MAX(CASE WHEN symbol='{s}' THEN ret END) AS \"{s}\"" for s in pairs
    )
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE wide AS
        WITH r AS (
            SELECT symbol, CAST(bar_open AS DATE) AS d,
                   (close / lag(close) OVER (PARTITION BY symbol ORDER BY bar_open) - 1) AS ret
            FROM read_parquet('{_glob(cfg, "D1")}'))
        SELECT d, {cols} FROM r GROUP BY d
    """)
    # header
    L.append("| | " + " | ".join(pairs) + " |")
    L.append("|" + "---|" * (len(pairs) + 1))
    for a in pairs:
        cells = []
        for b in pairs:
            c = con.execute(f'SELECT ROUND(corr("{a}","{b}"), 2) FROM wide').fetchone()[0]
            cells.append(str(c))
        L.append(f"| **{a}** | " + " | ".join(cells) + " |")
    L.append("\n*Thamani karibu na +1 = zinasonga pamoja; -1 = kinyume. Thibitisha "
             "makundi ya MFUMO.md (USD_group, USD_strength, EUR_group, AUD_NZD_group).*\n")
    return L


def sec_imbalance(con, cfg, pairs) -> list[str]:
    L = ["## 5. Volume Imbalance (1m) — sanity (wastani ukaribie 0)\n"]
    L.append("| Pair | Mean imbalance | p05 | p95 |")
    L.append("|------|----------------|-----|-----|")
    for sym in pairs:
        path = (REPO_ROOT / cfg["paths"]["processed"] / "candles" /
                f"symbol={sym}" / "tf=1m.parquet")
        src = str(path).replace("\\", "/")
        r = con.execute(f"""
            SELECT ROUND(AVG(volume_imbalance), 4),
                   ROUND(QUANTILE_CONT(volume_imbalance, 0.05), 3),
                   ROUND(QUANTILE_CONT(volume_imbalance, 0.95), 3)
            FROM read_parquet('{src}') WHERE volume_imbalance IS NOT NULL
        """).fetchone()
        L.append(f"| {sym} | {r[0]} | {r[1]} | {r[2]} |")
    L.append("")
    return L


def main() -> int:
    cfg = load_config()
    pairs = cfg["pairs"]
    # hakikisha candles zipo
    if not (REPO_ROOT / cfg["paths"]["processed"] / "candles").exists():
        print("HITILAFU: candles hazipo. Endesha build_candles.py kwanza.", file=sys.stderr)
        return 1

    con = duckdb.connect()
    con.execute("SET preserve_insertion_order=false")

    out = ["# Ripoti ya EDA — EliteFX SEHEMU 1\n",
           f"*Imezalishwa: {datetime.now():%Y-%m-%d %H:%M}*\n"]

    out += sec_spread_by_hour(con, cfg, pairs)
    print("  [1/5] spread kwa saa — done")
    out += sec_gaps(con, cfg)
    print("  [2/5] gaps — done")
    out += sec_returns(con, cfg, pairs)
    print("  [3/5] returns/vol — done")
    out += sec_correlation(con, cfg, pairs)
    print("  [4/5] correlation — done")
    out += sec_imbalance(con, cfg, pairs)
    print("  [5/5] volume imbalance — done")

    path = REPO_ROOT / cfg["paths"]["reports"] / "eda_report.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(out), encoding="utf-8")
    print(f"\nRipoti: {path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
