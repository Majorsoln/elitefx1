# WAVE-B (first cut) — HC2-10 FAILED-BREAK-SWEEP — S1 TRAIN GRID (FROZEN by Chief)

> **Mechanism MPYA kabisa** (liquidity-sweep / stop-hunt) — orthogonal na WAVE-A (compression/
> pullback/SR-fade). PD: "tujari hilo pendekezo" (2026-07-14). Uthibitisho unapita gate ile ile
> ya `docs/STRATEGIES.md` (S1 TRAIN → S2 VALIDATION + BH-FDR → HOLDOUT one-shot). VALIDATION/
> HOLDOUT HAZIGUSWI hapa. Grid FROZEN kabla ya S1.

## Kwa nini HC2-10 peke yake (WAVE-A ilishindwa 0/3)
Mechanism tofauti kabisa (structure/sweep, si trend/compression), TAYARI (`false_break` imejengwa +
self-test), cost-profile bora (30m), gold-eligible (SUITABLE, max_spread 75). Ikishindwa pia →
ushahidi wa nguvu tuhamie OOB. Ikifaulu → candidate wa strategy #3.

## HC2-10 — grid (FROZEN)
| Kipengele | Thamani |
|---|---|
| Trigger | `false_break` (entry=**market**, params default: look=20, rearm=8 — hakuna param-grid wave hii) |
| allow_long (signal bar i) | `isfinite(d1_dist_sup_atr) & d1_dist_sup_atr <= 0.5` (long kwenye D1 support extreme) |
| allow_short (signal bar i) | `isfinite(d1_dist_res_atr) & d1_dist_res_atr <= 0.5` (short kwenye D1 resistance extreme) |
| SL × TP (ATR) | {1.0, 1.5} × {2.0, 3.0} |
| max_hold | 24 bars (30m) |
| Pairs | EURGBP, EURCHF, AUDUSD, NZDUSD, **XAUUSD** (gold SUITABLE; max_spread 75) |
| TF | 30m |
| Cells | 1 × 4 × 5 = **20** |

**NaN/UNKNOWN → allow=False** (isfinite guard, kama C2-3). Costs = spread(config/per-bar) + slip
ndani ya episodes. Hakuna h4_trend condition (HC2-10 ni pure sweep kwenye D1 extreme — tofauti na
HC2-06 iliyokuwa na h4 filter).

## Muundo wa S2 (baada ya S1)
HC2-10 = FAMILY moja. Survivors za S1 (net+ N≥MIN_N) → pre-register kwa S2 VALIDATION + pvalue_boot
(B=50k, m=3) + BH-FDR q=0.10 (engine RASMI). Kama gold ni pekee inayonusurika, izingatie tail-risk
(spr p99=108, spikes za news — cost-share ya lower-bound). Survivor → C2-6 HOLDOUT one-shot.

## Matokeo yanayowezekana (yote halali)
- Survivor(s) OOS → strategy #3 (docs/STRATEGIES.md). - Hakuna → LESSON; pivot → OOB (C).
