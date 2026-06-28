"""
contextual_alpha_engine.py — PHASE 13 (Chief Quant). Contextual Alpha Framework.

Discovery ya Phase 12: aggregate event = NO tradeable edge (0/5), LAKINI
mean_reversion×EURUSD=+0.90 (P100), deep_pullback×EURUSD=+0.37 (P97). Chief:
hii sio "tumepata edge" — ni discovery kwamba **EVENT SIO UNIVERSAL; ni CONDITIONAL
OBJECT**. Context sio filter — ni sehemu ya IDENTITY ya event.

  Principle 30 (APPROVED): An Event does not exist independently of its market context.
  F-030 (APPROVED): Edge existence is conditional, not universal.
  F-031 (APPROVED): Universal Events do not exist. Only Contextual Events exist.

Terminology mpya: Event → **Contextual Event**; Proven Edge → **Candidate Alpha**
(mpaka pre-registered OOS validation). spread = ECOLOGY variable, sio cost pekee.

Tunatafuta **Contextual Alpha Objects**, sio events:

    Mean Reversion + Pair + State + Regime + Liquidity + Execution + Session

Maswali (Chief):
  Q1. Kwa kila Contextual Event: pair+state+regime+liquidity+execution + P(edge).
  Q2. Ukiondoa PAIR, edge inapotea?
  Q3. Ukiondoa STATE, edge inapotea?
  Q4. Variables zipi ni IDENTITY na zipi ni MODIFIERS? (ablation leave-one-out)
  Q5. Jenga HIERARCHY: event → pair → vol → spread → session. Alpha iko wapi?

Null = random direction (skill net ya spread). Bayesian P(edge>0)=Φ(EV/SE).
Candidate Alpha = Bayesian>95% NA null-p<0.05 NA bootstrap CI-low>0 (⚠️ multiple
comparisons — bado ni CANDIDATE, sio APPROVED). NO ML.

Reuse: market_state_engine (cfg, pip), latent_structure (state_path), event_library
(EVENTS_ALL), configuration_engine (EVENTS_SET, VERT), context_value (HORIZON).

Output: reports/contextual_alpha_report.md
Self-test: python src/research/contextual_alpha_engine.py --self-test
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

REPO_ROOT = Path(__file__).resolve().parents[2]
TFS = ["H1", "H2", "H4", "D1"]
MIN_N = 300
NREP = 200
DIMS = ["pair", "vol", "spr", "sess"]      # context dimensions (event ni base)


def _phi(z):
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def session_of(hour):
    """UTC hour -> FX session (ecology dimension)."""
    if 0 <= hour < 7:
        return "ASIAN"
    if 7 <= hour < 13:
        return "LONDON"
    if 13 <= hour < 20:
        return "NEWYORK"
    return "OFF"


def edge_stat(fwd, spr, d, rng=None, nrep=0):
    """net = d·fwd − spr. Rudisha n, ev, bayes=Φ(EV/SE); kama nrep>0: null(random-dir)
    p + bootstrap 95% CI."""
    net = d * fwd - spr
    n = len(net)
    if n < 2:
        return dict(n=n, ev=float(net.mean()) if n else float("nan"), bayes=float("nan"),
                    p=float("nan"), lo=float("nan"), hi=float("nan"))
    ev = float(net.mean()); se = float(net.std(ddof=1) / math.sqrt(n))
    bayes = _phi(ev / se) if se > 0 else float("nan")
    out = dict(n=n, ev=ev, bayes=bayes, p=float("nan"), lo=float("nan"), hi=float("nan"))
    if nrep and rng is not None and se > 0:
        nulls = np.array([(rng.choice((-1.0, 1.0), n) * fwd - spr).mean() for _ in range(nrep)])
        out["p"] = (1 + int(np.sum(nulls >= ev))) / (nrep + 1)
        boot = np.array([net[rng.integers(0, n, n)].mean() for _ in range(nrep)])
        out["lo"], out["hi"] = float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))
    return out


def is_candidate(st):
    return (np.isfinite(st.get("bayes", np.nan)) and st["bayes"] > 0.95
            and np.isfinite(st.get("p", np.nan)) and st["p"] < 0.05
            and np.isfinite(st.get("lo", np.nan)) and st["lo"] > 0)


def build_arrays(pairs):
    """Per-instance contextual records (arrays za parallel)."""
    EV = []; SY = []; VOL = []; SPRST = []; SESS = []; D = []; FWD = []; SPRP = []
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
                        SESS.append(ses); D.append(int(s)); FWD.append(fwd); SPRP.append(sp)
        print(f"  {sym}: done", flush=True)
    A = dict(event=np.array(EV, dtype=object), pair=np.array(SY, dtype=object),
             vol=np.array(VOL, dtype=object), spr=np.array(SPRST, dtype=object),
             sess=np.array(SESS, dtype=object), d=np.array(D, float),
             fwd=np.array(FWD, float), sprp=np.array(SPRP, float))
    return A, no_px


def run(pairs, tfs):
    c = cfg(); rng = np.random.default_rng(0)
    A, no_px = build_arrays(pairs)
    if no_px:
        print("HITILAFU: state parquet haipo. Endesha market_state_engine.py kwanza.", file=sys.stderr)
        return 1
    base_event = A["event"]; n_tot = len(base_event)
    print(f"  instances={n_tot:,}", flush=True)

    def mask(conds):
        m = np.ones(n_tot, bool)
        for k, v in conds.items():
            m &= (A[k] == v)
        return m

    def stat(conds, nrep=0):
        m = mask(conds)
        return edge_stat(A["fwd"][m], A["sprp"][m], A["d"][m], rng, nrep), int(m.sum())

    # ---- Q1: contextual objects (event × pair × vol × spr × sess) ----
    groups = defaultdict(list)
    for i in range(n_tot):
        groups[(base_event[i], A["pair"][i], A["vol"][i], A["spr"][i], A["sess"][i])].append(i)
    cand = []
    for key, idx in groups.items():
        if len(idx) < MIN_N:
            continue
        ix = np.array(idx)
        st = edge_stat(A["fwd"][ix], A["sprp"][ix], A["d"][ix])
        cand.append((key, st, len(idx)))
    cand.sort(key=lambda t: (t[1]["bayes"] if np.isfinite(t[1]["bayes"]) else -1, t[1]["ev"]), reverse=True)

    L = ["# Contextual Alpha Framework — tunatafuta Contextual Alpha Objects, sio events (Phase 13)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | Contextual Event = event·pair·vol·spread·session | null(random-"
         f"dir)+bootstrap+Bayesian ({NREP} reps top) | forward {HORIZON}b net | min N={MIN_N} | instances={n_tot:,}*\n",
         "> **Principle 30 (Chief):** Event HAIPO bila market context — context ni sehemu ya IDENTITY. "
         "**F-030:** edge existence ni conditional, sio universal. **F-031:** universal events hazipo, ni "
         "Contextual Events tu. Terminology: Proven Edge → **Candidate Alpha** (⚠️ multiple comparisons — "
         "bado CANDIDATE mpaka pre-registered OOS). spread = ECOLOGY variable. NO ML. Profitable ≠ Tradable.\n"]

    # full test on top objects (positive EV only)
    L.append("\n## Q1 — Contextual Alpha Objects (top kwa Bayesian P(edge>0))\n")
    L.append("| event · pair · vol · spread · session | N | EV [95% CI] | null p | P(edge) | Candidate? |")
    L.append("|---------------------------------------|---|-------------|--------|---------|------------|")
    n_cand = 0; top_objs = []
    for key, st0, nn in cand[:30]:
        if st0["ev"] <= 0:
            continue
        full, _ = stat(dict(zip(["event"] + DIMS, key)), nrep=NREP)
        ok = is_candidate(full); n_cand += 1 if ok else 0
        if ok:
            top_objs.append((key, full, nn))
        L.append(f"| {' · '.join(key)} | {nn:,} | {full['ev']:+.2f} [{full['lo']:+.2f},{full['hi']:+.2f}] | "
                 f"{full['p']:.3f} | {full['bayes']*100:.0f}% | {'✅ CANDIDATE' if ok else '—'} |")
    L.append(f"\n→ **Candidate Alpha objects: {n_cand}** (⚠️ multiple comparisons — thibitisha kwa pre-registered OOS).")

    # anchor candidate (best) kwa Q2-Q5
    anchor = top_objs[0] if top_objs else (cand[0] if cand else None)
    if anchor is None:
        print("HITILAFU: hakuna contextual object N≥MIN_N.", file=sys.stderr); return 1
    akey = anchor[0]; aconds = dict(zip(["event"] + DIMS, akey))
    L.append(f"\n*Anchor kwa Q2–Q5: **{' · '.join(akey)}** (object yenye ushahidi bora).*")

    # ---- Q2: remove PAIR ----
    L.append("\n## Q2 — Ukiondoa PAIR, edge inapotea?\n")
    with_pair, n_wp = stat(aconds, nrep=NREP)
    no_pair_conds = {k: v for k, v in aconds.items() if k != "pair"}
    no_pair, n_np = stat(no_pair_conds, nrep=NREP)
    L.append(f"- na PAIR ({akey[1]}): EV={with_pair['ev']:+.2f}, P(edge)={with_pair['bayes']*100:.0f}% (N={n_wp:,})")
    L.append(f"- bila PAIR (pooled pairs): EV={no_pair['ev']:+.2f}, P(edge)={no_pair['bayes']*100:.0f}% (N={n_np:,})")
    pair_identity = with_pair["ev"] - no_pair["ev"] > 0.3 or (is_candidate(with_pair) and not is_candidate(no_pair))
    L.append(f"\n→ {'✅ edge INAPOTEA bila pair → PAIR ni sehemu ya IDENTITY' if pair_identity else '⚠️ edge inabaki bila pair → pair = modifier'}.")

    # ---- Q3: remove STATE (vol) ----
    L.append("\n## Q3 — Ukiondoa STATE (volatility), edge inapotea?\n")
    no_vol_conds = {k: v for k, v in aconds.items() if k != "vol"}
    no_vol, n_nv = stat(no_vol_conds, nrep=NREP)
    L.append(f"- na STATE ({akey[2]}): EV={with_pair['ev']:+.2f}, P(edge)={with_pair['bayes']*100:.0f}%")
    L.append(f"- bila STATE (pooled vol): EV={no_vol['ev']:+.2f}, P(edge)={no_vol['bayes']*100:.0f}% (N={n_nv:,})")
    vol_identity = with_pair["ev"] - no_vol["ev"] > 0.3 or (is_candidate(with_pair) and not is_candidate(no_vol))
    L.append(f"\n→ {'✅ STATE ni sehemu ya IDENTITY' if vol_identity else '⚠️ STATE = modifier (edge inabaki bila yake)'}.")

    # ---- Q4: identity vs modifier (leave-one-dim-out) ----
    L.append("\n## Q4 — Variables zipi ni IDENTITY, zipi ni MODIFIERS? (leave-one-out ablation)\n")
    L.append("| dimension iliyoondolewa | EV bila yake | P(edge) bila yake | ΔEV | jukumu |")
    L.append("|-------------------------|--------------|-------------------|-----|--------|")
    for dim in DIMS:
        sub = {k: v for k, v in aconds.items() if k != dim}
        s, ns = stat(sub, nrep=120)
        dev = with_pair["ev"] - s["ev"]
        ident = dev > 0.3 or (is_candidate(with_pair) and not is_candidate(s))
        L.append(f"| {dim} ({aconds[dim]}) | {s['ev']:+.2f} | {s['bayes']*100:.0f}% | {dev:+.2f} | "
                 f"{'IDENTITY' if ident else 'modifier'} |")
    L.append("\n→ dimension yenye ΔEV kubwa (edge inaporomoka ikiondolewa) = IDENTITY; ndogo = modifier.")

    # ---- Q5: hierarchy ----
    L.append("\n## Q5 — Hierarchy: alpha inazaliwa ngazi gani? (event → pair → vol → spread → session)\n")
    L.append("| ngazi | context | N | EV | P(edge) |")
    L.append("|-------|---------|---|----|---------|")
    order = ["event"] + DIMS
    for j in range(1, len(order) + 1):
        sub = {k: aconds[k] for k in order[:j]}
        s, ns = stat(sub, nrep=120)
        label = " · ".join(str(aconds[k]) for k in order[:j])
        L.append(f"| {j} | {label} | {ns:,} | {s['ev']:+.2f} | {s['bayes']*100:.0f}% |")
    L.append("\n→ ngazi ambapo EV inageuka chanya/Candidate = hapo ndipo alpha inazaliwa (pair peke yake au full stack?).")

    L.append("\n## VERDICT — Phase 13 Contextual Alpha Framework\n")
    if top_objs:
        names = "; ".join(" · ".join(k) for k, _, _ in top_objs[:5])
        L.append(f"→ **Candidate Alpha objects ({n_cand}) zimepatikana** (mf. {names}). Hizi sio events — ni "
                 "**Contextual Alpha Objects** (F-031). Q2/Q3/Q4 zinaonyesha ni dimensions zipi ni IDENTITY "
                 "(edge inategemea) dhidi ya modifiers. ⚠️ Bado **CANDIDATE** (multiple comparisons) — hatua "
                 "inayofuata ni **pre-registered OOS validation** ya hizi objects (sio kufungua strategy bado).")
    else:
        L.append(f"→ ⚠️ Hakuna Candidate Alpha object iliyopita triple criterion baada ya null/bootstrap. "
                 "Edge ya Phase 12 (EURUSD) inaweza kuwa multiple-comparisons artifact. Inahitaji uchunguzi zaidi.")
    L.append("\n*Contextual Alpha: event ni base, context (pair/vol/spread/session) ni IDENTITY (Principle 30). "
             "edge conditional (F-030); universal events hazipo (F-031). Q2/Q3 ablation ya pair/state; Q4 "
             "identity-vs-modifier (leave-one-out); Q5 hierarchy. Candidate Alpha (sio Proven) — multiple "
             "comparisons; OOS validation inahitajika. null=random-direction; Bayesian=Φ(EV/SE). NO ML. "
             "Profitable ≠ Tradable Edge.*")
    out = REPO_ROOT / c["paths"]["reports"] / "contextual_alpha_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)} (Candidate Alpha objects: {n_cand})")
    return 0


def self_test():
    """(1) edge_stat: directional skill -> EV>0, Bayesian~1, candidate. (2) ablation/identity:
       skill ipo TU kwa pair=EURUSD; ukiondoa pair (pool) edge inapotea -> pair=IDENTITY."""
    rng = np.random.default_rng(0)
    # edge_stat core
    fwd = rng.normal(0, 10, 5000); spr = np.full(5000, 1.0)
    d = np.where(rng.random(5000) < 0.62, np.sign(fwd), -np.sign(fwd))
    st = edge_stat(fwd, spr, d, rng, nrep=200)
    core_ok = st["ev"] > 0 and st["bayes"] > 0.95 and st["p"] < 0.05 and is_candidate(st)
    print(f"core: EV={st['ev']:+.2f} bayes={st['bayes']*100:.0f}% p={st['p']:.3f} cand={is_candidate(st)}")

    # identity: build pooled set: EURUSD skillful, others noise
    n1 = 4000; n2 = 12000
    fwd1 = rng.normal(0, 10, n1); d1 = np.where(rng.random(n1) < 0.70, np.sign(fwd1), -np.sign(fwd1))
    fwd2 = rng.normal(0, 10, n2); d2 = rng.choice((-1.0, 1.0), n2)   # noise (other pairs)
    spr1 = np.full(n1, 1.0); spr2 = np.full(n2, 1.0)
    with_pair = edge_stat(fwd1, spr1, d1, rng, nrep=150)             # EURUSD only
    pooled = edge_stat(np.r_[fwd1, fwd2], np.r_[spr1, spr2], np.r_[d1, d2], rng, nrep=150)  # pair removed
    identity_ok = is_candidate(with_pair) and not is_candidate(pooled) and with_pair["ev"] - pooled["ev"] > 0.3
    print(f"identity: with-pair EV={with_pair['ev']:+.2f}(cand={is_candidate(with_pair)}) | "
          f"pooled EV={pooled['ev']:+.2f}(cand={is_candidate(pooled)}) -> pair=IDENTITY {identity_ok}")

    ok = core_ok and identity_ok
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default=None)
    ap.add_argument("--reps", type=int, default=None)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    global NREP
    if a.reps:
        NREP = a.reps
    c = cfg()
    pairs = [a.symbol] if a.symbol else c["pairs"]
    return run(pairs, None)


if __name__ == "__main__":
    raise SystemExit(main())
