# Event × State Interaction — edge iko kwenye mwingiliano? (Phase 6, Interaction Engine)

*2026-06-26 22:02 | events × latent state (k=4) | EV±95%CI (net pips), Win, Triple Barrier (±1.0σ, 10b) | outcome forward 6b net | min N=150*

> **F-020 (Chief, Experimental):** trading edge inaweza kutoka **Event × Configuration**, sio Event peke yake. 'Pullback works ONLY inside State X.' Acceptance rule: hakuna Event inaingia Opportunity Engine bila Event × Configuration → Expected Payoff. Principle 21: Selection > Prediction. NO ML.


## pullback — Event alone EV = -1.17 pips (N=338,682)

| state | N | EV [95% CI] | Win% | TP/SL/TIME |
|-------|---|-------------|------|------------|
| C0 | 225,025 | -1.07 [-1.2,-0.9] | 48% | 47/50/3 |
| C1 | 68,233 | -1.29 [-1.7,-0.9] | 49% | 46/47/8 |
| C2 | 3,890 | -7.48 [-8.6,-6.4] | 35% | 45/49/6 |
| C3 | 41,534 | -0.94 [-1.5,-0.4] | 49% | 47/48/5 |

→ **pullback**: best **C3** EV -0.94 vs worst **C2** -7.48 (spread 6.5 pips). — mwingiliano dhaifu

## deep_pullback — Event alone EV = -0.84 pips (N=338,682)

| state | N | EV [95% CI] | Win% | TP/SL/TIME |
|-------|---|-------------|------|------------|
| C0 | 225,025 | -0.64 [-0.8,-0.5] | 48% | 48/49/3 |
| C1 | 68,233 | -1.13 [-1.5,-0.8] | 47% | 46/47/8 |
| C2 | 3,890 | -6.54 [-7.6,-5.4] | 34% | 48/45/6 |
| C3 | 41,534 | -0.96 [-1.5,-0.4] | 49% | 47/49/5 |

→ **deep_pullback**: best **C0** EV -0.64 vs worst **C2** -6.54 (spread 5.9 pips). ✅ edge kwenye Event×State (C0 significant > event-alone)

## trend_continuation — Event alone EV = -1.27 pips (N=746,712)

| state | N | EV [95% CI] | Win% | TP/SL/TIME |
|-------|---|-------------|------|------------|
| C0 | 480,111 | -0.95 [-1.1,-0.9] | 48% | 47/49/3 |
| C1 | 132,422 | -1.67 [-1.9,-1.4] | 47% | 45/47/8 |
| C2 | 6,202 | -8.64 [-9.6,-7.7] | 31% | 42/52/5 |
| C3 | 127,977 | -1.69 [-2.0,-1.4] | 48% | 47/49/5 |

→ **trend_continuation**: best **C0** EV -0.95 vs worst **C2** -8.64 (spread 7.7 pips). ✅ edge kwenye Event×State (C0 significant > event-alone)

## breakout — Event alone EV = -1.80 pips (N=160,429)

| state | N | EV [95% CI] | Win% | TP/SL/TIME |
|-------|---|-------------|------|------------|
| C0 | 97,282 | -1.28 [-1.5,-1.0] | 47% | 47/51/3 |
| C1 | 14,932 | -4.55 [-5.4,-3.7] | 44% | 41/51/8 |
| C2 | 341 | -19.52 [-24.9,-14.1] | 18% | 25/73/3 |
| C3 | 47,874 | -1.87 [-2.4,-1.4] | 48% | 47/49/4 |

→ **breakout**: best **C0** EV -1.28 vs worst **C2** -19.52 (spread 18.2 pips). ✅ edge kwenye Event×State (C0 significant > event-alone)

## mean_reversion — Event alone EV = -0.25 pips (N=348,096)

| state | N | EV [95% CI] | Win% | TP/SL/TIME |
|-------|---|-------------|------|------------|
| C0 | 224,049 | -0.41 [-0.6,-0.3] | 50% | 48/48/3 |
| C1 | 46,532 | +0.44 [-0.0,+0.9] | 51% | 48/44/7 |
| C2 | 1,606 | -1.72 [-3.6,+0.1] | 44% | 60/35/5 |
| C3 | 75,909 | -0.17 [-0.6,+0.2] | 50% | 47/49/4 |

→ **mean_reversion**: best **C1** EV +0.44 vs worst **C2** -1.72 (spread 2.2 pips). ✅ edge kwenye Event×State (C1 significant > event-alone)

## VERDICT — F-020: edge iko kwenye Event × Configuration?

- events zenye edge ya Event×State (best-cluster EV CI ya chini > event-alone, spread >2 pips): **4/5**

→ ✅ **F-020 inaungwa mkono**: kwa events kadhaa, EV inategemea LATENT STATE (Event × Configuration). Hii ndiyo msingi wa Opportunity Engine: rank Event×State combos kwa Expected Payoff. (Experimental — confirm kwa walk-forward.)

*Event × latent state EV±CI = je tukio linafanya kazi ndani ya configuration fulani tu. Edge = best-cluster EV (CI ya chini) inazidi event-alone EV. Principle 21: Selection > Prediction. F-019: information ina value tu ikiboresha payoff/decision. Acceptance rule: Event × Configuration → Expected Payoff kabla ya Opportunity Engine. NO ML bado (target haijajengwa). Profitable ≠ Tradable Edge.*