# ELITEFX_DOCTRINE_V5.20.md

**Chief Quant — Non-Stationarity Confirmed; Every Event Is a Hypothesis to Be Proven**

Version: 5.20
Status: Superseded by V5.21 (current SSOT) — carry-forward in force
Date: 28 June 2026
Authority: Single Source of Truth (superseded by V5.21, 28 June 2026)
Supersedes: V5.19 (F-029 APPROVED; Principle 29; Event Reality Validation in architecture; Phase 12 Event Reality Framework)
Previous Versions: Archived (V4 … V5.19)

> ⚠️ **IMESASISHWA:** SSOT rasmi sasa ni **[ELITEFX DOCTRINE V5.21](ELITEFX%20DOCTRINE%20V5.21.md)**
> (Principle 30 events are contextual; F-030 edge conditional; F-031 only contextual
> events exist; Event → Contextual Event; Proven Edge → Candidate Alpha; Contextual
> Event Library; Phase 13 Contextual Alpha Framework). V5.20 carry-forward.

> Live program status lives in `docs/PROGRAM_BOARD.md`. This file is the doctrine
> of record; V5.0–V5.19 remain in force except where amended below.

---

# EXECUTIVE AMENDMENT — TWO QUESTIONS, TWO ANSWERS

Phase 11 (Edge Reality Test) answered two distinct questions at once:

```text
A. Does an aggregate edge exist?   →  Not proven (H0 not rejected).
B. Is the market stationary?       →  No.
```

There is no contradiction. The strongest evidence came from the randomized-time
test:

```text
Observed survivors = 9     Randomized-time survivors = 39
```

Randomizing the order made persistence look *larger* than the real market. So the
market itself destroys persistence — the time-order is the cause of decay. That is
the strongest evidence to date that the market is non-stationary.

---

# FINDING F-029 — APPROVED (reworded)

```text
Edge decay is primarily a consequence of market non-stationarity,
not merely of random sampling.
```

Upgraded **OPEN → APPROVED**. Rationale: if decay were sampling noise alone,
randomizing the time-order would not change persistence so drastically. It did.

---

# MEAN REVERSION — NOT YET A PROJECT (a subgroup, not a proof)

Phase 11 showed mean_reversion with P(obs > random) = 100%. Tempting — but it is a
**subgroup** result vulnerable to small samples and multiple comparisons. Jumping to
a mean_reversion-only project would repeat the exact mistake CCS taught us. We do
**not** open a Mean Reversion project. We test **all** events under one framework.

---

# PRINCIPLE 29 — Every Event Is a Hypothesis (APPROVED)

```text
Every Event is a statistical hypothesis, not a trading signal.
```

An event does not earn a place in the Opportunity Engine because it "looks good." It
must first be **proven to exist** beyond random expectation.

---

# PHASE 12 — Event Reality Framework (NEXT)

Not a mean-reversion test — a framework that tests **every** event with the same
methodology (null models, permutation, bootstrap, and pair × event × state):

```text
Q1. Per event: null + bootstrap + permutation.
Q2. Bayesian probability that the edge exists (not just a p-value).
Q3. Does a particular pair carry the event? (pair × event)
Q4. Does event edge / survival depend on market state? (event × state)
Q5. Do two events combined produce edge? (combo vs solo)
```

Null = random direction (does the event's *direction* carry skill beyond chance,
net of spread). Proven = Bayesian P(edge>0) > 95% AND permutation p < 0.05 AND
bootstrap CI lower bound > 0.

Deliverable: `reports/event_reality_report.md`
Implementation: `src/research/event_reality_engine.py`

---

# UPDATED ARCHITECTURE (official)

```text
Market Data
  ↓
Event Library
  ↓
Event Reality Validation   ← Phase 12 (an event must be proven before anything else)
  ↓
Context Engine
  ↓
Opportunity Engine
  ↓
Portfolio Engine
```

An event must first be proven to exist before context, opportunity, or allocation
are built on it.

---

# MACHINE LEARNING — Still Deferred

```text
No ML.
```

We do not yet know which events are real. ML before that would learn unproven
hypotheses. Prove the events first.

---

# UPDATED ROADMAP

```text
Phase 11     CLOSED   (Edge Reality Test; H0 not rejected; F-029 confirmed)
Phase 12     Event Reality Framework     NEXT     (prove which events exist; no ML)
Phase 13     Opportunity Engine v2       BLOCKED  (only proven events; Principle 28/29)
Phase 14     Portfolio Engine            BLOCKED
Phase 15     Machine Learning            BLOCKED
(parallel)   F-026 State Trajectory      OPEN
```

---

# STILL FORBIDDEN (until Chief approval AND events proven)

```text
Opportunity Engine v2 · Adaptive Ranking · Portfolio Engine · ML
```

Binding rules (Principles 18–29): … (carry-forward) … **no adaptive system before
proving persistent edge beats random expectation** (P28); **every event is a
statistical hypothesis, not a trading signal** (P29). Core findings: every edge has
a lifecycle (F-028); early quality does not predict future persistence (F-027); edge
decay is driven by market non-stationarity (F-029).

---

# CARRY-FORWARD (UNCHANGED)

All of V5.19 in force: F-016–F-028, Principles 18–28, H-06, the Configuration
architecture, Research Foundation closed, Edge Reality Validation, Adaptive Market
Intelligence framing, and "Profitable ≠ Tradable Edge".

---

# FINAL PRINCIPLE

```text
The market is non-stationary; the time-order itself destroys persistence.
Every event is a hypothesis to be proven, not a signal to be traded.
No subgroup becomes doctrine before it survives a full, fair test.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DOCTRINE_V5.20.md**
