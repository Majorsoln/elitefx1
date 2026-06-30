# Evidence Operations — Evidence inatembeaje ndani ya mfumo? (Decision Science D1)

*2026-06-30 22:11 | 9 pairs, 180 tagged evidence objects | operations PURE (immutable, audit-trail) + conflict taxonomy | NO Decision Engine | NO ML*

> **P67** Evidence = Claim+Quality+Operational. **P68** Evidence ni immutable; aggregation ni OPERATION ya nje. **P69** decision-ready ≠ trade-ready. **P70 (OPEN)** confidence = model. D1: jinsi Evidence inavyotembea (operations), sio tu inavyoonekana. NO Decision Engine.

## Q1 — Operations juu ya Evidence Object

| operation | maana | matokeo |
|-----------|-------|---------|
| aggregate | inverse-variance combine (closed) | value -0.545, unc 0.069, n 170,124 |
| filter | chagua subset (mfano live) | 180/180 live |
| merge | mbili → moja | value -0.399 |
| expire | songesha age → operational state | fresh → expired |
| split | gawa support → unc inakua | n 21,969 → 10,984 (unc 0.171→0.242) |

## Q2 — Operations zipi zinahifadhi audit trail? (P66)

| operation | audit-preserving? | mfano audit |
|-----------|-------------------|-------------|
| aggregate | ✅ | ['aggregate(n=8)'] |
| filter | ✅ | ['make_evidence(src=EURUSD:H1:pullback)', 'filter(live)'] |
| merge | ✅ | ['merge(EURUSD:H1:pullback|EURUSD:H1:deep_pullback)'] |
| expire | ✅ | ['make_evidence(src=EURUSD:H1:pullback)', 'expire(+2005)'] |
| split | ✅ | ['make_evidence(src=EURUSD:H1:pullback)', 'split[0]'] |

→ operations ZOTE zinahifadhi audit trail (P66: kila decision itrace kwa evidence + ops zake).

## Q3 — Evidence Object ni immutable kweli?

- operations (expire/split) **hazibadilishi input**: ✅ input unchanged.
- `freeze(eo)` inatoa **read-only view** (MappingProxyType): ✅ write inakataliwa.
- by-convention dict ni mutable; operations ni PURE (zinazalisha objects mpya) + `freeze` kwa enforcement ya kweli. Hii ndiyo immutability ya contract (P68).

## Q4 — Conflict taxonomy

| conflict dimension | score | tafsiri |
|--------------------|-------|---------|
| intra (split-half) | 0.27 | kutoaminika ndani ya object moja (muda) |
| cross-pair | 0.07 | events zinapingana kati ya pairs |
| cross-timeframe | 0.02 | events zinapingana kati ya timeframes |
| cross-engine | 0.07 | events/representations tofauti zinapingana |

→ conflict **SIO scalar moja** — ina taxonomy. Decision Engine itahitaji kujua conflict *ya aina gani* kabla ya policy (P26 abstain kwa high cross-engine/cross-pair).

## Q5 — Operations gani zinabadilisha decision-readiness?

| operation | readiness inabadilika? |
|-----------|------------------------|
| (base) | ready=True |
| expire | ready True→False ✅ inabadilisha |
| split (support↓) | ready True→False ✅ inabadilisha |
| aggregate (conflicting) | ready→False ✅ inabadilisha (conflict) |

→ **expire, split, aggregate(conflict)** zinaweza kuondoa decision-readiness; filter inaiacha kwa zilizobaki. Readiness ni operational state, sio ya kudumu.

## VERDICT — D1 Evidence Operations

→ ✅ **Evidence Operations zimefafanuliwa** kama functions PURE juu ya objects immutable (P68): aggregate/filter/merge/expire/split — zote zinahifadhi **audit trail** (P66), hazibadilishi input (Q3), na zinaweza kubadilisha **decision-readiness** (Q5). Conflict ina **taxonomy** (intra/cross-pair/cross-timeframe/cross-engine), sio scalar (Q4). Object + operations sasa zimefungwa — msingi thabiti wa Decision Engine (haitabadilika tukibadilisha representation). **Hakuna Decision Engine bado.** NO ML.

**Bado Decision Science D1 — hakuna decision-action wala alpha.** Hii ni Evidence Engineering: jinsi evidence inavyotembea, kabla ya consumer (Decision Engine).

## Honest Caveats

1. **Immutability ni by-convention + `freeze`** — Python dict si frozen kwa asili; operations ni PURE lakini caller anaweza bado kumutate dict mbichi. Enforcement kamili (frozen dataclass) ni hatua ya engineering ya baadaye.
2. **Conflict taxonomy ni descriptive, sio causal** — cross-pair/cross-tf disagreement inaweza kutoka sample size / non-stationarity, sio 'evidence mbaya'. Ni ramani ya wapi kupingana, sio kwa nini.
3. **aggregate/merge zinadhani independence** (inverse-variance) — pair×tf za event moja zina correlation; combined uncertainty ni optimistic (caveat ya D0 inaendelea).
4. **split inadhani homogeneity** (inagawa value sawa, inakuza SE tu) — kiuhalisia sub-regimes zinaweza kuwa na value tofauti; split halisi inahitaji data ya sub-regime.
5. **Readiness/operations ≠ edge (P69).** Operations zinapanga evidence kwa muundo unaoauditika; hazithibitishi alpha — decision-ready bado ni mbali na trade-ready.

*Operations PURE (aggregate/filter/merge/expire/split) juu ya Evidence Objects immutable; audit trail; conflict taxonomy (intra/cross-pair/cross-tf/cross-engine); readiness-change. Principle 67–70. NO Decision Engine. NO ML. Profitable ≠ Tradable Edge.*