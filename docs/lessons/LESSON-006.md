# LESSON-006@v1

```yaml
id: LESSON-006@v1
claim: "Cross-algorithm agreement is the wrong validity criterion for a representation; decision quality is the right one — and internal stability is not external validity."
type: METHOD
evidence:
  - "cluster_robustness_report.md: cross-algorithm ARI ≈0.12 (KMeans/GMM/Agglomerative solve different objectives) — old Principle 18 REMOVED (V5.12)"
  - "taxonomy_robustness_report.md: KMeans split-half stability 0.97 yet cross-algo ARI 0.08–0.30 → stable ≠ true (P41)"
  - "representation_value_report.md: the same representation improved EV-selection (F-019) — value shown at the decision level, not the agreement level"
counter_evidence: none found (scope: unsupervised structures; supervised settings have ground truth
  and different criteria)
validity_conditions: general (evaluation of unsupervised representations)
when_to_use: judging any clustering/representation — ask "does it improve a decision?" not "do
  algorithms agree?"; treat self-consistency metrics as necessary-but-weak
when_not_to_use: do not use this to skip robustness checks entirely — low agreement still demands
  a representation audit (P43) before trusting any single algorithm's output
provenance: {finding: F-018/F-019, phase: 5.11–5.13/19, doctrine: V5.12/V6.2, principle: P18(new)/P41}
lifecycle: ACTIVE
```
