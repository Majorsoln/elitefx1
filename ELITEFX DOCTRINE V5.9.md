# ELITEFX_DOCTRINE_V5.9.md

**Chief Quant Amendment — Latent Structure Before Taxonomy (No Human Theory)**

Version: 5.9
Status: Superseded by V5.10 (current SSOT) — carry-forward in force
Date: 25 June 2026
Authority: Single Source of Truth (superseded by V5.10, 26 June 2026)
Supersedes: V5.8 (rejects Phase 5.9 method; reframes F-015; renames Mechanism→Latent)
Previous Versions: Archived (V4, V4.1, V5.0, V5.1, V5.2, V5.3, V5.4, V5.5, V5.6, V5.7, V5.8)

> ⚠️ **IMESASISHWA:** SSOT rasmi sasa ni **[ELITEFX DOCTRINE V5.10](ELITEFX%20DOCTRINE%20V5.10.md)**
> (F-016 Latent Structures APPROVED; F-017 Rare States; Principle 18 algorithm
> independence; Market Configuration trading). V5.9 carry-forward.

> Live program status lives in `docs/PROGRAM_BOARD.md`. This file is the doctrine
> of record; V5.0–V5.8 remain in force except where amended below.

---

# EXECUTIVE AMENDMENT

Phase 5.9 (`mechanism_discovery_report.md`) was **NOT APPROVED** — not because the
code was wrong, but because the **hypothesis was not tested correctly.** That is a
normal, valuable step in quantitative research.

```text
The mechanisms (Expansion, Compression, Recovery, Neutral) did not come from data.
They came from a rule set.
```

This is **verification**, not **discovery**, and it imports a human taxonomy —
which violates a founding rule:

```text
NO HUMAN MARKET THEORY.
```

The correction: let the data speak first, name later.

```text
Features → Unknown Structure → Discovery → (only then) a name.
```

---

# METHODOLOGY CORRECTION

What Phase 5.9 did:

```text
Features → Chief names "Recovery" → model measures "Recovery"   (circular)
```

What is required:

```text
Features → Unknown latent structure → unsupervised discovery → later, a name
```

Two further faults are recorded:

1. **Incomplete signature** — only 4 variables (vol_z, vol_slope, age, pchg). The
   market state vector must use all key features: Volatility, Activity, Spread,
   Transition, Lifecycle.
2. **Cosine ignores scale** — `(0.1,0.2,0.3)` and `(0.4,0.8,1.2)` look identical
   to cosine although the market scale differs. Use **standardized Euclidean**,
   not cosine.

---

# FINDING F-015 — Reframed and OPEN

```text
WAS:  Universal Mechanisms, Local Coordinates.
NOW:  Latent Market Structures (existence) — under test.
```

Status: **OPEN — NOT PROVEN.** The Phase 5.9 report itself supported it on 0/4
events. F-015 remains a hypothesis until the **data** reveals latent structures
without a human taxonomy. The rule-based names (Expansion/Compression/…) are
**removed as ground truth**; they may survive only as *future illustrative
examples*, never as scientific findings.

(F-014 — interactions are pair-local — remains **APPROVED**.)

---

# RENAME — Mechanism Library → Latent State Library

```text
Mechanism Library      → Latent State Library
"learns mechanisms"    → "discovers latent market structures"
```

We do not yet know there are "mechanisms". We know there are state vectors; we
are testing whether they cluster.

---

# UPDATED ARCHITECTURE

```text
Volume Bars
↓
State Detection
↓
Lifecycle
↓
State Vector              (all key features)
↓
Latent Structure Discovery   ← unsupervised; no human labels
↓
Opportunity
↓
Payoff
↓
ML
```

This is **representation discovery** — still without supervised ML. Let the
market describe itself before any model is fit.

---

# UPDATED ROADMAP

```text
Phase 5.9    Mechanism Discovery          NOT APPROVED (human taxonomy; reworked)
Phase 5.9A   Latent Structure Discovery   NEXT       (unsupervised; do natural groups exist?)
Phase 6      Latent State Library         BLOCKED    (only if structures emerge robustly)
Phase 7      Adaptive Interaction Engine  BLOCKED
Phase 8      Market State Vector / Opportunity   BLOCKED
Phase 9      Payoff Engine                BLOCKED
Phase 10     Machine Learning             BLOCKED
```

## Phase 5.9A — Latent Structure Discovery (NEXT)

```text
Build Market State Vectors from all key features (per-pair standardized).
Find — without human labels — whether natural groups (latent structures) exist.
Only if they emerge robustly do we interpret and name them.
```

Method: unsupervised clustering, explained variance vs **permutation null**,
cross-pair recurrence. Standardized Euclidean (not cosine).

Deliverable: `latent_structure_report.md`
Implementation: `src/research/latent_structure.py`

---

# STILL FORBIDDEN (until Chief approval)

```text
Latent State Library · Adaptive Interaction Engine · Payoff Engine · ML
```

And, newly binding:

```text
No human market taxonomy may enter a scientific finding before the data
demonstrates the structure.
```

---

# CARRY-FORWARD (UNCHANGED)

All of V5.8 remains in force EXCEPT: Phase 5.9's mechanism method and names are
rejected; F-015 is reframed and OPEN; "Mechanism Library"→"Latent State Library".
F-001…F-014, R-001/R-002, Principles 01–03, 12, 13, the Market Lifecycle Model,
the three component categories, and "Profitable ≠ Tradable Edge" all stand.

---

# FINAL PRINCIPLE

```text
No human market theory.
Let the data speak first; name last.

Discovery is not verification.
Find the structure before you label it.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DOCTRINE_V5.9.md**
