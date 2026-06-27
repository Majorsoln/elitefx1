# Configuration Confidence Engine — ranking ya institutional grade (Phase 7)

*2026-06-26 22:52 | Configuration = Pair·Event·LatentState(k=4)·Regime·Direction·ExecContext | CCS = EV × Confidence × Persistence × SampleQuality | 5-fold walk-forward | outcome forward 6b net | min N=100*

> **Principle 24 (Chief):** hakuna Configuration inapangwa (ranked) kwa Expected Payoff PEKE YAKE — lazima iingie confidence interval, persistence, walk-forward stability, sample quality. **F-023:** ranking ndio lugha ya asili ya Opportunity Engine (sio classification). **F-024 (OPEN):** Confidence ina thamani sawa na Expected Payoff. **F-022 (APPROVED):** configs mbaya zina persistence kubwa kuliko nzuri. CCS = target ya baadaye ya ML (Configuration Score, sio BUY/SELL). NO ML bado.

## Muhtasari

- Configurations zenye N≥100: **1,492**  |  CCS>0: **467**  |  EV-rank vs CCS-rank Spearman ρ = **+0.91**  |  Top-25 overlap (EV vs CCS): **10/25**


## Top 25 configurations kwa **CCS** (opportunities zenye ushahidi bora)

| Configuration | N | EV [95% CI] | t | conf | persist | stab | sampleQ | CCS |
|---------------|---|-------------|---|------|---------|------|---------|-----|
| EURJPY·mean_reversion·C1·HIGH·SHORT·WIDE | 342 | +21.42 [+10.1,+32.7] | +3.7 | 1.00 | 1.00 | 0.61 | 0.25 | **+5.46** |
| EURJPY·mean_reversion·C3·HIGH·SHORT·WIDE | 557 | +17.64 [+8.3,+27.0] | +3.7 | 1.00 | 0.80 | 0.00 | 0.36 | **+5.05** |
| USDJPY·pullback·C1·LOW·LONG·NORMAL | 643 | +10.75 [+5.4,+16.1] | +3.9 | 1.00 | 0.80 | 0.21 | 0.39 | **+3.36** |
| USDJPY·trend_continuation·C1·LOW·LONG·NORMAL | 2,061 | +5.63 [+2.2,+9.1] | +3.2 | 1.00 | 0.80 | 0.36 | 0.67 | **+3.03** |
| USDJPY·pullback·C3·NORMAL·SHORT·NORMAL | 658 | +6.36 [+0.5,+12.2] | +2.1 | 0.97 | 1.00 | 0.48 | 0.40 | **+2.44** |
| EURJPY·mean_reversion·C0·HIGH·LONG·WIDE | 390 | +8.70 [+3.8,+13.6] | +3.5 | 1.00 | 1.00 | 0.43 | 0.28 | **+2.44** |
| EURJPY·mean_reversion·C1·HIGH·LONG·WIDE | 277 | +13.12 [+6.1,+20.1] | +3.7 | 1.00 | 0.80 | 0.32 | 0.22 | **+2.28** |
| USDJPY·deep_pullback·C1·HIGH·LONG·WIDE | 445 | +8.95 [+2.3,+15.6] | +2.6 | 0.99 | 0.80 | 0.00 | 0.31 | **+2.19** |
| GBPUSD·breakout·C3·HIGH·SHORT·WIDE | 558 | +8.60 [-2.5,+19.6] | +1.5 | 0.87 | 0.80 | 0.00 | 0.36 | **+2.15** |
| EURJPY·mean_reversion·C3·HIGH·LONG·NORMAL | 1,447 | +4.53 [+0.2,+8.9] | +2.1 | 0.96 | 0.80 | 0.00 | 0.59 | **+2.06** |
| USDCAD·mean_reversion·C1·HIGH·SHORT·NORMAL | 991 | +4.14 [+1.5,+6.8] | +3.1 | 1.00 | 1.00 | 0.58 | 0.50 | **+2.05** |
| EURJPY·breakout·C0·LOW·LONG·NORMAL | 2,190 | +3.73 [+1.5,+6.0] | +3.3 | 1.00 | 0.80 | 0.39 | 0.69 | **+2.05** |
| USDJPY·breakout·C3·HIGH·SHORT·WIDE | 624 | +7.03 [-0.1,+14.2] | +1.9 | 0.95 | 0.80 | 0.00 | 0.38 | **+2.04** |
| EURJPY·trend_continuation·C0·LOW·LONG·NORMAL | 10,503 | +2.79 [+1.9,+3.7] | +5.9 | 1.00 | 0.80 | 0.19 | 0.91 | **+2.04** |
| EURUSD·trend_continuation·C1·LOW·LONG·NORMAL | 1,272 | +3.62 [+1.4,+5.9] | +3.2 | 1.00 | 1.00 | 0.52 | 0.56 | **+2.03** |
| USDJPY·mean_reversion·C1·HIGH·SHORT·NORMAL | 1,144 | +4.73 [+0.9,+8.6] | +2.4 | 0.98 | 0.80 | 0.00 | 0.53 | **+1.99** |
| USDJPY·trend_continuation·C0·HIGH·LONG·NORMAL | 5,983 | +2.87 [+1.9,+3.9] | +5.7 | 1.00 | 0.80 | 0.45 | 0.86 | **+1.96** |
| GBPUSD·trend_continuation·C3·LOW·SHORT·WIDE | 240 | +10.13 [+4.6,+15.7] | +3.6 | 1.00 | 1.00 | 0.39 | 0.19 | **+1.96** |
| EURJPY·mean_reversion·C3·HIGH·LONG·WIDE | 804 | +5.86 [-0.7,+12.4] | +1.8 | 0.92 | 0.80 | 0.00 | 0.45 | **+1.92** |
| USDCHF·trend_continuation·C3·HIGH·SHORT·NORMAL | 2,873 | +2.53 [+0.9,+4.1] | +3.1 | 1.00 | 1.00 | 0.75 | 0.74 | **+1.87** |
| USDJPY·trend_continuation·C1·LOW·SHORT·WIDE | 121 | +17.24 [+5.5,+29.0] | +2.9 | 1.00 | 1.00 | 0.20 | 0.11 | **+1.85** |
| EURJPY·pullback·C1·HIGH·LONG·NORMAL | 1,844 | +4.76 [+1.8,+7.7] | +3.2 | 1.00 | 0.60 | 0.12 | 0.65 | **+1.85** |
| EURGBP·pullback·C3·HIGH·SHORT·NORMAL | 783 | +4.17 [+1.6,+6.7] | +3.2 | 1.00 | 1.00 | 0.56 | 0.44 | **+1.83** |
| EURJPY·breakout·C0·HIGH·LONG·NORMAL | 1,388 | +3.17 [+0.7,+5.7] | +2.5 | 0.99 | 1.00 | 0.78 | 0.58 | **+1.82** |
| EURJPY·mean_reversion·C3·HIGH·SHORT·NORMAL | 1,122 | +3.59 [-0.3,+7.5] | +1.8 | 0.93 | 1.00 | 0.61 | 0.53 | **+1.76** |

## Bottom 25 configurations kwa **CCS** — **'WAPI USIFANYE TRADE'** (F-022: persistent negatives)

| Configuration | N | EV [95% CI] | t | conf | persist | stab | sampleQ | CCS |
|---------------|---|-------------|---|------|---------|------|---------|-----|
| EURJPY·trend_continuation·C3·HIGH·LONG·WIDE | 1,038 | -14.32 [-20.6,-8.1] | -4.5 | 1.00 | 0.80 | 0.26 | 0.51 | **-5.83** |
| EURJPY·trend_continuation·C3·HIGH·SHORT·NORMAL | 2,573 | -8.02 [-11.2,-4.9] | -5.0 | 1.00 | 0.80 | 0.26 | 0.72 | **-4.62** |
| EURJPY·trend_continuation·C1·HIGH·SHORT·WIDE | 847 | -9.73 [-14.3,-5.1] | -4.1 | 1.00 | 1.00 | 0.44 | 0.46 | **-4.46** |
| USDJPY·deep_pullback·C1·LOW·SHORT·NORMAL | 643 | -12.18 [-17.5,-6.8] | -4.5 | 1.00 | 0.80 | 0.29 | 0.39 | **-3.81** |
| USDJPY·mean_reversion·C3·HIGH·LONG·WIDE | 1,020 | -9.30 [-15.4,-3.2] | -3.0 | 1.00 | 0.80 | 0.11 | 0.50 | **-3.75** |
| EURJPY·deep_pullback·C1·HIGH·SHORT·NORMAL | 1,844 | -6.99 [-9.9,-4.1] | -4.7 | 1.00 | 0.80 | 0.30 | 0.65 | **-3.62** |
| USDCAD·trend_continuation·C3·HIGH·LONG·NORMAL | 2,673 | -4.82 [-6.7,-3.0] | -5.1 | 1.00 | 1.00 | 0.55 | 0.73 | **-3.51** |
| EURJPY·breakout·C3·HIGH·LONG·WIDE | 330 | -17.51 [-29.3,-5.7] | -2.9 | 1.00 | 0.80 | 0.02 | 0.25 | **-3.46** |
| USDCAD·trend_continuation·C1·HIGH·LONG·NORMAL | 2,791 | -4.70 [-6.2,-3.2] | -6.1 | 1.00 | 1.00 | 0.65 | 0.74 | **-3.46** |
| GBPUSD·breakout·C0·LOW·SHORT·NORMAL | 1,644 | -5.48 [-7.8,-3.1] | -4.5 | 1.00 | 1.00 | 0.68 | 0.62 | **-3.41** |
| USDCHF·mean_reversion·C3·HIGH·LONG·NORMAL | 1,724 | -5.35 [-7.4,-3.3] | -5.2 | 1.00 | 1.00 | 0.70 | 0.63 | **-3.38** |
| USDCAD·trend_continuation·C0·NORMAL·LONG·WIDE | 1,482 | -5.55 [-7.5,-3.6] | -5.5 | 1.00 | 1.00 | 0.46 | 0.60 | **-3.31** |
| USDCHF·trend_continuation·C1·HIGH·SHORT·WIDE | 1,075 | -6.38 [-8.8,-4.0] | -5.2 | 1.00 | 1.00 | 0.54 | 0.52 | **-3.30** |
| EURJPY·mean_reversion·C0·LOW·SHORT·NORMAL | 4,911 | -4.76 [-6.2,-3.3] | -6.5 | 1.00 | 0.80 | 0.31 | 0.83 | **-3.16** |
| EURJPY·breakout·C1·HIGH·LONG·WIDE | 119 | -37.04 [-57.8,-16.3] | -3.5 | 1.00 | 0.80 | 0.12 | 0.11 | **-3.15** |
| EURJPY·trend_continuation·C3·HIGH·SHORT·WIDE | 1,526 | -8.47 [-13.1,-3.8] | -3.6 | 1.00 | 0.60 | 0.03 | 0.60 | **-3.07** |
| USDCAD·trend_continuation·C0·NORMAL·SHORT·NORMAL | 8,560 | -3.43 [-4.3,-2.6] | -8.1 | 1.00 | 1.00 | 0.81 | 0.90 | **-3.07** |
| USDJPY·trend_continuation·C1·LOW·SHORT·NORMAL | 1,093 | -7.25 [-11.5,-3.0] | -3.4 | 1.00 | 0.80 | 0.24 | 0.52 | **-3.03** |
| GBPUSD·mean_reversion·C3·HIGH·LONG·WIDE | 907 | -7.04 [-15.4,+1.3] | -1.6 | 0.90 | 1.00 | 0.46 | 0.48 | **-3.01** |
| USDCAD·breakout·C3·HIGH·LONG·NORMAL | 1,082 | -5.76 [-8.6,-3.0] | -4.0 | 1.00 | 1.00 | 0.54 | 0.52 | **-2.99** |
| USDJPY·deep_pullback·C3·NORMAL·LONG·NORMAL | 658 | -7.56 [-13.4,-1.7] | -2.5 | 0.99 | 1.00 | 0.53 | 0.40 | **-2.97** |
| GBPUSD·mean_reversion·C3·HIGH·SHORT·NORMAL | 1,370 | -5.08 [-8.9,-1.2] | -2.6 | 0.99 | 1.00 | 0.77 | 0.58 | **-2.91** |
| EURJPY·trend_continuation·C3·HIGH·LONG·NORMAL | 1,961 | -4.39 [-7.3,-1.5] | -2.9 | 1.00 | 1.00 | 0.52 | 0.66 | **-2.90** |
| EURJPY·trend_continuation·C1·HIGH·LONG·WIDE | 899 | -7.68 [-13.7,-1.6] | -2.5 | 0.99 | 0.80 | 0.38 | 0.47 | **-2.87** |
| USDCAD·deep_pullback·C1·HIGH·LONG·NORMAL | 1,539 | -4.61 [-6.6,-2.6] | -4.4 | 1.00 | 1.00 | 0.69 | 0.61 | **-2.79** |

## Principle 24 / F-024 — je Confidence inabadilisha ranking? (EV peke yake vs CCS)

- Spearman ρ kati ya EV-ranking na CCS-ranking = **+0.91** (rankings zinatofautiana).
- Top-25: EV-alone na CCS zinashiriki **10/25** tu — **15** configurations zenye EV juu ZIMESHUSHWA na CCS (confidence/sample ndogo).

**Mifano: EV juu lakini CCS imeshusha (kwa nini ranking ya EV peke yake ni hatari):**

| Configuration | N | EV | conf | persist | sampleQ | CCS |
|---------------|---|----|------|---------|---------|-----|
| GBPUSD·pullback·C3·NORMAL·SHORT·WIDE | 135 | +14.71 | 1.00 | 1.00 | 0.12 | +1.75 |
| EURJPY·deep_pullback·C3·NORMAL·LONG·WIDE | 163 | +14.16 | 0.98 | 0.80 | 0.14 | +1.55 |
| GBPUSD·trend_continuation·C1·LOW·SHORT·WIDE | 228 | +13.63 | 0.99 | 0.60 | 0.19 | +1.50 |
| USDJPY·breakout·C3·NORMAL·LONG·WIDE | 129 | +12.23 | 0.99 | 0.80 | 0.11 | +1.10 |
| EURUSD·pullback·C1·LOW·SHORT·WIDE | 104 | +10.82 | 0.96 | 0.80 | 0.09 | +0.79 |
| GBPUSD·trend_continuation·C1·LOW·LONG·WIDE | 174 | +10.37 | 1.00 | 0.60 | 0.15 | +0.92 |

→ ✅ **F-024 inaungwa mkono**: Configuration zenye EV kubwa lakini N ndogo / confidence ndogo / persistence ndogo zinashuka kwenye CCS. Expected Payoff PEKE YAKE inadanganya — Confidence ina thamani sawa (Principle 24).

## F-022 (APPROVED) — negative persistence > positive (walk-forward 70/30)

- train-positive → test-positive: **42%** (N configs = 494)
- train-negative → test-negative: **66%** (N configs = 998)

→ ✅ **F-022 imethibitishwa tena**: edge mbaya inaendelea (persist) zaidi kuliko nzuri. 'Trade less, but in the right environment' — jua WAPI USIFANYE trade kwanza.

## VERDICT — Phase 7 Confidence Engine

→ Kati ya 1,492 configurations, **467** zina CCS>0 (edge + ushahidi). CCS inachanganya EV, confidence (t/CI), walk-forward persistence, na sample quality kuwa kipimo kimoja cha kuaminika. Hii ndiyo entity ambayo **Opportunity Engine itafanya RANKING** (Principle 23 — rank Configurations, sio classify Trades). Acceptance: Opportunity Engine itapokea CCS, sio EV peke yake.

*CCS = EV × Confidence × Persistence × SampleQuality (concept ya Chief; multipliers ∈[0,1], no-lookahead K-fold). Principle 24: hakuna ranking kwa EV peke yake. F-024: confidence = thamani sawa na payoff. F-023: ranking, sio classification. F-022: negative edge persistent zaidi. CCS = target ya baadaye ya ML (Configuration Score). Research Foundation imefungwa. Profitable ≠ Tradable Edge.*