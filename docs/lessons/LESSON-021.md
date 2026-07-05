# LESSON-021@v1

```yaml
id: LESSON-021@v1
claim: "The benefit a market event gets from context-ranking is event-specific: some events become in-sample profitable at the top context decile while others only improve toward zero."
type: MARKET-CONDITIONAL
evidence:
  - "event_context_matrix_report.md (Phase 4): context benefit (Top10 − All EV, net spread, online
    prequential) ranges +2.49 (mean_reversion: −0.20→+2.29) · pullback +2.47 · deep_pullback +2.14 ·
    trend_continuation +2.11 down to pattern_completion −0.81 (−1.26→−2.06)"
  - "5/9 events become profitable @Top10 (EV>0): mean_reversion, pullback, deep_pullback,
    trend_continuation, news_shock; breakout/vol_breakout/vol_expansion improve but stay <0"
counter_evidence: "these are the SAME event×context objects that FAILED prospective validation:
  Phase 14 (contextual_alpha_confirmation) — 282 pre-registered → 0 survived future-OOS + BH-FDR;
  the @Top10 profits are online-prequential in-sample (net spread, NO triple barrier, NO OOS)"
validity_conditions: {pairs: 9 FX, period: 2016-2024, events: 9 Tier-1/2, context: (vol_state,
  age-bucket) decile score F-008, metric: EV net spread, sample: IN-SAMPLE / online-prequential, no cost model}
review_trigger: "pre-registered future-OOS + FDR re-test of any specific event×context (P31; LESSON-009);
  cost-model integration; regime shift — any result forces a version; in-sample re-runs cannot promote it"
when_to_use: prioritizing WHICH events to study for context-conditioning — mean_reversion/pullback
  family respond most to context ranking; as a map of where context-response concentrates (not tradability)
when_not_to_use: never as evidence of tradable edge — the ranking @Top10 is in-sample and the same
  objects died 0/282 OOS; do not read 'profitable @Top10' as anything more than in-sample context response
provenance: {finding: F-008, phase: 4, doctrine: V5.3-V5.5, principle: P13}
lifecycle: CANDIDATE
```

**Maelezo kwa mwanafunzi:** context si swichi ya jumla — inanufaisha events tofauti kwa viwango
tofauti (mean_reversion +2.49 dhidi ya pattern_completion −0.81). Lakini "profitable @Top10" hapa ni
in-sample; Phase 14 iliua uhusiano huo OOS (0/282). Lesson ni RAMANI ya wapi context inajibu, si edge.
