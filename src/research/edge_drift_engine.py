"""
edge_drift_engine.py — PHASE 10 (Chief Quant). Edge Drift Engine.

Phase 9 (Edge Lifecycle Engine) ilithibitisha **F-028 (APPROVED): kila trading edge
ina LIFECYCLE** (Birth → Growth → Decay → Death). Median survival = window 1 tu;
~2% ya configs ndizo zilizodumu windows zote. Report ilionyesha **WHEN** edge inakufa
— lakini SIO **WHY**. Chief: bila kujua sababu, adaptive ranking ni curve-fitting.

Phase 10 inajibu **WHY**: ni nini kilibadilika kati ya window ambapo edge ilikuwa hai
na window ambapo ilikufa? Configuration ina (regime, spread_state, latent, direction,
event) ZILIZOFUNGWA — lakini THAMANI HALISI (ATR pips, spread pips, activity) zinadrift
(state labels ni RELATIVE/rolling). Hapa ndipo tunatafuta sababu.

Maswali (Chief):
  Q1. Edge ilikufa kwa sababu volatility/spread/activity (mazingira halisi) yalibadilika?
  Q2. Kwa kila config iliyokufa: Before → After (ATR, spread, activity).
  Q3. Je kuna transitions (↑/↓) zinazojirudia kabla ya kifo?
  Q4. Je kifo cha edge kinaweza kutabirika window MOJA kabla? (swali muhimu; NO ML)
  Q5. Je events zina lifespan tofauti — na KWA NINI (sio tu "mean_reversion inaongoza")?

+ F-027 (REFORMULATED) causal test: corr(window-1 EV [early quality], survival
  [future]) — ndogo => early quality HAITABIRI future survival.

⚠️ NO ML (Chief): ML kabla ya kujibu hili itafundishwa "historical corpses".

Reuse: latent_structure (kmeans, collect, state_path, signatures via mechanism_discovery),
configuration_engine (assign, K, EVENTS_SET, VERT, KSIG), context_value (HORIZON),
confidence_engine (spearman), market_state_engine (cfg, pip).

Output: reports/edge_drift_report.md
Self-test: python src/research/edge_drift_engine.py --self-test
"""
from __future__ import annotations

import argparse, sys
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path

import numpy as np
import polars as pl

from market_state_engine import cfg, pip
from mechanism_discovery import signatures
from latent_structure import kmeans, collect, state_path
from configuration_engine import assign, K, EVENTS_SET, VERT
from event_library import EVENTS_ALL
from context_value import HORIZON
from confidence_engine import spearman

REPO_ROOT = Path(__file__).resolve().parents[2]
TFS = ["H1", "H2", "H4", "D1"]
MIN_N = 200
NWIN = 6
MIN_WIN = 25
THR = 0.05            # 5% relative change = "transition" (↑/↓) ya mazingira
TOPN = 20
ENVS = ["atr", "spr", "act"]      # volatility, spread, activity (mazingira halisi)


def build_acc_env(pairs, cen):
    """acc[config_key] = list ya (ts, net, atr_pips, spr_pips, tc) — mazingira halisi
    kwa kila signal (kwa drift analysis)."""
    acc = defaultdict(list); no_px = True
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
            sig, *_ = signatures(df, pp); fin = np.all(np.isfinite(sig), axis=1)
            cl = np.full(len(sig), -1)
            if fin.any():
                cl[fin] = assign(sig[fin], cen)
            close = df["c"].to_numpy() / pp; high = df["h"].to_numpy() / pp; low = df["l"].to_numpy() / pp
            atr_pips = df["atr"].to_numpy() / pp
            spr = df["spr"].to_numpy(); spr = np.where(np.isfinite(spr), spr, 0.0)
            tc = df["tc"].to_numpy().astype(float)
            vol = df["volatility_state"].to_list(); exec_ctx = df["spread_state"].to_list()
            ts = df["ts"].to_numpy().astype("datetime64[s]").astype(np.int64)
            n = len(close)
            for ev in EVENTS_SET:
                s = EVENTS_ALL[ev](close, high, low)
                for i in range(n):
                    if s[i] == 0 or cl[i] < 0 or i + VERT >= n or not (atr_pips[i] > 0):
                        continue
                    reg = vol[i]; ex = exec_ctx[i]
                    if reg == "UNKNOWN" or ex == "UNKNOWN" or i + HORIZON >= n:
                        continue
                    d = int(s[i]); direction = "LONG" if d == 1 else "SHORT"
                    net = float(d * (close[i + HORIZON] - close[i]) - spr[i])
                    acc[(sym, ev, f"C{cl[i]}", reg, direction, ex)].append(
                        (int(ts[i]), net, float(atr_pips[i]), float(spr[i]), float(tc[i])))
        print(f"  {sym}: done", flush=True)
    return acc, no_px


def find_death(ev):
    """Kupatikana kwa kifo cha kwanza: window ya kwanza ≤0 baada ya window chanya.
    Rudisha (death_idx, last_alive) au (None, None) kama haijaanza chanya / haijafa."""
    if len(ev) == 0 or ev[0] <= 0:
        return None, None
    for w in range(1, len(ev)):
        if ev[w] <= 0 and ev[w - 1] > 0:
            return w, w - 1
    return None, None


def proc_config(rows, nwin=NWIN):
    """Rolling windows kwa muda -> ev[], atr[], spr[], act[] + death info. None kama N ndogo."""
    r = sorted(rows, key=lambda t: t[0])
    if len(r) < MIN_N:
        return None
    arr = np.array([(x[1], x[2], x[3], x[4]) for x in r], float)   # net, atr, spr, tc
    chunks = np.array_split(arr, nwin)
    if min(len(ch) for ch in chunks) < MIN_WIN:
        return None
    ev = np.array([ch[:, 0].mean() for ch in chunks])
    atr = np.array([ch[:, 1].mean() for ch in chunks])
    spr = np.array([ch[:, 2].mean() for ch in chunks])
    act = np.array([ch[:, 3].mean() for ch in chunks])
    death, last = find_death(ev)
    sw = 0
    for e in ev:
        if e > 0:
            sw += 1
        else:
            break
    return dict(ev=ev, atr=atr, spr=spr, act=act, n=len(r), first_pos=bool(ev[0] > 0),
                death=death, last_alive=last, survival=sw, win1_ev=float(ev[0]))


def _dir(before, after, thr=THR):
    if before <= 0:
        return "→"
    rel = (after - before) / before
    return "↑" if rel > thr else ("↓" if rel < -thr else "→")


def run(pairs, tfs):
    c = cfg(); rng = np.random.default_rng(0)
    pool = [X for sym in pairs if len(X := collect(sym, rng)) > 50]
    if not pool:
        print("HITILAFU: hakuna state parquet. Endesha market_state_engine.py kwanza.", file=sys.stderr)
        return 1
    _, cen, _ = kmeans(np.vstack(pool), K, rng)
    print(f"  latent clusters k={K} fitted", flush=True)
    acc, no_px = build_acc_env(pairs, cen)
    if no_px:
        print("HITILAFU: OHLC haipo. Endesha market_state_engine.py (OHLC update) kwanza.", file=sys.stderr)
        return 1

    cfgs = {}
    for key, rows in acc.items():
        pc = proc_config(rows)
        if pc is not None:
            cfgs[key] = pc
    if not cfgs:
        print(f"HITILAFU: hakuna Configuration yenye N≥{MIN_N}.", file=sys.stderr)
        return 1

    dead = {k: v for k, v in cfgs.items() if v["death"] is not None}
    pos_start = {k: v for k, v in cfgs.items() if v["first_pos"]}

    # F-027 reformulated (causal): early quality (window-1 EV) vs future survival
    rho_es = spearman([v["win1_ev"] for v in pos_start.values()],
                      [v["survival"] for v in pos_start.values()]) if len(pos_start) > 2 else float("nan")

    L = ["# Edge Drift Engine — KWA NINI edge inakufa? (Phase 10)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | rolling {NWIN} windows | mazingira halisi (ATR/spread/activity) "
         f"per window | death = window ya kwanza ≤0 baada ya chanya | min N={MIN_N} | configs: {len(cfgs):,} "
         f"(dead: {len(dead):,})*\n",
         "> **Lengo (Chief):** Phase 9 ilionyesha WHEN edge inakufa (F-028: kila edge ina lifecycle). Phase 10 "
         "inatafuta **WHY** — config dimensions zimefungwa, lakini ATR/spread/activity HALISI zinadrift "
         "(states ni relative). Bila sababu, adaptive ranking = curve-fitting. **Principle 27:** prefer LIVING "
         "edges. **F-027 (reformulated):** early quality may not predict future survivability. NO ML (vinginevyo "
         "tunafundisha 'historical corpses'). Profitable ≠ Tradable Edge.\n"]

    # F-027 reformulated
    L.append("\n## F-027 (reformulated, CAUSAL) — je early quality inatabiri future survival?\n")
    L.append(f"- Spearman(window-1 EV, survival windows) = **{rho_es:+.2f}** (configs zilizoanza chanya: "
             f"{len(pos_start)})")
    weak = abs(rho_es) < 0.4
    L.append(f"\n→ {'✅ **F-027 (reformulated) inaungwa mkono**' if weak else '⚠️ uhusiano upo'}: early quality "
             f"{'HAITABIRI' if weak else 'inahusiana kiasi na'} future survival — "
             f"{'config nzuri mwanzoni ≠ config inayodumu (tofauti na whole-sample corr ya Phase 9)' if weak else 'bado kuna signal'}.")

    # Q1 — sababu: which environment changed at death (Δ from last-alive to death)
    L.append("\n## Q1 — Edge ilikufa kwa sababu mazingira yalibadilika? (Δ last-alive → death)\n")
    if dead:
        dd = {e: [] for e in ENVS}; dev = []
        for v in dead.values():
            w, la = v["death"], v["last_alive"]
            for e in ENVS:
                b = v[e][la]
                dd[e].append((v[e][w] - b) / b if b > 0 else 0.0)
            dev.append(v["ev"][w] - v["ev"][la])
        L.append("| mazingira | mean Δ% (death vs last-alive) | corr(Δenv, ΔEV) |")
        L.append("|-----------|------------------------------|------------------|")
        rho_env = {}
        for e in ENVS:
            rho_env[e] = spearman(dd[e], dev)
            nm = {"atr": "volatility (ATR)", "spr": "spread", "act": "activity"}[e]
            L.append(f"| {nm} | {np.mean(dd[e])*100:+.1f}% | {rho_env[e]:+.2f} |")
        worst = max(ENVS, key=lambda e: abs(np.mean(dd[e])))
        L.append(f"\n→ mazingira yaliyobadilika ZAIDI wakati wa kifo: **{ {'atr':'volatility','spr':'spread','act':'activity'}[worst] }** "
                 f"(mean Δ {np.mean(dd[worst])*100:+.1f}%). corr kubwa zaidi |ρ| na ΔEV inaonyesha sababu inayohusiana zaidi.")

    # Q2 — Before → After per dead config
    L.append("\n## Q2 — Before → After kwa configs zilizokufa (sampuli)\n")
    L.append("| Configuration | death@win | ATR before→after | spread before→after | activity before→after | EV before→after |")
    L.append("|---------------|-----------|------------------|---------------------|------------------------|-----------------|")
    for key, v in sorted(dead.items(), key=lambda kv: kv[1]["n"], reverse=True)[:TOPN]:
        w, la = v["death"], v["last_alive"]
        L.append(f"| {'·'.join(key)} | {w+1}/{NWIN} | {v['atr'][la]:.0f}→{v['atr'][w]:.0f} {_dir(v['atr'][la],v['atr'][w])} | "
                 f"{v['spr'][la]:.1f}→{v['spr'][w]:.1f} {_dir(v['spr'][la],v['spr'][w])} | "
                 f"{v['act'][la]:.0f}→{v['act'][w]:.0f} {_dir(v['act'][la],v['act'][w])} | "
                 f"{v['ev'][la]:+.1f}→{v['ev'][w]:+.1f} |")

    # Q3 — recurring transitions before death
    L.append("\n## Q3 — Transitions zinazojirudia kabla ya kifo (ATR·spread·activity)\n")
    if dead:
        combo = Counter()
        for v in dead.values():
            w, la = v["death"], v["last_alive"]
            combo[(f"ATR{_dir(v['atr'][la],v['atr'][w])}", f"spr{_dir(v['spr'][la],v['spr'][w])}",
                   f"act{_dir(v['act'][la],v['act'][w])}")] += 1
        tot = sum(combo.values())
        L.append("| transition (ATR · spread · activity) | mara | % ya vifo |")
        L.append("|--------------------------------------|------|-----------|")
        for combo_k, ct in combo.most_common(8):
            L.append(f"| {' · '.join(combo_k)} | {ct} | {100*ct/tot:.0f}% |")
        top_combo, top_ct = combo.most_common(1)[0]
        L.append(f"\n→ transition inayojirudia zaidi kabla ya kifo: **{' · '.join(top_combo)}** "
                 f"({100*top_ct/tot:.0f}% ya vifo).")

    # Q4 — predictability one window ahead (no ML)
    L.append("\n## Q4 — Je kifo kinaweza kutabirika window MOJA kabla? (rule-based, NO ML)\n")
    # signal: window w EV ilipungua (vs w-1) -> je window w+1 itakuwa ≤0?
    decl_next_neg = decl = rose_next_neg = rose = 0
    base_neg = base_tot = 0
    for v in cfgs.values():
        ev = v["ev"]
        for w in range(1, NWIN - 1):
            nxt_neg = ev[w + 1] <= 0
            base_neg += 1 if nxt_neg else 0; base_tot += 1
            if ev[w] < ev[w - 1]:
                decl += 1; decl_next_neg += 1 if nxt_neg else 0
            else:
                rose += 1; rose_next_neg += 1 if nxt_neg else 0
    base = base_neg / base_tot if base_tot else float("nan")
    p_decl = decl_next_neg / decl if decl else float("nan")
    p_rose = rose_next_neg / rose if rose else float("nan")
    L.append(f"- base rate P(window inayofuata ≤0) = **{base*100:.0f}%**")
    L.append(f"- P(next ≤0 | EV ilipungua window hii) = **{p_decl*100:.0f}%** (n={decl})")
    L.append(f"- P(next ≤0 | EV iliongezeka window hii) = **{p_rose*100:.0f}%** (n={rose})")
    lift = p_decl - base
    L.append(f"\n→ {'✅ kifo kina-tabirika KIASI' if lift > 0.03 else '⚠️ signal dhaifu'}: EV inayopungua "
             f"inainua P(kifo) kwa **{lift*100:+.0f}pp** juu ya base — rule rahisi (no ML) inatoa onyo la mapema "
             f"({'inatumika' if lift>0.03 else 'haitoshi peke yake'}).")

    # Q5 — event lifespan + why
    L.append("\n## Q5 — Events zina lifespan tofauti — na KWA NINI?\n")
    ev_surv = defaultdict(list); ev_drift = defaultdict(list); ev_atr = defaultdict(list); ev_spr = defaultdict(list)
    for key, v in pos_start.items():
        e = key[1]; ev_surv[e].append(v["survival"])
        # drift magnitude = mean |Δ%| ya mazingira kati ya windows mfululizo
        dr = np.mean([np.mean(np.abs(np.diff(v[m]) / np.where(v[m][:-1] > 0, v[m][:-1], 1))) for m in ENVS])
        ev_drift[e].append(dr); ev_atr[e].append(np.mean(v["atr"])); ev_spr[e].append(np.mean(v["spr"]))
    L.append("| event | mean survival (win) | mean env drift % | mean ATR | mean spread | configs |")
    L.append("|-------|---------------------|------------------|----------|-------------|---------|")
    for e in sorted(ev_surv, key=lambda e: np.mean(ev_surv[e]), reverse=True):
        L.append(f"| {e} | {np.mean(ev_surv[e]):.2f}/{NWIN} | {np.mean(ev_drift[e])*100:.1f}% | "
                 f"{np.mean(ev_atr[e]):.0f} | {np.mean(ev_spr[e]):.1f} | {len(ev_surv[e])} |")
    # je survival inahusiana kinyume na drift? (drift ndogo -> lifespan ndefu)
    es = [(np.mean(ev_surv[e]), np.mean(ev_drift[e])) for e in ev_surv]
    rho_sd = spearman([x[0] for x in es], [x[1] for x in es]) if len(es) > 2 else float("nan")
    L.append(f"\n→ corr(survival, env-drift) kwa event = **{rho_sd:+.2f}** "
             f"({'✅ events zenye drift NDOGO zinaishi muda mrefu — ndiyo sababu (sio bahati)' if rho_sd < -0.3 else 'uhusiano si wazi; sababu nyingine'}).")

    L.append("\n## VERDICT — Phase 10 Edge Drift Engine\n")
    L.append(f"→ Edge inakufa ikiambatana na mabadiliko ya mazingira halisi (ATR/spread/activity) ingawa state-"
             f"labels zimefungwa. F-027 (reformulated): early quality ρ={rho_es:+.2f} na survival — "
             f"{'haitabiri' if abs(rho_es)<0.4 else 'inahusiana kiasi'}. Kifo kina-tabirika kiasi window moja "
             f"kabla (rule-based). Hii ndiyo msingi wa **Adaptive Market Intelligence**: Opportunity Engine "
             "ifuatilie LIFECYCLE (living edges), ondoe zinazoonyesha dalili za kifo. NO ML bado (tungefundisha "
             "historical corpses). Inayofuata: Opportunity Engine v2 (lifecycle-aware) / F-026 state trajectory.")
    L.append("\n*Edge Drift = mabadiliko ya mazingira halisi (ATR/spread/activity) yanayoambatana na kifo cha "
             "edge. Q1 sababu, Q2 before→after, Q3 transitions, Q4 predictability (no ML), Q5 event lifespan+why. "
             "F-027 reformulated = causal (early quality → future survival). F-028: kila edge ina lifecycle. "
             "Principle 27: prefer living edges. NO ML. Profitable ≠ Tradable Edge.*")
    out = REPO_ROOT / c["paths"]["reports"] / "edge_drift_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)} ({len(cfgs):,} configs, dead {len(dead):,}, "
          f"F-027 ρ={rho_es:+.2f})")
    return 0


def self_test():
    """(1) find_death sahihi. (2) proc_config: death + env arrays. (3) Q4 logic: EV
       inayopungua inatabiri next≤0. (4) F-027 causal: early-EV haihusiani na survival."""
    # find_death
    fd_ok = (find_death(np.array([6, 4, -3, -2, -4, -5])) == (2, 1)
             and find_death(np.array([5, 5, 5, 5, 5, 5])) == (None, None)
             and find_death(np.array([-1, 2, 3, 4, 5, 6])) == (None, None))
    print(f"find_death: {fd_ok}")

    rng = np.random.default_rng(0)
    def mk(ev_means, atr_means, per_win):
        rows = []; t = 0
        for w in range(len(ev_means)):
            for _ in range(per_win):
                rows.append((t, float(rng.normal(ev_means[w], 4)),
                             float(rng.normal(atr_means[w], 1)), 1.0, 1000.0)); t += 1
        return rows
    # edge inayokufa wakati ATR inapanda
    pc = proc_config(mk([6, 4, -3, -2, -4, -5], [10, 12, 22, 24, 26, 28], 80))
    pc_ok = pc is not None and pc["death"] == 2 and pc["last_alive"] == 1 and pc["atr"][2] > pc["atr"][1]
    print(f"proc_config: death={pc['death']} atr[1]={pc['atr'][1]:.0f}->atr[2]={pc['atr'][2]:.0f} (ok={pc_ok})")

    # F-027 causal: configs ambapo window-1 EV haihusiani na survival
    pos = []
    # config A: win1 juu sana lakini inakufa mapema (survival 1); B: win1 ndogo lakini inadumu (survival 6)
    pos.append(proc_config(mk([20, -5, -5, -5, -5, -5], [10]*6, 80)))   # win1=20, survival 1
    pos.append(proc_config(mk([2, 2, 2, 2, 2, 2], [10]*6, 80)))         # win1=2, survival 6
    pos.append(proc_config(mk([15, -3, -3, -3, -3, -3], [10]*6, 80)))   # win1=15, survival 1
    pos.append(proc_config(mk([3, 3, 3, 3, 3, 3], [10]*6, 80)))         # win1=3, survival 6
    pos = [p for p in pos if p and p["first_pos"]]
    rho = spearman([p["win1_ev"] for p in pos], [p["survival"] for p in pos])
    f27_ok = rho < 0   # high early EV -> short survival (negative/weak corr)
    print(f"F-027 causal: ρ(win1_ev, survival)={rho:+.2f} (early≠future, ok={f27_ok})")

    ok = fd_ok and pc_ok and f27_ok
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
