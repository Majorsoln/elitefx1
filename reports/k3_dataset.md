# M4-1 — DATASET ya KAIROS-3 (H1, bars ZOTE × dirs 2 × pairs 12, TRAIN PEKEE)

*2026-08-01 19:52 | charter: docs/CYCLE4_ML_CHARTER.md §6.2/§3/§4 · spec: docs/KAIROS_3_SPEC.md §3 | labels: `episodes` (golden, next-bar fill, tie→SL, gharama halisi) | entry = MARKET open ya bar i+1, slippage 0.1 pip | max_hold=24*

> **TRAIN PEKEE (2016-2022).** VALIDATION ni ya gate ya M4-2; HOLDOUT + sealed 2026-05+ hazipo kwenye njia hii (guard mbili: split-guard + assert ya `max(ts) < TRAIN_END`).

> **HAKUNA labeler mpya.** Labels za bars ZOTE zinatoka `episodes()` ile ile ya golden kupitia **residue-class scan** (stride = max_hold + 2 = 26) — non-overlap ya episodes hairuki bar hata moja kwa ujenzi. Self-test [2] inathibitisha parity dhidi ya episodes iliyoitwa bar-moja-moja.


## Ukubwa

- rows: **1,025,338** · pairs 12 · dirs 2 · geometries ['sl2tp1', 'sl1tp1'] (label sets, si rows tofauti)
- per-pair: `{'EURUSD': 85324, 'GBPUSD': 85330, 'USDJPY': 85356, 'EURJPY': 85352, 'USDCAD': 85328, 'USDCHF': 85344, 'AUDUSD': 85354, 'NZDUSD': 85360, 'EURGBP': 85346, 'GBPJPY': 87108, 'EURCHF': 87112, 'XAUUSD': 83024}`
- faili: `data\processed\k3/<pair>.parquet` + `k3_manifest.json` (**nje ya git** — data nzito; ripoti hii ndiyo rekodi)

## Manifest (mpaka rasmi — M4-2 ita-assert)

- **FEATURES** (28, zote za SIGNAL bar i — decidable): `vol_state, activity_state, spread_state, session_entry, hour, dow, atr_pips, atr_rel, range_atr, nr7_flag, h4_ema_slope, h4_linreg_slope, h4_trend_sign, h4_vol_state, h4_act_state, h4_dist_res_atr, h4_dist_sup_atr, h4_rsi14, h4_roc10, d1_ema_slope, d1_linreg_slope, d1_trend_sign, d1_vol_state, d1_act_state, d1_dist_res_atr, d1_dist_sup_atr, d1_rsi14, d1_roc10`
- **OUTCOMES** (8, KAMWE ndani ya X): `pnl_pips_sl2tp1, pnl_R_sl2tp1, win_sl2tp1, bars_held_sl2tp1, pnl_pips_sl1tp1, pnl_R_sl1tp1, win_sl1tp1, bars_held_sl1tp1`
- **META**: `pair, split, year, dir, ts_entry, ts_exit, signal_bar, fold`
- `load_k3()` ina-assert: hakuna outcome ndani ya X (leak #1).

## Label balance (bwawa ni heterogeneous? — spec §2)

| geometry | N | win-rate | EV_R (gross ya bwawa lote) |
|---|---|---|---|
| sl2tp1 (2.0/1.0) | 1,025,338 | 66.0% | -0.0470 |
| sl1tp1 (1.0/1.0) | 1,025,338 | 49.2% | -0.1019 |

*EV_R hapa ni ya **bwawa lote bila uteuzi** (kila bar, pande zote mbili) — inatarajiwa kuwa HASI (gharama kila bar). Kazi ya GBM ni kupata **subset** yenye EV chanya; kama bwawa lote lina EV hasi kubwa, threshold italazimika kuwa kali (§4.4 cost-aware).*

## Purged + embargoed CV (charter §4.2 — `purged_cv.py`)

- folds 5 za **MUDA** (mpaka mmoja kwa pairs zote — cross-pair leakage haiwezekani) · embargo = horizon ya juu ya label

| fold | n_train | n_test | n_dropped (purge+embargo) | drop% | test_start | test_end |
|---|---|---|---|---|---|---|
| 0 | 819,048 | 205,060 | 1,230 | 0.12% | 2016-01-03T23:00:00.000000 | 2017-05-25T19:00:00.000000 |
| 1 | 818,881 | 205,060 | 1,397 | 0.14% | 2017-05-25T20:00:00.000000 | 2018-10-18T16:00:00.000000 |
| 2 | 817,817 | 205,062 | 2,459 | 0.24% | 2018-10-18T17:00:00.000000 | 2020-03-16T07:00:00.000000 |
| 3 | 818,035 | 205,078 | 2,225 | 0.22% | 2020-03-16T08:00:00.000000 | 2021-08-10T05:00:00.000000 |
| 4 | 820,000 | 205,078 | 260 | 0.03% | 2021-08-10T06:00:00.000000 | 2022-12-30T21:00:00.000000 |

## Feature completeness (NaN% — pengo kubwa = haifundishwi)

| feature | NaN% |
|---|---|
| d1_linreg_slope | 1.1% |
| d1_dist_res_atr | 1.1% |
| d1_dist_sup_atr | 1.1% |
| d1_roc10 | 0.6% |
| d1_ema_slope | 0.2% |
| h4_linreg_slope | 0.2% |
| h4_dist_res_atr | 0.2% |
| h4_dist_sup_atr | 0.2% |
| atr_rel | 0.1% |
| h4_roc10 | 0.1% |
| h4_ema_slope | 0.0% |
| d1_trend_sign | 0.0% |
| d1_vol_state | 0.0% |
| d1_act_state | 0.0% |
| d1_rsi14 | 0.0% |
| h4_trend_sign | 0.0% |
| h4_vol_state | 0.0% |
| h4_act_state | 0.0% |
| h4_rsi14 | 0.0% |
| vol_state | 0.0% |
| activity_state | 0.0% |
| spread_state | 0.0% |
| session_entry | 0.0% |
| hour | 0.0% |
| dow | 0.0% |
| atr_pips | 0.0% |
| range_atr | 0.0% |
| nr7_flag | 0.0% |

## Caveats

1. **Dataset si edge.** Ni chakula cha M4-2 pekee; hakuna madai ya EV hapa.
2. **Gharama zimo ndani ya kila label** (spread ya bar ya entry + slippage, L-039). Bwawa lote lina EV hasi kwa ujenzi — hiyo ndiyo hoja ya threshold ya cost-aware.
3. **Overlap ya labels ni kubwa** (kila bar ina label yenye horizon hadi max_hold) — ndiyo maana purge+embargo ni LAZIMA, si mapambo. Bila hiyo, CV yoyote ni ya uongo.
4. **dirs 2 kwa kila bar:** long na short zinapimwa kwa uhuru; model itajifunza P(win | features, dir). Hii ni signal GENERATION (charter §2), si filtering ya nr7.
5. `nr7_flag` ipo ili M4-2 iweze kulinganisha ML dhidi ya breadth baseline **ndani ya dataset ile ile** (si kuchanganya vyanzo viwili).

*reuse-only: episodes/_mask_context-free path/_atr_rel/_extra_states/_ctx_feats/_sess ni imports. Profitable != Tradable Edge. Protect capital first.*