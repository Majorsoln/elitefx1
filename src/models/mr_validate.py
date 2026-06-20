"""
mr_validate.py — Validation ya pair-specific mean-reversion (DOCTRINE §5: stability).

Test #3 ilionyesha mean-reversion (fade extreme) D1 kwa AUDUSD/EURGBP. Kabla ya kuamini,
DOCTRINE inadai: edge lazima iwe THABITI kwenye sub-periods (regime-decay check). Tunapima
edge kwa vipindi VIWILI vya train kando:
    P1 = 2016–2020    |    P2 = 2021–2024
Edge ROBUST = significant (Phase B p<0.05) NA net>0 kwa VIPINDI VYOTE. Ikidumu kimoja tu =
overfit/regime-decay. (2025+ holdout HAIGUSWI — ni final test moja, baadaye.)

Signal: fade |price_vs_ema|≥q80 (per period). Net baada ya cost. Phase B circular-shift.
NO-LOOKAHEAD, non-overlapping.

Endesha (PC ya Japhet):  python src/models/mr_validate.py
Self-test (popote):       python src/models/mr_validate.py --self-test
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]

TF = "D1"
H = 5
EXT_Q = 0.80
N_PERM = 5000
PERIODS = [("2016-2020", "2016-01-01", "2020-12-31"),
           ("2021-2024", "2021-01-01", "2024-12-31")]
FOCUS = ["AUDUSD", "EURGBP", "GBPUSD", "NZDUSD"]    # Test #3 ✅ pairs


def circ_perm(pos, fwd, n_perm, rng):
    obs = float(np.mean(pos * fwd))
    n = len(pos); cnt = 1
    for _ in range(n_perm):
        s = int(rng.integers(5, n - 5))
        if np.mean(np.roll(pos, s) * fwd) >= obs:
            cnt += 1
    return obs, cnt / (n_perm + 1)


def evaluate(pve, fwd, cost, rng):
    if len(pve) < 50:
        return None
    thr = np.quantile(np.abs(pve), EXT_Q)
    m = np.abs(pve) >= thr
    pos = -np.sign(pve[m])                      # FADE
    f, c = fwd[m], cost[m]
    nz = pos != 0
    pos, f, c = pos[nz], f[nz], c[nz]
    if len(pos) < 50:
        return None
    net = pos * f - c
    _, p = circ_perm(pos, f, N_PERM, rng)
    return dict(n=len(pos), net=float(net.mean()), win=float((net > 0).mean()), p=p)


# ───────────────────────── DATA PATH ─────────────────────────

def _pip(s):
    return 0.01 if "JPY" in s.upper() else 0.0001


def arrays_pair_period(pair, start, end):
    import polars as pl
    from data.dataset import load_candles
    c = pl.col("close")
    df = load_candles(pair, TF, start=start, end=end).with_columns(
        c.ewm_mean(span=200, min_samples=200).alias("ema"))
    df = df.with_columns(
        ((c - pl.col("ema")) / pl.col("ema")).alias("pve"),
        (c.shift(-H).log() - c.log()).alias("fwd"),
        (2 * pl.col("spread_mean_pips") * _pip(pair) / c).alias("cost"),
    )
    d = df.select(["pve", "fwd", "cost"]).drop_nulls().gather_every(H)
    return d["pve"].to_numpy(), d["fwd"].to_numpy(), d["cost"].to_numpy()


def run():
    from data.dataset import config
    cfg = config()
    if not (REPO_ROOT / cfg["paths"]["processed"] / "candles").exists():
        print("HITILAFU: candles hazipo.", file=sys.stderr); return 1
    rng = np.random.default_rng(11)
    L = ["# Mean-Reversion Validation — Sub-Period Stability\n",
         f"*Imezalishwa: {datetime.now():%Y-%m-%d %H:%M} | fade D1, net baada ya cost, Phase B "
         f"(N={N_PERM}) | P1=2016–2020, P2=2021–2024 | 2025+ HAIJAGUSWA*\n",
         "> ROBUST = net>0 NA p<0.05 kwa VIPINDI VYOTE. Kimoja tu = regime-decay/overfit.\n",
         "| Pair | P1 net | P1 p | P2 net | P2 p | Hukumu |",
         "|------|--------|------|--------|------|--------|"]
    pairs = FOCUS + [p for p in cfg["pairs"] if p not in FOCUS]
    for p in pairs:
        res = {}
        ok = True
        for name, s, e in PERIODS:
            try:
                pve, fwd, cost = arrays_pair_period(p, s, e)
            except FileNotFoundError:
                res[name] = None; ok = False; continue
            r = evaluate(pve, fwd, cost, rng)
            res[name] = r
            if not (r and r["net"] > 0 and r["p"] < 0.05):
                ok = False
        r1, r2 = res["2016-2020"], res["2021-2024"]
        def cell(r): return (f"{r['net']:+.5f}", f"{r['p']:.3f}") if r else ("—", "—")
        n1, p1 = cell(r1); n2, p2 = cell(r2)
        verdict = "✅ ROBUST" if ok else "❌"
        star = " ⭐" if p in FOCUS else ""
        L.append(f"| {p}{star} | {n1} | {p1} | {n2} | {p2} | {verdict} |")
    L.append("\n---\n*⭐ = Test #3 ✅ pairs. **ROBUST** (net>0 + p<0.05 vipindi VYOTE) = edge "
             "ya kuaminika → inastahili final OOS test (2025+). Ikidumu kipindi kimoja tu → "
             "regime-decay (overfit) → tusiijengee. Cost imejumuishwa; threshold per-period.*")
    out = REPO_ROOT / cfg["paths"]["reports"] / "mr_validate.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"Ripoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """Planted MR vipindi vyote -> robust (net>0, p<0.05 zote mbili)."""
    rng = np.random.default_rng(0)
    def mk():
        pve = rng.normal(0, 0.01, 1500)
        fwd = -0.3 * pve + rng.normal(0, 0.002, 1500)
        cost = np.full(1500, 0.00005)
        return evaluate(pve, fwd, cost, rng)
    a, b = mk(), mk()
    print(f"P1: net={a['net']:+.5f} p={a['p']:.3f} | P2: net={b['net']:+.5f} p={b['p']:.3f}")
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
