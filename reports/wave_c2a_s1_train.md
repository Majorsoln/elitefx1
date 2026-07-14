# WAVE-C2-A — S1 TRAIN (grid FROZEN m=84; docs/WAVE_C2A_REGISTRATION.md)

*2026-07-14 09:50 | TF=30m | split=TRAIN (2016-2022 PEKEE) | cells=84 | context ON signals (_mask_context_dir, signal-bar i; NaN→excluded) | costs ndani ya episodes (spread+slip) | MIN_N=30*

> **UAMINIFU:** S1 = TRAIN EXPLORATION — hakuna p-value/FDR hapa; namba zote ni in-sample. Uthibitisho = S2 (family-pooled + BH-FDR kwenye VALIDATION) → C2-6 freeze → HOLDOUT one-shot. LESSON-001/002/029. Profitable != Tradable Edge.


## Muhtasari kwa hypothesis

| hypothesis | cells | cells N>=MIN_N | jumla N | EV>0 cells | median EV net | median cost_share |
|------------|-------|----------------|---------|------------|----------------|--------------------|
| HC2-01 ALIGNED-COMPRESSION | 40 | 40 | 58,022 | 0/40 | -1.533 | 6.67 |
| HC2-03 TREND-PULLBACK-RESUME | 24 | 24 | 17,794 | 7/24 | -0.649 | 2.02 |
| HC2-06 HTF-SR-FADE | 20 | 6 | 389 | 3/6 | -0.809 | 0.24 |

## Candidates zenye EV_net>0 (N>=MIN_N; in-sample TRAIN — SI survivors)

| hypothesis | trigger | pair | SL | TP | N | EV net | gross | cost_share | win% | PF | timeout% |
|------------|---------|------|----|----|---|--------|-------|------------|------|----|----------|
| HC2-06 | bb_fade | EURGBP | 1.5 | 1.5 | 32 | +4.487 | +5.465 | 0.1791 | 65.6 | 2.054 | 0 |
| HC2-06 | bb_fade | EURGBP | 1.0 | 1.5 | 32 | +3.061 | +4.040 | 0.2423 | 50.0 | 1.73 | 0 |
| HC2-03 | trend_resume | EURUSD | 1.0 | 3.0 | 809 | +0.410 | +0.883 | 0.5352 | 28.4 | 1.054 | 5 |
| HC2-03 | trend_resume | EURUSD | 1.5 | 3.0 | 745 | +0.376 | +0.852 | 0.5592 | 37.0 | 1.039 | 9 |
| HC2-03 | rsi2_pullback | EURUSD | 1.0 | 2.0 | 619 | +0.279 | +0.719 | 0.6122 | 36.2 | 1.042 | 1 |
| HC2-03 | rsi2_pullback | EURUSD | 1.5 | 2.0 | 584 | +0.183 | +0.621 | 0.7056 | 45.4 | 1.022 | 3 |
| HC2-03 | rsi2_pullback | EURUSD | 1.0 | 3.0 | 582 | +0.167 | +0.608 | 0.725 | 28.0 | 1.023 | 3 |
| HC2-03 | trend_resume | EURUSD | 1.5 | 2.0 | 807 | +0.119 | +0.594 | 0.7996 | 45.6 | 1.014 | 4 |
| HC2-03 | trend_resume | EURUSD | 1.0 | 2.0 | 861 | +0.108 | +0.579 | 0.8136 | 35.8 | 1.016 | 2 |
| HC2-06 | bb_fade | AUDUSD | 1.0 | 1.5 | 31 | +0.058 | +1.189 | 0.951 | 45.2 | 1.01 | 0 |

*Cells chanya: 10/84. Next: S2 = kila hypothesis kama FAMILY moja (pool R, mtindo wa family_pooled) kwenye VALIDATION + BH-FDR (Chief). Grid frozen — hakuna cell mpya baada ya hapa.*