# K4 TRAINING DATASET — entry-quality (nr7 STRAT-001/002; TRAIN+VALID)

*rows=4,222 | strategies=STRAT-001(USDCHF SL2/TP1) + STRAT-002(USDJPY SL1/TP1) | nr7_break no-LATE H1 | features=signal-bar (decidable) | HOLDOUT HAIGUSWI (2025+ sealed)*

> **Curriculum note (charter §M3-QA):** dataset hii ni malighafi ya K4 — LAZIMA ithibitishwe (label integrity, no-leakage, class balance, N per regime, mwaka-coverage) na SCIENTIST-D KABLA ya M3-5 training. Outcomes = honest harness (costs ndani); features = signal-bar tu.


## Manifest (K-2): FEATURES (decidable, signal-bar) vs OUTCOMES vs META

- **FEATURES** (27): `vol_state, activity_state, spread_state, session_entry, hour, dow, atr_pips, atr_rel, range_nr7_atr, h4_ema_slope, h4_linreg_slope, h4_trend_sign, h4_vol_state, h4_act_state, h4_dist_res_atr, h4_dist_sup_atr, h4_rsi14, h4_roc10, d1_ema_slope, d1_linreg_slope, d1_trend_sign, d1_vol_state, d1_act_state, d1_dist_res_atr, d1_dist_sup_atr, d1_rsi14, d1_roc10`
- **OUTCOMES** (8, KAMWE si feature): `pnl_pips, pnl_R, win, exit_type, bars_held, mfe_r, mae_r, mfe_peak_bar`
- **META** (identifiers, si feature — `year`/`dir` = year-proxy §D5): `strategy, split, pair, year, dir, ts_entry, entry_bar`
- Trainer ya M3-5 itumie `k4_dataset.load_k4(features_only=True)` -> (X,y) yenye ASSERT kwamba hakuna OUTCOMES ndani ya X (trap ya leak #1 — mfe_r/pnl_* kama feature).

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

## Feature completeness (NaN% — FEATURES za manifest; pengo kubwa = haifundishwi)

| feature | NaN% |
|---------|------|
| vol_state | 0.0 |
| activity_state | 0.0 |
| spread_state | 0.0 |
| session_entry | 0.0 |
| hour | 0.0 |
| dow | 0.0 |
| atr_pips | 0.0 |
| atr_rel | 0.2 |
| range_nr7_atr | 0.0 |
| h4_ema_slope | 0.0 |
| h4_linreg_slope | 0.2 |
| h4_trend_sign | 0.0 |
| h4_vol_state | 0.0 |
| h4_act_state | 0.0 |
| h4_dist_res_atr | 0.2 |
| h4_dist_sup_atr | 0.2 |
| h4_rsi14 | 0.0 |
| h4_roc10 | 0.1 |
| d1_ema_slope | 0.2 |
| d1_linreg_slope | 0.9 |
| d1_trend_sign | 0.0 |
| d1_vol_state | 0.0 |
| d1_act_state | 0.0 |
| d1_dist_res_atr | 0.9 |
| d1_dist_sup_atr | 0.9 |
| d1_rsi14 | 0.0 |
| d1_roc10 | 0.6 |

## Cells 'hazifundishiki bado' (N<30 per strategy×regime — §Q6, QUARANTINE)

*Model isijifunze kelele ya cell tupu. Regime = (vol_state, activity_state, spread_state).*

| strategy | vol_state | activity_state | spread_state | N |
|----------|-----------|----------------|--------------|---|
| STRAT-001 | LOW | HIGH | WIDE | 10 |
| STRAT-001 | LOW | NORMAL | WIDE | 24 |
| STRAT-001 | UNKNOWN | UNKNOWN | UNKNOWN | 19 |
| STRAT-001 | UNKNOWN | UNKNOWN | WIDE | 9 |
| STRAT-002 | HIGH | LOW | WIDE | 25 |
| STRAT-002 | LOW | HIGH | NORMAL | 29 |
| STRAT-002 | LOW | HIGH | WIDE | 5 |
| STRAT-002 | LOW | NORMAL | WIDE | 23 |
| STRAT-002 | NORMAL | HIGH | WIDE | 14 |
| STRAT-002 | UNKNOWN | UNKNOWN | UNKNOWN | 14 |
| STRAT-002 | UNKNOWN | UNKNOWN | WIDE | 13 |

## Tahadhari za mafunzo (ndani ya kitabu — §D1/§C5 audit)

- **VALID selection-taint (§D1):** STRAT-001/002 ZILICHAGULIWA kwa VALIDATION 2023-24 (order statistics — STRAT-001 1/1,939 wa FDR). Win ya VALID (79.3%/60.6%) ime-overstate vs holdout halisi (73.9%/57.8%). NIDHAMU M3-5: model selection = blocked-CV ndani ya TRAIN PEKEE; VALID = check MOJA bila tuning; lift ya VALID tarajia ~0.35-0.5x mbele (shrinkage).
- **Server-time/DST (§C5):** `hour` ni server-time; DST inahamisha London/NY ±1h kwa wiki kadhaa kwa mwaka -> hour-level features zina jitter; `session_entry` ni imara zaidi.
- **Non-stationarity (§D5):** `atr_pips` ni ABSOLUTE level (year-proxy risk) — `atr_rel` (relative, rolling-median 60 PAST bars) imeongezwa kama mbadala deseasonalized (K-3).

*data/strategies/k4_dataset.parquet — 1 row kwa trade (META + FEATURES + OUTCOMES). Time-aware CV: tumia `ts_entry`/`entry_bar` (K-1) + blocked folds (purge bars 24, §D3). Next (M3-5): SCIENTIST-D design model interpretable (p(win|state)) baada ya certification.*