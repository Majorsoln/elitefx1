# ELITEFX_DECISION_DOCTRINE_V9.md

**Chief Quant — D5 FULLY APPROVED; End of the Decision Architecture Era; the Engine–Policy Contract Is the API of Decision Science; D6 Opens Specification-First.**

Version: Decision Doctrine V9
Status: APPROVED — ACTIVE (Decision-domain SSOT)
Date: 2 July 2026
Authority: Single Source of Truth for the **Decision** domain
Companion: `ELITEFX DOCTRINE V6.9.md` (the **Market** domain SSOT)
Supersedes: Decision Doctrine V8 (adds Principle 92–97; D5 CLOSED; red line ya reliability; risk taxonomy; Canonical Domain Objects; INTENT direction; D6 specification-first)

> Chief review mbili za 2026-07-02: (1) kazi ya V8/G-7/G-8/Audit#2 **APPROVED**; (2) `reports/
> decision_policy_report.md` imewasilishwa (run ya Japhet) na kureviewiwa → **D5 FULLY APPROVED —
> CLOSED**. Mwisho wa **Decision Architecture Era** (D0–D5): Evidence, Decision, Policy na mahusiano
> yao vimefungwa. Kilichobaki ni orchestration — **D6 inafunguliwa, specification kwanza**.

---

# THE SENTENCE (Chief, 2026-07-02)

```text
Market Science huzalisha ushahidi (Evidence);
Decision Science hubadilisha ushahidi huo kuwa maamuzi kupitia sera (Policies);
Engine husimamia mtiririko huo bila kubeba logic ya maamuzi.
```

Huu ndio msingi wa ELITEFX kwa sentensi moja.

---

# PRINCIPLE 92 — Dependency Direction Is Official (APPROVED)

```text
Decision Science shall depend only on the Evidence interface and never directly
on Market Science implementations.
```

```text
Market Science
        │
        ▼
 Evidence Snapshot
        │
══════════════════════   ← API pekee (P63/P79)
        │
        ▼
Decision Science
```

Hakuna import ya chini kwenda juu. (Ilianzia kama watch item **W-1** ya Architecture Audit #2 —
demo-instantiation ya leo inakubalika kwa research; **Decision Engine haitaruhusiwa kabisa**.)

# PRINCIPLE 93 — Canonical Domain Objects (OPEN)

```text
All core domain objects shall follow a common architectural contract:
immutable identity, provenance, lifecycle and auditability.
```

Ugunduzi wa Chief: Evidence Object, Decision Object, Execution Object (P89), Portfolio Object (baadaye)
— zote ni aina moja ya kitu: immutable · auditable · versionable · referential. **Architectural
inheritance, sio code inheritance.** Status: OPEN (itafafanuliwa rasmi baadaye).

# PRINCIPLE 94 — The Engine–Policy Contract Is the Only Gateway (APPROVED)

```text
The Engine–Policy contract shall be the only mechanism through which decision logic is executed.
```

```text
Engine ──▶ Policy.decide(snapshot) ──▶ (action, reason) ──▶ Decision Object
```

Hii ndiyo **API rasmi ya Decision Science** — contract, sio implementation. Kesho Rule Policy /
Bayesian Policy / ML Policy (ikiidhinishwa) zinaweza kubadilishana; Engine haitajua.

# PRINCIPLE 95 — Full Reproducibility Vector (OPEN)

```text
Decision reproducibility shall include policy version, evidence schema version,
and doctrine version.
```

Policy version peke yake haitoshi (Policy v2 inaweza kutegemea Evidence Schema v3). Roadmap:
Decision Object ibebe `{policy_id, schema_version, doctrine_version}`. Status: OPEN (D-baadaye).

# PRINCIPLE 96 — Policy Selection Is External (OPEN)

```text
Policy selection shall be external to individual decision policies.
```

Kesho: Conservative / Aggressive / Capital-Preservation / News Mode / FTMO Mode — **nani anachagua
policy?** Sio policy yenyewe (haipaswi kujichagua), na sio Engine (P97). Layer ya Policy Selection
haijafafanuliwa — swali la wazi la architecture. Status: OPEN.

# PRINCIPLE 97 — The Engine Is an Orchestrator Only (APPROVED)

```text
The Decision Engine shall orchestrate decisions but shall never contain decision policy logic.
```

Responsibility MOJA tu:

```text
Receive Snapshot → Receive Policy → Call Policy → Create Decision Object
```

Basi. Hakuna logic nyingine · hakuna heuristics · hakuna market calculations · hakuna evidence
calculations.

---

# RED LINE — Reliability ≠ Probability (Chief, 2026-07-02)

```text
Decision Engine SHALL NOT use reliability directly as a probability — until P70
(confidence model) is closed.
```

reliability ya leo = Φ(EV/SE) inayojaa kwa n kubwa (saturation). Kuitumia kama probability ni
kujenga artifact ndani ya Engine. **Red line — haivukwi.**

---

# TERMINOLOGY DIRECTION (D6, sio amendment ya sasa) — ACTION → INTENT

SELECT ni action ya biashara; Decision Engine itafanya actions zisizo za trading pia. Future doctrine
itumie **INTENT**: `ENTER · WAIT · EXIT · ABSTAIN · HEDGE · REDUCE`. Inafafanuliwa rasmi kwenye D6
specification.

---

# RISK TAXONOMY (amended — Chief, 2026-07-02)

Future Risk Assessment ya kila audit igawanywe **tatu**:

```text
Architecture Risks   (muundo/contract/coupling — mf. R-2 reliability saturation)
Research Risks       (mchakato wa utafiti — mf. R-1 data ya PC moja = Research Infrastructure Risk)
Governance Risks     (workflow/approvals/ledger)
```

Na kila audit iwe na sehemu ya **Architectural Maturity** (`| Layer | Maturity |`).

---

# CHAPTER 2 ROADMAP — DECISION SCIENCE

```text
Evidence Layer      ✅ FROZEN (kwa INTERFACE — P90)
D4  Decision Objects         ✅ APPROVED
D5  Decision Policy          ✅ FULLY APPROVED — CLOSED (report delivered + reviewed 2026-07-02)
        ══ END OF THE DECISION ARCHITECTURE ERA (D0–D5) ══
D6  Decision Engine          ACTIVE — SPECIFICATION FIRST
      deliverable ya kwanza: reports/decision_engine_specification.md (document, SIO code)
      maswali 8: responsibilities · boundaries · inputs · outputs · error handling ·
                 audit responsibilities · policy injection · snapshot validation
      implementation inaanza TU baada ya spec kupitishwa na Chief.
D7  Execution Object         NOT YET ELIGIBLE (P91; P89)
D8  Decision Quality/Outcome NOT YET ELIGIBLE (P91)
D9  Portfolio / Live         NOT YET ELIGIBLE (P91)
```

---

# FORBIDDEN IN THE DECISION DOMAIN (until Chief approval)

```text
Yote ya V8 +
Decision logic ndani ya Engine (P97) · import yoyote ya Market Science ndani ya Decision Engine
(P92) · reliability kama probability kabla P70 haijafungwa (RED LINE) · policy kujichagua yenyewe
(P96) · D6 coding kabla ya specification kupitishwa · ML · live deployment
```

---

# OPEN DECISION QUESTIONS

```text
Q-048 (D6)  Decision Engine Specification (maswali 8; document-first).          ← ACTIVE
P93      Canonical Domain Objects (common architectural contract).               OPEN
P95      Reproducibility vector (policy + schema + doctrine versions).           OPEN
P96      Policy Selection layer (nani anachagua policy?).                        OPEN
P89      Execution Object · P81 internal-vs-external · P70/P74/P78.              OPEN
```

---

# FINAL PRINCIPLE (Decision Doctrine)

```text
The architecture era ends when nothing is ambiguous — what remains is orchestration.
The engine is a servant of the architecture, never its source.
A contract outlives every implementation that honors it.
We do not start the Engine because we can — we start it because the system became eligible.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DECISION_DOCTRINE_V9.md**
