#!/usr/bin/env python3
"""Self-test ya EVAL-002 (L4) — stdlib pekee, haihitaji data (R-1 mitigation).

Mirror ya EVAL-001 selftest; tofauti: chanzo = Permanent Truths + findings APPROVED, hivyo
maps_to_lesson ni OPTIONAL (truths kadhaa hazina lesson bado — mf. T6/T11/T12).

Inakagua:
  [1] kila line ni JSON halali; fields za lazima zipo
  [2] ids unique, prefix EVAL-002-
  [3] options 4 (A-D); answer ni key halali
  [4] provenance ina report/doc iliyopo repo
  [5] maps_to_lesson: ikiwa si null NA inaanza 'LESSON-', LAZIMA iwe kwenye LESSON_INDEX.md
  [6] control_type negative|positive; angalau moja ya kila aina
  [7] BIAS: answer distribution (si letter moja >60%); length bias WARN
Exit 0 = PASS; exit 1 = FAIL ya muundo.
"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
QFILE = Path(__file__).resolve().parent / "questions.jsonl"
INDEX = ROOT / "docs" / "lessons" / "LESSON_INDEX.md"
REQUIRED = ("id", "control_type", "truth", "prompt", "options", "answer",
            "ground_truth", "rubric", "provenance")


def main() -> int:
    errors, warns = [], []
    index_text = INDEX.read_text(encoding="utf-8")
    rows = []
    for lineno, line in enumerate(QFILE.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append((lineno, json.loads(line)))
        except json.JSONDecodeError as e:
            errors.append(f"[1] line {lineno}: JSON invalid ({e})")

    seen = set()
    answers, longest_hits, control_types = [], 0, Counter()
    for lineno, q in rows:
        for f in REQUIRED:
            if f not in q:
                errors.append(f"[1] {q.get('id', f'line {lineno}')}: field '{f}' haipo")
        qid = q.get("id", "")
        if qid in seen:
            errors.append(f"[2] duplicate id: {qid}")
        seen.add(qid)
        if not qid.startswith("EVAL-002-"):
            errors.append(f"[2] id prefix mbaya: {qid}")
        opts = q.get("options", {})
        if sorted(opts) != ["A", "B", "C", "D"]:
            errors.append(f"[3] {qid}: options si A-D nne: {sorted(opts)}")
        ans = q.get("answer")
        if ans not in opts:
            errors.append(f"[3] {qid}: answer '{ans}' haipo kwenye options")
        else:
            answers.append(ans)
            if opts and len(opts[ans]) == max(len(v) for v in opts.values()):
                longest_hits += 1
        prov = q.get("provenance", {})
        ref = prov.get("report") or prov.get("doc")
        if not ref:
            errors.append(f"[4] {qid}: provenance haina report/doc")
        elif not (ROOT / ref).is_file():
            errors.append(f"[4] {qid}: provenance file haipo: {ref}")
        lid = q.get("maps_to_lesson")
        if lid and lid.startswith("LESSON-"):
            if lid.split("@")[0] not in index_text:
                errors.append(f"[5] {qid}: maps_to_lesson {lid} haipo LESSON_INDEX.md")
        ct = q.get("control_type")
        if ct not in ("negative", "positive"):
            errors.append(f"[6] {qid}: control_type batili: {ct!r}")
        else:
            control_types[ct] += 1

    n = len(rows)
    if control_types.get("positive", 0) == 0:
        errors.append("[6] hakuna positive control")
    if control_types.get("negative", 0) == 0:
        errors.append("[6] hakuna negative control")
    dist = Counter(answers)
    if n and max(dist.values()) / n > 0.60:
        warns.append(f"[7] answer position degenerate ({dict(dist)}) -> scorer LAZIMA a-shuffle")
    if n and longest_hits == n:
        warns.append(f"[7] chaguo sahihi ni refu zaidi kila mara ({n}/{n}) -> rubric-grader ndio default")

    print(f"questions={n} unique_ids={len(seen)} controls={dict(control_types)} "
          f"answer_dist={dict(sorted(dist.items()))} longest_is_answer={longest_hits}/{n}")
    for w in warns:
        print("  WARN " + w)
    if errors:
        print(f"\nSELF-TEST: FAIL ({len(errors)} errors)")
        for e in errors:
            print("  " + e)
        return 1
    print(f"\nSELF-TEST: PASS ({len(warns)} warnings)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
