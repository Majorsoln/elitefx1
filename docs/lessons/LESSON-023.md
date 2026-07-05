# LESSON-023@v1

```yaml
id: LESSON-023@v1
claim: "In-sample fit is systematically inflated by leakage across every event; only a no-lookahead out-of-sample projection measures the real structure."
type: METHOD
evidence:
  - "representation_operationalization_report.md (Phase 21): leak gap (joint-fit minus Nyström-OOS
    silhouette) present in ALL 5 events — pullback +0.328, deep_pullback +0.328, breakout +0.218,
    mean_reversion +0.227, trend_continuation +0.194 (mean +0.259)"
  - "in-sample/joint-fit silhouette mean 0.836 was leakage-inflated; true OOS (Nyström, fit-on-past-
    project-future) mean 0.577 — ~31% lower. Manifold survives OOS but is weaker than in-sample showed"
counter_evidence: "the structure did NOT vanish OOS — Nyström OOS silhouette 0.452..0.640, rolling
  walk-forward stable across 5 folds; leakage inflates the magnitude, it does not manufacture the
  structure from nothing (contrast LESSON-009 where the survivor WAS an artifact)"
validity_conditions: general as method; the leak-gap figures are FX manifold representations (robust
  norm + self-tuning spectral, Nyström OOS extension, 5-fold rolling, landmarks=700)
when_to_use: any time an in-sample metric (silhouette/R²/EV/accuracy) is reported — assume it is
  inflated until reproduced by a no-lookahead OOS projection; quantify the leak gap explicitly rather
  than trusting the in-sample number
when_not_to_use: a large leak gap is not proof the structure is fake — check whether it SURVIVES OOS
  (here it did, ~0.58); do not use leakage to dismiss a representation that still clears the OOS bar
provenance: {finding: F-039, phase: 21, doctrine: V6.4, principle: P44/P45}
lifecycle: ACTIVE  # Chief review 2026-07-05
```

**Maelezo kwa mwanafunzi:** in-sample silhouette 0.836 ilionekana imara; OOS halisi ilikuwa 0.577 —
imeinuliwa kwa ~31% na leakage, KILA event. Namba ya in-sample daima ni deni hadi ithibitishwe OOS
bila lookahead. Lakini leakage inainua ukubwa, haiundi structure isiyokuwepo — hapa ilinusurika.
