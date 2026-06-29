# Event Taxonomy — je kila Event ina sub-events? (Phase 18)

*2026-06-29 19:12 | UNSUPERVISED KMeans (numpy) kwenye context features | feature gap vs permutation null + outcome-identity R²(label) perm-controlled | min N=800*

> **F-037 (Chief, OPEN):** events zinaweza kuwa na latent SUB-EVENTS zenye statistical identity tofauti (MR@LowVol ≠ MR@HighVol?). **F-036:** variables ni conditional entities. **Principle 38:** hakuna universal representation — Event Representation Family. Subtype EXISTS ikiwa outcome-identity (payoff) inatofautiana kwa significance. ⚠️ in-sample discovery (OOS = Phase 19, Principle 37). NO ML.


## Q1–Q3 — Je events zina subtypes? (feature-structure + outcome-identity)

| event | N | best k | feature gap | outcome R²(subtype) | perm p | subtypes? |
|-------|---|--------|-------------|---------------------|--------|-----------|
| pullback | 351,042 | 3 | +0.088 | 0.00000 | 0.935 | — |
| deep_pullback | 351,042 | 3 | +0.062 | 0.00000 | 0.613 | — |
| trend_continuation | 774,209 | 4 | +0.110 | 0.00003 | 0.032 | ✅ |
| breakout | 166,324 | 3 | +0.121 | 0.00012 | 0.032 | ✅ |
| mean_reversion | 360,924 | 4 | +0.131 | 0.00003 | 0.097 | — |

→ events zenye sub-events (outcome-identity significant NA feature structure): **trend_continuation, breakout**.

## Q4+Q5 — Representation & alpha kwa subtype (per-subtype centroid + EV)


### trend_continuation (k=4)

| subtype | N | vol | act | spr | atr | traj | age | trans | EV | one-sided p | edge? |
|---------|---|---|---|---|---|---|---|---|----|----|----|
| S0 | 69,365 | 1.0 | 1.1 | 0.2 | 20.6 | 0.1 | 1.0 | 1.0 | -1.46 | 1.000 | — |
| S1 | 313,389 | 0.4 | 0.6 | 0.0 | 17.1 | -0.1 | 16.0 | 0.0 | -1.03 | 1.000 | — |
| S2 | 265,461 | 1.7 | 1.4 | 0.0 | 25.2 | 0.1 | 16.8 | 0.0 | -1.44 | 1.000 | — |
| S3 | 125,994 | 1.2 | 1.2 | 1.0 | 22.7 | 0.0 | 16.7 | 0.0 | -1.57 | 1.000 | — |

*trend_continuation whole-event EV = -1.30. Centroid tofauti kati ya subtypes = representation inabadilika kwa subtype (Q4). Subtype yenye edge (✅) = alpha iko kwenye SUB-event, sio event nzima (Q5).*

### breakout (k=3)

| subtype | N | vol | act | spr | atr | traj | age | trans | EV | one-sided p | edge? |
|---------|---|---|---|---|---|---|---|---|----|----|----|
| S0 | 60,560 | 1.7 | 1.7 | 0.3 | 25.9 | -0.0 | 18.8 | 0.0 | -2.47 | 1.000 | — |
| S1 | 30,721 | 1.5 | 1.5 | 0.2 | 21.5 | 0.8 | 1.5 | 0.6 | -1.11 | 1.000 | — |
| S2 | 75,043 | 0.4 | 0.7 | 0.1 | 17.9 | -0.1 | 16.8 | 0.0 | -1.68 | 1.000 | — |

*breakout whole-event EV = -1.86. Centroid tofauti kati ya subtypes = representation inabadilika kwa subtype (Q4). Subtype yenye edge (✅) = alpha iko kwenye SUB-event, sio event nzima (Q5).*

## VERDICT — Phase 18 Event Taxonomy

→ ✅ **F-037 inaungwa mkono (in-sample)**: events **trend_continuation, breakout** zina sub-events zenye statistical identity tofauti (outcome-identity significant + feature structure). Sub-events zenye edge (in-sample, p<0.05, EV>0): **0/17** — alpha inaweza kuwa kwenye SUB-event, sio event nzima (Q5). Representation inabadilika kwa subtype (Q4). ⚠️ in-sample discovery — hatua inayofuata: Event-Subtype Confirmation (OOS + FDR, Principle 37). Architecture V6: Event Detection → **Event Taxonomy** → Event-Specific Representation. NO ML.

*Event Taxonomy: UNSUPERVISED KMeans kwenye context features; feature gap vs permutation null + outcome-identity R²(label) perm-controlled; per-subtype centroid (Q4) + EV/p (Q5). F-037: events zina latent sub-events. Principle 38: Event Representation Family. ⚠️ in-sample (OOS=Phase 19). NO ML. Profitable ≠ Tradable Edge.*