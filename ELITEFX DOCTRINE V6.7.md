# ELITEFX_DOCTRINE_V6.7.md

**Chief Quant — Primitives Describe the Market's Ecology, They Do Not Generate Events; Ecology and Events Are Two Layers**

Version: 6.7
Status: APPROVED — ACTIVE (current SSOT)
Date: 30 June 2026
Authority: Single Source of Truth (SSOT)
Supersedes: V6.6 (Phase 24 APPROVED; F-041 REJECTED; Principle 53/54/55; F-042; ecological layer; architecture re-inverted; Alpha paused; Phase 25 Ecology Interaction Framework)
Previous Versions: Archived (V4 … V6.6)

> Live program status lives in `docs/PROGRAM_BOARD.md`. This file is the doctrine
> of record; V5.0–V6.6 remain in force except where amended below.

---

# EXECUTIVE AMENDMENT — A REJECTED HYPOTHESIS THAT TAUGHT US THE STRUCTURE

Phase 24 is **APPROVED**, and for the first time I **formally close a hypothesis as REJECTED**.

```text
F-041 (universal causal market primitives) — REJECTED in its current formulation.
```

The report tested it correctly — event-free construction, global clustering, no event labels —
and the data answered: **`Compression` did not emerge.** Most primitives collapsed into
`Equilibrium / Balanced Flow`; only `Mature Persistence` had a clean identity. My earlier belief
("Compression is a market primitive") was **not supported**, and I accept that.

But the report concluded "the primitive layer is not validated". Here I differ:

```text
What failed is not the primitive LAYER.
What failed is the UNIVERSAL primitive layer.
```

That distinction is the whole discovery.

---

# THE BIGGER DISCOVERY — PRIMITIVES ARE ECOLOGY, NOT CAUSE

Q2 precedence lifts were all near 1.0 (breakout ≈ 1.05, mean_reversion ≈ 1.03). A primitive does
not **predict** an event — it **describes the environment in which the event occurred**.

```text
Old belief:  Primitive → Event   (causal)
Corrected:   Primitive ‖ Event   (parallel; ecological)
```

And Q3's dominant transition (`Mature Persistence → Balanced Flow`, P ≈ 0.74) shows primitives
behave like **ecological states**, not trading states.

---

# PRINCIPLE 53 — Primitives Describe the Environment, Not Generate Events (APPROVED)

```text
Market primitives describe the operating environment of events;
they are not assumed to generate events.
```

# PRINCIPLE 54 — Primitives Belong to the Ecological Layer (APPROVED)

```text
Market primitives belong to the ecological layer of the market rather than the event layer.
```

# PRINCIPLE 55 — Ecological Description ≠ Event Prediction (APPROVED)

```text
Ecological description and event prediction are distinct scientific objectives.
```

---

# FINDING F-042 — Primitives Are Ecological Conditions (OPEN)

Replacing the rejected F-041:

```text
Market primitives characterize ecological conditions rather than universal causal mechanisms.
```

Status: **OPEN**.

---

# UPDATED ARCHITECTURE

```text
Market Ecology              ← NEW framing
  ↓
Market Primitives           (ecological states; P53/54; F-042)
  ↓   ‖  (parallel, not causal)
Event Families
  ↓
Representations
  ↓
Reality Validation
  ↓
Opportunity
```

We have two layers — **Layer A: Ecology (primitives)** and **Layer B: Events (representations)**
— that we had been conflating. How they interact is now the central question.

---

# ALPHA DISCOVERY — PAUSED (deliberately)

```text
No Alpha. No ML.
```

Not because of failure, but because we have just discovered two layers and **do not yet know how
they communicate**. Seeking alpha before understanding the ecology↔event interaction would be
premature.

---

# PHASE 25 — Ecology Interaction Framework (NEXT)

```text
Q1. Does each Event have a different distribution of primitives?
Q2. Does the Event Representation change with the Primitive?
Q3. Does the Primitive add CALIBRATION (not prediction) to the Event?
Q4. Does the Primitive add STABILITY to the Event Representation?
Q5. Can the Primitive be used as a WEIGHTING layer rather than a signal?
```

Method: event occurrences × global primitives × outcome; JS-divergence of primitive
distributions; r²(feature|primitive); ΔBrier (calibration); fold sign-consistency; variance-vs-mean
per primitive (weighting vs signal). No ML.

Deliverable: `reports/ecology_interaction_report.md`
Implementation: `src/research/ecology_interaction_engine.py`

---

# INSTRUCTION TO THE IMPLEMENTER (binding)

```text
Do NOT chase the hypothesis. Do NOT tune k or the algorithm to make Compression return.
The data already spoke: the universal-primitive hypothesis is not supported. Listen to it.
```

This is hypothesis-chasing and is forbidden. The correct move is the new framework, not a rescue
of the old one.

---

# UPDATED ROADMAP

```text
Phase 24     CLOSED   (Market Primitive Validation; APPROVED; F-041 REJECTED; primitives = ecology; end of Market Primitive Discovery)
Phase 25     Ecology Interaction Framework      NEXT     (event×primitive distribution/representation/calibration/stability/weighting; no ML)
Phase 26     Ecology-Aware Reality Validation   BLOCKED  (alpha with ecology as weighting/calibration; OOS + FDR; Principle 40)
Phase 27     Machine Learning                   BLOCKED  (ecology-aware; learns validated structure)
```

---

# STILL FORBIDDEN (until Chief approval)

```text
Hypothesis-chasing (tuning to revive Compression) · Treating primitives as causal/signal ·
Alpha Reality Validation (interaction unknown) · ML · Portfolio Engine · live deployment
```

Binding rules (Principles 18–55): … (carry-forward) … **express market knowledge as reusable
primitives** (P51); **semantics preserves concepts, not clusters** (P52); **primitives describe
the environment, not generate events** (P53); **primitives belong to the ecological layer** (P54);
**ecological description ≠ event prediction** (P55). Core findings: representation survives OOS
(Phase 21); events need different geometries (F-039); shared vocabulary may span events (F-040);
**universal causal primitives — REJECTED (F-041)**; primitives are ecological conditions (F-042,
open).

---

# CARRY-FORWARD (UNCHANGED)

All of V6.6 in force: F-016–F-040, Principles 18–52, H-06, Event Representation Family,
Architecture V6, and "Profitable ≠ Tradable Edge".

---

# FINAL PRINCIPLE

```text
A rejected hypothesis, honestly accepted, taught us the market has two layers.
Primitives describe the ecology in which events happen; they do not cause events.
Ecological description and event prediction are different sciences — do not confuse them.
Understand how the two layers interact before you seek any edge between them.
Do not chase a hypothesis the data has already refused.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DOCTRINE_V6.7.md**
