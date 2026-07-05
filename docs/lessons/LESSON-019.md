# LESSON-019@v1

```yaml
id: LESSON-019@v1
claim: "Adding state-age to a transition model sharpens probability estimates (LogLoss/Brier) without changing classification accuracy — age is a calibration variable, not a class predictor."
type: METHOD
evidence:
  - "state_transition_model_report.md (Phase 1.8): Model B(state,age) vs A(state) online prequential —
    LogLoss improves +2.0..+5.4% (EURUSD H1 0.322→0.309 = +4.0%; GBPUSD H2 0.343→0.325 = +5.4%),
    Brier slightly down (0.158→0.154), but ACCURACY FLAT (90→90 · 91→91 · 92→92 · 93→93% kila mahali)"
  - "state_age_report.md (Phase 1.6): P(stay) rises with age (median Δ 16+ vs 1-3: volatility +14.1pp,
    activity +40.0pp, spread +28.2pp) — hazard is age-dependent (not memoryless), WHY age informs probability"
counter_evidence: "at coarse timeframe / low n the gain vanishes or reverses — USDJPY D1 ΔLogLoss −0.1%
  ('age helps?' = —); ECE is mixed, not uniformly improved (e.g. 0.000→0.003). Calibration gain is not
  universal across timeframes"
validity_conditions: general as method; magnitude figures are FX (9 pairs, 2016-2024, H1-D1 bars,
  online prequential Laplace α=0.5)
when_to_use: any feature that improves LogLoss/Brier but NOT accuracy — recognize it as
  calibration/sharpening value; use it for sizing/abstention (probability quality), not for switching
  the predicted class; audit accuracy AND a proper scoring rule separately, never accuracy alone
when_not_to_use: do not discard the variable because accuracy is flat (that is the wrong metric — it
  DOES improve probability quality); do not assume the calibration gain holds at every timeframe (D1 fails)
provenance: {phase: 1.6/1.8, finding: (age-dependence of hazard)}
lifecycle: ACTIVE  # Chief review 2026-07-05
```

**Maelezo kwa mwanafunzi:** kuna aina mbili za "kuboresha utabiri": kubadilisha DARASA unalotabiri
(accuracy) na kunoa UWEZEKANO unaoshikilia (LogLoss/Brier/calibration). Age haifanyi ya kwanza,
inafanya ya pili. Mfumo unaopima accuracy pekee ungetupa variable yenye thamani halisi ya sizing.
