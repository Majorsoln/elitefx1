"""
spread_quality.py — GAP 4: Spread distribution (institutional: spread = data).

Spread ndio gharama halisi ya kuingia/kutoka. Volume Bars + entries/exits zote
zinategemea cost halisi. Hapa tunapima spread (pips) kwa kila pair:

  • median | p95 | p99 | max         (mgawanyo)
  • % ticks > max_spread_pips (config) (frequency ya spread mbaya)
  • rollover/news spread = p95 ya saa 21–23 UTC (rollover spike)
  • median spread kwa mwaka          (spread regime)

pip = 0.01 (JPY) au 0.0001 (nyingine). Inatumia approx_quantile (haraka, 200M+ rows).

Endesha: python src/data/spread_quality.py            (-> reports/spread_quality_report.md)
         python src/data/spread_quality.py --symbol EURUSD
Self-test: python src/data/spread_quality.py --self-test
"""
from __future__ import annotations

import argparse, sys
from datetime import datetime
from pathlib import Path

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


def measure(con, src, t, pp, thr):
    """Rudisha dict ya spread metrics (pips)."""
    con.execute("SET TimeZone='UTC'")
    # CAST AS TIMESTAMP kabla ya EXTRACT(hour) — kuepuka pytz kwenye TIMESTAMPTZ.
    base = f"""
        SELECT (ask-bid)/{pp} AS spr,
               EXTRACT(hour FROM CAST("{t}" AS TIMESTAMP))::INT AS hr,
               EXTRACT(year FROM "{t}")::INT AS yr
        FROM read_parquet('{src}', union_by_name=>true)
        WHERE bid>0 AND ask>0 AND ask>=bid
    """
    q = f"""
        SELECT approx_quantile(spr,0.5), approx_quantile(spr,0.95), approx_quantile(spr,0.99),
               max(spr), avg(spr),
               avg(CASE WHEN spr > {thr} THEN 1.0 ELSE 0.0 END),
               approx_quantile(CASE WHEN hr IN (21,22,23) THEN spr END, 0.95)
        FROM ({base})
    """
    med, p95, p99, mx, avg, pct_over, roll = con.execute(q).fetchone()
    qy = f"SELECT yr, approx_quantile(spr,0.5) FROM ({base}) GROUP BY 1 ORDER BY 1"
    by_year = [(int(y), float(m)) for y, m in con.execute(qy).fetchall()]
    return dict(med=med, p95=p95, p99=p99, mx=mx, avg=avg, pct_over=pct_over,
                roll=roll, by_year=by_year)


def run(pairs, raw_root, out_path, thr_map):
    con = duckdb.connect(); res = {}
    for p in pairs:
        base = raw_root / f"symbol={p}"
        if not base.exists() or not list(base.rglob("*.parquet")):
            print(f"  {p}: (hakuna data)"); res[p] = None; continue
        src = _posix(base / "**" / "*.parquet")
        t = time_col(con, src); thr = thr_map.get(p, 99)
        print(f"  {p}: nascan...", flush=True)
        res[p] = (measure(con, src, t, pip(p), thr), thr)
        print(f"  {p}: done")

    L = ["# Spread Quality Report (GAP 4)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | spread = (ask-bid) pips | approx_quantile | "
         "rollover = p95 saa 21–23 UTC*\n",
         "## Mgawanyo wa spread (pips)\n",
         "| Pair | median | p95 | p99 | max | avg | %>max | rollover p95 | hukumu |",
         "|------|--------|-----|-----|-----|-----|-------|--------------|--------|"]
    for p in pairs:
        r = res.get(p)
        if not r:
            L.append(f"| {p} | — | — | — | — | — | — | — | ⚪ |"); continue
        m, thr = r
        roll = m["roll"] if m["roll"] is not None else float("nan")
        # hukumu: spread isiyo na outliers nyingi, %>max ndogo
        bad = (m["pct_over"] or 0) * 100
        verd = "✅ safi" if bad < 5 else ("⚠️ outliers" if bad < 15 else "❌ spread mbaya")
        L.append(f"| {p} | {m['med']:.2f} | {m['p95']:.2f} | {m['p99']:.2f} | {m['mx']:.1f} | "
                 f"{m['avg']:.2f} | {bad:.1f}% (>{thr}) | {roll:.2f} | {verd} |")

    allyrs = sorted({y for r in res.values() if r for y, _ in r[0]["by_year"]})
    if allyrs:
        L.append("\n## Median spread kwa mwaka (spread regime, pips)\n")
        L.append("| Pair | " + " | ".join(str(y) for y in allyrs) + " |")
        L.append("|------|" + "----|" * len(allyrs))
        for p in pairs:
            r = res.get(p)
            if not r:
                L.append(f"| {p} |" + " — |" * len(allyrs)); continue
            d = dict(r[0]["by_year"])
            L.append(f"| {p} | " + " | ".join(f"{d[y]:.2f}" if y in d else "—" for y in allyrs) + " |")

    L.append("\n---\n*Spread ni gharama halisi — entries/exits & Volume Bars zitumie cost hii (sio "
             "fixed). %>max = frequency ya spread isiyo ya kawaida (config max_spread_pips). rollover "
             "p95 (21–23 UTC) inathibitisha no-trade window. Median/mwaka inaonyesha spread regime.*")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out_path.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    import tempfile
    con = duckdb.connect(); con.execute("SET TimeZone='UTC'")
    d = Path(tempfile.mkdtemp()) / "t.parquet"
    # spread: 0.0001 (1 pip) mara nyingi, + outlier 0.0010 (10 pip) saa 22
    con.execute(f"""
        COPY (SELECT * FROM (VALUES
          (TIMESTAMPTZ '2023-03-01 10:00:00+00', 1.1000, 1.1001),
          (TIMESTAMPTZ '2023-03-01 11:00:00+00', 1.1000, 1.1001),
          (TIMESTAMPTZ '2023-03-01 12:00:00+00', 1.1000, 1.1001),
          (TIMESTAMPTZ '2023-03-01 22:00:00+00', 1.1000, 1.1010)
        ) t(timestamp,bid,ask)) TO '{_posix(d)}' (FORMAT PARQUET)
    """)
    m = measure(con, _posix(d), "timestamp", 0.0001, 5.0)
    print(f"median={m['med']:.2f} p99={m['p99']:.2f} max={m['mx']:.2f} %>5={m['pct_over']*100:.0f}% roll={m['roll']:.2f}")
    ok = abs(m["med"] - 1.0) < 0.5 and m["mx"] >= 9.9 and m["pct_over"] > 0 and m["roll"] is not None
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
    out = Path(a.out) if a.out else REPO_ROOT / c["paths"]["reports"] / "spread_quality_report.md"
    return run(pairs, raw, out, c.get("max_spread_pips", {}))


if __name__ == "__main__":
    raise SystemExit(main())
