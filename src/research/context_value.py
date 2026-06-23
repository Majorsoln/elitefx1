"""
context_value.py — PHASE 1.9 (Chief Quant gate). CONTEXT ECONOMIC VALUE TEST.

Phase 1.6–1.8 zilithibitisha kuwa State / Age / Transition zina STRUCTURE
(zinaelezeka) na kuwa age inaboresha CALIBRATION ya P(change). Lakini Chief
Quant amesisitiza (doctrine V5.2, Principle 03):

    Prediction ≠ Economic Value.

LogLoss nzuri SI edge. Calibration nzuri SI edge. Accuracy nzuri SI edge.
Edge ni DECISION-QUALITY IMPROVEMENT tu. Swali pekee:

    Je Context inaboresha trading DECISIONS kwenye events halisi?

Mtihani (bila strategy, ML, optimization, fitting, triple barrier — Chief):
  • Event MOJA kutoka KJ Library: TREND PULLBACK (Event #1).
        long  : close > close[short] AND close < close[long]
        short : close < close[short] AND close > close[long]
  • OUTCOME = forward HORIZON bars (no triple barrier):
        fwd_pips = (close[i+H] − close[i]) / pip
        net      = direction × fwd_pips − spread_pips[i]      (baada ya gharama)
  • Linganisha sera mbili (ONLINE PREQUENTIAL, no-lookahead):
        Case A  Event ALONE     : chukua KILA event.
        Case B  Event + CONTEXT : chukua TU kama context (state, age-bucket)
                                   ilikuwa na EV>0 kwenye historia ya NYUMA.

  • Metrics za DECISION QUALITY (Chief): Win Rate · EV · R-Multiple · Hit Rate
        Win Rate  = % net > 0          (faida baada ya gharama)
        EV        = wastani net pips/trade           (metric rasmi)
        R-Mult    = wastani net / ATR_pips(entry)     (faida kwa kipimo cha risk)
        Hit Rate  = % gross direction sahihi (kabla ya gharama)

Verdict ya doctrine (V5.2):
    Event + Context  outperforms  Event Alone   →  STATE→AGE→TRANSITION→EVENT
    imehalalishwa KIUCHUMI → Phase 2 inafunguliwa.
    Vinginevyo: State Engine ina manufaa lakini HAITOSHI kwa alpha.

Statistical (LogLoss base-rate vs context) inaonyeshwa kama SUPPORTING tu —
SIO edge (Chief).

Chanzo: raw ticks -> bars (reuse market_state_engine) -> states + age (reuse
state_context_engine) -> events + outcomes. Self-contained, no-lookahead.

Output: reports/context_value_report.md
Endesha: python src/research/context_value.py
         python src/research/context_value.py --symbol EURGBP --tf H1
Self-test: python src/research/context_value.py --self-test
"""
from __future__ import annotations

import argparse, sys
from datetime import datetime
from pathlib import Path

import numpy as np
import duckdb

# reuse (sibling modules; dir iko kwenye sys.path tunapoendesha script moja kwa moja)
from market_state_engine import (cfg, pip, time_col, h1_from_ticks, rollup, state_df)
from state_context_engine import context_for_dim, _bidx

REPO_ROOT = Path(__file__).resolve().parents[2]
TFS = ["H1", "H2", "H4", "D1"]
DIMS = [("volatility", "volatility_state"),
        ("activity",   "activity_state"),
        ("spread",     "spread_state")]

# --- Events (KJ Event Library) ---
SHORT_LEN   = 5     # Trend Pullback (KJ #1)
LONG_LEN    = 20
BREAKOUT_LEN = 10   # Super Simple Breakout (KJ #4)
MEANREV_LEN  = 10   # Mean Reversion (KJ #8-style: N-bar extreme)
# --- Outcome (no triple barrier — forward horizon, net ya spread) ---
HORIZON   = 6        # bars mbele kwa outcome (Japhet anaweza kurekebisha)
# --- Tathmini ya prequential ---
MIN_OBS   = 30       # samples za chini kwa (state,bucket) kabla ya kutumia context
ALPHA     = 0.5      # Laplace smoothing kwa P(win)
_posix = lambda p: str(p).replace("\\", "/")


def pullback_signals(close, high=None, low=None) -> np.ndarray:
    """+1 = long, -1 = short, 0 = hakuna. Trend Pullback (KJ #1), no-lookahead.
    Long: close > close[short] AND close < close[long]; short = mirror."""
    n = len(close); sig = np.zeros(n, dtype=int)
    for i in range(LONG_LEN, n):
        cs, cl = close[i - SHORT_LEN], close[i - LONG_LEN]
        if close[i] > cs and close[i] < cl:
            sig[i] = 1
        elif close[i] < cs and close[i] > cl:
            sig[i] = -1
    return sig


def breakout_signals(close, high, low) -> np.ndarray:
    """Super Simple Breakout (KJ #4), no-lookahead. Long: close inavunja juu ya
    highest(high, x) ya bars ZILIZOPITA; short: chini ya lowest(low, x)."""
    n = len(close); sig = np.zeros(n, dtype=int); x = BREAKOUT_LEN
    for i in range(x, n):
        hh = np.max(high[i - x:i]); ll = np.min(low[i - x:i])      # past x bars (excl. i)
        if close[i] > hh:
            sig[i] = 1
        elif close[i] < ll:
            sig[i] = -1
    return sig


def meanrev_signals(close, high=None, low=None) -> np.ndarray:
    """Mean Reversion (KJ #8-style), no-lookahead. Long pale close = lowest(close, N)
    (N-bar low -> tegemea bounce); short pale close = highest(close, N)."""
    n = len(close); sig = np.zeros(n, dtype=int); N = MEANREV_LEN
    for i in range(N - 1, n):
        w = close[i - N + 1:i + 1]                                  # window inajumuisha i
        if close[i] <= w.min():
            sig[i] = 1
        elif close[i] >= w.max():
            sig[i] = -1
    return sig


# Event registry (jina -> signal fn). KJ Event Library.
EVENTS = {
    "pullback":      pullback_signals,
    "breakout":      breakout_signals,
    "mean_reversion": meanrev_signals,
}


def event_records(close, spr_pips, atr_pips, sig, age):
    """Rudisha (idx, nets, wins, rmults, hits, age_buckets) kwa kila event yenye
    outcome kamili. close tayari pips-scaled. net/hit/rmult kama doctrine. age
    inatoka context_for_dim (online); outcome = LABEL ya baadaye (sio decision input)."""
    idx = []; nets = []; wins = []; rmults = []; hits = []; abk = []
    n = len(close)
    for i in range(n):
        if sig[i] == 0 or i + HORIZON >= n:
            continue
        fwd = close[i + HORIZON] - close[i]          # pips (close ime-scale)
        gross = sig[i] * fwd                          # gross directional pips
        net = gross - spr_pips[i]                      # baada ya gharama (round-trip proxy)
        ap = atr_pips[i]
        idx.append(i)
        nets.append(float(net)); wins.append(1 if net > 0 else 0)
        hits.append(1 if gross > 0 else 0)
        rmults.append(float(net / ap) if (np.isfinite(ap) and ap > 0) else np.nan)
        abk.append(_bidx(int(age[i])) if age[i] > 0 else None)
    return idx, np.array(nets), np.array(wins), np.array(rmults), np.array(hits), abk


def _agg(win, net, rmult, hit):
    """Wastani wa metrics nne kutoka lists (nan-safe kwa rmult)."""
    n = len(net)
    return dict(
        n=n,
        win=float(np.mean(win)) if n else float("nan"),
        ev=float(np.mean(net)) if n else float("nan"),
        r=float(np.nanmean(rmult)) if (n and np.isfinite(rmult).any()) else float("nan"),
        hit=float(np.mean(hit)) if n else float("nan"))


def prequential_value(state_keys, age_bkts, nets, wins, rmults, hits):
    """ONLINE prequential (no-lookahead): Case A (Event alone) vs Case B
    (Event + Context). Gate ya B = (state, age-bucket) ilikuwa na EV>0 nyuma.
    Rudisha aggregates za decision-quality + statistical (supporting)."""
    ev_hist = {}                 # key -> [sum_net, count]   (EV gate)
    win_hist = {}                # key -> [wins, count]       (P(win|key))
    g_win = [0, 0]               # global [wins, count]       (P(win) base-rate)
    A = dict(win=[], net=[], r=[], hit=[])
    B = dict(win=[], net=[], r=[], hit=[])
    llA = llB = brA = brB = 0.0; n_scored = 0

    for i in range(len(nets)):
        net = nets[i]; win = int(wins[i]); rm = rmults[i]; hit = int(hits[i])
        key = None if age_bkts[i] is None else (state_keys[i], age_bkts[i])

        # --- Case A: chukua zote ---
        A["win"].append(win); A["net"].append(net); A["r"].append(rm); A["hit"].append(hit)

        # --- Case B: gate EV>0 (past tu) ---
        eh = ev_hist.get(key)
        if key is not None and eh and eh[1] >= MIN_OBS and (eh[0] / eh[1]) > 0:
            B["win"].append(win); B["net"].append(net); B["r"].append(rm); B["hit"].append(hit)

        # --- statistical (supporting): P(win) A base-rate vs B per-key, past tu ---
        wh = win_hist.get(key)
        if g_win[1] >= MIN_OBS and key is not None and wh and wh[1] >= MIN_OBS:
            pA = (g_win[0] + ALPHA) / (g_win[1] + 2 * ALPHA)
            pB = (wh[0] + ALPHA) / (wh[1] + 2 * ALPHA)
            for p, isA in ((pA, True), (pB, False)):
                p = min(max(p, 1e-12), 1 - 1e-12)
                ll = -(win * np.log(p) + (1 - win) * np.log(1 - p)); br = (p - win) ** 2
                if isA: llA += ll; brA += br
                else:   llB += ll; brB += br
            n_scored += 1

        # --- update BAADA ya decision (no-lookahead) ---
        g_win[0] += win; g_win[1] += 1
        if key is not None:
            ev_hist.setdefault(key, [0.0, 0]); ev_hist[key][0] += net; ev_hist[key][1] += 1
            win_hist.setdefault(key, [0, 0]); win_hist[key][0] += win; win_hist[key][1] += 1

    a = _agg(A["win"], A["net"], A["r"], A["hit"])
    b = _agg(B["win"], B["net"], B["r"], B["hit"])
    return dict(A=a, B=b, cov=(b["n"] / a["n"]) if a["n"] else float("nan"),
                ll_A=(llA / n_scored) if n_scored else float("nan"),
                ll_B=(llB / n_scored) if n_scored else float("nan"),
                br_A=(brA / n_scored) if n_scored else float("nan"),
                br_B=(brB / n_scored) if n_scored else float("nan"), n_scored=n_scored)


def evaluate_pair_tf(df, pp, sigfn=pullback_signals):
    """df ina ts, o,h,l,c, atr, spr (pips), + state cols. sigfn = event signal
    fn (EVENTS). Rudisha {dim: metrics}."""
    close = df["c"].to_numpy() / pp                  # pips-scale
    high = df["h"].to_numpy() / pp
    low = df["l"].to_numpy() / pp
    atr_pips = df["atr"].to_numpy() / pp
    spr = df["spr"].to_numpy()
    spr = np.where(np.isfinite(spr), spr, 0.0)
    sig = sigfn(close, high, low)
    res = {}
    for dim, col in DIMS:
        states = df[col].to_list()
        age, _ = context_for_dim(states)
        idx, nets, wins, rmults, hits, abk = event_records(close, spr, atr_pips, sig, age)
        if len(nets) == 0:
            res[dim] = None; continue
        skeys = [states[i] for i in idx]
        m = prequential_value(skeys, abk, nets, wins, rmults, hits)
        m["n_events"] = len(nets)
        res[dim] = m
    return res


def run(pairs, tfs, event="pullback"):
    c = cfg(); raw = REPO_ROOT / c["paths"]["raw_ticks"]
    sigfn = EVENTS[event]
    if not raw.exists():
        print(f"HITILAFU: '{raw}' haipo. (Phase 1.9 inahitaji raw ticks.)", file=sys.stderr)
        return 1
    con = duckdb.connect(); rows = {d[0]: [] for d in DIMS}; any_data = False
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
            res = evaluate_pair_tf(df, pp, sigfn)
            for dim, _ in DIMS:
                if res[dim]:
                    rows[dim].append((sym, tf, res[dim])); any_data = True
            ev = res["volatility"]
            print(f"    {tf}: events≈{ev['n_events'] if ev else 0}")
    if not any_data:
        print("HITILAFU: hakuna events/data.", file=sys.stderr); return 1

    L = ["# Context Economic Value Test — je Context inaboresha DECISIONS? (Phase 1.9)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | Event: {event} | "
         f"outcome: forward {HORIZON} bars NET ya spread | ONLINE prequential (no-lookahead) | "
         f"context gate: EV>0 past, min={MIN_OBS}*\n",
         "> **Principle 03 (V5.2): Prediction ≠ Economic Value.** LogLoss/calibration SI edge. "
         "Edge ni decision-quality. Case A = Event alone; Case B = Event + (State+Age+Transition). "
         "Verdict: **B outperforms A** kwa EV/R/Win → Context adds economic value → Phase 2 inafunguliwa. "
         "NO strategy / ML / optimization / triple barrier (Chief directive).\n",
         "## DECISION QUALITY — Case A (Event alone) → Case B (Event + Context)\n",
         "| Dim | Pair | TF | events | Win% A→B | EV A→B (pips) | R-mult A→B | cov | value? |",
         "|-----|------|----|--------|----------|---------------|------------|-----|--------|"]
    for dim, _ in DIMS:
        for sym, tf, m in rows[dim]:
            a, b = m["A"], m["B"]
            dev = b["ev"] - a["ev"]; dr = b["r"] - a["r"]
            add = "✅" if (dev == dev and dev > 0 and b["ev"] > 0 and (dr != dr or dr >= 0)) else "—"
            L.append(f"| {dim[:3]} | {sym} | {tf} | {m['n_events']:,} | "
                     f"{a['win']*100:.0f}→{b['win']*100:.0f}% | {a['ev']:+.2f}→{b['ev']:+.2f} | "
                     f"{a['r']:+.2f}→{b['r']:+.2f} | {m['cov']*100:.0f}% | {add} |")

    L.append("\n## Supporting — Hit Rate + statistical P(win) (SIO edge, ni rejea tu)\n")
    L.append("| Dim | Pair | TF | Hit% A→B | LogLoss A→B | ΔLL% |")
    L.append("|-----|------|----|----------|-------------|------|")
    for dim, _ in DIMS:
        for sym, tf, m in rows[dim]:
            a, b = m["A"], m["B"]
            if not (m["ll_A"] == m["ll_A"]):
                ll = "—→—"; dll = float("nan")
            else:
                ll = f"{m['ll_A']:.3f}→{m['ll_B']:.3f}"; dll = (m["ll_A"]-m["ll_B"])/m["ll_A"]*100 if m["ll_A"] else 0
            L.append(f"| {dim[:3]} | {sym} | {tf} | {a['hit']*100:.0f}→{b['hit']*100:.0f}% | {ll} | "
                     f"{dll:+.1f} |" if dll == dll else
                     f"| {dim[:3]} | {sym} | {tf} | {a['hit']*100:.0f}→{b['hit']*100:.0f}% | {ll} | — |")

    # ── VERDICT ya doctrine ──
    L.append("\n## VERDICT — Je Context inaboresha trading decisions? (median kwa dimension)\n")
    for dim, _ in DIMS:
        devs = [m["B"]["ev"] - m["A"]["ev"] for _, _, m in rows[dim]
                if m["B"]["ev"] == m["B"]["ev"] and m["A"]["ev"] == m["A"]["ev"]]
        drs = [m["B"]["r"] - m["A"]["r"] for _, _, m in rows[dim]
               if m["B"]["r"] == m["B"]["r"] and m["A"]["r"] == m["A"]["r"]]
        dws = [m["B"]["win"] - m["A"]["win"] for _, _, m in rows[dim]
               if m["B"]["win"] == m["B"]["win"] and m["A"]["win"] == m["A"]["win"]]
        if devs:
            mdev = float(np.median(devs)); win = sum(1 for d in devs if d > 0)
            mdr = float(np.median(drs)) if drs else float("nan")
            mdw = float(np.median(dws)) if dws else float("nan")
            verd = "✅ Context adds ECONOMIC value" if mdev > 0 else "❌ hakuna faida ya kiuchumi"
            L.append(f"- **{dim}**: ΔEV={mdev:+.2f} pips, ΔR={mdr:+.2f}, ΔWin={mdw*100:+.0f}pp "
                     f"({win}/{len(devs)} pair×TF chanya) → {verd}")
    L.append("\n*Doctrine gate (V5.2, Principle 03): **Prediction ≠ Economic Value.** Kama Event+Context "
             "> Event Alone kwa EV/R/Win, architecture ya V5 imehalalishwa KIUCHUMI → Phase 2 (Adaptive "
             "Volume Bars) inafunguliwa. Kama HAPANA → State Engine ina manufaa lakini HAITOSHI kwa alpha. "
             "Metric rasmi = Expected Value (net pips); LogLoss ni supporting tu. Event/HORIZON ni vigezo; "
             "doctrine inahitaji THUBUTISHO, sio tuning.*")
    out = REPO_ROOT / c["paths"]["reports"] / "context_value_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """(1) Context-INFORMATIVE: outcome inategemea state -> Case B inazidi Case A
       kwa Win/EV/R (na LogLoss B<A).  (2) Context-NULL: outcome random -> hakuna faida."""
    rng = np.random.default_rng(0); N = 40000

    def synth(informative):
        sk = []; nets = []; wins = []; rms = []; hits = []; abk = []
        for _ in range(N):
            st = "G" if rng.random() < 0.5 else "B"
            mu = (+3.0 if st == "G" else -3.0) if informative else 0.0
            net = rng.normal(mu, 5.0)
            sk.append(st); nets.append(net); wins.append(1 if net > 0 else 0)
            hits.append(1 if net + rng.normal(0, 0.5) > 0 else 0)   # gross ≈ direction
            rms.append(net / 5.0); abk.append(0)
        return prequential_value(sk, abk, np.array(nets), np.array(wins),
                                 np.array(rms), np.array(hits))

    m = synth(True)
    a, b = m["A"], m["B"]
    inf_ev  = b["ev"]  > a["ev"]  + 0.5
    inf_win = b["win"] > a["win"] + 0.02
    inf_r   = b["r"]   > a["r"]   + 0.1
    inf_ll  = m["ll_B"] < m["ll_A"]
    print(f"informative: Win {a['win']*100:.0f}→{b['win']*100:.0f}% | EV {a['ev']:+.2f}→{b['ev']:+.2f} | "
          f"R {a['r']:+.2f}→{b['r']:+.2f} | cov={m['cov']*100:.0f}% | LogLoss {m['ll_A']:.3f}→{m['ll_B']:.3f}")

    m2 = synth(False); a2, b2 = m2["A"], m2["B"]
    null_flat = abs(b2["ev"] - a2["ev"]) < 0.5
    print(f"null:        Win {a2['win']*100:.0f}→{b2['win']*100:.0f}% | EV {a2['ev']:+.2f}→{b2['ev']:+.2f} "
          f"(ΔEV={b2['ev']-a2['ev']:+.2f}, tarajio ≈0)")

    # signal + record logic kwenye bei bandia (events zote 3)
    close = np.cumsum(rng.normal(0, 1, 500)) + 1000.0
    high = close + np.abs(rng.normal(0, 0.5, 500)); low = close - np.abs(rng.normal(0, 0.5, 500))
    sigs = {nm: fn(close, high, low) for nm, fn in EVENTS.items()}
    sig_ok = all((s != 0).sum() > 0 and set(np.unique(s)).issubset({-1, 0, 1}) for s in sigs.values())
    sig = sigs["pullback"]
    idx, nn, ww, rr, hh, aa = event_records(close, np.full(len(close), 0.5),
                                            np.full(len(close), 10.0), sig, np.arange(1, len(close)+1))
    rec_ok = len(nn) > 0 and all(i + HORIZON < len(close) for i in idx) and np.isfinite(rr).any()
    print(f"signals/event: " + " ".join(f"{nm}={int((s!=0).sum())}" for nm, s in sigs.items())
          + f" | records(pullback)={len(nn)}")

    ok = inf_ev and inf_win and inf_r and inf_ll and null_flat and rec_ok and sig_ok
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default=None)
    ap.add_argument("--tf", default=None, choices=TFS)
    ap.add_argument("--event", default="pullback", choices=list(EVENTS))
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    c = cfg()
    pairs = [a.symbol] if a.symbol else c["pairs"]
    tfs = [a.tf] if a.tf else TFS
    return run(pairs, tfs, a.event)


if __name__ == "__main__":
    raise SystemExit(main())
