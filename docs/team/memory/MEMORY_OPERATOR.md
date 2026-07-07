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
