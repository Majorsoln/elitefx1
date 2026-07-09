# Strategy Lab — S1 candidates (TRAIN)

*2026-07-09 12:44 | TF=H1 | split=train | cells tested=2004 | candidates (N>=30)=2004 | costs ndani (episodes) | RANK=population view*

> **UAMINIFU:** hizi ni CANDIDATES, SIO strategies. TRAIN=in-sample; uthibitisho = S2 (walk-forward VALIDATION + BH-FDR) na S3 (HOLDOUT, mara moja). RED LINES: hakuna kuchagua kwa holdout; hakuna metric bila costs. LESSON-001/002/029/033/034. Profitable != Tradable Edge.


## Top candidates (population rank)

| event | pair | SL | TP | session | vol | N | EV net | win% | PF | maxDD | tr/day |
|-------|------|----|----|---------|-----|---|--------|------|----|-------|--------|
| nr7_break | GBPUSD | 2.0 | 3.0 | ('LONDON', 'NY') | HIGH | 168 | +12.761 | 57.1 | 1.595 | 650.3 | 0.09 |
| nr7_break | GBPUSD | 2.0 | 1.5 | ('LONDON', 'NY') | HIGH | 178 | +12.602 | 68.5 | 1.77 | 186.1 | 0.10 |
| nr7_break | GBPUSD | 1.0 | 1.5 | ('LONDON', 'NY') | HIGH | 182 | +11.201 | 54.4 | 1.856 | 192.5 | 0.10 |
| nr7_break | GBPUSD | 1.5 | 1.5 | ('LONDON', 'NY') | HIGH | 181 | +10.719 | 62.4 | 1.669 | 284.3 | 0.10 |
| nr7_break | GBPUSD | 2.0 | 2.0 | ('LONDON', 'NY') | HIGH | 174 | +10.188 | 62.6 | 1.51 | 416.7 | 0.10 |
| nr7_break | GBPUSD | 1.5 | 3.0 | ('LONDON', 'NY') | HIGH | 171 | +9.187 | 48.5 | 1.437 | 545.8 | 0.09 |
| nr7_break | GBPUSD | 2.0 | 1.5 | ('LONDON', 'NY') | None | 519 | +7.539 | 67.2 | 1.506 | 478.5 | 0.28 |
| nr7_break | GBPUSD | 1.0 | 3.0 | ('LONDON', 'NY') | HIGH | 173 | +8.961 | 37.6 | 1.504 | 492.8 | 0.10 |
| nr7_break | USDCAD | 2.0 | 3.0 | ('LONDON', 'NY') | HIGH | 106 | +9.732 | 56.6 | 1.558 | 356.6 | 0.06 |
| nr7_break | GBPUSD | 1.5 | 2.0 | ('LONDON', 'NY') | HIGH | 177 | +8.676 | 55.9 | 1.46 | 316.3 | 0.10 |
| nr7_break | USDCAD | 1.5 | 3.0 | ('LONDON', 'NY') | HIGH | 107 | +9.270 | 50.5 | 1.574 | 296.6 | 0.06 |
| nr7_break | GBPUSD | 2.0 | 2.0 | ('LONDON', 'NY') | None | 512 | +6.877 | 60.0 | 1.386 | 670.9 | 0.28 |
| nr7_break | GBPUSD | 1.0 | 2.0 | ('LONDON', 'NY') | HIGH | 178 | +8.221 | 44.9 | 1.513 | 251.1 | 0.10 |
| nr7_break | GBPUSD | 1.0 | 1.5 | ('LONDON', 'NY') | None | 532 | +6.649 | 53.2 | 1.579 | 375.1 | 0.29 |
| nr7_break | USDCAD | 2.0 | 2.0 | ('LONDON', 'NY') | None | 296 | +7.199 | 63.2 | 1.55 | 391.3 | 0.16 |
| nr7_break | GBPUSD | 2.0 | 3.0 | ('LONDON', 'NY') | None | 493 | +6.550 | 49.7 | 1.314 | 1047.4 | 0.27 |
| nr7_break | GBPUSD | 2.0 | 3.0 | no-LATE | HIGH | 452 | +6.536 | 51.1 | 1.279 | 992.5 | 0.25 |
| nr7_break | GBPUSD | 1.5 | 1.5 | ('LONDON', 'NY') | None | 525 | +6.323 | 61.0 | 1.447 | 457.1 | 0.29 |
| nr7_break | USDCAD | 1.5 | 2.0 | ('LONDON', 'NY') | None | 297 | +6.568 | 57.2 | 1.55 | 348.9 | 0.16 |
| shock_follow | EURJPY | 1.5 | 2.0 | ASIA | NORMAL | 50 | +9.497 | 60.0 | 1.83 | 113.8 | 0.03 |
| nr7_break | USDCAD | 1.5 | 1.5 | ('LONDON', 'NY') | None | 303 | +6.475 | 66.0 | 1.661 | 212.5 | 0.17 |
| nr7_break | GBPUSD | 1.0 | 1.0 | ('LONDON', 'NY') | HIGH | 188 | +7.011 | 62.8 | 1.646 | 99.4 | 0.10 |
| nr7_break | AUDUSD | 2.0 | 2.0 | ('LONDON', 'NY') | HIGH | 301 | +6.370 | 61.1 | 1.569 | 218.6 | 0.17 |
| nr7_break | GBPUSD | 1.0 | 3.0 | ('LONDON', 'NY') | None | 508 | +5.823 | 35.0 | 1.374 | 676.9 | 0.28 |
| nr7_break | USDCAD | 2.0 | 3.0 | ('LONDON', 'NY') | None | 285 | +6.363 | 50.9 | 1.399 | 504.5 | 0.16 |
| nr7_break | EURUSD | 1.0 | 3.0 | ('LONDON', 'NY') | None | 439 | +5.908 | 38.0 | 1.591 | 273.0 | 0.24 |
| second_chance | EURJPY | 1.5 | 3.0 | LATE | None | 294 | +6.285 | 46.3 | 1.376 | 327.9 | 0.16 |
| second_chance | EURJPY | 2.0 | 3.0 | LATE | None | 294 | +6.270 | 50.3 | 1.34 | 408.2 | 0.16 |
| nr7_break | GBPUSD | 1.5 | 2.0 | ('LONDON', 'NY') | None | 518 | +5.679 | 53.3 | 1.343 | 613.8 | 0.28 |
| nr7_break | GBPUSD | 2.0 | 1.0 | ('LONDON', 'NY') | HIGH | 186 | +6.762 | 74.7 | 1.483 | 186.1 | 0.10 |
| nr7_break | GBPUSD | 1.5 | 3.0 | ('LONDON', 'NY') | None | 501 | +5.637 | 43.7 | 1.293 | 1108.4 | 0.28 |
| nr7_break | GBPUSD | 1.0 | 2.0 | ('LONDON', 'NY') | None | 524 | +5.562 | 44.3 | 1.408 | 537.0 | 0.29 |
| nr7_break | AUDUSD | 1.5 | 2.0 | ('LONDON', 'NY') | HIGH | 303 | +5.997 | 56.8 | 1.578 | 150.3 | 0.17 |
| nr7_break | USDCAD | 2.0 | 1.5 | ('LONDON', 'NY') | None | 302 | +5.957 | 69.5 | 1.533 | 315.8 | 0.17 |
| shock_follow | EURJPY | 1.5 | 1.5 | ASIA | NORMAL | 50 | +8.526 | 66.0 | 1.9 | 113.8 | 0.03 |
| second_chance | EURJPY | 2.0 | 3.0 | LATE | LOW | 82 | +7.515 | 57.3 | 1.53 | 170.6 | 0.04 |
| nr7_break | EURUSD | 1.5 | 3.0 | ('LONDON', 'NY') | None | 430 | +5.460 | 45.6 | 1.429 | 340.8 | 0.24 |
| nr7_break | EURUSD | 2.0 | 3.0 | ('LONDON', 'NY') | None | 416 | +5.469 | 51.0 | 1.392 | 388.4 | 0.23 |
| nr7_break | USDCAD | 1.5 | 3.0 | ('LONDON', 'NY') | None | 289 | +5.810 | 45.0 | 1.402 | 698.2 | 0.16 |
| second_chance | EURJPY | 1.5 | 1.5 | LATE | LOW | 82 | +7.350 | 68.3 | 1.936 | 85.5 | 0.04 |

*S1 = candidates -> S2 walk-forward+FDR -> S3 holdout. Chief directive + GRID RULING.*