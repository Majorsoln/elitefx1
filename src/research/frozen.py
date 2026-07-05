"""
frozen.py — A-4 IMMUTABILITY ENFORCEMENT (Execution Science E2; Chief ruling Q4, 2026-07-05).

Objects za domain (Decision/Execution) zimekuwa immutable **kwa makubaliano** tu (Python dicts);
hakuna kilichozuia mutation ya bahati mbaya (`obj["lifecycle"]="X"`). A-4/R-5: enforcement halisi.
Chief E2 Q4: **(b) stdlib deep-freeze()** — hakuna dependency mpya (Rule 4/P107 — stdlib PEKEE),
dict-compatible. `make_*` za Decision+Execution zinaita `freeze()` mwishoni.

Semantics:
  dict            → types.MappingProxyType (read-only view; __setitem__ inaraise TypeError)
  list/tuple      → tuple (immutable) ya values zilizo-frozen (recursive)
  set/frozenset   → frozenset ya values zilizo-frozen
  scalar/None     → kama ilivyo (tayari immutable)
Idempotent: freeze(freeze(x)) == freeze(x). NB: list→tuple ni **mabadiliko ya aina** ya makusudi
(consumers wanaolinganisha na list wa-coerce kwa list()).

Evidence Layer HAIGUSWI hapa (interface-frozen — P90; retrofit = uamuzi tofauti wa Chief, E2 Q4).

Self-test: python src/research/frozen.py --self-test
"""
from __future__ import annotations

import argparse
from types import MappingProxyType


def freeze(obj):
    """Deep-freeze recursive → immutable structure (A-4). Tazama semantics kwenye docstring ya module."""
    if isinstance(obj, MappingProxyType):
        return obj                                            # tayari frozen (idempotent)
    if isinstance(obj, dict):
        return MappingProxyType({k: freeze(v) for k, v in obj.items()})
    if isinstance(obj, (list, tuple)):
        return tuple(freeze(v) for v in obj)
    if isinstance(obj, (set, frozenset)):
        return frozenset(freeze(v) for v in obj)
    return obj                                                # scalar/None — immutable tayari


def is_frozen(obj):
    """True kama obj (na watoto wake) hawawezi ku-mutate kimuundo."""
    if isinstance(obj, MappingProxyType):
        return all(is_frozen(v) for v in obj.values())
    if isinstance(obj, tuple):
        return all(is_frozen(v) for v in obj)
    if isinstance(obj, frozenset):
        return all(is_frozen(v) for v in obj)
    if isinstance(obj, (dict, list, set)):
        return False                                          # mutable containers
    return True                                               # scalar/None


# ---------------------------------------------------------------- self-test (Rule 7)
def self_test():
    ok_all = True

    # (1) top-level mutation inazuiwa (TypeError)
    f = freeze({"lifecycle": "PROPOSED", "id": "dec:1"})
    try:
        f["lifecycle"] = "VALIDATED"; blocked = False
    except TypeError:
        blocked = True
    ok = blocked and f["lifecycle"] == "PROPOSED"
    ok_all &= ok
    print(f"[1] top-level mutation blocked: {blocked} value-intact={f['lifecycle']=='PROPOSED'} -> {'OK' if ok else 'FAIL'}")

    # (2) nested mutation inazuiwa (dict→proxy, list→tuple)
    f2 = freeze({"audit": ["a"], "integrity": {"state": "READY"}, "refs": ["snap:1"]})
    b_list = isinstance(f2["audit"], tuple)
    b_dict = isinstance(f2["integrity"], MappingProxyType)
    try:
        f2["integrity"]["state"] = "X"; nested_blocked = False
    except TypeError:
        nested_blocked = True
    ok = b_list and b_dict and nested_blocked
    ok_all &= ok
    print(f"[2] nested: list→tuple={b_list} dict→proxy={b_dict} nested-mutation-blocked={nested_blocked} -> {'OK' if ok else 'FAIL'}")

    # (3) idempotent + is_frozen
    ok = freeze(f) is not None and is_frozen(f2) and freeze(freeze({"x": [1, 2]})) == freeze({"x": [1, 2]})
    ok_all &= ok
    print(f"[3] idempotent + is_frozen: {is_frozen(f2)} -> {'OK' if ok else 'FAIL'}")

    # (4) values readable + scalars untouched
    ok = f2["refs"] == ("snap:1",) and freeze(5) == 5 and freeze(None) is None and freeze("x") == "x"
    ok_all &= ok
    print(f"[4] readable + scalars: refs={f2['refs']} -> {'OK' if ok else 'FAIL'}")

    # (5) not frozen: plain dict/list report False
    ok = (not is_frozen({"a": 1})) and (not is_frozen([1])) and is_frozen(("a",)) and is_frozen(5)
    ok_all &= ok
    print(f"[5] is_frozen discriminates mutable vs immutable -> {'OK' if ok else 'FAIL'}")

    print(f"\nSELF-TEST: {'PASS' if ok_all else 'FAIL'}")
    return 0 if ok_all else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    print("frozen.py — freeze() util (A-4). Tumia --self-test.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
