# M4-0 — BREADTH BASELINE (nr7_break × pairs 12 × D1, POOLED)

*2026-08-01 22:26 | charter: docs/CYCLE4_ML_CHARTER.md §1B/§5 · spec: docs/KAIROS_3_SPEC.md §5.3 | splits: TRAIN 2016-2022 + VALIDATION 2023-2024 | filter: None, vol=None, max_hold=20 | swap: IMETUMIKA (config swap_pips_per_night, rmap.apply_swap) | costs: spread halisi ya bar ya entry + slippage (L-039) | engine RASMI: pvalue_boot mean_block=3, seed=hash(registration)*

> **HII SI EDGE CLAIM MPYA.** Logic ni ILE ILE iliyothibitika (`nr7_break` × H1 × no-LATE = STRAT-001/002), imeenezwa tu kutoka pairs 2 → pairs 12 (chanzo (B) cha nafasi, charter §1B). Kusudi ni **kipimo**: namba ambayo KAIROS-3 (na HATUA 1-3 zote za ML) **LAZIMA izidi**.

> **HOLDOUT (2025-01→2026-04) HAIJAGUSWA** na dirisha **SEALED 2026-05+** (Doctrine §3.1b) haliingii — runner ina-refuse split yoyote isiyokuwa train/validation KABLA ya kusoma data.

> **POOLED ndiyo hukumu (LESSON-041).** Per-pair = diagnostics TU; hakuna best-pair selection popote kwenye faili hii.


## BASELINE LINE (bar ya KAIROS-3)

> ### KAIROS-3 LAZIMA izidi: **EV_net = +19.98 pips/trade** (pooled FX, N=407, bila XAUUSD), **trades/mwaka = 211.4** (VALIDATION).
>
> Currency ya hukumu (L-041) = **EV_R = +0.1856** (R-units, pooled pairs 12). Pips: **+29.75** (pairs zote, pip-scale ya XAUUSD ndani) · **+19.98** (FX pekee, N=407 — ndiyo inayolinganishwa na KAIROS-1 +1.92 / KAIROS-2 +2.65).
>
> N (VALID) = **422** · p_boot = 0.0005 · variant = **SL1/TP1** (variant yenye nguvu zaidi VALIDATION kati ya mbili — bar ya JUU = conservative kwa challenger; zote: SL2/TP1 EV_R=+0.0657 · SL1/TP1 EV_R=+0.1856).
>
> Kwa spec §5.2 ya KAIROS-3 (EV_net ≥ 3.0 pips NA ≥ 3× gharama): bar halisi ya kupita = **max(3.0, +19.98)** pips/trade, NA trades/mwaka ≥ 211.4 (breadth haipaswi kupungua).

## Pooled (HUKUMU — L-041) kwa kila exit-variant

| variant | split | pairs | N | EV_R | CI90 (R) | EV_pips (12) | EV_pips (FX) | trades/mwaka | win% | PF | p_boot | p_z | B_eff |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SL2/TP1 | TRAIN | 12 | 1301 | +0.0823 | [+0.0520, +0.1126] | +62.46 | +12.32 | 186.2 | 73.0 | 1.31 | 0.0001 | 3e-06 | 10000 |
| SL2/TP1 | VALIDATION | 12 | 383 | +0.0657 | [+0.0080, +0.1208] | -1.29 | +16.78 | 191.9 | 72.1 | 1.24 | 0.033797 | 0.026234 | 10000 |
| SL1/TP1 | TRAIN | 12 | 1465 | +0.1885 | [+0.1460, +0.2300] | +49.75 | +14.89 | 209.7 | 61.4 | 1.47 | 0.0001 | 0.0 | 10000 |
| SL1/TP1 | VALIDATION | 12 | 422 | +0.1856 | [+0.1072, +0.2591] | +29.75 | +19.98 | 211.4 | 61.6 | 1.46 | 0.0005 | 4.8e-05 | 10000 |

*Pairs bila dirisha (hazikuingia pooling): hakuna. p_boot ni **descriptive** hapa (baseline, si test iliyosajiliwa) — TRAIN/VALIDATION zimeshatumika na utafiti wa nr7; hakuna dirisha jipya lililochomwa.*

## Per-pair (DIAGNOSTICS TU — ⚠ SI selection)

> ⚠ **TAHADHARI (LESSON-041):** namba hizi HAZITUMIKI kuchagua pair 'bora'. Kuchagua pair yenye EV kubwa zaidi ya TRAIN ni max-selection bias — ilipinduka hasi OOS 3/3. Zinaonyeshwa kwa uwazi wa accounting (jumla ya N zao = N ya pooled) na kwa kanuni ya `pairs[]` hapa chini, ambayo ni **sheria ya sign+N, si ranking**.


### SL2/TP1

| pair | N (train) | EV_R (train) | EV_pips (train) | N (valid) | EV_R (valid) | EV_pips (valid) | trades/mwaka (valid) |
|---|---|---|---|---|---|---|---|
| AUDUSD | 121 | +0.1257 | +17.30 | 35 | +0.1272 | +11.44 | 17.5 |
| EURCHF | 72 | +0.1313 | +12.59 | 30 | +0.1745 | +18.12 | 15.0 |
| EURGBP | 125 | +0.0840 | +13.57 | 36 | +0.1380 | +8.68 | 18.0 |
| EURJPY | 127 | +0.0705 | +18.20 | 39 | +0.1377 | +44.09 | 19.5 |
| EURUSD | 127 | -0.0277 | -4.84 | 39 | -0.0499 | -8.07 | 19.5 |
| GBPJPY | 70 | +0.1615 | +45.82 | 17 | +0.4865 | +160.53 | 8.5 |
| GBPUSD | 115 | +0.0783 | +15.21 | 33 | +0.0308 | +4.59 | 16.5 |
| NZDUSD | 123 | +0.0367 | +2.84 | 34 | -0.3127 | -38.43 | 17.0 |
| USDCAD | 114 | +0.0935 | +17.75 | 35 | +0.2034 | +24.69 | 17.5 |
| USDCHF | 125 | +0.0046 | +1.26 | 33 | -0.0746 | -11.17 | 16.5 |
| USDJPY | 123 | +0.0990 | +11.60 | 38 | +0.1153 | +38.48 | 19.0 |
| XAUUSD | 59 | +0.3092 | +1117.89 | 14 | -0.0438 | -477.74 | 7.0 |

### SL1/TP1

| pair | N (train) | EV_R (train) | EV_pips (train) | N (valid) | EV_R (valid) | EV_pips (valid) | trades/mwaka (valid) |
|---|---|---|---|---|---|---|---|
| AUDUSD | 135 | +0.2733 | +18.64 | 37 | +0.3052 | +17.47 | 18.5 |
| EURCHF | 76 | +0.2781 | +12.59 | 30 | +0.5208 | +25.22 | 15.0 |
| EURGBP | 145 | +0.1990 | +14.02 | 41 | -0.0220 | -2.22 | 20.5 |
| EURJPY | 149 | +0.2013 | +20.59 | 41 | +0.3004 | +47.13 | 20.5 |
| EURUSD | 153 | +0.1065 | +6.60 | 48 | +0.0572 | +3.85 | 24.1 |
| GBPJPY | 74 | +0.4060 | +50.84 | 17 | +0.7404 | +117.50 | 8.5 |
| GBPUSD | 127 | +0.2118 | +23.77 | 38 | +0.0982 | +9.04 | 19.0 |
| NZDUSD | 142 | +0.1480 | +9.20 | 41 | -0.2274 | -14.17 | 20.5 |
| USDCAD | 130 | +0.1685 | +17.19 | 35 | +0.4137 | +26.65 | 17.5 |
| USDCHF | 136 | +0.0525 | +4.71 | 35 | +0.0294 | +1.07 | 17.5 |
| USDJPY | 139 | +0.0606 | +2.79 | 44 | +0.2724 | +44.85 | 22.1 |
| XAUUSD | 59 | +0.4668 | +880.51 | 15 | +0.1841 | +294.81 | 7.5 |

## PENDEKEZO la `pairs[]` kwa `config/models.yaml` (KAIROS-1/2 multi-pair)

> **KANUNI (pre-registered, SI ranking):** pair inapendekezwa IKIWA **EV_R > 0 kwenye TRAIN** NA **EV_R > 0 kwenye VALIDATION** NA **N_valid ≥ 30**.
> **HAKUNA "top-N kwa EV"** (= max-selection bias, LESSON-041). Orodha ni ya **alfabeti**, si ya EV — hata mpangilio usipendekeze ranking.
> Hili ni **PENDEKEZO la utafiti. PD ndiye anayehariri `config/models.yaml`** — code haiandiki registry.


### SL2/TP1

**(a) Zilizopita kanuni:**

| pair | EV_R train | EV_R valid | N valid | EV_pips valid |
|---|---|---|---|---|
| AUDUSD | +0.1257 | +0.1272 | 35 | +11.44 |
| EURCHF | +0.1313 | +0.1745 | 30 | +18.12 |
| EURGBP | +0.0840 | +0.1380 | 36 | +8.68 |
| EURJPY | +0.0705 | +0.1377 | 39 | +44.09 |
| GBPUSD | +0.0783 | +0.0308 | 33 | +4.59 |
| USDCAD | +0.0935 | +0.2034 | 35 | +24.69 |
| USDJPY | +0.0990 | +0.1153 | 38 | +38.48 |

```yaml
    pairs:      [AUDUSD, EURCHF, EURGBP, EURJPY, GBPUSD, USDCAD, USDJPY]   # M4-0 rule: EV_R>0 train NA valid NA N_valid>=30
```

**(b) Zilizokataliwa + sababu:**

| pair | EV_R train | EV_R valid | N valid | sababu |
|---|---|---|---|---|
| EURUSD | -0.0277 | -0.0499 | 39 | EV_R TRAIN -0.0277 <= 0; EV_R VALID -0.0499 <= 0 |
| GBPJPY | +0.1615 | +0.4865 | 17 | N_valid 17 < 30 |
| NZDUSD | +0.0367 | -0.3127 | 34 | EV_R VALID -0.3127 <= 0 |
| USDCHF | +0.0046 | -0.0746 | 33 | EV_R VALID -0.0746 <= 0 |
| XAUUSD | +0.3092 | -0.0438 | 14 | EV_R VALID -0.0438 <= 0; N_valid 14 < 30 |

### SL1/TP1

**(a) Zilizopita kanuni:**

| pair | EV_R train | EV_R valid | N valid | EV_pips valid |
|---|---|---|---|---|
| AUDUSD | +0.2733 | +0.3052 | 37 | +17.47 |
| EURCHF | +0.2781 | +0.5208 | 30 | +25.22 |
| EURJPY | +0.2013 | +0.3004 | 41 | +47.13 |
| EURUSD | +0.1065 | +0.0572 | 48 | +3.85 |
| GBPUSD | +0.2118 | +0.0982 | 38 | +9.04 |
| USDCAD | +0.1685 | +0.4137 | 35 | +26.65 |
| USDCHF | +0.0525 | +0.0294 | 35 | +1.07 |
| USDJPY | +0.0606 | +0.2724 | 44 | +44.85 |

```yaml
    pairs:      [AUDUSD, EURCHF, EURJPY, EURUSD, GBPUSD, USDCAD, USDCHF, USDJPY]   # M4-0 rule: EV_R>0 train NA valid NA N_valid>=30
```

**(b) Zilizokataliwa + sababu:**

| pair | EV_R train | EV_R valid | N valid | sababu |
|---|---|---|---|---|
| EURGBP | +0.1990 | -0.0220 | 41 | EV_R VALID -0.0220 <= 0 |
| GBPJPY | +0.4060 | +0.7404 | 17 | N_valid 17 < 30 |
| NZDUSD | +0.1480 | -0.2274 | 41 | EV_R VALID -0.2274 <= 0 |
| XAUUSD | +0.4668 | +0.1841 | 15 | N_valid 15 < 30 |

## Caveats (uwazi)

1. **Si edge claim.** Baseline = kipimo cha nafasi za logic iliyopo kwa pairs 12; p_boot ni descriptive. STRAT-001/002 PEKEE ndizo PROVEN (holdout one-shot) — docs/STRATEGIES.md.
2. **VALIDATION ni ya 2023-2024** na tayari imetumika na utafiti wa nr7 (grid ya S1/S2). Hakuna dirisha jipya lililofunguliwa hapa; HOLDOUT + sealed 2026-05+ hazijaguswa.
3. **Pips vs R:** XAUUSD ina pip 0.01 — EV_pips ya pairs zote inatawaliwa na gold. Hukumu = EV_R (dimensionless); safu ya FX-pekee ndiyo inayolinganishwa na KAIROS-1/2.
4. **trades/mwaka** = Σ ya per-pair (n_i / miaka_i) — pairs zinatradiwa SAMBAMBA; risk-engine (max_slots/correlated) itapunguza idadi halisi inayotekelezwa.
5. **Kanuni ya `pairs[]` haithibitishi pair yoyote OOS.** Ni screen ya sign-consistency (train NA valid) + N — inapunguza selection bias, HAIIONDOI. Uthibitisho = holdout/forward.
6. **B_eff** ya bootstrap inapunguzwa kutoka 10,000 kadri N inavyokua (RAM: array (B×N) ya _stationary_indices; sakafu 1,000). Engine na mean_block hazijabadilika.

*reuse-only: episodes/_mask_context/pvalue_boot/load_window/_r_normalize/pool_streams/_boot_ci ni imports (ZERO changes). Profitable != Tradable Edge. Protect capital first.*