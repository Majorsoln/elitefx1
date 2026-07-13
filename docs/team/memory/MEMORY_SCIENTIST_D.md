# MEMORY — SCIENTIST-D (Institutional Quantitative Data Scientist)

IDENTITY: Mwanachama mpya wa timu (aliyeteuliwa na Project Director, 2026-07-10). Wewe ni
**external reviewer wa daraja la taasisi (institute-grade)** — data scientist mwenye utaalamu wa
kina wa features, statistics za kisasa za utafiti wa masoko, na ML. Kazi yako SI kutekeleza
mfumo — ni **kuuchambua, kuukosoa, na kuuboresha kwa utaalamu huru**.

## UHURU WAKO (directive ya PD — soma vizuri)
- **HUFUNGWI na doctrine za mradi kwenye UCHAMBUZI na RIPOTI zako.** Unaruhusiwa — na
  unatarajiwa — ku-challenge kila kitu: methodology ya Chief, Entry Doctrine, FDR approach,
  splits, chochote. Think out of the box. Usimpendeze mtu yeyote; andika kama reviewer wa nje
  anayelipwa kusema ukweli.
- Mipaka 4 TU (ya uadilifu wa data, si ya doctrine):
  1. HAKUNA kuendesha selection/majaribio MAPYA juu ya madirisha ya holdout/bikira — unaweza
     KUSOMA matokeo yaliyokwisha-funguliwa (yote yako git).
  2. Huchezei/hubadilishi artifacts za git za matokeo.
  3. Kila claim ya namba kwenye ripoti yako ina chanzo (file/commit).
  4. Mapendekezo yako = DESIGNS za majaribio; utekelezaji unapita kwa Chief/PD (registration).

## MFUMO WETU WA KUPATA STRATEGIES (jinsi tunavyofanya — usome kisha uhukumu)
1. **Data:** ticks bid/ask 2016-01→2026-05, pairs 12 (majors 9 + GBPJPY, EURCHF, XAUUSD), PC ya
   Operator (~26GB+). `market_state_engine.py` inajenga bars H1/H2/H4/D1 + states (volatility/
   activity/spread — rolling terciles, DESEASONALIZED kwa saa, no-lookahead) →
   `data/processed/state/`.
2. **Entries:** `src/research/event_library_v2.py` — EVENTS_V2: entries 20 katika familia 9
   (compression: nr7/nr4/inside/squeeze; trend-pullback; breakout-stop; session; shock;
   mean-reversion; price-action; gap-reversion; session-drift). Zote edge-triggered (+rearm),
   market au stop semantics, no-lookahead (self-tested kwa truncation invariance).
3. **Harness:** `event_quality_report.episodes()` — position 1 kwa cell (non-overlap), entry
   "next bar" honest (market=open; stop=touch, gap-honest), SL/TP za ATR(14) (+ exit variants:
   trailing/breakeven/time), tie-bar→SL (worst case), costs = spread halisi ya bar ya entry +
   slippage (0.1 mkt / 0.3 stop). Context filters (session/vol-state) zinawekwa KWENYE signals
   kabla ya simulation (decidability: vol ya bar ya SIGNAL, session ya bar ya ENTRY).
4. **Factory:** `strategy_lab.py` — GRID (cells 1,000-2,400 kwa mzunguko: event × pair × SL/TP
   {1,1.5,2}×{1,1.5,2,3} × session/vol filters) → TRAIN 2016-22 (search) → VALIDATION 2023-24 +
   **BH-FDR q=0.10 (m=cells tested)** → HOLDOUT 2025-01→2026-04 (one-shot, Chief token, cells
   pre-registered PEKEE). Pre-registration discipline kali (registration inafungwa kwa commit
   KABLA ya kufungua dirisha). p-value: one-sided normal approx (mean/SE). `strength_lab.py` =
   cross-pair USD index framework. `failure_autopsy.py` = taxonomy ya vizuizi.

## MATOKEO YOTE HADI SASA (PASS na FAIL — usome raw data mwenyewe pia)
**PROVEN-OOS (strategies rasmi 2):**
- STRAT-001: nr7×USDCHF H1, SL2/TP1, no-LATE — TRAIN +0.36 (N=1607) / VALID +3.07 p=9e-6
  (pekee 1/1,939 FDR) / HOLDOUT +1.92, win 73.9%, N=303, p=0.021.
- STRAT-002: nr7×USDJPY H1, SL1/TP1, no-LATE — HOLDOUT +2.65, win 57.8%, N=327, p=0.029
  (S3b: 3/5 registered siblings walipita; wawili = plateau ya STRAT-001 kwenye USDCHF).
**FAILED kwenye madirisha bikira (funzo kubwa):**
- S3b: nr7×EURUSD −0.84 (pair-mirage); nr7×GBPUSD +2.84 lakini p=0.17 (underpowered).
- S3c: nr7×{GBPJPY,EURCHF} cells 3 — ZOTE EV>0 lakini 0/3 significance; GBPJPY VALID +7.52 →
  bikira +0.33 (shrinkage ya exposure-tainted selection — LESSON L-d).
**AUTOPSY ya C1 (cells 2,004):** SURVIVOR 1 · B3a FDR-TAX 87 (86 nr7 — "waliouawa na multiplicity")
· B3b UNDERPOWERED 429 · B2 MIRAGE 370 · B4 DEAD 1,052 (jump_off 54/54, breakout_stop 52/54,
trend-family >92% dead kwenye H1 majors) · B5 STARVED 65 · COST-KILLED 324 (nr7 192).
**CYCLE-2:** H1 events mpya (gap_fade, london_drift, squeeze, nr4-H1): S2 = **0/1,068** (dead).
H4 (compression+shock): S2 = **SURVIVORS 30/1,152** (~3 kwa bahati) katika makundi 8, TRAIN
coherence 30/30: nr7×EURGBP (plateau 8; +5..+6, win 75-82%), nr4×GBPJPY (7; VALID +41..+49 vs
TRAIN +8..+11 — regime?), nr7×XAUUSD (4; VALID +319 vs TRAIN +8..+51 — gold bull 2023-24?),
nr7×AUDUSD (4), shock×XAUUSD (2; +949!), nr7×EURJPY/USDJPY/GBPJPY. S3-C2 inasubiri uamuzi wa PD.
**STRENGTH (usd_drift):** DEAD in-sample — pairs 7/7 hasi (N~1,700 kila moja). Archived.

## ACCESS — SOMA HIZI MWENYEWE (raw, si muhtasari wangu)
- Ripoti: `reports/strategy_lab_report*.md`, `failure_autopsy_report.md`, `event_quality_report.md`,
  `strength_lab_report.md`, `market_state_report.md`, `docs/CHIEF_STATUS.md` (Validation Log nzima).
- Raw candidates (git history): C1 TRAIN `ccfbb24` · C1 VALID+p `e1a0d27` · C1 HOLDOUT `86a5977`
  · pairs-11 TRAIN/VALID `b1fdc85`/`686744f` · C2 TRAIN p12 `4bbb70b`(H1)/`ffb212e`(H4) ·
  C2 VALID `96793e7`(H1)/`d3c03a6`(H4). Soma kwa: `git show <commit>:data/strategies/<file>.jsonl`
- Code: `src/research/{event_library_v2,event_quality_report,strategy_lab,failure_autopsy,strength_lab}.py`
- Lessons: `docs/lessons/` (36+) — hasa LESSON-001/002/029/033/034 + L-a..L-d za S-series.

## UDHAIFU AMBAO CHIEF MWENYEWE ANAUSHUKU (starting points — USIISHIE HAPA; tafuta zaidi)
1. Validation = dirisha MOJA (2023-24) — sio rolling walk-forward; regime-dependence haipimwi.
2. p-values = normal approx juu ya PnL za fat-tails/skew (hasa high-win/small-TP structures).
3. Independence assumption ya trades — serial/regime correlation haijashughulikiwa (block methods?).
4. BH juu ya cells zilizo-correlated sana (param plateaus) — m inavimba, power inapotea.
5. Costs = median spread + slip constant — hakuna slippage model ya volatility/news.
6. Hakuna portfolio-level analysis: correlation kati ya strategies, DD ya pamoja, sizing.
7. High-win/small-TP = fragile kwa win% decay na spread widening (STRAT-001 breakeven ~68%).
8. Non-stationarity (F-029) haitumiki kama FEATURE — hakuna regime-conditional deployment.
9. Feature space finyu: OHLC/ATR/session/vol-state tu — tick density, volume bars (code zipo
   src/data!), microstructure, cross-pair — hazitumiki.
10. Cumulative multiplicity across cycles juu ya validation ileile (garden of forking paths).

## LAST COMPLETED (2026-07-12): reports/data_science_review.md (review ya kwanza)
Deliverables: `reports/data_science_review.md` (English, institutional) +
`scripts/scientist_d_recompute.py` (inazalisha KILA namba ya ripoti kutoka git artifacts —
hakuna dirisha lililoguswa). Verdicts ZOTE za BH-FDR zilithibitika kwa recomputation huru
(C1 1/1939 · p11 1/2299 · C2H1 0/1068 · C2H4 30/1152 · S3b 3/5).

### FINDINGS KUU (na namba)
1. **P-VALUE ENGINE INA BIAS YA KIMUUNDO** (finding kubwa zaidi): normal-approx z-test ni
   anti-conservative kwa negative-skew (high-win/small-TP): true size @0.05 = 6.1-7.0%
   (×1.22-1.41) kwa SL2/TP1; conservative (×0.76) kwa TP3. Ushahidi kwenye artifacts: TP1.0
   = 49% ya significant cells vs 24% ya grid; TP3 = 6% vs 26%. Mfumo unachagua structure
   FRAGILE kwa sehemu kwa sababu ya artifact ya takwimu. Skew-corrected: STRAT-001 p
   0.021→0.027 (bado PASS); SIB-1 0.049→0.058 (si significant nominal!); S3b verdict k=3
   inasimama kwa margin ya 0.002 tu kwenye BH space. → R1: block bootstrap engine.
2. **SHRINKAGE imepimwa**: C1 VALID→HOLDOUT (1,870 cells joined): bucket p<0.01 EV +3.57→+1.42
   (−60%); p 0.01-0.05 −75%; OLS slope 0.346. C2-H4 survivors median VALID/TRAIN = 2.1×
   (XAU hadi 41×) = regime ya 2023-24. Tegemeo la S3-C2: survivor EV itapungua nusu-⅔.
3. **WINDOW 2023-24 imechimbwa mara 4**: cells 4,519 distinct na p-values (1939+360+1068+1152),
   FDR per-run kamwe si global; C2 hypothesis-formation ilijua matokeo ya holdout ya nr7 →
   "dirisha bikira" la H4 2025-26 ni CONFIRMATION ya familia inayojulikana, si discovery.
4. **UCHUMI MWEMBAMBA**: STRAT-001 costs = 36% ya gross; +0.5 pip widening = −26% ya net edge;
   win-margin 2.2 SE. STRAT-002: 16%/19%/2.0 SE. Hakuna spread stress, hakuna control chart.
5. **Correlation structure**: C1 = 1,939 cells / 110 combos (~17.6 cells/combo → effective m
   ndogo sana; B3a "FDR-TAX 87" = artifact ya m iliyovimba); C2 survivors 30 = groups 8.
6. **Power**: S3c ilihitaji N 2.2-2.6×; SIB-5 3.0× — foreseeable ex-ante; MDE rule inahitajika.

### MAPENDEKEZO RANKED (R1-R8 kwenye ripoti; designs runnable ndani)
R1 bootstrap p-engine + re-state S3/S3b (HIGH/LOW) · R2 S3-C2 family-level m=8, q=0.05 kwa
tainted families, bootstrap p, forward deployment gate, shrunken-EV≥MDE (HIGH/LOW — ndiyo
pendekezo langu kwa uamuzi wa PD unaosubiri: Option B yenye masharti) · R3 rolling-origin
yearly folds 2016-24 kwa families (HIGH/MED) · R4 portfolio v0: overlap/corr/joint-DD ya
STRAT-001+002 (HIGH/LOW) · R5 cost stress + WIDE-state + gold cost model (MED/LOW) ·
R6 win-rate CUSUM control chart pre-registered (MED/LOW) · R7 MDE registration rule (MED/TRIV) ·
R8 tick-density compression features = minimal meta-labeling + K4 (MED/MED-HIGH).
Methods triage: Romano-Wolf/SPA + stationary bootstrap = YES kuu; PSR/DSR partial (idea si
formalism); CPCV overkill (rolling-origin inatosha); meta-labeling minimal-form baadaye;
HRP/deep/genetic = NO kwa sasa. Doctrine challenges 4: "walk-forward" jina si sahihi; "m=cells"
si honesty ni power leak; one-shot holdout = regime draw moja (dai interval estimates + forward
tranche); q=0.10 per-run kwenye window iliyotumika si guarantee mpya.

### OPEN QUESTIONS (za mzunguko ujao)
- Je, S3b ingesimama chini ya exact bootstrap p (pnls halisi, si two-point approx)? (R1 itajibu
  — cells zimeshafunguliwa, ni halali.) Two-point null yangu inapuuza timeout exits (inaelekea
  ku-overstate correction kidogo).
- Trade-time overlap ya STRAT-001 vs 002 (R4) — hakuna mtu anayejua leo.
- XAUUSD cost model (spread halisi ya ticks) kabla ya registration yoyote ya gold.
- DST jitter ya session boundaries (±1h) — robustness check ndogo.
- Kama S3-C2 itaendeshwa kwa m=30 cell-level badala ya m=8 family-level: plateau double-count.

## CHIEF RESPONSE (2026-07-12): REVIEW ACCEPTED — findings zote 8 + doctrine challenges 4
Chief ali-verify W1 kwa MC huru: check yake ya kwanza (idealized 1:2) ilitofautiana; ujenzi wako
(cost-adjusted payoffs) ulithibitika HASA (0.0609). Action plan: WAVE-1 = R1/R4/R5/R6
(IMPLEMENTER-A, designs zako verbatim), WAVE-2 = R3/R8; doctrine: EP-8 (MDE), EP-9
(correlation-aware multiplicity), rename walk-forward, interval verdicts + forward gates;
S3-C2 = B-prime (R2 yako). KAZI YAKO IJAYO: (1) referee wa R1 ikija (verify bootstrap engine
dhidi ya jedwali lako); (2) baada ya R3: andika regime-conditional deployment proposal.

## COMPLETED (2026-07-12): REFEREE ya WAVE-1 R1 — VERDICT: **APPROVED**, deviations 2 ACCEPTED
Deliverables: `reports/wave1_referee_report.md` + `scripts/scientist_d_referee_r1.py` (MC huru:
nulls ZANGU + variant implementations zangu, ikiita pvalue_boot yao bila kubadilisha; hakuna
dirisha la data). Matokeo muhimu (yote kwenye script, seeds fixed):
- **Acceptance zote PASS kwa engine rasmi (mb3+NW):** sym i.i.d. boot 0.0533 ≈ z 0.0537,
  |diff| 0.021; skew nulls za §A3-W1: z 0.0620/0.0710 (jedwali langu linarudi HASA), boot
  **0.0500/0.0497** (nominal); pos-skew N=70: z 0.0397→boot 0.0487 (inarekebisha pande zote
  mbili); determinism bit-identical ✅.
- **Deviation (i) mb=3 (sio ~10): NILIKUBALI — implementer yuko sahihi.** Verbatim design YANGU
  (mb10+iid-sd) inashindwa acceptance test yangu mwenyewe: size 0.0697 @N=100 (claim yao 0.072
  imethibitika); hata mb10+NW 0.0660 ✗. "~10" yangu ilikuwa intuition ya N≳300; b~n^(1/3) → 3-5
  kwa N=100-300. Mechanism story yao ("block-averaging inameza skew") si sahihi kikamilifu
  kinadharia (mean* isiyo-studentized inabaki na skew ~γ/√n) — lakini effect kwenye studentized
  t* ni halisi na ya maamuzi (~10 resampling units tu @N=100).
- **Deviation (ii) NW studentization: NILIKUBALI.** Isolation: blocks ndogo → skew fix
  (mb3+iid 0.0517 kwenye skew); NW → dependence fix (AR0.5: mb3+iid 0.0977 → mb3+NW 0.0680).
  Residual documented: 0.068 @ρ=0.5, 0.095 @ρ=0.7 (vs z 0.17/0.25) — si defect, ni property;
  §4.3 inaifanya observable. Power price: 0.670 vs z 0.723 @N=303 (STRAT-001 alternative) —
  ~5pp, bei ya haki ya kuondoa size bias ×1.2-1.4.
- **R6 posterior-SE note: CONFIRMED na ZAIDI ya walivyodai** — flat SE@60 ingevunja STRAT-001
  PIA (line 74.31% > holdout 73.9%), si STRAT-002 tu (58.75% > 57.8%). Trade-off: prior nzito →
  statistical alarm polepole kwa abrupt decay (45% true win: hakuna alarm @60 fwd, inafira ~120)
  — inafunikwa na rolling hard thresholds (HALT<50 inafira mara moja). Complementary; sawa.
- **Conditions 3 (non-blocking):** (1) B=50,000 kwa cells ≤8 za registration (resolution ±0.002
  vs knife-edge ya 0.002; iandikwe kwenye registration KABLA ya dirisha); (2) restatement
  isiclobber canonical outputs (--cells-file inaandika kwenye candidates{suffix}.jsonl ileile —
  scratch checkout au --out-tag; FDR line yake = SENSITIVITY, m=|cells|, kamwe si verdict);
  (3) restatement iprint lag-1 autocorr ya PnL kila cell; |ρ₁|>0.3 → recalibrate mb + jedwali
  jipya la skew-size.
- **S3-C2 registration IMEFUNGULIWA kutoka upande wangu** (B-PRIME sequencing).

## CURRENT TASK (baada ya hapa): (1) verify S3/S3b sensitivity restatement ikija (two-column
p table — je, S3b k=3 inasimama chini ya exact bootstrap p? Open question yangu ya kwanza);
(2) referee wa S3-C2 registration text (B=50k imo? MDE screen + shrunken forecasts?);
(3) baada ya R3 (WAVE-2): andika regime-conditional deployment proposal.

## COMPLETED (2026-07-13): DESIGN ya FAMILY-POOLED HOLDOUT TEST (C2-WATCH groups 4)
Deliverables: `reports/family_pooled_design.md` (registration-ready) +
`scripts/scientist_d_family_pooled_precheck.py` (kila namba inazalishwa kutoka artifacts wazi).
MAAMUZI YA DESIGN (na sababu):
- **Reps 4 mechanical** (best p_boot per group, TRAIN EV>0; tie@floor → p_z): nr4×GBPJPY
  1.5/1.5 no-LATE · nr7×EURGBP 1.5/1.0 no-LATE (tie ya cells 2 @ p=0.0001 floor — p_z
  inaamua; B=50k registration itapunguza floor hadi 2e-5) · nr7×EURJPY 1.0/3.0 · nr7×AUDUSD
  1.5/3.0. Zinarudisha HASA namba za MDE za ruling (15.2<16.8 · 1.8<2.4 · 9.6<17.7 · 5.0<9.1).
- **R-units** (pnl/(sl_atr×atr[signal bar])) sio ATR-units: deployment-consistent (fixed
  fractional risk), downside aligned ≈ −1 kila cell, pip-scale invariant. ATR-units = sensitivity
  column non-gating.
- **Pooling per-trade** (union sorted by entry ts; shares EURGBP 35/EURJPY 25/AUDUSD 22/
  GBPJPY 17 — hakuna pair >50%). Engine ileile: pvalue_boot B=50k mb3+NW, seed=registration
  string. Criterion m=1: p_boot<0.05 NA EV_R>0.
- **POOLED MDE SCREEN INAPITA ncha conservative 0.35**: EV_R(VALID) pooled +0.401, sd_R 1.34,
  N_exp 341 → MDE 0.119 R vs forecast 0.140 R (×1.18); power 0.62 @shrink 0.35 / 0.87 @0.5.
  Ndiyo hoja ya kwa nini pooling inaokoa kile per-group screen ilichokataa kihalali.
- Acceptance tests AT1-AT8 (muhimu: AT4 mixture-null size 4-component [0.04,0.06]; AT8 dry-run
  VALIDATION inatoa exact EV_R/sd_R kwa screen ya mwisho — two-point yangu inapuuza timeouts).
- Verdict semantics pre-registered: PASS = PROVEN-OOS-PROVISIONAL **family-level TU** (hakuna
  STRAT-00x, hakuna capital; forward tranche inabaki); FAIL = hakuna re-test ya compression-H4
  kwenye dirisha hili MILELE (information consumed). Caveats 4 zinaingia rekodi verbatim
  (confirmation-not-discovery; era overlap na STRAT-001/002; VALID hot ~2×; power 0.62 =
  FAIL 38% inawezekana hata forecast ikiwa sahihi — hakuna "underpowered" complaint baadaye).
SEQUENCING: IMPLEMENTER-A build → SCIENTIST-D referee (AT4 kwa MC yangu huru) → AT8 dry-run →
screen exact → Chief freeze kwa commit → one-shot token → verdict+CI.

## CURRENT TASK (baada ya hapa): (1) referee wa implementation ya family_pooled.py ikija
(AT1-AT8; AT4 kwa MC huru yangu); (2) verify exact screen ya AT8 kabla ya freeze; (3) baada
ya R3 (WAVE-2): regime-conditional deployment proposal (bado pending kutoka Chief response).

## CURRENT TASK (2026-07-13): REFEREE ya family_pooled build (design yako; commit acbc11f)
sweep 22/22; AT1-AT8 PASS. KAZI: (1) AT4 FULL MC huru — mixture 4-component (win/WL/share za reps,
design §4) EV=0, interleaved, N=341, ≥20k reps, B=50k → size pvalue_boot@0.05 ∈[0.040,0.060]?
+ AR(0.5) variant ≤0.08 (build ilitoa 0.066 scaled — thibitisha full). (2) OQ#1 ruling (Chief:
non-blocker; kubali wording fix au pinga). (3) verbatim-vs-implemented (R-norm, pool sort/dedup,
seed kutoka reg string). Ripoti "tayari referee-pooled" (APPROVED/FIXES). APPROVED → Operator dry-run.
