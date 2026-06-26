"""
rare_state_analysis.py — PHASE 5.10 (Chief Quant). Rare State Analysis.

Phase 5.9A (F-016): latent market structures zipo (k=4). Cluster C1 ilikuwa ~1%
TU. Chief (F-017 hypothesis): **Rare States may carry disproportionately high
information** — institutional quant hawajali common clusters; wanajali RARE
regimes (crash/news/liquidity vacuum = 1% lakini zinaamua performance).

Sasa hatutafuti ENTRY. Tunatafuta MARKET CONFIGURATION:
    Trade si signal. Trade ni consequence ya market configuration.

Phase 5.10 inazingatia CLUSTER NDOGO ZAIDI (rare) na kuichunguza:
  • frequency (overall + per pair)
  • feature signature (vol/act/spread/lifecycle/transition) vs global
  • raw state composition (volatility/activity/spread states)
  • duration (run length: bars mfululizo ndani ya rare state)
  • exit distribution (rare state inakwenda cluster gani?)
  • return distribution (kama close ipo): je rare state ina payoff/dispersion tofauti?

> Cluster ≠ State (Chief): hatuipi jina; tunaichunguza tabia. NO ML, NO human
> taxonomy. Inasoma state parquet (cached). Returns zinahitaji 'c' kwenye parquet
> (endesha market_state_engine baada ya update ya OHLC); vinginevyo structure tu.

Reuse: market_state_engine(cfg,pip), latent_structure(kmeans, FEAT, K…),
mechanism_discovery.signatures.

Output: reports/rare_state_analysis.md
Endesha: python src/research/rare_state_analysis.py
Self-test: python src/research/rare_state_analysis.py --self-test
"""
from __future__ import annotations

import argparse, sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np
import polars as pl

from market_state_engine import cfg, pip
from mechanism_discovery import signatures, SIG_DIM
from latent_structure import kmeans, FEAT, CAP_PER_PAIR, state_path

REPO_ROOT = Path(__file__).resolve().parents[2]
TFS = ["H1", "H2", "H4", "D1"]
K = 4                  # latent clusters (Phase 5.9A best k)
HORIZON = 6            # forward bars kwa return distribution
LEVELS = ["LOW", "NORMAL", "HIGH"]
_posix = lambda p: str(p).replace("\\", "/")


def read_series(sym):
    """Rudisha list ya dict per TF: sig[finite], vs, acts, sprs, close(or None), ts."""
    out = []
    for tf in TFS:
        p = state_path(sym, tf)
        if not p.exists():
            continue
        df = pl.read_parquet(p)
        sig, vs, acts, *_ = signatures(df, pip(sym))
        m = np.all(np.isfinite(sig), axis=1)
        d = dict(sig=sig[m],
                 vs=[v for v, k in zip(vs, m) if k],
                 acts=[a for a, k in zip(acts, m) if k],
                 sprs=[s for s, k in zip(df["spread_state"].to_list(), m) if k],
                 close=(df["c"].to_numpy()[m] / pip(sym)) if "c" in df.columns else None)
        out.append(d)
    return out


def assign(sig, cen):
    return ((sig[:, None, :] - cen[None, :, :]) ** 2).sum(2).argmin(1)


def runs(labels, target):
    """Run lengths za bars mfululizo == target, + cluster inayofuata (exit)."""
    lengths = []; exits = []
    i = 0; n = len(labels)
    while i < n:
        if labels[i] == target:
            j = i
            while j < n and labels[j] == target:
                j += 1
            lengths.append(j - i)
            if j < n:
                exits.append(int(labels[j]))
            i = j
        else:
            i += 1
    return lengths, exits


def run(pairs, tfs):
    c = cfg(); rng = np.random.default_rng(0)
    series = {}; pool = []
    for sym in pairs:
        s = read_series(sym)
        if not s:
            print(f"  {sym}: (hakuna state parquet)"); continue
        series[sym] = s
        for d in s:
            X = d["sig"]
            pool.append(X[rng.choice(len(X), min(len(X), CAP_PER_PAIR), replace=False)] if len(X) else X)
        print(f"  {sym}: TFs={len(s)}", flush=True)
    if not series:
        print("HITILAFU: hakuna state parquet. Endesha market_state_engine.py kwanza.", file=sys.stderr)
        return 1
    Xp = np.vstack([p for p in pool if len(p)])
    lab, cen, _ = kmeans(Xp, K, rng)
    # rare = cluster ndogo zaidi (global)
    glob = Counter(lab.tolist()); rare = min(glob, key=glob.get)
    print(f"  clusters (sample): {dict(glob)} -> rare = C{rare}", flush=True)

    # accumulate rare-state stats kuvuka series zote
    prof_rare = np.zeros(SIG_DIM); n_rare = 0; prof_all = np.zeros(SIG_DIM); n_all = 0
    comp = {dim: Counter() for dim in ("vs", "acts", "sprs")}
    durations = []; exits = Counter(); per_pair_rate = {}
    ret_rare = []; ret_other = []
    for sym, s in series.items():
        pr_n = 0; pr_tot = 0
        for d in s:
            L = assign(d["sig"], cen); pr_tot += len(L)
            prof_all += d["sig"].sum(0); n_all += len(d["sig"])
            mr = L == rare; pr_n += int(mr.sum())
            prof_rare += d["sig"][mr].sum(0); n_rare += int(mr.sum())
            for dim, key in (("vs", "vs"), ("acts", "acts"), ("sprs", "sprs")):
                for x, k in zip(d[key], mr):
                    if k:
                        comp[dim][x] += 1
            ln, ex = runs(L, rare); durations += ln; exits.update(ex)
            if d["close"] is not None and len(d["close"]) > HORIZON:
                cl = d["close"]; fwd = np.full(len(cl), np.nan)
                fwd[:-HORIZON] = np.abs(cl[HORIZON:] - cl[:-HORIZON])     # |H-bar move| pips
                rr = fwd[mr]; ro = fwd[~mr]
                ret_rare += rr[np.isfinite(rr)].tolist(); ret_other += ro[np.isfinite(ro)].tolist()
        per_pair_rate[sym] = 100 * pr_n / pr_tot if pr_tot else 0.0

    pr = prof_rare / max(n_rare, 1); pa = prof_all / max(n_all, 1)
    L = ["# Rare State Analysis — market configuration ya cluster nadra (Phase 5.10)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | latent k={K} | rare cluster = C{rare} (ndogo zaidi) | "
         f"profile/duration/exit/returns | NO labels za binadamu | rare bars={n_rare:,}/{n_all:,}*\n",
         "> **F-017 (Chief):** rare states zinaweza kubeba INFORMATION nyingi (crash/news/liquidity = 1% "
         "lakini zinaamua performance). Trade = consequence ya MARKET CONFIGURATION, sio signal. "
         "Cluster ≠ State — tunachunguza tabia, hatuipi jina. NO ML.\n",
         f"## 1) Frequency — rare C{rare} = **{100*n_rare/max(n_all,1):.1f}%** ya bars\n",
         "| pair | rate % |", "|------|--------|"]
    for sym, r in per_pair_rate.items():
        L.append(f"| {sym} | {r:.1f}% |")

    L.append(f"\n## 2) Feature signature — rare C{rare} vs global (mean, per-pair z)\n")
    L.append("| feature | rare | global | Δ |")
    L.append("|---------|------|--------|---|")
    for i, f in enumerate(FEAT):
        L.append(f"| {f} | {pr[i]:+.2f} | {pa[i]:+.2f} | {pr[i]-pa[i]:+.2f} |")

    L.append(f"\n## 3) Raw state composition ndani ya rare C{rare}\n")
    L.append("| dimension | distribution |")
    L.append("|-----------|--------------|")
    for dim, lab_name in (("vs", "volatility"), ("acts", "activity"), ("sprs", "spread")):
        tot = sum(comp[dim].values()) or 1
        dist = " · ".join(f"{kk} {100*vv/tot:.0f}%" for kk, vv in comp[dim].most_common())
        L.append(f"| {lab_name} | {dist} |")

    L.append(f"\n## 4) Duration (run length, bars) + exit distribution\n")
    if durations:
        a = np.array(durations)
        L.append(f"- duration: median **{np.median(a):.0f}** | mean {a.mean():.1f} | p90 {np.percentile(a,90):.0f} "
                 f"| max {a.max()} | n_runs {len(a):,}")
        tote = sum(exits.values()) or 1
        ex = " · ".join(f"C{kk} {100*vv/tote:.0f}%" for kk, vv in exits.most_common())
        L.append(f"- exit → {ex}")
    else:
        L.append("- (hakuna runs)")

    L.append(f"\n## 5) Return distribution (|{HORIZON}-bar move| pips): rare vs non-rare\n")
    if ret_rare and ret_other:
        rr = np.array(ret_rare); ro = np.array(ret_other)
        L.append("| set | n | mean | median | p95 | p99 |")
        L.append("|-----|---|------|--------|-----|-----|")
        for nm, x in (("rare", rr), ("non-rare", ro)):
            L.append(f"| {nm} | {len(x):,} | {x.mean():.1f} | {np.median(x):.1f} | "
                     f"{np.percentile(x,95):.0f} | {np.percentile(x,99):.0f} |")
        ratio = rr.mean() / ro.mean() if ro.mean() > 0 else float("nan")
        L.append(f"\n→ rare/non-rare mean move ratio = **{ratio:.2f}×** "
                 f"({'✅ rare ina dispersion kubwa zaidi (F-017)' if ratio > 1.3 else '— sawa-sawa'})")
    else:
        L.append("*(close haipo kwenye state parquet — endesha market_state_engine baada ya update ya "
                 "OHLC ili kupata return distribution. Structure (1–4) imekamilika.)*")

    L.append("\n---\n*Rare cluster ni MARKET CONFIGURATION, sio jina. F-017: rare states zikiwa na "
             "dispersion/return kubwa zaidi = high information. Hatuanzi Opportunity Engine; kwanza "
             "tunajua rare state inafanya nini (Configuration thinking). Cluster ≠ State (Latent State "
             "CANDIDATE). NO ML, NO human taxonomy. Inayofuata: Cluster Robustness (5.11), Validation (5.12).*")
    out = REPO_ROOT / c["paths"]["reports"] / "rare_state_analysis.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """(1) runs(): run lengths + exits sahihi. (2) assign(): nearest centroid.
       (3) rare cluster = ndogo zaidi kwenye blobs zenye uwiano tofauti."""
    L = np.array([2, 2, 0, 0, 0, 2, 2, 2, 1])
    ln, ex = runs(L, 2)
    runs_ok = (ln == [2, 3] and ex == [0, 1])
    print(f"runs: lengths={ln} exits={ex} (ok={runs_ok})")
    cen = np.array([[0, 0], [10, 10]], float)
    asg = assign(np.array([[0.1, 0.1], [9, 9], [0.2, 0]], float), cen)
    asg_ok = list(asg) == [0, 1, 0]
    print(f"assign: {list(asg)} (ok={asg_ok})")
    rng = np.random.default_rng(0)
    X = np.vstack([rng.normal(0, 0.4, (3000, 3)), rng.normal(8, 0.4, (3000, 3)),
                   rng.normal(40, 0.4, (120, 3))])                      # cluster 3 = rare, far apart
    lab, cen2, _ = kmeans(X, 3, rng)
    from collections import Counter as C
    g = C(lab.tolist()); rare = min(g, key=g.get)
    rare_ok = g[rare] < 300
    print(f"rare cluster size={g[rare]} (rare detected={rare_ok})")
    ok = runs_ok and asg_ok and rare_ok
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
    return run(pairs, TFS)


if __name__ == "__main__":
    raise SystemExit(main())
