# LESSON-035@v1

```yaml
id: LESSON-035@v1
claim: "Evidence objects are immutable contracts and aggregation is an operation performed on them, not a mutation of them — so the combination rule can change without touching the evidence or the objects that cite it."
type: GOVERNANCE
evidence:
  - "PROGRAM_BOARD V3 P67/P68 (APPROVED, evidence_theory_report.md): every Evidence Object is three layers
    (Claim + Evidence Quality + Operational State) and is an IMMUTABLE contract; 'aggregation is an external
    operation, not part of the object — so Bayesian / Dempster-Shafer / voting can replace inverse-variance
    without changing the object'"
  - "evidence_operations_report.md (D1): pure operations on immutable objects (aggregate / filter / merge /
    expire / split) with an audit trail and conflict taxonomy — the objects are inputs, never mutated in place"
  - "PROGRAM_BOARD V6 (APPROVED): Evidence Layer (Object · Operations · Set · Snapshot) FROZEN; P83 decisions
    are immutable first-class objects; P84 every Decision references the exact Snapshot ID → full audit chain"
counter_evidence: "none found (scope: D0-D3 Evidence architecture). Bound: immutability is of the CONTRACT/
  object, not a ban on new computation — aggregation methods evolve freely as external operations; and an
  immutable, well-formed object can still carry a wrong claim (immutability ≠ correctness)"
validity_conditions: general (any system that combines uncertain inputs into decisions; demonstrated on the
  Evidence Object → Operations → Set → Snapshot chain)
when_to_use: designing any evidence/feature/signal object — freeze the object as an immutable contract and
  put ALL combination logic in external, swappable operations; this lets the aggregation method change
  (inverse-variance → Bayesian → voting) without a data migration or touching downstream citations
when_not_to_use: do not fold aggregation into the object (that locks you to one combination rule and breaks
  provenance); and immutability is not correctness — a clean, frozen object with a wrong claim is still
  wrong (pair with LESSON-025 — define the contract first, and validate the claim separately)
provenance: {principle: P67/P68/P83/P84, phase: D0/D1/D3, doctrine: (V3 / V6 — Evidence Layer FROZEN)}
lifecycle: CANDIDATE  # RESEARCHER-K batch 6 — inasubiri review ya Chief
```

**Maelezo kwa mwanafunzi:** Evidence Object ni *contract isiyobadilika* (Claim + Quality + Operational State).
Ku-aggregate (kuunganisha) ni **operesheni ya nje**, si sehemu ya object — hivyo unaweza kubadilisha njia ya
kuunganisha (inverse-variance → Bayesian → voting) bila kugusa evidence wala Decisions zinazoiref. Immutability
inalinda provenance (P84: kila Decision inaref Snapshot ID kamili) — lakini object safi yenye claim batili bado ni batili.
