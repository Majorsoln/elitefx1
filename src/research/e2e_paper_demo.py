"""
e2e_paper_demo.py — PIPELINE SMOKE TEST (paper-mode; Chief, kwa paper-validation ya Operator).

Inapitisha mnyororo MZIMA end-to-end kwa snapshot SYNTHETIC (HAKUNA data ya 26GB, HAKUNA network,
HAKUNA pesa) ili kuthibitisha kwamba vipande vyote vinaunganika:

  Evidence Snapshot → decision_engine.decide(+Policy) → Decision(PROPOSED)
     → integrity_gate.gate(+FTMO constraints) → Decision(VALIDATED|REJECTED)
     → broker_adapter.execute(paper) → Execution Object → decision_repository (E3)
     → broker_adapter.settle → Settlement record

Scenarios 3: (A) clean → FILLED+settled · (B) FTMO breach → Gate REJECTED (capital protected) ·
(C) weak evidence → ABSTAIN (hakuna trade). Mwisho: repository lineage + K6 queries.

Endesha:  python src/research/e2e_paper_demo.py --run
NB: hii ni SMOKE TEST ya wiring, SIO backtest/edge claim. Profitable ≠ Tradable Edge.
"""
from __future__ import annotations

import argparse
import os
import tempfile

from decision_engine import decide
from integrity_gate import gate
from broker_adapter import build_constraints, build_context, execute, settle, PaperBroker
import decision_repository as repo

VERSIONS = {"schema_version": "snapshot@v1", "doctrine_version": "V12"}
CFG = {"max_slots": 4, "max_correlated_slots": 2, "max_daily_loss": 500, "max_total_dd": 1000,
       "daily_budget_start": 400, "max_per_trade": 120,
       "correlation_groups": {"USD_group": ["EURUSD", "GBPUSD"], "EUR_group": ["EURUSD", "EURJPY"]},
       "max_spread": {"EURUSD": 1.5}}


def _snapshot(sid, state="READY", rel=0.95, conflict=0.0, as_of=0):
    return {"id": sid, "as_of": as_of, "readiness_state": state, "reliability": rel,
            "uncertainty": 0.2, "temporal_conflict": conflict,
            "structural_conflict": {"cross-pair": conflict}, "aggregate": {"support": 800}}


def _policy(action):
    return {"id": "policy:demo@v1", "decide": lambda s: (action, f"demo rule (state={s['readiness_state']})")}


def _trade(pair="EURUSD", as_of=0):
    return {"pair": pair, "side": "BUY", "sl_pips": 20, "pip_value": 0.1,
            "ref_price": 1.2000, "as_of": as_of, "sl": 1.1980, "tp": 1.2060}


def _acct(daily_loss=0, total_dd=0, open_slots=1):
    return {"daily_loss": daily_loss, "total_dd": total_dd, "open_slots": open_slots,
            "correlation_exposure": {}, "spread_by_pair": {"EURUSD": 0.8}}


def _dview(d):
    """Repo-view ya decision: repository inataka `as_of` (E3 contract); Decision Object ina `timestamp`."""
    v = dict(d)
    v["as_of"] = int(d["timestamp"])
    return v


def _p(s):
    print(s, flush=True)


def run():
    with tempfile.TemporaryDirectory() as tmp:
        log = os.path.join(tmp, "paper_runs.jsonl")
        constraints = build_constraints(CFG)
        _p("=" * 72)
        _p("ELITEFX PIPELINE SMOKE TEST (paper-mode; synthetic snapshot; HAKUNA pesa)")
        _p("=" * 72)

        # ---- SCENARIO A: clean evidence → trade FILLED + settled -----------------
        _p("\n[A] Clean READY snapshot, hakuna conflict, akaunti safi")
        snapA = _snapshot("snap:A", state="READY", rel=0.95, conflict=0.0, as_of=10)
        dA = decide(snapA, _policy("SELECT"))
        repo.append(log, "decision", _dview(dA), VERSIONS)
        _p(f"    engine.decide  → {dA['id']}  action={dA['action']} lifecycle={dA['lifecycle']}")
        ctxA = build_context(_acct(open_slots=1), "EURUSD", worst_case=40)
        gA = gate(dA, constraints, ctxA)
        repo.append(log, "decision", _dview(gA), VERSIONS)
        _p(f"    gate           → {gA['id']}  lifecycle={gA['lifecycle']} "
           f"verdict={gA['eligibility']['verdict']} (parent={gA['parent_decision_id']})")
        xA = execute(gA, _trade(as_of=12), CFG, _acct(open_slots=1), PaperBroker(slippage=0.0002),
                     repo_path=log, versions=VERSIONS)
        _p(f"    execute(paper) → {xA['id']}  status={xA['status']} qty={xA['filled_qty']} "
           f"intent={xA['intent']} (parent={xA['parent_decision_id']})")
        sA = settle(xA, realized_pnl=37.5, as_of=200, repo_path=log, versions=VERSIONS)
        _p(f"    settle         → {sA['id']}  pnl={sA['pnl']} (parent={sA['parent_execution_id']})")

        # ---- SCENARIO B: FTMO breach → Gate REJECTS (capital protected) ----------
        _p("\n[B] Same SELECT decision, LAKINI akaunti karibu na daily-loss limit (−460)")
        snapB = _snapshot("snap:B", state="READY", rel=0.95, conflict=0.0, as_of=20)
        dB = decide(snapB, _policy("SELECT"))
        repo.append(log, "decision", _dview(dB), VERSIONS)
        ctxB = build_context(_acct(daily_loss=460, open_slots=1), "EURUSD", worst_case=50)
        gB = gate(dB, constraints, ctxB)
        repo.append(log, "decision", _dview(gB), VERSIONS)
        _p(f"    gate           → lifecycle={gB['lifecycle']} verdict={gB['eligibility']['verdict']} "
           f"failed={gB['eligibility']['failed']}")
        try:
            execute(gB, _trade(as_of=22), CFG, _acct(daily_loss=460), PaperBroker())
            _p("    execute        → !! HITILAFU: order ilipita (haikupaswa)")
        except Exception as e:
            _p(f"    execute        → REFUSED ({type(e).__name__}): decision si VALIDATED → mtaji umelindwa ✓")

        # ---- SCENARIO C: weak evidence → policy ABSTAIN (hakuna trade) ------------
        _p("\n[C] Snapshot dhaifu (STALE) → policy ABSTAIN")
        snapC = _snapshot("snap:C", state="STALE", rel=0.55, conflict=0.0, as_of=30)
        dC = decide(snapC, _policy("ABSTAIN"))
        repo.append(log, "decision", _dview(dC), VERSIONS)
        _p(f"    engine.decide  → {dC['id']}  action={dC['action']} committing={dC['action'] in ('SELECT','ENTER','EXIT','REDUCE','HEDGE')}")
        _p("    (hakuna gate/execute — ABSTAIN si committing intent) ✓")

        # ---- REPOSITORY: lineage + K6 queries (training-data-ready) ---------------
        _p("\n" + "-" * 72)
        _p("REPOSITORY (E3) — rekodi za append-only, training-data-ready:")
        recs = repo.load(log)
        _p(f"    jumla ya records: {len(recs)}  "
           f"(decision {sum(r['kind']=='decision' for r in recs)} · "
           f"execution {sum(r['kind']=='execution' for r in recs)} · "
           f"settlement {sum(r['kind']=='settlement' for r in recs)})")
        ln = repo.lineage(log, xA["parent_decision_id"])
        _p(f"    lineage({xA['parent_decision_id']}): chain={len(ln['chain'])} "
           f"executions={len(ln['executions'])} gaps={ln['gaps']}")
        _p(f"    by_outcome('FILLED'): {len(repo.by_outcome(log, 'FILLED'))}  "
           f"by_time_window(0,250): {len(repo.by_time_window(log, 0, 250))}")
        integ = repo.integrity_check(log)
        _p(f"    integrity_check: records={integ['records']} duplicates={integ['duplicates']} "
           f"dangling={integ['dangling']} ok={integ['ok']}")

        kinds = [r["kind"] for r in recs]
        ok = (xA["status"] == "FILLED" and gB["lifecycle"] == "REJECTED"
              and dC["action"] == "ABSTAIN" and integ["ok"]
              and kinds.count("execution") == 1 and kinds.count("settlement") == 1
              and len(ln["chain"]) == 2 and ln["gaps"] == [])
        _p("\n" + "=" * 72)
        _p(f"SMOKE TEST: {'PASS ✓  — mnyororo mzima unatembea end-to-end' if ok else 'FAIL'}")
        _p("=" * 72)
        return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.run or a.self_test:
        return run()
    print("Tumia: python src/research/e2e_paper_demo.py --run")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
