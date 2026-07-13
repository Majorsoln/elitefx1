# Semantic Taxonomy — clusters zinamaanisha nini kwa lugha ya soko? (Phase 22)

*2026-06-30 18:52 | robust norm + self-tuning spectral (Phase 21 repr) | k=3/event | deterministic profile→market-language map | NO ML*

> **Principle 46 (Chief):** taxonomy haijakamilika hadi latent states zitafsirike kisemantiki. **Principle 47:** andika clusters kwa lugha ya soko, sio ID. **F-039 (APPROVED):** events tofauti geometry tofauti. Discovery inabaki unsupervised; semantics ni tafsiri JUU ya clusters (post-hoc), sio human theory inayosukuma clustering. NO ML.

## Q1+Q2+Q3 — kila cluster kwa lugha ya soko (interpretation + communicability)

| event | cluster | N | semantic label (market language) | profile | distinct | interpretable? |
|-------|---------|---|----------------------------------|---------|----------|----------------|
| pullback | C0 | 78 | **Compression (Quiet Coil)** | vol=chini, activity=chini, spread=tight, trajectory=tuli, age=iliyokomaa | 1.29 | ✅ |
| pullback | C1 | 1,355 | **Equilibrium / Balanced Flow** | vol=wastani, activity=wastani, spread=tight, trajectory=tuli, age=wastani | 0.19 | — |
| pullback | C2 | 67 | **High-Volatility Regime** | vol=juu, activity=juu, spread=tight, trajectory=tuli, age=iliyokomaa | 1.30 | ✅ |
| deep_pullback | C0 | 73 | **Compression (Quiet Coil)** | vol=chini, activity=chini, spread=tight, trajectory=tuli, age=iliyokomaa | 1.23 | ✅ |
| deep_pullback | C1 | 1,360 | **Equilibrium / Balanced Flow** | vol=wastani, activity=wastani, spread=tight, trajectory=tuli, age=wastani | 0.21 | — |
| deep_pullback | C2 | 67 | **High-Volatility Regime** | vol=juu, activity=juu, spread=tight, trajectory=tuli, age=iliyokomaa | 1.27 | ✅ |
| trend_continuation | C0 | 1,126 | **Equilibrium / Balanced Flow** | vol=wastani, activity=wastani, spread=tight, trajectory=tuli, age=wastani | 0.31 | — |
| trend_continuation | C1 | 97 | **Compression (Quiet Coil)** | vol=chini, activity=chini, spread=tight, trajectory=tuli, age=iliyokomaa | 1.30 | ✅ |
| trend_continuation | C2 | 277 | **Equilibrium / Balanced Flow** | vol=wastani, activity=wastani, spread=tight, trajectory=tuli, age=wastani | 1.45 | ✅ |
| breakout | C0 | 65 | **High-Volatility Regime** | vol=juu, activity=juu, spread=tight, trajectory=tuli, age=iliyokomaa | 1.32 | ✅ |
| breakout | C1 | 1,358 | **Equilibrium / Balanced Flow** | vol=wastani, activity=wastani, spread=tight, trajectory=tuli, age=wastani | 0.19 | — |
| breakout | C2 | 77 | **Compression (Quiet Coil)** | vol=chini, activity=chini, spread=tight, trajectory=tuli, age=iliyokomaa | 1.54 | ✅ |
| mean_reversion | C0 | 58 | **Compression (Quiet Coil)** | vol=chini, activity=chini, spread=tight, trajectory=tuli, age=iliyokomaa | 1.38 | ✅ |
| mean_reversion | C1 | 84 | **High-Volatility Regime** | vol=juu, activity=juu, spread=tight, trajectory=tuli, age=iliyokomaa | 1.26 | ✅ |
| mean_reversion | C2 | 1,358 | **Equilibrium / Balanced Flow** | vol=wastani, activity=wastani, spread=tight, trajectory=tuli, age=wastani | 0.19 | — |

- **Q2 interpretable** (distinct ≥ 0.5): **10/15** (67%)
- **Q3 communicable bila ID** (concrete market label, sio 'Equilibrium / Balanced Flow'): **9/15** (60%)

## Q4 — Je semantic labels zina-repeat kwenye pairs? (transferable vocabulary)

- pairs zilizochambuliwa: **9**
- labels zinazojitokeza kwenye ≥2 pairs: **3** (Compression (Quiet Coil), Equilibrium / Balanced Flow, High-Volatility Regime)
- labels za pair-moja tu: ['Low-Volatility Drift']

→ ✅ vocabulary INA-transfer (concepts zinarudi kwenye pairs nyingi).

## Q5 — Je semantic labels zina predictive value (vs cluster IDs)?

| grouping | #groups | R²(outcome) |
|----------|---------|-------------|
| cluster IDs (event×cluster) | 15 | 0.0024 |
| semantic labels (market concepts) | 3 | 0.0000 |

- ratio R²(label)/R²(id) = **0.01** kwa **groups 3 vs 15** (12 chache).

→ ⚠️ semantic labels zinapoteza predictive value sana (cluster IDs zina info ambayo label haiishiki).

## VERDICT — Phase 22 Semantic Taxonomy

→ ⚠️ **taxonomy BADO haijatafsirika kikamilifu**: labels zinapoteza predictive value. Semantics inahitaji kazi zaidi (vocabulary/rules bora) kabla ya Reality Validation. Principle 46 bado.

**Bado tuko 'Market Understanding Era' — SIO Alpha Era.** Edge haijathibitishwa; semantics ni hatua ya kuelewa soko, sio alpha.

## Honest Caveats

1. **Semantic labels ≠ edge (Principle 40/46).** Hii inathibitisha clusters zinatafsirika kwa lugha ya soko — **haionyeshi alpha.** Tafsiri nzuri sio faida.
2. **Label-map ni deterministic rule, sio discovery.** Tunazuia human theory isisukume clustering (clustering ni unsupervised); lakini RAMANI ya profile→lugha ina human choice ya thresholds (ZTHR=0.5, traj±0.15). Mabadiliko ya thresholds yanaweza kubadili labels — sio canonical.
3. **R²(outcome) sio edge.** Q5 inapima variance-explained ya net return kwa grouping, sio EV baada ya gharama wala OOS. Groups chache zenye R² sawa = generalization bora, sio profit.
4. **'Interpretable' ni profile-distinctiveness, sio uthibitisho kwamba dhana ya soko ni sahihi.** Cluster yenye vol juu + traj inashuka tunaiita 'Momentum Exhaustion' — ni hypothesis ya kiisimu, haijathibitishwa kuwa ndiyo mechanism halisi ya soko.
5. **Q4 cross-pair overlap = vocabulary sawa, sio kwamba cluster ni SAME object cross-pair.** Label ile ile kwenye pairs mbili haimaanishi geometry/edge sawa (F-039: geometry ni event-specific).

*Robust norm + self-tuning spectral (Phase 21 repr) -> kmeans -> deterministic profile→market language. Discovery=unsupervised; semantics=post-hoc layer. Principle 46/47. NO ML. Profitable ≠ Tradable Edge.*