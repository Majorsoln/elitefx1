"""
purged_cv.py — M4-1: PURGED + EMBARGOED cross-validation splitter (charter §4.2, RED LINE ya leakage).

KWA NINI (charter docs/CYCLE4_ML_CHARTER.md §4.2): labels zetu ni **triple-barrier** — label ya bar i
inategemea bei za bars [i+1, i+1+max_hold]. Kwa hiyo labels zinazokaribiana **zinapishana kwa muda**.
K-fold ya kawaida ingeweka label inayopishana na test-block ndani ya TRAIN -> model inaona bei za
kipindi cha test -> **leakage ni hakika**, si uwezekano. Kinga (López de Prado):

  1. **PURGE:** toa kwenye TRAIN kila label ambayo dirisha lake [t0, t1] **linagusa** dirisha la TEST.
  2. **EMBARGO:** toa pia labels zinazoanza mara tu **baada ya** TEST (serial correlation ya bei
     haikatiki kwenye mpaka). Default embargo = **horizon ya label yenyewe** (max_hold) — ndicho
     kipimo cha asili, si namba ya kubahatisha.

MUUNDO: folds ni **za MUDA** (si za row-index) ili pairs 12 zigawanywe kwa MPAKA MMOJA wa muda —
vinginevyo test ya pair A ingekuwa train ya pair B kwa tarehe ile ile (cross-pair leakage).

PURE: numpy pekee; hakuna I/O, hakuna data. Statistic HAKUNA (huu ni mgawanyo, si kipimo).
Self-test: python purged_cv.py --self-test
"""
from __future__ import annotations

import argparse
import sys

import numpy as np


def time_blocks(t0, n_folds):
    """Mipaka ya folds kwa MUDA: blocks n_folds zinazofuatana, kila moja na ~idadi sawa ya rows.
    Rudisha list ya (start, end) — half-open [start, end) isipokuwa ya mwisho (inajumuisha mwisho).
    Mipaka inaanguka kwenye quantiles za t0 (sio muda sawa) ili folds zisiwe tupu wakati data
    haijasambaa sawia."""
    t0 = np.asarray(t0)
    if n_folds < 2:
        raise ValueError("n_folds lazima iwe >= 2")
    if len(t0) < n_folds:
        raise ValueError(f"rows ({len(t0)}) chache kuliko folds ({n_folds})")
    s = np.sort(t0)
    edges = [s[0]]
    for k in range(1, n_folds):
        edges.append(s[int(round(k * len(s) / n_folds))])
    edges.append(s[-1])
    blocks = []
    for k in range(n_folds):
        blocks.append((edges[k], edges[k + 1]))
    return blocks


def purged_folds(t0, t1, n_folds=5, embargo=None):
    """Rudisha list ya (train_idx, test_idx) — arrays za int64.

    t0 = wakati label inaanza (bar ya ENTRY); t1 = wakati label inaisha (bar ya EXIT). Zote
    datetime64 (au numeric) za urefu ule ule. embargo = timedelta64 (au numeric) — muda baada ya
    TEST ambao TRAIN haiwezi kuanza ndani yake; None -> **horizon ya juu ya label** (max(t1 - t0)),
    ndiyo default ya kanuni (§4.2).

    TEST fold k = rows zenye t0 ndani ya block k.
    TRAIN fold k = rows ZOTE nyingine ISIPOKUWA:
      (a) PURGE: [t0, t1] inagusa [block_start, block_end]  (overlap yoyote — hata ya mwisho mmoja);
      (b) EMBARGO: t0 iko ndani ya (block_end, block_end + embargo].
    """
    t0 = np.asarray(t0); t1 = np.asarray(t1)
    if len(t0) != len(t1):
        raise ValueError("t0 na t1 lazima ziwe urefu sawa")
    if len(t0) == 0:
        raise ValueError("hakuna rows")
    if np.any(t1 < t0):
        raise ValueError("t1 < t0 kwa baadhi ya rows (label inaisha kabla haijaanza)")
    if embargo is None:
        embargo = (t1 - t0).max()
    blocks = time_blocks(t0, n_folds)
    idx = np.arange(len(t0), dtype=np.int64)
    folds = []
    for k, (a, b) in enumerate(blocks):
        in_test = (t0 >= a) & (t0 <= b) if k == n_folds - 1 else (t0 >= a) & (t0 < b)
        test = idx[in_test]
        overlap = (t0 <= b) & (t1 >= a)                     # PURGE: mgusano wowote na block
        emb = (t0 > b) & (t0 <= b + embargo)                # EMBARGO: baada ya block
        train = idx[~(in_test | overlap | emb)]
        folds.append((train, test))
    return folds


def fold_report(t0, t1, folds):
    """Muhtasari kwa kila fold: n_train, n_test, n_purged (+embargoed), madirisha ya muda.
    Accounting TU (hakuna statistic)."""
    t0 = np.asarray(t0); t1 = np.asarray(t1); n = len(t0)
    rows = []
    for k, (tr, te) in enumerate(folds):
        dropped = n - len(tr) - len(te)
        rows.append(dict(fold=k, n_train=int(len(tr)), n_test=int(len(te)), n_dropped=int(dropped),
                         test_start=str(t0[te].min()) if len(te) else None,
                         test_end=str(t0[te].max()) if len(te) else None,
                         drop_share=round(dropped / n, 4)))
    return rows


# ---------- self-test ----------
def self_test():
    ok = True
    H = np.timedelta64(1, "h")
    n = 1000
    t0 = np.datetime64("2016-01-01T00") + np.arange(n) * H
    hold = np.array([(i % 24) + 1 for i in range(n)])        # horizon inayotofautiana 1..24
    t1 = t0 + hold * H

    folds = purged_folds(t0, t1, n_folds=5)

    # [1] test folds: disjoint NA zinafunika rows ZOTE (hakuna row inayopotea kwenye test)
    all_test = np.concatenate([te for _, te in folds])
    t1_ok = len(all_test) == n and len(np.unique(all_test)) == n
    print(f"  [1] test folds disjoint + coverage kamili: {len(all_test)}/{n} unique="
          f"{len(np.unique(all_test))} -> {t1_ok}")
    ok = ok and t1_ok

    # [2] PURGE EXACT: HAKUNA label ya train inayogusa dirisha la test (hii ndiyo RED LINE)
    t2 = True
    for k, (tr, te) in enumerate(folds):
        a, b = t0[te].min(), t0[te].max()
        touch = (t0[tr] <= b) & (t1[tr] >= a)
        t2 = t2 and not touch.any()
    print(f"  [2] purge: hakuna train-label inayogusa [test_start, test_end] kwenye folds zote -> {t2}")
    ok = ok and t2

    # [3] EMBARGO EXACT: hakuna train inayoanza ndani ya (test_end, test_end + embargo]
    emb = (t1 - t0).max()
    t3 = True
    for tr, te in folds:
        b = t0[te].max()
        t3 = t3 and not (((t0[tr] > b) & (t0[tr] <= b + emb)).any())
    print(f"  [3] embargo (default = horizon ya juu = {emb}): hakuna train ndani ya window -> {t3}")
    ok = ok and t3

    # [4] train/test HAZIINGILIANI kabisa (intersection tupu)
    t4 = all(len(np.intersect1d(tr, te)) == 0 for tr, te in folds)
    print(f"  [4] train ∩ test = tupu kwenye folds zote -> {t4}")
    ok = ok and t4

    # [5] purge INAFANYA KAZI KWELI: bila purge, train ingekuwa kubwa zaidi (drop > 0)
    rep = fold_report(t0, t1, folds)
    t5 = all(r["n_dropped"] > 0 for r in rep) and all(r["n_train"] > 0 and r["n_test"] > 0 for r in rep)
    print(f"  [5] drop kwa kila fold: {[r['n_dropped'] for r in rep]} (zote > 0; train/test si tupu) -> {t5}")
    ok = ok and t5

    # [6] embargo=0 -> drop NDOGO kuliko default (monotonic); embargo kubwa -> drop KUBWA
    d0 = sum(r["n_dropped"] for r in fold_report(t0, t1, purged_folds(t0, t1, 5, np.timedelta64(0, "h"))))
    dd = sum(r["n_dropped"] for r in rep)
    dbig = sum(r["n_dropped"] for r in
               fold_report(t0, t1, purged_folds(t0, t1, 5, np.timedelta64(100, "h"))))
    t6 = d0 < dd < dbig
    print(f"  [6] monotonicity ya embargo: drop(0h)={d0} < drop(default)={dd} < drop(100h)={dbig} -> {t6}")
    ok = ok and t6

    # [7] MULTI-PAIR: mpaka MMOJA wa muda kwa pairs zote (cross-pair leakage haiwezekani)
    t0m = np.concatenate([t0, t0]); t1m = np.concatenate([t1, t1])
    pair = np.array(["A"] * n + ["B"] * n)
    fm = purged_folds(t0m, t1m, n_folds=4)
    t7 = True
    for tr, te in fm:
        a, b = t0m[te].min(), t0m[te].max()
        t7 = t7 and not ((t0m[tr] <= b) & (t1m[tr] >= a)).any()       # hata cross-pair
        t7 = t7 and set(pair[te]) == {"A", "B"}                        # fold ina pairs zote
    print(f"  [7] multi-pair: mpaka wa muda ni MMOJA (pairs A+B kwenye kila test; hakuna overlap) -> {t7}")
    ok = ok and t7

    # [8] determinism + guards
    f1 = purged_folds(t0, t1, 5); f2 = purged_folds(t0, t1, 5)
    det = all(np.array_equal(a[0], b[0]) and np.array_equal(a[1], b[1]) for a, b in zip(f1, f2))
    guards = 0
    for bad in (lambda: purged_folds(t0, t1, 1),
                lambda: purged_folds(t0, t1[::-1] - np.timedelta64(999, "h"), 5),
                lambda: purged_folds(t0[:2], t1[:2], 5)):
        try:
            bad()
        except ValueError:
            guards += 1
    t8 = det and guards == 3
    print(f"  [8] determinism={det} · guards (n_folds<2, t1<t0, rows<folds) = {guards}/3 -> {t8}")
    ok = ok and t8

    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.parse_args()
    return self_test()


if __name__ == "__main__":
    raise SystemExit(main())
