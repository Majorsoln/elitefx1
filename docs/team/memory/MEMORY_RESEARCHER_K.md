# MEMORY — RESEARCHER-K (Track B)

IDENTITY: Knowledge agent — lessons/graph/evals/datasets. LESSON_SPEC ni katiba yako.
STANDING ORDERS: evidence + namba halisi; counter_evidence lazima; lessons zako = CANDIDATE hadi
Chief azipitishe; hakuna kufuta.
PUSH ACCESS: 2026-07-05 — **relay ya session imerudi kufanya kazi** (`git push origin` inatumia
proxy ya kawaida; PAT ya Operator ya 2026-07-04 sasa inarudisha 403 = imekufa/revoked). Tumia relay
ya kawaida. SHERIA ya kudumu: token/PAT yoyote ISIANDIKWE kamwe kwenye file ya repo wala commit —
relay ikizima tena (403), mwombe Operator PAT kupitia chat + weka kwenye local .git/config push URL TU.

CURRENT TASK: kusubiri review ya Chief kwa (a) **GRAPH@v2** (EVAL-001 linkage) na (b) **K1 batch 4**
(LESSON-019..026, CANDIDATE). Zikipita → link 019-026 kwenye graph (→GRAPH@v3) → EVAL-002.
LAST COMPLETED: **K1 batch 4 + EVAL-001 graph-linking** (2026-07-05).
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
NEXT AFTER: (baada ya approval) link 019-026 graph (→GRAPH@v3) → **EVAL-002** (Permanent Truths /
findings APPROVED) → batch 5 (Truths 12 zilizobaki + findings generalizable + D1-D4/E-series).

LESSON CANDIDATES kutoka reports/ (mapitio ya Chief, 2026-07-04 — batch 4+; kila moja soma
report yake kupata NAMBA kabla ya kuandika):
1. state_age + state_transition_model: age = CALIBRATOR sio predictor (accuracy flat, ECE ↓) — METHOD
2. adaptive_volume_bar + volume_information: bars zilishindwa stability (0/9) lakini zikashinda
   information (18/18) — lesson: pima swali SAHIHI kabla ya kukataa wazo — METHOD
3. event_context_matrix: context response ni event-specific (Tier 1/2/3) — MARKET-COND
4. component_interaction: same transition inageuza sign kwa age (lifecycle var) — MARKET-COND
5. representation_operationalization: leak gap ipo KILA mahali (+0.19..+0.33) — in-sample daima
   imevimba; OOS-survival ndiyo kipimo — METHOD
6. semantic_taxonomy + consistency: interpretability ≠ prediction (R²-drop si failure) — METHOD
7. evidence_theory (D0): define contract kabla ya kudai ukweli — GOVERNANCE
8. decision_policy (D5): conflict lazima iwe explicit input, sio hidden ndani ya readiness — METHOD
OPEN QUESTIONS: hakuna kwa sasa.

CHIEF REVIEW (2026-07-04): **K2 GRAPH@v1 APPROVED** — nodes 110/edges 124, self-test PASS
(imeendeshwa na Chief). Rulings OQ-G1..G5: ZOTE kwa mapendekezo yako —
  G1: doctrine versions SIO nodes v1 (zibaki ndani ya lessons; K3 itafikiria).
  G2: range-ids kugawanywa kwa batch maalum ya board definitions (sio kubuni).
  G3: contradicts+mode inabaki (hakuna edge type mpya bila amendment ya Master V1 §3.4).
  G4: domain taxonomy — anza na 3 zilizopo; Chief ataipanua na K3/K4 mahitaji halisi.
  G5: Truths/Failed-Ideas zinaingia graph BAADA ya kuwa lessons (single source of truth).
CURRENT TASK MPYA: **K3 EVAL-001** — dead ends 9 + lessons ACTIVE → benchmark questions zenye
ground truth (knowledge/evals/EVAL-001/): kila swali = scenario halisi ya utafiti wetu (mf. setup
ya Phase 8) + jibu sahihi + evidence ref + rubric ya kupima jibu la model; self-test stdlib;
format inayoweza kuendeshwa na model yoyote. Baada yake: K1 batch 4 (candidates 8).

CHIEF REVIEW (2026-07-05): **K3 EVAL-001 APPROVED** (CANDIDATE→ACTIVE) — maswali 13, self-test
PASS (warning ya length-bias imefungwa ipasavyo kwa sharti la rubric-grading; raw-MCQ-by-length
MARUFUKU inabaki). Positive controls 4 = design sahihi. OQ-E1/E2/E4: endelea na defaults zako;
mabadiliko yoyote ya scoring protocol yanahitaji Chief.
CURRENT TASK MPYA: (a) EVAL-001 graph-linking; (b) K1 BATCH 4 (candidates 8 — lessons 019-026);
baada yake EVAL-002 (Permanent Truths/findings APPROVED).
