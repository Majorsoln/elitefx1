"""
state_half_life.py — PHASE 1 (Chief Priority 2). State duration / half-life.

Swali: HIGH_VOL inaishi bars ngapi kabla ya kubadilika? Hii ndiyo msingi wa
VERTICAL BARRIER ya Triple Barrier — bila hii hatujui 5/10/20 bars ipi sahihi.

Kwa kila dimension/state/pair/TF tunapima RUN LENGTH (bars mfululizo ndani ya
state ileile):
  median | p75 | p90 | mean | n_runs

Inasoma data/processed/state/symbol=<P>/tf=<TF>.parquet (endesha state engine kwanza).
Output: reports/state_half_life_report.md
Endesha: python src/research/state_half_life.py
Self-test: python src/research/state_half_life.py --self-test
"""
from __future__ import annotations

import argparse, sys
from collections import defaultdict
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


def cfg():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)

def state_path(sym, tf):
    return REPO_ROOT / cfg()["paths"]["processed"] / "state" / f"symbol={sym}" / f"tf={tf}.parquet"


def run_lengths(states):
    """Rudisha {state: [run lengths]}. UNKNOWN inakata run (haijumuishwi)."""
    out = defaultdict(list); cur = None; ln = 0
    for x in states:
        if x == "UNKNOWN":
            if cur is not None:
                out[cur].append(ln)
            cur = None; ln = 0; continue
        if x == cur:
            ln += 1
        else:
            if cur is not None:
                out[cur].append(ln)
            cur = x; ln = 1
    if cur is not None:
        out[cur].append(ln)
    return out


def stats(runs):
    if not runs:
        return None
    a = np.array(runs)
    return dict(med=float(np.median(a)), p75=float(np.percentile(a, 75)),
                p90=float(np.percentile(a, 90)), mean=float(a.mean()), n=len(a))


def run(pairs, tfs):
    miss = []; data = {d[0]: [] for d in DIMS}
    for sym in pairs:
        for tf in tfs:
            p = state_path(sym, tf)
            if not p.exists():
                miss.append(f"{sym}/{tf}"); continue
            df = pl.read_parquet(p)
            for dim, levels, col in DIMS:
                rl = run_lengths(df[col].to_list())
                data[dim].append((sym, tf, {lv: stats(rl.get(lv, [])) for lv in levels}, levels))
    if all(len(v) == 0 for v in data.values()):
        print("HITILAFU: hakuna state parquet. Endesha market_state_engine.py kwanza.\n"
              f"  Zilizokosekana: {', '.join(miss[:8])}{'...' if len(miss)>8 else ''}", file=sys.stderr)
        return 1

    L = ["# State Half-Life Report — duration (Phase 1, Chief Priority 2)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | run length (bars mfululizo) kwa state | "
         "median/p75/p90/mean | msingi wa VERTICAL BARRIER*\n",
         "> 'HIGH_VOL inaishi bars ngapi?' median = muda wa kawaida; p90 = mkia. Vertical barrier "
         "(Triple Barrier) iendane na duration HII, sio nambari ya kubahatisha (5/10/20).\n"]
    for dim, levels, _ in DIMS:
        L.append(f"\n## {dim.upper()} — run length (bars)\n")
        cols = " | ".join(f"{lv} med/p90" for lv in levels)
        L.append(f"| Pair | TF | {cols} |")
        L.append("|------|----|" + "----|" * len(levels))
        for sym, tf, st, lv in data[dim]:
            cells = []
            for level in lv:
                s = st[level]
                cells.append(f"{s['med']:.0f}/{s['p90']:.0f}" if s else "—")
            L.append(f"| {sym} | {tf} | " + " | ".join(cells) + " |")
    if miss:
        L.append(f"\n*Hazikupatikana (endesha state engine): {len(miss)} pair×TF.*")
    L.append("\n---\n*Run length = bars mfululizo ndani ya state. median = vertical barrier ya msingi; "
             "p90 = mkia (state inavyoweza kudumu). Hii inajibu swali la Triple Barrier vertical "
             "barrier moja kwa moja. Inayofuata: volume_bars -> Event Diagnostics. Metric = EV.*")
    out = REPO_ROOT / cfg()["paths"]["reports"] / "state_half_life_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"Ripoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """Runs zinazojulikana: HIGH ina runs za 5; LOW za 10."""
    seq = (["LOW"]*10 + ["NORMAL"]*3 + ["HIGH"]*5 + ["NORMAL"]*2) * 40
    rl = run_lengths(seq)
    sL = stats(rl["LOW"]); sH = stats(rl["HIGH"])
    print(f"LOW median={sL['med']} (tarajio 10) | HIGH median={sH['med']} (tarajio 5) | n_HIGH={sH['n']}")
    # UNKNOWN inakata run
    rl2 = run_lengths(["HIGH","HIGH","UNKNOWN","HIGH","HIGH","HIGH"])
    print(f"UNKNOWN-split HIGH runs: {sorted(rl2['HIGH'])} (tarajio [2,3])")
    ok = (sL["med"] == 10 and sH["med"] == 5 and sorted(rl2["HIGH"]) == [2, 3])
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
