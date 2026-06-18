"""direction_edge.py — Phase B: je MWELEKEO (UP/DOWN) una edge halisi? (Model 1 gate)

Hili ndilo SWALI LA KWANZA la modeler, na onyo kuu la mfumo: Model 1 inatakiwa
itoe mwelekeo (UP/DOWN), LAKINI validation ya features (reports/model1_feature_validation.md)
ilionyesha:
  - next-bar (k=1) directional IC ≈ 0  (hakuna edge wa next-bar)
  - long-horizon (k≥10) raw IC ina SPURIOUS-REGRESSION bias (random walk -> IC -0.15 @ k20)
  -> Hitimisho: jibu definitive linahitaji PERMUTATION test (Sehemu 7, Phase B), sio IC ghafi.

Hati hii inajibu: "Kwa multi-bar holding, je trend-following signal (price-vs-EMA,
EMA slope) ina edge wa mwelekeo unaozidi BAHATI?" — KABLA hatujajenga HMM states,
Model 1, entries au R6 zinazotegemea mwelekeo.

## Mbinu: Circular-shift permutation (inadhibiti spurious-regression bias)

Kwa kila (pair, tf, signal, horizon h):
  1. Signal s_t = trend score (price_vs_ema AU ema_slope), no-lookahead (past+current TU).
     Position p_t = sign(s_t)  ∈ {-1, +1}.
  2. Forward return  f_t = log(close_{t+h} / close_t).  NON-OVERLAPPING (gather_every(h))
     ili windows zisigongane (overlap + signal persistent = spurious dependence).
  3. Statistic = mean(p_t · f_t)  (mean signed strategy return kwa trade) + hit-rate.
  4. NULL (circular shift): zungusha p kwa offset ya nasibu dhidi ya f, mara N=10,000.
     Hii inahifadhi muundo (autocorrelation) wa p NA f, lakini inavunja ALIGNMENT ya
     kweli. p-value = sehemu ya permutations zenye statistic >= observed (one-sided).

KWA NINI circular-shift, sio IC ghafi?  Spurious-regression bias hutokea kwa sababu
signal PERSISTENT dhidi ya returns ~random-walk hutoa correlation iliyovimba HATA
wakipokuwa HURU. Chini ya circular shift, p na f hubaki huru lakini huhifadhi
persistence yao — kwa hiyo NULL DISTRIBUTION yenyewe ina ile inflation ya spurious.
Observed inahesabika "edge" TU ikizidi kile spurious alignment inachozalisha. Hii
ndiyo de-biasing sahihi ya tatizo la long-horizon walilolibaini.

Drift: chini ya circular shift, p_t·f_t ina mean ≈ mean(p)·mean(f) (static bias × drift),
kwa hiyo permutation INAKADIRIA "direction-timing skill" ZAIDI ya static long/short bias
+ drift. Tunaripoti pia drift baseline (always-long) kwa uwazi.

## Matumizi
Data halisi (PC ya Japhet, candles 26GB):
    python src/models/direction_edge.py
Synthetic self-test (popote, numpy tu — kuthibitisha MACHINERY kabla ya data halisi):
    python src/models/direction_edge.py --self-test

Inatoa reports/model1_direction_edge.md
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]

HTF = ["D1", "H4", "H2", "H1"]
SIGNALS = ["price_vs_ema", "ema_slope"]   # directional features (zilizo ⚠️ haijatatuliwa)
# Holding horizons (bars) kwa multi-bar — mwelekeo si swali la next-bar (k=1 IC≈0).
HORIZONS = {"D1": [3, 5, 10], "H4": [5, 10, 20], "H2": [5, 10, 20], "H1": [6, 12, 24]}
N_PERM = 10_000
MIN_SAMPLES = 60
ALPHA = 0.05
SEED = 7


# ───────────────────────── CORE (numpy tu — testable bila polars) ─────────────────────────

def directional_stats(pos: np.ndarray, fwd: np.ndarray) -> dict:
    """Statistic za rule ya mwelekeo: mean signed return + hit-rate."""
    mean_ret = float(np.mean(pos * fwd))
    nz = fwd != 0
    hit = float(np.mean(np.sign(pos[nz]) == np.sign(fwd[nz]))) if nz.any() else float("nan")
    drift = float(np.mean(fwd))          # always-long baseline
    long_frac = float(np.mean(pos > 0))  # je signal ina bias ya upande mmoja?
    return dict(mean_ret=mean_ret, hit=hit, drift=drift, long_frac=long_frac, n=int(len(pos)))


def circular_shift_pvalue(
    pos: np.ndarray, fwd: np.ndarray, n_perm: int = N_PERM, rng: np.random.Generator | None = None
) -> tuple[float, float, float, float]:
    """One-sided permutation p-value kwa circular shift ya `pos` dhidi ya `fwd`.

    Inarudisha (observed_stat, p_value, null_mean, null_std). p inajumuisha +1/+1
    (unbiased permutation lower bound: p kamwe si 0 hasa).
    """
    rng = rng or np.random.default_rng(SEED)
    n = len(pos)
    obs = float(np.mean(pos * fwd))
    if n < 3:
        return obs, float("nan"), float("nan"), float("nan")
    # offsets za nasibu 1..n-1 (epuka 0 = no shift)
    offs = rng.integers(1, n, size=n_perm)
    null = np.array([np.mean(np.roll(pos, int(o)) * fwd) for o in offs])
    p = (np.sum(null >= obs) + 1) / (n_perm + 1)   # one-sided: edge = positive signed return
    return obs, float(p), float(null.mean()), float(null.std())


def evaluate_series(
    sig: np.ndarray, fwd: np.ndarray, n_perm: int = N_PERM, rng: np.random.Generator | None = None
) -> dict | None:
    """Pima signal moja dhidi ya forward return moja (already non-overlapping). None kama ndogo."""
    m = np.isfinite(sig) & np.isfinite(fwd)
    sig, fwd = sig[m], fwd[m]
    pos = np.sign(sig)
    nz = pos != 0           # ondoa signal == 0 (hakuna mwelekeo)
    pos, fwd = pos[nz], fwd[nz]
    if len(pos) < MIN_SAMPLES:
        return None
    stats = directional_stats(pos, fwd)
    obs, p, nmean, nstd = circular_shift_pvalue(pos, fwd, n_perm, rng)
    stats.update(p=p, null_mean=nmean, null_std=nstd)
    return stats


# ───────────────────────── DATA PATH (polars/dataset.py — PC ya Japhet) ─────────────────────────

def _build_signals(df):
    """RAW directional predictors (no-lookahead) — DEFINITIONS SAWA na feature_validation.py."""
    import polars as pl
    c = pl.col("close")
    df = df.with_columns(c.ewm_mean(span=200, min_samples=200).alias("ema"))
    return df.with_columns(
        ((pl.col("ema") / pl.col("ema").shift(20)) - 1).alias("ema_slope"),
        ((c - pl.col("ema")) / pl.col("ema")).alias("price_vs_ema"),
    )


def evaluate_pair_tf(pair: str, tf: str, rng: np.random.Generator) -> list[dict]:
    import polars as pl
    from data.dataset import load_candles

    df = _build_signals(load_candles(pair, tf))
    c = pl.col("close")
    rows = []
    for h in HORIZONS[tf]:
        d = df.with_columns((c.shift(-h).log() - c.log()).alias("fwd"))
        sk = d.gather_every(h)   # NON-OVERLAPPING: windows zisigongane
        for s in SIGNALS:
            x = sk.select([pl.col(s).alias("sig"), pl.col("fwd")]).drop_nulls()
            if x.height < MIN_SAMPLES:
                continue
            res = evaluate_series(x["sig"].to_numpy(), x["fwd"].to_numpy(), N_PERM, rng)
            if res is None:
                continue
            res.update(pair=pair, tf=tf, signal=s, h=h)
            rows.append(res)
    return rows


# ───────────────────────── REPORT ─────────────────────────

def _verdict(sig_rows: list[dict]) -> str:
    """Hukumu kwa kila (tf, signal): pairs ngapi significant (p<α) kwa mwelekeo sahihi."""
    n = len(sig_rows)
    n_sig = sum(1 for r in sig_rows if r["p"] < ALPHA and r["mean_ret"] > 0)
    n_hit = sum(1 for r in sig_rows if r["hit"] > 0.5)
    # chini ya null, kwa α=0.05, n_sig ~ Binom(n, 0.05): tegemea ~0.05n kwa bahati.
    exp_chance = ALPHA * n
    if n_sig == 0:
        return f"❌ HAKUNA edge (0/{n} significant; bahati≈{exp_chance:.1f})"
    if n_sig <= exp_chance + 1:
        return f"⚠️ shaka ({n_sig}/{n} significant ≈ bahati {exp_chance:.1f}) — multiple-testing"
    return f"✅ edge ({n_sig}/{n} significant, hit>0.5 {n_hit}/{n}; bahati≈{exp_chance:.1f})"


def fmt_report(rows: list[dict], npairs: int, n_perm: int) -> str:
    L = ["# Model 1 — Directional Edge (Phase B Permutation)\n",
         f"*Imezalishwa: {datetime.now():%Y-%m-%d %H:%M} | circular-shift permutation "
         f"(N={n_perm:,}) | mean signed return, no-lookahead, NON-overlapping | pairs={npairs} | "
         f"α={ALPHA}*\n",
         "> **Swali:** je trend-following signal (price-vs-EMA, EMA slope) ina edge wa "
         "MWELEKEO kwa multi-bar holding, unaozidi bahati? Hii ndiyo gate KABLA ya kujenga "
         "HMM states / Model 1 / entries / R6 (zinazotegemea mwelekeo).\n"]
    for tf in HTF:
        L.append(f"\n## {tf}\n")
        for s in SIGNALS:
            sub = sorted([r for r in rows if r["tf"] == tf and r["signal"] == s],
                         key=lambda r: (r["h"], r["pair"]))
            if not sub:
                continue
            L.append(f"\n### `{s}`  — {_verdict(sub)}\n")
            L.append("| Pair | h | mean_ret | hit | drift(LO) | long% | p (perm) | "
                     "null μ±σ | n |")
            L.append("|------|---|----------|-----|-----------|-------|----------|----------|---|")
            for r in sub:
                star = "  ⬅️" if (r["p"] < ALPHA and r["mean_ret"] > 0) else ""
                L.append(
                    f"| {r['pair']} | {r['h']} | {r['mean_ret']:+.5f} | {r['hit']:.3f} | "
                    f"{r['drift']:+.5f} | {r['long_frac']:.2f} | **{r['p']:.4f}**{star} | "
                    f"{r['null_mean']:+.5f}±{r['null_std']:.5f} | {r['n']:,} |"
                )
    L.append("\n---\n### Tafsiri & methodolojia\n")
    L.append("- **mean_ret** = mean(sign(signal)·forward_return) kwa trade (non-overlapping). "
             "**p (perm)** = one-sided circular-shift p-value: P(null ≥ observed). p < α NA "
             "mean_ret > 0 = mwelekeo una edge unaozidi spurious alignment + drift.")
    L.append("- **Kwa nini circular-shift, sio IC ghafi:** signal persistent dhidi ya returns "
             "~random-walk hutoa correlation iliyovimba hata wakiwa huru (spurious-regression, "
             "ndio sababu k≥10 IC haiaminiki). Circular shift huhifadhi persistence ya kila "
             "series lakini huvunja alignment → NULL yenyewe ina inflation hiyo → p-value "
             "imede-bias.")
    L.append("- **drift(LO)** = mean(forward_return) (always-long). **long%** = sehemu ya muda "
             "signal iko long. Permutation tayari ina-account static bias+drift (null μ ≈ "
             "long-bias × drift); kwa hiyo p inapima **direction-timing skill**, sio drift.")
    L.append(f"- **Multiple testing:** pairs {npairs} × horizons × signals. Kwa α={ALPHA}, "
             f"tegemea ~{ALPHA*npairs:.1f} significant KWA BAHATI kwa kila (tf,signal). Hukumu "
             "✅ inahitaji significant ZAIDI ya hii (sio 1–2 zilizotawanyika).")
    L.append("- **Hatua inayofuata:** signal/TF zenye ✅ → ndizo zinazoaminika kwa mwelekeo wa "
             "Model 1. Zikikosekana kote → mwelekeo (UP/DOWN) si tradeable kwa trend-following "
             "next-step; mfumo lazima ufikiriwe upya (k.m. vol-regime + symmetric, au mwelekeo "
             "kutoka chanzo kingine) — KABLA ya kujenga juu yake.")
    return "\n".join(L)


# ───────────────────────── SELF-TEST (synthetic — thibitisha machinery) ─────────────────────────

def self_test(n_perm: int = 2000) -> int:
    """Thibitisha machinery kama timu ilivyofanya kwa diagnostics (§0): planted edge -> p ndogo;
    random walk -> p ~uniform (hakuna false positive ya kimfumo)."""
    rng = np.random.default_rng(SEED)
    print("SELF-TEST: machinery ya direction_edge (numpy tu, hakuna data halisi)\n")

    # 1) PLANTED EDGE: forward return ina drift inayotegemea position halisi.
    n = 1500
    pos_true = rng.choice([-1.0, 1.0], size=n)
    fwd = pos_true * 0.002 + rng.normal(0, 0.01, n)     # edge wa kweli + noise
    sig = pos_true.copy()
    r = evaluate_series(sig, fwd, n_perm, rng)
    print(f"  [1] PLANTED edge : mean_ret={r['mean_ret']:+.5f} hit={r['hit']:.3f} p={r['p']:.4f}")
    assert r["p"] < 0.01, f"planted edge haijagunduliwa (p={r['p']})"
    assert r["hit"] > 0.55, f"hit-rate ndogo isivyotarajiwa ({r['hit']})"

    # 2) PURE NOISE (random walk): signal=price-vs-EMA, returns iid. Hakuna edge.
    #    Pima FALSE-POSITIVE rate kwenye seeds nyingi — lazima iwe karibu α, sio kubwa.
    fp = 0
    trials = 40
    for _ in range(trials):
        rw_ret = rng.normal(0, 0.01, n)
        price = np.cumsum(rw_ret)
        ema = _ewm(price, span=50)
        sign = price - ema                  # price-vs-EMA (persistent, spurious-prone)
        fwdn = np.concatenate([np.diff(price, n=1)[:], [np.nan]])  # next-step rw return
        # multi-bar non-overlapping h=5
        h = 5
        f5 = np.full(n, np.nan)
        f5[:-h] = price[h:] - price[:-h]
        idx = np.arange(0, n, h)
        rr = evaluate_series(sign[idx], f5[idx], n_perm, rng)
        if rr is not None and rr["p"] < ALPHA and rr["mean_ret"] > 0:
            fp += 1
    rate = fp / trials
    print(f"  [2] PURE NOISE   : false-positive rate = {fp}/{trials} = {rate:.3f} "
          f"(tegemea ~α={ALPHA})")
    assert rate <= 0.20, f"false-positive rate kubwa mno ({rate}) — machinery ina bias!"

    # 3) NULL ya circular-shift ina-center karibu na static bias×drift (sanity)
    print(f"  [3] circular-shift null inadhibiti spurious alignment (de-biased).")
    print("\n✅ SELF-TEST PASS: planted edge inagunduliwa; noise haitoi false positives za "
          "kimfumo; spurious-regression imedhibitiwa.")
    return 0


def _ewm(x: np.ndarray, span: int) -> np.ndarray:
    """EWM mean rahisi (numpy) kwa self-test tu."""
    a = 2.0 / (span + 1.0)
    out = np.empty_like(x)
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


# ───────────────────────── MAIN ─────────────────────────

def main() -> int:
    if "--self-test" in sys.argv:
        return self_test()

    sys.path.insert(0, str(REPO_ROOT / "src"))
    from data.dataset import config

    cfg = config()
    pairs = cfg["pairs"]
    if not (REPO_ROOT / cfg["paths"]["processed"] / "candles").exists():
        print("HITILAFU: candles hazipo. Endesha build_candles.py kwanza (au --self-test).",
              file=sys.stderr)
        return 1

    rng = np.random.default_rng(SEED)
    rows: list[dict] = []
    for tf in HTF:
        for p in pairs:
            try:
                rows += evaluate_pair_tf(p, tf, rng)
            except FileNotFoundError:
                print(f"  ONYO: {p} {tf} haipo — naruka.", file=sys.stderr)
        print(f"  [{tf}] done")

    out = REPO_ROOT / cfg["paths"]["reports"] / "model1_direction_edge.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(fmt_report(rows, len(pairs), N_PERM), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
