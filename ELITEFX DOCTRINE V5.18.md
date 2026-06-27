# ELITEFX_DOCTRINE_V5.18.md

**Chief Quant — Every Edge Has a Lifecycle; Edge Is Non-Stationary; Find Out WHY It Dies**

Version: 5.18
Status: APPROVED — ACTIVE (current SSOT)
Date: 27 June 2026
Authority: Single Source of Truth (SSOT)
Supersedes: V5.17 (Survivability Engine → Edge Lifecycle Engine; F-027 REFORMULATED; F-028; Principle 27; Phase 10 Edge Drift Engine)
Previous Versions: Archived (V4 … V5.17)

> Live program status lives in `docs/PROGRAM_BOARD.md`. This file is the doctrine
> of record; V5.0–V5.17 remain in force except where amended below.

---

# EXECUTIVE AMENDMENT — EDGE IS NON-STATIONARY

Phase 9 (Edge Lifecycle Engine) revealed the deepest finding of the project so far:

```text
Edge is non-stationary.
```

Phase 8 did not fail because CCS was bad. It failed because the assumption that
market edge is **stationary** is false:

```text
Median survival = 1 window  (≈ 229 trades)
Only ~2% of configurations stayed positive across all 6 windows.
```

This is not a failure of CCS. It is the rejection of a hidden assumption. And it is
the project's biggest discovery.

But Phase 9 showed **WHEN** an edge dies, not **WHY**. Without the cause, adaptive
ranking would only be another form of curve-fitting. So the next step is not
adaptation — it is **explanation**.

---

# SURVIVABILITY ENGINE → EDGE LIFECYCLE ENGINE (renamed)

Survivability is a single metric. The phenomenon is a **framework**:

```text
Birth → Growth → Decay → Death
```

Institutional desks do not say "the edge survived." They say the edge **matured**,
**decayed**, **disappeared**. The Phase 9 component (`survivability_engine.py`)
remains the first metric within the **Edge Lifecycle Engine**; the framework — not
the single survival rate — is what the Opportunity Engine consumes.

---

# FINDING F-028 — Every Trading Edge Has a Lifecycle (APPROVED)

```text
Every trading edge has a lifecycle.
```

Directly confirmed by Phase 9 (birth → growth → decay → death; median survival of
one window; clear decay slope). Status: **APPROVED**.

---

# FINDING F-027 — REFORMULATED (causal, not descriptive)

The Phase 9 correlation between survivability and EV/CCS (ρ ≈ +0.74–0.79) came from
the **same sample** — a descriptive coupling, not a causal test. F-027 is therefore
**not closed and not rejected — it is REFORMULATED**:

```text
WAS:  Survivability is independent from Quality.
NOW:  Early Quality may not predict Future Survivability.
```

This is the correct hypothesis, and the Phase 9 decay evidence already points to it
(window-1 edge does not predict window-2+). It must be tested in a **causal /
temporal** setting (early quality → future survival), not whole-sample correlation.

---

# PRINCIPLE 27 — Prefer Living Edges

```text
The Opportunity Engine shall prefer living edges
over historically profitable edges.
```

A historically profitable configuration is not tradeable if its edge is already in
decay. Living edge > historical edge.

---

# PHASE 10 — Edge Drift Engine (NEXT)

The window index tells us *when*, not *why*. The next question is: **what changed
between the window where the edge lived and the window where it died?** (The
configuration's state labels are fixed, but the absolute environment — ATR, spread,
activity — drifts because states are relative.)

```text
Q1. Did the edge die because regime / volatility / spread / activity / event-mix changed?
Q2. For each dead configuration, show Before → After (volatility, activity, spread, latent, regime).
Q3. Are there transitions that recur before an edge dies?
Q4. Can edge death be predicted one window in advance?   ← the key question
Q5. Do some events have longer lifespans than others — and WHY (not just "which leads")?
```

Deliverable: `reports/edge_drift_report.md`
Implementation: `src/research/edge_drift_engine.py`

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
Edge Lifecycle Engine      ← Phase 9 (survivability) + Phase 10 (drift = WHY)
  ↓
Opportunity Engine         (prefer living edges; remove dying/bad; rank; )
  ↓
Portfolio Engine           (allocation)
  ↓
Execution Engine
```

---

# MACHINE LEARNING — Still Deferred (and now we know why)

```text
No ML.
```

ML trained before we understand market adaptation would be trained on **historical
corpses** — dead edges. ML comes only after we can describe how and why edges drift.

---

# THE PROJECT, REFRAMED

We are no longer only building an Opportunity Engine. We are building an **Adaptive
Market Intelligence System**. The real problem the data exposed is not "which trade
is good?" but:

```text
"When does an edge begin to die, and why?"
```

Answer that, and the Opportunity Engine, Portfolio Engine, and ML are all built on
an understanding of market change, not on history alone.

---

# UPDATED ROADMAP

```text
Phase 9      CLOSED   (Edge Lifecycle Engine; F-028; edge non-stationary)
Phase 10     Edge Drift Engine           NEXT     (WHY edge dies; F-027 causal; predict death; no ML)
Phase 11     Opportunity Engine v2       BLOCKED  (lifecycle-aware: prefer living, remove dying)
Phase 12     Portfolio Engine            BLOCKED  (allocation)
Phase 13     Machine Learning            BLOCKED  (after market-adaptation understood)
(parallel)   F-026 State Trajectory      OPEN     (state momentum — related to drift)
```

---

# STILL FORBIDDEN (until Chief approval)

```text
Opportunity Engine v2 · Portfolio Engine · Execution Engine · ML
```

Binding rules (Principles 18–27): … (carry-forward) … **Opportunity = Quality ×
Availability × Survivability** (P25); **capital preservation before opportunity
discovery** (P26); **prefer living edges over historically profitable edges** (P27).
Core Principle: bad configurations persist more than good ones (F-022). Core
finding: every edge has a lifecycle (F-028); edge is non-stationary.

---

# CARRY-FORWARD (UNCHANGED)

All of V5.17 in force: F-016–F-026 (F-027 reformulated), Principles 18–26, H-06,
the Configuration architecture, Research Foundation closed, F-022 as Core Principle,
and "Profitable ≠ Tradable Edge".

---

# FINAL PRINCIPLE

```text
Edge is non-stationary; every edge has a lifecycle.
We find out WHEN it dies, then WHY — explanation before adaptation.
Prefer living edges over historical ones.

We are building an Adaptive Market Intelligence System,
not just a trade picker.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DOCTRINE_V5.18.md**
