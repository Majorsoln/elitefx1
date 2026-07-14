"""
intraday_state_engine.py — C2-0 (MZUNGUKO-2): INTRADAY STATES 15m + 30m (Chief masharti #1).

"HTF-bias -> 15m/30m entries" haiwezekani bila states za 15m/30m — hii ndiyo msingi wa data.
Module MPYA kwa makusudi: HAIGUSI market_state_engine.py (H1/H2/H4/D1 + golden self-test yake
zinabaki byte-identical). Inatumia TENA building blocks zake kwa IMPORT (sio copy):
  cfg, pip, time_col, _atr (Wilder), _deseason (saa-ya-siku trailing, shift(1)),
  _reg3 (LOW/NORMAL/HIGH terciles za trailing, shift(1)), _rank_wide (spread WIDE rank-based).

MCHAKATO: ticks -> 15m base bars (time_bucket INTERVAL 15 MINUTE; o/h/l/c bid, tc=count,
spr=median((ask-bid)/pip)) -> rollup 30m (group_by_dynamic every=30m; o first/h max/l min/c last/
tc sum/spr weighted-by-tc — semantiki ILEILE ya market_state_engine.rollup) -> states kwa kila bar
(SIGNAL-bar decidable, no-lookahead): volatility_state (_reg3 juu ya atr_n), activity_state
(_reg3 juu ya tc_n), spread_state (_rank_wide juu ya spr_n), session (saa ya bar — _sess).

Output (mpangilio ULEULE wa engine -> loaders zote zilizopo zinafanya kazi kupitia state_path):
  data/processed/state/symbol=<SYM>/tf=15m.parquet · tf=30m.parquet
  reports/cycle2_intraday_htf.md (sehemu ya states; htf_context.py inaongeza sehemu yake)

Pairs ZOTE 12 (config; XAUUSD pip=0.01 APPROVED). Hakuna pair iliyopendelewa.
Endesha (PC ya data): python src/research/intraday_state_engine.py [--symbol X]
Self-test (bila data): python src/research/intraday_state_engine.py --self-test
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import polars as pl

from market_state_engine import cfg, pip, time_col, _atr, _reg3, _rank_wide, _posix
from event_quality_report import _sess

REPO_ROOT = Path(__file__).resolve().parents[2]
TFS_INTRA = ["15m", "30m"]
BARS_PER_DAY = {"15m": 96, "30m": 48}
WIN_BARS_INTRA = {tf: n * 252 for tf, n in BARS_PER_DAY.items()}     # ~mwaka 1/TF (kama engine)
MINUTES = {"15m": 15, "30m": 30}
# Deseason window: engine H1 ina SEAS_WIN=60 same-hour samples = SIKU 60 (1 sample/saa/siku).
# Intraday ina samples 4 (15m) / 2 (30m) kwa saa kwa siku -> scale ili baseline ibaki ~siku 60
# za muda halisi (bila hii, baseline ina-adapt ndani ya surge ya wiki chache -> false-NORMAL).
SEAS_WIN_INTRA = {"15m": 60 * 4, "30m": 60 * 2}
SEAS_MIN_INTRA = {"15m": 10 * 4, "30m": 10 * 2}


def _deseason_intra(col, win, minp):
    """Formula ILEILE ya market_state_engine._deseason (metric / trailing-mean ya SAA-ileile,
    shift(1), guard baseline>0) — window parametrized kwa TF ya intraday (muda-sawa na engine)."""
    base = pl.col(col).rolling_mean(window_size=win, min_periods=minp).shift(1).over("hour")
    return pl.when(base > 0).then(pl.col(col) / base).otherwise(None)


def bars_from_ticks(con, src, t, pp, minutes=15) -> pl.DataFrame:
    """15m base bars kutoka ticks — query ILEILE ya h1_from_ticks isipokuwa INTERVAL (reuse ya
    semantiki: bid o/h/l/c, tc=COUNT, spr=median((ask-bid)/pip), guards bid>0/ask>bid)."""
    con.execute("SET TimeZone='UTC'")
    q = f"""
        SELECT time_bucket(INTERVAL {minutes} MINUTE, CAST("{t}" AS TIMESTAMP)) AS ts,
               arg_min(bid,"{t}") AS o, max(bid) AS h, min(bid) AS l, arg_max(bid,"{t}") AS c,
               COUNT(*) AS tc, approx_quantile((ask-bid)/{pp}, 0.5) AS spr
        FROM read_parquet('{src}', union_by_name=>true)
        WHERE bid>0 AND ask>0 AND ask>bid
        GROUP BY 1 ORDER BY 1
    """
    return con.execute(q).pl()


def rollup_30m(df15: pl.DataFrame) -> pl.DataFrame:
    """30m kutoka 15m — aggregation ILEILE ya market_state_engine.rollup (o first, h max, l min,
    c last, tc sum, spr weighted na tc)."""
    return (df15.sort("ts").group_by_dynamic("ts", every="30m").agg(
        pl.col("o").first().alias("o"), pl.col("h").max().alias("h"),
        pl.col("l").min().alias("l"), pl.col("c").last().alias("c"),
        pl.col("tc").sum().alias("tc"),
        ((pl.col("spr") * pl.col("tc")).sum() / pl.col("tc").sum()).alias("spr")))


def state_df_intraday(df: pl.DataFrame, tf: str) -> pl.DataFrame:
    """States za 15m/30m — mchakato ULEULE wa market_state_engine.state_df (atr -> deseason ->
    _reg3/_rank_wide, zote shift(1)/trailing = SIGNAL-bar decidable, no-lookahead) + session col."""
    win = WIN_BARS_INTRA[tf]; minp = max(20, win // 4)
    sw, sm = SEAS_WIN_INTRA[tf], SEAS_MIN_INTRA[tf]
    df = _atr(df.sort("ts")).with_columns(pl.col("ts").dt.hour().alias("hour"))
    df = df.with_columns([_deseason_intra("atr", sw, sm).alias("atr_n"),
                          _deseason_intra("tc", sw, sm).alias("tc_n"),
                          _deseason_intra("spr", sw, sm).alias("spr_n")])
    df = df.with_columns([_reg3("atr_n", win, minp).alias("volatility_state"),
                          _reg3("tc_n", win, minp).alias("activity_state")])
    df = df.with_columns(pl.Series("spread_state", _rank_wide(df["spr_n"].to_numpy())))
    sess = [_sess(int(h)) for h in df["hour"].to_list()]
    return df.with_columns(pl.Series("session", sess, dtype=pl.String))


OUT_COLS = ["ts", "o", "h", "l", "c", "atr", "tc", "spr",
            "volatility_state", "activity_state", "spread_state", "session"]


def _coverage(df: pl.DataFrame):
    """Coverage per year + sanity (spread median, session distribution) kwa report."""
    yr = (df.group_by(pl.col("ts").dt.year().alias("year")).agg(pl.len().alias("bars"))
            .sort("year"))
    sess = (df.group_by("session").agg(pl.len().alias("bars")).sort("session"))
    tot = max(1, len(df))
    return dict(bars=len(df),
                years={int(r["year"]): int(r["bars"]) for r in yr.iter_rows(named=True)},
                spr_med=float(df["spr"].drop_nulls().median() or float("nan")),
                sessions={r["session"]: round(int(r["bars"]) / tot, 3) for r in sess.iter_rows(named=True)})


def run(pairs):
    import duckdb
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
        print(f"  {sym}: nascan 15m...", flush=True)
        b15 = bars_from_ticks(con, src, t, pip(sym), minutes=15)
        for tf, bars in (("15m", b15), ("30m", rollup_30m(b15))):
            df = state_df_intraday(bars, tf)
            out = REPO_ROOT / c["paths"]["processed"] / "state" / f"symbol={sym}" / f"tf={tf}.parquet"
            out.parent.mkdir(parents=True, exist_ok=True)
            df.select(OUT_COLS).write_parquet(out)
            cov = _coverage(df)
            rows.append((sym, tf, cov))
            print(f"    {tf}: bars={cov['bars']:,} spr_med={cov['spr_med']:.2f}")
    if not rows:
        print("HITILAFU: hakuna data.", file=sys.stderr); return 1

    # report (sehemu ya states; htf_context inaongeza yake)
    L = ["# C2-0 — Intraday states (15m/30m) + HTF context (MZUNGUKO-2)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | pairs={len(set(r[0] for r in rows))} | TF: 15m, 30m | "
         "states: vol/activity (_reg3 deseasonalized, trailing ~mwaka 1) + spread (_rank_wide) + "
         "session | NO-LOOKAHEAD (shift(1)/trailing kila mahali — semantiki ya market_state_engine)*\n",
         "## A) Coverage + sanity (states za 15m/30m)\n",
         "| Pair | TF | bars | years (coverage) | spread med (pips) | sessions (ASIA/LON/NY/LATE) |",
         "|------|----|------|------------------|-------------------|------------------------------|"]
    for sym, tf, cov in rows:
        yrs = " ".join(f"{y}:{n // 1000}k" for y, n in cov["years"].items())
        ss = cov["sessions"]
        L.append(f"| {sym} | {tf} | {cov['bars']:,} | {yrs} | {cov['spr_med']:.2f} | "
                 f"{ss.get('ASIA', 0):.2f}/{ss.get('LONDON', 0):.2f}/{ss.get('NY', 0):.2f}/{ss.get('LATE', 0):.2f} |")
    L.append("\n*Sehemu B (HTF context features + uthibitisho wa no-lookahead) inaongezwa na "
             "htf_context.py. Self-test evidence: run_selftests.py (intraday_state_engine + htf_context).*")
    rep = REPO_ROOT / c["paths"]["reports"] / "cycle2_intraday_htf.md"
    rep.parent.mkdir(parents=True, exist_ok=True)
    rep.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {rep.relative_to(REPO_ROOT)}")
    return 0


# ---------------------------------------------------------------- self-test (bila data)
def _synth_15m(n_days=420, seed=0):
    """15m bars synthetic zenye seasonality ya saa + surge (kama self_test ya engine, 15m grid)."""
    from datetime import datetime as dt, timedelta
    rng = np.random.default_rng(seed)
    ts = []; o = []; h = []; l = []; cc = []; tc = []; spr = []
    price = 1.10; cur = dt(2018, 1, 1); N = 96 * n_days
    for k in range(N):
        hour = cur.hour
        seas = 1.0 + 0.8 * np.sin((hour - 3) / 24 * 2 * np.pi)
        surge = 2.0 if 96 * 260 <= k < 96 * 290 else 1.0
        volx = 0.0004 * (1.0 + 0.6 * np.sin((hour - 3) / 24 * 2 * np.pi)) * surge
        ret = rng.normal(0, volx); op = price; c = price * (1 + ret)
        ts.append(cur); o.append(op)
        h.append(max(op, c) * (1 + abs(rng.normal(0, volx / 2))))
        l.append(min(op, c) * (1 - abs(rng.normal(0, volx / 2)))); cc.append(c)
        tc.append(max(1, int(250 * seas * surge + rng.normal(0, 25))))
        spr.append(abs(rng.normal(0.9, 0.1)))
        price = c; cur += timedelta(minutes=15)
    return pl.DataFrame(dict(ts=ts, o=o, h=h, l=l, c=cc, tc=tc, spr=spr))


def self_test():
    ok = True
    df15 = _synth_15m()

    # (a) 30m ROLLUP CORRECTNESS: linganisha na aggregation ya mkono kwenye windows za kwanza
    df30 = rollup_30m(df15)
    ok_pairs = len(df30) * 2 == len(df15)
    manual_ok = True
    for w in range(5):
        a, b = df15[2 * w], df15[2 * w + 1]
        r = df30[w]
        exp_spr = (a["spr"][0] * a["tc"][0] + b["spr"][0] * b["tc"][0]) / (a["tc"][0] + b["tc"][0])
        manual_ok &= (r["o"][0] == a["o"][0] and r["c"][0] == b["c"][0]
                      and r["h"][0] == max(a["h"][0], b["h"][0])
                      and r["l"][0] == min(a["l"][0], b["l"][0])
                      and r["tc"][0] == a["tc"][0] + b["tc"][0]
                      and abs(r["spr"][0] - exp_spr) < 1e-12)
    print(f"  [a] 30m rollup == manual agg (o/h/l/c/tc/spr-weighted): pairs-2to1={ok_pairs} manual={manual_ok}")
    ok = ok and ok_pairs and manual_ok

    # (b) NO-LOOKAHEAD (truncation invariance): states za prefix == prefix ya states za full
    R15 = state_df_intraday(df15, "15m")
    cut = 96 * 300
    R15p = state_df_intraday(df15.head(cut), "15m")
    same = all((R15["volatility_state"].head(cut) == R15p["volatility_state"]).all()
               for _ in [0]) and (R15["activity_state"].head(cut) == R15p["activity_state"]).all()
    print(f"  [b] no-lookahead (truncation invariance ya states): {same}")
    ok = ok and bool(same)

    # (c) deseason + surge (kama golden ya engine): surge ya activity inatambulika kwenye 15m
    surge_high = (R15.slice(96 * 265, 96 * 20)["activity_state"] == "HIGH").mean()
    unk = (R15["activity_state"] == "UNKNOWN").sum()
    print(f"  [c] surge HIGH%={surge_high * 100:.0f}% (>50 lengo) UNKNOWN(warmup)={unk}")
    ok = ok and surge_high > 0.50 and unk > 0

    # (d) session decidability: session ya kila bar = _sess(hour ya bar YAKE) (ratiba, ex-ante)
    hrs = R15["hour"].to_list()[:500]; sess = R15["session"].to_list()[:500]
    sess_ok = all(_sess(int(h)) == s for h, s in zip(hrs, sess))
    dist = R15.group_by("session").agg(pl.len()).sort("session")
    print(f"  [d] session=f(hour ya bar): {sess_ok} (dist: {dict(zip(dist['session'].to_list(), dist['len'].to_list()))})")
    ok = ok and sess_ok

    # (e) 30m states pia zinajengeka + schema kamili (OUT_COLS)
    R30 = state_df_intraday(df30, "30m")
    schema_ok = all(c in R30.columns for c in OUT_COLS)
    print(f"  [e] 30m states schema (OUT_COLS zote): {schema_ok}")
    ok = ok and schema_ok

    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default=None)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    c = cfg()
    return run([a.symbol] if a.symbol else c["pairs"])


if __name__ == "__main__":
    raise SystemExit(main())
