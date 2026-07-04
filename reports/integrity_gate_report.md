# Integrity Gate — Implementation Report (E1, P105)

*2026-07-04 | IMPLEMENTER-A | Chief rulings Q1-Q5 (SPEC APPROVED, 2026-07-04) zimetekelezwa |
Spec: `reports/integrity_gate_specification.md` | Rules 1-8 | NO ML | NO FTMO hardcode*

> **VALIDATION ≠ ELIGIBILITY.** Engine inakagua STRUCTURE (D6); Gate inakagua ELIGIBILITY (E1).
> Gate = eligibility-orchestrator (Rule 3/P97) inayoita `constraint.check(decision, context)`
> zilizoinjectiwa; VALIDATED/REJECTED = Decision Object MPYA (id mpya + `parent_decision_id`, SIO
> mutation — P83/P85); FTMO = constraint injected (P81), SIO literal. Format: Rule 8.

---

## Implementation Report

**Deliverables (code):**

| Faili | Mabadiliko | Doctrine |
|-------|-----------|----------|
| `src/research/integrity_gate.py` | **MPYA** — `gate()` + `validate_decision()` (Q8) + `validate_constraint()` + `GateError`; `GATE_ID="gate:integrity@v1"`; `VERDICTS=(ELIGIBLE, INELIGIBLE)` | P105; Rule 3/4/5/6/7; P81/P97 |
| `src/research/decision_object.py` | **Q1** `transition()`: PROPOSED→VALIDATED **imeretire** (Gate = canonical crossing); **Q2** `_gate_decision_id()`; **Q3** field `parent_decision_id` (default None) + `make_gate_decision()`; self_test [7] mpya + _report zimesasishwa | P83/P85; Chief Q1-Q3/Q5 |

**Mtiririko (Gate ndani ya pipeline):**

```text
Engine(D6) ──▶ Decision Object (PROPOSED) ──▶ gate(decision, constraints, context) ──┬─▶ VALIDATED (id mpya, parent link)
                                              validate_decision (Q8, structural)     └─▶ REJECTED  (id mpya, parent link)
                                              for c in constraints: c.check(...)      ⇢ GateError (system failure, si REJECTED)
                                              AND/veto → make_gate_decision (object MPYA)
```

**Rulings zilizotekelezwa (1:1):**

- **Q1 (BLOCKER):** `transition()` haipiti tena PROPOSED→VALIDATED (inaraise). Crossing halali ni
  `make_gate_decision(parent, "VALIDATED"|"REJECTED", gate_id)` — object MPYA immutable. `transition()`
  inabaki kwa VALIDATED→EXECUTED→SETTLED na side-states (P86 CANCELLED bado salama).
- **Q2:** `id = "dec:" + sha1(parent_id | new_lifecycle | gate_id | as_of)[:10]` → VALIDATED na
  REJECTED za parent MMOJA zina id TOFAUTI, wala hazigongani na PROPOSED.
- **Q3:** `parent_decision_id` inanyoosha object mpya → PROPOSED (P85). Chain:
  `Snapshot → PROPOSED → VALIDATED`, zote append-only, immutable.
- **Q4:** uniform pass-through — Gate inaendesha decisions ZOTE (ikiwemo ABSTAIN); short-circuit iko
  ndani ya **constraint** (mf. constraint inarudisha ELIGIBLE kwa non-committing intent), SIO Gate.
- **Q5:** `gate_id = "gate:integrity@v1"` (P88 pattern) inarekodiwa kwenye object mpya (kama policy_id)
  → eligibility reproducible.

**Design invariants (spec Q1-Q8):**

- **Rule 3/P97 (Gate ndogo):** hakuna eligibility logic ndani ya Gate — risk/compliance/correlation/FTMO
  zote ni **constraints injected**. Gate inagusa surface mbili tu: `constraint["id"]` + `constraint["check"]`.
- **Rule 4 (ignorance):** direct imports = `decision_object` + stdlib PEKEE (imethibitishwa self-test [6]).
- **Rule 5 (stateless):** hakuna cache/global/budget-counter — risk-budget "state" inaishi kwenye
  `context` (injected). Module-mutables = `[]` (self-test [5]).
- **Rule 6 (correctness):** constraints ZOTE zinaendeshwa + audited (hakuna short-circuit ya Gate);
  AND/veto ni binary.
- **GateError ≠ REJECTED:** input batili (invalid_decision/lifecycle/constraint/verdict, constraint_failure)
  = system failure → error. Constraint INELIGIBLE = OUTCOME → REJECTED object (mirror EngineError vs ABSTAIN).

## Self Tests

`python src/research/integrity_gate.py --self-test` → **PASS** (7/7). Bila data ya nje (Rule 7).

```text
[1] Q8 validation: bad-decision · non-PROPOSED-blocked · bad-action              -> OK
[2] eligible→VALIDATED: new-id · parent-link · carry-over (action/policy/refs)   -> OK
[3] ineligible→REJECTED: lifecycle=REJECTED · failed constraint logged · all-audited -> OK
[4] GateError: invalid-constraint · constraint-failure · invalid-verdict          -> OK
[5] deterministic + stateless: id-stable · module-mutables=[] · validated≠rejected -> OK
[6] gate ignorance (Rule 4) + P81 no-FTMO-import: bad-imports=[] · market-leak=[]  -> OK
[7] injection: empty→VALIDATED · abstain short-circuit→VALIDATED · commit→REJECTED -> OK
```

Regression (modules zilizoathirika/zinazohusiana) — zote **PASS**:

```text
decision_object : PASS   (test [7] mpya: transition-retired · new-id · parent-link)
decision_engine : PASS   (haijaguswa; inatumia make_decision + field mpya)
decision_policy : PASS
integrity_gate  : PASS
```

Mazingira: self-tests zilizoendeshwa hapa baada ya `pip install numpy polars duckdb pyyaml`
(zinahitajika na chain iliyopo — decision_object → market_state_engine). Kwenye PC ya Operator stack
tayari ipo.

## Known Limitations

1. **P107 transitive purity — inarithi baseline FAIL (Audit #5), SIO leak mpya.** `integrity_gate`
   DIRECT imports = `decision_object` + stdlib (PURE ✅, kama Engine). LAKINI `decision_object` ina-import
   `numpy` + `market_state_engine` (→polars) module-level, hivyo Gate haiwezi ku-load bila Market stack.
   Imethibitishwa kwa clean-env probe (2026-07-04). **E1 haiongezi impurity yoyote mpya**; remediation
   (options a/b/c) ni **uamuzi wa Chief #1 uliopo PENDING** — sijaipreempt (Rule 1). *Tathmini: mara
   remediation itakapopita, Gate inakuwa transitive-pure bila mabadiliko ya E1 logic.*
2. **Constraints/context providers bado hazipo** — Gate ni interface. Risk-budget, compliance,
   correlation, na FTMO (P81) ni Execution Science (haijaanza). Hadi zipatikane, caller anapitisha
   constraints kwa mkono (kama policy leo, P96 OPEN).
3. **Eligibility ni binary** (ELIGIBLE/INELIGIBLE). Hakuna "conditional/degraded" — sizing/haircut ni
   Execution Science, sio Gate.
4. **Immutability ni by-convention** (make_gate_decision inarudisha object mpya; parent haibadilishwi —
   imethibitishwa self-test). Enforcement kamili (frozen) ni A-4, inafungwa **E2** (P89) — sio E1.
5. **Gate haithibitishi chochote kiuchumi** — ita-orchestrate constraints ambazo bado hazipo;
   decision-eligible ≠ trade-profitable (P69). Protect capital first.
6. **VALIDATED→EXECUTED bado iko kwenye `transition()`** (same-id) — E2 (Execution Object) itashughulikia
   crossing hiyo; E1 iligusa PROPOSED→VALIDATED pekee (kama Chief alivyoagiza).

## Open Questions

1. **Symmetry ya REJECTED kwenye `transition()`.** Gate hutoa REJECTED kama object MPYA (make_gate_decision).
   `transition()` bado inaruhusu PROPOSED→REJECTED (same-id) kwa matumizi yasiyo ya eligibility. Je,
   iretire pia kwa symmetry na Q1, au ibaki? (Chief Q1 iligusa VALIDATED pekee.) **Pendekezo:** ibaki
   kwa sasa (non-gate rejection), i-review E2.
2. **`context` schema.** Reproducibility ya eligibility inahitaji `context` iwe na version/hash
   (mirror P95). Je, tuongeze `context_version`/`context_ref` E1, au tuiache hadi Execution Science
   ilete constraints halisi? **Pendekezo:** subiri constraints halisi (E-later) — schema ifuate mahitaji.
3. **Combination rule zaidi ya AND/veto.** Sasa: constraint yoyote INELIGIBLE → REJECTED. Je, kutakuwa
   na constraints za "warning" (non-veto) baadaye? **Pendekezo:** hapana E1 — veto binary ni RED LINE
   ya eligibility; warnings ni Execution Science.
4. **P107 remediation** (option a/b/c) — bado PENDING Chief #1. E1 inashiriki dependency ile ile ya
   `decision_object`; remediation moja itaponya Engine + Gate kwa pamoja.

---

*Integrity Gate = eligibility orchestrator only (P97); contract pekee = constraint.check(decision,
context); PROPOSED Decision Object pekee kama input (P83); VALIDATED/REJECTED = object MPYA, sio
mutation (P83/P85); FTMO = injected constraint (P81), sio hardcode; direct imports safi (Rule 4),
transitive inarithi baseline (P107, remediation PENDING Chief). Engine = STRUCTURE, Gate = ELIGIBILITY.
Self-test PASS 7/7. NO ML. Profitable ≠ Tradable Edge. Protect capital first.*
