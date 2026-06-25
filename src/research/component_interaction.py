"""
component_interaction.py — PHASE 5.7 (Chief Quant). Component Interaction.

Phase 5.6 iliganua context kuwa components na kupata volatility/activity zenye
mchango mkubwa zaidi (MARGINALLY). Lakini Chief correction (F-012): marginal
attribution ≠ feature importance. Soko hufanya kazi kama:

    Volatility × Activity × Transition × Age   (kwa wakati mmoja)

Kwa hiyo edge inaweza kuwa kwenye INTERACTION, sio component moja. Phase 5.7
inapima interactions kwa Tier-1 events:

  2-way:  Volatility × Activity
          Volatility × Transition
          Activity × State Age
          Transition × State Age
  3-way:  Volatility × Activity × Transition

Kwa kila cell ya interaction: AvgWin · AvgLoss · EV · n. SWALI: je EV-spread ya
JOINT (interaction) inazidi marginal spreads? Ikizidi -> interaction inaongeza
discrimination -> F-012 imethibitishwa, na pia inatofautisha **Driver** (athari
ya moja kwa moja) na **Gatekeeper** (huruhusu/kuzuia mazingira ya payoff).

Outcome = forward HORIZON net ya spread (ileile ya F-009/F-010). NO ML, NO
Payoff Engine bado — interaction structure kwanza (Chief).

Reuse: market_state_engine, state_context_engine, event_library, context_value.

Output: reports/component_interaction_report.md
Endesha: python src/research/component_interaction.py
         python src/research/component_interaction.py --symbol EURGBP --tf H1
Self-test: python src/research/component_interaction.py --self-test
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
from context_value import HORIZON

REPO_ROOT = Path(__file__).resolve().parents[2]
TFS = ["H1", "H2", "H4", "D1"]
TIER1 = ["mean_reversion", "pullback", "deep_pullback", "trend_continuation"]
GROUP_A = {"mean_reversion", "deep_pullback"}
VOL = ["LOW", "NORMAL", "HIGH"]; ACT = ["LOW", "NORMAL", "HIGH"]
TRANS = ["Tlo", "Tmid", "Thi"]; AGE = ["1-3", "4-8", "9-15", "16+"]
# 2-way interactions (Chief): (name, A-order, B-order, A-key, B-key)
INTERACTIONS = [
    ("volatility×activity",  VOL, ACT, "vol", "act"),
    ("volatility×transition", VOL, TRANS, "vol", "trans"),
    ("activity×state_age",   ACT, AGE, "act", "age"),
    ("transition×state_age", TRANS, AGE, "trans", "age"),
]
MIN_CELL = 100          # instances za chini kwa cell ili kuhesabu
_posix = lambda p: str(p).replace("\\", "/")


def _pchg_bucket(p):
    if not np.isfinite(p):
        return None
    return "Tlo" if p < 0.08 else ("Tmid" if p < 0.15 else "Thi")


def _acc(store, key, net):
    d = store.setdefault(key, [0.0, 0, 0.0, 0, 0.0, 0])
    d[0] += net; d[1] += 1
    if net > 0: d[2] += net; d[3] += 1
    else: d[4] += -net; d[5] += 1


def _ev(d):  return d[0] / d[1] if d[1] else float("nan")
def _avgwin(d):  return d[2] / d[3] if d[3] else 0.0
def _avgloss(d): return d[4] / d[5] if d[5] else 0.0


def _spread(store):
    evs = [_ev(d) for d in store.values() if d[1] >= MIN_CELL]
    return (max(evs) - min(evs)) if len(evs) >= 2 else float("nan")


def _new_acc():
    return dict(vol={}, act={}, trans={}, age={},                 # marginals
                inter={n[0]: {} for n in INTERACTIONS}, three={})  # 2-way + 3-way


def process_df(df, pp, acc):
    close = df["c"].to_numpy() / pp; high = df["h"].to_numpy() / pp; low = df["l"].to_numpy() / pp
    spr = df["spr"].to_numpy(); spr = np.where(np.isfinite(spr), spr, 0.0)
    vs = df["volatility_state"].to_list(); acts = df["activity_state"].to_list()
    vage, vpchg = context_for_dim(vs)
    n = len(close)
    for ev in TIER1:
        sig = EVENTS_ALL[ev](close, high, low)
        A = acc[ev]
        for i in range(n):
            if sig[i] == 0 or i + HORIZON >= n or vs[i] == "UNKNOWN":
                continue
            net = sig[i] * (close[i + HORIZON] - close[i]) - spr[i]
            v = vs[i]
            a = acts[i] if acts[i] != "UNKNOWN" else None
            tr = _pchg_bucket(vpchg[i])
            ag = AGE[_bidx(int(vage[i]))] if vage[i] > 0 else None
            comp = dict(vol=v, act=a, trans=tr, age=ag)
            # marginals
            _acc(A["vol"], v, net)
            if a: _acc(A["act"], a, net)
            if tr: _acc(A["trans"], tr, net)
            if ag: _acc(A["age"], ag, net)
            # 2-way
            for nm, _Al, _Bl, ka, kb in INTERACTIONS:
                va, vb = comp[ka], comp[kb]
                if va is not None and vb is not None:
                    _acc(A["inter"][nm], (va, vb), net)
            # 3-way vol×act×trans
            if a and tr:
                _acc(A["three"], (v, a, tr), net)


def run(pairs, tfs):
    c = cfg(); raw = REPO_ROOT / c["paths"]["raw_ticks"]
    if not raw.exists():
        print(f"HITILAFU: '{raw}' haipo.", file=sys.stderr); return 1
    con = duckdb.connect()
    acc = {ev: _new_acc() for ev in TIER1}
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
            process_df(df, pp, acc)
            print(f"    {tf}: done", flush=True)

    marg_key = {"vol": "vol", "act": "act", "trans": "trans", "age": "age"}
    L = ["# Component Interaction — je edge iko kwenye INTERACTION? (Phase 5.7, Tier 1)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | 2-way + 3-way interactions | cell = EV (pips) net | "
         f"min n/cell = {MIN_CELL} | outcome = forward net | Group A=reward, B=loss*\n",
         "> **F-012 / Q-010 (Chief):** marginal ≠ importance. Edge inaweza kuwa kwenye Vol×Act×Transition, "
         "sio component moja. Joint EV-spread > marginal spread -> interaction inaongeza discrimination. "
         "Pia: **Driver ≠ Gatekeeper** (Transition inaweza kuwa gate, sio driver). NO ML, NO Payoff Engine.\n"]
    inter_wins = 0; inter_tot = 0
    for ev in TIER1:
        A = acc[ev]; grp = "A (Reward)" if ev in GROUP_A else "B (Loss)"
        L.append(f"\n## {ev} — Group {grp}\n")
        marg_sp = {k: _spread(A[marg_key[k]]) for k in marg_key}
        for nm, Al, Bl, ka, kb in INTERACTIONS:
            store = A["inter"][nm]
            L.append(f"### {nm} — EV (pips) per cell\n")
            L.append("| " + ka + " \\ " + kb + " | " + " | ".join(Bl) + " |")
            L.append("|" + "----|" * (len(Bl) + 1))
            for ra in Al:
                cells = []
                for cb in Bl:
                    d = store.get((ra, cb))
                    cells.append(f"{_ev(d):+.1f}" if (d and d[1] >= MIN_CELL) else "—")
                L.append(f"| {ra} | " + " | ".join(cells) + " |")
            js = _spread(store)
            ms = max([marg_sp[ka], marg_sp[kb]] if marg_sp[ka] == marg_sp[ka] and marg_sp[kb] == marg_sp[kb]
                     else [x for x in [marg_sp[ka], marg_sp[kb]] if x == x] or [float("nan")])
            adds = (js == js and ms == ms and js > ms)
            inter_tot += 1; inter_wins += 1 if adds else 0
            L.append(f"\n→ joint EV-spread = {js:.1f} vs marginal max ({ka}/{kb}) = {ms:.1f} → "
                     f"{'✅ interaction inaongeza discrimination' if adds else '— haiongezi zaidi ya marginal'}\n")
        # 3-way: top/bottom EV cells
        three = [((v, a, tr), _ev(d), d[1]) for (v, a, tr), d in A["three"].items() if d[1] >= MIN_CELL]
        three.sort(key=lambda x: x[1], reverse=True)
        if three:
            L.append("### volatility×activity×transition — top/bottom EV cells\n")
            L.append("| rank | vol×act×trans | EV | n |")
            L.append("|------|---------------|----|---|")
            for r in three[:3]:
                L.append(f"| top | {'×'.join(r[0])} | {r[1]:+.1f} | {r[2]:,} |")
            for r in three[-2:]:
                L.append(f"| bottom | {'×'.join(r[0])} | {r[1]:+.1f} | {r[2]:,} |")
            L.append(f"\n→ 3-way EV range = **{three[0][1] - three[-1][1]:.1f} pips** "
                     f"(best {'×'.join(three[0][0])} {three[0][1]:+.1f} vs worst {three[-1][1]:+.1f})")

    L.append("\n## VERDICT — F-012: je interactions zinaongeza discrimination zaidi ya marginals?\n")
    if inter_tot:
        L.append(f"- Interactions zinazoongeza discrimination: **{inter_wins}/{inter_tot}** (2-way × Tier-1).")
        if inter_wins > inter_tot / 2:
            L.append("\n→ ✅ **F-012 imethibitishwa**: edge iko kwenye INTERACTION, sio component moja. "
                     "Interaction Engine ijengwe kabla ya Payoff Engine. Transition (marginal ndogo) inaweza "
                     "kuwa **GATEKEEPER** (inaruhusu vol×act) — Driver ≠ Gatekeeper.")
        else:
            L.append("\n→ Interactions hazikuongeza discrimination wazi zaidi ya marginals; inahitaji 3-way "
                     "au components zaidi.")
    L.append("\n*Joint EV-spread > marginal = interaction matters (F-012). 3-way range inaonyesha kama "
             "vol×act×transition pamoja zinazalisha cells zenye EV tofauti sana. Hii ndiyo 'market "
             "mechanism modeling' (sio feature importance). Payoff Engine (Phase 6) ijengwe juu ya "
             "interaction structure HII. NO ML bado. Profitable ≠ Tradable Edge.*")
    out = REPO_ROOT / c["paths"]["reports"] / "component_interaction_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """Synthetic: EV kubwa TU pale vol=HIGH NA act=HIGH (interaction). Marginally
    vol na act zina spread ndogo; joint spread kubwa -> interaction inaongeza."""
    rng = np.random.default_rng(0); N = 90000
    acc = {"ev": _new_acc()}; X = acc["ev"]
    for _ in range(N):
        v = rng.choice(VOL); a = rng.choice(ACT); tr = rng.choice(TRANS)
        edge = 10.0 if (v == "HIGH" and a == "HIGH") else 0.0     # interaction-only edge
        net = edge + rng.normal(0, 4)
        _acc(X["vol"], v, net); _acc(X["act"], a, net); _acc(X["trans"], tr, net)
        _acc(X["inter"]["volatility×activity"], (v, a), net)
        _acc(X["three"], (v, a, tr), net)
    js = _spread(X["inter"]["volatility×activity"])
    ms = max(_spread(X["vol"]), _spread(X["act"]))
    ok = js > ms * 2 and js > 5
    print(f"joint(vol×act) EV-spread={js:.1f} vs marginal max={ms:.1f} (interaction adds={ok})")
    # best 3-way cell lazima iwe HIGH×HIGH×*
    three = sorted(((k, _ev(d)) for k, d in X["three"].items() if d[1] >= MIN_CELL),
                   key=lambda x: x[1], reverse=True)
    best_ok = three[0][0][0] == "HIGH" and three[0][0][1] == "HIGH"
    print(f"best 3-way cell = {three[0][0]} EV={three[0][1]:+.1f} (HIGH×HIGH={best_ok})")
    ok = ok and best_ok
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
