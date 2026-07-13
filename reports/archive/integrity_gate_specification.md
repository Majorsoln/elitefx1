# Integrity Gate Specification — VALIDATION ≠ ELIGIBILITY (E1, P105)

*2026-07-04 | Deliverable ya kwanza ya E1 (Chief: "spec kabla ya code — maswali 8 kama D6") |
Coding inaanza TU baada ya spec hii kupitishwa | NO code bado | NO ML | NO FTMO hardcode*

> **P105** Integrity Gate ni hatua rasmi kati ya Decision Engine na Execution. **V11/E1 ruling:**
> *Engine inakagua STRUCTURE; Gate inakagua ELIGIBILITY.* **P81** FTMO/MWONGOZO ni **execution
> constraint** — inaingia kupitia Execution Science, SIO Decision Science → Gate italeta **interface
> ya constraints**, HAI-hardcode FTMO. **P83/P85** VALIDATED = **Decision Object MPYA** (id mpya,
> append-only history), **SIO mutation**. **P97/Rule 3** logic ya eligibility ni ya constraints
> (injected), SIO ya Gate. Ordering STRICT: `E1 → E2 → E3 → E4`.

---

## Kanuni elekezi (kabla ya maswali 8)

Engine nzima ilikuwa sentensi moja (D6). Gate nzima pia ni sentensi moja:

```text
Receive PROPOSED Decision → Receive Constraints → Check Eligibility → Emit VALIDATED | REJECTED Decision (MPYA)
```

Tofauti ya msingi na Engine (ndiyo sababu Gate ipo tofauti — VALIDATION ≠ ELIGIBILITY):

```text
ENGINE (D6)  swali: "Je, uamuzi umeundwa vizuri?"  → STRUCTURE  → Decision Object (PROPOSED)
GATE   (E1)  swali: "Je, uamuzi unaruhusiwa LEO?"  → ELIGIBILITY → Decision Object (VALIDATED|REJECTED)
```

Gate haigusi ushahidi (snapshot ime-freeze), haigusi action (policy tayari imeamua), haigusi soko.
Inauliza swali moja jipya: **eligibility** — na inaijibu kwa **constraints zilizoinjectiwa**, sio kwa
logic yake yenyewe (P97). Kila kitu kingine kwenye spec hii ni kufafanua mipaka ya sentensi hiyo.

Nafasi ya Gate kwenye pipeline:

```text
Evidence Snapshot ──▶ ENGINE ──▶ Decision Object (PROPOSED) ──▶ GATE ──┬─▶ Decision Object (VALIDATED) ──▶ Execution (E2)
     (P79/P80)        (D6)              (P83)                  (E1)     └─▶ Decision Object (REJECTED)  ──▶ history (P85)
```

---

## Q1 — Gate responsibilities (NINI inafanya)

Gate ina majukumu **manne tu**, kwa mfuatano (mirror ya Engine, lakini kwa eligibility):

| # | Responsibility | Doctrine |
|---|----------------|----------|
| 1 | **Kupokea** Decision Object (lifecycle = PROPOSED) na **EligibilityConstraints** (injected) + **context** (injected) | P83; P81; Rule 4 |
| 2 | **Kuvalidate** decision kimuundo (structural — tazama Q8): NI Decision Object halali na iko PROPOSED | P83 |
| 3 | **Kuita** kila `constraint.check(decision, context)` na kupokea `(verdict, reason)` — Gate inaorchestrate, hai-decide | **P97** (contract pekee) |
| 4 | **Kuunda Decision Object MPYA** immutable: VALIDATED (constraints zote ELIGIBLE) au REJECTED (constraint yoyote INELIGIBLE), yenye `parent_decision_id` → PROPOSED (P85), na kuiongeza kwenye history | P83/P85; V11/E1 ruling |

Hakuna jukumu la tano. Gate **hairun policy tena**, **haihesabu risk budget yenyewe**, **haisomi FTMO
file** — hizo ni ndani ya constraints/context (Q7). Retry/scheduling ni za caller (baadaye E3/E4).

## Q2 — Gate boundaries (NINI HAIFANYI — kamwe)

| Boundary | Maana | Doctrine |
|----------|-------|----------|
| ❌ Hakuna structural re-validation | Snapshot/policy structure tayari zime-check na Engine (D6 Q8). Gate haiangalii snapshot tena | P97 (single responsibility) |
| ❌ Hakuna decision logic / re-decide | Gate haibadilishi `action`; policy tayari imeamua. Gate inauliza eligibility ya uamuzi uliopo tu | **P97 / Rule 3** |
| ❌ Hakuna evidence/market calculations | Gate haihesabu EV/reliability/conflict; snapshot ime-freeze — Gate haiitazami hata | P92 |
| ❌ Hakuna eligibility logic ndani ya Gate | Gate haina `if risk_used > budget`; risk/compliance/correlation ni **constraints injected** | **P97 / Rule 3** |
| ❌ Hakuna FTMO hardcode | FTMO ni **execution constraint** (P81) — inapita kama constraint provider injected (Execution Science), kamwe si literal ndani ya Gate module | **P81** |
| ❌ Hakuna import ya Market/Execution Science | Gate module inaimport `decision_object` + stdlib PEKEE (mirror Rule 4); constraints ni opaque | Rule 4 / P92 / P107 |
| ❌ Hakuna mutation | Gate haibadilishi PROPOSED object wala constraints wala context; inaunda object MPYA (P83) | P68/P83; **V11/E1 ruling** |
| ❌ Hakuna execution | VALIDATED ≠ trade; fills/slippage ni Execution Object (E2/P89) | P89 |
| ❌ Hakuna state | No cache, no globals, no budget-counter ndani ya Gate; risk budget "state" inaishi kwenye context (injected), sio Gate | Rule 5 |

## Q3 — Inputs

| Input | Aina | Sharti |
|-------|------|--------|
| `decision` | Decision Object (P83) | Lazima ipite structural validation (Q8) **NA** `lifecycle == "PROPOSED"`. Gate inagate decisions za PROPOSED pekee — VALIDATED/EXECUTED/terminal ni makosa (Q5). |
| `constraints` | orodha ya EligibilityConstraint (injected) | Kila moja lazima itimize contract: ina `id` (`constraint:name@vN`, mfano wa P88) na callable `check(decision, context) → (verdict, reason)`. Gate inaichukulia kama **opaque**. Orodha tupu = hakuna kizuizi (tazama Q4/Open Questions). |
| `context` | EligibilityContext (injected, opaque) | Hali ya nje inayohitajika na constraints: risk budget iliyotumika, compliance rules, correlation/exposure ya sasa, allow-list ya policy. Gate **haisomi**; inaipitisha kwa constraints tu (P97). |

**Constraint selection ni NJE ya Gate (mirror P96):** nani achague constraints zipi zitumike leo ni
layer ya nje (Execution Science / caller). Gate kamwe haina constraint iliyofichwa au default —
ikiwemo FTMO (P81).

## Q4 — Outputs

Output ni **Decision Object MPYA immutable (P83)** — moja kati ya mbili, kutegemea eligibility:

| Outcome | Object | Fields muhimu |
|---------|--------|---------------|
| Constraints ZOTE ELIGIBLE | **VALIDATED** Decision Object (id MPYA) | `lifecycle = VALIDATED`; `parent_decision_id = <PROPOSED id>` (P85); `action/reason/evidence_refs/policy_id` zime-carry-over bila kubadilika; `eligibility` = rekodi ya constraints zilizopita; `audit` += gate entries |
| Constraint yoyote INELIGIBLE | **REJECTED** Decision Object (id MPYA) | kama juu, ila `lifecycle = REJECTED`; `eligibility` inarekodi **constraint iliyokataa + sababu** |

**Muundo wa msingi (V11/E1 ruling):** PROPOSED object **inabaki kama ilivyo** (immutable, P83).
Gate **haifanyi mutation** — inatoa object MPYA yenye **id mpya** na `parent_decision_id` inayonyoosha
nyuma. History inaonyesha `PROPOSED → VALIDATED` (au `PROPOSED → REJECTED`) kama **objects mbili
tofauti** zilizounganishwa kwa parent link, sio field moja iliyobadilishwa. Hii ni append-only
decision history (P85).

**REJECTED ≠ error (mirror ya D6 Q5):** kukataliwa kwa eligibility ni **outcome halali** wa Gate
(kama vile ABSTAIN ni outcome halali wa policy) — inarekodiwa kwenye history. Kushindwa kwa **mfumo**
(input batili) ni GateError, SIO REJECTED (Q5). REJECTED ≠ CANCELLED (P86): REJECTED = eligibility
imekataa; CANCELLED = ilisimamishwa na nje (news/broker/manual) baada ya kuwa halali.

**parent_decision_id — pendekezo kwa Chief (Open Question kutoka MEMORY):** ongeza field mpya
`parent_decision_id` kwenye Decision Object (P85 traceability). Chain kamili inakuwa:
`Snapshot → PROPOSED decision → VALIDATED decision` — zote immutable, zote append-only, traceable
kikamilifu. Bila field hii, VALIDATED object ingekuwa "yatima" (haijulikani ilitoka PROPOSED ipi).
Tazama **Open Questions** kwa athari kwenye id-derivation na `transition()`.

## Q5 — Error handling

Kanuni kuu (mirror ya Engine): **Gate kamwe HAIBUNI eligibility.** Ikishindwa ku-orchestrate, inatoa
**GateError** (rekodi ya kushindwa kwa mfumo) — SIO REJECTED decision. Kwa nini: REJECTED ni **outcome
wa eligibility** (constraint imesema hapana); kushindwa kwa mfumo si eligibility.

| Kesi | Tabia ya Gate | Kwa nini |
|------|---------------|----------|
| Decision invalid kimuundo (Q8 inashindwa) | **GateError** (`invalid_decision`); hakuna object | Gate haiwezi kuthibitisha P83 |
| Decision `lifecycle != PROPOSED` | **GateError** (`invalid_lifecycle`) | Gate inagate PROPOSED pekee; VALIDATED-mara-mbili si halali |
| Constraint haitimizi contract (hakuna `check`/`id`) | **GateError** (`invalid_constraint`) | P97 contract |
| `constraint.check` inarusha exception | **GateError** (`constraint_failure`, exception imerekodiwa); hakuna object | Gate haiokoi logic ya constraint (P97) |
| `constraint.check` inarudisha verdict nje ya enum | **GateError** (`invalid_verdict`) | verdict enum (Q7) |
| Constraint inarudisha **INELIGIBLE** | **SIO error.** → REJECTED Decision Object (Q4) | Eligibility ni **outcome**, sio kushindwa kwa mfumo |
| `context` haina data constraint inayohitaji | **Nje ya Gate.** Constraint yenyewe ndiyo inaamua (INELIGIBLE au ku-raise → `constraint_failure`) | P97 — Gate haijui mahitaji ya constraint |

GateErrors zinahifadhiwa kwenye **error log ya Gate** (auditable) — lakini SIO kwenye decision history
(P85 ni ya decisions halali: PROPOSED/VALIDATED/REJECTED — sio system failures).

## Q6 — Audit responsibilities

Gate inaandika **eligibility audit** — nyongeza juu ya audit ya Decision Object (P66):

```text
gate.receive   {decision_id, lifecycle}
gate.check     {constraint_id, decision_id, verdict, why}        (moja kwa kila constraint)
gate.validate  {new_decision_id, parent_decision_id, decision_id}          (outcome = eligible)
gate.reject    {new_decision_id, parent_decision_id, failed_constraint, why} (outcome = ineligible)
```

- Traceability inaenea: **VALIDATED → (parent) PROPOSED → Snapshot → Set → Operations → Objects**
  (P85 + P84 chain).
- Gate HAIANDIKI kwenye audit ya PROPOSED object (immutability, P68) — object mpya inabeba audit yake
  (imerithi audit ya parent + gate entries).
- Reproducibility ya eligibility = `{parent_decision_id, constraint_ids, context_ref}`. **Roadmap
  (mirror P95 OPEN):** context yenyewe ipewe `context_version`/hash ili eligibility iwe reproducible
  kikamilifu (risk budget/compliance state inabadilika kwa muda). Haitekelezwi E1 bila Chief approval;
  imeandikwa hapa ili spec isije ikadaiwa haikuiona.

## Q7 — Constraint injection

- **Dependency injection tupu (mirror Engine Q7):** `gate.validate(decision, constraints, context)` —
  constraints + context zinapita kama arguments. Hakuna registry ya ndani, hakuna default constraint,
  hakuna config-file lookup ndani ya Gate (hiyo ingekuwa constraint selection — nje ya Gate).
- Gate inagusa **surface mbili tu** za kila constraint: `constraint["id"]` (kurekodi) na
  `constraint["check"](decision, context)` (kuita). Chochote kingine ni opaque.
- **verdict enum:** `check` inarudisha `(verdict, reason)` ambapo `verdict ∈ {ELIGIBLE, INELIGIBLE}`.
  Verdict nyingine yoyote → GateError (`invalid_verdict`, Q5). *(Pendekezo: enum ndogo kwa makusudi —
  eligibility ni binary; "conditional/degraded" si eligibility bali ni sizing, ambayo ni Execution
  Science, sio Gate.)*
- **Combination rule:** decision ni ELIGIBLE ikiwa **constraints ZOTE** zinarudi ELIGIBLE (AND / veto).
  Constraint moja INELIGIBLE = REJECTED. Gate haipimi "uzito" wa constraint — veto ni binary (RED LINE
  ya eligibility). *(Short-circuit ni ruhusa ya optimization ya baadaye — Rule 6: correctness kwanza,
  audit constraints zote kwa uwazi.)*
- **FTMO/MWONGOZO inaingia HAPA (P81):** ni constraint provider inayotoka **Execution Science**,
  injected kama constraint yoyote nyingine. Gate haijui ni FTMO — inaona `constraint.check` tu. Hii
  ndiyo interface ambayo V11 iliagiza: Gate ilete interface ya constraints, isihardcode FTMO.
- **Swappability:** kubadilisha/kuongeza constraint = kubadilisha argument. Gate code haiguswi —
  risk-budget, correlation, compliance, FTMO zote zinapita kwenye contract ile ile.

## Q8 — Decision validation (structural)

Validation ya Gate ni **structural PEKEE** juu ya **Decision Object** (SIO snapshot — Engine tayari
imeikagua). Gate inathibitisha kwamba kitu kilichofika NI Decision Object halali iliyo PROPOSED.
Semantic eligibility (je, inaruhusiwa leo?) ni **kazi ya constraints**, sio ya Gate.

Checklist (zote lazima zipite; la sivyo → GateError):

```text
D1  ni mapping yenye `id` ya decision (P83)                       → invalid_decision
D2  ina `action` ∈ Decision ACTIONS enum                          → invalid_decision (P60)
D3  ina `evidence_refs` (→ snapshot id) na `policy_id` (P84/P88)  → invalid_decision
D4  ina `lifecycle` NA `lifecycle == "PROPOSED"`                   → invalid_lifecycle
D5  ina `audit` (list) — chain ya provenance ipo                  → invalid_decision
```

Gate **HAIHESABU** eligibility kutoka values (haipimi kama reliability ni "nzuri", haisomi risk
budget — hizo ni constraints); inathibitisha uwepo/aina/lifecycle tu.

---

## Mchoro wa mwisho (Gate ndani ya architecture)

```text
                              ┌───────────────────────────────┐
  (Execution Science)        │        INTEGRITY GATE          │
Constraints ──constraints──▶ │  validate(decision) Q8         │
(FTMO=constraint, P81)       │  for c in constraints:  Q7     │
Context     ──context──────▶ │      c.check(decision, ctx)    │──▶ Decision VALIDATED (id mpya, parent link)
                             │  all ELIGIBLE? → VALIDATED     │──▶ Decision REJECTED  (id mpya, parent link)
Decision (PROPOSED) ──────▶  │  any INELIGIBLE? → REJECTED    │──▶ GateError (Q5, si decision)
   (from Engine, P83)        └───────────────────────────────┘
                                  hakuna eligibility logic (P97)
                                  hakuna FTMO hardcode (P81)
                                  hakuna mutation — object MPYA (P83/P85)
                                  hakuna Market/Execution imports (Rule 4/P107)
```

---

## VERDICT — E1 Specification

→ Spec inajibu maswali 8 na inafunga Gate kwenye responsibility moja (P97): **pokea PROPOSED
decision, validate kimuundo, ita constraints (injected), unda object MPYA (VALIDATED|REJECTED).**
VALIDATION ≠ ELIGIBILITY imetekelezwa kama mgawanyo wa kimuundo: Engine = STRUCTURE, Gate =
ELIGIBILITY. FTMO haipo ndani ya Gate — ni constraint injected (P81). VALIDATED ni object MPYA, sio
mutation (P83/P85). Gate ni module ndogo kama Engine — na ndivyo inavyopaswa: **architecture ndiyo
bidhaa; Gate ni mtumishi wa eligibility.**

**Hakuna code iliyoandikwa.** Implementation inaanza baada ya Chief kupitisha spec hii — na baada ya
Open Questions #1 (parent_decision_id / `transition()` reconciliation) kutolewa uamuzi, kwa sababu
inagusa `decision_object.py` (D4, approved).

## Known Limitations / Honest Caveats

1. **`transition()` vs VALIDATED-object-mpya inagongana.** `decision_object.py` ya sasa ina
   `transition(dec, "VALIDATED")` inayorudisha object yenye **id ILE ILE** (lifecycle-bump). V11/E1
   ruling inasema VALIDATED = **object MPYA, id MPYA**. Haviwezi vyote viwili kuwa canonical. Spec hii
   inapendekeza njia ya Gate (object mpya + parent link); `transition()` ya same-id inabaki open kwa
   Chief — tazama Open Questions #1. **Rule 1: sijabadilisha `decision_object.py`** — nimesimama na
   nauliza.
2. **id-collision hatari.** `_decision_id` ya sasa = hash(`snapshot_id|action|as_of|policy_id`).
   VALIDATED object yenye snapshot/action/policy/as_of ile ile ingepata **id ile ile ya PROPOSED** →
   si "id mpya". Kufunga hili kunahitaji discriminator (mf. lifecycle + parent) kwenye id-derivation —
   Open Questions #2.
3. **Constraints/context bado hazipo.** Gate ni interface; risk-budget/compliance/correlation/FTMO
   providers ni Execution Science (hazijaandikwa). Hadi zipatikane, caller angepitisha constraints kwa
   mkono (kama policy leo, P96 OPEN).
4. **Eligibility ni binary (ELIGIBLE/INELIGIBLE).** Hakuna "conditional/degraded" — sizing/haircut ni
   Execution Science, sio Gate. Kama Chief anataka verdict ya tatu, Q7 enum inabadilika.
5. **Spec hii haithibitishi chochote kiuchumi.** Gate ita-orchestrate constraints ambazo bado hazipo;
   decision-eligible ≠ trade-profitable (P69). Protect capital first.

## Open Questions (kwa Chief — sihamishi bila uamuzi)

1. **`transition()` reconciliation (BLOCKER ya implementation).** Je, njia ya Gate (VALIDATED = object
   MPYA, id mpya, `parent_decision_id`) ndiyo canonical crossing ya `PROPOSED → VALIDATED`, na
   `transition()` ya same-id i-retire (au ibaki kwa lifecycle za ndani tu: EXECUTED/SETTLED)?
   **Pendekezo langu:** ndiyo — Gate ndiyo mzalishaji rasmi wa VALIDATED; `transition()` isiende
   njia ya PROPOSED→VALIDATED tena. Inahitaji edit ndogo ya `decision_object.py` (D4-adjacent) →
   Chief approval kwanza (Rule 1).
2. **id-derivation ya object mpya.** Nini iingie kwenye hash ili VALIDATED/REJECTED zipate id
   tofauti na PROPOSED (na kila mmoja tofauti)? **Pendekezo:** `new_id =
   hash(parent_decision_id | new_lifecycle | gate_id | as_of)`. `gate_id` (mf. `gate:integrity@v1`)
   inaingia kama `policy_id` ilivyo (P88-style) → eligibility reproducible + traceable.
3. **`parent_decision_id` field kwenye Decision Object** — approve kuiongeza (P85)? Ni field mpya
   kwenye D4 object; ndiyo msingi wa "sio-yatima" traceability.
4. **Abstentions / non-committing actions.** Je, Gate ipitishe ABSTAIN/WAIT (hazitumii risk budget)
   moja kwa moja, au zipite kwenye constraints kama kila decision? **Pendekezo:** zipite uniformly
   (Gate agnostic); constraint inaweza ku-short-circuit intents zisizo-committing → ELIGIBLE trivially.
   Hii inaweka Gate pure na eligibility-logic kwenye constraints (P97).
5. **`gate_id` versioning.** Je, Gate yenyewe ipewe versioned id (`gate:integrity@v1`) inayorekodiwa
   kwenye VALIDATED object (kama `policy_id`)? **Pendekezo:** ndiyo — reproducibility ya eligibility
   inahitaji kujua toleo la Gate lililotumika.

---

*Integrity Gate = eligibility orchestrator only (P97); contract pekee = constraint.check(decision,
context); PROPOSED Decision Object pekee kama input (P83); VALIDATED = object MPYA, sio mutation
(P83/P85); FTMO = injected constraint, sio hardcode (P81); hakuna Market/Execution imports (Rule
4/P107). Engine = STRUCTURE, Gate = ELIGIBILITY. NO code bado. NO ML. Profitable ≠ Tradable Edge.
Protect capital first.*
