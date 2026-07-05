"""
decision_repository.py — EXECUTION SCIENCE E3 (P106; Chief-approved spec + rulings Q1-Q5).

Decision Repository = persistence + query NJE ya Engine (P106). Append-only (P85); records
immutable; refs kamili → training-data-ready (E3↔K6). Rulings: JSONL core (stdlib-pure — P107);
lenient ingest + lineage() inaonyesha gaps; versions vector (P95) kila record; queries za msingi
+ by-outcome + by-time-window (mahitaji ya K6). Schema completeness > query completeness.

Backend: JSONL (file path injected). DuckDB adapter = nje ya module hii (haipo bado).
Self-test: python src/research/decision_repository.py --self-test  (stdlib pekee, tmp file)
"""
from __future__ import annotations

import argparse
import json
import os
import tempfile

REPO_ID = "repository:decision@v1"
KINDS = ("decision", "execution", "settlement")           # E4/Q4: settlement = kind mpya (object wa tano)
REQUIRED = {"decision": ("id", "as_of", "lifecycle"),
            "execution": ("id", "as_of", "status"),
            "settlement": ("id", "as_of", "parent_execution_id", "pnl")}


class RepositoryError(ValueError):
    """Append/query request batili (structural — si outcome)."""


def _plain(obj):
    """Frozen mappings/tuples → plain dict/list kwa JSON (deep)."""
    if hasattr(obj, "items"):
        return {k: _plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_plain(v) for v in obj]
    return obj


def append(path, kind, obj, versions):
    """Append record moja (lenient: hakuna dangling-ref check — integrity_check ni tofauti).
    versions = {"schema_version": .., "doctrine_version": ..} (P95 — LAZIMA)."""
    if kind not in KINDS:
        raise RepositoryError(f"kind batili: {kind}")
    missing = [f for f in REQUIRED[kind] if f not in obj]
    if missing:
        raise RepositoryError(f"{kind} inakosa fields: {missing}")
    if not isinstance(versions, dict) or not {"schema_version", "doctrine_version"} <= set(versions):
        raise RepositoryError("versions vector (P95) inakosa schema_version/doctrine_version")
    rec = {"repo_id": REPO_ID, "kind": kind, "versions": dict(versions), "obj": _plain(obj)}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    return rec


def load(path):
    """Records zote kwa order ya kuandikwa (append-only log)."""
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def _oid(r):
    return r["obj"]["id"]


def lineage(path, decision_id):
    """Chain kamili ya decision: parents (kupitia parent_decision_id) + executions zake.
    Gaps (parent isiyopo kwenye log) zinaonyeshwa — hazivunji (lenient/ruling Q3)."""
    recs = {(_oid(r)): r for r in load(path)}
    chain, gaps, cur = [], [], decision_id
    while cur:
        r = recs.get(cur)
        if r is None:
            gaps.append(cur)
            break
        chain.append(r)
        cur = r["obj"].get("parent_decision_id")
    execs = [r for r in recs.values() if r["kind"] == "execution"
             and r["obj"].get("parent_decision_id") == decision_id]
    return {"decision_id": decision_id, "chain": chain, "executions": execs, "gaps": gaps}


def by_snapshot(path, snapshot_id):
    return [r for r in load(path) if snapshot_id in tuple(r["obj"].get("evidence_refs", ()))]


def by_policy(path, policy_id):
    return [r for r in load(path) if r["obj"].get("policy_id") == policy_id]


def by_outcome(path, status):
    """K6 query 1: execution records kwa outcome (FILLED/PARTIAL/REJECTED/UNFILLED)."""
    return [r for r in load(path) if r["kind"] == "execution" and r["obj"].get("status") == status]


def by_time_window(path, start, end):
    """K6 query 2: records zote zenye start <= as_of <= end."""
    return [r for r in load(path) if start <= r["obj"].get("as_of", start - 1) <= end]


def integrity_check(path):
    """Query tofauti (ruling Q3): duplicate ids + dangling parent refs."""
    recs = load(path)
    ids, dups, dangling = set(), [], []
    for r in recs:
        oid = _oid(r)
        if oid in ids:
            dups.append(oid)
        ids.add(oid)
    for r in recs:
        for ref in ("parent_decision_id", "parent_execution_id"):   # E4: settlement→execution pia
            p = r["obj"].get(ref)
            if p and p not in ids:
                dangling.append((_oid(r), p))
    return {"records": len(recs), "duplicates": dups, "dangling": dangling,
            "ok": not dups and not dangling}


# ---------------------------------------------------------------- self-tests
def _v():
    return {"schema_version": "snapshot@v1", "doctrine_version": "V12"}


def self_test():
    ok_all = True
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "log.jsonl")
        d1 = {"id": "dec:1", "as_of": 10, "lifecycle": "PROPOSED",
              "evidence_refs": ["snap:a"], "policy_id": "policy:x@v2"}
        d2 = {"id": "dec:2", "as_of": 11, "lifecycle": "VALIDATED",
              "parent_decision_id": "dec:1", "evidence_refs": ["snap:a"], "policy_id": "policy:x@v2"}
        e1 = {"id": "exe:1", "as_of": 12, "status": "FILLED", "parent_decision_id": "dec:2"}
        for k, o in (("decision", d1), ("decision", d2), ("execution", e1)):
            append(p, k, o, _v())
        # [1] append-only + load order
        ok = [_oid(r) for r in load(p)] == ["dec:1", "dec:2", "exe:1"]
        ok_all &= ok
        print(f"[1] append-only order -> {'OK' if ok else 'FAIL'}")
        # [2] contract: kind/fields/versions zinakataliwa
        bad = 0
        for args in (( "trade", d1, _v()), ("decision", {"id": "x"}, _v()), ("decision", d1, {})):
            try:
                append(p, *args); bad += 1
            except RepositoryError:
                pass
        ok = bad == 0
        ok_all &= ok
        print(f"[2] contract rejects -> {'OK' if ok else 'FAIL'}")
        # [3] lineage: chain 2 + execution 1 + hakuna gap
        ln = lineage(p, "dec:2")
        ok = len(ln["chain"]) == 2 and len(ln["executions"]) == 1 and ln["gaps"] == []
        ok_all &= ok
        print(f"[3] lineage chain/exec/gaps -> {'OK' if ok else 'FAIL'}")
        # [4] lenient ingest: dangling parent inakubaliwa; lineage + integrity zinaiona
        append(p, "decision", {"id": "dec:9", "as_of": 20, "lifecycle": "VALIDATED",
                               "parent_decision_id": "dec:missing"}, _v())
        ok = lineage(p, "dec:9")["gaps"] == ["dec:missing"] and not integrity_check(p)["ok"]
        ok_all &= ok
        print(f"[4] lenient + integrity_check -> {'OK' if ok else 'FAIL'}")
        # [5] queries: snapshot/policy/outcome/time-window
        ok = (len(by_snapshot(p, "snap:a")) == 2 and len(by_policy(p, "policy:x@v2")) == 2
              and len(by_outcome(p, "FILLED")) == 1 and len(by_time_window(p, 11, 12)) == 2)
        ok_all &= ok
        print(f"[5] queries (snapshot/policy/outcome/window) -> {'OK' if ok else 'FAIL'}")
        # [5b] E4/Q4: kind=settlement — append + store + parent_execution_id dangling detection
        # (settlement iko kwenye log p ile ile ambayo ina exe:1; parent exe:1 ipo → si dangling)
        append(p, "settlement", {"id": "settle:1", "as_of": 30, "parent_execution_id": "exe:1", "pnl": 42.5}, _v())
        append(p, "settlement", {"id": "settle:2", "as_of": 31, "parent_execution_id": "exe:missing", "pnl": -5}, _v())
        dangling = dict(integrity_check(p)["dangling"])
        recs2 = load(p)
        ok = (sum(1 for r in recs2 if r["kind"] == "settlement") == 2
              and dangling.get("settle:2") == "exe:missing"             # dangling settlement detected (lenient)
              and "settle:1" not in dangling)                           # parent exe:1 ipo → si dangling
        ok_all &= ok
        print(f"[5b] settlement kind + parent_execution_id integrity -> {'OK' if ok else 'FAIL'}")
        # [6] P107: module hii imports = stdlib pekee
        import pathlib
        src = pathlib.Path(__file__).read_text(encoding="utf-8")
        imps = [l.strip() for l in src.splitlines() if l.strip().startswith(("import ", "from "))]
        allowed = ("from __future__", "import argparse", "import json", "import os",
                   "import tempfile", "import pathlib")
        bad_imports = [i for i in imps if not i.startswith(allowed)]
        ok = bad_imports == []
        ok_all &= ok
        print(f"[6] stdlib-pure imports: bad={bad_imports} -> {'OK' if ok else 'FAIL'}")
    print(f"\nSELF-TEST: {'PASS' if ok_all else 'FAIL'}")
    return 0 if ok_all else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    if ap.parse_args().self_test:
        return self_test()
    print("Repository haina standalone run — inaitwa na caller (P106).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
