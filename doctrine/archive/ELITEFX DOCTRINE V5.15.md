# ELITEFX_DOCTRINE_V5.15.md

**Chief Quant — Research Foundation Closed; Configuration is the Atomic Unit; Rank, Don't Classify**

Version: 5.15
Status: Superseded by V5.16 (current SSOT) — carry-forward in force
Date: 26 June 2026
Authority: Single Source of Truth (superseded by V5.16, 27 June 2026)
Supersedes: V5.14 (H-07→F-022 APPROVED; F-023, F-024; Principle 23, 24; Configuration = final atomic unit; Confidence Engine inserted; Research Foundation CLOSED)
Previous Versions: Archived (V4 … V5.14)

> ⚠️ **IMESASISHWA:** SSOT rasmi sasa ni **[ELITEFX DOCTRINE V5.16](ELITEFX%20DOCTRINE%20V5.16.md)**
> (F-024 APPROVED; F-025 Edge = Magnitude × Availability; Principle 25 Opportunity =
> Quality × Availability; F-026 state trajectory OPEN; Gap 3 closed; Portfolio Engine
> added; Phase 8 Opportunity Engine). V5.15 carry-forward.

> Live program status lives in `docs/PROGRAM_BOARD.md`. This file is the doctrine
> of record; V5.0–V5.14 remain in force except where amended below.

---

# EXECUTIVE AMENDMENT — RESEARCH FOUNDATION CLOSED

Phase 6.5 (Configuration Engine, `configuration_engine_report.md`) was the last
brick of the Research Foundation. The chain is proven end to end:

```text
1. States exist.
2. State transitions carry information.
3. State age adds calibration.
4. Events alone are not enough.
5. Event × State raises Expected Value.
6. Configuration is the atomic trading unit.
7. Bad configurations are more persistent than good ones.
```

The next step is **not** to find new edge. It is to **measure how much we can
trust the edge we already see**. That is the Confidence Engine.

---

# FINDING F-022 — Bad Configurations Are More Persistent (APPROVED)

H-07 is upgraded **EXPERIMENTAL → APPROVED**.

```text
Bad configurations are more persistent than good configurations.
```

Evidence (Phase 6.5): train-positive → positive ≈ 42% vs train-negative →
negative ≈ 66%. Retail systems learn *where to enter*; institutional systems first
learn *where NOT to enter*. Knowing where not to trade is the more durable edge.

---

# FINDING F-023 — Ranking Is the Native Language of the Opportunity Engine (APPROVED)

The top configurations do not resemble one another (e.g. `EURJPY · Mean Reversion ·
C1 · HIGH · SHORT · WIDE` vs `GBPUSD · Trend Continuation · C1 · LOW · LONG ·
WIDE`). No single rule fits them. The engine must learn a **population**, not a
rule.

```text
Ranking is the native language of the Opportunity Engine — not classification.
```

---

# FINDING F-024 — Confidence Is As Valuable As Expected Payoff (OPEN)

Expected Payoff alone is not enough: two configurations may both show EV = +15 but
one has N = 120 and the other N = 12,000 — they are **not** equal.

```text
Confidence is as valuable as Expected Payoff.
```

Status: **OPEN — under test** (Phase 7 Confidence Engine).

---

# CONFIGURATION — THE FINAL ATOMIC UNIT

The progression `Indicator → Signal → Event → Configuration` ends here. **No new
component is added below the Configuration.** The Configuration is the atomic
object of ELITEFX, and the entity the Opportunity Engine will rank:

```text
Configuration = Pair × Event × Latent State × Regime × Direction × Execution Context
```

---

# PRINCIPLE 23 — Rank Configurations, Don't Classify Trades

```text
The Opportunity Engine shall rank Configurations, not classify Trades.
```

The target is not "BUY" or "SELL". The target is "Configuration A has higher
expected payoff than Configuration B."

---

# PRINCIPLE 24 — No Ranking by Expected Payoff Alone

```text
No Configuration shall be ranked using Expected Payoff alone.
```

Every ranking must incorporate: **confidence interval · persistence · walk-forward
stability · sample quality.** An institutional desk does not take the highest-EV
trade if its confidence is low.

---

# PHASE 7 — Confidence Engine (NEXT)

For each Configuration, measure at least:

```text
Expected Value (EV) · 95% Confidence Interval · Sample size (N) ·
Walk-forward persistence · Stability score · Probability calibration (if applicable)
```

Then build a **Configuration Confidence Score (CCS)** combining them scientifically
(concept, not final formula):

```text
CCS  ≈  EV × Confidence × Persistence × Sample Quality
```

The Opportunity Engine consumes the CCS, not EV alone.

Deliverable: `reports/confidence_engine_report.md`
Implementation: `src/research/confidence_engine.py`

---

# UPDATED PIPELINE (official)

```text
OLD:  Configuration → Opportunity Engine

NEW:  Configuration
      ↓
      Confidence Engine          ← Phase 7 (CCS: EV + Confidence + Persistence + Sample Quality)
      ↓
      Opportunity Engine         (ranks Configurations by CCS)
      ↓
      Trade Lifecycle
```

The Opportunity Engine cannot rank reliably without knowing the **quality of the
evidence** behind each Configuration.

---

# MACHINE LEARNING — The Target Is Now Visible

For the first time the ML target is clear. ML will not output BUY/SELL. It will
output a **Configuration Score**. That target only exists once the Confidence
Engine defines it — so ML remains deferred until Phase 7 is done.

---

# UPDATED ROADMAP

```text
Phase 6.5    CLOSED   (Configuration Engine; F-021/F-022; atomic unit confirmed)
Phase 7      Confidence Engine           NEXT     (CCS: EV + Confidence + Persistence + Sample Quality)
Phase 8      Opportunity Engine          BLOCKED  (ranks Configurations by CCS; F-023/P23)
Phase 9      Machine Learning            BLOCKED  (predicts Configuration Score)
```

---

# STILL FORBIDDEN (until Chief approval)

```text
Opportunity Engine · ML (LightGBM/RF/XGBoost)
```

Binding rules: **decision quality over algorithm agreement** (P18); **survival =
EV/decision-quality improvement** (P19); **feature competition** (P20); **selection
over prediction** (P21); **opportunity = Configuration, never an Event** (P22);
**rank Configurations, don't classify Trades** (P23); **no ranking by Expected
Payoff alone** (P24).

---

# CARRY-FORWARD (UNCHANGED)

All of V5.14 in force: F-016 (latent structures), F-017 Experimental, F-018
(Decision Robustness), F-019 (Value Law), F-020 (Event × Configuration), F-021 (no
universal edge), Principles 18–22, H-06 (rare = execution risk), the Market
Configuration architecture, and "Profitable ≠ Tradable Edge".

---

# FINAL PRINCIPLE

```text
The Research Foundation is closed.
Configuration is the atomic unit; it is ranked, not classified.

Confidence is as valuable as Expected Payoff —
no edge is ranked by payoff alone.
Bad configurations persist more than good ones: learn where NOT to trade first.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DOCTRINE_V5.15.md**
