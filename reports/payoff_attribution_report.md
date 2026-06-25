# Payoff Attribution — context inafanya kazi kupitia SABABU gani? (Phase 5.6, Tier 1)

*2026-06-25 19:50 | components: volatility, activity, spread, state_age, transition | spread = max−min ya AvgWin/AvgLoss/P(win) kuvuka states za component | outcome = forward net | Group A=reward, B=loss*

> **Q-009 (Chief):** Kwa NINI context inasababisha reward expansion (Group A: MR, Deep PB) au loss compression (Group B: PB, TC)? Tunaganua context kuwa components na kupima nani anabeba AvgWin (reward) au AvgLoss (loss) separation. Causality, sio EV. NO ML.


## mean_reversion — Group A (Reward Expansion)

| component | ΔAvgWin | ΔAvgLoss | ΔP(win) | groups |
|-----------|---------|----------|---------|--------|
| volatility | 5.6 | 5.7 | +1pp | 3 |
| activity | 5.2 | 4.9 | +1pp | 3 |
| spread | 2.9 | 3.2 | +0pp | 2 |
| state_age | 1.0 | 1.7 | +1pp | 4 |
| transition | 2.5 | 3.5 | +1pp | 3 |

→ **mean_reversion**: reward-driver = **volatility** (ΔAvgWin 5.6); loss-driver = **volatility** (ΔAvgLoss 5.7). Mechanism ya event hii (reward expansion) inahusishwa zaidi na **volatility**.

## pullback — Group B (Loss Compression)

| component | ΔAvgWin | ΔAvgLoss | ΔP(win) | groups |
|-----------|---------|----------|---------|--------|
| volatility | 4.5 | 5.7 | +1pp | 3 |
| activity | 4.7 | 5.3 | +0pp | 3 |
| spread | 0.5 | 1.0 | +1pp | 2 |
| state_age | 1.5 | 1.9 | +1pp | 4 |
| transition | 2.6 | 2.6 | +0pp | 3 |

→ **pullback**: reward-driver = **activity** (ΔAvgWin 4.7); loss-driver = **volatility** (ΔAvgLoss 5.7). Mechanism ya event hii (loss compression) inahusishwa zaidi na **volatility**.

## deep_pullback — Group A (Reward Expansion)

| component | ΔAvgWin | ΔAvgLoss | ΔP(win) | groups |
|-----------|---------|----------|---------|--------|
| volatility | 5.6 | 4.7 | +0pp | 3 |
| activity | 5.3 | 4.7 | +1pp | 3 |
| spread | 1.3 | 0.2 | +1pp | 2 |
| state_age | 1.9 | 1.6 | +1pp | 4 |
| transition | 2.7 | 2.5 | +1pp | 3 |

→ **deep_pullback**: reward-driver = **volatility** (ΔAvgWin 5.6); loss-driver = **activity** (ΔAvgLoss 4.7). Mechanism ya event hii (reward expansion) inahusishwa zaidi na **volatility**.

## trend_continuation — Group B (Loss Compression)

| component | ΔAvgWin | ΔAvgLoss | ΔP(win) | groups |
|-----------|---------|----------|---------|--------|
| volatility | 5.4 | 5.4 | +1pp | 3 |
| activity | 4.8 | 5.3 | +0pp | 3 |
| spread | 2.9 | 2.0 | +1pp | 2 |
| state_age | 1.7 | 1.3 | +0pp | 4 |
| transition | 3.4 | 2.5 | +1pp | 3 |

→ **trend_continuation**: reward-driver = **volatility** (ΔAvgWin 5.4); loss-driver = **volatility** (ΔAvgLoss 5.4). Mechanism ya event hii (loss compression) inahusishwa zaidi na **volatility**.

## VERDICT — components zinazobeba payoff mechanism (jumla kuvuka Tier 1)

- **Reward (AvgWin) drivers**, juu→chini: volatility (21.1), activity (20.0), transition (11.2), spread (7.5), state_age (6.1)
- **Loss (AvgLoss) drivers**, juu→chini: volatility (21.4), activity (20.2), transition (11.1), state_age (6.5), spread (6.4)

→ Payoff Engine (Phase 6) ijengwe juu ya components hizi (sababu halisi), sio context score ya jumla. Reward-mechanism inaongozwa na **volatility**; loss-mechanism na **volatility**.

*Attribution = mchango wa component kwa AvgWin/AvgLoss separation (sababu ya payoff mechanism, F-011). Sio prediction wala EV upya. Hii ndiyo daraja descriptive→predictive: Payoff Engine (Phase 6) itatabiri DISTRIBUTION juu ya components hizi. NO ML bado (Chief). Profitable ≠ Tradable Edge.*