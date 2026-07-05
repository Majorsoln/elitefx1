# LESSON-028@v1

```yaml
id: LESSON-028@v1
claim: "Architectural purity means transitive dependency purity, not just the absence of direct forbidden imports — the dependency graph is the architecture."
type: GOVERNANCE
evidence:
  - "PROGRAM_BOARD P107 APPROVED (V11, 2026-07-03): source OBS-1 (Chief #2) — decision_object.py had
    no market logic yet imported market_state_engine, so the Decision Engine could not load without the
    entire Market stack. Direct purity ≠ transitive purity"
  - "decision_repository_report.md (E3): self-test verifies 'stdlib-pure imports (P107 transitively PURE)'
    — the remediation is checkable (6/6 PASS); transitive purity became a testable gate, not a slogan"
counter_evidence: "none found (scope: Decision/Execution architecture D0-E4). Bound: transitive purity
  constrains the import graph, not runtime behaviour — a transitively-pure module can still be logically
  wrong; purity is a necessary architectural property, not a correctness proof"
validity_conditions: general (any layered/modular system with a dependency direction; demonstrated on
  the Market↔Decision boundary and the E1-E4 chain)
when_to_use: reviewing any module's compliance — check what it TRANSITIVELY pulls in (build/import the
  module in isolation), not just whether its own body contains forbidden calls; encode the check as a
  test (E3 did: import-purity self-test) so drift is caught automatically
when_not_to_use: transitive purity is not a substitute for correctness or interface design — a clean
  dependency graph atop a wrong contract is still wrong; do not let 'imports are pure' imply 'logic is right'
provenance: {principle: P107, doctrine: (Permanent Truth 11), phase: Audit#5/E3, finding: OBS-1}
lifecycle: CANDIDATE
```

**Maelezo kwa mwanafunzi:** module inaweza kuwa haina market logic yoyote kwenye mwili wake, lakini
ikiimport market stack — haiwezi ku-load bila hiyo. Purity halisi ni ya **dependency graph** nzima
(transitive), si direct imports pekee. E3 iliifanya itestike (import-purity self-test), si kauli tu.
