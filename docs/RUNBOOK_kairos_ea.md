# RUNBOOK — KAIROS EA (MQL5): compile → Strategy Tester → demo chart → signal-log

> KAIROS EA (`mql5/KAIROS.mq5`) = port HALISI ya STRAT-001/002 (docs/KAIROS_EA_CHARTER.md).
> **Demo/backtest PEKEE.** Live (akaunti halisi) = Faza 4 — inahitaji **SAINI YA PD** (§3.1b/§9).

## 0. Strategy (parity na Python — usibadilishe)
- **nr7 (compression):** `range(bar)=high−low`; `nr = range[signal] ≤ MIN(range za bars InpNR zilizofungwa, INCLUSIVE)`.
  buy-stop = `high+tick`, sell-stop = `low−tick` (OCO). Chanzo: `event_library_v2.nr7_break`.
- **no-LATE:** session ya bar ya **ENTRY (i+1)** LAZIMA 0–16 (ASIA/LONDON/NY); hour ≥ `InpNoLateStart` (17) = LATE → hakuna order.
  (Python `_mask_context` inatumia `_sess(hour[i+1])` — ratiba ex-ante; kwa H1 EA entry bar = bar inayoundwa.)
- **ATR:** Wilder ATR(`InpATR`=14). **SL/TP kwa ATR ya bar ya SIGNAL** (Python `a=atr[i]`); tie → SL.
- **OCO:** moja ikijaza → nyingine inafutwa; pending isiyojaza inaisha mwisho wa bar ya entry (window = bar MOJA).

## 1. Install + compile (MetaEditor)
1. Nakili `mql5/KAIROS.mq5` → `<MT5 Data Folder>/MQL5/Experts/KAIROS.mq5`
   (MT5: **File → Open Data Folder**).
2. Fungua MetaEditor (F4 kutoka MT5) → fungua `KAIROS.mq5` → **Compile (F7)**. Lazima: `0 errors, 0 warnings`.
3. `KAIROS` sasa inaonekana kwenye MT5 **Navigator → Expert Advisors**.

## 2. Inputs — KAIROS-1 vs KAIROS-2 (variants, si EA mbili)
| Input | KAIROS-1 (USDCHF) | KAIROS-2 (USDJPY) | Maana |
|-------|-------------------|-------------------|-------|
| Symbol/chart | **USDCHF** H1 | **USDJPY** H1 | pair (attach kwenye chart husika) |
| `InpSL_mult` | **2.0** | **1.0** | SL = mult × ATR |
| `InpTP_mult` | **1.0** | **1.0** | TP = mult × ATR |
| `InpNR` | 7 | 7 | nr window |
| `InpATR` | 14 | 14 | Wilder ATR |
| `InpNoLateStart` | 17 | 17 | LATE huanza (hakuna entry) |
| `InpTick` | 0.1 | 0.1 | stop offset (PIPS; Python TICK) |
| `InpMagic` | e.g. 20260726**1** | e.g. 20260726**2** | tofautisha instances |
| `InpRiskPct` | 0.5 | 0.5 | risk % ya balance/trade |
| `InpMaxPositions` | 1 | 1 | position moja/symbol |
| `InpDailyLossPct` | 5.0 | 5.0 | daily-loss guard |

> Chanzo: `live_engine.STRATS` — KAIROS-1 USDCHF SL2.0/TP1.0, KAIROS-2 USDJPY SL1.0/TP1.0.

## 3. Backtest — Strategy Tester (chombo cha PD)
1. MT5: **View → Strategy Tester** (Ctrl+R).
2. Expert = `KAIROS`; Symbol = **USDCHF** (au USDJPY); Period = **H1**.
3. Modeling = **Every tick based on real ticks** (bora) au *1 minute OHLC* (haraka).
4. Weka tarehe (Date range), Deposit, Leverage; **Inputs** tab → weka SL/TP mult ya variant.
5. **Start**. Angalia: graph ya balance, `Results`/`Journal`. Signal-log → `MQL5/Files/` ya tester.

> **CROSS-CHECK, si replica:** fill/spread/tick data ya MT5 ≠ Python backtest. Kigezo = EV chanya +
> mwelekeo unaolingana. Tofauti kubwa → chunguza fill/spread (KAIROS_EA_CHARTER §MIPAKA).

## 4. Demo chart (unaona ikitrade kwenye terminal)
1. Fungua akaunti ya **DEMO** (broker); fungua chart **USDCHF H1**.
2. Buruta `KAIROS` kutoka Navigator → chart. Weka inputs (KAIROS-1). **OK**.
3. Wezesha **AutoTrading** (kitufe cha juu) + ruhusu "Allow Algo Trading" kwenye EA dialog.
4. EA inasubiri bar mpya ya H1; ikipata nr7 + si LATE → inaweka OCO buy-stop/sell-stop.
5. (KAIROS-2) rudia kwenye chart **USDJPY H1** na `InpMagic` tofauti.

## 5. Signal-log (parity EA-2)
Faili: `MQL5/Files/KAIROS_signals_<SYMBOL>_<MAGIC>.csv` (tester: Files ya tester).
Header: `ts,range_pips,rmin_pips,nr,atr_pips,session,long_level_pips,short_level_pips`.
- **1 mstari kwa kila bar ya H1 iliyofungwa** (signal bar), bila kujali kama trade imefanyika.
- Thamani zote **PIP-SPACE** (÷ pip size) kwa ulinganisho wa moja kwa moja na Python (`nr7_break`+`wilder_atr`).
- `ts` = muda wa **signal bar** (epoch). `session` = session ya **entry bar (i+1)** — ndiyo inayotumika kwenye
  no-LATE gate (parity na `_mask_context`). `nr` = 1/0. `long/short_level` = `high+tick` / `low−tick`.
- **EA-2** (kazi ijayo): harness ya Python italinganisha CSV hii na `nr7_break`+`wilder_atr`+`_sess` kwenye
  bars zilezile → `range/rmin/nr/atr/long_level/short_level/session` LAZIMA zifanane (tolerance ya rounding).
  ATR: EA inatumia `iATR` (Wilder) — seeding ya awali inaweza tofautiana kidogo na `wilder_atr` (atr[0]=tr[0])
  lakini inaungana ndani ya tolerance baada ya warmup.

## 6. Usalama / mipaka
- **Demo pekee** hadi Faza 4. Live = SAINI YA PD (§3.1b/§9.3 orders+token). EA hii **HAINA** kizuizi cha
  akaunti live — nidhamu ni ya Operator/PD (usiwashe kwenye akaunti halisi bila saini).
- EA ina **strategy logic** (IP ya PD/local). Conduit-EA isiyo na logic (kwa LESSEE, §9) = kazi tofauti.
- Position moja/symbol; magic per instance; daily-loss guard = FTMO-style (deterministic).
