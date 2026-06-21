"""
ftmo_mc.py — FTMO Monte Carlo SAHIHI (fix #2 na #3 za audit).

Bugs zilizorekebishwa (kutoka portfolio_mc ya zamani):
  #2  DAILY-LOSS & CALENDAR: portfolio_mc ilikagua -5% kwa KILA trade (kana
      kwamba trade moja = siku moja). FTMO daily-loss ni JUMLA ya P&L ndani
      ya SIKU ya kalenda. Hapa P&L inakusanywa kwa siku (D1 bar = siku),
      tunakagua:  -5% kwa siku  |  -10% total (static, dhidi ya initial)  |
      +10% target. Hakuna time-limit (FTMO iliondoa) -> tunaendesha hadi
      PASS au breach, na cap ya MAX_DAYS kuzuia loop.
  #3  CORRELATION: block-bootstrap ya zamani ilichora R za kila pair peke
      yake (IID) -> inapunguza hatari ya hasara ya pamoja siku moja. Hapa
      tunaresample BLOCK za SIKU; siku moja inabeba pairs ZOTE zilizotrade
      siku ileile pamoja -> cross-pair correlation ya siku ileile inahifadhiwa,
      na serial dependence inahifadhiwa na block.

CHANZO KIMOJA: trades zinatoka validate_real (strategy halisi, R-unit = SL =
2ATR, rolling threshold no-lookahead). Hii ndiyo authority — portfolio_mc
imepitwa kwa hesabu ya FTMO.

Train 2016-2024 (in-sample MC).  OOS ni shot moja — haitumiki kupima MC.
Endesha:    python src/models/ftmo_mc.py
Self-test:  python src/models/ftmo_mc.py --self-test
"""
from __future__ import annotations

import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]

RISK_PCT = 0.01            # 1% ya equity kwa trade (1R loss = stop = 1%)
TARGET, DAILY, TOTAL = 0.10, 0.05, 0.10
BLOCK_DAYS = 5            # ~wiki ya biashara (huhifadhi serial dependence)
N_SIM = 5000
MAX_DAYS = 1000          # cap ya trade-days kwa path (hakuna time-limit FTMO)
TRAIN = ("2016-01-01", "2024-12-31")
YEARS_TRAIN = 9


def dated_trades(pair, s, e):
    """Trades za strategy halisi (validate_real) zenye tarehe -> [(np.datetime64, R)]."""
    from models.validate_real import load, real_trades
    bo, close, ema, atr, pve, cost, thr = load(pair, s, e)
    R, idxs = real_trades(close, ema, atr, pve, cost, thr, 0)
    return [(bo[i], float(r)) for i, r in zip(idxs, R)]


def daily_series(pairs, s, e):
    """Kusanya P&L (RISK_PCT*R) kwa SIKU ya kalenda, pairs zote pamoja.
    Rudisha (days_sorted, day_returns, n_trades_total)."""
    day_pnl = defaultdict(float); n = 0
    for p in pairs:
        for dt, r in dated_trades(p, s, e):
            day_pnl[np.datetime64(dt, "D")] += RISK_PCT * r
            n += 1
    days = sorted(day_pnl)
    return days, np.array([day_pnl[d] for d in days]), n


def simulate(rets, rng):
    """Block-bootstrap SIKU -> FTMO sim. Rudisha (pass_rate, median_days, breach)."""
    nd = len(rets)
    if nd < BLOCK_DAYS:
        return None, None, None
    npass = 0; days_to = []
    breach = {"daily": 0, "total": 0, "timeout": 0}
    for _ in range(N_SIM):
        eq = 1.0; length = 0; outcome = None
        while length < MAX_DAYS and outcome is None:
            start = int(rng.integers(0, nd))
            for k in range(BLOCK_DAYS):
                r = float(rets[(start + k) % nd]); length += 1
                if r <= -DAILY:                          # daily-loss breach (siku nzima)
                    outcome = "daily"; break
                eq *= (1.0 + r)
                if eq <= 1.0 - TOTAL:                     # total DD (static dhidi ya initial)
                    outcome = "total"; break
                if eq >= 1.0 + TARGET:                    # target
                    outcome = "pass"; break
                if length >= MAX_DAYS:
                    break
        if outcome == "pass":
            npass += 1; days_to.append(length)
        elif outcome in ("daily", "total"):
            breach[outcome] += 1
        else:
            breach["timeout"] += 1
    med = int(np.median(days_to)) if days_to else None
    return npass / N_SIM, med, breach


def old_per_trade(pairs, s, e, rng):
    """Mbinu YA ZAMANI (BUG): kila trade = siku, IID block ya trades. Kwa kulinganisha tu."""
    pool = []
    for p in pairs:
        pool += [RISK_PCT * r for _, r in dated_trades(p, s, e)]
    R = np.array(pool); n = len(R)
    if n < 9:
        return None
    npass = 0; B = 8; MAXT = 250
    for _ in range(N_SIM):
        eq = 1.0; t = 0; done = False
        while t < MAXT and not done:
            st = int(rng.integers(0, n - B))
            for r in R[st:st + B]:
                t += 1
                if r <= -DAILY:               # BUG: trade moja inakaguliwa kama siku
                    done = True; break
                eq *= (1 + r)
                if eq <= 1 - TOTAL:
                    done = True; break
                if eq >= 1 + TARGET:
                    npass += 1; done = True; break
                if t >= MAXT:
                    break
    return npass / N_SIM


def run():
    sys.path.insert(0, str(REPO_ROOT / "src"))
    from data.dataset import config
    cfg = config()
    if not (REPO_ROOT / cfg["paths"]["processed"] / "candles").exists():
        print("HITILAFU: candles hazipo.", file=sys.stderr); return 1
    from models.validate_real import PAIRS
    rng = np.random.default_rng(7)
    days, rets, ntr = daily_series(PAIRS, *TRAIN)
    pr, med, br = simulate(rets, rng)
    old = old_per_trade(PAIRS, *TRAIN, rng)
    dpy = len(days) / YEARS_TRAIN
    cal_yrs = f"{med / dpy:.1f}" if med and dpy else "—"

    L = ["# FTMO Monte Carlo — calendar-day + cross-pair (SAHIHI)\n",
         f"*Imezalishwa: {datetime.now():%Y-%m-%d %H:%M} | pairs: {', '.join(PAIRS)} | "
         f"risk {RISK_PCT*100:.0f}%/trade | trades={ntr}, trade-days={len(days)} | "
         f"N={N_SIM} | block={BLOCK_DAYS} siku | TRAIN 2016-2024 (in-sample)*\n",
         "> Daily-loss = JUMLA ya P&L kwa siku ya kalenda (-5%). Total = -10% static "
         "dhidi ya initial. Target +10%. Block ya SIKU = cross-pair corr ya siku ileile "
         "inahifadhiwa (fix #3). Hakuna time-limit; cap MAX_DAYS={}.\n".format(MAX_DAYS)]

    if pr is None:
        L.append("**Sample ndogo mno kwa MC (trade-days < block).**")
    else:
        tot = N_SIM
        L.append("## Matokeo (mbinu SAHIHI)\n")
        L.append(f"- **FTMO pass-rate: {pr*100:.1f}%**")
        L.append(f"- median trade-days → pass: {med if med else '—'}  (≈ {cal_yrs} miaka kwa "
                 f"~{dpy:.0f} trade-days/mwaka)")
        L.append(f"- breach breakdown: daily {br['daily']/tot*100:.1f}% | "
                 f"total {br['total']/tot*100:.1f}% | timeout(no pass) {br['timeout']/tot*100:.1f}%")
        if old is not None:
            L.append(f"\n## Kulinganisha: mbinu YA ZAMANI (BUG #2 — per-trade = siku, IID)\n")
            L.append(f"- pass-rate ya zamani: {old*100:.1f}%  → tofauti na sahihi: "
                     f"{(old-pr)*100:+.1f} pp")
            L.append("- *Mbinu ya zamani ilikadiria daily-loss kimakosa (trade moja = siku) "
                     "na ilipuuza cross-pair correlation -> pass-rate isiyoaminika.*")

    L.append(f"\n---\n*FTMO MC sahihi: P&L kwa SIKU ya kalenda (daily-loss halisi), total "
             "static, block ya siku (cross-pair corr). Trades = validate_real (strategy halisi, "
             "R-unit=SL). Hii ni IN-SAMPLE: pass-rate ya juu HAITHIBITISHI edge — angalia "
             "validate_real OOS + Phase B kwanza. Kama edge haipo (EV≤0), MC ni mazoezi ya "
             "nadharia tu.*")
    out = REPO_ROOT / cfg["paths"]["reports"] / "ftmo_mc.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"FTMO pass={pr*100 if pr else 0:.1f}% | Ripoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """Hakikisha: (1) drift+ -> pass>drift- , (2) siku ya -6% inasababisha daily breach."""
    rng = np.random.default_rng(0)
    pos = rng.normal(0.006, 0.008, 400)
    neg = rng.normal(-0.006, 0.008, 400)
    pp, _, _ = simulate(pos, rng)
    pn, _, _ = simulate(neg, rng)
    db = np.concatenate([[-0.06], np.zeros(399)])          # siku moja -6%, nyingine 0
    _, _, brk = simulate(db, rng)
    print(f"pass(drift+)={pp*100:.1f}%  pass(drift-)={pn*100:.1f}%")
    print(f"daily-breach test: daily={brk['daily']/N_SIM*100:.1f}% "
          f"(tarajio >0; siku ya -6% inavunja sheria ya -5%)")
    ok = pp > pn and brk["daily"] > 0
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if "--self-test" in sys.argv:
        return self_test()
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
