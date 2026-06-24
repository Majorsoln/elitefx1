"""
event_diagnostics.py — PHASE 3 (Chief Quant approved). Event Diagnostics.

States/Age/Transitions/Context zimethibitishwa (Phase 1–2.1). Sasa tunahamia
EVENTS. Phase 3 HAITAFITI alpha, entries, au outcomes — ni DIAGNOSTICS tu:
tunaelewa events 9 (Event Library) zinavyotokea NDANI ya context.

Kwa kila event (event_library.EVENTS_ALL), tunapima:
  1. FREQUENCY              : mara ngapi hutokea (count + per 1000 bars).
  2. CONTEXT COVERAGE       : % zenye context kamili (state+age+pchange valid),
                              + % "favorable" (vol pchange < 0.5 = state stable).
  3. STATE DISTRIBUTION     : zinatokea kwenye vol/activity state zipi (L/N/H).
  4. AGE DISTRIBUTION       : zinatokea kwenye vol state-age bucket zipi (1-3..16+).
  5. TRANSITION DISTRIBUTION: vol transition gani inafuata (escalate/revert/stay,
                              ndani ya HT bars).

Chanzo: calendar bars (market_state_engine state_df) -> states + atr + OHLC;
context (age, pchange) kutoka state_context_engine (online, no-lookahead). Events
zinasomwa kutoka close/high/low (no-lookahead). Aggregate kuvuka pairs × TFs.

> NO Triple Barrier · NO ML · NO Outcome model (Chief: Event Layer bado
> haijachunguzwa kikamilifu). Hii ni ramani ya event×context, sio strategy.

Output: reports/event_diagnostics_report.md
Endesha: python src/research/event_diagnostics.py
         python src/research/event_diagnostics.py --symbol EURGBP --tf H1
Self-test: python src/research/event_diagnostics.py --self-test
"""
from __future__ import annotations

import argparse, sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
import polars as pl
import duckdb

from market_state_engine import (cfg, pip, time_col, h1_from_ticks, rollup, state_df)
from state_context_engine import context_for_dim, _bidx, BUCKETS
from event_library import EVENTS_ALL

REPO_ROOT = Path(__file__).resolve().parents[2]
TFS = ["H1", "H2", "H4", "D1"]
LEVELS = ["LOW", "NORMAL", "HIGH"]
LVL = {"LOW": 0, "NORMAL": 1, "HIGH": 2}
BLABEL = ["1-3", "4-8", "9-15", "16+"]
HT = 12               # horizon (bars) kwa transition inayofuata
FAVOR_PCHG = 0.5      # favorable context = vol pchange < hii (state stable)
_posix = lambda p: str(p).replace("\\", "/")


def _new_acc():
    return dict(n=0, ctx=0, fav=0,
                vol={l: 0 for l in LEVELS}, act={l: 0 for l in LEVELS},
                age=[0, 0, 0, 0], trans=dict(escalate=0, revert=0, stay=0))


def next_transition(vol_states, i):
    """Vol transition baada ya bar i (ndani ya HT): escalate/revert/stay."""
    cur = vol_states[i]
    if cur not in LVL:
        return None
    for j in range(i + 1, min(i + 1 + HT, len(vol_states))):
        nx = vol_states[j]
        if nx == "UNKNOWN":
            return None
        if nx != cur:
            return "escalate" if LVL[nx] > LVL[cur] else "revert"
    return "stay"


def accumulate(df, acc, total):
    """Sasisha accumulators kwa kila event juu ya df moja (pair×TF)."""
    close = df["c"].to_numpy(); high = df["h"].to_numpy(); low = df["l"].to_numpy()
    vol_states = df["volatility_state"].to_list()
    act_states = df["activity_state"].to_list()
    vol_age, vol_pchg = context_for_dim(vol_states)
    n = len(close); total[0] += n
    for name, fn in EVENTS_ALL.items():
        sig = fn(close, high, low)
        a = acc[name]
        for i in range(n):
            if sig[i] == 0:
                continue
            vs = vol_states[i]
            if vs == "UNKNOWN":
                continue
            a["n"] += 1
            a["vol"][vs] += 1
            if act_states[i] in a["act"]:
                a["act"][act_states[i]] += 1
            if vol_age[i] > 0:
                a["age"][_bidx(int(vol_age[i]))] += 1
            if np.isfinite(vol_pchg[i]):
                a["ctx"] += 1
                if vol_pchg[i] < FAVOR_PCHG:
                    a["fav"] += 1
            tr = next_transition(vol_states, i)
            if tr:
                a["trans"][tr] += 1


def _pct(d, keys, tot):
    return [100 * d[k] / tot if tot else 0.0 for k in keys]


def run(pairs, tfs):
    c = cfg(); raw = REPO_ROOT / c["paths"]["raw_ticks"]
    if not raw.exists():
        print(f"HITILAFU: '{raw}' haipo.", file=sys.stderr); return 1
    con = duckdb.connect()
    acc = {name: _new_acc() for name in EVENTS_ALL}
    total = [0]
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
            accumulate(df, acc, total)
            print(f"    {tf}: done", flush=True)
    tot_bars = total[0]
    if tot_bars == 0:
        print("HITILAFU: hakuna data.", file=sys.stderr); return 1

    L = ["# Event Diagnostics — events 9 ndani ya context (Phase 3)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | events: Event Library (KJ) | aggregate kuvuka pairs × TFs | "
         f"context (vol age/pchange) online no-lookahead | transition horizon {HT} bars | bars={tot_bars:,}*\n",
         "> **Phase 3 (Chief):** tunaelewa events zinavyotokea NDANI ya context (sio alpha/entries). "
         "Diagnostics: frequency · context coverage · state/age/transition distribution. NO Triple Barrier, "
         "NO ML, NO outcomes — Event Layer ramani tu.\n",
         "## 1) Frequency + Context coverage\n",
         "| Event | n | per 1000 bars | ctx coverage | favorable (pchg<0.5) |",
         "|-------|---|---------------|--------------|----------------------|"]
    for name in EVENTS_ALL:
        a = acc[name]; n = a["n"]
        freq = 1000 * n / tot_bars
        cov = 100 * a["ctx"] / n if n else 0.0
        fav = 100 * a["fav"] / a["ctx"] if a["ctx"] else 0.0
        L.append(f"| {name} | {n:,} | {freq:.1f} | {cov:.0f}% | {fav:.0f}% |")

    L.append("\n## 2) State distribution — volatility | activity (% ya events)\n")
    L.append("| Event | vol L/N/H | act L/N/H |")
    L.append("|-------|-----------|-----------|")
    for name in EVENTS_ALL:
        a = acc[name]
        v = _pct(a["vol"], LEVELS, sum(a["vol"].values()))
        ac = _pct(a["act"], LEVELS, sum(a["act"].values()))
        L.append(f"| {name} | {v[0]:.0f}/{v[1]:.0f}/{v[2]:.0f} | {ac[0]:.0f}/{ac[1]:.0f}/{ac[2]:.0f} |")

    L.append("\n## 3) Age distribution — vol state-age bucket (% ya events)\n")
    L.append("| Event | " + " | ".join(BLABEL) + " |")
    L.append("|-------|" + "----|" * len(BLABEL))
    for name in EVENTS_ALL:
        a = acc[name]; tota = sum(a["age"])
        cells = " | ".join(f"{100*x/tota:.0f}" if tota else "0" for x in a["age"])
        L.append(f"| {name} | {cells} |")

    L.append("\n## 4) Transition distribution — vol move inayofuata (% ya events)\n")
    L.append("| Event | escalate | revert | stay |")
    L.append("|-------|----------|--------|------|")
    for name in EVENTS_ALL:
        a = acc[name]; tt = sum(a["trans"].values())
        e, r, s = _pct(a["trans"], ["escalate", "revert", "stay"], tt)
        L.append(f"| {name} | {e:.0f}% | {r:.0f}% | {s:.0f}% |")

    L.append("\n---\n*Phase 3 = ramani ya Event × Context (sio strategy). Inajenga juu ya states/age/"
             "transitions/context zilizothibitishwa (F-001..F-007). Inayofuata (baada ya Chief review): "
             "Event × Context Matrix (Phase 4). Bado HAIRUHUSIWI: Triple Barrier, ML, Outcome models. "
             "Metric = EV (phases zijazo). 'favorable' = vol pchange<0.5 (state stable), proxy ya neutral.*")
    out = REPO_ROOT / c["paths"]["reports"] / "event_diagnostics_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)} ({tot_bars:,} bars, {len(EVENTS_ALL)} events)")
    return 0


def self_test():
    """Integration: df bandia yenye states + prices -> accumulate inajaza
    diagnostics zote bila error; frequency/coverage/dist zina maana."""
    rng = np.random.default_rng(0); n = 5000
    close = np.cumsum(rng.normal(0, 0.6, n)) + 1000.0
    high = close + np.abs(rng.normal(0, 0.5, n)); low = close - np.abs(rng.normal(0, 0.5, n))
    # state series zenye runs (sio random kabisa) ili age/transition ziwe na maana
    vs = []; cur = "NORMAL"
    for _ in range(n):
        if rng.random() < 0.1:
            cur = rng.choice(LEVELS)
        vs.append(cur)
    acts = list(rng.choice(LEVELS, n))
    df = pl.DataFrame(dict(c=close, h=high, l=low,
                           volatility_state=vs, activity_state=acts))
    acc = {name: _new_acc() for name in EVENTS_ALL}; total = [0]
    accumulate(df, acc, total)
    # checks
    fired = {k: acc[k]["n"] for k in EVENTS_ALL}
    all_fired = all(v > 0 for v in fired.values())
    cov_ok = all(acc[k]["ctx"] <= acc[k]["n"] for k in EVENTS_ALL)
    trans_ok = all(sum(acc[k]["trans"].values()) <= acc[k]["n"] for k in EVENTS_ALL)
    age_ok = all(sum(acc[k]["age"]) <= acc[k]["n"] for k in EVENTS_ALL)
    nt = next_transition(["LOW", "LOW", "HIGH"], 0)        # escalate
    nt2 = next_transition(["HIGH", "HIGH", "LOW"], 0)       # revert
    nt3 = next_transition(["NORMAL"] * 20, 0)              # stay
    tn_ok = (nt == "escalate" and nt2 == "revert" and nt3 == "stay")
    print(f"events fired (all>0)={all_fired} | total_bars={total[0]}")
    print(f"coverage<=n={cov_ok} trans<=n={trans_ok} age<=n={age_ok} | next_transition ok={tn_ok}")
    print(f"sample (pullback): n={fired['pullback']} vol={acc['pullback']['vol']}")
    ok = all_fired and cov_ok and trans_ok and age_ok and tn_ok
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
