# MODEL STEWARD — practical vs learned + weakness map + agenda

*2026-07-30T16:13:44 UTC · READ-ONLY meta-model (Doctrine V2 §8.2) · min_n=30*

> **SAMPLE: replay/validation, si forward halisi bado — power inakua na forward data. HAKUNA dai la 'model imethibitika forward' bila forward.**


## (A) PRACTICAL vs LEARNED (per model)

| model | N | learned EV (pips) | practical mean (pips) | 90% CI | divergence | verdict | mean R |
|-------|---|-------------------|-----------------------|--------|------------|---------|--------|
| STRAT-001 | 425 | 1.92 | 3.072 | [1.874, 4.244] | 1.152 | ✓ HOLDS | 0.1371 |
| STRAT-002 | 443 | 2.65 | 3.861 | [1.753, 5.841] | 1.211 | ✓ HOLDS | 0.1598 |

## (B) WEAKNESS MAP (per model × dimension; kila cell N + CI + verdict)


### STRAT-001

| dimension | cell | N | mean (pips) | 90% CI | divergence | verdict |
|-----------|------|---|-------------|--------|------------|---------|
| session | ASIA | 326 | 2.193 | [0.753, 3.608] | 0.273 | ✓ HOLDS |
| session | LONDON | 19 | 7.463 | — | 5.543 | · INSUFFICIENT |
| session | NY | 80 | 5.612 | [3.086, 8.013] | 3.692 | ▲ LIFTS |
| vol | HIGH | 142 | 3.444 | [0.827, 6.137] | 1.524 | ✓ HOLDS |
| vol | LOW | 142 | 3.267 | [2.023, 4.516] | 1.347 | ▲ LIFTS |
| vol | MID | 141 | 2.501 | [0.56, 4.334] | 0.581 | ✓ HOLDS |
| streak | AFTER_2L+ | 22 | 8.011 | — | 6.091 | · INSUFFICIENT |
| streak | AFTER_LOSS | 65 | -0.045 | [-3.352, 3.257] | -1.965 | ✓ HOLDS |
| streak | AFTER_WIN | 337 | 3.311 | [1.944, 4.568] | 1.391 | ▲ LIFTS |
| streak | FRESH | 1 | 16.361 | — | 14.441 | · INSUFFICIENT |
| cost | HIGH-COST | 108 | 1.368 | [-1.399, 4.015] | -0.552 | ✓ HOLDS |
| cost | LOW-COST | 190 | 4.227 | [2.674, 5.712] | 2.307 | ▲ LIFTS |
| cost | MID-COST | 127 | 2.793 | [0.531, 5.011] | 0.873 | ✓ HOLDS |

### STRAT-002

| dimension | cell | N | mean (pips) | 90% CI | divergence | verdict |
|-----------|------|---|-------------|--------|------------|---------|
| session | ASIA | 168 | 2.856 | [-0.549, 5.783] | 0.206 | ✓ HOLDS |
| session | LONDON | 162 | 4.249 | [0.625, 8.12] | 1.599 | ✓ HOLDS |
| session | NY | 113 | 4.797 | [0.472, 8.932] | 2.147 | ✓ HOLDS |
| vol | HIGH | 148 | 5.586 | [0.809, 10.652] | 2.936 | ✓ HOLDS |
| vol | LOW | 148 | 1.925 | [0.157, 3.694] | -0.725 | ✓ HOLDS |
| vol | MID | 147 | 4.072 | [1.23, 6.865] | 1.422 | ✓ HOLDS |
| streak | AFTER_2L+ | 73 | 1.629 | [-3.428, 6.757] | -1.021 | ✓ HOLDS |
| streak | AFTER_LOSS | 103 | 3.86 | [-0.362, 8.004] | 1.21 | ✓ HOLDS |
| streak | AFTER_WIN | 266 | 4.624 | [1.917, 7.468] | 1.974 | ✓ HOLDS |
| streak | FRESH | 1 | -36.292 | — | -38.942 | · INSUFFICIENT |
| cost | HIGH-COST | 112 | 9.678 | [4.095, 15.1] | 7.028 | ▲ LIFTS |
| cost | LOW-COST | 166 | 0.693 | [-1.842, 3.121] | -1.957 | ✓ HOLDS |
| cost | MID-COST | 165 | 3.099 | [-0.115, 6.15] | 0.449 | ✓ HOLDS |

## (C) IMPROVEMENT AGENDA (ranked athari × uhakika — PENDEKEZO, si auto-apply)

> Steward HAITEKELEZI. Kila kipengele = hypothesis kwa Chief/PD kupitia registration ya kawaida (kama SCIENTIST-D). L-041: diagnostics, SI 'best cell = strategy mpya'.

| # | model | weakness | N | divergence | hypothesis (trade language) | proposed experiment | risk |
|---|-------|----------|---|------------|-----------------------------|---------------------|------|
| 1 | ALL | regime dimension haipo kwenye log (DATA-GAP) | 0 | None | regime (trend/range/compression) haijalog na live_engine bado | ongeza HTF regime tag kwenye execution record ya engine (additive) ili weakness-map ya regime iwezekane | hakuna (log field additive) |

## (D) SAMPLE-HONESTY + PROVENANCE

- **SAMPLE: replay/validation, si forward halisi bado — power inakua na forward data. HAKUNA dai la 'model imethibitika forward' bila forward.**
- data: `C:\Users\Hp\project\elitefx1\data\paper\paper_log.jsonl` · lines=6984 · closed-trades=868 · sha256=5d107ea95f26b5bb
- commit: `366ac9ade5465db4ce405f3d20ae16f4e7d6f959` · generated_at: 2026-07-30T16:13:44.722646+00:00
- verdict key: HOLDS (CI inagusa learned) · SHRINKS (CI chini ya learned — shrinkage) · LIFTS (CI juu) · INSUFFICIENT (N<min_n, anti-noise).

*Zoezi endelevu: kila data mpya (paper/forward) -> Steward inasasisha ramani + ajenda. reports/model_steward.json = malighafi ya panel MODEL HEALTH (Dashboard-V2, §8.2).*