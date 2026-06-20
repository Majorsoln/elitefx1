"""
model2_mr.py — MODEL 2: EURGBP mean-reversion kama STRATEGY (triple-barrier).

Edge iliyothibitishwa (mr_validate): EURGBP D1 mean-reversion, thabiti sub-periods.
Hapa tunaigeuza kuwa STRATEGY halisi na exits za triple-barrier (sio forward-return fixed):
  ENTRY : |price_vs_ema| ≥ q80 (extreme) → FADE (juu→short, chini→long)
  EXITS (first-hit):
    TP   : bei inarudi MEAN (close inavuka EMA200) — lengo la mean-reversion
    SL   : adverse move ≥ SL_ATR × ATR(14)
    TIME : timeout baada ya TIMEOUT bars
Parameters FIXED (hazijatune — DOCTRINE §6). Cost = round-trip spread. Non-overlapping
(trade mpya baada ya iliyopita kufungwa). Train 2016–2024 TU; 2025+ holdout HAIGUSWI.

Inatoa trade stats: n, win%, profit factor, expectancy, total return, max DD.

Endesha (PC ya Japhet):  python src/models/model2_mr.py
Self-test (popote):       python src/models/model2_mr.py --self-test
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]

PAIRS = ["EURGBP", "AUDUSD", "EURUSD"]     # robust/borderline kutoka mr_validate
EXT_Q = 0.80
SL_ATR = 1.5
TIMEOUT = 15
TRAIN_END = "2024-12-31"


def backtest(close, ema, atr, pve, cost):
    """Event-driven triple-barrier. Rudisha list ya pnl-returns (baada ya cost)."""
    thr = np.quantile(np.abs(pve[np.isfinite(pve)]), EXT_Q)
    n = len(close)
    trades = []
    i = 1
    while i < n - 1:
        if not (np.isfinite(pve[i]) and abs(pve[i]) >= thr and np.isfinite(atr[i]) and atr[i] > 0):
            i += 1; continue
        direction = -np.sign(pve[i])           # FADE
        entry = close[i]
        sl_dist = SL_ATR * atr[i]
        exit_j = min(i + TIMEOUT, n - 1)
        for j in range(i + 1, min(i + TIMEOUT, n - 1) + 1):
            adverse = direction * (close[j] - entry)
            if adverse <= -sl_dist:            # SL
                exit_j = j; break
            if direction * (ema[j] - close[j]) <= 0:   # rudi mean -> TP
                exit_j = j; break
            exit_j = j
        ret = direction * (close[exit_j] / entry - 1) - cost[i]
        trades.append(float(ret))
        i = exit_j + 1                          # non-overlapping
    return trades


def stats(trades):
    t = np.array(trades)
    if len(t) < 10:
        return None
    wins = t[t > 0]; losses = t[t < 0]
    pf = wins.sum() / abs(losses.sum()) if losses.sum() != 0 else float("inf")
    eq = np.cumprod(1 + t)
    dd = float((1 - eq / np.maximum.accumulate(eq)).max())
    return dict(n=len(t), win=float((t > 0).mean()), pf=float(pf),
                exp_bps=float(t.mean() * 1e4), total=float(eq[-1] - 1), maxdd=dd)


# ───────────────────────── DATA PATH ─────────────────────────

def _pip(s):
    return 0.01 if "JPY" in s.upper() else 0.0001


def arrays(pair):
    import polars as pl
    from data.dataset import load_candles
    c, h, l = pl.col("close"), pl.col("high"), pl.col("low")
    df = load_candles(pair, "D1", end=TRAIN_END).with_columns(
        c.ewm_mean(span=200, min_samples=200).alias("ema"),
        pl.max_horizontal(h - l, (h - c.shift(1)).abs(), (l - c.shift(1)).abs()).alias("tr"))
    df = df.with_columns(
        pl.col("tr").ewm_mean(alpha=1/14, min_samples=14).alias("atr"),
        ((c - pl.col("ema")) / pl.col("ema")).alias("pve"),
        (2 * pl.col("spread_mean_pips") * _pip(pair) / c).alias("cost"))
    d = df.select(["close", "ema", "atr", "pve", "cost"]).drop_nulls()
    return (d["close"].to_numpy(), d["ema"].to_numpy(), d["atr"].to_numpy(),
            d["pve"].to_numpy(), d["cost"].to_numpy())


def run():
    from data.dataset import config
    cfg = config()
    if not (REPO_ROOT / cfg["paths"]["processed"] / "candles").exists():
        print("HITILAFU: candles hazipo.", file=sys.stderr); return 1
    L = ["# Model 2 — EURGBP Mean-Reversion Strategy (triple-barrier, TRAIN)\n",
         f"*Imezalishwa: {datetime.now():%Y-%m-%d %H:%M} | D1, fade extreme, TP=rudi-mean / "
         f"SL={SL_ATR}×ATR / timeout={TIMEOUT} | cost imo | TRAIN 2016–2024 | 2025+ HAIJAGUSWA*\n",
         "| Pair | trades | win% | profit factor | expectancy (bps) | total ret | max DD |",
         "|------|--------|------|---------------|------------------|-----------|--------|"]
    for p in PAIRS:
        try:
            close, ema, atr, pve, cost = arrays(p)
        except FileNotFoundError:
            continue
        s = stats(backtest(close, ema, atr, pve, cost))
        if not s:
            L.append(f"| {p} | <10 trades | — | — | — | — | — |"); continue
        L.append(f"| {p} | {s['n']} | {s['win']*100:.1f}% | {s['pf']:.2f} | {s['exp_bps']:+.1f} "
                 f"| {s['total']*100:+.1f}% | {s['maxdd']*100:.1f}% |")
    L.append("\n---\n*Profit factor >1.2 + expectancy +ve + max DD ndogo = strategy ina afya "
             "(TRAIN). PF≈1.0 = hakuna edge baada ya exits halisi. **Hii ni TRAIN tu** — "
             "ikionyesha afya, hatua ya mwisho ni **OOS 2025+ (mara MOJA, bila tuning).** "
             "Parameters (SL_ATR, timeout) ni FIXED, hazijatune.*")
    out = REPO_ROOT / cfg["paths"]["reports"] / "model2_mr.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"Ripoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """Synthetic mean-reverting (Ornstein-Uhlenbeck) -> fade ina PF>1."""
    rng = np.random.default_rng(0)
    n = 3000
    x = np.zeros(n)                            # log-price deviation from mean (mean-reverting)
    for k in range(1, n):
        x[k] = 0.9 * x[k-1] + rng.normal(0, 0.01)
    close = 1.1 * np.exp(x)
    ema = 1.1 * np.exp(0.0 * x)                # mean ≈ 1.1 (EMA ya kweli ingekuwa karibu)
    ema = np.full(n, np.nan);
    # EMA rahisi (span 50) kwa test
    a = 2/51; e = close[0]
    ema_l = []
    for v in close:
        e = a*v + (1-a)*e; ema_l.append(e)
    ema = np.array(ema_l)
    atr = np.full(n, 0.01*1.1)
    pve = (close - ema) / ema
    cost = np.full(n, 0.00005)
    s = stats(backtest(close, ema, atr, pve, cost))
    print(f"  trades={s['n']} win={s['win']:.3f} PF={s['pf']:.2f} exp={s['exp_bps']:+.1f}bps")
    ok = s and s["pf"] > 1.1 and s["exp_bps"] > 0
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if "--self-test" in sys.argv:
        return self_test()
    sys.path.insert(0, str(REPO_ROOT / "src"))
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
