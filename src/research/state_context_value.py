"""
state_context_value.py — PHASE 1.9 (Chief Quant gate). Context Value Test.

Phase 1.6–1.8 zilithibitisha kuwa State / Age / Transition ni DESCRIBABLE
(zinaelezeka) na kuwa age inaboresha CALIBRATION ya P(change). Lakini bado
hatujajibu swali kubwa la Chief Quant (doctrine V5.2, Principle 03):

    Je Context ina MATTER kwenye trading?  (trading relevance, sio statistical tu)

Mtihani (bila strategy, bila ML, bila triple barrier — Chief directive):
  • Chukua EVENT MOJA kutoka KJ Event Library: TREND PULLBACK (Event #1).
        long  : close > close[short] AND close < close[long]
        short : close < close[short] AND close > close[long]
  • OUTCOME = forward return baada ya HORIZON bars, NET ya spread (pips):
        net = direction × (close[i+H] − close[i])/pip − spread_pips[i]
  • Linganisha sera mbili (ONLINE PREQUENTIAL, no-lookahead):
        Event ALONE     : chukua KILA event signal.
        Event + CONTEXT : chukua event TU kama context yake (state, age-bucket)
                          ilikuwa na EV>0 kwenye historia ya NYUMA tu.

Verdict ya doctrine:
    Event + Context  >  Event Alone   →  "Context adds value to events."
    (EV = wastani wa net pips kwa trade; ndio metric rasmi, sio win rate.)

Pia tunaonyesha uthibitisho wa STATISTICAL (kwa kila context dimension):
    LogLoss A: P(win) base-rate  vs  B: P(win | state, age-bucket).
    Δ>0 = context ina taarifa kuhusu outcome ya event (sio EV tu).

Chanzo: raw ticks -> bars (reuse market_state_engine) -> states + age
(reuse state_context_engine) -> events + outcomes. Self-contained (recompute),
hairuhusu lookahead.

Output: reports/state_context_value_report.md
Endesha: python src/research/state_context_value.py
         python src/research/state_context_value.py --symbol EURGBP --tf H1
Self-test: python src/research/state_context_value.py --self-test
"""
from __future__ import annotations

import argparse, sys
from datetime import datetime
from pathlib import Path

import numpy as np
import duckdb, yaml

# reuse (sibling modules; dir iko kwenye sys.path tunapoendesha script moja kwa moja)
from market_state_engine import (cfg, pip, time_col, h1_from_ticks, rollup, state_df)
from state_context_engine import context_for_dim, _bidx, BUCKETS

REPO_ROOT = Path(__file__).resolve().parents[2]
TFS = ["H1", "H2", "H4", "D1"]
DIMS = [("volatility", "volatility_state"),
        ("activity",   "activity_state"),
        ("spread",     "spread_state")]

# --- Event: Trend Pullback (KJ Event #1) ---
SHORT_LEN = 5
LONG_LEN  = 20
# --- Outcome (no triple barrier — forward horizon, net ya spread) ---
HORIZON   = 6        # bars mbele kwa outcome (Japhet anaweza kurekebisha)
# --- Tathmini ya prequential ---
MIN_OBS   = 30       # samples za chini kwa (state,bucket) kabla ya kutumia context
ALPHA     = 0.5      # Laplace smoothing kwa P(win)
_posix = lambda p: str(p).replace("\\", "/")


def pullback_signals(close: np.ndarray) -> np.ndarray:
    """+1 = long, -1 = short, 0 = hakuna. Trend Pullback (KJ #1), no-lookahead
    (inatumia close za sasa/nyuma tu)."""
    n = len(close); sig = np.zeros(n, dtype=int)
    for i in range(LONG_LEN, n):
        cs, cl = close[i - SHORT_LEN], close[i - LONG_LEN]
        if close[i] > cs and close[i] < cl:
            sig[i] = 1
        elif close[i] < cs and close[i] > cl:
            sig[i] = -1
    return sig


def event_records(close, spr_pips, sig, age):
    """Rudisha (keys_bucket[], nets[], wins[]) kwa kila event yenye outcome kamili.
    key_bucket = age-bucket index (context key inaongezwa na caller per dim).
    net = direction×fwd_pips − spread (round-trip cost proxy). no-lookahead:
    outcome inatumia close[i+H] (bei ya BAADAYE) — ni LABEL, sio decision input."""
    nets = []; wins = []; idx = []; abk = []
    n = len(close)
    for i in range(n):
        if sig[i] == 0 or i + HORIZON >= n:
            continue
        fwd = (close[i + HORIZON] - close[i]) / 1.0     # tayari pips (close ime-scale nje)
        net = sig[i] * fwd - spr_pips[i]
        nets.append(float(net)); wins.append(1 if net > 0 else 0)
        idx.append(i); abk.append(_bidx(int(age[i])) if age[i] > 0 else None)
    return idx, np.array(nets), np.array(wins), abk


def prequential_value(state_keys, age_bkts, nets, wins):
    """ONLINE prequential (no-lookahead): linganisha Event-alone vs Event+Context.

    state_keys[i] = state ya bar ya event (string)  | age_bkts[i] = bucket idx au None
    Context key = (state, age-bucket). Maamuzi yote yanatumia historia ya NYUMA tu.

    Rudisha: ev_all, ev_ctx, cov, n_all, n_ctx, ll_A, ll_B, br_A, br_B, n_scored
    """
    ev_hist = {}                 # key -> [sum_net, count]   (EV gate)
    win_hist = {}                # key -> [wins, count]       (P(win|key))
    g_win = [0, 0]               # global [wins, count]       (P(win) base-rate)
    net_all = []; net_ctx = []
    llA = llB = brA = brB = 0.0; n_scored = 0
    for i in range(len(nets)):
        net = nets[i]; win = int(wins[i])
        key = None if age_bkts[i] is None else (state_keys[i], age_bkts[i])

        # --- decision (past tu) ---
        net_all.append(net)                                  # Event alone: chukua zote
        eh = ev_hist.get(key)
        if key is not None and eh and eh[1] >= MIN_OBS and (eh[0] / eh[1]) > 0:
            net_ctx.append(net)                              # Event+Context: gate EV>0

        # --- statistical scoring (P(win): A base-rate vs B per-key), past tu ---
        wh = win_hist.get(key)
        if g_win[1] >= MIN_OBS and key is not None and wh and wh[1] >= MIN_OBS:
            pA = (g_win[0] + ALPHA) / (g_win[1] + 2 * ALPHA)
            pB = (wh[0] + ALPHA) / (wh[1] + 2 * ALPHA)
            for p, acc in ((pA, "A"), (pB, "B")):
                p = min(max(p, 1e-12), 1 - 1e-12)
                ll = -(win * np.log(p) + (1 - win) * np.log(1 - p))
                br = (p - win) ** 2
                if acc == "A":
                    llA += ll; brA += br
                else:
                    llB += ll; brB += br
            n_scored += 1

        # --- update BAADA ya decision (no-lookahead) ---
        g_win[0] += win; g_win[1] += 1
        if key is not None:
            ev_hist.setdefault(key, [0.0, 0]); ev_hist[key][0] += net; ev_hist[key][1] += 1
            win_hist.setdefault(key, [0, 0]); win_hist[key][0] += win; win_hist[key][1] += 1

    na = len(net_all); nc = len(net_ctx)
    out = dict(
        ev_all=float(np.mean(net_all)) if na else float("nan"),
        ev_ctx=float(np.mean(net_ctx)) if nc else float("nan"),
        cov=(nc / na) if na else float("nan"), n_all=na, n_ctx=nc,
        ll_A=(llA / n_scored) if n_scored else float("nan"),
        ll_B=(llB / n_scored) if n_scored else float("nan"),
        br_A=(brA / n_scored) if n_scored else float("nan"),
        br_B=(brB / n_scored) if n_scored else float("nan"), n_scored=n_scored)
    return out


def evaluate_pair_tf(df, pp):
    """df ina ts, o,h,l,c, spr (pips), + state columns. Rudisha {dim: metrics}."""
    close = df["c"].to_numpy() / pp                  # pips-scale (tofauti thabiti)
    spr = df["spr"].to_numpy()                       # tayari pips (median spread/bar)
    spr = np.where(np.isfinite(spr), spr, 0.0)
    sig = pullback_signals(close)
    res = {}
    for dim, col in DIMS:
        states = df[col].to_list()
        age, _ = context_for_dim(states)
        idx, nets, wins, abk = event_records(close, spr, sig, age)
        if len(nets) == 0:
            res[dim] = None; continue
        skeys = [states[i] for i in idx]
        res[dim] = prequential_value(skeys, abk, nets, wins)
        res[dim]["n_events"] = len(nets)
    return res


def run(pairs, tfs):
    c = cfg(); raw = REPO_ROOT / c["paths"]["raw_ticks"]
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
            res = evaluate_pair_tf(df, pp)
            for dim, _ in DIMS:
                if res[dim]:
                    rows[dim].append((sym, tf, res[dim])); any_data = True
            ev = res["volatility"]
            print(f"    {tf}: events≈{ev['n_events'] if ev else 0}")
    if not any_data:
        print("HITILAFU: hakuna events/data.", file=sys.stderr); return 1

    L = ["# State Context Value Test — je Context ina faida kwenye Events? (Phase 1.9)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | Event: Trend Pullback (KJ #1, short={SHORT_LEN}/long={LONG_LEN}) | "
         f"outcome: forward {HORIZON} bars NET ya spread (pips) | ONLINE prequential (no-lookahead) | "
         f"context gate: EV>0 past, min={MIN_OBS}*\n",
         "> **Principle 03 (V5.2):** Context lazima ithibitishe TRADING relevance, sio statistical tu. "
         "EV = wastani net pips/trade (metric rasmi). Verdict: **Event+Context > Event Alone** = "
         "Context adds value. NO strategy / NO ML / NO triple barrier (Chief directive).\n",
         "## Trading relevance — EV (net pips/trade): Event ALONE vs Event + CONTEXT\n",
         "| Dim | Pair | TF | events | EV alone | EV +ctx | ΔEV | cov | ctx adds value? |",
         "|-----|------|----|--------|----------|---------|-----|-----|-----------------|"]
    for dim, _ in DIMS:
        for sym, tf, m in rows[dim]:
            dev = m["ev_ctx"] - m["ev_all"] if (m["ev_ctx"] == m["ev_ctx"]) else float("nan")
            add = "✅" if (dev == dev and dev > 0 and m["ev_ctx"] > 0) else "—"
            L.append(f"| {dim[:3]} | {sym} | {tf} | {m['n_events']:,} | "
                     f"{m['ev_all']:+.2f} | {m['ev_ctx']:+.2f} | {dev:+.2f} | "
                     f"{m['cov']*100:.0f}% | {add} |")

    L.append("\n## Statistical relevance — P(win): base-rate (A) vs context (B)\n")
    L.append("| Dim | Pair | TF | n | LogLoss A→B | ΔLL% | Brier A→B |")
    L.append("|-----|------|----|---|-------------|------|-----------|")
    for dim, _ in DIMS:
        for sym, tf, m in rows[dim]:
            if not (m["ll_A"] == m["ll_A"]):
                continue
            dll = (m["ll_A"] - m["ll_B"]) / m["ll_A"] * 100 if m["ll_A"] else 0
            L.append(f"| {dim[:3]} | {sym} | {tf} | {m['n_scored']:,} | "
                     f"{m['ll_A']:.3f}→{m['ll_B']:.3f} | {dll:+.1f} | "
                     f"{m['br_A']:.3f}→{m['br_B']:.3f} |")

    # ── Verdict ya doctrine ──
    L.append("\n## VERDICT — Context adds value to events? (median kwa dimension)\n")
    for dim, _ in DIMS:
        devs = [m["ev_ctx"] - m["ev_all"] for _, _, m in rows[dim]
                if m["ev_ctx"] == m["ev_ctx"] and m["ev_all"] == m["ev_all"]]
        dlls = [(m["ll_A"] - m["ll_B"]) / m["ll_A"] * 100 for _, _, m in rows[dim]
                if m["ll_A"] == m["ll_A"] and m["ll_A"]]
        if devs:
            mdev = float(np.median(devs)); win = sum(1 for d in devs if d > 0)
            mll = float(np.median(dlls)) if dlls else float("nan")
            verd = "✅ Context adds trading value" if mdev > 0 else "❌ hakuna faida ya EV"
            L.append(f"- **{dim}**: median ΔEV = {mdev:+.2f} pips/trade "
                     f"({win}/{len(devs)} pair×TF chanya), median ΔLogLoss = {mll:+.1f}% → {verd}")
    L.append("\n*Doctrine gate (V5.2): kama Event+Context > Event Alone kwa EV, architecture ya V5 "
             "imehalalishwa kwa TRADING (sio statistical tu) -> Phase 2 (Adaptive Volume Bars) "
             "inafunguliwa. Metric rasmi = Expected Value (net pips), sio win rate. Event/HORIZON ni "
             "vigezo (Japhet anaweza kurekebisha); doctrine inahitaji THUBUTISHO, sio tuning.*")
    out = REPO_ROOT / c["paths"]["reports"] / "state_context_value_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """(1) Context-INFORMATIVE: outcome ya event inategemea state -> Event+Context EV
       inazidi Event-alone, na LogLoss B < A.
       (2) Context-NULL: outcome random kwa state -> hakuna faida (ΔEV ≈ 0)."""
    rng = np.random.default_rng(0)
    N = 40000
    # --- (1) informative: state "G" -> events shinda; state "B" -> events poteza ---
    states = []; nets = []; wins = []; abk = []
    skeys = []
    for _ in range(N):
        st = "G" if rng.random() < 0.5 else "B"
        # net: G -> mean +3 pips, B -> mean -3 pips (spread tayari imejumuishwa)
        net = rng.normal(+3.0 if st == "G" else -3.0, 5.0)
        states.append(st); skeys.append(st)
        nets.append(net); wins.append(1 if net > 0 else 0)
        abk.append(0)                                   # bucket moja (umri haijaribiwi hapa)
    m = prequential_value(skeys, abk, np.array(nets), np.array(wins))
    inf_ev = m["ev_ctx"] > m["ev_all"] + 0.5            # context gate inaboresha EV wazi
    inf_ll = m["ll_B"] < m["ll_A"]                       # context inatabiri win vyema
    print(f"informative: EV alone={m['ev_all']:+.2f} +ctx={m['ev_ctx']:+.2f} "
          f"(cov={m['cov']*100:.0f}%) | LogLoss A={m['ll_A']:.3f} B={m['ll_B']:.3f}")

    # --- (2) null: net haategemei state ---
    skeys2 = []; nets2 = []; wins2 = []; abk2 = []
    for _ in range(N):
        st = "G" if rng.random() < 0.5 else "B"
        net = rng.normal(0.0, 5.0)                       # hakuna edge, hakuna tofauti ya state
        skeys2.append(st); nets2.append(net); wins2.append(1 if net > 0 else 0); abk2.append(0)
    m2 = prequential_value(skeys2, abk2, np.array(nets2), np.array(wins2))
    null_flat = abs(m2["ev_ctx"] - m2["ev_all"]) < 0.5  # hakuna faida ya maana
    print(f"null:        EV alone={m2['ev_all']:+.2f} +ctx={m2['ev_ctx']:+.2f} "
          f"(ΔEV={m2['ev_ctx']-m2['ev_all']:+.2f}, tarajio ≈0)")

    # --- (3) signal + outcome logic kwenye bei bandia ---
    close = np.cumsum(rng.normal(0, 1, 500)) + 1000.0
    sig = pullback_signals(close)
    sig_ok = (sig != 0).sum() > 0 and set(np.unique(sig)).issubset({-1, 0, 1})
    idx, nn, ww, aa = event_records(close, np.full(len(close), 0.5), sig, np.arange(1, len(close)+1))
    rec_ok = len(nn) > 0 and all(i + HORIZON < len(close) for i in idx)
    print(f"signals: n={int((sig!=0).sum())} records={len(nn)} (ok={sig_ok and rec_ok})")

    ok = inf_ev and inf_ll and null_flat and sig_ok and rec_ok
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
