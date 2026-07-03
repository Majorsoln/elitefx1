# ELITEFX_DOCTRINE_V6.2.md

**Chief Quant — An Algorithm Cannot Rescue a Bad Representation; Audit Geometry Before Rejecting Ontology**

Version: 6.2
Status: Superseded by V6.3 (current SSOT) — carry-forward in force
Date: 28 June 2026
Authority: Single Source of Truth (superseded by V6.3, 28 June 2026)
Supersedes: V6.1 (Principle 41, 42, 43; F-038 → Partially Approved; breakout k=3 retracted; Phase 20 Representation Geometry Audit)
Previous Versions: Archived (V4 … V6.1)

> ⚠️ **IMESASISHWA:** SSOT rasmi sasa ni **[ELITEFX DOCTRINE V6.3](ELITEFX%20DOCTRINE%20V6.3.md)**
> (Principle 42/43 CONFIRMED; Principle 44 normalization = representation; F-039 events may
> need different geometries; Representation Family / Geometry Selection architecture; end of
> Representation Discovery Era; Phase 21 Representation Operationalization). V6.2 carry-forward.

> Live program status lives in `docs/PROGRAM_BOARD.md`. This file is the doctrine
> of record; V5.0–V6.1 remain in force except where amended below.

---

# EXECUTIVE AMENDMENT — REPRESENTATION BEFORE CLUSTERING

Phase 19 showed no event subtype was robust across algorithms. The correct reading is
**not** "subtypes are KMeans artifacts (ontology failure)" — it is:

```text
The current subtype representation is not algorithm-invariant.
```

That is the difference between an **ontology failure** and a **methodology failure**,
and Phase 19 cannot distinguish them. The lesson is bigger than the taxonomy:

```text
An algorithm cannot rescue a bad representation.
```

---

# THE PARADOX THAT IS THE REAL DISCOVERY

```text
Pullback split-half stability = 0.97        Breakout = 0.98
…yet cross-algorithm agreement is weak (mean ARI 0.08–0.30).
```

KMeans reproduces itself well, but other algorithms disagree. So **stable ≠ true**.

---

# PRINCIPLE 41 — Internal Stability ≠ External Validity (APPROVED)

```text
Internal stability is not evidence of external validity.
```

# PRINCIPLE 42 — Representation Precedes Clustering (APPROVED)

```text
Robust clustering requires robust representation before robust algorithms.
```

# PRINCIPLE 43 — Disagreement Triggers a Representation Audit (APPROVED)

```text
Algorithm disagreement is evidence to audit the representation,
not automatically to reject the ontology.
```

The ontology may be correct while our coordinates are wrong.

---

# FINDING F-038 — PARTIALLY APPROVED (reworded)

```text
Some events exhibit evidence of latent heterogeneity, but the current taxonomy
is not yet robust to representation and clustering methodology.
```

Status downgraded **APPROVED → PARTIALLY APPROVED**. The specific complexity claims
(e.g., breakout k=3) are **retracted** — Phase 19 showed best-k is itself unstable
(50–67%).

---

# PHASE 20 — Representation Geometry Audit (NEXT)

Before improving clustering, determine whether the feature space itself allows a true
taxonomy to emerge. Not event-confirmation, not consensus-clustering — geometry first:

```text
Q1. Does the current feature space have enough separability?
    (silhouette / Davies–Bouldin / Calinski–Harabasz per event, vs permutation null)
Q2. Does our normalization hide structure? (z-score vs robust vs percentile)
Q3. Do the event-specific representations have different geometry?
Q4. Does treating trajectory/activity/volatility/spread as a manifold (vs coordinates)
    change separability? (Laplacian eigenmaps)
Q5. Does a new representation increase agreement between algorithms? (cross-algo ARI)
```

Deliverable: `reports/representation_geometry_report.md`
Implementation: `src/research/representation_geometry_engine.py`

---

# MACHINE LEARNING — Still Deferred (reason updated)

```text
No ML.
```

The reason is no longer "we have no edge". It is: **we have no representation whose
geometry lets an edge emerge stably.** Get the representation right and algorithms
follow; get it wrong and the best algorithm still yields an unreliable ontology.

---

# UPDATED ROADMAP

```text
Phase 19     CLOSED   (Taxonomy Robustness; 0 robust subtypes; representation not algorithm-invariant)
Phase 20     Representation Geometry Audit   NEXT   (separability/normalization/manifold/algo-agreement; no ML)
Phase 21     Improved-Representation Taxonomy BLOCKED (rebuild taxonomy on audited representation)
Phase 22     Event-Subtype Edge Confirmation BLOCKED (OOS + FDR; Principle 40)
Phase 23     Machine Learning            BLOCKED
```

---

# STILL FORBIDDEN (until Chief approval)

```text
Single-algorithm ontology · Treating taxonomy as alpha · ML · Portfolio Engine
```

Binding rules (Principles 18–43): … (carry-forward) … **ontology never from one
clustering algorithm** (P39); **valid taxonomy ≠ alpha** (P40); **internal stability
≠ external validity** (P41); **representation precedes clustering** (P42); **algorithm
disagreement → audit representation, not reject ontology** (P43). Core findings:
taxonomy is hierarchical/event-specific (F-038, partial); a representation can fail
while structure exists (F-033).

---

# CARRY-FORWARD (UNCHANGED)

All of V6.1 in force: F-016–F-037, Principles 18–40, H-06, Event Representation
Family, Architecture V6, and "Profitable ≠ Tradable Edge".

---

# FINAL PRINCIPLE

```text
An algorithm cannot rescue a bad representation.
Stable is not the same as true; agreement across methods is the test.
When algorithms disagree, audit the coordinates before you reject the ontology.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DOCTRINE_V6.2.md**
