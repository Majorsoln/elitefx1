# ELITEFX — CONDUIT BRIDGE — "MODEL INAAMUA, EA INATEKELEZA" (directive ya PD 2026-07-30; Doctrine §9)

> PD: "maamuzi model ndio zinaamua; EA inapokea points na actions inayopaswa kufanya kwa muda husika,
> wakati EA inatoa update data kupeleka kwenye Python ikafanyiwe mchakato kamili." Hii ndiyo §9 hasa:
> **model ndiyo inayotrade; EA = conduit (HAINA strategy logic)**. KAIROS.mq5 (EA-1, logic ndani) =
> chombo cha Strategy Tester/backtest cha PD PEKEE — SI njia ya live.

## USANIFU
```
[MT5]--(read-only copy_rates)-->[mt5_data: CANONICAL increment §8.3b]-->[UBONGO python]
UBONGO: state -> nr7 signal -> decision -> DailyRiskBudgetSizer -> integrity_gate compliance
     -> COMMANDS (points+actions+muda) --> commands.json --> [EA-CONDUIT inasoma]
EA-CONDUIT: inaweka/inafuta stop-orders + SL/TP + size HASA kama amri; expiry (valid-until);
     inaripoti FILLS/executions --> results.json --> [UBONGO ina-ingest -> log/dashboard/steward]
```
- **Transport:** faili za JSON kwenye MQL5\Files (bridge dir; env ELITEFX_BRIDGE_DIR). Atomic writes,
  sequence ids, idempotent (amri ina id — EA haitekelezi mara mbili).
- **Cadence:** kila H1 bar mpya iliyofungwa (Task Scheduler/daemon): canonical update -> ubongo edge
  decision -> commands. EA inapoll kila tick/timer.

## EDGE MODE (kipande kipya cha ubongo — reuse kila kitu)
Replay/forward ya sasa inashughulikia bars ZILIZOKAMILIKA (entry+exit zinajulikana). LIVE inahitaji
**uamuzi kwenye ukingo**: bar ya signal ikifungwa SASA -> nr7 check (bar ya mwisho iliyofungwa) ->
no-LATE (entry bar = inayofuata) -> ATR/SL/TP/size/compliance -> amri ya stop-orders (OCO) yenye
expiry ya bar 1. REUSE: nr7_break, wilder_atr/_sess semantics, DailyRiskBudgetSizer, integrity_gate.
HAKUNA fill-simulation (fills halisi zinatoka EA/results). STRAT configs HAZIBADILIKI.

## SCHEMA
- **commands.json** (ubongo->EA): {seq, issued_utc, commands:[{cmd_id, action: PLACE_OCO|CANCEL,
  symbol, buy_stop, sell_stop, sl_buy, tp_buy, sl_sell, tp_sell, lots, expiry_utc, magic, strategy}]}
- **results.json** (EA->ubongo): append per event {cmd_id, event: PLACED|FILLED|CANCELLED|EXPIRED|
  REJECTED|CLOSED, order_id, price, ts, error?}. Ubongo ina-ingest -> decision_repository log
  (execution/settlement REAL — si paper-sim) -> dashboard/steward.

## USALAMA / NIDHAMU
- **DEMO PEKEE sasa** (§3.1b Faza): EA-conduit inakataa live account (account-mode check) hadi PD
  SIGNATURE (Faza 4). Hakuna saini inayohitajika kwa demo.
- EA HAINA logic ya strategy (IP §9): haina nr7/ATR/decisions — inatekeleza amri tu. Ndiyo EA
  itakayokodishwa (lessee anapata conduit tupu).
- Ubongo: sealed/holdout guards zinabaki; risk/compliance HALAZIMISHWI na EA — zimeamuliwa na ubongo.
- Kill-switch: commands.json yenye action=CANCEL_ALL; EA pia ina input ya kusimama.

## AWAMU
1. **BRIDGE-1 (Python, inajaribika bila MT5):** live_brain edge-mode + commands writer + results
   ingester (-> decision_repository/log). Self-tests kwa faili bandia.
2. **BRIDGE-2 (MQL5):** KAIROS_CONDUIT.mq5 — poll commands, execute, report results. Demo-only guard.
3. **BRIDGE-3 (integration):** PC ya PD — demo end-to-end: ubongo unaamua, unaona trades kwenye
   terminal (demo), dashboard inaonyesha. -> VPS -> (baadaye) sealed-window acceptance + live (saini).

## EA-2 (parity ya KAIROS.mq5) — HADHI
Imeahirishwa: KAIROS.mq5 = tester-tool tu sasa; live haitumii logic yake (ubongo=Python — hakuna
port-parity inayohitajika kwa live). Swali la GHARAMA (tester loss PF 0.72) linabaki WAZI na
LITAJIBIWA na demo-forward halisi ya conduit (fills halisi za demo, wiki chache). Parity ya tester
itafufuliwa TU kama tutataka kutumia namba za Strategy Tester kama ushahidi.
