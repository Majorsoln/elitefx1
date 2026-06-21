"""
data_report.py — Ripoti kamili ya data ZOTE zinazopatikana + ukaguzi wa QUALITY.

Inascan raw ticks (Hive: symbol=*/year=*/.../*.parquet) kwa DuckDB, pair kwa pair,
kwa pass MOJA kila pair (aggregation; hakuna sort), na inatoa:

  1. MUHTASARI kwa pair: tarehe (from→to), miaka, jumla ya ticks, siku za biashara,
     ticks/siku, % zenye volume.
  2. KWA-MWAKA kwa pair: ticks, weekdays present, coverage%, %vol, bad-price, Sat-ticks.
  3. QUALITY verdict kwa pair: PASS / WARN / FAIL kutoka nambari (sio template).

Quality checks (raw-level):
  • bad price:  bid≤0 au ask≤0 au ask<bid           (lazima ≈ 0%)
  • neg spread: ask<bid                              (lazima 0)
  • coverage:   weekdays_present / weekdays_expected ≥ min_year_coverage (config)
  • volume:     % ticks zenye bid_vol+ask_vol > 0
  • Sat ticks:  ticks za Jumamosi (UTC)             (lazima ≈ 0 — soko limefungwa)

Endesha (PC ya Japhet, root ya repo):
  python src/data/data_report.py                 # pairs zote (config) -> reports/data_report.md
  python src/data/data_report.py --symbol EURUSD # pair moja
Self-test (popote, bila data):
  python src/data/data_report.py --self-test
"""
from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

import duckdb
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config" / "data_config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _posix(p: Path) -> str:
    return str(p).replace("\\", "/")


def weekdays_between(d0: date, d1: date) -> int:
    """Idadi ya Mon–Fri kati ya d0 na d1 (inclusive)."""
    if d1 < d0:
        return 0
    days = (d1 - d0).days + 1
    full, rem = divmod(days, 7)
    wd = full * 5
    start = d0.weekday()                 # Mon=0 … Sun=6
    for i in range(rem):
        if (start + i) % 7 < 5:
            wd += 1
    return wd


def detect_volcols(con, src):
    schema = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{src}', union_by_name => true)").fetchall()
    cols = [r[0] for r in schema]
    time_col = next((c for c in cols if any(k in c.lower() for k in ("time", "date", "ts", "stamp"))), None)
    vol_cols = [c for c in cols if "vol" in c.lower() and "imbalance" not in c.lower()]
    return time_col, vol_cols


def analyze_pair(con, src, time_col, vol_cols):
    """Pass moja: aggregation kwa mwaka. Rudisha list ya dict kwa kila mwaka."""
    con.execute("SET TimeZone='UTC'")
    t = f'"{time_col}"'
    volsum = " + ".join(f'COALESCE("{c}",0)' for c in vol_cols) if vol_cols else "0"
    q = f"""
        SELECT
          EXTRACT(year FROM {t})::INT                                              AS yr,
          COUNT(*)                                                                 AS ticks,
          COUNT(DISTINCT CASE WHEN isodow({t}) NOT IN (6,7)
                              THEN CAST({t} AS DATE) END)                          AS wdays,
          SUM(CASE WHEN bid<=0 OR ask<=0 OR ask<bid THEN 1 ELSE 0 END)            AS bad,
          SUM(CASE WHEN ask<bid THEN 1 ELSE 0 END)                                AS negspr,
          SUM(CASE WHEN ({volsum})>0 THEN 1 ELSE 0 END)                           AS wvol,
          SUM(CASE WHEN isodow({t})=6 THEN 1 ELSE 0 END)                          AS sat,
          MIN(CAST({t} AS DATE))                                                   AS d0,
          MAX(CAST({t} AS DATE))                                                   AS d1
        FROM read_parquet('{src}', union_by_name => true)
        GROUP BY 1 ORDER BY 1
    """
    out = []
    for yr, ticks, wdays, bad, negspr, wvol, sat, d0, d1 in con.execute(q).fetchall():
        exp = weekdays_between(d0, d1)
        out.append(dict(yr=int(yr), ticks=int(ticks), wdays=int(wdays),
                        bad=int(bad), negspr=int(negspr), wvol=int(wvol),
                        sat=int(sat), d0=d0, d1=d1,
                        cov=(wdays / exp if exp else 0.0)))
    return out


def verdict(rows, min_cov, has_vol):
    """PASS/WARN/FAIL kutoka nambari za pair nzima."""
    if not rows:
        return "⚪ HAKUNA DATA", {}
    tot = sum(r["ticks"] for r in rows)
    bad = sum(r["bad"] for r in rows)
    neg = sum(r["negspr"] for r in rows)
    wvol = sum(r["wvol"] for r in rows)
    sat = sum(r["sat"] for r in rows)
    bad_pct = bad / tot if tot else 0
    vol_pct = wvol / tot if tot else 0
    sat_pct = sat / tot if tot else 0
    # coverage ya chini kabisa kati ya miaka KAMILI (sio mwaka wa kwanza/mwisho wa nusu)
    full_years = rows[1:-1] if len(rows) > 2 else rows
    min_year_cov = min((r["cov"] for r in full_years), default=1.0)
    m = dict(tot=tot, bad_pct=bad_pct, neg=neg, vol_pct=vol_pct, sat_pct=sat_pct,
             min_year_cov=min_year_cov)
    fails = []
    if bad_pct > 0.001:
        fails.append(f"bad-price {bad_pct*100:.2f}%")
    if neg > 0:
        fails.append(f"neg-spread {neg}")
    if min_year_cov < min_cov:
        fails.append(f"coverage {min_year_cov*100:.0f}%<{min_cov*100:.0f}%")
    warns = []
    if has_vol and vol_pct < 0.50:
        warns.append(f"volume {vol_pct*100:.0f}%")
    if sat_pct > 0.001:
        warns.append(f"Sat-ticks {sat_pct*100:.2f}%")
    if min_cov > min_year_cov >= min_cov - 0.05:
        warns.append("coverage borderline")
    if fails:
        return "❌ FAIL (" + ", ".join(fails) + ")", m
    if warns:
        return "⚠️ WARN (" + ", ".join(warns) + ")", m
    return "✅ PASS", m


def run(pairs, raw_root, out_path):
    cfg = load_config()
    min_cov = cfg.get("quality", {}).get("min_year_coverage", 0.90)
    con = duckdb.connect()
    summary = []     # (pair, rows, verdict_str, metrics)
    for pair in pairs:
        base = raw_root / f"symbol={pair}"
        if not base.exists() or not list(base.rglob("*.parquet")):
            print(f"  {pair}: (hakuna data)")
            summary.append((pair, [], "⚪ HAKUNA DATA", {}))
            continue
        src = _posix(base / "**" / "*.parquet")
        time_col, vol_cols = detect_volcols(con, src)
        if not time_col:
            print(f"  {pair}: (hakuna time column)")
            summary.append((pair, [], "❌ FAIL (no time col)", {}))
            continue
        print(f"  {pair}: nascan...", flush=True)
        rows = analyze_pair(con, src, time_col, vol_cols)
        v, m = verdict(rows, min_cov, bool(vol_cols))
        summary.append((pair, rows, v, m))
        print(f"  {pair}: {v}")

    L = ["# Ripoti ya Data — Muhtasari + Quality\n",
         f"*Pairs: {len(pairs)} | chanzo: raw ticks (Hive) | min coverage = {min_cov*100:.0f}% "
         "| checks: bad-price, neg-spread, coverage, volume%, Sat-ticks*\n"]

    # 1) MUHTASARI
    L += ["## 1) Muhtasari kwa pair\n",
          "| Pair | From | To | Miaka | Ticks | Siku(wd) | Ticks/siku | %vol | Verdict |",
          "|------|------|----|-------|-------|----------|-----------|------|---------|"]
    for pair, rows, v, m in summary:
        if not rows:
            L.append(f"| {pair} | — | — | — | — | — | — | — | {v} |"); continue
        d0 = min(r["d0"] for r in rows); d1 = max(r["d1"] for r in rows)
        tot = sum(r["ticks"] for r in rows); wd = sum(r["wdays"] for r in rows)
        L.append(f"| {pair} | {d0} | {d1} | {len(rows)} | {tot:,} | {wd:,} | "
                 f"{tot//max(wd,1):,} | {m.get('vol_pct',0)*100:.0f}% | {v} |")

    # 2) KWA MWAKA
    L += ["\n## 2) Coverage + quality kwa mwaka\n"]
    for pair, rows, v, m in summary:
        if not rows:
            continue
        L.append(f"### {pair} — {v}\n")
        L.append("| Mwaka | Ticks | Weekdays | Coverage | %vol | bad | Sat-ticks |")
        L.append("|-------|-------|----------|----------|------|-----|-----------|")
        for r in rows:
            vp = (r["wvol"] / r["ticks"] * 100) if r["ticks"] else 0
            cov = r["cov"] * 100
            flag = "" if cov >= min_cov * 100 else " ⚠️"
            L.append(f"| {r['yr']} | {r['ticks']:,} | {r['wdays']} | {cov:.0f}%{flag} | "
                     f"{vp:.0f}% | {r['bad']} | {r['sat']:,} |")
        L.append("")

    # 3) HITIMISHO
    npass = sum(1 for _, _, v, _ in summary if v.startswith("✅"))
    nwarn = sum(1 for _, _, v, _ in summary if v.startswith("⚠️"))
    nfail = sum(1 for _, _, v, _ in summary if v.startswith("❌"))
    nnone = sum(1 for _, _, v, _ in summary if v.startswith("⚪"))
    L += ["## 3) Hitimisho\n",
          f"- ✅ PASS: {npass} | ⚠️ WARN: {nwarn} | ❌ FAIL: {nfail} | ⚪ hakuna data: {nnone}",
          "\n---\n*Quality: bad-price/neg-spread lazima ≈0; coverage = weekdays zilizopo ÷ "
          f"weekdays zinazotarajiwa (≥{min_cov*100:.0f}%); %vol = ticks zenye bid_vol+ask_vol>0; "
          "Sat-ticks lazima ≈0 (soko limefungwa Jumamosi UTC). Verdict inatokana na nambari.*"]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out_path.relative_to(REPO_ROOT)} | PASS {npass} WARN {nwarn} FAIL {nfail}")
    return 0


def self_test():
    """Jenga raw ndogo ya pairs 2 (Hive) -> thibitisha aggregation + verdict."""
    import tempfile
    root = Path(tempfile.mkdtemp())
    con = duckdb.connect(); con.execute("SET TimeZone='UTC'")

    def write(pair, values):
        d = root / f"symbol={pair}" / "year=2023"
        d.mkdir(parents=True)
        rows = ",\n".join(values)
        con.execute(f"""
            COPY (SELECT * FROM (VALUES {rows})
                  t(timestamp,bid,ask,bid_vol,ask_vol,day,month,year))
            TO '{_posix(d / 'ticks.parquet')}' (FORMAT PARQUET)
        """)

    # AAA: safi (weekday, volume>0)
    write("AAA", [
        "(TIMESTAMPTZ '2023-03-01 10:00:00+00',1.10,1.11,2.0,3.0,1,3,2023)",   # Wed
        "(TIMESTAMPTZ '2023-03-02 10:00:00+00',1.10,1.11,1.0,1.0,2,3,2023)",   # Thu
    ])
    # BBB: ina bad price (ask<bid) + Sat tick + zero-vol
    write("BBB", [
        "(TIMESTAMPTZ '2023-03-01 10:00:00+00',1.10,1.11,1.0,1.0,1,3,2023)",   # Wed ok
        "(TIMESTAMPTZ '2023-03-04 10:00:00+00',1.10,1.11,0.0,0.0,4,3,2023)",   # Sat, zero-vol
        "(TIMESTAMPTZ '2023-03-02 10:00:00+00',1.20,1.10,1.0,1.0,2,3,2023)",   # ask<bid (bad)
    ])

    cfg_min = 0.90
    res = {}
    for pair in ("AAA", "BBB"):
        src = _posix(root / f"symbol={pair}" / "**" / "*.parquet")
        tc, vc = detect_volcols(con, src)
        rows = analyze_pair(con, src, tc, vc)
        v, m = verdict(rows, cfg_min, bool(vc))
        res[pair] = (rows, v, m)
        print(f"{pair}: {v} | ticks={sum(r['ticks'] for r in rows)} "
              f"bad_pct={m['bad_pct']*100:.1f}% sat_pct={m['sat_pct']*100:.1f}%")

    aaa_ok = res["AAA"][1].startswith("✅")
    bbb_bad = "bad-price" in res["BBB"][1] or "neg-spread" in res["BBB"][1]
    # BBB ina tick 1 ya Sat kati ya 3 -> sat detected
    bbb_sat = res["BBB"][2]["sat_pct"] > 0
    print("AAA PASS?", aaa_ok, "| BBB ina bad?", bbb_bad, "| BBB Sat?", bbb_sat)
    ok = aaa_ok and bbb_bad and bbb_sat
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="Ripoti ya data zote + quality")
    ap.add_argument("--symbol", default=None, help="pair moja (default: zote za config)")
    ap.add_argument("--out", default=None, help="njia ya output (default: reports/data_report.md)")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    cfg = load_config()
    raw_root = REPO_ROOT / cfg["paths"]["raw_ticks"]
    if not raw_root.exists():
        print(f"HITILAFU: '{raw_root}' haipo. Endesha kutoka root ya repo.", file=sys.stderr)
        return 1
    pairs = [args.symbol] if args.symbol else cfg["pairs"]
    out_path = Path(args.out) if args.out else (REPO_ROOT / cfg["paths"]["reports"] / "data_report.md")
    return run(pairs, raw_root, out_path)


if __name__ == "__main__":
    raise SystemExit(main())
