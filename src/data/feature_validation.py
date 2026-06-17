"""
feature_validation.py — Thibitisha predictive power ya features za Model 1 KABLA ya
kujenga model (MODEL1_FEATURES.md). Kanuni: tusijenge kwa dhana (kosa la imbalance).

Inahesabu RAW predictors (#1-#5, #9 za MODEL1_FEATURES.md) kwa polars, kisha inapima
dhidi ya FORWARD returns (no-lookahead) kwa horizons kadhaa:

  Directional (returns, EMA200 slope, price-vs-EMA): rank-IC vs forward SIGNED return.
  Strength    (volatility, ADX):                      rank-IC vs |forward return|.
  Confirmation(volume_imbalance, tick_count):         vs signed NA |forward return|.

EMA200/ADX/vol zinatumia bar ya sasa + zilizopita TU (no-lookahead). Forward return
= close_{t+k}/close_t (target ya baadaye). rank-IC (Spearman) = robust kwa non-linear.

DuckDB (via dataset.py) -> polars. Inatoa reports/model1_feature_validation.md
Endesha kwenye PC ya Japhet:  python src\\data\\feature_validation.py
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from data.dataset import load_candles, config, REPO_ROOT  # noqa: E402

HTF = ["D1", "H4", "H2", "H1"]
# k=1 = PRIMARY (unbiased). k=5 = supportive. Long-horizon (k>=10) IC/hit-rate kwa
# features PERSISTENT (price_vs_ema/ema_slope) zina spurious-regression bias (tulithibitisha:
# random walk -> IC -0.15 @ k20). Multi-horizon definitive = Phase B permutation (Sehemu 7).
HORIZONS = [1, 5]
IC_THRESHOLD = 0.03            # |rank-IC| thabiti hapo juu = ina edge (FX huwa ndogo)
DIR = ["ret", "ema_slope", "price_vs_ema"]
STR = ["vol", "adx"]
CONF = ["volume_imbalance", "tick_count"]


def add_adx(df: pl.DataFrame, n: int = 14) -> pl.DataFrame:
    """ADX(14) kwa Wilder smoothing (≈ ewm alpha=1/n). No-lookahead (past+current)."""
    h, l, c = pl.col("high"), pl.col("low"), pl.col("close")
    df = df.with_columns(h.shift(1).alias("ph"), l.shift(1).alias("pl_"), c.shift(1).alias("pc"))
    df = df.with_columns(
        pl.max_horizontal((h - l), (h - pl.col("pc")).abs(), (l - pl.col("pc")).abs()).alias("tr"),
        (h - pl.col("ph")).alias("up"),
        (pl.col("pl_") - l).alias("dn"),
    )
    df = df.with_columns(
        pl.when((pl.col("up") > pl.col("dn")) & (pl.col("up") > 0)).then(pl.col("up"))
          .otherwise(0.0).alias("pdm"),
        pl.when((pl.col("dn") > pl.col("up")) & (pl.col("dn") > 0)).then(pl.col("dn"))
          .otherwise(0.0).alias("mdm"),
    )
    a = 1.0 / n
    df = df.with_columns(
        pl.col("tr").ewm_mean(alpha=a, min_samples=n).alias("atr"),
        pl.col("pdm").ewm_mean(alpha=a, min_samples=n).alias("pdms"),
        pl.col("mdm").ewm_mean(alpha=a, min_samples=n).alias("mdms"),
    )
    df = df.with_columns(
        (100 * pl.col("pdms") / pl.col("atr")).alias("pdi"),
        (100 * pl.col("mdms") / pl.col("atr")).alias("mdi"),
    )
    df = df.with_columns(
        (100 * (pl.col("pdi") - pl.col("mdi")).abs()
         / (pl.col("pdi") + pl.col("mdi"))).alias("dx")
    )
    return df.with_columns(pl.col("dx").ewm_mean(alpha=a, min_samples=n).alias("adx"))


def build_features(df: pl.DataFrame) -> pl.DataFrame:
    """RAW predictors za Model 1 (no-lookahead). EMA200 halisi (ewm)."""
    c = pl.col("close")
    df = df.with_columns((c.log() - c.log().shift(1)).alias("ret"))
    df = df.with_columns(
        pl.col("ret").rolling_std(window_size=20).alias("vol"),
        c.ewm_mean(span=200, min_samples=200).alias("ema"),
    )
    df = df.with_columns(
        ((pl.col("ema") / pl.col("ema").shift(20)) - 1).alias("ema_slope"),
        ((c - pl.col("ema")) / pl.col("ema")).alias("price_vs_ema"),
    )
    return add_adx(df)


def evaluate(df: pl.DataFrame, pair: str, tf: str) -> list[dict]:
    c = pl.col("close")
    df = df.with_columns(
        [(c.shift(-k).log() - c.log()).alias(f"fwd{k}") for k in HORIZONS]
    )
    rows = []
    for k in HORIZONS:
        fwd = f"fwd{k}"
        # NON-OVERLAPPING: chukua kila k-th row ili forward windows zisigongane
        # (overlap + feature persistent = spurious IC / Stambaugh bias).
        sk = df.gather_every(k)
        for f in DIR:
            d = sk.drop_nulls([f, fwd])
            if d.height < 60:
                continue
            ic = d.select(pl.corr(f, fwd, method="spearman")).item()
            hit = d.select((pl.col(f).sign() == pl.col(fwd).sign()).mean()).item()
            rows.append(dict(pair=pair, tf=tf, feat=f, kind="dir", k=k, ic=ic, hit=hit,
                             n=d.height))
        for f in STR:
            d = sk.drop_nulls([f, fwd])
            if d.height < 60:
                continue
            ic = d.select(pl.corr(f, pl.col(fwd).abs(), method="spearman")).item()
            rows.append(dict(pair=pair, tf=tf, feat=f, kind="str", k=k, ic=ic, hit=None,
                             n=d.height))
        for f in CONF:
            d = sk.drop_nulls([f, fwd])
            if d.height < 60:
                continue
            ic = d.select(pl.corr(f, fwd, method="spearman")).item()
            ica = d.select(pl.corr(f, pl.col(fwd).abs(), method="spearman")).item()
            rows.append(dict(pair=pair, tf=tf, feat=f, kind="conf", k=k, ic=ic, hit=ica,
                             n=d.height))
    return rows


def _agg(rows: list[dict], tf: str, feat: str) -> dict:
    """Mean IC + idadi ya pairs zenye |IC|>threshold, kwa kila horizon."""
    df = pl.DataFrame(rows).filter((pl.col("tf") == tf) & (pl.col("feat") == feat))
    out = {}
    for k in HORIZONS:
        s = df.filter(pl.col("k") == k)["ic"].fill_nan(None).drop_nulls()
        if s.len() == 0:
            out[k] = (None, 0)
        else:
            n_sig = int((s.abs() > IC_THRESHOLD).sum())
            out[k] = (round(s.mean(), 4), n_sig)
    return out


def fmt(rows: list[dict], npairs: int) -> str:
    L = ["# Model 1 — Feature Validation\n",
         f"*Imezalishwa: {datetime.now():%Y-%m-%d %H:%M} | rank-IC (Spearman) vs forward "
         f"returns, no-lookahead | pairs={npairs} | \|IC\|>{IC_THRESHOLD} = edge*\n"]
    hdr = "| Feature | " + " | ".join(f"k={k}" for k in HORIZONS) + " |"
    sep = "|---------|" + "".join("-----|" for _ in HORIZONS)
    for tf in HTF:
        L.append(f"\n## {tf}\n")
        L.append("**Directional** (vs forward SIGNED return) — mean IC (n pairs \\|IC\\|>thr):\n")
        L.append(hdr)
        L.append(sep)
        for f in DIR:
            a = _agg(rows, tf, f)
            cells = " | ".join(f"{a[k][0]} ({a[k][1]})" for k in HORIZONS)
            L.append(f"| {f} | {cells} |")
        L.append("\n**Strength** (vs \\|forward return\\|) — mean IC (n pairs \\|IC\\|>thr):\n")
        L.append(hdr)
        L.append(sep)
        for f in STR:
            a = _agg(rows, tf, f)
            cells = " | ".join(f"{a[k][0]} ({a[k][1]})" for k in HORIZONS)
            L.append(f"| {f} | {cells} |")
        L.append("\n**Confirmation** (signed IC) — mean IC (n pairs \\|IC\\|>thr):\n")
        L.append(hdr)
        L.append(sep)
        for f in CONF:
            a = _agg(rows, tf, f)
            cells = " | ".join(f"{a[k][0]} ({a[k][1]})" for k in HORIZONS)
            L.append(f"| {f} | {cells} |")
    L.append("\n---\n### Tafsiri & methodolojia\n")
    L.append("- **k=1 ni metric ya msingi (unbiased).** Feature yenye mean IC ~0 na pairs "
             "chache zenye \\|IC\\|>thr = **haina predictive power** → idemote/idrop "
             "(kama `volume_imbalance`).")
    L.append("- **Directional** (returns/EMA slope/price-vs-EMA): signed IC + hit-rate. "
             "**Strength** (vol/ADX): IC dhidi ya \\|return\\| = je inatabiri UKUBWA wa move "
             "(sio mwelekeo). **Confirmation**: signed IC ≈ 0 kote = haifai Model 1.")
    L.append("- ⚠️ **Bias ya long-horizon:** k=5 ni supportive tu; k≥10 kwa features "
             "persistent (price_vs_ema/ema_slope) zina **spurious-regression bias** "
             "(tulithibitisha: random walk → IC −0.15 @ k20). Kwa hiyo tumebaki k=1/k=5; "
             "**multi-horizon predictive testing definitive = Phase B permutation (Sehemu 7).**")
    return "\n".join(L)


def main() -> int:
    cfg = config()
    pairs = cfg["pairs"]
    if not (REPO_ROOT / cfg["paths"]["processed"] / "candles").exists():
        print("HITILAFU: candles hazipo. Endesha build_candles.py kwanza.", file=sys.stderr)
        return 1
    rows = []
    for tf in HTF:
        for p in pairs:
            try:
                df = load_candles(p, tf)
            except FileNotFoundError:
                print(f"  ONYO: {p} {tf} haipo — naruka.", file=sys.stderr)
                continue
            rows += evaluate(build_features(df), p, tf)
        print(f"  [{tf}] done")
    out = REPO_ROOT / cfg["paths"]["reports"] / "model1_feature_validation.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(fmt(rows, len(pairs)), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
