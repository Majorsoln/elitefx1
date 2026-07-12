# Strategy Lab — cycle-2 candidates (TRAIN)

*2026-07-12 17:17 | cycle=2 | TF=H4 | split=train | cells tested=1152 | candidates (N>=30)=1152 | costs ndani (episodes) | RANK=population view*

> **UAMINIFU:** hizi ni CANDIDATES, SIO strategies. TRAIN=in-sample; uthibitisho = S2 (walk-forward VALIDATION + BH-FDR) na S3 (HOLDOUT, mara moja). RED LINES: hakuna kuchagua kwa holdout; hakuna metric bila costs. LESSON-001/002/029/033/034. Profitable != Tradable Edge.


## Top candidates (population rank)

| event | pair | SL | TP | session | vol | N | EV net | win% | PF | maxDD | tr/day |
|-------|------|----|----|---------|-----|---|--------|------|----|-------|--------|
| shock_follow | XAUUSD | 1.0 | 3.0 | None | None | 247 | +290.683 | 37.2 | 1.587 | 6192.6 | 0.11 |
| shock_follow | XAUUSD | 1.0 | 3.0 | no-LATE | None | 202 | +292.531 | 37.6 | 1.593 | 8102.5 | 0.09 |
| shock_follow | XAUUSD | 1.5 | 3.0 | no-LATE | None | 199 | +214.177 | 44.7 | 1.325 | 13122.3 | 0.09 |
| shock_follow | XAUUSD | 1.5 | 3.0 | None | None | 241 | +206.539 | 44.0 | 1.311 | 9490.8 | 0.11 |
| shock_follow | XAUUSD | 2.0 | 3.0 | no-LATE | None | 196 | +163.183 | 50.0 | 1.21 | 22249.2 | 0.09 |
| shock_follow | XAUUSD | 2.0 | 3.0 | None | None | 238 | +154.635 | 49.2 | 1.197 | 19272.6 | 0.11 |
| shock_follow | XAUUSD | 1.0 | 2.0 | no-LATE | None | 208 | +143.599 | 42.3 | 1.31 | 13909.8 | 0.10 |
| shock_follow | XAUUSD | 1.0 | 2.0 | None | None | 254 | +136.834 | 42.1 | 1.293 | 11840.5 | 0.12 |
| nr7_break | XAUUSD | 2.0 | 2.0 | no-LATE | None | 479 | +105.176 | 55.7 | 1.165 | 22488.8 | 0.22 |
| shock_follow | XAUUSD | 1.0 | 1.5 | no-LATE | None | 211 | +100.550 | 48.3 | 1.24 | 12216.4 | 0.10 |
| nr7_break | XAUUSD | 2.0 | 2.0 | None | None | 549 | +84.561 | 56.5 | 1.128 | 27549.4 | 0.25 |
| nr7_break | XAUUSD | 2.0 | 1.0 | no-LATE | None | 580 | +80.175 | 72.1 | 1.195 | 23630.3 | 0.27 |
| nr4_inside | XAUUSD | 2.0 | 2.0 | None | None | 497 | +81.627 | 53.7 | 1.125 | 27613.0 | 0.23 |
| shock_follow | XAUUSD | 1.5 | 1.5 | no-LATE | None | 209 | +90.737 | 57.4 | 1.174 | 16040.4 | 0.10 |
| nr7_break | XAUUSD | 2.0 | 1.5 | no-LATE | None | 518 | +77.222 | 62.0 | 1.138 | 19739.7 | 0.24 |
| shock_follow | XAUUSD | 1.5 | 2.0 | no-LATE | None | 205 | +90.549 | 49.8 | 1.149 | 17597.7 | 0.09 |
| shock_follow | XAUUSD | 1.0 | 1.5 | None | None | 257 | +85.688 | 47.5 | 1.201 | 11586.1 | 0.12 |
| nr7_break | XAUUSD | 2.0 | 3.0 | no-LATE | None | 426 | +71.413 | 45.8 | 1.095 | 25423.5 | 0.20 |
| shock_follow | XAUUSD | 1.5 | 2.0 | None | None | 249 | +77.666 | 49.4 | 1.126 | 16271.9 | 0.12 |
| nr7_break | XAUUSD | 1.0 | 2.0 | no-LATE | None | 559 | +65.510 | 39.9 | 1.138 | 20906.9 | 0.26 |
| nr7_break | XAUUSD | 1.0 | 3.0 | None | None | 588 | +61.035 | 30.8 | 1.108 | 21609.8 | 0.27 |
| nr7_break | XAUUSD | 1.5 | 2.0 | no-LATE | None | 515 | +61.446 | 49.1 | 1.104 | 29210.5 | 0.24 |
| nr4_inside | XAUUSD | 2.0 | 3.0 | None | None | 440 | +59.505 | 44.1 | 1.077 | 49965.8 | 0.20 |
| shock_follow | XAUUSD | 2.0 | 1.5 | no-LATE | None | 207 | +65.136 | 62.8 | 1.109 | 23783.1 | 0.10 |
| nr7_break | XAUUSD | 1.0 | 3.0 | no-LATE | None | 516 | +54.705 | 30.4 | 1.1 | 21433.1 | 0.24 |
| nr7_break | XAUUSD | 2.0 | 1.0 | None | None | 672 | +51.302 | 71.4 | 1.118 | 25884.0 | 0.31 |
| nr7_break | XAUUSD | 1.0 | 1.5 | no-LATE | None | 592 | +48.768 | 46.3 | 1.115 | 18017.5 | 0.27 |
| nr7_break | XAUUSD | 1.0 | 2.0 | None | None | 663 | +46.215 | 39.7 | 1.094 | 29072.9 | 0.30 |
| nr4_inside | XAUUSD | 1.0 | 3.0 | None | None | 554 | +47.105 | 30.0 | 1.087 | 54071.8 | 0.26 |
| shock_follow | XAUUSD | 1.5 | 1.5 | None | None | 255 | +52.950 | 55.7 | 1.098 | 18121.1 | 0.12 |
| nr4_inside | XAUUSD | 2.0 | 2.0 | no-LATE | None | 434 | +46.906 | 53.2 | 1.071 | 27290.8 | 0.20 |
| nr7_break | XAUUSD | 1.5 | 2.0 | None | None | 602 | +42.638 | 49.3 | 1.07 | 44149.1 | 0.28 |
| nr7_break | XAUUSD | 1.5 | 1.5 | no-LATE | None | 549 | +42.797 | 55.4 | 1.082 | 22028.8 | 0.25 |
| nr4_inside | XAUUSD | 1.5 | 3.0 | None | None | 489 | +42.864 | 38.5 | 1.062 | 50869.3 | 0.23 |
| nr7_break | XAUUSD | 1.5 | 1.0 | no-LATE | None | 603 | +40.451 | 65.3 | 1.101 | 28475.2 | 0.28 |
| nr7_break | XAUUSD | 1.0 | 1.0 | no-LATE | None | 628 | +40.031 | 57.0 | 1.117 | 23657.4 | 0.29 |
| nr7_break | XAUUSD | 2.0 | 3.0 | None | None | 473 | +40.378 | 46.1 | 1.051 | 32195.3 | 0.22 |
| nr4_inside | XAUUSD | 1.5 | 2.0 | None | None | 549 | +39.344 | 47.0 | 1.066 | 52911.6 | 0.25 |
| squeeze_break | XAUUSD | 2.0 | 1.0 | no-LATE | None | 309 | +41.114 | 68.0 | 1.101 | 19988.4 | 0.14 |
| nr4_inside | XAUUSD | 1.0 | 3.0 | no-LATE | None | 481 | +35.927 | 29.7 | 1.067 | 47707.3 | 0.22 |

*S1 = candidates -> S2 walk-forward+FDR -> S3 holdout. Chief directive + GRID RULING.*