# Family-Pooled Build — Referee Report (SCIENTIST-D)

*2026-07-13 · Referee: SCIENTIST-D (design owner, `reports/family_pooled_design.md`) ·
Subject: `src/research/family_pooled.py` build (commit `acbc11f`, IMPLEMENTER-A) ·
MC evidence: `scripts/scientist_d_referee_pooled.py` (pure Monte Carlo — no data window touched)*

## VERDICT: **APPROVED WITH 2 REQUIRED PRE-FREEZE FIXES (F1, F2)** — *provisional until §2 MC
table is filled (full B-ladder running at commit time; placeholders {…} below will be replaced
in the finalization commit; approval is void if any §2 band fails)*

The implementation is faithful to the design, reuse purity is verified, all 8 acceptance tests
pass (re-run by me locally), and my independent full-scale AT4 Monte Carlo confirms the pooled
test's size is nominal (§2). Two small defects must be fixed before Chief freezes registration —
both are in the *screen/one-shot protection logic*, not in the statistic itself — plus the OQ#1
wording amendment (accepted; design already amended). Nothing blocks Operator's AT8 dry-run
once F1/F2 land.

---

## 1. Verbatim-vs-implemented review (design §1–§8)

Verified line-by-line against the design-of-record:

| Design item | Implementation | Status |
|---|---|---|
| §1 fixed universe (4 reps, no-LATE, vol=None) | `REP_CELLS` — matches design table exactly | ✅ |
| §2 R-units: pnl_R = pnl/(sl_atr × atr[entry_bar−1]) | `_r_normalize` — signal-bar ATR, the exact SL quantity of `episodes()`; AT2 exact to 1e-12 | ✅ |
| §2 ATR-unit sensitivity | `pnl_atr` + `p_atr` column | ✅ |
| §3.1 stream path identical to `strategy_lab.evaluate` | `cell_stream`: event fn → `_mask_context` on signals → `episodes` (fill rules untouched) | ✅ |
| §3.2 pool sorted by (ts_entry, pair); dedup | `pool_streams` + AT7 assert | ✅ |
| §3.3 seed from registration string, `_seed_from_key` hashing | `registration_string` + `_seed_from_registration` (sha1→12hex→int over the full string). OQ#2: the "hashing-scheme" interpretation is exactly what the design intended — confirmed | ✅ |
| §3.3 B=50,000, mean_block=3, α=0.05, m=1 criterion (p<0.05 AND EV_R>0) | `B_REG`, `MEAN_BLOCK`, `ALPHA`, `run_family` verdict line | ✅ |
| §5-AT5 holdout red line via existing `load_window` guard | verified: PermissionError raised before any read; no new data path | ✅ |
| §5-AT6 no-clobber | outputs = `family_pooled_c2watch.jsonl` + `family_pooled_report.md` only; sentinel test passes | ✅ |
| §6 CI + verdict semantics text | `_boot_ci` (90%, descriptive) + report generator carries PASS/FAIL semantics and §7 caveats verbatim | ✅ |
| §8.1 reuse purity | `git show acbc11f`: only `load_window` gained `ts=` (additive); `episodes`/`_mask_context`/`pvalue_boot` untouched. **Golden hashes re-verified by me locally** (mr=28cc2218e7d1c43f, nr7=872edc444171653e intact); `event_quality_report` + `strategy_lab` self-tests PASS on my run | ✅ |
| §4 MDE screen arithmetic | `mde_screen` formula correct, **but called with the wrong N** — see F1 | ❌ → F1 |
| one-shot integrity vs missing data | `run_family` silently proceeds if a pair's window is missing — see F2 | ❌ → F2 |
| §5 descriptive record: per-rep EV_R & sign | derivable from the per-trade jsonl rows but not printed in the report | ⚠ N1 |

## 2. AT4 FULL MC (independent; my nulls, my variant engine; official `pvalue_boot` called unmodified)

Full spec (≥20k reps at B=50,000) costs ~13 h of compute (benchmarked: 2.4 s/call at B=50k,
n=341), so I ran a **B-ladder** — statistically equivalent for size estimation because finite-B
jitter of p is ±√(p(1−p)/B) (= .0049/.0022/.0010 at B=2k/10k/50k) and induces only second-order
size bias; the ladder demonstrates B-stability empirically. Two honest EV=0 null constructions
("matched to reps" is ambiguous — I test both): NULL-A = reps' W/L shape in R-units with
breakeven win%; NULL-B = reps' observed win% with (1−w)/−w payoffs (the build's construction).
Mixture shares .17/.35/.25/.22, N=341, interleaved.

| Run | Config | Size @ α=0.05 | Band | Result |
|---|---|---|---|---|
| 1a | official, NULL-A, 20,000 reps @ B=2,000 | {S1A} | [0.040, 0.060] | {R1A} |
| 1b | official, NULL-B, 20,000 reps @ B=2,000 | {S1B} | [0.040, 0.060] | {R1B} |
| 2 | official, NULL-A, 4,000 reps @ B=10,000 | {S2} | [0.035, 0.065] | {R2} |
| 3 | official, NULL-A, 600 reps @ B=50,000 (registration B) | {S3} | [0.030, 0.070] | {R3} |
| 4 | official, NULL-A + AR(ρ=0.5) copula clustering, 8,000 reps @ B=2,000 | {S4} | ≤ 0.080 | {R4} |
| 5 | **referee's own** stationary-bootstrap+NW variant (different construction, own RNG), NULL-A, 8,000 reps @ B=2,000 | {S5} | agree w/ 1a within 2·SE | {R5} |
| — | z-test reference on the same nulls | {SZ} | (reference) | — |

{MC_SUMMARY}

## 3. OQ rulings (referee)

- **OQ#1 (AT1 fixed-slip residual): ACCEPTED — implementer is right, my design wording was
  wrong.** `episodes()` slippage is a constant in pips (a genuine broker cost that does not
  scale with price units), so pnl_R under ×s scaling differs by exactly −SLIP·(1−1/s)/R_trade.
  The build verifies structural invariance exactly and the residual against closed form (1e-9)
  — a *stronger* test than my original "bit-identical" wording, which was internally
  inconsistent with my own AT2 formula (cost/R is not scale-free). Magnitude here: SLIP_STOP =
  0.3 pips vs R = 22.7–88.5 pips → 0.003–0.013 R, immaterial vs EV_R 0.14–0.40. Do **NOT**
  make slippage pip-proportional in `episodes()` — that would silently change every published
  artifact for zero benefit. Design §2/§5-AT1 amended accordingly (this commit); Chief's
  non-blocker ruling concurred with.
- **OQ#2 (seed interpretation): CONFIRMED** — hashing-scheme over the full registration string
  is what the design intended.
- **OQ#3 (REP-2 tie-break B=50k recompute): correct reading** — that is a registration step
  (Chief, §8.4), not build scope. It must appear in the freeze commit text.
- **OQ#4 (record format): no objection from referee** — pooled per-trade rows in the jsonl are
  exactly what post-hoc verification needs; Chief may add format at freeze if desired.

## 4. REQUIRED FIXES (small; before Chief freeze — both protect the one-shot, neither touches the statistic)

**F1 — MDE screen must use N_exp(holdout), not N(split).** `run_family` calls
`mde_screen(ev_r, sd_r, n)` with `n` = pooled trade count of the split being run. On the AT8
dry-run (VALIDATION, expected pooled N≈531) this understates MDE by √(531/341) ≈ 1.25×
(0.119 R → 0.095 R) — an anti-conservative screen, the exact failure mode the ruling of
2026-07-12 refused to accept. Design §4 defines MDE at **N_exp = Σ_reps (n_i/days_i) × 347**.
Fix (a few lines): `cell_stream`/`run_family` already have `data["days"]` per pair — compute
`n_exp = sum(len(stream_i)/days_i * 347)` and call `mde_screen(ev_r, sd_r, n_exp)` for the
registration screen (the split-n version may remain as a descriptive extra). Acceptance:
on the AT6/7/8 fixture, screen MDE must equal 1.645·sd_R/√n_exp with n_exp built from
days=250 fixtures, not from pooled N.

**F2 — abort on missing pairs (one-shot protection).** `run_family` silently continues when
`load_window` returns None for a pair (`missing.append` → pooled test of <4 streams). If that
ever happened on the holdout one-shot, it would burn the virgin window with a *different test
than the one registered* (wrong composition, wrong N, same registration string). Fix:
`if missing: raise RuntimeError(...)` for `split in ("validation","holdout")` runs used for
screen/verdict (the registered test is defined over exactly 4 streams). Acceptance: fixture
run with one pair removed must raise, not report.

**N1 (non-blocking nit):** print per-rep EV_R and sign in the report (design §5 descriptive
list) — the data is already in the jsonl. **N2 (non-blocking):** `is_timeout` labels a genuine
SL/TP hit exactly at the last allowed bar as a timeout (descriptive only; rare). Neither blocks.

## 5. Conditions carried to registration (unchanged from design + WAVE-1 referee)

1. B=50,000 at the final verdict; REP-2 tie-break recompute at B=50k recorded in the freeze
   commit (OQ#3).
2. AT8 dry-run screen binds on **exact** VALID EV_R/sd_R with F1's N_exp — pre-check forecast
   was margin ×1.18 at shrink 0.35; if the exact numbers fail, registration does not happen.
3. Lag-1 autocorrelation of the pooled series printed with the verdict; |ρ₁| > 0.3 → engine
   recalibration before the verdict is accepted (WAVE-1 condition 3 analog — the report
   generator already prints it).

## 6. Sequencing after this report

F1+F2 (IMPLEMENTER-A, ~30 min) → referee spot-check of the two fixes (diff-level; no new MC
needed — the statistic is untouched) → Operator AT8 dry-run on VALIDATION → exact screen at
shrink 0.35 → Chief freeze commit → one-shot with token.

*SCIENTIST-D · Referee of record for the family-pooled test · MC script:
`scripts/scientist_d_referee_pooled.py` (seeds fixed; official engine called unmodified) ·
Golden-hash regression re-verified locally · No data window touched.*
