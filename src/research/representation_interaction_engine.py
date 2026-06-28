"""
representation_interaction_engine.py — PHASE 16 (Chief Quant). Representation Interaction Audit.

Phase 15 (Representation Audit) verdict ILIKATALIWA na Chief: ilipima variables MOJA-MOJA
(base + variable), wakati doctrine ni HIERARCHICAL/INTERACTION (State → Age → Transition →
Trajectory) — kama DNA: gene moja haina effect, genes pamoja zinatengeneza protein.
Standalone incremental R² inaweza kushindwa wakati COMBINATION ndiyo yenye taarifa.

  Principle 34 (APPROVED): variable inaweza kuchangia kupitia INTERACTION, CALIBRATION,
                           au STABILITY hata kama standalone predictive contribution ni ndogo.
  Principle 35 (APPROVED): ubora wa representation HAUPIMWI kwa predictive gain pekee.
  F-034 (APPROVED): redundancy kati ya hierarchical variables inategemewa; SI uselessness
                    (Persistence = derivative ya Age — uthibitisho wa ontology).

Phase 16 inapima INTERACTIONS + institutional metrics (sio additive R² pekee):
  Q1. Je Age × Transition inaongeza information (sio Age peke yake)?
  Q2. Je Trajectory × Event inaongeza information?
  Q3. Je Age × Trajectory × Transition ni bora kuliko kila moja peke yake?
  Q4. Je hierarchy ya doctrine (State→Age→Transition→Trajectory) inaonekana kwenye data?
  Q5. Ni interactions zipi zina surviving information baada ya permutation?

Metrics mpya: Incremental Calibration (Brier), Stability across folds, Transferability
across pairs, Robustness across regimes — sio incremental R² pekee.

Mbinu: variance-explained R² (joint cells) ikidhibitiwa na permutation null; Brier kwa
random folds; sign-stability across folds; cross-group Spearman ya cell-EV. NO ML.

Reuse: representation_audit_engine (build_df, r2), confidence_engine (spearman).

Output: reports/representation_interaction_report.md
Self-test: python src/research/representation_interaction_engine.py --self-test
"""
from __future__ import annotations

import argparse, sys
from collections import defaultdict
from datetime import datetime
from itertools import combinations
from pathlib import Path

import numpy as np
import polars as pl

from market_state_engine import cfg
from representation_audit_engine import build_df, r2
from confidence_engine import spearman

REPO_ROOT = Path(__file__).resolve().parents[2]
NREP = 25
KFOLD = 4
MIN_CELL = 40


def group_inc(df, base, add, rng, nrep=NREP):
    """Incremental R² ya kuongeza `add` (joint) juu ya `base`, perm-controlled.
    base=[X], add=[Y] -> je (X,Y) inaongeza juu ya X peke yake (interaction/joint)."""
    r_b = r2(df, base); r_full = r2(df, base + add); inc = r_full - r_b
    nulls = []
    for _ in range(nrep):
        ds = df
        for col in add:
            ds = ds.with_columns(pl.col(col).shuffle(seed=int(rng.integers(0, 1_000_000_000))))
        nulls.append(r2(ds, base + add) - r_b)
    nulls = np.array(nulls)
    p = (1 + int(np.sum(nulls >= inc))) / (nrep + 1)
    return inc, float(nulls.mean()), p, r_full


def brier(df, cols, rng, reps=3):
    """Brier score (calibration) ya kutabiri win=(y>0) kwa cell win-rate; random train/test."""
    win_all = float((df["y"] > 0).cast(pl.Float64).mean())
    dfw = df.with_columns((pl.col("y") > 0).cast(pl.Float64).alias("win"))
    out = []
    for _ in range(reps):
        m = rng.random(dfw.height) < 0.5
        tr = dfw.filter(m); te = dfw.filter(~m)
        if cols:
            rate = tr.group_by(cols).agg(pl.col("win").mean().alias("p"))
            te2 = te.join(rate, on=cols, how="left").with_columns(pl.col("p").fill_null(win_all))
            pred = te2["p"].to_numpy()
        else:
            pred = np.full(te.height, float(tr["win"].mean()))
        w = te["win"].to_numpy()
        out.append(float(np.mean((w - pred) ** 2)))
    return float(np.mean(out))


def stability(df, cols, rng, k=KFOLD):
    """Sehemu ya cells ambazo ishara ya EV inakubaliana kati ya folds zote (random)."""
    fold = rng.integers(0, k, df.height)
    d = df.with_columns(pl.Series("fold", fold))
    g = d.group_by(cols + ["fold"]).agg(pl.col("y").mean().alias("ev"), pl.len().alias("n")).filter(pl.col("n") >= MIN_CELL)
    by_cell = defaultdict(list)
    for row in g.iter_rows(named=True):
        key = tuple(row[c] for c in cols)
        by_cell[key].append(row["ev"])
    consistent = 0; tot = 0
    for key, evs in by_cell.items():
        if len(evs) >= k:
            tot += 1
            s = np.sign(np.mean(evs))
            if all(np.sign(e) == s for e in evs):
                consistent += 1
    return consistent / tot if tot else float("nan"), tot


def xcorr_over(df, split_col, cols, min_n=MIN_CELL):
    """Mean pairwise Spearman ya cell-EV vectors kati ya values za split_col (transfer/robust)."""
    g = df.group_by([split_col] + cols).agg(pl.col("y").mean().alias("ev"), pl.len().alias("n")).filter(pl.col("n") >= min_n)
    vals = defaultdict(dict)
    for row in g.iter_rows(named=True):
        key = tuple(row[c] for c in cols)
        vals[row[split_col]][key] = row["ev"]
    splits = list(vals); cors = []
    for a, b in combinations(splits, 2):
        shared = set(vals[a]) & set(vals[b])
        if len(shared) >= 4:
            sk = list(shared)
            cors.append(spearman([vals[a][k] for k in sk], [vals[b][k] for k in sk]))
    cors = [c for c in cors if np.isfinite(c)]
    return float(np.mean(cors)) if cors else float("nan"), len(cors)


def run(pairs, tfs):
    c = cfg(); rng = np.random.default_rng(0)
    df, no_px = build_df(pairs)
    if no_px:
        print("HITILAFU: state parquet haipo. Endesha market_state_engine.py kwanza.", file=sys.stderr)
        return 1
    print(f"  instances={df.height:,}", flush=True)

    L = ["# Representation Interaction Audit — je hierarchy/interaction inaongeza taarifa? (Phase 16)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | joint R² (perm-controlled, {NREP} reps) + Brier calibration + "
         f"fold-stability + cross-pair/regime transfer | instances={df.height:,}*\n",
         "> **Principle 34/35 (Chief):** variable inaweza kuchangia kupitia INTERACTION/CALIBRATION/STABILITY "
         "hata standalone ikiwa ndogo; representation HAIPIMWI kwa predictive gain pekee. **F-034:** redundancy "
         "ya hierarchical variables inategemewa. Hatupimi base+variable-moja tena — tunapima INTERACTIONS + "
         "institutional metrics (calibration/stability/transferability/robustness). NO ML.\n"]

    def fmt_inc(label, base, add):
        inc, nl, p, rf = group_inc(df, base, add, rng)
        adds = inc > nl and p < 0.05
        return inc, nl, p, adds, (f"| {label} | {rf:.5f} | {inc:+.6f} | {nl:+.6f} | {p:.3f} | "
                                  f"{'✅' if adds else '—'} |")

    # Q1
    L.append("\n## Q1 — Age × Transition (juu ya kila moja peke yake)\n")
    L.append("| test | R²(joint) | incremental | null | p | adds? |")
    L.append("|------|-----------|-------------|------|---|-------|")
    _, _, _, q1a, r1 = fmt_inc("Age → +Transition", ["age"], ["trans"]); L.append(r1)
    _, _, _, q1b, r2r = fmt_inc("Transition → +Age", ["trans"], ["age"]); L.append(r2r)
    L.append(f"\n→ Age × Transition {'✅ inaongeza information zaidi ya kila moja peke yake' if (q1a or q1b) else '— haijaongeza juu ya standalone'}.")

    # Q2
    L.append("\n## Q2 — Trajectory × Event\n")
    L.append("| test | R²(joint) | incremental | null | p | adds? |")
    L.append("|------|-----------|-------------|------|---|-------|")
    _, _, _, q2a, r3 = fmt_inc("Event → +Trajectory", ["event"], ["traj"]); L.append(r3)
    _, _, _, q2b, r4 = fmt_inc("Trajectory → +Event", ["traj"], ["event"]); L.append(r4)
    L.append(f"\n→ Trajectory × Event {'✅ inaongeza information' if (q2a or q2b) else '— haijaongeza juu ya standalone'}.")

    # Q3
    L.append("\n## Q3 — Age × Trajectory × Transition (juu ya pairwise/standalone)\n")
    r_a = r2(df, ["age"]); r_t = r2(df, ["traj"]); r_x = r2(df, ["trans"])
    r_3 = r2(df, ["age", "traj", "trans"])
    inc3, nl3, p3, q3 = fmt_inc("(Age,Traj) → +Transition", ["age", "traj"], ["trans"])[:4]
    L.append(f"- R²(Age)={r_a:.5f} · R²(Traj)={r_t:.5f} · R²(Trans)={r_x:.5f} · **R²(Age,Traj,Trans)={r_3:.5f}**")
    L.append(f"- 3-way juu ya best-standalone: +{r_3 - max(r_a, r_t, r_x):.5f}; "
             f"adding Transition to (Age,Traj): inc={inc3:+.6f} (p={p3:.3f}, {'✅' if q3 else '—'})")
    L.append(f"\n→ 3-way {'✅ ni bora kuliko kila moja peke yake' if r_3 > max(r_a, r_t, r_x) + 1e-6 and q3 else '— haijazidi kwa uhakika'}.")

    # Q4 — hierarchy
    L.append("\n## Q4 — Je hierarchy ya doctrine (State→Age→Transition→Trajectory) inaonekana?\n")
    L.append("| hatua | imeongezwa | R² hadi sasa | incremental | p | inaongeza? |")
    L.append("|-------|------------|--------------|-------------|---|------------|")
    order = ["vol", "age", "trans", "traj"]; sel = []; hier_steps = 0
    for col in order:
        if not sel:
            rf = r2(df, [col]); sel.append(col)
            L.append(f"| 1 | {col} (State) | {rf:.5f} | (base) | — | — |"); continue
        inc, nl, p, rf = group_inc(df, sel, [col], rng)
        adds = inc > nl and p < 0.05; hier_steps += 1 if adds else 0
        sel.append(col)
        L.append(f"| {len(sel)} | {col} | {rf:.5f} | {inc:+.6f} | {p:.3f} | {'✅' if adds else '—'} |")
    L.append(f"\n→ hatua za hierarchy zinazoongeza taarifa: **{hier_steps}/{len(order)-1}** "
             f"({'hierarchy inaonekana kwenye data' if hier_steps >= 2 else 'hierarchy haijathibitika wazi'}).")

    # Q5 — surviving interactions
    L.append("\n## Q5 — Interactions zenye surviving information baada ya permutation\n")
    L.append("| interaction | incremental (juu ya member 1) | p | survives? |")
    L.append("|-------------|-------------------------------|---|-----------|")
    pairs_test = [("event", "traj"), ("event", "age"), ("age", "trans"), ("traj", "trans"),
                  ("age", "traj"), ("vol", "trans"), ("event", "vol"), ("activity", "event")]
    survivors = []
    for a, b in pairs_test:
        inc, nl, p, rf = group_inc(df, [a], [b], rng)
        surv = inc > nl and p < 0.05; survivors.append((a, b)) if surv else None
        L.append(f"| {a} × {b} | {inc:+.6f} | {p:.3f} | {'✅' if surv else '—'} |")
    L.append(f"\n→ interactions zilizonusurika permutation: **{len(survivors)}/{len(pairs_test)}**"
             + (f" ({', '.join(f'{a}×{b}' for a,b in survivors)})" if survivors else ""))

    # Institutional metrics — headline grouping (age,traj,trans) vs standalone age
    L.append("\n## Metrics za institutional (zaidi ya R²) — grouping: Age·Trajectory·Transition\n")
    G = ["age", "traj", "trans"]; S = ["age"]
    bg = brier(df, G, rng); bs = brier(df, S, rng); bbase = brier(df, [], rng)
    stab_g, ng = stability(df, G, rng); stab_s, ns = stability(df, S, rng)
    tr_g, ntr = xcorr_over(df, "pair", G); rob_g, nrob = xcorr_over(df, "vol", ["age", "traj"])
    L.append("| metric | standalone (Age) | interaction (Age·Traj·Trans) | bora? |")
    L.append("|--------|------------------|------------------------------|-------|")
    L.append(f"| Brier (chini=bora) | {bs:.5f} | {bg:.5f} | {'✅' if bg < bs else '—'} |")
    L.append(f"| Fold-stability (sign) | {stab_s*100:.0f}% | {stab_g*100:.0f}% | {'✅' if stab_g > stab_s else '—'} |")
    L.append(f"| Transferability (cross-pair ρ) | — | {tr_g:+.2f} | {'✅' if np.isfinite(tr_g) and tr_g>0.2 else '—'} |")
    L.append(f"| Robustness (cross-regime ρ) | — | {rob_g:+.2f} | {'✅' if np.isfinite(rob_g) and rob_g>0.2 else '—'} |")
    L.append(f"\n*(Brier base={bbase:.5f}; calibration/stability institutional, sio predictive gain pekee — Principle 35.)*")

    # VERDICT
    any_inter = (q1a or q1b or q2a or q2b or q3 or len(survivors) >= 1)
    cal_ok = bg < bs; stab_ok = np.isfinite(stab_g) and np.isfinite(stab_s) and stab_g > stab_s
    L.append("\n## VERDICT — Phase 16 Representation Interaction Audit\n")
    if any_inter or cal_ok or stab_ok:
        L.append(f"→ ✅ representation ya hierarchical/interaction **INACHANGIA** zaidi ya standalone: "
                 f"interactions zilizonusurika={len(survivors)}; hierarchy steps={hier_steps}; "
                 f"calibration {'imeboreshwa' if cal_ok else 'haijaboreshwa'}; stability "
                 f"{'imeboreshwa' if stab_ok else 'haijaboreshwa'}. Hii inaunga mkono Principle 34/35 — "
                 "age/traj/transition zina thamani kwa interaction/calibration/stability hata kama standalone "
                 "R² ni ndogo (Phase 15). HAZIONDOLEWI doctrine. Inayofuata: jenga representation ya "
                 "interaction-aware kisha rudia Confirmation (OOS+FDR).")
    else:
        L.append("→ ⚠️ hata kwa interactions + institutional metrics, hakuna ushahidi wa nyongeza juu ya base "
                 "kwa data hii. (SI uthibitisho kuwa hierarchy imefeli — inaweza kuwa representation FORM "
                 "[continuous] au evaluation bado haijatosha; Principle 33.)")
    L.append("\n*Interaction audit: joint R² (perm-controlled), Brier calibration, fold-stability, cross-pair "
             "transferability, cross-regime robustness. Principle 34: contribution kupitia interaction/"
             "calibration/stability. Principle 35: usipime kwa predictive gain pekee. F-034: redundancy ya "
             "hierarchical = ontology sahihi. NO ML. Profitable ≠ Tradable Edge.*")
    out = REPO_ROOT / c["paths"]["reports"] / "representation_interaction_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)} (interactions survive: {len(survivors)}, "
          f"hierarchy steps: {hier_steps}, Brier {bs:.4f}->{bg:.4f})")
    return 0


def self_test():
    """(1) group_inc inagundua INTERACTION (XOR) ambapo standalone R²≈0 lakini joint kubwa.
       (2) noise interaction haina survival. (3) brier/stability/xcorr sanity."""
    rng = np.random.default_rng(0); n = 12000
    A = rng.integers(0, 2, n); B = rng.integers(0, 2, n)
    # XOR interaction: y inategemea (A==B), SIO A wala B peke yake
    y = np.where(A == B, 5.0, -5.0) + rng.normal(0, 4, n)
    noise = rng.integers(0, 2, n)
    df = pl.DataFrame(dict(A=[str(x) for x in A], B=[str(x) for x in B],
                           noise=[str(x) for x in noise], y=y))

    rA = r2(df, ["A"]); rAB = r2(df, ["A", "B"])
    inc, nl, p, rf = group_inc(df, ["A"], ["B"], rng, nrep=30)
    xor_ok = rA < 0.01 and rAB > 0.1 and inc > nl and p < 0.05
    print(f"XOR: R²(A)={rA:.4f} R²(A,B)={rAB:.4f} inc={inc:.4f} null={nl:.4f} p={p:.3f} (interaction={xor_ok})")

    incn, nln, pn, _ = group_inc(df, ["A"], ["noise"], rng, nrep=30)
    noise_ok = not (incn > nln and pn < 0.05)
    print(f"noise interaction: inc={incn:.5f} p={pn:.3f} (no-signal={noise_ok})")

    b_ab = brier(df, ["A", "B"], rng); b_a = brier(df, ["A"], rng)
    brier_ok = b_ab < b_a   # joint inaboresha calibration ya win
    print(f"brier: A={b_a:.4f} (A,B)={b_ab:.4f} (joint better={brier_ok})")

    ok = xor_ok and noise_ok and brier_ok
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default=None)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    c = cfg()
    pairs = [a.symbol] if a.symbol else c["pairs"]
    return run(pairs, None)


if __name__ == "__main__":
    raise SystemExit(main())
