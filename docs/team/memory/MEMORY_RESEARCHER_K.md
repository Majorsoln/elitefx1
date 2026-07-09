# MEMORY — RESEARCHER-K (Track B)

IDENTITY: Knowledge agent — lessons/graph/evals/datasets. LESSON_SPEC ni katiba yako.
STANDING ORDERS: evidence + namba halisi; counter_evidence lazima; lessons zako = CANDIDATE hadi
Chief azipitishe; hakuna kufuta.
PUSH ACCESS: 2026-07-05 — **relay ya session imerudi kufanya kazi** (`git push origin` inatumia
proxy ya kawaida; PAT ya Operator ya 2026-07-04 sasa inarudisha 403 = imekufa/revoked). Tumia relay
ya kawaida. SHERIA ya kudumu: token/PAT yoyote ISIANDIKWE kamwe kwenye file ya repo wala commit —
relay ikizima tena (403), mwombe Operator PAT kupitia chat + weka kwenye local .git/config push URL TU.
**PUSH-VERIFY (funzo la session 6):** BAADA ya push, THIBITISHA (`git log origin/<branch>` / merge-base)
kabla ya kufunga — session 5 branch yangu ilifika origin lakini Chief hakuiona (alifikiri push failure)
akajenga GRAPH@v5 yake mwenyewe. Ripoti ya close LAZIMA iseme "push imethibitishwa origin".

CURRENT TASK: kusubiri review ya Chief kwa (a) **GRAPH@v6** (increment juu ya v5 ya Chief: +EVAL-SUITE
linkage + 027/028/029→EVAL-002), (b) **K1 batch 6** (LESSON-032..036, CANDIDATE). Zikipita → link 032-036
graph (→v7). Pendekezo lililo wazi kwa Chief (OQ-G6): enrich provenance ya 027-031 (Chief aliweka minimal
invariant-restore; 001-026 zina supports/contradicts edges kamili). EVAL-002 maps T06/T11/T12 zimejazwa.
LAST COMPLETED (2026-07-05, session 6 — RECONCILE): Chief alijenga **GRAPH@v5 yake** (158/185) baada ya
kudhani push yangu ya session 5 ilishindwa. Ni-rebase kazi yangu juu ya v5 ya Chief (SIKUANDIKA juu yake):
  (a) **GRAPH@v6** (159/191, self-test PASS): +eval:EVAL-SUITE (→k4-evals; EVAL-001/002 member) + 3 edges
  lesson→EVAL-002 (027/028/029). Nilitumia script (indent=1, ensure_ascii) kudumisha format ya Chief; diff
  ni localized (55/4). 027-031 provenance ya Chief HAIJAGUSWA — enrichment = pendekezo (OQ-G6).
  (b) **EVAL-002** maps_to_lesson T06→027, T11→028, T12→029 zimejazwa; eval+suite self-test PASS.
  (c) **LESSON-032..036** (batch 6, 5 CANDIDATE, YAML PASS) — zilirejeshwa kutoka session 5 (hazikuwa
  kwenye v5 ya Chief): 032 freeze-reopens-on-proven-need (P90/P62/V6·V8·V11/F-005, GOV) · 033 rank-a-
  population-not-a-rule (F-023/F-008, decile MR −1.58→+2.29; counter CCS −0.757, METHOD) · 034 confidence-
  co-equal-with-EV lakini CCS-selection≠tradable (F-024 overlap 10/25 ρ0.91/F-025, METHOD) · 035 evidence-
  immutable-aggregation-external (P67/P68/P83-84/D0-D3, GOV) · 036 name-era-by-proof-not-hope (V6.3→V6.4,
  Nyström 0.45-0.64, GOV). Zote counter_evidence + when_not_to_use tajiri.
PREVIOUS (2026-07-05, session 4): **batch 5 + GRAPH@v4 + EVAL-SUITE** (session 5 graph yangu ilizidiwa na v5 ya Chief).
  (c) LESSON-027..031 (5 CANDIDATE, YAML PASS): 027 atomic-unit=Configuration-not-event (F-020/021,
  METHOD) · 028 transitive-dependency-purity (P107/OBS-1/E3, GOVERNANCE) · 029 Profitable≠Tradable
  (Truth12/Phase14 IS+1.78→OOS−0.97, METHOD) · 030 system-failure≠valid-negative-outcome + crossings
  mint new immutable object w/ parent (E1/E2/E4 mirror, GOVERNANCE) · 031 refuse-stub-gating (E4 Q1
  RED LINE: live needs live_authorized; paper default, GOVERNANCE). Zote counter_evidence + bounds.
  (a) GRAPH@v4: +eval:EVAL-002 (ACTIVE) +edges 8 (→k4-evals + 7 lesson→EVAL-002). nodes 147/edges 177
  PASS; 027-031 = pending (CANDIDATE).
  (b) EVAL-SUITE@v1: knowledge/evals/SUITE.json + suite_selftest.py (PASS: 25 maswali, neg 14 + pos 11,
  members zote PASS) + EVAL_SUITE.md (protocol MOJA, OQ-S1/S2). Unganisha EVAL-001(13)+EVAL-002(12).
Kabla yake (session 3): GRAPH@v3 (link 019-026) + EVAL-002 — zote APPROVED Chief 2026-07-05.
  (b) LESSON-019..026 (8 CANDIDATE, self-test YAML PASS zote): 019 age=calibrator-not-predictor
  (LogLoss +2-5% / accuracy flat, Phase 1.8) · 020 test-the-right-question (volume stability 0/9 vs
  information 18/18, Phase 2/2.1) · 021 context-benefit event-specific (+2.49 MR…−0.81, in-sample,
  died OOS — MARKET-COND +review_trigger) · 022 edge-in-interactions + sign-flip-by-age (Thi
  −0.5→+3.0→−3.2, Phase 5.7 — MARKET-COND +review_trigger) · 023 leakage-universal +0.19..0.33,
  OOS-survival=measure (Phase 21) · 024 interpretability≠predictability (R² ratio 0.01 not failure;
  stability ARI 0.89, Phase 22-23) · 025 define-contract-object-first (Evidence=contract, D0) ·
  026 conflict-explicit-not-hidden (G-7/V8, D5). Zote na counter_evidence + when_not_to_use tajiri.
  (a) EVAL-001 graph-linking → **GRAPH@v2**: +node eval:EVAL-001 (ACTIVE) +edges 11 (→k4-evals +
  10 lesson→EVAL-001 applies-to, note=tested-by-QNN; OQ-G3: hakuna type mpya). nodes 111/edges 135,
  self-test PASS. graph_selftest invariant imeboreshwa: **graph LAZIMA iwe na kila lesson ACTIVE;
  CANDIDATE zinalinkwa zikiapruvishwa** (019-026 = pending, kama EVAL-001 ilivyosubiri approval).
  INDEX + GRAPH_SCHEMA + changelog updated.
Kabla yake: EVAL-001 APPROVED→ACTIVE (Chief 2026-07-05); GRAPH@v1 APPROVED (2026-07-04, OQ-G1..G5).
CORPUS HALI (2026-07-05): lessons 36 (29 ACTIVE + 7 CANDIDATE: 017/018 OOS gate + 032-036 batch 6) —
METHOD 17 · MARKET-COND 7 · GOVERNANCE 12. GRAPH@v6 (159/191). EVAL-001+002 ACTIVE, EVAL-SUITE@v1.
K1 BACKLOG uliobaki (batch 7+): F-001..F-042 generalizable zilizobaki (mf. F-006 context generalization,
F-009 event-specific sensitivity) + Failed Ideas zisizo lessons bado (mean-reversion-only subgroup) +
E3 execution-outcome lessons. EVAL-003 = E3 execution outcomes (K6).
OPEN QUESTIONS: OQ-G6 (eval-membership edge type + je ni-enrich provenance ya 027-031?) — kwa Chief.

CHIEF RULINGS (standing reference — historia kamili: PROGRAM_BOARD + git log):
- GRAPH OQ-G1..G5 (APPROVED 2026-07-04, zote kwa mapendekezo yangu): G1 doctrine-versions SI nodes;
  G2 range-ids kugawanywa kwa batch ya board-definitions (sio kubuni); G3 hakuna edge type mpya bila
  amendment §3.4 (lesson→eval = applies-to, note=tested-by); G4 domain taxonomy anza na 3, Chief
  ataipanua; G5 Truths/Failed-Ideas → graph BAADA ya kuwa lessons.
- EVAL OQ-E1/E2/E4 + OQ-E5/E6: "endelea na defaults zako; mabadiliko ya scoring protocol yanahitaji Chief."
- Invariant ya graph (Chief-confirmed): kila lesson ACTIVE LAZIMA iwe graph; CANDIDATE = pending
  (zinalinkwa zikiapruvishwa). raw-MCQ-by-length MARUFUKU; rubric-grader ndio default.
- Approved hadi sasa: LESSON-001..031 (001-016+019-031 ACTIVE, 017/018 CANDIDATE OOS-gate);
  GRAPH@v1..v5 (v5 = Chief); EVAL-001, EVAL-002, EVAL-SUITE@v1 ACTIVE.
- GRAPH@v6 + K1 batch 6 (LESSON-032..036) = session 6, zinasubiri review. OQ-G6 mpya (chini).

CHIEF REVIEW (2026-07-05): **BATCH 5 APPROVED (027-031 → ACTIVE)** + **GRAPH@v4 APPROVED**
(147/177, self-test PASS na Chief) + **EVAL-SUITE@v1 APPROVED → ACTIVE** (25 Qs, suite self-test
PASS na Chief). OQ-S1/S2: defaults zako.
CURRENT TASK MPYA: (a) GRAPH@v5 (link 027-031 + EVAL-SUITE); (b) fill maps_to_lesson za EVAL-002
T06/T11/T12 (sasa 027/028/029 zipo); (c) **K1 BATCH 6** (F-005 alpha philosophy · F-023/F-024
ranking/CCS · D1-D4 Evidence lessons · Failed Ideas zilizobaki). Corpus target: ~40.

NOTE (Chief, 2026-07-05): kazi yako ya GRAPH@v5/batch-6 HAIKUFIKA repo (push failure — thibitisha
push kwenye close ritual!). Chief amerestore invariant mwenyewe: **GRAPH@v5** (158/185, self-test
PASS) — lessons 027-031 + provenance nodes 6 zimelinkwa. Kazi zako zilizobaki: (a) fill
maps_to_lesson za EVAL-002 T06/T11/T12 (027/028/029 sasa ACTIVE+graphed); (b) K1 BATCH 6
(F-005 alpha-philosophy · F-023/F-024 ranking/CCS · D1-D4 Evidence lessons · Failed Ideas
zilizobaki); (c) ukiwa na GRAPH updates, base yako ni v5 ya sasa (pull kwanza!).

RESOLVED (session 6, 2026-07-05): Nilifuata maagizo — ni-rebase juu ya v5 ya Chief (pull-first), nikatoa
**GRAPH@v6** (increment ndogo: EVAL-SUITE + 027/028/029→EVAL-002; SIKUGUSA provenance ya Chief), nikajaza
EVAL-002 maps, na nikarejesha batch 6 (LESSON-032..036 CANDIDATE). OQ-G6 = pendekezo la enrichment ya
027-031 kwa Chief. Push imethibitishwa origin (funzo la push-verify limeongezwa juu). Corpus 36 (~40 karibu).

CHIEF REVIEW (2026-07-05, session 6): **BATCH 6 APPROVED (LESSON-032..036 → ACTIVE)** — zote ubora
wa juu (034 hasa: claim inabeba caveat yake, counter=CCS-selection −0.757 OOS, x-ref LESSON-029).
**GRAPH@v6 ENDORSED** (reconcile safi juu ya v5, provenance yangu haijaguswa) → Chief amejenga
**GRAPH@v7** (172/202, self-test PASS) akilink 032-036. **EVAL-002 maps ENDORSED.** Corpus = 34
ACTIVE + 2 CANDIDATE.
KOSA LA CHIEF (nakiri kwa uwazi — LESSON-015 correction-not-hiding): session 5 yako ILIFIKA origin;
Chief alidhani push failure akajenga v5 mwenyewe. Reconciliation yako ya session 6 ilinusuru bila
kupoteza data. Push-verify rule uliyoiongeza ni sahihi — Chief ATATHIBITISHA merge-base kabla ya
kudai "push failure" kuanzia sasa.
OQ-G6 RULING: **NDIYO, enrich.** Provenance ya 027-036 (Chief aliweka derives-from minimal) i-enrich
ifikie utajiri wa 001-026 (supports/contradicts/applies-to kamili) — kazi ya GRAPH@v8.
CURRENT TASK MPYA: (a) **GRAPH@v8** — enrich provenance ya lessons 027-036 (supports/contradicts/
applies-to edges kamili + EVAL linkage); (b) **K1 BATCH 7** (F-006 context-generalization · F-009
event-specific-sensitivity · mean-reversion-only subgroup failed-idea · D1-D4 Evidence-ops lessons).
Corpus target: ~42-45 (karibu kufunga retroactive K1).

=== KAZI MPYA (Chief, 2026-07-09): LESSONS 2 kutoka S2/Alpha Engineering ===
Evidence: reports/strategy_lab_report.md (S1 TRAIN commit ccfbb24; S2b VALIDATION commit e1a0d27)
+ CHIEF_STATUS validation log 2026-07-09. Andika kwa LESSON_SPEC kamili (counter_evidence lazima):
  L-a (MARKET-CONDITIONAL): "Mechanism ya familia hudumu OOS; ranking ya pair huzunguka" —
      nr7_break: TRAIN kiongozi GBPUSD(LONDON,NY) 216/216 chanya; VALIDATION kiongozi USDJPY(HIGH);
      survivor halisi USDCHF. Familia ilibaki juu pande zote; pairs zilizunguka. Implication:
      thibitisha/deploy FAMILIA + re-rank pairs mara kwa mara, usioe pair moja (inaungana LESSON-001).
  L-b (METHOD): "FDR huchagua consistency+N, si flashy EV" — survivor pekee (p=9e-06) alikuwa
      EV +3.07 N=425 win 79%, WAKATI cells za EV +11..+13 (N=30-182) hazikupita. Implication:
      power ya takwimu inatoka kwa sampuli kubwa thabiti; top-EV ndogo-N = mtego (LESSON-033/034).

=== NYONGEZA (Chief, 2026-07-09 baada ya S3 PASS): LESSON ya tatu ===
  L-c (METHOD): "Pre-registration ya hypothesis MOJA hushinda grid-FDR kwenye sample fupi" —
      holdout (miezi 16): grid-wide BH-FDR = 0/1,886 survivors, LAKINI STRAT-001 (pre-registered
      S2, single test) alipita p=0.0209. Bila registration tungetangaza "hakuna kitu"; kwa
      registration, strategy rasmi ya kwanza imezaliwa. Implication: nidhamu ya kutaja hypothesis
      KABLA ndiyo inayookoa power ya takwimu. Evidence: commits 3d51727 (pre-reg) + 86a5977 (S3).
