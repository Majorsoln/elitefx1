# Event Quality — entries V1 (conditions) vs V2 (episodes) — TRAIN TU

*2026-07-09 09:17 | TF=H1 | pairs=9 | TRAIN < 2023-01-01 (sacred splits) | exit SL/TP 1.5/1.5 ATR, timeout 24b, tie->SL | costs = spr halisi + slip (mkt 0.1/stop 0.3) | episode = position 1 kwa event x pair*

> **UAMINIFU (Chief):** hii ni EXPLORATION ya TRAIN inayolisha grid ya S1 — SIO edge claim. Kila namba ni in-sample; uthibitisho = S2 (walk-forward+FDR) na S3 (holdout, mara moja). LESSON-001/002/029. Profitable != Tradable Edge.


## 1) V1 vs V2 — aggregate (pairs zote)

| event | N | trades/siku | EV net (pips) | win% | PF |
|-------|---|-------------|---------------|------|----|
| v1:pullback | 29,701 | 1.81 | -1.238 | 49.4 | 0.90 |
| v1:deep_pullback | 29,701 | 1.81 | -1.197 | 49.8 | 0.90 |
| v1:breakout | 28,172 | 1.72 | -1.249 | 49.6 | 0.90 |
| v1:volatility_breakout | 27,730 | 1.69 | -1.208 | 49.7 | 0.90 |
| v1:trend_continuation | 46,048 | 2.81 | -0.943 | 50.2 | 0.92 |
| v1:volatility_expansion | 29,055 | 1.77 | -0.832 | 50.3 | 0.93 |
| v1:news_shock | 9,622 | 0.59 | -0.743 | 50.7 | 0.94 |
| v1:mean_reversion | 37,869 | 2.31 | -1.199 | 49.4 | 0.90 |
| v1:pattern_completion | 22,276 | 1.36 | -1.460 | 48.9 | 0.88 |
| v2:pullback_v2 | 25,550 | 1.56 | -1.485 | 49.0 | 0.88 |
| v2:trend_resume | 21,453 | 1.31 | -1.501 | 48.9 | 0.88 |
| v2:jump_off | 24,971 | 1.52 | -4.487 | 42.1 | 0.68 |
| v2:breakout_stop | 36,923 | 2.25 | -2.846 | 46.1 | 0.78 |
| v2:second_chance | 5,938 | 0.36 | -0.446 | 51.8 | 0.96 |
| v2:big_range_mo | 24,460 | 1.49 | -1.331 | 49.5 | 0.89 |
| v2:session_orb | 18,165 | 1.11 | -0.753 | 50.4 | 0.94 |
| v2:lowvol_reversal | 27,468 | 1.67 | -1.013 | 50.0 | 0.92 |
| v2:pattern_3lows | 21,402 | 1.30 | -1.504 | 48.8 | 0.88 |
| v2:mr_zscore | 15,810 | 0.96 | -1.114 | 49.6 | 0.91 |
| v2:shock_follow | 8,588 | 0.52 | -0.812 | 50.9 | 0.93 |
| v2:rsi2_pullback | 12,844 | 0.78 | -0.810 | 50.5 | 0.93 |
| v2:bb_fade | 18,196 | 1.11 | -1.423 | 48.9 | 0.89 |
| v2:engulf_extreme | 5,424 | 0.33 | -1.731 | 48.2 | 0.85 |
| v2:inside_break | 20,859 | 1.27 | -1.148 | 50.1 | 0.91 |
| v2:nr7_break | 21,421 | 1.30 | -0.108 | 52.4 | 0.99 |

## 2) V2 kwa pair (rows za juu kwa EV, min N=30)

| event | pair | N | EV net (pips) | win% | PF |
|-------|------|---|---------------|------|----|
| v2:second_chance | EURJPY | 666 | +1.568 | 54.7 | 1.11 |
| v2:shock_follow | EURJPY | 927 | +1.170 | 53.9 | 1.08 |
| v2:nr7_break | GBPUSD | 2,246 | +0.908 | 53.5 | 1.05 |
| v2:second_chance | USDCHF | 615 | +0.712 | 55.6 | 1.08 |
| v2:nr7_break | AUDUSD | 2,569 | +0.574 | 54.0 | 1.06 |
| v2:session_orb | USDJPY | 1,868 | +0.518 | 52.0 | 1.05 |
| v2:inside_break | USDJPY | 2,514 | +0.469 | 51.7 | 1.04 |
| v2:shock_follow | USDJPY | 919 | +0.378 | 52.9 | 1.03 |
| v2:nr7_break | EURGBP | 2,261 | +0.352 | 53.5 | 1.04 |
| v2:nr7_break | USDJPY | 2,589 | +0.247 | 52.2 | 1.02 |
| v2:trend_resume | EURJPY | 2,386 | +0.154 | 51.8 | 1.01 |
| v2:second_chance | EURUSD | 666 | +0.151 | 52.6 | 1.01 |
| v2:nr7_break | EURUSD | 2,215 | +0.140 | 52.0 | 1.01 |
| v2:shock_follow | EURUSD | 997 | +0.018 | 51.5 | 1.00 |
| v2:second_chance | GBPUSD | 704 | -0.044 | 53.0 | 1.00 |
| v2:rsi2_pullback | EURUSD | 1,440 | -0.050 | 50.8 | 1.00 |
| v2:lowvol_reversal | EURJPY | 3,136 | -0.100 | 50.7 | 0.99 |
| v2:session_orb | EURUSD | 2,058 | -0.103 | 50.9 | 0.99 |
| v2:session_orb | EURJPY | 1,946 | -0.115 | 51.2 | 0.99 |
| v2:nr7_break | USDCAD | 2,263 | -0.125 | 52.5 | 0.99 |
| v2:session_orb | GBPUSD | 2,165 | -0.151 | 51.8 | 0.99 |
| v2:rsi2_pullback | USDJPY | 1,394 | -0.250 | 51.1 | 0.98 |
| v2:rsi2_pullback | USDCAD | 1,415 | -0.426 | 51.0 | 0.97 |
| v2:rsi2_pullback | USDCHF | 1,397 | -0.499 | 52.0 | 0.95 |
| v2:mr_zscore | USDCAD | 1,761 | -0.541 | 51.6 | 0.96 |

## 3) V2 kwa session (EV net pips; entry hour ya server time)

| event | ASIA | LONDON | NY | LATE |
|-------|-----|-----|-----|-----|
| v2:pullback_v2 | -1.04 (n=6118) | -1.47 (n=4471) | -0.84 (n=6261) | -2.27 (n=8700) |
| v2:trend_resume | -2.02 (n=6153) | -0.69 (n=4403) | -1.33 (n=5351) | -1.73 (n=5546) |
| v2:jump_off | -3.67 (n=4259) | -4.85 (n=6683) | -5.16 (n=9455) | -3.33 (n=4574) |
| v2:breakout_stop | -2.30 (n=9848) | -2.06 (n=9444) | -3.69 (n=11404) | -3.35 (n=6227) |
| v2:second_chance | -1.14 (n=1735) | -0.57 (n=685) | -0.78 (n=956) | +0.18 (n=2562) |
| v2:big_range_mo | -1.61 (n=7557) | -0.87 (n=7172) | -1.43 (n=7383) | -1.52 (n=2348) |
| v2:session_orb | — | -0.78 (n=13085) | -0.70 (n=5080) | — |
| v2:lowvol_reversal | -1.14 (n=6254) | -0.97 (n=4249) | -1.72 (n=5310) | -0.64 (n=11655) |
| v2:pattern_3lows | -1.27 (n=5662) | -1.17 (n=5095) | -1.03 (n=5710) | -2.66 (n=4935) |
| v2:mr_zscore | -1.28 (n=3865) | -1.38 (n=4970) | -1.19 (n=4493) | -0.17 (n=2482) |
| v2:shock_follow | +0.99 (n=1138) | -0.50 (n=2419) | -1.41 (n=4238) | -1.16 (n=793) |
| v2:rsi2_pullback | -1.37 (n=4483) | -0.85 (n=3164) | -0.35 (n=2754) | -0.25 (n=2443) |
| v2:bb_fade | -1.26 (n=2687) | -1.49 (n=4075) | -1.23 (n=6285) | -1.70 (n=5149) |
| v2:engulf_extreme | -0.73 (n=1260) | -1.99 (n=1796) | -1.90 (n=1519) | -2.38 (n=849) |
| v2:inside_break | -0.38 (n=5429) | -0.01 (n=3935) | -0.67 (n=4462) | -2.68 (n=7033) |
| v2:nr7_break | +0.59 (n=3807) | +2.23 (n=1296) | +2.64 (n=3356) | -1.26 (n=12962) |

## 4) V2 kwa VOLATILITY STATE (uchambuzi wa soko — market_state_engine, deseasonalized, no-lookahead)

| event | LOW | NORMAL | HIGH |
|-------|-----|-----|-----|
| v2:pullback_v2 | -1.60 (n=7366) | -1.29 (n=8157) | -1.52 (n=8980) |
| v2:trend_resume | -1.27 (n=6025) | -1.43 (n=6921) | -1.89 (n=7652) |
| v2:jump_off | -4.92 (n=6105) | -4.20 (n=7972) | -4.28 (n=9837) |
| v2:breakout_stop | -2.77 (n=10150) | -2.90 (n=11988) | -2.88 (n=13252) |
| v2:second_chance | +0.15 (n=1701) | -0.67 (n=1909) | -0.50 (n=2084) |
| v2:big_range_mo | -1.19 (n=6996) | -1.38 (n=7990) | -1.64 (n=8466) |
| v2:session_orb | -1.39 (n=5242) | -0.70 (n=6048) | -0.18 (n=6163) |
| v2:lowvol_reversal | -1.28 (n=7756) | -0.86 (n=8808) | -0.81 (n=9781) |
| v2:pattern_3lows | -1.34 (n=6039) | -2.07 (n=6994) | -1.21 (n=7509) |
| v2:mr_zscore | -1.14 (n=4391) | -0.93 (n=5097) | -0.97 (n=5678) |
| v2:shock_follow | -1.25 (n=2085) | +0.25 (n=2787) | -1.56 (n=3367) |
| v2:rsi2_pullback | -0.84 (n=3898) | -0.50 (n=4136) | -0.87 (n=4277) |
| v2:bb_fade | -1.42 (n=5016) | -1.41 (n=5855) | -1.56 (n=6578) |
| v2:engulf_extreme | -1.66 (n=1668) | -1.42 (n=1782) | -1.78 (n=1773) |
| v2:inside_break | -1.83 (n=5815) | -1.42 (n=6638) | -0.61 (n=7532) |
| v2:nr7_break | -0.62 (n=6069) | -0.69 (n=6786) | +0.71 (n=7692) |

-> Cell chanya thabiti = event x state filter ya grid ya S1 (mf. 'mr_zscore NORMAL tu'). Phase 12 Q4 ilionyesha state-dependence; hapa inapimwa kwa trade structure halisi.

## VERDICT (descriptive tu)

- Linganisha jozi v1 vs v2 (mf. v1:pullback vs v2:pullback_v2): D1-fix inaonekana kwenye trades/siku na EV net.
- Rows za juu za sehemu 2 + sessions bora za sehemu 3 = grid ya S1 (strategy_lab). HAKUNA row inayoitwa 'strategy' kabla ya S2 (FDR) + S3 (holdout).


*Harness: episode non-overlap, next-bar honest, costs kila trade, TRAIN<2023-01-01. Chief direct. Profitable != Tradable Edge.*