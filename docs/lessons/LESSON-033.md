# LESSON-033@v1

```yaml
id: LESSON-033@v1
claim: "When the winning cases share no common rule, model the population and rank it — do not classify into pass/fail, because the decision-relevant signal lives in the relative ordering, not in a threshold."
type: METHOD
evidence:
  - "PROGRAM_BOARD F-023 (APPROVED, configuration_engine_report.md): top configurations do not resemble
    one another (e.g. EURJPY·MeanReversion·C1·HIGH·SHORT·WIDE vs GBPUSD·TrendContinuation·C1·LOW·LONG·WIDE)
    — no single rule fits the winners; the engine must learn a POPULATION, not a rule (drives P23)"
  - "PROGRAM_BOARD F-008 (APPROVED, context_selectivity_report.md): binary context filtering was too
    permissive (~99% accept); decile RANKING showed strong monotonic EV (Pullback D1 −3.16 → D10 +1.29;
    Breakout −3.80 → −0.32; Mean Reversion −1.58 → +2.29; 3/3 events). Context = ranking system, not pass/fail"
counter_evidence: "ranking is the right FRAME but NOT proof of tradability: the CCS-ranked portfolio was
  −0.757 pips/trade OOS and Top-5% by train-CCS was −1.162 (worse than trade-all) — opportunity_engine_
  report.md. Ranking selects the native representation; it does not make the ordering survive OOS (LESSON-001)"
validity_conditions: general as method (population-ranking over rule-classification for heterogeneous
  winners); the market grounding is FX configurations (9 pairs, decile-EV curves 3/3 Tier-1 events)
when_to_use: framing any selection problem where the positive cases are heterogeneous — build a scoring/
  ranking model over the population and act on the ordering (top-k, deciles), rather than searching for a
  single classification rule that 'accepts' the good ones; a permissive binary filter (~99% accept) is a
  symptom that ranking is the correct frame
when_not_to_use: ranking is a REPRESENTATION choice, not evidence of edge — a monotonic in-sample decile
  curve can still die OOS (CCS portfolio −0.757); do not deploy a ranking without pre-registered OOS proof
  (LESSON-001/LESSON-029); and where a genuine single rule exists, a population model is needless complexity
provenance: {finding: F-023/F-008, phase: 3.5/6.5, principle: P21/P23}
lifecycle: ACTIVE  # Chief review 2026-07-05
```

**Maelezo kwa mwanafunzi:** configurations zinazoshinda hazifanani (EURJPY·MR·SHORT vs GBPUSD·TrendCont·LONG)
— hakuna KANUNI moja inayozibana. Kwa hiyo unajifunza *idadi* (population) na kupanga (rank), si ku-classify
pass/fail. Binary filter iliyokubali ~99% ilikuwa dalili kwamba ranking ndiyo frame sahihi. Lakini decile
curve nzuri in-sample bado inaweza kufa OOS (CCS −0.757) — ranking ni uwakilishi, si uthibitisho wa edge.
