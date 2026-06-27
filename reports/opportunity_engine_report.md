# Opportunity Engine — kutoka CCS hadi MAAMUZI (Phase 8)

*2026-06-27 18:50 | OppScore = Quality(CCS) × Availability(frequency) | OUT-OF-SAMPLE (rank kwa TRAIN 70%, pima kwa TEST 30%) | min N=100 | configs tradeable (train_ccs>0): 494/1492*

> **Lengo (Chief):** sio edge mpya — bali kuthibitisha CCS inaweza kuwa mfumo wa MAAMUZI bila ML. **F-025 (APPROVED):** Edge ina Magnitude NA Availability. **Principle 25:** Opportunity Score = Quality × Availability. **F-023/P23:** rank Configurations, usi-classify Trades. NO ML bado (CCS/OppScore = target ya baadaye ya ML). Profitable ≠ Tradable Edge.


## Q1 — CCS-ranked vs trade-all (portfolio EV ya TEST, per-trade)

- **trade-all**: EV = **-1.122** pips/trade (configs 1492, test trades 574,059)
- **CCS-selected (train_ccs>0)**: EV = **-0.757** pips/trade (configs 494, test trades 163,051)
- **uplift = +0.365 pips/trade**

| select Top% (train_ccs) | configs | test EV/trade | test total pips | test trades |
|-------------------------|---------|---------------|-----------------|-------------|
| 5% | 74 | -1.162 | -36,328 | 31,262 |
| 10% | 149 | -0.639 | -38,573 | 60,320 |
| 20% | 298 | -0.330 | -34,949 | 105,882 |
| 50% | 746 | -0.779 | -192,343 | 247,011 |

→ ⚠️ CCS-ranking haijaboresha vya kutosha.

## Q2 — Concentration: top configs zinabeba edge kiasi gani? (TEST pips)

*Universe ya tradeable (train_ccs>0): 494 configs; jumla TEST pips = -123,418*

| top% (kwa train_ccs) | configs | cum TEST pips | % ya edge yote |
|----------------------|---------|---------------|----------------|
| 5% | 24 | -9,741 | 8% |
| 10% | 49 | -16,726 | 14% |
| 20% | 98 | -47,705 | 39% |
| 50% | 247 | -44,954 | 36% |

→ Top 20% ya configurations zinabeba **39%** ya edge — edge imesambaa zaidi.

## Q3 — Je Availability inaboresha portfolio? CCS-pekee vs OppScore=CCS×Availability

*Kwa kila budget (idadi ya configs zinazochaguliwa), JUMLA ya TEST pips (out-of-sample):*

| budget (configs) | CCS-only: total pips | EV/trade | OppScore: total pips | EV/trade | OppScore − CCS |
|------------------|----------------------|----------|----------------------|----------|----------------|
| 10 | -2,650 | -0.86 | -19,652 | -1.45 | -17,002 |
| 25 | -10,352 | -1.21 | +3,446 | +0.11 | +13,798 |
| 50 | -16,193 | -0.92 | -12,427 | -0.26 | +3,766 |
| 100 | -43,968 | -1.04 | -32,017 | -0.49 | +11,951 |

→ ⚠️: kwa budget 3/4, OppScore (Quality × Availability) inakusanya JUMLA kubwa zaidi ya pips kuliko CCS pekee — portfolio return inahitaji frequency, sio magnitude tu. (CCS-only huchagua configs adimu zenye quality juu lakini throughput ndogo.)

## Q4 — PRIORITY QUEUE (bila ML): Top 30/467 kwa OppScore = CCS × Availability

| # | Configuration | N | full EV | full CCS | OppScore |
|---|---------------|---|---------|----------|----------|
| 1 | EURJPY·trend_continuation·C0·LOW·LONG·NORMAL | 10,503 | +2.79 | +2.04 | +21,414 |
| 2 | USDJPY·trend_continuation·C0·HIGH·LONG·NORMAL | 5,983 | +2.87 | +1.96 | +11,755 |
| 3 | USDJPY·trend_continuation·C0·NORMAL·LONG·NORMAL | 8,493 | +1.55 | +0.83 | +7,057 |
| 4 | USDJPY·trend_continuation·C0·LOW·LONG·NORMAL | 10,839 | +1.17 | +0.64 | +6,941 |
| 5 | USDCAD·trend_continuation·C0·HIGH·LONG·NORMAL | 5,890 | +1.37 | +1.16 | +6,830 |
| 6 | EURJPY·trend_continuation·C0·HIGH·LONG·NORMAL | 5,735 | +1.75 | +1.19 | +6,815 |
| 7 | USDJPY·trend_continuation·C1·LOW·LONG·NORMAL | 2,061 | +5.63 | +3.03 | +6,242 |
| 8 | USDCHF·trend_continuation·C3·HIGH·SHORT·NORMAL | 2,873 | +2.53 | +1.87 | +5,383 |
| 9 | USDCAD·mean_reversion·C0·NORMAL·LONG·NORMAL | 4,036 | +1.79 | +1.15 | +4,624 |
| 10 | EURJPY·breakout·C0·LOW·LONG·NORMAL | 2,190 | +3.73 | +2.05 | +4,480 |
| 11 | EURUSD·mean_reversion·C0·LOW·LONG·NORMAL | 4,087 | +1.35 | +1.07 | +4,383 |
| 12 | EURJPY·pullback·C1·HIGH·LONG·NORMAL | 1,844 | +4.76 | +1.85 | +3,413 |
| 13 | GBPUSD·mean_reversion·C0·HIGH·SHORT·NORMAL | 2,597 | +1.88 | +1.30 | +3,369 |
| 14 | USDJPY·mean_reversion·C0·HIGH·LONG·NORMAL | 2,238 | +2.67 | +1.47 | +3,299 |
| 15 | EURUSD·mean_reversion·C0·NORMAL·LONG·NORMAL | 3,615 | +1.42 | +0.88 | +3,188 |
| 16 | USDCHF·mean_reversion·C0·NORMAL·SHORT·NORMAL | 4,320 | +1.11 | +0.72 | +3,107 |
| 17 | EURJPY·mean_reversion·C3·HIGH·LONG·NORMAL | 1,447 | +4.53 | +2.06 | +2,980 |
| 18 | EURJPY·mean_reversion·C3·HIGH·SHORT·WIDE | 557 | +17.64 | +5.05 | +2,812 |
| 19 | USDJPY·trend_continuation·C3·LOW·LONG·NORMAL | 1,667 | +3.35 | +1.59 | +2,651 |
| 20 | EURUSD·trend_continuation·C1·LOW·LONG·NORMAL | 1,272 | +3.62 | +2.03 | +2,577 |
| 21 | EURUSD·mean_reversion·C0·HIGH·SHORT·NORMAL | 2,238 | +2.10 | +1.15 | +2,567 |
| 22 | EURJPY·breakout·C0·HIGH·LONG·NORMAL | 1,388 | +3.17 | +1.82 | +2,523 |
| 23 | GBPUSD·mean_reversion·C0·LOW·LONG·NORMAL | 3,996 | +1.36 | +0.61 | +2,427 |
| 24 | EURJPY·deep_pullback·C0·LOW·LONG·NORMAL | 4,633 | +0.94 | +0.52 | +2,402 |
| 25 | USDJPY·deep_pullback·C0·HIGH·LONG·NORMAL | 2,341 | +2.42 | +1.02 | +2,380 |
| 26 | EURJPY·pullback·C0·LOW·LONG·NORMAL | 3,649 | +1.44 | +0.65 | +2,373 |
| 27 | USDJPY·mean_reversion·C1·HIGH·SHORT·NORMAL | 1,144 | +4.73 | +1.99 | +2,274 |
| 28 | EURUSD·deep_pullback·C0·LOW·LONG·NORMAL | 4,033 | +0.94 | +0.56 | +2,249 |
| 29 | USDJPY·pullback·C1·LOW·LONG·NORMAL | 643 | +10.75 | +3.36 | +2,164 |
| 30 | USDCAD·mean_reversion·C3·HIGH·SHORT·NORMAL | 1,640 | +2.63 | +1.28 | +2,096 |

→ ✅ **Q4: NDIYO** — priority queue ni rule-based deterministic (panga kwa OppScore), hakuna ML. Hii ndiyo entity Opportunity Engine inatoa: orodha ya configurations kwa kipaumbele.

## VERDICT — Phase 8 Opportunity Engine

→ ⚠️ CCS-selection haijageuza portfolio kuwa chanya kwa uhakika out-of-sample; inahitaji uchambuzi zaidi (cost model, walk-forward ya muda mrefu) kabla ya Opportunity Engine kamili.

*OppScore = Quality(CCS) × Availability(frequency) [F-025/Principle 25]. Validation YOTE out-of-sample (rank kwa train, pima kwa test; no-lookahead). Q1 portfolio uplift, Q2 concentration (Pareto), Q3 availability faida, Q4 priority queue bila ML. Architecture: Configuration → Confidence → Opportunity → Portfolio. NO ML bado (CCS/OppScore = target ya ML). Profitable ≠ Tradable Edge (hakuna cost model kamili / walk-forward ya muda).*