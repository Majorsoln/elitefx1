# WAVE-B2 — HIGH-CONVICTION SELECTIVE-STRUCTURE @ H1 — S1 TRAIN GRID (FROZEN by Chief)

> **Msingi (PD + Chief, 2026-07-15):** mechanisms 2 zilizoonyesha edge HALISI per trade kwenye 30m
> (HC2-06 SR-fade: EURGBP EV+4.49 PF2.05; HC2-10 sweep: EURCHF gross+1.16) lakini zikaliwa na
> gharama/power — sasa kwenye **H1** (moves kubwa per trade → cost-ratio bora; recipe ya
> STRAT-001/002) na kwenye pairs zilizoonyesha gross+. **Trades chache, probability ya juu** (PD:
> "trade sio kila saa; tunahitaji highest possibility"). Frequency ya "sokoni kila siku" inatoka
> PORTFOLIO, si strategy moja. LESSON-039 (cost/move-ratio) + LESSON-007-nuance (rare = pooled S2).
> S1 TRAIN PEKEE. VALIDATION/HOLDOUT HAZIGUSWI. Grid FROZEN kabla ya S1.

## HB2-06 — HTF-SR-FADE @ H1
| Kipengele | Thamani (FROZEN) |
|---|---|
| Triggers | `bb_fade`, `engulf_extreme` (market, one-sided) |
| allow_long (signal bar i) | `isfinite & d1_dist_sup_atr<=0.5 & h4_trend_sign>=0` |
| allow_short (signal bar i) | `isfinite & d1_dist_res_atr<=0.5 & h4_trend_sign<=0` |
| TF / SL×TP / hold | **H1** / {1.0,1.5}×{1.5,2.0} / 16 bars |
| Pairs | EURGBP, EURCHF, USDCHF, AUDUSD, NZDUSD |
| Cells | 2×4×5 = **40** |

## HB2-10 — FAILED-BREAK-SWEEP @ H1
| Kipengele | Thamani (FROZEN) |
|---|---|
| Trigger | `false_break` (market; look=20, rearm=8 default) |
| allow_long / allow_short | `isfinite & d1_dist_sup_atr<=0.5` / `isfinite & d1_dist_res_atr<=0.5` (hakuna h4) |
| TF / SL×TP / hold | **H1** / {1.0,1.5}×{2.0,3.0} / 16 bars |
| Pairs | EURGBP, EURCHF, USDCHF, AUDUSD, NZDUSD |
| Cells | 1×4×5 = **20** |

**TOTAL m = 60.** NaN→allow=False (isfinite). **XAUUSD NJE kwa makusudi** (LESSON-039: fade-on-gold
mismatch — gross −24.6; gold inasubiri mechanisms za momentum). Costs ndani ya episodes.

## PREREQUISITE (infra ndogo — kabla ya S1)
1. **H1 context parquet:** htf_context iruhusu `--ltf H1` (H1 state za engine ZIPO; as-of backward
   join ile ile inazuia leakage — H4/D1 bar iliyoFUNGWA ≤ t). Operator ajenge context ya H1 kwa pairs 5+.
2. **Per-hypothesis TF kwenye runner:** HYPOTHESES zipate field `tf` (default "30m" — WAVE-A
   haiathiriki); load_window itumie tf ya hypothesis.

## S2 (baada ya S1) — POWER-BY-POOLING
Kila HB2 = FAMILY moja: cells za TRAIN net+ → pool R-normalized streams (mtindo `family_pooled`)
kwenye VALIDATION → test moja per family + BH-FDR (m=2 families). Hii ndiyo suluhu ya "rare setup,
provable evidence". Survivor → C2-6 HOLDOUT one-shot → strategy #3/#4.
