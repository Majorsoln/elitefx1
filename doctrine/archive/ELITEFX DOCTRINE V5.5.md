# ELITEFX_DOCTRINE_V5.5.md

**Chief Quant Amendment — Context Is A Payoff Filter (Mechanism Discovered)**

Version: 5.5
Status: Superseded by V5.6 (current SSOT) — carry-forward in force
Date: 24 June 2026
Authority: Single Source of Truth (superseded by V5.6, 25 June 2026)
Supersedes: V5.4 (records F-010, F-011; opens Payoff Engine direction)
Previous Versions: Archived (V4, V4.1, V5.0, V5.1, V5.2, V5.3, V5.4)

> ⚠️ **IMESASISHWA:** SSOT rasmi sasa ni **[ELITEFX DOCTRINE V5.6](ELITEFX%20DOCTRINE%20V5.6.md)**
> (F-012 Interactions not Individual Features; Driver ≠ Gatekeeper; Interaction
> Engine). Payoff Engine FROZEN hadi interaction structure ithibitishwe. V5.5 carry-forward.

> Live program status lives in `docs/PROGRAM_BOARD.md`. This file is the doctrine
> of record; V5.0–V5.4 remain in force except where amended below.

---

# EXECUTIVE AMENDMENT

Phase 5.5 (`outcome_decomposition_report.md`) gave the project its first
**mechanism, not correlation** — the line between institutional quant and retail
backtest. Two findings:

```text
F-010  Context improves PAYOFF DISTRIBUTION, not WIN PROBABILITY.
F-011  Tier-1 events split into TWO payoff mechanisms.
```

The architecture changes shape:

```text
OLD:  Context → Higher Win Rate
NEW:  Context → Better Payoff Distribution → Higher Expected Value
```

---

# FINDING F-010 — Context Is A Payoff Filter

Decomposing EV = P(win)·AvgWin − P(loss)·AvgLoss by context decile (Tier-1):

```text
ΔP(win) D10−D1 ≈ +3pp  (small, all four events)
ΔEV     D10−D1 ≈ +4 pips  (large)
```

The EV uplift is **not** a hit-rate effect. It comes from winner size and/or
loss size. Therefore (OFFICIAL):

```text
Context ≠ Probability Filter
Context = Payoff Filter
```

Consistent with Phase 1.9 (win-rate flat, EV up) and Phase 5 (P(TP) flat across
deciles). Status: **APPROVED.** Q-008 CLOSED.

---

# FINDING F-011 — Tier-1 Has Two Payoff Mechanisms

```text
Group A — Reward Expansion (AvgWin grows with context)
  Mean Reversion      ΔAvgWin +3.6
  Deep Pullback       ΔAvgWin +3.1

Group B — Loss Compression (AvgLoss shrinks with context)
  Pullback            ΔAvgLoss −2.4
  Trend Continuation  ΔAvgLoss −2.8
```

Tier-1 events are **not interchangeable**. The Event Library must be organised
by **payoff mechanism**, not by event name alone. Status: **APPROVED.**

---

# NEW DIRECTION — Expected Payoff Engine

The Opportunity Engine no longer outputs a binary decision:

```text
OLD output:  Trade  YES / NO
NEW output:  Expected Distribution
```

For an input `(Pair + Event + Context)` it returns:

```text
Expected Winner
Expected Loser
Expected Holding Time
Expected Tail Size
Expected Variance
```

Example:

```text
EURGBP · Pullback · Context 0.91
  → Expected Winner 42 pips · Expected Loser 23 pips · Expected Time 5 bars
```

The system stops asking *"Will I win?"* and asks *"If I win, how much; if I
lose, how much?"* This is institutional thinking. ML, when finally allowed, will
predict the **distribution**, not TP.

---

# UPDATED ROADMAP

```text
Phase 5     Triple Barrier (Tier 1)      RESOLVED   (P(TP) flat — explained by F-010)
Phase 5.5   Outcome Decomposition        COMPLETE   (F-010, F-011)
Phase 5.6   Payoff Attribution           NEXT       (which context components drive payoff?)
Phase 6     Payoff Distribution Engine   QUEUED     (Expected Winner/Loser/Time/Tail/Var)
Phase 7     Trade Lifecycle Controller   BLOCKED
Phase 8     Machine Learning             BLOCKED    (predict DISTRIBUTION, not TP)
```

Program direction (revised):

```text
Outcome Engine → Payoff Engine → Trade Lifecycle → ML
```

## Phase 5.6 — Payoff Attribution (mechanism → cause)

F-011 gives the *mechanism* (reward vs loss) but not the *cause*. Phase 5.6
decomposes the context score into components (volatility, activity, spread,
state age, transition probability) and attributes AvgWin / AvgLoss separation
to each — so the Payoff Engine is built on **real causes**, not a blended score.

Deliverable: `payoff_attribution_report.md`
Implementation: `src/research/payoff_attribution.py`

---

# STILL FORBIDDEN (until Chief approval)

```text
LightGBM · Random Forest · XGBoost · Outcome/ML Models
```

ML is reserved for predicting the **payoff distribution**, and only after
attribution (5.6) and the Payoff Engine design (6) are established on Tier-1.

---

# CARRY-FORWARD (UNCHANGED)

All of V5.4 remains in force: Findings F-001…F-009, R-001/R-002, Principles
01–03, 12, 13, the Event Priority Tiers, the
Volume→State→Age→Transition→Context-Score→Event-Ranking architecture, and
"Profitable ≠ Tradable Edge".

---

# FINAL PRINCIPLE

```text
Not "Will I win?" but "If I win, how much; if I lose, how much?"

Context shapes the payoff distribution.
Mechanism before model. Cause before prediction.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DOCTRINE_V5.5.md**
