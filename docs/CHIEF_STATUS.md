# CHIEF_STATUS.md — ELITEFX Live Status

> **Owner: Chief Quant #2** (Doctrine Custodian — G-01). Hii ndiyo "tuko wapi sasa" ya mradi —
> ina-update kila uamuzi wa Chief/Project Director.
> Last updated: 2026-07-08.

---

## Current Phase

```text
MASTER ARCHITECTURE V1 — TRACKS MBILI SAMBAMBA (updated 2026-07-07 baada ya Audit #6)
TRACK A (Engineering):    E1-E4 ZOTE CLOSED (paper). Validated PC ya Operator (sweep 11/11).
                          Audit #6 PASS. **P107 RESOLVED** (core transitively PURE; purity_check).
                          KAZI HAI: real-data runbook (snapshots kutoka ticks halisi).
**ALPHA ENGINEERING (S-series) — OPENED 2026-07-08 (directive ya Project Director; Master V1
s8.2 knowledge-need):** S1 Strategy Factory (events x pairs x params, backtest+costs, TRAIN) ->
S2 Validation (walk-forward 2023-24 + FDR) -> S3 Holdout proof (2025+, mara moja) -> S4 Deploy
(policies + K4 training data). QUICK WIN kwanza: OOS-confirm LESSON-017/018 (candidates za Phase 12).
**S0 (Chief direct, 2026-07-08): EVENT LIBRARY V2** — ukaguzi wa Chief ulipata defects 4 kwenye
entries za V1 (D1 conditions-sio-events [334/1000 bars, spread kila bar -> Phase 12 EV negative];
D2 uaminifu wa KJ umepotea [stop-entries #3/#4, percentile #5, volume filter #8]; D3 hakuna
session structure; D4 pockets P100/P97 bila toleo kali; D5 [PD 2026-07-09] KJ-9 si ulimwengu
wote). Zimejengwa: event_library_v2.py (**entries 16, familia 7**: edge-trigger+rearm,
stop-entries intrabar, session ORB, mr_zscore, trend_resume, + mpya 5: rsi2_pullback/bb_fade/
engulf_extreme/inside_break/nr7_break) + event_quality_report.py (harness ya haki V1-vs-V2:
episode non-overlap, SL/TP za ATR, tie->SL, costs kila trade, TRAIN<2023 enforced; entries
zinapimwa NDANI ya uchambuzi wa soko: x volatility_state + x session). Sweep 14/14 PASS.
Operator: RUNBOOK_event_quality.md. S1 grid = EVENTS_V2 + context dimension (memory ya
IMPLEMENTER-A ime-update). Kanuni: ENTRY = trigger; UCHAMBUZI = context (states/session/age);
AI inajifunza ramani context->event->outcome (K4), sio triggers peke yake.
TRACK B (Knowledge & AI): K0-K3 ✅ — corpus 36 (34 ACTIVE) · GRAPH@v7 (172/202) · EVAL-SUITE 25 Qs.
                          KAZI HAI: batch 7 + GRAPH@v8 (kufunga K1 retroactive).
Governance:               Chief Quant (Unified) — directive ya Project Director. Board Approval
                          Log + roadmap zimesawazishwa na Audit #6 (governance lag imefungwa).
```

## Doctrine of Record

| Domain | File | Status |
|--------|------|--------|
| **Supreme** | `ELITEFX MASTER ARCHITECTURE V1.md` | ACTIVE (Tracks A+B; governance §6; mabadiliko §8) |
| Market | `ELITEFX DOCTRINE V6.9.md` | FROZEN → reopenable-by-knowledge-need (V1 §8.2) |
| Decision | `ELITEFX DECISION DOCTRINE V12.md` | ACTIVE |
| **Entry** | `ELITEFX ENTRY DOCTRINE V1.md` | **ACTIVE (NEW 2026-07-09)** — familia 7 · entries 16 (EVENTS_V2) · context layer · EP-1..EP-7 · njia S0→S4 |
| Governance | `docs/PROGRAM_BOARD.md` (G-01 + roles + workflow) | ACTIVE |

## Roadmap (STRICT ordering — V11)

```text
E1-E4  ✅ CLOSED (paper) — Integrity Gate · Execution Object · Repository · Broker Adapter
       validated PC ya Operator (11/11) · Audit #6 PASS · P107 RESOLVED
INAYOFUATA (Track A):  real-data validation ✅ → K4 datasets (rekodi halisi → training) au
                       OOS-validation rasmi (pre-reg+FDR) — SIO naive PnL backtest (Chief judgment)
                       → (baadaye, kwa proof + PD approval) paper-trading live → Production
INAYOFUATA (Track B):  K1 batch 7 + GRAPH@v8 (funga retroactive) → K4 Datasets → K5 (EVAL→RAG→SFT)
Baadaye (Decision Sci): P96 Policy Selection · P70 confidence model (RED LINE) · P78 redundancy
NOT YET ELIGIBLE:      D8 Decision Quality/Outcome · D9 Portfolio/Live
GATED:                 Trading-ML (evals + OOS + Project Director) · live money (artifact ya PD)
```

## Validation Log

- **2026-07-06 — PAPER SMOKE TEST: PASS kwenye PC ya Operator (Windows).** Mnyororo mzima
  (Snapshot→Engine→Gate→Broker→Execution→Repository→Settlement) umetembea end-to-end kwenye
  stack halisi: [A] FILLED+settled · [B] FTMO REJECTED (mtaji umelindwa) · [C] ABSTAIN;
  repository lineage/integrity ok. **Mara ya kwanza mfumo mzima unakimbia nje ya CI.** Self-test
  sweep 10/10 (via `run_selftests.py`, cross-platform). Inayofuata: Audit #6 → real-data runbook.
- **2026-07-06 — SELF-TEST SWEEP: 10/10 PASS kwenye PC ya Operator (Windows, cp1252 fix).**
  Modules zote 9 + e2e_paper_demo zimethibitishwa kwenye stack halisi ya Operator. **TRACK A
  imethibitishwa end-to-end kwenye mkono halisi — SI CI tu.** Hatua inayofuata: AUDIT #6.

- **2026-07-07 — REAL-DATA VALIDATION: PASS kwenye PC ya Operator.** Snapshots 5 halisi
  (breakout/deep_pullback/mean_reversion/pullback/trend_continuation) kutoka states za ticks
  (9 pairs × H1-D1, 2016-2024). Policy-injection kwa data halisi ilionyesha tabia TOFAUTI:
  capital_preservation → 5 ABSTAIN · conservative → 4 SELECT + 1 ABSTAIN · aggressive → 4 SELECT
  + 1 HEDGE (deep_pullback = INVALID readiness). Gate: SELECT zote VALIDATED (akaunti safi);
  repository integrity ok (provenance → snapshot halisi). **Mashine inasoma evidence halisi na
  policies zinabadilika kwa usahihi.**
  ⚠️ **UAMINIFU (Chief):** SELECT hapa = "evidence READY + thresholds za policy zimefikiwa" —
  SIO "trade yenye faida". Policies ni ILLUSTRATIVE (R-2; D5 CLOSED = architecture, SIO edge;
  RED LINE reliability ≠ probability). SELECT 4 SI trades 4 nzuri. Edge = OOS proof (haijafanywa).
  **OBSERVATION:** conservative ime-SELECT 4/5 READY → threshold zaweza kuwa permissive (echo ya
  R-2 saturation + Phase-3 ~99%-permissive); capital_preservation ndiyo guard halisi. Policy
  validation = kazi ya baadaye (D8/OOS), SIO sasa.

- **2026-07-07 — DETERMINISM confirmed:** real-data run × 2 = output byte-identical (pure/
  deterministic end-to-end kwa data halisi). **CHIEF JUDGMENT (doctrine-consistent):** HATUTAFANYI
  naive paper-trading PnL run juu ya 2016-2024 kwa policies illustrative — PnL in-sample bila OOS/FDR
  = mtego wa LESSON-001/002/029 (Chapter 1: 0/282 survived FDR). Namba nzuri ingeshawishi edge isiyopo.
  Njia zenye nidhamu: K4 Datasets (rekodi halisi → training data) au OOS-validation rasmi (pre-reg+FDR),
  SIO naive backtest. Edge = OOS proof + Project Director approval kabla ya pesa.

- **2026-07-09 — S0 EVENT QUALITY RUN: DONE kwenye PC ya Operator (TRAIN 2016-2022, H1, pairs 9,
  episodes ~500k).** Matokeo makuu (IN-SAMPLE TRAIN — sio edge claims; S2 FDR ndiyo hukumu):
  (1) **nr7_break (familia F3, MPYA) = nyota ya S0**: aggregate −0.108 (bora kuliko zote; PF 0.99),
  chanya kwenye pairs 5 (GBPUSD +0.91 n=2246 · AUDUSD +0.57 n=2569 · EURGBP +0.35 · USDJPY +0.25 ·
  EURUSD +0.14), **session-structure kali: LONDON +2.23 / NY +2.64 / ASIA +0.59 / LATE −1.26**, na
  **HIGH vol +0.71 (n=7692)**. Mantiki inashikamana: compression inalipuka pale participation
  inapoingia — mechanism-consistent, sio data-mining artifact ya wazi. (2) Pockets nyingine chanya:
  second_chance×EURJPY +1.57 · shock_follow×EURJPY +1.17 / ×USDJPY +0.38 (ASIA +0.99) ·
  session_orb×USDJPY +0.52 · inside_break×USDJPY +0.47. (3) **Stop-breakout entries za bei ghali**:
  jump_off −4.49 na breakout_stop −2.85 aggregate — breakout inalipa spread+slippage+adverse
  selection kwa SL/TP 1.5/1.5; watajaribiwa S1 kwa TP 2-3R kabla ya kuuawa. (4) V1 zote negative
  (kama Phase 12) — D1-fix imepunguza trades/siku bila kuharibu ulinganifu. TAHADHARI ya Chief:
  cells 144+ zimeangaliwa — rows chanya za juu zinaweza kuwa bahati; kazi ya S2 (FDR) kuamua.
  Uamuzi wa Chief: S1 grid TIER-1 = nr7_break (+session/vol filters), second_chance, shock_follow,
  session_orb, inside_break, rsi2_pullback; wengine TIER-2/kwa ukamilifu.

- **2026-07-09 — S1 STRATEGY FACTORY RUN: DONE (TRAIN) + S2 REGISTRATION FROZEN (Chief).**
  Grid cells 2,004 (pre-registered kwa code) juu ya TRAIN 2016-2022: candidates 2,004 (min N=50),
  EV>0 = 805 (40%). Muundo: **nr7_break inatawala** (cells chanya 530; na filter (LONDON,NY) =
  **216/216 chanya**, no-LATE 203/216, bila filter 111/216 — gradient ya mechanism inashikamana);
  top: nr7×GBPUSD (LONDON,NY)×HIGH EV +7..+13 net (PF 1.4-1.9, N 168-532), nr7×USDCAD/AUDUSD/
  EURUSD; shock_follow×EURJPY ASIA (+8.5..+9.5, N=50); second_chance×EURJPY LATE (+6.3..+7.5).
  **UAMINIFU:** top rows = max order-statistics za cells 2,004 in-sample — shrinkage kubwa OOS
  inatarajiwa; hukumu = S2. **REGISTRATION FROZEN (uamuzi wa Chief):** S2 = grid ILEILE, code
  ILEILE (hakuna mabadiliko yoyote kati ya sasa na S2 run; mabadiliko yoyote = re-registration),
  juu ya VALIDATION 2023-2024, BH-FDR q=0.10 juu ya cells zote. Prediction ya wazi (falsifiable):
  kama familia ya nr7_break itasalia na muundo uleule (GBPUSD/USDCAD/AUDUSD, LONDON+NY) baada ya
  FDR → mechanism ni halisi; isiposalia → LESSON mpya ya kupinga. S2 run = Operator (amri moja).
  NB ya S2 scope: validation ni window moja 2023-24 + FDR (OOS-confirmation); rolling walk-forward
  kamili = uboreshaji wa baadaye (S2.1) kama itahitajika.

- **2026-07-09 — S2 VALIDATION + FDR: DONE (hukumu ya kwanza ya OOS katika historia ya mradi).**
  Grid frozen (cells 2,004) juu ya VALIDATION 2023-24: candidates 1,939. **BH-FDR q=0.10 →
  SURVIVOR 1/1,939** (kwa bahati wangetarajiwa ~0.1 — yaani survivor huyu ana uwezekano mkubwa
  wa kuwa HALISI). Tathmini ya prediction ya Chief (iliyorekodiwa kabla): **familia ya nr7_break
  IMESALIA kileo** — inatawala top ya validation vilevile — LAKINI uongozi wa pair ULIZUNGUKA:
  TRAIN kiongozi = GBPUSD (LONDON,NY); VALIDATION kiongozi = USDJPY (HIGH vol, hasa bila session
  filter; GBPUSD (LONDON,NY) HIGH ilibaki chanya +8..+13 lakini N=30 tu kwa miaka 2). shock_follow
  ASIA pia ilizunguka EURJPY→USDJPY. **LESSON-material (Track B): mechanism ya familia hudumu OOS;
  ranking ya pair huzunguka — thibitisha familia, sio pair.** engulf_extreme×EURJPY imejitokeza
  fresh validation (haikuwa TRAIN top → mtuhumiwa wa bahati; FDR haikumpitisha).
  **AMENDMENT ya reporting (statistics HAZIKUGUSWA):** ripoti ya S2 ilisema "1 survivor" bila
  kumtaja (defect ya write_outputs); imerekebishwa — survivors sasa wanatajwa kwa jina + p-value
  kwenye report na jsonl (self-test 5b). Re-run ya validation (deterministic) inahitajika
  kumtaja survivor → registration ya S3.

- **2026-07-09 — S2b: SURVIVOR AMETAJWA — REGISTRATION ya S3 (STRAT-001).**
  **STRAT-001 = nr7_break × USDCHF · H1 · SL 2.0×ATR / TP 1.0×ATR · filter: no-LATE · vol: ALL.**
  VALIDATION 2023-24: N=425, EV **+3.07 pips net**, win **79.3%**, PF 1.61, ~0.8 trades/siku,
  p=9.0e-06 (pekee aliyeshinda BH-FDR q=0.10 kati ya 1,939; kwa bahati ~0.1).
  **COHERENCE (TRAIN 2016-22): chanya PIA** — N=1,607, EV +0.36, win 71.1%, PF 1.05, 0.88 tr/siku.
  Profile ya edge halisi: SIYO nyota ya in-sample (aliepuka mtego wa max-order-statistic),
  bali thabiti pande zote mbili, N kubwa, mwelekeo uleule. Muundo: high-win/small-target
  (TP 1×ATR, SL 2×ATR; breakeven ~68% dhidi ya observed 71-79%) — FRAGILITY kuu = win% decay;
  monitoring ya lazima. STATUS: **CANDIDATE-VALIDATED** (bado SIO strategy rasmi — S3 inasubiri).
  **S3 BLOCKER (data):** holdout = 2025+ lakini ticks za PC ya Operator zinaishia 2024 →
  Operator apakue ticks 2025-01 → 2026-06 (chanzo kilekile, angalau USDCHF; bora pairs zote),
  aendeshe market_state_engine, KISHA one-shot S3 kwa token ya Chief. Criterion ya S3
  (pre-registered): STRAT-001 pekee, EV>0 NA p<0.05 (single test — hakuna multiple comparison).
  SAMBAMBA (haipotezi holdout): STRAT-001 inaingia forward paper-trading (paper_trader).
  Track B: LESSON mbili mpya kwa RESEARCHER-K — (a) mechanism ya familia hudumu OOS, ranking ya
  pair huzunguka; (b) FDR huchagua N+consistency, si flashy EV.

- **2026-07-09 — S3 PRE-REGISTRATION (imefungwa KABLA ya kuona holdout; Chief token imetolewa).**
  (1) **HOLDOUT WINDOW = 2025-01-01 → 2026-04 (data zote za >=2025 zilizopo).** Miezi 05-06/2026
  haipo kwa Operator — itakuwa forward-monitoring baadaye, SIO sehemu ya S3. Kwa ~0.8 tr/siku
  tunatarajia N≈300+ kwa STRAT-001 — inatosha kwa single test.
  (2) **CRITERION (STRAT-001 PEKEE):** EV>0 NA p<0.05 (one-sided, single test). PASS → strategy
  RASMI ya kwanza (inaenda S4). FAIL → STRAT-001 anakufa kwa heshima + LESSON; HAKUNA "kujaribu
  mwingine kwenye holdout".
  (3) **SEAL YA HOLDOUT:** run ya S3 itaendesha grid nzima (code frozen — hatubadilishi chochote),
  LAKINI matokeo ya cells NYINGINE ZOTE za holdout ni SEALED: hayawezi kuzalisha candidate yoyote
  mpya, hayawezi kutumika kwa selection, hayarejelewi kwenye ripoti za mbele. Strategy yoyote
  mpya ya baadaye inaanza S1/S2 upya kwa data mpya. (Hii inazuia post-hoc selection juu ya
  holdout — RED LINE ya Master V1 + LESSON-002.)
  (4) **INTEGRITY GATE kabla ya S3 (lazima):** baada ya kuongeza ticks mpya na ku-rebuild states,
  Operator ata-RE-RUN --split validation na kulinganisha na iliyokwisha-commit (byte-identical
  inatarajiwa — computations zote ni trailing/no-lookahead). Ikitofautiana → SIMAMA, ripoti
  (data-source inconsistency); S3 HAIFANYIKI hadi ieleweke.

- **2026-07-09 — S3 HOLDOUT (one-shot): HUKUMU = ✅ PASS — STRAT-001 NI STRATEGY RASMI YA KWANZA
  YA ELITEFX (PROVEN-OOS).** Holdout 2025-01→2026-04 (data mpya kabisa, haijawahi kuwepo mfumoni):
  **N=303 · EV +1.92 pips net · win 73.9% · PF 1.31 · 0.87 tr/siku · maxDD 221 pips ·
  p=0.0209 < 0.05 ✓ na EV>0 ✓** (criterion pre-registered, single test). Uthabiti vipindi VITATU:
  TRAIN +0.36 (N=1,607, win 71.1%) · VALID +3.07 (N=425, 79.3%) · HOLDOUT +1.92 (N=303, 73.9%) —
  mwelekeo uleule, availability ileile (~0.85 tr/siku), hakuna sura ya overfit-decay.
  NB: BH-FDR ya grid nzima kwenye holdout = 0/1,886 — HAINA maana kwa criterion yetu (hiyo ni
  multiple-testing juu ya cells SEALED; hypothesis yetu ilikuwa MOJA, pre-registered — hii ndiyo
  nguvu halisi ya registration). Cells nyingine zote za holdout zinabaki SEALED milele.
  TAHADHARI hai: (a) edge ni MODEST (+1.9/trade net) na win-margin juu ya breakeven ~6 points —
  win% decay ndiyo hatari #1; monitoring ya forward ni lazima; (b) **INTEGRITY GATE: PASS
  CONFIRMED 2026-07-09 20:26** — Operator ali-re-run --split validation baada ya state rebuild;
  `git diff e1a0d27 -- data/strategies/candidates.jsonl` = TUPU (byte-identical, screenshot
  kwenye chat). Data mpya haikugusa historia. Rekodi ya S3 imefungwa BILA masharti.
  **S4 IMEFUNGULIWA:** (1) IMPLEMENTER-A: STRAT-001 → decision policy rasmi + signal tool ya
  paper-trading; (2) K4: episodes za strategy_lab = training data ya kwanza yenye edge halisi;
  (3) forward paper-trading ya STRAT-001 (tathmini dhidi ya tegemeo la holdout);
  (4) LIVE bado GATED: maamuzi ya PD (live-artifact + max_spread) yanabaki PENDING.

- **2026-07-09 — S3b REGISTRATION (OPTION B approved na PD; imefungwa KABLA ya kufungua holdout).**
  Uchaguzi: kimakanika kutoka B3a ya autopsy (TRAIN+VALID PEKEE — git e613f32 inathibitisha
  holdout haikusomwa na selection): best-p kwa kila pair yenye TRAIN EV>0, +1 diversity ya
  session-filter. **CELLS 5 PEKEE zinafunguliwa kwenye holdout; nyingine zote zinabaki SEALED:**
    SIB-1: nr7_break × USDCHF · SL1.5/TP1.0 · no-LATE · vol ALL   (VALID p=0.0002)
    SIB-2: nr7_break × USDJPY · SL1.0/TP1.0 · no-LATE · vol ALL   (VALID p=0.0007)
    SIB-3: nr7_break × USDCHF · SL2.0/TP1.0 · (LONDON,NY) · ALL   (VALID p=0.0009)
    SIB-4: nr7_break × EURUSD · SL2.0/TP1.5 · no-LATE · vol ALL   (VALID p=0.0026)
    SIB-5: nr7_break × GBPUSD · SL2.0/TP1.0 · no-LATE · vol HIGH  (VALID p=0.0070)
  CRITERION (pre-registered): BH-FDR q=0.10 juu ya p-values 5 za HOLDOUT (m=5) NA EV>0.
  Survivors → STRAT-002.. (PROVEN-OOS). Utaratibu huu ni one-time; hakuna batch ya pili
  kutoka holdout hii. Chanzo cha holdout rows: candidates.jsonl ya commit 86a5977 (tayari
  ina p za kila cell — hakuna run mpya inayohitajika).

- **2026-07-09 — S3b VERDICT: 3/5 PASS (BH-FDR q=0.10, m=5; expected false ~0.3).**
  Holdout (cells 5 zilizosajiliwa PEKEE zilifunguliwa):
    SIB-1 USDCHF 1.5/1.0 no-LATE: N=310, EV +1.41, win 67.7%, p=0.049 → **PASS**
    SIB-2 USDJPY 1.0/1.0 no-LATE: N=327, EV +2.65, win 57.8%, p=0.029 → **PASS**
    SIB-3 USDCHF 2.0/1.0 (LONDON,NY): N=82, EV +3.60, win 75.6%, p=0.036 → **PASS**
    SIB-4 EURUSD 2.0/1.5 no-LATE: EV −0.84 → **FAIL** (pair-level mirage — EURUSD imekufa holdout)
    SIB-5 GBPUSD 2.0/1.0 no-LATE HIGH: EV +2.84 LAKINI p=0.17 (N=103) → FAIL (underpowered tena;
          anabaki candidate wa forward-OOS ya baadaye — HAJAthibitishwa)
  **MAJINA RASMI + PORTFOLIO RULING (Chief):**
    · **STRAT-002 = nr7_break × USDJPY · SL1.0/TP1.0 · no-LATE (PROVEN-OOS)** — slot MPYA ya
      pair huru; pamoja na STRAT-001 → ~1.6 trades/siku jumla.
    · SIB-1 na SIB-3 (USDCHF) = **uthibitisho wa PLATEAU ya params ya STRAT-001** (robustness
      kwa maana ya Davey) — trades zao zina-overlap sana na STRAT-001 (NR7 bar ileile), kwa hiyo
      SIO slots huru za deployment; zinarekodiwa PROVEN-OOS kama correlation-group "USDCHF-nr7";
      deployment ya USDCHF inabaki STRAT-001 pekee (FTMO correlation constraint inaunga mkono).
  Mechanism confirmation: nr7+TP1.0+no-LATE sasa imethibitika kwenye pairs MBILI huru (USDCHF,
  USDJPY) na param-plateau (SL 1.5-2.0) — hii si cell ya bahati, ni FAMILIA halisi.
  Holdout: SEALED tena kabisa — batch hii ilikuwa one-time (ruling 4331e57).

- **2026-07-09 — ALPHA CYCLE-2 OPENED (directive ya PD: "out of the box — trade za aina tofauti,
  uelewa mpana").** Lengo: AI ipate TAXONOMY pana ya aina za trade, kila aina na P(mafanikio|context)
  yake — sio aina moja. **Events MPYA 4 zimejengwa (Chief direct; registry sasa = 20; sweep 16/16):**
  `squeeze_break` (mgandamizo wa MULTI-BAR — BB-width quantile), `nr4_inside` (Crabel ID/NR4,
  mgandamizo maradufu), `gap_fade` (FAMILIA MPYA F8: liquidity-gap reversion — aina tofauti kabisa
  ya trade), `london_drift` (FAMILIA MPYA F9: session-drift/seasonality ya saa).
  **HYPOTHESES ZA CYCLE-2 (familia-level, pre-registered):**
    H-C2-1 Compression kwa KINA: squeeze/nr4/nr7 kwenye **H4** + pairs za spread nyembamba
           (remedy ya COST-KILLED 324 ya autopsy — ATR×2, spread ileile).
    H-C2-2 Shock refinement (mshipa hai #2: pooled +0.34): ASIA + JPY pairs + H4.
    H-C2-3 Gap reversion (aina mpya — reversion ya liquidity, si breakout).
    H-C2-4 Session drift (aina mpya — ratiba, si bei).
    H-C2-5 Currency STRENGTH cross-pair (dimension mpya kabisa — framework ya multi-pair;
           spec kwa IMPLEMENTER-A).
    H-C2-6 EXIT SCIENCE kwa STRAT-001/002 (Davey "7 Sensible Exits": trailing ATR, breakeven,
           time-exit) — kuboresha proven bila entry-risk mpya.
  **OOS RULES za C2 (uadilifu):** S1-C2=TRAIN · S2-C2=VALID 2023-24 (halali kwa familia MPYA —
  hazikuchaguliwa kwayo; m=cells zote za C2) · S3-C2: familia mpya kabisa (gap/drift/strength)
  zaweza one-shot batch kwenye 2025→2026-04 (hazijaguswa nayo); compression/shock-adjacent →
  **2026-05+/forward TU** (Chief aliona holdout top-40 ya grid-1 — knowledge leak inazuiliwa).
  **PAIRS EXPANSION (ombi kwa PD):** angalia chanzo chako kama kina XAUUSD (gold), GBPJPY,
  EURCHF — diversity ya soko kwa AI + compression kwenye gold ni familia classic.

## Top Risks (live)

| # | Risk | Status |
|---|------|--------|
| R-1 | Data ~26GB kwenye PC moja (Japhet) — kila report inaitegemea | **HIGH/HIGH** — mitigation: self-tests bila data |
| P107 | Transitive Market leak | **RESOLVED 2026-07-07** — decision_object core = stdlib+frozen; Track A runtime transitively PURE; `purity_check.py` automates (P104 gap closed); sweep 11/11 |
| A-1 | Reliability saturation Φ(EV/SE) (P70) | OPEN **kwa makusudi** — RED LINE reliability ≠ probability inabaki |
| A-3 | Redundancy (P78) — correlated evidence → reliability optimistic | Imepangwa BAADA ya Execution Science |
| A-2 | Snapshot age-shift semantics vs production event-time | WATCH (E-series) |
| R-2 | Policies ni illustrative (hazijathibitishwa OOS) | Kumbuka: D5 CLOSED = architecture, SIO edge |

## Open Debts / Actions

| Item | Nani | Status |
|------|------|--------|
| AI Strategy discussion | — | **CLOSED (2026-07-04)** — Master Architecture V1; amendments 4 zimeingizwa; Tracks A+B sambamba |
| K1 retroactive backlog (batch 7 → ~42-45) + GRAPH@v8 | RESEARCHER-K | ACTIVE |
| P107 remediation | IMPLEMENTER-A | **CLOSED 2026-07-07** (purity_check; 11/11) |
| F-005 full-metric re-run | Japhet (data run ijayo) | DEBT (V11) |
| Real-data validation | Operator | **DONE 2026-07-07 (PASS)** |
| K4 Datasets (rekodi halisi → training data) au batch 7 | Chief/RESEARCHER-K | NEXT (chaguo la PD) |
| Maamuzi ya Project Director: live-artifact format + max_spread per-pair | Project Director | PENDING (kabla ya live) |

## Governance

```text
Project Director (Japhet)  — vision/data/testing/FINAL project+production decision/Production Owner
Chief Quant (Unified)      — science + doctrine + architecture + knowledge (aliyekuwa #1 + #2);
                             audit functions ndani yake
Implementer                — engines/implementation/reports/experiments/production code
Workflow: Chief (decision+doctrine) → Implementer → Chief (review+compliance) → Project Director
```

*Profitable ≠ Tradable Edge. Protect capital first.*

> **UFAFANUZI RASMI (2026-07-09, swali la PD):** Events 4 za CYCLE-2 = **HYPOTHESES
> AMBAZO HAZIJAPIMWA** (self-test ya code tu — SIO utafiti). Zinasubiri pipeline ileile:
> S1-C2 (TRAIN, PC ya Operator) → S2-C2 (VALID+FDR) → S3-C2 (OOS mpya). HAKUNA pair mpya
> iliyoongezwa — ilikuwa ombi la kuangalia chanzo tu; pair mpya huingia TU baada ya data
> + pipeline kamili. Vyanzo vya hypotheses: (a) lessons/data zetu (compression/shock/COST
> remedy — autopsy), (b) maarifa ya Chief (gap/drift/strength) — VYOTE hupita mlango
> uleule; data ya nyuma ya Operator ndiyo hakimu pekee; hakuna kinacholisha AI (K4)
> bila OOS proof (EP-3). Kifo cha hypothesis pia ni LESSON.

- **2026-07-09 — PAIRS 11 ACTIVE + EXPOSURE DISCLOSURE (uwazi wa Chief).** GBPJPY + EURCHF:
  states zimejengwa (2016→2026-05), integrity PASS (diff ya validation = nyongeza za pairs mpya
  TU; rows zote za zamani byte-identical). XAUUSD: disk ipo, IMEZUIWA na metals guard hadi
  pip support (IMPLEMENTER-A). **DISCLOSURE:** mpangilio wa maelekezo ya Chief ulisababisha
  validation 2023-24 ya nr7×GBPJPY/EURCHF kuonekana KABLA ya registration (exposure isiyosajiliwa;
  kosa la mchakato la Chief — LESSON-015 style). Mitigation: dirisha la 2025-01→2026-04 la pairs
  mpya ni BIKIRA (halijawahi kufunguliwa) → S3c inayopendekezwa: registration ya kimakanika ya
  cells chache za nr7×pairs-mpya (kwa idhini ya PD, "option B" style), one-shot kwenye dirisha
  hilo, exposure ya leo ikitamkwa wazi kwenye registration.

- **2026-07-09 — S3c APPROVED na PD + KANUNI YA UCHAGUZI IMEFUNGWA (kabla ya data kamili).**
  Universe: cells za nr7_break × {GBPJPY, EURCHF} pekee (grid ileile ya C1). KANUNI (mechanical):
  kwa kila pair, cell yenye p bora zaidi ya VALIDATION 2023-24 yenye TRAIN EV>0 (coherence);
  max cells 2 za ziada kama p<0.01 — jumla isiyozidi 4. CRITERION: BH-FDR q=0.10 (m=idadi
  halisi ya walioorodheshwa) NA EV>0, kwenye dirisha BIKIRA la 2025-01→2026-04 la pairs mpya
  PEKEE (cells za pairs za zamani zinabaki SEALED; re-run ya holdout haizifungui — namba zao
  tayari zipo git 86a5977, hakuna exposure mpya). DISCLOSURE inayobebwa: validation ya pairs
  mpya ilionekana kabla ya registration (07c59df) — uchaguzi unabaki mechanical kwa kanuni hii.
  Mchakato: Operator anaendesha TRAIN + VALIDATION za pairs 11 (deterministic; rows za zamani
  byte-identical) → Chief anataja cells kwa kanuni → freeze → one-shot holdout → hukumu.

- **2026-07-09 — S3c REGISTRATION FROZEN (kanuni ya 97b2fdb imetumika kimakanika; determinism
  2004/2004 rows za zamani identical).** Cells 3 PEKEE zitafunguliwa kwenye dirisha bikira
  2025-01→2026-04 la pairs mpya (nyingine zote za holdout zinabaki SEALED):
    SIBC-1: nr7_break × EURCHF · SL1.0/TP2.0 · (LONDON,NY) — VALID p=0.0039 EV+4.55 N=94; TRAIN +1.42 N=456
    SIBC-2: nr7_break × GBPJPY · SL1.0/TP1.5 · (LONDON,NY) — VALID p=0.0204 EV+7.52 N=176; TRAIN +7.37 N=643
    SIBC-3: nr7_break × EURCHF · SL1.0/TP1.0 · (LONDON,NY) — VALID p=0.0061 EV+2.68 win 70.8% N=96; TRAIN +2.18 N=466
  CRITERION: BH-FDR q=0.10 (m=3) NA EV>0 kwenye holdout ya pairs mpya. One-time batch.

- **2026-07-09 — S3c VERDICT: 0/3 PASS (BH-FDR q=0.10, m=3) — HAKUNA STRAT-003 leo.**
  Dirisha bikira 2025-01→2026-04 la pairs mpya: SIBC-1 EURCHF 1.0/2.0: EV +1.76 p=0.156 ·
  SIBC-2 GBPJPY 1.0/1.5: EV +0.33 p=0.462 · SIBC-3 EURCHF 1.0/1.0: EV +1.21 (win 64.3%) p=0.131.
  ZOTE chanya (mwelekeo wa familia unaendelea) lakini HAKUNA aliyefikia significance — criterion
  pre-registered inasema FAIL, na tunaheshimu. USOMAJI wa Chief: (1) shrinkage kubwa ya GBPJPY
  (VALID +7.5 → holdout +0.33) inathibitisha KWA NINI dirisha bikira lilihitajika — namba za
  validation zilizoonekana kabla ya registration zilikuwa zime-overstate; nidhamu imeokoa
  portfolio kutoka kwenye deployment ya uongo. (2) EURCHF cells mbili (p≈0.13-0.16, EV +1.2..+1.8,
  maxDD ndogo) = FORWARD-WATCH (kama GBPUSD SIB-5): hazipandi kuwa strategies, zinafuatiliwa
  kwa forward/paper bila deployment. (3) Portfolio rasmi inabaki: STRAT-001 + STRAT-002.
  LESSON-material (RESEARCHER-K, L-d): "exposure-tainted selection hushuka OOS; dirisha bikira
  ndilo hakimu" — mfumo ulikataa kujidanganya. Batch S3c CLOSED; holdout SEALED tena kote.

- **2026-07-10 — S1-C2 KAMILI (pairs 11) + REVIEW ya Chief + S2-C2 REGISTRATION FROZEN.**
  H1 (events 4 mpya): DHAIFU kwa ujumla (EV>0 = 82/1032, 8%): gap_fade KARIBU-KUFA (1/240,
  mean −4.55) · squeeze_break H1 −2.35 · london_drift hasi ila POCKET ya USDJPY (+1.89, N=1,654!)
  · nr4_inside H1 pockets za JPY (+2.2..+2.3, N>1,000). H4 (cost-remedy H-C2-1/2): **NYOTA —
  nr7 237/264 chanya, mean +4.59** (H1 ilikuwa +0.76 — hypothesis ya gharama IMETHIBITIKA
  in-sample); nr4_inside 159/264 (+1.02); top: nr4×GBPJPY 2.0/3.0 no-LATE **+18.3 (N=351)**,
  nr7×GBPUSD/GBPJPY +12..+14. shock H4 flat; squeeze H4 hasi. **STRENGTH (usd_drift): DEAD
  in-sample (pairs 7 zote hasi, N~1,700) → ARCHIVED + LESSON (H-C2-5 imekufa geti la kwanza).**
  GOLD: states zipo lakini config haikuwa nayo → runs hazina XAUUSD; Chief ame-commit config
  (pairs 12 rasmi — kuondoa human error ya mara 3). **S2-C2 REGISTRATION FROZEN:** grid_c2
  code ILEILE, pairs 12, TRAIN re-run (H1+H4, kwa gold) KISHA validation (H1+H4); criterion:
  BH-FDR q=0.10 kwa kila run (m=cells tested) NA EV>0; hakuna mabadiliko ya code/grid kati
  ya sasa na hukumu; survivors → mchakato wa S3-C2 (dirisha la OOS litapangwa kwa kanuni za
  uadilifu zilizopo: compression/shock → 2026-05+/forward; wengine wanaweza 2025+ bikira).

- **2026-07-10 — S2-C2 VERDICT: H1 = 0/1,068 (events mpya za H1 zimekufa FDR — kifo cha heshima,
  LESSONS) · H4 = SURVIVORS 30/1,152 (kwa bahati ~3 → ~27 halisi).** Muundo wa survivors:
  makundi 8 ya (event×pair), YOTE compression/shock kwenye H4, karibu yote no-LATE, na **TRAIN
  coherence 30/30 (kila survivor ana TRAIN EV>0)**:
    nr7×EURGBP (plateau 8): TRAIN +3.5..+4.6 → VALID +5.1..+5.8, win 75-82% (uthabiti safi)
    nr4×GBPJPY (plateau 7): TRAIN +8..+11 → VALID +41..+49 (VALID moto — shrinkage inatarajiwa)
    nr7×XAUUSD (4): TRAIN +8..+51 → VALID +319..+325 (GOLD mara ya kwanza — bull ya 2023-24;
      shrinkage inatarajiwa) · shock×XAUUSD (2): VALID +949, TRAIN +155
    nr7×AUDUSD (4), nr7×EURJPY (2), nr7×USDJPY (2), nr7×GBPJPY (1)
  TAHADHARI: VALID>>TRAIN kwa GBPJPY/gold = sehemu ni regime ya 2023-24; S3-C2 ndiyo hukumu.
  **UAMUZI WA PD UNAOSUBIRIWA (S3-C2 window):** kanuni frozen (0e45f73) inasema compression/
  shock → 2026-05+/forward TU (knowledge-leak guard ya Chief). HOJA ya amendment: uchaguzi wa
  S2-C2 ulikuwa MECHANICAL (BH-FDR, si hiari ya Chief) → leak haikuweza kuelekeza uchaguzi;
  dirisha la H4 2025-01→2026-04 ni BIKIRA (halijawahi kuhesabiwa na yeyote); kwa ~0.2-0.35
  tr/day, miezi 16 inatoa N≈100-170 kwa kila cell (inatosha). OPTION A = heshimu kanuni kama
  ilivyo (subiri data 2026-05+ + forward — miezi kadhaa). OPTION B (pendekezo la Chief) =
  amendment yenye disclosure: one-shot ya survivors 30 pre-registered kwenye dirisha bikira
  la H4 2025-01→2026-04, BH-FDR q=0.10 m=30 NA EV>0.

- **2026-07-12 — DATA SCIENCE REVIEW (SCIENTIST-D) IMEPOKELEWA + CHIEF RESPONSE: ACCEPTED.**
  Ripoti: reports/data_science_review.md + scripts/scientist_d_recompute.py (kila namba
  inazalishwa kutoka artifacts; hakuna dirisha lililoguswa). **Chief verification:** BH verdicts
  zote zinarudi ✓; finding kuu (W1: z-test anti-conservative ×1.22-1.41 kwa high-win/small-TP)
  Chief aliipima kwa MC huru — check ya kwanza ya Chief (idealized 1:2) ilikosea; ujenzi wa
  SCIENTIST-D (payoffs za net-ya-costs) ulithibitika HASA (0.0609) — reviewer alishinda; hii
  yenyewe ni funzo la utamaduni wa verification. FINDINGS ZILIZOKUBALIWA (zote 8 W1-W8 + C7 1-4):
  skew-bias ya p-engine (STRAT-001 p 0.021→0.027 bado PASS; SIB-1 0.049→0.058 = knife-edge —
  rekodi imewekewa alama; deployment HAIATHIRIKI kwa kuwa SIB si slots); shrinkage slope 0.346
  (VALID→HOLDOUT −60..−75% kwa significant cells); window 2023-24 imechimbwa ×4 (cells 4,519);
  costs = 36% ya gross ya STRAT-001; misnomer ya "walk-forward"; m-ya-cells inapoteza power
  (combos 110 halisi vs cells 1,939); MDE haikuwepo (S3c ilitabirika ex-ante); hakuna portfolio
  layer. **ACTION PLAN (Chief):** WAVE-1 (IMPLEMENTER-A, kabla ya S3-C2): R1 bootstrap p-engine
  (stationary block, studentized; self-tests dhidi ya jedwali la W1) + sensitivity restatement ya
  S3/S3b · R4 portfolio v0 (overlap/corr/joint-DD ya STRAT-001+002; rule: corr>0.4 → nusu size)
  · R5 cost stress (EV(Δspread) kwenye kila ripoti; WIDE-state split; GOLD spread model kwa
  spread_quality.py — gold registration BLOCKED hadi hii) · R6 win-rate CUSUM pre-registered
  (STRAT-001: review<70%/halt<66% @60-trade rolling; STRAT-002 thresholds kwa hesabu ileile).
  WAVE-2: R3 rolling-origin yearly folds (regime robustness) · R8 tick-compression features (C3).
  DOCTRINE AMENDMENTS: EP-8 (MDE rule — hakuna registration ya cell ambayo shrunken-EV < MDE) +
  EP-9 (multiplicity = correlation-aware, "m inahesabu SELECTION yote", si cell-count tu) +
  rename "walk-forward"→"static validation" hadi R3 + hukumu za holdout zirekodiwe na interval,
  si binary tu, na deployment iwe na forward-tranche gate. **S3-C2 = OPTION B-PRIME (design ya
  R2, iliyoungwa mkono na reviewer huru): m=8 (wawakilishi wa makundi, kanuni mechanical),
  q=0.05, bootstrap engine (R1 KWANZA), EV>0, MDE screen + shrunken forecasts, survivors =
  PROVEN-OOS-PROVISIONAL (capital baada ya forward tranche); makundi ya GOLD yanasubiri R5.**
  Inasubiri: approval ya PD ya B-prime.

- **2026-07-12 — B-PRIME APPROVED na PD.** Mpangilio uliofungwa (sequencing): (1) WAVE-1 ya
  IMPLEMENTER-A — R1 bootstrap engine NDIYO gate (S3-C2 haitumii z-test tena); (2) SCIENTIST-D
  referee wa R1; (3) S3-C2 registration: p za bootstrap kwa survivors 30 wa VALID (cells
  zilizokwisha-funguliwa — halali), wawakilishi 8 kwa kanuni mechanical (best bootstrap-p per
  group, TRAIN EV>0), MDE screen + shrunken forecast (×0.35-0.5), makundi ya GOLD deferred hadi
  gold cost model (R5); (4) one-shot dirisha bikira H4 2025-01→2026-04, BH q=0.05 m=(waliobaki
  baada ya MDE screen), EV>0; (5) survivors = PROVEN-OOS-PROVISIONAL → forward tranche kabla ya
  paper-portfolio kamili. R4/R5/R6 zinaenda sambamba na hilo.

- **2026-07-12 — WAVE-1 DELIVERED (IMPLEMENTER-A) + CHIEF REVIEW: OK; referee = SCIENTIST-D.**
  R1 pvalue_boot (stationary bootstrap + Newey-West, percentile-t, seed=cell; ENGINE SWAP
  pre-registered kwa commit KABLA ya dirisha jipya; p_z inabaki sensitivity column) — na
  DEVIATIONS 2 kwa ushahidi (mb=3 sio 10: mb10 ilishindwa acceptance ya design; +NW kwa AR
  clustering 0.058 vs z 0.121). CHIEF SPOT-CHECK HURU: size 0.053 kwenye cost-adjusted skew
  null (z=0.061) — inapima kwa haki. R4 portfolio_v0 (rule corr>0.4→halve, pre-registered) ·
  R5 cost_stress (EV(Δspread) kila report; WIDE-split → deployment-policy tu; gold p95/2
  slippage inasubiri approval) · R6 winrate_monitor (thresholds PRE-REGISTERED: STRAT-001
  70/66 @60; STRAT-002 54.0/50.0). Sweep 21/21; episodes()/artifacts hazikuguswa. INAYOFUATA:
  SCIENTIST-D referee ya R1 (deviations = hukumu yake) → S3-C2 registration.

- **2026-07-12 — REFEREE (SCIENTIST-D): R1 APPROVED.** Deviations 2 (mb=3 + Newey-West)
  zimekubaliwa kwa MC huru ya referee (implementations zake mwenyewe; pvalue_boot ya
  IMPLEMENTER-A haikuguswa): skew nulls z=0.062/0.071 inarudi HASA, boot=0.050 nominal;
  verbatim design yake ya awali (mb10) inashindwa test yake mwenyewe (0.0697) — "implementer
  sahihi". Isolation imeonyeshwa: blocks ndogo=skew fix, NW=dependence fix (AR0.5: 0.098→0.068).
  R6 posterior-SE note CONFIRMED. Conditions 3 non-blocking: B=50k kwa registered cells kwenye
  hukumu za mwisho; restatement isiclobber artifacts za awali + m-sensitivity note; lag-1
  autocorr iwe observable. **S3-C2 REGISTRATION: UNLOCKED.** Hatua: (1) Operator: re-run
  S2-C2 H4 validation kwa engine mpya (restatement rasmi — survivors watapangwa upya kwa
  p_boot; inaweza kutofautiana na 30 wa z-test); (2) Chief: groups → reps mechanical (best
  p_boot per group, TRAIN EV>0) + MDE screen (shrunken ×0.35-0.5) + GOLD DEFERRED (cost model
  ya R5 inasubiri spread run ya Operator) → FREEZE; (3) one-shot q=0.05.

- **2026-07-12 — S3-C2 RULING (mechanical, kwa kanuni za B-prime): REGISTRATION HAIFANYIKI —
  dirisha bikira la H4 LIMEHIFADHIWA.** Restatement (p_boot rasmi): survivors 30→**12** (18 wa
  z-test walikuwa artifact ya skew — utabiri wa W1 umetimia kwenye data yetu wenyewe). **GOLD
  IMETOWEKA KABISA:** makundi ya XAUUSD (nr7 +319, shock +949) HAYAKUSALIA p_boot — namba za
  kuvutia zaidi za C2 zilikuwa artifact ya skew + regime ya 2023-24 (LESSON kubwa). Makundi 4
  yaliyobaki (nr4×GBPJPY 5 cells, nr7×EURGBP 4, nr7×EURJPY 2, nr7×AUDUSD 1; wote TRAIN EV>0).
  **MDE SCREEN (sd kutoka payoff structure; N_exp kutoka trades/day × 347):** kwa shrink 0.35
  (ncha conservative ya rule ya B-prime) — **4/4 FAIL** (GBPJPY 15.2<16.8 · EURGBP 1.8<2.4 ·
  EURJPY 9.6<17.7 · AUDUSD 5.0<9.1). Kwa 0.5, wawili wangepita — LAKINI kuchagua 0.5 BAADA ya
  kuona kwamba inawapitisha = post-hoc selection (dhambi ileile tunayoikataza); range 0.35-0.5
  iliachwa wazi kwenye registration — azimio la uaminifu: ncha conservative INAFUNGA. **HUKUMU:
  hakuna one-shot leo; dirisha bikira linabaki BIKIRA; makundi 4 = C2-WATCH.** Njia mbili mbele:
  (a) forward window inakua (data 2026-05+ kila mwezi) hadi N itoshe; (b) SCIENTIST-D apewe
  design ya FAMILY-POOLED test (ATR/R-normalized across pairs — N_exp pooled ~341 inatosha) —
  registration mpya + referee KABLA ya dirisha lolote. Uzito wa siku: mfumo ULIKATAA kujidanganya
  mara ya pili leo — kwanza kwa engine, sasa kwa power arithmetic. Portfolio inabaki
  STRAT-001/002; R3 (rolling folds) inapanda kipaumbele.

- **2026-07-12 — FAMILY-POOLED DESIGN (SCIENTIST-D): APPROVED (Chief verification huru inarudi
  hasa).** reports/family_pooled_design.md — mtihani MMOJA (m=1) kwenye dirisha bikira H4:
  "compression-H4 family (reps 4 mechanical: nr4×GBPJPY 1.5/1.5, nr7×EURGBP 1.5/1.0, nr7×EURJPY
  1.0/3.0, nr7×AUDUSD 1.5/3.0; wote no-LATE) ikitradiwa kama STREAM MOJA ya R-units ina EV>0
  net ya costs". Ubunifu wa msingi: **pooling inageuza tests 4 zilizoshindwa MDE (N~60-121)
  kuwa MOJA yenye power (N=341)** — MDE 0.119 R vs shrunken 0.140 (×0.35 conservative tip) =
  PASS ×1.18, power 0.62. R-normalization (pips hazi-pool across pairs), GOLD imetengwa (skew
  artifact), criterion pre-registered (pvalue_boot B=50k <0.05 NA EV_R>0), dry-run ya VALIDATION
   inahesabu screen HASA kabla ya freeze (fail→stop→LESSON), caveats 4 za uaminifu (confirmation
  si discovery; correlated na STRAT-001/002 era; power 0.62 = FAIL 38% hata kama forecast sahihi
  — hakuna kuita "underpowered" baadaye). PASS = "compression-H4 family PROVEN-OOS-PROVISIONAL"
  → forward paper ya reps 4 kama stream + kipaumbele R3/R8; HAITENGENEZI STRAT-00x, HAITOI
  capital, per-pair inahitaji forward tranche yake. Chief verification: N=341/EV_R=0.401/MDE=0.119
  zinarudi hasa (huru). SEQUENCE (§8): IMPLEMENTER-A ajenge family_pooled.py + AT1-AT8 →
  SCIENTIST-D referee (MC ya AT4) → dry-run VALIDATION → screen 0.35 → Chief freeze → one-shot.

- **2026-07-13 — FAMILY-POOLED BUILD (IMPLEMENTER-A): APPROVED.** family_pooled.py (runner +
  AT1-AT8; REUSE-only, load_window +ts additive; sweep 22/22). OQ#1 (AT1 fixed-slip residual
  SLIP·(1−1/scale)/R) = Chief ruling NON-BLOCKER (hakuna rescaling production; wording fix;
  SCIENTIST-D athibitishe). AT4 = scaled-sanity 0.066 → full MC = kazi ya referee. SEQUENCE:
  SCIENTIST-D referee (full AT4 + OQ#1 + verbatim) → Operator dry-run VALIDATION → screen 0.35
  (fail→stop→LESSON) → Chief freeze → one-shot. Portfolio inabaki STRAT-001/002.

- **2026-07-13 — FAMILY-POOLED REFEREE (SCIENTIST-D): APPROVED WITH FIXES (F1/F2); AT4 full MC
  PASS (bands 6/6).** Verbatim-vs-implemented PASS §1-§8; golden hashes re-verified huru; OQ#1
  ACCEPTED (implementer sahihi — design wording imerekebishwa; slippage IBAKI pips-constant,
  residual 0.003-0.013 R immaterial). **AT4 full MC (B-ladder ya busara badala ya 13h compute):
  size 0.040-0.051 kwenye iid nulls mbili, AR(0.5) 0.064 vs z-test 0.124 — engine inashikilia.**
  UAMINIFU wa referee: kwenye iid mixture z-test PIA ~nominal (skews za reps 4 zinaghairiana) →
  bootstrap hapa ni BIMA dhidi ya DEPENDENCE, si kurekebisha bias kubwa ya iid; criterion
  inabaki kama design. **FIXES 2 za lazima kabla ya freeze (protection logic, SI statistic):**
  F1 = MDE screen inatumia N ya split (dry-run VALID N~531) badala ya N_exp(holdout)=341 →
  understates MDE ×1.25 = anti-conservative (mtego ULE ULE ruling ya 07-12 ilikataa!); lazima
  itumie N_exp=Σ(n_i/days_i)×347. F2 = run_family i-abort kama pair inakosekana (vinginevyo
  one-shot ingechoma dirisha kwa mtihani WA TOFAUTI na registered). N1 = print per-rep EV_R
  (non-blocking). SEQUENCE: IMPLEMENTER-A F1+F2 (~30min) → SCIENTIST-D spot-check (diff-level,
  hakuna MC mpya) → Operator dry-run VALID → screen 0.35 kwa N_exp → Chief freeze → one-shot.

- **2026-07-13 — F1/F2 FIXED (IMPLEMENTER-A) + CHIEF SPOT-CHECK: PASS.** F1: registration
  screen sasa inatumia N_exp (self-test: N_exp=634 ≠ pooled N=457; MDE=1.645·sd/√N_exp; split-N
  = descriptive). F2: missing-pair → RuntimeError (drop GBPJPY → raise, si silent). Sweep 22/22.
  CHIEF diff verification: F1/F2 zinagusa screen-call + abort TU — ZERO statistic functions
  zimebadilika (pvalue_boot/pool/R-norm intact) → spot-check ya referee (diff-level, statistic
  untouched) imetimia; hakuna MC mpya inahitajika. **GATE INAYOFUATA: AT8 dry-run VALIDATION**
  (Operator, data halisi) → exact EV_R/sd_R → screen shrink 0.35 kwa N_exp=341. PASS → Chief
  freeze registration → one-shot. FAIL → stop, document becomes LESSON (S3c-style, dirisha bikira
  halijaguswa).
