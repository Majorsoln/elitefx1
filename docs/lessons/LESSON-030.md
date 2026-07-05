# LESSON-030@v1

```yaml
id: LESSON-030@v1
claim: "A system failure is categorically distinct from a valid negative outcome, and every domain crossing mints a new immutable object with a parent link — never a mutation."
type: GOVERNANCE
evidence:
  - "integrity_gate_report.md (E1): VALIDATED/REJECTED = a NEW Decision Object (new id + parent_decision_id),
    not a mutation; transition() PROPOSED→VALIDATED was RETIRED (the Gate is the canonical crossing);
    GateError (system failure) ≠ REJECTED (a valid eligibility outcome)"
  - "execution_object_report.md (E2): 'ExecutionError ≠ REJECTED/UNFILLED — mirror Engine/Gate'; status
    ∈ {FILLED, PARTIAL, REJECTED, UNFILLED} is a FACT derived from the report, while ExecutionError is a
    system failure; deep-freeze (frozen.py 5/5 PASS) enforces immutability of the minted object"
  - "broker_adapter_report.md (E4): same mirror — AdapterError (system failure) vs REJECTED outcome;
    the pattern repeats identically across E1→E2→E4"
counter_evidence: "none found (scope: E1-E4 Execution architecture). Bound: the pattern is about object
  lifecycle and error taxonomy, not about whether the outcome is good — a cleanly-minted REJECTED object
  is still a rejection; the discipline buys auditability, not success"
validity_conditions: general (any pipeline with domain crossings and outcomes; demonstrated across the
  full E1-E4 Execution chain)
when_to_use: designing any stage that transforms a domain object (validate/execute/settle) — mint a NEW
  immutable object with a parent_id (never mutate in place), and keep a system-failure exception strictly
  separate from a valid negative outcome (REJECTED/UNFILLED are data, errors are faults)
when_not_to_use: do not collapse the two — swallowing a system failure as a 'negative outcome' hides
  faults; and do not mutate an object 'for efficiency' (immutability + parent lineage is the audit trail)
provenance: {phase: E1/E2/E4, principle: P83/P85/P87/P89, doctrine: (Execution Science)}
lifecycle: CANDIDATE
```

**Maelezo kwa mwanafunzi:** kuvuka domain yoyote (validate → execute → settle) kunazaa object MPYA
yenye `parent_id`, si mutation — hiyo ndiyo audit trail. Na kosa la mfumo (GateError/ExecutionError/
AdapterError) SI matokeo hasi halali (REJECTED/UNFILLED). Pattern hii ilijirudia bila kubadilika E1→E4.
