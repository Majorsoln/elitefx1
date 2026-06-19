"""
regime_signal.py — TEST #4: Position-in-Range (E2) × Volatility (C1) — ushauri wa washauri.

Hypothesis (B): signal ileile (bei iko juu/chini ya range) ina maana TOFAUTI kwa vol:
  - LOW vol  + bei extreme -> MEAN-REVERSION (inarudi)  -> continuation win < 0.50
  - HIGH vol + bei extreme -> BREAKOUT       (inaendelea)-> continuation win > 0.50

Signal: E2 = (close − min_N)/(max_N − min_N) ∈ [0,1] (position-in-range, descriptive).
  extreme = E2>=0.8 (top) au E2<=0.2 (bottom). Continuation position: top->+1, bottom->−1.
Conditioner: vol (rolling std) -> quartiles. Win = net (baada ya cost) upande wa continuation.
NO-LOOKAHEAD: E2/vol bar t; fwd t->t+h. Non-overlapping. Cost = round-trip spread.

Operationalization ya reframe: regime (vol) inaconditioning signal (E2). Inajenga juu ya
Test #3 (mean-reversion at extremes), sasa kwa signal safi + conditioner proven (IC 0.19).

Endesha (PC ya Japhet):  python src/models/regime_signal.py
Self-test (popote):       python src/models/regime_signal.py --self-test
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]

TFS = ["D1", "H4"]
H = {"D1": 5, "H4": 10}
RANGE_N = {"D1": 10, "H4": 20}        # window ya range & vol
TOP, BOT = 0.80, 0.20                 # extreme position thresholds


def continuation_by_vol(e2, vol, fwd, cost):
    """Kwa kila vol quartile: continuation win-rate (net) kati ya bars za extreme position."""
    top = e2 >= TOP
    bot = e2 <= BOT
    pos = np.where(top, 1.0, np.where(bot, -1.0, 0.0))   # follow breakout direction
    vq = np.digitize(vol, np.quantile(vol, [0.25, 0.50, 0.75]))   # 0..3
    out = {}
    for q in range(4):
        m = (pos != 0) & (vq == q)
        n = int(m.sum())
        if n < 30:
            out[q] = (n, None, None); continue
        net = pos[m] * fwd[m] - cost[m]
        out[q] = (n, float((net > 0).mean()), float(net.mean()))
    return out


# ───────────────────────── DATA PATH ─────────────────────────

def _pip(s):
    return 0.01 if "JPY" in s.upper() else 0.0001


def evaluate_pair_tf(pair, tf):
    import polars as pl
    from data.dataset import load_candles
    n, h = RANGE_N[tf], H[tf]
    c = pl.col("close")
    df = load_candles(pair, tf).with_columns(
        c.rolling_min(window_size=n).alias("lo"),
        c.rolling_max(window_size=n).alias("hi"),
        (c.log() - c.log().shift(1)).alias("ret"),
    )
    df = df.with_columns(
        ((c - pl.col("lo")) / (pl.col("hi") - pl.col("lo"))).alias("e2"),
        pl.col("ret").rolling_std(window_size=n).alias("vol"),
        (c.shift(-h).log() - c.log()).alias("fwd"),
        (2 * pl.col("spread_mean_pips") * _pip(pair) / c).alias("cost"),
    )
    d = df.select(["e2", "vol", "fwd", "cost"]).drop_nulls().gather_every(h)  # non-overlapping
    if d.height < 200:
        return None
    return continuation_by_vol(d["e2"].to_numpy(), d["vol"].to_numpy(),
                               d["fwd"].to_numpy(), d["cost"].to_numpy())


def run():
    from data.dataset import config
    cfg = config()
    if not (REPO_ROOT / cfg["paths"]["processed"] / "candles").exists():
        print("HITILAFU: candles hazipo.", file=sys.stderr); return 1
    # agg[tf][q] = [n, win*n, ret*n]
    agg = {tf: {q: [0, 0.0, 0.0] for q in range(4)} for tf in TFS}
    for tf in TFS:
        for p in cfg["pairs"]:
            try:
                r = evaluate_pair_tf(p, tf)
            except FileNotFoundError:
                continue
            if not r:
                continue
            for q in range(4):
                nn, win, mret = r[q]
                if win is not None:
                    agg[tf][q][0] += nn
                    agg[tf][q][1] += win * nn
                    agg[tf][q][2] += mret * nn
        print(f"  [{tf}] done")

    L = ["# Trend Structure #4 — Position-in-Range × Volatility\n",
         f"*Imezalishwa: {datetime.now():%Y-%m-%d %H:%M} | E2=(close−min)/(max−min); extreme "
         f"≥{TOP}/≤{BOT}; continuation (breakout) net baada ya cost | vol quartiles | non-overlap*\n",
         "> Hypothesis: LOW-vol (Q1) → mean-reversion (win <0.50); HIGH-vol (Q4) → breakout "
         "(win >0.50). Kama win inaflip na vol → regime inaconditioning signal (edge).\n"]
    for tf in TFS:
        L.append(f"\n## {tf} (range={RANGE_N[tf]}, fwd={H[tf]})\n")
        L.append("| Vol quartile | extreme bars | continuation win | mean net |")
        L.append("|--------------|--------------|------------------|----------|")
        names = {0: "Q1 (LOW vol)", 3: "Q4 (HIGH vol)"}
        for q in range(4):
            n, wsum, rsum = agg[tf][q]
            if n == 0:
                L.append(f"| {names.get(q, f'Q{q+1}')} | 0 | — | — |"); continue
            win = wsum / n
            flag = "  ⬅️" if abs(win - 0.5) >= 0.03 else ""
            L.append(f"| {names.get(q, f'Q{q+1}')} | {n:,} | {win:.3f}{flag} | {rsum/n:+.6f} |")
    L.append("\n---\n*continuation win = bet ya BREAKOUT (top→long, bottom→short), net baada "
             "ya spread. **Cha kuangalia:** je Q1 (low-vol) <0.50 (mean-reversion) NA Q4 "
             "(high-vol) >0.50 (breakout)? Flip hiyo = regime inaconditioning signal → edge "
             "→ Phase B. Zote ~0.50 = E2×vol haisaidii. Zote <0.50 = mean-reversion kila vol "
             "(= Test #3, vol haiongezi).*")
    out = REPO_ROOT / cfg["paths"]["reports"] / "regime_signal.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"Ripoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """Planted: low-vol -> mean-reversion (continuation FAILS); high-vol -> breakout (works)."""
    rng = np.random.default_rng(0)
    n = 40000
    e2 = rng.uniform(0, 1, n)
    vol = rng.uniform(0, 1, n)
    top = e2 >= TOP; bot = e2 <= BOT
    pos = np.where(top, 1.0, np.where(bot, -1.0, 0.0))
    # high vol -> fwd inafuata pos (breakout); low vol -> fwd kinyume (mean-rev)
    sign_eff = np.where(vol > 0.5, 1.0, -1.0)
    fwd = 0.002 * pos * sign_eff + rng.normal(0, 0.002, n)
    cost = np.full(n, 0.00003)
    r = continuation_by_vol(e2, vol, fwd, cost)
    for q in range(4):
        print(f"  Q{q+1} (vol {'LOW' if q==0 else 'HIGH' if q==3 else 'mid'}): "
              f"n={r[q][0]:5d} continuation_win={r[q][1]:.3f}")
    ok = r[0][1] < 0.45 and r[3][1] > 0.55     # low-vol mean-rev, high-vol breakout
    print("\nSELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if "--self-test" in sys.argv:
        return self_test()
    sys.path.insert(0, str(REPO_ROOT / "src"))
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
