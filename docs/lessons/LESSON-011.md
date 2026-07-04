# LESSON-011@v1

```yaml
id: LESSON-011@v1
claim: "Context selection improves expected value through payoff size/asymmetry, not through win probability."
type: MARKET-CONDITIONAL
evidence:
  - "outcome_decomposition_report.md: decile D10−D1 ΔP(win) ≈ +3pp (small) vs ΔEV ≈ +4 pips (large), 4/4 Tier-1 events (F-010)"
  - "two mechanisms (F-011): Reward Expansion (Mean Reversion ΔAvgWin +3.6, Deep Pullback +3.1) vs Loss Compression (Pullback ΔAvgLoss −2.4, Trend Continuation −2.8)"
  - "context is a RANKING engine, not a binary filter (F-008: monotonic decile-EV, 3/3 events)"
counter_evidence: "P(TP) flat across context deciles (Phase 5 reopened) — the naive 'context →
  higher win rate' hypothesis was refuted, which is what forced this decomposition"
validity_conditions: {pairs: 9 FX, period: 2016-2024, events: Tier-1 (MR/PB/DPB/TC), representation:
  vol/spread/activity context deciles, raw pips no cost model}
review_trigger: cost-model integration; new event families; regime shift
when_to_use: designing selection/sizing — rank by context and expect better payoff distribution;
  do not promise higher hit-rate
when_not_to_use: outside tested events/pairs; and never as proof of tradable edge (raw pips ≠ net)
provenance: {finding: F-008/F-010/F-011, phase: 3.5/5.5, doctrine: V5.3-V5.5, principle: P13}
lifecycle: ACTIVE
```
