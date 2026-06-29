# ELITEFX_DOCTRINE_V6.1.md

**Chief Quant — Taxonomy Is Event-Specific; Ontology Must Be Algorithm-Independent; Taxonomy ≠ Alpha**

Version: 6.1
Status: APPROVED — ACTIVE (current SSOT)
Date: 28 June 2026
Authority: Single Source of Truth (SSOT)
Supersedes: V6.0 (F-037 → Partially Approved; F-038; Principle 39, 40; Phase 19 Taxonomy Robustness Audit)
Previous Versions: Archived (V4 … V6.0)

> Live program status lives in `docs/PROGRAM_BOARD.md`. This file is the doctrine
> of record; V5.0–V6.0 remain in force except where amended below.

---

# EXECUTIVE AMENDMENT — FROM SIGNALS TO MARKET ONTOLOGY

The project has climbed: Signals → Events → Representations → **Market Ontology**. Phase
18 asked the right question — not "does the event have an edge?" but "is the event
itself homogeneous?" — and the data answered:

```text
trend_continuation → distinguishable sub-events (k=4)
breakout           → distinguishable sub-events (k=3)
pullback · deep_pullback · mean_reversion → no sufficient evidence (current method)
```

Two cautions follow, both now doctrine.

---

# FINDING F-037 — PARTIALLY APPROVED (reworded)

```text
Some Events exhibit statistically distinguishable latent sub-events;
event taxonomy is therefore event-dependent, not universal.
```

Not "events have sub-events" (universal) — only **some** do.

---

# FINDING F-038 — Taxonomy Is Hierarchical and Event-Specific (APPROVED)

Different events showed different latent complexity (k=4 vs k=3 vs none). There is no
universal taxonomy.

```text
Market taxonomy is hierarchical and event-specific;
different Events possess different latent complexity.
```

---

# PRINCIPLE 39 — Ontology Must Be Algorithm-Independent (APPROVED)

Phase 18 used KMeans alone (spherical clusters, fixed k, distance-dependent). Ontology
cannot rest on one algorithm.

```text
Market ontology shall never be inferred from a single clustering algorithm.
```

Ontology must be robust across methodologies (KMeans, GMM, Agglomerative, …).

---

# PRINCIPLE 40 — Valid Taxonomy Is Not Alpha (APPROVED)

Phase 18 found subtypes, but **0/17 carried a positive edge**. A correct ontology is
not a tradable edge.

```text
A valid market taxonomy is not evidence of tradable alpha.
```

Ontology and alpha are two different things. (Quant history is full of systems that
found real structure but could not turn it into profit after costs.)

---

# PHASE 19 — Taxonomy Robustness Audit (NEXT)

Do not jump to OOS edge confirmation. First prove the subtypes are real, not KMeans
artifacts:

```text
Q1. Do KMeans / GMM / Agglomerative give similar taxonomy? (ARI / NMI)
Q2. How stable are subtype assignments? (split-half ARI)
Q3. Are centroids stable across sample variation? (bootstrap)
Q4. Do subtypes persist in future OOS?
Q5. Is taxonomy complexity (k) stable across subsamples?
```

A subtype is robust only if it is algorithm-independent AND stable AND OOS-persistent.

Deliverable: `reports/taxonomy_robustness_report.md`
Implementation: `src/research/taxonomy_robustness_engine.py`

---

# MACHINE LEARNING — Still Deferred

```text
No ML.
```

Only after a taxonomy is proven algorithm-independent (Principle 39) and OOS-persistent
do we attempt to turn a subtype into alpha — and even then, taxonomy ≠ alpha
(Principle 40).

---

# UPDATED ROADMAP

```text
Phase 18     CLOSED   (Event Taxonomy; F-037 partial, F-038; subtypes exist for some events; 0/17 edge)
Phase 19     Taxonomy Robustness Audit   NEXT     (algorithm-independence + stability + OOS persistence; no ML)
Phase 20     Event-Subtype Edge Confirmation BLOCKED (only robust subtypes; OOS + FDR; Principle 40)
Phase 21     Event-Specific Opportunity  BLOCKED
Phase 22     Portfolio Engine            BLOCKED
Phase 23     Machine Learning            BLOCKED  (one model per robust subtype)
```

---

# STILL FORBIDDEN (until Chief approval)

```text
Single-algorithm ontology · Treating taxonomy as alpha · Opportunity Engine · ML
```

Binding rules (Principles 18–40): … (carry-forward) … **no universal representation —
each Event defines its own representation space** (P38); **ontology never from one
clustering algorithm** (P39); **valid taxonomy is not tradable alpha** (P40). Core
findings: events may contain latent sub-events (F-037, partial); taxonomy is
hierarchical and event-specific (F-038).

---

# CARRY-FORWARD (UNCHANGED)

All of V6.0 in force: F-016–F-036, Principles 18–38, H-06, Research Foundation closed,
Event Representation Family, Architecture V6, and "Profitable ≠ Tradable Edge".

---

# FINAL PRINCIPLE

```text
Different events have different latent complexity — taxonomy is event-specific.
Never trust an ontology built on one algorithm.
A correct taxonomy is not an edge: ontology and alpha are separate proofs.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DOCTRINE_V6.1.md**
