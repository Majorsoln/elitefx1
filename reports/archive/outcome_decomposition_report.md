# Outcome Decomposition — chanzo cha uplift ya EV (Phase 5.5, Tier 1)

*2026-06-24 21:47 | EV = P(win)×AvgWin − P(loss)×AvgLoss kwa context decile | outcome = forward HORIZON net ya spread (ileile ya F-009) | context score = Phase 3.5*

> **Q-008 (Chief):** Phase 5 ilionyesha P(TP) flat kuvuka deciles, lakini Phase 4 EV uplift kubwa. Je context inaongeza **P(win)**, **AvgWin**, au **asymmetry**? Hii inafungua EV. Hypothesis (Scenario A): context = reward SIZE, sio win probability. NO ML (Chief).


## mean_reversion

| decile | P(win) | EV | AvgWin | MedWin | p95Win | AvgLoss | MedLoss | p95Loss | n |
|--------|--------|----|--------|--------|--------|---------|---------|---------|---|
| D1 | 49% | -1.58 | 35.9 | 22.8 | 110 | 37.2 | 24.6 | 111 | 33,848 |
| D2 | 48% | -1.27 | 26.9 | 17.5 | 82 | 27.8 | 18.5 | 84 | 33,848 |
| D3 | 49% | -0.74 | 22.2 | 14.2 | 68 | 23.1 | 15.2 | 71 | 33,848 |
| D4 | 49% | -0.76 | 20.8 | 13.4 | 65 | 21.5 | 14.4 | 65 | 33,848 |
| D5 | 49% | -0.65 | 21.6 | 14.2 | 66 | 22.4 | 14.9 | 69 | 33,849 |
| D6 | 50% | -0.50 | 21.7 | 14.4 | 65 | 22.6 | 15.3 | 69 | 33,848 |
| D7 | 49% | -0.38 | 21.0 | 14.0 | 63 | 21.3 | 14.1 | 64 | 33,848 |
| D8 | 50% | -0.06 | 23.0 | 15.4 | 71 | 23.2 | 15.7 | 69 | 33,848 |
| D9 | 50% | +0.33 | 26.6 | 17.8 | 80 | 26.2 | 17.5 | 78 | 33,848 |
| D10 | 52% | +2.29 | 39.5 | 25.1 | 124 | 37.8 | 24.3 | 115 | 33,849 |

→ **mean_reversion** D10−D1: ΔP(win)=+3pp · ΔAvgWin=+3.6 · ΔAvgLoss=+0.6 · ΔEV=+3.86 → driver: **AvgWin (reward size)**

## pullback

| decile | P(win) | EV | AvgWin | MedWin | p95Win | AvgLoss | MedLoss | p95Loss | n |
|--------|--------|----|--------|--------|--------|---------|---------|---------|---|
| D1 | 47% | -3.16 | 35.2 | 23.2 | 105 | 37.5 | 24.5 | 115 | 32,869 |
| D2 | 47% | -1.96 | 26.8 | 18.2 | 81 | 27.8 | 19.0 | 83 | 32,869 |
| D3 | 47% | -1.41 | 23.0 | 15.1 | 71 | 23.2 | 15.5 | 71 | 32,869 |
| D4 | 47% | -1.24 | 21.8 | 14.1 | 69 | 22.0 | 15.0 | 67 | 32,870 |
| D5 | 48% | -1.10 | 19.6 | 12.4 | 62 | 20.2 | 13.0 | 63 | 32,869 |
| D6 | 47% | -1.31 | 20.5 | 13.0 | 65 | 20.8 | 13.5 | 66 | 32,869 |
| D7 | 48% | -1.06 | 20.0 | 12.7 | 64 | 20.6 | 13.2 | 65 | 32,870 |
| D8 | 48% | -1.14 | 21.4 | 14.1 | 66 | 21.9 | 14.6 | 67 | 32,869 |
| D9 | 48% | -0.34 | 24.7 | 16.1 | 77 | 24.0 | 15.8 | 74 | 32,869 |
| D10 | 51% | +1.29 | 37.0 | 23.1 | 118 | 35.1 | 22.3 | 110 | 32,870 |

→ **pullback** D10−D1: ΔP(win)=+3pp · ΔAvgWin=+1.7 · ΔAvgLoss=-2.4 · ΔEV=+4.45 → driver: **AvgLoss (loss control)**

## deep_pullback

| decile | P(win) | EV | AvgWin | MedWin | p95Win | AvgLoss | MedLoss | p95Loss | n |
|--------|--------|----|--------|--------|--------|---------|---------|---------|---|
| D1 | 47% | -3.16 | 34.8 | 22.0 | 108 | 36.9 | 23.1 | 117 | 32,869 |
| D2 | 47% | -1.65 | 22.3 | 14.6 | 70 | 23.0 | 15.2 | 70 | 32,869 |
| D3 | 47% | -1.15 | 21.4 | 13.8 | 68 | 21.4 | 14.3 | 66 | 32,869 |
| D4 | 47% | -1.03 | 19.3 | 12.2 | 61 | 19.1 | 12.3 | 60 | 32,870 |
| D5 | 47% | -1.00 | 20.0 | 12.7 | 62 | 19.8 | 12.7 | 62 | 32,869 |
| D6 | 47% | -0.96 | 21.6 | 13.9 | 68 | 21.3 | 14.1 | 65 | 32,869 |
| D7 | 48% | -0.71 | 23.0 | 15.3 | 71 | 22.6 | 15.1 | 70 | 32,870 |
| D8 | 49% | -0.63 | 23.9 | 16.0 | 74 | 24.0 | 16.0 | 73 | 32,869 |
| D9 | 50% | +0.19 | 27.9 | 18.6 | 84 | 27.3 | 18.5 | 82 | 32,869 |
| D10 | 50% | +1.30 | 37.9 | 24.5 | 116 | 35.9 | 23.8 | 107 | 32,870 |

→ **deep_pullback** D10−D1: ΔP(win)=+3pp · ΔAvgWin=+3.1 · ΔAvgLoss=-1.0 · ΔEV=+4.46 → driver: **AvgWin (reward size)**

## trend_continuation

| decile | P(win) | EV | AvgWin | MedWin | p95Win | AvgLoss | MedLoss | p95Loss | n |
|--------|--------|----|--------|--------|--------|---------|---------|---------|---|
| D1 | 47% | -3.47 | 38.4 | 24.1 | 121 | 40.3 | 25.5 | 126 | 74,049 |
| D2 | 47% | -2.08 | 26.0 | 17.0 | 79 | 27.0 | 17.9 | 82 | 74,049 |
| D3 | 46% | -1.63 | 21.5 | 13.7 | 67 | 21.7 | 14.1 | 67 | 74,049 |
| D4 | 47% | -1.45 | 20.6 | 13.6 | 63 | 20.6 | 13.8 | 62 | 74,049 |
| D5 | 46% | -1.51 | 21.2 | 13.9 | 67 | 21.0 | 14.1 | 63 | 74,050 |
| D6 | 47% | -1.28 | 20.5 | 13.5 | 63 | 20.4 | 13.6 | 62 | 74,049 |
| D7 | 47% | -1.04 | 21.9 | 14.3 | 67 | 21.5 | 14.3 | 65 | 74,049 |
| D8 | 48% | -0.58 | 24.6 | 16.1 | 76 | 23.6 | 15.6 | 71 | 74,049 |
| D9 | 49% | -0.50 | 27.9 | 18.5 | 84 | 27.3 | 17.8 | 82 | 74,049 |
| D10 | 50% | +0.81 | 39.3 | 25.1 | 120 | 37.5 | 23.8 | 117 | 74,050 |

→ **trend_continuation** D10−D1: ΔP(win)=+3pp · ΔAvgWin=+0.9 · ΔAvgLoss=-2.8 · ΔEV=+4.28 → driver: **AvgLoss (loss control)**

## VERDICT — Context inafanya kazi kupitia mechanism gani?

- **mean_reversion**: ΔEV +3.86 ← AvgWin (reward size) (ΔP(win) +3pp, ΔAvgWin +3.6, ΔAvgLoss +0.6)
- **pullback**: ΔEV +4.45 ← AvgLoss (loss control) (ΔP(win) +3pp, ΔAvgWin +1.7, ΔAvgLoss -2.4)
- **deep_pullback**: ΔEV +4.46 ← AvgWin (reward size) (ΔP(win) +3pp, ΔAvgWin +3.1, ΔAvgLoss -1.0)
- **trend_continuation**: ΔEV +4.28 ← AvgLoss (loss control) (ΔP(win) +3pp, ΔAvgWin +0.9, ΔAvgLoss -2.8)

→ **Scenario A imeungwa mkono**: kwa 4/4 Tier-1 events, uplift ya EV inatokana na PAYOFF SIZE/asymmetry, SIO win probability. Context = reward engine, sio hit-rate engine. (Inalingana na Phase 1.9: win-rate flat, EV juu.)

*EV decomposed = P(win)×AvgWin − P(loss)×AvgLoss kwa decile (outcome = forward net, ileile ya F-009). Hii inafichua MECHANISM: P(win) vs AvgWin vs AvgLoss. Hakuna F-010 bado (Chief). Mpaka mechanism ijulikane, hatuendi Outcome Engine wala ML. Profitable ≠ Tradable Edge.*