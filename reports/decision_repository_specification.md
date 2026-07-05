# Decision Repository Specification — PERSISTENCE ≠ ENGINE (E3, P106)

*2026-07-05 | Deliverable ya kwanza ya E3 (Chief: "E3 Decision Repository spec — persistence nje ya
Engine; training-data-ready schema; maswali 8"; E1+E2 CLOSED) | Coding baada ya spec kupitishwa | NO
code bado | NO ML | mkutano wa Track A ↔ Track B (E3↔K6)*

> **P106** Decision Repository = **persistence contract NJE ya Engine**. Engine/Gate/Recorder zinabaki
> stateless/pure (P97/P103/Rule 5) — **state (history) inahamishiwa Repository**. **P85** history ni
> **append-only** (kamwe usifute/mutate). **P83/A-4** records ni immutable (frozen). **Master §2**:
> E3 = mahali tracks zinakutana — *decision history + execution outcomes = raw material ya K6*. Kila
> rekodi iwe na **refs kamili** (snapshot→policy→decision→gate→execution) → **training-data-ready**.

---

## Kanuni elekezi (kabla ya maswali 8)

Engine (D6), Gate (E1), Recorder (E2) zote ni **stateless** — kila moja inapokea, inazalisha object
mpya, inasahau. Lakini objects hizo lazima **ziishi mahali** ili D8 (decision quality) na K6 (lessons/
datasets) ziweze kujifunza kutoka kwao. **E3 ndio "kumbukumbu" ya mfumo:**

```text
Engine/Gate/Recorder = FUNCTIONS (pure, stateless)  →  hazihifadhi kitu
Decision Repository   = MEMORY   (stateful, append-only)  →  inahifadhi kila kitu, milele (P85)
```

Hii ndiyo sababu ya kiarchitecture E3 ipo tofauti: **statefulness imefungiwa hapa** ili Engine ibaki
safi (P97). Repository si Engine mwingine — ni **store + query service**. Sentensi yake moja:

```text
append(record) → (never mutate)  ·  query(by refs) → records + lineage kamili (training-data-ready)
```

Nafasi kwenye pipeline (E3 = confluence ya Track A na Track B):

```text
  TRACK A (machine):  Snapshot→Engine→Decision(PROPOSED)→Gate→Decision(VALIDATED)→Recorder→Execution
                                          │        │              │                        │
                                          └────────┴──────────────┴────────────────────────┘
                                                          ▼ append (P85, immutable)
                                            ┌──────────────────────────────────┐
                                            │      DECISION REPOSITORY (E3)     │  ← state iko HAPA (P106)
                                            │  append-only · refs · query       │
                                            └──────────────────────────────────┘
                                                          ▼ query (lineage kamili)
  TRACK B (mind):     D8 Decision Quality   ·   K6 Lessons/Datasets   ·   K2 Graph (record nodes)
```

---

## Q1 — Repository responsibilities (NINI inafanya)

| # | Responsibility | Doctrine |
|---|----------------|----------|
| 1 | **Kuhifadhi (append)** records immutable: Decision (PROPOSED/VALIDATED/REJECTED) · Execution · Settlement | P85/P83; P106 |
| 2 | **Kuweka index** kwa refs (id, parent_decision_id, evidence_refs/snapshot, policy_id, gate_id) | P84/P88 |
| 3 | **Kuhudumia queries**: by-id · by-snapshot · by-policy · by-status · **lineage(id)** (chain kamili) | P106 (D8+K6) |
| 4 | **Kuhifadhi provenance chain** bila kuivunja — record moja → lineage kamili (training-data-ready) | P84/P85; Master §2 |

Hakuna jukumu la tano. Repository **haitafsiri** data (haihesabu quality — D8; haitengenezi lessons —
K6); inahifadhi na kuhudumia tu. *Store, don't interpret.*

## Q2 — Repository boundaries (NINI HAIFANYI — kamwe)

| Boundary | Maana | Doctrine |
|----------|-------|----------|
| ❌ SI Engine | Haina decision/eligibility/execution logic; inahifadhi matokeo ya hizo | **P97/P106** |
| ❌ Hakuna mutation/update/delete | Append-only pekee; kurekebisha = record MPYA (correction), history ibaki | **P85** |
| ❌ Hakuna quality computation | Decision quality/FDR/outcome-scoring ni **D8** — Repo inatoa data, D8 inahesabu | P87; Master |
| ❌ Hakuna lesson generation | Lessons/datasets ni **K6/K1** — Repo ni chanzo (L0/L1 raw), si mzalishaji | Master §3.4 |
| ❌ Hakuna market/broker imports | Records ni frozen dicts; storage backend ni injected; core = stdlib (Rule 4/P107) | Rule 4/P107 |
| ❌ Hakuna reliability-as-probability | Repo inahifadhi `reliability` kama rekodi tu (kama Decision Object) | **RED LINE/P70** |
| ❌ Hakuna in-Engine state | Repository ni component tofauti; Engine haiiimport wala haitegemei state yake | P103/P106 |

## Q3 — Inputs

| Input | Aina | Sharti |
|-------|------|--------|
| `record` | Decision · Execution · Settlement (immutable/frozen) | Lazima ipite structural validation (Q8): ina `id`, `kind`, refs sahihi. Repo inaikubali **as-is** (haibadilishi). |
| `backend` | StorageBackend (injected) | Interface: `put(id, record)` · `get(id)` · `iter()` — opaque. In-memory (self-test) au JSONL/duckdb (prod). Repo haijui backend ni ipi. |
| query params | id / snapshot_id / policy_id / status / kind | Kwa Q4 queries. |

**Storage backend ni NJE ya Repository core (mirror P96/E1-E2 injection):** core ya Repo ni pure
(stdlib); backend halisi (file/db) inapita kama argument — kama report/constraint zilivyo injected.

## Q4 — Outputs

| Query | Output | Mtumiaji |
|-------|--------|----------|
| `get(id)` | record moja (immutable) | wote |
| `by_snapshot(sid)` / `by_policy(pid)` / `by_status(s)` / `by_kind(k)` | orodha ya records | D8, K6 |
| **`lineage(id)`** | **bundle ya training-data-ready**: `{snapshot_id, proposed, validated|rejected, gate/eligibility, execution, settlement}` — chain nzima kutoka record moja | **K6/K2/D8** |
| `history(kind?)` | append-only stream (kwa dataset builds, K4/K6) | K6 |

**`lineage()` ndiyo output ya msingi ya E3↔K6:** kutoka execution_id (au decision_id), inarudisha
**mnyororo kamili** — hii ndiyo "training example" moja: *muktadha (snapshot) → sera (policy) →
uamuzi (decision) → ustahiki (gate/eligibility) → matokeo (execution/settlement)*. Bila E3, refs
zipo lakini hazijaunganishwa; E3 inaziunganisha kuwa rekodi inayoweza kufundisha.

## Q5 — Error handling

| Kesi | Tabia | Kwa nini |
|------|-------|----------|
| `append` ya id iliyopo (duplicate) | **RepositoryError** (`duplicate_id`) — SIO overwrite | P85 (immutability; overwrite = mutation) |
| Record haina refs sahihi (parent haipo) | **Chaguo la Chief (Open Q#3):** (a) RepositoryError(`dangling_ref`) au (b) kukubali + `resolve()` ionyeshe gap | Integrity vs ingest-order |
| Record malformed kimuundo (Q8) | **RepositoryError** (`invalid_record`) | P83 |
| `get`/`lineage` ya id isiyopo | **None / partial lineage** (SIO error — query miss ni halali) | query semantics |
| Backend I/O failure | **RepositoryError** (`backend_failure`, imerekodiwa) | Repo haiokoi backend |

RepositoryErrors → error log; history yenyewe (P85) inabaki safi (records halali pekee).

## Q6 — Audit / provenance

- **Repository YENYEWE ndio audit/history ya mfumo** (P85) — kila append ni rekodi ya kudumu. Hakuna
  audit tofauti inayohitajika juu yake; append log = ukweli.
- Provenance chain (Q4 `lineage`): `Settlement → Execution → Decision(VALIDATED) → Decision(PROPOSED)
  → Snapshot → Set → Operations → Objects` (P84/P85 kamili).
- **Reproducibility vector** (kila record): `{snapshot_id, policy_id, gate_id, recorder_id}` +
  (roadmap P95) `{schema_version, doctrine_version}` → training example inajitosheleza.

## Q7 — Injection (storage backend)

- **Dependency injection tupu:** `Repository(backend)` — backend inapita kama argument. Core haina
  file-path/db-connection iliyofichwa.
- Repo inagusa **surface tatu za backend**: `put(id, record)` · `get(id)` · `iter()`. Chochote kingine
  (indexing internals, transactions) ni opaque.
- **Swappability:** InMemoryBackend (self-test, R-1 mitigation — bila data ya nje) · JsonlBackend
  (prod, append-only file) · DuckDbBackend (D8 heavy queries, baadaye). Repo code haiguswi.

## Q8 — Validation (structural)

Validation ni **structural PEKEE** juu ya record kabla ya append:

```text
G1  ina `id` (kipekee kwa kind)                                   → invalid_record
G2  ina `kind` ∈ {DECISION, EXECUTION, SETTLEMENT}                → invalid_record
G3  ina refs zinazolingana na kind:
      DECISION   → evidence_refs (snapshot) + policy_id           → invalid_record
      EXECUTION  → parent_decision_id (→ VALIDATED)               → invalid_record
      SETTLEMENT → parent_execution_id (→ EXECUTION)              → invalid_record
G4  record ni frozen/immutable (A-4)                              → invalid_record
G5  `id` haipo tayari kwenye store                                → duplicate_id (Q5)
```

Repo **HAIhakiki** semantics (je uamuzi ulikuwa sahihi? — D8; je ushahidi ulitosha? — policy);
inathibitisha muundo + refs + uniqueness tu.

---

## SCHEMA — Training-data-ready record (E3 ↔ K6/K2)

Kila record iliyohifadhiwa ina **envelope** ya kawaida (ili K2 graph iunde `record` nodes na K6
ijenge datasets bila kubuni):

```yaml
id:        <exec:… | dec:… | settle:…>      # kipekee, stable (P83)
kind:      DECISION | EXECUTION | SETTLEMENT
refs:                                       # provenance kamili — ndiyo msingi wa training-data-ready
  snapshot_id:  snap:…                      # (DECISION; huzunguka kwa lineage)
  policy_id:    policy:name@vN              # (DECISION)
  gate_id:      gate:integrity@v1           # (VALIDATED/REJECTED)
  parent_decision_id:  dec:…                # (EXECUTION → VALIDATED; DECISION-VALIDATED → PROPOSED)
  parent_execution_id: exec:…              # (SETTLEMENT → EXECUTION)
  recorder_id:  recorder:execution@v1       # (EXECUTION)
payload:   <object frozen kamili (Decision/Execution/Settlement)>
versions:  {schema_version, doctrine_version}   # roadmap P95 — reproducibility kamili (Open Q#4)
appended_at: <int>                          # wakati wa kuingia store (SIO as_of ya object)
```

**`lineage(id)`** inakusanya records zote za mnyororo kuwa **training example moja**:
`context(snapshot) → policy → proposed → eligibility(gate) → validated → execution(outcome) →
settlement(pnl)`. Hii ndiyo hasa "raw material ya K6" (Master §2) — S3 Execution Stream inasoma hapa.

## STORAGE BACKEND — pendekezo (Chief achague; Open Q#2)

```text
(a) InMemoryBackend  — dict; kwa self-test (Rule 7, bila data ya nje) + tests. LAZIMA ipo.
(b) JsonlBackend     — append-only .jsonl (json ya stdlib); human+machine readable, git-friendly,
                       inalingana na K4 dataset builds (file-based, L3). PENDEKEZO kwa prod default.
(c) DuckDbBackend    — kwa D8 heavy analytical queries (baadaye; duckdb tayari ipo repo kwa Market).
```

**Pendekezo langu:** core ya Repository iwe **pure/stdlib** (interface + in-memory + JSONL) →
**transitively PURE** (kama frozen/execution_object). DuckDB backend = adapter ya hiari ya baadaye
(D8), haiingii core (iepushe P107 leak). JSONL append-only = default: inaheshimu P85 (append =
kuandika mstari; kamwe usifute), R-1 (readable bila DB), na L3 dataset pattern.

## SETTLEMENT / PnL — definition (E2 Open Q#2; Chief aliomba hapa)

E2 ilisema Execution Object inaishia FILLED/PARTIAL/REJECTED/UNFILLED (fill outcome); **PnL/return
haipo E2**. E3 inafafanua **Settlement Record** kama object wa tano (ndugu wa Evidence/Decision/
Execution/Lesson):

```text
Settlement Record (immutable, frozen):
  id: settle:…
  parent_execution_id → EXECUTION (entry)          # + optional exit_execution_id (close)
  realized_pnl · return · holding_period · costs   # matokeo halisi baada ya position kufungwa
  as_of (close time)
```

- **Nani anaizalisha:** close-fills zinatoka **broker (E4)**; settlement = pairing ya entry+exit
  executions + hesabu ya PnL. **Component ya settlement = E4-adjacent** (inahitaji broker outcome).
- **E3 scope:** inafafanua **schema + storage + lineage** ya Settlement (ili D8/K6 zisome), SIO
  broker-connection wala PnL-model. Decision-quality (je PnL hii ni edge?) ni **D8** (per-decision
  OOS + FDR). **Settlement records the number; D8 judges it; K6 learns from it.**
- **Open:** je Settlement ni object tofauti au extension ya Execution? **Pendekezo:** object tofauti
  (Execution = fill outcome, immutable mara moja; Settlement = realized outcome baada ya close —
  events tofauti kwa wakati). Chief athibitishe (Open Q#1).

---

## VERDICT — E3 Specification

→ Spec inajibu maswali 8 na inafunga E3 kwenye: **persistence + query service NJE ya Engine (P106)** —
append-only (P85), immutable records (A-4), refs kamili → **training-data-ready** (`lineage()` =
training example moja). Statefulness imefungiwa hapa ili Engine/Gate/Recorder zibaki pure (P97/P103).
Storage backend = injected (core pure/stdlib; JSONL default; DuckDB baadaye). Settlement Record
imefafanuliwa (schema/storage/lineage E3; broker/PnL-source = E4; quality = D8). E3 = mkutano rasmi
wa Track A na Track B (E3↔K6). **Store, don't interpret.**

**Hakuna code iliyoandikwa.** Implementation baada ya Chief kupitisha spec + Open Questions #1
(Settlement object) na #2 (backend default).

## Known Limitations

1. **Settlement inahitaji broker (E4)** — E3 inafafanua schema/lineage tu; close-fills + PnL halisi
   ni E4. Hadi E4, Settlement records ni injected (simulator).
2. **Repository ni STATEFUL** — tofauti na Engine/Gate/Recorder. Ni kwa makusudi (P106): state
   imefungiwa hapa. Self-test itatumia InMemoryBackend (bila data ya nje, Rule 7).
3. **P95 (schema_version/doctrine_version) ni roadmap** — reproducibility vector kamili haijafungwa;
   `versions` field imependekezwa lakini inahitaji Chief approval.
4. **D8 na K6 hazipo bado** — E3 inahudumia data kwa consumers ambao bado hawajajengwa; interface
   imeundwa kwa mahitaji yao yaliyotajwa (Master §2/§3), itathibitishwa zitakapofika.
5. **Ref-integrity policy (dangling) haijaamuliwa** — Open Q#3 (strict reject vs lenient ingest).

## Open Questions (kwa Chief — Rule 1)

1. **Settlement = object tofauti au extension ya Execution?** Pendekezo: object tofauti (events
   tofauti kwa wakati: fill vs realized-close). Inaathiri schema ya E3.
2. **Storage backend default** — JSONL (pendekezo langu: append-only, stdlib-pure, L3-aligned) au
   DuckDB (query-fast lakini inaleta dependency kwenye core)? Pendekezo: JSONL core + DuckDB adapter
   ya hiari (nje ya core, iepushe P107).
3. **Dangling-ref policy** — append ikatae record yenye parent isiyopo (`dangling_ref`) au ikubali +
   `resolve()` ionyeshe gap? Pendekezo: lenient ingest (order-independent) + `lineage()` inaonyesha
   gaps; integrity-check ni query tofauti.
4. **`versions` vector (P95)** — tuongeze `schema_version`/`doctrine_version` kwa kila record sasa
   (reproducibility kamili kwa K6) au tuahirishe? Pendekezo: ongeza sasa — ni cheap, na K6 itaihitaji.
5. **Query surface kwa K6/D8** — je queries za sasa (by-snapshot/policy/status + lineage) zinatosha,
   au Track B inahitaji zaidi (mf. by-regime, by-outcome)? Napendekeza **kikao kifupi na RESEARCHER-K/
   Chief** kabla ya implementation (schema "ijadiliwe na mahitaji ya Track B mezani" — agizo lako).

---

*Decision Repository = persistence + query NJE ya Engine (P106); append-only (P85); records immutable
(A-4); refs kamili → training-data-ready (lineage = training example); state imefungiwa hapa (Engine
inabaki pure — P97/P103); backend injected (core stdlib-pure; JSONL default); Settlement = object wa
tano (broker/PnL=E4, quality=D8). E3 = mkutano wa Track A↔B (E3↔K6). NO code bado. NO ML. Store, don't
interpret. Profitable ≠ Tradable Edge. Protect capital first.*
