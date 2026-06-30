# ELITEFX_DECISION_DOCTRINE_V4.md

**Chief Quant — Evidence Is a Value Object; Provenance Is a Graph; Readiness Belongs to a Snapshot. Decisions Are Made on Evidence Sets, Not Single Objects.**

Version: Decision Doctrine V4
Status: APPROVED — ACTIVE (Decision-domain SSOT)
Date: 30 June 2026
Authority: Single Source of Truth for the **Decision** domain
Companion: `ELITEFX DOCTRINE V6.9.md` (the **Market** domain SSOT)
Supersedes: Decision Doctrine V3 (adds Principle 71–75; Evidence Set layer; provenance graph; snapshot readiness; value-object identity; D2 Evidence Sets before D2-old Decision Families)

> D1 FULLY APPROVED ("the first report that no longer talks about Forex — it talks about software
> architecture"). Amendments: transformations are **pure** (P71); provenance is a **graph** (P72);
> readiness belongs to a **Snapshot** (P73); temporal vs structural conflict (P74, OPEN); Evidence
> Objects are **value objects** (P75). And decisions are made on **Evidence Sets**, not single objects.

---

# THE INTER-DOMAIN ARCHITECTURE (amended)

```text
MARKET SCIENCE:   Market → Representation → Evidence Object
══════════════════════════════════════════════  API (Principle 63)
DECISION SCIENCE: Evidence Objects → Evidence Sets → Decision → Execution → Feedback
```

A decision is never made on one Evidence Object; it is made on an **Evidence Set** (a collection
that can be measured, ordered, and audited together).

---

# PRINCIPLE 71 — Pure Evidence Transformations (APPROVED)

```text
Evidence transformations shall be pure, deterministic and side-effect free.
```

Evidence behaves like a functional-programming object; the Decision Engine will have no side
effects — essential for audit.

# PRINCIPLE 72 — Provenance Is a Graph (APPROVED)

```text
Evidence provenance shall be represented as a directed graph, not merely a chronological log.
```

`aggregate`/`merge` have multiple parents; `split` has multiple children. Provenance is a DAG of
Evidence Objects (nodes = value-object ids; edges = parent → child), not a flat list.

# PRINCIPLE 73 — Readiness Belongs to a Snapshot (APPROVED)

```text
Decision-readiness belongs to an Evidence Snapshot, not to the immutable Evidence Object itself.
```

The Evidence Object is immutable; **readiness changes over time**. Readiness is therefore evaluated
on a *snapshot* (the evidence as-of a point in time), not stored on the object.

# PRINCIPLE 74 — Temporal vs Structural Conflict (OPEN)

```text
Evidence conflict shall explicitly distinguish temporal contradiction from structural disagreement.
```

"Yesterday bullish, today bearish" is a **temporal contradiction** — not intra, not cross-engine.
The Decision Engine must know this. Status: **OPEN** (the current taxonomy covers structural
disagreement; temporal is to be added).

# PRINCIPLE 75 — Evidence Objects Are Value Objects (APPROVED)

```text
Evidence Objects shall be value objects with immutable identity.
```

Identity is content-derived (Claim + Quality + source), enabling deduplication and graph nodes —
and allowing the implementation language to change without changing the doctrine.

---

# PART 1 — EVIDENCE THEORY (updated)

## Evidence Object (value object; three layers; immutable)

```text
identity : content hash of Claim + Quality + source (P75)
A. Claim            : value, direction, source
B. Quality          : confidence (model), uncertainty, support, coverage
C. Operational facts: age, conflict   (raw; readiness is NOT stored here — P73)
provenance: parents[] + op  (graph edges, P72)
```

## Evidence Operations (pure; P71/P72)

`aggregate · filter · merge · expire · split` — pure functions producing new Evidence Objects,
each recording parents+op (provenance graph) and extending the audit trail (P66).

## Evidence Set (D2 — the unit the Decision Engine consumes)

```text
- A collection keyed by value-object identity (dedup by id — P75).      [Q1, Q3]
- Aggregation is order-invariant (set semantics); provenance is order-sensitive (graph).  [Q2]
- The set has its OWN confidence = aggregate of members (+ conflict).    [Q4]
- The set has readiness only via a SNAPSHOT (as-of time) — P73.          [Q5]
```

## Snapshot

A Snapshot = an Evidence Set (or object) evaluated as-of a time → recomputes freshness/expiry, then
readiness. The same set is decision-ready at one time and not at another; the objects never change.

## Conflict (taxonomy; P74 pending)

Structural: intra(split-half) · cross-pair · cross-timeframe · cross-engine (each controlling for
the others). **Temporal contradiction (P74) is not yet implemented** and must be added before the
Decision Engine.

---

# PART 2 — DECISION THEORY (still deferred)

The decision **family** (P60) operates on **Evidence Sets**. Decision-family work remains
**DEFERRED** until the Evidence Layer (Object + Operations + Set) is closed and approved.

---

# CHAPTER 2 ROADMAP — DECISION SCIENCE

```text
D0   Evidence Theory        ✅ APPROVED   (3-layer Evidence Object; lifecycle; sufficiency)
D1   Evidence Operations    ✅ APPROVED   (pure ops; audit; conflict taxonomy; readiness)
D2   Evidence Sets          NEXT          (collection; identity/dedup; order-invariance; set confidence; snapshot readiness)
D3   Decision Families      BLOCKED       (DEFERRED — select/abstain/size/… on Evidence Sets)
D4   Decision Quality       BLOCKED       (per-decision OOS + FDR)
D5   Portfolio Decisions    BLOCKED       (allocation; ranking ≠ allocation)
D6   Live Decision Engine   BLOCKED       (consumes Evidence Sets; production-agnostic)
```

---

# FORBIDDEN IN THE DECISION DOMAIN (until Chief approval)

```text
Impure/side-effecting transformations (P71) · Provenance as a flat log only (P72) · Storing
readiness on the object (P73) · Mutable Evidence Objects (P75) · Any Decision Engine before the
Evidence Layer (Object+Operations+Set) is closed · Decision-family work · ML · live deployment
```

---

# OPEN DECISION QUESTIONS

```text
DQ (D2)  Evidence Sets: collection, ordering, duplicates, set confidence, snapshot readiness.  ← ACTIVE
P74      Temporal vs structural conflict — design.                                             OPEN
P70      Confidence model (explicit, recalibratable).                                          OPEN
DQ-1     Non-selection decision value (abstention/sizing).                                     DEFERRED (D3)
```

---

# FINAL PRINCIPLE (Decision Doctrine)

```text
Evidence is a value object: defined by what it claims and how good it is, not by when you read it.
Provenance is a graph; transformations are pure; readiness lives in a snapshot, not the object.
Decisions are made on sets of evidence, measured and audited together — never on a single object.
Build the infrastructure that survives a change of representation, language, or model.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DECISION_DOCTRINE_V4.md**
