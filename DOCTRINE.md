# DOCTRINE YA MFUMO — EliteFX

*Hii ndiyo **katiba** ya mfumo: falsafa, architecture, na sheria — zilizojengwa juu ya
**uthibitisho wa data**, sio nadharia. Inaongoza maamuzi yote. Inasimamia juu ya
exploratory docs zilizopita (zimefutwa; historia iko git). Kanuni kuu:
**hakuna kinachoenda mbele bila kuthibitishwa kwa data.***

---

## 1. Falsafa ya msingi

1. **Soko ni PROBABILISTIC, sio deterministic.** Hatusemi "itapanda"; tunasema "ina
   nafasi kubwa zaidi, ndani ya muktadha huu."
2. **Hatutabiri mwelekeo.** Tunafanya: **tambua hali (regime) → tathmini signal →
   conditional probability → chuja uamuzi (trade/skip).**
3. **Edge inatoka kwenye FILTERING + RISK MANAGEMENT**, sio kwenye utabiri wa direction.
4. **Kila kitu kinathibitishwa kwa data** kabla ya kujengwa juu yake.

---

## 2. Yale DATA imetufundisha (msingi wa doctrine — usipingane na haya)

| Ugunduzi | Hali | Ushahidi |
|----------|------|----------|
| ⭐ **Volatility = edge pekee thabiti** | imethibitishwa | IC 0.19 (9/9 pairs); vol clustering ACF r²>0 → **persistent** |
| ❌ **Mwelekeo (trend) haupatikani** | imethibitishwa | EMA slope, price-vs-EMA, momentum, **MTF alignment**, ER/vol-conditioned — zote ~0.50 (sarafu) |
| 🟡 **Mean-reversion kwenye extremes** | lead dhaifu | D1 range-pairs (AUDUSD/EURGBP p=0.0002 baada ya cost+Phase B); **inahitaji OOS** |
| ❌ **`volume_imbalance` haitabiri** | imethibitishwa | IC≈0, hit<0.50, bars 250k+ |
| **Returns ni fat-tailed; regimes ni halisi** | imethibitishwa | excess kurtosis (Student-t); ACF r²>0 |
| **HTF alignment = context, SIO edge** | imethibitishwa | Test #1: \|align\|=4 → win 0.503 |

> **Hitimisho la data:** edge ya uhakika iko kwenye **VOLATILITY/regime**, sio mwelekeo.
> Data yetu (OHLC + tick volume) ina muundo wa **volatility**, sio directional alpha.

---

## 3. Architecture ya "brain" (layers 4)

```
1. REGIME DETECTION      hali ya sasa: vol-state × structure-state
        │                (TREND / RANGE / HIGH-VOL / LOW-VOL)
        ▼
2. SIGNAL EVALUATION     ubora wa setup (score 0→1) — sio blind
        │
        ▼
3. CONDITIONAL PROBABILITY   P(win | regime + signal) ← HAPA NDIPO EDGE
        │
        ▼
4. DECISION LAYER        IF P > threshold → TRADE; ELSE → SKIP (meta-labeling)
```

**Strategy switching:** `IF regime==RANGE/LOW-VOL → mean-reversion logic; IF
regime==TREND/HIGH-VOL → breakout logic.` (Sio strategy moja kila wakati.)

**Multi-timeframe:** HTF = **context** (lazima ithibitishwe inaongeza edge, sio
assumption); LTF = **execution.** Alignment SI signal.

---

## 4. Majukumu ya Models (reframed)

| Tabaka | Jukumu (mpya) |
|--------|----------------|
| **Model 1** | **Regime/Context Detector** — *"soko liko hali gani SASA?"* (NIYO, sio mwelekeo). Output = muktadha kwa Model 2. |
| **Model 2** | **Signal + conditional decision** (trade/skip) ndani ya regime. Mean-reversion/breakout kulingana na regime. |
| **Sizing / Compliance / R1–R7** | Hazibadiliki — risk framework (ona §4b). Edge halisi iko HAPA + filtering. |

### 4b. Trade & Risk Management — KAMA TULIVYOKUBALIANA AWALI (hazibadiliki)

Reset hii inahusu **utafutaji wa edge/strategy (Model 1 & 2) PEKEE.** Tabaka za **kusimamia
pesa & hatari zinabaki KAMA zilivyo kwenye MFUMO.md** — hazina mjadala mpya:

| Tabaka | Kinachobaki (MFUMO.md) |
|--------|------------------------|
| **Sizing (Sehemu 4)** | **DailyRiskBudgetSizer** — bajeti ya siku inayobadilika (win/loss factor), gawa kwa slots, lotsize kutoka SL. Japhet anaweka values. |
| **Compliance (Sehemu 5)** | **Checks 5** (Daily Loss, Total DD, Slots, Correlation, Spread) — **mamlaka ya juu**, worst-case exposure, logi ya kila uamuzi. |
| **Trade Mgmt (Sehemu 6)** | **R1–R7** (breakeven, partial exit, trailing, TP reduce/extend, regime exit, time-stop). Hujaribiwa moja-moja kabla ya kuchanganya. |
| **FTMO Rules (Sehemu 8)** | +10% target, −5% daily, −10% total, min siku 4 — high-water-mark. |

> **Mstari usiovukwa (kanuni ya awali):** **ML inatabiri/inatambua muktadha (Model 1, 2);
> RULES zinasimamia pesa (Sizing, Compliance, R1–R7).** Compliance ikisema "hapana", trade
> haifunguki — hata kama signal ni nzuri kiasi gani. Hili **halibadiliki.**

---

## 5. Doctrine ya kuthibitisha edge (lazima ipite YOTE)

1. **Phase B** — permutation null (circular-shift): inazidi bahati?
2. **Stability** — thabiti kwa **≥60% pairs**, **≥2 TF**, NA **sub-periods** (2016–2020 vs 2021–2024).
3. **Cost** — inaokoka **spread halisi** (round-trip).
4. **OOS** — inaishi **2025+ holdout** (gusa **MARA MOJA**, mwishoni, bila tuning).
5. **Labels** — Triple-Barrier (ATR-based) + **Purged/Embargoed CV** (kuepuka leakage).

**Reality check:** win-rate ~**52–58%** = "nzuri." Profit = filtering + risk mgmt, sio win-rate kubwa.

---

## 6. Kanuni za kuepuka overfit (chuma)

1. **Moja-moja** — pima feature/signal moja kwa wakati.
2. **Phase B gate** kila dai.
3. **Holdout 2025+ takatifu** — mara moja mwisho.
4. **Chache na imara** > nyingi dhaifu; kila feature iwe na **mantiki ya kiuchumi**.
5. **Meta-overfitting:** hesabu jaribio ZOTE za mradi; kujaribu vingi = njia ya siri ya overfit.
6. **Simplest-first:** Logistic → LightGBM. **Transformer baadaye TU** ikishinda OOS+Phase B.

---

## 7. Mbinu TUSIZOTUMIA (anti-patterns — zimethibitishwa kushindwa au hatari)

- ❌ Pure indicator signals (RSI/MACD/EMA blindly)
- ❌ Simple MTF alignment kama signal ("zote juu → buy")
- ❌ Direct direction prediction
- ❌ Kitchen-sink ML / Transformer-first (overfit)
- ❌ Kuamini blueprint bila kuthibitisha kila layer kwa data

---

## 8. Msingi wa data (SEHEMU 1 — imara, hauguswi)

Candles 45M (pairs 9 × TF 8), CET-aligned, no-lookahead, kupitia `dataset.py`.
Features zilizopo: OHLC, volume/imbalance, spread, returns, volatility⭐, EMA/slope,
ADX, ER, position-in-range, Hurst. Rejea `DATA_GUIDE.md`.

---

## 9. Hali ya sasa & hatua inayofuata

- **Imethibitishwa:** vol-regime (msingi wa Model 1).
- **Lead:** mean-reversion (range/low-vol; inahitaji OOS).
- **Inayofuata:** jenga **Regime Detector** (vol × structure) → kisha **conditional-probability
  validation** ya signals ndani ya kila regime (layer 3) — kwa nidhamu ya Sehemu 5 hapo juu.

> *Doctrine hii inasasishwa pale tu data mpya inathibitisha. Sio maoni — ni makubaliano
> yaliyojengwa kwa ushahidi.*
