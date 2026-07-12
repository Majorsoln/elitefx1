# ELITEFX — Independent Data Science Review (SCIENTIST-D)

*2026-07-12 · External institutional review · Author: SCIENTIST-D (appointed by Project Director 2026-07-10)*

**Scope.** Full review of the alpha-research pipeline (S0→S4, Cycles 1–2): methodology, statistics,
artifacts, and code. Every number below is recomputed by me from committed artifacts or quoted with
its source. **Integrity boundaries respected:** no new experiments were run on holdout/virgin
windows; all recomputations use already-opened results read from git history
(`git show <commit>:data/strategies/*.jsonl`). Reproduction script: `scripts/scientist_d_recompute.py`
(reads artifacts from git history only; touches no data windows).

**Sources used.** Raw candidates: C1 TRAIN `ccfbb24`, C1 VALID `e1a0d27`, C1 HOLDOUT `86a5977`,
pairs-11 VALID `686744f`, C2-H1 VALID `96793e7`, C2-H4 TRAIN `ffb212e`, C2-H4 VALID `d3c03a6`.
Code: `src/research/{event_quality_report,strategy_lab,event_library_v2,market_state_engine}.py`.
Reports: `reports/{strategy_lab_report*,failure_autopsy_report,event_quality_report}.md`,
`docs/CHIEF_STATUS.md` (Validation Log).

---

## Executive summary

This is a far more disciplined retail-scale research program than the median institutional desk:
pre-registration frozen by commit before windows open, sealed one-shot holdout with a token guard
enforced in code (`strategy_lab.py:220-221`), honest next-bar fills, worst-case tie resolution,
per-trade costs, BH-FDR, and — rarest of all — a culture of recording its own process failures
(the S3c exposure disclosure, `07c59df`). I verified every published FDR verdict by independent
recomputation and **all of them reproduce exactly** (§A2).

The five findings that matter most:

1. **The p-value engine is structurally biased toward exactly the fragile strategy type the Chief
   already worries about.** The one-sided normal approximation (`strategy_lab.py:pvalue_gt0`) is
   anti-conservative for negatively-skewed PnL (high-win/small-TP) and conservative for
   positively-skewed PnL (low-win/big-TP). Monte Carlo under a payoff-matched null: true size at
   nominal α=0.05 is **6.2–7.1%** for SL2/TP1 structures and **3.9%** for TP3 structures (§A3-W1).
   Consequence in the artifacts: TP=1.0 cells are **49%** of nominally significant validation cells
   vs **24%** of the grid; TP=3.0 are 6% vs 26%. Part of the "high-win/small-TP dominance" is a
   statistical artifact, not the market. Skew-corrected, SIB-1's holdout p moves 0.049→**0.058**
   (no longer nominally significant) and the S3b 3/5 verdict survives by a margin of **0.002** in
   BH space. STRAT-001 still passes its single-test criterion (0.021→0.027 < 0.05). Fix is cheap
   (block bootstrap over stored per-cell PnLs) and should be retrofitted as a sensitivity
   re-analysis of S3/S3b before any S3-C2 verdict is issued (§B-R1).

2. **Selection shrinkage is severe, measurable, and should be priced into every future verdict.**
   Joining C1 VALID (`e1a0d27`) to C1 HOLDOUT (`86a5977`) on 1,870 common cells: cells with VALID
   p<0.01 average EV **+3.57 → +1.42** on holdout (**−60%**); p∈[0.01,0.05): **−75%**; OLS slope
   EV_holdout ≈ 0.35·EV_valid. The C2-H4 survivors currently show median VALID/TRAIN EV ratio
   **2.1×** (XAUUSD up to **41×**, `ffb212e`→`d3c03a6`) — a regime signature, not an edge estimate.
   Anyone planning S3-C2 should expect survivor EVs to shrink by half to two-thirds, and size
   the registration (and expectations) accordingly.

3. **The 2023-24 validation window is nearly mined out, and Cycle-2's "virgin window" argument is
   weaker than Cycle-1's was.** Cumulative distinct candidate-cells with p-values computed on the
   same 2023-24 window: **4,519** across four runs (1,939 C1 + 360 new pairs-11 + 1,068 C2-H1 +
   1,152 C2-H4), with FDR applied per-run, never globally. Worse: the decision to push compression
   to H4 in C2 was made *after* seeing nr7 survive both the 2023-24 window (C1) and the 2025-01→
   2026-04 holdout (STRAT-001/002). The H4 cells are new, but the *family × era* hypothesis is
   not — family-level knowledge of "compression works in 2025-26" leaked into C2's design. A
   one-shot on the H4 2025-01→2026-04 window is therefore *confirmation of a family already known
   to work in that era*, not independent discovery. §B-R2 proposes how to run it honestly anyway.

4. **The economics are thinner than the statistics.** From `86a5977` + autopsy spread table:
   STRAT-001 costs consume ~**36%** of gross edge (net +1.92, est. cost ~1.1 pips/trade); a
   permanent +0.5 pip spread widening removes **26%** of its net edge (STRAT-002: 16%/19%). Win-rate
   margins over breakeven are **2.2 SE** (STRAT-001) and **2.0 SE** (STRAT-002). These are real but
   fragile edges; the binding risk is cost/win-rate drift, and there is currently no spread-widening
   stress test, no win-rate control chart, and no portfolio-level view.

5. **What is missing is not more mining — it is evaluation infrastructure.** Single static
   validation window (the "walk-forward" label in the code comments is a misnomer — nothing rolls);
   no regime-conditional evaluation; trade-independence assumed everywhere; no correlation/joint-DD
   analysis of STRAT-001+002; feature space limited to OHLC/ATR/session/vol-tercile while tick
   density and volume-bar code (`src/data/`) sits unused. Recommendations §B are ranked with this
   in mind: the highest-value work is retrofitting honest uncertainty (bootstrap, regime slices,
   portfolio joint risk) onto what exists, not generating new candidates.

---

## A. Independent assessment of methodology

### A1. What is genuinely strong (verified in code/artifacts)

| Practice | Evidence | Assessment |
|---|---|---|
| Pre-registration frozen by commit *before* windows open | S3 (`CHIEF_STATUS` 2026-07-09), S3b (`4331e57`), S3c (`b9cdc55`), S2-C2 (`0e45f73`) | Genuine. The S3c 0/3 FAIL being accepted without re-rolling is the strongest evidence the discipline is real. |
| Holdout guard enforced in code, not policy | `strategy_lab.py:218-221` raises `PermissionError` before reading ≥2025 without Chief token | Better than most professional shops. |
| Honest simulation | `event_quality_report.py:episodes()` — next-bar entry, stop fills `max(level, open)` gap-honest, OCO-ambiguous bars skipped, tie→SL worst-case, per-trade cost = entry-bar spread + slippage | Sound. Self-tests cover determinism, non-overlap, noise+costs→negative EV, tie→SL. |
| Decidability of filters | `_mask_context` (`strategy_lab.py:116-140`): session = entry bar (schedule, ex-ante), vol-state = signal bar | Correct; the earlier post-hoc-filter bug was caught and fixed. |
| Negative results kept and taxonomized | `failure_autopsy_report.md` (B2 370 mirage cells, B4 1,052 dead), C2-H1 0/1,068, strength 0/7 archived | The autopsy is the single most valuable research document in the repo. |
| Process-failure disclosure | S3c exposure disclosure (`07c59df`), reporting amendment (S2) | Rare and valuable. GBPJPY VALID +7.52 → virgin +0.33 subsequently proved the disclosure mattered. |

### A2. Verification: every published verdict recomputes

Recomputed BH-FDR (q=0.10) from stored p-values in the artifacts, my code, independent of
`bh_fdr()`:

| Run | Artifact | Published | Recomputed | Match |
|---|---|---|---|---|
| C1 S2 validation | `e1a0d27` (1,939 cells) | 1 survivor | k=1, same cell (nr7×USDCHF 2.0/1.0 no-LATE, p=9.0e-06) | ✅ |
| pairs-11 validation | `686744f` (2,299 cells) | 1 survivor | k=1 | ✅ |
| C2-H1 validation | `96793e7` (1,068) | 0 | k=0 | ✅ |
| C2-H4 validation | `d3c03a6` (1,152) | 30 | k=30, same 30 flags | ✅ |
| S3b holdout m=5 | `CHIEF_STATUS` p-values | 3/5 | k=3 (SIB-1/2/3) | ✅ |

STRAT-001's three-window trajectory reproduces from `ccfbb24`/`e1a0d27`/`86a5977`:
TRAIN N=1,607 EV+0.36 win 71.1% → VALID N=425 EV+3.07 win 79.3% p=9e-06 → HOLDOUT N=303 EV+1.92
win 73.9% p=0.021, availability stable 0.81–0.88 tr/day. The artifact chain is internally
consistent. **Nothing in this review disputes the arithmetic; the issues below are about what the
arithmetic assumes.**

### A3. Weaknesses, each with numbers

#### W1. The p-value engine systematically favors negative-skew (high-win/small-TP) structures

`pvalue_gt0` is a one-sided z-test on per-trade PnL. Cell PnL under SL/TP-in-ATR exits is
approximately two-point: win +W, lose −L. For TP<SL (high win rate), skew is negative
(STRAT-001 structure: skew ≈ −0.8); for TP=3 structures, positive. For skewed distributions the
t/z statistic is biased: samples with fewer losses have *both* higher mean *and* smaller SD, so t
inflates on the profitable side of negative-skew nulls.

Monte Carlo (400k reps, two-point null matched to each cell's stored win/PF, EV=0):

| Structure | True size @ nominal 0.05 | Inflation |
|---|---|---|
| SL2/TP1, N=303 (STRAT-001-like) | 0.062 | ×1.24 |
| SL2/TP1, N=100, win~69% null | 0.071 | ×1.41 |
| SL1.5/TP1.5, N=107 | 0.046 | ×0.92 |
| SL1/TP3, N=70 | 0.039 | ×0.77 |

Observable consequence in `e1a0d27`: among the 88 cells with nominal p<0.05 & EV>0, **49% are
TP=1.0** (grid base rate 24%) and only 6% are TP=3.0 (base rate 26%). Mean win% of significant
cells = 61.9%. The mechanism story ("compression pays quickly") may be true, but the test
statistic *independently* pushes the same direction. The pipeline is optimizing partly for a
statistical artifact — and the artifact-favored structure is precisely the fragile one
(small win-margin over breakeven, cost-sensitive).

Skew-corrected p-values for the proven/registered cells (payoff-matched null MC; approximate —
ignores timeout exits, which would slightly soften it):

| Cell | Stored p | Corrected p | Status impact |
|---|---|---|---|
| STRAT-001 holdout | 0.0209 | **0.027** | Still passes pre-registered p<0.05 ✅ |
| STRAT-002 (SIB-2) | 0.0288 | **0.033** | Passes alone; see BH note |
| SIB-1 | 0.0488 | **0.058** | No longer nominally significant |
| SIB-3 | 0.0357 | **0.040** | Passes BH rank-2 threshold by 0.0002 |
| SIB-5 | 0.1725 | 0.201 | Fail (unchanged) |

S3b re-verdict with corrected p's under the same pre-registered BH q=0.10 m=5: still k=3 — but
only because SIB-1's 0.058 clears the rank-3 threshold 0.060 **by 0.002**. The official record
stands, but it stands on a knife edge that the published numbers do not reveal. Before S3-C2, the
p-value machinery should be replaced (§B-R1) and S3/S3b re-stated as a sensitivity analysis —
this uses only already-opened cells and is fully legal under the integrity rules.

#### W2. One static validation window; selection shrinkage is large and now measurable

S2 is called "walk-forward" in the code header (`strategy_lab.py:6`) but is a single static
2023-24 split. Nothing rolls. Regime-dependence is therefore untested at selection time, and the
system's own artifacts now quantify the cost:

- **VALID→HOLDOUT shrinkage (C1, 1,870 joined cells):** p<0.01 bucket: mean EV +3.57→+1.42
  (−60%), only 64% remain EV>0; p∈[0.01,0.05): +3.57→+0.88 (−75%). OLS: EV_holdout ≈
  −0.81 + 0.346·EV_valid (corr 0.31). TRAIN→VALID slope is likewise 0.61.
- **Era artifacts among current C2-H4 survivors** (`ffb212e`→`d3c03a6`): median VALID/TRAIN EV
  ratio 2.1; nr4×GBPJPY 4.1–5.3×; XAUUSD 4.2–41×; shock×XAUUSD VALID +949 vs TRAIN +155. The
  2023-24 gold bull and yen volatility are doing much of the work.
- Already-documented instances: pair-leadership rotation TRAIN→VALID (GBPUSD→USDJPY,
  `CHIEF_STATUS` S2), GBPJPY VALID +7.52 → virgin +0.33 (S3c).

The lesson the system half-learned ("mechanism survives, pair ranking rotates") has a stronger
general form: **point estimates from any single window are era samples, not edge estimates.**
Every deployment expectation should be set from shrunken estimates (empirical-Bayes toward the
family mean, or simply ×0.35–0.5 per the measured slope), and evaluation should move to
multi-window consistency (§B-R3).

#### W3. Multiplicity accounting is simultaneously too harsh and too lenient

- **Too harsh within a run:** BH m counts cells, but cells within an (event, pair) share the same
  event stream with overlapping trades — C1's 1,939 cells span only **110** (event,pair) combos
  (~17.6 cells/combo); C2-H4's 1,152 span 48. The effective number of independent hypotheses is
  closer to the combo count than the cell count. This is why 86 of the 87 "FDR-TAX" casualties
  (autopsy B3a) are nr7 siblings: one family paid an m≈1,939 tax ~17 times over. BH remains
  *valid* under positive dependence, but its power is being squandered, and the Chief's B3
  diagnosis ("pooling") is directionally right. The clean statistical fix is a correlation-aware
  procedure (Romano-Wolf / SPA via bootstrap, §C1), not just coarser grids.
- **Too lenient across runs:** 4,519 distinct cells have now been tested against the same 2023-24
  window over four registrations, each with its own q=0.10 budget. The FDR guarantee applies
  per-run; there is no global accounting. And hypothesis *formation* for C2 (compression→H4)
  was conditioned on C1's validation *and holdout* outcomes, so the C2-H4 FDR on the same window
  is not a fresh 10% budget — family-level, it is closer to a confirmation exercise. This is the
  garden of forking paths operating at the level of *which grid gets built*, which no per-run FDR
  can see. It cannot be fixed retroactively; it can be priced in (§B-R2: stricter q, family-level
  m, forward tranche before deployment).

#### W4. Cost model is optimistic in exactly the tail that kills these structures

Costs = entry-bar median spread + fixed slippage (0.1/0.3 pips). Missing: spread widening at
news/rollover, volatility-dependent slippage, and any stress scenario. Because cost enters EV
once per trade, sensitivity is exactly linear and brutal for the proven strategies
(holdout EVs from `86a5977`; median spreads from autopsy: USDCHF ~1.0, USDJPY ~0.4):

| Strategy | Net EV | Est. cost/trade | Cost as % of gross | EV if spread +0.5 pip | EV if +1.0 pip |
|---|---|---|---|---|---|
| STRAT-001 (USDCHF) | +1.92 | ~1.1 | 36% | +1.42 (−26%) | +0.92 (−52%) |
| STRAT-002 (USDJPY) | +2.65 | ~0.5 | 16% | +2.15 | +1.65 |
| SIB-1 (plateau) | +1.41 | ~1.1 | 44% | +0.91 | +0.41 |

The `spread_state` (NORMAL/WIDE) already computed in the state engine is unused in evaluation —
a WIDE-conditional EV table is a one-day job with existing data (§B-R5). For XAUUSD (C2), where
the pip is $0.01 and spreads are tens of pips, the fixed-slippage assumption is materially
weaker than for FX majors; any gold survivor needs a dedicated cost sensitivity before S3-C2 is
even registered. Also note `maxdd` is computed on trade-close equity (`strategy_lab.py:_maxdd`),
understating intra-trade drawdown — relevant for FTMO-style constraints.

#### W5. Underpowered registrations were predictable ex-ante — power analysis is absent

S3c "failed" at N≈100 per cell. From the stored (EV, p, N): SIBC-3 implied per-trade sd ≈ 11.1
pips → at its observed EV +1.21, p<0.05 requires N≈226 (2.2×); SIBC-1 needs 2.6×; SIB-5 needs
3.0×. A 16-month window at 0.2 trades/day *cannot* validate cells of this EV/sd class — the
failure was foreseeable at registration time without touching any data. Every future
registration should carry a pre-computed minimum detectable effect: with per-trade sd σ and
window N, MDE ≈ 1.645σ/√N. (For N=100, σ=12 pips → MDE ≈ 2.0 pips/trade. Cells whose *shrunken*
EV forecast is below MDE should not be registered — they burn virgin windows for guaranteed
ambiguity.) "FORWARD-WATCH" status for EURCHF was the right instinct; making the arithmetic
explicit makes it a rule instead of an instinct.

#### W6. No portfolio layer exists

STRAT-001 and STRAT-002 are both nr7_break, both no-LATE, both TP=1×ATR, on two USD pairs whose
volatility regimes co-move. NR7 compression days cluster cross-pair (dollar-wide quiet days), so
their entries plausibly coincide. Nothing in the repo measures: trade-time overlap, PnL
correlation of the two streams, joint drawdown, or what "~1.6 trades/day" means for margin and
FTMO daily-loss limits when both fire the same London morning. The episodes needed to compute
all of this already exist deterministically (§B-R4). Deployment ruling treats SIB-1/3 as one
correlation group with STRAT-001 (correct), but the same question for STRAT-001 vs STRAT-002 is
open and unanswered.

#### W7. Independence assumptions untested; feature space frozen at OHLC-derived

Trades within a cell are non-overlapping but not independent: volatility clustering and regime
persistence induce serial correlation in win/loss runs, which the z-test (and my two-point MC)
ignores; a block bootstrap addresses both this and W1 in one move. Meanwhile the project owns
tick data and working code for tick density, volume bars, adaptive volume bars, spread quality
(`src/data/`) — none of which feed the research loop. Given repeated evidence that the live vein
is compression→expansion, the obvious unused feature is a *better compression measure* (tick
count/volume contraction inside the NR7 bar) rather than more OHLC variants.

#### W8. Minor harness notes (no action urgent)

Session boundaries are fixed server-time hours; DST shifts London/NY by an hour for several
weeks/year — a session-filtered edge should tolerate ±1h boundary jitter (cheap robustness check
on open windows). Timeout exits (24 bars→close) mix a third outcome into the two-point payoff —
included in EV, fine, but worth reporting as a separate outcome share per strategy. `MIN_N=30`
pre-filter before FDR is outcome-independent under the null — acceptable.

---

## B. Recommendations, ranked (impact × effort), with runnable designs

All designs use existing data/code on already-opened windows unless stated. Implementation goes
through Chief/PD registration per doctrine.

### R1 — Replace the normal-approx p-value with a block-bootstrap engine, and re-state S3/S3b as a sensitivity analysis
**Impact: HIGH (fixes W1, W7-independence; changes what survives all future FDRs). Effort: LOW (~1 day).**

Design:
1. In `strategy_lab.py`, add `pvalue_boot(pnls, B=10_000, mean_block=10)`: stationary bootstrap
   (Politis-Romano; geometric block length ~10 trades) over the *ordered* per-cell PnL sequence;
   p = fraction of bootstrap means of the *centered* series ≥ observed mean (equivalently a
   percentile-t if computing studentized statistics — prefer studentized for accuracy).
2. Self-test: (a) on symmetric i.i.d. nulls, bootstrap p ≈ z-test p; (b) on two-point negative-skew
   nulls, bootstrap size ≈ nominal where z-test size ≈ 1.3–1.4× nominal (reproduce §A3-W1 table);
   (c) determinism via fixed seed derived from cell key.
3. Re-run `--split validation` and the already-opened S3/S3b cells with both engines; publish a
   two-column p table. Cells already opened — no new exposure. Acceptance: documented deltas;
   S3-C2 registration (whenever it happens) uses the bootstrap engine only.
4. Pre-register the engine swap by commit *before* any new window is opened.

### R2 — S3-C2: family-level registration on the virgin H4 window, with leak-priced criteria
**Impact: HIGH (the pending PD decision). Effort: LOW (selection rule + one run).**

My independent position on Option A vs B (`CHIEF_STATUS` 2026-07-10): Option B is defensible —
the mechanical FDR selection means the leak steered *hypothesis formation*, not *cell choice* —
but the family-era leak (§A3-W3) means this one-shot cannot carry the same evidential weight as
C1's S3. Run it, but price the leak into the design:

1. **Register groups, not cells.** The 30 survivors are 8 (event,pair) groups (recomputed from
   `d3c03a6`: nr7×EURGBP 8, nr4×GBPJPY 7, nr7×XAUUSD 4, nr7×AUDUSD 4, shock×XAUUSD 2,
   nr7×EURJPY 2, nr7×USDJPY 2, nr7×GBPJPY 1). For each group pre-register ONE representative
   cell by mechanical rule (best VALID p with TRAIN EV>0 — same rule as S3b/S3c). m=8, not 30:
   more power, no plateau double-counting, and plateau robustness is then checked descriptively,
   not inferentially.
2. **Tighter budget for the tainted families:** BH q=0.05 (not 0.10) for compression/shock groups;
   the bootstrap engine (R1) for all p-values. EV>0 requirement stays.
3. **Deployment gate, not proof gate:** any survivor is styled *PROVEN-OOS-PROVISIONAL* and must
   additionally show EV>0 on the forward tranche (2026-05→deployment date, data that exists by
   then) before capital. This converts the unavoidable leak into a two-stage verification.
4. **Expectation-setting:** publish shrunken EV forecasts next to registration
   (×0.35–0.5 per §A3-W2). If shrunken EV < MDE of the window (W5 arithmetic), do not register
   the group at all. Applying this today: XAUUSD groups pass trivially on EV size but fail cost
   realism until R5's gold cost model exists; EURGBP (EV +3.3–6.5 pips, spread ~0.8?) needs the
   MDE check first.

### R3 — Rolling-origin re-evaluation of the nr7/nr4 families (regime robustness without new data)
**Impact: HIGH (answers "is this a regime or an edge" — the #1 open scientific question). Effort: MEDIUM (~2-3 days).**

Design: on TRAIN+VALID only (2016-2024, all opened), for the proven cells and the 8 C2 groups:
evaluate per calendar year (9 folds), embargoing 24 bars (=max_hold) at each boundary — purging
is nearly free here since episodes are non-overlapping and features are trailing. Report per
fold: EV, win%, N, and the **sign consistency count** (folds EV>0 / folds). Pre-registered
descriptive criterion (this is diagnostics, not selection — no FDR game): a deployable family
should be EV>0 in ≥6/9 years and not owe >50% of pooled EV to a single year. STRAT-001 gets the
same table including 2025-26 (already opened). This directly tests F-029 (non-stationarity) as a
*measurement*, and creates the regime-conditional deployment substrate (weakness #8 in the
Chief's own list).

### R4 — Portfolio layer v0: overlap, correlation, joint drawdown of STRAT-001+002
**Impact: HIGH (deployment risk is portfolio risk; FTMO limits are portfolio-level). Effort: LOW (~1 day).**

Design: re-run the two proven cells' episodes on TRAIN/VALID/HOLDOUT (deterministic, opened),
keeping entry/exit bar indices and timestamps. Compute: (a) fraction of days both fire;
(b) fraction of *hours* both hold positions; (c) daily-PnL correlation of the two streams;
(d) joint equity curve and max joint drawdown vs sum-of-individual; (e) worst joint day vs FTMO
daily-loss limit under intended sizing. Decision rule to pre-register: if daily-PnL correlation
> 0.4, halve per-strategy size. Extends trivially to any S3-C2 survivor before deployment.

### R5 — Cost stress harness (spread widening + WIDE-state conditioning + gold cost model)
**Impact: MEDIUM-HIGH (the edges are cost-thin; §A3-W4). Effort: LOW.**

Design: (1) EV(Δspread) is analytic — publish the table for every proven/candidate cell as part
of every future report (one line of code in `write_outputs`). (2) Split each proven cell's
opened-window trades by the existing `spread_state` of the entry bar; report EV_NORMAL vs
EV_WIDE. If EV_WIDE < 0, add a decidable WIDE-skip filter to the *deployment policy* (not the
backtest) and forward-verify. (3) For XAUUSD: build the empirical spread distribution from ticks
(code exists: `spread_quality.py`) before any gold registration; replace the 0.3-pip stop
slippage with a percentile-based figure for gold.

### R6 — Pre-registered win-rate control chart for deployed strategies
**Impact: MEDIUM (the #1 live risk is win% decay; currently "monitoring" is unspecified). Effort: LOW.**

Design: for each deployed strategy, from holdout parameters set: breakeven win% w_be (STRAT-001:
68.3% at current costs; STRAT-002: 52.3%), observed w_obs, and a CUSUM on the trade-level
win/loss Bernoulli sequence calibrated so that: alarm if the rolling posterior mean win% (Beta
prior from holdout N) drops below w_be + 1 SE. Pre-register kill/resize thresholds *now*, before
forward data accumulates — e.g. STRAT-001: review at 60-trade rolling win < 70%, halt at < 66%.
This converts "monitoring ya lazima" from intention to mechanism, and removes the temptation to
re-litigate after drawdowns.

### R7 — Register a standing MDE rule (stop burning virgin windows on underpowered cells)
**Impact: MEDIUM. Effort: TRIVIAL (a paragraph of doctrine + 5 lines of code).**

Design: at registration time compute per cell: expected N in the window (from TRAIN/VALID
trades/day × window days), per-trade sd from VALID, MDE = 1.645·σ/√N, and shrunken EV forecast
(slope 0.35–0.5 from §A3-W2, updated as more VALID→virgin pairs accumulate). Registration
requires shrunken-EV ≥ MDE. S3c would have been stopped by this rule; SIB-5 too.

### R8 — Compression-quality features from ticks (the one feature-engineering bet worth making)
**Impact: MEDIUM (only alpha-side item on this list). Effort: MEDIUM-HIGH (Operator PC runs).**

Rationale: every surviving strategy is compression→expansion. The current NR7/NR4 definition
sees only range. Tick data can distinguish "quiet compression" (low tick count, thin
participation) from "coiled compression" (high tick count in narrow range — absorption). Design:
compute tick-count and tick-imbalance percentiles for NR7 signal bars on TRAIN only; split
STRAT-001/002 TRAIN+VALID trades by tercile of signal-bar tick intensity; if EV spread across
terciles is material (>1 pip) and monotone, register ONE decidable filter variant (e.g.
"tick-count ≥ median") as a C3 hypothesis through the standard pipeline. This is meta-labeling
in its minimal, honest form (see §C4) and doubles as the first K4 feature with proven-edge
provenance.

*Not recommended now:* more event families on H1 majors (autopsy B4 is emphatic), deep models on
303-trade samples, HMM regime models (tercile states + yearly folds cover the need at current N),
genetic/evolutionary parameter search (multiplicity bomb).

---

## C. Modern methods triage — what has REAL value here, and what is buzzword

**C1. Stationary block bootstrap + Romano-Wolf/SPA — YES, highest value.**
One bootstrap infrastructure solves three documented problems at once: skew bias (W1, quantified
×1.24–1.41), serial dependence (W7), and correlation-blind multiplicity (W3 — resampling the
*joint* cell PnL matrix gives the null max-statistic distribution across correlated cells, which
is exactly White's Reality Check / Hansen's SPA; Romano-Wolf gives stepwise FWER with the same
machinery). With 17 cells/combo, correlation-aware testing recovers most of the power BH loses —
the B3a "FDR-TAX 87" category would largely not exist under Romano-Wolf. This should become the
standard S2/S3 engine. Cost: ~2-3 days; PnL sequences already exist per cell in memory at run
time.

**C2. Deflated Sharpe Ratio / PSR — PARTIAL.**
The moment-correction insight of PSR (skew/kurtosis-adjusted significance) is subsumed by the
bootstrap (C1) at trade level. DSR's trial-count deflation duplicates what BH/RW already do, and
its independence assumptions fit this correlated grid poorly. Adopt the *idea* (report
skew/kurtosis of PnL per strategy; distrust normal-based anything) — skip the formalism.

**C3. Purged/embargoed CV and CPCV — PARTIAL.**
Full López de Prado CPCV is overkill: labels here are short episodes (≤24 bars), features are
trailing, leakage risk is minor. The valuable 20% is **multiple chronological evaluation windows
with embargo** = R3's rolling-origin design. Do that; skip combinatorial purging until label
horizons grow (e.g., if D1/weekly strategies appear).

**C4. Meta-labeling — YES, but in minimal form and second.**
The architecture is already meta-labeling-shaped: ENTRY = trigger, AI learns
P(success|context) (Entry Doctrine; K4). The honest v0 is R8: one tick-derived context feature,
tercile analysis, one registered filter. The dishonest version — training a classifier on
TRAIN+VALID trades of a strategy *selected on VALID* and reporting its in-sample lift — would
manufacture leakage; any learned gate must be trained strictly on TRAIN trades and validated as
a NEW hypothesis through S2/S3. Full ML meta-labeling becomes worthwhile when the portfolio has
5+ strategies and thousands of forward trades; not before.

**C5. Regime-conditional evaluation/deployment — YES (cheap, overdue).**
Not fancy models: R3's per-year folds + existing vol/spread states conditioning (R5). The
evidence that this matters is already in-house: VALID/TRAIN ratios of 2–41× (§A3-W2), pair
rotation, gold-bull artifacts. A strategy whose entire pooled EV comes from 2023-24 should be
sized differently from one positive 7/9 years — today the system cannot see the difference.

**C6. Portfolio construction (correlation, joint DD, sizing) — YES (R4 is the v0).**
Formal optimizers (mean-variance, HRP) are premature for 2 strategies; trade-stream overlap +
correlation + joint-DD + a pre-registered correlation haircut rule is the right scale. Revisit
HRP at 5+ uncorrelated streams. Kelly-style sizing: compute the number, then deploy a fixed
fraction (¼ Kelly) *capped by FTMO daily-loss arithmetic from R4(e)* — the prop-firm constraint,
not growth-optimality, is binding.

**C7. Doctrine challenges (my external-reviewer obligations):**
1. **"Walk-forward" naming** (`strategy_lab.py:6`, CHIEF_STATUS): S2 is a static split. Rename or
   make it roll (R3). Words shape expectations.
2. **"m = all cells" as honesty doctrine:** counting every cell is presented as conservative
   honesty, but with ~17 correlated cells per combo it is not a virtue — it is a power leak that
   killed 86 nr7 siblings (B3a) and then required *new* holdout batches (S3b) to resurrect two of
   them, spending virgin data to fix a statistics choice. Correlation-aware multiplicity (C1) is
   both more honest and more powerful. The doctrine should say "m accounts for ALL selection,
   correlation-aware" not "m = cell count".
3. **One-shot holdout as the supreme court:** a single 16-month window is itself one regime draw.
   S3's binary PASS/FAIL creates cliff-edge incentives (SIB-1 passed by 0.001 nominal; corrected,
   by 0.002 of BH slack). Keep the one-shot discipline, but (a) use interval estimates, not just
   binary verdicts, in the record; (b) make deployment contingent on forward tranches (R2.3, R6)
   so that a lucky holdout cannot alone carry capital.
4. **Per-run FDR budgets on a reused window** (W3): future cycles testing *any* family already
   validated on 2023-24 should not present q=0.10 on that window as a fresh guarantee. Either
   move validation forward (rolling origin as data accumulates) or tighten q per revisit.

---

## Bottom line

The system's discipline is real and its two proven strategies are probably (not certainly) real
but small: my corrected estimate for STRAT-001 is EV ≈ +1.4–1.9 pips/trade (p≈0.027 single-test)
with a cost structure that consumes a third of gross and a win-margin of ~2 SE; STRAT-002 similar
with better cost geometry. The research factory's biggest returns now come not from new mining
but from: honest uncertainty (bootstrap/RW — R1), regime accounting (R3), portfolio risk (R4),
cost stress (R5), and pre-committed monitoring (R6). The pending S3-C2 should run on the virgin
H4 window only under leak-priced, family-level, bootstrap-based criteria with a forward
deployment gate (R2) — and everyone should expect the survivor EVs to shrink by half or more,
because the system's own artifacts now prove that they do.

*SCIENTIST-D · External review · All recomputations from committed artifacts; no virgin window
touched. Reproduction: `scripts/scientist_d_recompute.py`.*
