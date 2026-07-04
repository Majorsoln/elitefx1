# LESSON-010@v1

```yaml
id: LESSON-010@v1
claim: "Assume non-stationarity: edge persistence must be re-proven per window, never extrapolated from past performance."
type: METHOD
evidence:
  - "survivability_engine_report.md: median edge survival 1/6 windows; ~2% survive all; decay slope ≈ −0.87 pips/window (F-028)"
  - "edge_reality_report.md: randomized-time survivors 39 ≫ observed 9 — the real time-order destroys persistence (F-029: market non-stationarity)"
  - "edge_drift_report.md: early quality → future persistence, causal ρ≈0.03 (F-027); environment does not explain decay"
counter_evidence: none found (scope: 9 FX pairs 2016-2024; negative edge DOES persist — F-022 —
  the asymmetry is itself part of the lesson)
validity_conditions: general as method; magnitude figures are MARKET-CONDITIONAL (FX, volume bars,
  2016-2024)
when_to_use: any system design that assumes a measured edge will continue — build re-validation
  (walk-forward, living-edge preference P27) into the architecture, not as an afterthought
when_not_to_use: do not conclude 'nothing persists' — bad configurations persist (~66%), and that
  persistence is exploitable via removal (P26)
provenance: {finding: F-027/F-028/F-029 + F-022, phase: 9-11, doctrine: V5.18-V5.20, principle: P26/P27/P28}
lifecycle: ACTIVE
```
