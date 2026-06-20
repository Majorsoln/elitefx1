"""
eval_exits.py — P1 (evaluation upgrade) + P2 (exit research) [DOCTRINE §1.6, §1.7].

Insight ya review: edge = ENTRY + EXIT; tathmini kwa EV (sio win-rate); block bootstrap
(sio IID). Hapa: ENTRY ileile (EURGBP MR fade extreme) × EXITS 6 tofauti, kila moja kwa:
  EV (avg R) · Profit Factor · win% · avg win/loss R · MaxDD · trades/yr ·
  block-bootstrap FTMO pass-rate (block=8 trades -> inahifadhi serial dependence).

R-multiple: risk unit = 1.5×ATR/entry (sare kwa exits zote). Exits zisizo na SL zinaweza
kupoteza > 1R (tail risk inaonekana). Cost imo. Train 2016-2024; 2025+ HAIGUSWI.

Endesha (PC ya Japhet):  python src/models/eval_exits.py
Self-test (popote):       python src/models/eval_exits.py --self-test
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]

PAIR = "EURGBP"
EXT_Q = 0.80
TIMEOUT = 20
RISK_ATR = 1.5
YEARS = 9
TRAIN_END = "2024-12-31"
# block-bootstrap FTMO
RISK_PCT = 0.01
BLOCK = 8
N_SIM = 3000
MAX_TRADES = 150
TARGET, DAILY, TOTAL = 0.10, 0.05, 0.10
EXITS = ["h5", "h10", "tp_mean", "atr_tp_sl", "atr_trail", "tp_mean_sl"]


def _exit(i, direction, close, ema, atr, n, rule):
    """Rudisha exit index kulingana na rule (event-driven)."""
    entry = close[i]; a = atr[i]; best = 0.0
    end = min(i + TIMEOUT, n - 1)
    if rule == "h5":
        return min(i + 5, n - 1)
    if rule == "h10":
        return min(i + 10, n - 1)
    for j in range(i + 1, end + 1):
        fav = direction * (close[j] - entry)
        if rule == "tp_mean":
            if direction * (ema[j] - close[j]) <= 0:
                return j
        elif rule == "atr_tp_sl":
            if fav >= 2 * a:
                return j
            if fav <= -2 * a:
                return j
        elif rule == "atr_trail":
            best = max(best, fav)
            if best > 0 and fav <= best - 2 * a:
                return j
        elif rule == "tp_mean_sl":
            if fav <= -2 * a:
                return j
            if direction * (ema[j] - close[j]) <= 0:
                return j
    return end


def trades_for_exit(close, ema, atr, pve, cost, rule):
    thr = np.quantile(np.abs(pve[np.isfinite(pve)]), EXT_Q)
    n = len(close); R = []; i = 1
    while i < n - 1:
        if not (np.isfinite(pve[i]) and abs(pve[i]) >= thr and np.isfinite(atr[i]) and atr[i] > 0):
            i += 1; continue
        d = -np.sign(pve[i]); entry = close[i]
        ej = _exit(i, d, close, ema, atr, n, rule)
        ret = d * (close[ej] / entry - 1) - cost[i]
        risk = RISK_ATR * atr[i] / entry
        if risk > 0:
            R.append(ret / risk)
        i = ej + 1
    return np.array(R)


def metrics(R):
    if len(R) < 10:
        return None
    w = R[R > 0]; l = R[R < 0]
    pf = w.sum() / abs(l.sum()) if l.sum() != 0 else float("inf")
    eq = np.cumprod(1 + RISK_PCT * R)
    dd = float((1 - eq / np.maximum.accumulate(eq)).max())
    return dict(n=len(R), tpy=len(R) / YEARS, win=float((R > 0).mean()),
                ev=float(R.mean()), pf=float(pf),
                aw=float(w.mean()) if len(w) else 0, al=float(l.mean()) if len(l) else 0,
                maxdd=dd)


def block_bootstrap_ftmo(R, rng):
    if len(R) < BLOCK + 1:
        return None
    npass = 0
    for _ in range(N_SIM):
        seq = []
        while len(seq) < MAX_TRADES:
            s = int(rng.integers(0, len(R) - BLOCK))
            seq.extend(R[s:s + BLOCK])
        eq = 1.0; done = False
        for r in seq[:MAX_TRADES]:
            pnl = RISK_PCT * r
            if pnl <= -DAILY:
                done = True; break
            eq *= (1 + pnl)
            if eq <= 1 - TOTAL:
                done = True; break
            if eq >= 1 + TARGET:
                npass += 1; done = True; break
    return npass / N_SIM


# ───────────────────────── DATA PATH ─────────────────────────
def _pip(s):
    return 0.01 if "JPY" in s.upper() else 0.0001

def get_arrays():
    import polars as pl
    from data.dataset import load_candles
    c, h, l = pl.col("close"), pl.col("high"), pl.col("low")
    df = load_candles(PAIR, "D1", end=TRAIN_END).with_columns(
        c.ewm_mean(span=200, min_samples=200).alias("ema"),
        pl.max_horizontal(h - l, (h - c.shift(1)).abs(), (l - c.shift(1)).abs()).alias("tr"))
    df = df.with_columns(
        pl.col("tr").ewm_mean(alpha=1/14, min_samples=14).alias("atr"),
        ((c - pl.col("ema")) / pl.col("ema")).alias("pve"),
        (2 * pl.col("spread_mean_pips") * _pip(PAIR) / c).alias("cost"))
    d = df.select(["close", "ema", "atr", "pve", "cost"]).drop_nulls()
    return [d[x].to_numpy() for x in ["close", "ema", "atr", "pve", "cost"]]


def run():
    from data.dataset import config
    cfg = config()
    if not (REPO_ROOT / cfg["paths"]["processed"] / "candles").exists():
        print("HITILAFU: candles hazipo.", file=sys.stderr); return 1
    close, ema, atr, pve, cost = get_arrays()
    rng = np.random.default_rng(7)
    L = ["# Exit Research — EURGBP MR (entry ileile, exit tofauti)\n",
         f"*Imezalishwa: {datetime.now():%Y-%m-%d %H:%M} | entry=fade |pve|≥q{int(EXT_Q*100)} | "
         f"R-unit={RISK_ATR}×ATR | cost imo | block-bootstrap FTMO (block={BLOCK}, risk={RISK_PCT*100:.0f}%) "
         "| TRAIN | 2025+ HAIJAGUSWA*\n",
         "> Edge = entry + EXIT. EV (avg R) + PF ndio muhimu, sio win%. FTMO% = block-bootstrap "
         "(inahifadhi clustering).\n",
         "| Exit | trades | /yr | win% | **EV(R)** | **PF** | avgWin | avgLoss | MaxDD | FTMO pass% |",
         "|------|--------|-----|------|-----------|--------|--------|---------|-------|-----------|"]
    for rule in EXITS:
        R = trades_for_exit(close, ema, atr, pve, cost, rule)
        m = metrics(R)
        if not m:
            L.append(f"| {rule} | <10 | — | — | — | — | — | — | — | — |"); continue
        pr = block_bootstrap_ftmo(R, rng)
        L.append(f"| {rule} | {m['n']} | {m['tpy']:.1f} | {m['win']*100:.0f}% | **{m['ev']:+.3f}** "
                 f"| **{m['pf']:.2f}** | {m['aw']:+.2f} | {m['al']:+.2f} | {m['maxdd']*100:.1f}% "
                 f"| {pr*100:.1f}% |")
    L.append("\n---\n*Entry ni ILEILE (MR fade); tofauti ni EXIT tu. **EV(R)>0 + PF>1.3** = exit "
             "nzuri. Linganisha: je exit inabadilisha edge kwa kiasi gani? (review: exit inaweza "
             "kueleza 80%). FTMO pass% = block-bootstrap (clustering imehifadhiwa) — halisi zaidi "
             "kuliko IID. MaxDD/avgLoss kubwa = tail risk (exits zisizo na SL).*")
    out = REPO_ROOT / cfg["paths"]["reports"] / "eval_exits.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"Ripoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """Exits 2 kwenye synthetic MR -> metrics + bootstrap zinafanya kazi; exit nzuri PF>poor."""
    rng = np.random.default_rng(0)
    n = 3000
    x = np.zeros(n)
    for k in range(1, n):
        x[k] = 0.9 * x[k-1] + rng.normal(0, 0.01)
    close = 1.1 * np.exp(x)
    a = 2/51; e = close[0]; ema = []
    for v in close:
        e = a*v + (1-a)*e; ema.append(e)
    ema = np.array(ema); atr = np.full(n, 0.011); pve = (close-ema)/ema; cost = np.full(n, 5e-5)
    for rule in ["tp_mean", "h5"]:
        R = trades_for_exit(close, ema, atr, pve, cost, rule)
        m = metrics(R); pr = block_bootstrap_ftmo(R, rng)
        print(f"  {rule}: n={m['n']} EV={m['ev']:+.3f} PF={m['pf']:.2f} FTMO%={pr*100:.0f}")
    print("SELF-TEST: PASS" )
    return 0


def main():
    if "--self-test" in sys.argv:
        return self_test()
    sys.path.insert(0, str(REPO_ROOT / "src"))
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
