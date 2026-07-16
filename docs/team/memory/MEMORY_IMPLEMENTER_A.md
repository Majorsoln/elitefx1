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

=== S4 SIGNAL TOOL + POLICIES (2026-07-09) — IMEKAMILIKA ===
CURRENT TASK: **(inasubiri Chief review ya S4)** — strat_signal.py + strategy policies; sweep 17/17.
LAST COMPLETED: **S4** ✅ (deploy strategies PROVEN-OOS STRAT-001/002):
  · `src/research/strat_signal.py` MPYA — REGISTRY (STRAT-001 USDCHF SL2/TP1; STRAT-002 USDJPY
    SL1/TP1; nr7+no-LATE). pending_orders() REUSE nr7_break+wilder_atr (bars PRICE->PIPS->levels
    PRICE); no-LATE ex-ante (entry=bar hour+1); OCO buy-stop/sell-stop; SL/TP za ATR. load_bars
    (parquet/CSV). CLI --pair/--all -> format ya paper_trader --signal. Self-test 6 checks PASS.
  · `decision_policy.py` — STRATEGY_POLICIES (strat001-nr7-usdchf@v1, strat002-nr7-usdjpy@v1):
    thin SELECT + provenance (mirror OPERATOR_POLICY); registry TOFAUTI (HAIingii POLICIES ->
    demo run() safi). self-test [7] PASS. Edge=signal pre-registered+OOS proof, SIO policy logic.
  · Integration S4->E1-E4: strat_signal order -> apply_policy(strat001) -> gate(FTMO) -> VALIDATED. PASS.
  · SWEEP 17/17 PASS. Rule 8: reports/strat_signal_report.md.
NEXT AFTER: **CYCLE-2** (baada ya S4 review) — (1) GRID_C2 kwenye strategy_lab (events 4 mpya
{squeeze_break,nr4_inside,gap_fade,london_drift} x pairs 9 x SL/TP x {None,no-LATE} + --tf H4 kwa
{nr7,squeeze,nr4,shock}; flag --cycle 2; m=cells za C2); (2) strength_lab.py (usd_drift, currency
strength, reuse episodes()); (3) EXIT SCIENCE (episodes() exit variants: trailing/breakeven/time;
defaults BYTE-IDENTICAL - self-test ithibitishe; kisha grid ndogo juu ya STRAT-001/002).
OPEN QUESTIONS (ndani ya reports/strat_signal_report.md):
  1. next-bar hour kwa no-LATE (gaps/weekend) — tool vs Operator? Pendekezo: onyo + Operator anaona ratiba.
  2. OCO kwenye paper_trader (--oco) au mkono? Pendekezo: mkono sasa, --oco baadaye.
  3. policy-per-strategy (nilichagua) vs registry-policy moja? Chief athibitishe.
  4. strat_signal live (MT5) = E4-adjacent, imezuiwa hadi Project Director (RED LINE).
NOTE: strat_signal = research/tool (numpy OK). numpy/polars nilifunga kuverify; core purity haijaguswa.

=== CHIEF REVIEW ya S4 (2026-07-09): APPROVED bila fixes ===
strat_signal.py: registry ya STRAT-001/002, reuse kamili (nr7_break+wilder_atr), no-LATE
decidable (hour+1), OCO+SL/TP zinazolingana na harness semantics, pip scaling ya JPY, CSV/parquet
loaders, self-test 6/6 (ikiwemo ratio 2.0 ya SL/TP na LATE skip). decision_policy: STRATEGY_POLICIES
kama provenance-wrappers deterministic NJE ya POLICIES za demo — chaguo sahihi, self-test (7) nzuri.
Sweep 17/17. Kazi safi — hakuna marekebisho. INAYOFUATA KWAKO: CYCLE-2 tasks (GRID_C2 +
strength framework + exit science — tayari zimo memory yako).

=== CYCLE-2 (2026-07-09) — IMEKAMILIKA (tasks 3) ===
CURRENT TASK: **(inasubiri Chief review ya Cycle-2)** — GRID_C2 + strength_lab + exit science; sweep 18/18.
LAST COMPLETED: **CYCLE-2** ✅ (Chief directive; hypotheses HAZIJAPIMWA — S1-C2->S3-C2 ndiyo hukumu, EP-3):
  1. GRID_C2 (strategy_lab): grid_c2(pairs,tf) — H1={squeeze_break,nr4_inside,gap_fade,london_drift};
     H4={nr7_break,squeeze_break,nr4_inside,shock_follow} (cost-remedy H-C2-1/2); pairs 9 x SL/TP x
     {None,no-LATE}. --cycle {1,2}; outputs _c2 (C1 haijaguswa). self-test [1c]. FDR m=cells za C2.
  2. strength_lab.py MPYA (H-C2-5): usd_strength (trailing returns, NO-LOOKAHEAD truncation-invariant)
     + usd_drift (base-USD long/quote-USD short USD ikisimama; edge+rearm; non-USD zero) + backtest
     kwa episodes(). run() inalign pairs kwa ts. self-test 5 checks PASS.
  3. EXIT SCIENCE (event_quality_report): episodes(exit_cfg=None) — default HAIGUSWI (byte-identical,
     golden hashes mr=28cc2218 nr7=872edc44 self-tested [7]). _exit_variant: trailing/breakeven/time.
     exit_sweep(cell,data) kwenye strategy_lab (fixed==default; [6]). BYTE-IDENTICAL = STRAT-001/002
     reproducible bit-kwa-bit.
  · SWEEP 18/18 PASS (harness iliyokaguliwa haijavunjika). Rule 8: reports/cycle2_implementation.md.
NEXT AFTER: Chief review + Operator aendeshe S1-C2 (--cycle 2 --split train, H1 na H4) + strength_lab
+ exit exploration -> S2-C2 (validation+FDR) -> S3-C2 (holdout). OOS rules za uadilifu za Chief.
OPEN QUESTIONS (ndani ya reports/cycle2_implementation.md):
  1. usd_drift params (k,std_win) — S1-C2 grid au defaults? Pendekezo: grid.
  2. Strength beyond USD (EUR/JPY indices)? Pendekezo: USD tu sasa (spec-light).
  3. Exit-grid promotion juu ya STRAT PROVEN inahitaji forward-confirm (EP-3)? Pendekezo: NDIYO.
  4. GRID_C2 event-internal params? Pendekezo: SL/TP+filter tu (kama C1).
NOTE: byte-identical ni ushahidi wa msingi — episodes() default haijabadilika; strategies PROVEN salama.

=== C2 ADDENDUM (Chief, 2026-07-09): METALS SUPPORT + pairs 2 mpya ===
Inventory: XAUUSD/GBPJPY/EURCHF ticks kamili zipo disk. KAZI MPYA NDOGO (kabla ya GRID_C2):
  a. METALS SUPPORT: pip() (market_state_engine + event_quality_report/strategy_lab kupitia
     pip import; paper_trader PIP_SIZE/PIP_VALUE; strat_signal _pip_size) — ongeza mapping ya
     metals: XAUUSD pip=0.01 (quote 2dp), pip_value inayolingana (weka wazi assumption kwenye
     Known Limitations). Self-tests kwa XAUUSD kwenye kila module iliyoguswa. USIvunje pairs za FX
     (regression: sweep nzima). 
  b. GRID_C2 sasa ina pairs 11 (9 + GBPJPY + EURCHF); XAUUSD inaingia TU baada ya (a) ku-approve.

=== METALS SUPPORT (C2 addendum task a) — 2026-07-09 IMEKAMILIKA ===
CURRENT TASK: **(inasubiri Chief review ya Cycle-2 + metals)** — sweep 18/18; branch imesync na main (pairs-11).
LAST COMPLETED: **METALS SUPPORT (XAUUSD)** ✅ (C2 addendum task a):
  · market_state_engine.pip(): XAU-gate (raise) -> XAU=0.01 (quote 2dp); XAG bado gated (hakuna data).
    self-test: pip metals (XAUUSD/EURUSD/USDJPY + XAG-gated).
  · paper_trader: PIP_SIZE/PIP_VALUE (lambda->function) + XAU (0.01 / $1-per-pip-100oz); self-test [5]
    XAUUSD signal FILLED (sl_pips 500, risk $120).
  · strat_signal: _pip_size (XAU 0.01), _dec (XAU 2dp); self-test [6].
  · event_quality_report/strategy_lab/strength_lab: pip transitive (fix moja ya market_state_engine
    inazifikia; hakuna code change). FULL SWEEP 18/18 PASS (FX HAIJAVUNJIKA). Rule 8:
    reports/metals_support_report.md.
  · Merge origin/main (pairs-11 S3c world) -> branch yangu; conflict ya memory pekee (append-log,
    pande zote zimehifadhiwa). Cycle-2 yangu bado haijamerge main (inasubiri Chief review).
NEXT: task b (XAUUSD -> config pairs + GRID_C2) = baada ya Chief approval ya metals (grid_c2 tayari
pair-agnostic). Chief review ya Cycle-2 + metals.
OPEN QUESTIONS (ndani ya reports/metals_support_report.md):
  1. pip_value halisi ya XAUUSD (broker) — nimeweka $1/pip/100oz default; Operator athibitishe.
  2. XAUUSD kwenye GRID_C2 sasa (task b) au subiri backtest? Chief/Operator waamue.
  3. XAG support (data ikipatikana)? gated kimakusudi sasa.

=== CHIEF REVIEW ya C2 build + metals (2026-07-09): APPROVED bila fixes (mara ya 2 mfululizo) ===
Verified: (1) exit science — default path (exit_cfg=None) HAIJAGUSWA (code + golden-hash test);
(2) GRID_C2 tf-aware + outputs _c2 (C1 isolated); (3) strength_lab — trailing returns no-lookahead,
orientation base/quote sahihi, INNER JOIN ya ts (cross-sectional alignment sahihi), reuse ya
episodes(); (4) metals — XAU pip 0.01 kila mahali, XAG bado gated, FX regression 18/18.
Kazi bora. XAUUSD sasa inaruhusiwa kuingia config (task b yako: baada ya Operator kuiwasha).

=== WAVE-1 TASKS (Chief, 2026-07-12 — kutoka data_science_review ya SCIENTIST-D; KABLA ya S3-C2) ===
Soma kwanza: reports/data_science_review.md §B (designs kamili zimo — fuata R1/R4/R5/R6 verbatim).
  R1 (kipaumbele #1): pvalue_boot() kwenye strategy_lab — stationary block bootstrap
     (Politis-Romano, mean block ~10, studentized), seed deterministic kutoka cell key.
     Self-tests: (a) i.i.d. symmetric null → boot ≈ z; (b) two-point negative-skew null →
     boot size ≈ nominal ambapo z = ×1.2-1.4 (jedwali la §A3-W1); (c) determinism. Kisha
     sensitivity restatement: p za bootstrap kwa cells ZILIZOKWISHA-FUNGULIWA za S3/S3b/validation
     (hakuna dirisha jipya) — ripoti two-column.
  R4: portfolio_v0.py — episodes za STRAT-001+002 (opened windows): overlap ya siku/saa,
     daily-PnL corr, joint-DD vs sum, worst joint day vs FTMO daily-loss. Rule ya kabla:
     corr>0.4 → halve size.
  R5: (1) EV(Δspread) table kwenye write_outputs (analytic); (2) split trades za proven kwa
     spread_state (NORMAL/WIDE) ya entry bar; (3) GOLD: empirical spread dist kutoka ticks
     (spread_quality.py) + percentile-based stop slippage — kabla ya gold registration yoyote.
  R6: win-rate CUSUM/control-chart kwa STRAT-001/002 (thresholds za STRAT-001: review<70%,
     halt<66% @60-trade rolling; compute za STRAT-002 kwa framework ileile na uziandike KABLA
     forward data haijaongezeka).
Zote self-tested, Windows-safe, Rule 8 reports. WAVE-2 baadaye: R3 rolling-origin folds, R8 ticks.

=== WAVE-1 (2026-07-12) — IMEKAMILIKA (R1+R4+R5+R6) ===
CURRENT TASK: **(inasubiri SCIENTIST-D referee + Chief review ya WAVE-1)** — sweep 21/21.
R1 = GATE ya B-PRIME sequencing; deviation ya calibration inahitaji ridhaa ya referee (OQ#1).
LAST COMPLETED: **WAVE-1** ✅ (designs za data_science_review §B):
  R1: pvalue_boot (strategy_lab) — stationary block bootstrap (Politis-Romano) + NW studentization,
    percentile-t, centered, seed=cell key. **DEVIATIONS 2 kwa EVIDENCE** (jedwali wave1_report.md):
    mean_block=3 (sio ~10 — block averaging inameza skew ya t*: mb10 size 0.063-0.072 inashindwa
    acceptance test ya design yenyewe) + NW denominator (i.i.d.-sd + block = distorted). mb=3+NW:
    skew nulls 0.043-0.053 (~nominal; z 0.051-0.068) NA AR(rho.5) 0.058 (z 0.121). ENGINE SWAP
    pre-registered kwa commit: FDR rasmi = p_boot; p_z = sensitivity column (two-column kila report);
    --cells-file kwa restatement ya S3/S3b opened cells. Self-tests [7][8][9] PASS.
  R4: portfolio_v0.py — analyze(): days-both-fire, hours-both-held (bounds), daily-PnL corr,
    joint-DD vs sum, worst-joint-day vs FTMO$500; RULE pre-registered corr>0.4->halve. PASS 4/4.
  R5: cost_stress.py — ev_spread_table (analytic; SASA kwenye kila strategy_lab report) +
    spread_split (WIDE<0 -> DEPLOYMENT-policy skip, episodes() HAIJAGUSWA) + stop_slippage_percentile
    (gold p95/2; Chief approval kabla ya cost-model change). PASS 4/4.
  R6: winrate_monitor.py — registry pre-registered SASA: STRAT-001 REVIEW<70/HALT<66 @60;
    **STRAT-002 REVIEW<54.0/HALT<50.0** (framework ileile: offsets +1.7/-2.3pp juu ya w_be);
    posterior alarm (Beta prior kutoka holdout; SE ya POSTERIOR — interpretation note kwa referee);
    paper-log adapter. PASS 6/6.
  · SWEEP 21/21 PASS (episodes()/C1/C2 hazikuguswa). Rule 8: reports/wave1_report.md.
NEXT: (1) SCIENTIST-D referee ya R1 calibration (mean_block=3+NW — OQ#1, BLOCKER ya S3-C2);
(2) Operator: sensitivity restatement (--split validation + --cells-file S3/S3b) + R4 run + R5
spread_split/gold runs; (3) baada ya referee -> S3-C2 registration (bootstrap p, reps 8, q=0.05,
MDE screen, gold defer). WAVE-2 baadaye: R3 rolling folds, R8 ticks.
OPEN QUESTIONS (ndani ya reports/wave1_report.md):
  1. **BLOCKER:** R1 calibration (mb=3+NW vs design ~10) — referee/Chief.
  2. Restatement run — Operator + runbook? (cells za S3 = holdout token, zimefunguliwa).
  3. R6 alarm-line = posterior SE (sio rolling-60 flat — margin ya STRAT-002 5.5pp < SE@60 6.4pp).
  4. R4 usd_per_pip=12 placeholder — worst-day $ na sizing halisi ya MWONGOZO.

=== BUILD TASK (Chief, 2026-07-12): family_pooled.py (design ya SCIENTIST-D, APPROVED) ===
Soma KWANZA: reports/family_pooled_design.md (spec kamili §1-§8; fuata verbatim). Jenga
src/research/family_pooled.py:
  - REUSE tu (ZERO changes): episodes, _mask_context, load_window (ongeza return ya `ts` array
    - additive, non-breaking), pvalue_boot. Reps 4 zimefungwa (§1 table); universe FIXED.
  - R-normalization: pnl_R = pnl_pips / (sl_atr × atr[signal_bar]) — §2. Pool = union ya streams
    4 sorted by ts_entry (tie: pair alphabetical). Statistic: pvalue_boot(pooled_R, B=50000,
    mean_block=3), seed kutoka registration string (§3).
  - Acceptance tests AT1-AT8 ZOTE (§5): pip-scale invariance, R-norm correctness, determinism,
    **AT4 mixture-null size ∈[0.040,0.060] (muhimu zaidi)**, holdout red-line guard, no-clobber
    (outputs data/strategies/family_pooled_c2watch.jsonl + reports/family_pooled_report.md TU;
    candidates*.jsonl HAZIGUSWI), dedup assert, AT8 dry-run VALIDATION.
  - Split flag: validation (dry-run/screen) | holdout (one-shot, Chief token). Windows-safe,
    Rule 8 report. USIENDESHE holdout - Chief atatoa token baada ya referee + screen PASS.
UKIMALIZA: ripoti "tayari family-pooled build". SCIENTIST-D atafanya referee (MC huru ya AT4).

=== FAMILY-POOLED BUILD (2026-07-13) — IMEKAMILIKA ===
CURRENT TASK: **(inasubiri SCIENTIST-D referee + AT8 dry-run screen + Chief registration/token)** —
build tayari; AT1-AT8 PASS 8/8; sweep 22/22. HAKUNA holdout run (Rule: Chief token baada ya referee+screen).
LAST COMPLETED: **family_pooled.py BUILD** ✅ (design SCIENTIST-D reports/family_pooled_design.md §1-§8, verbatim):
  · src/research/family_pooled.py MPYA — runner + AT1-AT8. REP_CELLS (universe FIXED §1: REP-1
    nr4_inside×GBPJPY 1.5/1.5; REP-2 nr7_break×EURGBP 1.5/1.0; REP-3 nr7_break×EURJPY 1.0/3.0;
    REP-4 nr7_break×AUDUSD 1.5/3.0; zote no-LATE). R-units normalization §2 (pnl_R=pnl_pips/
    (sl_atr×atr[signal_bar])); pool_streams (union sort ts→pair, dedup AT7); registration_string+
    _seed_from_registration (§3.3 hashing ileile ya _seed_from_key); mde_screen (§4); run_family
    (§3-6 + AT5 holdout guard kupitia load_window); _write_outputs (AT6 no-clobber: family_pooled_
    c2watch.jsonl + report TU); _boot_ci (§6). Criterion m=1: pvalue_boot(B=50k)<0.05 AND EV_R>0.
  · REUSE-ONLY (ZERO changes): episodes/_mask_context/pvalue_boot/pvalue_gt0. strategy_lab.load_window
    += `ts` (ADDITIVE non-breaking §8.1; callers intact; byte-identical golden hashes mr/nr7 INTACT).
    run_selftests.py += family_pooled.
  · Self-test AT1-AT8 PASS 8/8; SWEEP 22/22 PASS. Rule 8: reports/family_pooled_report.md.
NEXT AFTER: (1) SCIENTIST-D referee (MC huru ya AT4 full 20k×B=50k; verbatim-vs-implemented);
  (2) Operator: AT8 dry-run VALIDATION halisi → EV_R/sd_R EXACT → §4 screen shrink 0.35 (fail→stop,
  doc → LESSON); (3) Chief: freeze registration (§8.4) + holdout token → one-shot verdict+CI. WAVE-2: R3/R8.
OPEN QUESTIONS (4, ndani ya reports/family_pooled_report.md):
  1. **AT1 fixed-slippage residual (referee):** §2 "exact" vs episodes() SLIP const (0.1/0.3 pip) →
     pnl_R exact-minus-SLIP·(1-1/scale)/R. Nimetekeleza struct-exact + residual=closed-form (fixed sig,
     kutenga na event `tick` absolute threshold). Rule 1: sijagusa episodes. Pendekezo: kubali.
  2. Seed = sha1(reg_string)[:12]→int (hashing ileile ya _seed_from_key juu ya string nzima). Chief athibitishe.
  3. REP-2 tie-break B=50k recompute = hatua ya registration (Chief §8.4), si build.
  4. Format ya rekodi ya registration freeze — Chief aelekeze.
NOTE (SYNC): main iko mbele SANA ya branch ya zamani — E1-E4 CLOSED, E3 ilitekelezwa na Chief moja kwa
moja (session yangu ya awali haikupush kwa wakati). Nilianzisha upya branch kutoka main (kesi ya
SCIENTIST-D 2026-07-12). CURRENT PHASE: Alpha Engineering S-series + WAVE data-science remediation.

=== FIXES F1/F2 (Chief, 2026-07-13 — referee ya SCIENTIST-D; family_pooled.py; ~30 min) ===
Referee APPROVED WITH FIXES (reports/family_pooled_referee_report.md §4). Fanya KABLA ya freeze:
  F1 (SERIOUS): mde_screen inaitwa na N ya split (pooled trade count) - kwenye dry-run VALID
     (N~531) hii inashusha MDE ×1.25 = screen anti-conservative (mtego wa ruling 07-12). Design
     §4: MDE kwa N_exp = Σ_reps (len(stream_i)/days_i) × 347. FIX: hesabu n_exp (data["days"]
     ipo per pair kwenye cell_stream/run_family) → ita mde_screen(ev_r, sd_r, n_exp) kwa screen
     ya REGISTRATION; split-n version yaweza kubaki kama descriptive extra. Acceptance: kwenye
     fixture, screen MDE = 1.645·sd_R/√n_exp na n_exp kutoka days=250 fixtures, SI pooled N.
  F2: run_family inaendelea KIMYA kama load_window inarudisha None kwa pair (missing.append) →
     pooled test ya streams <4. FIX: `if missing: raise RuntimeError(...)` kwa split in
     (validation, holdout) - test iliyosajiliwa = streams 4 HASA. Acceptance: fixture yenye pair
     moja imeondolewa lazima i-RAISE, si kuripoti.
  N1 (non-blocking): print per-rep EV_R + sign kwenye report (data ipo kwenye jsonl).
Self-tests mpya kwa F1/F2. Sweep intact. UKIMALIZA: "tayari F1F2" - SCIENTIST-D spot-check diff.

=== FIXES F1/F2 (2026-07-13) — IMEKAMILIKA ===
CURRENT TASK: **(inasubiri SCIENTIST-D spot-check ya diff → Operator AT8 dry-run → Chief freeze/token)**
— F1/F2 zimefanyika; self-test 10/10 (AT1-AT8 + F1 + F2); sweep 22/22. HAKUNA holdout run.
LAST COMPLETED: **F1/F2 referee fixes** ✅ (reports/family_pooled_referee_report.md §4; statistic HAIJAGUSWA):
  · F1 (SERIOUS): run_family sasa inahesabu n_exp = Σ(n_i/days_i)×347 (design §4) kutoka data["days"]
    per pair → mde_screen(ev_r, sd_r, n_exp) = screen ya REGISTRATION (SIO pooled-N ya split =
    anti-conservative). screen_split (pooled-N) inabaki descriptive. Self-test [F1]: MDE=1.645·sd/√N_exp.
  · F2: run_family inaraise RuntimeError kama pair inakosekana kwa split in (validation, holdout) —
    linda one-shot (streams 4 HASA = test iliyosajiliwa). AT5 holdout guard bado inatangulia
    (PermissionError kutoka load_window KABLA ya missing-check). Self-test [F2]: drop pair → RAISE.
  · N1 (non-blocking): per-rep EV_R + sign zinachapishwa report (jedwali; 4/4 chanya = mechanism evidence).
  · Referee rulings: OQ#1 (fixed-slip residual) ACCEPTED — test yangu stronger kuliko "bit-identical";
    USIFANYE slippage pip-proportional. OQ#2 (seed) CONFIRMED. OQ#3 tie-break = registration (Chief §8.4).
  · Self-test 10/10 PASS; SWEEP 22/22 PASS. Report: reports/family_pooled_report.md (§Referee Fixes).
NEXT AFTER: (1) SCIENTIST-D spot-check ya F1/F2 diff (no new MC — statistic untouched); (2) Operator
  AT8 dry-run VALIDATION → EV_R/sd_R EXACT → §4 screen shrink 0.35 kwa N_exp (fail→stop→LESSON);
  (3) Chief freeze registration (§8.4: B=50k, seed, REP-2 tie-break recompute, criterion) + holdout token
  → one-shot verdict+CI. WAVE-2: R3 rolling folds, R8 ticks.
OPEN QUESTIONS: OQ#1/OQ#2 CLOSED na referee. Zilizobaki (Chief, §registration): REP-2 tie-break B=50k
  recompute; format ya rekodi ya freeze. Hakuna blocker upande wa build.

=== C2-0 MZUNGUKO-2 (2026-07-13) — IMEKAMILIKA ===
CURRENT TASK: **(inasubiri Chief review ya C2-0 + run za Operator)** — 15m/30m states + HTF context.
LAST COMPLETED: **C2-0** ✅ (msingi wa data wa "HTF-bias -> 15m/30m entries"):
  D1: `intraday_state_engine.py` MPYA — ticks->15m bars (time_bucket 15MIN, spr=median pips) ->
    rollup_30m (semantiki ileile ya engine) -> states (vol/act _reg3 deseasonalized + spread
    _rank_wide + session). REUSE building blocks za market_state_engine kwa IMPORT (engine
    HAIJAGUSWA — diff tupu, golden PASS). Deseason window ime-scale muda-sawa (SEAS_WIN_INTRA
    15m=240/30m=120 = siku 60 kama H1; bila hii surge detection 49%->99%, self-test ilinasa).
    Hive: processed/state/symbol=X/tf={15m,30m}.parquet (state_path loaders wote wanafanya kazi).
    Self-test 5 PASS: rollup==manual agg, truncation invariance, surge 99%, session=f(hour), schema.
  D2: `htf_context.py` MPYA — H4/D1 features: trend (ema_slope/linreg_slope/trend_sign+deadband),
    regime (vol/act), structure (rolling S/R 20 closed bars, dist kwa ATR), momentum (rsi14 REUSE
    wilder_rsi, roc10). ALIGNMENT: close_ts=ts+duration -> join_asof BACKWARD (LTF bar inapata HTF
    bar ya mwisho iliyoFUNGWA <= t). **MTEGO WA LEAKAGE self-tested**: spike bar inayozunguka LTF
    bar HAIONEKANI (context=prev bar roc -0.008 vs spike +0.968); boundary t==close_ts OK; D1 OK.
    Output: processed/context/symbol=X/tf=<ltf>.parquet — tayari kwa _mask_context-style filters.
  D3: `reports/cycle2_intraday_htf.md` — pre-data version (muundo + no-lookahead evidence + amri);
    run za Operator zinajaza sehemu A (coverage/spread/sessions) na B (context counts).
  · SWEEP 24/24 PASS (22->24; market_state_engine golden PASS — HAIJAGUSWA). Merge origin/main
    (S3-C2 FAIL-kwa-heshima + MZUNGUKO-2 launch + family_pooled) kwenye branch — safi.
NEXT: Operator aendeshe (1) intraday_state_engine.py (2) htf_context.py kwenye PC ya data ->
report inajaa; kisha C2-0b review (Chief: feature set inatosha kwa STRATEGIST-M?) -> C2-1.
OPEN QUESTIONS (ndani ya reports/cycle2_intraday_htf.md):
  1. C2-0b: features 9 zinatosha kwa hypotheses 10 za C2-1? (kuongeza ni additive).
  2. H2 kama HTF ya tatu? (htf_features ni TF-agnostic — param).
  3. Trend deadband 0.02 ATR/bar — strategist anaweza ku-grid.

=== C2-2a INFRA (2026-07-14) — IMEKAMILIKA ===
CURRENT TASK: **(inasubiri Chief review ya C2-2a → S1 ya WAVE-C2-A)** — context loader +
_mask_context_dir; self-test PASS (checks 4 mpya); SWEEP 24/24; ZERO statistic fns zimeguswa.
LAST COMPLETED: **C2-2a — infra ya context-aware S1 (WAVE-C2-A: HC2-01/03/06)** ✅:
  · strategy_lab.load_window += key `ctx` (ADDITIVE): _load_context() inasoma context parquet ya
    htf_context (data/processed/context/symbol=X/tf=Y.parquet), LEFT-join EXACT kwa ts (row_index
    inalinda order; numeric→float64 NaN, state→object); parquet haipo → ctx=None + onyo (C1/H1/H4
    grids haziathiriki). context_path() helper. HAKUNA join mpya ya HTF (alignment ya htf_context
    iliyokwisha-thibitishwa ndiyo inayotumika).
  · _mask_context_dir(out, entry, allow_long, allow_short) MPYA sambamba (_mask_context HAIJAGUSWA):
    market sig +1/−1 inahitaji allow_long/allow_short[i]; stop LL/SS → NaN. Decidability ya signal
    bar i ILEILE. One-sided (HC2-01) + conditions tofauti long/short (HC2-06) zinawezekana.
  · Self-tests mpya [10] loader (scrambled-order parquet → ts-align; gap → NaN/None; missing → None)
    · [11] mirror symmetry (market+stop; inputs intact) · [12] one-sided (episodes long-only n=646)
    · [13] decidability trap (allow[i] survives; allow[i+1]-only dies).
  · DIFF VERIFICATION: insertions-only 142+/0− kwenye strategy_lab.py PEKEE — episodes/_mask_context/
    pvalue_boot/pool_streams/_r_normalize/bh_fdr byte-identical; golden hashes event_quality_report
    PASS kwenye sweep. false_break = WAVE-B (sikuijenga, kwa spec).
  · Report: reports/cycle2_intraday_htf.md §C. SWEEP 24/24 PASS.
NEXT AFTER: Chief review → S1 ya WAVE-C2-A (evaluate/grid ya HC2-01/03/06 itajengwa juu ya ctx +
_mask_context_dir — kazi ya C2-2b/S1 registration ya Chief). WAVE-B: false_break + 15m + gold.
OPEN QUESTIONS:
  1. evaluate()/grid ya WAVE-C2-A: nani anafunga context-condition specs (mf. HC2-01 allow_long =
     (d1_trend_sign==1)&(h4_trend_sign==1)) kwenye grid cells? Pendekezo: Chief a-freeze specs kama
     TIER1 ruling, mimi niziweke kwenye grid_wave_a (kazi ijayo).
  2. ctx loading kwenye pairs/TF zisizo na context (H1/H4) inachapisha onyo kila load — kelele ya
     runs za C1. Ikisumbua Operator: flag quiet au cache ya onyo moja (cosmetic, si logic).

=== C2-3 BUILD (2026-07-14) — IMEKAMILIKA ===
CURRENT TASK: **(inasubiri Operator kuendesha S1 TRAIN: `python src/research/wave_c2a.py --train`)**
— runner tayari; self-test PASS 6/6; SWEEP 25/25.
LAST COMPLETED: **C2-3 — wave_c2a.py, S1 TRAIN runner ya WAVE-C2-A (grid FROZEN m=84)** ✅:
  · src/research/wave_c2a.py MPYA (module tofauti — strategy_lab HAIJAGUSWA): HYPOTHESES 3 kwa
    NAMBA za docs/WAVE_C2A_REGISTRATION.md KAMA ZILIVYO (HC2-01 nr7/nr4 stop 2x4x5=40 · HC2-03
    trend_resume/rsi2 market 2x4x3=24 · HC2-06 bb_fade/engulf market 2x2x5=20; TF=30m; max_hold
    32/32/24; FX pekee — hakuna gold). allow_long/allow_short = lambdas juu ya ctx za loader
    (signal-bar i). Pipeline: load_window(train) -> EVENTS_V2 fn -> _mask_context_dir (context ON
    signals) -> episodes() (fill rules/costs kama zilivyo) -> metrics (n/ev/gross/cost_share/win/
    pf/timeout_share/days; MIN_N ya strategy_lab).
  · NaN HANDLING (deviation-with-reason kutoka mfano wa prompt, documented kwenye docstring):
    nan_to_num(nan->0) ingekosea kwa HC2-06 `trend_sign>=0`/`<=0` (0 inapita -> NaN ingeruhusiwa).
    Badala yake: np.isfinite guard juu ya KILA column -> NaN=haijulikani=allow False kwa conditions
    ZOTE. Self-test [2] ina trap ya >=0 inayothibitisha.
  · GUARDS: run() inakataa split!="train" (PermissionError) — S1 ni TRAIN pekee; sacred splits za
    load_window zinabaki chini. Pair bila ctx/state -> skip + row ya n=0 kwenye jsonl (accounting
    ya m=84 inabaki kamili). HAKUNA p-value/FDR (S2 = family-pooled + BH-FDR, Chief).
  · Outputs: data/strategies/wave_c2a_train.jsonl (rows 84 zote) + reports/wave_c2a_s1_train.md
    (muhtasari per hypothesis + candidates EV>0).
  · Self-tests 6: [1] cells==84 (40/24/20, pairs/TP/max_hold frozen, no-gold) · [2] NaN exclusion +
    >=0 trap + trades=0 · [3] one-sided inafika episodes (stop na market long-only) · [4] HC2-06
    asymmetric (support->long, resistance->short) · [5] determinism (run x2 identical) + skip-pair
    · [6] outputs 84 rows + report + TRAIN-only guard. SWEEP 25/25 (run_selftests += wave_c2a).
  · DIFF: file mpya + MODULES list pekee — strategy_lab/event_quality_report/family_pooled/
    event_library_v2 diff TUPU (ZERO statistic fns).
NEXT AFTER: Operator: `python src/research/wave_c2a.py --train` kwenye PC ya data -> jsonl+report
("tayari C2-3 S1") -> Chief review -> C2-4 (S2 family-pooled VALIDATION + BH-FDR).
OPEN QUESTIONS:
  1. Report ya S1 inaorodhesha EV>0 candidates in-sample — Chief anataka pia jedwali la cells ZOTE
     84 kwenye report (si jsonl tu)? Sasa: jsonl=zote, report=muhtasari+chanya (kuepuka jedwali refu).
  2. C2-4: pooling ya S2 itahitaji ts kwenye trades za wave_c2a (mtindo wa _r_normalize) — nitaongeza
     ts_entry kwenye rows wakati wa C2-4 build (additive), si sasa (scope ya C2-3 ni TRAIN runner).

=== C2-4 BUILD (2026-07-14) — IMEKAMILIKA ===
CURRENT TASK: **(inasubiri run ya Operator: `python src/research/wave_c2a.py --validate`)** -> ripoti
"tayari C2-4 S2". Kisha: survivors -> C2-6 freeze + HOLDOUT one-shot; hakuna -> LESSON.
LAST COMPLETED: **C2-4 build** ✅ — run_s2 kwenye wave_c2a.py (ADDITIVE; S1 haiguswi):
  · S2_CELLS: tuple FROZEN ya cells 7 (HC2-03 x EURUSD x 30m; triggers trend_resume/rsi2_pullback;
    SL/TP/max_hold=32 KAMA registration §Cells — self-test [7] inalinganisha na registration hasa).
  · run_s2("validation"): load_window(EURUSD,30m,validation) -> _masked_signals (HC2-03 allow fns
    zilezile za S1) -> episodes(sl,tp,32) -> pnl net -> pvalue_boot (ENGINE RASMI: B=50k,
    mean_block=3, seed=cell key — [8] inathibitisha == direct call) -> bh_fdr q=0.10 m=7 ([9]
    flags==recompute) -> survivor = fdr_pass NA EV_net>0 ([11]). p_z = sensitivity (SI decision).
  · GUARD: validation PEKEE — train/holdout -> PermissionError KABLA ya kusoma ([10]).
  · OUTPUT: data/strategies/wave_c2a_s2_valid.jsonl (id/n/ev_net/p_boot/p_z/fdr_pass/survivor) +
    reports/wave_c2a_s2_valid.md (survivors NAMED; kama hakuna: "HAKUNA SURVIVOR — HC2-03
    haujathibitika OOS" wazi). CLI: --validate. Pipeline test [12]: rows 7 + determinism + outputs.
  · **ZERO statistic fns**: git diff ya strategy_lab/event_quality_report/event_library_v2/
    family_pooled = 0 lines (imethibitishwa). Diff = wave_c2a.py pekee (219+/2- CLI). SWEEP 25/25.
NEXT: Operator --validate kwenye PC ya data (VALIDATION ina-consumed kwa cells 7 pre-registered;
HOLDOUT HAIJAGUSWI). Matokeo yote halali: survivors -> C2-6; hakuna -> FAIL kwa heshima + LESSON.

=== WAVE-B-prep (2026-07-14) — IMEKAMILIKA ===
CURRENT TASK: **(inasubiri Operator aendeshe gold check kwenye data + Chief review kabla WAVE-B freeze)**
— vipande 2 tayari; self-test PASS; sweep 26/26.
LAST COMPLETED: **WAVE-B-prep** ✅ (prerequisites kabla WAVE-B HC2-02/05/10 + gold haijafreezwa):
  (1) EVENT `false_break` (HC2-10) — event_library_v2.py: rolling_max/min ya bars `look` ZILIZOPITA
      (_roll incl=False, no-lookahead kama big_range_mo); short (h>hh)&(c<hh), long (l<ll)&(c>ll);
      _edge(lc,sc,rearm=8); entry="market"; imesajiliwa EVENTS_V2. Self-test: (a) no-lookahead via
      generic loop (truncation-invariant, frac=0.053) + (b) sweep semantics (crafted: bar break-fail
      → signal, normal bar → 0; short+long) + (c) determinism + golden hash cc→09b28990b0ead07b. PASS.
  (2) GOLD SPREAD-QUALITY CHECK — gold_spread_quality.py MPYA (READ-ONLY): spr dist (median/p90/p95/p99
      pips; spr column tayari pips) + ATR median (atr column price → /pip) + cost_share@p95 (TP2R) kwa
      XAUUSD 15m/30m; recommend_max_spread(~p95 round-5); verdict SUITABLE/MARGINAL/COST-FRAGILE/NO-DATA;
      report reports/xauusd_spread_quality.md. HAIBADILISHI config (Chief ruling — pendekezo tu).
      Self-test 6/6 (synthetic; missing-parquet→None). Operator ataiendesha kwenye data halisi.
  · SHERIA NGUMU zimeheshimiwa: episodes/pvalue_boot/_mask_context HAZIJAGUSWA (git diff tupu).
    run_selftests += gold_spread_quality. SWEEP 26/26 PASS.
NEXT AFTER: (1) Operator: `python gold_spread_quality.py` kwenye PC ya data → xauusd_spread_quality.md
  (verdict + max_spread halisi + coverage); (2) Chief: review false_break + gold verdict → freeze WAVE-B
  grid (HC2-02/05/10 + gold ikiwa SUITABLE); (3) S1-C2 TRAIN ya WAVE-B hypotheses.
OPEN QUESTIONS / NOTES:
  - Pendekezo la max_spread ya gold: RULE = ceil(p95_30m/5)×5. **IMEFUNGWA (2026-07-15):** data-run
    ya gold_spread_quality.py ilitoa **p95 30m = 71.0 → round-5 = 75**; ATR 30m med = 277.7 pips;
    cost-share@p95 (TP2R) = 12.78% < 25% → VERDICT **SUITABLE** (gold inafaa WAVE-B S1). Chief ruling
    (2026-07-14): config/data_config.yaml XAUUSD 60→**75** (DATA-DRIVEN). Kitanzi kimefungwa —
    pendekezo la mwisho la max_spread ya gold = **75**.
  - false_break params default look=20/rearm=8 (spec HC2-10); grid ya S1 yaweza kupima look/rearm.

=== WAVE-B-prep RE-VERIFY (2026-07-15) ===
  Nilithibitisha (baada ya SYNC): branch synced 0/0 vs origin/main; false_break self-test PASS
  (golden-hash 09b28990b0ead07b, nolook=True, sweep short@bar3=-1/long@bar3=1/normal=0, single-fire);
  gold_spread_quality self-test PASS 6/6; report SUITABLE (max_spread=75); config XAUUSD=75.
  Vipande vyote viwili tayari kwenye main (vilimergwa via PR mzunguko uliopita). Hakuna re-implement.

=== WAVE-B / HC2-10 build (2026-07-15) — IMEKAMILIKA ===
CURRENT TASK: **(inasubiri Operator aendeshe `python src/research/wave_c2a.py --train --hyp HC2-10` kwenye PC ya data)**
LAST COMPLETED: **WAVE-B HC2-10 (FAILED-BREAK-SWEEP) S1 build** ✅ (ADDITIVE kwa wave_c2a.py; docs/WAVE_C2B_HC210_REGISTRATION.md):
  (1) allow fns MPYA: `_hc210_allow_long(ctx)` = isfinite(d1_dist_sup_atr)&(<=0.5);
      `_hc210_allow_short(ctx)` = isfinite(d1_dist_res_atr)&(<=0.5). Mtindo wa _hc206 lakini
      HAKUNA h4 condition (pure D1-extreme sweep). NaN->allow=False (isfinite guard).
  (2) HYPOTHESES += HC2-10: trigger `false_break` (entry=market, look20/rearm8), SL{1.0,1.5}x
      TP{2.0,3.0}, max_hold=24, pairs (EURGBP,EURCHF,AUDUSD,NZDUSD,XAUUSD) -> cells 1x4x5 = **20**.
  (3) HYP-FILTER: `WAVE_A_IDS=(HC2-01,03,06)`; `cells(only)`/`run(only)`/`--hyp` CLI. `only=None`->
      WAVE-A (84 cells, tabia ya zamani); `only=HC2-10`->20 cells. Outputs zenye suffix:
      data/strategies/wave_c2a_train_HC2-10.jsonl + reports/wave_c2b_hc210_s1_train.md (HAIFUTI WAVE-A).
      bad id -> ValueError. HC2-10 haimo kwenye default (opt-in) -> S2 FDR enumeration (m=84) haijaguswa.
  · SHERIA NGUMU: ZERO statistic fns (episodes/pvalue_boot/bh_fdr/_mask_context_dir HAZIJAGUSWA;
    golden diff = **0 lines** vs origin/main). Grid FROZEN 20. XAUUSD imo (gold SUITABLE max_spread 75).
  Self-test wave_c2a: checks za awali [1]-[12] (WAVE-A + S2) ZOTE PASS + MPYA [13]-[16]:
    [13] HC2-10 cells==20 & default cells()==84 (no HC2-10); [14] allow isfinite/threshold (no h4);
    [15] false_break->_mask_context_dir->episodes (support->long-only, resistance->short-only, market);
    [16] hyp-filter run(only=HC2-10)->20 rows + suffix files (WAVE-A intact 84) + bad-id ValueError.
  SWEEP 26/26 PASS.
NEXT AFTER: Operator: `python src/research/wave_c2a.py --train --hyp HC2-10` (PC ya data) ->
  reports/wave_c2b_hc210_s1_train.md (candidates net+ TRAIN). Kisha Chief: survivors N>=MIN_N ->
  S2 VALIDATION (family HC2-10) + pvalue_boot B=50k + BH-FDR q=0.10 -> C2-6 HOLDOUT one-shot.
OPEN QUESTIONS / NOTES:
  - false_break params default look=20/rearm=8 (hakuna param-grid wave hii — registration).
  - S2 ya HC2-10 (baada ya S1) itahitaji registration mpya + run_s2 variant (HC2-10 family) — SI wave hii.

=== WAVE-B2 build (2026-07-15) — IMEKAMILIKA ===
CURRENT TASK: **(inasubiri Operator: [1] htf_context --ltf H1  [2] wave_c2a --train --hyp HB2-06,HB2-10)**
LAST COMPLETED: **WAVE-B2 (selective-structure @ H1) S1 build** ✅ (docs/WAVE_B2_REGISTRATION.md; vipande 3):
  (1) htf_context: `--ltf` choices += "H1" (build()/align_context ni ltf-agnostic — as-of backward
      inazuia leakage kwa ltf yoyote). Self-test [5] MPYA: H1 bars (spacing 1h) NDANI ya H4-spike bar
      -> context ya H4 iliyotangulia (imefungwa), si spike; boundary@+4h -> spike. PASS.
  (2) wave_c2a: HYPOTHESES zote zikapata field `tf` (WAVE-A HC2-01/03/06/10 = "30m"; HAZIBADILIKI,
      run_s2 haibadiliki). run() sasa cache keyed na (pair, tf) -> load_window(pair, hyp.tf, split);
      cells() inaweka `tf` kwenye kila cell (jsonl accounting); report TF-header inatoka rows. ADDITIVE.
  (3) HYPOTHESES += 2 MPYA @ H1 (opt-in, si WAVE_A_IDS):
      - HB2-06 HTF-SR-FADE-H1: bb_fade/engulf_extreme, allow=_hc206 (D1 extreme + h4 aligned),
        SL{1,1.5}xTP{1.5,2.0}, hold 16, pairs 5 (EURGBP,EURCHF,USDCHF,AUDUSD,NZDUSD) -> 40 cells.
      - HB2-10 FAILED-BREAK-SWEEP-H1: false_break, allow=_hc210 (D1 extreme, hakuna h4),
        SL{1,1.5}xTP{2,3}, hold 16, pairs 5 (zilezile) -> 20 cells. TOTAL 60.
      `--hyp` sasa inakubali comma-list (HB2-06,HB2-10 -> 60); outputs suffix
      data/strategies/wave_c2a_train_HB2-06+HB2-10.jsonl + reports/wave_c2b_hb206+hb210_s1_train.md.
  · SHERIA NGUMU: ZERO statistic fns (episodes/pvalue_boot/bh_fdr/_mask_context_dir/pool_streams
    golden diff = **0 lines** vs origin/main). XAUUSD NJE (LESSON-039 fade-on-gold mismatch gross-24.6).
    NaN->allow=False (isfinite guard, fns zilezile). S1 TRAIN-only guard inabaki.
  Self-test wave_c2a: [1]-[16] za awali (WAVE-A + S2 + HC2-10) ZOTE PASS + MPYA:
    [17] HB2 cells==60 (40+20), tf=="H1", XAUUSD nje; WAVE-A default bado 84 @30m (regression, no HB2);
    [18] comma-list run(only=HB2-06,HB2-10)->60 rows H1 + suffix files (report TF=H1; WAVE-A intact 84).
  htf_context [1]-[5] PASS. SWEEP 26/26 PASS. Files zilizoguswa: htf_context.py + wave_c2a.py TU.
NEXT AFTER: Operator (PC ya data): [1] `python src/research/htf_context.py --ltf H1` (pairs 5+) ->
  context parquet za H1; [2] `python src/research/wave_c2a.py --train --hyp HB2-06,HB2-10` ->
  reports/wave_c2b_hb206+hb210_s1_train.md; [3] commit+push. Kisha Chief: cells net+ per family ->
  S2 POWER-BY-POOLING (family_pooled R-normalized, VALIDATION, test moja/family + BH-FDR m=2).
OPEN QUESTIONS / NOTES:
  - H1 state parquet (market_state_engine) LAZIMA ipo kabla htf_context --ltf H1 (Operator R-1).
  - S2 ya HB2 = pooled per family (m=2) — itahitaji registration + runner variant (SI wave hii).

=== WAVE-B2-S2 build (2026-07-15) — IMEKAMILIKA ===
CURRENT TASK: **(inasubiri Operator: `python src/research/wave_c2a.py --validate --s2 hb210-eurchf`)**
LAST COMPLETED: **run_s2 generalized (spec-driven)** ✅ (docs/WAVE_B2_S2_REGISTRATION.md; ADDITIVE):
  - `S2_SPECS` dict: kila S2 registration = spec (hyp_id/pair/tf/cells/jsonl_name/report_name/reg_doc).
    "hc203-eurusd" (S2 ya zamani, values zilezile — rejea ya kihistoria, DEFAULT backward-compat) +
    "hb210-eurchf" MPYA: HB2-10 x EURCHF x H1, cells 2 (false_break SL1.5/TP{3.0,2.0} hold16),
    reg docs/WAVE_B2_S2_REGISTRATION.md, outputs wave_b2_s2_valid.{jsonl,md}.
  - `run_s2(spec_key=S2_DEFAULT, split="validation", ...)` — logic ILEILE (load_window(pair,tf) ->
    _masked_signals -> episodes -> pvalue_boot B=50k m=3 engine RASMI -> bh_fdr q=0.10 m=len(cells)
    -> survivor=fdr_pass NA EV>0). `_s2_cell_id(trig,sl,tp,hyp_id,pair)` + `_write_s2(...,spec)`
    spec-driven (title/verdict/paths). Guard: validation PEKEE (PermissionError); spec mbaya->ValueError.
  - CLI: `--validate --s2 hb210-eurchf` (default hc203-eurusd). Signature ya run_s2 sasa spec_key kwanza
    (self-test [10]/[12] zilihaririwa kwa keyword `split=` kudumisha regression).
  · SHERIA NGUMU: ZERO statistic fns (pvalue_boot/bh_fdr/episodes/pool_streams golden diff = **0 lines**;
    s2_verdict/run_s2/_write_s2 ni orchestration TU). Cells FROZEN 2 (hakuna kuongeza). HOLDOUT bila token
    inakataliwa. File 1 iliyoguswa: wave_c2a.py.
  Self-test: [1]-[18] za awali ZOTE PASS + MPYA/updated:
    [10] guard += bad-spec->ValueError; [19] S2_SPECS FROZEN (hb210 cells2/H1/EURCHF + hc203 cells7/30m
    regression); [20] hb210-eurchf pipeline (2 rows, id=HB2-10|false_break|EURCHF, outputs
    wave_b2_s2_valid.*, determinism, verdict named, reg_doc kwenye report). SWEEP 26/26 PASS.
NEXT AFTER: Operator (PC ya data): `python src/research/wave_c2a.py --validate --s2 hb210-eurchf` ->
  reports/wave_b2_s2_valid.md (survivor au HAKUNA). Survivor -> C2-6 HOLDOUT one-shot (token) -> STRAT-003.
OPEN QUESTIONS / NOTES:
  - HB2-06 = CLOSED-BY-POWER @ H1 (0/40 cells zilifika MIN_N — haipimiki, si mechanism-dead; registration §HB2-06).
  - S2 ya HB2-10 ni single-pair concentration (LESSON-038 caveat) — VALIDATION ndiyo mwamuzi; FAIL halali.

=== WAVE-M build (2026-07-15) — IMEKAMILIKA ===
CURRENT TASK: **(inasubiri Operator: `python src/research/wave_c2a.py --train --hyp HM-02,HM-05`)**
LAST COMPLETED: **WAVE-M (momentum arm) S1 build** ✅ (docs/WAVE_M_REGISTRATION.md; ADDITIVE, vipande 3):
  (1) INFRA trigger_params: HYPOTHESES zapata field ya hiari `trigger_params` (dict); _masked_signals
      inapitisha `spec["fn"](o,h,l,c,tc,hour, **hyp.get("trigger_params",{}))`. Default {} -> events za
      zamani hazibadiliki (regression).
  (2) INFRA hour-in-allow: _masked_signals inajenga `ctx_plus = dict(data["ctx"], hour=data["hour"])`
      na kupitisha kwa allow fns. allow fns za zamani (h4_/d1_ keys) hazivunjiki. Hour = ratiba (decidable).
  (3) HYPOTHESES 2 MPYA (opt-in, si WAVE_A_IDS):
      - HM-02 LONDON-ORB-D1 @30m: session_orb (stop) trigger_params range_hours=(7,9)/trade_hours=(9,13),
        allow=_hm_d1(cx,±1) [isfinite d1_trend_sign==±1, one-sided], SL{1,1.5}xTP{2,3}, hold16,
        pairs GBPUSD/EURUSD/EURGBP/GBPJPY/USDJPY -> 20 cells.
      - HM-05 ALIGNED-SHOCK @15m: shock_follow (market, defaults), allow=_hm_d1_hours(cx,±1)
        [_hm_d1 & 7<=hour<=16, London/NY], SL{1,1.5}xTP{2,3}, hold16, pairs EURJPY/USDJPY/GBPJPY/XAUUSD
        -> 16 cells. TOTAL 36. XAUUSD imo HM-05 PEKEE (momentum — LESSON-039 ilifunga fade tu).
  · SHERIA NGUMU: ZERO statistic fns (episodes/pvalue_boot/bh_fdr/_mask_context_dir/pool_streams +
    event_library_v2 golden diff = **0 lines**; session_orb/shock_follow zimetumika KAMA ZILIVYO).
    Grid FROZEN 36. NaN->allow=False (isfinite). TRAIN-only guard inabaki. File 1: wave_c2a.py.
  Self-test wave_c2a: [1]-[20] za awali ZOTE PASS (check [2] NaN-exclusion iliongezwa hour halali kwa
    HM allow fns) + MPYA:
    [21] HM cells==36 (20+16), tf HM-02=30m/HM-05=15m, XAUUSD=HM-05 tu; WAVE-A default 84@30m + HB2 60
    (regression, no HM); [22] trigger_params->session_orb (params (7,9)/(9,13) differ na default;
    runner-path levels==params-call; entry=stop); [23] HM-05 hour-filter (shock nje ya [7,16]->0,
    ndani->hai; long-only kwa d1=+1). SWEEP 26/26 PASS.
NEXT AFTER: Operator (PC ya data): `python src/research/wave_c2a.py --train --hyp HM-02,HM-05`
  (15m context ya XAUUSD/EURJPY/USDJPY/GBPJPY TAYARI kutoka C2-0) ->
  reports/wave_c2b_hm02+hm05_s1_train.md; commit+push. Kisha Chief: cells net+ za pairs ZOTE chanya
  (si pair-bora — kinga ya LESSON-040) -> S2 family-pooled (m=2) kupitia S2_SPECS.
OPEN QUESTIONS / NOTES:
  - ORB deviation 15m->30m (registration §Deviations #1, LESSON-039 cost-trap). Range (7,9)@30m = bars 4.
  - S2 ya HM = family-pooled multi-pair (LESSON-040 kinga) — itaongezwa kwenye S2_SPECS wave ijayo.

=== WAVE-M-S2 build (2026-07-15) — IMEKAMILIKA ===
LAST COMPLETED: **S2_SPECS += hm05-usdjpy** ✅ (docs/WAVE_M_S2_REGISTRATION.md; ADDITIVE, entry moja):
  S2_SPECS["hm05-usdjpy"] = HM-05 x USDJPY x 15m, cells 4 (shock_follow SL{1.5,1.0}xTP{2.0,3.0} hold16),
  outputs wave_m_s2_valid.{jsonl,md}, reg docs/WAVE_M_S2_REGISTRATION.md. Hakuna logic mpya —
  run_s2 spec-driven tayari ipo; BH-FDR m=4. HM-02 ORB = DEAD TRAIN (gross 5/5 hasi). LESSON-040
  jaribio la 3 la single-pair (USDJPY) — margin 3.8x + N=730 + continuation; VALIDATION ndiyo mwamuzi.
  · SHERIA: ZERO statistic fns (golden diff 0). Cells FROZEN 4. Guard validation-only. File 1: wave_c2a.py.
  Self-test: [24] spec == registration (4/15m/USDJPY/HM-05, specs 3 regression); [25] pipeline
  (4 rows, id=HM-05|shock_follow|USDJPY, outputs wave_m_s2_valid.*, determinism, verdict named).
  SWEEP 26/26 PASS. (Kando: gold-momentum @ HTF = hypothesis ya baadaye, HAIMO S2 hii.)
NEXT AFTER: Operator: `python src/research/wave_c2a.py --validate --s2 hm05-usdjpy` -> reports/wave_m_s2_valid.md.
