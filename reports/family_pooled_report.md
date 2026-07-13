# Family-Pooled Holdout Test — C2-WATCH (HOLDOUT)

*2026-07-13 20:23 | design: reports/family_pooled_design.md | TF=H4 | m=1 single-hypothesis | reuse-only (episodes/_mask_context/pvalue_boot ZERO changes; load_window +ts additive)*

> **H1 (pre-registered):** compression-H4 family (cells 4, risk-normalized stream moja) ina EV chanya net-of-costs. **Criterion:** pvalue_boot(B=50k) < 0.05 NA pooled EV_R > 0 (design §0).


## Registration (design §3.3)

- reg string: `FAMILY-POOLED-C2WATCH-H4|nr4_inside|GBPJPY|1.5|1.5|no-LATE|None|nr7_break|EURGBP|1.5|1.0|no-LATE|None|nr7_break|EURJPY|1.0|3.0|no-LATE|None|nr7_break|AUDUSD|1.5|3.0|no-LATE|None`
- seed (deterministic): `116818170447252` · B=50000 · mean_block=3 · α=0.05
- pairs missing (no window): none

## Fixed universe (§1)

| rep | event | pair | SL | TP | filter |
|-----|-------|------|----|----|--------|
| REP-1 | nr4_inside | GBPJPY | 1.5 | 1.5 | no-LATE |
| REP-2 | nr7_break | EURGBP | 1.5 | 1.0 | no-LATE |
| REP-3 | nr7_break | EURJPY | 1.0 | 3.0 | no-LATE |
| REP-4 | nr7_break | AUDUSD | 1.5 | 3.0 | no-LATE |

## Result (R-units, design §2-§4-§6)

- pooled N = **353** · EV_R = **+0.1098** · sd_R = 1.2735
- **p_boot = 0.05434** (RASMI) · p_z = 0.05265 (sensitivity) · p_atr = 0.05028 (ATR-unit sensitivity)
- 90% bootstrap CI ya EV_R: [-0.0053, +0.2187]
- **MDE screen ya REGISTRATION** (shrink 0.35, **N_exp=343** — design §4, F1): MDE=0.1131 vs forecast=0.0384 → FAIL (margin ×0.34)
  - descriptive (NON-gating) split-N screen (pooled N=353): MDE=0.1115 → FAIL (SIO screen ya registration — F1)
- descriptive (NON-gating): shares={'EURJPY': 0.27, 'AUDUSD': 0.22, 'EURGBP': 0.34, 'GBPJPY': 0.17} · timeout_share=0.07 · lag-1 ρ=+0.024 

### Per-rep EV_R (descriptive, NON-gating — N1)

| rep | pair | n | EV_R | sign |
|-----|------|---|------|------|
| REP-1 | GBPJPY | 61 | +0.0564 | + |
| REP-2 | EURGBP | 119 | +0.0629 | + |
| REP-3 | EURJPY | 96 | +0.1516 | + |
| REP-4 | AUDUSD | 77 | +0.1723 | + |

- 4/4 reps EV_R chanya (4/4 = mechanism evidence kali).

## VERDICT (pre-registered §6): **FAIL**

→ Family claim inakufa kwenye dirisha hili kwa heshima; C2-WATCH inabaki forward-only (path a). HAKUNA re-test ya compression-H4 kwenye 2025-01→2026-04 (design §6).

## Caveats (design §7 — verbatim record)

1. Confirmation, si discovery (family-era leak §A3-W3) → PROVISIONAL cap + forward gate.
2. Window overlap na STRAT-001/002 proof era → PASS = correlated evidence, si replication huru.
3. VALID estimates ni hot (VALID/TRAIN ~2×) → shrink = measured slope (0.346), si pessimism.
4. One-sided deal: shrink-0.35 truth → power 0.62; FAIL ~38% hata kama forecast ni sahihi.

*design: SCIENTIST-D reports/family_pooled_design.md · engine strategy_lab.pvalue_boot (wave1_referee_report.md) · reuse-only. Profitable != Tradable Edge. Protect capital first.*