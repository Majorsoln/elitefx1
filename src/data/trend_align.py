"""
trend_align.py — TEST #1: Multi-TF alignment (TREND_STRUCTURES.md).

Swali: je trend-following ina edge pale D1+H4+H2+H1 ZOTE zinakubaliana mwelekeo?
"Trend wa kweli = scales zote zinaelekea upande mmoja."

Mbinu: kwa kila TF, sign ya trend = sign(close − EMA200). Tunamerge TF kubwa kwenye
base (H1) kwa **as-of (no-lookahead):** kwa wakati t, tunatumia bar ya TF kubwa
iliyoFUNGWA tu (avail = bar_open + interval ≤ decision-time). alignment = jumla ya
signs (−4…+4). Position = sign(alignment). Win = forward return upande huo.

UWAZI: inaonyesha — kwa kila kiwango cha alignment — bars NGAPI, win-rate, mean fwd ret.
Kama |align|=4 (makubaliano kamili) ina win >0.5 thabiti → lead; vinginevyo ❌.
(Hii ni scan ya uwazi; ikionyesha lead, inafuatwa na Phase B.)

Endesha (PC ya Japhet):  python src/data/trend_align.py
Self-test (popote):       python src/data/trend_align.py --self-test
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

BASE_TF = "H1"
HTF = ["D1", "H4", "H2", "H1"]          # zote zinazochangia alignment
TF_MIN = {"D1": 1440, "H4": 240, "H2": 120, "H1": 60}
FWD_H = 12                               # forward holding (bars za base H1)


def win_by_align(align, fwd):
    """numpy: kwa kila kiwango cha alignment, (n, win-rate ya sign(align)·fwd, mean)."""
    import numpy as np
    out = {}
    for lvl in range(-4, 5):
        m = align == lvl
        n = int(m.sum())
        if n == 0:
            out[lvl] = (0, None, None)
            continue
        if lvl == 0:
            out[lvl] = (n, None, float(fwd[m].mean()))   # hakuna mwelekeo
            continue
        dir_ret = np.sign(lvl) * fwd[m]
        out[lvl] = (n, float((dir_ret > 0).mean()), float(dir_ret.mean()))
    return out


# ───────────────────────── DATA PATH ─────────────────────────

def _sign_tf(pair, tf):
    """Rudisha polars df: avail (muda bar inafungwa, UTC), sign (∈ −1/0/+1)."""
    import polars as pl
    from data.dataset import load_candles
    c = pl.col("close")
    df = load_candles(pair, tf).with_columns(c.ewm_mean(span=200, min_samples=200).alias("ema"))
    df = df.with_columns(
        pl.when(c > pl.col("ema")).then(1).when(c < pl.col("ema")).then(-1)
          .otherwise(0).alias("sign"),
        (pl.col("bar_open") + pl.duration(minutes=TF_MIN[tf])).alias("avail"),
    )
    return df


def scan_pair():
    pass


def run():
    import numpy as np
    import polars as pl
    from data.dataset import config
    cfg = config()
    pairs = cfg["pairs"]
    if not (REPO_ROOT / cfg["paths"]["processed"] / "candles").exists():
        print("HITILAFU: candles hazipo.", file=sys.stderr)
        return 1

    agg = {lvl: [0, 0.0, 0.0] for lvl in range(-4, 5)}  # n, win*n, ret*n
    for p in pairs:
        base = _sign_tf(p, BASE_TF).select(
            ["avail", "close", "sign"]).rename({"sign": "s_H1"}).sort("avail")
        base = base.with_columns(
            (pl.col("close").shift(-FWD_H).log() - pl.col("close").log()).alias("fwd"))
        for tf in ["D1", "H4", "H2"]:
            h = _sign_tf(p, tf).select(["avail", "sign"]).rename(
                {"sign": f"s_{tf}"}).sort("avail")
            base = base.join_asof(h, on="avail", strategy="backward")
        base = base.with_columns(
            (pl.col("s_H1") + pl.col("s_D1") + pl.col("s_H4") + pl.col("s_H2")).alias("align"))
        d = base.select(["align", "fwd"]).drop_nulls()
        res = win_by_align(d["align"].to_numpy(), d["fwd"].to_numpy())
        for lvl in range(-4, 5):
            n, win, mret = res[lvl]
            if n > 0:
                agg[lvl][0] += n
                if win is not None:
                    agg[lvl][1] += win * n
                agg[lvl][2] += mret * n

    grand = sum(agg[l][0] for l in agg)
    L = ["# Trend Structure #1 — Multi-TF Alignment\n",
         f"*Imezalishwa: {datetime.now():%Y-%m-%d %H:%M} | base={BASE_TF}, fwd={FWD_H} bars | "
         "sign(close−EMA200) kwa D1/H4/H2/H1, as-of no-lookahead | pairs=9*\n",
         "> alignment = jumla ya signs (−4=zote chini … +4=zote juu). Position=sign(align). "
         "Win-rate ya |align|=4 >0.5 thabiti = makubaliano kamili yana edge.\n",
         "| alignment | maana | total bars | % | win-rate | mean fwd ret |",
         "|-----------|-------|-----------|---|----------|--------------|"]
    for lvl in range(4, -5, -1):
        n, wsum, rsum = agg[lvl]
        if n == 0:
            continue
        win = "—" if lvl == 0 else f"{wsum/n:.3f}"
        flag = ""
        if lvl != 0 and abs((wsum/n) - 0.5) >= 0.03:
            flag = "  ⬅️"
        pct = 100.0 * n / grand
        meaning = {4: "zote JUU", -4: "zote CHINI", 0: "mgawanyiko"}.get(lvl, "")
        L.append(f"| {lvl:+d} | {meaning} | {n:,} | {pct:.1f}% | {win}{flag} | {rsum/n:+.5f} |")
    L.append("\n---\n*Kama |align|=4 (±4) ina win-rate ~0.50 → makubaliano kamili ya TF "
             "**HAYANA** edge ya mwelekeo (trend wa kweli haukusaidia). Kama >0.55 thabiti "
             "→ **lead** → fuatwa na Phase B (permutation) kuthibitisha. ⬅️ = win ≠ 0.50 kwa ≥0.03.*")
    out = REPO_ROOT / cfg["paths"]["reports"] / "trend_align.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"Ripoti: {out.relative_to(REPO_ROOT)}")
    return 0


def self_test():
    """Thibitisha logic ya win_by_align: planted (align +4 -> fwd +) -> win>0.5; random -> ~0.5."""
    import numpy as np
    rng = np.random.default_rng(0)
    n = 40000
    align = rng.integers(-4, 5, n)
    fwd_pl = 0.0005 * align + rng.normal(0, 0.003, n)   # alignment inatabiri
    fwd_rd = rng.normal(0, 0.003, n)
    rp = win_by_align(align, fwd_pl)
    rr = win_by_align(align, fwd_rd)
    print("PLANTED (tarajio |align|=4 win > 0.5):")
    for lvl in (4, -4, 2, -2):
        print(f"  align={lvl:+d}: n={rp[lvl][0]:5d} win={rp[lvl][1]:.3f}")
    print("RANDOM (tarajio win ~ 0.50):")
    for lvl in (4, -4):
        print(f"  align={lvl:+d}: n={rr[lvl][0]:5d} win={rr[lvl][1]:.3f}")
    ok = rp[4][1] > 0.55 and rp[-4][1] > 0.55 and abs(rr[4][1] - 0.5) < 0.04
    print("\nSELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if "--self-test" in sys.argv:
        return self_test()
    sys.path.insert(0, str(REPO_ROOT / "src"))
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
