# Trend Patterns & Structures — Model 1 (kwa ML kujifunza)

*Catalog ya **patterns/structures zote** ambazo ML (Model 1) itajifunza kwa **kutambua
trend**, pamoja na **mantiki, formula, na jinsi ya kupima kila moja**. Kanuni kuu:
**kuepuka overfit** — tunapima MOJA-MOJA, tunathibitisha kabla ya kuongeza. Rejea:
`MODEL1_FEATURES.md`, `DIAGNOSTICS_DECISIONS.md`.*

**Timeframes:** D1, H4, H2, H1.

---

## 0. Thesis & kanuni za kuepuka overfit

**Thesis:** mwelekeo **peke yake** ni dhaifu (tumethibitisha: trend-following no edge).
Edge ya kweli — kama ipo — iko kwenye **mwelekeo ULIOWEKEWA MASHARTI:** *"trend up, NA
trend ni safi (sio chop), NA TF zinakubaliana, NA regime inaruhusu."* ML inajifunza
kuchanganya masharti haya — mtu hawezi kwa if/else.

**Kanuni 8 za kuepuka overfit:**
1. **Moja-moja:** pima structure moja kwa wakati; usichanganye zote (kitchen-sink = overfit).
2. **Phase B gate:** kila dai lazima lipite permutation null (vinginevyo ni bahati/spurious).
3. **Train/OOS:** funza 2016–2024; **2025+ ni holdout — usiguse hadi mwisho.**
4. **Chache na imara** > nyingi dhaifu.
5. **Kila feature iwe na MANTIKI ya kiuchumi**, sio statistical tu (data-mining = overfit).
6. **Conditioners** zinapimwa kwa *subset-edge* (sio kutafuta threshold bora — hiyo ni overfit).
7. **Multiple-testing:** tegemea false positives; hitaji ushahidi ZAIDI ya bahati.
8. **Meta-overfitting (research process):** kila mbinu/feature mpya tunayojaribu = jaribio
   jingine. **Hesabu jaribio ZOTE** za mradi mzima; holdout 2025+ ni **takatifu** — gusa
   mara MOJA mwishoni, bila tuning. (Kujaribu mbinu nyingi = njia ya siri ya overfit.)

**Aina mbili za features (zinapimwa tofauti):**
- **Directional** — zenyewe zinatabiri mwelekeo. *Pima:* rank-IC vs forward signed return + Phase B.
- **Conditioner** — hazitabiri mwelekeo, bali zinaeleza **LINI** directional ina edge.
  *Pima:* gawa data kwa (high/low ya conditioner), angalia kama directional-edge **inaboreka** kwenye subset moja.

---

## A. DIRECTION (mwelekeo)

| # | Pattern | Formula | Mantiki | Status |
|---|---------|---------|---------|--------|
| A1 | MA slope (EMA 20/50/200) | `EMA_p[t]/EMA_p[t−k] − 1` | trend inaendelea | EMA200 ✓ dhaifu |
| A2 | Price vs MA | `(close − EMA_p)/EMA_p` | juu/chini ya trend | ✓ extremes→mean-rev |
| A3 | MA crossover | `EMA_fast − EMA_slow` (norm. kwa ATR) | fast ikipita slow = regime mpya | ⬜ |
| A4 | MA ribbon alignment | score: `+1 EMA20>EMA50>EMA200; −1 reverse; 0 mchanganyiko` | trend kamili wa scales zote | ⬜ |

## B. STRENGTH / QUALITY (ubora — trend safi vs chop)

| # | Pattern | Formula | Mantiki | Status |
|---|---------|---------|---------|--------|
| B1 | ADX (+DI/−DI) | Wilder | nguvu ya trend | ✓ dhaifu |
| B2 | **Efficiency Ratio** (Kaufman) | `\|close_t−close_{t−n}\| / Σ\|close_i−close_{i−1}\|` ∈[0,1] | 1=trend safi, 0=chop | 🆕 **conditioner muhimu** |
| B3 | Regression slope + **R²** | OLS ya close juu ya muda, window n | slope=mwelekeo, R²=usafi | 🆕 |
| B4 | ATR / realized range | `mean(TR, n)` | ukubwa wa moves | ✓ |

## C. REGIME (muktadha)

| # | Pattern | Formula | Mantiki | Status |
|---|---------|---------|---------|--------|
| C1 | **Volatility** (rolling std) | `std(returns, n)` | HIGH/LOW vol | ⭐ **imethibitishwa (IC 0.19)** |
| C2 | **Hurst exponent** | R/S au DFA, window n | H>0.5 trending; H<0.5 mean-revert | 🆕 **conditioner muhimu** |
| C3 | Variance ratio | `Var(q-ret)/(q·Var(1-ret))` | >1 trending; <1 mean-revert | 🆕 |

## D. MULTI-TIMEFRAME (nguvu inayotarajiwa)

| # | Pattern | Formula | Mantiki | Status |
|---|---------|---------|---------|--------|
| D1 | **TF alignment** | jumla ya `sign(direction)` kwa D1+H4+H2+H1 (−4…+4) | trend wa kweli = scales zote zinakubaliana | 🆕 **kipaumbele** |
| D2 | HTF context | trend-state ya TF kubwa kama feature ya ndogo | top-down (falsafa ya MFUMO) | 🆕 |

## E. STRUCTURE (price action / swings)

| # | Pattern | Formula | Mantiki | Status |
|---|---------|---------|---------|--------|
| E1 | Higher-highs / Lower-lows | hesabu ya HH/HL vs LH/LL kwenye swings (rolling) | structure ya soko (sio MA) | 🆕 |
| E2 | Position in range | `(close − min_n)/(max_n − min_n)` ∈[0,1] | Donchian/stochastic position | 🆕 |
| E3 | Breakout | flag: new N-bar high/low | trend mpya unaanza | 🆕 |

---

## Protocol ya kupima (kila structure)

```
1. JENGA feature (no-lookahead: bar t inatumia past + current tu).
2. AINA?
   - Directional  -> rank-IC vs forward signed return (k=1) + Phase B permutation.
   - Conditioner  -> gawa data (high/low ya conditioner); je directional-edge
                     inaboreka kwenye subset moja? + Phase B kwenye subset.
3. GRADE: STRONG (Phase B p<0.05, thabiti pairs/TF) / WEAK / ❌.
4. UAMUZI: STRONG -> weka kwenye feature set ya ML. ❌ -> tupa (rekodi).
5. Train/OOS: matokeo ya train tu; OOS 2025+ inaguswa MWISHO.
```

**Acceptance:** STRONG/MOD kwa pairs/TF nyingi ZAIDI ya inavyotarajiwa kwa bahati
(multiple-testing). Conditioner "inafanya kazi" kama directional-edge kwenye subset
"nzuri" inazidi ile ya jumla kwa kiasi kinachopita Phase B.

## Maboresho kutoka peer-review (yamekubaliwa)

**Feature construction:**
- **Vol-normalize directional features** (slope ÷ ATR au rolling-std) → stationarity
  (ML isichanganye moves kubwa za regime tofauti).
- **Match window `n` ya feature na target horizon `k`** (usipime usafi wa bars 100 nyuma
  ukilenga bar 1 mbele).
- **Hurst / ER / Variance-ratio:** windows **kubwa (100–500)**, jaribu multi-window
  (20/50/100), angalia **stability**, sio IC tu (zina estimation noise kubwa).
- **Pick MOJA** ya Hurst/Variance-ratio (zinapima kitu kile kile → multicollinearity).
- **MTF alignment:** anza **equal-sum** (hakuna free params kuepuka overfit); **acha
  LightGBM ijifunze weights** — usitune kwa mkono.

**Validation (nyongeza):**
- **Non-linear:** feature ikifeli rank-IC LAKINI ina mantiki ya kiuchumi → pima
  **Mutual Information** + kama conditioner (usitupe haraka — rank-IC inakosa non-monotonic).
- **Stability check:** feature lazima iwe +ve kwa **≥60% ya pairs**, **≥2 TF**, NA thabiti
  kwenye **sub-periods** (2016–2020 vs 2021–2024) — vinginevyo overfit / regime-decay.
- **Interaction phase** (baada ya individual + Phase B): pima **trend-edge ndani ya**
  {high/low ER · high/low vol · aligned/misaligned TF}. **Hapa ndipo edge halisi.**

**Labels (kwa final model):**
- `k=1` ni clean lakini noisy. Hamia **`sign(Σ returns over k)`** au **Triple-Barrier**
  (TP/SL kwa ATR + timeout) ili kuondoa noise.
- **Meta-labeling:** lengo si "UP/DOWN" bali **"je signal itafanya kazi?"** (= conditioner
  thesis — kila mtu amefika hapa).
- ⚠️ **Triple-barrier/meta-label = overlapping & path-dependent → LAZIMA Purged + Embargoed
  CV** (Lopez de Prado), vinginevyo leakage. Pia long-`k` + features persistent =
  spurious-regression → tumia non-overlapping/permutation (`direction_edge.py`).

**Model:** Logistic (baseline) → **LightGBM** (non-linear interactions + overfit control).
**Transformer baadaye TU** ikishinda LightGBM kwenye OOS+Phase B (features ndizo leverage).

**Tayari tumeshughulikia (tusihesabu mara mbili):**
- **MTF lookahead bias:** imetatuliwa kwenye `trend_align.py` (as-of `avail=bar_open+interval`,
  backward — bar zilizofungwa TU).
- **Long-horizon spurious-regression bias:** tunajua + tunadhibiti kwa permutation.

---

## Mpangilio wa kupima (kipaumbele — mantiki kubwa, overfit ndogo)

1. **D1 — Multi-TF alignment** (kipaumbele: mantiki kubwa, hatujapima)
2. **B2 — Efficiency Ratio** kama conditioner (je trend-edge inaboreka pale trend ni safi?)
3. **C2 — Hurst** kama conditioner (trending vs mean-reverting regime)
4. **A3/A4 — MA crossover / ribbon**
5. **E1/E2 — Structure (HH/LL, position in range)**
6. **B3 — Regression slope + R²**

## Tracking

| Structure | Aina | Imepimwa? | Grade | Uamuzi |
|-----------|------|-----------|-------|--------|
| D1/D2 — Multi-TF alignment | directional | ✅ | ❌ | win ~0.50 hata \|align\|=4; drop kama directional |
| B2 — Efficiency Ratio | conditioner | ✅ | ❌ | Q1–Q4 flat ~0.49; trend safi haisaidii |
| C1 — Volatility | conditioner | ✅ | ❌ (kwa trend) | high-vol → trend-follow MBAYA (mean-rev tilt) |
| Fade-extreme (mean-reversion) | directional+cost | ✅ | 🟢 partial | **D1 edge:** AUDUSD/EURGBP robust (p=0.0002), GBPUSD/NZDUSD suggestive; H4 eaten by cost. **Thibitisha OOS 2025+.** |
| E2 (Position-in-Range) × Volatility | signal×conditioner | 🔄 Test #4 | — | hypothesis: low-vol→mean-rev, high-vol→breakout (washauri A+B) |

> **Hatua:** tunaanza na **#1 (Multi-TF alignment)**. Kama directional features
> zikikubaliana pale TF zote zinaelekea upande mmoja → hapo ndipo trend wa kweli.
> Tukipata edge inayopita Phase B → tumepata structure ya kwanza halali.
