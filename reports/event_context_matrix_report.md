# Event × Context Matrix — ni event gani inanufaika zaidi na context? (Phase 4)

*2026-06-24 20:06 | Event Only vs Event + Top context deciles (score = online prequential EV ya (vol_state, age-bucket), F-008) | EV net ya spread | bars=1,020,735*

> **Phase 4 (Chief):** F-008 = Context ni RANKING ENGINE. Hapa tunapima uplift ya kuchukua context-decile bora kwa kila event. Improvement = Top10 EV − All EV. Swali: ni event gani inanufaika ZAIDI na context? (msingi kabla ya Triple Barrier). NO ML, NO triple barrier.

## Matrix — EV (pips) kwa context-rank

| Event | n | freq/1k | All EV | Win% | Top10 | Top20 | Top30 | Top50 | Improvement (T10−All) |
|-------|---|---------|--------|------|-------|-------|-------|-------|-----------------------|
| pullback | 341,571 | 335 | -1.17 | 48% | +1.29 | +0.48 | -0.06 | -0.51 | +2.47 |
| deep_pullback | 341,571 | 335 | -0.85 | 48% | +1.29 | +0.75 | +0.29 | -0.16 | +2.14 |
| breakout | 161,885 | 159 | -1.86 | 47% | -0.32 | -0.61 | -0.72 | -0.93 | +1.54 |
| volatility_breakout | 140,302 | 137 | -1.24 | 48% | -0.01 | -0.35 | -0.40 | -0.52 | +1.23 |
| trend_continuation | 753,429 | 738 | -1.30 | 47% | +0.81 | +0.16 | -0.09 | -0.52 | +2.11 |
| volatility_expansion | 152,803 | 150 | -1.05 | 48% | -1.21 | -1.12 | -0.87 | -0.89 | -0.15 |
| news_shock | 28,410 | 28 | -0.95 | 49% | +0.00 | -0.00 | -0.56 | -0.14 | +0.95 |
| mean_reversion | 351,318 | 344 | -0.20 | 50% | +2.29 | +1.31 | +0.85 | +0.33 | +2.49 |
| pattern_completion | 99,059 | 97 | -1.26 | 48% | -2.06 | -1.65 | -1.76 | -1.44 | -0.81 |

## Win% — All vs Top10 (kwa context)

| Event | Win% All | Win% Top10 | ΔWin |
|-------|----------|------------|------|
| pullback | 48% | 51% | +3pp |
| deep_pullback | 48% | 50% | +2pp |
| breakout | 47% | 50% | +3pp |
| volatility_breakout | 48% | 50% | +2pp |
| trend_continuation | 47% | 50% | +3pp |
| volatility_expansion | 48% | 49% | +1pp |
| news_shock | 49% | 49% | +1pp |
| mean_reversion | 50% | 52% | +2pp |
| pattern_completion | 48% | 48% | +0pp |

## VERDICT — events zilizopangwa kwa CONTEXT BENEFIT (Top10 − All)

- **mean_reversion**: improvement +2.49 pips (All -0.20 → Top10 +2.29) — ✅ profitable @Top10
- **pullback**: improvement +2.47 pips (All -1.17 → Top10 +1.29) — ✅ profitable @Top10
- **deep_pullback**: improvement +2.14 pips (All -0.85 → Top10 +1.29) — ✅ profitable @Top10
- **trend_continuation**: improvement +2.11 pips (All -1.30 → Top10 +0.81) — ✅ profitable @Top10
- **breakout**: improvement +1.54 pips (All -1.86 → Top10 -0.32) — ↑ improved (bado <0)
- **volatility_breakout**: improvement +1.23 pips (All -1.24 → Top10 -0.01) — ↑ improved (bado <0)
- **news_shock**: improvement +0.95 pips (All -0.95 → Top10 +0.00) — ✅ profitable @Top10
- **volatility_expansion**: improvement -0.15 pips (All -1.05 → Top10 -1.21) — ↑ improved (bado <0)
- **pattern_completion**: improvement -0.81 pips (All -1.26 → Top10 -2.06) — ↑ improved (bado <0)

→ Event inayonufaika ZAIDI na context: **mean_reversion** (+2.49 pips uplift). Events 5/9 zinakuwa profitable (@Top10 EV>0) kwa context-ranking.

*Matrix inajibu event-specificity ya context (F-008). All EV = event peke yake (bila context); Top X% = decile bora kwa context score (no-lookahead, Phase 3.5). Improvement>0 = context-ranking inanufaisha event hiyo. Hili ni la msingi kabla ya Triple Barrier (Phase 5, BLOCKED). NO ML/outcome models (Chief). Metric = EV (net pips).*