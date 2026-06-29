"""
taxonomy_robustness_engine.py — PHASE 19 (Chief Quant). Taxonomy Robustness Audit.

Phase 18 (Event Taxonomy) ilionyesha trend_continuation (k=4) na breakout (k=3) zina
sub-events; pullback/deep_pullback/mean_reversion hazikuonyesha. Lakini ilitumia
**KMeans pekee**. Chief: **Principle 39** — market ontology HAITAINFERWA kutoka clustering
algorithm moja. Kabla ya OOS confirmation, lazima tuhakikishe subtypes ni ALGORITHM-
INDEPENDENT na STABLE (sio artifact ya KMeans).

Pia: Phase 18 ilionyesha 0/17 subtypes zina edge -> **Principle 40**: taxonomy halali ≠
tradable alpha. (F-038: taxonomy ni hierarchical & event-specific; complexity tofauti.)

Phase 19 (Taxonomy Robustness Audit). Maswali:
  Q1. KMeans vs GMM vs Agglomerative — taxonomy inafanana? (ARI / NMI)
  Q2. Subtype assignment stability (split-half ARI).
  Q3. Centroid stability kwenye tofauti za sample (bootstrap).
  Q4. Subtypes zinaendelea OOS? (IS centroids -> OOS outcome-identity perm test)
  Q5. Complexity (best-k) inabaki thabiti kwenye subsamples?

Subtype ni ROBUST ikiwa: cross-algorithm ARI juu NA split-half ARI juu NA OOS-persist.
NO ML.

Reuse: cluster_robustness (ari, gmm, agglomerative), latent_structure (kmeans),
event_taxonomy_engine (FEAT, VLEVEL, TRAJ_WIN, _runlen, _standardize, subtype_analysis,
r2_label), market_state_engine (cfg, pip), event_library, configuration_engine, context_value.

Output: reports/taxonomy_robustness_report.md
Self-test: python src/research/taxonomy_robustness_engine.py --self-test
"""
from __future__ import annotations

import argparse, math, sys
from datetime import datetime
from pathlib import Path

import numpy as np
import polars as pl

from market_state_engine import cfg, pip
from latent_structure import kmeans, state_path
from cluster_robustness import ari, gmm, agglomerative
from event_library import EVENTS_ALL
from configuration_engine import EVENTS_SET, VERT
from context_value import HORIZON
from event_taxonomy_engine import FEAT, VLEVEL, TRAJ_WIN, _runlen, _standardize, subtype_analysis, r2_label

REPO_ROOT = Path(__file__).resolve().parents[2]
TFS = ["H1", "H2", "H4", "D1"]
MIN_EVENT_N = 800
CAP_KG = 5000         # KMeans/GMM subsample
CAP_AG = 1200         # Agglomerative subsample (O(n^2))
NBOOT = 6             # k-stability / centroid bootstraps
IS_FRAC = 0.6


def nmi(a, b):
    """Normalized Mutual Information kati ya labelings."""
    a = np.unique(a, return_inverse=True)[1]; b = np.unique(b, return_inverse=True)[1]
    n = len(a); ca = np.bincount(a); cb = np.bincount(b)
    cont = np.zeros((len(ca), len(cb)))
    for i in range(n):
        cont[a[i], b[i]] += 1
    pij = cont / n; pa = ca / n; pb = cb / n
    mi = 0.0
    for i in range(len(ca)):
        for j in range(len(cb)):
            if pij[i, j] > 0:
                mi += pij[i, j] * math.log(pij[i, j] / (pa[i] * pb[j]))
    Ha = -np.sum(pa * np.log(pa + 1e-12)); Hb = -np.sum(pb * np.log(pb + 1e-12))
    return mi / math.sqrt(Ha * Hb) if Ha > 0 and Hb > 0 else 0.0


def assign(X, cen):
    return ((X[:, None, :] - cen[None, :, :]) ** 2).sum(2).argmin(1)


def centroids(X, lab, k):
    return np.array([X[lab == j].mean(0) if (lab == j).any() else X.mean(0) for j in range(k)])


def build_event_xy_ts(pairs):
    feats = {e: {kk: [] for kk in FEAT} for e in EVENTS_SET}
    ys = {e: [] for e in EVENTS_SET}; ts_ = {e: [] for e in EVENTS_SET}
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
            ts = df["ts"].to_numpy().astype("datetime64[s]").astype(np.int64)
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
                    if sig[e][i] != 0:
                        for kk in FEAT:
                            feats[e][kk].append(fv[kk])
                        ys[e].append(float(int(sig[e][i]) * (close[i + HORIZON] - close[i]) - spr[i]))
                        ts_[e].append(int(ts[i]))
        print(f"  {sym}: done", flush=True)
    out = {}
    for e in EVENTS_SET:
        if len(ys[e]) >= MIN_EVENT_N:
            X = np.column_stack([np.array(feats[e][kk], float) for kk in FEAT])
            out[e] = (X, np.array(ys[e], float), np.array(ts_[e], np.int64))
    return out, no_px


def robustness(X, y, ts, rng):
    """Rudisha metrics za robustness kwa event moja."""
    Xs = _standardize(X); n = len(Xs)
    # best k (subsample)
    samp = rng.choice(n, min(n, CAP_KG), replace=False)
    r = subtype_analysis(X[samp], y[samp], rng); k = r["k"]

    # Q1: cross-algorithm agreement (common subsample for 3-way incl. agglomerative)
    s3 = rng.choice(n, min(n, CAP_AG), replace=False); Z = Xs[s3]
    lk = kmeans(Z, k, rng)[0]; lg = gmm(Z, k, rng); la = agglomerative(Z, k)
    ari_kg = ari(lk, lg); ari_ka = ari(lk, la); ari_ga = ari(lg, la)
    nmi_kg = nmi(lk, lg)
    mean_ari = float(np.mean([ari_kg, ari_ka, ari_ga]))

    # Q2: split-half assignment stability (KMeans)
    perm = rng.permutation(n); h1, h2 = perm[:n // 2], perm[n // 2:]
    c1 = centroids(Xs[h1], kmeans(Xs[h1], k, rng)[0], k)
    c2 = centroids(Xs[h2], kmeans(Xs[h2], k, rng)[0], k)
    common = rng.choice(n, min(n, CAP_KG), replace=False)
    split_ari = ari(assign(Xs[common], c1), assign(Xs[common], c2))

    # Q3: centroid stability (bootstrap) — mean cross-boot assignment ARI
    boots = []
    base_c = centroids(Xs[samp], kmeans(Xs[samp], k, rng)[0], k)
    for _ in range(NBOOT):
        bs = rng.choice(n, min(n, CAP_KG), replace=True)
        cb = centroids(Xs[bs], kmeans(Xs[bs], k, rng)[0], k)
        boots.append(ari(assign(Xs[common], base_c), assign(Xs[common], cb)))
    cent_stab = float(np.mean(boots))

    # Q4: OOS persistence — fit on IS, assign OOS, outcome-identity perm test on OOS
    order = np.argsort(ts); cut = int(n * IS_FRAC)
    is_idx, oos_idx = order[:cut], order[cut:]
    c_is = centroids(Xs[is_idx], kmeans(Xs[is_idx], k, rng)[0], k)
    oos_lab = assign(Xs[oos_idx], c_is); y_oos = y[oos_idx]
    oos_r2 = r2_label(y_oos, oos_lab)
    nulls = np.array([r2_label(y_oos, rng.permutation(oos_lab)) for _ in range(30)])
    oos_p = (1 + int(np.sum(nulls >= oos_r2))) / 31

    # Q5: k-stability across subsamples
    ks = []
    for _ in range(NBOOT):
        bs = rng.choice(n, min(n, CAP_KG), replace=False)
        ks.append(subtype_analysis(X[bs], y[bs], rng, nrep=15)["k"])
    modal_k = int(np.bincount(ks).argmax()); k_consist = float(np.mean(np.array(ks) == modal_k))

    robust = mean_ari > 0.5 and split_ari > 0.5 and oos_p < 0.05
    return dict(k=k, ari_kg=ari_kg, ari_ka=ari_ka, ari_ga=ari_ga, mean_ari=mean_ari, nmi_kg=nmi_kg,
                split_ari=split_ari, cent_stab=cent_stab, oos_r2=oos_r2, oos_p=oos_p,
                modal_k=modal_k, k_consist=k_consist, robust=robust)


def run(pairs, tfs):
    c = cfg(); rng = np.random.default_rng(0)
    data, no_px = build_event_xy_ts(pairs)
    if no_px:
        print("HITILAFU: state parquet haipo. Endesha market_state_engine.py kwanza.", file=sys.stderr)
        return 1
    if not data:
        print(f"HITILAFU: hakuna event N≥{MIN_EVENT_N}.", file=sys.stderr); return 1

    res = {}
    for e in EVENTS_SET:
        if e in data:
            X, y, ts = data[e]
            print(f"  {e}: robustness...", flush=True)
            res[e] = robustness(X, y, ts, rng)

    L = ["# Taxonomy Robustness Audit — je subtypes ni algorithm-independent & stable? (Phase 19)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | KMeans/GMM/Agglomerative ARI+NMI | split-half + bootstrap "
         f"stability | OOS persistence | k-stability | min N={MIN_EVENT_N}*\n",
         "> **Principle 39 (Chief):** market ontology HAITAINFERWA kutoka clustering algorithm moja. "
         "**Principle 40:** valid taxonomy ≠ tradable alpha (Phase 18: 0/17 subtypes zilikuwa na edge). "
         "**F-038:** taxonomy ni hierarchical & event-specific. Subtype ni ROBUST ikiwa cross-algo ARI>0.5 "
         "NA split-half ARI>0.5 NA OOS-persist (p<0.05). NO ML.\n"]

    # Q1
    L.append("\n## Q1 — Cross-algorithm agreement (ARI: KMeans/GMM/Agglomerative)\n")
    L.append("| event | k | ARI(KM,GMM) | ARI(KM,Agg) | ARI(GMM,Agg) | mean ARI | NMI(KM,GMM) | algo-independent? |")
    L.append("|-------|---|-------------|-------------|--------------|----------|-------------|-------------------|")
    for e in res:
        r = res[e]
        L.append(f"| {e} | {r['k']} | {r['ari_kg']:.2f} | {r['ari_ka']:.2f} | {r['ari_ga']:.2f} | "
                 f"{r['mean_ari']:.2f} | {r['nmi_kg']:.2f} | {'✅' if r['mean_ari']>0.5 else '—'} |")

    # Q2+Q3
    L.append("\n## Q2+Q3 — Stability (split-half ARI; bootstrap centroid ARI)\n")
    L.append("| event | split-half ARI | bootstrap centroid ARI | stable? |")
    L.append("|-------|----------------|------------------------|---------|")
    for e in res:
        r = res[e]
        L.append(f"| {e} | {r['split_ari']:.2f} | {r['cent_stab']:.2f} | {'✅' if r['split_ari']>0.5 and r['cent_stab']>0.5 else '—'} |")

    # Q4
    L.append("\n## Q4 — OOS persistence (IS centroids → OOS outcome-identity)\n")
    L.append("| event | OOS R²(subtype) | perm p | persists OOS? |")
    L.append("|-------|-----------------|--------|---------------|")
    for e in res:
        r = res[e]
        L.append(f"| {e} | {r['oos_r2']:.5f} | {r['oos_p']:.3f} | {'✅' if r['oos_p']<0.05 else '—'} |")

    # Q5
    L.append("\n## Q5 — Complexity (best-k) stability across subsamples\n")
    L.append("| event | best k | modal k | k-consistency |")
    L.append("|-------|--------|---------|---------------|")
    for e in res:
        r = res[e]
        L.append(f"| {e} | {r['k']} | {r['modal_k']} | {r['k_consist']*100:.0f}% |")

    robust_events = [e for e in res if res[e]["robust"]]
    L.append("\n## VERDICT — Phase 19 Taxonomy Robustness\n")
    if robust_events:
        L.append(f"→ ✅ subtypes ROBUST (algorithm-independent + stable + OOS-persist): "
                 f"**{', '.join(robust_events)}** ({len(robust_events)}/{len(res)}). Hizi PEKEE zinastahili "
                 "kuendelea (Principle 39 imetimizwa). ⚠️ **Principle 40:** taxonomy robust ≠ alpha — bado "
                 "hatujathibitisha tradability. Inayofuata: Event-Subtype OOS edge confirmation (FDR).")
    else:
        L.append(f"→ ⚠️ hakuna subtype iliyo ROBUST kwa vigezo vyote (cross-algo ARI>0.5 + split-half>0.5 + "
                 "OOS-persist). Subtypes za Phase 18 zinaweza kuwa **artifact ya KMeans** (Principle 39 "
                 "imezuia kuzitumia). Taxonomy inahitaji representation/algorithm bora kabla ya kuaminika.")
    L.append("\n*Taxonomy Robustness: cross-algorithm ARI/NMI (KMeans/GMM/Agglomerative), split-half + "
             "bootstrap stability, OOS outcome-identity persistence, k-stability. Principle 39: si algorithm "
             "moja. Principle 40: taxonomy ≠ alpha. F-038: hierarchical & event-specific. NO ML. "
             "Profitable ≠ Tradable Edge.*")
    out = REPO_ROOT / c["paths"]["reports"] / "taxonomy_robustness_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)} (robust subtypes: {len(robust_events)}/{len(res)})")
    return 0


def self_test():
    """(1) nmi: identical=1, independent≈0. (2) blobs 3 -> KMeans/GMM/Agglomerative ARI juu
       (algorithm-independent). (3) noise -> ARI chini."""
    rng = np.random.default_rng(0)
    a = np.array([0, 0, 1, 1, 2, 2] * 50)
    nmi_id = nmi(a, a); b = rng.permutation(a); nmi_rand = nmi(a, b)
    nmi_ok = nmi_id > 0.99 and nmi_rand < 0.2
    print(f"nmi: identical={nmi_id:.2f} independent={nmi_rand:.2f} (ok={nmi_ok})")

    # blobs (well separated) -> algorithms agree
    cen = np.array([[0, 0, 0], [8, 8, 0], [0, 0, 8]], float)
    X = np.vstack([cen[i] + rng.normal(0, 0.4, (200, 3)) for i in range(3)])
    lk = kmeans(X, 3, rng)[0]; lg = gmm(X, 3, rng); la = agglomerative(X, 3)
    blob_ari = np.mean([ari(lk, lg), ari(lk, la), ari(lg, la)])
    blob_ok = blob_ari > 0.7
    print(f"blobs: mean cross-algo ARI={blob_ari:.2f} (algo-independent={blob_ok})")

    # noise -> low agreement
    Y = rng.normal(0, 1, (400, 3))
    nk = kmeans(Y, 3, rng)[0]; ng = gmm(Y, 3, rng); na = agglomerative(Y, 3)
    noise_ari = np.mean([ari(nk, ng), ari(nk, na), ari(ng, na)])
    noise_ok = noise_ari < 0.5
    print(f"noise: mean cross-algo ARI={noise_ari:.2f} (not-robust={noise_ok})")

    ok = nmi_ok and blob_ok and noise_ok
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
