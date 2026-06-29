# ELITEFX_DOCTRINE_V6.0.md

**Chief Quant — ELITEFX Architecture V6: No Universal Representation; Variables Are Conditional; Events May Contain Sub-Events**

Version: 6.0
Status: Superseded by V6.1 (current SSOT) — carry-forward in force
Date: 28 June 2026
Authority: Single Source of Truth (superseded by V6.1, 28 June 2026)
Supersedes: V5.25 (F-036; Principle 38; F-037; Market Representation → Event Representation Family; Architecture V6; Phase 18 Event Taxonomy)
Previous Versions: Archived (V4 … V5.25)

> ⚠️ **IMESASISHWA:** SSOT rasmi sasa ni **[ELITEFX DOCTRINE V6.1](ELITEFX%20DOCTRINE%20V6.1.md)**
> (F-037 → Partially Approved; F-038 taxonomy hierarchical & event-specific; Principle 39
> ontology si algorithm moja; Principle 40 taxonomy ≠ alpha; Phase 19 Taxonomy Robustness
> Audit). V6.0 carry-forward.

> Live program status lives in `docs/PROGRAM_BOARD.md`. This file is the doctrine
> of record; V5.0–V5.25 remain in force except where amended below.

---

# EXECUTIVE AMENDMENT — THE TURNING POINT (ONTOLOGY, NOT OPTIMIZATION)

Phase 17 is the largest turning point of the project. Not because of a big R², not
because it found an edge — because it discovered the **correct ontology of the
market**. That is the difference between science and optimization.

What the Chief had wrong, now corrected by data:

```text
WAS:   Market → Context → Event
THEN:  Event → Context
NOW:   Context has no existence of its own — the Event creates the meaning of context.
```

Activity is meaningless for Breakout, but matters for Mean Reversion and Pullback,
and behaves differently for Trend Continuation. So Activity is not a variable — it is
an **Event-conditioned variable**.

---

# FINDING F-036 — Variables Are Conditional Entities (APPROVED)

```text
Market variables are conditional entities;
their information content depends on the governing Event.
```

Terminology: **Variable → Conditional Variable**. A variable does not exist outside
an Event.

---

# PRINCIPLE 38 — No Universal Representation (APPROVED)

```text
There shall be no universal market representation.
Each Event defines its own representation space.
```

Phase 17 Q4 showed Mean Reversion needs {Spread, Activity, Pair} while Breakout needs
{Session, Spread, Pair, Volatility}. Representation is **event-local**.

The concept **"Market Representation" is replaced by "Event Representation Family":**

```text
Pullback Representation · Deep Pullback Representation · Breakout Representation ·
Mean Reversion Representation · Trend Continuation Representation
```

Each with its own ontology.

---

# FINDING F-037 — Events May Contain Sub-Events (OPEN)

```text
Events may themselves consist of multiple latent sub-events
with different statistical identities.
```

Mean Reversion at LOW VOL may be a different event from Mean Reversion at HIGH VOL:

```text
Mean Reversion → { MR-LowVol, MR-HighVol, MR-News, MR-Range }
```

Status: **OPEN — under test** (Phase 18 Event Taxonomy).

---

# ELITEFX ARCHITECTURE V6 (official)

```text
Market
  ↓
Event Detection
  ↓
Event Taxonomy            ← Phase 18 (latent sub-events)
  ↓
Event-Specific Representation   (Event Representation Family; Principle 38)
  ↓
Reality Validation        (per-event/subtype OOS + FDR; Principle 37)
  ↓
Opportunity Engine
  ↓
Portfolio Engine
  ↓
Execution Engine
```

---

# PHASE 18 — Event Taxonomy (NEXT)

Goal: not to find alpha directly, but to determine whether each event is composed of
sub-events with different statistical identities.

```text
Q1. Does Mean Reversion have subtypes?
Q2. Does Breakout have subtypes?
Q3. Does Pullback have subtypes?
Q4. Does the Event Representation change by subtype?
Q5. Do some sub-events carry alpha — instead of the whole event?
```

Method: unsupervised KMeans (numpy) over context features; feature-structure gap vs
permutation null; outcome-identity R²(label on y), permutation-controlled; per-subtype
EV. In-sample discovery (OOS confirmation later, Principle 37).

Deliverable: `reports/event_taxonomy_report.md`
Implementation: `src/research/event_taxonomy_engine.py`

---

# MACHINE LEARNING — The Target Is Now Clear (still deferred)

For the first time the ML target is clear. ML will not be trained on "the market". It
will be trained on **a single Event subtype**:

```text
One model for Mean Reversion · another for Breakout · another for Pullback —
not one model for the whole market.
```

Still deferred until the taxonomy and event-specific representations are validated OOS.

---

# THE NEW OFFICIAL GOAL OF ELITEFX

```text
Build a FAMILY of Event-dependent representations,
and later a FAMILY of Event-dependent models.
```

Not one representation of the market. Not one model of the market.

---

# UPDATED ROADMAP

```text
Phase 17     CLOSED   (Event-Centric Representation; F-035/F-036; Event Representation Family)
Phase 18     Event Taxonomy              NEXT     (latent sub-events per event; no ML)
Phase 19     Event-Subtype Confirmation  BLOCKED  (per-subtype OOS + FDR; Principle 37)
Phase 20     Event-Specific Opportunity  BLOCKED
Phase 21     Portfolio Engine            BLOCKED
Phase 22     Machine Learning            BLOCKED  (one model per event subtype)
```

---

# STILL FORBIDDEN (until Chief approval)

```text
Universal representation · Universal model · Opportunity Engine v2 · Portfolio Engine · ML
```

Binding rules (Principles 18–38): … (carry-forward) … **Events are the semantic
anchors** (P36); **significance + OOS over effect size in low S/N** (P37); **no
universal representation — each Event defines its own representation space** (P38).
Core findings: state variables derive meaning through Events (F-035); variables are
conditional entities (F-036); events may contain latent sub-events (F-037).

---

# CARRY-FORWARD (UNCHANGED)

All of V5.25 in force: F-016–F-035, Principles 18–37, H-06, Research Foundation
closed, Confirmation Framework, Event Reality Validation, and "Profitable ≠ Tradable
Edge".

---

# FINAL PRINCIPLE

```text
The Event creates the meaning of context; variables are conditional, not universal.
There is no one representation of the market — there is a family, one per Event,
and perhaps one per sub-event.
We build a family of event-dependent representations, then a family of event-dependent models.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DOCTRINE_V6.0.md**
