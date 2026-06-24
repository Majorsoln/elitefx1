# ELITEFX_DOCTRINE_V5.4.md

**Chief Quant Amendment — Event-Specific Context Sensitivity & Event Priority**

Version: 5.4
Status: APPROVED — ACTIVE (current SSOT)
Date: 24 June 2026
Authority: Single Source of Truth (SSOT)
Supersedes: V5.3 (records F-009; adds Event Priority Framework; opens Phase 5)
Previous Versions: Archived (V4, V4.1, V5.0, V5.1, V5.2, V5.3)

> Live program status (phases, ledger, approvals) lives in
> `docs/PROGRAM_BOARD.md`. This file is the doctrine of record; V5.0–V5.3 remain
> in force except where amended below.

---

# EXECUTIVE AMENDMENT

Phase 4 (`event_context_matrix_report.md`) produced the first map of *where edge
may hide*. It earned one finding and opened outcome research:

```text
F-009  Context Sensitivity Is Event-Specific
```

The Event Library is no longer one block. Events differ in how much they
respond to context ranking — and that difference now drives research priority.

---

# FINDING F-009 — Context Sensitivity Is Event-Specific

We began doctrine with: `Event = Unit of Opportunity`. Correct. But Phase 4
shows event QUALITY depends on **context sensitivity**:

```text
Event Quality depends on Context Sensitivity.
```

Measured by improvement = (Top-10% context EV) − (All EV), per event:

```text
Tier 1 (strong context benefit; Top10 EV > 0)
  Mean Reversion      +2.49
  Pullback            +2.47
  Deep Pullback       +2.14
  Trend Continuation  +2.11

Tier 2 (context helps, but EV still ≤ ~0)
  Breakout            +1.54
  Volatility Breakout +1.23
  News Shock          +0.95

Tier 3 (context fails)
  Volatility Expansion -0.15
  Pattern Completion   -0.81
```

Status: **APPROVED.** Q-006 CLOSED.

---

# EVENT PRIORITY FRAMEWORK

```text
Tier 1   (research priority — outcome candidates)
--------
Mean Reversion
Pullback
Deep Pullback
Trend Continuation

Tier 2   (context helps but insufficient alone)
--------
Breakout
Volatility Breakout
News Shock

Tier 3   (archived from edge research for now)
--------
Volatility Expansion
Pattern Completion
```

Consequence:

```text
Tier 1 Events  >  Tier 2 Events  >  Tier 3 Events
```

for context-interaction quality. Outcome research proceeds on **Tier 1 only**.
Tier 3 is archived from current edge research (not deleted — may return with a
better representation or context definition).

---

# CLARIFICATION — Profitable ≠ Tradable Edge (OFFICIAL)

Phase 4 showed 5/9 events with Top-10% EV > 0. This is **not edge yet**:

```text
Profitable  ≠  Tradable Edge
```

because there is still:

```text
• no full transaction-cost model
• no barrier labeling validated
• no walk-forward of outcome
• results are raw pips
```

A positive pip EV under context ranking is a **research candidate**, not a
deployable edge. This clarification is binding on all downstream phases.

---

# PHASE 5 OPENED — Triple Barrier Research (Tier 1 only)

For the first time, Triple Barrier outcome research is **APPROVED** — scoped to
Tier 1 events.

Deliverable: `triple_barrier_design_report.md`
Implementation: `src/research/triple_barrier_design.py`

Objective — build the outcome framework and answer:

```text
1. Barrier width?   k ∈ {0.5, 1.0, 1.5, 2.0} σ      (σ = ATR @ entry)
2. Vertical?        N ∈ {3, 5, 10, 20} bars
3. P(TP), P(SL), P(TIME)  per Tier-1 event
4. Do these probabilities change by CONTEXT DECILE?
```

Barriers are LOCKED at entry (no resizing — no look-ahead). Same-bar TP&SL
resolves to SL (conservative).

---

# UPDATED ROADMAP

```text
Phase 4     Event × Context Matrix       COMPLETE   (F-009)
Phase 5     Triple Barrier (Tier 1)      REOPENED   (P(TP) flat across deciles vs EV uplift)
Phase 5.5   Outcome Decomposition        NEXT       (P(win) vs AvgWin vs AvgLoss by decile)
Phase 6     Outcome Engine               BLOCKED
Phase 7     Trade Lifecycle Controller   BLOCKED
```

## Phase 5 Note — P(TP) ≠ Context (mechanism open)

Phase 5 delivered the triple-barrier design but **refuted an implicit
assumption**: context did **not** change P(TP) across deciles (mean_reversion
48% → 48%), even though Phase 4 showed large EV uplift. So the F-009 uplift is
**not** a win-probability effect. Likely it is payoff size / asymmetry
(consistent with Phase 1.9: win-rate flat, EV up). Phase 5.5 (Outcome
Decomposition) settles the mechanism before any Outcome Engine or ML. No new
finding (F-010) is recorded until the mechanism is known.

---

# STILL FORBIDDEN (until Chief approval)

```text
LightGBM · Random Forest · XGBoost · Outcome Models (ML)
```

Reason: first **Event + Context + Outcome** must be verified (Phases 4–5). No ML
searches for alpha before that triad is established on Tier-1 events.

---

# CARRY-FORWARD (UNCHANGED)

All of V5.3 remains in force: Findings F-001…F-008, R-001/R-002, Principles
01–03, 12 (Context Is A Filter) and 13 (Context Ranking), the
Volume→State→Age→Transition→Context-Score→Event-Ranking architecture, and the
EV-not-win-rate decision metric.

---

# FINAL PRINCIPLE

```text
Market → Context → Event → Outcome.

Not which event occurs,
but which events have better outcome odds
under specific context.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DOCTRINE_V5.4.md**
