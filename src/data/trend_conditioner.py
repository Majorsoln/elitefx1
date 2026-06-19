"""
trend_conditioner.py — TEST #2: Conditioner-interaction (TREND_STRUCTURES.md).

Pendekezo #1 la washauri + thesis yetu: mwelekeo PEKEE ni dhaifu, lakini labda
trend-following INAFANYA KAZI ndani ya regime fulani. Swali:

  "Je win-rate ya trend-following (sign(EMA slope)) inaboreka pale:
     - trend ni SAFI (Efficiency Ratio juu) ?
     - volatility iko juu/chini ?"

Mbinu: signal ya mwelekeo = sign(ema_slope). Conditioner (ER au vol) inagawa bars kwa
QUARTILE (Q1..Q4) PER (pair, tf). Ndani ya kila quartile, pima trend-follow win-rate.
- High-ER quartile ina win >0.55 ? -> trend-following inafanya kazi kwenye trend safi (edge).
- win <0.45 -> mean-reversion ndio inafanya kazi hapo (reverse).
- zote ~0.50 -> conditioner haisaidii.

NO-LOOKAHEAD: signal+conditioner kwa bar t (past+current); fwd return t->t+h.
ER & ema kwa window zinazolingana na horizon (B's ushauri).

Endesha (PC ya Japhet):  python src/data/trend_conditioner.py
Self-test (popote):       python src/data/trend_conditioner.py --self-test
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

TFS = ["D1", "H4", "H1"]
H = {"D1": 5, "H4": 10, "H1": 12}        # forward holding
ER_N = {"D1": 10, "H4": 20, "H1": 24}    # window ya ER/slope (~ inalingana na horizon)
COND = ["ER", "vol"]


def win_by_quartile(sig_sign, fwd, cond):
    """numpy: gawa kwa quartile ya cond; ndani ya kila Q, trend-follow win-rate.
    Rudisha {Q: (n, win, mean_dir_ret)}."""
    import numpy as np
    qs = np.quantile(cond, [0.25, 0.50, 0.75])
    bucket = np.digitize(cond, qs)        # 0..3 => Q1..Q4
    out = {}
    for q in range(4):
        m = (bucket == q) & (sig_sign != 0)
        n = int(m.sum())
        if n == 0:
            out[q] = (0, None, None); continue
        dir_ret = sig_sign[m] * fwd[m]
        out[q] = (n, float((dir_ret > 0).mean()), float(dir_ret.mean()))
    return out


# ───────────────────────── DATA PATH ─────────────────────────

def _features(pair, tf):
    import numpy as np
    import polars as pl
    from data.dataset import load_candles
    n = ER_N[tf]; h = H[tf]
    c = pl.col("close")
    df = load_candles(pair, tf)
    df = df.with_columns(c.ewm_mean(span=200, min_samples=200).alias("ema"),
                         (c.log() - c.log().shift(1)).alias("ret"))
    df = df.with_columns(
        ((pl.col("ema") / pl.col("ema").shift(n)) - 1).alias("slope"),
        pl.col("ret").rolling_std(window_size=n).alias("vol"),
        # Efficiency Ratio = |net change| / sum|changes| (window n)
        ((c - c.shift(n)).abs()
         / (c - c.shift(1)).abs().rolling_sum(window_size=n)).alias("ER"),
        (c.shift(-h).log() - c.log()).alias("fwd"),
    )
    d = df.select(["slope", "vol", "ER", "fwd"]).drop_nulls()
    return d


def run():
    import numpy as np
    from data.dataset import config
    cfg = config()
    pairs = cfg["pairs"]
    if not (REPO_ROOT / cfg["paths"]["processed"] / "candles").exists():
        print("HITILAFU: candles hazipo.", file=sys.stderr); return 1

    # agg[tf][cond][q] = [n, win*n, ret*n]
    agg = {tf: {co: {q: [0, 0.0, 0.0] for q in range(4)} for co in COND} for tf in TFS}
    for tf in TFS:
        for p in pairs:
            d = _features(p, tf)
            if d.height < 200:
                continue
            sig = np.sign(d["slope"].to_numpy())
            fwd = d["fwd"].to_numpy()
            for co in COND:
                res = win_by_quartile(sig, fwd, d[co].to_numpy())
                for q in range(4):
                    n, win, mret = res[q]
                    if n:
                        agg[tf][co][q][0] += n
                        agg[tf][co][q][1] += win * n
                        agg[tf][co][q][2] += mret * n

    L = ["# Trend Structure #2 — Conditioner Interaction\n",
         f"*Imezalishwa: {datetime.now():%Y-%m-%d %H:%M} | signal=sign(EMA slope); "
         "conditioner quartiles (Q1=chini…Q4=juu) | trend-follow win-rate ndani ya kila Q | "
         "no-lookahead | pairs=9*\n",
         "> Q4 ya ER (trend safi) win >0.55 = trend-following ina edge hapo. "
         "win <0.45 = mean-reversion. Zote ~0.50 = conditioner haisaidii.\n"]
    for tf in TFS:
        L.append(f"\n## {tf}  (fwd={H[tf]}, window={ER_N[tf]})\n")
        for co in COND:
            label = "Efficiency Ratio (usafi wa trend)" if co == "ER" else "Volatility"
            L.append(f"\n**Conditioner: {label}**\n")
            L.append("| Quartile | total bars | trend-follow win | mean dir ret |")
            L.append("|----------|-----------|------------------|--------------|")
            for q in range(4):
                n, wsum, rsum = agg[tf][co][q]
                if n == 0:
                    L.append(f"| Q{q+1} | 0 | — | — |"); continue
                win = wsum / n
                flag = "  ⬅️" if abs(win - 0.5) >= 0.03 else ""
                L.append(f"| Q{q+1}{' (juu)' if q==3 else ' (chini)' if q==0 else ''} "
                         f"| {n:,} | {win:.3f}{flag} | {rsum/n:+.5f} |")
    L.append("\n---\n*⬅️ = win ≠ 0.50 kwa ≥0.03. **Cha kuangalia:** je win-rate inabadilika "
             "monotonic na quartile ya ER/vol? Q4-ER (trend safi) >0.55 thabiti kwenye "
             "TF/pairs → **edge ya kwanza** (trend-following ndani ya trend safi) → Phase B. "
             "Q4-ER <0.45 → mean-reversion kwenye trend safi. Zote ~0.50 → conditioner haisaidii.*")
    out = REPO_ROOT / cfg["paths"]["reports"] / "trend_conditioner.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"Ripoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """Planted: trend-following inafanya kazi TU kwenye high-ER (Q4). -> Q4 win>0.55, Q1~0.5."""
    import numpy as np
    rng = np.random.default_rng(0)
    n = 60000
    slope = rng.normal(0, 1, n)
    ER = rng.uniform(0, 1, n)
    vol = rng.uniform(0, 1, n)
    # fwd inategemea slope TU pale ER iko juu (high-ER => trend-follow inafanya kazi)
    fwd = np.where(ER > 0.75, 0.002 * np.sign(slope), 0.0) + rng.normal(0, 0.003, n)
    r = win_by_quartile(np.sign(slope), fwd, ER)
    rv = win_by_quartile(np.sign(slope), fwd, vol)
    print("ER conditioner (tarajio Q4 win>0.55, Q1~0.50):")
    for q in range(4):
        print(f"  Q{q+1}: n={r[q][0]:6d} win={r[q][1]:.3f}")
    print("vol conditioner (tarajio FLAT — vol haitenganishi edge):")
    for q in range(4):
        print(f"  Q{q+1}: win={rv[q][1]:.3f}")
    vol_wins = [rv[q][1] for q in range(4)]
    # ER: inatenganisha (Q4 >> Q1). vol: flat (haitenganishi).
    ok = (r[3][1] > 0.55 and (r[3][1] - r[0][1]) > 0.10
          and (max(vol_wins) - min(vol_wins)) < 0.05)
    print("\nSELF-TEST:", "PASS" if ok else "FAIL",
          f"(ER separation={r[3][1]-r[0][1]:.2f}, vol spread={max(vol_wins)-min(vol_wins):.2f})")
    return 0 if ok else 1


def main():
    if "--self-test" in sys.argv:
        return self_test()
    sys.path.insert(0, str(REPO_ROOT / "src"))
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
