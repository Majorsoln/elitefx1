# M4-0 — BREADTH BASELINE (nr7_break × pairs 12 × D1, POOLED)

*2026-08-01 22:06 | charter: docs/CYCLE4_ML_CHARTER.md §1B/§5 · spec: docs/KAIROS_3_SPEC.md §5.3 | splits: TRAIN 2016-2022 + VALIDATION 2023-2024 | filter: None, vol=None, max_hold=20 | costs: spread halisi ya bar ya entry + slippage (L-039) | engine RASMI: pvalue_boot mean_block=3, seed=hash(registration)*

> **HII SI EDGE CLAIM MPYA.** Logic ni ILE ILE iliyothibitika (`nr7_break` × H1 × no-LATE = STRAT-001/002), imeenezwa tu kutoka pairs 2 → pairs 12 (chanzo (B) cha nafasi, charter §1B). Kusudi ni **kipimo**: namba ambayo KAIROS-3 (na HATUA 1-3 zote za ML) **LAZIMA izidi**.

> **HOLDOUT (2025-01→2026-04) HAIJAGUSWA** na dirisha **SEALED 2026-05+** (Doctrine §3.1b) haliingii — runner ina-refuse split yoyote isiyokuwa train/validation KABLA ya kusoma data.

> **POOLED ndiyo hukumu (LESSON-041).** Per-pair = diagnostics TU; hakuna best-pair selection popote kwenye faili hii.


## BASELINE LINE (bar ya KAIROS-3)

> ### KAIROS-3 LAZIMA izidi: **EV_net = +21.75 pips/trade** (pooled FX, N=407, bila XAUUSD), **trades/mwaka = 211.4** (VALIDATION).
>
> Currency ya hukumu (L-041) = **EV_R = +0.2109** (R-units, pooled pairs 12). Pips: **+31.68** (pairs zote, pip-scale ya XAUUSD ndani) · **+21.75** (FX pekee, N=407 — ndiyo inayolinganishwa na KAIROS-1 +1.92 / KAIROS-2 +2.65).
>
> N (VALID) = **422** · p_boot = 0.0002 · variant = **SL1/TP1** (variant yenye nguvu zaidi VALIDATION kati ya mbili — bar ya JUU = conservative kwa challenger; zote: SL2/TP1 EV_R=+0.0865 · SL1/TP1 EV_R=+0.2109).
>
> Kwa spec §5.2 ya KAIROS-3 (EV_net ≥ 3.0 pips NA ≥ 3× gharama): bar halisi ya kupita = **max(3.0, +21.75)** pips/trade, NA trades/mwaka ≥ 211.4 (breadth haipaswi kupungua).

## Pooled (HUKUMU — L-041) kwa kila exit-variant

| variant | split | pairs | N | EV_R | CI90 (R) | EV_pips (12) | EV_pips (FX) | trades/mwaka | win% | PF | p_boot | p_z | B_eff |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SL2/TP1 | TRAIN | 12 | 1301 | +0.1026 | [+0.0738, +0.1315] | +65.74 | +15.55 | 186.2 | 73.1 | 1.40 | 0.0001 | 0.0 | 10000 |
| SL2/TP1 | VALIDATION | 12 | 383 | +0.0865 | [+0.0329, +0.1419] | +1.80 | +19.72 | 191.9 | 72.3 | 1.33 | 0.007999 | 0.004794 | 10000 |
| SL1/TP1 | TRAIN | 12 | 1465 | +0.2116 | [+0.1689, +0.2508] | +51.62 | +16.71 | 209.7 | 61.4 | 1.54 | 0.0001 | 0.0 | 10000 |
| SL1/TP1 | VALIDATION | 12 | 422 | +0.2109 | [+0.1332, +0.2904] | +31.68 | +21.75 | 211.4 | 61.6 | 1.54 | 0.0002 | 4e-06 | 10000 |

*Pairs bila dirisha (hazikuingia pooling): hakuna. p_boot ni **descriptive** hapa (baseline, si test iliyosajiliwa) — TRAIN/VALIDATION zimeshatumika na utafiti wa nr7; hakuna dirisha jipya lililochomwa.*

## Per-pair (DIAGNOSTICS TU — ⚠ SI selection)

> ⚠ **TAHADHARI (LESSON-041):** namba hizi HAZITUMIKI kuchagua pair 'bora'. Kuchagua pair yenye EV kubwa zaidi ya TRAIN ni max-selection bias — ilipinduka hasi OOS 3/3. Zinaonyeshwa kwa uwazi wa accounting (jumla ya N zao = N ya pooled) na kwa kanuni ya `pairs[]` hapa chini, ambayo ni **sheria ya sign+N, si ranking**.


### SL2/TP1

| pair | N (train) | EV_R (train) | EV_pips (train) | N (valid) | EV_R (valid) | EV_pips (valid) | trades/mwaka (valid) |
|---|---|---|---|---|---|---|---|
| AUDUSD | 121 | +0.1458 | +19.99 | 35 | +0.1465 | +13.94 | 17.5 |
| EURCHF | 72 | +0.1589 | +14.89 | 30 | +0.1986 | +20.19 | 15.0 |
| EURGBP | 125 | +0.1116 | +17.11 | 36 | +0.1850 | +12.33 | 18.0 |
| EURJPY | 127 | +0.0879 | +21.55 | 39 | +0.1489 | +47.11 | 19.5 |
| EURUSD | 127 | -0.0078 | -1.57 | 39 | -0.0271 | -4.89 | 19.5 |
| GBPJPY | 70 | +0.1693 | +47.82 | 17 | +0.4915 | +162.20 | 8.5 |
| GBPUSD | 115 | +0.0932 | +18.72 | 33 | +0.0494 | +7.86 | 16.5 |
| NZDUSD | 123 | +0.0608 | +6.14 | 34 | -0.2818 | -34.74 | 17.0 |
| USDCAD | 114 | +0.1128 | +21.18 | 35 | +0.2179 | +26.68 | 17.5 |
| USDCHF | 125 | +0.0316 | +4.73 | 33 | -0.0493 | -7.85 | 16.5 |
| USDJPY | 123 | +0.1228 | +15.28 | 38 | +0.1272 | +41.60 | 19.0 |
| XAUUSD | 59 | +0.3106 | +1122.36 | 14 | -0.0426 | -470.34 | 7.0 |

### SL1/TP1

| pair | N (train) | EV_R (train) | EV_pips (train) | N (valid) | EV_R (valid) | EV_pips (valid) | trades/mwaka (valid) |
|---|---|---|---|---|---|---|---|
| AUDUSD | 135 | +0.2972 | +20.24 | 37 | +0.3299 | +19.09 | 18.5 |
| EURCHF | 76 | +0.3101 | +13.91 | 30 | +0.5567 | +26.77 | 15.0 |
| EURGBP | 145 | +0.2307 | +16.05 | 41 | +0.0347 | -0.12 | 20.5 |
| EURJPY | 149 | +0.2201 | +22.40 | 41 | +0.3172 | +49.42 | 20.5 |
| EURUSD | 153 | +0.1267 | +8.21 | 48 | +0.0792 | +5.37 | 24.1 |
| GBPJPY | 74 | +0.4149 | +51.95 | 17 | +0.7476 | +118.68 | 8.5 |
| GBPUSD | 127 | +0.2297 | +25.90 | 38 | +0.1178 | +10.73 | 19.0 |
| NZDUSD | 142 | +0.1750 | +11.00 | 41 | -0.1989 | -12.48 | 20.5 |
| USDCAD | 130 | +0.1907 | +19.15 | 35 | +0.4357 | +28.13 | 17.5 |
| USDCHF | 136 | +0.0846 | +6.80 | 35 | +0.0614 | +3.12 | 17.5 |
| USDJPY | 139 | +0.0865 | +4.80 | 44 | +0.2869 | +46.71 | 22.1 |
| XAUUSD | 59 | +0.4687 | +883.54 | 15 | +0.1864 | +301.31 | 7.5 |

## PENDEKEZO la `pairs[]` kwa `config/models.yaml` (KAIROS-1/2 multi-pair)

> **KANUNI (pre-registered, SI ranking):** pair inapendekezwa IKIWA **EV_R > 0 kwenye TRAIN** NA **EV_R > 0 kwenye VALIDATION** NA **N_valid ≥ 30**.
> **HAKUNA "top-N kwa EV"** (= max-selection bias, LESSON-041). Orodha ni ya **alfabeti**, si ya EV — hata mpangilio usipendekeze ranking.
> Hili ni **PENDEKEZO la utafiti. PD ndiye anayehariri `config/models.yaml`** — code haiandiki registry.


### SL2/TP1

**(a) Zilizopita kanuni:**

| pair | EV_R train | EV_R valid | N valid | EV_pips valid |
|---|---|---|---|---|
| AUDUSD | +0.1458 | +0.1465 | 35 | +13.94 |
| EURCHF | +0.1589 | +0.1986 | 30 | +20.19 |
| EURGBP | +0.1116 | +0.1850 | 36 | +12.33 |
| EURJPY | +0.0879 | +0.1489 | 39 | +47.11 |
| GBPUSD | +0.0932 | +0.0494 | 33 | +7.86 |
| USDCAD | +0.1128 | +0.2179 | 35 | +26.68 |
| USDJPY | +0.1228 | +0.1272 | 38 | +41.60 |

```yaml
    pairs:      [AUDUSD, EURCHF, EURGBP, EURJPY, GBPUSD, USDCAD, USDJPY]   # M4-0 rule: EV_R>0 train NA valid NA N_valid>=30
```

**(b) Zilizokataliwa + sababu:**

| pair | EV_R train | EV_R valid | N valid | sababu |
|---|---|---|---|---|
| EURUSD | -0.0078 | -0.0271 | 39 | EV_R TRAIN -0.0078 <= 0; EV_R VALID -0.0271 <= 0 |
| GBPJPY | +0.1693 | +0.4915 | 17 | N_valid 17 < 30 |
| NZDUSD | +0.0608 | -0.2818 | 34 | EV_R VALID -0.2818 <= 0 |
| USDCHF | +0.0316 | -0.0493 | 33 | EV_R VALID -0.0493 <= 0 |
| XAUUSD | +0.3106 | -0.0426 | 14 | EV_R VALID -0.0426 <= 0; N_valid 14 < 30 |

### SL1/TP1

**(a) Zilizopita kanuni:**

| pair | EV_R train | EV_R valid | N valid | EV_pips valid |
|---|---|---|---|---|
| AUDUSD | +0.2972 | +0.3299 | 37 | +19.09 |
| EURCHF | +0.3101 | +0.5567 | 30 | +26.77 |
| EURGBP | +0.2307 | +0.0347 | 41 | -0.12 |
| EURJPY | +0.2201 | +0.3172 | 41 | +49.42 |
| EURUSD | +0.1267 | +0.0792 | 48 | +5.37 |
| GBPUSD | +0.2297 | +0.1178 | 38 | +10.73 |
| USDCAD | +0.1907 | +0.4357 | 35 | +28.13 |
| USDCHF | +0.0846 | +0.0614 | 35 | +3.12 |
| USDJPY | +0.0865 | +0.2869 | 44 | +46.71 |

```yaml
    pairs:      [AUDUSD, EURCHF, EURGBP, EURJPY, EURUSD, GBPUSD, USDCAD, USDCHF, USDJPY]   # M4-0 rule: EV_R>0 train NA valid NA N_valid>=30
```

**(b) Zilizokataliwa + sababu:**

| pair | EV_R train | EV_R valid | N valid | sababu |
|---|---|---|---|---|
| GBPJPY | +0.4149 | +0.7476 | 17 | N_valid 17 < 30 |
| NZDUSD | +0.1750 | -0.1989 | 41 | EV_R VALID -0.1989 <= 0 |
| XAUUSD | +0.4687 | +0.1864 | 15 | N_valid 15 < 30 |

## Caveats (uwazi)

1. **Si edge claim.** Baseline = kipimo cha nafasi za logic iliyopo kwa pairs 12; p_boot ni descriptive. STRAT-001/002 PEKEE ndizo PROVEN (holdout one-shot) — docs/STRATEGIES.md.
2. **VALIDATION ni ya 2023-2024** na tayari imetumika na utafiti wa nr7 (grid ya S1/S2). Hakuna dirisha jipya lililofunguliwa hapa; HOLDOUT + sealed 2026-05+ hazijaguswa.
3. **Pips vs R:** XAUUSD ina pip 0.01 — EV_pips ya pairs zote inatawaliwa na gold. Hukumu = EV_R (dimensionless); safu ya FX-pekee ndiyo inayolinganishwa na KAIROS-1/2.
4. **trades/mwaka** = Σ ya per-pair (n_i / miaka_i) — pairs zinatradiwa SAMBAMBA; risk-engine (max_slots/correlated) itapunguza idadi halisi inayotekelezwa.
5. **Kanuni ya `pairs[]` haithibitishi pair yoyote OOS.** Ni screen ya sign-consistency (train NA valid) + N — inapunguza selection bias, HAIIONDOI. Uthibitisho = holdout/forward.
6. **B_eff** ya bootstrap inapunguzwa kutoka 10,000 kadri N inavyokua (RAM: array (B×N) ya _stationary_indices; sakafu 1,000). Engine na mean_block hazijabadilika.

*reuse-only: episodes/_mask_context/pvalue_boot/load_window/_r_normalize/pool_streams/_boot_ci ni imports (ZERO changes). Profitable != Tradable Edge. Protect capital first.*