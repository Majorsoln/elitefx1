"""
mt5_data.py — FORWARD TRACK F2: MT5 READ-ONLY data feed (docs/FORWARD_TRACK_CHARTER.md F2).

Chota H1 bars za hivi karibuni (USDCHF/USDJPY) kutoka MetaTrader5 kwa KUSOMA TU, zibadilishe
kuwa features (REUSE market_state_engine — GIGO: forward LAZIMA ilingane na training), andika
forward store <dir>/<SYMBOL>.npz ambayo `live_engine --forward` (F1) inaisoma. Paper — HAKUNA order.

READ-ONLY KABISA (§9.2 half salama ya MT5): market-data pekee — copy_rates + symbols_get + symbol_info.
HAKUNA order-send / order-check / position-modify / account-write (grep-assert kwenye self-test [d]).
Order-execution + token + PD-signature = §9.3 (baadaye, SI hapa).

Chief (2026-07-24): H1-level approximation — spr = rate spread(points)->pips; tc = tick_volume (proxy ya
activity). SI tick-exact. Features (atr/regime) = REUSE _atr(ATR14 Wilder)/_deseason/_reg3 (usivumbue).

Endesha:  python mt5_data.py --out <dir> [--bars N] [--symbols USDCHF USDJPY]
Self-test: python mt5_data.py --self-test   (bila MT5 — mock rows)
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from live_engine import FORWARD_START, _forward_start_epoch
from market_state_engine import pip, state_df

TF = "H1"
H1_SECONDS = 3600
CANON = ("USDCHF", "USDJPY")
_META = "_mt5_meta.json"


# ---------- MT5 seam (READ-ONLY; mock-able) ----------

def _resolve_symbol(symbol, mt5, override=None):
    """USDCHF/USDJPY -> symbol halisi ya broker (handle suffix .m/.raw/.pro). override = config."""
    if override:
        return override
    try:
        syms = [s.name for s in (mt5.symbols_get() or [])]
    except Exception:
        syms = []
    if symbol in syms:
        return symbol
    for s in syms:                                   # base match (EURUSD.m -> EURUSD)
        if s.split(".")[0].upper() == symbol.upper():
            return s
    return symbol                                    # fallback — copy_rates itatoa error kama batili


def _fetch_rates(symbol, n, _mt5=None, override=None):
    """READ-ONLY: H1 bars n za mwisho kupitia mt5.copy_rates_from_pos. Rudisha (rows, point).
    rows = list ya dict {time, open, high, low, close, tick_volume, spread}. Import ya MetaTrader5 = LAZY
    (module i-import bila MT5). _mt5 = injection ya mock kwa self-test."""
    mt5 = _mt5
    if mt5 is None:
        import MetaTrader5 as mt5                     # LAZY — hutegemewa PC ya Operator pekee
        if not mt5.initialize():
            raise RuntimeError(f"mt5.initialize() imeshindwa: {mt5.last_error()}")
    resolved = _resolve_symbol(symbol, mt5, override)
    info = mt5.symbol_info(resolved)
    point = float(getattr(info, "point", pip(symbol) / 10.0)) if info else pip(symbol) / 10.0
    rates = mt5.copy_rates_from_pos(resolved, mt5.TIMEFRAME_H1, 0, int(n))   # SOMA market data (read-only)
    if rates is None or len(rates) == 0:
        raise RuntimeError(f"copy_rates_from_pos({resolved}) haikurudisha data: "
                           f"{getattr(mt5, 'last_error', lambda: '?')()}")
    rows = [dict(time=int(r["time"]), open=float(r["open"]), high=float(r["high"]),
                 low=float(r["low"]), close=float(r["close"]),
                 tick_volume=float(r["tick_volume"]), spread=float(r["spread"]))
            for r in rates]
    return rows, point, resolved


# ---------- rates -> npz arrays (REUSE market_state_engine features) ----------

def rates_to_arrays(rows, sym, point=None):
    """MT5 rows -> arrays za forward store (schema HALISI ya event_quality_report.load_pair, PIP-SPACE).
    REUSE state_df (_atr/_deseason/_reg3) — features SAWASAWA na training (GIGO). H1-approx:
    spr = spread(points) * point / pip; tc = tick_volume. Urefu sawa; dtype sahihi."""
    import polars as pl
    if not rows:
        raise ValueError(f"{sym}: rows tupu (hakuna rates)")
    pp = pip(sym)
    if point is None:
        point = pp / 10.0                            # standard fractional-pip broker (10 points/pip)
    ts = np.array([r["time"] for r in rows], dtype="int64").astype("datetime64[s]")
    df = pl.DataFrame(dict(
        ts=ts.astype("datetime64[us]"),
        o=[float(r["open"]) for r in rows], h=[float(r["high"]) for r in rows],
        l=[float(r["low"]) for r in rows], c=[float(r["close"]) for r in rows],
        tc=[float(r["tick_volume"]) for r in rows],
        spr=[float(r["spread"]) * point / pp for r in rows]))     # spread points -> PIPS
    st = state_df(df, TF)                            # REUSE: atr (price-space), hour, volatility_state
    return dict(
        o=st["o"].to_numpy() / pp, h=st["h"].to_numpy() / pp,
        l=st["l"].to_numpy() / pp, c=st["c"].to_numpy() / pp,
        atr=st["atr"].to_numpy() / pp,
        spr=np.nan_to_num(st["spr"].to_numpy(), nan=0.0),
        tc=st["tc"].to_numpy().astype(float),
        hour=st["hour"].to_numpy().astype(int),
        vol=np.asarray(st["volatility_state"].to_list()),
        ts=ts)                                       # datetime64[s] — live_engine _as_of/candidates


# ---------- write forward store ----------

def write_store(out_dir, symbols=CANON, bars=1500, forward_start=FORWARD_START,
                _fetch=None, overrides=None):
    """Kila sym -> fetch (read-only) -> rates_to_arrays -> np.savez(<dir>/<SYMBOL>.npz).
    GUARD: bars zenye ts >= FORWARD_START PEKEE zinahifadhiwa (features zilihesabiwa na warmup wa
    bars ZOTE zilizochotwa -> trailing windows sahihi; zilizopublishiwa = forward tu §3.1b).
    Provenance -> <dir>/_mt5_meta.json. _fetch(sym, n) -> (rows, point, resolved) [mock kwa self-test]."""
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    fetch = _fetch or (lambda s, n: _fetch_rates(s, n, override=(overrides or {}).get(s)))
    fs_epoch = _forward_start_epoch(forward_start)
    meta = dict(source="MetaTrader5 (read-only copy_rates_from_pos)", tf=TF, approx="H1-approx "
                "(spr=points->pips, tc=tick_volume; SI tick-exact)", forward_start=str(forward_start),
                fetched_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"), symbols={})
    for sym in symbols:
        rows, point, resolved = fetch(sym, bars)
        arrs = rates_to_arrays(rows, sym, point=point)
        keep = arrs["ts"].astype("datetime64[s]").astype("int64") >= fs_epoch   # forward guard
        arrs = {k: v[keep] for k, v in arrs.items()}
        np.savez(str(out / f"{sym}.npz"), **arrs)
        meta["symbols"][sym] = dict(resolved=resolved, point=point, bars_fetched=len(rows),
                                    bars_forward=int(keep.sum()),
                                    first_ts=(int(arrs["ts"][0].astype("datetime64[s]").astype("int64"))
                                              if keep.sum() else None))
    (out / _META).write_text(json.dumps(meta, indent=2, sort_keys=True), encoding="utf-8")
    return meta


# ---------- self-test (bila MT5 — mock rows) ----------

def _mock_rows(sym, n=400, seed=1, start="2026-07-25"):
    """H1 price-bars synthetic (forward era >= FORWARD_START) kwa umbo la MT5 rate rows."""
    from event_library_v2 import _synthetic
    o, h, l_, c, tc, hour = _synthetic(n=n, seed=seed)
    pp = pip(sym); base = 150.0 if "JPY" in sym.upper() else 0.9
    t0 = int(np.datetime64(start, "s").astype("int64"))
    rows = []
    for i in range(n):
        rows.append(dict(time=t0 + i * H1_SECONDS,
                         open=base + float(o[i]) * pp, high=base + float(h[i]) * pp,
                         low=base + float(l_[i]) * pp, close=base + float(c[i]) * pp,
                         tick_volume=float(100 + (i % 50)), spread=10.0))   # 10 points -> ~1 pip
    return rows


def self_test():
    ok = True
    import live_engine as le

    # (a) SCHEMA: rates_to_arrays -> keys kamili, urefu sawa, PIP-SPACE
    rows = _mock_rows("USDCHF", n=400, seed=1)
    arr = rates_to_arrays(rows, "USDCHF")
    keys_need = {"o", "h", "l", "c", "atr", "spr", "tc", "hour", "vol", "ts"}
    lens = {len(arr[k]) for k in keys_need}
    pip_space = (np.nanmedian(arr["c"]) > 100)          # 0.9/0.0001 ~ 9000 -> pip-space (si 0.9 raw)
    schema_ok = (keys_need <= set(arr) and len(lens) == 1 and lens.pop() == len(rows)
                 and arr["ts"].dtype == np.dtype("datetime64[s]") and pip_space
                 and arr["hour"].dtype.kind in "iu")
    print(f"  [a] schema kamili (keys/urefu/pip-space/dtype) -> {schema_ok}")
    ok = ok and schema_ok

    # (b) FORWARD_START guard: mock za sealed era (< FORWARD_START) -> store tupu (0 bars forward)
    import tempfile
    fs_epoch = _forward_start_epoch()
    with tempfile.TemporaryDirectory() as tmp:
        sealed_fetch = lambda s, n: (_mock_rows(s, n=300, seed=1, start="2025-06-01"), pip(s) / 10.0, s)
        m_sealed = write_store(tmp, symbols=("USDCHF",), bars=300, _fetch=sealed_fetch)
        z = np.load(Path(tmp) / "USDCHF.npz", allow_pickle=True)
        guard_ok = (m_sealed["symbols"]["USDCHF"]["bars_forward"] == 0 and len(z["ts"]) == 0)
    print(f"  [b] FORWARD_START guard: sealed-era bars_forward=0 (store tupu) -> {guard_ok}")
    ok = ok and guard_ok

    # (c) ROUND-TRIP: write_store -> live_engine._forward_loader -> run(forward=True) bila error
    with tempfile.TemporaryDirectory() as tmp:
        fwd_fetch = lambda s, n: (_mock_rows(s, n=400, seed=(2 if "JPY" in s else 1)), pip(s) / 10.0, s)
        write_store(tmp, symbols=CANON, bars=400, _fetch=fwd_fetch)
        loader = le._forward_loader(tmp)
        # npz i-load na schema ya load_window (zote zipo, ts forward)
        for sym in CANON:
            w = loader(sym, "H1", "forward")
            assert w is not None and w["ts"] is not None and len(w["ts"]) > 0
            assert (w["ts"].astype("datetime64[s]").astype("int64") >= fs_epoch).all()
        res = le.run(sink=[], _loader=loader, forward=True, watermark=(fs_epoch - 1))
        rt_ok = (res["forward"] and res["skipped_sealed"] == 0 and res["candidates"] >= 0
                 and "log" in res)
    print(f"  [c] round-trip npz->_forward_loader->run(forward): candidates={res['candidates']} "
          f"skipped_sealed=0 (bila error) -> {rt_ok}")
    ok = ok and rt_ok

    # (d) READ-ONLY grep-assert: hakuna order-write / position-modify kwenye CALLS za module.
    # Tokens zimeundwa kwa concatenation ili zisijitokeze kama literal contiguous kwenye faili hii
    # (vinginevyo orodha yenyewe ingejigrep). "_" = W.
    src = Path(__file__).read_text(encoding="utf-8")
    W = "_"
    forbidden = ["order" + W + "send(", "order" + W + "check(", "order" + W + "calc",
                 "." + "order" + W, "positions" + W + "get(", "position" + W + "close",
                 "position" + W + "modify", "Bu" + "y(", "Sel" + "l(", "account" + W + "info_double("]
    hits = [t for t in forbidden if t in src]
    read_only_ok = hits == []
    print(f"  [d] READ-ONLY (hakuna order/position-write CALLS): hits={hits} -> {read_only_ok}")
    ok = ok and read_only_ok

    # (e) DETERMINISM: rates_to_arrays(rows ile ile) -> bit-identical
    a1 = rates_to_arrays(rows, "USDCHF"); a2 = rates_to_arrays(rows, "USDCHF")
    det = all(np.array_equal(a1[k], a2[k]) for k in ("o", "h", "l", "c", "atr", "spr", "tc", "hour", "ts"))
    print(f"  [e] determinism (rates_to_arrays bit-identical) -> {det}")
    ok = ok and det

    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None, help="forward store dir (andika <SYMBOL>.npz)")
    ap.add_argument("--bars", type=int, default=1500, help="H1 bars za mwisho kuchota (warmup + forward)")
    ap.add_argument("--symbols", nargs="+", default=list(CANON))
    ap.add_argument("--forward-start", default=FORWARD_START)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.out:
        print("Tumia --out <dir> (forward store) | --self-test.", file=sys.stderr)
        return 2
    meta = write_store(a.out, symbols=tuple(a.symbols), bars=a.bars, forward_start=a.forward_start)
    for sym, s in meta["symbols"].items():
        print(f"  {sym} ({s['resolved']}): fetched={s['bars_fetched']} forward={s['bars_forward']} "
              f"point={s['point']}")
    print(f"MT5 READ-ONLY store -> {a.out} ({_META} = provenance, H1-approx).")
    print(f"  next: live_engine.py --forward --data {a.out} -> model_steward.py -> dashboard ingest")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
