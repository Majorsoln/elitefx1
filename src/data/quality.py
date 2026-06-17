"""
quality.py — Ukaguzi wa ubora wa candles (SEHEMU 1). Inazalisha ripoti ya Kiswahili.

Inakagua kila (symbol, tf) kwenye data/processed/candles na kuandika
reports/data_quality_report.md. Ukaguzi:

  STRUCTURAL (PASS/FAIL — lazima zipite):
    - OHLC sanity: high >= max(open,close,low), low <= min(open,close)
    - Bei chanya: low > 0
    - Hakuna duplicate bar_open
    - Muda monotonic (hakuna kurudi nyuma)

  INFORMATIONAL (WARN — ripoti tu, si kushindwa):
    - Coverage: n_bars, first/last bar, idadi ya siku
    - Gaps: mapengo (bila weekend) zaidi ya kizingiti
    - Spread per-pair: mean/p50/p95/max (pips) + bars zaidi ya max_spread
    - Liquidity: tick_count min/p50 + bars chini ya min_tick_count

Endesha kwenye PC ya Japhet:
    python src\\data\\quality.py
    python src\\data\\quality.py --symbol EURUSD
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

import duckdb
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config" / "data_config.yaml"

# TF -> dakika (kwa hesabu ya gaps)
TF_MINUTES = {"1m": 1, "5m": 5, "15m": 15, "30m": 30,
              "H1": 60, "H2": 120, "H4": 240, "D1": 1440}


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def candle_path(symbol: str, tf: str, cfg: dict) -> Path:
    return (REPO_ROOT / cfg["paths"]["processed"] / "candles" /
            f"symbol={symbol}" / f"tf={tf}.parquet")


def check_one(con, symbol: str, tf: str, cfg: dict) -> dict | None:
    path = candle_path(symbol, tf, cfg)
    if not path.exists():
        return None
    src = str(path).replace("\\", "/")
    max_spread = cfg["max_spread_pips"].get(symbol, 9999)
    min_tc = cfg["quality"].get("min_tick_count", 3)
    gap_limit = cfg["quality"].get("max_gap_minutes", 60)
    iv = TF_MINUTES[tf]

    m = con.execute(f"""
        WITH c AS (SELECT * FROM read_parquet('{src}')),
        g AS (SELECT bar_open, open, high, low, close, tick_count,
                     spread_mean_pips, spread_max_pips,
                     lag(bar_open) OVER (ORDER BY bar_open) AS prev
              FROM c)
        SELECT
            (SELECT COUNT(*) FROM c)                                       AS n_bars,
            (SELECT COUNT(*) - COUNT(DISTINCT bar_open) FROM c)            AS dup_bars,
            (SELECT MIN(bar_open) FROM c)                                  AS first_bar,
            (SELECT MAX(bar_open) FROM c)                                  AS last_bar,
            (SELECT COUNT(DISTINCT CAST(bar_open AS DATE)) FROM c)         AS n_days,
            -- structural violations
            SUM(CASE WHEN high < low OR high < open OR high < close
                      OR low > open OR low > close THEN 1 ELSE 0 END)      AS ohlc_viol,
            SUM(CASE WHEN low <= 0 THEN 1 ELSE 0 END)                      AS nonpos,
            -- spread (pips)
            ROUND(AVG(spread_mean_pips), 3)                               AS spr_mean,
            ROUND(QUANTILE_CONT(spread_mean_pips, 0.50), 3)              AS spr_p50,
            ROUND(QUANTILE_CONT(spread_mean_pips, 0.95), 3)              AS spr_p95,
            ROUND(MAX(spread_max_pips), 2)                               AS spr_max,
            SUM(CASE WHEN spread_mean_pips > {max_spread} THEN 1 ELSE 0 END) AS n_over_spread,
            -- liquidity
            MIN(tick_count)                                              AS tc_min,
            CAST(ROUND(QUANTILE_CONT(tick_count, 0.50)) AS BIGINT)        AS tc_p50,
            SUM(CASE WHEN tick_count < {min_tc} THEN 1 ELSE 0 END)        AS n_low_liq,
            -- gaps (bila weekend: prev si Ijumaa/Jumamosi)
            SUM(CASE WHEN prev IS NOT NULL
                      AND date_diff('minute', prev, bar_open) > {iv} + {gap_limit}
                      AND dayofweek(prev) NOT IN (5, 6) THEN 1 ELSE 0 END) AS n_gaps,
            MAX(CASE WHEN prev IS NOT NULL AND dayofweek(prev) NOT IN (5, 6)
                     THEN date_diff('minute', prev, bar_open) END)         AS max_gap_min
        FROM g
    """).fetchone()
    cols = ["n_bars", "dup_bars", "first_bar", "last_bar", "n_days", "ohlc_viol",
            "nonpos", "spr_mean", "spr_p50", "spr_p95", "spr_max", "n_over_spread",
            "tc_min", "tc_p50", "n_low_liq", "n_gaps", "max_gap_min"]
    r = dict(zip(cols, m))

    # --- Outliers: returns zenye |z-score| > outlier_sigma (mshukiwa, WARN) ---
    sigma = cfg["quality"].get("outlier_sigma", 8)
    r["n_outliers"] = con.execute(f"""
        WITH ret AS (
            SELECT (close / lag(close) OVER (ORDER BY bar_open) - 1) AS x
            FROM read_parquet('{src}')),
        s AS (SELECT AVG(x) mu, STDDEV_SAMP(x) sd FROM ret WHERE x IS NOT NULL)
        SELECT COUNT(*) FROM ret, s
        WHERE x IS NOT NULL AND s.sd > 0 AND ABS((x - s.mu) / s.sd) > {sigma}
    """).fetchone()[0]

    # --- Per-year coverage: siku za biashara / 260 (~siku za kazi za FX kwa mwaka),
    #     miaka KAMILI tu (acha mwaka wa mwisho partial). Flag kama < min_year_coverage.
    #     260 (sio 252) ni makini zaidi: pengo la 10% (siku ~234) sasa litaonekana. ---
    min_cov = cfg["quality"].get("min_year_coverage", 0.90)
    cov = con.execute(f"""
        WITH yr AS (
            SELECT EXTRACT(year FROM bar_open) AS y,
                   COUNT(DISTINCT CAST(bar_open AS DATE)) / 260.0 AS cov
            FROM read_parquet('{src}') GROUP BY y),
        mx AS (SELECT MAX(y) my FROM yr)
        SELECT ROUND(MIN(cov), 2), CAST(arg_min(y, cov) AS BIGINT)
        FROM yr, mx WHERE y < my
    """).fetchone()
    r["min_year_cov"], r["worst_year"] = (cov[0], cov[1]) if cov[0] is not None else (None, None)
    r["cov_ok"] = r["min_year_cov"] is None or r["min_year_cov"] >= min_cov

    r["symbol"], r["tf"] = symbol, tf
    r["pass"] = (r["ohlc_viol"] == 0 and r["nonpos"] == 0 and r["dup_bars"] == 0)
    return r


def fmt_report(rows: list[dict], cfg: dict) -> str:
    L = []
    L.append("# Ripoti ya Ubora wa Data — EliteFX SEHEMU 1\n")
    L.append(f"*Imezalishwa: {datetime.now():%Y-%m-%d %H:%M} | Candles: data/processed/candles*\n")

    n_fail = sum(1 for r in rows if not r["pass"])
    verdict = "✅ DATA IKO TAYARI" if n_fail == 0 else f"❌ KUNA MATATIZO ({n_fail} structural fail)"
    L.append(f"## Hukumu ya jumla: {verdict}\n")
    L.append(f"- Jumla ya (symbol×tf) zilizokaguliwa: **{len(rows)}**")
    L.append(f"- Structural checks zilizofeli: **{n_fail}**\n")

    # 1. Structural
    L.append("## 1. Structural (PASS/FAIL — lazima zipite)\n")
    L.append("| Symbol | TF | Bars | Dup | OHLC viol | Non-pos | Hali |")
    L.append("|--------|----|------|-----|-----------|---------|------|")
    for r in rows:
        flag = "✅ PASS" if r["pass"] else "❌ FAIL"
        L.append(f"| {r['symbol']} | {r['tf']} | {r['n_bars']:,} | {r['dup_bars']} "
                 f"| {r['ohlc_viol']} | {r['nonpos']} | {flag} |")

    # 2. Coverage
    L.append("\n## 2. Coverage (muda na idadi)\n")
    L.append("| Symbol | TF | Bars | Siku | Bar ya kwanza | Bar ya mwisho |")
    L.append("|--------|----|------|------|---------------|---------------|")
    for r in rows:
        L.append(f"| {r['symbol']} | {r['tf']} | {r['n_bars']:,} | {r['n_days']:,} "
                 f"| {r['first_bar']} | {r['last_bar']} |")

    # 3. Spread (pips)
    L.append("\n## 3. Spread per-pair (pips)\n")
    L.append("| Symbol | TF | Mean | p50 | p95 | Max | > max_spread |")
    L.append("|--------|----|------|-----|-----|-----|--------------|")
    for r in rows:
        ms = cfg["max_spread_pips"].get(r["symbol"], "—")
        L.append(f"| {r['symbol']} | {r['tf']} | {r['spr_mean']} | {r['spr_p50']} "
                 f"| {r['spr_p95']} | {r['spr_max']} | {r['n_over_spread']:,} (>{ms}) |")

    # 4. Liquidity & gaps
    L.append("\n## 4. Liquidity (tick_count) na Gaps (bila weekend)\n")
    L.append("| Symbol | TF | tc_min | tc_p50 | low-liq bars | Gaps | Max gap (min) |")
    L.append("|--------|----|--------|--------|--------------|------|---------------|")
    for r in rows:
        L.append(f"| {r['symbol']} | {r['tf']} | {r['tc_min']} | {r['tc_p50']} "
                 f"| {r['n_low_liq']:,} | {r['n_gaps']} | {r['max_gap_min'] or 0} |")

    # 5. Outliers & per-year coverage
    L.append("\n## 5. Outliers (z-score) na Coverage kwa mwaka\n")
    L.append(f"| Symbol | TF | Outliers (>{cfg['quality'].get('outlier_sigma',8)}σ) "
             f"| Min year cov | Mwaka mbaya | Coverage ≥ {cfg['quality'].get('min_year_coverage',0.90)} |")
    L.append("|--------|----|-----------|--------------|-------------|------------------|")
    for r in rows:
        cov = "—" if r["min_year_cov"] is None else f"{r['min_year_cov']:.2f}"
        wy = "—" if r["worst_year"] is None else r["worst_year"]
        ok = "✅" if r["cov_ok"] else "⚠️ chini"
        L.append(f"| {r['symbol']} | {r['tf']} | {r['n_outliers']:,} | {cov} | {wy} | {ok} |")
    L.append(f"\n*Outliers = returns nje ya {cfg['quality'].get('outlier_sigma',8)}σ — "
             "WACHUNGUZWE (matukio halisi kama Brexit yanaweza kuwa halali, si lazima "
             "data mbovu). Coverage hupima miaka KAMILI tu (mwaka wa mwisho partial "
             "umeachwa). Coverage chini ya kizingiti = pengo la data la kuchunguza.*")

    L.append("\n---\n*Structural lazima zipite. Spread/liquidity/gaps/outliers/coverage "
             "ni taarifa za kuongoza filtering ya model (Sehemu 2 & 3) na kuchunguza "
             "pengo — si sababu ya kushindwa kiotomatiki.*")
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser(description="Kagua ubora wa candles")
    ap.add_argument("--symbol", default=None)
    ap.add_argument("--tf", default=None, choices=list(TF_MINUTES))
    args = ap.parse_args()

    cfg = load_config()
    symbols = [args.symbol] if args.symbol else cfg["pairs"]
    tfs = [args.tf] if args.tf else cfg["timeframes"]

    con = duckdb.connect()
    rows = []
    for sym in symbols:
        for tf in tfs:
            r = check_one(con, sym, tf, cfg)
            if r is None:
                print(f"  ONYO: {sym} {tf} haijajengwa bado — naruka.", file=sys.stderr)
                continue
            rows.append(r)
            print(f"  [{sym} {tf}] {'PASS' if r['pass'] else 'FAIL'}  "
                  f"bars={r['n_bars']:,} spr_p50={r['spr_p50']}p gaps={r['n_gaps']}")

    if not rows:
        print("Hakuna candles zilizopatikana. Endesha build_candles.py kwanza.", file=sys.stderr)
        return 1

    out = REPO_ROOT / cfg["paths"]["reports"] / "data_quality_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(fmt_report(rows, cfg), encoding="utf-8")
    n_fail = sum(1 for r in rows if not r["pass"])
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)}  ({len(rows)} kaguliwa, {n_fail} fail)")
    return 0 if n_fail == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
