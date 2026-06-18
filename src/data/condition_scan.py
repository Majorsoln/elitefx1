"""
condition_scan.py — Scan ya UWAZI ya conditions za EMA200 kwenye data halisi.

Lengo: kuonyesha kwa uwazi — kwa kila condition (close vs EMA200, pamoja na thresholds/
extremes), **bars NGAPI zime-meet**, na **nini kilitokea baadaye** (win-rate + mean
forward return). Hakuna IC/p-value — hesabu na matokeo wazi tu.

Condition zinatumia price_vs_ema = (close − EMA200)/EMA200. Direction ya trend-following:
  above/far/extreme ABOVE  -> LONG  (tunatarajia bei ipande zaidi)
  below/far/extreme BELOW  -> SHORT (tunatarajia bei ishuke zaidi)
Win = forward return iko upande wa trade. Thresholds = quantiles per (pair, tf)
(robust). NO-LOOKAHEAD: condition bar t, forward return t -> t+h.

Endesha (PC ya Japhet):  python src/data/condition_scan.py
Self-test (popote):       python src/data/condition_scan.py --self-test
Inatoa reports/condition_scan.md
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

TFS = ["D1", "H4", "H1"]
H = {"D1": 5, "H4": 10, "H1": 12}        # forward holding (bars) kwa kila TF
# (condition_name, implied_direction)  — direction: +1 LONG, -1 SHORT
COND_DEFS = [
    ("above (pve>0)",        +1),
    ("below (pve<0)",        -1),
    ("far_above (>=q70)",    +1),
    ("far_below (<=q30)",    -1),
    ("extreme_above (>=q90)", +1),
    ("extreme_below (<=q10)", -1),
]


def scan_arrays(pve, fwd, q):
    """pve, fwd = numpy arrays (zilizosafishwa). q = dict ya quantiles.
    Rudisha dict: cond -> (n, win_rate, mean_dir_ret)."""
    import numpy as np
    masks = {
        "above (pve>0)":        pve > 0,
        "below (pve<0)":        pve < 0,
        "far_above (>=q70)":    pve >= q["q70"],
        "far_below (<=q30)":    pve <= q["q30"],
        "extreme_above (>=q90)": pve >= q["q90"],
        "extreme_below (<=q10)": pve <= q["q10"],
    }
    out = {}
    for name, direction in COND_DEFS:
        m = masks[name]
        n = int(m.sum())
        if n == 0:
            out[name] = (0, None, None)
            continue
        dir_ret = direction * fwd[m]          # return upande wa trade
        win = float((dir_ret > 0).mean())     # win-rate ya directional bet
        out[name] = (n, win, float(dir_ret.mean()))
    return out


# ───────────────────────── DATA PATH (polars/dataset.py) ─────────────────────────

def scan_pair_tf(pair, tf):
    import numpy as np
    import polars as pl
    from data.dataset import load_candles

    h = H[tf]
    df = load_candles(pair, tf)
    c = pl.col("close")
    df = df.with_columns(c.ewm_mean(span=200, min_samples=200).alias("ema"))
    df = df.with_columns(((c - pl.col("ema")) / pl.col("ema")).alias("pve"))
    df = df.with_columns((c.shift(-h).log() - c.log()).alias("fwd"))
    d = df.select(["pve", "fwd"]).drop_nulls()
    pve = d["pve"].to_numpy()
    fwd = d["fwd"].to_numpy()
    q = {"q70": float(np.quantile(pve, 0.70)), "q30": float(np.quantile(pve, 0.30)),
         "q90": float(np.quantile(pve, 0.90)), "q10": float(np.quantile(pve, 0.10))}
    return scan_arrays(pve, fwd, q), len(pve)


def run():
    from data.dataset import config
    cfg = config()
    pairs = cfg["pairs"]
    if not (REPO_ROOT / cfg["paths"]["processed"] / "candles").exists():
        print("HITILAFU: candles hazipo. Endesha build_candles.py kwanza.", file=sys.stderr)
        return 1

    # agg[tf][cond] = [list ya (n, win, mean_ret) per pair] + total_bars
    L = ["# Condition Scan — EMA200 (data halisi)\n",
         f"*Imezalishwa: {datetime.now():%Y-%m-%d %H:%M} | price_vs_ema = (close−EMA200)/EMA200 | "
         "win = forward return upande wa trade | NO-lookahead*\n",
         "> Trend-following: above→LONG, below→SHORT. Win-rate ~0.50 = bahati (hakuna edge); "
         ">0.50 thabiti = edge.\n"]
    for tf in TFS:
        L.append(f"\n## {tf}  (forward holding = {H[tf]} bars)\n")
        L.append("| Condition | dir | total bars | % ya data | win-rate | mean fwd ret |")
        L.append("|-----------|-----|-----------|-----------|----------|--------------|")
        agg = {name: [0, 0.0, 0.0, 0] for name, _ in COND_DEFS}  # n, win_sum*n, ret_sum*n, npairs
        grand = 0
        for p in pairs:
            res, total = scan_pair_tf(p, tf)
            grand += total
            for name, _ in COND_DEFS:
                n, win, mret = res[name]
                if n > 0:
                    agg[name][0] += n
                    agg[name][1] += win * n      # weighted kwa n
                    agg[name][2] += mret * n
                    agg[name][3] += 1
        for name, direction in COND_DEFS:
            n, wsum, rsum, _ = agg[name]
            d = "LONG" if direction > 0 else "SHORT"
            if n == 0:
                L.append(f"| {name} | {d} | 0 | — | — | — |")
                continue
            win = wsum / n
            mret = rsum / n
            pct = 100.0 * n / grand if grand else 0
            flag = "  ⬅️" if abs(win - 0.5) >= 0.03 else ""
            L.append(f"| {name} | {d} | {n:,} | {pct:.1f}% | {win:.3f}{flag} | {mret:+.5f} |")
    L.append("\n---\n*Win-rate ni wastani (weighted kwa bars) wa pairs 9. **⬅️** = win-rate "
             "inatofautiana na 0.50 kwa ≥0.03 (mshukiwa wa edge — angalia kama thabiti kwa "
             "TF/condition zote). Kama zote ~0.50 hata kwenye extremes → trend-following "
             "haina edge ya mwelekeo, hata kwa thresholds.*")
    out = REPO_ROOT / cfg["paths"]["reports"] / "condition_scan.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"Ripoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """Thibitisha logic: planted trend (above EMA -> inaendelea juu) -> win>0.5;
    random walk -> win~0.5."""
    import numpy as np
    rng = np.random.default_rng(0)
    n = 20000
    # planted: forward return inategemea sign ya pve (trend-following inafanya kazi)
    pve = rng.normal(0, 0.01, n)
    fwd_trend = 0.5 * pve + rng.normal(0, 0.005, n)     # above -> +fwd
    fwd_rand = rng.normal(0, 0.005, n)
    q = {"q70": float(np.quantile(pve, .70)), "q30": float(np.quantile(pve, .30)),
         "q90": float(np.quantile(pve, .90)), "q10": float(np.quantile(pve, .10))}
    rt = scan_arrays(pve, fwd_trend, q)
    rr = scan_arrays(pve, fwd_rand, q)
    print("PLANTED trend (tarajio win > 0.5):")
    for nm, _ in COND_DEFS:
        print(f"  {nm:24s} n={rt[nm][0]:6d} win={rt[nm][1]:.3f}")
    print("RANDOM (tarajio win ~ 0.50):")
    for nm, _ in COND_DEFS:
        print(f"  {nm:24s} n={rr[nm][0]:6d} win={rr[nm][1]:.3f}")
    ok = rt["extreme_above (>=q90)"][1] > 0.55 and abs(rr["above (pve>0)"][1] - 0.5) < 0.03
    print("\nSELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if "--self-test" in sys.argv:
        return self_test()
    sys.path.insert(0, str(REPO_ROOT / "src"))
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
