# Interaction Stability — je interactions zina survive cross-market? (Phase 5.8, Tier 1)

*2026-06-25 22:57 | per-pair cell EV → rank consistency (Spearman), CV, modal best cell | min n/cell/pair=50, min pairs=4 | outcome = forward net*

> **Q-011 (Chief):** Phase 5.7 ilipata interaction bora (cells) lakini HAIKUPIMA stability. Je cell bora kwenye EURUSD ni bora kwenye GBPUSD? Rank consistency juu = **UNIVERSAL RULE**; chini = **ADAPTIVE/LOCAL RULE**. Interaction Engine inahitaji UNIVERSAL. NO ML.

## Stability kwa event × interaction

| Event | interaction | rank consist | CV med | modal best cell | modal freq | pairs | verdict |
|-------|-------------|--------------|--------|-----------------|-----------|-------|---------|
| mean_reversion | volatility×activity | +0.07 | 4.2 | NORMAL×NORMAL | 33% | 9 | — adaptive/local |
| mean_reversion | volatility×transition | +0.20 | 2.5 | HIGH×Tmid | 44% | 9 | — adaptive/local |
| mean_reversion | activity×state_age | +0.22 | 2.2 | HIGH×4-8 | 33% | 9 | — adaptive/local |
| mean_reversion | transition×state_age | +0.19 | 2.1 | Thi×4-8 | 44% | 9 | — adaptive/local |
| mean_reversion | vol×act×transition | +0.09 | 2.7 | LOW×HIGH×Thi | 22% | 9 | — adaptive/local |
| pullback | volatility×activity | +0.03 | 0.8 | NORMAL×LOW | 33% | 9 | — adaptive/local |
| pullback | volatility×transition | +0.01 | 1.1 | NORMAL×Tlo | 33% | 9 | — adaptive/local |
| pullback | activity×state_age | -0.01 | 0.9 | LOW×1-3 | 22% | 9 | — adaptive/local |
| pullback | transition×state_age | -0.02 | 1.1 | Thi×16+ | 33% | 9 | — adaptive/local |
| pullback | vol×act×transition | +0.01 | 1.4 | HIGH×HIGH×Tmid | 22% | 9 | — adaptive/local |
| deep_pullback | volatility×activity | +0.06 | 1.1 | LOW×NORMAL | 33% | 9 | — adaptive/local |
| deep_pullback | volatility×transition | +0.00 | 0.9 | HIGH×Tmid | 33% | 9 | — adaptive/local |
| deep_pullback | activity×state_age | +0.02 | 1.3 | NORMAL×9-15 | 33% | 9 | — adaptive/local |
| deep_pullback | transition×state_age | -0.03 | 1.2 | Thi×4-8 | 33% | 9 | — adaptive/local |
| deep_pullback | vol×act×transition | +0.04 | 2.1 | LOW×HIGH×Thi | 22% | 9 | — adaptive/local |
| trend_continuation | volatility×activity | +0.14 | 0.8 | NORMAL×LOW | 22% | 9 | — adaptive/local |
| trend_continuation | volatility×transition | +0.12 | 1.1 | NORMAL×Tlo | 44% | 9 | — adaptive/local |
| trend_continuation | activity×state_age | +0.12 | 0.8 | HIGH×1-3 | 22% | 9 | — adaptive/local |
| trend_continuation | transition×state_age | +0.07 | 0.9 | Thi×4-8 | 33% | 9 | — adaptive/local |
| trend_continuation | vol×act×transition | +0.07 | 1.3 | NORMAL×HIGH×Tlo | 33% | 9 | — adaptive/local |

## VERDICT — Q-011: interactions ni universal au local?

- Universal interactions: **0/20** (rank consistency ≥0.3 NA modal best ≥50% pairs).

→ ⚠️ **Interactions nyingi ni LOCAL** (adaptive). Interaction Engine lazima iwe ADAPTIVE per-pair, sio universal rules. Hii ni finding muhimu kabla ya kujenga engine.

*Rank consistency = wastani Spearman ya cell-EV ordering kati ya pairs (juu = ordering ileile kila pair = universal). CV = mtawanyiko wa cell EV kuvuka pairs (ndogo = stable). Modal best = cell bora inayojirudia. Universal -> Interaction Engine ya rules; Local -> engine adaptive. NO ML bado (Chief). Profitable ≠ Tradable Edge.*