# MEMORY — OPERATOR (Project Director, Japhet)

IDENTITY: Binadamu pekee wa timu. PC ya data (~26GB), runs, prompts za agents, commits, final decision.
RUNBOOK LOG (kila run: tarehe · amri · matokeo — jaza baada ya kila run):

## PENDING RUNS (kutoka kwa Chief)
1. **F-005 full-metric re-run** (debt rasmi tangu V11) — itapata runbook ya Chief kabla ya run.
2. Hakuna nyingine kwa sasa — data runs mpya zitakuja na E-series/K4.

## KAZI ZAKO ZA SASA (2026-07-04)
1. (Dakika 5, mara moja) GitHub: ipa **Claude GitHub App write access** kwenye Majorsoln/elitefx1;
   kisha **revoke PAT** ulizotuma kwenye chat (mbili zinaonekana historia).
2. Fungua session mpya ya AI na prompt ya **RESEARCHER-K** (docs/team/PROMPTS.md) — K1 batch 3.
3. Fungua session mpya na prompt ya **IMPLEMENTER-A** — E1 spec.
4. Matokeo yakija: yaletee Chief (session hii au mpya na prompt ya Chief) kwa review.

## LOG
- 2026-07-04: Team system imeundwa; hakuna run iliyofanyika bado.

## RUNBOOK HAI (2026-07-05): Paper Validation
Chief amejenga `src/research/e2e_paper_demo.py` (smoke test ya mnyororo mzima; CI PASS) + runbook
`docs/RUNBOOK_paper_validation.md`. KAZI YAKO: fuata runbook hatua 1-5 kwenye PC yako, bandika
output kwa Chief. Hii ndiyo mtihani wa kwanza wa mashine nzima kwenye stack halisi.

## LOG — 2026-07-06
- **PAPER SMOKE TEST: PASS** kwenye PC ya Operator (Windows). e2e_paper_demo.py end-to-end OK
  (A:FILLED+settled, B:FTMO REJECTED, C:ABSTAIN; records 7, integrity ok). HATUA 3 (bash loop)
  ilikwama Windows → Chief ametoa `run_selftests.py` (cross-platform, 10/10 PASS CI).
  KAZI YAKO IJAYO: `cd src/research && python run_selftests.py` → bandika output (thibitisho la
  self-test sweep kwenye stack yako). Kisha: Audit #6 + real-data runbook.

## RUNBOOK HAI (2026-07-07): Real-Data Validation
`docs/RUNBOOK_real_data_validation.md` + `src/research/real_data_paper_run.py` (harness — inajenga
snapshots kutoka ticks halisi via build_tagged_evidence → decision → gate → repository). KAZI YAKO:
(1) hakikisha states zipo (market_state_engine.py kama inahitajika); (2) endesha
`python real_data_paper_run.py --policy conservative` (+ capital_preservation + aggressive);
(3) bandika output. Tegemeo: ABSTAIN nyingi = SAHIHI (protect capital). SIO edge claim.

## LOG — 2026-07-07 (REAL-DATA VALIDATION: PASS)
Snapshots 5 halisi × policies 3. capital_preservation=5 ABSTAIN; conservative=4 SELECT+1 ABSTAIN;
aggressive=4 SELECT+1 HEDGE. Gate: SELECT zote VALIDATED; integrity ok. Mashine + data halisi = OK.
UAMINIFU: SELECT ≠ trade nzuri (policies illustrative; edge = OOS, haijafanywa). Kazi ijayo:
paper-trading run ya mfululizo (time-ordered) au K4 datasets (E3 outcomes = training data).

## RUNBOOK HAI (2026-07-08): EVENT QUALITY — entries V1 vs V2 (TRAIN 2016-2022) — KIPAUMBELE
Chief amejenga mwenyewe `event_library_v2.py` (**entries 16, familia 7**: edge-trigger+rearm,
stop-entries halisi za intrabar, session ORB ya London, volume filter kwa `tc`, ATR-stretch MR,
+ mbinu mpya 5: rsi2_pullback/bb_fade/engulf_extreme/inside_break/nr7_break)
+ `event_quality_report.py` (harness ya haki: episode non-overlap, SL/TP za ATR, costs halisi
kila trade; jedwali la entries × VOLATILITY STATE + sessions = entry ndani ya uchambuzi wa soko;
inaKATA ts>=2023 YENYEWE — sacred splits). Sweep 14/14 PASS CI. KAZI YAKO: fuata
`docs/RUNBOOK_event_quality.md`: git pull → `python run_selftests.py` (14/14) →
`python event_quality_report.py` → commit `reports/event_quality_report.md` → ripoti
**"tayari event quality"**. Ripoti hii inalisha grid ya S1 (IMPLEMENTER-A).

## RUNBOOK HAI (2026-07-07): FORWARD Paper-Trading — TAYARI KUTUMIA
`paper_trader.py` (Chief direct; self-test 4/4 + sweep 12/12). Kila signal yako ya MWONGOZO:
  python paper_trader.py --signal PAIR SIDE ENTRY SL TP     (mashine: decide+gate+size+fill+log)
  python paper_trader.py --close paper:N --price P          (settlement + bajeti ya siku)
  python paper_trader.py --status                           (hali ya akaunti ya paper)
Log: data/paper/paper_log.jsonl (COMMIT kila siku = pre-registration ya umma). Tathmini rasmi ya
Chief baada ya siku 20+/trades 30+. HAKUNA pesa halisi.

## LOG — 2026-07-09 (S0 EVENT QUALITY: DONE)
Venv repair (numpy/duckdb/pyarrow force-reinstall; snapshot: src/research/requirements.txt) →
sweep 14/14 → event_quality_report (TRAIN, H1, pairs 9, ~500k episodes) → committed (eace58d).
Chief review: nr7_break = nyota (chanya pairs 5; LONDON/NY/HIGH-vol kali); pockets: second_chance
×EURJPY, shock_follow×EURJPY/USDJPY, session_orb×USDJPY, inside_break×USDJPY. S1 grid ruling
imeandikwa kwenye MEMORY_IMPLEMENTER_A. KAZI YAKO IJAYO: fungua session ya IMPLEMENTER-A
(prompt: docs/team/PROMPTS.md) — memory yake ina QUICK-WIN (OOS-confirm 017/018) + S1 spec +
grid ruling. Paper-trading ya kila siku inaendelea.

## RUNBOOK HAI (2026-07-09): S1 STRATEGY LAB — TRAIN run
strategy_lab.py iko tayari (IMPLEMENTER-A + Chief fixes 2; sweep 15/15). KAZI YAKO:
  git pull
  cd src\research
  python run_selftests.py                REM tegemeo: 15/15 PASS
  python strategy_lab.py --split train   REM S1: grid cells ~2000 juu ya TRAIN (dakika kadhaa)
  REM commit: reports/strategy_lab_report.md + data/strategies/candidates.jsonl
Ripoti: "tayari S1". Chief atakagua candidates + kufunga registration, KISHA ndiyo
--split validation (S2 + FDR — hukumu). USIENDESHE validation kabla ya review ya Chief
(nidhamu ya pre-registration; kuepuka forking paths).

## LOG — 2026-07-09 (S1 TRAIN: DONE; REGISTRATION FROZEN) + RUNBOOK HAI: S2 VALIDATION
S1: cells 2,004 → candidates 2,004 (EV>0: 805). nr7_break×(LONDON,NY) = 216/216 chanya. Chief
amefunga registration (grid+code frozen). KAZI YAKO SASA (S2 — hukumu, amri moja):
  git pull
  cd src\research
  python strategy_lab.py --split validation
  cd ..\..
  git add reports\strategy_lab_report.md data\strategies\candidates.jsonl
  git commit -m "S2 validation + FDR" && git push origin main
Ripoti: "tayari S2". Ripoti itakuwa na sehemu ya FDR (survivors + wangapi kwa bahati) —
strategy za kwanza RASMI zinaweza kuzaliwa hapa (au kufa kwa heshima; zote mbili ni sayansi).

## LOG — 2026-07-09 (S2: DONE — SURVIVOR 1/1,939!) + RUNBOOK: S2 re-run (kumtaja survivor)
FDR imepitisha strategy MOJA kati ya 1,939 (kwa bahati ~0.1 — huyu ana nguvu halisi). Defect ya
reporting: hakutajwa kwa jina. Chief amerekebisha (survivors sasa wanaandikwa + p-values kwenye
jsonl). Run ni deterministic — namba zilezile, jina linaonekana. KAZI YAKO (dakika ~5):
  git pull
  cd src\research
  python strategy_lab.py --split validation
  cd ..\..
  git add -A && git commit -m "S2 re-run: survivor named" && git push origin main
Ripoti: "tayari S2b". Kisha Chief anafunga registration ya S3 (holdout — mara MOJA tu).

## LOG — 2026-07-09 (S2b: SURVIVOR = STRAT-001) + KAZI ZAKO MPYA
**STRAT-001: nr7_break × USDCHF · H1 · SL 2.0×ATR / TP 1.0×ATR · no-LATE (usiingie saa 17-23
server) · vol yoyote.** VALID: EV +3.07/trade net, win 79.3%, N=425, ~0.8 tr/siku, p=9e-06
(1/1,939 FDR). TRAIN pia chanya (N=1,607, win 71%). STATUS: CANDIDATE-VALIDATED.
KAZI ZAKO (mpangilio):
  1. **DATA ya S3 (blocker):** pakua ticks 2025-01 → 2026-06 kutoka chanzo chako kilekile
     (angalau USDCHF; bora pairs zote 9) → endesha market_state_engine kuzalisha states.
     Ripoti "data 2025-26 tayari" — Chief atakupa token ya S3 (one-shot).
  2. **Paper-trading ya STRAT-001 (sasa, sambamba):** kila bar ya H1 ya USDCHF yenye range
     nyembamba zaidi ya bars 7 (NR7), na saa si 17-23: weka stop pande zote (high+0.1 pip /
     low−0.1 pip); ikigusa: SL=2×ATR14, TP=1×ATR14, timeout 24 bars → paper_trader --signal
     kama kawaida. Hii ni forward OOS ya ziada — haipotezi holdout.
  3. RESEARCHER-K session (Track B): lessons mbili mpya za S2 zimo kwenye memory yake.

## RUNBOOK HAI (2026-07-09): S3 HOLDOUT — ONE-SHOT (token imetolewa)
Holdout window IMEFUNGWA: 2025-01 → 2026-04 (05-06/2026 hazipo — zitakuwa forward-monitoring).
HATUA (mpangilio MKALI):
  1. Ingiza ticks mpya (2025-01→2026-04) kwenye store ileile ya raw → endesha
     market_state_engine (states sasa zitafika 2026-04).
  2. INTEGRITY GATE (lazima kabla ya S3):
       cd src\research
       python strategy_lab.py --split validation
       cd ..\..  &&  git diff --stat data/strategies/candidates.jsonl
     Tegemeo: HAKUNA tofauti (byte-identical na iliyokwisha-commit). Ikitofautiana → SIMAMA,
     bandika diff kwa Chief. USIENDELEE hatua 3.
  3. S3 ONE-SHOT (mara MOJA pekee):
       cd src\research
       python strategy_lab.py --split holdout --holdout-final CHIEF-HOLDOUT-S3
  4. Commit ripoti + jsonl → push → ripoti "tayari S3".
KUMBUKA: hukumu = STRAT-001 PEKEE (EV>0 na p<0.05). Cells nyingine zote za holdout = SEALED
(hazizai candidates; hazitumiki kwa selection). Paper-trading ya STRAT-001 inaendelea sambamba.

## LOG — 2026-07-09 (S3: ✅ PASS — STRAT-001 NI STRATEGY RASMI YA KWANZA)
Holdout: N=303, EV +1.92 net, win 73.9%, PF 1.31, p=0.021 (criterion imepita). KAZI ZAKO:
  1. THIBITISHA kwa neno moja: integrity gate (hatua 2 — validation re-run) ilionyesha diff
     TUPU kabla ya holdout? (rekodi ya kisayansi inahitaji neno lako.)
  2. Fungua session ya IMPLEMENTER-A — S4 task (strat001_signal.py + policy) imo memory yake.
  3. Endelea paper-trading STRAT-001 kila siku (baada ya tool ya 2 itakuwa rahisi zaidi).
  4. Session ya RESEARCHER-K — sasa lessons 3 (L-a, L-b, L-c) zimo memory yake.

## LOG — 2026-07-09 20:26 (INTEGRITY GATE: PASS CONFIRMED)
Re-run ya validation baada ya state rebuild = byte-identical na e1a0d27 (diff TUPU; screenshot).
S3 rekodi imefungwa BILA masharti. STRAT-001 anasimama imara. Kazi zilizobaki: IMPLEMENTER-A
session (S4: strat001_signal.py + policy), RESEARCHER-K session (lessons 3), paper-trading kila siku.

## LOG — 2026-07-09 (S3b: 3/5 PASS — STRAT-002 AMEZALIWA)
**STRAT-002 = nr7_break × USDJPY · H1 · SL 1.0×ATR / TP 1.0×ATR · no-LATE** (holdout: N=327,
EV +2.65, win 57.8%, p=0.029). USDCHF plateau (SIB-1/3) inathibitisha STRAT-001; EURUSD FAIL;
GBPUSD underpowered (forward candidate). PORTFOLIO YA PAPER SASA: STRAT-001 (USDCHF) +
STRAT-002 (USDJPY) = ~1.6 trades/siku. KAZI: paper-trade ZOTE MBILI kila siku (NR7 + no-LATE;
USDJPY: SL=TP=1×ATR14). IMPLEMENTER-A session: S4 tool sasa i-cover strategies zote mbili
(memory yake ime-update).

## LOG — 2026-07-09 (CYCLE-2 OPENED) + KAZI
Events mpya 4 (gap_fade, london_drift, squeeze_break, nr4_inside) + charter ya C2 (CHIEF_STATUS).
KAZI MPYA: (a) angalia chanzo chako cha ticks kama kina XAUUSD / GBPJPY / EURCHF — ripoti
"pairs mpya zinapatikana: ..."; (b) endelea kukusanya data mpya kila mwezi (2026-05+ = OOS ya
baadaye ya compression/shock C2); (c) IMPLEMENTER-A: S4 tool kwanza, kisha C2 tasks (memory yake).

## RUNBOOK HAI (2026-07-09): SIGNAL TOOL ya kila siku (S4 — APPROVED, sweep 17/17)
Paper-trading yako sasa ni nusu-otomatiki. Kila siku (au kila bar ya H1 ikifunga):
  cd src\research
  python strat_signal.py --all --bars-dir <dir yenye USDCHF.parquet na USDJPY.parquet>
  (au: python strat_signal.py --pair USDCHF --bars <path.parquet au .csv>)
Tool inakuambia: kama kuna NR7 + no-LATE -> inakupa amri KAMILI za paper_trader --signal
(entry/SL/TP zimehesabiwa). Weka OCO stops MT5 (demo); ikijaza moja, futa nyingine, endesha
amri ya paper_trader iliyotolewa. Ikifika TP/SL: paper_trader --close. Commit data/paper/ kila siku.

## RUNBOOK HAI (2026-07-09): CYCLE-2 TRAIN RUNS + GOLD ACTIVATION
C2 build APPROVED (sweep 18/18). KAZI (mpangilio; commit BAADA ya kila run — files za _c2):
  0. GOLD: ongeza "- XAUUSD" kwenye config pairs (metals support iko sasa) →
     python market_state_engine.py --symbol XAUUSD   (states za gold; guard imefunguliwa kwa XAU)
  1. cd src\research && python strategy_lab.py --cycle 2 --split train
     → commit "S1-C2 train H1" (candidates_c2.jsonl + report)
  2. python strategy_lab.py --cycle 2 --tf H4 --split train
     → commit "S1-C2 train H4"   (NB: inaandika juu ya _c2 files - ndiyo maana commit kati)
  3. python strength_lab.py       → commit "strength exploration (TRAIN)"
Ripoti: "tayari S1-C2". Chief atakagua + kufunga registration ya S2-C2 (USIENDESHE validation).
Paper-trading ya STRAT-001/002 inaendelea kila siku.

## LOG — 2026-07-10 (MWANACHAMA MPYA: SCIENTIST-D — directive yako)
Chief ametengeneza SCIENTIST-D (institutional data scientist / external reviewer huru — hafungwi
na doctrine kwenye uchambuzi). Prompt: docs/team/PROMPTS.md (mwisho). Memory yake ina mfumo mzima
+ matokeo YOTE (pass/fail) + access ya raw artifacts + udhaifu unaoshukiwa. KAZI YAKO: fungua
session MPYA ya AI na prompt ya SCIENTIST-D → atasoma mwenyewe → ataandika
reports/data_science_review.md (udhaifu wa njia yetu + nini tufanye) → "tayari SCIENTIST-D" →
Chief atajibu ripoti hoja kwa hoja mbele yako (PD ndiye msuluhishi wa migongano).

## LOG — 2026-07-12 (SOMO: branch-hygiene ya agents; SCIENTIST-D design bado)
Session ya SCIENTIST-D ilifanya kazi kwenye branch ya zamani (data-science-review-n3dm9l) yenye
memory ILIYOPITWA -> ilirudia review ya kwanza (commit 2081453) badala ya task mpya (family-pooled
design, iliyoko main 1a3d314). Chief ameongeza "SYNC KWANZA: git checkout main && git pull" kwenye
prompts zote. KAZI: fungua SCIENTIST-D session UPYA baada ya git checkout main && git pull ->
atasoma task ya family-pooled design -> commit+push -> "tayari design".
