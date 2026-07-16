# WAVE-M — S2 VALIDATION REGISTRATION (FROZEN by Chief, 2026-07-15)

> **Pre-registration ya S2.** HM-02 ORB imekufa TRAIN (gross hasi pairs 5/5 — mechanism verdict,
> kill safi). S2 hii = **HM-05 ALIGNED-SHOCK × USDJPY × 15m, cells 4 PEKEE** (zote TRAIN net+).
> FROZEN kabla ya kufungua VALIDATION. HOLDOUT HAIGUSWI.

## Uaminifu kamili (LESSON-040 — jaribio la TATU la single-pair)
Kesi mbili za nyuma za "pair-bora ya TRAIN" zilifeli OOS (HC2-03 EURUSD; HB2-10 EURCHF). Hii ni
ya tatu — na expectations ziko chini ipasavyo. **Tofauti za kesi hii (zilizoandikwa KABLA ya
VALIDATION):**
1. **Margin ya gharama 3.8×** (gross +1.56 vs cost ~0.41; cost_share 0.26) — kesi zilizofeli
   zilikuwa ~2× (cost_share 0.50–0.80). Edge ndogo-karibu-na-gharama ndiyo iliyokufa mara mbili;
   hii ina nafasi zaidi ya kunusurika shrinkage (~0.35 slope ingeacha net ~+0.4 bado chanya).
2. **N=730 per cell** (mara 2.4 ya EURCHF 299) — estimate imara zaidi.
3. **Breadth ya mechanism kwenye gross:** 3/4 pairs chanya (USDJPY, GBPJPY, XAUUSD) — mechanism
   ya shock-continuation ina uhai zaidi ya pair moja; ni NET ndiyo inayochujwa na gharama.
4. Mechanism ni CONTINUATION (aina ya STRAT-001/002) — si reversion iliyofeli 0/6.
Bado: hoja hizi zote ni za TRAIN (correlated evidence — LESSON-040). **VALIDATION ndiyo mwamuzi.**

## Cells FROZEN (4) — HM-05 × USDJPY × 15m
| # | trigger | SL | TP | max_hold | TRAIN EV_net (rejea) |
|---|---------|----|----|----------|----------------------|
| 1 | shock_follow (len20,k3,rearm10) | 1.5 | 2.0 | 16 | +1.263 (N=730) |
| 2 | shock_follow | 1.0 | 2.0 | 16 | +1.114 (N=730) |
| 3 | shock_follow | 1.5 | 3.0 | 16 | +0.709 (N=725) |
| 4 | shock_follow | 1.0 | 3.0 | 16 | +0.568 (N=729) |

Context (signal-bar i): `allow_long = isfinite(d1_trend_sign) & d1_trend_sign==+1 & 7<=hour<=16`;
mirror short. NaN → excluded.

## Test (RASMI)
- Window: **VALIDATION 2023–2024**. Kila cell → `pvalue_boot` (B=50k, mean_block=3, engine RASMI)
  → **BH-FDR q=0.10, m=4**. Survivor = fdr_pass NA EV_net>0. p_z sensitivity tu.
- Cells 4 zina-correlate (trigger mmoja, SL/TP tofauti) — BH inabaki valid (conservative).

## Kando (SI sehemu ya S2 hii — kumbukumbu ya wave ijayo)
- **Gold-momentum @ HTF:** XAUUSD shock gross **+11.5** @15m (mechanism inafanya kazi kwenye gold
  kama LESSON-039 ilivyodokeza — continuation ndio mtindo wa gold) lakini spread ~36 inameza.
  Hypothesis halali ya baadaye: shock/momentum ya gold kwenye **H1/H4** (ATR kubwa → gross kubwa
  vs spread ile ile). Inahitaji registration mpya — HAIJUMUISHWI hapa.
- HM-02 ORB: DEAD (gross 5/5 hasi) — hakuna revisit bila design mpya kabisa.

## Matokeo yanayowezekana (yote halali)
- **Survivor:** → C2-6 freeze + HOLDOUT one-shot → ikipita = **STRAT-003** (shock-continuation USDJPY).
- **Hakuna survivor:** momentum-@-intraday single-pair pia imefungwa → uamuzi wa PD: gold-HTF arm /
  OOB / consolidation.
