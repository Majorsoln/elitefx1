"""
portfolio.py — EUR MR system: TRAIN portfolio FTMO + OOS (holdout). VERDICT-driven.

REKEBISHO (baada ya audit):
  • BUG ya OOS contamination IMEREKEBISHWA: warmup 2024 inatumika kwa EMA TU; trades
    zinachujwa entry_date ≥ 2025-01-01 (hakuna 2024/train inayoingia OOS).
  • Footer/ verdict ni CONDITIONAL kutoka nambari (PASS/FAIL/INCONCLUSIVE), sio template.
  • EURJPY IMEONDOLEWA (ilifeli mr_validate sub-period ❌ — gate ya KABLA ya OOS).
  • False precision imepunguzwa; n inaonyeshwa wazi.

ONYO: holdout 2025+ ni SHOT MOJA. Ikifeli, ni fail — hatupati ku-re-pick portfolio
baada ya kuiona. Edge mpya inahitaji holdout mpya/iliyobaki.

Edges: MR-fade (entry EVENT |pve|≥q80, exit tp_mean) — EURGBP (robust), EURUSD (borderline).
Endesha:  python src/models/portfolio.py        (train)
          python src/models/portfolio.py --oos   (holdout — shot moja)
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]

EUR_PAIRS = ["EURGBP", "EURUSD"]            # EURJPY imeondolewa (ilifeli mr_validate)
EXT_Q = 0.80
TIMEOUT = 20
RISK_ATR = 1.5
RISK_PCT = 0.01
BLOCK = 8
N_SIM = 4000
N_PERM = 2000
MAX_TRADES = 250
MIN_VERDICT_N = 30                          # chini ya hii = INCONCLUSIVE
TARGET, DAILY, TOTAL = 0.10, 0.05, 0.10
TRAIN = ("2016-01-01", "2024-12-31")
OOS_START = np.datetime64("2025-01-01")
YEARS_TRAIN = 9


def _cross_into(cond):
    c = cond.astype(bool)
    return np.where(c & ~np.r_[False, c[:-1]])[0]


def gen_trades(bar_open, close, ema, atr, pve, cost):
    """MR-fade (event) + tp_mean exit -> list ya (entry_date, R)."""
    thr = np.nanquantile(np.abs(pve), EXT_Q)
    idx = _cross_into(np.abs(pve) >= thr); n = len(close); out = []; last = -1
    for i in idx:
        i = int(i)
        if i <= last or i < 1 or i >= n - 1 or not (np.isfinite(atr[i]) and atr[i] > 0):
            continue
        d = -np.sign(pve[i]); ej = min(i + TIMEOUT, n - 1)
        for j in range(i + 1, min(i + TIMEOUT, n - 1) + 1):
            if d * (ema[j] - close[j]) <= 0 or d * (close[j] - close[i]) <= -2 * atr[i]:
                ej = j; break
        R = (d * (close[ej] / close[i] - 1) - cost[i]) / (RISK_ATR * atr[i] / close[i])
        out.append((bar_open[i], float(R))); last = ej
    return out


def m_stats(R):
    R = np.asarray(R)
    if len(R) == 0:
        return None
    w = R[R > 0]; l = R[R < 0]
    pf = w.sum() / abs(l.sum()) if l.sum() != 0 else float("inf")
    eq = np.cumprod(1 + RISK_PCT * R); dd = float((1 - eq / np.maximum.accumulate(eq)).max())
    return dict(n=len(R), ev=float(R.mean()), pf=float(pf), win=float((R > 0).mean()),
                total=float(eq[-1] - 1), maxdd=dd)


def verdict(m):
    if not m or m["n"] < MIN_VERDICT_N:
        return f"⚪ INCONCLUSIVE (n={m['n'] if m else 0} < {MIN_VERDICT_N})"
    return "✅ PASS" if (m["pf"] > 1.2 and m["ev"] > 0) else "❌ FAIL"


def perm_p(R, rng):
    """Phase B: je mean(R) inazidi null ya sign-flip? (random ±1 weights)."""
    R = np.asarray(R); obs = R.mean(); n = len(R); cnt = 1
    for _ in range(N_PERM):
        if (R * rng.choice([-1.0, 1.0], n)).mean() >= obs:
            cnt += 1
    return cnt / (N_PERM + 1)


def portfolio_mc(R, rng):
    R = np.asarray(R)
    if len(R) < BLOCK + 1:
        return None, None
    npass = 0; ttp = []
    for _ in range(N_SIM):
        seq = []
        while len(seq) < MAX_TRADES:
            s = int(rng.integers(0, len(R) - BLOCK)); seq.extend(R[s:s+BLOCK])
        eq = 1.0
        for t, r in enumerate(seq[:MAX_TRADES], 1):
            pnl = RISK_PCT * r
            if pnl <= -DAILY: break
            eq *= (1 + pnl)
            if eq <= 1 - TOTAL: break
            if eq >= 1 + TARGET:
                npass += 1; ttp.append(t); break
    return npass / N_SIM, (np.median(ttp) if ttp else None)


def _pip(s):
    return 0.01 if "JPY" in s.upper() else 0.0001

def arrays(pair, start, end):
    import polars as pl
    from data.dataset import load_candles
    c, h, l = pl.col("close"), pl.col("high"), pl.col("low")
    df = load_candles(pair, "D1", start=start, end=end).with_columns(
        c.ewm_mean(span=200, min_samples=200).alias("ema"),
        pl.max_horizontal(h - l, (h - c.shift(1)).abs(), (l - c.shift(1)).abs()).alias("tr"))
    df = df.with_columns(
        pl.col("tr").ewm_mean(alpha=1/14, min_samples=14).alias("atr"),
        ((c - pl.col("ema")) / pl.col("ema")).alias("pve"),
        (2 * pl.col("spread_mean_pips") * _pip(pair) / c).alias("cost"))
    d = df.select(["bar_open", "close", "ema", "atr", "pve", "cost"]).drop_nulls()
    return [d[x].to_numpy() for x in ["bar_open", "close", "ema", "atr", "pve", "cost"]]


def run(oos):
    from data.dataset import config
    cfg = config()
    if not (REPO_ROOT / cfg["paths"]["processed"] / "candles").exists():
        print("HITILAFU: candles hazipo.", file=sys.stderr); return 1
    rng = np.random.default_rng(7)
    label = "OOS 2025–2026/04 (HELDOUT — shot moja)" if oos else "TRAIN 2016–2024"
    per = {}; pool = []
    for p in EUR_PAIRS:
        s, e = ("2024-01-01", "2026-04-30") if oos else TRAIN
        trades = gen_trades(*arrays(p, s, e))
        if oos:   # REKEBISHO: chuja kweli 2025+ (warmup 2024 haihesabiwi)
            trades = [(dt, r) for dt, r in trades if dt >= OOS_START]
        R = [r for _, r in trades]
        per[p] = m_stats(R); pool.extend(R)

    pm = m_stats(pool)
    L = [f"# Portfolio — EUR MR System ({label})\n",
         f"*Imezalishwa: {datetime.now():%Y-%m-%d %H:%M} | MR-fade event + tp_mean exit | risk "
         f"{RISK_PCT*100:.0f}%/trade | cost imo | EURJPY imeondolewa (ilifeli mr_validate)*\n"]
    # VERDICT juu kabisa
    L.append(f"## VERDICT: {verdict(pm)}\n")
    L.append("| Pair | n | EV(R) | PF | win% | total | MaxDD | verdict |")
    L.append("|------|---|-------|----|------|-------|-------|---------|")
    for p in EUR_PAIRS:
        m = per[p]
        if not m:
            L.append(f"| {p} | 0 | — | — | — | — | — | ⚪ |"); continue
        L.append(f"| {p} | {m['n']} | {m['ev']:+.2f} | {m['pf']:.2f} | {m['win']*100:.0f}% "
                 f"| {m['total']*100:+.1f}% | {m['maxdd']*100:.1f}% | {verdict(m)} |")
    if pm:
        L.append(f"\n**Portfolio:** n={pm['n']}, EV={pm['ev']:+.2f}R, PF={pm['pf']:.2f}, "
                 f"total={pm['total']*100:+.1f}%, MaxDD={pm['maxdd']*100:.1f}%")
        pp = perm_p(pool, rng)
        L.append(f"- **Phase B** (permutation null): p = {pp:.3f} "
                 f"({'edge > bahati' if pp < 0.05 else 'HAIZIDI bahati'})")
    if not oos and pm:
        pr, ttp = portfolio_mc(pool, rng); tpy = len(pool) / YEARS_TRAIN
        yrs = f"{ttp/tpy:.1f}" if ttp and tpy else "—"
        L.append(f"- portfolio trades/yr ≈ {tpy:.0f} | FTMO pass (block-bootstrap) {pr*100:.0f}% "
                 f"| median trades→pass {ttp} → ≈ {yrs} years")
    L.append(f"\n---\n*VERDICT inatokana na nambari: PASS = PF>1.2 NA EV>0 NA n≥{MIN_VERDICT_N}; "
             "vinginevyo FAIL/INCONCLUSIVE. OOS: warmup 2024 (EMA tu) → trades 2025+ TU "
             "(contamination imerekebishwa). Holdout = SHOT MOJA: ikifeli, ni fail — hatupati "
             "ku-re-pick. n ndogo OOS = INCONCLUSIVE, sio ushindi.*")
    out = REPO_ROOT / cfg["paths"]["reports"] / ("portfolio_oos.md" if oos else "portfolio_train.md")
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"VERDICT: {verdict(pm)} | Ripoti: {out.relative_to(REPO_ROOT)}")
    return 0


def main():
    sys.path.insert(0, str(REPO_ROOT / "src"))
    return run("--oos" in sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
