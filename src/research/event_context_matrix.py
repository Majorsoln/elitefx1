"""
event_context_matrix.py — PHASE 4 (Chief Quant approved). Event × Context Matrix.

F-008 imethibitisha: Context = RANKING ENGINE (sio binary filter). Phase 3.5
ilionyesha decile-EV inapanda na context score. Sasa swali la msingi (kabla ya
Triple Barrier):

    Ni Event gani inanufaika ZAIDI na Context?

Kwa kila event (Event Library 9), tunalinganisha:

  Event Only            : EV · Win% · Frequency  (events zote, bila context)
  Event + Top Context   : Top 10% · 20% · 30% · 50% kwa CONTEXT SCORE
                          (score = online prequential EV ya (vol_state, age-bucket),
                           no-lookahead — kutoka Phase 3.5).

Matrix:
  | Event | All EV | Top10 EV | Top20 EV | Top30 EV | Top50 EV | Improvement |
  Improvement = Top10 − All (uplift ya kuchukua decile bora 10% kwa context).

Hii inajenga juu ya F-008 (context = ranking) na inajibu event-specificity:
context inanufaisha events fulani zaidi ya nyingine. Hili ndilo swali la msingi
kabla ya Triple Barrier.

> NO Triple Barrier · NO ML · NO Outcome model (Chief). Matrix tu.

Reuse: context_selectivity (event_scored, top_frac), event_library (events 9),
market_state_engine (bars/states).

Output: reports/event_context_matrix_report.md
Endesha: python src/research/event_context_matrix.py
         python src/research/event_context_matrix.py --symbol EURGBP --tf H1
Self-test: python src/research/event_context_matrix.py --self-test
"""
from __future__ import annotations

import argparse, sys
from datetime import datetime
from pathlib import Path

import numpy as np
import duckdb

from market_state_engine import (cfg, pip, time_col, h1_from_ticks, rollup, state_df)
from event_library import EVENTS_ALL
from context_selectivity import event_scored, top_frac

REPO_ROOT = Path(__file__).resolve().parents[2]
TFS = ["H1", "H2", "H4", "D1"]
FRACS = [(0.10, "Top10"), (0.20, "Top20"), (0.30, "Top30"), (0.50, "Top50")]


def run(pairs, tfs):
    c = cfg(); raw = REPO_ROOT / c["paths"]["raw_ticks"]
    if not raw.exists():
        print(f"HITILAFU: '{raw}' haipo.", file=sys.stderr); return 1
    con = duckdb.connect()
    pool = {ev: dict(s=[], n=[], w=[]) for ev in EVENTS_ALL}
    total_bars = 0
    for sym in pairs:
        base = raw / f"symbol={sym}"
        if not base.exists() or not list(base.rglob("*.parquet")):
            print(f"  {sym}: (hakuna data)"); continue
        src = str(base / "**" / "*.parquet").replace("\\", "/")
        t = time_col(con, src); pp = pip(sym)
        print(f"  {sym}: nascan H1...", flush=True)
        h1 = h1_from_ticks(con, src, t, pp)
        for tf in tfs:
            df = state_df(rollup(h1, tf), tf)
            total_bars += len(df)
            close = df["c"].to_numpy() / pp; high = df["h"].to_numpy() / pp
            low = df["l"].to_numpy() / pp
            spr = df["spr"].to_numpy(); spr = np.where(np.isfinite(spr), spr, 0.0)
            vs = df["volatility_state"].to_list()
            for ev in EVENTS_ALL:
                s, n, w = event_scored(close, high, low, spr, vs, EVENTS_ALL[ev])
                pool[ev]["s"].append(s); pool[ev]["n"].append(n); pool[ev]["w"].append(w)
            print(f"    {tf}: done", flush=True)
    if total_bars == 0:
        print("HITILAFU: hakuna data.", file=sys.stderr); return 1

    rows = []
    for ev in EVENTS_ALL:
        if not pool[ev]["s"]:
            continue
        nets = np.concatenate(pool[ev]["n"]); wins = np.concatenate(pool[ev]["w"])
        scores = np.concatenate(pool[ev]["s"])
        nall = len(nets)
        all_ev = float(np.mean(nets)) if nall else float("nan")
        all_win = float(np.mean(wins)) if nall else float("nan")
        tops = {lab: top_frac(scores, nets, wins, fr) for fr, lab in FRACS}
        rows.append((ev, nall, all_ev, all_win, tops))

    L = ["# Event × Context Matrix — ni event gani inanufaika zaidi na context? (Phase 4)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | Event Only vs Event + Top context deciles (score = online "
         f"prequential EV ya (vol_state, age-bucket), F-008) | EV net ya spread | bars={total_bars:,}*\n",
         "> **Phase 4 (Chief):** F-008 = Context ni RANKING ENGINE. Hapa tunapima uplift ya kuchukua "
         "context-decile bora kwa kila event. Improvement = Top10 EV − All EV. Swali: ni event gani "
         "inanufaika ZAIDI na context? (msingi kabla ya Triple Barrier). NO ML, NO triple barrier.\n",
         "## Matrix — EV (pips) kwa context-rank\n",
         "| Event | n | freq/1k | All EV | Win% | Top10 | Top20 | Top30 | Top50 | Improvement (T10−All) |",
         "|-------|---|---------|--------|------|-------|-------|-------|-------|-----------------------|"]
    bench = []
    for ev, nall, all_ev, all_win, tops in rows:
        freq = 1000 * nall / total_bars
        t10 = tops["Top10"][0]; t20 = tops["Top20"][0]; t30 = tops["Top30"][0]; t50 = tops["Top50"][0]
        imp = t10 - all_ev if (t10 == t10 and all_ev == all_ev) else float("nan")
        bench.append((ev, imp, all_ev, t10))
        L.append(f"| {ev} | {nall:,} | {freq:.0f} | {all_ev:+.2f} | {all_win*100:.0f}% | "
                 f"{t10:+.2f} | {t20:+.2f} | {t30:+.2f} | {t50:+.2f} | {imp:+.2f} |")

    L.append("\n## Win% — All vs Top10 (kwa context)\n")
    L.append("| Event | Win% All | Win% Top10 | ΔWin |")
    L.append("|-------|----------|------------|------|")
    for ev, nall, all_ev, all_win, tops in rows:
        w10 = tops["Top10"][1]
        L.append(f"| {ev} | {all_win*100:.0f}% | {w10*100:.0f}% | {(w10-all_win)*100:+.0f}pp |")

    # ── ranking: ni event gani inanufaika zaidi ──
    L.append("\n## VERDICT — events zilizopangwa kwa CONTEXT BENEFIT (Top10 − All)\n")
    bench_valid = [b for b in bench if b[1] == b[1]]
    bench_valid.sort(key=lambda x: x[1], reverse=True)
    for ev, imp, all_ev, t10 in bench_valid:
        tag = "✅ profitable @Top10" if t10 > 0 else "↑ improved (bado <0)"
        L.append(f"- **{ev}**: improvement {imp:+.2f} pips (All {all_ev:+.2f} → Top10 {t10:+.2f}) — {tag}")
    if bench_valid:
        best = bench_valid[0]
        prof = [b for b in bench_valid if b[3] > 0]
        L.append(f"\n→ Event inayonufaika ZAIDI na context: **{best[0]}** (+{best[1]:.2f} pips uplift). "
                 f"Events {len(prof)}/{len(bench_valid)} zinakuwa profitable (@Top10 EV>0) kwa context-ranking.")
    L.append("\n*Matrix inajibu event-specificity ya context (F-008). All EV = event peke yake (bila "
             "context); Top X% = decile bora kwa context score (no-lookahead, Phase 3.5). Improvement>0 = "
             "context-ranking inanufaisha event hiyo. Hili ni la msingi kabla ya Triple Barrier (Phase 5, "
             "BLOCKED). NO ML/outcome models (Chief). Metric = EV (net pips).*")
    out = REPO_ROOT / c["paths"]["reports"] / "event_context_matrix_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)} ({len(rows)} events, {total_bars:,} bars)")
    return 0


def self_test():
    """Synthetic: score inahusiana na net -> Top10 EV > All EV (uplift>0) kwa events
    zote; null -> uplift ≈ 0. Inatumia top_frac (Phase 3.5)."""
    rng = np.random.default_rng(0); N = 30000
    latent = rng.normal(0, 2, N)
    nets = latent + rng.normal(0, 3, N); wins = (nets > 0).astype(int)
    scores = latent + rng.normal(0, 0.5, N)               # informative
    all_ev = float(np.mean(nets))
    t10 = top_frac(scores, nets, wins, 0.10)[0]
    t50 = top_frac(scores, nets, wins, 0.50)[0]
    uplift_ok = (t10 - all_ev) > 1.0 and t10 > t50       # top10 bora kuliko top50 kuliko all
    print(f"informative: All={all_ev:+.2f} Top50={t50:+.2f} Top10={t10:+.2f} | uplift>0={uplift_ok}")

    scores2 = rng.normal(0, 1, N)                         # null
    t10n = top_frac(scores2, nets, wins, 0.10)[0]
    null_ok = abs(t10n - all_ev) < 0.6
    print(f"null: All={all_ev:+.2f} Top10={t10n:+.2f} (Δ={t10n-all_ev:+.2f}, tarajio ≈0)")

    # events 9 zinapatikana
    ev_ok = len(EVENTS_ALL) == 9
    print(f"events count={len(EVENTS_ALL)} (=9? {ev_ok})")
    ok = uplift_ok and null_ok and ev_ok
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
