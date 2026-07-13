# Family-Pooled Holdout Test — C2-WATCH (VALIDATION)

*2026-07-13 20:19 | design: reports/family_pooled_design.md | TF=H4 | m=1 single-hypothesis | reuse-only (episodes/_mask_context/pvalue_boot ZERO changes; load_window +ts additive)*

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

- pooled N = **531** · EV_R = **+0.3690** · sd_R = 1.2707
- **p_boot = 0.00002** (RASMI) · p_z = 0.00000 (sensitivity) · p_atr = 0.00002 (ATR-unit sensitivity)
- 90% bootstrap CI ya EV_R: [+0.2786, +0.4533]
- **MDE screen ya REGISTRATION** (shrink 0.35, **N_exp=342** — design §4, F1): MDE=0.1131 vs forecast=0.1292 → PASS (margin ×1.14)
  - descriptive (NON-gating) split-N screen (pooled N=531): MDE=0.0907 → PASS (SIO screen ya registration — F1)
- descriptive (NON-gating): shares={'AUDUSD': 0.22, 'EURJPY': 0.24, 'EURGBP': 0.34, 'GBPJPY': 0.2} · timeout_share=0.05 · lag-1 ρ=+0.020 

### Per-rep EV_R (descriptive, NON-gating — N1)

| rep | pair | n | EV_R | sign |
|-----|------|---|------|------|
| REP-1 | GBPJPY | 107 | +0.4349 | + |
| REP-2 | EURGBP | 182 | +0.2260 | + |
| REP-3 | EURJPY | 127 | +0.4722 | + |
| REP-4 | AUDUSD | 115 | +0.4201 | + |

- 4/4 reps EV_R chanya (4/4 = mechanism evidence kali).

## VERDICT (pre-registered §6): **PASS**

→ FAMILY claim = **PROVEN-OOS-PROVISIONAL (family level)**: inaidhinisha forward paper-trading ya reps 4 kama stream moja + priority ya R3/R8. HAIUNDI STRAT-00x, HAIRUHUSU capital, HAITHIBITISHI pair/cell binafsi (design §6).

## Caveats (design §7 — verbatim record)

1. Confirmation, si discovery (family-era leak §A3-W3) → PROVISIONAL cap + forward gate.
2. Window overlap na STRAT-001/002 proof era → PASS = correlated evidence, si replication huru.
3. VALID estimates ni hot (VALID/TRAIN ~2×) → shrink = measured slope (0.346), si pessimism.
4. One-sided deal: shrink-0.35 truth → power 0.62; FAIL ~38% hata kama forecast ni sahihi.

*design: SCIENTIST-D reports/family_pooled_design.md · engine strategy_lab.pvalue_boot (wave1_referee_report.md) · reuse-only. Profitable != Tradable Edge. Protect capital first.*