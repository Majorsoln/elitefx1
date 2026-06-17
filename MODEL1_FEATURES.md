# Model 1 — Feature Inventory & Validation Plan

*Model 1 = Regime Classifier (HMM → LightGBM), msingi wa mfumo (MFUMO Sehemu 2).
Hati hii inaorodhesha **kila taarifa** Model 1 inayotumia, na **jinsi tutakavyo-thibitisha
kila moja KABLA ya kujenga model** — kanuni: tusijenge kwa dhana, tujenge kwa ushahidi
(kama tulivyofanya kwa `volume_imbalance`). Rejea: `DIAGNOSTICS_DECISIONS.md`,
`reports/feature_diagnostics.md`.*

**Timeframes:** D1, H4, H2, H1 (HTF nne).

---

## 1. Inventory ya taarifa zote

### A. HMM inputs (HATUA 1 — unsupervised)
| # | Taarifa | TF | Maelezo |
|---|---------|----|---------|
| 1 | **Returns** (close-to-close) | D1,H4,H2,H1 | log-return; **vol-standardized** (uamuzi wa diagnostics) |
| 2 | **Volatility** (rolling std) | D1,H4,H2,H1 | rolling std ya returns |

### B. LightGBM features (HATUA 2 — supervised)
| # | Taarifa | TF | Maelezo |
|---|---------|----|---------|
| 3 | **EMA200 slope** | kila TF | mteremko wa EMA200 (directional) |
| 4 | **Price vs EMA200** (% distance) | kila TF | (close − EMA)/EMA (directional) |
| 5 | **ADX** | kila TF | nguvu ya trend (strength, sio mwelekeo) |
| 6 | **Per-TF state** | D1,H4,H2,H1 | hali ya regime ya kila TF (derived) |
| 7 | **HMM hidden state** (ya sasa) | cross-TF | output ya HMM (derived) |
| 8 | **HMM transition probability** | cross-TF | uwezekano wa kubadilika regime (derived) |

### C. Volume confirmation (Sehemu 1)
| # | Taarifa | TF | Maelezo |
|---|---------|----|---------|
| 9 | **Volume / tick_count / volume_imbalance** | kila TF | "regime/trend confirmation" |

> #6, #7, #8 ni **derived kutoka HMM/pipeline yenyewe** — vinathibitishwa kupitia HMM
> (post-fit). Tunachokithibitisha **sasa** ni RAW predictors: **#1–#5 na #9**, kila moja × TF 4.

---

## 2. Validation methodology (kabla ya modeling)

Target = **forward trend** (no-lookahead): feature ya wakati `t` dhidi ya return ya
baadaye (forward k-bars), signal hutumia past tu.

| Aina | Features | Mtihani | "Validated" kama |
|------|----------|---------|------------------|
| **Directional** | returns, EMA200 slope, price-vs-EMA | IC dhidi ya **forward signed return** + monotonicity ya quantile + hit-rate | \|IC\| thabiti kwa pairs (≥~0.02–0.03), hit-rate > 0.50, quantile monotonic |
| **Strength** | ADX, volatility | dhidi ya **\|forward return\|** / trend persistence (sio mwelekeo) | high value → \|forward return\| / persistence kubwa zaidi |
| **Confirmation** | volume / imbalance | je inaongeza taarifa **zaidi ya bei**? (incremental) | inaboresha utabiri zaidi ya price-only |

**Forward horizons:** kadhaa (k = 1, 5, 10, 20 bars) ili kuona kama edge ipo na kwa muda gani.

**Hatua ya kushindwa:** feature isiyopita (kama `volume_imbalance` next-bar) — **idemote/idrop**,
isijengewe model. Tunajenga Model 1 kwa features **zilizothibitishwa tu**.

---

## 3. HMM — je tumepata "best approach" baada ya diagnostics?

**Yaliyofungwa (data-backed):**
- ✅ **Regimes ni HALISI** — ACF(r²)=0.10–0.16 (9/9). HMM/regime modeling ina msingi.
- ✅ **Emissions:** vol-standardized returns **+ Student-t** (conditional kurtosis 8/9 bado >1).
  Pure Gaussian ingekosea. (`DIAGNOSTICS_DECISIONS.md #1`.)
- ✅ **Returns hazitabiriki moja kwa moja** — ACF(r)≈0 (soko efficient).

**Nuance muhimu ya kitaalamu (haijafungwa kikamilifu):**
- ACF(r)≈0 lakini ACF(r²)>0 ina maana: **muundo wa regime uko kwenye VOLATILITY**, sio
  mwelekeo. Kwa hiyo HMM (kwenye returns+vol) itang'amua zaidi **HIGH-VOL vs LOW-VOL
  regimes** kuliko UP/DOWN/RANGE moja kwa moja. **Mwelekeo (UP/DOWN) lazima utoke kwa
  trend features** (#3, #4) — ndiyo **sababu hasa hybrid (HMM + LightGBM) ina mantiki:**
  HMM kwa vol-regime, trend features kwa direction.

**Bado wazi (maamuzi ya hatua ya modeling, sio data analysis):**
- Idadi ya hidden states (MFUMO=3; data-driven: jaribu 2–5 kwa BIC/likelihood).
- Feature set kamili ya HMM (returns/vol; TF gani; univariate au multivariate).
- Je hidden states zinamap vizuri kwa UP/DOWN/RANGE (validation post-fit).

**Hitimisho:** diagnostics zimetupa **emission distribution sahihi + uthibitisho regimes zipo
+ ujuzi kuwa HMM ni vol-regime detector** — hii ni *misingi* ya best approach. Lakini
"best approach" KAMILI (states, feature set) inakamilika **wakati wa modeling**, ikitegemea
**validation ya features hapa chini (#1–#5, #9)** ambayo tunaanza sasa.
