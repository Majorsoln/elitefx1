"""
representation_geometry_engine.py — PHASE 20 (Chief Quant). Representation Geometry Audit.

Phase 19 ilionyesha subtypes hazikupita robustness (cross-algo ARI dhaifu). Chief:
SI "subtypes ni KMeans artifacts" (ontology failure) — bali **"current representation
is not algorithm-invariant"** (methodology/representation failure). Tofauti kubwa:

  Principle 41: internal stability ≠ external validity (KMeans inajirudia 0.97 lakini
                algorithms hazikubaliani -> stable ≠ true).
  Principle 42: robust clustering inahitaji robust REPRESENTATION kabla ya robust algorithms.
  Principle 43: algorithm disagreement = ushahidi wa kufanya AUDIT ya representation, SIO
                kukataa ontology moja kwa moja.

"Algorithm haiwezi kuokoa representation mbaya." Kabla ya clustering bora, lazima tujue
kama FEATURE SPACE yenyewe inaruhusu taxonomy ya kweli kujitokeza. Maswali:

  Q1. Je feature space ina separability ya kutosha? (silhouette / Davies–Bouldin /
      Calinski–Harabasz per event, vs permutation null)
  Q2. Je normalization yetu inaficha structure? (zscore vs robust vs percentile)
  Q3. Je event-specific representations zina geometry tofauti?
  Q4. Je manifold (spectral embedding) badala ya coordinates inabadilisha separability?
  Q5. Je representation mpya inaongeza agreement kati ya algorithms? (cross-algo ARI)

NO ML. Geometry tu (numpy: silhouette, DB, CH, Laplacian eigenmaps).

Reuse: event_taxonomy_engine (build_event_features, _standardize, subtype_analysis, FEAT),
latent_structure (kmeans), cluster_robustness (gmm, ari), market_state_engine (cfg).

Output: reports/representation_geometry_report.md
Self-test: python src/research/representation_geometry_engine.py --self-test
"""
from __future__ import annotations

import argparse, sys
from datetime import datetime
from pathlib import Path

import numpy as np

from market_state_engine import cfg
from latent_structure import kmeans
from cluster_robustness import gmm, ari
from event_taxonomy_engine import build_event_features

REPO_ROOT = Path(__file__).resolve().parents[2]
CAP_SIL = 800          # silhouette subsample (O(n^2))
CAP_ARI = 2500         # km/gmm subsample
CAP_SPEC = 600         # spectral embedding subsample
EVENTS_ORDER = ["pullback", "deep_pullback", "trend_continuation", "breakout", "mean_reversion"]


# ---------- geometry metrics (numpy) ----------
def silhouette(X, lab, rng, cap=CAP_SIL):
    if len(np.unique(lab)) < 2:
        return 0.0
    n = len(X); idx = rng.choice(n, min(n, cap), replace=False)
    Z = X[idx]; L = lab[idx]
    D = np.sqrt(np.maximum(((Z[:, None, :] - Z[None, :, :]) ** 2).sum(2), 0))
    cl = np.unique(L); s = []
    for i in range(len(Z)):
        same = L == L[i]; same[i] = False
        if same.sum() == 0:
            continue
        a = D[i, same].mean()
        b = min(D[i, L == c].mean() for c in cl if c != L[i])
        s.append((b - a) / max(a, b) if max(a, b) > 0 else 0.0)
    return float(np.mean(s)) if s else 0.0


def davies_bouldin(X, lab):
    cl = np.unique(lab)
    if len(cl) < 2:
        return float("nan")
    cen = [X[lab == c].mean(0) for c in cl]
    S = [np.sqrt(((X[lab == c] - cen[i]) ** 2).sum(1)).mean() for i, c in enumerate(cl)]
    k = len(cl); tot = 0.0
    for i in range(k):
        tot += max((S[i] + S[j]) / (np.sqrt(((cen[i] - cen[j]) ** 2).sum()) + 1e-12)
                   for j in range(k) if j != i)
    return tot / k


def calinski_harabasz(X, lab):
    n = len(X); cl = np.unique(lab); k = len(cl)
    if k < 2 or n <= k:
        return 0.0
    g = X.mean(0)
    bw = sum(len(X[lab == c]) * ((X[lab == c].mean(0) - g) ** 2).sum() for c in cl)
    wi = sum(((X[lab == c] - X[lab == c].mean(0)) ** 2).sum() for c in cl)
    return float((bw / (k - 1)) / (wi / (n - k))) if wi > 0 else 0.0


# ---------- normalizations ----------
def norm_z(X):
    mu = X.mean(0); sd = X.std(0); sd[sd < 1e-9] = 1.0
    return (X - mu) / sd


def norm_robust(X):
    med = np.median(X, 0); mad = np.median(np.abs(X - med), 0) * 1.4826; mad[mad < 1e-9] = 1.0
    return (X - med) / mad


def norm_pct(X):
    out = np.empty_like(X, float)
    for j in range(X.shape[1]):
        out[:, j] = np.argsort(np.argsort(X[:, j])) / max(len(X) - 1, 1)
    return out


# ---------- manifold (Laplacian eigenmaps) ----------
def spectral_embed(X, k, rng, cap=CAP_SPEC, knn=10):
    """Spectral embedding (Ng–Jordan–Weiss) na LOCAL (self-tuning) scaling — σ_i =
    distance ya knn-th nearest neighbor; embedding rows zime-normalize (unit norm).
    Inakamata local manifold structure, sio global scale."""
    n = len(X); idx = rng.choice(n, min(n, cap), replace=False); Z = X[idx]
    D2 = np.maximum(((Z[:, None, :] - Z[None, :, :]) ** 2).sum(2), 0)
    Ds = np.sort(D2, axis=1)
    sig = np.sqrt(Ds[:, min(knn, len(Ds) - 1)]) + 1e-9      # local scale per point
    W = np.exp(-D2 / np.outer(sig, sig)); np.fill_diagonal(W, 0.0)
    d = W.sum(1); dm = 1.0 / np.sqrt(d + 1e-12)
    Lsym = np.eye(len(Z)) - (dm[:, None] * W * dm[None, :])
    w, v = np.linalg.eigh(Lsym)
    emb = v[:, :k]                                                     # NJW: k smallest-eigenvalue vectors
    emb = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-12)   # row-normalize
    return emb, idx


def cross_algo_ari(X, k, rng, cap=CAP_ARI):
    n = len(X); idx = rng.choice(n, min(n, cap), replace=False); Z = X[idx]
    return ari(kmeans(Z, k, rng)[0], gmm(Z, k, rng))


def run(pairs, tfs):
    c = cfg(); rng = np.random.default_rng(0)
    data, no_px = build_event_features(pairs)
    if no_px:
        print("HITILAFU: state parquet haipo. Endesha market_state_engine.py kwanza.", file=sys.stderr)
        return 1
    if not data:
        print("HITILAFU: hakuna event.", file=sys.stderr); return 1

    L = ["# Representation Geometry Audit — je feature space inaruhusu taxonomy? (Phase 20)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | silhouette / Davies–Bouldin / Calinski–Harabasz | normalization "
         f"(z/robust/pct) | manifold (Laplacian eigenmaps) | cross-algo ARI | NO ML*\n",
         "> **Principle 42 (Chief):** robust clustering inahitaji robust REPRESENTATION kabla ya robust "
         "algorithms. **Principle 41:** internal stability ≠ external validity. **Principle 43:** algorithm "
         "disagreement -> audit representation, sio kukataa ontology. 'Algorithm haiwezi kuokoa representation "
         "mbaya.' Tunakagua kama coordinates zetu zinaficha structure.\n"]

    info = {}
    for e in EVENTS_ORDER:
        if e not in data:
            continue
        X, y = data[e]; Xs = norm_z(X)
        # k=3 default thabiti kwa kulinganisha geometry (Phase 19: best-k haijathibitika)
        k = 3
        lab = kmeans(Xs, k, rng)[0]
        sil = silhouette(Xs, lab, rng); db = davies_bouldin(Xs, lab); ch = calinski_harabasz(Xs, lab)
        # null: shuffle each feature -> separability ya bahati
        Xn = np.column_stack([rng.permutation(Xs[:, j]) for j in range(Xs.shape[1])])
        ln = kmeans(Xn, k, rng)[0]; sil_n = silhouette(Xn, ln, rng)
        info[e] = dict(X=X, y=y, k=k, sil=sil, db=db, ch=ch, sil_null=sil_n)
        print(f"  {e}: geometry done", flush=True)

    # Q1
    L.append("\n## Q1 — Separability ya feature space (standardized, k=3)\n")
    L.append("| event | silhouette | sil(null) | Davies–Bouldin↓ | Calinski–Harabasz↑ | separable? |")
    L.append("|-------|-----------|-----------|-----------------|---------------------|------------|")
    for e in info:
        r = info[e]
        sep = r["sil"] > r["sil_null"] + 0.05 and r["sil"] > 0.25
        L.append(f"| {e} | {r['sil']:.3f} | {r['sil_null']:.3f} | {r['db']:.2f} | {r['ch']:.0f} | "
                 f"{'✅' if sep else '—'} |")
    L.append("\n*(silhouette >0.25 & > null = separable; DB chini bora; CH juu bora. Phase 19: agreement "
             "dhaifu — Q1 inaonyesha kama ni kwa sababu feature space haina separability.)*")

    # Q2 — normalization
    L.append("\n## Q2 — Je normalization inaficha structure? (silhouette kwa z/robust/percentile)\n")
    L.append("| event | z-score | robust(MAD) | percentile | bora |")
    L.append("|-------|---------|-------------|------------|------|")
    for e in info:
        X = info[e]["X"]; k = info[e]["k"]; cells = {}
        for nm, fn in [("z", norm_z), ("robust", norm_robust), ("pct", norm_pct)]:
            Xt = fn(X); lab = kmeans(Xt, k, rng)[0]; cells[nm] = silhouette(Xt, lab, rng)
        best = max(cells, key=cells.get)
        L.append(f"| {e} | {cells['z']:.3f} | {cells['robust']:.3f} | {cells['pct']:.3f} | {best} |")
    L.append("\n→ tofauti kubwa kati ya normalizations = normalization inaathiri structure (Principle 42).")

    # Q3 — per-event geometry differs (already from Q1 sil/db/ch)
    L.append("\n## Q3 — Je event-specific representations zina geometry tofauti?\n")
    sils = {e: info[e]["sil"] for e in info}
    spread = max(sils.values()) - min(sils.values()) if sils else 0.0
    L.append(f"- silhouette range kati ya events: **{min(sils.values()):.3f} … {max(sils.values()):.3f}** "
             f"(spread {spread:.3f})")
    L.append(f"\n→ {'✅ geometry inatofautiana kwa event' if spread > 0.05 else '— geometry inafanana'} "
             "(inaunga mkono Event Representation Family — kila event geometry yake).")

    # Q4 + Q5 — manifold vs coordinates + cross-algo ARI per representation
    L.append("\n## Q4+Q5 — Manifold vs coordinates; je representation inaongeza algorithm agreement?\n")
    L.append("| event | ARI(z) | ARI(robust) | ARI(pct) | ARI(manifold) | sil(coord) | sil(manifold) | rep inasaidia? |")
    L.append("|-------|--------|-------------|----------|---------------|------------|---------------|----------------|")
    helped = 0
    for e in info:
        X = info[e]["X"]; k = info[e]["k"]
        ari_z = cross_algo_ari(norm_z(X), k, rng)
        ari_r = cross_algo_ari(norm_robust(X), k, rng)
        ari_p = cross_algo_ari(norm_pct(X), k, rng)
        emb, _ = spectral_embed(norm_z(X), k, rng)
        ari_m = ari(kmeans(emb, k, rng)[0], gmm(emb, k, rng))
        sil_coord = info[e]["sil"]
        lab_m = kmeans(emb, k, rng)[0]; sil_m = silhouette(emb, lab_m, rng)
        base = ari_z
        best_alt = max(ari_r, ari_p, ari_m)
        rep_helps = best_alt > base + 0.15 or sil_m > sil_coord + 0.1
        helped += 1 if rep_helps else 0
        L.append(f"| {e} | {ari_z:.2f} | {ari_r:.2f} | {ari_p:.2f} | {ari_m:.2f} | {sil_coord:.2f} | "
                 f"{sil_m:.2f} | {'✅' if rep_helps else '—'} |")
    L.append(f"\n→ events ambapo representation mbadala/manifold inaongeza agreement au separability: "
             f"**{helped}/{len(info)}**.")

    # VERDICT
    n_sep = sum(1 for e in info if info[e]["sil"] > info[e]["sil_null"] + 0.05 and info[e]["sil"] > 0.25)
    L.append("\n## VERDICT — Phase 20 Representation Geometry\n")
    if helped >= 1 or n_sep >= 1:
        L.append(f"→ representation/geometry **INAATHIRI** matokeo: events {n_sep}/{len(info)} zina separability "
                 f"ya feature space; representation mbadala (robust/percentile/manifold) iliongeza agreement kwa "
                 f"{helped}/{len(info)}. Hii inaunga mkono **Principle 42/43**: tatizo la Phase 19 lilikuwa "
                 "REPRESENTATION, sio lazima ontology. Inayofuata: jenga representation iliyoboreshwa (manifold/"
                 "normalization bora) kisha rudia taxonomy + robustness. NO ML bado.")
    else:
        L.append(f"→ ⚠️ feature space ya sasa **haina separability** (silhouette ≈ null kwa events zote) na "
                 "representation mbadala hazikuongeza agreement. Hii inaelekeza kuwa coordinates za sasa "
                 "(vol/act/spr/atr/traj/age/trans) hazibebi geometry ya cluster — inahitaji features mpya kabisa "
                 "(sio normalization/manifold tu). Principle 42: representation ndiyo kizuizi.")
    L.append("\n*Geometry: silhouette/DB/CH vs permutation null; normalization (z/robust/pct); Laplacian "
             "eigenmaps manifold; cross-algo ARI per representation. Principle 41 (stable≠true), 42 "
             "(representation kabla ya clustering), 43 (disagreement → audit representation). NO ML. "
             "Profitable ≠ Tradable Edge.*")
    out = REPO_ROOT / c["paths"]["reports"] / "representation_geometry_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)} (separable: {n_sep}/{len(info)}; rep-helps: {helped}/{len(info)})")
    return 0


def self_test():
    """(1) metrics: blobs -> silhouette juu/DB chini/CH juu; noise -> sil ndogo zaidi.
       (2) normalization: structure kwenye feature ndogo, noise kwenye feature kubwa ->
           z-score inarudisha TRUE labels (ARI), raw inashindwa.
       (3) manifold: rings 2 (nonlinear) -> spectral embedding inarudisha ring membership (ARI)."""
    rng = np.random.default_rng(0)
    # (1) blobs vs noise — silhouette discriminates
    cen = np.array([[0, 0, 0], [8, 8, 0], [0, 0, 8]], float)
    Xb = np.vstack([cen[i] + rng.normal(0, 0.4, (250, 3)) for i in range(3)])
    lb = kmeans(Xb, 3, rng)[0]
    sb = silhouette(Xb, lb, rng); dbb = davies_bouldin(Xb, lb); chb = calinski_harabasz(Xb, lb)
    Yn = rng.normal(0, 1, (750, 3)); sn = silhouette(Yn, kmeans(Yn, 3, rng)[0], rng)
    m1 = sb > 0.5 and sb > sn + 0.4 and dbb < 1.0 and chb > 100
    print(f"metrics: blob sil={sb:.2f} DB={dbb:.2f} CH={chb:.0f} | noise sil={sn:.2f} (ok={m1})")

    # (2) normalization: TRUE structure in small-scale feat0; huge-scale noise feat1 dominates raw distance
    true = np.repeat([0, 1, 2], 200)
    f0 = np.repeat([0.0, 5.0, 10.0], 600 // 3) + rng.normal(0, 0.3, 600)
    f1 = rng.normal(0, 5000, 600)
    Xr = np.column_stack([f0, f1])
    ari_raw = ari(kmeans(Xr, 3, rng)[0], true)
    ari_z = ari(kmeans(norm_z(Xr), 3, rng)[0], true)
    m2 = ari_z > ari_raw + 0.3
    print(f"normalization: raw ARI(true)={ari_raw:.2f} -> z ARI(true)={ari_z:.2f} (recovered={m2})")

    # (3) manifold: concentric rings; recover ring membership (ARI to truth) on same subsample
    t = rng.uniform(0, 2 * np.pi, 600)
    r = np.where(rng.random(600) < 0.5, 1.0, 4.0)
    ring = np.column_stack([r * np.cos(t), r * np.sin(t)]) + rng.normal(0, 0.08, (600, 2))
    true_ring = (r > 2).astype(int)
    emb, idx = spectral_embed(ring, 2, rng, cap=600)
    ari_coord = ari(kmeans(ring[idx], 2, rng)[0], true_ring[idx])
    ari_man = ari(kmeans(emb, 2, rng)[0], true_ring[idx])
    m3 = ari_man > ari_coord + 0.3
    print(f"manifold: rings coord ARI={ari_coord:.2f} -> manifold ARI={ari_man:.2f} (improved={m3})")

    ok = m1 and m2 and m3
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
