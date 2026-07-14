# WAVE-C2-A — S1 TRAIN GRID REGISTRATION (FROZEN by Chief)

> **Pre-registration ya S1 (TRAIN 2016–2022 PEKEE).** Grid hii ni FROZEN kabla ya S1 kuendeshwa.
> S1 = grid-search kwenye TRAIN; survivors → S2 VALIDATION (family-pooled + BH-FDR) → C2-6 freeze
> → HOLDOUT one-shot. HOLDOUT/VALID HAZIGUSWI hapa. Context = `_mask_context_dir` (signal-bar i,
> decidable). Costs = spread(config) + slippage(0.1 market / 0.3 stop). Entry = next-bar honest.

** Shared:** TF entry = **30m** · max_hold per hypothesis · pairs = **FX pekee** (gold deferred,
spread provisional) · context values = SIGNAL bar i (as-of joined, `ctx` ya loader) · exit via
`episodes()` kama ilivyo · MIN_N ya candidate = ile ya strategy_lab (default).

---

## HC2-01 — ALIGNED-COMPRESSION (compression→expansion; prior kali zaidi)

| Kipengele | Thamani (FROZEN) |
|---|---|
| Triggers | `nr7_break`, `nr4_inside` (entry=**stop**, one-sided) |
| allow_long (signal bar i) | `d1_trend_sign==+1` **NA** `h4_trend_sign==+1` |
| allow_short (signal bar i) | `d1_trend_sign==-1` **NA** `h4_trend_sign==-1` |
| SL × TP (ATR) | {1.0, 1.5} × {2.0, 3.0} |
| max_hold | 32 bars (30m) |
| Pairs | USDCHF, USDJPY, EURJPY, AUDUSD, GBPJPY |
| Cells | 2 × 4 × 5 = **40** |

## HC2-03 — TREND-PULLBACK-RESUME (buy-dip-in-trend; Phase-12 pocket)

| Kipengele | Thamani (FROZEN) |
|---|---|
| Triggers | `trend_resume`, `rsi2_pullback` (entry=**market**, one-sided) |
| allow_long | `h4_trend_sign==+1` **NA** `d1_trend_sign==+1` **NA** `h4_rsi14<70` |
| allow_short | `h4_trend_sign==-1` **NA** `d1_trend_sign==-1` **NA** `h4_rsi14>30` |
| SL × TP (ATR) | {1.0, 1.5} × {2.0, 3.0} |
| max_hold | 32 bars |
| Pairs | USDJPY, GBPJPY, EURUSD |
| Cells | 2 × 4 × 3 = **24** |

## HC2-06 — HTF-SR-FADE (structure/reversion; conditions tofauti kwa long/short)

| Kipengele | Thamani (FROZEN) |
|---|---|
| Triggers | `bb_fade`, `engulf_extreme` (entry=**market**, one-sided) |
| allow_long | `d1_dist_sup_atr<=0.5` **NA** `h4_trend_sign>=0` (long kwenye support) |
| allow_short | `d1_dist_res_atr<=0.5` **NA** `h4_trend_sign<=0` (short kwenye resistance) |
| SL × TP (ATR) | {1.0, 1.5} × {1.5} (reversion — symmetric-ish, hakuna runner mkubwa) |
| max_hold | 24 bars |
| Pairs | EURGBP, EURCHF, USDCHF, AUDUSD, NZDUSD |
| Cells | 2 × 2 × 5 = **20** |

---

## TOTAL: m = 84 cells (TRAIN). NaN/UNKNOWN context → allow=False (excluded — decidable).

**S2 muundo (baada ya S1):** kila hypothesis = FAMILY moja; survivors za S1 zina-pool R
(mtindo wa `family_pooled`) → test moja yenye power kwa mechanism → BH-FDR kwa hypotheses 3.
Grid ndogo (84) kwa makusudi (LESSON-002; C2-WATCH ilikufa power 0.62). NaN-context bars
hazihesabiwi (allow=False) — hakuna imputation.

**Ruled OUT wave hii (si kufutwa):** 15m (HC2-02/05), `false_break` (HC2-10), gold. → WAVE-C2-B.
