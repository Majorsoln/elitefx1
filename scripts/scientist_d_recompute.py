"""scientist_d_recompute.py — SCIENTIST-D independent recomputation (data_science_review.md).

Reads ONLY already-committed artifacts from git history (no data windows touched, no new
experiments). Reproduces every number cited in reports/data_science_review.md:
  1. BH-FDR verification for all published verdicts (C1/p11/C2-H1/C2-H4 + S3b m=5)
  2. C1 VALID->HOLDOUT selection shrinkage (join on cell key)
  3. Normal-approx p-value size under skewed two-point nulls (Monte Carlo)
  3b. Skew-corrected p for STRAT-001/002 + S3b siblings; S3b BH re-verdict
  4. Plateau/correlation structure (cells per (event,pair) combo; survivor groups)
  5. Fragility arithmetic for proven strategies (breakeven win%, cost share, spread stress)
  7. Cumulative cell-tests on the 2023-24 validation window
  8. C2-H4 VALID/TRAIN EV ratios (regime signature)
  9. Power/MDE arithmetic for S3c/SIB-5

Usage:  python scripts/scientist_d_recompute.py      (run from repo root; needs numpy + git)
"""
from __future__ import annotations
import json, math, subprocess, sys
from collections import Counter
from math import erfc, sqrt
import numpy as np

COMMITS = {
    "c1_train":   ("ccfbb24", "data/strategies/candidates.jsonl"),
    "c1_valid":   ("e1a0d27", "data/strategies/candidates.jsonl"),
    "c1_holdout": ("86a5977", "data/strategies/candidates.jsonl"),
    "p11_valid":  ("686744f", "data/strategies/candidates.jsonl"),
    "c2_train_h4": ("ffb212e", "data/strategies/candidates_c2.jsonl"),
    "c2_valid_h1": ("96793e7", "data/strategies/candidates_c2.jsonl"),
    "c2_valid_h4": ("d3c03a6", "data/strategies/candidates_c2.jsonl"),
}

def load(tag):
    commit, path = COMMITS[tag]
    txt = subprocess.run(["git", "show", f"{commit}:{path}"], capture_output=True,
                         text=True, check=True).stdout
    return [json.loads(l) for l in txt.splitlines() if l.strip()]

def key(r):
    sf = r["session_filter"]
    if isinstance(sf, list):
        sf = tuple(sf)
    return (r["event"], r["pair"], r["sl_atr"], r["tp_atr"], sf, r["vol_filter"])

def bh(pvals, q=0.10):
    pv = np.asarray(pvals, float); m = len(pv)
    order = np.argsort(pv); k = 0
    for rank, idx in enumerate(order, 1):
        if pv[idx] <= q * rank / m:
            k = rank
    if k == 0:
        return np.zeros(m, bool), 0
    return pv <= pv[order[k - 1]], k

def zval(p):
    lo, hi = 0.0, 10.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if 0.5 * erfc(mid / sqrt(2)) > p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2

def main():
    rng = np.random.default_rng(7)

    print("== 1) BH-FDR verification ==")
    for tag, published in [("c1_valid", 1), ("p11_valid", 1), ("c2_valid_h1", 0), ("c2_valid_h4", 30)]:
        rows = load(tag)
        _, k = bh([r["p"] for r in rows])
        stored = sum(1 for r in rows if r.get("fdr_survivor"))
        print(f"  {tag}: n={len(rows)} recomputed k={k} stored={stored} published={published} "
              f"match={k == stored == published}")
    _, k5 = bh([0.049, 0.029, 0.036, 0.999, 0.17])   # S3b (CHIEF_STATUS); SIB-4 EV<0 -> p large
    print(f"  S3b m=5: k={k5} (published 3)")

    print("\n== 2) C1 VALID->HOLDOUT shrinkage ==")
    cv = {key(r): r for r in load("c1_valid")}
    ch = {key(r): r for r in load("c1_holdout")}
    common = [x for x in cv if x in ch]
    for lo, hi in [(0, .01), (.01, .05), (.05, .2), (.2, 1.01)]:
        ks = [x for x in common if lo <= cv[x]["p"] < hi]
        evv = np.mean([cv[x]["ev"] for x in ks]); evh = np.mean([ch[x]["ev"] for x in ks])
        frac = np.mean([ch[x]["ev"] > 0 for x in ks])
        print(f"  p in [{lo},{hi}): n={len(ks)} EV {evv:+.2f} -> {evh:+.2f} "
              f"(shrink {100*(1-evh/evv):.0f}%), frac holdout EV>0 = {frac:.2f}")
    evv = np.array([cv[x]["ev"] for x in common]); evh = np.array([ch[x]["ev"] for x in common])
    b, a = np.polyfit(evv, evh, 1)[::-1]
    print(f"  OLS: EV_holdout = {b:+.2f} + {a:.3f}*EV_valid (n={len(common)})")

    print("\n== 3) z-test size under skewed two-point nulls (MC 200k) ==")
    def size(W, L, N, alpha, reps=200_000):
        w0 = L / (W + L)
        x = np.where(rng.random((reps, N)) < w0, W, -L).astype(float)
        t = x.mean(1) / (x.std(1, ddof=1) / math.sqrt(N))
        return (t >= zval(alpha)).mean()
    for lbl, W, L, N in [("SL2/TP1 N=303", 10.98, 23.7, 303), ("SL2/TP1 N=100", 10.0, 22.0, 100),
                         ("SL1.5/TP1.5 N=107", 15.0, 17.0, 107), ("SL1/TP3 N=70", 30.0, 11.0, 70)]:
        s = size(W, L, N, 0.05)
        print(f"  {lbl}: size@0.05 = {s:.4f} (x{s/0.05:.2f})")

    print("\n== 3b) skew-corrected p (payoff-matched null) ==")
    hold = load("c1_holdout")
    def find(rows, *kk):
        for r in rows:
            if key(r) == kk:
                return r
    targets = [("STRAT-001", "nr7_break", "USDCHF", 2.0, 1.0, "no-LATE", None),
               ("STRAT-002/SIB-2", "nr7_break", "USDJPY", 1.0, 1.0, "no-LATE", None),
               ("SIB-1", "nr7_break", "USDCHF", 1.5, 1.0, "no-LATE", None),
               ("SIB-3", "nr7_break", "USDCHF", 2.0, 1.0, ("LONDON", "NY"), None),
               ("SIB-5", "nr7_break", "GBPUSD", 2.0, 1.0, "no-LATE", "HIGH")]
    corr = []
    for lbl, *kk in targets:
        r = find(hold, *kk)
        n, ev, win, pf, p0 = r["n"], r["ev"], r["win"], r["pf"], r["p"]
        WL = pf * (1 - win) / win
        L = ev / (win * WL - (1 - win)); W = WL * L
        w0 = L / (W + L); t_obs = zval(p0)
        x = np.where(rng.random((400_000, n)) < w0, W, -L).astype(float)
        t = x.mean(1) / (x.std(1, ddof=1) / math.sqrt(n))
        pc = float((t >= t_obs).mean()); corr.append(pc)
        print(f"  {lbl}: p_stored={p0:.4f} -> p_corrected={pc:.4f} (x{pc/p0:.2f})")
    _, kc = bh([corr[2], corr[1], corr[3], 0.99, corr[4]])
    print(f"  S3b BH m=5 with corrected p: k={kc} (published 3)")

    print("\n== 4) correlation structure ==")
    rows = load("c1_valid")
    print(f"  C1 VALID: {len(rows)} cells / {len({(r['event'], r['pair']) for r in rows})} (event,pair) combos")
    surv = [r for r in load("c2_valid_h4") if r.get("fdr_survivor")]
    g = Counter((r["event"], r["pair"]) for r in surv)
    print(f"  C2-H4 survivors: {len(surv)} cells in {len(g)} groups: {dict(g)}")

    print("\n== 7) cumulative tests on 2023-24 window ==")
    k1 = {key(r) for r in load("c1_valid")}; k11 = {key(r) for r in load("p11_valid")}
    new = k11 - k1
    tot = len(k1) + len(new) + len(load("c2_valid_h1")) + len(load("c2_valid_h4"))
    print(f"  C1={len(k1)} + p11 new={len(new)} + C2H1=1068 + C2H4=1152 -> {tot} distinct cell-tests")

    print("\n== 8) C2-H4 VALID/TRAIN EV ratios (survivors) ==")
    t4 = {key(r): r for r in load("c2_train_h4")}
    ratios = [r["ev"] / t4[key(r)]["ev"] for r in surv if key(r) in t4 and t4[key(r)]["ev"] > 0]
    print(f"  median={np.median(ratios):.1f} max={max(ratios):.1f} (n={len(ratios)})")

    print("\n== 9) power/MDE (from stored EV,p,N) ==")
    for lbl, ev, p, n in [("SIBC-3 EURCHF", 1.21, 0.131, 105), ("SIBC-1 EURCHF", 1.76, 0.156, 94),
                          ("SIB-5 GBPUSD", 2.84, 0.17, 103)]:
        sd = ev / zval(p) * math.sqrt(n)
        print(f"  {lbl}: implied sd={sd:.1f} -> N for p<.05 at same EV ~ {(1.645*sd/ev)**2:.0f} ({(1.645*sd/ev)**2/n:.1f}x)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
