# ELITEFX_DOCTRINE_V6.3.md

**Chief Quant — End of the Representation Discovery Era; Normalization Is Representation; Operationalize Before Alpha**

Version: 6.3
Status: Superseded by V6.4 (current SSOT) — carry-forward in force
Date: 28 June 2026
Authority: Single Source of Truth (superseded by V6.4, 30 June 2026)
Supersedes: V6.2 (Principle 42/43 CONFIRMED; Principle 44; F-039; architecture += Representation Family / Geometry Selection; Phase 21 Representation Operationalization)
Previous Versions: Archived (V4 … V6.2)

> ⚠️ **IMESASISHWA:** SSOT rasmi sasa ni **[ELITEFX DOCTRINE V6.4](ELITEFX%20DOCTRINE%20V6.4.md)**
> (Phase 21 APPROVED — representation SURVIVES OOS; F-039 APPROVED; Principle 45 operational
> robustness ≠ statistical stability; Principle 46 taxonomy must be semantically interpretable;
> Principle 47 express clusters in market language; **"Alpha Discovery Era" retracted** — still
> Market Understanding Era; end of Representation Engineering Era; Phase 22 Semantic Taxonomy).
> V6.3 carry-forward. **NOTE:** the V6.3 wording "the Alpha Discovery Era opens" is retracted.

> Live program status lives in `docs/PROGRAM_BOARD.md`. This file is the doctrine
> of record; V5.0–V6.2 remain in force except where amended below.

---

# EXECUTIVE AMENDMENT — END OF THE REPRESENTATION DISCOVERY ERA

Phase 20 is the **end of the "Representation Discovery Era"**. We no longer search for
a new representation every week. The evidence:

```text
Coordinate space   → weak separability (silhouette ~0.21–0.23, near/below null)
Robust normalization → better geometry than z-score for every event
Manifold (Laplacian eigenmaps) → strong separability & agreement (ARI up to 0.89–0.99;
                                  silhouette up to ~0.58–0.79)
```

These directly confirm Principles 42 and 43. **Careful wording:** this means

```text
Evidence now favors a representation limitation over an ontology limitation.
```

— not "it is not ontology". The ontology debate is not closed until the manifold
representation is confirmed out-of-sample.

---

# PRINCIPLES 42 & 43 — CONFIRMED

```text
Principle 42  Robust clustering requires robust representation before robust algorithms.   [CONFIRMED]
Principle 43  Algorithm disagreement triggers a representation audit before ontology rejection.   [CONFIRMED]
```

Promoted from proposed to **Confirmed Principles** — they now have direct data support.

---

# PRINCIPLE 44 — Normalization Is Part of the Representation (APPROVED)

Q2 (robust ≈ 0.33–0.35 vs z-score ≈ 0.22 vs percentile ≈ 0.17–0.19) shows normalization
is not preprocessing — it changes the geometry.

```text
Feature normalization is an integral component of market representation,
not merely a preprocessing step.
```

---

# FINDING F-039 — Events May Need Different Geometries (OPEN)

Manifold helped almost every event, but **breakout stayed weak**. Mean Reversion may
have a simple manifold; Breakout a harder one.

```text
Different Events may require different geometric representations.
```

An extension of Principle 38. Status: **OPEN**.

---

# UPDATED ARCHITECTURE

```text
Market
  ↓
Representation Family        (normalization + geometry are choices, not fixed)
  ↓
Geometry Selection           ← which normalization / manifold per event
  ↓
Taxonomy
  ↓
Reality Validation
```

Representation is a **family**, not a single object, and geometry is part of the choice.

---

# PHASE 21 — Representation Operationalization (NEXT)

We have a promising representation, but it has not shown it can work **outside the
research environment**. Before any new taxonomy:

```text
Q1. Can a Nyström extension project OOS data onto the manifold without losing structure?
Q2. Does the manifold geometry stay stable across rolling walk-forward?
Q3. Do ARI and silhouette stay high in future periods?
Q4. Does robust+manifold work for all pairs, or is there an event-specific best choice?
Q5. Operational cost: can this representation be used live WITHOUT leakage?
```

Method: fit the embedding on PAST landmarks only; project FUTURE points via Nyström
with no re-fit (no lookahead). Compare proper-Nyström vs joint-fit to quantify leakage
inflation. No new taxonomy until this passes.

Deliverable: `reports/representation_operationalization_report.md`
Implementation: `src/research/representation_operationalization_engine.py`

---

# MACHINE LEARNING — Still Deferred (reason updated again)

```text
No ML.
```

The reason has evolved: not "no edge", not "no representation", but **"we have a
promising representation that has not yet shown it can work outside research."** Once
it operationalizes OOS without leakage, the **Alpha Discovery Era** opens.

---

# UPDATED ROADMAP

```text
Phase 20     CLOSED   (Representation Geometry; manifold + robust normalization; end of Representation Discovery Era)
Phase 21     Representation Operationalization   NEXT   (Nyström OOS, rolling stability, leakage; no ML)
Phase 22     Improved-Representation Taxonomy    BLOCKED (rebuild on operationalized representation)
Phase 23     Event-Subtype Edge Confirmation     BLOCKED (OOS + FDR; Principle 40)
Phase 24     Machine Learning                    BLOCKED  (Alpha Discovery Era)
```

---

# STILL FORBIDDEN (until Chief approval)

```text
New taxonomy before operationalization · ML · Portfolio Engine · live deployment
```

Binding rules (Principles 18–44): … (carry-forward) … **internal stability ≠ external
validity** (P41); **representation precedes clustering [CONFIRMED]** (P42); **algorithm
disagreement → audit representation [CONFIRMED]** (P43); **normalization is part of the
representation** (P44). Core findings: representation limitation favored over ontology
limitation (F-038 partial); events may need different geometries (F-039, open).

---

# CARRY-FORWARD (UNCHANGED)

All of V6.2 in force: F-016–F-038, Principles 18–43, H-06, Event Representation Family,
Architecture V6, and "Profitable ≠ Tradable Edge".

---

# FINAL PRINCIPLE

```text
The Representation Discovery Era is over; now we operationalize.
Normalization is representation; geometry is a choice, not a constant.
A representation that works only in research is not a representation we can trade.
Confirm it out-of-sample, without leakage, before opening the Alpha Discovery Era.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DOCTRINE_V6.3.md**
