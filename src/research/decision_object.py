"""
decision_object.py — DECISION SCIENCE PHASE D4 (Chief Quant).

Evidence Layer (D0 Object → D1 Operations → D2 Set → D3 Snapshot) sasa **FROZEN** kama stable
architecture. Chief: kama Market Science ilianza kwa kufafanua **Event** kabla ya algorithms,
Decision Science ianze kwa kufafanua **Decision Object** kabla ya Decision Engine. Decision Engine
iwe *consumer* wa architecture, sio sehemu inayolazimisha ibadilike.

  Principle 80: Evidence Snapshot inafafanua **complete decision context** kwa Decision Layer.
  Principle 81 (OPEN): tofautisha internal evidence conflicts na external execution constraints.
  Principle 82: decision-readiness ni **state machine** (READY→STALE→EXPIRED→INVALID), sio score.
  Principle 83: **maamuzi ni immutable first-class objects** (kama Evidence).
  Principle 84: kila Decision Object inareference **exact Evidence Snapshot ID** iliyotoka.

Hii ni **Decision Object** (data structure + lifecycle + provenance + integrity + audit), SIO
Decision Engine. Hakuna logic inayomap snapshot→action (hiyo ni engine). Demo inatumia action ya
default **ABSTAIN** (P26 capital preservation) — hakuna decision inayofanywa hapa. NO ML.

Maswali (Chief, D4):
  Q1. Decision Object ina fields gani? (id, action, reason, reliability, risk, evidence_refs, timestamp)
  Q2. Decision ina lifecycle gani? (PROPOSED→VALIDATED→EXECUTED→SETTLED; side EXPIRED/REJECTED/CANCELLED)
  Q3. Decision ina provenance yake? (snapshot → decision graph; P84)
  Q4. Decision ina integrity metrics gani? (structural; SIO OOS bado; P87)
  Q5. Decision ina audit trail gani? (P66)

Reuse: evidence_snapshot (make_snapshot, readiness_state), evidence_operations (build_tagged_evidence),
evidence_set (make_set), market_state_engine (cfg).

Output: reports/decision_object_report.md
Self-test: python src/research/decision_object.py --self-test
"""
from __future__ import annotations

import argparse, sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np

from market_state_engine import cfg
from evidence_snapshot import make_snapshot
from evidence_operations import build_tagged_evidence
from evidence_set import make_set

REPO_ROOT = Path(__file__).resolve().parents[2]

# Decision family (P60) — action enum
ACTIONS = ["SELECT", "ABSTAIN", "REDUCE", "HEDGE", "DIVERSIFY", "WAIT", "EXIT", "SUSPEND"]
# Decision lifecycle state machine (Q2; mirrors P82 for decisions)
LIFECYCLE = ["PROPOSED", "VALIDATED", "EXECUTED", "SETTLED"]
# side states: REJECTED (integrity fail) · EXPIRED (evidence expired) · CANCELLED (P86: stopped
# before execution by news/broker/manual — DISTINCT from rejection)
LIFECYCLE_SIDE = ["EXPIRED", "REJECTED", "CANCELLED"]


def _decision_id(snapshot_id, action, as_of, policy_id):
    import hashlib
    return "dec:" + hashlib.sha1(f"{snapshot_id}|{action}|{int(as_of)}|{policy_id}".encode()).hexdigest()[:10]


def make_decision(snapshot, action="ABSTAIN", reason=None, audit=None, policy_id="policy:default@v0"):
    """Construct an immutable Decision Object (P83) inayoreference exact Snapshot ID (P84) NA
    Decision Policy ID (P88). NB: hakuna engine-logic hapa — action ni INPUT (demo = ABSTAIN, P26).
    Decision Objects kwa pamoja = permanent decision history (P85)."""
    assert action in ACTIONS, f"action lazima iwe {ACTIONS}"
    sid = snapshot["id"]
    rstate = snapshot["readiness_state"]
    # INTEGRITY metrics (Q4; P87) — uhalali wa object KABLA ya execution; STRUCTURAL, SIO outcome/OOS
    struct_max = max([v for v in snapshot["structural_conflict"].values()], default=0.0)
    integrity = {
        "evidence_readiness_state": rstate,               # P82
        "evidence_reliability": round(snapshot["reliability"], 4),   # P70 OPEN (sio confidence rasmi)
        "temporal_conflict": round(snapshot["temporal_conflict"], 4),
        "structural_conflict_max": round(struct_max, 4),
        "support_behind": snapshot["aggregate"]["support"] if snapshot["aggregate"] else 0,
        "is_abstention": action == "ABSTAIN",
    }
    dec = {
        # --- Claim (Q1) ---
        "id": _decision_id(sid, action, snapshot["as_of"], policy_id),
        "action": action,
        "reason": reason or f"snapshot={rstate}; default capital-preservation (P26)",
        "reliability": round(snapshot["reliability"], 4),      # inherits snapshot (P70 OPEN)
        "risk": round(snapshot["uncertainty"], 4) if np.isfinite(snapshot["uncertainty"]) else None,
        # --- references (Q3; P84 + P88) ---
        "evidence_refs": [sid],                                # references SNAPSHOT ID, sio objects
        "policy_id": policy_id,                                # P88: policy iliyounda decision hii
        "parent_decision_id": None,                            # E1/Q3 (P85): decision-mzazi (Gate ndiyo huijaza); PROPOSED=None
        "parents": [sid],                                      # snapshot → decision (graph, P72 style)
        # --- operational (Q2) ---
        "timestamp": int(snapshot["as_of"]),
        "lifecycle": "PROPOSED",
        # --- integrity (Q4; P87) + audit (Q5) ---
        "integrity": integrity,
        "audit": list(audit) if audit else [f"make_decision(action={action}, snapshot={sid}, policy={policy_id})"],
    }
    return dec


def transition(dec, to_state):
    """Q2: lifecycle transition (immutable — rudisha object mpya + audit). P83.
    CANCELLED (P86) inaruhusiwa KABLA ya execution tu (PROPOSED/VALIDATED) — tofauti na REJECTED.

    E1 (Chief ruling Q1, 2026-07-04): **PROPOSED→VALIDATED imeretire hapa** — VALIDATION ≠ ELIGIBILITY.
    Crossing PROPOSED→VALIDATED ni ya **Integrity Gate** (E1) inayozalisha Decision Object MPYA (id
    mpya + parent_decision_id) kupitia `make_gate_decision` — SIO same-id lifecycle bump. transition()
    inabaki kwa lifecycle za baada-ya-eligibility (VALIDATED→EXECUTED→SETTLED) na side-states."""
    valid = {"PROPOSED": {"REJECTED", "EXPIRED", "CANCELLED"},  # VALIDATED imeondolewa (Gate ndiyo canonical crossing — E1/Q1)
             "VALIDATED": {"EXECUTED", "REJECTED", "EXPIRED", "CANCELLED"},
             "EXECUTED": {"SETTLED"},                          # baada ya execution huwezi CANCEL
             "SETTLED": set(), "REJECTED": set(), "EXPIRED": set(), "CANCELLED": set()}
    if to_state not in valid.get(dec["lifecycle"], set()):
        raise ValueError(f"transition batili {dec['lifecycle']} → {to_state}")
    new = {k: (list(v) if isinstance(v, list) else v) for k, v in dec.items()}
    new["lifecycle"] = to_state
    new["audit"] = list(dec["audit"]) + [f"transition({dec['lifecycle']}→{to_state})"]
    return new


def _gate_decision_id(parent_id, new_lifecycle, gate_id, as_of):
    """E1/Q2 (Chief): id ya Decision Object MPYA iliyotolewa na Gate. Inajumuisha parent + lifecycle +
    gate_id ili VALIDATED na REJECTED za parent MMOJA zipate id TOFAUTI, na zisigongane na id ya
    PROPOSED (P83 unique identity)."""
    import hashlib
    return "dec:" + hashlib.sha1(
        f"{parent_id}|{new_lifecycle}|{gate_id}|{int(as_of)}".encode()).hexdigest()[:10]


def make_gate_decision(parent, new_lifecycle, gate_id, eligibility=None, audit=None):
    """E1 (Chief ruling Q1-Q3/Q5): Integrity Gate hutoa Decision Object MPYA immutable kutoka kwa
    decision-mzazi wa **PROPOSED** — VALIDATED (eligible) au REJECTED (ineligible). **SIO mutation**
    (P83/P85): parent inabaki kama ilivyo; object mpya ina id mpya (Q2) na `parent_decision_id`
    inayonyoosha nyuma (Q3, P85 traceability). `gate_id` (P88 pattern) inarekodiwa kama policy_id."""
    assert new_lifecycle in ("VALIDATED", "REJECTED"), "Gate hutoa VALIDATED|REJECTED tu"
    assert parent.get("lifecycle") == "PROPOSED", "Gate inagate decision za PROPOSED pekee"
    new = {k: (list(v) if isinstance(v, list) else dict(v) if isinstance(v, dict) else v)
           for k, v in parent.items()}
    new["id"] = _gate_decision_id(parent["id"], new_lifecycle, gate_id, parent["timestamp"])
    new["lifecycle"] = new_lifecycle
    new["parent_decision_id"] = parent["id"]                   # Q3 (P85): sio-yatima
    new["gate_id"] = gate_id                                   # Q5 (P88): eligibility reproducible
    if eligibility is not None:
        new["eligibility"] = eligibility                       # rekodi ya constraints (E1 Q4/Q6)
    base_audit = list(audit) if audit else list(parent["audit"])
    new["audit"] = base_audit + [
        f"gate({gate_id}): {parent['lifecycle']}→{new_lifecycle} (parent={parent['id']})"]
    return new


def decision_provenance(dec):
    """Q3: provenance graph — Decision → Evidence Snapshot(s)."""
    return {"decision": dec["id"], "snapshots": list(dec["evidence_refs"])}


def run(pairs, rng):
    c = cfg()
    print("Building snapshots then Decision Objects (action=ABSTAIN default)...", flush=True)
    tagged, no_px = build_tagged_evidence(pairs)
    if no_px:
        print("HITILAFU: state parquet haina OHLC. Endesha market_state_engine.py kwanza.", file=sys.stderr)
        return 1
    if len(tagged) < 4:
        print("HITILAFU: evidence haitoshi.", file=sys.stderr)
        return 1
    by_event = defaultdict(list); tags_by_event = defaultdict(list)
    for e, t in tagged:
        by_event[t["engine"]].append(e); tags_by_event[t["engine"]].append((e, t))
    decisions = {}
    for ev, eos in by_event.items():
        snap = make_snapshot(make_set(eos, label=ev), as_of=0, tagged=tags_by_event[ev])
        # action = ABSTAIN default (hakuna engine) — kama snapshot si READY, abstain ni sahihi (P26)
        decisions[ev] = make_decision(snap, action="ABSTAIN",
                                      reason=f"evidence {snap['readiness_state']} → abstain (no Decision Engine; P26)")
    return _report(c, pairs, decisions)


def _report(c, pairs, decisions):
    L = ["# Decision Objects — fafanua Decision kabla ya Decision Engine (Decision Science D4)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | {len(pairs)} pairs, {len(decisions)} decision objects "
         f"(action=ABSTAIN default) | immutable value objects referencing snapshot IDs | NO Decision Engine | NO ML*\n",
         "> **P80** Snapshot = complete decision context. **P81 (OPEN)** internal-evidence vs external-"
         "execution conflict. **P82** readiness = state machine. **P83** decisions ni immutable first-class "
         "objects. **P84** kila decision inareference exact Snapshot ID. **Evidence Layer FROZEN.** Hii ni "
         "Decision Object (structure), SIO Decision Engine."]

    d0 = list(decisions.values())[0]

    # Q1 — fields
    L.append("\n## Q1 — Decision Object: fields\n")
    L.append("| field | maana | mfano |")
    L.append("|-------|-------|-------|")
    L.append(f"| id | immutable identity (P83) | {d0['id']} |")
    L.append(f"| action | decision family (P60) | {d0['action']} |")
    L.append(f"| reason | maelezo | {d0['reason']} |")
    L.append(f"| reliability | kutoka snapshot (P70 OPEN: sio 'confidence') | {d0['reliability']} |")
    L.append(f"| risk | uncertainty ya evidence | {d0['risk']} |")
    L.append(f"| evidence_refs | **Snapshot ID** (P84), sio objects | {d0['evidence_refs']} |")
    L.append(f"| policy_id | **Decision Policy** iliyounda (P88) | {d0['policy_id']} |")
    L.append(f"| timestamp | as-of | {d0['timestamp']} |")
    L.append(f"| lifecycle | state (Q2) | {d0['lifecycle']} |")

    # Q2 — lifecycle
    L.append("\n## Q2 — Decision lifecycle (state machine)\n")
    L.append("```text")
    L.append("PROPOSED → VALIDATED → EXECUTED → SETTLED")
    L.append("   ↘ REJECTED / EXPIRED / CANCELLED (side states; P86: CANCELLED ≠ REJECTED)")
    L.append("```")
    # PROPOSED→VALIDATED = Integrity Gate (E1, object MPYA); VALIDATED→EXECUTED→SETTLED = transition()
    chain = make_gate_decision(d0, "VALIDATED", "gate:integrity@v1")   # E1/Q1: crossing = object mpya
    steps = [d0["lifecycle"], chain["lifecycle"]]
    for s in ("EXECUTED", "SETTLED"):
        chain = transition(chain, s); steps.append(chain["lifecycle"])
    L.append(f"- mfano transitions: {' → '.join(steps)} (PROPOSED→VALIDATED = Gate/object mpya E1; "
             "salio = transition(); kila hatua immutable + audit; P83).")

    # Q3 — provenance
    L.append("\n## Q3 — Decision provenance (→ Evidence Snapshot; P84)\n")
    L.append("| decision | → snapshot refs |")
    L.append("|----------|-----------------|")
    for ev in sorted(decisions):
        pv = decision_provenance(decisions[ev])
        L.append(f"| {decisions[ev]['id']} ({ev}) | {pv['snapshots']} |")
    L.append("\n- kila Decision inareference **Snapshot ID** halisi (P84), sio Evidence Object moja kwa "
             "moja → mfumo fully auditable (Decision → Snapshot → Set → Operations → Objects).")

    # Q4 — integrity metrics (P87)
    L.append("\n## Q4 — Decision INTEGRITY metrics (P87: uhalali KABLA ya execution; SIO outcome/OOS)\n")
    L.append("| decision | evidence state | reliability | temporal-cf | struct-cf | support | abstention? |")
    L.append("|----------|----------------|-------------|-------------|-----------|---------|-------------|")
    for ev in sorted(decisions):
        q = decisions[ev]["integrity"]
        L.append(f"| {ev} | {q['evidence_readiness_state']} | {q['evidence_reliability']} | "
                 f"{q['temporal_conflict']} | {q['structural_conflict_max']} | {q['support_behind']:,} | "
                 f"{'✅' if q['is_abstention'] else '—'} |")
    L.append("\n- **integrity** metrics (P87) ni **structural** (zinatoka snapshot) — zinapima uhalali wa decision KABLA ya execution, SIO outcome/OOS quality (hiyo ni "
             "D5 Decision Quality baadaye, per-decision OOS + FDR). Decision-ready ≠ trade-ready (P69).")

    # Q5 — audit trail
    L.append("\n## Q5 — Decision audit trail (P66)\n")
    dtmp = make_gate_decision(d0, "VALIDATED", "gate:integrity@v1")   # E1: validate = Gate/object mpya
    L.append(f"- mfano audit (baada ya create + gate-validate): `{dtmp['audit']}`")
    L.append("- kila make/transition inaongeza audit entry inayoreference snapshot ID → traceable kabisa.")

    # VERDICT
    L.append("\n## VERDICT — D4 Decision Objects\n")
    L.append("→ ✅ **Decision Object imefafanuliwa** kama **immutable first-class value object** (P83) yenye "
             "fields (Q1: action/reason/reliability/risk/evidence_refs/timestamp), **lifecycle state machine** "
             "(Q2), **provenance** inayoreference **exact Snapshot ID** (Q3, P84), **integrity metrics** "
             "structural (Q4; P87), na **audit trail** (Q5, P66). Snapshot = complete decision context (P80). "
             "Sasa Decision Engine itakuwa *consumer* mdogo: snapshot → action, ikijaza Decision Object. "
             "**Hakuna Decision Engine bado.** NO ML.")
    L.append("\n**Bado Decision Science D4 — hakuna decision-LOGIC wala alpha.** Action zote ni ABSTAIN "
             "default (P26); hakuna selection/sizing iliyofanywa. Hii ni definition ya object, sio engine.")

    # HONEST CAVEATS
    L.append("\n## Honest Caveats\n")
    L.append("1. **Hakuna decision inayofanywa hapa** — action=ABSTAIN ni default ya kudumu (P26), sio "
             "matokeo ya logic. Decision Engine (D-baadaye) ndiyo itakayochagua action kutoka snapshot.")
    L.append("2. **Quality metrics ni structural, SIO outcome.** Zinapima ubora wa EVIDENCE nyuma ya decision, "
             "sio kama decision ilikuwa sahihi (hakuna OOS/FDR bado — D5). Decision-ready ≠ trade-ready (P69).")
    L.append("3. **reliability = snapshot reliability = Φ(EV/SE)** — inajaa kwa n kubwa (P70 OPEN); 'reliability' "
             "ni jina la muda.")
    L.append("4. **P81 (external constraints) haijatekelezwa** — Decision Object bado haina uwanja wa broker/"
             "news/execution constraints; ni kazi ya baadaye.")
    L.append("5. **Immutability ni by-convention** (transition inarudisha object mpya) — Python dict si frozen; "
             "enforcement kamili (frozen dataclass) ni engineering ya baadaye, kama Evidence Object.")

    L.append("\n*Decision Object: immutable value object (P83) referencing exact Snapshot ID (P84); action "
             "family (P60); lifecycle state machine; structural integrity; audit trail. Evidence Layer FROZEN. "
             "NO Decision Engine. NO ML. Profitable ≠ Tradable Edge.*")

    out = REPO_ROOT / c["paths"]["reports"] / "decision_object_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)} ({len(decisions)} decision objects)")
    return 0


def self_test():
    # snapshot ya bandia (minimal, mimic make_snapshot output)
    snap = {"id": "snap:abc1234567", "as_of": 0, "readiness_state": "READY", "reliability": 0.72,
            "uncertainty": 0.3, "temporal_conflict": 0.0,
            "structural_conflict": {"cross-pair": 0.1}, "aggregate": {"support": 500}}

    # (1) fields + references snapshot ID (P84)
    d = make_decision(snap, action="ABSTAIN")
    ok_fields = (d["evidence_refs"] == [snap["id"]] and d["action"] == "ABSTAIN"
                 and "id" in d and d["lifecycle"] == "PROPOSED")
    print(f"fields + snapshot-ref (P84): refs={d['evidence_refs']} action={d['action']} -> {'OK' if ok_fields else 'FAIL'}")

    # (2) immutable identity (P83): same inputs → same id; input not mutated by gate-crossing
    d2 = make_decision(snap, action="ABSTAIN")
    before = dict(d); dv = make_gate_decision(d, "VALIDATED", "gate:integrity@v1")  # E1: crossing = object mpya
    ok_immut = (d["id"] == d2["id"] and d["lifecycle"] == before["lifecycle"] == "PROPOSED"
                and dv["lifecycle"] == "VALIDATED")
    print(f"immutable identity + no-mutate: id-stable={d['id']==d2['id']} input={d['lifecycle']} new={dv['lifecycle']} -> {'OK' if ok_immut else 'FAIL'}")

    # (3) lifecycle transitions valid; invalid rejected (PROPOSED→VALIDATED = Gate, si transition)
    chain = transition(transition(dv, "EXECUTED"), "SETTLED")               # VALIDATED→EXECUTED→SETTLED
    ok_life = chain["lifecycle"] == "SETTLED"
    try:
        transition(d, "EXECUTED"); ok_bad = False   # PROPOSED→EXECUTED batili
    except ValueError:
        ok_bad = True
    print(f"lifecycle: PROPOSED→(gate)VALIDATED→…→{chain['lifecycle']}; invalid-blocked={ok_bad} -> {'OK' if ok_life and ok_bad else 'FAIL'}")

    # (4) audit grows + references snapshot
    ok_audit = len(dv["audit"]) > len(d["audit"]) and snap["id"] in d["audit"][0]
    print(f"audit trail: create={len(d['audit'])} →gate-validate={len(dv['audit'])} refs-snap={snap['id'] in d['audit'][0]} -> {'OK' if ok_audit else 'FAIL'}")

    # (5) quality metrics structural
    q = d["integrity"]
    ok_q = q["evidence_readiness_state"] == "READY" and q["is_abstention"] and "support_behind" in q
    print(f"integrity (structural): state={q['evidence_readiness_state']} abstain={q['is_abstention']} -> {'OK' if ok_q else 'FAIL'}")

    # (6) P86: CANCELLED ≠ REJECTED — inafikika KABLA ya execution tu (PROPOSED/VALIDATED);
    # baada ya EXECUTED huwezi CANCEL; CANCELLED ni terminal (VALIDATED sasa hutoka kwa Gate — E1)
    c1 = transition(make_decision(snap), "CANCELLED")                       # PROPOSED → CANCELLED
    v_ = make_gate_decision(make_decision(snap), "VALIDATED", "gate:integrity@v1")
    c2 = transition(v_, "CANCELLED")                                        # VALIDATED → CANCELLED
    try:
        transition(transition(v_, "EXECUTED"), "CANCELLED")
        ok_no_exec_cancel = False                                           # EXECUTED → CANCELLED batili
    except ValueError:
        ok_no_exec_cancel = True
    try:
        transition(c1, "VALIDATED"); ok_terminal = False                    # CANCELLED ni terminal
    except ValueError:
        ok_terminal = True
    ok_cancel = (c1["lifecycle"] == "CANCELLED" and c2["lifecycle"] == "CANCELLED"
                 and ok_no_exec_cancel and ok_terminal)
    print(f"P86 CANCELLED: proposed→{c1['lifecycle']} validated→{c2['lifecycle']} "
          f"executed-blocked={ok_no_exec_cancel} terminal={ok_terminal} -> {'OK' if ok_cancel else 'FAIL'}")

    # (7) E1 (Chief Q1-Q3): PROPOSED→VALIDATED imeretire kwenye transition(); Gate = object MPYA
    try:
        transition(d, "VALIDATED"); ok_retired = False                     # retired → lazima iraise
    except ValueError:
        ok_retired = True
    gv = make_gate_decision(d, "VALIDATED", "gate:integrity@v1")
    gr = make_gate_decision(d, "REJECTED", "gate:integrity@v1")
    ok_gate = (gv["id"] != d["id"] and gv["id"] != gr["id"]                 # Q2: id mpya + VALIDATED≠REJECTED
               and gv["parent_decision_id"] == d["id"]                      # Q3: parent link
               and gr["parent_decision_id"] == d["id"]
               and gv["gate_id"] == "gate:integrity@v1"                     # Q5
               and d["lifecycle"] == "PROPOSED" and d.get("parent_decision_id") is None)  # parent salama
    print(f"E1 gate-crossing: transition-retired={ok_retired} new-id={gv['id']!=d['id']} "
          f"validated≠rejected={gv['id']!=gr['id']} parent-link={gv['parent_decision_id']==d['id']} -> {'OK' if ok_retired and ok_gate else 'FAIL'}")

    ok = (ok_fields and ok_immut and ok_life and ok_bad and ok_audit and ok_q and ok_cancel
          and ok_retired and ok_gate)
    print(f"\nSELF-TEST: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    c = cfg()
    return run(c["pairs"], np.random.default_rng(4))


if __name__ == "__main__":
    raise SystemExit(main())
