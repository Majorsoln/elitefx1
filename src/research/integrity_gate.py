"""
integrity_gate.py — DECISION SCIENCE E1 (IMPLEMENTATION; Chief-approved spec + rulings Q1-Q5).

VALIDATION ≠ ELIGIBILITY. Engine inakagua STRUCTURE (D6); Gate inakagua ELIGIBILITY (E1). Gate =
GENERIC eligibility-orchestrator tu: inapokea Decision Object (PROPOSED) + EligibilityConstraints
(injected) + context, inaita `constraint.check(decision, context)`, inaunda Decision Object MPYA —
VALIDATED (zote ELIGIBLE) au REJECTED (yoyote INELIGIBLE). HAKUNA eligibility logic hapa (logic ni
ya constraints — Rule 3/P97). HAKUNA FTMO hardcode (P81: FTMO = constraint injected, si literal).

Spec: reports/integrity_gate_specification.md (maswali 8). Chief rulings (2026-07-04, SPEC APPROVED):
  Q1  Gate = canonical crossing PROPOSED→VALIDATED; transition() imeretire (decision_object).
  Q2  id ya object mpya = hash(parent_id | new_lifecycle | gate_id | as_of).
  Q3  parent_decision_id (P85 traceability) — object mpya inanyoosha nyuma kwa PROPOSED.
  Q4  uniform pass-through: Gate inapitisha decisions ZOTE; constraint yenyewe inaweza short-circuit.
  Q5  gate_id = "gate:integrity@v1" (P88 pattern) — irekodiwe kama policy_id.

Chief Implementation Rules (D6/E1):
  Rule 3  Gate ndogo — eligibility logic yote iko kwenye constraints (injected).
  Rule 4  Gate inajua TU: Decision Object · Constraint · Context. Imports: decision_object + stdlib.
  Rule 5  Stateless — no cache, no globals, no budget-counter (budget "state" iko kwenye context).
  Rule 6  Correctness kwanza — constraints ZOTE zinaendeshwa + audited (hakuna short-circuit ya Gate).
  Rule 7  Self-test (chini) — bila data ya nje.

Doctrine: P105 (Integrity Gate), P81 (FTMO=execution constraint), P83/P85 (object MPYA immutable,
sio mutation; parent link), P97/Rule 3 (orchestrator, si decider), P88 (gate_id versioned).

Self-test: python src/research/integrity_gate.py --self-test
"""
from __future__ import annotations

import argparse

from decision_object import make_gate_decision, ACTIONS

ACTIONS = tuple(ACTIONS)   # rebind list→tuple: immutable membership-set kwa Q8/D2 (stateless — Rule 5)

# Gate identity (Chief Q5; P88 pattern) — inarekodiwa kwenye VALIDATED/REJECTED object
GATE_ID = "gate:integrity@v1"
# Verdict enum ya constraint (spec Q7) — eligibility ni binary; sizing/haircut ni Execution Science
VERDICTS = ("ELIGIBLE", "INELIGIBLE")
# Contract fields (spec Q8): Decision Object envelope + Constraint contract
DECISION_REQUIRED = ("id", "action", "evidence_refs", "policy_id", "lifecycle", "audit", "timestamp")
CONSTRAINT_REQUIRED = ("id", "check")


class GateError(ValueError):
    """Input haitimizi contract ya Gate (SYSTEM failure — SIO REJECTED). Mirror ya EngineError:
    kukataliwa kwa eligibility (INELIGIBLE) ni OUTCOME (REJECTED object); kushindwa kwa mfumo ni error."""


def validate_decision(decision):
    """Q8 (structural PEKEE): decision NI Decision Object halali NA iko PROPOSED. Gate HAIrevalidate
    snapshot (Engine ilifanya D6/Q8) wala haisomi values kwa eligibility (hiyo ni constraints)."""
    if not isinstance(decision, dict):
        raise GateError("invalid_decision: si mapping")
    missing = [f for f in DECISION_REQUIRED if f not in decision]          # D1/D3/D5
    if missing:
        raise GateError(f"invalid_decision: inakosa fields {missing}")
    if decision["action"] not in ACTIONS:                                  # D2 (P60)
        raise GateError(f"invalid_decision: action {decision['action']!r} nje ya enum")
    if not isinstance(decision["audit"], list):                            # D5
        raise GateError("invalid_decision: audit si list")
    if decision["lifecycle"] != "PROPOSED":                                # D4 — Gate inagate PROPOSED pekee
        raise GateError(f"invalid_lifecycle: {decision['lifecycle']} (PROPOSED pekee)")
    return decision


def validate_constraint(constraint):
    """Contract check (spec Q7): constraint ina id (versioned) na check(decision, context) callable.
    Gate inagusa surface mbili tu — id (kurekodi) na check (kuita). Chochote kingine ni opaque."""
    if not isinstance(constraint, dict):
        raise GateError("invalid_constraint: si mapping")
    missing = [f for f in CONSTRAINT_REQUIRED if f not in constraint]
    if missing:
        raise GateError(f"invalid_constraint: inakosa fields {missing}")
    if not callable(constraint["check"]):
        raise GateError("invalid_constraint: check si callable")
    return constraint


def gate(decision, constraints, context=None, gate_id=GATE_ID):
    """GATE NZIMA: validate → constraints (injected, AND/veto) → Decision Object MPYA (VALIDATED|REJECTED).
    Pure & deterministic (P71): inputs sawa → object ile ile (id sawa). Constraints ZOTE zinaendeshwa
    na ku-audited (Rule 6 — hakuna short-circuit ya Gate; short-circuit ni ndani ya constraint, Q4)."""
    validate_decision(decision)
    checks = []
    for c in constraints:
        validate_constraint(c)
        try:
            verdict, reason = c["check"](decision, context)
        except Exception as e:                                             # Gate haiokoi logic ya constraint (P97)
            raise GateError(f"constraint_failure: {c['id']} raised {type(e).__name__}: {e}")
        if verdict not in VERDICTS:
            raise GateError(f"invalid_verdict: {c['id']} -> {verdict!r}")
        checks.append({"constraint_id": c["id"], "verdict": verdict, "why": reason})
    failed = [ch["constraint_id"] for ch in checks if ch["verdict"] == "INELIGIBLE"]
    new_lifecycle = "REJECTED" if failed else "VALIDATED"                  # AND/veto: yoyote INELIGIBLE → REJECTED
    eligibility = {"gate_id": gate_id, "verdict": ("INELIGIBLE" if failed else "ELIGIBLE"),
                   "checks": checks, "failed": failed}
    return make_gate_decision(decision, new_lifecycle, gate_id, eligibility=eligibility)


# ---------------------------------------------------------------- self-tests (Rule 7)
def _fake_decision(lifecycle="PROPOSED", action="ABSTAIN", did="dec:test000001", as_of=0):
    """Decision Object bandia (minimal; mimic decision_object output) — hakuna import ya chain nzito."""
    return {"id": did, "action": action, "reason": "test", "reliability": 0.7, "risk": 0.3,
            "evidence_refs": ["snap:t1"], "policy_id": "policy:test@v1", "parent_decision_id": None,
            "parents": ["snap:t1"], "timestamp": as_of, "lifecycle": lifecycle,
            "integrity": {"is_abstention": action == "ABSTAIN"}, "audit": [f"make_decision(action={action})"]}


def _fake_constraint(cid="constraint:test@v1", verdict="ELIGIBLE", reason="ok", raises=False,
                     short_circuit_abstain=False):
    def check(decision, context):
        if raises:
            raise RuntimeError("boom")
        if short_circuit_abstain and decision.get("action") == "ABSTAIN":
            return "ELIGIBLE", "non-committing intent — pass-through (Q4)"
        return verdict, reason
    return {"id": cid, "check": check}


def self_test():
    ok_all = True

    # (1) Q8 structural validation — malformed / non-PROPOSED zinakataliwa (GateError, si REJECTED)
    try:
        gate({"id": "x"}, []); ok = False
    except GateError:
        ok = True
    try:
        gate(_fake_decision(lifecycle="VALIDATED"), []); ok2 = False       # PROPOSED pekee (D4)
    except GateError:
        ok2 = True
    try:
        gate(_fake_decision(action="NOTANACTION"), []); ok3 = False        # action nje ya enum (D2)
    except GateError:
        ok3 = True
    ok_all &= ok and ok2 and ok3
    print(f"[1] Q8 validation: bad-decision={ok} non-PROPOSED-blocked={ok2} bad-action={ok3} -> {'OK' if ok and ok2 and ok3 else 'FAIL'}")

    # (2) eligible path → VALIDATED object MPYA (id mpya + parent link + carry-over)
    d = _fake_decision()
    v = gate(d, [_fake_constraint(verdict="ELIGIBLE")])
    ok = (v["lifecycle"] == "VALIDATED" and v["id"] != d["id"]
          and v["parent_decision_id"] == d["id"] and v["gate_id"] == GATE_ID
          and v["action"] == d["action"] and v["policy_id"] == d["policy_id"]
          and v["evidence_refs"] == d["evidence_refs"]
          and v["eligibility"]["verdict"] == "ELIGIBLE" and v["eligibility"]["failed"] == [])
    ok_all &= ok
    print(f"[2] eligible→VALIDATED: new-id={v['id']!=d['id']} parent={v['parent_decision_id']==d['id']} carry-over={v['policy_id']==d['policy_id']} -> {'OK' if ok else 'FAIL'}")

    # (3) ineligible path → REJECTED object (SIO error); failed constraint imerekodiwa; id ≠ parent
    r = gate(d, [_fake_constraint(cid="constraint:risk@v1", verdict="ELIGIBLE"),
                 _fake_constraint(cid="constraint:budget@v1", verdict="INELIGIBLE", reason="budget exceeded")])
    ok = (r["lifecycle"] == "REJECTED" and r["id"] != d["id"]
          and r["parent_decision_id"] == d["id"]
          and r["eligibility"]["failed"] == ["constraint:budget@v1"]
          and len(r["eligibility"]["checks"]) == 2)                        # constraints ZOTE audited (Rule 6)
    ok_all &= ok
    print(f"[3] ineligible→REJECTED: lifecycle={r['lifecycle']} failed={r['eligibility']['failed']} all-audited={len(r['eligibility']['checks'])==2} -> {'OK' if ok else 'FAIL'}")

    # (4) GateError semantics: invalid_constraint · constraint_failure · invalid_verdict (system failures)
    try:
        gate(d, [{"id": "c"}]); e1 = False                                 # hakuna check
    except GateError:
        e1 = True
    try:
        gate(d, [_fake_constraint(raises=True)]); e2 = False               # check inarusha
    except GateError:
        e2 = True
    try:
        gate(d, [_fake_constraint(verdict="MAYBE")]); e3 = False           # verdict nje ya enum
    except GateError:
        e3 = True
    ok_all &= e1 and e2 and e3
    print(f"[4] GateError: invalid-constraint={e1} constraint-failure={e2} invalid-verdict={e3} -> {'OK' if e1 and e2 and e3 else 'FAIL'}")

    # (5) determinism + statelessness (Rule 5 / P71): same inputs → id ile ile; module haina mutable state;
    #     VALIDATED na REJECTED za parent MMOJA zina id TOFAUTI (Q2)
    v2 = gate(d, [_fake_constraint(verdict="ELIGIBLE")])
    import integrity_gate as _self
    muts = [k for k, val in vars(_self).items()
            if not k.startswith("__") and isinstance(val, (dict, list, set))]
    ok = v["id"] == v2["id"] and muts == [] and v["id"] != r["id"]
    ok_all &= ok
    print(f"[5] deterministic + stateless: id-stable={v['id']==v2['id']} module-mutables={muts} validated≠rejected={v['id']!=r['id']} -> {'OK' if ok else 'FAIL'}")

    # (6) Gate ignorance (Rule 4/P107 direct): sehemu ya GATE (kabla ya self-tests) — imports =
    #     decision_object + stdlib PEKEE; hakuna market-leak vocabulary (code ya market imepenya).
    #     P81 (FTMO SI hardcode) inathibitishwa na bad_imports==[]: FTMO ni constraint INJECTED —
    #     hakuna ftmo import/symbol inawezekana; FTMO inatajwa kwenye docstring (mafunzo) tu.
    import pathlib
    full = pathlib.Path(__file__).read_text(encoding="utf-8")
    gate_src = full.split("self-tests (Rule 7)")[0]                        # scan gate portion only
    imports = [ln.strip() for ln in gate_src.splitlines()
               if ln.strip().startswith(("import ", "from ")) and "integrity_gate" not in ln]
    allowed = ("from __future__", "import argparse", "from decision_object")
    bad_imports = [i for i in imports if not i.startswith(allowed)]
    # market-domain leak words (hazipo kwenye prose ya Gate — zingeonyesha code ya market imepenya)
    forbidden_words = ["market_" + "state", "event_" + "library", "representa" + "tion",
                       "configura" + "tion_engine", "pol" + "ars", "num" + "py",
                       "evidence_" + "set", "evidence_" + "snapshot", "evidence_" + "operations"]
    bad_words = [w for w in forbidden_words if w in gate_src.lower()]
    ftmo_imported = any("ft" + "mo" in i.lower() for i in imports)         # P81: hakuna ftmo import
    ok = bad_imports == [] and bad_words == [] and not ftmo_imported
    ok_all &= ok
    print(f"[6] gate ignorance (Rule 4) + P81 no-FTMO-import: bad-imports={bad_imports} market-leak={bad_words} ftmo-imported={ftmo_imported} -> {'OK' if ok else 'FAIL'}")

    # (7) constraint injection (Q4/Q7): empty constraints → VALIDATED (hakuna veto); short-circuit ya
    #     abstain → ELIGIBLE; swap constraint = swap outcome bila Gate kubadilika
    v_empty = gate(d, [])
    v_sc = gate(_fake_decision(action="ABSTAIN"), [_fake_constraint(verdict="INELIGIBLE", short_circuit_abstain=True)])
    r_commit = gate(_fake_decision(action="SELECT"), [_fake_constraint(verdict="INELIGIBLE", short_circuit_abstain=True)])
    ok = (v_empty["lifecycle"] == "VALIDATED"                              # empty = no veto
          and v_sc["lifecycle"] == "VALIDATED"                            # abstain short-circuited → ELIGIBLE (Q4)
          and r_commit["lifecycle"] == "REJECTED")                        # committing intent → constraint veto
    ok_all &= ok
    print(f"[7] injection: empty→{v_empty['lifecycle']} abstain-short-circuit→{v_sc['lifecycle']} commit→{r_commit['lifecycle']} -> {'OK' if ok else 'FAIL'}")

    print(f"\nSELF-TEST: {'PASS' if ok_all else 'FAIL'}")
    return 0 if ok_all else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    print("Gate haina standalone run — constraints/context ni injected (Execution Science). "
          "Tumia --self-test. Demo harness itakuja E4 (Broker Adapter).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
