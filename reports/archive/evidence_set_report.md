# Evidence Sets — Decision hutokea juu ya COLLECTION, sio object moja (Decision Science D2)

*2026-06-30 22:31 | 9 pairs, 180 evidence objects, 5 sets (per event) | value-object identity + snapshot readiness | NO Decision Engine | NO ML*

> **P71** transformations pure. **P72** provenance = graph. **P73** readiness = snapshot, sio object. **P74 (OPEN)** temporal vs structural conflict. **P75** Evidence = value objects wenye immutable identity. Architecture: Evidence Objects → **Evidence Sets** → Decision → Execution.

## Q1+Q3 — Evidence Collection (keyed by value-object identity) + duplicates

| set (event) | n in | n unique | duplicates removed |
|-------------|------|----------|--------------------|
| breakout | 36 | 36 | 0 |
| deep_pullback | 36 | 36 | 0 |
| mean_reversion | 36 | 36 | 0 |
| pullback | 36 | 36 | 0 |
| trend_continuation | 36 | 36 | 0 |

- **Q1:** Evidence Set = collection ya Evidence Objects keyed by **id** (P75 value-object identity). **Q3:** duplicate (id ile ile = content ile ile) huondolewa moja kwa moja.

## Q2 — Ordering ina maana?

- set-aggregate (inverse-variance) ni **order-INVARIANT**: value -1.6975 vs reversed -1.6975 → ✅ haina tofauti.
- **Hitimisho:** kwa AGGREGATION ordering haina maana (set semantics); kwa **provenance/audit** ordering ina maana (graph ina mwelekeo, P72). Set = unordered kwa thamani, ordered kwa lineage.

## Q4 — Evidence Set ina confidence yake?

| set | members(live) | set value | set uncertainty | set confidence | set conflict |
|-----|---------------|-----------|-----------------|----------------|--------------|
| breakout | 36 | -1.698 | 0.081 | 1.00 | 0.02 |
| deep_pullback | 36 | -0.855 | 0.050 | 1.00 | 0.12 |
| mean_reversion | 36 | -0.400 | 0.053 | 1.00 | 0.16 |
| pullback | 36 | -1.277 | 0.050 | 1.00 | 0.01 |
| trend_continuation | 36 | -1.327 | 0.035 | 1.00 | 0.05 |

- **Q4:** ndio — set ina confidence YAKE = aggregate ya members (P68 operation). Set-confidence ni property ya SET, inayotokana na members + conflict kati yao.

## Q5 — Evidence Set ina readiness yake? (SNAPSHOT — P73)

| set | now=0 (ready?) | now=+stale | now=+TTL (expired) |
|-----|----------------|------------|--------------------|
| breakout | True (decision-ready) | True | False (live 0) |
| deep_pullback | True (decision-ready) | True | False (live 0) |
| mean_reversion | True (decision-ready) | True | False (live 0) |
| pullback | True (decision-ready) | True | False (live 0) |
| trend_continuation | True (decision-ready) | True | False (live 0) |

- **Q5/P73:** readiness ni ya **SNAPSHOT** (as-of time), SIO ya Evidence Object immutable. Set ile ile ina readiness tofauti kwa nyakati tofauti — object haibadiliki, snapshot ndio hubadilika.

## P72 — Provenance graph (demo)

- set `breakout`: nodes 37, edges 36 (aggregate ina parents 36 → graph, sio list).

## Conflict taxonomy (D1 carry) + P74 note

| dimension | score |
|-----------|-------|
| intra (split-half) | 0.27 |
| cross-pair | 0.07 |
| cross-timeframe | 0.02 |
| cross-engine | 0.07 |

- **P74 (OPEN):** temporal contradiction (evidence ya jana bullish vs leo bearish) bado haijatenganishwa na structural disagreement — ni kazi ya baadaye (intra hapa ni split-half, sio temporal).

## VERDICT — D2 Evidence Sets

→ ✅ **Evidence Set imefafanuliwa**: collection keyed by value-object identity (Q1/Q3 dedup, P75); aggregate **order-invariant** (Q2); set ina **confidence yake** (Q4); set ina **readiness ya SNAPSHOT** (Q5, P73 — inabadilika kwa muda, object haibadiliki); provenance ni **graph** (P72). Evidence Layer (Object→Operations→Set) sasa kamili — Decision Engine itafanya kazi juu ya **sets**, sio objects. **Hakuna Decision Engine bado.** NO ML.

**Bado Decision Science D2 — hakuna decision-action wala alpha.** Evidence Layer ni infrastructure; Decision (juu ya sets) ni hatua inayofuata baada ya Chief kuidhinisha.

## Honest Caveats

1. **Set-confidence inarithi caveat za aggregate** — inverse-variance inadhani independence; members (pair×tf za event moja) zina correlation → set-uncertainty ni optimistic.
2. **Dedup by content-hash identity** — near-duplicates (value ~sawa lakini si sawa kabisa) HAZIondolewi; identity ni exact-content, sio fuzzy. Hii ni sahihi kwa value object lakini haishughulikii redundancy ya kistatistiki.
3. **Snapshot readiness inatumia age-shift rahisi** (huongeza bars kwa wote sawa) — kiuhalisia kila member ina recency yake; snapshot halisi inahitaji as-of timestamps per member.
4. **P74 temporal conflict HAIJATEKELEZWA** — 'intra' hapa ni split-half (structural), sio temporal contradiction (jana vs leo). Decision Engine itahitaji tofauti hii kabla ya kuamua.
5. **Set ≠ edge.** Evidence Layer inapanga ushahidi kwa muundo unaoauditika; haithibitishi alpha. Decision-ready set bado si trade-ready (P69).

*Evidence Set: dedup by value-object id (P75); order-invariant aggregate; set-confidence; snapshot readiness (P73); provenance graph (P72); pure ops (P71). NO Decision Engine. NO ML. Profitable ≠ Tradable Edge.*