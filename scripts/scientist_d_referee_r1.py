"""SCIENTIST-D REFEREE MC — independent verification of WAVE-1 R1 pvalue_boot (commit 9328f16).

Calls the IMPLEMENTER's actual pvalue_boot/pvalue_gt0 unmodified; all nulls and variant
implementations are mine (independent of their calibration scripts). Pure simulation —
touches NO data windows.

Acceptance tests (data_science_review.md SS B-R1):
  (a) symmetric i.i.d. null: p_boot ~ p_z, both size ~0.05
  (b) two-point negative-skew nulls (SS A3-W1, cost-adjusted payoffs): z size 1.2-1.4x, boot ~nominal
  (c) determinism from cell key
Deviation judgment:
  (i)  mean_block=3 vs ~10  -> measure mb10 size on the same skew nulls (their claim: 0.063-0.072)
  (ii) NW studentization    -> AR(rho) cluster nulls (their claim: mb3+NW 0.058 vs z 0.121);
       isolation variants: verbatim design (mb10 + iid-sd), mb3 + iid-sd, mb1 + iid-sd.
"""
import math
import sys
import time

import numpy as np

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "src" / "research"))
import strategy_lab as SL  # noqa: E402  (their code, unmodified)

ALPHA = 0.05


# ---- my own variant implementations (for isolation; NOT their code) ----
def p_boot_iid_sd(x, B, mean_block, rng_seed):
    """Stationary bootstrap + percentile-t with plain i.i.d. sd studentization.
    mean_block=10 == the VERBATIM SS B-R1 design; mean_block=1 == i.i.d. bootstrap."""
    x = np.asarray(x, float)
    n = len(x)
    sd = x.std(ddof=1)
    if sd == 0:
        return 0.0 if x.mean() > 0 else 1.0
    t_obs = x.mean() / (sd / math.sqrt(n))
    y = x - x.mean()
    rng = np.random.default_rng(rng_seed)
    idx = SL._stationary_indices(n, B, min(mean_block, n), rng)  # reuse their sampler (tested separately)
    ys = y[idx]
    sd_s = ys.std(axis=1, ddof=1)
    sd_s = np.maximum(sd_s, 1e-12)
    t_star = ys.mean(axis=1) / (sd_s / math.sqrt(n))
    return float((1 + int((t_star >= t_obs).sum())) / (B + 1))


# ---- null generators (mine) ----
def gen_two_point(rng, reps, n, W, L):
    """EV=0 two-point null: win prob w0 = L/(W+L)."""
    w0 = L / (W + L)
    return np.where(rng.random((reps, n)) < w0, W, -L).astype(float)


def gen_sym(rng, reps, n):
    return rng.standard_normal((reps, n))


def gen_ar1(rng, reps, n, rho):
    e = rng.standard_normal((reps, n))
    x = np.empty((reps, n))
    x[:, 0] = e[:, 0] / math.sqrt(1 - rho * rho)
    for j in range(1, n):
        x[:, j] = rho * x[:, j - 1] + e[:, j]
    return x


def size_run(label, samples, methods, B=600):
    reps = samples.shape[0]
    out = {}
    for mname, fn in methods.items():
        t0 = time.time()
        rej = 0
        for i in range(reps):
            if fn(samples[i], i) < ALPHA:
                rej += 1
        s = rej / reps
        se = math.sqrt(s * (1 - s) / reps)
        out[mname] = s
        print(f"  {label:28s} {mname:18s} size@0.05 = {s:.4f} (+-{2*se:.4f})  [{time.time()-t0:.0f}s]",
              flush=True)
    return out


def main():
    rng = np.random.default_rng(20260712)
    B = 600

    m_z = lambda x, i: SL.pvalue_gt0(x)
    m_b3 = lambda x, i: SL.pvalue_boot(x, B=B, mean_block=3, seed=10_000 + i)
    m_b10 = lambda x, i: SL.pvalue_boot(x, B=B, mean_block=10, seed=20_000 + i)
    m_verb = lambda x, i: p_boot_iid_sd(x, B, 10, 30_000 + i)   # verbatim SS B-R1
    m_b3iid = lambda x, i: p_boot_iid_sd(x, B, 3, 40_000 + i)
    m_b1iid = lambda x, i: p_boot_iid_sd(x, B, 1, 50_000 + i)

    print("== (a) SYMMETRIC i.i.d. null N(0,1), N=100 ==", flush=True)
    S = gen_sym(rng, 3000, 100)
    size_run("sym N=100", S, {"z": m_z, "boot mb3 (OFFICIAL)": m_b3}, B)
    d = [abs(SL.pvalue_boot(S[i], B=B, seed=60_000 + i) - SL.pvalue_gt0(S[i])) for i in range(400)]
    print(f"  mean |p_boot - p_z| on symmetric null = {np.mean(d):.4f} (their self-test [7]: 0.025)")

    print("== (b) SKEW NULLS (SS A3-W1 payoff-matched, EV=0) ==", flush=True)
    # STRAT-001 structure: W=10.98 / L=23.70 (cost-adjusted holdout payoffs), N=303
    A = gen_two_point(rng, 2000, 303, 10.98, 23.70)
    size_run("skew SL2/TP1 N=303", A,
             {"z": m_z, "boot mb3 (OFFICIAL)": m_b3, "boot mb10 (their fn)": m_b10,
              "VERBATIM mb10+iid": m_verb, "mb3+iid-sd": m_b3iid}, B)
    # N=100, win~69% null
    Bn = gen_two_point(rng, 3000, 100, 10.0, 22.0)
    size_run("skew SL2/TP1 N=100", Bn,
             {"z": m_z, "boot mb3 (OFFICIAL)": m_b3, "boot mb10 (their fn)": m_b10,
              "VERBATIM mb10+iid": m_verb, "mb3+iid-sd": m_b3iid}, B)
    # positive skew TP3 structure N=70 (z should be CONSERVATIVE ~0.039)
    P = gen_two_point(rng, 3000, 70, 30.0, 11.0)
    size_run("pos-skew SL1/TP3 N=70", P, {"z": m_z, "boot mb3 (OFFICIAL)": m_b3}, B)

    print("== (ii) DEPENDENCE NULLS (AR(1), mean 0) ==", flush=True)
    C5 = gen_ar1(rng, 3000, 100, 0.5)
    size_run("AR rho=0.5 N=100", C5,
             {"z": m_z, "boot mb3 (OFFICIAL)": m_b3, "mb1+iid-sd": m_b1iid, "mb3+iid-sd": m_b3iid}, B)
    C7 = gen_ar1(rng, 3000, 100, 0.7)   # robustness beyond their calibration
    size_run("AR rho=0.7 N=100 (stress)", C7, {"z": m_z, "boot mb3 (OFFICIAL)": m_b3}, B)

    print("== POWER (two-point alternative, STRAT-001 holdout params: win=0.739, W=10.98/L=23.70) ==",
          flush=True)
    for n, reps in [(303, 1500), (100, 2000)]:
        X = np.where(rng.random((reps, n)) < 0.739, 10.98, -23.70).astype(float)
        pw = np.mean([SL.pvalue_boot(X[i], B=B, mean_block=3, seed=70_000 + i) < ALPHA
                      for i in range(reps)])
        pwz = np.mean([SL.pvalue_gt0(X[i]) < ALPHA for i in range(reps)])
        print(f"  N={n}: power boot mb3 = {pw:.3f} | z = {pwz:.3f}")

    print("== (c) DETERMINISM ==", flush=True)
    x = gen_two_point(rng, 1, 200, 10.0, 22.0)[0]
    cellA = dict(event="nr7_break", pair="USDCHF", sl_atr=2.0, tp_atr=1.0,
                 session_filter="no-LATE", vol_filter=None)
    cellB = dict(cellA, pair="USDJPY")
    p1 = SL.pvalue_boot(x, B=2000, cell=cellA)
    p2 = SL.pvalue_boot(x, B=2000, cell=cellA)
    p3 = SL.pvalue_boot(x, B=2000, cell=cellB)
    print(f"  same cell twice: {p1} == {p2} -> {p1 == p2}; different cell: {p3} (differs: {p3 != p1});"
          f" seeds differ: {SL._seed_from_key(cellA) != SL._seed_from_key(cellB)}")
    print("  B=10_000 MC resolution at p=0.05: 2*SE =",
          f"{2*math.sqrt(0.05*0.95/10_000):.4f} (registration knife-edge note)")

    print("DONE", flush=True)


if __name__ == "__main__":
    main()
