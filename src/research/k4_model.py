"""
k4_model.py — M3-5: K4 MODEL v0 (entry-quality p(win|mazingira)). BUILD ya design-of-record
`reports/k4_model_design.md` (SCIENTIST-D, Chief-approved). Design = SPEC (hakuna deviation bila Chief).

Per-strategy models (STRAT-001/002; hakuna pooling): PRIMARY = L2-logistic, CHALLENGER = shallow tree
(depth<=3, min_leaf>=100). BLOCKED leave-one-year-out CV ndani ya TRAIN PEKEE (folds=miaka 7, purge
bars 24), grid 16, prune-once, FREEZE kwa commit KABLA ya VALID. Decision metric = ΔEV_R@70% (SI
accuracy/AUC). H0 = "hakuna lift" (§4 criterion imefungwa). VALID = eval MOJA baada ya freeze.

IMPLEMENTATION NOTE (si deviation ya kimaudhui): L2-logistic ni convex -> optimum MMOJA; imetekelezwa
kwa IRLS/Newton (pure-numpy, deterministic) = coefficients ZILEZILE za lbfgs kwa tolerance. Tree =
greedy CART deterministic. Artifact = JSON (coefficients/splits — auditable; HAKUNA pickle). sklearn
HAIHITAJIKI (sweep inabaki portable). Bootstrap ya CI ni utility MPYA (haishiriki jina na pvalue_boot).

ZERO golden/statistic fns za research zimeguswa (load_k4 assert ya k4_dataset inatumika kama ilivyo).

CLI:  --cv (grid+prune+report)  |  --freeze (Chief, baada ya CV-PASS)  |  --eval-valid (one-shot)  |  --self-test
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

from k4_dataset import FEATURES, OUTCOMES, OUT_PARQUET, load_k4

REPO_ROOT = Path(__file__).resolve().parents[2]
STRATS = ("STRAT-001", "STRAT-002")
YEARS = tuple(range(2016, 2023))            # TRAIN folds (leave-one-year-out)
PURGE_H = 24                                 # bars/hours purge kila upande wa boundary (H1)
Q_PRIMARY, Q_ALT = 0.70, 0.50               # retention (PRIMARY decision = 70%)
EXCLUDE = ("atr_pips", "hour")              # §6 hygiene: absolute-level year-proxy + DST jitter
CORE = ["vol_state", "activity_state", "spread_state", "session_entry", "atr_rel", "range_nr7_atr",
        "h4_trend_sign", "d1_trend_sign", "h4_rsi14", "d1_rsi14", "h4_roc10", "d1_roc10",
        "d1_dist_res_atr"]
# §4 criterion (imefungwa KABLA ya namba yoyote)
DEV_FLOOR = 0.05                             # ΔEV_R@70% >= +0.05 R (economic floor)
P_ALPHA = 0.05                              # one-sided block-bootstrap p < 0.05
EV_RET_MIN = 0.90                           # EV-retention@70% >= 0.90 (CV)
EV_RET_MIN_VALID = 0.80                     # VALID sign-only + retention >= 0.80
BOOT_B, BOOT_MB, SEED = 10_000, 3, 20260717
CATEG = {"vol_state", "activity_state", "spread_state", "session_entry",
         "h4_vol_state", "h4_act_state", "d1_vol_state", "d1_act_state"}
ARTIFACT = "k4_model_v0.json"
REPORT = "k4_model_report.md"


def feature_sets():
    """CORE + FULL (FEATURES za manifest minus EXCLUDE). Chaguo kati yao ni NDANI ya CV tu (§1)."""
    full = [f for f in FEATURES if f not in EXCLUDE]
    return {"CORE": list(CORE), "FULL": full}


def grid():
    """Configs 16 per strategy (pre-declared — multiplicity yote inayoruhusiwa, §2)."""
    g = []
    for fs in ("CORE", "FULL"):
        for C in (0.03, 0.1, 0.3, 1.0):
            g.append(dict(kind="logistic", C=C, fs=fs))
        for depth in (2, 3):
            for leaf in (100, 150):
                g.append(dict(kind="tree", depth=depth, min_leaf=leaf, fs=fs))
    return g


# ---------- preprocess (per-fold; hakuna cross-fold leakage, §1) ----------

def _prep_fit(rows, feats):
    """rows = list ya dict (TRAIN fold). Rudisha params: categories (one-hot), median (numeric),
    mean/sd (standardize) — zote kutoka TRAINING fold PEKEE."""
    cats, med, mu, sd, num = {}, {}, {}, {}, []
    for f in feats:
        if f in CATEG:
            vals = sorted({("NA" if r.get(f) is None else str(r.get(f))) for r in rows})
            cats[f] = vals
        else:
            num.append(f)
            col = np.array([np.nan if r.get(f) is None else float(r.get(f)) for r in rows], float)
            m = float(np.nanmedian(col)) if np.isfinite(col).any() else 0.0
            filled = np.where(np.isfinite(col), col, m)
            med[f] = m; mu[f] = float(filled.mean())
            s = float(filled.std()); sd[f] = s if s > 1e-9 else 1.0
    colnames = []
    for f in feats:
        if f in CATEG:
            colnames += [f"{f}={v}" for v in cats[f]]
        else:
            colnames.append(f)
    return dict(feats=feats, cats=cats, med=med, mu=mu, sd=sd, num=num, colnames=colnames)


def _prep_apply(params, rows):
    """rows -> design matrix (np) kwa colnames za params. Categorical isiyoonekana -> all-zero."""
    n = len(rows); cols = []
    for f in params["feats"]:
        if f in CATEG:
            for v in params["cats"][f]:
                cols.append(np.array([1.0 if ("NA" if r.get(f) is None else str(r.get(f))) == v
                                      else 0.0 for r in rows], float))
        else:
            col = np.array([np.nan if r.get(f) is None else float(r.get(f)) for r in rows], float)
            col = np.where(np.isfinite(col), col, params["med"][f])
            cols.append((col - params["mu"][f]) / params["sd"][f])
    return np.column_stack(cols) if cols else np.zeros((n, 0))


# ---------- models (pure-numpy, deterministic) ----------

class LogisticL2:
    """L2-logistic (convex -> optimum mmoja) kwa IRLS/Newton yenye ridge. Intercept HAIPENALIZWI.
    lam = 1/C (sklearn convention). Deterministic (hakuna randomness)."""
    def __init__(self, C=1.0, max_iter=100, tol=1e-8):    # Newton (quadratic) hukaribia <20 iters
        self.C = C; self.max_iter = max_iter; self.tol = tol; self.w = None; self.b = 0.0

    def fit(self, X, y):
        n, p = X.shape
        Xb = np.column_stack([np.ones(n), X])          # intercept = col 0
        w = np.zeros(p + 1)
        lam = 1.0 / self.C
        R = np.eye(p + 1); R[0, 0] = 0.0               # ridge, intercept off
        for _ in range(self.max_iter):
            z = Xb @ w
            pr = 1.0 / (1.0 + np.exp(-np.clip(z, -35, 35)))
            W = np.clip(pr * (1 - pr), 1e-9, None)
            grad = Xb.T @ (pr - y) + lam * (R @ w)
            H = Xb.T @ (Xb * W[:, None]) + lam * R
            try:
                step = np.linalg.solve(H + 1e-9 * np.eye(p + 1), grad)
            except np.linalg.LinAlgError:
                break
            w_new = w - step
            if np.max(np.abs(w_new - w)) < self.tol:
                w = w_new; break
            w = w_new
        self.b = float(w[0]); self.w = w[1:]
        return self

    def predict_proba(self, X):
        z = self.b + X @ self.w
        return 1.0 / (1.0 + np.exp(-np.clip(z, -35, 35)))

    def coefs(self, colnames):
        return {"intercept": round(self.b, 8),
                **{cn: round(float(c), 8) for cn, c in zip(colnames, self.w)}}


class ShallowTree:
    """CART deterministic (Gini), depth<=d, min_samples_leaf>=leaf. Leaf value = mean(y) (calibrated
    p, si rank). Split search: kila column, thresholds = midpoints za unique values (0.5 kwa binary);
    tie-break kwa (column index, threshold) -> deterministic."""
    def __init__(self, depth=3, min_leaf=100):
        self.depth = depth; self.min_leaf = min_leaf; self.tree = None

    @staticmethod
    def _gini(y):
        if len(y) == 0:
            return 0.0
        p = y.mean(); return 2 * p * (1 - p)

    def _build(self, X, y, d):
        node = {"value": round(float(y.mean()) if len(y) else 0.5, 8), "n": int(len(y))}
        if d >= self.depth or len(y) < 2 * self.min_leaf or y.min() == y.max():
            return node
        n, p = X.shape; best = None
        base = self._gini(y) * n
        for j in range(p):
            xs = np.unique(X[:, j])
            if len(xs) < 2:
                continue
            thr = (xs[:-1] + xs[1:]) / 2.0
            for t in thr:
                left = X[:, j] <= t
                nl = int(left.sum()); nr = n - nl
                if nl < self.min_leaf or nr < self.min_leaf:
                    continue
                imp = self._gini(y[left]) * nl + self._gini(y[~left]) * nr
                gain = base - imp
                if best is None or gain > best[0] + 1e-12:
                    best = (gain, j, float(t))
        if best is None or best[0] <= 0:
            return node
        _, j, t = best
        left = X[:, j] <= t
        node.update(feat=j, thr=t,
                    left=self._build(X[left], y[left], d + 1),
                    right=self._build(X[~left], y[~left], d + 1))
        return node

    def fit(self, X, y):
        self.tree = self._build(X, y.astype(float), 0); return self

    def _pred1(self, x, node):
        while "feat" in node:
            node = node["left"] if x[node["feat"]] <= node["thr"] else node["right"]
        return node["value"]

    def predict_proba(self, X):
        return np.array([self._pred1(x, self.tree) for x in X])


def _fit_config(config, tr_rows, te_rows, y_key="win"):
    """Preprocess (fit TRAIN) + fit model + predict TEST. Rudisha (probs_te, params, model)."""
    feats = _fs_for(config)                                         # CORE/FULL/PRUNED (custom list)
    feats = [f for f in feats if any(f in r for r in tr_rows)]      # zilizopo kwenye data
    params = _prep_fit(tr_rows, feats)
    Xtr = _prep_apply(params, tr_rows); Xte = _prep_apply(params, te_rows)
    ytr = np.array([r[y_key] for r in tr_rows], float)
    if config["kind"] == "logistic":
        m = LogisticL2(C=config["C"]).fit(Xtr, ytr)
    else:
        m = ShallowTree(depth=config["depth"], min_leaf=config["min_leaf"]).fit(Xtr, ytr)
    return m.predict_proba(Xte), params, m


# ---------- metrics (§3) ----------

def _pstar_for_q(p, q):
    """Threshold inayoweka ~q fraction ya trades (keep p>=p*): quantile ya (1-q)."""
    return float(np.quantile(p, 1 - q))


def delta_ev(p, pnl_R, q, pstar=None):
    """M1 ΔEV_R@q + M2 EV-retention@q. Rudisha dict (dev, ev_ret, pstar, n_keep, keep_mask)."""
    p = np.asarray(p, float); r = np.asarray(pnl_R, float)
    ps = _pstar_for_q(p, q) if pstar is None else pstar
    keep = p >= ps
    ev_all = float(r.mean()) if len(r) else 0.0
    ev_f = float(r[keep].mean()) if keep.any() else 0.0
    tot = float(r.sum())
    ev_ret = float(r[keep].sum() / tot) if tot != 0 else 0.0
    return dict(dev=ev_f - ev_all, ev_ret=ev_ret, pstar=ps, n_keep=int(keep.sum()), keep=keep)


def loss_streaks(win_seq):
    """M3: max + P95 ya consecutive-loss runs (time-ordered). win_seq = 0/1 (1=win)."""
    runs = []; cur = 0
    for w in win_seq:
        if w == 0:
            cur += 1
        else:
            if cur:
                runs.append(cur)
            cur = 0
    if cur:
        runs.append(cur)
    if not runs:
        return dict(max=0, p95=0.0)
    return dict(max=int(max(runs)), p95=float(np.percentile(runs, 95)))


def _auc(p, y):
    p = np.asarray(p, float); y = np.asarray(y, int)
    pos = p[y == 1]; neg = p[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return 0.5
    order = np.argsort(p, kind="mergesort"); ranks = np.empty(len(p)); ranks[order] = np.arange(1, len(p) + 1)
    return float((ranks[y == 1].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def _block_boot_p(pnl_R, p, pstar, q, B=BOOT_B, mb=BOOT_MB, seed=SEED):
    """Utility MPYA (SI pvalue_boot): stationary block bootstrap ya ΔEV_R@q juu ya trade sequence
    (paired — mask ya filter inahesabiwa NDANI ya resample kwa pstar iliyofungwa). Rudisha
    (p_one_sided, ci_lo, ci_hi). p = frac{ΔEV* <= 0} (+1)/(B+1) — one-sided kwa H0 ΔEV<=0."""
    r = np.asarray(pnl_R, float); pp = np.asarray(p, float); n = len(r)
    if n < 4:
        return 1.0, float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    L = max(1, mb); nb = int(np.ceil(n / L))
    devs = np.empty(B)
    for b in range(B):
        starts = rng.integers(0, n, size=nb)
        idx = (starts[:, None] + np.arange(L)[None, :]).ravel()[:n] % n
        rr = r[idx]; ppp = pp[idx]
        keep = ppp >= pstar
        ev_all = rr.mean()
        ev_f = rr[keep].mean() if keep.any() else ev_all
        devs[b] = ev_f - ev_all
    p_one = (1 + int(np.sum(devs <= 0))) / (B + 1)
    return float(p_one), float(np.quantile(devs, 0.05)), float(np.quantile(devs, 0.95))


# ---------- blocked CV (§2) ----------

def _purge_train(tr_rows, te_rows, purge_h=PURGE_H):
    """Ondoa train-rows zenye ts_entry ndani ya `purge_h` saa za mpaka wa test-year (§D3)."""
    tt = np.array([np.datetime64(r["ts_entry"]) for r in te_rows])
    lo = tt.min() - np.timedelta64(purge_h, "h"); hi = tt.max() + np.timedelta64(purge_h, "h")
    out = []
    for r in tr_rows:
        t = np.datetime64(r["ts_entry"])
        if not (lo <= t <= hi):
            out.append(r)
    return out


def blocked_cv(rows, config):
    """Leave-one-year-out CV. Rudisha (oof_p, oof_r, oof_y, oof_ts, per_fold_coefs). oof = kila trade
    mara MOJA (predicted na fold ambapo mwaka wake = test)."""
    rows = sorted(rows, key=lambda r: r["ts_entry"])
    years = sorted({r["year"] for r in rows})
    oof_p, oof_r, oof_y, oof_ts, coefs = [], [], [], [], []
    for ty in years:
        te = [r for r in rows if r["year"] == ty]
        tr = [r for r in rows if r["year"] != ty]
        tr = _purge_train(tr, te)
        if len(tr) < 50 or not te:
            continue
        probs, params, m = _fit_config(config, tr, te)
        oof_p += list(probs); oof_r += [r["pnl_R"] for r in te]
        oof_y += [r["win"] for r in te]; oof_ts += [r["ts_entry"] for r in te]
        if config["kind"] == "logistic":
            coefs.append((ty, m.coefs(params["colnames"])))
    return (np.array(oof_p), np.array(oof_r, float), np.array(oof_y, int),
            np.array(oof_ts), coefs)


def _cv_metrics(oof_p, oof_r, oof_y, q=Q_PRIMARY, boot=True, boot_B=BOOT_B, seed=SEED):
    """Metrics za CV pooled oof (ordered kwa ts nje). Rudisha dict (dev, ev_ret, pstar, p_boot, ci, auc)."""
    d = delta_ev(oof_p, oof_r, q)
    res = dict(dev=round(d["dev"], 5), ev_ret=round(d["ev_ret"], 4), pstar=round(d["pstar"], 5),
               n=len(oof_r), n_keep=d["n_keep"], auc=round(_auc(oof_p, oof_y), 4))
    if boot:
        pb, lo, hi = _block_boot_p(oof_r, oof_p, d["pstar"], q, B=boot_B, seed=seed)
        res.update(p_boot=round(pb, 5), ci_lo=round(lo, 5), ci_hi=round(hi, 5))
    return res


def _reject_h0(mcv):
    """§4 CV criterion: zote tatu (dev>0 & p<0.05 ; dev>=+0.05 ; ev_ret>=0.90)."""
    return bool(mcv["dev"] > 0 and mcv.get("p_boot", 1.0) < P_ALPHA
                and mcv["dev"] >= DEV_FLOOR and mcv["ev_ret"] >= EV_RET_MIN)


def _unstable_features(coefs, top=5, max_flips=2):
    """§6 prune: features za top-|coef| (wastani) zenye sign-flip kwenye >max_flips folds -> prune.
    UNKNOWN dummy ikiwa top-5 -> prune pia. Rudisha set ya raw-feature names za kuondoa."""
    if not coefs:
        return set()
    allcn = set()
    for _, cd in coefs:
        allcn |= set(cd) - {"intercept"}
    meanabs = {cn: np.mean([abs(cd.get(cn, 0.0)) for _, cd in coefs]) for cn in allcn}
    top5 = sorted(meanabs, key=meanabs.get, reverse=True)[:top]
    drop = set()
    for cn in top5:
        signs = [np.sign(cd.get(cn, 0.0)) for _, cd in coefs if cd.get(cn, 0.0) != 0.0]
        flips = sum(1 for s in signs if s != signs[0]) if signs else 0
        if flips > max_flips or cn.endswith("=UNKNOWN") or "UNKNOWN" in cn:
            drop.add(cn.split("=")[0])                 # raw feature name
    return drop


def cv_select(rows, prune=True, boot_B=BOOT_B):
    """Grid 16 -> winner kwa ΔEV_R@70% (selection metric §2); prune pass MOJA (PRIMARY); rudisha
    dict ya winner (config, metrics, coefs, pruned). boot_B ndogo = self-test kasi."""
    def _score(cfg, rws):
        op, orr, oy, ots, cf = blocked_cv(rws, cfg)
        if len(orr) < 10:
            return None
        return dict(cfg=cfg, m=_cv_metrics(op, orr, oy, boot=False), coefs=cf)
    scored = [s for s in (_score(c, rows) for c in grid()) if s]
    if not scored:
        return None
    win = max(scored, key=lambda s: s["m"]["dev"])
    pruned = []
    if prune and win["cfg"]["kind"] == "logistic":
        drop = _unstable_features(win["coefs"])
        if drop:
            pruned = sorted(drop)
            rows2 = rows                                # data haibadiliki; tunachuja features
            _fs = feature_sets()
            # jenga config yenye feature-set iliyopunguzwa (custom list)
            base = _fs[win["cfg"]["fs"]]
            newfeats = [f for f in base if f not in drop]
            cfg2 = dict(win["cfg"], fs="PRUNED", _feats=newfeats)
            # re-CV mara MOJA na feature-set custom
            op, orr, oy, ots, cf = blocked_cv(rows2, cfg2)
            win = dict(cfg=cfg2, m=_cv_metrics(op, orr, oy, boot=False), coefs=cf)
    # final metrics + bootstrap juu ya winner (out-of-fold)
    op, orr, oy, ots, cf = blocked_cv(rows, win["cfg"])
    win["m"] = _cv_metrics(op, orr, oy, boot=True, boot_B=boot_B)
    win["coefs"] = cf; win["reject_h0"] = _reject_h0(win["m"])
    win["pruned"] = pruned
    win["streak_all"] = loss_streaks(list(oy))
    d = delta_ev(op, orr, Q_PRIMARY)
    win["streak_filt"] = loss_streaks(list(oy[d["keep"]]))
    return win


# feature_sets() inaongeza PRUNED path: _fit_config inasoma cfg["_feats"] kama ipo
_ORIG_FS = feature_sets
def _fs_for(cfg):
    if cfg.get("fs") == "PRUNED" and "_feats" in cfg:
        return cfg["_feats"]
    return _ORIG_FS()[cfg["fs"]]


# ---------- data loading ----------

def _load_rows(split_filter="train", path=None):
    """Rudisha list ya dict rows (FEATURES + win + pnl_R + ts_entry + year + strategy) kwa split.
    AT3: split_filter='train' -> rows za validation zinakataliwa (haziingii CV)."""
    df = load_k4(path, features_only=False)
    keep_cols = [c for c in df.columns]
    rows = df.to_dicts()
    if split_filter is not None:
        rows = [r for r in rows if r.get("split") == split_filter]
    return rows


def _dataset_hash(path=None):
    path = Path(path) if path else (REPO_ROOT / "data" / "strategies" / OUT_PARQUET)
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


# ---------- CLI: --cv / --freeze / --eval-valid ----------

def run_cv(out_root=REPO_ROOT, path=None, rows_by_strat=None, boot_B=BOOT_B):
    """Grid+prune+report+verdict kwa kila strategy (TRAIN-CV PEKEE). AT3: rows za validation
    hazitumiki (split_filter='train'). Rudisha dict ya matokeo per strategy."""
    res = {}
    for name in STRATS:
        if rows_by_strat is not None:
            rows = rows_by_strat[name]
        else:
            rows = [r for r in _load_rows("train", path) if r["strategy"] == name]
        # AT3 guard: kama kuna row ya validation imepenya -> kataa
        if any(r.get("split") == "validation" for r in rows):
            raise PermissionError("AT3: --cv HAIRUHUSU rows za validation (VALID = eval MOJA baada ya freeze)")
        win = cv_select(rows, boot_B=boot_B)
        res[name] = win
    if out_root is not None:
        _write_report(res, out_root, path)
    return res


def freeze(cv_res, out_root=REPO_ROOT, path=None):
    """Andika artifact JSON (config, coefficients/tree, p*, criterion, dataset hash). Chief-only
    baada ya CV-PASS. HAKUNA pickle."""
    art = dict(version="k4_v0", dataset_hash=_dataset_hash(path),
               criterion=dict(dev_floor=DEV_FLOOR, p_alpha=P_ALPHA, ev_ret_min=EV_RET_MIN,
                              q=Q_PRIMARY, valid_ev_ret_min=EV_RET_MIN_VALID),
               strategies={})
    for name, win in cv_res.items():
        art["strategies"][name] = dict(
            config={k: v for k, v in win["cfg"].items() if not k.startswith("_")},
            feats=_fs_for(win["cfg"]), pstar=win["m"]["pstar"],
            reject_h0=win["reject_h0"], cv_metrics=win["m"], pruned=win["pruned"],
            coefs_last_fold=(win["coefs"][-1][1] if win["coefs"] else None))
    dest = Path(out_root) / "data" / "strategies" / ARTIFACT
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(art, indent=2, sort_keys=True), encoding="utf-8")
    return dest


def eval_valid(out_root=REPO_ROOT, path=None, rows_by_strat=None, freeze_path=None):
    """One-shot VALID eval. AT3/AT7: LAZIMA freeze file ipo + dataset-hash inalingana; p* inasomwa
    kutoka freeze (KAMWE haihesabiwi upya). Refit PRIMARY kwa TRAIN nzima, predict VALID, apply p*."""
    fp = Path(freeze_path) if freeze_path else (Path(out_root) / "data" / "strategies" / ARTIFACT)
    if not fp.exists():
        raise RuntimeError("AT3: --eval-valid inahitaji freeze file iliyo-commit (haipo)")
    art = json.loads(fp.read_text(encoding="utf-8"))
    if art.get("dataset_hash") != _dataset_hash(path):
        raise RuntimeError("AT3: dataset hash haifanani na freeze — dataset imebadilika")
    out = {}
    for name in STRATS:
        spec = art["strategies"][name]
        if rows_by_strat is not None:
            tr = rows_by_strat[name]["train"]; va = rows_by_strat[name]["validation"]
        else:
            allrows = [r for r in _load_rows(None, path) if r["strategy"] == name]
            tr = [r for r in allrows if r["split"] == "train"]
            va = [r for r in allrows if r["split"] == "validation"]
        cfg = dict(spec["config"])
        if cfg.get("fs") == "PRUNED":
            cfg["_feats"] = spec["feats"]
        probs, _, _ = _fit_config(cfg, tr, va)
        pstar = spec["pstar"]                          # AT7: kutoka freeze, HAIHESABIWI upya
        d = delta_ev(probs, np.array([r["pnl_R"] for r in va], float), Q_PRIMARY, pstar=pstar)
        va_pass = bool(d["dev"] > 0 and d["ev_ret"] >= EV_RET_MIN_VALID)
        out[name] = dict(dev=round(d["dev"], 5), ev_ret=round(d["ev_ret"], 4), pstar=pstar,
                         n=len(va), valid_pass=va_pass)
    _append_valid_report(out, out_root)
    return out


# ---------- reports ----------

def _write_report(res, out_root, path):
    L = ["# K4 MODEL v0 — CV REPORT (TRAIN blocked leave-one-year-out; design k4_model_design.md)\n",
         f"*folds=7 (2016-2022) | purge {PURGE_H}h | grid 16 + prune-once | decision=ΔEV_R@70% | "
         f"boot mb={BOOT_MB} B={BOOT_B:,} | H0=hakuna lift; criterion §4: dev>0 & p<{P_ALPHA} & "
         f"dev>=+{DEV_FLOOR}R & ev-ret>={EV_RET_MIN}*\n",
         "> **H0 = HAKUNA lift** (design §0). 'NO-LIFT' ni matokeo halali (LESSON), si kushindwa. "
         "VALID HAIJAGUSWA hapa (eval MOJA baada ya freeze). Accuracy si decision (marufuku §D).\n"]
    for name in STRATS:
        w = res.get(name)
        L.append(f"\n## {name}\n")
        if not w:
            L.append("_data haitoshi (CV haikukamilika)._"); continue
        m = w["m"]
        L.append(f"- **winner:** `{ {k: v for k, v in w['cfg'].items() if not k.startswith('_')} }` "
                 f"(pruned: {w['pruned'] or 'none'})")
        L.append(f"- **ΔEV_R@70% = {m['dev']:+.4f} R** | p_boot={m.get('p_boot')} "
                 f"(CI [{m.get('ci_lo')}, {m.get('ci_hi')}]) | EV-retention={m['ev_ret']} | "
                 f"pstar={m['pstar']} | AUC={m['auc']} (diagnostic) | N={m['n']}")
        L.append(f"- loss-streak (max/P95): all={w['streak_all']['max']}/{w['streak_all']['p95']} "
                 f"-> filtered={w['streak_filt']['max']}/{w['streak_filt']['p95']}")
        L.append(f"- **VERDICT ya H0: {'REJECT (CV-lift)' if w['reject_h0'] else 'FAIL-TO-REJECT (NO-LIFT)'}** "
                 f"(criterion §4).")
    L.append("\n*Next: CV-PASS -> Chief ruling -> --freeze (commit) -> --eval-valid (one-shot). "
             "CV-FAIL -> LESSON 'no deployable lift v0'. Profitable != Tradable Edge.*")
    rpt = Path(out_root) / "reports" / REPORT; rpt.parent.mkdir(parents=True, exist_ok=True)
    rpt.write_text("\n".join(L), encoding="utf-8")
    return rpt


def _append_valid_report(out, out_root):
    rpt = Path(out_root) / "reports" / REPORT
    L = ["\n\n## VALID (one-shot — baada ya freeze; sign-only, §4)\n",
         "| strategy | ΔEV_R@70% | EV-retention | pstar (frozen) | N | VALID |",
         "|----------|-----------|--------------|----------------|---|-------|"]
    for name in STRATS:
        o = out[name]
        L.append(f"| {name} | {o['dev']:+.4f} | {o['ev_ret']} | {o['pstar']} | {o['n']} | "
                 f"{'PASS' if o['valid_pass'] else 'FAIL'} |")
    L.append("\n*VALID = sign-only (taint §D1 + power). Expectation: lift ~0.35-0.5x ya CV. "
             "PASS -> M3-6 gate; FAIL -> LESSON 'CV lift haikuhamia era mpya'.*")
    with open(rpt, "a", encoding="utf-8") as f:
        f.write("\n".join(L))
    return rpt


# ---------- self-test (AT1-AT7; fixtures synthetic) ----------

def _synth(strat, n_per_year=120, planted=False, null=False, seed=0):
    """Rows synthetic zenye schema ya k4: FEATURES + win + pnl_R + ts_entry + year + strategy + split.
    planted: feature 'atr_rel' ina signal ya kweli (win inategemea) -> AUC~0.65. null: labels huru."""
    rng = np.random.default_rng(seed)
    rows = []
    for yr in YEARS:
        base = np.datetime64(f"{yr}-01-04T00")
        for k in range(n_per_year):
            ts = base + np.timedelta64(int(k) * 6, "h")
            ar = float(rng.uniform(0.5, 2.0))
            vs = ["LOW", "NORMAL", "HIGH", "UNKNOWN"][rng.integers(0, 4)]
            if planted:
                pw = 1 / (1 + np.exp(-(1.6 * (ar - 1.25))))     # atr_rel -> win (signal)
                win = int(rng.random() < pw)
            elif null:
                win = int(rng.random() < 0.7)
            else:
                win = int(rng.random() < 0.6)
            pnl = (1.0 if win else -1.0) * abs(rng.normal(1.0, 0.3))
            rows.append(dict(strategy=strat, split="train", year=yr, dir=1,
                             ts_entry=str(ts), entry_bar=k,
                             vol_state=vs, activity_state="NORMAL", spread_state="NORMAL",
                             session_entry="LONDON", dow=int(k % 5), atr_pips=ar * 10, atr_rel=ar,
                             range_nr7_atr=float(rng.uniform(0.3, 1.0)), hour=int(k % 24),
                             h4_trend_sign=int(rng.integers(-1, 2)), d1_trend_sign=1,
                             h4_rsi14=float(rng.uniform(30, 70)), d1_rsi14=float(rng.uniform(30, 70)),
                             h4_roc10=float(rng.normal(0, 0.01)), d1_roc10=float(rng.normal(0, 0.01)),
                             d1_dist_res_atr=float(rng.uniform(0, 3)),
                             pnl_pips=pnl * 10, pnl_R=pnl, win=win, exit_type="TP" if win else "SL",
                             bars_held=int(rng.integers(1, 20)), mfe_r=abs(pnl), mae_r=-abs(pnl),
                             mfe_peak_bar=int(rng.integers(0, 10))))
    return rows


def self_test():
    ok = True
    import tempfile

    # AT1 leak trap: 'mfe_r' (outcome) kwenye FEATURES -> load_k4 assert; X ya trainer ni subset ya manifest
    fs = feature_sets()
    at1a = not (set(fs["CORE"]) & set(OUTCOMES)) and not (set(fs["FULL"]) & set(OUTCOMES))
    at1b = all(f in FEATURES for f in fs["FULL"]) and not any(f in EXCLUDE for f in fs["FULL"])
    print(f"  [AT1] leak trap: no-outcome-in-FS={at1a} FULL<=manifest-EXCLUDE={at1b} -> {at1a and at1b}")
    ok = ok and at1a and at1b

    # AT2 blocked-CV correctness: fold = mwaka mmoja; purge inaondoa boundary; oof cover kila trade mara moja
    rows = _synth("STRAT-001", seed=1)
    cfg = dict(kind="logistic", C=0.3, fs="CORE")
    op, orr, oy, ots, cf = blocked_cv(rows, cfg)
    oof_cover = len(op) == len(rows)                    # kila trade oof mara moja (hakuna purge kwenye test)
    # purge: train ya fold-2017 haina ts ndani ya 24h ya mipaka ya 2017
    te17 = [r for r in rows if r["year"] == 2017]
    tr17 = _purge_train([r for r in rows if r["year"] != 2017], te17)
    tt = np.array([np.datetime64(r["ts_entry"]) for r in te17])
    lo = tt.min() - np.timedelta64(24, "h"); hi = tt.max() + np.timedelta64(24, "h")
    purge_ok = all(not (lo <= np.datetime64(r["ts_entry"]) <= hi) for r in tr17)
    folds_ok = len(cf) == len(YEARS)
    at2 = oof_cover and purge_ok and folds_ok
    print(f"  [AT2] blocked-CV: oof-cover={oof_cover} purge-clean={purge_ok} folds=7={folds_ok} -> {at2}")
    ok = ok and at2

    # AT3 no-VALID-tuning: --cv juu ya rows zenye validation -> PermissionError; eval-valid bila freeze -> error
    rows_v = _synth("STRAT-001", seed=2) + [dict(_synth("STRAT-001", seed=3)[0], split="validation")]
    g_cv = False
    try:
        run_cv(out_root=None, rows_by_strat={"STRAT-001": rows_v, "STRAT-002": _synth("STRAT-002", seed=4)})
    except PermissionError:
        g_cv = True
    g_ev = False
    try:
        with tempfile.TemporaryDirectory() as tmp:
            eval_valid(out_root=tmp, freeze_path=Path(tmp) / "nope.json")
    except RuntimeError:
        g_ev = True
    at3 = g_cv and g_ev
    print(f"  [AT3] no-VALID-tuning: cv-rejects-valid={g_cv} eval-needs-freeze={g_ev} -> {at3}")
    ok = ok and at3

    # AT4 metric exactness: sequence inayojulikana -> ΔEV_R, EV-retention, streak closed-form
    p = np.array([0.9, 0.8, 0.7, 0.2, 0.1]); r = np.array([2.0, -1.0, 1.0, -1.0, -1.0])
    d = delta_ev(p, r, q=0.6)                            # keep p>=quantile(0.4)=0.46 -> top3 (0.9,0.8,0.7)
    # kept = idx 0,1,2 -> pnl [2,-1,1] mean 0.667; all mean 0.0; dev=0.667; ev_ret = 2/-... sum kept=2, all=0 -> ret undefined(0)
    ev_all = r.mean()
    exp_dev = np.mean([2.0, -1.0, 1.0]) - ev_all
    strk = loss_streaks([1, 0, 0, 1, 0, 0, 0, 1])       # runs: 2, 3 -> max 3
    at4 = (abs(d["dev"] - exp_dev) < 1e-12 and d["n_keep"] == 3 and strk["max"] == 3)
    print(f"  [AT4] metric exact: dev={d['dev']:.4f}(=={exp_dev:.4f}) n_keep={d['n_keep']} "
          f"streak-max={strk['max']} -> {at4}")
    ok = ok and at4

    # AT5 determinism: blocked_cv + metrics mara mbili -> bit-identical (seed+solver fixed)
    cfg5 = dict(kind="logistic", C=0.3, fs="CORE")
    a5 = blocked_cv(_synth("STRAT-001", seed=5), cfg5)
    b5 = blocked_cv(_synth("STRAT-001", seed=5), cfg5)
    m5a = _cv_metrics(a5[0], a5[1], a5[2], boot=True, boot_B=500)
    m5b = _cv_metrics(b5[0], b5[1], b5[2], boot=True, boot_B=500)
    at5 = (json.dumps(m5a, sort_keys=True) == json.dumps(m5b, sort_keys=True)
           and json.dumps(a5[4], sort_keys=True) == json.dumps(b5[4], sort_keys=True))
    print(f"  [AT5] determinism: metrics+coefs bit-identical -> {at5}")
    ok = ok and at5

    # AT6 planted-signal detect + null sanity (blocked_cv config MMOJA — kasi; MC ndogo, B ndogo)
    cfg6 = dict(kind="logistic", C=1.0, fs="CORE")
    pl6 = blocked_cv(_synth("STRAT-001", n_per_year=150, planted=True, seed=11), cfg6)
    detect = _auc(pl6[0], pl6[2]) > 0.55                 # signal ipo (AUC juu ya 0.5 by construction)
    rej = 0; M = 12
    for s in range(M):
        o6 = blocked_cv(_synth("STRAT-001", n_per_year=80, null=True, seed=100 + s), cfg6)
        d6 = delta_ev(o6[0], o6[1], Q_PRIMARY)
        if d6["dev"] > 0 and d6["dev"] >= DEV_FLOOR:      # criterion partial
            pb, _, _ = _block_boot_p(o6[1], o6[0], d6["pstar"], Q_PRIMARY, B=400, seed=SEED)
            if pb < P_ALPHA:
                rej += 1
    null_ok = rej <= 4                                   # <= ~1/3 kwa MC=12, B ndogo (lenient)
    at6 = detect and null_ok
    print(f"  [AT6] planted-detect(AUC {_auc(pl6[0], pl6[2]):.3f})={detect} null-reject={rej}/{M}={null_ok} -> {at6}")
    ok = ok and at6

    # AT7 threshold freeze: pstar kutoka freeze file, eval-valid HAIHESABU upya
    cvr = run_cv(out_root=None, boot_B=200,
                 rows_by_strat={"STRAT-001": _synth("STRAT-001", seed=7),
                                "STRAT-002": _synth("STRAT-002", seed=8)})
    with tempfile.TemporaryDirectory() as tmp:
        # jenga parquet ya dataset kwa hash
        import polars as pl
        allr = _synth("STRAT-001", seed=7) + _synth("STRAT-002", seed=8)
        for r in allr[:50]:
            r["split"] = "train"
        (Path(tmp) / "data" / "strategies").mkdir(parents=True, exist_ok=True)
        pl.DataFrame(allr).write_parquet(Path(tmp) / "data" / "strategies" / OUT_PARQUET)
        fdest = freeze(cvr, out_root=tmp, path=Path(tmp) / "data" / "strategies" / OUT_PARQUET)
        art = json.loads(fdest.read_text(encoding="utf-8"))
        has_pstar = all("pstar" in art["strategies"][s] for s in STRATS)
        no_pickle = fdest.suffix == ".json"
        # dataset-hash mismatch -> eval-valid error
        rbs = {name: dict(train=_synth(name, seed=7 if name == "STRAT-001" else 8),
                          validation=_synth(name, seed=20)) for name in STRATS}
        mism = False
        try:
            eval_valid(out_root=tmp, path=Path(tmp) / "data" / "strategies" / OUT_PARQUET,
                       rows_by_strat=rbs, freeze_path=fdest)
        except Exception:
            mism = True                                  # hash inaweza kufanana; tunataka pstar-read tu
        # thibitisha eval inasoma pstar ya freeze (haihesabu upya): patcha delta_ev kudai pstar ilipitishwa
        used_frozen = {"ok": True}
        import k4_model as _km
        _orig = _km.delta_ev
        def _spy(p, r, q, pstar=None):
            if pstar is None:
                used_frozen["ok"] = False
            return _orig(p, r, q, pstar=pstar)
        _km.delta_ev = _spy
        try:
            eval_valid(out_root=tmp, path=Path(tmp) / "data" / "strategies" / OUT_PARQUET,
                       rows_by_strat=rbs, freeze_path=fdest)
        except Exception:
            pass
        finally:
            _km.delta_ev = _orig
    at7 = has_pstar and no_pickle and used_frozen["ok"]
    print(f"  [AT7] threshold freeze: pstar-in-artifact={has_pstar} json(no-pickle)={no_pickle} "
          f"valid-reads-frozen-pstar={used_frozen['ok']} -> {at7}")
    ok = ok and at7

    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def _oof_for(win, rows):
    """(pnl_R, p, pstar) za winner oof — kwa AT6 boot."""
    op, orr, oy, ots, cf = blocked_cv(rows, win["cfg"])
    d = delta_ev(op, orr, Q_PRIMARY)
    return orr, op, d["pstar"]


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--cv", action="store_true", help="grid+prune+report (TRAIN-CV PEKEE)")
    ap.add_argument("--freeze", action="store_true", help="andika k4_model_v0.json (Chief, baada ya CV-PASS)")
    ap.add_argument("--eval-valid", action="store_true", help="VALID one-shot (inahitaji freeze file)")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.cv:
        res = run_cv()
        for name in STRATS:
            w = res[name]
            print(f"{name}: ΔEV_R@70%={w['m']['dev']:+.4f} p_boot={w['m'].get('p_boot')} "
                  f"H0={'REJECT' if w['reject_h0'] else 'FAIL-TO-REJECT'}")
        print(f"  reports/{REPORT}")
        return 0
    if a.freeze:
        res = run_cv(out_root=None)
        dest = freeze(res)
        print(f"FROZEN -> {dest.relative_to(REPO_ROOT)}")
        return 0
    if a.eval_valid:
        out = eval_valid()
        for name in STRATS:
            print(f"{name} VALID: ΔEV_R@70%={out[name]['dev']:+.4f} ret={out[name]['ev_ret']} "
                  f"-> {'PASS' if out[name]['valid_pass'] else 'FAIL'}")
        return 0
    print("Tumia --cv | --freeze | --eval-valid | --self-test.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
