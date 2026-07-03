# ELITEFX_DECISION_DOCTRINE_V8.md

**Chief Quant — A Frozen Layer Freezes Its Interface; Phases Progress by Eligibility; the Architecture Auditor Guards Against Drift.**

Version: Decision Doctrine V8
Status: APPROVED — ACTIVE (Decision-domain SSOT)
Date: 2 July 2026
Authority: Single Source of Truth for the **Decision** domain
Companion: `ELITEFX DOCTRINE V6.9.md` (the **Market** domain SSOT)
Supersedes: Decision Doctrine V7 (adds Principle 90–91; interface-freeze wording; "NOT YET ELIGIBLE" wording; Architecture Auditor role; D5 conflict-input amendment)

> Chief review ya **Architecture Audit #1** (`docs/CHIEF_GAP_REVIEW.md`) — **APPROVED**. G-1 inasimama:
> **D5 inabaki ACTIVE** hadi `reports/decision_policy_report.md` iwasilishwe na kureviewiwa — workflow
> (Research → Report → Chief Review → Approval) haivunjwi. Amendments mbili za principle (P90/P91),
> amendment moja ya D5 (conflict = explicit policy input), na role mpya ya governance.

---

# PRINCIPLE 90 — Frozen Means Interface-Frozen (APPROVED)

```text
A frozen layer guarantees interface stability, not implementation immutability.
```

Evidence Layer imefreeze **kwa interface**, sio kwa implementation. Kesho tunaweza kuboresha
performance, storage, au serialization — lakini **contract** (Object → Operations → Set → Snapshot;
fields; semantics) haitikisiki. "FROZEN" popote kwenye doctrine/board isomeke hivi.

# PRINCIPLE 91 — Eligibility Governs Progression (APPROVED)

```text
Progression between phases shall be governed by eligibility criteria rather than
implementation readiness.
```

Decision Engine (D6) **haijablockiwa** — iko **NOT YET ELIGIBLE**. "Block" ina maana kuna tatizo;
hapa hakuna tatizo — tunafuata governance: phase inafunguka pale eligibility criteria (report ya
phase iliyotangulia + Chief approval) zinapotimia, sio pale code inapokuwa tayari.

---

# GOVERNANCE — THREE ROLES (amended)

```text
Chief Quant           direction · doctrine · architecture
Implementer           doctrine → implementation + reports
Architecture Auditor  Doctrine ⇄ Architecture ⇄ Implementation ⇄ Tests ⇄ Reports (drift guard)
```

Kila review ya Auditor inaangalia mnyororo mzima (sio file→file) na inamalizika na:
(1) **Layer-Drift Matrix** (`| Layer | Status | Drift? |`) na
(2) **Future Risk Assessment** (`| Risk | Probability | Impact |` — architectural risks, sio bugs).
Rekodi: `docs/ARCHITECTURE_AUDIT.md`.

---

# D5 AMENDMENT — CONFLICT IS AN EXPLICIT POLICY INPUT (G-7)

V7 Q3 inasema: *"A policy chooses its action from the snapshot's readiness_state (P82), reliability,
and **conflict**."* Audit (G-7) iligundua conflict ilikuwa implicit tu (kupitia readiness INVALID) —
`CONFLICT_CEIL` ilikuwa dead import. Uamuzi wa Chief: **isifutwe — iwe explicit input.**

```text
Kila policy inasoma conflict (temporal + structural max) moja kwa moja, na ina TOLERANCE yake:
  capital_preservation  tolerance = 0.00          (conflict yoyote → ABSTAIN)
  conservative          tolerance = CONFLICT_CEIL (≥ ceiling → ABSTAIN)
  aggressive            tolerance = CONFLICT_CEIL (≥ ceiling → HEDGE)
```

Logic imebadilika → **policies zime-bump hadi `@v2`** (P88 versioning discipline: version mpya =
policy_id mpya = decision id mpya). D5 inabaki ACTIVE hadi report (G-1).

---

# CHAPTER 2 ROADMAP — DECISION SCIENCE (wording amended)

```text
Evidence Layer      ✅ FROZEN (kwa INTERFACE — P90)
D4  Decision Objects         ✅ APPROVED
D5  Decision Policy          ACTIVE            (report PENDING — G-1; data run ya Japhet)
D6  Decision Engine          NOT YET ELIGIBLE  (P91 — inafunguka D5 ikifungwa)
D7  Execution Object         NOT YET ELIGIBLE  (P89)
D8  Decision Quality/Outcome NOT YET ELIGIBLE  (per-decision OOS + FDR; P87)
D9  Portfolio / Live         NOT YET ELIGIBLE
```

---

# FORBIDDEN IN THE DECISION DOMAIN (until Chief approval)

```text
Yote ya V7 (Decision logic ndani ya Engine · decisions bila policy_id · cancellation=rejection ·
Integrity=Outcome · Decision=Execution · claiming policy profitability · ML · live deployment)
+ Kuvunja interface ya Evidence Layer (P90 — implementation inaweza kuboreshwa, contract hapana)
+ Kufungua phase bila eligibility (P91 — report + Chief approval kwanza)
+ Kuchanganya hygiene commits na research commits (Chief 2026-07-02)
```

---

# OPEN DECISION QUESTIONS

```text
Q-047 (D5)  Decision Policy — REPORT PENDING (G-1: reports/decision_policy_report.md).     ← ACTIVE
P89      Execution Object (immutable; independent of Decision).                            OPEN
P81      Internal-evidence vs external-execution constraints.                              OPEN
P70/P74/P78  Confidence model · temporal conflict · redundancy vs duplication.             OPEN
```

---

# FINAL PRINCIPLE (Decision Doctrine)

```text
A frozen layer is a promise about its interface, not a museum of its implementation.
Phases open by eligibility, not by eagerness — governance is the gate, not the obstacle.
The auditor does not oppose the chief nor defend the implementer:
the auditor keeps Doctrine, Implementation and Documents from drifting apart.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DECISION_DOCTRINE_V8.md**
