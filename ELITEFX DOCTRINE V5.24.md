# ELITEFX_DOCTRINE_V5.24.md

**Chief Quant — Representation Is Not Prediction; Variables Live in a Hierarchy, Not Alone**

Version: 5.24
Status: APPROVED — ACTIVE (current SSOT)
Date: 28 June 2026
Authority: Single Source of Truth (SSOT)
Supersedes: V5.23 (Principle 34, 35; F-034; Phase 15 verdict reframed; Phase 16 Representation Interaction Audit)
Previous Versions: Archived (V4 … V5.23)

> Live program status lives in `docs/PROGRAM_BOARD.md`. This file is the doctrine
> of record; V5.0–V5.23 remain in force except where amended below.

---

# EXECUTIVE AMENDMENT — THE PHASE 15 VERDICT IS REJECTED

The Phase 15 arithmetic is correct, but its **interpretation** is wrong, and is
rejected. Phase 15 measured `base + one variable` at a time and concluded the
doctrine variables (age, trajectory, transition, persistence, activity) add no
information — then leapt to "representation near its limit." That leap breaks the
doctrine, which never claimed these variables live alone:

```text
State → Age → Transition → Trajectory      (one hierarchical system)
```

`Age = 4` alone is meaningless. `HIGH, Age=4, Transition=LOW→HIGH, Trajectory=Rising`
is where the information lives. Like genes: one gene shows no effect; five together
build a protein. A standalone incremental test can fail while the **combination**
carries the signal.

Two more gaps in Phase 15:

```text
- Incremental R² measures LINEAR/ADDITIVE contribution — it can miss interactions entirely.
- It confused REPRESENTATION with PREDICTION (R² is not the only quality).
```

---

# REDUNDANCY IS CONFIRMATION, NOT A PROBLEM

Phase 15 found Age ↔ Persistence = 0.82 and Transition ↔ Persistence = 1.00. That is
**expected**: persistence is a derivative of age. High redundancy among hierarchical
variables confirms the ontology is correct — it does not mean the variables are
useless.

---

# PRINCIPLE 34 — Contribution Beyond Standalone Prediction (APPROVED)

```text
A variable may contribute through interaction, calibration, or stability
even when its standalone predictive contribution is negligible.
```

# PRINCIPLE 35 — Representation ≠ Predictive Gain (APPROVED)

```text
Representation quality shall not be judged solely by predictive gain.
```

Representation can improve calibration, stability, transferability, robustness, and
generalization without raising R². (We already saw State Age improve **calibration**
but not accuracy.)

# FINDING F-034 — Hierarchical Redundancy Is Expected (APPROVED)

```text
Redundancy among hierarchical variables is expected
and does not imply uselessness.
```

---

# PHASE 15 — CONCLUSION CORRECTED

The Phase 15 report's conclusion is amended from "representation near its limit" to:

```text
No evidence of incremental STANDALONE contribution
under the current representation and evaluation.
```

The doctrine variables (age, trajectory, transition, persistence) are **not removed**.

---

# PHASE 16 — Representation Interaction Audit (NEXT)

No more `base + one variable`. Evaluate **interactions, hierarchy, and institutional
metrics**:

```text
Q1. Does Age × Transition add information (not Age alone)?
Q2. Does Trajectory × Event add information?
Q3. Is Age × Trajectory × Transition better than each alone?
Q4. Does the doctrine hierarchy (State→Age→Transition→Trajectory) appear in the data?
Q5. Which interactions retain information after permutation?
```

New metrics, not incremental R² alone:

```text
Incremental Calibration (ECE/Brier) · Stability across folds ·
Transferability across pairs · Robustness across regimes.
```

Deliverable: `reports/representation_interaction_report.md`
Implementation: `src/research/representation_interaction_engine.py`

---

# MACHINE LEARNING — Still Deferred

```text
No ML.
```

We test whether the architecture works **together** before any ML. The true test of
ELITEFX's architecture is whether the hierarchical variables gain power in
combination — which the doctrine always claimed.

---

# UPDATED ROADMAP

```text
Phase 15     CLOSED   (Audit; standalone insufficient; verdict corrected; variables retained)
Phase 16     Representation Interaction Audit   NEXT   (interactions + calibration/stability/transfer/robust; no ML)
Phase 17     Expanded-Representation Confirmation BLOCKED (re-run OOS+FDR with interaction-aware representation)
Phase 18     Opportunity Engine v2       BLOCKED
Phase 19     Machine Learning            BLOCKED
```

---

# STILL FORBIDDEN (until Chief approval)

```text
Removing hierarchical variables · More data · New strategy · Opportunity Engine v2 · ML
```

Binding rules (Principles 18–35): … (carry-forward) … **validation failure ⇒
representation failure until proven** (P33); **contribution may be via interaction/
calibration/stability** (P34); **representation quality is not judged by predictive
gain alone** (P35). Core findings: a representation can fail while structure exists
(F-033); hierarchical redundancy is expected (F-034).

---

# CARRY-FORWARD (UNCHANGED)

All of V5.23 in force: F-016–F-033, Principles 18–33, H-06, Research Foundation
closed, Contextual Event Library, Confirmation Framework, and "Profitable ≠ Tradable
Edge".

---

# FINAL PRINCIPLE

```text
Variables live in a hierarchy, not alone — test them together, like genes.
Representation is not prediction; calibration and stability are quality too.
Redundancy among hierarchical variables confirms the ontology; it does not condemn it.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DOCTRINE_V5.24.md**
