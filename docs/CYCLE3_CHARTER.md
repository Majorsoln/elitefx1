# ELITEFX — CHARTER YA MZUNGUKO-3: "AI YA MAZINGIRA" (Muongozo wa PD, 2026-07-16)

**Muongozo wa PD (verbatim spirit):** tuna pairs 12; tunafanya utafiti wa KILA pair kwa set ya
strategies + mbinu tofauti, kila strategy kubadili parameters, ili kujua MAZINGIRA na mabadiliko
yake (EURUSD 2016 ≠ 2018; EURUSD ≠ symbols nyingine). Lazima tupate strategies nzuri za kila
wakati: **model inayotambua STATES**, kisha **nyingine inayojua "mazingira haya → entries/exits
zinatafutwaje"**.

**Misingi iliyobaki thabiti:** STRAT-001/002 IMMUTABLE · sacred splits (TRAIN 2016-22 / VALID
2023-24 / HOLDOUT SEALED-per-use) · costs halisi (+ swap kwa swing) · lessons 41 (hasa L-039
cost/move, L-040 correlated evidence, L-041 selection-bias→breadth) · hakuna post-hoc.

---

## TABAKA 3 ZA AI (mapping ya muongozo)

### TABAKA 1 — STATE MODEL ("model inayotambua states") — ✅ IPO
`market_state_engine` + `intraday_state_engine` + `htf_context`: kwa kila bar ya kila pair,
mfumo tayari unajua — vol regime (LOW/NORMAL/HIGH, deseasonalized), activity, spread state,
session, HTF trend/structure/momentum. Deterministic, no-lookahead, imethibitishwa. **Hii ndiyo
"macho" ya AI.**

### TABAKA 2 — RAMANI YA TABIA / R-MAP ("kujua mazingira na mabadiliko") — 🔨 KAZI 1
Utafiti wa utaratibu, TRAIN PEKEE: **events 20 za library × pairs 12 × TF {H1, H4, D1} ×
param grid ndogo**, kila trade ikiwa TAGGED na mazingira yake (vol state, session, HTF trend,
mwaka). Output: **ATLAS** — jedwali kubwa linalojibu:
  - "nr7 inafanyaje EURUSD kwenye LOW-vol 2016 vs HIGH-vol 2018?"
  - "Mechanism gani ina EV chanya kwenye mazingira gani, kwa pairs NGAPI?" (breadth — L-041)
Swing inajumuishwa: max_hold ndefu (D1 hadi bars 20 ≈ wiki 4) + **swap model** (gharama ya
kubeba usiku, config per pair, default conservative) — hoja ya PD ya "buy leo sell next week".
**ATLAS ni RAMANI, si madai:** hypothesis yoyote kutoka atlas inayotaka kuwa STRAT inapita
gate ile ile (S2 VALID multi-pair-pooled → HOLDOUT one-shot). Atlas inatumia TRAIN tu —
VALIDATION/HOLDOUT haziguswi na ujenzi wa ramani.

### TABAKA 3 — MODEL K4 ("mazingira haya → entries/exits") — 🔨 KAZI 2
Model inayojifunza kutoka trades za STRATEGIES ZILIZOTHIBITIKA (STRAT-001/002: trades maelfu
TRAIN + mamia holdout, kila moja na state-features zake za signal bar):
  - **Entry quality:** `p(win | mazingira)` — kuchuja signals; win rate inapanda kwa UCHAMBUZI
    (si jiometri ya TP/SL) → mfululizo wa hasara unafupika → daily/max-loss ya FTMO inalindwa.
  - **Exit intelligence:** kutoka trade-paths (failure_autopsy): mazingira gani trade inapaswa
    kufungwa mapema / kuachwa iende.
  - Nidhamu: train TRAIN, tune VALID, **HOLDOUT HAIGUSWI** na model yoyote; model-filtered
    strategy inathibitishwa kama strategy mpya (gate kamili) kabla ya kupandishwa.

### TABAKA 4 (deterministic, si model) — SIZING/COMPLIANCE
Risk per trade + max trades/siku vinawekwa hesabu ili mfululizo mbaya USIWEZE kuvunja
daily-loss/max-loss ya FTMO (algorithm rules, kama Master Architecture inavyotaka).

---

## MPANGILIO WA KAZI (phases)

| Phase | Nini | Nani |
|---|---|---|
| M3-1 | **Swap model** (additive kwa harness; per-night pip cost, config) + **R-MAP runner** (events×pairs×TF×params, regime-tagged, TRAIN only) | IMPLEMENTER-A |
| M3-2 | Operator: run R-MAP → ATLAS report (behavior kwa pair/mwaka/regime) | Operator |
| M3-3 | Chief + STRATEGIST-M: soma atlas → hypotheses zenye **breadth** (regime-conditional families) → S2 pooled → HOLDOUT | Chief |
| M3-4 (sambamba) | **K4 dataset builder**: kila signal ya nr7 (STRAT-001/002) TRAIN/VALID + state-features + outcome → training data | IMPLEMENTER-A |
| M3-5 | K4 model v0 (p(win|state) — rahisi kwanza: logistic/tree, interpretable) + report ya lift (win rate kabla/baada, streak reduction, EV retention) — TRAIN fit, VALID check | SCIENTIST-D design + IMPLEMENTER-A build |
| M3-6 | Model-filtered STRAT-001/002 → gate kamili → deploy paper | Chief |

**Kinga za nidhamu (zisizojadilika):** atlas=TRAIN only · kila claim OOS inapita S2-pooled-breadth
(L-041) · hakuna cell-mining (atlas inaeleza, haichagui) · K4 haioni HOLDOUT kamwe · swap/costs
ndani ya kila namba.

---

## MBINU YA PAIR-LESSONS (directive ya PD 2026-07-16: "lesson ya kufundisha KILA pair
## how to entries and exit at highest probability")

Kutoka atlas + trade-paths, kwa **KILA pair kati ya 12** tunazalisha somo lake rasmi
(`docs/pair_lessons/LESSONS_<PAIR>.md` — human-readable NA machine-readable kwa models):

**A. ENTRY LESSONS (highest probability):**
   - Kutoka R-MAP: mechanisms × mazingira (vol/session/trend/mwaka) zenye win% na EV ya juu
     kwa pair HIYO — ranked kwa STABILITY (miaka mingapi chanya, L-010) si kwa cell moja bora.
   - Kila lesson ina namba: "EURUSD: nr7 hushinda 58% kwenye NORMAL-vol + London + D1-trend,
     lakini 31% kwenye HIGH-vol LATE" — hiyo ndiyo elimu ya model ya entries.

**B. EXIT LESSONS (kutoka trade-paths — MFE/MAE):**
   - Kwa kila trade ya atlas: **MFE** (faida kubwa iliyofikiwa kabla ya exit) na **MAE**
     (hasara kubwa iliyopitiwa) — zinahesabiwa na helper additive (episodes HAIGUSWI).
   - Maswali yanayojibiwa kwa kila pair×mazingira: washindi hufikia kilele lini (bars ngapi)?
     walioshindwa huwa hawarudi baada ya MAE gani? timeout-trades zilikuwa na MFE gani
     iliyopotea? → sheria za exit: "USDJPY LOW-vol: chukua 1.5R ndani ya bars 8, usisubiri" /
     "trade iliyofika -0.7R kwenye HIGH-vol hurudi 12% tu — funga mapema".

**C. NIDHAMU YA LESSON:** lesson yoyote inayotaka kuwa SEHEMU YA STRATEGY/live inapita gate
   (S2 pooled breadth → HOLDOUT). Lessons ni elimu ya TRAIN kwa models — si ruhusa ya kutrade
   bila uthibitisho. Format: kila lesson ina evidence (namba+chanzo), validity_conditions,
   when_to_use/when_not (muundo ule ule wa docs/lessons).
