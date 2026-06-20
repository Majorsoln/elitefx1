"""
montecarlo_ftmo.py — VIABILITY: je EURGBP MR + sizing inapita FTMO? (DOCTRINE §5 / MFUMO §7)

Swali halisi: edge moja ya wastani (EURGBP mean-reversion) + risk per trade — je inafikia
+10% KABLA ya −5% (siku) au −10% (jumla)? Monte Carlo ya challenges 5000.

Hatua:
  1. Hesabu EURGBP MR trades (train 2016-2024) -> R-multiples (PnL / risk per trade).
  2. Bootstrap trades, risk r% kila trade, fuata FTMO rules, hesabu pass-rate.
  3. Jaribu risk levels mbalimbali + onyesha pass% NA muda (trades/years) wa kupita.

FTMO: target +10%, daily loss −5% (kutoka day-start), total floor −10% (kutoka initial).
Trade moja ≈ siku moja (EURGBP D1 ina trades chache). Bootstrap = IID (sahili; haijumuishi
autocorrelation/regime). 2025+ HAIGUSWI. DOCTRINE target: pass-rate ≥ 60%.

Endesha (PC ya Japhet):  python src/models/montecarlo_ftmo.py
Self-test (popote):       python src/models/montecarlo_ftmo.py --self-test
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]

PAIR = "EURGBP"
SL_ATR = 1.5
TIMEOUT = 15
EXT_Q = 0.80
TRAIN_END = "2024-12-31"
YEARS = 9                       # 2016-2024
RISKS = [0.005, 0.01, 0.015, 0.02, 0.03]    # risk per trade (% ya account)
N_SIM = 5000
MAX_TRADES = 150
TARGET, DAILY, TOTAL = 0.10, 0.05, 0.10


def trades_R(close, ema, atr, pve, cost):
    """EURGBP MR trades -> R-multiples (trade_return / risk per trade)."""
    thr = np.quantile(np.abs(pve[np.isfinite(pve)]), EXT_Q)
    n = len(close); R = []; i = 1
    while i < n - 1:
        if not (np.isfinite(pve[i]) and abs(pve[i]) >= thr and np.isfinite(atr[i]) and atr[i] > 0):
            i += 1; continue
        direction = -np.sign(pve[i]); entry = close[i]
        risk_ret = SL_ATR * atr[i] / entry
        sl_dist = SL_ATR * atr[i]
        exit_j = min(i + TIMEOUT, n - 1)
        for j in range(i + 1, min(i + TIMEOUT, n - 1) + 1):
            if direction * (close[j] - entry) <= -sl_dist:
                exit_j = j; break
            if direction * (ema[j] - close[j]) <= 0:
                exit_j = j; break
            exit_j = j
        ret = direction * (close[exit_j] / entry - 1) - cost[i]
        if risk_ret > 0:
            R.append(ret / risk_ret)
        i = exit_j + 1
    return np.array(R)


def simulate(Rs, risk, rng):
    """Rudisha ('pass'|'fail_daily'|'fail_total'|'timeout', n_trades)."""
    eq = 1.0
    for k in range(1, MAX_TRADES + 1):
        pnl = risk * Rs[rng.integers(len(Rs))]
        if pnl <= -DAILY:
            return "fail_daily", k
        eq *= (1 + pnl)
        if eq <= 1 - TOTAL:
            return "fail_total", k
        if eq >= 1 + TARGET:
            return "pass", k
    return "timeout", MAX_TRADES


def mc(Rs, risk, rng):
    res = {"pass": 0, "fail_daily": 0, "fail_total": 0, "timeout": 0}
    ttp = []
    for _ in range(N_SIM):
        out, k = simulate(Rs, risk, rng)
        res[out] += 1
        if out == "pass":
            ttp.append(k)
    return res, (np.median(ttp) if ttp else None)


# ───────────────────────── DATA PATH ─────────────────────────

def _pip(s):
    return 0.01 if "JPY" in s.upper() else 0.0001


def get_R():
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
    return trades_R(*(d[x].to_numpy() for x in ["close", "ema", "atr", "pve", "cost"]))


def run():
    from data.dataset import config
    cfg = config()
    if not (REPO_ROOT / cfg["paths"]["processed"] / "candles").exists():
        print("HITILAFU: candles hazipo.", file=sys.stderr); return 1
    Rs = get_R()
    rng = np.random.default_rng(7)
    tpy = len(Rs) / YEARS
    L = ["# Viability — EURGBP MR Monte Carlo FTMO Pass-Rate\n",
         f"*Imezalishwa: {datetime.now():%Y-%m-%d %H:%M} | trades={len(Rs)} ({tpy:.0f}/mwaka) | "
         f"R-mult mean={Rs.mean():+.3f}, win={ (Rs>0).mean():.2f} | sims={N_SIM} | "
         "FTMO: +10%/−5%day/−10%total | bootstrap IID*\n",
         "> DOCTRINE target: **pass-rate ≥ 60%.** Pia angalia muda (trades→years) wa kupita.\n",
         "| Risk/trade | PASS% | fail daily | fail total | timeout | median trades→pass | ≈ years |",
         "|-----------|-------|-----------|-----------|---------|--------------------|---------|"]
    for r in RISKS:
        res, med = mc(Rs, r, rng)
        yrs = f"{med/tpy:.1f}" if med else "—"
        L.append(f"| {r*100:.1f}% | **{res['pass']/N_SIM*100:.1f}%** | {res['fail_daily']/N_SIM*100:.1f}% "
                 f"| {res['fail_total']/N_SIM*100:.1f}% | {res['timeout']/N_SIM*100:.1f}% "
                 f"| {med if med else '—'} | {yrs} |")
    L.append(f"\n---\n*EURGBP MR ina **trades ~{tpy:.0f}/mwaka** (chache — pair moja, D1). "
             "PASS% ≥60% kwa risk fulani = mfumo viable kwa edge moja. Lakini angalia **years** — "
             "kama kupita kunahitaji miaka mingi, ni polepole mno kivitendo → tunahitaji pairs/edges "
             "zaidi. Bootstrap ni IID (haijumuishi clustering). Risk kubwa = pass haraka lakini "
             "fail-total juu. 2025+ HAIJAGUSWA.*")
    out = REPO_ROOT / cfg["paths"]["reports"] / "montecarlo_ftmo.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"Ripoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """R-dist yenye edge chanya -> pass-rate juu kwa risk wastani."""
    rng = np.random.default_rng(0)
    # win 60%, +1R win, -1R loss -> edge chanya
    Rs = np.where(rng.random(2000) < 0.60, 1.0, -1.0)
    res, med = mc(Rs, 0.02, rng)
    print(f"edge +ve: PASS%={res['pass']/N_SIM*100:.1f} fail_total%={res['fail_total']/N_SIM*100:.1f} median→{med}")
    # no edge (50/50) -> pass-rate chini sana
    Rn = np.where(rng.random(2000) < 0.50, 1.0, -1.0)
    res2, _ = mc(Rn, 0.02, rng)
    print(f"no edge:  PASS%={res2['pass']/N_SIM*100:.1f}")
    ok = res["pass"]/N_SIM > 0.5 and res2["pass"]/N_SIM < res["pass"]/N_SIM
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if "--self-test" in sys.argv:
        return self_test()
    sys.path.insert(0, str(REPO_ROOT / "src"))
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
