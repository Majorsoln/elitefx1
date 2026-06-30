# Representation Geometry Audit — je feature space inaruhusu taxonomy? (Phase 20)

*2026-06-30 09:40 | silhouette / Davies–Bouldin / Calinski–Harabasz | normalization (z/robust/pct) | manifold (Laplacian eigenmaps) | cross-algo ARI | NO ML*

> **Principle 42 (Chief):** robust clustering inahitaji robust REPRESENTATION kabla ya robust algorithms. **Principle 41:** internal stability ≠ external validity. **Principle 43:** algorithm disagreement -> audit representation, sio kukataa ontology. 'Algorithm haiwezi kuokoa representation mbaya.' Tunakagua kama coordinates zetu zinaficha structure.


## Q1 — Separability ya feature space (standardized, k=3)

| event | silhouette | sil(null) | Davies–Bouldin↓ | Calinski–Harabasz↑ | separable? |
|-------|-----------|-----------|-----------------|---------------------|------------|
| pullback | 0.220 | 0.149 | 1.71 | 72608 | — |
| deep_pullback | 0.214 | 0.184 | 1.71 | 72608 | — |
| trend_continuation | 0.220 | 0.282 | 1.65 | 175014 | — |
| breakout | 0.232 | 0.167 | 1.62 | 45423 | — |
| mean_reversion | 0.218 | 0.166 | 1.67 | 82651 | — |

*(silhouette >0.25 & > null = separable; DB chini bora; CH juu bora. Phase 19: agreement dhaifu — Q1 inaonyesha kama ni kwa sababu feature space haina separability.)*

## Q2 — Je normalization inaficha structure? (silhouette kwa z/robust/percentile)

| event | z-score | robust(MAD) | percentile | bora |
|-------|---------|-------------|------------|------|
| pullback | 0.210 | 0.354 | 0.171 | robust |
| deep_pullback | 0.228 | 0.336 | 0.185 | robust |
| trend_continuation | 0.230 | 0.346 | 0.174 | robust |
| breakout | 0.247 | 0.334 | 0.193 | robust |
| mean_reversion | 0.222 | 0.323 | 0.186 | robust |

→ tofauti kubwa kati ya normalizations = normalization inaathiri structure (Principle 42).

## Q3 — Je event-specific representations zina geometry tofauti?

- silhouette range kati ya events: **0.214 … 0.232** (spread 0.018)

→ — geometry inafanana (inaunga mkono Event Representation Family — kila event geometry yake).

## Q4+Q5 — Manifold vs coordinates; je representation inaongeza algorithm agreement?

| event | ARI(z) | ARI(robust) | ARI(pct) | ARI(manifold) | sil(coord) | sil(manifold) | rep inasaidia? |
|-------|--------|-------------|----------|---------------|------------|---------------|----------------|
| pullback | 0.31 | -0.01 | 0.49 | 0.89 | 0.22 | 0.66 | ✅ |
| deep_pullback | 0.01 | -0.01 | 0.41 | 0.99 | 0.21 | 0.79 | ✅ |
| trend_continuation | 0.24 | 0.04 | 0.48 | 0.98 | 0.22 | 0.72 | ✅ |
| breakout | 0.23 | -0.01 | 0.62 | 0.45 | 0.23 | 0.62 | ✅ |
| mean_reversion | 0.26 | -0.00 | 0.57 | 0.93 | 0.22 | 0.58 | ✅ |

→ events ambapo representation mbadala/manifold inaongeza agreement au separability: **5/5**.

## VERDICT — Phase 20 Representation Geometry

→ representation/geometry **INAATHIRI** matokeo: events 0/5 zina separability ya feature space; representation mbadala (robust/percentile/manifold) iliongeza agreement kwa 5/5. Hii inaunga mkono **Principle 42/43**: tatizo la Phase 19 lilikuwa REPRESENTATION, sio lazima ontology. Inayofuata: jenga representation iliyoboreshwa (manifold/normalization bora) kisha rudia taxonomy + robustness. NO ML bado.

*Geometry: silhouette/DB/CH vs permutation null; normalization (z/robust/pct); Laplacian eigenmaps manifold; cross-algo ARI per representation. Principle 41 (stable≠true), 42 (representation kabla ya clustering), 43 (disagreement → audit representation). NO ML. Profitable ≠ Tradable Edge.*