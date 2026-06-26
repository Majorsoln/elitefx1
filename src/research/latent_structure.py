"""
latent_structure.py — PHASE 5.9A (Chief Quant). Latent Market Structure.

Phase 5.9 (Mechanism Discovery) HAIKUIDHINISHWA: ilipiga HUMAN TAXONOMY
(Expansion/Exhaustion/…) kwa rules, kisha kuipima — hiyo ni VERIFICATION, sio
DISCOVERY. Inakiuka doctrine: **NO HUMAN MARKET THEORY**.

Phase 5.9A inafanya kinyume: hatuweki labels. Tunaacha DATA ijieleze.

    Features → Unknown Structure → Discovery → (baadaye) jina.

Mbinu (UNSUPERVISED, numpy tu — hakuna sklearn, hakuna human labels):
  1. Tengeneza Market State Vectors kutoka features ZOTE muhimu (per-pair
     standardized -> kutatua tatizo la SCALE alilolitaja Chief):
        vol_z · vol_slope · act_z · act_slope · spr_z · transition · lifecycle
  2. KMeans (numpy) kwa k ∈ {3,4,5,6}. Pima EXPLAINED VARIANCE (between/total).
  3. PERMUTATION NULL: changanya kila column kivyake, cluster tena -> null EV.
     Real EV ≫ null EV  =>  kuna NATURAL STRUCTURE (sio bahati).
  4. CROSS-PAIR: je clusters zinajirudia kwa pairs zote? (latent structure ya
     soko, sio ya pair moja).

Verdict: latent structures ZIPO ikiwa real EV ≫ null NA clusters zinajirudia
cross-pair. Majina YATAKUJA mwishoni (sio sasa). Sio Cosine (inapuuza scale);
ni standardized Euclidean.

> NO Mechanism Library (Chief). NO ML supervised. Hii ni representation discovery.

Reuse: market_state_engine, mechanism_discovery.signatures (feature extraction).

Output: reports/latent_structure_report.md
Endesha: python src/research/latent_structure.py
Self-test: python src/research/latent_structure.py --self-test
"""
from __future__ import annotations

import argparse, sys
from datetime import datetime
from pathlib import Path

import numpy as np
import polars as pl

from market_state_engine import cfg, pip
from mechanism_discovery import signatures, SIG_DIM   # feature extraction tu (sio taxonomy)

REPO_ROOT = Path(__file__).resolve().parents[2]
TFS = ["H1", "H2", "H4", "D1"]
K_LIST = [3, 4, 5, 6]
CAP_PER_PAIR = 8000     # sample cap kwa pair (clustering)
NULL_SHUFFLES = 3       # permutation null repeats
FEAT = ["vol_z", "vol_slope", "act_z", "act_slope", "spr_z", "transition", "lifecycle"]
_posix = lambda p: str(p).replace("\\", "/")


def kmeans(X, k, rng, iters=60, restarts=4):
    """numpy KMeans. Rudisha (labels, centroids, inertia)."""
    n = len(X); best = (None, None, np.inf)
    for _ in range(restarts):
        cen = X[rng.choice(n, k, replace=False)].copy()
        lab = np.zeros(n, int)
        for _ in range(iters):
            d = ((X[:, None, :] - cen[None, :, :]) ** 2).sum(2)
            new_lab = d.argmin(1)
            cen2 = np.array([X[new_lab == j].mean(0) if (new_lab == j).any() else cen[j]
                             for j in range(k)])
            if np.array_equal(new_lab, lab) and np.allclose(cen2, cen):
                lab = new_lab; cen = cen2; break
            lab, cen = new_lab, cen2
        inertia = float(((X - cen[lab]) ** 2).sum())
        if inertia < best[2]:
            best = (lab.copy(), cen.copy(), inertia)
    return best


def explained_var(X, inertia):
    total = float(((X - X.mean(0)) ** 2).sum())
    return 1.0 - inertia / total if total > 0 else 0.0


def null_ev(X, k, rng):
    """EV ya data iliyochanganywa (kila column kivyake) — structure ya bahati."""
    evs = []
    for _ in range(NULL_SHUFFLES):
        Xs = np.column_stack([rng.permutation(X[:, j]) for j in range(X.shape[1])])
        _, _, inr = kmeans(Xs, k, rng, restarts=2)
        evs.append(explained_var(Xs, inr))
    return float(np.mean(evs))


def state_path(sym, tf):
    return REPO_ROOT / cfg()["paths"]["processed"] / "state" / f"symbol={sym}" / f"tf={tf}.parquet"


def collect(sym, rng):
    """Rudisha vectors[N×7] (finite, per-df standardized) kwa pair, sampled.
    INASOMA state parquet (cached na market_state_engine) — HAKUNA tick rescan
    (haraka mara nyingi; atr/tc/spr/volatility_state vyote vimo)."""
    pp = pip(sym); rows = []
    for tf in TFS:
        p = state_path(sym, tf)
        if not p.exists():
            continue
        df = pl.read_parquet(p)
        sig, *_ = signatures(df, pp)
        rows.append(sig[np.all(np.isfinite(sig), axis=1)])
    X = np.vstack(rows) if rows else np.empty((0, SIG_DIM))
    if len(X) > CAP_PER_PAIR:
        X = X[rng.choice(len(X), CAP_PER_PAIR, replace=False)]
    return X


def run(pairs, tfs):
    c = cfg(); rng = np.random.default_rng(0)
    Xs = []; pair_ids = []; miss = 0
    for sym in pairs:
        print(f"  {sym}: nasoma state parquet...", flush=True)
        X = collect(sym, rng)
        if len(X) > 50:
            Xs.append(X); pair_ids += [sym] * len(X)
        else:
            miss += 1
        print(f"    vectors={len(X)}")
    if not Xs:
        print("HITILAFU: hakuna state parquet. Endesha market_state_engine.py kwanza "
              "(data/processed/state/...).", file=sys.stderr); return 1
    if miss:
        print(f"  (onyo: pairs {miss} hazina state parquet)")
    X = np.vstack(Xs); pid = np.array(pair_ids)
    print(f"  jumla vectors={len(X)} dim={X.shape[1]}", flush=True)

    L = ["# Latent Market Structure — je makundi ya asili yapo? (Phase 5.9A)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | Market State Vector ({', '.join(FEAT)}) per-pair standardized "
         f"| UNSUPERVISED KMeans (numpy) | EV vs permutation null | N={len(X):,}*\n",
         "> **Q-012 (Chief, reframed):** BILA labels za binadamu — je market state vectors zinajikusanya "
         "kuwa makundi ya asili (latent structures)? Real EV ≫ null = structure ipo. Clusters zikijirudia "
         "cross-pair = latent structure ya soko. **NO HUMAN TAXONOMY** — majina yatakuja mwishoni. NO ML.\n",
         "## Cluster validity — explained variance: real vs permutation null\n",
         "| k | EV real | EV null | gap (real−null) | structure? |",
         "|---|---------|---------|-----------------|------------|"]
    results = {}
    for k in K_LIST:
        lab, cen, inr = kmeans(X, k, rng)
        ev = explained_var(X, inr); nev = null_ev(X, k, rng)
        results[k] = (ev, nev, lab, cen)
        gap = ev - nev
        L.append(f"| {k} | {ev:.3f} | {nev:.3f} | {gap:+.3f} | {'✅' if gap > 0.10 else '—'} |")
    # best k = gap kubwa zaidi
    bestk = max(K_LIST, key=lambda k: results[k][0] - results[k][1])
    ev, nev, lab, cen = results[bestk]; gap = ev - nev
    L.append(f"\n→ best k = **{bestk}** (gap {gap:+.3f}).\n")

    # cross-pair: je clusters zinajirudia?
    L.append(f"## Cross-pair recurrence (k={bestk}) — je clusters zipo kwa pairs zote?\n")
    L.append("| cluster | size % | pairs present (≥5%) | universal? |")
    L.append("|---------|--------|---------------------|------------|")
    pairs_u = sorted(set(pid)); recur = 0
    for j in range(bestk):
        mask = lab == j; size = mask.mean() * 100
        present = sum(1 for p in pairs_u if (pid[mask] == p).sum() / max((pid == p).sum(), 1) >= 0.05)
        uni = present >= 0.75 * len(pairs_u)
        recur += 1 if uni else 0
        L.append(f"| C{j} | {size:.0f}% | {present}/{len(pairs_u)} | {'✅' if uni else '—'} |")

    L.append("\n## VERDICT — Q-012: latent market structures zipo?\n")
    struct = gap > 0.10
    universal = recur >= 0.5 * bestk
    if struct and universal:
        L.append(f"✅ **Latent structures ZIPO na zinajirudia cross-pair** (gap {gap:+.3f}, {recur}/{bestk} "
                 "clusters universal). Zinaweza kuwa 'Latent State Library'. **Sasa** (na sio kabla) "
                 "tunaweza kuanza kuzifasiri/kuzipa majina. F-015 inaelekea kuthibitishwa kama LATENT "
                 "STRUCTURE (sio human mechanism).")
    elif struct:
        L.append(f"⚠️ **Structure ipo (gap {gap:+.3f}) lakini si universal** ({recur}/{bestk} clusters "
                 "cross-pair). Latent structures ni pair-local zaidi — inalingana na F-014.")
    else:
        L.append(f"❌ **Hakuna structure ya asili wazi** (gap {gap:+.3f} ≤ 0.10). Market state vectors "
                 "hazijikusanyi zaidi ya bahati; inahitaji features zaidi au representation tofauti.")
    L.append("\n*UNSUPERVISED: hakuna labels za binadamu (Expansion/etc.) zilizotumika — data yenyewe. "
             "Per-pair standardized (scale-invariant; sio cosine). EV vs permutation null = structure halisi "
             "dhidi ya bahati. Cross-pair recurrence = latent structure ya soko. Majina YATAKUJA tu kama "
             "clusters zithibitike. F-015 = 'Latent Market Structures' (OPEN). NO ML, NO Latent State "
             "Library bado (Chief). Profitable ≠ Tradable Edge.*")
    out = REPO_ROOT / c["paths"]["reports"] / "latent_structure_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """(1) blobs 3 -> EV real ≫ null (structure). (2) uniform noise -> gap ndogo."""
    rng = np.random.default_rng(0)
    # (1) blobs
    centers = np.array([[0, 0, 0, 0], [6, 6, 0, 0], [0, 0, 6, 6]], float)
    X = np.vstack([centers[i] + rng.normal(0, 0.6, (1500, 4)) for i in range(3)])
    _, _, inr = kmeans(X, 3, rng); ev = explained_var(X, inr); nev = null_ev(X, 3, rng)
    blob_ok = (ev - nev) > 0.3 and ev > 0.7
    print(f"blobs: EV real={ev:.3f} null={nev:.3f} gap={ev-nev:+.3f} (structure={blob_ok})")
    # (2) uniform noise
    Y = rng.uniform(0, 1, (4500, 4))
    _, _, inr2 = kmeans(Y, 3, rng); ev2 = explained_var(Y, inr2); nev2 = null_ev(Y, 3, rng)
    noise_ok = (ev2 - nev2) < 0.15
    print(f"noise: EV real={ev2:.3f} null={nev2:.3f} gap={ev2-nev2:+.3f} (no-structure={noise_ok})")
    ok = blob_ok and noise_ok
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default=None)
    ap.add_argument("--tf", default=None, choices=TFS)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    c = cfg()
    pairs = [a.symbol] if a.symbol else c["pairs"]
    return run(pairs, TFS)


if __name__ == "__main__":
    raise SystemExit(main())
