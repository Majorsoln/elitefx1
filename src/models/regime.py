"""
regime.py — MODEL 1: Regime/Context Detector (DOCTRINE §3-4, §9).

Model 1 SI mtabiri wa mwelekeo — ni **detector ya hali ya sasa.** Output = muktadha
kwa Model 2: vol-state × structure-state → regimes 4:
    LV-RANGE · LV-TREND · HV-RANGE · HV-TREND
  (vol_hi = rolling-vol ≥ median; trend = Efficiency-Ratio ≥ median; per pair/tf — hakuna
   parameter ya kutune, median split tu → kuepuka overfit.)

Hii ni DESCRIPTIVE (deterministic), si prediction → hakuna Phase B kwa label zenyewe.
Tunathibitisha mambo MAWILI ya kuhalalisha regime detector:
  1. PERSISTENCE — je regime inadumu? (P(stay) >> baseline = clustering → muktadha ni
     informative). Vol clustering (ACF r²>0) inatabiri hili.
  2. VOL-STATE MAGNITUDE — je HIGH-vol ina |forward return| kubwa zaidi? (= edge yetu
     IC 0.19 kwenye ngazi ya regime).

NO-LOOKAHEAD: vol/ER bar t (past+current); forward |ret| t→t+1.

Endesha (PC ya Japhet):  python src/models/regime.py
Self-test (popote):       python src/models/regime.py --self-test
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]

TFS = ["D1", "H4", "H1"]
WIN = {"D1": 20, "H4": 20, "H1": 24}        # window ya vol & Efficiency Ratio
REGIME_NAMES = {0: "LV-RANGE", 1: "LV-TREND", 2: "HV-RANGE", 3: "HV-TREND"}


def label_regimes(vol, er):
    """Median split (hakuna tuning): regime = 2·vol_hi + trend. Rudisha int array 0..3."""
    vhi = (vol >= np.nanmedian(vol)).astype(int)
    trend = (er >= np.nanmedian(er)).astype(int)
    return 2 * vhi + trend, vhi


def characterize(regime, vhi, fwd_abs):
    """Rudisha: pct kila regime, P(stay), baseline, mean|fwd| HIGH vs LOW vol."""
    n = len(regime)
    pct = {r: float((regime == r).mean()) for r in range(4)}
    # persistence: P(regime_{t+1}==regime_t)
    stay = float((regime[1:] == regime[:-1]).mean())
    base = float(sum(p * p for p in pct.values()))      # P(stay) kama i.i.d.
    # vol-state magnitude
    hi_m = float(np.nanmean(fwd_abs[vhi == 1]))
    lo_m = float(np.nanmean(fwd_abs[vhi == 0]))
    return pct, stay, base, hi_m, lo_m


# ───────────────────────── DATA PATH ─────────────────────────

def features_pair_tf(pair, tf):
    import polars as pl
    from data.dataset import load_candles
    n = WIN[tf]
    c = pl.col("close")
    df = load_candles(pair, tf).with_columns((c.log() - c.log().shift(1)).alias("ret"))
    df = df.with_columns(
        pl.col("ret").rolling_std(window_size=n).alias("vol"),
        ((c - c.shift(n)).abs()
         / (c - c.shift(1)).abs().rolling_sum(window_size=n)).alias("er"),
        (c.shift(-1).log() - c.log()).abs().alias("fwd_abs"),
    )
    d = df.select(["vol", "er", "fwd_abs"]).drop_nulls()
    return d["vol"].to_numpy(), d["er"].to_numpy(), d["fwd_abs"].to_numpy()


def run():
    from data.dataset import config
    cfg = config()
    if not (REPO_ROOT / cfg["paths"]["processed"] / "candles").exists():
        print("HITILAFU: candles hazipo.", file=sys.stderr); return 1

    L = ["# Model 1 — Regime Detector (vol × structure)\n",
         f"*Imezalishwa: {datetime.now():%Y-%m-%d %H:%M} | regime=vol-state×structure-state "
         "(median split) | descriptive, no-lookahead | pairs=9*\n",
         "> Regime 4: LV/HV (vol) × RANGE/TREND (Efficiency Ratio). Hakuna prediction ya "
         "direction — ni muktadha kwa Model 2. Thibitisha: (1) persistence, (2) vol-state magnitude.\n"]
    for tf in TFS:
        # aggregate
        pct_agg = {r: 0.0 for r in range(4)}; stay_s = base_s = hi_s = lo_s = 0.0; npairs = 0
        for p in cfg["pairs"]:
            try:
                vol, er, fa = features_pair_tf(p, tf)
            except FileNotFoundError:
                continue
            if len(vol) < 200:
                continue
            regime, vhi = label_regimes(vol, er)
            pct, stay, base, hi, lo = characterize(regime, vhi, fa)
            for r in range(4):
                pct_agg[r] += pct[r]
            stay_s += stay; base_s += base; hi_s += hi; lo_s += lo; npairs += 1
        if npairs == 0:
            continue
        L.append(f"\n## {tf} (window={WIN[tf]})\n")
        L.append("**Mgawanyo wa regime (wastani wa pairs):**\n")
        L.append("| Regime | % time |")
        L.append("|--------|--------|")
        for r in range(4):
            L.append(f"| {REGIME_NAMES[r]} | {100*pct_agg[r]/npairs:.1f}% |")
        stay = stay_s/npairs; base = base_s/npairs
        pflag = "✅ persistent" if stay - base >= 0.10 else "⚠️ dhaifu"
        L.append(f"\n**Persistence:** P(stay) = **{stay:.3f}** vs baseline (i.i.d.) {base:.3f} "
                 f"→ {pflag} (regime inadumu, sio kelele).")
        ratio = hi_s / lo_s if lo_s else 0
        vflag = "✅" if ratio >= 1.3 else "⚠️"
        L.append(f"\n**Vol-state magnitude:** mean \\|fwd ret\\| HIGH-vol = {hi_s/npairs:.5f} vs "
                 f"LOW-vol = {lo_s/npairs:.5f} → **{ratio:.2f}×** {vflag} (HIGH-vol = moves kubwa zaidi).")
    L.append("\n---\n*Regime detector ni msingi wa Model 1 (DOCTRINE §4). Persistence "
             "inathibitisha kujua regime ya SASA kunatoa taarifa ya karibu. Vol-state "
             "magnitude inathibitisha edge yetu (vol → ukubwa) kwenye ngazi ya regime. "
             "Model 2 itatumia regime kama muktadha (mean-reversion kwenye RANGE, n.k.).*")
    out = REPO_ROOT / cfg["paths"]["reports"] / "regime_detector.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"Ripoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """Planted: regimes persistent (blocks) + HIGH-vol ina |fwd| kubwa. Thibitisha detection."""
    rng = np.random.default_rng(0)
    n = 20000
    # vol inabadilika kwa blocks (persistent regimes)
    vol = np.repeat(rng.uniform(0, 1, n // 50 + 1), 50)[:n]
    er = np.repeat(rng.uniform(0, 1, n // 50 + 1), 50)[:n]
    regime, vhi = label_regimes(vol, er)
    fwd_abs = np.where(vhi == 1, rng.uniform(0, 0.02, n), rng.uniform(0, 0.005, n))  # HIGH-vol bigger
    pct, stay, base, hi, lo = characterize(regime, vhi, fwd_abs)
    print(f"  pct: {[round(pct[r],2) for r in range(4)]}")
    print(f"  P(stay)={stay:.3f} vs baseline={base:.3f} (persistence)")
    print(f"  |fwd| HIGH-vol={hi:.5f} vs LOW-vol={lo:.5f}  ratio={hi/lo:.2f}")
    ok = (stay - base) >= 0.10 and (hi / lo) >= 1.3
    print("\nSELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if "--self-test" in sys.argv:
        return self_test()
    sys.path.insert(0, str(REPO_ROOT / "src"))
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
