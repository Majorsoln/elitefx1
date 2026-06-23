"""
adaptive_volume_bars.py — PHASE 2 (Chief Quant approved, NO ML). State stability.

Chief Quant directive (2026-06-23): design Adaptive Volume Bars na ujibu swali
MOJA tu kwa sasa (hakuna ML, hakuna entries):

    Do Adaptive Volume Bars produce MORE STABLE state distributions
    than calendar bars?

Wazo: calendar bars (H1) zina activity inayobadilika kwa miaka (tick_regime:
broker/feed scale change). Volume bars ni INFORMATION CLOCK — bar inafungwa kwa
volume, sio saa — kwa hiyo state distribution (hasa Activity) inapaswa kuwa
THABITI zaidi kuvuka miaka. Tunajaribu hilo moja kwa moja.

Mbinu (apples-to-apples, no-lookahead):
  1. Jenga ADAPTIVE volume bars (reuse volume_bars.py: m1 -> daily threshold ->
     form_bars). Jenga calendar H1 bars (reuse market_state_engine.h1_from_ticks).
  2. Weka state labels ZINAZOFANANA kwa bar types ZOTE MBILI:
       volatility_state = ATR(14) rolling terciles (win bars, past tu)
       activity_state   = activity-count rolling terciles (ticks/bar)
     (reuse _atr + _reg3 ya market_state_engine -> definition ileile).
  3. INSTABILITY = wastani wa std ya state-proportions KUVUKA MIAKA. Ndogo = thabiti.
       Volume bars zikiwa thabiti zaidi -> instability_volume < instability_calendar.

NO spread/deseason hapa (volume bars zina muda tofauti) — tunalinganisha
Volatility & Activity tu, kwa definition ileile, ili linganisho liwe la haki.

Output: reports/adaptive_volume_bar_report.md
Endesha: python src/data/adaptive_volume_bars.py
         python src/data/adaptive_volume_bars.py --symbol EURGBP
Self-test: python src/data/adaptive_volume_bars.py --self-test
"""
from __future__ import annotations

import argparse, sys
from datetime import datetime
from pathlib import Path

import numpy as np
import polars as pl
import duckdb

# reuse: bar construction + state labeling (no duplication)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "research"))
from volume_bars import (m1_from_ticks, daily_threshold, form_bars, TARGET_BPD)
from market_state_engine import (h1_from_ticks, time_col, pip, _atr, _reg3)

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config" / "data_config.yaml"

WIN = 500            # rolling window (bars) kwa terciles — sawa kwa bar types zote
MINP = 125
LEVELS = ["LOW", "NORMAL", "HIGH"]
_posix = lambda p: str(p).replace("\\", "/")


def cfg():
    import yaml
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def label_states(df: pl.DataFrame) -> pl.DataFrame:
    """df ina ts, h, l, c, act (activity count). Rudisha + volatility_state,
    activity_state (rolling terciles, no-lookahead, definition ya state engine)."""
    df = _atr(df.sort("ts"))                                  # +atr (h,l,c)
    return df.with_columns([_reg3("atr", WIN, MINP).alias("volatility_state"),
                            _reg3("act", WIN, MINP).alias("activity_state")])


def instability(ts_list, states):
    """Wastani wa std ya state-proportions KUVUKA MIAKA. Ndogo = thabiti.
    UNKNOWN imeondolewa; mwaka wenye < MIN_Y bars umerukwa."""
    MIN_Y = 50
    years = np.array([t.year for t in ts_list])
    props = {lv: [] for lv in LEVELS}
    for y in np.unique(years):
        ss = [s for s, m in zip(states, years == y) if m and s != "UNKNOWN"]
        if len(ss) < MIN_Y:
            continue
        n = len(ss)
        for lv in LEVELS:
            props[lv].append(ss.count(lv) / n)
    disps = [float(np.std(props[lv])) for lv in LEVELS if len(props[lv]) >= 2]
    return float(np.mean(disps)) if disps else float("nan"), len(props["LOW"])


def build_volume_bars(m1: pl.DataFrame) -> pl.DataFrame:
    """Reuse volume_bars.py: m1 -> adaptive volume bars. Rudisha df ts,h,l,c,act."""
    g = m1.group_by("d").agg(pl.col("vol").sum().alias("dv")).sort("d")
    thr = daily_threshold(g["d"].to_list(), g["dv"].to_numpy())
    b = form_bars(m1["ts"].to_list(), m1["d"].to_list(),
                  m1["o"].to_numpy(), m1["h"].to_numpy(), m1["l"].to_numpy(),
                  m1["c"].to_numpy(), m1["vol"].to_numpy(), m1["tc"].to_numpy(), thr)
    return pl.DataFrame(dict(ts=b["t_end"], h=b["h"], l=b["l"], c=b["c"],
                            act=np.array(b["ticks"], float)))


def analyze_pair(con, src, t, pp):
    """Rudisha (cal_inst, vol_inst, n_cal, n_vb) kwa vol & act dims."""
    # calendar H1
    h1 = h1_from_ticks(con, src, t, pp).rename({"tc": "act"})
    cal = label_states(h1.select(["ts", "h", "l", "c", "act"]))
    # adaptive volume bars
    m1 = m1_from_ticks(con, src, t)
    vb = label_states(build_volume_bars(m1))

    out = {}
    for dim in ("volatility_state", "activity_state"):
        ci, ny_c = instability(cal["ts"].to_list(), cal[dim].to_list())
        vi, ny_v = instability(vb["ts"].to_list(), vb[dim].to_list())
        out[dim] = dict(cal=ci, vol=vi, ny=min(ny_c, ny_v))
    return out, len(cal), len(vb)


def run(pairs):
    c = cfg(); raw = REPO_ROOT / c["paths"]["raw_ticks"]
    if not raw.exists():
        print(f"HITILAFU: '{raw}' haipo.", file=sys.stderr); return 1
    con = duckdb.connect(); rows = []
    for sym in pairs:
        base = raw / f"symbol={sym}"
        if not base.exists() or not list(base.rglob("*.parquet")):
            print(f"  {sym}: (hakuna data)"); continue
        src = _posix(base / "**" / "*.parquet")
        t = time_col(con, src); pp = pip(sym)
        print(f"  {sym}: nascan (calendar + volume)...", flush=True)
        res, n_cal, n_vb = analyze_pair(con, src, t, pp)
        rows.append((sym, res, n_cal, n_vb))
        print(f"    calendar={n_cal:,} bars | volume={n_vb:,} bars")
    if not rows:
        print("HITILAFU: hakuna data.", file=sys.stderr); return 1

    L = ["# Adaptive Volume Bars — state distribution stability (PHASE 2)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | INSTABILITY = wastani std ya state-proportions kuvuka miaka "
         f"(ndogo=thabiti) | terciles win={WIN} bars (sawa kwa zote) | calendar=H1 vs adaptive volume bars "
         f"(target {TARGET_BPD}/siku)*\n",
         "> **Swali (Chief):** Je adaptive volume bars zinatoa state distributions THABITI zaidi kuliko "
         "calendar bars? Volume bars = information clock -> zinatarajiwa kuwa thabiti zaidi (hasa Activity, "
         "ambayo huyumba na tick_regime). 'volume better?' = instability(volume) < instability(calendar). "
         "NO ML, NO entries (Chief).\n",
         "## INSTABILITY kwa dimension — calendar (H1) vs volume bars\n",
         "| Pair | dim | instab calendar | instab volume | Δ (cal−vol) | volume thabiti zaidi? |",
         "|------|-----|-----------------|---------------|-------------|-----------------------|"]
    better = {"volatility_state": 0, "activity_state": 0}; tot = 0
    for sym, res, _, _ in rows:
        tot += 1
        for dim in ("volatility_state", "activity_state"):
            d = res[dim]; delta = d["cal"] - d["vol"]
            win = (delta == delta and delta > 0)
            better[dim] += 1 if win else 0
            L.append(f"| {sym} | {dim[:3]} | {d['cal']:.4f} | {d['vol']:.4f} | {delta:+.4f} | "
                     f"{'✅' if win else '—'} |")

    L.append("\n## VERDICT — je volume bars zinaleta state distributions thabiti zaidi?\n")
    for dim in ("volatility_state", "activity_state"):
        L.append(f"- **{dim[:10]}**: volume thabiti zaidi kwa **{better[dim]}/{tot}** pairs")
    act = better["activity_state"]; vol = better["volatility_state"]
    if act > tot / 2:
        verd = ("✅ **NDIYO (hasa Activity)** — volume bars zinastabilize activity distribution "
                f"({act}/{tot}). Information clock inafanya kazi -> Phase 2 ina msingi.")
    else:
        verd = (f"❌ **HAPANA wazi** — volume bars hazikustabilize activity vya kutosha ({act}/{tot}). "
                "Inahitaji uchunguzi kabla ya kuendelea.")
    L.append(f"\n{verd}")
    L.append("\n*Definition ya state ni ileile (ATR/activity terciles, win=500 bars) kwa bar types zote "
             "-> linganisho la haki. INSTABILITY ndogo = state proportions hazibadiliki kwa miaka. NO ML "
             "(Chief). Inayofuata baada ya approval: regime/transition juu ya volume bars. Metric = EV.*")
    out = REPO_ROOT / c["paths"]["reports"] / "adaptive_volume_bar_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """(1) instability: proportions thabiti -> ndogo; zinazoyumba -> kubwa.
       (2) label_states: prices bandia -> labels halali.
       (3) reuse: build_volume_bars inatoa bars kutoka m1 bandia."""
    from datetime import datetime as dt, timedelta
    # (1) instability metric
    rng = np.random.default_rng(0)
    ts = [dt(2018 + (i // 1000), 1, 1) + timedelta(hours=i % 1000) for i in range(5000)]
    stable = list(rng.choice(LEVELS, 5000, p=[0.33, 0.34, 0.33]))      # mwaka-kwa-mwaka sawa
    drift = []
    for i in range(5000):
        yr = i // 1000
        p = [0.6 - 0.12 * yr, 0.2 + 0.0 * yr, 0.2 + 0.12 * yr]          # inahama kila mwaka
        p = [max(0.01, x) for x in p]; p = [x / sum(p) for x in p]
        drift.append(rng.choice(LEVELS, p=p))
    is_stable, _ = instability(ts, stable); is_drift, _ = instability(ts, drift)
    m1_ok = is_stable < is_drift
    print(f"instability: stable={is_stable:.4f} < drift={is_drift:.4f}  ({m1_ok})")

    # (2) label_states on synthetic prices
    n = 3000; close = np.cumsum(rng.normal(0, 0.5, n)) + 1000.0
    df = pl.DataFrame(dict(ts=list(range(n)), h=close + 0.5, l=close - 0.5, c=close,
                           act=np.abs(rng.normal(100, 30, n))))
    lab = label_states(df)
    lab_ok = set(lab["volatility_state"].unique()).issubset(set(LEVELS) | {"UNKNOWN"}) and \
             (lab["activity_state"] != "UNKNOWN").sum() > 0
    print(f"label_states: vol levels ok={lab_ok}")

    # (3) build_volume_bars reuse on synthetic m1
    days = 40; ts2 = []; dts = []; o = []; h = []; l = []; cc = []; vol = []; tc = []
    cur = dt(2020, 1, 1); price = 1.10
    for dy in range(days):
        for minute in range(0, 1440, 3):
            ret = rng.normal(0, 0.0002); op = price; c2 = price * (1 + ret)
            ts2.append(cur); dts.append(cur.date())
            o.append(op); h.append(max(op, c2)); l.append(min(op, c2)); cc.append(c2)
            vol.append(abs(rng.normal(100, 20))); tc.append(int(abs(rng.normal(50, 10))))
            price = c2; cur += timedelta(minutes=3)
    m1 = pl.DataFrame(dict(ts=ts2, d=dts, o=o, h=h, l=l, c=cc, vol=vol, tc=tc))
    vb = build_volume_bars(m1)
    vb_ok = len(vb) > 10 and set(vb.columns) >= {"ts", "h", "l", "c", "act"}
    print(f"build_volume_bars: n={len(vb)} cols_ok={vb_ok}")

    ok = m1_ok and lab_ok and vb_ok
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default=None)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    c = cfg()
    pairs = [a.symbol] if a.symbol else c["pairs"]
    return run(pairs)


if __name__ == "__main__":
    raise SystemExit(main())
