# K4 MODEL v0 — REGISTRATION (kwa Chief; deliverable §7.3 ya k4_model_design.md)

> Criterion imefungwa **KABLA ya namba yoyote** (design §4). Build: `src/research/k4_model.py`
> (self-test AT1–AT7 PASS, sweep GREEN). Dataset: `data/strategies/k4_dataset.parquet` (M3-FIX:
> K-1 ts_entry, K-2 manifest+load_k4 assert, K-3 atr_rel). Model = per-strategy (STRAT-001/002,
> hakuna pooling); PRIMARY L2-logistic, CHALLENGER shallow tree — mshindi 1 per strategy ndani ya CV.

## CRITERION YA KUKATAA H0 (verbatim, §4 — imefungwa)

**H0 = "model haina lift ya maana."** CV verdict (per strategy, huru, α=0.05) — kataa H0 **IFF zote tatu**
kwenye CV pooled out-of-fold (folds 7, leave-one-year-out, purge bars 24):
1. `ΔEV_R@70% > 0` NA one-sided block-bootstrap `p < 0.05`;
2. `ΔEV_R@70% ≥ +0.05 R` (economic floor);
3. `EV-retention@70% ≥ 0.90` (usiue total edge).

**H0 ikikataliwa → FREEZE (commit) → VALID one-shot:** PASS iff `ΔEV_R@70% > 0` (sign) NA
`EV-retention@70% ≥ 0.80`. (Sign-only: power + taint ya §D1.)

- CV-PASS + VALID-PASS → M3-6 gate (Chief; forward kabla ya live).
- CV-PASS + VALID-FAIL → LESSON ("CV lift haikuhamia era mpya"); HAIENDI M3-6.
- CV-FAIL → LESSON ("no deployable lift v0"); hakuna filter. **Hakuna re-grid baada ya kuona VALID.**

## PARAMETERS (frozen constants — `k4_model.py`)
| | thamani |
|---|---|
| Folds | miaka 7 (2016–2022), leave-one-year-out, kwa `ts_entry` |
| Purge/embargo | bars 24 (= MAX_HOLD) kila upande wa boundary |
| Grid | logistic C∈{.03,.1,.3,1} × {CORE,FULL} + tree depth∈{2,3}×leaf∈{100,150}×{CORE,FULL} = **16** |
| Prune | pass MOJA (sign-flip >2/7 folds au dummy UNKNOWN kwenye top-5 |coef|) → re-CV MOJA |
| Retention q | 70% (PRIMARY), 50% (alt) |
| Bootstrap | stationary block (mb=3, B=10,000), seed FIXED — utility ya CI, SI pvalue_boot ya research |
| p* threshold | TRAIN-CV PEKEE (wastani across folds), imefungwa kama NAMBA — VALID/live haire-quantize |
| Exclusions | `atr_pips` (year-proxy), `hour` (DST jitter); `dir`/`year` = META (si features) |

## SEQUENCING
build (IMPLEMENTER-A ✅) → review Chief + SCIENTIST-D (AT6 MC huru) → Operator `--cv` (PC ya data,
dakika kadhaa) → report + H0 verdict → **KAMA CV-PASS:** Chief ruling → `--freeze` (commit; artifact
`data/strategies/k4_model_v0.json` — config/coefficients/p*/criterion/**dataset hash**; HAKUNA pickle)
→ `--eval-valid` (one-shot; inasoma p* kutoka freeze, inakagua dataset hash) → M3-6 gate. **KAMA
CV-FAIL:** LESSON, hakuna filter.

- **Dataset commit hash:** (ijazwe na Operator baada ya `--build` — `git rev-parse` ya commit ya parquet)
- **Freeze commit:** (ijazwe na Chief baada ya `--freeze`)

*Marufuku (§D binding): accuracy si decision metric; hakuna tuning juu ya VALID; hakuna OUTCOMES ndani
ya X (load_k4 assert); hakuna deep nets; HOLDOUT haipo kwenye mchakato huu (dataset haina 2025+).*
