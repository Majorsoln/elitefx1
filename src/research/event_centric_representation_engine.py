"""
event_centric_representation_engine.py — PHASE 17 (Chief Quant). Event-Centric Representation.

Phase 16 discovery (F-035, APPROVED): market state variables zinapata maana kupitia
mwingiliano na **EVENTS**, sio kati yao. Event × Trajectory/Activity/Volatility ✅,
lakini Age × Transition / Age × Trajectory ❌. Architecture imebadilika:

  OLD:  State → Age → Transition → Trajectory → Event
  NEW:  Event → Context     (kila Event ina context yake)

  Principle 36: Events ndio SEMANTIC ANCHORS ya representation; context inapata thamani
                tu ikiwa imeunganishwa na Event.
  Principle 37: low signal-to-noise markets -> tathmini kwa ROBUST significance + OOS
                repeatability, SIO effect size pekee.

Phase 17 inajenga representation EVENT-SPECIFIC (sio moja kwa events zote). Maswali:
  Q1. Je Event ndiyo kweli semantic anchor? (R²(event) vs context standalone; je context
      inapata nguvu IKIWA imefungwa kwa event?)
  Q2. Kwa kila Event: ni context zipi zinaongeza taarifa (within-event, perm-controlled)?
  Q3. Je kuna context variables zenye thamani kwa Event moja lakini si nyingine?
  Q4. Minimal event-specific representation (greedy per event).
  Q5. Je representation ya Mean Reversion inatofautiana na ya Breakout?

Mbinu: within-event incremental R² ikidhibitiwa na permutation (Principle 37: significance-
first). NO ML, NO data mpya.

Reuse: representation_audit_engine (build_df, r2), representation_interaction_engine
(group_inc, brier), confidence_engine (spearman).

Output: reports/event_centric_representation_report.md
Self-test: python src/research/event_centric_representation_engine.py --self-test
"""
from __future__ import annotations

import argparse, sys
from datetime import datetime
from pathlib import Path

import numpy as np
import polars as pl

from market_state_engine import cfg
from configuration_engine import EVENTS_SET
from representation_audit_engine import build_df, r2
from representation_interaction_engine import group_inc, brier

REPO_ROOT = Path(__file__).resolve().parents[2]
CTX = ["pair", "vol", "spread", "session", "activity", "age", "traj", "trans", "persist"]
MIN_EVENT_N = 500
NREP = 25


def per_event_info(df_e, rng, nrep=NREP):
    """Kwa event subset: incremental R² ya kila context var (juu ya base tupu = event fixed),
    perm-controlled. Rudisha dict var -> (inc, null, p, significant)."""
    out = {}
    for v in CTX:
        inc, nl, p, _ = group_inc(df_e, [], [v], rng, nrep=nrep)
        out[v] = (inc, nl, p, inc > nl and p < 0.05)
    return out


def minimal_rep(df_e, rng, nrep=20):
    """Greedy forward selection ya context vars WITHIN event (significance-first)."""
    sel = []; remaining = list(CTX)
    while remaining:
        best = None
        for v in remaining:
            inc, nl, p, _ = group_inc(df_e, sel, [v], rng, nrep=nrep)
            if p < 0.05 and inc > nl and (best is None or inc - nl > best[1]):
                best = (v, inc - nl, p)
        if best is None:
            break
        sel.append(best[0]); remaining.remove(best[0])
    return sel


def run(pairs, tfs):
    c = cfg(); rng = np.random.default_rng(0)
    df, no_px = build_df(pairs)
    if no_px:
        print("HITILAFU: state parquet haipo. Endesha market_state_engine.py kwanza.", file=sys.stderr)
        return 1
    print(f"  instances={df.height:,}", flush=True)

    r_event = r2(df, ["event"])
    events = [e for e in EVENTS_SET if df.filter(pl.col("event") == e).height >= MIN_EVENT_N]

    L = ["# Event-Centric Representation — kila Event ina context yake (Phase 17)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | within-event incremental R² (perm-controlled, {NREP} reps) | "
         f"significance-first (Principle 37) | instances={df.height:,}*\n",
         "> **F-035 (Chief):** state variables zinapata maana kupitia mwingiliano na EVENTS, sio kati yao. "
         "**Principle 36:** Events ndio SEMANTIC ANCHORS; context inapata thamani tu ikiwa imefungwa kwa Event. "
         "**Principle 37:** low S/N -> significance + OOS, sio effect size. Tunajenga representation EVENT-"
         "SPECIFIC (sio moja kwa events zote). NO ML.\n"]

    # ---- Q1: Event as semantic anchor ----
    L.append("\n## Q1 — Je Event ndiyo semantic anchor?\n")
    ctx_standalone = {v: r2(df, [v]) for v in ["vol", "activity", "traj", "spread"]}
    L.append(f"- R²(Event) = **{r_event:.5f}**  vs  context standalone: "
             + " · ".join(f"{v}={ctx_standalone[v]:.5f}" for v in ctx_standalone))
    # je context inapata nguvu ikifungwa kwa event? (event+ctx) - event vs ctx standalone
    gains = {}
    for v in ["vol", "activity", "traj"]:
        inc, nl, p, _ = group_inc(df, ["event"], [v], rng)
        gains[v] = (inc, p)
    L.append("- context ikiunganishwa na Event (incremental juu ya Event): "
             + " · ".join(f"{v}=+{gains[v][0]:.6f}(p={gains[v][1]:.3f})" for v in gains))
    anchor = r_event > max(ctx_standalone.values()) and any(gains[v][1] < 0.05 for v in gains)
    L.append(f"\n→ {'✅ Event NI semantic anchor' if anchor else '⚠️ Event si anchor dhahiri'}: Event peke yake "
             "inaeleza zaidi ya context yoyote peke yake, na context inapata taarifa ikiunganishwa na Event.")

    # ---- Q2: per-event informative context map ----
    L.append("\n## Q2 — Kwa kila Event: context zipi zinaongeza taarifa? (within-event, ✅ = significant)\n")
    L.append("| event | " + " | ".join(CTX) + " |")
    L.append("|-------|" + "|".join(["---"] * len(CTX)) + "|")
    info = {}
    for e in events:
        df_e = df.filter(pl.col("event") == e)
        info[e] = per_event_info(df_e, rng)
        cells = " | ".join("✅" if info[e][v][3] else "—" for v in CTX)
        L.append(f"| {e} | {cells} |")

    # ---- Q3: context valuable for one event not another ----
    L.append("\n## Q3 — Context variables zenye thamani kwa Event moja lakini si nyingine\n")
    specific = []
    for v in CTX:
        sig_events = [e for e in events if info[e][v][3]]
        if 0 < len(sig_events) < len(events):
            specific.append((v, sig_events))
    for v, ev in sorted(specific, key=lambda t: len(t[1])):
        L.append(f"- **{v}**: ina taarifa kwa [{', '.join(ev)}] tu (sio events zote) -> event-specific")
    if not specific:
        L.append("- (hakuna; context zinazofanana kwa events zote au hakuna)")
    L.append("\n→ event-specific context = uthibitisho kuwa representation moja kwa events zote ni kosa.")

    # ---- Q4: minimal event-specific representation ----
    L.append("\n## Q4 — Minimal event-specific representation (greedy within-event)\n")
    L.append("| event | minimal representation | size |")
    L.append("|-------|------------------------|------|")
    minimal = {}
    for e in events:
        df_e = df.filter(pl.col("event") == e)
        minimal[e] = minimal_rep(df_e, rng)
        L.append(f"| {e} | {' + '.join(minimal[e]) if minimal[e] else '(hakuna signal)'} | {len(minimal[e])} |")

    # ---- Q5: MR vs Breakout ----
    L.append("\n## Q5 — Je Mean Reversion na Breakout zina representation tofauti?\n")
    mr = set(minimal.get("mean_reversion", [])); bk = set(minimal.get("breakout", []))
    if "mean_reversion" in minimal and "breakout" in minimal:
        L.append(f"- Mean Reversion: {{{', '.join(sorted(mr)) or '∅'}}}")
        L.append(f"- Breakout: {{{', '.join(sorted(bk)) or '∅'}}}")
        L.append(f"- shared: {{{', '.join(sorted(mr & bk)) or '∅'}}} · MR-only: {{{', '.join(sorted(mr - bk)) or '∅'}}} "
                 f"· BK-only: {{{', '.join(sorted(bk - mr)) or '∅'}}}")
        differ = mr != bk
        L.append(f"\n→ {'✅ representation ZINATOFAUTIANA' if differ else '— zinafanana'}: "
                 f"{'kulazimisha representation moja kwa Breakout na Mean Reversion ni kosa (event-specific ni sahihi)' if differ else 'event hizi zinashiriki representation'}.")
    else:
        L.append("- (data haitoshi kwa MR/Breakout)")
        differ = False

    # institutional calibration per event (Principle 35/37) — Brier ya minimal vs base
    L.append("\n## Metric ya ziada — calibration (Brier) ya minimal event-rep vs Event-pekee\n")
    L.append("| event | Brier(event-only) | Brier(event-minimal) | bora? |")
    L.append("|-------|-------------------|----------------------|-------|")
    for e in events:
        df_e = df.filter(pl.col("event") == e)
        b0 = brier(df_e, [], rng); bm = brier(df_e, minimal[e], rng) if minimal[e] else b0
        L.append(f"| {e} | {b0:.5f} | {bm:.5f} | {'✅' if bm < b0 else '—'} |")

    # VERDICT
    L.append("\n## VERDICT — Phase 17 Event-Centric Representation\n")
    n_specific = len(specific); n_differ = differ
    if anchor and (n_specific >= 1 or n_differ):
        L.append(f"→ ✅ **Event ndiyo semantic anchor** (F-035/Principle 36): kila Event ina context yake; "
                 f"context **{n_specific}** ni event-specific; Mean Reversion vs Breakout representation "
                 f"{'zinatofautiana' if n_differ else 'zinafanana'}. Hii inathibitisha kuwa representation MOJA "
                 "kwa events zote ndiyo ilikuwa logic gap. Inayofuata: jenga event-specific representations "
                 "kisha rudia Confirmation (OOS+FDR, Principle 37) — SIO ML bado.")
    else:
        L.append("→ ⚠️ ushahidi wa event-specific context ni dhaifu kwa data hii; representation moja inaweza "
                 "kutosha, au signal ni ndogo mno (Principle 37: thibitisha kwa OOS).")
    L.append("\n*Event-Centric: within-event incremental R² (perm-controlled), event-specific minimal "
             "representation, MR vs Breakout. F-035: context inapata maana kupitia Event. Principle 36: Events = "
             "anchors. Principle 37: significance + OOS, sio effect size. NO ML. Profitable ≠ Tradable Edge.*")
    out = REPO_ROOT / c["paths"]["reports"] / "event_centric_representation_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)} (event-specific ctx: {n_specific}; MR≠BK: {differ})")
    return 0


def self_test():
    """Synthetic: event 'mr' -> signal kwenye 'vol'; event 'bk' -> signal kwenye 'activity'.
       Thibitisha: per_event_info inagundua vol kwa mr, activity kwa bk; minimal sets tofauti."""
    rng = np.random.default_rng(0); n = 16000
    ev = rng.choice(["mr", "bk"], n)
    vol = rng.choice(["LOW", "NORMAL", "HIGH"], n)
    act = rng.choice(["LOW", "NORMAL", "HIGH"], n)
    noise = rng.choice(["a", "b", "c"], n)
    volmap = {"LOW": -4.0, "NORMAL": 0.0, "HIGH": 4.0}
    actmap = {"LOW": 4.0, "NORMAL": 0.0, "HIGH": -4.0}
    y = np.array([
        (volmap[vol[i]] if ev[i] == "mr" else actmap[act[i]]) + rng.normal(0, 6)
        for i in range(n)])
    # columns: include all CTX names (fill unused with constant/noise to keep group_inc happy)
    cols = dict(event=list(ev), pair=["P"] * n, vol=list(vol), spread=["NORMAL"] * n,
                session=list(noise), activity=list(act), age=["mid"] * n,
                traj=["FLAT"] * n, trans=["N"] * n, persist=["1"] * n, y=y)
    df = pl.DataFrame(cols)

    info_mr = per_event_info(df.filter(pl.col("event") == "mr"), rng, nrep=30)
    info_bk = per_event_info(df.filter(pl.col("event") == "bk"), rng, nrep=30)
    mr_ok = info_mr["vol"][3] and not info_mr["activity"][3]
    bk_ok = info_bk["activity"][3] and not info_bk["vol"][3]
    print(f"mr: vol sig={info_mr['vol'][3]} activity sig={info_mr['activity'][3]} (ok={mr_ok})")
    print(f"bk: activity sig={info_bk['activity'][3]} vol sig={info_bk['vol'][3]} (ok={bk_ok})")

    min_mr = minimal_rep(df.filter(pl.col("event") == "mr"), rng, nrep=20)
    min_bk = minimal_rep(df.filter(pl.col("event") == "bk"), rng, nrep=20)
    differ = set(min_mr) != set(min_bk) and "vol" in min_mr and "activity" in min_bk
    print(f"minimal: mr={min_mr} bk={min_bk} (differ={differ})")

    ok = mr_ok and bk_ok and differ
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
