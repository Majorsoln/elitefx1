# Strategy Lab — cycle-2 candidates (TRAIN)

*2026-07-10 22:30 | cycle=2 | TF=H1 | split=train | cells tested=1056 | candidates (N>=30)=1032 | costs ndani (episodes) | RANK=population view*

> **UAMINIFU:** hizi ni CANDIDATES, SIO strategies. TRAIN=in-sample; uthibitisho = S2 (walk-forward VALIDATION + BH-FDR) na S3 (HOLDOUT, mara moja). RED LINES: hakuna kuchagua kwa holdout; hakuna metric bila costs. LESSON-001/002/029/033/034. Profitable != Tradable Edge.


## Top candidates (population rank)

| event | pair | SL | TP | session | vol | N | EV net | win% | PF | maxDD | tr/day |
|-------|------|----|----|---------|-----|---|--------|------|----|-------|--------|
| nr4_inside | USDJPY | 2.0 | 2.0 | no-LATE | None | 1,196 | +2.296 | 54.5 | 1.163 | 718.4 | 0.66 |
| nr4_inside | USDJPY | 1.5 | 2.0 | no-LATE | None | 1,252 | +2.156 | 48.1 | 1.171 | 874.8 | 0.69 |
| nr4_inside | EURJPY | 1.5 | 3.0 | no-LATE | None | 1,080 | +2.171 | 40.0 | 1.126 | 933.1 | 0.59 |
| london_drift | USDJPY | 2.0 | 2.0 | None | None | 1,654 | +1.889 | 51.7 | 1.134 | 827.1 | 0.91 |
| london_drift | USDJPY | 2.0 | 2.0 | no-LATE | None | 1,654 | +1.889 | 51.7 | 1.134 | 827.1 | 0.91 |
| nr4_inside | USDJPY | 2.0 | 3.0 | no-LATE | None | 1,104 | +1.963 | 46.5 | 1.121 | 928.5 | 0.60 |
| nr4_inside | EURJPY | 2.0 | 3.0 | no-LATE | None | 1,024 | +1.762 | 45.4 | 1.089 | 1543.6 | 0.56 |
| london_drift | USDJPY | 2.0 | 3.0 | None | None | 1,504 | +1.618 | 44.0 | 1.101 | 1424.0 | 0.82 |
| london_drift | USDJPY | 2.0 | 3.0 | no-LATE | None | 1,504 | +1.618 | 44.0 | 1.101 | 1424.0 | 0.82 |
| nr4_inside | USDJPY | 1.5 | 3.0 | no-LATE | None | 1,162 | +1.640 | 40.3 | 1.114 | 1079.3 | 0.64 |
| london_drift | USDJPY | 1.5 | 3.0 | None | None | 1,610 | +1.524 | 38.1 | 1.107 | 1411.6 | 0.88 |
| london_drift | USDJPY | 1.5 | 3.0 | no-LATE | None | 1,610 | +1.524 | 38.1 | 1.107 | 1411.6 | 0.88 |
| london_drift | USDJPY | 1.5 | 2.0 | None | None | 1,727 | +1.481 | 45.6 | 1.117 | 742.2 | 0.95 |
| london_drift | USDJPY | 1.5 | 2.0 | no-LATE | None | 1,727 | +1.481 | 45.6 | 1.117 | 742.2 | 0.95 |
| nr4_inside | AUDUSD | 2.0 | 3.0 | no-LATE | None | 982 | +1.571 | 45.7 | 1.115 | 718.0 | 0.54 |
| nr4_inside | USDJPY | 1.0 | 2.0 | no-LATE | None | 1,334 | +1.363 | 37.6 | 1.131 | 1064.4 | 0.73 |
| nr4_inside | USDJPY | 2.0 | 1.5 | no-LATE | None | 1,251 | +1.307 | 60.5 | 1.103 | 824.6 | 0.69 |
| nr4_inside | USDJPY | 1.0 | 3.0 | no-LATE | None | 1,249 | +1.260 | 31.0 | 1.109 | 1361.4 | 0.69 |
| london_drift | USDJPY | 1.0 | 3.0 | None | None | 1,717 | +1.161 | 28.9 | 1.102 | 890.2 | 0.94 |
| london_drift | USDJPY | 1.0 | 3.0 | no-LATE | None | 1,717 | +1.161 | 28.9 | 1.102 | 890.2 | 0.94 |
| london_drift | EURJPY | 1.5 | 3.0 | None | None | 1,588 | +1.168 | 38.0 | 1.065 | 1067.8 | 0.87 |
| london_drift | EURJPY | 1.5 | 3.0 | no-LATE | None | 1,588 | +1.168 | 38.0 | 1.065 | 1067.8 | 0.87 |
| london_drift | EURJPY | 1.0 | 3.0 | None | None | 1,679 | +1.129 | 29.4 | 1.08 | 1052.7 | 0.92 |
| london_drift | EURJPY | 1.0 | 3.0 | no-LATE | None | 1,679 | +1.129 | 29.4 | 1.08 | 1052.7 | 0.92 |
| london_drift | USDJPY | 2.0 | 1.5 | None | None | 1,733 | +1.085 | 57.9 | 1.086 | 1089.3 | 0.95 |
| london_drift | USDJPY | 2.0 | 1.5 | no-LATE | None | 1,733 | +1.085 | 57.9 | 1.086 | 1089.3 | 0.95 |
| nr4_inside | AUDUSD | 1.5 | 3.0 | no-LATE | None | 1,025 | +1.146 | 39.3 | 1.092 | 606.8 | 0.56 |
| nr4_inside | AUDUSD | 2.0 | 1.5 | no-LATE | None | 1,110 | +1.081 | 61.2 | 1.105 | 754.0 | 0.61 |
| london_drift | USDJPY | 1.5 | 1.5 | None | None | 1,787 | +0.965 | 52.0 | 1.085 | 662.5 | 0.98 |
| london_drift | USDJPY | 1.5 | 1.5 | no-LATE | None | 1,787 | +0.965 | 52.0 | 1.085 | 662.5 | 0.98 |
| squeeze_break | GBPUSD | 2.0 | 3.0 | None | None | 1,087 | +1.024 | 44.0 | 1.048 | 1051.4 | 0.60 |
| nr4_inside | AUDUSD | 2.0 | 2.0 | no-LATE | None | 1,054 | +0.997 | 53.4 | 1.083 | 733.2 | 0.58 |
| nr4_inside | EURJPY | 1.5 | 1.5 | no-LATE | None | 1,210 | +0.945 | 52.6 | 1.068 | 663.6 | 0.66 |
| nr4_inside | USDJPY | 1.5 | 1.5 | no-LATE | None | 1,301 | +0.862 | 53.4 | 1.074 | 927.0 | 0.71 |
| squeeze_break | NZDUSD | 2.0 | 3.0 | no-LATE | None | 898 | +0.895 | 45.9 | 1.072 | 1014.6 | 0.49 |
| nr4_inside | USDCAD | 2.0 | 3.0 | no-LATE | None | 957 | +0.877 | 43.8 | 1.05 | 1234.5 | 0.53 |
| nr4_inside | EURJPY | 1.5 | 2.0 | no-LATE | None | 1,152 | +0.815 | 45.5 | 1.051 | 1175.1 | 0.63 |
| nr4_inside | AUDUSD | 1.5 | 1.5 | no-LATE | None | 1,147 | +0.724 | 54.4 | 1.076 | 708.5 | 0.63 |
| nr4_inside | USDCHF | 2.0 | 3.0 | no-LATE | None | 992 | +0.720 | 46.3 | 1.056 | 685.7 | 0.54 |
| london_drift | EURJPY | 2.0 | 3.0 | None | None | 1,495 | +0.670 | 44.0 | 1.033 | 1250.7 | 0.82 |

*S1 = candidates -> S2 walk-forward+FDR -> S3 holdout. Chief directive + GRID RULING.*