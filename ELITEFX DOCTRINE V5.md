# ELITEFX_DOCTRINE_V5.md

**Chief Quant Approved — Institutional Research & Trading Framework**

> ⚠️ **IMESASISHWA:** SSOT rasmi sasa ni
> **[ELITEFX DOCTRINE V5.3](ELITEFX%20DOCTRINE%20V5.3.md)** (Information Density &
> Context Generalization), kupitia V5.2/V5.1. Mtiririko wa core:
> **Volume Representation → State → State Age → Transition → Context Filter → Event**.
> Soma V5.3; live status: `docs/PROGRAM_BOARD.md`. V5.0 hapa ni carry-forward tu.

Version: 5.0
Status: Carry-forward reference (superseded by V5.1 and V5.2)
Authority: Single Source of Truth (SSOT)
Previous Versions: Archived (V4, V4.1)

---

# PART 1 — PHILOSOPHY

## 1.1 Core Belief

Market prediction is not the objective.

The objective is:

```text
Positive Expected Value (EV)
+
Risk Control
+
Survivability
+
Scalability
```

EliteFX does not attempt to predict every market move.

EliteFX seeks to identify situations where:

```text
Expected Reward
>
Expected Risk
```

after:

* spread
* commission
* slippage
* execution friction

---

## 1.2 Market Reality

Markets are:

* noisy
* adaptive
* partially efficient
* non-stationary

Therefore:

```text
No pattern is assumed permanent.
No edge is assumed eternal.
```

Every hypothesis must earn survival.

---

## 1.3 Scientific Method

Every trading idea is treated as a hypothesis.

Lifecycle:

```text
Hypothesis
→ Research
→ Validation
→ Deployment
→ Monitoring
→ Retirement
```

No exceptions.

---

## 1.4 Anti-Overfitting Doctrine

Forbidden:

* feature dumping
* indicator stacking
* data snooping
* parameter mining
* retrospective storytelling

Required:

* holdout
* walk-forward
* cost-adjusted evaluation
* statistical validation

---

# PART 2 — EDGE DOCTRINE

## 2.1 Source of Edge

Edge does NOT come from:

```text
Event alone
Regime alone
ML alone
Indicators alone
```

Edge emerges from:

```text
Event
+
Context
+
Management
+
Risk Allocation
```

---

## 2.2 Event Is Not Edge

Example:

```text
Breakout
```

is not edge.

Example:

```text
EURGBP
+
Range Compression
+
Breakout Failure
+
Adaptive Exit
+
Positive EV
```

may become edge.

---

## 2.3 ML Is Not Edge

Machine learning is a ranking tool.

ML cannot create information.

ML can only:

```text
Discover
Rank
Estimate
```

relationships already present.

---

# PART 3 — MARKET ARCHITECTURE

## 3.1 Dual Time Framework

EliteFX recognizes two clocks.

### Calendar Time

Used for:

* sessions
* weekends
* macro timing
* economic releases

### Market Time

Used for:

* execution
* opportunity detection
* modeling

Implemented using:

```text
Volume Bars
```

---

## 3.2 Multi-Scale Market Context

Instead of:

```text
D1
H4
H1
```

the preferred architecture is:

```text
Macro Context
Intermediate Context
Execution Context
```

which may be implemented using:

```text
25000 Volume Bars
5000 Volume Bars
1000 Volume Bars
```

Research may modify exact scales.

---

# PART 4 — REGIME DOCTRINE

## 4.1 Regimes Are Latent

Regimes are not facts.

Regimes are hypotheses.

Possible regimes:

```text
Trend Expansion
Trend Mature
Trend Exhaustion
Range Compression
Range Expansion
Volatility Shock
```

---

## 4.2 No Regime Definition Is Sacred

Potential regime definitions:

* ADX
* Hurst
* Volatility
* EMA Slope
* Market Structure

Research must determine which works.

---

## 4.3 Regime Validation Rule

Every regime definition must prove:

```text
Predictive usefulness
```

Otherwise it is discarded.

---

# PART 5 — EVENT LIBRARY

## 5.1 Event Library Principle

Events generate opportunities.

Events do not generate trades.

---

## 5.2 Core Event Library

Derived from KJ_Entries_Exits.

### Event 1

Trend Pullback

### Event 2

Deep Pullback

### Event 3

Breakout

### Event 4

Volatility Breakout

### Event 5

Trend Continuation

### Event 6

Volatility Expansion

### Event 7

News Shock

### Event 8

Mean Reversion

### Event 9

Pattern Completion

---

## 5.3 Experimental Event Library

Examples:

* Liquidity Sweep Proxy
* Market Structure Shift
* Compression Release
* Volatility Collapse
* Exhaustion Spike

Experimental events must pass validation before promotion.

---

# PART 6 — OPPORTUNITY ENGINE

## 6.1 Objective

Determine:

```text
How good is this opportunity?
```

---

## 6.2 Inputs

```text
Pair
Regime
Event
Volatility
Volume
Structure
Session
Calendar Risk
```

---

## 6.3 Output

```text
Opportunity Score
0.00 → 1.00
```

---

## 6.4 Approval Threshold

Research determines threshold.

Example:

```text
Score > 0.80
```

---

# PART 7 — TRIPLE BARRIER FRAMEWORK

## 7.1 Outcome Labeling

Every event receives:

```text
TP
SL
TIME
```

labels.

---

## 7.2 Dynamic Volatility

Barrier width:

```text
Barrier Width
=
k × Volatility
```

Volatility calculated at entry.

---

## 7.3 Barrier Lock Rule

Critical rule:

Once trade opens:

```text
TP
SL
```

become fixed.

No barrier resizing.

This prevents look-ahead bias.

---

## 7.4 Volume-Bar Vertical Barrier

Time barrier uses:

```text
N future volume bars
```

not clock hours.

Example:

```text
5 volume bars
```

---

# PART 8 — OUTCOME ENGINE

## 8.1 Objective

Estimate:

```text
P(TP)
P(SL)
P(TIME)
```

---

## 8.2 Expected Value

Formula:

```text
EV
=
P(TP)×Reward
-
P(SL)×Risk
```

Trade approval depends on EV.

Not win rate.

---

## 8.3 Pre-Trade Outcome

Used before entry.

---

## 8.4 In-Trade Outcome

Recalculated after entry.

Used by lifecycle controller.

---

# PART 9 — TRADE LIFECYCLE CONTROLLER

## 9.1 Controller Principle

Health and management are merged.

No separate conflicting models.

---

## 9.2 Controller Actions

Allowed actions:

```text
HOLD
REDUCE
LOCK
EXIT
REVERSE
```

---

## 9.3 Lifecycle Inputs

```text
Updated Outcome Probabilities
Volatility
Time In Trade
News Risk
Weekend Risk
```

---

# PART 10 — MANAGEMENT FRAMEWORK

Available management styles:

* Fixed Target
* Trailing Stop
* Partial Exit
* Breakeven
* Time Exit
* News Exit
* Weekend Exit

---

## 10.1 Management Attribution

Every event must be tested against every exit.

Research target:

```text
Event
×
Exit
```

matrix.

---

# PART 11 — PAIR INTELLIGENCE

## 11.1 Pair Independence Doctrine

No edge is assumed transferable.

Example:

```text
EURGBP
≠
GBPJPY
≠
XAUUSD
```

---

## 11.2 Pair-Specific Learning

Every pair receives:

```text
Own Event Statistics
Own Regime Statistics
Own Opportunity Statistics
```

---

# PART 12 — PORTFOLIO CONTROLLER

## 12.1 Portfolio Before Execution

Before trade execution:

Portfolio Controller reviews exposure.

---

## 12.2 Hidden Correlation Rule

Example:

```text
BUY EURUSD
BUY GBPUSD
BUY AUDUSD
```

may equal:

```text
3× USD Short
```

Controller must detect this.

---

## 12.3 Portfolio Heat

Maximum aggregate risk must be controlled.

---

# PART 13 — RISK ALLOCATION ENGINE

## 13.1 Position Sizing

Based on:

```text
EV
Confidence
Drawdown
Portfolio Heat
```

---

## 13.2 Dynamic Risk

Risk may decrease during drawdowns.

Risk may increase only after validation.

---

# PART 14 — MACHINE LEARNING FRAMEWORK

## 14.1 Approved Models

Initial:

* Logistic Regression
* Random Forest
* LightGBM

---

## 14.2 Future Models

Allowed after proof:

* Transformers
* Temporal Fusion Transformers
* Deep Reinforcement Learning

---

## 14.3 Model Selection Rule

More complex models must outperform simpler models.

Otherwise:

```text
Choose simpler model.
```

---

# PART 15 — RESEARCH PROTOCOL

## Phase 0

Event Attribution

```text
Event
×
Pair
×
Regime
```

Output:

```text
event_outcome_matrix.md
```

---

## Phase 0.5

Event × Exit Attribution

Output:

```text
event_exit_matrix.md
```

---

## Phase 1

Opportunity Engine

---

## Phase 2

Outcome Engine

---

## Phase 3

Lifecycle Controller

---

## Phase 4

Portfolio Controller

---

## Phase 5

Deployment

---

# PART 16 — STATISTICAL VALIDATION

Required:

* Walk Forward
* Holdout
* Bootstrap
* Block Bootstrap
* Multiple Testing Control

---

## Approved Methods

* FDR
* Benjamini-Hochberg
* Deflated Sharpe Ratio
* White Reality Check

---

# PART 17 — HYPOTHESIS KILL FRAMEWORK

## 17.1 Principle

Every hypothesis has a death condition.

---

## 17.2 Kill Criteria

Hypothesis is retired if:

```text
EV < 0

Walk-forward failure

Holdout failure

Cost destroys edge

Regime instability

Portfolio instability
```

---

## 17.3 No Emotional Attachment

Research does not defend hypotheses.

Research attempts to destroy hypotheses.

Survivors earn deployment.

---

# PART 18 — TRANSACTION COST MODEL

## 18.1 Cost Is First-Class

Cost is part of reality.

Not post-processing.

---

## 18.2 Dynamic Friction

Transaction cost model includes:

```text
Spread
Commission
Slippage
Execution Delay
```

---

## 18.3 Volatility Shock Adjustment

During:

```text
News
Expansion
Volatility Shock
```

cost assumptions must increase.

---

# PART 19 — PRODUCTION ARCHITECTURE

```text
Volume Bars
        ↓
Event Library
        ↓
Context Engine
        ↓
Opportunity Engine
        ↓
Triple Barrier
        ↓
Outcome Engine
        ↓
Trade Lifecycle Controller
        ↓
Portfolio Controller
        ↓
Risk Allocation Engine
        ↓
Execution
```

---

# FINAL PRINCIPLE

```text
Predict less.
Measure more.

Assume less.
Validate more.

Optimize less.
Generalize more.

Protect capital first.
Seek edge second.
Scale only after proof.
```

**END OF ELITEFX_DOCTRINE_V5.md**
