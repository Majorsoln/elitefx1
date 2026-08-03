# KAIROS — ADAPTIVE ENTRY INTELLIGENCE ENGINE (design ya PD 2026-08-02) + njia ya ujenzi

> PD ameweka vision: models 8 kwenye tabaka 3 (Understanding / Decision / Validation), timeframes 7
> (D1→M5), fusion → BUY/SELL/WAIT. Hati hii inahifadhi vision **kama ilivyo** (§1) na inaongeza
> **njia ya ujenzi inayoweza kuishi** (§3) kwa kizuizi kimoja cha kihesabu (§2).

## 1. VISION (PD — haijabadilishwa)
| Tabaka | Model | Kazi |
|---|---|---|
| UNDERSTANDING | **HMM** | market regime: trend/range/vol/transition (D1→H1) |
| | **Transformer** | price sequence → direction + movement probability |
| | **LSTM** | historical memory: "tumewahi kuona hali hii?" |
| | **CNN** | chart patterns: sweep, break-retest, order block, MSS |
| DECISION | **XGBoost** | entry quality: A+/A/B/reject |
| | **PPO** | strategy selection: trend / breakout / reversal / mean-reversion |
| VALIDATION | **Quantile NN** | SL/TP kutoka distribution (si ATR multiplier) |
| | **Distributional NN** | EV estimation — entries za EV+ pekee |

TF hierarchy: D1 macro → H4/H2 structure → **H1 decision** → M30 validation → M15 confirm → M5 timing.

## 2. KIZUIZI: BAJETI YA DATA (hesabu, si maoni)

**Tunayo:** ~64k H1 bars/pair × pairs 12 ≈ 774k bar-observations.
**Lakini training inahitaji LABELS (trades), si bars.** nr7 × pairs 12 = ~2,700 trades/mwaka →
TRAIN (miaka 7) ≈ **19,000 trades zenye label.**

**Tunachohitaji:** Transformer ndogo ≈ 100k+ params · CNN ≈ 50k+ · LSTM ≈ 20k+ · pamoja **>200k
parameters** kwa **19,000 examples.**

> Uwiano wa kawaida ni **examples 10-100 kwa parameter MOJA**. Tunahitaji ~2,000,000 labels kwa
> models 8. Tuna 19,000. **Ni pungufu mara ~100.** Hii si tahadhari — ni hesabu.

Matokeo yasiyoepukika: models zitakariri **noise** ya TRAIN. In-sample itang'aa; OOS itaanguka.

**Ushahidi wetu wenyewe (si nadharia):** M4-2 (KAIROS-3) ilitumia **rows 1,025,338** — dataset KUBWA
zaidi tuliyoweza kujenga (kila bar, si signals pekee). GBM ilipata **signal halisi** (lift monotone,
out-of-fold, purged+embargoed). Ikashindwa kwa **27-47% ya lengo** — si kwa kukosa taarifa, bali kwa
**gharama** (cost 1.5-3.3× gross). *Models 7 za ziada hazibadilishi hesabu ya gharama.*

**Hitimisho:** kizuizi si **uwezo wa model** — ni **uwiano wa move-dhidi-ya-gharama**. Hilo ndilo
tulilothibitisha mara nyingi zaidi kuliko kitu kingine chochote kwenye mradi.

## 3. NJIA: NGAZI YA USHAHIDI (vision ile ile, hatua kwa hatua)
Kanuni: **kila component inalazimika KUSHINDA bora ya sasa ili iingie.** Isiposhinda → LESSON,
haiingii. Tunamalizia na vipande vilivyothibitika **tu** — vinavyoweza kutambuliwa, kuboreshwa, na
kukodishwa (attestation inahitaji kueleza model inafanya nini).

**MAHALI: HTF (H4/D1), si H1.** Data yetu: cost/move ratio H1 = 2.5× · H4 = **8.3×** · D1 = **8.7×**.
Kizuizi kilichoua M4-2 ni **kidogo mara 3** kwenye H4. Lift ile ile iliyoshindwa H1 **inaweza kutosha**.

| # | Hatua | Kwa nini hapa | Sharti la kuingia |
|---|---|---|---|
| 1 | **XGBoost entry-quality** juu ya bwawa la **families 16 × pairs 12 × HTF** | bwawa TOFAUTI-TOFAUTI (si sare kama K4) — hapo GBM ina kazi; tabular, sample-efficient, auditable | EV_net > breadth-HTF baseline |
| 2 | **EV gate (rahisi kwanza)** `EV = p×TP − (1−p)×SL − cost` kutoka p ya (1) | haihitaji NN; inatoa lango la EV mara moja | inakata trades za EV− bila kupunguza EV ya jumla |
| 3 | **Quantile SL/TP** | inapimika peke yake: je distribution-based inashinda ATR-multiplier? | EV_net juu ya SL/TP tuli |
| 4 | **Regime (HMM)** | LAZIMA ishindane na `volatility_state` iliyopo (KMeans, permutation-null validated) | lift juu ya regime iliyopo |
| 5 | **Sequence (Transformer AU LSTM — MMOJA)** | zote zinasoma series ile ile; mbili = overfit mara mbili | delta chanya juu ya (1)-(4) |
| 6 | **CNN patterns** | features zilizopo tayari zinakamata sehemu kubwa | delta chanya |
| 7 | **PPO strategy-selection** | **haiwezi kuchagua kutoka strategies zisizokuwepo** — inahitaji 3+ zilizothibitika kwanza | EV ya portfolio juu ya kila strategy peke yake |

**PPO ni ya mwisho kwa muundo, si kwa upendeleo:** kazi yake ni *kuchagua*; hakuna cha kuchagua hadi
tuwe na strategies kadhaa zilizothibitika. Tukifika hapo, ndipo Distributional NN (EV) nayo inakuwa na
maana — inakadiria distribution ya matokeo ya mchanganyiko.

## 4. NIDHAMU (haibadiliki)
Splits takatifu · purged+embargoed CV · pooled multi-pair (L-041) · EV_net cost-aware (L-039) ·
artifacts JSON/npz (hakuna pickle) · pre-registration kabla ya namba.
**HOLDOUT ni MARA MOJA:** tunajaribu kwa upana TRAIN/VALID, tunapeleka **mchanganyiko MMOJA** holdout.

## 5. MATOKEO YANAYOWEZEKANA (yote halali)
- Hatua 1-3 zinapita → **KAIROS-3 halisi** (GBM + EV + Quantile SL/TP) — tayari ni model yenye nguvu.
- Hatua 4-6 hazitoi lift → **LESSON**: kwa data yetu, sequence/pattern models hazina cha kuongeza.
  Hilo ni **jibu**, si kushindwa.
- Zote zinapita → vision ya PD imejengwa **na kila kipande kina ushahidi wake.**
