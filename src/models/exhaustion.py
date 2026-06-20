"""
exhaustion.py — Priority 2: Exhaustion vs Momentum (DOCTRINE §10, P14-16).

Swali: bei ikiwa STRETCHED (MR entry), je ni stretch-to-REVERSE (exhaustion → fade inalipa)
au stretch-to-CONTINUE (momentum → fade inashindwa)? Tunajaribu features kutenganisha.

Mbinu (kwa ushauri wa reviewer):
  • EV-curve kwa QUANTILE (Q1–Q5) KWANZA — sio threshold, sio binary. Angalia kama
    RELATIONSHIP ipo kabla ya cutoff yoyote (kuepuka threshold-overfit).
  • Feature iwekwe TU ikiongeza EV (incremental) — "narrative gain ≠ edge gain".
  • Entry = MR event (|pve| inavuka INTO ≥q80, fade); exit = tp_mean; cost imo.
  • Pool EUR-MR survivors (EURGBP/EURUSD/EURJPY) kwa sample ya kutosha.

Features (state vs transition vs rejection):
  accel       : |ret[i]| − |ret[i−1]|        (momentum accelerating?)  [transition]
  vol_expand  : vol[i] − vol[i−5]            (vol expanding?)          [transition]
  wick_rej*   : wick dhidi ya move / range   (*PROXY ya rejection — OHLC, sio order flow)
  time_since  : bars tangu extreme iliyopita                          [memory]

R-unit = 1.5×ATR. Train 2016-2024; 2025+ HAIGUSWI.
Endesha (PC ya Japhet):  python src/models/exhaustion.py
Self-test (popote):       python src/models/exhaustion.py --self-test
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]

PAIRS = ["EURGBP", "EURUSD", "EURJPY"]      # D1 MR survivors
TFS = ["D1", "H4", "H1"]                      # H4/H1 = entries nyingi zaidi (n kubwa)
EXT_Q = 0.80
TIMEOUT = 20
RISK_ATR = 1.5
NQ = 5
TRAIN_END = "2024-12-31"
FEATURES = ["accel", "vol_expand", "wick_rej", "time_since"]


def _cross_into(cond):
    c = cond.astype(bool)
    return np.where(c & ~np.r_[False, c[:-1]])[0]


def collect(close, o, hi, lo, ema, atr, pve, ret, vol, cost):
    """MR fade entries (event) -> list ya (R, {features})."""
    thr = np.nanquantile(np.abs(pve), EXT_Q)
    ext_idx = _cross_into(np.abs(pve) >= thr)
    is_ext = np.abs(pve) >= thr
    # time since previous extreme bar
    tsince = np.full(len(close), np.nan); last = -1
    for k in range(len(close)):
        tsince[k] = (k - last) if last >= 0 else np.nan
        if is_ext[k]:
            last = k
    n = len(close); rows = []; last_exit = -1
    for i in ext_idx:
        i = int(i)
        if i <= last_exit or i < 6 or i >= n - 1 or not (np.isfinite(atr[i]) and atr[i] > 0):
            continue
        d = -np.sign(pve[i])
        # exit = tp_mean (rudi EMA) au SL 2ATR au timeout
        ej = min(i + TIMEOUT, n - 1)
        for j in range(i + 1, min(i + TIMEOUT, n - 1) + 1):
            fav = d * (close[j] - close[i])
            if d * (ema[j] - close[j]) <= 0 or fav <= -2 * atr[i]:
                ej = j; break
        R = (d * (close[ej] / close[i] - 1) - cost[i]) / (RISK_ATR * atr[i] / close[i])
        rng_bar = max(hi[i] - lo[i], 1e-12)
        wick = ((hi[i] - max(o[i], close[i])) if d < 0 else (min(o[i], close[i]) - lo[i])) / rng_bar
        rows.append((R, dict(
            accel=abs(ret[i]) - abs(ret[i-1]),
            vol_expand=vol[i] - vol[i-5],
            wick_rej=wick,
            time_since=tsince[i])))
        last_exit = ej
    return rows


def rank_ic(rows, feat):
    """Spearman rank-IC (feature vs R) — robust kuliko endpoint-spread. + p ya kawaida."""
    v = np.array([r[1][feat] for r in rows]); R = np.array([r[0] for r in rows])
    m = np.isfinite(v) & np.isfinite(R); v, R = v[m], R[m]
    if len(R) < 30:
        return None, 0
    rv = np.argsort(np.argsort(v)); rr = np.argsort(np.argsort(R))
    ic = float(np.corrcoef(rv, rr)[0, 1])
    return ic, len(R)


def ev_curve(rows, feat):
    vals = np.array([r[1][feat] for r in rows]); R = np.array([r[0] for r in rows])
    m = np.isfinite(vals) & np.isfinite(R)
    vals, R = vals[m], R[m]
    if len(R) < NQ * 8:
        return None
    qs = np.quantile(vals, [i / NQ for i in range(1, NQ)])
    b = np.digitize(vals, qs)
    return [(int((b == q).sum()), float(R[b == q].mean()) if (b == q).any() else None) for q in range(NQ)]


# ───────────────────────── DATA PATH ─────────────────────────
def _pip(s):
    return 0.01 if "JPY" in s.upper() else 0.0001

def arrays(pair, tf):
    import polars as pl
    from data.dataset import load_candles
    c, h, l, o = pl.col("close"), pl.col("high"), pl.col("low"), pl.col("open")
    df = load_candles(pair, tf, end=TRAIN_END).with_columns(
        c.ewm_mean(span=200, min_samples=200).alias("ema"),
        (c.log() - c.log().shift(1)).alias("ret"),
        pl.max_horizontal(h - l, (h - c.shift(1)).abs(), (l - c.shift(1)).abs()).alias("tr"))
    df = df.with_columns(
        pl.col("tr").ewm_mean(alpha=1/14, min_samples=14).alias("atr"),
        ((c - pl.col("ema")) / pl.col("ema")).alias("pve"),
        pl.col("ret").rolling_std(20).alias("vol"),
        (2 * pl.col("spread_mean_pips") * _pip(pair) / c).alias("cost"))
    d = df.select(["close", "open", "high", "low", "ema", "atr", "pve", "ret", "vol", "cost"]).drop_nulls()
    return [d[x].to_numpy() for x in ["close", "open", "high", "low", "ema", "atr", "pve", "ret", "vol", "cost"]]


def run():
    from data.dataset import config
    cfg = config()
    if not (REPO_ROOT / cfg["paths"]["processed"] / "candles").exists():
        print("HITILAFU: candles hazipo.", file=sys.stderr); return 1
    L = ["# Priority 2 — Exhaustion vs Momentum (rank-IC + EV-curve)\n",
         f"*Imezalishwa: {datetime.now():%Y-%m-%d %H:%M} | MR-fade entries (EUR pairs), exit tp_mean, "
         "cost imo | rank-IC (Spearman feature vs R) + EV-curve | 2025+ HAIJAGUSWA*\n",
         "> **rank-IC** ndio metric kuu (robust kuliko endpoint-spread). \\|IC\\|≥~0.06 thabiti "
         "kwa TF + n kubwa = structure halisi. Curve jagged + IC≈0 = NOISE → DROP. Narrative ≠ edge.\n",
         "## rank-IC (feature vs R) kwa TF\n",
         "| Feature | " + " | ".join(f"{tf} IC (n)" for tf in TFS) + " |",
         "|---------|" + "---|" * len(TFS)]
    rows_by_tf = {}
    for tf in TFS:
        rows = []
        for p in PAIRS:
            try:
                rows += collect(*arrays(p, tf))
            except FileNotFoundError:
                continue
        rows_by_tf[tf] = rows
    for f in FEATURES:
        cells = []
        for tf in TFS:
            ic, n = rank_ic(rows_by_tf[tf], f)
            cells.append(f"{ic:+.3f} ({n})" if ic is not None else "·")
        nm = f + (" *(proxy)*" if f == "wick_rej" else "")
        L.append(f"| {nm} | " + " | ".join(cells) + " |")
    # EV-curve ya TF yenye n kubwa zaidi (H1 kawaida)
    big_tf = max(TFS, key=lambda t: len(rows_by_tf[t]))
    rows = rows_by_tf[big_tf]; R = np.array([r[0] for r in rows]); base = float(R.mean()) if len(R) else 0
    L.append(f"\n## EV-curve (Q1–Q5) — {big_tf} (n={len(R)}, baseline EV={base:+.3f}R)\n")
    L.append("| Feature | Q1 (n) | Q2 | Q3 | Q4 | Q5 |")
    L.append("|---------|--------|----|----|----|----|")
    for f in FEATURES:
        cur = ev_curve(rows, f)
        if not cur:
            L.append(f"| {f} | sample ndogo | | | | |"); continue
        L.append(f"| {f} | " + " | ".join(f"{ev:+.3f} ({n})" if ev is not None else "—" for n, ev in cur) + " |")
    L.append(f"\n---\n*rank-IC = Spearman(feature, R) — feature INATENGANISHA winners/losers kama "
             "\\|IC\\| ni meaningful NA thabiti kwa TF. Curve jagged + IC≈0 = noise → DROP (hata "
             "kama ina mantiki). EV-curve inaonyeshwa kwa TF yenye n kubwa. wick_rej = PROXY ya "
             "rejection (OHLC, sio order flow). Keep features zenye IC thabiti → conditional strategy → OOS.*")
    out = REPO_ROOT / cfg["paths"]["reports"] / "exhaustion.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"Ripoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """Planted: feature 'accel' inatenganisha R (accel ndogo -> exhaustion -> R+). EV-curve ionyeshe structure."""
    rng = np.random.default_rng(0)
    n = 4000
    rows = []
    for _ in range(600):
        a = rng.normal(0, 1)
        R = -0.3 * a + rng.normal(0, 0.5)        # accel ndogo (hasi) -> R kubwa (exhaustion)
        rows.append((R, dict(accel=a, vol_expand=rng.normal(), wick_rej=rng.random(), time_since=rng.random()*20)))
    cur = ev_curve(rows, "accel")
    print("accel EV-curve (tarajio: Q1 high -> Q5 low):")
    for q, (nn, ev) in enumerate(cur):
        print(f"  Q{q+1}: n={nn} EV={ev:+.3f}")
    cur2 = ev_curve(rows, "vol_expand")  # no relationship
    sp1 = cur[-1][1] - cur[0][1]; sp2 = cur2[-1][1] - cur2[0][1]
    print(f"accel spread={sp1:+.3f} (structure) | vol_expand spread={sp2:+.3f} (~0)")
    ok = abs(sp1) > 0.3 and abs(sp2) < 0.2
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if "--self-test" in sys.argv:
        return self_test()
    sys.path.insert(0, str(REPO_ROOT / "src"))
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
