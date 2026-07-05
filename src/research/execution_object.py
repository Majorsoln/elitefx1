"""
execution_object.py — EXECUTION SCIENCE E2 (IMPLEMENTATION; Chief-approved spec + rulings Q1-Q5).

EXECUTION ≠ DECISION. Decision Object (D4/E1) inarekodi *kilichoamuliwa* (INTENT) + structural
integrity; **Execution Object (E2)** inarekodi *KILICHOTOKEA* sokoni — fills/slippage/rejects/partial
(OUTCOME, P87/P89). Execution ni **object immutable TOFAUTI** na Decision (P89), wa nne (ndugu wa
Evidence/Decision/Execution/Lesson).

Vipande viwili (spec E2):
  1. EXECUTION OBJECT   — data structure ya outcome (immutable; A-4 frozen).
  2. EXECUTION RECORDER — `record(decision, report)`: Decision(VALIDATED) + ExecutionReport(injected)
                          → Execution Object MPYA (parent_decision_id → VALIDATED; mirror E1 crossing).

Chief rulings (2026-07-05, E2 spec APPROVED):
  Q1  Decision domain inaishia VALIDATED; execution-outcome = Execution Object (SIO Decision lifecycle).
  Q2  status = FILLED · PARTIAL · REJECTED · UNFILLED (SETTLED inadefer E3).
  Q3  Recorder inakataa non-committing intents; committing = ENTER · EXIT · REDUCE · HEDGE.
  Q4  A-4 deep-freeze() (stdlib) kwa objects zote za domain (frozen.py).
  Q5  sizing/qty/side/ref_price zinakuja na **ExecutionReport** (E4 path), SIO Decision (INTENT tu).

Rules (E2): Rule 3 (Recorder ndogo — hakuna decision/broker logic) · Rule 4 (imports = frozen +
stdlib PEKEE; **hakuna decision_object/market/broker** → transitively PURE) · Rule 5 (stateless) ·
Rule 6 (correctness) · Rule 7 (self-test). Doctrine: P89/P87 (Execution ≠ Decision; outcome),
P85 (append-only, parent link), P81 (broker/FTMO = E4, injected report), A-4 (frozen).

NB (enum): committing set inajumuisha **SELECT** = jina la sasa la D4 enum kwa "ENTER" (D6 SELECT→ENTER
migration bado OPEN). Non-committing (WAIT/ABSTAIN/DIVERSIFY/SUSPEND) zinakataliwa (Q3).

Self-test: python src/research/execution_object.py --self-test
"""
from __future__ import annotations

import argparse
import hashlib
from collections.abc import Mapping

from frozen import freeze                                     # A-4 (E2 Q4) — stdlib-pure

RECORDER_ID = "recorder:execution@v1"                         # P88 pattern — reproducibility
# Execution outcome status (Chief Q2). SETTLED inadefer E3.
STATUS = ("FILLED", "PARTIAL", "REJECTED", "UNFILLED")
SIDES = ("BUY", "SELL")
# Committing intents (Chief Q3): ENTER·EXIT·REDUCE·HEDGE. SELECT = current-enum alias ya ENTER
# (D6 migration OPEN). WAIT/ABSTAIN/DIVERSIFY/SUSPEND = non-committing → hazitekelezwi.
COMMITTING_INTENTS = ("ENTER", "SELECT", "EXIT", "REDUCE", "HEDGE")
DECISION_REQUIRED = ("id", "action", "evidence_refs", "policy_id", "lifecycle", "audit", "timestamp")
REPORT_REQUIRED = ("status", "intended", "fills", "as_of")
INTENDED_REQUIRED = ("side", "qty", "ref_price")


class ExecutionError(ValueError):
    """Input haitimizi contract ya Recorder (SYSTEM failure — SIO outcome). Mirror ya Engine/GateError:
    REJECTED/UNFILLED ni OUTCOME halali (fact ya soko); input batili ni error."""


def _execution_id(decision_id, status, filled_qty, as_of):
    """id ya Execution Object (mirror _gate_decision_id): parent + outcome → id ya kipekee."""
    return "exec:" + hashlib.sha1(
        f"{decision_id}|{status}|{filled_qty}|{int(as_of)}".encode()).hexdigest()[:10]


def validate_decision(decision):
    """Q8/V1-V3 (structural PEKEE): NI Decision Object, lifecycle==VALIDATED, action ni committing.
    Recorder HAIrevalidate snapshot/eligibility (Engine+Gate zilifanya); haisomi values kwa maana."""
    if not isinstance(decision, Mapping):
        raise ExecutionError("invalid_decision: si mapping")
    missing = [f for f in DECISION_REQUIRED if f not in decision]
    if missing:
        raise ExecutionError(f"invalid_decision: inakosa fields {missing}")
    if decision["lifecycle"] != "VALIDATED":                             # V2 — VALIDATED pekee (Q1/E1)
        raise ExecutionError(f"invalid_lifecycle: {decision['lifecycle']} (VALIDATED pekee)")
    if decision["action"] not in COMMITTING_INTENTS:                     # V3 (Q3) — non-committing hazitekelezwi
        raise ExecutionError(f"invalid_decision: action {decision['action']!r} si committing intent")
    return decision


def validate_report(report):
    """Contract ya ExecutionReport (injected; broker=E4). Structural + consistency (R1-R3)."""
    if not isinstance(report, Mapping):
        raise ExecutionError("invalid_report: si mapping")
    missing = [f for f in REPORT_REQUIRED if f not in report]
    if missing:
        raise ExecutionError(f"invalid_report: inakosa fields {missing}")
    if report["status"] not in STATUS:                                   # R1
        raise ExecutionError(f"invalid_report: status {report['status']!r} nje ya enum")
    intended = report["intended"]
    if not isinstance(intended, Mapping) or any(f not in intended for f in INTENDED_REQUIRED):
        raise ExecutionError("invalid_report: intended inakosa {side,qty,ref_price}")
    if intended["side"] not in SIDES or intended["qty"] <= 0 or intended["ref_price"] < 0:
        raise ExecutionError("invalid_report: intended batili (side/qty/ref_price)")
    if not isinstance(report["fills"], (list, tuple)):                   # R2
        raise ExecutionError("invalid_report: fills si orodha")
    for f in report["fills"]:
        if not isinstance(f, Mapping) or any(k not in f for k in ("qty", "price", "ts")):
            raise ExecutionError("invalid_report: fill inakosa {qty,price,ts}")
        if f["qty"] < 0 or f["price"] < 0:
            raise ExecutionError("inconsistent_report: fill qty/price hasi")
    return report


def record(decision, report, recorder_id=RECORDER_ID):
    """RECORDER NZIMA: validate → derive outcome → Execution Object MPYA immutable (P89, A-4 frozen).
    Pure & deterministic (P71). REJECTED/UNFILLED = outcome (SIO error). Recorder haiamui side/qty
    (zinatoka report — Q5); haihesabu edge (slippage = avg−ref, ni fact iliyorekodiwa, si tathmini)."""
    validate_decision(decision)
    validate_report(report)
    intended = report["intended"]
    intended_qty = intended["qty"]
    fills = list(report["fills"])
    filled_qty = sum(f["qty"] for f in fills)
    if filled_qty > intended_qty:                                       # R3 consistency
        raise ExecutionError(f"inconsistent_report: filled {filled_qty} > intended {intended_qty}")
    reject_reason = report.get("reject_reason")
    # derive canonical status kutoka facts (Q4) — cross-check na report.status (R3)
    if filled_qty == 0 and reject_reason:
        derived = "REJECTED"
    elif filled_qty == 0:
        derived = "UNFILLED"
    elif filled_qty < intended_qty:
        derived = "PARTIAL"
    else:
        derived = "FILLED"
    if report["status"] != derived:
        raise ExecutionError(f"inconsistent_report: status {report['status']} vs facts {derived}")
    avg_fill_price = (sum(f["qty"] * f["price"] for f in fills) / filled_qty) if filled_qty else None
    slippage = (avg_fill_price - intended["ref_price"]) if avg_fill_price is not None else None
    audit = list(decision["audit"]) + [
        f"record({recorder_id}): decision={decision['id']} status={derived} filled={filled_qty}"]
    if derived == "REJECTED":
        audit.append(f"reject({recorder_id}): {reject_reason}")
    execution = {
        "id": _execution_id(decision["id"], derived, filled_qty, report["as_of"]),
        "parent_decision_id": decision["id"],                           # P85 (mirror E1) — Execution → Decision(VALIDATED)
        "recorder_id": recorder_id,                                     # P88 reproducibility
        "intent": decision["action"],                                  # INTENT kutoka decision (Q5: Decision = intent tu)
        "status": derived,                                             # Q2 outcome
        "intended": {"side": intended["side"], "qty": intended_qty, "ref_price": intended["ref_price"]},
        "fills": [{"qty": f["qty"], "price": f["price"], "ts": f["ts"]} for f in fills],
        "filled_qty": filled_qty,
        "remaining_qty": intended_qty - filled_qty,
        "avg_fill_price": avg_fill_price,
        "slippage": slippage,                                          # fact iliyorekodiwa (SIO tathmini)
        "reject_reason": reject_reason,
        "report_ref": report.get("report_ref"),                       # broker/venue ref (E4)
        "timestamp": int(report["as_of"]),
        "audit": audit,
    }
    return freeze(execution)                                            # A-4 (E2 Q4)


# ---------------------------------------------------------------- self-tests (Rule 7)
def _fake_decision(lifecycle="VALIDATED", action="ENTER", did="dec:val00001", as_of=0):
    """Decision Object bandia (VALIDATED) — plain dict; HAKUNA import ya decision_object (purity)."""
    return {"id": did, "action": action, "reason": "test", "evidence_refs": ("snap:t1",),
            "policy_id": "policy:test@v1", "parent_decision_id": "dec:prop00001",
            "gate_id": "gate:integrity@v1", "lifecycle": lifecycle, "timestamp": as_of,
            "audit": ["make_decision(...)", "gate(...): PROPOSED→VALIDATED"]}


def _report(status, fills, side="BUY", qty=100, ref_price=1.2000, reject_reason=None, as_of=0):
    r = {"status": status, "intended": {"side": side, "qty": qty, "ref_price": ref_price},
         "fills": fills, "as_of": as_of}
    if reject_reason is not None:
        r["reject_reason"] = reject_reason
    return r


def self_test():
    ok_all = True

    # (1) validation: bad decision · non-VALIDATED · non-committing intent → ExecutionError
    try:
        record({"id": "x"}, _report("UNFILLED", [])); e1 = False
    except ExecutionError:
        e1 = True
    try:
        record(_fake_decision(lifecycle="PROPOSED"), _report("UNFILLED", [])); e2 = False
    except ExecutionError:
        e2 = True
    try:
        record(_fake_decision(action="ABSTAIN"), _report("UNFILLED", [])); e3 = False   # Q3
    except ExecutionError:
        e3 = True
    ok_all &= e1 and e2 and e3
    print(f"[1] validation: bad-decision={e1} non-VALIDATED={e2} non-committing={e3} -> {'OK' if e1 and e2 and e3 else 'FAIL'}")

    # (2) FILLED: fills == intended → status FILLED; slippage; parent link; intent carried
    d = _fake_decision(action="ENTER")
    x = record(d, _report("FILLED", [{"qty": 60, "price": 1.2002, "ts": 1}, {"qty": 40, "price": 1.2007, "ts": 2}]))
    avg = (60 * 1.2002 + 40 * 1.2007) / 100
    ok = (x["status"] == "FILLED" and x["filled_qty"] == 100 and x["remaining_qty"] == 0
          and abs(x["avg_fill_price"] - avg) < 1e-9 and abs(x["slippage"] - (avg - 1.2000)) < 1e-9
          and x["parent_decision_id"] == d["id"] and x["intent"] == "ENTER"
          and x["id"].startswith("exec:") and x["recorder_id"] == RECORDER_ID)
    ok_all &= ok
    print(f"[2] FILLED: status={x['status']} filled={x['filled_qty']} slippage={x['slippage']:.5f} parent={x['parent_decision_id']==d['id']} -> {'OK' if ok else 'FAIL'}")

    # (3) PARTIAL: filled < intended → status PARTIAL; remaining > 0
    p = record(d, _report("PARTIAL", [{"qty": 30, "price": 1.2003, "ts": 1}]))
    ok = p["status"] == "PARTIAL" and p["filled_qty"] == 30 and p["remaining_qty"] == 70 and p["slippage"] is not None
    ok_all &= ok
    print(f"[3] PARTIAL: status={p['status']} filled={p['filled_qty']} remaining={p['remaining_qty']} -> {'OK' if ok else 'FAIL'}")

    # (4) REJECTED / UNFILLED = OUTCOME (SIO error)
    rj = record(d, _report("REJECTED", [], reject_reason="broker: max exposure"))
    uf = record(d, _report("UNFILLED", []))
    ok = (rj["status"] == "REJECTED" and rj["reject_reason"] == "broker: max exposure"
          and rj["avg_fill_price"] is None and rj["slippage"] is None
          and uf["status"] == "UNFILLED" and uf["filled_qty"] == 0)
    ok_all &= ok
    print(f"[4] REJECTED/UNFILLED (outcome≠error): rejected={rj['status']} reason-logged={rj['reject_reason'] is not None} unfilled={uf['status']} -> {'OK' if ok else 'FAIL'}")

    # (5) ExecutionError: invalid_report (status nje enum) · inconsistent (filled>intended) · (status vs facts)
    try:
        record(d, _report("MAYBE", [])); s1 = False
    except ExecutionError:
        s1 = True
    try:
        record(d, _report("FILLED", [{"qty": 150, "price": 1.2, "ts": 1}])); s2 = False   # 150 > 100
    except ExecutionError:
        s2 = True
    try:
        record(d, _report("FILLED", [{"qty": 30, "price": 1.2, "ts": 1}])); s3 = False     # status FILLED lakini facts PARTIAL
    except ExecutionError:
        s3 = True
    ok_all &= s1 and s2 and s3
    print(f"[5] ExecutionError: bad-status={s1} filled>intended={s2} status-vs-facts={s3} -> {'OK' if s1 and s2 and s3 else 'FAIL'}")

    # (6) determinism + stateless + A-4 frozen
    x2 = record(d, _report("FILLED", [{"qty": 100, "price": 1.2005, "ts": 1}]))
    x3 = record(d, _report("FILLED", [{"qty": 100, "price": 1.2005, "ts": 1}]))
    import execution_object as _self
    muts = [k for k, v in vars(_self).items()
            if not k.startswith("__") and isinstance(v, (dict, list, set))]
    frozen_ok = True
    try:
        x2["status"] = "PARTIAL"; frozen_ok = False                                        # top-level → TypeError
    except TypeError:
        pass
    try:
        x2["intended"]["qty"] = 1; frozen_ok = False                                       # nested → TypeError
    except TypeError:
        pass
    ok = x2["id"] == x3["id"] and muts == [] and frozen_ok and isinstance(x2["fills"], tuple)
    ok_all &= ok
    print(f"[6] deterministic + stateless + A-4: id-stable={x2['id']==x3['id']} mutables={muts} frozen={frozen_ok} -> {'OK' if ok else 'FAIL'}")

    # (7) Rule 4 purity: imports = frozen + stdlib PEKEE; hakuna decision_object/market/broker → transitively PURE
    import pathlib
    full = pathlib.Path(__file__).read_text(encoding="utf-8")
    src = full.split("self-tests (Rule 7)")[0]
    imports = [ln.strip() for ln in src.splitlines()
               if ln.strip().startswith(("import ", "from ")) and "execution_object" not in ln]
    allowed = ("from __future__", "import argparse", "import hashlib", "from collections", "from frozen")
    bad_imports = [i for i in imports if not i.startswith(allowed)]
    # transitively PURE: hakuna IMPORT ya decision_object/market/broker (frozen ni stdlib-pure).
    # Scan ni kwenye import-lines PEKEE (SIO prose — docstring inataja broker/FTMO=E4 kimafunzo).
    leak = ["decision_" + "object", "market_", "event_", "bro" + "ker", "ft" + "mo", "pol" + "ars", "num" + "py"]
    leak_imports = [i for i in imports if any(w in i.lower() for w in leak)]
    ok = bad_imports == [] and leak_imports == []
    ok_all &= ok
    print(f"[7] Rule 4 purity (transitively pure): bad-imports={bad_imports} leak-imports={leak_imports} -> {'OK' if ok else 'FAIL'}")

    print(f"\nSELF-TEST: {'PASS' if ok_all else 'FAIL'}")
    return 0 if ok_all else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    print("Execution Recorder haina standalone run — report ni injected (broker=E4). Tumia --self-test.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
