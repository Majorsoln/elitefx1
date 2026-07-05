# LESSON-022@v1

```yaml
id: LESSON-022@v1
claim: "Marginal component analysis understates discrimination: the effect lives in the interaction, and a component's sign can reverse conditional on another (age)."
type: MARKET-CONDITIONAL
evidence:
  - "component_interaction_report.md (Phase 5.7, Tier 1): joint EV-spread > marginal-max in every cell —
    vol×act 1.3 vs 0.8; vol×trans 2.8 vs 0.8; act×age 1.7 vs 0.7; transition×age 6.3 vs 0.8; 3-way
    vol×act×trans range 5.1 pips (HIGH×HIGH×Tmid +2.4 vs NORMAL×NORMAL×Tlo −2.6)"
  - "SIGN REVERSAL by age within one transition — Thi: age 1-3 = −0.5 → 4-8 = +3.0 → 9-15 = +1.7 →
    16+ = −3.2 (same transition, opposite sign across the lifecycle); F-012, Driver ≠ Gatekeeper"
counter_evidence: "interaction discrimination is IN-SAMPLE (net spread, Tier-1, pre-Phase-12); the
  same search space later produced 0/282 OOS survivors (Phase 14). Higher joint spread = more
  in-sample separation, NOT proven OOS edge (P32: identity needs independent explanatory power)"
validity_conditions: {pairs: 9 FX, period: 2016-2024, cells: vol/activity/transition/state_age
  terciles+buckets, min n/cell 100, metric: EV net spread, sample: IN-SAMPLE}
review_trigger: "pre-registered OOS + FDR on any joint cell (P31/LESSON-009); new representation;
  regime shift — any result forces a version; whole-sample interaction strength cannot promote it"
when_to_use: never judge a variable by its marginal EV alone — inspect joint cells (interactions can
  carry 6-8× the marginal spread) and watch for sign-flips conditional on a lifecycle variable (age)
  before calling a component a driver or a dead end
when_not_to_use: high joint EV-spread is not tradable edge (in-sample; 0/282 OOS); do not build a
  cell-rule engine on these interactions (LESSON-005: coordinate-cell rules do not generalize cross-pair)
provenance: {finding: F-012, phase: 5.7, doctrine: V5.6-V5.7}
lifecycle: CANDIDATE
```

**Maelezo kwa mwanafunzi:** transition ileile (Thi) inatoa −0.5, +3.0, +1.7, −3.2 kadri umri
unavyobadilika — marginal average ingeificha kabisa. Interactions hubeba discrimination (joint
6.3 vs marginal 0.8), lakini in-sample; usaidie kufikiri, si kutrade (Phase 14: 0/282 OOS).
