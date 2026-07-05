#!/usr/bin/env python3
"""Self-test ya EVAL-SUITE (L4) — stdlib pekee, haihitaji data (R-1 mitigation).

Inakagua manifest ya suite dhidi ya members halisi, na inaendesha self-test ya kila member:
  [1] SUITE.json inasomeka; fields za lazima zipo
  [2] kila member: dir + questions.jsonl zipo; idadi ya maswali inalingana na manifest
  [3] control counts (negative/positive) za manifest zinalingana na questions.jsonl halisi
  [4] total_questions + total_controls zinalingana na jumla ya members
  [5] kila member eval_selftest.py inarudi PASS (exit 0)
Exit 0 = PASS; exit 1 = FAIL.
"""
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SUITE = HERE / "SUITE.json"


def count_member(qfile: Path):
    n, ctrl = 0, Counter()
    for line in qfile.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        q = json.loads(line)
        n += 1
        ctrl[q.get("control_type")] += 1
    return n, ctrl


def main() -> int:
    errors = []
    suite = json.loads(SUITE.read_text(encoding="utf-8"))
    for f in ("id", "members", "total_questions", "total_controls", "scoring_protocol"):
        if f not in suite:
            errors.append(f"[1] SUITE.json: field '{f}' haipo")

    agg_n, agg_ctrl = 0, Counter()
    for m in suite.get("members", []):
        mdir = ROOT / m["dir"]
        qfile = mdir / "questions.jsonl"
        if not qfile.is_file():
            errors.append(f"[2] {m['id']}: questions.jsonl haipo ({qfile})")
            continue
        n, ctrl = count_member(qfile)
        if n != m.get("questions"):
            errors.append(f"[2] {m['id']}: questions manifest={m.get('questions')} halisi={n}")
        for k in ("negative", "positive"):
            if ctrl.get(k, 0) != m.get("controls", {}).get(k):
                errors.append(f"[3] {m['id']}: control '{k}' manifest={m.get('controls', {}).get(k)} halisi={ctrl.get(k, 0)}")
        agg_n += n
        agg_ctrl += ctrl
        # [5] member self-test
        st = mdir / "eval_selftest.py"
        if st.is_file():
            r = subprocess.run([sys.executable, str(st)], capture_output=True, text=True)
            if r.returncode != 0:
                errors.append(f"[5] {m['id']}: eval_selftest FAIL\n{r.stdout}{r.stderr}")

    if agg_n != suite.get("total_questions"):
        errors.append(f"[4] total_questions manifest={suite.get('total_questions')} halisi={agg_n}")
    for k in ("negative", "positive"):
        if agg_ctrl.get(k, 0) != suite.get("total_controls", {}).get(k):
            errors.append(f"[4] total_controls '{k}' manifest={suite.get('total_controls', {}).get(k)} halisi={agg_ctrl.get(k, 0)}")

    print(f"suite={suite.get('id')} members={len(suite.get('members', []))} "
          f"total_questions={agg_n} controls={dict(agg_ctrl)}")
    if errors:
        print(f"\nSUITE SELF-TEST: FAIL ({len(errors)} errors)")
        for e in errors:
            print("  " + e)
        return 1
    print("\nSUITE SELF-TEST: PASS (members zote PASS)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
