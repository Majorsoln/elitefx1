# ELITEFX_DECISION_DOCTRINE_V3.md

**Chief Quant — The Evidence Object Has Three Layers and Is Immutable; Operations Move Evidence Through the System. Decision-Ready Is Not Trade-Ready.**

Version: Decision Doctrine V3
Status: Superseded by Decision Doctrine V4 (current Decision-domain SSOT) — carry-forward in force
Date: 30 June 2026
Authority: Single Source of Truth (superseded by Decision Doctrine V4, 30 June 2026)
Companion: `ELITEFX DOCTRINE V6.9.md` (the **Market** domain SSOT)
Supersedes: Decision Doctrine V2 (adds Principle 67–70; three-layer Evidence Object; Evidence Object vs Evidence Operations; conflict taxonomy; D1 Evidence Operations before D2 Decision Families)

> ⚠️ **IMESASISHWA:** Decision-domain SSOT rasmi sasa ni **[ELITEFX DECISION DOCTRINE V4](ELITEFX%20DECISION%20DOCTRINE%20V4.md)**
> (D1 FULLY APPROVED + amendments: **P71** transformations pure/deterministic/side-effect-free; **P72**
> provenance = directed graph; **P73** readiness = Evidence Snapshot, sio object; **P74 OPEN** temporal vs
> structural conflict; **P75** Evidence = value objects wenye immutable identity; **Evidence Sets** —
> decisions juu ya collection sio object moja; D2 Evidence Sets KABLA ya Decision Families). V3 carry-forward.

> D0 APPROVED. Chief amendments before the Decision Doctrine is closed: the Evidence Object has
> **three layers** (Claim / Quality / Operational State), it is an **immutable contract**, and
> **aggregation is an operation upon it, not a part of it**. "Decision-ready" ≠ "trade-ready".

---

# THE INTER-DOMAIN ARCHITECTURE (unchanged from V2)

```text
MARKET SCIENCE:   Market → Representation → Evidence Object
══════════════════════════════════════════════  API (Principle 63)
DECISION SCIENCE: Evidence Object → [Evidence Operations] → Decision Engine → Execution → Feedback
```

---

# PRINCIPLE 67 — Evidence Has Three Layers (APPROVED)

The eight fields are not one kind of information; they fall into three layers, and the Decision
Engine reads **categories**, not a flat list.

```text
Every Evidence Object shall consist of three layers:
  A. Claim              — value · direction · source                 (the assertion)
  B. Evidence Quality   — confidence · uncertainty · support · coverage   (how good the claim is)
  C. Operational State  — freshness · conflict · expiry              (whether it is usable NOW)
```

# PRINCIPLE 68 — Objects Are Immutable; Aggregation Is an Operation (APPROVED)

```text
Evidence Objects are immutable contracts; aggregation is an external operation performed on them.
```

Today aggregation is inverse-variance; tomorrow it may be Bayesian pooling, Dempster–Shafer, or
weighted voting. The **object must not change** when the operation does. Operations are pure: they
consume Evidence Objects and produce new Evidence Objects (with an extended audit trail), never
mutating their inputs.

# PRINCIPLE 69 — Decision-Ready Is Not Trade-Ready (APPROVED)

```text
Decision-ready evidence does not imply trade-ready evidence.
```

"Decision-ready" means the object is *ready to be consumed by the Decision Engine* (sufficient
support, confidence, non-expired, low conflict) — **not** that a trade is profitable. (Terminology:
"decision-grade" → **"decision-ready"**.)

# PRINCIPLE 70 — Confidence Is a Model, Not a Stored Fact (OPEN)

```text
Confidence should be derived from an explicit confidence model rather than stored as a primitive fact.
```

Today confidence = Φ(EV/SE); that is one model and it **saturates** at large support. The Evidence
Object should not hard-store confidence as primitive truth; it should reference a confidence model
that can be recalibrated (OOS) without changing the object. Status: **OPEN** — to be designed.

---

# PART 1 — EVIDENCE THEORY (updated)

## The Evidence Object (three layers, immutable)

```text
A. Claim            : value, direction, source
B. Quality          : confidence (model output), uncertainty, support, coverage
C. Operational State: freshness (fresh→stale→expired), conflict, expiry
```

Lifecycle (Operational State): `fresh → stale → expired`. Expired evidence cannot move a decision
(P66 needs a live trace). The object is immutable (P68); a read-only view is available (`freeze`).

## Evidence Operations (D1 — the canonical home of operations, P68)

Operations are **pure** functions on immutable Evidence Objects, each extending the audit trail
(P66):

```text
aggregate — inverse-variance combine (closed under aggregation; today's model)
filter    — select a subset by predicate (e.g., live-only)
merge     — combine two into one
expire    — advance age → change Operational State
split     — divide support (e.g., per sub-regime); uncertainty grows as n falls
```

All five preserve the audit trail. **expire, split, and aggregate(conflicting)** can change
decision-readiness; readiness is an Operational State, not a permanent property.

## Conflict Has a Taxonomy (not a scalar)

Conflict is not one number; it is classified by the dimension along which evidence disagrees, each
measured **controlling for the other dimensions**:

```text
intra (split-half)  — instability within one object over time
cross-pair          — pairs disagree (controlling tf, engine)
cross-timeframe     — timeframes disagree (controlling pair, engine)
cross-engine        — engines / representations disagree (controlling pair, tf)
```

**Conflict policy (P26):** high unresolved conflict — especially cross-engine or cross-pair —
defaults to **ABSTAIN**; the Decision Engine never silently picks a side. The policy may depend on
*which kind* of conflict is present.

---

# PART 2 — DECISION THEORY (still deferred until operations are closed)

The decision **family** (P60): `select · abstain · reduce · hedge · diversify · wait · exit ·
suspend`. **Decision Family work (D2) remains DEFERRED** until the Evidence Object and its
Operations are closed and approved. Carried decision principles: P19, P21, P23–26, P40, P57–62.

---

# CHAPTER 2 ROADMAP — DECISION SCIENCE

```text
D0   Evidence Theory          ✅ APPROVED   (Evidence Object spec; 3 layers; lifecycle; sufficiency)
D1   Evidence Operations      NEXT          (pure ops on immutable objects; audit; conflict taxonomy; readiness)
D2   Decision Families        BLOCKED       (DEFERRED — select/abstain/size/… ; decision-specific value)
D3   Decision Quality         BLOCKED       (per-decision OOS + FDR)
D4   Portfolio Decisions      BLOCKED       (allocation; ranking ≠ allocation)
D5   Live Decision Engine     BLOCKED       (consumes Evidence Objects; production-agnostic)
```

---

# FORBIDDEN IN THE DECISION DOMAIN (until Chief approval)

```text
Mutating an Evidence Object (P68) · Building aggregation INTO the object (P68) · Treating
decision-ready as trade-ready (P69) · Hard-storing confidence as primitive truth (P70) · Any
Decision Engine before Object + Operations are closed · Decision-family work (D2) · ML · live deployment
```

---

# OPEN DECISION QUESTIONS

```text
DQ (D1)  Evidence Operations: which ops, audit-preservation, immutability, conflict taxonomy,
         readiness-change.                                                              ← ACTIVE
P70      Confidence model (explicit, recalibratable) — design.                          OPEN
DQ-1     Non-selection decision value (abstention/sizing).                              DEFERRED (D2)
```

---

# FINAL PRINCIPLE (Decision Doctrine)

```text
Evidence is three things at once: a claim, its quality, and its operational state — never confuse them.
The object is an immutable contract; operations move it through the system and leave an audit trail.
Aggregation is something we DO to evidence, not something evidence IS.
Conflict is a taxonomy, not a number; abstain when the disagreement is real.
Decision-ready is not trade-ready — and confidence is a model, not a fact.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DECISION_DOCTRINE_V3.md**
