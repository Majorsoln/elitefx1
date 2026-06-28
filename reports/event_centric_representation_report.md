# Event-Centric Representation — kila Event ina context yake (Phase 17)

*2026-06-28 20:39 | within-event incremental R² (perm-controlled, 25 reps) | significance-first (Principle 37) | instances=2,003,541*

> **F-035 (Chief):** state variables zinapata maana kupitia mwingiliano na EVENTS, sio kati yao. **Principle 36:** Events ndio SEMANTIC ANCHORS; context inapata thamani tu ikiwa imefungwa kwa Event. **Principle 37:** low S/N -> significance + OOS, sio effect size. Tunajenga representation EVENT-SPECIFIC (sio moja kwa events zote). NO ML.


## Q1 — Je Event ndiyo semantic anchor?

- R²(Event) = **0.00012**  vs  context standalone: vol=0.00000 · activity=0.00000 · traj=0.00000 · spread=0.00002
- context ikiunganishwa na Event (incremental juu ya Event): vol=+0.000048(p=0.038) · activity=+0.000032(p=0.038) · traj=+0.000024(p=0.038)

→ ✅ Event NI semantic anchor: Event peke yake inaeleza zaidi ya context yoyote peke yake, na context inapata taarifa ikiunganishwa na Event.

## Q2 — Kwa kila Event: context zipi zinaongeza taarifa? (within-event, ✅ = significant)

| event | pair | vol | spread | session | activity | age | traj | trans | persist |
|-------|---|---|---|---|---|---|---|---|---|
| pullback | — | ✅ | ✅ | ✅ | ✅ | — | ✅ | ✅ | — |
| deep_pullback | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — | — |
| trend_continuation | ✅ | ✅ | ✅ | ✅ | ✅ | — | — | — | — |
| breakout | ✅ | ✅ | ✅ | ✅ | — | — | ✅ | — | — |
| mean_reversion | ✅ | ✅ | ✅ | ✅ | ✅ | — | ✅ | — | — |

## Q3 — Context variables zenye thamani kwa Event moja lakini si nyingine

- **age**: ina taarifa kwa [deep_pullback] tu (sio events zote) -> event-specific
- **trans**: ina taarifa kwa [pullback] tu (sio events zote) -> event-specific
- **pair**: ina taarifa kwa [deep_pullback, trend_continuation, breakout, mean_reversion] tu (sio events zote) -> event-specific
- **activity**: ina taarifa kwa [pullback, deep_pullback, trend_continuation, mean_reversion] tu (sio events zote) -> event-specific
- **traj**: ina taarifa kwa [pullback, deep_pullback, breakout, mean_reversion] tu (sio events zote) -> event-specific

→ event-specific context = uthibitisho kuwa representation moja kwa events zote ni kosa.

## Q4 — Minimal event-specific representation (greedy within-event)

| event | minimal representation | size |
|-------|------------------------|------|
| pullback | spread + traj | 2 |
| deep_pullback | pair + spread + vol | 3 |
| trend_continuation | pair + spread + vol | 3 |
| breakout | session + spread + pair + vol | 4 |
| mean_reversion | spread + activity + pair | 3 |

## Q5 — Je Mean Reversion na Breakout zina representation tofauti?

- Mean Reversion: {activity, pair, spread}
- Breakout: {pair, session, spread, vol}
- shared: {pair, spread} · MR-only: {activity} · BK-only: {session, vol}

→ ✅ representation ZINATOFAUTIANA: kulazimisha representation moja kwa Breakout na Mean Reversion ni kosa (event-specific ni sahihi).

## Metric ya ziada — calibration (Brier) ya minimal event-rep vs Event-pekee

| event | Brier(event-only) | Brier(event-minimal) | bora? |
|-------|-------------------|----------------------|-------|
| pullback | 0.24955 | 0.24953 | ✅ |
| deep_pullback | 0.24970 | 0.24961 | ✅ |
| trend_continuation | 0.24931 | 0.24906 | ✅ |
| breakout | 0.24930 | 0.24955 | — |
| mean_reversion | 0.24999 | 0.24998 | ✅ |

## VERDICT — Phase 17 Event-Centric Representation

→ ✅ **Event ndiyo semantic anchor** (F-035/Principle 36): kila Event ina context yake; context **5** ni event-specific; Mean Reversion vs Breakout representation zinatofautiana. Hii inathibitisha kuwa representation MOJA kwa events zote ndiyo ilikuwa logic gap. Inayofuata: jenga event-specific representations kisha rudia Confirmation (OOS+FDR, Principle 37) — SIO ML bado.

*Event-Centric: within-event incremental R² (perm-controlled), event-specific minimal representation, MR vs Breakout. F-035: context inapata maana kupitia Event. Principle 36: Events = anchors. Principle 37: significance + OOS, sio effect size. NO ML. Profitable ≠ Tradable Edge.*