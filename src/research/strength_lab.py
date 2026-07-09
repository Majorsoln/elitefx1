"""
strength_lab.py — CURRENCY STRENGTH framework (Cycle-2 H-C2-5; Chief spec-light, 2026-07-09).

Wazo: pairs hazitembei peke yake — currency MOJA (USD) inaposimama/kudhoofika, inasukuma pairs zake
zote. `usd_drift` = event linalotumia USD STRENGTH INDEX (trailing returns za USD dhidi ya wenzake)
kutoa signal kwa kila USD pair kulingana na upande wa USD (base au quote).

MKATABA:
  usd_strength(closes_by_pair, window) -> array: wastani wa trailing returns za USD (base=+r, quote=-r).
    NO-LOOKAHEAD: thamani ya i inatumia closes <= i TU (trailing window).
  usd_drift(pair, usd_str, k, rearm) -> {"sig"}: edge-triggered. base-USD (USDJPY): long USD ikisimama;
    quote-USD (EURUSD): short pair USD ikisimama (USD up = EURUSD down). Threshold = k×std(usd_str).
  Backtest: episodes() ya event_quality_report (fill rules ZILIZOKAGULIWA; costs kila trade). SIBADILISHI.

HII NI EXPLORATION (inalisha grid; SIO edge claim). TRAIN in-sample; uthibitisho = S2/S3. Pairs zisizo
na USD (EURJPY/EURGBP) hazishiriki. Reuse: event_library_v2 (_edge, _roll, wilder_atr),
event_quality_report (episodes, _metrics).
Self-test (bila data): python strength_lab.py --self-test
"""
from __future__ import annotations

import argparse
import sys

import numpy as np

from event_library_v2 import _edge, _roll, wilder_atr
from event_quality_report import episodes, _metrics


def _is_usd(pair):
    return "USD" in pair.upper()


def _base_is_usd(pair):
    return pair.upper().startswith("USD")


def usd_strength(closes_by_pair, window=20):
    """USD strength index: wastani (kwa USD pairs) wa trailing return ya USD. base-USD => +r;
    quote-USD => -r (pair up = USD down). NO-LOOKAHEAD: r[i] = c[i]/c[i-window]-1 (closes <= i)."""
    usd_pairs = {p: c for p, c in closes_by_pair.items() if _is_usd(p)}
    if not usd_pairs:
        raise ValueError("hakuna USD pair kwenye closes_by_pair")
    n = len(next(iter(usd_pairs.values())))
    mat = []
    for p, c in usd_pairs.items():
        c = np.asarray(c, float)
        r = np.full(n, np.nan)
        r[window:] = c[window:] / c[:-window] - 1.0        # trailing return (no-lookahead)
        mat.append(r if _base_is_usd(p) else -r)           # orientation: USD kama base au quote
    import warnings
    with warnings.catch_warnings():                        # bars za kwanza `window` = NaN zote (sawa)
        warnings.simplefilter("ignore", category=RuntimeWarning)
        return np.nanmean(np.vstack(mat), axis=0)


def usd_drift(pair, usd_str, k=1.0, std_win=50, rearm=10):
    """Signal ya usd_drift kwa USD pair. USD ikisimama (usd_str > k×std) -> fuata USD kwenye pair hii.
    base-USD (USDJPY): long; quote-USD (EURUSD): short. Edge-triggered + rearm. NO-LOOKAHEAD."""
    n = len(usd_str)
    if not _is_usd(pair):
        return {"sig": np.zeros(n, dtype=int)}             # non-USD pair haishiriki
    sd = _roll(usd_str, std_win, np.std, incl=True)        # trailing std (incl bar i; <= i)
    with np.errstate(invalid="ignore"):
        strong = usd_str > k * sd                          # USD inasimama
        weak = usd_str < -k * sd                           # USD inadhoofika
    if _base_is_usd(pair):                                 # USDxxx: USD strong -> pair up -> long
        long_c, short_c = strong, weak
    else:                                                  # xxxUSD: USD strong -> pair down -> short
        long_c, short_c = weak, strong
    return {"sig": _edge(long_c, short_c, rearm)}


def backtest_pair(pair, usd_str, o, h, l, c, atr, spr, hour, vol=None, k=1.0, sl_atr=1.5, tp_atr=1.5):
    """usd_drift -> episodes() (market entry; costs). Rudisha list ya pnl (pips)."""
    out = usd_drift(pair, usd_str, k=k)
    trs = episodes(out, "market", o, h, l, c, atr, spr, hour, vol, sl_atr=sl_atr, tp_atr=tp_atr)
    return [t[3] for t in trs]


# ---------- run (data ya Operator) ----------
def run(pairs, tf, k=1.0):
    from market_state_engine import cfg, pip
    from latent_structure import state_path
    import polars as pl
    from datetime import datetime, timezone
    TRAIN_END = datetime(2023, 1, 1)
    frames = {}
    for sym in pairs:
        p = state_path(sym, tf)
        if not p.exists():
            continue
        df = pl.read_parquet(p).sort("ts").filter(pl.col("ts") < TRAIN_END)
        if df.height >= 500:
            frames[sym] = df
    usd_syms = [s for s in frames if _is_usd(s)]
    if len(usd_syms) < 2:
        print("HITILAFU: USD pairs pungufu (>=2 zinahitajika). Endesha market_state_engine.py.", file=sys.stderr)
        return 1
    # align kwa ts (inner join) ili strength iwe cross-sectional sahihi
    base = frames[usd_syms[0]].select("ts")
    for s in usd_syms[1:]:
        base = base.join(frames[s].select("ts"), on="ts", how="inner")
    ts_keep = base.sort("ts")["ts"]
    closes = {}
    aligned = {}
    for s in usd_syms:
        d = frames[s].join(pl.DataFrame({"ts": ts_keep}), on="ts", how="inner").sort("ts")
        pp = pip(s)
        closes[s] = d["c"].to_numpy() / pp
        aligned[s] = d
    ustr = usd_strength(closes)
    from datetime import datetime as _dt
    L = ["# Currency Strength (usd_drift) — TRAIN TU (Cycle-2 H-C2-5)\n",
         f"*{_dt.now():%Y-%m-%d %H:%M} | TF={tf} | USD pairs={len(usd_syms)} | k={k} | costs ndani | "
         "EXPLORATION (in-sample) — uthibitisho S2/S3. Profitable != Tradable Edge.*\n",
         "| pair | N | EV net (pips) | win% | PF |", "|------|---|---------------|------|----|"]
    for s in usd_syms:
        d = aligned[s]; pp = pip(s)
        pn = backtest_pair(s, ustr, d["o"].to_numpy() / pp, d["h"].to_numpy() / pp,
                           d["l"].to_numpy() / pp, d["c"].to_numpy() / pp, d["atr"].to_numpy() / pp,
                           np.nan_to_num(d["spr"].to_numpy(), nan=0.0), d["ts"].dt.hour().to_numpy(),
                           np.asarray(d["volatility_state"].to_list()), k=k)
        m = _metrics(pn)
        if m["n"] >= 30:
            L.append(f"| {s} | {m['n']:,} | {m['ev']:+.3f} | {m['win']*100:.1f} | {m['pf']:.2f} |")
        else:
            L.append(f"| {s} | <30 | — | — | — |")
    from pathlib import Path
    out = Path(__file__).resolve().parents[2] / "reports" / "strength_lab_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"Ripoti: {out}")
    return 0


# ---------- self-test (bila data) ----------
def _synth_usd(n=2000, seed=0):
    """Closes za USD pairs ambapo USD ina-trend (rising) thabiti -> strength chanya inayojulikana
    (signal > noise). base-USD zinapanda; quote-USD zinashuka (USD up = pair down)."""
    rng = np.random.default_rng(seed)
    usd_trend = np.linspace(0.0, 0.10, n)                                  # USD inasimama kwa kasi thabiti
    closes = {}
    for p in ("EURUSD", "GBPUSD", "USDJPY", "USDCHF"):
        noise = np.cumsum(rng.normal(0, 0.0002, n))                        # noise < signal
        if _base_is_usd(p):
            base = 100.0 if p.endswith("JPY") else 1.0
            closes[p] = base * (1 + usd_trend + noise)
        else:
            closes[p] = 1.10 * (1 - usd_trend + noise)                     # quote-USD: USD up -> pair down
    return closes


def self_test():
    ok = True
    closes = _synth_usd()
    n = len(closes["EURUSD"])

    # [1] usd_strength: USD ina-trend up thabiti -> strength chanya baada ya warmup
    us = usd_strength(closes, window=20)
    m_late = np.nanmean(us[100:])
    s_ok = np.isfinite(m_late) and m_late > 0
    print(f"  [1] usd_strength (USD rising): mean(after-warmup)={m_late:+.5f} > 0 -> {s_ok}")
    ok = ok and s_ok

    # [1b] NO-LOOKAHEAD: usd_strength(prefix) == usd_strength(full)[:len(prefix)] (trailing tu)
    us_pre = usd_strength({p: c[:1000] for p, c in closes.items()}, window=20)
    nolook = np.allclose(us_pre, us[:1000], equal_nan=True)
    print(f"  [1b] no-lookahead (truncation invariance): {nolook}")
    ok = ok and nolook

    # [2] usd_drift orientation: USDJPY (base) long-bias; EURUSD (quote) short-bias (USD inasimama)
    sig_jpy = usd_drift("USDJPY", us, k=0.5)["sig"]
    sig_eur = usd_drift("EURUSD", us, k=0.5)["sig"]
    mask = np.arange(n) >= 100
    jpy_long = int((sig_jpy[mask] == 1).sum()); jpy_short = int((sig_jpy[mask] == -1).sum())
    eur_long = int((sig_eur[mask] == 1).sum()); eur_short = int((sig_eur[mask] == -1).sum())
    orient_ok = jpy_long > jpy_short and eur_short > eur_long and (jpy_long + eur_short) > 0
    print(f"  [2] orientation (USD strong): USDJPY long={jpy_long}/short={jpy_short}; EURUSD long={eur_long}/short={eur_short} -> {orient_ok}")
    ok = ok and orient_ok

    # [3] non-USD pair -> hakuna signal
    non_usd = (usd_drift("EURJPY", us)["sig"] == 0).all()
    print(f"  [3] non-USD (EURJPY) -> zero signal: {non_usd}")
    ok = ok and non_usd

    # [4] backtest_pair -> episodes na costs (edge-triggered -> episodes chache, gaps > rearm)
    rng = np.random.default_rng(1)
    c = closes["USDJPY"] / (0.01)                                  # -> pips
    o = np.roll(c, 1); o[0] = c[0]
    sp = np.abs(rng.normal(0, 5, n))
    h = np.maximum(o, c) + sp; l = np.minimum(o, c) - sp
    atr = np.maximum(h - l, 1.0); spr = np.full(n, 1.0); hour = np.arange(n) % 24
    pn = backtest_pair("USDJPY", us, o, h, l, c, atr, spr, hour, k=0.5)
    bt_ok = len(pn) > 0
    print(f"  [4] backtest_pair (episodes+costs): trades={len(pn)} EV={np.mean(pn):+.3f} -> {bt_ok}")
    ok = ok and bt_ok

    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Currency strength (usd_drift) — Cycle-2")
    ap.add_argument("--tf", default="H1")
    ap.add_argument("--k", type=float, default=1.0)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    from market_state_engine import cfg
    return run(cfg()["pairs"], a.tf, a.k)


if __name__ == "__main__":
    raise SystemExit(main())
