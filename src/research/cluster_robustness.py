"""
cluster_robustness.py — PHASE 5.11 (Chief Quant). Cluster Robustness.

Phase 5.9A (F-016) ilithibitisha latent structures kwa KMeans. Lakini KMeans ina
assumption: **spherical clusters**. Financial markets haziko spherical. Chief
(Principle 18): *No market state shall be accepted unless it is
algorithm-independent.*

Phase 5.11 inarudia latent structure discovery kwa MBINU TOFAUTI na kupima
ikiwa makundi yale yale yanajitokeza:

  • KMeans            (centroid / spherical)
  • GMM (EM)          (probabilistic / elliptical)
  • Agglomerative     (hierarchical / average linkage)

Tunapima makubaliano kwa **Adjusted Rand Index (ARI)** kati ya mbinu (kwenye
subsample ileile). ARI ya juu kuvuka mbinu = clusters ni ROBUST (sio artifact
ya algorithm moja) -> Principle 18 imetimizwa.

numpy tu (hakuna sklearn). NO ML supervised — clustering validation.

Reuse: latent_structure(collect, kmeans, FEAT), market_state_engine(cfg).

Output: reports/cluster_robustness_report.md
Endesha: python src/research/cluster_robustness.py
Self-test: python src/research/cluster_robustness.py --self-test
"""
from __future__ import annotations

import argparse, sys
from datetime import datetime
from pathlib import Path

import numpy as np

from market_state_engine import cfg
from latent_structure import collect, kmeans, FEAT

REPO_ROOT = Path(__file__).resolve().parents[2]
K = 4                  # latent clusters (Phase 5.9A)
N_ROB = 800            # subsample kwa linganisho la haki (agglomerative O(n^2))
_posix = lambda p: str(p).replace("\\", "/")


def _comb2(x):
    return x * (x - 1.0) / 2.0


def ari(a, b):
    """Adjusted Rand Index kati ya labelings mbili."""
    a = np.unique(a, return_inverse=True)[1]; b = np.unique(b, return_inverse=True)[1]
    n = len(a)
    cont = np.zeros((a.max() + 1, b.max() + 1))
    for i in range(n):
        cont[a[i], b[i]] += 1
    sum_c = _comb2(cont).sum()
    sa = _comb2(cont.sum(1)).sum(); sb = _comb2(cont.sum(0)).sum()
    tot = _comb2(n)
    exp = sa * sb / tot if tot else 0.0
    mx = (sa + sb) / 2
    return (sum_c - exp) / (mx - exp) if (mx - exp) != 0 else 1.0


def gmm(X, k, rng, iters=40):
    """Gaussian Mixture (diagonal cov) via EM, numpy. Rudisha labels."""
    n, d = X.shape
    lab, means, _ = kmeans(X, k, rng)
    var = np.array([X[lab == j].var(0) + 1e-6 if (lab == j).any() else np.ones(d) for j in range(k)])
    w = np.array([max((lab == j).mean(), 1e-3) for j in range(k)]); w /= w.sum()
    resp = np.zeros((n, k))
    for _ in range(iters):
        # E-step: log p(x|j) diagonal gaussian + log w
        logp = np.empty((n, k))
        for j in range(k):
            diff = X - means[j]
            logp[:, j] = (-0.5 * (np.log(2 * np.pi * var[j]).sum() + (diff * diff / var[j]).sum(1))
                          + np.log(w[j]))
        logp -= logp.max(1, keepdims=True)
        r = np.exp(logp); r /= r.sum(1, keepdims=True); resp = r
        # M-step
        Nk = resp.sum(0) + 1e-9
        w = Nk / n
        means = (resp.T @ X) / Nk[:, None]
        for j in range(k):
            diff = X - means[j]
            var[j] = (resp[:, j][:, None] * diff * diff).sum(0) / Nk[j] + 1e-6
    return resp.argmax(1)


def agglomerative(X, k):
    """Average-linkage agglomerative (Lance-Williams), numpy. Rudisha labels."""
    n = len(X)
    D = ((X[:, None, :] - X[None, :, :]) ** 2).sum(2)
    np.fill_diagonal(D, np.inf)
    members = [[i] for i in range(n)]
    sizes = np.ones(n); active = np.ones(n, bool)
    nclust = n
    while nclust > k:
        idx = np.where(active)[0]
        sub = D[np.ix_(idx, idx)]
        p, q = np.unravel_index(np.argmin(sub), sub.shape)
        i, j = idx[p], idx[q]
        if i > j:
            i, j = j, i
        # average linkage update: D[i,m] = (s_i*D[i,m]+s_j*D[j,m])/(s_i+s_j)
        new = (sizes[i] * D[i, :] + sizes[j] * D[j, :]) / (sizes[i] + sizes[j])
        D[i, :] = new; D[:, i] = new; D[i, i] = np.inf
        members[i] += members[j]; sizes[i] += sizes[j]
        active[j] = False; D[j, :] = np.inf; D[:, j] = np.inf
        nclust -= 1
    lab = np.empty(n, int)
    for cid, root in enumerate(np.where(active)[0]):
        for m in members[root]:
            lab[m] = cid
    return lab


def run(pairs, tfs):
    c = cfg(); rng = np.random.default_rng(0); Xs = []
    for sym in pairs:
        print(f"  {sym}: nasoma state parquet...", flush=True)
        X = collect(sym, rng)
        if len(X) > 50:
            Xs.append(X)
        print(f"    vectors={len(X)}")
    if not Xs:
        print("HITILAFU: hakuna state parquet. Endesha market_state_engine.py kwanza.", file=sys.stderr)
        return 1
    X = np.vstack(Xs)
    if len(X) > N_ROB:
        X = X[rng.choice(len(X), N_ROB, replace=False)]
    print(f"  robustness subsample N={len(X)}", flush=True)

    methods = {}
    methods["KMeans"] = kmeans(X, K, rng)[0]
    methods["GMM"] = gmm(X, K, rng)
    methods["Agglomerative"] = agglomerative(X, K)

    names = list(methods)
    L = ["# Cluster Robustness — je latent structures ni algorithm-independent? (Phase 5.11)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | methods: {', '.join(names)} | k={K} | agreement = Adjusted "
         f"Rand Index (ARI) | subsample N={len(X):,} | features: {', '.join(FEAT)}*\n",
         "> **Principle 18 (Chief):** No market state accepted unless algorithm-independent. KMeans "
         "inadhani spherical clusters; markets si spherical. Makundi yale yale yakijitokeza kwa GMM na "
         "Agglomerative -> ROBUST. ARI ya juu = makubaliano. NO sklearn, NO ML.\n",
         "## Cluster size (% per method)\n",
         "| method | " + " | ".join(f"C{j}" for j in range(K)) + " |",
         "|--------|" + "----|" * K]
    for nm in names:
        lab = methods[nm]; sizes = [f"{100*(lab==j).mean():.0f}%" for j in range(K)]
        L.append(f"| {nm} | " + " | ".join(sizes) + " |")

    L.append("\n## Agreement — Adjusted Rand Index (ARI) kati ya mbinu\n")
    L.append("| pair | ARI |")
    L.append("|------|-----|")
    aris = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            v = ari(methods[names[i]], methods[names[j]]); aris.append(v)
            L.append(f"| {names[i]} ↔ {names[j]} | {v:+.2f} |")
    mean_ari = float(np.mean(aris)) if aris else float("nan")

    L.append(f"\n## VERDICT — Principle 18: latent structures ni robust?\n")
    robust = mean_ari >= 0.5
    L.append(f"- mean ARI kuvuka mbinu = **{mean_ari:+.2f}**")
    if robust:
        L.append("\n→ ✅ **ROBUST / algorithm-independent**: makundi yale yale yanajitokeza kwa KMeans, GMM, "
                 "na Agglomerative (ARI ≥ 0.5). Principle 18 imetimizwa. Latent structures si artifact ya "
                 "KMeans → zinaweza kuendelea kuwa Latent State CANDIDATES (kuelekea Validated).")
    else:
        L.append(f"\n→ ⚠️ **HAZIJA-ROBUST vya kutosha** (ARI {mean_ari:+.2f} < 0.5): clusters zinategemea "
                 "algorithm. Kabla ya kukubali kama market states, inahitaji representation/feature bora au "
                 "non-spherical method (HDBSCAN). Principle 18 haijatimizwa bado.")
    L.append("\n*ARI: +1 = makubaliano kamili, 0 = bahati. Robust ikiwa mbinu tofauti (spherical/"
             "elliptical/hierarchical) zinatoa makundi yale yale. Principle 18. DBSCAN/HDBSCAN (density) "
             "inaweza kuongezwa baadaye (inahitaji density tuning). NO ML supervised. Inayofuata: Latent "
             "State Validation (5.12) -> Configuration Engine.*")
    out = REPO_ROOT / c["paths"]["reports"] / "cluster_robustness_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)} | mean ARI={mean_ari:+.2f}")
    return 0


def self_test():
    """3 blobs zilizotenganishwa -> KMeans/GMM/Agglomerative zote zinakubaliana (ARI~1).
       Pia ARI logic: labeling ileile -> 1.0; random -> ~0."""
    rng = np.random.default_rng(0)
    X = np.vstack([rng.normal(0, 0.5, (300, 4)), rng.normal(7, 0.5, (300, 4)),
                   rng.normal([0, 7, 0, 7], 0.5, (300, 4))])
    km = kmeans(X, 3, rng)[0]; gm = gmm(X, 3, rng); ag = agglomerative(X, 3)
    a1 = ari(km, gm); a2 = ari(km, ag); a3 = ari(gm, ag)
    agree = min(a1, a2, a3) > 0.85
    print(f"blobs ARI: KM↔GMM={a1:.2f} KM↔Agg={a2:.2f} GMM↔Agg={a3:.2f} (agree={agree})")
    same = ari([0, 0, 1, 1], [1, 1, 0, 0]); rand = ari([0, 1, 0, 1, 0, 1], [0, 0, 1, 1, 0, 1])
    ari_ok = abs(same - 1.0) < 1e-9 and rand < 0.5
    print(f"ARI logic: identical={same:.2f} (=1?) randomish={rand:.2f} (<0.5?)")
    ok = agree and ari_ok
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
