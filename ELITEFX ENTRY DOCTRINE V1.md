# ELITEFX_ENTRY_DOCTRINE_V1.md

**Chief Quant (Unified) — Entry Science: Familia 7, Entries 16, na Safu ya Uchambuzi wa Soko**

Version: 1.0
Status: APPROVED — ACTIVE (Entry-domain SSOT)
Date: 9 July 2026
Authority: Single Source of Truth kwa domain ya **Entries** (Alpha Engineering S-series)
Imefunguliwa chini ya: `ELITEFX MASTER ARCHITECTURE V1.md` §8.2 (knowledge-need) — directive ya
Project Director (2026-07-08/09). Market Doctrine V6.9 inabaki FROZEN; hii ni doctrine MPYA,
si amendment ya V6.9.
Companions: `ELITEFX DOCTRINE V6.9.md` (Market) · `ELITEFX DECISION DOCTRINE V12.md` (Decision)
Code ya rekodi: `src/research/event_library_v2.py` (EVENTS_V2) · `src/research/event_quality_report.py`

> Live status: `docs/CHIEF_STATUS.md`. Runbook ya Operator: `docs/RUNBOOK_event_quality.md`.

---

## §1 — KANUNI KUU (Entry Constitution)

```text
EP-1  ENTRY = TRIGGER; UCHAMBUZI = CONTEXT.  Entry haisemi soko liko hali gani — inasema
      "sasa hivi". Uchambuzi wa soko (volatility/activity/spread states, session, age)
      unaishi NJE ya entry na unaizunguka. AI inajifunza ramani kamili:
      P(matokeo | context ya soko, event, params) — SIO trigger peke yake (BOT).
EP-2  EVENT ≠ CONDITION.  Signal halali ni TRANSITION (edge-trigger + rearm/cooldown).
      Condition inayowaka kila bar ya tatu (V1: pullback 334/1000 bars) si event — ni kelele
      inayochoma spread (chanzo cha Phase 12: 0/5 proven).
EP-3  KILA ENTRY NI STATISTICAL HYPOTHESIS (Principle 29 inaendelea).  Entry inaitwa
      "strategy" TU baada ya S2 (walk-forward + FDR) na S3 (holdout, mara moja).
EP-4  HAKUNA METRIC BILA COSTS.  Kila pima la entry linalipa spread halisi ya bar ya entry
      + slippage (market 0.1 pip / stop 0.3 pip). Tie-bar (SL+TP bar moja) -> SL (worst case).
EP-5  "NEXT BAR" HONEST + NO LOOKAHEAD.  Market entry = OPEN ya bar ijayo; stop entry =
      touch ya bar ijayo (gap-honest: max(level, open) kwa long). Signal ya index i
      inatumia data ya <= i tu.
EP-6  SACRED SPLITS.  Exploration ya entries = TRAIN 2016-2022 TU (enforced kwa code).
      VALIDATION 2023-24 = S2. HOLDOUT 2025+ = S3, mara moja, kwa token ya Chief.
EP-7  FAMILIA KABLA YA WINGI.  Mbinu mpya inaongezwa TU ikiwa ni familia/mantiki mpya —
      kila hypothesis ya ziada inapandisha kizingiti cha FDR kwa zote (LESSON-002).
```

## §2 — FAMILIA 7 ZA ENTRIES (taxonomy rasmi)

Kila familia ina mantiki ya soko inayojitegemea (kwa nini edge ingeweza kuwepo):

| Familia | Mantiki ya soko | Entries |
|---------|-----------------|---------|
| F1 TREND-PULLBACK | Trend hujirudia; rukio la muda mfupi ndani ya trend = bei ya punguzo | pullback_v2 · trend_resume · second_chance · rsi2_pullback |
| F2 BREAKOUT | Kizuizi kikivunjika, order-flow hufuata; wengi hushindwa, wanaofanikiwa hulipa sana | breakout_stop · jump_off |
| F3 COMPRESSION→EXPANSION | Volatility hu-cluster; mgandamizo (range nyembamba) hutangulia mlipuko | inside_break · nr7_break |
| F4 SESSION | FX ina muundo wa masaa (London/NY open); liquidity + participation hubadilika kwa ratiba | session_orb |
| F5 SHOCK/MOMENTUM | Habari/mtiririko mkubwa hu-underreact kwa muda mfupi | shock_follow · big_range_mo |
| F6 MEAN-REVERSION | Bei iliyovutwa mbali kupita kiasi hurudi (liquidity providers hurejesha) | mr_zscore · lowvol_reversal · bb_fade |
| F7 PRICE-ACTION | Mifumo ya candles kwenye MAHALI muhimu (extreme) = alama za mabadiliko ya udhibiti | pattern_3lows · engulf_extreme |

## §3 — ENTRIES 16 (rejista rasmi — `EVENTS_V2`)

Aina: **market** = agizo la market kwenye OPEN ya bar ijayo · **stop** = stop order,
fill kwa touch ya bar ijayo (intrabar). Zote zime-mirror long/short, edge-triggered.

| # | Entry | Familia | Aina | Chanzo | Rule (upande wa long; short = mirror) |
|---|-------|---------|------|--------|----------------------------------------|
| 1 | pullback_v2 | F1 | market | KJ #1 | c>c[5] NA c<c[20] (rukio dhidi ya trend fupi ndani ya trend kubwa) |
| 2 | trend_resume | F1 | market | KJ #2 + mod | c>SMA20 NA pullback imetokea (c[1]<c[3]) NA resumption (c>high[1]) |
| 3 | second_chance | F1 | market | KJ #5 | c>SMA10 NA (c<percentile-10 ya closes 15 AU downs 3 mfululizo) |
| 4 | rsi2_pullback | F1 | market | MPYA (Connors) | c>SMA100 NA RSI(2)<10 — kasi ya returns, sio umbali wa bei |
| 5 | breakout_stop | F2 | stop | KJ #4 | buy-stop = HH(10)+tick; sell-stop = LL(10)−tick (OCO) |
| 6 | jump_off | F2 | stop | KJ #3 | trend (c>c[20]) → buy-stop = pbase + 2×ATR(15); pbase=(HH10+LL10)/2 |
| 7 | inside_break | F3 | stop | MPYA | inside bar → stops kwenye high/low za bar-mama (OCO) |
| 8 | nr7_break | F3 | stop | MPYA (Crabel) | range nyembamba zaidi ya bars 7 → stops juu/chini ya bar hiyo |
| 9 | session_orb | F4 | stop | KJ #7 kwa FX | range ya saa 7-8 (London open) → stops pande zote, hai saa 9-12 |
| 10 | shock_follow | F5 | market | KJ #7 proxy | |ret| > 3×std(ret,20) → fuata mwelekeo wa mshtuko |
| 11 | big_range_mo | F5 | market | KJ #6 | range > 2×std+mean (ranges 5) NA momentum ya bars 10 |
| 12 | mr_zscore | F6 | market | toleo kali la pocket P100 | stretch (SMA20−c)/ATR14 ≥ 1.5 → nunua kurudi |
| 13 | lowvol_reversal | F6 | market | KJ #8 (+volume) | tick-volume < SMA(tc,5) NA c = lowest(c,5) |
| 14 | bb_fade | F6 | market | MPYA | close NJE ya Bollinger(20,2) jana, NDANI leo → fade (re-entry = confirmation) |
| 15 | pattern_3lows | F7 | market | KJ #9 | lows 3 zinazopanda NA c>high[1] |
| 16 | engulf_extreme | F7 | market | MPYA | bullish engulfing IKITOKEA kwenye low ya bars 10 (pattern + MAHALI) |

Mbinu MPYA 5 (nje ya KJ-9, directive ya PD 2026-07-09): rsi2_pullback · inside_break ·
nr7_break · bb_fade · engulf_extreme.

## §4 — SAFU YA UCHAMBUZI WA SOKO (context layer)

Kabla entry haijapimwa/kutumika, soko linachambuliwa kwa safu hizi (zote no-lookahead):

```text
C1  MARKET STATES (market_state_engine): volatility_state (LOW/NORMAL/HIGH),
    activity_state, spread_state — rolling terciles, deseasonalized kwa saa.
C2  SESSION: ASIA (0-6) · LONDON (7-11) · NY (12-16) · LATE (17-23) — spread/vol
    hutofautiana mara 3-5; entry ileile ina EV tofauti kwa session.
C3  STATE AGE + TRANSITIONS (F-001..F-007): soko limekaa hali hii muda gani, na
    linaelekea wapi.
EVIDENCE: Phase 12 Q4 — edge ni STATE-DEPENDENT (mf. mean_reversion: −0.68 LOW,
+0.20 NORMAL, −0.14 HIGH). Kwa hiyo kila entry inapimwa NDANI ya context
(event_quality_report: jedwali entry×vol-state na entry×session), na grid ya S1 ina
dimension ya context filter: {none, vol_state, session, vol_state×session}.
```

## §5 — NJIA YA UTHIBITISHO (entry → strategy → AI)

```text
S0 (HII):  Entry Doctrine + EVENTS_V2 + harness ya haki  ................. DONE 2026-07-09
RUN:       event_quality_report kwenye data halisi (TRAIN)  .............. Operator
S1:        strategy_lab — grid: entries 16 × pairs 9 × TF × SL/TP × context filters
S2:        walk-forward 2023-24 + BH-FDR + null baseline  → survivors
S3:        HOLDOUT 2025+ (mara moja, token ya Chief)      → strategies rasmi
S4:        deploy kama decision policies + K4 training data → AI inajifunza
           P(matokeo | context, event, params) — entries/exits/management (FTMO = algo rules)
```

## §6 — RED LINES (zinazorithiwa + mpya)

- Profitable ≠ Tradable Edge (daima).
- Hakuna kuchagua kwa holdout; hakuna metric bila costs; survivors = CANDIDATES hadi S3.
- LESSON-001 (static ranking hufa OOS) · LESSON-002 (FDR lazima) · LESSON-029.
- Entry mpya bila familia/mantiki mpya = REJECTED by default (EP-7).
- Mabadiliko ya doctrine hii: Chief pekee, na yanarekodiwa hapa + CHIEF_STATUS.

*Profitable ≠ Tradable Edge. Protect capital first.*
