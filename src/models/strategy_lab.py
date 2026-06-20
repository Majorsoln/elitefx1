"""
strategy_lab.py — Engine MOJA ya pamoja (inatumia review kiujumla).

Inaapply:
  • EVENT-centric: entry = trigger kwenye TRANSITION bar (crossing), sio kila bar yenye state.
  • Edge = ENTRY + EXIT: kila method ina exit yake (tp_mean kwa MR; atr_tp_sl kwa momentum).
  • EV-metrics (sio win%): EV(R), PF, MaxDD, trades/yr.
  • Methods ZOTE × pairs ZOTE 9 (sio pair moja).
  • PORTFOLIO FTMO: kusanya survivors -> block-bootstrap account-level pass-rate (HAPA FTMO
    inapimwa, sio pair moja).
Sub-period stability (P1/P2) + cost. Train 2016-2024; 2025+ HAIGUSWI. Risk unit = 1.5×ATR.

Methods (event-centric, D1; intraday/carry zaongezwa baadaye):
  mr_stretch  : event=|pve| inavuka INTO ≥q80 ; FADE ; exit tp_mean
  range_fade  : event=E2 inavuka INTO ≥0.8/≤0.2 ; FADE ; exit tp_mean
  breakout    : event=close inavuka Donchian-hi/lo ; FOLLOW ; exit atr_tp_sl
  vol_expand  : event=vol inavuka chini→juu median ; FOLLOW momentum ; exit atr_tp_sl
  trend_flip  : event=EMA slope inavuka 0 ; FOLLOW new dir ; exit atr_tp_sl
  pullback    : event=trend-up NA close inagusa EMA (pullback) ; FOLLOW ; exit tp_mean

Endesha (PC ya Japhet):  python src/models/strategy_lab.py
Self-test (popote):       python src/models/strategy_lab.py --self-test
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]

TF = "D1"
TIMEOUT = 20
RISK_ATR = 1.5
EXT_Q = 0.80
YEARS = 9
TRAIN_END = "2024-12-31"
PERIODS = [(2016, 2020), (2021, 2024)]
# portfolio FTMO
RISK_PCT = 0.01
BLOCK = 8
N_SIM = 3000
MAX_TRADES = 200
TARGET, DAILY, TOTAL = 0.10, 0.05, 0.10


# ───────── EVENT-centric entries: rudisha (idx, direction) ─────────
def _cross_into(cond):
    """Index ambapo cond inakuwa True ikitoka False (transition INTO state)."""
    c = cond.astype(bool)
    return np.where(c & ~np.r_[False, c[:-1]])[0]

def ev_mr_stretch(F):
    pve = F["pve"]; thr = np.nanquantile(np.abs(pve), EXT_Q)
    idx = _cross_into(np.abs(pve) >= thr)
    return idx, -np.sign(pve[idx])

def ev_range_fade(F):
    e2 = F["e2"]
    idx = _cross_into((e2 >= 0.8) | (e2 <= 0.2))
    return idx, np.where(e2[idx] >= 0.8, -1.0, 1.0)

def ev_breakout(F):
    up = _cross_into(F["close"] > F["dhi"]); dn = _cross_into(F["close"] < F["dlo"])
    idx = np.r_[up, dn]; dirs = np.r_[np.ones(len(up)), -np.ones(len(dn))]
    o = np.argsort(idx); return idx[o], dirs[o]

def ev_vol_expand(F):
    idx = _cross_into(F["vol"] >= np.nanmedian(F["vol"]))
    # follow momentum ya bar ya event
    d = np.sign(F["close"][idx] - F["close"][np.maximum(idx-1, 0)])
    return idx, d

def ev_trend_flip(F):
    s = F["slope"]; idx = np.where(np.sign(s[1:]) != np.sign(s[:-1]))[0] + 1
    return idx, np.sign(s[idx])

def ev_pullback(F):
    up = (F["close"] > F["ema_l"]) & (F["slope"] > 0)
    touch = _cross_into(up & (F["close"] <= F["ema_s"]))
    dn = (F["close"] < F["ema_l"]) & (F["slope"] < 0)
    touchd = _cross_into(dn & (F["close"] >= F["ema_s"]))
    idx = np.r_[touch, touchd]; dirs = np.r_[np.ones(len(touch)), -np.ones(len(touchd))]
    o = np.argsort(idx); return idx[o], dirs[o]

STRATS = {
    "mr_stretch": (ev_mr_stretch, "tp_mean"),
    "range_fade": (ev_range_fade, "tp_mean"),
    "breakout":   (ev_breakout, "atr_tp_sl"),
    "vol_expand": (ev_vol_expand, "atr_tp_sl"),
    "trend_flip": (ev_trend_flip, "atr_tp_sl"),
    "pullback":   (ev_pullback, "tp_mean"),
}


def _exit_idx(i, d, close, ema, atr, n, rule):
    entry = close[i]; a = atr[i]; best = 0.0; end = min(i + TIMEOUT, n - 1)
    for j in range(i + 1, end + 1):
        fav = d * (close[j] - entry)
        if rule == "tp_mean":
            if d * (ema[j] - close[j]) <= 0: return j
            if fav <= -2 * a: return j           # SL ya usalama
        elif rule == "atr_tp_sl":
            if fav >= 2 * a or fav <= -2 * a: return j
    return end


def backtest(F, entry_fn, rule):
    close, ema, atr, cost, yr = F["close"], F["ema_l"], F["atr"], F["cost"], F["yr"]
    n = len(close); idx, dirs = entry_fn(F)
    out = []  # (year, R)
    last_exit = -1
    for k in range(len(idx)):
        i = int(idx[k]); d = dirs[k]
        if i <= last_exit or i < 1 or i >= n - 1 or d == 0 or not (np.isfinite(atr[i]) and atr[i] > 0):
            continue
        ej = _exit_idx(i, d, close, ema, atr, n, rule)
        ret = d * (close[ej] / close[i] - 1) - cost[i]
        risk = RISK_ATR * atr[i] / close[i]
        if risk > 0:
            out.append((int(yr[i]), ret / risk))
        last_exit = ej
    return out


def metrics(trades):
    if len(trades) < 12:
        return None
    R = np.array([r for _, r in trades])
    w = R[R > 0]; l = R[R < 0]
    pf = w.sum() / abs(l.sum()) if l.sum() != 0 else float("inf")
    eq = np.cumprod(1 + RISK_PCT * R); dd = float((1 - eq / np.maximum.accumulate(eq)).max())
    p1 = np.array([r for y, r in trades if 2016 <= y <= 2020])
    p2 = np.array([r for y, r in trades if 2021 <= y <= 2024])
    robust = len(p1) >= 8 and len(p2) >= 8 and p1.mean() > 0 and p2.mean() > 0 and pf > 1.2
    return dict(n=len(R), tpy=len(R)/YEARS, ev=float(R.mean()), pf=float(pf),
                maxdd=dd, win=float((R > 0).mean()), robust=robust)


def portfolio_ftmo(all_R, rng):
    """Block-bootstrap account-level FTMO pass-rate (survivors pooled)."""
    if len(all_R) < BLOCK + 1:
        return None, None
    npass = 0; ttp = []
    for _ in range(N_SIM):
        seq = []
        while len(seq) < MAX_TRADES:
            s = int(rng.integers(0, len(all_R) - BLOCK)); seq.extend(all_R[s:s+BLOCK])
        eq = 1.0
        for t, r in enumerate(seq[:MAX_TRADES], 1):
            pnl = RISK_PCT * r
            if pnl <= -DAILY: break
            eq *= (1 + pnl)
            if eq <= 1 - TOTAL: break
            if eq >= 1 + TARGET:
                npass += 1; ttp.append(t); break
    return npass / N_SIM, (np.median(ttp) if ttp else None)


# ───────────────────────── DATA PATH ─────────────────────────
def _pip(s):
    return 0.01 if "JPY" in s.upper() else 0.0001

def features(pair):
    import polars as pl
    from data.dataset import load_candles
    c, h, l = pl.col("close"), pl.col("high"), pl.col("low")
    df = load_candles(pair, TF, end=TRAIN_END).with_columns(
        c.ewm_mean(span=200, min_samples=200).alias("ema_l"),
        c.ewm_mean(span=50, min_samples=50).alias("ema_s"),
        (c.log() - c.log().shift(1)).alias("ret"),
        pl.max_horizontal(h - l, (h - c.shift(1)).abs(), (l - c.shift(1)).abs()).alias("tr"),
        h.rolling_max(20).shift(1).alias("dhi"), l.rolling_min(20).shift(1).alias("dlo"),
        c.rolling_min(20).alias("lo20"), c.rolling_max(20).alias("hi20"))
    df = df.with_columns(
        pl.col("bar_open").dt.year().alias("yr"),
        pl.col("tr").ewm_mean(alpha=1/14, min_samples=14).alias("atr"),
        ((c - pl.col("ema_l")) / pl.col("ema_l")).alias("pve"),
        ((pl.col("ema_l") / pl.col("ema_l").shift(20)) - 1).alias("slope"),
        ((c - pl.col("lo20")) / (pl.col("hi20") - pl.col("lo20"))).alias("e2"),
        pl.col("ret").rolling_std(20).alias("vol"),
        (2 * pl.col("spread_mean_pips") * _pip(pair) / c).alias("cost"))
    cols = ["yr", "close", "ema_l", "ema_s", "atr", "pve", "slope", "e2", "vol", "dhi", "dlo", "cost"]
    d = df.select(cols).drop_nulls()
    return {k: d[k].to_numpy() for k in cols}


def run():
    from data.dataset import config
    cfg = config()
    if not (REPO_ROOT / cfg["paths"]["processed"] / "candles").exists():
        print("HITILAFU: candles hazipo.", file=sys.stderr); return 1
    rng = np.random.default_rng(7)
    rows = []; survivor_R = []
    for p in cfg["pairs"]:
        try:
            F = features(p)
        except FileNotFoundError:
            continue
        for name, (fn, rule) in STRATS.items():
            tr = backtest(F, fn, rule)
            m = metrics(tr)
            rows.append((name, p, m))
            if m and m["robust"]:
                survivor_R.extend([r for _, r in tr])
        print(f"  {p} done")

    survivors = [(n, p, m) for n, p, m in rows if m and m["robust"]]
    pf_pass, pf_ttp = portfolio_ftmo(np.array(survivor_R), rng) if survivor_R else (None, None)
    port_tpy = len(survivor_R) / YEARS if survivor_R else 0

    L = ["# Strategy Lab — Methods × Pairs (event-centric) + PORTFOLIO FTMO\n",
         f"*Imezalishwa: {datetime.now():%Y-%m-%d %H:%M} | D1, entry=EVENT + exit, EV-metrics, "
         f"cost imo | sub-period robust (PF>1.2, EV>0 P1&P2) | 2025+ HAIJAGUSWA*\n",
         "## Survivors (robust)\n",
         "| Method | Pair | trades/yr | EV(R) | PF | MaxDD |",
         "|--------|------|-----------|-------|----|----|"]
    if survivors:
        for n, p, m in sorted(survivors, key=lambda x: -x[2]["ev"]):
            L.append(f"| {n} | {p} | {m['tpy']:.1f} | **{m['ev']:+.3f}** | {m['pf']:.2f} | {m['maxdd']*100:.1f}% |")
    else:
        L.append("| HAKUNA | | | | | |")
    L.append(f"\n## PORTFOLIO FTMO (survivors zote pamoja — HAPA FTMO inapimwa)\n")
    if pf_pass is not None:
        yrs = f"{pf_ttp/port_tpy:.1f}" if pf_ttp and port_tpy else "—"
        L.append(f"- **Survivors:** {len(survivors)} strategies | **portfolio trades/yr ≈ {port_tpy:.0f}**")
        L.append(f"- **FTMO pass-rate (block-bootstrap, account-level): {pf_pass*100:.1f}%** "
                 f"(DOCTRINE target ≥60%)")
        L.append(f"- median trades→pass: {pf_ttp} → **≈ {yrs} years**")
    else:
        L.append("- Survivors hazitoshi kwa portfolio MC.")
    L.append("\n---\n*Event-centric (trigger kwenye transition). Edge=entry+exit. EV sio win%. "
             "PORTFOLIO ndio kipimo cha FTMO (sio pair moja): survivors zote zinaongeza "
             "frequency+diversification → pass haraka. Trades/yr ya portfolio = jumla. "
             "Block-bootstrap=clustering. Intraday/carry methods zaongezwa baadaye.*")
    out = REPO_ROOT / cfg["paths"]["reports"] / "strategy_lab.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nSurvivors: {[(n,p) for n,p,_ in survivors]} | portfolio FTMO: {pf_pass}")
    print(f"Ripoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    rng = np.random.default_rng(0)
    n = 3000
    x = np.zeros(n)
    for k in range(1, n): x[k] = 0.9*x[k-1] + rng.normal(0, 0.01)
    close = 1.1*np.exp(x)
    a = 2/51; e = close[0]; ema=[]
    for v in close: e=a*v+(1-a)*e; ema.append(e)
    ema = np.array(ema)
    F = dict(close=close, ema_l=ema, ema_s=ema, atr=np.full(n,0.011),
             pve=(close-ema)/ema, slope=np.gradient(ema), e2=np.full(n,0.5),
             vol=np.full(n,0.01), dhi=close*1.01, dlo=close*0.99,
             cost=np.full(n,5e-5), yr=np.repeat(np.arange(2016,2025), n//9+1)[:n])
    tr = backtest(F, ev_mr_stretch, "tp_mean"); m = metrics(tr)
    print(f"  mr_stretch: n={m['n']} EV={m['ev']:+.3f} PF={m['pf']:.2f} robust={m['robust']}")
    pf, ttp = portfolio_ftmo(np.array([r for _,r in tr]), rng)
    print(f"  portfolio FTMO%={pf*100:.0f} ttp={ttp}")
    print("SELF-TEST:", "PASS" if (m and m['ev']>0) else "FAIL")
    return 0


def main():
    if "--self-test" in sys.argv:
        return self_test()
    sys.path.insert(0, str(REPO_ROOT / "src"))
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
