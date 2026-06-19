# Trend Structure #3 — Fade-Extreme (Mean-Reversion) + Cost + Phase B

*Imezalishwa: 2026-06-19 18:58 | fade |price_vs_ema|≥q80 | NET = baada ya round-trip spread | circular-shift perm N=5000 | non-overlapping*

> Signal: bei extreme juu→SHORT, extreme chini→LONG (fade). p_sh<0.05 NA net>0 = edge halisi baada ya gharama. Hii ni lead pekee iliyojirudia.


## D1 (fwd=5)

| Pair | n | gross | cost | **net** | win(net) | p_sh | edge? |
|------|---|-------|------|---------|----------|------|-------|
| EURUSD | 100 | -0.00050 | 0.00007 | **-0.00058** | 0.530 | 0.8118 | ❌ |
| GBPUSD | 100 | +0.00200 | 0.00018 | **+0.00182** | 0.580 | 0.0344 | ✅ |
| USDJPY | 100 | -0.00006 | 0.00010 | **-0.00016** | 0.430 | 0.0492 | ❌ |
| EURJPY | 100 | +0.00181 | 0.00013 | **+0.00167** | 0.540 | 0.4007 | ❌ |
| USDCAD | 100 | +0.00075 | 0.00022 | **+0.00054** | 0.550 | 0.2126 | ❌ |
| USDCHF | 100 | +0.00198 | 0.00034 | **+0.00163** | 0.600 | 0.0732 | ❌ |
| AUDUSD | 100 | +0.00285 | 0.00031 | **+0.00253** | 0.590 | 0.0002 | ✅ |
| NZDUSD | 100 | +0.00297 | 0.00043 | **+0.00254** | 0.610 | 0.0312 | ✅ |
| EURGBP | 100 | +0.00404 | 0.00025 | **+0.00379** | 0.640 | 0.0002 | ✅ |

## H4 (fwd=10)

| Pair | n | gross | cost | **net** | win(net) | p_sh | edge? |
|------|---|-------|------|---------|----------|------|-------|
| EURUSD | 319 | +0.00026 | 0.00007 | **+0.00018** | 0.495 | 0.2364 | ❌ |
| GBPUSD | 319 | +0.00064 | 0.00018 | **+0.00046** | 0.536 | 0.1170 | ❌ |
| USDJPY | 319 | -0.00019 | 0.00010 | **-0.00029** | 0.486 | 0.6363 | ❌ |
| EURJPY | 319 | +0.00039 | 0.00014 | **+0.00025** | 0.539 | 0.1248 | ❌ |
| USDCAD | 319 | +0.00044 | 0.00020 | **+0.00025** | 0.498 | 0.0676 | ❌ |
| USDCHF | 319 | +0.00031 | 0.00028 | **+0.00003** | 0.480 | 0.2767 | ❌ |
| AUDUSD | 319 | +0.00104 | 0.00033 | **+0.00072** | 0.545 | 0.0136 | ✅ |
| NZDUSD | 319 | +0.00064 | 0.00040 | **+0.00025** | 0.508 | 0.1474 | ❌ |
| EURGBP | 319 | +0.00062 | 0.00027 | **+0.00035** | 0.549 | 0.0666 | ❌ |

---
*gross = fade return kabla ya cost; net = baada ya round-trip spread. **✅ inahitaji p_sh<0.05 NA net>0** (significant NA inalipa baada ya gharama). Kama net hasi licha ya gross+ve → spread inakula edge (hasa TF ndogo). Kama ✅ kwa pairs nyingi → mean-reversion ni edge halisi ya mwelekeo (sio trend).*