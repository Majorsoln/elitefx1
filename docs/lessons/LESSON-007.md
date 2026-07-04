# LESSON-007@v1

```yaml
id: LESSON-007@v1
claim: "Rare/extreme market states are execution-risk states, not payoff states."
type: MARKET-CONDITIONAL
evidence:
  - "rare_state_analysis.md (5.10R): rare-state mean move ≈23.8 pips vs non-rare ≈26.2 (ratio ≈0.91× — NO payoff premium); spread +12σ; activity −1σ — H-05 REJECTED"
counter_evidence: none found (scope: payoff hypothesis tested and rejected; execution-risk
  hypothesis H-06 remains OPEN/untested — Phase 5.12 queued)
validity_conditions: {pairs: 9 FX, period: 2016-2024, rarity: state-vector rarity in volume-bar
  representation}
review_trigger: Phase 5.12 execution-risk validation; any live execution data from E-series
when_to_use: sizing/abstention around extreme states — expect the danger in the SPREAD (cost),
  not opportunity in the move; "rare = big move" intuition is false here
when_not_to_use: do not treat as proof that rare states are safe to trade with tight costs —
  the execution-risk half is unproven, so the conservative reading (avoid) stands
provenance: {finding: F-017/H-05→H-06, phase: 5.10/5.10R, doctrine: V5.11/V5.12}
lifecycle: ACTIVE
```
