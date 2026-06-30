# ELITEFX_DECISION_DOCTRINE_V1.md

**Chief Quant — The Decision Doctrine. Market Science Tells Us What Is; Decision Science Tells Us What To Do.**

Version: Decision Doctrine V1
Status: APPROVED — ACTIVE (new domain SSOT)
Date: 30 June 2026
Authority: Single Source of Truth for the **Decision** domain
Companion: `ELITEFX DOCTRINE V6.9.md` (the **Market** domain SSOT)

> ELITEFX is now two independent sciences (Principle 61):
> **A. Market Doctrine** — Representation · Event Taxonomy · Semantics · Geometry (mature).
> **B. Decision Doctrine** — Evidence · Decision · Risk · Opportunity · Abstention · Sizing ·
> Portfolio · Execution (this document; the new frontier).
>
> Phase 26 proved the split: a representation can have prediction value and explanation value and
> still carry **no Selection Decision Value** (0/9 variables OOS). Knowing the market ≠ knowing
> what to do. This document governs the second science.

---

# WHY THIS DOCUMENT EXISTS

```text
Market research and decision theory are separate scientific domains (Principle 61).
Our problem is no longer "how is the market built?" — it is
"how do we convert evidence into action?"
```

Market Science has matured enough for now (Principle 62: stop expanding representations once they
no longer change decisions). The remaining gap is **Decision Science**, and it is an architecture,
not another report.

---

# THE DECISION ARCHITECTURE

```text
Market
  ↓
Representation        (Market Doctrine: event-specific geometry, semantics)
  ↓
Evidence             ← representations act ONLY through evidence (Principle 59)
  ↓
Decision             (a FAMILY, not "trade": Principle 60)
  ↓
Execution            (cost/spread-aware; capital preservation first — P26)
  ↓
Feedback             (decision outcome updates evidence, not representation)
```

A representation never touches a decision directly; it must first become **evidence**
(Principle 59). The decision then chooses an action from the **decision family**.

---

# DEFINITIONS (the vocabulary of the second science)

**1. Decision** — a choice of action from a *family*, not a binary "trade/no-trade":
```text
{ select · abstain · reduce size · hedge · diversify · wait · exit · suspend }
```
Decision Value is **decision-specific** (Principle 60): failure under one (e.g. selection)
does not imply failure under another (e.g. abstention or sizing).

**2. Evidence** — a quantified, decision-relevant summary derived from representation: an
effect size with uncertainty (EV, SE, sample quality, persistence), pre-registered, OOS-aware.
Representation → Evidence is where Market Science hands off to Decision Science (Principle 59).

**3. Confidence** — the calibrated reliability of evidence (not its magnitude). Carries through
to sizing, never to direction. (Builds on the Confidence Engine: CCS = EV × Confidence ×
Persistence × Sample Quality.)

**4. Opportunity** — Quality × Availability × Survivability (Principle 25), evaluated as a
**population to rank**, never a single rule (Principle 23). Opportunity is a decision input,
not a decision.

**5. Abstention** — the decision to *not act*. The default action. Capital preservation precedes
opportunity discovery (Principle 26); "where NOT to trade" is answered first (F-022: bad
configurations persist more reliably than good ones).

**6. Sizing** — the magnitude of action conditioned on confidence and survivability, not on
predicted direction. A candidate decision-axis Phase 26 did **not** test (Principle 60).

**7. Portfolio decision** — allocation across ranked opportunities; ranking ≠ allocation. The
portfolio decision manages joint risk, correlation, and capacity — distinct from per-opportunity
selection.

**8. Decision Quality** — measured by the *decision*, not the prediction:
```text
- Selection DV   = OOS ΔEV of selecting positive-EV cells vs trade-all   (Phase 26: 0/9)
- Abstention DV  = OOS loss avoided by not acting in flagged regimes      (UNTESTED)
- Sizing DV      = OOS risk-adjusted improvement from confidence-sizing   (UNTESTED)
- Portfolio DV   = OOS improvement in joint EV / drawdown from allocation (UNTESTED)
```
A finding earns its place only if it improves a decision metric (Principle 19).

**9. Decision Lifecycle** — birth → growth → decay → death of a decision rule's value
(extends F-028 from edges to decisions). A decision rule is judged living/dead by rolling
walk-forward decision quality, not historical profitability (Principle 27).

**10. Decision Failure** — distinct failure modes to name and guard against:
```text
- Confusing prediction value with decision value (Principle 58)
- Letting a representation act without evidence (Principle 59)
- Generalizing one decision's failure to all decisions (Principle 60)
- Acting when abstention dominates (violating capital-preservation, P26)
- Treating a valid taxonomy / structure as alpha (Principle 40)
```

---

# DECISION-DOMAIN PRINCIPLES

New (this turn):
```text
P58  Prediction Value, Decision Value, and Explanation Value are independent dimensions
     and shall never be treated as interchangeable.
P59  Representations shall influence decisions only through evidence, never directly.
P60  Decision Value is decision-specific; failure under one decision does not imply
     failure under all decisions.
P61  Market research and decision theory are separate scientific domains and shall evolve
     independently.
P62  A research program shall stop expanding market representations once additional
     representations fail to change decisions.
```

Carried from the Market chain because they are inherently decision-principles:
```text
P19  No finding without decision-quality impact.
P21  Selection > Prediction.
P23  Rank Configurations, don't classify Trades.    P24  No ranking by Expected Payoff alone.
P25  Opportunity = Quality × Availability × Survivability.
P26  Capital preservation before opportunity discovery.
P40  A valid taxonomy is not alpha.
P57  Primitives are descriptive metadata until independent decision value is shown.
```

---

# WHAT IS FORBIDDEN IN THE DECISION DOMAIN (until Chief approval)

```text
Direct representation→action (skip evidence) · One-decision generalization · Treating
ranking as allocation · Acting without an abstention test · ML · live deployment
```

---

# OPEN DECISION QUESTIONS (the new research frontier)

```text
DQ-1  Does any variable carry decision value under a NON-selection decision (abstention/sizing)?
DQ-2  What is the minimal Evidence object that a representation must produce to be decision-usable?
DQ-3  How is Confidence calibrated so it drives sizing without leaking into direction?
DQ-4  How is Decision Quality measured per decision-type, OOS, with FDR control?
DQ-5  What is the Decision Lifecycle of an abstention rule vs a selection rule?
```

---

# FINAL PRINCIPLE (Decision Doctrine)

```text
The market tells us what is; the decision tells us what to do — they are different sciences.
A representation must become evidence before it may move a decision.
Decision is a family, not a trade; value proven for one action is not value for another.
Abstention is a decision, and usually the right one.
Measure everything by the decision it changes, out of sample.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DECISION_DOCTRINE_V1.md**
