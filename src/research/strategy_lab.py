"""
strategy_lab.py — S1 STRATEGY FACTORY (Alpha Engineering; Chief directive + GRID RULING 2026-07-09).

MCHAKATO: GRID (events V2 x pairs x SL/TP x context-filter) -> backtest kwa `episodes()` ya
event_quality_report (fill rules ZILIZOKAGULIWA — SIBADILISHI) -> metrics kwa costs -> candidates.
S1 = TRAIN search (in-sample) -> candidates.jsonl. S2 = walk-forward VALIDATION + BH-FDR (machinery
imo hapa: bh_fdr/pvalue_gt0). S3 = HOLDOUT mara moja (imezuiwa kwa code hadi Chief token).

MKATABA (spec ya Chief + rulings):
  1. GRID: EVENTS_V2 (TIER-1 pre-registered filters + TIER-2 default) x pairs x SL/TP{1,1.5,2}x{1,1.5,2,3}
     x context-filter {ALL, session, vol} — filters PRE-REGISTERED per event (FDR inahesabu ZOTE).
  2. BACKTEST: `episodes()` (next-bar honest, tie->SL, costs kila trade). SIBADILISHI fill rules (Chief).
  3. SACRED SPLITS (RED LINE, enforced kwa code): TRAIN <2023 (search) | VALIDATION 2023-2024 |
     HOLDOUT >=2025 (refuse kusoma bila --holdout-final + token sahihi).
  4. METRICS: N, EV net/trade (pips, costs ndani), win%, PF, maxDD, trades/day. RANK = population view
     (LESSON-033/034 — si top-EV pekee: N + availability + consistency).
  5. FDR: BH correction (bh_fdr) juu ya p-values za VALIDATION; null baseline (wangapi kwa bahati).
  6. OUTPUT: reports/strategy_lab_report.md + data/strategies/candidates.jsonl. Survivors = CANDIDATES
     hadi S3. RED LINES: hakuna kuchagua kwa holdout; hakuna metric bila costs.

Research harness (numpy OK — SIO Engine core; purity inahusu core). Reuse: event_library_v2 (EVENTS_V2),
event_quality_report (episodes, _metrics, SESSIONS, _sess).
Endesha (PC ya data): python strategy_lab.py --split train        (S1 candidates)
                      python strategy_lab.py --split validation   (S2 walk-forward + FDR)
Self-test (bila data): python strategy_lab.py --self-test
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

from event_library_v2 import EVENTS_V2, _synthetic
from event_quality_report import episodes, _metrics, SESSIONS

# Cycle-2 EXIT SCIENCE (H-C2-6): variants za exploration juu ya strategy (STRAT-001/002). 'fixed' =
# default byte-identical (exit_cfg=None). Forward-confirm kabla ya kubadilisha strategy iliyothibitishwa.
EXIT_VARIANTS = ({"mode": "fixed"}, {"mode": "trailing", "k": 1.0}, {"mode": "trailing", "k": 2.0},
                 {"mode": "breakeven", "r": 1.0}, {"mode": "time", "bars": 12})

REPO_ROOT = Path(__file__).resolve().parents[2]
MIN_N = 30                                    # sample ya chini kuwa candidate
SL_GRID = (1.0, 1.5, 2.0)
TP_GRID = (1.0, 1.5, 2.0, 3.0)
VOLS = ("LOW", "NORMAL", "HIGH")

# sacred splits (RED LINE)
TRAIN_END = datetime(2023, 1, 1)
VALID_END = datetime(2025, 1, 1)
HOLDOUT_TOKEN = "CHIEF-HOLDOUT-S3"            # lazima ilingane ili kusoma >=2025 (Chief pekee)

# GRID RULING (Chief 2026-07-09) — TIER-1 pre-registered: pairs + session/vol filters per event.
# session_filter: None=ALL | "no-LATE" | jina la session | list ya sessions.  vol_filter: None=ALL | jina.
TIER1 = {
    "nr7_break":     dict(pairs="ALL", sessions=(None, "no-LATE", ("LONDON", "NY")), vols=(None, "HIGH")),
    "second_chance": dict(pairs=("EURJPY", "USDCHF", "EURUSD"), sessions=(None, "LATE"), vols=(None, "LOW")),
    "shock_follow":  dict(pairs=("EURJPY", "USDJPY"), sessions=(None, "ASIA"), vols=(None, "NORMAL")),
    "session_orb":   dict(pairs=("USDJPY", "EURUSD", "GBPUSD"), sessions=(None,), vols=(None, "HIGH")),
    "inside_break":  dict(pairs=("USDJPY",), sessions=(None, "LONDON"), vols=(None, "HIGH")),
    "rsi2_pullback": dict(pairs=("EURUSD", "USDJPY"), sessions=(None,), vols=(None,)),
}
# TIER-2 (default context — ALL sessions/vols) endesha kwa ukamilifu compute ikiruhusu.
TIER2 = ("mr_zscore", "lowvol_reversal", "trend_resume", "big_range_mo",
         "pullback_v2", "pattern_3lows", "bb_fade", "engulf_extreme")
# stop-breakouts: usiwaue — jaribu TP {2,3}R (ruling). Negative kila param -> archive kwa evidence.
STOP_BREAKOUTS = {"jump_off": dict(pairs="ALL", sessions=(None,), vols=(None,)),
                  "breakout_stop": dict(pairs="ALL", sessions=(None,), vols=(None,))}


def grid(pairs):
    """Zalisha candidate specs zote (cartesian) kutoka GRID RULING. Kila spec = dict inayoelezea cell.
    FDR itahesabu ZOTE zilizozalishwa hapa (pre-registration ya honest multiple-testing)."""
    cells = []
    def add(bank, sltp):
        for ev, evp in bank.items():
            syms = pairs if evp["pairs"] == "ALL" else [p for p in evp["pairs"] if p in pairs]
            for sym in syms:
                for sl in SL_GRID:
                    for tp in sltp:
                        for sf in evp["sessions"]:
                            for vf in evp["vols"]:
                                cells.append(dict(event=ev, pair=sym, sl_atr=sl, tp_atr=tp,
                                                  session_filter=sf, vol_filter=vf))
    add(TIER1, TP_GRID)
    add({k: dict(pairs="ALL", sessions=(None,), vols=(None,)) for k in TIER2}, TP_GRID)
    add(STOP_BREAKOUTS, (2.0, 3.0))          # ruling: stop-breakouts jaribu TP {2,3}R
    return cells


# ---------- CYCLE-2 GRID (Chief 2026-07-09; HAIGUSI TIER1/TIER2 za C1 hapo juu) ----------
# H1: events 4 MPYA za C2 (squeeze/nr4/gap/drift). H4: cost-remedy set (H-C2-1/2: compression+shock).
# filters {None, no-LATE}; vol {None}. m ya FDR = cells ZOTE za C2 (pre-registration tofauti na C1).
C2_EVENTS_H1 = ("squeeze_break", "nr4_inside", "gap_fade", "london_drift")
C2_EVENTS_H4 = ("nr7_break", "squeeze_break", "nr4_inside", "shock_follow")


def grid_c2(pairs, tf):
    """GRID ya Cycle-2. TF inaamua event set: H4 = cost-remedy (H-C2-1/2); H1 = events 4 mpya."""
    events = C2_EVENTS_H4 if tf == "H4" else C2_EVENTS_H1
    cells = []
    for ev in events:
        for sym in pairs:
            for sl in SL_GRID:
                for tp in TP_GRID:
                    for sf in (None, "no-LATE"):
                        cells.append(dict(event=ev, pair=sym, sl_atr=sl, tp_atr=tp,
                                          session_filter=sf, vol_filter=None))
    return cells


def _mask_context(out, entry, hour, vol, sf, vf):
    """CHIEF FIX (review 2026-07-09): context filter inawekwa KWENYE SIGNALS — kabla ya
    episodes() — ili position-gating (non-overlap) iendane na strategy halisi ya filtered
    (post-hoc filter iliruhusu trade ya nje-ya-filter kuzuia signal ya ndani-ya-filter).
    Decidability (EP-5): session = saa ya bar ya ENTRY i+1 (ratiba, inajulikana ex-ante);
    vol = STATE ya bar ya SIGNAL i (state ya i+1 haijulikani hadi bar ifunge)."""
    n = len(hour)
    allow = np.ones(n, bool)
    if sf is not None:
        from event_quality_report import _sess
        sess_entry = np.array([_sess(int(hour[i + 1])) if i + 1 < n else "LATE" for i in range(n)])
        if sf == "no-LATE":
            allow &= sess_entry != "LATE"
        elif isinstance(sf, (list, tuple)):
            allow &= np.isin(sess_entry, list(sf))
        else:
            allow &= sess_entry == sf
    if vf is not None and vol is not None:
        allow &= np.asarray(vol) == vf
    if entry == "market":
        sig = out["sig"].copy(); sig[~allow] = 0
        return {"sig": sig}
    LL = out["long_level"].copy(); SS = out["short_level"].copy()
    LL[~allow] = np.nan; SS[~allow] = np.nan
    return {"long_level": LL, "short_level": SS}


def _mask_context_dir(out, entry, allow_long, allow_short):
    """C2-2a (WAVE-C2-A infra): DIRECTION-AWARE context mask — generalization ya _mask_context
    (ambayo HAIGUSWI — inazima pande zote). Hii inaruhusu HTF-bias one-sided (HC2-01: upande wa
    trend TU) na conditions TOFAUTI kwa long/short (HC2-06: long kwenye support, short kwenye
    resistance). allow_long/allow_short = bool arrays za SIGNAL bar i (context conditions za
    h4_/d1_ arrays kutoka loader — as-of joined, bar iliyoFUNGWA). Decidability ILEILE ya
    _mask_context: mask inatumia value ya signal bar i, si entry bar i+1 (self-test [13] trap).
    Market: sig +1 inahitaji allow_long[i]; sig -1 inahitaji allow_short[i].
    Stop:   long_level inahitaji allow_long[i]; short_level inahitaji allow_short[i] (NaN=disarm)."""
    allow_long = np.asarray(allow_long, bool)
    allow_short = np.asarray(allow_short, bool)
    if entry == "market":
        sig = out["sig"].copy()
        if len(allow_long) != len(sig) or len(allow_short) != len(sig):
            raise ValueError("allow arrays lazima ziwe urefu wa sig (signal-bar aligned)")
        sig[(sig == 1) & ~allow_long] = 0
        sig[(sig == -1) & ~allow_short] = 0
        return {"sig": sig}
    LL = out["long_level"].copy(); SS = out["short_level"].copy()
    if len(allow_long) != len(LL) or len(allow_short) != len(SS):
        raise ValueError("allow arrays lazima ziwe urefu wa levels (signal-bar aligned)")
    LL[~allow_long] = np.nan
    SS[~allow_short] = np.nan
    return {"long_level": LL, "short_level": SS}


def _maxdd(pnls):
    """Max drawdown ya equity curve ya cumulative pnl (pips)."""
    eq = np.cumsum(pnls)
    peak = np.maximum.accumulate(eq)
    return float((peak - eq).max()) if len(eq) else 0.0


def evaluate(cell, data, days):
    """Backtest cell moja: event fn(params default) -> context mask KWENYE signals ->
    episodes -> metrics+costs. Rudisha dict ya candidate (au None kama N<MIN_N)."""
    spec = EVENTS_V2[cell["event"]]
    out = spec["fn"](data["o"], data["h"], data["l"], data["c"], data.get("tc"), data.get("hour"))
    out = _mask_context(out, spec["entry"], data["hour"], data.get("vol"),
                        cell["session_filter"], cell["vol_filter"])
    trs = episodes(out, spec["entry"], data["o"], data["h"], data["l"], data["c"],
                   data["atr"], data["spr"], data["hour"], data.get("vol"),
                   sl_atr=cell["sl_atr"], tp_atr=cell["tp_atr"])
    pn = [t[3] for t in trs]
    m = _metrics(pn)
    if m["n"] < MIN_N:
        return None
    return dict(**cell, n=m["n"], ev=round(m["ev"], 4), win=round(m["win"], 4),
                pf=round(m["pf"], 3) if math.isfinite(m["pf"]) else None,
                maxdd=round(_maxdd(pn), 2), trades_per_day=round(m["n"] / max(days, 1), 3),
                pnls=pn)                       # pnls zinahifadhiwa kwa FDR (S2); zinaondolewa kwenye jsonl


def exit_sweep(cell, data, variants=EXIT_VARIANTS):
    """Cycle-2 EXIT SCIENCE: sweep exit variants juu ya cell moja (STRAT-001/002). Rudisha
    list ya (variant, metrics). 'fixed' = default (exit_cfg=None, byte-identical). EXPLORATION."""
    spec = EVENTS_V2[cell["event"]]
    out = spec["fn"](data["o"], data["h"], data["l"], data["c"], data.get("tc"), data.get("hour"))
    out = _mask_context(out, spec["entry"], data["hour"], data.get("vol"),
                        cell["session_filter"], cell["vol_filter"])
    rows = []
    for v in variants:
        ecfg = None if v["mode"] == "fixed" else v
        trs = episodes(out, spec["entry"], data["o"], data["h"], data["l"], data["c"],
                       data["atr"], data["spr"], data["hour"], data.get("vol"),
                       sl_atr=cell["sl_atr"], tp_atr=cell["tp_atr"], exit_cfg=ecfg)
        rows.append((v, _metrics([t[3] for t in trs])))
    return rows


# ---------- FDR machinery (S2) ----------
def pvalue_gt0(pnls):
    """One-sided p-value: H0 mean<=0 vs H1 mean>0 (normal approx, stdlib erfc).
    R1 (SCIENTIST-D W1): z-test ina skew bias (negative-skew/high-win structures -> size ×1.2-1.4
    @0.05). Inabaki kama SENSITIVITY column; engine RASMI ya FDR/registration = pvalue_boot (chini)."""
    p = np.asarray(pnls, float); n = len(p)
    if n < 2:
        return 1.0
    sd = p.std(ddof=1)
    if sd == 0:
        return 0.0 if p.mean() > 0 else 1.0
    t = p.mean() / (sd / math.sqrt(n))
    return 0.5 * math.erfc(t / math.sqrt(2.0))


def _seed_from_key(cell):
    """R1: seed deterministic kutoka cell key (event|pair|sl|tp|filters) — reproducible bit-kwa-bit."""
    import hashlib
    key = "|".join(str(cell.get(k)) for k in ("event", "pair", "sl_atr", "tp_atr",
                                              "session_filter", "vol_filter"))
    return int(hashlib.sha1(key.encode()).hexdigest()[:12], 16)


def _stationary_indices(n, B, mean_block, rng):
    """Stationary bootstrap ya Politis-Romano: blocks za urefu wa geometric(1/mean_block),
    circular (wrap-around). Rudisha indices (B, n). Vectorized juu ya B (loop fupi ya n columns)."""
    p = 1.0 / max(1.0, float(mean_block))
    starts = rng.integers(0, n, size=(B, n))          # restart points (zinatumika pale restart=True)
    restart = rng.random((B, n)) < p
    idx = np.empty((B, n), dtype=np.int64)
    cur = starts[:, 0].copy()                          # block ya kwanza daima inaanza random
    idx[:, 0] = cur
    for j in range(1, n):
        cur = np.where(restart[:, j], starts[:, j], (cur + 1) % n)
        idx[:, j] = cur
    return idx


def _se_nw(mat, K):
    """Newey-West (Bartlett) long-run SE ya mean. mat: (B, n) au (n,). Inafanya studentization
    iendane na block resampling (denominator ya i.i.d. + block resampling ilipima size 0.063-0.072
    kwenye skew nulls — jedwali la calibration kwenye reports/wave1_report.md)."""
    m2 = np.atleast_2d(np.asarray(mat, float))
    n = m2.shape[1]
    d = m2 - m2.mean(axis=1, keepdims=True)
    lrv = (d * d).mean(axis=1)
    for k in range(1, K + 1):
        lrv += 2.0 * (1.0 - k / (K + 1)) * (d[:, k:] * d[:, :-k]).sum(axis=1) / n
    return np.sqrt(np.maximum(lrv, 1e-12) / n)


def pvalue_boot(pnls, B=10_000, mean_block=3, seed=None, cell=None):
    """R1 (ENGINE RASMI ya FDR/registration): one-sided p (H0 mean<=0) kwa STATIONARY BLOCK
    BOOTSTRAP (Politis-Romano) yenye STUDENTIZATION ya Newey-West (percentile-t):
      t_obs = mean/se_NW; series ina-CENTER (H0 kweli); kila resample -> t* = mean*/se_NW*;
      p = (1 + #{t* >= t_obs}) / (B + 1).
    CALIBRATION (deviation 2 kutoka design ya SCIENTIST-D — evidence: wave1_r1_report.md):
      (i) mean_block=3 (sio ~10): block kubwa inameza skewness ya t* (skew ya block-means ~ γ/√b)
          -> size 0.063-0.072 kwenye skew nulls (acceptance test b haiwezekani na mb=10);
          mb=3: skew size 0.043-0.053 (~nominal) NA AR(rho=0.5)-cluster 0.058 (z: 0.121).
      (ii) studentization = Newey-West K=mean_block (sio i.i.d. sd): denominator inayoendana na
          block dependence. Inarekebisha W1 (skew) + W7 (dependence). Seed deterministic:
    `cell` (cell key) > `seed`; bila yoyote -> 0 (daima reproducible)."""
    x = np.asarray(pnls, float); n = len(x)
    if n < 2:
        return 1.0
    if x.std(ddof=1) == 0:
        return 0.0 if x.mean() > 0 else 1.0
    K = max(1, min(int(mean_block), n - 2))
    t_obs = float(x.mean() / _se_nw(x, K)[0])
    y = x - x.mean()                                   # center -> H0 mean=0 ni kweli kwenye resamples
    if seed is None:
        seed = _seed_from_key(cell) if cell is not None else 0
    rng = np.random.default_rng(seed)
    idx = _stationary_indices(n, B, min(mean_block, n), rng)
    t_star = y[idx].mean(axis=1) / _se_nw(y[idx], K)
    return float((1 + int((t_star >= t_obs).sum())) / (B + 1))


def bh_fdr(pvals, q=0.10):
    """Benjamini-Hochberg: rudisha (survivors_mask, k, expected_false). Cells ZOTE zinahesabika (m)."""
    pv = np.asarray(pvals, float); m = len(pv)
    if m == 0:
        return np.zeros(0, bool), 0, 0.0
    order = np.argsort(pv)
    k = 0
    for rank, idx in enumerate(order, 1):
        if pv[idx] <= q * rank / m:
            k = rank
    if k == 0:
        return np.zeros(m, bool), 0, 0.0
    cutoff = pv[order[k - 1]]
    survivors = pv <= cutoff
    return survivors, int(k), round(q * k, 2)


# ---------- data loading (SACRED SPLITS — enforced) ----------
def context_path(sym, tf):
    """Njia ya context parquet ya htf_context.py (h4_*/d1_* per LTF bar, as-of aligned)."""
    from market_state_engine import cfg
    return REPO_ROOT / cfg()["paths"]["processed"] / "context" / f"symbol={sym}" / f"tf={tf}.parquet"


def _load_context(df, sym, tf, path=None):
    """C2-2a CONTEXT LOADER: soma context parquet (output ya htf_context — as-of BACKWARD join
    imekwisha-thibitishwa no-lookahead; HAKUNA join mpya ya HTF hapa) na i-align kwenye state df
    kwa `ts` (LEFT join EXACT — context ina row kwa kila LTF bar, C2-0 report). Rudisha dict
    {col: array} ya columns za h4_*/d1_* SAMBAMBA na o/h/l/c (order ya ts ILEILE — row_index
    inalinda order ya left frame): numeric -> float64 (null->NaN); state (string) -> object.
    Values ni za SIGNAL bar (decidable). ADDITIVE: parquet ikikosekana -> None + onyo
    (load ya state HAIVUNJIKI — grids za C1/H1/H4 bila context zinaendelea kama zamani)."""
    import polars as pl
    p = Path(path) if path is not None else context_path(sym, tf)
    if not p.exists():
        print(f"  ONYO: context parquet haipo ({sym}/{tf}: {p.name}) -> ctx=None "
              "(HTF context-filters hazipatikani kwa pair hii)")
        return None
    cdf = pl.read_parquet(p)
    j = (df.select("ts").with_row_index("__i")
           .join(cdf, on="ts", how="left").sort("__i").drop("__i"))
    ctx = {}
    for col in j.columns:
        if col == "ts":
            continue
        if j[col].dtype in (pl.Utf8, pl.String, pl.Categorical):
            ctx[col] = np.asarray(j[col].to_list(), dtype=object)
        else:
            ctx[col] = j[col].cast(pl.Float64).to_numpy()
    return ctx


def load_window(sym, tf, split, holdout_token=None):
    """Soma state parquet kwa split. RED LINE: holdout inarefuse bila token sahihi (KABLA ya kusoma)."""
    if split == "holdout" and holdout_token != HOLDOUT_TOKEN:
        raise PermissionError("RED LINE: HOLDOUT (>=2025) imezuiwa — inahitaji --holdout-final + Chief token")
    import polars as pl
    from market_state_engine import pip
    from latent_structure import state_path
    p = state_path(sym, tf)
    if not p.exists():
        return None
    df = pl.read_parquet(p).sort("ts")
    if split == "train":
        df = df.filter(pl.col("ts") < TRAIN_END)
    elif split == "validation":
        df = df.filter((pl.col("ts") >= TRAIN_END) & (pl.col("ts") < VALID_END))
    elif split == "holdout":
        df = df.filter(pl.col("ts") >= VALID_END)
    else:
        raise ValueError(f"split batili: {split}")
    if df.height < 500:
        return None
    pp = pip(sym)
    return dict(o=df["o"].to_numpy() / pp, h=df["h"].to_numpy() / pp, l=df["l"].to_numpy() / pp,
                c=df["c"].to_numpy() / pp, atr=df["atr"].to_numpy() / pp,
                spr=np.nan_to_num(df["spr"].to_numpy(), nan=0.0), tc=df["tc"].to_numpy().astype(float),
                hour=df["ts"].dt.hour().to_numpy(), vol=np.asarray(df["volatility_state"].to_list()),
                ts=df["ts"].to_numpy(),                        # family_pooled (§8.1): cross-pair ordering — ADDITIVE, non-breaking
                ctx=_load_context(df, sym, tf),                # C2-2a: HTF context arrays (h4_*/d1_*) au None — ADDITIVE
                days=df["ts"].dt.date().n_unique())


def load_cells_file(path):
    """R1 restatement: soma cells maalum (jsonl: event/pair/sl_atr/tp_atr/session_filter/vol_filter)
    badala ya grid nzima — kwa re-run ya cells ZILIZOKWISHA-FUNGULIWA (S3/S3b) na engines zote mbili.
    Hakuna dirisha jipya: split guards (ikiwemo holdout token) zinabaki zilezile."""
    cells = []
    with open(path, encoding="utf-8") as f:
        for ln in f:
            if not ln.strip():
                continue
            r = json.loads(ln)
            sf = r.get("session_filter")
            cells.append(dict(event=r["event"], pair=r["pair"], sl_atr=float(r["sl_atr"]),
                              tp_atr=float(r["tp_atr"]),
                              session_filter=tuple(sf) if isinstance(sf, list) else sf,
                              vol_filter=r.get("vol_filter")))
    return cells


def search(pairs, tf, split, holdout_token=None, cycle=1, cells_override=None):
    """Endesha grid juu ya split. cycle 1 = grid ya C1; cycle 2 = grid_c2 (tf-aware);
    cells_override = orodha maalum (R1 restatement — hakuna grid).
    Rudisha (candidates, n_cells_tested, days_total)."""
    cells = cells_override if cells_override is not None else (
        grid_c2(pairs, tf) if cycle == 2 else grid(pairs))
    cache = {sym: load_window(sym, tf, split, holdout_token) for sym in pairs}   # load mara moja kwa pair
    cands = []; tested = 0
    days_tot = sum(d["days"] for d in cache.values() if d)
    for k, cell in enumerate(cells, 1):
        data = cache.get(cell["pair"])
        if data is None:
            continue
        tested += 1
        cand = evaluate(cell, data, data["days"])
        if cand is not None:
            cands.append(cand)
        if k % 200 == 0:
            print(f"  ...cells {k}/{len(cells)} (candidates hadi sasa: {len(cands)})", flush=True)
    return cands, tested, days_tot


# ---------- output ----------
def _population_rank(cands):
    """Population view (LESSON-033/034): rank kwa EV chanya NA availability (trades/day) NA N — si EV pekee."""
    return sorted(cands, key=lambda x: (x["ev"] > 0, x["ev"] * math.log1p(x["n"])), reverse=True)


def write_outputs(cands, tested, split, tf, days_tot, apply_fdr=False, q=0.10, out_root=REPO_ROOT, cycle=1):
    out_root = Path(out_root)
    strat_dir = out_root / "data" / "strategies"
    strat_dir.mkdir(parents=True, exist_ok=True)
    suffix = "" if cycle == 1 else f"_c{cycle}"     # C2 haiandiki juu ya candidates za C1

    # FDR KWANZA (kabla ya jsonl) ili p-values + survivor flag ziingie kwenye rekodi zote.
    # R1 ENGINE SWAP (pre-registered kwa commit hii, KABLA ya dirisha jipya — SCIENTIST-D design 4):
    # FDR/registration RASMI = pvalue_boot (stationary block bootstrap, studentized; seed=cell key).
    # pvalue_gt0 (z) inabaki kama SENSITIVITY column -> ripoti two-column (restatement ya R1 design 3).
    fdr_line = ""; surv_rows = []
    if apply_fdr and cands:
        p_boot = [pvalue_boot(c["pnls"], cell=c) for c in cands]
        p_z = [pvalue_gt0(c["pnls"]) for c in cands]
        surv, k, exp_false = bh_fdr(p_boot, q)
        for c, pb, pz, s in zip(cands, p_boot, p_z, surv):
            c["p"] = round(float(pb), 6)               # p RASMI = bootstrap (R1)
            c["p_z"] = round(float(pz), 6)             # sensitivity column (engine ya zamani)
            c["fdr_survivor"] = bool(s)
        surv_rows = sorted((c for c in cands if c["fdr_survivor"]), key=lambda x: x["p"])
        fdr_line = (f"- **BH-FDR (q={q}) juu ya p_boot (R1 bootstrap engine — RASMI)**: "
                    f"{int(surv.sum())}/{len(cands)} survivors; ~{exp_false} zinatarajiwa kwa bahati (null). "
                    f"Cells tested (m)={tested}. p_z (z-test ya zamani) = sensitivity column.")

    jl = strat_dir / f"candidates{suffix}.jsonl"
    with open(jl, "w", encoding="utf-8") as f:
        for c in _population_rank(cands):
            rec = {k: v for k, v in c.items() if k != "pnls"}
            rec["split"] = split
            f.write(json.dumps(rec, sort_keys=True) + "\n")

    L = [f"# Strategy Lab — cycle-{cycle} candidates ({split.upper()})\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | cycle={cycle} | TF={tf} | split={split} | cells tested={tested} | "
         f"candidates (N>={MIN_N})={len(cands)} | costs ndani (episodes) | RANK=population view*\n",
         "> **UAMINIFU:** hizi ni CANDIDATES, SIO strategies. TRAIN=in-sample; uthibitisho = S2 "
         "(walk-forward VALIDATION + BH-FDR) na S3 (HOLDOUT, mara moja). RED LINES: hakuna kuchagua "
         "kwa holdout; hakuna metric bila costs. LESSON-001/002/029/033/034. Profitable != Tradable Edge.\n"]
    if fdr_line:
        L.append("\n## FDR (S2)\n" + fdr_line + "\n")
        if surv_rows:
            L.append("### SURVIVORS — waliosalia BH-FDR juu ya p_boot (hawa PEKEE ndio registration ya S3)\n")
            L.append("| event | pair | SL | TP | session | vol | N | EV net | win% | PF | p_boot | p_z |")
            L.append("|-------|------|----|----|---------|-----|---|--------|------|----|--------|-----|")
            for c in surv_rows:
                L.append(f"| {c['event']} | {c['pair']} | {c['sl_atr']} | {c['tp_atr']} | "
                         f"{c['session_filter']} | {c['vol_filter']} | {c['n']:,} | {c['ev']:+.3f} | "
                         f"{c['win']*100:.1f} | {c['pf'] if c['pf'] is not None else 'inf'} | "
                         f"{c['p']:.2e} | {c['p_z']:.2e} |")
            L.append("")
    # R5(1): EV(Δspread) analytic — cost stress kwa kila ripoti (survivors, au top-10 kama hakuna FDR)
    from cost_stress import ev_spread_table, SPREAD_DELTAS
    stress_rows = ev_spread_table(surv_rows if surv_rows else _population_rank(cands)[:10])
    if stress_rows:
        L.append("\n## Cost stress — EV(Δspread) analytic (R5; kila trade inalipa spread mara moja)\n")
        L.append("| cell | EV | " + " | ".join(f"EV@+{d}" for d in SPREAD_DELTAS) + " | breakeven Δspread |")
        L.append("|------|----|" + "|".join(["----"] * len(SPREAD_DELTAS)) + "|------|")
        for r in stress_rows:
            L.append(f"| {r['label']} | {r['ev']:+.3f} | "
                     + " | ".join(f"{r['ev_dspread'][f'+{d}']:+.3f}" for d in SPREAD_DELTAS)
                     + f" | {r['breakeven_dspread']:.3f} |")

    L.append("\n## Top candidates (population rank)\n")
    L.append("| event | pair | SL | TP | session | vol | N | EV net | win% | PF | maxDD | tr/day |")
    L.append("|-------|------|----|----|---------|-----|---|--------|------|----|-------|--------|")
    for c in _population_rank(cands)[:40]:
        L.append(f"| {c['event']} | {c['pair']} | {c['sl_atr']} | {c['tp_atr']} | {c['session_filter']} | "
                 f"{c['vol_filter']} | {c['n']:,} | {c['ev']:+.3f} | {c['win']*100:.1f} | "
                 f"{c['pf'] if c['pf'] is not None else 'inf'} | {c['maxdd']:.1f} | {c['trades_per_day']:.2f} |")
    L.append("\n*S1 = candidates -> S2 walk-forward+FDR -> S3 holdout. Chief directive + GRID RULING.*")
    rpt = out_root / "reports" / f"strategy_lab_report{suffix}.md"
    rpt.parent.mkdir(parents=True, exist_ok=True)
    rpt.write_text("\n".join(L), encoding="utf-8")
    return jl, rpt


# ---------- self-test (bila data halisi) ----------
def self_test():
    ok = True

    # (1) grid inazalisha cells; ZOTE zina fields sahihi; pairs zisizo kwenye orodha hazitokei
    pairs = ["EURUSD", "USDJPY", "EURJPY", "GBPUSD", "USDCHF"]
    cells = grid(pairs)
    keys_ok = all({"event", "pair", "sl_atr", "tp_atr", "session_filter", "vol_filter"} <= set(c) for c in cells)
    pairs_ok = all(c["pair"] in pairs for c in cells)
    tier1_present = {c["event"] for c in cells} >= set(TIER1) | set(TIER2)
    # inside_break = USDJPY pekee (pre-registration inaheshimiwa)
    ib_pairs = {c["pair"] for c in cells if c["event"] == "inside_break"}
    reg_ok = ib_pairs == {"USDJPY"}
    print(f"  [1] grid: cells={len(cells)} keys={keys_ok} pairs-scoped={pairs_ok} tier-coverage={tier1_present} pre-reg={reg_ok}")
    ok = ok and keys_ok and pairs_ok and tier1_present and reg_ok and len(cells) > 100

    # (1c) CYCLE-2 grid: H1 = events 4 mpya; H4 = cost-remedy set; filters {None, no-LATE}; HAIGUSI C1
    c2_h1 = grid_c2(pairs, "H1")
    c2_h4 = grid_c2(pairs, "H4")
    ev_h1 = {c["event"] for c in c2_h1}; ev_h4 = {c["event"] for c in c2_h4}
    sf_h1 = {c["session_filter"] for c in c2_h1}
    c2_ok = (ev_h1 == set(C2_EVENTS_H1) and ev_h4 == set(C2_EVENTS_H4)
             and sf_h1 == {None, "no-LATE"} and all(c["vol_filter"] is None for c in c2_h1)
             and ev_h1.isdisjoint(set(TIER1)) )   # C2 H1 events ni tofauti na TIER1 za C1
    print(f"  [1c] grid_c2: H1={sorted(ev_h1)} H4-includes-nr7={'nr7_break' in ev_h4} filters={sorted(str(x) for x in sf_h1)} -> {c2_ok}")
    ok = ok and c2_ok

    # (2) evaluate juu ya synthetic: candidate ina metrics + costs (EV inaweza hasi — sawa)
    o, h, l, c, tc, hour = _synthetic(n=6000, seed=3)
    atr = np.maximum(h - l, 0.1)
    spr = np.full(len(c), 1.0)
    vol = np.array(["NORMAL"] * len(c))
    data = dict(o=o, h=h, l=l, c=c, atr=atr, spr=spr, tc=tc, hour=hour, vol=vol, days=250)
    cand = evaluate(dict(event="mr_zscore", pair="EURUSD", sl_atr=1.5, tp_atr=1.5,
                         session_filter=None, vol_filter=None), data, 250)
    ev_ok = cand is not None and cand["n"] >= MIN_N and "ev" in cand and "maxdd" in cand
    print(f"  [2] evaluate: n={cand['n'] if cand else 0} ev={cand['ev'] if cand else None} maxdd={cand['maxdd'] if cand else None}")
    ok = ok and ev_ok

    # (2b) context filter inapunguza trades (vol_filter=HIGH < ALL kwenye data ya NORMAL -> 0/None)
    cand_hi = evaluate(dict(event="mr_zscore", pair="EURUSD", sl_atr=1.5, tp_atr=1.5,
                            session_filter=None, vol_filter="HIGH"), data, 250)
    filt_ok = cand_hi is None            # data yote NORMAL -> HIGH filter -> N=0 -> None
    print(f"  [2b] context filter (HIGH kwenye NORMAL data -> None): {filt_ok}")
    ok = ok and filt_ok

    # (2c) CHIEF FIX: mask iko kwenye SIGNALS na inaheshimu decidability — session ya bar ya
    # ENTRY (i+1) na vol ya bar ya SIGNAL (i)
    n4 = 48
    hr4 = np.arange(n4) % 24
    sig_all = {"sig": np.ones(n4, dtype=int)}
    masked = _mask_context(sig_all, "market", hr4, None, "LONDON", None)["sig"]
    idx_on = np.flatnonzero(masked != 0)
    sess_ok = all(7 <= hr4[i + 1] <= 11 for i in idx_on if i + 1 < n4)
    vol4 = np.array(["HIGH" if i % 2 == 0 else "LOW" for i in range(n4)])
    masked_v = _mask_context(sig_all, "market", hr4, vol4, None, "HIGH")["sig"]
    vol_ok = all(vol4[i] == "HIGH" for i in np.flatnonzero(masked_v != 0))
    mask_ok = sess_ok and vol_ok and masked.sum() > 0 and masked_v.sum() > 0
    print(f"  [2c] signal-mask: session@entry-bar={sess_ok} vol@signal-bar={vol_ok} -> {mask_ok}")
    ok = ok and mask_ok

    # (3) BH-FDR math: pvals zenye survivors zinazojulikana
    pv = [0.001, 0.008, 0.02, 0.6, 0.9]
    surv, k, ef = bh_fdr(pv, q=0.10)
    # BH: sorted 0.001,0.008,0.02,0.6,0.9; thresholds 0.02,0.04,0.06,0.08,0.10 -> 0.02<=0.06 (rank3) pass
    bh_ok = k == 3 and surv.tolist() == [True, True, True, False, False]
    print(f"  [3] BH-FDR: k={k} survivors={surv.tolist()} expected_false={ef} -> {bh_ok}")
    ok = ok and bh_ok

    # (3b) pvalue_gt0: chanya thabiti -> p ndogo; noise -> p ~ kubwa
    p_pos = pvalue_gt0([2.0, 2.5, 1.8, 2.2, 2.1, 1.9] * 5)
    p_noise = pvalue_gt0(list(np.random.default_rng(0).normal(0, 2, 200)))
    pv_ok = p_pos < 0.01 and p_noise > 0.05
    print(f"  [3b] pvalue: strong+={p_pos:.4f} noise={p_noise:.3f} -> {pv_ok}")
    ok = ok and pv_ok

    # (4) SACRED SPLITS RED LINE: holdout bila token -> PermissionError (KABLA ya kusoma data)
    try:
        load_window("EURUSD", "H1", "holdout", holdout_token=None)
        red_ok = False
    except PermissionError:
        red_ok = True
    try:
        load_window("EURUSD", "H1", "holdout", holdout_token="wrong")
        red_ok = red_ok and False
    except PermissionError:
        red_ok = red_ok and True
    print(f"  [4] RED LINE holdout guard (no/ wrong token -> refuse): {red_ok}")
    ok = ok and red_ok

    # (5) write_outputs (temp dir — SI kwenye repo halisi): candidates.jsonl haina pnls, ina split
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        jl, rpt = write_outputs([cand], tested=len(cells), split="train", tf="H1", days_tot=250, out_root=tmp)
        rec = json.loads(open(jl, encoding="utf-8").readline())
        rpt_exists = rpt.exists()
        out_ok = "pnls" not in rec and rec["split"] == "train" and rpt_exists
        print(f"  [5] outputs: jsonl no-pnls={('pnls' not in rec)} split={rec.get('split')} report={rpt_exists}")
    ok = ok and out_ok

    # (5b) FDR reporting: survivor anatajwa kwa JINA (report + jsonl ina p/fdr_survivor)
    base = dict(pair="EURUSD", sl_atr=1.5, tp_atr=1.5, session_filter=None, vol_filter=None,
                n=60, win=0.6, pf=1.5, maxdd=10.0, trades_per_day=0.1)
    strong = dict(base, event="nr7_break", ev=2.0, pnls=[2.0, 2.5, 1.8, 2.2, 2.1, 1.9] * 10)
    noise = dict(base, event="bb_fade", ev=0.01,
                 pnls=list(np.random.default_rng(1).normal(0, 2, 60)))
    with tempfile.TemporaryDirectory() as tmp:
        jl, rpt = write_outputs([strong, noise], tested=2, split="validation", tf="H1",
                                days_tot=500, apply_fdr=True, out_root=tmp)
        txt = rpt.read_text(encoding="utf-8")
        recs = [json.loads(l) for l in open(jl, encoding="utf-8")]
        named = "SURVIVORS" in txt and "nr7_break" in txt.split("SURVIVORS")[1].split("##")[0]
        flags = {r["event"]: r.get("fdr_survivor") for r in recs}
        flag_ok = flags.get("nr7_break") is True and flags.get("bb_fade") is False and all("p" in r for r in recs)
        print(f"  [5b] FDR survivor reporting: named-in-report={named} jsonl-flags={flag_ok}")
    ok = ok and named and flag_ok

    # (7) R1a: symmetric i.i.d. null -> bootstrap p ~ z p (hakuna skew -> engines zikubaliane)
    rng7 = np.random.default_rng(11)
    diffs = []
    for i in range(40):
        x = rng7.normal(0.05, 1.0, 80)
        diffs.append(abs(pvalue_boot(x, B=600, seed=1000 + i) - pvalue_gt0(x)))
    sym_ok = float(np.mean(diffs)) < 0.04
    print(f"  [7] R1 symmetric null: mean|p_boot - p_z|={np.mean(diffs):.4f} (<0.04) -> {sym_ok}")
    ok = ok and sym_ok

    # (8) R1b: two-point NEGATIVE-SKEW null (SL2/TP1-like: +1 @2/3, -2 @1/3, EV=0, N=100) —
    # reproduce §A3-W1: z size @0.05 imevimba (~0.07, ×1.4); bootstrap size ~ nominal na < z
    rng8 = np.random.default_rng(12)
    M, N8 = 600, 100
    rej_z = rej_b = 0
    for i in range(M):
        x = np.where(rng8.random(N8) < (2.0 / 3.0), 1.0, -2.0)
        if pvalue_gt0(x) < 0.05:
            rej_z += 1
        if pvalue_boot(x, B=400, seed=2000 + i) < 0.05:
            rej_b += 1
    size_z, size_b = rej_z / M, rej_b / M
    skew_ok = size_z > 0.055 and size_b < size_z and 0.015 <= size_b <= 0.085
    print(f"  [8] R1 skew-null size @0.05 (W1): z={size_z:.3f} (imevimba) boot={size_b:.3f} (~nominal, <z) -> {skew_ok}")
    ok = ok and skew_ok

    # (9) R1c: determinism — cell key ileile -> p ILEILE bit-kwa-bit; key tofauti -> seed tofauti
    xd = rng7.normal(0.3, 1.0, 60)
    cellA = dict(event="nr7_break", pair="USDCHF", sl_atr=2.0, tp_atr=1.0,
                 session_filter="no-LATE", vol_filter=None)
    cellB = dict(cellA, pair="USDJPY")
    pA1 = pvalue_boot(xd, B=800, cell=cellA); pA2 = pvalue_boot(xd, B=800, cell=cellA)
    det_ok = pA1 == pA2 and _seed_from_key(cellA) != _seed_from_key(cellB)
    print(f"  [9] R1 determinism: p(cellA) stable={pA1 == pA2} seeds-differ={_seed_from_key(cellA) != _seed_from_key(cellB)} -> {det_ok}")
    ok = ok and det_ok

    # (6) EXIT SCIENCE sweep: 'fixed' variant == default evaluate() N (byte-identical path); variants run
    cell_nr7 = dict(event="nr7_break", pair="EURUSD", sl_atr=2.0, tp_atr=1.0,
                    session_filter=None, vol_filter=None)
    rows = exit_sweep(cell_nr7, data)
    fixed_m = next(m for v, m in rows if v["mode"] == "fixed")
    cand_nr7 = evaluate(cell_nr7, data, 250)
    fixed_matches = cand_nr7 is not None and fixed_m["n"] == cand_nr7["n"]
    variants_run = all(m["n"] >= 0 for _, m in rows) and len(rows) == len(EXIT_VARIANTS)
    print(f"  [6] exit_sweep: fixed==default(N={fixed_m['n']})={fixed_matches} variants={len(rows)} run={variants_run}")
    ok = ok and fixed_matches and variants_run

    # ---------- C2-2a: context loader + _mask_context_dir ----------
    # [10] loader: alignment kwa ts (parquet ROWS SCRAMBLED kwa makusudi — join ni kwa ts, si order),
    #      dtypes (numeric->float64 NaN, state->object), pengo la ts -> NaN/None, missing -> None+onyo
    import polars as pl
    from datetime import timedelta
    with tempfile.TemporaryDirectory() as tmp:
        n10 = 60
        ts10 = [datetime(2024, 1, 1) + timedelta(minutes=15 * k) for k in range(n10)]
        cdf = pl.DataFrame({
            "ts": ts10,
            "h4_trend_sign": pl.Series((np.arange(n10) % 3 - 1), dtype=pl.Int8),
            "h4_vol_state": [("LOW", "NORMAL", "HIGH")[k % 3] for k in range(n10)],
            "d1_roc10": np.arange(n10) * 0.01,
        }).filter(pl.col("ts") != ts10[7])                    # pengo: bar 7 haina context row
        p10 = Path(tmp) / "ctx.parquet"
        cdf.sample(fraction=1.0, shuffle=True, seed=0).write_parquet(p10)   # SCRAMBLED order
        sdf = pl.DataFrame({"ts": ts10})
        ctx = _load_context(sdf, "TEST", "15m", path=p10)
        k_chk = [0, 5, 23, 59]
        align_ok = (ctx is not None and all(len(v) == n10 for v in ctx.values())
                    and all(ctx["h4_trend_sign"][k] == (k % 3 - 1) for k in k_chk)
                    and all(ctx["h4_vol_state"][k] == ("LOW", "NORMAL", "HIGH")[k % 3] for k in k_chk)
                    and all(abs(ctx["d1_roc10"][k] - k * 0.01) < 1e-12 for k in k_chk))
        gap_ok = (np.isnan(ctx["h4_trend_sign"][7]) and np.isnan(ctx["d1_roc10"][7])
                  and ctx["h4_vol_state"][7] is None)
        f64_ok = ctx["h4_trend_sign"].dtype == np.float64 and ctx["h4_vol_state"].dtype == object
        missing = _load_context(sdf, "TEST", "15m", path=Path(tmp) / "haipo.parquet")
        miss_ok = missing is None
    t10 = align_ok and gap_ok and f64_ok and miss_ok
    print(f"  [10] ctx loader: ts-align(scrambled)={align_ok} gap->NaN/None={gap_ok} "
          f"dtypes={f64_ok} missing->None={miss_ok}")
    ok = ok and t10

    # [11] _mask_context_dir MIRROR SYMMETRY: swap (allow_long<->allow_short) + flip ya sig/levels
    #      -> matokeo yana-mirror HASA (hakuna upande uliopendelewa); inputs HAZIGUSWI (copy)
    rng11 = np.random.default_rng(11); n11 = 200
    sig11 = rng11.integers(-1, 2, n11)
    A = rng11.random(n11) < 0.5; B = rng11.random(n11) < 0.5
    sig_in = sig11.copy()
    m1 = _mask_context_dir({"sig": sig11}, "market", A, B)["sig"]
    m2 = _mask_context_dir({"sig": -sig11}, "market", B, A)["sig"]
    mkt_mirror = np.array_equal(m2, -m1) and np.array_equal(sig11, sig_in)   # + input intact
    LL11 = np.where(rng11.random(n11) < 0.4, 100.0 + np.arange(n11), np.nan)
    SS11 = np.where(rng11.random(n11) < 0.4, 90.0 - np.arange(n11), np.nan)
    s1 = _mask_context_dir({"long_level": LL11, "short_level": SS11}, "stop", A, B)
    s2 = _mask_context_dir({"long_level": SS11, "short_level": LL11}, "stop", B, A)
    stop_mirror = (np.array_equal(s2["long_level"], s1["short_level"], equal_nan=True)
                   and np.array_equal(s2["short_level"], s1["long_level"], equal_nan=True))
    t11 = mkt_mirror and stop_mirror
    print(f"  [11] dir-mask mirror symmetry: market={mkt_mirror} stop={stop_mirror}")
    ok = ok and t11

    # [12] one-sided (HC2-01): allow_short=all-False -> HAKUNA short (market: sig -1 zote 0;
    #      stop: SS zote NaN na episodes() haitoi trade yoyote ya d=-1); long leg HAIJAGUSWA
    none12 = np.zeros(len(c), bool); all12 = np.ones(len(c), bool)
    from event_library_v2 import nr7_break, mr_zscore as _mrz
    mm = _mask_context_dir(_mrz(o, h, l, c), "market", all12, none12)["sig"]
    mkt_os = (mm != -1).all() and (mm == 1).any()
    st_out = nr7_break(o, h, l, c)
    st_m = _mask_context_dir(st_out, "stop", all12, none12)
    trs12 = episodes(st_m, "stop", o, h, l, c, atr, spr, hour)
    stop_os = (not np.isfinite(st_m["short_level"]).any()
               and np.array_equal(st_m["long_level"], st_out["long_level"], equal_nan=True)
               and all(t[2] == 1 for t in trs12) and len(trs12) > 0)
    t12 = mkt_os and stop_os
    print(f"  [12] one-sided: market no-shorts={mkt_os} stop SS=NaN+episodes long-only "
          f"(n={len(trs12)})={stop_os}")
    ok = ok and t12

    # [13] DECIDABILITY TRAP: mask inatumia value ya SIGNAL bar i, si entry bar i+1 —
    #      allow[i]=True pekee -> signal inaishi; allow[i+1]=True pekee -> signal inakufa
    n13 = 12; sig13 = np.zeros(n13, int); sig13[5] = 1
    aI = np.zeros(n13, bool); aI[5] = True                     # signal bar i TU
    aI1 = np.zeros(n13, bool); aI1[6] = True                   # entry bar i+1 TU (mtego)
    surv = _mask_context_dir({"sig": sig13}, "market", aI, np.zeros(n13, bool))["sig"][5] == 1
    dead = _mask_context_dir({"sig": sig13}, "market", aI1, np.zeros(n13, bool))["sig"][5] == 0
    t13 = surv and dead
    print(f"  [13] decidability (signal-bar i, si i+1): allow[i]->survives={surv} "
          f"allow[i+1]-only->dies={dead}")
    ok = ok and t13

    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="train", choices=["train", "validation", "holdout"])
    ap.add_argument("--tf", default="H1")
    ap.add_argument("--cycle", type=int, default=1, choices=[1, 2], help="1=C1 grid (TIER1/2); 2=GRID_C2")
    ap.add_argument("--holdout-final", dest="token", default=None, help="Chief token kwa holdout (S3)")
    ap.add_argument("--cells-file", dest="cells_file", default=None,
                    help="R1 restatement: jsonl ya cells maalum ZILIZOFUNGULIWA (badala ya grid)")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    from market_state_engine import cfg
    pairs = cfg()["pairs"]
    override = load_cells_file(a.cells_file) if a.cells_file else None
    if override is not None:
        pairs = sorted({c["pair"] for c in override})   # load data za pairs za cells hizo tu
    cands, tested, days = search(pairs, a.tf, a.split, a.token, cycle=a.cycle, cells_override=override)
    apply_fdr = a.split in ("validation", "holdout")     # FDR = out-of-sample pekee (S2/S3)
    jl, rpt = write_outputs(cands, tested, a.split, a.tf, days, apply_fdr=apply_fdr, cycle=a.cycle)
    print(f"cycle={a.cycle} candidates={len(cands)} (cells tested={tested}) split={a.split}")
    print(f"  {jl.relative_to(REPO_ROOT)}\n  {rpt.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
