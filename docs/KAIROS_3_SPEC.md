# KAIROS-3 — SPEC (mgombea wa model wa tatu; Mzunguko-4)

> PD (2026-07-30): "trade bora zaidi... kila version iwe na ubora wa positions." KAIROS-3 = model ya
> **UBORA**, si wingi. Inaongezwa kwenye portfolio (KAIROS-1/2 ZINABAKI — hazijapimwa live bado).
> Registry: `config/models.yaml` (PD anahariri bila code).

## 1. KAIROS-3 NI NINI (kwa sentensi moja)
**Model ya ML inayochagua entries BORA kutoka kwenye bwawa PANA la candidates** (event families 16 ×
pairs 12), badala ya kufuata sheria moja. Rules zinatoa **wapi pa kuangalia**; ML inaamua **ipi ya
kuchukua**.

## 2. KWA NINI SIYO K4 UPYA (hoja ya kisayansi — muhimu)
K4 (L-042) ilijaribu kuchuja **nr7 PEKEE** -> NO-LIFT. Sababu iliyogundulika: bwawa la nr7 lilikuwa
**sare (homogeneous)** — trades zote karibu ubora sawa; hakukuwa na "mbaya" za kutupa.
KAIROS-3 inachuja bwawa **TOFAUTI-TOFAUTI (heterogeneous)**: families 16 × pairs 12 × mazingira
mbalimbali -> **kuna tofauti halisi ya ubora ndani ya bwawa**. Hapo ndipo GBM ina kazi.
**Tatizo tofauti kimuundo, si jaribio lile lile mara ya pili.**

## 3. MTIRIRIKO (stack ya PD — serial kwa UBORA)
```
[1] CANDIDATE POOL   families 16 x pairs 12 x H1  (rules — cheap, pana)
        v
[2] FEATURES         k4 manifest (vol/session/atr_rel/range) + HTF context (H4/D1)
                     + family one-hot + LSTM trend-embedding (stacked feature)
        v
[3] GBM PROBABILITY  P(TP kabla ya SL)  <- ubongo wa uamuzi (LightGBM/XGBoost)
        v
[4] THRESHOLD        imechaguliwa kwa EV_net (SI accuracy) — juu = trades chache, bora zaidi
        v
[5] REGIME           volatility_state (ipo); Transformer = challenger BAADAYE ikizidi
        v
[6] EXIT             v1: SL/TP fixed (ATR).  v2: RL policy (hold/trail/toka)
        v
[7] RISK ENGINE      LANGO PEKEE (max_slots 7 / correlated 3 / bajeti ya siku) — SHARED na KAIROS zote
```

## 4. TOLEO (versioning — kila moja inapita gate yake)
| Toleo | Kinachoongezwa | Sharti la kupita |
|---|---|---|
| **v1.0** | pool + features + **GBM** + threshold | EV_net > breadth-baseline NA > 3.0 pips/trade |
| **v1.1** | + **LSTM** trend-embedding (stacked feature) | delta EV_net chanya juu ya v1.0 |
| **v2.0** | + **RL** exit management | EV_net juu ya SL/TP fixed NA max-DD isiongezeke |
| challenger | **Transformer** regime | lazima izidi volatility_state iliyopo |
Toleo jipya HALIFUTI la zamani (§2 doctrine). Anomaly-detector = **circuit-breaker ya mfumo**, si
sehemu ya KAIROS-3 (inalinda KAIROS zote).

## 5. VIGEZO VYA KUPOKELEWA (pre-registered — KABLA ya namba)
KAIROS-3 inakubaliwa IKIWA **ZOTE** zinatimia:
1. **HOLDOUT one-shot:** EV_net > 0, p_boot < 0.05 (pooled multi-pair, L-041).
2. **UBORA (bar ya PD):** EV_net **>= 3.0 pips/trade** (juu ya KAIROS-1 1.92 / KAIROS-2 2.65) NA
   >= 3x gharama ya wastani (L-039).
3. **BREADTH:** izidi nr7-pairs-12 baseline (M4-0) — si nr7-pairs-2 pekee.
4. **ORTHOGONALITY:** correlation ya returns za kila siku na KAIROS-1/2 **< 0.3** (isiwe nakala ya bet
   iliyopo — vinginevyo inaongeza ukubwa wa hatari, si diversification).
5. **N ya kutosha:** >= 200 trades (HOLDOUT+VALID) — vinginevyo INSUFFICIENT.
Kikikosekana kimoja -> **LESSON**, si model. Hakuna kulazimisha.

## 6. PAIRS (multi-pair kwa ujenzi)
Utafiti unatoa `pairs[]` — pairs zilizofanya vizuri **pooled** (si best-pair, L-041). Zinaingia
`config/models.yaml`. Model moja, pairs nyingi, bila kizuizi cha model-level (PD directive).

## 7. ITAKAVYOONEKANA IKIPITA (models.yaml)
```yaml
  KAIROS-3:
    call_sign:  KAIROS-3
    enabled:    true
    pairs:      [USDCHF, USDJPY, EURUSD, GBPUSD, ...]   # kutoka utafiti
    sl_atr:     <kutoka grid>
    tp_atr:     <kutoka grid>
    learned_ev: <HOLDOUT EV>
    magic:      20260801003
    model_artifact: models/kairos3_gbm_v1.json          # trees (auditable, si pickle)
    threshold:  0.58                                    # P(win) ya chini kabisa
```
Ikiingia hapo: **inatrade sambamba na KAIROS-1/2**, inapita risk-engine ile ile, inaonekana kwenye
dashboard/Steward kama scorecard yake (KAIROS-3), na inaweza kukodishwa peke yake (§9).

## 8. NIDHAMU (haibadiliki)
Splits takatifu (HOLDOUT one-shot mwishoni) · purged+embargoed CV · labels kutoka `episodes` (golden) ·
EV_net cost-aware · artifact JSON (hakuna pickle) · Steward inaifuatilia kama zingine.

## 9. HATARI ZINAZOJULIKANA (uwazi)
- Bwawa pana = **multiple-testing kubwa** -> purged CV + pooled + holdout-one-shot ndizo kinga.
- ML inaweza kujifunza "family X ni nzuri" tu = breadth iliyofichwa -> ndiyo maana **M4-0 baseline ni
  lazima** (ML lazima izidi breadth, si kuiga).
- Uwezekano halisi wa kushindwa upo. Ikishindwa -> LESSON + KAIROS-1/2 zinaendelea.
