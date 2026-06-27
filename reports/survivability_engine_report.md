# Survivability Engine — je edge inadumu? (Phase 9)

*2026-06-27 19:17 | rolling walk-forward 6 windows (kwa muda, sio 70/30) | survivability = sehemu ya windows zenye EV>0 | min N=200 | configs: 1,271*

> **Lengo (Chief):** Phase 8 ilikataa hypothesis (CCS-selection haitoi portfolio chanya OOS). Dimension mpya: **Opportunity = Quality × Availability × Survivability**. **Principle 26:** kazi ya kwanza ya Opportunity Engine ni KULINDA MTAJI (ondoa mabaya), sio kutafuta alpha. **F-022 (Core Principle):** edge mbaya inadumu zaidi ya nzuri. **F-027 (OPEN):** survivability ni dimension HURU kutoka quality. NO ML bado. Profitable ≠ Tradable Edge.


## F-027 — Je Survivability ni HURU kutoka Quality? (corr ndogo = huru)

- Spearman(survivability, EV) = **+0.74**
- Spearman(survivability, CCS) = **+0.79**

→ ⚠️ F-027 haijaungwa mkono kikamilifu: survivability ina uhusiano na quality (EV/CCS) — huenda si huru kabisa.

## Q1 — Configurations zinazodumu zaidi (rolling 6 windows)

| Configuration | N | overall EV | CCS | surv-rate | survival (win) | last-win EV | decay/win |
|---------------|---|-----------|-----|-----------|----------------|-------------|-----------|
| EURJPY·mean_reversion·C1·HIGH·SHORT·WIDE | 342 | +21.42 | +5.46 | 100% | 6/6 | +20.02 | -1.12 |
| EURJPY·mean_reversion·C1·HIGH·LONG·WIDE | 277 | +13.12 | +2.28 | 100% | 6/6 | +22.73 | +0.78 |
| USDJPY·pullback·C1·LOW·LONG·NORMAL | 643 | +10.75 | +3.36 | 100% | 6/6 | +3.12 | +1.30 |
| GBPUSD·trend_continuation·C3·LOW·SHORT·WIDE | 240 | +10.13 | +1.96 | 100% | 6/6 | +13.84 | +2.47 |
| EURJPY·mean_reversion·C0·HIGH·LONG·WIDE | 390 | +8.70 | +2.44 | 100% | 6/6 | +2.62 | -1.84 |
| EURJPY·deep_pullback·C3·NORMAL·SHORT·NORMAL | 538 | +5.47 | +1.40 | 100% | 6/6 | +9.88 | -0.07 |
| AUDUSD·deep_pullback·C3·LOW·LONG·NORMAL | 418 | +4.82 | +1.41 | 100% | 6/6 | +3.56 | +0.36 |
| EURUSD·trend_continuation·C1·LOW·LONG·NORMAL | 1,272 | +3.62 | +2.03 | 100% | 6/6 | +6.56 | +0.38 |
| USDCAD·mean_reversion·C0·HIGH·LONG·WIDE | 363 | +3.51 | +0.50 | 100% | 6/6 | +5.57 | +0.11 |
| EURJPY·mean_reversion·C3·HIGH·SHORT·WIDE | 557 | +17.64 | +5.05 | 83% | 5/6 | -7.38 | -7.48 |
| EURJPY·trend_continuation·C3·LOW·LONG·WIDE | 215 | +7.44 | +0.76 | 83% | 1/6 | +0.07 | +2.38 |
| GBPUSD·trend_continuation·C3·NORMAL·SHORT·WIDE | 393 | +7.06 | +1.59 | 83% | 5/6 | -2.04 | -2.40 |
| USDJPY·pullback·C3·NORMAL·SHORT·NORMAL | 658 | +6.36 | +2.44 | 83% | 2/6 | +2.18 | -1.00 |
| GBPUSD·deep_pullback·C1·HIGH·SHORT·WIDE | 556 | +6.02 | +1.17 | 83% | 4/6 | +2.44 | -5.21 |
| EURJPY·mean_reversion·C3·HIGH·LONG·WIDE | 804 | +5.86 | +1.92 | 83% | 4/6 | +0.05 | -2.64 |
| GBPUSD·mean_reversion·C1·HIGH·SHORT·WIDE | 345 | +5.67 | +0.49 | 83% | 2/6 | +0.72 | -2.62 |
| USDJPY·trend_continuation·C1·LOW·LONG·NORMAL | 2,061 | +5.63 | +3.03 | 83% | 2/6 | +4.11 | -0.54 |
| USDCHF·mean_reversion·C1·HIGH·LONG·WIDE | 398 | +4.87 | +1.09 | 83% | 4/6 | +1.85 | -1.76 |
| NZDUSD·mean_reversion·C3·NORMAL·SHORT·WIDE | 214 | +4.71 | +0.63 | 83% | 2/6 | +4.57 | +0.76 |
| USDJPY·mean_reversion·C1·HIGH·LONG·WIDE | 285 | +4.65 | +0.54 | 83% | 4/6 | +18.41 | -1.75 |
| EURUSD·mean_reversion·C1·HIGH·LONG·WIDE | 239 | +4.55 | +0.64 | 83% | 0/6 | +12.08 | +2.73 |
| EURJPY·deep_pullback·C1·HIGH·LONG·WIDE | 457 | +4.53 | +1.01 | 83% | 4/6 | +2.60 | -1.06 |
| USDCAD·mean_reversion·C3·HIGH·LONG·WIDE | 542 | +4.42 | +1.42 | 83% | 4/6 | +3.31 | -1.44 |
| USDCAD·deep_pullback·C3·LOW·SHORT·NORMAL | 345 | +4.41 | +0.79 | 83% | 1/6 | +8.96 | -0.83 |
| EURUSD·mean_reversion·C1·LOW·LONG·NORMAL | 397 | +4.18 | +0.46 | 83% | 2/6 | +9.92 | +2.19 |

## Q2 — Median survival time ya edge

- Configs zilizoanza chanya (window 1 EV>0): **519/1271**
- **Median survival = 1.0/6 windows** (≈ 229 trades)
- Configs zilizodumu windows ZOTE (6/6): **9/519** (2% ya zilizoanza chanya)

## Q3 — Edge decay inaanza lini? (wastani wa EV kwa window index)

| window | mean EV (configs zote) | mean EV (zilizoanza chanya) | trades-hadi-hapa (wastani) |
|--------|------------------------|----------------------------|----------------------------|
| 1 | -1.084 | +4.626 | 247 |
| 2 | -0.872 | -0.637 | 493 |
| 3 | -0.817 | +0.326 | 740 |
| 4 | -1.176 | -0.722 | 986 |
| 5 | -0.967 | -1.200 | 1,233 |
| 6 | -1.115 | -0.947 | 1,479 |

→ wastani wa decay slope (configs zilizoanza chanya) = **-0.874 pips/window** (edge inafifia kwa muda).

## Q4 — Je survivability inatabirika? (mean surv-rate kwa dimension)

- **event** (spread 15pp): mean_reversion=50% · deep_pullback=41% · pullback=40% · trend_continuation=35% · breakout=35%
- **regime** (spread 4pp): HIGH=42% · LOW=41% · NORMAL=38%
- **latent** (spread 4pp): C3=43% · C1=41% · C0=39%
- **direction** (spread 2pp): LONG=41% · SHORT=40%
- **exec** (spread 4pp): WIDE=43% · NORMAL=39%

→ dimension zenye spread kubwa zinatabiri survivability vizuri zaidi (state/regime/event/context huamua kama edge itadumu).

## Q5 — High survivability, EV ya wastani (workhorses za portfolio ya muda mrefu)

*surv-rate ≥ Q3 (50%) NA 0 < EV ≤ median (-1.10); zinapatikana: 0*

→ hakuna config inayolingana (survivability ya juu inaambatana na EV ya juu hapa).

## VERDICT — Phase 9 Survivability Engine

→ Survivability ni dimension inayohusiana kiasi (ρ_EV +0.74, ρ_CCS +0.79). Median edge survival = 1.0/6 windows. Hii inathibitisha mwelekeo wa Chief: Opportunity Engine lazima ijenge juu ya **Survivability** (na Principle 26 — ondoa mabaya kwanza), sio CCS pekee. Inayofuata: Opportunity Engine iliyojengwa upya (remove-bad → rank survivable → allocate). NO ML bado.

*Survivability = sehemu ya rolling windows zenye EV>0 (durability ya muda, sio split moja). F-027: corr(survivability, quality) ndogo = dimension huru. Q2 median survival, Q3 decay onset, Q4 predictability kwa dimension, Q5 durable-modest workhorses. Opportunity = Quality × Availability × Survivability (Principle 25 enhanced). Principle 26: linda mtaji kwanza. NO ML. Profitable ≠ Tradable Edge.*