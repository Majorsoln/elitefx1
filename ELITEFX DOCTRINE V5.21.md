# ELITEFX_DOCTRINE_V5.21.md

**Chief Quant — Events Are Contextual; Edge Existence Is Conditional, Not Universal**

Version: 5.21
Status: Superseded by V5.22 (current SSOT) — carry-forward in force
Date: 28 June 2026
Authority: Single Source of Truth (superseded by V5.22, 28 June 2026)
Supersedes: V5.20 (Principle 30; F-030; F-031; Event → Contextual Event; Proven Edge → Candidate Alpha; Contextual Event Library; Phase 13 Contextual Alpha Framework)
Previous Versions: Archived (V4 … V5.20)

> ⚠️ **IMESASISHWA:** SSOT rasmi sasa ni **[ELITEFX DOCTRINE V5.22](ELITEFX%20DOCTRINE%20V5.22.md)**
> (Phase 13 = exploratory; Principle 31 hypothesis-until-prospective-validation;
> Principle 32 identity needs independent explanatory power; F-032 refinement raises
> false-discovery; Candidate Alpha → Contextual Alpha Hypothesis; Phase 14 Confirmation
> Framework). V5.21 carry-forward.

> Live program status lives in `docs/PROGRAM_BOARD.md`. This file is the doctrine
> of record; V5.0–V5.20 remain in force except where amended below.

---

# EXECUTIVE AMENDMENT — THE BIGGEST DOCTRINE CHANGE SINCE PHASE 1

Phase 12 did not show an edge. It exposed a **logic gap** the doctrine never had.

```text
Aggregate event        → no tradeable edge (0/5).
Mean Reversion × EURUSD → +0.90.   Deep Pullback × EURUSD → +0.37.
```

The naive reading is "we found an edge." The correct reading is deeper: **an event
is not universal — it is a conditional object.** We were asking the wrong question:

```text
WRONG:  "Does Mean Reversion have an edge?"
RIGHT:  "What market ecology creates a Mean Reversion with an edge?"
```

That is the difference between **event taxonomy** and **alpha taxonomy**.

---

# CONTEXT IS NOT A FILTER — IT IS IDENTITY

Our old doctrine had `Event → Context`, where context was a *filter*. That was the
gap. Context is part of the event's **identity**:

```text
Event ≠ Event          (without its context)
```

So the concept "Event" is replaced by **Contextual Event**. No event lives alone:

```text
Mean Reversion + Pair + State + Regime + Liquidity + Execution
```

That is the entity.

---

# PRINCIPLE 30 — Events Are Contextual (APPROVED)

```text
An Event does not exist independently of its market context.
```

---

# FINDING F-030 — Edge Existence Is Conditional (APPROVED)

```text
Edge existence is conditional, not universal.
```

Phase 12 confirmed it directly: aggregate events show no edge, yet specific contexts
(EURUSD) do.

# FINDING F-031 — Only Contextual Events Exist (APPROVED)

```text
Universal Events do not exist. Only Contextual Events exist.
```

---

# TERMINOLOGY (binding)

```text
Event        →  Contextual Event
Proven Edge  →  Candidate Alpha   (until pre-registered OOS validation)
```

The EURUSD findings (Mean Reversion +0.90, Deep Pullback +0.37) are **Candidate
Alpha**, NOT Proven Edge — multiple comparisons remain; they must survive a
pre-registered out-of-sample test before any "APPROVED" status.

---

# SPREAD IS ECOLOGY, NOT JUST COST

The implementer said "spread eats the edge." Half true — that is a symptom, not the
discovery. Spread is itself part of the **context/ecology**, not merely a cost. It is
an ecology variable that helps define the Contextual Event.

---

# ARCHITECTURE — Contextual Event Library

```text
OLD:  Event Library → Context Engine

NEW:  Contextual Event Library
        ↓
      Event Reality Validation
        ↓
      Opportunity Engine        (selects Contextual Alpha Objects, not events)
        ↓
      Portfolio Engine
```

An event is born *with* its context; context is not added later.

---

# PHASE 13 — Contextual Alpha Framework (NEXT)

We no longer search for events. We search for **Contextual Alpha Objects**:

```text
Q1. For each Contextual Event: Pair + State + Regime + Liquidity + Execution + Session,
    with probability of edge.
Q2. Remove Pair  — does the edge disappear?
Q3. Remove State — does the edge disappear?
Q4. Which variables are part of IDENTITY, and which are MODIFIERS?  (key question)
Q5. Build a hierarchy (event → pair → vol → spread → session): where is the alpha —
    the full stack, or the pair alone?
```

Candidate Alpha = Bayesian P(edge>0) > 95% AND null (random-direction) p < 0.05 AND
bootstrap CI lower bound > 0 — and still flagged Candidate (multiple comparisons).

Deliverable: `reports/contextual_alpha_report.md`
Implementation: `src/research/contextual_alpha_engine.py`

---

# MACHINE LEARNING — Still Deferred

```text
No ML.
```

We will not open a "Mean Reversion Strategy" (repeating the subgroup mistake). ML
comes only after Contextual Alpha Objects are validated out-of-sample.

---

# UPDATED ROADMAP

```text
Phase 12     CLOSED   (Event Reality; 0/5 universal; EURUSD candidates; F-030/F-031)
Phase 13     Contextual Alpha Framework  NEXT     (Contextual Alpha Objects; identity vs modifier; no ML)
Phase 14     Pre-registered OOS Validation BLOCKED (confirm Candidate Alpha out-of-sample)
Phase 15     Opportunity Engine v2       BLOCKED  (selects validated Contextual Alpha)
Phase 16     Portfolio Engine            BLOCKED
Phase 17     Machine Learning            BLOCKED
```

---

# STILL FORBIDDEN (until Chief approval AND OOS validation)

```text
Mean Reversion Strategy · Opportunity Engine v2 · Portfolio Engine · ML
```

Binding rules (Principles 18–30): … (carry-forward) … **every event is a statistical
hypothesis** (P29); **an event does not exist independently of its market context**
(P30). Core findings: edge existence is conditional (F-030); only contextual events
exist (F-031); edge decay is driven by non-stationarity (F-029).

---

# CARRY-FORWARD (UNCHANGED)

All of V5.20 in force: F-016–F-029, Principles 18–29, H-06, Research Foundation
closed, Edge/Event Reality Validation, Adaptive Market Intelligence framing, and
"Profitable ≠ Tradable Edge".

---

# FINAL PRINCIPLE

```text
We were asking the wrong question.
Not "does this event have an edge?" but "what ecology creates an edge?"

Events are contextual; edge is conditional, not universal.
Context is identity, not a filter. Spread is ecology, not just cost.
A candidate is not an edge until it survives out-of-sample.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DOCTRINE_V5.21.md**
