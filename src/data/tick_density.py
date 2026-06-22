"""
tick_density.py — GAP 1: Coverage ≠ Quality. Mgawanyo wa tick density.

Coverage 100% haimaanishi ubora sawa kila siku. Siku moja yaweza kuwa ticks 500,
nyingine 300,000 — bado "100% coverage". Volume Bars ni nyeti kwa hili: siku
zenye density ndogo zinatoa bars chache/zilizopotoka. Hapa tunapima:

  • ticks/siku (weekday) — quantiles: min p1 p5 p25 med p75 p95 p99 max
  • THIN days: weekday zenye ticks < 10% ya median (holiday/half-day/feed gap)
  • profile ya saa (UTC) — peak vs trough (session structure)
  • median ticks/siku KWA MWAKA (kuunganisha na tick_regime)

> Tick volume = PROXY (Dukascopy tick/quote volume, sio exchange volume — FX ni OTC).

Endesha: python src/data/tick_density.py            (pairs zote -> reports/tick_density_report.md)
         python src/data/tick_density.py --symbol EURUSD
Self-test: python src/data/tick_density.py --self-test
"""
from __future__ import annotations

import argparse, sys
from datetime import datetime
from pathlib import Path

import numpy as np
import duckdb, yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config" / "data_config.yaml"
THIN_FRAC = 0.10        # weekday < 10% ya median = "thin"


def cfg():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)

def _posix(p): return str(p).replace("\\", "/")

def time_col(con, src):
    sch = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{src}', union_by_name=>true)").fetchall()
    cols = [r[0] for r in sch]
    return next((c for c in cols if any(k in c.lower() for k in ("time","date","ts","stamp"))), None)


def per_day(con, src, tc):
    con.execute("SET TimeZone='UTC'")
    q = f"""
        SELECT CAST("{tc}" AS DATE) AS d,
               EXTRACT(year FROM "{tc}")::INT AS yr,
               isodow("{tc}") AS dow,
               COUNT(*) AS ticks
        FROM read_parquet('{src}', union_by_name=>true)
        WHERE bid>0 AND ask>0 GROUP BY 1,2,3 ORDER BY 1
    """
    return con.execute(q).fetchall()

def per_hour(con, src, tc):
    con.execute("SET TimeZone='UTC'")
    q = f"""
        SELECT EXTRACT(hour FROM "{tc}")::INT AS h, COUNT(*) AS ticks,
               COUNT(DISTINCT CAST("{tc}" AS DATE)) AS days
        FROM read_parquet('{src}', union_by_name=>true)
        WHERE bid>0 AND ask>0 GROUP BY 1 ORDER BY 1
    """
    return con.execute(q).fetchall()


def analyze(rows_day, rows_hour):
    """Rudisha metrics dict kutoka per-day + per-hour rows."""
    wd = np.array([t for _, _, dow, t in rows_day if dow <= 5], float)   # Mon-Fri
    if len(wd) < 10:
        return None
    qs = np.percentile(wd, [0,1,5,25,50,75,95,99,100])
    med = qs[4]
    thin = int((wd < THIN_FRAC * med).sum())
    # per year median
    yrs = sorted({yr for _, yr, _, _ in rows_day})
    by_year = {}
    for yr in yrs:
        v = [t for _, y, dow, t in rows_day if y == yr and dow <= 5]
        by_year[yr] = float(np.median(v)) if v else 0.0
    # hour profile
    hr = {h: (ticks / days if days else 0) for h, ticks, days in rows_hour}
    if hr:
        peak_h = max(hr, key=hr.get); trough_h = min(hr, key=hr.get)
        ratio = hr[peak_h] / hr[trough_h] if hr[trough_h] else float("inf")
    else:
        peak_h = trough_h = ratio = None
    return dict(n_wd=len(wd), q=qs, med=med, thin=thin, by_year=by_year,
                hr=hr, peak_h=peak_h, trough_h=trough_h, ratio=ratio)


def fmt(x): return f"{int(x):,}" if x == x else "—"

def run(pairs, raw_root, out_path):
    con = duckdb.connect()
    res = {}
    for p in pairs:
        base = raw_root / f"symbol={p}"
        if not base.exists() or not list(base.rglob("*.parquet")):
            print(f"  {p}: (hakuna data)"); res[p] = None; continue
        src = _posix(base / "**" / "*.parquet")
        tc = time_col(con, src)
        print(f"  {p}: nascan...", flush=True)
        res[p] = analyze(per_day(con, src, tc), per_hour(con, src, tc))
        print(f"  {p}: done")

    L = ["# Tick Density Report (GAP 1 — Coverage ≠ Quality)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | ticks/siku (weekday) | THIN = <{THIN_FRAC*100:.0f}% ya median | "
         "tick volume = PROXY (Dukascopy, sio exchange volume)*\n",
         "## Mgawanyo wa ticks/siku (weekday)\n",
         "| Pair | min | p1 | p5 | p25 | median | p75 | p95 | p99 | max | THIN days |",
         "|------|-----|----|----|----|--------|-----|-----|-----|-----|-----------|"]
    for p in pairs:
        m = res.get(p)
        if not m:
            L.append(f"| {p} | — | — | — | — | — | — | — | — | — | — |"); continue
        q = m["q"]
        L.append(f"| {p} | " + " | ".join(fmt(x) for x in q) + f" | {m['thin']} |")

    L.append("\n## Profile ya saa (UTC) — session structure\n")
    L.append("| Pair | peak hr | trough hr | peak/trough | tafsiri |")
    L.append("|------|---------|-----------|-------------|---------|")
    for p in pairs:
        m = res.get(p)
        if not m or m["peak_h"] is None:
            L.append(f"| {p} | — | — | — | — |"); continue
        tafsiri = "U-shape (session halisi)" if m["ratio"] and m["ratio"] > 2 else "flat (shaka)"
        L.append(f"| {p} | {m['peak_h']:02d}:00 | {m['trough_h']:02d}:00 | {m['ratio']:.1f}× | {tafsiri} |")

    L.append("\n## Median ticks/siku kwa mwaka (regime ya density)\n")
    allyrs = sorted({y for m in res.values() if m for y in m["by_year"]})
    if allyrs:
        L.append("| Pair | " + " | ".join(str(y) for y in allyrs) + " |")
        L.append("|------|" + "----|" * len(allyrs))
        for p in pairs:
            m = res.get(p)
            if not m:
                L.append(f"| {p} |" + " — |" * len(allyrs)); continue
            L.append(f"| {p} | " + " | ".join(fmt(m["by_year"].get(y, float('nan'))) for y in allyrs) + " |")

    L.append("\n---\n*THIN days = weekday zenye liquidity ndogo (holidays/half-days/feed gaps) — "
             "Volume Bars zizifikirie. peak/trough >2× = session U-shape halisi (London/NY). "
             "Median/mwaka inaonyesha kama density imeshuka kwa miaka (-> tick_regime).*")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out_path.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    # planted: weekday med ~1000, siku 1 thin (~50), U-shape ya saa
    rng = np.random.default_rng(0)
    rows_day = []
    for i in range(60):
        dow = (i % 7) + 1
        if dow > 5:   # weekend chache
            continue
        t = 50 if i == 10 else int(rng.normal(1000, 50))
        rows_day.append((f"2023-01-{i+1:02d}", 2023, dow, t))
    rows_hour = [(h, (5000 if 12 <= h <= 16 else 500) * 100, 100) for h in range(24)]
    m = analyze(rows_day, rows_hour)
    print(f"median={m['med']:.0f} thin={m['thin']} peak={m['peak_h']} trough={m['trough_h']} ratio={m['ratio']:.1f}")
    ok = (m["thin"] == 1 and 12 <= m["peak_h"] <= 16 and m["ratio"] > 2)
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
    out = Path(a.out) if a.out else REPO_ROOT / c["paths"]["reports"] / "tick_density_report.md"
    return run(pairs, raw, out)


if __name__ == "__main__":
    raise SystemExit(main())
