"""
decision_policy.py — DECISION SCIENCE PHASE D5 (Chief Quant).

Evidence Layer FROZEN. Decision Object imefafanuliwa (D4, P83/84/88). Chief: kabla ya Decision
Engine, fafanua **Decision Policy** — safu inayotenganisha Decision Object na Decision Engine. Engine
ibaki GENERIC; sera (policies) zibadilike bila kuvunja architecture.

  Principle 85: Decision Objects kwa pamoja = permanent decision history.
  Principle 86: cancellation ≠ rejection.
  Principle 87: Decision Integrity ≠ Decision Outcome.
  Principle 88: kila Decision inareference Decision Policy iliyotumika.
  Principle 89 (OPEN): Execution ni immutable object tofauti na Decision Object.

Hii ni **Decision Policy Framework**, SIO Decision Engine (D6). Policy = sheria (versioned) inayomap
**Snapshot → action** (P80 complete context). Engine (baadaye) itaita policy tu. NO ML.
**Tahadhari:** policies ni RULE-based na conservative — hazithibitishi alpha (P26 default = ABSTAIN;
value halisi ni hasi → mostly ABSTAIN/AVOID). Decision-ready ≠ trade-ready (P69).

Maswali (Chief, D5):
  Q1. Policy ni nini?
  Q2. Policy ina version?
  Q3. Policy inachagua action vipi?
  Q4. Policy inaweza kubadilishwa bila kubadilisha Engine?
  Q5. Decision Engine na Policy zinawasiliana vipi?

Reuse: decision_object (make_decision, ACTIONS), evidence_snapshot (make_snapshot),
evidence_operations (build_tagged_evidence), evidence_set (make_set), market_state_engine (cfg),
evidence_object (CONFLICT_CEIL).

Output: reports/decision_policy_report.md
Self-test: python src/research/decision_policy.py --self-test
"""
from __future__ import annotations

import argparse, sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np

from market_state_engine import cfg
from evidence_object import CONFLICT_CEIL
from evidence_snapshot import make_snapshot
from evidence_operations import build_tagged_evidence
from evidence_set import make_set
from decision_object import make_decision

REPO_ROOT = Path(__file__).resolve().parents[2]

# reliability thresholds (P70 OPEN — hizi ni policy params, sio doctrine)
HI, MID, LO = 0.90, 0.75, 0.60


# ---------- Decision Policy (versioned rule: Snapshot → action) ----------
def _policy(name, version, decide_fn):
    return {"name": name, "version": version, "id": f"policy:{name}@v{version}", "decide": decide_fn}


def _capital_preservation(snap):
    """Conservative kabisa: SELECT tu kama READY + reliability juu sana + hakuna conflict; vinginevyo
    ABSTAIN (P26). Ndiyo default doctrine-aligned policy."""
    st = snap["readiness_state"]; rel = snap["reliability"]
    if st == "INVALID":
        return "ABSTAIN", "invalid evidence (conflict) → protect capital (P26)"
    if st == "READY" and rel >= HI:
        return "SELECT", f"READY + reliability {rel:.2f}≥{HI}"
    return "ABSTAIN", f"{st}, reliability {rel:.2f} < {HI} → abstain (P26)"


def _conservative(snap):
    st = snap["readiness_state"]; rel = snap["reliability"]
    if st == "INVALID":
        return "ABSTAIN", "invalid evidence"
    if st == "READY" and rel >= MID:
        return "SELECT", f"READY + reliability {rel:.2f}≥{MID}"
    if st == "STALE":
        return "WAIT", "stale evidence → wait for refresh"
    return "ABSTAIN", f"{st}, reliability {rel:.2f} < {MID}"


def _aggressive(snap):
    st = snap["readiness_state"]; rel = snap["reliability"]
    if st == "INVALID":
        return "HEDGE", "conflict → hedge instead of abstain"
    if st in ("READY", "STALE") and rel >= LO:
        return "SELECT", f"{st} + reliability {rel:.2f}≥{LO}"
    if st == "EXPIRED":
        return "WAIT", "expired → wait"
    return "REDUCE", f"{st}, reliability {rel:.2f} < {LO} → reduce"


POLICIES = {
    "capital_preservation": _policy("capital_preservation", 1, _capital_preservation),
    "conservative": _policy("conservative", 1, _conservative),
    "aggressive": _policy("aggressive", 1, _aggressive),
}


def apply_policy(policy, snapshot):
    """Q5: CONTRACT ya Engine↔Policy. Engine inaita hii; policy inarudisha (action, reason); Engine
    inaifunga kwenye Decision Object inayoreference policy_id (P88) + snapshot_id (P84).
    Hii ndiyo pekee inayounganisha Engine na Policy — loosely coupled."""
    action, reason = policy["decide"](snapshot)
    return make_decision(snapshot, action=action, reason=f"[{policy['id']}] {reason}",
                         policy_id=policy["id"])


def run(pairs, rng):
    c = cfg()
    print("Building snapshots then applying policies...", flush=True)
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
    snaps = {ev: make_snapshot(make_set(eos, label=ev), 0, tags_by_event[ev]) for ev, eos in by_event.items()}
    return _report(c, pairs, snaps)


def _report(c, pairs, snaps):
    L = ["# Decision Policy Framework — safu kati ya Decision Object na Engine (Decision Science D5)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | {len(pairs)} pairs, {len(snaps)} snapshots, "
         f"{len(POLICIES)} policies | versioned rules: Snapshot→action | NO Decision Engine | NO ML*\n",
         "> **P85** decisions = permanent history. **P86** cancelled ≠ rejected. **P87** integrity ≠ "
         "outcome. **P88** kila decision inareference policy. **P89 (OPEN)** Execution Object. Policy = "
         "sheria (versioned) inayotenganisha Object na Engine; Engine ibaki GENERIC. NO Decision Engine (D6)."]

    # Q1 — what is a policy
    L.append("\n## Q1 — Policy ni nini?\n")
    L.append("Policy = **kanuni iliyopewa jina na version** inayomap **Evidence Snapshot (complete context, "
             "P80) → action** kutoka decision family (P60). Ni **decision LOGIC**, tofauti na Decision Engine "
             "(orchestrator). Engine inaita policy; policy inaamua. NO ML — rule-based tu.")
    L.append("\n| policy | id (versioned) | tabia |")
    L.append("|--------|----------------|-------|")
    L.append("| capital_preservation | policy:capital_preservation@v1 | ABSTAIN isipokuwa READY + reliability juu sana (P26) |")
    L.append("| conservative | policy:conservative@v1 | SELECT kwa READY+mid; STALE→WAIT |")
    L.append("| aggressive | policy:aggressive@v1 | SELECT kwa READY/STALE+low; INVALID→HEDGE |")

    # Q2 — versioning
    L.append("\n## Q2 — Policy ina version?\n")
    L.append("Ndio — `name@vN`. Kila Decision Object inareference **policy_id kamili** (P88) → maamuzi ni "
             "**reproducible** hata tukibadilisha policy baadaye (version mpya = policy_id mpya = decision_id mpya).")

    # Q3 — how policy chooses action (applied to real snapshots)
    L.append("\n## Q3 — Policy inachagua action vipi? (kwenye snapshots halisi)\n")
    L.append("| snapshot (event) | readiness | reliability | capital_preservation | conservative | aggressive |")
    L.append("|------------------|-----------|-------------|----------------------|--------------|------------|")
    for ev in sorted(snaps):
        s = snaps[ev]
        a1, _ = POLICIES["capital_preservation"]["decide"](s)
        a2, _ = POLICIES["conservative"]["decide"](s)
        a3, _ = POLICIES["aggressive"]["decide"](s)
        L.append(f"| {ev} | {s['readiness_state']} | {s['reliability']:.2f} | {a1} | {a2} | {a3} |")
    L.append("\n- action inatoka **readiness_state (P82) + reliability + conflict** — SIO market prediction. "
             "Default = ABSTAIN (P26). *value halisi ni hasi → mostly ABSTAIN/AVOID; hii SI alpha (P69).*")

    # Q4 — swappable without engine change
    L.append("\n## Q4 — Policy inabadilishwa bila kubadilisha Engine?\n")
    ev0 = sorted(snaps)[0]; s0 = snaps[ev0]
    acts = {pid: apply_policy(P, s0)["action"] for pid, P in POLICIES.items()}
    L.append(f"- snapshot ile ile (`{ev0}`) → policies tofauti → actions: "
             f"**{', '.join(f'{k}={v}' for k, v in acts.items())}**.")
    L.append("- `apply_policy(policy, snapshot)` haibadiliki — policy ime-**inject**-iwa. Engine (D6) itaita "
             "`apply_policy` tu; kubadilisha policy hakubadilishi Engine code → **loosely coupled** (P84 refs).")

    # Q5 — engine<->policy communication
    L.append("\n## Q5 — Decision Engine na Policy zinawasiliana vipi?\n")
    d = apply_policy(POLICIES["capital_preservation"], s0)
    L.append("**Contract (moja tu):**")
    L.append("```text")
    L.append("Engine ── snapshot ──▶ Policy.decide(snapshot) ── (action, reason) ──▶ Engine")
    L.append("Engine ── wraps ──▶ Decision Object { action, policy_id (P88), evidence_refs=[snapshot_id] (P84) }")
    L.append("```")
    L.append(f"- mfano: `{d['id']}` action={d['action']}, policy_id={d['policy_id']}, evidence_refs={d['evidence_refs']}.")
    L.append("- Engine haijui LOGIC ya policy; inajua contract tu. Policy haijui Engine. **Fully decoupled.**")

    # VERDICT
    L.append("\n## VERDICT — D5 Decision Policy Framework\n")
    L.append("→ ✅ **Decision Policy imefafanuliwa** kama **versioned rule** (Snapshot→action; Q1/Q2), "
             "inayochagua action kutoka readiness+reliability (Q3), **swappable bila kubadilisha Engine** "
             "(Q4, dependency injection), yenye **contract moja** ya Engine↔Policy (Q5). Kila Decision "
             "inareference policy_id (P88) → reproducible. Sasa Engine (D6) itakuwa **generic orchestrator** "
             "tu. **Hakuna Decision Engine bado.** NO ML.")
    L.append("\n**Bado Decision Science D5 — policies ni rule-based, hazithibitishi alpha.** value halisi ni "
             "hasi → maamuzi mengi ni ABSTAIN/AVOID (P26); decision-ready ≠ trade-ready (P69).")

    # HONEST CAVEATS
    L.append("\n## Honest Caveats\n")
    L.append("1. **Policies ni ILLUSTRATIVE rules, hazijathibitishwa.** Thresholds (HI/MID/LO reliability) ni "
             "human choices; hakuna OOS/backtest inayoonyesha policy yoyote ina faida. Ni muundo, sio edge.")
    L.append("2. **'SELECT' HAIMAANISHI trade yenye faida.** reliability = Φ(EV/SE) inayojaa (P70 OPEN); value "
             "halisi ni hasi → hata 'SELECT' ingekuwa kwenye EV hasi. Aggressive policy ni ya mfano tu, sio "
             "pendekezo.")
    L.append("3. **Policy inatumia snapshot fields tu** (P80) — haiangalii external constraints (P89/P81 OPEN: "
             "broker/news/liquidity). Kwa hiyo action ni 'intended', sio 'executable'.")
    L.append("4. **Reproducibility inategemea policy_id + snapshot_id** — kama snapshot inatumia age-shift "
             "sare (D3 caveat), reproducibility ni ndani ya mfano huo, sio production event-time.")
    L.append("5. **Hakuna Decision Engine wala Execution (P89 OPEN)** — 'action' ni maamuzi yaliyopangwa; "
             "kilichotekelezwa (fills/slippage/rejects) ni Execution Object, bado haipo.")

    L.append("\n*Decision Policy = versioned rule Snapshot→action; swappable (injection); Engine↔Policy "
             "contract = policy.decide(snapshot); decision references policy_id (P88). Rule-based, NO alpha, "
             "NO Decision Engine, NO ML. Profitable ≠ Tradable Edge.*")

    out = REPO_ROOT / c["paths"]["reports"] / "decision_policy_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)} ({len(snaps)} snapshots × {len(POLICIES)} policies)")
    return 0


def self_test():
    def snap(state, rel):
        return {"id": "snap:x", "as_of": 0, "readiness_state": state, "reliability": rel,
                "uncertainty": 0.3, "temporal_conflict": 0.0,
                "structural_conflict": {"cross-pair": 0.0}, "aggregate": {"support": 500}}

    # (1) policy chooses action from snapshot (Q3)
    ready_hi = snap("READY", 0.95)
    a_cp, _ = POLICIES["capital_preservation"]["decide"](ready_hi)
    a_ag, _ = POLICIES["aggressive"]["decide"](snap("EXPIRED", 0.2))
    ok_choose = a_cp == "SELECT" and a_ag == "WAIT"
    print(f"policy chooses action: cap-pres(READY,0.95)={a_cp} aggr(EXPIRED)={a_ag} -> {'OK' if ok_choose else 'FAIL'}")

    # (2) swappability (Q4): same snapshot, different policies → (potentially) different actions
    s = snap("READY", 0.78)
    acts = {k: POLICIES[k]["decide"](s)[0] for k in POLICIES}
    ok_swap = acts["capital_preservation"] == "ABSTAIN" and acts["conservative"] == "SELECT"
    print(f"swappability: {acts} -> {'OK' if ok_swap else 'FAIL'}")

    # (3) decision references policy_id (P88) + snapshot_id (P84); reproducible
    d1 = apply_policy(POLICIES["conservative"], s); d2 = apply_policy(POLICIES["conservative"], s)
    ok_ref = (d1["policy_id"] == "policy:conservative@v1" and d1["evidence_refs"] == ["snap:x"]
              and d1["id"] == d2["id"])
    print(f"policy_id + reproducible: policy={d1['policy_id']} id-stable={d1['id']==d2['id']} -> {'OK' if ok_ref else 'FAIL'}")

    # (4) version change → different policy_id → different decision id
    v2 = _policy("conservative", 2, _conservative)
    d3 = apply_policy(v2, s)
    ok_ver = d3["policy_id"] == "policy:conservative@v2" and d3["id"] != d1["id"]
    print(f"versioning: v2 policy={d3['policy_id']} diff-id={d3['id']!=d1['id']} -> {'OK' if ok_ver else 'FAIL'}")

    # (5) INVALID snapshot → conservative ABSTAIN, aggressive HEDGE (conflict handling)
    inv = snap("INVALID", 0.9)
    ok_inv = POLICIES["conservative"]["decide"](inv)[0] == "ABSTAIN" and POLICIES["aggressive"]["decide"](inv)[0] == "HEDGE"
    print(f"invalid handling: conservative=ABSTAIN aggressive=HEDGE -> {'OK' if ok_inv else 'FAIL'}")

    ok = ok_choose and ok_swap and ok_ref and ok_ver and ok_inv
    print(f"\nSELF-TEST: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    c = cfg()
    return run(c["pairs"], np.random.default_rng(5))


if __name__ == "__main__":
    raise SystemExit(main())
