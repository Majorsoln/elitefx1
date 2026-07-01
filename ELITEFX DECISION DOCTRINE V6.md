# ELITEFX_DECISION_DOCTRINE_V6.md

**Chief Quant — The Evidence Layer Is Frozen. Decisions Are Immutable Objects That Reference Their Snapshot. Define the Decision Before Its Engine.**

Version: Decision Doctrine V6
Status: APPROVED — ACTIVE (Decision-domain SSOT)
Date: 30 June 2026
Authority: Single Source of Truth for the **Decision** domain
Companion: `ELITEFX DOCTRINE V6.9.md` (the **Market** domain SSOT)
Supersedes: Decision Doctrine V5 (adds Principle 80–84; FREEZES the Evidence Layer; readiness state machine; Decision Objects; D4 Decision Objects before the Decision Engine)

> D3 FULLY APPROVED — no amendments needed. **The Evidence Layer is now frozen as stable
> architecture.** Amendments: the Snapshot is the complete decision context (P80); internal vs
> external conflict (P81, OPEN); readiness is a **state machine** (P82); decisions are **immutable
> first-class objects** (P83) that reference their exact **Snapshot ID** (P84). Define the Decision
> Object before the Decision Engine — as we defined the Event before the algorithms.

---

# THE OFFICIAL ELITEFX ARCHITECTURE

```text
MARKET SCIENCE
  Market → Representation
DECISION SCIENCE — Evidence Layer  [FROZEN]
  Evidence Object → Evidence Operations → Evidence Set → Evidence Snapshot
══════════════════════════════════════════════  ← Snapshot = complete decision context (P80/P79)
DECISION SCIENCE — Decision Layer
  Decision Object → Decision Engine → Execution → Feedback
```

---

# THE EVIDENCE LAYER IS FROZEN

```text
No new Evidence Object, Operation, Set, or Snapshot — unless data shows a large logic gap.
```

D0–D3 are declared **stable architecture**. If we keep changing the foundation, Decision Science
never begins. The Evidence Layer (Object · Operations · Set · Snapshot) is closed.

---

# PRINCIPLE 80 — The Snapshot Is the Complete Decision Context (APPROVED)

```text
The Evidence Snapshot defines the complete decision context available to the Decision Layer.
```

The Decision Layer sees the Snapshot and nothing else — not history, not operations, not raw
objects. The Snapshot is the entirety of what a decision may be based on.

# PRINCIPLE 81 — Internal Conflict vs External Constraint (OPEN)

Temporal and structural conflicts are **internal** (about the evidence). Broker outage, news halt,
execution failure are **external** — not part of the evidence, but they affect the decision.

```text
Decision context shall distinguish internal evidence conflicts from external execution constraints.
```

Status: **OPEN**.

# PRINCIPLE 82 — Readiness Is a State Machine (APPROVED)

```text
Decision-readiness shall be modeled as an explicit state machine rather than a numeric score.
```

```text
READY → STALE → EXPIRED → INVALID
```

(READY: usable; STALE: aging/below threshold but live; EXPIRED: no live evidence; INVALID:
contradictory evidence — conflict above ceiling.) States are more auditable than scores.

# PRINCIPLE 83 — Decisions Are Immutable First-Class Objects (APPROVED)

```text
Decisions shall themselves be represented as immutable first-class objects.
```

Evidence is an object; a Decision must be an object too — with identity, lifecycle, provenance,
quality, and audit.

# PRINCIPLE 84 — Every Decision References Its Snapshot (APPROVED)

```text
Every Decision Object shall reference the exact Evidence Snapshot from which it originated.
```

A decision refers to a **Snapshot ID**, not to individual Evidence Objects — making the whole
system fully auditable: Decision → Snapshot → Set → Operations → Objects.

---

# PART 2 — DECISION THEORY (begins: the Decision Object, D4)

## The Decision Object (immutable value object; P83)

```text
Claim        : id · action (decision family, P60) · reason · reliability · risk
Reference    : evidence_refs = [Snapshot ID]   (P84 — not raw objects)
Operational  : timestamp · lifecycle state
Quality (Q4) : evidence readiness_state · reliability · temporal/structural conflict · support · is_abstention
                (STRUCTURAL — not outcome/OOS quality, which is D5)
Audit (Q5)   : creation + lifecycle transitions, each referencing the Snapshot ID (P66)
```

## Decision Lifecycle (state machine; Q2)

```text
PROPOSED → VALIDATED → EXECUTED → SETTLED
    ↘ REJECTED / EXPIRED   (side states)
```

Transitions are immutable (each returns a new object with an extended audit trail).

## Not the Decision Engine

D4 defines the **object**, not the engine. No logic maps a Snapshot to an action yet; the demo
uses the capital-preservation default (**ABSTAIN**, P26). The Decision Engine will be a small
*consumer*: `Snapshot → action`, filling a Decision Object — it will not force the architecture to
change.

Deliverable: `reports/decision_object_report.md`
Implementation: `src/research/decision_object.py`

---

# CHAPTER 2 ROADMAP — DECISION SCIENCE

```text
Evidence Layer   ✅ FROZEN   (D0 Object · D1 Operations · D2 Set · D3 Snapshot)
D4  Decision Objects        NEXT       (immutable Decision Object; lifecycle; provenance; quality; audit)
D5  Decision Engine         BLOCKED    (Snapshot → action; small consumer)
D6  Decision Quality        BLOCKED    (per-decision OOS + FDR)
D7  Portfolio Decisions     BLOCKED
D8  Live Decision Engine    BLOCKED    (production-agnostic)
```

---

# FORBIDDEN IN THE DECISION DOMAIN (until Chief approval)

```text
Changing the frozen Evidence Layer (except on a proven large logic gap) · Decisions that are not
immutable objects (P83) · Decisions that don't reference a Snapshot ID (P84) · Readiness as a
numeric score (P82) · Any Decision Engine before the Decision Object is closed · ML · live deployment
```

---

# OPEN DECISION QUESTIONS

```text
DQ (D4)  Decision Object: fields, lifecycle, provenance, quality, audit.        ← ACTIVE
P81      Internal vs external (execution) constraints in the decision context.  OPEN
P70      Confidence model (then "reliability" → "confidence").                  OPEN
P74/P78  Temporal-vs-structural conflict model · redundancy vs duplication.     OPEN
```

---

# FINAL PRINCIPLE (Decision Doctrine)

```text
The Evidence Layer is finished; stop rebuilding the foundation and start deciding.
The Snapshot is the whole context; a decision may see nothing else.
A decision is an object — immutable, identified, and bound to the exact snapshot it came from.
Define the decision before its engine, so the engine is a consumer, not a source of churn.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DECISION_DOCTRINE_V6.md**
