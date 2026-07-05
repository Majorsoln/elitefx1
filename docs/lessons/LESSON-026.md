# LESSON-026@v1

```yaml
id: LESSON-026@v1
claim: "Evidence conflict must be an explicit, separately-tolerable decision input — not folded into a single readiness or confidence score."
type: GOVERNANCE
evidence:
  - "decision_policy_report.md (D5): action derives from readiness_state (P82) + reliability + CONFLICT
    as distinct inputs — not from a market prediction; default ABSTAIN (P26); unresolved high conflict → ABSTAIN"
  - "G-7 amendment (Decision Doctrine V8, 2026-07-02, board approval log): 'conflict = explicit policy
    input; per-policy tolerance (capital_preservation 0.00; conservative/aggressive CONFLICT_CEIL);
    logic changed → policies bumped to @v2 (P88 versioning)'"
  - "evidence_theory_report.md (D0): conflict has a TAXONOMY (intra/split-half · cross-pair · cross-
    timeframe · cross-engine), measured controlling for the other dimensions — 'not a scalar' (P74)"
counter_evidence: "none found (scope: Decision Architecture D0-D5). Bound: making conflict explicit
  does not resolve it — high unresolved conflict maps to ABSTAIN, not to a confident either-side call;
  explicitness is about auditability/policy-control, not about producing an answer"
validity_conditions: general (any evidence-aggregation → decision boundary; demonstrated on the
  Decision Policy / Evidence Snapshot architecture, 9 pairs, 5 snapshots, 3 policies)
when_to_use: designing any aggregation-to-decision step — surface conflict/disagreement as a
  first-class signal with its own per-policy tolerance, so different risk postures can treat the same
  conflict differently (capital-preservation abstains at 0.00; aggressive tolerates up to a ceiling)
when_not_to_use: do not hide conflict inside a blended readiness/confidence number — that removes the
  policy's ability to tune tolerance and erases the audit trail (the G-7 change existed precisely to
  pull conflict OUT of the readiness bundle)
provenance: {phase: D5, principle: P74/P82/P88, doctrine: Decision Doctrine V8 (G-7)}
lifecycle: CANDIDATE
```

**Maelezo kwa mwanafunzi:** conflict ikifichwa ndani ya readiness/confidence score moja, policy
inapoteza uwezo wa kuiweka tolerance na audit trail inafutika. G-7 ilitoa conflict NJE kama input
wazi (capital_preservation 0.00 · aggressive CONFLICT_CEIL), policies → @v2. Uwazi si ufumbuzi —
conflict kubwa isiyotatuliwa → ABSTAIN, si upande wa uhakika.
