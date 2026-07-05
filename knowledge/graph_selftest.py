#!/usr/bin/env python3
"""Self-test ya knowledge/graph.json (L2) — stdlib pekee, haihitaji data (R-1 mitigation).

Inakagua:
  [1] JSON inasomeka na ina meta/nodes/edges
  [2] node ids ni unique
  [3] kila edge endpoint ipo kwenye nodes; edge type imo kwenye meta.edge_types
  [4] kila lesson node ina >=1 derives-from edge (provenance ni lazima — K0)
  [5] lesson lifecycle kwenye graph inalingana na docs/lessons/LESSON_INDEX.md
  [6] kila node ya kind report/doc ina file iliyopo kwenye repo
Exit 0 = PASS; exit 1 = FAIL (na orodha ya makosa).
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GRAPH = ROOT / "knowledge" / "graph.json"
INDEX = ROOT / "docs" / "lessons" / "LESSON_INDEX.md"


def main() -> int:
    errors = []

    # [1] load
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    for key in ("meta", "nodes", "edges"):
        if key not in graph:
            errors.append(f"[1] '{key}' haipo kwenye graph.json")
    nodes, edges = graph.get("nodes", []), graph.get("edges", [])
    edge_types = set(graph.get("meta", {}).get("edge_types", {}))

    # [2] unique ids
    ids = [n["id"] for n in nodes]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        errors.append(f"[2] node ids duplicated: {sorted(dupes)}")
    id_set = set(ids)

    # [3] edge integrity
    for e in edges:
        for end in ("from", "to"):
            if e.get(end) not in id_set:
                errors.append(f"[3] edge endpoint haipo kwenye nodes: {e.get(end)!r} ({e})")
        if e.get("type") not in edge_types:
            errors.append(f"[3] edge type nje ya meta.edge_types: {e.get('type')!r}")

    # [4] kila lesson ina provenance edge
    lesson_ids = {n["id"] for n in nodes if n.get("kind") == "lesson"}
    derived = {e["from"] for e in edges if e.get("type") == "derives-from"}
    for lid in sorted(lesson_ids - derived):
        errors.append(f"[4] lesson bila derives-from edge: {lid}")

    # [5] lifecycle vs LESSON_INDEX.md
    index_lc = dict(
        re.findall(
            r"^\|\s*(LESSON-\d+@v\d+)\s*\|[^|]*\|[^|]*\|\s*(\w+)\s*\|",
            INDEX.read_text(encoding="utf-8"),
            re.M,
        )
    )
    for n in nodes:
        if n.get("kind") != "lesson":
            continue
        short = n["id"].split(":", 1)[1]
        want = index_lc.get(short)
        if want is None:
            errors.append(f"[5] {short} haipo kwenye LESSON_INDEX.md")
        elif n.get("lifecycle") != want:
            errors.append(f"[5] lifecycle mismatch {short}: graph={n.get('lifecycle')} index={want}")
    # Policy: graph LAZIMA iwe na kila lesson ACTIVE; CANDIDATE zinalinkwa zikiapruvishwa (pending OK).
    graph_shorts = {i.split(":", 1)[1] for i in lesson_ids}
    pending = []
    for short in sorted(set(index_lc) - graph_shorts):
        if index_lc[short] == "ACTIVE":
            errors.append(f"[5] ACTIVE lesson imo INDEX lakini haipo graph: {short}")
        else:
            pending.append(short)

    # [6] report/doc/eval files zipo
    for n in nodes:
        if n.get("kind") in ("report", "doc", "eval") and not (ROOT / n["file"]).is_file():
            errors.append(f"[6] file haipo: {n['file']} ({n['id']})")

    kinds = {}
    for n in nodes:
        kinds[n.get("kind")] = kinds.get(n.get("kind"), 0) + 1
    types = {}
    for e in edges:
        types[e.get("type")] = types.get(e.get("type"), 0) + 1
    print(f"nodes={len(nodes)} {kinds}")
    print(f"edges={len(edges)} {types}")
    if pending:
        print(f"pending (CANDIDATE lessons not yet linked, link on approval): {pending}")

    if errors:
        print(f"\nSELF-TEST: FAIL ({len(errors)} errors)")
        for err in errors:
            print("  " + err)
        return 1
    print("\nSELF-TEST: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
