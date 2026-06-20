"""
cross_pair_mr.py — METHOD #2/#13: Cross-pair Spread Mean-Reversion (Correlation Divergence).

Mantiki: pairs zenye correlation kubwa (AUDUSD–NZDUSD = 0.85) — hata kama kila moja
haitabiriki, SPREAD yao (tofauti) hu-mean-revert. Tukiona spread imetofautiana kupita
kiasi → bet convergence (market-neutral: long moja, short nyingine).

Spread = log(closeA) − log(closeB). z = (spread − rolling_mean)/rolling_std (window 20).
Signal: |z|≥2 → pos = −sign(z) (fade spread). PnL = pos·(spread change). Cost = round-trip
miguu MIWILI. Sub-period stability (P1 2016-20, P2 2021-24) + Phase B. NO-LOOKAHEAD,
non-overlapping. 2025+ HAIGUSWI.

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
N_PERM = 5000
MIN_N = 40
PAIRS = [("AUDUSD", "NZDUSD"), ("EURUSD", "GBPUSD"), ("AUDUSD", "EURUSD")]
PERIODS = [("P1", 2016, 2020), ("P2", 2021, 2024)]


def circ_perm(pos, fwd, n_perm, rng):
    obs = float(np.mean(pos * fwd)); n = len(pos); cnt = 1
    for _ in range(n_perm):
        s = int(rng.integers(2, n - 2))
        if np.mean(np.roll(pos, s) * fwd) >= obs:
            cnt += 1
    return cnt / (n_perm + 1)


def evaluate(z, fwd, cost, rng):
    """z = spread z-score; fwd = spread change t->t+H; pos = -sign(z) (fade)."""
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
    pnl = pos * fwd[kept]                    # faida ikiwa spread inarudi mean
    net = pnl - cost[kept]
    p = circ_perm(pos, fwd[kept], N_PERM, rng)
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
    sp = pl.col("cA").log() - pl.col("cB").log()
    df = df.with_columns(sp.alias("sp"))
    df = df.with_columns(
        pl.col("bar_open").dt.year().alias("yr"),
        ((pl.col("sp") - pl.col("sp").rolling_mean(WIN)) / pl.col("sp").rolling_std(WIN)).alias("z"),
        (pl.col("sp").shift(-H) - pl.col("sp")).alias("fwd"),
        (2 * (pl.col("sA") * _pip(A) / pl.col("cA") + pl.col("sB") * _pip(B) / pl.col("cB"))).alias("cost"),
    )
    d = df.select(["yr", "z", "fwd", "cost"]).drop_nulls()
    return (d["yr"].to_numpy(), d["z"].to_numpy(), d["fwd"].to_numpy(), d["cost"].to_numpy())


def run():
    from data.dataset import config
    cfg = config()
    if not (REPO_ROOT / cfg["paths"]["processed"] / "candles").exists():
        print("HITILAFU: candles hazipo.", file=sys.stderr); return 1
    rng = np.random.default_rng(11)
    L = ["# Method #2/#13 — Cross-pair Spread Mean-Reversion\n",
         f"*Imezalishwa: {datetime.now():%Y-%m-%d %H:%M} | spread=log(A)−log(B), |z|≥{Z_EXT}, "
         f"fade | net baada ya cost (miguu 2) | Phase B N={N_PERM} | sub-period | 2025+ HAIJAGUSWA*\n",
         "> ROBUST = net>0 NA p<0.05 vipindi VYOTE. Stat-arb: corr pairs' spread hu-mean-revert.\n",
         "| Spread | P1 n | P1 net | P1 p | P2 n | P2 net | P2 p | Hukumu |",
         "|--------|------|--------|------|------|--------|------|--------|"]
    for A, B in PAIRS:
        try:
            yr, z, fwd, cost = spread_arrays(A, B)
        except FileNotFoundError:
            continue
        res = {}; ok = True
        for _, y0, y1 in PERIODS:
            m = (yr >= y0) & (yr <= y1)
            r = evaluate(z[m], fwd[m], cost[m], rng)
            res[(y0)] = r
            if not (r and r["net"] > 0 and r["p"] < 0.05):
                ok = False
        r1, r2 = res[2016], res[2021]
        def c(r): return (str(r["n"]), f"{r['net']:+.5f}", f"{r['p']:.3f}") if r else ("—", "—", "—")
        a, b = c(r1), c(r2)
        L.append(f"| {A}−{B} | {a[0]} | {a[1]} | {a[2]} | {b[0]} | {b[1]} | {b[2]} "
                 f"| {'✅ ROBUST' if ok else '❌'} |")
    L.append("\n---\n*✅ ROBUST (net>0 + p<0.05 vipindi VYOTE) = spread MR ni edge halisi → "
             "inastahili OOS. Stat-arb ni market-neutral (long A, short B). Cost = miguu 2 "
             "(spread ya pairs zote). β=1 (log-spread); cointegration kamili = hatua ya pili.*")
    out = REPO_ROOT / cfg["paths"]["reports"] / "cross_pair_mr.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"Ripoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """Planted: spread ina mean-reversion -> fade ina net>0, p<0.05."""
    rng = np.random.default_rng(0)
    def mk():
        z = rng.normal(0, 1.2, 1500)
        fwd = -0.4 * (z * 0.01) + rng.normal(0, 0.003, 1500)   # spread inarudi (sign ya z)
        return evaluate(z, fwd, np.full(1500, 0.00010), rng)
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
