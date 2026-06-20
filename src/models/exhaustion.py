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

def arrays(pair):
    import polars as pl
    from data.dataset import load_candles
    c, h, l, o = pl.col("close"), pl.col("high"), pl.col("low"), pl.col("open")
    df = load_candles(pair, "D1", end=TRAIN_END).with_columns(
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
    rows = []
    for p in PAIRS:
        try:
            rows += collect(*arrays(p))
        except FileNotFoundError:
            continue
    R = np.array([r[0] for r in rows])
    base_ev = float(R.mean()) if len(R) else 0
    L = ["# Priority 2 — Exhaustion vs Momentum (Quantile EV Curve)\n",
         f"*Imezalishwa: {datetime.now():%Y-%m-%d %H:%M} | MR-fade entries (EUR pairs), exit tp_mean, "
         f"cost imo | EV(R) per quantile | baseline EV(all)={base_ev:+.3f}R, n={len(R)} | 2025+ HAIJAGUSWA*\n",
         "> Quantile EV-curve KWANZA (sio threshold). Feature ikionyesha STRUCTURE (EV inabadilika "
         "monotonic/wazi kwa quantile) = inatenganisha winners/losers. Narrative gain ≠ edge gain.\n",
         "| Feature | Q1 EV (n) | Q2 | Q3 | Q4 | Q5 | spread Q5−Q1 |",
         "|---------|-----------|----|----|----|----|--------------|"]
    for f in FEATURES:
        cur = ev_curve(rows, f)
        if not cur:
            L.append(f"| {f} | sample ndogo | | | | | |"); continue
        cells = " | ".join(f"{ev:+.3f} ({n})" if ev is not None else "—" for n, ev in cur)
        sp = cur[-1][1] - cur[0][1] if (cur[-1][1] is not None and cur[0][1] is not None) else None
        flag = "  ⬅️" if sp is not None and abs(sp) >= 0.15 else ""
        L.append(f"| {f}{' *(proxy)*' if f=='wick_rej' else ''} | {cells} | {sp:+.3f}{flag} |"
                 if sp is not None else f"| {f} | {cells} | — |")
    L.append(f"\n---\n*baseline EV(all entries) = **{base_ev:+.3f}R**. Feature INAONGEZA edge kama "
             "quantile fulani ina EV **juu zaidi** ya baseline kwa kiasi (⬅️ = spread Q5−Q1 ≥0.15R). "
             "Hapo ndipo tutaweza kuchagua quantiles (mf. Q1-Q2=exhaustion) — BAADAYE, kwa ushahidi. "
             "Feature isiyo na structure → DROP (hata kama ina mantiki). wick_rej ni PROXY ya rejection "
             "(OHLC, sio order flow). Hatua: keep features zenye structure → conditional strategy → OOS.*")
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
