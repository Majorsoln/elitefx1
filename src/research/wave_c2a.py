"""
wave_c2a.py — C2-3: S1 TRAIN runner ya WAVE-C2-A (grid FROZEN na Chief — docs/WAVE_C2A_REGISTRATION.md).

HYPOTHESES 3 za STRATEGIST-M (HC2-01 ALIGNED-COMPRESSION · HC2-03 TREND-PULLBACK-RESUME ·
HC2-06 HTF-SR-FADE), TF ya entry = 30m, TRAIN 2016-2022 PEKEE. Cells = 84 (40+24+20) —
zime-enumerate KAMA ZILIVYO kwenye registration; hakuna pair/SL/TP ya ziada.

MCHAKATO (kwa kila cell): load_window(pair, "30m", "train") [ina `ctx` ya C2-2a] →
EVENTS_V2[trigger] signals → allow_long/allow_short kutoka context ya SIGNAL bar i →
_mask_context_dir (context ON signals, KABLA ya episodes — mtindo wa evaluate/_mask_context) →
episodes() (fill rules ZILIZOKAGULIWA — SIGUSWI; costs kila trade) → metrics.

NaN/UNKNOWN HANDLING (registration §TOTAL): NaN kwenye numeric context = "haijulikani" =
allow False (bar haihesabiwi; hakuna imputation). IMPLEMENTATION NOTE (deviation-with-reason
kutoka mfano wa prompt): nan_to_num(nan→0) ingekosea kwa conditions za HC2-06 zenye
`trend_sign>=0` / `<=0` (0 inapita comparison → NaN ingeruhusiwa). Badala yake kila condition
ina guard ya wazi ya np.isfinite juu ya KILA column inayotumika — semantics ileile ya
registration ("NaN → allow=False") kwa conditions ZOTE, self-tested ([2] trap ya >=0).

S1 = TRAIN EXPLORATION: HAKUNA p-value/FDR hapa (S2 = family-pooled + BH-FDR kwenye VALIDATION).
HAKUNA VALID/HOLDOUT kusomwa — run() inakataa split yoyote isiyo "train" (guard + sacred splits
za load_window zinabaki). Gold HAIMO (pairs za registration ni FX pekee).

Outputs: data/strategies/wave_c2a_train.jsonl (rows za cells ZOTE 84 — accounting kamili ya
pre-registration; metrics null kama N=0) + reports/wave_c2a_s1_train.md.

Endesha (PC ya data):  python wave_c2a.py --train
Self-test (bila data): python wave_c2a.py --self-test
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

from event_library_v2 import EVENTS_V2, _synthetic
from event_quality_report import episodes, _metrics, SLIP_MARKET, SLIP_STOP
from strategy_lab import _mask_context_dir, load_window, MIN_N

REPO_ROOT = Path(__file__).resolve().parents[2]
TF = "30m"                                     # registration: TF ya entry = 30m (shared)
OUT_JSONL = "wave_c2a_train.jsonl"
OUT_REPORT = "wave_c2a_s1_train.md"


# ---------- context conditions (FROZEN — docs/WAVE_C2A_REGISTRATION.md) ----------
# Zote zinafanya kazi juu ya values za SIGNAL bar i (ctx ya loader ni as-of joined, decidable).
# Kila column inayotumika ina isfinite guard: NaN = haijulikani = allow False (§TOTAL).

def _fin(ctx, col):
    """Numeric context column -> float64 array (loader tayari anatoa float64; hii ni ulinzi)."""
    return np.asarray(ctx[col], float)


def _hc201_allow(ctx, sign):
    d1 = _fin(ctx, "d1_trend_sign"); h4 = _fin(ctx, "h4_trend_sign")
    with np.errstate(invalid="ignore"):
        return np.isfinite(d1) & np.isfinite(h4) & (d1 == sign) & (h4 == sign)


def _hc203_allow(ctx, sign):
    d1 = _fin(ctx, "d1_trend_sign"); h4 = _fin(ctx, "h4_trend_sign"); rsi = _fin(ctx, "h4_rsi14")
    with np.errstate(invalid="ignore"):
        ok = np.isfinite(d1) & np.isfinite(h4) & np.isfinite(rsi) & (d1 == sign) & (h4 == sign)
        return ok & ((rsi < 70.0) if sign == 1 else (rsi > 30.0))


def _hc206_allow_long(ctx):
    sup = _fin(ctx, "d1_dist_sup_atr"); h4 = _fin(ctx, "h4_trend_sign")
    with np.errstate(invalid="ignore"):
        return np.isfinite(sup) & np.isfinite(h4) & (sup <= 0.5) & (h4 >= 0)


def _hc206_allow_short(ctx):
    res = _fin(ctx, "d1_dist_res_atr"); h4 = _fin(ctx, "h4_trend_sign")
    with np.errstate(invalid="ignore"):
        return np.isfinite(res) & np.isfinite(h4) & (res <= 0.5) & (h4 <= 0)


# ---------- HYPOTHESES (grid FROZEN — thamani KAMA ZILIVYO kwenye registration) ----------
HYPOTHESES = (
    dict(id="HC2-01", name="ALIGNED-COMPRESSION",
         triggers=("nr7_break", "nr4_inside"),
         allow_long=lambda ctx: _hc201_allow(ctx, +1),
         allow_short=lambda ctx: _hc201_allow(ctx, -1),
         sl=(1.0, 1.5), tp=(2.0, 3.0), max_hold=32,
         pairs=("USDCHF", "USDJPY", "EURJPY", "AUDUSD", "GBPJPY")),          # cells 2x4x5 = 40
    dict(id="HC2-03", name="TREND-PULLBACK-RESUME",
         triggers=("trend_resume", "rsi2_pullback"),
         allow_long=lambda ctx: _hc203_allow(ctx, +1),
         allow_short=lambda ctx: _hc203_allow(ctx, -1),
         sl=(1.0, 1.5), tp=(2.0, 3.0), max_hold=32,
         pairs=("USDJPY", "GBPJPY", "EURUSD")),                              # cells 2x4x3 = 24
    dict(id="HC2-06", name="HTF-SR-FADE",
         triggers=("bb_fade", "engulf_extreme"),
         allow_long=_hc206_allow_long,
         allow_short=_hc206_allow_short,
         sl=(1.0, 1.5), tp=(1.5,), max_hold=24,
         pairs=("EURGBP", "EURCHF", "USDCHF", "AUDUSD", "NZDUSD")),          # cells 2x2x5 = 20
)


def cells():
    """Enumerate cells ZOTE za grid FROZEN (m=84). FDR ya S2 itahesabu enumeration HII."""
    out = []
    for hyp in HYPOTHESES:
        for trig in hyp["triggers"]:
            for pair in hyp["pairs"]:
                for sl in hyp["sl"]:
                    for tp in hyp["tp"]:
                        out.append(dict(hypothesis=hyp["id"], trigger=trig, pair=pair,
                                        sl_atr=sl, tp_atr=tp, max_hold=hyp["max_hold"]))
    return out


# ---------- evaluation (REUSE: EVENTS_V2 + _mask_context_dir + episodes; hakuna fill/stat mpya) ----------

def _masked_signals(hyp, trig, data):
    """Signals za trigger + context mask ya direction (ON signals, kabla ya episodes).
    Inarudishwa mara moja kwa (hyp, trig, pair) — SL/TP hazibadilishi signals."""
    spec = EVENTS_V2[trig]
    out = spec["fn"](data["o"], data["h"], data["l"], data["c"], data.get("tc"), data.get("hour"))
    aL = hyp["allow_long"](data["ctx"])
    aS = hyp["allow_short"](data["ctx"])
    return _mask_context_dir(out, spec["entry"], aL, aS), spec["entry"]


def eval_cell(out_masked, entry, data, sl, tp, max_hold):
    """episodes() + metrics za cell moja. Costs ziko NDANI ya pnl ya episodes (spread+slip);
    hapa tunazihesabu tena kwa uwazi (gross/cost_share) — HATUBADILISHI pnl."""
    trs = episodes(out_masked, entry, data["o"], data["h"], data["l"], data["c"],
                   data["atr"], data["spr"], data["hour"], data.get("vol"),
                   sl_atr=sl, tp_atr=tp, max_hold=max_hold)
    pnls = [t[3] for t in trs]
    m = _metrics(pnls)
    row = dict(n=m["n"])
    if m["n"] == 0:
        return row
    slip = SLIP_MARKET if entry == "market" else SLIP_STOP
    costs = [float(data["spr"][t[0]]) + slip for t in trs]           # t[0] = entry bar
    gross = [p + c_ for p, c_ in zip(pnls, costs)]
    tot_gross = float(np.sum(gross))
    nbar = len(data["c"])
    timeout = [int(t[1] == min(t[0] + max_hold, nbar - 1)) for t in trs]
    row.update(ev=round(m["ev"], 4), win=round(m["win"], 4),
               pf=round(m["pf"], 3) if np.isfinite(m["pf"]) else None,
               gross=round(float(np.mean(gross)), 4),
               cost_share=(round(float(np.sum(costs)) / tot_gross, 4) if tot_gross > 0 else None),
               timeout_share=round(float(np.mean(timeout)), 4),
               min_n_ok=bool(m["n"] >= MIN_N))
    return row


def run(split="train", out_root=REPO_ROOT, write=True):
    """Endesha grid FROZEN. GUARD: S1 ya WAVE-C2-A ni TRAIN PEKEE — split nyingine inakataliwa
    hapa (na sacred-splits guard ya load_window inabaki chini yake). Rudisha rows za cells zote."""
    if split != "train":
        raise PermissionError("C2-3 ni TRAIN PEKEE (S1 exploration) — VALID/HOLDOUT haziguswi hapa")
    pairs_all = sorted({p for hyp in HYPOTHESES for p in hyp["pairs"]})
    cache = {p: load_window(p, TF, split) for p in pairs_all}
    skipped = sorted(p for p in pairs_all
                     if cache[p] is None or cache[p].get("ctx") is None)
    for p in skipped:
        why = "state parquet haipo/fupi" if cache[p] is None else "context parquet haipo (ctx=None)"
        print(f"  ONYO: {p}/{TF} — {why}; cells za pair hii zinarukwa (zinabaki kwenye jsonl kama n=0)")

    rows = []
    sig_cache = {}
    for cell in cells():
        pair = cell["pair"]
        data = cache[pair]
        rec = dict(cell, days=(data["days"] if data is not None else 0))
        if data is None or data.get("ctx") is None:
            rec.update(n=0, skipped=True)
            rows.append(rec)
            continue
        hyp = next(h for h in HYPOTHESES if h["id"] == cell["hypothesis"])
        key = (cell["hypothesis"], cell["trigger"], pair)
        if key not in sig_cache:
            sig_cache[key] = _masked_signals(hyp, cell["trigger"], data)
        out_masked, entry = sig_cache[key]
        rec.update(eval_cell(out_masked, entry, data, cell["sl_atr"], cell["tp_atr"],
                             cell["max_hold"]))
        rows.append(rec)
    if write:
        _write_outputs(rows, split, out_root, skipped)
    return rows


# ---------- outputs ----------

def _write_outputs(rows, split, out_root, skipped=()):
    out_root = Path(out_root)
    sdir = out_root / "data" / "strategies"; sdir.mkdir(parents=True, exist_ok=True)
    jl = sdir / OUT_JSONL
    with open(jl, "w", encoding="utf-8") as f:
        for r in rows:
            rec = dict(r); rec["split"] = split
            f.write(json.dumps(rec, sort_keys=True) + "\n")

    L = [f"# WAVE-C2-A — S1 TRAIN (grid FROZEN m=84; docs/WAVE_C2A_REGISTRATION.md)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | TF={TF} | split={split.upper()} (2016-2022 PEKEE) | "
         f"cells={len(rows)} | context ON signals (_mask_context_dir, signal-bar i; NaN→excluded) | "
         f"costs ndani ya episodes (spread+slip) | MIN_N={MIN_N}*\n",
         "> **UAMINIFU:** S1 = TRAIN EXPLORATION — hakuna p-value/FDR hapa; namba zote ni in-sample. "
         "Uthibitisho = S2 (family-pooled + BH-FDR kwenye VALIDATION) → C2-6 freeze → HOLDOUT "
         "one-shot. LESSON-001/002/029. Profitable != Tradable Edge.\n"]
    if skipped:
        L.append(f"\n**ONYO:** pairs zilizorukwa (state/context haipo): {', '.join(skipped)} — "
                 "cells zao zimo jsonl kama n=0/skipped.\n")

    L.append("\n## Muhtasari kwa hypothesis\n")
    L.append("| hypothesis | cells | cells N>=MIN_N | jumla N | EV>0 cells | median EV net | median cost_share |")
    L.append("|------------|-------|----------------|---------|------------|----------------|--------------------|")
    for hyp in HYPOTHESES:
        hr = [r for r in rows if r["hypothesis"] == hyp["id"]]
        okr = [r for r in hr if r.get("min_n_ok")]
        n_tot = sum(r.get("n", 0) for r in hr)
        if okr:
            evs = [r["ev"] for r in okr]
            css = [r["cost_share"] for r in okr if r.get("cost_share") is not None]
            med_cs = f"{np.median(css):.2f}" if css else "—"
            L.append(f"| {hyp['id']} {hyp['name']} | {len(hr)} | {len(okr)} | {n_tot:,} | "
                     f"{sum(1 for e in evs if e > 0)}/{len(okr)} | {np.median(evs):+.3f} | {med_cs} |")
        else:
            L.append(f"| {hyp['id']} {hyp['name']} | {len(hr)} | 0 | {n_tot:,} | — | — | — |")

    pos = sorted((r for r in rows if r.get("min_n_ok") and r.get("ev", 0) > 0),
                 key=lambda r: r["ev"], reverse=True)
    L.append("\n## Candidates zenye EV_net>0 (N>=MIN_N; in-sample TRAIN — SI survivors)\n")
    L.append("| hypothesis | trigger | pair | SL | TP | N | EV net | gross | cost_share | win% | PF | timeout% |")
    L.append("|------------|---------|------|----|----|---|--------|-------|------------|------|----|----------|")
    for r in pos:
        L.append(f"| {r['hypothesis']} | {r['trigger']} | {r['pair']} | {r['sl_atr']} | {r['tp_atr']} | "
                 f"{r['n']:,} | {r['ev']:+.3f} | {r['gross']:+.3f} | "
                 f"{r['cost_share'] if r['cost_share'] is not None else '—'} | "
                 f"{r['win']*100:.1f} | {r['pf'] if r['pf'] is not None else 'inf'} | "
                 f"{r['timeout_share']*100:.0f} |")
    if not pos:
        L.append("| — | — | — | — | — | — | — | — | — | — | — | — |")
    L.append(f"\n*Cells chanya: {len(pos)}/{len(rows)}. Next: S2 = kila hypothesis kama FAMILY moja "
             "(pool R, mtindo wa family_pooled) kwenye VALIDATION + BH-FDR (Chief). "
             "Grid frozen — hakuna cell mpya baada ya hapa.*")

    rpt = out_root / "reports" / OUT_REPORT; rpt.parent.mkdir(parents=True, exist_ok=True)
    rpt.write_text("\n".join(L), encoding="utf-8")
    return jl, rpt


# ---------- self-test (synthetic — bila data ya nje) ----------

def _fixture(seed, n=4000, ctx=None):
    """Bars synthetic + ctx dict inayoiga loader ya C2-2a (numeric float64; signal-bar values)."""
    o, h, l, c, tc, hour = _synthetic(n=n, seed=seed)
    atr = np.maximum(h - l, 0.1)
    base_ctx = dict(
        d1_trend_sign=np.ones(n), h4_trend_sign=np.ones(n), h4_rsi14=np.full(n, 50.0),
        d1_dist_sup_atr=np.full(n, 2.0), d1_dist_res_atr=np.full(n, 2.0),
    )
    if ctx:
        base_ctx.update(ctx)
    return dict(o=o, h=h, l=l, c=c, atr=atr, spr=np.full(n, 1.0), tc=tc, hour=hour,
                vol=np.array(["NORMAL"] * n), ts=None, ctx=base_ctx, days=250)


def self_test():
    ok = True

    # [1] GRID FROZEN: cells 84 (40+24+20); pairs/SL/TP/max_hold KAMA registration; hakuna gold
    cs = cells()
    per = {h["id"]: sum(1 for c_ in cs if c_["hypothesis"] == h["id"]) for h in HYPOTHESES}
    p01 = {c_["pair"] for c_ in cs if c_["hypothesis"] == "HC2-01"}
    tp06 = {c_["tp_atr"] for c_ in cs if c_["hypothesis"] == "HC2-06"}
    t1 = (len(cs) == 84 and per == {"HC2-01": 40, "HC2-03": 24, "HC2-06": 20}
          and p01 == {"USDCHF", "USDJPY", "EURJPY", "AUDUSD", "GBPJPY"}
          and tp06 == {1.5}
          and not any(c_["pair"] == "XAUUSD" for c_ in cs)
          and all(c_["max_hold"] == (24 if c_["hypothesis"] == "HC2-06" else 32) for c_ in cs))
    print(f"  [1] grid frozen: cells={len(cs)} per-hyp={per} tp06={sorted(tp06)} no-gold=True -> {t1}")
    ok = ok and t1

    # [2] NaN-context EXCLUSION: NaN kwenye column yoyote -> allow=False kwa hypotheses ZOTE.
    #     Trap ya >=0 (HC2-06): h4_trend_sign=NaN LAZIMA iwe False (nan_to_num(0)>=0 ingekosea).
    n2 = 8
    ctx_nan = dict(d1_trend_sign=np.full(n2, np.nan), h4_trend_sign=np.full(n2, np.nan),
                   h4_rsi14=np.full(n2, np.nan), d1_dist_sup_atr=np.full(n2, np.nan),
                   d1_dist_res_atr=np.full(n2, np.nan))
    all_false = all(not fn(ctx_nan).any() for h in HYPOTHESES for fn in (h["allow_long"], h["allow_short"]))
    ctx_trap = dict(ctx_nan, d1_dist_sup_atr=np.full(n2, 0.1))       # sup iko OK, trend=NaN
    trap_ok = not _hc206_allow_long(ctx_trap).any()                  # >=0 trap: NaN -> False
    # NaN bar haitoi trade: fixture yenye ctx NaN yote -> episodes 0 trades
    fx_nan = _fixture(3, n=3000, ctx={k: np.full(3000, np.nan) for k in ctx_nan})
    hyp01 = HYPOTHESES[0]
    outm, entry = _masked_signals(hyp01, "nr7_break", fx_nan)
    r_nan = eval_cell(outm, entry, fx_nan, 1.0, 2.0, 32)
    t2 = all_false and trap_ok and r_nan["n"] == 0
    print(f"  [2] NaN exclusion: allow all-False={all_false} >=0-trap(NaN->False)={trap_ok} "
          f"trades=0={r_nan['n'] == 0}")
    ok = ok and t2

    # [3] ONE-SIDED INAFIKA episodes: ctx aligned-up -> HC2-01 (stop) na HC2-03 (market)
    #     zinatoa trades za LONG TU (allow_short=False by construction ya conditions)
    fx_up = _fixture(4)
    om1, e1 = _masked_signals(HYPOTHESES[0], "nr7_break", fx_up)
    trs1 = episodes(om1, e1, fx_up["o"], fx_up["h"], fx_up["l"], fx_up["c"], fx_up["atr"],
                    fx_up["spr"], fx_up["hour"], fx_up["vol"], sl_atr=1.0, tp_atr=2.0, max_hold=32)
    om3, e3 = _masked_signals(HYPOTHESES[1], "trend_resume", fx_up)
    trs3 = episodes(om3, e3, fx_up["o"], fx_up["h"], fx_up["l"], fx_up["c"], fx_up["atr"],
                    fx_up["spr"], fx_up["hour"], fx_up["vol"], sl_atr=1.0, tp_atr=2.0, max_hold=32)
    t3 = (len(trs1) > 0 and all(t[2] == 1 for t in trs1)
          and len(trs3) > 0 and all(t[2] == 1 for t in trs3))
    print(f"  [3] one-sided->episodes: HC2-01 stop long-only (n={len(trs1)}) "
          f"HC2-03 market long-only (n={len(trs3)}) -> {t3}")
    ok = ok and t3

    # [4] HC2-06 CONDITIONS TOFAUTI long/short: karibu na support (trend 0) -> long TU;
    #     karibu na resistance -> short TU
    n4 = 3000
    fx_sup = _fixture(5, n=n4, ctx=dict(h4_trend_sign=np.zeros(n4),
                                        d1_dist_sup_atr=np.full(n4, 0.3),
                                        d1_dist_res_atr=np.full(n4, 2.0)))
    fx_res = _fixture(5, n=n4, ctx=dict(h4_trend_sign=np.zeros(n4),
                                        d1_dist_sup_atr=np.full(n4, 2.0),
                                        d1_dist_res_atr=np.full(n4, 0.3)))
    hyp06 = HYPOTHESES[2]
    oms, es = _masked_signals(hyp06, "bb_fade", fx_sup)
    omr, _ = _masked_signals(hyp06, "bb_fade", fx_res)
    ts_ = episodes(oms, es, fx_sup["o"], fx_sup["h"], fx_sup["l"], fx_sup["c"], fx_sup["atr"],
                   fx_sup["spr"], fx_sup["hour"], fx_sup["vol"], sl_atr=1.0, tp_atr=1.5, max_hold=24)
    tr_ = episodes(omr, es, fx_res["o"], fx_res["h"], fx_res["l"], fx_res["c"], fx_res["atr"],
                   fx_res["spr"], fx_res["hour"], fx_res["vol"], sl_atr=1.0, tp_atr=1.5, max_hold=24)
    t4 = (len(ts_) > 0 and all(t[2] == 1 for t in ts_)
          and len(tr_) > 0 and all(t[2] == -1 for t in tr_))
    print(f"  [4] HC2-06 asymmetric: support->long-only (n={len(ts_)}) "
          f"resistance->short-only (n={len(tr_)}) -> {t4}")
    ok = ok and t4

    # [5]+[6] FULL PIPELINE (monkeypatch load_window na fixtures) + DETERMINISM + outputs + guard
    import tempfile
    _self = sys.modules[__name__]
    pairs_all = sorted({p for h in HYPOTHESES for p in h["pairs"]})
    fx = {p: _fixture(30 + k) for k, p in enumerate(pairs_all)}
    fx[pairs_all[0]] = dict(fx[pairs_all[0]], ctx=None)              # pair moja: ctx haipo -> skip
    orig = _self.load_window
    _self.load_window = lambda sym, tf, split, token=None: fx.get(sym)
    try:
        with tempfile.TemporaryDirectory() as tmp:
            rows_a = run("train", out_root=tmp)
            rows_b = run("train", out_root=tmp)
            det = json.dumps(rows_a, sort_keys=True) == json.dumps(rows_b, sort_keys=True)
            n_rows = len(rows_a) == 84
            skip_rows = [r for r in rows_a if r.get("skipped")]
            skip_ok = all(r["pair"] == pairs_all[0] and r["n"] == 0 for r in skip_rows) and skip_rows
            traded = [r for r in rows_a if r.get("n", 0) > 0]
            fields_ok = all({"ev", "gross", "cost_share", "win", "pf", "timeout_share",
                             "min_n_ok", "days"} <= set(r) for r in traded if r["n"] > 0)
            jl = Path(tmp) / "data" / "strategies" / OUT_JSONL
            rpt = Path(tmp) / "reports" / OUT_REPORT
            recs = [json.loads(ln) for ln in open(jl, encoding="utf-8")]
            out_ok = (jl.exists() and rpt.exists() and len(recs) == 84
                      and all(r["split"] == "train" for r in recs))
        try:
            run("validation", write=False)
            guard_ok = False
        except PermissionError:
            guard_ok = True
    finally:
        _self.load_window = orig
    t56 = det and n_rows and bool(skip_ok) and fields_ok and out_ok and guard_ok
    print(f"  [5] determinism={det} rows=84={n_rows} skip-pair(ctx=None)->n=0={bool(skip_ok)}")
    print(f"  [6] outputs: jsonl 84 rows + report={out_ok} fields={fields_ok} "
          f"TRAIN-only guard (validation->refuse)={guard_ok}")
    ok = ok and t56

    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", action="store_true", help="endesha grid FROZEN kwenye TRAIN (PC ya data)")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.train:
        print("Tumia --train (S1 TRAIN run) au --self-test.", file=sys.stderr)
        return 2
    rows = run("train")
    traded = [r for r in rows if r.get("min_n_ok")]
    pos = [r for r in traded if r.get("ev", 0) > 0]
    print(f"WAVE-C2-A S1 TRAIN: cells={len(rows)} N>=MIN_N={len(traded)} EV>0={len(pos)}")
    print(f"  data/strategies/{OUT_JSONL}\n  reports/{OUT_REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
