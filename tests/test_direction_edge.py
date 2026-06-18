"""test_direction_edge.py — thibitisha MACHINERY ya Phase B directional-edge harness.

Sawa na rigor ya timu (DIAGNOSTICS_DECISIONS.md §0): kabla ya kuamini matokeo ya data
halisi, lazima tuhakikishe machinery (a) inagundua edge ikiwepo (nulls 3 zote), (b) HAITOI
false positive ya kimfumo kwenye noise — hasa kesi ya spurious-regression (signal persistent
dhidi ya random walk), hatari halisi ya long-horizon.

Endesha: pytest tests/  (au: python tests/test_direction_edge.py)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from models.direction_edge import (  # noqa: E402
    ALPHA, block_bootstrap, circular_shift_pvalue, evaluate_series,
    random_direction_pvalue, self_test,
)


def test_planted_edge_is_strong():
    """Edge wa kweli -> grade STRONG (nulls 3 zote), CI inaondoa 0, hit > 0.5."""
    rng = np.random.default_rng(0)
    n = 1500
    pos = rng.choice([-1.0, 1.0], size=n)
    fwd = pos * 0.002 + rng.normal(0, 0.01, n)
    r = evaluate_series(pos.copy(), fwd, n_perm=3000, n_boot=1000, rng=rng)
    assert r is not None and r["grade"] == "STRONG", r
    assert r["p_shift"] < 0.01 and r["ci_lo"] > 0 and r["hit"] > 0.55, r


def test_circular_shift_is_exact_and_matches_brute():
    """FFT circular-shift null = brute np.roll (exact), obs = shift 0, p ∈ [1/n, 1]."""
    rng = np.random.default_rng(5)
    n = 300
    pos = rng.choice([-1.0, 1.0], size=n)
    fwd = rng.normal(0, 0.01, n)
    obs, p, _, _ = circular_shift_pvalue(pos, fwd)
    brute = np.array([np.mean(np.roll(pos, k) * fwd) for k in range(n)])
    assert abs(obs - brute[0]) < 1e-12
    assert abs(p - np.sum(brute >= brute[0]) / n) < 1e-12
    assert 1.0 / n <= p <= 1.0


def test_noise_false_positive_rate_near_alpha():
    """Spurious-regression case: price-vs-EMA (persistent) dhidi ya random walk.
    STRONG/MODERATE false-positive rate lazima iwe karibu α (sababu ya nulls 3 + circular-shift)."""
    rng = np.random.default_rng(11)
    n, h, trials, fp = 1500, 5, 40, 0
    for _ in range(trials):
        price = np.cumsum(rng.normal(0, 0.01, n))
        a = 2.0 / 51.0
        ema = np.empty_like(price)
        ema[0] = price[0]
        for i in range(1, n):
            ema[i] = a * price[i] + (1 - a) * ema[i - 1]
        sig = price - ema
        f = np.full(n, np.nan)
        f[:-h] = price[h:] - price[:-h]
        idx = np.arange(0, n, h)
        r = evaluate_series(sig[idx], f[idx], n_perm=1500, n_boot=600, rng=rng)
        if r is not None and r["grade"] in ("STRONG", "MODERATE"):
            fp += 1
    assert fp / trials <= 0.20, f"false-positive rate kubwa mno: {fp}/{trials}"


def test_null_pvalues_bounds():
    """p-values zote ∈ (0, 1]; bootstrap CI lo ≤ hi."""
    rng = np.random.default_rng(3)
    pos = rng.choice([-1.0, 1.0], size=200)
    fwd = rng.normal(0, 0.01, 200)
    _, p_sh, _, _ = circular_shift_pvalue(pos, fwd)
    p_dir = random_direction_pvalue(pos, fwd, n_perm=500, rng=rng)
    bp, lo, hi = block_bootstrap(pos, fwd, n_boot=500, rng=rng)
    assert 0.0 < p_sh <= 1.0 and 0.0 < p_dir <= 1.0 and 0.0 < bp <= 1.0
    assert lo <= hi


if __name__ == "__main__":
    raise SystemExit(self_test())
