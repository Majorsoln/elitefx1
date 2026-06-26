# ELITEFX_DOCTRINE_V5.8.md

**Chief Quant Amendment — Universal Mechanisms, Local Coordinates**

Version: 5.8
Status: Superseded by V5.9 (current SSOT) — carry-forward in force
Date: 25 June 2026
Authority: Single Source of Truth (superseded by V5.9, 25 June 2026)
Supersedes: V5.7 (records F-014; opens F-015; inserts Mechanism Layer)
Previous Versions: Archived (V4, V4.1, V5.0, V5.1, V5.2, V5.3, V5.4, V5.5, V5.6, V5.7)

> ⚠️ **IMESASISHWA:** SSOT rasmi sasa ni **[ELITEFX DOCTRINE V5.9](ELITEFX%20DOCTRINE%20V5.9.md)**
> (Phase 5.9 mechanism method REJECTED — human taxonomy; F-015 reframed to "Latent
> Market Structures", OPEN; Mechanism Library → Latent State Library). V5.8 carry-forward
> EXCEPT the Mechanism-name framing, which V5.9 rejects.

> Live program status lives in `docs/PROGRAM_BOARD.md`. This file is the doctrine
> of record; V5.0–V5.7 remain in force except where amended below.

---

# EXECUTIVE AMENDMENT

Phase 5.8 (`interaction_stability_report.md`) **falsified** the universal-rules
hypothesis: 0/20 interactions were stable across pairs. Scientific process — we
do not defend hypotheses, we replace them when falsified.

```text
F-014  Interaction Structure is NOT Universal. It is Pair-Specific.
```

But a deeper reading suggests the interaction still exists — what changes is the
**mapping**, not the **mechanism**:

```text
F-015  Universal Mechanisms, Local Coordinates  (hypothesis under test)
```

```text
Markets have different COORDINATES, but the same PHYSICS.
```

---

# FINDING F-014 — Interaction Structure Is Pair-Specific

In the feature **coordinate space** (LOW/NORMAL/HIGH cells), no interaction
generalises:

```text
0/20 interactions universal (rank consistency ≥ 0.3 and modal best ≥ 50% pairs).
```

Therefore we will **not** build a rule engine keyed on cell IDs. Status:
**APPROVED.** Q-011 CLOSED (universal rules do not exist in coordinate space).

---

# FINDING F-015 — Universal Mechanisms, Local Coordinates (HYPOTHESIS)

The interaction is real; only its coordinates are local:

```text
EURUSD best:  HIGH × HIGH × Tmid
GBPJPY best:  LOW  × NORMAL × Thi
```

These different cells may describe the **same mechanism** — e.g. *Transition into
Expansion*. So the system needs an abstraction:

```text
Coordinate:  HIGH × HIGH × Tmid   (pair-local)
Mechanism:   "Expansion Ready"     (universal)
```

Status: **APPROVED as a hypothesis to verify** (Phase 5.9). The decisive test is
**mechanism similarity**, not cell similarity — rank/Spearman over labels
*underestimates* it (HIGH×HIGH×Tmid and NORMAL×HIGH×Tmid may be almost
identical mechanisms).

---

# DOCTRINE CORRECTION — Interaction Engine Learns Mechanisms

Removed (rejected):

```text
Interaction Engine learns best interaction cells.
```

Replaced (official):

```text
Interaction Engine learns Market Mechanisms.
Each Pair maps its own coordinates to those mechanisms.
```

A **Mechanism Layer** is inserted between Transition and Pair Mapping.

---

# UPDATED ARCHITECTURE

```text
Volume Bars
↓
State Detection
↓
Lifecycle                 (F-013)
↓
Transition
↓
Mechanism Mapping         ← NEW (F-015): coordinate → universal mechanism
↓
Pair Coordinate Mapping   (each pair's local coordinates)
↓
Market State Vector
↓
Opportunity
↓
Payoff
```

This is **representation learning** — without ML yet. That is the institutional
approach: learn the representation (mechanisms) before fitting any model.

---

# UPDATED ROADMAP

```text
Phase 5.8   Interaction Stability         COMPLETE   (F-014; universal rules falsified)
Phase 5.9   Mechanism Discovery           NEXT       (F-015: same mechanism, different cells?)
Phase 6     Mechanism Library             BLOCKED    (catalogue of universal mechanisms)
Phase 7     Adaptive Interaction Engine   BLOCKED    (per-pair coordinate mapping)
Phase 8     Market State Vector           BLOCKED
Phase 9     Payoff Engine                 BLOCKED
Phase 10    Machine Learning              BLOCKED
```

## Phase 5.9 — Mechanism Discovery (NEXT)

For Tier-1 events, characterise each pair's best interaction cells by an
**environmental signature** independent of LOW/NORMAL/HIGH labels (volatility
level/slope, activity level/slope, spread, lifecycle age, transition), name a
candidate mechanism (Expansion/Exhaustion/Compression/Recovery), and test:

```text
Do different best cells across pairs share the same mechanism?
Mechanism agreement  >>  cell-label agreement   →  F-015 supported.
```

Deliverable: `mechanism_discovery_report.md`
Implementation: `src/research/mechanism_discovery.py`

The decisive metric is **mechanism similarity** (signature), not cell similarity
(label).

---

# STILL FORBIDDEN (until Chief approval)

```text
Mechanism Library · Adaptive Interaction Engine · Payoff Engine · ML
```

ML is deferred until the mechanism representation is established. We are doing
representation discovery first.

---

# CARRY-FORWARD (UNCHANGED)

All of V5.7 remains in force: Findings F-001…F-013, R-001/R-002, Principles
01–03, 12, 13, Event Priority Tiers, payoff mechanism groups, the three
component categories (Driver/Gatekeeper/Lifecycle), the Market Lifecycle Model,
and "Profitable ≠ Tradable Edge".

---

# FINAL PRINCIPLE

```text
Different coordinates, same physics.

The edge is a mechanism, not a cell.
Learn the representation before the model.

Universal rules do not exist in coordinate space —
they may exist in latent market behaviour. That is the next question.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DOCTRINE_V5.8.md**
