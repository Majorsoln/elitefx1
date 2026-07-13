# WAVE-1 (R1 · R4 · R5 · R6) — Implementation Report

*2026-07-12 | IMPLEMENTER-A | SCIENTIST-D data_science_review §B designs + Chief directive |
Rules 1-8 | NO ML | R1 = GATE ya sequencing ya B-PRIME (kabla ya S3-C2 registration)*

> **WAVE-1:** R1 bootstrap p-engine (engine swap pre-registered kwa commit hii, KABLA ya dirisha
> jipya) · R4 portfolio v0 · R5 cost stress · R6 win-rate control chart. Zote self-tested, bila data
> ya nje, Windows-safe (ASCII). Format: Rule 8.

---

## Implementation Report

### R1 — `pvalue_boot` (strategy_lab.py) — ENGINE RASMI ya FDR/registration

`pvalue_boot(pnls, B=10_000, mean_block=3, cell=...)`: one-sided p (H0 mean≤0) kwa **stationary
block bootstrap** (Politis-Romano) yenye **studentization ya Newey-West** (percentile-t); series
ina-center (H0 kweli); `p = (1+#{t* ≥ t_obs})/(B+1)`; seed deterministic kutoka cell key
(`_seed_from_key`). **Engine swap kwenye `write_outputs`:** BH-FDR sasa juu ya `p_boot`; `p_z`
(z-test ya zamani) inabaki **sensitivity column** — kila FDR report ni **two-column** (restatement
ya design 3 inatoka moja kwa moja kwenye re-run ya `--split validation`). `--cells-file` mpya:
re-run ya cells maalum ZILIZOFUNGULIWA (S3/S3b) bila grid — split guards (holdout token) zinabaki.

**⚠️ DEVIATIONS 2 kutoka design verbatim — kwa EVIDENCE (kwa referee/Chief):**

Design ilisema *"geometric block length ~10 trades… prefer studentized"*. Nilitekeleza verbatim
kwanza, kisha nikapima size kwa MC (nulls za §A3-W1; M=2500-3000, B=500-600, N=100):

| Variant | skew-null (+1/−2 @⅔) | skew-null (win69) | AR-cluster (ρ=0.5) null |
|---|---|---|---|
| z-test (ya zamani) | 0.068 ✗ (W1) | 0.051 | 0.121 ✗ |
| **verbatim**: block10 + i.i.d.-sd studentization | 0.063 ✗ | 0.072 ✗ | — |
| block10 non-studentized | 0.093 ✗ | 0.088 ✗ | — |
| i.i.d. (block=1) studentized | 0.042 ✓ | 0.041 ✓ | 0.100 ✗ |
| block10 + **NW** studentization | 0.063 ✗ | 0.066 ✗ | 0.056 ✓ |
| **block=3 + NW studentization (CHAGUO)** | **0.053 ✓** | **0.043 ✓** | **0.058 ✓** |

**Chanzo cha tatizo (kilichogunduliwa kwa vipimo):** block averaging inameza skewness ya t\*
(skew ya block-means ~ γ/√b) — kwa mean_block=10 na N~100, **acceptance test (b) ya design
yenyewe haiwezekani** (boot size 0.063-0.072 ≈ z, hakuna correction). Deviation:
**(i) mean_block=3** (badala ya ~10) na **(ii) studentization = Newey-West K=mean_block** (badala
ya i.i.d. sd — denominator inayoendana na block dependence). Mchanganyiko huu unafaulu ZOTE:
skew ~nominal NA dependence-null 0.058 (vs z 0.121). Power @N=300, EV>0 halisi: 0.61.
`mean_block` ni parameter — referee/Chief wakitaka thamani nyingine, mstari mmoja.

### R4 — `portfolio_v0.py` (MPYA)

`analyze(tradesA, tradesB, daysA, daysB, ...)`: (a) fraction ya siku zote mbili zinafire;
(b) fraction ya saa zote mbili zina positions (lower/upper bound kwa day-level hours); (c) daily-PnL
corr (union ya siku, realized siku ya exit); (d) max joint DD vs sum-of-individual; (e) worst joint
day (pips + $) vs FTMO daily-loss $500. **RULE pre-registered:** corr > 0.4 → **halve size** (flag
`halve_size` auto). `run()` inasoma windows zilizofunguliwa (reuse `load_window`/`episodes`;
holdout = token). Data run = Operator.

### R5 — `cost_stress.py` (MPYA) + integration

(1) `ev_spread_table` — **EV(Δspread) analytic** (EV−Δ; +0.2/+0.5/+1.0 + breakeven Δ) sasa
inaprintiwa kwenye **kila** `strategy_lab` report (survivors au top-10). (2) `spread_split(trades,
spread_state)` — EV_NORMAL vs EV_WIDE kwa entry bar; EV_WIDE<0 → verdict ya **WIDE-skip kwenye
DEPLOYMENT policy** (SIO backtest — episodes() haijaguswa, byte-identical inabaki) + forward-verify.
(3) `stop_slippage_percentile(spreads, pct=95)` — GOLD: percentile-based stop slippage kutoka
empirical tick spreads; deliverable = NAMBA + assumption wazi; **kuiingiza kwenye cost model =
Chief approval** (sio silent change). Gold registration inabaki BLOCKED hadi hapo (ruling).

### R6 — `winrate_monitor.py` (MPYA) — thresholds PRE-REGISTERED SASA

Registry: STRAT-001 (w_be 68.3%, holdout 73.9%/N303) — REVIEW<70.0% · HALT<66.0% @60-trade
(zilizotolewa). **STRAT-002 kwa framework ILEILE (offsets zilezile juu ya w_be: +1.7pp/−2.3pp):
REVIEW<54.0% · HALT<50.0%** — zime-pre-register HAPA kabla forward data haijaongezeka (self-test [1]
inathibitisha ulinganifu wa offsets). Statistical alarm: posterior mean (Beta prior kutoka holdout)
< w_be + 1·SE. Status: OK/REVIEW/HALT/WARMUP. `results_from_paper_log` — adapter ya paper log (E3).

**Interpretation note (kwa referee):** "1 SE" = SE ya **posterior** (n_eff = N_holdout + n_forward),
SIO SE ya rolling-60 flat — SE@60 (6.4pp) ingekuwa JUU ya margin ya STRAT-002 (5.5pp): alarm
isingefikiwa kimuundo hata kwa holdout performance. Imeandikwa kwenye code + hapa.

## Self Tests

```text
strategy_lab   PASS (+3): [7] symmetric null |p_boot−p_z|=0.025 · [8] W1 skew-null size z=0.058→boot=0.045
                          (~nominal, <z) · [9] determinism kutoka cell key (bit-identical; keys differ)
portfolio_v0   PASS (4): correlated→corr=1.0/HALVE · disjoint→corr≈0/no-halve · joint-DD≤sum +
                          worst-day −$720 → FTMO breach flag · determinism
cost_stress    PASS (4): EV−Δ exact · spread_split (WIDE<0→skip-verdict; WIDE≥0→no-skip) ·
                          gold p95/2 + small-sample guard
winrate_monitor PASS (6): framework offsets S1==S2 · healthy→OK · 65%→HALT/68.3%→REVIEW ·
                          statistical alarm · warmup · paper-log adapter
FULL SWEEP: 21/21 PASS (18→21; regression zote salama — episodes()/C1/C2 hazikuguswa)
```

## Known Limitations

1. **R1 deviations (mean_block=3 + NW) zinahitaji ridhaa ya SCIENTIST-D referee** — design ilisema
   ~10; vipimo vyangu vinaonyesha ~10 inashindwa acceptance test ya design yenyewe. Evidence table
   juu; MC scripts reproducible (seeds fixed). Hii ndiyo hatua ya referee kwenye sequencing.
2. **Sensitivity restatement (R1 design 3) inahitaji data** — machinery ipo (two-column default +
   `--cells-file`); run halisi (validation + opened S3/S3b cells) = Operator/Chief (holdout token
   kwa cells za S3 zilizofunguliwa — hakuna dirisha jipya).
3. **R4 `usd_per_pip=12` ni placeholder ya intended sizing** (risk $120/SL~10pips scale) — sizing
   halisi inatoka MWONGOZO/E4 kwa kila trade; worst-day $ ni approximate hadi Operator alete
   per-trade sizing halisi. Hours-overlap ni day-level bound (lower/upper), si bar-aligned join.
4. **R5(3) gold slippage assumption**: stop fill = half-spread ya p95 — Chief a-approve kabla ya
   matumizi; flat 0.3-pip inabaki kwenye harness hadi hapo (hakuna silent cost-model change).
5. **R6 w_be/holdout params ni za review** (68.3/52.3 n.k.) — kama costs zikibadilika (R5 ikionyesha
   spreads halisi tofauti), w_be lazima zi-restate na Chief.
6. **R1 power @N=100 ni ndogo** (kama z) — MDE screen ya B-PRIME (EP-8) ndiyo inayoshughulikia hili.

## Open Questions

1. **R1 calibration approval (BLOCKER ya S3-C2):** referee/Chief wakubali mean_block=3 + NW
   studentization (evidence table juu) au waelekeze vinginevyo? Parameter change = mstari mmoja +
   re-calibration table.
2. **Restatement run:** nani anaendesha (`--split validation` + `--cells-file` ya S3/S3b cells)?
   Napendekeza Operator na runbook fupi; cells za S3 zinahitaji holdout token (zimefunguliwa tayari).
3. **R6 alarm-line interpretation** (posterior SE vs rolling SE) — referee athibitishe.
4. **R4 sizing halisi** — worst-day $ ipimwe tena na per-trade sizing ya MWONGOZO (E4 data).

---

*WAVE-1: R1 pvalue_boot (stationary bootstrap + NW studentization, mb=3 — calibrated kwa evidence;
FDR rasmi = p_boot, p_z = sensitivity; engine swap pre-registered kwa commit hii) · R4 portfolio v0
(corr>0.4→halve, pre-registered) · R5 cost stress (EV(Δspread) kila ripoti; WIDE-split; gold p95
slippage) · R6 win-rate chart (STRAT-002 thresholds pre-registered SASA). Sweep 21/21. NO ML.
Profitable ≠ Tradable Edge. Protect capital first.*
