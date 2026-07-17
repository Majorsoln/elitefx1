# K4 MODEL v0 — DESIGN YA M3-5 (entry-quality: p(win | mazingira))

*2026-07-17 · Author: SCIENTIST-D (design-of-record; charter §M3-5 "SCIENTIST-D design +
IMPLEMENTER-A build") · Inafuata VERBATIM §D ya `reports/m3_curriculum_audit.md` (hati yangu ya
certification) · Dataset: `data/strategies/k4_dataset.parquet` baada ya M3-FIX (K-1 ts_entry ✓,
K-2 manifest+`load_k4` assert ✓, K-3 atr_rel ✓ — verified `e070b30`/`30aa2ba`; baselines
hazikubadilika: 71.1/79.3/59.0/60.6%).*

---

## 0. Lengo, falsafa, na H0

Model v0 inajibu swali MOJA: **je, mazingira ya signal bar yanaweza kuchuja trades za
STRAT-001/002 kwa namna inayoboresha EV-per-trade na kufupisha mfululizo wa hasara, bila
kuua total edge?** (charter §Tabaka-3: win rate inapanda kwa uchambuzi, si jiometri.)

**H0 rasmi (§D6): HAKUNA lift ya maana.** Hypothesis ya kwanza ni kwamba model haina thamani —
kuikataa kwa ushahidi ndiyo mafanikio. Uwezekano mkubwa (max single-feature AUC = 0.532,
`scientist_d_m3_audit.py`) ni kwamba lift itakuwa ndogo au sifuri; verdict ya "NO-LIFT" ni
matokeo halali, yanarekodiwa kama LESSON, na K4-filter HAIENDI M3-6. Hakuna mtu anayelazimisha
model kufanya kazi.

**Marufuku za msingi (§D, binding):**
- Accuracy NI MARUFUKU kama decision metric (baseline 71%/59% — "wote-washinda" hupata 71%).
- Hakuna tuning yoyote juu ya VALID (selection-tainted — STRAT-001/002 walichaguliwa KWA
  window hiyo; §D1). VALID = check MOJA baada ya freeze.
- Hakuna OUTCOMES ndani ya X (`load_k4` assert — §D2). Hakuna deep nets (§D6, N~1.6k).
- HOLDOUT haipo kwenye mchakato huu KABISA (dataset yenyewe haina 2025+).

## 1. Model class na muundo (§D6, C3)

**Per-strategy models — MBILI tofauti, hakuna pooling.** Payoff geometries ni tofauti
(STRAT-001 USDCHF SL2/TP1, baseline 71.1%; STRAT-002 USDJPY SL1/TP1, 59.0%) na N inatosha
kila upande (1,607 / 1,746 TRAIN). Pooling ingehitaji strategy-indicator + calibration mbili —
ugumu bila faida kwa strategies 2. (Strategy ya tatu ikizaliwa, revisit.)

- **PRIMARY: Logistic regression, L2 penalty** — coefficients zinasomeka, calibration ya
  asili, deterministic. Solver `lbfgs`, `max_iter=1000`, seed fixed.
- **CHALLENGER (moja tu): Decision tree, depth ≤ 3, min_samples_leaf ≥ 100** — kwa
  interaction rahisi ambazo logistic haioni. Tree inashindana na logistic NDANI ya CV kwa
  metric rasmi (§3); mshindi mmoja per strategy ndiye anayefungwa.
- **HAKUNA class re-weighting/SMOTE:** tunataka p(win) iliyo-calibrated, si classifier
  balanced — re-weighting inaharibu calibration ambayo threshold policy (§5) inaitegemea.

**Feature sets (pre-declared — chaguo kati yao ni NDANI ya CV tu):**
- `CORE` (regime + compression quality + HTF muktadha; ~13 raw → ~19 baada ya one-hot):
  `vol_state, activity_state, spread_state, session_entry, atr_rel, range_nr7_atr,
  h4_trend_sign, d1_trend_sign, h4_rsi14, d1_rsi14, h4_roc10, d1_roc10, d1_dist_res_atr`
- `FULL` = FEATURES za manifest **MINUS exclusions za hygiene (§6): `atr_pips` (absolute
  level = year-proxy, §D5 — `atr_rel` inaziba) na `hour` (DST jitter; `session_entry`
  inatosha)** → 25 raw.
- Preprocess per-fold (hakuna cross-fold leakage): one-hot kwa categoricals (UNKNOWN = level
  yake — 2016-warmup ipo TRAIN); numeric NaN → median ya TRAINING-fold; standardize kwa
  mean/sd ya TRAINING-fold.

## 2. CV protocol — BLOCKED time-CV ndani ya TRAIN PEKEE (§D3)

- **Folds = miaka 7 (2016..2022), leave-one-year-out**, kwa `ts_entry` (K-1). Mwaka ni block
  ya asili hapa: N per mwaka 205-270 kila strategy, coverage kamili (audit §K4).
- **Purge/embargo: bars 24** (= MAX_HOLD) kila upande wa boundary ya fold — trade za train
  zenye `entry_bar` ndani ya bars 24 za trade yoyote ya test-year boundary zinaondolewa
  (na `ts_entry` ± 24h sawa kwa H1). Hii inazuia jirani-leakage ya serial correlation (§D3).
- **Hyperparameter grid (pre-declared, NDOGO — hii ndiyo multiplicity yote inayoruhusiwa):**
  logistic `C ∈ {0.03, 0.1, 0.3, 1.0}` × feature set `∈ {CORE, FULL}` (cells 8) + tree
  `depth ∈ {2,3} × min_leaf ∈ {100,150}` × {CORE, FULL} (cells 8) = configs 16 per strategy.
  Selection metric = utility rasmi ya §3 (ΔEV_R@70% ya CV pooled), SI accuracy/AUC/log-loss.
- **Prune pass MOJA (§6):** baada ya CV ya kwanza, features za PRIMARY zenye sign-flip ya
  coefficient kwenye >2/7 folds zinaondolewa, na CV inarudiwa mara MOJA. Hakuna iteration
  zaidi — mbili tu: full grid, prune, FREEZE.
- **FREEZE kwa commit** (config + coefficients + threshold p* + H0 criterion) KABLA ya VALID.
- **VALID = evaluation MOJA, bila kugusa chochote.** Expectation iliyoandikwa mapema (§D1):
  lift ya VALID inatarajiwa **×0.35–0.5 ya lift ya CV** (slope ya shrinkage iliyopimwa ya
  mfumo huu — `data_science_review.md` §A3-W2); VALID pia ime-inflate baseline (79.3% vs
  holdout 73.9% kwa STRAT-001) — kwa hiyo hukumu ya VALID ni ya SIGN, si ya ukubwa.

## 3. Metrics RASMI (§D4) — zote na CI za stationary-block bootstrap (mb=3, B=10,000)

Retention pre-declared: **q ∈ {70%, 50%}** (PRIMARY = 70%). Filter = weka trades zenye
p̂(win) ≥ p* ambapo p* = threshold ya §5. Kwa kila strategy, kwa mfululizo ULIOPANGWA kwa
`ts_entry`:

| # | Metric | Definition | Nafasi |
|---|---|---|---|
| M1 | **ΔEV_R@q** | EV_R(filtered) − EV_R(all) | **PRIMARY** (decision) |
| M2 | **EV-retention@q** | Σ pnl_R(filtered) / Σ pnl_R(all) | guard (usiue total edge) |
| M3 | **Loss-streak@q** | max + P95 ya consecutive-loss runs (time-ordered), filtered vs all | FTMO guard |
| M4 | AUC, reliability curve (deciles za p̂ vs win-rate halisi) | diagnostic PEKEE — kamwe si decision |

CI: block bootstrap juu ya trade sequence (inaheshimu clustering); ΔEV_R CI kwa paired
resampling (mask ya filter inabaki ndani ya resample).

## 4. Criterion ya kukataa H0 (imefungwa SASA, kabla ya namba yoyote)

**CV verdict (per strategy, huru — deployment decisions mbili tofauti, kila moja α=0.05):**
Kataa H0 ("model ina lift") IFF zote tatu, kwenye CV pooled (folds 7, out-of-fold predictions):
1. ΔEV_R@70% > 0 na one-sided block-bootstrap p < 0.05;
2. ΔEV_R@70% ≥ **+0.05 R** (economic floor — chini ya hapo si lift inayolipa uendeshaji;
   +0.05 R ≈ +1.0 pip STRAT-001 / +0.5 pip STRAT-002 kwa ATR za kawaida);
3. EV-retention@70% ≥ **0.90** (filter isiyoue total edge).

**H0 ikikataliwa → FREEZE → VALID one-shot:** PASS iff ΔEV_R@70% > 0 (sign) NA
EV-retention@70% ≥ 0.80. (Sign-only kwa sababu ya power: N_valid×0.7 ≈ 300; na taint ya §D1.)
- CV-PASS + VALID-PASS → model v0 inapanda M3-6 (gate kamili ya Chief; forward kabla ya live).
- CV-PASS + VALID-FAIL → LESSON ("CV lift haikuhamia era mpya") — model HAIENDI M3-6; error
  analysis inarudi kwenye curriculum (charter §5).
- CV-FAIL (H0 inabaki) → LESSON "no deployable lift v0"; K4 inabaki dataset ya thamani kwa
  uchambuzi; hakuna filter. **Hakuna njia ya tatu, hakuna re-grid baada ya kuona VALID.**

## 5. Threshold policy + hesabu za streak/FTMO

- **p\* imewekwa kwenye TRAIN-CV PEKEE:** p\* = wastani (across folds) wa quantile ya p̂
  inayotoa retention 70% kwenye out-of-fold predictions; inafungwa kama NAMBA ABSOLUTE
  (si re-quantile juu ya VALID/live — retention halisi itaachwa i-drift na ku-monitor).
- **Monitoring ya retention (deployment):** kama rolling-60-trade retention halisi inatoka
  nje ya 70%±15pts → flag ya recalibration (kupitia gate, si silent retune) — inaingia
  kwenye winrate_monitor infrastructure (R6).
- **Streak arithmetic (kwa Tabaka-4 sizing, deterministic):** kwa win rate w na trades n/mwaka,
  E[max loss-streak] ≈ ln(n)/ln(1/(1−w)). Baselines TRAIN: STRAT-001 w=0.711, n≈230/yr →
  max-streak ≈ 4.4; STRAT-002 w=0.590, n≈250/yr → ≈ 6.2. Filter ikiongeza w kwa +3pts:
  STRAT-001 → 4.1, STRAT-002 → 5.7 — faida ndogo lakini FTMO-relevant (daily-loss budget =
  streak × risk-per-trade). Jedwali hili linachapishwa kwenye report ya model na kupelekwa
  Tabaka-4 kama input ya sizing; sizing yenyewe SI kazi ya M3-5.

## 6. Feature hygiene + per-year stability (§D5)

- X inatoka `k4_dataset.load_k4(features_only=True)` TU (assert ya manifest ndani yake);
  exclusions za ziada za design hii: `atr_pips`, `hour` (sababu §1). `dir`/`year` ni META —
  haziingii (long/short asymmetry = extension ya v1, si v0).
- **Per-year coefficient stability (PRIMARY model):** refit kwa kila fold; kwa features 5 za
  juu kwa |coef|: sign lazima iwe ile ile kwenye ≥5/7 folds. Ukiukaji → prune pass ya §2.
  Ripoti inaonyesha jedwali la coefficients per fold — hii ndiyo "interpretable" kwa vitendo.
- **UNKNOWN check:** kama dummy ya `*_UNKNOWN` (warmup-2016) inaingia top-5 kwa |coef| →
  flag nyekundu (model inajifunza "2016", si regime) — feature hiyo inaondolewa kwenye prune.
- Reliability curve kwenye CV lazima iwe monotonic-ish (deciles); calibration mbaya →
  logistic inashinda tree kwa default (tunahitaji p, si rank).

## 7. Deliverables za IMPLEMENTER-A + acceptance tests

**Deliverables:**
1. `src/research/k4_model.py` — CLI: `--cv` (grid+prune+report), `--freeze` (andika
   `data/strategies/k4_model_v0.json`: config, coefficients/tree rules, p*, criterion,
   dataset hash), `--eval-valid` (inakataa kukimbia bila freeze file iliyo-commit — angalia
   AT3), `--self-test`. Model artifact = **JSON** (coefficients/splits — auditable,
   deterministic; HAKUNA pickle).
2. `reports/k4_model_report.md` — per strategy: jedwali la CV per fold (metrics zote §3 + CI),
   coefficients per fold (stability), reliability deciles, verdict ya H0 kwa criterion §4,
   frozen config + p*, streak table §5. VALID section inaongezwa TU baada ya freeze commit.
3. Registration text kwa Chief (criterion §4 verbatim + dataset commit hash + freeze commit).

**Acceptance tests (self-test, bila data ya nje — fixtures synthetic):**
- **AT1 leak trap:** kuingiza `mfe_r` kwenye FEATURES → `load_k4`/trainer assert inalia.
  Pia: X ya trainer inathibitishwa kuwa subset ya manifest FEATURES minus exclusions.
- **AT2 blocked-CV correctness:** fixture yenye ts; assert (a) kila fold = mwaka mmoja;
  (b) HAKUNA trade ya train ndani ya purge ya bars 24 kutoka boundary za test year;
  (c) out-of-fold predictions zina-cover kila trade mara moja.
- **AT3 no-VALID-tuning guard:** `--eval-valid` bila freeze file → error; `--cv` juu ya rows
  za split=validation → PermissionError (trainer inakataa kufit VALID); freeze file ina
  dataset hash — mismatch → error.
- **AT4 metric exactness:** outcomes crafted (sequence inayojulikana) → ΔEV_R, EV-retention,
  max/P95 streak = closed-form values (1e-12).
- **AT5 determinism:** run mbili → coefficients + metrics bit-identical (seed+solver fixed).
- **AT6 planted-signal/null sanity:** synthetic labels zenye feature X ya kweli (AUC~0.65
  by construction) → pipeline ina-detect (H0 rejected kwenye CV) · synthetic NULL (labels
  huru na features, w=0.7) → H0 inabaki kwa ~nominal rate (MC ndogo, M=200: reject ≤ ~10%).
- **AT7 threshold freeze:** p* inahesabiwa kutoka CV artifacts pekee; assert kwamba VALID
  eval inasoma p* kutoka freeze file, kamwe haihesabu upya.

**Sequencing:** build (IMPLEMENTER-A) → review ya Chief + referee yangu (AT6 kwa MC yangu
huru, kama utaratibu wa WAVE-1/family-pooled) → Operator: `--cv` kwenye PC ya data → prune →
FREEZE commit (Chief) → `--eval-valid` one-shot → report + verdict → M3-6 gate (kama PASS).

---

**Matarajio ya uwazi (yamefungwa kabla ya namba):** kwa max single-feature AUC 0.532 na
serial correlation, matokeo yanayowezekana zaidi ni lift ndogo (ΔEV_R@70% ∈ [0, +0.1] R)
au H0 kubaki. STRAT-002 (baseline 59%, TP kubwa kiasi) ana nafasi kubwa zaidi ya filter
yenye maana kuliko STRAT-001 (71% tayari, edge ndogo per trade). Verdict yoyote — ikiwemo
"hakuna lift" — ni ujuzi mpya wa curriculum, si kushindwa kwa mradi.

*SCIENTIST-D · Design inafuata §D1-D6 za m3_curriculum_audit.md verbatim · Hakuna dirisha
jipya: TRAIN-CV + VALID one-shot (dataset haina 2025+) · Profitable ≠ Tradable Edge.*
