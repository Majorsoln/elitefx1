"""
real_data_paper_run.py — REAL-DATA VALIDATION (paper; harness — IMPURE by design).

Tofauti na `e2e_paper_demo.py` (synthetic), hii inajenga **Evidence Snapshots kutoka data HALISI**
(states za ticks zako, kupitia `build_tagged_evidence` — njia ileile iliyotumika kwenye reports zote)
kisha inazipitisha kwenye mnyororo wa maamuzi:

  ticks/states (26GB) → build_tagged_evidence → Evidence Snapshot (kwa kila event)
     → decision_engine.decide(+Policy) → Decision(PROPOSED)
     → integrity_gate.gate(+FTMO constraints kutoka ftmo_config) → VALIDATED|REJECTED
     → decision_repository (E3) — rekodi halisi zenye provenance decision→snapshot

MUHIMU (uaminifu wa Chief): mfumo utaABSTAIN mara nyingi — hiyo ndiyo TABIA SAHIHI (doctrine:
value halisi ni hasi → protect capital, P26). Hii inathibitisha **MASHINE inafanya kazi na evidence
halisi**, SIO kwamba ina faida. *Profitable ≠ Tradable Edge.*

Harness hii ni IMPURE kwa makusudi (inajenga evidence kutoka market stack) — kama
decision_engine_report.py; core ya pipeline (Engine/Gate/Repo) inabaki PURE (purity_check.py).

Endesha (PC ya Operator, baada ya states kujengwa):
  python src/research/real_data_paper_run.py --policy conservative
"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile
from collections import Counter, defaultdict

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# Harness imports (market stack — inahitaji data; IMPURE kwa makusudi)
from evidence_operations import build_tagged_evidence
from evidence_set import make_set
from evidence_snapshot import make_snapshot
# Pure pipeline (core)
from decision_policy import POLICIES
from decision_engine import decide
from integrity_gate import gate
from broker_adapter import build_constraints, build_context
import decision_repository as repo

VERSIONS = {"schema_version": "snapshot@v1", "doctrine_version": "V12"}


def _dview(d):
    v = dict(d); v["as_of"] = int(d["timestamp"]); return v


def _fresh_account():
    """Akaunti safi ya paper (mwanzo wa siku; hakuna exposure)."""
    return {"daily_loss": 0, "total_dd": 0, "open_slots": 0,
            "correlation_exposure": {}, "spread_by_pair": {}}


def _load_ftmo():
    """Soma FTMO constraints kutoka config/ftmo_config.yaml (values za Operator)."""
    try:
        import yaml
        path = os.path.join(os.path.dirname(__file__), "..", "..", "config", "ftmo_config.yaml")
        return yaml.safe_load(open(path, encoding="utf-8"))
    except Exception:
        return {}


def run(policy_name, pairs, log):
    print(f"Building Evidence Snapshots kutoka data HALISI (pairs={len(pairs)})...", flush=True)
    tagged, no_px = build_tagged_evidence(pairs)
    if no_px:
        print("HITILAFU: state parquet haina OHLC. Endesha market_state_engine.py kwanza "
              "(jenga states kutoka ticks).", file=sys.stderr)
        return 2
    by_event = defaultdict(list); tags = defaultdict(list)
    for e, t in tagged:
        by_event[t["engine"]].append(e); tags[t["engine"]].append((e, t))
    snaps = {ev: make_snapshot(make_set(eos, label=ev), 0, tags[ev]) for ev, eos in by_event.items()}
    print(f"Snapshots {len(snaps)} zimejengwa (events: {', '.join(sorted(snaps))})\n")

    P = POLICIES[policy_name]
    print(f"Policy: {P['id']}")
    print("=" * 68)

    # (1) Decisions halisi kupitia Engine
    actions = Counter()
    decisions = {}
    for ev in sorted(snaps):
        d = decide(snaps[ev], P)
        decisions[ev] = d
        actions[d["action"]] += 1
        repo.append(log, "decision", _dview(d), VERSIONS)
        print(f"  {ev:22s} readiness={snaps[ev]['readiness_state']:8s} → {d['action']}")

    # (2) Gate eligibility kwa SELECT (akaunti safi + FTMO constraints halisi)
    constraints = build_constraints(_ftmo_view(_load_ftmo()))
    validated = rejected = 0
    for ev, d in decisions.items():
        if d["action"] != "SELECT":
            continue
        ctx = build_context(_fresh_account(), pair="EURUSD", worst_case=0)
        g = gate(d, constraints, ctx)
        repo.append(log, "decision", _dview(g), VERSIONS)
        if g["lifecycle"] == "VALIDATED":
            validated += 1
        else:
            rejected += 1

    # (3) Muhtasari
    print("=" * 68)
    print(f"DECISIONS: {sum(actions.values())} (kupitia Engine kwa evidence halisi)")
    for a, n in actions.most_common():
        print(f"    {a:10s} {n}")
    print(f"GATE (kwa SELECT): VALIDATED={validated} REJECTED={rejected}")
    recs = repo.load(log)
    integ = repo.integrity_check(log)
    print(f"REPOSITORY: records={len(recs)} integrity_ok={integ['ok']} "
          f"(kila decision ina provenance → snapshot halisi)")
    print("\nNB: ABSTAIN nyingi = TABIA SAHIHI (protect capital, P26). Mashine inafanya kazi na "
          "evidence halisi. Profitable ≠ Tradable Edge.")
    return 0


def _ftmo_view(c):
    """Chukua fields za FTMO kutoka config (build_constraints inahitaji hizi)."""
    keys = ("max_slots", "max_correlated_slots", "max_daily_loss", "max_total_dd",
            "daily_budget_start", "max_per_trade", "correlation_groups", "max_spread")
    view = {k: c[k] for k in keys if isinstance(c, dict) and k in c}
    # defaults salama kama config haina baadhi (paper-only)
    view.setdefault("max_slots", 4); view.setdefault("max_correlated_slots", 2)
    view.setdefault("max_daily_loss", 500); view.setdefault("max_total_dd", 1000)
    view.setdefault("daily_budget_start", 400); view.setdefault("max_per_trade", 120)
    view.setdefault("correlation_groups", {}); view.setdefault("max_spread", {})
    return view


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", default="conservative", choices=list(POLICIES))
    ap.add_argument("--pairs", nargs="*", default=None)
    a = ap.parse_args()
    try:
        import yaml
        cfgpairs = yaml.safe_load(open(os.path.join(os.path.dirname(__file__), "..", "..",
                                                    "config", "data_config.yaml")))["pairs"]
    except Exception:
        cfgpairs = ["EURUSD", "GBPUSD", "USDJPY", "EURJPY", "USDCAD", "USDCHF", "AUDUSD", "NZDUSD", "EURGBP"]
    pairs = a.pairs or cfgpairs
    with tempfile.TemporaryDirectory() as tmp:
        return run(a.policy, pairs, os.path.join(tmp, "real_run.jsonl"))


if __name__ == "__main__":
    raise SystemExit(main())
