"""
run_selftests.py — endesha self-test za modules zote (cross-platform: Windows/Linux/Mac).

Badala ya bash loop (haifanyi kazi Windows CMD), hii inaita kila module kwa subprocess na
inatoa muhtasari. Endesha kutoka src/research:  python run_selftests.py
"""
from __future__ import annotations

import subprocess
import sys

MODULES = ["frozen", "decision_object", "evidence_snapshot", "decision_policy", "decision_engine",
           "integrity_gate", "execution_object", "decision_repository", "broker_adapter",
           "e2e_paper_demo"]


def main():
    results = []
    for m in MODULES:
        flag = "--run" if m == "e2e_paper_demo" else "--self-test"
        try:
            out = subprocess.run([sys.executable, f"{m}.py", flag],
                                 capture_output=True, text=True, timeout=180)
            txt = out.stdout + out.stderr
            ok = ("SELF-TEST: PASS" in txt) or ("SMOKE TEST: PASS" in txt)
        except Exception as e:
            ok = False
            txt = str(e)
        results.append((m, ok))
        print(f"  {'PASS' if ok else 'FAIL'}  {m}")
        if not ok:
            print("    --- output ya mwisho ---")
            print("    " + "\n    ".join(txt.strip().splitlines()[-8:]))

    passed = sum(1 for _, ok in results if ok)
    print(f"\n{'=' * 50}")
    print(f"SELF-TEST SWEEP: {passed}/{len(results)} PASS")
    print("=" * 50)
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
