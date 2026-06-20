"""
mr_robustness.py — Je edge inategemea EMA200 tu? (parameter robustness, sio optimization).

Swali la Japhet: tukitumia EMA200 kwa pairs/TF zote, je ndio sababu pairs zingine zilishindwa?
Tunajibu kwa ROBUSTNESS (sio kutafuta EMA bora — hiyo ni overfit):
  Endesha sub-period stability (mr_validate) kwa EMA span = 50, 100, 200.
  - EURGBP ikibaki ROBUST kwenye ZOTE → edge ni halisi (sio knife-edge ya 200).
  - Pair iliyoshindwa ikiamka KWA UTHABITI (EMA nyingi) → ilifichwa na EMA200 (halisi).
    Ikiamka kwenye EMA moja tu → cherry-pick / overfit (sio halisi).

ROBUST = net>0 NA Phase B p<0.05 kwa vipindi VYOTE (P1 2016-2020, P2 2021-2024).
2025+ holdout HAIGUSWI.

Endesha (PC ya Japhet):  python src/models/mr_robustness.py
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

TF = "D1"
H = 5
EXT_Q = 0.80
N_PERM = 3000
MIN_N = 40
EMAS = [50, 100, 200]
PERIODS = [("P1", 2016, 2020), ("P2", 2021, 2024)]


def circ_perm(pos, fwd, n_perm, rng):
    obs = float(np.mean(pos * fwd)); n = len(pos); cnt = 1
    for _ in range(n_perm):
        s = int(rng.integers(2, n - 2))
        if np.mean(np.roll(pos, s) * fwd) >= obs:
            cnt += 1
    return cnt / (n_perm + 1)


def evaluate(pve, fwd, cost, rng):
    if len(pve) < 100:
        return None
    thr = np.quantile(np.abs(pve), EXT_Q)
    ext = np.where(np.abs(pve) >= thr)[0]
    kept = []; last = -H - 1
    for i in ext:
        if i - last >= H:
            kept.append(i); last = i
    kept = np.array(kept)
    if len(kept) < MIN_N:
        return None
    pos = -np.sign(pve[kept]); f, c = fwd[kept], cost[kept]
    nz = pos != 0; pos, f, c = pos[nz], f[nz], c[nz]
    if len(pos) < MIN_N:
        return None
    net = (pos * f - c).mean()
    p = circ_perm(pos, f, N_PERM, rng)
    return float(net), p


def _pip(s):
    return 0.01 if "JPY" in s.upper() else 0.0001


def features_full(pair, span):
    import polars as pl
    from data.dataset import load_candles
    c = pl.col("close")
    df = load_candles(pair, TF).with_columns(c.ewm_mean(span=span, min_samples=span).alias("ema"))
    df = df.with_columns(
        pl.col("bar_open").dt.year().alias("yr"),
        ((c - pl.col("ema")) / pl.col("ema")).alias("pve"),
        (c.shift(-H).log() - c.log()).alias("fwd"),
        (2 * pl.col("spread_mean_pips") * _pip(pair) / c).alias("cost"))
    d = df.select(["yr", "pve", "fwd", "cost"]).drop_nulls()
    return (d["yr"].to_numpy(), d["pve"].to_numpy(), d["fwd"].to_numpy(), d["cost"].to_numpy())


def robust(pair, span, rng):
    yr, pve, fwd, cost = features_full(pair, span)
    for _, y0, y1 in PERIODS:
        m = (yr >= y0) & (yr <= y1)
        r = evaluate(pve[m], fwd[m], cost[m], rng)
        if not (r and r[0] > 0 and r[1] < 0.05):
            return False
    return True


def main():
    sys.path.insert(0, str(REPO_ROOT / "src"))
    from data.dataset import config
    cfg = config()
    if not (REPO_ROOT / cfg["paths"]["processed"] / "candles").exists():
        print("HITILAFU: candles hazipo.", file=sys.stderr); return 1
    rng = np.random.default_rng(11)
    L = ["# Mean-Reversion — EMA Parameter Robustness\n",
         f"*Imezalishwa: {datetime.now():%Y-%m-%d %H:%M} | ROBUST = net>0 + p<0.05 vipindi VYOTE "
         f"(P1 2016-20, P2 2021-24) | EMA span 50/100/200 | sio optimization*\n",
         "| Pair | EMA50 | EMA100 | EMA200 | Hukumu |",
         "|------|-------|--------|--------|--------|"]
    for p in cfg["pairs"]:
        flags = {}
        for span in EMAS:
            try:
                flags[span] = robust(p, span, rng)
            except FileNotFoundError:
                flags[span] = None
        cnt = sum(1 for v in flags.values() if v)
        mark = lambda v: "✅" if v else ("—" if v is None else "❌")
        if cnt == 3:
            h = "🟢 thabiti (EMA zote)"
        elif cnt == 0:
            h = "❌ hakuna"
        else:
            h = f"⚠️ {cnt}/3 (fragile)"
        L.append(f"| {p} | {mark(flags[50])} | {mark(flags[100])} | {mark(flags[200])} | {h} |")
    L.append("\n---\n*🟢 ROBUST kwa EMA zote = edge halisi, haitegemei EMA200. "
             "⚠️ {1,2}/3 = inategemea EMA fulani → fragile/overfit-risk. ❌ = hakuna mean-reversion "
             "(pengine pair inatrend). **Kujibu swali:** kama EURGBP ni 🟢 na pair iliyoshindwa "
             "haiamki kwa uthabiti → EMA200 HAIKUWA tatizo; failures ni halisi.*")
    out = REPO_ROOT / cfg["paths"]["reports"] / "mr_robustness.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"Ripoti: {out.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
