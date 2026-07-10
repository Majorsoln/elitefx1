# Strategy Lab — S1 candidates (VALIDATION)

*2026-07-10 20:59 | TF=H1 | split=validation | cells tested=2364 | candidates (N>=30)=2299 | costs ndani (episodes) | RANK=population view*

> **UAMINIFU:** hizi ni CANDIDATES, SIO strategies. TRAIN=in-sample; uthibitisho = S2 (walk-forward VALIDATION + BH-FDR) na S3 (HOLDOUT, mara moja). RED LINES: hakuna kuchagua kwa holdout; hakuna metric bila costs. LESSON-001/002/029/033/034. Profitable != Tradable Edge.


## FDR (S2)
- **BH-FDR (q=0.1)**: 1/2299 survivors; ~0.1 zinatarajiwa kwa bahati (null). Cells tested (multiple-testing m)=2364.

### SURVIVORS — waliosalia BH-FDR (hawa PEKEE ndio registration ya S3)

| event | pair | SL | TP | session | vol | N | EV net | win% | PF | p |
|-------|------|----|----|---------|-----|---|--------|------|----|---|
| nr7_break | USDCHF | 2.0 | 1.0 | no-LATE | None | 425 | +3.068 | 79.3 | 1.605 | 9.00e-06 |


## Top candidates (population rank)

| event | pair | SL | TP | session | vol | N | EV net | win% | PF | maxDD | tr/day |
|-------|------|----|----|---------|-----|---|--------|------|----|-------|--------|
| nr7_break | USDJPY | 2.0 | 3.0 | None | HIGH | 182 | +11.250 | 52.2 | 1.404 | 503.3 | 0.35 |
| nr7_break | USDJPY | 2.0 | 2.0 | None | HIGH | 204 | +8.757 | 54.9 | 1.331 | 561.0 | 0.39 |
| nr7_break | GBPJPY | 1.0 | 2.0 | ('LONDON', 'NY') | None | 175 | +8.522 | 45.1 | 1.412 | 307.7 | 0.28 |
| nr7_break | GBPUSD | 2.0 | 2.0 | ('LONDON', 'NY') | HIGH | 30 | +12.537 | 66.7 | 2.176 | 92.4 | 0.06 |
| nr7_break | USDJPY | 1.5 | 3.0 | None | HIGH | 197 | +7.842 | 44.2 | 1.286 | 502.7 | 0.38 |
| nr7_break | USDJPY | 1.0 | 2.0 | None | HIGH | 229 | +7.398 | 42.8 | 1.367 | 307.5 | 0.44 |
| nr7_break | GBPJPY | 1.0 | 1.5 | ('LONDON', 'NY') | None | 176 | +7.519 | 52.3 | 1.412 | 217.5 | 0.28 |
| shock_follow | USDJPY | 2.0 | 3.0 | ASIA | None | 49 | +9.908 | 53.1 | 1.408 | 203.9 | 0.09 |
| nr7_break | GBPUSD | 2.0 | 1.5 | ('LONDON', 'NY') | HIGH | 30 | +10.678 | 73.3 | 2.137 | 92.4 | 0.06 |
| nr7_break | USDJPY | 1.0 | 1.0 | None | HIGH | 261 | +6.232 | 59.8 | 1.449 | 166.8 | 0.50 |
| nr7_break | EURCHF | 2.0 | 3.0 | ('LONDON', 'NY') | HIGH | 37 | +9.506 | 67.6 | 2.132 | 170.6 | 0.06 |
| nr7_break | GBPJPY | 1.5 | 1.5 | ('LONDON', 'NY') | None | 175 | +6.584 | 58.3 | 1.291 | 331.2 | 0.28 |
| nr7_break | USDJPY | 1.0 | 3.0 | None | HIGH | 211 | +6.317 | 34.6 | 1.279 | 405.3 | 0.40 |
| nr7_break | USDJPY | 1.0 | 3.0 | ('LONDON', 'NY') | None | 271 | +5.949 | 36.9 | 1.36 | 484.2 | 0.52 |
| nr7_break | USDJPY | 2.0 | 1.0 | None | HIGH | 247 | +6.046 | 70.9 | 1.336 | 346.5 | 0.47 |
| nr7_break | GBPJPY | 1.5 | 2.0 | ('LONDON', 'NY') | None | 173 | +6.390 | 49.7 | 1.237 | 461.3 | 0.28 |
| nr7_break | USDJPY | 1.0 | 2.0 | ('LONDON', 'NY') | None | 280 | +5.798 | 43.6 | 1.388 | 592.5 | 0.54 |
| nr7_break | EURJPY | 2.0 | 3.0 | ('LONDON', 'NY') | HIGH | 92 | +7.153 | 47.8 | 1.209 | 586.4 | 0.18 |
| nr7_break | USDJPY | 1.0 | 1.5 | None | HIGH | 244 | +5.887 | 47.9 | 1.324 | 340.8 | 0.47 |
| engulf_extreme | EURJPY | 2.0 | 3.0 | None | None | 143 | +6.452 | 47.5 | 1.265 | 315.4 | 0.27 |
| nr7_break | GBPUSD | 2.0 | 1.0 | ('LONDON', 'NY') | HIGH | 32 | +8.962 | 81.2 | 2.294 | 85.2 | 0.06 |
| nr7_break | USDJPY | 2.0 | 1.5 | None | HIGH | 222 | +5.727 | 60.4 | 1.236 | 538.7 | 0.42 |
| nr7_break | EURCHF | 2.0 | 2.0 | ('LONDON', 'NY') | HIGH | 40 | +8.323 | 72.5 | 2.09 | 145.4 | 0.06 |
| nr7_break | USDJPY | 2.0 | 1.5 | no-LATE | None | 386 | +5.068 | 62.9 | 1.294 | 809.6 | 0.74 |
| nr7_break | GBPUSD | 1.5 | 2.0 | ('LONDON', 'NY') | HIGH | 30 | +8.696 | 60.0 | 1.737 | 86.4 | 0.06 |
| nr7_break | USDJPY | 1.5 | 1.0 | None | HIGH | 254 | +5.360 | 66.5 | 1.315 | 287.9 | 0.49 |
| nr7_break | EURJPY | 2.0 | 1.5 | ('LONDON', 'NY') | HIGH | 104 | +6.252 | 61.5 | 1.239 | 431.0 | 0.20 |
| engulf_extreme | EURJPY | 1.5 | 3.0 | None | None | 147 | +5.788 | 40.1 | 1.272 | 288.3 | 0.28 |
| nr7_break | USDJPY | 2.0 | 2.0 | no-LATE | None | 366 | +4.791 | 54.1 | 1.233 | 1009.5 | 0.70 |
| nr7_break | USDJPY | 2.0 | 1.0 | no-LATE | None | 429 | +4.557 | 74.6 | 1.359 | 235.9 | 0.82 |
| nr7_break | USDJPY | 2.0 | 2.0 | ('LONDON', 'NY') | None | 264 | +4.889 | 55.3 | 1.227 | 771.4 | 0.51 |
| nr7_break | GBPUSD | 1.5 | 1.5 | ('LONDON', 'NY') | HIGH | 30 | +7.943 | 66.7 | 1.785 | 82.5 | 0.06 |
| shock_follow | USDJPY | 1.0 | 3.0 | ASIA | None | 49 | +6.940 | 38.8 | 1.401 | 166.8 | 0.09 |
| nr7_break | USDJPY | 1.0 | 1.0 | ('LONDON', 'NY') | None | 294 | +4.762 | 61.6 | 1.462 | 272.8 | 0.56 |
| nr7_break | USDJPY | 1.5 | 2.0 | None | HIGH | 217 | +5.029 | 47.9 | 1.194 | 546.8 | 0.42 |
| nr7_break | GBPUSD | 2.0 | 2.0 | no-LATE | HIGH | 130 | +5.491 | 59.2 | 1.412 | 171.6 | 0.25 |
| nr7_break | USDJPY | 1.0 | 1.0 | no-LATE | HIGH | 133 | +5.460 | 59.4 | 1.37 | 279.7 | 0.26 |
| nr7_break | USDJPY | 1.0 | 1.0 | ('LONDON', 'NY') | HIGH | 96 | +5.819 | 60.4 | 1.395 | 242.2 | 0.18 |
| nr7_break | USDJPY | 1.0 | 1.5 | ('LONDON', 'NY') | None | 284 | +4.703 | 49.6 | 1.352 | 690.0 | 0.54 |
| nr7_break | USDJPY | 2.0 | 3.0 | no-LATE | None | 341 | +4.498 | 46.9 | 1.194 | 957.1 | 0.65 |

*S1 = candidates -> S2 walk-forward+FDR -> S3 holdout. Chief directive + GRID RULING.*