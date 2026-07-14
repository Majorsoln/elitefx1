"""
gold_spread_quality.py — WAVE-B-prep: XAUUSD spread-quality check (HC2-03/05/10 gold gate).

Charter (cycle2_strategy_hypotheses.md §6 risk #4): XAUUSD max_spread=60 ni **provisional**; kabla ya
kuingiza gold kwenye S1 ya HC2-03/05/10, spread halisi lazima uthibitishwe — vinginevyo EV ya gold
itakuwa optimistic. Module hii = **READ-ONLY**: inasoma states za XAUUSD 15m NA 30m, inakokotoa
usambazaji wa spread (median/p90/p95/p99, pips; pip=0.01), inalinganisha na ATR (cost-share) na
max_spread ya sasa, na **INAPENDEKEZA** max_spread ya data-driven (~p95) kwa ripoti. **HAIBADILISHI
config** (Chief ruling — pendekezo tu; Chief/Operator waamue).

Reuse: `latent_structure.state_path` (mpangilio wa parquet), `market_state_engine.pip` (XAUUSD 0.01).
NB (units): column `spr` tayari iko **pips** (engine: median((ask-bid)/pip)); column `atr` iko **price**
units — loaders (strategy_lab.load_window) hu-gawanya kwa pip, kwa hivyo atr_pips = atr / pip.

Data iko PC ya Operator (R-1): module inashughulikia parquet isiyopo kwa neema (coverage gap kwa
report). Self-test = synthetic (bila data ya nje).

Endesha (PC ya data):  python gold_spread_quality.py     -> reports/xauusd_spread_quality.md
Self-test (bila data):  python gold_spread_quality.py --self-test
"""
from __future__ import annotations

import argparse
import math
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
SYM = "XAUUSD"
TFS = ("15m", "30m")
PROVISIONAL_MAX_SPREAD = 60          # config/data_config.yaml (provisional; pip=0.01)
# Cost-share gate (charter §5): gross ya trade ya kushinda ~ tp_atr×ATR; cost = spread (mara moja) +
# slip. HC2-03/05/10 zote zina TP >= 2.0R. Gold "inafaa" kama cost-share @p95 iko chini ya kizingiti.
TP_ATR_REF = 2.0                     # HC2-10 TP; HC2-03/05 pia >= 2.0
COST_SHARE_OK = 0.25                 # (spr_p95)/(TP_ATR×ATR_med) < 0.25 -> gold viable (headroom ya slip)


def spread_stats(spr_pips):
    """Usambazaji wa spread (pips). spr tayari iko pips (engine). None kama hakuna data halali."""
    x = np.asarray(spr_pips, float)
    x = x[np.isfinite(x)]
    if x.size == 0:
        return None
    return dict(n=int(x.size), median=float(np.median(x)),
                p90=float(np.percentile(x, 90)), p95=float(np.percentile(x, 95)),
                p99=float(np.percentile(x, 99)), mean=float(x.mean()), max=float(x.max()))


def recommend_max_spread(p95):
    """Pendekezo la max_spread ya data-driven ~ p95 (round juu hadi 5 ya karibu — headroom ndogo).
    SI kubadilisha config (Chief ruling); ni namba ya kupendekeza kwenye report."""
    return int(math.ceil(p95 / 5.0) * 5)


def cost_share(spr_p95, atr_med_pips, tp_atr=TP_ATR_REF):
    """Sehemu ya gross (tp_atr×ATR) inayoliwa na spread @p95 (mara moja kwa trade). Slip haijajumuishwa
    (lower bound; report inaeleza). NaN kama atr<=0."""
    gross = tp_atr * atr_med_pips
    return spr_p95 / gross if gross > 0 else float("nan")


def _load_state(sym, tf):
    """READ-ONLY: soma state parquet. None kama haipo (data iko PC ya Operator — R-1)."""
    from latent_structure import state_path
    import polars as pl
    p = state_path(sym, tf)
    if not p.exists():
        return None
    return pl.read_parquet(p)


def analyze_tf(df, sym, tf):
    """spr stats (pips) + ATR median (pips) + cost-share proxy. df = state parquet ya tf."""
    from market_state_engine import pip
    pp = pip(sym)
    st = spread_stats(df["spr"].to_numpy())
    if st is None:
        return None
    atr_pips = np.asarray(df["atr"].to_numpy(), float) / pp        # atr column = price -> pips
    atr_med = float(np.nanmedian(atr_pips))
    st.update(tf=tf, atr_med_pips=atr_med,
              spr_med_over_atr=(st["median"] / atr_med if atr_med > 0 else float("nan")),
              spr_p95_over_atr=(st["p95"] / atr_med if atr_med > 0 else float("nan")),
              cost_share_p95=cost_share(st["p95"], atr_med))
    return st


def analyze(sym=SYM, tfs=TFS):
    """Rudisha {tf: stats|None}. None per-tf = parquet haipo (coverage gap)."""
    res = {}
    for tf in tfs:
        df = _load_state(sym, tf)
        res[tf] = analyze_tf(df, sym, tf) if df is not None else None
    return res


def _verdict(res):
    """Gold inafaa WAVE-B S1? Msingi = 30m (default ya entry; 15m ni granularity-only). SUITABLE kama
    cost_share_p95 (30m) < COST_SHARE_OK; MARGINAL kama < 2×; vinginevyo COST-FRAGILE."""
    s30 = res.get("30m")
    if s30 is None:
        return "NO-DATA", "state parquet ya 30m haipo — Operator aendeshe intraday_state_engine kwanza."
    cs = s30["cost_share_p95"]
    if cs < COST_SHARE_OK:
        return "SUITABLE", f"cost-share @p95 (TP {TP_ATR_REF}R) = {cs:.2%} < {COST_SHARE_OK:.0%}."
    if cs < 2 * COST_SHARE_OK:
        return "MARGINAL", f"cost-share @p95 = {cs:.2%} (kati ya {COST_SHARE_OK:.0%} na {2*COST_SHARE_OK:.0%})."
    return "COST-FRAGILE", f"cost-share @p95 = {cs:.2%} >= {2*COST_SHARE_OK:.0%} — spread inameza edge."


def run(sym=SYM, out_root=REPO_ROOT):
    res = analyze(sym)
    verdict, why = _verdict(res)
    L = [f"# XAUUSD Spread-Quality Check — WAVE-B gold gate\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | {sym} | TF: {', '.join(TFS)} | pip=0.01 | "
         f"READ-ONLY (HAIBADILISHI config) | charter §6 risk #4*\n",
         "> Provisional `max_spread_pips: XAUUSD = 60` inahitaji uthibitisho wa data kabla gold iingie "
         f"S1 ya HC2-03/05/10. Pendekezo la data-driven hapa (~p95) = **pendekezo tu**; Chief/Operator waamue.\n"]
    s30 = res.get("30m")
    rec = recommend_max_spread(s30["p95"]) if s30 else None
    L.append("\n## Spread distribution (pips)\n")
    L.append("| TF | n | median | p90 | p95 | p99 | max | ATR med (pips) | spr_med/ATR | spr_p95/ATR | cost-share@p95 (TP2R) |")
    L.append("|----|---|--------|-----|-----|-----|-----|----------------|-------------|-------------|-----------------------|")
    for tf in TFS:
        s = res.get(tf)
        if s is None:
            L.append(f"| {tf} | — | — | — | — | — | — | — | — | — | *parquet haipo (coverage gap)* |")
        else:
            L.append(f"| {tf} | {s['n']:,} | {s['median']:.1f} | {s['p90']:.1f} | {s['p95']:.1f} | "
                     f"{s['p99']:.1f} | {s['max']:.1f} | {s['atr_med_pips']:.1f} | "
                     f"{s['spr_med_over_atr']:.3f} | {s['spr_p95_over_atr']:.3f} | {s['cost_share_p95']:.2%} |")
    L.append(f"\n## Pendekezo (SI kubadilisha config)\n")
    L.append(f"- max_spread ya sasa (provisional): **{PROVISIONAL_MAX_SPREAD}** pips")
    if s30 is not None:
        L.append(f"- **Pendekezo la data-driven (~p95 30m, round-5): `XAUUSD: {rec}`** "
                 f"(p95={s30['p95']:.1f}; {'SHUSHA' if rec < PROVISIONAL_MAX_SPREAD else 'PANDISHA'} "
                 f"kutoka {PROVISIONAL_MAX_SPREAD})")
        L.append(f"- ATR 30m med = {s30['atr_med_pips']:.1f} pips; spr p95 = {s30['p95']:.1f} pips "
                 f"→ spr p95 ni {s30['spr_p95_over_atr']:.1%} ya ATR (cost-share @TP {TP_ATR_REF}R = "
                 f"{s30['cost_share_p95']:.2%}; slip haijajumuishwa — lower bound).")
    else:
        L.append("- Pendekezo halipatikani — state parquet ya 30m haipo (Operator aendeshe engine).")
    L.append(f"\n## VERDICT: gold WAVE-B S1 → **{verdict}**\n")
    L.append(f"- {why}")
    L.append(f"- Msingi = **30m** (default ya entry; 15m = granularity-only, charter §0.5 cost-trap). "
             f"HC2-03/05/10 ndizo hypotheses zenye XAUUSD.")
    L.append("\n## Known Limitations\n")
    L.append("1. **READ-ONLY** — hakuna config iliyobadilishwa (Chief ruling). Pendekezo tu.")
    L.append("2. **Cost-share = lower bound** (slip haijajumuishwa; spread mara moja kwa trade). Report "
             "ya S1 (cost_stress ev_spread_table) ndio hesabu kamili ya EV(Δspread) per cell.")
    L.append("3. **Data iko PC ya Operator (R-1)** — parquet ikikosekana, report inaonyesha coverage gap; "
             "self-test = synthetic (bila data ya nje).")
    L.append("4. spr = median per bar (engine); tail intrabar (spikes za news) haionekani hapa — "
             "p99 ndio proxy ya karibu zaidi ya tail risk.")
    L.append("\n*WAVE-B-prep | charter §6 risk #4 | READ-ONLY | Profitable != Tradable Edge.*")
    out = out_root / "reports" / "xauusd_spread_quality.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"Ripoti: {out.relative_to(out_root)} | verdict={verdict} | "
          f"rec_max_spread={rec if rec is not None else 'NO-DATA'}")
    return 0


# ---------- self-test (bila data ya nje, synthetic) ----------
def self_test():
    ok = True

    # (1) spread_stats: ordering (median<=p90<=p95<=p99<=max) + values sahihi kwa dist inayojulikana
    rng = np.random.default_rng(7)
    spr = 35.0 * np.exp(rng.normal(0, 0.25, 20000))            # lognormal ~ gold spread (~35 median)
    st = spread_stats(spr)
    order_ok = st["median"] <= st["p90"] <= st["p95"] <= st["p99"] <= st["max"]
    med_ok = abs(st["median"] - 35.0) < 3.0                    # median ya lognormal ~ scale
    print(f"  [1] spread_stats: median={st['median']:.1f} p95={st['p95']:.1f} p99={st['p99']:.1f} "
          f"ordering={order_ok} -> {'OK' if order_ok and med_ok else 'FAIL'}")
    ok = ok and order_ok and med_ok

    # (2) spread_stats: empty/all-nan -> None (data gap)
    none_ok = spread_stats([]) is None and spread_stats([np.nan, np.nan]) is None
    print(f"  [2] empty/nan -> None: {none_ok} -> {'OK' if none_ok else 'FAIL'}")
    ok = ok and none_ok

    # (3) recommend_max_spread: ~p95 round-5 up; cost_share math
    rec = recommend_max_spread(47.2)
    cs = cost_share(50.0, 200.0, tp_atr=2.0)                   # 50/(2*200)=0.125
    rec_ok = rec == 50 and abs(cs - 0.125) < 1e-9
    print(f"  [3] recommend(47.2)->{rec} (==50) · cost_share(50,200,2)={cs:.3f} (==0.125) -> {'OK' if rec_ok else 'FAIL'}")
    ok = ok and rec_ok

    # (4) analyze_tf via synthetic polars df (spr pips + atr price-units): units + cost-share
    import polars as pl
    n = 5000
    spr_c = 35.0 * np.exp(rng.normal(0, 0.25, n))
    atr_price = np.full(n, 2.0)                                # price units; pip=0.01 -> 200 pips
    df = pl.DataFrame({"spr": spr_c, "atr": atr_price})
    s = analyze_tf(df, "XAUUSD", "30m")
    atr_ok = abs(s["atr_med_pips"] - 200.0) < 1e-6             # 2.0/0.01 = 200 pips
    cs_ok = abs(s["cost_share_p95"] - (s["p95"] / (2.0 * 200.0))) < 1e-9
    ratio_ok = abs(s["spr_p95_over_atr"] - s["p95"] / 200.0) < 1e-9
    print(f"  [4] analyze_tf: atr_med_pips={s['atr_med_pips']:.0f}(==200) cost_share@p95={s['cost_share_p95']:.3f} "
          f"ratio-ok={ratio_ok} -> {'OK' if atr_ok and cs_ok and ratio_ok else 'FAIL'}")
    ok = ok and atr_ok and cs_ok and ratio_ok

    # (5) verdict logic: SUITABLE (spread ndogo) vs COST-FRAGILE (spread kubwa) vs NO-DATA
    v_suit = _verdict({"30m": dict(cost_share_p95=0.10)})[0]
    v_marg = _verdict({"30m": dict(cost_share_p95=0.30)})[0]
    v_frag = _verdict({"30m": dict(cost_share_p95=0.80)})[0]
    v_none = _verdict({"30m": None})[0]
    verdict_ok = (v_suit == "SUITABLE" and v_marg == "MARGINAL"
                  and v_frag == "COST-FRAGILE" and v_none == "NO-DATA")
    print(f"  [5] verdict: 0.10->{v_suit} 0.30->{v_marg} 0.80->{v_frag} none->{v_none} -> {'OK' if verdict_ok else 'FAIL'}")
    ok = ok and verdict_ok

    # (6) READ-ONLY: _load_state ya parquet isiyopo -> None (hakuna crash; config haiguswi)
    missing_ok = _load_state("XAUUSD__NOPE", "30m") is None
    print(f"  [6] READ-ONLY missing parquet -> None: {missing_ok} -> {'OK' if missing_ok else 'FAIL'}")
    ok = ok and missing_ok

    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
