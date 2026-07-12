"""
cost_stress.py — WAVE-1 R5: cost stress harness (SCIENTIST-D design — verbatim; Chief 2026-07-12).

Edges zetu ni cost-thin (W4: cost model ni optimistic kwenye tail inayoziua). Vipande 3:
  (1) EV(Δspread) ANALYTIC: kila trade inalipa spread mara MOJA (entry) -> EV_new = EV − Δspread.
      `ev_spread_table(cands, deltas)` — pia inaitwa na strategy_lab.write_outputs (kila ripoti).
  (2) `spread_split(trades, spread_state)`: gawa trades za cell (opened windows) kwa spread_state
      ya ENTRY bar (NORMAL vs WIDE). EV_WIDE < 0 -> WIDE-skip filter kwenye DEPLOYMENT policy
      (SIO backtest) + forward-verify. Hakuna mabadiliko ya episodes() (byte-identical inabaki).
  (3) GOLD: `stop_slippage_percentile(spreads, pct)` — empirical spread distribution kutoka ticks
      (spread_quality.py machinery ya Operator) -> percentile-based stop slippage badala ya 0.3-pip
      flat, KABLA ya gold registration yoyote. Deliverable = NAMBA + ripoti; kuiingiza kwenye cost
      model ya harness = uamuzi wa Chief (pre-registered, sio silent change).

Pure functions (numpy pekee) — data runs = Operator. Self-test: python cost_stress.py --self-test
"""
from __future__ import annotations

import argparse
import sys

import numpy as np

SPREAD_DELTAS = (0.2, 0.5, 1.0)     # pips — stress steps za kawaida (kila ripoti)


def ev_spread_table(cands, deltas=SPREAD_DELTAS):
    """R5(1) analytic: EV_new = ev − Δ (spread inalipwa mara moja kwa trade). Rudisha rows za
    (cell-label, ev, {Δ: ev_new}, breakeven_dspread) — breakeven = Δ inayofuta EV (ev yenyewe)."""
    rows = []
    for c in cands:
        ev = float(c["ev"])
        rows.append(dict(label=f"{c['event']}x{c['pair']} SL{c['sl_atr']}/TP{c['tp_atr']} {c.get('session_filter')}",
                         ev=round(ev, 3),
                         ev_dspread={f"+{d}": round(ev - d, 3) for d in deltas},
                         breakeven_dspread=round(max(0.0, ev), 3)))
    return rows


def spread_split(trades, spread_state):
    """R5(2): gawa pnls kwa spread_state ya ENTRY bar. trades = episodes() tuples (entry_bar=t[0]);
    spread_state = array ya state kwa bar (kutoka state parquet ya pair). Rudisha
    {state: {n, ev, win}} + verdict ya WIDE-skip (deployment-policy recommendation, si backtest)."""
    groups = {}
    for t in trades:
        st = str(spread_state[t[0]])
        groups.setdefault(st, []).append(t[3])
    out = {}
    for st, pn in groups.items():
        p = np.asarray(pn, float)
        out[st] = dict(n=len(p), ev=round(float(p.mean()), 4), win=round(float((p > 0).mean()), 4))
    wide = out.get("WIDE")
    out["_verdict"] = ("WIDE-skip filter kwenye DEPLOYMENT policy (EV_WIDE<0) + forward-verify"
                       if wide and wide["ev"] < 0 else "hakuna WIDE-skip (EV_WIDE>=0 au hakuna WIDE trades)")
    return out


def stop_slippage_percentile(spreads, pct=95):
    """R5(3) GOLD: percentile-based stop slippage kutoka empirical spread samples (ticks).
    Replacement ya 0.3-pip flat KWA GOLD — worst-case fill ya stop hutokea spread ikiwa pana.
    Rudisha dict ya percentiles muhimu + figure iliyopendekezwa (pct-th percentile / 2 = half-spread
    ya upande mmoja wa stop fill; assumption imeandikwa wazi — Chief ata-approve kabla ya matumizi)."""
    s = np.asarray(spreads, float)
    s = s[np.isfinite(s) & (s >= 0)]
    if len(s) < 100:
        raise ValueError(f"spread samples chache mno ({len(s)}); percentile isingekuwa ya kuaminika")
    pcts = {p: round(float(np.percentile(s, p)), 3) for p in (50, 75, 90, 95, 99)}
    return dict(n=len(s), percentiles=pcts,
                recommended_stop_slippage=round(float(np.percentile(s, pct)) / 2.0, 3),
                assumption=f"stop fill inalipa half-spread ya {pct}th percentile (upande mmoja); "
                           "flat 0.3-pip inabadilishwa kwa GOLD tu baada ya Chief approval")


# ---------- self-test (bila data) ----------
def self_test():
    ok = True

    # [1] ev_spread_table: analytic exact (EV−Δ); breakeven = EV
    cands = [dict(event="nr7_break", pair="USDCHF", sl_atr=2.0, tp_atr=1.0,
                  session_filter="no-LATE", ev=1.92),
             dict(event="nr7_break", pair="EURGBP", sl_atr=1.0, tp_atr=1.0,
                  session_filter=None, ev=0.4)]
    rows = ev_spread_table(cands)
    t1 = (rows[0]["ev_dspread"]["+0.5"] == 1.42 and rows[0]["ev_dspread"]["+1.0"] == 0.92
          and rows[1]["ev_dspread"]["+0.5"] == -0.1 and rows[1]["breakeven_dspread"] == 0.4)
    print(f"  [1] EV(dspread) analytic: {rows[0]['ev_dspread']} breakeven={rows[1]['breakeven_dspread']} -> {t1}")
    ok = ok and t1

    # [2] spread_split: WIDE hasi -> verdict ya WIDE-skip; NORMAL split sahihi
    spread_state = np.array(["NORMAL"] * 50 + ["WIDE"] * 50)
    trades = ([(i, i + 2, 1, 2.0, "NY", "-") for i in range(0, 40, 2)]          # NORMAL: +2.0
              + [(i, i + 2, 1, -1.5, "NY", "-") for i in range(50, 90, 2)])     # WIDE: -1.5
    sp = spread_split(trades, spread_state)
    t2 = (sp["NORMAL"]["ev"] == 2.0 and sp["WIDE"]["ev"] == -1.5 and sp["NORMAL"]["n"] == 20
          and "WIDE-skip" in sp["_verdict"] and "DEPLOYMENT" in sp["_verdict"])
    print(f"  [2] spread_split: NORMAL ev={sp['NORMAL']['ev']} WIDE ev={sp['WIDE']['ev']} verdict-skip={('WIDE-skip' in sp['_verdict'])} -> {t2}")
    ok = ok and t2

    # [2b] WIDE chanya -> hakuna skip
    sp2 = spread_split([(i, i + 1, 1, 1.0, "NY", "-") for i in range(50, 70)], spread_state)
    t2b = "hakuna WIDE-skip" in sp2["_verdict"]
    print(f"  [2b] WIDE chanya -> no-skip: {t2b}")
    ok = ok and t2b

    # [3] gold percentile slippage: distribution inayojulikana; guard ya samples chache
    rng = np.random.default_rng(3)
    spreads = np.abs(rng.lognormal(mean=np.log(3.0), sigma=0.4, size=20_000))   # gold-like (pips)
    g = stop_slippage_percentile(spreads, pct=95)
    p95 = float(np.percentile(spreads, 95))
    t3 = abs(g["recommended_stop_slippage"] - p95 / 2) < 0.01 and g["percentiles"][50] < g["percentiles"][99]
    try:
        stop_slippage_percentile([1.0] * 50); t3b = False
    except ValueError:
        t3b = True
    print(f"  [3] gold slippage: rec={g['recommended_stop_slippage']} (~p95/2={p95/2:.3f}) small-sample-guard={t3b} -> {t3 and t3b}")
    ok = ok and t3 and t3b

    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Cost stress (R5): EV(dspread) + spread_state split + gold slippage")
    ap.add_argument("--self-test", action="store_true")
    ap.parse_args()
    return self_test()     # pure module — data runs zinaitwa kutoka scripts za Operator/strategy_lab


if __name__ == "__main__":
    raise SystemExit(main())
