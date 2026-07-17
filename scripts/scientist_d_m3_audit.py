"""scientist_d_m3_audit.py — M3-QA curriculum audit (SCIENTIST-D, external reviewer).

Adversarial checks juu ya vitabu 2 vya data (data/strategies/k4_dataset.parquet +
rmap_train.parquet) — kila namba ya reports/m3_curriculum_audit.md inazalishwa hapa.
Hakuna dirisha jipya linaloguswa: parquets ni TRAIN(+VALID kwa K4) tu, zilizokwisha-jengwa.

Sehemu:
  K1 label integrity (win/pnl/exit_type/MFE-MAE consistency; recompute dhidi ya proven artifacts)
  K2 duplicates + identifiability (hakuna ts column — proxy checks)
  K3 class balance + N per regime (cells <30 = 'haifundishiki bado')
  K4 year coverage + UNKNOWN warmup shares
  K5 single-feature AUC screen (leak hunt: AUC>0.60 = suspect kwa domain hii)
  R1 atlas n-distribution (cell-thinness), UNKNOWN×year confound, D1 session artifact
  R2 breadth recompute (nr7 H4 HIGH n.k.) + year-concentration ya star combos
  R3 swap/cost materiality kwa TF

Usage: python scripts/scientist_d_m3_audit.py   (repo root; polars+numpy)
"""
from __future__ import annotations
import json, subprocess
import numpy as np
import polars as pl

SL = {"STRAT-001": 2.0, "STRAT-002": 1.0}

def sec(t): print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)

k4 = pl.read_parquet("data/strategies/k4_dataset.parquet")
rm = pl.read_parquet("data/strategies/rmap_train.parquet")

sec("K1) K4 LABEL INTEGRITY")
w_ok = (k4["win"] == (k4["pnl_pips"] > 0).cast(pl.Int64)).all()
tp = k4.filter(pl.col("exit_type") == "TP"); sl_ = k4.filter(pl.col("exit_type") == "SL")
to = k4.filter(pl.col("exit_type") == "timeout")
tp_pos = float((tp["pnl_pips"] > 0).mean()); sl_neg = float((sl_["pnl_pips"] < 0).mean())
print(f"  win==(pnl>0): {w_ok} | TP-exits pnl>0: {tp_pos:.4f} | SL-exits pnl<0: {sl_neg:.4f} | timeouts n={to.height}")
# pnl_R * (sl_atr*atr) == pnl (rounding 1e-3)
r_err = (k4.with_columns(sl_atr=pl.col("strategy").replace_strict(SL))
           .with_columns(err=(pl.col("pnl_R") * pl.col("sl_atr") * pl.col("atr_pips") - pl.col("pnl_pips")).abs()))
print(f"  pnl_R*risk==pnl: max_err={float(r_err['err'].max()):.4f} pips (rounding tu)")
mfe_ok = float((k4["mfe_r"] >= 0).mean()); mae_ok = float((k4["mae_r"] <= 0).mean())
mfe_ge = float((k4["mfe_r"] >= k4["pnl_R"] - 1e-6).mean())
print(f"  mfe_r>=0: {mfe_ok:.4f} | mae_r<=0: {mae_ok:.4f} | mfe_r>=pnl_R (gross>=net): {mfe_ge:.4f}")
# recompute baselines vs PROVEN git artifacts (e1a0d27 = C1 VALID; ccfbb24 = C1 TRAIN)
def cell_from(commit, pair, sl, tp_):
    txt = subprocess.run(["git", "show", f"{commit}:data/strategies/candidates.jsonl"],
                         capture_output=True, text=True, check=True).stdout
    for line in txt.splitlines():
        r = json.loads(line)
        if (r["event"] == "nr7_break" and r["pair"] == pair and r["sl_atr"] == sl
                and r["tp_atr"] == tp_ and r["session_filter"] == "no-LATE" and r["vol_filter"] is None):
            return r
for name, pair, slv, tpv in (("STRAT-001", "USDCHF", 2.0, 1.0), ("STRAT-002", "USDJPY", 1.0, 1.0)):
    for split, commit in (("train", "ccfbb24"), ("validation", "e1a0d27")):
        art = cell_from(commit, pair, slv, tpv)
        sub = k4.filter((pl.col("strategy") == name) & (pl.col("split") == split))
        ev = float(sub["pnl_pips"].mean()); wr = float(sub["win"].mean())
        m = (sub.height == art["n"] and abs(ev - art["ev"]) < 5e-3 and abs(wr - art["win"]) < 5e-4)
        print(f"  {name}/{split} vs {commit}: N {sub.height}=={art['n']} EV {ev:+.3f}=={art['ev']:+.3f} "
              f"win {wr:.4f}=={art['win']:.4f} -> {'MATCH' if m else 'MISMATCH!'}")

sec("K2) K4 DUPLICATES / IDENTIFIABILITY")
dups = k4.height - k4.unique().height
print(f"  exact duplicate rows: {dups} / {k4.height}")
print(f"  ts/entry-bar column? {'ts_entry' in k4.columns or 'entry_bar' in k4.columns} "
      f"-> (hakuna: non-overlap haithibitiki KUTOKA kitabu; time-aware CV ya M3-5 haiwezekani bila ts) ")

sec("K3) K4 CLASS BALANCE + N PER REGIME (train split pekee — ndiyo ya kufundishia)")
tr = k4.filter(pl.col("split") == "train")
for col in ("vol_state", "spread_state", "activity_state", "session_entry", "d1_vol_state"):
    g = (tr.group_by("strategy", col).agg(n=pl.len(), win=pl.col("win").mean())
           .sort(["strategy", col]))
    cells = [f"{r['strategy'][-3:]}|{r[col]}: n={r['n']} w={r['win']:.2f}" for r in g.iter_rows(named=True)]
    small = [f"{r['strategy'][-3:]}|{r[col]}(n={r['n']})" for r in g.iter_rows(named=True) if r["n"] < 30]
    print(f"  {col}: " + " · ".join(cells))
    if small:
        print(f"    << N<30 (haifundishiki): {small}")

sec("K4) K4 YEAR COVERAGE + UNKNOWN/NaN kwa mwaka")
g = k4.group_by("strategy", "split", "year").agg(n=pl.len(), win=pl.col("win").mean()).sort(["strategy", "year"])
for r in g.iter_rows(named=True):
    print(f"  {r['strategy']}/{r['split']}/{r['year']}: n={r['n']} win={r['win']:.3f}")
unk = k4.group_by("year").agg(
    unk_vol=(pl.col("vol_state") == "UNKNOWN").mean(),
    d1_nan=pl.col("d1_linreg_slope").is_null().mean()).sort("year")
print("  UNKNOWN vol / d1 NaN kwa mwaka: " +
      " · ".join(f"{r['year']}:{r['unk_vol']:.2f}/{r['d1_nan']:.2f}" for r in unk.iter_rows(named=True)))

sec("K5) K4 SINGLE-FEATURE AUC SCREEN (leak hunt; flag > 0.60) — train, per strategy")
def auc(x, y):
    x = np.asarray(x, float); y = np.asarray(y, int)
    m = np.isfinite(x)
    x, y = x[m], y[m]
    if y.sum() in (0, len(y)) or len(y) < 50:
        return np.nan
    r = x.argsort().argsort().astype(float) + 1
    n1 = y.sum(); n0 = len(y) - n1
    a = (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)
    return max(a, 1 - a)
numf = ["hour", "dow", "atr_pips", "range_nr7_atr", "h4_ema_slope", "h4_linreg_slope",
        "h4_trend_sign", "h4_dist_res_atr", "h4_dist_sup_atr", "h4_rsi14", "h4_roc10",
        "d1_ema_slope", "d1_linreg_slope", "d1_trend_sign", "d1_dist_res_atr",
        "d1_dist_sup_atr", "d1_rsi14", "d1_roc10", "dir"]
flags = []
for name in ("STRAT-001", "STRAT-002"):
    sub = tr.filter(pl.col("strategy") == name)
    aucs = {f: auc(sub[f].cast(pl.Float64, strict=False).to_numpy(), sub["win"].to_numpy())
            for f in numf if f in sub.columns}
    top = sorted(((v, k) for k, v in aucs.items() if np.isfinite(v)), reverse=True)[:6]
    print(f"  {name}: top AUC " + " · ".join(f"{k}={v:.3f}" for v, k in top))
    flags += [f"{name}:{k}={v:.3f}" for v, k in top if v > 0.60]
print(f"  FLAGS (>0.60): {flags or 'HAKUNA — hakuna feature inayotabiri kupita kiasi (leak-clean)'}")

sec("R1) ATLAS: cell-thinness + UNKNOWN×year confound + D1 session artifact")
print(f"  rows={rm.height:,} | n<30: {float((rm['n'] < 30).mean()):.1%} | median n={int(rm['n'].median())} | "
      f"n>=30 rows={int((rm['n'] >= 30).sum()):,}")
u = rm.group_by("year").agg(unk=(pl.col("vol_state") == "UNKNOWN").mean(),
                            trades_unk=pl.col("n").filter(pl.col("vol_state") == "UNKNOWN").sum(),
                            trades=pl.col("n").sum()).sort("year")
print("  UNKNOWN share (rows / trades) kwa mwaka: " +
      " · ".join(f"{r['year']}:{r['unk']:.2f}/{(r['trades_unk'] or 0)/r['trades']:.2f}" for r in u.iter_rows(named=True)))
d1s = rm.filter(pl.col("tf") == "D1")["sess_top"].value_counts()
print(f"  D1 sess_top: {dict(zip(d1s['sess_top'], d1s['count']))}  <- hour(D1 bar)=00 daima")
h4s = rm.filter(pl.col("tf") == "H4")["sess_top"].value_counts().sort("count", descending=True)
print(f"  H4 sess_top: {dict(zip(h4s['sess_top'], h4s['count']))}")

sec("R2) ATLAS BREADTH RECOMPUTE + year-concentration ya star combos")
def breadth(ev, tf, vs):
    s = (rm.filter((pl.col("event") == ev) & (pl.col("tf") == tf) & (pl.col("vol_state") == vs))
           .group_by("pair").agg(ev_p=(pl.col("ev_net") * pl.col("n")).sum() / pl.col("n").sum(),
                                 n=pl.col("n").sum()))
    return int((s["ev_p"] > 0).sum()), s.height, s
for ev, tf, vs in (("nr7_break", "H4", "HIGH"), ("shock_follow", "H4", "LOW"),
                   ("nr7_break", "D1", "LOW"), ("lowvol_reversal", "D1", "NORMAL")):
    pos, tot, s = breadth(ev, tf, vs)
    yr = (rm.filter((pl.col("event") == ev) & (pl.col("tf") == tf) & (pl.col("vol_state") == vs))
            .group_by("year").agg(ev_y=(pl.col("ev_net") * pl.col("n")).sum() / pl.col("n").sum(),
                                  n=pl.col("n").sum()).sort("year"))
    yline = " ".join(f"{r['year']}:{r['ev_y']:+.1f}(n={r['n']})" for r in yr.iter_rows(named=True))
    pos_y = int((yr["ev_y"] > 0).sum())
    print(f"  {ev}×{tf}×{vs}: breadth {pos}/{tot} (report ✓?) | miaka EV+: {pos_y}/{yr.height} | {yline}")

sec("R3) SWAP/COST MATERIALITY kwa TF (atlas)")
g = (rm.group_by("tf").agg(ev=(pl.col("ev_net") * pl.col("n")).sum() / pl.col("n").sum(),
                           gross=(pl.col("gross") * pl.col("n")).sum() / pl.col("n").sum(),
                           n=pl.col("n").sum()).sort("tf"))
for r in g.iter_rows(named=True):
    drag = r["gross"] - r["ev"]
    print(f"  {r['tf']}: trades={r['n']:,} gross={r['gross']:+.2f} ev_net={r['ev']:+.2f} "
          f"drag(cost+swap)={drag:.2f} pips ({100*drag/abs(r['gross']) if r['gross'] else 0:.0f}% ya |gross|)")
print("\nAUDIT DONE — namba hizi ndizo za reports/m3_curriculum_audit.md")
