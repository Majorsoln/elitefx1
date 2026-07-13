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

## CURRENT TASK (C2-1)
Andika `reports/cycle2_strategy_hypotheses.md`: BEST 10 strategies kama hypotheses
(HTF-context + 15m/30m trigger + exit + hypothesis ya kiuchumi + pairs + rank), features
zinazohitajika kwa kila moja, mpango wa tabia-kwa-pair, na out-of-the-box 2-3.

## HISTORIA
- (tupu — mzunguko unaanza. Ongeza matokeo baada ya kila session.)
