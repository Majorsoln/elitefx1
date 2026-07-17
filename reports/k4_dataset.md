# K4 TRAINING DATASET — entry-quality (nr7 STRAT-001/002; TRAIN+VALID)

*rows=4,222 | strategies=STRAT-001(USDCHF SL2/TP1) + STRAT-002(USDJPY SL1/TP1) | nr7_break no-LATE H1 | features=signal-bar (decidable) | HOLDOUT HAIGUSWI (2025+ sealed)*

> **Curriculum note (charter §M3-QA):** dataset hii ni malighafi ya K4 — LAZIMA ithibitishwe (label integrity, no-leakage, class balance, N per regime, mwaka-coverage) na SCIENTIST-D KABLA ya M3-5 training. Outcomes = honest harness (costs ndani); features = signal-bar tu.


## Counts + baseline (win rate = p(pnl>0), class balance)

| strategy | split | N | wins | win_rate | EV_pips | EV_R |
|----------|-------|---|------|----------|--------|------|
| STRAT-001 | train | 1,607 | 1,143 | 0.711 | +0.357 | +0.006 |
| STRAT-001 | validation | 425 | 337 | 0.793 | +3.068 | +0.135 |
| STRAT-002 | train | 1,746 | 1,030 | 0.590 | +1.977 | +0.132 |
| STRAT-002 | validation | 444 | 269 | 0.606 | +4.051 | +0.164 |

## Exit-type distribution (TP / SL / timeout)

| strategy | split | TP | SL | timeout |
|----------|-------|----|----|---------|
| STRAT-001 | train | 1133 | 451 | 23 |
| STRAT-001 | validation | 337 | 85 | 3 |
| STRAT-002 | train | 1030 | 715 | 1 |
| STRAT-002 | validation | 268 | 175 | 1 |

## Feature completeness (NaN% — feature yenye pengo kubwa haifundishwi, §M3-QA)

| feature | NaN% |
|---------|------|
| year | 0.0 |
| dir | 0.0 |
| hour | 0.0 |
| dow | 0.0 |
| atr_pips | 0.0 |
| atr_n | 100.0 |
| range_nr7_atr | 0.0 |
| pnl_pips | 0.0 |
| pnl_R | 0.0 |
| win | 0.0 |
| bars_held | 0.0 |
| mfe_r | 0.0 |
| mae_r | 0.0 |
| mfe_peak_bar | 0.0 |
| d1_act_state | 0.0 |
| d1_dist_res_atr | 0.9 |
| d1_dist_sup_atr | 0.9 |
| d1_ema_slope | 0.2 |
| d1_linreg_slope | 0.9 |
| d1_roc10 | 0.6 |
| d1_rsi14 | 0.0 |
| d1_trend_sign | 0.0 |
| d1_vol_state | 0.0 |
| h4_act_state | 0.0 |
| h4_dist_res_atr | 0.2 |
| h4_dist_sup_atr | 0.2 |
| h4_ema_slope | 0.0 |
| h4_linreg_slope | 0.2 |
| h4_roc10 | 0.1 |
| h4_rsi14 | 0.0 |
| h4_trend_sign | 0.0 |
| h4_vol_state | 0.0 |

*data/strategies/k4_dataset.parquet — 1 row kwa trade (signal-bar features + outcome). Next (M3-5): SCIENTIST-D design model interpretable (p(win|state)) baada ya certification.*