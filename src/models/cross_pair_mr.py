"""
cross_pair_mr.py — METHOD #2/#13: Cross-pair Spread Mean-Reversion (Correlation Divergence).

Mantiki: corr pairs (AUDUSD–NZDUSD 0.85) — spread yao hu-mean-revert hata kama kila pair
haitabiriki. Stat-arb market-neutral (long A, short β·B).

β imekadiriwa kwa rolling OLS (no-lookahead): β = Cov(logA,logB)/Var(logB), window WIN_BETA.
Spread residual s = logA − β·logB; z = (s − mean)/std (window WIN). Signal |z|≥2 → fade.
PnL HALISI ya trade (shika β ya ENTRY): pnl = pos·[(Δlog A over H) − β_entry·(Δlog B over H)].
Cost = round-trip miguu 2. Sub-period (P1/P2) + Phase B. NO-LOOKAHEAD, non-overlapping.

Endesha (PC ya Japhet):  python src/models/cross_pair_mr.py
Self-test (popote):       python src/models/cross_pair_mr.py --self-test
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]

H = 5
Z_EXT = 2.0
WIN = 20
WIN_BETA = 60
N_PERM = 5000
MIN_N = 40
PAIRS = [("AUDUSD", "NZDUSD"), ("EURUSD", "GBPUSD"), ("AUDUSD", "EURUSD")]
PERIODS = [("P1", 2016, 2020), ("P2", 2021, 2024)]


def circ_perm(pos, ret, n_perm, rng):
    obs = float(np.mean(pos * ret)); n = len(pos); cnt = 1
    for _ in range(n_perm):
        s = int(rng.integers(2, n - 2))
        if np.mean(np.roll(pos, s) * ret) >= obs:
            cnt += 1
    return cnt / (n_perm + 1)


def evaluate(z, beta, dla, dlb, cost, rng):
    """pos=-sign(z) kwenye spread; pnl = pos·(ΔlogA − β_entry·ΔlogB) − cost."""
    if len(z) < 100:
        return None
    ext = np.where(np.abs(z) >= Z_EXT)[0]
    kept = []; last = -H - 1
    for i in ext:
        if i - last >= H:
            kept.append(i); last = i
    kept = np.array(kept)
    if len(kept) < MIN_N:
        return None
    pos = -np.sign(z[kept])
    ret = dla[kept] - beta[kept] * dlb[kept]      # spread return (β ya entry)
    net = pos * ret - cost[kept]
    p = circ_perm(pos, ret, N_PERM, rng)
    return dict(n=len(kept), net=float(net.mean()), win=float((net > 0).mean()), p=p)


# ───────────────────────── DATA PATH ─────────────────────────

def _pip(s):
    return 0.01 if "JPY" in s.upper() else 0.0001


def spread_arrays(A, B):
    import polars as pl
    from data.dataset import load_candles
    dfa = load_candles(A, "D1").select(
        ["bar_open", "close", "spread_mean_pips"]).rename({"close": "cA", "spread_mean_pips": "sA"})
    dfb = load_candles(B, "D1").select(
        ["bar_open", "close", "spread_mean_pips"]).rename({"close": "cB", "spread_mean_pips": "sB"})
    df = dfa.join(dfb, on="bar_open", how="inner").sort("bar_open")
    df = df.with_columns(pl.col("cA").log().alias("la"), pl.col("cB").log().alias("lb"))
    df = df.with_columns(
        (((pl.col("la") * pl.col("lb")).rolling_mean(WIN_BETA)
          - pl.col("la").rolling_mean(WIN_BETA) * pl.col("lb").rolling_mean(WIN_BETA))
         / ((pl.col("lb") ** 2).rolling_mean(WIN_BETA)
            - pl.col("lb").rolling_mean(WIN_BETA) ** 2)).alias("beta"))
    df = df.with_columns((pl.col("la") - pl.col("beta") * pl.col("lb")).alias("sp"))
    df = df.with_columns(
        pl.col("bar_open").dt.year().alias("yr"),
        ((pl.col("sp") - pl.col("sp").rolling_mean(WIN)) / pl.col("sp").rolling_std(WIN)).alias("z"),
        (pl.col("la").shift(-H) - pl.col("la")).alias("dla"),     # ΔlogA over H
        (pl.col("lb").shift(-H) - pl.col("lb")).alias("dlb"),     # ΔlogB over H
        (2 * (pl.col("sA") * _pip(A) / pl.col("cA") + pl.col("sB") * _pip(B) / pl.col("cB"))).alias("cost"),
    )
    d = df.select(["yr", "z", "beta", "dla", "dlb", "cost"]).drop_nulls()
    return tuple(d[c].to_numpy() for c in ["yr", "z", "beta", "dla", "dlb", "cost"])


def run():
    from data.dataset import config
    cfg = config()
    if not (REPO_ROOT / cfg["paths"]["processed"] / "candles").exists():
        print("HITILAFU: candles hazipo.", file=sys.stderr); return 1
    rng = np.random.default_rng(11)
    L = ["# Method #2/#13 — Cross-pair Spread Mean-Reversion (β estimated)\n",
         f"*Imezalishwa: {datetime.now():%Y-%m-%d %H:%M} | s=logA−β·logB (β rolling OLS {WIN_BETA}), "
         f"|z|≥{Z_EXT} fade | PnL β ya entry | net baada ya cost (miguu 2) | Phase B N={N_PERM} | "
         "sub-period | 2025+ HAIJAGUSWA*\n",
         "> ROBUST = net>0 NA p<0.05 vipindi VYOTE. Stat-arb market-neutral (long A, short β·B).\n",
         "| Spread | P1 n | P1 net | P1 p | P2 n | P2 net | P2 p | Hukumu |",
         "|--------|------|--------|------|------|--------|------|--------|"]
    for A, B in PAIRS:
        try:
            yr, z, beta, dla, dlb, cost = spread_arrays(A, B)
        except FileNotFoundError:
            continue
        res = {}; ok = True
        for _, y0, y1 in PERIODS:
            m = (yr >= y0) & (yr <= y1)
            r = evaluate(z[m], beta[m], dla[m], dlb[m], cost[m], rng)
            res[y0] = r
            if not (r and r["net"] > 0 and r["p"] < 0.05):
                ok = False
        r1, r2 = res[2016], res[2021]
        def c(r): return (str(r["n"]), f"{r['net']:+.5f}", f"{r['p']:.3f}") if r else ("—", "—", "—")
        a, b = c(r1), c(r2)
        L.append(f"| {A}−{B} | {a[0]} | {a[1]} | {a[2]} | {b[0]} | {b[1]} | {b[2]} "
                 f"| {'✅ ROBUST' if ok else '❌'} |")
    L.append(f"\n---\n*✅ ROBUST (net>0 + p<0.05 vipindi VYOTE) = spread MR ni edge halisi → OOS. "
             f"β rolling OLS (window {WIN_BETA}, no-lookahead); PnL hutumia β ya ENTRY (sio β "
             "inayobadilika). Cost = miguu 2. Market-neutral (long A, short β·B).*")
    out = REPO_ROOT / cfg["paths"]["reports"] / "cross_pair_mr.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"Ripoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """Planted: spread mean-reverts -> fade net>0, p<0.05. (dlb=0, beta=1 -> pnl=pos·dla)."""
    rng = np.random.default_rng(0)
    def mk():
        z = rng.normal(0, 1.2, 1500)
        dla = -0.4 * (z * 0.01) + rng.normal(0, 0.003, 1500)   # spread return inarudi
        return evaluate(z, np.ones(1500), dla, np.zeros(1500), np.full(1500, 0.0001), rng)
    a, b = mk(), mk()
    print(f"P1: n={a['n']} net={a['net']:+.5f} p={a['p']:.3f} | P2: n={b['n']} net={b['net']:+.5f} p={b['p']:.3f}")
    ok = a["net"] > 0 and a["p"] < 0.05 and b["net"] > 0 and b["p"] < 0.05
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if "--self-test" in sys.argv:
        return self_test()
    sys.path.insert(0, str(REPO_ROOT / "src"))
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
