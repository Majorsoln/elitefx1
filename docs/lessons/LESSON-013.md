# LESSON-013@v1

```yaml
id: LESSON-013@v1
claim: "Writing and reviewing a specification before any code yields smaller and more compliant implementations than code-first development."
type: GOVERNANCE
evidence:
  - "decision_engine_report.md (D6): engine core ~60 lines, functions 2 (decide, decide_batch), self-tests 5/5 PASS, forbidden imports = 0 (self-test [4]: bad-imports=[], forbidden-words=[]) — compliance checklist P92–P102 yote ✓"
  - "decision_engine_specification.md: spec ilijibu maswali 8 ya Chief na kufunga Engine kwenye responsibility MOJA (P97) kabla mstari wa kwanza wa code haujaandikwa"
  - "PROJECT_MEMORY.md §3.1: 'D6 (spec → architecture review → implementation) ilitoa implementation safi zaidi ya mradi'; timeline §1: D6 CLOSED = 'implementation iliyokataa kuwa ngumu'"
counter_evidence: "none found for contract components (scope: D0–D6 record). Boundary: Chapter One
  research probes (Phases 0–26, reports 55+) ziliendeshwa report-first bila spec rasmi na zilizaa
  findings 42 — spec-first imethibitishwa kwa CONTRACT components, sio exploratory harnesses"
validity_conditions: general (demonstrated on Decision Engine D6 — full case; D0–D5 contract-first
  record inaunga mkono)
when_to_use: kila component yenye contract surface (E1–E4, K-series tooling) — order ni
  spec → architecture review → implementation → compliance checklist; spec ndiyo hatua ambapo
  complexity inaondolewa, sio code review
when_not_to_use: exploratory research probes ambapo SWALI (sio interface) ndiyo product — kulazimisha
  spec ritual kamili kwenye analysis harness ya mara moja kunapunguza kasi ya discovery bila kuongeza
  compliance value (precedent ya Chapter One); spec-first pia si kinga ya version races (angalia
  LESSON-014 / D-1)
provenance: {phase: D6 (Decision Architecture), doctrine: Decision Doctrine V10→V11, principle: P90–P102 (spec-defined)}
lifecycle: ACTIVE  # Chief review 2026-07-04
```

**Maelezo kwa mwanafunzi (binadamu au model):** discovery kubwa ya D6 haikuwa engine — ilikuwa
mchakato. Complexity iliuawa kwenye karatasi (spec review), hivyo code haikupata nafasi ya kuwa
ngumu. Kanuni: kwa contract component, gharama ya kufikiri kabla < gharama ya ku-refactor baadaye.
