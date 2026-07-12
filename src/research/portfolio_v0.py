"""
portfolio_v0.py — WAVE-1 R4: portfolio layer v0 (SCIENTIST-D design — verbatim; Chief 2026-07-12).

STRAT-001 (nr7×USDCHF SL2/TP1 no-LATE) + STRAT-002 (nr7×USDJPY SL1/TP1 no-LATE) zinaendeshwa kama
streams mbili — deployment risk ni PORTFOLIO risk (FTMO limits ni portfolio-level). Hii module
inapima juu ya windows ZILIZOFUNGULIWA (hakuna dirisha jipya):
  (a) fraction ya SIKU zote mbili zinafire        (overlap ya entries)
  (b) fraction ya SAA (bars) zote mbili zina positions wazi
  (c) correlation ya daily-PnL za streams mbili
  (d) joint equity curve: max joint drawdown vs sum-of-individual DDs
  (e) worst joint DAY (pips na $ chini ya intended sizing) vs FTMO daily-loss limit
RULE (pre-registered na design): daily-PnL corr > 0.4 -> HALVE per-strategy size.

Pure analysis (`analyze`) = self-testable bila data; `run()` inasoma parquet (PC ya Operator) na
inatumia episodes() + cells za PROVEN registry. Rule 8 report: reports/portfolio_v0_report.md.
Self-test: python src/research/portfolio_v0.py --self-test
"""
from __future__ import annotations

import argparse
import sys

import numpy as np

# cells za strategies PROVEN (provenance: S3/S3b registrations; strat_signal.STRATEGIES)
PORTFOLIO = {
    "STRAT-001": dict(event="nr7_break", pair="USDCHF", sl_atr=2.0, tp_atr=1.0,
                      session_filter="no-LATE", vol_filter=None, usd_per_pip=12.0),  # ~risk$120/SL10p scale
    "STRAT-002": dict(event="nr7_break", pair="USDJPY", sl_atr=1.0, tp_atr=1.0,
                      session_filter="no-LATE", vol_filter=None, usd_per_pip=12.0),
}
CORR_HALVE_THRESHOLD = 0.4          # pre-registered (R4): corr>0.4 -> halve per-strategy size
FTMO_DAILY_LOSS = 500.0             # $ (ftmo_config max_daily_loss)


def _daily_pnl(trades, days):
    """PnL kwa siku (realized siku ya EXIT bar). trades = episodes() tuples; days = day-label kwa bar.
    Rudisha dict day -> pnl."""
    out = {}
    for t in trades:
        d = days[t[1]]                              # exit bar day
        out[d] = out.get(d, 0.0) + t[3]
    return out


def _maxdd(series):
    eq = np.cumsum(series)
    return float((np.maximum.accumulate(eq) - eq).max()) if len(series) else 0.0


def analyze(tradesA, tradesB, daysA, daysB, n_barsA=None, n_barsB=None,
            usd_per_pipA=12.0, usd_per_pipB=12.0):
    """R4 metrics (a)-(e) + halve-size rule. trades* = episodes() tuples; days* = day-label kwa bar
    ya pair husika (streams zinaweza kuwa na calendars kidogo tofauti — join kwa day label)."""
    # (a) siku zote mbili zinafire (entries) — denominator: siku za union ya trading za streams
    fireA = {daysA[t[0]] for t in tradesA}
    fireB = {daysB[t[0]] for t in tradesB}
    all_days = sorted(set(daysA) | set(daysB))
    both_fire = len(fireA & fireB)
    frac_days_both = both_fire / max(1, len(all_days))
    frac_days_both_given_any = both_fire / max(1, len(fireA | fireB))

    # (b) saa (bars) zote mbili zina positions wazi — kwa day+intraday index tunatumia bar indices
    # za kila pair juu ya day labels zinazoshirikiwa: approximate kwa hours held per day overlap.
    n_barsA = n_barsA or len(daysA); n_barsB = n_barsB or len(daysB)
    heldA = np.zeros(n_barsA, bool)
    for t in tradesA:
        heldA[t[0]:t[1] + 1] = True
    heldB = np.zeros(n_barsB, bool)
    for t in tradesB:
        heldB[t[0]:t[1] + 1] = True
    # map kwa day: masaa yaliyoshikwa kwa siku kila stream; overlap ya chini (conservative lower
    # bound ni max(0, hA+hB-24); tunatumia min(hA,hB) = upper bound ya saa za pamoja) — ripoti zote
    hoursA = {}; hoursB = {}
    for i, d in enumerate(daysA):
        hoursA[d] = hoursA.get(d, 0) + int(heldA[i])
    for i, d in enumerate(daysB):
        hoursB[d] = hoursB.get(d, 0) + int(heldB[i])
    ub = sum(min(hoursA.get(d, 0), hoursB.get(d, 0)) for d in all_days)
    lb = sum(max(0, hoursA.get(d, 0) + hoursB.get(d, 0) - 24) for d in all_days)
    total_hours = sum(len([i for i, x in enumerate(daysA) if x == d]) for d in all_days) or 1
    frac_hours_both = dict(lower=lb / total_hours, upper=ub / total_hours)

    # (c) daily-PnL correlation (union ya siku; 0 pale stream haina trade)
    pA = _daily_pnl(tradesA, daysA); pB = _daily_pnl(tradesB, daysB)
    sA = np.array([pA.get(d, 0.0) for d in all_days])
    sB = np.array([pB.get(d, 0.0) for d in all_days])
    if sA.std() > 0 and sB.std() > 0:
        corr = float(np.corrcoef(sA, sB)[0, 1])
    else:
        corr = 0.0

    # (d) joint equity: max joint DD vs sum-of-individual
    dd_joint = _maxdd(sA + sB)
    dd_A, dd_B = _maxdd(sA), _maxdd(sB)

    # (e) worst joint day (pips + $) vs FTMO daily loss
    joint_daily_usd = sA * usd_per_pipA + sB * usd_per_pipB
    worst_pips = float((sA + sB).min()) if len(all_days) else 0.0
    worst_usd = float(joint_daily_usd.min()) if len(all_days) else 0.0

    return dict(
        n_days=len(all_days), n_tradesA=len(tradesA), n_tradesB=len(tradesB),
        frac_days_both_fire=round(frac_days_both, 4),
        frac_days_both_fire_given_any=round(frac_days_both_given_any, 4),
        frac_hours_both_held=dict(lower=round(frac_hours_both["lower"], 4),
                                  upper=round(frac_hours_both["upper"], 4)),
        daily_pnl_corr=round(corr, 4),
        maxdd_joint=round(dd_joint, 2), maxdd_sumA_B=round(dd_A + dd_B, 2),
        maxdd_A=round(dd_A, 2), maxdd_B=round(dd_B, 2),
        worst_joint_day_pips=round(worst_pips, 2), worst_joint_day_usd=round(worst_usd, 2),
        ftmo_daily_limit_usd=FTMO_DAILY_LOSS,
        breaches_ftmo_daily=bool(-worst_usd >= FTMO_DAILY_LOSS),
        halve_size=bool(corr > CORR_HALVE_THRESHOLD),
        halve_rule=f"pre-registered: daily-PnL corr > {CORR_HALVE_THRESHOLD} -> halve per-strategy size",
    )


# ---------- run (data ya Operator; windows zilizofunguliwa) ----------
def run(splits=("train", "validation"), tf="H1", holdout_token=None):
    from strategy_lab import load_window, evaluate, _mask_context   # reuse loaders/semantics
    from event_library_v2 import EVENTS_V2
    from event_quality_report import episodes
    import polars as pl
    from latent_structure import state_path
    from datetime import datetime
    from pathlib import Path

    streams = {}
    for name, cell in PORTFOLIO.items():
        pair = cell["pair"]
        trades_all = []; days_all = []
        offset = 0
        for split in splits:
            d = load_window(pair, tf, split, holdout_token)
            if d is None:
                continue
            # day labels: re-load ts kwa window hii (load_window hairudishi ts)
            df = pl.read_parquet(state_path(pair, tf)).sort("ts")
            from strategy_lab import TRAIN_END, VALID_END
            if split == "train":
                df = df.filter(pl.col("ts") < TRAIN_END)
            elif split == "validation":
                df = df.filter((pl.col("ts") >= TRAIN_END) & (pl.col("ts") < VALID_END))
            else:
                df = df.filter(pl.col("ts") >= VALID_END)
            days = df["ts"].dt.strftime("%Y-%m-%d").to_list()
            spec = EVENTS_V2[cell["event"]]
            out = spec["fn"](d["o"], d["h"], d["l"], d["c"], d.get("tc"), d.get("hour"))
            out = _mask_context(out, spec["entry"], d["hour"], d.get("vol"),
                                cell["session_filter"], cell["vol_filter"])
            trs = episodes(out, spec["entry"], d["o"], d["h"], d["l"], d["c"], d["atr"], d["spr"],
                           d["hour"], d.get("vol"), sl_atr=cell["sl_atr"], tp_atr=cell["tp_atr"])
            trades_all += [(t[0] + offset, t[1] + offset, t[2], t[3], t[4], t[5]) for t in trs]
            days_all += days
            offset = len(days_all)
        streams[name] = (trades_all, days_all)

    (tA, dA), (tB, dB) = streams["STRAT-001"], streams["STRAT-002"]
    m = analyze(tA, tB, dA, dB, usd_per_pipA=PORTFOLIO["STRAT-001"]["usd_per_pip"],
                usd_per_pipB=PORTFOLIO["STRAT-002"]["usd_per_pip"])
    L = ["# Portfolio v0 — STRAT-001 + STRAT-002 (WAVE-1 R4)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | splits={splits} | windows ZILIZOFUNGULIWA tu | "
         "RULE pre-registered: corr>0.4 -> halve size*\n"]
    for k, v in m.items():
        L.append(f"- **{k}**: {v}")
    out_p = Path(__file__).resolve().parents[2] / "reports" / "portfolio_v0_report.md"
    out_p.write_text("\n".join(L), encoding="utf-8")
    print(f"Ripoti: {out_p}")
    print(f"corr={m['daily_pnl_corr']} halve_size={m['halve_size']} "
          f"worst_joint_day=${m['worst_joint_day_usd']} (FTMO {FTMO_DAILY_LOSS})")
    return 0


# ---------- self-test (synthetic; bila data) ----------
def _mk_days(n_days, bars_per_day=24):
    return [f"d{k:03d}" for k in range(n_days) for _ in range(bars_per_day)]


def self_test():
    ok = True
    days = _mk_days(50)

    # [1] correlated streams (same-day, aligned pnl) -> corr juu -> HALVE; overlap (a)/(b) > 0
    tA = [(k * 24 + 1, k * 24 + 5, 1, 10.0 if k % 2 == 0 else -8.0, "LONDON", "-") for k in range(40)]
    tB = [(k * 24 + 2, k * 24 + 6, 1, 9.0 if k % 2 == 0 else -7.5, "LONDON", "-") for k in range(40)]
    m = analyze(tA, tB, days, days)
    c_ok = (m["daily_pnl_corr"] > 0.9 and m["halve_size"] is True
            and m["frac_days_both_fire"] > 0.5 and m["frac_hours_both_held"]["upper"] > 0)
    print(f"  [1] correlated: corr={m['daily_pnl_corr']} halve={m['halve_size']} both-fire={m['frac_days_both_fire']} -> {c_ok}")
    ok = ok and c_ok

    # [2] disjoint streams (siku tofauti kabisa, pnl random huru) -> corr~0, no halve, both-fire=0
    rng = np.random.default_rng(5)
    tA2 = [(k * 48 + 1, k * 48 + 4, 1, float(rng.normal(0, 5)), "NY", "-") for k in range(20)]      # shufwa
    tB2 = [(k * 48 + 25, k * 48 + 28, -1, float(rng.normal(0, 5)), "ASIA", "-") for k in range(20)]  # witiri
    m2 = analyze(tA2, tB2, days, days)
    d_ok = (m2["halve_size"] is False and m2["frac_days_both_fire"] == 0.0
            and m2["frac_hours_both_held"]["upper"] == 0.0)
    print(f"  [2] disjoint: corr={m2['daily_pnl_corr']} halve={m2['halve_size']} both-fire={m2['frac_days_both_fire']} -> {d_ok}")
    ok = ok and d_ok

    # [3] joint DD <= sum of individual DDs (diversification arithmetic); worst-day na FTMO flag
    dd_ok = m2["maxdd_joint"] <= m2["maxdd_sumA_B"] + 1e-9
    tA3 = [(1, 2, 1, -30.0, "NY", "-")]     # siku moja hasara kubwa pande zote
    tB3 = [(3, 4, 1, -30.0, "NY", "-")]
    m3 = analyze(tA3, tB3, days, days, usd_per_pipA=12.0, usd_per_pipB=12.0)
    ftmo_ok = m3["worst_joint_day_usd"] == -720.0 and m3["breaches_ftmo_daily"] is True
    print(f"  [3] joint-DD<=sum={dd_ok}; worst-day=${m3['worst_joint_day_usd']} breach={m3['breaches_ftmo_daily']} -> {dd_ok and ftmo_ok}")
    ok = ok and dd_ok and ftmo_ok

    # [4] determinism
    det = analyze(tA, tB, days, days) == m
    print(f"  [4] determinism -> {det}")
    ok = ok and det

    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Portfolio v0 (R4): STRAT-001+002 overlap/corr/joint-DD")
    ap.add_argument("--splits", default="train,validation",
                    help="comma-separated (train,validation[,holdout — inahitaji token])")
    ap.add_argument("--holdout-final", dest="token", default=None)
    ap.add_argument("--tf", default="H1")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    return run(tuple(s.strip() for s in a.splits.split(",")), a.tf, a.token)


if __name__ == "__main__":
    raise SystemExit(main())
