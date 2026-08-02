# M4-0b — COST STRESS + CAPACITY ya BREADTH (nr7_break × H1) — **pairs[] zilizopendekezwa (M4-0)**

*2026-08-01 19:19 | nyongeza ya reports/breadth_baseline.md (M4-0) | splits: TRAIN + VALIDATION | reuse: cost_stress (R5) + config HALISI ya ftmo_config + semantiki za lango la live (live_brain/broker_adapter) | HOLDOUT + sealed 2026-05+ HAZIJAGUSWA*

> **Swali:** breadth ina EV_net +0.91 pips/trade (FX) — **inastahimili gharama kiasi gani, na risk-engine itaruhusu ngapi kati ya ~2,680/mwaka?** Hii ni hatua ya KABLA ya kupanua `pairs[]` live, si utafiti mpya.

> **Lango (config halisi):** max_slots = **7** · max_correlated_slots = **3** · groups: `{'USD_group': ['EURUSD', 'GBPUSD', 'AUDUSD', 'NZDUSD'], 'USD_strength': ['USDJPY', 'USDCAD', 'USDCHF'], 'EUR_group': ['EURUSD', 'EURJPY', 'EURGBP'], 'AUD_NZD_group': ['AUDUSD', 'NZDUSD']}`

> ⚠ **Mipaka ya sim:** CHECK 3 (slots) + CHECK 4 (correlation) PEKEE. daily_loss/total_dd/max_spread zinategemea P&L ya wakati halisi — hazipo hapa. Hii ni **kadirio la capacity**, si backtest ya akaunti.

> **Scenario ya deployment:** kila model inatumia `pairs[]` ILIYOPENDEKEZWA na M4-0 (kanuni ile ile — hakuna uchaguzi mpya):
>   · **SL2/TP1** (9): `AUDUSD, EURUSD, GBPJPY, GBPUSD, NZDUSD, USDCAD, USDCHF, USDJPY, XAUUSD`
>   · **SL1/TP1** (8): `AUDUSD, EURUSD, GBPJPY, GBPUSD, USDCAD, USDCHF, USDJPY, XAUUSD`


## 1. COST STRESS — EV(Δspread) analytic (cost_stress §R5(1))

> `EV_new = EV − Δ` (spread inalipwa mara MOJA kwa trade). **breakeven Δ = EV yenyewe.**


### SL2/TP1 · TRAIN — pooled FX EV = **+1.25 pips**, breakeven Δspread = **1.25 pip**
| Δspread | +0.2 | +0.5 | +1.0 |
|---|---|---|---|
| EV_net (pips) | +1.05 | +0.75 | +0.25 |

### SL2/TP1 · VALIDATION — pooled FX EV = **+1.58 pips**, breakeven Δspread = **1.58 pip**
| Δspread | +0.2 | +0.5 | +1.0 |
|---|---|---|---|
| EV_net (pips) | +1.38 | +1.08 | +0.58 |

### SL1/TP1 · TRAIN — pooled FX EV = **+1.53 pips**, breakeven Δspread = **1.53 pip**
| Δspread | +0.2 | +0.5 | +1.0 |
|---|---|---|---|
| EV_net (pips) | +1.33 | +1.03 | +0.53 |

### SL1/TP1 · VALIDATION — pooled FX EV = **+1.78 pips**, breakeven Δspread = **1.78 pip**
| Δspread | +0.2 | +0.5 | +1.0 |
|---|---|---|---|
| EV_net (pips) | +1.58 | +1.28 | +0.78 |

**Per-pair breakeven Δspread (pips — kila pair kwa pip-scale yake):**

| variant | split | AUDUSD | EURUSD | GBPJPY | GBPUSD | NZDUSD | USDCAD | USDCHF | USDJPY | XAUUSD |
|---|---|---|---|---|---|---|---|---|---|---|
| SL2/TP1 | TRAIN | +1.77 | +2.06 | +0.96 | +1.72 | +0.21 | +1.83 | +0.36 | +1.35 | +29.42 |
| SL2/TP1 | VALIDATION | +0.82 | +2.16 | -0.39 | +2.67 | -0.15 | +0.28 | +3.07 | +4.56 | +32.81 |
| SL1/TP1 | TRAIN | +1.54 | +1.95 | +1.47 | +1.84 | +1.42 | +0.58 | +1.98 | +15.50 |
| SL1/TP1 | VALIDATION | +1.04 | +1.44 | +2.76 | +1.57 | +0.24 | +1.21 | +4.05 | +37.96 |

## 2. COST STRESS — spread_state ya bar ya ENTRY (cost_stress §R5(2))

> Je trades zinazoingia wakati spread ni **WIDE** ndizo zinazokula faida? (spread_state = column ya state parquet, rank-based, no-lookahead.)

| variant | split | state | N | EV_R | EV_pips (FX) | win% |
|---|---|---|---|---|---|---|
| SL2/TP1 | TRAIN | **NORMAL** | 11557 | +0.0407 | +1.25 | 72.0 |
| SL2/TP1 | TRAIN | **UNKNOWN** | 138 | +0.0499 | +2.80 | 71.7 |
| SL2/TP1 | TRAIN | **WIDE** | 2313 | +0.0263 | +1.16 | 71.2 |
| SL2/TP1 | VALIDATION | **NORMAL** | 2947 | +0.0636 | +1.75 | 73.8 |
| SL2/TP1 | VALIDATION | **WIDE** | 683 | +0.0079 | +0.79 | 70.7 |
| SL1/TP1 | TRAIN | **NORMAL** | 10758 | +0.0862 | +1.53 | 58.6 |
| SL1/TP1 | TRAIN | **UNKNOWN** | 126 | +0.2132 | +5.93 | 63.5 |
| SL1/TP1 | TRAIN | **WIDE** | 2157 | +0.0459 | +1.26 | 57.0 |
| SL1/TP1 | VALIDATION | **NORMAL** | 2690 | +0.1080 | +2.03 | 59.8 |
| SL1/TP1 | VALIDATION | **WIDE** | 630 | +0.0505 | +0.68 | 57.5 |

**Verdict ya WIDE (cost_stress):** {
"SL2/TP1/train": "hakuna WIDE-skip (EV_WIDE>=0 au hakuna WIDE trades)",
"SL2/TP1/validation": "hakuna WIDE-skip (EV_WIDE>=0 au hakuna WIDE trades)",
"SL1/TP1/train": "hakuna WIDE-skip (EV_WIDE>=0 au hakuna WIDE trades)",
"SL1/TP1/validation": "hakuna WIDE-skip (EV_WIDE>=0 au hakuna WIDE trades)"
}

## 3. CAPACITY — risk-engine kama lango (CHECK 3 + CHECK 4)

| scope | split | mode | N | accepted | rejected | reject% | slots | corr | EV_R acc | EV_R rej | trades/mwaka acc | conc max | conc mean | %muda at-cap |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SL2/TP1 | TRAIN | live | 14008 | 13706 | 302 | 2.2% | 121 | 181 | +0.0399 | -0.0284 | 1961.9 | 7 | 2.94 | 3.1% |
| SL2/TP1 | TRAIN | strict | 14008 | 13706 | 302 | 2.2% | 121 | 181 | +0.0399 | -0.0284 | 1961.9 | 7 | 2.94 | 3.1% |
| SL2/TP1 | VALIDATION | live | 3630 | 3573 | 57 | 1.6% | 20 | 37 | +0.0507 | +0.2028 | 1790.5 | 7 | 2.72 | 1.9% |
| SL2/TP1 | VALIDATION | strict | 3630 | 3573 | 57 | 1.6% | 20 | 37 | +0.0507 | +0.2028 | 1790.5 | 7 | 2.72 | 1.9% |
| SL1/TP1 | TRAIN | live | 13041 | 13007 | 34 | 0.3% | 34 | 0 | +0.0809 | +0.0108 | 1861.8 | 7 | 2.38 | 1.4% |
| SL1/TP1 | TRAIN | strict | 13041 | 13007 | 34 | 0.3% | 34 | 0 | +0.0809 | +0.0108 | 1861.8 | 7 | 2.38 | 1.4% |
| SL1/TP1 | VALIDATION | live | 3320 | 3318 | 2 | 0.1% | 2 | 0 | +0.0972 | -0.0875 | 1662.7 | 7 | 2.19 | 0.8% |
| SL1/TP1 | VALIDATION | strict | 3320 | 3318 | 2 | 0.1% | 2 | 0 | +0.0972 | -0.0875 | 1662.7 | 7 | 2.19 | 0.8% |
| **COMBINED (models 2)** | TRAIN | live | 27049 | 21401 | 5648 | 20.9% | 2846 | 2802 | +0.0752 | -0.0032 | 3063.4 | 7 | 3.93 | 15.7% |
| **COMBINED (models 2)** | TRAIN | strict | 27049 | 21401 | 5648 | 20.9% | 2846 | 2802 | +0.0752 | -0.0032 | 3063.4 | 7 | 3.93 | 15.7% |
| **COMBINED (models 2)** | VALIDATION | live | 6950 | 5782 | 1168 | 16.8% | 522 | 646 | +0.0757 | +0.0663 | 2897.4 | 7 | 3.71 | 11.8% |
| **COMBINED (models 2)** | VALIDATION | strict | 6950 | 5782 | 1168 | 16.8% | 522 | 646 | +0.0757 | +0.0663 | 2897.4 | 7 | 3.71 | 11.8% |

*`EV_R acc` vs `EV_R rej`: kama zilizokataliwa ni **bora** kuliko zilizopita, lango linakata faida (queueing bias) — hiyo ni gharama iliyofichwa ya breadth, si ya bure.*

## 4. SWALI LA WAZI kwa Chief/PD (halijarekebishwa hapa — ni observation)

Code ya live ina **asymmetry** kwenye correlation: `live_brain.decide` inaongeza reservation kwa kundi **MOJA** (`live_engine._corr_group` — la kwanza linalolingana), wakati CHECK 4 (`broker_adapter`) inakagua **makundi YOTE** ya pair. Matokeo: EURUSD iliyo wazi inaongeza `USD_group` pekee; `EUR_group` inabaki 0, kwa hiyo EURJPY inaweza kupita hata kama nia ilikuwa kuizuia. Safu **`live`** hapo juu = tabia ya sasa; safu **`strict`** = kila kundi linaongezeka. Tofauti kati yao = ukubwa wa athari.
**Sijabadilisha code ya live** — hilo ni uamuzi wa Chief/PD, si la runner ya utafiti.

## 5. Jinsi ya kusoma (uamuzi, si namba tu)

1. **Kama breakeven Δspread < ~1 pip:** breadth ni fragile kwa cost-regime. Chaguo: (a) WIDE-skip filter kwenye DEPLOYMENT policy (si backtest — inahitaji forward-verify); (b) pairs zenye breakeven kubwa pekee; (c) subiri forward evidence.
2. **Kama reject% ni kubwa:** `pairs[]` iliyopanuka HAIONGEZI trades kwa uwiano — slots ndizo kikwazo. Kupanua pairs kunaongeza **uteuzi** (nafasi bora zaidi kwa slot), si wingi.
3. **Kama EV_R ya zilizokataliwa > ya zilizopita:** lango linakata faida — hoja ya kupanga foleni kwa ubora (queue by EV/threshold) badala ya first-come-first-served. Hii ndiyo hasa kazi ya KAIROS-3 (§3: chuja bwawa pana).

*reuse-only: cost_stress/pool_streams/pair_stream(episodes)/ftmo_config ni imports. Baseline ≠ edge. Profitable != Tradable Edge. Protect capital first.*