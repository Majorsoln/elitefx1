# Context Generalization Test — je Context inageneralize? (Phase 1.95)

*2026-06-23 23:02 | events: pullback, breakout, mean_reversion | Case A (Event alone) vs B (Event + Context) | ONLINE prequential (no-lookahead) | metrics: Win · EV · Trade Count*

> **Q-001 (Chief):** Je Context inaboresha zaidi ya Event Family moja? Tunaondoa hatari ya thamani kuwa ya Trend Pullback PEKEE. Context ikifaidisha events ≥2 → inageneralize → Principle 12 (Context = filter) imeimarishwa.

## Per event × dimension — aggregate kwa pairs×TFs zote

| Event | Dim | cells | median ΔEV (pips) | median ΔWin | trades A→B | cov | +EV cells | value? |
|-------|-----|-------|-------------------|-------------|-----------|-----|-----------|--------|
| pullback | vol | 36 | +1.26 | +1pp | 351,083→74,427 | 21% | 33/36 | ✅ |
| pullback | act | 36 | +0.59 | +0pp | 351,083→58,726 | 17% | 25/36 | ✅ |
| pullback | spr | 36 | +0.67 | +1pp | 351,083→61,780 | 18% | 27/36 | ✅ |
| breakout | vol | 36 | +0.83 | +0pp | 166,356→37,356 | 22% | 21/36 | ✅ |
| breakout | act | 36 | +0.04 | +1pp | 166,356→30,268 | 18% | 19/36 | ✅ |
| breakout | spr | 36 | +0.18 | -0pp | 166,356→27,562 | 17% | 19/36 | ✅ |
| mean_reversion | vol | 36 | +0.54 | +1pp | 360,985→145,664 | 40% | 28/36 | ✅ |
| mean_reversion | act | 36 | +0.18 | +0pp | 360,985→143,251 | 40% | 23/36 | ✅ |
| mean_reversion | spr | 36 | +0.35 | +0pp | 360,985→140,028 | 39% | 26/36 | ✅ |

## VERDICT — Q-001: je Context inageneralize kuvuka event families?

- **pullback**: ✅ Context adds value
- **breakout**: ✅ Context adds value
- **mean_reversion**: ✅ Context adds value

✅ **Context value GENERALIZES** — inafaidisha zaidi ya Trend Pullback (3/3 events). Q-001 = NDIYO. Principle 12 imeimarishwa.

*Doctrine (V5.2, Principle 12): Context = FILTER, sio alpha source. Phase 1.95 inathibitisha kama filter hii inafanya kazi kuvuka event families (sio over-fit kwa event moja). NDIYO → Phase 2 (Adaptive Volume Bars) inaendelea kwa msingi imara. Metric = EV (net pips). NO ML (Chief). Events/HORIZON ni vigezo; doctrine inahitaji THUBUTISHO.*