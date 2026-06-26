"""
mechanism_discovery.py — PHASE 5.9 (Chief Quant). Mechanism Discovery.

Phase 5.8 (F-014): interaction cells HAZIJAWA universal across pairs (0/20).
Lakini Chief observation (F-015, hypothesis): interaction IPO — kinachobadilika
ni MAPPING, sio MECHANISM. EURUSD best = HIGH×HIGH×Tmid; GBPJPY best =
LOW×NORMAL×Thi — lakini zote zinaweza kuwa "Transition into Expansion".

    Markets have different COORDINATES, but the same PHYSICS.

Hii inajaribu: je best cells za pairs tofauti zina SIGNATURE ya kimazingira
inayofanana (mechanism moja), hata kama labels (LOW/NORMAL/HIGH) ni tofauti?

Mbinu — kila instance inapata SIGNATURE huru na labels (per-pair normalized):
  vol_z · vol_slope · act_z · act_slope · spr_z · lifecycle(age) · transition(pchg)
Kisha kwa kila pair tunachukua TOP-K interaction cells (kwa EV), tunapooli
instances zao -> "pair edge signature", na kuipa JINA la mechanism (rule):
  Expansion · Exhaustion · Compression · Recovery · Neutral

Tunapima:
  • Cell-label agreement (Jaccard ya top cells kuvuka pairs)  — tarajio NDOGO (F-014)
  • Mechanism agreement (modal mechanism freq)                — kubwa => F-015
  • Signature similarity (cosine ya edge signatures)          — kubwa => F-015

Verdict: mechanism/signature agreement >> cell agreement -> "Universal mechanisms,
local coordinates" (F-015). Sio cell similarity bali MECHANISM similarity (Chief).

NO ML — representation/mechanism discovery (descriptive). Outcome = forward net.

Reuse: market_state_engine, state_context_engine, event_library, context_value.

Output: reports/mechanism_discovery_report.md
Endesha: python src/research/mechanism_discovery.py
Self-test: python src/research/mechanism_discovery.py --self-test
"""
from __future__ import annotations

import argparse, sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np
import duckdb

from market_state_engine import (cfg, pip, time_col, h1_from_ticks, rollup, state_df)
from state_context_engine import context_for_dim, _bidx
from event_library import EVENTS_ALL
from context_value import HORIZON

REPO_ROOT = Path(__file__).resolve().parents[2]
TFS = ["H1", "H2", "H4", "D1"]
TIER1 = ["mean_reversion", "pullback", "deep_pullback", "trend_continuation"]
VOLL = ["LOW", "NORMAL", "HIGH"]; ACTL = ["LOW", "NORMAL", "HIGH"]; TRANSL = ["Tlo", "Tmid", "Thi"]
SIG_DIM = 7             # vol_z, vol_slope, act_z, act_slope, spr_z, age, pchange
MIN_CELL = 80           # instances za chini kwa cell (per pair)
TOPK = 3                # top cells kwa pair kuunda edge signature
_posix = lambda p: str(p).replace("\\", "/")


def _pchg_bucket(p):
    if not np.isfinite(p):
        return None
    return "Tlo" if p < 0.08 else ("Tmid" if p < 0.15 else "Thi")


def _z(x):
    m, s = np.nanmean(x), np.nanstd(x)
    return (x - m) / s if s > 1e-12 else np.zeros_like(x)


def _slope_z(x, k=5):
    """(x - trailing mean_k) z-normalized -> rising(+)/falling(−)."""
    n = len(x); base = np.copy(x)
    for i in range(n):
        lo = max(0, i - k)
        base[i] = x[i] - np.mean(x[lo:i]) if i > lo else 0.0
    return _z(base)


def signatures(df, pp):
    """Rudisha (sig[N×7], vs, acts, trans, age) kwa kila bar (per-pair normalized)."""
    atr = df["atr"].to_numpy() / pp; tc = df["tc"].to_numpy().astype(float)
    spr = df["spr"].to_numpy(); spr = np.where(np.isfinite(spr), spr, np.nanmedian(spr))
    vol_z = _z(atr); vol_sl = _slope_z(atr); act_z = _z(tc); act_sl = _slope_z(tc); spr_z = _z(spr)
    vs = df["volatility_state"].to_list(); acts = df["activity_state"].to_list()
    vage, vpchg = context_for_dim(vs)
    age_n = np.array([_bidx(int(a)) / 3.0 if a > 0 else np.nan for a in vage])
    pchg = np.where(np.isfinite(vpchg), vpchg, np.nan)
    sig = np.column_stack([vol_z, vol_sl, act_z, act_sl, spr_z, age_n, pchg])
    return sig, vs, acts, [_pchg_bucket(p) for p in vpchg], vage


def mechanism_name(s):
    """Jina la mechanism kutoka edge signature [vol_z,vol_sl,act_z,act_sl,spr_z,age,pchg]."""
    vol_z, vol_sl, act_z, act_sl, spr_z, age, pchg = s
    if vol_z > 0.3 and age >= 0.6 and (pchg == pchg and pchg > 0.12):
        return "Exhaustion"
    if vol_z > 0.3 and vol_sl > 0:
        return "Expansion"
    if vol_z < -0.2 and vol_sl < 0:
        return "Compression"
    if vol_sl > 0.2:
        return "Recovery"
    return "Neutral"


def _cos(a, b):
    a = np.array(a); b = np.array(b)
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb)) if na > 1e-9 and nb > 1e-9 else float("nan")


def process_df(df, pp, sym, acc):
    close = df["c"].to_numpy() / pp; high = df["h"].to_numpy() / pp; low = df["l"].to_numpy() / pp
    spr = df["spr"].to_numpy(); spr = np.where(np.isfinite(spr), spr, 0.0)
    sig, vs, acts, trans, vage = signatures(df, pp)
    n = len(close)
    for ev in TIER1:
        s = EVENTS_ALL[ev](close, high, low)
        store = acc[ev].setdefault(sym, {})
        for i in range(n):
            if s[i] == 0 or i + HORIZON >= n or vs[i] == "UNKNOWN":
                continue
            a = acts[i] if acts[i] != "UNKNOWN" else None
            tr = trans[i]
            if a is None or tr is None or not np.all(np.isfinite(sig[i])):
                continue
            net = s[i] * (close[i + HORIZON] - close[i]) - spr[i]
            cell = (vs[i], a, tr)
            d = store.setdefault(cell, [0.0, 0, np.zeros(SIG_DIM)])
            d[0] += net; d[1] += 1; d[2] += sig[i]


def pair_edge(store):
    """Rudisha (topcells[list], edge_sig[7], mech) kutoka top-K cells za pair."""
    cells = [(c, d[0] / d[1], d[1], d[2] / d[1]) for c, d in store.items() if d[1] >= MIN_CELL]
    if len(cells) < TOPK:
        return None
    cells.sort(key=lambda x: x[1], reverse=True)
    top = cells[:TOPK]
    # edge signature = weighted mean signature ya top cells
    tot = sum(t[2] for t in top)
    esig = sum(t[3] * t[2] for t in top) / tot
    return [t[0] for t in top], esig, mechanism_name(esig)


def _jaccard(sets):
    js = []
    for i in range(len(sets)):
        for j in range(i + 1, len(sets)):
            u = sets[i] | sets[j]; inter = sets[i] & sets[j]
            js.append(len(inter) / len(u) if u else 0.0)
    return float(np.mean(js)) if js else float("nan")


def run(pairs, tfs):
    c = cfg(); raw = REPO_ROOT / c["paths"]["raw_ticks"]
    if not raw.exists():
        print(f"HITILAFU: '{raw}' haipo.", file=sys.stderr); return 1
    con = duckdb.connect()
    acc = {ev: {} for ev in TIER1}
    for sym in pairs:
        base = raw / f"symbol={sym}"
        if not base.exists() or not list(base.rglob("*.parquet")):
            print(f"  {sym}: (hakuna data)"); continue
        src = _posix(base / "**" / "*.parquet")
        t = time_col(con, src); pp = pip(sym)
        print(f"  {sym}: nascan H1...", flush=True)
        h1 = h1_from_ticks(con, src, t, pp)
        for tf in tfs:
            df = state_df(rollup(h1, tf), tf)
            process_df(df, pp, sym, acc)
        print("    done", flush=True)

    L = ["# Mechanism Discovery — universal mechanisms, local coordinates? (Phase 5.9, Tier 1)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | per-pair top-{TOPK} cells (vol×act×trans) → environmental "
         "SIGNATURE (vol_z/slope, act_z/slope, spr_z, lifecycle, transition) → mechanism name | "
         "mechanism similarity vs cell similarity*\n",
         "> **Q-012 (Chief / F-015):** cells hazikuwa universal (F-014). Lakini je best cells za pairs "
         "tofauti zina MECHANISM ileile (Expansion/Exhaustion/…)? Markets = coordinates tofauti, physics "
         "ileile? Mechanism agreement >> cell agreement -> F-015. NO ML.\n"]
    sup = 0; tot = 0
    for ev in TIER1:
        edges = {sym: pair_edge(store) for sym, store in acc[ev].items()}
        edges = {s: e for s, e in edges.items() if e}
        if len(edges) < 2:
            L.append(f"\n## {ev}\n*(pairs <2 zenye data ya kutosha)*"); continue
        tot += 1
        L.append(f"\n## {ev}\n")
        L.append("| pair | top cells (vol×act×trans) | mechanism | vol_z | vol_slope | age | pchg |")
        L.append("|------|---------------------------|-----------|-------|-----------|-----|------|")
        for sym, (cells, esig, mech) in edges.items():
            cellstr = "; ".join("×".join(c) for c in cells)
            L.append(f"| {sym} | {cellstr} | **{mech}** | {esig[0]:+.2f} | {esig[1]:+.2f} | "
                     f"{esig[5]:.2f} | {esig[6]:.2f} |")
        # metrics
        label_sets = [set("×".join(c) for c in cells) for cells, _, _ in edges.values()]
        cell_agree = _jaccard(label_sets)
        mechs = [m for _, _, m in edges.values()]
        modal_m, modal_c = Counter(mechs).most_common(1)[0]
        mech_agree = modal_c / len(mechs)
        sigs = [e[1] for e in edges.values()]
        coss = [_cos(sigs[i], sigs[j]) for i in range(len(sigs)) for j in range(i + 1, len(sigs))]
        sig_sim = float(np.nanmean(coss)) if coss else float("nan")
        f015 = (mech_agree > cell_agree + 0.2 and sig_sim > 0.5)
        sup += 1 if f015 else 0
        L.append(f"\n→ cell-label agreement = {cell_agree:.2f} | mechanism agreement = {mech_agree:.2f} "
                 f"(modal **{modal_m}**) | signature similarity = {sig_sim:+.2f} → "
                 f"{'✅ F-015 (universal mechanism, local coordinates)' if f015 else '— mechanism haijafanana'}")

    L.append("\n## VERDICT — F-015: universal mechanisms, local coordinates?\n")
    if tot:
        L.append(f"- Events zinazounga mkono F-015: **{sup}/{tot}** (mechanism agreement >> cell agreement "
                 "NA signature similarity >0.5).")
        if sup > tot / 2:
            L.append("\n→ ✅ **F-015 imeungwa mkono**: best cells tofauti kwa pairs zinashiriki MECHANISM "
                     "ileile (signature) licha ya labels tofauti. Interaction Engine ijifunze MECHANISMS "
                     "(Expansion/Exhaustion/…), kila pair ina-map coordinates zake. → Mechanism Library.")
        else:
            L.append("\n→ ⚠️ Mechanism similarity haijawa wazi; inahitaji signature richer au mechanism "
                     "taxonomy bora kabla ya Mechanism Library.")
    L.append("\n*Signature ni per-pair normalized (huru na labels). Mechanism = JINA kutoka signature "
             "(physics), sio cell label (coordinate). Mechanism similarity (cosine) > cell similarity "
             "(Jaccard) = F-015. Hii ni MECHANISM similarity, sio cell similarity (Chief). Inayofuata: "
             "Mechanism Library (Phase 6). NO ML bado. Profitable ≠ Tradable Edge.*")
    out = REPO_ROOT / c["paths"]["reports"] / "mechanism_discovery_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """(1) F-015 case: pairs 2 zenye CELLS tofauti lakini SIGNATURE ileile (high vol_z,
       rising) -> mechanism sawa, cell agreement ndogo, signature similarity juu.
       (2) mechanism_name + cosine logic."""
    # mechanism naming
    exp = mechanism_name([0.8, 0.5, 0.3, 0.1, 0.0, 0.3, 0.05])
    exh = mechanism_name([0.9, -0.1, 0.2, 0.0, 0.0, 0.8, 0.20])
    comp = mechanism_name([-0.5, -0.4, -0.2, 0.0, 0.0, 0.3, 0.05])
    name_ok = (exp == "Expansion" and exh == "Exhaustion" and comp == "Compression")
    print(f"mechanism_name: Expansion={exp=='Expansion'} Exhaustion={exh=='Exhaustion'} Compression={comp=='Compression'}")

    # build two fake pair stores: different top cells, same edge signature region
    def store_with(cells_sig):
        st = {}
        for cell, sig in cells_sig:
            st[cell] = [50.0, 100, np.array(sig) * 100]   # EV ~0.5, n=100, sig sum
        return st
    expsig = [0.8, 0.5, 0.4, 0.2, 0.0, 0.3, 0.05]
    pA = store_with([(("HIGH", "HIGH", "Tmid"), expsig),
                     (("HIGH", "NORMAL", "Tmid"), expsig),
                     (("NORMAL", "HIGH", "Thi"), expsig)])
    pB = store_with([(("LOW", "NORMAL", "Thi"), expsig),
                     (("NORMAL", "LOW", "Thi"), expsig),
                     (("LOW", "LOW", "Tmid"), expsig)])
    eA, eB = pair_edge(pA), pair_edge(pB)
    mech_same = eA[2] == eB[2] == "Expansion"
    sig_sim = _cos(eA[1], eB[1])
    cell_ag = _jaccard([set("×".join(c) for c in eA[0]), set("×".join(c) for c in eB[0])])
    f015_ok = mech_same and sig_sim > 0.9 and cell_ag < 0.3
    print(f"F-015: mech_same={mech_same} sig_sim={sig_sim:.2f} cell_agreement={cell_ag:.2f} -> {f015_ok}")

    ok = name_ok and f015_ok
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
    tfs = [a.tf] if a.tf else TFS
    return run(pairs, tfs)


if __name__ == "__main__":
    raise SystemExit(main())
