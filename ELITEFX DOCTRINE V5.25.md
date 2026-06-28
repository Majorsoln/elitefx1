# ELITEFX_DOCTRINE_V5.25.md

**Chief Quant — Events Are the Semantic Anchor; Each Event Has Its Own Context**

Version: 5.25
Status: APPROVED — ACTIVE (current SSOT)
Date: 28 June 2026
Authority: Single Source of Truth (SSOT)
Supersedes: V5.24 (F-035; Principle 36, 37; Event → Context architecture; Phase 16 hierarchy wording corrected; Phase 17 Event-Centric Representation)
Previous Versions: Archived (V4 … V5.24)

> Live program status lives in `docs/PROGRAM_BOARD.md`. This file is the doctrine
> of record; V5.0–V5.24 remain in force except where amended below.

---

# EXECUTIVE AMENDMENT — A REAL DISCOVERY (FROM DATA, NOT INTUITION)

Phase 16 is the first report since Phase 14 to change the architecture by **evidence**,
not intuition. Its Q5 interaction table is the discovery:

```text
Event × Trajectory   ✅        Age × Transition        ❌
Event × Volatility   ✅        Age × Trajectory        ❌
Activity × Event     ✅        Transition × Trajectory ❌
```

State variables do **not** build a self-standing internal hierarchy. Trajectory (and
Activity, Volatility) acquire meaning only **when attached to an Event**.

```text
OLD (intuition):  State → Age → Transition → Trajectory → Event
NEW (data):       Event → Context     (each Event has its own Context)
```

---

# FINDING F-035 — State Variables Derive Meaning Through Events (APPROVED)

```text
Market state variables derive meaning primarily through their interaction
with Events, not through their interaction with one another.
```

---

# PRINCIPLE 36 — Events Are the Semantic Anchors (APPROVED)

```text
Events are the semantic anchors of market representation.
Context variables acquire value only when attached to an Event.
```

The market does not say "volatility is HIGH." It says "breakout while volatility is
rising" or "mean reversion while activity is low." The Event is the anchor.

---

# PRINCIPLE 37 — Significance Over Effect Size in Low S/N (APPROVED)

The surviving interactions had tiny incremental R² (≈ +0.00002 … +0.00015) yet were
statistically significant. In forex the signal-to-noise ratio is very low, so R²
gains will always be small while decision quality can change a lot.

```text
In low signal-to-noise markets, representation hypotheses shall be evaluated
primarily by robust statistical evidence and out-of-sample repeatability,
not by effect size alone.
```

Caveat: significance alone is insufficient — it must be paired with OOS validation.

---

# PHASE 16 — HIERARCHY WORDING CORRECTED

The Phase 16 hierarchy verdict is amended from "hierarchy not confirmed" to:

```text
Standalone hierarchy showed no incremental information;
the hierarchy attached to an Event is where the information appears.
```

The hierarchy was not falsified — it was measured **outside its environment** (without
the Event anchor).

---

# PHASE 17 — Event-Centric Representation (NEXT)

We no longer force one representation for all events. Build **event-specific**
representations:

```text
Q1. Is the Event truly the semantic anchor of representation?
Q2. For each Event, which contexts add information (Trajectory, Activity, Volatility, …)?
Q3. Are there context variables valuable for one Event but not another?
Q4. Can we build a minimal event-specific representation instead of one for all events?
Q5. Should Mean Reversion's representation differ from Breakout's?
```

Deliverable: `reports/event_centric_representation_report.md`
Implementation: `src/research/event_centric_representation_engine.py`

---

# UPDATED ARCHITECTURE (official)

```text
Event (semantic anchor)
  ↓
Event-specific Context (only the variables that matter for THAT event)
  ↓
Event Reality Validation  (per-event, OOS + FDR — Principle 37)
  ↓
Opportunity Engine
  ↓
Portfolio Engine
```

---

# MACHINE LEARNING — Still Deferred

```text
No ML.
```

First build event-specific representations and confirm them OOS. ML afterward.

---

# UPDATED ROADMAP

```text
Phase 16     CLOSED   (Interaction Audit; F-035; Event × context, not context × context)
Phase 17     Event-Centric Representation  NEXT   (per-event context; minimal event-specific reps; no ML)
Phase 18     Event-Specific Confirmation   BLOCKED (per-event OOS + FDR; Principle 37)
Phase 19     Opportunity Engine v2         BLOCKED
Phase 20     Machine Learning              BLOCKED
```

---

# STILL FORBIDDEN (until Chief approval)

```text
One representation for all events · More data · Opportunity Engine v2 · ML
```

Binding rules (Principles 18–37): … (carry-forward) … **contribution via interaction/
calibration/stability** (P34); **representation ≠ predictive gain** (P35); **Events are
the semantic anchors; context acquires value only attached to an Event** (P36);
**significance + OOS over effect size in low S/N** (P37). Core findings: hierarchical
redundancy is expected (F-034); state variables derive meaning through Events (F-035).

---

# CARRY-FORWARD (UNCHANGED)

All of V5.24 in force: F-016–F-034, Principles 18–35, H-06, Research Foundation
closed, Contextual Event Library, Confirmation Framework, and "Profitable ≠ Tradable
Edge".

---

# FINAL PRINCIPLE

```text
The Event is the anchor; context only means something attached to it.
Each Event has its own context — one representation for all events was the gap.
In a noisy market, trust significance and out-of-sample repeatability, not effect size.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DOCTRINE_V5.25.md**
