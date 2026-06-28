# Event Reality Framework — ni events zipi zipo KWELI kitakwimu? (Phase 12)

*2026-06-28 15:07 | null (random-direction) + bootstrap + permutation (300 reps) + Bayesian | outcome forward 6b net spread | min N=300*

> **Principle 29 (Chief):** kila Event ni STATISTICAL HYPOTHESIS, sio trading signal. Tunajenga Opportunity juu ya events zilizothibitishwa tu. **F-029 (APPROVED):** edge decay = market non-stationarity. Chief amekataa mean_reversion-only (subgroup/multiple-comparisons). Hapa events ZOTE kwa methodology ileile. Null = random direction (skill ya mwelekeo net ya spread). Bayesian P(edge>0)=Φ(EV/SE). NO ML. Profitable ≠ Tradable Edge.


## Q1+Q2 — kila event: null + bootstrap + permutation + Bayesian P(edge exists)

| event | N | EV [95% CI boot] | null EV (rand-dir) | perm p | Bayesian P(edge>0) | proven? |
|-------|---|------------------|--------------------|--------|--------------------|---------|
| pullback | 351,042 | -1.212 [-1.35,-1.07] | -1.017 | 0.997 | 0% | — |
| deep_pullback | 351,042 | -0.810 [-0.94,-0.66] | -1.016 | 0.007 | 0% | — |
| trend_continuation | 774,209 | -1.295 [-1.38,-1.21] | -0.973 | 1.000 | 0% | — |
| breakout | 166,324 | -1.864 [-2.07,-1.64] | -0.872 | 1.000 | 0% | — |
| mean_reversion | 360,924 | -0.212 [-0.34,-0.05] | -0.926 | 0.003 | 0% | — |

→ events zilizothibitishwa (Bayesian>95% NA p<0.05 NA CI-low>0): **0/5**.

## Q3 — Je pair fulani inabeba event? (EV + Bayesian kwa pair × event)

- **pullback**: USDJPY=-0.66(P1) · EURGBP=-0.98(P0) · EURUSD=-1.15(P0) · EURJPY=-1.16(P0) · AUDUSD=-1.18(P0) · NZDUSD=-1.29(P0)  →  zilizothibitishwa: hakuna
- **deep_pullback**: EURUSD=+0.37(P97) · USDJPY=-0.44(P5) · GBPUSD=-0.68(P1) · EURJPY=-0.87(P0) · USDCHF=-0.90(P0) · AUDUSD=-1.01(P0)  →  zilizothibitishwa: EURUSD
- **trend_continuation**: USDJPY=+0.22(P87) · GBPUSD=-1.04(P0) · EURUSD=-1.05(P0) · EURJPY=-1.13(P0) · NZDUSD=-1.51(P0) · AUDUSD=-1.69(P0)  →  zilizothibitishwa: hakuna
- **breakout**: USDJPY=-0.01(P49) · EURJPY=-1.57(P0) · USDCHF=-1.57(P0) · EURUSD=-2.08(P0) · NZDUSD=-2.08(P0) · EURGBP=-2.11(P0)  →  zilizothibitishwa: hakuna
- **mean_reversion**: EURUSD=+0.90(P100) · AUDUSD=+0.11(P74) · EURJPY=-0.11(P35) · EURGBP=-0.14(P18) · USDCAD=-0.15(P24) · GBPUSD=-0.36(P11)  →  zilizothibitishwa: EURUSD

*(P = Bayesian P(edge>0)%. Inaonyesha kama event ni ya pair maalum au ya jumla.)*

## Q4 — Je event edge inategemea market state? (EV kwa volatility state)

| event | LOW | NORMAL | HIGH |
|-------|-----|--------|------|
| pullback | -1.11 | -1.00 | -1.41 |
| deep_pullback | -0.97 | -0.94 | -0.62 |
| trend_continuation | -0.96 | -1.68 | -1.23 |
| breakout | -1.32 | -2.21 | -1.96 |
| mean_reversion | -0.68 | +0.20 | -0.14 |

→ EV inayobadilika sana kati ya states = event-edge inategemea market state (state-dependent).

## Q5 — Je events mbili zikichanganywa zinazalisha edge? (combo vs solo)

| combo (A+B, same dir) | N | combo EV | solo A EV | solo B EV | combo > best solo? |
|------------------------|---|----------|-----------|-----------|--------------------|
| breakout+trend_continuation | 164,795 | -1.861 | -1.864 | -1.295 | — |
| pullback+trend_continuation | 139,813 | -1.125 | -1.212 | -1.295 | ✅ |
| deep_pullback+mean_reversion | 78,886 | -0.323 | -0.810 | -0.212 | — |
| breakout+pullback | 23,884 | -1.854 | -1.864 | -1.212 | — |

→ combos zinazozidi best-solo: **1/4** (mwingiliano dhaifu kwa wengi).

## VERDICT — Phase 12 Event Reality Framework

→ ⚠️ **HAKUNA event iliyothibitishwa** kuzidi random-direction kwa triple criterion. Hii inaunga mkono F-029/H0: 'edge' nyingi ni noise / non-stationarity. Opportunity Engine bado imezuiwa (Principle 28). Inahitaji representation/context bora au event mpya.

*Event Reality: null=random-direction (skill ya mwelekeo net ya spread), bootstrap CI, permutation p, Bayesian P(edge>0)=Φ(EV/SE). proven = Bayesian>95% NA p<0.05 NA CI-low>0. Principle 29: event = statistical hypothesis. F-029: decay = non-stationarity. Q3 pair-carrier, Q4 state-dependence, Q5 combos. NO ML. Profitable ≠ Tradable Edge.*