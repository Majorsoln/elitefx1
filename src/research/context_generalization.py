"""
context_generalization.py — PHASE 1.95 (Chief Quant). CONTEXT GENERALIZATION TEST.

Phase 1.9 (context_value.py) ilionyesha Context inaongeza EV kwenye event MOJA:
Trend Pullback. Hatari ya quant: labda thamani hiyo ni ya Trend Pullback PEKEE
(over-specific). Chief Quant directive (2026-06-23, Q-001):

    Je Context inaboresha zaidi ya Event Family MOJA?

Tunajaribu events nyingine MBILI kutoka KJ Event Library:
    • Breakout        (KJ #4, Super Simple Breakout)
    • Mean Reversion  (KJ #8-style, N-bar extreme)
(+ Trend Pullback kama baseline ya kulinganisha).

Kwa kila event: Case A (Event alone) vs Case B (Event + Context), ONLINE
prequential (no-lookahead), gate = (state, age-bucket) yenye EV>0 nyuma.
Metrics (Chief): **Win Rate · EV · Trade Count.**

VERDICT:
    Context ikiongeza EV kwenye events ≥2 → **inageneralize** (sio Pullback only)
    -> Principle 12 (Context = filter) imeimarishwa kuvuka event families.

Reuse: context_value.py (events, evaluation, prequential) + market_state_engine
(bars/states). Self-contained, no-lookahead.

Output: reports/context_generalization_report.md
Endesha: python src/research/context_generalization.py
         python src/research/context_generalization.py --symbol EURGBP --tf H1
Self-test: python src/research/context_generalization.py --self-test
"""
from __future__ import annotations

import argparse, sys
from datetime import datetime
from pathlib import Path

import numpy as np
import duckdb

from context_value import (cfg, pip, EVENTS, evaluate_pair_tf, DIMS, TFS)
from market_state_engine import (time_col, h1_from_ticks, rollup, state_df)

REPO_ROOT = Path(__file__).resolve().parents[2]
EVENTS_TEST = ["pullback", "breakout", "mean_reversion"]   # baseline + 2 mpya
_posix = lambda p: str(p).replace("\\", "/")


def _summarize(cells):
    """cells = list ya metrics dicts (kwa pair×TF). Rudisha aggregate ya event×dim."""
    devs = [m["B"]["ev"] - m["A"]["ev"] for m in cells
            if m["B"]["ev"] == m["B"]["ev"] and m["A"]["ev"] == m["A"]["ev"]]
    dws = [m["B"]["win"] - m["A"]["win"] for m in cells
           if m["B"]["win"] == m["B"]["win"] and m["A"]["win"] == m["A"]["win"]]
    nA = sum(m["A"]["n"] for m in cells); nB = sum(m["B"]["n"] for m in cells)
    return dict(
        k=len(cells),
        mdev=float(np.median(devs)) if devs else float("nan"),
        mdw=float(np.median(dws)) if dws else float("nan"),
        nA=nA, nB=nB, cov=(nB / nA) if nA else float("nan"),
        pos=sum(1 for d in devs if d > 0), ndev=len(devs))


def run(pairs, tfs):
    c = cfg(); raw = REPO_ROOT / c["paths"]["raw_ticks"]
    if not raw.exists():
        print(f"HITILAFU: '{raw}' haipo. (Phase 1.95 inahitaji raw ticks.)", file=sys.stderr)
        return 1
    con = duckdb.connect()
    coll = {ev: {d[0]: [] for d in DIMS} for ev in EVENTS_TEST}
    any_data = False
    for sym in pairs:
        base = raw / f"symbol={sym}"
        if not base.exists() or not list(base.rglob("*.parquet")):
            print(f"  {sym}: (hakuna data)"); continue
        src = _posix(base / "**" / "*.parquet")
        t = time_col(con, src); pp = pip(sym)
        print(f"  {sym}: nascan H1...", flush=True)
        h1 = h1_from_ticks(con, src, t, pp)
        for tf in tfs:
            df = state_df(rollup(h1, tf), tf)          # bars + states MARA MOJA
            for ev in EVENTS_TEST:
                res = evaluate_pair_tf(df, pp, EVENTS[ev])
                for dim, _ in DIMS:
                    if res[dim]:
                        coll[ev][dim].append(res[dim]); any_data = True
            print(f"    {tf}: done", flush=True)
    if not any_data:
        print("HITILAFU: hakuna events/data.", file=sys.stderr); return 1

    L = ["# Context Generalization Test — je Context inageneralize? (Phase 1.95)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | events: {', '.join(EVENTS_TEST)} | Case A (Event alone) "
         "vs B (Event + Context) | ONLINE prequential (no-lookahead) | metrics: Win · EV · Trade Count*\n",
         "> **Q-001 (Chief):** Je Context inaboresha zaidi ya Event Family moja? Tunaondoa hatari ya "
         "thamani kuwa ya Trend Pullback PEKEE. Context ikifaidisha events ≥2 → inageneralize → "
         "Principle 12 (Context = filter) imeimarishwa.\n",
         "## Per event × dimension — aggregate kwa pairs×TFs zote\n",
         "| Event | Dim | cells | median ΔEV (pips) | median ΔWin | trades A→B | cov | +EV cells | value? |",
         "|-------|-----|-------|-------------------|-------------|-----------|-----|-----------|--------|"]
    event_pass = {}
    for ev in EVENTS_TEST:
        dim_pos = 0
        for dim, _ in DIMS:
            s = _summarize(coll[ev][dim])
            if s["k"] == 0:
                continue
            good = (s["mdev"] == s["mdev"] and s["mdev"] > 0 and s["pos"] > s["ndev"] / 2)
            dim_pos += 1 if good else 0
            L.append(f"| {ev} | {dim[:3]} | {s['k']} | {s['mdev']:+.2f} | {s['mdw']*100:+.0f}pp | "
                     f"{s['nA']:,}→{s['nB']:,} | {s['cov']*100:.0f}% | {s['pos']}/{s['ndev']} | "
                     f"{'✅' if good else '—'} |")
        event_pass[ev] = dim_pos >= 2          # context inafaidisha event kwenye ≥2 dimensions

    # ── VERDICT ya generalization ──
    L.append("\n## VERDICT — Q-001: je Context inageneralize kuvuka event families?\n")
    for ev in EVENTS_TEST:
        L.append(f"- **{ev}**: {'✅ Context adds value' if event_pass[ev] else '❌ haijafaidisha (≥2 dims)'}")
    n_pass = sum(event_pass.values())
    new_pass = sum(event_pass[e] for e in ("breakout", "mean_reversion"))
    if new_pass >= 1 and n_pass >= 2:
        verdict = ("✅ **Context value GENERALIZES** — inafaidisha zaidi ya Trend Pullback "
                   f"({n_pass}/{len(EVENTS_TEST)} events). Q-001 = NDIYO. Principle 12 imeimarishwa.")
    else:
        verdict = ("❌ **Context value HAIJAGENERALIZE vya kutosha** — inaonekana zaidi kwa Trend "
                   f"Pullback ({n_pass}/{len(EVENTS_TEST)} events). Q-001 = bado. Inahitaji uchunguzi.")
    L.append(f"\n{verdict}")
    L.append("\n*Doctrine (V5.2, Principle 12): Context = FILTER, sio alpha source. Phase 1.95 inathibitisha "
             "kama filter hii inafanya kazi kuvuka event families (sio over-fit kwa event moja). NDIYO → "
             "Phase 2 (Adaptive Volume Bars) inaendelea kwa msingi imara. Metric = EV (net pips). NO ML "
             "(Chief). Events/HORIZON ni vigezo; doctrine inahitaji THUBUTISHO.*")
    out = REPO_ROOT / c["paths"]["reports"] / "context_generalization_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """Integration: jenga bars bandia zenye state cols, endesha events zote 3
    kupitia evaluate_pair_tf + _summarize. Lazima zitoe metrics finite bila error."""
    import polars as pl
    rng = np.random.default_rng(0); n = 4000
    close = np.cumsum(rng.normal(0, 0.5, n)) + 1000.0
    high = close + np.abs(rng.normal(0, 0.3, n)); low = close - np.abs(rng.normal(0, 0.3, n))
    vs = rng.choice(["LOW", "NORMAL", "HIGH"], n); a_s = rng.choice(["LOW", "NORMAL", "HIGH"], n)
    ss = rng.choice(["NORMAL", "WIDE"], n)
    df = pl.DataFrame(dict(
        ts=np.arange(n), o=close, h=high, l=low, c=close,
        atr=np.full(n, 0.10), spr=np.full(n, 0.5),
        volatility_state=vs, activity_state=a_s, spread_state=ss))
    ok = True
    for ev in EVENTS_TEST:
        res = evaluate_pair_tf(df, 0.0001, EVENTS[ev])
        cells = [res[d[0]] for d in DIMS if res[d[0]]]
        s = _summarize(cells)
        finite = all(np.isfinite([res[d[0]]["A"]["ev"], res[d[0]]["B"]["ev"]]).any() for d in DIMS if res[d[0]])
        print(f"{ev}: dims_with_events={len(cells)} ΣtradesA={s['nA']} cov={s['cov']*100:.0f}%")
        ok = ok and len(cells) >= 1 and finite
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
