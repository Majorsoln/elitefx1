"""
decision_engine.py — DECISION SCIENCE D6 (IMPLEMENTATION; Chief-approved architecture).

Engine = GENERIC ORCHESTRATOR tu: inapokea Evidence Snapshot + Decision Policy, inaita
policy.decide(snapshot), inafunga jibu kwenye Decision Object. HAKUNA decision logic hapa
(logic ni ya Policy — Rule 3).

Chief Implementation Rules (D6):
  Rule 3  Engine ndogo — logic yoyote ya maamuzi inahamia Policy.
  Rule 4  Engine haijui Market/Events/State/Representation/Features. Inajua TU:
          Snapshot · Policy · Decision Object. (Angalia imports: decision_object + stdlib PEKEE.)
  Rule 5  Stateless — no cache, no globals, no singleton, no memory.
  Rule 6  Correctness kwanza; hakuna optimization.
  Rule 7  Kila sehemu ina self-test (chini).

Doctrine zinazotekelezwa: P59/63 (evidence-only interface), P77/79/80 (input = Snapshot pekee),
P83 (Decision Object immutable), P84 (reference exact snapshot id), P88 (reference policy id),
P71 (pure/deterministic).

Self-test: python src/research/decision_engine.py --self-test
"""
from __future__ import annotations

import argparse

from decision_object import make_decision

# Contract fields (P80: snapshot ndiyo context YOTE; hizi ndizo engine inazitegemea)
SNAPSHOT_REQUIRED = ("id", "as_of", "readiness_state", "reliability", "uncertainty",
                     "temporal_conflict", "structural_conflict", "aggregate")
POLICY_REQUIRED = ("id", "decide")


class ContractError(ValueError):
    """Input haitimizi contract ya Engine (snapshot/policy batili)."""


def validate_snapshot(snapshot):
    """Contract check (P80/P84): snapshot lazima iwe na fields zote za context."""
    if not isinstance(snapshot, dict):
        raise ContractError("snapshot si mapping")
    missing = [f for f in SNAPSHOT_REQUIRED if f not in snapshot]
    if missing:
        raise ContractError(f"snapshot inakosa fields: {missing}")
    return snapshot


def validate_policy(policy):
    """Contract check (P88): policy lazima iwe na id (versioned) na decide(snapshot)."""
    if not isinstance(policy, dict):
        raise ContractError("policy si mapping")
    missing = [f for f in POLICY_REQUIRED if f not in policy]
    if missing:
        raise ContractError(f"policy inakosa fields: {missing}")
    if not callable(policy["decide"]):
        raise ContractError("policy.decide si callable")
    return policy


def decide(snapshot, policy):
    """ENGINE NZIMA: validate → policy.decide(snapshot) → Decision Object (P83/84/88).
    Pure & deterministic (P71): inputs sawa → Decision Object ile ile (id sawa)."""
    validate_snapshot(snapshot)
    validate_policy(policy)
    action, reason = policy["decide"](snapshot)
    return make_decision(snapshot, action=action,
                         reason=f"[{policy['id']}] {reason}", policy_id=policy["id"])


def decide_batch(snapshots, policy):
    """Batch = map ya decide (stateless; order haiathiri decision yoyote binafsi)."""
    return [decide(s, policy) for s in snapshots]


# ---------------------------------------------------------------- self-tests (Rule 7)
def _fake_snapshot(state="READY", rel=0.9, sid="snap:t1"):
    return {"id": sid, "as_of": 0, "readiness_state": state, "reliability": rel,
            "uncertainty": 0.3, "temporal_conflict": 0.0,
            "structural_conflict": {"cross-pair": 0.0}, "aggregate": {"support": 500}}


def _fake_policy(pid="policy:test@v1", action="ABSTAIN"):
    return {"id": pid, "decide": lambda s: (action, f"test rule (state={s['readiness_state']})")}


def self_test():
    ok_all = True

    # (1) contract validation — malformed inputs zinakataliwa
    try:
        decide({"id": "x"}, _fake_policy()); ok = False
    except ContractError:
        ok = True
    try:
        decide(_fake_snapshot(), {"id": "p"}); ok2 = False
    except ContractError:
        ok2 = True
    ok_all &= ok and ok2
    print(f"[1] contract validation: bad-snapshot-blocked={ok} bad-policy-blocked={ok2} -> {'OK' if ok and ok2 else 'FAIL'}")

    # (2) decide → Decision Object yenye snapshot_id (P84) + policy_id (P88)
    d = decide(_fake_snapshot(), _fake_policy())
    ok = list(d["evidence_refs"]) == ["snap:t1"] and d["policy_id"] == "policy:test@v1" and d["lifecycle"] == "PROPOSED"  # A-4: refs=tuple
    ok_all &= ok
    print(f"[2] refs: snapshot={d['evidence_refs']} policy={d['policy_id']} -> {'OK' if ok else 'FAIL'}")

    # (3) determinism + statelessness (Rule 5 / P71): calls zinazofanana → id ile ile;
    #     module haina mutable state (hakuna dict/list/set kwenye namespace ya module)
    d2 = decide(_fake_snapshot(), _fake_policy())
    import decision_engine as _self
    muts = [k for k, v in vars(_self).items()
            if not k.startswith("__") and isinstance(v, (dict, list, set))]
    ok = d["id"] == d2["id"] and muts == []
    ok_all &= ok
    print(f"[3] deterministic + stateless: id-stable={d['id']==d2['id']} module-mutables={muts} -> {'OK' if ok else 'FAIL'}")

    # (4) engine ignorance (Rule 4): sehemu ya ENGINE (kabla ya self-tests) — imports ni
    #     decision_object + stdlib PEKEE; hakuna msamiati wa market
    import pathlib
    full = pathlib.Path(__file__).read_text(encoding="utf-8")
    engine_src = full.split("self-tests (Rule 7)")[0]          # scan engine portion only
    imports = [ln.strip() for ln in engine_src.splitlines()
               if ln.strip().startswith(("import ", "from ")) and "decision_engine" not in ln]
    allowed = ("from __future__", "import argparse", "from decision_object")
    bad_imports = [i for i in imports if not i.startswith(allowed)]
    forbidden_words = ["market_" + "state", "event_" + "library", "representa" + "tion",
                       "evidence_" + "operations", "evidence_" + "set", "evidence_" + "snapshot",
                       "pol" + "ars", "num" + "py"]
    bad_words = [w for w in forbidden_words if w in engine_src]
    ok = bad_imports == [] and bad_words == []
    ok_all &= ok
    print(f"[4] engine ignorance: bad-imports={bad_imports} forbidden-words={bad_words} -> {'OK' if ok else 'FAIL'}")

    # (5) batch = map ya single; policy inabadilishwa bila engine kubadilika (injection)
    snaps = [_fake_snapshot(sid=f"snap:t{i}") for i in range(3)]
    batch = decide_batch(snaps, _fake_policy())
    singles = [decide(s, _fake_policy()) for s in snaps]
    swap = decide(_fake_snapshot(), _fake_policy(pid="policy:other@v2", action="WAIT"))
    ok = ([b["id"] for b in batch] == [s["id"] for s in singles]
          and swap["action"] == "WAIT" and swap["policy_id"] == "policy:other@v2")
    ok_all &= ok
    print(f"[5] batch==map + policy-injection: batch-match={[b['id'] for b in batch]==[s['id'] for s in singles]} swap-action={swap['action']} -> {'OK' if ok else 'FAIL'}")

    print(f"\nSELF-TEST: {'PASS' if ok_all else 'FAIL'}")
    return 0 if ok_all else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    print("Engine haina standalone run — tumia decision_engine_report.py (demo harness).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
