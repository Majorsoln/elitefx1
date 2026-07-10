# Strategy Lab — S1 candidates (TRAIN)

*2026-07-10 20:55 | TF=H1 | split=train | cells tested=2364 | candidates (N>=30)=2364 | costs ndani (episodes) | RANK=population view*

> **UAMINIFU:** hizi ni CANDIDATES, SIO strategies. TRAIN=in-sample; uthibitisho = S2 (walk-forward VALIDATION + BH-FDR) na S3 (HOLDOUT, mara moja). RED LINES: hakuna kuchagua kwa holdout; hakuna metric bila costs. LESSON-001/002/029/033/034. Profitable != Tradable Edge.


## Top candidates (population rank)

| event | pair | SL | TP | session | vol | N | EV net | win% | PF | maxDD | tr/day |
|-------|------|----|----|---------|-----|---|--------|------|----|-------|--------|
| nr7_break | GBPJPY | 1.0 | 2.0 | ('LONDON', 'NY') | HIGH | 214 | +12.559 | 44.4 | 1.567 | 518.1 | 0.10 |
| nr7_break | GBPJPY | 1.0 | 3.0 | ('LONDON', 'NY') | HIGH | 207 | +12.339 | 36.7 | 1.483 | 578.1 | 0.10 |
| nr7_break | GBPUSD | 2.0 | 3.0 | ('LONDON', 'NY') | HIGH | 168 | +12.761 | 57.1 | 1.595 | 650.3 | 0.09 |
| nr7_break | GBPUSD | 2.0 | 1.5 | ('LONDON', 'NY') | HIGH | 178 | +12.602 | 68.5 | 1.77 | 186.1 | 0.10 |
| nr7_break | GBPUSD | 1.0 | 1.5 | ('LONDON', 'NY') | HIGH | 182 | +11.201 | 54.4 | 1.856 | 192.5 | 0.10 |
| nr7_break | GBPUSD | 1.5 | 1.5 | ('LONDON', 'NY') | HIGH | 181 | +10.719 | 62.4 | 1.669 | 284.3 | 0.10 |
| nr7_break | GBPJPY | 1.0 | 1.5 | ('LONDON', 'NY') | HIGH | 218 | +9.845 | 50.9 | 1.478 | 518.1 | 0.10 |
| nr7_break | GBPUSD | 2.0 | 2.0 | ('LONDON', 'NY') | HIGH | 174 | +10.188 | 62.6 | 1.51 | 416.7 | 0.10 |
| nr7_break | GBPJPY | 1.0 | 3.0 | ('LONDON', 'NY') | None | 620 | +8.031 | 36.0 | 1.381 | 578.1 | 0.28 |
| nr7_break | GBPJPY | 1.5 | 1.5 | ('LONDON', 'NY') | None | 630 | +7.546 | 61.4 | 1.389 | 771.2 | 0.29 |
| nr7_break | GBPJPY | 1.0 | 1.5 | ('LONDON', 'NY') | None | 643 | +7.367 | 52.6 | 1.456 | 518.1 | 0.29 |
| nr7_break | GBPJPY | 1.5 | 3.0 | ('LONDON', 'NY') | None | 601 | +7.427 | 44.3 | 1.283 | 863.4 | 0.28 |
| nr7_break | GBPUSD | 1.5 | 3.0 | ('LONDON', 'NY') | HIGH | 171 | +9.187 | 48.5 | 1.437 | 545.8 | 0.09 |
| nr7_break | GBPUSD | 2.0 | 1.5 | ('LONDON', 'NY') | None | 519 | +7.539 | 67.2 | 1.506 | 478.5 | 0.28 |
| nr7_break | GBPJPY | 1.0 | 2.0 | ('LONDON', 'NY') | None | 634 | +7.173 | 43.7 | 1.385 | 518.1 | 0.29 |
| nr7_break | GBPUSD | 1.0 | 3.0 | ('LONDON', 'NY') | HIGH | 173 | +8.961 | 37.6 | 1.504 | 492.8 | 0.10 |
| nr7_break | USDCAD | 2.0 | 3.0 | ('LONDON', 'NY') | HIGH | 106 | +9.732 | 56.6 | 1.558 | 356.6 | 0.06 |
| nr7_break | GBPUSD | 1.5 | 2.0 | ('LONDON', 'NY') | HIGH | 177 | +8.676 | 55.9 | 1.46 | 316.3 | 0.10 |
| nr7_break | GBPJPY | 1.5 | 2.0 | ('LONDON', 'NY') | HIGH | 210 | +8.340 | 49.0 | 1.286 | 771.2 | 0.10 |
| nr7_break | USDCAD | 1.5 | 3.0 | ('LONDON', 'NY') | HIGH | 107 | +9.270 | 50.5 | 1.574 | 296.6 | 0.06 |
| nr7_break | GBPUSD | 2.0 | 2.0 | ('LONDON', 'NY') | None | 512 | +6.877 | 60.0 | 1.386 | 670.9 | 0.28 |
| nr7_break | GBPUSD | 1.0 | 2.0 | ('LONDON', 'NY') | HIGH | 178 | +8.221 | 44.9 | 1.513 | 251.1 | 0.10 |
| nr7_break | GBPJPY | 1.5 | 2.0 | ('LONDON', 'NY') | None | 619 | +6.556 | 51.9 | 1.282 | 771.2 | 0.28 |
| nr7_break | GBPUSD | 1.0 | 1.5 | ('LONDON', 'NY') | None | 532 | +6.649 | 53.2 | 1.579 | 375.1 | 0.29 |
| nr7_break | GBPJPY | 1.0 | 1.0 | ('LONDON', 'NY') | HIGH | 220 | +7.716 | 63.6 | 1.476 | 532.5 | 0.10 |
| nr7_break | USDCAD | 2.0 | 2.0 | ('LONDON', 'NY') | None | 296 | +7.199 | 63.2 | 1.55 | 391.3 | 0.16 |
| nr7_break | GBPUSD | 2.0 | 3.0 | ('LONDON', 'NY') | None | 493 | +6.550 | 49.7 | 1.314 | 1047.4 | 0.27 |
| nr7_break | GBPUSD | 2.0 | 3.0 | no-LATE | HIGH | 452 | +6.536 | 51.1 | 1.279 | 992.5 | 0.25 |
| nr7_break | GBPUSD | 1.5 | 1.5 | ('LONDON', 'NY') | None | 525 | +6.323 | 61.0 | 1.447 | 457.1 | 0.29 |
| nr7_break | GBPJPY | 1.5 | 1.0 | ('LONDON', 'NY') | None | 641 | +6.072 | 72.2 | 1.417 | 771.2 | 0.29 |
| nr7_break | GBPJPY | 2.0 | 2.0 | ('LONDON', 'NY') | HIGH | 206 | +7.099 | 52.4 | 1.222 | 557.9 | 0.09 |
| nr7_break | GBPJPY | 2.0 | 1.5 | ('LONDON', 'NY') | None | 620 | +5.862 | 64.5 | 1.263 | 652.6 | 0.28 |
| nr7_break | USDCAD | 1.5 | 2.0 | ('LONDON', 'NY') | None | 297 | +6.568 | 57.2 | 1.55 | 348.9 | 0.16 |
| shock_follow | EURJPY | 1.5 | 2.0 | ASIA | NORMAL | 50 | +9.497 | 60.0 | 1.83 | 113.8 | 0.03 |
| nr7_break | GBPJPY | 1.5 | 1.5 | ('LONDON', 'NY') | HIGH | 214 | +6.925 | 56.5 | 1.264 | 771.2 | 0.10 |
| nr7_break | USDCAD | 1.5 | 1.5 | ('LONDON', 'NY') | None | 303 | +6.475 | 66.0 | 1.661 | 212.5 | 0.17 |
| nr7_break | GBPUSD | 1.0 | 1.0 | ('LONDON', 'NY') | HIGH | 188 | +7.011 | 62.8 | 1.646 | 99.4 | 0.10 |
| nr7_break | GBPJPY | 1.0 | 1.0 | ('LONDON', 'NY') | None | 649 | +5.662 | 63.8 | 1.445 | 532.5 | 0.30 |
| nr7_break | AUDUSD | 2.0 | 2.0 | ('LONDON', 'NY') | HIGH | 301 | +6.370 | 61.1 | 1.569 | 218.6 | 0.17 |
| nr7_break | GBPUSD | 1.0 | 3.0 | ('LONDON', 'NY') | None | 508 | +5.823 | 35.0 | 1.374 | 676.9 | 0.28 |

*S1 = candidates -> S2 walk-forward+FDR -> S3 holdout. Chief directive + GRID RULING.*