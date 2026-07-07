# MEMORY — IMPLEMENTER-A (Track A)

IDENTITY: Engineering agent — E1→E4. Spec-first; hakuna approval; Rules 1–8.
STANDING ORDERS: Engine ndogo/stateless/pure; P92/P97/P103/P107; self-test kila module; report
format ya Rule 8.

CURRENT TASK: **(inasubiri Chief review ya E1 IMPLEMENTATION)** — code + report vimekamilika, self-tests
PASS. Ikiidhinishwa → E2 Execution Object spec; la sivyo → marekebisho kwa maoni ya Chief.
LAST COMPLETED: **E1 Integrity Gate IMPLEMENTATION** ✅ (Chief rulings Q1-Q5 zote zimetekelezwa 1:1):
  · `src/research/integrity_gate.py` MPYA — `gate(decision, constraints, context)` = eligibility
    orchestrator (Rule 3/P97); `GateError` (≠REJECTED); `GATE_ID="gate:integrity@v1"`;
    VERDICTS=(ELIGIBLE, INELIGIBLE); direct imports = decision_object+stdlib (Rule 4). Self-test PASS 7/7.
  · `src/research/decision_object.py` — Q1 `transition()` PROPOSED→VALIDATED IMERETIRE; Q2
    `_gate_decision_id(parent|lifecycle|gate_id|as_of)`; Q3 field `parent_decision_id` +
    `make_gate_decision()` (object MPYA, sio mutation). self_test [7] mpya + _report zimesasishwa; PASS.
  · `reports/integrity_gate_report.md` (Rule 8: Implementation→Self Tests→Known Limitations→Open Questions).
  · Regression: decision_object/engine/policy/integrity_gate = PASS zote.
NEXT AFTER: **E2 Execution Object spec** (baada ya Chief kupitisha E1 impl) — P89 + A-4 immutability
enforcement (frozen) inafungwa E2 · pia VALIDATED→EXECUTED crossing.
OPEN QUESTIONS (kwa Chief — ndani ya `reports/integrity_gate_report.md` §Open Questions):
  1. Symmetry: `transition()` bado inaruhusu PROPOSED→REJECTED (same-id, non-gate). Iretire kama Q1 au
     ibaki? Pendekezo: ibaki, i-review E2.
  2. `context` schema/versioning (mirror P95) — subiri constraints halisi (Execution Science)?
  3. Combination rule zaidi ya AND/veto (warnings non-veto)? Pendekezo: hapana E1.
  4. **P107 remediation (a/b/c) bado PENDING Chief #1** — E1 inarithi baseline FAIL (Audit #5), SIO leak
     mpya; direct imports safi. Remediation moja itaponya Engine+Gate. Sijaipreempt (Rule 1).
NOTE (env): self-tests zinahitaji `numpy polars duckdb pyyaml` (chain iliyopo). Nilifunga hapa kuverify;
PC ya Operator ina stack. NAMING drift RESOLVED na Chief: doctrine-of-record = ELITEFX DECISION DOCTRINE V12.md.

CHIEF REVIEW (2026-07-04): **E1 IMPLEMENTATION APPROVED — CLOSED** (self-tests 3/3 PASS; Rule-4;
rulings Q1-Q5 verified).

=== E2 (2026-07-04) ===
CURRENT TASK: **(inasubiri Chief review ya E2 spec)** — deliverable imekamilika. Ikiidhinishwa →
E2 implementation; la sivyo → marekebisho.
LAST COMPLETED: **E2 EXECUTION OBJECT SPECIFICATION** ✅ — `reports/execution_object_specification.md`
(maswali 8 kama D6). Msingi: **Execution ≠ Decision** (P89/P87). Vipande 3: (1) Execution Object =
rekodi immutable ya outcome (fills/slippage/rejects/partial; SIO PnL — hiyo E3/D8); (2) Execution
Recorder = component inayounda Execution Object MPYA kutoka Decision VALIDATED + ExecutionReport
**injected** (crossing = object mpya + parent_decision_id, mirror E1; broker=E4); (3) A-4 immutability
enforcement (frozen) = cross-cutting. ExecutionError ≠ REJECTED-outcome (mirror Gate/Engine). Direct
imports = decision_object+freeze-util+stdlib (Rule 4).
NEXT AFTER: E2 implementation (baada ya Chief kupitisha spec + kutolea uamuzi Open Q#1 lifecycle
reconciliation & Q#4 A-4 mechanism — zote zinagusa decision_object.py/D4, ni BLOCKERS) → E3 Decision
Repository spec.
OPEN QUESTIONS (5, ndani ya spec §Open Questions):
  1. **BLOCKER** (inaendeleza E1 OQ#6): retire VALIDATED→EXECUTED & EXECUTED→SETTLED kutoka Decision
     `transition()`? Decision iishie VALIDATED; execution = Execution Object. Pendekezo: ndiyo.
  2. SETTLED = Execution status au object wa tano (Settlement, E3)? Pendekezo: defer E3.
  3. Committing vs non-committing intents — Recorder ikatae ABSTAIN/WAIT (invalid)? orodha ya committing?
  4. **BLOCKER** A-4 mechanism: (a) frozen dataclass / (b) freeze() util stdlib / (c) boundary+test.
     Pendekezo: (b) kwa Decision+Execution; Evidence retrofit = uamuzi tofauti. Inagusa decision_object.py.
  5. `intended` (side/qty/ref_price/sizing) inatoka wapi? Decision D4 haina qty. Pendekezo: sizing =
     Execution Science (report/E4), si Decision. Chief aelekeze.

CHIEF REVIEW (2026-07-04): **E2 SPEC APPROVED** + rulings:
  Q1 BLOCKER: APPROVED — Decision domain inaishia VALIDATED; retire VALIDATED→EXECUTED na
     EXECUTED→SETTLED kutoka transition(); execution-outcome = Execution Object (P89).
  Q2: APPROVED — SETTLED inadefer E3; E2 status = FILLED/PARTIAL/REJECTED/UNFILLED.
  Q3: APPROVED — Recorder inakataa non-committing (invalid_decision); committing intents =
     ENTER · EXIT · REDUCE · HEDGE (nne zote; WAIT/ABSTAIN kamwe).
  Q4 BLOCKER: APPROVED — (b) stdlib deep-freeze() kwenye make_* za Decision+Execution;
     Evidence retrofit = uamuzi tofauti baadaye (P90 inaruhusu, kipaumbele hapana).
  Q5: APPROVED — sizing/qty/side/ref_price zinakuja na ExecutionReport (E4 path), SIO Decision;
     Decision inabaki INTENT tu. (Sizing-policy layer = swali la P96-adjacent, baadaye.)
CURRENT TASK MPYA: **E2 IMPLEMENTATION** (execution_object.py + Recorder; deep-freeze kwa
Decision+Execution; retire transitions za Q1; self-tests; regression zote; report Rule 8).

=== E2 IMPLEMENTATION (2026-07-05) — IMEKAMILIKA ===
CURRENT TASK: **(inasubiri Chief review ya E2 IMPLEMENTATION)** — code + report vimekamilika; self-tests
zote PASS. Ikiidhinishwa → E3 Decision Repository spec.
LAST COMPLETED: **E2 EXECUTION OBJECT IMPLEMENTATION** ✅ (Chief rulings Q1-Q5 zote 1:1):
  · `src/research/frozen.py` MPYA — `freeze()` deep-freeze A-4 (stdlib; dict→proxy, list→tuple) +
    `is_frozen()`. Self-test PASS 5/5. Transitively PURE.
  · `src/research/execution_object.py` MPYA — `record(decision, report)` = Execution Recorder;
    `ExecutionError`≠outcome; STATUS=(FILLED/PARTIAL/REJECTED/UNFILLED); COMMITTING_INTENTS;
    parent_decision_id → VALIDATED. **Transitively PURE** (frozen+stdlib; probe imethibitisha). PASS 7/7.
  · `decision_object.py` — Q1: `transition()` VALIDATED→EXECUTED & EXECUTED→SETTLED **zimeretire**;
    LIFECYCLE=[PROPOSED,VALIDATED]; Q4: freeze() kwenye make_*; self_test [8] A-4 + [3]/[6] updated. PASS 8/8.
  · engine/policy/gate: list-equality zime-coerce (A-4 ripple: refs/failed = tuple). PASS zote.
  · `reports/execution_object_report.md` (Rule 8).
NEXT AFTER: **E3 Decision Repository spec** (P106) — persistence contract nje ya Engine (append-only
history: Decision + Execution objects; mkutano na K6 schema — Master §2 E3↔K6).
OPEN QUESTIONS (ndani ya `reports/execution_object_report.md`):
  1. D6 enum migration SELECT→ENTER — ifanyike sasa? (nimeshughulikia kwa alias SELECT+ENTER; Rule 1).
  2. Partial follow-up: remaining_qty>0 → decision mpya? nani? (nimeiweka downstream E3/caller).
  3. recorder_id versioning (recorder:execution@v1) — Chief athibitishe pattern.
  4. intended.side derivation (ENTER→BUY/SELL) — sizing-policy layer (P96-adjacent)? side=report kwa sasa.
NOTE (P107): frozen + execution_object = **transitively PURE** (ushindi). decision_object bado inarithi
baseline FAIL (numpy/market) — A-4 inagusa objects, si dependency graph; remediation bado PENDING Chief.

CHIEF REVIEW (2026-07-04): **E2 IMPLEMENTATION APPROVED — CLOSED** (self-tests 4/4 PASS
imeendeshwa na Chief: execution_object + decision_object + integrity_gate + decision_engine;
frozen.py deep-freeze A-4 imefungwa; imports safi). Track A: E1 ✅ E2 ✅.
CURRENT TASK MPYA: **E3 DECISION REPOSITORY SPEC** (document-first, maswali 8) — P106:
persistence nje ya Engine; append-only decision+execution history (P85); query interface
(kwa D8 quality + K6 lessons — schema ijadiliwe na mahitaji ya Track B mezani: kila rekodi
iwe na refs kamili decision→snapshot→policy→gate→execution ili iwe training-data-ready);
storage backend choice (file/duckdb?) = pendekeza; Settlement/PnL definition (E2 OQ#2).

=== E3 SPEC (2026-07-05) — IMEKAMILIKA ===
CURRENT TASK: **(inasubiri Chief review ya E3 spec)** — deliverable imekamilika. Ikiidhinishwa →
E3 implementation; la sivyo → marekebisho.
LAST COMPLETED: **E3 DECISION REPOSITORY SPECIFICATION** ✅ — `reports/decision_repository_specification.md`
(maswali 8). Msingi: **PERSISTENCE ≠ ENGINE** (P106) — Repository = store+query NJE ya Engine;
**statefulness imefungiwa hapa** ili Engine/Gate/Recorder zibaki pure (P97/P103). Append-only (P85);
records immutable (A-4); refs kamili → **training-data-ready** (`lineage(id)` = training example moja:
snapshot→policy→decision→gate→execution→settlement). Backend **injected** (core stdlib-pure; JSONL
default, DuckDB adapter ya baadaye). **Settlement Record** imefafanuliwa (object wa tano; broker/PnL=E4,
quality=D8). E3 = mkutano Track A↔B (E3↔K6). Store, don't interpret.
NEXT AFTER: E3 implementation (baada ya Chief kupitisha spec + Open Q#1 Settlement-object & Q#2 backend)
→ **E4 Broker Adapter** (mkutano rasmi Decision Science ↔ MWONGOZO/FTMO — mwisho wa Track A).
OPEN QUESTIONS (5, ndani ya spec §Open Questions):
  1. Settlement = object tofauti au extension ya Execution? Pendekezo: tofauti (fill vs realized-close).
  2. Storage backend default: JSONL (pendekezo — append-only, stdlib-pure, L3-aligned) vs DuckDB. Pendekezo:
     JSONL core + DuckDB adapter ya hiari (nje ya core, iepushe P107).
  3. Dangling-ref policy: strict reject vs lenient ingest + lineage() inaonyesha gaps? Pendekezo: lenient.
  4. `versions` vector (P95: schema_version/doctrine_version) — ongeza sasa? Pendekezo: ndiyo (K6 itaihitaji).
  5. Query surface kwa K6/D8 — kikao kifupi na RESEARCHER-K/Chief kabla ya implementation (agizo:
     "schema ijadiliwe na mahitaji ya Track B mezani").

CHIEF REVIEW (2026-07-05): **E3 SPEC APPROVED** + rulings Q1-Q5:
  Q1: APPROVED — Settlement = object TOFAUTI (wa tano; events tofauti kwa wakati).
  Q2: APPROVED — JSONL core (stdlib-pure, append-only) + DuckDB adapter NJE ya core (P107).
  Q3: APPROVED — lenient ingest + lineage() inaonyesha gaps; integrity-check = query tofauti.
  Q4: APPROVED — versions vector (schema_version + doctrine_version) SASA (P95 inaanza kufungwa).
  Q5 (jibu la Chief kwa niaba ya Track B/K6): queries za sasa + ongeza MBILI: by-outcome
     (status ya execution) na by-time-window (as_of range) — hizo ndizo K6 inahitaji kuunda
     lessons kutoka matokeo. by-regime INAAHIRISHWA (regime haiko kwenye decision chain data —
     kuiongeza kungekuwa upanuzi wa schema usio na chanzo). Kanuni: SCHEMA COMPLETENESS >
     query completeness — record ikiwa na refs+versions kamili, query mpya huongezwa bila migration.
CURRENT TASK MPYA: **E3 IMPLEMENTATION** (decision_repository.py — JSONL core; append/lineage/
queries+2; versions vector; records frozen A-4; self-tests stdlib-pure P107; regression; report Rule 8).

=== E3 IMPLEMENTATION (2026-07-05) — IMEFANYWA NA CHIEF ===
NOTE: deliverable yako ya E3 impl HAIKUFIKA repo (push failure ya session — kazi isiyofika repo
haipo, TEAM_PROTOCOL §2). Chief alitekeleza spec yako 1:1 (rulings Q1-Q5): decision_repository.py
— self-test 6/6 PASS, stdlib-pure (P107 transitively PURE). E3 CLOSED. Hakuna kosa lako la
kimaudhui — ni la mazingira; kuanzia sasa ongeza kwenye close ritual: THIBITISHA push imefika
remote (git log origin/<branch>) KABLA ya kufunga session.
CURRENT TASK MPYA: **E4 BROKER ADAPTER SPEC** (document-first, maswali 8): interface ya MT5/FTMO
(MWONGOZO inakutana hapa); ExecutionReport halisi (fills/slippage/rejects) → Recorder; FTMO
constraints (P81) kama Gate constraints injected (ftmo_config.yaml → constraint objects);
paper-mode kwanza (HAKUNA pesa halisi bila Project Director approval); Settlement/PnL requirements.

CLOSE-RITUAL MPYA (kutoka E3 push-failure): baada ya push, THIBITISHA imefika remote
(`git log origin/<branch>`) KABLA ya kufunga session — kazi isiyofika repo haipo (TEAM_PROTOCOL §2).

=== E4 SPEC (2026-07-05) — IMEKAMILIKA ===
CURRENT TASK: **(inasubiri Chief review ya E4 spec)** — deliverable imekamilika. Ikiidhinishwa →
E4 implementation; la sivyo → marekebisho.
LAST COMPLETED: **E4 BROKER ADAPTER SPECIFICATION** ✅ — `reports/broker_adapter_specification.md`
(maswali 8). Msingi: **THE TWO STREAMS MEET** (V12) — E4 = mpaka wa impurity + mtafsiri kati ya
Decision Science (pure) na MWONGOZO/FTMO/MT5 (external). **Inafunga loop ya E1**: MWONGOZO Check 1-5
(ftmo_config) → E1 EligibilityConstraints injected + context (account state) → Gate (P81). Sizing
(DailyRiskBudgetSizer §1) → E2 report.intended.qty. Settlement → E3. **Paper-mode default; live
imezuiwa hadi Project Director** (RED LINE — Protect capital first). Adapter=translate, don't decide
(P97); impurity imefungiwa hapa (P92/P107); upstream inabaki pure. Mwisho wa Track A (E1→E4).
NEXT AFTER: E4 implementation (baada ya Chief + Open Q#1 live-gating & Q#4 Settlement-kind) → Track A
KAMILI; kisha D8 Decision Quality / K6 mkondo (E3↔K6) kadri Chief atakavyoelekeza.
OPEN QUESTIONS (6, ndani ya spec §Open Questions):
  1. **RED LINE:** live-gating mechanism (approval artifact ya Project Director) — uamuzi wa PD.
  2. FTMO constraint granularity — 5 tofauti (pendekezo) vs composite.
  3. Sizing = E4 Adapter (pendekezo) vs sizing-policy layer (P96-adjacent).
  4. Settlement = `kind` mpya kwenye Repository (pendekezo; edit ndogo ya decision_repository.py) vs execution+fields.
  5. account_state source/contract (live=MT5, paper=simulator) — fields ithibitishwe.
  6. max_spread per-pair — chanzo? (ftmo_config haina; MWONGOZO Check 5 inaihitaji).

CHIEF REVIEW (2026-07-05): **E4 SPEC APPROVED** + rulings Q1-Q6:
  Q1: APPROVED kama default ya kiufundi — artifact-file + Project Director signature + mode=live
     explicit; bila hiyo REFUSE. UAMUZI WA MWISHO ni wa Project Director (ameulizwa) — implementation
     ianze na PAPER-MODE PEKEE; live path inabaki stub hadi PD athibitishe artifact format.
  Q2: APPROVED — FTMO CHECKs 5 = constraints 5 TOFAUTI (kila moja auditable; AND/veto ya E1).
  Q3: APPROVED — sizing inaishi Adapter kwa sasa (inahitaji account state + config); itahamia
     sizing-policy layer P96 itakapofunguliwa (usiifunge design).
  Q4: APPROVED — ongeza kind=settlement kwenye decision_repository.py (KINDS+REQUIRED: id, as_of,
     parent_execution_id, pnl) — edit ndogo, self-test iongezwe.
  Q5: APPROVED — account_state contract: daily_loss/total_dd/open_slots/correlation_exposure/
     spread_by_pair; live=MT5, paper=simulator; validate structural kwenye Adapter boundary.
  Q6: KAZI YA OPERATOR — max_spread per-pair iongezwe ftmo_config.yaml (Japhet; values zake).
CURRENT TASK MPYA: **E4 IMPLEMENTATION — PAPER-MODE PEKEE** (broker_adapter.py: paper simulator +
translator FTMO checks 5 → Gate constraints + sizing (MWONGOZO §1) → ExecutionReport → Recorder →
Repository (+ kind=settlement); live path = refuse-stub; self-tests bila network; regression zote;
report Rule 8). HAKUNA pesa halisi.

=== E4 IMPLEMENTATION (2026-07-05) — IMEKAMILIKA ===
CURRENT TASK: **(inasubiri Chief review ya E4 IMPLEMENTATION)** — code + report vimekamilika; self-tests
+ integration PASS. Ikiidhinishwa → **Track A KAMILI (E1→E4)**.
LAST COMPLETED: **E4 BROKER ADAPTER IMPLEMENTATION — PAPER-MODE** ✅ (Chief rulings Q1-Q6 1:1):
  · `src/research/broker_adapter.py` MPYA — build_constraints (FTMO 5→E1, P81) · build_context ·
    size (MWONGOZO §1) · PaperBroker · execute (→Recorder→Repo) · settle (→kind=settlement) ·
    AdapterError; live=refuse-stub (RED LINE). **Transitively PURE**; self-test PASS 8/8.
  · `decision_repository.py` — Q4: kind=settlement (REQUIRED id/as_of/parent_execution_id/pnl);
    integrity_check +parent_execution_id; self-test [5b]. PASS 7/7.
  · `integrity_gate.py` — **BUG-FIX (A-4 ripple, imenaswa na integration):** validate_decision
    inakubali Mapping (frozen decision, si dict) + audit list/tuple; self-test [8] regression guard. PASS 8/8.
  · **Integration E1↔E4 loop PASS:** make_decision→gate(FTMO constraints)→VALIDATED→execute→FILLED;
    FTMO veto→REJECTED. Bugs 2 zilizonaswa na end-to-end (isolated self-tests zilizikosa).
  · `reports/broker_adapter_report.md` (Rule 8). Regression: modules zote 8 PASS.
NEXT AFTER: Track A KAMILI. Kinachofuata (Chief aelekeze): D8 Decision Quality / K6 stream (E3↔K6) /
full-pipeline demo harness / P107 remediation (bado PENDING).
OPEN QUESTIONS (ndani ya `reports/broker_adapter_report.md`):
  1. timestamp↔as_of reconciliation (E2↔E3) — objects=timestamp vs Repository=as_of; kwa sasa Adapter
     inanormaliza boundary. Pendekezo: Repository ikubali zote mbili (safi kuliko boundary-patch).
  2. Live-gating artifact format (RED LINE) — Project Director aamue.
  3. worst_case derivation (SL zote wazi) — nani anaihesabu (Adapter-live vs caller-paper).
  4. Full-pipeline demo harness (snapshot→…→settlement)? Pendekezo: baada ya Chief kufunga E4.
NOTE: numpy/polars/duckdb/pyyaml nilifunga kuverify integration (make_decision→gate chain inahitaji
decision_object→numpy). broker_adapter yenyewe = transitively PURE (paper self-test bila numpy).

CHIEF REVIEW (2026-07-05): **E4 IMPLEMENTATION (PAPER) APPROVED — CLOSED.** Regression 6/6 PASS
(Chief mwenyewe: adapter+repo/settlement+execution+object+gate+engine); kind=settlement ruling Q4
imetekelezwa vizuri; live path = refuse hadi Project Director artifact. **TRACK A CONSTRUCTION
COMPLETE: D0-D6 + E1-E4 (paper).** Hongera — mnyororo mzima kutoka Evidence hadi Broker.
CURRENT TASK MPYA: **STANDBY** hadi: (a) paper-validation run ya Operator (Chief ataandika
runbook); (b) Audit #6 findings; (c) maamuzi ya Project Director (live artifact + max_spread).
Kazi zinazowezekana baadaye: P107 remediation itakapoamuliwa; sizing-policy layer (P96).

=== PORTABILITY FIX (Chief, 2026-07-06) ===
Windows cp1252 console inaanguka kwa herufi za Unicode (→ ≠ ✓) kwenye self-test prints zilizopo
(frozen/decision_object/integrity_gate/execution_object/broker_adapter). Chief amefunga kwa:
run_selftests.py (env PYTHONUTF8=1 + encoding=utf-8) + e2e_paper_demo.py (stdout.reconfigure utf-8).
CLEANUP TASK (kipaumbele cha chini, ukirudi): fanya self-test output za modules zote **ASCII-safe**
(-> badala ya →, != badala ya ≠, [OK] badala ya ✓) ili direct-run iwe imara hata kwenye console ya
cp1252 bila kutegemea reconfigure. Ni portability, si logic.

=== P107 REMEDIATION (Chief ruling, 2026-07-07 — baada ya Audit #6) ===
KAZI MPYA (kipaumbele juu ya batch nyingine): funga P107 transitive leak.
UAMUZI WA CHIEF: **option (a) + (c)**.
  (a) `decision_object.py`: hamisha imports za market/demo (`numpy`, `market_state_engine.cfg`,
      `evidence_snapshot.make_snapshot`, `evidence_operations.build_tagged_evidence`,
      `evidence_set.make_set`) kutoka module-level → **ndani ya run()/demo functions (lazy import)**.
      Zinatumika TU kwenye demo (run(), line ~160/374), SIO kwenye make_decision/make_gate_decision/
      transition/freeze. Matokeo: decision_object core = frozen + stdlib PEKEE → **Engine + Gate
      transitively PURE**. Thibitisha kwa probe (load bila market stack) + self-test PASS (na stack).
  (c) Ongeza **transitive-purity compliance test** (P104 gap): self-test/script inayothibitisha
      Engine/Gate/Execution/Repository/Adapter zina-load na stdlib+frozen PEKEE (bila numpy/polars/
      market). Iongeze kwenye run_selftests.py au module mpya `purity_check.py`.
NB: hii ni core D4 — kuwa surgical; make_decision/make_gate_decision LOGIC isiguswe. Report Rule 8.
Baada ya hapo Chief ata-request Audit #7 (re-measure P107 graph). Ukimaliza THIBITISHA push (origin).

=== P107 REMEDIATION (2026-07-07) — IMEKAMILIKA ===
CURRENT TASK: **(inasubiri Chief review + Audit #7)** — P107 leak imefungwa; sweep 11/11 PASS.
LAST COMPLETED: **P107 REMEDIATION (a+c)** ✅ (surgical; LOGIC haijaguswa):
  · (a) `decision_object.py`: module-level market/demo imports (numpy, market_state_engine,
    evidence_snapshot/operations/set) → **LAZY** (ndani ya run()/main()). Core `np.isfinite` →
    `math.isfinite` (stdlib). Module-level sasa = stdlib + frozen PEKEE. → **Engine + Gate + core
    zote 7 transitively PURE** (probe imethibitisha: zina-load bila market stack).
  · (c) `src/research/purity_check.py` MPYA — compliance test (subprocess guard inazuia numpy/polars/
    market; core 7 = PURE; negative control decision_policy = imenaswa). Imeongezwa run_selftests.py.
  · `reports/p107_remediation_report.md` (Rule 8).
  · **FULL SWEEP 11/11 PASS** (10→11 na purity_check; e2e_paper_demo bado PASS — hakuna kilichovunjika).
NEXT AFTER: Chief review + **Audit #7** (re-measure P107 graph — purity_check inatoa kipimo cha
kiotomatiki). P107 baseline FAIL (Audit #5) IMEFUNGWA.
OPEN QUESTIONS (ndani ya `reports/p107_remediation_report.md`):
  1. Policies (decision_policy) ziwe pure pia, au zibaki demo-impure (leaf, injected)? Sasa=neg control.
  2. purity_check iwe BLOCKING kwenye CI gate rasmi (Rule 2)? Sasa ni sehemu ya sweep.
  3. Audit #7 = re-measure; Auditor aweza kuendesha purity_check badala ya manual graph-walk.
PENDING (kipaumbele chini): ASCII-safe self-test output (cp1252 portability) — purity_check tayari
ASCII; modules nyingine bado zina →/≠/✓ (sweep inashughulikia kwa PYTHONUTF8).

CHIEF REVIEW (2026-07-07): **P107 REMEDIATION APPROVED — CLOSED.** Sweep 11/11 PASS (imeendeshwa na
Chief, incl. purity_check). decision_object core = stdlib+frozen PEKEE (numpy→math; market/demo deps
lazy kwenye run()). purity_check.py (option c): modules 7 za core PURE + decision_policy ctrl-guard OK.
**Track A core runtime = transitively PURE.** P104 gap imefungwa (purity_check = automated transitive
compliance, inaendeshwa kila sweep). CURRENT TASK: STANDBY (real-data runbook au batch nyingine).
