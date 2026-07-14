"""
htf_context.py — C2-0b (MZUNGUKO-2): HTF "BIG-PICTURE" CONTEXT FEATURES (Chief masharti #2).

"HTF big-picture" inatafsiriwa kuwa FEATURES zinazohesabika (si maneno) kutoka H4 na D1 (state
parquet za market_state_engine — zipo tayari):
  trend/slope: ema20_slope (EMA(20) diff ya bars 3, /ATR) · linreg_slope (OLS juu ya closes 20,
               /ATR per bar) · trend_sign (+1/-1/0 na deadband)
  regime:      volatility_state + activity_state (za HTF bar iliyoFUNGWA)
  structure:   resistance = rolling_max(h,20) · support = rolling_min(l,20) (trailing, closed bars);
               dist_res_atr = (res-c)/ATR · dist_sup_atr = (c-sup)/ATR
  momentum:    rsi14 (wilder_rsi — REUSE event_library_v2) · roc10 = c/c[10]-1

ALIGNMENT NGUMU (hatari kuu — LEAKAGE): ts ya HTF bar ya engine ni BUCKET-OPEN time. Kwa kila LTF
bar (open-time t), context LAZIMA itoke kwenye HTF bar ya MWISHO iliyoFUNGWA kabla/kwenye t:
  close_ts = ts + duration(TF)  ->  join_asof(LTF.ts, HTF.close_ts, strategy="backward")
KAMWE bar inayomzunguka t (bado inaendelea — ina future info). Self-test ina MTEGO wa wazi:
H4 bar inayozunguka LTF bar ina spike kubwa; context ya LTF LAZIMA isione spike.

Output: data/processed/context/symbol=<SYM>/tf=<15m|30m>.parquet — kwa kila LTF bar, columns za
h4_* + d1_* TAYARI kwa context-filter ON signals (_mask_context style ya strategy_lab).
Endesha (PC ya data): python src/research/htf_context.py [--symbol X] [--ltf 15m]
Self-test (bila data): python src/research/htf_context.py --self-test
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import polars as pl

from market_state_engine import cfg
from event_library_v2 import wilder_rsi

REPO_ROOT = Path(__file__).resolve().parents[2]
HTF_DURATION = {"H1": timedelta(hours=1), "H2": timedelta(hours=2),
                "H4": timedelta(hours=4), "D1": timedelta(days=1)}
TREND_DEADBAND = 0.02          # |linreg_slope| (ATR/bar) chini ya hii -> trend_sign=0 (flat)
SR_WIN = 20                    # rolling S/R window (closed bars)
EMA_SPAN, EMA_DIFF = 20, 3
LINREG_WIN = 20
ROC_K = 10


def _linreg_slope(c, n=LINREG_WIN):
    """OLS slope ya closes juu ya rolling window n (per bar). Trailing (window inaishia bar hii —
    bar IMEFUNGWA; as-of join ndiyo inahakikisha LTF haioni bar inayoendelea). Vectorized."""
    from numpy.lib.stride_tricks import sliding_window_view
    c = np.asarray(c, float)
    out = np.full(len(c), np.nan)
    if len(c) < n:
        return out
    x = np.arange(n) - (n - 1) / 2.0
    denom = float((x * x).sum())
    out[n - 1:] = sliding_window_view(c, n) @ x / denom
    return out


def htf_features(df: pl.DataFrame, tf: str, prefix: str) -> pl.DataFrame:
    """Features za big-picture kwa KILA HTF bar (computed kwenye CLOSE ya bar — bar imefungwa;
    hakuna rolling ya future). Rudisha close_ts + <prefix>_* columns tayari kwa as-of join."""
    df = df.sort("ts")
    c = df["c"].to_numpy(); h = df["h"].to_numpy(); l = df["l"].to_numpy()
    atr = df["atr"].to_numpy()
    safe_atr = np.where(atr > 0, atr, np.nan)

    ema = pl.Series(c).ewm_mean(span=EMA_SPAN).to_numpy()
    ema_slope = np.full(len(c), np.nan)
    ema_slope[EMA_DIFF:] = (ema[EMA_DIFF:] - ema[:-EMA_DIFF]) / safe_atr[EMA_DIFF:]
    lin = _linreg_slope(c) / safe_atr
    with np.errstate(invalid="ignore"):
        trend_sign = np.where(np.isnan(lin), 0, np.sign(lin) * (np.abs(lin) > TREND_DEADBAND))

    # structure: trailing rolling S/R juu ya closed bars (inclusive ya bar hii — imefungwa)
    from numpy.lib.stride_tricks import sliding_window_view
    res = np.full(len(c), np.nan); sup = np.full(len(c), np.nan)
    if len(c) >= SR_WIN:
        res[SR_WIN - 1:] = sliding_window_view(h, SR_WIN).max(axis=1)
        sup[SR_WIN - 1:] = sliding_window_view(l, SR_WIN).min(axis=1)
    dist_res = (res - c) / safe_atr
    dist_sup = (c - sup) / safe_atr

    rsi = wilder_rsi(c, 14)
    roc = np.full(len(c), np.nan)
    roc[ROC_K:] = c[ROC_K:] / c[:-ROC_K] - 1.0

    out = pl.DataFrame({
        "close_ts": (df["ts"] + HTF_DURATION[tf]),
        f"{prefix}_ema_slope": ema_slope, f"{prefix}_linreg_slope": lin,
        f"{prefix}_trend_sign": trend_sign.astype(np.int8),
        f"{prefix}_vol_state": df["volatility_state"], f"{prefix}_act_state": df["activity_state"],
        f"{prefix}_dist_res_atr": dist_res, f"{prefix}_dist_sup_atr": dist_sup,
        f"{prefix}_rsi14": rsi, f"{prefix}_roc10": roc,
    })
    return out.sort("close_ts")


def align_context(ltf_ts: pl.DataFrame, feats: pl.DataFrame) -> pl.DataFrame:
    """AS-OF BACKWARD join (kiini cha no-lookahead): kwa kila LTF bar open-time t, chukua HTF row
    yenye close_ts kubwa zaidi <= t — bar ya MWISHO iliyoFUNGWA kabla/kwenye t. Bar inayomzunguka
    t ina close_ts > t -> HAIWEZI kuchaguliwa (mtego wa self-test unathibitisha)."""
    return ltf_ts.sort("ts").join_asof(feats, left_on="ts", right_on="close_ts", strategy="backward")


def build(sym, ltf, htfs=("H4", "D1")):
    """Jenga context parquet kwa pair+LTF: soma LTF state bars + HTF state bars (engine iliyopo),
    compute features, as-of join, andika processed/context/symbol=<sym>/tf=<ltf>.parquet."""
    from latent_structure import state_path
    p_ltf = state_path(sym, ltf)
    if not p_ltf.exists():
        return None
    ltf_df = pl.read_parquet(p_ltf).sort("ts")
    out = ltf_df.select("ts")
    for tf in htfs:
        p = state_path(sym, tf)
        if not p.exists():
            return None
        feats = htf_features(pl.read_parquet(p), tf, tf.lower())
        out = align_context(out, feats).drop("close_ts")
    c = cfg()
    dest = REPO_ROOT / c["paths"]["processed"] / "context" / f"symbol={sym}" / f"tf={ltf}.parquet"
    dest.parent.mkdir(parents=True, exist_ok=True)
    out.write_parquet(dest)
    return dest, len(out)


def run(pairs, ltfs=("15m", "30m")):
    done = []
    for sym in pairs:
        for ltf in ltfs:
            r = build(sym, ltf)
            if r is None:
                print(f"  {sym}/{ltf}: state parquet haipo (endesha intraday_state_engine + "
                      "market_state_engine kwanza) — naruka")
                continue
            dest, n = r
            print(f"  {sym}/{ltf}: context bars={n:,} -> {dest.relative_to(REPO_ROOT)}")
            done.append((sym, ltf, n))
    if not done:
        print("HITILAFU: hakuna context iliyojengwa.", file=sys.stderr)
        return 1
    # ongeza sehemu B kwenye report ya C2-0
    c = cfg()
    rep = REPO_ROOT / c["paths"]["reports"] / "cycle2_intraday_htf.md"
    lines = ["\n## B) HTF context features (H4/D1 -> 15m/30m; as-of BACKWARD, no-lookahead)\n",
             f"*{datetime.now():%Y-%m-%d %H:%M} | features: ema_slope/linreg_slope/trend_sign (trend), "
             "vol_state/act_state (regime), dist_res_atr/dist_sup_atr (structure, rolling S/R "
             f"{SR_WIN} closed bars), rsi14/roc10 (momentum) | join: close_ts=ts+duration, backward*\n",
             "| Pair | LTF | context bars |", "|------|-----|--------------|"]
    for sym, ltf, n in done:
        lines.append(f"| {sym} | {ltf} | {n:,} |")
    lines.append("\n*No-lookahead: self-test ya MTEGO (htf_context [2]) inathibitisha context ya LTF "
                 "bar HAIONI HTF bar inayoizunguka (future info) — inatumia bar iliyoFUNGWA kabla.*")
    with open(rep, "a", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\nRipoti (sehemu B imeongezwa): {rep.relative_to(REPO_ROOT)}")
    return 0


# ---------------------------------------------------------------- self-test (bila data)
def _mk_h4(n=200, start=None, spike_at=None):
    """H4 state-bars synthetic (schema ya engine). spike_at: index ya bar yenye SPIKE kubwa
    (h/c mara 2) — mtego wa leakage."""
    start = start or datetime(2020, 1, 6)
    rng = np.random.default_rng(1)
    ts = [start + timedelta(hours=4 * i) for i in range(n)]
    c = 100 + np.cumsum(rng.normal(0, 0.5, n))
    o = np.r_[c[0], c[:-1]]
    h = np.maximum(o, c) + 0.3; l = np.minimum(o, c) - 0.3
    if spike_at is not None:
        c[spike_at] *= 2.0; h[spike_at] = c[spike_at] + 50.0    # spike isiyoweza kupuuzwa
    atr = np.full(n, 1.0)
    return pl.DataFrame(dict(ts=ts, o=o, h=h, l=l, c=c, atr=atr,
                             tc=np.full(n, 100), spr=np.full(n, 1.0),
                             volatility_state=["NORMAL"] * n, activity_state=["NORMAL"] * n,
                             spread_state=["NORMAL"] * n))


def self_test():
    ok = True

    # [1] features sanity: trend halisi (up-drift) -> trend_sign=+1 mwishoni; RSI/ROC finite;
    #     S/R: dist_res>=0 na dist_sup>=0 (res>=c>=sup kwa rolling max/min)
    n = 300
    up = _mk_h4(n)
    upc = up.with_columns(pl.Series("c", 100 + np.arange(n) * 0.5))      # mteremko safi juu
    upc = upc.with_columns([(pl.col("c") + 0.3).alias("h"), (pl.col("c") - 0.3).alias("l")])
    f = htf_features(upc, "H4", "h4")
    tail = f.tail(50)
    t1 = ((tail["h4_trend_sign"] == 1).all()
          and tail["h4_rsi14"].is_finite().all() and tail["h4_roc10"].is_finite().all()
          and (tail["h4_dist_res_atr"] >= -1e-9).all() and (tail["h4_dist_sup_atr"] >= -1e-9).all())
    print(f"  [1] features: up-trend sign=+1, RSI/ROC finite, S/R distances >=0 -> {t1}")
    ok = ok and bool(t1)

    # [2] MTEGO WA LEAKAGE (kiini cha C2-0): LTF bar iko NDANI ya H4 bar yenye SPIKE.
    #     Context ya LTF LAZIMA iwe ya bar iliyoTANGULIA (imefungwa) — isione spike.
    spike_i = 100
    h4 = _mk_h4(200, spike_at=spike_i)
    feats = htf_features(h4, "H4", "h4")
    t_open = h4["ts"][spike_i]                                   # open ya spike bar
    t_inside = t_open + timedelta(minutes=45)                    # LTF bar NDANI ya spike bar
    t_after = t_open + timedelta(hours=4)                        # LTF bar BAADA ya spike bar kufunga
    ltf = pl.DataFrame({"ts": [t_inside, t_after]})
    j = align_context(ltf, feats)
    # row 0 (ndani): lazima close_ts <= t_inside => bar iliyotangulia (close = t_open) — HAKUNA spike
    prev_roc = feats.filter(pl.col("close_ts") == t_open)["h4_roc10"][0]
    spike_roc = feats.filter(pl.col("close_ts") == t_open + timedelta(hours=4))["h4_roc10"][0]
    got_inside = j["h4_roc10"][0]; got_after = j["h4_roc10"][1]
    trap_ok = (abs(got_inside - prev_roc) < 1e-12                # ndani -> bar iliyotangulia ✓
               and abs(got_inside - spike_roc) > 0.1             # HAION I spike (roc ya spike ni kubwa)
               and abs(got_after - spike_roc) < 1e-12)           # baada ya close -> spike bar sasa halali
    print(f"  [2] MTEGO leakage: inside-bar context==prev (roc {got_inside:+.4f}) != spike ({spike_roc:+.4f}); "
          f"after-close==spike -> {trap_ok}")
    ok = ok and trap_ok

    # [2b] boundary hasa: LTF t == close_ts ya bar -> bar hiyo inaruhusiwa (imefungwa KWENYE t)
    j2 = align_context(pl.DataFrame({"ts": [t_open + timedelta(hours=4)]}), feats)
    t2b = abs(j2["h4_roc10"][0] - spike_roc) < 1e-12
    print(f"  [2b] boundary (t == close_ts): bar iliyofungwa KWENYE t inaruhusiwa -> {t2b}")
    ok = ok and t2b

    # [3] D1 duration: close_ts = ts + siku 1 (join haitumii bar ya leo kabla haijafunga)
    d1 = _mk_h4(50)
    d1 = d1.with_columns(pl.Series("ts", [datetime(2020, 1, 6) + timedelta(days=i) for i in range(50)]))
    fd = htf_features(d1, "D1", "d1")
    mid_day = datetime(2020, 2, 10, 13, 0)                       # katikati ya siku ya bar 35
    jd = align_context(pl.DataFrame({"ts": [mid_day]}), fd)
    # bar ya mwisho iliyofungwa kabla ya 2020-02-10 13:00 = bar ya 2020-02-09 (close 02-10 00:00)
    expect = fd.filter(pl.col("close_ts") == datetime(2020, 2, 10))["d1_roc10"][0]
    t3 = abs(jd["d1_roc10"][0] - expect) < 1e-12
    print(f"  [3] D1 as-of (mid-day -> bar ya jana iliyofungwa): {t3}")
    ok = ok and t3

    # [4] determinism + schema: columns zote za h4_/d1_ zinapatikana kwenye build-style join
    ltf_ts = pl.DataFrame({"ts": [t_open + timedelta(minutes=15 * k) for k in range(20)]})
    a = align_context(ltf_ts, feats); b = align_context(ltf_ts, feats)
    t4 = a.equals(b) and all(col in a.columns for col in
                             ["h4_ema_slope", "h4_linreg_slope", "h4_trend_sign", "h4_vol_state",
                              "h4_act_state", "h4_dist_res_atr", "h4_dist_sup_atr", "h4_rsi14", "h4_roc10"])
    print(f"  [4] determinism + schema kamili -> {t4}")
    ok = ok and t4

    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default=None)
    ap.add_argument("--ltf", default=None, choices=["15m", "30m"])
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    pairs = [a.symbol] if a.symbol else cfg()["pairs"]
    return run(pairs, (a.ltf,) if a.ltf else ("15m", "30m"))


if __name__ == "__main__":
    raise SystemExit(main())
