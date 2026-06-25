# ELITEFX_DOCTRINE_V5.7.md

**Chief Quant Amendment — Market Lifecycle Model**

Version: 5.7
Status: APPROVED — ACTIVE (current SSOT)
Date: 25 June 2026
Authority: Single Source of Truth (SSOT)
Supersedes: V5.6 (records F-013; Lifecycle Model; Market State Vector)
Previous Versions: Archived (V4, V4.1, V5.0, V5.1, V5.2, V5.3, V5.4, V5.5, V5.6)

> Live program status lives in `docs/PROGRAM_BOARD.md`. This file is the doctrine
> of record; V5.0–V5.6 remain in force except where amended below.

---

# EXECUTIVE AMENDMENT

Phase 5.7 (`component_interaction_report.md`) confirmed F-012 (16/16 interactions
beat marginals) — but reading the structure revealed something deeper. The
biggest joint spreads were in **Transition × State Age** (6–7 pips), and the
pattern was not a simple interaction:

```text
Mean Reversion · Transition × Age
  Thi · 4–8   → +3.0
  Thi · 16+   → −3.2
```

The same Transition flips sign depending on the age of the state. This is a
**sequential / lifecycle** effect: the market has memory, not just state.

```text
F-013  State Age is a LIFECYCLE variable, not a TIME variable.
```

---

# FINDING F-013 — State Age Is a Lifecycle Variable

```text
Age 12 in Expansion  ≠  Age 12 in Compression.
```

The same numeric age means different things at different lifecycle stages.
Therefore age cannot be used as a bare numeric feature:

```text
WRONG:  Age = numeric feature
RIGHT:  Age = lifecycle encoding (stage of the regime's life)
```

Architecture gains a layer:

```text
State → Age → Transition → Lifecycle Stage
```

Status: **APPROVED.**

---

# THREE COMPONENT CATEGORIES

V5.6 introduced Driver ≠ Gatekeeper. F-013 adds a third role. Components are no
longer interchangeable features; each plays a distinct role:

```text
Drivers            change the payoff.            e.g. Volatility
Gatekeepers        allow/block the setup.        e.g. Transition
Lifecycle Variables decide the market stage.     e.g. State Age
```

Transition is both a **Gatekeeper** and a **Routing Variable** — it routes which
driver is allowed to act ("now, allow volatility to be used"). A weak marginal
score does not make it unimportant.

---

# MARKET LIFECYCLE MODEL

The market is no longer described as a **Regime** alone:

```text
Market = Regime + Lifecycle Stage + Transition Gate
```

State, Age and Transition are parts of **one market-lifecycle system**, not
independent features.

## Context Engine → Market State Vector

The Context Engine no longer emits a flat "Context Score". It emits a **Market
State Vector**:

```text
Market State Vector = {
  Volatility, Activity, Spread,
  Transition, Lifecycle, Interaction
}
```

A score, when needed, is an **output** of this vector — not the input.

---

# UPDATED ARCHITECTURE

```text
Market
↓
State Detection
↓
Lifecycle Modeling          ← F-013
↓
Transition Routing          ← Gatekeeper/Routing
↓
Interaction Engine          ← F-012 (pending stability, Phase 5.8)
↓
Market State Vector
↓
Event Evaluation
↓
Payoff Distribution
↓
Trade Lifecycle Controller
↓
Execution
```

---

# UPDATED ROADMAP

```text
Phase 5.7   Component Interaction         COMPLETE   (F-012 confirmed; F-013 discovered)
Phase 5.8   Interaction Stability         NEXT       (universal vs local — cross-market)
Phase 5.9   Market State Vector           QUEUED     (assemble the vector)
Phase 6     Interaction Engine            BLOCKED    (needs stable interactions)
Phase 7     Payoff Engine                 BLOCKED
Phase 8     Machine Learning              BLOCKED
```

## Phase 5.8 — Interaction Stability (NEXT)

Phase 5.7 found strong interaction cells but did **not** test whether they hold
across markets. Before any Interaction Engine, interactions must be
**generalizable**:

```text
Is HIGH×HIGH×Tmid best on EURUSD also best on GBPUSD — or local coincidence?
```

For each interaction, measure cross-pair consistency (coefficient of variation,
rank consistency / Spearman, modal best cell):

```text
Stable   → Universal Rule  (Interaction Engine = rules)
Unstable → Adaptive Rule   (Interaction Engine = per-pair adaptive)
```

Deliverable: `interaction_stability_report.md`
Implementation: `src/research/interaction_stability.py`

---

# STILL FORBIDDEN (until Chief approval)

```text
Interaction Engine · Payoff Engine · LightGBM · Random Forest · XGBoost · ML
```

The Interaction Engine itself is blocked until Phase 5.8 proves the interactions
generalize.

---

# CARRY-FORWARD (UNCHANGED)

All of V5.6 remains in force: Findings F-001…F-012, R-001/R-002, Principles
01–03, 12, 13, Event Priority Tiers, payoff mechanism groups, the
Driver ≠ Gatekeeper distinction, and "Profitable ≠ Tradable Edge".

---

# FINAL PRINCIPLE

```text
The market has memory, not just state.

State + Age + Transition are one lifecycle system,
not independent features.

Age is a stage of life, not a number.
Distinguish Driver, Gatekeeper, and Lifecycle.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DOCTRINE_V5.7.md**
