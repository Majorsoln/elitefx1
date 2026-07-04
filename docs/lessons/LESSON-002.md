# LESSON-002@v1

```yaml
id: LESSON-002@v1
claim: "Multiple-testing correction is mandatory: apparent edges multiply with context refinement and vanish under FDR control."
type: METHOD
evidence:
  - contextual_alpha_report.md: "30 'candidate alpha' objects discovered via context refinement (Phase 13)"
  - contextual_alpha_confirmation_report.md: "282 pre-registered hypotheses, future OOS, Benjamini-Hochberg FDR → 0 survived (Phase 14)"
counter_evidence: none found (scope: the one representation tested — Event+Pair+Vol+Spread+Session;
  note F-033: failure of a representation is not proof of no alpha)
validity_conditions: general (method lesson; any search over many context combinations)
when_to_use: any time a search/refinement process produces "discoveries" — count the comparisons,
  pre-register, hold out future data, apply FDR before believing anything
when_not_to_use: do not use the 30→0 result to conclude "no alpha exists" — that conflates
  representation failure with absence of structure (F-033/P33); the correct next step is to audit
  the representation, not to abandon the search or to double down on more data
provenance: {finding: F-032 (CONFIRMED) + F-033, phase: 14, doctrine: V5.23, principle: P31/P32/P33}
lifecycle: ACTIVE
```

**Maelezo kwa mwanafunzi:** refinement inaongeza *apparent* edge na *false-discovery risk* kwa
wakati mmoja — huwezi kupata ya kwanza bila kubeba ya pili. Nidhamu (pre-registration, OOS, FDR)
ndiyo bei ya kuamini chochote.
