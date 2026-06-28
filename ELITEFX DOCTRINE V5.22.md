# ELITEFX_DOCTRINE_V5.22.md

**Chief Quant — Exploration Is Not Confirmation; Survive Out-of-Sample or It Is Not Alpha**

Version: 5.22
Status: Superseded by V5.23 (current SSOT) — carry-forward in force
Date: 28 June 2026
Authority: Single Source of Truth (superseded by V5.23, 28 June 2026)
Supersedes: V5.21 (Phase 13 = exploratory; Principle 31, 32; F-032; Candidate Alpha → Contextual Alpha Hypothesis; Phase 14 Confirmation Framework)
Previous Versions: Archived (V4 … V5.21)

> ⚠️ **IMESASISHWA:** SSOT rasmi sasa ni **[ELITEFX DOCTRINE V5.23](ELITEFX%20DOCTRINE%20V5.23.md)**
> (F-032 Confirmed; Principle 33 validation-failure = representation-failure; F-033 a
> representation can fail while structure exists; Phase 14 reframed as Current
> Representation Failure; Phase 15 Representation Audit). V5.22 carry-forward.

> Live program status lives in `docs/PROGRAM_BOARD.md`. This file is the doctrine
> of record; V5.0–V5.21 remain in force except where amended below.

---

# EXECUTIVE AMENDMENT — EXPLORATION ≠ CONFIRMATION

Phase 13 (Contextual Alpha) is accepted as an **Exploratory Research Report**, not
confirmatory evidence. Its conceptual contribution stands and is confirmed:

```text
Principle 30  Confirmed   (events are contextual)
F-030         Confirmed   (edge existence is conditional)
F-031         Confirmed   (only contextual events exist)
```

Adding context raises EV step by step (event → +pair → +vol → +spread → +session),
which supports Principle 30 / F-030. **But the "30 Candidate Alpha Objects" are
rejected as alpha** — the report fell into the logic gaps we have been avoiding:

```text
1. Selection bias    — "top by Bayesian" chosen after seeing the data.
2. Multiple comparisons — hundreds/thousands of cells; Top 30 ⇒ high false-discovery.
3. UNKNOWN states    — identity must be observable & reproducible (UNKNOWN ≠ identity).
4. Identity test weak — leave-one-out ≠ proof; Pair may be a PROXY (spread/liquidity/session).
5. No mechanism      — "remove pair ⇒ EV drops" answers WHAT, not WHY.
```

So those objects are **Research Candidates**, and their status is now **Contextual
Alpha Hypothesis** — not Candidate Alpha.

---

# PRINCIPLE 31 — Hypothesis Until Prospective Validation (APPROVED)

```text
Every Contextual Alpha Object is a hypothesis
until it survives prospective validation.
```

---

# PRINCIPLE 32 — Identity Requires Independent Explanatory Power (APPROVED)

```text
Identity variables must demonstrate independent explanatory power,
not merely predictive association.
```

Pair may only be called part of an alpha's identity if it retains power **after
controlling for** spread, session, and volatility — otherwise it is a proxy.

---

# FINDING F-032 — Refinement Raises Apparent Edge and False-Discovery Risk (APPROVED)

```text
Context refinement increases apparent edge,
but also increases false discovery risk.
```

Phase 13 demonstrated this directly: the more context we add, the higher the apparent
EV — and the higher the chance the result is selection, not signal.

---

# TERMINOLOGY (binding)

```text
Candidate Alpha   →  Contextual Alpha Hypothesis   (until pre-registered OOS survival)
```

No object may be called "alpha" until it survives prospective, out-of-sample,
multiple-comparison-controlled validation.

---

# PHASE 14 — Contextual Alpha Confirmation Framework (NEXT)

The next report must NOT be "Top 30 Candidates". It must answer one question: **does
even a single hypothesis survive outside the data that discovered it?**

```text
1. Pre-register all Contextual Alpha Hypotheses BEFORE testing (defined on in-sample only).
2. Test on a FUTURE out-of-sample period that was not used to discover them.
3. Control multiple comparisons with False Discovery Rate (Benjamini–Hochberg).
4. Remove or explain every UNKNOWN state — no hypothesis with incomplete identity is accepted.
5. Independent-contribution ablation (not just leave-one-out): does Pair retain power
   after controlling for Spread, Session, and Volatility?
```

Deliverable: `reports/contextual_alpha_confirmation_report.md`
Implementation: `src/research/alpha_confirmation_engine.py`

---

# MACHINE LEARNING — Still Deferred

```text
No ML.
```

The valuable next step is not finding more alpha; it is proving whether even one
hypothesis lives out-of-sample. ML before that learns selection artifacts.

---

# UPDATED ROADMAP

```text
Phase 13     CLOSED   (Exploratory; P30/F-030/F-031 confirmed; objects → hypotheses)
Phase 14     Confirmation Framework      NEXT     (pre-register + future OOS + BH-FDR + independent contribution; no ML)
Phase 15     Opportunity Engine v2       BLOCKED  (only OOS-survived hypotheses)
Phase 16     Portfolio Engine            BLOCKED
Phase 17     Machine Learning            BLOCKED
```

---

# STILL FORBIDDEN (until Chief approval AND OOS survival)

```text
Mean Reversion Strategy · Opportunity Engine v2 · Portfolio Engine · ML
```

Binding rules (Principles 18–32): … (carry-forward) … **events are contextual**
(P30); **hypothesis until prospective validation** (P31); **identity requires
independent explanatory power, not association** (P32). Core findings: edge is
conditional (F-030); only contextual events exist (F-031); refinement raises apparent
edge and false-discovery risk (F-032).

---

# CARRY-FORWARD (UNCHANGED)

All of V5.21 in force: F-016–F-031, Principles 18–30, H-06, Research Foundation
closed, Contextual Event Library, Edge/Event Reality Validation, and "Profitable ≠
Tradable Edge".

---

# FINAL PRINCIPLE

```text
Exploration is not confirmation.
Refinement makes edges look bigger and falser at the same time.
An object is alpha only after it survives out-of-sample, with multiple comparisons controlled
and its identity shown to be independent — not a proxy.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DOCTRINE_V5.22.md**
