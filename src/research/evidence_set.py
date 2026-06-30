"""
evidence_set.py — DECISION SCIENCE PHASE D2 (Chief Quant).

D0 (Evidence Object) + D1 (Evidence Operations) = Evidence Layer. Chief: Decision Engine
HAITAWAHI kuona object MOJA — itaona **collection**. Maamuzi ya kweli yanatokana na mkusanyiko
wa ushahidi unaoweza kupimwa/kuagizwa/kukaguliwa kwa pamoja.

  Principle 71: evidence transformations ni PURE/deterministic/side-effect-free.
  Principle 72: provenance ni GRAPH yenye mwelekeo, sio log ya tarehe tu.
  Principle 73: decision-readiness ni ya **Evidence Snapshot**, sio object immutable.
  Principle 74 (OPEN): tofautisha temporal contradiction na structural disagreement.
  Principle 75: Evidence Objects ni VALUE OBJECTS wenye immutable identity.

Architecture mpya: Evidence Objects → **Evidence Sets** → Decision → Execution.

Maswali (Chief, D2):
  Q1. Evidence Collection ni nini?
  Q2. Ordering ina maana?
  Q3. Duplicate Evidence inatibiwa vipi?
  Q4. Evidence Set ina confidence yake?
  Q5. Evidence Set ina readiness yake? (snapshot — P73)

Mbinu: fasili EvidenceSet (keyed by value-object id, P75); onyesha aggregate ni order-invariant
(Q2) lakini provenance ni order-sensitive; dedupe by id (Q3); set-confidence = aggregate (Q4);
set-readiness = SNAPSHOT as-of time (Q5, P73). Provenance graph (P72). NO Decision Engine. NO ML.

Reuse: evidence_object (make_evidence, is_expired, decision_ready, CONFLICT_CEIL, TTL_BARS,
STALE_BARS, _freshness), evidence_operations (op_aggregate, conflict_taxonomy,
build_tagged_evidence), market_state_engine (cfg).

Output: reports/evidence_set_report.md
Self-test: python src/research/evidence_set.py --self-test
"""
from __future__ import annotations

import argparse, sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np

from market_state_engine import cfg
from evidence_object import (make_evidence, is_expired, decision_ready, _freshness,
                             CONFLICT_CEIL, TTL_BARS, STALE_BARS)
from evidence_operations import op_aggregate, conflict_taxonomy, build_tagged_evidence

REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------- Evidence Set (collection keyed by value-object identity, P75) ----------
def make_set(eos, label="set"):
    """Q1/Q3: Evidence Collection = dedup by id (value-object identity, P75). Ordering haihifadhiwi
    kwa identity (Q2: set semantics); provenance/order huhifadhiwa kando."""
    by_id = {}
    dups = 0
    for e in eos:
        if e["id"] in by_id:
            dups += 1
        else:
            by_id[e["id"]] = e
    return {"label": label, "members": list(by_id.values()), "n_in": len(eos),
            "n_unique": len(by_id), "duplicates": dups}


def set_aggregate(evset):
    """Q4: set-level Evidence Object (confidence ya SET) = op_aggregate ya members (live)."""
    return op_aggregate(evset["members"])


def set_snapshot(evset, now_bars):
    """Q5/P73: SNAPSHOT as-of `now_bars` — recompute freshness/expiry ya kila member kulingana na
    muda wa sasa, kisha readiness ya set. Readiness ni property ya snapshot, SIO ya object."""
    snap = []
    for e in evset["members"]:
        age = e["age_bars"] + int(now_bars)
        snap.append(make_evidence(e["value"], e["uncertainty"], e["support"], e["coverage"],
                                  age, e["source"], conflict=e["conflict"]))
    agg = op_aggregate(snap)
    ready, why = decision_ready(agg) if agg is not None else (False, "no live evidence")
    live = sum(1 for e in snap if not is_expired(e))
    return {"now_bars": int(now_bars), "agg": agg, "ready": ready, "why": why, "live": live,
            "n": len(snap)}


def provenance_graph(eos):
    """P72: directed provenance graph — nodes (ids), edges (parent → child)."""
    nodes = set(); edges = []
    for e in eos:
        nodes.add(e["id"])
        for p in e.get("parents", []):
            nodes.add(p); edges.append((p, e["id"]))
    return nodes, edges


def run(pairs, rng):
    c = cfg()
    print("Building tagged evidence then Evidence Sets per event...", flush=True)
    tagged, no_px = build_tagged_evidence(pairs)
    if no_px:
        print("HITILAFU: state parquet haina OHLC. Endesha market_state_engine.py kwanza.", file=sys.stderr)
        return 1
    if len(tagged) < 4:
        print("HITILAFU: evidence haitoshi.", file=sys.stderr)
        return 1
    by_event = defaultdict(list)
    for e, t in tagged:
        by_event[t["engine"]].append(e)
    sets = {ev: make_set(eos, label=ev) for ev, eos in by_event.items()}
    return _report(c, pairs, tagged, sets)


def _report(c, pairs, tagged, sets):
    L = ["# Evidence Sets — Decision hutokea juu ya COLLECTION, sio object moja (Decision Science D2)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | {len(pairs)} pairs, {len(tagged)} evidence objects, "
         f"{len(sets)} sets (per event) | value-object identity + snapshot readiness | NO Decision Engine | NO ML*\n",
         "> **P71** transformations pure. **P72** provenance = graph. **P73** readiness = snapshot, sio "
         "object. **P74 (OPEN)** temporal vs structural conflict. **P75** Evidence = value objects wenye "
         "immutable identity. Architecture: Evidence Objects → **Evidence Sets** → Decision → Execution."]

    # Q1 + Q3 — collection & duplicates
    L.append("\n## Q1+Q3 — Evidence Collection (keyed by value-object identity) + duplicates\n")
    L.append("| set (event) | n in | n unique | duplicates removed |")
    L.append("|-------------|------|----------|--------------------|")
    for ev in sorted(sets):
        s = sets[ev]
        L.append(f"| {ev} | {s['n_in']} | {s['n_unique']} | {s['duplicates']} |")
    L.append("\n- **Q1:** Evidence Set = collection ya Evidence Objects keyed by **id** (P75 value-object "
             "identity). **Q3:** duplicate (id ile ile = content ile ile) huondolewa moja kwa moja.")

    # Q2 — ordering
    L.append("\n## Q2 — Ordering ina maana?\n")
    ev0 = sorted(sets)[0]; mem = sets[ev0]["members"]
    a1 = set_aggregate({"members": mem})
    a2 = set_aggregate({"members": list(reversed(mem))})
    order_inv = a1 is not None and a2 is not None and abs(a1["value"] - a2["value"]) < 1e-9
    L.append(f"- set-aggregate (inverse-variance) ni **order-INVARIANT**: value {a1['value']:+.4f} vs "
             f"reversed {a2['value']:+.4f} → {'✅ haina tofauti' if order_inv else '❌ inatofautiana'}.")
    L.append("- **Hitimisho:** kwa AGGREGATION ordering haina maana (set semantics); kwa **provenance/"
             "audit** ordering ina maana (graph ina mwelekeo, P72). Set = unordered kwa thamani, ordered kwa lineage.")

    # Q4 — set confidence
    L.append("\n## Q4 — Evidence Set ina confidence yake?\n")
    L.append("| set | members(live) | set value | set uncertainty | set confidence | set conflict |")
    L.append("|-----|---------------|-----------|-----------------|----------------|--------------|")
    for ev in sorted(sets):
        agg = set_aggregate(sets[ev])
        if agg is None:
            L.append(f"| {ev} | 0 | — | — | — | — |")
            continue
        live = sum(1 for e in sets[ev]["members"] if not is_expired(e))
        L.append(f"| {ev} | {live} | {agg['value']:+.3f} | {agg['uncertainty']:.3f} | "
                 f"{agg['confidence']:.2f} | {agg['conflict']:.2f} |")
    L.append("\n- **Q4:** ndio — set ina confidence YAKE = aggregate ya members (P68 operation). Set-"
             "confidence ni property ya SET, inayotokana na members + conflict kati yao.")

    # Q5 — set readiness as snapshot (P73)
    L.append("\n## Q5 — Evidence Set ina readiness yake? (SNAPSHOT — P73)\n")
    L.append("| set | now=0 (ready?) | now=+stale | now=+TTL (expired) |")
    L.append("|-----|----------------|------------|--------------------|")
    for ev in sorted(sets):
        s0 = set_snapshot(sets[ev], 0)
        s1 = set_snapshot(sets[ev], STALE_BARS + 1)
        s2 = set_snapshot(sets[ev], TTL_BARS + 1)
        L.append(f"| {ev} | {s0['ready']} ({s0['why']}) | {s1['ready']} | {s2['ready']} (live {s2['live']}) |")
    L.append("\n- **Q5/P73:** readiness ni ya **SNAPSHOT** (as-of time), SIO ya Evidence Object immutable. "
             "Set ile ile ina readiness tofauti kwa nyakati tofauti — object haibadiliki, snapshot ndio hubadilika.")

    # provenance graph (P72) demo
    L.append("\n## P72 — Provenance graph (demo)\n")
    agg_demo = set_aggregate(sets[sorted(sets)[0]])
    nodes, edges = provenance_graph((sets[sorted(sets)[0]]["members"] + ([agg_demo] if agg_demo else [])))
    L.append(f"- set `{sorted(sets)[0]}`: nodes {len(nodes)}, edges {len(edges)} "
             f"(aggregate ina parents {len(agg_demo['parents']) if agg_demo else 0} → graph, sio list).")

    # conflict taxonomy (carry from D1, P74 note)
    tax = conflict_taxonomy(tagged)
    L.append("\n## Conflict taxonomy (D1 carry) + P74 note\n")
    L.append("| dimension | score |")
    L.append("|-----------|-------|")
    for k in ["intra (split-half)", "cross-pair", "cross-timeframe", "cross-engine"]:
        L.append(f"| {k} | {tax.get(k,0.0):.2f} |")
    L.append("\n- **P74 (OPEN):** temporal contradiction (evidence ya jana bullish vs leo bearish) bado "
             "haijatenganishwa na structural disagreement — ni kazi ya baadaye (intra hapa ni split-half, sio temporal).")

    # VERDICT
    L.append("\n## VERDICT — D2 Evidence Sets\n")
    L.append(f"→ ✅ **Evidence Set imefafanuliwa**: collection keyed by value-object identity (Q1/Q3 dedup, "
             f"P75); aggregate **order-invariant** (Q2); set ina **confidence yake** (Q4); set ina **readiness "
             f"ya SNAPSHOT** (Q5, P73 — inabadilika kwa muda, object haibadiliki); provenance ni **graph** "
             "(P72). Evidence Layer (Object→Operations→Set) sasa kamili — Decision Engine itafanya kazi juu ya "
             "**sets**, sio objects. **Hakuna Decision Engine bado.** NO ML.")
    L.append("\n**Bado Decision Science D2 — hakuna decision-action wala alpha.** Evidence Layer ni "
             "infrastructure; Decision (juu ya sets) ni hatua inayofuata baada ya Chief kuidhinisha.")

    # HONEST CAVEATS
    L.append("\n## Honest Caveats\n")
    L.append("1. **Set-confidence inarithi caveat za aggregate** — inverse-variance inadhani independence; "
             "members (pair×tf za event moja) zina correlation → set-uncertainty ni optimistic.")
    L.append("2. **Dedup by content-hash identity** — near-duplicates (value ~sawa lakini si sawa kabisa) "
             "HAZIondolewi; identity ni exact-content, sio fuzzy. Hii ni sahihi kwa value object lakini "
             "haishughulikii redundancy ya kistatistiki.")
    L.append("3. **Snapshot readiness inatumia age-shift rahisi** (huongeza bars kwa wote sawa) — kiuhalisia "
             "kila member ina recency yake; snapshot halisi inahitaji as-of timestamps per member.")
    L.append("4. **P74 temporal conflict HAIJATEKELEZWA** — 'intra' hapa ni split-half (structural), sio "
             "temporal contradiction (jana vs leo). Decision Engine itahitaji tofauti hii kabla ya kuamua.")
    L.append("5. **Set ≠ edge.** Evidence Layer inapanga ushahidi kwa muundo unaoauditika; haithibitishi "
             "alpha. Decision-ready set bado si trade-ready (P69).")

    L.append("\n*Evidence Set: dedup by value-object id (P75); order-invariant aggregate; set-confidence; "
             "snapshot readiness (P73); provenance graph (P72); pure ops (P71). NO Decision Engine. NO ML. "
             "Profitable ≠ Tradable Edge.*")

    out = REPO_ROOT / c["paths"]["reports"] / "evidence_set_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)} ({len(sets)} sets, {len(tagged)} objects)")
    return 0


def self_test():
    mk = lambda v, s, src, age=10: make_evidence(v, s, 300, 0.1, age, src)
    a = mk(1.0, 0.3, "P1:H1:e"); b = mk(1.2, 0.3, "P2:H1:e"); c = mk(0.9, 0.3, "P3:H1:e")

    # (1) collection + dedup (Q1/Q3): adding identical object haiongezi unique
    s = make_set([a, b, c, a, b], label="e")
    ok_dedup = s["n_unique"] == 3 and s["duplicates"] == 2
    print(f"collection/dedup: n_in={s['n_in']} unique={s['n_unique']} dups={s['duplicates']} -> {'OK' if ok_dedup else 'FAIL'}")

    # (2) ordering invariance (Q2)
    a1 = set_aggregate({"members": [a, b, c]}); a2 = set_aggregate({"members": [c, b, a]})
    ok_order = abs(a1["value"] - a2["value"]) < 1e-9
    print(f"order-invariance: {a1['value']:.4f} vs {a2['value']:.4f} -> {'OK' if ok_order else 'FAIL'}")

    # (3) set confidence (Q4): agreeing set -> uncertainty < member
    ok_conf = a1["uncertainty"] < a["uncertainty"] and 0 <= a1["confidence"] <= 1
    print(f"set confidence: set_unc={a1['uncertainty']:.3f} < member {a['uncertainty']:.3f} -> {'OK' if ok_conf else 'FAIL'}")

    # (4) snapshot readiness (Q5/P73): ready now, not ready after TTL
    big = make_set([mk(2.0, 0.3, "x"), mk(2.1, 0.3, "y")], "big")
    r0 = set_snapshot(big, 0)["ready"]; rT = set_snapshot(big, TTL_BARS + 5)["ready"]
    ok_snap = r0 and not rT
    print(f"snapshot readiness: now={r0} TTL+={rT} -> {'OK' if ok_snap else 'FAIL'}")

    # (5) provenance graph (P72): aggregate ina parents -> edges
    nodes, edges = provenance_graph([a, b, a1])
    ok_graph = len(edges) == len(a1["parents"]) and len(a1["parents"]) >= 2
    print(f"provenance graph: nodes={len(nodes)} edges={len(edges)} agg-parents={len(a1['parents'])} -> {'OK' if ok_graph else 'FAIL'}")

    ok = ok_dedup and ok_order and ok_conf and ok_snap and ok_graph
    print(f"\nSELF-TEST: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    c = cfg()
    return run(c["pairs"], np.random.default_rng(2))


if __name__ == "__main__":
    raise SystemExit(main())
