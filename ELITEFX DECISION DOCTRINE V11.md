# ELITEFX_DECISION_DOCTRINE_V11.md

**Chief Quant — Two-Chief Governance; Validation ≠ Eligibility; Purity Extends to the Graph; the Reviewer Arrives.**

Version: Decision Doctrine V11
Status: APPROVED — ACTIVE (Decision-domain SSOT)
Date: 3 July 2026
Authority: Single Source of Truth for the **Decision** domain
Companion: `ELITEFX DOCTRINE V6.9.md` (the **Market** domain SSOT)
Supersedes: Decision Doctrine V10 (adds Principle 107; two-Chief governance; E1 pre-spec rulings;
open-principle scheduling; alpha philosophy; hygiene approvals E-2/E-3/E-4)

> Chief review 2026-07-03: majibu rasmi ya Chief #1 kwa maswali 20 ya onboarding ya **Chief Quant #2**
> (`docs/CHIEF2_ONBOARDING_REVIEW.md`). Uelewa wa Chief #2 umethibitishwa (">95% sahihi"); OBS-1
> yake imezaa **Principle 107**. "Tunajenga institution, si trading bot."

---

# GOVERNANCE — TWO CHIEFS, ONE FINAL AUTHORITY (APPROVED)

```text
Chief Quant #1 — Scientific Director
    Doctrine · Final Approval · Scientific Direction · Architecture
    FINAL DECISIONS ZOTE zinatoka hapa.

Chief Quant #2 — Scientific Reviewer
    Independent Scientific Review · Counter-analysis · Alternative hypotheses ·
    Blind review · Challenge assumptions · Strategic advice
    Anaweza kupinga. Anaweza kupendekeza. APPROVAL ni ya Chief #1 pekee.

Implementer            — doctrine → implementation + reports
Architecture Auditor   — compliance pekee (PASS/FAIL; hakuna approval language)
```

Sababu ni moja: **institution haiwezi kuwa na final authority mbili.**

Maagizo ya Chief #1 kwa Reviewer: *"Usijaribu kuwa Chief #1 wa pili. Kila phase jiulize: 'Chief #1
anaweza kuwa amekosea wapi?' Ukiona hakuna — sema hakuna. Ukiona kuna — pingana. Kwa evidence.
Hiyo ndiyo thamani yako."*

---

# PRINCIPLE 107 — Transitive Dependency Purity (APPROVED)

```text
Architectural purity shall include transitive dependency purity, not only direct imports.
```

Chanzo: **OBS-1 ya Chief #2** — `decision_engine.py` ni import-pure moja kwa moja (self-test [4]
PASS), lakini `decision_object.py` inaimport `market_state_engine` (→ polars) kwa demo-instantiation;
matokeo: Engine haiwezi ku-load bila Market Science stack. Engine ni pure — **dependency graph bado
si pure**. Tofauti rasmi: **Direct purity ≠ Transitive purity.**

> **Agizo la Chief:** Auditor aanze kupima **dependency graph** (nyongeza juu ya 4-point compliance
> review ya kila PR).

---

# E1 — PRE-SPEC DOCTRINE RULINGS (E1 HAIJAFUNGULIWA)

E1 itafunguliwa rasmi kwa **Chief Directive** (P91). Implementer ataandika specification kama D6.
Rulings zifuatazo zinatangulia spec:

```text
VALIDATION ≠ ELIGIBILITY  (msingi wa E1)

Engine inakagua STRUCTURE:     Snapshot ipo? Policy ipo? Fields ziko?
Gate   inakagua ELIGIBILITY:   Policy hii inaruhusiwa leo? Risk budget ipo?
                               Compliance imekidhi? Correlation imekubalika?
```

- **FTMO = Execution Constraint.** SI sehemu ya Decision Policy; SI sehemu ya Decision Engine.
  MWONGOZO unaingia kupitia **Execution Science**, si Decision Science (ndiyo sababu P81 ilifunguliwa
  mapema).
- **VALIDATED haitengenezwi na Engine.** Integrity Gate itazalisha **Decision Object MPYA**
  (immutable, Decision ID mpya). History itaonyesha PROPOSED → VALIDATED. **Sio mutation.**
- **Ordering: STRICT** — `E1 → E2 → E3 → E4`. Hakuna parallel; sababu ni dependency.
- **A-4 (immutability enforcement)** itafungwa wakati wa **E2** — P89 Execution Object italeta
  immutability enforcement.

---

# OPEN PRINCIPLES — SCHEDULING (uamuzi wa Chief)

```text
P70  Confidence model    HAITAFUNGWI SASA — "sitaruhusu ifungwe kwa kubahatisha";
                         Execution Science haiihitaji. RED LINE inabaki.
P96  Policy Selection    Decision Science phase ya BAADAYE (SIO Execution Science).
                         Kwa sasa Japhet anachagua policy kwa mkono — na hiyo ni sahihi.
P78  Redundancy          BAADA ya Execution Science (haituzuizi kujenga Execution).
```

---

# ALPHA PHILOSOPHY (uamuzi wa Chief)

```text
Tutatafuta alpha lini?  Pale Decision itakapohitaji.
Hatutarudi Market Science kwa sababu hatuna kazi. Tutairudia pale ambapo
Decision Layer itasema: "Nahitaji evidence mpya ambayo haipo." Siyo kabla.
Market Science imefreeze — kwa dhati.
```

- **F-005 full-metric re-run: ifanywe** (ni debt).
- **D5 report re-run @v2: si lazima** (policy version imebadilika; history ipo — P88).
- **Phase 5.12 Rare States: bado** — Execution Science haitaihitaji.

---

# MWONGOZO — OFFICIAL RELATIONSHIP (mikondo miwili)

```text
MWONGOZO          = Operational Manual     (mkondo wa mkono)
Decision Science  = Research Architecture  (mkondo wa sayansi)
Hazijakutana bado. Zitakutana E4 — Broker Adapter.
```

FTMO values (`ftmo_config.yaml`) ni **judgement, siyo evidence** — ndiyo maana hazijaingia doctrine.
Baadaye zinaweza kupimwa.

---

# HYGIENE APPROVALS (2026-07-03)

```text
E-2  Rules 1–8              → docs/D6_IMPLEMENTATION_RULES.md
                              (operational specification — SIYO doctrine, SIYO report)
E-3  asset.zip / report.zip → zitolewe repo (artifacts)
E-4  doctrine/archive/      → iundwe; root ibaki na current doctrines pekee
```

---

# FORBIDDEN IN THE DECISION DOMAIN (until Chief approval)

```text
Yote ya V10 +
Transitive dependency ya Market domain ndani ya Decision modules bila kutambuliwa (P107) ·
E-phase yoyote kuanza bila Chief Directive (P91) ·
Chief #2 kutoa approval (governance — approval ni ya Chief #1 pekee) · ML · live deployment
```

---

# OPEN DECISION QUESTIONS

```text
E1 (P105)  Integrity Gate — spec (baada ya Chief Directive; rulings za V11 zinaongoza)      OPEN
E3 (P106)  Decision Repository — persistence contract nje ya Engine.                        OPEN
P107       Dependency-graph measurement ya Auditor (utekelezaji wa agizo).                  OPEN
SPEC-TEXT  Rules 1–8 kuwekwa repo.                                    ✅ RESOLVED (V11 — E-2)
P89 · P81 · P70 · P74 · P78 · P93 · P95 · P96                                               OPEN
```

---

# FINAL PRINCIPLE (Decision Doctrine)

```text
An institution has one final authority and many honest challengers.
Validation asks whether a decision is well-formed; eligibility asks whether it is allowed today.
Purity that stops at direct imports is not purity — the dependency graph is the architecture.
We return to the market only when a decision asks for evidence that does not exist.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX_DECISION_DOCTRINE_V11.md**
