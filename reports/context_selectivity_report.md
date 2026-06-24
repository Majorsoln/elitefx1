# Context Selectivity — je context ni ranking engine au binary filter? (Phase 3.5)

*2026-06-24 19:08 | context score = online prequential EV ya (vol_state, age-bucket) | deciles + Top X% | outcome forward 6 bars net ya spread | aggregate pairs×TFs*

> **Q-005 (Chief):** Phase 3 ilionyesha 'favorable ≈ 99%' = context binary ni PERMISSIVE mno. Hapa tunapanga events kwa CONTEXT SCORE (deciles). EV ikipanda na decile -> Context = RANKING ENGINE (discrimination ipo). EV flat -> hakuna selectivity. NO ML, NO triple barrier.


## pullback — EV/Win/Count kwa decile ya context score (D1=chini → D10=juu)

| decile | EV (pips) | Win% | n |
|--------|-----------|------|---|
| D1 | -3.16 | 47% | 32,869 |
| D2 | -1.96 | 47% | 32,869 |
| D3 | -1.41 | 47% | 32,869 |
| D4 | -1.24 | 47% | 32,870 |
| D5 | -1.10 | 48% | 32,869 |
| D6 | -1.31 | 47% | 32,869 |
| D7 | -1.06 | 48% | 32,870 |
| D8 | -1.14 | 48% | 32,869 |
| D9 | -0.34 | 48% | 32,869 |
| D10 | +1.29 | 51% | 32,870 |

*Top X% kwa context score (pullback):*

| bucket | EV (pips) | Win% | n |
|--------|-----------|------|---|
| Top 10% | +1.29 | 51% | 32,869 |
| Top 20% | +0.48 | 50% | 65,738 |
| Top 30% | -0.06 | 49% | 98,607 |
| Top 50% | -0.51 | 48% | 164,346 |
| All | -1.14 | 48% | 328,693 |

→ **pullback**: D10−D1 EV = +4.45 pips, monotonic steps 7/9 → ✅ RANKING (discrimination)

## breakout — EV/Win/Count kwa decile ya context score (D1=chini → D10=juu)

| decile | EV (pips) | Win% | n |
|--------|-----------|------|---|
| D1 | -3.80 | 46% | 14,937 |
| D2 | -2.34 | 47% | 14,938 |
| D3 | -2.13 | 47% | 14,938 |
| D4 | -1.82 | 47% | 14,937 |
| D5 | -1.50 | 46% | 14,938 |
| D6 | -1.56 | 46% | 14,938 |
| D7 | -0.92 | 47% | 14,937 |
| D8 | -0.93 | 48% | 14,938 |
| D9 | -0.90 | 48% | 14,938 |
| D10 | -0.32 | 50% | 14,938 |

*Top X% kwa context score (breakout):*

| bucket | EV (pips) | Win% | n |
|--------|-----------|------|---|
| Top 10% | -0.32 | 50% | 14,937 |
| Top 20% | -0.61 | 49% | 29,875 |
| Top 30% | -0.72 | 49% | 44,813 |
| Top 50% | -0.93 | 48% | 74,688 |
| All | -1.62 | 47% | 149,377 |

→ **breakout**: D10−D1 EV = +3.48 pips, monotonic steps 7/9 → ✅ RANKING (discrimination)

## mean_reversion — EV/Win/Count kwa decile ya context score (D1=chini → D10=juu)

| decile | EV (pips) | Win% | n |
|--------|-----------|------|---|
| D1 | -1.58 | 49% | 33,848 |
| D2 | -1.27 | 48% | 33,848 |
| D3 | -0.74 | 49% | 33,848 |
| D4 | -0.76 | 49% | 33,848 |
| D5 | -0.65 | 49% | 33,849 |
| D6 | -0.50 | 50% | 33,848 |
| D7 | -0.38 | 49% | 33,848 |
| D8 | -0.06 | 50% | 33,848 |
| D9 | +0.33 | 50% | 33,848 |
| D10 | +2.29 | 52% | 33,849 |

*Top X% kwa context score (mean_reversion):*

| bucket | EV (pips) | Win% | n |
|--------|-----------|------|---|
| Top 10% | +2.29 | 52% | 33,848 |
| Top 20% | +1.31 | 51% | 67,696 |
| Top 30% | +0.85 | 51% | 101,544 |
| Top 50% | +0.33 | 50% | 169,241 |
| All | -0.33 | 50% | 338,482 |

→ **mean_reversion**: D10−D1 EV = +3.86 pips, monotonic steps 8/9 → ✅ RANKING (discrimination)

## VERDICT — Q-005: Context = Ranking Engine au Binary Filter?

✅ **Context = RANKING ENGINE** (3/3 events: EV inapanda na context score). Sio pass/fail — ni mfumo wa kupanga (decile). Phase 4 (Event × Context Matrix) itumie context kama SCORE/rank, sio threshold ya binary.

*Score = online prequential EV ya (vol_state, age-bucket), no-lookahead (past instances tu; H-horizon overlap kama Phase 1.9). Deciles zinajibu 'discrimination ipo?'. Hii inafafanua MAANA ya context (ranking vs filter) kabla ya Phase 4. NO ML/triple barrier (Chief). Metric = EV (net pips). 'favorable' ya binary (Phase 3) imeachwa — ilikuwa permissive mno.*