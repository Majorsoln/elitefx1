# ARCHITECTURE AUDIT LOG — EliteFX

> Rekodi ya kudumu ya **Architecture Auditor** (role: Chief review 2026-07-02; Decision Doctrine V8).
> Kazi: kuhakikisha **Doctrine ⇄ Architecture ⇄ Implementation ⇄ Tests ⇄ Reports** havitelezi.
> Kila audit inamalizika na **Layer-Drift Matrix**, **Architectural Maturity** (amri ya Chief,
> 2026-07-02) na **Future Risk Assessment** iliyogawanywa **Architecture / Research / Governance**
> risks (taxonomy ya Chief, V9). Audit #1 = `docs/CHIEF_GAP_REVIEW.md` (APPROVED 2026-07-02).
>
> **MIPAKA YA ROLE (amri ya Chief, 2026-07-03):** Auditor **hakubali research · haanzishi doctrine ·
> ha-design implementation**. Anakagua compliance tu. Kwa hiyo Auditor **KAMWE hatumii** maneno ya
> approval ("APPROVED" ni la Chief pekee). Vocabulary rasmi ya verdicts za Auditor:
> **`Architecture Review: PASS`** / **`Architecture Review: FAIL`** / *"Compliant with current
> doctrine"*. Kila Architecture Review inamalizika na sehemu mbili za lazima:
> **(1) Compliance Matrix** (`| Principle | Status |`) na **(2) Architectural Drift Watch**
> (`| Item | Risk |`).
>
> **ROLE MERGE (Chief #1 restructure, 2026-07-03 — G-01):** kuanzia Audit #5, role ya Architecture
> Auditor **imeunganishwa ndani ya Chief Quant #2 (Doctrine Custodian & Architecture Governor)**.
> Reviews sasa ni **Architecture + Doctrine kwa pamoja**. Mipaka yote hapo juu inabaki (hakuna
> approval language; PASS/FAIL pekee; RED LINE — principle mpya inazaliwa kwa Chief #1 pekee).

---

## AUDIT #2 — 2026-07-02 (baada ya Chief review ya Audit #1)

Scope: hali ya mnyororo mzima baada ya amendments za Chief (P90/P91, G-7 @v2, G-8, hygiene G-2…G-6).

### Layer-Drift Matrix

| Layer | Status | Drift? |
|-------|--------|--------|
| **Doctrine** | Market V6.9 (FROZEN) + Decision V8 (ACTIVE) — SSOT mbili, zinaelekezana kwa usahihi | ❌ Hakuna |
| **Architecture** | Evidence Layer interface-frozen (P90); Decision Layer: Object → Policy → [Engine NOT YET ELIGIBLE] → [Execution OPEN P89] | ❌ Hakuna |
| **Implementation** | `evidence_object/operations/set/snapshot` + `decision_object` + `decision_policy` (@v2) — principles P63–P91 zinaonekana kwenye code | ⚠️ **Watch item W-1** (tazama chini) |
| **Tests** | Self-tests 6 modules × zote PASS (ikiwa ni pamoja na P86 CANCELLED mpya na G-7 explicit-conflict) | ❌ Hakuna |
| **Reports** | 54/55 zipo na zinaendana na ledger; **`decision_policy_report.md` PENDING (G-1)** — inasubiri data run ya Japhet | ⚠️ G-1 (inajulikana, APPROVED na Chief) |
| **Governance** | Board sasa ina D5 `[~]`, NOT YET ELIGIBLE wording, amendment/approval log za 2026-07-02; hygiene G-2…G-6 zimefungwa | ❌ Hakuna |

### Watch item W-1 — Decision code inaimport Market engines moja kwa moja

`decision_policy.py` / `decision_object.py` / evidence modules zinaimport `market_state_engine`,
`event_library`, `configuration_engine` n.k. **kwa demo-instantiation** (build_tagged_evidence).
P63/P64 zinasema Evidence Object ndiyo **API pekee** kati ya domains, na Decision Science ni
production-agnostic. Kwa research/demo hii inakubalika (evidence inajengwa mahali fulani), lakini:
**Decision Engine (D6) LAZIMA ipokee Snapshot pekee** — isiimport chochote cha Market domain.
Hii ni mstari mwekundu wa kwanza nitakaouangalia kwenye audit ya D6.

### Future Risk Assessment

| # | Risk (architectural, sio bug) | Probability | Impact |
|---|-------------------------------|-------------|--------|
| R-1 | **Governance-loop single point of failure:** kila report inahitaji data iliyo kwenye PC moja (Japhet, ~26GB nje ya git). Japhet akikosekana, workflow Research→Report inasimama (kama G-1 ilivyoonyesha kwa mara ya kwanza). | HIGH | HIGH |
| R-2 | **Reliability saturation (P70 OPEN) ndani ya policies:** thresholds HI/MID/LO zinapima Φ(EV/SE) inayojaa kwa n kubwa → policies zote zitaona "reliability juu" kwenye aggregates kubwa; SELECT/ABSTAIN itaamuliwa na artifact, sio ubora halisi. Ikifika D6/D8 bila confidence-model, kosa litajengwa ndani ya Engine. | HIGH | MEDIUM |
| R-3 | **Snapshot age-shift sare (D3 caveat) vs production event-time:** `_resolve` inashift age sawa kwa members wote. D6/D7 zitakapohitaji per-member event-time, semantics ya readiness inaweza kubadilika kimya — interface ile ile, maana tofauti (hatari ya P90 kwa upande wa semantics). | MEDIUM | HIGH |
| R-4 | **Redundancy P78 OPEN inaingia kwenye maamuzi:** members correlated (pair/TF zinazofanana) zinahesabiwa kama evidence huru → set reliability optimistic → policies zita-SELECT zaidi ya inavyostahili. Hatari inakua kila layer mpya inayotumia reliability bila kuisahihisha. | MEDIUM | HIGH |
| R-5 | **Immutability by-convention (Python dicts):** codebase inavyokua (D6–D9), mtu/agent anaweza ku-mutate object kwa bahati mbaya bila test kuikamata — provenance/audit ingebaki sahihi kwa jina tu. Frozen dataclasses au `freeze()` enforcement itahitajika kabla ya D7 Execution. | MEDIUM | MEDIUM |
| R-6 | **Doctrine sprawl:** files 47+ za doctrine (V1…V8 + patches) kwenye root; SSOT ni 2 tu. Hatari: mtu (au AI agent) kusoma version ya zamani kama ya sasa. Suluhisho jepesi: folder `doctrine/archive/` (hygiene ya baadaye — inahitaji Chief approval kwa sababu inahamisha files za rekodi). | LOW | MEDIUM |

### Verdict

Hakuna drift mpya. Gap pekee inayosimama ni **G-1** (report pending — nje ya uwezo wa environment
hii). W-1 ni mstari wa kukumbuka kwa D6, sio tatizo la leo. Architecture iko stable — na kwa mujibu
wa P90, sasa tunajua stability hiyo inamaanisha nini hasa: **contract haitikisiki; implementation
inaweza kupumua.**

*Profitable ≠ Tradable Edge. Protect capital first.*

---

## AUDIT #3 — 2026-07-02 (baada ya D5 kufungwa; Decision Doctrine V9)

Scope: hali baada ya D5 FULLY APPROVED, P92–P97, na kufunguliwa kwa D6 (specification-first).
Muundo mpya kwa amri ya Chief: + **Architectural Maturity**; risks zimegawanywa makundi matatu.

### Layer-Drift Matrix

| Layer | Status | Drift? |
|-------|--------|--------|
| **Doctrine** | Market V6.9 (FROZEN) + Decision V9 (ACTIVE); P92–P97 zimeingizwa board + doctrine | ❌ Hakuna |
| **Architecture** | Evidence (interface-frozen) → Policy (@v2) → [Engine: SPEC phase] → [Execution P89 OPEN]; dependency direction rasmi (P92) | ❌ Hakuna |
| **Implementation** | Decision chain kamili D0–D5; W-1 sasa inatawaliwa na P92 (demo-instantiation inaruhusiwa; Engine hairuhusiwi) | ⚠️ D-1 (tazama chini) |
| **Tests** | Self-tests 6 modules PASS (pamoja na P86 CANCELLED + G-7 explicit-conflict) | ❌ Hakuna |
| **Reports** | 55/55 — `decision_policy_report.md` imewasilishwa (run ya Japhet) na kureviewiwa | ⚠️ D-1 |
| **Governance** | D5 `[✓]` CLOSED; Q-047 CLOSED; Q-048 OPEN (D6 spec); approval log kamili | ❌ Hakuna |

### Drift item D-1 — Report @v1 vs Code @v2 (imerekodiwa, sio tatizo)

Report ya D5 iliyoapproved ilizalishwa na **policies @v1** (main wakati wa run ya Japhet — kabla
branch hii yenye G-7 @v2 haijamergiwa). Code ya sasa ni **@v2** (Chief-approved). Hii **SIO drift
ya kificho** — ni kesi ya kwanza halisi ya P88 kufanya kazi: version tofauti → decision ids tofauti;
provenance iko wazi. Mapendekezo: data run ijayo i-regenerate report kwa @v2 (optional; D5 imefungwa
kihalali). Nimeiweka hapa ili isionekane baadaye kama inconsistency isiyoelezwa.

### Architectural Maturity (sehemu mpya ya kudumu — amri ya Chief)

| Layer | Maturity |
|-------|----------|
| Market Science | **Stable** (FROZEN — P62; discovery imesimamishwa kwa makusudi) |
| Evidence Layer | **Frozen** (kwa interface — P90) |
| Decision Objects | **Stable** (D4 approved; P86/P87/P88 zimetestiwa) |
| Decision Policy | **Stable** (D5 CLOSED; @v2; illustrative rules — bado si validated economically) |
| Decision Engine | **Specification** (D6 ACTIVE; document-first; hakuna code) |
| Execution Object | **Not Started** (P89 OPEN) |
| Policy Selection | **Not Started** (P96 OPEN — gap mpya iliyotambuliwa na Chief) |
| Portfolio / Live | **Not Started** (NOT YET ELIGIBLE) |

### Future Risk Assessment (taxonomy mpya: Architecture / Research / Governance)

**Architecture Risks**

| # | Risk | Probability | Impact |
|---|------|-------------|--------|
| A-1 | **Reliability saturation (P70 OPEN)** ikiingia kwenye Engine kama probability — sasa ina RED LINE rasmi ya Chief; hatari inabaki hadi confidence-model ifungwe | HIGH | MEDIUM |
| A-2 | **Snapshot age-shift sare vs production event-time** (D3 caveat) — semantics zinaweza kubadilika kimya chini ya interface ile ile (P90 upande wa maana) | MEDIUM | HIGH |
| A-3 | **Redundancy P78 OPEN** — evidence correlated inahesabiwa mara mbili → reliability optimistic → policies zina-SELECT kupita kiasi | MEDIUM | HIGH |
| A-4 | **Immutability by-convention** (Python dicts) — enforcement (frozen structures) inahitajika kabla ya D7 Execution; P93 Canonical Domain Objects itasaidia hapa | MEDIUM | MEDIUM |
| A-5 | **Policy Selection layer haipo** (P96 OPEN) — bila hiyo, chaguo la policy litaishia ndani ya Engine au user kwa ad-hoc; ndiyo gap kubwa ya architecture iliyobaki | MEDIUM | HIGH |

**Research Risks**

| # | Risk | Probability | Impact |
|---|------|-------------|--------|
| R-1 | **Research Infrastructure Risk** (jina la Chief): kila report inahitaji data ya PC moja (~26GB, Japhet). Mitigation ndogo: kila engine ina `--self-test` isiyohitaji data | HIGH | HIGH |
| R-2 | **Policies ni illustrative** — hazijathibitishwa OOS; hatari ya kizazi kijacho kuzichukulia kama validated kwa sababu D5 ime-CLOSED (CLOSED = architecture, SIO edge) | MEDIUM | HIGH |

**Governance Risks**

| # | Risk | Probability | Impact |
|---|------|-------------|--------|
| G-1 | **Doctrine sprawl** — files 48+ za doctrine kwenye root; SSOT ni 2; hatari ya kusoma version ya zamani kama ya sasa (mitigation: Current Doctrine section ya board) | LOW | MEDIUM |
| G-2 | **Dual-branch race** — run za Japhet (main) na kazi ya implementer (branch) zinaweza kutofautiana version (kama D-1); mitigation: merge mapema, rebase mara kwa mara | MEDIUM | LOW |

### Verdict

Hakuna drift mpya isiyotawaliwa. D-1 imerekodiwa na inatawaliwa na P88. Gap kubwa ya architecture
iliyobaki ni **Policy Selection (P96)** — Chief ameiona kabla haijawa tatizo; hiyo ndiyo kazi ya
audit. D6 inaanza na specification — mstari wangu mwekundu wa kwanza kwenye review ya spec/code:
**hakuna import ya Market Science (P92), hakuna logic ndani ya Engine (P97), hakuna reliability-
kama-probability (RED LINE).**

*Profitable ≠ Tradable Edge. Protect capital first.*

---

## ARCHITECTURE REVIEW — D6 Decision Engine Specification — 2026-07-03

Scope: `reports/decision_engine_specification.md` (deliverable ya Q-048) dhidi ya Decision Doctrine
V9 na architecture iliyofungwa (D0–D5). Muundo mpya kwa amri ya Chief: Compliance Matrix +
Architectural Drift Watch; vocabulary ya Auditor (hakuna approval language).

Nini kimekaguliwa: consistency ya spec na doctrine · dependency direction · governance · principles.
Nini HAKIJAKAGULIWA (nje ya role): ubora wa research · design choices (hizo ni za Implementer na
uamuzi ni wa Chief — mf. EngineError-vs-ABSTAIN, INTENT migration).

### Compliance Matrix

| Principle | Status | Ushahidi kwenye spec |
|-----------|--------|----------------------|
| P77/P79 (Snapshot = canonical input pekee) | **PASS** | Q3 + Q8/S5 — Object/Set ghafi zinakataliwa |
| P80 (complete context; hakuna evidence calc) | **PASS** | Q2 — "Hakuna evidence calculations" |
| P82 (readiness = state machine; states ≠ errors) | **PASS** | Q5 — INVALID/STALE/EXPIRED = input ya policy, sio EngineError |
| P83/P84/P85 (immutable Decision; snapshot ref; history append-only) | **PASS** | Q4 |
| P86 (external constraints → CANCELLED lifecycle, sio Engine) | **PASS** | Q5 (P81 nje ya scope) |
| P88 (policy_id inarekodiwa) | **PASS** | Q4 + Q7 |
| P91 (eligibility; specification-first imeheshimiwa) | **PASS** | Hakuna code; deliverable ni document |
| **P92** (hakuna Market imports ndani ya Engine) | **PASS** | Q2 boundary + mchoro wa mwisho |
| **P94** (contract = njia pekee ya decision logic) | **PASS** | Q1/Q7 — surface mbili tu: `id` + `decide` |
| P95 (reproducibility vector — OPEN) | **PASS (noted)** | Q6 roadmap; haitekelezwi bila Chief |
| **P96** (policy selection external; hakuna hidden default) | **PASS** | Q3/Q7 — "Engine kamwe haina default policy iliyofichwa" |
| **P97** (orchestration only; hakuna logic) | **PASS** | Q1 (majukumu 4) + Q2 + Q8 (validation structural tu) |
| **RED LINE** (reliability ≠ probability hadi P70) | **PASS** | Q2 — reliability inapitishwa kama rekodi tu |
| P69 (decision-ready ≠ trade-ready; hakuna alpha claims) | **PASS** | Honest Caveat 5 |

### Architectural Drift Watch

| Item | Risk |
|------|------|
| Market imports (ndani ya Engine spec) | **None** |
| Policy logic leakage (thresholds/heuristics ndani ya Engine) | **None** |
| Reliability-as-probability | **None** |
| Engine growth (scope creep zaidi ya majukumu 4) | **Watch** — EngineError log ni artifact mpya (ndogo, yenye sababu); kila nyongeza ijayo ipimwe dhidi ya P97 |
| INTENT migration (inagusa ACTIONS enum ya D4 iliyoapproved) | **Watch** — inahitaji uamuzi wa Chief kabla ya code (spec Caveat 2) |
| Policy Selection pressure (P96 OPEN — layer haipo) | **Watch** — bila layer, chaguo la policy litajaribu kuingia ndani ya Engine au caller ad-hoc |

### Verdict ya Auditor

**Architecture Review: PASS — Compliant with current doctrine (V9).**

Wording note (mstari wa role): hii ni **ukaguzi wa architecture tu**. Approval ya specification
(Q-048) — pamoja na maamuzi ya design yaliyo wazi ndani yake (EngineError-vs-ABSTAIN; INTENT
migration) — ni **jukumu la Chief**. Implementation ya D6 haianzi hadi Chief apitishe spec.

*Profitable ≠ Tradable Edge. Protect capital first.*

---

## ARCHITECTURE COMPLIANCE REVIEW #4 — `decision_engine.py` — 2026-07-03

Scope: 4-point compliance review (amri ya Chief kwa kila PR ya Engine) + hali baada ya merge ya
mikondo miwili (branch V8/V9/spec + main engine-implementation) na Chief review ya D6.

### 4-Point Compliance Review (mandate mpya ya Chief)

| # | Check | Kipimo | Verdict |
|---|-------|--------|---------|
| 1 | **Engine size** (P103) | File 159 lines; engine core (kabla ya self-tests) ~72 lines; functions 2 (`decide`, `decide_batch`) + validators 2 | **PASS** |
| 2 | **Forbidden imports** (Rule 4) | Imports za engine core: `__future__`, `argparse`, `decision_object` PEKEE; self-test [4] `bad-imports=[]`, `forbidden-words=[]` — nimeiendesha upya leo: PASS | **PASS** |
| 3 | **Stateless compliance** (Rule 5) | Hakuna module-level dict/list/set (self-test [3] `module-mutables=[]`); hakuna cache/singleton; deterministic (id-stable) | **PASS** |
| 4 | **Policy leakage** (Rule 3/P97) | Hakuna threshold/heuristic yoyote ndani ya engine; `decide` = validate → `policy.decide` → `make_decision`; hakuna `if reliability...` popote | **PASS** |

Self-tests zote (decision_object, decision_policy @v2, decision_engine) zimeendeshwa upya kwenye
merged tree leo: **PASS 3/3.**

### Compliance Matrix (dhidi ya doctrine ya repo)

| Principle | Status | Ushahidi |
|-----------|--------|----------|
| P92-V9 (hakuna Market imports) | PASS | import-purity self-test [4] |
| P94-V9 (contract = njia pekee) | PASS | `policy["decide"](snapshot)` pekee; surface 2 (`id`, `decide`) |
| P97-V9 (orchestrator only) | PASS | hakuna decision logic |
| P84/P88 (refs) | PASS | self-test [2] |
| P71/P100 (pure/deterministic) | PASS | self-test [3] |
| RED LINE (reliability ≠ probability) | PASS | engine haisomi `reliability` kabisa (inapita ndani ya `make_decision` kama rekodi) |
| P103 (bounded complexity) | PASS | leo; itapimwa kila PR |
| P104 (continuous compliance tests) | PASS | tests zipo module-ndani; zinaendeshwa kila run |

### Architectural Drift Watch

| Item | Risk |
|------|------|
| Market imports | **None** |
| Policy leakage | **None** |
| Engine growth | **Watch** (P103 — kila PR itapimwa; leo core ~72 lines = baseline) |
| **D-2: Principle-numbering collision** | **Watch — OPEN kwa Chief** (V8/V9 P90–P97 vs spec-text P92–P102; maudhui yanakamilishana, nambari zinagongana; V10 ina pendekezo la reconciliation; engine report inatumia nambari za spec-text) |
| D-3: Spec-text ya Chief (P90–P102) haiko repo | **Watch** (queue item OPEN; compliance checklist ya Rule 2 inahitaji matini kamili) |
| D-4: Specs mbili za D6 kwenye repo | **None (informational)** — `decision_engine_specification.md` (branch, maswali 8) na Rules 1–8 (spec-text ya Chief); engine inatimiza ZOTE mbili kwa maudhui (ContractError≈EngineError; structural validation; stateless; SELECT vocabulary imebaki — INTENT migration bado uamuzi wa Chief) |
| VALIDATED transition (nani?) | **Resolved kama P105 OPEN** — Integrity Gate (E1); Engine na Policy hazifanyi |

### Architectural Maturity

| Layer | Maturity |
|-------|----------|
| Market Science | **Stable** (FROZEN — P62) |
| Evidence Layer | **Frozen** (interface — P90) |
| Decision Objects | **Stable** |
| Decision Policy | **Stable** (@v2; illustrative — si validated economically) |
| Decision Engine | **Stable** (D6 CLOSED 2026-07-03; baseline core ~72 lines) |
| Integrity Gate (E1) | **Not Started** (P105 OPEN) |
| Execution Object (E2) | **Not Started** (P89 OPEN) |
| Decision Repository (E3) | **Not Started** (P106 OPEN) |
| Broker Adapter (E4) | **Not Started** |

### Verdict ya Auditor

**Architecture Review: PASS — Compliant with current doctrine (V10).**

4/4 compliance checks PASS; baseline ya engine size imerekodiwa (core ~72 lines) kwa ajili ya
review za baadaye (P103). Drift pekee inayosubiri uamuzi ni **D-2 (numbering collision)** na **D-3
(spec-text kuwekwa repo)** — zote zimeflagiwa kwa Chief kwenye V10 na board. Approval ya D6
ilikuwa — na inabaki — **ya Chief** (2026-07-03).

*Profitable ≠ Tradable Edge. Protect capital first.*

---

## ADDENDUM ya Review #4 — 2026-07-03 (architecture review ya Chief juu ya V10)

- **P103 imerekebishwa** (kabla haijawa reference ya kudumu): principle sasa inasomeka *"The Decision
  Engine shall remain minimal and bounded in responsibility"* — doctrine **haifungi idadi ya mistari**.
  Kipimo cha core ~72 lines kinabaki HAPA (Architecture Audit) kama **benchmark ya leo tu**;
  implementation inaweza kuboreshwa bila kugusa doctrine ilmradi responsibility haiongezeki.
- **D-2 (numbering collision) — RESOLVED**: numbers ni unique mradi mzima; doctrine = P90–P106
  (V8/V9/V10 as-is); spec-text ya D6 = **Rules 1–8** (specification, si principles). Rekodi za
  kihistoria (engine report yenye labels za zamani) hazibadilishwi — mapping imeelezwa kwenye
  Review #4 hapo juu. D-3 (spec-text kuwekwa repo kama Rules 1–8) inabaki **Watch/OPEN**.
- Reconciliation ya branches + Chapter 3 ordering (Gate→Object→Repository→Adapter): **ENDORSED** na Chief.

*Profitable ≠ Tradable Edge. Protect capital first.*

---

## AUDIT #5 — 2026-07-03 (P107 dependency-graph BASELINE; audit ya kwanza ya Architecture Governor)

Scope: agizo la Chief #1 (V11/P107 — "Auditor aanze kupima dependency graph"). Kipimo cha kwanza cha
**transitive dependency purity** ya Decision domain: imports zote za module-level (direct) kwenye
Decision chain, kisha chain inafuatwa. Hii ni **baseline** — kila audit ijayo italinganisha hapa.

### Dependency Graph (direct module-level imports; Market-domain kwa **bold**)

| Module | Decision-domain imports | Market-domain / heavy imports |
|--------|------------------------|-------------------------------|
| `evidence_object` | — | **market_state_engine · latent_structure · event_library · configuration_engine · context_value · event_taxonomy_engine · contextual_alpha_engine** (+numpy, polars) |
| `evidence_operations` | evidence_object | **market_state_engine · latent_structure · event_library · configuration_engine · context_value** (+numpy, polars) |
| `evidence_set` | evidence_object · evidence_operations | **market_state_engine** (+numpy) |
| `evidence_snapshot` | evidence_object · evidence_operations · evidence_set | **market_state_engine** (+numpy) |
| `decision_object` | evidence_snapshot · evidence_operations · evidence_set | **market_state_engine** (+numpy) |
| `decision_policy` | decision_object + evidence chain | **market_state_engine** (+numpy) |
| `decision_engine` | decision_object | — *(direct: PURE ✅)* |
| `decision_engine_report` *(harness)* | engine + policy + evidence chain | **market_state_engine** *(by design — harness ndiyo inashikilia pipeline, engine inabaki mjinga)* |

### Findings

1. **Engine transitive chain si pure:** `decision_engine → decision_object → market_state_engine`
   (na kupitia evidence chain → latent_structure/event_library/configuration_engine/…). Direct
   purity ✅ (self-test [4]); **transitive purity ❌** — Engine haiwezi ku-load bila Market stack
   nzima (polars). Imethibitishwa kwa vitendo kwenye environment safi (2026-07-03).
2. **Kila module ya Decision chain inaimport `market_state_engine.cfg` module-level** — inaruhusiwa
   kama demo-instantiation (P92 allowance ya W-1), lakini inafunga *loading* ya Decision domain kwa
   Market stack — production isolation haiwezekani hadi hili litatuliwe.
3. Self-test [4] na 4-point review vinapima **direct imports pekee** — regression ya transitive
   purity haitakamatwa na tests za sasa (gap ya P104).

### Remediation options (PENDEKEZO kwa Chief #1 — SIO uamuzi; RED LINE inaheshimiwa)

```text
(a) Kuhamisha demo/build_tagged_evidence dependencies kwenye harness/report modules pekee
(b) Lazy imports (ndani ya __main__/self-test) kwenye evidence/decision modules
(c) Compliance test mpya ya transitive graph (P104+P107) inayoendeshwa kila PR
```

*(a)+(c) pamoja ndiyo pendekezo langu; uamuzi ni wa Chief #1; utekelezaji ni wa Implementer.*

### Compliance Matrix

| Principle | Status |
|-----------|--------|
| P92 (dependency direction; demo-allowance kwa research modules) | ✅ Compliant |
| P97/P103 (engine orchestrator/bounded) | ✅ PASS |
| P104 (automated compliance tests) | ⚠️ Direct-only — transitive check haipo bado |
| **P107 (transitive dependency purity)** | ❌ **Baseline FAIL** (Engine chain inavuja Market stack) — inayojulikana; ndiyo chanzo cha principle yenyewe; remediation inasubiri Chief #1 |

### Architectural Drift Watch

| Item | Risk |
|------|------|
| Transitive Market leak (P107) | Engine inashindwa ku-load bila polars/Market stack; production/E-series isolation imefungwa hadi remediation |
| Compliance tests direct-only | Regression ya transitive purity haitakamatwa na self-test [4] |
| Governance transition (Auditor → Chief #2) | Watch — vocabulary na mipaka ya Auditor lazima zibaki zilezile ndani ya role mpya |

### Verdict

**Architecture Review: PASS — hakuna drift MPYA; P107 baseline imerekodiwa kama FAIL inayojulikana**
(iliyorekodiwa doctrine — V11; remediation ni uamuzi wa Chief #1, utekelezaji wa Implementer).

*Profitable ≠ Tradable Edge. Protect capital first.*
