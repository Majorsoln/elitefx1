# ELITEFX_DECISION_DOCTRINE_V2.md

**Chief Quant — Decision Science Is a Consumer of Market Science; The Evidence Object Is the Contract Between Them. Decision Science Begins With Evidence, Not Decisions.**

Version: Decision Doctrine V2
Status: APPROVED — ACTIVE (Decision-domain SSOT)
Date: 30 June 2026
Authority: Single Source of Truth for the **Decision** domain
Companion: `ELITEFX DOCTRINE V6.9.md` (the **Market** domain SSOT)
Supersedes: Decision Doctrine V1 (adds Principle 63–66; Evidence-first restructure; Evidence Object as the inter-domain API; Chapter-2 roadmap D0–D5)

> Chief amendment to The Split: **Decision Science is not a continuation of Market Science — it
> is a *consumer* of it.** The two domains meet at one object: the **Evidence Object**. Decision
> Science begins with **Evidence Theory**, not with decisions.

---

# THE INTER-DOMAIN ARCHITECTURE (official)

```text
MARKET SCIENCE
──────────────────────────────
Market
  ↓
Representation
  ↓
Evidence Object            ← the PRODUCT of Market Science
══════════════════════════════  ← API / contract (Principle 63)
DECISION SCIENCE
──────────────────────────────
Evidence Object            ← the INPUT to Decision Science
  ↓
Decision Engine
  ↓
Execution
  ↓
Feedback
```

The **Evidence Object** is the contractual interface. Decision Science does not care *how* the
evidence was produced (representation, rule engine, or one day ML) — only that it is valid and
its uncertainty is known. Change the market side freely; the Decision Engine must not change.

---

# DECISION-DOMAIN PRINCIPLES (these come first)

# PRINCIPLE 63 — Evidence Is the Contract (APPROVED)

```text
Evidence is the contractual interface between Market Science and Decision Science.
```

Without a defined Evidence Object, Decision Science cannot be built independently. This is the
first principle of the Decision domain.

# PRINCIPLE 64 — Decision Science Is Production-Agnostic (APPROVED)

```text
Decision Science shall not depend on how evidence was produced,
only on its validity and uncertainty.
```

# PRINCIPLE 65 — Evidence Is a First-Class Object (APPROVED)

```text
Evidence shall be treated as a first-class object with its own lifecycle,
independent of market representations.
```

# PRINCIPLE 66 — Decisions Are Traceable to Evidence (APPROVED)

```text
Every decision must be traceable to explicit evidence objects.
```

Institutional auditability: no decision without a citable evidence trail.

---

# PART 1 — EVIDENCE THEORY (must precede all Decision Theory)

Decision cannot occur before Evidence (Principle 63). Decision Science is, first,
**Evidence Engineering**.

## The Evidence Object

A first-class object (Principle 65) with explicit fields and its own lifecycle:

```text
value        — the effect (e.g., EV in pips), directionful
confidence   — calibrated reliability, e.g. P(edge) = Φ(value / uncertainty)   [NOT magnitude]
uncertainty  — standard error / dispersion of the effect
support      — sample size behind the evidence (n)
coverage     — share of the population the evidence speaks for
freshness    — recency (age since the evidence's data window)
conflict     — degree of internal/external disagreement (sign instability)
source       — provenance tag (which representation/engine produced it)
```

## Evidence Lifecycle

```text
fresh → stale → expired
```

Evidence has a time-to-live; an expired evidence object may not move a decision (Principle 66
requires a *live* trace). Freshness and expiry are intrinsic to the object (Principle 65).

## The D0 questions (this phase)

```text
Q1. What fields does an Evidence Object contain? (confidence, uncertainty, freshness, support,
    conflict, coverage, source, value)
Q2. When two pieces of evidence conflict, what should the Decision Engine do?
Q3. When does evidence expire?
Q4. How is evidence aggregated?
Q5. How much evidence does a decision need? (sufficiency)
```

**Conflict policy (Q2, contract-level, not a Decision Engine):** conflicting evidence must
*widen* aggregate uncertainty and lower confidence; unresolved high-conflict evidence defaults to
**abstention** (capital preservation, P26) — the Decision Engine never silently picks a side.

**Aggregation (Q4):** combine independent evidence by **inverse-variance weighting** of `value`;
the aggregate is itself an Evidence Object (closed under aggregation) carrying combined
uncertainty, summed support, min freshness, and a conflict score.

**Sufficiency (Q5):** evidence is **decision-grade** only above explicit thresholds (minimum
support, minimum confidence, non-expired, conflict below a ceiling). Below threshold → abstain.

Deliverable: `reports/evidence_theory_report.md`
Implementation: `src/research/evidence_object.py` (the Evidence Object + lifecycle + aggregation;
**no Decision Engine** until this spec is approved).

---

# PART 2 — DECISION THEORY (only after Evidence Theory is approved)

The decision **family** (a decision is not "trade"):

```text
{ select · abstain · reduce size · hedge · diversify · wait · exit · suspend }
```

Decision Value is decision-specific (Principle 60). Abstention is a decision and usually the
right one (capital preservation, P26). Decision Quality is measured per decision-type, OOS, with
FDR control (P40 lesson). **Decision Family work is DEFERRED until D0 (Evidence Theory) is
complete and approved** (Chief).

Carried decision-relevant principles: P19 (no finding without decision impact), P21 (selection >
prediction), P23/P24 (rank configurations; not EV alone), P25 (Quality × Availability ×
Survivability), P26 (capital preservation first), P40 (taxonomy ≠ alpha), P57 (primitives are
metadata until decision value), P58 (three independent value dimensions), P59 (representations
act only through evidence), P60 (decision value is decision-specific).

---

# CHAPTER 2 ROADMAP — DECISION SCIENCE

```text
CHAPTER 1   Market Science                      ✅ COMPLETE (frozen; Market Doctrine V6.9)
══════════════════════════════════════════════
CHAPTER 2   Decision Science
  D0   Evidence Theory            NEXT      (Evidence Object spec; fields/lifecycle/conflict/aggregation/sufficiency)
  D1   Decision Objects           BLOCKED   (after D0 approved)
  D2   Decision Families          BLOCKED   (select/abstain/size/hedge/… ; decision-specific value)
  D3   Decision Quality           BLOCKED   (per-decision OOS measurement + FDR)
  D4   Portfolio Decisions        BLOCKED   (allocation; ranking ≠ allocation)
  D5   Live Decision Engine       BLOCKED   (consumes Evidence Objects; production-agnostic)
```

---

# FORBIDDEN IN THE DECISION DOMAIN (until Chief approval)

```text
Writing any Decision Engine before the Evidence Object spec is approved · Direct
representation→action (skip evidence, P59/63) · Untraceable decisions (P66) · Decision-family
work before D0 · One-decision generalization (P60) · ML · live deployment
```

---

# OPEN DECISION QUESTIONS

```text
DQ (D0)  Evidence Object: fields, conflict policy, expiry, aggregation, sufficiency.   ← ACTIVE
DQ-1     Does any variable carry decision value under a NON-selection decision?         DEFERRED (after D0)
DQ-3     How is Confidence calibrated to drive sizing without leaking into direction?   BLOCKED
DQ-4     How is Decision Quality measured per decision-type, OOS, with FDR?             BLOCKED
```

---

# FINAL PRINCIPLE (Decision Doctrine)

```text
Decision Science consumes Market Science; it does not extend it.
The Evidence Object is the contract between the two — define it before anything else.
Decision Science begins with Evidence, not with decisions.
Every decision must trace to live, sufficient, non-conflicting evidence — or it abstains.
Change the market side freely; the contract, and the Decision Engine, must hold.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DECISION_DOCTRINE_V2.md**
