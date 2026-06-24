"""
volume_information.py — PHASE 2.1 (Chief Quant approved, NO ML). Information value.

Phase 2 (`adaptive_volume_bar_report.md`) ilithibitisha: volume bars HAZITOI
state distributions thabiti zaidi kuliko calendar (R-002, 0/9). Lakini Chief:

    Volume bars hazijastabilize states.
    Lakini je zinaongeza INFORMATION?

Hii inajaribu hilo MOJA KWA MOJA — Calendar (H1) vs adaptive Volume bars — kwa
taarifa NNE (definition ileile ya state kwa zote: ATR/activity terciles):

  1. State persistence      : wastani run length (bars mfululizo katika state).
  2. State age effect        : Δ P(stay) = P(stay)@16+ − P(stay)@1-3 (duration info).
  3. Transition predictability: Model B LogLoss/accuracy (P(next|state,age)) —
                                CHINI/JUU = bora (reuse state_transition_model).
  4. Context value           : EV uplift ya Event+Context vs Event alone (Trend
                                Pullback, GROSS/cost-neutral ili kutenga taarifa).

VERDICT: volume bars zikishinda kwenye predictability NA/AU context value
(taarifa zenye thamani ya trading) -> zina INFORMATION zaidi licha ya kukosa
stability. NO ML, NO entries (Chief). Information comparison, sio tradability.

Reuse: adaptive_volume_bars (bars+label), market_state_engine, state_age,
state_half_life, state_transition_model, context_value, state_context_engine.

Output: reports/volume_information_report.md
Endesha: python src/data/volume_information.py
         python src/data/volume_information.py --symbol EURGBP
Self-test: python src/data/volume_information.py --self-test
"""
from __future__ import annotations

import argparse, sys
from datetime import datetime
from pathlib import Path

import numpy as np
import polars as pl
import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "research"))
from market_state_engine import h1_from_ticks, time_col, pip
from volume_bars import m1_from_ticks
from state_age import age_hazard, pstay
from state_half_life import run_lengths
from state_transition_model import evaluate as tm_evaluate
from context_value import pullback_signals, event_records, prequential_value
from state_context_engine import context_for_dim
from adaptive_volume_bars import build_volume_bars, label_states, cfg

REPO_ROOT = Path(__file__).resolve().parents[2]
DIMS2 = [("volatility", "volatility_state"), ("activity", "activity_state")]
CLASSES = ["LOW", "NORMAL", "HIGH"]
_posix = lambda p: str(p).replace("\\", "/")


def persistence(states):
    """Wastani run length (bars mfululizo katika state ileile)."""
    rl = run_lengths(states)
    runs = [x for v in rl.values() for x in v]
    return float(np.mean(runs)) if runs else float("nan")


def age_effect(states):
    """Δ P(stay) = P(stay)@16+ − P(stay)@1-3 (duration-dependence info)."""
    ps = pstay(age_hazard(states))
    return (ps[3] - ps[0]) if (ps[0] == ps[0] and ps[3] == ps[3]) else float("nan")


def predictability(states):
    """Model B (P(next|state,age)) LogLoss + accuracy. Chini LogLoss = predictable zaidi."""
    m = tm_evaluate(states, CLASSES)
    if not m:
        return float("nan"), float("nan")
    return m["B"]["ll"], m["B"]["acc"]


def context_uplift(df, col, pp):
    """EV uplift (GROSS, spr=0) ya Event+Context vs Event alone kwa dimension moja."""
    close = df["c"].to_numpy() / pp
    high = df["h"].to_numpy() / pp
    low = df["l"].to_numpy() / pp
    atr_pips = df["atr"].to_numpy() / pp
    spr0 = np.zeros(len(close))                       # cost-neutral: tenga taarifa
    sig = pullback_signals(close, high, low)
    states = df[col].to_list()
    age, _ = context_for_dim(states)
    idx, nets, wins, rmults, hits, abk = event_records(close, spr0, atr_pips, sig, age)
    if len(nets) == 0:
        return float("nan")
    skeys = [states[i] for i in idx]
    m = prequential_value(skeys, abk, nets, wins, rmults, hits)
    a, b = m["A"], m["B"]
    return (b["ev"] - a["ev"]) if (a["ev"] == a["ev"] and b["ev"] == b["ev"]) else float("nan")


def analyze_pair(con, src, t, pp):
    """Jenga calendar + volume bars, label, rudisha (cal_metrics, vol_metrics)."""
    h1 = h1_from_ticks(con, src, t, pp).rename({"tc": "act"})
    cal = label_states(h1.select(["ts", "h", "l", "c", "act"]))
    vb = label_states(build_volume_bars(m1_from_ticks(con, src, t)))
    return _metrics(cal, pp), _metrics(vb, pp)


def _metrics(df, pp):
    out = {}
    for dim, col in DIMS2:
        states = df[col].to_list()
        ll, acc = predictability(states)
        out[dim] = dict(persist=persistence(states), age=age_effect(states),
                        ll=ll, acc=acc, ctx=context_uplift(df, col, pp))
    return out


def run(pairs):
    c = cfg(); raw = REPO_ROOT / c["paths"]["raw_ticks"]
    if not raw.exists():
        print(f"HITILAFU: '{raw}' haipo.", file=sys.stderr); return 1
    con = duckdb.connect(); rows = []
    for sym in pairs:
        base = raw / f"symbol={sym}"
        if not base.exists() or not list(base.rglob("*.parquet")):
            print(f"  {sym}: (hakuna data)"); continue
        src = _posix(base / "**" / "*.parquet")
        t = time_col(con, src); pp = pip(sym)
        print(f"  {sym}: nascan (calendar + volume)...", flush=True)
        cal, vb = analyze_pair(con, src, t, pp)
        rows.append((sym, cal, vb))
        print(f"    done")
    if not rows:
        print("HITILAFU: hakuna data.", file=sys.stderr); return 1

    L = ["# Volume Information Value — je volume bars zina TAARIFA zaidi? (Phase 2.1)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | Calendar (H1) vs adaptive Volume bars | metrics: persistence · "
         "age effect (ΔP(stay)) · transition predictability (Model B LogLoss/acc) · context value (EV uplift, "
         "GROSS) | definition ya state ileile (terciles)*\n",
         "> **Q-003 (Chief):** Volume bars hazikufanya states stable (R-002). Lakini je zina INFORMATION "
         "zaidi? 'volume+info' = volume inashinda kwenye predictability NA/AU context value (taarifa za "
         "trading). NO ML, GROSS (cost-neutral) ili kutenga taarifa, sio tradability.\n"]
    wins = {d[0]: dict(persist=0, age=0, predict=0, ctx=0) for d in DIMS2}; tot = len(rows)
    info_pairs = {d[0]: 0 for d in DIMS2}
    for dim, _ in DIMS2:
        L.append(f"\n## {dim.upper()} — Calendar (C) vs Volume (V)\n")
        L.append("| Pair | persist C/V | ageΔ C/V | LogLoss C/V | acc C/V | ctxEV C/V | volume+info? |")
        L.append("|------|-------------|----------|-------------|---------|-----------|--------------|")
        for sym, cal, vb in rows:
            cc = cal[dim]; vv = vb[dim]
            w_pred = (vv["ll"] < cc["ll"]) if (vv["ll"] == vv["ll"] and cc["ll"] == cc["ll"]) else False
            w_ctx = (vv["ctx"] > cc["ctx"]) if (vv["ctx"] == vv["ctx"] and cc["ctx"] == cc["ctx"]) else False
            w_age = (abs(vv["age"]) > abs(cc["age"])) if (vv["age"] == vv["age"] and cc["age"] == cc["age"]) else False
            w_per = (vv["persist"] > cc["persist"]) if (vv["persist"] == vv["persist"] and cc["persist"] == cc["persist"]) else False
            wins[dim]["predict"] += w_pred; wins[dim]["ctx"] += w_ctx
            wins[dim]["age"] += w_age; wins[dim]["persist"] += w_per
            info = w_pred or w_ctx                         # taarifa za thamani ya trading
            info_pairs[dim] += 1 if info else 0
            L.append(f"| {sym} | {cc['persist']:.1f}/{vv['persist']:.1f} | "
                     f"{cc['age']*100:+.0f}/{vv['age']*100:+.0f}pp | {cc['ll']:.3f}/{vv['ll']:.3f} | "
                     f"{cc['acc']*100:.0f}/{vv['acc']*100:.0f}% | {cc['ctx']:+.2f}/{vv['ctx']:+.2f} | "
                     f"{'✅' if info else '—'} |")

    L.append("\n## VERDICT — Q-003: je volume bars zinaongeza INFORMATION?\n")
    for dim, _ in DIMS2:
        w = wins[dim]
        L.append(f"- **{dim}**: volume inashinda → predictability {w['predict']}/{tot}, "
                 f"context {w['ctx']}/{tot}, age-effect {w['age']}/{tot}, persistence {w['persist']}/{tot} "
                 f"| info(pred∨ctx) {info_pairs[dim]}/{tot} pairs")
    tot_info = sum(info_pairs.values()); tot_cells = tot * len(DIMS2)
    if tot_info > tot_cells / 2:
        verd = (f"✅ **NDIYO** — volume bars zinaonyesha taarifa zaidi ({tot_info}/{tot_cells} dim×pair "
                "kwa predictability∨context). Volume = alternative representation YENYE thamani -> Chief "
                "aamue hatua inayofuata.")
    else:
        verd = (f"❌ **HAPANA wazi** — volume bars hazikuonyesha taarifa zaidi ({tot_info}/{tot_cells}). "
                "Calendar bars zinatosha; volume bars = representation mbadala bila faida ya taarifa "
                "iliyothibitishwa.")
    L.append(f"\n{verd}")
    L.append("\n*Definition ya state ileile (terciles) kwa Calendar na Volume -> linganisho la haki. "
             "Context value ni GROSS (cost-neutral) ili kupima TAARIFA, sio tradability. NO ML (Chief). "
             "Verdict hii inajibu Q-003; haifungui ML/Triple Barrier. Metric = EV (net pips kwenye phases "
             "zijazo).*")
    out = REPO_ROOT / c["paths"]["reports"] / "volume_information_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """(1) predictability: deterministic(6) series < random series (LogLoss).
       (2) persistence/age helpers run.  (3) context_uplift kwenye df bandia."""
    # (1) predictable (duration 6) vs random
    det = []
    for k in range(3000):
        det += [CLASSES[k % 3]] * 6
    rng = np.random.default_rng(0)
    rnd = list(rng.choice(CLASSES, 18000))
    ll_det, _ = predictability(det); ll_rnd, _ = predictability(rnd)
    pred_ok = ll_det < ll_rnd
    print(f"predictability: deterministic LL={ll_det:.3f} < random LL={ll_rnd:.3f}  ({pred_ok})")

    # (2) persistence + age effect (runs za bars 20 ili bucket 16+ ijae)
    det20 = []
    for k in range(1500):
        det20 += [CLASSES[k % 3]] * 20
    p_det = persistence(det20); a_det = age_effect(det20)
    helpers_ok = p_det == p_det and a_det == a_det          # vyote finite
    print(f"persistence(det20)={p_det:.1f} | ageΔ(det20)={a_det*100:+.0f}pp  ({helpers_ok})")

    # (3) context_uplift on synthetic df (informative state -> uplift inawezekana)
    n = 6000; close = np.cumsum(rng.normal(0, 0.5, n)) + 1000.0
    vs = rng.choice(CLASSES, n)
    df = pl.DataFrame(dict(c=close, h=close + 0.5, l=close - 0.5, atr=np.full(n, 0.10),
                           volatility_state=vs, activity_state=vs))
    up = context_uplift(df, "volatility_state", 0.0001)
    ctx_ok = up == up                                     # finite (inarun bila error)
    print(f"context_uplift(synthetic)={up:+.2f} finite={ctx_ok}")

    ok = pred_ok and helpers_ok and ctx_ok
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
    return run(pairs)


if __name__ == "__main__":
    raise SystemExit(main())
