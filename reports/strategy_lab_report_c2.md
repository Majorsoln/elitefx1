# Strategy Lab — cycle-2 candidates (VALIDATION)

*2026-07-12 17:24 | cycle=2 | TF=H1 | split=validation | cells tested=1152 | candidates (N>=30)=1068 | costs ndani (episodes) | RANK=population view*

> **UAMINIFU:** hizi ni CANDIDATES, SIO strategies. TRAIN=in-sample; uthibitisho = S2 (walk-forward VALIDATION + BH-FDR) na S3 (HOLDOUT, mara moja). RED LINES: hakuna kuchagua kwa holdout; hakuna metric bila costs. LESSON-001/002/029/033/034. Profitable != Tradable Edge.


## FDR (S2)
- **BH-FDR (q=0.1)**: 0/1068 survivors; ~0.0 zinatarajiwa kwa bahati (null). Cells tested (multiple-testing m)=1152.


## Top candidates (population rank)

| event | pair | SL | TP | session | vol | N | EV net | win% | PF | maxDD | tr/day |
|-------|------|----|----|---------|-----|---|--------|------|----|-------|--------|
| squeeze_break | XAUUSD | 2.0 | 2.0 | None | None | 264 | +100.717 | 57.2 | 1.249 | 7614.6 | 0.43 |
| squeeze_break | XAUUSD | 2.0 | 2.0 | no-LATE | None | 249 | +89.386 | 57.0 | 1.22 | 8512.3 | 0.41 |
| squeeze_break | XAUUSD | 2.0 | 1.5 | None | None | 289 | +66.085 | 62.6 | 1.189 | 9539.8 | 0.48 |
| squeeze_break | XAUUSD | 2.0 | 3.0 | None | None | 252 | +59.608 | 46.0 | 1.118 | 10371.5 | 0.41 |
| squeeze_break | XAUUSD | 2.0 | 3.0 | no-LATE | None | 237 | +51.975 | 45.6 | 1.102 | 9944.9 | 0.39 |
| squeeze_break | XAUUSD | 2.0 | 1.5 | no-LATE | None | 272 | +34.340 | 61.4 | 1.094 | 10713.2 | 0.45 |
| squeeze_break | XAUUSD | 1.5 | 3.0 | None | None | 286 | +28.527 | 38.1 | 1.063 | 14884.6 | 0.47 |
| gap_fade | XAUUSD | 1.0 | 1.5 | no-LATE | None | 48 | +38.835 | 43.8 | 1.135 | 4266.6 | 0.08 |
| squeeze_break | XAUUSD | 1.5 | 2.0 | None | None | 296 | +25.716 | 47.0 | 1.065 | 12684.6 | 0.49 |
| squeeze_break | XAUUSD | 1.5 | 2.0 | no-LATE | None | 280 | +17.532 | 46.8 | 1.045 | 14418.5 | 0.46 |
| squeeze_break | XAUUSD | 2.0 | 1.0 | None | None | 329 | +13.459 | 69.9 | 1.047 | 12946.4 | 0.54 |
| squeeze_break | XAUUSD | 1.5 | 3.0 | no-LATE | None | 271 | +8.071 | 36.9 | 1.018 | 14420.6 | 0.45 |
| london_drift | GBPJPY | 1.5 | 3.0 | None | None | 448 | +5.011 | 40.0 | 1.175 | 1038.9 | 0.72 |
| london_drift | GBPJPY | 1.5 | 3.0 | no-LATE | None | 448 | +5.011 | 40.0 | 1.175 | 1038.9 | 0.72 |
| gap_fade | USDJPY | 1.5 | 1.5 | None | None | 40 | +6.138 | 57.5 | 1.368 | 206.1 | 0.08 |
| london_drift | EURJPY | 1.5 | 3.0 | None | None | 456 | +3.361 | 39.5 | 1.143 | 807.4 | 0.87 |
| london_drift | EURJPY | 1.5 | 3.0 | no-LATE | None | 456 | +3.361 | 39.5 | 1.143 | 807.4 | 0.87 |
| squeeze_break | GBPJPY | 2.0 | 3.0 | None | None | 257 | +3.692 | 47.9 | 1.126 | 946.7 | 0.41 |
| squeeze_break | XAUUSD | 1.5 | 1.5 | None | None | 324 | +3.253 | 52.5 | 1.009 | 12774.8 | 0.53 |
| gap_fade | USDCHF | 2.0 | 2.0 | None | None | 43 | +4.870 | 60.5 | 1.522 | 110.4 | 0.08 |
| gap_fade | USDJPY | 1.0 | 1.5 | None | None | 40 | +4.955 | 45.0 | 1.35 | 138.9 | 0.08 |
| gap_fade | USDCHF | 1.5 | 2.0 | None | None | 43 | +4.811 | 55.8 | 1.556 | 117.5 | 0.08 |
| london_drift | GBPJPY | 2.0 | 3.0 | None | None | 425 | +2.980 | 44.9 | 1.089 | 1485.7 | 0.68 |
| london_drift | GBPJPY | 2.0 | 3.0 | no-LATE | None | 425 | +2.980 | 44.9 | 1.089 | 1485.7 | 0.68 |
| london_drift | EURJPY | 2.0 | 3.0 | None | None | 433 | +2.763 | 45.5 | 1.1 | 798.1 | 0.83 |
| london_drift | EURJPY | 2.0 | 3.0 | no-LATE | None | 433 | +2.763 | 45.5 | 1.1 | 798.1 | 0.83 |
| gap_fade | USDJPY | 2.0 | 1.5 | None | None | 40 | +4.487 | 60.0 | 1.234 | 226.3 | 0.08 |
| squeeze_break | XAUUSD | 1.5 | 1.0 | None | None | 360 | +2.821 | 63.1 | 1.01 | 7835.5 | 0.59 |
| gap_fade | USDJPY | 1.5 | 2.0 | None | None | 40 | +4.403 | 50.0 | 1.214 | 206.1 | 0.08 |
| nr4_inside | EURJPY | 2.0 | 1.0 | no-LATE | None | 345 | +2.486 | 71.6 | 1.172 | 527.6 | 0.66 |
| gap_fade | USDJPY | 1.0 | 2.0 | None | None | 40 | +3.892 | 37.5 | 1.232 | 138.9 | 0.08 |
| squeeze_break | USDJPY | 2.0 | 1.5 | no-LATE | None | 317 | +2.451 | 60.2 | 1.158 | 412.6 | 0.61 |
| gap_fade | USDJPY | 1.5 | 1.0 | None | None | 40 | +3.590 | 67.5 | 1.264 | 156.6 | 0.08 |
| nr4_inside | EURJPY | 1.5 | 1.5 | no-LATE | None | 337 | +2.286 | 55.5 | 1.129 | 535.0 | 0.65 |
| nr4_inside | USDJPY | 1.5 | 1.0 | no-LATE | None | 354 | +2.238 | 64.7 | 1.178 | 294.2 | 0.68 |
| london_drift | EURJPY | 1.5 | 2.0 | None | None | 488 | +2.079 | 46.7 | 1.099 | 547.8 | 0.94 |
| london_drift | EURJPY | 1.5 | 2.0 | no-LATE | None | 488 | +2.079 | 46.7 | 1.099 | 547.8 | 0.94 |
| gap_fade | USDJPY | 1.0 | 1.0 | None | None | 40 | +3.453 | 57.5 | 1.299 | 99.2 | 0.08 |
| gap_fade | USDCHF | 1.5 | 1.0 | None | None | 43 | +3.295 | 74.4 | 1.643 | 54.7 | 0.08 |
| london_drift | GBPJPY | 1.0 | 3.0 | None | None | 479 | +1.990 | 28.8 | 1.084 | 1108.0 | 0.77 |

*S1 = candidates -> S2 walk-forward+FDR -> S3 holdout. Chief directive + GRID RULING.*