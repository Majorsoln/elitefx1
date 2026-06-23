"""
state_context_engine.py — PHASE 1.7 (CQ-012). State Context Engine.

State Age report ilithibitisha: P(change) inategemea UMRI wa state (Markov
imeanguka). Kwa hiyo context kamili ya bar yoyote ni:

    { state, state_age, transition_probability }   (kwa kila dimension)

transition_probability = P(change | state, age-bucket), iliyokadiriwa
ONLINE kutoka historia ya NYUMA TU (no-lookahead): kwa kila bar tunatumia
makisio kutoka transitions zilizoonekana kabla yake, kisha tunasasisha.

Hii ndiyo Context Layer ambayo Event Layer & Triple Barrier zitaitumia
(doctrine V5.1: STATE -> STATE AGE -> TRANSITION -> EVENT).

Inasoma data/processed/state/symbol=<P>/tf=<TF>.parquet (state engine kwanza).
Output:
  data/processed/state_context/symbol=<P>/tf=<TF>.parquet
    cols: ts, <dim>_state, <dim>_age, <dim>_pchange   (dim = vol/act/spr)
  reports/state_context_report.md
Endesha: python src/research/state_context_engine.py
Self-test: python src/research/state_context_engine.py --self-test
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
DIMS = [("vol", "volatility_state"), ("act", "activity_state"), ("spr", "spread_state")]
BUCKETS = [(1, 3), (4, 8), (9, 15), (16, 10**9)]
BLABEL = ["1-3", "4-8", "9-15", "16+"]
MIN_OBS = 20         # samples za chini kwa (state,bucket) kabla ya kutoa pchange


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


def context_for_dim(states):
    """ONLINE (no-lookahead): rudisha (age[], pchange[]).
    pchange[i] = P(change | state_i, bucket_i) kutoka transitions za NYUMA tu."""
    n = len(states)
    age = np.zeros(n, dtype=int)
    pchg = np.full(n, np.nan)
    counts = {}                       # (state, bucket) -> [changes, total]
    prev = None; a = 0
    for i in range(n):
        cur = states[i]
        if cur == "UNKNOWN":
            prev = None; a = 0; continue
        a = a + 1 if cur == prev else 1
        prev = cur; age[i] = a
        key = (cur, _bidx(a))
        c = counts.get(key)
        if c and c[1] >= MIN_OBS:
            pchg[i] = c[0] / c[1]      # makisio ya NYUMA (kabla ya kusasisha)
        # observe i->i+1 (sasisha BAADA ya kuweka pchg[i] => no-lookahead)
        if i + 1 < n and states[i + 1] != "UNKNOWN":
            changed = 1 if states[i + 1] != cur else 0
            counts.setdefault(key, [0, 0])
            counts[key][0] += changed; counts[key][1] += 1
    return age, pchg


def build(df: pl.DataFrame) -> pl.DataFrame:
    out = {"ts": df["ts"]}
    for short, col in DIMS:
        states = df[col].to_list()
        age, pchg = context_for_dim(states)
        out[f"{short}_state"] = states
        out[f"{short}_age"] = age
        out[f"{short}_pchange"] = pchg
    return pl.DataFrame(out)


def _hazard_by_bucket(age, pchg):
    """mean pchange kwa age bucket (sanity: inapaswa kupanda na umri kama state_age)."""
    out = []
    for lo, hi in BUCKETS:
        m = (age >= lo) & (age <= hi) & np.isfinite(pchg)
        out.append(float(np.mean(pchg[m])) if m.any() else float("nan"))
    return out


def run(pairs, tfs):
    c = cfg(); miss = []; rows = []
    for sym in pairs:
        for tf in tfs:
            p = state_path(sym, tf)
            if not p.exists():
                miss.append(f"{sym}/{tf}"); continue
            df = pl.read_parquet(p)
            ctx = build(df)
            out = REPO_ROOT / c["paths"]["processed"] / "state_context" / f"symbol={sym}" / f"tf={tf}.parquet"
            out.parent.mkdir(parents=True, exist_ok=True)
            ctx.write_parquet(out)
            cov = {}
            haz = {}
            for short, _ in DIMS:
                a = ctx[f"{short}_age"].to_numpy(); pc = ctx[f"{short}_pchange"].to_numpy()
                cov[short] = float(np.isfinite(pc).mean())
                haz[short] = _hazard_by_bucket(a, pc)
            rows.append((sym, tf, len(ctx), cov, haz))
            print(f"  {sym}/{tf}: bars={len(ctx)} cov(vol/act/spr)="
                  f"{cov['vol']*100:.0f}/{cov['act']*100:.0f}/{cov['spr']*100:.0f}%")
    if not rows:
        print("HITILAFU: hakuna state parquet. Endesha market_state_engine.py kwanza.\n"
              f"  Zilizokosekana: {', '.join(miss[:8])}{'...' if len(miss)>8 else ''}", file=sys.stderr)
        return 1

    L = ["# State Context Engine — output (Phase 1.7, CQ-012)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | per-bar: state + state_age + P(change|state,age) | "
         "online no-lookahead | chanzo: state series*\n",
         "> Context = { state, age, transition_probability }. pchange imekadiriwa kutoka transitions "
         "za NYUMA tu (online). Hii ndiyo layer ya doctrine V5.1: STATE -> STATE AGE -> TRANSITION.\n",
         "## Coverage (% bars zenye pchange halali) + hazard kwa age (mean pchange)\n",
         "| Pair | TF | bars | cov vol/act/spr | vol haz 1-3→16+ | act haz 1-3→16+ | spr haz 1-3→16+ |",
         "|------|----|------|-----------------|-----------------|-----------------|-----------------|"]
    for sym, tf, n, cov, haz in rows:
        def hz(h): return f"{h[0]*100:.0f}→{h[3]*100:.0f}" if (h[0]==h[0] and h[3]==h[3]) else "—"
        L.append(f"| {sym} | {tf} | {n:,} | "
                 f"{cov['vol']*100:.0f}/{cov['act']*100:.0f}/{cov['spr']*100:.0f}% | "
                 f"{hz(haz['vol'])} | {hz(haz['act'])} | {hz(haz['spr'])} |")
    if miss:
        L.append(f"\n*Hazikupatikana: {len(miss)} pair×TF.*")
    L.append("\n---\n*State Context Engine = component ya msingi (CQ-012). Output parquet ina "
             "state+age+pchange kwa kila dimension, tayari kwa Event Layer & Triple Barrier. pchange ni "
             "ONLINE no-lookahead. 'haz 1-3→16+' inaonyesha P(change) inavyobadilika na umri (linganisha "
             "na state_age_report). Inayofuata (Phase 1.8): state_transition_model (P(next|state) vs "
             "P(next|state,age), LogLoss/Brier). Metric = EV (CQ-008).*")
    out = REPO_ROOT / c["paths"]["reports"] / "state_context_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """(1) no-lookahead (NaN mwanzoni); (2) geometric -> pchange ~0.2 flat;
       (3) age-dependent (duration 8) -> hazard inapanda na umri."""
    # geometric p_change=0.2
    rng = np.random.default_rng(0); geo = []; cur = "A"
    for _ in range(60000):
        geo.append(cur)
        if rng.random() < 0.2:
            cur = "B" if cur == "A" else "A"
    age, pc = context_for_dim(geo)
    early_nan = np.isnan(pc[:30]).any()
    haz_g = _hazard_by_bucket(age, pc)
    geo_flat = (max([x for x in haz_g if x==x]) - min([x for x in haz_g if x==x])) < 0.08
    # deterministic duration 8
    det = []
    for k in range(2000):
        det += [("A" if k % 2 == 0 else "B")] * 8
    age2, pc2 = context_for_dim(det)
    haz_d = _hazard_by_bucket(age2, pc2)
    det_rising = (haz_d[1] > haz_d[0])      # bucket 4-8 (ina age 8 inayobadilika) > 1-3 (~0)
    print(f"geometric hazard by bucket: {[round(x,2) for x in haz_g]} (tarajio ~0.2 flat)")
    print(f"deterministic(8) hazard:    {[round(x,2) for x in haz_d]} (1-3 chini, 4-8 juu)")
    print(f"no-lookahead (NaN early)={early_nan}")
    ok = early_nan and geo_flat and det_rising
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
