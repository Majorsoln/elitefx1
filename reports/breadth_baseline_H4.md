# M4-0 — BREADTH BASELINE (nr7_break × pairs 12 × H4, POOLED)

*2026-08-01 22:06 | charter: docs/CYCLE4_ML_CHARTER.md §1B/§5 · spec: docs/KAIROS_3_SPEC.md §5.3 | splits: TRAIN 2016-2022 + VALIDATION 2023-2024 | filter: no-LATE, vol=None, max_hold=24 | costs: spread halisi ya bar ya entry + slippage (L-039) | engine RASMI: pvalue_boot mean_block=3, seed=hash(registration)*

> **HII SI EDGE CLAIM MPYA.** Logic ni ILE ILE iliyothibitika (`nr7_break` × H1 × no-LATE = STRAT-001/002), imeenezwa tu kutoka pairs 2 → pairs 12 (chanzo (B) cha nafasi, charter §1B). Kusudi ni **kipimo**: namba ambayo KAIROS-3 (na HATUA 1-3 zote za ML) **LAZIMA izidi**.

> **HOLDOUT (2025-01→2026-04) HAIJAGUSWA** na dirisha **SEALED 2026-05+** (Doctrine §3.1b) haliingii — runner ina-refuse split yoyote isiyokuwa train/validation KABLA ya kusoma data.

> **POOLED ndiyo hukumu (LESSON-041).** Per-pair = diagnostics TU; hakuna best-pair selection popote kwenye faili hii.


## BASELINE LINE (bar ya KAIROS-3)

> ### KAIROS-3 LAZIMA izidi: **EV_net = +5.24 pips/trade** (pooled FX, N=1965, bila XAUUSD), **trades/mwaka = 1051.5** (VALIDATION).
>
> Currency ya hukumu (L-041) = **EV_R = +0.1422** (R-units, pooled pairs 12). Pips: **+18.89** (pairs zote, pip-scale ya XAUUSD ndani) · **+5.24** (FX pekee, N=1965 — ndiyo inayolinganishwa na KAIROS-1 +1.92 / KAIROS-2 +2.65).
>
> N (VALID) = **2101** · p_boot = 0.000105 · variant = **SL1/TP1** (variant yenye nguvu zaidi VALIDATION kati ya mbili — bar ya JUU = conservative kwa challenger; zote: SL2/TP1 EV_R=+0.0783 · SL1/TP1 EV_R=+0.1422).
>
> Kwa spec §5.2 ya KAIROS-3 (EV_net ≥ 3.0 pips NA ≥ 3× gharama): bar halisi ya kupita = **max(3.0, +5.24)** pips/trade, NA trades/mwaka ≥ 1051.5 (breadth haipaswi kupungua).

## Pooled (HUKUMU — L-041) kwa kila exit-variant

| variant | split | pairs | N | EV_R | CI90 (R) | EV_pips (12) | EV_pips (FX) | trades/mwaka | win% | PF | p_boot | p_z | B_eff |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SL2/TP1 | TRAIN | 12 | 7296 | +0.0717 | [+0.0589, +0.0843] | +10.60 | +4.60 | 1043.9 | 72.7 | 1.26 | 0.000365 | 0.0 | 2741 |
| SL2/TP1 | VALIDATION | 12 | 1936 | +0.0783 | [+0.0547, +0.1035] | +26.67 | +4.53 | 968.9 | 73.4 | 1.29 | 0.0001 | 0.0 | 10000 |
| SL1/TP1 | TRAIN | 12 | 8013 | +0.1409 | [+0.1237, +0.1592] | +7.60 | +4.84 | 1146.5 | 59.4 | 1.33 | 0.000401 | 0.0 | 2495 |
| SL1/TP1 | VALIDATION | 12 | 2101 | +0.1422 | [+0.1053, +0.1767] | +18.89 | +5.24 | 1051.5 | 59.7 | 1.33 | 0.000105 | 0.0 | 9519 |

*Pairs bila dirisha (hazikuingia pooling): hakuna. p_boot ni **descriptive** hapa (baseline, si test iliyosajiliwa) — TRAIN/VALIDATION zimeshatumika na utafiti wa nr7; hakuna dirisha jipya lililochomwa.*

## Per-pair (DIAGNOSTICS TU — ⚠ SI selection)

> ⚠ **TAHADHARI (LESSON-041):** namba hizi HAZITUMIKI kuchagua pair 'bora'. Kuchagua pair yenye EV kubwa zaidi ya TRAIN ni max-selection bias — ilipinduka hasi OOS 3/3. Zinaonyeshwa kwa uwazi wa accounting (jumla ya N zao = N ya pooled) na kwa kanuni ya `pairs[]` hapa chini, ambayo ni **sheria ya sign+N, si ranking**.


### SL2/TP1

| pair | N (train) | EV_R (train) | EV_pips (train) | N (valid) | EV_R (valid) | EV_pips (valid) | trades/mwaka (valid) |
|---|---|---|---|---|---|---|---|
| AUDUSD | 520 | +0.1289 | +6.39 | 148 | +0.1314 | +5.65 | 74.1 |
| EURCHF | 640 | +0.0244 | +0.80 | 168 | +0.0104 | -0.34 | 84.1 |
| EURGBP | 619 | +0.0810 | +4.23 | 173 | +0.1892 | +5.76 | 86.6 |
| EURJPY | 550 | +0.0773 | +4.73 | 144 | +0.0288 | +2.83 | 72.1 |
| EURUSD | 639 | +0.1011 | +6.02 | 161 | +0.0026 | +1.10 | 80.6 |
| GBPJPY | 613 | +0.0820 | +9.29 | 141 | +0.1052 | +12.19 | 70.5 |
| GBPUSD | 638 | +0.0446 | +4.67 | 175 | +0.0469 | +3.28 | 87.6 |
| NZDUSD | 577 | +0.1061 | +4.96 | 155 | +0.0515 | +2.67 | 77.6 |
| USDCAD | 669 | +0.0303 | +1.52 | 194 | +0.0421 | +3.55 | 97.1 |
| USDCHF | 658 | +0.0532 | +3.12 | 199 | +0.0807 | +4.03 | 99.6 |
| USDJPY | 593 | +0.0904 | +5.65 | 150 | +0.1136 | +10.92 | 75.1 |
| XAUUSD | 580 | +0.0590 | +80.18 | 128 | +0.1626 | +339.40 | 64.1 |

### SL1/TP1

| pair | N (train) | EV_R (train) | EV_pips (train) | N (valid) | EV_R (valid) | EV_pips (valid) | trades/mwaka (valid) |
|---|---|---|---|---|---|---|---|
| AUDUSD | 556 | +0.2346 | +5.91 | 157 | +0.2398 | +5.46 | 78.6 |
| EURCHF | 723 | +0.0373 | +0.66 | 189 | +0.0299 | +0.33 | 94.6 |
| EURGBP | 670 | +0.1771 | +4.77 | 189 | +0.2279 | +3.28 | 94.6 |
| EURJPY | 605 | +0.2016 | +7.02 | 155 | +0.1797 | +10.55 | 77.6 |
| EURUSD | 690 | +0.2001 | +6.17 | 175 | +0.0028 | +0.73 | 87.6 |
| GBPJPY | 658 | +0.1719 | +9.79 | 148 | +0.2658 | +17.10 | 74.0 |
| GBPUSD | 715 | +0.0739 | +3.85 | 185 | +0.0962 | +4.06 | 92.6 |
| NZDUSD | 614 | +0.2397 | +6.07 | 167 | +0.1744 | +3.73 | 83.6 |
| USDCAD | 759 | +0.0076 | +0.19 | 214 | +0.0614 | +2.42 | 107.1 |
| USDCHF | 736 | +0.1054 | +3.10 | 217 | +0.0880 | +2.03 | 108.6 |
| USDJPY | 659 | +0.2208 | +7.45 | 169 | +0.2534 | +12.65 | 84.6 |
| XAUUSD | 628 | +0.0814 | +40.03 | 136 | +0.1668 | +216.05 | 68.1 |

## PENDEKEZO la `pairs[]` kwa `config/models.yaml` (KAIROS-1/2 multi-pair)

> **KANUNI (pre-registered, SI ranking):** pair inapendekezwa IKIWA **EV_R > 0 kwenye TRAIN** NA **EV_R > 0 kwenye VALIDATION** NA **N_valid ≥ 30**.
> **HAKUNA "top-N kwa EV"** (= max-selection bias, LESSON-041). Orodha ni ya **alfabeti**, si ya EV — hata mpangilio usipendekeze ranking.
> Hili ni **PENDEKEZO la utafiti. PD ndiye anayehariri `config/models.yaml`** — code haiandiki registry.


### SL2/TP1

**(a) Zilizopita kanuni:**

| pair | EV_R train | EV_R valid | N valid | EV_pips valid |
|---|---|---|---|---|
| AUDUSD | +0.1289 | +0.1314 | 148 | +5.65 |
| EURCHF | +0.0244 | +0.0104 | 168 | -0.34 |
| EURGBP | +0.0810 | +0.1892 | 173 | +5.76 |
| EURJPY | +0.0773 | +0.0288 | 144 | +2.83 |
| EURUSD | +0.1011 | +0.0026 | 161 | +1.10 |
| GBPJPY | +0.0820 | +0.1052 | 141 | +12.19 |
| GBPUSD | +0.0446 | +0.0469 | 175 | +3.28 |
| NZDUSD | +0.1061 | +0.0515 | 155 | +2.67 |
| USDCAD | +0.0303 | +0.0421 | 194 | +3.55 |
| USDCHF | +0.0532 | +0.0807 | 199 | +4.03 |
| USDJPY | +0.0904 | +0.1136 | 150 | +10.92 |
| XAUUSD | +0.0590 | +0.1626 | 128 | +339.40 |

```yaml
    pairs:      [AUDUSD, EURCHF, EURGBP, EURJPY, EURUSD, GBPJPY, GBPUSD, NZDUSD, USDCAD, USDCHF, USDJPY, XAUUSD]   # M4-0 rule: EV_R>0 train NA valid NA N_valid>=30
```

**(b) Zilizokataliwa + sababu:**

| pair | EV_R train | EV_R valid | N valid | sababu |
|---|---|---|---|---|

### SL1/TP1

**(a) Zilizopita kanuni:**

| pair | EV_R train | EV_R valid | N valid | EV_pips valid |
|---|---|---|---|---|
| AUDUSD | +0.2346 | +0.2398 | 157 | +5.46 |
| EURCHF | +0.0373 | +0.0299 | 189 | +0.33 |
| EURGBP | +0.1771 | +0.2279 | 189 | +3.28 |
| EURJPY | +0.2016 | +0.1797 | 155 | +10.55 |
| EURUSD | +0.2001 | +0.0028 | 175 | +0.73 |
| GBPJPY | +0.1719 | +0.2658 | 148 | +17.10 |
| GBPUSD | +0.0739 | +0.0962 | 185 | +4.06 |
| NZDUSD | +0.2397 | +0.1744 | 167 | +3.73 |
| USDCAD | +0.0076 | +0.0614 | 214 | +2.42 |
| USDCHF | +0.1054 | +0.0880 | 217 | +2.03 |
| USDJPY | +0.2208 | +0.2534 | 169 | +12.65 |
| XAUUSD | +0.0814 | +0.1668 | 136 | +216.05 |

```yaml
    pairs:      [AUDUSD, EURCHF, EURGBP, EURJPY, EURUSD, GBPJPY, GBPUSD, NZDUSD, USDCAD, USDCHF, USDJPY, XAUUSD]   # M4-0 rule: EV_R>0 train NA valid NA N_valid>=30
```

**(b) Zilizokataliwa + sababu:**

| pair | EV_R train | EV_R valid | N valid | sababu |
|---|---|---|---|---|

## Caveats (uwazi)

1. **Si edge claim.** Baseline = kipimo cha nafasi za logic iliyopo kwa pairs 12; p_boot ni descriptive. STRAT-001/002 PEKEE ndizo PROVEN (holdout one-shot) — docs/STRATEGIES.md.
2. **VALIDATION ni ya 2023-2024** na tayari imetumika na utafiti wa nr7 (grid ya S1/S2). Hakuna dirisha jipya lililofunguliwa hapa; HOLDOUT + sealed 2026-05+ hazijaguswa.
3. **Pips vs R:** XAUUSD ina pip 0.01 — EV_pips ya pairs zote inatawaliwa na gold. Hukumu = EV_R (dimensionless); safu ya FX-pekee ndiyo inayolinganishwa na KAIROS-1/2.
4. **trades/mwaka** = Σ ya per-pair (n_i / miaka_i) — pairs zinatradiwa SAMBAMBA; risk-engine (max_slots/correlated) itapunguza idadi halisi inayotekelezwa.
5. **Kanuni ya `pairs[]` haithibitishi pair yoyote OOS.** Ni screen ya sign-consistency (train NA valid) + N — inapunguza selection bias, HAIIONDOI. Uthibitisho = holdout/forward.
6. **B_eff** ya bootstrap inapunguzwa kutoka 10,000 kadri N inavyokua (RAM: array (B×N) ya _stationary_indices; sakafu 1,000). Engine na mean_block hazijabadilika.

*reuse-only: episodes/_mask_context/pvalue_boot/load_window/_r_normalize/pool_streams/_boot_ci ni imports (ZERO changes). Profitable != Tradable Edge. Protect capital first.*