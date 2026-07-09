# Cycle-2 — GRID_C2 + Strength Framework + Exit Science (Implementation Report)

*2026-07-09 | IMPLEMENTER-A | Alpha Cycle-2 (Chief directive 2026-07-09) | Rules 1-8 | NO ML |
research harness (numpy) — SIO Engine core*

> **Cycle-2 = diversification pre-registration.** (1) GRID_C2 (events 4 mpya + H4 cost-remedy);
> (2) `strength_lab.py` (currency strength → usd_drift); (3) EXIT SCIENCE (episodes() exit variants,
> **default BYTE-IDENTICAL**). Hizi ni hypotheses AMBAZO HAZIJAPIMWA (code + self-test tu) — zinasubiri
> S1-C2→S2-C2→S3-C2 (data ndiyo hakimu; EP-3: hakuna kinacholisha AI bila OOS proof). Format: Rule 8.

---

## Implementation Report

**1. GRID_C2 (strategy_lab.py — HAIGUSI TIER1/TIER2 za C1):**
- `grid_c2(pairs, tf)`: **H1** = events 4 mpya `{squeeze_break, nr4_inside, gap_fade, london_drift}`;
  **H4** = cost-remedy set `{nr7_break, squeeze_break, nr4_inside, shock_follow}` (H-C2-1/2). Pairs 9 ×
  SL/TP grid ileile × filters `{None, no-LATE}`; vol `{None}`.
- `--cycle {1,2}` flag; cycle 2 → outputs tofauti (`candidates_c2.jsonl`, `strategy_lab_report_c2.md`)
  ili C1 (STRAT-001/002 winners) isiandikwe juu. FDR m = cells za C2 (pre-registration tofauti).

**2. `strength_lab.py` (MPYA — H-C2-5, currency strength):**
- `usd_strength(closes_by_pair, window)`: USD strength index = wastani wa trailing returns za USD
  (base-USD `+r`, quote-USD `−r`). **NO-LOOKAHEAD** (r[i] = c[i]/c[i−window]−1; truncation-invariant, self-tested).
- `usd_drift(pair, usd_str, k)`: event — USD ikisimama (`usd_str > k·std`), base-USD (USDJPY) → long,
  quote-USD (EURUSD) → short. Edge-triggered + rearm. Non-USD pairs (EURJPY/EURGBP) → zero signal.
- Backtest: `episodes()` iliyokaguliwa (costs; SIBADILISHI). `run()` inalign pairs kwa `ts` (inner join).

**3. EXIT SCIENCE (event_quality_report.py — H-C2-6):**
- `episodes(..., exit_cfg=None)`: **default path HAIGUSWI** (imefungwa chini ya `if exit_cfg is None:` —
  textually identical) → **BYTE-IDENTICAL** (golden hashes zilizonaswa KABLA: mr_zscore `28cc2218…`,
  nr7 SL2/TP1 `872edc44…`; self-test inathibitisha).
- `_exit_variant()`: **trailing** (k×ATR, best-price trail), **breakeven** (SL→entry baada ya +rR),
  **time** (exit bars N). Intrabar convention = sawa na default (SL/trailing kabla ya TP; tie→stop).
- `exit_sweep(cell, data)` (strategy_lab): sweep exit variants juu ya STRAT-001/002 (exploration;
  'fixed' == default byte-identical). Forward-confirm kabla ya kubadilisha strategy iliyothibitishwa.

## Self Tests — zote PASS (bila data halisi)

```text
strategy_lab.py   PASS: +[1c] grid_c2 (H1 events 4 mpya; H4 nr7+shock; filters {None,no-LATE}; C1 hazijaguswa)
                        +[6] exit_sweep (fixed==default N; variants 5 run)
strength_lab.py   PASS (MPYA): usd_strength(USD rising)>0 · NO-LOOKAHEAD · orientation (USDJPY long/EURUSD
                        short) · non-USD zero · backtest_pair (episodes+costs)
event_quality_report PASS: +[7] exit-science DEFAULT BYTE-IDENTICAL (golden match) + variants run
FULL SWEEP: 18/18 PASS (17->18 na strength_lab; harness iliyokaguliwa haijavunjika)
```

**Byte-identical ni ushahidi wa msingi:** kubadilisha `episodes()` hakukuvunja tabia ya default →
STRAT-001/002 (na candidates zote za C1) zinabaki reproducible bit-kwa-bit.

## Known Limitations

1. **Events 4 za C2 + usd_drift = hypotheses HAZIJAPIMWA** — self-test = correctness ya code, SIO
   utafiti. Uthibitisho = S1-C2→S2-C2→S3-C2 (data). OOS rules za uadilifu za Chief zinatumika (familia
   mpya kabisa 2025-26 one-shot; compression/shock-adjacent forward-only 2026-05+).
2. **strength_lab align kwa inner-join ya ts** — pairs zenye timestamps tofauti zinapunguza sampuli;
   Operator athibitishe coverage. usd_drift threshold (k/std_win) = defaults, si tuned (S1-C2 ita-grid).
3. **Exit variants intrabar convention** — trailing/breakeven zinatumia same-bar order (stop kabla ya
   TP); intrabar path halisi (je +1R ilifikwa kabla ya breakeven?) haijulikani kwa OHLC — conservative
   assumption, imeandikwa. Exploration tu.
4. **H4 data** — GRID_C2 H4 inahitaji state parquet za H4 (Operator). Grid logic ni tf-agnostic; data ndiyo tofauti.
5. **strategy_lab/strength_lab = research harness** (numpy) — SIO Engine core; purity ya core (P107) haijaguswa.

## Open Questions

1. **usd_drift params (k, std_win)** — S1-C2 i-grid au defaults? Pendekezo: grid ndani ya S1-C2 (kama SL/TP).
2. **Strength beyond USD** — je tuongeze EUR/JPY strength indices (multi-currency), au USD tu kwa C2?
   Pendekezo: USD tu sasa (spec-light); panua ikithibitika.
3. **Exit-grid promotion** — exit_sweep juu ya STRAT-001/002 ni exploration; ikionyesha uboreshaji,
   je inahitaji OOS mpya (forward) kabla ya kubadilisha strategy PROVEN? Pendekezo: NDIYO (EP-3;
   strategy iliyothibitishwa haibadilishwi bila forward-confirm).
4. **GRID_C2 event params** — kama C1, nimebaki SL/TP+filter (si event-internal params). Sawa? Pendekezo: ndiyo.

---

*Cycle-2: GRID_C2 (--cycle 2, tf-aware; C1 haijaguswa) + strength_lab.py (usd_drift, NO-LOOKAHEAD,
reuse episodes) + EXIT SCIENCE (episodes exit_cfg; default BYTE-IDENTICAL — golden verified; trailing/
breakeven/time + exit_sweep). Sweep 18/18 PASS. Hypotheses HAZIJAPIMWA — S1-C2→S3-C2 ndiyo hukumu
(EP-3). NO ML. Profitable ≠ Tradable Edge. Protect capital first.*
