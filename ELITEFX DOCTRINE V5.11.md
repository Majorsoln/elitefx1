# ELITEFX_DOCTRINE_V5.11.md

**Chief Quant Amendment — Economic Meaning Over Cluster Identity; Payoff Gate**

Version: 5.11
Status: APPROVED — ACTIVE (current SSOT)
Date: 26 June 2026
Authority: Single Source of Truth (SSOT)
Supersedes: V5.10 (amends Principle 18; adds F-018, Principle 19; F-017→Experimental)
Previous Versions: Archived (V4 … V5.10)

> Live program status lives in `docs/PROGRAM_BOARD.md`. This file is the doctrine
> of record; V5.0–V5.10 remain in force except where amended below.

---

# EXECUTIVE AMENDMENT

Two phase outcomes, two doctrine changes:

```text
Phase 5.10  Rare State Analysis     APPROVED (but F-017 stays Experimental)
Phase 5.11  Cluster Robustness      NOT APPROVED
```

The biggest change is a new governing rule:

```text
No finding enters the Doctrine until it shows impact on
PAYOFF or DECISION QUALITY.                       (Principle 19)
```

We are not building a taxonomy of market states. We are building a trading
system with an edge.

---

# PHASE 5.10 — APPROVED; F-017 → EXPERIMENTAL

`rare_state_analysis.md` did what was wanted: it studied a **market
configuration**, not a signal. The rare cluster (~0.3% of bars) shows extreme
spread, very low activity, and 1–3 bar duration.

But the decisive part — **does the rare state change the payoff?** — was not
computed (OHLC was absent). Doctrine does not say "the rare state exists"; it
asks "what is its payoff impact." Therefore:

```text
F-017  Rare States May Carry High Information     STATUS: EXPERIMENTAL
```

**Phase 5.10R** (after OHLC): rerun with forward return distribution, MAE, MFE,
Triple Barrier outcome, payoff distribution, holding time. Only then can F-017
be Approved.

---

# PHASE 5.11 — NOT APPROVED; PRINCIPLE 18 AMENDED

`cluster_robustness_report.md`: mean ARI ≈ 0.12; Agglomerative collapsed to one
98% cluster. Latent structures were algorithm-dependent → Principle 18 (as
written) failed.

But "algorithm independent" was **too strict**. KMeans (spherical), GMM
(elliptical), Agglomerative (linkage tree) make different assumptions; they need
not produce identical clusters. The right test is not cluster identity:

```text
AMENDED Principle 18:
  Do not require clusters to MATCH.
  Require ECONOMIC MEANING to match.
```

Two algorithms may find 4 vs 6 clusters and both be valid — if both detect the
same market configurations carrying the same payoff.

## FINDING F-018 — Representation Robustness > Cluster Identity

```text
Representation Robustness is more important than Cluster Identity.
```

So Phase 5.11 is not re-run with more algorithms. Instead, **Phase 5.11B**
tests whether latent structures survive different **representations** (z-score,
robust, percentile, rolling normalization), and whether the configurations carry
the same meaning. (F-018 is methodological; market findings still face
Principle 19.)

---

# NEW PRINCIPLE — Principle 19 (Payoff Gate)

```text
No Finding enters the Doctrine
unless it demonstrates impact on
Payoff or Decision Quality.
```

The goal is edge, not taxonomy. A structure that does not change a payoff
distribution or a decision is descriptive, not doctrine.

---

# NEW HYPOTHESIS — H-05 (Liquidity, not Volatility)

The rare state moved **spread +12σ**, activity −1σ, volatility only slightly
positive. Spread — not volatility — moved farthest. So:

```text
H-05  Rare States are LIQUIDITY Events, not VOLATILITY Events.
```

Status: **OPEN — under test** (Phase 5.12 Liquidity Event Validation). This is
now the correct hypothesis to test.

---

# UPDATED ROADMAP

```text
Phase 5.10R  Rare State Payoff           NEXT   (returns/MAE/MFE/barrier/holding → F-017?)
Phase 5.11B  Representation Robustness    NEXT   (F-018: structure across encodings)
Phase 5.12   Liquidity Event Validation   BLOCKED (H-05)
Phase 6      Configuration Engine         BLOCKED
Phase 7      Opportunity Engine           BLOCKED
Phase 8      Payoff Engine                BLOCKED
Phase 9      Machine Learning             BLOCKED
```

Deliverables:
`rare_state_analysis.md` (5.10R, OHLC) · `src/research/rare_state_analysis.py`
`representation_robustness_report.md` (5.11B) · `src/research/representation_robustness.py`

---

# STILL FORBIDDEN (until Chief approval)

```text
Configuration Engine · Opportunity Engine · Payoff Engine · ML
```

Binding rules: **no human market taxonomy before the data shows structure**
(V5.9); **economic meaning, not cluster identity** (Principle 18 amended);
**no finding without payoff/decision-quality impact** (Principle 19).

---

# CARRY-FORWARD (UNCHANGED)

All of V5.10 in force: F-016 (latent structures APPROVED), Principle 18 (now
amended), the Market Configuration architecture, Latent State Candidate stages,
and "Profitable ≠ Tradable Edge". F-017 downgraded to Experimental.

---

# FINAL PRINCIPLE

```text
Economic meaning, not cluster identity.
No finding without payoff impact.

The goal is edge, not taxonomy.
A rare configuration matters only if it changes the payoff.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DOCTRINE_V5.11.md**
