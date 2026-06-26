"""
confidence_engine.py — PHASE 7 (Chief Quant). Configuration Confidence Engine.

Phase 6.5 (Configuration Engine) ilithibitisha: Configuration ndio ATOMIC TRADING
UNIT (Pair × Event × Latent State × Regime × Direction × Execution Context), na
**F-022 (APPROVED)**: configurations MBAYA zina persistence kubwa kuliko nzuri
(train-negative→negative ~66% vs train-positive→positive ~42%). Pia:
  F-023 (APPROVED): Ranking ndio lugha ya asili ya Opportunity Engine (sio classification).
  F-024 (OPEN):     Confidence ina thamani sawa na Expected Payoff.

Tatizo: Expected Payoff PEKE YAKE haitoshi. Configuration mbili zinaweza kuwa na
EV=+15 lakini moja N=120, nyingine N=12,000 — HAZIFANANI. Principle 24: hakuna
Configuration inapangwa (ranked) kwa Expected Payoff peke yake. Lazima iingie:
confidence interval, persistence, walk-forward stability, sample quality.

Phase 7 inapima kwa kila Configuration:
  • Expected Value (EV) + 95% CI
  • Sample size (N) + sample quality
  • t-statistic + confidence (edge ni halisi, sio bahati)
  • K-fold walk-forward persistence (ishara inaendelea kwa muda?)
  • Stability score (ukubwa wa EV ni thabiti kati ya folds?)
  • Configuration Confidence Score (CCS) = EV × Confidence × Persistence × SampleQuality

Kisha inaonyesha: ranking kwa CCS ≠ ranking kwa EV peke yake (Principle 24/F-024),
na inathibitisha F-022 (negative persistence > positive). NO ML bado — CCS ndio
target ya baadaye ya ML (Configuration Score, sio BUY/SELL).

Reuse: configuration_engine (assign, wf_split, EVENTS_SET, K, VERT, KSIG),
latent_structure (kmeans, collect, state_path), mechanism_discovery (signatures),
event_library, context_value (HORIZON), triple_barrier_design (first_touch).

Output: reports/confidence_engine_report.md
Self-test: python src/research/confidence_engine.py --self-test
"""
from __future__ import annotations

import argparse, math, sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
import polars as pl

from market_state_engine import cfg, pip
from mechanism_discovery import signatures
from latent_structure import kmeans, collect, state_path
from event_library import EVENTS_ALL
from context_value import HORIZON
from triple_barrier_design import first_touch
from configuration_engine import assign, wf_split, EVENTS_SET, K, VERT, KSIG

REPO_ROOT = Path(__file__).resolve().parents[2]
TFS = ["H1", "H2", "H4", "D1"]
MIN_N = 100            # sample ya chini kwa Configuration
KFOLD = 5              # walk-forward folds (persistence)
N0 = 1000             # sample-quality reference (N/(N+N0))
STAB_FLOOR = 2.0       # pip floor kwa stability CoV (kuepuka blow-up karibu na EV≈0)
TOPN = 25
_posix = lambda p: str(p).replace("\\", "/")


def _phi(t):
    """Normal CDF (math.erf) — scalar."""
    return 0.5 * (1.0 + math.erf(t / math.sqrt(2.0)))


def _conf_two_sided(t):
    """Confidence kwamba EV ≠ 0 (bila kujali ishara): 2Φ(|t|)−1 ∈ [0,1]."""
    return max(0.0, 2.0 * _phi(abs(t)) - 1.0)


def confidence_score(rows):
    """Configuration moja (rows = list ya (ts,net,win,tb)) -> takwimu + CCS.

    CCS = EV × Confidence × Persistence × SampleQuality (Chief: concept, sio formula
    ya mwisho). Kila multiplier ∈ [0,1]; EV inabaki na ishara/ukubwa -> CCS chanya
    kubwa = edge nzuri thabiti; CCS hasi kubwa = edge mbaya thabiti (F-022 avoid-list)."""
    r = sorted(rows, key=lambda t: t[0])           # panga kwa muda (no-lookahead folds)
    nets = np.array([x[1] for x in r], float); n = len(nets)
    ev = float(nets.mean())
    sd = float(nets.std(ddof=1)) if n > 1 else float("nan")
    se = sd / math.sqrt(n) if n > 1 and sd > 0 else float("nan")
    ci = 1.96 * se if np.isfinite(se) else float("nan")
    t = ev / se if np.isfinite(se) and se > 0 else 0.0
    conf = _conf_two_sided(t)
    # K-fold walk-forward: EV kwa kila fold ya muda; persistence = ishara inakubaliana
    folds = np.array_split(nets, KFOLD)
    fev = np.array([f.mean() for f in folds if len(f)])
    persistence = float(np.mean(np.sign(fev) == np.sign(ev))) if len(fev) and ev != 0 else 0.0
    # stability = uthabiti wa UKUBWA kati ya folds (1 − CoV iliyofungwa)
    stability = float(max(0.0, 1.0 - fev.std() / (abs(ev) + STAB_FLOOR))) if len(fev) else 0.0
    sample_q = n / (n + N0)
    ccs = ev * conf * persistence * sample_q
    # rejea 70/30 split (linganisho na configuration_engine)
    tr, te = wf_split(r)
    tev = float(np.mean([x[1] for x in tr])) if tr else float("nan")
    sev = float(np.mean([x[1] for x in te])) if te else float("nan")
    return dict(n=n, ev=ev, ci=ci, se=se, t=t, conf=conf, persistence=persistence,
                stability=stability, sample_q=sample_q, ccs=ccs, train_ev=tev, test_ev=sev)


def spearman(a, b):
    """Spearman rank corr (numpy) — kupima jinsi ranking ya EV inavyotofautiana na CCS."""
    a = np.asarray(a, float); b = np.asarray(b, float)
    if len(a) < 3:
        return float("nan")
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    ra = ra - ra.mean(); rb = rb - rb.mean()
    d = math.sqrt((ra @ ra) * (rb @ rb))
    return float(ra @ rb / d) if d > 0 else float("nan")


def build_acc(pairs, cen):
    """acc[config_key] = list ya (ts, net, win, tb_label). config_key sawa na Phase 6.5."""
    acc = defaultdict(list); no_px = True
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
            sig, *_ = signatures(df, pp); fin = np.all(np.isfinite(sig), axis=1)
            cl = np.full(len(sig), -1)
            if fin.any():
                cl[fin] = assign(sig[fin], cen)
            close = df["c"].to_numpy() / pp; high = df["h"].to_numpy() / pp; low = df["l"].to_numpy() / pp
            atr_pips = df["atr"].to_numpy() / pp
            spr = df["spr"].to_numpy(); spr = np.where(np.isfinite(spr), spr, 0.0)
            vol = df["volatility_state"].to_list(); exec_ctx = df["spread_state"].to_list()
            ts = df["ts"].to_numpy().astype("datetime64[s]").astype(np.int64)
            n = len(close)
            for ev in EVENTS_SET:
                s = EVENTS_ALL[ev](close, high, low)
                for i in range(n):
                    if s[i] == 0 or cl[i] < 0 or i + VERT >= n or not (atr_pips[i] > 0):
                        continue
                    reg = vol[i]; ex = exec_ctx[i]
                    if reg == "UNKNOWN" or ex == "UNKNOWN" or i + HORIZON >= n:
                        continue
                    d = int(s[i]); direction = "LONG" if d == 1 else "SHORT"
                    net = float(d * (close[i + HORIZON] - close[i]) - spr[i])
                    tb, oc = first_touch(i, d, KSIG * atr_pips[i], close, high, low, n)
                    lab = oc if tb <= VERT else "TIME"
                    acc[(sym, ev, f"C{cl[i]}", reg, direction, ex)].append(
                        (int(ts[i]), net, 1 if net > 0 else 0, lab))
        print(f"  {sym}: done", flush=True)
    return acc, no_px


def run(pairs, tfs):
    c = cfg(); rng = np.random.default_rng(0)
    pool = [X for sym in pairs if len(X := collect(sym, rng)) > 50]
    if not pool:
        print("HITILAFU: hakuna state parquet. Endesha market_state_engine.py kwanza.", file=sys.stderr)
        return 1
    _, cen, _ = kmeans(np.vstack(pool), K, rng)
    print(f"  latent clusters k={K} fitted", flush=True)
    acc, no_px = build_acc(pairs, cen)
    if no_px:
        print("HITILAFU: OHLC haipo. Endesha market_state_engine.py (OHLC update) kwanza.", file=sys.stderr)
        return 1

    stats = {k: confidence_score(v) for k, v in acc.items() if len(v) >= MIN_N}
    if not stats:
        print(f"HITILAFU: hakuna Configuration yenye N≥{MIN_N}.", file=sys.stderr)
        return 1

    def fmt(key, st):
        name = "·".join(key)
        return (f"| {name} | {st['n']:,} | {st['ev']:+.2f} [{st['ev']-st['ci']:+.1f},{st['ev']+st['ci']:+.1f}] | "
                f"{st['t']:+.1f} | {st['conf']:.2f} | {st['persistence']:.2f} | {st['stability']:.2f} | "
                f"{st['sample_q']:.2f} | **{st['ccs']:+.2f}** |")

    by_ccs = sorted(stats.items(), key=lambda kv: kv[1]["ccs"])
    best = list(reversed(by_ccs[-TOPN:]))
    worst = by_ccs[:TOPN]

    # Principle 24 / F-024: ranking kwa EV peke yake vs CCS
    keys = list(stats.keys())
    ev_arr = [stats[k]["ev"] for k in keys]; ccs_arr = [stats[k]["ccs"] for k in keys]
    rho = spearman(ev_arr, ccs_arr)
    top_ev = set(sorted(keys, key=lambda k: stats[k]["ev"], reverse=True)[:TOPN])
    top_ccs = set(sorted(keys, key=lambda k: stats[k]["ccs"], reverse=True)[:TOPN])
    overlap = len(top_ev & top_ccs)
    # mfano: high EV lakini imeshushwa na CCS (confidence/sample ndogo)
    demoted = sorted(top_ev - top_ccs, key=lambda k: stats[k]["ev"], reverse=True)

    # F-022: persistence ya negative vs positive (70/30 split, sawa na Phase 6.5)
    pos_k = [k for k in keys if np.isfinite(stats[k]["train_ev"]) and stats[k]["train_ev"] > 0]
    neg_k = [k for k in keys if np.isfinite(stats[k]["train_ev"]) and stats[k]["train_ev"] < 0]
    pos_persist = np.mean([stats[k]["test_ev"] > 0 for k in pos_k]) if pos_k else float("nan")
    neg_persist = np.mean([stats[k]["test_ev"] < 0 for k in neg_k]) if neg_k else float("nan")

    n_pos_ccs = sum(1 for k in keys if stats[k]["ccs"] > 0)
    L = ["# Configuration Confidence Engine — ranking ya institutional grade (Phase 7)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | Configuration = Pair·Event·LatentState(k={K})·Regime·Direction·"
         f"ExecContext | CCS = EV × Confidence × Persistence × SampleQuality | {KFOLD}-fold walk-forward | "
         f"outcome forward {HORIZON}b net | min N={MIN_N}*\n",
         "> **Principle 24 (Chief):** hakuna Configuration inapangwa (ranked) kwa Expected Payoff PEKE YAKE — "
         "lazima iingie confidence interval, persistence, walk-forward stability, sample quality. **F-023:** "
         "ranking ndio lugha ya asili ya Opportunity Engine (sio classification). **F-024 (OPEN):** Confidence "
         "ina thamani sawa na Expected Payoff. **F-022 (APPROVED):** configs mbaya zina persistence kubwa "
         "kuliko nzuri. CCS = target ya baadaye ya ML (Configuration Score, sio BUY/SELL). NO ML bado.\n",
         "## Muhtasari\n",
         f"- Configurations zenye N≥{MIN_N}: **{len(stats):,}**  |  CCS>0: **{n_pos_ccs}**  |  "
         f"EV-rank vs CCS-rank Spearman ρ = **{rho:+.2f}**  |  Top-{TOPN} overlap (EV vs CCS): "
         f"**{overlap}/{TOPN}**\n",
         f"\n## Top {len(best)} configurations kwa **CCS** (opportunities zenye ushahidi bora)\n",
         "| Configuration | N | EV [95% CI] | t | conf | persist | stab | sampleQ | CCS |",
         "|---------------|---|-------------|---|------|---------|------|---------|-----|"]
    for key, st in best:
        L.append(fmt(key, st))

    L.append(f"\n## Bottom {len(worst)} configurations kwa **CCS** — **'WAPI USIFANYE TRADE'** (F-022: persistent negatives)\n")
    L.append("| Configuration | N | EV [95% CI] | t | conf | persist | stab | sampleQ | CCS |")
    L.append("|---------------|---|-------------|---|------|---------|------|---------|-----|")
    for key, st in worst:
        L.append(fmt(key, st))

    # Principle 24 demonstration
    L.append("\n## Principle 24 / F-024 — je Confidence inabadilisha ranking? (EV peke yake vs CCS)\n")
    L.append(f"- Spearman ρ kati ya EV-ranking na CCS-ranking = **{rho:+.2f}** "
             f"({'rankings zinatofautiana' if rho < 0.95 else 'rankings zinakaribiana'}).")
    L.append(f"- Top-{TOPN}: EV-alone na CCS zinashiriki **{overlap}/{TOPN}** tu — "
             f"**{TOPN-overlap}** configurations zenye EV juu ZIMESHUSHWA na CCS (confidence/sample ndogo).")
    if demoted:
        L.append("\n**Mifano: EV juu lakini CCS imeshusha (kwa nini ranking ya EV peke yake ni hatari):**\n")
        L.append("| Configuration | N | EV | conf | persist | sampleQ | CCS |")
        L.append("|---------------|---|----|------|---------|---------|-----|")
        for k in demoted[:6]:
            st = stats[k]
            L.append(f"| {'·'.join(k)} | {st['n']:,} | {st['ev']:+.2f} | {st['conf']:.2f} | "
                     f"{st['persistence']:.2f} | {st['sample_q']:.2f} | {st['ccs']:+.2f} |")
        L.append("\n→ ✅ **F-024 inaungwa mkono**: Configuration zenye EV kubwa lakini N ndogo / confidence "
                 "ndogo / persistence ndogo zinashuka kwenye CCS. Expected Payoff PEKE YAKE inadanganya — "
                 "Confidence ina thamani sawa (Principle 24).")
    else:
        L.append("\n→ ⚠️ EV-ranking na CCS-ranking zinakaribiana sana hapa; F-024 inahitaji utofauti zaidi "
                 "wa N/variance kati ya configs.")

    # F-022 confirmation
    L.append("\n## F-022 (APPROVED) — negative persistence > positive (walk-forward 70/30)\n")
    L.append(f"- train-positive → test-positive: **{pos_persist*100:.0f}%** (N configs = {len(pos_k)})")
    L.append(f"- train-negative → test-negative: **{neg_persist*100:.0f}%** (N configs = {len(neg_k)})")
    if np.isfinite(neg_persist) and np.isfinite(pos_persist) and neg_persist > pos_persist:
        L.append("\n→ ✅ **F-022 imethibitishwa tena**: edge mbaya inaendelea (persist) zaidi kuliko nzuri. "
                 "'Trade less, but in the right environment' — jua WAPI USIFANYE trade kwanza.")
    else:
        L.append("\n→ ⚠️ kwa data hii negative persistence haijazidi positive; inahitaji folds/data zaidi.")

    L.append("\n## VERDICT — Phase 7 Confidence Engine\n")
    L.append(f"→ Kati ya {len(stats):,} configurations, **{n_pos_ccs}** zina CCS>0 (edge + ushahidi). CCS "
             "inachanganya EV, confidence (t/CI), walk-forward persistence, na sample quality kuwa kipimo "
             "kimoja cha kuaminika. Hii ndiyo entity ambayo **Opportunity Engine itafanya RANKING** (Principle "
             "23 — rank Configurations, sio classify Trades). Acceptance: Opportunity Engine itapokea CCS, sio "
             "EV peke yake.")
    L.append("\n*CCS = EV × Confidence × Persistence × SampleQuality (concept ya Chief; multipliers ∈[0,1], "
             "no-lookahead K-fold). Principle 24: hakuna ranking kwa EV peke yake. F-024: confidence = thamani "
             "sawa na payoff. F-023: ranking, sio classification. F-022: negative edge persistent zaidi. CCS = "
             "target ya baadaye ya ML (Configuration Score). Research Foundation imefungwa. Profitable ≠ "
             "Tradable Edge.*")
    out = REPO_ROOT / c["paths"]["reports"] / "confidence_engine_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)} ({len(stats):,} configs, {n_pos_ccs} CCS>0, ρ={rho:+.2f})")
    return 0


def self_test():
    """(1) _phi sahihi. (2) confidence_score: EV ileile (+5) lakini high-N-stable ina CCS
       KUBWA kuliko low-N-noisy (Principle 24/F-024). (3) confidently-negative -> CCS hasi
       kubwa, persistence=1. (4) spearman ya rankings tofauti < 1."""
    rng = np.random.default_rng(0)
    phi_ok = abs(_phi(0) - 0.5) < 1e-9 and abs(_phi(1.96) - 0.975) < 0.002
    print(f"_phi: Φ(0)={_phi(0):.3f} Φ(1.96)={_phi(1.96):.3f} (ok={phi_ok})")

    def mk(mu, sd, n, t0=0):
        return [(t0 + k, float(rng.normal(mu, sd)), 0, "TP") for k in range(n)]

    # EV ileile +5; A = N kubwa, noise ndogo (confident & stable); B = N ndogo, noise kubwa
    A = confidence_score(mk(5.0, 4.0, 6000))
    B = confidence_score(mk(5.0, 40.0, 120))
    same_ev = abs(A["ev"] - B["ev"]) < 2.0
    ccs_sep = A["ccs"] > B["ccs"] * 2          # confidence inashusha B sana
    print(f"EV≈same: A.ev={A['ev']:+.2f} B.ev={B['ev']:+.2f} | CCS: A={A['ccs']:+.2f} (conf {A['conf']:.2f}, "
          f"sampleQ {A['sample_q']:.2f}) >> B={B['ccs']:+.3f} (conf {B['conf']:.2f}, sampleQ {B['sample_q']:.2f}) "
          f"-> sep={ccs_sep}")

    # confidently negative, stable
    Ng = confidence_score(mk(-6.0, 5.0, 5000))
    neg_ok = Ng["ccs"] < 0 and Ng["persistence"] > 0.8 and Ng["conf"] > 0.9
    print(f"neg config: CCS={Ng['ccs']:+.2f} persist={Ng['persistence']:.2f} conf={Ng['conf']:.2f} (ok={neg_ok})")

    # spearman: rankings za EV vs CCS zinatofautiana (kwa sababu N/variance tofauti)
    cfgs = {"A": A, "B": B, "Ng": Ng,
            "C": confidence_score(mk(3.0, 4.0, 8000)),
            "D": confidence_score(mk(8.0, 60.0, 110))}     # EV juu sana lakini noisy & ndogo
    ks = list(cfgs)
    rho = spearman([cfgs[k]["ev"] for k in ks], [cfgs[k]["ccs"] for k in ks])
    # D ina EV juu zaidi lakini CCS ndogo -> ranking inatofautiana
    ev_top = max(ks, key=lambda k: cfgs[k]["ev"]); ccs_top = max(ks, key=lambda k: cfgs[k]["ccs"])
    rank_diff = ev_top != ccs_top and rho < 1.0
    print(f"ranking: EV-top={ev_top} CCS-top={ccs_top} ρ={rho:+.2f} (diff={rank_diff})")

    ok = phi_ok and same_ev and ccs_sep and neg_ok and rank_diff
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
