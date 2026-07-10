"""
strat_signal.py — S4 SIGNAL TOOL kwa strategies PROVEN-OOS (Chief S4 + UPDATE 2026-07-09).

STRAT-001 (nr7_break × USDCHF H1 · SL 2.0×ATR / TP 1.0×ATR · no-LATE · PROVEN-OOS, S3)
STRAT-002 (nr7_break × USDJPY H1 · SL 1.0×ATR / TP 1.0×ATR · no-LATE · PROVEN-OOS, S3b)

Inasoma bars za hivi karibuni (parquet/CSV), inagundua NR7 kwenye bar ILIYOFUNGA (REUSE
event_library_v2.nr7_break + wilder_atr — HAKUNA math mpya), inatoa pending OCO stop-orders
(buy-stop high+0.1pip / sell-stop low−0.1pip; SL/TP za ATR) katika format ya `paper_trader --signal`.
Operator anaweka orders MT5; ikijaza, anaendesha paper_trader (decide→gate FTMO→size→fill→log E3).

MKATABA: bars ziko PRICE; ndani zinabadilishwa PIPS (nr7/atr contract) kisha levels->PRICE.
no-LATE: entry = bar INAYOFUATA (hour+1); ikiwa 17-23 -> skip (filter ya strategy, decidable ex-ante).
NR7 pending = bar MOJA tu (episodes(): stop hufill bar i+1 pekee). Provenance: strategy_lab S1-S3.
NO pesa, NO network. Self-test na bars synthetic.
Endesha: python strat_signal.py --pair USDCHF --bars <path>   |   --all --bars-dir <dir>
Self-test: python strat_signal.py --self-test
"""
from __future__ import annotations

import argparse
import sys

import numpy as np

from event_library_v2 import nr7_break, wilder_atr

# REGISTRY ya strategies PROVEN-OOS (SL/TP kwa ATR units; no_late=True; atr_len 14; nr7 n=7)
STRATEGIES = {
    "STRAT-001": dict(pair="USDCHF", sl_atr=2.0, tp_atr=1.0, no_late=True, atr_len=14, nr7_n=7,
                      provenance="S3 holdout N=303 EV+1.92 win73.9% p=0.021"),
    "STRAT-002": dict(pair="USDJPY", sl_atr=1.0, tp_atr=1.0, no_late=True, atr_len=14, nr7_n=7,
                      provenance="S3b holdout N=327 EV+2.65 win57.8% p=0.029"),
}
LATE_HOURS = set(range(17, 24))          # no-LATE = entry hour 17-23 skip (event_quality_report SESSIONS)


def _pip_size(pair):
    p = pair.upper()
    if p.startswith("XAU"):                   # gold: pip=0.01 (C2 addendum)
        return 0.01
    return 0.01 if p.endswith("JPY") else 0.0001


def _dec(pair):
    p = pair.upper()
    if p.startswith("XAU"):                   # gold quote = 2dp
        return 2
    return 3 if p.endswith("JPY") else 5


def pending_orders(o, h, l, c, hour, pair, strat):
    """Rudisha pending OCO orders kwa bar ILIYOFUNGA ya mwisho (PRICE). [] kama hakuna NR7 au no-LATE.
    Kila order = dict(side, entry, sl, tp). REUSE nr7_break + wilder_atr (pips internally)."""
    ps = _pip_size(pair)
    o_p, h_p, l_p, c_p = (np.asarray(x, float) / ps for x in (o, h, l, c))
    if len(c_p) < max(strat["nr7_n"], strat["atr_len"]) + 1:
        return []
    lv = nr7_break(o_p, h_p, l_p, c_p, n=strat["nr7_n"])
    atr = wilder_atr(h_p, l_p, c_p, strat["atr_len"])
    i = len(c_p) - 1                                   # bar iliyofunga ya mwisho
    a = atr[i]
    if not (a > 0):
        return []
    if strat["no_late"] and (int(hour[i]) + 1) % 24 in LATE_HOURS:   # entry = bar ijayo (hour+1)
        return []
    orders = []
    d = _dec(pair)
    if np.isfinite(lv["long_level"][i]):               # buy-stop
        e = lv["long_level"][i]
        orders.append(dict(side="BUY", entry=round(e * ps, d),
                           sl=round((e - strat["sl_atr"] * a) * ps, d),
                           tp=round((e + strat["tp_atr"] * a) * ps, d)))
    if np.isfinite(lv["short_level"][i]):              # sell-stop
        e = lv["short_level"][i]
        orders.append(dict(side="SELL", entry=round(e * ps, d),
                           sl=round((e + strat["sl_atr"] * a) * ps, d),
                           tp=round((e - strat["tp_atr"] * a) * ps, d)))
    return orders


def load_bars(path, pair):
    """Soma bars za hivi karibuni (PRICE). parquet (state format: o/h/l/c/ts) au CSV (o,h,l,c,ts/hour)."""
    if str(path).endswith(".parquet"):
        import polars as pl
        df = pl.read_parquet(path).sort("ts")
        return dict(o=df["o"].to_numpy(), h=df["h"].to_numpy(), l=df["l"].to_numpy(),
                    c=df["c"].to_numpy(), hour=df["ts"].dt.hour().to_numpy())
    import csv
    from datetime import datetime
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    def col(r, *names):
        for nm in names:
            if nm in r:
                return r[nm]
        raise KeyError(f"CSV inakosa column {names}")
    o = np.array([float(col(r, "o", "open")) for r in rows])
    h = np.array([float(col(r, "h", "high")) for r in rows])
    l = np.array([float(col(r, "l", "low")) for r in rows])
    c = np.array([float(col(r, "c", "close")) for r in rows])
    try:
        hour = np.array([int(col(r, "hour")) for r in rows])
    except KeyError:
        hour = np.array([datetime.fromisoformat(col(r, "ts", "time", "timestamp")).hour for r in rows])
    return dict(o=o, h=h, l=l, c=c, hour=hour)


def _print_strat(name, strat, bars):
    orders = pending_orders(bars["o"], bars["h"], bars["l"], bars["c"], bars["hour"],
                            strat["pair"], strat)
    hdr = (f"{name} (nr7_break × {strat['pair']} H1 · SL{strat['sl_atr']}/TP{strat['tp_atr']} ATR · "
           f"no-LATE · PROVEN-OOS [{strat['provenance']}])")
    print(hdr)
    if not orders:
        print("  hakuna NR7 signal kwenye bar ya mwisho (au no-LATE) -> HAKUNA order")
        return
    for od in orders:
        stop = "BUY-STOP" if od["side"] == "BUY" else "SELL-STOP"
        print(f"  {stop}: place kwa MT5, kisha ikijaza:")
        print(f"    python paper_trader.py --signal {strat['pair']} {od['side']} "
              f"{od['entry']} {od['sl']} {od['tp']}")
    print("  (OCO: place zote mbili; ikijaza moja, futa nyingine. Halali bar MOJA tu.)")


# ---------- self-test (bars synthetic) ----------
def _make_nr7_bars(pair="USDCHF", last_hour=10, n=30, seed=0):
    """Bars za PRICE ambapo bar ya mwisho ni NR7 (range nyembamba zaidi ya 7) + ATR halali."""
    rng = np.random.default_rng(seed)
    ps = _pip_size(pair)
    base = 0.9000 if pair == "USDCHF" else 145.00
    c = base + np.cumsum(rng.normal(0, 10 * ps, n))
    o = np.roll(c, 1); o[0] = c[0]
    wide = 30 * ps + np.abs(rng.normal(0, 10 * ps, n))
    h = np.maximum(o, c) + wide
    l = np.minimum(o, c) - wide
    # lazimisha bar ya mwisho iwe NR7: range nyembamba SANA
    h[-1] = max(o[-1], c[-1]) + 2 * ps
    l[-1] = min(o[-1], c[-1]) - 2 * ps
    hour = ((np.arange(n) + last_hour - (n - 1)) % 24).astype(int)
    return dict(o=o, h=h, l=l, c=c, hour=hour)


def self_test():
    ok_all = True

    # [1] REGISTRY: strategies 2, params sahihi za STRAT-001/002 (nr7 + no-LATE)
    ok = (set(STRATEGIES) == {"STRAT-001", "STRAT-002"}
          and STRATEGIES["STRAT-001"]["pair"] == "USDCHF" and STRATEGIES["STRAT-001"]["sl_atr"] == 2.0
          and STRATEGIES["STRAT-002"]["pair"] == "USDJPY" and STRATEGIES["STRAT-002"]["tp_atr"] == 1.0
          and all(s["no_late"] for s in STRATEGIES.values()))
    ok_all &= ok
    print(f"[1] registry (STRAT-001 USDCHF SL2/TP1, STRAT-002 USDJPY SL1/TP1, no-LATE) -> {'OK' if ok else 'FAIL'}")

    # [2] NR7 bar -> OCO orders (buy-stop juu, sell-stop chini); SL/TP zinafuata direction
    bars = _make_nr7_bars("USDCHF", last_hour=10)
    ods = pending_orders(bars["o"], bars["h"], bars["l"], bars["c"], bars["hour"], "USDCHF",
                         STRATEGIES["STRAT-001"])
    by = {o["side"]: o for o in ods}
    buy_ok = "BUY" in by and by["BUY"]["entry"] > by["BUY"]["sl"] and by["BUY"]["tp"] > by["BUY"]["entry"]
    sell_ok = "SELL" in by and by["SELL"]["entry"] < by["SELL"]["sl"] and by["SELL"]["tp"] < by["SELL"]["entry"]
    ok = buy_ok and sell_ok
    ok_all &= ok
    print(f"[2] NR7->OCO: buy(entry>sl,tp>entry)={buy_ok} sell(entry<sl,tp<entry)={sell_ok} orders={len(ods)} -> {'OK' if ok else 'FAIL'}")

    # [2b] SL distance = 2×ATR kwa STRAT-001 (TP = 1×ATR); ratio SL/TP = 2.0 (long)
    if "BUY" in by:
        sl_d = by["BUY"]["entry"] - by["BUY"]["sl"]; tp_d = by["BUY"]["tp"] - by["BUY"]["entry"]
        ratio_ok = abs(sl_d / tp_d - 2.0) < 0.05
    else:
        ratio_ok = False
    ok_all &= ratio_ok
    print(f"[2b] STRAT-001 SL/TP = 2.0×ATR/1.0×ATR (ratio {sl_d/tp_d:.2f}) -> {'OK' if ratio_ok else 'FAIL'}")

    # [3] no-LATE: bar ya mwisho hour=16 -> entry hour 17 (LATE) -> HAKUNA order
    bars_late = _make_nr7_bars("USDCHF", last_hour=16)
    ods_late = pending_orders(bars_late["o"], bars_late["h"], bars_late["l"], bars_late["c"],
                              bars_late["hour"], "USDCHF", STRATEGIES["STRAT-001"])
    ok = len(ods_late) == 0
    ok_all &= ok
    print(f"[3] no-LATE filter (entry hour 17 -> skip): orders={len(ods_late)} -> {'OK' if ok else 'FAIL'}")

    # [4] non-NR7 bar (range pana ya mwisho) -> HAKUNA order
    bars2 = _make_nr7_bars("USDCHF", last_hour=10, seed=2)
    ps = _pip_size("USDCHF")
    bars2["h"][-1] = max(bars2["o"][-1], bars2["c"][-1]) + 200 * ps   # bar pana -> si NR7
    bars2["l"][-1] = min(bars2["o"][-1], bars2["c"][-1]) - 200 * ps
    ods2 = pending_orders(bars2["o"], bars2["h"], bars2["l"], bars2["c"], bars2["hour"], "USDCHF",
                          STRATEGIES["STRAT-001"])
    ok = len(ods2) == 0
    ok_all &= ok
    print(f"[4] non-NR7 bar -> no order: orders={len(ods2)} -> {'OK' if ok else 'FAIL'}")

    # [5] JPY pip scaling: STRAT-002 USDJPY -> entry ~145, prices zenye 3 decimals
    barsj = _make_nr7_bars("USDJPY", last_hour=10)
    odsj = pending_orders(barsj["o"], barsj["h"], barsj["l"], barsj["c"], barsj["hour"], "USDJPY",
                          STRATEGIES["STRAT-002"])
    ok = len(odsj) > 0 and 100 < odsj[0]["entry"] < 200
    ok_all &= ok
    print(f"[5] USDJPY pip scaling (entry ~145): {odsj[0]['entry'] if odsj else None} -> {'OK' if ok else 'FAIL'}")

    # [6] METALS (C2 addendum): _pip_size/_dec za XAUUSD (2dp, pip 0.01); FX haijavunjika
    xau_ok = (_pip_size("XAUUSD") == 0.01 and _dec("XAUUSD") == 2
              and _pip_size("EURUSD") == 0.0001 and _dec("EURUSD") == 5
              and _pip_size("USDJPY") == 0.01 and _dec("USDJPY") == 3)
    ok_all &= xau_ok
    print(f"[6] metals pip scaling: XAUUSD pip={_pip_size('XAUUSD')} dec={_dec('XAUUSD')} (FX intact) -> {'OK' if xau_ok else 'FAIL'}")

    print("SELF-TEST:", "PASS" if ok_all else "FAIL")
    return 0 if ok_all else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Signal tool kwa strategies PROVEN-OOS (S4)")
    ap.add_argument("--pair", default=None, help="USDCHF au USDJPY (strategy moja)")
    ap.add_argument("--all", action="store_true", help="strategies zote")
    ap.add_argument("--bars", default=None, help="path ya bars (parquet/CSV) kwa --pair")
    ap.add_argument("--bars-dir", default=None, help="dir yenye <PAIR>.parquet kwa --all")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.all:
        if not a.bars_dir:
            print("--all inahitaji --bars-dir <dir yenye USDCHF.parquet, USDJPY.parquet>")
            return 1
        import os
        for name, strat in STRATEGIES.items():
            p = os.path.join(a.bars_dir, f"{strat['pair']}.parquet")
            if not os.path.exists(p):
                print(f"{name}: {p} haipo -> naruka"); continue
            _print_strat(name, strat, load_bars(p, strat["pair"]))
        return 0
    if a.pair and a.bars:
        pair = a.pair.upper()
        strat = next((s for s in STRATEGIES.values() if s["pair"] == pair), None)
        name = next((n for n, s in STRATEGIES.items() if s["pair"] == pair), None)
        if strat is None:
            print(f"hakuna strategy PROVEN kwa {pair} (zilizopo: USDCHF, USDJPY)")
            return 1
        _print_strat(name, strat, load_bars(a.bars, pair))
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
