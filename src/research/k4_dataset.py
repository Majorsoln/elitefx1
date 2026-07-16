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


def _year(ts_scalar):
    return int(str(ts_scalar)[:4])


def _extra_states(pair, split):
    """activity_state/spread_state/atr_n/day-of-week — SAMBAMBA na load_window (soma+sort+filter
    ILE ILE). Rudisha dict au None (parquet haipo/fupi). ts inarudishwa kwa uthibitisho wa alignment."""
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
                atr_n=df["atr_n"].to_numpy() if "atr_n" in df.columns else np.full(df.height, np.nan),
                dow=df["ts"].dt.weekday().to_numpy())


def _ctx_feats(ctx, i):
    """h4_*/d1_* zote za ctx kwenye signal bar i (numeric->float/None; state->str). {} kama ctx None."""
    if not ctx:
        return {}
    out = {}
    for k in sorted(ctx):
        v = ctx[k][i]
        if isinstance(v, (str, np.str_)) or v is None:
            out[k] = None if v is None else str(v)
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
            strategy=name, split=split, pair=pair, year=_year(ts[i]), dir=int(d),
            # --- features za SIGNAL bar (decidable) ---
            vol_state=str(vs), activity_state=str(ext["activity_state"][i]),
            spread_state=str(ext["spread_state"][i]),
            session_entry=_sess(int(hour[eb])), hour=int(hour[i]), dow=int(ext["dow"][i]),
            atr_pips=round(float(a), 4),
            atr_n=(None if not np.isfinite(ext["atr_n"][i]) else round(float(ext["atr_n"][i]), 6)),
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

    # feature completeness (NaN%) — feature yenye pengo kubwa HAIFUNDISHWI (curriculum gate)
    L.append("\n## Feature completeness (NaN% — feature yenye pengo kubwa haifundishwi, §M3-QA)\n")
    L.append("| feature | NaN% |")
    L.append("|---------|------|")
    if rows:
        allcols = [k for k in cols if k not in ("strategy", "split", "pair", "exit_type",
                                                "vol_state", "activity_state", "spread_state",
                                                "session_entry")]
        for feat in allcols:
            miss = sum(1 for r in rows if r.get(feat) is None)
            L.append(f"| {feat} | {100 * miss / len(rows):.1f} |")

    L.append("\n*data/strategies/k4_dataset.parquet — 1 row kwa trade (signal-bar features + outcome). "
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
    data["ctx"] = dict(d1_trend_sign=np.ones(n), h4_rsi14=np.full(n, 55.0)) if ctx else None
    return data


def _fixture_ext(data):
    """extra-states sambamba na fixture (ts ILE ILE)."""
    n = len(data["c"])
    return dict(ts=data["ts"],
                activity_state=np.where(np.arange(n) % 3 == 0, "LOW", "NORMAL"),
                spread_state=np.where(np.arange(n) % 5 == 0, "WIDE", "NORMAL"),
                atr_n=np.full(n, 1.0), dow=(data["ts"].astype("datetime64[D]").astype(int) % 7))


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
            need = {"strategy", "split", "pair", "year", "dir", "vol_state", "activity_state",
                    "spread_state", "session_entry", "hour", "dow", "atr_pips", "range_nr7_atr",
                    "pnl_pips", "pnl_R", "win", "exit_type", "bars_held", "mfe_r", "mae_r"}
            schema_ok = all(need <= set(r) for r in ra) and len(ra) > 0
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
