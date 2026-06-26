"""
representation_robustness.py — PHASE 5.11B (Chief Quant). Representation Robustness.

Phase 5.11 (Cluster Robustness) HAIKUIDHINISHWA: KMeans vs GMM vs Agglomerative
ARI ≈ 0.12 (Agglomerative ilianguka cluster moja 98%). Lakini Chief: "algorithm
independent" ni kali mno — KMeans(spherical)/GMM(elliptical)/Agglomerative(tree)
zina assumption tofauti, hazipaswi kutoa clusters zile zile.

Amendment (F-018): **Representation Robustness > Cluster Identity.** Swali sahihi
sio "KMeans vs GMM"; ni: **tukibadilisha REPRESENTATION, latent structures
zinabaki?**

Tunajaribu representations 4 (algorithm moja: KMeans k=4) kwa features ZILE ZILE:
  • zscore      : (x − mean)/std
  • robust      : (x − median)/(1.4826·MAD)
  • percentile  : ECDF rank ∈ [0,1]
  • rolling     : rolling-window z (per series, order-aware)

Kwa kila representation: KMeans -> EV gap vs permutation null (structure ipo?)
+ cross-representation **ARI** (assignments zinakubaliana kuvuka encodings?).

Verdict: REPRESENTATION-ROBUST ikiwa structure inabaki (EV gap>0) kwa zote NA
ARI ya juu kuvuka representations -> latent structures si artifact ya encoding
moja (F-018; kuelekea Principle 18 iliyorekebishwa).

> NO sklearn, NO ML. Inasoma state parquet. Economic-meaning matching kamili
> inahitaji payoff (Phase 5.10R / OHLC); hapa ni structural persistence.

Reuse: latent_structure(kmeans, explained_var, null_ev, state_path, CAP_PER_PAIR),
cluster_robustness(ari), state_context_engine(context_for_dim, _bidx).

Output: reports/representation_robustness_report.md
Self-test: python src/research/representation_robustness.py --self-test
"""
from __future__ import annotations

import argparse, sys
from datetime import datetime
from pathlib import Path

import numpy as np
import polars as pl

from market_state_engine import cfg, pip
from state_context_engine import context_for_dim, _bidx
from latent_structure import kmeans, explained_var, null_ev, state_path, CAP_PER_PAIR
from cluster_robustness import ari

REPO_ROOT = Path(__file__).resolve().parents[2]
TFS = ["H1", "H2", "H4", "D1"]
K = 4
ROLL_W = 500
FEAT = ["atr", "atr_slope", "tc", "tc_slope", "spr", "transition", "lifecycle"]
REPS = ["zscore", "robust", "percentile", "rolling"]
_posix = lambda p: str(p).replace("\\", "/")


def _slope_raw(x, k=5):
    n = len(x); out = np.zeros(n)
    cs = np.concatenate([[0.0], np.cumsum(x)])
    for i in range(n):
        lo = max(0, i - k)
        out[i] = x[i] - (cs[i] - cs[lo]) / (i - lo) if i > lo else 0.0
    return out


def _rolling_z(x, w=ROLL_W):
    n = len(x); cs = np.concatenate([[0.0], np.cumsum(x)]); cs2 = np.concatenate([[0.0], np.cumsum(x * x)])
    idx = np.arange(n); lo = np.maximum(0, idx - w + 1); cnt = (idx - lo + 1).astype(float)
    m = (cs[idx + 1] - cs[lo]) / cnt
    v = (cs2[idx + 1] - cs2[lo]) / cnt - m * m
    sd = np.sqrt(np.maximum(v, 0.0))
    return np.where(sd > 1e-9, (x - m) / sd, 0.0)


def raw_features(df, pp):
    """Rudisha (R_raw[N×7], R_roll[N×7]) per series (finite rows)."""
    atr = df["atr"].to_numpy() / pp; tc = df["tc"].to_numpy().astype(float)
    spr = df["spr"].to_numpy(); spr = np.where(np.isfinite(spr), spr, np.nanmedian(spr))
    vs = df["volatility_state"].to_list()
    vage, vpchg = context_for_dim(vs)
    age_n = np.array([_bidx(int(a)) / 3.0 if a > 0 else np.nan for a in vage])
    pchg = np.where(np.isfinite(vpchg), vpchg, np.nan)
    cols = [atr, _slope_raw(atr), tc, _slope_raw(tc), spr, pchg, age_n]
    R = np.column_stack(cols)
    Rroll = np.column_stack([_rolling_z(c) for c in cols])
    m = np.all(np.isfinite(R), axis=1) & np.all(np.isfinite(Rroll), axis=1)
    return R[m], Rroll[m]


def enc_zscore(R):
    mu = R.mean(0); sd = R.std(0); sd[sd < 1e-12] = 1.0
    return (R - mu) / sd


def enc_robust(R):
    med = np.median(R, 0); mad = np.median(np.abs(R - med), 0) * 1.4826; mad[mad < 1e-12] = 1.0
    return (R - med) / mad


def enc_percentile(R):
    out = np.empty_like(R)
    for j in range(R.shape[1]):
        order = np.argsort(R[:, j], kind="mergesort"); ranks = np.empty(len(R))
        ranks[order] = np.arange(len(R)); out[:, j] = ranks / max(len(R) - 1, 1)
    return out


def collect_raw(sym, rng):
    Rs = []; RRs = []
    for tf in TFS:
        p = state_path(sym, tf)
        if not p.exists():
            continue
        R, RR = raw_features(pl.read_parquet(p), pip(sym))
        if len(R):
            Rs.append(R); RRs.append(RR)
    if not Rs:
        return None, None
    R = np.vstack(Rs); RR = np.vstack(RRs)
    if len(R) > CAP_PER_PAIR:
        idx = rng.choice(len(R), CAP_PER_PAIR, replace=False); R = R[idx]; RR = RR[idx]
    return R, RR


def run(pairs, tfs):
    c = cfg(); rng = np.random.default_rng(0); Rs = []; RRs = []
    for sym in pairs:
        print(f"  {sym}: nasoma state parquet...", flush=True)
        R, RR = collect_raw(sym, rng)
        if R is not None:
            Rs.append(R); RRs.append(RR)
        print(f"    vectors={0 if R is None else len(R)}")
    if not Rs:
        print("HITILAFU: hakuna state parquet. Endesha market_state_engine.py kwanza.", file=sys.stderr)
        return 1
    R = np.vstack(Rs); RR = np.vstack(RRs)
    # representations (zote kwenye points ZILE ZILE)
    reps = {"zscore": enc_zscore(R), "robust": enc_robust(R),
            "percentile": enc_percentile(R), "rolling": enc_zscore(RR)}
    labels = {}; ev = {}; nev = {}
    for nm, X in reps.items():
        lab, cen, inr = kmeans(X, K, rng)
        labels[nm] = lab; ev[nm] = explained_var(X, inr); nev[nm] = null_ev(X, K, rng)
        print(f"  {nm}: EV={ev[nm]:.3f} null={nev[nm]:.3f}", flush=True)

    L = ["# Representation Robustness — latent structures zinabaki kuvuka encodings? (Phase 5.11B)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | representations: {', '.join(REPS)} | algorithm moja (KMeans "
         f"k={K}) | structure = EV vs null; agreement = cross-representation ARI | N={len(R):,}*\n",
         "> **F-018 (Chief):** 'algorithm independent' ni kali mno. Swali sahihi: tukibadilisha "
         "REPRESENTATION (zscore/robust/percentile/rolling), latent structures zinabaki? Structure "
         "ikidumu + ARI ya juu kuvuka encodings -> robust (sio artifact ya encoding moja). NO ML.\n",
         "## Structure persistence — EV real vs permutation null\n",
         "| representation | EV real | EV null | gap | structure? |",
         "|----------------|---------|---------|-----|------------|"]
    persist = 0
    for nm in REPS:
        g = ev[nm] - nev[nm]; ok = g > 0.10; persist += ok
        L.append(f"| {nm} | {ev[nm]:.3f} | {nev[nm]:.3f} | {g:+.3f} | {'✅' if ok else '—'} |")

    L.append("\n## Cross-representation agreement — ARI (cluster assignments)\n")
    L.append("| pair | ARI |")
    L.append("|------|-----|")
    aris = []
    for i in range(len(REPS)):
        for j in range(i + 1, len(REPS)):
            v = ari(labels[REPS[i]], labels[REPS[j]]); aris.append(v)
            L.append(f"| {REPS[i]} ↔ {REPS[j]} | {v:+.2f} |")
    mean_ari = float(np.mean(aris)) if aris else float("nan")

    L.append(f"\n## VERDICT — F-018: latent structures ni representation-robust?\n")
    robust = persist >= 3 and mean_ari >= 0.4
    L.append(f"- structure inadumu kwa **{persist}/{len(REPS)}** representations | mean cross-rep ARI = "
             f"**{mean_ari:+.2f}**")
    if robust:
        L.append("\n→ ✅ **REPRESENTATION-ROBUST**: latent structures zinabaki kuvuka encodings tofauti "
                 "na assignments zinakubaliana (ARI ≥ 0.4). Si artifact ya encoding moja → Latent State "
                 "Candidates zinaweza kuendelea (kuelekea economic-meaning validation kwa payoff).")
    else:
        L.append("\n→ ⚠️ **HAZIJA-ROBUST vya kutosha**: structure au agreement inategemea encoding "
                 f"(persist {persist}/{len(REPS)}, ARI {mean_ari:+.2f}). Inahitaji feature/representation bora.")
    L.append("\n*Representation robustness (F-018) > cluster identity: tunabadilisha ENCODING, sio "
             "algorithm. Structure ikidumu kuvuka zscore/robust/percentile/rolling = si artifact. "
             "Economic-meaning matching KAMILI (Principle 18 iliyorekebishwa) inahitaji payoff "
             "(Phase 5.10R/5.12). NO ML. Profitable ≠ Tradable Edge.*")
    out = REPO_ROOT / c["paths"]["reports"] / "representation_robustness_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)} | persist={persist}/{len(REPS)} ARI={mean_ari:+.2f}")
    return 0


def self_test():
    """3 blobs separable -> structure inabaki + ARI ya juu kuvuka zscore/robust/percentile."""
    rng = np.random.default_rng(0)
    R = np.vstack([rng.normal(0, 0.5, (400, 5)), rng.normal(8, 0.5, (400, 5)),
                   rng.normal([0, 8, 0, 8, 0], 0.5, (400, 5))])
    reps = {"zscore": enc_zscore(R), "robust": enc_robust(R), "percentile": enc_percentile(R)}
    labs = {}; gaps = {}
    for nm, X in reps.items():
        lab, cen, inr = kmeans(X, 3, rng); labs[nm] = lab
        gaps[nm] = explained_var(X, inr) - null_ev(X, 3, rng)
    persist = all(g > 0.1 for g in gaps.values())
    aris = [ari(labs["zscore"], labs["robust"]), ari(labs["zscore"], labs["percentile"]),
            ari(labs["robust"], labs["percentile"])]
    agree = min(aris) > 0.8
    print(f"gaps: {[round(g,2) for g in gaps.values()]} (persist={persist})")
    print(f"cross-rep ARI: {[round(a,2) for a in aris]} (agree={agree})")
    # encoding sanity
    enc_ok = enc_percentile(np.array([[1.0], [3.0], [2.0]])).flatten().tolist() == [0.0, 1.0, 0.5]
    print(f"percentile encoding monotone: {enc_ok}")
    ok = persist and agree and enc_ok
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
