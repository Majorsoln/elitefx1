# WAVE-1 R1 — Referee Report (SCIENTIST-D)

*2026-07-12 · Referee: SCIENTIST-D (design owner, §B-R1 of `reports/data_science_review.md`) ·
Subject: `pvalue_boot` engine, commit `9328f16` (`reports/wave1_report.md`) ·
Verification: independent Monte Carlo, `scripts/scientist_d_referee_r1.py` (my own null
constructions and variant implementations; calls the implementer's functions unmodified;
**no data windows touched** — pure simulation).*

---

## VERDICT: **APPROVED** — both deviations ACCEPTED. S3-C2 registration is unblocked from my side.

Three non-blocking conditions/recommendations below (§4); one of them (§4.1, bootstrap B for
registered cells) should be folded into the S3-C2 registration text before the window opens.

---

## 1. Acceptance tests (§B-R1 design) — all PASS on the official engine (mb=3 + NW)

All sizes at nominal α=0.05; M=2,000–3,000 reps, B=600, ±2·SE shown in the log. Nulls are my
§A3-W1 constructions (cost-adjusted two-point payoffs, EV=0), generated independently of the
implementer's calibration scripts.

| Test | z-test (old) | `pvalue_boot` (official) | Required | Result |
|---|---|---|---|---|
| (a) symmetric i.i.d. N(0,1), N=100 | 0.0537 | 0.0533; mean \|p_boot−p_z\| = 0.021 | boot ≈ z | ✅ |
| (b) skew SL2/TP1 N=303 (W=10.98/L=23.70) | 0.0620 | **0.0500** | ~nominal | ✅ |
| (b) skew SL2/TP1 N=100 (win~69%) | 0.0710 | **0.0497** | ~nominal | ✅ |
| (b′) pos-skew SL1/TP3 N=70 | 0.0397 (conservative) | 0.0487 | — | ✅ (fixes both directions) |
| (c) determinism from cell key | — | bit-identical on repeat; different keys → different seeds/p | required | ✅ |

The z-test sizes reproduce my §A3-W1 table exactly (0.062 / 0.071 / 0.039) — the W1 finding and
the engine's correction of it are now triple-verified (my review MC, Chief's independent
spot-check 0.053, this referee MC).

Code review of the changed surfaces: `_stationary_indices` verified independently (continuation
fraction 0.669 ≈ 1−1/3, implied mean block 3.02, visited indices uniform); `_se_nw` = sd/√n on
i.i.d. data; p = (1+#{t\*≥t_obs})/(B+1) is the correct conservative-valid form; centering under
H0 correct; engine swap in `write_outputs` correct (official p = bootstrap, `p_z` retained as
sensitivity column, BH on `p_boot`); `--cells-file` path preserves all split guards including
the holdout token inside `load_window`.

## 2. Deviation (i) — `mean_block=3` instead of my "~10": **ACCEPTED, implementer is right**

My verbatim design (block ~10 + i.i.d.-sd studentization) **fails my own acceptance test (b)**,
and I confirm it with my own implementation of the verbatim variant:

| Variant @ skew null | N=303 | N=100 |
|---|---|---|
| verbatim: mb10 + i.i.d.-sd (my §B-R1 as written) | 0.0600 | **0.0697** ✗ |
| mb10 + NW (their fn, mean_block=10) | 0.0540 | **0.0660** ✗ |
| **mb3 + NW (official)** | **0.0500** ✓ | **0.0497** ✓ |

Their reported failure (0.063–0.072 at mb=10) reproduces. The mechanism they cite
(block-averaging suppressing the skewness the percentile-t must capture) is imprecise as stated —
the unstudentized mean\* retains skew ~γ/√n regardless of block size — but the empirical effect
on the *studentized* statistic is real and decisive: with N~100 and mean block 10 there are only
~10 effective resampling units, and the t\* distribution degrades exactly where the correction is
needed. My "~10" was an N≳300 intuition; the b~n^{1/3} rule gives 3–5 for N=100–300. **mb=3 is
the correct calibration for this system's cell sizes.**

## 3. Deviation (ii) — Newey-West studentization (K=mean_block): **ACCEPTED**

Isolation runs show the two deviations do separable, verifiable work:

| Variant | skew N=100 | AR(ρ=0.5) N=100 | AR(ρ=0.7) N=100 (stress) |
|---|---|---|---|
| z-test | 0.0710 | 0.1733 | 0.2483 |
| mb1 + i.i.d.-sd (plain i.i.d. bootstrap) | — | 0.1697 | — |
| mb3 + i.i.d.-sd (blocks, no NW) | 0.0517 | 0.0977 | — |
| **mb3 + NW (official)** | **0.0497** | **0.0680** | 0.0950 |

Small blocks fix the skew; NW is what buys the dependence robustness (0.0977 → 0.0680). My AR
null construction differs from theirs (Gaussian AR(1); their "cluster" null gave z=0.121 vs my
0.173) — directionally identical conclusions, so the disagreement is null-construction detail,
not substance.

**Documented residual (not a defect, a property):** under genuinely strong serial dependence the
engine is still mildly anti-conservative (0.068 @ρ=0.5; 0.095 @ρ=0.7 — vs z's 0.17/0.25). Trade
sequences from non-overlapping episodes should be far below ρ=0.5; §4.3 makes this checkable
instead of assumed.

Power price of validity: at the STRAT-001 holdout alternative (win 73.9%, W=10.98/L=23.70),
power = 0.670 (boot) vs 0.723 (z) at N=303 — about 5pp, which is the honest cost of removing a
×1.2–1.4 size bias. The MDE screen (EP-8) governs the small-N regime as intended.

## 4. Conditions / recommendations (non-blocking, ranked)

1. **B for registered cells (fold into S3-C2 registration text).** At B=10,000 the MC resolution
   of a p-value near 0.05 is ±0.004 (2·SE) — the same order as the S3b knife edge (0.002).
   For the ≤8 registered representative cells, use **B=50,000** (resolution ±0.002); it is
   deterministic (seed = cell key), costs seconds, and the value of B must be written into the
   registration before the window opens so precision is not a post-hoc choice.
2. **Restatement runs must not clobber canonical outputs.** `--cells-file` writes to the same
   `data/strategies/candidates{suffix}.jsonl` + report paths as grid runs. Run the S3/S3b
   restatement in a scratch checkout (or add an `--out-tag`), and label its FDR line clearly:
   with m = |cells in file| it is a **sensitivity table**, never a new verdict.
3. **Make the dependence assumption observable.** Have the restatement run print lag-1
   autocorrelation of each cell's PnL sequence alongside the two p columns. Pre-registered rule
   of thumb: if any proven/registered cell shows |ρ₁| > 0.3, `mean_block` must be recalibrated
   upward *with a fresh skew-size table* (blocks large enough for strong dependence and small
   enough for skew cannot both hold at N~100 — at that point subsampling or Politis-White
   auto-selection, not a bigger constant).

## 5. R6 `winrate_monitor` posterior-SE note — **CONFIRMED** (and stronger than they claimed)

Their note says flat rolling-60 SE would structurally break the alarm for STRAT-002. My
arithmetic (independent): flat SE@60 = 6.45pp puts the alarm line at 58.75%, **above** STRAT-002's
holdout win rate 57.8% → chronic alarm even at proven performance. The same holds for
**STRAT-001** (line 74.31% > holdout 73.9%), which they did not claim — the posterior-SE choice
is not just defensible for STRAT-002, it is the only version of my R6 line that works for either
strategy. Posterior SE at n_eff=327 gives line 55.06% < 57.8% ✓.

Documented trade-off (fine as designed): the holdout prior dominates early forward data, so the
*statistical* alarm is slow against abrupt decay — at a true forward win rate of 45%, no
statistical alarm at 60 forward trades (posterior 55.8% vs line 54.8%), fires by ~120. Abrupt
decay is covered by the pre-registered rolling hard thresholds (rolling-60 at 45% → HALT<50%
fires immediately); the posterior alarm is the slow-chronic-decay detector. The two alarms are
complementary, and both are pre-registered before forward data exists — which was the point of R6.
Optional future refinement (not now): cap prior weight (e.g. n_eff ≤ N_hold + forward window)
once forward N is large, so very old holdout evidence cannot mask a slow regime change forever.

## 6. Sequencing

R1 is fit to be the official FDR/registration engine. With this approval, per the PD-approved
B-PRIME sequencing, **S3-C2 registration may proceed**: bootstrap p on the 30 opened VALID
survivors, 8 mechanical group representatives, MDE screen with shrunken forecasts, gold deferred
to R5, q=0.05, one-shot on H4 2025-01→2026-04 — with §4.1 (B=50,000) and §4.2–4.3 folded into
the registration/restatement runbook.

*Every number above regenerates from `scripts/scientist_d_referee_r1.py` (fixed seeds; ~3 min).*
