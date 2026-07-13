# Evidence Snapshots — picha ya ushahidi kwa wakati fulani (Decision Science D3)

*2026-07-01 18:24 | 9 pairs, 5 sets | Snapshot = canonical Decision-Layer input (P79) | temporal + structural conflict | NO Decision Engine | NO ML*

> **P76** maana order-independent, lineage kando. **P77** maamuzi juu ya **Snapshots**, sio objects ghafi. **P78 (OPEN)** redundancy vs duplication. **P79** **Snapshot = canonical input** kwa Decision Layer. Architecture: Object→Operations→Set→**Snapshot** ══ Decision→Execution.

## Q1+Q2 — Snapshot ni nini + fields

**Q1:** Snapshot = **immutable point-in-time view** ya Evidence Set as-of muda T: inaresolve freshness/expiry ya kila member kwa T, inabaki na live tu, inakokotoa reliability/readiness, na inarekodi temporal + structural conflict + provenance root. Ni 'picha' ambayo Decision Layer inaiona (P77/P79).

| field | maana |
|-------|-------|
| as_of | muda T wa snapshot |
| n_total / n_live | members wote / wasio-expired as-of T |
| reliability | set reliability = aggregate confidence (P70 OPEN: SIO 'confidence' rasmi) |
| value / uncertainty | aggregate effect + SE (live) |
| readiness | set-ready **na** temporal-conflict < ceiling (snapshot-level, P73) |
| temporal_conflict | older-vs-newer sign contradiction (P74) |
| structural_conflict | taxonomy ya D1 (intra/cross-pair/cross-tf/cross-engine) |
| provenance | nodes/edges za graph (P72) |

## Q3 — Snapshot readiness inakokotolewaje?

- `readiness = decision_ready(aggregate ya live members @T)` **NA** `temporal_conflict < 0.35`. Yaani: support/reliability/non-expired/low-structural-conflict (P26 default abstain) **pamoja na** kutokuwa na contradiction ya kimuda (P74).

| set | as_of=0 | as_of=+stale | as_of=+TTL |
|-----|---------|--------------|------------|
| breakout | True (ready) | True | False (live 0) |
| deep_pullback | True (ready) | True | False (live 0) |
| mean_reversion | True (ready) | True | False (live 0) |
| pullback | True (ready) | True | False (live 0) |
| trend_continuation | True (ready) | True | False (live 0) |

## Q4 — Temporal conflict (P74) kwenye snapshot

| set | temporal_conflict | older mean | newer mean | tafsiri |
|-----|-------------------|-----------|-----------|---------|
| breakout | 0.00 | -2.058 | -1.593 | thabiti kimuda |
| deep_pullback | 0.00 | -0.813 | -0.989 | thabiti kimuda |
| mean_reversion | 0.00 | -0.285 | -0.475 | thabiti kimuda |
| pullback | 0.00 | -1.243 | -1.384 | thabiti kimuda |
| trend_continuation | 0.00 | — | — | thabiti kimuda |

- temporal conflict (older vs newer) ni **tofauti** na structural (cross-pair/engine). Snapshot inaitenga wazi — Decision Engine itahitaji kujua aina ya conflict kabla ya policy.

## Q5 — Decision Engine itapokea Object, Set, au Snapshot?

→ **SNAPSHOT** (P79). Mfano `decision_input(breakout)`: as_of=0, n_live=36, reliability=1.00, value=-1.698, readiness=True, temporal_conflict=0.00.
- Object = immutable claim; Set = collection; **Snapshot = picha as-of T** ambayo ndiyo pekee inayobeba readiness + conflict resolved → ndiyo canonical Decision-Layer input.

## VERDICT — D3 Evidence Snapshots

→ ✅ **Evidence Snapshot imefafanuliwa** kama immutable point-in-time view ya Evidence Set (Q1/Q2), readiness imekokotolewa as-of T pamoja na temporal-conflict gate (Q3), temporal conflict imetenganishwa na structural (Q4, P74), na **Snapshot = canonical Decision-Layer input** (Q5, P79). **Evidence Layer sasa KAMILI**: Object→Operations→Set→Snapshot. Decision Engine itakuwa consumer mdogo wa snapshot. **Hakuna Decision Engine bado.** NO ML.

**Bado Decision Science D3 — hakuna decision-action wala alpha.** Snapshot ni picha ya ushahidi, sio uamuzi wala edge.

## Honest Caveats

1. **Snapshot inatumia age-shift sare** (huongeza bars sawa kwa wote) — kiuhalisia kila member ina as-of timestamp yake; snapshot ya production inahitaji per-member event-time, sio shift moja.
2. **Temporal conflict = median-age split rahisi** — ni proxy ya P74, sio model kamili ya regime-change; inaweza kukosa contradictions za polepole au kuripoti za bahati kwa n ndogo.
3. **Reliability bado = Φ(EV/SE)** (P70 OPEN) — inajaa kwa support kubwa; 'reliability' ni jina la muda hadi confidence-model rasmi ifungwe.
4. **Redundancy (P78 OPEN) haijashughulikiwa** — snapshot ina dedupe ya identity tu; members correlated (EURUSD H1 vs H4) bado huhesabiwa mara mbili → reliability optimistic.
5. **Snapshot ≠ edge (P69).** Evidence Layer kamili ni infrastructure inayoauditika; haithibitishi alpha. Decision-ready snapshot bado si trade-ready.

*Evidence Snapshot = immutable as-of-T view ya Evidence Set; readiness @T + temporal-conflict gate; temporal vs structural conflict; canonical Decision-Layer input (P79). Principle 76–79. NO Decision Engine. NO ML. Profitable ≠ Tradable Edge.*