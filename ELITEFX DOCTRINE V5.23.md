# ELITEFX_DOCTRINE_V5.23.md

**Chief Quant — Validation Failure Is Representation Failure, Not Absence of Alpha**

Version: 5.23
Status: Superseded by V5.24 (current SSOT) — carry-forward in force
Date: 28 June 2026
Authority: Single Source of Truth (superseded by V5.24, 28 June 2026)
Supersedes: V5.22 (F-032 Confirmed; Principle 33; F-033; Phase 14 reframed as Representation Failure; Phase 15 Representation Audit)
Previous Versions: Archived (V4 … V5.22)

> ⚠️ **IMESASISHWA:** SSOT rasmi sasa ni **[ELITEFX DOCTRINE V5.24](ELITEFX%20DOCTRINE%20V5.24.md)**
> (Phase 15 verdict REJECTED — standalone ≠ hierarchy; Principle 34 contribution via
> interaction/calibration/stability; Principle 35 representation ≠ predictive gain;
> F-034 hierarchical redundancy expected; Phase 16 Representation Interaction Audit).
> V5.23 carry-forward.

> Live program status lives in `docs/PROGRAM_BOARD.md`. This file is the doctrine
> of record; V5.0–V5.22 remain in force except where amended below.

---

# EXECUTIVE AMENDMENT — A FAILURE WORTH MORE THAN A FALSE EDGE

Phase 14 (Confirmation) was the first report to reject **our own** hypotheses
correctly:

```text
282 hypotheses pre-registered → UNKNOWN removed → future OOS → Benjamini–Hochberg FDR
→ 0 survived.
```

Scientifically this is worth more than a report claiming alpha. It stopped us from
building on false discoveries. **F-032 is now Confirmed** (Phase 13: 30 "good" →
Phase 14: 0 after FDR = the definition of selection inflation).

But the implementer's conclusion ("no alpha; need new ecology or more data") is
**premature** and is rejected. There is a critical distinction:

```text
Science does not say "alpha does not exist."
Science says "we do not yet have sufficient evidence."
```

---

# THE REAL FINDING — CURRENT REPRESENTATION FAILURE

We tested **one** representation: `Event + Pair + Vol + Spread + Session`. The
doctrine contains many variables never yet combined into the representation: state
trajectory, state age, regime transition, opportunity persistence, event sequencing,
market memory, execution timing. So the Phase 14 null result is not "No Alpha" — it
is **Current Representation Failure**.

---

# PRINCIPLE 33 — Validation Failure ⇒ Representation Failure (APPROVED)

```text
Failure to validate an alpha hypothesis does not imply absence of alpha;
it implies failure of the current representation until proven otherwise.
```

# FINDING F-033 — A Representation Can Fail While Structure Exists (APPROVED)

```text
A representation can fail while the underlying market
still contains exploitable structure.
```

---

# PHASE 15 — Representation Audit (NEXT)

Before adding data, complexity, or ML, we must prove the **current representation has
reached its limit**. That has not been shown. No ML, no new data, no new strategy —
audit the representation itself:

```text
1. What hidden assumptions are baked into the current representation?
2. Which doctrine variables are not yet included?
3. Do state age / trajectory / transition / persistence / activity add INCREMENTAL
   information over Event + Pair + Vol + Spread + Session?
4. Is there redundancy among the existing variables?
5. What is the minimal sufficient representation — all the information, no added noise?
```

Method: variance-of-outcome explained (R²), incremental R² controlled by a
permutation null (removes cardinality-overfit), Cramér's V for redundancy, greedy
forward selection for the minimal sufficient set.

Deliverable: `reports/representation_audit_report.md`
Implementation: `src/research/representation_audit_engine.py`

---

# MACHINE LEARNING / MORE DATA — Both Deferred

```text
No ML. No more data. No new strategy.
```

The next decision — representation, data, or genuinely no provable edge — can only be
made after the Representation Audit shows whether the current representation is at its
limit.

---

# UPDATED ROADMAP

```text
Phase 14     CLOSED   (Confirmation; 0 survived FDR; F-032 confirmed; representation failure)
Phase 15     Representation Audit        NEXT     (assumptions, missing vars, incremental info, redundancy, minimal set; no ML)
Phase 16     Expanded-Representation Confirmation  BLOCKED (re-run Phase 14 with audited representation)
Phase 17     Opportunity Engine v2       BLOCKED
Phase 18     Machine Learning            BLOCKED
```

The Audit decides whether the problem is **representation**, **data**, or **truly no
provable edge**.

---

# STILL FORBIDDEN (until Chief approval)

```text
More data · New strategy · Opportunity Engine v2 · Portfolio Engine · ML
```

Binding rules (Principles 18–33): … (carry-forward) … **hypothesis until prospective
validation** (P31); **identity requires independent explanatory power** (P32);
**validation failure implies representation failure until proven otherwise** (P33).
Core findings: refinement raises apparent edge and false-discovery risk (F-032); a
representation can fail while structure exists (F-033).

---

# CARRY-FORWARD (UNCHANGED)

All of V5.22 in force: F-016–F-032, Principles 18–32, H-06, Research Foundation
closed, Contextual Event Library, Edge/Event Reality Validation, Confirmation
Framework, and "Profitable ≠ Tradable Edge".

---

# FINAL PRINCIPLE

```text
A null result is information, not a verdict on the market.
"We could not validate it" ≠ "it does not exist."
Before more data or more complexity, prove the current representation is exhausted.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DOCTRINE_V5.23.md**
