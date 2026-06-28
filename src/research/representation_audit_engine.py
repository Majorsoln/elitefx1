"""
representation_audit_engine.py — PHASE 15 (Chief Quant). Representation Audit.

Phase 14 (Confirmation) ilionyesha: hypotheses 282 zilipre-registerwa, UNKNOWN
ziliondolewa, future OOS + Benjamini–Hochberg FDR zilitumika -> **0 zilinusurika**.
Chief: hii SI "No Alpha" — ni **Current Representation Failure** (Principle 33; F-033).
Tulijaribu representation MOJA tu: Event + Pair + Vol + Spread + Session. Doctrine ina
variables nyingi ambazo bado hazijaingizwa (state age, trajectory, transition,
persistence, activity, sequencing, memory, execution timing).

Kabla ya kuongeza data/complexity/ML, tunakagua REPRESENTATION yenyewe (NO ML, NO data
mpya, NO strategy). Maswali (Chief):

  Q1. Assumptions zipi zimefichwa kwenye current representation?
  Q2. Doctrine variables zipi bado hazijaingizwa?
  Q3. Je state age/trajectory/transition/persistence/activity vinaongeza INCREMENTAL
      information juu ya Event+Pair+Vol+Spread+Session?
  Q4. Je kuna REDUNDANCY kati ya variables zilizopo?
  Q5. Minimal sufficient representation ni ipi (taarifa zote bila noise ya ziada)?

Mbinu: variance-of-outcome EXPLAINED na representation cells (R²), incremental R²
ikidhibitiwa na PERMUTATION null (kuondoa cardinality-overfit); redundancy = Cramér's V.
Outcome y = directional net (d·fwd − spread). polars groupby kwa kasi.

Reuse: market_state_engine (cfg, pip), latent_structure (state_path), event_library
(EVENTS_ALL), configuration_engine (EVENTS_SET, VERT), context_value (HORIZON),
contextual_alpha_engine (session_of).

Output: reports/representation_audit_report.md
Self-test: python src/research/representation_audit_engine.py --self-test
"""
from __future__ import annotations

import argparse, sys
from datetime import datetime
from pathlib import Path

import numpy as np
import polars as pl

from market_state_engine import cfg, pip
from latent_structure import state_path
from event_library import EVENTS_ALL
from configuration_engine import EVENTS_SET, VERT
from context_value import HORIZON
from contextual_alpha_engine import session_of

REPO_ROOT = Path(__file__).resolve().parents[2]
TFS = ["H1", "H2", "H4", "D1"]
BASE = ["event", "pair", "vol", "spread", "session"]          # current representation
ADDON = ["activity", "age", "traj", "trans", "persist"]       # doctrine vars to test
ALLV = BASE + ADDON
NREP = 30             # permutation reps for incremental-info null
VLEVEL = {"LOW": 0, "NORMAL": 1, "HIGH": 2, "UNKNOWN": 1}
TRAJ_WIN = 3


def _run_lengths(states):
    rl = np.ones(len(states), int)
    for i in range(1, len(states)):
        rl[i] = rl[i - 1] + 1 if states[i] == states[i - 1] else 1
    return rl


def _persist_bucket(r):
    return "1" if r <= 1 else ("2-3" if r <= 3 else ("4-8" if r <= 8 else "9+"))


def _age_bucket(r):
    return "new" if r <= 2 else ("mid" if r <= 6 else "old")


def build_df(pairs):
    cols = {k: [] for k in ALLV + ["y"]}
    no_px = True
    for sym in pairs:
        pp = pip(sym)
        for tf in TFS:
            p = state_path(sym, tf)
            if not p.exists():
                continue
            df = pl.read_parquet(p)
            if "c" not in df.columns:
                continue
            no_px = False
            close = df["c"].to_numpy() / pp; high = df["h"].to_numpy() / pp; low = df["l"].to_numpy() / pp
            atr = df["atr"].to_numpy() / pp
            spr = df["spr"].to_numpy(); spr = np.where(np.isfinite(spr), spr, 0.0)
            vol = df["volatility_state"].to_list(); sprst = df["spread_state"].to_list()
            act = df["activity_state"].to_list(); hours = df["ts"].dt.hour().to_list()
            rl = _run_lengths(vol); L = np.array([VLEVEL.get(v, 1) for v in vol])
            n = len(close)
            sig = {ev: EVENTS_ALL[ev](close, high, low) for ev in EVENTS_SET}
            for i in range(n):
                if i + VERT >= n or i + HORIZON >= n or not (atr[i] > 0):
                    continue
                fwd = close[i + HORIZON] - close[i]; sp = spr[i]
                traj = ("UP" if i >= TRAJ_WIN and L[i] > L[i - TRAJ_WIN]
                        else "DOWN" if i >= TRAJ_WIN and L[i] < L[i - TRAJ_WIN] else "FLAT")
                trans = "Y" if i >= 1 and vol[i] != vol[i - 1] else "N"
                pb = _persist_bucket(rl[i]); ab = _age_bucket(rl[i])
                for ev in EVENTS_SET:
                    s = sig[ev][i]
                    if s == 0:
                        continue
                    y = float(int(s) * fwd - sp)
                    cols["event"].append(ev); cols["pair"].append(sym); cols["vol"].append(vol[i])
                    cols["spread"].append(sprst[i]); cols["session"].append(session_of(hours[i]))
                    cols["activity"].append(act[i]); cols["age"].append(ab); cols["traj"].append(traj)
                    cols["trans"].append(trans); cols["persist"].append(pb); cols["y"].append(y)
        print(f"  {sym}: done", flush=True)
    return pl.DataFrame(cols), no_px


def r2(df, cols):
    """Fraction ya variance ya y iliyoelezwa na representation cells (cols)."""
    N = df.height
    if N == 0:
        return 0.0
    gm = df["y"].mean()
    tot = float((df["y"] ** 2).sum() - N * gm * gm)
    if tot <= 0:
        return 0.0
    if not cols:
        return 0.0
    g = df.group_by(cols).agg(pl.len().alias("n"), pl.col("y").sum().alias("s"),
                              (pl.col("y") ** 2).sum().alias("ss"))
    within = float((g["ss"] - g["s"] ** 2 / g["n"]).sum())
    return 1.0 - within / tot


def inc_info(df, base, var, rng, nrep=NREP):
    """Incremental R² ya var juu ya base, ikidhibitiwa na permutation null (cardinality)."""
    r_b = r2(df, base); r_bv = r2(df, base + [var]); inc = r_bv - r_b
    nulls = []
    for _ in range(nrep):
        ds = df.with_columns(pl.col(var).shuffle(seed=int(rng.integers(0, 1_000_000_000))))
        nulls.append(r2(ds, base + [var]) - r_b)
    nulls = np.array(nulls)
    p = (1 + int(np.sum(nulls >= inc))) / (nrep + 1)
    return inc, float(nulls.mean()), p


def cramers_v(df, a, b):
    """Cramér's V (association) kati ya categorical a na b."""
    g = df.group_by([a, b]).agg(pl.len().alias("n"))
    av = g[a].unique().to_list(); bv = g[b].unique().to_list()
    ai = {x: i for i, x in enumerate(av)}; bi = {x: i for i, x in enumerate(bv)}
    M = np.zeros((len(av), len(bv)))
    for row in g.iter_rows(named=True):
        M[ai[row[a]], bi[row[b]]] = row["n"]
    N = M.sum()
    if N == 0 or min(M.shape) < 2:
        return 0.0
    E = M.sum(1, keepdims=True) * M.sum(0, keepdims=True) / N
    chi2 = float(np.sum((M - E) ** 2 / np.where(E > 0, E, 1)))
    return float(np.sqrt(chi2 / (N * (min(M.shape) - 1))))


ASSUMPTIONS = [
    "Context ni STATIC @entry — haijumuishi historia/trajectory ya state (F-026).",
    "States ni DISCRETE terciles (LOW/NORMAL/HIGH) — hupoteza ukubwa endelevu wa ATR.",
    "spread_state ni BINARY (NORMAL/WIDE) — liquidity ni continuum, sio 2 buckets.",
    "Outcome ni horizon FIXED (forward {} bars) — haijaribu holding/exit adaptive.".format(HORIZON),
    "Hakuna STATE AGE / PERSISTENCE / TRANSITION kwenye representation (vipo doctrine, F-013).",
    "Hakuna ACTIVITY state ingawa ipo (vol+spread tu zinatumika).",
    "Variables zinadhaniwa INDEPENDENT/additive — hakuna interaction/sequencing/memory.",
    "Pair inadhaniwa identity — inaweza kuwa proxy ya spread/liquidity (Principle 32).",
]
MISSING = {
    "activity": "Activity state — IPO kwenye parquet, HAIJATUMIKA. (inaweza kuingizwa sasa)",
    "age": "State age (lifecycle, F-013) — inaweza kuingizwa sasa.",
    "traj": "State trajectory/momentum (F-026) — inaweza kuingizwa sasa.",
    "trans": "Regime transition flag — inaweza kuingizwa sasa.",
    "persist": "State persistence (run-length) — inaweza kuingizwa sasa.",
    "sequencing": "Event sequencing — INAHITAJI infra mpya (haijatekelezwa).",
    "memory": "Market memory (autocorr/path) — INAHITAJI infra mpya.",
    "exec_timing": "Execution timing (intrabar) — INAHITAJI tick-level (nje ya scope hii).",
}


def run(pairs, tfs):
    c = cfg(); rng = np.random.default_rng(0)
    df, no_px = build_df(pairs)
    if no_px:
        print("HITILAFU: state parquet haipo. Endesha market_state_engine.py kwanza.", file=sys.stderr)
        return 1
    print(f"  instances={df.height:,}", flush=True)
    r_base = r2(df, BASE)

    L = ["# Representation Audit — je representation yetu imefikia ukomo? (Phase 15)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | base = {' + '.join(BASE)} | incremental R² (perm-controlled, "
         f"{NREP} reps) | Cramér's V redundancy | outcome = directional net | instances={df.height:,}*\n",
         "> **Principle 33 (Chief):** kushindwa kuthibitisha alpha ≠ kukosekana kwa alpha — ni **failure ya "
         "REPRESENTATION ya sasa** mpaka ithibitishwe vinginevyo. **F-033:** representation inaweza kushindwa "
         "wakati market ina exploitable structure. Kabla ya data/ML/strategy mpya — kagua representation. "
         f"R²(base) = **{r_base:.5f}**. NO ML, NO data mpya.\n"]

    # Q1
    L.append("\n## Q1 — Assumptions zilizofichwa kwenye current representation\n")
    for a in ASSUMPTIONS:
        L.append(f"- {a}")

    # Q2
    L.append("\n## Q2 — Doctrine variables ambazo HAZIJAINGIZWA\n")
    for k, v in MISSING.items():
        flag = "✅ testable sasa" if k in ADDON else "⏳ inahitaji infra"
        L.append(f"- **{k}**: {v}  ({flag})")

    # Q3
    L.append("\n## Q3 — Incremental information juu ya base (perm-controlled)\n")
    L.append("| variable | R²(base+var) | incremental | null incremental | p | inaongeza taarifa? |")
    L.append("|----------|--------------|-------------|------------------|---|--------------------|")
    inc_results = {}
    for v in ADDON:
        inc, nl, p = inc_info(df, BASE, v, rng)
        inc_results[v] = (inc, nl, p)
        adds = inc > nl and p < 0.05
        L.append(f"| {v} | {r_base + inc:.5f} | {inc:+.6f} | {nl:+.6f} | {p:.3f} | {'✅ ndiyo' if adds else '—'} |")
    adders = [v for v in ADDON if inc_results[v][0] > inc_results[v][1] and inc_results[v][2] < 0.05]
    L.append(f"\n→ variables zinazoongeza incremental information halisi: **{', '.join(adders) if adders else 'hakuna'}**.")

    # Q4
    L.append("\n## Q4 — Redundancy (Cramér's V kati ya variables; >0.5 = redundant)\n")
    L.append("| pair ya variables | Cramér's V |")
    L.append("|-------------------|------------|")
    red = []
    for i in range(len(ALLV)):
        for j in range(i + 1, len(ALLV)):
            v = cramers_v(df, ALLV[i], ALLV[j])
            if v > 0.5:
                red.append((ALLV[i], ALLV[j], v))
    for a, b, v in sorted(red, key=lambda t: -t[2]):
        L.append(f"| {a} ↔ {b} | {v:.2f} |")
    if not red:
        L.append("| (hakuna pair yenye V>0.5) | — |")
    L.append(f"\n→ pairs redundant (V>0.5): **{len(red)}** "
             f"({'zibanwe/ziunganishwe' if red else 'variables ni kiasi huru'}).")

    # Q5 — greedy minimal sufficient representation
    L.append("\n## Q5 — Minimal sufficient representation (greedy forward selection)\n")
    remaining = list(ALLV); sel = []; steps = []
    while remaining:
        best = None
        for v in remaining:
            inc, nl, p = inc_info(df, sel, v, rng, nrep=20)
            if p < 0.05 and inc > nl and (best is None or inc - nl > best[1]):
                best = (v, inc - nl, inc, p)
        if best is None:
            break
        sel.append(best[0]); remaining.remove(best[0]); steps.append(best)
    L.append("| hatua | imeongezwa | incremental (− null) | p | representation hadi sasa |")
    L.append("|-------|------------|----------------------|---|--------------------------|")
    for k, (v, gain, inc, p) in enumerate(steps, 1):
        L.append(f"| {k} | {v} | {gain:+.6f} | {p:.3f} | {' + '.join(sel[:k])} |")
    L.append(f"\n→ **minimal sufficient representation: {' + '.join(sel) if sel else '(hakuna variable yenye signal)'}** "
             f"({len(sel)}/{len(ALLV)} variables). Zilizobaki hazina incremental signal -> ni noise/redundant.")

    # VERDICT
    L.append("\n## VERDICT — Phase 15 Representation Audit\n")
    new_signal = [v for v in adders if v in ADDON]
    if new_signal:
        L.append(f"→ ✅ representation ya sasa **HAIJAFIKIA UKOMO**: variables **{', '.join(new_signal)}** "
                 "zinaongeza incremental information halisi (perm-controlled) juu ya base. Hii inaunga mkono "
                 "Principle 33/F-033 — tatizo lilikuwa REPRESENTATION, sio lazima kukosekana kwa alpha. Hatua "
                 "inayofuata: jenga representation iliyopanuliwa (base + hizi) kisha rudia Confirmation (Phase 14) "
                 "— SIO data/ML mpya bado.")
    else:
        L.append("→ ⚠️ variables za ziada za doctrine (age/traj/trans/persist/activity) **hazikuonyesha** "
                 "incremental information juu ya base. Representation inakaribia ukomo kwa variables hizi — "
                 "labda tatizo ni representation FORM (continuous vs discrete) au kweli signal ni dhaifu. "
                 "Inahitaji minimal-sufficient form mpya kabla ya kuhitimisha.")
    L.append("\n*Representation Audit: R² variance-explained, incremental perm-controlled (cardinality null), "
             "Cramér's V redundancy, greedy minimal-sufficient. Principle 33: validation failure = representation "
             "failure hadi ithibitishwe. F-033: representation inaweza kushindwa wakati structure ipo. NO ML, NO "
             "data mpya, NO strategy. Profitable ≠ Tradable Edge.*")
    out = REPO_ROOT / c["paths"]["reports"] / "representation_audit_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)} (adders: {','.join(adders) or 'none'}; "
          f"minimal: {','.join(sel) or 'none'})")
    return 0


def self_test():
    """(1) r2 monotonic + 0 kwa empty. (2) inc_info: var yenye SIGNAL halisi (y inategemea) ->
       inc>null, p<0.05; var ya NOISE -> si significant. (3) cramers_v: duplicate column V≈1."""
    rng = np.random.default_rng(0); n = 12000
    sig_var = rng.choice(["A", "B", "C"], n)
    eff = {"A": 0.0, "B": 3.0, "C": -3.0}
    y = np.array([rng.normal(eff[s], 8) for s in sig_var])
    noise_var = rng.choice(["X", "Y", "Z"], n)
    base = rng.choice(["p", "q"], n)
    df = pl.DataFrame(dict(base=base, sig=sig_var, noise=noise_var, dup=sig_var.copy(), y=y))

    r0 = r2(df, []); r1 = r2(df, ["sig"])
    r2ok = abs(r0) < 1e-9 and r1 > 0.02
    print(f"r2: empty={r0:.4f} sig={r1:.4f} (ok={r2ok})")

    inc_s, nl_s, p_s = inc_info(df, ["base"], "sig", rng, nrep=30)
    inc_n, nl_n, p_n = inc_info(df, ["base"], "noise", rng, nrep=30)
    inc_ok = (inc_s > nl_s and p_s < 0.05) and not (inc_n > nl_n and p_n < 0.05)
    print(f"inc: sig inc={inc_s:.5f} null={nl_s:.5f} p={p_s:.3f} | noise inc={inc_n:.5f} p={p_n:.3f} (ok={inc_ok})")

    v_dup = cramers_v(df, "sig", "dup"); v_noise = cramers_v(df, "sig", "noise")
    cram_ok = v_dup > 0.95 and v_noise < 0.2
    print(f"cramers: dup={v_dup:.2f} noise={v_noise:.2f} (ok={cram_ok})")

    ok = r2ok and inc_ok and cram_ok
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
