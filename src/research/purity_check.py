"""
purity_check.py — P107 TRANSITIVE-PURITY COMPLIANCE TEST (Chief ruling c, 2026-07-07).

Audit #5 gap (P104): self-test [4] + 4-point review vinapima DIRECT imports pekee — regression ya
**transitive** purity haitakamatwa. Hii inaziba gap: inathibitisha kwamba core ya Track A
(Engine/Gate/Execution/Repository/Adapter + decision_object + frozen) ina-**load** kwa stdlib+frozen
PEKEE — bila numpy/polars/duckdb/market_state_engine/evidence_*.

Njia: kila module inaimportwa kwenye **subprocess safi** yenye import-guard inayozuia market/heavy
modules. Ikipakia → PURE. Ikianguka kwa ImportError ya module iliyozuiwa → IMPURE (transitive leak).
Negative control (`decision_policy`, ambayo ni impure kwa makusudi) LAZIMA ianguke — inathibitisha
guard inafanya kazi kweli (test si no-op).

Stdlib PEKEE (subprocess/sys/os). ASCII-safe (Windows cp1252). Chief: iongezwe run_selftests.py.
Self-test: python src/research/purity_check.py --self-test
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

# core ya Track A ambayo LAZIMA iwe transitively pure (inayotumika kwenye pipeline ya production)
CORE = ("frozen", "decision_object", "decision_engine", "integrity_gate",
        "execution_object", "decision_repository", "broker_adapter")
# module za market/heavy ambazo core HAIPASWI kuzihitaji ku-load
BLOCKED = ("numpy", "polars", "duckdb", "yaml", "market_state_engine", "event_library",
           "evidence_object", "evidence_snapshot", "evidence_operations", "evidence_set",
           "configuration_engine", "latent_structure")
# impure kwa makusudi (demo/policy) — negative control: LAZIMA ianguke chini ya guard
IMPURE_CONTROL = ("decision_policy",)

_PROBE = """
import builtins
_real = builtins.__import__
BLOCK = {block!r}
def _guard(name, *a, **k):
    if name.split('.')[0] in BLOCK:
        raise ImportError('P107-blocked: ' + name)
    return _real(name, *a, **k)
builtins.__import__ = _guard
import {mod}
"""


def load_is_pure(mod):
    """Jaribu ku-import `mod` kwenye subprocess safi yenye guard. Rudisha (pure_bool, detail)."""
    code = _PROBE.format(block=set(BLOCKED), mod=mod)
    here = os.path.dirname(os.path.abspath(__file__))
    r = subprocess.run([sys.executable, "-c", code], cwd=here,
                       capture_output=True, text=True, timeout=120)
    if r.returncode == 0:
        return True, "loaded"
    last = (r.stderr or "").strip().splitlines()
    return False, (last[-1] if last else "non-zero exit")


def self_test():
    ok_all = True
    print("P107 transitive-purity compliance (core = stdlib + frozen PEKEE):")
    for m in CORE:
        pure, detail = load_is_pure(m)
        ok_all &= pure
        print(f"  [{'PURE' if pure else 'LEAK'}]  {m:22} {'' if pure else '-> ' + detail}")

    # negative control: impure module LAZIMA ianguke (guard inafanya kazi -> test si no-op)
    ctrl_ok = True
    for m in IMPURE_CONTROL:
        pure, _ = load_is_pure(m)
        caught = not pure
        ctrl_ok &= caught
        print(f"  [ctrl:{'OK' if caught else 'BAD'}] {m:22} (impure -> lazima ianguke chini ya guard)")
    ok_all &= ctrl_ok

    print(f"\nSELF-TEST: {'PASS' if ok_all else 'FAIL'}")
    return 0 if ok_all else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.parse_args()
    return self_test()   # module hii ni compliance test yenyewe — daima inaendesha check


if __name__ == "__main__":
    raise SystemExit(main())
