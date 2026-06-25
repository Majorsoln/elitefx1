"""
payoff_attribution.py — PHASE 5.6 (Chief Quant). Payoff Attribution.

Phase 5.5 (F-010/F-011) ilithibitisha MECHANISM: context inaboresha PAYOFF
DISTRIBUTION (sio win probability). Tier-1 ina mechanism mbili:
  Group A (Reward Expansion): mean_reversion, deep_pullback   -> AvgWin inakua
  Group B (Loss Compression): pullback, trend_continuation    -> AvgLoss inashuka

Lakini bado hatujajua CAUSALITY: ni SEHEMU GANI za context zinazosababisha
reward expansion au loss compression? Phase 5.6 inaganua context score kuwa
COMPONENTS na kupima mchango wa kila moja:

  volatility_state · activity_state · spread_state · state_age (vol) ·
  transition_probability (vol pchange)

Kwa kila Tier-1 event, kwa kila component, tunapima jinsi AvgWin / AvgLoss /
P(win) zinavyotofautiana KATI YA states za component hiyo (spread = max−min).
Component yenye AvgWin-spread kubwa = REWARD driver; AvgLoss-spread kubwa =
LOSS driver. Hii inaonyesha context inafanya kazi kupitia SABABU gani.

Outcome = forward HORIZON net ya spread (ileile ya F-009/F-010). NO ML, NO
prediction — attribution/diagnostics tu (sababu, sio EV upya).

> Hii ndiyo daraja kati ya DESCRIPTIVE na PREDICTIVE: Payoff Engine (Phase 6)
> itajengwa juu ya sababu HALISI, sio score ya jumla.

Reuse: market_state_engine (bars/states), state_context_engine (age/pchange),
event_library (Tier-1), context_value (HORIZON).

Output: reports/payoff_attribution_report.md
Endesha: python src/research/payoff_attribution.py
         python src/research/payoff_attribution.py --symbol EURGBP --tf H1
Self-test: python src/research/payoff_attribution.py --self-test
"""
from __future__ import annotations

import argparse, sys
from datetime import datetime
from pathlib import Path

import numpy as np
import duckdb

from market_state_engine import (cfg, pip, time_col, h1_from_ticks, rollup, state_df)
from state_context_engine import context_for_dim, _bidx, BUCKETS
from event_library import EVENTS_ALL
from context_value import HORIZON

REPO_ROOT = Path(__file__).resolve().parents[2]
TFS = ["H1", "H2", "H4", "D1"]
TIER1 = ["mean_reversion", "pullback", "deep_pullback", "trend_continuation"]
GROUP_A = {"mean_reversion", "deep_pullback"}        # Reward Expansion (F-011)
GROUP_B = {"pullback", "trend_continuation"}         # Loss Compression (F-011)
BLABEL = ["1-3", "4-8", "9-15", "16+"]
COMPONENTS = ["volatility", "activity", "spread", "state_age", "transition"]
MIN_G = 100          # instances za chini kwa group (state) ili kuhesabu kwenye spread
_posix = lambda p: str(p).replace("\\", "/")


def _pchg_bucket(p):
    if not np.isfinite(p):
        return None
    return "Tlo" if p < 0.08 else ("Tmid" if p < 0.15 else "Thi")   # transition prob low/mid/high


def _new_acc():
    # component -> group -> [sum_win, n_win, sum_loss, n_loss, n_tot]
    return {c: {} for c in COMPONENTS}


def process_df(df, pp, acc):
    close = df["c"].to_numpy() / pp; high = df["h"].to_numpy() / pp; low = df["l"].to_numpy() / pp
    spr = df["spr"].to_numpy(); spr = np.where(np.isfinite(spr), spr, 0.0)
    vs = df["volatility_state"].to_list(); acts = df["activity_state"].to_list()
    sprs = df["spread_state"].to_list()
    vage, vpchg = context_for_dim(vs)
    n = len(close)
    for ev in TIER1:
        sig = EVENTS_ALL[ev](close, high, low)
        A = acc[ev]
        for i in range(n):
            if sig[i] == 0 or i + HORIZON >= n:
                continue
            if vs[i] == "UNKNOWN":
                continue
            net = sig[i] * (close[i + HORIZON] - close[i]) - spr[i]
            comps = {
                "volatility": vs[i],
                "activity": acts[i] if acts[i] != "UNKNOWN" else None,
                "spread": sprs[i] if sprs[i] != "UNKNOWN" else None,
                "state_age": BLABEL[_bidx(int(vage[i]))] if vage[i] > 0 else None,
                "transition": _pchg_bucket(vpchg[i]),
            }
            for cname, g in comps.items():
                if g is None:
                    continue
                d = A[cname].setdefault(g, [0.0, 0, 0.0, 0, 0])
                d[4] += 1
                if net > 0:
                    d[0] += net; d[1] += 1
                else:
                    d[2] += -net; d[3] += 1


def _group_stats(d):
    sw, nw, sl, nl, nt = d
    return dict(pw=nw / nt if nt else 0.0,
                avgwin=sw / nw if nw else 0.0, avgloss=sl / nl if nl else 0.0, n=nt)


def _spread(comp):
    """max-min ya avgwin/avgloss/pw kuvuka groups (zenye n>=MIN_G)."""
    gs = [(_group_stats(d)) for g, d in comp.items() if d[4] >= MIN_G]
    if len(gs) < 2:
        return None
    aw = [s["avgwin"] for s in gs]; al = [s["avgloss"] for s in gs]; pw = [s["pw"] for s in gs]
    return dict(daw=max(aw) - min(aw), dal=max(al) - min(al), dpw=(max(pw) - min(pw)) * 100, k=len(gs))


def run(pairs, tfs):
    c = cfg(); raw = REPO_ROOT / c["paths"]["raw_ticks"]
    if not raw.exists():
        print(f"HITILAFU: '{raw}' haipo.", file=sys.stderr); return 1
    con = duckdb.connect()
    acc = {ev: _new_acc() for ev in TIER1}
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
            process_df(df, pp, acc)
            print(f"    {tf}: done", flush=True)

    L = ["# Payoff Attribution — context inafanya kazi kupitia SABABU gani? (Phase 5.6, Tier 1)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | components: {', '.join(COMPONENTS)} | spread = max−min ya "
         "AvgWin/AvgLoss/P(win) kuvuka states za component | outcome = forward net | Group A=reward, B=loss*\n",
         "> **Q-009 (Chief):** Kwa NINI context inasababisha reward expansion (Group A: MR, Deep PB) au "
         "loss compression (Group B: PB, TC)? Tunaganua context kuwa components na kupima nani anabeba "
         "AvgWin (reward) au AvgLoss (loss) separation. Causality, sio EV. NO ML.\n"]
    agg_reward = {c: 0.0 for c in COMPONENTS}; agg_loss = {c: 0.0 for c in COMPONENTS}
    for ev in TIER1:
        grp = "A (Reward Expansion)" if ev in GROUP_A else "B (Loss Compression)"
        L.append(f"\n## {ev} — Group {grp}\n")
        L.append("| component | ΔAvgWin | ΔAvgLoss | ΔP(win) | groups |")
        L.append("|-----------|---------|----------|---------|--------|")
        sp = {}
        for cname in COMPONENTS:
            s = _spread(acc[ev][cname])
            sp[cname] = s
            if s is None:
                L.append(f"| {cname} | — | — | — | <2 |"); continue
            L.append(f"| {cname} | {s['daw']:.1f} | {s['dal']:.1f} | {s['dpw']:+.0f}pp | {s['k']} |")
            agg_reward[cname] += s["daw"]; agg_loss[cname] += s["dal"]
        valid = {k: v for k, v in sp.items() if v}
        if valid:
            rdrv = max(valid, key=lambda k: valid[k]["daw"])
            ldrv = max(valid, key=lambda k: valid[k]["dal"])
            focus = rdrv if ev in GROUP_A else ldrv
            mech = "reward expansion" if ev in GROUP_A else "loss compression"
            L.append(f"\n→ **{ev}**: reward-driver = **{rdrv}** (ΔAvgWin {valid[rdrv]['daw']:.1f}); "
                     f"loss-driver = **{ldrv}** (ΔAvgLoss {valid[ldrv]['dal']:.1f}). "
                     f"Mechanism ya event hii ({mech}) inahusishwa zaidi na **{focus}**.")

    L.append("\n## VERDICT — components zinazobeba payoff mechanism (jumla kuvuka Tier 1)\n")
    rrank = sorted(agg_reward.items(), key=lambda x: x[1], reverse=True)
    lrank = sorted(agg_loss.items(), key=lambda x: x[1], reverse=True)
    L.append(f"- **Reward (AvgWin) drivers**, juu→chini: " +
             ", ".join(f"{k} ({v:.1f})" for k, v in rrank if v > 0))
    L.append(f"- **Loss (AvgLoss) drivers**, juu→chini: " +
             ", ".join(f"{k} ({v:.1f})" for k, v in lrank if v > 0))
    L.append(f"\n→ Payoff Engine (Phase 6) ijengwe juu ya components hizi (sababu halisi), sio context "
             "score ya jumla. Reward-mechanism inaongozwa na **{}**; loss-mechanism na **{}**."
             .format(rrank[0][0] if rrank else "—", lrank[0][0] if lrank else "—"))
    L.append("\n*Attribution = mchango wa component kwa AvgWin/AvgLoss separation (sababu ya payoff "
             "mechanism, F-011). Sio prediction wala EV upya. Hii ndiyo daraja descriptive→predictive: "
             "Payoff Engine (Phase 6) itatabiri DISTRIBUTION juu ya components hizi. NO ML bado (Chief). "
             "Profitable ≠ Tradable Edge.*")
    out = REPO_ROOT / c["paths"]["reports"] / "payoff_attribution_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """Synthetic: component moja (volatility) inadhibiti winner size; nyingine random.
    Attribution lazima itambue volatility kama reward-driver (ΔAvgWin kubwa zaidi)."""
    rng = np.random.default_rng(0); N = 60000
    acc = {"ev": _new_acc()}
    A = acc["ev"]
    for _ in range(N):
        vlevel = rng.choice(["LOW", "NORMAL", "HIGH"])
        # winner size inategemea volatility (HIGH -> winners kubwa); P(win) constant 0.5
        win = rng.random() < 0.5
        base = {"LOW": 4.0, "NORMAL": 8.0, "HIGH": 16.0}[vlevel]
        net = (base + rng.normal(0, 2)) if win else -(6.0 + rng.normal(0, 2))
        comps = {"volatility": vlevel,
                 "activity": rng.choice(["LOW", "NORMAL", "HIGH"]),   # random (no effect)
                 "spread": rng.choice(["NORMAL", "WIDE"]),
                 "state_age": rng.choice(BLABEL),
                 "transition": rng.choice(["Tlo", "Tmid", "Thi"])}
        for cn, g in comps.items():
            d = A[cn].setdefault(g, [0.0, 0, 0.0, 0, 0]); d[4] += 1
            if net > 0: d[0] += net; d[1] += 1
            else: d[2] += -net; d[3] += 1
    sp = {cn: _spread(A[cn]) for cn in COMPONENTS}
    rdrv = max((k for k in sp if sp[k]), key=lambda k: sp[k]["daw"])
    vol_aw = sp["volatility"]["daw"]; act_aw = sp["activity"]["daw"]
    ok = (rdrv == "volatility" and vol_aw > 3 * max(act_aw, 0.1))
    print(f"reward-driver detected = {rdrv} (volatility ΔAvgWin={vol_aw:.1f} vs activity={act_aw:.1f})")
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
