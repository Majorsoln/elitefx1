# ELITEFX_DOCTRINE_V5.6.md

**Chief Quant Amendment — Interactions, Not Individual Features**

Version: 5.6
Status: Superseded by V5.7 (current SSOT) — carry-forward in force
Date: 25 June 2026
Authority: Single Source of Truth (superseded by V5.7, 25 June 2026)
Supersedes: V5.5 (records F-012; inserts Interaction Engine; freezes Payoff Engine)
Previous Versions: Archived (V4, V4.1, V5.0, V5.1, V5.2, V5.3, V5.4, V5.5)

> ⚠️ **IMESASISHWA:** SSOT rasmi sasa ni **[ELITEFX DOCTRINE V5.7](ELITEFX%20DOCTRINE%20V5.7.md)**
> (F-013 State Age = Lifecycle Variable; Market Lifecycle Model; Market State
> Vector; three component categories). V5.6 carry-forward.

> Live program status lives in `docs/PROGRAM_BOARD.md`. This file is the doctrine
> of record; V5.0–V5.5 remain in force except where amended below.

---

# EXECUTIVE AMENDMENT

Phase 5.6 (`payoff_attribution_report.md`) decomposed the context score into
components and found volatility/activity dominant **marginally**. The Chief Quant
correction moves the project from *feature importance* to *market mechanism
modeling*:

```text
F-012  Market Opportunity Emerges from Feature INTERACTIONS,
       not Individual Features.
```

A component's marginal attribution number does **not** make it the key feature.
The market acts as `Volatility × Activity × Transition × Age` simultaneously, so
the edge may live in the **interaction**, not any single component.

---

# FINDING F-012 — Interactions, Not Individual Features

What Phase 5.6 measured was **marginal attribution**: change one component, see
how payoff moves. But:

```text
High Volatility            may be good.
High Volatility + Low Activity   may have NO edge.
High Volatility + Old State + Expansion Transition   may BE the edge.
```

Therefore (OFFICIAL):

```text
Single components do not explain Market Opportunity.
Interactions do.
```

Status: **APPROVED.** The Phase 5.6 conclusion ("build the Payoff Engine on these
components") is **rejected as premature** — interaction structure must be verified
first.

---

# DRIVER ≠ GATEKEEPER

A low marginal-importance component is not necessarily unimportant. Phase 5.6 put
Transition low (~11) — but Transition may be a **gate**, not a driver:

```text
Transition may say: "now, allow volatility to be used."
```

So importance score alone is insufficient. Doctrine distinguishes:

```text
Driver      — directly affects payoff size/odds.
Gatekeeper  — allows or blocks the environment in which payoff occurs.
```

A component can be a weak driver yet a strong gatekeeper. The Interaction Engine
must capture both roles.

---

# UPDATED ARCHITECTURE (Interaction Engine inserted)

```text
Volume Bars
↓
State Detection
↓
State Age
↓
Transition
↓
Interaction Engine        ← NEW (F-012)
↓
Context Score
↓
Event
↓
Payoff Distribution
↓
Trade Lifecycle
↓
Execution
```

The Context Score is now an **output of** the Interaction Engine, not a flat
blend of components.

---

# UPDATED ROADMAP

```text
Phase 5.6   Payoff Attribution           COMPLETE   (marginal; conclusion corrected by F-012)
Phase 5.7   Component Interaction         NEXT       (2-way + 3-way interactions, Tier 1)
Phase 6     Payoff Distribution Engine    FROZEN     (until interaction structure verified)
Phase 7     Trade Lifecycle Controller    BLOCKED
Phase 8     Machine Learning              BLOCKED    (predict distribution, not TP)
```

Revised direction:

```text
Payoff Engine → Interaction Engine → Distribution Engine
```

## Phase 5.7 — Component Interaction (NEXT)

For Tier-1 events, measure interaction structure before any engine is built:

```text
2-way:  Volatility × Activity · Volatility × Transition
        Activity × State Age · Transition × State Age
3-way:  Volatility × Activity × Transition
```

Per interaction cell: AvgWin · AvgLoss · EV · n. Key test: joint EV-spread vs
marginal spread (interaction adds discrimination?).

Deliverable: `component_interaction_report.md`
Implementation: `src/research/component_interaction.py`

The Payoff Engine (Phase 6) is **frozen** until this interaction structure is
verified — it must be built on interactions, not on a single component ranking.

---

# STILL FORBIDDEN (until Chief approval)

```text
Payoff Engine (Phase 6) · LightGBM · Random Forest · XGBoost · ML Models
```

---

# CARRY-FORWARD (UNCHANGED)

All of V5.5 remains in force: Findings F-001…F-011, R-001/R-002, Principles
01–03, 12, 13, Event Priority Tiers, payoff mechanism groups (F-011), the
Expected Payoff Engine output direction (F-010), and "Profitable ≠ Tradable Edge".

---

# FINAL PRINCIPLE

```text
Feature importance is not market mechanism.

The edge is in the interaction, not the feature.
Distinguish the Driver from the Gatekeeper.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DOCTRINE_V5.6.md**
