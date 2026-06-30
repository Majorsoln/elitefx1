# ELITEFX_DOCTRINE_V6.8.md

**Chief Quant — The End of the Market Understanding Era; We Now Seek Structure That Changes Decisions, Not Structure That Describes the Market**

Version: 6.8
Status: Superseded by V6.9 (current Market-domain SSOT) — carry-forward in force
Date: 30 June 2026
Authority: Single Source of Truth (superseded by V6.9, 30 June 2026)
Supersedes: V6.7 (Phase 25 APPROVED; F-042 REJECTED; Principle 56/57; end of Market Understanding Era; Decision Theory turn; Phase 26 Decision Value Framework)
Previous Versions: Archived (V4 … V6.7)

> ⚠️ **IMESASISHWA:** SSOT rasmi sasa ni **[ELITEFX DOCTRINE V6.9](ELITEFX%20DOCTRINE%20V6.9.md)**
> (Market domain) + **[ELITEFX DECISION DOCTRINE V1](ELITEFX%20DECISION%20DOCTRINE%20V1.md)** (Decision
> domain). Phase 26 **FULLY APPROVED**; **Principle 58** Prediction/Decision/Explanation ni dimensions
> huru; **Principle 59** representations zinaathiri decisions kupitia evidence tu; **Principle 60**
> decision value ni decision-specific (Phase 26 ilipima **selection** tu); **Principle 61** market vs
> decision science ni domains tofauti; **Principle 62** acha kupanua representations zisizo badilisha
> decision; **mwisho wa Chapter One** — doctrine imegawanyika Market + Decision; market-discovery
> FROZEN. V6.8 carry-forward.

> Live program status lives in `docs/PROGRAM_BOARD.md`. This file is the doctrine
> of record; V5.0–V6.7 remain in force except where amended below.

---

# EXECUTIVE AMENDMENT — THE END OF THE MARKET UNDERSTANDING ERA

Phase 25 is **APPROVED**, and I **formally close F-042 as REJECTED**.

```text
F-042 (primitives are an ecological layer that aids events via calibration/weighting) — REJECTED.
```

The report tested it well and the data is clear: ΔBrier ≈ 0 (0/5 events improved), the weighting
view carried no decision value. I accept the data.

But the implementer wrote "interaction is weak." I put it differently:

```text
The interaction we were looking for simply does not exist.
```

---

# THE DISCOVERY — ECOLOGY IS A BACKGROUND PROPERTY

Q1's JS-divergence between events' primitive distributions was ≈ **0.000**. Every event lives in
almost the same ecology. This erases our assumption:

```text
We assumed:  Ecology → Event  (ecology conditions the event)
Data says:   Ecology does NOT discriminate events.
```

Ecology is not a conditioning variable. It is a **background property** — like the weather. Rain
does not choose which match is played; it is just the environment.

---

# PRINCIPLE 56 — Ecology Is a Background Property (APPROVED)

```text
Market ecology is a background property of the market, not an event discriminator.
```

# PRINCIPLE 57 — Primitives Are Descriptive Metadata Until Proven (APPROVED)

Q4 showed ~90% sign-consistency: the primitive **maintains consistency** but does not change
performance. So a primitive is a **descriptor**, not a predictor. (Q2's r² ≈ 0.24 is **rejected**
as mechanical overlap — the primitive is built from the same features — and is **not** taken into
doctrine.)

```text
Market primitives shall be treated as descriptive metadata
unless independent decision value is demonstrated.
```

---

# PRIMITIVE RESEARCH — PAUSED

```text
Stop digging for new primitives.
```

Across many tests the primitive layer is **not** a signal, **not** a weighting, **not** a
calibration, **not** a discriminator. Continuing would be **hypothesis-chasing**, which doctrine
forbids.

---

# THE TURN — FROM MARKET STRUCTURE TO DECISION THEORY

We began by asking "does the Event have an edge?" and travelled through states, transitions,
trajectory, taxonomy, semantics, primitives, ecology. The gap that remains is not in the market —
it is in **decision theory**. We have built excellent representations but never shown:

```text
Which DECISION does this representation change?
```

New objective for ELITEFX:

```text
We will no longer search for new market structure.
We will search for structure that changes decisions.
```

---

# PHASE 26 — Decision Value Framework (NEXT)

```text
Q1. Which variables have ever changed a DECISION (not a prediction) across the whole project?
Q2. For each Principle, show its decision value.
Q3. Which findings have never changed a decision? (remove them)
Q4. Build a Decision Graph:  Representation → Decision → Execution.
Q5. Score each variable on: Prediction Value | Decision Value | Explanation Value.
```

Method (data-driven for variables): Prediction Value = r²(outcome|levels); **Decision Value =
out-of-sample, time-split SELECTION ΔEV** (choose levels with positive train-EV, compare realized
EV vs trade-all); Explanation Value = level-profile distinctiveness. Q2/Q3 = a curated doctrine
audit of decision-relevance. No ML.

Deliverable: `reports/decision_value_framework_report.md`
Implementation: `src/research/decision_value_framework_engine.py`

---

# SCIENTIFIC CAUTION (Chief)

```text
Failing to show decision value under the CURRENT metrics does not prove primitives are useless.
It proves only that we have no evidence for them as signal / weighting / calibration
within the CURRENT architecture.
```

---

# MACHINE LEARNING — Still Deferred · ALPHA — Still Deferred

```text
No ML. No Alpha yet.
```

Alpha now waits on a different proof: a variable/structure with demonstrated **out-of-sample
decision value**, not merely predictive or explanatory value.

---

# UPDATED ROADMAP

```text
Phase 25     CLOSED   (Ecology Interaction; APPROVED; F-042 REJECTED; ecology = background; end of Market Understanding Era)
Phase 26     Decision Value Framework           NEXT     (PV/DV/XV scoreboard; decision audit; Decision Graph; no ML)
Phase 27     Decision-Aware Reality Validation  BLOCKED  (alpha on DV-variables only; OOS + FDR; Principle 40)
Phase 28     Machine Learning                   BLOCKED  (learns decision-relevant structure)
```

---

# STILL FORBIDDEN (until Chief approval)

```text
Hypothesis-chasing (reviving primitives) · Using primitives/ecology in decisions (no DV shown) ·
Findings with no decision value (flag for removal) · Alpha Reality Validation · ML · Portfolio Engine
```

Binding rules (Principles 18–57): … (carry-forward) … **primitives describe the environment**
(P53); **primitives belong to the ecological layer** (P54); **ecological description ≠ event
prediction** (P55); **ecology is a background property, not a discriminator** (P56); **primitives
are descriptive metadata until independent decision value is shown** (P57). Core findings:
representation survives OOS (Phase 21); events need different geometries (F-039); **F-041 & F-042
REJECTED**; the open gap is decision value, not market structure.

---

# CARRY-FORWARD (UNCHANGED)

All of V6.7 in force: F-016–F-040 (F-041/F-042 rejected), Principles 18–55, H-06, Event
Representation Family, Architecture V6, and "Profitable ≠ Tradable Edge".

---

# FINAL PRINCIPLE

```text
Ecology is the market's weather: background, not a chooser of events.
A primitive that changes nothing you decide is metadata, not knowledge.
We have understood the market enough; what we have not shown is which understanding changes a decision.
From here we measure everything by one question: does it change the decision, out of sample?

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DOCTRINE_V6.8.md**
