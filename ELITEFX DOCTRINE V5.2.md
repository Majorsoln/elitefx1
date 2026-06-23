# ELITEFX_DOCTRINE_V5.2.md

**Chief Quant Amendment — Context Is a First-Class Citizen**

Version: 5.2
Status: APPROVED
Date: 23 June 2026
Authority: Single Source of Truth (SSOT)
Supersedes: V5.0 (full) and V5.1 (folds the State-Dynamics amendment into the core)
Previous Versions: Archived (V4, V4.1, V5.0, V5.1)

---

# EXECUTIVE SUMMARY

V5.2 introduces the following, all justified by completed research
(`state_age_report.md`, `state_context_report.md`, `state_transition_model_report.md`)
and amended by Chief Quant review:

```text
• State Age
• State Context Engine
• Transition Probability Layer
• State Age = CALIBRATOR, not predictor   (Chief Quant amendment)
• Hypothesis H-01 — TESTED AND REJECTED   (Chief Quant amendment)
• Event × Context Rule
• Principle 03 — trading relevance gate
• Phase 1.8 Transition Modeling
• Phase 1.9 Context Value Test            (gate to Phase 2)
```

This is **not a change of direction.** It adds what the data has already
proven — and removes what it has *not.* The two governing statements of this
version are:

```text
Context is now a first-class citizen.

Events no longer exist independently.
```

Everything in V5.0 and V5.1 that is not explicitly amended below **remains
in force.** The official decision metric remains **Expected Value (EV > 0),
not win rate.**

---

# NEW PRINCIPLE — Principle 03 (Trading Relevance)

V5.1 established Principles 01 (*State precedes Event*) and 02 (*Transition
precedes Opportunity*). V5.2 adds a third, which governs the whole Context
program:

## Principle 03 — Context must prove trading relevance

```text
Context must prove trading relevance,
not only statistical relevance.
```

A finding that Context is statistically describable (state, age, transition
probability, calibration) is **necessary but not sufficient.** Before Context
is allowed to drive architecture beyond Phase 1, it must be shown to change
the **EV of decisions on real events** — not merely to fit the data better.
This principle is what makes **Phase 1.9 (Context Value Test)** a mandatory
gate before Phase 2.

---

# AMENDMENT 1 — State Context Engine Is Now Core Architecture

## What changed

Old core flow (V5.1 still implied Transition came straight after State):

```text
STATE
↓
TRANSITION
↓
EVENT
```

New core flow (official as of V5.2):

```text
STATE
↓
STATE AGE
↓
TRANSITION PROBABILITY
↓
EVENT
```

## Why

`state_age_report.md` proved that the probability of a transition depends on
the **age** of the state, not on the state alone:

```text
P(transition) = f(state, age)
```

NOT:

```text
P(transition) = f(state)
```

The Markov / memoryless assumption is rejected. A `LOW_VOL` born one bar ago
is not the same object as a `LOW_VOL` that has survived 20 bars.

## New doctrine section — 2.6 State Context Engine

Insert into PART 2 (Market Architecture) the following section. The State
Context Engine emits, for every bar, the full context vector:

```python
Context = {
    volatility_state,
    activity_state,
    spread_state,

    volatility_age,
    activity_age,
    spread_age,

    pchange_vol,
    pchange_act,
    pchange_spread
}
```

`pchange_*` = P(change | state, age-bucket), estimated **online, from past
transitions only** (no look-ahead). This Context vector is the layer that the
Event Layer and the Triple Barrier Framework will consume downstream.

Implementation of record: `src/research/state_context_engine.py`
(Phase 1.7, CQ-012).

---

# AMENDMENT 2 — Hypothesis H-01 Tested and REJECTED

## What we believed

`state_age_report.md` showed that **Activity** has the largest ΔP(stay) with
age (+40pp vs volatility +14pp, spread +28pp). We rushed from that to the
claim that *Activity carries the most predictive information* (V5.1 Finding F,
proposed Hypothesis H-01).

## The quant error we made

We conflated two different things:

```text
Signal Strength   ≠   Predictability
```

Strong state-memory (a state that, once entered, tends to persist) is **not**
the same as a state whose *next move* is easy to predict.

## HYPOTHESIS H-01 — REJECTED

Original (now rejected):

```text
Activity Dynamics carry more predictive information.
```

Phase 1.8 (`state_transition_model_report.md`) showed the opposite ordering:
Activity is the **hardest** dimension to predict (median ΔLogLoss only +2.2%,
and the lowest accuracy ≈ 56–63%), while volatility (+3.9%) and spread (+4.5%)
predict more cleanly (accuracy ≈ 83–93%).

Replacement statement (OFFICIAL):

```text
Activity Dynamics exhibit strong state-memory characteristics
but remain difficult to predict.
```

New finding (OFFICIAL):

```text
Volatility and Spread currently provide
the most predictable state dynamics.
```

```text
Measure more. Assume less. Kill hypotheses that fail.
```

---

# AMENDMENT 3 — The Event × Context Rule

## What changed

Previously an event could, in principle, be evaluated alone:

```text
Breakout
```

This is now forbidden.

## RULE (OFFICIAL)

```text
No event may be evaluated without context.
```

Bad (rejected):

```text
Trend Pullback
```

Good (required):

```text
Trend Pullback
+
LOW_VOL
+
Activity Age 2
+
Pchange 44%
```

In other words:

```text
Event           is NOT a feature.
Event × Context IS the feature.
```

This formalises and tightens V5.1's Layer-4 rule (`Event + State + Transition`)
into a hard gate: any research, scoring, or labelling that consumes a bare
event without its Context vector is non-compliant with doctrine.

---

# AMENDMENT 4 — Phase 1.8: State Transition Model (Inserted Before Volume Bars)

## What changed

A modelling phase is inserted into the roadmap **before** Volume Bars, to
test whether age is merely descriptive context or a genuine predictive
feature.

## Objective

Compare:

```text
Model A:  P(next_state | state)
Model B:  P(next_state | state, age)
```

## Metrics

```text
LogLoss
Brier Score
Calibration (ECE)
```

Evaluation is **online prequential** (no look-ahead, no arbitrary split):
each bar is predicted from past counts only, then scored, then the counts are
updated.

## Decision rule

```text
If age does NOT improve predictive power:
    Age stays as context only.

If age DOES improve predictive power:
    Age becomes a first-class feature.
```

## Result (Phase 1.8 — COMPLETE)

`state_transition_model_report.md` reports that Model B (with age) beats
Model A on LogLoss and Brier across all pairs and timeframes:

```text
volatility   median ΔLogLoss = +3.9%
activity     median ΔLogLoss = +2.2%
spread       median ΔLogLoss = +4.5%
```

## Chief Quant interpretation — Age is a CALIBRATOR, not a predictor

The improvement is real but its **nature** matters. Accuracy is essentially
unchanged while calibration improves sharply:

```text
Accuracy   91% → 91%      (direction unchanged)
ECE        0.030 → 0.013  (confidence much better)
```

This means the model did **not** learn a new direction. It learned **better
confidence**. Therefore the doctrine is corrected:

```text
WRONG:  State Age predicts transitions.
RIGHT:  State Age improves transition probability calibration.
```

Per the decision rule, age is promoted — but specifically as a **first-class
CALIBRATION feature** (it sharpens P(change)), not as a new directional
predictor.

Implementation of record: `src/research/state_transition_model.py`.

---

# UPDATED DEVELOPMENT ROADMAP

```text
Phase 0     Data Validation              COMPLETE
Phase 1     Market State Engine          COMPLETE
Phase 1.5   Transition Engine            COMPLETE
Phase 1.6   State Age Analysis           COMPLETE
Phase 1.7   State Context Engine         COMPLETE   (Amendment 1)
Phase 1.8   State Transition Model       COMPLETE   (Amendment 4 — age = calibrator)
Phase 1.9   Context Value Test           NEXT       (NEW — gate to Phase 2)
Phase 2     Adaptive Volume Bars         BLOCKED    (until Phase 1.9 proves value)
Phase 3     Event Diagnostics
Phase 4     Event × Context Matrix
Phase 5     Triple Barrier Framework
Phase 6     Outcome Engine
Phase 7     Trade Lifecycle Controller
Phase 8     Risk Allocation Engine
Phase 9     Machine Learning Models
Phase 10    Production Deployment
```

## Phase 1.9 — Context Value Test (NEW, mandatory gate)

Objective — prove **Principle 03**: does Context add *trading* value, not just
statistical value?

```text
Take one KJ event (e.g. Trend Pullback).
Measure:   Event alone
   vs      Event + Context
```

```text
If   Event + Context  >  Event alone   →  V5 architecture is validated.
```

Constraints (Chief Quant directive): **no strategy, no ML, no LightGBM, no
Triple Barrier** at this phase. Just the doctrine proof.

Deliverable: `state_context_value_report.md`.

> Phase 2 (Adaptive Volume Bars) stays **BLOCKED** until this report shows
> Context-conditioned events carry higher EV than bare events. Volume Bars is
> the next major milestone — not because *market states are complete*, but
> because *market context is validated.*

---

# AMENDMENTS NOT YET MADE

The following are deliberately **left untouched** in V5.2 because research has
not yet reached them. They remain as defined in V5.0:

```text
Volume Bars
Triple Barrier
Event Library
Opportunity Engine
```

When research reaches each, it will be amended on the same evidentiary basis
as Amendments 1–4: data first, doctrine second.

---

# UPDATED PRODUCTION ARCHITECTURE

The PART 19 production stack is updated to make Context explicit and ordered:

```text
Volume Bars
        ↓
State + State Age          (State Engine + age)
        ↓
Transition Probability     (State Context Engine)
        ↓
Event Library              (Event × Context only)
        ↓
Opportunity Engine
        ↓
Triple Barrier
        ↓
Outcome Engine
        ↓
Trade Lifecycle Controller
        ↓
Portfolio Controller
        ↓
Risk Allocation Engine
        ↓
Execution
```

---

# CARRY-FORWARD (UNCHANGED FROM V5.0 / V5.1)

All of the following remain in full force and are not restated here:

* PART 1 — Philosophy (EV, scientific method, anti-overfitting)
* PART 2 — Edge Doctrine (Event + Context + Management + Risk)
* PART 4 — Regime Doctrine (regimes are latent hypotheses)
* PART 7 — Triple Barrier Framework (barrier lock, volume-bar vertical barrier)
* PART 8 — Outcome Engine (EV, not win rate)
* PART 9–13 — Lifecycle, Pair Intelligence, Portfolio, Risk Allocation
* PART 16–18 — Statistical Validation, Hypothesis Kill, Transaction Cost
* V5.1 Findings A–E and Principles 01–02 (State precedes Event; Transition
  precedes Opportunity). **Finding F is amended** (see Amendment 2): Activity
  shows the strongest state-memory effects, but volatility and spread
  demonstrate higher predictive stability.

---

# FINAL PRINCIPLE

```text
Predict less.
Measure more.

Assume less.
Validate more.

Context first.
Events second.

Protect capital first.
Seek edge second.
Scale only after proof.
```

**END OF ELITEFX_DOCTRINE_V5.2.md**
