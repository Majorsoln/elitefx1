# Execution Object Specification — EXECUTION ≠ DECISION (E2, P89)

*2026-07-04 | Deliverable ya kwanza ya E2 (Chief: "E2 Execution Object spec — document-first, maswali
8"; E1 CLOSED) | Coding inaanza TU baada ya spec hii kupitishwa | NO code bado | NO ML | NO broker
(E4) | NO PnL/attribution (E3/D8)*

> **P89** Execution ni **immutable object TOFAUTI** na Decision Object — inarekodi *kilichotekelezwa*
> (fills/slippage/rejects/partial), si *kilichoamuliwa*. **P87** Decision Integrity ≠ Decision Outcome
> → **outcome inaishi hapa**, si kwenye Decision Object. **A-4 (R-5)** immutability by-convention →
> **enforcement (frozen)** inafungwa E2. **Crossing** VALIDATED→EXECUTED = **object MPYA + parent_id**
> (mirror E1 — sio mutation; P83/P85). Broker = **E4**; PnL/decision-quality = **E3/D8** (nje ya E2).

---

## Kanuni elekezi (kabla ya maswali 8)

Engine (D6) na Gate (E1) zilikuwa sentensi moja kila moja. E2 ina **vipande viwili** vinavyoshikamana:

```text
1. EXECUTION OBJECT   (object)  : rekodi immutable ya outcome ya utekelezaji mmoja
2. EXECUTION RECORDER (component): VALIDATED Decision + ExecutionReport → Execution Object MPYA
   + A-4 IMMUTABILITY ENFORCEMENT (cross-cutting): frozen kwa objects zote za domain
```

Mstari wa msingi wa doctrine (kinachotofautisha E2 na kila kitu kilichotangulia):

```text
DECISION OBJECT (D4/E1)  = "tuliamua NINI, na ushahidi ulikuwa halali kiasi gani"  → INTENT + INTEGRITY
EXECUTION OBJECT (E2)    = "KILICHOTOKEA sokoni tulipojaribu kutekeleza"           → OUTCOME (P87)
```

Decision inaishia VALIDATED (imeruhusiwa — E1). **Execution ni object mpya, wa nne** (ndugu wa
Evidence/Decision/Execution/Lesson — Master Architecture §7.2). E2 **haitekelezi** biashara yenyewe
(hakuna broker — E4); inafafanua **jinsi outcome inavyorekodiwa** ikiwasili, na **enforcement ya
immutability** kabla ya domain kukua zaidi. Kila kitu kingine ni kufafanua mipaka ya vipande hivyo.

Nafasi kwenye pipeline:

```text
Snapshot ─▶ Engine ─▶ Decision(PROPOSED) ─▶ Gate(E1) ─▶ Decision(VALIDATED) ─▶ Recorder(E2) ─▶ Execution Object
 (P79)      (D6)         (P83)               (E1)          (P85, parent)      + ExecutionReport   (P89, parent=VALIDATED)
                                                                              (injected; broker=E4)
```

---

## Q1 — Execution Object: NI nini (fields — kilichorekodiwa)

Execution Object ni **rekodi immutable ya outcome ya jaribio MOJA la utekelezaji** wa Decision moja
VALIDATED. Fields (structural — sio hesabu ya edge):

| field | maana | doctrine |
|-------|-------|----------|
| `id` | identity immutable (`exec:<hash>`) | P83/P89 |
| `parent_decision_id` | → Decision Object **VALIDATED** iliyotekelezwa (provenance) | P85 (mirror E1) |
| `status` | outcome state (Q4 lifecycle): FILLED · PARTIAL · REJECTED · UNFILLED | P89 |
| `intended` | `{side, qty, ref_price}` — **nakala** kutoka decision (intent) | P87 (intent vs outcome) |
| `fills` | orodha ya `{qty, price, ts}` — kilichojazwa kweli (0..n) | P89 |
| `filled_qty` / `remaining_qty` | jumla iliyojazwa / iliyobaki (partial → remaining>0) | P89 |
| `avg_fill_price` | wastani wa fills (None kama UNFILLED/REJECTED) | P89 |
| `slippage` | `avg_fill_price − ref_price` (kiasi, **si tathmini**) | P89 |
| `reject_reason` | kama REJECTED: sababu ya broker/constraint (opaque string) | P81 |
| `report_ref` | reference ya ExecutionReport chanzo (Q7; broker=E4) | P84-style |
| `timestamp` | wakati wa outcome (as-of ya report) | — |
| `audit` | rekodi ya recorder (Q6) — imerithi + execution entries | P66 |

**Execution Object HAINA:** PnL, return, holding-period, decision-quality — hizo ni **outcome
aggregation (E3)** na **decision-quality (D8)**, si execution-recording. Execution inarekodi *nini
kilitokea kwenye kuweka order*, si *ilikuwa na faida kiasi gani*.

## Q2 — Boundaries (Execution Object / Recorder HAIFANYI — kamwe)

| Boundary | Maana | Doctrine |
|----------|-------|----------|
| ❌ Execution ≠ Decision | Haibadilishi/haimutate Decision Object; ni object mpya tofauti | **P89** |
| ❌ Hakuna decision logic / re-decide | Recorder haiamui side/qty; hizo zinatoka decision (intent) | P97 |
| ❌ Hakuna broker connectivity | Haiunganishi API, hai-send order — ExecutionReport ni **injected** (broker=E4) | **P81/E4** |
| ❌ Hakuna PnL / return / attribution | Outcome-aggregation ni E3; decision-quality/FDR ni D8 | Master §3.2 (S3→E3); P87 |
| ❌ Hakuna FTMO/MWONGOZO hardcode | Constraints za execution ni injected (E1 Gate/E4); rejects zinarekodiwa kama **fact** tu | **P81** |
| ❌ Hakuna eligibility re-check | Eligibility ilishafanywa (E1 Gate); Recorder inatekeleza decision VALIDATED iliyoruhusiwa | E1 |
| ❌ Hakuna import ya Market/Broker Science | Imports: `decision_object` (+ freeze util) + stdlib (mirror Rule 4/P107) | Rule 4/P107 |
| ❌ Hakuna mutation | Recorder inaunda object MPYA; frozen enforcement (A-4) inazuia mutation kimuundo | **P83/A-4** |

## Q3 — Inputs

| Input | Aina | Sharti |
|-------|------|--------|
| `decision` | Decision Object | Lazima ipite structural validation (Q8) **NA** `lifecycle == "VALIDATED"`. Recorder inatekeleza decisions zilizoruhusiwa (E1) pekee — PROPOSED/REJECTED ni makosa (Q5). |
| `report` | ExecutionReport (injected, opaque) | `{status, fills:[{qty,price,ts}], reject_reason?, as_of}` — kilichotoka kwa mtekelezaji (broker=E4, au simulator/caller kwa sasa). Recorder inaipokea, hai-generate. |

**Chanzo cha ExecutionReport ni NJE ya E2 (mirror P96/E1):** hadi Broker Adapter (E4) ifafanuliwe,
caller (Japhet/simulator) ndiye anayepitisha report. Recorder kamwe haina broker-connection iliyofichwa.

## Q4 — Outputs + VALIDATED→EXECUTED crossing

Output ni **Execution Object MPYA immutable (P83/P89)** — object wa aina TOFAUTI na Decision (sio
lifecycle-bump ya decision). **Crossing VALIDATED→EXECUTED (Chief E2, mirror E1):**

```text
Decision(VALIDATED)  ──recorder(decision, report)──▶  Execution Object MPYA
   (inabaki kama ilivyo,                                id mpya (exec:…),
    immutable — P83)                                    parent_decision_id = <VALIDATED id>  (P85)
```

- **Decision Object HAIMUTATE.** History: `VALIDATED → (execution recorded)` = objects **mbili
  tofauti** (Decision + Execution) zilizounganishwa kwa `parent_decision_id`. Append-only (P85).
- **Execution lifecycle (status)** — state ya outcome, si ya decision:

```text
        ┌──────────┐  fills == intended        FILLED
report ▶│ RECORDER │──────────────────────────▶ PARTIAL   (0 < filled < intended; remaining > 0)
        └──────────┘  fills == 0 & rejected  ▶  REJECTED  (reject_reason imerekodiwa)
                      fills == 0 & no reject ▶  UNFILLED   (order haikujazwa; hakuna reject rasmi)
```

- **Partial fills:** Execution Object moja inabeba `fills:[…]` + `filled_qty/remaining_qty`. Kama
  remaining>0 kunahitaji decision/utekelezaji mpya — hilo ni **downstream** (caller/E3), si E2.
- **Settlement:** `SETTLED` (P-lifecycle ya zamani) = hatua ya baadaye (E3/settlement); **E2 inaishia
  kwenye outcome ya utekelezaji** (fill/partial/reject/unfilled). Tazama Open Questions #2.

## Q5 — Error handling

Kanuni kuu (mirror Engine/Gate): **Recorder kamwe HAIBUNI outcome.** Ikishindwa ku-record, inatoa
**ExecutionError** (system failure) — SIO Execution Object bandia. Tofauti muhimu:

| Kesi | Tabia | Kwa nini |
|------|-------|----------|
| Order **REJECTED** na broker/constraint | **SIO error** → Execution Object `status=REJECTED` (reject_reason) | Reject ni **outcome halali** (fact ya soko), si kushindwa kwa recorder |
| Order **UNFILLED** (haikujazwa) | **SIO error** → `status=UNFILLED` | Outcome halali |
| `decision` invalid kimuundo (Q8) | **ExecutionError** (`invalid_decision`) | P83 |
| `decision.lifecycle != VALIDATED` | **ExecutionError** (`invalid_lifecycle`) | Recorder inatekeleza VALIDATED pekee (E1) |
| `report` haitimizi contract (hakuna status/fills) | **ExecutionError** (`invalid_report`) | Q7 contract |
| `report` fills zinapingana (filled > intended, price<0) | **ExecutionError** (`inconsistent_report`) | integrity ya structural |

ExecutionErrors → **error log** (auditable), SIO execution history (P85 ni ya outcomes halali:
FILLED/PARTIAL/REJECTED/UNFILLED). Mirror kamili ya EngineError/GateError: **failure ya mfumo ≠
outcome.**

## Q6 — Audit / provenance

Recorder inaandika **execution audit** (nyongeza juu ya P66):

```text
exec.receive   {decision_id, lifecycle}
exec.record    {decision_id, status, filled_qty, slippage}
exec.reject    {decision_id, reject_reason}          (status = REJECTED)
```

Provenance chain kamili (P84/P85):

```text
Execution ──parent_decision_id──▶ Decision(VALIDATED) ──parent_decision_id──▶ Decision(PROPOSED)
          ──▶ Snapshot ──▶ Set ──▶ Operations ──▶ Objects
```

- Execution Object inarithi audit ya decision + inaongeza execution entries → **fully traceable**.
- Reproducibility ya execution = `{parent_decision_id, report_ref}`. Broker/venue metadata itakuja E4.

## Q7 — Injection (ExecutionReport / broker-fills)

- **Dependency injection tupu (mirror policy/constraint):** `record(decision, report)` — report
  inapita kama argument. Hakuna broker-client ndani ya Recorder, hakuna default, hakuna venue-config.
- Recorder inagusa **surface za report tu**: `status`, `fills`, `reject_reason`, `as_of`. Chochote
  kingine (venue internals) ni opaque.
- **Broker/MWONGOZO/FTMO inaingia E4 (P81):** Broker Adapter ndiyo itakayozalisha ExecutionReport
  halisi kutoka MWONGOZO/FTMO execution. E2 inafafanua **contract ya report**, si broker yenyewe —
  kama E1 ilivyofafanua contract ya constraint bila FTMO hardcode.
- **Swappability:** simulator-report leo, broker-report (E4) kesho — Recorder code haiguswi; contract
  ile ile. (D5 Q4 pattern.)

## Q8 — Validation (structural)

Validation ya Recorder ni **structural PEKEE** — kwenye Decision Object (VALIDATED) na ExecutionReport.
Haihesabu chochote (slippage ni kutoa, si tathmini; RED LINE/P97).

```text
Decision (mirror E1/Q8):
  V1  ni Decision Object halali (id, action, evidence_refs, policy_id, audit)   → invalid_decision
  V2  lifecycle == VALIDATED                                                    → invalid_lifecycle
  V3  action ni committing intent (ENTER/EXIT/…); ABSTAIN/WAIT haihitaji exec   → tazama Open Q#3

Report:
  R1  ina status ∈ {FILLED, PARTIAL, REJECTED, UNFILLED}                         → invalid_report
  R2  fills ni orodha ya {qty≥0, price≥0, ts}                                    → invalid_report
  R3  status vs fills zinaoana (FILLED→remaining==0; REJECTED→fills==[])         → inconsistent_report
```

---

## A-4 — IMMUTABILITY ENFORCEMENT (cross-cutting; Chief E2)

**Tatizo (R-5/A-4):** objects zote (Evidence/Decision/Execution) ni Python **dicts** — immutable
**kwa makubaliano** tu (`make_*`/`transition`/`make_gate_decision` zinarudisha dict mpya). Hakuna
kinachozuia agent/mtu ku-`obj["lifecycle"]="EXECUTED"` kwa bahati mbaya; provenance/audit
ingebaki sahihi kwa **jina** tu. Kadri domain inavyokua (E2→E4), hii ni hatari.

**Pendekezo (Chief achague — SIO uamuzi wangu, Rule 1):**

```text
(a) frozen dataclasses (typed, frozen=True) kwa Evidence/Decision/Execution
    + : type-safe, __setattr__ inazuia mutation kikamilifu
    − : refactor kubwa ya make_* zote; inagusa Evidence Layer (interface-frozen — P90)
(b) freeze() utility: recursive deep-freeze → MappingProxyType (read-only views)
    + : ndogo, stdlib PEKEE (Rule 4/P107), dict-compatible; make_* zinaita freeze() mwishoni
    − : underlying dict bado ipo kama reference ya ndani; deep-copy inahitajika kabla ya proxy
(c) freeze kwenye construction-boundary tu + immutability self-test kila module (runtime check)
    + : ndogo zaidi; inakamata regression kwenye tests
    − : haizuii mutation kwa vitendo (test-time detection, si prevention)
```

**Pendekezo langu:** **(b) kwa objects MPYA (Execution) + Decision**, kama utility ya pamoja
(`freeze(obj)` — deep-freeze → `MappingProxyType`, stdlib pekee). **Evidence Layer retrofit iachwe
kwa uamuzi tofauti wa Chief** (ni interface-frozen — P90; kuigusa implementation yake ni nje ya E2
scope). Hii inafunga A-4 kwa domain inayoendelea kukua bila kuhatarisha frozen layer.

**Athari kwa E1/D4 (Rule 1 — nasimama, nauliza):** `transition()`/`make_gate_decision`/`make_decision`
zingehitaji kuita `freeze()` mwishoni, na self-tests zingehitaji ku-assert mutation inakataliwa. Hii
ni edit ya `decision_object.py` — inahitaji Chief approval kabla ya code (Open Q#4).

---

## Mchoro wa mwisho (Execution ndani ya architecture)

```text
                              ┌─────────────────────────────────┐
  (Broker Adapter = E4)       │       EXECUTION RECORDER (E2)     │
ExecutionReport ──report────▶ │  validate(decision, report) Q8    │
(injected; fills/slippage)    │  status ← outcome (Q4)            │──▶ Execution Object MPYA
                              │  wrap + audit (Q6)                │    (P89; parent_decision_id → VALIDATED)
Decision(VALIDATED) ────────▶ │  Execution ≠ Decision (P89)       │──▶ ExecutionError (Q5, si outcome)
   (from Gate E1, P85)        └─────────────────────────────────┘
                                   hakuna decision logic (P97)
                                   hakuna broker connection (P81/E4)
                                   hakuna PnL/attribution (E3/D8)
                                   hakuna mutation — frozen (A-4)
```

---

## VERDICT — E2 Specification

→ Spec inajibu maswali 8 na inafunga E2 kwenye: **(1) Execution Object** = rekodi immutable ya outcome
(P89, TOFAUTI na Decision — P87); **(2) Execution Recorder** = component inayounda Execution Object
MPYA kutoka Decision VALIDATED + ExecutionReport injected (crossing = object mpya + parent_id, mirror
E1); **(3) A-4 immutability enforcement** = frozen mechanism kwa domain objects. Broker (E4),
PnL/attribution (E3/D8), na eligibility (E1) ziko NJE kwa makusudi. **Execution ≠ Decision** ndiyo
mstari mkuu. Recorder ni component ndogo kama Engine/Gate — na ndivyo inavyopaswa.

**Hakuna code iliyoandikwa.** Implementation inaanza baada ya Chief kupitisha spec hii **na** kutolea
uamuzi Open Questions #1 (crossing/lifecycle reconciliation) na #4 (A-4 mechanism) — zote zinagusa
`decision_object.py` (D4, approved) → Rule 1.

## Known Limitations

1. **Broker haipo (E4)** — ExecutionReport ni injected; hakuna fill halisi wa soko. E2 inafafanua
   contract tu; decision-executable ≠ decision-filled hadi E4.
2. **A-4 (b) MappingProxyType haizui deep-mutation kikamilifu** bila deep-copy kabla ya proxy —
   implementation lazima i-freeze recursively (nested dicts/lists → tuple/proxy). Ni engineering
   detail ya utekelezaji, imeainishwa hapa.
3. **Evidence Layer retrofit ya A-4 imeachwa nje** (interface-frozen, P90) — enforcement kamili ya
   domain nzima inahitaji uamuzi tofauti wa Chief.
4. **SETTLED/settlement haijafafanuliwa E2** — E2 inaishia kwenye execution outcome; settlement/PnL ni
   E3. Lifecycle ya zamani ya Decision (EXECUTED→SETTLED) inahitaji reconciliation (Open Q#1).
5. **Spec haithibitishi chochote kiuchumi** — slippage ni kiasi kilichorekodiwa, si tathmini ya edge;
   Profitable ≠ Tradable Edge; Protect capital first.

## Open Questions (kwa Chief — sihamishi bila uamuzi; Rule 1)

1. **Lifecycle reconciliation (BLOCKER — inaendeleza E1 Open Q#6).** Decision Object ya sasa ina
   lifecycle `PROPOSED→VALIDATED→EXECUTED→SETTLED` na `transition()` inaruhusu VALIDATED→EXECUTED
   (same-id). Kama Execution ni **object mpya tofauti** (P89), je EXECUTED/SETTLED **ziretire kutoka
   Decision lifecycle** (kama PROPOSED→VALIDATED ilivyoretire E1), na Decision iishie **VALIDATED**?
   **Pendekezo:** ndiyo — Decision-domain inaishia VALIDATED; execution-outcome ni Execution Object.
   Retire VALIDATED→EXECUTED na EXECUTED→SETTLED kutoka `transition()`.
2. **SETTLED ni Execution-lifecycle au object tofauti (E3)?** Je settlement (PnL realized) ni `status`
   ya Execution Object au object wa tano (Settlement)? **Pendekezo:** i-defer E3 — E2 status inaishia
   FILLED/PARTIAL/REJECTED/UNFILLED.
3. **Committing vs non-committing intents (V3).** ABSTAIN/WAIT hazitekelezwi — je Recorder ikatae
   (invalid) au izalishe Execution `status=UNFILLED` trivially? **Pendekezo:** Recorder inakataa
   non-committing kabla ya report (ni makosa ku-execute ABSTAIN) — invalid_decision. Chief athibitishe
   orodha ya committing intents (ENTER/EXIT/REDUCE/HEDGE?).
4. **A-4 mechanism (BLOCKER — inagusa D4/E1 code).** Chagua (a) frozen dataclass / (b) freeze() util /
   (c) construction-boundary+test. **Pendekezo:** (b) stdlib deep-freeze kwa Decision+Execution;
   Evidence retrofit = uamuzi tofauti. Utekelezaji unahitaji edit ya `decision_object.py` (freeze kwenye
   make_*) → Rule 1: nasimama.
5. **`intended` (side/qty/ref_price) inatoka wapi kwenye Decision Object?** D4 ya sasa ina `action`
   (INTENT) lakini **haina qty/side/ref_price** wazi. Je qty/sizing inaongezwa Decision Object (nani —
   policy? execution?) au inakuja na ExecutionReport? **Pendekezo:** sizing ni Execution Science concern
   (P81-adjacent) — inakuja na report/E4, si Decision. Chief aelekeze; hii inaathiri Q1 `intended`.

---

*Execution Object = immutable outcome record (P89), TOFAUTI na Decision (P87); Recorder = component
inayounda object mpya kutoka VALIDATED + ExecutionReport injected (parent_id, mirror E1); broker=E4,
PnL=E3/D8, eligibility=E1 (zote nje); A-4 immutability enforcement (frozen) = cross-cutting. Direct
imports safi (Rule 4). NO code bado. NO ML. NO broker. Profitable ≠ Tradable Edge. Protect capital
first.*
