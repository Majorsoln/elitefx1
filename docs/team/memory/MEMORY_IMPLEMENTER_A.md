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

=== M3-1 build (2026-07-16) — MZUNGUKO-3 TABAKA-2 — IMEKAMILIKA ===
LAST COMPLETED: **M3-1 R-MAP atlas + swap model + MFE/MAE** ✅ (docs/CYCLE3_CHARTER.md; ADDITIVE):
  (1) SWAP MODEL: config/data_config.yaml `swap_pips_per_night` (default 0.5, XAUUSD 1.5; symmetric,
      LIMITATION documented). helper `apply_swap(trades, ts, swap)` (rmap.py): nights = midnight-
      crossings (date-diff ya ts[entry]/ts[exit]); pnl_swing = pnl_net - nights*swap. WRAPPER —
      episodes HAIGUSWI.
  (2) R-MAP RUNNER `src/research/rmap.py` (MPYA): events 21 (EVENTS_V2 zote — needs hour/tc zapatikana)
      x pairs 12 x TF {H1,H4,D1} x SL{1,1.5,2} x TP{1,1.5,2,3} x max_hold{H1:24,H4:24,D1:20}. Kila
      trade TAGGED (signal-bar): vol_state, session (_sess(hour[i])), d1_trend_sign (ctx kama ipo),
      mwaka wa entry. Output data/strategies/rmap_train.parquet (mstari 1 kwa CELL×MWAKA×VOL_STATE:
      event,pair,tf,sl,tp,year,vol_state,n,ev_net(swing),gross,win,cost_share + MFE/MAE cols +
      d1_align_frac,sess_top). reports/rmap_atlas.md: top-20 (event×tf×vol_state) kwa BREADTH ya pairs
      (L-041 — si cell moja) + per-event breadth. GUARD TRAIN-only (PermissionError); HAKUNA FDR (ramani,
      si test).
  (3) MFE/MAE helper `excursions(trades,o,h,l,c,out,entry,atr,sl_atr)` (rmap.py): MFE/MAE kwa pips NA R
      (÷ sl_atr*atr[signal bar]) + mfe_peak_bar. Entry price = ILE ILE ya episodes (market o[i+1];
      stop max/min(level,open)). parquet cols: mfe_r_med, mae_r_med, mfe_peak_bar_med, timeout_mfe_r_med.
  · SHERIA: ZERO statistic/golden fns (episodes/pvalue_boot/_mask_context/wave_c2a byte-identical;
    golden diff 0). run_selftests += rmap. Files: data_config.yaml + run_selftests.py + rmap.py(mpya).
  Self-test rmap [1]-[6]: swap-nights (0/3, det), MFE/MAE exactness (market+stop entry), TRAIN-guard
    (valid/holdout refused), full-run (schema/years/vol/swap-drag/determinism/outputs), usable_events 21.
    SWEEP 27/27 PASS. RUNTIME kadirio: ~5 min full 12 pairs (1 pair=23s synthetic; sio overnight).
NEXT AFTER: Operator: `python src/research/rmap.py --train` -> rmap_train.parquet + rmap_atlas.md ->
  commit+push. Kisha M3-3: Chief+STRATEGIST-M soma atlas -> hypotheses zenye breadth -> S2 pooled.
OPEN QUESTIONS / NOTES:
  - Swap symmetric (long/short sawa) — refine ikiwa broker swap-table itapatikana (asymmetric carry).
  - Atlas group-key = vol_state (schema ya charter); session/d1-trend zimehifadhiwa kama summary cols
    (sess_top, d1_align_frac) — si group-axis (kuepuka row-explosion). H4/D1: h4-trend NaN (ctx ya HTF
    haijengwi kwa H4/D1 LTF) -> d1_align_frac None kwa TF hizo (additive, si kosa).

=== M3-4 build (2026-07-16) — MZUNGUKO-3 TABAKA-3 — IMEKAMILIKA ===
LAST COMPLETED: **K4 training dataset builder** ✅ (docs/CYCLE3_CHARTER.md §Tabaka-3; src/research/k4_dataset.py MPYA):
  Kwa kila split {train,validation} × strategy {STRAT-001 USDCHF SL2/TP1, STRAT-002 USDJPY SL1/TP1}:
  pipeline HASA ya proven (nr7_break + _mask_context('no-LATE') + episodes, max_hold default 24 —
  outcomes zinalingana na STRAT-001/002). Kwa KILA TRADE, row moja:
  - features za SIGNAL bar (decidable): vol_state, activity_state, spread_state (kutoka state parquet,
    aligned+assert ts), session_entry(_sess(hour[entry])), hour(signal), dow, atr_pips, atr_n,
    range_nr7_atr((h-l)/atr), h4_*/d1_* zote za ctx (kama H1 context ipo), mwaka(signal).
  - outcome: pnl_pips, pnl_R(pnl/(sl*atr)), win, exit_type(TP/SL/timeout, tie->SL kama episodes),
    bars_held, mfe_r/mae_r/mfe_peak_bar (rmap.excursions).
  OUTPUT: data/strategies/k4_dataset.parquet + reports/k4_dataset.md (counts+win_rate baseline+EV,
  exit-type dist, feature NaN% completeness — curriculum gate §M3-QA).
  · HOLDOUT HAIGUSWI: splits {train,validation} PEKEE (PermissionError vinginevyo) + HARD assert
    max(ts) < 2025 (RED LINE, hata 'validation' yenye leak inakataliwa).
  · SHERIA: ZERO golden fns (episodes/_mask_context/nr7_break byte-identical; golden diff 0). REUSE
    _mask_context (no-LATE proven) + rmap.excursions (MFE/MAE). run_selftests += k4_dataset.
  Self-test [1]-[5]: HOLDOUT-guard (holdout/mixed refused), RED-LINE ts>=2025 refuse, decidability
    EXACT (vol_state==vol[signal i], si entry i+1 — trap), full build (schema/splits/strat/no-holdout/
    exit/ctx/determinism/outputs), exit_type correctness (TP/SL/timeout). SWEEP 28/28 PASS.
  BASELINE win rates (rejea, proven registry holdout): STRAT-001 73.9%, STRAT-002 57.8%. TRAIN/VALID
  halisi = Operator's `--build` run (data PC).
NEXT AFTER: Operator: `python src/research/k4_dataset.py --build` -> k4_dataset.parquet + report ->
  commit+push. Kisha M3-QA: SCIENTIST-D certify dataset (label integrity/leakage/balance/coverage)
  KABLA ya M3-5 (SCIENTIST-D design model p(win|state)).
OPEN QUESTIONS / NOTES:
  - ctx (h4_/d1_) inahitaji htf_context --ltf H1 iwe imejengwa; ikikosekana -> ctx cols None (additive).
  - Baseline win_rate ya TRAIN/VALID (ndani ya dataset) inaweza kutofautiana kidogo na holdout provenance
    (window tofauti) — hii ni sawa; curriculum inahitaji per-regime N + mwaka-coverage (report ina hizo).

=== M3-FIX (2026-07-17) — certification audit fixes — IMEKAMILIKA ===
LAST COMPLETED: **M3-FIX** ✅ (reports/m3_curriculum_audit.md §A/§C; Chief ameidhinisha; deterministic, hakuna re-research):
  K4 (k4_dataset.py):
  - K-1: `ts_entry` (ISO str ya ts[entry_bar]) + `entry_bar` (int) kwenye kila row -> time-aware/blocked CV.
  - K-2: MANIFEST rasmi top-level: `FEATURES` (decidable signal-bar: base 9 + ctx 18), `OUTCOMES`
    (pnl_*/win/exit_type/bars_held/mfe_*/mae_*/mfe_peak_bar), `META` (identifiers incl year/dir/ts_entry).
    `load_k4(features_only=True)` -> (X,y) + ASSERT hakuna OUTCOMES ndani ya X (trap ya leak #1). Report
    inaandika FEATURES+OUTCOMES.
  - K-3: `atr_n` IMEONDOLEWA (100% NaN — state parquet haiihifadhi); badala yake `atr_rel` =
    atr/rolling_median(atr,60 PAST bars,shift(1)) — relative vol level, no-lookahead (self-test trap).
  - K-4: string "None"/"null"/"nan" (htf warmup null-cast) -> null halisi kwenye ctx state-cols.
  - K-5: report inaorodhesha cells N<30 "hazifundishiki" (§Q6 quarantine) + notes VALID-taint(§D1) + DST(§C5).
  ATLAS (rmap.py) A-1:
  - Breadth Top-20 + columns "miaka EV+ /present" + "median N"; rank kwa (breadth, years_pos).
  - Q1: vol_state=UNKNOWN (=2016 warmup) HAIMO kwenye ranking-tables za report (ipo kwenye parquet — data).
  - Notes: Q2 (D1 sess_top='ASIA' artifact), Q3/Q5 (row!=lesson, MFE-SL inflate), lesson-generator isome PARQUET.
  · SHERIA: ZERO statistic/golden fns (episodes/pvalue_boot/_mask_context/nr7_break byte-identical; golden 0).
    Files: k4_dataset.py + rmap.py TU. Self-test k4 [1]-[9] (+manifest-assert, ts_entry monotonic, atr_rel
    trap, K-4 null); rmap [1]-[7] (+UNKNOWN nje ya ranking, columns miaka/median-N). SWEEP 28/28 PASS.
NEXT AFTER: Operator: `python src/research/k4_dataset.py --build` + `python src/research/rmap.py --train`
  (dakika) -> commit+push -> "tayari M3 rebuilds" -> M3-5 GO (SCIENTIST-D design model p(win|state)).
OPEN QUESTIONS / NOTES:
  - M3-5 loader itumie k4_dataset.load_k4() (manifest-asserted) + blocked-CV (ts_entry, purge bars 24, §D3).
  - atr_rel warmup (bars < 60) = NaN by design (no-lookahead); rows za mwanzo wa TRAIN zinaweza kuwa None.

=== M3-3-S2 build (2026-07-17) — SWING FAMILY #1 S2 runner — IMEKAMILIKA ===
LAST COMPLETED: **swing_family.py S2 VALIDATION runner** ✅ (docs/M3_SWING_FAMILY_REGISTRATION.md; MPYA, additive):
  FAMILY FROZEN: nr7_break × D1 × vol=LOW (signal-bar; UNKNOWN excluded Q1) × SL2.0/TP1.0 × hold20,
  pairs ZOTE 12 pooled kwa R (L-041, gold haitawali — R-units). run_s2(split="validation"):
  kwa kila pair: load_window(D1) -> nr7_break -> _mask_context(vf="LOW") -> episodes -> apply_swap
  (rmap, swing carry) -> _r_normalize (pnl_swing) -> pool_streams (ts ordering + dedup AT7) ->
  pvalue_boot(B=50k, mean_block=3, seed=20260717 FIXED) -> criterion p<0.05 NA EV_R>0 (m=1). p_z sens.
  GUARD: validation PEKEE (PermissionError); pair bila data -> RuntimeError (F2: pairs 12 LAZIMA,
  hakuna silent skip). OUTPUT: data/strategies/swing_family_s2.jsonl (per-pair n/ev_R + pooled row) +
  reports/swing_family_s2.md (VERDICT WAZI: PASS->C2-6/HOLDOUT->STRAT-003; FAIL->LESSON/forward-only).
  · SHERIA: ZERO statistic fns (pvalue_boot/pool_streams/_r_normalize/episodes/_mask_context imports TU;
    golden diff 0). Spec FROZEN (param 1, pairs 12, vol LOW). run_selftests += swing_family.
  Self-test [1]-[5]: guard (train/holdout refused), F2 pair-missing->RuntimeError, vol=LOW decidability
    (signal-bar EXACT + UNKNOWN nje), swap-drag (EV_R swap < no-swap), full-run (determinism + gold
    R-normalized haitawali (atr×100 -> EV_R oda ile ile) + verdict + outputs). SWEEP 29/29 PASS.
NEXT AFTER: Operator: `python src/research/swing_family.py --validate` -> swing_family_s2.md (VERDICT).
  PASS -> C2-6 freeze + HOLDOUT one-shot (token) -> STRAT-003. FAIL -> LESSON (N_valid ~110, power wastani).
OPEN QUESTIONS / NOTES:
  - _r_normalize is_timeout tag inatumia hardcoded 24 (H4 design ya family_pooled) si max_hold 20 —
    ni TAG ya sensitivity tu, HAIATHIRI pnl_R wala verdict (fn imetumika kama ilivyo, ZERO stat touched).
  - Swap band (Q7): symmetric, hakuna weekend-triple/rate-diff sign — R-pooling + per-pair EVs kubwa
    zinapunguza athari; registration inakiri hili.

=== M3-5 build (2026-07-17) — K4 MODEL v0 — IMEKAMILIKA ===
LAST COMPLETED: **k4_model.py (K4 entry-quality model v0)** ✅ (BUILD ya reports/k4_model_design.md — design=SPEC):
  Per-strategy (STRAT-001/002, hakuna pooling): PRIMARY L2-logistic, CHALLENGER shallow tree (depth<=3,
  min_leaf>=100). BLOCKED leave-one-year-out CV (folds 7, purge 24h), grid 16, prune-once, FREEZE.
  Decision = ΔEV_R@70% (SI accuracy/AUC). Metrics M1-M4 + block-bootstrap CI (utility MPYA, mb=3 B=10k
  — SI pvalue_boot). H0 criterion §4 (dev>0 & p<0.05 & dev>=+0.05R & ev-ret>=0.90). p* TRAIN-CV pekee.
  · IMPLEMENTATION NOTE (si deviation ya kimaudhui): sklearn HAIPO env -> L2-logistic (convex, optimum
    mmoja) imetekelezwa kwa IRLS/Newton pure-numpy = coefs zilezile za lbfgs; tree = CART greedy
    deterministic. Artifact = JSON (HAKUNA pickle) kama design inavyotaka. Sweep portable.
  CLI: --cv (grid+prune+report) / --freeze (JSON artifact + dataset hash) / --eval-valid (one-shot,
    inasoma p* kutoka freeze, inakagua hash) / --self-test.
  · SHERIA: ZERO golden/statistic fns za research (load_k4 assert ya k4_dataset inatumika kama ilivyo;
    pvalue_boot/pool_streams n.k. HAZIGUSWI). --cv inakataa rows za validation (AT3 PermissionError).
  Self-test AT1-AT7 ZOTE PASS: leak-trap (no OUTCOMES kwenye FS), blocked-CV correctness (fold=mwaka,
    purge clean, oof cover), no-VALID-tuning guard, metric exactness (closed-form), determinism,
    planted-signal detect (AUC 0.67) + null sanity (MC), threshold-freeze (pstar kutoka artifact).
    Duration ~15s. SWEEP 30/30 PASS.
  Deliverables: k4_model.py + docs/K4_MODEL_REGISTRATION.md (criterion §4 verbatim kwa Chief). Report
    (reports/k4_model_report.md) inazalishwa na --cv run ya Operator (data PC).
NEXT AFTER: Operator: `python src/research/k4_model.py --cv` (dakika) -> Chief anasoma report + H0 verdict.
  CV-PASS -> Chief ruling -> --freeze -> commit -> --eval-valid (MOJA). CV-FAIL -> LESSON, hakuna filter.
OPEN QUESTIONS / NOTES:
  - Matarajio (design, imefungwa): max single-feature AUC 0.532 -> lift ndogo au H0 kubaki inawezekana
    zaidi; verdict yoyote (ikiwemo NO-LIFT) ni ujuzi wa curriculum, si kushindwa.
  - sklearn parity: kama Operator anataka lbfgs halisi, inaweza kubadili _fit_config kutumia sklearn
    (convex -> matokeo yanafanana); pure-numpy imechaguliwa kwa portability ya sweep + determinism.

=== M-DASH build (2026-07-20) — THE GLASS BOX dashboard — IMEKAMILIKA ===
LAST COMPLETED: **Django monitoring dashboard KAMILI** ✅ (docs/DASHBOARD_CHARTER.md; dir MPYA `dashboard/`
  — src/research HAIJAGUSWA, diff = dashboard/ tu):
  · Setup: project elitefx_dash + app monitor; SQLite (Postgres-ready); REPO_ROOT/paths/secret kupitia env
    (HAKUNA secret repo). Dark institutional theme (style.css moja, monospace kwa namba).
  · DB models 12 + Lease (mirror ya artifacts, SI logic): Trade, DecisionTrace, ComplianceCheck,
    StrategyPerf, ModelVersion, PairStrategyCell, VpsHeartbeat, Alert, Report, LedgerEntry, Lesson,
    AuditEvent (append-only — save/delete update inakataa). KILA moja + source_ref + is_demo (glass-box).
  · Ingest (manage.py ingest [--demo]): read-only loaders — paper_log.jsonl (decision/execution/settlement
    -> Trade+trace+checks), MODEL_REGISTRY.md (+promised EV regex), EXPERIMENT_LEDGER.md, reports/*.md
    (+archive), lessons 42, rmap parquet (polars, aggregation event×pair) AU pair_strategy.jsonl,
    alerts.jsonl (env), heartbeat.json (env), StrategyPerf derived. Artifact haipo -> "no data" (KAMWE
    kubuni). IDEMPOTENT (natural keys). REAL ingest imethibitishwa: registry 3, ledger 13, reports 98,
    lessons 42, cells 252 (rmap halisi); paper/alerts/hb = "no data" waaminifu.
  · Panels 9 ZOTE (read-only, @require_GET): Command Deck (status banner OPERATIONAL/DEGRADED/NO-DATA +
    KPI + sparkline + ticker), Portfolio (equity + per-strategy + monthly heatmap mwaka×mwezi + toggle),
    Live Actions (blotter + decision-trace expandable + per-trade compliance badges), Trust/Compliance
    (score kubwa + gauges per rule + violations nyekundu), Model Registry (cards + lifecycle timeline +
    LIVE-vs-PROMISED overlay na shrinkage band 0.35-0.5x + degradation flag + ATTESTATION export
    JSON/HTML/PDF na SHA-256 hash reproducible), Pair×Strategy heatmap (drill-down + lessons),
    Diagnosis/Alerts, VPS Health (freshness per pair), Ledger+Lessons+Reports browser (md viewer salama).
  · Roles (leasing foundation V2 §5.4): groups internal/attestor/lessee + Lease model; decorators
    panel_access/model_access; lessee = model MOJA aliyokodishwa + attestation yake TU; AuditEvent
    inarekodi attestation views (append-only). bootstrap_roles --demo-users.
  · Demo fixtures (monitor/fixtures/, format ILEILE ya artifacts halisi -> loaders zilezile zinajaribiwa):
    paper_log 10 trades (1 violation ya demo), registry/ledger/reports/lessons, pair_strategy 24,
    alerts 3, heartbeat. is_demo=True + demo banner WAZI kwenye UI.
  · TESTS 9/9 GREEN (`python dashboard/manage.py test`): (a) ingest correctness + idempotent;
    (b) no-fabrication (artifact tupu -> 0 + panels "no data" 200); (c) read-only (POST->405 kila panel,
    hakuna trade-mutation, smoke 200 panels zote + drill-downs); (d) attestation hash stable +
    sensitivity + audit append-only; (e) role access (lessee-scoped 403s, attestor scope, anon->login).
  · DEVIATION-with-reason (documented kwenye glasschart.js): Chart.js file haikuweza ku-vendor (proxy
    403 kwa CDN kwenye env ya build) -> glasschart.js (canvas lib ndogo self-contained, HAKUNA CDN —
    line+band+sparkline). Operator anaweza ku-vendor chart.umd.min.js baadaye; templates zinatumia gc.*.
  · Research sweep 30/30 PASS (src/research byte-untouched).
RUNBOOK: pip install -r dashboard/requirements.txt && cd dashboard && python manage.py migrate &&
  python manage.py ingest --demo && python manage.py bootstrap_roles --demo-users &&
  python manage.py runserver  -> login internal-demo/internal-demo. Real data: python manage.py ingest.
NEXT AFTER: M-DASH-QA (audit ya Chief/SCIENTIST-D); VPS agent kuandika heartbeat.json; monitors
  kuandika alerts.jsonl; paper_trader run halisi -> paper_log.jsonl -> panels zote live.

=== M-DASH-FIX (2026-07-20) — audit findings F1-F7 — IMEKAMILIKA ===
LAST COMPLETED: **M-DASH-FIX** ✅ (reports/mdash_audit.md §FINDINGS; Chief ameidhinisha; diff = dashboard/ tu):
  F1 (MEDIUM): AuditEvent += AppendOnlyQuerySet — QuerySet.update()/delete()/bulk_update() zinaraise
    ValueError (bulk ops hazipiti Model.save()); immutability sasa instance+queryset level. (DB-level
    grant-revoke = prod deployment note, documented kwenye docstring.)
  F2 (MEDIUM): unit-mix imeondolewa — rebuild_strategy_perf + views._equity_series zinatumia `pnl_r`
    PEKEE kwa R-metrics; closed trades bila pnl_r zime-exclude + kuripotiwa kwenye ingest note
    ("N bila pnl_r zimeachwa nje"). Hakuna currency ndani ya R kamwe.
  F3 (LOW-MED): _dt hardened (garbage->None); load_alerts/load_heartbeat HAZIWEKI now() — ts=None +
    "[invalid/missing ts]" tag / ingest note; Alert.ts+VpsHeartbeat.ts sasa nullable (migration 0002);
    _system_status: hb.ts None -> DEGRADED (SI OPERATIONAL); templates deck/vps zinaonyesha "ts batili".
  F4 (LOW): registry parser _ROW6 + _ROW5 — WATCH table (5 col: id|class|status|signal|njia) ina-parse;
    real ingest sasa models 6 (STRAT-001/002, K4-filter + C2/SWING/K4-WATCH version='watch').
  F5 (LOW): _read_jsonl -> (rows, n_bad) skip+note kwa JSON mbovu (paper_log/pair_strategy/alerts);
    load_heartbeat JSON mbovu -> (0, "invalid json...") — hakuna crash.
  F6 (LOW): attest.build_payload += repo_commit (git rev-parse HEAD ya REPO_ROOT; fallback 'unknown')
    NDANI ya hashed payload — auditor wa nje ana-pin repo state.
  F7 (INFO): settings fail-closed — DEBUG default 0; DEBUG=0 bila ELITEFX_SECRET_KEY -> ImproperlyConfigured.
    RUNBOOK UPDATE: dev/demo sasa inahitaji `export ELITEFX_DEBUG=1` (au weka ELITEFX_SECRET_KEY).
  · TESTS 15/15 GREEN (9 za awali + AuditFixTests F1-F6 — repro za auditor kama tests). Repro scripts
    za auditor zimeendeshwa: adversarial.py — P1 skip-note, P2 fabricated-now?=False, P3 probe EXC
    (ts=None halali — fix inafanya kazi), P4 net_r=1.0 (no mix), P6/P6b blocked, P7 hash match,
    P8 repo_commit present; http_probe.py — 405/404/403 zote sahihi, hakuna cross-leak.
  · READ-ONLY + NO-FABRICATION intact (F3 inaziimarisha). src/research HAIJAGUSWA.
NEXT AFTER: Chief update MODEL_REGISTRY/DOCTRINE -> matumizi ya wateja/leasing yameruhusiwa (audit §RUHUSA:
  F1+F2+F3 done = lessee-access unblocked; F6+F7 done = prod-deploy note cleared).

=== LIVE-ENGINE build (2026-07-21) — LIVE PAPER ENGINE — IMEKAMILIKA ===
LAST COMPLETED: **live_engine.py (AI inayoendesha forward, paper)** ✅ (docs/LIVE_ENGINE_CHARTER.md; WIRING ya modules):
  Forward loop (replay validation; HOLDOUT HAIGUSWI) kwa STRAT-001 (USDCHF SL2/TP1) + STRAT-002
  (USDJPY SL1/TP1) no-LATE H1: STATE -> nr7_break SIGNAL -> DECISION (decision_engine.decide +
  STRAT_POLICY SELECT) -> SIZE (broker_adapter.size DailyRiskBudgetSizer, ftmo_config.yaml +
  data_config max_spread) -> COMPLIANCE (integrity_gate.gate + build_constraints 5) -> EXECUTE
  (mode=paper, execution_object.record) -> LOG (decision_repository.append paper_log.jsonl).
  · WIRING PEKEE — ZERO golden/statistic/fill fns mpya: honest fills/costs = episodes (byte-identical;
    forward loop = replay ya episodes-candidates kwa ts order — episodes yenyewe no-look-ahead).
    no-LATE = _mask_context (proven). entry_px/exit_px derived kutoka episodes pnl (hakuna fill mpya).
  · LOG schema inalingana HASA na dashboard/monitor/loaders.py: records decision(signal: aggregate)/
    decision(gate: eligibility.passed+failed)/execution(order_id,pair,side,qty,entry,sl,tp,status,
    as_of,mode=paper,+learned_ev/spread/slippage)/settlement(id=order_id,realized_pnl,pnl_r,exit_price).
    REJECTED trades zime-log (execution status=REJECTED + reject_reason) -> zinaonekana Live Actions.
  · mode=paper PEKEE (broker_adapter Q1 live=refuse-stub HAIBADILISHWI). STRAT configs HAZIBADILIKI.
    Append-only. learned_ev tag (STRAT-001 +1.92, STRAT-002 +2.65) kwa STEWARD divergence (§8.2, baadaye).
  Self-test [a]-[f]: no-look-ahead (nr7 level truncation-inv), forward determinism (bit-identical),
    log schema round-trip (kinds+keys+linked closed==filled), compliance-veto (max_daily_loss ndogo ->
    REJECTED + logged reason, hakuna settlement), sizer budget=0 -> qty=0 (hakuna trade), mode=paper.
    SWEEP 31/31 PASS. ROUND-TRIP HALISI (Django loader): engine log -> 44 Trades (5 CLOSED/39 REJECTED),
    137 DecisionTrace, 220 ComplianceCheck, strategies mapped, pnl_r+mode=paper. (Synthetic random ->
    total_dd $1000 inasimamisha trading = capital protection SAHIHI; data halisi ya proven-EV = fill juu.)
RUNBOOK: python src/research/live_engine.py --run [--split validation]  -> data/paper/paper_log.jsonl
  (append-only). Kisha dashboard: cd dashboard && ELITEFX_DEBUG=1 python manage.py ingest (BILA --demo)
  -> Live Actions + Compliance + Portfolio panels zinaonyesha trades HALISI za AI.
NEXT AFTER: Operator: --run kwenye forward/validation data -> ingest -> dashboard live. MODEL STEWARD
  (§8.2) = mzunguko ujao (learned_ev tag tayari ipo kwa divergence). MT5 adapter (§8.3) = baadaye.

=== MODEL-STEWARD build (2026-07-22) — meta-model READ-ONLY — IMEKAMILIKA ===
LAST COMPLETED: **model_steward.py (MODEL STEWARD — mwalimu wa models)** ✅ (docs/MODEL_STEWARD_CHARTER.md; V2 §8.2):
  META-MODEL READ-ONLY: inasoma data/paper/paper_log.jsonl (link exec+settle kwa order_id) -> per
  model (STRAT-001/002) realized R + learned_ev tag. PRACTICAL vs LEARNED (pips — unit sawa na
  learned_ev): practical mean + bootstrap CI (REUSE family_pooled._boot_ci, seeded) dhidi ya
  learned_ev -> verdict HOLDS/SHRINKS/LIFTS/INSUFFICIENT.
  WEAKNESS MAP (per model × dim): session (_sess kutoka as_of) / vol (atr_rel proxy = |entry-sl|/
  sl_atr, terciles) / streak (FRESH/AFTER_WIN/AFTER_LOSS/AFTER_2L+) / cost-drag ((spread+slip)/gross,
  median-split). Kila cell {N, mean, CI, divergence, verdict}; N<min_n(30) -> INSUFFICIENT (anti-noise).
  AGENDA ranked (|divergence|×N): weakness + hypothesis (lugha ya trade) + proposed experiment
  (registration ya kawaida — SI auto-apply) + risk. + regime DATA-GAP item (regime haijalog na engine).
  OUTPUT: reports/model_steward.md [(A) practical-vs-learned; (B) weakness map; (C) agenda; (D)
  SAMPLE-HONESTY + provenance commit+lines+sha+tarehe] + .json (malighafi ya panel MODEL HEALTH V2).
  · SHERIA: READ-ONLY KWELI (reports/ PEKEE — log/registry/configs HAZIGUSWI). ZERO golden fns
    (import _boot_ci/_sess tu; regex-check haina def episodes/pvalue/_boot_ci). HAKUNA "best cell=
    strategy" (L-041 — diagnostics si discovery). SAMPLE-HONESTY: practical=replay/validation, SI forward.
  Self-test [a]-[f]+: read-only (log hash 2-run sawa), determinism (bootstrap seeded), anti-noise
    (N<30->INSUFFICIENT), verdict-logic (learned high/mid/low -> SHRINKS/HOLDS/LIFTS), provenance
    (commit+lines au fail), honesty-tag (au fail), no-data (log haipo->models={}), no-golden-touch.
    SWEEP 32/32 PASS. Sampuli (synthetic N=20-24<min_n): zote INSUFFICIENT (anti-noise SAHIHI).
RUNBOOK: live_engine --run -> paper_log.jsonl; kisha `python src/research/model_steward.py`
  -> reports/model_steward.{md,json}. Zoezi endelevu: kila forward data mpya -> update ramani+ajenda.
NEXT AFTER: Dashboard-V2 panel MODEL HEALTH inasoma model_steward.json (§8.2). Chief/PD wanachagua
  majaribio kutoka agenda kupitia registration. Regime weakness-map inahitaji engine i-log regime tag.
OPEN QUESTIONS / NOTES:
  - practical-vs-learned kwa PIPS (learned_ev native unit); mean_R (unit-free) ni secondary kwa cross-model.
  - Power ndogo bado (validation replay, N<min_n per cell) -> verdicts INSUFFICIENT hadi forward data ikue.

=== STEWARD-FIX v0.2 (2026-07-22) — cost dimension outcome-conditioning — IMEKAMILIKA ===
LAST COMPLETED: **STEWARD-FIX** ✅ (docs/lessons/LESSON-043; surgical — dimension MOJA):
  KASORO (v0): _cost_bucket ilitumia `drag=(spread+slippage)/(|pnl_pips|+cost)` median-split ->
  pnl_pips ni MATOKEO -> OUTCOME-CONDITIONING -> cells za uongo (STRAT-001 HIGH-DRAG CI ultra-tight
  [8.164,8.566], LOW-DRAG "SHRINKS" -2.211 = artifact ya magnitude-split, si udhaifu).
  FIX (v0.2): _cost_bucket sasa EX-ANTE absolute cost: `cost_pips = spread + slippage` (inajulikana
  wakati wa entry, HAKUNA pnl) -> tercile NDANI ya model -> LOW-COST/MID-COST/HIGH-COST (muundo wa
  _vol_bucket). weakness_map "cost" inatumia labels mpya; _HYP["cost"] ibaki (actionable: epuka
  HIGH-COST entries kabla ya trade). Dimensions nyingine (session/vol/streak) = ex-ante -> ZIBAKI.
  · Self-test [h] MPYA: pnl-flip (×-7.3) HAKUBADILISHI cost-bucket (ex-ante invariance); labels =
    {LOW/MID/HIGH-COST}, hakuna -DRAG. [a]-[g] za awali GREEN. SWEEP 32/32. ZERO golden fns (surgical).
  DEMO kabla-vs-baada: KABLA drag-split HIGH=+0.4 SHRINKS / LOW=+5.4 LIFTS (magnitude artifact);
  BAADA cost-tercile cells zote ~2.4-3.3 (mean ya jumla), CI kawaida, hakuna SHRINKS ya uongo.
  · Agenda #1 ya v0 (cost=LOW-DRAG SHRINKS) IMEKATALIWA (artifact). STRAT-001/002 = HOLDS (headline sahihi).
NEXT AFTER: Chief athibitishe artifact imeondoka (weakness-map ya cost sasa ex-ante). Kanuni L-043:
  kila dimension ya diagnostics LAZIMA iwe ex-ante (mwalimu naye curriculum yake i-certify — GIGO).

=== DASH-V2-A1 build (2026-07-23) — MODEL SCORECARD (Awamu 1, INTERNAL) — IMEKAMILIKA ===
LAST COMPLETED: **Dashboard-V2 Awamu 1: MODEL SCORECARD** ✅ (docs/DASHBOARD_V2_DESIGN.md §3 A-G; additive, dashboard/ tu):
  1. monitor/callsigns.py: CALLSIGNS {STRAT-001:KAIROS-1, STRAT-002:KAIROS-2} + to_public/to_internal/
     public_meta. PUBLIC_META (call-sign->{version,status}) BILA pair/logic/params (anonymization §9, msingi wa Awamu 3).
  2. loaders.load_steward(reports_dir): soma reports/model_steward.json (READ-ONLY, si DB ingest — view
     inasoma live). Fail-soft: haipo/mbovu -> ({}, note).
  3. monitor/language.py: say(topic,...) -> sentensi fupi (trade+English) kwa status/promise/weakness/
     compliance. DETERMINISTIC (input sawa -> output sawa).
  4. Views (INTERNAL tu, PANEL_ROLES["scorecards"]={"internal"}): /scorecards/ (list: call-sign +
     status-light HOLDS/LIFTS=green, SHRINKS=red, INSUFFICIENT/no-data=yellow + sentensi);
     /scorecards/<call_sign>/ (detail A-G: A STATUS BAND, B AHADI vs UHALISIA + shrinkage bar, C MAAMUZI
     YA SASA open+trace, D MAAMUZI YA NYUMA closed history + kwanini + sheria, E RAMANI YA UDHAIFU
     weakness_map kwa rangi, F SHERIA rejected+sababu, G MWENENDO equity curve gc.line). call_sign kwenye
     URL -> to_internal server-side; bad call-sign -> 404.
  5. context.py nav += SCORECARDS; access PANEL_ROLES += scorecards; templates scorecards_list.html +
     scorecard_detail.html (rithi base.html); style.css += status-lights + weakness cells + shrinkbar.
  · SHERIA: READ-ONLY (GET pekee, POST->405). REUSE loaders (load_paper_log/registry mirror + load_steward
    mpya). Fail-soft steward/paper_log haipo -> "no data". INTERNAL tu (lessee/attestor->403; Awamu 3=lessee).
    F7/append-only/attestation HAZIJAGUSWA. src/research byte-untouched (sweep 32/32 PASS).
  Tests (21/21 GREEN; 6 mpya): callsign round-trip + PUBLIC_META haina pair-leak; load_steward fail-soft;
    status-light mapping; scorecard detail 200 internal / 404 bad-callsign / 403 lessee+attestor / 302 anon /
    405 POST; language.say deterministic. End-to-end: KAIROS-1 green/HOLDS, KAIROS-2 red/SHRINKS, A-G zote.
RUNBOOK: live_engine --run -> paper_log; ingest (bila --demo); model_steward.py -> model_steward.json;
  kisha login internal -> /scorecards/ -> bofya KAIROS-1/2 kwa scorecard kamili A-G.
NEXT AFTER: Awamu 2 (OVERVIEW roll-up ya scorecards); Awamu 3 (LESSEE view — reuse scorecard + anonymize
  call-sign + hide pair/IP + token). callsigns.py = msingi tayari.
OPEN QUESTIONS / NOTES:
  - Scorecard inasoma steward.json LIVE (si DB) — inasasishwa kila model_steward.py inavyoendeshwa. Demo
    scorecards zinahitaji reports_dir yenye model_steward.json (Operator aendeshe steward kwanza).

=== DASH-V2-A2 build (2026-07-23) — OVERVIEW: FLEET status-lights kwenye COMMAND DECK — IMEKAMILIKA ===
LAST COMPLETED: **Dashboard-V2 Awamu 2: OVERVIEW / FLEET** ✅ (docs/DASHBOARD_V2_DESIGN.md §4; additive, dashboard/ tu):
  · COMMAND DECK iliyopo (/deck/, INTERNAL) imekuzwa kuwa "taasisi kwa jicho moja": FLEET ya models kwa
    status-lights juu ya equity/actions. Panels zote za zamani (equity KPIs, sparkline, today's actions,
    active models) ZIMEBAKI kama zilivyo.
  1. views.command_deck: REUSE helpers za Awamu 1 (_steward_models/_scorecard_summary/_status_light — SI
     overview mpya). ids = CALLSIGNS ∪ steward-models ∪ Trade.strategy; fleet = _scorecard_summary(i) kwa
     kila i ndani ya CALLSIGNS au smodels; tally {green/yellow/red}; steward_note fail-soft;
     alerts_count/alerts_recent; demo flag. Context mpya: fleet, fleet_tally, steward_note, alerts_count.
  2. deck.html: section "FLEET — MODELS KWA JICHO MOJA" juu ya grid g4 — cards (light + call-sign +
     meta.version/status + sentensi + verdict/closed), link -> /scorecards/<call_sign>/; summary
     "🟢 X · 🟡 Y · 🔴 Z · alerts N"; steward-note banner ikiwa model_steward.json haipo; else "no data".
  · SHERIA: READ-ONLY mirror (GET pekee). Deck role/access HAIJABADILIKA (INTERNAL tu). Hakuna chart-lib
     mpya. F7/append-only/attestation HAZIJAGUSWA. src/research byte-untouched (sweep 32/32 PASS; golden fns
     episodes/pvalue_boot/_mask_context/pool_streams/_r_normalize/nr7_break = 0 lines diff).
  Tests (25/25 GREEN; 4 mpya DeckFleetTests): (a) deck ina fleet cards zenye call-sign + link /scorecards/<cs>/;
    (b) fleet tally sahihi (🟢1 KAIROS-1 HOLDS · 🔴1 KAIROS-2 SHRINKS · 🟡0); (c) deck INTERNAL tu
    (anon->302, lessee->403, attestor->403); (d) fail-soft bila steward.json (deck 200, KAIROS-1 present,
    "Steward:" note, green 0 / red 0 — lights = NO-DATA yellow).
RUNBOOK: login internal -> /deck/ -> ona FLEET rollup juu; bofya card -> /scorecards/<call_sign>/ (Awamu 1).
NEXT AFTER: Awamu 3 (LESSEE view — reuse scorecard + anonymize call-sign + hide pair/IP + token).

=== DASH-V2-A3 build (2026-07-24) — LESSEE VIEW (anonymized MY MODELS, IP-protection) — IMEKAMILIKA ===
LAST COMPLETED: **Dashboard-V2 Awamu 3: LESSEE VIEW** ✅ (docs/DASHBOARD_V2_DESIGN.md §1/§3/§7 + DOCTRINE_V2 §9;
  additive, dashboard/ tu). Mteja anaona scorecard za models ALIZOKODI TU, kwa CALL-SIGN (KAIROS-x),
  ANONYMIZED KIKAMILIFU. KANUNI KUU (IP §9): lessee HAONI KAMWE pair (USDCHF/USDJPY), internal id
  (STRAT-001/002), logic/params/features, wala models za wengine.
  1. access.lessee_can_see(user, call_sign): internal/attestor = call-signs zote; lessee = to_internal
     (call_sign) IKIWA ndani ya user_leases zake TU; vinginevyo PermissionDenied (403). Mapping ni
     server-side (haipiti kwa client).
  2. views._lessee_scorecard(call_sign): REUSE hesabu za A-G (steward + Trade mirror) LAKINI rudisha
     fields ANONYMIZED PEKEE — call-sign, public_meta(version/status), light+sentensi, learned vs
     practical, weakness_map (dims salama: session/vol/streak/cost — pair-dim ikitokea INAONDOLEWA),
     compliance rollup, equity series (R). Section D = list ya dict {date, dir, R, result, reason, rules}
     BILA pair/internal id/record_id. reason = hatua (signal→gate→fill) — SI record_id (record_id huvuja
     pair). _lessee_card(): muhtasari wa list bila internal id. DEFENCE-IN-DEPTH: context HAINA Trade mbichi.
  3. Views+urls: /my/ (lessee_list — leases zake->to_public; internal/attestor=zote QA) + /my/<call_sign>/
     (lessee_detail — to_internal->404 kama haipo; lessee_can_see->403; _lessee_scorecard; AuditEvent append).
     lessee_home: lessee-branch -> lessee_list (SI lessee.html ya zamani iliyokuwa inavuja STRAT-xxx).
     Templates MPYA: scorecard_lessee_list.html + scorecard_lessee.html (A-G rahisi, HAKUNA pair/id column).
  4. context.nav: is_lessee -> nav_panels = [("my","/my/","MY MODELS")] TU. base.html nav = loop ya
     nav_panels kwa roles zote (highlight panel="my" sahihi).
  · SHERIA: READ-ONLY (GET; POST->405). Lessee-isolation NGUMU (lease-scoped). F7/append-only/attestation
     HAZIJAGUSWA. src/research byte-untouched (sweep 32/32 PASS; golden fns 0 lines diff).
  Tests (30/30 GREEN; 5 mpya LesseeViewTests + test_e ya zamani imesasishwa kuakisi anonymized landing):
    (a) lessee /my/ ina KAIROS-1 TU + link, HAKUNA KAIROS-2/STRAT-001; (b) /my/KAIROS-1/ 200 NA
    assertNotContains USDCHF/USDJPY/STRAT-001/STRAT-002 (NO-LEAK) + AuditEvent + POST->405; (c) isolation
    KAIROS-2 asiyekodi->403, lessee wa STRAT-002 -> KAIROS-1 403, call-sign batili->404; (d) internal=zote,
    anon->302; (e) nav lessee = ["MY MODELS"] tu (is_lessee True, nav_panels moja).
RUNBOOK: login lessee-demo (nywila=lessee-demo; ana Lease STRAT-001) -> / au /my/ -> KAIROS-1 -> scorecard
  anonymized. Internal QA: /my/ -> KAIROS-1 + KAIROS-2.
NEXT AFTER: Awamu 4 (lugha + filter kwenye lessee view).
OPEN QUESTIONS:
  - /registry/<leased-model>/ (model_access ya zamani) bado inaruhusu lessee kuona pair/internal MOJA KWA
    MOJA (URL). Awamu 3 iliongeza /my/ anonymized LAKINI HAIKUONDOA njia ya /registry/ (nje ya scope).
    Je, tuzuie /registry/<model>/ + attest kwa lessee sasa (IP §9) au ibaki kwa "leased attestation"? — Chief.

=== DASH-V2-A3-FIX (2026-07-24) — funga back-door ya lessee (registry/attestation RAW) — IMEKAMILIKA ===
LAST COMPLETED: **Security fix — LESSON-044 (complete mediation)** ✅ (docs/lessons/LESSON-044.md;
  DOCTRINE_V2 §9 inashinda §5.4; surgical, access.py+tests.py TU).
  TUKIO: Awamu 3 /my/ ilikuwa anonymized, LAKINI routes za zamani /registry/<model_id>/ +
  /registry/<model_id>/attest.{json,html,pdf} (@model_access) zilimpa lessee grant ya leased model_id.
  attest.build_payload inarudisha model_id (STRAT-001) + Trade.pair -> lessee-demo angeweza kufungua
  /registry/STRAT-001/attest.json na kuona internal-id + pair (URL-guessing, id rahisi). Anonymization
  imevunjika kupitia mlango wa nyuma.
  FIX: access.model_access -> ONDOA lessee-lease grant; sasa internal/attestor PEKEE (kama panel_access
  "registry"). Lessee -> PermissionDenied (403) kwa registry_detail + attestation zote. §9 KAIROS
  anonymization inashinda §5.4 (leased raw attestation) — lessee anahudumiwa na /my/ (anonymized) PEKEE;
  anonymized attestation-by-call-sign = Awamu 4+.
  HAKUNA kingine kimeguswa: /my/ inabaki; attestation kwa internal/attestor inabaki; attest.build_payload/
  F7/append-only HAZIJAGUSWA. src/research byte-untouched (sweep 32/32).
  Tests (31/31 GREEN): test_e ya zamani imegeuzwa (lessee registry/attest = 403 SASA, si 200). MPYA
  test_f_registry_attest_backdoor_closed: lessee-demo (lease STRAT-001) -> /registry/STRAT-001/ +
  attest.{json,html,pdf} ZOTE = 403 (NEGATIVE, LESSON-044 kanuni 3); lessee /my/KAIROS-1/ bado = 200;
  REGRESSION internal bado = 200 kwa route zilezile.
KANUNI (LESSON-044): anonymization ni per-SURFACE (route), si per-VIEW. Funga KILA njia ya data ya role
  (si nav tu). Jaribu NEGATIVE (403) kwa kila anonymized-role, si happy-path pekee.
NEXT AFTER: Awamu 4 (lugha + filter kwenye lessee view; anonymized attestation-by-call-sign).

=== DASH-V2-A4 build (2026-07-24) — LUGHA (SW+EN) + FILTER CHIPS — DASHBOARD-V2 KAMILI ===
LAST COMPLETED: **Dashboard-V2 Awamu 4 (ya mwisho): R3 lugha + R5 filtering** ✅ (design §0/§5; additive,
  dashboard/ tu). Dashboard-V2 sasa KAMILI (Awamu 1-4).
  1. LUGHA (R3): language.py += say_en(topic) + say_both(topic)->{"sw","en"} (English rahisi, si jargon;
     DETERMINISTIC). say() ya Kiswahili HAIJAGUSWA (backward-compat). Views (scorecard_detail +
     _lessee_scorecard) say_* zote -> say_both. Templates (scorecard_detail.html + scorecard_lessee.html):
     kila sentensi = mistari MIWILI (SW juu <br> EN chini kwa .src). Sections A/B/E/F zote bilingual.
  2. FILTER CHIPS (R5): section D server-side kwa GET params (READ-ONLY, si POST):
     ?result=W|L · ?session=ASIA|LONDON|NY · ?from&to=YYYY-MM-DD. INTERNAL PIA ?pair=<pair>. Helpers mpya
     views.py: _session_of(dt) (UTC hour->ASIA/LONDON/NY, mipaka=research session_of), _filter_closed(
     closed, request, allow_pair) -> (filtered, total, active), _chip_qs (toggle+preserve), _filter_chips
     (groups+any_active). Chuja closed list KABLA ya render; n_closed/light/equity/compliance zinabaki FULL
     (filter=section-D pekee). Partial mpya _filters.html (chips + date form + tally "X (zimechujwa kutoka
     Y)"). style.css += .chip/.chips/.daterange. Tally kwenye template.
  3. LESSEE section D: chips zile zile ISIPOKUWA pair — _filter_chips(allow_pair=False), _filter_closed
     inapuuza ?pair kwa lessee (§9). Hata ?pair=USDCHF smuggled -> INAPUUZWA + no-leak (hakuna pair/id).
  · SHERIA: READ-ONLY (filter=query param). REUSE say()/closed data. Lessee HANA pair (§9). Sentensi
     DETERMINISTIC. F7/append-only/attestation/anonymization (A3-FIX) HAZIJAGUSWA. src/research byte-untouched
     (sweep 32/32; golden fns 0 diff).
  Tests (35/35 GREEN; 4 mpya Awamu4LangFilterTests): (a) say_both sw+en zisizo tupu + tofauti + determ,
    topics zote; (b) internal KAIROS-2 filters: result=W->3, result=L->2, session=NY->2, session=LONDON->3,
    date-range 03-01..05-01 ->2 (d_shown/d_total via r.context); (c) lessee chips = {result,session} TU
    (HAKUNA pair), result/session filter zinafanya kazi, ?pair smuggled inapuuzwa + assertNotContains
    USDCHF/STRAT-001 (no-leak); (d) internal pair chip ipo + ?pair=USDJPY->5, NOPE->0; anon->302.
RUNBOOK: /scorecards/KAIROS-x/ au /my/KAIROS-x/ -> chips (Wins/Losses · ASIA/LONDON/NY [· pair internal])
  + date form; sentensi zote SW+EN. Clear = request.path.
DASHBOARD-V2 = KAMILI (Awamu 1 SCORECARD · 2 OVERVIEW/FLEET · 3 LESSEE anonymized · A3-FIX back-door · 4
  lugha+filter). NEXT: subiri directive mpya ya PD/Chief.

=== FWD-F1 build (2026-07-25) — FORWARD TRACK F1: engine forward-append incremental — IMEKAMILIKA ===
LAST COMPLETED: **Forward Track F1 — live_engine --forward (FORWARD-APPEND)** ✅ (docs/FORWARD_TRACK_CHARTER.md
  F1; additive, src/research/live_engine.py TU; ZERO golden/statistic; STRAT configs HASA).
  Lengo: geuza Steward REPLAY -> FORWARD halisi (bars mpya baada ya FORWARD-START, decision KABLA ya matokeo).
  1. FORWARD_START = "2026-07-24" (§3.1b mpaka mtakatifu; override --forward-start). _forward_start_epoch().
     GUARD: candidate yenye entry as_of < FORWARD_START -> skipped_sealed (KAMWE haiingii forward log).
     Dirisha 2026-05->start + HOLDOUT (2025..2026-04) zote ziko chini ya mpaka -> hazichukuliwi forward.
  2. _watermark(records): as_of ya juu kabisa ya decision/execution (SI settlement — settlement=exit ya
     baadaye). Forward inashughulikia candidates zenye entry as_of > watermark TU (idempotent/resumable).
  3. run() += params forward/forward_start/watermark: baada ya cands.sort, filter (sealed guard + watermark);
     summary += forward/watermark/forward_start/skipped_sealed/skipped_watermark. --run (replay) HAIJABADILIKA.
     run_forward(data_dir, log_path): soma watermark kutoka paper_log iliyopo -> run(forward=True). _forward_loader
     (<data_dir>/<SYMBOL>.npz, schema ya load_window — F2/MT5 itaandika store; kwa sasa fixture/npz).
  4. CLI: --forward --data <dir> [--forward-start]. Idempotent: run mbili bila data mpya -> candidates_new=0.
  · SHERIA: append-only (repo.append); no-look-ahead (episodes; nr7 level truncation-invariant); costs halisi
    (spread+slip); mode=paper. Golden 0 (event_quality_report/strategy_lab/event_library HAZIJAGUSWA).
    Sealed window + HOLDOUT red-line HAZIGUSWI. src/research diff = live_engine.py TU.
  Self-test (live_engine, +6 mpya; sweep 32/32 PASS): (g) sealed-guard bars<START -> skipped_sealed, 0 rekodi
    (holdout+sealed); (h) forward-append bars>=START -> rekodi zinaongezwa; (i) watermark idempotence rerun
    -> +0; (j) incremental watermark<all -> candidates zote mpya; (k) forward records valid vs
    decision_repository.REQUIRED + as_of>=START + paper; (l) run_forward auto-watermark idempotent.
  E2E (npz store): RUN1 44 cand/5 filled/137 rekodi; RUN2 (data ile ile) +0 (idempotent); SEALED store
    (2025) -> 0 cand, 44 skipped_sealed, 0 rekodi (mlango umefungwa).
RUNBOOK: (F2 baadaye) mt5_data.py vuta bars -> live_engine.py --forward --data <store> -> model_steward.py
  -> dashboard ingest -> scorecard FORWARD inasasishwa. Chini: siku 20+/trades 30+ kabla hitimisho.
KNOWN LIMITATION: forward run kila batch = account state fresh (_acct_state) — cum_pnl/daily-budget
  HAZIBEBWI kati ya runs (per-trade pnl_r honest imehifadhiwa; gating ni per-batch). Cross-run open-position
  carry si lazima F1 (kila candidate = trade kamili entry+exit kutoka episodes).
NEXT: F2 — mt5_data.py READ-ONLY data feed (inahitaji MT5 kwenye PC ya Operator).

=== FWD-F2 build (2026-07-25) — MT5 READ-ONLY data feed (forward store) — IMEKAMILIKA ===
LAST COMPLETED: **Forward Track F2 — src/research/mt5_data.py** ✅ (docs/FORWARD_TRACK_CHARTER.md F2;
  additive, faili MPYA moja; ZERO golden/reused-module kuguswa — import tu).
  Chota H1 bars za USDCHF/USDJPY kutoka MT5 kwa KUSOMA TU -> features (REUSE market_state_engine) ->
  forward store <dir>/<SYMBOL>.npz ambayo live_engine --forward (F1) inaisoma. Paper — HAKUNA order.
  1. Seam ya MT5 mock-able: _fetch_rates(symbol, n) -> (rows, point, resolved) kupitia
     mt5.copy_rates_from_pos(sym, TIMEFRAME_H1, 0, n). Import ya MetaTrader5 = LAZY (module i-import bila
     MT5). _resolve_symbol: USDCHF/USDJPY -> broker symbol (handle suffix .m/.raw/.pro; override config).
  2. rates_to_arrays(rows, sym, point): -> arrays za npz kwa schema HALISI ya load_pair (PIP-SPACE):
     o/h/l/c=price/pip; spr=spread(points)*point/pip (H1-approx); atr=state_df _atr(ATR14 Wilder)/pip;
     hour=server-hour int; vol=volatility_state (REUSE _deseason/_reg3); tc=tick_volume float; ts=epoch
     datetime64[s]. REUSE state_df -> features SAWASAWA na training (GIGO — usivumbue).
  3. write_store(dir): fetch -> rates_to_arrays -> np.savez. GUARD: bars ts >= FORWARD_START PEKEE
     (features zilihesabiwa na warmup wa bars ZOTE -> trailing windows sahihi; publish = forward tu).
     Provenance <dir>/_mt5_meta.json (source, H1-approx, forward_start, resolved/point/counts kila sym).
  4. CLI: python mt5_data.py --out <dir> [--bars N] [--symbols USDCHF USDJPY] [--forward-start].
  · SHERIA: READ-ONLY KABISA — copy_rates + symbols_get + symbol_info PEKEE; HAKUNA order-write/
    position-modify/account-write. REUSE pip/_atr/_deseason/_reg3 (state_df). ZERO golden; live_engine/
    market_state_engine HAZIBADILIKA (import tu). run_selftests 32/32 (mt5_data = standalone self-test, si
    kwenye sweep-list — sweep inabaki 32).
  Self-test (mt5_data --self-test, bila MT5 — mock rows; PASS): (a) schema kamili (keys/urefu/pip-space/
    dtype); (b) FORWARD_START guard (sealed-era -> store tupu); (c) round-trip npz -> live_engine.
    _forward_loader -> run(forward=True) bila error (candidates=9); (d) READ-ONLY grep-assert (tokens
    zimeundwa kwa concatenation ili zisijigrep — hakuna order/position-write CALLS); (e) determinism.
RUNBOOK (F1+F2 kamili): (Operator, PC yenye MT5) python mt5_data.py --out <store> -> python live_engine.py
  --forward --data <store> -> python model_steward.py -> dashboard ingest -> scorecard FORWARD inasasishwa.
  Cadence: kila siku/wiki. Chini: siku 20+/trades 30+ kabla hitimisho (N ndogo = si proof).
KNOWN LIMITATION: H1-approx (Chief 2026-07-24) — spr=points->pips (SI tick-median), tc=tick_volume (proxy);
  SI tick-exact. volatility_state=UNKNOWN hadi history itoshe (rolling min_periods ya WIN_BARS H1) — GIGO-
  consistent (math ileile ya training). MT5 order-execution+token+PD-signature = §9.3 (baadaye).
NEXT: F2 imekamilisha Forward Track engine-side (F1 append + F2 feed). Subiri directive ya PD/Chief
  (mfano: run forward live kwenye PC ya Operator, au §9.3 live path).

=== FWD-F2-CONN (2026-07-25) — MT5 login/creds kupitia ENV (SALAMA, bado READ-ONLY) — IMEKAMILIKA ===
LAST COMPLETED: **MT5 connection fix — src/research/mt5_data.py** ✅ (surgical, faili moja; READ-ONLY inabaki).
  TUKIO (Operator): mt5.initialize(path) -> -6 "Authorization failed" — terminal imepatikana LAKINI
  haijalogini. FIX: creds kupitia ENV (password KAMWE kwenye argv/print/log/provenance).
  1. _fetch_rates(..., mt5_path, login, password, server): jenga kwargs kwa mt5.initialize — path=mt5_path
     (kama ipo); login/password/server ZOTE zikiwepo -> login=int(login), password, server. Ita
     mt5.initialize(**kwargs). initialize ikishindwa -> RuntimeError yenye ujumbe: -6 => weka ENV
     ELITEFX_MT5_LOGIN/PASSWORD/SERVER (+ ELITEFX_MT5_PATH). err = mt5.last_error() (HAKUNA password).
  2. write_store(..., _mt5, mt5_path, login, password, server): threads creds -> default fetch ->
     _fetch_rates. _mt5 = injection ya mock kwa test.
  3. main: ENV resolution — mt5_path=ELITEFX_MT5_PATH (au --mt5-path), login=ELITEFX_MT5_LOGIN,
     password=ELITEFX_MT5_PASSWORD, server=ELITEFX_MT5_SERVER. Pitisha write_store.
  4. USALAMA: password si kwenye argv (ENV pekee), si kwenye print/log/_mt5_meta.json. meta haina creds.
  · SHERIA: READ-ONLY (copy_rates/symbols_get/symbol_info pekee — grep-assert [d] bado GREEN). schema/
    rates_to_arrays/FORWARD_START guard HAZIJAGUSWA. ZERO golden; live_engine/market_state_engine import tu.
  Self-test (mt5_data --self-test, PASS; +1 mpya): (a-e) za awali GREEN; (f) connection — _FakeMT5 captures
    initialize kwargs (path/login=int/password/server ZOTE zinapokelewa) NA password (secret) HAIPO kwenye
    _mt5_meta.json (grep-assert). run_selftests 32/32.
RUNBOOK (Operator, PC yenye MT5 login):
  set ELITEFX_MT5_LOGIN=<acct>  ELITEFX_MT5_PASSWORD=<pw>  ELITEFX_MT5_SERVER=<broker-server>
  [ELITEFX_MT5_PATH=C:\...\terminal64.exe kama inahitajika]
  python src/research/mt5_data.py --out <store>  ->  live_engine.py --forward --data <store>
  -> model_steward.py -> dashboard ingest. (password kwenye ENV pekee — kamwe si kwenye amri/log.)
NEXT: Forward Track (F1 append + F2 feed + connection) tayari. Subiri directive ya PD/Chief (endesha
  forward live PC ya Operator, au §9.3 live-execution path).

=== FWD-CYCLE build (2026-07-26) — forward orchestrator (cadence, soak/VPS) — IMEKAMILIKA ===
LAST COMPLETED: **Forward Track orchestrator — src/research/forward_cycle.py** ✅ (docs/FORWARD_TRACK_CHARTER.md
  ROLLOUT; faili MPYA moja; ZERO golden/trade logic — inaita CLIs zilizopo kwa subprocess TU).
  Lengo: cadence nzima ya forward kwa amri MOJA + log ya kila run — Faza 1 SOAK (PC demo, siku 2-3,
  inapima UIMARA WA BOMBA) + Faza 3 VPS (24/7). Paper/READ-ONLY.
  1. Hatua 4 kwa mpangilio (subprocess, sys.executable, ENV inarithiwa -> ELITEFX_MT5_* zinapita):
     mt5_data.py --out <store> -> live_engine.py --forward --data <store> -> model_steward.py ->
     dashboard/manage.py ingest (bila --demo). Kila hatua: capture stdout/stderr/returncode/duration.
  2. FAIL-SOFT + fail-fast: hatua FAIL -> zilizobaki SKIPPED + exit-code!=0; --continue-on-error kuendelea.
     mt5_data FAIL (MT5 down) -> zilizobaki ZOTE skipped (bomba lasimama salama). Subprocess exception
     (binary/cwd batili) -> FAIL (si crash).
  3. LOG: append data/forward/cycle_log.jsonl -> {ts, step, status, returncode, duration_s, summary
     (candidates_new/filled/rejected kutoka stdout ya live_engine kwa regex), error_tail (stderr tail 15)}.
     _print_summary: hatua ngapi OK/FAIL/SKIP + candidates_new/filled.
  4. CLI: --store data/forward (default) · --skip-dashboard · --continue-on-error. Task-Scheduler/cron-ready
     (exit-code!=0 = cycle imeshindwa). run_cycle(..., _runner=) = injection kwa test.
  · SHERIA: READ-ONLY/paper (inaita CLIs, HAIBADILISHI). ZERO golden; live_engine/mt5_data/model_steward
    HAZIJAGUSWA (subprocess tu). forward_cycle import = stdlib pekee (subprocess/json/re/time) -> i-import
    bila numpy/MT5/Django.
  Self-test (forward_cycle --self-test, stub subprocess; PASS): (a) mpangilio hatua 4 + live_engine
    summary(candidates_new=7); (b) fail-soft model_steward FAIL -> exit!=0 + dashboard SKIPPED (haikuitwa);
    (c) cycle_log.jsonl append (4->8) + schema kamili; (d) mt5-fail -> zilizobaki ZOTE skipped; (e)
    --continue-on-error (hakuna skip) + --skip-dashboard (hatua 3). run_selftests 32/32 (forward_cycle si
    kwenye sweep-list).
RUNBOOK (Faza 1 SOAK, PC demo — ENV ya MT5 kama FWD-F2-CONN):
  python src/research/forward_cycle.py                      # amri MOJA (hatua 4 + log)
  # Task Scheduler (Windows): Action = python.exe src\research\forward_cycle.py; Trigger = kila saa/siku;
  #   "Start in" = repo root; ENV ELITEFX_MT5_* kwenye system/user env. exit!=0 -> Scheduler inaona fail.
  # cron (VPS Faza 3): 0 * * * * cd <repo> && python src/research/forward_cycle.py >> cron.out 2>&1
  Log: data/forward/cycle_log.jsonl (1 mstari/hatua/run; JSONL append-only).
sample cycle_log (run moja OK): mt5_data OK · live_engine OK summary{candidates_new,filled,rejected} ·
  model_steward OK · dashboard_ingest OK (4 mistari, exit 0).
NEXT: Forward Track KAMILI (F1 append + F2 feed + connection + cycle orchestrator). Operator aendeshe Faza 1
  SOAK. Subiri directive ya PD/Chief (Faza 2/3 au §9.3).

=== EA-1 build (2026-07-26) — KAIROS EA (MQL5): STRAT-001/002 ndani ya MT5 — IMEKAMILIKA ===
LAST COMPLETED: **KAIROS EA (MQL5)** ✅ (docs/KAIROS_EA_CHARTER.md; faili MPYA: mql5/KAIROS.mq5 +
  docs/RUNBOOK_kairos_ea.md; HAKUNA Python/golden kuguswa — MQL5 mpya). PORT HALISI ya STRAT-001/002
  kwa Strategy Tester (backtest ya PD) + chart demo/live.
  PARITY (port kutoka src/research, BILA kubadilisha):
  - nr7_break (event_library_v2): rngSig = high[1]-low[1]; rmin = MIN(range za bars 1..InpNR INCLUSIVE);
    nr = rngSig <= rmin. buy-stop = high[1]+tickOff, sell-stop = low[1]-tickOff (OCO). tick = InpTick(0.1)
    pips -> price (0.1*pipSize).
  - no-LATE: MUHIMU — Python _mask_context inatumia session ya bar ya ENTRY (i+1), SI signal
    (_sess(hour[i+1]), EP-5 ex-ante schedule). Kwa H1 EA entry bar = shift 0 (inayoundwa); signal = shift 1.
    late = hour(shift0) >= InpNoLateStart(17). _sess: ASIA 0-6, LONDON 7-11, NY 12-16, LATE 17-23.
  - ATR = Wilder(InpATR=14) kupitia iATR, thamani ya SIGNAL bar (shift 1). SL/TP kwa ATR ya SIGNAL bar
    (Python episodes: a=atr[i], i=signal — SI entry). SL=InpSL_mult*ATR, TP=InpTP_mult*ATR. tie->SL
    (broker fill). OCO: moja ikijaza -> futa nyingine (OcoCleanup kila tick); pending = bar MOJA (expiry).
  - Variants (INPUT): KAIROS-1 USDCHF SL2.0/TP1.0 · KAIROS-2 USDJPY SL1.0/TP1.0 (attach chart + inputs).
  - Risk: InpRiskPct (lot kwa SL-distance x tick_value), InpMaxPositions=1/symbol/magic, InpDailyLossPct
    (baseline = balance ya mwanzo wa siku, deterministic), InpMagic per instance. CTrade/BuyStop/SellStop.
  - SIGNAL-LOG CSV (MQL5/Files/KAIROS_signals_<sym>_<magic>.csv): ts(signal bar epoch), range_pips,
    rmin_pips, nr(1/0), atr_pips, session(entry-bar/i+1), long_level_pips, short_level_pips. PIP-SPACE (÷pip)
    kwa parity ya moja kwa moja na Python. 1 mstari/closed bar. Strategy-Tester safe.
  · NIDHAMU: demo/backtest PEKEE (live = Faza 4 + SAINI YA PD §3.1b/§9). HAKUNA golden/Python kuguswa
    (src/research byte-untouched; sweep 32/32). MQL5 haicompili hapa (Linux) — PD anacompile MetaEditor (F7).
  RUNBOOK (docs/RUNBOOK_kairos_ea.md): install Experts/ -> compile F7 -> Strategy Tester (USDCHF/USDJPY H1,
    real ticks) -> demo chart attach + AutoTrading -> signal-log kwa parity. Inputs table KAIROS-1 vs KAIROS-2.
NEXT: EA-2 = parity harness (Python) inalinganisha signal-log na nr7_break+wilder_atr+_sess (levels/atr/
  session LAZIMA zifanane) + deploy/backtest guide. (EA-1 imeandaa .mq5; PD anacompile + backtest.)
KUMBUKA (parity subtleties kwa EA-2): (1) no-LATE = session ya ENTRY bar (i+1), si signal; (2) SL/TP ATR =
  SIGNAL bar; (3) rmin INCLUSIVE (bars 1..7 incl signal); (4) log = PIP-SPACE; (5) iATR seeding vs
  wilder_atr(atr[0]=tr[0]) hutofautiana kidogo warmup -> tolerance; (6) MT5 fill/spread != Python (cross-check).

=== BRIDGE-1 build (2026-07-30) — CONDUIT BRIDGE Awamu 1 (Python ubongo) — IMEKAMILIKA ===
LAST COMPLETED: **live_brain.py (edge-mode + commands writer + results ingester)** ✅ (docs/CONDUIT_BRIDGE_
  CHARTER.md Awamu 1; faili MPYA moja; ZERO golden/reused-module kuguswa — import tu; ZERO MT5).
  Doctrine §9: MODEL INAAMUA, EA (Awamu 2) itatekeleza tu. Python HAIWEKI order (hakuna MetaTrader5;
  transport = JSON bridge files). DEMO PEKEE (§3.1b; live = saini ya PD).
  (a) EDGE edge_decision(): bar ya mwisho ILIYOFUNGWA (i=n-1) -> nr7_break (REUSE golden) -> no-LATE
      (_sess ya ENTRY bar i+1 = (hour[i]+1)%24; LATE -> veto) -> ATR ya SIGNAL bar (data['atr'][i], parity
      na live_engine a=atr[i]) -> SL/TP -> size (DailyRiskBudgetSizer+FTMO) -> integrity_gate. PASS ->
      PLACE_OCO {cmd_id=strategy:bar_ts (deterministic), symbol, magic, lots, buy_stop/sell_stop,
      sl_buy/tp_buy/sl_sell/tp_sell, bar_ts, expiry_utc=bar_open+2h}; FAIL/veto -> None + sababu. Levels
      PIP-SPACE -> PRICE (*pip; digits 3 JPY / 5). Account view fresh (BRIDGE-1 haitunzi cross-bar state).
  (b) write_commands(): <bridge>/commands.json {seq, issued_utc, commands[]} atomic (tmp+os.replace),
      idempotent (seti ile ile ya cmd_id -> seq haiongezeki). --cancel-all -> CANCEL_ALL (kill-switch).
  (c) ingest_results(): results.jsonl/json -> FILLED/REJECTED/EXPIRED/CANCELLED -> execution; CLOSED ->
      settlement(+pnl/pnl_r/exit); PLACED -> ack. Append paper_log.jsonl (repo.append; schema=live_brain@v1).
      Idempotent kwa record id (exec:<oid>/<oid>) -> re-ingest +0. learned_ev tag; mode=paper account=demo;
      settlement.id=oid==execution.order_id (dashboard linkage).
  (d) CLI: --bridge-dir (env ELITEFX_BRIDGE_DIR) · --decide · --ingest · --cycle · --cancel-all · --self-test.
  · SHERIA: REUSE nr7_break/_sess/sizer/gate/_canonical_loader/STRATS; STRAT configs HASA; paper_log
    dashboard-compatible. ZERO golden; live_engine/event_library/event_quality/broker_adapter/integrity_gate/
    decision_repository byte-untouched (import tu). sweep 32/32.
  Self-test (PASS): (a) edge nr7 -> PLACE_OCO levels/SL/TP/lots sahihi (buy_stop=(high+0.1)*pip; sl_buy=
    (high+0.1-2*ATR)*pip; cmd_id/magic/expiry); (b) no-LATE (entry hour 17) -> hakuna amri; (c) budget=0 ->
    qty=0 -> hakuna amri; (d) commands atomic+idempotent; (e) ingest FILLED+CLOSED repo-valid + idempotent
    (+0) + linkage; (f) determinism.
RUNBOOK (Awamu 1, bila MT5): python live_brain.py --cycle --bridge-dir <MQL5/Files/bridge> = (1) ingest
  results za EA -> paper_log; (2) canonical -> edge decide -> commands.json. Cadence: kila H1 bar (Task
  Scheduler baada ya mt5_data canonical). EA (Awamu 2) inapoll commands, inatekeleza, inaripoti results.
NEXT: BRIDGE-2 (KAIROS_CONDUIT.mq5 — poll commands, execute, report results; demo-only guard; HAINA logic).

=== BRIDGE-2 build (2026-07-30) — KAIROS_CONDUIT.mq5 (EA tupu conduit) — IMEKAMILIKA ===
LAST COMPLETED: **KAIROS_CONDUIT.mq5 + docs/RUNBOOK_conduit.md** ✅ (docs/CONDUIT_BRIDGE_CHARTER.md Awamu 2;
  faili MPYA; HAKUNA KAIROS.mq5/Python kuguswa). EA TUPU (HAINA strategy logic — IP §9) inayotekeleza amri
  za live_brain (ubongo). DEMO PEKEE.
  1. Inputs: InpBridgeDir("bridge"), InpPollSeconds(5), InpMagicFilter(0=zote), InpEnabled(true).
  2. DEMO-ONLY guard (OnInit): ACCOUNT_TRADE_MODE != DEMO -> INIT_FAILED ("LIVE = SAINI YA PD Faza 4").
     Hakuna njia ya kuipita.
  3. OnTimer (poll): soma <Files>\<bridge>\commands.json -> flat JSON parser YETU (JNum/JStr string-search;
     split kwa "cmd_id"). seq ile ile -> usisome tena. cmd_id HAIJATEKELEZWA (processed.txt — idempotent
     kati ya restarts): PLACE_OCO -> CTrade.BuyStop+SellStop (lots/SL/TP/magic; ORDER_TIME_GTC + EA-managed
     expiry). CANCEL_ALL -> futa pending za magic zetu (kill-switch, hata InpEnabled=false). Magic filter.
  4. OCO + lifecycle: OnTradeTransaction DEAL_ENTRY_IN -> FILLED + futa nyingine (OCO); DEAL_ENTRY_OUT ->
     CLOSED (+pnl = DEAL_PROFIT+SWAP+COMMISSION). ScanExpiry (UTC TimeGMT() >= expiry) -> futa + EXPIRED.
     Placement fail -> REJECTED. Kila tukio -> append <bridge>\results.jsonl (JSON mstari mmoja). EA PEKEE
     inaandika results; ubongo unasoma.
  5. HAKUNA nr7/ATR/indicators/decisions (conduit tupu — itakodishwa kwa lessee §9).
  · SHERIA: KAIROS.mq5 (tester-tool) HAIJAGUSWA; Python HAIJAGUSWA (sweep 32/32). MQL5 haicompili hapa
    (Linux) — PD anacompile F7. results schema = HASA inayotarajiwa na live_brain._event_to_records.
  BRIDGE-3 integration quick-check (bila MT5, hapa): results.jsonl bandia (PLACED+FILLED+CLOSED, umbo HASA
    la EA) -> live_brain.ingest_results -> execution+settlement repo-REQUIRED valid, idempotent (re-ingest
    +0/skipped 2), linkage settlement.id==execution.order_id, learned_ev=1.92 tag, PLACED ignored. PASS.
  RUNBOOK (docs/RUNBOOK_conduit.md): compile F7 -> demo chart attach -> ELITEFX_BRIDGE_DIR=<DataFolder>\MQL5\
    Files\bridge -> cadence: mt5_data canonical + live_brain --cycle (ingest+decide) -> ona pending/fills
    terminal + results.jsonl. Kill-switch: live_brain --cancel-all.
KNOWN LIMITATION (BRIDGE-3 hardening): g_oco (hali ya OCO) iko kwenye kumbukumbu — EA ikirestart kabla
  position kufunga, FILLED/CLOSED za order za awali hazitaripotiwa (rebuild kutoka positions/comment =
  baadaye). expiry = UTC (broker-time-independent). Orders = GTC + EA-managed expiry.
NEXT: BRIDGE-3 (integration PC ya PD: demo end-to-end -> VPS -> baadaye sealed-window acceptance + live saini).

=== M4-0 build (2026-08-01) — BREADTH BASELINE (nr7 × pairs 12 pooled) — IMEKAMILIKA (runner) ===
LAST COMPLETED: **src/research/breadth_baseline.py** ✅ (docs/CYCLE4_ML_CHARTER.md §1B/§5/§6.1 +
  docs/KAIROS_3_SPEC.md §5.3) + **docs/RUNBOOK_breadth_baseline.md** + registration kwenye run_selftests.
  KUSUDI: namba ambayo KAIROS-3 (na ML yote M4-1..M4-4) LAZIMA ishinde — SI hypothesis mpya: logic
  ILE ILE iliyothibitika (`nr7_break` × H1 × no-LATE = STRAT-001/002) ikienezwa pairs 2 -> **12 pooled**.
  1. SPEC FROZEN: nr7_break (stop/OCO) · H1 · no-LATE · vol=None · max_hold=24 · variants MBILI
     SL2.0/TP1.0 (KAIROS-1) na SL1.0/TP1.0 (KAIROS-2) · pairs 12 (data_config) · splits **TRAIN +
     VALIDATION PEKEE**.
  2. POOLED = hukumu (L-041): `_r_normalize`+`pool_streams` (family_pooled) -> EV_R, EV_pips,
     EV_pips_FX (bila XAUUSD — pip-scale), N, trades/mwaka (Σ n_i/miaka_i), p_boot (pvalue_boot,
     mean_block=3, seed=hash(registration)), CI90 (`_boot_ci`), p_z, win%, PF. Per-pair =
     **diagnostics TU** yenye tahadhari ya L-041 iliyoandikwa kwenye ripoti.
  3. RED LINE `_guard_split`: split != train/validation -> PermissionError **KABLA ya kusoma data**
     (holdout/sealed/forward/all). Red-line ya `load_window` (token) inabaki juu yake.
  4. `recommend_pairs()` — KANUNI pre-registered, SI ranking: EV_R>0 TRAIN **NA** VALIDATION **NA**
     N_valid>=30; orodha ya **alfabeti** (si EV); HAKUNA top-N. Ripoti: (a) zilizopita + YAML snippet;
     (b) zilizokataliwa + sababu. Ni PENDEKEZO — **PD ndiye anayehariri config/models.yaml**.
  5. Outputs: `reports/breadth_baseline.md` (BASELINE LINE + pooled per variant + per-pair
     diagnostics + pendekezo la pairs[] + caveats) na `data/strategies/breadth_baseline.jsonl`
     (kind=pair/pooled/pairs_rule/baseline). No-clobber (candidates*.jsonl hazibadilishwi).
  6. `boot_B()`: engine ILEILE, B ina-cap kwa RAM (array B×N ya _stationary_indices; sakafu 1,000,
     kamwe zaidi ya B iliyoombwa) — `B_eff` inaripotiwa kwenye jedwali.
  · SHERIA: golden ZERO changes — episodes/_mask_context/pvalue_boot/pvalue_gt0/load_window/
    _r_normalize/pool_streams/_boot_ci ni **imports TU**. Gharama halisi kwenye kila namba (L-039).
    HOLDOUT + sealed 2026-05+ HAZIJAGUSWA.
  Self-test (PASS, sweep **33/33**): (a) pooled math == family_pooled (EV_R/p_boot/CI90 recompute huru
    kwa golden fns); (b) HOLDOUT/sealed guard (4 splits + pair_stream -> PermissionError, load_window
    haikuitwa hata mara moja); (c) determinism (run mara 2 = JSON ileile) + no-clobber + outputs +
    BASELINE LINE ndani ya ripoti + rule-closure/exhaustive + coverage 12/12; (d) Σ per-pair N ==
    pooled N; (e) pairs[]-rule: train-only chanya (+0.30, KUBWA kuliko mshindi) **INAKATALIWA**,
    N_valid=29 INAKATALIWA, orodha ni alfabeti; nyongeza: no-LATE decidability (entries LATE = 0) na
    L-039 (EV_pips(spr0) − EV_pips(spr2) == 2.0 EXACT = gharama ipo ndani ya kila namba).
MATOKEO HALISI (PD aliendesha PC ya data 2026-08-01; commit 777b8c7 — reports/breadth_baseline.md):
  **BASELINE LINE (imesajiliwa): KAIROS-3 LAZIMA izidi EV_net = +0.91 pips/trade (FX pooled,
  N=4934), EV_R = +0.0526, trades/mwaka = 2,680 — VALIDATION, variant SL1/TP1.**
  | variant | split | N | EV_R | EV_pips FX | win% | PF | p_boot |
  | SL2/TP1 | TRAIN | 19,164 | +0.0291 | +1.02 | 71.4 | 1.10 | 0.00096 |
  | SL2/TP1 | VALID |  5,094 | +0.0328 | +0.90 | 72.2 | 1.11 | 0.00076 |
  | SL1/TP1 | TRAIN | 20,316 | +0.0559 | +1.09 | 57.7 | 1.12 | 0.00100 |
  | SL1/TP1 | VALID |  5,355 | +0.0526 | +0.91 | 58.1 | 1.11 | 0.00027 |
  - **BREADTH INAFANYA KAZI kwa mechanism-level:** VALID ≈ TRAIN (haikushuka — tofauti na fails 3/3
    za L-041 ambazo zilipinduka hasi OOS); 9/12 (SL2/TP1) na 8/12 (SL1/TP1) pairs sign-consistent.
  - pairs[] PENDEKEZO (kanuni, si ranking): SL2/TP1 → AUDUSD EURUSD GBPJPY GBPUSD NZDUSD USDCAD
    USDCHF USDJPY XAUUSD (9); SL1/TP1 → zilezile bila NZDUSD (8). Zilizokataliwa: EURCHF (train −),
    EURGBP (valid −, train − kwa SL1), EURJPY (valid −), NZDUSD (valid − kwa SL1) — **EUR-crosses
    zote tatu zinaanguka kwenye variants zote mbili** (hypothesis: NR7 inahitaji expansion
    follow-through; pairs za range-bound/low-vol zinatoa false breaks — SI dai, ni observation).
  - USDCHF/USDJPY (pairs za STRAT-001/002) zimepita kanuni **zenyewe** = consistency check ya ndani.
    Zote mbili hazikuwa top za TRAIN (USDCHF train +0.0060 → valid +0.1355) = ushahidi zaidi wa L-041
    (TRAIN ranking ni kelele).
  - **TAHADHARI (L-039):** +0.91 pips/trade ⇒ breakeven Δspread = 0.91 pip (cost_stress §1 analytic).
    KAIROS-1 = 1.92, KAIROS-2 = 2.65 → breadth ni dhaifu mara 2-3 kwa kila trade; inashinda kwa
    WINGI (~2× pip-flow ya pairs-2), si UBORA. Charter §4.4 inataka edge ~3-4× cost — hii ni ~0.7×.
  - **R vs pips divergence:** GBPJPY (+0.0126 R / −0.39 pips) na NZDUSD (+0.0040 R / −0.15 pips)
    kwenye SL2/TP1 zinapita kwa R lakini si kwa pips VALIDATION. Kanuni ilikuwa **pre-registered kwa
    EV_R** — kuongeza pips-filter SASA (baada ya kuona namba) = kuhamisha magoli (post-hoc selection).
    Imeandikwa kama caveat; uamuzi ni wa PD, na uthibitisho ni forward/holdout.
NEXT: (i) M4-0b iliyopendekezwa — cost-stress (Δspread 0.2/0.5/1.0 + WIDE-split, cost_stress.py
  iliyopo) + capacity chini ya risk-engine (max_slots 7 / correlated 3; 2,680/mwaka ≈ 10-11/siku)
  KABLA PD hajapanua pairs[] live; (ii) M4-1 DATASET (triple-barrier + features kwa bars ZOTE, pairs
  12, TRAIN pekee; purged+embargoed CV). Bar ya KAIROS-3 sasa iko wazi: spec §5.2 (≥3.0 pips) ndiyo
  binding, si breadth (+0.91) — ML lazima ilete **UBORA**, wingi tayari unamilikiwa na breadth.

=== M4-0b (2026-08-01) — COST STRESS + CAPACITY ya breadth — IMEKAMILIKA (PD aliendesha) ===
LAST COMPLETED: **src/research/breadth_capacity.py** ✅ (commits fbb76b2 + cfc6c6e; sweep 34/34).
  Reuse-only: cost_stress R5(1)/R5(2) · config HALISI ya ftmo_config · semantiki HALISI za lango la
  live (live_engine._corr_group reservation + broker_adapter._groups_of check) · pair_stream ya M4-0.
  Splits TRAIN+VALIDATION pekee; HOLDOUT + sealed 2026-05+ hazijaguswa.
MATOKEO (PD, 2026-08-01) — **scenario MBILI zililinganishwa:**
  | scenario | variant | breakeven Δspread (VALID) | COMBINED rej (VALID) | at-cap |
  | pairs 12 | SL2/TP1 | 0.90 pip | 26.6% | 29.0% |
  | pairs 12 | SL1/TP1 | 0.91 pip | " | " |
  | pairs[] pendekezo (9/8) | SL2/TP1 | **1.58 pip** | **16.8%** | **11.8%** |
  | pairs[] pendekezo (9/8) | SL1/TP1 | **1.78 pip** | " | " |
  - **Kanuni ya pairs[] ya M4-0 haikuondoa tu pairs hasi — iliboresha ustahimilivu wa gharama MARA
    ~2** (0.90 → 1.58/1.78 pips; KAIROS-1 = 1.92). Pooled-FX EV = breakeven kwa ufafanuzi.
  - **TAHADHARI YA MSINGI (selection bias):** kanuni ilitumia VALIDATION kuchagua pairs, kisha
    tunapima EV kwenye VALIDATION ILEILE → makadirio ya 1.58/1.78 ni **hot** (in-sample-of-the-rule).
    Mwelekeo (kuondoa pairs zenye ishara hasi mfululizo kunasaidia) ni wa kuaminika; **ukubwa SI**.
    Precedent ya mradi: VALID/TRAIN ~2× hot → shrink 0.346 (family_pooled §4). Hakimu = forward/holdout.
  - **CAPACITY:** model MOJA haina kikwazo (rej 0.1-2.2%). **Models MBILI kwenye akaunti moja** ndipo
    lango linabana: pairs 12 → 26.6% rej / at-cap 29%; pendekezo 9/8 → 16.8% rej / at-cap 11.8%.
    Hitimisho: kupanua pairs kupita kiasi kunanunua **msongamano**, si nafasi.
  - **EV acc vs rej:** ishara inapinduka kati ya splits (TRAIN rej hasi, VALID rej chanya) na N ya
    rejects ni ndogo (2-238 per-variant) → **hakuna ushahidi wa queueing bias ya kimfumo; ni kelele.**
    Hoja ya kupanga foleni kwa UBORA inabaki halali kimuundo (at-cap 12-29% = uteuzi wa nasibu),
    si kwa namba hizi.
  - **BASELINE LINE ya KAIROS-3 HAIBADILIKI** (pairs-12 pooled: EV_net +0.91 pips FX / EV_R +0.0526 /
    2,680 kwa mwaka). Sababu: ilikuwa pre-registered kwa pairs-12; na kwa vyovyote spec §5.2 (≥3.0
    pips) ndiyo binding — inazidi 0.91 NA 1.78.
  - SWALI LA WAZI (halijarekebishwa, ni la Chief/PD): live_brain ina-increment correlation-group MOJA
    wakati CHECK 4 inakagua makundi YOTE → EUR_group cap ni laini kuliko nia. Safu `live` vs `strict`
    kwenye ripoti zinaonyesha ukubwa wa tofauti.
PENDEKEZO KWA PD: panua `pairs[]` kwa orodha ZA KANUNI (KAIROS-1 → 9, KAIROS-2 → 8), **si** pairs 12;
  fuatilia spread (breakeven ~1.6-1.8 pip si pana kiasi cha kupuuza); hakimu wa mwisho = forward.
NEXT: M4-1 DATASET (triple-barrier + features, bars ZOTE, pairs 12, TRAIN pekee, purged+embargoed CV).

=== M4-1 (2026-08-01) — DATASET ya KAIROS-3 — IMEKAMILIKA (PD alijenga) ===
LAST COMPLETED: **purged_cv.py + k3_dataset.py** ✅ (commit 830fcd4; sweep 36/36).
  Ubunifu muhimu: **residue-class scan** (stride = max_hold+2 = 26) unaruhusu `episodes()` YA GOLDEN
  kutoa label kwa **KILA bar** bila kuandika labeler mpya — ndani ya class moja trade daima inafunga
  kabla ya signal ifuatayo, kwa hiyo non-overlap discipline hairuki bar hata moja. Parity
  imethibitishwa dhidi ya episodes iliyoitwa bar-moja-moja (mismatch 0, coverage kamili).
MATOKEO (PD, 2026-08-01): **rows 1,025,338** · pairs 12 · dirs 2 · folds 5 (purged+embargoed).
  | geometry | win-rate (bila uteuzi) | EV_R (bila uteuzi) |
  | sl2tp1 | 65.96% | −0.0470 |
  | sl1tp1 | 49.25% | −0.1019 |
  - Bwawa lote lina EV hasi kwa ujenzi (kila bar inalipa gharama) — ndiyo hatua sahihi ya sifuri.
  - Sanity: sl1tp1 (1:1 symmetric) ina win ~49.25% ≈ sarafu bila alpha; sl2tp1 (TP karibu, SL mbali)
    ina win 65.96% ≈ break-even ya kijiometri 66.7% — labels ni consistent kimuundo.
  - Uteuzi unaohitajika ni MDOGO: 854 trades/mwaka × miaka 7 ≈ 0.6% ya bwawa (breadth-12 = ~1.8%).
DECISIONS (PD alinipa mamlaka 2026-08-01 "unaweza decide... lakini zingatia makubaliano"):
  1. **config/models.yaml SIJAIHARIRI** — agreement (KAIROS_3_SPEC §6 + kichwa cha models.yaml)
     inasema PD ndiye anayehariri. Nimempa block ya kupaste (KAIROS-1 → 9 pairs, KAIROS-2 → 8).
  2. **BASELINE LINE haibadiliki** (+0.91 pips pairs-12) — ilikuwa pre-registered; kuipandisha kwa
     kuwa 9/8 zinaonekana bora = kuhamisha magoli.
  3. **Code ya live sijaigusa** (asymmetry ya correlation ni SWALI LA WAZI lenye namba).
  4. **WIDE-skip: sijaamua** hadi nisome §2 ya reports/breadth_cost_capacity*.md.
  5. **M4-2 trainer = LightGBM**, artifact = JSON tree dump (hakuna pickle), **inference = pure-numpy
     scorer yetu** (live/paper hazitegemei framework — mwendelezo wa msimamo wa k4_model).
NEXT: **docs/M4_2_REGISTRATION.md imesajiliwa KABLA ya model yoyote** (charter §4.6): kupita =
  EV_R > +0.0328 (sl2tp1) / +0.0526 (sl1tp1) NA trades/mwaka ≥ 854/890 NA p_boot<0.05 NA folds ≥4/5.
  Kisha: jenga k3_model.py (GBM + threshold sweep juu ya out-of-fold + freeze), TRAIN PEKEE.

=== M4-2 (2026-08-01) — GBM CV: **LESSON** (vigezo vilivyosajiliwa havikutimia) ===
MATOKEO (PD aliendesha; reports/k3_model_cv_*.md):
  | geometry | pool EV_R | best OOF (threshold) | lift | ilihitajika | % ya lengo |
  | sl2tp1 | −0.0470 | **−0.0252** (top-5%) | +0.0218 R | +0.0798 R | 27% |
  | sl1tp1 | −0.1019 | **−0.0295** (top-1%) | +0.0724 R | +0.1545 R | 47% |
  - **HAKUNA threshold yenye EV_R chanya** (achilia mbali kuzidi breadth). c1 imeanguka kila mahali;
    c3 (p_boot) imeanguka kwa ujenzi kwa kuwa EV<0 (p≈0.79-1.0).
  - **Signal IPO:** lift ni monotone kutoka top-20% hadi top-5%/1% kwenye geometries ZOTE MBILI,
    out-of-fold, purged. Hii SI kelele — GBM inapanga (rank) kitu halisi.
  - **Tail inarudi nyuma:** top-0.1% ni MBAYA kuliko top-5% (sl2tp1 −0.0753 vs −0.0252) — predictions
    zenye ujasiri zaidi SI trades bora. Onyo kwa yeyote atakayerudia.
  - Utambuzi (takriban, kutoka decomposition ya EV): cost/R ≈ 0.036 (sl2tp1) / 0.087 (sl1tp1) ->
    gross ≈ +0.011 / +0.058 R. **Gharama ni mara 1.5-3.3 ya gross edge** = muundo ULE ULE wa L-039
    ("discriminating diagnostic ni gross-vs-cost margin, si net pekee").
MPAKA WA MADAI (muhimu — kosa la muundo wangu wa M4-1, nalimiliki):
  Dataset ya M4-1 ina **market entry kwenye open ya bar i+1 na mwelekeo uliochaguliwa EX-ANTE**
  (ilifuata charter §6.2 "bars ZOTE"). Lakini nr7 inavyofanya kazi ni **stop-entry OCO** — soko lenyewe
  ndilo linalochagua upande kwa kuvunja. KAIROS_3_SPEC §3 inasema rules zinatoa "wapi pa kuangalia"
  (pamoja na mechanics ZAO za entry) na ML inachagua "ipi ya kuchukua". Kwa hiyo M4-2 ilipima
  **"ML inabashiri mwelekeo ex-ante kwenye kila bar ya H1"** — SI design ya spec.
  -> LESSON ni halali na imefungwa; LAKINI haiuai variant ya spec (family-pool yenye entry mechanics
     zao). Hiyo ingehitaji **pre-registration MPYA**, si re-tune ya jaribio lililoanguka.
UAMUZI (charter §5, pre-registered): **HATUA 2 (LSTM) HAIANZI.** SITARUDIA M4-2 kwa hyperparams
  nyingine — hiyo ingekuwa multiple-testing juu ya data ileile baada ya kuona matokeo (haramu §4.6).
INASUBIRI: namba ya `nr7_flag`-only (baseline ya ndani) kutoka ripoti — inaamua kama ni "ML haiwezi"
  au "bwawa la all-bars/market-entry ndilo lisilofaa".

=== 2026-08-01 (jioni) — COST BUDGET + LESSON-045 + M4-HTF registration ===
LAST COMPLETED:
  1. **cost_budget.py + config/broker_costs.yaml** (commit d878ad6) — jibu la kizuizi cha PD ("sina
     commission/swap; itatumika na brokers tofauti"): badala ya kufunga gharama za broker mmoja,
     kila strategy ina **BAJETI** (= EV yake; breakeven Δ kwa cost_stress R5(1)) na broker YEYOTE
     anapimwa dhidi yake bila backtest. Uwiano wa doctrine unapimwa kwa **GROSS/cost** (charter §4.4
     inamaanisha gross — mfano wake ni "+0.5 gross vs cost 1.5 = HASARA"), si net/cost.
     Kikomo cha commission (tradable, ≥3× gross/cost): KAIROS-1 $2.40/lot · KAIROS-2 $4.83 ·
     breadth-8 $1.93 · breadth-9 $1.27 · breadth-12 $0.00.
     **MATOKEO MAKUU: kwenye raw/ECN ($7/lot) HAKUNA strategy inayotimiza doctrine, na breadth-12
     inakufa (EV −0.04). Kwenye spread-only: KAIROS-1/2 + breadth-8/9 zote zinapita.** Aina ya
     broker ni PARAMETER ya strategy. Hii pia inathibitisha (kwa kigezo cha PILI, huru) pendekezo
     la 9/8 badala ya pairs 12.
  2. **docs/lessons/LESSON-045.md** — M4-2: taarifa ipo (lift monotone OOF), gharama ni mara 1.5-3.3
     ya gross edge. Muundo ULE ULE wa L-039 kwa data mara ~50 zaidi na mbinu tofauti. Mpaka wa dai
     umeandikwa wazi: M4-1 ilitumia market-entry + mwelekeo wa ex-ante, si stop-entry ya nr7 — kwa
     hiyo variant ya KAIROS_3_SPEC §3 (family-pool yenye entry mechanics zao) HAIJAPIMWA.
  3. **docs/M4_HTF_REGISTRATION.md** (KABLA ya namba) + `breadth_baseline.py --tf H4|D1` (additive;
     TF_SPEC yenye provenance: H4 hold24/no-LATE = C2-WATCH; D1 hold20/None = swing_family).
     Vigezo: EV_R>0 VALID · ishara isibadilike TRAIN→VALID · **gross/cost ≥ 3×** · ≥6/12 pairs ·
     trades/mwaka bila floor. Hoja: spread haibadiliki na TF, move inakua -> cost/R inashuka ~2×
     (H4) hadi ~5× (D1). Ushahidi wa awali: C2-WATCH (H4) na Swing (D1) zote zilikuwa +EV_R,
     zilianguka kwa POWER si ishara.
  Sweep 38/38. H1 outputs za M4-0 HAZIFUTWI (suffix ya TF kwa H4/D1).
NEXT: PD aendeshe `--tf H4` na `--tf D1` + `cost_budget --report`; kisha tathmini dhidi ya vigezo
  vya M4_HTF_REGISTRATION §3.

=== M4-HTF (2026-08-01) — HUKUMU: vigezo VYOTE vitano vimetimia (H4 na D1) ===
MATOKEO (PD aliendesha, NA swap — rmap.apply_swap + config; reports/breadth_baseline_{H4,D1}_swap.md):
  | TF/variant | EV_R TRAIN→VALID | EV_pips FX (VALID) | swap drag | trades/mwaka | p_boot | pairs |
  | H4 SL1/TP1 | +0.1373 → **+0.1386** | **+5.14** | 0.10 pips | 1,051 | 0.0001 | 11/12 |
  | H4 SL2/TP1 | +0.0664 → +0.0730 | +4.23 | 0.30 | 969 | 0.0001 | 11/12 |
  | D1 SL1/TP1 | +0.1885 → **+0.1856** | **+19.98** | 1.77 | 211 | 0.0005 | 8/12 |
  | D1 SL2/TP1 | +0.0823 → +0.0657 | +16.78 | 2.94 | 192 | 0.0338 | 7/12 |
  TATHMINI dhidi ya M4_HTF_REGISTRATION §3 (vigezo vilivyofungwa KABLA):
   1. EV_R>0 VALID: ✅ 4/4 · 2. ishara imara TRAIN→VALID: ✅ 4/4 (H4 SL1 imesogea 0.0013 TU) ·
   3. **gross/cost ≥3×: ✅ H4 ~8.3× / 7.0× · D1 ~9.4× / 5.7×** (H1 breadth ilikuwa 2.52×) ·
   4. ≥6/12 pairs: ✅ (11/12, 11/12, 8/12, 7/12) · 5. trades/mwaka: imeripotiwa (hakuna floor).
  -> **HTF-BREADTH NI MGOMBEA** kwa mujibu wa tafsiri iliyofungwa mapema.
KOSA LANGU LA KADIRIO (nalimiliki): nilikadiria swap ya D1 ~7 pips (usiku 14) na H4 ~1.5 (usiku 3).
  HALISI: D1 = 1.77 (≈usiku 3.5), H4 = 0.10 (≈usiku 0.2). Sababu: max_hold ni kikomo, si muda halisi —
  trades nyingi zinafunga mapema kwa TP/SL. Kadirio langu lilikuwa conservative mara ~4.
MAANA (uzito wa matokeo):
  · H4: ~1,051 trades/mwaka × +5.14 pips ≈ **~5,400 pips/mwaka**; H1 breadth ≈ 2,400; KAIROS-1/2 ≈ 1,000.
  · D1: ~211 × +19.98 ≈ **~4,200 pips/mwaka**, na msongamano wa slots hauwezi kubana (trade 1 kila
    siku 1.7 kwa pairs 12).
  · **Bajeti ya gharama inakuwa pana:** commission inayoruhusiwa (tradable ≥3× gross/cost) inapanda
    kutoka $1.9-4.8/lot (H1) hadi **~$12.5/lot (H4)** na **~$50/lot (D1)**. Aina ya broker inaacha
    kuwa kikwazo — hii ndiyo faida kubwa kuliko EV yenyewe.
  · Uthibitisho wa ndani: Swing Family (D1 nr7 × LOW-vol, NA swap) ilitoa EV_R +0.067 (N=139); sisi
    (bila filter) +0.1856 (N=422). Filter ya LOW-vol ilipunguza N mara 3 bila kuboresha EV.
  · Gold: XAUUSD IMEKATALIWA na kanuni kwenye D1 (variants zote) — EV_pips(12) ya D1 SL2 VALID ni
    −1.29 wakati FX ni +16.78. Kanuni ilifanya kazi bila mkono wa mtu.
TAHADHARI ZILIZOBAKI (zimeandikwa kwenye registration tangu mwanzo):
  · Madirisha ya H4/D1 TRAIN/VALID yameshaguswa (grid ya C2; atlas ya rmap) -> p_boot ni DESCRIPTIVE.
    HII SI ushahidi wa OOS. Kilicho na uzito ni kwamba **hypothesis (cost/R inashuka na TF)
    ilisajiliwa KABLA** na ikathibitika 2/2 TF na 4/4 variants.
  · HOLDOUT: hatua yoyote inayoigusa INAHITAJI pre-registration MPYA + idhini ya Chief/PD (historia
    ya dirisha hili ni ngumu — C2-WATCH na Swing zote zilishaligusa kwa namna zao).
NEXT (pendekezo langu): (1) PD athibitishe pairs[] + forward paper (H4 kwanza — trades nyingi zaidi,
  hakuna dirisha linalochomwa); (2) pre-registration mpya ya holdout ikiamuliwa; (3) LESSON-046 ya
  M4-HTF baada ya PD kusoma.
