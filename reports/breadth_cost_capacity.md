# M4-0b — COST STRESS + CAPACITY ya BREADTH (nr7_break × pairs 12 × H1)

*2026-08-01 18:56 | nyongeza ya reports/breadth_baseline.md (M4-0) | splits: TRAIN + VALIDATION | reuse: cost_stress (R5) + config HALISI ya ftmo_config + semantiki za lango la live (live_brain/broker_adapter) | HOLDOUT + sealed 2026-05+ HAZIJAGUSWA*

> **Swali:** breadth ina EV_net +0.91 pips/trade (FX) — **inastahimili gharama kiasi gani, na risk-engine itaruhusu ngapi kati ya ~2,680/mwaka?** Hii ni hatua ya KABLA ya kupanua `pairs[]` live, si utafiti mpya.

> **Lango (config halisi):** max_slots = **7** · max_correlated_slots = **3** · groups: `{'USD_group': ['EURUSD', 'GBPUSD', 'AUDUSD', 'NZDUSD'], 'USD_strength': ['USDJPY', 'USDCAD', 'USDCHF'], 'EUR_group': ['EURUSD', 'EURJPY', 'EURGBP'], 'AUD_NZD_group': ['AUDUSD', 'NZDUSD']}`

> ⚠ **Mipaka ya sim:** CHECK 3 (slots) + CHECK 4 (correlation) PEKEE. daily_loss/total_dd/max_spread zinategemea P&L ya wakati halisi — hazipo hapa. Hii ni **kadirio la capacity**, si backtest ya akaunti.


## 1. COST STRESS — EV(Δspread) analytic (cost_stress §R5(1))

> `EV_new = EV − Δ` (spread inalipwa mara MOJA kwa trade). **breakeven Δ = EV yenyewe.**


### SL2/TP1 · TRAIN — pooled FX EV = **+1.02 pips**, breakeven Δspread = **1.02 pip**
| Δspread | +0.2 | +0.5 | +1.0 |
|---|---|---|---|
| EV_net (pips) | +0.82 | +0.52 | +0.02 |

### SL2/TP1 · VALIDATION — pooled FX EV = **+0.90 pips**, breakeven Δspread = **0.90 pip**
| Δspread | +0.2 | +0.5 | +1.0 |
|---|---|---|---|
| EV_net (pips) | +0.70 | +0.40 | -0.10 |

### SL1/TP1 · TRAIN — pooled FX EV = **+1.09 pips**, breakeven Δspread = **1.09 pip**
| Δspread | +0.2 | +0.5 | +1.0 |
|---|---|---|---|
| EV_net (pips) | +0.89 | +0.59 | +0.09 |

### SL1/TP1 · VALIDATION — pooled FX EV = **+0.91 pips**, breakeven Δspread = **0.91 pip**
| Δspread | +0.2 | +0.5 | +1.0 |
|---|---|---|---|
| EV_net (pips) | +0.71 | +0.41 | -0.09 |

**Per-pair breakeven Δspread (pips — kila pair kwa pip-scale yake):**

| variant | split | EURUSD | GBPUSD | USDJPY | EURJPY | USDCAD | USDCHF | AUDUSD | NZDUSD | EURGBP | GBPJPY | EURCHF | XAUUSD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SL2/TP1 | TRAIN | +2.06 | +1.72 | +1.35 | +1.51 | +1.83 | +0.36 | +1.77 | +0.21 | +0.20 | +0.96 | -0.22 | +29.42 |
| SL2/TP1 | VALIDATION | +2.16 | +2.67 | +4.56 | -1.55 | +0.28 | +3.07 | +0.82 | -0.15 | -0.87 | -0.39 | +0.47 | +32.81 |
| SL1/TP1 | TRAIN | +1.95 | +1.84 | +1.98 | +1.52 | +1.42 | +0.58 | +1.54 | +0.55 | +0.12 | +1.47 | -0.46 | +15.50 |
| SL1/TP1 | VALIDATION | +1.44 | +1.57 | +4.05 | -0.96 | +0.24 | +1.21 | +1.04 | -0.25 | -0.77 | +2.76 | +0.61 | +37.96 |

## 2. COST STRESS — spread_state ya bar ya ENTRY (cost_stress §R5(2))

> Je trades zinazoingia wakati spread ni **WIDE** ndizo zinazokula faida? (spread_state = column ya state parquet, rank-based, no-lookahead.)

| variant | split | state | N | EV_R | EV_pips (FX) | win% |
|---|---|---|---|---|---|---|
| SL2/TP1 | TRAIN | **NORMAL** | 15824 | +0.0325 | +1.06 | 71.6 |
| SL2/TP1 | TRAIN | **UNKNOWN** | 183 | +0.0107 | +1.01 | 69.4 |
| SL2/TP1 | TRAIN | **WIDE** | 3157 | +0.0131 | +0.82 | 70.4 |
| SL2/TP1 | VALIDATION | **NORMAL** | 4146 | +0.0414 | +1.09 | 72.7 |
| SL2/TP1 | VALIDATION | **WIDE** | 948 | -0.0048 | +0.05 | 70.0 |
| SL1/TP1 | TRAIN | **NORMAL** | 16751 | +0.0594 | +1.09 | 57.8 |
| SL1/TP1 | TRAIN | **UNKNOWN** | 195 | +0.0997 | +3.00 | 58.5 |
| SL1/TP1 | TRAIN | **WIDE** | 3370 | +0.0361 | +0.96 | 57.1 |
| SL1/TP1 | VALIDATION | **NORMAL** | 4357 | +0.0610 | +1.10 | 58.3 |
| SL1/TP1 | VALIDATION | **WIDE** | 998 | +0.0162 | +0.05 | 56.9 |

**Verdict ya WIDE (cost_stress):** {
"SL2/TP1/train": "hakuna WIDE-skip (EV_WIDE>=0 au hakuna WIDE trades)",
"SL2/TP1/validation": "WIDE-skip filter kwenye DEPLOYMENT policy (EV_WIDE<0) + forward-verify",
"SL1/TP1/train": "hakuna WIDE-skip (EV_WIDE>=0 au hakuna WIDE trades)",
"SL1/TP1/validation": "hakuna WIDE-skip (EV_WIDE>=0 au hakuna WIDE trades)"
}

## 3. CAPACITY — risk-engine kama lango (CHECK 3 + CHECK 4)

| scope | split | mode | N | accepted | rejected | reject% | slots | corr | EV_R acc | EV_R rej | trades/mwaka acc | conc max | conc mean | %muda at-cap |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SL2/TP1 | TRAIN | live | 19164 | 17798 | 1366 | 7.1% | 1281 | 85 | +0.0322 | -0.0115 | 2547.4 | 7 | 3.64 | 12.7% |
| SL2/TP1 | TRAIN | strict | 19164 | 17798 | 1366 | 7.1% | 1281 | 85 | +0.0322 | -0.0115 | 2547.4 | 7 | 3.64 | 12.7% |
| SL2/TP1 | VALIDATION | live | 5094 | 4856 | 238 | 4.7% | 218 | 20 | +0.0302 | +0.0862 | 2433.0 | 7 | 3.44 | 8.6% |
| SL2/TP1 | VALIDATION | strict | 5094 | 4856 | 238 | 4.7% | 218 | 20 | +0.0302 | +0.0862 | 2433.0 | 7 | 3.44 | 8.6% |
| SL1/TP1 | TRAIN | live | 20316 | 19329 | 987 | 4.9% | 918 | 69 | +0.0600 | -0.0235 | 2766.5 | 7 | 3.13 | 8.8% |
| SL1/TP1 | TRAIN | strict | 20316 | 19329 | 987 | 4.9% | 918 | 69 | +0.0600 | -0.0235 | 2766.5 | 7 | 3.13 | 8.8% |
| SL1/TP1 | VALIDATION | live | 5355 | 5197 | 158 | 2.9% | 142 | 16 | +0.0516 | +0.0860 | 2603.8 | 7 | 2.91 | 5.4% |
| SL1/TP1 | VALIDATION | strict | 5355 | 5197 | 158 | 2.9% | 142 | 16 | +0.0516 | +0.0860 | 2603.8 | 7 | 2.91 | 5.4% |
| **COMBINED (models 2)** | TRAIN | live | 39480 | 27212 | 12268 | 31.1% | 10247 | 2021 | +0.0668 | -0.0100 | 3894.8 | 7 | 4.70 | 33.6% |
| **COMBINED (models 2)** | TRAIN | strict | 39480 | 27140 | 12340 | 31.3% | 9910 | 2430 | +0.0658 | -0.0074 | 3884.5 | 7 | 4.68 | 32.6% |
| **COMBINED (models 2)** | VALIDATION | live | 10449 | 7666 | 2783 | 26.6% | 2214 | 569 | +0.0554 | +0.0087 | 3840.9 | 7 | 4.55 | 29.0% |
| **COMBINED (models 2)** | VALIDATION | strict | 10449 | 7620 | 2829 | 27.1% | 2142 | 687 | +0.0559 | +0.0082 | 3817.8 | 7 | 4.53 | 28.1% |

*`EV_R acc` vs `EV_R rej`: kama zilizokataliwa ni **bora** kuliko zilizopita, lango linakata faida (queueing bias) — hiyo ni gharama iliyofichwa ya breadth, si ya bure.*

## 4. SWALI LA WAZI kwa Chief/PD (halijarekebishwa hapa — ni observation)

Code ya live ina **asymmetry** kwenye correlation: `live_brain.decide` inaongeza reservation kwa kundi **MOJA** (`live_engine._corr_group` — la kwanza linalolingana), wakati CHECK 4 (`broker_adapter`) inakagua **makundi YOTE** ya pair. Matokeo: EURUSD iliyo wazi inaongeza `USD_group` pekee; `EUR_group` inabaki 0, kwa hiyo EURJPY inaweza kupita hata kama nia ilikuwa kuizuia. Safu **`live`** hapo juu = tabia ya sasa; safu **`strict`** = kila kundi linaongezeka. Tofauti kati yao = ukubwa wa athari.
**Sijabadilisha code ya live** — hilo ni uamuzi wa Chief/PD, si la runner ya utafiti.

## 5. Jinsi ya kusoma (uamuzi, si namba tu)

1. **Kama breakeven Δspread < ~1 pip:** breadth ni fragile kwa cost-regime. Chaguo: (a) WIDE-skip filter kwenye DEPLOYMENT policy (si backtest — inahitaji forward-verify); (b) pairs zenye breakeven kubwa pekee; (c) subiri forward evidence.
2. **Kama reject% ni kubwa:** `pairs[]` iliyopanuka HAIONGEZI trades kwa uwiano — slots ndizo kikwazo. Kupanua pairs kunaongeza **uteuzi** (nafasi bora zaidi kwa slot), si wingi.
3. **Kama EV_R ya zilizokataliwa > ya zilizopita:** lango linakata faida — hoja ya kupanga foleni kwa ubora (queue by EV/threshold) badala ya first-come-first-served. Hii ndiyo hasa kazi ya KAIROS-3 (§3: chuja bwawa pana).

*reuse-only: cost_stress/pool_streams/pair_stream(episodes)/ftmo_config ni imports. Baseline ≠ edge. Profitable != Tradable Edge. Protect capital first.*