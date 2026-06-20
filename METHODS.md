# CANDIDATE METHODS — Pair × Mbinu Map (research)

*Mtazamo: kila pair ina mbinu zinazo-IFAA (mean-reversion → EURGBP; nyingine → breakout/
carry/spread). Tunajenga **ramani ya pair × mbinu** kwa kupima MOJA-MOJA, kwa nidhamu.
Tunaongozwa na DOCTRINE.md.*

## Kanuni (kuepuka overfit)
1. **Kila mbinu = hypothesis ya kiuchumi** (kwa nini iwe na edge) — sio blind search.
2. **Moja-moja:** Phase B + sub-period stability + parameter-robustness (kama EMA) + cost.
3. **OOS 2025+ takatifu** — gusa mara moja, mwishoni, kwa survivors.
4. **Tarajia wengi watashindwa.** Multiple-testing: kila mbinu mpya = jaribio jingine.

## Methods (kila moja: mantiki + pairs zinazofaa + status)

| # | Mbinu | Mantiki ya kiuchumi | Pairs zinazofaa | Status |
|---|-------|---------------------|-----------------|--------|
| 1 | **Mean-reversion** (fade extreme kutoka mean ndefu) | range-bound pairs huzunguka mean (hakuna macro driver mkali) | range/cross (EURGBP) | ✅ **EURGBP** (EMA100/200) |
| 2 | **Cross-pair spread MR** (mf. AUDUSD−NZDUSD) | pairs correlated (0.85) → spread yao hu-mean-revert hata kama kila moja haitabiriki | AUDUSD-NZDUSD, EUR/GBP/USD | ⬜ **kipaumbele** |
| 3 | **Breakout** (Donchian range break) | range ikivunjika → vol expansion + momentum | mixed; HIGH-vol regime | ⬜ |
| 4 | **Structure** (swings HH/LL, position-in-range) | bei inaheshimu levels (sio mistari ya MA) | mixed | ⬜ |
| 5 | **Regime-switched** (MR low-vol, breakout high-vol) | regime tofauti hupendelea strategy tofauti | zote (kupitia Model 1) | ⬜ |
| 6 | **Trend conditional** (momentum ndani ya macro regime) | carry/commodity flows huleta trends za kweli | USDJPY, AUD/NZD/CAD | ⬜ (generic FAILED; conditional untested) |
| 7 | **Carry** (rate differential) | FX risk premium (documented) | AUDJPY, NZDJPY (high vs low yield) | ⬜ (inahitaji rate data) |
| 8 | **Session/time-of-day** | liquidity/flow patterns kwa session | intraday (1m–30m) | ⬜ (intraday) |

## Mpangilio wa kupima (kipaumbele)
1. **#2 Cross-pair spread MR** — mantiki kubwa (corr 0.85 tunayo), tuna data, tofauti kabisa. **Anza hapa.**
2. **#3 Breakout** — mbinu tofauti na MR/trend.
3. **#4 Structure** — price-action, untested.
4. **#5 Regime-switched** — inatumia Model 1.
5. #6–#8 baadaye (#7 inahitaji rate data; #8 ni intraday).

## Pair → Method map (inajazwa kadri tunavyopima)

| Pair | Mbinu iliyothibitishwa |
|------|------------------------|
| EURGBP | ✅ Mean-reversion (D1) |
| AUDUSD | ? |
| NZDUSD | ? |
| GBPUSD | ? |
| EURUSD | ? |
| USDJPY | ? |
| EURJPY | ? |
| USDCAD | ? |
| USDCHF | ? |

> **Lengo:** kila pair ipate mbinu yake (au ikubaliwe haina edge). Survivors za rigor +
> OOS ndizo zinazoingia mfumo. Hii ndiyo "specialist per pair" — kwa **ushahidi, sio dhana.**
