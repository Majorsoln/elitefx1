# ELITEFX_DOCTRINE_V5.13.md

**Chief Quant — Phase 5 Closed; Interaction Engine; Selection Over Prediction**

Version: 5.13
Status: Superseded by V5.14 (current SSOT) — carry-forward in force
Date: 26 June 2026
Authority: Single Source of Truth (superseded by V5.14, 26 June 2026)
Supersedes: V5.12 (closes Phase 5; F-019, F-020; Principle 20, 21; Interaction Engine)
Previous Versions: Archived (V4 … V5.12)

> ⚠️ **IMESASISHWA:** SSOT rasmi sasa ni **[ELITEFX DOCTRINE V5.14](ELITEFX%20DOCTRINE%20V5.14.md)**
> (F-020 APPROVED; F-021 hakuna universal edge; Principle 22 opportunity =
> Configuration; Market Configuration = Event+State+Pair+Regime+Direction+Execution;
> H-07; Phase 6.5 Configuration Engine). V5.13 carry-forward.

> Live program status lives in `docs/PROGRAM_BOARD.md`. This file is the doctrine
> of record; V5.0–V5.12 remain in force except where amended below.

---

# EXECUTIVE AMENDMENT — PHASE 5 CLOSED

Phase 5.13 (`representation_value_report.md`) answered the foundational question of
quantitative trading — *does this information change the quality of decisions?* —
and **Phase 5 is now officially closed.**

The next step is **not** Machine Learning. It is the **Interaction Engine**,
because that is where we test whether the edge lives in the event, in the market
configuration, or in the interaction of the two.

---

# FINDING F-019 — The Value Law (APPROVED)

```text
Information has value only if it changes
Expected Payoff or Decision Quality.
```

This is now the supreme rule of ELITEFX.

---

# FINDING F-020 — Event × Configuration (EXPERIMENTAL)

```text
Trading Edge may emerge from Event × Configuration interactions,
not from Events alone.
```

Phase 5.13 already showed EV varies strongly across latent clusters, and that
selection by representation changes the EV of some events. But Event × Cluster was
not yet measured directly. That is Phase 6.

Status: **OPEN — under test** (Phase 6 Interaction Engine).

---

# PRINCIPLE 20 — Feature Competition

```text
Every new feature must compete against the current system.
If it does not improve Expected Value or Probability Calibration,
it shall be rejected.
```

Institutional feature selection: nothing is added on intuition; it must beat the
incumbent.

---

# PRINCIPLE 21 — Selection Over Prediction

Phase 5.13 showed the representation improved **EV-selection** but **not LogLoss**.
It did not change the *prediction*; it changed the *choice*.

```text
Selection is more valuable than Prediction.
```

Institutional trading does not build a better forecast; it builds a better
**choice**.

---

# UPDATED PIPELINE (official)

```text
OLD:  States → Opportunity → Trade

NEW:  Events
      ↓
      Market Configuration
      ↓
      Interaction Engine        ← Phase 6
      ↓
      Expected Payoff
      ↓
      Opportunity Ranking
      ↓
      Trade Lifecycle
```

---

# NEW ACCEPTANCE RULE

```text
No Event enters the Opportunity Engine until it shows:
    Event × Market Configuration → Expected Payoff
(not the Event alone).
```

---

# PHASE 6 — Interaction Engine (NEXT)

For each event (Pullback, Deep Pullback, Trend Continuation, Breakout, Mean
Reversion), measure per latent state:

```text
EV (± 95% confidence interval) · Win rate · Triple Barrier outcomes · Sample size
```

So we can say "Pullback works ONLY inside State X" or "Breakout dies inside State
Y". This is where the Opportunity Engine is born.

Deliverable: `event_state_interaction_report.md`
Implementation: `src/research/event_state_interaction.py`

---

# MACHINE LEARNING — Still Deferred

No LightGBM yet. ML cannot discover interactions well if we ourselves do not yet
know the interaction exists — and we have **not built a good target**. The
Interaction Engine builds that understanding first.

---

# UPDATED ROADMAP

```text
Phase 5      CLOSED   (state/context/payoff/representation foundation complete)
Phase 6      Interaction Engine          NEXT     (Event × State EV/CI/TB)
Phase 7      Opportunity Engine          BLOCKED  (ranks Expected Payoff)
Phase 8      Payoff Engine               BLOCKED
Phase 9      Machine Learning            BLOCKED  (after a good target exists)
```

---

# STILL FORBIDDEN (until Chief approval)

```text
Opportunity Engine · Payoff Engine · ML (LightGBM/RF/XGBoost)
```

Binding rules: **decision quality over algorithm agreement** (P18); **survival =
EV/decision-quality improvement** (P19); **feature competition** (P20);
**selection over prediction** (P21); **Event × Configuration before any Event
enters Opportunity** (acceptance rule).

---

# CARRY-FORWARD (UNCHANGED)

All of V5.12 in force: F-016 (latent structures), F-017 Experimental, F-018
(Decision Robustness), Principles 18–19, H-06 (rare = execution risk), the
Trading-Science / Market-Configuration architecture, and "Profitable ≠ Tradable
Edge".

---

# FINAL PRINCIPLE

```text
The edge is in the event, the configuration, or their interaction —
Phase 6 tells us which.

Selection over prediction.
Information survives only if it changes Expected Payoff or Decision Quality.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DOCTRINE_V5.13.md**
