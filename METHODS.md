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
| 9 | **Volatility Expansion** (ATR squeeze→expansion) | vol ndogo (squeeze) → expansion + move | JPY-crosses (EURJPY); *GBPJPY/XAUUSD/NAS100 nje ya data* | ⬜ intraday |
| 10 | **London Open Breakout** | liquidity inaingia London → breakout ya range ya Asia | GBPUSD, EURUSD | ⬜ intraday/session |
| 11 | **Asian Range Breakout** | range tulivu ya Asia → breakout | EURJPY; *GBPJPY/AUDJPY nje ya data* | ⬜ intraday/session |
| 12 | **Pullback to Value Area** (trend continuation) | trend hu-pullback kwa value kabla ya kuendelea | USDJPY, EURUSD | ⬜ (trend-refined) |
| 13 | **Correlation Divergence** ⟵ *= #2* | corr pairs zikitofautiana → zinarudiana | EURUSD–GBPUSD, AUDUSD–NZDUSD | ⬜ **kipaumbele** |
| 14 | **Commodity-linked Trend** ⟵ *= #6 refined* | commodity flows → trend halisi | AUDUSD, USDCAD, NZDUSD | ⬜ |
| 15 | **Yield Differential Trend** ⟵ *= #7 carry* | rate differential = FX risk premium | USDJPY; *AUDJPY/NZDJPY nje ya data* | ⬜ (inahitaji rate data) |
| 16 | **Volatility Mean-Reversion** ⟵ *= #1 conditional* | vol ikiwa extreme → bei inarudi | EURGBP; *EURCHF nje ya data* | ⬜ (extension ya EURGBP) |

> **Data scope:** pairs zetu 9 = EURUSD, GBPUSD, USDJPY, EURJPY, USDCAD, USDCHF, AUDUSD,
> NZDUSD, EURGBP. Instruments *nje ya data* (GBPJPY, XAUUSD, NAS100, AUDJPY, EURCHF) zinahitaji
> kuongeza data (Dukascopy inazo) — tunaweza, ukitaka. Kwa sasa tunapima mbinu kwenye pairs 9.
>
> **Intraday (#9/10/11):** zinatumia 1m–30m + session (tunazo candles, hatujazitumia bado).

## Mpangilio wa kupima (kipaumbele — baada ya kuongeza #9–16)
1. **#2/#13 Cross-pair spread MR / Correlation Divergence** — wote tumeichagua; mantiki kubwa (corr 0.85), tuna D1 data. **Anza hapa.**
2. **#16 Volatility Mean-Reversion (EURGBP)** — extension ya haraka ya edge iliyothibitishwa.
3. **#10/#11 Intraday breakouts** (London/Asian) — mwelekeo mpya, tuna 1m–30m data, tofauti kabisa.
4. **#3 Breakout (Donchian D1)** · **#4 Structure** (swings/range position).
5. **#12 Pullback** · **#14 Commodity trend** (conditional).
6. **Zinahitaji data ya ziada:** #9 (XAUUSD/NAS100/GBPJPY), #15/#7 (rate data za carry).

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
