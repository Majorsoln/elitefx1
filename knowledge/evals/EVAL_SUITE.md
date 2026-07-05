# EVAL-SUITE@v1 — Runner Manifest (EVAL-001 + EVAL-002)

*Builder: RESEARCHER-K (Track B, K3) | 2026-07-05 | Status: **CANDIDATE — inasubiri review ya Chief***
*Layer: L4 (`ELITEFX MASTER ARCHITECTURE V1.md` §3.4) | Manifest: `SUITE.json` | Runner: `suite_selftest.py`*
*Directive: Chief review 2026-07-05 — "EVAL-SUITE (unganisha 001+002: runner manifest + jumla 25 + scoring protocol moja)"*

## Suite ni nini

Mkusanyiko rasmi wa evals zote za "mtihani wa udereva" wa model — manifest MOJA (`SUITE.json`) +
protocol MOJA ya scoring + runner MOJA (`suite_selftest.py`). Suite haibadilishi evals; inaziunganisha
ili model ipimwe kwa **maswali 25** kwa mpigo mmoja na baseline moja.

## Members (25 maswali; negative 14 · positive 11)

| Eval | Maswali | Controls | Theme | Status |
|------|---------|----------|-------|--------|
| EVAL-001 | 13 | neg 9 · pos 4 | Dead ends 9 (usirudie kosa) + positive controls 4 | ACTIVE |
| EVAL-002 | 12 | neg 5 · pos 7 | Permanent Truths 12 (tumia truth) + overreach-negative 5 (mpaka) | ACTIVE |
| **Jumla** | **25** | **neg 14 · pos 11** | negative+positive symmetry: usirudie kosa NA usikatae ukweli halali | — |

Symmetry ya suite ndiyo hoja: **negative controls** (dead ends + overreach) huzuia model
inayo-affirm kila kitu; **positive controls** (truths + remove-bad-first n.k.) huzuia model
inayo-reject kila kitu. "Understands market" = kufaulu pande zote mbili.

## Scoring protocol (MOJA — imo `SUITE.json.scoring_protocol`)

1. Model inapewa `prompt` + `options` PEKEE.
2. **Grader wa default = rubric-based** (LLM-judge/binadamu) → FULL/PARTIAL/ZERO kwa kila swali;
   raw-MCQ-by-length ni **MARUFUKU** (chaguo sahihi huwa refu zaidi kwa design).
3. MCQ ya haraka: SHUFFLE + length-normalize (answer positions tayari balanced kila eval).
4. **Controls ni gates** (pande zote): affirm-overreach au reject-truth-halali = fail.
5. **EVAL FIRST** (§3.5 K5): endesha suite nzima KABLA ya training = baseline; model ikifaulu bila
   training → training haihitajiki bado.

## Runner / self-test

```text
python3 knowledge/evals/suite_selftest.py
suite=EVAL-SUITE@v1 members=2 total_questions=25 controls={'negative': 14, 'positive': 11}
SUITE SELF-TEST: PASS (members zote PASS)
```

Inakagua: SUITE.json fields · kila member (dir + questions.jsonl zipo; idadi + controls zinalingana
na manifest) · total_questions/total_controls · **kila member `eval_selftest.py` inarudi PASS**.
Stdlib pekee, haihitaji data (R-1 mitigation).

## OQ-S (kwa Chief)

| # | Swali | Pendekezo |
|---|-------|-----------|
| OQ-S1 | Suite pass threshold? | 25/25 polarity floor; ≥21/25 FULL kwa rubric = "understands market" |
| OQ-S2 | EVAL-003+ (E3 execution outcomes → empirical eval, K6) ziongezwe suite? | Ndiyo baada ya E3 stream (S3 lessons); manifest inakua bila kubadili protocol |

*Baada ya batch 5 kupitishwa, EVAL-002 itaweza kulinkwa graph (kama EVAL-001) na lessons 027-031
(T6/T11/T12 + E-series) zitajaza maps_to_lesson za T06/T11/T12 zilizo null sasa.*
