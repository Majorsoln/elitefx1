"""
triple_barrier_design.py — PHASE 5 (Chief Quant approved). Triple Barrier Design.

F-009: context sensitivity ni EVENT-SPECIFIC. Tier 1 events (mean_reversion,
pullback, deep_pullback, trend_continuation) zinanufaika zaidi na context na
zina Top10 EV>0. Sasa (kwa MARA YA KWANZA) tunaidhinishwa kujenga OUTCOME
framework — Triple Barrier labeling — kwa TIER 1 PEKEE.

⚠️ Profitable ≠ Tradable Edge: hizi ni pips, bila transaction model kamili, bila
walk-forward ya outcome. Hii ni DESIGN/diagnostics ya barrier, sio edge.

Triple Barrier (kwa kila event entry, no-lookahead forward):
  σ = ATR(14) pips @ entry.
  Upper/Lower barrier = entry ± k·σ  (kwa mwelekeo wa trade; long: TP juu, SL chini).
  Vertical barrier = N bars.
  Outcome = barrier ya KWANZA kugusa: TP | SL | TIME (vertical).
  (Same-bar TP&SL -> SL, conservative.)

Maswali (Chief):
  1. Barrier width gani?    k ∈ {0.5, 1.0, 1.5, 2.0} σ
  2. Vertical gani?         N ∈ {3, 5, 10, 20} bars
  3. Kwa kila event: P(TP), P(SL), P(TIME)
  4. Je hubadilika kwa CONTEXT DECILE? (context score = Phase 3.5)

NO ML / LightGBM / RF / XGBoost (Chief). Design tu.

Reuse: market_state_engine (bars/states/atr), state_context_engine (age),
event_library (Tier 1 signals), context_value (HORIZON/MIN_OBS kwa context score).

Output: reports/triple_barrier_design_report.md
Endesha: python src/research/triple_barrier_design.py
         python src/research/triple_barrier_design.py --symbol EURGBP --tf H1
Self-test: python src/research/triple_barrier_design.py --self-test
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
from context_value import HORIZON, MIN_OBS

REPO_ROOT = Path(__file__).resolve().parents[2]
TFS = ["H1", "H2", "H4", "D1"]
TIER1 = ["mean_reversion", "pullback", "deep_pullback", "trend_continuation"]
KS = [0.5, 1.0, 1.5, 2.0]            # barrier width (× σ)
NS = [3, 5, 10, 20]                  # vertical (bars)
MAXN = max(NS)
REF_K, REF_N = 1.0, 10               # reference combo kwa decile analysis
OUT = ["TP", "SL", "TIME"]
_posix = lambda p: str(p).replace("\\", "/")


def first_touch(i, d, ksig, close, high, low, n):
    """Bar ya kwanza (1..MAXN) ambapo TP au SL inaguswa. Rudisha (touch_bar, outcome).
    Same-bar TP&SL -> SL (conservative). Isiyoguswa -> (MAXN+1, 'TIME')."""
    entry = close[i]
    for j in range(1, MAXN + 1):
        if i + j >= n:
            break
        hi = high[i + j] - entry; lo = low[i + j] - entry
        if d == 1:
            sl = lo <= -ksig; tp = hi >= ksig
        else:
            sl = hi >= ksig; tp = lo <= -ksig
        if sl:                      # SL kwanza (pia kama zote mbili)
            return j, "SL"
        if tp:
            return j, "TP"
    return MAXN + 1, "TIME"


def process_df(df, pp, pools):
    """Sasisha pools[event] = dict(grid, dec) kwa df moja (pair×TF)."""
    close = df["c"].to_numpy() / pp; high = df["h"].to_numpy() / pp; low = df["l"].to_numpy() / pp
    atr_pips = df["atr"].to_numpy() / pp
    spr = df["spr"].to_numpy(); spr = np.where(np.isfinite(spr), spr, 0.0)
    vol_states = df["volatility_state"].to_list()
    age, _ = context_for_dim(vol_states)
    n = len(close)
    for ev in TIER1:
        sig = EVENTS_ALL[ev](close, high, low)
        P = pools[ev]; ev_hist = P["_evh"]
        for i in range(n):
            if sig[i] == 0 or i + MAXN >= n:
                continue
            vs = vol_states[i]; s = atr_pips[i]
            if vs == "UNKNOWN" or age[i] <= 0 or not (s > 0):
                continue
            key = (vs, _bidx(int(age[i])))
            eh = ev_hist.get(key)
            score = (eh[0] / eh[1]) if (eh and eh[1] >= MIN_OBS) else np.nan
            d = sig[i]
            # barrier touches per k
            ref_out = None
            for k in KS:
                tb, oc = first_touch(i, d, k * s, close, high, low, n)
                for N in NS:
                    out = oc if tb <= N else "TIME"
                    P["grid"][(k, N)][out] += 1
                    if k == REF_K and N == REF_N:
                        ref_out = out
            if np.isfinite(score) and ref_out is not None:
                P["dec"].append((score, ref_out))
            # update context-score history (Phase 3.5 style; net forward HORIZON)
            net = d * (close[i + HORIZON] - close[i]) - spr[i]
            ev_hist.setdefault(key, [0.0, 0]); ev_hist[key][0] += net; ev_hist[key][1] += 1


def _new_pool():
    return dict(grid={(k, N): Counter() for k in KS for N in NS}, dec=[], _evh={})


def decile_probs(dec):
    """Rudisha list ya (p_tp, p_sl, p_time, n) kwa deciles 10 (chini->juu kwa score)."""
    if len(dec) < 200:
        return None
    dec = sorted(dec, key=lambda x: x[0])
    m = len(dec); out = []
    for q in range(10):
        seg = [o for _, o in dec[q * m // 10:(q + 1) * m // 10]]
        c = Counter(seg); tot = len(seg) or 1
        out.append((c["TP"] / tot, c["SL"] / tot, c["TIME"] / tot, len(seg)))
    return out


def run(pairs, tfs):
    c = cfg(); raw = REPO_ROOT / c["paths"]["raw_ticks"]
    if not raw.exists():
        print(f"HITILAFU: '{raw}' haipo.", file=sys.stderr); return 1
    con = duckdb.connect()
    pools = {ev: _new_pool() for ev in TIER1}
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
            process_df(df, pp, pools)
            print(f"    {tf}: done", flush=True)

    L = ["# Triple Barrier Design — outcome framework (Phase 5, Tier 1 events)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | σ=ATR(14) pips @entry | barrier k∈{KS}σ × vertical N∈{NS} bars "
         f"| outcome = first touch (TP/SL/TIME) | context score = Phase 3.5*\n",
         "> **Phase 5 (Chief):** Tier 1 events PEKEE. ⚠️ **Profitable ≠ Tradable Edge** — hizi ni pips, "
         "bila transaction model kamili, barrier labeling design, hakuna walk-forward. NO ML (Chief). "
         "Swali: barrier/vertical gani? P(TP/SL/TIME)? je hubadilika kwa context decile?\n"]
    for ev in TIER1:
        P = pools[ev]
        L.append(f"\n## {ev}\n")
        L.append("### P(TP) / P(SL) / P(TIME) % — barrier (σ) × vertical (bars)\n")
        L.append("| σ \\ N | " + " | ".join(str(N) for N in NS) + " |")
        L.append("|-------|" + "----|" * len(NS))
        for k in KS:
            cells = []
            for N in NS:
                cc = P["grid"][(k, N)]; tot = sum(cc.values()) or 1
                cells.append(f"{100*cc['TP']/tot:.0f}/{100*cc['SL']/tot:.0f}/{100*cc['TIME']/tot:.0f}")
            L.append(f"| {k:.1f} | " + " | ".join(cells) + " |")
        # context decile (ref k,N)
        dp = decile_probs(P["dec"])
        L.append(f"\n### P(TP) kwa CONTEXT DECILE (ref {REF_K:.1f}σ, {REF_N} bars; D1=chini→D10=juu)\n")
        if dp is None:
            L.append("*(scored instances <200 — haitoshi)*")
        else:
            L.append("| decile | P(TP) | P(SL) | P(TIME) | n |")
            L.append("|--------|-------|-------|---------|---|")
            for q, (ptp, psl, pti, nn) in enumerate(dp, 1):
                L.append(f"| D{q} | {ptp*100:.0f}% | {psl*100:.0f}% | {pti*100:.0f}% | {nn:,} |")
            d_tp = dp[9][0] - dp[0][0]
            L.append(f"\n→ P(TP) D10−D1 = **{d_tp*100:+.0f}pp** "
                     f"({'✅ context inaboresha odds za TP' if d_tp > 0.01 else '— flat'})")

    L.append("\n---\n*Triple Barrier = OUTCOME LABELING design (Tier 1, F-009). σ=ATR @entry; barriers "
             "zime-LOCK @entry (no resizing, no-lookahead). Same-bar TP&SL=SL (conservative). P(TP) "
             "ikipanda na context decile = context inaboresha outcome odds (sio EV tu). ⚠️ Profitable ≠ "
             "Tradable Edge — bado hakuna transaction model/walk-forward/ML. Inayofuata (Chief): Outcome "
             "Engine + EV(context) kamili. NO ML mpaka Event+Context+Outcome vihakikiwe.*")
    out = REPO_ROOT / c["paths"]["reports"] / "triple_barrier_design_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)} (Tier 1: {', '.join(TIER1)})")
    return 0


def self_test():
    """(1) first_touch: TP/SL/TIME kwenye paths zinazojulikana.
       (2) decile_probs: score inayohusiana na P(TP) -> D10 P(TP) > D1."""
    # path: entry=100, k*σ=1 -> TP @ +1. bar1 ndani ya band; bar2 high=102 -> TP
    close = np.array([100, 100.3, 101.0, 101.0, 101.0], float)
    high = np.array([100, 100.5, 102.0, 102.0, 102.0], float)   # bar1 +0.5 (<1), bar2 +2 -> TP
    low = np.array([100, 99.6, 100.5, 100.5, 100.5], float)     # never <= -1 (no SL)
    tb, oc = first_touch(0, 1, 1.0, close, high, low, len(close))   # k*σ=1 -> TP @ +1
    tp_ok = (oc == "TP" and tb == 2)
    # SL path: low hits 98.5
    low2 = np.array([100, 98.5, 98.5, 98.5, 98.5], float)
    high2 = np.array([100, 100.2, 100.2, 100.2, 100.2], float)
    tb2, oc2 = first_touch(0, 1, 1.0, close, high2, low2, len(close))
    sl_ok = (oc2 == "SL" and tb2 == 1)
    # TIME path: flat within band
    flat = np.full(25, 100.0)
    tb3, oc3 = first_touch(0, 1, 1.0, flat, flat + 0.2, flat - 0.2, len(flat))
    time_ok = (oc3 == "TIME")
    print(f"first_touch: TP={tp_ok} SL={sl_ok} TIME={time_ok}")

    # decile: P(TP) rises with score
    rng = np.random.default_rng(0); N = 8000
    latent = rng.normal(0, 1, N)
    outs = ["TP" if rng.random() < 1 / (1 + np.exp(-latent[i])) else "SL" for i in range(N)]
    dec = list(zip(latent + rng.normal(0, 0.3, N), outs))
    dp = decile_probs(dec)
    dec_ok = dp is not None and dp[9][0] > dp[0][0] + 0.2
    print(f"decile P(TP): D1={dp[0][0]:.2f} D10={dp[9][0]:.2f} (rises={dec_ok})")

    ok = tp_ok and sl_ok and time_ok and dec_ok
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
