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
from strategy_lab import _mask_context_dir, load_window, MIN_N, pvalue_boot, pvalue_gt0, bh_fdr

REPO_ROOT = Path(__file__).resolve().parents[2]
TF = "30m"                                     # registration: TF ya entry = 30m (shared)
OUT_JSONL = "wave_c2a_train.jsonl"
OUT_REPORT = "wave_c2a_s1_train.md"

# ---------- C2-4: S2 VALIDATION (docs/WAVE_C2A_S2_REGISTRATION.md — FROZEN na Chief) ----------
# HC2-03 PEKEE, EURUSD PEKEE, 30m. Cells 7 KAMA ZILIVYO kwenye registration §Cells (order ya
# jedwali; (trigger, sl, tp, max_hold)). Hakuna cell ya ziada, hakuna re-selection.
S2_HYP_ID = "HC2-03"
S2_PAIR = "EURUSD"
S2_CELLS = (
    ("trend_resume", 1.0, 3.0, 32),
    ("trend_resume", 1.5, 3.0, 32),
    ("trend_resume", 1.5, 2.0, 32),
    ("trend_resume", 1.0, 2.0, 32),
    ("rsi2_pullback", 1.0, 2.0, 32),
    ("rsi2_pullback", 1.5, 2.0, 32),
    ("rsi2_pullback", 1.0, 3.0, 32),
)
S2_B = 50_000                                  # registration: pvalue_boot B=50k (engine RASMI)
S2_Q = 0.10                                    # registration: BH-FDR q=0.10 kati ya cells 7
S2_OUT_JSONL = "wave_c2a_s2_valid.jsonl"
S2_OUT_REPORT = "wave_c2a_s2_valid.md"


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


# HC2-10 FAILED-BREAK-SWEEP (WAVE-B; docs/WAVE_C2B_HC210_REGISTRATION.md) — pure sweep kwenye D1
# extreme, HAKUNA h4 condition (tofauti na HC2-06). isfinite guard: NaN -> allow False.
def _hc210_allow_long(ctx):
    sup = _fin(ctx, "d1_dist_sup_atr")
    with np.errstate(invalid="ignore"):
        return np.isfinite(sup) & (sup <= 0.5)


def _hc210_allow_short(ctx):
    res = _fin(ctx, "d1_dist_res_atr")
    with np.errstate(invalid="ignore"):
        return np.isfinite(res) & (res <= 0.5)


# WAVE-A (C2-3/C2-4) = hypotheses 3 za awali. HC2-10 ni WAVE-B — ni opt-in kupitia --hyp/only PEKEE;
# run()/cells() bila `only` zinabaki WAVE-A (tabia ya zamani, cells=84).
WAVE_A_IDS = ("HC2-01", "HC2-03", "HC2-06")


# ---------- HYPOTHESES (grid FROZEN — thamani KAMA ZILIVYO kwenye registration) ----------
HYPOTHESES = (
    dict(id="HC2-01", name="ALIGNED-COMPRESSION", tf="30m",
         triggers=("nr7_break", "nr4_inside"),
         allow_long=lambda ctx: _hc201_allow(ctx, +1),
         allow_short=lambda ctx: _hc201_allow(ctx, -1),
         sl=(1.0, 1.5), tp=(2.0, 3.0), max_hold=32,
         pairs=("USDCHF", "USDJPY", "EURJPY", "AUDUSD", "GBPJPY")),          # cells 2x4x5 = 40
    dict(id="HC2-03", name="TREND-PULLBACK-RESUME", tf="30m",
         triggers=("trend_resume", "rsi2_pullback"),
         allow_long=lambda ctx: _hc203_allow(ctx, +1),
         allow_short=lambda ctx: _hc203_allow(ctx, -1),
         sl=(1.0, 1.5), tp=(2.0, 3.0), max_hold=32,
         pairs=("USDJPY", "GBPJPY", "EURUSD")),                              # cells 2x4x3 = 24
    dict(id="HC2-06", name="HTF-SR-FADE", tf="30m",
         triggers=("bb_fade", "engulf_extreme"),
         allow_long=_hc206_allow_long,
         allow_short=_hc206_allow_short,
         sl=(1.0, 1.5), tp=(1.5,), max_hold=24,
         pairs=("EURGBP", "EURCHF", "USDCHF", "AUDUSD", "NZDUSD")),          # cells 2x2x5 = 20
    dict(id="HC2-10", name="FAILED-BREAK-SWEEP", tf="30m",
         triggers=("false_break",),
         allow_long=_hc210_allow_long, allow_short=_hc210_allow_short,
         sl=(1.0, 1.5), tp=(2.0, 3.0), max_hold=24,
         pairs=("EURGBP", "EURCHF", "AUDUSD", "NZDUSD", "XAUUSD")),          # cells 1x4x5 = 20
    # WAVE-B2 (docs/WAVE_B2_REGISTRATION.md) — selective-structure @ H1 (moves kubwa per trade ->
    # cost-ratio bora; LESSON-039). XAUUSD NJE kwa makusudi (fade-on-gold mismatch). tf="H1".
    dict(id="HB2-06", name="HTF-SR-FADE-H1", tf="H1",
         triggers=("bb_fade", "engulf_extreme"),
         allow_long=_hc206_allow_long, allow_short=_hc206_allow_short,       # fns zilezile (D1/H4)
         sl=(1.0, 1.5), tp=(1.5, 2.0), max_hold=16,
         pairs=("EURGBP", "EURCHF", "USDCHF", "AUDUSD", "NZDUSD")),          # cells 2x4x5 = 40
    dict(id="HB2-10", name="FAILED-BREAK-SWEEP-H1", tf="H1",
         triggers=("false_break",),
         allow_long=_hc210_allow_long, allow_short=_hc210_allow_short,       # D1-extreme, hakuna h4
         sl=(1.0, 1.5), tp=(2.0, 3.0), max_hold=16,
         pairs=("EURGBP", "EURCHF", "USDCHF", "AUDUSD", "NZDUSD")),          # cells 1x4x5 = 20
)


def _active_ids(only):
    """Rudisha tuple ya hypothesis-ids zilizochaguliwa. `only=None` -> WAVE_A_IDS (default @30m).
    `only` = string moja au comma-list (mf. 'HB2-06,HB2-10'). Bad id -> ValueError."""
    if only is None:
        return WAVE_A_IDS
    ids = [x.strip() for x in str(only).split(",") if x.strip()]
    valid = {h["id"] for h in HYPOTHESES}
    bad = [i for i in ids if i not in valid]
    if bad:
        raise ValueError(f"--hyp id haipo kwenye HYPOTHESES: {', '.join(bad)}")
    return tuple(ids)


def cells(only=None):
    """Enumerate cells za grid FROZEN. `only=None` -> WAVE-A (m=84; FDR ya S2 inahesabu HII);
    `only=<id[,id...]>` -> hypotheses zilizochaguliwa (mf. HC2-10 -> 20; HB2-06,HB2-10 -> 60).
    Kila cell inabeba `tf` ya hypothesis (default '30m'). WAVE-B (HC2-10/HB2-*) haimo kwenye default."""
    active = _active_ids(only)
    out = []
    for hyp in HYPOTHESES:
        if hyp["id"] not in active:
            continue
        for trig in hyp["triggers"]:
            for pair in hyp["pairs"]:
                for sl in hyp["sl"]:
                    for tp in hyp["tp"]:
                        out.append(dict(hypothesis=hyp["id"], tf=hyp["tf"], trigger=trig, pair=pair,
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


def run(split="train", out_root=REPO_ROOT, write=True, only=None):
    """Endesha grid FROZEN. GUARD: S1 ya WAVE-C2-A ni TRAIN PEKEE — split nyingine inakataliwa
    hapa (na sacred-splits guard ya load_window inabaki chini yake). Rudisha rows za cells zote.
    `only=<id>` (mf. HC2-10) inachuja hypothesis moja + inaandika outputs zenye suffix (HAIFUTI
    WAVE-A). `only=None` -> WAVE-A (tabia ya zamani, 84 cells)."""
    if split != "train":
        raise PermissionError("C2-3 ni TRAIN PEKEE (S1 exploration) — VALID/HOLDOUT haziguswi hapa")
    active = _active_ids(only)                        # raises ValueError kwa id mbaya
    # load_window kwa (pair, tf) — hypotheses zinaweza kuwa na TF tofauti (WAVE-A 30m, WAVE-B2 H1).
    pairs_tf = sorted({(p, hyp["tf"]) for hyp in HYPOTHESES if hyp["id"] in active
                       for p in hyp["pairs"]})
    cache = {(p, tf): load_window(p, tf, split) for (p, tf) in pairs_tf}
    skipped = []
    for (p, tf) in pairs_tf:
        d = cache[(p, tf)]
        if d is None or d.get("ctx") is None:
            why = "state parquet haipo/fupi" if d is None else "context parquet haipo (ctx=None)"
            print(f"  ONYO: {p}/{tf} — {why}; cells za pair hii zinarukwa (zinabaki kwenye jsonl kama n=0)")
            skipped.append(f"{p}/{tf}")

    rows = []
    sig_cache = {}
    for cell in cells(only):
        pair = cell["pair"]; tf = cell["tf"]
        data = cache[(pair, tf)]
        rec = dict(cell, days=(data["days"] if data is not None else 0))
        if data is None or data.get("ctx") is None:
            rec.update(n=0, skipped=True)
            rows.append(rec)
            continue
        hyp = next(h for h in HYPOTHESES if h["id"] == cell["hypothesis"])
        key = (cell["hypothesis"], cell["trigger"], pair, tf)
        if key not in sig_cache:
            sig_cache[key] = _masked_signals(hyp, cell["trigger"], data)
        out_masked, entry = sig_cache[key]
        rec.update(eval_cell(out_masked, entry, data, cell["sl_atr"], cell["tp_atr"],
                             cell["max_hold"]))
        rows.append(rec)
    if write:
        _write_outputs(rows, split, out_root, skipped, only=only)
    return rows


# ---------- outputs ----------

def _write_outputs(rows, split, out_root, skipped=(), only=None):
    out_root = Path(out_root)
    # `only` -> suffix ili USIFUTE outputs za WAVE-A (mf. HC2-10 -> wave_c2a_train_HC2-10.jsonl /
    # reports/wave_c2b_hc210_s1_train.md). None -> majina ya zamani (byte-identical).
    if only is None:
        jl_name, rpt_name = OUT_JSONL, OUT_REPORT
        head, title_m = "WAVE-C2-A", "grid FROZEN m=84; docs/WAVE_C2A_REGISTRATION.md"
    else:
        suffix = "+".join(_active_ids(only))                       # HC2-10 | HB2-06+HB2-10
        slug = suffix.replace("-", "").lower()                     # -> hc210 | hb206+hb210
        jl_name = f"wave_c2a_train_{suffix}.jsonl"
        rpt_name = f"wave_c2b_{slug}_s1_train.md"
        title_m = f"{suffix} grid FROZEN m={len(rows)}"
        head = "WAVE-B"
    tfs = "/".join(sorted({r.get("tf", TF) for r in rows}))        # 30m (WAVE-A) | H1 (WAVE-B2)
    sdir = out_root / "data" / "strategies"; sdir.mkdir(parents=True, exist_ok=True)
    jl = sdir / jl_name
    with open(jl, "w", encoding="utf-8") as f:
        for r in rows:
            rec = dict(r); rec["split"] = split
            f.write(json.dumps(rec, sort_keys=True) + "\n")

    L = [f"# {head} — S1 TRAIN ({title_m})\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | TF={tfs} | split={split.upper()} (2016-2022 PEKEE) | "
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
    present_ids = {r["hypothesis"] for r in rows}
    for hyp in HYPOTHESES:
        if hyp["id"] not in present_ids:
            continue
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

    rpt = out_root / "reports" / rpt_name; rpt.parent.mkdir(parents=True, exist_ok=True)
    rpt.write_text("\n".join(L), encoding="utf-8")
    return jl, rpt


# ---------- C2-4: S2 VALIDATION runner (ADDITIVE — S1 haiguswi) ----------

def _s2_cell_id(trig, sl, tp):
    """dict ya cell kwa seed ya pvalue_boot (_seed_from_key: event/pair/sl/tp/filters) + `id` string.
    session_filter=S2_HYP_ID inatofautisha seeds na grids nyingine za pair/trigger ileile."""
    return dict(hypothesis=S2_HYP_ID, event=trig, pair=S2_PAIR, sl_atr=sl, tp_atr=tp,
                session_filter=S2_HYP_ID, vol_filter=None,
                id=f"{S2_HYP_ID}|{trig}|{S2_PAIR}|SL{sl}/TP{tp}")


def s2_verdict(cells_pnls, q=S2_Q, B=S2_B):
    """Test RASMI ya registration juu ya streams za cells 7: kila cell -> pvalue_boot (engine RASMI
    ya strategy_lab — B, mean_block=3, seed deterministic kutoka cell) + p_z (sensitivity, SI
    decision) -> bh_fdr(q) kati ya cells ZOTE zilizopita (m=len). Survivor = fdr_pass NA EV_net>0.
    HAKUNA statistic mpya hapa — orchestration tu (pvalue_boot/pvalue_gt0/bh_fdr haziguswi)."""
    rows = []
    for cid, pnls in cells_pnls:
        m = _metrics(pnls)
        rows.append(dict(cid, n=m["n"],
                         ev_net=(round(m["ev"], 4) if m["n"] else None),
                         win=(round(m["win"], 4) if m["n"] else None),
                         p_boot=round(float(pvalue_boot(pnls, B=B, mean_block=3, cell=cid)), 6),
                         p_z=round(float(pvalue_gt0(pnls)), 6)))
    surv, k, exp_false = bh_fdr([r["p_boot"] for r in rows], q)
    for r, s in zip(rows, surv):
        r["fdr_pass"] = bool(s)
        r["survivor"] = bool(s and (r["ev_net"] is not None) and r["ev_net"] > 0)
    return rows, int(k), exp_false


def run_s2(split="validation", out_root=REPO_ROOT, write=True, B=S2_B):
    """C2-4: endesha cells 7 FROZEN kwenye VALIDATION + BH-FDR. GUARD: 'validation' PEKEE —
    TRAIN imekwisha (S1); HOLDOUT inahitaji token CHIEF-HOLDOUT-S3 kwenye C2-6, SI hapa."""
    if split != "validation":
        raise PermissionError("C2-4 S2 ni VALIDATION PEKEE — TRAIN imekwisha (S1); "
                              "HOLDOUT = C2-6 one-shot (token CHIEF-HOLDOUT-S3), SI hapa")
    data = load_window(S2_PAIR, TF, split)
    if data is None or data.get("ctx") is None:
        print(f"HITILAFU: {S2_PAIR}/{TF} state/context parquet haipo (endesha intraday_state_engine"
              " + htf_context kwanza).", file=sys.stderr)
        return None
    hyp = next(h for h in HYPOTHESES if h["id"] == S2_HYP_ID)
    sig_cache = {}
    cells_pnls = []
    for trig, sl, tp, mh in S2_CELLS:
        if trig not in sig_cache:
            sig_cache[trig] = _masked_signals(hyp, trig, data)
        out_masked, entry = sig_cache[trig]
        trs = episodes(out_masked, entry, data["o"], data["h"], data["l"], data["c"],
                       data["atr"], data["spr"], data["hour"], data.get("vol"),
                       sl_atr=sl, tp_atr=tp, max_hold=mh)
        cells_pnls.append((_s2_cell_id(trig, sl, tp), [t[3] for t in trs]))
    rows, k, exp_false = s2_verdict(cells_pnls, q=S2_Q, B=B)
    if write:
        _write_s2(rows, k, exp_false, split, out_root)
    return rows


def _write_s2(rows, k, exp_false, split, out_root):
    out_root = Path(out_root)
    sdir = out_root / "data" / "strategies"; sdir.mkdir(parents=True, exist_ok=True)
    jl = sdir / S2_OUT_JSONL
    with open(jl, "w", encoding="utf-8") as f:
        for r in rows:
            rec = {kk: vv for kk, vv in r.items() if kk not in ("session_filter", "vol_filter")}
            rec["split"] = split
            f.write(json.dumps(rec, sort_keys=True) + "\n")

    survivors = [r for r in rows if r["survivor"]]
    L = [f"# WAVE-C2-A — S2 VALIDATION (cells 7 FROZEN; docs/WAVE_C2A_S2_REGISTRATION.md)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | {S2_HYP_ID} x {S2_PAIR} x {TF} | split={split.upper()} "
         f"(2023-2024) | m={len(rows)} | engine RASMI: pvalue_boot B={S2_B:,} mean_block=3 | "
         f"BH-FDR q={S2_Q} | criterion: fdr_pass NA EV_net>0 | p_z = sensitivity (SI decision)*\n"]
    if survivors:
        L.append(f"## SURVIVORS ({len(survivors)}) — wanaendelea C2-6 freeze -> HOLDOUT one-shot\n")
        L.append("| id | N | EV net | win% | p_boot (RASMI) | p_z (sens.) |")
        L.append("|----|---|--------|------|----------------|-------------|")
        for r in sorted(survivors, key=lambda x: x["p_boot"]):
            L.append(f"| {r['id']} | {r['n']:,} | {r['ev_net']:+.3f} | {r['win']*100:.1f} | "
                     f"{r['p_boot']:.4f} | {r['p_z']:.4f} |")
    else:
        L.append("## HAKUNA SURVIVOR — HC2-03 haujathibitika OOS\n")
        L.append("Cells 7 za FROZEN hazikupita BH-FDR (q=0.10) NA EV_net>0 kwenye VALIDATION. "
                 "Kwa registration: hii ni FAIL kwa heshima — LESSON; portfolio inabaki "
                 "STRAT-001/002. (Tahadhari ya awali ya registration: TRAIN EVs ndogo + shrinkage.)")
    L.append(f"\n## Cells zote 7 (accounting kamili; BH k={k}, ~{exp_false} kwa bahati)\n")
    L.append("| id | N | EV net | p_boot | p_z | fdr_pass | survivor |")
    L.append("|----|---|--------|--------|-----|----------|----------|")
    for r in rows:
        ev = f"{r['ev_net']:+.3f}" if r["ev_net"] is not None else "—"
        L.append(f"| {r['id']} | {r['n']:,} | {ev} | {r['p_boot']:.4f} | {r['p_z']:.4f} | "
                 f"{'YES' if r['fdr_pass'] else 'no'} | {'**YES**' if r['survivor'] else 'no'} |")
    L.append("\n*VALIDATION ime-consumed kwa cells hizi 7 (pre-registered). HOLDOUT HAIJAGUSWA "
             "(token C2-6). Engine RASMI haijabadilika. Profitable != Tradable Edge.*")
    rpt = out_root / "reports" / S2_OUT_REPORT; rpt.parent.mkdir(parents=True, exist_ok=True)
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
    per = {hid: sum(1 for c_ in cs if c_["hypothesis"] == hid) for hid in WAVE_A_IDS}
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

    # ===== C2-4: S2 VALIDATION checks =====

    # [7] S2_CELLS FROZEN == registration §Cells: 7 hasa, HC2-03/EURUSD/30m, triggers/SL/TP/max_hold
    reg = {("trend_resume", 1.0, 3.0, 32), ("trend_resume", 1.5, 3.0, 32),
           ("trend_resume", 1.5, 2.0, 32), ("trend_resume", 1.0, 2.0, 32),
           ("rsi2_pullback", 1.0, 2.0, 32), ("rsi2_pullback", 1.5, 2.0, 32),
           ("rsi2_pullback", 1.0, 3.0, 32)}
    t7 = (len(S2_CELLS) == 7 and set(S2_CELLS) == reg and S2_PAIR == "EURUSD"
          and S2_HYP_ID == "HC2-03" and TF == "30m" and S2_B == 50_000 and S2_Q == 0.10)
    print(f"  [7] S2_CELLS FROZEN == registration (7; HC2-03/EURUSD/30m; B=50k q=0.10) -> {t7}")
    ok = ok and t7

    # [8] engine RASMI + seed determinism: p_boot ya s2_verdict == pvalue_boot(cell=cid) direct,
    #     na inarudiwa bit-kwa-bit (seed kutoka cell key)
    rng8 = np.random.default_rng(88)
    pn8 = list(rng8.normal(0.5, 2.0, 90))
    cid8 = _s2_cell_id("trend_resume", 1.0, 3.0)
    rows8a, _, _ = s2_verdict([(cid8, pn8)], B=1500)
    rows8b, _, _ = s2_verdict([(cid8, pn8)], B=1500)
    direct = round(float(pvalue_boot(pn8, B=1500, mean_block=3, cell=cid8)), 6)
    t8 = rows8a[0]["p_boot"] == rows8b[0]["p_boot"] == direct
    print(f"  [8] engine RASMI (pvalue_boot cell-seeded, mean_block=3) + determinism: "
          f"{rows8a[0]['p_boot']} == direct {direct} -> {t8}")
    ok = ok and t8

    # [9] BH-FDR m=7: s2_verdict flags == bh_fdr(p_boots zote 7, q=0.10) recomputed nje
    rng9 = np.random.default_rng(99)
    fix9 = [(_s2_cell_id(tr, sl, tp), list(rng9.normal(0.2 * i, 2.0, 80)))
            for i, (tr, sl, tp, mh) in enumerate(S2_CELLS)]
    rows9, k9, _ = s2_verdict(fix9, B=1200)
    surv9, k9b, _ = bh_fdr([r["p_boot"] for r in rows9], S2_Q)
    t9 = (len(rows9) == 7 and k9 == k9b
          and [r["fdr_pass"] for r in rows9] == list(map(bool, surv9)))
    print(f"  [9] BH-FDR m=7 (flags == recompute nje; k={k9}) -> {t9}")
    ok = ok and t9

    # [10] GUARD: run_s2 inakubali validation PEKEE — train/holdout -> refuse KABLA ya kusoma data
    g_train = g_hold = False
    try:
        run_s2("train", write=False)
    except PermissionError:
        g_train = True
    try:
        run_s2("holdout", write=False)
    except PermissionError:
        g_hold = True
    print(f"  [10] guard: train-refused={g_train} holdout-refused={g_hold} -> {g_train and g_hold}")
    ok = ok and g_train and g_hold

    # [11] survivor logic: edge chanya wazi -> FDR-pass + survivor; noise -> hakuna
    rng11 = np.random.default_rng(11)
    strong = list(rng11.normal(2.0, 1.0, 120))                       # edge wazi (EV +2)
    fix11 = [(_s2_cell_id("trend_resume", 1.0, 3.0), strong)]
    fix11 += [(_s2_cell_id("rsi2_pullback", 1.0, 2.0 + i), list(rng11.normal(0.0, 2.0, 100)))
              for i in range(6)]                                     # noise 6
    rows11, _, _ = s2_verdict(fix11, B=1500)
    sv = [r for r in rows11 if r["survivor"]]
    t11 = (len(sv) == 1 and sv[0]["id"].startswith("HC2-03|trend_resume") and sv[0]["ev_net"] > 0
           and all(not r["survivor"] for r in rows11[1:]))
    print(f"  [11] survivor logic: strong-edge->survivor(1), noise->0 -> {t11}")
    ok = ok and t11

    # [12] full S2 pipeline (monkeypatch load_window; B ndogo): rows 7, outputs, determinism
    import tempfile
    _self = sys.modules[__name__]
    orig = _self.load_window
    fx12 = _fixture(77)
    _self.load_window = lambda sym, tf, split, token=None: fx12 if sym == S2_PAIR else None
    try:
        with tempfile.TemporaryDirectory() as tmp:
            ra = run_s2("validation", out_root=tmp, B=800)
            rb = run_s2("validation", out_root=tmp, B=800)
            det12 = json.dumps(ra, sort_keys=True) == json.dumps(rb, sort_keys=True)
            jl = Path(tmp) / "data" / "strategies" / S2_OUT_JSONL
            rpt = Path(tmp) / "reports" / S2_OUT_REPORT
            recs = [json.loads(ln) for ln in open(jl, encoding="utf-8")]
            fields12 = all({"id", "n", "ev_net", "p_boot", "p_z", "fdr_pass", "survivor",
                            "split"} <= set(r) for r in recs)
            txt = rpt.read_text(encoding="utf-8")
            named12 = ("SURVIVORS" in txt) or ("HAKUNA SURVIVOR" in txt and "haujathibitika OOS" in txt)
            t12 = det12 and len(ra) == 7 and len(recs) == 7 and fields12 and named12
    finally:
        _self.load_window = orig
    print(f"  [12] S2 pipeline: rows=7 determinism={det12} jsonl-fields={fields12} report-verdict={named12} -> {t12}")
    ok = ok and t12

    # ===== WAVE-B: HC2-10 FAILED-BREAK-SWEEP checks =====

    # [13] HC2-10 cells == 20 (pairs 5 x SL/TP 4 x trigger 1); default cells() bado 84 (WAVE-A;
    #      HC2-10 haimo). Grid KAMA registration (false_break; SL{1,1.5}xTP{2,3}; max_hold 24).
    c10 = cells(only="HC2-10")
    t13 = (len(c10) == 20 and len(cells()) == 84
           and {c_["trigger"] for c_ in c10} == {"false_break"}
           and {c_["pair"] for c_ in c10} == {"EURGBP", "EURCHF", "AUDUSD", "NZDUSD", "XAUUSD"}
           and {(c_["sl_atr"], c_["tp_atr"]) for c_ in c10} == {(1.0, 2.0), (1.0, 3.0), (1.5, 2.0), (1.5, 3.0)}
           and all(c_["max_hold"] == 24 for c_ in c10)
           and not any(c_["hypothesis"] == "HC2-10" for c_ in cells()))
    print(f"  [13] HC2-10 grid: cells={len(c10)}(==20) default-cells={len(cells())}(==84, no HC2-10) -> {t13}")
    ok = ok and t13

    # [14] allow fns: isfinite guard (NaN -> False) + threshold (<=0.5 True, >0.5 False); hakuna h4
    n14 = 6
    ctx_nan10 = dict(d1_dist_sup_atr=np.full(n14, np.nan), d1_dist_res_atr=np.full(n14, np.nan))
    ctx_in = dict(d1_dist_sup_atr=np.full(n14, 0.3), d1_dist_res_atr=np.full(n14, 0.4))
    ctx_out = dict(d1_dist_sup_atr=np.full(n14, 0.9), d1_dist_res_atr=np.full(n14, 1.2))
    t14 = (not _hc210_allow_long(ctx_nan10).any() and not _hc210_allow_short(ctx_nan10).any()
           and _hc210_allow_long(ctx_in).all() and _hc210_allow_short(ctx_in).all()
           and not _hc210_allow_long(ctx_out).any() and not _hc210_allow_short(ctx_out).any())
    print(f"  [14] HC2-10 allow: NaN->False + (<=0.5)->True + (>0.5)->False (no h4) -> {t14}")
    ok = ok and t14

    # [15] false_break -> _mask_context_dir -> episodes: support extreme -> long TU;
    #      resistance extreme -> short TU (conditions tofauti long/short zafika episodes)
    n15 = 4000
    fx_sup10 = _fixture(21, n=n15, ctx=dict(d1_dist_sup_atr=np.full(n15, 0.3),
                                            d1_dist_res_atr=np.full(n15, 2.0)))
    fx_res10 = _fixture(21, n=n15, ctx=dict(d1_dist_sup_atr=np.full(n15, 2.0),
                                            d1_dist_res_atr=np.full(n15, 0.3)))
    hyp10 = next(h for h in HYPOTHESES if h["id"] == "HC2-10")
    oms10, es10 = _masked_signals(hyp10, "false_break", fx_sup10)
    omr10, _ = _masked_signals(hyp10, "false_break", fx_res10)
    ts10 = episodes(oms10, es10, fx_sup10["o"], fx_sup10["h"], fx_sup10["l"], fx_sup10["c"],
                    fx_sup10["atr"], fx_sup10["spr"], fx_sup10["hour"], fx_sup10["vol"],
                    sl_atr=1.0, tp_atr=2.0, max_hold=24)
    tr10 = episodes(omr10, es10, fx_res10["o"], fx_res10["h"], fx_res10["l"], fx_res10["c"],
                    fx_res10["atr"], fx_res10["spr"], fx_res10["hour"], fx_res10["vol"],
                    sl_atr=1.0, tp_atr=2.0, max_hold=24)
    t15 = (es10 == "market" and len(ts10) > 0 and all(t[2] == 1 for t in ts10)
           and len(tr10) > 0 and all(t[2] == -1 for t in tr10))
    print(f"  [15] false_break->mask->episodes: support->long(n={len(ts10)}) "
          f"resistance->short(n={len(tr10)}) entry=market -> {t15}")
    ok = ok and t15

    # [16] HYP-FILTER pipeline: run(only=HC2-10) -> 20 rows HC2-10 TU + outputs zenye suffix
    #      (HAIFUTI WAVE-A); run() default -> 84 rows WAVE-A (hakuna HC2-10)
    import tempfile
    _self = sys.modules[__name__]
    pairs16 = sorted({p for h in HYPOTHESES for p in h["pairs"]})
    fx16 = {p: _fixture(40 + k) for k, p in enumerate(pairs16)}
    orig = _self.load_window
    _self.load_window = lambda sym, tf, split, token=None: fx16.get(sym)
    try:
        with tempfile.TemporaryDirectory() as tmp:
            r10 = run("train", out_root=tmp, only="HC2-10")
            rA = run("train", out_root=tmp)
            jl10 = Path(tmp) / "data" / "strategies" / "wave_c2a_train_HC2-10.jsonl"
            rp10 = Path(tmp) / "reports" / "wave_c2b_hc210_s1_train.md"
            jlA = Path(tmp) / "data" / "strategies" / OUT_JSONL
            rpA = Path(tmp) / "reports" / OUT_REPORT
            recs10 = [json.loads(ln) for ln in open(jl10, encoding="utf-8")]
            filt_ok = (len(r10) == 20 and all(r["hypothesis"] == "HC2-10" for r in r10)
                       and len(rA) == 84 and not any(r["hypothesis"] == "HC2-10" for r in rA))
            files_ok = (jl10.exists() and rp10.exists() and jlA.exists() and rpA.exists()
                        and jl10 != jlA and len(recs10) == 20
                        and all(r["hypothesis"] == "HC2-10" for r in recs10))
            title_ok = "WAVE-B" in rp10.read_text(encoding="utf-8")
            # bad id -> ValueError
            try:
                run("train", out_root=tmp, only="HC9-99"); bad_ok = False
            except ValueError:
                bad_ok = True
        t16 = filt_ok and files_ok and title_ok and bad_ok
    finally:
        _self.load_window = orig
    print(f"  [16] hyp-filter: run(only=HC2-10)->20 rows + suffix files (WAVE-A intact, 84); "
          f"bad-id->ValueError={bad_ok} -> {t16}")
    ok = ok and t16

    # ===== WAVE-B2: selective-structure @ H1 checks =====

    # [17] HB2 grid: cells == 60 (HB2-06 40 + HB2-10 20), tf=="H1" zote, XAUUSD NJE; WAVE-A default
    #      bado 84 @30m (regression) na haina HB2-*
    cH = cells(only="HB2-06,HB2-10")
    per_hb = {hid: sum(1 for c_ in cH if c_["hypothesis"] == hid) for hid in ("HB2-06", "HB2-10")}
    dflt = cells()
    t17 = (len(cH) == 60 and per_hb == {"HB2-06": 40, "HB2-10": 20}
           and {c_["tf"] for c_ in cH} == {"H1"}
           and not any(c_["pair"] == "XAUUSD" for c_ in cH)
           and len(dflt) == 84 and {c_["tf"] for c_ in dflt} == {"30m"}
           and not any(c_["hypothesis"] in ("HB2-06", "HB2-10") for c_ in dflt))
    print(f"  [17] HB2 grid: cells={len(cH)}(==60) per-hyp={per_hb} tf=H1 no-gold=True | "
          f"WAVE-A default={len(dflt)}(==84)@30m -> {t17}")
    ok = ok and t17

    # [18] HYP-FILTER comma-list pipeline: run(only='HB2-06,HB2-10') -> 60 rows (H1, HB2 tu) +
    #      outputs suffix wa comma-list (HAIFUTI WAVE-A); WAVE-A default bado 84
    import tempfile
    _self = sys.modules[__name__]
    pairs18 = sorted({p for h in HYPOTHESES for p in h["pairs"]})
    fx18 = {p: _fixture(60 + k) for k, p in enumerate(pairs18)}
    orig = _self.load_window
    _self.load_window = lambda sym, tf, split, token=None: fx18.get(sym)
    try:
        with tempfile.TemporaryDirectory() as tmp:
            rHB = run("train", out_root=tmp, only="HB2-06,HB2-10")
            rA18 = run("train", out_root=tmp)
            jlHB = Path(tmp) / "data" / "strategies" / "wave_c2a_train_HB2-06+HB2-10.jsonl"
            rpHB = Path(tmp) / "reports" / "wave_c2b_hb206+hb210_s1_train.md"
            jlA18 = Path(tmp) / "data" / "strategies" / OUT_JSONL
            recsHB = [json.loads(ln) for ln in open(jlHB, encoding="utf-8")]
            filt18 = (len(rHB) == 60 and {r["hypothesis"] for r in rHB} == {"HB2-06", "HB2-10"}
                      and all(r["tf"] == "H1" for r in rHB)
                      and len(rA18) == 84 and not any(r["hypothesis"].startswith("HB2") for r in rA18))
            files18 = (jlHB.exists() and rpHB.exists() and jlA18.exists()
                       and len(recsHB) == 60 and all(r["tf"] == "H1" for r in recsHB))
            hdr18 = "TF=H1" in rpHB.read_text(encoding="utf-8")
        t18 = filt18 and files18 and hdr18
    finally:
        _self.load_window = orig
    print(f"  [18] comma-list: run(only=HB2-06,HB2-10)->60 rows H1 + suffix files (report TF=H1); "
          f"WAVE-A intact 84 -> {t18}")
    ok = ok and t18

    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", action="store_true", help="endesha grid FROZEN kwenye TRAIN (PC ya data)")
    ap.add_argument("--validate", action="store_true",
                    help="C2-4: S2 VALIDATION — cells 7 FROZEN (HC2-03 EURUSD) + BH-FDR")
    ap.add_argument("--hyp", default=None,
                    help="chuja hypothesis moja au comma-list kwa --train (mf. HC2-10 -> 20; "
                         "HB2-06,HB2-10 -> 60; outputs zenye suffix). Bila hii -> WAVE-A (84 cells).")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.validate:
        rows = run_s2("validation")
        if rows is None:
            return 1
        sv = [r for r in rows if r["survivor"]]
        if sv:
            print(f"WAVE-C2-A S2: SURVIVORS {len(sv)}/7 -> " + ", ".join(r["id"] for r in sv))
        else:
            print("WAVE-C2-A S2: hakuna survivor - HC2-03 haujathibitika OOS (FAIL kwa heshima)")
        print(f"  data/strategies/{S2_OUT_JSONL}\n  reports/{S2_OUT_REPORT}")
        return 0
    if not a.train:
        print("Tumia --train (S1 TRAIN) | --validate (C2-4 S2) | --self-test.", file=sys.stderr)
        return 2
    rows = run("train", only=a.hyp)
    traded = [r for r in rows if r.get("min_n_ok")]
    pos = [r for r in traded if r.get("ev", 0) > 0]
    tag = a.hyp if a.hyp else "WAVE-A"
    print(f"WAVE-C2-A S1 TRAIN [{tag}]: cells={len(rows)} N>=MIN_N={len(traded)} EV>0={len(pos)}")
    if a.hyp:
        suffix = "+".join(_active_ids(a.hyp)); slug = suffix.replace("-", "").lower()
        print(f"  data/strategies/wave_c2a_train_{suffix}.jsonl\n  reports/wave_c2b_{slug}_s1_train.md")
    else:
        print(f"  data/strategies/{OUT_JSONL}\n  reports/{OUT_REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
