"""test_direction_edge.py — thibitisha MACHINERY ya Phase B directional-edge harness.

Sawa na rigor ya timu (DIAGNOSTICS_DECISIONS.md §0): kabla ya kuamini matokeo ya data
halisi, lazima tuhakikishe machinery (a) inagundua edge ikiwepo, (b) HAITOI false
positive ya kimfumo kwenye noise — hasa kwenye kesi ya spurious-regression (signal
persistent dhidi ya random walk) ambayo ndio hatari halisi ya long-horizon.

Endesha: pytest tests/  (au: python tests/test_direction_edge.py)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from models.direction_edge import (  # noqa: E402
    ALPHA, circular_shift_pvalue, evaluate_series, self_test,
)


def test_planted_edge_detected():
    """Edge wa kweli (forward return inategemea position) -> p ndogo, hit > 0.5."""
    rng = np.random.default_rng(0)
    n = 1500
    pos = rng.choice([-1.0, 1.0], size=n)
    fwd = pos * 0.002 + rng.normal(0, 0.01, n)
    r = evaluate_series(pos.copy(), fwd, n_perm=2000, rng=rng)
    assert r is not None and r["p"] < 0.01, r
    assert r["hit"] > 0.55, r


def test_noise_false_positive_rate_near_alpha():
    """Spurious-regression case: signal=price-vs-EMA (persistent) dhidi ya random walk.
    False-positive rate lazima iwe karibu na α — sio kuvimba (ndio sababu ya circular-shift)."""
    rng = np.random.default_rng(11)
    n, h, trials, fp = 1500, 5, 40, 0
    for _ in range(trials):
        price = np.cumsum(rng.normal(0, 0.01, n))
        a = 2.0 / (50 + 1.0)
        ema = np.empty_like(price)
        ema[0] = price[0]
        for i in range(1, n):
            ema[i] = a * price[i] + (1 - a) * ema[i - 1]
        sig = price - ema
        f = np.full(n, np.nan)
        f[:-h] = price[h:] - price[:-h]
        idx = np.arange(0, n, h)
        r = evaluate_series(sig[idx], f[idx], n_perm=1500, rng=rng)
        if r is not None and r["p"] < ALPHA and r["mean_ret"] > 0:
            fp += 1
    assert fp / trials <= 0.20, f"false-positive rate kubwa mno: {fp}/{trials}"


def test_pvalue_bounds():
    """p-value daima iko (0, 1]; haiwezi kuwa 0 hasa (unbiased permutation)."""
    rng = np.random.default_rng(3)
    pos = rng.choice([-1.0, 1.0], size=200)
    fwd = rng.normal(0, 0.01, 200)
    _, p, _, _ = circular_shift_pvalue(pos, fwd, n_perm=500, rng=rng)
    assert 0.0 < p <= 1.0


if __name__ == "__main__":
    raise SystemExit(self_test())
