"""
market_state_engine.py — PHASE 1 (CQ-003). MARKET STATE ENGINE v1.

⚠️ Hii ni MARKET STATE LAYER v1 (building blocks) — SIO "regime engine" ya mwisho.
Regime za kweli (Compression/Expansion/Transition/Shock/Recovery) zinajengwa juu ya
hizi + transitions (zinakuja baada ya volume_bars). Hapa tunatoa STATE LABELS za kila
bar, kwa kila TF muhimu:

  • volatility_state : LOW | NORMAL | HIGH   (ATR(14))
  • activity_state   : LOW | NORMAL | HIGH   (tick_count)
  • spread_state     : NORMAL | WIDE          (median spread)

MANTIKI (sio assumption za matokeo ya zamani):
  1. DESEASONALIZE: kila metric ÷ wastani wa SAA-ileile ya siku (trailing, no-lookahead)
     -> "HIGH" = juu ya kawaida ya SAA hiyo, sio tu "ni mchana".
  2. vol/activity: TERCILES za rolling (past tu, ~mwaka 1/TF) -> LOW/NORMAL/HIGH.
     spread: RANK-based (top WIDE_Q ndani ya trailing window) — TIE/AGGREGATION-ROBUST
     (value-threshold ilikuwa inaweza kuvuruga kwa discrete spread; rank ni invariant).
  3. ABSOLUTE distributions (median ATR/spread/ticks) zinaonyeshwa pia -> pair individuality
     (terciles peke yake huficha tofauti EURGBP vs GBPJPY).

Pairs ZOTE (config) × TF [H1, H2, H4, D1]. Hakuna pair/TF iliyopendelewa.

Output:
  reports/market_state_report.md
  data/processed/state/symbol=<P>/tf=<TF>.parquet      (downstream; gitignored)

Endesha: python src/research/market_state_engine.py                 (zote)
         python src/research/market_state_engine.py --symbol EURGBP
         python src/research/market_state_engine.py --tf D1
Self-test: python src/research/market_state_engine.py --self-test
"""
from __future__ import annotations

import argparse, sys, warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import polars as pl
import duckdb, yaml

warnings.filterwarnings("ignore", message=".*min_periods.*")

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config" / "data_config.yaml"

TFS = ["H1", "H2", "H4", "D1"]
WIN_BARS = {"H1": 24 * 252, "H2": 12 * 252, "H4": 6 * 252, "D1": 252}   # ~mwaka 1/TF (vol/activity)
SEAS_WIN = 60          # trailing same-hour samples (deseasonalization)
SEAS_MIN = 10
SPREAD_WIN = 750       # trailing window kwa spread RANK (TF-invariant)
SPREAD_MIN = 150
LO_Q, HI_Q, WIDE_Q = 0.33, 0.67, 0.85
EVERY = {"H2": "2h", "H4": "4h", "D1": "1d"}


def cfg():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)

def _posix(p): return str(p).replace("\\", "/")
def pip(sym): return 0.01 if "JPY" in sym.upper() else 0.0001

def time_col(con, src):
    sch = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{src}', union_by_name=>true)").fetchall()
    cols = [r[0] for r in sch]
    return next((c for c in cols if any(k in c.lower() for k in ("time","date","ts","stamp"))), None)


def h1_from_ticks(con, src, t, pp) -> pl.DataFrame:
    """H1 bars kutoka ticks. CAST AS TIMESTAMP (naive) -> time_bucket bila pytz.
    spread = median (ask-bid) pips; spread>0 tu (kuepuka zero/inf kwenye deseason)."""
    con.execute("SET TimeZone='UTC'")
    q = f"""
        SELECT time_bucket(INTERVAL 1 HOUR, CAST("{t}" AS TIMESTAMP)) AS ts,
               arg_min(bid,"{t}") AS o, max(bid) AS h, min(bid) AS l, arg_max(bid,"{t}") AS c,
               COUNT(*) AS tc, approx_quantile((ask-bid)/{pp}, 0.5) AS spr
        FROM read_parquet('{src}', union_by_name=>true)
        WHERE bid>0 AND ask>0 AND ask>bid
        GROUP BY 1 ORDER BY 1
    """
    return con.execute(q).pl()


def rollup(df: pl.DataFrame, tf: str) -> pl.DataFrame:
    if tf == "H1":
        return df.sort("ts")
    return (df.sort("ts").group_by_dynamic("ts", every=EVERY[tf]).agg(
        pl.col("o").first().alias("o"), pl.col("h").max().alias("h"),
        pl.col("l").min().alias("l"), pl.col("c").last().alias("c"),
        pl.col("tc").sum().alias("tc"),
        ((pl.col("spr") * pl.col("tc")).sum() / pl.col("tc").sum()).alias("spr")))


def _atr(df: pl.DataFrame, n=14) -> pl.DataFrame:
    h = df["h"].to_numpy(); l = df["l"].to_numpy(); c = df["c"].to_numpy()
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum.reduce([h - l, np.abs(h - pc), np.abs(l - pc)])
    a = 1/n; atr = np.empty_like(tr); atr[0] = tr[0]
    for i in range(1, len(tr)):
        atr[i] = a*tr[i] + (1-a)*atr[i-1]
    return df.with_columns(pl.Series("atr", atr))


def _deseason(col):
    """metric / trailing-mean ya SAA-ileile (no-lookahead). Guard dhidi ya baseline≈0."""
    base = pl.col(col).rolling_mean(window_size=SEAS_WIN, min_periods=SEAS_MIN).shift(1).over("hour")
    return pl.when(base > 0).then(pl.col(col) / base).otherwise(None)


def _reg3(name, win, minp):
    c = pl.col(name)
    lo = c.rolling_quantile(quantile=LO_Q, window_size=win, min_periods=minp).shift(1)
    hi = c.rolling_quantile(quantile=HI_Q, window_size=win, min_periods=minp).shift(1)
    return (pl.when(lo.is_null() | c.is_null() | c.is_nan()).then(pl.lit("UNKNOWN"))
              .when(c < lo).then(pl.lit("LOW"))
              .when(c > hi).then(pl.lit("HIGH"))
              .otherwise(pl.lit("NORMAL")))


def _rank_wide(x, win=SPREAD_WIN, minp=SPREAD_MIN, q=WIDE_Q):
    """WIDE kama rank ya x[i] ndani ya trailing window > q. Tie/aggregation-robust,
    TF-invariant (~ (1-q) WIDE by construction). No-lookahead (past tu)."""
    n = len(x); out = np.array(["UNKNOWN"] * n, dtype=object)
    for i in range(n):
        if not np.isfinite(x[i]):
            continue
        s = x[max(0, i-win):i]
        s = s[np.isfinite(s)]
        if len(s) < minp:
            continue
        out[i] = "WIDE" if (s < x[i]).mean() > q else "NORMAL"
    return out


def state_df(df: pl.DataFrame, tf: str) -> pl.DataFrame:
    win = WIN_BARS[tf]; minp = max(20, win // 4)
    df = _atr(df.sort("ts")).with_columns(pl.col("ts").dt.hour().alias("hour"))
    df = df.with_columns([_deseason("atr").alias("atr_n"),
                          _deseason("tc").alias("tc_n"),
                          _deseason("spr").alias("spr_n")])
    df = df.with_columns([_reg3("atr_n", win, minp).alias("volatility_state"),
                          _reg3("tc_n", win, minp).alias("activity_state")])
    return df.with_columns(pl.Series("spread_state", _rank_wide(df["spr_n"].to_numpy())))


# ───────────── muhtasari ─────────────
def _dist(s: pl.Series, levels):
    known = s.filter(s != "UNKNOWN")
    n = len(known) or 1
    vc = (dict(zip(known.value_counts().to_series(0).to_list(),
                   known.value_counts().to_series(1).to_list())) if len(known) else {})
    return {lv: vc.get(lv, 0)/n for lv in levels}, len(known)

def _persist(s: pl.Series):
    runs = []; cur = None; ln = 0
    for x in s.to_list():
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

def _med(df, col):
    a = df[col].drop_nulls().drop_nans().to_numpy()
    return float(np.median(a)) if len(a) else float("nan")


def summarize(df, sym, tf, pp):
    vd, vn = _dist(df["volatility_state"], ["LOW","NORMAL","HIGH"])
    ad, _ = _dist(df["activity_state"], ["LOW","NORMAL","HIGH"])
    sd, _ = _dist(df["spread_state"], ["NORMAL","WIDE"])
    return dict(sym=sym, tf=tf, n=vn, vol=vd, act=ad, spr=sd,
                pv=_persist(df["volatility_state"]), pa=_persist(df["activity_state"]),
                ps=_persist(df["spread_state"]),
                atr_pips=_med(df, "atr")/pp, spr_pips=_med(df, "spr"), tc_med=_med(df, "tc"))


def write_report(rows, out_path):
    L = [f"# Market State Engine v1 — pairs ZOTE × TF ZOTE (PHASE 1, CQ-003)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | TF: {', '.join(TFS)} | DESEASONALIZED (saa-ya-siku, "
         f"trailing {SEAS_WIN}) | vol/activity terciles {LO_Q}/{HI_Q} (~mwaka 1/TF) | spread RANK top "
         f"{int((1-WIDE_Q)*100)}% (trailing {SPREAD_WIN}) | no-lookahead*\n",
         "> ⚠️ **STATE LAYER v1 (building blocks) — SIO regime engine ya mwisho.** States ni "
         "vipengele; regime za kweli (Compression/Expansion/Transition/Shock) + transitions "
         "zinajengwa baadaye. Labels RELATIVE kwa mwaka uliopita (no-lookahead).\n",
         "## A) State distribution (% ya bars) + persistence (run length)\n",
         "| Pair | TF | n | vol L/N/H | act L/N/H | spr WIDE | persist v/a/s |",
         "|------|----|---|-----------|-----------|----------|---------------|"]
    for r in rows:
        v = r["vol"]; a = r["act"]; s = r["spr"]
        L.append(f"| {r['sym']} | {r['tf']} | {r['n']:,} | "
                 f"{v['LOW']*100:.0f}/{v['NORMAL']*100:.0f}/{v['HIGH']*100:.0f} | "
                 f"{a['LOW']*100:.0f}/{a['NORMAL']*100:.0f}/{a['HIGH']*100:.0f} | "
                 f"{s['WIDE']*100:.0f}% | {r['pv']:.0f}/{r['pa']:.0f}/{r['ps']:.0f} |")
    L += ["\n## B) ABSOLUTE distributions (pair individuality — GAP 3)\n",
          "*Terciles huzalisha ~33/33/33 kila pair; hapa ndipo tofauti HALISI za pair zinaonekana.*\n",
          "| Pair | TF | median ATR (pips) | median spread (pips) | median ticks/bar |",
          "|------|----|-------------------|----------------------|------------------|"]
    for r in rows:
        L.append(f"| {r['sym']} | {r['tf']} | {r['atr_pips']:.1f} | {r['spr_pips']:.2f} | {r['tc_med']:,.0f} |")
    L.append("\n---\n*STATE v1: deseasonalized (saa) -> states za HALI YA SOKO sio saa. vol/activity = "
             "rolling terciles (relative, no-lookahead). spread = RANK-based (tie/aggregation-robust, "
             "TF-invariant — inarekebisha GAP 2). Absolute median (pips) = pair individuality (GAP 3). "
             "Inayofuata: volume_bars -> regime_transition_report. Metric rasmi = Expected Value (CQ-008).*")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(L), encoding="utf-8")


def run(pairs, tfs):
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
        print(f"  {sym}: nascan H1...", flush=True)
        h1 = h1_from_ticks(con, src, t, pip(sym))
        for tf in tfs:
            df = state_df(rollup(h1, tf), tf)
            rows.append(summarize(df, sym, tf, pip(sym)))
            out = REPO_ROOT / c["paths"]["processed"] / "state" / f"symbol={sym}" / f"tf={tf}.parquet"
            out.parent.mkdir(parents=True, exist_ok=True)
            df.select(["ts","atr","tc","spr","volatility_state","activity_state","spread_state"]).write_parquet(out)
            print(f"    {tf}: bars={len(df)}")
    if not rows:
        print("HITILAFU: hakuna data.", file=sys.stderr); return 1
    rep = REPO_ROOT / c["paths"]["reports"] / "market_state_report.md"
    write_report(rows, rep)
    print(f"\nRipoti: {rep.relative_to(REPO_ROOT)} ({len(rows)} pair×TF)")
    return 0


def self_test():
    """H1 synthetic: (1) deseasonalize inaondoa false-HIGH ya seasonality,
       (2) surge halisi inatambulika, (3) no-lookahead, (4) spread RANK ni
       TF-invariant + robust (~15% WIDE hata kwenye degenerate/discrete)."""
    from datetime import datetime as dt, timedelta
    rng = np.random.default_rng(0)
    ts=[];o=[];h=[];l=[];cc=[];tc=[];spr=[]
    price=1.10; cur=dt(2018,1,1); N=24*400
    for k in range(N):
        hour=cur.hour
        seas=1.0+0.8*np.sin((hour-3)/24*2*np.pi)
        surge=2.0 if 24*250<=k<24*280 else 1.0
        volx=0.001*(1.0+0.6*np.sin((hour-3)/24*2*np.pi))*surge
        ret=rng.normal(0,volx); op=price; c=price*(1+ret)
        ts.append(cur);o.append(op);h.append(max(op,c)*(1+abs(rng.normal(0,volx/2))))
        l.append(min(op,c)*(1-abs(rng.normal(0,volx/2)))); cc.append(c)
        tc.append(max(1,int(1000*seas*surge+rng.normal(0,80)))); spr.append(abs(rng.normal(0.9,0.1)))
        price=c; cur+=timedelta(hours=1)
    df=pl.DataFrame(dict(ts=ts,o=o,h=h,l=l,c=cc,tc=tc,spr=spr))
    R=state_df(df,"H1"); win=WIN_BARS["H1"]; minp=max(20,win//4)
    Rraw=(df.sort("ts").with_columns(pl.col("ts").dt.hour().alias("hour"))
            .with_columns(_reg3("tc",win,minp).alias("act_raw")))
    def hr_std(frame,col):
        f=frame.slice(24*100,24*140).filter(pl.col(col)!="UNKNOWN")
        g=(f.with_columns((pl.col(col)=="HIGH").cast(pl.Float64).alias("hi"))
             .group_by(pl.col("ts").dt.hour()).agg(pl.col("hi").mean()))
        return float(np.std(g["hi"].to_numpy()))
    std_raw=hr_std(Rraw,"act_raw"); std_des=hr_std(R,"activity_state")
    unk=(R["activity_state"]=="UNKNOWN").sum()
    surge_high=(R.slice(24*255,24*20)["activity_state"]=="HIGH").mean()
    # spread RANK robustness: degenerate point-mass + discrete -> bado ~ (1-WIDE_Q)
    deg=np.where(rng.random(5000)<0.7, 1.0, rng.uniform(1.0,3.0,5000))   # 70% tie kwenye 1.0
    w=_rank_wide(deg); frac=np.mean([x=="WIDE" for x in w if x!="UNKNOWN"])
    print(f"UNKNOWN={unk} | HIGH-rate std/hr raw={std_raw:.3f}->des={std_des:.3f} | surge HIGH%={surge_high*100:.0f}%")
    print(f"spread RANK on degenerate(70% tie): WIDE%={frac*100:.0f}% (lengo ~{int((1-WIDE_Q)*100)}%)")
    ok=(unk>0 and std_des<std_raw*0.6 and surge_high>0.50 and 0.05<frac<0.25)
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
