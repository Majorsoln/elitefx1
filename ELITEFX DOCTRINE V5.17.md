# ELITEFX_DOCTRINE_V5.17.md

**Chief Quant — Capital Preservation First; Survivability as a Third Dimension of Edge**

Version: 5.17
Status: APPROVED — ACTIVE (current SSOT)
Date: 27 June 2026
Authority: Single Source of Truth (SSOT)
Supersedes: V5.16 (F-022 → Core Principle; Principle 26 capital preservation; Principle 25 enhanced with Survivability; F-027; Opportunity Engine reframed; Survivability Engine; full architecture)
Previous Versions: Archived (V4 … V5.16)

> Live program status lives in `docs/PROGRAM_BOARD.md`. This file is the doctrine
> of record; V5.0–V5.16 remain in force except where amended below.

---

# EXECUTIVE AMENDMENT — A HYPOTHESIS REJECTED BY DATA

Phase 8 (Opportunity Engine) did the most important thing in quantitative research:
**it rejected our own hypothesis with evidence.**

```text
trade-all     = −1.122 pips/trade
CCS-selected  = −0.757 pips/trade   (improved, but still losing)
Top 5% by train-CCS = −1.162        (the "best" became the worst out-of-sample)
```

We believed high-CCS configurations would stay good out-of-sample. They did not.
This is not an implementation error — it is a rejected hypothesis. **In Quant
Research, when a hypothesis is rejected, the doctrine changes, not the data.**

---

# OPPORTUNITY ENGINE — REFRAMED

The Opportunity Engine is no longer "choose the best trades." It becomes:

```text
OLD:  Opportunity Engine → Choose Best Trades

NEW:  Opportunity Engine
        ↓
      Remove Bad Opportunities
        ↓
      Rank Remaining Opportunities
        ↓
      Portfolio Allocation
```

Institutional desks do not make money by finding good trades; they make money by
**removing bad trades first.**

---

# F-022 — PROMOTED TO CORE PRINCIPLE

F-022 (bad configurations are more persistent than good ones) was an observation.
Phase 8 showed positive ranking does not survive out-of-sample while the negative
edge persists. F-022 is therefore **promoted from Finding to Core Principle.**

---

# PRINCIPLE 26 — Capital Preservation First (APPROVED)

```text
The first responsibility of the Opportunity Engine
is capital preservation, not opportunity discovery.
```

The Opportunity Engine must first answer **"Where should we NOT trade?"** and only
then **"Where should we trade?"**

---

# PRINCIPLE 25 — Enhanced with Survivability

CCS measured Quality. OppScore added Availability. Phase 8 showed both are still
insufficient. A third dimension is required:

```text
Opportunity = Quality × Availability × Survivability
```

**Survivability** answers neither "was it good?" nor "how often did it occur?" but:

```text
"Did it STAY good over time?"
```

---

# FINDING F-027 — Survivability May Be Independent of Quality (OPEN)

```text
Configuration Survivability is independent from Configuration Quality.
```

Phase 8 hinted at it (high in-sample quality did not predict out-of-sample
performance). Status: **OPEN — under test** (Phase 9 Survivability Engine; measured
as the correlation between survivability and EV/CCS — low correlation ⇒ independent
dimension).

---

# PHASE 9 — Survivability Engine (NEXT)

For each Configuration, using **many rolling walk-forwards** (not a single 70/30
split), answer:

```text
1. Which configurations survive well across many rolling windows?
2. What is the median survival time of an edge?
3. After how many trades / how much time does edge decay begin?
4. Is survivability predictable from state, regime, event, or context?
5. Are there configurations with modest EV but high survivability —
   better for a long-term portfolio?
```

Deliverable: `reports/survivability_engine_report.md`
Implementation: `src/research/survivability_engine.py`

---

# UPDATED ARCHITECTURE (official)

```text
Market Data
  ↓
Event Library
  ↓
Context Engine
  ↓
Configuration Engine
  ↓
Confidence Engine          (Quality — CCS)
  ↓
Survivability Engine       ← Phase 9 (does the edge last?)
  ↓
Opportunity Engine         (remove bad → rank survivable → )
  ↓
Portfolio Engine           (allocation)
  ↓
Execution Engine
```

---

# MACHINE LEARNING — Still Deferred

No ML, no new indicators, no new entries. The next step is not alpha discovery; it
is to learn which configurations **last**. ML (learning the Configuration Score)
comes only after survivability is understood.

---

# UPDATED ROADMAP

```text
Phase 8      CLOSED   (Opportunity Engine; hypothesis rejected; reframed remove-bad-first)
Phase 9      Survivability Engine        NEXT     (rolling WF; durability; F-027; no ML)
Phase 10     Opportunity Engine v2       BLOCKED  (remove bad → rank survivable → allocate)
Phase 11     Portfolio Engine            BLOCKED  (allocation)
Phase 12     Machine Learning            BLOCKED  (learns Configuration Score)
(parallel)   F-026 State Trajectory      OPEN     (state momentum)
```

---

# STILL FORBIDDEN (until Chief approval)

```text
Opportunity Engine v2 · Portfolio Engine · Execution Engine · ML
```

Binding rules (Principles 18–26): decision quality over algorithm agreement (P18);
survival = EV/decision-quality improvement (P19); feature competition (P20);
selection over prediction (P21); opportunity = Configuration, never an Event (P22);
rank Configurations, don't classify Trades (P23); no ranking by Expected Payoff
alone (P24); **Opportunity = Quality × Availability × Survivability** (P25);
**capital preservation before opportunity discovery** (P26). Core Principle: bad
configurations persist more than good ones (F-022).

---

# CARRY-FORWARD (UNCHANGED)

All of V5.16 in force: F-016–F-026, Principles 18–25, H-06 (rare = execution risk),
the Configuration architecture, Research Foundation closed, F-025 (Magnitude +
Availability), and "Profitable ≠ Tradable Edge".

---

# FINAL PRINCIPLE

```text
When data rejects a hypothesis, the doctrine changes — not the data.

Protect capital before seeking alpha: remove bad first, then rank.
Edge is Quality × Availability × Survivability.
A good configuration is not the same as a configuration that lasts.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DOCTRINE_V5.17.md**
