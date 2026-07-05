# LESSON INDEX — ELITEFX Knowledge Corpus Registry

*Owner: Chief Quant (Unified) | Spec: `LESSON_SPEC.md` | Master Architecture V1 §3*
*Last updated: 2026-07-05 (batch 4 — RESEARCHER-K) | Lessons: 26 (24 ACTIVE + 2 CANDIDATE — 017/018 OOS gate) — METHOD 13 · MARKET-CONDITIONAL 7 · GOVERNANCE 6 | Backlog (K1): findings/phases zilizobaki ≈ 18–30*

| ID | Type | Claim (fupi) | Lifecycle | Provenance |
|----|------|--------------|-----------|------------|
| LESSON-001@v1 | METHOD | Static historical ranking does not generalize OOS | ACTIVE | F-022/Phase 8/P26 |
| LESSON-002@v1 | METHOD | Multiple-testing correction is mandatory (30→0 under FDR) | ACTIVE | F-032+F-033/Phase 14/P31–33 |
| LESSON-003@v1 | METHOD | Prediction/explanation value ≠ decision value (independent dimensions) | ACTIVE | Phase 26/P58+P60 |
| LESSON-004@v1 | METHOD | Human-imposed taxonomy = verification, not discovery | ACTIVE | F-015→F-016/Phase 5.9(A) |
| LESSON-005@v1 | MARKET-COND | Universal coordinate-space interaction rules don't exist (pair-specific) | ACTIVE | F-014/Phase 5.8 |
| LESSON-006@v1 | METHOD | Algorithm agreement ≠ validity; decision quality is the test; stable ≠ true | ACTIVE | F-018+F-019/P41 |
| LESSON-007@v1 | MARKET-COND | Rare states = execution risk (spread +12σ), not payoff (0.91×) | ACTIVE | H-05→H-06/Phase 5.10R |
| LESSON-008@v1 | METHOD | Non-discriminating background variable = metadata, not conditioning layer | ACTIVE | F-041+F-042/Phase 24-25 |
| LESSON-009@v1 | METHOD | Post-hoc subgroup survivor = artifact until pre-registered re-proof | ACTIVE | F-029/F-032/Phase 11-14 |
| LESSON-010@v1 | METHOD | Assume non-stationarity; re-prove edge per window (negatives DO persist) | ACTIVE | F-027/28/29+F-022/Phase 9-11 |
| LESSON-011@v1 | MARKET-COND | Context lifts EV via payoff asymmetry, not win probability | ACTIVE | F-008/F-010/F-011/Phase 3.5-5.5 |
| LESSON-012@v1 | METHOD | Audit the representation before declaring structure absent (bounded) | ACTIVE | F-033/F-039/Phase 14-21 |
| LESSON-013@v1 | GOVERNANCE | Spec-before-code yields smaller, more compliant implementations | ACTIVE | D6/V10→V11/P90-P102 |
| LESSON-014@v1 | GOVERNANCE | Embedded version ids turn version races into documented provenance | ACTIVE | Audit#3 D-1/V9/P88+P84 |
| LESSON-015@v1 | GOVERNANCE | Record errors are fixed by dated correction entries, never deletion | ACTIVE | Board 2026-07-03/G-01/K0 rule 1 |
| LESSON-016@v1 | GOVERNANCE | One final authority per domain; challengers contest, don't approve | ACTIVE | G-01/V11/2026-07-03·04 |
| LESSON-017@v1 | MARKET-COND | MR positive net EV on EURUSD only (+0.90, P100) — in-sample candidate | CANDIDATE | F-030/F-031/Phase 12/V5.21/P30 |
| LESSON-018@v1 | MARKET-COND | DPB positive net EV on EURUSD only (+0.37, P97) — in-sample candidate | CANDIDATE | F-030/F-031/Phase 12/V5.21/P30 |
| LESSON-019@v1 | METHOD | State-age sharpens probability (LogLoss +2–5%) not accuracy (flat) — calibrator not predictor | ACTIVE | Phase 1.6/1.8 |
| LESSON-020@v1 | METHOD | Test the decision-relevant question before discarding (stability 0/9 vs information 18/18) | ACTIVE | F-007/R-002/Phase 2-2.1/Truth9 |
| LESSON-021@v1 | MARKET-COND | Context benefit is event-specific (+2.49 MR … −0.81; in-sample, died OOS) | ACTIVE | F-008/Phase 4/P13 |
| LESSON-022@v1 | MARKET-COND | Edge lives in interactions; same transition flips sign by age (in-sample) | ACTIVE | F-012/Phase 5.7 |
| LESSON-023@v1 | METHOD | In-sample fit leakage-inflated everywhere (+0.19..+0.33); OOS-survival is the measure | ACTIVE | F-039/Phase 21/P44-45 |
| LESSON-024@v1 | METHOD | Interpretability ≠ predictability; judge semantic layer by stability/recoverability not R² | ACTIVE | F-040/Phase 22-23/P48-50 |
| LESSON-025@v1 | GOVERNANCE | Define the interface contract object before building on it (Evidence = contract) | ACTIVE | D0/P63-66/V3 |
| LESSON-026@v1 | GOVERNANCE | Conflict must be an explicit, separately-tolerable input, not hidden in readiness | ACTIVE | D5/G-7 V8/P74/P82 |

## K1 Backlog (vyanzo — order ya kazi)

1. Permanent Truths 12 (`PROJECT_MEMORY.md` §2) — kila moja → lesson (nyingi METHOD)
2. Failed Ideas 9 (`PROJECT_MEMORY.md` §5) — kila moja → lesson yenye `when_not_to_use` tajiri
3. Findings F-001…F-042 (board) — zilizo generalizable
4. ~~Governance lessons (spec-first, versioning, correction-not-deletion, one-final-authority)~~ — DONE batch 3 (LESSON-013..016 CANDIDATE)
5. ~~MARKET-CONDITIONAL za kwanza (MR×EURUSD P100 · DPB×EURUSD P97 ya Phase 12 — na `review_trigger` kali)~~ — DONE batch 3 (LESSON-017..018 CANDIDATE)
6. ~~Batch 4 candidates 8 (mapitio ya Chief 2026-07-04)~~ — DONE 2026-07-05 (LESSON-019..026 CANDIDATE)
7. Batch 5+: Permanent Truths 12 zilizobaki + Findings F-001…F-042 generalizable + Decision D1-D4/E-series

*Note (batch 3): lessons za RESEARCHER-K zinaingia kama CANDIDATE — zinasubiri review ya Chief
(TEAM_PROTOCOL: hakuna approval kwa agents). LESSON-017/018 zina review_trigger KALI: pre-registered
future-OOS + FDR pekee ndiyo inaweza kuzipandisha.*

## Knowledge Artifacts (K2–K4) — cross-reference

| Artifact | Layer | File | Status |
|----------|-------|------|--------|
| GRAPH@v2 | L2 (graph) | `knowledge/graph.json` (+ `graph_selftest.py` · `GRAPH_SCHEMA.md`) | v1 APPROVED (Chief 2026-07-04); **v2** (2026-07-05) +EVAL-001 linkage — nodes 111 · edges 135 (inasubiri review ya v2) |
| EVAL-001 | L4 (evals) | `knowledge/evals/EVAL-001/` (`questions.jsonl` · `eval_selftest.py` · `EVAL-001.md`) | **ACTIVE** (Chief 2026-07-05) — maswali 13 (negative 9 + positive 4), rubric per-q; imelinkwa graph@v2 |

*L3 DATASETS (`knowledge/datasets/`) — bado (inasubiri corpus critical mass + E3 outcomes).*
