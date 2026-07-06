# LESSON-034@v1

```yaml
id: LESSON-034@v1
claim: "Expected payoff alone misranks opportunities; confidence (sample quality, persistence, walk-forward stability) is a co-equal ranking dimension — but a confidence-selected portfolio is not thereby tradable."
type: METHOD
evidence:
  - "PROGRAM_BOARD F-024 (APPROVED, confidence_engine_report.md): ranking Top-25 by EV vs by CCS overlap
    only 10/25 (Spearman ρ ≈ +0.91 but the tails diverge); high-EV/low-N configurations get demoted —
    Expected Payoff alone misleads; ranking must fold in confidence interval, persistence, sample quality (CCS)"
  - "PROGRAM_BOARD F-025 (APPROVED, confidence_engine_report.md): CCS carries no capacity — CCS=5.4
    occurring 2×/yr ≠ CCS=3.9 occurring 300×; portfolio value depends on Availability (frequency), not
    magnitude alone (drives Opportunity Score = Quality × Availability, P25)"
counter_evidence: "confidence-as-ranking is valuable, but CCS-SELECTION as a portfolio is a dead end: the
  CCS-selected universe returned −0.757 pips/trade OOS and Top-5% by train-CCS −1.162 (opportunity_engine_
  report.md, Phase 8 — REJECTED). Confidence sharpens the ranking; it does not manufacture positive OOS edge"
validity_conditions: general as method (confidence as a ranking dimension co-equal with EV); grounding is
  the FX CCS work (Configuration Confidence Score over 9 pairs; EV-vs-CCS overlap 10/25)
when_to_use: ranking opportunities where sample sizes and stability vary — never rank on point-estimate EV
  alone; demote high-EV/low-N cases and weight persistence + walk-forward stability + sample quality, and
  account separately for availability (frequency), since a rare high-CCS edge is not a portfolio
when_not_to_use: do not treat a confidence-selected set as tradable — CCS-selection died OOS (−0.757);
  confidence improves the ORDERING, it is not itself proof of edge (LESSON-029); and CCS without a capacity
  dimension over-credits rare configurations (F-025)
provenance: {finding: F-024/F-025, phase: 7-8, principle: P24/P25}
lifecycle: ACTIVE  # Chief review 2026-07-05
```

**Maelezo kwa mwanafunzi:** kupanga kwa EV pekee kunadanganya — Top-25 kwa EV na kwa CCS zinaingiliana 10/25
tu; configs zenye EV kubwa lakini N ndogo zinashushwa. Confidence (CCS) ni *mwelekeo wa pili* wa ranking wenye
thamani sawa na EV. LAKINI CCS-selection kama portfolio ilikufa OOS (−0.757) — confidence inanoa mpangilio,
haitengenezi edge. Na CCS bila *availability* (5.4 mara 2/mwaka ≠ 3.9 mara 300) inazidi kusifia nadra.
