# ELITEFX_DOCTRINE_V5.19.md

**Chief Quant — Does the Edge Even Exist? Prove It Beats Random Before Building Anything**

Version: 5.19
Status: APPROVED — ACTIVE (current SSOT)
Date: 27 June 2026
Authority: Single Source of Truth (SSOT)
Supersedes: V5.18 (F-027 APPROVED new wording; F-029; Principle 28; Edge Reality Validation inserted; Phase 11 Edge Reality Test)
Previous Versions: Archived (V4 … V5.18)

> Live program status lives in `docs/PROGRAM_BOARD.md`. This file is the doctrine
> of record; V5.0–V5.18 remain in force except where amended below.

---

# EXECUTIVE AMENDMENT — THE MOST FUNDAMENTAL QUESTION

Phase 10 answered the question the project has chased from the start:

```text
Can the edge we see today be trusted tomorrow?
```

The answer, by evidence (Spearman ≈ 0.03 between early quality and future survival):

```text
No.  Early performance ≠ Future persistence.
```

This is not because the edge is bad. It is because early quality carries no
information about future persistence. That forces a more fundamental question,
which is **not yet answered**:

```text
Does the edge even exist — or are we looking at random fluctuations?
```

We will not build an Opportunity Engine, adaptive system, or ML until we know.

---

# FINDING F-027 — APPROVED (reworded)

```text
Early Edge Quality does not predict Future Edge Persistence.
```

Upgraded **REFORMULATED → APPROVED**. The Phase 10 causal test (window-1 EV vs
survival, ρ ≈ +0.03) confirms it directly — and shows the Phase 9 whole-sample
correlation (ρ ≈ +0.74) was a same-sample artifact.

---

# A CAUTION — DO NOT ASSUME A HIDDEN VARIABLE

Phase 10 showed ATR, spread, and activity do **not** explain edge decay. But moving
from "these don't explain it" to "there must be a hidden variable" skips a
scientific step. There is a larger possibility that must be tested first.

---

# FINDING F-029 — Edge Decay May Be Stochastic (OPEN)

```text
Edge decay may be stochastic rather than deterministic.
```

An edge may not die because of some variable. It may die because market
participants change, liquidity changes, execution changes — or simply because it was
noise. The edge may be a **random process**, not a deterministic one. Status:
**OPEN — under test** (Phase 11).

---

# PRINCIPLE 28 — Prove Edge Beats Random Before Building (APPROVED)

```text
No adaptive system shall be built before proving that
persistent edge exists beyond random expectation.
```

This is now binding. ML, adaptive ranking, Opportunity Engine v2, and Portfolio
allocation are all blocked until Edge Reality is established.

---

# PHASE 11 — Edge Reality Test (NEXT)

Two hypotheses:

```text
H1: The market contains real persistent edges.
H0: The observed edge is sampling noise.
```

Using null models, permutation tests, and bootstrap:

```text
Q1. Null model — shuffle outcomes: does decay/survival look the same?
Q2. Randomized order — does survivability look the same?
Q3. Bootstrap — is observed decay outside the random-world confidence interval?
Q4. Permutation — are the Top survivors more than random expectation?
Q5. P(Observed Edge > Random Edge) for each event.
```

Deliverable: `reports/edge_reality_report.md`
Implementation: `src/research/edge_reality_engine.py`

---

# UPDATED ARCHITECTURE (official)

```text
Configuration
  ↓
Confidence Engine          (Quality — CCS)
  ↓
Edge Lifecycle Engine      (does the edge last?)
  ↓
Edge Reality Validation    ← Phase 11 (is the edge real, or noise?)
  ↓
Opportunity Engine         (only if edge is proven real)
  ↓
Portfolio Engine
```

Validation now precedes Opportunity. We validate that the edge is real before we
build anything that trades it.

---

# MACHINE LEARNING — Still Deferred (Principle 28)

```text
No ML.
```

If the edge is noise, ML would learn noise. Edge Reality first; everything else
after.

---

# UPDATED ROADMAP

```text
Phase 10     CLOSED   (Edge Drift; F-027 APPROVED; environment does not explain decay)
Phase 11     Edge Reality Test           NEXT     (H1 vs H0; null/permutation/bootstrap; no ML)
Phase 12     Opportunity Engine v2       BLOCKED  (only if H1 proven; Principle 28)
Phase 13     Portfolio Engine            BLOCKED
Phase 14     Machine Learning            BLOCKED
(parallel)   F-026 State Trajectory      OPEN     (only pursue if a hidden variable is justified)
```

---

# STILL FORBIDDEN (until Chief approval AND Edge Reality proven)

```text
Opportunity Engine v2 · Adaptive Ranking · Portfolio Engine · ML
```

Binding rules (Principles 18–28): … (carry-forward) … **prefer living edges over
historically profitable edges** (P27); **no adaptive system before proving
persistent edge beats random expectation** (P28). Core findings: bad configurations
persist more than good ones (F-022); every edge has a lifecycle (F-028); early edge
quality does not predict future persistence (F-027); edge may be non-stationary and
its decay possibly stochastic (F-029).

---

# CARRY-FORWARD (UNCHANGED)

All of V5.18 in force: F-016–F-028, Principles 18–27, H-06, the Configuration
architecture, Research Foundation closed, Adaptive Market Intelligence framing, and
"Profitable ≠ Tradable Edge".

---

# FINAL PRINCIPLE

```text
Before adaptation, before ML, before allocation —
prove the edge is real, not noise.

Early performance does not predict future persistence.
Decay may be stochastic. Do not assume a hidden variable until the data demands one.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DOCTRINE_V5.19.md**
