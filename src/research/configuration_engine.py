"""
configuration_engine.py — PHASE 6.5 (Chief Quant). Configuration Engine.

Phase 6 (Interaction Engine) ilithibitisha F-020 (sasa APPROVED): trading edge
inatoka **Event × Market Configuration**, sio Event peke yake. Lakini bado kila
Event ina EV hasi kwa wastani — kwa sababu tunatazama Event × State PEKEE.

Chief: "No Event possesses universal edge. Edge exists only inside a COMPLETE
Market Configuration." (F-021, APPROVED). Principle 22: trading opportunity
inawakilishwa na Market Configuration, KAMWE sio Event peke yake.

Definition mpya ya Market Configuration (atomic trading unit ya ELITEFX):

    Configuration = Pair
                  + Event
                  + Latent State        (kmeans cluster, Phase 5.9A)
                  + Regime              (volatility_state: LOW/NORMAL/HIGH)
                  + Direction           (LONG / SHORT)
                  + Execution Context   (spread_state: NORMAL/WIDE)

Sio event. Sio signal. **Configuration.** Kwa kila Configuration tunapima:

  • EV (net pips) ± 95% CI    • Win rate    • Triple Barrier (TP/SL/TIME)
  • Sample size (N)           • Walk-forward stability (train EV vs test EV)

H-07 (Chief, OPEN): "Negative Edge is more stable than Positive Edge." Tunapima
kama KUONDOA configurations mbaya kunaboresha Expected Value kuliko KUONGEZA
configurations nzuri (out-of-sample, no-lookahead train/test split).

Acceptance rule mpya: hakuna strategy inaingia mfumo mpaka ifafanuliwe kama
Market Configuration → Expected Payoff (sio Indicator → BUY). NO ML bado.

Reuse: latent_structure(kmeans, collect, state_path), mechanism_discovery
(signatures), event_library, context_value(HORIZON), triple_barrier_design(first_touch).

Output: reports/configuration_engine_report.md
Self-test: python src/research/configuration_engine.py --self-test
"""
from __future__ import annotations

import argparse, sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
import polars as pl

from market_state_engine import cfg, pip
from mechanism_discovery import signatures
from latent_structure import kmeans, collect, state_path
from event_library import EVENTS_ALL
from context_value import HORIZON
from triple_barrier_design import first_touch

REPO_ROOT = Path(__file__).resolve().parents[2]
TFS = ["H1", "H2", "H4", "D1"]
EVENTS_SET = ["pullback", "deep_pullback", "trend_continuation", "breakout", "mean_reversion"]
K = 4
VERT = 10              # vertical barrier (bars)
KSIG = 1.0             # barrier width (× ATR @ entry)
MIN_N = 100            # sample ya chini kwa Configuration ili kuripoti/kuhukumu
WF_FRAC = 0.70         # train fraction (walk-forward, kwa kila configuration kwa muda)
TOPN = 25              # configurations ngapi kuonyesha kila upande
_posix = lambda p: str(p).replace("\\", "/")


def assign(sig, cen):
    return ((sig[:, None, :] - cen[None, :, :]) ** 2).sum(2).argmin(1)


def _ci95(x):
    a = np.array(x, float)
    return 1.96 * a.std(ddof=1) / np.sqrt(len(a)) if len(a) > 1 else float("nan")


def wf_split(rows, frac=WF_FRAC):
    """rows = list ya (ts, net, win, tb). Panga kwa MUDA, gawa train/test (no-lookahead)."""
    r = sorted(rows, key=lambda t: t[0])
    cut = int(len(r) * frac)
    return r[:cut], r[cut:]


def config_stats(rows):
    """Rudisha takwimu za Configuration moja: N, EV±CI, Win, TB, train/test EV, stable?"""
    nets = [r[1] for r in rows]; wins = [r[2] for r in rows]
    tb = Counter(r[3] for r in rows)
    ev = float(np.mean(nets)); ci = _ci95(nets); win = float(np.mean(wins))
    tr, te = wf_split(rows)
    tev = float(np.mean([r[1] for r in tr])) if tr else float("nan")
    sev = float(np.mean([r[1] for r in te])) if te else float("nan")
    # stable = train na test zina ishara ileile (edge inaendelea out-of-sample)
    stable = bool(np.isfinite(tev) and np.isfinite(sev) and np.sign(tev) == np.sign(sev) and abs(sev) > 1e-9)
    return dict(n=len(rows), ev=ev, ci=ci, win=win, tb=tb, train_ev=tev, test_ev=sev, stable=stable)


def h07_portfolio(acc):
    """H-07: je kuondoa configurations mbaya kunashinda kuongeza nzuri (out-of-sample)?

    Kwa kila Configuration (N≥MIN_N): gawa train/test kwa muda. Amua ISHARA kutoka
    TRAIN tu (no-lookahead), kisha pima TEST EV ya:
      • baseline : test instances zote (trade-all).
      • add-good : test instances za configs zenye train_ev>0 tu.
      • remove-bad: test instances za configs zote ISIPOKUWA train_ev<0.
    Pia: persistence — sehemu ya train-positive zinazobaki positive vs train-negative
    zinazobaki negative kwenye test. H-07 inaungwa mkono ikiwa remove-bad ≥ add-good
    NA negative configs zina-persist zaidi kuliko positive."""
    base_test = []; good_test = []; nobad_test = []
    pos_keep = pos_persist = neg_keep = neg_persist = 0
    for rows in acc.values():
        if len(rows) < MIN_N:
            continue
        tr, te = wf_split(rows)
        if len(tr) < 20 or len(te) < 10:
            continue
        train_ev = float(np.mean([r[1] for r in tr]))
        test_nets = [r[1] for r in te]; test_ev = float(np.mean(test_nets))
        base_test += test_nets
        if train_ev > 0:
            good_test += test_nets
            nobad_test += test_nets          # train-positive: keep katika remove-bad pia
            pos_keep += 1; pos_persist += 1 if test_ev > 0 else 0
        elif train_ev < 0:
            neg_keep += 1; neg_persist += 1 if test_ev < 0 else 0
            # train-negative: HAIINGII remove-bad wala add-good
        else:
            nobad_test += test_nets          # train-neutral: keep katika remove-bad
    base = float(np.mean(base_test)) if base_test else float("nan")
    good = float(np.mean(good_test)) if good_test else float("nan")
    nobad = float(np.mean(nobad_test)) if nobad_test else float("nan")
    pos_rate = pos_persist / pos_keep if pos_keep else float("nan")
    neg_rate = neg_persist / neg_keep if neg_keep else float("nan")
    return dict(base=base, add_good=good, remove_bad=nobad, n_base=len(base_test),
                n_good=len(good_test), n_nobad=len(nobad_test),
                pos_persist=pos_rate, neg_persist=neg_rate, pos_keep=pos_keep, neg_keep=neg_keep)


def run(pairs, tfs):
    c = cfg(); rng = np.random.default_rng(0)
    pool = [X for sym in pairs if len(X := collect(sym, rng)) > 50]
    if not pool:
        print("HITILAFU: hakuna state parquet. Endesha market_state_engine.py kwanza.", file=sys.stderr)
        return 1
    _, cen, _ = kmeans(np.vstack(pool), K, rng)
    print(f"  latent clusters k={K} fitted", flush=True)

    # acc[config_key] = list ya (ts_epoch, net, win, tb_label)
    acc = defaultdict(list)
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
            sig, *_ = signatures(df, pp); fin = np.all(np.isfinite(sig), axis=1)
            cl = np.full(len(sig), -1)
            if fin.any():
                cl[fin] = assign(sig[fin], cen)
            close = df["c"].to_numpy() / pp; high = df["h"].to_numpy() / pp; low = df["l"].to_numpy() / pp
            atr_pips = df["atr"].to_numpy() / pp
            spr = df["spr"].to_numpy(); spr = np.where(np.isfinite(spr), spr, 0.0)
            vol = df["volatility_state"].to_list(); exec_ctx = df["spread_state"].to_list()
            ts = df["ts"].to_numpy().astype("datetime64[s]").astype(np.int64)
            n = len(close)
            for ev in EVENTS_SET:
                s = EVENTS_ALL[ev](close, high, low)
                for i in range(n):
                    if s[i] == 0 or cl[i] < 0 or i + VERT >= n or not (atr_pips[i] > 0):
                        continue
                    reg = vol[i]; ex = exec_ctx[i]
                    if reg == "UNKNOWN" or ex == "UNKNOWN":   # configuration isiyo kamili -> ruka
                        continue
                    d = int(s[i]); direction = "LONG" if d == 1 else "SHORT"
                    if i + HORIZON >= n:
                        continue
                    net = float(d * (close[i + HORIZON] - close[i]) - spr[i])
                    win = 1 if net > 0 else 0
                    tb, oc = first_touch(i, d, KSIG * atr_pips[i], close, high, low, n)
                    lab = oc if tb <= VERT else "TIME"
                    key = (sym, ev, f"C{cl[i]}", reg, direction, ex)
                    acc[key].append((int(ts[i]), net, win, lab))
        print(f"  {sym}: done", flush=True)
    if no_px:
        print("HITILAFU: OHLC haipo. Endesha market_state_engine.py (OHLC update) kwanza.", file=sys.stderr)
        return 1

    # tathmini kila configuration
    stats = {k: config_stats(v) for k, v in acc.items() if len(v) >= MIN_N}
    if not stats:
        print(f"HITILAFU: hakuna Configuration yenye N≥{MIN_N}.", file=sys.stderr)
        return 1
    h07 = h07_portfolio(acc)

    def fmt(key, st):
        sym, ev, cl, reg, dr, ex = key
        name = f"{sym}·{ev}·{cl}·{reg}·{dr}·{ex}"
        tb = st["tb"]; t = sum(tb.values()) or 1
        flag = "✅" if st["stable"] else "—"
        return (f"| {name} | {st['n']:,} | {st['ev']:+.2f} [{st['ev']-st['ci']:+.1f},{st['ev']+st['ci']:+.1f}] | "
                f"{st['win']*100:.0f}% | {100*tb['TP']/t:.0f}/{100*tb['SL']/t:.0f}/{100*tb['TIME']/t:.0f} | "
                f"{st['train_ev']:+.2f} | {st['test_ev']:+.2f} | {flag} |")

    ranked = sorted(stats.items(), key=lambda kv: kv[1]["test_ev"] if np.isfinite(kv[1]["test_ev"]) else -1e9)
    best = list(reversed(ranked[-TOPN:]))
    worst = ranked[:TOPN]
    n_stable = sum(1 for _, st in stats.items() if st["stable"])
    n_pos = sum(1 for _, st in stats.items() if st["ev"] > 0)

    L = ["# Configuration Engine — atomic trading unit ya ELITEFX (Phase 6.5)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | Configuration = Pair·Event·LatentState(k={K})·Regime·Direction·"
         f"ExecContext | EV±95%CI (net pips), Win, Triple Barrier (±{KSIG:.1f}σ,{VERT}b) | outcome forward "
         f"{HORIZON}b net | walk-forward train {int(WF_FRAC*100)}% | min N={MIN_N}*\n",
         "> **F-021 (Chief, APPROVED):** No Event possesses universal edge; edge exists only inside a "
         "COMPLETE Market Configuration. **Principle 22:** a trading opportunity is represented by a Market "
         "Configuration, NEVER by an Event alone. Acceptance rule: Market Configuration → Expected Payoff "
         "(sio Indicator → BUY). **H-07 (OPEN):** Negative Edge is more stable than Positive Edge — je "
         "kuondoa configs mbaya kunashinda kuongeza nzuri? NO ML bado (target haijajengwa).\n",
         f"## Muhtasari\n",
         f"- Configurations zenye N≥{MIN_N}: **{len(stats):,}**  |  EV>0: **{n_pos}**  |  "
         f"walk-forward stable (train/test ishara ileile): **{n_stable}**\n",
         f"\n## Top {len(best)} configurations kwa **out-of-sample (test) EV**\n",
         "| Configuration | N | EV [95% CI] | Win% | TP/SL/TIME | train EV | test EV | stable |",
         "|---------------|---|-------------|------|------------|----------|---------|--------|"]
    for key, st in best:
        L.append(fmt(key, st))

    L.append(f"\n## Bottom {len(worst)} configurations — **'WAPI USIFANYE TRADE'** (test EV mbaya zaidi)\n")
    L.append("| Configuration | N | EV [95% CI] | Win% | TP/SL/TIME | train EV | test EV | stable |")
    L.append("|---------------|---|-------------|------|------------|----------|---------|--------|")
    for key, st in worst:
        L.append(fmt(key, st))

    # H-07 verdict
    L.append("\n## H-07 — Negative Edge ni stable zaidi? Remove-bad vs Add-good (out-of-sample)\n")
    L.append("| portfolio (test, no-lookahead) | EV (pips) | N test |")
    L.append("|--------------------------------|-----------|--------|")
    L.append(f"| baseline (trade-all) | {h07['base']:+.3f} | {h07['n_base']:,} |")
    L.append(f"| add-good (train_ev>0 tu) | {h07['add_good']:+.3f} | {h07['n_good']:,} |")
    L.append(f"| remove-bad (zote ila train_ev<0) | {h07['remove_bad']:+.3f} | {h07['n_nobad']:,} |")
    up_add = h07["add_good"] - h07["base"]; up_rem = h07["remove_bad"] - h07["base"]
    L.append(f"\n- uplift add-good = **{up_add:+.3f}** | uplift remove-bad = **{up_rem:+.3f}** "
             f"(juu ya baseline)")
    L.append(f"- persistence: train-positive→positive **{h07['pos_persist']*100:.0f}%** "
             f"(N={h07['pos_keep']}) vs train-negative→negative **{h07['neg_persist']*100:.0f}%** "
             f"(N={h07['neg_keep']})")
    h07_support = (np.isfinite(up_rem) and np.isfinite(up_add) and up_rem >= up_add
                   and np.isfinite(h07["neg_persist"]) and np.isfinite(h07["pos_persist"])
                   and h07["neg_persist"] > h07["pos_persist"])
    if h07_support:
        L.append("\n→ ✅ **H-07 inaungwa mkono**: kuondoa configurations mbaya kunaboresha EV "
                 "≥ kuongeza nzuri, NA negative edge inaendelea (persist) zaidi out-of-sample. "
                 "'Trade less, but in the right environment.' (Experimental — thibitisha kwa walk-forward zaidi.)")
    else:
        L.append("\n→ ⚠️ **H-07 haijaungwa mkono kikamilifu**: kwa data hii, remove-bad haijazidi add-good "
                 "kwa uhakika au negative edge si stable zaidi. Inahitaji folds zaidi/data zaidi.")

    L.append("\n## VERDICT — F-021 / Principle 22\n")
    if n_stable >= 1:
        L.append(f"→ ✅ **Configuration ndio atomic unit**: kati ya {len(stats):,} configurations, "
                 f"**{n_stable}** zina edge inayoendelea out-of-sample (train/test ishara ileile). Event "
                 "peke yake (EV hasi) HAITOSHI — edge ipo ndani ya configuration kamili (F-021). Hizi "
                 "Configuration Objects ndizo msingi wa Opportunity Engine (rank kwa Expected Payoff).")
    else:
        L.append(f"→ ⚠️ Hakuna configuration yenye edge thabiti out-of-sample bado kati ya {len(stats):,}. "
                 "Inahitaji dimensions zaidi (regime/execution bora) au data zaidi kabla ya Opportunity Engine.")
    L.append("\n*Configuration = Pair·Event·LatentState·Regime·Direction·ExecContext (atomic trading unit). "
             "EV±CI/Win/TB per configuration; stable = train/test (walk-forward) ishara ileile (no-lookahead). "
             "H-07: remove-bad vs add-good out-of-sample. Principle 22: opportunity = Configuration, sio Event. "
             "F-019: information ina value tu ikiboresha payoff/decision. Acceptance: Market Configuration → "
             "Expected Payoff kabla ya Opportunity Engine. NO ML bado. Profitable ≠ Tradable Edge.*")
    out = REPO_ROOT / c["paths"]["reports"] / "configuration_engine_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)} ({len(stats):,} configs, {n_stable} stable)")
    return 0


def self_test():
    """(1) config_stats: stable hugunduliwa wakati train/test ishara ileile, sio vinginevyo.
       (2) h07_portfolio: configuration moja stable-negative -> remove-bad inaboresha test EV
           kuliko add-good; negative persistence > positive persistence."""
    rng = np.random.default_rng(0)
    # CI helper
    ci = _ci95(rng.normal(0, 10, 4000)); ci_ok = abs(ci - 1.96 * 10 / np.sqrt(4000)) < 0.1

    def mk(mu_tr, mu_te, n=400, t0=0):
        """rows: nusu ya kwanza (train) mean=mu_tr, nusu ya pili (test) mean=mu_te; ts inaongezeka."""
        r = []
        for k in range(n):
            mu = mu_tr if k < n * WF_FRAC else mu_te
            net = float(rng.normal(mu, 5))
            r.append((t0 + k, net, 1 if net > 0 else 0, "TP" if net > 0 else "SL"))
        return r

    # stable positive (train + test wote +6)
    sp = config_stats(mk(6.0, 6.0)); stable_pos_ok = sp["stable"] and sp["test_ev"] > 0
    # unstable (train +6, test -6) -> stable=False
    us = config_stats(mk(6.0, -6.0)); unstable_ok = not us["stable"]
    # stable negative (train + test wote -6)
    sn = config_stats(mk(-6.0, -6.0)); stable_neg_ok = sn["stable"] and sn["test_ev"] < 0
    print(f"config_stats: stable+={stable_pos_ok} unstable_detected={unstable_ok} stable-={stable_neg_ok}")

    # H-07 portfolio: configs nyingi flat (~0), moja stable-negative kubwa (train&test -8),
    # chache stable-positive ndogo (+2). Remove-bad inaondoa drag kubwa -> > add-good.
    acc = {}
    for j in range(8):
        acc[("P", "ev", f"C{j%4}", "NORMAL", "LONG", "NORMAL_" + str(j))] = mk(0.2, 0.0, n=300, t0=0)
    acc[("P", "ev", "C0", "HIGH", "SHORT", "WIDE")] = mk(-8.0, -8.0, n=600, t0=0)     # drag kubwa thabiti
    acc[("P", "ev", "C1", "LOW", "LONG", "NORMAL")] = mk(2.5, 2.5, n=400, t0=0)        # nzuri ndogo thabiti
    h = h07_portfolio(acc)
    up_add = h["add_good"] - h["base"]; up_rem = h["remove_bad"] - h["base"]
    h07_ok = up_rem >= up_add and h["neg_persist"] >= h["pos_persist"] and h["neg_keep"] >= 1
    print(f"H-07: base={h['base']:+.2f} add-good={h['add_good']:+.2f} remove-bad={h['remove_bad']:+.2f} "
          f"| up_add={up_add:+.2f} up_rem={up_rem:+.2f} | neg_persist={h['neg_persist']:.2f} "
          f"pos_persist={h['pos_persist']:.2f} (ok={h07_ok})")

    ok = ci_ok and stable_pos_ok and unstable_ok and stable_neg_ok and h07_ok
    print("CI95 ok:", ci_ok)
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
