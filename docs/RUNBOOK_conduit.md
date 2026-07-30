# RUNBOOK — CONDUIT BRIDGE: live_brain (ubongo) + KAIROS_CONDUIT.mq5 (EA tupu)

> Doctrine §9: **MODEL (Python) INAAMUA, EA INATEKELEZA.** `mql5/KAIROS_CONDUIT.mq5` = conduit TUPU
> (HAINA strategy logic — ndiyo itakayokodishwa kwa lessee). Strategy/IP ipo `src/research/live_brain.py`.
> **DEMO PEKEE.** Live (akaunti halisi) = Faza 4 — **SAINI YA PD** (§3.1b/§9).

## 0. Usanifu (mtiririko)
```
MT5 --(read-only copy_rates)--> mt5_data (CANONICAL §8.3) --> live_brain edge decision
     --> commands.json --> KAIROS_CONDUIT (poll, execute) --> results.jsonl
     --> live_brain ingest --> paper_log.jsonl --> model_steward + dashboard
```
Bridge dir (transport) = `<MT5 Data Folder>\MQL5\Files\<InpBridgeDir>` (default `bridge`).
Python: `ELITEFX_BRIDGE_DIR` = folda ILE ILE.

## 1. Compile (MetaEditor) + install
1. Nakili `mql5/KAIROS_CONDUIT.mq5` -> `<MT5 Data Folder>\MQL5\Experts\` (File -> Open Data Folder).
2. MetaEditor (F4) -> fungua -> **Compile (F7)**: `0 errors`. (Agent HAWEZI compile — PD anacompile.)
3. `KAIROS_CONDUIT` sasa iko Navigator -> Expert Advisors.

## 2. Bridge dir + ENV
- Tengeneza folda `<Data Folder>\MQL5\Files\bridge`.
- Weka **`ELITEFX_BRIDGE_DIR`** (mazingira ya Python) = njia HIYO (au tumia `--bridge-dir`).
- (MT5 creds kwa canonical feed: `ELITEFX_MT5_LOGIN/PASSWORD/SERVER` — rejea RUNBOOK_kairos_ea / FWD-F2-CONN.)

## 3. Attach EA (demo chart)
1. Fungua akaunti ya **DEMO** (guard ya EA inakataa non-DEMO -> INIT_FAILED).
2. Buruta `KAIROS_CONDUIT` kwenye chart yoyote (mfano USDCHF H1). Inputs:
   | Input | Default | Maana |
   |-------|---------|-------|
   | `InpBridgeDir` | `bridge` | folda ndani ya MQL5\Files |
   | `InpPollSeconds` | 5 | poll ya commands.json |
   | `InpMagicFilter` | 0 | 0 = magics zote; vinginevyo magic moja |
   | `InpEnabled` | true | false = poll bila PLACE_OCO (CANCEL bado) |
3. Wezesha **AutoTrading** + "Allow Algo Trading". EA moja inaweza kushughulikia symbols zote
   (USDCHF+USDJPY) — commands zina `symbol`+`magic` ndani.

## 4. Cadence (ubongo — kila H1 bar mpya)
```
# 1) canonical update + 2) edge decide + ingest results (amri moja):
python src/research/live_brain.py --cycle --bridge-dir "<...>\MQL5\Files\bridge"
#   = ingest results.jsonl za EA -> paper_log  +  canonical -> edge -> commands.json
# (canonical feed yenyewe: python src/research/mt5_data.py ; au forward_cycle.py kwa hatua zote)
```
Task Scheduler (Windows): endesha `live_brain.py --cycle` kila saa (baada ya `mt5_data`). EA inapoll
commands.json kila `InpPollSeconds`. **Kill-switch:** `python src/research/live_brain.py --cancel-all`.

## 5. Schema (rejea)
- **commands.json** (ubongo->EA): `{seq, issued_utc, commands:[{cmd_id, action:PLACE_OCO|CANCEL_ALL,
  strategy, symbol, magic, lots, buy_stop, sell_stop, sl_buy, tp_buy, sl_sell, tp_sell, bar_ts, expiry_utc}]}`.
- **results.jsonl** (EA->ubongo, mstari mmoja/tukio): `{cmd_id, event:PLACED|FILLED|CANCELLED|EXPIRED|
  REJECTED|CLOSED, order_id, symbol, side?, price?, qty?, sl?, tp?, pnl?(CLOSED), exit_price?, ts, error?}`.
  EA **pekee** inaandika results; ubongo unasoma. FILLED->execution, CLOSED->settlement (decision_repository).

## 6. Kuona ikifanya kazi (BRIDGE-3 integration)
1. `live_brain.py --decide` -> `commands.json` inaonekana (angalia `seq`, `cmd_id`).
2. EA (demo) inapoll -> unaona **pending BuyStop/SellStop** kwenye terminal (Trade tab) + `results.jsonl`
   ina `PLACED`. Moja ikijaza -> nyingine inafutwa (OCO) + `FILLED`. Isiyojaza baada ya expiry -> `EXPIRED`.
   Position ikifunga (SL/TP) -> `CLOSED` (+pnl kutoka HistoryDeal).
3. `live_brain.py --ingest` -> `results.jsonl` -> `data/paper/paper_log.jsonl` (idempotent) -> `model_steward.py`
   -> dashboard `ingest` -> scorecard/FLEET zinaonyesha trades halisi za demo.
- Quick-check (bila MT5): weka `results.jsonl` bandia (FILLED+CLOSED) kwenye bridge -> `live_brain --ingest`
  -> paper_log inapata execution+settlement (repo-valid, linkage `settlement.id==execution.order_id`).

## 7. Usalama / mipaka
- **DEMO-only guard** kwenye `OnInit` — non-DEMO -> INIT_FAILED (hakuna njia ya kuipita). Live = Faza 4 + saini.
- EA **HAINA** nr7/ATR/decisions (IP §9). Idempotent kati ya restarts kwa `processed.txt` (cmd_id).
- **Limitation (BRIDGE-3 hardening):** hali ya OCO (g_oco) iko kwenye kumbukumbu — EA ikirestart kabla
  position kufunga, FILLED/CLOSED ya order za awali hazitaripotiwa (rebuild kutoka positions/comment =
  kazi ya baadaye). Expiry = UTC (`TimeGMT()`), broker-time-independent.
- `expiry_utc` = bar-close + 1h (entry window = bar 1). Orders = `ORDER_TIME_GTC` + EA-managed expiry.
