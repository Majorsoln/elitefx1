# Event Diagnostics — events 9 ndani ya context (Phase 3)

*2026-06-24 15:52 | events: Event Library (KJ) | aggregate kuvuka pairs × TFs | context (vol age/pchange) online no-lookahead | transition horizon 12 bars | bars=1,020,735*

> **Phase 3 (Chief):** tunaelewa events zinavyotokea NDANI ya context (sio alpha/entries). Diagnostics: frequency · context coverage · state/age/transition distribution. NO Triple Barrier, NO ML, NO outcomes — Event Layer ramani tu.

## 1) Frequency + Context coverage

| Event | n | per 1000 bars | ctx coverage | favorable (pchg<0.5) |
|-------|---|---------------|--------------|----------------------|
| pullback | 341,629 | 334.7 | 99% | 100% |
| deep_pullback | 341,629 | 334.7 | 99% | 100% |
| breakout | 161,937 | 158.6 | 99% | 100% |
| volatility_breakout | 140,338 | 137.5 | 99% | 100% |
| trend_continuation | 753,611 | 738.3 | 99% | 100% |
| volatility_expansion | 152,831 | 149.7 | 99% | 100% |
| news_shock | 28,422 | 27.8 | 99% | 100% |
| mean_reversion | 351,416 | 344.3 | 99% | 100% |
| pattern_completion | 99,080 | 97.1 | 99% | 100% |

## 2) State distribution — volatility | activity (% ya events)

| Event | vol L/N/H | act L/N/H |
|-------|-----------|-----------|
| pullback | 33/33/34 | 36/33/31 |
| deep_pullback | 33/33/34 | 36/33/31 |
| breakout | 30/33/37 | 23/33/44 |
| volatility_breakout | 32/34/34 | 20/33/47 |
| trend_continuation | 32/33/34 | 32/33/35 |
| volatility_expansion | 30/34/36 | 17/33/51 |
| news_shock | 25/33/42 | 11/26/63 |
| mean_reversion | 32/33/34 | 28/33/38 |
| pattern_completion | 31/34/35 | 29/34/37 |

## 3) Age distribution — vol state-age bucket (% ya events)

| Event | 1-3 | 4-8 | 9-15 | 16+ |
|-------|----|----|----|----|
| pullback | 20 | 20 | 17 | 42 |
| deep_pullback | 20 | 20 | 17 | 42 |
| breakout | 26 | 18 | 15 | 41 |
| volatility_breakout | 26 | 17 | 16 | 42 |
| trend_continuation | 22 | 20 | 16 | 42 |
| volatility_expansion | 29 | 15 | 15 | 41 |
| news_shock | 44 | 10 | 10 | 36 |
| mean_reversion | 23 | 19 | 16 | 42 |
| pattern_completion | 23 | 19 | 17 | 42 |

## 4) Transition distribution — vol move inayofuata (% ya events)

| Event | escalate | revert | stay |
|-------|----------|--------|------|
| pullback | 25% | 28% | 47% |
| deep_pullback | 25% | 28% | 47% |
| breakout | 25% | 27% | 48% |
| volatility_breakout | 27% | 26% | 47% |
| trend_continuation | 25% | 27% | 48% |
| volatility_expansion | 27% | 26% | 47% |
| news_shock | 25% | 24% | 51% |
| mean_reversion | 25% | 27% | 48% |
| pattern_completion | 25% | 28% | 47% |

---
*Phase 3 = ramani ya Event × Context (sio strategy). Inajenga juu ya states/age/transitions/context zilizothibitishwa (F-001..F-007). Inayofuata (baada ya Chief review): Event × Context Matrix (Phase 4). Bado HAIRUHUSIWI: Triple Barrier, ML, Outcome models. Metric = EV (phases zijazo). 'favorable' = vol pchange<0.5 (state stable), proxy ya neutral.*