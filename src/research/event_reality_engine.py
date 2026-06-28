"""
event_reality_engine.py — PHASE 12 (Chief Quant). Event Reality Framework.

Phase 11 (Edge Reality Test) verdict: aggregate edge HAIJATHIBITISHWA kuzidi random
(H0); na randomized-time ilionyesha persistence HALISI ni MBAYA kuliko random ->
**F-029 (APPROVED): edge decay ni matokeo ya market NON-STATIONARITY, sio sampling
noise tu.** mean_reversion ilionekana kuvutia (P(obs>random)=100%) LAKINI Chief
amekataa kuruka kwenye mean_reversion-only: hiyo ni subgroup (hatari ya small-sample
/ multiple comparisons — kosa lile lile la CCS).

Badala yake: **Event Reality Framework** — pima EVENTS ZOTE kwa methodology ileile.
**Principle 29:** kila Event ni STATISTICAL HYPOTHESIS, sio trading signal. Tunajenga
Opportunity juu ya events zilizothibitishwa kisayansi tu.

Maswali (Chief):
  Q1. Kwa kila event: null (random-direction) + bootstrap + permutation.
  Q2. Bayesian probability kwamba "Edge Exists" kwa kila event (sio p-value tu).
  Q3. Je pair fulani ndiyo inabeba event? (pair × event).
  Q4. Je event survival/edge inategemea market state? (event × volatility state).
  Q5. Je events mbili zikichanganywa zinazalisha edge? (combo vs solo).

Null = RANDOM DIRECTION (d -> ±1 random): hupima kama MWELEKEO wa event una skill
zaidi ya bahati, net ya spread. Bayesian P(edge>0) = Φ(EV/SE) (flat prior). NO ML.

Reuse: market_state_engine (cfg, pip, state_path-via latent_structure), event_library
(EVENTS_ALL), configuration_engine (EVENTS_SET, VERT), context_value (HORIZON).

Output: reports/event_reality_report.md
Self-test: python src/research/event_reality_engine.py --self-test
"""
from __future__ import annotations

import argparse, math, sys
from collections import defaultdict
from datetime import datetime
from itertools import combinations
from pathlib import Path

import numpy as np
import polars as pl

from market_state_engine import cfg, pip
from latent_structure import state_path
from event_library import EVENTS_ALL
from configuration_engine import EVENTS_SET, VERT
from context_value import HORIZON

REPO_ROOT = Path(__file__).resolve().parents[2]
TFS = ["H1", "H2", "H4", "D1"]
MIN_N = 300           # sample ya chini kwa event/sub-group ili kuripoti
NREP = 300            # null/bootstrap repetitions
VOL_STATES = ["LOW", "NORMAL", "HIGH"]


def _phi(z):
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def event_real(fwd, spr, d, rng, nrep=NREP):
    """Reality test ya event moja. net = d·fwd − spr.
      observed EV, SE, Bayesian P(edge>0)=Φ(EV/SE), bootstrap 95% CI,
      null (random-direction) p = P(null_mean ≥ obs)."""
    fwd = np.asarray(fwd, float); spr = np.asarray(spr, float); d = np.asarray(d, float)
    net = d * fwd - spr
    n = len(net); ev = float(net.mean())
    se = float(net.std(ddof=1) / math.sqrt(n)) if n > 1 else float("nan")
    bayes = _phi(ev / se) if se and se > 0 else float("nan")
    boot = np.array([net[rng.integers(0, n, n)].mean() for _ in range(nrep)])
    lo, hi = np.percentile(boot, [2.5, 97.5])
    nulls = np.array([(rng.choice((-1.0, 1.0), n) * fwd - spr).mean() for _ in range(nrep)])
    p = (1 + int(np.sum(nulls >= ev))) / (nrep + 1)
    return dict(n=n, ev=ev, se=se, bayes=bayes, lo=float(lo), hi=float(hi),
                p=p, null_mean=float(nulls.mean()))


def proven(st):
    """Edge 'imethibitishwa' kwa triple criterion: Bayesian>0.95 NA p<0.05 NA CI ya chini>0."""
    return (np.isfinite(st["bayes"]) and st["bayes"] > 0.95 and st["p"] < 0.05 and st["lo"] > 0)


def collect_events(pairs):
    """Rudisha per-event arrays (fwd, spr, d, sym, vol) + combo nets za bar-level."""
    ev_fwd = defaultdict(list); ev_spr = defaultdict(list); ev_d = defaultdict(list)
    ev_sym = defaultdict(list); ev_vol = defaultdict(list)
    combo = defaultdict(list)
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
            vol = df["volatility_state"].to_list()
            n = len(close)
            sig = {ev: EVENTS_ALL[ev](close, high, low) for ev in EVENTS_SET}
            for i in range(n):
                if i + VERT >= n or i + HORIZON >= n or not (atr[i] > 0):
                    continue
                fwd = close[i + HORIZON] - close[i]; sp = spr[i]
                fired = []
                for ev in EVENTS_SET:
                    s = sig[ev][i]
                    if s != 0:
                        d = int(s); fired.append((ev, d))
                        ev_fwd[ev].append(fwd); ev_spr[ev].append(sp); ev_d[ev].append(d)
                        ev_sym[ev].append(sym); ev_vol[ev].append(vol[i])
                for (a, da), (b, db) in combinations(fired, 2):
                    if da == db:
                        combo[tuple(sorted((a, b)))].append(da * fwd - sp)
        print(f"  {sym}: done", flush=True)
    return ev_fwd, ev_spr, ev_d, ev_sym, ev_vol, combo, no_px


def run(pairs, tfs):
    c = cfg(); rng = np.random.default_rng(0)
    ev_fwd, ev_spr, ev_d, ev_sym, ev_vol, combo, no_px = collect_events(pairs)
    if no_px:
        print("HITILAFU: OHLC/state parquet haipo. Endesha market_state_engine.py kwanza.", file=sys.stderr)
        return 1

    # per-event reality
    stats = {}
    for ev in EVENTS_SET:
        if len(ev_fwd[ev]) >= MIN_N:
            stats[ev] = event_real(np.array(ev_fwd[ev]), np.array(ev_spr[ev]), np.array(ev_d[ev]), rng)

    L = ["# Event Reality Framework — ni events zipi zipo KWELI kitakwimu? (Phase 12)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | null (random-direction) + bootstrap + permutation ({NREP} reps) "
         f"+ Bayesian | outcome forward {HORIZON}b net spread | min N={MIN_N}*\n",
         "> **Principle 29 (Chief):** kila Event ni STATISTICAL HYPOTHESIS, sio trading signal. Tunajenga "
         "Opportunity juu ya events zilizothibitishwa tu. **F-029 (APPROVED):** edge decay = market non-"
         "stationarity. Chief amekataa mean_reversion-only (subgroup/multiple-comparisons). Hapa events ZOTE "
         "kwa methodology ileile. Null = random direction (skill ya mwelekeo net ya spread). Bayesian "
         "P(edge>0)=Φ(EV/SE). NO ML. Profitable ≠ Tradable Edge.\n"]

    # Q1 + Q2
    L.append("\n## Q1+Q2 — kila event: null + bootstrap + permutation + Bayesian P(edge exists)\n")
    L.append("| event | N | EV [95% CI boot] | null EV (rand-dir) | perm p | Bayesian P(edge>0) | proven? |")
    L.append("|-------|---|------------------|--------------------|--------|--------------------|---------|")
    n_proven = 0
    for ev in EVENTS_SET:
        if ev not in stats:
            L.append(f"| {ev} | <{MIN_N} | — | — | — | — | — |"); continue
        st = stats[ev]; pv = proven(st); n_proven += 1 if pv else 0
        L.append(f"| {ev} | {st['n']:,} | {st['ev']:+.3f} [{st['lo']:+.2f},{st['hi']:+.2f}] | "
                 f"{st['null_mean']:+.3f} | {st['p']:.3f} | {st['bayes']*100:.0f}% | "
                 f"{'✅' if pv else '—'} |")
    L.append(f"\n→ events zilizothibitishwa (Bayesian>95% NA p<0.05 NA CI-low>0): **{n_proven}/{len(stats)}**.")

    # Q3 — pair × event
    L.append("\n## Q3 — Je pair fulani inabeba event? (EV + Bayesian kwa pair × event)\n")
    for ev in EVENTS_SET:
        if ev not in stats:
            continue
        fwd = np.array(ev_fwd[ev]); spr = np.array(ev_spr[ev]); d = np.array(ev_d[ev]); sy = np.array(ev_sym[ev])
        rows = []
        for s in sorted(set(sy)):
            m = sy == s
            if m.sum() < MIN_N:
                continue
            stp = event_real(fwd[m], spr[m], d[m], rng, nrep=120)
            rows.append((s, stp))
        if not rows:
            continue
        rows.sort(key=lambda r: r[1]["ev"], reverse=True)
        cells = " · ".join(f"{s}={st['ev']:+.2f}(P{st['bayes']*100:.0f})" for s, st in rows[:6])
        carriers = [s for s, st in rows if proven(st)]
        L.append(f"- **{ev}**: {cells}  →  zilizothibitishwa: {', '.join(carriers) if carriers else 'hakuna'}")
    L.append("\n*(P = Bayesian P(edge>0)%. Inaonyesha kama event ni ya pair maalum au ya jumla.)*")

    # Q4 — event × market state
    L.append("\n## Q4 — Je event edge inategemea market state? (EV kwa volatility state)\n")
    L.append("| event | LOW | NORMAL | HIGH |")
    L.append("|-------|-----|--------|------|")
    for ev in EVENTS_SET:
        if ev not in stats:
            continue
        fwd = np.array(ev_fwd[ev]); spr = np.array(ev_spr[ev]); d = np.array(ev_d[ev]); vl = np.array(ev_vol[ev])
        cells = []
        for vs in VOL_STATES:
            m = vl == vs
            if m.sum() < MIN_N:
                cells.append("—"); continue
            net = d[m] * fwd[m] - spr[m]
            cells.append(f"{net.mean():+.2f}")
        L.append(f"| {ev} | {cells[0]} | {cells[1]} | {cells[2]} |")
    L.append("\n→ EV inayobadilika sana kati ya states = event-edge inategemea market state (state-dependent).")

    # Q5 — combos
    L.append("\n## Q5 — Je events mbili zikichanganywa zinazalisha edge? (combo vs solo)\n")
    L.append("| combo (A+B, same dir) | N | combo EV | solo A EV | solo B EV | combo > best solo? |")
    L.append("|------------------------|---|----------|-----------|-----------|--------------------|")
    n_combo_win = 0; n_combo_tot = 0
    for (a, b), nets in sorted(combo.items(), key=lambda kv: len(kv[1]), reverse=True):
        if len(nets) < MIN_N or a not in stats or b not in stats:
            continue
        n_combo_tot += 1
        cev = float(np.mean(nets)); aev = stats[a]["ev"]; bev = stats[b]["ev"]
        best = max(aev, bev); win = cev > best
        n_combo_win += 1 if win else 0
        L.append(f"| {a}+{b} | {len(nets):,} | {cev:+.3f} | {aev:+.3f} | {bev:+.3f} | "
                 f"{'✅' if win else '—'} |")
    L.append(f"\n→ combos zinazozidi best-solo: **{n_combo_win}/{n_combo_tot}** "
             f"({'mwingiliano una thamani' if n_combo_tot and n_combo_win > n_combo_tot/2 else 'mwingiliano dhaifu kwa wengi'}).")

    # VERDICT
    L.append("\n## VERDICT — Phase 12 Event Reality Framework\n")
    proven_list = [ev for ev in stats if proven(stats[ev])]
    if proven_list:
        L.append(f"→ events **ZILIZOTHIBITISHWA kitakwimu** (zaidi ya random-direction, Bayesian>95%, CI-low>0): "
                 f"**{', '.join(proven_list)}** ({len(proven_list)}/{len(stats)}). Hizi PEKEE ndizo zinaruhusiwa "
                 "kuendelea kwenye Context/Opportunity Engine (Principle 29: event = hypothesis iliyothibitishwa). "
                 "Nyingine zinabaki hypotheses zisizothibitishwa — HAZIINGII Opportunity Engine bado.")
    else:
        L.append("→ ⚠️ **HAKUNA event iliyothibitishwa** kuzidi random-direction kwa triple criterion. Hii "
                 "inaunga mkono F-029/H0: 'edge' nyingi ni noise / non-stationarity. Opportunity Engine bado "
                 "imezuiwa (Principle 28). Inahitaji representation/context bora au event mpya.")
    L.append("\n*Event Reality: null=random-direction (skill ya mwelekeo net ya spread), bootstrap CI, "
             "permutation p, Bayesian P(edge>0)=Φ(EV/SE). proven = Bayesian>95% NA p<0.05 NA CI-low>0. "
             "Principle 29: event = statistical hypothesis. F-029: decay = non-stationarity. Q3 pair-carrier, "
             "Q4 state-dependence, Q5 combos. NO ML. Profitable ≠ Tradable Edge.*")
    out = REPO_ROOT / c["paths"]["reports"] / "event_reality_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)} (events proven: {n_proven}/{len(stats)})")
    return 0


def self_test():
    """(1) event_real: directional skill (d=sign(fwd)) -> EV>0, Bayesian~1, p ndogo, proven.
       (2) noise (d random) -> EV≈−spr, Bayesian chini, si proven.
       (3) combo: intersection yenye skill kubwa zaidi -> combo EV > solo."""
    rng = np.random.default_rng(0); n = 6000
    fwd = rng.normal(0, 10, n); spr = np.full(n, 1.0)

    # (1) REAL: direction ina skill (inafuata ishara ya fwd mara nyingi)
    d_real = np.where(rng.random(n) < 0.65, np.sign(fwd), -np.sign(fwd))
    st_r = event_real(fwd, spr, d_real, rng, nrep=200)
    real_ok = st_r["ev"] > 0 and st_r["bayes"] > 0.95 and st_r["p"] < 0.05 and proven(st_r)
    print(f"REAL: EV={st_r['ev']:+.2f} bayes={st_r['bayes']*100:.0f}% p={st_r['p']:.3f} proven={proven(st_r)}")

    # (2) NOISE: direction random
    d_noise = rng.choice((-1.0, 1.0), n)
    st_n = event_real(fwd, spr, d_noise, rng, nrep=200)
    noise_ok = not proven(st_n) and st_n["bayes"] < 0.95
    print(f"NOISE: EV={st_n['ev']:+.2f} bayes={st_n['bayes']*100:.0f}% p={st_n['p']:.3f} proven={proven(st_n)}")

    # (3) combo: subset (mf. nusu ya kwanza) yenye skill kubwa zaidi
    d_combo = d_real.copy()
    strong = np.arange(n) < n // 2
    d_combo[strong] = np.where(rng.random(strong.sum()) < 0.85, np.sign(fwd[strong]), -np.sign(fwd[strong]))
    combo_ev = float((d_combo[strong] * fwd[strong] - spr[strong]).mean())
    solo_ev = st_r["ev"]
    combo_ok = combo_ev > solo_ev
    print(f"combo: combo EV={combo_ev:+.2f} > solo EV={solo_ev:+.2f} (ok={combo_ok})")

    ok = real_ok and noise_ok and combo_ok
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default=None)
    ap.add_argument("--reps", type=int, default=None)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    global NREP
    if a.reps:
        NREP = a.reps
    c = cfg()
    pairs = [a.symbol] if a.symbol else c["pairs"]
    return run(pairs, None)


if __name__ == "__main__":
    raise SystemExit(main())
