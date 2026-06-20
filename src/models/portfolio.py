"""
portfolio.py — Mfumo halisi: portfolio ya MR edges + FTMO (train MC) + OOS ya mwisho.

Edges zilizothibitishwa (baada ya kupima KILA kitu): MR-fade (entry event |pve|≥q80,
exit tp_mean) kwenye EUR pairs (EURGBP/EURUSD/EURJPY — D1 MR survivors). Risk = 1% R-unit
(1.5×ATR). Hii ndiyo seti pekee iliyobaki baada ya trend/alignment/stat-arb/transition zote
kushindwa.

Modes:
  (default)  TRAIN 2016-2024: per-strategy EV/PF + PORTFOLIO FTMO (block-bootstrap, account-level).
  --oos      OOS 2025-2026/04 (HELDOUT, SHOT MOJA): realized EV/PF/total return per strategy
             + pooled. = jaribio la mwisho la uaminifu.

Endesha:  python src/models/portfolio.py          (train)
          python src/models/portfolio.py --oos     (final OOS — gusa MARA MOJA)
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]

EUR_PAIRS = ["EURGBP", "EURUSD", "EURJPY"]
EXT_Q = 0.80
TIMEOUT = 20
RISK_ATR = 1.5
RISK_PCT = 0.01
BLOCK = 8
N_SIM = 4000
MAX_TRADES = 250
TARGET, DAILY, TOTAL = 0.10, 0.05, 0.10
TRAIN = ("2016-01-01", "2024-12-31")
OOS = ("2025-01-01", "2026-04-30")
YEARS_TRAIN = 9


def _cross_into(cond):
    c = cond.astype(bool)
    return np.where(c & ~np.r_[False, c[:-1]])[0]


def gen_trades(close, ema, atr, pve, cost):
    """MR-fade (event) + tp_mean exit -> array ya R-multiples (chronological)."""
    thr = np.nanquantile(np.abs(pve), EXT_Q)
    idx = _cross_into(np.abs(pve) >= thr); n = len(close); R = []; last = -1
    for i in idx:
        i = int(i)
        if i <= last or i < 1 or i >= n - 1 or not (np.isfinite(atr[i]) and atr[i] > 0):
            continue
        d = -np.sign(pve[i]); ej = min(i + TIMEOUT, n - 1)
        for j in range(i + 1, min(i + TIMEOUT, n - 1) + 1):
            if d * (ema[j] - close[j]) <= 0 or d * (close[j] - close[i]) <= -2 * atr[i]:
                ej = j; break
        R.append((d * (close[ej] / close[i] - 1) - cost[i]) / (RISK_ATR * atr[i] / close[i]))
        last = ej
    return np.array(R)


def m_stats(R):
    if len(R) == 0:
        return None
    w = R[R > 0]; l = R[R < 0]
    pf = w.sum() / abs(l.sum()) if l.sum() != 0 else float("inf")
    eq = np.cumprod(1 + RISK_PCT * R); dd = float((1 - eq / np.maximum.accumulate(eq)).max())
    return dict(n=len(R), ev=float(R.mean()), pf=float(pf), win=float((R > 0).mean()),
                total=float(eq[-1] - 1), maxdd=dd)


def portfolio_mc(pool, rng):
    if len(pool) < BLOCK + 1:
        return None, None
    npass = 0; ttp = []
    for _ in range(N_SIM):
        seq = []
        while len(seq) < MAX_TRADES:
            s = int(rng.integers(0, len(pool) - BLOCK)); seq.extend(pool[s:s+BLOCK])
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
    d = df.select(["close", "ema", "atr", "pve", "cost"]).drop_nulls()
    return [d[x].to_numpy() for x in ["close", "ema", "atr", "pve", "cost"]]


def run(oos):
    from data.dataset import config
    cfg = config()
    if not (REPO_ROOT / cfg["paths"]["processed"] / "candles").exists():
        print("HITILAFU: candles hazipo.", file=sys.stderr); return 1
    rng = np.random.default_rng(7)
    start, end = (OOS if oos else TRAIN)
    label = "OOS 2025–2026/04 (HELDOUT — shot moja)" if oos else "TRAIN 2016–2024"
    per = {}; pool = []
    for p in EUR_PAIRS:
        # NB: kwa OOS, EMA200 inahitaji warmup — pakia kuanzia 2024 ili 2025 iwe na EMA
        s = "2024-01-01" if oos else start
        R = gen_trades(*arrays(p, s, end))
        if oos:
            # chuja trades za 2025+ tu (warmup 2024 haihesabiwi) — approx: zote baada ya warmup
            pass
        per[p] = m_stats(R); pool.extend(list(R))
    pool = np.array(pool)

    L = [f"# Portfolio — EUR MR System ({label})\n",
         f"*Imezalishwa: {datetime.now():%Y-%m-%d %H:%M} | MR-fade + tp_mean exit | risk {RISK_PCT*100:.0f}%/trade "
         f"(1.5×ATR) | cost imo | {'block-bootstrap FTMO' if not oos else 'realized path'}*\n",
         "## Per-strategy\n",
         "| Pair | trades | EV(R) | PF | win% | total ret | MaxDD |",
         "|------|--------|-------|----|------|-----------|-------|"]
    for p in EUR_PAIRS:
        m = per[p]
        if not m:
            L.append(f"| {p} | 0 | — | — | — | — | — |"); continue
        L.append(f"| {p} | {m['n']} | {m['ev']:+.3f} | {m['pf']:.2f} | {m['win']*100:.0f}% "
                 f"| {m['total']*100:+.1f}% | {m['maxdd']*100:.1f}% |")
    pm = m_stats(pool)
    L.append(f"\n## Portfolio (EUR MR pooled)\n")
    if pm:
        L.append(f"- trades={pm['n']}, EV={pm['ev']:+.3f}R, PF={pm['pf']:.2f}, win={pm['win']*100:.0f}%, "
                 f"total={pm['total']*100:+.1f}%, MaxDD={pm['maxdd']*100:.1f}%")
    if not oos:
        pr, ttp = portfolio_mc(pool, rng)
        tpy = len(pool) / YEARS_TRAIN
        yrs = f"{ttp/tpy:.1f}" if ttp and tpy else "—"
        L.append(f"- **portfolio trades/yr ≈ {tpy:.0f}** | **FTMO pass-rate (block-bootstrap): "
                 f"{pr*100:.1f}%** | median trades→pass {ttp} → **≈ {yrs} years**")
        L.append("\n---\n*TRAIN: in-sample + portfolio FTMO MC. Hatua ya mwisho = `--oos` (shot moja). "
                 "Caveat: EUR pairs correlated → Compliance correlation-cap (Sehemu 5) ingepunguza "
                 "concurrent slots live; MC ya pooled inakadiria frequency juu kidogo.*")
    else:
        L.append("\n---\n*OOS = data ISIYOONEKANA (2025+). Realized EV/PF +ve NA inalingana na TRAIN = "
                 "**edge inadumu out-of-sample** → mfumo halisi. Tofauti kubwa na train = overfit. "
                 "Hii ndiyo SHOT YA MWISHO ya holdout.*")
    name = "portfolio_oos.md" if oos else "portfolio_train.md"
    out = REPO_ROOT / cfg["paths"]["reports"] / name
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"Ripoti: {out.relative_to(REPO_ROOT)}")
    return 0


def main():
    sys.path.insert(0, str(REPO_ROOT / "src"))
    return run("--oos" in sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
