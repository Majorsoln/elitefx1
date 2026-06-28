"""
alpha_confirmation_engine.py — PHASE 14 (Chief Quant). Contextual Alpha Confirmation.

Phase 13 ilikuwa EXPLORATORY tu. Chief alikataa "30 Candidate Alpha" kama alpha kwa
sababu ya logic gaps: (1) selection bias (top kwa Bayesian baada ya kuona data),
(2) multiple comparisons (mamia ya cells), (3) UNKNOWN states kwenye identity,
(4) leave-one-out haitoshi (Pair inaweza kuwa PROXY ya spread/session/vol),
(5) hakuna mechanism/independent contribution. Sasa ni **Contextual Alpha Hypothesis**.

  Principle 31: kila Contextual Alpha Object ni HYPOTHESIS mpaka inusurike prospective
                validation.
  Principle 32: identity variables lazima zionyeshe INDEPENDENT explanatory power, sio
                predictive association tu.
  F-032: context refinement huongeza apparent edge, LAKINI pia false discovery risk.

Phase 14 inathibitisha kwa ukali (confirmatory, sio exploratory):
  1. PRE-REGISTER hypotheses zote kwa IN-SAMPLE tu (discovery period).
  2. TEST kwenye FUTURE OOS period (haikutumika kuzigundua).
  3. Benjamini–Hochberg FDR kudhibiti multiple comparisons.
  4. ONDOA/eleza UNKNOWN — hakuna hypothesis yenye identity isiyokamilika.
  5. INDEPENDENT CONTRIBUTION ya Pair (baada ya kudhibiti spread/session/vol), sio
     leave-one-out pekee.

Swali: je hata hypothesis MOJA inaishi nje ya data iliyoigundua? NO ML.

Reuse: market_state_engine (cfg, pip), latent_structure (state_path), event_library
(EVENTS_ALL), configuration_engine (EVENTS_SET, VERT), context_value (HORIZON),
contextual_alpha_engine (session_of, _phi).

Output: reports/contextual_alpha_confirmation_report.md
Self-test: python src/research/alpha_confirmation_engine.py --self-test
"""
from __future__ import annotations

import argparse, math, sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
import polars as pl

from market_state_engine import cfg, pip
from latent_structure import state_path
from event_library import EVENTS_ALL
from configuration_engine import EVENTS_SET, VERT
from context_value import HORIZON
from contextual_alpha_engine import session_of, _phi

REPO_ROOT = Path(__file__).resolve().parents[2]
TFS = ["H1", "H2", "H4", "D1"]
IS_FRAC = 0.60        # in-sample (discovery) fraction; OOS = last 40% (future, hold-out)
MIN_IS = 200          # in-sample sample ya chini ili ku-PRE-REGISTER
MIN_OOS = 100         # OOS sample ya chini ili ku-TEST
FDR_Q = 0.10          # Benjamini–Hochberg target FDR
DIMS = ["pair", "vol", "spr", "sess"]


def bh_fdr(pvals, q=FDR_Q):
    """Benjamini–Hochberg: rudisha boolean array (True = survives FDR q)."""
    p = np.asarray(pvals, float); m = len(p)
    if m == 0:
        return np.zeros(0, bool)
    order = np.argsort(p); sp = p[order]
    thresh = q * (np.arange(1, m + 1) / m)
    below = sp <= thresh
    out = np.zeros(m, bool)
    if below.any():
        kmax = np.max(np.where(below)[0])
        cut = sp[kmax]
        out = p <= cut
    return out


def oos_pvalue(net):
    """One-sided p kwamba mean(net) > 0 (net tayari ina spread cost). p = Φ(−EV/SE)."""
    n = len(net)
    if n < 2:
        return float("nan"), float("nan"), float("nan")
    ev = float(net.mean()); se = float(net.std(ddof=1) / math.sqrt(n))
    if se <= 0:
        return ev, se, float("nan")
    return ev, se, _phi(-ev / se)


def build_arrays(pairs):
    EV = []; SY = []; VOL = []; SPRST = []; SESS = []; D = []; FWD = []; SPRP = []; TS = []
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
            vol = df["volatility_state"].to_list(); sprst = df["spread_state"].to_list()
            hours = df["ts"].dt.hour().to_list()
            ts = df["ts"].to_numpy().astype("datetime64[s]").astype(np.int64)
            n = len(close)
            sig = {ev: EVENTS_ALL[ev](close, high, low) for ev in EVENTS_SET}
            for i in range(n):
                if i + VERT >= n or i + HORIZON >= n or not (atr[i] > 0):
                    continue
                fwd = close[i + HORIZON] - close[i]; sp = spr[i]; ses = session_of(hours[i])
                for ev in EVENTS_SET:
                    s = sig[ev][i]
                    if s != 0:
                        EV.append(ev); SY.append(sym); VOL.append(vol[i]); SPRST.append(sprst[i])
                        SESS.append(ses); D.append(int(s)); FWD.append(fwd); SPRP.append(sp); TS.append(int(ts[i]))
        print(f"  {sym}: done", flush=True)
    A = dict(event=np.array(EV, dtype=object), pair=np.array(SY, dtype=object),
             vol=np.array(VOL, dtype=object), spr=np.array(SPRST, dtype=object),
             sess=np.array(SESS, dtype=object), d=np.array(D, float),
             fwd=np.array(FWD, float), sprp=np.array(SPRP, float), ts=np.array(TS, np.int64))
    return A, no_px


def confirm(A):
    """Rudisha summary ya pre-registration + OOS + BH-FDR + independent contribution."""
    ts = A["ts"]; cut = np.quantile(ts, IS_FRAC)
    is_m = ts < cut; oos_m = ts >= cut
    net_all = A["d"] * A["fwd"] - A["sprp"]
    keys = list(zip(A["event"], A["pair"], A["vol"], A["spr"], A["sess"]))
    keys = np.array(keys, dtype=object)

    # ---- PRE-REGISTER kwa IN-SAMPLE tu ----
    is_idx = defaultdict(list)
    for i in np.where(is_m)[0]:
        is_idx[tuple(keys[i])].append(i)
    registered = []; excluded_unknown = 0
    for key, idx in is_idx.items():
        if "UNKNOWN" in key:          # req 4: identity haijakamilika
            excluded_unknown += 1; continue
        if len(idx) < MIN_IS:
            continue
        ev_is = float(net_all[np.array(idx)].mean())
        if ev_is > 0:                 # hypothesis ya directional edge (pre-registered)
            registered.append((key, ev_is, len(idx)))

    # ---- TEST kwa OOS ----
    oos_idx = defaultdict(list)
    for i in np.where(oos_m)[0]:
        oos_idx[tuple(keys[i])].append(i)
    tested = []
    for key, ev_is, n_is in registered:
        idx = oos_idx.get(key, [])
        if len(idx) < MIN_OOS:
            continue
        net = net_all[np.array(idx)]
        ev_o, se_o, p = oos_pvalue(net)
        if np.isfinite(p):
            tested.append(dict(key=key, ev_is=ev_is, n_is=n_is, ev_oos=ev_o, n_oos=len(idx), p=p))
    pvals = np.array([t["p"] for t in tested])
    surv = bh_fdr(pvals, FDR_Q) if len(tested) else np.zeros(0, bool)
    for t, s in zip(tested, surv):
        t["survives"] = bool(s)

    # ---- INDEPENDENT CONTRIBUTION ya pair (req 5), kwa OOS ----
    # ctx4 = (event,vol,spr,sess) bila pair; je pair maalum inazidi pairs nyingine ndani ya ctx?
    ctx_idx = defaultdict(lambda: defaultdict(list))   # ctx4 -> pair -> oos indices
    for i in np.where(oos_m)[0]:
        e, pr, v, sp, se = keys[i]
        ctx_idx[(e, v, sp, se)][pr].append(i)
    for t in tested:
        e, pr, v, sp, se = t["key"]; bucket = ctx_idx[(e, v, sp, se)]
        others = [j for p2, js in bucket.items() if p2 != pr for j in js]
        if len(others) >= MIN_OOS:
            ev_other = float(net_all[np.array(others)].mean())
            t["ev_other_pairs"] = ev_other
            t["pair_independent"] = t["ev_oos"] - ev_other > 0.2 and t["ev_oos"] > 0
        else:
            t["ev_other_pairs"] = float("nan"); t["pair_independent"] = None

    return dict(cut=cut, n_is=int(is_m.sum()), n_oos=int(oos_m.sum()),
                registered=len(registered), excluded_unknown=excluded_unknown,
                tested=tested, n_survive=int(surv.sum()))


def run(pairs, tfs):
    c = cfg()
    A, no_px = build_arrays(pairs)
    if no_px:
        print("HITILAFU: state parquet haipo. Endesha market_state_engine.py kwanza.", file=sys.stderr)
        return 1
    print(f"  instances={len(A['event']):,}", flush=True)
    S = confirm(A)
    tested = S["tested"]; tested.sort(key=lambda t: t["p"])

    L = ["# Contextual Alpha Confirmation — je hypothesis MOJA inaishi OOS? (Phase 14)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | pre-register kwa IN-SAMPLE ({int(IS_FRAC*100)}%) → test FUTURE "
         f"OOS ({int((1-IS_FRAC)*100)}%) | Benjamini–Hochberg FDR q={FDR_Q} | min IS={MIN_IS}, OOS={MIN_OOS}*\n",
         "> **Confirmatory, sio exploratory.** **Principle 31:** kila Contextual Alpha Object ni HYPOTHESIS "
         "mpaka inusurike prospective validation. **Principle 32:** identity lazima ionyeshe INDEPENDENT "
         "explanatory power (sio association). **F-032:** context refinement huongeza apparent edge NA false "
         "discovery risk. UNKNOWN states zimeondolewa (identity haijakamilika). NO ML. Profitable ≠ Tradable.\n",
         f"\n**Setup:** IS instances={S['n_is']:,} | OOS instances={S['n_oos']:,} | "
         f"pre-registered hypotheses={S['registered']} | excluded (UNKNOWN identity)={S['excluded_unknown']} | "
         f"tested OOS (N≥{MIN_OOS})={len(tested)} | **survive BH-FDR(q={FDR_Q})={S['n_survive']}**\n"]

    # survivors / top
    L.append("\n## Hypotheses zilizopita OOS + FDR (pre-registered)\n")
    surv = [t for t in tested if t.get("survives")]
    if surv:
        L.append("| event · pair · vol · spread · session | N(IS) | EV(IS) | N(OOS) | EV(OOS) | p | pair-independent? |")
        L.append("|---------------------------------------|-------|--------|--------|---------|---|-------------------|")
        for t in sorted(surv, key=lambda t: t["ev_oos"], reverse=True):
            pi = ("✅ ndiyo" if t["pair_independent"] else ("hapana" if t["pair_independent"] is False else "n/a"))
            L.append(f"| {' · '.join(t['key'])} | {t['n_is']:,} | {t['ev_is']:+.2f} | {t['n_oos']:,} | "
                     f"{t['ev_oos']:+.2f} | {t['p']:.4f} | {pi} |")
    else:
        L.append("*(hakuna hypothesis iliyopita BH-FDR.)*")

    # top by OOS p (whether or not survive) for transparency
    L.append("\n## Top 15 pre-registered hypotheses kwa OOS p-value (uwazi)\n")
    L.append("| event · pair · vol · spread · session | EV(IS) | EV(OOS) | OOS p | BH survive? |")
    L.append("|---------------------------------------|--------|---------|-------|-------------|")
    for t in tested[:15]:
        L.append(f"| {' · '.join(t['key'])} | {t['ev_is']:+.2f} | {t['ev_oos']:+.2f} | {t['p']:.4f} | "
                 f"{'✅' if t.get('survives') else '—'} |")

    # IS->OOS shrinkage (F-032 evidence)
    if tested:
        mean_is = float(np.mean([t["ev_is"] for t in tested]))
        mean_oos = float(np.mean([t["ev_oos"] for t in tested]))
        pos_oos = sum(1 for t in tested if t["ev_oos"] > 0)
        L.append("\n## F-032 — apparent edge vs OOS (shrinkage)\n")
        L.append(f"- pre-registered (IS EV>0) hypotheses: mean EV(IS) = **{mean_is:+.2f}** → mean EV(OOS) = "
                 f"**{mean_oos:+.2f}**")
        L.append(f"- bado chanya OOS: **{pos_oos}/{len(tested)}** ({100*pos_oos/len(tested):.0f}%)  "
                 f"(bahati ya nasibu ≈ 50%)")
        L.append(f"\n→ {'✅ F-032: edge inashuka sana IS→OOS (selection/refinement inazidisha apparent edge)' if mean_oos < mean_is * 0.5 else 'edge inadumu kiasi IS→OOS'}.")

    # VERDICT
    L.append("\n## VERDICT — Phase 14 Confirmation\n")
    if S["n_survive"] >= 1:
        ind = [t for t in surv if t.get("pair_independent")]
        L.append(f"→ ✅ **{S['n_survive']} hypothesis(zilinusurika)** OOS + BH-FDR(q={FDR_Q}) — uthibitisho wa "
                 f"kwanza wa prospective. Kati ya hizo, **{len(ind)}** zina pair-independent contribution "
                 "(Principle 32 — sio proxy ya spread/session/vol). Hizi PEKEE zinastahili kupanda kuelekea "
                 "Opportunity Engine (bado Contextual Alpha Hypothesis hadi replication zaidi).")
    else:
        L.append(f"→ ⚠️ **HAKUNA hypothesis iliyonusurika** OOS + BH-FDR. Apparent edge ya Phase 13 ilikuwa "
                 "selection bias + multiple comparisons (inathibitisha **F-032**). Hii ni 'protect capital "
                 "first': hatuna alpha ya kufanyiwa biashara bado. Opportunity Engine/ML zinabaki zimezuiwa "
                 "(Principle 28/31). Inahitaji representation/ecology mpya au data zaidi.")
    L.append("\n*Confirmatory: pre-register (IS) → future OOS → Benjamini–Hochberg FDR → independent-"
             "contribution. UNKNOWN identity excluded (Principle 32). F-032: refinement↑ apparent edge & FDR "
             "risk. Hypothesis hadi prospective validation (Principle 31). NO ML. Profitable ≠ Tradable Edge.*")
    out = REPO_ROOT / c["paths"]["reports"] / "contextual_alpha_confirmation_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)} (registered {S['registered']}, tested {len(tested)}, "
          f"survive {S['n_survive']})")
    return 0


def self_test():
    """(1) bh_fdr sahihi. (2) end-to-end: TRUE alpha (skill IS+OOS) inanusurika; noise nyingi
       hazinusuriki (FDR inadhibiti). (3) UNKNOWN imeondolewa kwenye registration."""
    # bh_fdr: p moja ndogo sana + nyingi kubwa
    p = np.array([0.0001] + [0.6] * 49)
    s = bh_fdr(p, 0.10)
    bh_ok = s[0] and s.sum() == 1
    print(f"bh_fdr: survivors={s.sum()} (first={s[0]}, ok={bh_ok})")

    rng = np.random.default_rng(0)
    EV = []; SY = []; VOL = []; SPRST = []; SESS = []; D = []; FWD = []; SPRP = []; TS = []

    def add(event, sym, vol, sprst, sess, skill, n, t0):
        for k in range(n):
            fwd = float(rng.normal(0, 10))
            d = float(np.sign(fwd)) if rng.random() < skill else float(-np.sign(fwd))
            if d == 0:
                d = 1.0
            EV.append(event); SY.append(sym); VOL.append(vol); SPRST.append(sprst); SESS.append(sess)
            D.append(d); FWD.append(fwd); SPRP.append(1.0); TS.append(t0 + k)

    # TRUE alpha: skill 0.66 (IS na OOS) — N kubwa
    add("mr", "EURUSD", "NORMAL", "NORMAL", "LONDON", 0.66, 1500, 0)        # IS
    add("mr", "EURUSD", "NORMAL", "NORMAL", "LONDON", 0.66, 1000, 100000)   # OOS
    # noise objects: skill 0.5 (hakuna edge) — IS & OOS
    for j in range(40):
        add(f"e{j%5}", f"P{j%8}", ["LOW", "NORMAL", "HIGH"][j % 3], "NORMAL", "ASIAN", 0.5, 500, j * 10)
        add(f"e{j%5}", f"P{j%8}", ["LOW", "NORMAL", "HIGH"][j % 3], "NORMAL", "ASIAN", 0.5, 350, 100000 + j * 10)
    # UNKNOWN object (lazima iondolewe)
    add("mr", "EURUSD", "UNKNOWN", "NORMAL", "LONDON", 0.8, 600, 50)

    A = dict(event=np.array(EV, dtype=object), pair=np.array(SY, dtype=object),
             vol=np.array(VOL, dtype=object), spr=np.array(SPRST, dtype=object),
             sess=np.array(SESS, dtype=object), d=np.array(D, float),
             fwd=np.array(FWD, float), sprp=np.array(SPRP, float), ts=np.array(TS, np.int64))
    S = confirm(A)
    surv_keys = [t["key"] for t in S["tested"] if t["survives"]]
    true_surv = any(k[0] == "mr" and k[1] == "EURUSD" and k[2] == "NORMAL" for k in surv_keys)
    unknown_excluded = S["excluded_unknown"] >= 1
    controlled = S["n_survive"] <= 3   # FDR inadhibiti noise (true + labda 1-2 false max)
    print(f"confirm: registered={S['registered']} excluded_unknown={S['excluded_unknown']} "
          f"survive={S['n_survive']} true_survives={true_surv}")

    ok = bh_ok and true_surv and unknown_excluded and controlled
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
