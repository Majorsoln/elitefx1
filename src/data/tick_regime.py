"""
tick_regime.py — GAP 2: Broker / feed structural break.

data_report ilionyesha EURUSD 2016≈44M ticks lakini 2021≈16M. Tofauti hii
kubwa yaweza kutoka: broker change, feed change, au storage/dedup change. Ni
MUHIMU kwa Volume Bars (threshold ya volume haiwezi kuwa fixed kama scale ya
tick imebadilika kwa miaka).

Tunapima KWA MWAKA, kwa pair:
  • ticks/mwaka
  • volume/mwaka (Σ bid_vol+ask_vol)  [tick volume = PROXY]
  • vol-per-tick/mwaka  → kutofautisha "ticks zimepungua" vs "unit imebadilika"
  • YoY ratio ya ticks → FLAG break kama ratio < 0.67 au > 1.5

Endesha: python src/data/tick_regime.py            (-> reports/tick_regime_report.md)
         python src/data/tick_regime.py --symbol EURUSD
Self-test: python src/data/tick_regime.py --self-test
"""
from __future__ import annotations

import argparse, sys
from datetime import datetime
from pathlib import Path

import numpy as np
import duckdb, yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config" / "data_config.yaml"
BREAK_LO, BREAK_HI = 0.67, 1.5      # YoY ratio nje ya hapa = structural break


def cfg():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)

def _posix(p): return str(p).replace("\\", "/")

def detect(con, src):
    sch = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{src}', union_by_name=>true)").fetchall()
    cols = [r[0] for r in sch]
    t = next((c for c in cols if any(k in c.lower() for k in ("time","date","ts","stamp"))), None)
    v = [c for c in cols if "vol" in c.lower() and "imbalance" not in c.lower()]
    return t, v


def per_year(con, src, t, vcols):
    con.execute("SET TimeZone='UTC'")
    vol = " + ".join(f'COALESCE("{c}",0)' for c in vcols) if vcols else "0"
    q = f"""
        SELECT EXTRACT(year FROM "{t}")::INT AS yr, COUNT(*) AS ticks, SUM({vol}) AS vol
        FROM read_parquet('{src}', union_by_name=>true)
        WHERE bid>0 AND ask>0 GROUP BY 1 ORDER BY 1
    """
    return [(int(yr), int(tk), float(v)) for yr, tk, v in con.execute(q).fetchall()]


def analyze(rows):
    """rows=[(yr,ticks,vol)] -> metrics + breaks."""
    if len(rows) < 2:
        return None
    yrs = [r[0] for r in rows]; ticks = [r[1] for r in rows]; vol = [r[2] for r in rows]
    vpt = [vol[i] / ticks[i] if ticks[i] else 0 for i in range(len(rows))]
    breaks = []
    for i in range(1, len(rows)):
        prev = ticks[i-1]
        ratio = ticks[i] / prev if prev else float("inf")
        if ratio < BREAK_LO or ratio > BREAK_HI:
            breaks.append((yrs[i], ratio))
    # scale ya jumla
    full = [t for t in ticks if t > 0]
    span = (max(full) / min(full)) if full else 1.0
    return dict(yrs=yrs, ticks=ticks, vol=vol, vpt=vpt, breaks=breaks, span=span)


def run(pairs, raw_root, out_path):
    con = duckdb.connect(); res = {}
    for p in pairs:
        base = raw_root / f"symbol={p}"
        if not base.exists() or not list(base.rglob("*.parquet")):
            print(f"  {p}: (hakuna data)"); res[p] = None; continue
        src = _posix(base / "**" / "*.parquet")
        t, v = detect(con, src)
        print(f"  {p}: nascan...", flush=True)
        res[p] = analyze(per_year(con, src, t, v))
        print(f"  {p}: done")

    L = ["# Tick Regime Report (GAP 2 — Structural Break)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | ticks & volume kwa mwaka | break = YoY ratio "
         f"<{BREAK_LO} au >{BREAK_HI} | tick volume = PROXY*\n",
         "> Kama scale ya tick imebadilika kwa miaka, **Volume Bars haziwezi kutumia threshold "
         "fixed** — lazima i-normalize kwa regime (au tumia rolling median ya volume).\n",
         "## Muhtasari\n",
         "| Pair | miaka | tick span (max/min) | breaks (YoY) | hukumu |",
         "|------|-------|---------------------|--------------|--------|"]
    for p in pairs:
        m = res.get(p)
        if not m:
            L.append(f"| {p} | — | — | — | ⚪ |"); continue
        bs = ", ".join(f"{y}({r:.2f}×)" for y, r in m["breaks"]) or "—"
        verd = "❌ REGIME SHIFT" if m["breaks"] else ("⚠️ scale pana" if m["span"] > 2 else "✅ stable")
        L.append(f"| {p} | {len(m['yrs'])} | {m['span']:.1f}× | {bs} | {verd} |")

    # per-pair detail
    allyrs = sorted({y for m in res.values() if m for y in m["yrs"]})
    if allyrs:
        L.append("\n## ticks/mwaka (millions)\n")
        L.append("| Pair | " + " | ".join(str(y) for y in allyrs) + " |")
        L.append("|------|" + "----|" * len(allyrs))
        for p in pairs:
            m = res.get(p)
            if not m:
                L.append(f"| {p} |" + " — |" * len(allyrs)); continue
            d = {y: t for y, t in zip(m["yrs"], m["ticks"])}
            L.append(f"| {p} | " + " | ".join(f"{d[y]/1e6:.1f}" if y in d else "—" for y in allyrs) + " |")
        L.append("\n## vol-per-tick/mwaka (kutofautisha count-drop vs unit-change)\n")
        L.append("| Pair | " + " | ".join(str(y) for y in allyrs) + " |")
        L.append("|------|" + "----|" * len(allyrs))
        for p in pairs:
            m = res.get(p)
            if not m:
                L.append(f"| {p} |" + " — |" * len(allyrs)); continue
            d = {y: v for y, v in zip(m["yrs"], m["vpt"])}
            L.append(f"| {p} | " + " | ".join(f"{d[y]:.2f}" if y in d else "—" for y in allyrs) + " |")

    L.append("\n---\n*tick span >2× au YoY break = scale imebadilika (broker/feed/dedup). Kama "
             "vol-per-tick imekaa imara lakini ticks zimeshuka -> ni dedup/feed compression (volume "
             "halisi i sawa). Volume Bars zinormalize kwa regime. Hii ni lazima kabla ya volume_bars.py.*")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out_path.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    # planted: ticks zinashuka kwa kasi 2016->2017 (break), vol-per-tick imara
    rows = [(2016, 44_000_000, 88_000_000.0),
            (2017, 16_000_000, 32_000_000.0),   # ratio 0.36 -> break
            (2018, 17_000_000, 34_000_000.0),
            (2019, 16_500_000, 33_000_000.0)]
    m = analyze(rows)
    print(f"span={m['span']:.1f}× breaks={m['breaks']} vpt={[round(x,2) for x in m['vpt']]}")
    ok = (len(m["breaks"]) == 1 and m["breaks"][0][0] == 2017 and abs(m["vpt"][0] - 2.0) < 1e-6)
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
    out = Path(a.out) if a.out else REPO_ROOT / c["paths"]["reports"] / "tick_regime_report.md"
    return run(pairs, raw, out)


if __name__ == "__main__":
    raise SystemExit(main())
