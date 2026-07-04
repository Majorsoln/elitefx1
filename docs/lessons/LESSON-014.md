# LESSON-014@v1

```yaml
id: LESSON-014@v1
claim: "Version identifiers embedded in every artifact convert version races into documented provenance instead of silent inconsistency."
type: GOVERNANCE
evidence:
  - "ARCHITECTURE_AUDIT.md Audit #3 (2026-07-02), drift item D-1: report ya D5 iliyoapproved ilizalishwa na policies @v1 wakati code ya sasa ni @v2 — iliruliwa 'SIO drift ya kificho': kesi ya kwanza halisi ya P88 kufanya kazi (version tofauti → decision ids tofauti; provenance iko wazi; re-run optional, D5 imefungwa kihalali)"
  - "decision_engine_report.md self-test [2]: kila Decision inabeba policy_id (P88) + snapshot_id refs (P84) — provenance inalindwa na TEST, sio convention"
counter_evidence: "versioning HAIKUZUIA race — G-2 (dual-branch race: run za main vs branch ya
  implementer) inabaki open governance risk (probability MEDIUM, Audit #3); versioning inafanya
  divergence isomeke, haifanyi isiwezekane"
validity_conditions: general (any artifact chain — code/policies/reports/lessons/datasets;
  demonstrated on D5 report-vs-code na P88 decision ids)
when_to_use: kubuni object/report/dataset yoyote mpya — id@vN tangu siku ya kwanza (Lesson corpus
  hii yenyewe inatumia P88-style ids; K3 datasets zitahitaji manifest + version); ukikutana na
  report-vs-code mismatch, swali la kwanza ni 'versions zipi?' kabla ya kuita drift
when_not_to_use: versioning si mbadala wa merge discipline (mitigation ya G-2 ni merge mapema /
  rebase mara kwa mara); usitumie 'provenance iko wazi' kama kisingizio cha kutokuregenerate
  artifact iliyopitwa pale decision inapoitegemea
provenance: {phase: D5→D6 (Audit #3), doctrine: Decision Doctrine V9, principle: P88/P84}
lifecycle: ACTIVE  # Chief review 2026-07-04
```

**Maelezo kwa mwanafunzi:** thamani ya P88 haikuonekana siku ilipoandikwa — ilionekana siku
mbili baadaye, race ya kwanza ilipotokea na kujibiwa kwa sentensi moja badala ya uchunguzi.
Provenance ni bima: unainunua kabla ya ajali.
