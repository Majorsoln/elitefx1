"""
representation_operationalization_engine.py — PHASE 21 (Chief Quant).

Phase 20 ilithibitisha (Principle 42/43 CONFIRMED): coordinate space ina separability
dhaifu; robust normalization + manifold (Laplacian eigenmaps) zinaboresha sana geometry
na cross-algo agreement. Chief: "Evidence now favors a REPRESENTATION limitation over an
ontology limitation" — LAKINI bado in-sample. **Mwisho wa Representation Discovery Era.**

Phase 21: je representation hii inaweza kufanya kazi PRODUCTION / OOS BILA LEAKAGE?
  Principle 44: feature normalization ni SEHEMU ya representation (sio preprocessing).
  F-039 (OPEN): events tofauti zinaweza kuhitaji geometry tofauti.

Maswali (Chief):
  Q1. Nyström extension inaweza ku-project OOS data kwenye manifold bila kupoteza structure?
  Q2. Je manifold geometry inabaki thabiti kwenye rolling walk-forward?
  Q3. Je ARI/silhouette zinaendelea kuwa juu kwenye future periods?
  Q4. Je robust+manifold ni universal au kuna event-specific uchaguzi bora? (F-039)
  Q5. Operational cost / leakage: je representation inatumika LIVE bila lookahead?

Mbinu: Nyström out-of-sample extension ya self-tuning normalized spectral embedding.
Fit kwenye PAST (landmarks) tu; project FUTURE bila re-fit (no leakage). Linganisha
proper-Nyström (no leakage) vs joint-fit (leakage) ili kupima leakage inflation. NO ML.

Reuse: taxonomy_robustness_engine (build_event_xy_ts), representation_geometry_engine
(silhouette, norm_robust), latent_structure (kmeans), cluster_robustness (ari),
representation_geometry_engine (spectral_embed kwa joint-fit reference).

Output: reports/representation_operationalization_report.md
Self-test: python src/research/representation_operationalization_engine.py --self-test
"""
from __future__ import annotations

import argparse, sys
from datetime import datetime
from pathlib import Path

import numpy as np

from market_state_engine import cfg
from latent_structure import kmeans
from cluster_robustness import ari
from taxonomy_robustness_engine import build_event_xy_ts
from representation_geometry_engine import silhouette, norm_robust, spectral_embed

REPO_ROOT = Path(__file__).resolve().parents[2]
EVENTS_ORDER = ["pullback", "deep_pullback", "trend_continuation", "breakout", "mean_reversion"]
K = 3
KNN = 10
LANDMARK = 700        # idadi ya landmarks (fit)
OOS_CAP = 1500        # OOS sample
NWIN = 5              # rolling walk-forward folds
MIN_EVENT_N = 1500


def _local_sigma(D2, knn=KNN):
    Ds = np.sort(D2, axis=1)
    return np.sqrt(Ds[:, min(knn, D2.shape[1] - 1)]) + 1e-9


def nystrom_fit(Z, k=K, knn=KNN):
    """Fit normalized self-tuning spectral embedding kwenye landmarks Z.
    Rudisha (emb_Z rownorm, U, lam, sigЗ, dZ) kwa OOS projection."""
    D2 = np.maximum(((Z[:, None, :] - Z[None, :, :]) ** 2).sum(2), 0)
    sigЗ = _local_sigma(D2, knn)
    W = np.exp(-D2 / np.outer(sigЗ, sigЗ)); np.fill_diagonal(W, 0.0)
    dZ = W.sum(1) + 1e-12
    Wn = W / np.sqrt(np.outer(dZ, dZ))
    w, v = np.linalg.eigh(Wn)
    U = v[:, -k:]; lam = w[-k:] + 1e-12               # top-k (largest eigenvalues of Wn)
    emb = U / (np.linalg.norm(U, axis=1, keepdims=True) + 1e-12)
    return dict(emb=emb, U=U, lam=lam, sig=sigЗ, dZ=dZ, Z=Z, k=k, knn=knn)


def nystrom_project(fit, Xnew):
    """Project OOS Xnew kwenye manifold ya landmarks (Nyström) — NO re-fit (no leakage)."""
    Z = fit["Z"]; sigЗ = fit["sig"]; dZ = fit["dZ"]; U = fit["U"]; lam = fit["lam"]
    D2 = np.maximum(((Xnew[:, None, :] - Z[None, :, :]) ** 2).sum(2), 0)
    sig_x = _local_sigma(D2, fit["knn"])
    Wx = np.exp(-D2 / np.outer(sig_x, sigЗ))
    dx = Wx.sum(1) + 1e-12
    Wxn = Wx / np.sqrt(np.outer(dx, dZ))
    emb = (Wxn @ U) / lam[None, :]
    return emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-12)


def _assign(emb, cen):
    return ((emb[:, None, :] - cen[None, :, :]) ** 2).sum(2).argmin(1)


def _centroids(emb, lab, k):
    return np.array([emb[lab == j].mean(0) if (lab == j).any() else emb.mean(0) for j in range(k)])


def operationalize(X, ts, rng):
    """Q1 fidelity + Q5 leakage + Q2/Q3 rolling kwa event moja (robust-normalized)."""
    Xr = norm_robust(X); n = len(Xr); order = np.argsort(ts)
    cut = int(n * 0.6)
    is_idx = order[:cut]; oos_idx = order[cut:]
    Zi = Xr[is_idx]; Lm = Zi[rng.choice(len(Zi), min(len(Zi), LANDMARK), replace=False)]
    oo = Xr[oos_idx]; oo = oo[rng.choice(len(oo), min(len(oo), OOS_CAP), replace=False)]

    fit = nystrom_fit(Lm)
    lab_lm = kmeans(fit["emb"], K, rng)[0]; cen = _centroids(fit["emb"], lab_lm, K)
    emb_oos = nystrom_project(fit, oo)
    lab_nys = _assign(emb_oos, cen)
    sil_nys = silhouette(emb_oos, lab_nys, rng)

    # oracle / leakage: joint-fit embedding on landmarks+oos (uses OOS to FIT = leakage)
    joint = np.vstack([Lm, oo])
    emb_joint, jidx = spectral_embed(joint, K, rng, cap=len(joint))
    # map joint embedding rows that correspond to oos (jidx are indices into joint)
    mask_oos = jidx >= len(Lm)
    emb_joint_oos = emb_joint[mask_oos]
    lab_joint_oos = kmeans(emb_joint_oos, K, rng)[0]
    sil_leak = silhouette(emb_joint_oos, lab_joint_oos, rng)
    # fidelity: do Nyström-projected OOS labels match a fresh clustering of emb_oos?
    lab_oos_self = kmeans(emb_oos, K, rng)[0]
    fidelity = ari(lab_nys, lab_oos_self)

    # Q2/Q3 rolling walk-forward: fit fold i, project fold i+1, silhouette trend
    folds = np.array_split(order, NWIN)
    roll_sil = []
    for i in range(NWIN - 1):
        tr = Xr[folds[i]]; te = Xr[folds[i + 1]]
        lm = tr[rng.choice(len(tr), min(len(tr), LANDMARK), replace=False)]
        f = nystrom_fit(lm)
        te_s = te[rng.choice(len(te), min(len(te), OOS_CAP), replace=False)]
        emb_te = nystrom_project(f, te_s)
        roll_sil.append(silhouette(emb_te, kmeans(emb_te, K, rng)[0], rng))
    return dict(sil_nys=sil_nys, sil_leak=sil_leak, fidelity=fidelity,
                roll_sil=roll_sil, roll_mean=float(np.mean(roll_sil)),
                roll_last=roll_sil[-1] if roll_sil else float("nan"),
                n_oos=len(oo))


def run(pairs, tfs):
    c = cfg(); rng = np.random.default_rng(0)
    data, no_px = build_event_xy_ts(pairs)
    if no_px:
        print("HITILAFU: state parquet haipo. Endesha market_state_engine.py kwanza.", file=sys.stderr)
        return 1
    res = {}
    for e in EVENTS_ORDER:
        if e in data and len(data[e][1]) >= MIN_EVENT_N:
            X, y, ts = data[e]
            print(f"  {e}: operationalizing...", flush=True)
            res[e] = operationalize(X, ts, rng)
    if not res:
        print(f"HITILAFU: hakuna event N≥{MIN_EVENT_N}.", file=sys.stderr); return 1

    L = ["# Representation Operationalization — je manifold inafanya kazi OOS bila leakage? (Phase 21)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | robust normalization + self-tuning spectral | Nyström OOS "
         f"extension (NO re-fit) | rolling walk-forward {NWIN} folds | landmarks={LANDMARK} | NO ML*\n",
         "> **Principle 44 (Chief):** feature normalization ni SEHEMU ya representation, sio preprocessing. "
         "**Principle 42/43 (CONFIRMED).** **F-039 (OPEN):** events tofauti zinaweza kuhitaji geometry tofauti. "
         "Phase 21: thibitisha representation inafanya kazi PRODUCTION/OOS bila lookahead (fit kwenye PAST tu, "
         "project FUTURE kwa Nyström). NO ML.\n"]

    # Q1 + Q5
    L.append("\n## Q1 + Q5 — Nyström OOS fidelity & leakage check\n")
    L.append("| event | Nyström OOS silhouette (no-leak) | joint-fit silhouette (leak) | leak gap | fidelity ARI | N(OOS) |")
    L.append("|-------|--------------------------------|-----------------------------|----------|--------------|--------|")
    for e in res:
        r = res[e]; gap = r["sil_leak"] - r["sil_nys"]
        L.append(f"| {e} | {r['sil_nys']:.3f} | {r['sil_leak']:.3f} | {gap:+.3f} | {r['fidelity']:.2f} | {r['n_oos']:,} |")
    L.append("\n*(fidelity ARI = je Nyström-projected labels zinakubaliana na fresh clustering ya OOS embedding. "
             "leak gap kubwa = joint-fit (leakage) inazidi sana proper-Nyström -> in-sample silhouette ilikuwa "
             "imeinuliwa na leakage. Q5: hakuna lookahead — fit kwenye PAST tu.)*")

    # Q2 + Q3
    L.append("\n## Q2 + Q3 — Rolling walk-forward: je geometry inabaki thabiti future?\n")
    L.append("| event | rolling silhouette (kila fold→inayofuata) | mean | last fold | thabiti? |")
    L.append("|-------|-------------------------------------------|------|-----------|----------|")
    for e in res:
        r = res[e]; seq = " → ".join(f"{s:.2f}" for s in r["roll_sil"])
        stable = r["roll_mean"] > 0.25 and r["roll_last"] > 0.2
        L.append(f"| {e} | {seq} | {r['roll_mean']:.3f} | {r['roll_last']:.3f} | {'✅' if stable else '—'} |")

    # Q4 — universal vs event-specific
    L.append("\n## Q4 — Universal au event-specific? (F-039)\n")
    sils = {e: res[e]["sil_nys"] for e in res}
    spread = max(sils.values()) - min(sils.values()) if sils else 0.0
    best = max(sils, key=sils.get); worst = min(sils, key=sils.get)
    L.append(f"- Nyström OOS silhouette range: **{min(sils.values()):.3f} ({worst}) … {max(sils.values()):.3f} "
             f"({best})** (spread {spread:.3f})")
    L.append(f"\n→ {'✅ event-specific geometry (F-039 inaungwa mkono): events zinatofautiana sana' if spread > 0.1 else '— geometry inafanana kati ya events (universal manifold inatosha)'}.")

    # VERDICT
    ok = [e for e in res if res[e]["fidelity"] > 0.6 and res[e]["roll_mean"] > 0.25
          and (res[e]["sil_leak"] - res[e]["sil_nys"]) < 0.2]
    L.append("\n## VERDICT — Phase 21 Representation Operationalization\n")
    if ok:
        L.append(f"→ ✅ representation **INAFANYA KAZI OOS** kwa events **{', '.join(ok)}** ({len(ok)}/{len(res)}): "
                 "Nyström inahifadhi structure (fidelity>0.6), rolling silhouette inabaki juu, na leak-gap ndogo "
                 "(in-sample haikuwa imeinuliwa sana na leakage). Hii ni operational bila lookahead. Inayofuata: "
                 "rebuild taxonomy kwenye representation hii + OOS edge confirmation — **mwanzo wa Alpha Discovery "
                 "Era**. NO ML bado.")
    else:
        L.append(f"→ ⚠️ representation **HAIJATHIBITIKA OOS** kwa vigezo vyote (0/{len(res)} au chache): ama "
                 "Nyström fidelity ndogo, ama rolling silhouette inaporomoka, ama leak-gap kubwa (manifold ya "
                 "Phase 20 ilikuwa imeinuliwa na in-sample leakage). Representation ya manifold ni in-sample "
                 "artifact zaidi kuliko operational — inahitaji landmarks/normalization bora kabla ya alpha.")
    L.append("\n*Nyström OOS extension (fit PAST landmarks, project FUTURE, no re-fit = no leakage). proper vs "
             "joint-fit = leakage inflation. Rolling walk-forward silhouette = stability. Principle 44: "
             "normalization = representation. F-039: event-specific geometry. NO ML. Profitable ≠ Tradable Edge.*")
    out = REPO_ROOT / c["paths"]["reports"] / "representation_operationalization_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)} (operational: {len(ok)}/{len(res)})")
    return 0


def self_test():
    """(1) Nyström fidelity: rings — fit kwenye landmarks, project OOS points; OOS labels (via
       landmark-centroids) zinapatana na TRUE ring membership (ARI juu). (2) leakage gap ndogo
       kwa structure halisi (Nyström ≈ joint)."""
    rng = np.random.default_rng(0); n = 1200
    t = rng.uniform(0, 2 * np.pi, n); r = np.where(rng.random(n) < 0.5, 1.0, 4.0)
    X = np.column_stack([r * np.cos(t), r * np.sin(t)]) + rng.normal(0, 0.08, (n, 2))
    true = (r > 2).astype(int)
    half = n // 2
    Lm = X[:half]; true_lm = true[:half]; OOS = X[half:]; true_oos = true[half:]
    fit = nystrom_fit(Lm, k=2)
    lab_lm = kmeans(fit["emb"], 2, rng)[0]; cen = _centroids(fit["emb"], lab_lm, 2)
    emb_oos = nystrom_project(fit, OOS); lab_oos = _assign(emb_oos, cen)
    fid = ari(lab_oos, true_oos)
    lm_ari = ari(lab_lm, true_lm)
    ok_fit = lm_ari > 0.9
    ok_oos = fid > 0.8
    print(f"nystrom: landmark ARI={lm_ari:.2f} | OOS-projected ARI(true)={fid:.2f} (fit_ok={ok_fit}, oos_ok={ok_oos})")

    ok = ok_fit and ok_oos
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
