# Strategy Lab — cycle-2 candidates (VALIDATION)

*2026-07-12 22:18 | cycle=2 | TF=H4 | split=validation | cells tested=1152 | candidates (N>=30)=1152 | costs ndani (episodes) | RANK=population view*

> **UAMINIFU:** hizi ni CANDIDATES, SIO strategies. TRAIN=in-sample; uthibitisho = S2 (walk-forward VALIDATION + BH-FDR) na S3 (HOLDOUT, mara moja). RED LINES: hakuna kuchagua kwa holdout; hakuna metric bila costs. LESSON-001/002/029/033/034. Profitable != Tradable Edge.


## FDR (S2)
- **BH-FDR (q=0.1) juu ya p_boot (R1 bootstrap engine — RASMI)**: 12/1152 survivors; ~1.2 zinatarajiwa kwa bahati (null). Cells tested (m)=1152. p_z (z-test ya zamani) = sensitivity column.

### SURVIVORS — waliosalia BH-FDR juu ya p_boot (hawa PEKEE ndio registration ya S3)

| event | pair | SL | TP | session | vol | N | EV net | win% | PF | p_boot | p_z |
|-------|------|----|----|---------|-----|---|--------|------|----|--------|-----|
| nr7_break | EURJPY | 1.0 | 3.0 | no-LATE | None | 127 | +27.478 | 40.2 | 1.861 | 1.00e-04 | 1.88e-03 |
| nr7_break | EURGBP | 1.5 | 1.0 | no-LATE | None | 182 | +5.197 | 76.9 | 1.94 | 1.00e-04 | 1.20e-05 |
| nr7_break | EURGBP | 2.0 | 1.0 | no-LATE | None | 173 | +5.764 | 82.1 | 2.02 | 1.00e-04 | 1.30e-05 |
| nr4_inside | GBPJPY | 1.5 | 1.5 | no-LATE | None | 107 | +43.291 | 72.9 | 2.862 | 1.00e-04 | 0.00e+00 |
| nr7_break | EURJPY | 1.0 | 1.5 | no-LATE | None | 147 | +18.442 | 53.7 | 1.755 | 3.00e-04 | 8.04e-04 |
| nr4_inside | GBPJPY | 1.5 | 2.0 | no-LATE | None | 98 | +48.964 | 64.3 | 2.682 | 5.00e-04 | 2.00e-06 |
| nr7_break | AUDUSD | 1.5 | 3.0 | no-LATE | None | 115 | +14.358 | 52.2 | 1.834 | 7.00e-04 | 1.26e-03 |
| nr4_inside | GBPJPY | 1.5 | 1.0 | no-LATE | None | 112 | +25.579 | 77.7 | 2.259 | 7.00e-04 | 3.10e-05 |
| nr4_inside | GBPJPY | 2.0 | 1.5 | no-LATE | None | 106 | +41.067 | 75.5 | 2.483 | 7.00e-04 | 5.00e-06 |
| nr4_inside | GBPJPY | 1.0 | 2.0 | no-LATE | None | 105 | +28.662 | 50.5 | 1.921 | 8.00e-04 | 1.19e-03 |
| nr7_break | EURGBP | 1.5 | 1.0 | None | None | 193 | +4.275 | 75.1 | 1.698 | 9.00e-04 | 2.85e-04 |
| nr7_break | EURGBP | 2.0 | 1.0 | None | None | 182 | +5.126 | 80.8 | 1.851 | 1.00e-03 | 8.30e-05 |


## Cost stress — EV(Δspread) analytic (R5; kila trade inalipa spread mara moja)

| cell | EV | EV@+0.2 | EV@+0.5 | EV@+1.0 | breakeven Δspread |
|------|----|----|----|----|------|
| nr7_breakxEURJPY SL1.0/TP3.0 no-LATE | +27.478 | +27.278 | +26.978 | +26.478 | 27.478 |
| nr7_breakxEURGBP SL1.5/TP1.0 no-LATE | +5.197 | +4.997 | +4.697 | +4.197 | 5.197 |
| nr7_breakxEURGBP SL2.0/TP1.0 no-LATE | +5.764 | +5.564 | +5.264 | +4.764 | 5.764 |
| nr4_insidexGBPJPY SL1.5/TP1.5 no-LATE | +43.291 | +43.091 | +42.791 | +42.291 | 43.291 |
| nr7_breakxEURJPY SL1.0/TP1.5 no-LATE | +18.442 | +18.242 | +17.942 | +17.442 | 18.442 |
| nr4_insidexGBPJPY SL1.5/TP2.0 no-LATE | +48.964 | +48.764 | +48.464 | +47.964 | 48.964 |
| nr7_breakxAUDUSD SL1.5/TP3.0 no-LATE | +14.358 | +14.158 | +13.858 | +13.358 | 14.358 |
| nr4_insidexGBPJPY SL1.5/TP1.0 no-LATE | +25.579 | +25.379 | +25.079 | +24.579 | 25.579 |
| nr4_insidexGBPJPY SL2.0/TP1.5 no-LATE | +41.067 | +40.867 | +40.567 | +40.067 | 41.067 |
| nr4_insidexGBPJPY SL1.0/TP2.0 no-LATE | +28.662 | +28.462 | +28.162 | +27.662 | 28.662 |
| nr7_breakxEURGBP SL1.5/TP1.0 None | +4.275 | +4.075 | +3.775 | +3.275 | 4.275 |
| nr7_breakxEURGBP SL2.0/TP1.0 None | +5.126 | +4.926 | +4.626 | +4.126 | 5.126 |

## Top candidates (population rank)

| event | pair | SL | TP | session | vol | N | EV net | win% | PF | maxDD | tr/day |
|-------|------|----|----|---------|-----|---|--------|------|----|-------|--------|
| shock_follow | XAUUSD | 2.0 | 3.0 | None | None | 71 | +949.048 | 60.6 | 2.22 | 10228.6 | 0.12 |
| shock_follow | XAUUSD | 2.0 | 3.0 | no-LATE | None | 63 | +943.361 | 60.3 | 2.172 | 13891.2 | 0.10 |
| shock_follow | XAUUSD | 1.0 | 3.0 | None | None | 80 | +623.311 | 40.0 | 2.01 | 9547.1 | 0.13 |
| shock_follow | XAUUSD | 1.5 | 3.0 | None | None | 75 | +604.471 | 48.0 | 1.732 | 12442.6 | 0.12 |
| shock_follow | XAUUSD | 1.0 | 3.0 | no-LATE | None | 71 | +522.695 | 38.0 | 1.816 | 8761.0 | 0.12 |
| shock_follow | XAUUSD | 1.5 | 3.0 | no-LATE | None | 66 | +521.853 | 47.0 | 1.613 | 14665.8 | 0.11 |
| shock_follow | XAUUSD | 2.0 | 2.0 | None | None | 71 | +503.557 | 63.4 | 1.67 | 11924.6 | 0.12 |
| shock_follow | XAUUSD | 2.0 | 2.0 | no-LATE | None | 63 | +484.991 | 63.5 | 1.626 | 14252.1 | 0.10 |
| nr7_break | XAUUSD | 1.5 | 2.0 | no-LATE | None | 112 | +372.713 | 54.5 | 1.521 | 9297.1 | 0.18 |
| nr7_break | XAUUSD | 1.5 | 2.0 | None | None | 130 | +354.411 | 53.1 | 1.495 | 13038.9 | 0.21 |
| nr7_break | XAUUSD | 2.0 | 2.0 | None | None | 125 | +354.778 | 58.4 | 1.444 | 19088.6 | 0.21 |
| nr7_break | XAUUSD | 2.0 | 1.0 | no-LATE | None | 128 | +339.402 | 78.1 | 1.801 | 7133.3 | 0.21 |
| nr7_break | XAUUSD | 2.0 | 1.0 | None | None | 153 | +324.912 | 77.1 | 1.743 | 9071.1 | 0.25 |
| nr7_break | XAUUSD | 1.5 | 1.0 | None | None | 155 | +319.433 | 72.3 | 1.78 | 8892.5 | 0.26 |
| squeeze_break | XAUUSD | 2.0 | 3.0 | None | None | 70 | +378.317 | 50.0 | 1.42 | 12637.6 | 0.12 |
| nr7_break | XAUUSD | 1.5 | 1.0 | no-LATE | None | 130 | +320.355 | 73.1 | 1.786 | 8144.3 | 0.21 |
| nr7_break | XAUUSD | 2.0 | 2.0 | no-LATE | None | 108 | +323.894 | 57.4 | 1.402 | 13135.8 | 0.18 |
| shock_follow | XAUUSD | 1.0 | 2.0 | None | None | 80 | +305.200 | 42.5 | 1.515 | 9400.7 | 0.13 |
| squeeze_break | XAUUSD | 2.0 | 3.0 | no-LATE | None | 69 | +291.816 | 47.8 | 1.313 | 12637.6 | 0.11 |
| nr7_break | XAUUSD | 1.5 | 3.0 | no-LATE | None | 101 | +257.679 | 43.6 | 1.29 | 19978.3 | 0.17 |
| shock_follow | XAUUSD | 1.5 | 2.0 | None | None | 75 | +270.256 | 52.0 | 1.348 | 12980.8 | 0.12 |
| shock_follow | XAUUSD | 2.0 | 1.5 | None | None | 74 | +269.690 | 64.9 | 1.374 | 14508.0 | 0.12 |
| nr7_break | XAUUSD | 1.5 | 1.5 | no-LATE | None | 118 | +241.784 | 58.5 | 1.371 | 9762.5 | 0.19 |
| nr7_break | XAUUSD | 1.5 | 1.5 | None | None | 140 | +232.522 | 57.1 | 1.361 | 12437.2 | 0.23 |
| nr7_break | XAUUSD | 1.0 | 1.0 | no-LATE | None | 136 | +216.053 | 60.3 | 1.539 | 9674.1 | 0.22 |
| nr7_break | XAUUSD | 2.0 | 1.5 | None | None | 135 | +214.901 | 63.0 | 1.295 | 15596.2 | 0.22 |
| squeeze_break | XAUUSD | 2.0 | 2.0 | None | None | 74 | +236.748 | 56.8 | 1.301 | 13471.4 | 0.12 |
| nr7_break | XAUUSD | 2.0 | 1.5 | no-LATE | None | 113 | +214.948 | 62.8 | 1.299 | 13821.9 | 0.19 |
| nr7_break | XAUUSD | 1.0 | 1.0 | None | None | 163 | +176.907 | 58.3 | 1.418 | 10895.6 | 0.27 |
| shock_follow | XAUUSD | 2.0 | 1.5 | no-LATE | None | 65 | +206.558 | 63.1 | 1.269 | 14624.2 | 0.11 |
| squeeze_break | XAUUSD | 2.0 | 1.0 | None | None | 95 | +189.315 | 73.7 | 1.394 | 13980.5 | 0.16 |
| shock_follow | XAUUSD | 1.0 | 2.0 | no-LATE | None | 71 | +200.196 | 39.4 | 1.319 | 10895.5 | 0.12 |
| squeeze_break | XAUUSD | 1.5 | 3.0 | None | None | 83 | +191.967 | 41.0 | 1.224 | 16493.1 | 0.14 |
| squeeze_break | XAUUSD | 2.0 | 1.0 | no-LATE | None | 92 | +185.062 | 73.9 | 1.387 | 13980.5 | 0.15 |
| squeeze_break | XAUUSD | 2.0 | 2.0 | no-LATE | None | 72 | +194.777 | 55.6 | 1.241 | 13471.4 | 0.12 |
| nr7_break | XAUUSD | 2.0 | 3.0 | no-LATE | None | 97 | +172.216 | 45.4 | 1.171 | 25942.7 | 0.16 |
| shock_follow | XAUUSD | 1.5 | 2.0 | no-LATE | None | 66 | +173.017 | 50.0 | 1.211 | 14252.4 | 0.11 |
| shock_follow | XAUUSD | 2.0 | 1.0 | None | None | 80 | +159.876 | 71.2 | 1.283 | 8689.4 | 0.13 |
| nr7_break | XAUUSD | 1.5 | 3.0 | None | None | 115 | +145.583 | 40.9 | 1.161 | 32545.5 | 0.19 |
| shock_follow | XAUUSD | 1.0 | 1.5 | None | None | 81 | +150.995 | 44.4 | 1.266 | 11296.2 | 0.13 |

*S1 = candidates -> S2 walk-forward+FDR -> S3 holdout. Chief directive + GRID RULING.*