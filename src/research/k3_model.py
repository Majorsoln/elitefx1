"""
k3_model.py — M4-2: GBM ya KAIROS-3 v1.0 (charter §6.3; **docs/M4_2_REGISTRATION.md = SPEC**).

Vigezo vya kupita vimesajiliwa **KABLA ya model yoyote** (charter §4.6) — `docs/M4_2_REGISTRATION.md`
§3. Hakuna kigezo kinachobadilishwa hapa; module hii inapima tu na kuripoti kwa uaminifu.

## Utaratibu (umefungwa §4 ya registration)
1. Data = M4-1 (`data/processed/k3/*.parquet`) — **TRAIN PEKEE 2016-2022**, bars zote × dirs 2 × pairs 12.
2. **Purged + embargoed CV** (`purged_cv.purged_folds`, folds 5 za MUDA) -> predictions za
   **out-of-fold PEKEE**. Hakuna in-sample prediction inayoingia kwenye sweep.
3. **Threshold sweep kwa EV_R** (SI accuracy/AUC) juu ya OOF: quantiles za uteuzi (top-q) ->
   EV_R, trades/mwaka, win%, p_boot, na uthabiti kwenye folds.
4. Matokeo yanapimwa dhidi ya §3 ya registration: EV_R > breadth NA trades/mwaka >= floor NA
   p_boot < 0.05 NA folds >= 4/5. **Ikikosa kimoja -> LESSON** (charter §5).
5. VALIDATION **HAIGUSWI** hapa (ni eval MOJA baada ya freeze); HOLDOUT/sealed hazipo kabisa.

## Maamuzi ya kiufundi (uaminifu wa artifact — charter §4.5/§4.7)
- Trainer = **LightGBM**; artifact = **JSON tree dump** (hakuna pickle).
- **Inference = pure-numpy** (`score_json`) juu ya JSON hiyo — live/paper HAZITEGEMEI framework
  (mwendelezo wa msimamo wa k4_model). Self-test [3] inathibitisha scorer yetu == LightGBM (1e-9).
- Ili scorer iwe EXACT na auditable: categoricals -> **integer codes** (vocab imefungwa ndani ya
  artifact) zinazotendewa kama numeric; NaN -> **sentinel -999.0** na `use_missing=False`. Kwa hiyo
  kila node ni `x[f] <= threshold` — hakuna missing-logic wala categorical-bitset ndani ya scorer.

Endesha (PC ya data): python k3_model.py --cv        (CV + sweep + ripoti; TRAIN pekee)
Self-test (bila data): python k3_model.py --self-test
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

from strategy_lab import pvalue_boot
from purged_cv import purged_folds
from k3_dataset import FEATURES, OUTCOMES, GEOMS, OUT_DIR, load_k3
from breadth_baseline import DAYS_PER_YEAR

REPO_ROOT = Path(__file__).resolve().parents[2]

# ---------- vigezo VILIVYOSAJILIWA (docs/M4_2_REGISTRATION.md §3 — HAVIBADILIKI hapa) ----------
BREADTH_EV_R = {"sl2tp1": 0.0328, "sl1tp1": 0.0526}        # M4-0 pooled VALIDATION
TRADES_FLOOR = {"sl2tp1": 854, "sl1tp1": 890}              # 2× nr7-pairs-2 (charter §5)
ALPHA = 0.05
MIN_FOLDS_PASS = 4                                          # kati ya N_FOLDS
N_FOLDS = 5
QUANTILES = (0.20, 0.10, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001)   # top-q ya bwawa (uteuzi)

# ---------- LightGBM params (zimefungwa kabla ya CV; deterministic) ----------
SEED = 20260801
PARAMS = dict(objective="binary", learning_rate=0.05, num_leaves=31, min_data_in_leaf=500,
              feature_fraction=0.8, bagging_fraction=0.8, bagging_freq=1, lambda_l2=1.0,
              max_bin=255, num_boost_round=300, seed=SEED, deterministic=True,
              force_row_wise=True, use_missing=False, zero_as_missing=False, verbose=-1)
SENTINEL = -999.0                                           # NaN -> sentinel (scorer exact)
B_BOOT = 10_000
MAX_BOOT_CELLS = 2e7

OUT_REPORT = "k3_model_cv.md"
OUT_ARTIFACT = "models/kairos3_gbm_v1_{geom}.json"          # tree dump + vocab + threshold


# ---------- encoding (vocab imefungwa ndani ya artifact) ----------
def build_vocab(df, feats):
    """Vocab ya deterministic kwa columns za string: {feature: [thamani zilizopangwa]}."""
    import polars as pl
    vocab = {}
    for f in feats:
        if f in df.columns and df.schema[f] in (pl.Utf8, pl.Categorical):
            vals = sorted(set(v for v in df[f].to_list() if v is not None))
            vocab[f] = vals
    return vocab


def encode(df, feats, vocab):
    """DataFrame -> matrix ya float32 (codes za categorical + numeric), NaN -> SENTINEL."""
    n = df.height
    X = np.full((n, len(feats)), SENTINEL, dtype=np.float32)
    for j, f in enumerate(feats):
        if f not in df.columns:
            continue
        if f in vocab:
            idx = {v: k for k, v in enumerate(vocab[f])}
            X[:, j] = np.array([idx.get(v, -1) if v is not None else SENTINEL
                                for v in df[f].to_list()], dtype=np.float32)
        else:
            col = df[f].cast(float).to_numpy().astype(np.float32)
            X[:, j] = np.where(np.isfinite(col), col, SENTINEL)
    return X


# ---------- pure-numpy scorer (inference bila framework) ----------
def _walk(node, x):
    while "split_index" in node:
        node = (node["left_child"] if x[node["split_feature"]] <= node["threshold"]
                else node["right_child"])
    return node["leaf_value"]


def score_json(artifact, X):
    """P(win) kwa pure-numpy kutoka JSON tree dump ya LightGBM. Inatumia `<=` PEKEE (hakuna
    missing/categorical logic — angalia §Maamuzi). Rudisha probabilities.
    MATUMIZI: inference ya LIVE (rows chache kwa bar) na uthibitisho wa parity. **SI ya batch
    kubwa** — ni loop ya Python kwa kila (mti × row); kwa CV/training tumia `booster.predict`."""
    trees = artifact["model"]["tree_info"]
    raw = np.zeros(len(X), dtype=float)
    for t in trees:
        st = t["tree_structure"]
        if "split_index" not in st:                       # mti wa jani moja
            raw += st.get("leaf_value", 0.0)
            continue
        for i in range(len(X)):
            raw[i] += _walk(st, X[i])
    return 1.0 / (1.0 + np.exp(-raw))


# ---------- accounting (hakuna statistic mpya) ----------
def _boot_B(n, B=B_BOOT):
    if n < 2:
        return int(B)
    return int(min(int(B), max(1000, int(MAX_BOOT_CELLS // max(n, 1)))))


def subset_stats(pnl_R, ts, seed=SEED):
    """EV_R, N, win%, trades/mwaka, p_boot kwa subset (pooled — L-041)."""
    n = len(pnl_R)
    if n == 0:
        return dict(n=0, ev_R=None, win=None, trades_per_year=None, p_boot=1.0)
    order = np.argsort(ts)                                 # mfuatano wa muda kwa block bootstrap
    r = np.asarray(pnl_R, float)[order]
    years = float((ts.max() - ts.min()) / np.timedelta64(1, "D") / DAYS_PER_YEAR)
    p = (round(float(pvalue_boot(r, B=_boot_B(n), mean_block=3, seed=seed)), 6) if n >= 2 else 1.0)
    return dict(n=int(n), ev_R=round(float(r.mean()), 5), win=round(float((r > 0).mean()), 4),
                trades_per_year=(round(n / years, 1) if years > 0 else None), p_boot=p)


# ---------- CV + sweep ----------
def run_cv(geom="sl1tp1", data_dir=None, out_root=REPO_ROOT, n_folds=N_FOLDS, write=True,
           params=None, quantiles=QUANTILES, verbose=True):
    """Purged-CV -> OOF predictions -> threshold sweep kwa EV_R -> tathmini dhidi ya registration §3."""
    import polars as pl
    import lightgbm as lgb

    p = Path(data_dir) if data_dir else (Path(out_root) / OUT_DIR)
    df = pl.read_parquet(str(p / "*.parquet"))
    if "split" in df.columns and set(df["split"].unique().to_list()) != {"train"}:
        raise PermissionError("M4-2 ni TRAIN PEKEE — dataset ina split nyingine (registration §4.5)")
    feats = [f for f in FEATURES if f in df.columns]
    leak = set(feats) & set(OUTCOMES)
    assert not leak, f"K3 LEAK: {sorted(leak)} ndani ya X"
    ycol, rcol = f"win_{geom}", f"pnl_R_{geom}"
    df = df.filter(pl.col(ycol).is_not_null() & pl.col(rcol).is_not_null())

    vocab = build_vocab(df, feats)
    X = encode(df, feats, vocab)
    y = df[ycol].cast(int).to_numpy()
    pnl_R = df[rcol].cast(float).to_numpy()
    # numpy inaparse ISO ya kila umbo (sekunde/microsecond) — polars inahitaji format moja
    t0 = np.asarray(df["ts_entry"].to_list(), dtype="datetime64[s]")
    t1 = np.asarray(df["ts_exit"].to_list(), dtype="datetime64[s]")

    folds = purged_folds(t0, t1, n_folds=n_folds)
    oof = np.full(len(y), np.nan)
    fold_of = np.full(len(y), -1, dtype=int)
    pr = dict(params or PARAMS)
    rounds = pr.pop("num_boost_round", 300)
    for k, (tr, te) in enumerate(folds):
        ds = lgb.Dataset(X[tr], label=y[tr], feature_name=feats, free_raw_data=False)
        booster = lgb.train(pr, ds, num_boost_round=rounds)
        oof[te] = booster.predict(X[te])
        fold_of[te] = k
        if verbose:
            print(f"  fold {k}: train {len(tr):,} test {len(te):,}", flush=True)

    have = np.isfinite(oof)
    rows = []
    for q in quantiles:
        thr = float(np.quantile(oof[have], 1 - q))
        sel = have & (oof >= thr)
        st = subset_stats(pnl_R[sel], t0[sel])
        per_fold = {}
        for k in range(n_folds):
            m = sel & (fold_of == k)
            per_fold[k] = (round(float(pnl_R[m].mean()), 5) if m.sum() else None)
        folds_pass = sum(1 for v in per_fold.values() if v is not None and v > BREADTH_EV_R[geom])
        rows.append(dict(q=q, threshold=round(thr, 6), **st, per_fold=per_fold,
                         folds_pass=folds_pass))

    # ---- tathmini dhidi ya registration §3 (HAKUNA kigezo kipya)
    verdict_rows = []
    for r in rows:
        c1 = r["ev_R"] is not None and r["ev_R"] > BREADTH_EV_R[geom]
        c2 = r["trades_per_year"] is not None and r["trades_per_year"] >= TRADES_FLOOR[geom]
        c3 = r["p_boot"] < ALPHA
        c4 = r["folds_pass"] >= MIN_FOLDS_PASS
        verdict_rows.append(dict(r, c1_ev=c1, c2_trades=c2, c3_p=c3, c4_folds=c4,
                                 passes=bool(c1 and c2 and c3 and c4)))
    passing = [r for r in verdict_rows if r["passes"]]
    best = max(passing, key=lambda r: r["ev_R"]) if passing else None
    verdict = "PASS" if best else "LESSON"

    # ---- baseline ya ndani: nr7_flag-only subset (uwazi — je ML inazidi breadth iliyofichwa?)
    nr7 = None
    if "nr7_flag" in df.columns:
        m = have & (df["nr7_flag"].cast(int).to_numpy() == 1)
        nr7 = subset_stats(pnl_R[m], t0[m])

    res = dict(geom=geom, n_rows=int(len(y)), n_features=len(feats), features=feats,
               folds=n_folds, params={**pr, "num_boost_round": rounds}, sweep=verdict_rows,
               verdict=verdict, best=best, nr7_only=nr7,
               registration=dict(breadth_ev_R=BREADTH_EV_R[geom], trades_floor=TRADES_FLOOR[geom],
                                 alpha=ALPHA, min_folds=MIN_FOLDS_PASS),
               pool=dict(n=int(len(y)), ev_R=round(float(pnl_R.mean()), 5),
                         win=round(float(y.mean()), 4)))
    if write:
        _write_outputs(res, out_root)
    return res


def _write_outputs(res, out_root):
    out_root = Path(out_root)
    g = res["geom"]
    L = [f"# M4-2 — GBM CV + threshold sweep ({g}) — **{res['verdict']}**\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | spec: docs/M4_2_REGISTRATION.md (§3 vigezo VILIVYOSAJILIWA "
         f"kabla ya model) | data: M4-1 TRAIN PEKEE, rows {res['n_rows']:,} | purged+embargoed CV "
         f"folds {res['folds']} | OOF predictions PEKEE | metric = EV_R (SI accuracy/AUC)*\n",
         f"> **Bwawa bila uteuzi:** N={res['pool']['n']:,} · win={100*res['pool']['win']:.2f}% · "
         f"EV_R={res['pool']['ev_R']:+.4f}\n",
         f"> **Vigezo (§3):** EV_R > **{res['registration']['breadth_ev_R']:+.4f}** (breadth VALID) NA "
         f"trades/mwaka ≥ **{res['registration']['trades_floor']}** NA p_boot < {ALPHA} NA "
         f"folds ≥ {MIN_FOLDS_PASS}/{res['folds']}\n"]
    if res["nr7_only"] and res["nr7_only"]["n"]:
        n7 = res["nr7_only"]
        L.append(f"> **Baseline ya ndani (nr7_flag-only, bila ML):** N={n7['n']:,} · "
                 f"EV_R={n7['ev_R']:+.4f} · trades/mwaka={n7['trades_per_year']} — ML lazima izidi "
                 f"hii pia, si bwawa lote tu.\n")

    L.append("\n## Threshold sweep (OOF)\n")
    L.append("| top-q | threshold P(win) | N | EV_R | win% | trades/mwaka | p_boot | folds>breadth | "
             "c1 EV | c2 N/yr | c3 p | c4 folds | **PASS** |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in res["sweep"]:
        L.append(f"| {r['q']:.3%} | {r['threshold']:.4f} | {r['n']:,} | "
                 f"{'—' if r['ev_R'] is None else format(r['ev_R'], '+.5f')} | "
                 f"{'—' if r['win'] is None else format(100 * r['win'], '.1f')} | "
                 f"{r['trades_per_year']} | {r['p_boot']} | {r['folds_pass']}/{res['folds']} | "
                 f"{'✓' if r['c1_ev'] else '✗'} | {'✓' if r['c2_trades'] else '✗'} | "
                 f"{'✓' if r['c3_p'] else '✗'} | {'✓' if r['c4_folds'] else '✗'} | "
                 f"{'**PASS**' if r['passes'] else '—'} |")

    L.append("\n## Per-fold EV_R (uthabiti — anti-cherry-picking)\n")
    L.append("| top-q | " + " | ".join(f"fold {k}" for k in range(res["folds"])) + " |")
    L.append("|---|" + "---|" * res["folds"])
    for r in res["sweep"]:
        L.append(f"| {r['q']:.3%} | " + " | ".join(
            ("—" if r["per_fold"][k] is None else format(r["per_fold"][k], "+.4f"))
            for k in range(res["folds"])) + " |")

    L.append(f"\n## VERDICT: **{res['verdict']}**\n")
    if res["best"]:
        b = res["best"]
        L.append(f"Threshold iliyopita yenye EV_R kubwa: **top-{b['q']:.3%}** (P ≥ {b['threshold']:.4f}) "
                 f"-> EV_R **{b['ev_R']:+.5f}** · N={b['n']:,} · trades/mwaka **{b['trades_per_year']}** "
                 f"· p_boot {b['p_boot']} · folds {b['folds_pass']}/{res['folds']}.")
        L.append("\n-> Hatua inayofuata (registration §4.3): **FREEZE** (hyperparams + threshold "
                 "kwenye commit) KISHA eval MOJA ya VALIDATION. Hakuna re-sweep baada ya freeze.")
    else:
        L.append("Hakuna threshold iliyotimiza vigezo VYOTE vinne vya §3. Kwa mujibu wa charter §5, "
                 "hii ni **LESSON** — na **HATUA 2 (LSTM) HAIANZI**.")
        L.append("\nKilichoshindikana kwa kila threshold kimeandikwa kwenye safu c1-c4 hapo juu "
                 "(uwazi: si 'karibu kufaulu' — ni kigezo gani hasa).")

    L.append("\n## Caveats\n")
    L.append("1. **CV ndani ya TRAIN pekee.** Hakuna madai ya OOS hapa; VALIDATION haijaguswa.")
    L.append("2. **OOF PEKEE** kwenye sweep — hakuna in-sample prediction inayoingia kwenye namba.")
    L.append("3. **Purge + embargo** zimetumika (labels zinapishana hadi max_hold). Bila hizo, EV yoyote "
             "ya CV ingekuwa ya uongo.")
    L.append("4. Threshold sweep juu ya OOF ni **uteuzi**: EV ya threshold iliyochaguliwa ni hot kidogo. "
             "Ndiyo maana VALIDATION ni eval MOJA baada ya freeze (registration §4.3-§4.4).")
    L.append("5. Artifact = JSON tree dump; inference = pure-numpy (`score_json`) — live haitegemei "
             "LightGBM. Self-test [3] inathibitisha parity.")
    L.append("\n*Profitable != Tradable Edge. Protect capital first.*")

    rpt = out_root / "reports" / OUT_REPORT.replace(".md", f"_{g}.md")
    rpt.parent.mkdir(parents=True, exist_ok=True)
    rpt.write_text("\n".join(L), encoding="utf-8")
    return rpt


# ---------- self-test ----------
def self_test():
    ok = True
    import tempfile
    import lightgbm as lgb
    import polars as pl

    rng = np.random.default_rng(7)
    n = 4000
    # dataset bandia yenye SIGNAL halisi: feature f0 inaamua P(win); nyingine ni kelele
    f0 = rng.normal(size=n)
    p_true = 1 / (1 + np.exp(-(1.5 * f0)))
    y = (rng.random(n) < p_true).astype(int)
    ts0 = np.datetime64("2016-01-01T00") + np.arange(n) * np.timedelta64(1, "h")
    ts1 = ts0 + np.timedelta64(5, "h")
    df = pl.DataFrame(dict(dir=rng.choice([1, -1], n), hour=(np.arange(n) % 24),
                           atr_pips=rng.uniform(5, 15, n), atr_rel=f0,
                           range_atr=rng.normal(size=n), nr7_flag=rng.integers(0, 2, n),
                           vol_state=np.array(["LOW", "NORMAL", "HIGH"])[np.arange(n) % 3],
                           activity_state=np.array(["NORMAL"] * n),
                           spread_state=np.array(["NORMAL", "WIDE"])[np.arange(n) % 2],
                           session_entry=np.array(["ASIA", "LONDON", "NY"])[np.arange(n) % 3],
                           dow=(np.arange(n) % 7),
                           win_sl1tp1=y, pnl_R_sl1tp1=np.where(y == 1, 0.9, -1.0),
                           split=np.array(["train"] * n),
                           ts_entry=[str(t) for t in ts0], ts_exit=[str(t) for t in ts1]))

    # [1] GUARD: dataset yenye split isiyo train -> PermissionError
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp) / "k3"; d.mkdir()
        df.with_columns(pl.lit("validation").alias("split")).write_parquet(d / "X.parquet")
        try:
            run_cv("sl1tp1", data_dir=d, out_root=tmp, write=False, verbose=False)
            t1 = False
        except PermissionError:
            t1 = True
    ok = ok and t1
    print(f"  [1] TRAIN-only guard (dataset ya validation -> refuse): {t1}")

    # [2] LEAK assert: outcome ndani ya FEATURES -> AssertionError
    _orig = globals()["FEATURES"]
    try:
        globals()["FEATURES"] = _orig + ["pnl_R_sl1tp1"]
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "k3"; d.mkdir(); df.write_parquet(d / "X.parquet")
            try:
                run_cv("sl1tp1", data_dir=d, out_root=tmp, write=False, verbose=False)
                t2 = False
            except AssertionError:
                t2 = True
    finally:
        globals()["FEATURES"] = _orig
    ok = ok and t2
    print(f"  [2] LEAK assert (outcome ndani ya X -> AssertionError): {t2}")

    # [3] SCORER PARITY (RED LINE ya artifact): pure-numpy == LightGBM (1e-9)
    feats = [f for f in FEATURES if f in df.columns]
    vocab = build_vocab(df, feats)
    X = encode(df, feats, vocab)
    pr = dict(PARAMS); rounds = pr.pop("num_boost_round"); pr["min_data_in_leaf"] = 20
    ds = lgb.Dataset(X, label=y, feature_name=feats, free_raw_data=False)
    booster = lgb.train(pr, ds, num_boost_round=25)
    art = dict(model=booster.dump_model(), vocab=vocab, features=feats, sentinel=SENTINEL)
    sub = X[:300]
    p_lgb = booster.predict(sub)
    p_ours = score_json(art, sub)
    dmax = float(np.abs(p_lgb - p_ours).max())
    t3 = dmax < 1e-9
    ok = ok and t3
    print(f"  [3] scorer parity (pure-numpy vs LightGBM, rows 300): max|Δ| = {dmax:.2e} -> {t3}")

    # [3b] artifact ni JSON safi (hakuna pickle) na inaweza kusomwa tena
    s = json.dumps(art)
    art2 = json.loads(s)
    t3b = float(np.abs(score_json(art2, sub) - p_ours).max()) == 0.0 and len(s) > 1000
    ok = ok and t3b
    print(f"  [3b] artifact JSON round-trip (hakuna pickle): identical={t3b}")

    # [4] CV kamili + vigezo vya registration + determinism
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp) / "k3"; d.mkdir(); df.write_parquet(d / "X.parquet")
        pr2 = dict(PARAMS, min_data_in_leaf=20, num_boost_round=25)
        ra = run_cv("sl1tp1", data_dir=d, out_root=tmp, n_folds=3, params=pr2, verbose=False)
        rb = run_cv("sl1tp1", data_dir=d, out_root=tmp, n_folds=3, params=pr2, write=False,
                    verbose=False)
        det = json.dumps(ra["sweep"], sort_keys=True) == json.dumps(rb["sweep"], sort_keys=True)
        rpt = (Path(tmp) / "reports" / "k3_model_cv_sl1tp1.md").read_text(encoding="utf-8")
        # signal ipo -> EV_R ya top-q lazima izidi ya bwawa (model inachagua kitu halisi)
        top = ra["sweep"][-1]; wide = ra["sweep"][0]
        lift = (top["ev_R"] is not None and wide["ev_R"] is not None
                and top["ev_R"] > wide["ev_R"] > ra["pool"]["ev_R"])
        crit = all(k in ra["registration"] for k in ("breadth_ev_R", "trades_floor", "alpha"))
        t4 = (det and lift and crit and ra["verdict"] in ("PASS", "LESSON")
              and "VERDICT" in rpt and "vigezo VILIVYOSAJILIWA" in rpt
              and all(set(("c1_ev", "c2_trades", "c3_p", "c4_folds")) <= set(r) for r in ra["sweep"]))
    ok = ok and t4
    print(f"  [4] CV+sweep: det={det} · lift (top-q {top['ev_R']:+.4f} > wide {wide['ev_R']:+.4f} > "
          f"pool {ra['pool']['ev_R']:+.4f})={lift} · verdict={ra['verdict']} -> {t4}")

    # [5] OOF PEKEE: kila row iliyotumika kwenye sweep ilitabiriwa na model ISIYOIONA (kwa ujenzi
    # wa purged_folds — hapa tunathibitisha hakuna row ya test iliyokuwa kwenye train ya fold yake)
    fol = purged_folds(np.array([np.datetime64(x) for x in df["ts_entry"].to_list()]),
                       np.array([np.datetime64(x) for x in df["ts_exit"].to_list()]), 3)
    t5 = all(len(np.intersect1d(tr, te)) == 0 for tr, te in fol)
    ok = ok and t5
    print(f"  [5] OOF discipline: train ∩ test = tupu kwenye folds zote -> {t5}")

    # [6] vigezo HAVIJABADILISHWA (mirror ya docs/M4_2_REGISTRATION.md §3)
    t6 = (BREADTH_EV_R == {"sl2tp1": 0.0328, "sl1tp1": 0.0526}
          and TRADES_FLOOR == {"sl2tp1": 854, "sl1tp1": 890}
          and ALPHA == 0.05 and MIN_FOLDS_PASS == 4)
    ok = ok and t6
    print(f"  [6] vigezo vya registration havijabadilika: breadth={BREADTH_EV_R} "
          f"floor={TRADES_FLOOR} α={ALPHA} folds={MIN_FOLDS_PASS} -> {t6}")

    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--cv", action="store_true", help="CV + threshold sweep (TRAIN pekee; PC ya data)")
    ap.add_argument("--geom", default=None, choices=list(GEOMS), help="default: zote mbili")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.cv:
        print("Tumia --cv [--geom sl1tp1|sl2tp1] | --self-test.", file=sys.stderr)
        return 2
    for g in ([a.geom] if a.geom else list(GEOMS)):
        print(f"\n=== M4-2 CV: {g} ===")
        r = run_cv(g)
        print(f"VERDICT ({g}): {r['verdict']}")
        for row in r["sweep"]:
            print(f"  top-{row['q']:.3%}: N={row['n']:,} EV_R={row['ev_R']} "
                  f"trades/yr={row['trades_per_year']} p={row['p_boot']} "
                  f"folds={row['folds_pass']}/{r['folds']} {'PASS' if row['passes'] else ''}")
        print(f"  reports/{OUT_REPORT.replace('.md', f'_{g}.md')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
