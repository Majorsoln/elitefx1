# LESSON-001@v1

```yaml
id: LESSON-001@v1
claim: "Static historical ranking of trading configurations does not generalize out-of-sample."
type: METHOD
evidence:
  - configuration_engine_report.md: "train+→+ ≈42% vs train−→− ≈66% (positive edge does not persist; negative does)"
  - opportunity_engine_report.md: "Top 5% by train-CCS = −1.162 OOS, worse than trade-all; CCS-selection portfolio −0.757 OOS"
counter_evidence: none found (scope: 9 FX pairs, 4 budget levels tested; only budget-25 positive,
  explained by availability effects, not ranking quality)
validity_conditions: general (method lesson; demonstrated on 9 FX pairs, 2016–2024, volume bars,
  configuration-level ranking)
when_to_use: any system that ranks strategies/configurations on historical performance and
  allocates capital by that rank; any backtest showing "top decile works"
when_not_to_use: ranking used only for REMOVAL of persistent negatives — negative edge IS
  persistent (F-022), so remove-bad-first survives where select-good fails (P26)
provenance: {finding: F-022 (CORE), phase: 8, doctrine: V5.17, principle: P26}
lifecycle: ACTIVE
```

**Maelezo kwa mwanafunzi (binadamu au model):** kushindwa kwa Phase 8 hakukuwa kushindwa kwa data —
kulikuwa ugunduzi kwamba asymmetry ipo: ubaya unadumu, uzuri haudumu. Mfumo sahihi unaanza kwa
kuondoa ubaya, si kutafuta uzuri.
