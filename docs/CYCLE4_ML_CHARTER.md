# ELITEFX — MZUNGUKO-4: ML SIGNAL GENERATION (directive ya PD 2026-07-30)

> PD: "tunaenda kubuni mbinu mpya za kuongeza nafasi za trade — iwe ML: LSTM + XGBoost/LightGBM + RL."
> Chief: nakubali mbinu zote tatu, LAKINI kila moja ipewe KAZI inayoifaa (§2). Hii ni **signal
> GENERATION** (nafasi mpya) — SI K4 (ilikuwa FILTERING ya signal iliyopo; NO-LIFT, L-042). Nafasi
> mpya = hypothesis-space mpya, halali kabisa.

## 1. TATIZO HALISI (kwa nini nafasi ni chache)
nr7 ni teule: ~trade 1 / siku 1.5 / pair. Pairs 2 hai -> trades ~3-5/wiki. Vyanzo VITATU vya nafasi:
- (A) **Signals mpya** (ML — hii charter).
- (B) **BREADTH: pairs 12 badala ya 2** kwa logic ile ile iliyothibitika (rahisi, haraka, hakuna ML —
  L-041 pooled). **Hii inaendeshwa SAMBAMBA** kama baseline; ML LAZIMA ishinde breadth, si nr7 pekee.
- (C) TF nyingine (H4/D1 WATCH zipo).

## 2. KAZI YA KILA MBINU (mgawanyo wa Chief — muhimu)
| Mbinu | Kazi ninayoipa | Kwa nini |
|---|---|---|
| **GBM (LightGBM/XGBoost)** | **HATUA 1 — signal generation.** P(TP kabla ya SL) kwa KILA bar (si nr7 pekee) -> threshold -> entries mpya | Tabular + features zetu; sample-efficient; **auditable** (trees -> JSON); haraka kujaribu |
| **LSTM** | **HATUA 2 — sequence member.** Label ile ile; kama ensemble/stacked feature ndani ya GBM | Inakamata mfuatano ambao features hazikamati; INAHITAJI ushahidi wa H1 kwanza (data-hungry, overfit-prone) |
| **RL** | **HATUA 3 — SI entry-discovery.** Bali **EXIT/POSITION MANAGEMENT + sizing policy** (shikilia/trail/toka; risk throttle) | RL kwa entry-from-scratch juu ya FX (SNR ndogo, ~64k bars/pair) = mashine ya overfit. Action-space ndogo (hold/exit/trail) + simulator wetu wa honest = matumizi salama na yenye thamani halisi |

**Uwazi (lazima ujue):** siikatai RL — naipeleka pale itakapotoa thamani badala ya kuunda udanganyifu.
Ikitokea HATUA 1+2 zikatoa signal nyingi, RL ya exit inakuwa na kazi halisi (kila trade ina exit).

## 3. LABEL (msingi wa yote) — TRIPLE-BARRIER kutoka harness YETU
Kwa kila bar-candidate: fungua kwa nadharia -> je TP (k×ATR) inagusa KABLA SL (m×ATR) ndani ya
max_hold? Label = win/loss/timeout + R halisi. **Chanzo = `event_quality_report.episodes`** (golden —
next-bar fills, tie->SL, gharama halisi). HAKUNA labeling mpya iliyoandikwa mkono (GIGO + parity).

## 4. NIDHAMU (haibadiliki — ndiyo inayotofautisha na "AI ya YouTube")
1. **Splits takatifu:** TRAIN 2016-2022 -> VALID 2023-2024 -> HOLDOUT (SEALED). Sealed 2026-05+ (§3.1b).
2. **Purged + embargoed CV** (labels zinapishana kwa muda — bila purge, leakage ni hakika).
3. **Pooled multi-pair** (L-041 anti-selection-bias); si best-pair.
4. **COST-AWARE (L-039) — RED LINE:** nafasi nyingi = gharama nyingi. Metric = **EV_net baada ya
   spread+slippage**, si accuracy/AUC. Signal yenye +0.5 pip gross na cost 1.5 pips = HASARA.
   Edge lazima iwe ~3-4x cost.
5. **Artifact:** JSON/npz + provenance (HAKUNA pickle). GBM -> tree dump; LSTM -> weights npz + arch JSON.
6. **Pre-registered kill criteria** KABLA ya kuona namba (§5).
7. Deps mpya (lightgbm/xgboost/torch) = zimeandikwa kwenye registry ya mradi; artifacts zinabaki
   auditable (JSON), si framework-locked.

## 5. KILL CRITERIA (pre-registered)
Kila hatua inasimama isipokuwa:
- **HATUA 1 (GBM):** VALID EV_net **> nr7 baseline NA > breadth-12 baseline**, trades/mwaka >= 2x nr7,
  p_boot < 0.05 (pooled). Vinginevyo -> LESSON, HATUA 2 haianzi.
- **HATUA 2 (LSTM):** lazima **iongeze** juu ya GBM (delta EV_net chanya, CV-stable). Vinginevyo GBM peke.
- **HATUA 3 (RL):** lazima **ipite exit ya sasa (SL/TP fixed)** kwa EV_net NA isiongeze max-DD.
- HOLDOUT inafunguliwa **MARA MOJA** mwishoni, kwa winner MMOJA (au hakuna).

## 6. AWAMU
1. **M4-0 (BREADTH baseline):** nr7 proven kwa pairs 12 pooled -> namba ya kushinda. (Rahisi, sambamba.)
2. **M4-1 (DATASET):** triple-barrier labels + features (REUSE k4_dataset manifest + episodes) kwa
   bars ZOTE (si nr7 pekee), pairs 12, TRAIN pekee. Purged-CV splitter.
3. **M4-2 (GBM):** LightGBM/XGBoost -> P(win) -> threshold-sweep kwa EV_net -> CV -> VALID check.
4. **M4-3 (LSTM):** sequence model, label ile ile; ensemble/stacking na GBM; VALID delta.
5. **M4-4 (RL exit):** policy ya exit/hold/trail juu ya signals za winner; simulator = harness yetu.
6. **M4-5 (GATE):** winner mmoja -> HOLDOUT one-shot -> registry (KAIROS-3?) au LESSON.

## 7. MATOKEO YANAYOWEZEKANA (uaminifu)
Uwezekano wa kweli: (i) GBM inatoa signals nyingi lakini gharama zinazila -> LESSON (thamani: tunajua);
(ii) GBM inatoa lift ndogo halali -> model mpya (KAIROS-3); (iii) yote yanashindwa -> nr7+breadth
inabaki portfolio. Zote TATU ni matokeo halali. Hatutalazimisha.
