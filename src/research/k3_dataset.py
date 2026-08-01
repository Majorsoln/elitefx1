"""
k3_dataset.py — M4-1: DATASET ya KAIROS-3 (docs/CYCLE4_ML_CHARTER.md §6.2 + §3; KAIROS_3_SPEC §3).

KUSUDI: triple-barrier labels + features kwa **BARS ZOTE** (si nr7 pekee), **pairs 12**, **TRAIN
PEKEE** — chakula cha GBM ya M4-2. Charter §3: "Chanzo = `event_quality_report.episodes` (golden —
next-bar fills, tie->SL, gharama halisi). **HAKUNA labeling mpya iliyoandikwa mkono** (GIGO + parity)."

## Tatizo la kiufundi na SULUHISHO lake (muhimu — hapa ndipo uaminifu unapoishi)
`episodes()` ina **non-overlap discipline**: bar iliyo ndani ya position iliyo wazi INARUKWA. Hiyo ni
sheria ya PORTFOLIO (position moja kwa wakati), si sheria ya LABELING — kwa dataset tunahitaji label
ya KILA bar. Kuandika labeler mpya = kuvunja parity (charter §3 inakataza).

**Suluhisho (ZERO code mpya ya fill):** bars zinagawanywa kwa **residue classes** za `stride =
max_hold + 2`. Ndani ya class moja, signals ziko mbali kiasi kwamba trade ya bar i (exit <= i+1+
max_hold) **daima** inafunga kabla ya signal inayofuata (i + max_hold + 2) — kwa hiyo non-overlap
HAIRUKI KAMWE. `episodes()` inaitwa mara `stride` kwa kila (pair, dir), na muungano wa classes zote
= bars ZOTE, kila moja ikiwa na label ya **fill logic ILE ILE ya golden** (byte-identical).
Uthibitisho uko kwenye self-test [2]: labels za residue-scan == labels za episodes iliyoitwa
moja-moja, na coverage = bars zote zenye atr>0.

## Muundo
- Kila bar i, kila **dir** (+1 long, -1 short): entry = MARKET kwenye open ya bar i+1 (charter §2:
  "P(TP kabla ya SL) kwa KILA bar"), gharama halisi = spread ya bar ya entry + SLIP_MARKET (L-039).
- **Geometries MBILI** (label sets, si rows tofauti): SL2.0/TP1.0 (KAIROS-1) na SL1.0/TP1.0
  (KAIROS-2) — M4-2 itafanya threshold-sweep juu ya zote mbili bila kujenga upya dataset.
- **Features = manifest ya k4_dataset** (REUSE: `_atr_rel`, `_extra_states`, `_ctx_feats`, `_sess`)
  — zote za **SIGNAL bar i** (decidable; state ya i+1 haijulikani). Nyongeza: `range_atr` (badala ya
  `range_nr7_atr` isiyo na maana nje ya nr7) na `nr7_flag` (je bar hii ni signal ya nr7? — daraja la
  kulinganisha ML dhidi ya breadth baseline ndani ya dataset ile ile).
- **SPLIT: TRAIN PEKEE** (2016-2022). Guard mbili: `split != "train"` -> PermissionError, NA assert
  `max(ts) < TRAIN_END`. VALIDATION haitumiki M4-1 (ni ya gate ya M4-2); HOLDOUT + sealed 2026-05+
  hazipo kwenye njia hii kabisa.
- **CV:** `purged_cv.purged_folds` (purge + embargo = horizon ya label) — folds za MUDA, mpaka mmoja
  kwa pairs zote (cross-pair leakage haiwezekani). Fold assignment inahifadhiwa kwenye dataset.

## Wapi inaandikwa (na kwa nini)
Parquet **kwa kila pair** ndani ya `data/processed/k3/` — si `data/strategies/`. Sababu: dataset ni
~1M rows (mamia ya MB); `data/processed/**` iko nje ya git (`.gitignore`), kama data nyingine nzito.
Rekodi zinazoenda git ni **ripoti** (`reports/k3_dataset.md`) + manifest JSON (nyepesi).

Endesha (PC ya data):  python k3_dataset.py --build
Self-test (bila data):  python k3_dataset.py --self-test
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

from event_library_v2 import EVENTS_V2
from event_quality_report import episodes, _sess, MAX_HOLD, SLIP_MARKET
from strategy_lab import load_window, TRAIN_END
from k4_dataset import _atr_rel, _extra_states, _ctx_feats, _year, BASE_FEATURES, CTX_FEATURES
from purged_cv import purged_folds, fold_report

REPO_ROOT = Path(__file__).resolve().parents[2]

TF = "H1"
SPLIT = "train"                                  # M4-1: TRAIN PEKEE (charter §6.2)
DIRS = (1, -1)
GEOMS = {"sl2tp1": (2.0, 1.0), "sl1tp1": (1.0, 1.0)}    # KAIROS-1 · KAIROS-2 geometry
STRIDE = MAX_HOLD + 2                            # residue spacing — non-overlap HAIRUKI (§Suluhisho)
N_FOLDS = 5
OUT_DIR = Path("data") / "processed" / "k3"      # NJE ya git (data/**), kama data nyingine nzito
OUT_REPORT = "k3_dataset.md"
OUT_MANIFEST = "k3_manifest.json"

# ---------- MANIFEST (mpaka rasmi — trainer ya M4-2 ita-assert dhidi yake) ----------
# FEATURES = za k4 manifest (BASE bila `range_nr7_atr`) + `range_atr` + `nr7_flag` + CTX zote.
FEATURES = ([f for f in BASE_FEATURES if f != "range_nr7_atr"] + ["range_atr", "nr7_flag"]
            + CTX_FEATURES)
OUTCOMES = [f"{k}_{g}" for g in GEOMS for k in ("pnl_pips", "pnl_R", "win", "bars_held")]
META = ["pair", "split", "year", "dir", "ts_entry", "ts_exit", "signal_bar", "fold"]


def load_k3(path=None, features_only=True, geom="sl1tp1"):
    """Loader ya M4-2: rudisha (X, y, meta). ASSERT ya manifest — HAKUNA outcome ndani ya X
    (leak #1). `geom` inachagua label set. path = directory ya parquet (default OUT_DIR)."""
    import polars as pl
    p = Path(path) if path else (REPO_ROOT / OUT_DIR)
    df = pl.read_parquet(str(p / "*.parquet")) if p.is_dir() else pl.read_parquet(p)
    if not features_only:
        return df
    feats = [c for c in FEATURES if c in df.columns]
    leak = set(feats) & set(OUTCOMES)
    assert not leak, f"K3 LEAK: outcome column(s) {sorted(leak)} ndani ya X"
    ycol = f"win_{geom}"
    assert ycol in df.columns, f"label {ycol} haipo (geoms: {list(GEOMS)})"
    return df.select(feats), df.select(ycol), df.select([c for c in META if c in df.columns])


def _pairs():
    from market_state_engine import cfg
    return list(cfg()["pairs"])


def _guard(split):
    if split != SPLIT:
        raise PermissionError(
            f"M4-1 DATASET ni TRAIN PEKEE — split='{split}' imekataliwa (charter §6.2). "
            "VALIDATION ni ya gate ya M4-2; HOLDOUT/sealed hazipo kwenye njia hii.")


def label_bars(data, sl_atr, tp_atr, dirs=DIRS, stride=STRIDE, max_hold=MAX_HOLD):
    """Labels za triple-barrier kwa **bars ZOTE** kwa kutumia `episodes()` KAMA ILIVYO.
    Residue-class scan (§Suluhisho): kwa kila dir na kila r < stride, sig[i]=dir kwa i≡r (mod stride)
    -> episodes -> trade kwa KILA bar iliyowekwa alama (non-overlap hairuki kwa ujenzi).
    Rudisha {(signal_bar, dir): (exit_bar, pnl_pips)}."""
    o, h, l_, c = data["o"], data["h"], data["l"], data["c"]
    atr, spr, hour, vol = data["atr"], data["spr"], data["hour"], data.get("vol")
    n = len(c)
    out = {}
    for d in dirs:
        for r in range(stride):
            sig = np.zeros(n, dtype=int)
            sig[r::stride] = d
            sig[n - 1:] = 0                                  # bar ya mwisho haina i+1
            trs = episodes({"sig": sig}, "market", o, h, l_, c, atr, spr, hour, vol,
                           sl_atr=sl_atr, tp_atr=tp_atr, max_hold=max_hold)
            for (eb, xb, dd, pnl, _sess_e, _vs) in trs:
                out[(eb - 1, int(dd))] = (int(xb), float(pnl))
    return out


def build_pair(pair, split=SPLIT, geoms=GEOMS):
    """Rows za dataset kwa pair moja (bars zote × dirs 2 × geometries 2 kama columns)."""
    _guard(split)
    data = load_window(pair, TF, split)
    if data is None or data.get("ts") is None:
        return [], f"{pair}: state parquet haipo/fupi"
    ext = _extra_states(pair, split)
    if ext is None or not np.array_equal(data["ts"], ext["ts"]):
        return [], f"{pair}: extra-states haipo au alignment imevunjika"
    ts = data["ts"]
    if len(ts) and np.datetime64(ts.max(), "D") >= np.datetime64(TRAIN_END, "D"):
        raise PermissionError(f"K3 RED LINE: {pair} ina ts >= TRAIN_END ({TRAIN_END}) — imezuiwa")

    o, h, l_, c = data["o"], data["h"], data["l"], data["c"]
    atr, hour, vol, ctx = data["atr"], data["hour"], data["vol"], data.get("ctx")
    n = len(c)
    atr_rel = _atr_rel(atr)
    nr7 = EVENTS_V2["nr7_break"]["fn"](o, h, l_, c, data.get("tc"), hour)
    nr7_flag = np.isfinite(nr7["long_level"])                # bar hii ni signal ya nr7? (decidable)

    labels = {g: label_bars(data, sl, tp) for g, (sl, tp) in geoms.items()}
    keys = sorted(set().union(*[set(v) for v in labels.values()]))
    rows = []
    for (i, d) in keys:
        a = atr[i]
        if not (a > 0) or i + 1 >= n:
            continue
        row = dict(pair=pair, split=split, year=_year(ts[i]), dir=int(d),
                   ts_entry=str(ts[i + 1]), signal_bar=int(i),
                   vol_state=str(vol[i]), activity_state=str(ext["activity_state"][i]),
                   spread_state=str(ext["spread_state"][i]),
                   session_entry=_sess(int(hour[i + 1])), hour=int(hour[i]),
                   dow=int(ext["dow"][i]), atr_pips=round(float(a), 4),
                   atr_rel=(None if not np.isfinite(atr_rel[i]) else round(float(atr_rel[i]), 6)),
                   range_atr=round(float((h[i] - l_[i]) / a), 4),
                   nr7_flag=int(bool(nr7_flag[i])))
        xb_max = i + 1
        for g in geoms:
            v = labels[g].get((i, d))
            if v is None:
                row[f"pnl_pips_{g}"] = None; row[f"pnl_R_{g}"] = None
                row[f"win_{g}"] = None; row[f"bars_held_{g}"] = None
                continue
            xb, pnl = v
            risk = geoms[g][0] * a
            row[f"pnl_pips_{g}"] = round(pnl, 4)
            row[f"pnl_R_{g}"] = (round(pnl / risk, 4) if risk > 0 else None)
            row[f"win_{g}"] = int(pnl > 0)
            row[f"bars_held_{g}"] = int(xb - (i + 1))
            xb_max = max(xb_max, xb)
        row["ts_exit"] = str(ts[min(xb_max, n - 1)])         # mwisho wa label (kwa purge/embargo)
        row.update(_ctx_feats(ctx, i))
        rows.append(row)
    return rows, None


def build(out_root=REPO_ROOT, pairs=None, write=True, n_folds=N_FOLDS, verbose=True):
    """Jenga dataset kamili: pairs 12 × bars zote × dirs 2, TRAIN PEKEE, + fold za purged-CV."""
    pairs = pairs or _pairs()
    outdir = Path(out_root) / OUT_DIR
    if write:
        outdir.mkdir(parents=True, exist_ok=True)
    per_pair, notes, t0_all, t1_all = [], [], [], []
    for pair in pairs:
        rows, note = build_pair(pair)
        if note:
            notes.append(note)
            if verbose:
                print(f"  {pair}: {note}", flush=True)
            continue
        per_pair.append((pair, rows))
        for r in rows:                      # mpangilio ULE ULE utakaotumika kwa fold assignment
            t0_all.append(np.datetime64(r["ts_entry"])); t1_all.append(np.datetime64(r["ts_exit"]))
        if verbose:
            print(f"  {pair}: rows {len(rows):,}", flush=True)
    if not per_pair:
        raise RuntimeError("hakuna pair yenye data — dataset haiwezi kujengwa")

    t0 = np.array(t0_all); t1 = np.array(t1_all)
    folds = purged_folds(t0, t1, n_folds=n_folds)
    fold_of = np.full(len(t0), -1, dtype=int)
    for k, (_tr, te) in enumerate(folds):
        fold_of[te] = k
    pos = 0
    for pair, rows in per_pair:
        for r in rows:
            r["fold"] = int(fold_of[pos]); pos += 1

    summary = dict(pairs=[p for p, _ in per_pair], n_rows=int(len(t0)), notes=notes,
                   n_folds=n_folds, stride=STRIDE, max_hold=MAX_HOLD, tf=TF, split=SPLIT,
                   geoms={g: list(v) for g, v in GEOMS.items()},
                   features=FEATURES, outcomes=OUTCOMES, meta=META,
                   folds=fold_report(t0, t1, folds),
                   per_pair={p: len(r) for p, r in per_pair},
                   label_balance={g: _balance(per_pair, g) for g in GEOMS},
                   nan_share=_nan_share(per_pair))
    if write:
        _write_outputs(per_pair, summary, out_root)
    return summary


def _balance(per_pair, geom):
    """win-rate + EV_R kwa label set (accounting; inaonyesha kama bwawa ni heterogeneous — spec §2)."""
    w = [r[f"win_{geom}"] for _p, rows in per_pair for r in rows if r.get(f"win_{geom}") is not None]
    er = [r[f"pnl_R_{geom}"] for _p, rows in per_pair for r in rows if r.get(f"pnl_R_{geom}") is not None]
    return dict(n=len(w), win_rate=(round(float(np.mean(w)), 4) if w else None),
                ev_R=(round(float(np.mean(er)), 4) if er else None))


def _nan_share(per_pair, feats=None):
    feats = feats or FEATURES
    tot = sum(len(r) for _p, r in per_pair) or 1
    out = {}
    for f in feats:
        miss = sum(1 for _p, rows in per_pair for r in rows if r.get(f) is None)
        out[f] = round(miss / tot, 4)
    return out


def _write_outputs(per_pair, s, out_root):
    import polars as pl
    out_root = Path(out_root)
    outdir = out_root / OUT_DIR; outdir.mkdir(parents=True, exist_ok=True)
    for pair, rows in per_pair:
        pl.DataFrame(rows, infer_schema_length=None).write_parquet(outdir / f"{pair}.parquet")
    (outdir / OUT_MANIFEST).write_text(json.dumps(s, indent=1, sort_keys=True), encoding="utf-8")

    L = [f"# M4-1 — DATASET ya KAIROS-3 ({TF}, bars ZOTE × dirs 2 × pairs {len(s['pairs'])}, TRAIN PEKEE)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | charter: docs/CYCLE4_ML_CHARTER.md §6.2/§3/§4 · spec: "
         f"docs/KAIROS_3_SPEC.md §3 | labels: `episodes` (golden, next-bar fill, tie→SL, gharama "
         f"halisi) | entry = MARKET open ya bar i+1, slippage {SLIP_MARKET} pip | max_hold={MAX_HOLD}*\n",
         "> **TRAIN PEKEE (2016-2022).** VALIDATION ni ya gate ya M4-2; HOLDOUT + sealed 2026-05+ "
         "hazipo kwenye njia hii (guard mbili: split-guard + assert ya `max(ts) < TRAIN_END`).\n",
         "> **HAKUNA labeler mpya.** Labels za bars ZOTE zinatoka `episodes()` ile ile ya golden "
         f"kupitia **residue-class scan** (stride = max_hold + 2 = {STRIDE}) — non-overlap ya "
         "episodes hairuki bar hata moja kwa ujenzi. Self-test [2] inathibitisha parity dhidi ya "
         "episodes iliyoitwa bar-moja-moja.\n"]

    L.append(f"\n## Ukubwa\n")
    L.append(f"- rows: **{s['n_rows']:,}** · pairs {len(s['pairs'])} · dirs 2 · geometries "
             f"{list(s['geoms'])} (label sets, si rows tofauti)")
    L.append(f"- per-pair: `{s['per_pair']}`")
    if s["notes"]:
        L.append(f"- pairs zilizorukwa: `{s['notes']}`")
    L.append(f"- faili: `{OUT_DIR}/<pair>.parquet` + `{OUT_MANIFEST}` "
             f"(**nje ya git** — data nzito; ripoti hii ndiyo rekodi)")

    L.append("\n## Manifest (mpaka rasmi — M4-2 ita-assert)\n")
    L.append(f"- **FEATURES** ({len(s['features'])}, zote za SIGNAL bar i — decidable): "
             f"`{', '.join(s['features'])}`")
    L.append(f"- **OUTCOMES** ({len(s['outcomes'])}, KAMWE ndani ya X): `{', '.join(s['outcomes'])}`")
    L.append(f"- **META**: `{', '.join(s['meta'])}`")
    L.append("- `load_k3()` ina-assert: hakuna outcome ndani ya X (leak #1).")

    L.append("\n## Label balance (bwawa ni heterogeneous? — spec §2)\n")
    L.append("| geometry | N | win-rate | EV_R (gross ya bwawa lote) |")
    L.append("|---|---|---|---|")
    for g, b in s["label_balance"].items():
        L.append(f"| {g} ({GEOMS[g][0]}/{GEOMS[g][1]}) | {b['n']:,} | "
                 f"{'—' if b['win_rate'] is None else format(100 * b['win_rate'], '.1f')}% | "
                 f"{'—' if b['ev_R'] is None else format(b['ev_R'], '+.4f')} |")
    L.append("\n*EV_R hapa ni ya **bwawa lote bila uteuzi** (kila bar, pande zote mbili) — inatarajiwa "
             "kuwa HASI (gharama kila bar). Kazi ya GBM ni kupata **subset** yenye EV chanya; kama "
             "bwawa lote lina EV hasi kubwa, threshold italazimika kuwa kali (§4.4 cost-aware).*")

    L.append(f"\n## Purged + embargoed CV (charter §4.2 — `purged_cv.py`)\n")
    L.append(f"- folds {s['n_folds']} za **MUDA** (mpaka mmoja kwa pairs zote — cross-pair leakage "
             f"haiwezekani) · embargo = horizon ya juu ya label")
    L.append("\n| fold | n_train | n_test | n_dropped (purge+embargo) | drop% | test_start | test_end |")
    L.append("|---|---|---|---|---|---|---|")
    for f in s["folds"]:
        L.append(f"| {f['fold']} | {f['n_train']:,} | {f['n_test']:,} | {f['n_dropped']:,} | "
                 f"{100 * f['drop_share']:.2f}% | {f['test_start']} | {f['test_end']} |")

    L.append("\n## Feature completeness (NaN% — pengo kubwa = haifundishwi)\n")
    L.append("| feature | NaN% |")
    L.append("|---|---|")
    for f, v in sorted(s["nan_share"].items(), key=lambda kv: -kv[1]):
        L.append(f"| {f} | {100 * v:.1f}% |")

    L.append("\n## Caveats\n")
    L.append("1. **Dataset si edge.** Ni chakula cha M4-2 pekee; hakuna madai ya EV hapa.")
    L.append("2. **Gharama zimo ndani ya kila label** (spread ya bar ya entry + slippage, L-039). "
             "Bwawa lote lina EV hasi kwa ujenzi — hiyo ndiyo hoja ya threshold ya cost-aware.")
    L.append("3. **Overlap ya labels ni kubwa** (kila bar ina label yenye horizon hadi max_hold) — "
             "ndiyo maana purge+embargo ni LAZIMA, si mapambo. Bila hiyo, CV yoyote ni ya uongo.")
    L.append("4. **dirs 2 kwa kila bar:** long na short zinapimwa kwa uhuru; model itajifunza "
             "P(win | features, dir). Hii ni signal GENERATION (charter §2), si filtering ya nr7.")
    L.append("5. `nr7_flag` ipo ili M4-2 iweze kulinganisha ML dhidi ya breadth baseline **ndani ya "
             "dataset ile ile** (si kuchanganya vyanzo viwili).")
    L.append("\n*reuse-only: episodes/_mask_context-free path/_atr_rel/_extra_states/_ctx_feats/_sess "
             "ni imports. Profitable != Tradable Edge. Protect capital first.*")

    rpt = out_root / "reports" / OUT_REPORT; rpt.parent.mkdir(parents=True, exist_ok=True)
    rpt.write_text("\n".join(L), encoding="utf-8")
    return outdir, rpt


# ---------- self-test ----------
def _fixture(seed, n=1500, start="2016-03-01T00"):
    from event_library_v2 import _synthetic
    o, h, l_, c, tc, hour = _synthetic(n=n, seed=seed)
    atr = np.maximum(h - l_, 0.1)
    ts = np.datetime64(start) + np.arange(n) * np.timedelta64(1, "h")
    hr = (ts.astype("datetime64[h]").astype(np.int64) % 24).astype(int)
    vol = np.array(["LOW", "NORMAL", "HIGH"])[np.arange(n) % 3]
    return dict(o=o, h=h, l=l_, c=c, atr=atr, spr=np.full(n, 1.0), tc=tc, hour=hr,
                vol=vol, ts=ts, days=n // 24, ctx=None)


def self_test():
    ok = True
    import tempfile
    _self = sys.modules[__name__]

    # ---- [1] GUARD: split yoyote isiyo train -> PermissionError KABLA ya data
    guards = {}
    for bad in ("validation", "holdout", "sealed"):
        try:
            build_pair("EURUSD", bad)
            guards[bad] = False
        except PermissionError:
            guards[bad] = True
    ok = ok and all(guards.values())
    print(f"  [1] TRAIN-only guard: {guards} -> {all(guards.values())}")

    # ---- [2] PARITY (RED LINE): residue-scan == episodes iliyoitwa BAR-MOJA-MOJA, na coverage kamili
    fx = _fixture(11, n=900)
    lab = label_bars(fx, 2.0, 1.0)
    n = len(fx["c"])
    mismatch, checked = 0, 0
    for i in range(0, n - 1, 37):                       # sampuli ya bars (moja-moja = ghali)
        for d in DIRS:
            sig = np.zeros(n, dtype=int); sig[i] = d
            trs = episodes({"sig": sig}, "market", fx["o"], fx["h"], fx["l"], fx["c"],
                           fx["atr"], fx["spr"], fx["hour"], fx["vol"], sl_atr=2.0, tp_atr=1.0)
            one = (int(trs[0][1]), float(trs[0][3])) if trs else None
            got = lab.get((i, d))
            checked += 1
            if one != got:
                mismatch += 1
    cov = sum(1 for i in range(n - 1) if fx["atr"][i] > 0 for d in DIRS if (i, d) in lab)
    expect = sum(1 for i in range(n - 1) if fx["atr"][i] > 0) * len(DIRS)
    t2 = mismatch == 0 and checked > 40 and cov == expect
    ok = ok and t2
    print(f"  [2] PARITY residue-scan vs episodes bar-moja-moja: mismatch {mismatch}/{checked} · "
          f"coverage {cov}/{expect} (bars zote × dirs 2) -> {t2}")

    # ---- [3] gharama halisi (L-039): spread juu -> pnl chini kwa EXACTLY Δspread kwa kila label
    fx0 = dict(fx, spr=np.zeros(n)); fx2 = dict(fx, spr=np.full(n, 2.0))
    l0 = label_bars(fx0, 2.0, 1.0); l2 = label_bars(fx2, 2.0, 1.0)
    diffs = [round(l0[k][1] - l2[k][1], 9) for k in l0 if k in l2]
    t3 = len(diffs) > 100 and all(abs(x - 2.0) < 1e-9 for x in diffs)
    ok = ok and t3
    print(f"  [3] L-039 costs kwenye kila label: Δpnl == Δspread (2.0) kwa labels {len(diffs)} -> {t3}")

    # ---- [4] build_pair kamili + manifest + hakuna outcome ndani ya FEATURES
    fxs = {p: _fixture(20 + k, n=1200) for k, p in enumerate(["EURUSD", "GBPUSD", "USDJPY"])}
    orig_lw, orig_ext = _self.load_window, _self._extra_states
    _self.load_window = lambda sym, tf, split, token=None: fxs.get(sym)
    _self._extra_states = lambda pair, split: dict(
        ts=fxs[pair]["ts"], activity_state=np.array(["NORMAL"] * len(fxs[pair]["ts"])),
        spread_state=np.array(["WIDE" if i % 5 == 0 else "NORMAL" for i in range(len(fxs[pair]["ts"]))]),
        dow=(fxs[pair]["ts"].astype("datetime64[D]").astype(int) % 7))
    try:
        rows, note = build_pair("EURUSD")
        leak = set(FEATURES) & set(OUTCOMES)
        has_all = all(k in rows[0] for k in ("win_sl2tp1", "win_sl1tp1", "ts_exit", "nr7_flag"))
        dirs_ok = {r["dir"] for r in rows} == {1, -1}
        t4 = note is None and len(rows) > 1000 and not leak and has_all and dirs_ok
        ok = ok and t4
        print(f"  [4] build_pair: rows {len(rows):,} · dirs {sorted({r['dir'] for r in rows})} · "
              f"manifest leak={bool(leak)} · columns za geometries zote -> {t4}")

        # ---- [5] build kamili + folds + determinism + outputs
        with tempfile.TemporaryDirectory() as tmp:
            sa = build(out_root=tmp, pairs=list(fxs), verbose=False)
            sb = build(out_root=tmp, pairs=list(fxs), write=False, verbose=False)
            det = json.dumps(sa, sort_keys=True) == json.dumps(sb, sort_keys=True)
            rpt = (Path(tmp) / "reports" / OUT_REPORT).read_text(encoding="utf-8")
            files = sorted(x.name for x in (Path(tmp) / OUT_DIR).iterdir())
            man = json.loads((Path(tmp) / OUT_DIR / OUT_MANIFEST).read_text(encoding="utf-8"))
            folds_ok = (len(sa["folds"]) == N_FOLDS
                        and all(f["n_train"] > 0 and f["n_test"] > 0 for f in sa["folds"])
                        and all(f["n_dropped"] > 0 for f in sa["folds"]))
            t5 = (det and folds_ok and sa["n_rows"] == sum(sa["per_pair"].values())
                  and files == sorted([f"{p}.parquet" for p in fxs] + [OUT_MANIFEST])
                  and man["split"] == "train" and "TRAIN PEKEE" in rpt
                  and "residue-class scan" in rpt and "Manifest" in rpt and "purged" in rpt.lower())
            ok = ok and t5
            print(f"  [5] build: rows {sa['n_rows']:,} · folds {len(sa['folds'])} "
                  f"(drop {[f['n_dropped'] for f in sa['folds']]}) · det={det} · files={files} -> {t5}")

        # ---- [6] CV: hakuna label ya train inayogusa dirisha la test (RED LINE, end-to-end)
        rows_all = []
        for p in fxs:
            r, _ = build_pair(p)
            rows_all.extend(r)
        t0 = np.array([np.datetime64(r["ts_entry"]) for r in rows_all])
        t1 = np.array([np.datetime64(r["ts_exit"]) for r in rows_all])
        fol = purged_folds(t0, t1, N_FOLDS)
        t6 = True
        for tr, te in fol:
            a, b = t0[te].min(), t0[te].max()
            t6 = t6 and not ((t0[tr] <= b) & (t1[tr] >= a)).any()
        ok = ok and t6
        print(f"  [6] purged-CV end-to-end (rows {len(rows_all):,}): hakuna train-label inayogusa "
              f"test-window -> {t6}")
    finally:
        _self.load_window, _self._extra_states = orig_lw, orig_ext

    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true", help="jenga dataset (PC ya data; dakika kadhaa)")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.build:
        print("Tumia --build | --self-test.", file=sys.stderr)
        return 2
    s = build()
    print(f"M4-1 DATASET: rows {s['n_rows']:,} · pairs {len(s['pairs'])} · folds {s['n_folds']}")
    for g, b in s["label_balance"].items():
        print(f"  {g}: N={b['n']:,} win={b['win_rate']} EV_R={b['ev_R']}")
    print(f"  {OUT_DIR}/<pair>.parquet (nje ya git)\n  reports/{OUT_REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
