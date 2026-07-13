# Strategy Lab (S1) — Implementation Report

*2026-07-09 | IMPLEMENTER-A | Alpha Engineering S1 (Chief directive + UPDATE 1/2 + GRID RULING
2026-07-09) | Rules 1-8 | NO ML | research harness (numpy) — SIO Engine core*

> **S1 = STRATEGY FACTORY.** GRID (EVENTS_V2 × pairs × SL/TP × context-filter) → backtest kwa
> `episodes()` ILIYOKAGULIWA (fill rules SIBADILISHI — Chief) → metrics kwa costs → candidates.
> Sacred splits enforced kwa code (HOLDOUT imezuiwa). BH-FDR machinery imo (S2). RED LINES:
> hakuna kuchagua kwa holdout; hakuna metric bila costs; survivors = CANDIDATES hadi S3. Format: Rule 8.

---

## Implementation Report

**Deliverable:** `src/research/strategy_lab.py` (+ imeongezwa kwenye `run_selftests.py` sweep).

**Vipengele (spec ya Chief 1-6 + GRID RULING):**

| # | Kipengele | Utekelezaji |
|---|-----------|-------------|
| 1 | **GRID** | `grid(pairs)` — TIER-1 pre-registered (nr7_break/second_chance/shock_follow/session_orb/inside_break/rsi2_pullback + pairs/session/vol filters halisi za RULING) + TIER-2 (8 events, default context) + STOP-BREAKOUTS (jump_off/breakout_stop, TP {2,3}R). SL{1,1.5,2}×TP{1,1.5,2,3}. Cells = **1,284** (synthetic-pair test). |
| 2 | **BACKTEST** | `evaluate()` inaita `episodes()` ya event_quality_report — **SIBADILISHI** fill rules (next-bar honest, tie→SL worst-case, costs kila trade). Context filter (`_match`) inaslicing trades kwa session/vol. |
| 3 | **SACRED SPLITS** | `load_window(sym, tf, split, token)` — TRAIN<2023 / VALIDATION 2023-24 / HOLDOUT≥2025. **RED LINE:** holdout inarefuse (`PermissionError`) bila `HOLDOUT_TOKEN` sahihi — **KABLA ya kusoma data**. |
| 4 | **METRICS** | N, EV net/trade (pips, costs ndani), win%, PF, maxDD (`_maxdd`), trades/day. RANK = `_population_rank` (EV chanya × log N — LESSON-033/034, si top-EV pekee). |
| 5 | **FDR** | `pvalue_gt0` (one-sided, normal approx stdlib erfc) + `bh_fdr` (Benjamini-Hochberg; m = cells zote tested; null baseline = expected false). Inatumika `--split validation/holdout` (out-of-sample pekee). |
| 6 | **OUTPUT** | `write_outputs` → `data/strategies/candidates.jsonl` (bila raw pnls) + `reports/strategy_lab_report.md`. |

**Reuse (Chief UPDATE 1):** `EVENTS_V2` (event_library_v2) + `episodes`/`_metrics`/`SESSIONS`
(event_quality_report). Fill semantics haziguswi.

**Modes:** `--split train` (S1 candidates, no FDR — in-sample) · `--split validation` (S2 walk-forward
+ BH-FDR) · `--split holdout` (S3, token-gated). `--self-test` (synthetic, bila data).

## Self Tests

`python strategy_lab.py --self-test` → **PASS** (bila data halisi):

```text
[1] grid: cells=1284 keys=OK pairs-scoped=OK tier-coverage=OK pre-reg=OK (inside_break=USDJPY pekee)
[2] evaluate: metrics + costs (EV=-2.17 kwenye synthetic — no free lunch)
[2b] context filter (HIGH kwenye NORMAL data -> None)
[3] BH-FDR math: k=3 survivors=[T,T,T,F,F] expected_false=0.3
[3b] pvalue: strong+ ~0.0000, noise ~0.41
[4] RED LINE holdout guard: no-token & wrong-token -> refuse (PermissionError)
[5] outputs (temp dir): candidates.jsonl bila pnls, split-labeled, report written
```

Regression: **FULL SWEEP 15/15 PASS** (14→15 na strategy_lab; hakuna kilichovunjika). Self-test
inaandika temp dir PEKEE — hakuna synthetic artifacts kwenye repo.

## Known Limitations

1. **TRAIN metrics ni in-sample** — S1 inatoa CANDIDATES, SIO edge. Uthibitisho = S2 (walk-forward
   VALIDATION + BH-FDR) na S3 (HOLDOUT mara moja). Profitable ≠ Tradable Edge.
2. **Event params = defaults** — grid ina-sweep SL/TP + context filters (kama RULING inavyosisitiza:
   "TP sweep" + session/vol), SIO kila param ya ndani ya event (short_len/k/n.k.). Kuongeza param-sweep
   = kupanua grid (na FDR m) — Open Q#1.
3. **Real run inahitaji data (PC ya Operator)** — `load_window` inasoma state parquet (polars). Self-test
   ni synthetic. Sikuweza kuendesha TRAIN/VALIDATION halisi hapa (R-1).
4. **pvalue ni normal-approx** (erfc), sio t-distribution kamili — kwa N kubwa (candidates zina N≥30,
   mara nyingi mamia) tofauti ni ndogo; kwa rigor ya juu, t-dist au bootstrap (Open Q#2).
5. **FDR independence assumption** — BH inadhani p-values huru/PRDS; candidates zinazogawana event/pair
   zina-correlate. BH-BY (conservative) au bootstrap-FDR = uboreshaji wa baadaye (S2 detail).
6. **maxDD ni pip-space, sio $/R** — sizing (MWONGOZO/E4) haijaunganishwa hapa; ni ranking metric.

## Open Questions

1. **Param-sweep depth** — je grid iongeze event-internal params (short_len/long_len/k/rearm/q...) au
   ibaki SL/TP + context (RULING)? Kila param-dim inaongeza cells → FDR m → bar ya survival. Pendekezo:
   baki na RULING (SL/TP+context) kwa S1; param-sweep = phase ya baadaye ikihitajika.
2. **p-value method** — normal-approx (sasa) vs t-dist vs bootstrap kwa metric-per-trade? Pendekezo:
   bootstrap kwa S2 (robust kwa fat tails za pnl); normal-approx inatosha kwa ranking wa S1.
3. **candidate promotion threshold** — S1 candidates.jsonl ina ZOTE N≥30. Je Chief anataka pre-filter
   (mf. EV>0 TRAIN) kabla ya S2, au S2 ipime zote? Pendekezo: peleka zote (pre-registration; S2 FDR
   inahesabu m halisi). RULING: "ZOTE bado zinapimwa S2."
4. **Walk-forward windows (S2)** — `--split validation` sasa inapima 2023-24 kwa ujumla. Walk-forward
   halisi (rolling train/test ndani ya validation) = uboreshaji; Chief aelekeze muundo.

---

*Strategy Lab S1 = GRID (EVENTS_V2 × pairs × SL/TP × context) → episodes() iliyokaguliwa → metrics+costs
→ candidates. Sacred splits enforced (HOLDOUT token-gated, RED LINE). BH-FDR + pvalue machinery (S2).
Population-view ranking (LESSON-033/034). Self-test 15/15 sweep PASS (synthetic, temp dir). Candidates
= CANDIDATES hadi S2/S3. NO ML. Profitable ≠ Tradable Edge. Protect capital first.*
