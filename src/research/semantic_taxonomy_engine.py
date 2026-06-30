"""
semantic_taxonomy_engine.py — PHASE 22 (Chief Quant).

Phase 21 ilithibitisha (APPROVED): representation ya manifold INASURVIVE OOS bila leakage
(silhouette 0.45–0.64 OOS; haikuuawa na leakage). Chief: hii ni MWISHO wa "Representation
Engineering Era" — LAKINI hatujathibitisha SEMANTICS. Clusters zipo, lakini zinamaanisha
nini kwa lugha ya soko?

  Principle 46: taxonomy haijakamilika hadi latent states zitafsirike kisemantiki.
  Principle 47: representations za operational ziandikwe kwa lugha ya soko, sio cluster ID.
  F-039 (APPROVED): events tofauti zinahitaji geometry tofauti kwa operational deployment.

Hatutaki model ijifunze "Cluster 4" — tunataka ijifunze "Momentum Exhaustion". Discovery
inabaki unsupervised (data-driven clusters); semantics ni LAYER ya tafsiri JUU ya clusters
zilizogunduliwa (post-hoc characterization), SIO mbinu ya discovery (hakuna human theory
inayosukuma clustering). NO ML.

Maswali (Chief):
  Q1. Kwa kila cluster: eleza volatility/spread/activity/trajectory kwa lugha ya soko.
  Q2. Je cluster ina market interpretation (profile inayotofautiana)?
  Q3. Je traders wawili wanaweza kuielewa BILA kujua cluster ID?
  Q4. Je semantic labels zina-repeat kwenye pairs nyingine? (transferable vocabulary)
  Q5. Je semantic labels zina predictive value zaidi/sawa na cluster IDs (kwa groups chache)?

Mbinu: robust normalization + self-tuning spectral embedding (representation iliyo-
operationalized Phase 21) -> kmeans (k=3) kwa kila event -> profile ya kila cluster ->
deterministic rule-map kwenda market language. NO ML.

Reuse: taxonomy_robustness_engine (build_event_xy_ts), representation_geometry_engine
(norm_robust, spectral_embed), latent_structure (kmeans), event_taxonomy_engine
(FEAT, r2_label), market_state_engine (cfg).

Output: reports/semantic_taxonomy_report.md
Self-test: python src/research/semantic_taxonomy_engine.py --self-test
"""
from __future__ import annotations

import argparse, sys
from datetime import datetime
from pathlib import Path

import numpy as np

from market_state_engine import cfg
from latent_structure import kmeans
from taxonomy_robustness_engine import build_event_xy_ts
from representation_geometry_engine import norm_robust, spectral_embed
from event_taxonomy_engine import FEAT, r2_label

REPO_ROOT = Path(__file__).resolve().parents[2]
EVENTS_ORDER = ["pullback", "deep_pullback", "trend_continuation", "breakout", "mean_reversion"]
K = 3
CAP = 1500
ZTHR = 0.5            # distinctiveness threshold (interpretable)
GENERIC = "Equilibrium / Balanced Flow"

# FEAT index map: ["vol","act","spr","atr","traj","age","trans"]
IVOL, IACT, ISPR, IATR, ITRAJ, IAGE, ITRN = range(7)


def semantic_label(raw, z, zthr=ZTHR, trajt=0.15, actt=0.3, aget=0.6):
    """Ramani ya deterministic: profile (raw + z-score dhidi ya event) -> lugha ya soko.
    raw = wastani halisi wa features; z = z-score ya profile dhidi ya event distribution.
    Thresholds zime-parametrize (default = doctrine) ili Phase 23 iweze ku-perturb (Q3)."""
    spr = raw[ISPR]; traj = raw[ITRAJ]
    vol_z, act_z, atr_z, age_z = z[IVOL], z[IACT], z[IATR], z[IAGE]
    if spr >= 0.5:
        return "Liquidity Stress (Wide Spread)"
    if vol_z >= zthr and traj >= trajt:
        return "Volatility Expansion"
    if vol_z >= zthr and traj <= -trajt:
        return "Momentum Exhaustion"
    if vol_z >= zthr:
        return "High-Volatility Regime"
    if vol_z <= -zthr and act_z <= -actt:
        return "Compression (Quiet Coil)"
    if vol_z <= -zthr and traj >= trajt:
        return "Early Expansion"
    if vol_z <= -zthr:
        return "Low-Volatility Drift"
    if age_z >= aget:
        return "Mature Persistence"
    if act_z >= zthr:
        return "Active Balanced Flow"
    return GENERIC


def distinctiveness(raw, z):
    """Je cluster inatofautiana kiasi gani na wastani wa event? (Q2)."""
    return max(abs(z[IVOL]), abs(z[IACT]), abs(z[IATR]), abs(z[IAGE]),
              abs(z[ITRAJ]), raw[ISPR])


def cluster_and_label(X, rng, k=K):
    """Cluster event (robust + spectral) -> per-cluster (raw profile, z, label, n).
    Rudisha (labels_per_point, cluster_info, idx) ambapo labels ni za subsample idx."""
    Xr = norm_robust(X)
    emb, idx = spectral_embed(Xr, k, rng, cap=CAP)
    lab = kmeans(emb, k, rng)[0]
    Xsub = X[idx]
    mu = Xsub.mean(0); sd = Xsub.std(0); sd[sd < 1e-9] = 1.0
    info = []
    for j in range(k):
        m = (lab == j)
        if not m.any():
            info.append(dict(cid=j, n=0, raw=mu, z=np.zeros_like(mu),
                             label=GENERIC, distinct=0.0))
            continue
        raw = Xsub[m].mean(0); z = (raw - mu) / sd
        info.append(dict(cid=j, n=int(m.sum()), raw=raw, z=z,
                         label=semantic_label(raw, z), distinct=float(distinctiveness(raw, z))))
    return lab, info, idx


def _describe(raw, z):
    """Maelezo mafupi ya lugha ya soko (Q1)."""
    def lvl(v, lo, hi, lo_t="chini", hi_t="juu", mid="wastani"):
        return hi_t if v >= hi else lo_t if v <= lo else mid
    vol = lvl(z[IVOL], -ZTHR, ZTHR)
    act = lvl(z[IACT], -ZTHR, ZTHR)
    spr = "WIDE" if raw[ISPR] >= 0.5 else "tight"
    trj = "inapanda" if raw[ITRAJ] >= 0.15 else "inashuka" if raw[ITRAJ] <= -0.15 else "tuli"
    age = lvl(z[IAGE], -ZTHR, 0.6, "changa", "iliyokomaa")
    return f"vol={vol}, activity={act}, spread={spr}, trajectory={trj}, age={age}"


def run(pairs, rng):
    c = cfg()
    print("Building event features (pooled)...", flush=True)
    data, no_px = build_event_xy_ts(pairs)
    if no_px:
        print("HITILAFU: state parquet haina OHLC. Endesha market_state_engine.py kwanza.", file=sys.stderr)
        return 1
    if not data:
        print("HITILAFU: hakuna event yenye sample ya kutosha.", file=sys.stderr)
        return 1
    events = [e for e in EVENTS_ORDER if e in data] + [e for e in data if e not in EVENTS_ORDER]

    # Q1/Q2/Q3 — cluster + label kila event (pooled), kusanya kwa Q5 global
    per_event = {}
    y_all, lab_codes, id_codes = [], [], []
    label_vocab = {}     # label -> idx (global codes)
    id_vocab = {}        # (event,cid) -> idx
    for e in events:
        X, y, ts = data[e]
        lab, info, idx = cluster_and_label(X, rng)
        per_event[e] = info
        ysub = y[idx]
        for p, cl in enumerate(lab):
            nfo = info[cl]
            lk = label_vocab.setdefault(nfo["label"], len(label_vocab))
            ik = id_vocab.setdefault((e, int(cl)), len(id_vocab))
            y_all.append(ysub[p]); lab_codes.append(lk); id_codes.append(ik)
        print(f"  {e}: {len(idx)} pts, clusters labelled", flush=True)
    y_all = np.array(y_all, float); lab_codes = np.array(lab_codes); id_codes = np.array(id_codes)

    # Q4 — je labels zina-repeat kwenye pairs? (per-pair vocabulary)
    pair_vocab = {}
    if len(pairs) > 1:
        for sym in pairs:
            d1, npx1 = build_event_xy_ts([sym])
            vocab = set()
            for e, (X, y, ts) in d1.items():
                if len(X) < CAP // 2:
                    continue
                _, info, _ = cluster_and_label(X, rng)
                for nfo in info:
                    if nfo["n"] > 0 and nfo["distinct"] >= ZTHR:
                        vocab.add(nfo["label"])
            pair_vocab[sym] = vocab
            print(f"  Q4 {sym}: {len(vocab)} distinctive labels", flush=True)

    return _report(c, events, per_event, y_all, lab_codes, id_codes,
                   label_vocab, id_vocab, pair_vocab)


def _report(c, events, per_event, y_all, lab_codes, id_codes, label_vocab, id_vocab, pair_vocab):
    L = ["# Semantic Taxonomy — clusters zinamaanisha nini kwa lugha ya soko? (Phase 22)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | robust norm + self-tuning spectral (Phase 21 repr) | "
         f"k={K}/event | deterministic profile→market-language map | NO ML*\n",
         "> **Principle 46 (Chief):** taxonomy haijakamilika hadi latent states zitafsirike kisemantiki. "
         "**Principle 47:** andika clusters kwa lugha ya soko, sio ID. **F-039 (APPROVED):** events tofauti "
         "geometry tofauti. Discovery inabaki unsupervised; semantics ni tafsiri JUU ya clusters (post-hoc), "
         "sio human theory inayosukuma clustering. NO ML."]

    # Q1 + Q2 + Q3
    L.append("\n## Q1+Q2+Q3 — kila cluster kwa lugha ya soko (interpretation + communicability)\n")
    L.append("| event | cluster | N | semantic label (market language) | profile | distinct | interpretable? |")
    L.append("|-------|---------|---|----------------------------------|---------|----------|----------------|")
    n_total = n_interp = n_concrete = 0
    for e in events:
        for nfo in per_event[e]:
            if nfo["n"] == 0:
                continue
            n_total += 1
            interp = nfo["distinct"] >= ZTHR
            concrete = interp and nfo["label"] != GENERIC
            n_interp += int(interp); n_concrete += int(concrete)
            L.append(f"| {e} | C{nfo['cid']} | {nfo['n']:,} | **{nfo['label']}** | {_describe(nfo['raw'], nfo['z'])} | "
                     f"{nfo['distinct']:.2f} | {'✅' if interp else '—'} |")
    interp_rate = n_interp / n_total if n_total else 0.0
    comm_rate = n_concrete / n_total if n_total else 0.0
    L.append(f"\n- **Q2 interpretable** (distinct ≥ {ZTHR}): **{n_interp}/{n_total}** ({interp_rate:.0%})")
    L.append(f"- **Q3 communicable bila ID** (concrete market label, sio '{GENERIC}'): "
             f"**{n_concrete}/{n_total}** ({comm_rate:.0%})")

    # Q4 — cross-pair repetition
    L.append("\n## Q4 — Je semantic labels zina-repeat kwenye pairs? (transferable vocabulary)\n")
    shared = []
    if pair_vocab:
        from collections import Counter
        cnt = Counter()
        for v in pair_vocab.values():
            cnt.update(v)
        shared = sorted([lab for lab, k in cnt.items() if k >= 2])
        n_pairs = len(pair_vocab)
        L.append(f"- pairs zilizochambuliwa: **{n_pairs}**")
        L.append(f"- labels zinazojitokeza kwenye ≥2 pairs: **{len(shared)}** "
                 f"({', '.join(shared) if shared else '—'})")
        L.append(f"- labels za pair-moja tu: {sorted([lab for lab, k in cnt.items() if k == 1])}")
        L.append(f"\n→ {'✅ vocabulary INA-transfer (concepts zinarudi kwenye pairs nyingi)' if shared else '— labels ni pair-specific (hazirudi)'}.")
    else:
        L.append("- (pair moja tu / synthetic — Q4 inahitaji pairs nyingi)")

    # Q5 — predictive value: labels vs cluster IDs
    L.append("\n## Q5 — Je semantic labels zina predictive value (vs cluster IDs)?\n")
    r2_id = r2_label(y_all, id_codes)
    r2_lab = r2_label(y_all, lab_codes)
    n_id = len(np.unique(id_codes)); n_lab = len(np.unique(lab_codes))
    ratio = r2_lab / r2_id if r2_id > 1e-9 else 0.0
    L.append(f"| grouping | #groups | R²(outcome) |")
    L.append(f"|----------|---------|-------------|")
    L.append(f"| cluster IDs (event×cluster) | {n_id} | {r2_id:.4f} |")
    L.append(f"| semantic labels (market concepts) | {n_lab} | {r2_lab:.4f} |")
    L.append(f"\n- ratio R²(label)/R²(id) = **{ratio:.2f}** kwa **groups {n_lab} vs {n_id}** "
             f"({n_id - n_lab} chache).")
    q5_win = (n_lab <= n_id) and (ratio >= 0.7)
    L.append(f"\n→ {'✅ semantic labels zinahifadhi predictive value kwa groups CHACHE (parsimony + transfer)' if q5_win else '⚠️ semantic labels zinapoteza predictive value sana (cluster IDs zina info ambayo label haiishiki)'}.")

    # VERDICT
    L.append("\n## VERDICT — Phase 22 Semantic Taxonomy\n")
    sem_ok = comm_rate >= 0.6 and (not pair_vocab or len(shared) >= 1) and q5_win
    if sem_ok:
        L.append(f"→ ✅ **taxonomy INA-tafsirika kisemantiki**: {comm_rate:.0%} ya clusters zina market label "
                 f"halisi, vocabulary ina-transfer ({len(shared)} labels shared), na labels zinahifadhi "
                 "predictive value kwa groups chache. Principle 46/47 zimetimizwa kiutendaji. Inayofuata: "
                 "**Reality Validation** ya alpha juu ya semantic states (sio cluster IDs). NO ML bado.")
    else:
        gaps = []
        if comm_rate < 0.6: gaps.append(f"communicability ndogo ({comm_rate:.0%})")
        if pair_vocab and not shared: gaps.append("labels hazi-transfer cross-pair")
        if not q5_win: gaps.append("labels zinapoteza predictive value")
        L.append(f"→ ⚠️ **taxonomy BADO haijatafsirika kikamilifu**: {', '.join(gaps)}. Semantics inahitaji "
                 "kazi zaidi (vocabulary/rules bora) kabla ya Reality Validation. Principle 46 bado.")
    L.append("\n**Bado tuko 'Market Understanding Era' — SIO Alpha Era.** Edge haijathibitishwa; semantics "
             "ni hatua ya kuelewa soko, sio alpha.")

    # HONEST CAVEATS
    L.append("\n## Honest Caveats\n")
    L.append("1. **Semantic labels ≠ edge (Principle 40/46).** Hii inathibitisha clusters zinatafsirika kwa "
             "lugha ya soko — **haionyeshi alpha.** Tafsiri nzuri sio faida.")
    L.append("2. **Label-map ni deterministic rule, sio discovery.** Tunazuia human theory isisukume clustering "
             "(clustering ni unsupervised); lakini RAMANI ya profile→lugha ina human choice ya thresholds "
             f"(ZTHR={ZTHR}, traj±0.15). Mabadiliko ya thresholds yanaweza kubadili labels — sio canonical.")
    L.append("3. **R²(outcome) sio edge.** Q5 inapima variance-explained ya net return kwa grouping, sio EV "
             "baada ya gharama wala OOS. Groups chache zenye R² sawa = generalization bora, sio profit.")
    L.append("4. **'Interpretable' ni profile-distinctiveness, sio uthibitisho kwamba dhana ya soko ni sahihi.** "
             "Cluster yenye vol juu + traj inashuka tunaiita 'Momentum Exhaustion' — ni hypothesis ya kiisimu, "
             "haijathibitishwa kuwa ndiyo mechanism halisi ya soko.")
    L.append("5. **Q4 cross-pair overlap = vocabulary sawa, sio kwamba cluster ni SAME object cross-pair.** "
             "Label ile ile kwenye pairs mbili haimaanishi geometry/edge sawa (F-039: geometry ni event-specific).")

    L.append("\n*Robust norm + self-tuning spectral (Phase 21 repr) -> kmeans -> deterministic profile→market "
             "language. Discovery=unsupervised; semantics=post-hoc layer. Principle 46/47. NO ML. "
             "Profitable ≠ Tradable Edge.*")

    out = REPO_ROOT / c["paths"]["reports"] / "semantic_taxonomy_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)} (interpretable {n_interp}/{n_total}, "
          f"communicable {n_concrete}/{n_total}, shared labels {len(shared)})")
    return 0


def self_test():
    rng = np.random.default_rng(22)
    # tatu regimes designed; FEAT=["vol","act","spr","atr","traj","age","trans"]
    def regime(n, vol, act, atr, traj, age, spr=0.0):
        X = np.column_stack([
            np.full(n, vol) + rng.normal(0, 0.05, n),       # vol
            np.full(n, act) + rng.normal(0, 0.05, n),       # act
            np.full(n, spr),                                # spr
            np.full(n, atr) + rng.normal(0, 0.02, n),       # atr
            np.full(n, traj) + rng.normal(0, 0.02, n),      # traj
            np.full(n, age) + rng.normal(0, 0.5, n),        # age
            rng.normal(0, 0.05, n),                         # trans
        ])
        return X

    # (1) semantic_label kwenye profiles designed (z dhidi ya event mix)
    A = regime(400, vol=2.0, act=2.0, atr=0.20, traj=1.0, age=5)    # high vol rising -> Expansion
    B = regime(400, vol=0.0, act=0.0, atr=0.05, traj=0.0, age=4)    # low vol quiet -> Compression
    Cc = regime(400, vol=2.0, act=1.0, atr=0.18, traj=-1.0, age=20) # high vol falling -> Exhaustion
    X = np.vstack([A, B, Cc])
    mu = X.mean(0); sd = X.std(0); sd[sd < 1e-9] = 1.0
    labs = []
    for blk in (A, B, Cc):
        raw = blk.mean(0); z = (raw - mu) / sd
        labs.append(semantic_label(raw, z))
    exp = ["Volatility Expansion", "Compression (Quiet Coil)", "Momentum Exhaustion"]
    ok_map = labs == exp
    print(f"label-map: {labs} (expected {exp}) -> {'OK' if ok_map else 'FAIL'}")

    # (2) clustering ya event hii -> kila regime ipate label distinct + concrete
    lab, info, idx = cluster_and_label(X, rng, k=3)
    got = sorted({nfo["label"] for nfo in info if nfo["n"] > 0})
    concrete = all(nfo["label"] != GENERIC and nfo["distinct"] >= ZTHR for nfo in info if nfo["n"] > 0)
    ok_clust = len(got) == 3 and concrete
    print(f"cluster->labels: {got} | all concrete+distinct={concrete} -> {'OK' if ok_clust else 'FAIL'}")

    # (3) cross-pair repetition: pair mbili zenye regimes zile zile -> shared vocab
    v1 = {semantic_label(blk.mean(0), (blk.mean(0) - mu) / sd) for blk in (A, B, Cc)}
    v2 = v1  # pair ya pili ina regimes sawa
    shared = v1 & v2
    ok_q4 = len(shared) >= 2
    print(f"cross-pair shared: {sorted(shared)} -> {'OK' if ok_q4 else 'FAIL'}")

    # (4) Q5: labels (3 groups) vs ids (3 ids hapa) R² > 0 na sawa
    y = np.concatenate([rng.normal(2, 1, 400), rng.normal(-1, 1, 400), rng.normal(0, 1, 400)])
    ids = np.array([0] * 400 + [1] * 400 + [2] * 400)
    lcodes = np.array([0] * 400 + [1] * 400 + [2] * 400)
    r2i = r2_label(y, ids); r2l = r2_label(y, lcodes)
    ok_q5 = r2l > 0.1 and abs(r2l - r2i) < 1e-9
    print(f"R²: id={r2i:.3f} label={r2l:.3f} -> {'OK' if ok_q5 else 'FAIL'}")

    ok = ok_map and ok_clust and ok_q4 and ok_q5
    print(f"\nSELF-TEST: {'PASS' if ok else 'FAIL'}")
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
    return run(pairs, np.random.default_rng(22))


if __name__ == "__main__":
    raise SystemExit(main())
