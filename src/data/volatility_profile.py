"""
volatility_profile.py — GAP 5: Volatility diagnostics (doctrine ya Dynamic Vol).

Doctrine mpya inategemea volatility ya nguvu (dynamic). Hapa tunapima, kwa pair,
kutoka D1 bars (zilizojengwa kutoka ticks):

  • ATR(14) — pips: median | p95            (range halisi ya kila siku)
  • realized vol (annualized) = std(logret)·√252
  • |daily return| pips: median | p95       (sigma proxy)
  • realized vol KWA MWAKA                   (vol regime: 2020 spike, n.k.)

D1 bucket = UTC day; weekend (Sat/Sun) imeondolewa. pip = 0.01 (JPY) / 0.0001.

Endesha: python src/data/volatility_profile.py            (-> reports/volatility_profile_report.md)
         python src/data/volatility_profile.py --symbol EURUSD
Self-test: python src/data/volatility_profile.py --self-test
"""
from __future__ import annotations

import argparse, sys
from datetime import datetime
from pathlib import Path

import numpy as np
import duckdb, yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config" / "data_config.yaml"


def cfg():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)

def _posix(p): return str(p).replace("\\", "/")
def pip(sym): return 0.01 if "JPY" in sym.upper() else 0.0001

def time_col(con, src):
    sch = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{src}', union_by_name=>true)").fetchall()
    cols = [r[0] for r in sch]
    return next((c for c in cols if any(k in c.lower() for k in ("time","date","ts","stamp"))), None)


def d1_bars(con, src, t):
    con.execute("SET TimeZone='UTC'")
    q = f"""
        SELECT time_bucket(INTERVAL 1 DAY, "{t}") AS d,
               arg_min(bid,"{t}") AS o, max(bid) AS h, min(bid) AS l, arg_max(bid,"{t}") AS c
        FROM read_parquet('{src}', union_by_name=>true)
        WHERE bid>0 AND ask>0 GROUP BY 1 ORDER BY 1
    """
    return con.execute(q).fetchall()


def analyze(bars, pp):
    """bars=[(d,o,h,l,c)] -> ATR/vol metrics (pips). Weekend imeondolewa."""
    b = [r for r in bars if r[0].isoweekday() <= 5 and r[4] and r[4] > 0]
    if len(b) < 30:
        return None
    d = [r[0] for r in b]
    h = np.array([r[2] for r in b]); l = np.array([r[3] for r in b]); c = np.array([r[4] for r in b])
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum.reduce([h - l, np.abs(h - pc), np.abs(l - pc)]) / pp        # pips
    # ATR(14) EMA
    a = 1/14; atr = np.empty_like(tr); atr[0] = tr[0]
    for i in range(1, len(tr)):
        atr[i] = a*tr[i] + (1-a)*atr[i-1]
    atr = atr[14:]                                                              # warmup
    logret = np.diff(np.log(c))
    rvol = float(np.std(logret) * np.sqrt(252))                                 # annualized
    absret_pips = np.abs(np.diff(c)) / pp
    # per year realized vol
    yrs = sorted({x.year for x in d})
    by_year = {}
    for yr in yrs:
        idx = [i for i in range(1, len(c)) if d[i].year == yr]
        if len(idx) > 5:
            lr = np.log(c[idx]) - np.log(c[[i-1 for i in idx]])
            by_year[yr] = float(np.std(lr) * np.sqrt(252))
    return dict(n=len(b),
                atr_med=float(np.median(atr)), atr_p95=float(np.percentile(atr, 95)),
                rvol=rvol,
                ar_med=float(np.median(absret_pips)), ar_p95=float(np.percentile(absret_pips, 95)),
                by_year=by_year)


def run(pairs, raw_root, out_path):
    con = duckdb.connect(); res = {}
    for p in pairs:
        base = raw_root / f"symbol={p}"
        if not base.exists() or not list(base.rglob("*.parquet")):
            print(f"  {p}: (hakuna data)"); res[p] = None; continue
        src = _posix(base / "**" / "*.parquet")
        t = time_col(con, src)
        print(f"  {p}: nascan...", flush=True)
        res[p] = analyze(d1_bars(con, src, t), pip(p))
        print(f"  {p}: done")

    L = ["# Volatility Profile Report (GAP 5)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | D1 bars kutoka ticks | ATR(14) pips | "
         "realized vol annualized = std(logret)·√252*\n",
         "## Mgawanyo wa volatility\n",
         "| Pair | n(siku) | ATR med | ATR p95 | realized vol | \\|ret\\| med (pips) | \\|ret\\| p95 |",
         "|------|---------|---------|---------|--------------|------------------|------------|"]
    for p in pairs:
        m = res.get(p)
        if not m:
            L.append(f"| {p} | — | — | — | — | — | — |"); continue
        L.append(f"| {p} | {m['n']:,} | {m['atr_med']:.0f} | {m['atr_p95']:.0f} | "
                 f"{m['rvol']*100:.1f}% | {m['ar_med']:.0f} | {m['ar_p95']:.0f} |")

    allyrs = sorted({y for m in res.values() if m for y in m["by_year"]})
    if allyrs:
        L.append("\n## Realized vol (annualized %) kwa mwaka — vol regime\n")
        L.append("| Pair | " + " | ".join(str(y) for y in allyrs) + " |")
        L.append("|------|" + "----|" * len(allyrs))
        for p in pairs:
            m = res.get(p)
            if not m:
                L.append(f"| {p} |" + " — |" * len(allyrs)); continue
            L.append(f"| {p} | " + " | ".join(f"{m['by_year'][y]*100:.0f}" if y in m["by_year"] else "—"
                                              for y in allyrs) + " |")

    L.append("\n---\n*ATR(14) = range ya kila siku (pips) — msingi wa SL/TP dynamic na threshold ya "
             "Volume Bars. realized vol/mwaka inaonyesha vol regime (k.m. 2020 COVID spike). Dynamic "
             "vol doctrine itumie ATR/realized-vol hizi, sio fixed pips.*")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out_path.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """Planted: random-walk D1 yenye vol inayojulikana -> ATR>0, rvol katika range mantiki."""
    rng = np.random.default_rng(0)
    from datetime import date, timedelta
    bars = []; price = 1.10; d0 = date(2022, 1, 3)
    i = 0; made = 0
    while made < 400:
        day = d0 + timedelta(days=i); i += 1
        if day.isoweekday() > 5:
            continue
        ret = rng.normal(0, 0.005)                 # ~0.5% daily
        o = price; c = price * (1 + ret)
        h = max(o, c) * (1 + abs(rng.normal(0, 0.002)))
        l = min(o, c) * (1 - abs(rng.normal(0, 0.002)))
        from datetime import datetime as _dt
        bars.append((_dt(day.year, day.month, day.day), o, h, l, c))
        price = c; made += 1
    m = analyze(bars, 0.0001)
    print(f"n={m['n']} ATR_med={m['atr_med']:.0f}pips rvol={m['rvol']*100:.1f}% |ret|med={m['ar_med']:.0f}")
    ok = (m["atr_med"] > 0 and 3 < m["rvol"]*100 < 20 and m["ar_med"] > 0)   # ~0.5%/siku -> ~8% ann
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default=None); ap.add_argument("--out", default=None)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    c = cfg(); raw = REPO_ROOT / c["paths"]["raw_ticks"]
    if not raw.exists():
        print(f"HITILAFU: '{raw}' haipo.", file=sys.stderr); return 1
    pairs = [a.symbol] if a.symbol else c["pairs"]
    out = Path(a.out) if a.out else REPO_ROOT / c["paths"]["reports"] / "volatility_profile_report.md"
    return run(pairs, raw, out)


if __name__ == "__main__":
    raise SystemExit(main())
