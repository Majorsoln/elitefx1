# MEMORY — STRATEGIST-M (Market Strategist)

**Jukumu:** mtaalamu wa STRATEGIES + ENTRIES. Top-down: HTF context → 15m/30m trigger.
Ninaanzisha MZUNGUKO-2 (best strategies). Sithibitishi mwenyewe — nawasilisha HYPOTHESES;
gate ya PROVEN ni ya Chief (`docs/STRATEGIES.md`).

## SOMA KILA SESSION (kwa order)
1. `docs/CYCLE2_CHARTER.md` — charter + ushauri wa Chief (muundo mzima).
2. `docs/STRATEGIES.md` — STRAT-001/002 (HAZIGUSWI) + gate.
3. `docs/lessons/LESSON_INDEX.md` + lessons — makosa ya zamani.
4. `src/research/event_library_v2.py`, `event_quality_report.py`, `strategy_lab.py`,
   `family_pooled.py` — jinsi signal/harness/context-filter vinavyofanya kazi.
5. `config/data_config.yaml` — pairs 12 + gharama (max_spread).

## KANUNI ZANGU (kutoka lessons)
- Kila sheria = NAMBA/feature. Hakuna curve-fit ya macho, hakuna post-hoc.
- HTF-context = filter ON signals (kabla ya episodes).
- Decidability: vol/context = signal-bar; session = entry-bar. Hakuna look-ahead.
- Costs halisi (spread+slippage). "Best 10" = hypothesis-list, si proven.
- Holdout/madirisha bikira HAYAGUSWI. Tabia-kwa-pair = TRAIN/VALID pekee.
- STRAT-001/002 HAZIBADILIKI.

## CURRENT TASK
C2-1 IMEKAMILIKA (2026-07-14). Nasubiri Chief review (C2-2: chagua testable subset + freeze
grid). Kazi yangu ijayo: C2-5 (tabia-kwa-pair kwa survivors, TRAIN/VALID pekee — mpango §4
wa ripoti; thresholds za uainishaji tayari zime-pre-register humo).

## HISTORIA
- **2026-07-14 (C2-1):** `reports/cycle2_strategy_hypotheses.md` — BEST 10 hypotheses, ranked:
  HC2-01 ALIGNED-COMPRESSION (30m nr7/nr4 one-sided, d1+h4 trend aligned) · HC2-02 LONDON-ORB-D1
  (15m) · HC2-03 TREND-PULLBACK-RESUME (30m) · HC2-04 NESTED-SQUEEZE (h4 LOW-vol + 30m squeeze) ·
  HC2-05 ALIGNED-SHOCK (15m) · HC2-06 HTF-SR-FADE · HC2-07 GAP-FADE-QUIET · HC2-08
  NY-HANDOFF-DRIFT · HC2-09 ASIA-RANGE-MR · HC2-10 FAILED-BREAK-SWEEP (event mpya `false_break`).
  Muundo: #1–5 continuation/expansion (priors kali: STRAT-001/002 + C2-WATCH), #6–10
  reversion/structure (diversification ya mechanism).
- **Features nilizoainisha kwa Chief/IMPLEMENTER-A (§3 ya ripoti):** (1) context loader —
  join ya context parquet kwenye load_window (additive); (2) `_mask_context_dir` — direction-aware
  mask (allow_long/allow_short kwenye signal bar) — kipande kikuu, kinahudumia 7/10;
  (3) event fn MOJA mpya `false_break` (sweep-reversal, PAST-bars levels); (4) params mpya za
  grid (session_orb 15m London; london_drift open_hr=12). Triggers 9/10 tayari zipo EVENTS_V2.
- **OOB 3 (§5):** usd_strength composite (cross-pair d1_trend_sign) · day-of-week structure
  (Friday-NY reversion / Monday continuation) · vol-state-TRANSITION kama trigger.
- **Risks nilizoinua kwa Chief (§6):** power vs m (pendekezo: family-pooled FDR pale mechanism
  moja); 15m cost trap (HC2-02/05 — fallback 30m ni PRE-S2 tu); overlap ya mechanisms
  (01/04 na 06/10) kwa portfolio; XAUUSD spread provisional lazima ithibitishwe kabla ya S1.
