# M4-0 — BREADTH BASELINE (nr7_break × pairs 12 × H4, POOLED)

*2026-08-01 22:25 | charter: docs/CYCLE4_ML_CHARTER.md §1B/§5 · spec: docs/KAIROS_3_SPEC.md §5.3 | splits: TRAIN 2016-2022 + VALIDATION 2023-2024 | filter: no-LATE, vol=None, max_hold=24 | swap: IMETUMIKA (config swap_pips_per_night, rmap.apply_swap) | costs: spread halisi ya bar ya entry + slippage (L-039) | engine RASMI: pvalue_boot mean_block=3, seed=hash(registration)*

> **HII SI EDGE CLAIM MPYA.** Logic ni ILE ILE iliyothibitika (`nr7_break` × H1 × no-LATE = STRAT-001/002), imeenezwa tu kutoka pairs 2 → pairs 12 (chanzo (B) cha nafasi, charter §1B). Kusudi ni **kipimo**: namba ambayo KAIROS-3 (na HATUA 1-3 zote za ML) **LAZIMA izidi**.

> **HOLDOUT (2025-01→2026-04) HAIJAGUSWA** na dirisha **SEALED 2026-05+** (Doctrine §3.1b) haliingii — runner ina-refuse split yoyote isiyokuwa train/validation KABLA ya kusoma data.

> **POOLED ndiyo hukumu (LESSON-041).** Per-pair = diagnostics TU; hakuna best-pair selection popote kwenye faili hii.


## BASELINE LINE (bar ya KAIROS-3)

> ### KAIROS-3 LAZIMA izidi: **EV_net = +5.14 pips/trade** (pooled FX, N=1965, bila XAUUSD), **trades/mwaka = 1051.5** (VALIDATION).
>
> Currency ya hukumu (L-041) = **EV_R = +0.1386** (R-units, pooled pairs 12). Pips: **+18.78** (pairs zote, pip-scale ya XAUUSD ndani) · **+5.14** (FX pekee, N=1965 — ndiyo inayolinganishwa na KAIROS-1 +1.92 / KAIROS-2 +2.65).
>
> N (VALID) = **2101** · p_boot = 0.000105 · variant = **SL1/TP1** (variant yenye nguvu zaidi VALIDATION kati ya mbili — bar ya JUU = conservative kwa challenger; zote: SL2/TP1 EV_R=+0.0730 · SL1/TP1 EV_R=+0.1386).
>
> Kwa spec §5.2 ya KAIROS-3 (EV_net ≥ 3.0 pips NA ≥ 3× gharama): bar halisi ya kupita = **max(3.0, +5.14)** pips/trade, NA trades/mwaka ≥ 1051.5 (breadth haipaswi kupungua).

## Pooled (HUKUMU — L-041) kwa kila exit-variant

| variant | split | pairs | N | EV_R | CI90 (R) | EV_pips (12) | EV_pips (FX) | trades/mwaka | win% | PF | p_boot | p_z | B_eff |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SL2/TP1 | TRAIN | 12 | 7296 | +0.0664 | [+0.0533, +0.0796] | +10.24 | +4.27 | 1043.9 | 72.6 | 1.24 | 0.000365 | 0.0 | 2741 |
| SL2/TP1 | VALIDATION | 12 | 1936 | +0.0730 | [+0.0482, +0.0968] | +26.36 | +4.23 | 968.9 | 73.2 | 1.27 | 0.0001 | 1e-06 | 10000 |
| SL1/TP1 | TRAIN | 12 | 8013 | +0.1373 | [+0.1197, +0.1557] | +7.46 | +4.72 | 1146.5 | 59.4 | 1.32 | 0.000401 | 0.0 | 2495 |
| SL1/TP1 | VALIDATION | 12 | 2101 | +0.1386 | [+0.1022, +0.1752] | +18.78 | +5.14 | 1051.5 | 59.7 | 1.32 | 0.000105 | 0.0 | 9519 |

*Pairs bila dirisha (hazikuingia pooling): hakuna. p_boot ni **descriptive** hapa (baseline, si test iliyosajiliwa) — TRAIN/VALIDATION zimeshatumika na utafiti wa nr7; hakuna dirisha jipya lililochomwa.*

## Per-pair (DIAGNOSTICS TU — ⚠ SI selection)

> ⚠ **TAHADHARI (LESSON-041):** namba hizi HAZITUMIKI kuchagua pair 'bora'. Kuchagua pair yenye EV kubwa zaidi ya TRAIN ni max-selection bias — ilipinduka hasi OOS 3/3. Zinaonyeshwa kwa uwazi wa accounting (jumla ya N zao = N ya pooled) na kwa kanuni ya `pairs[]` hapa chini, ambayo ni **sheria ya sign+N, si ranking**.


### SL2/TP1

| pair | N (train) | EV_R (train) | EV_pips (train) | N (valid) | EV_R (valid) | EV_pips (valid) | trades/mwaka (valid) |
|---|---|---|---|---|---|---|---|
| AUDUSD | 520 | +0.1223 | +6.04 | 148 | +0.1242 | +5.30 | 74.1 |
| EURCHF | 640 | +0.0149 | +0.44 | 168 | +0.0016 | -0.68 | 84.1 |
| EURGBP | 619 | +0.0753 | +3.97 | 173 | +0.1804 | +5.50 | 86.6 |
| EURJPY | 550 | +0.0730 | +4.40 | 144 | +0.0251 | +2.48 | 72.1 |
| EURUSD | 639 | +0.0966 | +5.77 | 161 | -0.0028 | +0.82 | 80.6 |
| GBPJPY | 613 | +0.0790 | +8.97 | 141 | +0.1028 | +11.90 | 70.5 |
| GBPUSD | 638 | +0.0415 | +4.41 | 175 | +0.0431 | +3.05 | 87.6 |
| NZDUSD | 577 | +0.0981 | +4.57 | 155 | +0.0449 | +2.36 | 77.6 |
| USDCAD | 669 | +0.0251 | +1.17 | 194 | +0.0366 | +3.25 | 97.1 |
| USDCHF | 658 | +0.0472 | +2.82 | 199 | +0.0753 | +3.77 | 99.6 |
| USDJPY | 593 | +0.0842 | +5.29 | 150 | +0.1097 | +10.55 | 75.1 |
| XAUUSD | 580 | +0.0583 | +79.27 | 128 | +0.1623 | +338.86 | 64.1 |

### SL1/TP1

| pair | N (train) | EV_R (train) | EV_pips (train) | N (valid) | EV_R (valid) | EV_pips (valid) | trades/mwaka (valid) |
|---|---|---|---|---|---|---|---|
| AUDUSD | 556 | +0.2293 | +5.77 | 157 | +0.2339 | +5.32 | 78.6 |
| EURCHF | 723 | +0.0321 | +0.55 | 189 | +0.0260 | +0.26 | 94.6 |
| EURGBP | 670 | +0.1730 | +4.68 | 189 | +0.2221 | +3.19 | 94.6 |
| EURJPY | 605 | +0.1984 | +6.90 | 155 | +0.1767 | +10.40 | 77.6 |
| EURUSD | 690 | +0.1973 | +6.10 | 175 | -0.0006 | +0.63 | 87.6 |
| GBPJPY | 658 | +0.1697 | +9.67 | 148 | +0.2637 | +16.98 | 74.0 |
| GBPUSD | 715 | +0.0723 | +3.78 | 185 | +0.0936 | +3.98 | 92.6 |
| NZDUSD | 614 | +0.2322 | +5.88 | 167 | +0.1689 | +3.61 | 83.6 |
| USDCAD | 759 | +0.0047 | +0.09 | 214 | +0.0581 | +2.33 | 107.1 |
| USDCHF | 736 | +0.1020 | +3.02 | 217 | +0.0843 | +1.94 | 108.6 |
| USDJPY | 659 | +0.2155 | +7.29 | 169 | +0.2506 | +12.54 | 84.6 |
| XAUUSD | 628 | +0.0808 | +39.68 | 136 | +0.1666 | +215.79 | 68.1 |

## PENDEKEZO la `pairs[]` kwa `config/models.yaml` (KAIROS-1/2 multi-pair)

> **KANUNI (pre-registered, SI ranking):** pair inapendekezwa IKIWA **EV_R > 0 kwenye TRAIN** NA **EV_R > 0 kwenye VALIDATION** NA **N_valid ≥ 30**.
> **HAKUNA "top-N kwa EV"** (= max-selection bias, LESSON-041). Orodha ni ya **alfabeti**, si ya EV — hata mpangilio usipendekeze ranking.
> Hili ni **PENDEKEZO la utafiti. PD ndiye anayehariri `config/models.yaml`** — code haiandiki registry.


### SL2/TP1

**(a) Zilizopita kanuni:**

| pair | EV_R train | EV_R valid | N valid | EV_pips valid |
|---|---|---|---|---|
| AUDUSD | +0.1223 | +0.1242 | 148 | +5.30 |
| EURCHF | +0.0149 | +0.0016 | 168 | -0.68 |
| EURGBP | +0.0753 | +0.1804 | 173 | +5.50 |
| EURJPY | +0.0730 | +0.0251 | 144 | +2.48 |
| GBPJPY | +0.0790 | +0.1028 | 141 | +11.90 |
| GBPUSD | +0.0415 | +0.0431 | 175 | +3.05 |
| NZDUSD | +0.0981 | +0.0449 | 155 | +2.36 |
| USDCAD | +0.0251 | +0.0366 | 194 | +3.25 |
| USDCHF | +0.0472 | +0.0753 | 199 | +3.77 |
| USDJPY | +0.0842 | +0.1097 | 150 | +10.55 |
| XAUUSD | +0.0583 | +0.1623 | 128 | +338.86 |

```yaml
    pairs:      [AUDUSD, EURCHF, EURGBP, EURJPY, GBPJPY, GBPUSD, NZDUSD, USDCAD, USDCHF, USDJPY, XAUUSD]   # M4-0 rule: EV_R>0 train NA valid NA N_valid>=30
```

**(b) Zilizokataliwa + sababu:**

| pair | EV_R train | EV_R valid | N valid | sababu |
|---|---|---|---|---|
| EURUSD | +0.0966 | -0.0028 | 161 | EV_R VALID -0.0028 <= 0 |

### SL1/TP1

**(a) Zilizopita kanuni:**

| pair | EV_R train | EV_R valid | N valid | EV_pips valid |
|---|---|---|---|---|
| AUDUSD | +0.2293 | +0.2339 | 157 | +5.32 |
| EURCHF | +0.0321 | +0.0260 | 189 | +0.26 |
| EURGBP | +0.1730 | +0.2221 | 189 | +3.19 |
| EURJPY | +0.1984 | +0.1767 | 155 | +10.40 |
| GBPJPY | +0.1697 | +0.2637 | 148 | +16.98 |
| GBPUSD | +0.0723 | +0.0936 | 185 | +3.98 |
| NZDUSD | +0.2322 | +0.1689 | 167 | +3.61 |
| USDCAD | +0.0047 | +0.0581 | 214 | +2.33 |
| USDCHF | +0.1020 | +0.0843 | 217 | +1.94 |
| USDJPY | +0.2155 | +0.2506 | 169 | +12.54 |
| XAUUSD | +0.0808 | +0.1666 | 136 | +215.79 |

```yaml
    pairs:      [AUDUSD, EURCHF, EURGBP, EURJPY, GBPJPY, GBPUSD, NZDUSD, USDCAD, USDCHF, USDJPY, XAUUSD]   # M4-0 rule: EV_R>0 train NA valid NA N_valid>=30
```

**(b) Zilizokataliwa + sababu:**

| pair | EV_R train | EV_R valid | N valid | sababu |
|---|---|---|---|---|
| EURUSD | +0.1973 | -0.0006 | 175 | EV_R VALID -0.0006 <= 0 |

## Caveats (uwazi)

1. **Si edge claim.** Baseline = kipimo cha nafasi za logic iliyopo kwa pairs 12; p_boot ni descriptive. STRAT-001/002 PEKEE ndizo PROVEN (holdout one-shot) — docs/STRATEGIES.md.
2. **VALIDATION ni ya 2023-2024** na tayari imetumika na utafiti wa nr7 (grid ya S1/S2). Hakuna dirisha jipya lililofunguliwa hapa; HOLDOUT + sealed 2026-05+ hazijaguswa.
3. **Pips vs R:** XAUUSD ina pip 0.01 — EV_pips ya pairs zote inatawaliwa na gold. Hukumu = EV_R (dimensionless); safu ya FX-pekee ndiyo inayolinganishwa na KAIROS-1/2.
4. **trades/mwaka** = Σ ya per-pair (n_i / miaka_i) — pairs zinatradiwa SAMBAMBA; risk-engine (max_slots/correlated) itapunguza idadi halisi inayotekelezwa.
5. **Kanuni ya `pairs[]` haithibitishi pair yoyote OOS.** Ni screen ya sign-consistency (train NA valid) + N — inapunguza selection bias, HAIIONDOI. Uthibitisho = holdout/forward.
6. **B_eff** ya bootstrap inapunguzwa kutoka 10,000 kadri N inavyokua (RAM: array (B×N) ya _stationary_indices; sakafu 1,000). Engine na mean_block hazijabadilika.

*reuse-only: episodes/_mask_context/pvalue_boot/load_window/_r_normalize/pool_streams/_boot_ci ni imports (ZERO changes). Profitable != Tradable Edge. Protect capital first.*