"""
conditional_edge.py — DOCTRINE layer C: je signal ina edge inayoTOFAUTIANA kwa REGIME?

Regime detector (regime.py) ni imara. Sasa swali la edge: chukua signal (fade-extreme =
mean-reversion lead), pima net win-rate (baada ya cost) NDANI ya kila regime. Kama regime
fulani (mf. LV-RANGE) ina win >0.55 thabiti → architecture (Model1 regime → Model2 signal)
inalipa. Zote ~0.50 → regime haisaidii signal hii.

Signal: position-in-range E2=(close−min)/(max−min); extreme E2≥0.8 (top)→SHORT,
≤0.2 (bottom)→LONG (fade). Net = baada ya round-trip spread. NO-LOOKAHEAD, non-overlapping.
Regime = vol-state × structure (kutoka regime.py, median split).

Endesha (PC ya Japhet):  python src/models/conditional_edge.py
Self-test (popote):       python src/models/conditional_edge.py --self-test
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
from models.regime import label_regimes, REGIME_NAMES  # noqa: E402

TFS = ["D1", "H4"]
H = {"D1": 5, "H4": 10}
WIN = {"D1": 20, "H4": 20}
TOP, BOT = 0.80, 0.20


def win_by_regime(e2, regime, fwd, cost):
    """Kwa kila regime: net win-rate ya fade kati ya bars za extreme position."""
    top = e2 >= TOP
    bot = e2 <= BOT
    pos = np.where(top, -1.0, np.where(bot, 1.0, 0.0))   # FADE (mean-reversion)
    out = {}
    for r in range(4):
        m = (pos != 0) & (regime == r)
        n = int(m.sum())
        if n < 30:
            out[r] = (n, None, None); continue
        net = pos[m] * fwd[m] - cost[m]
        out[r] = (n, float((net > 0).mean()), float(net.mean()))
    return out


# ───────────────────────── DATA PATH ─────────────────────────

def _pip(s):
    return 0.01 if "JPY" in s.upper() else 0.0001


def evaluate_pair_tf(pair, tf):
    import polars as pl
    from data.dataset import load_candles
    n, h = WIN[tf], H[tf]
    c = pl.col("close")
    df = load_candles(pair, tf).with_columns((c.log() - c.log().shift(1)).alias("ret"))
    df = df.with_columns(
        c.rolling_min(window_size=n).alias("lo"), c.rolling_max(window_size=n).alias("hi"),
        pl.col("ret").rolling_std(window_size=n).alias("vol"),
        ((c - c.shift(n)).abs() / (c - c.shift(1)).abs().rolling_sum(window_size=n)).alias("er"),
        (c.shift(-h).log() - c.log()).alias("fwd"),
        (2 * pl.col("spread_mean_pips") * _pip(pair) / c).alias("cost"),
    )
    df = df.with_columns(((c - pl.col("lo")) / (pl.col("hi") - pl.col("lo"))).alias("e2"))
    d = df.select(["e2", "vol", "er", "fwd", "cost"]).drop_nulls().gather_every(h)  # non-overlap
    if d.height < 200:
        return None
    regime, _ = label_regimes(d["vol"].to_numpy(), d["er"].to_numpy())
    return win_by_regime(d["e2"].to_numpy(), regime, d["fwd"].to_numpy(), d["cost"].to_numpy())


def run():
    from data.dataset import config
    cfg = config()
    if not (REPO_ROOT / cfg["paths"]["processed"] / "candles").exists():
        print("HITILAFU: candles hazipo.", file=sys.stderr); return 1
    agg = {tf: {r: [0, 0.0, 0.0] for r in range(4)} for tf in TFS}
    for tf in TFS:
        for p in cfg["pairs"]:
            try:
                r = evaluate_pair_tf(p, tf)
            except FileNotFoundError:
                continue
            if not r:
                continue
            for rg in range(4):
                nn, win, mret = r[rg]
                if win is not None:
                    agg[tf][rg][0] += nn; agg[tf][rg][1] += win * nn; agg[tf][rg][2] += mret * nn
        print(f"  [{tf}] done")

    L = ["# DOCTRINE Layer C — Fade-Extreme Edge × Regime\n",
         f"*Imezalishwa: {datetime.now():%Y-%m-%d %H:%M} | fade |E2| extreme, net baada ya cost | "
         "regime=vol×structure | non-overlapping | pairs=9*\n",
         "> Swali: je mean-reversion (fade) ina edge inayoTOFAUTIANA kwa regime? "
         "LV-RANGE win >0.55 = architecture inalipa. Zote ~0.50 = regime haisaidii.\n"]
    for tf in TFS:
        L.append(f"\n## {tf}\n")
        L.append("| Regime | extreme bars | fade net win | mean net |")
        L.append("|--------|--------------|--------------|----------|")
        for r in range(4):
            n, wsum, rsum = agg[tf][r]
            if n == 0:
                L.append(f"| {REGIME_NAMES[r]} | 0 | — | — |"); continue
            win = wsum / n
            flag = "  ⬅️" if abs(win - 0.5) >= 0.03 else ""
            L.append(f"| {REGIME_NAMES[r]} | {n:,} | {win:.3f}{flag} | {rsum/n:+.6f} |")
    L.append("\n---\n*fade net win = mean-reversion baada ya spread, ndani ya kila regime. "
             "**Cha kuangalia:** je regime fulani (hasa LV-RANGE / LV-TREND) ina win >0.55 "
             "thabiti kwenye TF/pairs? Hiyo = regime inaconditioning edge → Model1→Model2 "
             "inalipa → Phase B. Zote ~0.50 = regime haitenganishi edge → fikiri upya.*")
    out = REPO_ROOT / cfg["paths"]["reports"] / "conditional_edge.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"Ripoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """Planted: fade inafanya kazi TU kwenye LV-RANGE (regime 0). -> regime 0 win>0.55, zingine ~0.5."""
    rng = np.random.default_rng(0)
    n = 40000
    e2 = rng.uniform(0, 1, n)
    regime = rng.integers(0, 4, n)
    top = e2 >= TOP; bot = e2 <= BOT
    pos = np.where(top, -1.0, np.where(bot, 1.0, 0.0))
    # fade inalipa (fwd upande wa pos) TU kwenye regime 0
    fwd = np.where(regime == 0, 0.002 * pos, 0.0) + rng.normal(0, 0.003, n)
    cost = np.full(n, 0.00003)
    r = win_by_regime(e2, regime, fwd, cost)
    for rg in range(4):
        print(f"  {REGIME_NAMES[rg]}: n={r[rg][0]:5d} fade_win={r[rg][1]:.3f}")
    ok = r[0][1] > 0.55 and all(abs(r[k][1] - 0.5) < 0.05 for k in (1, 2, 3))
    print("\nSELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if "--self-test" in sys.argv:
        return self_test()
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
