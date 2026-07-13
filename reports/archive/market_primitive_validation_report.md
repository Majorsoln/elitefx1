# Market Primitive Validation — primitive ni mechanism au description? (Phase 24)

*2026-06-30 19:37 | 9 pairs, 1,020,735 bars (EVENT-FREE) | k=5 primitives (robust norm + kmeans, GLOBAL) | precedence window 5 | NO ML*

> **Principle 51 (Chief):** andika market knowledge kwa **reusable market primitives**, sio event labels. **Principle 52:** semantics ihifadhi concepts, sio kurudia clustering kikamilifu. **F-041 (OPEN):** seti ndogo ya universal market primitives inaweza kuwepo (candidate: Compression). Swali: primitive ni mechanism au description (cause au consequence)? NO ML.

## Q4+Q5 — Primitives zilizojengwa BILA event labels (+ je zinaongea lugha ya soko?)

| primitive | N | label (market language) | vol | act | spr | traj | distinct | concrete? |
|-----------|---|-------------------------|-----|-----|-----|------|----------|-----------|
| Pr4 | 458,531 | **Equilibrium / Balanced Flow** | 0.94 | 0.96 | 0.18 | -0.02 | 0.79 | — |
| Pr0 | 296,375 | **Mature Persistence** | 0.83 | 0.90 | 0.16 | +0.00 | 1.08 | ✅ |
| Pr2 | 218,886 | **Equilibrium / Balanced Flow** | 1.35 | 1.19 | 0.19 | +0.03 | 0.67 | — |
| Pr3 | 41,098 | **Equilibrium / Balanced Flow** | 1.37 | 1.25 | 0.26 | +0.01 | 2.85 | — |
| Pr1 | 5,845 | **Equilibrium / Balanced Flow** | 1.28 | 1.16 | 0.24 | -0.01 | 7.24 | — |

- **Q4:** primitives zimejengwa kutoka bar-stream PEKEE (hakuna event label iliyotumika) → ⚠️ hakuna primitive iliyopata label Compression (fallback = vol ya chini zaidi).
- **Q5:** primitives concrete (market label + distinct): **1/5** → ⚠️ nyingi ni majina tu kwenye clusters.

## Q2 — Je Mature Persistence (Pr0) inatokea KABLA ya events? (precedence)

*baseline P(primitive) = 0.290. lift>1 = primitive inatangulia event.*

| event | P(pre-window) | lift | N events |
|-------|---------------|------|----------|
| pullback | 0.284 | 0.98 | 351,141 |
| deep_pullback | 0.284 | 0.98 | 351,141 |
| trend_continuation | 0.294 | 1.01 | 774,502 |
| breakout | 0.306 | 1.05 | 166,408 |
| mean_reversion | 0.300 | 1.03 | 361,083 |

→ ⚠️ Compression haitangulii events kwa uthabiti — bado inaweza kuwa description/coincident.

## Q3 — Je primitive ina transitions zake? (Compression → Expansion → …)

| from \ to | Pr0 | Pr1 | Pr2 | Pr3 | Pr4 |
|---|---|---|---|---|---|
| **Pr0** (Mature Persistence) | 0.00 | 0.00 | 0.26 | 0.00 | 0.74 |
| **Pr1** (Equilibrium / Bala) | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 |
| **Pr2** (Equilibrium / Bala) | 0.37 | 0.00 | 0.00 | 0.13 | 0.50 |
| **Pr3** (Equilibrium / Bala) | 0.00 | 0.12 | 0.88 | 0.00 | 0.00 |
| **Pr4** (Equilibrium / Bala) | 0.61 | 0.00 | 0.39 | 0.00 | 0.00 |

- transition kubwa kutoka **Mature Persistence**: → **Equilibrium / Balanced Flow** (P=0.74).

## VERDICT — Phase 24 Market Primitive Validation

→ ⚠️ **primitive layer bado haijathibitika**: Q4 ❌ (no Compression emerged event-free), Q5 concrete 1/5. F-041 haijaungwa mkono kikamilifu; inahitaji representation/k bora.

**Bado Market Understanding Era — NO alpha.** Hatujui kama Compression ni *cause* au *consequence*; precedence (Q2) ni dalili, sio uthibitisho wa causality.

## Honest Caveats

1. **Primitives hutumia representation COARSE (global robust+kmeans), sio manifold ya event-specific (F-039).** Hii ni kwa makusudi (primitives = global market conditions) lakini ina maana primitive geometry si ile ile iliyo-operationalized Phase 21.
2. **Precedence (Q2) ≠ causality.** Lift>1 inaonyesha Compression hutangulia events, lakini non-stationarity / autocorrelation / overlap ya windows zinaweza kuunda lift bandia. Hakuna permutation/Granger test hapa — ni dalili, sio cause-vs-consequence proof.
3. **k=5 primitives ni human choice.** Idadi ya primitives na fallback (vol ya chini = Compression) zinaweza kubadili matokeo; primitive vocabulary bado haijawa canonical (Principle 49 bado).
4. **Primitive ≠ edge (Principle 40/48).** Hata kama Compression ni mechanism, haina alpha yenyewe; hii ni market structure, sio faida.
5. **'Event-free' si kweli kabisa** — bars zinatoka state engine ile ile; events na primitives zinashiriki features (vol/act/spr…), kwa hiyo overlap ya information inategemewa, sio independence.

*Event-free bar stream → robust norm + kmeans primitives → semantic_label naming; precedence lift; bar→bar transition matrix. Principle 51/52. F-041 OPEN. NO ML. Profitable ≠ Tradable Edge.*