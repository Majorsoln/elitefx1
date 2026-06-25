"""
interaction_stability.py — PHASE 5.8 (Chief Quant). Interaction Stability.

Phase 5.7 (F-012) ilithibitisha: edge iko kwenye INTERACTION (16/16 joint >
marginal). Lakini Chief correction: 3-way ilitumia top/bottom cells BILA kupima
STABILITY. Swali:

    Je cell bora (mfano HIGH×HIGH×Tmid) kwenye EURUSD ndiyo bora kwenye GBPUSD?
    Au ni LOCAL pattern (coincidence)?

Interaction Engine HAIWEZI kujengwa hadi interaction iwe GENERALIZABLE
(cross-market). Phase 5.8 inapima, kwa kila interaction, CONSISTENCY kuvuka
PAIRS:

  • per-pair cell EV
  • coefficient of variation (CV) ya cell EV kuvuka pairs   (ndogo = stable)
  • rank consistency = wastani Spearman ya cell-EV vectors kati ya pairs
  • modal best cell (cell bora inajirudia kwa pairs ngapi?)

Verdict:
  interaction STABLE (rank consistency juu)  -> UNIVERSAL RULE
  interaction UNSTABLE                        -> ADAPTIVE / LOCAL RULE

Outcome = forward HORIZON net ya spread. NO ML, NO Interaction Engine bado —
stability kwanza (Chief).

Reuse: market_state_engine, state_context_engine, event_library, context_value.

Output: reports/interaction_stability_report.md
Endesha: python src/research/interaction_stability.py
Self-test: python src/research/interaction_stability.py --self-test
"""
from __future__ import annotations

import argparse, sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np
import duckdb

from market_state_engine import (cfg, pip, time_col, h1_from_ticks, rollup, state_df)
from state_context_engine import context_for_dim, _bidx
from event_library import EVENTS_ALL
from context_value import HORIZON

REPO_ROOT = Path(__file__).resolve().parents[2]
TFS = ["H1", "H2", "H4", "D1"]
TIER1 = ["mean_reversion", "pullback", "deep_pullback", "trend_continuation"]
VOL = ["LOW", "NORMAL", "HIGH"]; ACT = ["LOW", "NORMAL", "HIGH"]
TRANS = ["Tlo", "Tmid", "Thi"]; AGE = ["1-3", "4-8", "9-15", "16+"]
INTERACTIONS = ["volatility×activity", "volatility×transition",
                "activity×state_age", "transition×state_age", "vol×act×transition"]
MIN_CELL_PAIR = 50      # instances za chini kwa cell ndani ya pair
MIN_PAIRS = 4           # cell lazima iwepo kwa pairs >= hii ili kuhesabu (common)
_posix = lambda p: str(p).replace("\\", "/")


def _pchg_bucket(p):
    if not np.isfinite(p):
        return None
    return "Tlo" if p < 0.08 else ("Tmid" if p < 0.15 else "Thi")


def _keys(v, a, tr, ag):
    """Rudisha {interaction: cell-key} (None ikikosa component)."""
    out = {}
    if a: out["volatility×activity"] = (v, a)
    if tr: out["volatility×transition"] = (v, tr)
    if a and ag: out["activity×state_age"] = (a, ag)
    if tr and ag: out["transition×state_age"] = (tr, ag)
    if a and tr: out["vol×act×transition"] = (v, a, tr)
    return out


def process_df(df, pp, sym, acc):
    close = df["c"].to_numpy() / pp; high = df["h"].to_numpy() / pp; low = df["l"].to_numpy() / pp
    spr = df["spr"].to_numpy(); spr = np.where(np.isfinite(spr), spr, 0.0)
    vs = df["volatility_state"].to_list(); acts = df["activity_state"].to_list()
    vage, vpchg = context_for_dim(vs)
    n = len(close)
    for ev in TIER1:
        sig = EVENTS_ALL[ev](close, high, low)
        for i in range(n):
            if sig[i] == 0 or i + HORIZON >= n or vs[i] == "UNKNOWN":
                continue
            net = sig[i] * (close[i + HORIZON] - close[i]) - spr[i]
            a = acts[i] if acts[i] != "UNKNOWN" else None
            tr = _pchg_bucket(vpchg[i])
            ag = AGE[_bidx(int(vage[i]))] if vage[i] > 0 else None
            for iname, key in _keys(vs[i], a, tr, ag).items():
                d = acc[ev][iname].setdefault(sym, {}).setdefault(key, [0.0, 0])
                d[0] += net; d[1] += 1


def _rankdata(x):
    order = np.argsort(x, kind="mergesort")
    r = np.empty(len(x), float); r[order] = np.arange(len(x))
    return r


def _spearman(a, b):
    if len(a) < 3:
        return float("nan")
    ra, rb = _rankdata(np.array(a)), _rankdata(np.array(b))
    if np.std(ra) == 0 or np.std(rb) == 0:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


def stability(per_pair):
    """per_pair = {pair: {cell: ev}}. Rudisha rank_consistency, cv_median,
    modal_best, modal_freq, n_pairs, n_common."""
    pairs = [p for p, d in per_pair.items() if d]
    if len(pairs) < 2:
        return None
    # common cells (zilizopo kwa >= MIN_PAIRS)
    cnt = Counter(c for p in pairs for c in per_pair[p])
    common = [c for c, k in cnt.items() if k >= min(MIN_PAIRS, len(pairs))]
    if len(common) < 2:
        return None
    # rank consistency: wastani Spearman kati ya jozi za pairs (kwa common zilizopo kwa zote)
    sps = []
    for i in range(len(pairs)):
        for j in range(i + 1, len(pairs)):
            a, b = per_pair[pairs[i]], per_pair[pairs[j]]
            cc = [c for c in common if c in a and c in b]
            if len(cc) >= 3:
                s = _spearman([a[c] for c in cc], [b[c] for c in cc])
                if s == s:
                    sps.append(s)
    rc = float(np.mean(sps)) if sps else float("nan")
    # CV per common cell across pairs
    cvs = []
    for c in common:
        vals = [per_pair[p][c] for p in pairs if c in per_pair[p]]
        if len(vals) >= MIN_PAIRS:
            m = np.mean(vals); sd = np.std(vals)
            cvs.append(sd / abs(m) if abs(m) > 1e-9 else float("inf"))
    cv_med = float(np.median(cvs)) if cvs else float("nan")
    # modal best cell (per pair argmax)
    bests = [max(per_pair[p], key=per_pair[p].get) for p in pairs if per_pair[p]]
    mb, mf = Counter(bests).most_common(1)[0]
    return dict(rc=rc, cv=cv_med, modal=mb, modal_freq=mf / len(pairs),
                n_pairs=len(pairs), n_common=len(common))


def run(pairs, tfs):
    c = cfg(); raw = REPO_ROOT / c["paths"]["raw_ticks"]
    if not raw.exists():
        print(f"HITILAFU: '{raw}' haipo.", file=sys.stderr); return 1
    con = duckdb.connect()
    acc = {ev: {i: {} for i in INTERACTIONS} for ev in TIER1}
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
            process_df(df, pp, sym, acc)
        print(f"    done", flush=True)

    L = ["# Interaction Stability — je interactions zina survive cross-market? (Phase 5.8, Tier 1)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | per-pair cell EV → rank consistency (Spearman), CV, modal "
         f"best cell | min n/cell/pair={MIN_CELL_PAIR}, min pairs={MIN_PAIRS} | outcome = forward net*\n",
         "> **Q-011 (Chief):** Phase 5.7 ilipata interaction bora (cells) lakini HAIKUPIMA stability. Je "
         "cell bora kwenye EURUSD ni bora kwenye GBPUSD? Rank consistency juu = **UNIVERSAL RULE**; chini "
         "= **ADAPTIVE/LOCAL RULE**. Interaction Engine inahitaji UNIVERSAL. NO ML.\n",
         "## Stability kwa event × interaction\n",
         "| Event | interaction | rank consist | CV med | modal best cell | modal freq | pairs | verdict |",
         "|-------|-------------|--------------|--------|-----------------|-----------|-------|---------|"]
    uni = 0; tot = 0
    for ev in TIER1:
        for iname in INTERACTIONS:
            per_pair = {sym: {cell: (d[0] / d[1]) for cell, d in cells.items() if d[1] >= MIN_CELL_PAIR}
                        for sym, cells in acc[ev][iname].items()}
            s = stability(per_pair)
            if s is None:
                L.append(f"| {ev} | {iname} | — | — | — | — | <2 | — |"); continue
            tot += 1
            universal = (s["rc"] == s["rc"] and s["rc"] >= 0.3 and s["modal_freq"] >= 0.5)
            uni += 1 if universal else 0
            verdict = "✅ UNIVERSAL" if universal else "— adaptive/local"
            L.append(f"| {ev} | {iname} | {s['rc']:+.2f} | {s['cv']:.1f} | {'×'.join(s['modal'])} | "
                     f"{s['modal_freq']*100:.0f}% | {s['n_pairs']} | {verdict} |")

    L.append("\n## VERDICT — Q-011: interactions ni universal au local?\n")
    if tot:
        L.append(f"- Universal interactions: **{uni}/{tot}** (rank consistency ≥0.3 NA modal best ≥50% pairs).")
        if uni > tot / 2:
            L.append("\n→ ✅ **Interactions ni GENERALIZABLE** (universal). Interaction Engine inaweza "
                     "kujengwa juu ya cells thabiti hizi (cross-market). Inayofuata: Market State Vector.")
        else:
            L.append("\n→ ⚠️ **Interactions nyingi ni LOCAL** (adaptive). Interaction Engine lazima iwe "
                     "ADAPTIVE per-pair, sio universal rules. Hii ni finding muhimu kabla ya kujenga engine.")
    L.append("\n*Rank consistency = wastani Spearman ya cell-EV ordering kati ya pairs (juu = ordering "
             "ileile kila pair = universal). CV = mtawanyiko wa cell EV kuvuka pairs (ndogo = stable). "
             "Modal best = cell bora inayojirudia. Universal -> Interaction Engine ya rules; Local -> "
             "engine adaptive. NO ML bado (Chief). Profitable ≠ Tradable Edge.*")
    out = REPO_ROOT / c["paths"]["reports"] / "interaction_stability_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """(1) UNIVERSAL: cell ordering ileile kwa pairs zote -> rank consistency juu.
       (2) LOCAL: ordering random kwa kila pair -> rank consistency chini."""
    rng = np.random.default_rng(0)
    cells = [("LOW", "LOW"), ("LOW", "HIGH"), ("HIGH", "LOW"), ("HIGH", "HIGH"), ("NORMAL", "NORMAL")]
    base = {c: v for c, v in zip(cells, [-3, 0, 1, 5, -1])}      # ordering ya kweli
    # (1) universal: kila pair = base + noise ndogo
    uni = {f"P{i}": {c: base[c] + rng.normal(0, 0.3) for c in cells} for i in range(8)}
    s1 = stability(uni)
    uni_ok = s1["rc"] > 0.6 and s1["modal"] == ("HIGH", "HIGH") and s1["modal_freq"] >= 0.5
    print(f"universal: rank_consist={s1['rc']:+.2f} modal={s1['modal']} freq={s1['modal_freq']*100:.0f}%")
    # (2) local: kila pair ordering random
    loc = {f"P{i}": {c: rng.normal(0, 3) for c in cells} for i in range(8)}
    s2 = stability(loc)
    loc_ok = abs(s2["rc"]) < 0.35
    print(f"local: rank_consist={s2['rc']:+.2f} (≈0?)")
    ok = uni_ok and loc_ok
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
