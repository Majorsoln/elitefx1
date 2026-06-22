"""
state_age.py — PHASE 1.6 (CQ, State Age Analysis). Markov assumption trap.

regime_transition iliuliza P(state_t -> state_t+1) — lakini hiyo inadhani
TRANSITION HAITEGEMEI UMRI wa state (Markov). Swali la Chief: je LOW ya umri
wa bar 1 ina P(stay) sawa na LOW ya umri wa bars 15?

Tunapima HAZARD kwa umri: kwa kila dimension, P(stay | age bucket).
  age = bars mfululizo ndani ya state hadi sasa (run length hadi sasa)
  buckets: 1-3 | 4-8 | 9-15 | 16+
  P(stay) ~ thabiti kwa buckets zote  => MEMORYLESS (Markov, geometric)
  P(stay) inashuka kwa umri            => state "inachoka" (duration-dependent)
  P(stay) inapanda kwa umri            => "ikidumu, inazidi kudumu"

Inasoma data/processed/state/symbol=<P>/tf=<TF>.parquet (state engine kwanza).
Output: reports/state_age_report.md
Endesha: python src/research/state_age.py
Self-test: python src/research/state_age.py --self-test
"""
from __future__ import annotations

import argparse, sys
from datetime import datetime
from pathlib import Path

import numpy as np
import polars as pl
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config" / "data_config.yaml"
TFS = ["H1", "H2", "H4", "D1"]
DIMS = [("volatility", "volatility_state"),
        ("activity",   "activity_state"),
        ("spread",     "spread_state")]
BUCKETS = [(1, 3), (4, 8), (9, 15), (16, 10**9)]
BLABEL = ["1-3", "4-8", "9-15", "16+"]


def cfg():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)

def state_path(sym, tf):
    return REPO_ROOT / cfg()["paths"]["processed"] / "state" / f"symbol={sym}" / f"tf={tf}.parquet"


def _bidx(age):
    for i, (lo, hi) in enumerate(BUCKETS):
        if lo <= age <= hi:
            return i
    return len(BUCKETS) - 1


def age_hazard(states):
    """Rudisha list ya [stay, total] kwa kila bucket (P(stay | age))."""
    res = [[0, 0] for _ in BUCKETS]
    prev = None; age = 0
    for i in range(len(states) - 1):
        cur = states[i]; nxt = states[i + 1]
        if cur == "UNKNOWN":
            prev = None; age = 0; continue
        age = age + 1 if cur == prev else 1
        prev = cur
        if nxt == "UNKNOWN":
            continue
        bi = _bidx(age)
        res[bi][1] += 1
        if nxt == cur:
            res[bi][0] += 1
    return res


def pstay(res):
    return [(s / t if t else float("nan")) for s, t in res]


def run(pairs, tfs):
    miss = []; data = {d[0]: [] for d in DIMS}
    for sym in pairs:
        for tf in tfs:
            p = state_path(sym, tf)
            if not p.exists():
                miss.append(f"{sym}/{tf}"); continue
            df = pl.read_parquet(p)
            for dim, col in DIMS:
                res = age_hazard(df[col].to_list())
                data[dim].append((sym, tf, res))
    if all(len(v) == 0 for v in data.values()):
        print("HITILAFU: hakuna state parquet. Endesha market_state_engine.py kwanza.\n"
              f"  Zilizokosekana: {', '.join(miss[:8])}{'...' if len(miss)>8 else ''}", file=sys.stderr)
        return 1

    L = ["# State Age Report — duration-dependence (Phase 1.6)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | P(stay | age bucket) kwa dimension | "
         "age = bars mfululizo hadi sasa | chanzo: state series*\n",
         "> Markov test: P(stay) ~ thabiti = MEMORYLESS; inashuka = state inachoka; inapanda = "
         "ikidumu inazidi kudumu. Δ = P(stay)@16+ − P(stay)@1-3.\n"]
    for dim, _ in DIMS:
        L.append(f"\n## {dim.upper()} — P(stay) % kwa umri wa state\n")
        L.append("| Pair | TF | " + " | ".join(BLABEL) + " | Δ(16+ −1-3) | tabia |")
        L.append("|------|----|" + "----|" * len(BLABEL) + "----|----|")
        for sym, tf, res in data[dim]:
            ps = pstay(res)
            d = (ps[3] - ps[0]) if (ps[3] == ps[3] and ps[0] == ps[0]) else float("nan")
            beh = "—" if d != d else ("↑ inazidi" if d > 0.03 else ("↓ inachoka" if d < -0.03 else "flat(Markov)"))
            cells = " | ".join(f"{x*100:.0f}" if x == x else "—" for x in ps)
            L.append(f"| {sym} | {tf} | {cells} | {d*100:+.0f} | {beh} |")

    # muhtasari wa tabia kwa dimension
    L.append("\n## Muhtasari — je transition inategemea umri?\n")
    for dim, _ in DIMS:
        ds = []
        for _, _, res in data[dim]:
            ps = pstay(res)
            if ps[0] == ps[0] and ps[3] == ps[3]:
                ds.append(ps[3] - ps[0])
        if ds:
            md = float(np.median(ds))
            verd = "↑ persistence inakua na umri" if md > 0.03 else \
                   ("↓ state inachoka (duration-dependent)" if md < -0.03 else "≈ MEMORYLESS (Markov inashikilia)")
            L.append(f"- **{dim}**: median Δ = {md*100:+.1f}pp → {verd}")

    if miss:
        L.append(f"\n*Hazikupatikana: {len(miss)} pair×TF.*")
    L.append("\n---\n*P(stay|age) inajaribu Markov assumption. Kama hazard inategemea umri, transition "
             "matrix peke yake haitoshi — Triple Barrier & event timing zitumie UMRI wa state pia. "
             "Δ ndogo (flat) = geometric durations (Markov ok). Metric = EV (CQ-008).*")
    out = REPO_ROOT / cfg()["paths"]["reports"] / "state_age_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"Ripoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """(1) Deterministic duration=8 -> age-dependent (P(stay) inashuka kwa umri).
       (2) Geometric (p_change=0.2) -> ~flat (Markov)."""
    # (1) kila run = bars 8 (A kisha B kubadilishana)
    det = []
    for k in range(400):
        det += [("A" if k % 2 == 0 else "B")] * 8
    res = age_hazard(det); ps = pstay(res)
    print(f"deterministic(8): P(stay) {[round(x,2) for x in ps]} (1-3 juu, 4-8 chini)")
    det_ok = ps[0] > ps[1]                    # 1-3 stays 100%, 4-8 ina age=8 inayobadilika
    # (2) geometric
    rng = np.random.default_rng(0); geo = []; cur = "A"
    for _ in range(40000):
        geo.append(cur)
        if rng.random() < 0.2:
            cur = "B" if cur == "A" else "A"
    res2 = age_hazard(geo); ps2 = pstay(res2)
    valid = [x for x in ps2 if x == x]
    flat = (max(valid) - min(valid)) < 0.08 if valid else False
    print(f"geometric(0.2): P(stay) {[round(x,2) for x in ps2]} (~flat ~0.8)")
    ok = det_ok and flat
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default=None); ap.add_argument("--tf", default=None, choices=TFS)
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
