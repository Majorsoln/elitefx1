# C2-1 — BEST 10 STRATEGY HYPOTHESES (STRATEGIST-M)

*2026-07-14 | STRATEGIST-M | Mzunguko-2 (docs/CYCLE2_CHARTER.md) | TF za entry: 15m/30m PEKEE |
HTF context: H4/D1 features za `htf_context.py` (as-of backward, no-lookahead PASS)*

> **UAMINIFU (charter #3):** hii ni **HYPOTHESIS-LIST, si PROVEN-LIST.** Ranked kwa logic ya
> trading + priors za ndani (STRAT-001/002, C2-WATCH, Phase-12 pockets, lessons 36). Kila moja
> ni falsifiable: sheria zote ni NAMBA/features zinazohesabika. Uthibitisho unapita gate ya
> `docs/STRATEGIES.md` (S1 TRAIN → S2 VALID+BH-FDR → S3 HOLDOUT one-shot). Sithibitishi mwenyewe;
> sikugusa holdout wala dirisha bikira lolote. Profitable ≠ Tradable Edge (LESSON-029).

---

## 0) Kanuni za muundo zilizotumika (zinabana kila hypothesis)

1. **HTF-context = FILTER ON SIGNALS** (mtindo wa `_mask_context`, KABLA ya `episodes()`) —
   si post-hoc (Chief fix 2026-07-09; LESSON-009).
2. **Decidability (EP-5):** HTF context + vol state = value ya **SIGNAL bar i** (as-of joined,
   bar iliyoFUNGWA); session = **saa ya ENTRY bar i+1** (ratiba, ex-ante). Hakuna look-ahead.
3. **Trigger = edge-trigger + rearm** (D1 fix ya V2) au stop-arm; entry = next-bar honest
   (market: open ya i+1; stop: touch ya i+1, gap-honest).
4. **Exit = SL/TP kwa ATR ya signal bar + max_hold** (harness ya `episodes()` kama ilivyo).
5. **Costs kwanza:** spread med 15m/30m (report C2-0): EURUSD 0.30 · USDJPY 0.40 · EURJPY 0.70 ·
   GBPUSD/EURGBP 0.90 · USDCHF/AUDUSD/EURCHF 1.00 · NZDUSD 1.10 · USDCAD 1.20 · GBPJPY 1.70 ·
   XAUUSD 35 (pip 0.01). Kwenye 15m ATR ni ndogo → cost share kubwa. Kwa hiyo: **default ya
   entry ni 30m**; 15m inatumika TU pale granularity ni ya lazima (ORB, shock) na kwa pairs za
   spread ndogo. Hakuna hypothesis yenye holding ya bars<8 za 15m (edge ndogo kuliko gharama).
6. **Context isiwe rare-state:** kila filter imechaguliwa itoe kiasi kikubwa cha bars
   (LESSON-007: rare states = execution risk; pia N ya kutosha kwa power — C2-WATCH ilikufa
   kwa power 0.62).
7. **Atomic unit = configuration (event × context)** — LESSON-027. Kila hypothesis hapa NI
   configuration kamili, si event peke yake.

**Notation ya context (features ZILIZOPO kwenye `data/processed/context/`):**
`d1_trend_sign`, `h4_trend_sign` ∈ {-1,0,+1} (linreg slope /ATR, deadband 0.02) ·
`h4_vol_state`, `d1_vol_state` ∈ {LOW,NORMAL,HIGH} · `h4_dist_res_atr`, `h4_dist_sup_atr`,
`d1_dist_res_atr`, `d1_dist_sup_atr` (umbali hadi rolling S/R 20-bar, units za ATR) ·
`h4_rsi14`, `d1_rsi14` · `h4_roc10`, `d1_roc10`. Za LTF bar yenyewe: `volatility_state`,
`activity_state`, `spread_state`, `session`, `hour`.

---

## 1) JEDWALI LA BEST 10 (ranked)

| # | Jina (ID) | HTF-context (namba) | Trigger (TF) | Exit (SL/TP ATR, hold) | Hypothesis fupi | Pairs (tarajio) |
|---|-----------|---------------------|--------------|------------------------|------------------|------------------|
| 1 | **HC2-01 ALIGNED-COMPRESSION** | `d1_trend_sign≠0` NA `h4_trend_sign==d1_trend_sign` | `nr7_break`/`nr4_inside` 30m, **upande wa trend TU** (one-sided stop) | SL 1.5 / TP 2.0–3.0, hold 32b | Compression-break iliyothibitika + HTF alignment huondoa nusu ya OCO inayopoteza | USDCHF, USDJPY, EURJPY, AUDUSD, GBPJPY |
| 2 | **HC2-02 LONDON-ORB-D1** | `d1_trend_sign≠0`; entry LONDON | `session_orb` 15m (range 07–08, trade 09–12), upande wa `d1_trend_sign` TU | SL 1.5 / TP 2.0, hold 24b (siku moja) | Asia range = liquidity pool; London open hujilimbikizia information flow; break yenye D1 bias huendesha siku | GBPUSD, EURUSD, EURGBP, GBPJPY |
| 3 | **HC2-03 TREND-PULLBACK-RESUME** | `h4_trend_sign==+1` NA `d1_trend_sign==+1` NA `h4_rsi14<70` (mirror short: −1/−1/>30) | `trend_resume` au `rsi2_pullback` 30m, upande wa trend TU | SL 1.5 / TP 2.0, hold 32b | Order-flow ya taasisi hununua pullbacks ndani ya trend (execution kwa tranches); LTF oversold-ndani-ya-uptrend = discount | USDJPY, GBPJPY, XAUUSD, EURUSD |
| 4 | **HC2-04 NESTED-SQUEEZE** | `h4_vol_state=="LOW"` (regime ya mgandamizo HTF) | `squeeze_break` 30m (OCO pande zote) | SL 1.5 / TP 2.0–3.0, hold 48b | Mgandamizo wa tabaka mbili (H4 LOW-vol + 30m squeeze) hutangulia expansion kubwa (vol clustering / regime transition) | EURUSD, USDCHF, EURCHF, EURGBP, USDJPY |
| 5 | **HC2-05 ALIGNED-SHOCK** | shock dir == `d1_trend_sign` (≠0); entry LONDON/NY | `shock_follow` 15m (k=3), upande wa trend TU | SL 1.5 / TP 2.0, hold 16b | Shock kuelekea trend ya HTF = underreaction/continuation; shock dhidi ya trend hu-revert — alignment huchuja nusu inayorudi | EURJPY, USDJPY, GBPJPY, XAUUSD |
| 6 | **HC2-06 HTF-SR-FADE** | `d1_dist_res_atr<=0.5` NA `h4_trend_sign<=0` (short kwenye resistance; mirror long kwenye support) | `bb_fade` au `engulf_extreme` 30m, upande wa fade TU | SL 1.5 / TP 1.5, hold 24b | HTF S/R hujilimbikizia limit orders/barriers; approach BILA momentum ya HTF hukataliwa | EURGBP, EURCHF, USDCHF, AUDUSD, NZDUSD |
| 7 | **HC2-07 GAP-FADE-QUIET** | `h4_vol_state!="HIGH"` (gap isiyo ya news-regime) | `gap_fade` 30m (k=0.5 ATR) | SL 1.5 / TP 1.5, hold 16b | Gap za weekend/rollover = liquidity vacuum; bila information mpya bei hurudi kwenye close ya zamani; HIGH-vol regime = gap za news (haziji-fill) — zinachujwa | ZOTE isipokuwa XAUUSD (spread ya open) |
| 8 | **HC2-08 NY-HANDOFF-DRIFT** | `d1_trend_sign≠0` NA mwelekeo wa London == `d1_trend_sign` | `london_drift` 30m variant: saa 12–13 UTC, mom=London bars (8×30m), upande wa makubaliano TU | SL 1.5 / TP 1.5, hold 16b | NY participants hujiunga na move ya Ulaya iliyopo (order splitting/herding) — handoff drift; D1 agreement huchuja siku za reversal | USDJPY, USDCAD, EURUSD, XAUUSD |
| 9 | **HC2-09 ASIA-RANGE-MR** | `d1_trend_sign==0` (D1 flat) NA `h4_vol_state!="HIGH"`; entry ASIA | `mr_zscore` 30m (k=1.5) pande zote | SL 1.5 / TP 1.5, hold 16b | Asia kwa EUR-crosses = inventory management, information flow ndogo → stretch hu-revert kwenye mean; D1-flat huondoa trend days | EURUSD, EURGBP, EURCHF, USDCHF |
| 10 | **HC2-10 FAILED-BREAK-SWEEP** | `d1_dist_res_atr<=0.5` (kwenye D1 extreme; mirror support) | **TRIGGER MPYA** `false_break` 30m: intrabar break ya HH(20) kisha close chini yake → short (mirror long) | SL 1.0 / TP 2.0, hold 24b | Stop-hunt/liquidity sweep: break kwenye HTF extreme inayoshindwa hunasa breakout traders; stops zao ndizo fuel ya reversal | EURGBP, EURCHF, AUDUSD, NZDUSD, XAUUSD |

**Muundo wa panga-mbili wa list:** #1–#5 ni **continuation/expansion** (priors kali za ndani),
#6–#10 ni **reversion/structure** (diversification ya mechanism — directive ya PD "trade za aina
tofauti"). Kila kundi lina angalau trigger moja iliyopo tayari kwenye `EVENTS_V2` — ni #10 pekee
inayohitaji event fn mpya.

---

## 2) MAELEZO KAMILI KWA KILA HYPOTHESIS (A–E + features)

### HC2-01 — ALIGNED-COMPRESSION (rank 1)

- **A. HTF-context:** `d1_trend_sign != 0` **NA** `h4_trend_sign == d1_trend_sign`
  (alignment kamili ya H4+D1). Values za SIGNAL bar (as-of joined). Hii ni filter pana
  (trend deadband 0.02 → sehemu kubwa ya bars ina sign ≠ 0) — si rare state.
- **B. Trigger (30m):** `nr7_break` (na variant `nr4_inside`) — stop-arm ILIYOPO, lakini
  **one-sided**: kama trend=+1, `long_level` pekee inabaki (`short_level=NaN`); mirror kwa −1.
- **C. Exit:** SL 1.5 ATR / TP {2.0, 3.0} ATR (grid), max_hold 32 bars za 30m (~siku 0.7 za trading).
  Hakuna look-ahead — harness ya `episodes()` kama ilivyo.
- **D. Hypothesis ya kiuchumi:** compression→expansion ndiyo mechanism PEKEE iliyothibitika
  kwenye mfumo huu (STRAT-001/002 H1; C2-WATCH H4 4/4 reps chanya). Udhaifu wake wa asili ni
  OCO symmetric: nusu ya breaks ni dhidi ya flow ya HTF na hufa haraka. Kama HTF trend ipo,
  order flow ya taasisi (inayojenga trend hiyo) inaelekea kuunga mkono break ya upande wake —
  tunanunua expansion pale tuli-na-tailwind. Hii ni behavioral (breakout traders + trend
  followers wanaingia pamoja) na structural (stops za counter-trend juu ya level).
- **E. Pairs:** USDCHF, USDJPY (nr7 proven H1 — extension ya TF, si copy), EURJPY, AUDUSD,
  GBPJPY (reps za C2-WATCH zenye EV_R chanya). Spread zote ≤1.7 pips kwenye 30m ATR ya kutosha.
- **Features HASA:** `d1_trend_sign`, `h4_trend_sign` (zipo) + **direction-aware context mask**
  (mpya — angalia §3) + context loader ndani ya `strategy_lab.load_window` (mpya).

### HC2-02 — LONDON-ORB-D1 (rank 2)

- **A. HTF-context:** `d1_trend_sign != 0` ya signal bar. Session ya entry = LONDON
  (built-in kwenye trigger: trade_hours 09–12 UTC).
- **B. Trigger (15m):** `session_orb` ILIYOPO: range = high/low ya saa 07–08 UTC (bars 8 za 15m),
  stop orders 09–12 UTC — lakini **one-sided kwa `d1_trend_sign`**. 15m ni ya lazima hapa
  (range ya saa 1 kwa 30m ni bars 2 tu — haina definition).
- **C. Exit:** SL 1.5 / TP 2.0 ATR (ATR ya 15m signal bar), max_hold 24 bars (hadi ~15:00 UTC —
  trade ya intraday inayokufa kabla ya LATE). Grid ndogo: TP {1.5, 2.0}.
- **D. Hypothesis:** Asia session hujenga range yenye stops pande zote (liquidity pool).
  London open ndiyo kipindi cha kwanza cha information flow nzito ya siku (Ulaya inafungua,
  fixings, orders za corporate). Break ya range hiyo YENYE bias ya D1 huwa mwanzo wa
  directional day — mechanism ya KJ #7/D3 iliyorudishwa V2, sasa na HTF gating. Session
  structure ni kali FX (spread/vol 3–5x kati ya sessions — docstring D3).
- **E. Pairs:** GBPUSD, EURUSD, EURGBP (London-centric flows), GBPJPY (vol ya kutosha kulipa
  spread 1.7). USDJPY inaingia kama sensitivity (Tokyo afternoon overlap).
- **Features HASA:** `d1_trend_sign` (ipo), `session_orb` params (zipo), direction-aware mask
  (mpya), `hour` (ipo).

### HC2-03 — TREND-PULLBACK-RESUME (rank 3)

- **A. HTF-context:** `h4_trend_sign == +1` NA `d1_trend_sign == +1` NA `h4_rsi14 < 70`
  (long; mirror short: −1, −1, `h4_rsi14 > 30`). RSI guard inazuia kuingia trend iliyoiva
  (exhaustion) — namba, si maoni.
- **B. Trigger (30m):** `trend_resume` ILIYOPO (pullback + resumption bar: c>SMA20, c[1]<c[3],
  c>h[1]) — upande wa trend TU. Variant ya grid: `rsi2_pullback` (ma_len=100, lo=10) —
  mechanism moja (buy-the-dip-in-trend), velocity tofauti.
- **C. Exit:** SL 1.5 / TP {2.0, 3.0}, max_hold 32 bars. Asymmetric TP>SL kwa makusudi:
  LESSON-011 — context lifts EV via **payoff asymmetry**, not win probability.
- **D. Hypothesis:** taasisi hazinunui breakout — zina-execute kwa tranches ndani ya trend;
  pullback ndipo passive bids zao ziko. Retail hushtuka na kuuza pullback (loss aversion);
  sisi tunanunua kutoka kwao kwenye discount, na resumption bar (c>h[1]) inathibitisha flow
  imerudi kabla hatujaingia (haishiki kisu). Prior ya ndani: deep_pullback/trend familia
  ilikuwa pocket ya Phase 12 (EURUSD P97, LESSON-018 candidate).
- **E. Pairs:** USDJPY, GBPJPY (trend persistence ya JPY crosses wakati wa carry regimes),
  XAUUSD (trends ndefu za gold; ATR 30m kubwa vs spread 35 → cost share OK), EURUSD (spread bora).
- **Features HASA:** `h4_trend_sign`, `d1_trend_sign`, `h4_rsi14` (zipo); direction mask (mpya).

### HC2-04 — NESTED-SQUEEZE (rank 4)

- **A. HTF-context:** `h4_vol_state == "LOW"` ya signal bar (regime ya mgandamizo ya HTF,
  deseasonalized, trailing — decidable). Hakuna trend filter — trade hii ni ya expansion
  isiyo na mwelekeo wa awali.
- **B. Trigger (30m):** `squeeze_break` ILIYOPO (BB-width kwenye quantile 0.15 ya bars 100 →
  stops kwenye HH/LL za bars 5). OCO pande zote — direction inatoka kwenye break yenyewe.
- **C. Exit:** SL 1.5 / TP {2.0, 3.0}, max_hold 48 bars (expansion ya regime huchukua muda).
- **D. Hypothesis:** volatility clustering (GARCH stylized fact): vol ya chini kihistoria
  hairudi kawaida polepole — hulipuka. Mgandamizo wa tabaka mbili (H4 regime LOW + 30m squeeze
  ya multi-bar) ni toleo la nested la familia iliyothibitika, likiwinda expansion KUBWA zaidi
  kuliko NR7 ya bar moja. Structural: wiki za range hujenga stop clusters pande zote mbili;
  break yoyote ina fuel.
- **E. Pairs:** EURUSD, USDCHF, EURCHF, EURGBP (pairs zinazokaa kwenye ranges ndefu — SNB/ECB
  crosses), USDJPY. EURCHF hasa: mgandamizo ni tabia yake ya msingi.
- **Features HASA:** `h4_vol_state` (ipo); `squeeze_break` (ipo); context loader (mpya).
  Hakuna direction mask (OCO).

### HC2-05 — ALIGNED-SHOCK (rank 5)

- **A. HTF-context:** direction ya shock == `d1_trend_sign` (≠0) — yaani long shock inakubaliwa
  tu kama `d1_trend_sign==+1` (mirror short). Session ya ENTRY bar ∈ {LONDON, NY} (shocks za
  Asia kwenye majors ni thin-liquidity artifacts).
- **B. Trigger (15m):** `shock_follow` ILIYOPO (|ret| > 3×std ya returns 20 zilizopita, rearm 10).
  15m ni ya lazima: shock hufa ndani ya dakika 30–60; 30m inachelewa. Spread-guard:
  `spread_state != "WIDE"` ya signal bar (shock nyingi huja na spread blowout — LESSON-007).
- **C. Exit:** SL 1.5 / TP 2.0, max_hold 16 bars (saa 4 — continuation ya shock ni ya muda mfupi).
- **D. Hypothesis:** post-news drift/underreaction: shock kuelekea trend ya HTF ni information
  inayothibitisha positioning iliyopo → follow-through (wale walio-underweight wanakimbilia).
  Shock DHIDI ya trend mara nyingi ni stop-run au overreaction → hu-revert. Kuchuja kwa
  alignment kunaondoa nusu inayorudi — hii ndiyo tofauti na shock_follow ghafi (TIER1 ilikuwa
  EURJPY/USDJPY bila HTF gating).
- **E. Pairs:** EURJPY, USDJPY, GBPJPY (JPY crosses ndizo shock-prone: BoJ, risk-off), XAUUSD
  (shock follow-through ya gold ni documented). Spread ya JPY crosses inabebeka kwenye ATR ya shock bar.
- **Features HASA:** `d1_trend_sign`, `spread_state` (zipo); direction mask (mpya); session
  filter ya entry bar (ipo — `_mask_context`).

### HC2-06 — HTF-SR-FADE (rank 6)

- **A. HTF-context (short leg):** `d1_dist_res_atr <= 0.5` (bei ndani ya nusu-ATR ya D1
  resistance ya rolling 20) **NA** `h4_trend_sign <= 0` (hakuna momentum ya H4 inayosukuma break).
  Mirror long: `d1_dist_sup_atr <= 0.5` NA `h4_trend_sign >= 0`.
- **B. Trigger (30m):** `bb_fade` ILIYOPO (close nje ya band kisha re-entry — confirmation) au
  `engulf_extreme` (engulfing kwenye extreme ya bars 10) — upande wa fade TU.
- **C. Exit:** SL 1.5 / TP 1.5, max_hold 24 bars. Symmetric: reversion trade haina runner.
- **D. Hypothesis:** structural — HTF S/R za rolling 20-bar hujilimbikizia limit orders,
  option barriers na take-profits. Approach ya level BILA momentum ya HTF (h4_trend_sign<=0)
  ina probability kubwa ya rejection: hakuna flow mpya ya kuvunja ukuta wa liquidity. Trigger
  ya LTF (re-entry/engulfing) inasubiri rejection IANZE — hatushiki kisu; tunachukua ride ya
  kurudi ndani ya range.
- **E. Pairs:** EURGBP, EURCHF (range-dwellers wa kudumu), USDCHF, AUDUSD, NZDUSD (antipodeans
  hukaa ranges nje ya risk events). Si GBPJPY/XAUUSD — breakout pairs.
- **Features HASA:** `d1_dist_res_atr`, `d1_dist_sup_atr`, `h4_trend_sign` (zipo); direction
  mask yenye **conditions tofauti kwa long/short** (mpya — generalization ndogo ya mask).

### HC2-07 — GAP-FADE-QUIET (rank 7)

- **A. HTF-context:** `h4_vol_state != "HIGH"` ya signal bar. Rollover no-trade window
  (config: 23:00–01:00 CET) tayari ni sheria ya mfumo — gap za rollover spread hazitradiwi;
  zinabaki gap za weekend/session halisi.
- **B. Trigger (30m):** `gap_fade` ILIYOPO (open ina-gap > 0.5×ATR dhidi ya close iliyopita NA
  bar imeanza kurudi). 30m: gap za FX zinaonekana vizuri (15m ina micro-gaps za kelele).
- **C. Exit:** SL 1.5 / TP 1.5, max_hold 16 bars. TP ya asili = close ya zamani; kwa harness
  ya sasa tunatumia ATR-symmetric (k=0.5 gap ≈ TP 1.5 inashughulikia fill nyingi).
- **D. Hypothesis:** mechanism tofauti kabisa na zote (familia F8): gap bila information mpya
  ni liquidity vacuum — bei ilihama bila trading. Market makers hurudisha bei kwenye eneo la
  volume (gap fill) — documented kwa FX weekend gaps. Filter ya `h4_vol_state!=HIGH` inaondoa
  gap za news regime (hizo ni HC2-05 territory, haziji-fill).
- **E. Pairs:** zote 11 za FX (mechanism ni universal ya microstructure); XAUUSD nje — spread
  ya Sunday open ya gold humeza edge.
- **Features HASA:** `h4_vol_state` (ipo); `gap_fade` (ipo); hakuna mpya zaidi ya context loader.

### HC2-08 — NY-HANDOFF-DRIFT (rank 8)

- **A. HTF-context:** `d1_trend_sign != 0` NA sign(London move) == `d1_trend_sign`, ambapo
  London move = `c - c[8]` kwenye bars za 30m (08:00→12:00 UTC) — inahesabika kwenye signal bar
  ya saa 12, data yote ya nyuma.
- **B. Trigger (30m):** variant ya `london_drift` ILIYOPO na params (open_hr=12, mom=8) —
  edge-trigger kwenye bar ya kwanza ya NY overlap; upande wa makubaliano TU.
- **C. Exit:** SL 1.5 / TP 1.5, max_hold 16 bars (kufa kabla ya LATE/rollover).
- **D. Hypothesis:** seasonality ya saa (familia F9): NY desk inafungua ikiwa na mandate ya
  ku-execute orders zilizokusanywa; inapoona Ulaya tayari imejenga mwelekeo unaokubaliana na
  trend ya D1, inajiunga (order splitting + momentum herding ya intraday). Double-agreement
  (London + D1) huchuja "London reversal days" maarufu.
- **E. Pairs:** USDJPY, USDCAD (NY-centric: CAD data 12:30 UTC), EURUSD, XAUUSD (COMEX open).
- **Features HASA:** `d1_trend_sign` (ipo); **momentum-agreement gating** — mom ya trigger
  yenyewe inatosha (london_drift tayari ina c>cm logic; tunaongeza tu d1 mask ya direction).

### HC2-09 — ASIA-RANGE-MR (rank 9)

- **A. HTF-context:** `d1_trend_sign == 0` (D1 flat — deadband ipo kwenye feature) NA
  `h4_vol_state != "HIGH"`. Session ya ENTRY = ASIA.
- **B. Trigger (30m):** `mr_zscore` ILIYOPO (stretch ≥ 1.5 ATR kutoka SMA20, rearm 10) —
  pande zote mbili (range trade ni symmetric).
- **C. Exit:** SL 1.5 / TP 1.5, max_hold 16 bars (kufa kabla London ivunje range).
- **D. Hypothesis:** Asia kwa EUR-crosses/majors zisizo za JPY ni kipindi cha inventory
  management — information flow ndogo, dealers hurudisha bei kwenye mean baada ya order kubwa
  moja kuisukuma. D1-flat + H4-vol-si-HIGH huthibitisha hakuna trend/news inayoendesha stretch.
  Prior ya ndani: MR ilikuwa pocket ya EURUSD (LESSON-017, P100 in-sample candidate).
- **E. Pairs:** EURUSD (spread 0.30 — pekee inayobeba MR ya intraday kwa uhakika), EURGBP,
  EURCHF, USDCHF. **Tahadhari ya costs waziwazi:** hii ndiyo hypothesis yenye risk kubwa ya
  cost-share (Asia ATR ndogo); kama S1 TRAIN inaonyesha gross<2×spread kwa pair, pair hiyo
  inakufa mapema — hilo ni jibu halali (falsification), si kushindwa kwa mchakato.
- **F. Features HASA:** `d1_trend_sign`, `h4_vol_state`, session mask (zipo zote); hakuna mpya.

### HC2-10 — FAILED-BREAK-SWEEP (rank 10)

- **A. HTF-context:** `d1_dist_res_atr <= 0.5` kwa short leg (bei kwenye D1 extreme);
  mirror long kwenye `d1_dist_sup_atr <= 0.5`.
- **B. Trigger (30m) — EVENT MPYA `false_break` (naiainisha kwa Chief/IMPLEMENTER-A):**
  ```
  false_break(o,h,l,c, look=20, rearm=8):
    hh = rolling_max(h, look, PAST bars — incl=False)   # level inayojulikana kabla ya bar
    ll = rolling_min(l, look, PAST bars — incl=False)
    sc (short): (h > hh) & (c < hh)     # intrabar break juu, close imerudi chini
    lc (long):  (l < ll) & (c > ll)     # intrabar break chini, close imerudi juu
    return edge-trigger(lc, sc, rearm)  # market entry: open ya bar ijayo
  ```
  No-lookahead: hh/ll za PAST bars (incl=False kama `big_range_mo`); condition inatumia bar
  iliyofungwa. Falsifiable, namba tupu.
- **C. Exit:** SL 1.0 / TP 2.0 (stop nyuma ya sweep high — ndiyo maana SL fupi inafanya kazi
  kimuundo), max_hold 24 bars.
- **D. Hypothesis:** liquidity sweep / stop-hunt: kwenye HTF extreme, break ya intrabar
  inayoshindwa kufunga nje imeonyesha (i) stops za juu zimeliwa (fuel imeisha), (ii) breakout
  traders wamenaswa na watalazimika kutoka — exit yao ndiyo mwendo wetu. Asymmetry ya
  structural: entry karibu na sweep high → SL ndogo, target range ya kurudi → payoff 2R
  (LESSON-011: edge kupitia payoff asymmetry).
- **E. Pairs:** EURGBP, EURCHF, AUDUSD, NZDUSD (range pairs — false breaks nyingi), XAUUSD
  (sweeps za gold ni tabia ya soko lake; ATR inabeba spread).
- **Features HASA:** `d1_dist_res_atr`/`d1_dist_sup_atr` (zipo); `false_break` event fn (MPYA);
  direction mask yenye conditions tofauti kwa upande (kama HC2-06).

---

## 3) FEATURES/INFRA ZINAZOHITAJIKA (kwa Chief + IMPLEMENTER-A)

**Zipo tayari (C2-0/C2-0b — hakuna kazi):** states 15m/30m (vol/act/spread/session/hour/atr/spr);
context h4_/d1_ (trend_sign, ema_slope, linreg_slope, vol_state, act_state, dist_res_atr,
dist_sup_atr, rsi14, roc10); triggers 9 kati ya 10 (`nr7_break`, `nr4_inside`, `session_orb`,
`trend_resume`, `rsi2_pullback`, `squeeze_break`, `shock_follow`, `bb_fade`, `engulf_extreme`,
`gap_fade`, `mr_zscore`, `london_drift`).

**Za kujenga (ndogo, zote testable):**

1. **Context loader:** `load_window` (au wrapper mpya isiyogusa iliyopo) i-join context parquet
   (`data/processed/context/symbol=X/tf=Y.parquet`) kwenye state arrays kwa `ts` — columns
   h4_/d1_ ziwe arrays sambamba na o/h/l/c. (Additive, mtindo wa `+ts` ya family_pooled §8.1.)
2. **Direction-aware context mask** — generalization ya `_mask_context`:
   `_mask_context_dir(out, entry, allow_long, allow_short)` ambapo allow_* ni boolean arrays
   za signal bar. Market: `sig==+1 & ~allow_long -> 0` (mirror short). Stop: `LL[~allow_long]=NaN`,
   `SS[~allow_short]=NaN`. Semantiki ya decidability ILEILE (values za signal bar). Hii inahudumia
   HC2-01/02/03/05/06/08/10 — ndiyo kipande kikuu kimoja cha infra cha mzunguko huu.
3. **Event fn mpya moja:** `false_break` (spec §2/HC2-10) — edge-trigger, PAST-bars levels,
   self-test ya no-lookahead kama za V2.
4. **Params mpya za grid (si code):** `session_orb(range=(7,8), trade=(9,12))` kwenye 15m;
   `london_drift(open_hr=12, mom=8)` kwenye 30m.
5. **(Kwa OOB-1 tu, hiari):** composite `usd_strength` — angalia §5.

**Grid discipline (ombi kwa Chief kwa C2-2):** kila hypothesis i-freeze grid NDOGO
(SL {1.0,1.5} × TP {1.5,2.0,3.0} kadri ya spec, pairs 4–5 zilizotajwa, trigger variants ≤2) —
cells chache kwa makusudi ili BH-FDR isile power (LESSON-002; C2-WATCH ilikufa kwa power 0.62).
Ninapendekeza m_total ya C2 iwe chini ya ~1,200 cells.

---

## 4) TABIA KWA PAIR — MPANGO (baada ya S1/S2; TRAIN/VALID PEKEE)

Charter C2-5. Kwa kila hypothesis iliyonusurika S2 (BH-FDR survivor), nitajenga **pair profile**
kwa TRAIN (2016–2022) na VALID (2023–2024) TU — hakuna holdout, hakuna dirisha bikira:

**Metrics kwa kila (hypothesis × pair):**

| Metric | Kwa nini |
|---|---|
| N, trades/day | Power + availability (LESSON-033: population view) |
| EV net (pips) + 90% bootstrap CI | Ukubwa wa edge na uhakika wake (si point estimate peke yake) |
| EV_R (R-units, mtindo wa family_pooled §2) | Ulinganifu kati ya pairs (pip-scale invariant) |
| win% + payoff ratio | LESSON-011: tunatarajia edge itoke payoff asymmetry — kama inatoka win% pekee, ni red flag ya curve-fit |
| PF, maxDD (R-units) | Ubora wa stream |
| cost share = (spread+slip)/gross | Pair inayolipa zaidi ya ~50% ya gross kwa gharama = fragile (cost_stress ipo) |
| timeout share | Trade nyingi zinazokufa kwa muda = trigger haifanyi kazi kwenye pair hiyo |
| EV kwa mwaka (7 za TRAIN + 2 za VALID) | Stability/non-stationarity (LESSON-010) — sign flips zinahesabiwa |
| EV kwa session × vol_state ya signal bar | Ramani ya tabia (decidable dimensions zilezile za harness) |

**Uainishaji (pre-registered kabla ya kuangalia namba):**
- **CORE:** EV>0 TRAIN NA VALID, CI ya VALID haigusi 0 kwa mbali, cost share <50%, ≥6/9 miaka chanya.
- **COMPATIBLE:** EV>0 pande zote lakini CI pana / miaka 5/9 — inabaki kwenye pool, haiongozi.
- **UNSTABLE:** sign flip TRAIN↔VALID — haitumiki (LESSON-010; hakuna "kuielezea" post-hoc).
- **DEAD:** EV<0 pande zote — evidence ya kudumu (negatives DO persist), inaandikwa.

**Sheria za uaminifu:** (1) uainishaji unafanywa na thresholds zilizoandikwa HAPA kabla ya
kuona data — hakuna kubadilisha baada ya matokeo (LESSON-009); (2) pair-profile SIYO
re-selection — cells za S3 registration zinabaki zile za S2 survivors; profile inaamua tu
ORDER ya registration na tafsiri; (3) pairs ambazo hazikuwa kwenye grid ya hypothesis
haziongezwi baada ya kuona matokeo ya jirani (hiyo ni post-hoc subgroup — LESSON-009).

---

## 5) OUT-OF-THE-BOX (mawazo 2–3 ya kimkakati, yote falsifiable)

### OOB-1 — USD-STRENGTH COMPOSITE kama HTF context (cross-pair information)
Feature mpya: `usd_strength[t]` = mean ya `d1_trend_sign` (sign-adjusted ili +1 = USD juu)
juu ya USD pairs 7 (EURUSD−, GBPUSD−, USDJPY+, USDCAD+, USDCHF+, AUDUSD−, NZDUSD−), as-of
joined kwa kila pair (values za bars zilizofungwa — no-lookahead ileile ya htf_context).
**Matumizi:** gating ya HC2-01/03: trade USD pair long-USD tu kama `usd_strength >= 3/7`.
**Kwa nini out-of-the-box:** mfumo wote hadi sasa ni single-pair; hii ni information ya
cross-sectional ambayo desks halisi hutumia (dollar flow ni factor moja inayoendesha majors
zote). **Falsifiable:** namba moja, thresholds {2/7, 3/7, 4/7} pre-registered; inapimwa kama
context-filter ON signals kama nyingine zote.

### OOB-2 — DAY-OF-WEEK STRUCTURE kama context dimension
`dow` (0–4) ya ENTRY bar ni ratiba — decidable ex-ante kama session. Hypotheses ndogo mbili
zilizounganishwa: (a) **Friday-LATE reversion** — position squaring kabla ya weekend
hu-revert move ya wiki: `mr_zscore` 30m, entry Friday NY pekee, dhidi ya `d1_roc10` sign;
(b) **Monday continuation** — mwelekeo wa Monday London (baada ya gap kufungwa/kutokuwepo)
huendelea wiki nzima ya D1 trend. **Kwa nini:** calendar seasonality ni orthogonal kabisa na
familia zote 7 za events zilizopo — diversification halisi ya mechanism. **Falsifiable:**
dow ni column moja; cells chache, pre-registered. **Tahadhari:** N kwa dow-cell inashuka ×5 —
grid lazima iwe ndogo sana (power ya kutosha ni sharti la Chief C2-2).

### OOB-3 — VOL-STATE-TRANSITION kama TRIGGER (si context)
Hadi sasa states ni FILTERS. Wazo: event halisi ni **TRANSITION** ya state ya 30m —
`vol_state[i-1]=="LOW" & vol_state[i]=="HIGH"` (edge-trigger by construction; states ni
trailing/deseasonalized, decidable). Direction kutoka `sign(c[i] - c[i-3])` (mwelekeo wa
bars zilizosababisha regime shift). **Hypothesis:** kuamka kwa vol baada ya usingizi si kelele
— ni information event (kitu kimebadilika); mwendo wa kwanza wa regime mpya huendelea.
Hii ni cousin ya HC2-04 lakini trigger ni state machine yenyewe, si price pattern — inapima
kama tabaka la states (uwekezaji mkubwa wa mfumo) lina alpha ya moja kwa moja. **Falsifiable:**
event fn ya mistari ~10 (`state_transition_break`), harness ileile.

---

## 6) RISKS ZA MCHAKATO NINAZOZIONA (kwa Chief kabla ya C2-2)

1. **Multiple testing:** hypotheses 10 × pairs ~5 × grid ndogo bado ni cells mia kadhaa.
   Pendekezo: FDR kwa FAMILY (kama family_pooled) pale mechanism ni moja (mf. HC2-01 pairs 5
   kama stream moja ya pooled R) — inaokoa power. Chief ndiye anaamua muundo wa m.
2. **15m cost trap:** HC2-02/05 pekee ndizo 15m; kama S1 inaonyesha cost share >60% kwenye
   pairs zote, kushusha hadi 30m variant ni marekebisho ya PRE-S2 (kabla ya validation) tu —
   baada ya hapo grid ime-freeze.
3. **Overlap ya mechanisms:** HC2-01 na HC2-04 zote ni compression; HC2-06 na HC2-10 zote ni
   structure-fade. Kama zote zinapita S2, correlation ya streams izingatiwe kwenye portfolio
   (si kazi yangu — nabainisha tu kwa uaminifu).
4. **XAUUSD spread provisional (60):** kabla ya kuingiza gold kwenye S1 ya HC2-03/05/10,
   spread_quality ithibitishe max_spread halisi — vinginevyo EV ya gold itakuwa optimistic.

---

*STRATEGIST-M | C2-1 imekamilika. Hakuna dirisha bikira lililoguswa; hakuna namba ya
TRAIN/VALID iliyoangaliwa kuandika ripoti hii — priors zote zinatoka kwenye documents za
mzunguko-1 zilizofungwa (STRATEGIES.md, lessons, C2-WATCH). Next: Chief review (C2-2) —
chagua testable subset, freeze grid, kisha S1.*
