# ELITEFX_DOCTRINE_V5.16.md

**Chief Quant — Edge Has Magnitude and Availability; From Knowledge to Decision**

Version: 5.16
Status: Superseded by V5.17 (current SSOT) — carry-forward in force
Date: 27 June 2026
Authority: Single Source of Truth (superseded by V5.17, 27 June 2026)
Supersedes: V5.15 (F-024 APPROVED; F-025 Magnitude+Availability; Principle 25; F-026 state trajectory; Gap 3 closed; Portfolio Engine added; Phase 8 Opportunity Engine)
Previous Versions: Archived (V4 … V5.15)

> ⚠️ **IMESASISHWA:** SSOT rasmi sasa ni **[ELITEFX DOCTRINE V5.17](ELITEFX%20DOCTRINE%20V5.17.md)**
> (Phase 8 hypothesis rejected; F-022 → Core Principle; Principle 26 capital
> preservation first; Principle 25 enhanced → Quality × Availability × Survivability;
> F-027 survivability independent of quality OPEN; Opportunity Engine reframed
> remove-bad-first; Phase 9 Survivability Engine). V5.16 carry-forward.

> Live program status lives in `docs/PROGRAM_BOARD.md`. This file is the doctrine
> of record; V5.0–V5.15 remain in force except where amended below.

---

# EXECUTIVE AMENDMENT — FROM KNOWLEDGE TO DECISION

Phase 7 (Confidence Engine) succeeded. We have moved from:

```text
Configuration → Expected Value
```

to the institutional form:

```text
Configuration → Evidence → Expected Value
```

Top-25 by EV and Top-25 by CCS overlap only **10/25** — the proof that confidence
changes the decision. **Principle 24 passes.** F-024 is **APPROVED**.

Until now we built **knowledge**. From here we build **decision** — and that is the
beginning of the AI.

---

# FINDING F-024 — Confidence Is As Valuable As Expected Payoff (APPROVED)

```text
Confidence is as valuable as Expected Payoff.
```

Upgraded **OPEN → APPROVED**. Ranking by CCS materially differs from ranking by EV
alone (Spearman ρ ≈ +0.91; Top-25 overlap 10/25; high-EV/low-N configurations are
correctly demoted).

---

# FINDING F-025 — Edge Has Magnitude AND Availability (APPROVED)

A logic gap remained: CCS = EV × Confidence × Persistence × Sample Quality has no
**Market Capacity**. A configuration with CCS = 5.4 occurring twice a year is not
equal to one with CCS = 3.9 occurring 300 times. Portfolio return depends on
**frequency**, not magnitude alone.

```text
Edge has two dimensions:
  1. Magnitude   (strength · confidence)
  2. Availability (frequency)
Both determine portfolio value.
```

Status: **APPROVED**.

---

# PRINCIPLE 25 — Opportunity = Quality × Availability

```text
The Opportunity Score shall incorporate both Quality and Availability.
```

```text
Opportunity = Quality × Availability
```

This is institutional portfolio optimization: rank not by per-trade quality alone,
but by the total edge a configuration can actually deliver to the book.

---

# FINDING F-026 — State Trajectory May Carry Information (OPEN)

The State Engine is still a **value**, but a state has **velocity**. `LOW → NORMAL →
HIGH` is not the same as `HIGH → HIGH → HIGH`, even though both end at HIGH. The
Opportunity Engine does not yet use **state trajectory**.

```text
State Direction (trajectory / momentum) may contain additional
predictive information beyond State Value.
```

Status: **OPEN — hypothesis** (tested after Phase 8). State Momentum is the next
research question, not part of Phase 8.

---

# GAP 3 — CLOSED

The Market State Report now reports **absolute distributions** alongside the
relative terciles (e.g. EURGBP median ATR ≈ 54 vs EURJPY ≈ 106 on D1). Pair
individuality — previously hidden by 33/33/33 terciles — is now visible. **Gap 3
is officially closed.**

---

# UPDATED ARCHITECTURE (official)

Ranking and allocation are two different things, so the pipeline gains a Portfolio
Engine:

```text
Configuration
  ↓
Confidence Engine          (CCS = Quality)
  ↓
Opportunity Engine         ← Phase 8 (rank by Quality × Availability; priority queue)
  ↓
Portfolio Engine           (allocation — ranking ≠ allocation)
  ↓
Trade Lifecycle
```

---

# PHASE 8 — Opportunity Engine (NEXT)

The goal is **not** new edge. It is to prove that CCS can be turned into a
**decision system**. The report must answer:

```text
1. By how much does CCS-ranking improve portfolio EV vs "trade-all"?
2. What fraction of the best configurations (Top 5/10/20%) carries most of the edge?
3. Does adding Availability (frequency) improve the portfolio vs CCS alone?
4. Can the Opportunity Engine build a priority queue WITHOUT ML?
```

All validation is out-of-sample (rank on train, measure on test).

Deliverable: `reports/opportunity_engine_report.md`
Implementation: `src/research/opportunity_engine.py`

---

# MACHINE LEARNING — The Final Step (after Phase 8)

Once Phase 8 proves CCS → decision, the last step is ML that learns the
**Configuration Score** — not BUY/SELL. The target now exists and has meaning.

---

# UPDATED ROADMAP

```text
Phase 7      CLOSED   (Confidence Engine; CCS; F-024 APPROVED)
Phase 8      Opportunity Engine          NEXT     (CCS → decision; Quality × Availability; priority queue; no ML)
Phase 9      Portfolio Engine            BLOCKED  (allocation; ranking ≠ allocation)
Phase 10     Machine Learning            BLOCKED  (learns Configuration Score)
(parallel)   F-026 State Trajectory      OPEN     (state momentum — next research hypothesis)
```

---

# STILL FORBIDDEN (until Chief approval)

```text
Portfolio Engine · ML (LightGBM/RF/XGBoost)
```

Binding rules: **decision quality over algorithm agreement** (P18); **survival =
EV/decision-quality improvement** (P19); **feature competition** (P20); **selection
over prediction** (P21); **opportunity = Configuration, never an Event** (P22);
**rank Configurations, don't classify Trades** (P23); **no ranking by Expected
Payoff alone** (P24); **Opportunity = Quality × Availability** (P25).

---

# CARRY-FORWARD (UNCHANGED)

All of V5.15 in force: F-016–F-023, Principles 18–24, H-06 (rare = execution risk),
the Configuration architecture, Research Foundation closed, and "Profitable ≠
Tradable Edge".

---

# FINAL PRINCIPLE

```text
We now build decision, not just knowledge.

Edge has magnitude and availability — opportunity is Quality × Availability.
Ranking is not allocation; both are needed.
A state has velocity, not only value (next question).

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DOCTRINE_V5.16.md**
