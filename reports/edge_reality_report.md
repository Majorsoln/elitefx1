# Edge Reality Test — je edge ni HALISI au ni noise? (Phase 11)

*2026-06-27 20:13 | null models + permutation + bootstrap (200 reps) | rolling 6 windows | configs N≥200: 1,271 | H1: edge halisi · H0: sampling noise*

> **Principle 28 (Chief):** HAKUNA adaptive system kabla ya kuthibitisha persistent edge ipo ZAIDI ya random expectation. **F-027 (APPROVED):** early quality haitabiri future persistence. **F-029 (OPEN):** edge decay inaweza kuwa stochastic. Swali: je 'survivors' tulizoziona ni zaidi ya bahati? ⚠️ Hatusemi 'kuna hidden variable' — kwanza thibitisha edge ipo. NO ML, NO Opportunity Engine.


**Observed:** configs=1,271 | first-positive=519 | EV>0=410 | survivors (6/6 windows)=**9** | mean survival=1.74 (Top 2% ref = 25)


## Q1 — Null model (shuffle outcomes): je survival inafanana na bahati?

- observed survivors = **9** | null-global survivors = **4.6** ± 2.0 (mean ± sd, 200 reps)
- observed mean-survival = **1.74** | null-global = **1.63**

→ observed ZAIDI ya null (z = +2.2).

## Q2 — Randomized order (time shuffle, keep config EV): je persistence ni halisi?

- observed survivors = **9** | null-time survivors = **39.3** ± 4.7
- observed mean-survival = **1.74** | null-time = **2.16**

→ null-time inashika EV ya config lakini inavunja muda; tofauti = persistence ya KWELI (haionekani).

## Q3 — Bootstrap / CI: je observed iko NJE ya random world?

- null-global 95% CI ya survivors = [1, 9]
- observed survivors = **9** (NDANI ya CI ⚠️)
- bootstrap ya observed (resample configs): 9 ± 3 [4, 16]

## Q4 — Permutation: je Top survivors ni ZAIDI ya random expectation?

- permutation p-value (P(null-global survivors ≥ observed)) = **0.050**

→ ✅ significant (p<0.05): survivors zaidi ya bahati.

## Q5 — P(Observed Edge > Random Edge) kwa kila event

| event | observed mean EV | null mean EV | P(obs > random) |
|-------|------------------|--------------|-----------------|
| breakout | -1.810 | -0.956 | 0% |
| deep_pullback | -0.848 | -0.965 | 89% |
| mean_reversion | +0.051 | -0.955 | 100% |
| pullback | -1.195 | -0.954 | 0% |
| trend_continuation | -1.397 | -0.970 | 0% |

→ events zenye P(obs>random) > 95%: **1/5**.

## VERDICT — H1 (edge halisi) vs H0 (noise)

→ ⚠️ **H0 haijakataliwa**: survivors observed (9) HAZIZIDI random kwa uhakika (null 4.6, z=+2.2, perm p=0.050, ndani ya CI). Sehemu kubwa ya 'edge' inaweza kuwa **sampling noise** (inaunga mkono F-029). Principle 28: HAIRUHUSIWI kujenga adaptive system/ML bado — edge halisi haijathibitishwa zaidi ya bahati.

*Edge Reality Test: null-global (shuffle outcomes) + null-time (shuffle order, keep EV) + permutation + bootstrap. H1 = survivors > random (perm p<0.05 NA nje ya null CI). F-027: early quality ≠ future persistence. F-029: decay inaweza kuwa stochastic. Principle 28: thibitisha edge > random kabla ya adaptive system. NO ML. Profitable ≠ Tradable Edge.*