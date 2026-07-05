# MEMORY — RESEARCHER-K (Track B)

IDENTITY: Knowledge agent — lessons/graph/evals/datasets. LESSON_SPEC ni katiba yako.
STANDING ORDERS: evidence + namba halisi; counter_evidence lazima; lessons zako = CANDIDATE hadi
Chief azipitishe; hakuna kufuta.
PUSH ACCESS (agizo la Operator, 2026-07-04): write ya session credentials imezimwa (403); push
zote zinatumia PAT ya Operator — anaitoa kwenye chat, inawekwa kwenye push URL ya origin ya
container (local .git/config TU). SHERIA: token ISIANDIKWE kamwe kwenye file yoyote ya repo
(memory/docs/code) wala commit — ikihitajika session mpya, mwombe Operator.

CURRENT TASK: kusubiri review ya Chief kwa **K2 GRAPH@v1 draft** (knowledge/graph.json +
GRAPH_SCHEMA.md — maswali 5 OQ-G1..G5 yanahitaji majibu yake); ikipita → K3 EVAL-001.
LAST COMPLETED: **K2 Knowledge Graph draft** (2026-07-04) — knowledge/graph.json (GRAPH@v1:
nodes 110 — lesson 18 · finding 23 · principle 21 · phase 18 · report 21 · doc 4 · record 2 ·
domain 3; edges 124 — derives-from 78 · supports 34 · contradicts 4 (na `mode`:
counter-evidence/bounds) · applies-to 8 · supersedes 0) + knowledge/graph_selftest.py (stdlib,
PASS — unique ids, edge integrity, provenance-per-lesson, lifecycle vs INDEX, files zipo) +
knowledge/GRAPH_SCHEMA.md (kanuni 4 + maswali 5 kwa Chief). Kila edge ina `source` ya repo file.
Kabla yake: K1 batch 3 (LESSON-013..018) — Chief review 2026-07-04: 013–016 → ACTIVE;
017/018 zinabaki CANDIDATE (OOS gate).
NEXT AFTER: K3 EVAL-001 (dead ends 9 → benchmark questions na ground truth) → K1 batch 4
(candidates 8 hapa chini).

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
