"""
mt5_data.py — MT5 READ-ONLY feed -> CANONICAL data (Doctrine §8.3; directive ya PD 2026-07-26).

DOCTRINE: MT5 = execution + FEED tu. Feed inasasisha DATA YETU YA KANUNI (canonical state parquet —
data/processed/state/symbol=<SYM>/tf=H1.parquet, ile ile ya training/load_pair) kwa INCREMENT:
bars mpya zilizoFUNGWA tu zinaongezwa (append-only, historia HAIGUSWI), features zinarehesabiwa kwa
state_df ILE ILE (GIGO — forward inalingana na training kwa ujenzi). HAKUNA silo/store ya pembeni.
Sealed window (§3.1b) = SHERIA YA ANALYSIS (engine FORWARD_START guard) — data inaingia canonical,
matumizi ndiyo yanayozuiwa.

READ-ONLY KABISA kwa upande wa MT5 (§9.2): market-data pekee — copy_rates + symbols_get + symbol_info.
HAKUNA order-send / order-check / position-modify / account-write (grep-assert kwenye self-test [d]).
Order-execution + token + PD-signature = §9.3 (baadaye, SI hapa).

Chief (2026-07-24): H1-level approximation — spr = rate spread(points)->pips; tc = tick_volume (proxy ya
activity). SI tick-exact. Features (atr/regime) = REUSE state_df/_atr/_deseason/_reg3 (usivumbue).

Endesha (canonical, default):  python mt5_data.py [--bars N] [--symbols USDCHF USDJPY]
Fixture/debug (npz — SI canonical): python mt5_data.py --out <dir>
Self-test: python mt5_data.py --self-test   (bila MT5 — mock rows)
"""
from __future__ import annotations

import argparse
import json
import os
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


def _fetch_rates(symbol, n, _mt5=None, override=None,
                 mt5_path=None, login=None, password=None, server=None):
    """READ-ONLY: H1 bars n za mwisho kupitia mt5.copy_rates_from_pos. Rudisha (rows, point, resolved).
    rows = list ya dict {time, open, high, low, close, tick_volume, spread}. Import ya MetaTrader5 = LAZY
    (module i-import bila MT5). _mt5 = injection ya mock kwa self-test.

    initialize kwargs: path=mt5_path (kama ipo); login/password/server ZOTE zikiwepo -> login=int(login),
    password, server (SALAMA — password KAMWE kwenye print/log/provenance). -6 'Authorization failed'
    kawaida = terminal ipo lakini haijalogini -> weka ELITEFX_MT5_LOGIN/PASSWORD/SERVER."""
    mt5 = _mt5
    if mt5 is None:
        import MetaTrader5 as mt5                     # LAZY — hutegemewa PC ya Operator pekee
    kwargs = {}
    if mt5_path:
        kwargs["path"] = mt5_path
    if login and password and server:                # creds ZOTE -> logini (SALAMA, si default terminal)
        kwargs["login"] = int(login); kwargs["password"] = password; kwargs["server"] = server
    if not mt5.initialize(**kwargs):
        err = mt5.last_error()                        # HAKUNA password hapa (err = code+ujumbe wa MT5)
        raise RuntimeError(
            f"mt5.initialize() imeshindwa: {err}. Kama -6 (Authorization failed): terminal imepatikana "
            f"lakini haijalogini — weka ENV ELITEFX_MT5_LOGIN / ELITEFX_MT5_PASSWORD / ELITEFX_MT5_SERVER "
            f"(na ELITEFX_MT5_PATH kwa njia ya terminal64.exe kama inahitajika).")
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


# ---------- rates -> bars/arrays (REUSE market_state_engine features) ----------

def _rows_to_bars_df(rows, sym, point=None):
    """MT5 rows -> polars bars df (schema ya canonical: ts,o,h,l,c,tc,spr — price-space; spr PIPS).
    Hii ndiyo lugha ya market_state_engine (h1_from_ticks inatoa muundo uleule kutoka ticks)."""
    import polars as pl
    if not rows:
        raise ValueError(f"{sym}: rows tupu (hakuna rates)")
    pp = pip(sym)
    if point is None:
        point = pp / 10.0                            # standard fractional-pip broker (10 points/pip)
    ts = np.array([r["time"] for r in rows], dtype="int64").astype("datetime64[s]")
    return pl.DataFrame(dict(
        ts=ts.astype("datetime64[us]"),
        o=[float(r["open"]) for r in rows], h=[float(r["high"]) for r in rows],
        l=[float(r["low"]) for r in rows], c=[float(r["close"]) for r in rows],
        tc=[float(r["tick_volume"]) for r in rows],
        spr=[float(r["spread"]) * point / pp for r in rows]))     # spread points -> PIPS


def rates_to_arrays(rows, sym, point=None):
    """MT5 rows -> arrays za fixture store (schema HALISI ya event_quality_report.load_pair, PIP-SPACE).
    REUSE state_df (_atr/_deseason/_reg3) — features SAWASAWA na training (GIGO). H1-approx:
    spr = spread(points) * point / pip; tc = tick_volume. Urefu sawa; dtype sahihi."""
    pp = pip(sym)
    df = _rows_to_bars_df(rows, sym, point=point)
    ts = df["ts"].to_numpy().astype("datetime64[s]")
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
                _fetch=None, overrides=None, _mt5=None,
                mt5_path=None, login=None, password=None, server=None):
    """Kila sym -> fetch (read-only) -> rates_to_arrays -> np.savez(<dir>/<SYMBOL>.npz).
    GUARD: bars zenye ts >= FORWARD_START PEKEE zinahifadhiwa (features zilihesabiwa na warmup wa
    bars ZOTE zilizochotwa -> trailing windows sahihi; zilizopublishiwa = forward tu §3.1b).
    Provenance -> <dir>/_mt5_meta.json. _fetch(sym, n) -> (rows, point, resolved) [mock kwa self-test]."""
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    fetch = _fetch or (lambda s, n: _fetch_rates(
        s, n, _mt5=_mt5, override=(overrides or {}).get(s),
        mt5_path=mt5_path, login=login, password=password, server=server))
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


# ---------- CANONICAL incremental update (Doctrine §8.3 — MT5 feed -> data yetu MOJA) ----------

def _canonical_path(sym, tf=TF):
    """Path ya canonical state parquet (ile ile ya training — latent_structure.state_path)."""
    from latent_structure import state_path                    # lazy (precedent: load_pair)
    return state_path(sym, tf)


def update_canonical(symbols=CANON, bars=1500, _fetch=None, overrides=None, _mt5=None,
                     mt5_path=None, login=None, password=None, server=None,
                     _state_path=None, _now=None):
    """MT5 (read-only) -> APPEND bars mpya zilizoFUNGWA kwenye canonical state parquet (INCREMENT).

    Kanuni (Doctrine §8.3):
      - Historia HAIGUSWI: rows mpya = ts > max(ts iliyopo) TU (append-only). Hakuna rewrite/backfill.
      - Bar inayoundwa SASA (haijafungwa) HAIINGII (closed-bar guard: ts + 1h <= now).
      - Features (atr/deseason/regime) zinarehesabiwa kwa state_df ILE ILE juu ya series nzima
        (deterministic — bars zile zile -> features zile zile; GIGO: forward = training pipeline).
      - Andika ATOMIC (tmp -> replace). Data YOTE inaingia (sealed window pia — §3.1b ni sheria ya
        ANALYSIS: engine FORWARD_START guard ndiyo inayozuia matumizi, si uhifadhi).
    Rudisha meta dict. _state_path(sym)->Path, _now=epoch (za self-test)."""
    import time
    import polars as pl
    fetch = _fetch or (lambda s, n: _fetch_rates(
        s, n, _mt5=_mt5, override=(overrides or {}).get(s),
        mt5_path=mt5_path, login=login, password=password, server=server))
    spath = _state_path or _canonical_path
    now_epoch = int(_now if _now is not None else time.time())
    meta = dict(source="MetaTrader5 (read-only copy_rates_from_pos) -> CANONICAL state parquet",
                tf=TF, doctrine="§8.3 incremental append-only; closed bars only; state_df features",
                approx="H1-approx (spr=points->pips, tc=tick_volume; SI tick-exact)",
                fetched_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"), symbols={})
    canon_cols = ["ts", "o", "h", "l", "c", "atr", "tc", "spr",
                  "volatility_state", "activity_state", "spread_state"]
    for sym in symbols:
        rows, point, resolved = fetch(sym, bars)
        new_bars = _rows_to_bars_df(rows, sym, point=point).with_columns(pl.col("tc").cast(pl.Float64))
        # closed-bar guard: bar ya H1 imefungwa kama open-ts + 1h <= now
        new_bars = new_bars.filter(
            (pl.col("ts").cast(pl.Int64) // 1_000_000 + H1_SECONDS) <= now_epoch)
        p = Path(spath(sym))
        if p.exists():
            old = pl.read_parquet(p)
            old_bars = (old.select(["ts", "o", "h", "l", "c", "tc", "spr"])
                        .with_columns(pl.col("tc").cast(pl.Float64)))
            last = old_bars["ts"].max()
            inc = new_bars.with_columns(pl.col("ts").cast(old_bars.schema["ts"])) \
                          .filter(pl.col("ts") > last)                       # INCREMENT PEKEE
            merged = pl.concat([old_bars, inc.select(old_bars.columns)],
                               how="vertical_relaxed").sort("ts")
            seeded = False
        else:                                                                # seed (PC bila historia)
            inc = new_bars
            merged = new_bars.sort("ts")
            seeded = True
        st = state_df(merged, TF)                                            # features ILE ILE (GIGO)
        out = st.select(canon_cols)
        assert out.height == merged.height                                   # hakuna row kupotea
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".tmp.parquet")
        out.write_parquet(tmp)
        tmp.replace(p)                                                       # atomic
        meta["symbols"][sym] = dict(
            resolved=resolved, point=point, bars_fetched=len(rows), appended=int(inc.height),
            rows_total=int(out.height), seeded=seeded,
            last_ts=(str(out["ts"].max()) if out.height else None), path=str(p))
    mp = Path(spath(symbols[0])).parent.parent / "_mt5_feed_meta.json"
    mp.parent.mkdir(parents=True, exist_ok=True)
    mp.write_text(json.dumps(meta, indent=2, sort_keys=True), encoding="utf-8")
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

    # (f) CONNECTION: initialize inapokea path+login+password+server (SALAMA); password HAIPO kwenye meta
    class _FakeMT5:
        TIMEFRAME_H1 = 16385
        def __init__(self): self.init_kwargs = None
        def initialize(self, **kw): self.init_kwargs = dict(kw); return True
        def last_error(self): return (0, "ok")
        def symbols_get(self): return []
        def symbol_info(self, s): return type("I", (), {"point": pip(s) / 10.0})()
        def copy_rates_from_pos(self, sym, tf, start, n): return _mock_rows(sym, n=int(n))
    fake = _FakeMT5()
    SECRET = "PW-SECRET-9137"
    with tempfile.TemporaryDirectory() as tmp:
        write_store(tmp, symbols=("USDCHF",), bars=120, _mt5=fake,
                    mt5_path="C:/mt5/terminal64.exe", login="12345678",
                    password=SECRET, server="Broker-Demo")
        meta_txt = (Path(tmp) / _META).read_text(encoding="utf-8")
    kw = fake.init_kwargs or {}
    init_ok = (kw.get("path") == "C:/mt5/terminal64.exe" and kw.get("login") == 12345678
               and kw.get("password") == SECRET and kw.get("server") == "Broker-Demo")
    pw_safe = (SECRET not in meta_txt and "password" not in meta_txt.lower())
    conn_ok = init_ok and pw_safe
    print(f"  [f] connection: initialize(path/login/password/server) ok={init_ok}; "
          f"password si kwenye {_META}={pw_safe} -> {conn_ok}")
    ok = ok and conn_ok

    # (g) CANONICAL INCREMENT (Doctrine §8.3): seed -> append mpya TU -> idempotent -> historia
    #     HAIGUSWI -> closed-bar guard (bar inayoundwa haiingii)
    import polars as pl
    all_rows = _mock_rows("USDCHF", n=360, seed=3, start="2026-07-20")
    t_last = all_rows[-1]["time"]
    now_ep = t_last + H1_SECONDS                       # bar ya mwisho imefungwa HASA sasa
    with tempfile.TemporaryDirectory() as tmp:
        spath = lambda sym, tf=TF: Path(tmp) / f"symbol={sym}" / f"tf={tf}.parquet"
        fetch1 = lambda s, n: (all_rows[:300], pip(s) / 10.0, s)
        m1 = update_canonical(symbols=("USDCHF",), _fetch=fetch1, _state_path=spath, _now=now_ep)
        s1 = m1["symbols"]["USDCHF"]
        seed_ok = s1["seeded"] and s1["appended"] == 300 and s1["rows_total"] == 300
        before = pl.read_parquet(spath("USDCHF")).select(["ts", "o", "h", "l", "c"])

        fetch2 = lambda s, n: (all_rows[100:360], pip(s) / 10.0, s)      # overlap 100..300 + mpya 60
        m2 = update_canonical(symbols=("USDCHF",), _fetch=fetch2, _state_path=spath, _now=now_ep)
        s2 = m2["symbols"]["USDCHF"]
        inc_ok = (not s2["seeded"]) and s2["appended"] == 60 and s2["rows_total"] == 360
        after = pl.read_parquet(spath("USDCHF"))
        hist_ok = after.select(["ts", "o", "h", "l", "c"]).head(300).equals(before)   # historia INTACT
        feat_ok = set(["atr", "volatility_state", "activity_state", "spread_state"]) <= set(after.columns)

        m3 = update_canonical(symbols=("USDCHF",), _fetch=fetch2, _state_path=spath, _now=now_ep)
        idem_ok = m3["symbols"]["USDCHF"]["appended"] == 0                # run tena -> +0 (idempotent)

        # closed-bar guard: now = ts ya bar ya mwisho (bado inaundwa) -> bar hiyo HAIINGII
        m4 = update_canonical(symbols=("USDCHF",), _fetch=fetch2, _state_path=spath, _now=t_last)
        closed_ok = m4["symbols"]["USDCHF"]["appended"] == 0 and \
            pl.read_parquet(spath("USDCHF")).height == 360
    canon_ok = seed_ok and inc_ok and hist_ok and feat_ok and idem_ok and closed_ok
    print(f"  [g] canonical increment: seed=300 +60 mpya, historia INTACT={hist_ok}, "
          f"idempotent(+0)={idem_ok}, closed-bar-guard={closed_ok} -> {canon_ok}")
    ok = ok and canon_ok

    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None,
                    help="FIXTURE/DEBUG tu: andika <SYMBOL>.npz (SI canonical; default = canonical)")
    ap.add_argument("--bars", type=int, default=1500, help="H1 bars za mwisho kuchota (warmup + mpya)")
    ap.add_argument("--symbols", nargs="+", default=list(CANON))
    ap.add_argument("--forward-start", default=FORWARD_START, help="(--out fixture path pekee)")
    ap.add_argument("--mt5-path", default=None, help="njia ya terminal64.exe (au ELITEFX_MT5_PATH)")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    # creds/path kutoka ENV (SALAMA — password KAMWE kwenye argv/print/log/meta)
    mt5_path = a.mt5_path or os.environ.get("ELITEFX_MT5_PATH")
    login = os.environ.get("ELITEFX_MT5_LOGIN")
    password = os.environ.get("ELITEFX_MT5_PASSWORD")
    server = os.environ.get("ELITEFX_MT5_SERVER")
    if a.out:                                        # fixture/debug npz (SI canonical)
        meta = write_store(a.out, symbols=tuple(a.symbols), bars=a.bars,
                           forward_start=a.forward_start,
                           mt5_path=mt5_path, login=login, password=password, server=server)
        for sym, s in meta["symbols"].items():
            print(f"  {sym} ({s['resolved']}): fetched={s['bars_fetched']} forward={s['bars_forward']} "
                  f"point={s['point']}")
        print(f"MT5 READ-ONLY fixture store -> {a.out} (SI canonical — Doctrine §8.3 default ni "
              f"bila --out).")
        return 0
    # DEFAULT (Doctrine §8.3): canonical incremental update
    meta = update_canonical(symbols=tuple(a.symbols), bars=a.bars,
                            mt5_path=mt5_path, login=login, password=password, server=server)
    for sym, s in meta["symbols"].items():
        print(f"  {sym} ({s['resolved']}): fetched={s['bars_fetched']} appended={s['appended']} "
              f"rows_total={s['rows_total']} last={s['last_ts']}{' (SEED)' if s['seeded'] else ''}")
    print("MT5 READ-ONLY feed -> CANONICAL state parquet (increment, closed bars; _mt5_feed_meta.json).")
    print("  next: live_engine.py --forward -> model_steward.py -> dashboard ingest")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
