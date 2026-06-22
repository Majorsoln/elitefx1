"""
market_regime.py — PHASE 1 (CQ-003). Market Regime Engine.

"Hakuna event itakayosomwa nje ya regime." Engine hii inaainisha KILA bar (D1)
kwa regime tatu, kutoka metrics zilezile zilizothibitishwa na reports za Phase 0:

  • volatility_regime : LOW | NORMAL | HIGH   (ATR(14), terciles 33/67)
  • activity_regime   : LOW | NORMAL | HIGH   (tick_count, terciles 33/67)
  • spread_regime     : NORMAL | WIDE          (median spread, > p85 = WIDE)

NIDHAMU (no-lookahead): kila bar inaainishwa kwa **rolling distribution ya bars
ZILIZOPITA tu** (window 252, min 60). Bar ya leo HAITUMII data ya baadaye.

Source methodology:
  tick_density_report (activity) · spread_quality_report (spread) ·
  volatility_profile_report (volatility) — Phase 0 = COMPLETE (CQ-001).

Output:
  reports/market_regime_report.md            (mgawanyo + persistence + transitions)
  data/processed/regime/symbol=<P>.parquet   (time series kwa downstream; gitignored)

Endesha (CQ-009: EURGBP kwanza):
  python src/research/market_regime.py                 # EURGBP
  python src/research/market_regime.py --symbol EURUSD
Self-test: python src/research/market_regime.py --self-test
"""
from __future__ import annotations

import argparse, sys
from datetime import datetime
from pathlib import Path

import numpy as np
import duckdb, yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config" / "data_config.yaml"

WIN = 252          # rolling window (~mwaka 1 wa biashara)
MIN_OBS = 60       # historia ya chini kabla ya kuainisha
LO_Q, HI_Q = 0.33, 0.67
WIDE_Q = 0.85
DEFAULT_PAIR = "EURGBP"      # CQ-009


def cfg():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)

def _posix(p): return str(p).replace("\\", "/")
def pip(sym): return 0.01 if "JPY" in sym.upper() else 0.0001

def time_col(con, src):
    sch = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{src}', union_by_name=>true)").fetchall()
    cols = [r[0] for r in sch]
    return next((c for c in cols if any(k in c.lower() for k in ("time","date","ts","stamp"))), None)


def d1_bars(con, src, t, pp):
    """D1 bars (CAST AS DATE -> hakuna pytz): OHLC, tick_count, median spread (pips)."""
    con.execute("SET TimeZone='UTC'")
    q = f"""
        SELECT CAST("{t}" AS DATE) AS d,
               arg_min(bid,"{t}") AS o, max(bid) AS h, min(bid) AS l, arg_max(bid,"{t}") AS c,
               COUNT(*) AS tc,
               approx_quantile((ask-bid)/{pp}, 0.5) AS spr
        FROM read_parquet('{src}', union_by_name=>true)
        WHERE bid>0 AND ask>0 AND ask>=bid
        GROUP BY 1 ORDER BY 1
    """
    return con.execute(q).fetchall()


def _atr(h, l, c, n=14):
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum.reduce([h - l, np.abs(h - pc), np.abs(l - pc)])
    a = 1/n; atr = np.empty_like(tr); atr[0] = tr[0]
    for i in range(1, len(tr)):
        atr[i] = a*tr[i] + (1-a)*atr[i-1]
    return atr


def _roll_class3(x, win=WIN, lo=LO_Q, hi=HI_Q, min_obs=MIN_OBS):
    """LOW/NORMAL/HIGH kwa rolling terciles za PAST tu (no-lookahead)."""
    out = np.array(["UNKNOWN"] * len(x), dtype=object)
    for i in range(len(x)):
        past = x[max(0, i-win):i]
        past = past[np.isfinite(past)]
        if len(past) < min_obs or not np.isfinite(x[i]):
            continue
        ql, qh = np.quantile(past, [lo, hi])
        out[i] = "LOW" if x[i] < ql else ("HIGH" if x[i] > qh else "NORMAL")
    return out


def _roll_class2(x, q=WIDE_Q, win=WIN, min_obs=MIN_OBS, hi="WIDE", lo="NORMAL"):
    out = np.array(["UNKNOWN"] * len(x), dtype=object)
    for i in range(len(x)):
        past = x[max(0, i-win):i]
        past = past[np.isfinite(past)]
        if len(past) < min_obs or not np.isfinite(x[i]):
            continue
        out[i] = hi if x[i] > np.quantile(past, q) else lo
    return out


def classify(bars):
    """bars=[(date,o,h,l,c,tc,spr)] -> dict ya arrays (no-lookahead regimes)."""
    b = [r for r in bars if r[0].isoweekday() <= 5 and r[4] and r[4] > 0]
    if len(b) < MIN_OBS + 5:
        return None
    d = [r[0] for r in b]
    h = np.array([r[2] for r in b], float); l = np.array([r[3] for r in b], float)
    c = np.array([r[4] for r in b], float); tc = np.array([r[5] for r in b], float)
    spr = np.array([r[6] for r in b], float)
    atr = _atr(h, l, c)
    return dict(date=d, atr=atr, tc=tc, spr=spr,
                volatility_regime=_roll_class3(atr),
                activity_regime=_roll_class3(tc),
                spread_regime=_roll_class2(spr))


def _dist(arr, levels):
    known = [x for x in arr if x != "UNKNOWN"]
    n = len(known) or 1
    return {lv: (sum(1 for x in known if x == lv), sum(1 for x in known if x == lv)/n) for lv in levels}, len(known)

def _persistence(arr):
    """Avg run length (bars) ya regime (bila UNKNOWN)."""
    runs = []; cur = None; ln = 0
    for x in arr:
        if x == "UNKNOWN":
            continue
        if x == cur:
            ln += 1
        else:
            if cur is not None:
                runs.append(ln)
            cur = x; ln = 1
    if cur is not None:
        runs.append(ln)
    return float(np.mean(runs)) if runs else 0.0


def write_report(sym, R, out_path):
    d = R["date"]
    L = [f"# Market Regime Report — {sym} (PHASE 1, CQ-003)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | D1 | no-lookahead rolling (win={WIN}, min={MIN_OBS}) | "
         f"vol/activity terciles {LO_Q}/{HI_Q} | spread WIDE > p{int(WIDE_Q*100)}*\n",
         f"Bars: {len(d)} | {d[0]} → {d[-1]}\n",
         "> Kila bar imeainishwa kwa distribution ya bars ZILIZOPITA tu — hakuna lookahead. "
         "Hii ndiyo context ambayo KILA event itasomwa ndani yake (CQ-002/003).\n",
         "## Mgawanyo wa regime\n",
         "| Dimension | LOW/NORMAL | NORMAL | HIGH/WIDE | n |",
         "|-----------|-----------|--------|-----------|---|"]
    vd, vn = _dist(R["volatility_regime"], ["LOW","NORMAL","HIGH"])
    ad, an = _dist(R["activity_regime"], ["LOW","NORMAL","HIGH"])
    sd, sn = _dist(R["spread_regime"], ["NORMAL","WIDE"])
    L.append(f"| volatility | {vd['LOW'][0]} ({vd['LOW'][1]*100:.0f}%) | {vd['NORMAL'][0]} ({vd['NORMAL'][1]*100:.0f}%) | {vd['HIGH'][0]} ({vd['HIGH'][1]*100:.0f}%) | {vn} |")
    L.append(f"| activity | {ad['LOW'][0]} ({ad['LOW'][1]*100:.0f}%) | {ad['NORMAL'][0]} ({ad['NORMAL'][1]*100:.0f}%) | {ad['HIGH'][0]} ({ad['HIGH'][1]*100:.0f}%) | {an} |")
    L.append(f"| spread | — | {sd['NORMAL'][0]} ({sd['NORMAL'][1]*100:.0f}%) | {sd['WIDE'][0]} ({sd['WIDE'][1]*100:.0f}%) | {sn} |")

    L.append("\n## Persistence (avg run length, bars)\n")
    L.append(f"- volatility: {_persistence(R['volatility_regime']):.1f} | "
             f"activity: {_persistence(R['activity_regime']):.1f} | "
             f"spread: {_persistence(R['spread_regime']):.1f}")

    # latest snapshot
    def last_known(a):
        for x in reversed(a):
            if x != "UNKNOWN":
                return x
        return "UNKNOWN"
    L.append("\n## Regime ya hivi karibuni\n")
    L.append(f"- date {d[-1]}: volatility={last_known(R['volatility_regime'])}, "
             f"activity={last_known(R['activity_regime'])}, spread={last_known(R['spread_regime'])}")

    L.append("\n---\n*CQ-003: regime engine ndiyo context layer. No-lookahead (rolling past). "
             "Terciles -> LOW/NORMAL/HIGH; spread p85 -> WIDE. Downstream (volume_bars, "
             "event_diagnostics) zita-join regime hii. Metric rasmi = Expected Value (CQ-008).*")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(L), encoding="utf-8")


def save_series(sym, R, c_cfg):
    import polars as pl
    df = pl.DataFrame({
        "date": [str(x) for x in R["date"]],
        "atr": R["atr"], "tick_count": R["tc"], "spread_med": R["spr"],
        "volatility_regime": list(R["volatility_regime"]),
        "activity_regime": list(R["activity_regime"]),
        "spread_regime": list(R["spread_regime"]),
    })
    out = REPO_ROOT / c_cfg["paths"]["processed"] / "regime" / f"symbol={sym}.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(out)
    return out


def run(sym):
    c = cfg(); raw = REPO_ROOT / c["paths"]["raw_ticks"]
    base = raw / f"symbol={sym}"
    if not base.exists() or not list(base.rglob("*.parquet")):
        print(f"HITILAFU: hakuna data ya {sym} chini ya {base}", file=sys.stderr); return 1
    con = duckdb.connect()
    src = _posix(base / "**" / "*.parquet")
    t = time_col(con, src)
    print(f"  {sym}: nascan D1...", flush=True)
    R = classify(d1_bars(con, src, t, pip(sym)))
    if not R:
        print("HITILAFU: bars hazitoshi.", file=sys.stderr); return 1
    rep = REPO_ROOT / c["paths"]["reports"] / "market_regime_report.md"
    write_report(sym, R, rep)
    ser = save_series(sym, R, c)
    print(f"Ripoti: {rep.relative_to(REPO_ROOT)}")
    print(f"Series: {ser.relative_to(REPO_ROOT)} (downstream)")
    return 0


def self_test():
    """Planted: cluster ya HIGH vol + HIGH activity inatambulika; mgawanyo karibu terciles."""
    from datetime import datetime as dt, timedelta
    rng = np.random.default_rng(0)
    bars = []; price = 0.85; day = dt(2016, 1, 4); made = 0
    while made < 500:
        if day.isoweekday() <= 5:
            hi_period = 300 <= made < 380           # cluster ya vol/activity kubwa
            vol = 0.004 if hi_period else 0.0015
            tcount = 40000 if hi_period else 12000
            ret = rng.normal(0, vol)
            o = price; c = price*(1+ret)
            h = max(o,c)*(1+abs(rng.normal(0,vol/2))); l = min(o,c)*(1-abs(rng.normal(0,vol/2)))
            spr = abs(rng.normal(0.9, 0.1))
            bars.append((day, o, h, l, c, int(tcount+rng.normal(0,500)), spr))
            price = c; made += 1
        day += timedelta(days=1)
    R = classify(bars)
    vd, vn = _dist(R["volatility_regime"], ["LOW","NORMAL","HIGH"])
    ad, _ = _dist(R["activity_regime"], ["LOW","NORMAL","HIGH"])
    # bars za cluster (index ~300-380, baada ya warmup) ziwe HIGH
    hi_idx = [i for i, d in enumerate(R["date"]) if 305 <= i < 375]
    hi_hits = sum(1 for i in hi_idx if R["volatility_regime"][i] == "HIGH")
    print(f"vol dist L/N/H = {vd['LOW'][0]}/{vd['NORMAL'][0]}/{vd['HIGH'][0]} | "
          f"cluster HIGH hits {hi_hits}/{len(hi_idx)}")
    print(f"activity HIGH% = {ad['HIGH'][1]*100:.0f}%")
    ok = (vn > 200 and hi_hits > len(hi_idx)*0.6 and vd["HIGH"][0] > 0 and vd["LOW"][0] > 0)
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default=DEFAULT_PAIR)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    return run(a.symbol)


if __name__ == "__main__":
    raise SystemExit(main())
