# Strategy Lab — S1 candidates (HOLDOUT)

*2026-07-10 21:09 | TF=H1 | split=holdout | cells tested=2364 | candidates (N>=30)=2246 | costs ndani (episodes) | RANK=population view*

> **UAMINIFU:** hizi ni CANDIDATES, SIO strategies. TRAIN=in-sample; uthibitisho = S2 (walk-forward VALIDATION + BH-FDR) na S3 (HOLDOUT, mara moja). RED LINES: hakuna kuchagua kwa holdout; hakuna metric bila costs. LESSON-001/002/029/033/034. Profitable != Tradable Edge.


## FDR (S2)
- **BH-FDR (q=0.1)**: 0/2246 survivors; ~0.0 zinatarajiwa kwa bahati (null). Cells tested (multiple-testing m)=2364.


## Top candidates (population rank)

| event | pair | SL | TP | session | vol | N | EV net | win% | PF | maxDD | tr/day |
|-------|------|----|----|---------|-----|---|--------|------|----|-------|--------|
| nr7_break | GBPJPY | 2.0 | 1.0 | no-LATE | HIGH | 113 | +8.973 | 74.3 | 1.517 | 317.4 | 0.27 |
| nr7_break | GBPJPY | 2.0 | 3.0 | None | None | 360 | +5.957 | 47.5 | 1.196 | 1660.8 | 0.86 |
| nr7_break | GBPJPY | 1.5 | 1.0 | no-LATE | HIGH | 115 | +6.844 | 68.7 | 1.388 | 320.4 | 0.28 |
| nr7_break | GBPJPY | 2.0 | 1.0 | no-LATE | None | 324 | +5.173 | 73.8 | 1.339 | 330.4 | 0.78 |
| shock_follow | USDJPY | 1.0 | 3.0 | ASIA | None | 60 | +7.127 | 38.3 | 1.48 | 119.1 | 0.17 |
| nr7_break | GBPJPY | 1.0 | 1.0 | no-LATE | HIGH | 118 | +6.099 | 60.2 | 1.401 | 228.8 | 0.28 |
| nr7_break | GBPJPY | 2.0 | 3.0 | no-LATE | None | 247 | +5.283 | 46.2 | 1.177 | 576.4 | 0.59 |
| mr_zscore | EURJPY | 2.0 | 3.0 | None | None | 270 | +5.115 | 45.9 | 1.214 | 897.7 | 0.78 |
| nr7_break | GBPJPY | 1.5 | 1.0 | no-LATE | None | 333 | +4.889 | 69.1 | 1.343 | 246.2 | 0.80 |
| shock_follow | EURJPY | 2.0 | 1.0 | ASIA | None | 44 | +7.406 | 79.5 | 1.805 | 73.7 | 0.13 |
| nr7_break | USDCHF | 2.0 | 1.5 | ('LONDON', 'NY') | None | 80 | +6.367 | 67.5 | 1.858 | 154.6 | 0.23 |
| engulf_extreme | EURJPY | 1.5 | 3.0 | None | None | 101 | +5.822 | 41.6 | 1.284 | 313.7 | 0.29 |
| nr7_break | GBPJPY | 2.0 | 2.0 | no-LATE | None | 272 | +4.732 | 54.0 | 1.178 | 581.1 | 0.65 |
| nr7_break | EURJPY | 1.0 | 2.0 | no-LATE | None | 314 | +4.607 | 42.4 | 1.312 | 312.2 | 0.91 |
| nr7_break | USDCHF | 2.0 | 3.0 | ('LONDON', 'NY') | None | 74 | +6.073 | 50.0 | 1.542 | 154.6 | 0.21 |
| session_orb | USDJPY | 2.0 | 2.0 | None | HIGH | 100 | +5.656 | 52.0 | 1.226 | 473.6 | 0.29 |
| shock_follow | EURJPY | 1.5 | 1.0 | ASIA | None | 44 | +6.638 | 75.0 | 1.752 | 66.6 | 0.13 |
| mr_zscore | USDJPY | 2.0 | 1.5 | None | None | 339 | +4.238 | 62.0 | 1.24 | 390.5 | 0.98 |
| nr7_break | GBPJPY | 2.0 | 2.0 | no-LATE | HIGH | 102 | +5.310 | 52.0 | 1.165 | 645.3 | 0.24 |
| shock_follow | USDJPY | 1.0 | 2.0 | ASIA | None | 61 | +5.939 | 44.3 | 1.449 | 103.2 | 0.18 |
| nr7_break | GBPJPY | 1.0 | 1.0 | no-LATE | None | 341 | +4.124 | 60.1 | 1.33 | 243.8 | 0.82 |
| shock_follow | EURJPY | 1.5 | 1.5 | ASIA | None | 44 | +6.292 | 63.6 | 1.477 | 183.3 | 0.13 |
| nr7_break | USDCHF | 1.5 | 1.5 | ('LONDON', 'NY') | None | 82 | +5.378 | 61.0 | 1.73 | 140.9 | 0.24 |
| nr7_break | USDCHF | 1.5 | 3.0 | ('LONDON', 'NY') | None | 77 | +5.233 | 44.2 | 1.493 | 140.9 | 0.22 |
| nr7_break | USDCAD | 1.0 | 3.0 | ('LONDON', 'NY') | None | 73 | +5.293 | 43.8 | 1.597 | 96.2 | 0.21 |
| shock_follow | EURJPY | 1.5 | 1.0 | None | NORMAL | 74 | +5.183 | 70.3 | 1.508 | 123.3 | 0.21 |
| nr7_break | GBPJPY | 2.0 | 1.0 | ('LONDON', 'NY') | None | 148 | +4.465 | 73.0 | 1.268 | 237.2 | 0.36 |
| nr7_break | GBPUSD | 2.0 | 2.0 | no-LATE | HIGH | 89 | +4.904 | 56.2 | 1.287 | 381.4 | 0.26 |
| nr7_break | USDCHF | 2.0 | 2.0 | ('LONDON', 'NY') | None | 77 | +5.004 | 58.4 | 1.503 | 154.6 | 0.22 |
| nr7_break | GBPJPY | 1.0 | 1.5 | no-LATE | None | 322 | +3.759 | 48.4 | 1.227 | 467.6 | 0.77 |
| shock_follow | USDJPY | 1.0 | 1.0 | None | None | 170 | +4.160 | 58.8 | 1.4 | 134.7 | 0.49 |
| nr7_break | GBPUSD | 2.0 | 3.0 | no-LATE | HIGH | 86 | +4.787 | 48.8 | 1.249 | 474.1 | 0.25 |
| mr_zscore | USDJPY | 2.0 | 2.0 | None | None | 314 | +3.687 | 53.8 | 1.178 | 484.0 | 0.91 |
| nr7_break | USDCAD | 1.0 | 1.0 | ('LONDON', 'NY') | HIGH | 33 | +5.974 | 69.7 | 2.113 | 57.7 | 0.10 |
| nr7_break | EURJPY | 1.0 | 2.0 | no-LATE | HIGH | 104 | +4.510 | 41.3 | 1.237 | 243.2 | 0.30 |
| nr7_break | EURJPY | 1.5 | 3.0 | no-LATE | None | 274 | +3.729 | 43.1 | 1.174 | 418.6 | 0.79 |
| nr7_break | USDCHF | 1.0 | 1.5 | ('LONDON', 'NY') | None | 82 | +4.735 | 50.0 | 1.744 | 96.6 | 0.24 |
| nr7_break | USDCAD | 1.0 | 2.0 | ('LONDON', 'NY') | HIGH | 31 | +6.023 | 51.6 | 1.612 | 83.8 | 0.09 |
| nr7_break | USDCAD | 2.0 | 3.0 | no-LATE | HIGH | 112 | +4.390 | 45.5 | 1.273 | 226.1 | 0.32 |
| shock_follow | EURJPY | 2.0 | 3.0 | None | None | 149 | +4.116 | 47.6 | 1.169 | 390.5 | 0.43 |

*S1 = candidates -> S2 walk-forward+FDR -> S3 holdout. Chief directive + GRID RULING.*