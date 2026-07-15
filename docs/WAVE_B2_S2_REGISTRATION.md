# WAVE-B2 — S2 VALIDATION REGISTRATION (FROZEN by Chief, 2026-07-15)

> **Pre-registration ya S2.** Cells zilizochaguliwa na S1 TRAIN (selection halali TRAIN;
> VALIDATION haijaguswa). FROZEN kabla ya kufungua VALIDATION. HB2-06 imefungwa kwa POWER
> (haipimwi — angalia §HB2-06). S2 hii = **HB2-10 × EURCHF × H1, cells 2 PEKEE.**

## Kwa nini EURCHF pekee (na kwa nini ni tofauti na kesi ya LESSON-038)
S1 @ H1: EURCHF median gross **+2.30** (mara 2 ya +1.16 yake @ 30m — thesis ya H1-cost-ratio
imethibitika ndani ya TRAIN), median net **+0.89**, cell bora net **+1.42** (N=299, cost_share
0.50, PF 1.18). EURGBP gross +0.98 lakini net −0.06 (TRAIN-hasi — HAIPRE-REGISTERIWI; kuiweka
kungechoma FDR budget kwa cell isiyo na TRAIN evidence).

**Uaminifu (LESSON-038 caveat, wazi):** hii ni single-pair concentration — mode ile ile
iliyoangusha HC2-03/EURUSD. Tofauti za kesi hii: (a) ukubwa — net +0.89..+1.42 vs +0.1..+0.4;
(b) cost_share 0.50/0.61 vs 0.53–0.80; (c) **cross-TF consistency** — EURCHF & EURGBP ndizo
top-2 gross kwenye 30m NA H1 kwa mpangilio ule ule (mechanism halisi kwenye EUR-crosses, si
artifact ya TF moja). Bado: VALIDATION NDIYO mwamuzi. FAIL ni jibu halali.

## Cells FROZEN (2) — HB2-10 × EURCHF × H1
| # | trigger | SL | TP | max_hold | TRAIN EV_net (rejea) |
|---|---------|----|----|----------|----------------------|
| 1 | false_break (look=20, rearm=8) | 1.5 | 3.0 | 16 | +1.419 (N=299) |
| 2 | false_break (look=20, rearm=8) | 1.5 | 2.0 | 16 | +0.888 (N=303) |

Context (signal-bar i): `allow_long = isfinite & d1_dist_sup_atr<=0.5`; `allow_short = isfinite &
d1_dist_res_atr<=0.5` (hakuna h4 — kama WAVE_B2_REGISTRATION). NaN → excluded.

## Test (RASMI)
- Window: **VALIDATION 2023–2024** (`split="validation"`). HOLDOUT HAIGUSWI (token C2-6).
- Kila cell: pnl net (costs ndani ya episodes) → `pvalue_boot` (B=50k, mean_block=3, engine RASMI)
  → **BH-FDR q=0.10, m=2**. Survivor = fdr_pass **NA** EV_net>0. p_z = sensitivity (SI decision).
- Tahadhari ya correlation: cells 2 zinashiriki trigger/pair (streams zinafanana kwa kiasi kikubwa)
  — BH-FDR inabaki valid (conservative chini ya positive dependence).

## HB2-06 — VERDICT: CLOSED-BY-POWER @ H1 (si mechanism verdict)
S1: cells 40, **0** zilifika MIN_N=30 (N per cell: min 4, median 10, max 16). Trigger×condition
(bb_fade/engulf NDANI ya D1-extreme) ni adimu mno kwenye bars za H1 za miaka 7. Hii si "mechanism
imekufa" — ni "haipimiki kwa muundo huu". Hakuna relaxation ya post-hoc (LESSON-009); revisit
halali = grid mpya iliyo-designed kwa power (mf. condition pana au trigger inayofire zaidi) kwenye
wave ijayo, pre-registered.

## Matokeo yanayowezekana (yote halali)
- **Survivor:** → C2-6 freeze + HOLDOUT one-shot (dirisha bikira H1 2025-01→2026-04, token) →
  ikipita = **STRAT-003** (docs/STRATEGIES.md).
- **Hakuna survivor:** LESSON (sweep-fade @ H1 EURCHF haujathibitika OOS); mechanism inabaki
  C2-WATCH-style forward-only; tunahamia momentum arm (HC2-02/05).
