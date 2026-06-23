"""
state_transition_model.py — PHASE 1.8. Je AGE inaongeza predictive power?

State Context ni descriptive (current state/age/pchange). Hii inajaribu kama
KUONGEZA AGE kunaboresha UTABIRI wa next_state:

  Model A:  P(next_state | state)
  Model B:  P(next_state | state, age-bucket)

Tathmini: ONLINE PREQUENTIAL (no-lookahead) — kila bar inatabiriwa kwa counts
za NYUMA tu, kisha next_state halisi inascoriwa, kisha counts zinasasishwa.
Bars zinascoriwa pale models ZOTE MBILI zina sample ya kutosha (linganisho la haki).

Metrics: LogLoss · Brier (multiclass) · Accuracy · ECE (calibration).
  Δ = A − B. Δ > 0 (B chini) => AGE inaboresha utabiri.

Laplace smoothing (alpha) kuepuka log(0). Inasoma state parquet (state engine).
Output: reports/state_transition_model_report.md
Endesha: python src/research/state_transition_model.py
Self-test: python src/research/state_transition_model.py --self-test
"""
from __future__ import annotations

import argparse, sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np
import polars as pl
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config" / "data_config.yaml"
TFS = ["H1", "H2", "H4", "D1"]
DIMS = [("volatility", ["LOW","NORMAL","HIGH"], "volatility_state"),
        ("activity",   ["LOW","NORMAL","HIGH"], "activity_state"),
        ("spread",     ["NORMAL","WIDE"],       "spread_state")]
BUCKETS = [(1, 3), (4, 8), (9, 15), (16, 10**9)]
ALPHA = 0.5        # Laplace smoothing
MIN_OBS = 30       # sample ya chini kabla ya kuscore (kwa model zote mbili)


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


def _smooth(counter, classes):
    tot = sum(counter.values())
    K = len(classes)
    return np.array([(counter.get(c, 0) + ALPHA) / (tot + ALPHA * K) for c in classes])


def evaluate(states, classes):
    """ONLINE prequential: rudisha metrics za Model A na B (na n_scored)."""
    cidx = {c: i for i, c in enumerate(classes)}
    cA = {}; cB = {}
    accA = dict(ll=0.0, br=0.0, acc=0, conf=[], corr=[]); accB = dict(ll=0.0, br=0.0, acc=0, conf=[], corr=[])
    n = 0; prev = None; age = 0
    for i in range(len(states) - 1):
        cur = states[i]; nxt = states[i + 1]
        if cur == "UNKNOWN":
            prev = None; age = 0; continue
        age = age + 1 if cur == prev else 1
        prev = cur
        if nxt == "UNKNOWN" or nxt not in cidx or cur not in cidx:
            continue
        keyB = (cur, _bidx(age))
        gA = cA.get(cur); gB = cB.get(keyB)
        if gA and gB and sum(gA.values()) >= MIN_OBS and sum(gB.values()) >= MIN_OBS:
            pA = _smooth(gA, classes); pB = _smooth(gB, classes)
            j = cidx[nxt]
            for p, acc in ((pA, accA), (pB, accB)):
                p = np.clip(p, 1e-12, 1.0)
                acc["ll"] += -np.log(p[j])
                acc["br"] += float(np.sum((p - np.eye(len(classes))[j]) ** 2))
                pred = int(np.argmax(p))
                acc["acc"] += int(pred == j)
                acc["conf"].append(float(p[pred])); acc["corr"].append(int(pred == j))
            n += 1
        cA.setdefault(cur, Counter())[nxt] += 1
        cB.setdefault(keyB, Counter())[nxt] += 1
    if n == 0:
        return None
    def fin(acc):
        return dict(ll=acc["ll"]/n, br=acc["br"]/n, acc=acc["acc"]/n,
                    ece=_ece(acc["conf"], acc["corr"]))
    return dict(n=n, A=fin(accA), B=fin(accB))


def _ece(conf, corr, bins=10):
    if not conf:
        return float("nan")
    conf = np.array(conf); corr = np.array(corr); n = len(conf); e = 0.0
    for b in range(bins):
        lo, hi = b/bins, (b+1)/bins
        m = (conf > lo) & (conf <= hi) if b > 0 else (conf >= lo) & (conf <= hi)
        if m.any():
            e += m.sum()/n * abs(conf[m].mean() - corr[m].mean())
    return float(e)


def run(pairs, tfs):
    miss = []; res = {d[0]: [] for d in DIMS}
    for sym in pairs:
        for tf in tfs:
            p = state_path(sym, tf)
            if not p.exists():
                miss.append(f"{sym}/{tf}"); continue
            df = pl.read_parquet(p)
            for dim, classes, col in DIMS:
                m = evaluate(df[col].to_list(), classes)
                if m:
                    res[dim].append((sym, tf, m))
    if all(len(v) == 0 for v in res.values()):
        print("HITILAFU: hakuna state parquet. Endesha market_state_engine.py kwanza.\n"
              f"  Zilizokosekana: {', '.join(miss[:8])}{'...' if len(miss)>8 else ''}", file=sys.stderr)
        return 1

    L = ["# State Transition Model — je AGE inaboresha utabiri? (Phase 1.8)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | Model A: P(next|state) vs Model B: P(next|state,age) | "
         f"ONLINE prequential (no-lookahead) | Laplace α={ALPHA}, min={MIN_OBS}*\n",
         "> Δ = A − B. LogLoss/Brier/ECE: chini ni bora -> Δ>0 = AGE inaboresha. Accuracy: juu ni bora.\n"]
    for dim, classes, _ in DIMS:
        L.append(f"\n## {dim.upper()}\n")
        L.append("| Pair | TF | n | LogLoss A→B | ΔLL% | Brier A→B | Acc A→B | ECE A→B | age helps? |")
        L.append("|------|----|---|-------------|------|-----------|---------|---------|------------|")
        for sym, tf, m in res[dim]:
            A, B = m["A"], m["B"]
            dll = (A["ll"] - B["ll"]) / A["ll"] * 100 if A["ll"] else 0
            helps = "✅" if (B["ll"] < A["ll"] and B["br"] <= A["br"]) else "—"
            L.append(f"| {sym} | {tf} | {m['n']:,} | {A['ll']:.3f}→{B['ll']:.3f} | {dll:+.1f} | "
                     f"{A['br']:.3f}→{B['br']:.3f} | {A['acc']*100:.0f}→{B['acc']*100:.0f}% | "
                     f"{A['ece']:.3f}→{B['ece']:.3f} | {helps} |")

    L.append("\n## Muhtasari — H-01: je AGE inaongeza predictive power?\n")
    for dim, _, _ in DIMS:
        dlls = [(m["A"]["ll"]-m["B"]["ll"])/m["A"]["ll"]*100 for _,_,m in res[dim] if m["A"]["ll"]]
        if dlls:
            md = float(np.median(dlls))
            verd = "✅ AGE inaboresha" if md > 1 else ("≈ haina tofauti" if md > -1 else "❌ inazidisha kosa")
            L.append(f"- **{dim}**: median ΔLogLoss = {md:+.1f}% → {verd}")
    L.append("\n*H-01 (doctrine Finding F): Activity ndiyo dimension yenye taarifa nyingi zaidi? "
             "Linganisha ΔLogLoss ya activity vs volatility hapo juu.*")
    if miss:
        L.append(f"\n*Hazikupatikana: {len(miss)} pair×TF.*")
    L.append("\n---\n*Online prequential = no-lookahead, no arbitrary split. Δ>0 (LogLoss/Brier chini "
             "kwa B) = age ina predictive value -> doctrine V5.1 (STATE AGE -> TRANSITION) imethibitishwa "
             "kwa utabiri, sio descriptive tu. Metric = EV (CQ-008) kwenye phases zijazo.*")
    out = REPO_ROOT / cfg()["paths"]["reports"] / "state_transition_model_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"Ripoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """(1) age-dependent (duration 6) -> Model B << Model A (logloss).
       (2) geometric (memoryless) -> B ≈ A."""
    classes = ["A", "B"]
    # (1) kila run = bars 6 (mabadiliko yanategemea AGE) -> age inatabiri vyema
    dep = []
    for k in range(3000):
        dep += [("A" if k % 2 == 0 else "B")] * 6
    m1 = evaluate(dep, classes)
    # (2) geometric p_change=0.2 (memoryless)
    rng = np.random.default_rng(0); geo = []; cur = "A"
    for _ in range(60000):
        geo.append(cur)
        if rng.random() < 0.2:
            cur = "B" if cur == "A" else "A"
    m2 = evaluate(geo, classes)
    print(f"age-dep: LogLoss A={m1['A']['ll']:.3f} B={m1['B']['ll']:.3f} "
          f"(B bora kwa maana? {m1['B']['ll'] < m1['A']['ll']*0.85})")
    print(f"geometric: LogLoss A={m2['A']['ll']:.3f} B={m2['B']['ll']:.3f} "
          f"(B ≈ A? {abs(m2['A']['ll']-m2['B']['ll'])/m2['A']['ll'] < 0.05})")
    ok = (m1["B"]["ll"] < m1["A"]["ll"] * 0.85
          and abs(m2["A"]["ll"] - m2["B"]["ll"]) / m2["A"]["ll"] < 0.05)
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
