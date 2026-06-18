"""direction_edge.py — Phase B: je MWELEKEO (UP/DOWN) una edge halisi? (Model 1 gate)

Hili ndilo SWALI LA KWANZA la modeler, na onyo kuu la mfumo: Model 1 inatakiwa
itoe mwelekeo (UP/DOWN), LAKINI validation ya features (reports/model1_feature_validation.md)
ilionyesha:
  - next-bar (k=1) directional IC ≈ 0  (hakuna edge wa next-bar)
  - long-horizon (k≥10) raw IC ina SPURIOUS-REGRESSION bias (random walk -> IC -0.15 @ k20)
  -> Hitimisho: jibu definitive linahitaji PERMUTATION test (Sehemu 7, Phase B), sio IC ghafi.

Hati hii inajibu: "Kwa multi-bar holding, je trend-following signal una edge wa MWELEKEO
unaozidi BAHATI?" — KABLA hatujajenga HMM states, Model 1, entries au R6.

## Signals (directional, no-lookahead — past+current TU)
  - price_vs_ema : (close − EMA200) / EMA200   (price juu/chini ya trend filter)
  - ema_slope    : EMA200 / EMA200[t−20] − 1   (mwelekeo wa trend)
  - mom{k}       : close / close[t−k] − 1       (multi-bar momentum, k∈MOM_LOOKBACKS)
Position p_t = sign(signal_t) ∈ {−1, +1}.

## Statistic
Forward return  f_t = log(close_{t+h}/close_t)  kwa holding horizon h, NON-OVERLAPPING
(gather_every(h) — windows zisigongane). Statistic = mean(p_t · f_t) (mean signed return
kwa trade) + directional hit-rate.

## Nulls TATU (kila moja inajibu swali tofauti — robustness kwa kukubaliana)
  1. CIRCULAR-SHIFT (exact, FFT — shifts zote n):
     "Je ALIGNMENT ya wakati kati ya signal na returns ni halisi?" Inazungusha p dhidi ya f;
     inahifadhi persistence ya kila series LAKINI inavunja alignment → null yenyewe ina
     inflation ya spurious-regression → p_shift IMEDE-BIAS drift + autocorrelation. PRIMARY.
  2. RANDOM-DIRECTION (sign-flip, ±1 @ 50/50 — MFUMO "entry za nasibu"):
     "Je mwelekeo unazidi sarafu (coin flip)?" Null inacenter 0; significant = sign inatabiri
     mwelekeo (inajumuisha drift-capture kama edge halali). p_dir.
  3. MOVING-BLOCK BOOTSTRAP (autocorr-robust CI ya effect size):
     Resample blocks za (p,f) → 95% CI ya mean_ret. CI inayoondoa 0 = effect thabiti. boot_p.

Hukumu: STRONG = nulls zote 3 zinakubali; MODERATE = circular-shift + moja; WEAK = moja;
❌ = hakuna. circular-shift (drift-controlled) ndio mwamuzi mkuu wa "skill".

## Matumizi
Data halisi (PC ya Japhet, candles 26GB):  python src/models/direction_edge.py
Synthetic self-test (popote, numpy tu):     python src/models/direction_edge.py --self-test
Inatoa reports/model1_direction_edge.md
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]

HTF = ["D1", "H4", "H2", "H1"]
MOM_LOOKBACKS = [10, 20]
SIGNALS = ["price_vs_ema", "ema_slope"] + [f"mom{k}" for k in MOM_LOOKBACKS]
HORIZONS = {"D1": [3, 5, 10], "H4": [5, 10, 20], "H2": [5, 10, 20], "H1": [6, 12, 24]}
N_PERM = 10_000        # random-direction null
N_BOOT = 2_000         # moving-block bootstrap
MIN_SAMPLES = 60
ALPHA = 0.05
SEED = 7


# ───────────────────────── CORE (numpy tu — testable bila polars) ─────────────────────────

def _clean(sig: np.ndarray, fwd: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Toa NaN na signal==0 (hakuna mwelekeo); rudisha (position ±1, forward return)."""
    m = np.isfinite(sig) & np.isfinite(fwd)
    sig, fwd = sig[m], fwd[m]
    pos = np.sign(sig)
    nz = pos != 0
    return pos[nz], fwd[nz]


def directional_stats(pos: np.ndarray, fwd: np.ndarray) -> dict:
    mean_ret = float(np.mean(pos * fwd))
    nz = fwd != 0
    hit = float(np.mean(np.sign(pos[nz]) == np.sign(fwd[nz]))) if nz.any() else float("nan")
    return dict(mean_ret=mean_ret, hit=hit, drift=float(np.mean(fwd)),
                long_frac=float(np.mean(pos > 0)), n=int(len(pos)))


def circular_shift_pvalue(pos: np.ndarray, fwd: np.ndarray) -> tuple[float, float, float, float]:
    """EXACT one-sided p-value kwa circular shift (shifts ZOTE n) kupitia FFT.

    null[k] = mean(roll(pos,k)·fwd). obs = null[0]. p = #{null ≥ obs}/n (≥ 1/n daima).
    Inadhibiti spurious-regression: persistence ya pos NA fwd inabaki kwenye null.
    """
    n = len(pos)
    if n < 3:
        return float(np.mean(pos * fwd)), float("nan"), float("nan"), float("nan")
    cc = np.fft.irfft(np.fft.rfft(pos) * np.conj(np.fft.rfft(fwd)), n) / n
    null = np.roll(cc[::-1], 1)          # = [mean(roll(pos,k)·fwd) for k in 0..n-1]
    obs = float(null[0])
    p = float(np.sum(null >= obs) / n)
    return obs, p, float(null.mean()), float(null.std())


def random_direction_pvalue(
    pos: np.ndarray, fwd: np.ndarray, n_perm: int = N_PERM, rng: np.random.Generator | None = None
) -> float:
    """One-sided p-value: je mwelekeo unazidi coin-flip (±1 @ 50/50)? (chunked, low-mem)."""
    rng = rng or np.random.default_rng(SEED)
    g = pos * fwd
    obs = float(g.mean())
    n, cnt, done, chunk = len(g), 0, 0, 1000
    while done < n_perm:
        m = min(chunk, n_perm - done)
        flips = rng.choice(np.array([-1.0, 1.0]), size=(m, n))
        cnt += int(np.sum((flips * g).mean(axis=1) >= obs))
        done += m
    return (cnt + 1) / (n_perm + 1)


def block_bootstrap(
    pos: np.ndarray, fwd: np.ndarray, n_boot: int = N_BOOT,
    rng: np.random.Generator | None = None, block: int | None = None
) -> tuple[float, float, float]:
    """Moving-block bootstrap ya mean_ret (autocorr-robust). Rudisha (p_one_sided, ci_lo, ci_hi)."""
    rng = rng or np.random.default_rng(SEED)
    g = pos * fwd
    n = len(g)
    if block is None:
        block = max(2, int(round(n ** (1 / 3))))
    nb = int(np.ceil(n / block))
    ar = np.arange(block)
    means = np.empty(n_boot)
    for b in range(n_boot):
        starts = rng.integers(0, n, size=nb)
        idx = ((starts[:, None] + ar[None, :]).ravel() % n)[:n]
        means[b] = g[idx].mean()
    lo, hi = np.quantile(means, [0.025, 0.975])
    p = (np.sum(means <= 0) + 1) / (n_boot + 1)   # one-sided: edge > 0
    return float(p), float(lo), float(hi)


def _grade(p_shift: float, p_dir: float, ci_lo: float, mean_ret: float) -> str:
    """STRONG/MODERATE/WEAK/none — circular-shift ndio mwamuzi mkuu (drift-controlled)."""
    if mean_ret <= 0:
        return "❌"
    s = p_shift < ALPHA
    others = sum([p_dir < ALPHA, ci_lo > 0])
    if s and others == 2:
        return "STRONG"
    if s and others == 1:
        return "MODERATE"
    if s or others >= 1:
        return "WEAK"
    return "❌"


def evaluate_series(
    sig: np.ndarray, fwd: np.ndarray, n_perm: int = N_PERM, n_boot: int = N_BOOT,
    rng: np.random.Generator | None = None
) -> dict | None:
    rng = rng or np.random.default_rng(SEED)
    pos, fwd = _clean(sig, fwd)
    if len(pos) < MIN_SAMPLES:
        return None
    r = directional_stats(pos, fwd)
    obs, p_shift, nmean, nstd = circular_shift_pvalue(pos, fwd)
    p_dir = random_direction_pvalue(pos, fwd, n_perm, rng)
    boot_p, ci_lo, ci_hi = block_bootstrap(pos, fwd, n_boot, rng)
    r.update(p_shift=p_shift, p_dir=p_dir, boot_p=boot_p, ci_lo=ci_lo, ci_hi=ci_hi,
             null_mean=nmean, null_std=nstd)
    r["grade"] = _grade(p_shift, p_dir, ci_lo, r["mean_ret"])
    return r


# ───────────────────────── DATA PATH (polars/dataset.py — PC ya Japhet) ─────────────────────────

def _build_signals(df):
    """RAW directional predictors (no-lookahead). EMA def. SAWA na feature_validation.py."""
    import polars as pl
    c = pl.col("close")
    df = df.with_columns(c.ewm_mean(span=200, min_samples=200).alias("ema"))
    df = df.with_columns(
        ((pl.col("ema") / pl.col("ema").shift(20)) - 1).alias("ema_slope"),
        ((c - pl.col("ema")) / pl.col("ema")).alias("price_vs_ema"),
    )
    return df.with_columns(
        [((c / c.shift(k)) - 1).alias(f"mom{k}") for k in MOM_LOOKBACKS]
    )


def evaluate_pair_tf(pair: str, tf: str, rng: np.random.Generator) -> list[dict]:
    import polars as pl
    from data.dataset import load_candles

    df = _build_signals(load_candles(pair, tf))
    c = pl.col("close")
    rows = []
    for h in HORIZONS[tf]:
        sk = df.with_columns((c.shift(-h).log() - c.log()).alias("fwd")).gather_every(h)
        for s in SIGNALS:
            x = sk.select([pl.col(s).alias("sig"), pl.col("fwd")]).drop_nulls()
            if x.height < MIN_SAMPLES:
                continue
            res = evaluate_series(x["sig"].to_numpy(), x["fwd"].to_numpy(),
                                  N_PERM, N_BOOT, rng)
            if res is None:
                continue
            res.update(pair=pair, tf=tf, signal=s, h=h)
            rows.append(res)
    return rows


# ───────────────────────── REPORT ─────────────────────────

def _verdict(sub: list[dict]) -> str:
    n = len(sub)
    strong = sum(1 for r in sub if r["grade"] == "STRONG")
    mod = sum(1 for r in sub if r["grade"] == "MODERATE")
    shift_sig = sum(1 for r in sub if r["p_shift"] < ALPHA and r["mean_ret"] > 0)
    exp = ALPHA * n
    if strong + mod == 0:
        return f"❌ HAKUNA edge (0 STRONG/MOD; shift-sig {shift_sig}/{n}, bahati≈{exp:.1f})"
    if strong == 0 and mod <= exp + 1:
        return f"⚠️ shaka ({mod} MOD ≈ bahati {exp:.1f}; 0 STRONG) — multiple-testing"
    return f"✅ edge (STRONG {strong}/{n}, MOD {mod}/{n}; shift-sig {shift_sig}/{n}, bahati≈{exp:.1f})"


def fmt_report(rows: list[dict], npairs: int) -> str:
    L = ["# Model 1 — Directional Edge (Phase B Permutation)\n",
         f"*Imezalishwa: {datetime.now():%Y-%m-%d %H:%M} | nulls 3: circular-shift (exact FFT), "
         f"random-direction (N={N_PERM:,}), moving-block bootstrap (N={N_BOOT:,}) | mean signed "
         f"return, no-lookahead, NON-overlapping | pairs={npairs} | α={ALPHA}*\n",
         "> **Swali:** je trend-following signal una edge wa MWELEKEO kwa multi-bar holding, "
         "unaozidi bahati? Gate KABLA ya HMM states / Model 1 / entries / R6.\n",
         "> **Grade:** STRONG=nulls 3 zote; MODERATE=circular-shift+moja; WEAK=moja; ❌=hakuna. "
         "circular-shift (`p_sh`) = mwamuzi mkuu (drift + spurious-regression controlled).\n"]
    for tf in HTF:
        L.append(f"\n## {tf}\n")
        for s in SIGNALS:
            sub = sorted([r for r in rows if r["tf"] == tf and r["signal"] == s],
                         key=lambda r: (r["h"], r["pair"]))
            if not sub:
                continue
            L.append(f"\n### `{s}`  — {_verdict(sub)}\n")
            L.append("| Pair | h | mean_ret | hit | drift | long% | p_sh | p_dir | "
                     "boot95% CI | grade | n |")
            L.append("|------|---|----------|-----|-------|-------|------|-------|"
                     "------------|-------|---|")
            for r in sub:
                L.append(
                    f"| {r['pair']} | {r['h']} | {r['mean_ret']:+.5f} | {r['hit']:.3f} | "
                    f"{r['drift']:+.5f} | {r['long_frac']:.2f} | **{r['p_shift']:.4f}** | "
                    f"{r['p_dir']:.4f} | [{r['ci_lo']:+.5f},{r['ci_hi']:+.5f}] | "
                    f"{r['grade']} | {r['n']:,} |"
                )
    L.append("\n---\n### Tafsiri & methodolojia\n")
    L.append("- **mean_ret** = mean(sign(signal)·forward_return) kwa trade (non-overlapping). "
             "**p_sh** = circular-shift (exact, shifts zote n): P(null ≥ obs). **p_dir** = "
             "random-direction (coin-flip ±1). **boot CI** = moving-block 95% CI ya mean_ret.")
    L.append("- **Kwa nini nulls 3:** circular-shift inadhibiti drift + spurious-regression "
             "(ndio sababu k≥10 IC haiaminiki) — null yenyewe ina inflation hiyo. "
             "random-direction inajibu 'je sign inazidi sarafu'. bootstrap inathibitisha "
             "effect-size ni thabiti (CI inaondoa 0). **STRONG** = zote zinakubali.")
    L.append("- **drift / long%:** circular-shift ina-account static bias+drift (null μ ≈ "
             "long-bias×drift); kwa hiyo p_sh inapima **direction-timing skill**, sio drift.")
    L.append(f"- **Multiple testing:** kwa α={ALPHA}, tegemea ~{ALPHA*npairs:.1f} significant "
             "KWA BAHATI kwa kila (tf,signal). ✅ inahitaji STRONG/MOD ZAIDI ya hii.")
    L.append("- **Hatua inayofuata:** signal/TF zenye ✅ → chanzo halali cha mwelekeo cha "
             "Model 1. Zikikosekana kote → mwelekeo (UP/DOWN) si tradeable kwa trend-following; "
             "mfumo ufikiriwe upya (vol-regime + symmetric, au mwelekeo chanzo kingine) KABLA "
             "ya kujenga juu yake.")
    return "\n".join(L)


# ───────────────────────── SELF-TEST (synthetic — thibitisha machinery) ─────────────────────────

def self_test() -> int:
    rng = np.random.default_rng(SEED)
    print("SELF-TEST: machinery ya direction_edge — nulls 3 (numpy tu)\n")

    # 1) PLANTED EDGE -> nulls zote 3 zinakubali (STRONG)
    n = 1500
    pos_true = rng.choice([-1.0, 1.0], size=n)
    fwd = pos_true * 0.002 + rng.normal(0, 0.01, n)
    r = evaluate_series(pos_true.copy(), fwd, 3000, 1000, rng)
    print(f"  [1] PLANTED : mean_ret={r['mean_ret']:+.5f} hit={r['hit']:.3f} "
          f"p_sh={r['p_shift']:.4f} p_dir={r['p_dir']:.4f} "
          f"CI=[{r['ci_lo']:+.5f},{r['ci_hi']:+.5f}] grade={r['grade']}")
    assert r["grade"] == "STRONG", r
    assert r["ci_lo"] > 0, r

    # 2) PURE NOISE (spurious-regression case): price-vs-EMA dhidi ya random walk.
    #    FALSE-POSITIVE rate ya STRONG/MOD lazima iwe karibu α — sio kuvimba.
    fp = 0
    trials = 40
    for _ in range(trials):
        price = np.cumsum(rng.normal(0, 0.01, n))
        ema = _ewm(price, 50)
        sig = price - ema
        h = 5
        f = np.full(n, np.nan)
        f[:-h] = price[h:] - price[:-h]
        idx = np.arange(0, n, h)
        rr = evaluate_series(sig[idx], f[idx], 2000, 800, rng)
        if rr is not None and rr["grade"] in ("STRONG", "MODERATE"):
            fp += 1
    rate = fp / trials
    print(f"  [2] NOISE   : STRONG/MOD false-positive = {fp}/{trials} = {rate:.3f} "
          f"(tegemea ~α={ALPHA})")
    assert rate <= 0.20, f"false-positive rate kubwa mno ({rate})"

    print("\n✅ SELF-TEST PASS: planted edge → STRONG (nulls 3); spurious-regression noise "
          "haitoi false positives za kimfumo.")
    return 0


def _ewm(x: np.ndarray, span: int) -> np.ndarray:
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
    out.write_text(fmt_report(rows, len(pairs)), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
