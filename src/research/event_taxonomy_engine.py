"""
event_taxonomy_engine.py — PHASE 18 (Chief Quant). Event Taxonomy.

Phase 17 (Event-Centric Representation) ilithibitisha F-035/F-036: variables ni
CONDITIONAL entities (info content inategemea Event), na hakuna universal representation
(Principle 38) — kila Event ina representation space yake (Event Representation Family).

Sasa swali jipya (F-037, OPEN): je EVENTS ZENYEWE ni homogeneous? Au kila Event ina
LATENT SUB-EVENTS zenye statistical identity tofauti?

    Mean Reversion @ LOW VOL  ?=  Mean Reversion @ HIGH VOL  (au ni events tofauti?)

Phase 18 (Event Taxonomy) inagundua sub-events ndani ya kila Event (UNSUPERVISED,
numpy KMeans kwenye context features — hakuna human labels). Maswali:

  Q1. Je Mean Reversion ina subtypes?
  Q2. Je Breakout ina subtypes?
  Q3. Je Pullback ina subtypes?
  Q4. Je representation inabadilika kwa subtype?
  Q5. Je baadhi ya sub-events ndizo zina alpha (badala ya event nzima)?

Mbinu: (a) FEATURE-STRUCTURE — clusters za asili kwenye feature space (explained var vs
permutation null, kama Phase 5.9A). (b) OUTCOME-IDENTITY — je subtypes zina y (payoff)
tofauti? R²(label on y) perm-controlled. Subtype EXISTS ikiwa outcome-identity ni
significant. Q5: per-subtype EV + one-sided p (⚠️ in-sample discovery; OOS = Phase 19,
Principle 37). NO ML.

Reuse: latent_structure (kmeans, explained_var, null_ev, state_path), market_state_engine
(cfg, pip), event_library (EVENTS_ALL), configuration_engine (EVENTS_SET, VERT),
context_value (HORIZON), contextual_alpha_engine (_phi).

Output: reports/event_taxonomy_report.md
Self-test: python src/research/event_taxonomy_engine.py --self-test
"""
from __future__ import annotations

import argparse, math, sys
from datetime import datetime
from pathlib import Path

import numpy as np
import polars as pl

from market_state_engine import cfg, pip
from latent_structure import kmeans, explained_var, null_ev, state_path
from event_library import EVENTS_ALL
from configuration_engine import EVENTS_SET, VERT
from context_value import HORIZON
from contextual_alpha_engine import _phi

REPO_ROOT = Path(__file__).resolve().parents[2]
TFS = ["H1", "H2", "H4", "D1"]
K_LIST = [2, 3, 4]
MIN_EVENT_N = 800
GAP_THR = 0.05
FEAT = ["vol", "act", "spr", "atr", "traj", "age", "trans"]
VLEVEL = {"LOW": 0.0, "NORMAL": 1.0, "HIGH": 2.0, "UNKNOWN": 1.0}
TRAJ_WIN = 3


def _runlen(states):
    rl = np.ones(len(states));
    for i in range(1, len(states)):
        rl[i] = rl[i - 1] + 1 if states[i] == states[i - 1] else 1
    return rl


def build_event_features(pairs):
    """Rudisha event -> dict(X[n×7] raw features, y[n] directional net)."""
    feats = {e: {k: [] for k in FEAT} for e in EVENTS_SET}
    ys = {e: [] for e in EVENTS_SET}
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
                if i + VERT >= n or i + HORIZON >= n or not (atr[i] > 0):
                    continue
                traj = (1.0 if i >= TRAJ_WIN and Lv[i] > Lv[i - TRAJ_WIN]
                        else -1.0 if i >= TRAJ_WIN and Lv[i] < Lv[i - TRAJ_WIN] else 0.0)
                trans = 1.0 if i >= 1 and vol[i] != vol[i - 1] else 0.0
                fv = dict(vol=VLEVEL.get(vol[i], 1.0), act=VLEVEL.get(act[i], 1.0),
                          spr=1.0 if sprst[i] == "WIDE" else 0.0, atr=atr[i],
                          traj=traj, age=min(rl[i], 30.0), trans=trans)
                for e in EVENTS_SET:
                    s = sig[e][i]
                    if s != 0:
                        for k in FEAT:
                            feats[e][k].append(fv[k])
                        ys[e].append(float(int(s) * (close[i + HORIZON] - close[i]) - spr[i]))
        print(f"  {sym}: done", flush=True)
    out = {}
    for e in EVENTS_SET:
        if len(ys[e]) >= MIN_EVENT_N:
            X = np.column_stack([np.array(feats[e][k], float) for k in FEAT])
            out[e] = (X, np.array(ys[e], float))
    return out, no_px


def _standardize(X):
    mu = X.mean(0); sd = X.std(0); sd[sd < 1e-9] = 1.0
    return (X - mu) / sd


def r2_label(y, labels):
    grand = y.mean(); tot = float(((y - grand) ** 2).sum())
    if tot <= 0:
        return 0.0
    within = 0.0
    for g in np.unique(labels):
        yg = y[labels == g]; within += float(((yg - yg.mean()) ** 2).sum())
    return 1.0 - within / tot


def subtype_analysis(X, y, rng, nrep=30):
    """Rudisha best_k, feature gap (ev−null), outcome R²(label) + perm p, labels."""
    Xs = _standardize(X)
    best = None
    for k in K_LIST:
        lab, cen, inr = kmeans(Xs, k, rng)
        ev = explained_var(Xs, inr); nev = null_ev(Xs, k, rng)
        gap = ev - nev
        if best is None or gap > best[0]:
            best = (gap, k, lab)
    gap, k, lab = best
    out_r2 = r2_label(y, lab)
    nulls = np.array([r2_label(y, rng.permutation(lab)) for _ in range(nrep)])
    p = (1 + int(np.sum(nulls >= out_r2))) / (nrep + 1)
    return dict(k=k, gap=gap, out_r2=out_r2, out_p=p, labels=lab)


def subtype_edge(y_sub):
    n = len(y_sub)
    if n < 2:
        return float("nan"), float("nan"), float("nan")
    ev = float(y_sub.mean()); se = float(y_sub.std(ddof=1) / math.sqrt(n))
    p = _phi(-ev / se) if se > 0 else float("nan")
    return ev, p, se


def run(pairs, tfs):
    c = cfg(); rng = np.random.default_rng(0)
    data, no_px = build_event_features(pairs)
    if no_px:
        print("HITILAFU: state parquet haipo. Endesha market_state_engine.py kwanza.", file=sys.stderr)
        return 1
    if not data:
        print(f"HITILAFU: hakuna event yenye N≥{MIN_EVENT_N}.", file=sys.stderr); return 1

    L = ["# Event Taxonomy — je kila Event ina sub-events? (Phase 18)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | UNSUPERVISED KMeans (numpy) kwenye context features | feature "
         f"gap vs permutation null + outcome-identity R²(label) perm-controlled | min N={MIN_EVENT_N}*\n",
         "> **F-037 (Chief, OPEN):** events zinaweza kuwa na latent SUB-EVENTS zenye statistical identity "
         "tofauti (MR@LowVol ≠ MR@HighVol?). **F-036:** variables ni conditional entities. **Principle 38:** "
         "hakuna universal representation — Event Representation Family. Subtype EXISTS ikiwa outcome-identity "
         "(payoff) inatofautiana kwa significance. ⚠️ in-sample discovery (OOS = Phase 19, Principle 37). NO ML.\n"]

    L.append("\n## Q1–Q3 — Je events zina subtypes? (feature-structure + outcome-identity)\n")
    L.append("| event | N | best k | feature gap | outcome R²(subtype) | perm p | subtypes? |")
    L.append("|-------|---|--------|-------------|---------------------|--------|-----------|")
    results = {}
    for e in EVENTS_SET:
        if e not in data:
            L.append(f"| {e} | <{MIN_EVENT_N} | — | — | — | — | — |"); continue
        X, y = data[e]
        r = subtype_analysis(X, y, rng); results[e] = (r, X, y)
        has = r["out_p"] < 0.05 and r["gap"] > GAP_THR
        L.append(f"| {e} | {len(y):,} | {r['k']} | {r['gap']:+.3f} | {r['out_r2']:.5f} | {r['out_p']:.3f} | "
                 f"{'✅' if has else '—'} |")
    sub_events = [e for e in results if results[e][0]["out_p"] < 0.05 and results[e][0]["gap"] > GAP_THR]
    L.append(f"\n→ events zenye sub-events (outcome-identity significant NA feature structure): "
             f"**{', '.join(sub_events) if sub_events else 'hakuna'}**.")

    # Q4 + Q5 per event with subtypes
    L.append("\n## Q4+Q5 — Representation & alpha kwa subtype (per-subtype centroid + EV)\n")
    for e in (sub_events or list(results)):
        r, X, y = results[e]; lab = r["labels"]
        L.append(f"\n### {e} (k={r['k']})\n")
        L.append("| subtype | N | " + " | ".join(FEAT) + " | EV | one-sided p | edge? |")
        L.append("|---------|---|" + "|".join(["---"] * len(FEAT)) + "|----|----|----|")
        for g in range(r["k"]):
            m = lab == g; Xg = X[m]; yg = y[m]
            if m.sum() == 0:
                continue
            cen = Xg.mean(0)
            ev, p, se = subtype_edge(yg)
            edge = np.isfinite(p) and p < 0.05 and ev > 0
            cells = " | ".join(f"{cen[j]:.1f}" for j in range(len(FEAT)))
            L.append(f"| S{g} | {m.sum():,} | {cells} | {ev:+.2f} | {p:.3f} | {'✅' if edge else '—'} |")
        whole_ev = float(y.mean())
        L.append(f"\n*{e} whole-event EV = {whole_ev:+.2f}. Centroid tofauti kati ya subtypes = representation "
                 "inabadilika kwa subtype (Q4). Subtype yenye edge (✅) = alpha iko kwenye SUB-event, sio event nzima (Q5).*")

    # aggregate Q5
    alpha_subs = 0; tot_subs = 0
    for e in results:
        r, X, y = results[e]; lab = r["labels"]
        for g in range(r["k"]):
            yg = y[lab == g]
            if len(yg) >= 200:
                tot_subs += 1
                ev, p, se = subtype_edge(yg)
                if np.isfinite(p) and p < 0.05 and ev > 0:
                    alpha_subs += 1

    L.append("\n## VERDICT — Phase 18 Event Taxonomy\n")
    if sub_events:
        L.append(f"→ ✅ **F-037 inaungwa mkono (in-sample)**: events **{', '.join(sub_events)}** zina sub-events "
                 f"zenye statistical identity tofauti (outcome-identity significant + feature structure). "
                 f"Sub-events zenye edge (in-sample, p<0.05, EV>0): **{alpha_subs}/{tot_subs}** — alpha inaweza "
                 "kuwa kwenye SUB-event, sio event nzima (Q5). Representation inabadilika kwa subtype (Q4). "
                 "⚠️ in-sample discovery — hatua inayofuata: Event-Subtype Confirmation (OOS + FDR, Principle "
                 "37). Architecture V6: Event Detection → **Event Taxonomy** → Event-Specific Representation. NO ML.")
    else:
        L.append("→ ⚠️ hakuna event iliyoonyesha sub-events zenye outcome-identity tofauti kwa significance "
                 "kwa data hii. Events zinaweza kuwa homogeneous zaidi kuliko dhana, au sub-structure inahitaji "
                 "features/representation tofauti (F-037 bado OPEN).")
    L.append("\n*Event Taxonomy: UNSUPERVISED KMeans kwenye context features; feature gap vs permutation null + "
             "outcome-identity R²(label) perm-controlled; per-subtype centroid (Q4) + EV/p (Q5). F-037: events "
             "zina latent sub-events. Principle 38: Event Representation Family. ⚠️ in-sample (OOS=Phase 19). "
             "NO ML. Profitable ≠ Tradable Edge.*")
    out = REPO_ROOT / c["paths"]["reports"] / "event_taxonomy_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)} (sub-events: {len(sub_events)}; alpha sub-events: {alpha_subs}/{tot_subs})")
    return 0


def self_test():
    """(1) Event yenye sub-events 2 (blobs 2 kwenye feature space, y +4 vs −4) -> outcome-identity
       significant + alpha kwenye subtype moja. (2) Noise event -> hakuna outcome-identity."""
    rng = np.random.default_rng(0); n = 4000
    # (1) two feature-blobs; blob A y~+4, blob B y~-4
    half = n // 2
    XA = rng.normal([0, 0, 0, 10, 0, 2, 0], 0.5, (half, 7))
    XB = rng.normal([2, 2, 1, 30, 1, 8, 1], 0.5, (half, 7))
    X = np.vstack([XA, XB])
    y = np.r_[rng.normal(4, 5, half), rng.normal(-4, 5, half)]
    r = subtype_analysis(X, y, rng, nrep=40)
    has = r["out_p"] < 0.05 and r["gap"] > GAP_THR
    # alpha: subtype yenye y chanya
    evs = [subtype_edge(y[r["labels"] == g]) for g in range(r["k"])]
    any_alpha = any(np.isfinite(p) and p < 0.05 and ev > 0 for ev, p, se in evs)
    print(f"subtypes: k={r['k']} gap={r['gap']:+.3f} out_r2={r['out_r2']:.4f} p={r['out_p']:.3f} has={has} alpha={any_alpha}")

    # (2) noise: uniform features, y noise
    Xn = rng.normal(0, 1, (n, 7)); yn = rng.normal(0, 5, n)
    rn = subtype_analysis(Xn, yn, rng, nrep=40)
    noise_ok = not (rn["out_p"] < 0.05 and rn["gap"] > GAP_THR)
    print(f"noise: gap={rn['gap']:+.3f} out_r2={rn['out_r2']:.5f} p={rn['out_p']:.3f} (no-subtypes={noise_ok})")

    ok = has and any_alpha and noise_ok
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
