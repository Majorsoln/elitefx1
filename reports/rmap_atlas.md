# R-MAP ATLAS — TABAKA 2 (behavioral map, TRAIN 2016-2022)

*grid: events 21 × pairs 12 × TF 3 × SL 3 × TP 4 | rows (cell×mwaka×vol_state)=186,512 | swap-adjusted (swing) | elapsed=349.2s | costs+swap ndani ya ev_net*

> **ATLAS ni RAMANI, si madai** (charter §Tabaka-2). TRAIN PEKEE — hakuna FDR (si hypothesis test). Breadth = pairs NGAPI zina EV+ (L-041 anti-selection-bias), si cell moja bora. Hypothesis yoyote kutoka hapa inapita gate: S2 pooled multi-pair → HOLDOUT one-shot.


## Top-20 (event × TF × vol_state) kwa BREADTH ya pairs (EV+ swing)

| event | TF | vol_state | pairs EV+ | / tested |
|-------|----|-----------|-----------|----------|
| shock_follow | H4 | LOW | 10 | 12 |
| nr7_break | H4 | HIGH | 10 | 12 |
| lowvol_reversal | D1 | NORMAL | 10 | 12 |
| nr7_break | D1 | LOW | 10 | 12 |
| nr7_break | D1 | NORMAL | 9 | 12 |
| nr7_break | D1 | HIGH | 9 | 12 |
| inside_break | H4 | UNKNOWN | 8 | 12 |
| nr4_inside | H4 | UNKNOWN | 8 | 12 |
| false_break | H4 | UNKNOWN | 8 | 12 |
| mr_zscore | D1 | UNKNOWN | 8 | 12 |
| shock_follow | D1 | HIGH | 8 | 12 |
| inside_break | D1 | UNKNOWN | 8 | 12 |
| shock_follow | H1 | UNKNOWN | 7 | 12 |
| nr7_break | H1 | UNKNOWN | 7 | 12 |
| pullback_v2 | H4 | UNKNOWN | 7 | 12 |
| second_chance | H4 | HIGH | 7 | 12 |
| big_range_mo | H4 | HIGH | 7 | 12 |
| session_orb | H4 | UNKNOWN | 7 | 12 |
| bb_fade | H4 | UNKNOWN | 7 | 12 |
| nr7_break | H4 | UNKNOWN | 7 | 12 |

## Breadth kwa event (combos za (TF×vol_state) zenye pair-yoyote EV+)

| event | regimes EV+ | / total |
|-------|-------------|---------|
| second_chance | 12 | 12 |
| shock_follow | 12 | 12 |
| engulf_extreme | 12 | 12 |
| nr7_break | 12 | 12 |
| trend_resume | 11 | 12 |
| mr_zscore | 11 | 12 |
| rsi2_pullback | 11 | 11 |
| gap_fade | 11 | 12 |
| lowvol_reversal | 10 | 12 |
| bb_fade | 10 | 12 |
| inside_break | 10 | 12 |
| nr4_inside | 10 | 12 |
| false_break | 10 | 12 |
| pullback_v2 | 9 | 12 |
| big_range_mo | 9 | 12 |
| pattern_3lows | 8 | 12 |
| squeeze_break | 8 | 11 |
| london_drift | 8 | 8 |
| session_orb | 7 | 8 |
| breakout_stop | 5 | 12 |
| jump_off | 3 | 12 |

*Malighafi kamili: data/strategies/rmap_train.parquet (mstari 1 kwa event×pair×tf×sl×tp×mwaka×vol_state; + MFE/MAE R medians kwa exit-lessons). Next (M3-3): Chief+STRATEGIST-M -> hypotheses zenye breadth -> S2 pooled.*