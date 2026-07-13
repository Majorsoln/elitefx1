"""scientist_d_family_pooled_precheck.py — SCIENTIST-D pre-check arithmetic for the
FAMILY-POOLED holdout test design (reports/family_pooled_design.md).

Inputs: ONLY already-open artifacts — the restated S2-C2 H4 validation file (p_boot engine,
commit 0fb20fd, working tree data/strategies/candidates_c2.jsonl) and the ruling constants in
docs/CHIEF_STATUS.md (2026-07-12 S3-C2 RULING: window days=347, shrink=0.35 conservative tip).
No data window is touched. Verifies:
  1. Rep selection is mechanical (best p_boot per group, TRAIN EV>0; tie -> p_z) and matches
     the reps implied by the Chief's per-group MDE numbers (15.2<16.8, 1.8<2.4, 9.6<17.7, 5.0<9.1).
  2. Chief's per-group MDE numbers reproduce exactly from (ev, win, pf, trades/day) via the
     two-point payoff sd (same method as the ruling).
  3. Pooled R-unit arithmetic: EV_R, sd_R per rep (ATR backed out via W+L=(TP+SL)*ATR, exact
     because per-trade cost cancels in W+L), pooled EV/sd/MDE, shrunken-forecast screen at 0.35,
     and power at shrink 0.35 / 0.50.

Usage: python scripts/scientist_d_family_pooled_precheck.py   (repo root; numpy only)
"""
from __future__ import annotations
import json, math
from math import erfc, sqrt

DAYS = 347            # holdout window trading days (ruling 2026-07-12)
SHRINK = (0.35, 0.50) # B-prime shrink range; conservative tip binds
Z05 = 1.6449          # one-sided 5%

GROUPS = [("nr4_inside", "GBPJPY"), ("nr7_break", "EURGBP"),
          ("nr7_break", "EURJPY"), ("nr7_break", "AUDUSD")]
CHIEF_MDE = {"GBPJPY": (15.2, 16.8), "EURGBP": (1.8, 2.4),
             "EURJPY": (9.6, 17.7), "AUDUSD": (5.0, 9.1)}   # (shrunken EV, MDE) pips


def two_point(ev, win, pf):
    """W, L, sd (pips) of the two-point payoff implied by stored (ev, win, pf) — the same
    'sd kutoka payoff structure' method as the S3-C2 ruling."""
    WL = pf * (1 - win) / win
    L = ev / (win * WL - (1 - win))
    W = WL * L
    sd = math.sqrt(win * (1 - win)) * (W + L)
    return W, L, sd


def main():
    rows = [json.loads(l) for l in open("data/strategies/candidates_c2.jsonl", encoding="utf-8")]
    surv = [r for r in rows if r.get("fdr_survivor")]
    assert len(surv) == 12, f"expected 12 p_boot survivors, got {len(surv)}"

    print("== 1) mechanical reps (best p_boot per group; tie -> p_z) ==")
    reps = []
    for ev_, pr in GROUPS:
        g = [r for r in surv if r["event"] == ev_ and r["pair"] == pr]
        g.sort(key=lambda r: (r["p"], r["p_z"]))
        reps.append(g[0])
        tie = sum(1 for r in g if r["p"] == g[0]["p"])
        print(f"  {ev_}x{pr}: {len(g)} cells; rep = SL{g[0]['sl_atr']}/TP{g[0]['tp_atr']} "
              f"{g[0]['session_filter']} (p_boot={g[0]['p']}, p_z={g[0]['p_z']}, tie@floor={tie})")

    print("\n== 2) reproduce Chief per-group MDE (pips) ==")
    pooled = []
    for r in reps:
        W, L, sd = two_point(r["ev"], r["win"], r["pf"])
        n_exp = r["trades_per_day"] * DAYS
        mde = Z05 * sd / math.sqrt(n_exp)
        shr = 0.35 * r["ev"]
        exp_s, exp_m = CHIEF_MDE[r["pair"]]
        ok = abs(shr - exp_s) < 0.15 and abs(mde - exp_m) < 0.15
        atr = (W + L) / (r["sl_atr"] + r["tp_atr"])      # exact: costs cancel in W+L
        R = r["sl_atr"] * atr
        pooled.append(dict(pair=r["pair"], n_exp=n_exp, ev_R=r["ev"] / R, sd_R=sd / R,
                           n_valid=r["n"], win=r["win"], tp_sl=(r["tp_atr"], r["sl_atr"])))
        print(f"  {r['pair']}: sd={sd:.1f} N_exp={n_exp:.1f} -> shrunkenEV={shr:.1f} vs MDE={mde:.1f} "
              f"(Chief: {exp_s}<{exp_m}) reproduce={ok} | ATR~{atr:.1f} pips, R~{R:.1f} pips")

    print("\n== 3) pooled R-unit arithmetic ==")
    Ntot = sum(p["n_exp"] for p in pooled)
    ev_pool = sum(p["n_exp"] * p["ev_R"] for p in pooled) / Ntot
    var_within = sum(p["n_exp"] * p["sd_R"] ** 2 for p in pooled) / Ntot
    var_between = sum(p["n_exp"] * (p["ev_R"] - ev_pool) ** 2 for p in pooled) / Ntot
    sd_pool = math.sqrt(var_within + var_between)
    mde_pool = Z05 * sd_pool / math.sqrt(Ntot)
    for p in pooled:
        print(f"  {p['pair']}: share={p['n_exp']/Ntot*100:.0f}% EV_R={p['ev_R']:+.3f} sd_R={p['sd_R']:.2f}")
    print(f"  pooled: N_exp={Ntot:.0f} EV_R(VALID)={ev_pool:+.3f} sd_R={sd_pool:.2f} MDE_R={mde_pool:.3f}")
    for s in SHRINK:
        fc = s * ev_pool
        z = fc / (sd_pool / math.sqrt(Ntot))
        power = 0.5 * erfc(-(z - Z05) / sqrt(2))
        print(f"  shrink {s}: forecast={fc:.3f} R -> screen {'PASS' if fc >= mde_pool else 'FAIL'} "
              f"(margin x{fc/mde_pool:.2f}); power@a=.05 ~ {power:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
