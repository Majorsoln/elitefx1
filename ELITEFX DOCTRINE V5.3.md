# ELITEFX_DOCTRINE_V5.3.md

**Chief Quant Amendment — Information Density & Context Generalization**

Version: 5.3
Status: APPROVED — ACTIVE (current SSOT)
Date: 24 June 2026
Authority: Single Source of Truth (SSOT)
Supersedes: V5.2 (records two new approved findings; corrects Volume Bars principle)
Previous Versions: Archived (V4, V4.1, V5.0, V5.1, V5.2)

> Live program status (phases, ledger, approvals) lives in
> `docs/PROGRAM_BOARD.md`. This file is the doctrine of record; V5.0–V5.2 remain
> in force except where amended below.

---

# EXECUTIVE AMENDMENT

V5.3 records two findings the data has now earned, and corrects one assumption:

```text
F-006  Context Value Generalizes Across Event Families
F-007  Volume Bars Increase Information Density
```

```text
CORRECTED:  Volume Bars exist because they stabilize states.   ← WRONG
OFFICIAL :  Volume Bars exist because they concentrate information.
            Information Density > Calendar Uniformity.
```

For the first time the architecture reads as **one connected system**, each
layer carrying its own evidence:

```text
Market
↓
Volume Representation     (F-007 — information density)
↓
States                    (F-001, F-002)
↓
State Age                 (F-003, F-004 — calibration)
↓
Transitions               (Phase 1.5/1.8)
↓
Context Filter            (F-005, F-006 — Principle 12)
```

The decision metric remains **Expected Value (EV > 0), not win rate.**

---

# FINDING F-006 — Context Value Generalizes Across Event Families

Source: `context_generalization_report.md` (Phase 1.95).

The Phase 1.9 result (Context adds economic value) was at risk of being
specific to **one** event (Trend Pullback). Phase 1.95 tested two more KJ
event families and the value held:

```text
Trend Pullback   → Context adds value
Breakout         → Context adds value
Mean Reversion   → Context adds value
```

…across all three state dimensions (volatility, activity, spread) at varying
strength. Therefore:

```text
Context ≠ Alpha
Context = Opportunity Filter        (Principle 12, now broadly evidenced)
```

Status: **APPROVED.** Q-001 CLOSED.

---

# FINDING F-007 — Volume Bars Increase Information Density

Source: `adaptive_volume_bar_report.md` (Phase 2) + `volume_information_report.md`
(Phase 2.1).

Phase 2 **rejected** the stability hypothesis (R-002): adaptive volume bars did
not produce more stable state distributions than calendar bars (0/9 volatility,
0/9 activity). But Phase 2.1 asked the deeper question — do they carry more
**information**? — and the answer was emphatic (18/18 dim×pair on
predictability ∨ context value):

```text
                    Calendar → Volume
State persistence        ↑
State age effect          ↑   (near-doubled, esp. activity)
Transition predictability ↑   (activity LogLoss 0.84 → 0.63, acc +12pp)
Context utility           ↑   (EV uplift improved in most pairs)
```

Conclusion (OFFICIAL):

```text
Volume bars do not improve stability.
Volume bars improve information:
  persistence · age effect · transition predictability · context utility.
Therefore volume bars remain the PREFERRED market representation.
```

Status: **APPROVED.** (PROGRAM_BOARD R-002 rejected stability; F-007 approves
information density.)

---

# DOCTRINE CORRECTION — Volume Bars Rationale

Remove (rejected):

```text
Volume Bars exist because they stabilize states.
```

Replace (official):

```text
Volume Bars exist because they concentrate information.

Information Density > Calendar Uniformity.
```

Volume Bars are **not** uniform in clock-time and are **not** more stable — and
that is fine. Their value is that equal-information bars sharpen persistence,
duration-dependence, transition predictability and context utility. This
supersedes the V5.2 note "Volume Bars → Alternative Representation, UNPROVEN":
it is now **PROVEN as information density** (F-007).

---

# UPDATED DEVELOPMENT ROADMAP

```text
Phase 0     Data Validation              COMPLETE
Phase 1     State Engine                 COMPLETE
Phase 1.5   Transition Engine            COMPLETE
Phase 1.6   State Age                    COMPLETE
Phase 1.7   State Context Engine         COMPLETE
Phase 1.8   Transition Model             COMPLETE   (age = calibrator)
Phase 1.9   Context Economic Value       COMPLETE   (F-005; context = filter)
Phase 1.95  Context Generalization       COMPLETE   (F-006)
Phase 2     Adaptive Volume Bars         COMPLETE   (R-002 stability rejected; F-007 information)
Phase 2.1   Volume Information Value      COMPLETE   (F-007)
Phase 3     Event Diagnostics            NEXT       (events × context, no outcomes)
Phase 4     Event × Context Matrix
Phase 5     Triple Barrier Framework     BLOCKED (Chief approval)
Phase 6     Outcome Engine               BLOCKED
Phase 9     Machine Learning Models      BLOCKED
Phase 10    Production Deployment
```

## Phase 3 — Event Diagnostics (NEXT)

We stop researching market states (proven) and volume bars (answered) and move
to **Events**. For each KJ event, map — **without outcomes, without ML** — how
it occurs inside context:

```text
Frequency · Context Coverage · State Distribution · Age Distribution
· Transition Distribution
```

Deliverable: `event_diagnostics_report.md`
Implementation: `src/research/event_diagnostics.py` (+ `event_library.py`, the
single source for all 9 KJ event signals).

---

# STILL FORBIDDEN (until Chief approval)

```text
Triple Barrier · LightGBM · Random Forest · Outcome Models
```

Reason: the Event Layer is not yet fully characterised. No ML may search for
alpha before the event structure is mapped (Phase 3) and the Event × Context
matrix is built (Phase 4).

---

# CARRY-FORWARD (UNCHANGED)

All of V5.2 remains in force except the Volume Bars rationale corrected above:
Principles 01–03 and 12 (Context Is A Filter), Amendments 1–4 (Context Engine,
age = calibrator, Event × Context Rule), Findings A–E, R-001 (H-01 rejected),
and the EV-not-win-rate decision metric.

---

# FINAL PRINCIPLE

```text
Predict less.        Measure more.
Assume less.         Validate more.
Context first.       Events second.
Information density. Not clock uniformity.

Protect capital first.
Seek edge second.
Scale only after proof.
```

**END OF ELITEFX_DOCTRINE_V5.3.md**
