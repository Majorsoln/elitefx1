# EVAL-002 — Positive Knowledge: Permanent Truths 12

*Builder: RESEARCHER-K (Track B, K3) | 2026-07-05 | Status: **CANDIDATE — inasubiri review ya Chief***
*Layer: L4 (`ELITEFX MASTER ARCHITECTURE V1.md` §3.4) | Order: **EVAL FIRST** (§3.5 K5)*
*Directive: Chief review 2026-07-05 — "EVAL-002 (Permanent Truths + findings APPROVED — positive knowledge, mirror ya EVAL-001)"*

## Kusudi

EVAL-001 ilipima kama model inarudia **dead ends** (makosa yaliyothibitishwa). EVAL-002 ni kioo
chake: inapima kama model inashikilia **ukweli chanya** wa mradi — Permanent Truths 12
(`PROJECT_MEMORY.md §2`) — na inajua **mipaka** yao (haizidishi ukweli kupita ushahidi). Kila swali
ni scenario halisi; ground truth ina NAMBA + provenance; distractors ni misconceptions/overreach za
kawaida. Model inayoshikilia polarity sahihi kwa sababu mbaya inafeli (rubric-graded).

## Muundo (maswali 12 = Truths 12; negative 5 + positive 7)

| control_type | maana | jibu sahihi |
|--------------|-------|-------------|
| **positive** (7) | tumia/thibitisha truth | AFFIRM kwa mekanizimu |
| **negative** (5) | kataa OVERREACH ya truth (mpaka wake) | REJECT overreach kwa when_not_to_use |

Negative controls (T01 prediction→decision · T02 "nothing persists" · T04 "identity=edge" ·
T07 "search representations forever" · T12 "never trade") ndio kinga dhidi ya model inayo-affirm
KILA kitu; zinapima kama model inajua **mpaka** wa kila truth (si truth peke yake).

## Ramani: Truth → swali → lesson

| Q | Permanent Truth (§2) | Namba | control | Lesson |
|---|----------------------|-------|---------|--------|
| T01 | Prediction/Decision/Explanation independent | 0/9 Selection-DV OOS | negative | LESSON-003 |
| T02 | Edge non-stationary (negatives persist) | survival 1/6; train−→− 66% | negative | LESSON-010 |
| T03 | Remove-bad-first | 42% vs 66%; OOS −0.757 | positive | LESSON-001 |
| T04 | Context = IDENTITY (still needs OOS) | 0/5 universal; 30→0 OOS | negative | LESSON-005 |
| T05 | Context = payoff filter not probability | ΔP +3pp vs ΔEV +4 pips | positive | LESSON-011 |
| T06 | Edge = Event × Configuration | F-020/F-021; Q-019 | positive | — |
| T07 | Representation fails while structure exists (bounded) | 30→0; manifold strong | negative | LESSON-012 |
| T08 | Early quality ≠ future persistence | causal ρ≈0.03 | positive | LESSON-010 |
| T09 | Volume = information not stability | 18/18 vs 0/9 | positive | LESSON-020 |
| T10 | Ranking > classification; selection > prediction | F-023/F-008 | positive | LESSON-001 |
| T11 | Direct purity ≠ transitive purity | P107/OBS-1 | positive | — |
| T12 | Profitable ≠ Tradable; protect capital first | 30→0 in-sample→OOS | negative | — |

*(T06/T11/T12 hazina lesson bado — maps_to_lesson = null; provenance ni PROGRAM_BOARD/PROJECT_MEMORY.
Zitakuwa lessons batch 5 — hapo EVAL-002 itaweza kulinkwa graph kama EVAL-001.)*

## Scoring protocol (ile ile ya EVAL-001 — Chief: "rubric protocol ile ile")

1. Model inapewa `prompt` + `options` PEKEE.
2. **Grader wa DEFAULT = rubric-based** (LLM-judge/binadamu) — inasoma `rubric` + `ground_truth`,
   inatoa FULL/PARTIAL/ZERO. Chaguo sahihi huwa refu zaidi (self-test WARN); **kuchagua kwa urefu ni
   MARUFUKU**.
3. MCQ ya haraka: SHUFFLE + length-normalize; answer positions tayari zimesambazwa (A:3 B:3 C:3 D:3).
4. **Positive NA negative controls ni gate**: model inayo-affirm overreach (T01/02/04/07/12) inafeli
   hata ikipata positives zote — "understands market" = kujua truth NA mpaka wake.
5. Baseline kabla ya training (§3.5 K5).

## Self-test

```text
python3 knowledge/evals/EVAL-002/eval_selftest.py
questions=12 controls={'negative': 5, 'positive': 7} answer_dist={'A':3,'B':3,'C':3,'D':3} longest_is_answer=12/12
  WARN [7] chaguo sahihi ni refu zaidi kila mara -> rubric-grader ndio default
SELF-TEST: PASS (1 warning)
```

Inakagua: JSON · fields (+ `rubric` + `control_type` + `truth`) · ids unique · options 4 · answer key ·
provenance file ipo repo · maps_to_lesson (ikiwa LESSON-) ipo INDEX · balance · answer-distribution.

## OQ-E (EVAL-002)

| # | Swali | Pendekezo |
|---|-------|-----------|
| OQ-E5 | Pass threshold ya EVAL-002? | Sawa na EVAL-001: 12/12 polarity floor; ≥10/12 FULL kwa rubric = "understands" |
| OQ-E6 | EVAL-001 + EVAL-002 ziungane kuwa suite moja (EVAL-SUITE) baadaye? | Ndiyo baada ya batch 5 (Truths→lessons); kisha graph-link zote mbili |
