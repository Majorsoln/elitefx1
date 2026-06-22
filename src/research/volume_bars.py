"""
volume_bars.py — PHASE 2 (CQ-004). ADAPTIVE Volume Bars.

FIXED VOLUME BARS = REJECTED (Chief). tick-scale imebadilika kwa miaka
(tick_regime: broker/feed) — threshold ya kudumu (1000/5000/10000 ticks)
ingetoa bars nyingi mno mwaka mmoja, chache mwingine. Badala yake:

  ADAPTIVE threshold (no-lookahead): tunalenga ~TARGET_BPD bars kwa siku.
    threshold_siku[d] = (wastani wa volume/siku, trailing ROLL_DAYS) / TARGET_BPD
  Volume bar inafungwa kila cumulative volume (bid_vol+ask_vol) inafika
  threshold ya siku husika. Activity ikipanda -> threshold inapanda -> idadi
  ya bars/siku inakaa thabiti (information clock, sio time clock).

Faida: bars/siku thabiti kwa miaka YOTE (licha ya tick_regime scale change),
na bar DURATION inakuwa fupi wakati wa activity kubwa (taarifa nyingi) — ndiyo
sababu ya volume bars.

Chanzo: raw ticks -> 1m bars (volume) -> adaptive volume bars.
Output: data/processed/volume_bars/symbol=<P>.parquet  (downstream; gitignored)
        reports/volume_bars_report.md
Endesha: python src/research/volume_bars.py                 (zote)
         python src/research/volume_bars.py --symbol EURGBP
Self-test: python src/research/volume_bars.py --self-test
"""
from __future__ import annotations

import argparse, sys
from datetime import datetime
from pathlib import Path

import numpy as np
import polars as pl
import duckdb, yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config" / "data_config.yaml"

TARGET_BPD = 24        # lengo: bars kwa siku (volume-clocked)
ROLL_DAYS = 20         # trailing window kwa makadirio ya volume/siku
MIN_DAYS = 5           # historia ya chini kabla ya kuanza


def cfg():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)

def _posix(p): return str(p).replace("\\", "/")

def time_col(con, src):
    sch = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{src}', union_by_name=>true)").fetchall()
    cols = [r[0] for r in sch]
    return next((c for c in cols if any(k in c.lower() for k in ("time","date","ts","stamp"))), None)


def m1_from_ticks(con, src, t) -> pl.DataFrame:
    """1m bars (CAST AS TIMESTAMP -> hakuna pytz): OHLC + volume + tick_count + date."""
    con.execute("SET TimeZone='UTC'")
    q = f"""
        SELECT time_bucket(INTERVAL 1 MINUTE, CAST("{t}" AS TIMESTAMP)) AS ts,
               CAST("{t}" AS DATE) AS d,
               arg_min(bid,"{t}") AS o, max(bid) AS h, min(bid) AS l, arg_max(bid,"{t}") AS c,
               SUM(COALESCE(bid_vol,0)+COALESCE(ask_vol,0)) AS vol, COUNT(*) AS tc
        FROM read_parquet('{src}', union_by_name=>true)
        WHERE bid>0 AND ask>0 AND ask>bid
        GROUP BY 1,2 ORDER BY 1
    """
    return con.execute(q).pl()


def daily_threshold(dates_unique, daily_vol):
    """threshold_siku[d] = trailing ROLL_DAYS mean(daily_vol) / TARGET_BPD (no-lookahead).
    Rudisha dict date->threshold (None kwa warmup)."""
    thr = {}
    for i, d in enumerate(dates_unique):
        past = daily_vol[max(0, i-ROLL_DAYS):i]      # siku zilizopita TU
        if len(past) < MIN_DAYS:
            thr[d] = None
        else:
            thr[d] = float(np.mean(past)) / TARGET_BPD
    return thr


def form_bars(ts, dates, o, h, l, c, vol, tc, thr_by_date):
    """Tengeneza adaptive volume bars kutoka 1m arrays. Rudisha dict ya arrays."""
    out = dict(t_start=[], t_end=[], o=[], h=[], l=[], c=[], volume=[], ticks=[], minutes=[])
    cum = 0.0; bo = bh = bl = bc = None; bt0 = None; bvol = 0.0; btk = 0; bmin = 0
    for i in range(len(ts)):
        thr = thr_by_date.get(dates[i])
        if thr is None or not (thr > 0):
            continue                                  # warmup
        if bo is None:                                # anza bar mpya
            bo = o[i]; bh = h[i]; bl = l[i]; bt0 = ts[i]
        bh = max(bh, h[i]); bl = min(bl, l[i]); bc = c[i]
        bvol += vol[i]; btk += int(tc[i]); bmin += 1; cum += vol[i]
        if cum >= thr:                                # funga bar
            out["t_start"].append(bt0); out["t_end"].append(ts[i])
            out["o"].append(bo); out["h"].append(bh); out["l"].append(bl); out["c"].append(bc)
            out["volume"].append(bvol); out["ticks"].append(btk); out["minutes"].append(bmin)
            cum = 0.0; bo = None; bvol = 0.0; btk = 0; bmin = 0
    return out


def _per_year(dates, vals, years):
    out = {}
    yarr = np.array([d.year for d in dates])
    for y in years:
        m = yarr == y
        out[y] = float(np.mean(vals[m])) if m.any() else float("nan")
    return out


def analyze(m1: pl.DataFrame):
    """Rudisha (bars dict, summary dict). Pia hesabu fixed-vs-adaptive bars/siku kwa mwaka."""
    g = m1.group_by("d").agg(pl.col("vol").sum().alias("dv")).sort("d")
    dates_u = g["d"].to_list(); dvol = g["dv"].to_numpy()
    thr_by_date = daily_threshold(dates_u, dvol)
    ts = m1["ts"].to_list(); dts = m1["d"].to_list()
    o=m1["o"].to_numpy(); h=m1["h"].to_numpy(); l=m1["l"].to_numpy()
    c=m1["c"].to_numpy(); vol=m1["vol"].to_numpy(); tc=m1["tc"].to_numpy()
    bars = form_bars(ts, dts, o, h, l, c, vol, tc, thr_by_date)

    # bars/siku (adaptive halisi) kwa mwaka
    bdays = np.array([t.date() for t in bars["t_end"]])
    uniq, counts = np.unique(bdays, return_counts=True)
    bpd_dates = [d for d in uniq]; bpd_vals = counts.astype(float)
    years = sorted({d.year for d in dates_u})
    adaptive_bpd = _per_year(bpd_dates, bpd_vals, years)
    # FIXED threshold = global median daily_vol / TARGET_BPD -> bars/siku = dv/fixed
    fixed_thr = float(np.median(dvol)) / TARGET_BPD
    fixed_bpd_daily = dvol / fixed_thr
    fixed_bpd = _per_year(dates_u, fixed_bpd_daily, years)

    minutes = np.array(bars["minutes"], float)
    summ = dict(n_bars=len(bars["o"]), years=years,
                adaptive_bpd=adaptive_bpd, fixed_bpd=fixed_bpd,
                dur_med=float(np.median(minutes)) if len(minutes) else 0,
                dur_p10=float(np.percentile(minutes,10)) if len(minutes) else 0,
                dur_p90=float(np.percentile(minutes,90)) if len(minutes) else 0)
    return bars, summ


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
        t = time_col(con, src)
        print(f"  {sym}: nascan 1m...", flush=True)
        m1 = m1_from_ticks(con, src, t)
        bars, summ = analyze(m1)
        out = REPO_ROOT / c["paths"]["processed"] / "volume_bars" / f"symbol={sym}.parquet"
        out.parent.mkdir(parents=True, exist_ok=True)
        pl.DataFrame({k: bars[k] for k in bars}).write_parquet(out)
        rows.append((sym, summ))
        print(f"    bars={summ['n_bars']:,} dur_med={summ['dur_med']:.0f}min")
    if not rows:
        print("HITILAFU: hakuna data.", file=sys.stderr); return 1

    years = sorted({y for _, s in rows for y in s["years"]})
    L = ["# Adaptive Volume Bars Report (PHASE 2, CQ-004)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | volume = bid_vol+ask_vol | target {TARGET_BPD} bars/siku | "
         f"adaptive threshold = trailing {ROLL_DAYS}d mean(daily vol)/target (no-lookahead)*\n",
         "> FIXED bars = REJECTED. Adaptive threshold inashika tick_regime scale change -> bars/siku "
         "THABITI kila mwaka. Bar duration (min) inafupika activity ikipanda = information clock.\n",
         "## Bars/siku kwa mwaka — ADAPTIVE (thabiti) vs FIXED (haiyumbi)\n",
         "| Pair | metric | " + " | ".join(str(y) for y in years) + " |",
         "|------|--------|" + "----|" * len(years)]
    for sym, s in rows:
        a = s["adaptive_bpd"]; f = s["fixed_bpd"]
        L.append(f"| {sym} | adaptive | " + " | ".join(f"{a.get(y,float('nan')):.0f}" for y in years) + " |")
        L.append(f"| {sym} | fixed | " + " | ".join(f"{f.get(y,float('nan')):.0f}" for y in years) + " |")
    L += ["\n## Bar duration (dakika/bar) + idadi\n",
          "| Pair | n_bars | dur median | dur p10 | dur p90 |",
          "|------|--------|-----------|---------|---------|"]
    for sym, s in rows:
        L.append(f"| {sym} | {s['n_bars']:,} | {s['dur_med']:.0f} | {s['dur_p10']:.0f} | {s['dur_p90']:.0f} |")
    L.append("\n---\n*ADAPTIVE: threshold inafuata kasi ya volume ya hivi karibuni -> bars/siku thabiti "
             "(linganisha adaptive vs fixed kwa mwaka: fixed inayumba na tick_regime, adaptive haiyumbi). "
             "Bar duration fupi = activity kubwa (information clock). Inayofuata: regime_transition kwenye "
             "volume bars -> Event Diagnostics. Metric = EV (CQ-008).*")
    outp = REPO_ROOT / c["paths"]["reports"] / "volume_bars_report.md"
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {outp.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """1m synthetic yenye VOLUME SCALE JUMP (×2 baada ya siku 100).
       Adaptive -> bars/siku thabiti pande zote; FIXED -> inaruka ×2."""
    from datetime import datetime as dt, timedelta
    rng = np.random.default_rng(0)
    ts=[];dts=[];o=[];h=[];l=[];c=[];vol=[];tc=[]
    price=1.10; cur=dt(2020,1,1); days=200
    for dy in range(days):
        scale = 1.0 if dy < 100 else 2.0                 # tick_regime scale change
        for minute in range(1440):
            if rng.random() < 0.3:                        # baadhi ya dakika hazina tick
                cur += timedelta(minutes=1); continue
            ret=rng.normal(0,0.0002); op=price; cc=price*(1+ret)
            ts.append(cur); dts.append(cur.date())
            o.append(op);h.append(max(op,cc));l.append(min(op,cc));c.append(cc)
            vol.append(abs(rng.normal(100,20))*scale); tc.append(int(abs(rng.normal(50,10))*scale))
            price=cc; cur+=timedelta(minutes=1)
    m1=pl.DataFrame(dict(ts=ts,d=dts,o=o,h=h,l=l,c=c,vol=vol,tc=tc))
    bars, s = analyze(m1)
    # gawanya kwa nusu (siku <100 = scale1, >=100 = scale2)
    split = (dt(2020,1,1) + timedelta(days=100)).date()
    bdays = [t.date() for t in bars["t_end"]]
    n1 = sum(1 for d in bdays if d < split); n2 = sum(1 for d in bdays if d >= split)
    days1 = len({d for d in bdays if d < split}); days2 = len({d for d in bdays if d >= split})
    a1 = n1/max(days1,1); a2 = n2/max(days2,1)                  # adaptive bars/siku kila nusu
    # fixed: daily_vol/fixed_thr
    g = m1.group_by("d").agg(pl.col("vol").sum().alias("dv")).sort("d")
    du = g["d"].to_list(); dv = g["dv"].to_numpy(); fthr = float(np.median(dv))/TARGET_BPD
    fb = dv/fthr
    f1 = float(np.mean([fb[i] for i,d in enumerate(du) if d < split]))
    f2 = float(np.mean([fb[i] for i,d in enumerate(du) if d >= split]))
    print(f"adaptive bars/siku: nusu1={a1:.1f} nusu2={a2:.1f} (lengo {TARGET_BPD}, ratio={a2/a1:.2f})")
    print(f"fixed bars/siku:    nusu1={f1:.1f} nusu2={f2:.1f} (ratio={f2/f1:.2f} ~ scale jump ×2)")
    print(f"n_bars={s['n_bars']} dur_med={s['dur_med']:.0f}min")
    ok = (s["n_bars"] > 100 and a2/a1 < 1.4 and f2/f1 > 1.6 and s["dur_med"] > 0)
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
