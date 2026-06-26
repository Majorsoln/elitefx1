# ELITEFX_DOCTRINE_V5.12.md

**Chief Quant Reassessment — Trading Science: Decision Quality Over Everything**

Version: 5.12
Status: Superseded by V5.13 (current SSOT) — carry-forward in force
Date: 26 June 2026
Authority: Single Source of Truth (superseded by V5.13, 26 June 2026)
Supersedes: V5.11 (replaces Principle 18; rewrites Principle 19; F-018→Decision Robustness; H-05 rejected, H-06 opened)
Previous Versions: Archived (V4 … V5.11)

> ⚠️ **IMESASISHWA:** SSOT rasmi sasa ni **[ELITEFX DOCTRINE V5.13](ELITEFX%20DOCTRINE%20V5.13.md)**
> (Phase 5 CLOSED; F-019 value law; F-020 Event × Configuration; Principle 20
> feature competition; Principle 21 selection > prediction; Phase 6 Interaction
> Engine). V5.12 carry-forward.

> Live program status lives in `docs/PROGRAM_BOARD.md`. This file is the doctrine
> of record; V5.0–V5.11 remain in force except where amended below.

---

# EXECUTIVE REASSESSMENT

The project has crossed from **Market Science** to **Trading Science**.

```text
OLD question:  "What states does the market have?"
NEW question:  "Which market information changes the QUALITY OF DECISIONS?"
```

Three reviews, three consequences:

```text
Market State Engine v1   APPROVED (foundation, not the end)
Rare State Analysis      APPROVED as descriptive — H-05 REJECTED, H-06 opened
Cluster Robustness       exploratory evidence only — NOT an acceptance criterion
```

From here, **anything that stays in the doctrine must prove it improves Expected
Value, Probability Calibration, or Decision Quality — otherwise it is removed.**

---

# MARKET STATE ENGINE v1 — APPROVED

States are built on relative normalization, deseasonalization, no-lookahead, and
pair-local thresholds — not human thresholds. This is the **foundation** of the
architecture (State → Transition → Age → Context → Configuration), not its end.

---

# RARE STATE — DESCRIPTIVE; H-05 REJECTED, H-06 OPENED

With the return distribution computed (5.10R), the data spoke:

```text
rare mean move ≈ 23.8 pips  vs  non-rare ≈ 26.2 pips   (ratio ≈ 0.91×)
```

The rare state does **not** carry bigger payoff. So:

```text
H-05  Rare State = Payoff State        REJECTED
```

But the rare state still has **spread +12σ** and very low activity. Spread, not
return, moved farthest — the edge can be eaten by execution. New hypothesis:

```text
H-06  Rare States are EXECUTION RISK States, not Payoff States.   (OPEN)
```

This is the interpretation the data supports.

---

# PRINCIPLE 18 — REPLACED (Decision Quality over Algorithm Agreement)

The old Principle 18 (Algorithm Independence) is **removed entirely.** Forcing
KMeans, GMM and Agglomerative — which solve different optimizations — to agree is
artificial. Low ARI (≈0.12) means cluster *identity* depends on the algorithm; it
does **not** mean the representation is bad.

```text
PRINCIPLE 18 (new):
  A market representation is valid if it consistently improves
  DECISION QUALITY, regardless of clustering algorithm.
```

We do not sell clusters. We sell decisions.

## FINDING F-018 — Decision Robustness (reframed)

```text
WAS:  Representation Robustness.
NOW:  Decision Robustness.
```

The evaluation changes from "KMeans vs GMM" to:

```text
Representation → Opportunity Quality → Expected Value
```

Cluster Robustness (5.11) and Representation Robustness (5.11B) remain only as
**exploratory** evidence — never acceptance criteria.

---

# PRINCIPLE 19 — THE SURVIVAL RULE (rewritten)

```text
No Feature, No State, No Representation shall remain inside ELITEFX
unless it improves Expected Value or Decision Quality.
```

This is the most important principle. Everything earns its place by improving EV,
calibration, or decision quality — or it is deleted.

---

# PHASE 5.13 — Representation Value (NEXT)

Before any Configuration/Opportunity Engine, one decisive test:

```text
Does adding the state representation improve:
  • Triple Barrier labels?
  • Opportunity ranking?
  • Expected Value?
  • Probability calibration?
  • Trade selection?

If nothing improves → remove the representation.
```

Method: assign Tier-1 events to latent clusters; measure EV-selection uplift and
win-probability calibration (LogLoss) vs baseline (online prequential). The
representation survives only if it improves a decision metric (Principle 19).

Deliverable: `representation_value_report.md`
Implementation: `src/research/representation_value.py`

---

# OPPORTUNITY ENGINE — Direction (future)

When it opens, the Opportunity Engine starts with **ranking**, not entry. It
predicts **Expected Payoff**, not BUY/SELL.

---

# UPDATED ROADMAP

```text
Phase 5.13   Representation Value         NEXT     (does the representation improve decisions?)
Phase 5.12   Liquidity Event Validation   QUEUED   (H-06: execution-risk, not payoff)
Phase 6      Configuration Engine         BLOCKED
Phase 7      Opportunity Engine           BLOCKED  (ranks Expected Payoff, not BUY/SELL)
Phase 8      Payoff Engine                BLOCKED
Phase 9      Machine Learning             BLOCKED
```

---

# STILL FORBIDDEN (until Chief approval)

```text
Configuration Engine · Opportunity Engine · Payoff Engine · ML
```

Binding rules: **economic meaning, not cluster identity** (Principle 18);
**no feature/state/representation survives without improving EV or decision
quality** (Principle 19); **no human taxonomy before the data shows structure**
(V5.9).

---

# CARRY-FORWARD (UNCHANGED)

All of V5.11 in force EXCEPT: old Principle 18 (Algorithm Independence) removed;
Principle 19 rewritten; F-018 reframed to Decision Robustness; H-05 rejected.
F-016 (latent structures exist) stands; F-017 stays Experimental; Market
Configuration architecture stands; "Profitable ≠ Tradable Edge" stands.

---

# FINAL PRINCIPLE

```text
Trading Science, not Market Science.
We do not sell clusters; we sell decisions.

Decision quality over algorithm agreement.
Nothing survives unless it improves Expected Value or Decision Quality.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DOCTRINE_V5.12.md**
