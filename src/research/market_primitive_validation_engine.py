"""
market_primitive_validation_engine.py — PHASE 24 (Chief Quant).

Phase 23 ilithibitisha (APPROVED): kuna **Emerging Core Vocabulary** — `Compression (Quiet
Coil)` ndiyo label pekee yenye consistency ya kweli cross-pair NA cross-event; labels ni
stable kwa thresholds; rule vocabulary inarecoverable data-driven (ARI ~0.62, sio kamili —
NZURI: semantics ni abstraction, sio copy ya clustering).

Chief discovery: `Compression` si event, si pair, si geometry — ni **MARKET CONDITION**. Labda
soko lina seti ndogo ya **MARKET PRIMITIVES** zinazojitokeza tena na tena kwenye events tofauti.
Architecture inageuka: Market → **Market Primitives** → Events → Representations.

  Principle 51: market knowledge iandikwe kwa **reusable market primitives**, sio event labels.
  Principle 52: semantics ihifadhi CONCEPTS, sio kurudia clustering kikamilifu.
  F-041 (OPEN): seti ndogo ya universal market primitives inaweza kuwepo (candidate: Compression).

Swali kuu: primitive ni MECHANISM au DESCRIPTION? (cause au consequence?)

Maswali (Chief):
  Q1. Je Compression ina tabia ile ile kwa events ZOTE?
  Q2. Je Compression inatokea KABLA ya breakout / pullback / mean_reversion? (precedence)
  Q3. Je primitive ina transitions zake? (Compression → Expansion → Exhaustion)
  Q4. Je primitives zinaweza kujengwa BILA Event labels kabisa? (KEY — layer ya juu zaidi)
  Q5. Je primitives zinaongea lugha ya market, au ni majina tu kwenye clusters?

Mbinu: jenga per-bar market-state STREAM (kila bar, BILA kuiweka kwenye event); cluster ->
market primitives (robust norm + kmeans, GLOBAL — sio event-specific); name kwa semantic_label;
pima precedence (window kabla ya event), transitions (bar→bar), na cross-event behavior. NO ML.

Reuse: market_state_engine (cfg, pip), latent_structure (kmeans, state_path), event_library
(EVENTS_ALL), configuration_engine (EVENTS_SET, VERT), context_value (HORIZON),
event_taxonomy_engine (FEAT, VLEVEL, TRAJ_WIN, _runlen), semantic_taxonomy_engine
(semantic_label, GENERIC, distinctiveness), cluster_robustness (ari).

Output: reports/market_primitive_validation_report.md
Self-test: python src/research/market_primitive_validation_engine.py --self-test
"""
from __future__ import annotations

import argparse, sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
import polars as pl

from market_state_engine import cfg, pip
from latent_structure import kmeans, state_path
from event_library import EVENTS_ALL
from configuration_engine import EVENTS_SET, VERT
from context_value import HORIZON
from event_taxonomy_engine import FEAT, VLEVEL, TRAJ_WIN, _runlen
from semantic_taxonomy_engine import semantic_label, GENERIC, distinctiveness

REPO_ROOT = Path(__file__).resolve().parents[2]
TFS = ["H1", "H2", "H4", "D1"]
KP = 5                      # idadi ya market primitives
FIT_CAP = 6000             # cap ya kmeans fit (assign all bars)
PRE_WIN = 5                # window kabla ya event (precedence Q2)
COMPRESSION = "Compression (Quiet Coil)"
IVOL = 0                    # FEAT index ya vol


# ---------- bar stream (EVENT-FREE) ----------
def build_bar_stream(pairs):
    """Kila bar (sio event-filtered): B (bars×FEAT), evt (event->0/1 per bar), sid (series id)."""
    B, sid = [], []
    evt = {e: [] for e in EVENTS_SET}
    no_px = True
    s = 0
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
            vol = df["volatility_state"].to_list(); act = df["activity_state"].to_list()
            sprst = df["spread_state"].to_list()
            rl = _runlen(vol); Lv = np.array([VLEVEL.get(v, 1.0) for v in vol])
            n = len(close)
            sig = {e: EVENTS_ALL[e](close, high, low) for e in EVENTS_SET}
            for i in range(n):
                if not (atr[i] > 0):
                    continue
                traj = (1.0 if i >= TRAJ_WIN and Lv[i] > Lv[i - TRAJ_WIN]
                        else -1.0 if i >= TRAJ_WIN and Lv[i] < Lv[i - TRAJ_WIN] else 0.0)
                trans = 1.0 if i >= 1 and vol[i] != vol[i - 1] else 0.0
                B.append([VLEVEL.get(vol[i], 1.0), VLEVEL.get(act[i], 1.0),
                          1.0 if sprst[i] == "WIDE" else 0.0, atr[i], traj,
                          min(rl[i], 30.0), trans])
                for e in EVENTS_SET:
                    evt[e].append(1 if sig[e][i] != 0 else 0)
                sid.append(s)
            s += 1
        print(f"  {sym}: stream built", flush=True)
    B = np.array(B, float); sid = np.array(sid, np.int64)
    evt = {e: np.array(v, np.int8) for e, v in evt.items()}
    return B, evt, sid, no_px


# ---------- primitives (no events used) ----------
def fit_primitives(B, rng, k=KP):
    """Robust-normalize + kmeans fit kwenye subsample; rudisha fit dict (assign all bars)."""
    med = np.median(B, 0); mad = np.median(np.abs(B - med), 0) * 1.4826; mad[mad < 1e-9] = 1.0
    Z = (B - med) / mad
    idx = rng.choice(len(Z), min(len(Z), FIT_CAP), replace=False)
    cen, _ = _km_fit(Z[idx], k, rng)
    mu = B.mean(0); sd = B.std(0); sd[sd < 1e-9] = 1.0
    return dict(med=med, mad=mad, cen=cen, mu=mu, sd=sd, k=k)


def _km_fit(Z, k, rng):
    lab, cen, _ = kmeans(Z, k, rng)
    return cen, lab


def assign_primitives(B, fit):
    Z = (B - fit["med"]) / fit["mad"]
    return ((Z[:, None, :] - fit["cen"][None, :, :]) ** 2).sum(2).argmin(1)


def name_primitives(B, prim, fit):
    """Kwa kila primitive id: raw profile, z (vs global), label, distinct, n."""
    info = {}
    for j in range(fit["k"]):
        m = prim == j
        if not m.any():
            info[j] = dict(n=0, raw=fit["mu"], z=np.zeros_like(fit["mu"]), label=GENERIC, distinct=0.0)
            continue
        raw = B[m].mean(0); z = (raw - fit["mu"]) / fit["sd"]
        info[j] = dict(n=int(m.sum()), raw=raw, z=z, label=semantic_label(raw, z),
                       distinct=float(distinctiveness(raw, z)))
    return info


def _compression_pid(info):
    """Primitive id ya Compression (label), au fallback = vol ya chini zaidi."""
    cand = [j for j, d in info.items() if d["label"] == COMPRESSION and d["n"] > 0]
    if cand:
        return max(cand, key=lambda j: info[j]["n"])
    live = [j for j in info if info[j]["n"] > 0]
    return min(live, key=lambda j: info[j]["raw"][IVOL]) if live else None


# ---------- Q2 precedence ----------
def precedence(prim, evt, sid, target_pid, w=PRE_WIN):
    """Lift = P(target primitive kwenye window kabla ya event) / baseline."""
    baseline = float((prim == target_pid).mean())
    out = {}
    for e, fired in evt.items():
        fracs = []
        idxs = np.where(fired == 1)[0]
        for i in idxs:
            lo = i - w
            if lo < 0 or sid[lo] != sid[i]:
                continue
            window = prim[lo:i]
            if len(window):
                fracs.append(float((window == target_pid).mean()))
        if fracs:
            pre = float(np.mean(fracs))
            out[e] = dict(pre=pre, lift=pre / baseline if baseline > 1e-9 else 0.0, n=len(fracs))
    return baseline, out


# ---------- Q3 transitions ----------
def transitions(prim, sid, info):
    """Transition matrix kati ya primitive LABELS (bar→bar, ndani ya series)."""
    k = len(info)
    M = np.zeros((k, k))
    for i in range(len(prim) - 1):
        if sid[i] == sid[i + 1] and prim[i] != prim[i + 1]:
            M[prim[i], prim[i + 1]] += 1
    row = M.sum(1, keepdims=True); row[row < 1e-9] = 1.0
    P = M / row
    return M, P


def run(pairs, rng):
    c = cfg()
    print("Building EVENT-FREE bar stream...", flush=True)
    B, evt, sid, no_px = build_bar_stream(pairs)
    if no_px:
        print("HITILAFU: state parquet haina OHLC. Endesha market_state_engine.py kwanza.", file=sys.stderr)
        return 1
    if len(B) < 1000:
        print("HITILAFU: bars hazitoshi.", file=sys.stderr)
        return 1
    print(f"  {len(B):,} bars, {len(np.unique(sid))} series", flush=True)
    fit = fit_primitives(B, rng)
    prim = assign_primitives(B, fit)              # Q4: primitives BILA events
    info = name_primitives(B, prim, fit)
    cpid = _compression_pid(info)
    baseline, prec = precedence(prim, evt, sid, cpid)
    M, P = transitions(prim, sid, info)
    return _report(c, pairs, B, evt, sid, fit, prim, info, cpid, baseline, prec, M, P)


def _report(c, pairs, B, evt, sid, fit, prim, info, cpid, baseline, prec, M, P):
    live = [j for j in info if info[j]["n"] > 0]
    n_distinct = sum(1 for j in live if info[j]["distinct"] >= 0.5)
    n_concrete = sum(1 for j in live if info[j]["distinct"] >= 0.5 and info[j]["label"] != GENERIC)
    comp_label = info[cpid]["label"] if cpid is not None else "—"

    L = ["# Market Primitive Validation — primitive ni mechanism au description? (Phase 24)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | {len(pairs)} pairs, {len(B):,} bars (EVENT-FREE) | "
         f"k={fit['k']} primitives (robust norm + kmeans, GLOBAL) | precedence window {PRE_WIN} | NO ML*\n",
         "> **Principle 51 (Chief):** andika market knowledge kwa **reusable market primitives**, sio event "
         "labels. **Principle 52:** semantics ihifadhi concepts, sio kurudia clustering kikamilifu. **F-041 "
         "(OPEN):** seti ndogo ya universal market primitives inaweza kuwepo (candidate: Compression). Swali: "
         "primitive ni mechanism au description (cause au consequence)? NO ML."]

    # Q4 + Q5 — event-free primitives + market language
    L.append("\n## Q4+Q5 — Primitives zilizojengwa BILA event labels (+ je zinaongea lugha ya soko?)\n")
    L.append("| primitive | N | label (market language) | vol | act | spr | traj | distinct | concrete? |")
    L.append("|-----------|---|-------------------------|-----|-----|-----|------|----------|-----------|")
    for j in sorted(live, key=lambda x: -info[x]["n"]):
        d = info[j]; r = d["raw"]
        L.append(f"| Pr{j} | {d['n']:,} | **{d['label']}** | {r[0]:.2f} | {r[1]:.2f} | {r[2]:.2f} | {r[4]:+.2f} | "
                 f"{d['distinct']:.2f} | {'✅' if (d['distinct']>=0.5 and d['label']!=GENERIC) else '—'} |")
    L.append(f"\n- **Q4:** primitives zimejengwa kutoka bar-stream PEKEE (hakuna event label iliyotumika) → "
             f"{'✅ Compression-like primitive IMEJITOKEZA bila events' if comp_label == COMPRESSION else '⚠️ hakuna primitive iliyopata label Compression (fallback = vol ya chini zaidi)'}.")
    L.append(f"- **Q5:** primitives concrete (market label + distinct): **{n_concrete}/{len(live)}** → "
             f"{'✅ zinaongea lugha ya soko' if n_concrete >= max(1, len(live)//2) else '⚠️ nyingi ni majina tu kwenye clusters'}.")

    # Q2 — precedence
    L.append(f"\n## Q2 — Je {comp_label} (Pr{cpid}) inatokea KABLA ya events? (precedence)\n")
    L.append(f"*baseline P(primitive) = {baseline:.3f}. lift>1 = primitive inatangulia event.*\n")
    L.append("| event | P(pre-window) | lift | N events |")
    L.append("|-------|---------------|------|----------|")
    n_precede = 0
    for e in EVENTS_SET:
        if e in prec:
            pr = prec[e]; lead = pr["lift"] > 1.15
            n_precede += int(lead)
            L.append(f"| {e} | {pr['pre']:.3f} | {pr['lift']:.2f}{' ⬆️' if lead else ''} | {pr['n']:,} |")
    L.append(f"\n→ {'✅ Compression INATANGULIA events nyingi (lift>1.15) — dalili ya MECHANISM, sio description tu' if n_precede >= 2 else '⚠️ Compression haitangulii events kwa uthabiti — bado inaweza kuwa description/coincident'}.")

    # Q3 — transitions
    L.append("\n## Q3 — Je primitive ina transitions zake? (Compression → Expansion → …)\n")
    L.append("| from \\ to | " + " | ".join(f"Pr{j}" for j in sorted(live)) + " |")
    L.append("|---" * (len(live) + 1) + "|")
    for i in sorted(live):
        cells = " | ".join(f"{P[i, j]:.2f}" for j in sorted(live))
        L.append(f"| **Pr{i}** ({info[i]['label'][:18]}) | {cells} |")
    # dominant transition kutoka Compression
    if cpid is not None:
        outs = [(j, P[cpid, j]) for j in sorted(live) if j != cpid]
        if outs:
            nxt = max(outs, key=lambda t: t[1])
            L.append(f"\n- transition kubwa kutoka **{comp_label}**: → **{info[nxt[0]]['label']}** (P={nxt[1]:.2f}).")

    # VERDICT
    L.append("\n## VERDICT — Phase 24 Market Primitive Validation\n")
    q4_ok = comp_label == COMPRESSION
    mech = n_precede >= 2
    ok = q4_ok and n_concrete >= max(1, len(live) // 2)
    if ok and mech:
        L.append(f"→ ✅ **{comp_label} ni primitive halisi & ina dalili za MECHANISM**: imejitokeza bila event "
                 f"labels (Q4), inaongea lugha ya soko (Q5: {n_concrete}/{len(live)}), na inatangulia events "
                 f"nyingi (Q2: {n_precede}). **F-041 inaungwa mkono** (bado OPEN). Inayofuata bado SI alpha — "
                 "thibitisha primitives zaidi + cause-vs-consequence. NO ML.")
    elif ok:
        L.append(f"→ 🟡 **{comp_label} ni primitive ya kueleweka (Q4/Q5 ✅) lakini bado DESCRIPTION, sio mechanism "
                 f"thabiti**: precedence dhaifu (Q2: {n_precede}/? events lift>1.15). F-041 partial — primitive "
                 "ipo lakini cause-vs-consequence haijajibiwa. NO ML.")
    else:
        L.append(f"→ ⚠️ **primitive layer bado haijathibitika**: Q4 {'✅' if q4_ok else '❌ (no Compression emerged event-free)'}, "
                 f"Q5 concrete {n_concrete}/{len(live)}. F-041 haijaungwa mkono kikamilifu; inahitaji representation/k bora.")
    L.append("\n**Bado Market Understanding Era — NO alpha.** Hatujui kama Compression ni *cause* au "
             "*consequence*; precedence (Q2) ni dalili, sio uthibitisho wa causality.")

    # HONEST CAVEATS
    L.append("\n## Honest Caveats\n")
    L.append("1. **Primitives hutumia representation COARSE (global robust+kmeans), sio manifold ya event-specific "
             "(F-039).** Hii ni kwa makusudi (primitives = global market conditions) lakini ina maana primitive "
             "geometry si ile ile iliyo-operationalized Phase 21.")
    L.append("2. **Precedence (Q2) ≠ causality.** Lift>1 inaonyesha Compression hutangulia events, lakini "
             "non-stationarity / autocorrelation / overlap ya windows zinaweza kuunda lift bandia. Hakuna "
             "permutation/Granger test hapa — ni dalili, sio cause-vs-consequence proof.")
    L.append("3. **k=5 primitives ni human choice.** Idadi ya primitives na fallback (vol ya chini = Compression) "
             "zinaweza kubadili matokeo; primitive vocabulary bado haijawa canonical (Principle 49 bado).")
    L.append("4. **Primitive ≠ edge (Principle 40/48).** Hata kama Compression ni mechanism, haina alpha "
             "yenyewe; hii ni market structure, sio faida.")
    L.append("5. **'Event-free' si kweli kabisa** — bars zinatoka state engine ile ile; events na primitives "
             "zinashiriki features (vol/act/spr…), kwa hiyo overlap ya information inategemewa, sio independence.")

    L.append("\n*Event-free bar stream → robust norm + kmeans primitives → semantic_label naming; precedence "
             "lift; bar→bar transition matrix. Principle 51/52. F-041 OPEN. NO ML. Profitable ≠ Tradable Edge.*")

    out = REPO_ROOT / c["paths"]["reports"] / "market_primitive_validation_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)} (Compression event-free={q4_ok}, "
          f"concrete {n_concrete}/{len(live)}, precede {n_precede})")
    return 0


def self_test():
    rng = np.random.default_rng(24)
    # Jenga bar stream ya bandia: mzunguko COMPRESSION(low vol) -> EXPANSION(high vol) -> mid,
    # na "event" inayofyatuka mwanzo wa expansion (hivyo compression inatangulia event).
    FEATN = len(FEAT)
    B, sid = [], []
    fired = []
    s = 0
    for series in range(4):
        for cycle in range(60):
            # compression block (low vol) urefu 4
            for _ in range(4):
                B.append([0.0, 0.0, 0.0, 0.05, -1.0, 5.0, 0.0])
                fired.append(0); sid.append(s)
            # expansion block (high vol) urefu 3; event hufyatuka kwenye bar ya kwanza
            for t in range(3):
                B.append([2.0, 2.0, 0.0, 0.30, 1.0, 2.0, 1.0])
                fired.append(1 if t == 0 else 0); sid.append(s)
            # mid block urefu 2
            for _ in range(2):
                B.append([1.0, 1.0, 0.0, 0.15, 0.0, 3.0, 0.0])
                fired.append(0); sid.append(s)
        s += 1
    B = np.array(B, float); sid = np.array(sid, np.int64)
    # ongeza noise kidogo
    B = B + rng.normal(0, 0.02, B.shape)
    evt = {"breakout": np.array(fired, np.int8)}

    fit = fit_primitives(B, rng, k=3)
    prim = assign_primitives(B, fit)
    info = name_primitives(B, prim, fit)
    cpid = _compression_pid(info)
    labels = {info[j]["label"] for j in info if info[j]["n"] > 0}
    ok_q4 = COMPRESSION in labels
    print(f"event-free primitives: {sorted(labels)} | Compression present={ok_q4} -> {'OK' if ok_q4 else 'FAIL'}")

    baseline, prec = precedence(prim, evt, sid, cpid)
    lift = prec["breakout"]["lift"] if "breakout" in prec else 0.0
    ok_q2 = lift > 1.15
    print(f"precedence lift (compression before breakout) = {lift:.2f} (baseline {baseline:.2f}) -> {'OK' if ok_q2 else 'FAIL'}")

    M, P = transitions(prim, sid, info)
    # transition kubwa kutoka compression iende high-vol (expansion)
    outs = [(j, P[cpid, j]) for j in info if j != cpid and info[j]["n"] > 0]
    nxt = max(outs, key=lambda t: t[1]) if outs else (None, 0)
    ok_q3 = nxt[0] is not None and info[nxt[0]]["raw"][IVOL] > info[cpid]["raw"][IVOL]
    print(f"dominant transition from Compression -> {info[nxt[0]]['label'] if nxt[0] is not None else '—'} "
          f"(P={nxt[1]:.2f}) higher-vol={ok_q3} -> {'OK' if ok_q3 else 'FAIL'}")

    ok = ok_q4 and ok_q2 and ok_q3
    print(f"\nSELF-TEST: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    c = cfg()
    return run(c["pairs"], np.random.default_rng(24))


if __name__ == "__main__":
    raise SystemExit(main())
