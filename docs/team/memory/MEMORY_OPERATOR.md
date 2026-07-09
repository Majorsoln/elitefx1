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
