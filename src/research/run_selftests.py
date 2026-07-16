"""
run_selftests.py — endesha self-test za modules zote (cross-platform: Windows/Linux/Mac).

Badala ya bash loop (haifanyi kazi Windows CMD), hii inaita kila module kwa subprocess na
inatoa muhtasari. Endesha kutoka src/research:  python run_selftests.py
"""
from __future__ import annotations

import os
import subprocess
import sys

MODULES = ["frozen", "decision_object", "evidence_snapshot", "decision_policy", "decision_engine",
           "integrity_gate", "execution_object", "decision_repository", "broker_adapter",
           "purity_check", "paper_trader", "event_library_v2", "event_quality_report",
           "strategy_lab", "failure_autopsy", "strat_signal", "strength_lab",
           "portfolio_v0", "cost_stress", "winrate_monitor", "family_pooled",
           "intraday_state_engine", "htf_context", "wave_c2a", "gold_spread_quality",
           "rmap", "e2e_paper_demo"]     # purity_check=P107; strategy_lab=S1(+R1 boot); WAVE-1 R4/R5/R6; intraday+htf=C2-0; wave_c2a=C2-3 (MZUNGUKO-2); false_break+gold=WAVE-B-prep; rmap=M3-1 (MZUNGUKO-3 atlas+swap+MFE/MAE)

# Windows CMD hutumia cp1252 kwa child stdout → herufi za Unicode (→ ≠ ✓) zinaanguka kwenye pipe.
# PYTHONUTF8=1 inalazimisha child zote ziwe UTF-8; encoding="utf-8" inasoma UTF-8 upande huu.
_ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}


def main():
    results = []
    for m in MODULES:
        flag = "--run" if m == "e2e_paper_demo" else "--self-test"
        try:
            out = subprocess.run([sys.executable, f"{m}.py", flag], env=_ENV,
                                 capture_output=True, encoding="utf-8", errors="replace", timeout=180)
            txt = (out.stdout or "") + (out.stderr or "")
            ok = ("SELF-TEST: PASS" in txt) or ("SMOKE TEST: PASS" in txt)
        except Exception as e:
            ok = False
            txt = str(e)
        results.append((m, ok))
        print(f"  {'PASS' if ok else 'FAIL'}  {m}")
        if not ok:
            print("    --- output ya mwisho ---")
            print("    " + "\n    ".join(txt.strip().splitlines()[-20:]))

    passed = sum(1 for _, ok in results if ok)
    print(f"\n{'=' * 50}")
    print(f"SELF-TEST SWEEP: {passed}/{len(results)} PASS")
    print("=" * 50)
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
