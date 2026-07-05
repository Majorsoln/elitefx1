#!/usr/bin/env python3
"""Self-test ya EVAL-001 (L4) — stdlib pekee, haihitaji data (R-1 mitigation).

Inakagua uadilifu wa muundo wa benchmark (SIO usahihi wa model — huo ni kazi ya scorer):
  [1] kila line ni JSON halali; fields zote za lazima zipo
  [2] ids ni unique na zina prefix EVAL-001-
  [3] options ni 4 (A-D); answer ni key halali ndani ya options
  [4] provenance ina report/doc iliyopo kwenye repo
  [5] maps_to_lesson ipo kwenye docs/lessons/LESSON_INDEX.md
  [6] control_type ni 'negative' au 'positive'; kuna angalau moja ya kila aina (positive controls
      hupima kama model inakataa KILA kitu kwa upofu — Chief directive 'dead ends + lessons ACTIVE')
  [7] BIAS: answer positions zimesambazwa (si letter moja kwa >60% ya maswali); chaguo sahihi
      SI refu zaidi kila mara. (Ikiwa degenerate -> WARN: scorer a-shuffle.)
Exit 0 = PASS; exit 1 = FAIL ya muundo.
"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
QFILE = Path(__file__).resolve().parent / "questions.jsonl"
INDEX = ROOT / "docs" / "lessons" / "LESSON_INDEX.md"
REQUIRED = ("id", "control_type", "dead_end", "prompt", "options", "answer",
            "ground_truth", "rubric", "provenance", "maps_to_lesson")


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
        if not qid.startswith("EVAL-001-"):
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
        lid = q.get("maps_to_lesson", "")
        short = lid.split("@")[0]
        if short and short not in index_text:
            errors.append(f"[5] {qid}: maps_to_lesson {lid} haipo LESSON_INDEX.md")
        ct = q.get("control_type")
        if ct not in ("negative", "positive"):
            errors.append(f"[6] {qid}: control_type batili: {ct!r}")
        else:
            control_types[ct] += 1

    n = len(rows)
    # [6] balance
    if control_types.get("positive", 0) == 0:
        errors.append("[6] hakuna positive control hata moja (model inaweza 'kufaulu' kwa kukataa kila kitu)")
    if control_types.get("negative", 0) == 0:
        errors.append("[6] hakuna negative control (dead end) hata moja")
    # [7] bias
    dist = Counter(answers)
    if n and max(dist.values()) / n > 0.60:
        warns.append(f"[7] answer position degenerate ({dict(dist)}) -> scorer LAZIMA a-shuffle")
    if n and longest_hits == n:
        warns.append(f"[7] chaguo sahihi ni refu zaidi kila mara ({n}/{n}) -> length bias; shuffle+normalize")

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
