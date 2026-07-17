"""
swing_family.py — M3-3: SWING FAMILY #1 S2 VALIDATION runner (docs/M3_SWING_FAMILY_REGISTRATION.md).

FAMILY (FROZEN): `nr7_break` (stop, OCO) × **D1** × filter `volatility_state=="LOW"` ya SIGNAL bar
(UNKNOWN excluded, Q1) × SL2.0/TP1.0 × max_hold 20. Kinga ya L-041: **pairs ZOTE 12 pooled kwa R**
(hakuna pair-selection; gold haitawali — R-units dimensionless). Compression-continuation swing
(familia ya STRAT-001/002; hoja ya PD "buy leo sell next week").

TEST RASMI (S2 VALIDATION 2023-2024): pool R-streams za pairs 12 → stream MOJA → `pvalue_boot`
(B=50k, mean_block=3, engine RASMI) → criterion **p_boot<0.05 NA EV_R>0** (m=1, hakuna FDR budget).
p_z sensitivity. VALIDATION ina-consumed. HOLDOUT HAIGUSWI (C2-6 token).

ADDITIVE: ZERO statistic fns (pvalue_boot/pool_streams/_r_normalize/episodes/_mask_context imports
TU — byte-identical). Swap = rmap.apply_swap (wrapper). GUARD: validation PEKEE; pair bila data ->
RuntimeError (F2: hakuna silent skip — pairs zote 12 LAZIMA).

Endesha (PC ya data): python swing_family.py --validate
Self-test (bila data):  python swing_family.py --self-test
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

from event_library_v2 import EVENTS_V2
from event_quality_report import episodes
from strategy_lab import load_window, _mask_context, pvalue_boot, pvalue_gt0
from family_pooled import _r_normalize, pool_streams
from rmap import apply_swap

REPO_ROOT = Path(__file__).resolve().parents[2]

# ---------- FAMILY SPEC (FROZEN — docs/M3_SWING_FAMILY_REGISTRATION.md) ----------
EVENT = "nr7_break"
TF = "D1"
VOL_FILTER = "LOW"                 # volatility_state ya SIGNAL bar (UNKNOWN excluded, Q1)
SL_ATR, TP_ATR = 2.0, 1.0          # jiometri ya STRAT-001 (high-win)
MAX_HOLD = 20                      # D1 bars (~wiki 4)
B = 50_000                         # pvalue_boot (engine RASMI)
MEAN_BLOCK = 3
ALPHA = 0.05                       # criterion: p_boot < 0.05 (m=1)
SEED = 20260717                    # seed FIXED (registration FROZEN) — reproducible
SWAP_DEFAULT = 0.5                 # fallback (pips/night) kama config haina pair
OUT_JSONL = "swing_family_s2.jsonl"
OUT_REPORT = "swing_family_s2.md"


def _pairs():
    from market_state_engine import cfg
    return list(cfg()["pairs"])


def _swap_cfg():
    from market_state_engine import cfg
    return cfg().get("swap_pips_per_night", {})


def _pair_stream(pair, split, swap):
    """R-stream ya pair moja: nr7_break -> vol=LOW mask (signal bar) -> episodes(SL2/TP1,hold20) ->
    apply_swap (swing carry) -> _r_normalize. Rudisha (stream_rows). Data haipo -> None (mpiga simu
    ndiye anayeamua RuntimeError — F2)."""
    data = load_window(pair, TF, split)
    if data is None or data.get("ts") is None:
        return None
    o, h, l_, c = data["o"], data["h"], data["l"], data["c"]
    atr, spr, hour, vol, ts = data["atr"], data["spr"], data["hour"], data["vol"], data["ts"]
    spec = EVENTS_V2[EVENT]
    out = spec["fn"](o, h, l_, c, data.get("tc"), hour)
    out = _mask_context(out, spec["entry"], hour, vol, None, VOL_FILTER)   # vf=LOW (signal-bar; UNKNOWN nje)
    trs = episodes(out, spec["entry"], o, h, l_, c, atr, spr, hour, vol,
                   sl_atr=SL_ATR, tp_atr=TP_ATR, max_hold=MAX_HOLD)
    sw = apply_swap(trs, ts, swap)                                          # (nights, pnl_swing)
    trs_sw = [(eb, xb, d, sw[k][1], sess, vs)                              # badilisha pnl -> pnl_swing
              for k, (eb, xb, d, pnl, sess, vs) in enumerate(trs)]
    return _r_normalize(trs_sw, atr, SL_ATR, ts, pair)


def run_s2(split="validation", out_root=REPO_ROOT, write=True, pairs=None):
    """S2 VALIDATION pooled test ya family. GUARD: validation PEKEE — TRAIN imekwisha (atlas);
    HOLDOUT = C2-6 one-shot (token), SI hapa. Pair bila data -> RuntimeError (F2, pairs zote 12)."""
    if split != "validation":
        raise PermissionError("SWING S2 ni VALIDATION PEKEE — TRAIN=atlas; HOLDOUT=C2-6 token, SI hapa")
    pairs = pairs or _pairs()
    swap_cfg = _swap_cfg()
    streams = []; per_pair = []
    for pair in pairs:
        swap = float(swap_cfg.get(pair, SWAP_DEFAULT))
        st = _pair_stream(pair, split, swap)
        if st is None:
            raise RuntimeError(f"F2: {pair}/{TF} {split} data haipo — pairs ZOTE 12 LAZIMA (hakuna silent skip)")
        streams.append(st)
        rs = [r["pnl_R"] for r in st]
        per_pair.append(dict(pair=pair, n=len(rs),
                             ev_R=(round(float(np.mean(rs)), 4) if rs else None)))
    pooled = pool_streams(streams)                                          # dedup (pair,entry_bar) AT7
    R = [r["pnl_R"] for r in pooled]
    n = len(R)
    ev_R = round(float(np.mean(R)), 4) if n else None
    p_boot = round(float(pvalue_boot(R, B=B, mean_block=MEAN_BLOCK, seed=SEED)), 6) if n >= 2 else 1.0
    p_z = round(float(pvalue_gt0(R)), 6) if n >= 2 else 1.0
    verdict = "PASS" if (ev_R is not None and ev_R > 0 and p_boot < ALPHA) else "FAIL"
    result = dict(pooled_n=n, pooled_ev_R=ev_R, p_boot=p_boot, p_z=p_z, verdict=verdict,
                  per_pair=per_pair)
    if write:
        _write_outputs(result, split, out_root)
    return result


# ---------- outputs ----------

def _write_outputs(res, split, out_root):
    out_root = Path(out_root)
    sdir = out_root / "data" / "strategies"; sdir.mkdir(parents=True, exist_ok=True)
    jl = sdir / OUT_JSONL
    with open(jl, "w", encoding="utf-8") as f:
        for pp in res["per_pair"]:
            f.write(json.dumps(dict(pp, kind="pair", split=split), sort_keys=True) + "\n")
        f.write(json.dumps(dict(kind="pooled", split=split, n=res["pooled_n"],
                                ev_R=res["pooled_ev_R"], p_boot=res["p_boot"], p_z=res["p_z"],
                                verdict=res["verdict"]), sort_keys=True) + "\n")

    pos_pairs = sum(1 for pp in res["per_pair"] if pp["ev_R"] is not None and pp["ev_R"] > 0)
    L = [f"# SWING FAMILY #1 — S2 VALIDATION ({EVENT} × {TF} × vol={VOL_FILTER}; docs/M3_SWING_FAMILY_REGISTRATION.md)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | split={split.upper()} (2023-2024) | pairs 12 pooled R "
         f"(L-041) | SL{SL_ATR}/TP{TP_ATR} hold {MAX_HOLD} | costs+swap ndani | engine RASMI: "
         f"pvalue_boot B={B:,} mean_block={MEAN_BLOCK} seed={SEED} | criterion p<{ALPHA} NA EV_R>0 (m=1)*\n"]
    if res["verdict"] == "PASS":
        L.append(f"## VERDICT: **PASS** — pooled EV_R {res['pooled_ev_R']:+.4f} (N={res['pooled_n']}), "
                 f"p_boot {res['p_boot']:.4f} < {ALPHA}\n")
        L.append("-> C2-6 freeze -> HOLDOUT one-shot (dirisha bikira D1 2025-01->2026-04, token "
                 "CHIEF-HOLDOUT-S3). Ikipita = STRAT-003 (swing high-win family).")
    else:
        L.append(f"## VERDICT: **FAIL kwa heshima** — pooled EV_R {res['pooled_ev_R']} (N={res['pooled_n']}), "
                 f"p_boot {res['p_boot']} (criterion p<{ALPHA} NA EV_R>0)\n")
        L.append("-> LESSON; family inabaki C2-WATCH-style forward-only (si dead). "
                 "Tahadhari za registration: N_valid ~110 -> power ya wastani.")
    L.append(f"\n*p_z (sensitivity, SI decision) = {res['p_z']}. VALIDATION ime-consumed kwa family hii. "
             "HOLDOUT HAIJAGUSWA (token C2-6). Engine RASMI haijabadilika.*")

    L.append("\n## Per-pair (R-normalized; pooled, HAKUNA pair-selection — accounting tu)\n")
    L.append("| pair | N | EV_R |")
    L.append("|------|---|------|")
    for pp in res["per_pair"]:
        ev = f"{pp['ev_R']:+.4f}" if pp["ev_R"] is not None else "—"
        L.append(f"| {pp['pair']} | {pp['n']} | {ev} |")
    L.append(f"\n*Pairs EV_R>0: {pos_pairs}/{len(res['per_pair'])} (breadth ya VALIDATION — rejea; "
             "decision ni pooled p_boot pekee). Gold (XAUUSD) kwa R-units — haitawali pooling.*")

    rpt = out_root / "reports" / OUT_REPORT; rpt.parent.mkdir(parents=True, exist_ok=True)
    rpt.write_text("\n".join(L), encoding="utf-8")
    return jl, rpt


# ---------- self-test (synthetic — bila data ya nje) ----------

def _fixture(seed, n=1200, vol_pattern="mixed", atr_scale=1.0, start="2023-06-01"):
    """D1 bars synthetic + ts (spacing siku 1) + vol_state (LOW/HIGH/UNKNOWN). atr_scale kubwa =
    'gold-like' (pips kubwa) kwa R-pooling sanity."""
    from event_library_v2 import _synthetic
    o, h, l_, c, tc, hour = _synthetic(n=n, seed=seed)
    o, h, l_, c = (x * atr_scale for x in (o, h, l_, c))
    atr = np.maximum(h - l_, 0.1)
    ts = (np.datetime64(start) + np.arange(n) * np.timedelta64(1, "D"))
    if vol_pattern == "all_low":
        vol = np.full(n, "LOW")
    elif vol_pattern == "none_low":
        vol = np.where(np.arange(n) % 2 == 0, "HIGH", "UNKNOWN")
    else:                                                    # mixed: LOW / HIGH / UNKNOWN
        vol = np.array(["LOW", "HIGH", "UNKNOWN"])[np.arange(n) % 3]
    return dict(o=o, h=h, l=l_, c=c, atr=atr, spr=np.full(n, 1.0), tc=tc,
                hour=(ts.astype("datetime64[h]").astype(int) % 24).astype(int),
                vol=vol, ts=ts, days=n, ctx=None)


def self_test():
    ok = True
    import sys as _sys, tempfile
    _self = _sys.modules[__name__]
    orig_lw = _self.load_window
    import market_state_engine as mse
    orig_cfg = mse.cfg
    P12 = ["EURUSD", "GBPUSD", "USDJPY", "EURJPY", "USDCAD", "USDCHF",
           "AUDUSD", "NZDUSD", "EURGBP", "GBPJPY", "EURCHF", "XAUUSD"]
    mse.cfg = lambda: dict(pairs=P12, paths=orig_cfg()["paths"],
                           swap_pips_per_night={p: (1.5 if p == "XAUUSD" else 0.5) for p in P12})

    # [1] GUARD: split != validation -> PermissionError KABLA ya kusoma data
    g_tr = g_ho = False
    try:
        run_s2("train", write=False)
    except PermissionError:
        g_tr = True
    try:
        run_s2("holdout", write=False)
    except PermissionError:
        g_ho = True
    print(f"  [1] guard: train-refused={g_tr} holdout-refused={g_ho} -> {g_tr and g_ho}")
    ok = ok and g_tr and g_ho

    # [2] F2: pair bila data -> RuntimeError (hakuna silent skip)
    fxs = {p: _fixture(10 + k) for k, p in enumerate(P12)}
    _self.load_window = lambda sym, tf, split, token=None: (None if sym == "XAUUSD" else fxs.get(sym))
    f2 = False
    try:
        run_s2("validation", write=False)
    except RuntimeError:
        f2 = True
    print(f"  [2] F2 pair-missing -> RuntimeError: {f2}")
    ok = ok and f2

    # [3] vol=LOW filter decidability (signal-bar) + UNKNOWN excluded: kwa pair yenye vol=all_low
    #     trades zipo; yenye none_low (HIGH/UNKNOWN pekee) -> trades 0 (mask inazuia)
    fx_low = _fixture(1, vol_pattern="all_low")
    fx_none = _fixture(1, vol_pattern="none_low")
    _self.load_window = lambda sym, tf, split, token=None: fx_low
    st_low = _pair_stream("EURUSD", "validation", 0.5)
    _self.load_window = lambda sym, tf, split, token=None: fx_none
    st_none = _pair_stream("EURUSD", "validation", 0.5)
    t3 = len(st_low) > 0 and len(st_none) == 0
    print(f"  [3] vol=LOW filter: all-LOW trades={len(st_low)} none-LOW(HIGH/UNKNOWN)={len(st_none)}(==0) -> {t3}")
    ok = ok and t3

    # [3b] DECIDABILITY EXACT + UNKNOWN excluded: kila trade ya stream ina vol[signal bar]=="LOW"
    fx_mix = _fixture(2, vol_pattern="mixed")
    _self.load_window = lambda sym, tf, split, token=None: fx_mix
    st_mix = _pair_stream("EURUSD", "validation", 0.5)
    sig_low = all(str(fx_mix["vol"][r["entry_bar"] - 1]) == "LOW" for r in st_mix)
    no_unknown = all(str(fx_mix["vol"][r["entry_bar"] - 1]) != "UNKNOWN" for r in st_mix)
    t3b = len(st_mix) > 0 and sig_low and no_unknown
    print(f"  [3b] decidability EXACT: signal-bar vol==LOW kwa {len(st_mix)} trades, UNKNOWN nje -> {t3b}")
    ok = ok and t3b

    # [4] SWAP inatumika: pnl_R yenye swap < pnl_R bila swap (drag chanya kwa trades zenye nights>0)
    fx_s = _fixture(3, vol_pattern="all_low")
    _self.load_window = lambda sym, tf, split, token=None: fx_s
    st_swap = _pair_stream("EURUSD", "validation", 2.0)      # swap kubwa
    st_noswap = _pair_stream("EURUSD", "validation", 0.0)    # swap sifuri
    mean_swap = np.mean([r["pnl_R"] for r in st_swap]); mean_noswap = np.mean([r["pnl_R"] for r in st_noswap])
    t4 = len(st_swap) == len(st_noswap) and mean_swap < mean_noswap    # D1 -> nights>0 -> drag
    print(f"  [4] swap drag: EV_R swap2.0={mean_swap:.4f} < swap0={mean_noswap:.4f} -> {t4}")
    ok = ok and t4

    # [5] FULL run + determinism + R-pooling sanity (gold haitawali) + verdict + outputs
    fxs2 = {}
    for k, p in enumerate(P12):
        # XAUUSD 'gold-like' (atr kubwa mara 100) — R-pooling lazima i-normalize
        fxs2[p] = _fixture(20 + k, vol_pattern="mixed", atr_scale=(100.0 if p == "XAUUSD" else 1.0))
    _self.load_window = lambda sym, tf, split, token=None: fxs2.get(sym)
    with tempfile.TemporaryDirectory() as tmp:
        ra = run_s2("validation", out_root=tmp)
        rb = run_s2("validation", out_root=tmp)
        det = json.dumps(ra, sort_keys=True) == json.dumps(rb, sort_keys=True)
        # gold R-scale sanity: |EV_R| ya XAUUSD iko katika oda ile ile ya pairs nyingine (si 100x)
        evs = {pp["pair"]: pp["ev_R"] for pp in ra["per_pair"]}
        others = [abs(evs[p]) for p in P12 if p != "XAUUSD" and evs[p] is not None]
        gold_ok = (evs["XAUUSD"] is not None
                   and abs(evs["XAUUSD"]) <= 5 * (max(others) if others else 1) + 1)
        verdict_ok = ra["verdict"] in ("PASS", "FAIL") and ra["pooled_n"] > 0
        jl = Path(tmp) / "data" / "strategies" / OUT_JSONL
        rpt = (Path(tmp) / "reports" / OUT_REPORT).read_text(encoding="utf-8")
        recs = [json.loads(ln) for ln in open(jl, encoding="utf-8")]
        files_ok = (len([r for r in recs if r["kind"] == "pair"]) == 12
                    and any(r["kind"] == "pooled" for r in recs)
                    and "VERDICT" in rpt and ("PASS" in rpt or "FAIL" in rpt))
    _self.load_window = orig_lw; mse.cfg = orig_cfg
    t5 = det and gold_ok and verdict_ok and files_ok
    print(f"  [5] full run: pooled_n={ra['pooled_n']} verdict={ra['verdict']} det={det} "
          f"gold-R-normalized={gold_ok} outputs={files_ok} -> {t5}")
    ok = ok and t5

    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true", help="endesha S2 VALIDATION pooled (PC ya data)")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.validate:
        print("Tumia --validate (S2 VALIDATION) | --self-test.", file=sys.stderr)
        return 2
    res = run_s2("validation")
    print(f"SWING FAMILY #1 S2: {res['verdict']} — pooled EV_R={res['pooled_ev_R']} "
          f"N={res['pooled_n']} p_boot={res['p_boot']} (p_z={res['p_z']})")
    print(f"  data/strategies/{OUT_JSONL}\n  reports/{OUT_REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
