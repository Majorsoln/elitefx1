"""
k4_dataset.py — M3-4 (MZUNGUKO-3, TABAKA 3): K4 TRAINING DATASET builder.

Kwa Model K4 (p(win|mazingira) — entry quality; charter docs/CYCLE3_CHARTER.md §Tabaka-3):
kila signal ya nr7_break kwenye configs HASA za STRAT-001 (USDCHF SL2/TP1 no-LATE) na STRAT-002
(USDJPY SL1/TP1 no-LATE), kwa split {train, validation}, na kwa KILA TRADE: features za mazingira
ya SIGNAL bar (decidable — hakuna kitu cha baadaye) + outcome yake (pnl, R, win, exit_type,
bars_held, MFE/MAE).

NIDHAMU (charter §Kinga + curriculum): **HOLDOUT HAIGUSWI KABISA** — hakuna signal ya 2025+
(hard guard: split ∈ {train,validation} PEKEE + assert max(ts) < HOLDOUT_START). Pipeline HASA ya
strategy iliyothibitika (REUSE nr7_break + _mask_context('no-LATE') + episodes — outcomes zinalingana
na STRAT-001/002 za proven). Features zote ni za signal-bar i (state ya i+1 haijulikani; session ya
entry = ratiba, decidable ex-ante — kama _mask_context).

ADDITIVE: ZERO golden fns (episodes/_mask_context/nr7_break byte-identical). MFE/MAE = rmap.excursions
(wrapper). OUTPUT: data/strategies/k4_dataset.parquet + reports/k4_dataset.md.

Endesha (PC ya data): python k4_dataset.py --build
Self-test (bila data):  python k4_dataset.py --self-test
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from event_library_v2 import EVENTS_V2
from event_quality_report import episodes, _sess, MAX_HOLD
from strategy_lab import _mask_context, load_window, TRAIN_END, VALID_END
from rmap import excursions

REPO_ROOT = Path(__file__).resolve().parents[2]
TF = "H1"
HOLDOUT_START = VALID_END                        # 2025-01-01 — hakuna signal >= hii KAMWE
SPLITS = ("train", "validation")                 # HOLDOUT HAIMO (hard guard)

# Configs HASA za PROVEN registry (docs/STRATEGIES.md) — nr7_break, no-LATE, H1, max_hold default (24)
STRATS = {
    "STRAT-001": dict(pair="USDCHF", sl_atr=2.0, tp_atr=1.0),
    "STRAT-002": dict(pair="USDJPY", sl_atr=1.0, tp_atr=1.0),
}
EVENT = "nr7_break"
SESSION_FILTER = "no-LATE"
OUT_PARQUET = "k4_dataset.parquet"
OUT_REPORT = "k4_dataset.md"
ATR_REL_WIN = 60                                 # rolling-median window (PAST bars) kwa atr_rel (K-3)

# ---------- MANIFEST (K-2): FEATURES (signal-bar decidable) vs OUTCOMES (matokeo) ----------
# Mpaka rasmi ili trainer ya M3-5 i-assert dhidi yake: outcome column KAMWE haiingii X (leak #1).
# `year`/`dir`/`ts_entry`/`entry_bar` ni META (identifiers) — SI features (year = year-proxy; §D5).
BASE_FEATURES = ["vol_state", "activity_state", "spread_state", "session_entry", "hour", "dow",
                 "atr_pips", "atr_rel", "range_nr7_atr"]
CTX_FEATURES = [f"{p}_{s}" for p in ("h4", "d1") for s in
                ("ema_slope", "linreg_slope", "trend_sign", "vol_state", "act_state",
                 "dist_res_atr", "dist_sup_atr", "rsi14", "roc10")]
FEATURES = BASE_FEATURES + CTX_FEATURES                    # decidable signal-bar PEKEE
OUTCOMES = ["pnl_pips", "pnl_R", "win", "exit_type", "bars_held",
            "mfe_r", "mae_r", "mfe_peak_bar"]              # matokeo — trainer HAIINGIZI kwenye X
META = ["strategy", "split", "pair", "year", "dir", "ts_entry", "entry_bar"]   # identifiers


def load_k4(path=None, features_only=True):
    """Loader ya M3-5: rudisha (X, y). ASSERT ya manifest — hakuna OUTCOMES column ndani ya X
    (trap ya leak #1: mfe_r/pnl_* kama feature = model 'inajua' baadaye). features_only=False ->
    rudisha DataFrame nzima. X inachukua FEATURES zilizopo tu; y = 'win'."""
    import polars as pl
    path = Path(path) if path else (REPO_ROOT / "data" / "strategies" / OUT_PARQUET)
    df = pl.read_parquet(path)
    if not features_only:
        return df
    feats = [c for c in FEATURES if c in df.columns]
    leak = set(feats) & set(OUTCOMES)
    assert not leak, f"K4 LEAK: outcome column(s) {sorted(leak)} ndani ya X"
    X = df.select(feats)
    y = df.select("win") if "win" in df.columns else None
    return X, y


def _year(ts_scalar):
    return int(str(ts_scalar)[:4])


def _atr_rel(atr, win=ATR_REL_WIN):
    """atr / rolling_median(atr, `win` PAST bars, shift(1)) — relative vol level (K-3; inaziba
    nafasi ya atr_n). NO-LOOKAHEAD: denominator = bars [i-win, i-1] PEKEE (haijumuishi bar i);
    numerator = atr[i] (ya signal bar, decidable). bars < win+? -> NaN."""
    atr = np.asarray(atr, float); n = len(atr); out = np.full(n, np.nan)
    for i in range(win, n):
        med = np.median(atr[i - win:i])                   # PAST win bars (haijumuishi i)
        if med > 0:
            out[i] = atr[i] / med
    return out


def _extra_states(pair, split):
    """activity_state/spread_state/day-of-week — SAMBAMBA na load_window (soma+sort+filter ILE ILE).
    (K-3: atr_n IMEONDOLEWA — state parquet haiihifadhi -> 100% NaN; badala yake atr_rel kwenye build.)
    Rudisha dict au None (parquet haipo/fupi). ts inarudishwa kwa uthibitisho wa alignment."""
    import polars as pl
    from latent_structure import state_path
    p = state_path(pair, TF)
    if not p.exists():
        return None
    df = pl.read_parquet(p).sort("ts")
    if split == "train":
        df = df.filter(pl.col("ts") < TRAIN_END)
    elif split == "validation":
        df = df.filter((pl.col("ts") >= TRAIN_END) & (pl.col("ts") < VALID_END))
    else:
        raise PermissionError("K4: split batili (HOLDOUT HAIGUSWI)")
    if df.height < 500:
        return None
    return dict(ts=df["ts"].to_numpy(),
                activity_state=np.asarray(df["activity_state"].to_list()),
                spread_state=np.asarray(df["spread_state"].to_list()),
                dow=df["ts"].dt.weekday().to_numpy())


# K-4: string-nulls za htf_context (state-column ya HTF bar ya warmup = "None"/"null"/"nan") -> null halisi
_NULLISH = {"None", "null", "nan", "NaN", "NAT", "", "none"}


def _ctx_feats(ctx, i):
    """h4_*/d1_* zote za ctx kwenye signal bar i (numeric->float/None; state->str; "None"->null). {} ctx None."""
    if not ctx:
        return {}
    out = {}
    for k in sorted(ctx):
        v = ctx[k][i]
        if isinstance(v, (str, np.str_)) or v is None:
            out[k] = None if (v is None or str(v) in _NULLISH) else str(v)   # K-4: "None" -> null
        else:
            fv = float(v)
            out[k] = None if not np.isfinite(fv) else round(fv, 6)
    return out


def _exit_type(d, e, sl_px, tp_px, h, l, xb, jend):
    """TP/SL/timeout kwa bar ya exit (tie -> SL, kama episodes). timeout = xb==jend NA hakuna barrier."""
    hit_sl = (l[xb] <= sl_px) if d == 1 else (h[xb] >= sl_px)
    hit_tp = (h[xb] >= tp_px) if d == 1 else (l[xb] <= tp_px)
    if hit_sl:
        return "SL"
    if hit_tp:
        return "TP"
    return "timeout"


def build_one(name, strat, split):
    """Rows za dataset kwa strategy moja × split. Pipeline HASA ya proven (nr7 + no-LATE + episodes)."""
    pair = strat["pair"]; sl_atr = strat["sl_atr"]; tp_atr = strat["tp_atr"]
    data = load_window(pair, TF, split)
    if data is None:
        return [], f"{name}/{split}: state parquet haipo/fupi"
    ext = _extra_states(pair, split)
    if ext is None or not np.array_equal(data["ts"], ext["ts"]):
        return [], f"{name}/{split}: extra-states haipo au alignment imevunjika"
    o, h, l_, c = data["o"], data["h"], data["l"], data["c"]
    atr, spr, hour, vol, ts = data["atr"], data["spr"], data["hour"], data["vol"], data["ts"]
    ctx = data.get("ctx")
    n = len(c)
    # HARD GUARD: hakuna signal ya HOLDOUT (>=2025) — kamwe
    if n and np.datetime64(ts.max(), "D") >= np.datetime64(HOLDOUT_START, "D"):
        raise PermissionError(f"K4 RED LINE: {pair}/{split} ina ts >= HOLDOUT ({HOLDOUT_START}) — imezuiwa")

    spec = EVENTS_V2[EVENT]
    out = spec["fn"](o, h, l_, c, data.get("tc"), hour)
    out = _mask_context(out, spec["entry"], hour, vol, SESSION_FILTER, None)     # no-LATE (proven)
    trs = episodes(out, spec["entry"], o, h, l_, c, atr, spr, hour, vol,
                   sl_atr=sl_atr, tp_atr=tp_atr, max_hold=MAX_HOLD)
    exc = excursions(trs, o, h, l_, c, out, spec["entry"], atr, sl_atr)
    atr_rel = _atr_rel(atr)                                # K-3: relative vol level (no-lookahead)

    rows = []
    for k, (eb, xb, d, pnl, sess_e, vs) in enumerate(trs):
        i = eb - 1                                        # signal bar (decidable)
        a = atr[i]
        # entry price = ILE ILE ya episodes (stop: max/min(level, open))
        lvl = out["long_level"][i] if d == 1 else out["short_level"][i]
        e = max(lvl, o[eb]) if d == 1 else min(lvl, o[eb])
        sl_px = e - d * sl_atr * a; tp_px = e + d * tp_atr * a
        jend = min(eb + MAX_HOLD, n - 1)
        etype = _exit_type(d, e, sl_px, tp_px, h, l_, xb, jend)
        mfe_p, mae_p, mfe_r, mae_r, peak = exc[k]
        risk = sl_atr * a
        row = dict(
            # --- META (identifiers — SI features) ---
            strategy=name, split=split, pair=pair, year=_year(ts[i]), dir=int(d),
            ts_entry=str(ts[eb]), entry_bar=int(eb),      # K-1: timestamp + bar-index kwa time-aware CV
            # --- features za SIGNAL bar (decidable) ---
            vol_state=str(vs), activity_state=str(ext["activity_state"][i]),
            spread_state=str(ext["spread_state"][i]),
            session_entry=_sess(int(hour[eb])), hour=int(hour[i]), dow=int(ext["dow"][i]),
            atr_pips=round(float(a), 4),
            atr_rel=(None if not np.isfinite(atr_rel[i]) else round(float(atr_rel[i]), 6)),  # K-3
            range_nr7_atr=(round(float((h[i] - l_[i]) / a), 4) if a > 0 else None),
            # --- outcome ---
            pnl_pips=round(float(pnl), 4),
            pnl_R=(round(float(pnl / risk), 4) if risk > 0 else None),
            win=int(pnl > 0), exit_type=etype, bars_held=int(xb - eb),
            mfe_r=(None if not np.isfinite(mfe_r) else round(float(mfe_r), 4)),
            mae_r=(None if not np.isfinite(mae_r) else round(float(mae_r), 4)),
            mfe_peak_bar=int(peak),
        )
        row.update(_ctx_feats(ctx, i))                    # h4_*/d1_* zote (kama ctx ipo)
        rows.append(row)
    return rows, None


def build(out_root=REPO_ROOT, write=True, splits=SPLITS, verbose=True):
    """Jenga dataset kamili: strategies 2 × splits {train,validation}. HOLDOUT HAIGUSWI.
    GUARD: split yoyote isiyo train/validation inakataliwa (PermissionError)."""
    bad = [s for s in splits if s not in SPLITS]
    if bad:
        raise PermissionError(f"K4: splits {bad} hazikubaliki — {SPLITS} PEKEE (HOLDOUT SEALED)")
    rows = []; notes = []
    for name, strat in STRATS.items():
        for split in splits:
            r, note = build_one(name, strat, split)
            rows.extend(r)
            if note:
                notes.append(note)
                if verbose:
                    print(f"  ONYO: {note}")
    if write:
        _write_outputs(rows, out_root, notes)
    return rows


# ---------- outputs ----------

def _write_outputs(rows, out_root, notes):
    import polars as pl
    out_root = Path(out_root)
    sdir = out_root / "data" / "strategies"; sdir.mkdir(parents=True, exist_ok=True)
    # union ya columns (ctx inaweza kukosekana kwa baadhi) — fill None
    cols = []
    for r in rows:
        for k in r:
            if k not in cols:
                cols.append(k)
    df = pl.DataFrame([{k: r.get(k) for k in cols} for r in rows]) if rows else pl.DataFrame()
    pq = sdir / OUT_PARQUET
    df.write_parquet(pq)

    L = ["# K4 TRAINING DATASET — entry-quality (nr7 STRAT-001/002; TRAIN+VALID)\n",
         f"*rows={len(rows):,} | strategies=STRAT-001(USDCHF SL2/TP1) + STRAT-002(USDJPY SL1/TP1) | "
         f"nr7_break no-LATE H1 | features=signal-bar (decidable) | HOLDOUT HAIGUSWI (2025+ sealed)*\n",
         "> **Curriculum note (charter §M3-QA):** dataset hii ni malighafi ya K4 — LAZIMA ithibitishwe "
         "(label integrity, no-leakage, class balance, N per regime, mwaka-coverage) na SCIENTIST-D "
         "KABLA ya M3-5 training. Outcomes = honest harness (costs ndani); features = signal-bar tu.\n"]
    if notes:
        L.append("\n**ONYO (windows zilizorukwa):** " + "; ".join(notes) + "\n")

    # K-2: FEATURE/OUTCOME MANIFEST (rasmi — loader load_k4() i-assert; outcome KAMWE ndani ya X)
    L.append("\n## Manifest (K-2): FEATURES (decidable, signal-bar) vs OUTCOMES vs META\n")
    L.append(f"- **FEATURES** ({len(FEATURES)}): `{', '.join(FEATURES)}`")
    L.append(f"- **OUTCOMES** ({len(OUTCOMES)}, KAMWE si feature): `{', '.join(OUTCOMES)}`")
    L.append(f"- **META** (identifiers, si feature — `year`/`dir` = year-proxy §D5): `{', '.join(META)}`")
    L.append("- Trainer ya M3-5 itumie `k4_dataset.load_k4(features_only=True)` -> (X,y) yenye "
             "ASSERT kwamba hakuna OUTCOMES ndani ya X (trap ya leak #1 — mfe_r/pnl_* kama feature).")

    # counts + baseline win rate + class balance per strategy×split
    L.append("\n## Counts + baseline (win rate = p(pnl>0), class balance)\n")
    L.append("| strategy | split | N | wins | win_rate | EV_pips | EV_R |")
    L.append("|----------|-------|---|------|----------|--------|------|")
    for name in STRATS:
        for split in SPLITS:
            sub = [r for r in rows if r["strategy"] == name and r["split"] == split]
            if not sub:
                L.append(f"| {name} | {split} | 0 | — | — | — | — |"); continue
            wins = sum(r["win"] for r in sub)
            wr = wins / len(sub)
            ev = float(np.mean([r["pnl_pips"] for r in sub]))
            evr = float(np.mean([r["pnl_R"] for r in sub if r["pnl_R"] is not None]))
            L.append(f"| {name} | {split} | {len(sub):,} | {wins:,} | {wr:.3f} | {ev:+.3f} | {evr:+.3f} |")

    # exit_type distribution
    L.append("\n## Exit-type distribution (TP / SL / timeout)\n")
    L.append("| strategy | split | TP | SL | timeout |")
    L.append("|----------|-------|----|----|---------|")
    for name in STRATS:
        for split in SPLITS:
            sub = [r for r in rows if r["strategy"] == name and r["split"] == split]
            if not sub:
                continue
            et = {t: sum(1 for r in sub if r["exit_type"] == t) for t in ("TP", "SL", "timeout")}
            L.append(f"| {name} | {split} | {et['TP']} | {et['SL']} | {et['timeout']} |")

    # feature completeness (NaN%) — feature yenye pengo kubwa HAIFUNDISHWI (curriculum gate §M3-QA)
    L.append("\n## Feature completeness (NaN% — FEATURES za manifest; pengo kubwa = haifundishwi)\n")
    L.append("| feature | NaN% |")
    L.append("|---------|------|")
    for feat in FEATURES:
        if rows and feat in cols:
            miss = sum(1 for r in rows if r.get(feat) is None)
            L.append(f"| {feat} | {100 * miss / len(rows):.1f} |")

    # K-5: regime-cells "hazifundishiki bado" (N<30 — §Q6): spread_state=UNKNOWN, d1_vol_state null, n.k.
    L.append("\n## Cells 'hazifundishiki bado' (N<30 per strategy×regime — §Q6, QUARANTINE)\n")
    L.append("*Model isijifunze kelele ya cell tupu. Regime = (vol_state, activity_state, spread_state).*\n")
    L.append("| strategy | vol_state | activity_state | spread_state | N |")
    L.append("|----------|-----------|----------------|--------------|---|")
    from collections import Counter
    untr = []
    for name in STRATS:
        sub = [r for r in rows if r["strategy"] == name]
        cnt = Counter((r["vol_state"], r["activity_state"], r["spread_state"]) for r in sub)
        for (v, a, s), nn in sorted(cnt.items()):
            if nn < 30:
                untr.append((name, v, a, s, nn))
                L.append(f"| {name} | {v} | {a} | {s} | {nn} |")
    if not untr:
        L.append("| — | — | — | — | — |")

    # C4 (§D1) + C5 (§C5): tahadhari za mafunzo — ndani ya kitabu ili kila mtumiaji aone
    L.append("\n## Tahadhari za mafunzo (ndani ya kitabu — §D1/§C5 audit)\n")
    L.append("- **VALID selection-taint (§D1):** STRAT-001/002 ZILICHAGULIWA kwa VALIDATION 2023-24 "
             "(order statistics — STRAT-001 1/1,939 wa FDR). Win ya VALID (79.3%/60.6%) ime-overstate "
             "vs holdout halisi (73.9%/57.8%). NIDHAMU M3-5: model selection = blocked-CV ndani ya TRAIN "
             "PEKEE; VALID = check MOJA bila tuning; lift ya VALID tarajia ~0.35-0.5x mbele (shrinkage).")
    L.append("- **Server-time/DST (§C5):** `hour` ni server-time; DST inahamisha London/NY ±1h kwa wiki "
             "kadhaa kwa mwaka -> hour-level features zina jitter; `session_entry` ni imara zaidi.")
    L.append("- **Non-stationarity (§D5):** `atr_pips` ni ABSOLUTE level (year-proxy risk) — `atr_rel` "
             "(relative, rolling-median 60 PAST bars) imeongezwa kama mbadala deseasonalized (K-3).")

    L.append("\n*data/strategies/k4_dataset.parquet — 1 row kwa trade (META + FEATURES + OUTCOMES). "
             "Time-aware CV: tumia `ts_entry`/`entry_bar` (K-1) + blocked folds (purge bars 24, §D3). "
             "Next (M3-5): SCIENTIST-D design model interpretable (p(win|state)) baada ya certification.*")

    rpt = out_root / "reports" / OUT_REPORT; rpt.parent.mkdir(parents=True, exist_ok=True)
    rpt.write_text("\n".join(L), encoding="utf-8")
    return pq, rpt


# ---------- self-test (synthetic — bila data ya nje) ----------

def _fixture(seed, split="train", n=4000, ctx=True):
    """Bars H1 synthetic zenye nr7 signals + ts ndani ya window ya split + state strings + ctx."""
    from event_library_v2 import _synthetic
    o, h, l_, c, tc, hour = _synthetic(n=n, seed=seed)
    atr = np.maximum(h - l_, 0.1)
    start = "2016-01-04" if split == "train" else "2023-06-01"
    ts = (np.datetime64(start) + np.arange(n) * np.timedelta64(1, "h"))
    hr = (ts.astype("datetime64[h]").astype(int) % 24).astype(int)
    data = dict(o=o, h=h, l=l_, c=c, atr=atr, spr=np.full(n, 1.0), tc=tc, hour=hr,
                vol=np.where(np.arange(n) % 2 == 0, "NORMAL", "HIGH"), ts=ts, days=250)
    # ctx: d1_vol_state ina "None" (null-cast artifact) scattered kwa K-4 test (baadhi ya trade-bars)
    dvs = np.where(np.arange(n) % 4 == 0, "None", "NORMAL").astype(object)
    data["ctx"] = (dict(d1_trend_sign=np.ones(n), h4_rsi14=np.full(n, 55.0), d1_vol_state=dvs)
                   if ctx else None)
    return data


def _fixture_ext(data):
    """extra-states sambamba na fixture (ts ILE ILE) — atr_n imeondolewa (K-3)."""
    n = len(data["c"])
    return dict(ts=data["ts"],
                activity_state=np.where(np.arange(n) % 3 == 0, "LOW", "NORMAL"),
                spread_state=np.where(np.arange(n) % 5 == 0, "WIDE", "NORMAL"),
                dow=(data["ts"].astype("datetime64[D]").astype(int) % 7))


def self_test():
    ok = True
    import sys as _sys, tempfile, json as _json
    _self = _sys.modules[__name__]

    # [1] HARD GUARD: build(split='holdout'/'test') -> PermissionError (HOLDOUT SEALED)
    g1 = g2 = False
    try:
        build(splits=("holdout",), write=False)
    except PermissionError:
        g1 = True
    try:
        build(splits=("train", "holdout"), write=False)
    except PermissionError:
        g2 = True
    print(f"  [1] HOLDOUT guard: holdout-refused={g1} mixed-refused={g2} -> {g1 and g2}")
    ok = ok and g1 and g2

    # [1b] RED-LINE assert: window yenye ts>=2025 -> PermissionError hata kama split='validation'
    orig_lw = _self.load_window; orig_ex = _self._extra_states
    leak = _fixture(3, split="train", n=2000)
    leak["ts"] = np.datetime64("2025-06-01") + np.arange(2000) * np.timedelta64(1, "h")  # HOLDOUT!
    _self.load_window = lambda p, tf, s, token=None: leak
    _self._extra_states = lambda p, s: _fixture_ext(leak)
    g3 = False
    try:
        build_one("STRAT-001", STRATS["STRAT-001"], "validation")
    except PermissionError:
        g3 = True
    _self.load_window = orig_lw; _self._extra_states = orig_ex
    print(f"  [1b] RED-LINE ts>=2025 -> refuse (hata validation): {g3}")
    ok = ok and g3

    # [2] DECIDABILITY trap: feature = state ya SIGNAL bar i, si entry bar i+1. Tengeneza vol
    #     inayobadilika kila bar; thibitisha row["vol_state"] == vol[signal] (si vol[entry]).
    fx = _fixture(1, split="train", n=4000)
    ext = _fixture_ext(fx)
    _self.load_window = lambda p, tf, s, token=None: fx
    _self._extra_states = lambda p, s: ext
    try:
        rows = build_one("STRAT-001", STRATS["STRAT-001"], "train")[0]
    finally:
        _self.load_window = orig_lw; _self._extra_states = orig_ex
    # kwa kila row: signal bar = ? tunahesabu upya kutoka trades ni ngumu; badala yake thibitisha
    # kila vol_state ni ya index ambapo entry bar ina vol tofauti (vol inabadilika kila bar).
    dec_ok = len(rows) > 0 and all(r["vol_state"] in ("NORMAL", "HIGH") for r in rows)
    # trap halisi: vol[i] != vol[i+1] daima (alternating) -> kama tungechukua entry bar, vol_state
    # ingekuwa "kinyume". Tunathibitisha kupitia recompute kwenye [2b].
    print(f"  [2] rows built: n={len(rows)} vol_state valid -> {dec_ok}")
    ok = ok and dec_ok

    # [2b] decidability EXACT: jenga upya signals na thibitisha vol_state == vol[eb-1] kwa kila trade
    fx2 = _fixture(1, split="train", n=4000)
    out = EVENTS_V2[EVENT]["fn"](fx2["o"], fx2["h"], fx2["l"], fx2["c"], fx2["tc"], fx2["hour"])
    out = _mask_context(out, "stop", fx2["hour"], fx2["vol"], SESSION_FILTER, None)
    trs = episodes(out, "stop", fx2["o"], fx2["h"], fx2["l"], fx2["c"], fx2["atr"], fx2["spr"],
                   fx2["hour"], fx2["vol"], sl_atr=2.0, tp_atr=1.0, max_hold=MAX_HOLD)
    _self.load_window = lambda p, tf, s, token=None: fx2
    _self._extra_states = lambda p, s: _fixture_ext(fx2)
    try:
        rows2 = build_one("STRAT-001", STRATS["STRAT-001"], "train")[0]
    finally:
        _self.load_window = orig_lw; _self._extra_states = orig_ex
    exact = (len(rows2) == len(trs)
             and all(rows2[k]["vol_state"] == str(fx2["vol"][trs[k][0] - 1]) for k in range(len(trs)))
             and all(rows2[k]["vol_state"] != str(fx2["vol"][trs[k][0]]) for k in range(len(trs))))
    print(f"  [2b] decidability EXACT: vol_state==vol[signal i] (si entry i+1) kwa {len(trs)} trades -> {exact}")
    ok = ok and exact

    # [3] full build + schema + determinism + outputs + baseline win rate
    fxs = {("USDCHF", "train"): _fixture(1, "train"), ("USDCHF", "validation"): _fixture(2, "validation"),
           ("USDJPY", "train"): _fixture(4, "train"), ("USDJPY", "validation"): _fixture(5, "validation")}
    _self.load_window = lambda p, tf, s, token=None: fxs.get((p, s))
    _self._extra_states = lambda p, s: _fixture_ext(fxs[(p, s)])
    try:
        with tempfile.TemporaryDirectory() as tmp:
            ra = build(out_root=tmp, verbose=False)
            rb = build(out_root=tmp, verbose=False)
            det = _json.dumps(ra, sort_keys=True) == _json.dumps(rb, sort_keys=True)
            need = {"strategy", "split", "pair", "year", "dir", "ts_entry", "entry_bar",
                    "vol_state", "activity_state", "spread_state", "session_entry", "hour", "dow",
                    "atr_pips", "atr_rel", "range_nr7_atr",
                    "pnl_pips", "pnl_R", "win", "exit_type", "bars_held", "mfe_r", "mae_r"}
            schema_ok = (all(need <= set(r) for r in ra) and len(ra) > 0
                         and not any("atr_n" in r for r in ra))          # K-3: atr_n imeondolewa
            splits_ok = set(r["split"] for r in ra) == {"train", "validation"}
            strat_ok = set(r["strategy"] for r in ra) == {"STRAT-001", "STRAT-002"}
            no_holdout = all(r["year"] <= 2024 for r in ra)
            et_ok = set(r["exit_type"] for r in ra) <= {"TP", "SL", "timeout"}
            ctx_ok = all("d1_trend_sign" in r and "h4_rsi14" in r for r in ra)
            import polars as pl
            pq = pl.read_parquet(Path(tmp) / "data" / "strategies" / OUT_PARQUET)
            rpt = (Path(tmp) / "reports" / OUT_REPORT).read_text(encoding="utf-8")
            files_ok = pq.height == len(ra) and "win_rate" in rpt and "HOLDOUT HAIGUSWI" in rpt
        t3 = (det and schema_ok and splits_ok and strat_ok and no_holdout and et_ok
              and ctx_ok and files_ok)
    finally:
        _self.load_window = orig_lw; _self._extra_states = orig_ex
    print(f"  [3] build: rows={len(ra)} schema={schema_ok} splits={splits_ok} strat={strat_ok} "
          f"no-holdout={no_holdout} exit={et_ok} ctx={ctx_ok}")
    print(f"  [4] outputs+determinism: files={files_ok} det={det} -> {t3}")
    ok = ok and t3

    # [5] exit_type correctness: trade crafted yenye TP hit (long) -> 'TP'; SL hit -> 'SL'
    #     entry e=100, sl_atr=2 atr=1 -> sl_px=98; tp_atr=1 -> tp_px=101. bar ya exit high>=101 -> TP
    h = np.array([100., 101.5]); l_ = np.array([100., 100.])
    tp = _exit_type(1, 100.0, 98.0, 101.0, h, l_, xb=1, jend=5)
    h2 = np.array([100., 100.]); l2 = np.array([100., 97.5])
    slt = _exit_type(1, 100.0, 98.0, 101.0, h2, l2, xb=1, jend=5)
    h3 = np.full(6, 100.5); l3 = np.full(6, 99.5)                # hakuna barrier (98..101) inayogusika
    to = _exit_type(1, 100.0, 98.0, 101.0, h3, l3, xb=5, jend=5)
    t5 = (tp == "TP" and slt == "SL" and to == "timeout")
    print(f"  [5] exit_type: TP={tp} SL={slt} timeout={to} -> {t5}")
    ok = ok and t5

    # [6] K-2 MANIFEST assert: load_k4 X ina FEATURES tu, HAKUNA OUTCOMES; leak -> AssertionError
    fx6 = {("USDCHF", "train"): _fixture(1, "train"), ("USDCHF", "validation"): _fixture(2, "validation"),
           ("USDJPY", "train"): _fixture(4, "train"), ("USDJPY", "validation"): _fixture(5, "validation")}
    _self.load_window = lambda p, tf, s, token=None: fx6.get((p, s))
    _self._extra_states = lambda p, s: _fixture_ext(fx6[(p, s)])
    try:
        with tempfile.TemporaryDirectory() as tmp:
            build(out_root=tmp, verbose=False)
            pqp = Path(tmp) / "data" / "strategies" / OUT_PARQUET
            X, y = load_k4(pqp, features_only=True)
            no_outcome = not (set(X.columns) & set(OUTCOMES))
            feats_ok = set(X.columns) <= set(FEATURES) and "atr_rel" in X.columns and "atr_n" not in X.columns
            y_ok = y is not None and y.columns == ["win"]
            # leak trap: kama tunga-rename win->kama feature, assert lazima ishike
            import polars as pl
            df_leak = pl.read_parquet(pqp).rename({"vol_state": "vol_state"})  # no-op; jenga leak kwa mkono
            trap = False
            try:
                # simulate: FEATURES ikiwa na 'win' -> load_k4 lazima i-assert
                _orig = globals()["FEATURES"]
                globals()["FEATURES"] = _orig + ["win"]
                load_k4(pqp, features_only=True)
            except AssertionError:
                trap = True
            finally:
                globals()["FEATURES"] = _orig
    finally:
        _self.load_window = orig_lw; _self._extra_states = orig_ex
    t6 = no_outcome and feats_ok and y_ok and trap
    print(f"  [6] K-2 manifest: X no-outcome={no_outcome} feats<=FEATURES={feats_ok} y=win={y_ok} "
          f"leak-assert={trap} -> {t6}")
    ok = ok and t6

    # [7] K-1 ts_entry: non-null + monotonic non-decreasing per strategy×split; entry_bar int
    fx7 = _fixture(1, "train")
    _self.load_window = lambda p, tf, s, token=None: fx7
    _self._extra_states = lambda p, s: _fixture_ext(fx7)
    try:
        r7 = build_one("STRAT-001", STRATS["STRAT-001"], "train")[0]
    finally:
        _self.load_window = orig_lw; _self._extra_states = orig_ex
    tse = [r["ts_entry"] for r in r7]
    t7 = (len(r7) > 0 and all(r["ts_entry"] is not None for r in r7)
          and tse == sorted(tse) and all(isinstance(r["entry_bar"], int) for r in r7)
          and all(r["entry_bar"] == r7[k]["entry_bar"] for k, r in enumerate(r7)))
    print(f"  [7] K-1 ts_entry: non-null + monotonic (n={len(r7)}) entry_bar int -> {t7}")
    ok = ok and t7

    # [8] K-3 atr_rel TRAP: no-lookahead (truncation invariance) — atr_rel[:k] haiathiriwi na bars > k
    aa = np.abs(np.random.default_rng(7).normal(5, 1.5, 300)) + 0.5
    full = _atr_rel(aa); trunc = _atr_rel(aa[:200])
    inv = np.allclose(full[:200][~np.isnan(full[:200])], trunc[~np.isnan(trunc)], equal_nan=False)
    # na denominator ni PAST tu: atr_rel[i] haitumii atr[i+1..]; warmup < win -> NaN
    warm_ok = np.all(np.isnan(full[:ATR_REL_WIN])) and np.isfinite(full[ATR_REL_WIN])
    t8 = inv and warm_ok
    print(f"  [8] K-3 atr_rel no-lookahead: truncation-invariant={inv} warmup<win=NaN={warm_ok} -> {t8}")
    ok = ok and t8

    # [9] K-4: d1_vol_state string "None" -> null halisi (si "None")
    fx9 = _fixture(1, "train")
    _self.load_window = lambda p, tf, s, token=None: fx9
    _self._extra_states = lambda p, s: _fixture_ext(fx9)
    try:
        r9 = build_one("STRAT-001", STRATS["STRAT-001"], "train")[0]
    finally:
        _self.load_window = orig_lw; _self._extra_states = orig_ex
    dvs_vals = set(r.get("d1_vol_state") for r in r9)
    t9 = "None" not in dvs_vals and None in dvs_vals            # warmup rows -> null, si "None"
    print(f"  [9] K-4 d1_vol_state 'None'->null: values={dvs_vals} -> {t9}")
    ok = ok and t9

    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true", help="jenga K4 dataset (TRAIN+VALID; PC ya data)")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.build:
        print("Tumia --build (K4 dataset) | --self-test.", file=sys.stderr)
        return 2
    rows = build()
    for name in STRATS:
        for split in SPLITS:
            sub = [r for r in rows if r["strategy"] == name and r["split"] == split]
            if sub:
                wr = sum(r["win"] for r in sub) / len(sub)
                print(f"  {name} {split}: N={len(sub)} win_rate={wr:.3f}")
    print(f"K4 dataset: rows={len(rows):,}\n  data/strategies/{OUT_PARQUET}\n  reports/{OUT_REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
