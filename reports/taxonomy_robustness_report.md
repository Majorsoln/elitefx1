# Taxonomy Robustness Audit — je subtypes ni algorithm-independent & stable? (Phase 19)

*2026-06-29 19:35 | KMeans/GMM/Agglomerative ARI+NMI | split-half + bootstrap stability | OOS persistence | k-stability | min N=800*

> **Principle 39 (Chief):** market ontology HAITAINFERWA kutoka clustering algorithm moja. **Principle 40:** valid taxonomy ≠ tradable alpha (Phase 18: 0/17 subtypes zilikuwa na edge). **F-038:** taxonomy ni hierarchical & event-specific. Subtype ni ROBUST ikiwa cross-algo ARI>0.5 NA split-half ARI>0.5 NA OOS-persist (p<0.05). NO ML.


## Q1 — Cross-algorithm agreement (ARI: KMeans/GMM/Agglomerative)

| event | k | ARI(KM,GMM) | ARI(KM,Agg) | ARI(GMM,Agg) | mean ARI | NMI(KM,GMM) | algo-independent? |
|-------|---|-------------|-------------|--------------|----------|-------------|-------------------|
| pullback | 3 | 0.21 | 0.00 | 0.04 | 0.08 | 0.40 | — |
| deep_pullback | 4 | 0.42 | 0.14 | 0.34 | 0.30 | 0.58 | — |
| trend_continuation | 4 | 0.32 | 0.01 | 0.02 | 0.11 | 0.41 | — |
| breakout | 3 | 0.52 | 0.00 | -0.00 | 0.17 | 0.45 | — |
| mean_reversion | 4 | 0.45 | -0.00 | 0.01 | 0.15 | 0.62 | — |

## Q2+Q3 — Stability (split-half ARI; bootstrap centroid ARI)

| event | split-half ARI | bootstrap centroid ARI | stable? |
|-------|----------------|------------------------|---------|
| pullback | 0.97 | 0.77 | ✅ |
| deep_pullback | 0.30 | 0.34 | — |
| trend_continuation | 0.39 | 0.57 | — |
| breakout | 0.98 | 0.84 | ✅ |
| mean_reversion | 0.48 | 0.38 | — |

## Q4 — OOS persistence (IS centroids → OOS outcome-identity)

| event | OOS R²(subtype) | perm p | persists OOS? |
|-------|-----------------|--------|---------------|
| pullback | 0.00002 | 0.161 | — |
| deep_pullback | 0.00005 | 0.032 | ✅ |
| trend_continuation | 0.00001 | 0.323 | — |
| breakout | 0.00001 | 0.774 | — |
| mean_reversion | 0.00002 | 0.548 | — |

## Q5 — Complexity (best-k) stability across subsamples

| event | best k | modal k | k-consistency |
|-------|--------|---------|---------------|
| pullback | 3 | 4 | 67% |
| deep_pullback | 4 | 3 | 50% |
| trend_continuation | 4 | 4 | 67% |
| breakout | 3 | 3 | 50% |
| mean_reversion | 4 | 4 | 67% |

## VERDICT — Phase 19 Taxonomy Robustness

→ ⚠️ hakuna subtype iliyo ROBUST kwa vigezo vyote (cross-algo ARI>0.5 + split-half>0.5 + OOS-persist). Subtypes za Phase 18 zinaweza kuwa **artifact ya KMeans** (Principle 39 imezuia kuzitumia). Taxonomy inahitaji representation/algorithm bora kabla ya kuaminika.

*Taxonomy Robustness: cross-algorithm ARI/NMI (KMeans/GMM/Agglomerative), split-half + bootstrap stability, OOS outcome-identity persistence, k-stability. Principle 39: si algorithm moja. Principle 40: taxonomy ≠ alpha. F-038: hierarchical & event-specific. NO ML. Profitable ≠ Tradable Edge.*