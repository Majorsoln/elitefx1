"""
context_selectivity.py — PHASE 3.5 (Chief Quant). Context Selectivity.

Phase 3 diagnostics zilionyesha tatizo: context "favorable" ≈ 99-100% kwa karibu
kila event. Hii SIO "events ni favorable daima" — ni kwamba CONTEXT DEFINITION
ya binary (pchange<0.5) ni PERMISSIVE mno (vol states zina P(change) ndogo,
~6-12%, kwa hiyo karibu zote zinapita). Filter inayokubali 99% = filter strength 0.

Chief suspicion: **Context = Ranking Engine**, sio **Pass/Fail Filter**.

Hii inajaribu hilo. Badala ya favorable-vs-not, tunatoa CONTEXT SCORE inayoendelea
kwa kila event instance (online prequential EV ya context bucket — no-lookahead),
kisha tunaipanga kwa DECILES + Top 10/20/30/50%, na kupima EV · Win Rate · Trade
Count kwa kila bucket.

  Decile-EV inapanda monotonically  -> Context = RANKING ENGINE (discrimination ipo)
  Decile-EV flat                    -> Context haina selectivity (binary/none)

Context score = online mean net EV ya (volatility_state, vol age-bucket) kutoka
event instances za NYUMA tu. Outcome = forward HORIZON bars, net ya spread.

> NO ML, NO triple barrier (Chief). Hii inafafanua MAANA ya context kabla ya
> Phase 4 (Event × Context Matrix).

Reuse: event_library (signals), market_state_engine (bars/states),
state_context_engine (age), context_value (HORIZON/MIN_OBS/pip).

Output: reports/context_selectivity_report.md
Endesha: python src/research/context_selectivity.py
         python src/research/context_selectivity.py --symbol EURGBP --tf H1
Self-test: python src/research/context_selectivity.py --self-test
"""
from __future__ import annotations

import argparse, sys
from datetime import datetime
from pathlib import Path

import numpy as np
import duckdb

from market_state_engine import (cfg, pip, time_col, h1_from_ticks, rollup, state_df)
from state_context_engine import context_for_dim, _bidx
from event_library import EVENTS_ALL
from context_value import HORIZON, MIN_OBS

REPO_ROOT = Path(__file__).resolve().parents[2]
TFS = ["H1", "H2", "H4", "D1"]
EVENTS_SEL = ["pullback", "breakout", "mean_reversion"]   # families zilizothibitishwa (F-006)
MIN_SCORED = 200          # instances za chini (zenye score) kwa decile analysis
_posix = lambda p: str(p).replace("\\", "/")


def event_scored(close, high, low, spr, vol_states, sigfn):
    """ONLINE prequential: rudisha (scores[], nets[], wins[]) kwa event instances.
    score[i] = mean net EV ya (vol_state, age-bucket) kutoka instances za NYUMA
    (>= MIN_OBS), NaN vinginevyo. Outcome = forward HORIZON, net ya spread."""
    age, _ = context_for_dim(vol_states)
    sig = sigfn(close, high, low)
    ev_hist = {}; scores = []; nets = []; wins = []
    n = len(close)
    for i in range(n):
        if sig[i] == 0 or i + HORIZON >= n:
            continue
        vs = vol_states[i]
        if vs == "UNKNOWN" or age[i] <= 0:
            continue
        key = (vs, _bidx(int(age[i])))
        eh = ev_hist.get(key)
        score = (eh[0] / eh[1]) if (eh and eh[1] >= MIN_OBS) else np.nan
        net = sig[i] * (close[i + HORIZON] - close[i]) - spr[i]
        scores.append(score); nets.append(float(net)); wins.append(1 if net > 0 else 0)
        ev_hist.setdefault(key, [0.0, 0]); ev_hist[key][0] += net; ev_hist[key][1] += 1
    return np.array(scores), np.array(nets), np.array(wins)


def decile_stats(scores, nets, wins):
    """Rudisha list ya (ev, win, n) kwa deciles 10 (chini->juu kwa score)."""
    idx = np.where(np.isfinite(scores))[0]
    if len(idx) < MIN_SCORED:
        return None
    order = idx[np.argsort(scores[idx], kind="mergesort")]
    m = len(order); out = []
    for d in range(10):
        seg = order[d * m // 10:(d + 1) * m // 10]
        out.append((float(np.mean(nets[seg])), float(np.mean(wins[seg])), len(seg)))
    return out


def top_frac(scores, nets, wins, frac):
    idx = np.where(np.isfinite(scores))[0]
    if len(idx) == 0:
        return (float("nan"), float("nan"), 0)
    order = idx[np.argsort(scores[idx], kind="mergesort")][::-1]      # juu -> chini
    k = max(1, int(len(order) * frac)); seg = order[:k]
    return float(np.mean(nets[seg])), float(np.mean(wins[seg])), k


def run(pairs, tfs):
    c = cfg(); raw = REPO_ROOT / c["paths"]["raw_ticks"]
    if not raw.exists():
        print(f"HITILAFU: '{raw}' haipo.", file=sys.stderr); return 1
    con = duckdb.connect()
    pool = {ev: dict(s=[], n=[], w=[]) for ev in EVENTS_SEL}
    for sym in pairs:
        base = raw / f"symbol={sym}"
        if not base.exists() or not list(base.rglob("*.parquet")):
            print(f"  {sym}: (hakuna data)"); continue
        src = _posix(base / "**" / "*.parquet")
        t = time_col(con, src); pp = pip(sym)
        print(f"  {sym}: nascan H1...", flush=True)
        h1 = h1_from_ticks(con, src, t, pp)
        for tf in tfs:
            df = state_df(rollup(h1, tf), tf)
            close = df["c"].to_numpy() / pp; high = df["h"].to_numpy() / pp
            low = df["l"].to_numpy() / pp
            spr = df["spr"].to_numpy(); spr = np.where(np.isfinite(spr), spr, 0.0)
            vs = df["volatility_state"].to_list()
            for ev in EVENTS_SEL:
                s, n, w = event_scored(close, high, low, spr, vs, EVENTS_ALL[ev])
                pool[ev]["s"].append(s); pool[ev]["n"].append(n); pool[ev]["w"].append(w)
            print(f"    {tf}: done", flush=True)

    L = ["# Context Selectivity — je context ni ranking engine au binary filter? (Phase 3.5)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | context score = online prequential EV ya (vol_state, age-bucket) "
         f"| deciles + Top X% | outcome forward {HORIZON} bars net ya spread | aggregate pairs×TFs*\n",
         "> **Q-005 (Chief):** Phase 3 ilionyesha 'favorable ≈ 99%' = context binary ni PERMISSIVE mno. "
         "Hapa tunapanga events kwa CONTEXT SCORE (deciles). EV ikipanda na decile -> Context = RANKING "
         "ENGINE (discrimination ipo). EV flat -> hakuna selectivity. NO ML, NO triple barrier.\n"]
    any_ranking = 0; n_ev = 0
    for ev in EVENTS_SEL:
        if not pool[ev]["s"]:
            continue
        scores = np.concatenate(pool[ev]["s"]); nets = np.concatenate(pool[ev]["n"])
        wins = np.concatenate(pool[ev]["w"])
        dec = decile_stats(scores, nets, wins)
        if dec is None:
            L.append(f"\n## {ev}\n*(scored instances < {MIN_SCORED} — haitoshi)*"); continue
        n_ev += 1
        L.append(f"\n## {ev} — EV/Win/Count kwa decile ya context score (D1=chini → D10=juu)\n")
        L.append("| decile | EV (pips) | Win% | n |")
        L.append("|--------|-----------|------|---|")
        for d, (evv, wr, nn) in enumerate(dec, 1):
            L.append(f"| D{d} | {evv:+.2f} | {wr*100:.0f}% | {nn:,} |")
        # Top X%
        L.append(f"\n*Top X% kwa context score ({ev}):*\n")
        L.append("| bucket | EV (pips) | Win% | n |")
        L.append("|--------|-----------|------|---|")
        for frac, lab in [(0.10, "Top 10%"), (0.20, "Top 20%"), (0.30, "Top 30%"),
                          (0.50, "Top 50%"), (1.0, "All")]:
            e, w, k = top_frac(scores, nets, wins, frac)
            L.append(f"| {lab} | {e:+.2f} | {w*100:.0f}% | {k:,} |")
        # verdict ya event
        top, bot = dec[9][0], dec[0][0]
        mono = sum(1 for d in range(9) if dec[d + 1][0] > dec[d][0])
        ranking = (top - bot) > 0 and mono >= 6
        any_ranking += 1 if ranking else 0
        L.append(f"\n→ **{ev}**: D10−D1 EV = {top - bot:+.2f} pips, monotonic steps {mono}/9 → "
                 f"{'✅ RANKING (discrimination)' if ranking else '— flat (hakuna selectivity wazi)'}")

    L.append("\n## VERDICT — Q-005: Context = Ranking Engine au Binary Filter?\n")
    if n_ev and any_ranking >= max(1, n_ev // 2 + n_ev % 2):
        L.append(f"✅ **Context = RANKING ENGINE** ({any_ranking}/{n_ev} events: EV inapanda na context "
                 "score). Sio pass/fail — ni mfumo wa kupanga (decile). Phase 4 (Event × Context Matrix) "
                 "itumie context kama SCORE/rank, sio threshold ya binary.")
    else:
        L.append(f"❌ **Hakuna ranking wazi** ({any_ranking}/{n_ev} events). Context score haitofautishi EV "
                 "kwa deciles -> selectivity dhaifu. Context definition inahitaji marekebisho kabla ya Phase 4.")
    L.append("\n*Score = online prequential EV ya (vol_state, age-bucket), no-lookahead (past instances tu; "
             "H-horizon overlap kama Phase 1.9). Deciles zinajibu 'discrimination ipo?'. Hii inafafanua "
             "MAANA ya context (ranking vs filter) kabla ya Phase 4. NO ML/triple barrier (Chief). "
             "Metric = EV (net pips). 'favorable' ya binary (Phase 3) imeachwa — ilikuwa permissive mno.*")
    out = REPO_ROOT / c["paths"]["reports"] / "context_selectivity_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """(1) informative: score inahusiana na net -> decile EV inapanda (ranking).
       (2) null: score random -> decile EV flat."""
    rng = np.random.default_rng(0); N = 20000
    # (1) net = score_signal + noise -> high-score deciles = high EV
    latent = rng.normal(0, 2, N)
    nets = latent + rng.normal(0, 3, N); wins = (nets > 0).astype(int)
    scores = latent + rng.normal(0, 0.5, N)               # score = noisy view ya latent
    dec = decile_stats(scores, nets, wins)
    mono = sum(1 for d in range(9) if dec[d + 1][0] > dec[d][0])
    rank_ok = (dec[9][0] - dec[0][0]) > 1.0 and mono >= 7
    t10 = top_frac(scores, nets, wins, 0.10)[0]; tall = top_frac(scores, nets, wins, 1.0)[0]
    print(f"informative: D1={dec[0][0]:+.2f} D10={dec[9][0]:+.2f} mono={mono}/9 | Top10%={t10:+.2f} All={tall:+.2f}")

    # (2) null: score haina uhusiano na net
    scores2 = rng.normal(0, 1, N)
    dec2 = decile_stats(scores2, nets, wins)
    spread2 = max(d[0] for d in dec2) - min(d[0] for d in dec2)
    null_ok = spread2 < 1.0
    print(f"null: decile EV spread={spread2:.2f} (tarajio ndogo)")

    ok = rank_ok and null_ok
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default=None)
    ap.add_argument("--tf", default=None, choices=TFS)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    c = cfg()
    pairs = [a.symbol] if a.symbol else c["pairs"]
    tfs = [a.tf] if a.tf else TFS
    return run(pairs, tfs)


if __name__ == "__main__":
    raise SystemExit(main())
