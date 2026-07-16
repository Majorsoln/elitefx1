"""
rmap.py — M3-1 (MZUNGUKO-3, TABAKA 2): R-MAP behavioral ATLAS + swap model + MFE/MAE exit-science.

RAMANI YA TABIA (charter docs/CYCLE3_CHARTER.md §Tabaka-2): events 21 za EVENTS_V2 × pairs 12 ×
TF {H1,H4,D1} × grid ndogo (SL {1.0,1.5,2.0} × TP {1.0,1.5,2.0,3.0}), kila TRADE ikiwa TAGGED na
mazingira ya SIGNAL bar (vol_state, session, d1/h4 trend_sign kama ctx ipo, mwaka). Output = ATLAS
compact (mstari 1 kwa CELL×MWAKA×VOL_STATE) + report ya breadth (L-041: pairs NGAPI, si cell moja).

NIDHAMU (charter §Kinga): ATLAS = TRAIN PEKEE (guard PermissionError); VALIDATION/HOLDOUT KAMWE.
Atlas ni RAMANI, si madai — hypothesis yoyote inapita gate ile ile (S2 pooled → HOLDOUT). HAKUNA
FDR hapa kwa makusudi (si hypothesis test). Costs halisi ndani ya episodes + SWAP (swing carry).

ADDITIVE: episodes/pvalue_boot/_mask_context* HAZIGUSWI. apply_swap na excursions ni WRAPPERS juu
ya trade tuples za episodes (golden hashes za episodes zinabaki byte-identical).

Endesha (PC ya data): python rmap.py --train        (nzito — run overnight; kadirio linachapishwa)
Self-test (bila data):  python rmap.py --self-test
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np

from event_library_v2 import EVENTS_V2, _synthetic
from event_quality_report import episodes, _sess, SLIP_MARKET, SLIP_STOP
from strategy_lab import load_window

REPO_ROOT = Path(__file__).resolve().parents[2]
ALL_TFS = ("H1", "H4", "D1")
SLS = (1.0, 1.5, 2.0)
TPS = (1.0, 1.5, 2.0, 3.0)
MAX_HOLD = {"H1": 24, "H4": 24, "D1": 20}            # charter: H1/H4 bars 24, D1 bars 20 (~wiki 4)
SWAP_DEFAULT = 0.5                                    # conservative fallback (pips/night)
AVAIL_KEYS = {"hour", "tc"}                           # data zinazopatikana kwa event fn (kando ya OHLC)
OUT_PARQUET = "rmap_train.parquet"
OUT_REPORT = "rmap_atlas.md"


def usable_events():
    """Events zote za EVENTS_V2 zenye `needs` zinazopatikana (hour/tc zipo; OHLC daima)."""
    return [e for e, s in EVENTS_V2.items() if all(k in AVAIL_KEYS for k in s["needs"])]


# ---------- (1) SWAP MODEL (additive wrapper — episodes HAIGUSWI) ----------

def _nights(entry_ts, exit_ts):
    """Idadi ya midnight-crossings kati ya entry na exit (date-diff kwa siku). datetime64 -> 'D'
    floor = tarehe; tofauti = usiku uliobebwa. Intraday (siku ile ile) = 0."""
    ed = np.datetime64(entry_ts, "D"); xd = np.datetime64(exit_ts, "D")
    return int((xd - ed) / np.timedelta64(1, "D"))


def apply_swap(trades, ts, swap):
    """Gharama ya kubeba usiku (swing). Kwa kila trade (entry_bar, exit_bar, ...): nights =
    midnight-crossings kati ya ts[entry_bar] na ts[exit_bar]; pnl_swing = pnl_net - nights*swap.
    Rudisha list ya (nights, pnl_swing) SAMBAMBA na trades. episodes HAIGUSWI (wrapper safi).
    LIMITATION: swap symmetric (long/short sawa) — carry ya kweli ni asymmetric (rate differential)."""
    out = []
    for (eb, xb, d, pnl, sess, vs) in trades:
        nights = _nights(ts[eb], ts[xb])
        out.append((nights, pnl - nights * swap))
    return out


# ---------- (3) MFE/MAE HELPER (exit-science — additive; episodes HAIGUSWI) ----------

def excursions(trades, o, h, l, c, out_sig, entry, atr, sl_atr):
    """Kwa kila trade: MFE (faida kubwa iliyofikiwa) na MAE (hasara kubwa iliyopitiwa) kabla ya exit,
    kwa pips NA kwa R (÷ sl_atr*atr[signal bar]) + bar-index ya MFE peak (bars baada ya entry).
    Entry price = ILE ILE ya episodes: market -> o[entry_bar]; stop -> max(level,open)/min kwa dir.
    Rudisha list ya (mfe_pips, mae_pips, mfe_r, mae_r, mfe_peak_bar). Additive — episodes HAIGUSWI."""
    res = []
    for (eb, xb, d, pnl, sess, vs) in trades:
        i = eb - 1                                        # signal bar
        if entry == "market":
            e = o[eb]
        else:
            lvl = out_sig["long_level"][i] if d == 1 else out_sig["short_level"][i]
            e = max(lvl, o[eb]) if d == 1 else min(lvl, o[eb])
        risk = sl_atr * atr[i]
        mfe = 0.0; mae = 0.0; peak = eb
        for b in range(eb, xb + 1):
            fav = d * ((h[b] if d == 1 else l[b]) - e)    # excursion ya faida (favorable extreme)
            adv = d * ((l[b] if d == 1 else h[b]) - e)    # excursion ya hasara (adverse extreme; <=0)
            if fav > mfe:
                mfe = fav; peak = b
            if adv < mae:
                mae = adv
        r = risk if risk > 0 else np.nan
        res.append((mfe, mae, mfe / r, mae / r, peak - eb))
    return res


# ---------- (2) R-MAP RUNNER ----------

def _year(ts_scalar):
    return int(str(ts_scalar)[:4])


def _finalize(group):
    """Group = dict ya lists (per CELL×MWAKA×VOL_STATE) -> row ya atlas (medians + means)."""
    n = len(group["swing"])
    gross_sum = float(np.sum(group["gross"]))
    drag = float(np.sum(group["cost"]) + np.sum(group["swap_cost"]))
    swing = np.asarray(group["swing"], float)
    mfe_r = np.asarray(group["mfe_r"], float); mae_r = np.asarray(group["mae_r"], float)
    peak = np.asarray(group["peak"], float)
    to_mfe = [group["mfe_r"][k] for k in range(n) if group["timeout"][k]]
    d1a = [group["d1_align"][k] for k in range(n) if group["d1_align"][k] is not None]
    sess_top = max(set(group["sess"]), key=group["sess"].count) if group["sess"] else "-"
    return dict(
        n=n,
        ev_net=round(float(swing.mean()), 4),
        gross=round(float(np.mean(group["gross"])), 4),
        win=round(float((swing > 0).mean()), 4),
        cost_share=(round(drag / gross_sum, 4) if gross_sum > 0 else None),
        mfe_r_med=round(float(np.median(mfe_r)), 4),
        mae_r_med=round(float(np.median(mae_r)), 4),
        mfe_peak_bar_med=round(float(np.median(peak)), 2),
        timeout_mfe_r_med=(round(float(np.median(to_mfe)), 4) if to_mfe else None),
        d1_align_frac=(round(float(np.mean(d1a)), 3) if d1a else None),
        sess_top=sess_top,
    )


def run(split="train", out_root=REPO_ROOT, write=True, events=None, pairs=None,
        tfs=ALL_TFS, verbose=True):
    """Jenga ATLAS. GUARD: TRAIN PEKEE — VALIDATION/HOLDOUT haziguswi (na sacred-splits ya
    load_window inabaki chini). Rudisha list ya rows (CELL×MWAKA×VOL_STATE)."""
    if split != "train":
        raise PermissionError("R-MAP ni TRAIN PEKEE (atlas = ramani ya TRAIN) — VALID/HOLDOUT kamwe")
    from market_state_engine import cfg
    conf = cfg()
    events = events or usable_events()
    pairs = pairs or conf["pairs"]
    swap_cfg = conf.get("swap_pips_per_night", {})
    groups = {}
    t0 = time.time(); n_signals = 0
    for pair in pairs:
        swap = float(swap_cfg.get(pair, SWAP_DEFAULT))
        for tf in tfs:
            data = load_window(pair, tf, split)
            if data is None:
                if verbose:
                    print(f"  ONYO: {pair}/{tf} — state parquet haipo; naruka")
                continue
            o, h, l_, c = data["o"], data["h"], data["l"], data["c"]
            atr, spr, hour, vol, ts = data["atr"], data["spr"], data["hour"], data["vol"], data["ts"]
            n = len(c)
            ctx = data.get("ctx")
            d1sign = (np.asarray(ctx["d1_trend_sign"], float)
                      if ctx and "d1_trend_sign" in ctx else None)
            for ev in events:
                spec = EVENTS_V2[ev]
                out = spec["fn"](o, h, l_, c, data.get("tc"), hour); entry = spec["entry"]
                n_signals += 1
                for sl in SLS:
                    for tp in TPS:
                        trs = episodes(out, entry, o, h, l_, c, atr, spr, hour, vol,
                                       sl_atr=sl, tp_atr=tp, max_hold=MAX_HOLD[tf])
                        if not trs:
                            continue
                        sw = apply_swap(trs, ts, swap)
                        exc = excursions(trs, o, h, l_, c, out, entry, atr, sl)
                        slip = SLIP_MARKET if entry == "market" else SLIP_STOP
                        for k, (eb, xb, d, pnl, sess_e, vs) in enumerate(trs):
                            i = eb - 1
                            nights, swing = sw[k]
                            mfe_p, mae_p, mfe_r, mae_r, peak_bar = exc[k]
                            cost = float(spr[eb]) + slip
                            jend = min(i + 1 + MAX_HOLD[tf], n - 1)
                            timeout = (xb == jend)
                            d1a = (None if d1sign is None or not np.isfinite(d1sign[i])
                                   else int(d == int(d1sign[i])))
                            key = (ev, pair, tf, sl, tp, _year(ts[eb]), vs)
                            g = groups.get(key)
                            if g is None:
                                g = groups[key] = dict(swing=[], gross=[], cost=[], swap_cost=[],
                                                       mfe_r=[], mae_r=[], peak=[], timeout=[],
                                                       d1_align=[], sess=[])
                            g["swing"].append(swing)
                            g["gross"].append(pnl + cost)
                            g["cost"].append(cost); g["swap_cost"].append(nights * swap)
                            g["mfe_r"].append(mfe_r); g["mae_r"].append(mae_r)
                            g["peak"].append(peak_bar); g["timeout"].append(bool(timeout))
                            g["d1_align"].append(d1a)
                            g["sess"].append(_sess(int(hour[i])))
    rows = []
    for (ev, pair, tf, sl, tp, year, vs), g in groups.items():
        rows.append(dict(event=ev, pair=pair, tf=tf, sl=sl, tp=tp, year=year, vol_state=vs,
                         **_finalize(g)))
    elapsed = time.time() - t0
    if verbose:
        print(f"  atlas: rows={len(rows):,} signals={n_signals:,} elapsed={elapsed:.1f}s")
    if write:
        _write_outputs(rows, out_root, elapsed, len(events), len(pairs), len(tfs))
    return rows


# ---------- outputs ----------

_COLS = ["event", "pair", "tf", "sl", "tp", "year", "vol_state", "n", "ev_net", "gross", "win",
         "cost_share", "mfe_r_med", "mae_r_med", "mfe_peak_bar_med", "timeout_mfe_r_med",
         "d1_align_frac", "sess_top"]


def _write_outputs(rows, out_root, elapsed, n_ev, n_pairs, n_tf):
    import polars as pl
    out_root = Path(out_root)
    sdir = out_root / "data" / "strategies"; sdir.mkdir(parents=True, exist_ok=True)
    df = pl.DataFrame(rows) if rows else pl.DataFrame({c: [] for c in _COLS})
    df = df.select([c for c in _COLS if c in df.columns])
    pq = sdir / OUT_PARQUET
    df.write_parquet(pq)

    # breadth (L-041): pooled ev per (event,tf,vol_state,pair); positive-pair count = breadth
    from collections import defaultdict
    pair_ev = defaultdict(lambda: [0.0, 0])          # (ev,tf,vs,pair) -> [sum(ev*n), sum(n)]
    for r in rows:
        k = (r["event"], r["tf"], r["vol_state"], r["pair"])
        pair_ev[k][0] += r["ev_net"] * r["n"]; pair_ev[k][1] += r["n"]
    breadth = defaultdict(lambda: [0, 0])            # (ev,tf,vs) -> [pos_pairs, tested_pairs]
    for (ev, tf, vs, pair), (s, nn) in pair_ev.items():
        b = breadth[(ev, tf, vs)]
        b[1] += 1
        if nn > 0 and s / nn > 0:
            b[0] += 1
    top = sorted(breadth.items(), key=lambda kv: (kv[1][0], kv[1][1]), reverse=True)[:20]

    ev_breadth = defaultdict(lambda: [0, 0])         # per event: [pos (ev,tf,vs) combos, total]
    for (ev, tf, vs), (pos, tot) in breadth.items():
        e = ev_breadth[ev]; e[1] += 1
        if pos > 0:
            e[0] += 1

    L = ["# R-MAP ATLAS — TABAKA 2 (behavioral map, TRAIN 2016-2022)\n",
         f"*grid: events {n_ev} × pairs {n_pairs} × TF {n_tf} × SL {len(SLS)} × TP {len(TPS)} | "
         f"rows (cell×mwaka×vol_state)={len(rows):,} | swap-adjusted (swing) | elapsed={elapsed:.1f}s | "
         "costs+swap ndani ya ev_net*\n",
         "> **ATLAS ni RAMANI, si madai** (charter §Tabaka-2). TRAIN PEKEE — hakuna FDR (si hypothesis "
         "test). Breadth = pairs NGAPI zina EV+ (L-041 anti-selection-bias), si cell moja bora. "
         "Hypothesis yoyote kutoka hapa inapita gate: S2 pooled multi-pair → HOLDOUT one-shot.\n"]

    L.append("\n## Top-20 (event × TF × vol_state) kwa BREADTH ya pairs (EV+ swing)\n")
    L.append("| event | TF | vol_state | pairs EV+ | / tested |")
    L.append("|-------|----|-----------|-----------|----------|")
    for (ev, tf, vs), (pos, tot) in top:
        L.append(f"| {ev} | {tf} | {vs} | {pos} | {tot} |")

    L.append("\n## Breadth kwa event (combos za (TF×vol_state) zenye pair-yoyote EV+)\n")
    L.append("| event | regimes EV+ | / total |")
    L.append("|-------|-------------|---------|")
    for ev, (pos, tot) in sorted(ev_breadth.items(), key=lambda kv: kv[1][0], reverse=True):
        L.append(f"| {ev} | {pos} | {tot} |")

    L.append("\n*Malighafi kamili: data/strategies/rmap_train.parquet (mstari 1 kwa "
             "event×pair×tf×sl×tp×mwaka×vol_state; + MFE/MAE R medians kwa exit-lessons). "
             "Next (M3-3): Chief+STRATEGIST-M -> hypotheses zenye breadth -> S2 pooled.*")

    rpt = out_root / "reports" / OUT_REPORT; rpt.parent.mkdir(parents=True, exist_ok=True)
    rpt.write_text("\n".join(L), encoding="utf-8")
    return pq, rpt


# ---------- self-test (synthetic — bila data ya nje) ----------

def _fixture(seed, n=3000, tf_hours=1, start="2016-01-04", ctx=True):
    """Bars synthetic + ts halisi (spacing tf_hours) + vol/ctx kama loader ya M3."""
    import numpy as _np
    o, h, l_, c, tc, hour = _synthetic(n=n, seed=seed)
    atr = _np.maximum(h - l_, 0.1)
    ts = (_np.datetime64(start) + _np.arange(n) * _np.timedelta64(tf_hours, "h"))
    data = dict(o=o, h=h, l=l_, c=c, atr=atr, spr=_np.full(n, 1.0), tc=tc,
                hour=(ts.astype("datetime64[h]").astype(int) % 24).astype(int),
                vol=_np.where(_np.arange(n) % 3 == 0, "HIGH", "NORMAL"), ts=ts, days=250)
    if ctx:
        data["ctx"] = dict(d1_trend_sign=_np.ones(n))
    else:
        data["ctx"] = None
    return data


def self_test():
    ok = True

    # [1] SWAP nights: intraday (siku ile ile) -> 0; siku 3 -> 3; determinism
    ts = np.array(["2016-01-04T08:00", "2016-01-04T15:00", "2016-01-07T09:00"], dtype="datetime64[h]")
    #     trade A: entry bar0 (08:00) -> exit bar1 (15:00) siku ile ile -> nights 0
    #     trade B: entry bar0 (04-01 08:00) -> exit bar2 (07-01 09:00) -> nights 3
    trs = [(0, 1, 1, 10.0, "LON", "NORMAL"), (0, 2, -1, 8.0, "LON", "HIGH")]
    sw = apply_swap(trs, ts, swap=0.5)
    sw2 = apply_swap(trs, ts, swap=0.5)
    t1 = (sw[0][0] == 0 and abs(sw[0][1] - 10.0) < 1e-12
          and sw[1][0] == 3 and abs(sw[1][1] - (8.0 - 3 * 0.5)) < 1e-12 and sw == sw2)
    print(f"  [1] swap nights: intraday=0 (pnl {sw[0][1]}), 3-day=3 (pnl {sw[1][1]}) det={sw==sw2} -> {t1}")
    ok = ok and t1

    # [2] MFE/MAE exactness kwa path inayojulikana (market entry). Bars (o,h,l,c) crafted:
    #     entry=100 (o[eb]); long trade eb=1..xb=3. highs [.,102,101,103] lows [.,99,98,100].
    #     MFE = max(h-e) = 103-100 = 3; peak bar = 3 (index) -> peak_bar = xb? peak at b=3 -> 3-1=2.
    #     MAE = min(l-e) = 98-100 = -2. R: sl_atr=1, atr[i=0]=2 -> risk 2 -> mfe_r 1.5, mae_r -1.0
    o = np.array([100., 100., 100., 100.]); h = np.array([100., 102., 101., 103.])
    l_ = np.array([100., 99., 98., 100.]); c = np.array([100., 100., 100., 102.])
    atr = np.array([2., 2., 2., 2.])
    trs2 = [(1, 3, 1, 5.0, "LON", "NORMAL")]                    # entry_bar=1, exit_bar=3, long
    ex = excursions(trs2, o, h, l_, c, {"sig": np.array([1, 0, 0, 0])}, "market", atr, sl_atr=1.0)
    mfe_p, mae_p, mfe_r, mae_r, peak = ex[0]
    t2 = (abs(mfe_p - 3.0) < 1e-9 and abs(mae_p + 2.0) < 1e-9
          and abs(mfe_r - 1.5) < 1e-9 and abs(mae_r + 1.0) < 1e-9 and peak == 2)
    print(f"  [2] MFE/MAE exact: mfe={mfe_p}(R {mfe_r}) mae={mae_p}(R {mae_r}) peak_bar={peak} -> {t2}")
    ok = ok and t2

    # [2b] STOP entry price = max(level, open): level=101, open=100 -> e=101; MFE=103-101=2
    trs2b = [(1, 3, 1, 0.0, "LON", "NORMAL")]
    out_stop = {"long_level": np.array([101., np.nan, np.nan, np.nan]),
                "short_level": np.full(4, np.nan)}
    exb = excursions(trs2b, o, h, l_, c, out_stop, "stop", atr, sl_atr=1.0)
    t2b = abs(exb[0][0] - 2.0) < 1e-9                            # mfe_pips = 103-101
    print(f"  [2b] stop entry=max(level,open)=101 -> mfe={exb[0][0]} (==2) -> {t2b}")
    ok = ok and t2b

    # [3] TRAIN-guard: run(split!='train') -> PermissionError KABLA ya kusoma data
    import sys as _sys, tempfile
    _self = _sys.modules[__name__]
    g_val = g_hold = False
    try:
        run(split="validation", write=False)
    except PermissionError:
        g_val = True
    try:
        run(split="holdout", write=False)
    except PermissionError:
        g_hold = True
    print(f"  [3] TRAIN-guard: validation-refused={g_val} holdout-refused={g_hold} -> {g_val and g_hold}")
    ok = ok and g_val and g_hold

    # [4]+[5] FULL RUN (monkeypatch load_window + cfg): schema, determinism, outputs, tags, swap-in-ev
    orig_lw = _self.load_window
    import market_state_engine as mse
    orig_cfg = mse.cfg
    fx = {("EURUSD", "H1"): _fixture(1, tf_hours=1), ("XAUUSD", "H1"): _fixture(2, tf_hours=1)}
    _self.load_window = lambda sym, tf, split, token=None: fx.get((sym, tf))
    mse.cfg = lambda: dict(pairs=["EURUSD", "XAUUSD"], paths=orig_cfg()["paths"],
                           swap_pips_per_night={"EURUSD": 0.5, "XAUUSD": 1.5})
    try:
        with tempfile.TemporaryDirectory() as tmp:
            evs = ["nr7_break", "shock_follow", "session_orb"]      # stop + market + hour-needing
            ra = run("train", out_root=tmp, events=evs, pairs=["EURUSD", "XAUUSD"],
                     tfs=("H1",), verbose=False)
            rb = run("train", out_root=tmp, events=evs, pairs=["EURUSD", "XAUUSD"],
                     tfs=("H1",), verbose=False)
            import json as _json
            det = _json.dumps(ra, sort_keys=True) == _json.dumps(rb, sort_keys=True)
            schema_ok = all(set(_COLS) == set(r) for r in ra) and len(ra) > 0
            years_ok = all(2016 <= r["year"] <= 2022 for r in ra)
            vs_ok = set(r["vol_state"] for r in ra) <= {"HIGH", "NORMAL"}
            # swap iko ndani ya ev_net: XAUUSD swap 1.5 -> rows za XAUUSD zenye timeout ndefu
            #   zina ev_net < gross (drag > 0); cost_share > 0 kwa rows zenye gross+
            drag_ok = any((r["cost_share"] is not None and r["cost_share"] > 0) for r in ra)
            import polars as pl
            pq = pl.read_parquet(Path(tmp) / "data" / "strategies" / OUT_PARQUET)
            rpt = (Path(tmp) / "reports" / OUT_REPORT).read_text(encoding="utf-8")
            files_ok = (pq.height == len(ra) and list(pq.columns) == _COLS
                        and "BREADTH" in rpt and "ATLAS ni RAMANI" in rpt)
            mfe_ok = all(("mfe_r_med" in r and "mae_r_med" in r
                          and "timeout_mfe_r_med" in r) for r in ra)
        t45 = det and schema_ok and years_ok and vs_ok and drag_ok and files_ok and mfe_ok
    finally:
        _self.load_window = orig_lw; mse.cfg = orig_cfg
    print(f"  [4] full-run: rows={len(ra)} schema={schema_ok} years={years_ok} vol={vs_ok} "
          f"swap-drag={drag_ok}")
    print(f"  [5] outputs: parquet+report={files_ok} MFE/MAE-cols={mfe_ok} determinism={det} -> {t45}")
    ok = ok and t45

    # [6] usable_events: events zote 21 zinapatikana (needs = hour/tc/())
    ue = usable_events()
    t6 = (len(ue) == len(EVENTS_V2) and "session_orb" in ue and "lowvol_reversal" in ue)
    print(f"  [6] usable_events={len(ue)} (==EVENTS_V2 {len(EVENTS_V2)}; needs hour/tc zapatikana) -> {t6}")
    ok = ok and t6

    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", action="store_true", help="jenga ATLAS kamili (TRAIN; nzito)")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.train:
        print("Tumia --train (ATLAS kamili) | --self-test.", file=sys.stderr)
        return 2
    rows = run("train")
    print(f"R-MAP ATLAS: rows={len(rows):,}\n  data/strategies/{OUT_PARQUET}\n  reports/{OUT_REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
