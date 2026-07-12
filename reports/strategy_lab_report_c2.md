# Strategy Lab — cycle-2 candidates (TRAIN)

*2026-07-12 17:12 | cycle=2 | TF=H1 | split=train | cells tested=1152 | candidates (N>=30)=1128 | costs ndani (episodes) | RANK=population view*

> **UAMINIFU:** hizi ni CANDIDATES, SIO strategies. TRAIN=in-sample; uthibitisho = S2 (walk-forward VALIDATION + BH-FDR) na S3 (HOLDOUT, mara moja). RED LINES: hakuna kuchagua kwa holdout; hakuna metric bila costs. LESSON-001/002/029/033/034. Profitable != Tradable Edge.


## Top candidates (population rank)

| event | pair | SL | TP | session | vol | N | EV net | win% | PF | maxDD | tr/day |
|-------|------|----|----|---------|-----|---|--------|------|----|-------|--------|
| gap_fade | XAUUSD | 1.5 | 2.0 | None | None | 78 | +153.246 | 53.8 | 1.614 | 3898.3 | 0.04 |
| gap_fade | XAUUSD | 1.5 | 3.0 | None | None | 77 | +147.870 | 45.5 | 1.496 | 5362.6 | 0.04 |
| gap_fade | XAUUSD | 1.0 | 3.0 | None | None | 77 | +146.367 | 36.4 | 1.581 | 3317.1 | 0.04 |
| gap_fade | XAUUSD | 2.0 | 2.0 | None | None | 78 | +133.361 | 57.7 | 1.467 | 4123.3 | 0.04 |
| gap_fade | XAUUSD | 1.0 | 2.0 | None | None | 78 | +130.425 | 43.6 | 1.604 | 2653.1 | 0.04 |
| gap_fade | XAUUSD | 2.0 | 3.0 | None | None | 77 | +121.330 | 49.4 | 1.349 | 5402.4 | 0.04 |
| gap_fade | XAUUSD | 1.5 | 1.5 | None | None | 79 | +118.653 | 59.5 | 1.52 | 3898.3 | 0.04 |
| gap_fade | XAUUSD | 1.0 | 1.5 | None | None | 79 | +109.424 | 49.4 | 1.562 | 2653.1 | 0.04 |
| gap_fade | XAUUSD | 2.0 | 1.5 | None | None | 79 | +108.203 | 64.6 | 1.422 | 4123.3 | 0.04 |
| gap_fade | XAUUSD | 1.5 | 2.0 | no-LATE | None | 75 | +104.128 | 53.3 | 1.407 | 3898.3 | 0.03 |
| gap_fade | XAUUSD | 1.0 | 2.0 | no-LATE | None | 75 | +89.254 | 44.0 | 1.41 | 2653.1 | 0.03 |
| gap_fade | XAUUSD | 2.0 | 2.0 | no-LATE | None | 75 | +84.620 | 57.3 | 1.29 | 4123.3 | 0.03 |
| gap_fade | XAUUSD | 1.5 | 1.5 | no-LATE | None | 76 | +83.739 | 59.2 | 1.359 | 3898.3 | 0.04 |
| gap_fade | XAUUSD | 1.0 | 1.5 | no-LATE | None | 76 | +81.240 | 50.0 | 1.415 | 2653.1 | 0.04 |
| gap_fade | XAUUSD | 1.0 | 3.0 | no-LATE | None | 74 | +78.019 | 36.5 | 1.305 | 3317.1 | 0.03 |
| gap_fade | XAUUSD | 2.0 | 1.5 | no-LATE | None | 76 | +74.035 | 64.5 | 1.283 | 4123.3 | 0.04 |
| gap_fade | XAUUSD | 1.5 | 1.0 | None | None | 79 | +69.870 | 68.3 | 1.379 | 4141.9 | 0.04 |
| gap_fade | XAUUSD | 1.5 | 3.0 | no-LATE | None | 74 | +67.214 | 44.6 | 1.22 | 5362.6 | 0.03 |
| gap_fade | XAUUSD | 1.0 | 1.0 | None | None | 79 | +61.025 | 58.2 | 1.371 | 2653.1 | 0.04 |
| gap_fade | XAUUSD | 1.5 | 1.0 | no-LATE | None | 76 | +47.956 | 68.4 | 1.255 | 4141.9 | 0.04 |
| gap_fade | XAUUSD | 2.0 | 1.0 | None | None | 79 | +45.977 | 70.9 | 1.215 | 4123.3 | 0.04 |
| gap_fade | XAUUSD | 1.0 | 1.0 | no-LATE | None | 76 | +44.204 | 59.2 | 1.269 | 2653.1 | 0.04 |
| gap_fade | XAUUSD | 2.0 | 3.0 | no-LATE | None | 74 | +40.788 | 48.6 | 1.114 | 5402.4 | 0.03 |
| gap_fade | XAUUSD | 2.0 | 1.0 | no-LATE | None | 76 | +24.277 | 71.0 | 1.112 | 4123.3 | 0.04 |
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

*S1 = candidates -> S2 walk-forward+FDR -> S3 holdout. Chief directive + GRID RULING.*