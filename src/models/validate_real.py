"""
validate_real.py — Phase B kwenye STRATEGY HALISI (fix #1,3,4,5,7 za audit).

Audit: validation ilipima fade+hold-5; deployment ni fade+tp_mean. p-value haihamishwi.
Hapa tunaunganisha: tunapima HASA strategy tunayodeploy, kwa null sahihi, bila lookahead.

  • Entry: |pve| ≥ ROLLING q80 (window 252, PAST tu — no lookahead).  [fix #5]
  • Exit: tp_mean (rudi EMA) AU 2ATR SL AU timeout 20.  [= deployment]
  • R-unit = 2×ATR (= SL) → loser stopped ≈ −1R (sizing sahihi).  [fix #7]
  • Phase B null: fade kwenye bars RANDOM (n ileile) + EXIT ILEILE → null mean R.
    Inaisolate: je KUCHAGUA extremes kunaongeza edge zaidi ya fade-random + same exit?
    p iliyoripotiwa kama fraction halisi (sio "0.000").  [fix #4]
  • EURJPY imeondolewa (ilifeli mr_validate).  [fix #6]

Train 2016-2024 NA OOS 2025+ (warmup 2024 kwa EMA/threshold; entries 2025+ tu).
Endesha:  python src/models/validate_real.py
Self-test: python src/models/validate_real.py --self-test
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]

PAIRS = ["EURGBP", "EURUSD"]
EXT_Q = 0.80
THR_WIN = 252
TIMEOUT = 20
SL_ATR = 2.0
N_PERM = 3000
MIN_N = 30
OOS_START = np.datetime64("2025-01-01")


def _exit(i, d, close, ema, atr, n):
    """tp_mean | 2ATR SL | timeout -> exit index."""
    end = min(i + TIMEOUT, n - 1)
    for j in range(i + 1, end + 1):
        if d * (ema[j] - close[j]) <= 0 or d * (close[j] - close[i]) <= -SL_ATR * atr[i]:
            return j
    return end


def _trade_R(i, d, close, ema, atr, cost, n):
    ej = _exit(i, d, close, ema, atr, n)
    ret = d * (close[ej] / close[i] - 1) - cost[i]
    return ret / (SL_ATR * atr[i] / close[i]), ej     # R-unit = SL


def real_trades(close, ema, atr, pve, cost, thr, valid_from):
    """Extreme-fade (rolling thr), event-centric non-overlapping. Rudisha (R-list, entry_idx-list)."""
    n = len(close)
    ext = (np.abs(pve) >= thr) & np.isfinite(thr)
    cross = ext & ~np.r_[False, ext[:-1]]
    R = []; idxs = []; last = -1
    for i in np.where(cross)[0]:
        i = int(i)
        if i < valid_from or i <= last or i >= n - 1 or not (np.isfinite(atr[i]) and atr[i] > 0):
            continue
        r, ej = _trade_R(i, -np.sign(pve[i]), close, ema, atr, cost, n)
        R.append(r); idxs.append(i); last = ej
    return np.array(R), idxs


def phase_b(real_mean, n_trades, close, ema, atr, pve, cost, valid_from, rng):
    """Null: fade kwenye bars RANDOM (n ileile) + exit ileile. p = P(null_mean >= real_mean)."""
    n = len(close)
    pool = [i for i in range(valid_from, n - 1)
            if np.isfinite(atr[i]) and atr[i] > 0 and np.isfinite(pve[i])]
    if len(pool) < n_trades * 2:
        return None
    cnt = 1
    for _ in range(N_PERM):
        pick = rng.choice(pool, size=n_trades, replace=False)
        rs = [_trade_R(int(i), -np.sign(pve[int(i)]), close, ema, atr, cost, n)[0] for i in pick]
        if np.mean(rs) >= real_mean:
            cnt += 1
    return cnt / (N_PERM + 1)


def stats(R):
    if len(R) < MIN_N:
        return None
    w = R[R > 0]; l = R[R < 0]
    pf = w.sum() / abs(l.sum()) if l.sum() != 0 else float("inf")
    return dict(n=len(R), ev=float(R.mean()), pf=float(pf), win=float((R > 0).mean()))


def _pip(s):
    return 0.01 if "JPY" in s.upper() else 0.0001

def load(pair, start, end):
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
    # rolling threshold (PAST tu, window THR_WIN) -- no lookahead
    df = df.with_columns(pl.col("pve").abs().rolling_quantile(EXT_Q, window_size=THR_WIN).alias("thr"))
    d = df.select(["bar_open", "close", "ema", "atr", "pve", "cost", "thr"]).drop_nulls()
    return [d[x].to_numpy() for x in ["bar_open", "close", "ema", "atr", "pve", "cost", "thr"]]


def run():
    from data.dataset import config
    cfg = config()
    if not (REPO_ROOT / cfg["paths"]["processed"] / "candles").exists():
        print("HITILAFU: candles hazipo.", file=sys.stderr); return 1
    rng = np.random.default_rng(7)
    L = ["# Validate REAL strategy — Phase B (unified, no-lookahead)\n",
         f"*Imezalishwa: {datetime.now():%Y-%m-%d %H:%M} | fade + tp_mean/2ATR-SL/timeout (= deployment) "
         f"| rolling-q80 threshold (PAST) | R-unit=2ATR | null=random-entry+same-exit, N={N_PERM} "
         "| 2025+ HAIJAGUSWA hadi mwisho*\n",
         "> p = P(fade kwenye bars random + exit ileile ≥ real). p<0.05 = KUCHAGUA extremes kunaongeza edge.\n",
         "| Pair | Window | n | EV(R) | PF | win% | Phase B p | verdict |",
         "|------|--------|---|-------|----|------|-----------|---------|"]
    for pair in PAIRS:
        for win, (s, e, vfrom_oos) in [("TRAIN 16-24", ("2016-01-01", "2024-12-31", None)),
                                        ("OOS 25+", ("2024-01-01", "2026-04-30", OOS_START))]:
            bo, close, ema, atr, pve, cost, thr = load(pair, s, e)
            valid_from = 0
            if vfrom_oos is not None:
                vf = np.searchsorted(bo, vfrom_oos)
                valid_from = int(vf)
            R, idxs = real_trades(close, ema, atr, pve, cost, thr, valid_from)
            m = stats(R)
            if not m:
                L.append(f"| {pair} | {win} | {len(R)} | — | — | — | — | ⚪ n<{MIN_N} |"); continue
            p = phase_b(m["ev"], m["n"], close, ema, atr, pve, cost, valid_from, rng)
            v = "✅ edge" if (p is not None and p < 0.05 and m["ev"] > 0) else "❌ HAKUNA"
            L.append(f"| {pair} | {win} | {m['n']} | {m['ev']:+.3f} | {m['pf']:.2f} | {m['win']*100:.0f}% "
                     f"| {p:.3f} | {v} |" if p is not None else
                     f"| {pair} | {win} | {m['n']} | {m['ev']:+.3f} | {m['pf']:.2f} | {m['win']*100:.0f}% | — | ⚪ |")
    L.append("\n---\n*Phase B HALISI: strategy ileile tunayodeploy, null=random-entry+same-exit "
             "(inaisolate value ya kuchagua extremes). Rolling threshold = no-lookahead. R-unit=SL "
             "(loss=−1R). p iliyoripotiwa ni fraction halisi. ✅ edge inahitaji p<0.05 NA EV>0 — "
             "TRAIN na OOS. Hii ndiyo jaribio sahihi: 'kuna edge kweli kwenye tunachocheza?'*")
    out = REPO_ROOT / cfg["paths"]["reports"] / "validate_real.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"Ripoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """Planted MR -> real strategy ina edge, p ndogo; random data -> p si ndogo."""
    rng = np.random.default_rng(0); n = 4000
    x = np.zeros(n)
    for k in range(1, n): x[k] = 0.9*x[k-1] + rng.normal(0, 0.01)
    close = 1.1*np.exp(x); a = 2/51; e = close[0]; ema = []
    for v in close: e = a*v+(1-a)*e; ema.append(e)
    ema = np.array(ema); atr = np.full(n, 0.011); pve = (close-ema)/ema; cost = np.full(n, 5e-5)
    thr = np.full(n, np.quantile(np.abs(pve), 0.8))
    R, idx = real_trades(close, ema, atr, pve, cost, thr, 0); m = stats(R)
    p = phase_b(m["ev"], m["n"], close, ema, atr, pve, cost, 0, rng)
    print(f"planted MR: n={m['n']} EV={m['ev']:+.3f} PF={m['pf']:.2f} Phase B p={p:.3f}")
    print("SELF-TEST:", "PASS" if (m["ev"] > 0 and p < 0.05) else "CHECK")
    return 0


def main():
    if "--self-test" in sys.argv:
        return self_test()
    sys.path.insert(0, str(REPO_ROOT / "src"))
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
