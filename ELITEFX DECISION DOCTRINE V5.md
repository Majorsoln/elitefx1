# ELITEFX_DECISION_DOCTRINE_V5.md

**Chief Quant — Evidence Meaning Is Order-Independent; The Evidence Snapshot Is the Canonical Input to the Decision Layer.**

Version: Decision Doctrine V5
Status: APPROVED — ACTIVE (Decision-domain SSOT)
Date: 30 June 2026
Authority: Single Source of Truth for the **Decision** domain
Companion: `ELITEFX DOCTRINE V6.9.md` (the **Market** domain SSOT)
Supersedes: Decision Doctrine V4 (adds Principle 76–79; Evidence Snapshot as canonical Decision input; Set Confidence → Set Reliability; D3 Evidence Snapshots before Decision Families)

> D2 FULLY APPROVED. Amendments: evidence meaning is **order-independent**, lineage is separate
> (P76); decisions operate on **snapshots**, not raw objects (P77); statistical redundancy ≠ identity
> duplication (P78, OPEN); the **Evidence Snapshot is the canonical input to the Decision Layer** (P79).
> Terminology: "Set Confidence" → **"Set Reliability"** until the confidence model (P70) is closed.

---

# THE FULL ARCHITECTURE (now explicit)

```text
MARKET SCIENCE
  Market → Representation → Evidence Object
DECISION SCIENCE
  Evidence Object → Evidence Operations → Evidence Set → Evidence Snapshot
══════════════════════════════════════════════════════  ← Snapshot = canonical Decision input (P79)
  → Decision → Execution → Feedback
```

---

# PRINCIPLE 76 — Meaning Is Order-Independent; Lineage Is Separate (APPROVED)

D2's Q2 (aggregation is order-invariant: `A+B+C = C+B+A`) is the **first theorem of Decision
Science**: an Evidence Set is a *mathematical set*, not a sequence.

```text
Evidence meaning shall be independent of insertion order;
historical lineage shall be represented separately through provenance.
```

So **Evidence Semantics** (the set) and **Evidence History** (the provenance graph) are two
different things.

# PRINCIPLE 77 — Decisions Operate on Snapshots (APPROVED)

```text
Decisions shall operate on Evidence Snapshots, not on raw Evidence Objects.
```

# PRINCIPLE 78 — Redundancy ≠ Duplication (OPEN)

Dedup by value-object identity removes *duplicates*; it does not remove *redundancy* (e.g. EURUSD
H1 vs H4 — different ids, near-identical information). The Decision Engine will need redundancy
management.

```text
Statistical redundancy shall be distinguished from identity duplication.
```

Status: **OPEN**.

# PRINCIPLE 79 — The Snapshot Is the Canonical Decision Input (APPROVED)

```text
The Evidence Snapshot shall be the canonical input to the Decision Layer.
```

The Decision Engine consumes a **Snapshot** — not an Object, not a raw Set.

---

# PART 1 — EVIDENCE THEORY (final shape of the Evidence Layer)

```text
Evidence Object   (value object; immutable identity; 3 layers)            — D0, P65/67/75
   ↓ Evidence Operations (pure; provenance graph)                          — D1, P68/71/72
Evidence Set      (mathematical set; dedup by identity; order-independent) — D2, P76
   ↓ as-of time T
Evidence Snapshot (immutable point-in-time view; the Decision input)      — D3, P77/79
```

## The Evidence Snapshot (D3)

```text
Q1 — A snapshot is an immutable point-in-time VIEW of an Evidence Set as-of time T: it resolves each
     member's operational state (freshness/expiry) at T, keeps the live members, computes set
     reliability and readiness, and records temporal + structural conflict and the provenance root.
Q2 — Fields: as_of · n_total/n_live · reliability · value/uncertainty · aggregate · readiness ·
     temporal_conflict · structural_conflict · provenance.
Q3 — readiness = decision_ready(aggregate of live members @T) AND temporal_conflict < ceiling.
Q4 — Temporal conflict (P74): older-vs-newer sign contradiction within the snapshot — distinct from
     structural disagreement (cross-pair/timeframe/engine). It gates readiness (abstain).
Q5 — The Decision Engine receives the SNAPSHOT (P79) — not the Object, not the raw Set.
```

## Set Reliability (terminology — P70 OPEN)

The set-level quality figure is **Set Reliability** (aggregate of member reliabilities), *not*
"Set Confidence", until the confidence model (P70) is formally closed.

## Conflict

Structural (intra/cross-pair/cross-timeframe/cross-engine, D1) **and** temporal (older-vs-newer,
D3, addressing P74). The snapshot carries both; readiness requires both below their ceilings.

Deliverable: `reports/evidence_snapshot_report.md`
Implementation: `src/research/evidence_snapshot.py`

---

# PART 2 — DECISION THEORY (still deferred)

The decision **family** (P60) operates on **Evidence Snapshots** (P77/79). Decision-family work
remains **DEFERRED** until the Evidence Layer (Object + Operations + Set + Snapshot) is closed and
approved — which D3 completes.

---

# CHAPTER 2 ROADMAP — DECISION SCIENCE

```text
D0  Evidence Theory       ✅ APPROVED
D1  Evidence Operations   ✅ APPROVED
D2  Evidence Sets         ✅ APPROVED
D3  Evidence Snapshots    NEXT       (canonical Decision input; temporal conflict; readiness @T)
D4  Decision Families     BLOCKED    (select/abstain/size/… on Snapshots; after Evidence Layer closed)
D5  Decision Quality      BLOCKED    (per-decision OOS + FDR)
D6  Portfolio Decisions   BLOCKED
D7  Live Decision Engine  BLOCKED    (small consumer of Snapshots; production-agnostic)
```

---

# FORBIDDEN IN THE DECISION DOMAIN (until Chief approval)

```text
Order-dependent set semantics (P76) · Deciding on raw objects/sets instead of snapshots (P77/79) ·
Treating identity-dedup as redundancy management (P78) · Any Decision Engine before the Evidence
Layer is closed · Decision-family work · ML · live deployment
```

---

# OPEN DECISION QUESTIONS

```text
DQ (D3)  Evidence Snapshot: definition, fields, readiness, temporal conflict, canonical input.  ← ACTIVE
P70      Confidence model (then "reliability" → "confidence").                                   OPEN
P74      Temporal vs structural conflict — formal model (D3 gives first version).                OPEN
P78      Redundancy vs duplication (redundancy management).                                      OPEN
```

---

# FINAL PRINCIPLE (Decision Doctrine)

```text
An Evidence Set is a set, not a sequence — meaning does not depend on order; history lives in the graph.
The Decision Layer never sees a raw object; it sees a snapshot — evidence as-of a moment in time.
Reliability is not yet confidence; duplication is not yet redundancy — name what you have honestly.
Close the Evidence Layer first; the Decision Engine is then only a small consumer of snapshots.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DECISION_DOCTRINE_V5.md**
