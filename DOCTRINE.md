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
5. **EVENT-CENTRIC, sio condition-centric.** Soko linazalisha *matukio* (vol-expansion,
   breakout, failure, stretch, sweep) — sio bars huru. Tafiti **aftermath ya EVENT**, sio
   "kila bar yenye condition". (Insight ya review — kiini cha edge isiyoonekana.)
6. **Edge = ENTRY + EXIT.** Exit (hasa kwa mean-reversion) inaweza kueleza sehemu kubwa ya
   performance. Pima *"entry ileile, exit tofauti"* — sio entry-signal pekee.
7. **Tathmini kwa EV, sio win-rate:** Expected Value, Profit Factor, avg-R, MaxDD,
   trades/year, time-to-target. Win-rate pekee inadanganya.
8. **Regime/feature lazima IONGEZE thamani inayopimika** (MR+regime vs MR-pekee), sio
   "regime ipo" pekee. (Bila hii: sahihi lakini irrelevant.)

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

---

## 10. Doctrine Extension V2 — Principles 11–22 (zimepokelewa)

*Kutoka Doctrine_Extension_Research_V2. Zinaongeza/kuimarisha §1.*

| # | Principle | Status |
|---|-----------|--------|
| 11 | **Edge ≠ win-rate** → EV, PF, avg-R, MaxDD, frequency, time-to-target, stability | ✅ (eval_exits, strategy_lab) |
| 12 | **Edge = Quality × Frequency × Stability** | ✅ portfolio frequency |
| 13 | **Event-centric** (event→outcome, sio condition→outcome) | ✅ strategy_lab (cross_into) |
| 14 | **State ≠ Transition** | ❌ tested: transition features (accel/vol-exp/wick/time) IC≈0 n-kubwa (OHLC) |
| 15 | **Location ≠ Intention** | ❌ intention haipo OHLC (hakuna order flow) |
| 16 | **Exhaustion vs Momentum** | ❌ tested: features hazitenganishi kwenye OHLC (rank-IC≈0) |
| 17 | **Regime existence ≠ edge** (signal-with vs signal-without regime) | ✅ partial (conditional_edge: regime haikusaidia fade) |
| 18 | **Exits ni research object** (entry ileile, exit tofauti) | ✅ eval_exits |
| 19 | **Multi-TF hierarchy** (D1 context, H1 setup, M15 trigger) | ⬜ Priority 5 |
| 20 | **Features chache zenye maana** > nyingi (lazima ilete taarifa MPYA) | ✅ kanuni |
| 21 | **Holdout ni TAKATIFU** (2025+) | ✅ |
| 22 | **Block bootstrap** > IID | ✅ |

**Research Priorities:** 1=Evaluation upgrade (✅ kiasi) · 2=**Exhaustion vs Momentum (kuu)** ·
3=Event framework · 4=Regime refinement (expansion/mature/exhaustion) · 5=MTF (D1/H1/M15).

**CORE BELIEF:** *Edge ni adimu. Research haitafuti kuthibitisha hypothesis — inajaribu
kuibomoa. Hypothesis inayoishi baada ya cost + holdout + walk-forward + block-bootstrap =
candidate edge.*

---

## 11. HUKUMU YA AUDIT (uwazi — hali halisi)

**OOS VERDICT: ❌ FAIL.** EUR-MR portfolio ilishindwa holdout 2025+ (TRAIN PF 1.15 → OOS
PF 0.79, EV −0.135R). Per §5.4, hii ni fail. Nidhamu ilifanya kazi — overfit imekamatwa
kabla ya pesa halisi. (Bonus: OOS ya awali ilikuwa **imechafuliwa** na 2024-warmup trades;
bug imerekebishwa portfolio.py — chuja entry_date ≥ 2025. Hata baada ya fix, fail inabaki.)

**Holdout 2025+ sasa IMETUMIKA kwa hypothesis ya EUR-MR (imefeli).** Hatupati ku-re-pick
portfolio baada ya kuona OOS. Edge mpya yoyote inahitaji holdout iliyobaki/mpya.

**Marekebisho ya nidhamu (kutoka audit):**
- Ripoti zote sasa zinatamka **VERDICT** (PASS/FAIL/INCONCLUSIVE) kutoka nambari — sio template.
- **EURJPY imeondolewa** (ilifeli `mr_validate` sub-period; haikupaswa kuwa portfolio).
- **Validator authority:** `mr_validate` (cost + circular-shift perm + sub-period + dedup) ni
  chanzo cha ukweli; `scan_all` "✅ EURJPY" ilikuwa criterion laini → superseded.
- **eval_exits.md numbers (EV+0.689) ni STATE-BASED entry (deprecated)** — sio event-centric
  (§1.5). Portfolio (event-centric) ndio sahihi; usinukuu eval_exits za zamani.
- **Phase B sasa kwenye portfolio/OOS** (permutation null), sio block-bootstrap pekee.

**META-OVERFITTING TALLY (§6.5):** majaribio ya mradi mzima ≈ scan_all 216 (6×9×4) +
mr_validate 9 + mr_robustness 27 (9×3) + eval_exits 6 + exhaustion 12 + cross_pair 6 +
strategy_lab 54 + portfolio = **300+ hypotheses.** Survivors 1–2 (EURGBP imara, EURUSD
borderline) zinaendana KABISA na false-discovery ya multiple-testing → **OOS fail haishangazi.**

**FREQUENCY (kizuizi cha kimfumo):** EURGBP MR ≈ 7–11 trades/yr → ~miaka 3.7 kufikia +10%.
Hata edge halisi haitoshi kupita FTMO kwa muda. Sio la kurekebishwa kwa tuning.

**Hitimisho la uaminifu:** Kwenye OHLC (majors 9, hakuna order flow), **HATUNA directional
edge robust inayodumu OOS.** Imara pekee: vol-regime (risk/sizing). ML iliyoandikwa MFUMO
Sehemu 2/3 **haijajengwa.** Edge halisi pekee katika trading hapa = **mfumo unaojiambia ukweli.**
