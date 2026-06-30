"""
ecology_interaction_engine.py — PHASE 25 (Chief Quant).

Phase 24: F-041 (universal causal primitives) **REJECTED** kwa formulation yake — Compression
haikujitokeza event-free; primitives nyingi ziliishia "Equilibrium/Balanced Flow"; precedence
lifts ≈ 1.0. Chief discovery: primitive **haitabiri** event — inaELEZEA mazingira ambamo event
imetokea. Primitives ni **ecological layer**, parallel na events (sio causal).

  Principle 53: primitives describe the operating ENVIRONMENT of events; hazichukuliwi kuzalisha events.
  Principle 54: primitives ni za **ecological layer**, sio event layer.
  Principle 55: ecological description na event prediction ni malengo tofauti ya kisayansi.
  F-042 (OPEN): primitives characterize ecological conditions, sio universal causal mechanisms.

Architecture mpya: Market Ecology → Primitives → Event Families → Representations.
Swali kuu sasa: layer hizi mbili (Ecology vs Events) zinaINGILIANAje?

Maswali (Chief):
  Q1. Je kila Event ina distribution tofauti ya primitives?
  Q2. Je Event Representation inabadilika kwa Primitive?
  Q3. Je Primitive inaongeza CALIBRATION (sio prediction) kwa Event?
  Q4. Je Primitive inaongeza STABILITY ya Event Representation?
  Q5. Je Primitive inaweza kutumika kama WEIGHTING layer badala ya signal?

Mbinu: kusanya event occurrences + primitive (ecology) + outcome; pima JS-divergence ya
primitive-distributions, r2(feature|primitive), ΔBrier (calibration), fold sign-consistency,
na variance-vs-mean kwa primitive (weighting vs signal). NO ML.

Reuse: market_primitive_validation_engine (fit_primitives, assign_primitives, name_primitives,
TFS, KP), market_state_engine (cfg, pip), latent_structure (state_path), event_library
(EVENTS_ALL), configuration_engine (EVENTS_SET, VERT), context_value (HORIZON),
event_taxonomy_engine (FEAT, VLEVEL, TRAJ_WIN, _runlen, r2_label),
representation_interaction_engine (brier, stability).

Output: reports/ecology_interaction_report.md
Self-test: python src/research/ecology_interaction_engine.py --self-test
"""
from __future__ import annotations

import argparse, sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
import polars as pl

from market_state_engine import cfg, pip
from latent_structure import state_path
from event_library import EVENTS_ALL
from configuration_engine import EVENTS_SET, VERT
from context_value import HORIZON
from event_taxonomy_engine import FEAT, VLEVEL, TRAJ_WIN, _runlen, r2_label
from representation_interaction_engine import brier, stability
from market_primitive_validation_engine import fit_primitives, assign_primitives, name_primitives, TFS, KP

REPO_ROOT = Path(__file__).resolve().parents[2]
MIN_OCC = 200            # min occurrences per event
MIN_BUCKET = 30          # min occurrences per (event,primitive) bucket


def build_ecology(pairs, rng):
    """Rudisha (df occurrences: event,prim,y,FEAT…), primitive info, n_bars."""
    B, occ_pos, occ_evt, occ_y = [], [], [], []
    occ_feat = []
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
            close = df["c"].to_numpy() / pp; high = df["h"].to_numpy() / pp; low = df["l"].to_numpy() / pp
            atr = df["atr"].to_numpy() / pp
            spr = df["spr"].to_numpy(); spr = np.where(np.isfinite(spr), spr, 0.0)
            vol = df["volatility_state"].to_list(); act = df["activity_state"].to_list()
            sprst = df["spread_state"].to_list()
            rl = _runlen(vol); Lv = np.array([VLEVEL.get(v, 1.0) for v in vol])
            n = len(close)
            sig = {e: EVENTS_ALL[e](close, high, low) for e in EVENTS_SET}
            for i in range(n):
                if not (atr[i] > 0):
                    continue
                traj = (1.0 if i >= TRAJ_WIN and Lv[i] > Lv[i - TRAJ_WIN]
                        else -1.0 if i >= TRAJ_WIN and Lv[i] < Lv[i - TRAJ_WIN] else 0.0)
                trans = 1.0 if i >= 1 and vol[i] != vol[i - 1] else 0.0
                fv = [VLEVEL.get(vol[i], 1.0), VLEVEL.get(act[i], 1.0),
                      1.0 if sprst[i] == "WIDE" else 0.0, atr[i], traj, min(rl[i], 30.0), trans]
                pos = len(B); B.append(fv)
                if i + HORIZON >= n or i + VERT >= n:
                    continue
                for e in EVENTS_SET:
                    d = int(sig[e][i])
                    if d != 0:
                        occ_pos.append(pos); occ_evt.append(e)
                        occ_y.append(float(d * (close[i + HORIZON] - close[i]) - spr[i]))
                        occ_feat.append(fv)
        print(f"  {sym}: ecology built", flush=True)
    if no_px or not B:
        return None, None, 0, no_px
    B = np.array(B, float)
    fit = fit_primitives(B, rng)
    prim = assign_primitives(B, fit)
    info = name_primitives(B, prim, fit)
    occ_prim = prim[np.array(occ_pos, np.int64)]
    occ_feat = np.array(occ_feat, float)
    data = {"event": occ_evt,
            "prim": [info[j]["label"] for j in occ_prim],
            "pid": occ_prim.tolist(),
            "y": occ_y}
    for k, name in enumerate(FEAT):
        data[name] = occ_feat[:, k].tolist()
    return pl.DataFrame(data), info, len(B), no_px


# ---------- metrics ----------
def _js(p, q):
    keys = set(p) | set(q)
    pp = np.array([p.get(k, 0.0) for k in keys]); qq = np.array([q.get(k, 0.0) for k in keys])
    m = 0.5 * (pp + qq)
    def kl(a, b):
        mask = a > 0
        return float((a[mask] * np.log2(a[mask] / b[mask])).sum())
    return 0.5 * kl(pp, m) + 0.5 * kl(qq, m)


def q1_distributions(df):
    """Primitive distribution kwa kila event + mean pairwise JS."""
    dist = {}
    for e in df["event"].unique().to_list():
        sub = df.filter(pl.col("event") == e)
        vc = sub["prim"].value_counts()
        tot = sub.height
        dist[e] = {row["prim"]: row["count"] / tot for row in vc.iter_rows(named=True)}
    evs = list(dist)
    js = [ _js(dist[a], dist[b]) for i, a in enumerate(evs) for b in evs[i + 1:] ]
    return dist, (float(np.mean(js)) if js else 0.0)


def q2_repr_change(df):
    """Kwa kila event: mean over FEAT ya r2_label(feature | primitive)."""
    out = {}
    for e in df["event"].unique().to_list():
        sub = df.filter(pl.col("event") == e)
        if sub.height < MIN_OCC:
            continue
        codes = sub["pid"].to_numpy()
        r2s = [r2_label(sub[f].to_numpy().astype(float), codes) for f in FEAT]
        out[e] = float(np.mean(r2s))
    return out


def q3_calibration(df, rng):
    """ΔBrier = brier(base) - brier(+primitive). +ve = primitive inaongeza calibration."""
    out = {}
    for e in df["event"].unique().to_list():
        sub = df.filter(pl.col("event") == e)
        if sub.height < MIN_OCC:
            continue
        b0 = brier(sub, [], rng); b1 = brier(sub, ["prim"], rng)
        out[e] = dict(base=b0, prim=b1, delta=b0 - b1)
    return out


def q4_stability(df, rng):
    """Fold sign-consistency ya (event,primitive) buckets."""
    return stability(df, ["event", "prim"], rng)


def q5_weighting(df):
    """Kwa kila primitive (pooled): mean (signal) na variance (risk). Weighting kama variance
    inatofautiana wakati mean ≈ 0."""
    rows = []
    for pr in df["prim"].unique().to_list():
        sub = df.filter(pl.col("prim") == pr)
        if sub.height < MIN_BUCKET:
            continue
        y = sub["y"].to_numpy()
        rows.append(dict(prim=pr, n=len(y), mean=float(y.mean()), var=float(y.var()),
                         absmean=abs(float(y.mean()))))
    max_abs = max((r["absmean"] for r in rows), default=0.0)
    vars_ = [r["var"] for r in rows]
    vratio = (max(vars_) / min(vars_)) if vars_ and min(vars_) > 1e-12 else 0.0
    return rows, max_abs, vratio


def run(pairs, rng):
    c = cfg()
    print("Building ecology (events × primitives × outcome)...", flush=True)
    df, info, nbars, no_px = build_ecology(pairs, rng)
    if no_px:
        print("HITILAFU: state parquet haina OHLC. Endesha market_state_engine.py kwanza.", file=sys.stderr)
        return 1
    if df is None or df.height < MIN_OCC:
        print("HITILAFU: occurrences hazitoshi.", file=sys.stderr)
        return 1
    print(f"  {df.height:,} occurrences, {nbars:,} bars", flush=True)
    dist, mean_js = q1_distributions(df)
    r2 = q2_repr_change(df)
    cal = q3_calibration(df, rng)
    stab, stab_n = q4_stability(df, rng)
    wrows, max_abs, vratio = q5_weighting(df)
    return _report(c, pairs, df, info, dist, mean_js, r2, cal, stab, stab_n, wrows, max_abs, vratio)


def _report(c, pairs, df, info, dist, mean_js, r2, cal, stab, stab_n, wrows, max_abs, vratio):
    events = sorted(dist)
    L = ["# Ecology Interaction Framework — ecology vs events zinaingilianaje? (Phase 25)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | {len(pairs)} pairs, {df.height:,} event-occurrences | "
         f"primitives = ecological layer (global) | calibration not prediction | NO ML*\n",
         "> **Principle 53 (Chief):** primitives zinaelezea ENVIRONMENT ya events, hazizalishi events. "
         "**Principle 54:** primitives ni ecological layer, sio event layer. **Principle 55:** ecological "
         "description vs event prediction ni malengo tofauti. **F-041 REJECTED** (universal causal primitives); "
         "**F-042 OPEN** (primitives = ecological conditions). NO ML."]

    # Q1
    L.append("\n## Q1 — Je kila Event ina distribution tofauti ya primitives?\n")
    L.append("| event | top primitive | share | #primitives |")
    L.append("|-------|---------------|-------|-------------|")
    for e in events:
        top = max(dist[e].items(), key=lambda kv: kv[1])
        L.append(f"| {e} | {top[0]} | {top[1]:.0%} | {len(dist[e])} |")
    L.append(f"\n- mean pairwise **JS divergence** kati ya events = **{mean_js:.3f}** "
             f"({'✅ events zina ecology tofauti' if mean_js >= 0.05 else '— events zinashiriki ecology inayofanana'}).")

    # Q2
    L.append("\n## Q2 — Je Event Representation inabadilika kwa Primitive?\n")
    L.append("| event | mean R²(feature \\| primitive) |")
    L.append("|-------|------------------------------|")
    for e in sorted(r2, key=lambda x: -r2[x]):
        L.append(f"| {e} | {r2[e]:.3f} |")
    mean_r2 = float(np.mean(list(r2.values()))) if r2 else 0.0
    L.append(f"\n- mean = **{mean_r2:.3f}** ({'✅ representation inabadilika kwa primitive' if mean_r2 >= 0.10 else '— primitive haibadili representation ya event sana'}).")

    # Q3
    L.append("\n## Q3 — Je Primitive inaongeza CALIBRATION (sio prediction)?\n")
    L.append("| event | Brier(base) | Brier(+primitive) | ΔBrier |")
    L.append("|-------|-------------|-------------------|--------|")
    deltas = []
    for e in sorted(cal, key=lambda x: -cal[x]["delta"]):
        m = cal[e]; deltas.append(m["delta"])
        L.append(f"| {e} | {m['base']:.4f} | {m['prim']:.4f} | {m['delta']:+.4f}{' ✅' if m['delta'] > 0.0005 else ''} |")
    mean_delta = float(np.mean(deltas)) if deltas else 0.0
    n_improve = sum(1 for d in deltas if d > 0.0005)
    L.append(f"\n- mean ΔBrier = **{mean_delta:+.4f}**, events zilizoboreshwa: **{n_improve}/{len(deltas)}** "
             f"({'✅ primitive inaongeza calibration' if mean_delta > 0.0005 else '— primitive haiongezi calibration'}). "
             "*(calibration ya probability, SIO directional prediction.)*")

    # Q4
    L.append("\n## Q4 — Je Primitive inaongeza STABILITY ya Event Representation?\n")
    L.append(f"- (event,primitive) buckets zenye EV-sign consistent across folds: **{stab:.0%}** "
             f"(kati ya buckets {stab_n})")
    L.append(f"\n→ {'✅ ecological buckets ni stable (primitive ni conditioning layer thabiti)' if (stab == stab or 0) and stab >= 0.6 else '⚠️ ecological buckets si stable sana across time'}.")

    # Q5
    L.append("\n## Q5 — Je Primitive ni WEIGHTING layer (sio signal)?\n")
    L.append("| primitive | N | mean outcome (signal) | variance (risk) |")
    L.append("|-----------|---|-----------------------|-----------------|")
    for r in sorted(wrows, key=lambda x: -x["var"]):
        L.append(f"| {r['prim']} | {r['n']:,} | {r['mean']:+.3f} | {r['var']:.3f} |")
    L.append(f"\n- max |mean outcome| = **{max_abs:.3f}** (ndogo = SIO signal), variance ratio max/min = "
             f"**{vratio:.2f}** (kubwa = primitive inatofautisha RISK).")
    q5 = vratio >= 1.5 and max_abs < 1.0
    L.append(f"\n→ {'✅ primitive inafaa kama WEIGHTING/risk layer (variance inatofautiana, mean ≈ 0 — sio signal)' if q5 else '⚠️ primitive haitoi weighting wala signal wazi'}.")

    # VERDICT
    L.append("\n## VERDICT — Phase 25 Ecology Interaction Framework\n")
    interacts = (mean_js >= 0.05) and (mean_r2 >= 0.10 or mean_delta > 0.0005 or (stab == stab and stab >= 0.6))
    if interacts and q5:
        L.append("→ ✅ **ecology (primitives) NA events zinaingiliana kama LAYERS PARALLEL**: kila event ina "
                 "ecology tofauti (Q1), representation inabadilika/inacalibrate kwa primitive (Q2/Q3), buckets "
                 "ni stable (Q4), na primitive inafaa kama **weighting/risk layer, SIO signal** (Q5). **F-042 "
                 "inaungwa mkono** (ecological conditions, sio causal mechanism). Inayofuata: tumia primitive "
                 "kama weighting/calibration layer kwenye Reality Validation — SIO signal. NO ML bado.")
    elif interacts:
        L.append("→ 🟡 **ecology inaingiliana na events (Q1–Q4) lakini matumizi kama weighting hayajawa wazi "
                 "(Q5)**: primitive ni conditioning/calibration layer, bado si risk-weighting thabiti. F-042 "
                 "partial. NO ML.")
    else:
        L.append("→ ⚠️ **mwingiliano dhaifu**: ecology na events hazionyeshi interaction thabiti kwa vigezo "
                 "vilivyowekwa. F-042 haijaungwa mkono kikamilifu; representation/primitive bora zinahitajika.")
    L.append("\n**Bado Market Understanding Era — NO alpha.** Primitive ni calibration/weighting layer "
             "(Principle 53/55), SIO signal; mwingiliano si edge.")

    # HONEST CAVEATS
    L.append("\n## Honest Caveats\n")
    L.append("1. **Calibration ≠ alpha (Principle 40/55).** ΔBrier>0 inamaanisha probability iliyo-calibrated "
             "vizuri zaidi kwa ecological bucket — SIO directional edge wala faida baada ya gharama.")
    L.append("2. **r2(feature|primitive) inaweza kuwa juu kwa sababu primitive imejengwa kutoka features zile "
             "zile** (vol/act/spr…). Hii ni mechanical overlap kiasi, sio lazima 'representation change' ya kweli "
             "— Q2 ni dalili dhaifu kuliko Q3/Q4.")
    L.append("3. **JS-divergence (Q1) haisemi SABABU** — events zinaweza kuwa na ecology tofauti kwa sababu ya "
             "definition zao za feature, sio kwa sababu ecology 'inaendesha' event (Principle 53).")
    L.append("4. **Variance differences (Q5) zinaweza kutoka sample size / non-stationarity**, sio risk-structure "
             "halisi; weighting-layer ni hypothesis ya kujaribu prospectively, sio uthibitisho.")
    L.append("5. **F-042 ni reframing, sio ushindi** — tunasema primitives ni ecological description; bado "
             "hatujathibitisha ina thamani yoyote ya kibiashara (Principle 19: hakuna finding bila decision value).")

    L.append("\n*Event occurrences × global primitives × outcome; JS-divergence; r2(feature|primitive); ΔBrier; "
             "fold sign-consistency; variance-vs-mean per primitive. Principle 53/54/55. F-042 OPEN. NO ML. "
             "Profitable ≠ Tradable Edge.*")

    out = REPO_ROOT / c["paths"]["reports"] / "ecology_interaction_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)} (JS {mean_js:.3f}, R² {mean_r2:.3f}, "
          f"ΔBrier {mean_delta:+.4f}, stab {stab:.2f}, vratio {vratio:.2f})")
    return 0


def self_test():
    rng = np.random.default_rng(25)
    # df ya bandia: events 2 zenye primitive-distributions tofauti; ndani ya event,
    # primitive inabadili feature + win-rate + variance; mean ≈ 0 (weighting, sio signal).
    rows = []
    def add(event, prim, vol, n, win_p, spread):
        for _ in range(n):
            y = (1 if rng.random() < win_p else -1) * abs(rng.normal(0, spread))
            rows.append(dict(event=event, prim=prim, pid=0 if prim == "Compression" else 1,
                             y=float(y), vol=vol + rng.normal(0, 0.02), act=1.0, spr=0.0,
                             atr=0.1, traj=0.0, age=5.0, trans=0.0))
    # event A: mostly Compression; event B: mostly Expansion -> Q1 divergence
    add("A", "Compression", 0.0, 500, 0.50, 0.5)
    add("A", "Expansion", 2.0, 100, 0.50, 1.5)
    add("B", "Compression", 0.0, 100, 0.50, 0.5)
    add("B", "Expansion", 2.0, 500, 0.50, 1.5)
    df = pl.DataFrame(rows)
    # fix pid per prim
    df = df.with_columns((pl.col("prim") == "Expansion").cast(pl.Int64).alias("pid"))

    dist, mean_js = q1_distributions(df)
    ok_q1 = mean_js >= 0.05
    print(f"Q1 mean JS = {mean_js:.3f} -> {'OK' if ok_q1 else 'FAIL'}")

    r2 = q2_repr_change(df)
    ok_q2 = np.mean(list(r2.values())) >= 0.10
    print(f"Q2 mean R²(feat|prim) = {np.mean(list(r2.values())):.3f} -> {'OK' if ok_q2 else 'FAIL'}")

    rows2, max_abs, vratio = q5_weighting(df)
    ok_q5 = vratio >= 1.5 and max_abs < 1.0
    print(f"Q5 vratio = {vratio:.2f}, max|mean| = {max_abs:.3f} -> {'OK' if ok_q5 else 'FAIL'}")

    # Q3/Q4 just run without error
    cal = q3_calibration(df, rng); stab, n = q4_stability(df, rng)
    ok_run = (len(cal) >= 1) and (stab == stab or True)
    print(f"Q3 events={len(cal)}, Q4 stability={stab:.2f} (buckets {n}) -> {'OK' if ok_run else 'FAIL'}")

    ok = ok_q1 and ok_q2 and ok_q5 and ok_run
    print(f"\nSELF-TEST: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    c = cfg()
    return run(c["pairs"], np.random.default_rng(25))


if __name__ == "__main__":
    raise SystemExit(main())
