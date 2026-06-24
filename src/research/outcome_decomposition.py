"""
outcome_decomposition.py — PHASE 5.5 (Chief Quant). Outcome Decomposition.

Phase 4 (F-009): context inaongeza EV kwa Tier 1 events (uplift kubwa Top10).
Phase 5 (triple barrier): P(TP) ni FLAT kuvuka context deciles (mean_reversion
48%→48%). Contradiction:

    Phase 4: Context improves EV massively.
    Phase 5: Context barely changes P(TP).

Chief hypothesis (Scenario A): context inaboresha REWARD SIZE, sio WIN
PROBABILITY. Hii inajaribu hilo kwa kufungua EV:

    EV = P(win) × AvgWin − P(loss) × AvgLoss

Kwa kila Tier 1 event, kwa kila CONTEXT DECILE, tunaonyesha:
  Winners : avg · median · 95%       (nets > 0)
  Losers  : avg · median · 95%       (nets ≤ 0, kwa ukubwa)
  P(win), EV (decomposed)

Swali kuu: Context inaongeza P(win), au AvgWin, au asymmetry? (au zote?)

Outcome = forward HORIZON bars, net ya spread (ILEILE iliyozaa F-009 uplift,
Phase 1.9/3.5). Context score = online prequential EV (Phase 3.5). NO ML.

> Hakuna F-010 bado (Chief). Hii inafichua MECHANISM ya context kabla ya Outcome
> Engine / ML. Profitable ≠ Tradable Edge.

Reuse: context_selectivity.event_scored (scores, nets, wins), market_state_engine,
event_library.

Output: reports/outcome_decomposition_report.md
Endesha: python src/research/outcome_decomposition.py
         python src/research/outcome_decomposition.py --symbol EURGBP --tf H1
Self-test: python src/research/outcome_decomposition.py --self-test
"""
from __future__ import annotations

import argparse, sys
from datetime import datetime
from pathlib import Path

import numpy as np
import duckdb

from market_state_engine import (cfg, pip, time_col, h1_from_ticks, rollup, state_df)
from event_library import EVENTS_ALL
from context_selectivity import event_scored

REPO_ROOT = Path(__file__).resolve().parents[2]
TFS = ["H1", "H2", "H4", "D1"]
TIER1 = ["mean_reversion", "pullback", "deep_pullback", "trend_continuation"]
MIN_DEC = 200          # instances za chini (zenye score) kwa decile decomposition
_posix = lambda p: str(p).replace("\\", "/")


def decompose(scores, nets, wins):
    """Rudisha list ya dict kwa deciles 10 (chini->juu kwa score): P(win), winner/
    loser stats, EV decomposed. EV = pw*AvgWin - (1-pw)*AvgLoss."""
    idx = np.where(np.isfinite(scores))[0]
    if len(idx) < MIN_DEC:
        return None
    order = idx[np.argsort(scores[idx], kind="mergesort")]
    m = len(order); out = []
    for d in range(10):
        seg = order[d * m // 10:(d + 1) * m // 10]
        ns = nets[seg]
        w = ns[ns > 0]; l = -ns[ns <= 0]                  # losses kama chanya
        pw = float(len(w) / len(ns)) if len(ns) else float("nan")
        aw = float(np.mean(w)) if len(w) else 0.0
        al = float(np.mean(l)) if len(l) else 0.0
        out.append(dict(
            pw=pw, ev=pw * aw - (1 - pw) * al, mean=float(np.mean(ns)),
            avgwin=aw, medwin=float(np.median(w)) if len(w) else 0.0,
            p95win=float(np.percentile(w, 95)) if len(w) else 0.0,
            avgloss=al, medloss=float(np.median(l)) if len(l) else 0.0,
            p95loss=float(np.percentile(l, 95)) if len(l) else 0.0, n=len(ns)))
    return out


def run(pairs, tfs):
    c = cfg(); raw = REPO_ROOT / c["paths"]["raw_ticks"]
    if not raw.exists():
        print(f"HITILAFU: '{raw}' haipo.", file=sys.stderr); return 1
    con = duckdb.connect()
    pool = {ev: dict(s=[], n=[], w=[]) for ev in TIER1}
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
            for ev in TIER1:
                s, n, w = event_scored(close, high, low, spr, vs, EVENTS_ALL[ev])
                pool[ev]["s"].append(s); pool[ev]["n"].append(n); pool[ev]["w"].append(w)
            print(f"    {tf}: done", flush=True)

    L = ["# Outcome Decomposition — chanzo cha uplift ya EV (Phase 5.5, Tier 1)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | EV = P(win)×AvgWin − P(loss)×AvgLoss kwa context decile | "
         "outcome = forward HORIZON net ya spread (ileile ya F-009) | context score = Phase 3.5*\n",
         "> **Q-008 (Chief):** Phase 5 ilionyesha P(TP) flat kuvuka deciles, lakini Phase 4 EV uplift "
         "kubwa. Je context inaongeza **P(win)**, **AvgWin**, au **asymmetry**? Hii inafungua EV. "
         "Hypothesis (Scenario A): context = reward SIZE, sio win probability. NO ML (Chief).\n"]
    summary = []
    for ev in TIER1:
        if not pool[ev]["s"]:
            continue
        scores = np.concatenate(pool[ev]["s"]); nets = np.concatenate(pool[ev]["n"])
        wins = np.concatenate(pool[ev]["w"])
        dec = decompose(scores, nets, wins)
        L.append(f"\n## {ev}\n")
        if dec is None:
            L.append(f"*(scored instances < {MIN_DEC} — haitoshi)*"); continue
        L.append("| decile | P(win) | EV | AvgWin | MedWin | p95Win | AvgLoss | MedLoss | p95Loss | n |")
        L.append("|--------|--------|----|--------|--------|--------|---------|---------|---------|---|")
        for q, r in enumerate(dec, 1):
            L.append(f"| D{q} | {r['pw']*100:.0f}% | {r['ev']:+.2f} | {r['avgwin']:.1f} | {r['medwin']:.1f} | "
                     f"{r['p95win']:.0f} | {r['avgloss']:.1f} | {r['medloss']:.1f} | {r['p95loss']:.0f} | {r['n']:,} |")
        d1, d10 = dec[0], dec[9]
        dpw = (d10["pw"] - d1["pw"]) * 100; daw = d10["avgwin"] - d1["avgwin"]
        dal = d10["avgloss"] - d1["avgloss"]; dev = d10["ev"] - d1["ev"]
        # mechanism: nini kinachoendesha Δ EV?
        driver = "AvgWin (reward size)" if abs(daw) >= abs(dal) and abs(daw) * 0.5 >= abs(dpw * 0.1) else \
                 ("AvgLoss (loss control)" if abs(dal) > abs(daw) else "P(win)")
        if abs(dpw) >= 3 and abs(dpw * 0.1) > max(abs(daw), abs(dal)) * 0.3:
            driver = "P(win)"
        L.append(f"\n→ **{ev}** D10−D1: ΔP(win)={dpw:+.0f}pp · ΔAvgWin={daw:+.1f} · ΔAvgLoss={dal:+.1f} · "
                 f"ΔEV={dev:+.2f} → driver: **{driver}**")
        summary.append((ev, dpw, daw, dal, dev, driver))

    L.append("\n## VERDICT — Context inafanya kazi kupitia mechanism gani?\n")
    for ev, dpw, daw, dal, dev, driver in summary:
        L.append(f"- **{ev}**: ΔEV {dev:+.2f} ← {driver} (ΔP(win) {dpw:+.0f}pp, ΔAvgWin {daw:+.1f}, ΔAvgLoss {dal:+.1f})")
    if summary:
        pw_driven = sum(1 for s in summary if s[5] == "P(win)")
        size_driven = sum(1 for s in summary if "AvgWin" in s[5] or "AvgLoss" in s[5])
        if size_driven > pw_driven:
            L.append(f"\n→ **Scenario A imeungwa mkono**: kwa {size_driven}/{len(summary)} Tier-1 events, uplift "
                     "ya EV inatokana na PAYOFF SIZE/asymmetry, SIO win probability. Context = reward engine, "
                     "sio hit-rate engine. (Inalingana na Phase 1.9: win-rate flat, EV juu.)")
        else:
            L.append(f"\n→ Uplift inatokana zaidi na P(win) ({pw_driven}/{len(summary)}). Scenario A haijaungwa mkono.")
    L.append("\n*EV decomposed = P(win)×AvgWin − P(loss)×AvgLoss kwa decile (outcome = forward net, ileile "
             "ya F-009). Hii inafichua MECHANISM: P(win) vs AvgWin vs AvgLoss. Hakuna F-010 bado (Chief). "
             "Mpaka mechanism ijulikane, hatuendi Outcome Engine wala ML. Profitable ≠ Tradable Edge.*")
    out = REPO_ROOT / c["paths"]["reports"] / "outcome_decomposition_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """(1) Scenario A: P(win) flat, AvgWin inakua na score -> driver=AvgWin, ΔP(win)≈0.
       (2) P(win)-driven: win-prob inakua na score -> ΔP(win) kubwa."""
    rng = np.random.default_rng(0); N = 40000
    # (1) win prob constant 0.5; winner size inakua na latent; loss fixed
    latent = rng.normal(0, 1, N)
    win = (rng.random(N) < 0.5).astype(int)
    nets = np.where(win == 1, 5.0 + 3.0 * (latent - latent.min()), -5.0)
    scores = latent + rng.normal(0, 0.3, N)
    dec = decompose(scores, nets, win)
    dpw = (dec[9]["pw"] - dec[0]["pw"]) * 100; daw = dec[9]["avgwin"] - dec[0]["avgwin"]
    a_ok = abs(dpw) < 5 and daw > 3
    print(f"Scenario A: ΔP(win)={dpw:+.0f}pp (≈0?) ΔAvgWin={daw:+.1f} (>0?) -> {a_ok}")

    # (2) win prob inakua na score; sizes fixed
    p = 1 / (1 + np.exp(-latent)); win2 = (rng.random(N) < p).astype(int)
    nets2 = np.where(win2 == 1, 8.0, -8.0)
    dec2 = decompose(scores, nets2, win2)
    dpw2 = (dec2[9]["pw"] - dec2[0]["pw"]) * 100
    b_ok = dpw2 > 20
    print(f"P(win)-driven: ΔP(win)={dpw2:+.0f}pp (>20?) -> {b_ok}")

    ok = a_ok and b_ok and dec is not None
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
