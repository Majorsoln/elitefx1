# ELITEFX_DOCTRINE_V6.6.md

**Chief Quant — The Market May Be Built From a Few Reusable Primitives; Compression Is the First Candidate**

Version: 6.6
Status: APPROVED — ACTIVE (current SSOT)
Date: 30 June 2026
Authority: Single Source of Truth (SSOT)
Supersedes: V6.5 (Phase 23 APPROVED; "Universal Vocabulary" → "Emerging Core Vocabulary"; Principle 51/52; F-041; Market Primitives; architecture inverted; Phase 24 Market Primitive Validation)
Previous Versions: Archived (V4 … V6.5)

> Live program status lives in `docs/PROGRAM_BOARD.md`. This file is the doctrine
> of record; V5.0–V6.5 remain in force except where amended below.

---

# EXECUTIVE AMENDMENT — FROM SEMANTICS TO MARKET PRIMITIVES

Phase 23 is **APPROVED**, and it is the **end of the "Semantic Engineering Era"**. We proved we
can give the market an interpretable language. But the report pointed at something larger than
its own verdict.

**Careful wording (Chief).** The report said "vocabulary is consistent & shows universality".
That is too strong: only **2/5** labels are consistent, and only **`Compression (Quiet Coil)`**
is truly consistent across events (within/overall ≈ 0.25, tiny cross-event spread). `Balanced
Flow` and `High-Volatility Regime` still vary. So the correct term is not "Universal Vocabulary"
but:

```text
Emerging Core Vocabulary.
```

---

# THE REAL DISCOVERY — MARKET PRIMITIVES

`Compression` recurs almost everywhere. Why? Because it is **not an event, not a pair, not a
geometry — it is a market condition.** The layering inverts:

```text
Old:  Market → Events → Semantics
New:  Market → Market Primitives → Events → Geometry
```

A hidden layer was underneath all along. We name it **Market Primitives** (not "semantic
labels"). `Compression` is the first candidate primitive.

---

# PRINCIPLE 51 — Express Market Knowledge as Reusable Primitives (APPROVED)

```text
Market knowledge shall be expressed through reusable market primitives
rather than event-specific labels.
```

# PRINCIPLE 52 — Semantics Preserves Concepts, Not Clusters (APPROVED)

Q4 gave a data-driven vs rule ARI ≈ 0.62 — **not** a perfect match, and that is **good**. The
gap means there is information our language has not yet described; a semantic system is an
abstraction, not a copy of the clustering.

```text
A semantic system should not aim to reproduce clustering perfectly;
it should aim to preserve the essential market concepts.
```

---

# FINDING F-041 — Universal Market Primitives May Exist (OPEN)

```text
A small set of universal market primitives may underlie multiple event families.
```

Current candidate: **Compression**. Others not yet proven. Status: **OPEN**.

---

# UPDATED ARCHITECTURE

```text
Market
  ↓
Market Primitives           ← NEW top layer (reusable conditions; P51; F-041)
  ↓
Events
  ↓
Representations             (geometry event-specific — F-039)
  ↓
Reality Validation
  ↓
Opportunity
```

---

# PHASE 24 — Market Primitive Validation (NEXT)

The key question: is a primitive a **mechanism** or a **description** (cause or consequence)?

```text
Q1. Does Compression behave the same across all events?
Q2. Does Compression occur BEFORE breakout / pullback / mean_reversion? (precedence)
Q3. Does the primitive have its own transitions? (Compression → Expansion → Exhaustion)
Q4. Can primitives be built WITHOUT using Event labels at all?  ← the key test
Q5. Do primitives speak market language, or are they just names on clusters?
```

Method: build an **event-free** per-bar market-state stream; cluster into primitives (global,
not event-specific); name via the semantic map; measure temporal precedence to events and
primitive→primitive transitions. No ML. If primitives can be built without the Event taxonomy,
we have found a higher layer of market structure.

Deliverable: `reports/market_primitive_validation_report.md`
Implementation: `src/research/market_primitive_validation_engine.py`

---

# MACHINE LEARNING — Still Deferred · ALPHA — Still Deferred (new reason)

```text
No ML. No Alpha Reality Validation yet.
```

New reason for deferring alpha: we do not yet know whether `Compression` is a **cause** or a
**consequence**. That must be answered before any edge work.

---

# UPDATED ROADMAP

```text
Phase 23     CLOSED   (Semantic Consistency; APPROVED; Emerging Core Vocabulary; Compression consistent; end of Semantic Engineering Era)
Phase 24     Market Primitive Validation        NEXT     (event-free primitives; precedence; transitions; mechanism vs description; no ML)
Phase 25     Semantic/Primitive Reality Validation BLOCKED (alpha on validated primitives/states; OOS + FDR; Principle 40)
Phase 26     Machine Learning                   BLOCKED  (learns validated market primitives)
```

---

# STILL FORBIDDEN (until Chief approval)

```text
Calling the vocabulary "universal" (it is emerging) · Alpha Reality Validation (cause/consequence unknown) ·
Semantic/primitive labels in the Opportunity Engine (until validated) · ML · Portfolio Engine · live deployment
```

Binding rules (Principles 18–52): … (carry-forward) … **semantics serves interpretability, not
prediction** (P48); **vocabulary must be stable before doctrine** (P49); **interpretability and
predictability are complementary** (P50); **express market knowledge as reusable primitives**
(P51); **semantics preserves concepts, not clusters** (P52). Core findings: representation
survives OOS (Phase 21); events need different geometries (F-039); a shared vocabulary may span
events (F-040); universal market primitives may exist (F-041, open; candidate Compression).

---

# CARRY-FORWARD (UNCHANGED)

All of V6.5 in force: F-016–F-040, Principles 18–50, H-06, Event Representation Family,
Architecture V6, and "Profitable ≠ Tradable Edge".

---

# FINAL PRINCIPLE

```text
The market may be built from a few reusable primitives that recur across events.
Compression is the first candidate — but a recurring condition is not yet a mechanism.
A primitive must be shown to PRECEDE, to TRANSITION, and to stand WITHOUT event labels
before we trust it; and even then it is structure, not edge.
Cause or consequence is the question — answer it before you seek alpha.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DOCTRINE_V6.6.md**
