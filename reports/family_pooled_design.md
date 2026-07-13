# FAMILY-POOLED HOLDOUT TEST — Design for Registration (C2-WATCH)

*2026-07-13 · Author: SCIENTIST-D (external reviewer) · Status: DESIGN — awaiting Chief
registration + referee before any window opens*

**Task provenance:** S3-C2 RULING 2026-07-12 (`docs/CHIEF_STATUS.md`): per-group MDE screen
failed 4/4 at the conservative shrink tip (0.35) → registration refused, virgin H4 window
preserved, C2-WATCH created; path (b) = SCIENTIST-D designs ONE family-pooled test with proper
cross-pair normalization. This document is that design. Every number is recomputed from open
artifacts by `scripts/scientist_d_family_pooled_precheck.py` (restated S2-C2 H4 file
`0fb20fd` = working-tree `data/strategies/candidates_c2.jsonl`; ruling constants). No data
window was touched in preparing it.

---

## 0. Summary

One pre-registered, single-hypothesis (m=1) test on the virgin H4 window 2025-01→2026-04:

> **H1:** The compression-H4 family (C2-WATCH), traded as one risk-normalized stream through
> its 4 mechanical representative cells, has positive expectancy net of costs.
> **Criterion:** `pvalue_boot` (official engine, B=50,000) on the pooled R-unit trade series
> < 0.05 **AND** pooled EV_R > 0.

Why this is worth a registration when the per-group screen said no: pooling the 4 reps gives
N_exp ≈ **341** and, in R-units, a pooled MDE of **0.119 R** against a shrunken (×0.35)
forecast of **0.140 R** — the screen **PASSES at the conservative tip** (margin ×1.18; power
≈ 0.62 at shrink 0.35, ≈ 0.87 at shrink 0.5). The same arithmetic that honestly blocked four
weak per-group tests licenses one adequately-powered family test. Gold groups are excluded
(vanished under p_boot — skew artifact; ruling 2026-07-12).

---

## 1. Fixed universe (no selection freedom remains)

The 4 representative cells, one per surviving C2-WATCH group, selected by the already-frozen
mechanical rule (best p_boot per group among the 12 restated survivors, TRAIN EV>0; tie at the
bootstrap floor → smaller p_z). Verified: this reproduces exactly the reps implied by the
ruling's MDE numbers (15.2<16.8 · 1.8<2.4 · 9.6<17.7 · 5.0<9.1 — all four reproduce to 0.1):

| # | Cell (event × pair · SL/TP · filter) | VALID N | EV (pips) | win% | PF | tr/day | p_boot | p_z |
|---|---|---|---|---|---|---|---|---|
| REP-1 | nr4_inside × GBPJPY · 1.5/1.5 · no-LATE | 107 | +43.29 | 72.9 | 2.862 | 0.172 | 0.0001 | ~0 |
| REP-2 | nr7_break × EURGBP · 1.5/1.0 · no-LATE | 182 | +5.20 | 76.9 | 1.940 | 0.349 | 0.0001 | 1.2e-05 |
| REP-3 | nr7_break × EURJPY · 1.0/3.0 · no-LATE | 127 | +27.48 | 40.2 | 1.861 | 0.243 | 0.0001 | 1.9e-03 |
| REP-4 | nr7_break × AUDUSD · 1.5/3.0 · no-LATE | 115 | +14.36 | 52.2 | 1.834 | 0.220 | 0.0007 | 1.3e-03 |

Notes. (i) REP-2 tie: two EURGBP cells sit at the B=10k floor p=1/(B+1)=0.0001; p_z tie-break
selects 1.5/1.0 (1.2e-05 < 1.3e-05) — same cell the ruling used. At registration, recompute
p_boot at B=50,000 for the tied pair and record that the tie-break is confirmed or overridden
by the finer floor (2e-05); either way the rule is mechanical. (ii) Four distinct pairs → the
pooled stream contains no duplicated trades by construction (asserted anyway, §5-AT7).
(iii) The 4 cells are the ONLY holdout cells opened; all other H4 2025-01→2026-04 cells remain
SEALED. Their individual holdout rows are recorded descriptively but license nothing per-cell.

## 2. Normalization: R-units (risk units), pip-scale invariant

Pips do not pool across pairs: REP-1 trades in ~59-pip-ATR GBPJPY, REP-2 in ~15-pip-ATR EURGBP
— a pip-pooled test would be a GBPJPY/EURJPY test wearing a family costume.

**Definition.** For a trade of cell c entered at bar e (signal bar i = e−1):

```
R_trade   = c.sl_atr × atr[i]          # SL distance in pips — signal-bar ATR, decidable,
                                        # exactly the quantity episodes() already uses for SL
pnl_R     = pnl_pips / R_trade          # net of costs (pnl_pips already is)
```

Rationale for R-units over ATR-units (both were on the table in the ruling):
- **Deployment-consistent:** under fixed fractional risk per trade (the only sizing the
  portfolio layer will use), realized return per trade is proportional to pnl/SL-distance =
  pnl_R. The pooled mean IS the deployable quantity.
- A loss is ≈ −(1 + cost_R) for every cell regardless of pair or SL multiple — the mixture is
  aligned on the downside, which is what the one-sided test cares about.
- Pip-scale invariance holds **up to the fixed pip-denominated slippage constants of
  `episodes()`** (SLIP_MARKET/SLIP_STOP are const pips, a real broker cost that does not scale
  with price units): multiplying a pair's pips by `s` leaves trade structure exactly invariant
  and changes pnl_R only by the closed-form slip residual −SLIP·(1−1/s)/R_trade (~0.001–0.013 R
  here — immaterial vs EV_R 0.14–0.40). *(Wording corrected post-build per OQ#1: the original
  "exact" claim overlooked the fixed slippage; Chief ruled non-blocker, referee concurs —
  see `family_pooled_referee_report.md`.)*

**Sensitivity column (recorded, non-gating):** the same test in ATR-units
(pnl_pips/atr[i]) — guards against the verdict being an artifact of the SL-rescaling choice.

## 3. Pooling and test statistic

1. Run `episodes()` for each rep cell on the window (fill rules untouched); collect per-trade
   `(ts_entry, pair, pnl_R)`. Extend `load_window` to also return the `ts` array (additive,
   non-breaking — needed for cross-pair ordering).
2. **Pool = union of the 4 streams, sorted by entry timestamp**; deterministic tie-break for
   identical timestamps: pair name alphabetical. Chronological interleaving matters: it makes
   block resampling capture same-day cross-pair dependence (GBP legs in REP-1/2, EUR legs in
   REP-2/3, common H4 compression days).
3. **Statistic:** official engine, unchanged: `pvalue_boot(pooled_R, B=50_000, mean_block=3)`
   (stationary bootstrap + Newey-West studentization K=3, percentile-t), seed derived
   deterministically from the registration string
   `"FAMILY-POOLED-C2WATCH-H4|" + "|".join(4 cell keys)` via the existing `_seed_from_key`
   hashing. B=50,000 per referee condition 1 (p floor 2e-05; resolution ±0.002 at the 0.05
   boundary).
4. **Criterion (pre-registered, single test, m=1):** p_boot < 0.05 AND pooled mean pnl_R > 0.
   No BH needed; no other test is run on this window.

**Weighting choice (explicit):** per-trade pooling, i.e. groups weight by trade frequency.
This answers the deployable question ("a trade taken by the family has EV>0") and the
composition is acceptably balanced — expected shares EURGBP 35% / EURJPY 25% / AUDUSD 22% /
GBPJPY 17% (no pair >50%, §4). Equal-group weighting would require a weighted-mean statistic
the engine doesn't have and would test a portfolio nobody plans to trade.

## 4. Power / MDE screen — the arithmetic that justifies registration

Method identical to the ruling's ("sd from payoff structure"), recomputed independently and
extended to R-units; all inputs from the restated open VALID artifact. Per rep: two-point
W/L from (EV, win, PF); sd_pips = √(w(1−w))·(W+L); ATR backed out exactly via
W+L = (TP+SL)·ATR (per-trade cost cancels in the sum); N_exp = tr/day × 347.

| Rep | share | EV_R (VALID) | sd_R | N_exp |
|---|---|---|---|---|
| GBPJPY | 17% | +0.489 | 0.89 | 59.7 |
| EURGBP | 35% | +0.229 | 0.70 | 121.1 |
| EURJPY | 25% | +0.546 | 1.96 | 84.3 |
| AUDUSD | 22% | +0.446 | 1.50 | 76.3 |
| **Pooled** | 100% | **+0.401** | **1.34** (incl. between-rep variance) | **341** |

- MDE_pooled = 1.645 × 1.34/√341 = **0.119 R**.
- Shrunken forecast, conservative tip (×0.35): **0.140 R ≥ 0.119 → SCREEN PASS (×1.18)**;
  at ×0.5: 0.201 R (×1.69).
- Power at α=0.05: **~0.62** if the true effect is the 0.35-shrunken value; **~0.87** at
  0.5-shrunken. This is a real test, not a coin flip — but if the true pooled effect is below
  ~0.12 R (≈70% shrinkage, S3c-like), it will likely fail; that is the honest deal.

**Registration-time recomputation (mandatory):** the table above uses two-point
approximations. Before freeze, compute EV_R and sd_R **exactly** from the actual R-normalized
VALID trade series of the 4 reps (validation is open; this is a re-read). The screen rule
binds on those exact numbers at shrink 0.35, same conservative-tip resolution as the ruling.
If the exact numbers fail the screen, registration does not happen — same discipline that
blocked the per-group tests. (Pre-check says it passes with ×1.18 margin; the exact sd will
differ slightly because of timeout exits, which two-point ignores.)

## 5. Acceptance tests (implementation must pass ALL before freeze; referee = SCIENTIST-D)

- **AT1 pip-scale invariance:** synthetic two-pair fixture with FIXED signals (event functions
  carry an absolute tick threshold — a separate, out-of-scope property); multiply one pair's
  o/h/l/c/atr/spr by 100 → trade structure (entries/exits/directions) bit-identical, unscaled
  pair's pnl_R bit-identical, scaled pair's pnl_R differs from base by exactly the closed-form
  slip residual −SLIP·(1−1/100)/R_trade (tolerance 1e-9). *(Amended per OQ#1 — see §2 note.)*
- **AT2 R-normalization correctness:** crafted bars with known ATR and forced SL exit →
  pnl_R = −(1 + cost/R) exactly; forced TP exit → +(tp_atr/sl_atr − cost/R) exactly.
- **AT3 determinism:** two full runs → bit-identical pooled series and p (seed from
  registration string; no global RNG state).
- **AT4 mixture-null size (the critical one):** simulate the 4-component two-point mixture
  matched to the reps' (win%, W/L, share) under EV=0 each, interleaved randomly, N=341;
  size of `pvalue_boot` at α=0.05 over ≥20k reps ∈ [0.040, 0.060]. Also run the referee's
  AR(ρ=0.5)-clustered variant of the mixture: size ≤ 0.08 (documented residual property of
  mb3+NW, `wave1_referee_report.md`).
- **AT5 holdout red line:** pooled runner refuses split=holdout without the Chief token
  (must reuse `load_window`'s existing guard — no new data path).
- **AT6 no-clobber:** outputs to `data/strategies/family_pooled_c2watch.jsonl` +
  `reports/family_pooled_report.md` only; canonical `candidates*.jsonl` untouched (referee
  condition 2).
- **AT7 dedup assert:** unique (pair, entry_bar) across the pooled stream; count per pair
  printed.
- **AT8 dry-run on VALIDATION:** full pipeline runs on the open 2023-24 window first; its
  pooled EV_R/sd_R feed §4's exact screen. (This dry-run is also the determinism fixture.)

Recorded with the verdict (descriptive, NON-gating): per-rep holdout EV_R and sign
(4/4 positive would be strong mechanism evidence; 2/4 would temper interpretation),
composition shares realized vs expected, timeout-exit share, lag-1 autocorrelation of the
pooled series (referee condition 3: |ρ₁|>0.3 → flag engine recalibration), p_z and ATR-unit
sensitivity columns.

## 6. Verdict semantics (pre-registered, so nobody negotiates with the result)

- **PASS (p_boot<0.05 & EV_R>0):** the FAMILY claim "compression-H4 has positive OOS
  expectancy" becomes **PROVEN-OOS-PROVISIONAL — family level**. It licenses: forward
  paper-trading of the 4 reps as one stream; priority for R3 (rolling folds) and R8 (tick
  features) on this family; nothing else. It does **NOT** create STRAT-00x, does not license
  capital, and does not certify any individual pair/cell — per-pair deployment still requires
  its own forward-tranche evidence under B-prime.
- **FAIL:** the family claim dies on this window with honor. C2-WATCH groups remain
  forward-only (path (a): window grows monthly). **No re-test of compression-H4 on
  2025-01→2026-04 in any form, pooled or otherwise — the window's family-level information is
  consumed by this one test either way.**
- Verdict is recorded with a 90% bootstrap CI on pooled EV_R (interval verdicts doctrine),
  not just the binary.

## 7. Honest caveats — what this test can and cannot prove (goes into the record verbatim)

1. **This is confirmation, not discovery.** The family-era leak documented in the review
   (§A3-W3 of `data_science_review.md`) still applies: compression was pushed to H4 partly
   because nr7 survived this same era on H1. Hence the PROVISIONAL cap and the forward gate —
   a PASS here plus a positive forward tranche is the evidence package, not a PASS alone.
2. **Window overlap with STRAT-001/002's proof era** means a PASS is correlated evidence with
   the existing portfolio's edge, not independent replication across time.
3. **VALID estimates are hot** (survivors' VALID/TRAIN EV ratio ~2× median): the shrink is not
   pessimism, it is the measured VALID→virgin slope (0.346) rounded kindly.
4. **One-sided deal accepted in advance:** at shrink-0.35 truth the power is 0.62 — a FAIL is
   ~38% likely even if the conservative forecast is exactly right. Nobody gets to call a FAIL
   "underpowered" afterwards; the number is on the table now.

## 8. Sequencing (per B-prime discipline)

1. IMPLEMENTER-A builds `src/research/family_pooled.py` (reuses `episodes`, `_mask_context`,
   `load_window`+ts, `pvalue_boot` — zero changes to any of them) + acceptance tests AT1-AT8.
2. SCIENTIST-D referees (independent MC for AT4; verbatim-vs-implemented check as in WAVE-1).
3. AT8 dry-run on VALIDATION → exact EV_R/sd_R → §4 screen at shrink 0.35. Fail → stop, no
   registration, this document becomes a LESSON.
4. Chief freezes registration by commit: 4 cell keys, seed string, B=50,000, criterion,
   verdict semantics §6, caveats §7. THEN the one-shot with Chief token. Verdict + descriptive
   record + CI. Window re-seals.

*SCIENTIST-D. Sources: restated survivors & rep stats `0fb20fd` (tree `candidates_c2.jsonl`);
ruling constants & per-group MDE `docs/CHIEF_STATUS.md` 2026-07-12; engine
`strategy_lab.py:pvalue_boot` (approved `wave1_referee_report.md`); arithmetic
`scripts/scientist_d_family_pooled_precheck.py` (all numbers reproduce, including the ruling's
15.2<16.8 · 1.8<2.4 · 9.6<17.7 · 5.0<9.1). No virgin window touched.*
