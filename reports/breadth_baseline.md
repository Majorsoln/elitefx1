# M4-0 — BREADTH BASELINE (nr7_break × pairs 12 × H1, POOLED)

*2026-08-01 09:32 | charter: docs/CYCLE4_ML_CHARTER.md §1B/§5 · spec: docs/KAIROS_3_SPEC.md §5.3 | splits: TRAIN 2016-2022 + VALIDATION 2023-2024 | filter: no-LATE, vol=None, max_hold=24 | costs: spread halisi ya bar ya entry + slippage (L-039) | engine RASMI: pvalue_boot mean_block=3, seed=hash(registration)*

> **HII SI EDGE CLAIM MPYA.** Logic ni ILE ILE iliyothibitika (`nr7_break` × H1 × no-LATE = STRAT-001/002), imeenezwa tu kutoka pairs 2 → pairs 12 (chanzo (B) cha nafasi, charter §1B). Kusudi ni **kipimo**: namba ambayo KAIROS-3 (na HATUA 1-3 zote za ML) **LAZIMA izidi**.

> **HOLDOUT (2025-01→2026-04) HAIJAGUSWA** na dirisha **SEALED 2026-05+** (Doctrine §3.1b) haliingii — runner ina-refuse split yoyote isiyokuwa train/validation KABLA ya kusoma data.

> **POOLED ndiyo hukumu (LESSON-041).** Per-pair = diagnostics TU; hakuna best-pair selection popote kwenye faili hii.


## BASELINE LINE (bar ya KAIROS-3)

> ### KAIROS-3 LAZIMA izidi: **EV_net = +0.91 pips/trade** (pooled FX, N=4934, bila XAUUSD), **trades/mwaka = 2680.0** (VALIDATION).
>
> Currency ya hukumu (L-041) = **EV_R = +0.0526** (R-units, pooled pairs 12). Pips: **+3.82** (pairs zote, pip-scale ya XAUUSD ndani) · **+0.91** (FX pekee, N=4934 — ndiyo inayolinganishwa na KAIROS-1 +1.92 / KAIROS-2 +2.65).
>
> N (VALID) = **5355** · p_boot = 0.000268 · variant = **SL1/TP1** (variant yenye nguvu zaidi VALIDATION kati ya mbili — bar ya JUU = conservative kwa challenger; zote: SL2/TP1 EV_R=+0.0328 · SL1/TP1 EV_R=+0.0526).
>
> Kwa spec §5.2 ya KAIROS-3 (EV_net ≥ 3.0 pips NA ≥ 3× gharama): bar halisi ya kupita = **max(3.0, +0.91)** pips/trade, NA trades/mwaka ≥ 2680.0 (breadth haipaswi kupungua).

## Pooled (HUKUMU — L-041) kwa kila exit-variant

| variant | split | pairs | N | EV_R | CI90 (R) | EV_pips (12) | EV_pips (FX) | trades/mwaka | win% | PF | p_boot | p_z | B_eff |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SL2/TP1 | TRAIN | 12 | 19164 | +0.0291 | [+0.0211, +0.0369] | +3.21 | +1.02 | 2741.8 | 71.4 | 1.10 | 0.000958 | 0.0 | 1043 |
| SL2/TP1 | VALIDATION | 12 | 5094 | +0.0328 | [+0.0163, +0.0477] | +3.40 | +0.90 | 2549.4 | 72.2 | 1.11 | 0.000764 | 0.000229 | 3926 |
| SL1/TP1 | TRAIN | 12 | 20316 | +0.0559 | [+0.0448, +0.0675] | +2.21 | +1.09 | 2906.7 | 57.7 | 1.12 | 0.000999 | 0.0 | 1000 |
| SL1/TP1 | VALIDATION | 12 | 5355 | +0.0526 | [+0.0295, +0.0744] | +3.82 | +0.91 | 2680.0 | 58.1 | 1.11 | 0.000268 | 5.1e-05 | 3734 |

*Pairs bila dirisha (hazikuingia pooling): hakuna. p_boot ni **descriptive** hapa (baseline, si test iliyosajiliwa) — TRAIN/VALIDATION zimeshatumika na utafiti wa nr7; hakuna dirisha jipya lililochomwa.*

## Per-pair (DIAGNOSTICS TU — ⚠ SI selection)

> ⚠ **TAHADHARI (LESSON-041):** namba hizi HAZITUMIKI kuchagua pair 'bora'. Kuchagua pair yenye EV kubwa zaidi ya TRAIN ni max-selection bias — ilipinduka hasi OOS 3/3. Zinaonyeshwa kwa uwazi wa accounting (jumla ya N zao = N ya pooled) na kwa kanuni ya `pairs[]` hapa chini, ambayo ni **sheria ya sign+N, si ranking**.


### SL2/TP1

| pair | N (train) | EV_R (train) | EV_pips (train) | N (valid) | EV_R (valid) | EV_pips (valid) | trades/mwaka (valid) |
|---|---|---|---|---|---|---|---|
| AUDUSD | 1555 | +0.0587 | +1.77 | 406 | +0.0266 | +0.82 | 203.2 |
| EURCHF | 1790 | -0.0257 | -0.22 | 509 | +0.0267 | +0.47 | 254.7 |
| EURGBP | 1791 | +0.0017 | +0.20 | 526 | -0.0583 | -0.87 | 263.2 |
| EURJPY | 1575 | +0.0398 | +1.51 | 429 | -0.0199 | -1.55 | 214.7 |
| EURUSD | 1336 | +0.0696 | +2.06 | 329 | +0.0931 | +2.16 | 164.6 |
| GBPJPY | 1716 | +0.0131 | +0.96 | 417 | +0.0126 | -0.39 | 208.7 |
| GBPUSD | 1492 | +0.0479 | +1.72 | 344 | +0.0737 | +2.67 | 172.2 |
| NZDUSD | 1678 | +0.0153 | +0.21 | 464 | +0.0040 | -0.15 | 232.2 |
| USDCAD | 1513 | +0.0521 | +1.83 | 416 | +0.0107 | +0.28 | 208.2 |
| USDCHF | 1607 | +0.0060 | +0.36 | 425 | +0.1355 | +3.07 | 212.7 |
| USDJPY | 1634 | +0.0581 | +1.35 | 429 | +0.0981 | +4.56 | 214.7 |
| XAUUSD | 1477 | +0.0344 | +29.42 | 400 | +0.0370 | +32.81 | 200.4 |

### SL1/TP1

| pair | N (train) | EV_R (train) | EV_pips (train) | N (valid) | EV_R (valid) | EV_pips (valid) | trades/mwaka (valid) |
|---|---|---|---|---|---|---|---|
| AUDUSD | 1647 | +0.1023 | +1.54 | 425 | +0.0856 | +1.04 | 212.7 |
| EURCHF | 1904 | -0.0659 | -0.46 | 525 | +0.0446 | +0.61 | 262.7 |
| EURGBP | 1903 | -0.0150 | +0.12 | 550 | -0.1033 | -0.77 | 275.2 |
| EURJPY | 1672 | +0.0882 | +1.52 | 464 | -0.0073 | -0.96 | 232.2 |
| EURUSD | 1410 | +0.1281 | +1.95 | 348 | +0.1242 | +1.44 | 174.2 |
| GBPJPY | 1814 | +0.0406 | +1.47 | 440 | +0.1221 | +2.76 | 220.2 |
| GBPUSD | 1571 | +0.0894 | +1.84 | 357 | +0.0926 | +1.57 | 178.7 |
| NZDUSD | 1796 | +0.0503 | +0.55 | 496 | -0.0080 | -0.25 | 248.2 |
| USDCAD | 1590 | +0.0821 | +1.42 | 439 | +0.0166 | +0.24 | 219.7 |
| USDCHF | 1687 | +0.0345 | +0.58 | 446 | +0.1051 | +1.21 | 223.2 |
| USDJPY | 1746 | +0.1319 | +1.98 | 444 | +0.1641 | +4.05 | 222.2 |
| XAUUSD | 1576 | +0.0449 | +15.50 | 421 | +0.0691 | +37.96 | 211.0 |

## PENDEKEZO la `pairs[]` kwa `config/models.yaml` (KAIROS-1/2 multi-pair)

> **KANUNI (pre-registered, SI ranking):** pair inapendekezwa IKIWA **EV_R > 0 kwenye TRAIN** NA **EV_R > 0 kwenye VALIDATION** NA **N_valid ≥ 30**.
> **HAKUNA "top-N kwa EV"** (= max-selection bias, LESSON-041). Orodha ni ya **alfabeti**, si ya EV — hata mpangilio usipendekeze ranking.
> Hili ni **PENDEKEZO la utafiti. PD ndiye anayehariri `config/models.yaml`** — code haiandiki registry.


### SL2/TP1

**(a) Zilizopita kanuni:**

| pair | EV_R train | EV_R valid | N valid | EV_pips valid |
|---|---|---|---|---|
| AUDUSD | +0.0587 | +0.0266 | 406 | +0.82 |
| EURUSD | +0.0696 | +0.0931 | 329 | +2.16 |
| GBPJPY | +0.0131 | +0.0126 | 417 | -0.39 |
| GBPUSD | +0.0479 | +0.0737 | 344 | +2.67 |
| NZDUSD | +0.0153 | +0.0040 | 464 | -0.15 |
| USDCAD | +0.0521 | +0.0107 | 416 | +0.28 |
| USDCHF | +0.0060 | +0.1355 | 425 | +3.07 |
| USDJPY | +0.0581 | +0.0981 | 429 | +4.56 |
| XAUUSD | +0.0344 | +0.0370 | 400 | +32.81 |

```yaml
    pairs:      [AUDUSD, EURUSD, GBPJPY, GBPUSD, NZDUSD, USDCAD, USDCHF, USDJPY, XAUUSD]   # M4-0 rule: EV_R>0 train NA valid NA N_valid>=30
```

**(b) Zilizokataliwa + sababu:**

| pair | EV_R train | EV_R valid | N valid | sababu |
|---|---|---|---|---|
| EURCHF | -0.0257 | +0.0267 | 509 | EV_R TRAIN -0.0257 <= 0 |
| EURGBP | +0.0017 | -0.0583 | 526 | EV_R VALID -0.0583 <= 0 |
| EURJPY | +0.0398 | -0.0199 | 429 | EV_R VALID -0.0199 <= 0 |

### SL1/TP1

**(a) Zilizopita kanuni:**

| pair | EV_R train | EV_R valid | N valid | EV_pips valid |
|---|---|---|---|---|
| AUDUSD | +0.1023 | +0.0856 | 425 | +1.04 |
| EURUSD | +0.1281 | +0.1242 | 348 | +1.44 |
| GBPJPY | +0.0406 | +0.1221 | 440 | +2.76 |
| GBPUSD | +0.0894 | +0.0926 | 357 | +1.57 |
| USDCAD | +0.0821 | +0.0166 | 439 | +0.24 |
| USDCHF | +0.0345 | +0.1051 | 446 | +1.21 |
| USDJPY | +0.1319 | +0.1641 | 444 | +4.05 |
| XAUUSD | +0.0449 | +0.0691 | 421 | +37.96 |

```yaml
    pairs:      [AUDUSD, EURUSD, GBPJPY, GBPUSD, USDCAD, USDCHF, USDJPY, XAUUSD]   # M4-0 rule: EV_R>0 train NA valid NA N_valid>=30
```

**(b) Zilizokataliwa + sababu:**

| pair | EV_R train | EV_R valid | N valid | sababu |
|---|---|---|---|---|
| EURCHF | -0.0659 | +0.0446 | 525 | EV_R TRAIN -0.0659 <= 0 |
| EURGBP | -0.0150 | -0.1033 | 550 | EV_R TRAIN -0.0150 <= 0; EV_R VALID -0.1033 <= 0 |
| EURJPY | +0.0882 | -0.0073 | 464 | EV_R VALID -0.0073 <= 0 |
| NZDUSD | +0.0503 | -0.0080 | 496 | EV_R VALID -0.0080 <= 0 |

## Caveats (uwazi)

1. **Si edge claim.** Baseline = kipimo cha nafasi za logic iliyopo kwa pairs 12; p_boot ni descriptive. STRAT-001/002 PEKEE ndizo PROVEN (holdout one-shot) — docs/STRATEGIES.md.
2. **VALIDATION ni ya 2023-2024** na tayari imetumika na utafiti wa nr7 (grid ya S1/S2). Hakuna dirisha jipya lililofunguliwa hapa; HOLDOUT + sealed 2026-05+ hazijaguswa.
3. **Pips vs R:** XAUUSD ina pip 0.01 — EV_pips ya pairs zote inatawaliwa na gold. Hukumu = EV_R (dimensionless); safu ya FX-pekee ndiyo inayolinganishwa na KAIROS-1/2.
4. **trades/mwaka** = Σ ya per-pair (n_i / miaka_i) — pairs zinatradiwa SAMBAMBA; risk-engine (max_slots/correlated) itapunguza idadi halisi inayotekelezwa.
5. **Kanuni ya `pairs[]` haithibitishi pair yoyote OOS.** Ni screen ya sign-consistency (train NA valid) + N — inapunguza selection bias, HAIIONDOI. Uthibitisho = holdout/forward.
6. **B_eff** ya bootstrap inapunguzwa kutoka 10,000 kadri N inavyokua (RAM: array (B×N) ya _stationary_indices; sakafu 1,000). Engine na mean_block hazijabadilika.

*reuse-only: episodes/_mask_context/pvalue_boot/load_window/_r_normalize/pool_streams/_boot_ci ni imports (ZERO changes). Profitable != Tradable Edge. Protect capital first.*