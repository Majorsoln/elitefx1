"""
mean_reversion_edge.py — TEST #3: Fade-extreme (mean-reversion) NA COST + Phase B.

Lead pekee inayojirudia (condition_scan + Test #2): bei ikiwa EXTREME kutoka EMA200,
inaelekea KURUDI (mean-reversion). Hapa tunaipima kwa UKALI:
  - Signal: |price_vs_ema| >= quantile (extreme) -> position = −sign(pve) (FADE).
  - Forward return (non-overlapping) MINUS round-trip spread cost (spread_mean_pips halisi).
  - Phase B: circular-shift permutation null -> je timing inazidi bahati?
Tunalenga D1/H4 (moves >> spread). Washauri wote wameuliza cost — tunaijibu.

NO-LOOKAHEAD: signal bar t; fwd t->t+h. Cost = 2 × spread × pip / price (enter+exit).

Endesha (PC ya Japhet):  python src/models/mean_reversion_edge.py
Self-test (popote):       python src/models/mean_reversion_edge.py --self-test
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]

TFS = ["D1", "H4"]
H = {"D1": 5, "H4": 10}
EXT_Q = 0.80          # extreme = |price_vs_ema| kwenye 20% ya juu
N_PERM = 5000
SEED = 11


def circ_perm(pos, fwd, n_perm, rng):
    """Circular-shift permutation: je mean(pos·fwd) inazidi null (timing skill)?"""
    obs = float(np.mean(pos * fwd))
    n = len(pos)
    cnt = 1
    for _ in range(n_perm):
        s = int(rng.integers(5, n - 5))
        if np.mean(np.roll(pos, s) * fwd) >= obs:
            cnt += 1
    return obs, cnt / (n_perm + 1)


def evaluate(pve, fwd, cost, rng):
    """pve, fwd, cost = arrays (non-overlapping, extreme bars tu zimebaki nje).
    Rudisha gross/net/win/p au None."""
    if len(pve) < 60:
        return None
    pos = -np.sign(pve)                      # FADE: above -> short, below -> long
    nz = pos != 0
    pos, fwd, cost = pos[nz], fwd[nz], cost[nz]
    if len(pos) < 60:
        return None
    gross = pos * fwd
    net = gross - cost                        # cost daima inapunguza
    obs, p = circ_perm(pos, fwd, N_PERM, rng)
    return dict(n=len(pos), gross=float(gross.mean()), cost=float(cost.mean()),
                net=float(net.mean()), win_net=float((net > 0).mean()), p_sh=p)


# ───────────────────────── DATA PATH ─────────────────────────

def _pip(sym):
    return 0.01 if "JPY" in sym.upper() else 0.0001


def evaluate_pair_tf(pair, tf, rng):
    import polars as pl
    from data.dataset import load_candles
    h = H[tf]
    c = pl.col("close")
    df = load_candles(pair, tf).with_columns(c.ewm_mean(span=200, min_samples=200).alias("ema"))
    df = df.with_columns(
        ((c - pl.col("ema")) / pl.col("ema")).alias("pve"),
        (c.shift(-h).log() - c.log()).alias("fwd"),
        # round-trip cost kama return: 2 × spread_pips × pip / close
        (2 * pl.col("spread_mean_pips") * _pip(pair) / c).alias("cost"),
    )
    d = df.select(["pve", "fwd", "cost"]).drop_nulls().gather_every(h)   # non-overlapping
    pve = d["pve"].to_numpy()
    if len(pve) < 100:
        return None
    thr = np.quantile(np.abs(pve), EXT_Q)
    m = np.abs(pve) >= thr                                                # extreme tu
    res = evaluate(pve[m], d["fwd"].to_numpy()[m], d["cost"].to_numpy()[m], rng)
    if res:
        res.update(pair=pair, tf=tf)
    return res


def run():
    from data.dataset import config
    cfg = config()
    if not (REPO_ROOT / cfg["paths"]["processed"] / "candles").exists():
        print("HITILAFU: candles hazipo.", file=sys.stderr); return 1
    rng = np.random.default_rng(SEED)
    rows = []
    for tf in TFS:
        for p in cfg["pairs"]:
            try:
                r = evaluate_pair_tf(p, tf, rng)
            except FileNotFoundError:
                continue
            if r:
                rows.append(r)
        print(f"  [{tf}] done")

    L = ["# Trend Structure #3 — Fade-Extreme (Mean-Reversion) + Cost + Phase B\n",
         f"*Imezalishwa: {datetime.now():%Y-%m-%d %H:%M} | fade |price_vs_ema|≥q{int(EXT_Q*100)} | "
         f"NET = baada ya round-trip spread | circular-shift perm N={N_PERM} | non-overlapping*\n",
         "> Signal: bei extreme juu→SHORT, extreme chini→LONG (fade). p_sh<0.05 NA net>0 = "
         "edge halisi baada ya gharama. Hii ni lead pekee iliyojirudia.\n"]
    for tf in TFS:
        L.append(f"\n## {tf} (fwd={H[tf]})\n")
        L.append("| Pair | n | gross | cost | **net** | win(net) | p_sh | edge? |")
        L.append("|------|---|-------|------|---------|----------|------|-------|")
        for r in [x for x in rows if x["tf"] == tf]:
            edge = "✅" if (r["p_sh"] < 0.05 and r["net"] > 0) else "❌"
            L.append(f"| {r['pair']} | {r['n']:,} | {r['gross']:+.5f} | {r['cost']:.5f} "
                     f"| **{r['net']:+.5f}** | {r['win_net']:.3f} | {r['p_sh']:.4f} | {edge} |")
    L.append("\n---\n*gross = fade return kabla ya cost; net = baada ya round-trip spread. "
             "**✅ inahitaji p_sh<0.05 NA net>0** (significant NA inalipa baada ya gharama). "
             "Kama net hasi licha ya gross+ve → spread inakula edge (hasa TF ndogo). "
             "Kama ✅ kwa pairs nyingi → mean-reversion ni edge halisi ya mwelekeo (sio trend).*")
    out = REPO_ROOT / cfg["paths"]["reports"] / "mean_reversion_edge.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"Ripoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """Planted: extreme pve -> fwd inarudi (mean-reversion). Fade inapaswa net>0, p_sh<0.05.
    Random -> p_sh ~uniform (si significant)."""
    rng = np.random.default_rng(0)
    n = 3000
    pve = rng.normal(0, 0.01, n)
    fwd_mr = -0.3 * pve + rng.normal(0, 0.002, n)     # bei inarudi (mean-reversion)
    fwd_rd = rng.normal(0, 0.002, n)
    cost = np.full(n, 0.00005)
    rp = evaluate(pve, fwd_mr, cost, rng)
    rr = evaluate(pve, fwd_rd, cost, rng)
    print(f"PLANTED MR: net={rp['net']:+.5f} win={rp['win_net']:.3f} p_sh={rp['p_sh']:.4f} "
          f"(tarajio net>0, p_sh<0.05)")
    print(f"RANDOM:     net={rr['net']:+.5f} win={rr['win_net']:.3f} p_sh={rr['p_sh']:.4f} "
          f"(tarajio p_sh si ndogo)")
    ok = rp["p_sh"] < 0.05 and rp["net"] > 0 and rr["p_sh"] > 0.05
    print("\nSELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if "--self-test" in sys.argv:
        return self_test()
    sys.path.insert(0, str(REPO_ROOT / "src"))
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
