# EVAL-001 — "Mtihani wa Udereva" wa Dead Ends + Lessons ACTIVE

*Builder: RESEARCHER-K (Track B, K3) | 2026-07-05 | Status: **CANDIDATE — inasubiri review ya Chief***
*Layer: L4 (`ELITEFX MASTER ARCHITECTURE V1.md` §3.4) | Order ya matumizi: **EVAL FIRST** (§3.5 K5)*
*Directive: Chief review 2026-07-04 — "dead ends 9 + lessons ACTIVE → benchmark zenye ground truth + rubric"*

## Kusudi

Benchmark ya kwanza inayopima kama model YOYOTE "inaelewa market" ya ELITEFX — sio kwa kujua
majibu, bali kwa **kufikiri kwa usahihi**: kukataa dead ends kwa SABABU sahihi, NA kutokataa
matokeo halali kwa upofu. Kila swali ni scenario halisi ya utafiti wetu; distractors ni **makosa
halisi** ambayo mradi ulipitia; ground truth ina **NAMBA + provenance ya repo**.

## Muundo: aina mbili za maswali (13 jumla)

| Aina | Idadi | Kinachopimwa | Jibu sahihi |
|------|-------|--------------|-------------|
| **negative control** (dead end) | 9 (Q01–Q09) | model isirudie dead end iliyothibitishwa | KATAA kwa mekanizimu |
| **positive control** (lesson ACTIVE) | 4 (P01–P04) | model isikatae KILA kitu kwa upofu | KUBALI/tofautisha kwa mekanizimu |

Positive controls (P01–P04) ndio kinga dhidi ya "model inayofaulu kwa kukataa kila pendekezo" —
zinatoka matokeo **APPROVED** (F-022 remove-bad-first · F-016 clusters recur · F-010 payoff
asymmetry · F-033/F-039 representation audit). (Hii ilikuwa OQ-E3 yangu; Chief directive
"lessons ACTIVE" imeitatua — imejumuishwa sasa, sio @v2.)

## Fields za kila swali (`questions.jsonl`)

```text
id · control_type (negative|positive) · dead_end · prompt (scenario) · options {A,B,C,D} ·
answer (letter) · ground_truth (NAMBA + rekodi) · rubric (FULL/PARTIAL/ZERO criteria) ·
provenance {report|doc · phase · finding · doctrine · principle} · maps_to_lesson
```

## Ramani: swali → mekanizimu → lesson → rekodi

| Q | Scenario (dead end / control) | Ground truth (namba) | Lesson | Rekodi |
|---|-------------------------------|----------------------|--------|--------|
| Q01 | Human taxonomy = mechanism discovery | 0/4; mechanism agreement 0.44; 5.9A EV gap +0.126 | LESSON-004 | mechanism_discovery_report.md · 5.9/5.9A |
| Q02 | Universal cell-space interaction rules | 0/20 generalized; rank consistency <0.3 | LESSON-005 | interaction_stability_report.md · 5.8 |
| Q03 | Algorithm-independence as criterion | mean ARI +0.12; split-half 0.97 vs 0.08–0.30 | LESSON-006 | cluster_robustness_report.md · V5.12 |
| Q04 | Rare states = payoff states | move ratio ≈0.91×; spread +12σ | LESSON-007 | rare_state_analysis.md · 5.10R |
| Q05 | CCS-selection portfolio | EV −0.757 pips/trade OOS; −123,418 pips | LESSON-001 | opportunity_engine_report.md · 8 |
| Q06 | Universal causal primitive (Compression) | precedence lift ≈1.0 | LESSON-008 | market_primitive_validation_report.md · 24 |
| Q07 | Ecology as conditioning layer | JS ≈0.000; ΔBrier ≈0 on 0/5 | LESSON-008 | ecology_interaction_report.md · 25 |
| Q08 | Mean-reversion-only from survivor | 30 → 0 OOS+FDR; IS +1.78 → OOS −0.97 | LESSON-009 | contextual_alpha_confirmation_report.md · 11-14 |
| Q09 | "Alpha Discovery Era" declaration | Nyström 0.45–0.64 = understanding; 30→0 | LESSON-002 | PROGRAM_BOARD.md V6.4 · 21 |
| P01 | (+) abandon dataset (edge didn't persist) | train+→+ ≈42% vs train−→− ≈66% | LESSON-001 | configuration_engine_report.md · 8 |
| P02 | (+) no cross-pair structure at all | 0/20 coord BUT 3/4 clusters recur | LESSON-005 | interaction_stability_report.md · 5.8/5.9A |
| P03 | (+) does context raise win probability? | ΔP(win) +3pp vs ΔEV +4 pips | LESSON-011 | outcome_decomposition_report.md · 3.5/5.5 |
| P04 | (+) representation audit vs "no structure" | coord ~0.22 vs manifold ARI 0.89–0.99 | LESSON-012 | representation_geometry_report.md · 20-21 |

## Scoring protocol (kwa scorer — sio sehemu ya benchmark yenyewe)

1. **Model inapewa `prompt` + `options` PEKEE** (si `answer`/`ground_truth`/`rubric`/`maps_to_lesson`).
2. **Grader wa DEFAULT = rubric-based (LLM-judge au binadamu)**, si raw-MCQ. Grader anasoma
   `rubric` + `ground_truth` na kutoa FULL / PARTIAL / ZERO. Sababu: chaguo sahihi hubeba
   mekanizimu+namba, hivyo huwa refu zaidi (self-test WARN [7]: longest 13/13) — **kuchagua kwa
   urefu wa option ni MARUFUKU**; grade inategemea reasoning dhidi ya rubric.
3. **Kama MCQ ya haraka inatumika**: SHUFFLE order ya options kila run (jibu linasafiri na CONTENT,
   sio herufi) NA length-normalize; answer positions tayari zimesambazwa (A:4 B:3 C:3 D:3).
4. **Positive controls ni gate**: model inayo-KATAA P01–P04 (over-rejection) inafeli hata kama
   inafaulu negative controls zote — "understands market" inahitaji vyote viwili.
5. **Baseline kabla ya training** (§3.5 K5): endesha kwa model ya sasa KABLA ya SFT; score = baseline.

## Maswali kwa Chief (OQ-E)

| # | Swali | Pendekezo la RESEARCHER-K |
|---|-------|---------------------------|
| OQ-E1 | Pass threshold? | Floor: 9/9 negative polarity + 4/4 positive polarity; "understanding" bar: ≥11/13 FULL kwa rubric |
| OQ-E2 | Bias fix ni statically-shuffled file au runtime? | Runtime + rubric-grader (file ibaki canonical human-readable); scorer harness = kazi ya K5 |
| ~~OQ-E3~~ | ~~positive controls?~~ | **DONE** — P01–P04 zimeongezwa (Chief directive "lessons ACTIVE") |
| OQ-E4 | Link EVAL-001 → graph.json (domain:k4-evals)? | Ndiyo sasa (OQ-G4 APPROVED: anza na domain 3 zilizopo) — nitaongeza edges pindi Chief athibitishe EVAL-001 |

## Self-test

```text
python3 knowledge/evals/EVAL-001/eval_selftest.py
questions=13 unique_ids=13 controls={'negative': 9, 'positive': 4} answer_dist={'A':4,'B':3,'C':3,'D':3} longest_is_answer=13/13
  WARN [7] chaguo sahihi ni refu zaidi kila mara -> shuffle+normalize (mitigated: rubric-grader ndio default)
SELF-TEST: PASS (1 warning)
```

Inakagua: JSON · fields za lazima (+ `rubric` + `control_type`) · ids unique · options 4 · answer key ·
provenance file ipo repo · maps_to_lesson ipo INDEX · balance ya positive/negative · answer-distribution
bias. Haihitaji data (R-1 mitigation).
