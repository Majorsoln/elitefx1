# ELITEFX — LIVE PAPER ENGINE (Option A) — "AI INAYOENDESHA"

> Directive ya PD 2026-07-21: njia A — unganisha vipande vyote kuwa AI MOJA inayotrade (paper
> kwanza → FTMO). Doctrine V2 §4 (tabaka) + §8 (evergreen loop, steward, MT5). STRAT-001/002
> zinatrade BILA filter (K4 no-lift). MT5-ready kwa adapter pattern (haitrade live bila saini ya PD).

## LENGO
Pipeline MOJA inayoendesha forward (bar-by-bar), inayochukua signal → decision → size → compliance
→ paper-execution → **log ambayo Glass Box dashboard inaisoma.** Kila trade ina decision-trace
kamili (glass-box). Hii ni AI yenyewe ikitenda — si sim ya utafiti, ni mfumo hai (paper mode).

## MTIRIRIKO (kila bar mpya, per pair za portfolio)
```
1. STATE      : bar mpya -> state engine (vol/session/HTF context)     [ipo]
2. SIGNAL     : nr7_break (STRAT-001 USDCHF SL2/TP1; STRAT-002 USDJPY SL1/TP1; no-LATE)  [ipo]
3. DECISION   : decision_engine + decision_policy (SELECT/VETO per policy)  [ipo]
4. SIZE       : DailyRiskBudgetSizer (broker_adapter) — risk_$ = min(budget/slots, max_per_trade);
                qty = risk_$/(sl_pips x pip_value). FTMO daily/max-loss -> streak isivunje.  [ipo]
5. COMPLIANCE : integrity_gate + constraints (daily_loss, slots, correlated-slots, no-trade-window,
                max_spread). FAIL -> trade inakataliwa + rekodi ya sababu.  [ipo]
6. EXECUTE    : broker_adapter mode=paper -> execution_object -> paper_trader  [ipo]
7. LOG        : decision + trade + compliance + trace -> paper_log.jsonl (dashboard inaisoma)  [+wire]
8. MONITOR    : Glass Box ingest -> Live Actions + Compliance + Portfolio panels  [ipo]
```

## KAZI YA A (integration — vingi vipo, kinachohitajika ni WIRING + forward loop + honest log)
- **Runner mpya** `src/research/live_engine.py`: loop ya forward (kwenye data ya paper/forward
  window 2026-05+ au replay) inayounganisha hatua 1-7 kwa STRAT-001/002. HAKUNA look-ahead
  (bar-by-bar, decision kwa bar iliyofungwa; fill next-bar honest — harness ile ile).
- **Honest log schema** (paper_log.jsonl) inayolingana HASA na kile dashboard `ingest` (bila --demo)
  inatarajia: per-trade {strategy, pair, dir, entry/exit ts+px, R, sl/tp, size, spread, slippage,
  decision_trace[signal,policy,size,compliance,fill], compliance_checks[...]}.
- **FTMO config** (deterministic): max_daily_loss, max_total_dd, max_slots, max_correlated_slots,
  risk_per_trade, no_trade_window, max_spread (kutoka data_config). Streak-math ya K4 design §5
  kama input ya sizing sanity.
- **Mode discipline:** mode=paper PEKEE (broker_adapter Q1 — live = refuse-stub hadi PD signature).
  MT5 adapter = kazi ya baadaye (§8.3); A inaandika interface tayari kwa MT5 bila kubadilisha ubongo.

## NIDHAMU
- ZERO look-ahead (bar-by-bar decidable). Costs+slippage halisi. STRAT-001/002 configs HAZIBADILIKI.
- ZERO golden/statistic fns kuguswa (episodes/pvalue n.k.). Engine mpya = wiring ya modules zilizopo.
- Log ni append-only (audit). Dashboard ingest (bila --demo) inasoma log hii -> live actions halisi.
- Self-test: forward loop determinism; compliance-veto path (trade inakataliwa ika-log); sizer
  budget=0 -> qty=0; log schema inalingana na dashboard ingest; no-look-ahead trap.

## STEWARD HOOK (§8.2 — baadaye, si sasa)
Log + attestation zinazozalishwa na A ndizo malighafi ya MODEL STEWARD (kupima practical vs learned).
A inahakikisha kila trade ina "learned expectation" tag (backtest EV ya strategy) ili divergence
ipimike baadaye. Steward yenyewe = mzunguko ujao.

## MATOKEO
AI moja inayoendesha (paper) → dashboard inaonyesha live actions + compliance halisi → njia ya
forward-track ya STRAT-001/002 kuelekea FTMO. Ikithibitika forward, live-gating (PD signature) → MT5.
