# ELITEFX_DECISION_DOCTRINE_V7.md

**Chief Quant — Decisions Are History; Policy Separates the Object From the Engine; Execution Is a Third Object.**

Version: Decision Doctrine V7
Status: APPROVED — ACTIVE (Decision-domain SSOT)
Date: 30 June 2026
Authority: Single Source of Truth for the **Decision** domain
Companion: `ELITEFX DOCTRINE V6.9.md` (the **Market** domain SSOT)
Supersedes: Decision Doctrine V6 (adds Principle 85–89; Decision History; CANCELLED state; Integrity ≠ Outcome; Decision Policy; Execution Object; D5 Decision Policy Framework before the Decision Engine)

> D4 FULLY APPROVED. Amendments: Decision Objects form a permanent **decision history** (P85);
> cancellation ≠ rejection (P86); **Integrity ≠ Outcome** (P87); every decision references its
> **Policy** (P88); Execution is a separate immutable object (P89, OPEN). And the next step is the
> **Decision Policy** layer — which keeps the Engine generic.

---

# THE OFFICIAL ELITEFX ARCHITECTURE (amended)

```text
MARKET SCIENCE:   Market → Representation
EVIDENCE LAYER [FROZEN]: Evidence Object → Operations → Set → Snapshot
DECISION LAYER:
     Decision Object
       ↓
     Decision Policy      (chooses the action — the LOGIC)
       ↓
     Decision Engine      (generic orchestrator — applies a policy to a snapshot)
       ↓
     Execution Object     (records what actually happened — P89, OPEN)
```

---

# PRINCIPLE 85 — Decisions Form the Permanent Decision History (APPROVED)

```text
Decision Objects collectively form the permanent decision history of the system.
```

Once a decision is an immutable object with lifecycle, provenance and audit, decisions become
**records**, not transient outputs. Later we will learn from the **history of decisions**, not
from the market alone.

# PRINCIPLE 86 — Cancellation ≠ Rejection (APPROVED)

```text
Decision cancellation shall be distinguished from decision rejection.
```

A decision stopped **before execution** by news, broker outage or manual intervention is
**CANCELLED**, not REJECTED. Lifecycle: `PROPOSED → VALIDATED → EXECUTED → SETTLED`, with side
states `REJECTED` (integrity fail), `EXPIRED` (evidence expired), and **`CANCELLED`** (stopped
pre-execution). CANCELLED is reachable only from PROPOSED/VALIDATED.

# PRINCIPLE 87 — Integrity ≠ Outcome (APPROVED)

```text
Decision Integrity shall be evaluated independently from Decision Outcome.
```

The pre-execution, structural metrics of a Decision Object are its **Integrity** (validity of the
object). **Quality/Outcome** — whether the decision was *right* — is a separate, later, OOS matter
(D-later). Terminology: "Decision Quality" → **"Decision Integrity"**.

# PRINCIPLE 88 — Every Decision References Its Policy (APPROVED)

```text
Every Decision Object shall reference the Decision Policy under which it was created.
```

The same Snapshot can yield different decisions under different policies (Conservative /
Aggressive / Capital-Preservation). A Decision must record the **policy_id** (`name@vN`) that
produced it → fully reproducible even if the policy changes later.

# PRINCIPLE 89 — Execution Is a Separate Object (OPEN)

```text
Execution shall be represented as an immutable object independent of the Decision Object.
```

`Decision: BUY` ≠ `Trade Executed`: a decision may be delayed, rejected by the broker, partially
filled, or find no price. Execution is therefore its own immutable object. Status: **OPEN** (built
after the Engine).

---

# PART 2 — DECISION THEORY

## The Decision Policy (D5 — the layer between Object and Engine)

```text
Q1  A Policy is a NAMED, VERSIONED rule that maps a Snapshot (complete context, P80) → an action
    from the decision family (P60). It is the decision LOGIC — separate from the Decision Engine.
Q2  Policies are versioned (name@vN); every Decision references the exact policy_id (P88) → reproducible.
Q3  A policy chooses its action from the snapshot's readiness_state (P82), reliability, and conflict
    — never from a market prediction. Default is ABSTAIN (P26).
Q4  Policies are swappable WITHOUT changing the Engine (dependency injection): the same snapshot under
    different policies yields different actions; the Engine code is unchanged.
Q5  Engine↔Policy contract (the only coupling):  policy.decide(snapshot) → (action, reason);
    the Engine wraps that into a Decision Object referencing policy_id (P88) and snapshot_id (P84).
```

Policies are **rule-based and conservative** — they do **not** prove alpha. With real EV negative,
most actions are ABSTAIN/AVOID (P26). Decision-ready ≠ trade-ready (P69).

Deliverable: `reports/decision_policy_report.md`
Implementation: `src/research/decision_policy.py`

## The Decision Engine (D6 — next; generic)

A small, generic orchestrator: takes a Snapshot and a Policy, applies the policy, and emits a
Decision Object. It contains **no decision logic** of its own — logic lives in policies, so policies
can change without touching the Engine.

---

# CHAPTER 2 ROADMAP — DECISION SCIENCE

```text
Evidence Layer      ✅ FROZEN
D4  Decision Objects        ✅ APPROVED   (immutable object; lifecycle incl. CANCELLED; integrity; policy_id)
D5  Decision Policy         NEXT          (versioned rule Snapshot→action; swappable; Engine↔Policy contract)
D6  Decision Engine         BLOCKED       (generic orchestrator: apply policy to snapshot)
D7  Execution Object        BLOCKED       (P89 — immutable; records fills/slippage/rejects)
D8  Decision Quality/Outcome BLOCKED      (per-decision OOS + FDR; separate from Integrity, P87)
D9  Portfolio / Live        BLOCKED
```

---

# FORBIDDEN IN THE DECISION DOMAIN (until Chief approval)

```text
Decision logic inside the Engine (it belongs in policies) · Decisions without a policy_id (P88) ·
Conflating cancellation with rejection (P86) · Conflating Integrity with Outcome (P87) · Conflating
Decision with Execution (P89) · Claiming a policy is profitable (rule-based, unvalidated) · ML · live deployment
```

---

# OPEN DECISION QUESTIONS

```text
DQ (D5)  Decision Policy: definition, versioning, action choice, swappability, Engine contract.  ← ACTIVE
P89      Execution Object (immutable; independent of Decision).                                  OPEN
P81      Internal-evidence vs external-execution constraints.                                    OPEN
P70/P74/P78  Confidence model · temporal conflict · redundancy vs duplication.                   OPEN
```

---

# FINAL PRINCIPLE (Decision Doctrine)

```text
Decisions are records, not moments — together they are the system's memory.
A cancelled decision is not a rejected one; integrity is not outcome — keep the distinctions.
The policy chooses; the engine only applies — so the engine never has to change when the policy does.
And a decision to act is not an execution — the market still gets its say.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DECISION_DOCTRINE_V7.md**
