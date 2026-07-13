"""scientist_d_referee_pooled.py — SCIENTIST-D referee MC for family_pooled.py (AT4 FULL).

Independent verification of the mixture-null size of the OFFICIAL engine (strategy_lab.pvalue_boot,
called unmodified) on the 4-component two-point mixture matched to the C2-WATCH reps
(design reports/family_pooled_design.md §1/§4/§5-AT4). No data window is touched — pure MC.

Null constructions (both honest EV=0 versions of "matched to reps"):
  NULL-A: reps' W/L shape in R-units (from the precheck two-point), win% shifted to breakeven.
  NULL-B: reps' observed win%, payoff (1-w)/-w (the build's self-test construction).
Interleaving: component per slot ~ Multinomial(shares .17/.35/.25/.22), N=341 (design §4).

Size ladder (finite-B jitter of p is ±sqrt(p(1-p)/B) ≈ .0049/.0022/.0010 at B=2k/10k/50k; the
ladder shows empirically that size is B-stable, since B=50k × 20k reps is computationally
infeasible ~13h):
  [1] official engine, NULL-A & NULL-B: 20,000 reps @ B=2,000     -> band [0.040, 0.060]
  [2] official engine, NULL-A:          4,000 reps @ B=10,000     -> band [0.035, 0.065]
  [3] official engine, NULL-A:            600 reps @ B=50,000     -> band [0.030, 0.070] (SE .009)
  [4] AR(rho=0.5) clustered NULL-A (Gaussian-copula latent on win/loss): 8,000 reps @ B=2,000
                                                                   -> size <= 0.08 (documented
                                                                      residual, wave1_referee)
  [5] REFEREE'S OWN independent stationary-bootstrap+NW implementation (different code path,
      own RNG), NULL-A: 8,000 reps @ B=2,000 -> agreement with official within 2*SE
  [6] z-test size on same nulls (reference column)

Usage: python scripts/scientist_d_referee_pooled.py  (repo root; ~60-75 min)
"""
from __future__ import annotations
import math, sys, time
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "research"))
from strategy_lab import pvalue_boot, pvalue_gt0  # OFFICIAL engine — untouched

ALPHA = 0.05
N = 341
SHARES = np.array([0.17, 0.35, 0.25, 0.22]); SHARES = SHARES / SHARES.sum()
# From scripts/scientist_d_family_pooled_precheck.py (two-point in R-units per rep):
#            pair     W_R     L_R     win(obs)
REPS = [("GBPJPY", 1.0316, 0.9695, 0.729),
        ("EURGBP", 0.6140, 1.0550, 0.769),
        ("EURJPY", 2.9400, 1.0600, 0.402),
        ("AUDUSD", 1.8790, 1.1180, 0.522)]


def draw_null_A(rng, n=N):
    """Reps' W/L shape, breakeven win w0=L/(W+L) -> EV=0 per component."""
    comp = rng.choice(4, size=n, p=SHARES)
    x = np.empty(n)
    for k, (_, W, L, _) in enumerate(REPS):
        m = comp == k
        w0 = L / (W + L)
        x[m] = np.where(rng.random(m.sum()) < w0, W, -L)
    return x


def draw_null_B(rng, n=N):
    """Reps' observed win w, payoff +(1-w)/-w -> EV=0 (build's construction)."""
    comp = rng.choice(4, size=n, p=SHARES)
    x = np.empty(n)
    for k, (_, _, _, w) in enumerate(REPS):
        m = comp == k
        x[m] = np.where(rng.random(m.sum()) < w, 1 - w, -w)
    return x


def draw_null_A_ar(rng, rho=0.5, n=N):
    """NULL-A with AR(rho) Gaussian-copula latent driving win/loss (clustered outcomes)."""
    comp = rng.choice(4, size=n, p=SHARES)
    z = np.empty(n); z[0] = rng.normal()
    e = rng.normal(size=n)
    for t in range(1, n):
        z[t] = rho * z[t - 1] + math.sqrt(1 - rho * rho) * e[t]
    u = 0.5 * (1 + np.vectorize(math.erf)(z / math.sqrt(2)))
    x = np.empty(n)
    for k, (_, W, L, _) in enumerate(REPS):
        m = comp == k
        w0 = L / (W + L)
        x[m] = np.where(u[m] < w0, W, -L)
    return x


# ---------- referee's OWN independent engine (variant implementation, own RNG) ----------
def _nw_se(v, K):
    v = np.atleast_2d(v)
    n = v.shape[1]
    d = v - v.mean(axis=1, keepdims=True)
    lrv = (d * d).mean(axis=1)
    for k in range(1, K + 1):
        lrv = lrv + 2.0 * (1 - k / (K + 1)) * np.einsum("ij,ij->i", d[:, k:], d[:, :-k]) / n
    return np.sqrt(np.maximum(lrv, 1e-12) / n)


def my_pboot(x, B=2000, mb=3, seed=0):
    """Referee variant: stationary bootstrap indices built via geometric block LENGTHS
    (different construction than the official running-restart form), NW K=mb, percentile-t."""
    n = len(x)
    K = max(1, min(mb, n - 2))
    t_obs = x.mean() / _nw_se(x, K)[0]
    y = x - x.mean()
    rng = np.random.default_rng(seed)
    idx = np.empty((B, n), dtype=np.int64)
    for b in range(B):
        pos = 0
        while pos < n:
            start = rng.integers(0, n)
            length = min(int(rng.geometric(1.0 / mb)), n - pos)
            idx[b, pos:pos + length] = (start + np.arange(length)) % n
            pos += length
    t_star = y[idx].mean(axis=1) / _nw_se(y[idx], K)
    return float((1 + (t_star >= t_obs).sum()) / (B + 1))


def size_run(label, draw, pfun, reps, B, band, seed0):
    t0 = time.time()
    rej = rej_z = 0
    rng = np.random.default_rng(seed0)
    for m in range(reps):
        x = draw(rng)
        if pfun(x, B=B, seed=seed0 + 1 + m) < ALPHA:
            rej += 1
        if pvalue_gt0(x) < ALPHA:
            rej_z += 1
    sz, sz_z = rej / reps, rej_z / reps
    se = math.sqrt(sz * (1 - sz) / reps)
    ok = band[0] <= sz <= band[1]
    print(f"  {label}: size={sz:.4f} (SE {se:.4f}) z-ref={sz_z:.4f} band{band} -> "
          f"{'PASS' if ok else 'FAIL'}   [{(time.time()-t0)/60:.1f} min]", flush=True)
    return sz, ok


def main():
    print(f"REFEREE AT4 FULL MC — mixture N={N}, shares {SHARES.round(2).tolist()}, alpha={ALPHA}")
    ok = True
    # [1] main runs @ B=2000, 20k reps
    s1a, o = size_run("[1a] official, NULL-A, 20k reps @ B=2000", draw_null_A,
                      lambda x, B, seed: pvalue_boot(x, B=B, mean_block=3, seed=seed),
                      20_000, 2_000, (0.040, 0.060), 11_000_000); ok &= o
    s1b, o = size_run("[1b] official, NULL-B, 20k reps @ B=2000", draw_null_B,
                      lambda x, B, seed: pvalue_boot(x, B=B, mean_block=3, seed=seed),
                      20_000, 2_000, (0.040, 0.060), 12_000_000); ok &= o
    # [2] B=10k confirmation
    s2, o = size_run("[2]  official, NULL-A,  4k reps @ B=10000", draw_null_A,
                     lambda x, B, seed: pvalue_boot(x, B=B, mean_block=3, seed=seed),
                     4_000, 10_000, (0.035, 0.065), 13_000_000); ok &= o
    # [3] B=50k spot (registration B)
    s3, o = size_run("[3]  official, NULL-A, 600 reps @ B=50000", draw_null_A,
                     lambda x, B, seed: pvalue_boot(x, B=B, mean_block=3, seed=seed),
                     600, 50_000, (0.030, 0.070), 14_000_000); ok &= o
    # [4] AR(0.5) clustered
    s4, o = size_run("[4]  official, NULL-A AR(0.5), 8k reps @ B=2000", draw_null_A_ar,
                     lambda x, B, seed: pvalue_boot(x, B=B, mean_block=3, seed=seed),
                     8_000, 2_000, (0.0, 0.080), 15_000_000); ok &= o
    # [5] referee's independent engine — agreement
    s5, _ = size_run("[5]  REFEREE variant engine, NULL-A, 8k reps @ B=2000", draw_null_A,
                     my_pboot, 8_000, 2_000, (0.035, 0.065), 16_000_000)
    agree = abs(s5 - s1a) <= 2 * math.sqrt(0.05 * 0.95 / 8_000) + 2 * math.sqrt(0.05 * 0.95 / 20_000)
    print(f"  [5b] agreement official vs referee variant: |{s1a:.4f}-{s5:.4f}|="
          f"{abs(s1a-s5):.4f} within 2SE bounds -> {'PASS' if agree else 'FAIL'}")
    ok &= agree
    print(f"\nREFEREE AT4 VERDICT: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
