# M4-2 — PRE-REGISTRATION (GBM ya KAIROS-3 v1.0)

> **Imeandikwa 2026-08-01, KABLA ya model yoyote kufundishwa** (charter docs/CYCLE4_ML_CHARTER.md
> §4.6: "Pre-registered kill criteria KABLA ya kuona namba"). Namba zilizo hapa chini zote zinatoka
> **M4-0/M4-0b/M4-1 zilizokwisha kutokea** — hakuna namba ya model ndani ya hati hii.
> Mabadiliko ya vigezo baada ya kuona matokeo ya model = kuhamisha magoli (haramu, §4.6).

## 1. Chanzo cha data (kimefungwa)

`data/processed/k3/<pair>.parquet` (M4-1) — **TRAIN PEKEE 2016-2022**, pairs 12, bars ZOTE × dirs 2,
labels kutoka `episodes()` ya golden (gharama halisi ndani ya kila label, L-039).

| kipimo | sl2tp1 (KAIROS-1 geometry) | sl1tp1 (KAIROS-2 geometry) |
|---|---|---|
| N (bwawa lote) | 1,025,338 | 1,025,338 |
| win-rate bila uteuzi | **65.96%** | **49.25%** |
| EV_R bila uteuzi | **−0.0470** | **−0.1019** |

Bwawa lote lina EV **hasi** kwa ujenzi (kila bar inalipa spread+slippage). Hii ndiyo hatua ya sifuri:
kazi ya GBM ni kupata **subset** yenye EV chanya inayozidi breadth — si kutabiri bei.

## 2. Kipimo cha uamuzi (SI accuracy, SI AUC)

**EV_R ya subset iliyochaguliwa** (R-units, net-of-costs, pooled pairs 12 — L-041/L-039).
Accuracy/AUC hazitatajwa kama sababu ya kupitisha au kukataa. Threshold inachaguliwa kwa **EV_R**,
si kwa probability calibration.

## 3. Vigezo vya KUPITA (pre-registered)

Model ya M4-2 **inapita** IKIWA, kwenye **purged+embargoed CV ndani ya TRAIN**, kuna threshold MOJA
inayotimiza **ZOTE**:

| # | Sharti | Namba | Chanzo |
|---|---|---|---|
| 1 | EV_R > breadth VALIDATION | **> +0.0328** (sl2tp1) · **> +0.0526** (sl1tp1) | M4-0 pooled |
| 2 | trades/mwaka ≥ 2× nr7-pairs-2 | **≥ 854** (sl2tp1) · **≥ 890** (sl1tp1) | charter §5; M4-0 per-pair (USDCHF+USDJPY) |
| 3 | p_boot < 0.05 (pooled, engine RASMI) | — | charter §5 |
| 4 | Sharti 1-3 zinashikilia kwenye **folds ≥ 4/5** | — | anti-fold-cherry-picking |

Ikikosa **kimoja** -> **LESSON**, na **HATUA 2 (LSTM) HAIANZI** (charter §5).

### 3b. Lift inayohitajika (kutoka §1 — ni matokeo ya hesabu, si lengo jipya)
Kufikia sharti 1, subset lazima ihamishe EV_R kwa **+0.080 R** (sl2tp1) au **+0.155 R** (sl1tp1)
kutoka bwawa lisilochaguliwa. Kwa makadirio (bila kuzingatia timeouts), hiyo ni win-rate ya
**≥ ~71.3%** (sl2tp1, kutoka 65.96% = **+5.3pp**) au **≥ ~57.0%** (sl1tp1, kutoka 49.25% = **+7.7pp**).
Uteuzi unaohitajika ni **mdogo**: 854 trades/mwaka × miaka 7 ≈ **0.6% ya bwawa** (breadth-12 hutumia
~1.8%). Nafasi ya kuwa mteule ipo; swali ni kama features zinabeba taarifa hiyo.

### 3c. Bar ya ZIADA kwa KAIROS-3 (spec §5.2 — si ya M4-2)
Kuwa **mgombea wa KAIROS-3** (si tu "kuzidi breadth"), model itahitaji **EV_net ≥ 3.0 pips/trade**.
Kwa R ya wastani (SL×ATR, H1 FX), hiyo ni takriban **EV_R ≥ 0.15** (sl2tp1) / **≥ 0.28** (sl1tp1) —
lift kubwa mara 2-3 kuliko sharti 1. **M4-2 inapimwa kwa §3 pekee**; §3c inatajwa hapa ili tusije
tukachanganya "imezidi breadth" na "inastahili kuwa KAIROS-3".

## 4. Utaratibu (umefungwa kabla ya kuanza)

1. **CV:** `purged_cv.purged_folds` (folds 5 za MUDA, embargo = horizon ya label). TRAIN PEKEE.
2. **Threshold sweep:** juu ya CV out-of-fold predictions PEKEE; EV_R kwa kila threshold.
3. **FREEZE:** hyperparams + threshold zinaandikwa kwenye commit **kabla** ya kugusa VALIDATION.
4. **VALIDATION = eval MOJA** baada ya freeze (charter §4.1). Si tuning, si re-sweep.
5. **HOLDOUT + sealed 2026-05+ HAZIGUSWI** kwenye M4-2 kabisa (ni za gate ya M4-5, mshindi MMOJA).

## 5. Kinga za leakage (zinazotekelezwa kwenye code)

- `load_k3()` ina-**assert** hakuna column ya OUTCOMES ndani ya X (leak #1).
- Features zote ni za **signal bar i** (state ya i+1 haijulikani wakati wa uamuzi).
- **Purge + embargo** ni lazima — labels zinapishana kwa hadi max_hold; bila hiyo CV yoyote ni ya uongo.
- Folds ni za **MUDA** kwa pairs zote pamoja (cross-pair leakage haiwezekani).
- `nr7_flag` ni feature halali (inajulikana kwenye bar i), **si** njia ya kurudisha breadth kwa siri:
  ripoti ya M4-2 italinganisha model dhidi ya `nr7_flag`-only subset kwa uwazi.

## 6. Artifact + utegemezi (charter §4.5/§4.7)

- Trainer: **LightGBM** (charter §2 inaitaja; inafaa kwa 1M × ~40 tabular). Imeongezwa kwenye
  `src/research/requirements.txt`.
- Artifact: **JSON tree dump** (`dump_model()`) — **HAKUNA pickle**, auditable.
- **Inference ni pure-numpy** juu ya JSON hiyo (scorer yetu), si framework — hivyo live/paper
  hazitegemei LightGBM, na self-test inathibitisha scorer yetu = predictions za LightGBM.

## 7. Matokeo yanayowezekana (yote halali — charter §7)

(i) Threshold inapatikana, EV_R inazidi breadth kwa trades za kutosha -> KAIROS-3 v1.0 inaendelea.
(ii) Lift ipo lakini haitoshi kwa sharti 2 (trades chache mno) -> LESSON: "ubora upo, wingi hapana".
(iii) Hakuna lift juu ya breadth -> **LESSON**, HATUA 2 haianzi, nr7+breadth inabaki portfolio.

Hakuna kati ya hizi ni "kushindwa kwa mradi". Kushindwa pekee kungekuwa kubadilisha vigezo hivi
baada ya kuona namba.

*Profitable ≠ Tradable Edge. Protect capital first.*
