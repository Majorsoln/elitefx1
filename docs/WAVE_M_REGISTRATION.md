# WAVE-M — MOMENTUM ARM (continuation + big-move) — S1 TRAIN GRID (FROZEN by Chief, 2026-07-15)

> **Msingi:** kila edge iliyothibitika kwenye mradi ni BREAKOUT/CONTINUATION (STRAT-001/002 nr7
> stop-entry; C2-WATCH 4/4 reps +EV); reversion/fade = 0/6 OOS mzunguko-2 (LESSON-037/038/039/040).
> Momentum = big-move → inashinda gharama (LESSON-039). PD: "ndio" (2026-07-15). Design inaepuka
> mtego wa LESSON-040: **hakuna single-pair selection** — S2 itakuwa family-pooled multi-pair.
> S1 TRAIN PEKEE; VALIDATION/HOLDOUT HAZIGUSWI. Grid FROZEN kabla ya S1.

## HM-02 — LONDON-ORB-D1 @ 30m
| Kipengele | Thamani (FROZEN) |
|---|---|
| Trigger | `session_orb` (entry=**stop**), params: `range_hours=(7,9)`, `trade_hours=(9,13)` |
| TF | **30m** (deviation kutoka 15m ya STRATEGIST-M — §6 yake risk#2 iliruhusu pre-S2; LESSON-039 cost-trap ya 15m; range 07–09 @30m = bars 4, definition ya kutosha) |
| allow_long / allow_short | `isfinite & d1_trend_sign==+1` / `==-1` (one-sided kwa D1 bias) |
| SL × TP (ATR) | {1.0, 1.5} × {2.0, 3.0} |
| max_hold | 16 bars (~saa 8 — trade inakufa kabla ya LATE) |
| Pairs | GBPUSD, EURUSD, EURGBP, GBPJPY, USDJPY |
| Cells | 1×4×5 = **20** |

## HM-05 — ALIGNED-SHOCK @ 15m
| Kipengele | Thamani (FROZEN) |
|---|---|
| Trigger | `shock_follow` (entry=**market**), params default (len_=20, k=3.0, rearm=10) |
| TF | **15m** (shock hufa ndani ya dakika 30–60; big-move by construction — ATR ya shock bar ni kubwa → cost-share inavumilika tofauti na reversion @15m) |
| allow_long | `isfinite & d1_trend_sign==+1` **NA** `hour(signal bar) ∈ [7,16]` (London/NY; Asia shocks = thin-liquidity artifacts) |
| allow_short | mirror (−1, hours zile zile) |
| SL × TP (ATR) | {1.0, 1.5} × {2.0, 3.0} |
| max_hold | 16 bars (saa 4) |
| Pairs | EURJPY, USDJPY, GBPJPY, **XAUUSD** (gold inaruhusiwa kwa MOMENTUM — LESSON-039 ilifunga fade tu; spread SUITABLE, max_spread 75) |
| Cells | 1×4×4 = **16** |

**TOTAL m = 36.** NaN→allow=False (isfinite). Hour = ratiba (decidable ex-ante — kama session ya EP-5).

## Deviations-with-reason (recorded wazi)
1. **ORB 15m→30m:** STRATEGIST-M §6 risk#2 aliruhusu "fallback 30m ni PRE-S2"; range (7,9) inatoa
   bars 4 za definition. LESSON-039.
2. **spread_state guard ya HM-05 imeahirishwa:** harness tayari ina-price spr HALISI ya entry bar
   kwenye kila trade (EV ni honest); guard ya WIDE ni ya EXECUTION layer (policy) endapo itafika S4.
3. **Session filter kwa hour ya SIGNAL bar** (si _sess ya entry bar): ratiba — decidable; entry ni
   bar inayofuata (dakika 15–30 baadaye, ndani ya dirisha lile lile).

## INFRA ndogo (IMPLEMENTER — additive)
1. `trigger_params` per hypothesis: runner ipitishe `**hyp.get("trigger_params", {})` kwenye event fn.
2. allow fns zipate `hour` pamoja na ctx: runner ijenge `ctx_plus = dict(ctx, hour=data["hour"])`.

## S2 (baada ya S1) — kinga ya LESSON-040
Kila HM = FAMILY: cells za TRAIN net+ za **pairs ZOTE zilizo chanya** (si pair-bora moja) → pool
R-normalized streams (mtindo family_pooled) kwenye VALIDATION → test 1 per family + BH-FDR m=2.
Kama pair MOJA tu ndiyo chanya TRAIN → tahadhari ya LESSON-040 inaandikwa na expectations chini.

## Matokeo yanayowezekana (yote halali)
- Survivor(s) OOS → C2-6 HOLDOUT one-shot → STRAT-003/004.
- Hakuna → momentum @ intraday imefungwa pia → OOB arm au consolidation (uamuzi wa PD).
