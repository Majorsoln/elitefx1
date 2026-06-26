"""
representation_value.py — PHASE 5.13 (Chief Quant). Representation Value.

Chief reassessment: tunatoka MARKET SCIENCE kwenda TRADING SCIENCE.

  Swali la zamani:  "Soko lina states gani?"
  Swali jipya:      "Ni taarifa zipi za soko zinazobadilisha ubora wa MAAMUZI?"

Principle 19: hakuna feature/state/representation inabaki ELITEFX bila kuboresha
Expected Value AU Decision Quality. Principle 18 (mpya): representation ni valid
ikiwa inaboresha decision quality, BILA kujali clustering algorithm.

Hii inajaribu **latent-state representation** (k-means clusters za Phase 5.9A)
kwa Tier-1 events: je kuiongeza kunaboresha?

  • Expected Value      — EV ya event ndani ya cluster bora vs zote (selection uplift)
  • Probability calibration — LogLoss ya P(win|cluster) vs base-rate
  • Opportunity ranking — EV inatofautiana kuvuka clusters? (discrimination)
  • Trade selection     — kuchukua clusters EV>0 (gate) inaboresha EV?

Kama hakuna kinachoboreshwa -> representation IONDOLEWE (Principle 19).

Outcome = forward HORIZON net ya spread (inahitaji OHLC kwenye state parquet —
endesha market_state_engine baada ya OHLC update). ONLINE prequential
(no-lookahead) kwa selection/calibration. NO ML.

Reuse: latent_structure(kmeans, collect, state_path), mechanism_discovery
(signatures), event_library, context_value(event_records, prequential_value,
HORIZON).

Output: reports/representation_value_report.md
Self-test: python src/research/representation_value.py --self-test
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
from latent_structure import kmeans, collect, state_path, CAP_PER_PAIR
from event_library import EVENTS_ALL
from context_value import event_records, prequential_value, HORIZON

REPO_ROOT = Path(__file__).resolve().parents[2]
TFS = ["H1", "H2", "H4", "D1"]
TIER1 = ["mean_reversion", "pullback", "deep_pullback", "trend_continuation"]
K = 4
_posix = lambda p: str(p).replace("\\", "/")


def assign(sig, cen):
    return ((sig[:, None, :] - cen[None, :, :]) ** 2).sum(2).argmin(1)


def run(pairs, tfs):
    c = cfg(); rng = np.random.default_rng(0)
    # 1) fit latent clusters (representation under test)
    pool = []
    for sym in pairs:
        X = collect(sym, rng)
        if len(X) > 50:
            pool.append(X)
    if not pool:
        print("HITILAFU: hakuna state parquet. Endesha market_state_engine.py kwanza.", file=sys.stderr)
        return 1
    _, cen, _ = kmeans(np.vstack(pool), K, rng)
    print(f"  latent clusters k={K} fitted", flush=True)

    # 2) per Tier-1 event: outcome + cluster
    data = {ev: dict(keys=[], net=[], win=[], rm=[], hit=[]) for ev in TIER1}
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
            sig, *_ = signatures(df, pp)
            fin = np.all(np.isfinite(sig), axis=1)
            cl = np.full(len(sig), -1)
            if fin.any():
                cl[fin] = assign(sig[fin], cen)
            close = df["c"].to_numpy() / pp; high = df["h"].to_numpy() / pp; low = df["l"].to_numpy() / pp
            atr_pips = df["atr"].to_numpy() / pp
            spr = df["spr"].to_numpy(); spr = np.where(np.isfinite(spr), spr, 0.0)
            age0 = np.ones(len(close))                       # dummy (abk haitumiki hapa)
            for ev in TIER1:
                s = EVENTS_ALL[ev](close, high, low)
                idx, nets, wins, rms, hits, _ = event_records(close, spr, atr_pips, s, age0)
                D = data[ev]
                for k, i in enumerate(idx):
                    if cl[i] < 0:
                        continue
                    D["keys"].append(f"C{cl[i]}"); D["net"].append(nets[k]); D["win"].append(int(wins[k]))
                    D["rm"].append(rms[k]); D["hit"].append(int(hits[k]))
        print(f"  {sym}: done", flush=True)

    if no_px:
        print("HITILAFU: OHLC haipo kwenye state parquet. Endesha market_state_engine.py (OHLC update) "
              "kwanza ili kupima representation VALUE (inahitaji outcomes).", file=sys.stderr)
        return 1

    L = ["# Representation Value — je latent representation inaboresha MAAMUZI? (Phase 5.13)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | representation = latent clusters (k={K}, Phase 5.9A) | Tier-1 "
         f"events | outcome forward {HORIZON} bars net ya spread | ONLINE prequential | metric = EV + "
         "calibration (Principle 19)*\n",
         "> **Trading Science (Chief):** swali sio 'states gani' bali 'taarifa gani inaboresha MAAMUZI'. "
         "Representation ina VALUE ikiwa inaboresha EV-selection AU calibration (LogLoss). Vinginevyo "
         "**iondolewe** (Principle 19). Principle 18: decision quality > algorithm agreement. NO ML.\n",
         "## Decision value kwa event — Event alone vs Event + latent representation\n",
         "| event | n | EV all→sel | uplift | Win all→sel | LogLoss base→repr | calib Δ% | value? |",
         "|-------|---|------------|--------|-------------|-------------------|----------|--------|"]
    valued = 0; total = 0
    for ev in TIER1:
        D = data[ev]
        if len(D["net"]) < 200:
            L.append(f"| {ev} | {len(D['net'])} | — | — | — | — | — | (n<200) |"); continue
        total += 1
        m = prequential_value(D["keys"], [0] * len(D["keys"]),
                              np.array(D["net"]), np.array(D["win"]), np.array(D["rm"]), np.array(D["hit"]))
        a, b = m["A"], m["B"]
        uplift = b["ev"] - a["ev"]; dll = (m["ll_A"] - m["ll_B"]) / m["ll_A"] * 100 if m["ll_A"] else 0
        value = (uplift > 0 and b["ev"] > a["ev"]) or (m["ll_B"] < m["ll_A"])
        valued += 1 if value else 0
        L.append(f"| {ev} | {m['A']['n']:,} | {a['ev']:+.2f}→{b['ev']:+.2f} | {uplift:+.2f} | "
                 f"{a['win']*100:.0f}→{b['win']*100:.0f}% | {m['ll_A']:.3f}→{m['ll_B']:.3f} | {dll:+.1f} | "
                 f"{'✅' if value else '—'} |")

    # per-cluster EV (discrimination / opportunity ranking)
    L.append("\n## EV per latent cluster (pooled Tier-1) — opportunity ranking\n")
    L.append("| cluster | n | EV (pips) | Win% |")
    L.append("|---------|---|-----------|------|")
    allk = Counter(); allnet = {}
    for ev in TIER1:
        for kk, nn, ww in zip(data[ev]["keys"], data[ev]["net"], data[ev]["win"]):
            allk[kk] += 1; allnet.setdefault(kk, []).append(nn)
    for kk in sorted(allnet):
        x = np.array(allnet[kk]); L.append(f"| {kk} | {len(x):,} | {x.mean():+.2f} | {(x>0).mean()*100:.0f}% |")
    evs = [np.mean(allnet[kk]) for kk in allnet if len(allnet[kk]) >= 200]
    disc = (max(evs) - min(evs)) if len(evs) >= 2 else float("nan")

    L.append("\n## VERDICT — Principle 19: latent representation ina decision value?\n")
    L.append(f"- events zenye value (EV-selection au calibration): **{valued}/{total}** | EV discrimination "
             f"kuvuka clusters = **{disc:+.2f} pips**")
    if total and valued > total / 2:
        L.append("\n→ ✅ **Representation INA VALUE**: inaboresha EV-selection/calibration kwa Tier-1 "
                 "(Principle 19 imetimizwa). Inaweza kuendelea kwenye Opportunity Engine (ranking ya "
                 "Expected Payoff).")
    else:
        L.append("\n→ ❌ **Representation HAIONGEZI value ya kutosha** (Principle 19): inaboresha "
                 f"{valued}/{total} events tu. Kwa mujibu wa Principle 19, representation hii **iondolewe** "
                 "au irekebishwe kabla ya Opportunity Engine.")
    L.append("\n*Decision value = EV-selection uplift AU calibration (LogLoss) improvement (online "
             "prequential, no-lookahead). Principle 18: decision quality > algorithm agreement. Principle "
             "19: hakuna representation inabaki bila kuboresha EV/Decision Quality. Opportunity Engine "
             "itatabiri Expected Payoff (ranking), sio BUY/SELL. NO ML bado. Profitable ≠ Tradable Edge.*")
    out = REPO_ROOT / c["paths"]["reports"] / "representation_value_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """(1) representation INA value: cluster inatabiri net -> EV-selection uplift + LogLoss B<A.
       (2) null: cluster random -> hakuna uplift. Inatumia context_value.prequential_value."""
    rng = np.random.default_rng(0); N = 30000
    # (1) informative: C_good -> +net, C_bad -> -net (P(win) pia inabadilika)
    keys = []; nets = []; wins = []; rms = []; hits = []
    for _ in range(N):
        good = rng.random() < 0.5
        net = rng.normal(+3 if good else -3, 5)
        keys.append("Cg" if good else "Cb"); nets.append(net); wins.append(1 if net > 0 else 0)
        rms.append(net / 5); hits.append(1 if net > 0 else 0)
    m = prequential_value(keys, [0] * N, np.array(nets), np.array(wins), np.array(rms), np.array(hits))
    inf_ok = m["B"]["ev"] > m["A"]["ev"] + 0.5 and m["ll_B"] < m["ll_A"]
    print(f"informative: EV {m['A']['ev']:+.2f}->{m['B']['ev']:+.2f} | LogLoss {m['ll_A']:.3f}->{m['ll_B']:.3f} (value={inf_ok})")
    # (2) null
    keys2 = [("Cg" if rng.random() < 0.5 else "Cb") for _ in range(N)]
    nets2 = rng.normal(0, 5, N); wins2 = (nets2 > 0).astype(int)
    m2 = prequential_value(keys2, [0] * N, nets2, wins2, nets2 / 5, wins2)
    null_ok = abs(m2["B"]["ev"] - m2["A"]["ev"]) < 0.5
    print(f"null: EV {m2['A']['ev']:+.2f}->{m2['B']['ev']:+.2f} (ΔEV≈0={null_ok})")
    # assign sanity
    asg = assign(np.array([[0.0, 0], [9, 9]]), np.array([[0.0, 0], [10, 10]]))
    ok = inf_ok and null_ok and list(asg) == [0, 1]
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
