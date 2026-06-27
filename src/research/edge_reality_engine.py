"""
edge_reality_engine.py — PHASE 11 (Chief Quant). Edge Reality Test.

Swali la msingi zaidi kuliko yote: **je edge tunayoiona ni HALISI, au ni random
variation?** Phase 10 (F-027 APPROVED): early edge quality HAITABIRI future
persistence (ρ≈0.03). F-029 (OPEN): edge decay inaweza kuwa STOCHASTIC, sio
deterministic. Principle 28: HAKUNA adaptive system kabla ya kuthibitisha kuwa
persistent edge ipo ZAIDI ya random expectation.

Hypotheses:
  H1: Market ina real persistent edges.
  H0: Observed edge ni sampling noise.

Hatutaki kujenga Opportunity Engine / ML kabla ya kujua ipi ni kweli. Phase 11
inatumia NULL MODELS + PERMUTATION + BOOTSTRAP:

  Q1. Null model: shuffle outcomes (global) -> je survival/decay inafanana?
  Q2. Randomized order (within-config time shuffle) -> je survivability inafanana?
  Q3. Bootstrap/percentile: je observed iko NJE ya CI ya random world?
  Q4. Permutation: je Top survivors (zinazodumu windows zote) ni ZAIDI ya random?
  Q5. P(Observed Edge > Random Edge) kwa kila event.

Maamuzi: H1 (edge halisi) ikiwa survivors observed > random kwa significance
(permutation p<0.05 NA nje ya null 97.5pct). Vinginevyo H0 (noise).

⚠️ Chief: TUSISEME "kuna hidden variable" — hiyo ni kuruka hatua. Kwanza thibitisha
edge ipo kabisa. NO ML, NO Opportunity Engine bado (Principle 28).

Reuse: confidence_engine (build_acc), latent_structure (kmeans, collect),
configuration_engine (K), market_state_engine (cfg).

Output: reports/edge_reality_report.md
Self-test: python src/research/edge_reality_engine.py --self-test
"""
from __future__ import annotations

import argparse, sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np

from market_state_engine import cfg
from latent_structure import kmeans, collect
from configuration_engine import K
from confidence_engine import build_acc

REPO_ROOT = Path(__file__).resolve().parents[2]
MIN_N = 200
NWIN = 6
MIN_WIN = 25
NREP = 200            # null/permutation repetitions
SURV_PCT = 0.02       # "Top 2% survivors" reference


def win_means(net, nwin=NWIN):
    return np.array([ch.mean() for ch in np.array_split(net, nwin)])


def survival_of(net, nwin=NWIN):
    """Rudisha (survival_windows, first_pos, overall_ev)."""
    ev = win_means(net, nwin)
    sw = 0
    for e in ev:
        if e > 0:
            sw += 1
        else:
            break
    return sw, bool(ev[0] > 0), float(net.mean())


def agg(items, nwin=NWIN):
    """items = list ya (event, net_array). Rudisha takwimu za jumla za 'edge'."""
    survivors = 0; fp = 0; surv_list = []; n_pos = 0; evs = []
    ev_by_event = defaultdict(list)
    for ename, net in items:
        sw, is_fp, m = survival_of(net, nwin)
        evs.append(m); ev_by_event[ename].append(m)
        if m > 0:
            n_pos += 1
        if is_fp:
            fp += 1; surv_list.append(sw)
            if sw == nwin:
                survivors += 1
    return dict(survivors=survivors, fp=fp, mean_surv=float(np.mean(surv_list)) if surv_list else 0.0,
                n_pos=n_pos, n=len(items), ev_disp=float(np.std(evs)) if evs else 0.0,
                ev_event={k: float(np.mean(v)) for k, v in ev_by_event.items()})


def null_global(items, pool, sizes, events, rng):
    """Shuffle outcomes ZOTE (break config↔outcome) -> resplit kwa sizes."""
    perm = rng.permutation(pool); out = []; c = 0
    for sz, en in zip(sizes, events):
        out.append((en, perm[c:c + sz])); c += sz
    return agg(out)


def null_time(items, rng):
    """Shuffle ORDER ndani ya kila config (break time-persistence, keep config EV)."""
    return agg([(en, rng.permutation(net)) for en, net in items])


def _pval_ge(null_arr, obs):
    """p = P(null ≥ obs) (one-sided), na +1 smoothing."""
    null_arr = np.asarray(null_arr, float)
    return (1 + int(np.sum(null_arr >= obs))) / (len(null_arr) + 1)


def run(pairs, tfs):
    c = cfg(); rng = np.random.default_rng(0)
    pool0 = [X for sym in pairs if len(X := collect(sym, rng)) > 50]
    if not pool0:
        print("HITILAFU: hakuna state parquet. Endesha market_state_engine.py kwanza.", file=sys.stderr)
        return 1
    _, cen, _ = kmeans(np.vstack(pool0), K, rng)
    print(f"  latent clusters k={K} fitted", flush=True)
    acc, no_px = build_acc(pairs, cen)
    if no_px:
        print("HITILAFU: OHLC haipo. Endesha market_state_engine.py (OHLC update) kwanza.", file=sys.stderr)
        return 1

    items = []
    for key, rows in acc.items():
        if len(rows) < MIN_N:
            continue
        net = np.array([x[1] for x in sorted(rows, key=lambda t: t[0])], float)
        if min(len(ch) for ch in np.array_split(net, NWIN)) < MIN_WIN:
            continue
        items.append((key[1], net))
    if not items:
        print(f"HITILAFU: hakuna Configuration yenye N≥{MIN_N}.", file=sys.stderr)
        return 1

    obs = agg(items)
    pool = np.concatenate([net for _, net in items])
    sizes = [len(net) for _, net in items]; events = [en for en, _ in items]

    # null distributions
    g_surv = []; g_meansurv = []; g_npos = []; g_event = defaultdict(list)
    t_surv = []; t_meansurv = []
    for _ in range(NREP):
        ng = null_global(items, pool, sizes, events, rng)
        g_surv.append(ng["survivors"]); g_meansurv.append(ng["mean_surv"]); g_npos.append(ng["n_pos"])
        for k, v in ng["ev_event"].items():
            g_event[k].append(v)
        nt = null_time(items, rng)
        t_surv.append(nt["survivors"]); t_meansurv.append(nt["mean_surv"])
    g_surv = np.array(g_surv); t_surv = np.array(t_surv)

    # bootstrap CI ya observed survivors (resample configs)
    boot = []
    idx = np.arange(len(items))
    for _ in range(NREP):
        bs = rng.choice(idx, len(idx), replace=True)
        boot.append(agg([items[i] for i in bs])["survivors"])
    boot = np.array(boot)

    top2 = max(1, int(len(items) * SURV_PCT))
    z_g = (obs["survivors"] - g_surv.mean()) / (g_surv.std() + 1e-9)
    # permutation test ya KUWEPO kwa edge hutumia NULL-GLOBAL (huvunja config↔outcome,
    # huhifadhi marginal). NULL-TIME huhifadhi EV ya config -> si null sahihi kwa survivor
    # count (config chanya hudumu hata baada ya time-shuffle); inatumika Q2 tu (persistence).
    p_perm = _pval_ge(g_surv, obs["survivors"])
    g_lo, g_hi = np.percentile(g_surv, [2.5, 97.5])
    outside = obs["survivors"] > g_hi

    L = ["# Edge Reality Test — je edge ni HALISI au ni noise? (Phase 11)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | null models + permutation + bootstrap ({NREP} reps) | "
         f"rolling {NWIN} windows | configs N≥{MIN_N}: {len(items):,} | H1: edge halisi · H0: sampling noise*\n",
         "> **Principle 28 (Chief):** HAKUNA adaptive system kabla ya kuthibitisha persistent edge ipo ZAIDI "
         "ya random expectation. **F-027 (APPROVED):** early quality haitabiri future persistence. **F-029 "
         "(OPEN):** edge decay inaweza kuwa stochastic. Swali: je 'survivors' tulizoziona ni zaidi ya bahati? "
         "⚠️ Hatusemi 'kuna hidden variable' — kwanza thibitisha edge ipo. NO ML, NO Opportunity Engine.\n",
         f"\n**Observed:** configs={len(items):,} | first-positive={obs['fp']} | EV>0={obs['n_pos']} | "
         f"survivors ({NWIN}/{NWIN} windows)=**{obs['survivors']}** | mean survival={obs['mean_surv']:.2f} "
         f"(Top {int(SURV_PCT*100)}% ref = {top2})\n"]

    # Q1
    L.append("\n## Q1 — Null model (shuffle outcomes): je survival inafanana na bahati?\n")
    L.append(f"- observed survivors = **{obs['survivors']}** | null-global survivors = "
             f"**{g_surv.mean():.1f}** ± {g_surv.std():.1f} (mean ± sd, {NREP} reps)")
    L.append(f"- observed mean-survival = **{obs['mean_surv']:.2f}** | null-global = "
             f"**{np.mean(g_meansurv):.2f}**")
    L.append(f"\n→ {'observed ZAIDI ya null' if obs['survivors'] > g_surv.mean() else 'observed ≈/chini ya null'} "
             f"(z = {z_g:+.1f}).")

    # Q2
    L.append("\n## Q2 — Randomized order (time shuffle, keep config EV): je persistence ni halisi?\n")
    L.append(f"- observed survivors = **{obs['survivors']}** | null-time survivors = "
             f"**{t_surv.mean():.1f}** ± {t_surv.std():.1f}")
    L.append(f"- observed mean-survival = **{obs['mean_surv']:.2f}** | null-time = **{np.mean(t_meansurv):.2f}**")
    L.append(f"\n→ null-time inashika EV ya config lakini inavunja muda; tofauti = persistence ya KWELI "
             f"({'ipo' if obs['survivors'] > t_surv.mean() else 'haionekani'}).")

    # Q3
    L.append("\n## Q3 — Bootstrap / CI: je observed iko NJE ya random world?\n")
    L.append(f"- null-global 95% CI ya survivors = [{g_lo:.0f}, {g_hi:.0f}]")
    L.append(f"- observed survivors = **{obs['survivors']}** ({'NJE ya CI ✅' if outside else 'NDANI ya CI ⚠️'})")
    L.append(f"- bootstrap ya observed (resample configs): {boot.mean():.0f} ± {boot.std():.0f} "
             f"[{np.percentile(boot,2.5):.0f}, {np.percentile(boot,97.5):.0f}]")

    # Q4
    L.append("\n## Q4 — Permutation: je Top survivors ni ZAIDI ya random expectation?\n")
    L.append(f"- permutation p-value (P(null-global survivors ≥ observed)) = **{p_perm:.3f}**")
    L.append(f"\n→ {'✅ significant (p<0.05): survivors zaidi ya bahati' if p_perm < 0.05 else '⚠️ si significant (p≥0.05): survivors ndani ya bahati'}.")

    # Q5
    L.append("\n## Q5 — P(Observed Edge > Random Edge) kwa kila event\n")
    L.append("| event | observed mean EV | null mean EV | P(obs > random) |")
    L.append("|-------|------------------|--------------|-----------------|")
    n_sig_event = 0
    for en in sorted(obs["ev_event"]):
        oev = obs["ev_event"][en]; nulls = np.array(g_event[en])
        p_gt = float(np.mean(oev > nulls)) if len(nulls) else float("nan")
        n_sig_event += 1 if p_gt > 0.95 else 0
        L.append(f"| {en} | {oev:+.3f} | {nulls.mean():+.3f} | {p_gt*100:.0f}% |")
    L.append(f"\n→ events zenye P(obs>random) > 95%: **{n_sig_event}/{len(obs['ev_event'])}**.")

    # VERDICT
    H1 = (p_perm < 0.05 and outside and obs["survivors"] > g_surv.mean())
    L.append("\n## VERDICT — H1 (edge halisi) vs H0 (noise)\n")
    if H1:
        L.append(f"→ ✅ **H1 inaungwa mkono**: survivors observed ({obs['survivors']}) ZIDI ya random "
                 f"(null {g_surv.mean():.1f}, z={z_g:+.1f}, perm p={p_perm:.3f}, nje ya 95% CI). Kuna edge "
                 f"halisi inayozidi bahati — sasa (na sio kabla) ni halali kujenga Opportunity Engine/adaptive "
                 "juu ya survivors hawa (Principle 28 imetimizwa). F-029 (stochastic decay) bado inahitaji test "
                 "ya ziada.")
    else:
        L.append(f"→ ⚠️ **H0 haijakataliwa**: survivors observed ({obs['survivors']}) HAZIZIDI random kwa "
                 f"uhakika (null {g_surv.mean():.1f}, z={z_g:+.1f}, perm p={p_perm:.3f}, "
                 f"{'nje' if outside else 'ndani'} ya CI). Sehemu kubwa ya 'edge' inaweza kuwa **sampling "
                 "noise** (inaunga mkono F-029). Principle 28: HAIRUHUSIWI kujenga adaptive system/ML bado — "
                 "edge halisi haijathibitishwa zaidi ya bahati.")
    L.append("\n*Edge Reality Test: null-global (shuffle outcomes) + null-time (shuffle order, keep EV) + "
             "permutation + bootstrap. H1 = survivors > random (perm p<0.05 NA nje ya null CI). F-027: early "
             "quality ≠ future persistence. F-029: decay inaweza kuwa stochastic. Principle 28: thibitisha edge "
             "> random kabla ya adaptive system. NO ML. Profitable ≠ Tradable Edge.*")
    out = REPO_ROOT / c["paths"]["reports"] / "edge_reality_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)} (survivors obs={obs['survivors']} null={g_surv.mean():.1f}, "
          f"perm p={p_perm:.3f}, {'H1' if H1 else 'H0'})")
    return 0


def self_test():
    """(1) real-edge synthetic (configs zenye EV chanya thabiti) -> survivors observed ≫ null,
       perm p<0.05 -> H1. (2) pure-noise synthetic (net~N(0,sd)) -> observed ≈ null,
       p not significant -> H0."""
    rng = np.random.default_rng(0)
    nwin = NWIN

    def mk(mu, sd, n):
        return np.array([rng.normal(mu, sd) for _ in range(n)], float)

    # (1) REAL edge (inayoiga uhalisia: configs chache zenye edge kweli, pooled ≈ hasi):
    #     15 configs EV +5 thabiti + 185 configs EV -1 -> pooled mean hasi (kama trade-all)
    real = [("ev", mk(5.0, 4.0, 480)) for _ in range(15)] + [("ev", mk(-1.0, 5.0, 480)) for _ in range(185)]
    obs_r = agg(real)
    pool = np.concatenate([n for _, n in real]); sizes = [len(n) for _, n in real]; evs = [e for e, _ in real]
    g = np.array([null_global(real, pool, sizes, evs, rng)["survivors"] for _ in range(120)])
    p_r = _pval_ge(g, obs_r["survivors"])
    h1 = obs_r["survivors"] > g.mean() and p_r < 0.05
    print(f"REAL: obs survivors={obs_r['survivors']} null-global={g.mean():.1f} perm p={p_r:.3f} -> H1={h1}")

    # (2) PURE NOISE: 200 configs net~N(0,6) -> observed survivors ≈ null
    noise = [("ev", mk(0.0, 6.0, 480)) for _ in range(200)]
    obs_n = agg(noise)
    pool2 = np.concatenate([n for _, n in noise]); sizes2 = [len(n) for _, n in noise]; evs2 = [e for e, _ in noise]
    g2 = np.array([null_global(noise, pool2, sizes2, evs2, rng)["survivors"] for _ in range(120)])
    p_n = _pval_ge(g2, obs_n["survivors"])
    h0 = not (p_n < 0.05)
    print(f"NOISE: obs survivors={obs_n['survivors']} null-global={g2.mean():.1f} perm p={p_n:.3f} -> H0_kept={h0}")

    ok = h1 and h0
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    global NREP
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default=None)
    ap.add_argument("--reps", type=int, default=NREP)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    NREP = a.reps
    c = cfg()
    pairs = [a.symbol] if a.symbol else c["pairs"]
    return run(pairs, None)


if __name__ == "__main__":
    raise SystemExit(main())
