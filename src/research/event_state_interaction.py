"""
event_state_interaction.py — PHASE 6 (Chief Quant). Interaction Engine.

Phase 5.13 (F-019) ilithibitisha: information ina value tu ikiwa inaboresha
Expected Payoff au Decision Quality. Representation iliboresha EV-SELECTION
(uchaguzi) lakini sio LogLoss (utabiri) -> Principle 21: Selection > Prediction.

Lakini bado hatujapima moja kwa moja **Event × Configuration**. Edge inaweza
kujificha hapo (F-020, Experimental):

    Pullback inside State X  ≠  Pullback inside State Y.

Phase 6 (Interaction Engine) inapima, kwa kila Event × latent state:

  • EV (net pips) + 95% Confidence Interval
  • Win rate
  • Triple Barrier outcomes (TP / SL / TIME)
  • Sample size (N)

-> tunajua "Pullback works ONLY inside State X" au "Breakout dies inside State Y".
Hapo ndipo Opportunity Engine itazaliwa (acceptance rule: hakuna Event inaingia
bila Event × Configuration → Expected Payoff).

Outcome = forward HORIZON net ya spread; Triple Barrier = ±KSIG·ATR, VERT bars,
direction-aware. Inahitaji OHLC kwenye state parquet. NO ML (Chief: hatujajenga
target bado).

Reuse: latent_structure(kmeans, collect, state_path), mechanism_discovery
(signatures), event_library, context_value(HORIZON), triple_barrier_design(first_touch).

Output: reports/event_state_interaction_report.md
Self-test: python src/research/event_state_interaction.py --self-test
"""
from __future__ import annotations

import argparse, sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np
import polars as pl

from market_state_engine import cfg, pip
from mechanism_discovery import signatures
from latent_structure import kmeans, collect, state_path
from event_library import EVENTS_ALL
from context_value import HORIZON
from triple_barrier_design import first_touch

REPO_ROOT = Path(__file__).resolve().parents[2]
TFS = ["H1", "H2", "H4", "D1"]
EVENTS_SET = ["pullback", "deep_pullback", "trend_continuation", "breakout", "mean_reversion"]
K = 4
VERT = 10              # vertical barrier (bars)
KSIG = 1.0             # barrier width (× ATR @ entry)
MIN_N = 150            # sample ya chini kwa (event, state) ili kuripoti
_posix = lambda p: str(p).replace("\\", "/")


def assign(sig, cen):
    return ((sig[:, None, :] - cen[None, :, :]) ** 2).sum(2).argmin(1)


def _ci95(x):
    a = np.array(x, float)
    return 1.96 * a.std(ddof=1) / np.sqrt(len(a)) if len(a) > 1 else float("nan")


def run(pairs, tfs):
    c = cfg(); rng = np.random.default_rng(0)
    pool = [X for sym in pairs if len(X := collect(sym, rng)) > 50]
    if not pool:
        print("HITILAFU: hakuna state parquet. Endesha market_state_engine.py kwanza.", file=sys.stderr)
        return 1
    _, cen, _ = kmeans(np.vstack(pool), K, rng)
    print(f"  latent clusters k={K} fitted", flush=True)

    # acc[event][cluster] = dict(net=[], win=[], tb=Counter())
    acc = {ev: {j: dict(net=[], win=[], tb=Counter()) for j in range(K)} for ev in EVENTS_SET}
    no_px = True
    for sym in pairs:
        pp = pip(sym)
        for tf in TFS:
            p = state_path(sym, tf)
            if not p.exists():
                continue
            df = pl.read_parquet(p)
            if "c" not in df.columns:
                continue
            no_px = False
            sig, *_ = signatures(df, pp); fin = np.all(np.isfinite(sig), axis=1)
            cl = np.full(len(sig), -1)
            if fin.any():
                cl[fin] = assign(sig[fin], cen)
            close = df["c"].to_numpy() / pp; high = df["h"].to_numpy() / pp; low = df["l"].to_numpy() / pp
            atr_pips = df["atr"].to_numpy() / pp
            spr = df["spr"].to_numpy(); spr = np.where(np.isfinite(spr), spr, 0.0)
            n = len(close)
            for ev in EVENTS_SET:
                s = EVENTS_ALL[ev](close, high, low)
                for i in range(n):
                    if s[i] == 0 or cl[i] < 0 or i + VERT >= n or not (atr_pips[i] > 0):
                        continue
                    d = int(s[i]); A = acc[ev][cl[i]]
                    if i + HORIZON < n:
                        A["net"].append(float(d * (close[i + HORIZON] - close[i]) - spr[i]))
                        A["win"].append(1 if d * (close[i + HORIZON] - close[i]) - spr[i] > 0 else 0)
                    tb, oc = first_touch(i, d, KSIG * atr_pips[i], close, high, low, n)
                    A["tb"][oc if tb <= VERT else "TIME"] += 1
        print(f"  {sym}: done", flush=True)
    if no_px:
        print("HITILAFU: OHLC haipo. Endesha market_state_engine.py (OHLC update) kwanza.", file=sys.stderr)
        return 1

    L = ["# Event × State Interaction — edge iko kwenye mwingiliano? (Phase 6, Interaction Engine)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | events × latent state (k={K}) | EV±95%CI (net pips), Win, "
         f"Triple Barrier (±{KSIG:.1f}σ, {VERT}b) | outcome forward {HORIZON}b net | min N={MIN_N}*\n",
         "> **F-020 (Chief, Experimental):** trading edge inaweza kutoka **Event × Configuration**, sio "
         "Event peke yake. 'Pullback works ONLY inside State X.' Acceptance rule: hakuna Event inaingia "
         "Opportunity Engine bila Event × Configuration → Expected Payoff. Principle 21: Selection > "
         "Prediction. NO ML.\n"]
    edge_events = 0; tot = 0
    for ev in EVENTS_SET:
        # pooled (event alone)
        allnet = [x for j in range(K) for x in acc[ev][j]["net"]]
        if len(allnet) < MIN_N:
            L.append(f"\n## {ev}\n*(N<{MIN_N})*"); continue
        tot += 1
        pooled_ev = float(np.mean(allnet))
        L.append(f"\n## {ev} — Event alone EV = {pooled_ev:+.2f} pips (N={len(allnet):,})\n")
        L.append("| state | N | EV [95% CI] | Win% | TP/SL/TIME |")
        L.append("|-------|---|-------------|------|------------|")
        cell_ev = []
        for j in range(K):
            A = acc[ev][j]; nN = len(A["net"])
            if nN < MIN_N:
                L.append(f"| C{j} | {nN} | (N<{MIN_N}) | — | — |"); continue
            e = float(np.mean(A["net"])); ci = _ci95(A["net"]); w = float(np.mean(A["win"]))
            tb = A["tb"]; t = sum(tb.values()) or 1
            cell_ev.append((j, e, ci, nN))
            L.append(f"| C{j} | {nN:,} | {e:+.2f} [{e-ci:+.1f},{e+ci:+.1f}] | {w*100:.0f}% | "
                     f"{100*tb['TP']/t:.0f}/{100*tb['SL']/t:.0f}/{100*tb['TIME']/t:.0f} |")
        if len(cell_ev) >= 2:
            best = max(cell_ev, key=lambda x: x[1]); worst = min(cell_ev, key=lambda x: x[1])
            spread = best[1] - worst[1]
            # edge: best cluster EV CI ya chini > event-alone EV (significant uplift)
            sig_edge = (best[1] - best[2]) > pooled_ev and spread > 2.0
            edge_events += 1 if sig_edge else 0
            L.append(f"\n→ **{ev}**: best **C{best[0]}** EV {best[1]:+.2f} vs worst **C{worst[0]}** "
                     f"{worst[1]:+.2f} (spread {spread:.1f} pips). "
                     f"{'✅ edge kwenye Event×State (C'+str(best[0])+' significant > event-alone)' if sig_edge else '— mwingiliano dhaifu'}")

    L.append("\n## VERDICT — F-020: edge iko kwenye Event × Configuration?\n")
    if tot:
        L.append(f"- events zenye edge ya Event×State (best-cluster EV CI ya chini > event-alone, spread "
                 f">2 pips): **{edge_events}/{tot}**")
        if edge_events >= 1:
            L.append("\n→ ✅ **F-020 inaungwa mkono**: kwa events kadhaa, EV inategemea LATENT STATE "
                     "(Event × Configuration). Hii ndiyo msingi wa Opportunity Engine: rank Event×State "
                     "combos kwa Expected Payoff. (Experimental — confirm kwa walk-forward.)")
        else:
            L.append("\n→ ⚠️ Event×State haijaonyesha edge kubwa zaidi ya Event alone; inahitaji "
                     "configuration/representation bora.")
    L.append("\n*Event × latent state EV±CI = je tukio linafanya kazi ndani ya configuration fulani tu. "
             "Edge = best-cluster EV (CI ya chini) inazidi event-alone EV. Principle 21: Selection > "
             "Prediction. F-019: information ina value tu ikiboresha payoff/decision. Acceptance rule: "
             "Event × Configuration → Expected Payoff kabla ya Opportunity Engine. NO ML bado (target "
             "haijajengwa). Profitable ≠ Tradable Edge.*")
    out = REPO_ROOT / c["paths"]["reports"] / "event_state_interaction_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """(1) CI helper sahihi. (2) Event×cluster edge detection: cluster moja EV juu sana
       (CI ya chini > pooled) -> edge inagunduliwa; flat -> hakuna."""
    rng = np.random.default_rng(0)
    # CI: known
    x = rng.normal(0, 10, 4000); ci = _ci95(x)
    ci_ok = abs(ci - 1.96 * 10 / np.sqrt(4000)) < 0.1
    print(f"CI95: {ci:.3f} (tarajio ~{1.96*10/np.sqrt(4000):.3f}, ok={ci_ok})")
    # edge case: 4 clusters, C3 EV=+6, others ~0
    cells = []
    for j in range(4):
        mu = 6.0 if j == 3 else 0.0
        net = rng.normal(mu, 5, 3000)
        cells.append((j, float(net.mean()), _ci95(net), len(net)))
    pooled = np.mean([6.0 if j == 3 else 0.0 for j in range(4)])  # ~1.5
    best = max(cells, key=lambda c: c[1])
    edge = (best[0] == 3 and (best[1] - best[2]) > pooled)
    print(f"edge: best=C{best[0]} EV={best[1]:+.2f} CIlow={best[1]-best[2]:+.2f} vs pooled~{pooled:.1f} (edge={edge})")
    # null: all ~0
    cells2 = [(j, float(rng.normal(0, 5, 3000).mean()), 0.2, 3000) for j in range(4)]
    spread2 = max(c[1] for c in cells2) - min(c[1] for c in cells2)
    null_ok = spread2 < 1.0
    print(f"null spread={spread2:.2f} (<1?)")
    ok = ci_ok and edge and null_ok
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default=None)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    c = cfg()
    pairs = [a.symbol] if a.symbol else c["pairs"]
    return run(pairs, None)


if __name__ == "__main__":
    raise SystemExit(main())
