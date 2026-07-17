# R-MAP ATLAS — TABAKA 2 (behavioral map, TRAIN 2016-2022)

*grid: events 21 × pairs 12 × TF 3 × SL 3 × TP 4 | rows (cell×mwaka×vol_state)=186,512 | swap-adjusted (swing) | elapsed=345.2s | costs+swap ndani ya ev_net*

> **ATLAS ni RAMANI, si madai** (charter §Tabaka-2). TRAIN PEKEE — hakuna FDR (si hypothesis test). Breadth = pairs NGAPI zina EV+ (L-041 anti-selection-bias), si cell moja bora. Hypothesis yoyote kutoka hapa inapita gate: S2 pooled multi-pair → HOLDOUT one-shot.


## Top-20 (event × TF × vol_state) kwa BREADTH + YEAR-STABILITY (EV+ swing)

> Rank = (pairs EV+, miaka EV+). **Q4-screen:** miaka EV+ < 5/7 = breadth ya utegemezi wa mwaka mmoja-mbili (si lesson). vol_state=UNKNOWN (=2016 warmup, Q1) HAIMO hapa (ipo kwenye parquet).

| event | TF | vol_state | pairs EV+ | / tested | miaka EV+ | median N |
|-------|----|-----------|-----------|----------|-----------|----------|
| nr7_break | D1 | LOW | 10 | 12 | 7/7 | 4 |
| shock_follow | H4 | LOW | 10 | 12 | 5/7 | 8 |
| nr7_break | H4 | HIGH | 10 | 12 | 4/7 | 32 |
| lowvol_reversal | D1 | NORMAL | 10 | 12 | 3/7 | 6 |
| nr7_break | D1 | NORMAL | 9 | 12 | 5/7 | 4 |
| nr7_break | D1 | HIGH | 9 | 12 | 5/7 | 5 |
| shock_follow | D1 | HIGH | 8 | 12 | 6/7 | 2 |
| nr7_break | H4 | NORMAL | 7 | 12 | 6/7 | 28 |
| pullback_v2 | D1 | LOW | 7 | 12 | 6/7 | 5 |
| second_chance | H4 | HIGH | 7 | 12 | 5/7 | 10 |
| big_range_mo | H4 | HIGH | 7 | 12 | 5/7 | 35 |
| second_chance | D1 | NORMAL | 7 | 12 | 4/7 | 1 |
| shock_follow | D1 | LOW | 7 | 12 | 4/7 | 1 |
| nr7_break | H4 | LOW | 7 | 12 | 3/7 | 24 |
| nr4_inside | H4 | HIGH | 7 | 12 | 3/7 | 25 |
| mr_zscore | D1 | HIGH | 7 | 12 | 3/7 | 4 |
| engulf_extreme | D1 | NORMAL | 7 | 12 | 3/7 | 1 |
| squeeze_break | D1 | LOW | 7 | 12 | 3/7 | 3 |
| bb_fade | D1 | NORMAL | 6 | 12 | 6/7 | 3 |
| engulf_extreme | H4 | NORMAL | 6 | 12 | 5/7 | 7 |

## Breadth kwa event (combos za (TF×vol_state) zenye pair-yoyote EV+; UNKNOWN nje)

| event | regimes EV+ | / total |
|-------|-------------|---------|
| second_chance | 9 | 9 |
| shock_follow | 9 | 9 |
| rsi2_pullback | 9 | 9 |
| engulf_extreme | 9 | 9 |
| nr7_break | 9 | 9 |
| gap_fade | 9 | 9 |
| trend_resume | 8 | 9 |
| mr_zscore | 8 | 9 |
| lowvol_reversal | 7 | 9 |
| bb_fade | 7 | 9 |
| inside_break | 7 | 9 |
| nr4_inside | 7 | 9 |
| false_break | 7 | 9 |
| pullback_v2 | 6 | 9 |
| big_range_mo | 6 | 9 |
| squeeze_break | 6 | 9 |
| london_drift | 6 | 6 |
| session_orb | 5 | 6 |
| pattern_3lows | 5 | 9 |
| breakout_stop | 3 | 9 |
| jump_off | 2 | 9 |

## Tahadhari za ramani (§B quarantine — binding kwa lesson-generator)

- **Q1 (UNKNOWN=2016):** vol_state=UNKNOWN ni mwaka 2016 PEKEE (warmup ya terciles) — regime-label ya uongo. Imeondolewa kwenye ranking-tables hapo juu; ipo kwenye parquet kama data. Lesson-generator i-filter UNKNOWN.
- **Q2 (D1 session artifact):** `sess_top` kwa TF=D1 ni 'ASIA' 100% (hour(D1 bar)=00 daima) — ARTIFACT, si taarifa. H4 session = open-hour ya bar ya masaa 4 (coarse). Session-lessons zitumike kwa H1/intraday PEKEE.
- **Q3/Q5:** row moja ya atlas SI lesson (55%+ zina n<30); lessons = aggregations (N pamoja + miaka EV+ ≥5/7). MFE ya SL-exit ime-inflate (excursions inajumuisha bar ya exit nzima) — exit-lessons za walioshindwa kwa tahadhari.

*Malighafi kamili: data/strategies/rmap_train.parquet (mstari 1 kwa event×pair×tf×sl×tp×mwaka×vol_state; + MFE/MAE R medians kwa exit-lessons). Lesson-generator isome PARQUET (+ quarantine §B), KAMWE si report hii. Next (M3-3): Chief+STRATEGIST-M -> hypotheses zenye breadth+stability -> S2 pooled.*