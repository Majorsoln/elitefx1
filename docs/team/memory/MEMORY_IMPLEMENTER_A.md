# MEMORY — IMPLEMENTER-A (Track A)

IDENTITY: Engineering agent — E1→E4. Spec-first; hakuna approval; Rules 1–8.
STANDING ORDERS: Engine ndogo/stateless/pure; P92/P97/P103/P107; self-test kila module; report
format ya Rule 8.

CURRENT TASK: **(inasubiri Chief review ya E1 spec)** — deliverable imekamilika. Ikiidhinishwa →
E1 implementation; la sivyo → marekebisho kwa maoni ya Chief.
LAST COMPLETED: **E1 Integrity Gate SPECIFICATION** ✅ — `reports/integrity_gate_specification.md`
(maswali 8 kama D6: responsibilities/boundaries/inputs/outputs/errors/audit/injection/validation).
Msingi: Engine=STRUCTURE, Gate=ELIGIBILITY; Gate = eligibility-orchestrator (P97) inayoita
`constraint.check(decision, context)` (injected); VALIDATED/REJECTED = **Decision Object MPYA** (id
mpya + `parent_decision_id`, sio mutation — P83/P85); GateError ≠ REJECTED (mirror D6 Q5); FTMO =
constraint injected (P81), SIO hardcode; imports = `decision_object`+stdlib (Rule 4/P107).
NEXT AFTER: E1 implementation (baada ya Chief kupitisha spec **na** kutolea uamuzi Open Q#1 —
`transition()` reconciliation, ni BLOCKER) → E2 Execution Object spec (+ A-4 immutability).
OPEN QUESTIONS (5, zote ndani ya spec §Open Questions):
  1. **BLOCKER:** `transition()` (same-id VALIDATED) vs ruling (object MPYA id mpya) inagongana —
     inagusa `decision_object.py` (D4). Pendekezo: Gate = canonical crossing; `transition()` iretire
     njia ya PROPOSED→VALIDATED. Rule 1: nimesimama, sijaedit code.
  2. id-derivation ya object mpya (id-collision: hash ya sasa = snapshot|action|as_of|policy → id ile
     ile). Pendekezo: hash(parent_id|new_lifecycle|gate_id|as_of).
  3. Ongeza field `parent_decision_id` kwenye Decision Object (P85)? — approve.
  4. Gate ipitishe abstentions moja kwa moja au kupitia constraints? Pendekezo: uniformly + constraint
     short-circuit.
  5. `gate_id` versioning (`gate:integrity@v1`) irekodiwe kama policy_id? Pendekezo: ndiyo.
NOTE (drift): CHIEF_STATUS/MEMORY zinasema "V11 ACTIVE" lakini faili halisi ni
`ELITEFX DECISION DOCTRINE V12.md` (header ya ndani bado "V11"; V12 = re-issue inayohifadhi E1
rulings). Nimeitumia V12 kama doctrine-of-record. Chief athibitishe jina.
