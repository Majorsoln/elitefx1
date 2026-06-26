# Configuration Engine — atomic trading unit ya ELITEFX (Phase 6.5)

*2026-06-26 22:29 | Configuration = Pair·Event·LatentState(k=4)·Regime·Direction·ExecContext | EV±95%CI (net pips), Win, Triple Barrier (±1.0σ,10b) | outcome forward 6b net | walk-forward train 70% | min N=100*

> **F-021 (Chief, APPROVED):** No Event possesses universal edge; edge exists only inside a COMPLETE Market Configuration. **Principle 22:** a trading opportunity is represented by a Market Configuration, NEVER by an Event alone. Acceptance rule: Market Configuration → Expected Payoff (sio Indicator → BUY). **H-07 (OPEN):** Negative Edge is more stable than Positive Edge — je kuondoa configs mbaya kunashinda kuongeza nzuri? NO ML bado (target haijajengwa).

## Muhtasari

- Configurations zenye N≥100: **1,492**  |  EV>0: **467**  |  walk-forward stable (train/test ishara ileile): **868**


## Top 25 configurations kwa **out-of-sample (test) EV**

| Configuration | N | EV [95% CI] | Win% | TP/SL/TIME | train EV | test EV | stable |
|---------------|---|-------------|------|------------|----------|---------|--------|
| EURJPY·mean_reversion·C1·HIGH·SHORT·WIDE | 342 | +21.42 [+10.1,+32.7] | 55% | 53/40/7 | +19.49 | +25.89 | ✅ |
| GBPUSD·trend_continuation·C1·LOW·LONG·WIDE | 174 | +10.37 [+4.0,+16.7] | 53% | 55/41/3 | +4.16 | +24.56 | ✅ |
| GBPUSD·trend_continuation·C1·LOW·SHORT·WIDE | 228 | +13.63 [+3.1,+24.1] | 48% | 47/43/9 | +9.52 | +23.11 | ✅ |
| USDCHF·breakout·C3·HIGH·SHORT·WIDE | 412 | +5.50 [-0.6,+11.6] | 52% | 52/44/3 | -1.54 | +21.84 | — |
| USDJPY·breakout·C3·NORMAL·LONG·WIDE | 129 | +12.23 [+2.6,+21.9] | 53% | 49/48/3 | +8.67 | +20.44 | ✅ |
| USDJPY·trend_continuation·C3·LOW·SHORT·WIDE | 110 | -0.41 [-12.3,+11.4] | 47% | 51/43/6 | -9.07 | +19.80 | — |
| GBPUSD·trend_continuation·C3·LOW·SHORT·WIDE | 240 | +10.13 [+4.6,+15.7] | 58% | 55/42/4 | +6.34 | +18.95 | ✅ |
| USDJPY·breakout·C0·HIGH·LONG·WIDE | 268 | +8.72 [+3.0,+14.4] | 52% | 51/45/4 | +4.59 | +18.25 | ✅ |
| USDCAD·pullback·C3·HIGH·SHORT·WIDE | 334 | -3.54 [-11.2,+4.2] | 51% | 51/46/3 | -12.87 | +17.99 | — |
| AUDUSD·mean_reversion·C1·NORMAL·LONG·WIDE | 103 | +7.25 [-0.2,+14.7] | 59% | 50/49/2 | +2.82 | +17.52 | ✅ |
| USDCAD·mean_reversion·C1·HIGH·SHORT·WIDE | 247 | +0.25 [-8.9,+9.4] | 51% | 52/43/6 | -7.29 | +17.51 | — |
| USDJPY·breakout·C3·HIGH·SHORT·WIDE | 624 | +7.03 [-0.1,+14.2] | 49% | 53/46/1 | +2.69 | +17.10 | ✅ |
| GBPUSD·deep_pullback·C3·NORMAL·LONG·NORMAL | 561 | +1.78 [-3.2,+6.8] | 48% | 47/48/5 | -4.75 | +16.95 | — |
| USDJPY·trend_continuation·C3·NORMAL·LONG·WIDE | 303 | +8.11 [+1.4,+14.9] | 53% | 47/51/3 | +4.38 | +16.80 | ✅ |
| EURJPY·deep_pullback·C1·LOW·LONG·WIDE | 122 | +7.92 [-3.1,+18.9] | 57% | 57/41/2 | +4.15 | +16.58 | ✅ |
| EURUSD·trend_continuation·C1·LOW·LONG·WIDE | 193 | -2.47 [-9.2,+4.3] | 44% | 48/46/6 | -10.49 | +16.20 | — |
| USDJPY·mean_reversion·C1·HIGH·SHORT·NORMAL | 1,144 | +4.73 [+0.9,+8.6] | 52% | 49/44/8 | -0.12 | +16.02 | — |
| EURJPY·mean_reversion·C3·NORMAL·LONG·WIDE | 309 | +5.41 [-1.3,+12.1] | 50% | 43/50/6 | +1.09 | +15.44 | ✅ |
| EURJPY·mean_reversion·C1·HIGH·LONG·WIDE | 277 | +13.12 [+6.1,+20.1] | 65% | 60/32/8 | +12.16 | +15.33 | ✅ |
| EURJPY·mean_reversion·C3·HIGH·SHORT·WIDE | 557 | +17.64 [+8.3,+27.0] | 53% | 48/45/8 | +19.15 | +14.15 | ✅ |
| USDJPY·deep_pullback·C1·NORMAL·LONG·WIDE | 136 | +4.64 [-4.5,+13.8] | 51% | 46/47/7 | +0.59 | +14.01 | ✅ |
| USDCHF·breakout·C0·HIGH·SHORT·WIDE | 201 | +3.75 [-1.6,+9.1] | 49% | 50/48/2 | -0.65 | +13.84 | — |
| USDCAD·pullback·C1·HIGH·SHORT·WIDE | 511 | -3.57 [-9.3,+2.2] | 46% | 44/49/7 | -10.87 | +13.35 | — |
| USDJPY·trend_continuation·C0·HIGH·LONG·WIDE | 1,206 | +3.46 [+1.1,+5.8] | 52% | 49/47/4 | -0.52 | +12.75 | — |
| USDCAD·mean_reversion·C3·HIGH·SHORT·WIDE | 651 | -0.32 [-7.1,+6.4] | 52% | 49/45/5 | -5.92 | +12.66 | — |

## Bottom 25 configurations — **'WAPI USIFANYE TRADE'** (test EV mbaya zaidi)

| Configuration | N | EV [95% CI] | Win% | TP/SL/TIME | train EV | test EV | stable |
|---------------|---|-------------|------|------------|----------|---------|--------|
| EURJPY·trend_continuation·C2·NORMAL·SHORT·WIDE | 103 | -13.85 [-24.0,-3.7] | 33% | 44/56/0 | -4.90 | -34.63 | ✅ |
| NZDUSD·breakout·C1·NORMAL·SHORT·NORMAL | 193 | -9.11 [-16.0,-2.2] | 45% | 45/51/4 | -1.45 | -26.93 | ✅ |
| EURJPY·breakout·C1·HIGH·LONG·WIDE | 119 | -37.04 [-57.8,-16.3] | 40% | 39/52/8 | -41.49 | -26.79 | ✅ |
| USDJPY·mean_reversion·C3·NORMAL·SHORT·WIDE | 184 | -11.11 [-19.8,-2.5] | 44% | 45/53/3 | -4.89 | -25.35 | ✅ |
| EURJPY·breakout·C3·NORMAL·SHORT·WIDE | 186 | -7.78 [-15.9,+0.4] | 48% | 51/48/2 | -0.42 | -24.88 | ✅ |
| USDCAD·trend_continuation·C2·HIGH·SHORT·WIDE | 131 | -16.66 [-23.5,-9.8] | 24% | 31/53/16 | -13.06 | -24.85 | ✅ |
| USDCAD·breakout·C1·NORMAL·LONG·NORMAL | 135 | -6.48 [-15.0,+2.0] | 44% | 47/44/9 | +1.46 | -24.67 | — |
| EURJPY·trend_continuation·C2·LOW·SHORT·WIDE | 122 | -9.53 [-21.7,+2.6] | 29% | 28/70/2 | -3.28 | -23.88 | ✅ |
| USDJPY·trend_continuation·C2·LOW·SHORT·WIDE | 143 | -12.41 [-21.6,-3.2] | 34% | 32/66/1 | -7.64 | -23.49 | ✅ |
| USDCAD·mean_reversion·C1·NORMAL·SHORT·WIDE | 101 | -6.99 [-20.1,+6.1] | 46% | 47/51/2 | +0.05 | -22.87 | — |
| USDCAD·breakout·C1·LOW·LONG·NORMAL | 111 | -8.29 [-17.3,+0.7] | 40% | 41/53/5 | -2.05 | -22.41 | ✅ |
| EURJPY·pullback·C1·LOW·SHORT·WIDE | 122 | -12.96 [-23.9,-2.0] | 39% | 39/59/2 | -9.12 | -21.79 | ✅ |
| USDJPY·breakout·C1·HIGH·LONG·NORMAL | 423 | -11.04 [-17.0,-5.1] | 44% | 39/53/8 | -6.45 | -21.73 | ✅ |
| USDCAD·deep_pullback·C3·HIGH·LONG·WIDE | 334 | +0.70 [-7.0,+8.4] | 48% | 45/52/3 | +10.07 | -20.91 | — |
| EURJPY·breakout·C1·HIGH·LONG·NORMAL | 401 | -8.09 [-14.9,-1.3] | 46% | 39/53/8 | -2.55 | -20.90 | ✅ |
| EURJPY·breakout·C1·HIGH·SHORT·NORMAL | 230 | -4.92 [-14.3,+4.5] | 43% | 41/56/3 | +1.44 | -19.78 | — |
| GBPUSD·pullback·C3·NORMAL·SHORT·NORMAL | 561 | -3.64 [-8.7,+1.4] | 50% | 46/49/5 | +3.01 | -19.05 | — |
| EURUSD·breakout·C0·LOW·SHORT·WIDE | 234 | -8.74 [-14.4,-3.1] | 40% | 38/59/3 | -4.39 | -18.74 | ✅ |
| USDJPY·mean_reversion·C3·HIGH·LONG·WIDE | 1,020 | -9.30 [-15.4,-3.2] | 49% | 44/54/2 | -5.45 | -18.30 | ✅ |
| GBPUSD·breakout·C1·LOW·SHORT·NORMAL | 140 | -6.07 [-17.2,+5.0] | 44% | 34/56/10 | -0.95 | -18.02 | ✅ |
| USDJPY·pullback·C2·LOW·SHORT·WIDE | 111 | -8.99 [-16.6,-1.4] | 38% | 39/59/3 | -5.22 | -17.54 | ✅ |
| USDCAD·deep_pullback·C1·HIGH·LONG·WIDE | 511 | -0.05 [-5.8,+5.7] | 50% | 49/44/7 | +7.42 | -17.38 | — |
| GBPUSD·breakout·C3·NORMAL·SHORT·NORMAL | 707 | -3.57 [-8.0,+0.8] | 48% | 45/51/5 | +2.37 | -17.36 | — |
| GBPUSD·trend_continuation·C2·HIGH·SHORT·WIDE | 108 | -7.90 [-19.6,+3.8] | 30% | 42/50/8 | -3.78 | -17.27 | ✅ |
| USDCAD·trend_continuation·C3·HIGH·LONG·WIDE | 1,170 | -5.01 [-9.9,-0.2] | 44% | 42/52/5 | +0.23 | -17.25 | — |

## H-07 — Negative Edge ni stable zaidi? Remove-bad vs Add-good (out-of-sample)

| portfolio (test, no-lookahead) | EV (pips) | N test |
|--------------------------------|-----------|--------|
| baseline (trade-all) | -1.122 | 574,059 |
| add-good (train_ev>0 tu) | -0.757 | 163,051 |
| remove-bad (zote ila train_ev<0) | -0.757 | 163,051 |

- uplift add-good = **+0.365** | uplift remove-bad = **+0.365** (juu ya baseline)
- persistence: train-positive→positive **42%** (N=494) vs train-negative→negative **66%** (N=998)

→ ✅ **H-07 inaungwa mkono**: kuondoa configurations mbaya kunaboresha EV ≥ kuongeza nzuri, NA negative edge inaendelea (persist) zaidi out-of-sample. 'Trade less, but in the right environment.' (Experimental — thibitisha kwa walk-forward zaidi.)

## VERDICT — F-021 / Principle 22

→ ✅ **Configuration ndio atomic unit**: kati ya 1,492 configurations, **868** zina edge inayoendelea out-of-sample (train/test ishara ileile). Event peke yake (EV hasi) HAITOSHI — edge ipo ndani ya configuration kamili (F-021). Hizi Configuration Objects ndizo msingi wa Opportunity Engine (rank kwa Expected Payoff).

*Configuration = Pair·Event·LatentState·Regime·Direction·ExecContext (atomic trading unit). EV±CI/Win/TB per configuration; stable = train/test (walk-forward) ishara ileile (no-lookahead). H-07: remove-bad vs add-good out-of-sample. Principle 22: opportunity = Configuration, sio Event. F-019: information ina value tu ikiboresha payoff/decision. Acceptance: Market Configuration → Expected Payoff kabla ya Opportunity Engine. NO ML bado. Profitable ≠ Tradable Edge.*