# ELITEFX_DECISION_DOCTRINE_V10.md

**Chief Quant — D6 Implementation APPROVED; the Engine Refused to Be Complex; the Next Chapter Is Execution Science.**

Version: Decision Doctrine V10
Status: APPROVED — ACTIVE (Decision-domain SSOT)
Date: 3 July 2026
Authority: Single Source of Truth for the **Decision** domain
Companion: `ELITEFX DOCTRINE V6.9.md` (the **Market** domain SSOT)
Supersedes: Decision Doctrine V9 (adds Principle 103–106; D6 CLOSED; Execution Science chapter; Auditor 4-point compliance review; principle-numbering reconciliation note)

> Chief review 2026-07-03: **D6 Decision Engine Implementation — APPROVED** ("implementation safi
> zaidi ambayo mradi umewahi kutoa — si kwa sababu ni ngumu, bali kwa sababu imekataa kuwa ngumu").
> NB ya Chief: hii ni **approval ya implementation, si approval ya matokeo ya biashara.**

---

# D6 — WHAT WAS APPROVED

```text
decision_engine.py  (core ~72 lines / file 159)
  decide(snapshot, policy) → Decision Object      ← ENGINE NZIMA ni functions mbili
  decide_batch = map(decide)
  imports: decision_object + stdlib PEKEE (import-purity self-tested)
  stateless (module-mutables self-tested) · pure/deterministic (id-stable)
  kila Decision: policy_id (P88) + snapshot_id (P84) · lifecycle PROPOSED
```

Chief aliyoyapenda: orchestrator tu · hakuna Market imports · Policy ndiyo inaamua · refs kamili ·
stateless imejaribiwa · Known Limitations za uaminifu (Execution haipo; reliability OPEN; policies
hazijathibitishwa OOS — "hii ni sayansi nzuri; hakuna madai yasiyoungwa mkono").

---

# PRINCIPLE 103 — The Engine Remains Minimal and Bounded in Responsibility (APPROVED; reworded 2026-07-03)

```text
The Decision Engine shall remain minimal and bounded in responsibility;
new business behavior belongs in policies or domain objects, not in the engine.
```

Chief: ukiona Engine inaanza kuwa na helpers nyingi / business logic / caches — **ujue architecture
inaanza kupotoka.** Retry, persistence, execution, broker — zote ni **layers mpya**, sio nyongeza
ndani ya Engine.

> **NB (review ya architecture, 2026-07-03):** doctrine **haifungi idadi ya mistari ya code** — hiyo
> ni implementation detail. Vipimo vya ukubwa (mf. core ~72 lines ya leo) ni **benchmark za
> Architecture Audit**, sio doctrine. Implementation inaweza kuboreshwa bila kubadilisha doctrine —
> ilmradi **responsibility** ya Engine haiongezeki.

# PRINCIPLE 104 — Continuous Architectural Purity (APPROVED)

```text
Architectural purity shall be continuously verified by automated compliance tests.
```

Self-test [4] ya engine (`bad-imports=[]`, `forbidden-words=[]`) si test ya mara moja — ni
**requirement ya kudumu**. Kila mabadiliko ya Engine yanapita compliance tests kabla ya review.

# PRINCIPLE 105 — The Integrity Gate (OPEN)

```text
Every Decision Object shall pass through an explicit Integrity Gate before execution.
```

Logic gap iliyogunduliwa na Chief kutoka swali la report ("nani anafanya VALIDATED?"): **Engine
hafanyi; Policy hafanyi** → kuna layer mpya isiyofafanuliwa. Integrity Gate ≠ execution — ni ukaguzi
wa structural/compliance kabla ya kutuma decision nje. Architecture:

```text
Evidence Snapshot → Decision Policy → Decision Engine → Decision Object
                                                            ↓
                                                     Integrity Gate
                                                            ↓
                                                        Execution
```

# PRINCIPLE 106 — The Decision Repository (OPEN)

```text
Decision persistence shall be delegated to a repository layer independent of the engine.
```

Uamuzi wa Chief kwa swali la storage: decision history **si sehemu ya Engine** — ni **Decision
Repository**, layer huru.

---

# AUDITOR — 4-POINT COMPLIANCE REVIEW (amri ya Chief, kila PR)

```text
1. Engine size            (P103 — bounded complexity)
2. Forbidden imports      (P92/Rule 4 — decision_object + stdlib pekee)
3. Stateless compliance   (Rule 5 — no cache/globals/singleton/memory)
4. Policy leakage         (P97/Rule 3 — hakuna decision logic ndani ya Engine)
```

Hii ni nyongeza juu ya Compliance Matrix + Architectural Drift Watch za kila review.

---

# PRINCIPLE-NUMBERING RECONCILIATION (RESOLVED — review ya 2026-07-03)

Mikondo miwili ya 2026-07-02/03 ilizalisha numbering mbili:

```text
Mkondo A (repo: V8/V9):        P90 interface-freeze · P91 eligibility · P92 dependency-direction ·
                               P93 canonical objects · P94 Engine–Policy contract · P95 repro-vector ·
                               P96 policy-selection-external · P97 orchestrator-only
Mkondo B (spec-text ya Chief,  P92 no-logic-in-engine · P94 knows-only-S/P/D · P97 stateless ·
 bado haiko repo):             P98 correctness-first · P99 self-test-per-step · P100 pure/deterministic ·
                               P101 refs · P102 report-format
```

**UAMUZI (approved 2026-07-03):** principle numbers ni **unique kwenye mradi mzima** — P mbili zenye
maana tofauti haziruhusiwi kuishi pamoja.

```text
DOCTRINE (unique):    P90–P97  = V8/V9 kama zilivyo (doctrine-of-record)
                      P98–P106 = V10 kuendelea (P98–P102 hazijatumika na doctrine —
                                 zimehifadhiwa; P103–P106 = hapa)
SPECIFICATION:        maudhui ya Mkondo B = **D6 Implementation Rules 1–8** (spec, SIO principles):
                      R1 no-doctrine-during-coding · R2 compliance checklist · R3 small engine ·
                      R4 knows-only-Snapshot/Policy/Decision · R5 stateless · R6 correctness-first ·
                      R7 self-test-per-step · R8 report format
```

Rekodi za kihistoria (engine report ya 2026-07-03 yenye labels P92–P102 za spec-text) hazibadilishwi —
Architecture Audit inaeleza mapping. Kuanzia sasa references mpya zitumie Rules 1–8 kwa spec na
P-numbers za doctrine-of-record pekee.

---

# CHAPTER 3 — EXECUTION SCIENCE (OPENED)

Chief: "changamoto zetu si za Decision Engine tena — zimehamia kwenye Execution Layer."

```text
Evidence Layer      ✅ FROZEN (interface — P90)
D4  Decision Objects   ✅ APPROVED
D5  Decision Policy    ✅ CLOSED
D6  Decision Engine    ✅ APPROVED — CLOSED (2026-07-03; implementation, si matokeo ya biashara)
        ══ EXECUTION SCIENCE BEGINS ══
E1  Integrity Gate       (P105 OPEN — structural/compliance check kabla ya execution)
E2  Execution Object     (P89 OPEN — immutable; fills/slippage/rejects)
E3  Decision Repository  (P106 OPEN — persistence nje ya Engine)
E4  Broker Adapter       (baadaye — kuunganisha na mazingira halisi)
```

Kila phase inaanza kwa **Chief phase-start approval** (P91) — na kwa utamaduni wa D6:
**specification kabla ya code**.

---

# FORBIDDEN IN THE DECISION DOMAIN (until Chief approval)

```text
Yote ya V9 +
Kuongeza features ndani ya Engine (P103 — retry/persistence/execution/broker = layers mpya) ·
Kubadilisha Engine bila automated compliance tests kupita (P104) ·
Execution bila Integrity Gate (P105, itakapofafanuliwa) ·
Persistence ndani ya Engine (P106) · ML · live deployment
```

---

# OPEN DECISION QUESTIONS

```text
E1 (P105)  Integrity Gate — nani anafanya VALIDATED; structural/compliance checks zipi?    OPEN
E3 (P106)  Decision Repository — persistence contract nje ya Engine.                        OPEN
SPEC-TEXT  D6 Implementation Rules 1–8 (spec-text ya Chief) kuwekwa repo kama Rules, si P#. OPEN
NUMBERING  Principle-numbering reconciliation.                     ✅ RESOLVED (2026-07-03)
P89 · P81 · P70 · P74 · P78 · P93 · P95 · P96                                               OPEN
```

---

# FINAL PRINCIPLE (Decision Doctrine)

```text
The cleanest implementation is the one that refused to be complex.
An engine that stays small is proof the architecture is working.
Validation belongs to a gate, persistence to a repository — the engine only decides to ask.
The market has not been asked yet: approving an implementation approves nothing about profit.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DECISION_DOCTRINE_V10.md**
