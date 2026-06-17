# Feature Diagnostics — EliteFX SEHEMU 1

*Imezalishwa: 2026-06-17 22:59 | Uthibitisho wa kitakwimu kabla ya modeling*

## 1. Distribution Moments (D1 log-returns) — je HMM ya Gaussian ni sahihi?

| Pair | Mean % | Std % | Skewness | Excess kurtosis | Min % | Max % |
|------|--------|-------|----------|-----------------|-------|-------|
| EURUSD | 0.003 | 0.457 | 0.04 | 2.07  ⬅️ fat tails | -2.96 | 2.15 |
| GBPUSD | -0.0029 | 0.592 | -1.55 | 25.92  ⬅️ fat tails | -9.4 | 3.14 |
| USDJPY | 0.0102 | 0.577 | -0.55 | 4.81  ⬅️ fat tails | -4.37 | 2.94 |
| EURJPY | 0.0132 | 0.556 | -1.06 | 12.98  ⬅️ fat tails | -7.16 | 2.5 |
| USDCAD | -0.0009 | 0.429 | -0.09 | 1.54  ⬅️ fat tails | -1.96 | 2.01 |
| USDCHF | -0.0092 | 0.468 | -0.48 | 3.5  ⬅️ fat tails | -3.68 | 2.18 |
| AUDUSD | 0.0001 | 0.626 | -0.24 | 2.85  ⬅️ fat tails | -4.66 | 3.35 |
| NZDUSD | -0.005 | 0.629 | -0.11 | 1.42  ⬅️ fat tails | -3.61 | 2.67 |
| EURGBP | 0.0059 | 0.451 | 1.33 | 17.96  ⬅️ fat tails | -2.07 | 6.47 |

*Normal: skew=0, excess kurtosis=0. **9/9** zina excess kurtosis > 1 (fat tails) kwenye returns **ghafi**. LAKINI: HMM yenye states nyingi ni *Gaussian mixture* — yenyewe ina fat tails. Kwa hiyo kurtosis ghafi PEKEE hairuhusu kuamua Student-t. **Uamuzi unategemea Section 2 (conditional normality).** Skew hasi = matukio ya kuanguka makubwa kuliko ya kupanda.*

## 2. Conditional Normality — je tunahitaji Student-t, au vol-scaling inatosha?

> Swali: HMM (Gaussian mixture) yenyewe ina fat tails. Tunastandardize returns kwa **rolling-vol (20-bar, no-lookahead)** kisha tunapima kurtosis tena. Kama bado kubwa → fat tails ni za kweli → **Student-t**. Kama inashuka karibu 0 → **vol-clustering ndio chanzo → Gaussian HMM inatosha** (hakuna haja ya Student-t).

| Pair | Excess kurt (raw) | Excess kurt (vol-std) | %\|z\|>3σ | %>4σ | %>5σ |
|------|-------------------|-----------------------|---------|------|------|
| EURUSD | 2.07 | 1.66  ⬅️ bado fat | 1.114 | 0.26 | 0.074 |
| GBPUSD | 25.92 | 5.09  ⬅️ bado fat | 1.003 | 0.297 | 0.186 |
| USDJPY | 4.81 | 4.1  ⬅️ bado fat | 1.56 | 0.446 | 0.223 |
| EURJPY | 12.98 | 6.26  ⬅️ bado fat | 1.04 | 0.334 | 0.149 |
| USDCAD | 1.54 | 2.01  ⬅️ bado fat | 1.151 | 0.186 | 0.0 |
| USDCHF | 3.5 | 2.6  ⬅️ bado fat | 0.78 | 0.371 | 0.111 |
| AUDUSD | 2.85 | 2.45  ⬅️ bado fat | 1.151 | 0.26 | 0.111 |
| NZDUSD | 1.42 | 0.98 | 0.817 | 0.111 | 0.074 |
| EURGBP | 17.96 | 3.5  ⬅️ bado fat | 1.263 | 0.334 | 0.111 |

*Gaussian inatarajia: |z|>3σ = **0.27%**, >4σ = **0.006%**, >5σ = **0.00006%**. Observed kubwa zaidi = fat tails. **Excess kurt (vol-std)** ndio uamuzi: **8/9** bado zina > 1 baada ya vol-scaling. Kama nyingi bado fat → **Student-t emissions**. Kama zimeshuka ~0 → **Gaussian HMM + vol-standardized returns inatosha** (model rahisi).*

## 3. Volatility Clustering — ACF ya r² (huhalalisha regime/HMM)

| Pair | ACF r (lag1) | ACF r² lag1 | lag5 | lag10 | lag20 |
|------|--------------|-------------|------|-------|-------|
| EURUSD | 0.002 | **0.099** | 0.12 | 0.028 | 0.031 |
| GBPUSD | 0.026 | **0.146** | 0.024 | 0.027 | 0.008 |
| USDJPY | -0.015 | **0.126** | 0.072 | 0.039 | 0.019 |
| EURJPY | -0.034 | **0.114** | 0.013 | 0.012 | 0.004 |
| USDCAD | -0.004 | **0.143** | 0.104 | 0.098 | 0.036 |
| USDCHF | 0.016 | **0.095** | 0.22 | 0.014 | 0.043 |
| AUDUSD | -0.007 | **0.161** | 0.098 | 0.072 | 0.069 |
| NZDUSD | 0.001 | **0.148** | 0.116 | 0.068 | 0.063 |
| EURGBP | 0.01 | **0.146** | 0.034 | 0.025 | 0.007 |

*ACF ya r (returns) ≈ 0 = soko efficient (hakuna mean-reversion rahisi). ACF ya r² > 0 = **vol clustering** (vol kubwa inafuatwa na vol kubwa) → regimes zipo → **HMM/Model 1 ina msingi.** 9/9 zina ACF r² lag1 > 0.05.*

## 4. `volume_imbalance` IC — je inatabiri return ya bar inayofuata? (Model 2)

> NO-LOOKAHEAD: imbalance ya bar `t` (inajulikana baada ya t kufunga) dhidi ya return ya bar `t+1` (lead). Contemporaneous = ndani ya bar `t` (sanity).

| Pair | TF | Contemp. corr | **Predictive IC** | Hit-rate (dir.) | n |
|------|----|---------------|-------------------|-----------------|---|
| EURUSD | 15m | 0.069 | **0.0029** | 0.4942 | 251,738 |
| EURUSD | 30m | 0.0588 | **0.0031** | 0.4959 | 125,883 |
| GBPUSD | 15m | 0.0571 | **0.0007** | 0.494 | 251,721 |
| GBPUSD | 30m | 0.0498 | **0.0012** | 0.4946 | 125,878 |
| USDJPY | 15m | 0.0217 | **0.003** | 0.4939 | 251,846 |
| USDJPY | 30m | -0.0046 | **0.0035** | 0.4978 | 125,929 |
| EURJPY | 15m | 0.0308 | **-0.001** | 0.4938 | 251,805 |
| EURJPY | 30m | 0.0112 | **0.0008** | 0.497 | 125,917 |
| USDCAD | 15m | 0.1013 | **0.0052** | 0.4955 | 251,633 |
| USDCAD | 30m | 0.0921 | **0.004** | 0.4987 | 125,841 |
| USDCHF | 15m | 0.0509 | **-0.0011** | 0.4895 | 251,639 |
| USDCHF | 30m | 0.0385 | **-0.0** | 0.4937 | 125,854 |
| AUDUSD | 15m | 0.0895 | **0.0015** | 0.4926 | 251,791 |
| AUDUSD | 30m | 0.0693 | **-0.0006** | 0.4952 | 125,909 |
| NZDUSD | 15m | 0.1123 | **0.0058** | 0.4947 | 251,714 |
| NZDUSD | 30m | 0.1017 | **0.0034** | 0.4962 | 125,897 |
| EURGBP | 15m | 0.0598 | **0.0015** | 0.4905 | 251,789 |
| EURGBP | 30m | 0.0462 | **-0.0005** | 0.4933 | 125,909 |

*Contemp. corr +ve = imbalance inaakisi move ya bar yenyewe (sanity). **Predictive IC** ndio muhimu: ≈0 = haina thamani ya kutabiri; |IC|≥0.02 thabiti kwa pairs = ina edge ndogo (FX microstructure IC huwa ndogo). Hit-rate > 0.50 = mwelekeo sahihi zaidi ya nasibu. **Kama IC≈0 kote → Model 2 isitegemee imbalance kama feature kuu.**

## 5. Correlation Stability — je groups za static zinafaa? (Compliance)

| Jozi | 2016–2020 | 2021–2026 | Δ (drift) |
|------|-----------|-----------|-----------|
| AUDUSD–NZDUSD | 0.8 | 0.89 | 0.09 |
| EURUSD–USDCHF | -0.78 | -0.76 | 0.02 |
| GBPUSD–EURGBP | -0.74 | -0.47 | 0.27  ⬅️ unstable |
| EURJPY–EURGBP | -0.08 | 0.18 | 0.26  ⬅️ unstable |
| EURUSD–GBPUSD | 0.57 | 0.78 | 0.21  ⬅️ unstable |
| USDJPY–USDCHF | 0.53 | 0.58 | 0.05 |

*Δ kubwa = correlation INABADILIKA kwa muda → groups za static (config) hazitoshi. **Ushauri (Sehemu 5):** tumia rolling correlation au net-currency exposure badala ya makundi ya kudumu yaliyowekwa kwa mkono.*
