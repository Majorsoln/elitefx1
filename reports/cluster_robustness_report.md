# Cluster Robustness — je latent structures ni algorithm-independent? (Phase 5.11)

*2026-06-26 16:34 | methods: KMeans, GMM, Agglomerative | k=4 | agreement = Adjusted Rand Index (ARI) | subsample N=800 | features: vol_z, vol_slope, act_z, act_slope, spr_z, transition, lifecycle*

> **Principle 18 (Chief):** No market state accepted unless algorithm-independent. KMeans inadhani spherical clusters; markets si spherical. Makundi yale yale yakijitokeza kwa GMM na Agglomerative -> ROBUST. ARI ya juu = makubaliano. NO sklearn, NO ML.

## Cluster size (% per method)

| method | C0 | C1 | C2 | C3 |
|--------|----|----|----|----|
| KMeans | 22% | 17% | 59% | 2% |
| GMM | 40% | 7% | 20% | 34% |
| Agglomerative | 98% | 0% | 0% | 1% |

## Agreement — Adjusted Rand Index (ARI) kati ya mbinu

| pair | ARI |
|------|-----|
| KMeans ↔ GMM | +0.32 |
| KMeans ↔ Agglomerative | +0.04 |
| GMM ↔ Agglomerative | +0.01 |

## VERDICT — Principle 18: latent structures ni robust?

- mean ARI kuvuka mbinu = **+0.12**

→ ⚠️ **HAZIJA-ROBUST vya kutosha** (ARI +0.12 < 0.5): clusters zinategemea algorithm. Kabla ya kukubali kama market states, inahitaji representation/feature bora au non-spherical method (HDBSCAN). Principle 18 haijatimizwa bado.

*ARI: +1 = makubaliano kamili, 0 = bahati. Robust ikiwa mbinu tofauti (spherical/elliptical/hierarchical) zinatoa makundi yale yale. Principle 18. DBSCAN/HDBSCAN (density) inaweza kuongezwa baadaye (inahitaji density tuning). NO ML supervised. Inayofuata: Latent State Validation (5.12) -> Configuration Engine.*