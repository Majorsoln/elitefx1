"""
scan_all.py — Systematic edge scan: method × KILA pair (DOCTRINE/METHODS).

Kila method (rules halisi) inapimwa kwa pairs ZOTE 9, kwa nidhamu ileile:
sub-period stability (P1 2016-20, P2 2021-24) + Phase B (circular-shift) + cost,
fixed-horizon h=5, non-overlapping. ROBUST = net>0 NA p<0.05 vipindi VYOTE.

Methods (D1, data tunayonayo):
  mr        : fade |price−EMA200| ≥ q80           (mean-reversion)
  range     : fade E2=(close−lo20)/(hi20−lo20) extreme (≥0.8/≤0.2)
  breakout  : follow Donchian-20 break (close > max high / < min low)
  trend     : follow sign(EMA200 slope), |slope|≥median
  pullback  : follow trend (close vs EMA200, slope) wakati dip (close vs EMA50)
  vol_mr    : fade |pve|≥q80 NA vol≥median        (vol-conditional MR)

Multiple-testing: combos 6×9=54; ROBUST inahitaji p<0.05 VIPINDI VYOTE
(P(bahati)=0.0025/combo → ~0.13 false ROBUST jumla). Survivor = halisi.
2025+ HAIGUSWI.

Endesha (PC ya Japhet):  python src/models/scan_all.py
Self-test (popote):       python src/models/scan_all.py --self-test
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]

H = 5
N_PERM = 1000
MIN_N = 35
EMA_LONG, EMA_SHORT, DONCH, SLOPE_K = 200, 50, 20, 20
TFS = ["D1", "H4", "H2", "H1"]
PERIODS = [("P1", 2016, 2020), ("P2", 2021, 2024)]
TRAIN_END = "2024-12-31"


# ───────── method position functions (F = dict ya numpy arrays) ─────────
def m_mr(F):
    pve = F["pve"]; thr = np.nanquantile(np.abs(pve), 0.80)
    return np.where(np.abs(pve) >= thr, -np.sign(pve), 0.0)

def m_range(F):
    e2 = F["e2"]
    return np.where(e2 >= 0.8, -1.0, np.where(e2 <= 0.2, 1.0, 0.0))

def m_breakout(F):
    return np.where(F["brk_up"], 1.0, np.where(F["brk_dn"], -1.0, 0.0))

def m_trend(F):
    s = F["slope"]; thr = np.nanquantile(np.abs(s), 0.50)
    return np.where(np.abs(s) >= thr, np.sign(s), 0.0)

def m_pullback(F):
    up = (F["close"] > F["ema_l"]) & (F["slope"] > 0) & (F["close"] < F["ema_s"])
    dn = (F["close"] < F["ema_l"]) & (F["slope"] < 0) & (F["close"] > F["ema_s"])
    return np.where(up, 1.0, np.where(dn, -1.0, 0.0))

def m_vol_mr(F):
    pve = F["pve"]; thr = np.nanquantile(np.abs(pve), 0.80)
    vhi = F["vol"] >= np.nanmedian(F["vol"])
    return np.where((np.abs(pve) >= thr) & vhi, -np.sign(pve), 0.0)

METHODS = {"mr": m_mr, "range": m_range, "breakout": m_breakout,
           "trend": m_trend, "pullback": m_pullback, "vol_mr": m_vol_mr}


def circ_perm(pos, fwd, rng):
    obs = float(np.mean(pos * fwd)); n = len(pos); cnt = 1
    for _ in range(N_PERM):
        s = int(rng.integers(2, n - 2))
        if np.mean(np.roll(pos, s) * fwd) >= obs:
            cnt += 1
    return cnt / (N_PERM + 1)


def eval_period(pos, fwd, cost, rng):
    idx = np.where((pos != 0) & np.isfinite(fwd) & np.isfinite(cost))[0]
    kept = []; last = -H - 1
    for i in idx:
        if i - last >= H:
            kept.append(i); last = i
    kept = np.array(kept)
    if len(kept) < MIN_N:
        return None
    p_ = pos[kept]; ret = p_ * fwd[kept] - cost[kept]
    return float(ret.mean()), circ_perm(p_, fwd[kept], rng), len(kept)


def robust(pos, F, rng):
    ok = True; nets = []
    for _, y0, y1 in PERIODS:
        m = (F["yr"] >= y0) & (F["yr"] <= y1)
        r = eval_period(pos[m], F["fwd"][m], F["cost"][m], rng)
        if r is None:
            return None
        net, p, n = r; nets.append(net)
        if not (net > 0 and p < 0.05):
            ok = False
    return ok, nets


# ───────────────────────── DATA PATH ─────────────────────────
def _pip(s):
    return 0.01 if "JPY" in s.upper() else 0.0001

def features(pair, tf):
    import polars as pl
    from data.dataset import load_candles
    c, h, l = pl.col("close"), pl.col("high"), pl.col("low")
    df = load_candles(pair, tf, end=TRAIN_END).with_columns(
        c.ewm_mean(span=EMA_LONG, min_samples=EMA_LONG).alias("ema_l"),
        c.ewm_mean(span=EMA_SHORT, min_samples=EMA_SHORT).alias("ema_s"),
        (c.log() - c.log().shift(1)).alias("ret"),
        h.rolling_max(DONCH).shift(1).alias("dhi"),
        l.rolling_min(DONCH).shift(1).alias("dlo"),
        c.rolling_min(DONCH).alias("lo20"), c.rolling_max(DONCH).alias("hi20"))
    df = df.with_columns(
        pl.col("bar_open").dt.year().alias("yr"),
        ((c - pl.col("ema_l")) / pl.col("ema_l")).alias("pve"),
        ((pl.col("ema_l") / pl.col("ema_l").shift(SLOPE_K)) - 1).alias("slope"),
        ((c - pl.col("lo20")) / (pl.col("hi20") - pl.col("lo20"))).alias("e2"),
        pl.col("ret").rolling_std(DONCH).alias("vol"),
        (c > pl.col("dhi")).alias("brk_up"), (c < pl.col("dlo")).alias("brk_dn"),
        (c.shift(-H).log() - c.log()).alias("fwd"),
        (2 * pl.col("spread_mean_pips") * _pip(pair) / c).alias("cost"))
    cols = ["yr", "close", "ema_l", "ema_s", "pve", "slope", "e2", "vol",
            "brk_up", "brk_dn", "fwd", "cost"]
    d = df.select(cols).drop_nulls()
    return {k: d[k].to_numpy() for k in cols}


def run():
    from data.dataset import config
    cfg = config()
    if not (REPO_ROOT / cfg["paths"]["processed"] / "candles").exists():
        print("HITILAFU: candles hazipo.", file=sys.stderr); return 1
    rng = np.random.default_rng(7)
    pairs = cfg["pairs"]
    grid = {}; survivors = []
    for tf in TFS:
        for p in pairs:
            try:
                F = features(p, tf)
            except FileNotFoundError:
                continue
            for name, fn in METHODS.items():
                res = robust(fn(F), F, rng)
                grid[(tf, name, p)] = res
                if res and res[0]:
                    survivors.append((name, p, tf, res[1]))
        print(f"  [{tf}] done")

    L = ["# Systematic Edge Scan — Method × Pair × Timeframe\n",
         f"*Imezalishwa: {datetime.now():%Y-%m-%d %H:%M} | ROBUST(✅)=net>0 + Phase B p<0.05 "
         f"VIPINDI VYOTE | h={H} bars, cost imo | {len(METHODS)} methods × {len(pairs)} pairs × "
         f"{len(TFS)} TF | 2025+ HAIJAGUSWA*\n",
         "> ✅=robust survivor; ❌=fail; ·=sample ndogo. Multiple-testing: stringent (p<0.05 vipindi vyote).\n"]
    for tf in TFS:
        L.append(f"\n## {tf}\n")
        L.append("| Method | " + " | ".join(pairs) + " |")
        L.append("|" + "---|" * (len(pairs) + 1))
        for name in METHODS:
            cells = []
            for p in pairs:
                r = grid.get((tf, name, p))
                cells.append("✅" if (r and r[0]) else ("❌" if r else "·"))
            L.append(f"| {name} | " + " | ".join(cells) + " |")
    L.append(f"\n## Survivors ({len(survivors)})\n")
    if survivors:
        for n, p, tf, nets in survivors:
            L.append(f"- **{n} / {p} / {tf}** — net P1={nets[0]:+.5f}, P2={nets[1]:+.5f}")
    else:
        L.append("HAKUNA")
    L.append("\n---\n*ROBUST inahitaji p<0.05 vipindi VYOTE → stringent. Survivors = wagombea wa "
             "edge → OOS ndio mwisho. Intraday-specific (#9/10/11 session), carry (#7/15 rate "
             "data) zinahitaji handling tofauti (hazipo hapa). h=5 bars per TF.*")
    out = REPO_ROOT / cfg["paths"]["reports"] / "scan_all.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nSurvivors: {[(n,p,tf) for n,p,tf,_ in survivors]}")
    print(f"Ripoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """Planted: 'mr' method ifanye kazi pair bandia. Thibitisha harness inagundua."""
    rng = np.random.default_rng(0)
    n = 3000
    yr = np.repeat(np.arange(2016, 2025), n // 9 + 1)[:n]
    pve = rng.normal(0, 0.01, n)
    fwd = -0.3 * pve + rng.normal(0, 0.003, n)      # MR: fade pve inalipa
    F = dict(yr=yr, pve=pve, fwd=fwd, cost=np.full(n, 0.00005))
    pos = np.where(np.abs(pve) >= np.quantile(np.abs(pve), 0.8), -np.sign(pve), 0.0)
    r = robust(pos, F, rng)
    print(f"planted MR robust={r[0]} nets={[round(x,5) for x in r[1]]}")
    # random -> not robust
    F2 = dict(F); F2["fwd"] = rng.normal(0, 0.003, n)
    r2 = robust(pos, F2, rng)
    print(f"random robust={r2[0]}")
    ok = r[0] and not r2[0]
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if "--self-test" in sys.argv:
        return self_test()
    sys.path.insert(0, str(REPO_ROOT / "src"))
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
