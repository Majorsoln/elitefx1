# LESSON-024@v1

```yaml
id: LESSON-024@v1
claim: "Interpretability and predictive value are separate axes; a semantic layer that loses R² is not failing — judge it by stability and recoverability, not by prediction."
type: METHOD
evidence:
  - "semantic_taxonomy_report.md (Phase 22): semantic labels lose predictive value — R²(label)/R²(id)
    = 0.01 for 3 vs 15 groups; yet Q2 interpretable (distinct ≥0.5) = 10/15 (67%) and vocabulary transfers"
  - "semantic_consistency_report.md (Phase 23): labels stable to ±20% threshold perturbation
    (ARI mean 0.890, min 0.887), data-driven recoverable (meta-cluster vs rule ARI 0.620), 2/5 labels
    consistent cross-pair/event — Principle 48: interpretability ≠ prediction (R² drop is NOT failure)"
counter_evidence: "consistency of RULE labels is not proof of real universality — the labels are the
  output of human-chosen thresholds (ZTHR=0.5, CONS_THR=0.7, ±20%); F-040 (shared vocabulary over
  event-specific geometry) stays OPEN until vocabulary is built fully data-driven"
validity_conditions: general as method; the semantic demonstration is FX (9 pairs, 5 events, 135
  clusters, robust-norm spectral representation)
when_to_use: evaluating any interpretation/semantic/naming layer — score it on stability (ARI to
  perturbation) and recoverability (data-driven ARI), not on R²/predictive lift; an interpretable
  label losing variance-explained is expected, not a defect
when_not_to_use: do not treat a stable, interpretable label as validated market truth — 'interpretable'
  = profile-distinctiveness (a linguistic hypothesis), not proof the named mechanism is real; keep
  discovery unsupervised, semantics strictly post-hoc (LESSON-004)
provenance: {finding: F-040, phase: 22-23, doctrine: V6.4-V6.6, principle: P46/P47/P48/P50}
lifecycle: ACTIVE  # Chief review 2026-07-05
```

**Maelezo kwa mwanafunzi:** semantic layer ilipoteza R² (ratio 0.01) lakini ilikuwa stable (ARI 0.89)
na recoverable (ARI 0.62). Hilo si kushindwa — interpretability na prediction ni axes mbili tofauti
(P48/P50). Unapima layer ya tafsiri kwa uthabiti/urejeleaji, si kwa R².
