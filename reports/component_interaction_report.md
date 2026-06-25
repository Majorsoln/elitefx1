# Component Interaction — je edge iko kwenye INTERACTION? (Phase 5.7, Tier 1)

*2026-06-25 20:56 | 2-way + 3-way interactions | cell = EV (pips) net | min n/cell = 100 | outcome = forward net | Group A=reward, B=loss*

> **F-012 / Q-010 (Chief):** marginal ≠ importance. Edge inaweza kuwa kwenye Vol×Act×Transition, sio component moja. Joint EV-spread > marginal spread -> interaction inaongeza discrimination. Pia: **Driver ≠ Gatekeeper** (Transition inaweza kuwa gate, sio driver). NO ML, NO Payoff Engine.


## mean_reversion — Group A (Reward)

### volatility×activity — EV (pips) per cell

| vol \ act | LOW | NORMAL | HIGH |
|----|----|----|----|
| LOW | -0.9 | -0.3 | -0.6 |
| NORMAL | -0.1 | +0.4 | +0.1 |
| HIGH | -0.3 | +0.0 | -0.2 |

→ joint EV-spread = 1.3 vs marginal max (vol/act) = 0.8 → ✅ interaction inaongeza discrimination

### volatility×transition — EV (pips) per cell

| vol \ trans | Tlo | Tmid | Thi |
|----|----|----|----|
| LOW | -0.9 | -0.1 | -0.6 |
| NORMAL | -1.5 | +0.2 | +0.1 |
| HIGH | -0.0 | +1.3 | -1.1 |

→ joint EV-spread = 2.8 vs marginal max (vol/trans) = 0.8 → ✅ interaction inaongeza discrimination

### activity×state_age — EV (pips) per cell

| act \ age | 1-3 | 4-8 | 9-15 | 16+ |
|----|----|----|----|----|
| LOW | -0.6 | -0.5 | -0.9 | -0.5 |
| NORMAL | +0.2 | +0.2 | +0.4 | -0.2 |
| HIGH | -0.6 | +0.7 | +0.5 | -0.4 |

→ joint EV-spread = 1.7 vs marginal max (act/age) = 0.7 → ✅ interaction inaongeza discrimination

### transition×state_age — EV (pips) per cell

| trans \ age | 1-3 | 4-8 | 9-15 | 16+ |
|----|----|----|----|----|
| Tlo | — | -0.4 | -0.6 | -0.5 |
| Tmid | +2.5 | +0.1 | +0.5 | +0.1 |
| Thi | -0.5 | +3.0 | +1.7 | -3.2 |

→ joint EV-spread = 6.3 vs marginal max (trans/age) = 0.8 → ✅ interaction inaongeza discrimination

### volatility×activity×transition — top/bottom EV cells

| rank | vol×act×trans | EV | n |
|------|---------------|----|---|
| top | HIGH×HIGH×Tmid | +2.4 | 7,081 |
| top | LOW×HIGH×Thi | +0.9 | 1,928 |
| top | HIGH×NORMAL×Tmid | +0.8 | 3,605 |
| bottom | HIGH×LOW×Tmid | -2.2 | 1,617 |
| bottom | NORMAL×NORMAL×Tlo | -2.6 | 1,010 |

→ 3-way EV range = **5.1 pips** (best HIGH×HIGH×Tmid +2.4 vs worst -2.6)

## pullback — Group B (Loss)

### volatility×activity — EV (pips) per cell

| vol \ act | LOW | NORMAL | HIGH |
|----|----|----|----|
| LOW | -0.8 | -1.8 | -0.9 |
| NORMAL | -1.0 | -0.9 | -1.2 |
| HIGH | -1.5 | -1.3 | -1.4 |

→ joint EV-spread = 1.1 vs marginal max (vol/act) = 0.4 → ✅ interaction inaongeza discrimination

### volatility×transition — EV (pips) per cell

| vol \ trans | Tlo | Tmid | Thi |
|----|----|----|----|
| LOW | -1.2 | -1.7 | -0.8 |
| NORMAL | +0.2 | -1.0 | -1.0 |
| HIGH | -1.5 | -1.3 | -0.3 |

→ joint EV-spread = 1.9 vs marginal max (vol/trans) = 0.5 → ✅ interaction inaongeza discrimination

### activity×state_age — EV (pips) per cell

| act \ age | 1-3 | 4-8 | 9-15 | 16+ |
|----|----|----|----|----|
| LOW | -0.6 | -1.1 | -0.6 | -1.2 |
| NORMAL | -1.1 | -1.3 | -1.4 | -1.3 |
| HIGH | -0.7 | -1.1 | -1.3 | -1.6 |

→ joint EV-spread = 1.0 vs marginal max (act/age) = 0.5 → ✅ interaction inaongeza discrimination

### transition×state_age — EV (pips) per cell

| trans \ age | 1-3 | 4-8 | 9-15 | 16+ |
|----|----|----|----|----|
| Tlo | — | -1.1 | -1.1 | -1.4 |
| Tmid | -2.0 | -1.0 | -1.1 | -1.5 |
| Thi | -0.8 | -4.6 | +1.9 | +2.9 |

→ joint EV-spread = 7.4 vs marginal max (trans/age) = 0.5 → ✅ interaction inaongeza discrimination

### volatility×activity×transition — top/bottom EV cells

| rank | vol×act×trans | EV | n |
|------|---------------|----|---|
| top | NORMAL×NORMAL×Tlo | +1.4 | 1,000 |
| top | NORMAL×HIGH×Tlo | +0.2 | 606 |
| top | HIGH×HIGH×Thi | +0.0 | 6,950 |
| bottom | HIGH×NORMAL×Tmid | -2.0 | 3,843 |
| bottom | LOW×NORMAL×Tmid | -2.5 | 4,552 |

→ 3-way EV range = **3.8 pips** (best NORMAL×NORMAL×Tlo +1.4 vs worst -2.5)

## deep_pullback — Group A (Reward)

### volatility×activity — EV (pips) per cell

| vol \ act | LOW | NORMAL | HIGH |
|----|----|----|----|
| LOW | -1.3 | -0.1 | -1.4 |
| NORMAL | -1.1 | -0.9 | -0.8 |
| HIGH | -0.9 | -0.5 | -0.6 |

→ joint EV-spread = 1.4 vs marginal max (vol/act) = 0.6 → ✅ interaction inaongeza discrimination

### volatility×transition — EV (pips) per cell

| vol \ trans | Tlo | Tmid | Thi |
|----|----|----|----|
| LOW | -0.9 | -0.5 | -1.2 |
| NORMAL | -1.7 | -0.9 | -1.0 |
| HIGH | -0.5 | -0.9 | -1.8 |

→ joint EV-spread = 1.3 vs marginal max (vol/trans) = 0.4 → ✅ interaction inaongeza discrimination

### activity×state_age — EV (pips) per cell

| act \ age | 1-3 | 4-8 | 9-15 | 16+ |
|----|----|----|----|----|
| LOW | -1.5 | -1.1 | -1.6 | -0.9 |
| NORMAL | -0.7 | -0.6 | -0.4 | -0.5 |
| HIGH | -1.3 | -1.0 | -0.8 | -0.5 |

→ joint EV-spread = 1.2 vs marginal max (act/age) = 0.6 → ✅ interaction inaongeza discrimination

### transition×state_age — EV (pips) per cell

| trans \ age | 1-3 | 4-8 | 9-15 | 16+ |
|----|----|----|----|----|
| Tlo | — | -0.8 | -0.9 | -0.7 |
| Tmid | +0.4 | -1.0 | -0.9 | -0.4 |
| Thi | -1.2 | +2.6 | -3.8 | -4.7 |

→ joint EV-spread = 7.3 vs marginal max (trans/age) = 0.5 → ✅ interaction inaongeza discrimination

### volatility×activity×transition — top/bottom EV cells

| rank | vol×act×trans | EV | n |
|------|---------------|----|---|
| top | LOW×NORMAL×Tmid | +0.5 | 4,552 |
| top | HIGH×NORMAL×Tmid | +0.1 | 3,843 |
| top | LOW×NORMAL×Tlo | -0.0 | 23,169 |
| bottom | HIGH×LOW×Thi | -2.6 | 1,647 |
| bottom | NORMAL×NORMAL×Tlo | -2.7 | 1,000 |

→ 3-way EV range = **3.3 pips** (best LOW×NORMAL×Tmid +0.5 vs worst -2.7)

## trend_continuation — Group B (Loss)

### volatility×activity — EV (pips) per cell

| vol \ act | LOW | NORMAL | HIGH |
|----|----|----|----|
| LOW | -0.9 | -0.9 | -1.4 |
| NORMAL | -1.3 | -1.9 | -1.8 |
| HIGH | -0.7 | -1.3 | -1.3 |

→ joint EV-spread = 1.2 vs marginal max (vol/act) = 0.7 → ✅ interaction inaongeza discrimination

### volatility×transition — EV (pips) per cell

| vol \ trans | Tlo | Tmid | Thi |
|----|----|----|----|
| LOW | -0.7 | -1.6 | -0.9 |
| NORMAL | +0.2 | -1.6 | -1.8 |
| HIGH | -1.4 | -1.6 | -0.6 |

→ joint EV-spread = 2.0 vs marginal max (vol/trans) = 0.7 → ✅ interaction inaongeza discrimination

### activity×state_age — EV (pips) per cell

| act \ age | 1-3 | 4-8 | 9-15 | 16+ |
|----|----|----|----|----|
| LOW | -1.3 | -0.9 | -0.7 | -1.1 |
| NORMAL | -1.7 | -1.6 | -1.4 | -1.1 |
| HIGH | -0.9 | -1.8 | -2.2 | -1.4 |

→ joint EV-spread = 1.6 vs marginal max (act/age) = 0.5 → ✅ interaction inaongeza discrimination

### transition×state_age — EV (pips) per cell

| trans \ age | 1-3 | 4-8 | 9-15 | 16+ |
|----|----|----|----|----|
| Tlo | +10.1 | -0.6 | -1.0 | -1.1 |
| Tmid | -2.3 | -1.6 | -1.7 | -1.5 |
| Thi | -1.2 | -3.0 | -3.0 | -1.5 |

→ joint EV-spread = 13.1 vs marginal max (trans/age) = 0.5 → ✅ interaction inaongeza discrimination

### volatility×activity×transition — top/bottom EV cells

| rank | vol×act×trans | EV | n |
|------|---------------|----|---|
| top | NORMAL×NORMAL×Tlo | +1.6 | 2,182 |
| top | HIGH×HIGH×Thi | -0.2 | 26,271 |
| top | HIGH×LOW×Tmid | -0.4 | 4,915 |
| bottom | NORMAL×NORMAL×Thi | -2.4 | 34,480 |
| bottom | LOW×HIGH×Thi | -2.6 | 4,635 |

→ 3-way EV range = **4.2 pips** (best NORMAL×NORMAL×Tlo +1.6 vs worst -2.6)

## VERDICT — F-012: je interactions zinaongeza discrimination zaidi ya marginals?

- Interactions zinazoongeza discrimination: **16/16** (2-way × Tier-1).

→ ✅ **F-012 imethibitishwa**: edge iko kwenye INTERACTION, sio component moja. Interaction Engine ijengwe kabla ya Payoff Engine. Transition (marginal ndogo) inaweza kuwa **GATEKEEPER** (inaruhusu vol×act) — Driver ≠ Gatekeeper.

*Joint EV-spread > marginal = interaction matters (F-012). 3-way range inaonyesha kama vol×act×transition pamoja zinazalisha cells zenye EV tofauti sana. Hii ndiyo 'market mechanism modeling' (sio feature importance). Payoff Engine (Phase 6) ijengwe juu ya interaction structure HII. NO ML bado. Profitable ≠ Tradable Edge.*