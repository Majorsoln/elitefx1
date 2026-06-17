"""
feature_diagnostics.py — Uthibitisho wa KITAKWIMU wa features kabla ya modeling.

EDA (eda.py) ni descriptive. Hii inajibu maswali ya inferential ambayo Model 1 & 2
zinategemea — KABLA ya kujenga model:

  1. MOMENTS         skew/kurtosis za returns -> je HMM (Gaussian) ni sahihi? (Model 1)
  2. VOL CLUSTERING  ACF ya r^2 -> je regimes/vol-clustering zipo kweli? (huhalalisha HMM)
  3. IMBALANCE IC    je volume_imbalance INATABIRI return ya bar inayofuata? (Model 2)
                     NO-LOOKAHEAD: signal_t dhidi ya return_{t+1} (lead), si ya sasa.
  4. CORR STABILITY  je correlation ni thabiti kwa muda? (Compliance groups, Sehemu 5)

DuckDB pekee (skewness/kurtosis/corr ni native). Log-returns kwa stats (standard).
Inatoa reports/feature_diagnostics.md

Endesha kwenye PC ya Japhet:
    python src\\data\\feature_diagnostics.py
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


def _path(cfg, sym, tf) -> str:
    p = (REPO_ROOT / cfg["paths"]["processed"] / "candles" /
         f"symbol={sym}" / f"tf={tf}.parquet")
    return str(p).replace("\\", "/")


def _glob(cfg, tf) -> str:
    p = REPO_ROOT / cfg["paths"]["processed"] / "candles" / "symbol=*" / f"tf={tf}.parquet"
    return str(p).replace("\\", "/")


# ---------- 1. Distribution moments (HMM normality) ----------
def sec_moments(con, cfg, pairs) -> list[str]:
    L = ["## 1. Distribution Moments (D1 log-returns) — je HMM ya Gaussian ni sahihi?\n"]
    L.append("| Pair | Mean % | Std % | Skewness | Excess kurtosis | Min % | Max % |")
    L.append("|------|--------|-------|----------|-----------------|-------|-------|")
    fat = 0
    for s in pairs:
        r = con.execute(f"""
            WITH r AS (SELECT ln(close / lag(close) OVER (ORDER BY bar_open)) AS lr
                       FROM read_parquet('{_path(cfg, s, "D1")}'))
            SELECT ROUND(AVG(lr)*100, 4), ROUND(STDDEV_SAMP(lr)*100, 3),
                   ROUND(skewness(lr), 2), ROUND(kurtosis(lr), 2),
                   ROUND(MIN(lr)*100, 2), ROUND(MAX(lr)*100, 2)
            FROM r WHERE lr IS NOT NULL
        """).fetchone()
        flag = "  ⬅️ fat tails" if r[3] is not None and r[3] > 1.0 else ""
        if r[3] and r[3] > 1.0:
            fat += 1
        L.append(f"| {s} | {r[0]} | {r[1]} | {r[2]} | {r[3]}{flag} | {r[4]} | {r[5]} |")
    L.append(f"\n*Normal: skew=0, excess kurtosis=0. **{fat}/{len(pairs)}** zina excess "
             "kurtosis > 1 (fat tails) → Gaussian HMM itakosea tails. **Ushauri:** tumia "
             "Student-t emissions au standardize returns kwa rolling-vol kabla ya HMM. "
             "Skew hasi = matukio ya kuanguka makubwa kuliko ya kupanda.*\n")
    return L


# ---------- 2. Volatility clustering (ACF r^2) ----------
def sec_vol_clustering(con, cfg, pairs) -> list[str]:
    L = ["## 2. Volatility Clustering — ACF ya r² (huhalalisha regime/HMM)\n"]
    L.append("| Pair | ACF r (lag1) | ACF r² lag1 | lag5 | lag10 | lag20 |")
    L.append("|------|--------------|-------------|------|-------|-------|")
    clustered = 0
    for s in pairs:
        r = con.execute(f"""
            WITH r AS (
                SELECT bar_open, ln(close / lag(close) OVER (ORDER BY bar_open)) AS lr
                FROM read_parquet('{_path(cfg, s, "D1")}')),
            v AS (SELECT bar_open, lr, lr*lr AS sq FROM r WHERE lr IS NOT NULL),
            lg AS (
                SELECT lr, lag(lr,1) OVER (ORDER BY bar_open) AS lr1,
                       sq,  lag(sq,1)  OVER (ORDER BY bar_open) AS s1,
                            lag(sq,5)  OVER (ORDER BY bar_open) AS s5,
                            lag(sq,10) OVER (ORDER BY bar_open) AS s10,
                            lag(sq,20) OVER (ORDER BY bar_open) AS s20
                FROM v)
            SELECT ROUND(corr(lr, lr1), 3), ROUND(corr(sq, s1), 3),
                   ROUND(corr(sq, s5), 3), ROUND(corr(sq, s10), 3), ROUND(corr(sq, s20), 3)
            FROM lg
        """).fetchone()
        if r[1] and r[1] > 0.05:
            clustered += 1
        L.append(f"| {s} | {r[0]} | **{r[1]}** | {r[2]} | {r[3]} | {r[4]} |")
    L.append(f"\n*ACF ya r (returns) ≈ 0 = soko efficient (hakuna mean-reversion rahisi). "
             f"ACF ya r² > 0 = **vol clustering** (vol kubwa inafuatwa na vol kubwa) → "
             f"regimes zipo → **HMM/Model 1 ina msingi.** {clustered}/{len(pairs)} zina "
             "ACF r² lag1 > 0.05.*\n")
    return L


# ---------- 3. volume_imbalance IC (Model 2 predictive value) ----------
def sec_imbalance_ic(con, cfg, pairs, tfs=("15m", "30m")) -> list[str]:
    L = ["## 3. `volume_imbalance` IC — je inatabiri return ya bar inayofuata? (Model 2)\n"]
    L.append("> NO-LOOKAHEAD: imbalance ya bar `t` (inajulikana baada ya t kufunga) dhidi "
             "ya return ya bar `t+1` (lead). Contemporaneous = ndani ya bar `t` (sanity).\n")
    L.append("| Pair | TF | Contemp. corr | **Predictive IC** | Hit-rate (dir.) | n |")
    L.append("|------|----|---------------|-------------------|-----------------|---|")
    for s in pairs:
        for tf in tfs:
            r = con.execute(f"""
                WITH b AS (
                    SELECT bar_open, open, close, volume_imbalance AS imb
                    FROM read_parquet('{_path(cfg, s, tf)}')),
                x AS (
                    SELECT imb,
                           close / open - 1                                   AS ret_inbar,
                           lead(close) OVER (ORDER BY bar_open) / close - 1    AS ret_next
                    FROM b)
                SELECT ROUND(corr(imb, ret_inbar), 4),
                       ROUND(corr(imb, ret_next),  4),
                       ROUND(AVG(CASE WHEN sign(imb) = sign(ret_next) THEN 1.0 ELSE 0.0 END), 4),
                       COUNT(*)
                FROM x
                WHERE imb IS NOT NULL AND imb <> 0 AND ret_next IS NOT NULL
            """).fetchone()
            ic = r[1]
            star = "  ⬅️" if ic is not None and abs(ic) >= 0.02 else ""
            L.append(f"| {s} | {tf} | {r[0]} | **{ic}**{star} | {r[2]} | {r[3]:,} |")
    L.append("\n*Contemp. corr +ve = imbalance inaakisi move ya bar yenyewe (sanity). "
             "**Predictive IC** ndio muhimu: ≈0 = haina thamani ya kutabiri; |IC|≥0.02 "
             "thabiti kwa pairs = ina edge ndogo (FX microstructure IC huwa ndogo). "
             "Hit-rate > 0.50 = mwelekeo sahihi zaidi ya nasibu. **Kama IC≈0 kote → "
             "Model 2 isitegemee imbalance kama feature kuu.**\n")
    return L


# ---------- 4. Correlation stability (Compliance groups) ----------
def sec_corr_stability(con, cfg, pairs) -> list[str]:
    L = ["## 4. Correlation Stability — je groups za static zinafaa? (Compliance)\n"]
    # jenga wide: date x pair -> log-return
    cols = ", ".join(f"MAX(CASE WHEN symbol='{s}' THEN lr END) AS \"{s}\"" for s in pairs)
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE w AS
        WITH r AS (
            SELECT symbol, CAST(bar_open AS DATE) AS d,
                   ln(close / lag(close) OVER (PARTITION BY symbol ORDER BY bar_open)) AS lr
            FROM read_parquet('{_glob(cfg, "D1")}'))
        SELECT d, {cols} FROM r GROUP BY d
    """)
    # jozi za kuvutia (kutoka EDA): zionyeshe drift kati ya vipindi
    pairs_of_interest = [
        ("AUDUSD", "NZDUSD"), ("EURUSD", "USDCHF"), ("GBPUSD", "EURGBP"),
        ("EURJPY", "EURGBP"), ("EURUSD", "GBPUSD"), ("USDJPY", "USDCHF"),
    ]
    L.append("| Jozi | 2016–2020 | 2021–2026 | Δ (drift) |")
    L.append("|------|-----------|-----------|-----------|")
    for a, b in pairs_of_interest:
        c1 = con.execute(f"SELECT corr(\"{a}\",\"{b}\") FROM w WHERE d < DATE '2021-01-01'").fetchone()[0]
        c2 = con.execute(f"SELECT corr(\"{a}\",\"{b}\") FROM w WHERE d >= DATE '2021-01-01'").fetchone()[0]
        c1 = round(c1, 2) if c1 is not None else None
        c2 = round(c2, 2) if c2 is not None else None
        d = round(abs(c1 - c2), 2) if (c1 is not None and c2 is not None) else "—"
        flag = "  ⬅️ unstable" if isinstance(d, float) and d >= 0.20 else ""
        L.append(f"| {a}–{b} | {c1} | {c2} | {d}{flag} |")
    L.append("\n*Δ kubwa = correlation INABADILIKA kwa muda → groups za static (config) "
             "hazitoshi. **Ushauri (Sehemu 5):** tumia rolling correlation au net-currency "
             "exposure badala ya makundi ya kudumu yaliyowekwa kwa mkono.*\n")
    return L


def main() -> int:
    cfg = load_config()
    pairs = cfg["pairs"]
    if not (REPO_ROOT / cfg["paths"]["processed"] / "candles").exists():
        print("HITILAFU: candles hazipo. Endesha build_candles.py kwanza.", file=sys.stderr)
        return 1

    con = duckdb.connect()
    con.execute("SET preserve_insertion_order=false")
    out = ["# Feature Diagnostics — EliteFX SEHEMU 1\n",
           f"*Imezalishwa: {datetime.now():%Y-%m-%d %H:%M} | Uthibitisho wa kitakwimu "
           "kabla ya modeling*\n"]

    out += sec_moments(con, cfg, pairs);         print("  [1/4] moments — done")
    out += sec_vol_clustering(con, cfg, pairs);  print("  [2/4] vol clustering — done")
    out += sec_imbalance_ic(con, cfg, pairs);    print("  [3/4] imbalance IC — done")
    out += sec_corr_stability(con, cfg, pairs);  print("  [4/4] corr stability — done")

    path = REPO_ROOT / cfg["paths"]["reports"] / "feature_diagnostics.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(out), encoding="utf-8")
    con.close()
    print(f"\nRipoti: {path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
