# Viability — EURGBP MR Monte Carlo FTMO Pass-Rate

*Imezalishwa: 2026-06-20 17:27 | trades=59 (7/mwaka) | R-mult mean=+0.386, win=0.59 | sims=5000 | FTMO: +10%/−5%day/−10%total | bootstrap IID*

> DOCTRINE target: **pass-rate ≥ 60%.** Pia angalia muda (trades→years) wa kupita.

| Risk/trade | PASS% | fail daily | fail total | timeout | median trades→pass | ≈ years |
|-----------|-------|-----------|-----------|---------|--------------------|---------|
| 0.5% | **98.6%** | 0.0% | 0.1% | 1.3% | 45.0 | 6.9 |
| 1.0% | **96.6%** | 0.0% | 3.3% | 0.0% | 21.0 | 3.2 |
| 1.5% | **90.2%** | 0.0% | 9.8% | 0.0% | 12.0 | 1.8 |
| 2.0% | **74.5%** | 17.1% | 8.3% | 0.0% | 8.0 | 1.2 |
| 3.0% | **57.0%** | 39.1% | 3.9% | 0.0% | 4.0 | 0.6 |

---
*EURGBP MR ina **trades ~7/mwaka** (chache — pair moja, D1). PASS% ≥60% kwa risk fulani = mfumo viable kwa edge moja. Lakini angalia **years** — kama kupita kunahitaji miaka mingi, ni polepole mno kivitendo → tunahitaji pairs/edges zaidi. Bootstrap ni IID (haijumuishi clustering). Risk kubwa = pass haraka lakini fail-total juu. 2025+ HAIJAGUSWA.*