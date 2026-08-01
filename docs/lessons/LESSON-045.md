# LESSON-045 — GBM juu ya bars ZOTE: taarifa ipo, gharama ni kubwa kuliko gross edge (H1 all-bar entry = NO-GO)

**Tarehe:** 2026-08-01 · **Chanzo:** M4-2 (MZUNGUKO-4) — `reports/k3_model_cv_*.md`,
spec `docs/M4_2_REGISTRATION.md` (vigezo vilisajiliwa KABLA ya model) · **Type:** RESEARCH

## Tukio

Charter ya Mzunguko-4 iliweka HATUA 1 = **signal generation** kwa GBM: P(TP kabla ya SL) kwa **kila
bar** (si nr7 pekee), pairs 12, H1. Dataset (M4-1) ilikuwa **rows 1,025,338** (bars zote × dirs 2),
labels kutoka `episodes()` ya golden (gharama halisi ndani ya kila label), purged+embargoed CV folds 5,
out-of-fold predictions pekee, threshold sweep kwa **EV_R** (si accuracy/AUC).

**Matokeo: LESSON** — hakuna threshold hata moja yenye EV_R chanya.

| geometry | bwawa (bila uteuzi) | bora zaidi (OOF) | lift iliyopatikana | iliyohitajika | % ya lengo |
|---|---|---|---|---|---|
| SL2/TP1 | −0.0470 (win 65.96%) | −0.0252 (top-5%) | +0.0218 R | +0.0798 R | **27%** |
| SL1/TP1 | −0.1019 (win 49.25%) | −0.0295 (top-1%) | +0.0724 R | +0.1545 R | **47%** |

## Dai (claim)

**Model ILIJIFUNZA kitu halisi — na bado ikashindwa, kwa sababu ya gharama, si kwa sababu ya
kutokuwa na taarifa.** Lift ni **monotone** kutoka top-20% hadi top-5%/1% kwenye **geometries zote
mbili**, out-of-fold, chini ya purge+embargo. Kelele haifanyi hivyo.

Kwa decomposition ya EV (takriban — inapuuza timeouts): cost/R ≈ 0.036 (SL2/TP1) / 0.087 (SL1/TP1),
kwa hiyo **gross edge ≈ +0.011 / +0.058 R — CHANYA**. Lakini gharama ni **mara 1.5–3.3 ya gross**.

Huu ni **muundo ULE ULE wa LESSON-039** ("the discriminating diagnostic is gross-vs-cost-margin, not
net alone"), sasa umethibitishwa kwa data mara ~50 zaidi na kwa mbinu tofauti kabisa (GBM badala ya
rules). Sababu ya kimuundo: **kuingia kwenye bar isiyochaguliwa kimuundo kunatoa move ndogo.** nr7
haitabiri mwelekeo vizuri zaidi — **inachagua bars ambazo move yake ni kubwa** ukilinganisha na cost.

## Ushahidi wa ziada (wa kiufundi — kwa yeyote atakayerudia)

1. **Tail inarudi nyuma.** top-0.1% ni MBAYA kuliko top-5% (SL2/TP1: −0.0753 vs −0.0252). Predictions
   zenye ujasiri mkubwa **si** trades bora. "Kaza threshold zaidi" SI jibu — imeshajaribiwa.
2. **c3 (p_boot) ilianguka kwa ujenzi:** p_boot inapima EV > 0; EV ilikuwa hasi kila mahali, kwa hiyo
   p ≈ 0.79–1.0. Hakuna taarifa ya ziada hapo.
3. Uteuzi uliohitajika ulikuwa **mdogo** (~0.6% ya bwawa) — kwa hiyo kushindwa si kwa sababu ya
   ukosefu wa nafasi ya kuchagua.

## MPAKA WA DAI (muhimu — kosa la muundo, limemilikiwa)

Dataset ya M4-1 ilitumia **market entry kwenye open ya bar i+1 na mwelekeo uliochaguliwa EX-ANTE**
(ilifuata charter §6.2 "bars ZOTE" kihalisi). Lakini nr7 hufanya kazi kwa **stop-entry OCO** — soko
lenyewe ndilo linalochagua upande kwa kuvunja level. Na `KAIROS_3_SPEC` §3 inasema rules zinatoa
"wapi pa kuangalia" (**pamoja na mechanics zao za entry**), ML inachagua "ipi ya kuchukua".

Kwa hiyo M4-2 ilipima: **"je ML inaweza kubashiri mwelekeo mapema kwenye kila bar ya H1?"** — jibu
ni HAPANA, kwa uhakika. Hiyo **si** design ya spec. Dai hili **halifuti** variant ya spec
(family-pool yenye entry mechanics zao) — hiyo ingehitaji **pre-registration MPYA**, si re-tune.

## Validity conditions

FX/gold, **H1**, entry ya **market** kwenye bar isiyochaguliwa kimuundo, mwelekeo wa ex-ante,
gharama halisi (spread ~0.3–0.9 pip + slippage). Imethibitishwa kwa pairs 12, miaka 7 ya TRAIN,
rows 1M, geometries 2, GBM (LightGBM) yenye purged CV.

## When to use / when NOT to use

- **Tumia:** unapopanga signal-generation yoyote inayoingia kwenye bars zisizochaguliwa kimuundo kwenye
  TF ya chini. Hesabu **gross-vs-cost KABLA** ya kufundisha chochote: kama gross inayotarajiwa < cost,
  hakuna model itakayookoa hilo.
- **USITUMIE** kama dai kwamba "ML haifanyi kazi kwenye FX" — haikupimwa hivyo. Wala kama dai dhidi ya
  ML juu ya **candidate pool yenye entry mechanics** (haijapimwa), au kwenye **TF za juu** ambapo
  cost/R inashuka mara 2–5 (H4/D1 — haijapimwa).

## Athari (zilizotekelezwa)

1. **HATUA 2 (LSTM) HAIANZI** — charter §5, kama ilivyosajiliwa. Sababu ya kiufundi pia: kikwazo ni
   **gharama**, si uwezo wa kupanga (ranking). LSTM ingeboresha ranking — si tatizo letu.
2. **HAKUNA re-tune ya M4-2.** Kubadilisha hyperparams baada ya kuona matokeo = multiple-testing juu
   ya data ileile (charter §4.6 inakataza). Jaribio limekwisha.
3. **Mwelekeo unaofuata = HTF (H4/D1)**, ambapo spread haibadiliki lakini move inakua — cost/R inashuka
   mara ~2 (H4) hadi ~5 (D1). Ushahidi unaounga mkono: mechanism ya compression tayari ilionyesha
   **EV_R chanya mara MBILI** kwenye HTF (C2-WATCH H4 p=0.0543; Swing Family D1 p=0.136) — zote
   zilianguka kwa **power**, si kwa ishara hasi.
4. `cost_budget.py` + `config/broker_costs.yaml` zimeongezwa: kila strategy sasa ina **bajeti ya
   gharama** iliyochapishwa, na broker yeyote anapimwa dhidi yake bila backtest.

## Swali lililo wazi

Ripoti ina safu ya **`nr7_flag`-only (bila ML)** ndani ya dataset ile ile. Kama nayo ni hasi, hiyo
ingethibitisha kwamba edge ya nr7 inatoka kwenye **entry mechanic** (stop-entry OCO), si kwenye hali
ya bar (compression). Ni ugunduzi wenye thamani kwa design yoyote ijayo — namba bado haijasomwa.

*Profitable ≠ Tradable Edge. Protect capital first.*
