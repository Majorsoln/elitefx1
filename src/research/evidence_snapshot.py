"""
evidence_snapshot.py — DECISION SCIENCE PHASE D3 (Chief Quant).

Evidence Layer: D0 Object → D1 Operations → D2 Set. Chief: kipande cha mwisho kabla ya Decision
Science ya kweli ni **Evidence Snapshot** — picha ya ushahidi ambayo Decision Layer inaiona kwa
wakati fulani. Decision Engine HAITAFANYA kazi juu ya Object wala Set ghafi, bali juu ya SNAPSHOT.

  Principle 76: maana ya evidence haitegemei insertion order; lineage huwakilishwa kando (provenance).
  Principle 77: maamuzi yanafanyika juu ya **Evidence Snapshots**, sio raw Evidence Objects.
  Principle 78 (OPEN): tofautisha statistical redundancy na identity duplication.
  Principle 79: **Evidence Snapshot ndiyo canonical input** kwa Decision Layer.

Architecture: Object → Operations → Set → **Snapshot** ══ Decision → Execution → Feedback.

Maswali (Chief, D3):
  Q1. Snapshot ni nini rasmi?
  Q2. Snapshot ina fields gani?
  Q3. Snapshot readiness inakokotolewaje?
  Q4. Temporal conflict (P74) inaonekana vipi kwenye snapshot?
  Q5. Decision Engine itapokea Object, Set, au Snapshot? (jibu: Snapshot — P79)

Mbinu: Snapshot = immutable point-in-time VIEW ya Evidence Set as-of T (resolve freshness/expiry,
keep live, set-reliability + readiness, temporal + structural conflict, provenance root). NO
Decision Engine. NO ML.

Reuse: evidence_object (make_evidence, is_expired, decision_ready, _freshness, CONFLICT_CEIL,
TTL_BARS, STALE_BARS), evidence_operations (op_aggregate, conflict_taxonomy, build_tagged_evidence,
_level_mean), evidence_set (make_set, provenance_graph), market_state_engine (cfg).

Output: reports/evidence_snapshot_report.md
Self-test: python src/research/evidence_snapshot.py --self-test
"""
from __future__ import annotations

import argparse, sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np

from market_state_engine import cfg
from evidence_object import (make_evidence, is_expired, decision_ready,
                             CONFLICT_CEIL, TTL_BARS, STALE_BARS, EPS)
from evidence_operations import op_aggregate, conflict_taxonomy, build_tagged_evidence, _level_mean
from evidence_set import make_set, provenance_graph

REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------- resolve member as-of time T (P73: operational state is time-varying) ----------
def _resolve(eo, as_of):
    """Evidence object iliyoresolve as-of T (age imeshiftiwa; identity ya CLAIM/QUALITY haibadiliki)."""
    return make_evidence(eo["value"], eo["uncertainty"], eo["support"], eo["coverage"],
                         eo["age_bars"] + int(as_of), eo["source"], conflict=eo["conflict"])


# ---------- temporal conflict (P74) ----------
def temporal_conflict(resolved_live):
    """Q4/P74: contradiction ya KIMUDA (older vs newer) — tofauti na structural. Gawa kwa median age
    (older/newer), linganisha ishara ya weighted-mean. Rudisha score [0,1] (opposite-sign weight)."""
    if len(resolved_live) < 2:
        return 0.0, None, None
    ages = np.array([e["age_bars"] for e in resolved_live])
    med = float(np.median(ages))
    older = [e for e in resolved_live if e["age_bars"] >= med]
    newer = [e for e in resolved_live if e["age_bars"] < med]
    if not older or not newer:
        return 0.0, None, None
    mo, wo = _level_mean(older); mn, wn = _level_mean(newer)
    s = np.sign(wo * mo + wn * mn) or 1.0
    dis = (wo if mo * s < 0 else 0.0) + (wn if mn * s < 0 else 0.0)
    return float(dis / (wo + wn)), float(mo), float(mn)


# ---------- the Evidence Snapshot (canonical Decision-Layer input, P79) ----------
def make_snapshot(evset, as_of, tagged=None):
    """Q1/Q2: immutable point-in-time view ya Evidence Set as-of T.
    Fields: as_of, set, n_total, n_live, reliability, aggregate, readiness, why,
            temporal_conflict, structural_conflict, provenance_root."""
    resolved = [_resolve(e, as_of) for e in evset["members"]]
    live = [e for e in resolved if not is_expired(e)]
    agg = op_aggregate(live) if live else None
    ready, why = decision_ready(agg) if agg is not None else (False, "no live evidence")
    tcf, mo, mn = temporal_conflict(live)
    # structural conflict (D1 taxonomy) kama tags zipo
    struct = conflict_taxonomy(tagged) if tagged else {"intra (split-half)": (agg["conflict"] if agg else 0.0)}
    nodes, edges = provenance_graph(resolved + ([agg] if agg else []))
    # readiness ya snapshot = set-readiness AND temporal conflict chini ya ceiling (P74)
    snap_ready = bool(ready and tcf < CONFLICT_CEIL)
    if tcf >= CONFLICT_CEIL:
        why_final = "temporal-conflict"          # P74: contradiction ya kimuda inatangulia (abstain)
    elif not ready:
        why_final = why
    else:
        why_final = "ready"
    # P82: readiness ni STATE MACHINE (READY→STALE→EXPIRED→INVALID), sio score.
    struct_max = max([v for k, v in struct.items()], default=0.0)
    state = readiness_state(len(live), agg, snap_ready, tcf, struct_max)
    label = evset.get("label", "set")
    sid = _snapshot_id(label, as_of, agg, len(live), state)
    return {
        "id": sid,                                              # P84: exact snapshot identity
        "as_of": int(as_of), "set": label,
        "n_total": len(resolved), "n_live": len(live),
        "reliability": (agg["confidence"] if agg else 0.0),     # Set RELIABILITY (P70 OPEN: sio "confidence")
        "value": (agg["value"] if agg else 0.0),
        "uncertainty": (agg["uncertainty"] if agg else float("inf")),
        "aggregate": agg,
        "readiness": snap_ready, "readiness_state": state, "why": why_final,
        "temporal_conflict": tcf, "older_mean": mo, "newer_mean": mn,
        "structural_conflict": struct,
        "provenance": {"nodes": len(nodes), "edges": len(edges)},
    }


def readiness_state(n_live, agg, ready, tcf, struct_max):
    """P82: state machine ya decision-readiness (SIO score). READY→STALE→EXPIRED→INVALID.
    Priority: conflict → INVALID; hakuna live → EXPIRED; ready → READY; vinginevyo → STALE."""
    if tcf >= CONFLICT_CEIL or struct_max >= CONFLICT_CEIL:
        return "INVALID"          # contradictory evidence — haiwezi kuamua
    if n_live == 0 or agg is None:
        return "EXPIRED"          # hakuna live evidence
    if ready:
        return "READY"
    return "STALE"                # live lakini haijafikia threshold (support/reliability/aging)


def _snapshot_id(label, as_of, agg, n_live, state):
    import hashlib
    v = agg["value"] if agg else 0.0; u = agg["uncertainty"] if agg else 0.0
    key = f"{label}|{int(as_of)}|{v:.6f}|{u:.6f}|{n_live}|{state}"
    return "snap:" + hashlib.sha1(key.encode()).hexdigest()[:10]


# Q5: the canonical Decision-Layer input is the Snapshot (P79).
def decision_input(evset, as_of, tagged=None):
    """P79: kile Decision Layer inapokea = SNAPSHOT (sio Object, sio Set ghafi)."""
    return make_snapshot(evset, as_of, tagged)


def run(pairs, rng):
    c = cfg()
    print("Building tagged evidence → sets → snapshots...", flush=True)
    tagged, no_px = build_tagged_evidence(pairs)
    if no_px:
        print("HITILAFU: state parquet haina OHLC. Endesha market_state_engine.py kwanza.", file=sys.stderr)
        return 1
    if len(tagged) < 4:
        print("HITILAFU: evidence haitoshi.", file=sys.stderr)
        return 1
    by_event = defaultdict(list)
    tags_by_event = defaultdict(list)
    for e, t in tagged:
        by_event[t["engine"]].append(e); tags_by_event[t["engine"]].append((e, t))
    sets = {ev: make_set(eos, label=ev) for ev, eos in by_event.items()}
    return _report(c, pairs, tagged, sets, tags_by_event)


def _report(c, pairs, tagged, sets, tags_by_event):
    L = ["# Evidence Snapshots — picha ya ushahidi kwa wakati fulani (Decision Science D3)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | {len(pairs)} pairs, {len(sets)} sets | Snapshot = "
         f"canonical Decision-Layer input (P79) | temporal + structural conflict | NO Decision Engine | NO ML*\n",
         "> **P76** maana order-independent, lineage kando. **P77** maamuzi juu ya **Snapshots**, sio "
         "objects ghafi. **P78 (OPEN)** redundancy vs duplication. **P79** **Snapshot = canonical input** "
         "kwa Decision Layer. Architecture: Object→Operations→Set→**Snapshot** ══ Decision→Execution."]

    snaps = {ev: make_snapshot(sets[ev], as_of=0, tagged=tags_by_event[ev]) for ev in sets}

    # Q1 + Q2 — definition + fields
    L.append("\n## Q1+Q2 — Snapshot ni nini + fields\n")
    L.append("**Q1:** Snapshot = **immutable point-in-time view** ya Evidence Set as-of muda T: inaresolve "
             "freshness/expiry ya kila member kwa T, inabaki na live tu, inakokotoa reliability/readiness, na "
             "inarekodi temporal + structural conflict + provenance root. Ni 'picha' ambayo Decision Layer "
             "inaiona (P77/P79).")
    L.append("\n| field | maana |")
    L.append("|-------|-------|")
    L.append("| as_of | muda T wa snapshot |")
    L.append("| n_total / n_live | members wote / wasio-expired as-of T |")
    L.append("| reliability | set reliability = aggregate confidence (P70 OPEN: SIO 'confidence' rasmi) |")
    L.append("| value / uncertainty | aggregate effect + SE (live) |")
    L.append("| readiness | set-ready **na** temporal-conflict < ceiling (snapshot-level, P73) |")
    L.append("| temporal_conflict | older-vs-newer sign contradiction (P74) |")
    L.append("| structural_conflict | taxonomy ya D1 (intra/cross-pair/cross-tf/cross-engine) |")
    L.append("| provenance | nodes/edges za graph (P72) |")

    # Q3 — readiness
    L.append("\n## Q3 — Snapshot readiness inakokotolewaje?\n")
    L.append("- `readiness = decision_ready(aggregate ya live members @T)` **NA** `temporal_conflict < "
             f"{CONFLICT_CEIL}`. Yaani: support/reliability/non-expired/low-structural-conflict (P26 default "
             "abstain) **pamoja na** kutokuwa na contradiction ya kimuda (P74).")
    L.append("\n| set | as_of=0 | as_of=+stale | as_of=+TTL |")
    L.append("|-----|---------|--------------|------------|")
    for ev in sorted(sets):
        s0 = make_snapshot(sets[ev], 0, tags_by_event[ev])
        s1 = make_snapshot(sets[ev], STALE_BARS + 1, tags_by_event[ev])
        s2 = make_snapshot(sets[ev], TTL_BARS + 1, tags_by_event[ev])
        L.append(f"| {ev} | {s0['readiness']} ({s0['why']}) | {s1['readiness']} | {s2['readiness']} (live {s2['n_live']}) |")

    # Q4 — temporal conflict
    L.append("\n## Q4 — Temporal conflict (P74) kwenye snapshot\n")
    L.append("| set | temporal_conflict | older mean | newer mean | tafsiri |")
    L.append("|-----|-------------------|-----------|-----------|---------|")
    for ev in sorted(sets):
        s = snaps[ev]
        om = f"{s['older_mean']:+.3f}" if s['older_mean'] is not None else "—"
        nm = f"{s['newer_mean']:+.3f}" if s['newer_mean'] is not None else "—"
        tf = "contradiction ya kimuda ⚠️" if s["temporal_conflict"] >= CONFLICT_CEIL else "thabiti kimuda"
        L.append(f"| {ev} | {s['temporal_conflict']:.2f} | {om} | {nm} | {tf} |")
    L.append("\n- temporal conflict (older vs newer) ni **tofauti** na structural (cross-pair/engine). "
             "Snapshot inaitenga wazi — Decision Engine itahitaji kujua aina ya conflict kabla ya policy.")

    # Q5 — canonical input
    L.append("\n## Q5 — Decision Engine itapokea Object, Set, au Snapshot?\n")
    ev0 = sorted(sets)[0]
    di = decision_input(sets[ev0], 0, tags_by_event[ev0])
    L.append(f"→ **SNAPSHOT** (P79). Mfano `decision_input({ev0})`: as_of={di['as_of']}, n_live={di['n_live']}, "
             f"reliability={di['reliability']:.2f}, value={di['value']:+.3f}, readiness={di['readiness']}, "
             f"temporal_conflict={di['temporal_conflict']:.2f}.")
    L.append("- Object = immutable claim; Set = collection; **Snapshot = picha as-of T** ambayo ndiyo "
             "pekee inayobeba readiness + conflict resolved → ndiyo canonical Decision-Layer input.")

    # VERDICT
    L.append("\n## VERDICT — D3 Evidence Snapshots\n")
    L.append("→ ✅ **Evidence Snapshot imefafanuliwa** kama immutable point-in-time view ya Evidence Set "
             "(Q1/Q2), readiness imekokotolewa as-of T pamoja na temporal-conflict gate (Q3), temporal "
             "conflict imetenganishwa na structural (Q4, P74), na **Snapshot = canonical Decision-Layer "
             "input** (Q5, P79). **Evidence Layer sasa KAMILI**: Object→Operations→Set→Snapshot. Decision "
             "Engine itakuwa consumer mdogo wa snapshot. **Hakuna Decision Engine bado.** NO ML.")
    L.append("\n**Bado Decision Science D3 — hakuna decision-action wala alpha.** Snapshot ni picha ya "
             "ushahidi, sio uamuzi wala edge.")

    # HONEST CAVEATS
    L.append("\n## Honest Caveats\n")
    L.append("1. **Snapshot inatumia age-shift sare** (huongeza bars sawa kwa wote) — kiuhalisia kila member "
             "ina as-of timestamp yake; snapshot ya production inahitaji per-member event-time, sio shift moja.")
    L.append("2. **Temporal conflict = median-age split rahisi** — ni proxy ya P74, sio model kamili ya "
             "regime-change; inaweza kukosa contradictions za polepole au kuripoti za bahati kwa n ndogo.")
    L.append("3. **Reliability bado = Φ(EV/SE)** (P70 OPEN) — inajaa kwa support kubwa; 'reliability' ni jina "
             "la muda hadi confidence-model rasmi ifungwe.")
    L.append("4. **Redundancy (P78 OPEN) haijashughulikiwa** — snapshot ina dedupe ya identity tu; members "
             "correlated (EURUSD H1 vs H4) bado huhesabiwa mara mbili → reliability optimistic.")
    L.append("5. **Snapshot ≠ edge (P69).** Evidence Layer kamili ni infrastructure inayoauditika; "
             "haithibitishi alpha. Decision-ready snapshot bado si trade-ready.")

    L.append("\n*Evidence Snapshot = immutable as-of-T view ya Evidence Set; readiness @T + temporal-conflict "
             "gate; temporal vs structural conflict; canonical Decision-Layer input (P79). Principle 76–79. "
             "NO Decision Engine. NO ML. Profitable ≠ Tradable Edge.*")

    out = REPO_ROOT / c["paths"]["reports"] / "evidence_snapshot_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)} ({len(sets)} snapshots)")
    return 0


def self_test():
    mk = lambda v, src, age: make_evidence(v, 0.3, 300, 0.1, age, src)

    # (1) snapshot fields + Q5 canonical input
    s = make_set([mk(2.0, "a", 10), mk(2.1, "b", 20)], "e")
    snap = make_snapshot(s, as_of=0)
    ok_fields = all(k in snap for k in ("as_of", "n_live", "reliability", "readiness",
                                        "temporal_conflict", "structural_conflict", "provenance"))
    print(f"snapshot fields: {ok_fields} (n_live={snap['n_live']}, ready={snap['readiness']}) -> {'OK' if ok_fields else 'FAIL'}")

    # (2) readiness flips with as_of (expiry) — P73
    r0 = make_snapshot(s, 0)["readiness"]; rT = make_snapshot(s, TTL_BARS + 5)["readiness"]
    ok_ready = r0 and not rT
    print(f"readiness as-of: now={r0} TTL+={rT} -> {'OK' if ok_ready else 'FAIL'}")

    # (3) temporal conflict (P74): older +, newer − → contradiction; agree → 0
    contra = make_set([mk(1.0, "old1", 60), mk(1.0, "old2", 50), mk(-1.0, "new1", 5), mk(-1.0, "new2", 8)], "c")
    sc = make_snapshot(contra, 0)
    agree = make_set([mk(1.0, "o", 60), mk(1.0, "n", 5)], "g")
    sa = make_snapshot(agree, 0)
    ok_temp = sc["temporal_conflict"] >= CONFLICT_CEIL and sa["temporal_conflict"] < CONFLICT_CEIL
    print(f"temporal conflict: contradiction={sc['temporal_conflict']:.2f} agree={sa['temporal_conflict']:.2f} -> {'OK' if ok_temp else 'FAIL'}")

    # (4) temporal contradiction removes readiness even if set otherwise strong
    ok_temp_ready = (not sc["readiness"]) and "temporal" in sc["why"]
    print(f"temporal gates readiness: ready={sc['readiness']} why={sc['why']} -> {'OK' if ok_temp_ready else 'FAIL'}")

    # (5) decision_input returns a snapshot (P79)
    di = decision_input(s, 0)
    ok_input = di.get("as_of") == 0 and "readiness" in di
    print(f"decision_input = snapshot: {ok_input} -> {'OK' if ok_input else 'FAIL'}")

    ok = ok_fields and ok_ready and ok_temp and ok_temp_ready and ok_input
    print(f"\nSELF-TEST: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    c = cfg()
    return run(c["pairs"], np.random.default_rng(3))


if __name__ == "__main__":
    raise SystemExit(main())
