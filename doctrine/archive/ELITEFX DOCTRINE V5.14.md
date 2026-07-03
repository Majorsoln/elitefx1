# ELITEFX_DOCTRINE_V5.14.md

**Chief Quant — Edge = Event × Market Configuration; Configuration as the Atomic Trading Unit**

Version: 5.14
Status: Superseded by V5.15 (current SSOT) — carry-forward in force
Date: 26 June 2026
Authority: Single Source of Truth (superseded by V5.15, 26 June 2026)
Supersedes: V5.13 (F-020 Approved; F-021; Principle 22; Market Configuration redefined; H-07; Phase 6.5 Configuration Engine)
Previous Versions: Archived (V4 … V5.13)

> ⚠️ **IMESASISHWA:** SSOT rasmi sasa ni **[ELITEFX DOCTRINE V5.15](ELITEFX%20DOCTRINE%20V5.15.md)**
> (Research Foundation CLOSED; H-07→F-022 APPROVED; F-023 ranking native language;
> F-024 confidence = payoff value; Principle 23 rank-don't-classify; Principle 24
> no-ranking-by-EV-alone; Configuration = final atomic unit; Phase 7 Confidence
> Engine). V5.14 carry-forward.

> Live program status lives in `docs/PROGRAM_BOARD.md`. This file is the doctrine
> of record; V5.0–V5.13 remain in force except where amended below.

---

# EXECUTIVE AMENDMENT — THE TURNING POINT

Phase 6 (Interaction Engine, `event_state_interaction_report.md`) gave the project
its first hard evidence of the central truth of quantitative trading:

```text
Edge  ≠  Event
Edge  =  Event × Market Configuration
```

For 4 of 5 events, Expected Value changes substantially with the latent state, and
some combinations outperform the event alone. The retail question "Does Pullback
work?" is replaced by the institutional question "In WHICH market configuration
does Pullback work?".

This closes the journey **Indicators → Events → States → Market Configuration**.

---

# FINDING F-020 — Event × Configuration (APPROVED)

```text
Trading edge emerges from Event × Market Configuration interactions,
not from events alone.
```

Status upgraded **EXPERIMENTAL → APPROVED**. This is now official doctrine.

---

# FINDING F-021 — No Universal Edge (APPROVED)

The decisive observation Phase 6 surfaced: **every event still has negative EV on
average** (pullback, continuation, breakout). This is not failure — it is proof
the architecture is right. We are still only running `Event → State`; we have not
yet used Pair, Regime, Direction, and Execution context.

```text
No Event possesses universal edge.
Edge exists only inside a COMPLETE Market Configuration.
```

Status: **APPROVED**. The event alone is not enough; the event inside a
configuration changes Expected Value.

---

# PRINCIPLE 22 — Opportunity is a Configuration, never an Event

```text
A trading opportunity shall never be represented by an Event.
It shall always be represented by a Market Configuration.
```

This is the principle the Opportunity Engine will be built upon.

---

# MARKET CONFIGURATION — REDEFINED (the atomic trading unit)

The Opportunity Engine will no longer use `Event × State` alone. A Market
Configuration — the **atomic trading unit** of ELITEFX — is:

```text
Market Configuration = Event
                     + Latent State
                     + Pair
                     + Regime
                     + Direction
                     + Execution Context
```

Not an event. Not a signal. A **Configuration**.

---

# NEW ACCEPTANCE RULE

```text
No strategy enters the system until it can be expressed as
    Market Configuration → Expected Payoff
(instead of  Indicator → BUY).
```

---

# HYPOTHESIS H-07 — Negative Edge More Stable Than Positive Edge (OPEN)

State C2 was poor across nearly all events in Phase 6. This reframes the question
from "which state is good?" to "which state must NOT be traded?". Institutional
systems do not chase "trade more"; they seek **trade less, but in the right
environment**.

```text
H-07  Negative Edge is more stable than Positive Edge.
```

Test: does **removing bad configurations** improve Expected Value more than
**adding good ones**? (out-of-sample, no-lookahead). Knowing *where NOT to trade*
may be worth more than knowing *where to trade*. Status: **OPEN** (Phase 6.5).

---

# PHASE 6.5 — Configuration Engine (NEXT)

Build the **Configuration Objects** that will become the basis of the Opportunity
Engine — not signals. For each Configuration (Pair + Event + Latent State + Regime
+ Direction + Execution Context) measure:

```text
EV · Win rate · Triple Barrier outcomes · Sample size ·
Confidence interval · Walk-forward stability
```

H-07 is tested inside the same engine (remove-bad vs add-good, out-of-sample).

Deliverable: `reports/configuration_engine_report.md`
Implementation: `src/research/configuration_engine.py`

---

# UPDATED PIPELINE (official)

```text
Events
  ↓
Market Configuration        ← Event + State + Pair + Regime + Direction + Execution
  ↓
Configuration Engine        ← Phase 6.5 (atomic trading unit; EV/CI/TB/stability)
  ↓
Expected Payoff
  ↓
Opportunity Ranking
  ↓
Trade Lifecycle
```

---

# MACHINE LEARNING — A Target Begins to Appear

The ML target is now coming into view, but we have **not** reached it. ML will not
predict BUY/SELL; it will predict the **Expected Payoff of a Configuration**. That
is a target with meaning — and it requires the Configuration Engine first.

---

# UPDATED ROADMAP

```text
Phase 6      CLOSED   (Interaction Engine; F-020 APPROVED)
Phase 6.5    Configuration Engine        NEXT     (Configuration Objects; EV/CI/TB/stability; H-07)
Phase 7      Opportunity Engine          BLOCKED  (ranks Expected Payoff of Configurations)
Phase 8      Payoff Engine               BLOCKED
Phase 9      Machine Learning            BLOCKED  (predicts Expected Payoff of a Configuration)
```

---

# STILL FORBIDDEN (until Chief approval)

```text
Opportunity Engine · Payoff Engine · ML (LightGBM/RF/XGBoost)
```

Binding rules: **decision quality over algorithm agreement** (P18); **survival =
EV/decision-quality improvement** (P19); **feature competition** (P20);
**selection over prediction** (P21); **opportunity = Configuration, never an
Event** (P22); **Market Configuration → Expected Payoff before any strategy
enters** (acceptance rule).

---

# CARRY-FORWARD (UNCHANGED)

All of V5.13 in force: F-016 (latent structures), F-017 Experimental, F-018
(Decision Robustness), F-019 (Value Law), Principles 18–21, H-06 (rare = execution
risk), the Trading-Science / Market-Configuration architecture, and "Profitable ≠
Tradable Edge".

---

# FINAL PRINCIPLE

```text
No event has a universal edge.
Edge lives only inside a complete Market Configuration.

A trading opportunity is a Configuration, never an Event.
Trade less, but in the right environment —
where NOT to trade may be worth more than where to trade.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DOCTRINE_V5.14.md**
