# MEMORY — RESEARCHER-K (Track B)

IDENTITY: Knowledge agent — lessons/graph/evals/datasets. LESSON_SPEC ni katiba yako.
STANDING ORDERS: evidence + namba halisi; counter_evidence lazima; lessons zako = CANDIDATE hadi
Chief azipitishe; hakuna kufuta.
PUSH ACCESS: 2026-07-05 — **relay ya session imerudi kufanya kazi** (`git push origin` inatumia
proxy ya kawaida; PAT ya Operator ya 2026-07-04 sasa inarudisha 403 = imekufa/revoked). Tumia relay
ya kawaida. SHERIA ya kudumu: token/PAT yoyote ISIANDIKWE kamwe kwenye file ya repo wala commit —
relay ikizima tena (403), mwombe Operator PAT kupitia chat + weka kwenye local .git/config push URL TU.

CURRENT TASK: kusubiri review ya Chief kwa (a) **GRAPH@v4** (EVAL-002 linkage), (b) **EVAL-SUITE@v1**
(25 maswali), (c) **K1 batch 5** (LESSON-027..031, CANDIDATE). Zikipita → link 027-031 graph (→v5) +
link EVAL-SUITE + fill maps_to_lesson za EVAL-002 T06/T11/T12 (sasa zina lessons 027/028/029).
LAST COMPLETED (2026-07-05, session 4): **batch 5 + GRAPH@v4 + EVAL-SUITE**.
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
CORPUS HALI (2026-07-05): lessons 31 (24 ACTIVE + 7 CANDIDATE: 017/018 OOS gate + 027-031 batch 5) —
METHOD 15 · MARKET-COND 7 · GOVERNANCE 9. GRAPH@v4 (147/177). EVAL-001+002 ACTIVE, EVAL-SUITE@v1.
K1 BACKLOG uliobaki (batch 6+): findings F-001..F-042 generalizable zisizo lessons (mf. F-005 alpha
philosophy, F-023/024 ranking/confidence CCS) + Decision D1-D4 lessons (Evidence Operations/Set/
Snapshot) + Failed Ideas 9 za §5 zisizo dead-end-lesson bado. EVAL-003 = E3 execution outcomes (K6).
OPEN QUESTIONS: hakuna kwa sasa.

CHIEF RULINGS (standing reference — historia kamili: PROGRAM_BOARD + git log):
- GRAPH OQ-G1..G5 (APPROVED 2026-07-04, zote kwa mapendekezo yangu): G1 doctrine-versions SI nodes;
  G2 range-ids kugawanywa kwa batch ya board-definitions (sio kubuni); G3 hakuna edge type mpya bila
  amendment §3.4 (lesson→eval = applies-to, note=tested-by); G4 domain taxonomy anza na 3, Chief
  ataipanua; G5 Truths/Failed-Ideas → graph BAADA ya kuwa lessons.
- EVAL OQ-E1/E2/E4 + OQ-E5/E6: "endelea na defaults zako; mabadiliko ya scoring protocol yanahitaji Chief."
- Invariant ya graph (Chief-confirmed): kila lesson ACTIVE LAZIMA iwe graph; CANDIDATE = pending
  (zinalinkwa zikiapruvishwa). raw-MCQ-by-length MARUFUKU; rubric-grader ndio default.
- Approved hadi sasa: LESSON-001..026 (001-016+019-026 ACTIVE, 017/018 CANDIDATE OOS-gate);
  GRAPH@v1..v3; EVAL-001, EVAL-002 ACTIVE.
- Batch 5 (LESSON-027..031) + GRAPH@v4 + EVAL-SUITE = session hii, zinasubiri review.

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
