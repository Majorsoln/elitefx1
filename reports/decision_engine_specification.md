# Decision Engine Specification — orchestrator, sio chanzo cha architecture (Decision Science D6)

*2026-07-02 | Deliverable ya kwanza ya D6 (Chief: "Nataka implementer aandike Decision Engine
Specification. Sio code. Document.") | Coding inaanza TU baada ya spec hii kupitishwa | NO ML*

> **P94** Engine–Policy contract = njia PEKEE ya kutekeleza decision logic. **P97** Engine ni
> orchestrator — kamwe haina policy logic. **P92** Decision Science inategemea Evidence interface
> pekee. **P96 (OPEN)** policy selection ni external. **RED LINE**: reliability ≠ probability hadi
> P70 ifungwe. Engine ni **mtumishi wa architecture, si chanzo cha architecture** (Chief, V9).

---

## Kanuni elekezi (kabla ya maswali 8)

Engine nzima ni sentensi moja:

```text
Receive Snapshot → Receive Policy → Call Policy → Create Decision Object
```

Kila kitu kingine kwenye spec hii ni kufafanua mipaka ya sentensi hiyo — sio kuiongezea.

---

## Q1 — Engine responsibilities (NINI inafanya)

Engine ina majukumu **manne tu**, kwa mfuatano:

| # | Responsibility | Doctrine |
|---|----------------|----------|
| 1 | **Kupokea** Evidence Snapshot (canonical input) na Policy (injected) | P79/P80; P94 |
| 2 | **Kuvalidate** snapshot kimuundo (structural — tazama Q8) kabla ya kuipeleka kwa policy | P82/P84 |
| 3 | **Kuita** `policy.decide(snapshot)` na kupokea `(action, reason)` | P94 (contract pekee) |
| 4 | **Kuunda** Decision Object immutable inayoreference `snapshot_id` (P84) + `policy_id` (P88), na kuiongeza kwenye decision history | P83/P85 |

Hakuna jukumu la tano. Retry/scheduling/multi-snapshot loops ni za caller (baadaye Portfolio/D9),
sio za Engine.

## Q2 — Engine boundaries (NINI HAIFANYI — kamwe)

| Boundary | Maana | Doctrine |
|----------|-------|----------|
| ❌ Hakuna decision logic | Engine haina `if reliability > x` yoyote; thresholds/tolerances ni mali ya Policy | **P97** |
| ❌ Hakuna market calculations | Engine haihesabu EV/volatility/state chochote | P97 |
| ❌ Hakuna evidence calculations | Engine haiaggregate, haifilter, hai-resolve evidence — Snapshot inafika ikiwa tayari | P80 (complete context) |
| ❌ Hakuna import ya Market Science | Engine module haiimport `market_state_engine`/`event_library`/... — inaona Snapshot interface PEKEE | **P92** |
| ❌ Hakuna policy selection | Engine inapokea policy iliyokwishachaguliwa; nani anachagua ni layer ya nje (haijafafanuliwa — P96 OPEN) | **P96** |
| ❌ Hakuna reliability-kama-probability | Engine haitumii `snapshot["reliability"]` kwa hesabu yoyote (sizing/ranking/probability). Inaipitisha kwenye Decision Object kama rekodi tu | **RED LINE (P70)** |
| ❌ Hakuna execution | `Decision: ENTER` ≠ trade; fills/slippage/rejects ni Execution Object (D7) | P89 |
| ❌ Hakuna mutation | Engine haibadilishi snapshot wala policy wala decision iliyoshaundwa | P68/P71/P83 |

## Q3 — Inputs

| Input | Aina | Sharti |
|-------|------|--------|
| `snapshot` | Evidence Snapshot (P79) | Lazima ipite structural validation (Q8). Engine inakataa Object/Set ghafi — **Snapshot pekee** (P77/P79). |
| `policy` | Decision Policy (injected) | Lazima itimize contract: ina `id` (`policy:name@vN`, P88) na callable `decide(snapshot) → (action, reason)` (P94). Engine inaichukulia kama **opaque** — haijui na haisomi logic yake. |
| `as_of` (optional) | wakati wa maamuzi | Default = `snapshot["as_of"]`. Engine HAIRESOLVE upya freshness — hiyo ni kazi ya Snapshot layer (P73). |

**Policy selection ni NJE ya Engine (P96 OPEN):** hadi layer ya Policy Selection ifafanuliwe,
caller (Japhet/research script) ndiye anayepitisha policy waziwazi. Engine kamwe haina default
policy iliyofichwa.

## Q4 — Outputs

Output ni **moja**: **Decision Object** immutable (P83), kama ilivyofafanuliwa D4, ikiwa na:

- `action` — kutoka kwa policy (angalia INTENT hapa chini)
- `reason` — `"[policy_id] ..."` kutoka kwa policy
- `policy_id` (P88) + `evidence_refs = [snapshot_id]` (P84) → fully auditable
- `lifecycle = PROPOSED` (transitions ni operations za baadaye, sio za Engine)
- `integrity` metrics za structural (P87) — zinatoka snapshot, sio kutoka Engine logic
- `audit` — entry za orchestration (Q6)

Decision Objects zote zinaongezwa kwenye **decision history** (P85) — append-only. Engine
hairudishi "signal" wala "trade" — inarudisha **rekodi ya uamuzi**.

**Terminology — ACTION → INTENT (direction ya Chief, V9):** enum ya D6 inaitwa **INTENT** kwa sababu
Engine itafanya maamuzi yasiyo ya biashara pia:

```text
INTENT = ENTER · WAIT · EXIT · ABSTAIN · HEDGE · REDUCE
```

Mapping ya nyuma: `SELECT (D4/D5) → ENTER`. Policies za @v2 zinaendelea kutumia vocabulary ya zamani
hadi zipate version mpya (P88: renaming = logic surface change → `@v3` itakapofika).

## Q5 — Error handling

Kanuni kuu: **Engine kamwe HAIBUNI decision.** Ikishindwa ku-orchestrate, inatoa **EngineError**
(rekodi ya kushindwa) — SIO Decision Object yenye ABSTAIN. Kwa nini: ABSTAIN ni **uamuzi wa policy**
(P97); kushindwa kwa mfumo si uamuzi.

| Kesi | Tabia ya Engine | Kwa nini |
|------|-----------------|----------|
| Snapshot invalid kimuundo (Q8 inashindwa) | **EngineError** (`invalid_snapshot`, na sababu); hakuna decision | Engine haiwezi kuthibitisha P80/P84 |
| Policy haitimizi contract (hakuna `decide`/`id`) | **EngineError** (`invalid_policy`) | P94 |
| `policy.decide` inarusha exception | **EngineError** (`policy_failure`, exception imerekodiwa); hakuna decision | Engine haiokoi logic ya policy (P97) |
| `policy.decide` inarudisha action nje ya enum | **EngineError** (`invalid_action`) | Decision Object enum (P60) |
| Snapshot `readiness_state = INVALID/EXPIRED/STALE` | **SIO error.** Snapshot halali kimuundo inapelekwa kwa policy; policy ndiyo inaamua (ABSTAIN/HEDGE/WAIT) | State ni **input ya maamuzi**, sio kushindwa kwa mfumo |
| External constraints (broker/news/halt) | Nje ya scope ya Engine (P81 OPEN); zitakapokuja ni sababu za **CANCELLED** (P86) kwenye lifecycle, sio za Engine | P81/P86 |

EngineErrors zinahifadhiwa kwenye **error log ya Engine** (auditable) — lakini SIO kwenye decision
history (P85 ni ya decisions halali pekee).

## Q6 — Audit responsibilities

Engine inaandika **orchestration audit** — nyongeza juu ya audits za objects (P66):

```text
engine.receive   {snapshot_id, as_of}
engine.validate  {snapshot_id, result: pass|fail, why}
engine.invoke    {policy_id, snapshot_id}
engine.decide    {decision_id, action, policy_id, snapshot_id}
```

- Kila decision inabaki traceable: **Decision → Snapshot → Set → Operations → Objects** (P84 chain).
- Engine HAIANDIKI kwenye audit ya snapshot/policy (immutability, P68) — ina log yake.
- Reproducibility ya sasa = `policy_id + snapshot_id` (P88/P84). **Roadmap (P95 OPEN):** Decision
  Object iongezewe `schema_version` (ya Evidence Snapshot) + `doctrine_version` → reproducibility
  vector kamili `{policy, schema, doctrine}`. Haitekelezwi D6 bila Chief approval — imeandikwa hapa
  ili spec isije ikadaiwa haikuiona.

## Q7 — Policy injection

- **Dependency injection tupu:** `engine.decide(snapshot, policy)` — policy inapita kama argument.
  Hakuna registry ya ndani, hakuna default, hakuna config-file lookup ndani ya Engine (hiyo ingekuwa
  policy selection — P96).
- Engine inagusa **surface mbili tu** za policy: `policy["id"]` (kurekodi, P88) na
  `policy["decide"](snapshot)` (kuita, P94). Chochote kingine ndani ya policy ni opaque.
- **Swappability (D5 Q4 imethibitishwa):** kubadilisha policy = kubadilisha argument. Engine code
  haiguswi — kesho Rule/Bayesian/ML Policy (ikiidhinishwa na Chief) zinapita kwenye contract ile ile.
- Policy version mpya = `policy_id` mpya = decision ids mpya (P88) — Engine haina jukumu la kujua
  version ipi ni "ya sasa"; hiyo ni ya Policy Selection layer (P96 OPEN).

## Q8 — Snapshot validation

Validation ya Engine ni **structural PEKEE** — kuthibitisha kwamba kitu kilichofika NI Evidence
Snapshot halali (P79). Semantic evaluation (je, ushahidi unatosha? una conflict?) ni **kazi ya
policy**, sio ya Engine.

Checklist (zote lazima zipite):

```text
S1  ina `id` ya snapshot (P84)                                → la sivyo: invalid_snapshot
S2  ina `as_of` (int)                                         → la sivyo: invalid_snapshot
S3  ina `readiness_state` ∈ {READY, STALE, EXPIRED, INVALID}  → la sivyo: invalid_snapshot (P82)
S4  ina fields za contract: reliability, uncertainty,
    temporal_conflict, structural_conflict, aggregate          → la sivyo: invalid_snapshot (P80)
S5  SIO Evidence Object wala Set ghafi (hakuna `members`/
    `layers` za top-level bila snapshot fields)                → la sivyo: invalid_snapshot (P77/P79)
```

Engine **HAIHESABU** chochote kutoka values (haipimi kama reliability ni "nzuri" — RED LINE + P97);
inathibitisha uwepo na aina tu.

---

## Mchoro wa mwisho (Engine ndani ya architecture)

```text
                         ┌──────────────────────────┐
   (P96 OPEN)            │      DECISION ENGINE      │
Policy Selection ──policy──▶  validate(snapshot)  Q8 │
                         │   policy.decide(snap)  Q7 │──▶ Decision Object (P83/84/85/88)
Evidence Snapshot ─snap──▶   wrap + audit     Q4/Q6 │──▶ EngineError (Q5, si decision)
   (P79/P80)             └──────────────────────────┘
                              hakuna logic (P97)
                              hakuna Market imports (P92)
                              hakuna reliability-as-probability (RED LINE)
```

---

## VERDICT — D6 Specification

→ Spec inajibu maswali 8 ya Chief na inafunga Engine kwenye responsibility moja (P97): **pokea,
validate kimuundo, ita policy, unda rekodi.** Mipaka ni mikali kuliko uwezo — kwa makusudi. Engine
ikipitishwa itakuwa module ndogo kuliko zote kwenye Decision Science, na ndivyo inavyopaswa kuwa:
**architecture ndiyo bidhaa; Engine ni mtumishi wake.**

**Hakuna code iliyoandikwa.** Implementation inaanza baada ya Chief kupitisha spec hii (Q-048).

## Honest Caveats

1. **Policy Selection (P96) haijafafanuliwa** — spec hii inaiweka NJE ya Engine kwa makusudi, lakini
   layer yenyewe bado haipo; hadi ifafanuliwe, caller ndiye anayechagua policy kwa mkono.
2. **INTENT enum inahitaji uamuzi wa migration** — SELECT→ENTER mapping imependekezwa hapa; kama
   Chief ataidhinisha, Decision Object ACTIONS enum inabadilika (D4 ilikuwa approved na enum ya
   zamani — mabadiliko yatahitaji amendment ndogo ya D4 objects au alias ya nyuma).
3. **EngineError si Decision** — uamuzi huu wa design (kutobuni ABSTAIN kwenye failure) ni pendekezo
   la spec; kama Chief anapendelea "fail → ABSTAIN decision", Q5 inabadilika (na itahitaji policy_id
   ya nani? — hii ndiyo sababu spec inapendekeza EngineError).
4. **P95 (reproducibility vector) imeandikwa kama roadmap tu** — schema_version/doctrine_version
   hazipo kwenye objects za leo; kuziongeza ni amendment ya baadaye.
5. **Spec hii haithibitishi chochote kiuchumi** — Engine ita-orchestrate policies ambazo ni
   illustrative (D5 caveat 1); decision-ready ≠ trade-ready (P69).

*Decision Engine = orchestrator only (P97); contract pekee = policy.decide(snapshot) (P94); Snapshot
pekee kama input (P79); hakuna Market imports (P92); reliability si probability (RED LINE/P70).
NO code bado. NO ML. Profitable ≠ Tradable Edge.*
