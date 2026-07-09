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

=== PAPER-TRADER (Chief spec-light, 2026-07-07 — directive ya Project Director) ===
CURRENT TASK: **paper_trader.py** — FORWARD paper-trading CLI (mkutano wa MWONGOZO na mashine).
Protocol: docs/RUNBOOK_forward_paper_trading.md. Mahitaji:
  1. `--signal PAIR SIDE ENTRY SL TP [--policy conservative]`: jenga decision (signal ya Operator =
     manual intent; snapshot nyepesi ya signal — readiness READY, provenance="operator-signal") →
     gate (FTMO constraints 5 kutoka config/ftmo_config.yaml + account state HALISI ya paper) →
     size (MWONGOZO §1: sl_pips kutoka ENTRY/SL; pip_value kwa pair) → paper-fill @ ENTRY →
     rekodi decision+execution kwenye data/paper/paper_log.jsonl (persistent, append-only, versions).
  2. `--close ORDER_ID --price P`: settlement (PnL halisi ya paper kwa qty×pips) + update account
     state (daily_loss/budget/slots — MWONGOZO HATUA 1: bajeti inashuka kwa loss_factor, inakua
     kwa win_factor) + rekodi kind=settlement.
  3. `--status`: account state ya sasa (bajeti iliyobaki, slots wazi, daily loss, positions wazi).
  4. Account state persistence: data/paper/account_state.json (reset ya siku = --new-day au auto
     kwa date change). correlation_exposure kutoka positions wazi (correlation_groups za config).
  5. Reuse core zilizopo (gate/execute/settle/repo) — USIJENGE mpya; hii ni CLI wrapper + state.
  6. Self-tests bila network; Windows-safe output (ASCII/UTF8 reconfigure); report Rule 8.
NB: pip_value kwa pair — tumia mapping rahisi ya MWONGOZO (quote USD=$10/lot... kwa qty units
tumia scale ya adapter iliyopo); weka wazi kwenye Known Limitations kama approximation.

=== ALPHA ENGINEERING S1: STRATEGY FACTORY (Chief, 2026-07-08 — directive ya Project Director) ===
KIPAUMBELE CHA JUU KULIKO ZOTE. Jenga `src/research/strategy_lab.py`:
  1. GRID: events 9 za Event Library.md (Davey — rules kamili zimo) × pairs 9 × TF (H1/H4) ×
     SL/TP params (mf. SL=ATR×{1,1.5,2}, TP=R×{1,1.5,2,3}) × filters za hiari (vol/activity state
     kutoka states zilizopo) → candidates (~elfu kadhaa).
  2. BACKTEST ENGINE (vectorized, polars): entries kwa rules za Davey verbatim ("next bar" honest);
     COSTS = spread halisi ya pair (median kutoka states) + slippage ndogo; NO LOOKAHEAD (kila
     signal inatumia bars zilizofungwa tu).
  3. SPLITS TAKATIFU: TRAIN 2016-2022 (search) · VALIDATION 2023-2024 (walk-forward) ·
     HOLDOUT 2025+ HAIGUSWI (S3 pekee, mara moja — enforce kwa code: refuse kusoma > 2024-12-31
     bila flag --holdout-final iliyo na Chief token).
  4. METRICS kwa kila candidate: trades N, EV net/trade, win%, PF, maxDD, trades/siku (availability),
     walk-forward consistency. RANK kwa population view (LESSON-033/034 — si top-EV pekee).
  5. FDR: BH correction juu ya validation results; ripoti survivors WAZI na wangapi wangetokea
     kwa bahati (null baseline).
  6. OUTPUT: reports/strategy_lab_report.md (survivors + metrics + registration list ya S3) +
     data/strategies/candidates.jsonl. Self-test na data synthetic ndogo (bila data halisi).
  RED LINES: hakuna kuchagua kwa holdout; hakuna metric bila costs; survivors = CANDIDATES hadi S3.
PIA (kazi ndogo ya kwanza, kabla ya S1): OOS-CONFIRM runbook ya LESSON-017/018 (MR×EURUSD,
DPB×EURUSD) — pre-registered test juu ya 2023-2024 validation window (SIO holdout) na FDR ya 2;
hii inaweza kutupa strategy halisi ya kwanza NDANI YA WIKI.

=== UPDATE ya S1 (Chief direct, 2026-07-08): EVENT LIBRARY V2 NDIYO MSINGI WA GRID ===
Chief amejenga mwenyewe `src/research/event_library_v2.py` (entries 11: edge-trigger+rearm,
stop-entries za intrabar [jump_off/breakout_stop/session_orb], volume filter [lowvol_reversal],
ATR-stretch MR [mr_zscore], resumption pullback [trend_resume]) + `event_quality_report.py`
(harness: episode non-overlap, next-bar honest, SL/TP za ATR, tie->SL, costs kila trade,
TRAIN<2023 enforced). Sweep 14/14 PASS. MABADILIKO KWA S1 SPEC YAKO:
  a. GRID ya strategy_lab.py itumie **EVENTS_V2 registry** (sio Event Library.md pekee) —
     mkataba: market events -> {"sig"}; stop events -> {"long_level","short_level"}; params
     za kila fn = dimensions za grid (short_len/long_len/k/rearm/q/range_hours n.k.).
  b. TUMIA `episodes()` ya event_quality_report.py kama reference semantics ya fills/exits —
     USIBADILISHE fill rules (next-bar open / stop touch / tie->SL worst case).
  c. Ripoti ya `event_quality_report.md` (Operator ataiendesha) = pruning ya kwanza ya grid:
     event x pair x session zenye EV net chanya TRAIN zinapata kipaumbele; ZOTE bado zinapimwa S2.

=== UPDATE 2 ya S1 (Chief direct, 2026-07-09 — maswali ya PD): ENTRIES 16 + CONTEXT LAYER ===
PD aliuliza (1) kwa nini 9->11 na akaagiza mbinu zaidi; (2) uchambuzi wa soko kabla ya entry.
Chief ameongeza: entries 5 MPYA (rsi2_pullback, bb_fade, engulf_extreme, inside_break, nr7_break)
-> EVENTS_V2 sasa = 16 katika familia 7. Harness sasa inapima kila entry x VOLATILITY STATE
(by_vol; jedwali la 4 la ripoti) + session (jedwali la 3). KWA S1 GRID YAKO: dimension ya
context filter = {none, vol_state, session, vol_state x session} — hii ndiyo safu ya uchambuzi
inayolishwa modeli baadaye (K4: P(outcome | context, event, params)). Sweep 14/14 PASS.

=== S1 GRID RULING (Chief, 2026-07-09 — baada ya S0 event_quality run ya Operator) ===
Evidence: reports/event_quality_report.md (TRAIN 2016-2022, H1, ~500k episodes). RULING ya grid:
  TIER-1 (kipaumbele cha compute + pre-registration ya S2):
    * nr7_break — pairs ZOTE; filters: session {ALL, no-LATE, LONDON+NY} × vol {ALL, HIGH};
      TP sweep muhimu (compression inaweza kulipa zaidi kwa 2-3R).
    * second_chance — EURJPY/USDCHF/EURUSD; filters {ALL, LATE, LOW}.
    * shock_follow — EURJPY/USDJPY; filters {ALL, ASIA, NORMAL}.
    * session_orb — USDJPY (+EURUSD/GBPUSD kwa kulinganisha); vol {ALL, HIGH}.
    * inside_break — USDJPY; session {ALL, LONDON} × vol {ALL, HIGH}.
    * rsi2_pullback — EURUSD/USDJPY (karibu-flat, TP/SL sweep inaweza kuifungua).
  TIER-2 (endesha kwa ukamilifu, compute ikiruhusu): mr_zscore, lowvol_reversal, trend_resume,
    big_range_mo, pullback_v2, pattern_3lows, bb_fade, engulf_extreme.
  STOP-BREAKOUTS (jump_off, breakout_stop): usiwaue bado — TRAIN inaonyesha −4.5/−2.8 kwa
    SL/TP 1.5/1.5; jaribu TP {2,3}R + session filters; wakibaki negative kila param → ripoti
    na tutawa-archive kwa evidence.
  KUMBUKA: hizi ni TRAIN in-sample; S1 inatoa candidates → S2 walk-forward 2023-24 + BH-FDR
  (cells zote zilizojaribiwa zinahesabika kwenye correction!) → S3 holdout mara moja.

=== S1 STRATEGY LAB (2026-07-09) — IMEKAMILIKA ===
CURRENT TASK: **(inasubiri Chief review ya S1)** — strategy_lab.py + report; sweep 15/15 PASS.
LAST COMPLETED: **S1 STRATEGY FACTORY** ✅ (`src/research/strategy_lab.py`; directive + GRID RULING):
  · GRID(pairs): TIER-1 pre-registered (nr7_break/second_chance/shock_follow/session_orb/inside_break/
    rsi2_pullback + pairs/session/vol filters halisi za RULING) + TIER-2 (8) + STOP-BREAKOUTS (TP{2,3}R);
    SL{1,1.5,2}xTP{1,1.5,2,3}. (~1284 cells kwa synthetic pairs 5.)
  · BACKTEST: `evaluate()` inatumia `episodes()` ya event_quality_report — SIBADILISHI fill rules
    (next-bar honest, tie->SL, costs kila trade). Context filter (session/vol) kwa slicing trades.
  · SACRED SPLITS enforced: `load_window(split, token)` — HOLDOUT>=2025 inarefuse (PermissionError)
    bila HOLDOUT_TOKEN sahihi KABLA ya kusoma (RED LINE). TRAIN<2023 / VALID 2023-24.
  · METRICS: N/EV-net/win/PF/maxDD/trades-per-day; RANK=population view (LESSON-033/034).
  · FDR (S2): pvalue_gt0 (erfc normal-approx) + bh_fdr (BH; m=cells zote; null baseline). apply_fdr
    kwa validation/holdout pekee (out-of-sample).
  · OUTPUT: data/strategies/candidates.jsonl (bila raw pnls) + reports/strategy_lab_report.md.
  · Self-test 7 checks PASS (synthetic, temp dir — hakuna artifacts repo). SWEEP 15/15 PASS.
  · Rule 8: reports/strategy_lab_implementation.md.
NEXT AFTER: Operator aendeshe TRAIN (candidates) -> S2 (`--split validation`: walk-forward+BH-FDR) ->
S3 (`--split holdout --holdout-final <token>`, mara moja). Chief review ya S1 + Open Questions.
OPEN QUESTIONS (ndani ya reports/strategy_lab_implementation.md):
  1. Param-sweep depth (event-internal params au SL/TP+context tu per RULING)? Pendekezo: RULING tu S1.
  2. p-value method (normal-approx sasa vs bootstrap S2)? Pendekezo: bootstrap S2.
  3. Candidate promotion threshold (zote N>=30 -> S2, au pre-filter)? Pendekezo: zote (pre-registration).
  4. Walk-forward windows halisi (rolling) kwa S2 — Chief aelekeze muundo.
NOTE: strategy_lab = research harness (numpy OK, SIO Engine core — purity inahusu core). numpy/polars
nilifunga kuverify; PC ya Operator ina stack. e2e/core sweep haijavunjika.

=== CHIEF REVIEW ya S1 strategy_lab (2026-07-09): APPROVED + FIXES 2 za Chief ===
VERDICT: APPROVED. Ubora mzuri: reuse sahihi ya episodes() (fill rules hazikuguswa), holdout
guard inakataa KABLA ya kusoma (PermissionError, self-tested), grid ruling/pre-registration
imeheshimiwa, BH-FDR math sahihi, outputs safi (no pnls). FIXES za Chief (committed juu yake):
  F1. Vol-filter decidability (EP-5): vol state ya bar ya ENTRY (i+1) haijulikani hadi bar
      ifunge -> episodes() sasa inarekodi vol[i] (bar ya SIGNAL); session inabaki hour[i+1]
      (ratiba = ex-ante).
  F2. Context filter ilikuwa POST-HOC (baada ya episodes) -> position-gating isingeendana na
      strategy halisi ya filtered. Sasa: _mask_context() inaweka filter KWENYE SIGNALS kabla
      ya episodes(); _match imeondolewa; self-test [2c] mpya inathibitisha. Sweep 15/15.
LESSON kwa kazi zijazo: filter yoyote ya strategy lazima (a) iamuliwe kwa taarifa zilizopo
wakati wa signal, (b) iingie KWENYE simulation, sio kwenye uchujaji wa matokeo.

=== S4 TASK (Chief, 2026-07-09 — baada ya S3 PASS): STRAT-001 -> POLICY + SIGNAL TOOL ===
STRAT-001 (PROVEN-OOS): nr7_break × USDCHF H1 · SL 2.0×ATR(14) / TP 1.0×ATR(14) · timeout 24
bars · no-LATE (entry-hour 17-23 = skip) · position 1 kwa wakati. Kazi mbili:
  1. **strat001_signal.py** (ndogo, kwanza): CLI inayosoma bars za hivi karibuni za USDCHF H1
     (CSV/parquet path ya Operator) → detect NR7 kwenye bar iliyofunga (REUSE event_library_v2.
     nr7_break + wilder_atr — USIANDIKE math mpya) → print pending orders (buy-stop high+0.1 /
     sell-stop low−0.1, SL/TP computed) katika format ya paper_trader --signal. Self-test na
     bars synthetic. Hii inamwezesha Operator paper-trade STRAT-001 bila hesabu za mkono.
  2. **policy rasmi**: "policy:strat001-nr7-usdchf@v1" kwenye decision_policy.py — deterministic,
     inaingia decision_engine → gate (FTMO 5) → paper broker (mnyororo uleule wa E1-E4).
     Provenance: strategy_lab S1-S3 (commits ccfbb24/e1a0d27/86a5977). Self-tests; Rule 8 report.

=== S4 UPDATE (Chief, 2026-07-09): tool + policy sasa ni za strategies MBILI ===
S3b imezaa STRAT-002 (nr7_break × USDJPY · SL1.0/TP1.0 · no-LATE · PROVEN-OOS). Badilisha
spec ya S4: strat001_signal.py → **strat_signal.py** yenye REGISTRY ya strategies PROVEN
(STRAT-001 USDCHF SL2/TP1; STRAT-002 USDJPY SL1/TP1; zote nr7+no-LATE) — CLI: --pair au
--all, inasoma bars, inatoa pending orders kwa format ya paper_trader. Policy: moja kwa kila
strategy ("policy:strat001@v1", "policy:strat002@v1") au registry-policy moja — chagua rahisi,
eleza. Bado: REUSE nr7_break + wilder_atr; self-tests; Rule 8 report.

=== CYCLE-2 TASK (Chief, 2026-07-09): S1-C2 GRID + STRENGTH FRAMEWORK ===
Events mpya 4 tayari zimejengwa na Chief (squeeze_break, nr4_inside, gap_fade, london_drift —
registry EVENTS_V2 sasa 20; USIzibadilishe). KAZI ZAKO (baada ya S4 tool):
  1. strategy_lab: ongeza GRID_C2 tofauti na ya cycle-1 (usiguse TIER1/TIER2 za C1):
     events {squeeze_break, nr4_inside, gap_fade, london_drift} × pairs 9 × SL/TP grid ileile
     × filters {None, no-LATE} + **--tf H4 kwa {nr7_break, squeeze_break, nr4_inside,
     shock_follow}** (H-C2-1/2: COST remedy). Flag --cycle 2. m ya FDR = cells zote za C2.
  2. CURRENCY STRENGTH framework (H-C2-5, spec-light): module inayosoma pairs zote 9 kwa
     pamoja → USD strength index (trailing returns za USD dhidi ya wenzake) → event
     "usd_drift": long/short pair kulingana na strength ya pande zake. NO LOOKAHEAD; costs
     kama kawaida. Jenga strength_lab.py ndogo, reuse episodes().
  3. EXIT SCIENCE (H-C2-6): episodes() ipate exit variants za hiari: trailing stop (k×ATR),
     breakeven baada ya +1R, time-exit. Defaults = tabia ya sasa BYTE-IDENTICAL (self-test
     ithibitishe!). Kisha grid ndogo ya exits juu ya STRAT-001/002 (exploration; forward confirm).
