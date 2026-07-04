# LESSON-003@v1

```yaml
id: LESSON-003@v1
claim: "Positive predictive or explanatory value does not imply positive decision value; the three are independent dimensions."
type: METHOD
evidence:
  - decision_value_framework_report.md: "0/9 variables carried Selection Decision Value OOS despite good prediction value and explanation value (Phase 26)"
  - representation_value_report.md: "representation lifted EV-selection while LogLoss unchanged (Phase 5.13) — the converse direction"
counter_evidence: none found (scope: SELECTION decision only, OOS ΔEV metric; per P60 failure under
  one decision type does not imply failure under all — abstention/sizing/hedging untested)
validity_conditions: general (method lesson; any pipeline that assumes Prediction → Decision)
when_to_use: whenever a feature/model is justified by predictive metrics (accuracy, LogLoss, R²) —
  demand a decision-level test (does it change what you DO, out-of-sample?) before adoption
when_not_to_use: do not generalize a failed SELECTION test to all decision types (P60); do not
  discard predictive/explanatory value entirely — they serve understanding, just not decisions
provenance: {finding: Phase 26 scoreboard, phase: 26, doctrine: V6.9, principle: P58/P60}
lifecycle: ACTIVE
```

**Maelezo kwa mwanafunzi:** kwa miongo, quant practice ilidhani `Prediction → Decision`. Data
ilikataa mnyororo huo. Kipimo cha mwisho cha information si "inatabiri?" bali "inabadilisha
unachofanya, nje ya sample?"
