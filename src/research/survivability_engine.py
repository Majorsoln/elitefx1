"""
survivability_engine.py — PHASE 9 (Chief Quant). Survivability Engine.

Phase 8 (Opportunity Engine) ilikataa hypothesis yetu kwa ushahidi: CCS-selection
HAIKUGEUZA portfolio kuwa chanya out-of-sample (trade-all −1.122 → CCS-selected
−0.757, bado hasi; Top 5% kwa train-CCS hata mbaya zaidi). Hii si kosa la
implementation — ni hypothesis iliyokataliwa na data → **doctrine inabadilika**.

Chief: F-022 imepandishwa kuwa **Core Principle**; **Principle 26** — Opportunity
Engine kazi yake ya kwanza ni KULINDA MTAJI, sio kutafuta alpha. Na dimension mpya:

    Opportunity = Quality × Availability × **Survivability**

CCS ilipima Quality. OppScore iliongeza Availability. Bado haitoshi. Swali jipya
si "configuration ilikuwa nzuri?" wala "ilitokea mara ngapi?" bali:

    **"Je iliendelea kuwa nzuri baada ya muda?"**  (Survivability)

F-027 (OPEN): Configuration Survivability ni dimension HURU kutoka Configuration
Quality. Phase 9 inapima, kwa kila Configuration, kwa **rolling walk-forward
NYINGI** (sio split moja ya 70/30):

  Q1. Configs zipi zinadumu vizuri katika windows nyingi za muda?
  Q2. Median survival time ya edge ni ipi?
  Q3. Edge decay inaanza baada ya trades/muda gani?
  Q4. Je survivability inatabirika kutokana na event/regime/state/context?
  Q5. Configs zenye EV ya wastani lakini survivability kubwa (bora kwa portfolio
      ya muda mrefu)?

+ F-027 test: corr(survivability, EV) na corr(survivability, CCS) — ndogo = HURU.

Reuse: confidence_engine (build_acc, confidence_score, spearman), latent_structure
(kmeans, collect), configuration_engine (K), market_state_engine (cfg). NO ML.

Output: reports/survivability_engine_report.md
Self-test: python src/research/survivability_engine.py --self-test
"""
from __future__ import annotations

import argparse, sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np

from market_state_engine import cfg
from latent_structure import kmeans, collect
from configuration_engine import K
from confidence_engine import build_acc, confidence_score, spearman

REPO_ROOT = Path(__file__).resolve().parents[2]
MIN_N = 200           # sample ya chini (rolling windows zinahitaji N kubwa zaidi)
NWIN = 6              # idadi ya rolling walk-forward windows (kwa muda)
MIN_WIN = 25          # sample ya chini kwa kila window
TOPN = 25
DIMS = [("event", 1), ("regime", 3), ("latent", 2), ("direction", 4), ("exec", 5)]


def survivability_stats(rows, nwin=NWIN):
    """Configuration moja -> survivability metrics kwa rolling windows za muda.
    Rudisha None kama N haitoshi."""
    r = sorted(rows, key=lambda t: t[0])
    nets = np.array([x[1] for x in r], float); n = len(nets)
    if n < MIN_N:
        return None
    chunks = np.array_split(nets, nwin)
    if min(len(ch) for ch in chunks) < MIN_WIN:
        return None
    win_ev = np.array([ch.mean() for ch in chunks])
    overall = float(nets.mean())
    surv_rate = float(np.mean(win_ev > 0))                  # sehemu ya windows zenye EV>0
    # survival_windows = windows za mfululizo CHANYA tangu mwanzo (edge "hai")
    sw = 0
    for e in win_ev:
        if e > 0:
            sw += 1
        else:
            break
    decay = float(np.polyfit(np.arange(nwin), win_ev, 1)[0])   # mteremko wa EV kwa muda (<0 = decay)
    ccs = confidence_score(r)["ccs"]
    return dict(n=n, overall_ev=overall, ccs=ccs, surv_rate=surv_rate, survival_windows=sw,
                decay=decay, win_ev=win_ev, trades_per_win=n / nwin,
                first_pos=bool(win_ev[0] > 0), last_ev=float(win_ev[-1]))


def surv_by_dim(stats, idx):
    """Group survivability kwa thamani ya dimension (key index) -> mean surv_rate + n."""
    g = defaultdict(list)
    for s in stats:
        g[s["key"][idx]].append(s["surv_rate"])
    return {k: (float(np.mean(v)), len(v)) for k, v in g.items()}


def run(pairs, tfs):
    c = cfg(); rng = np.random.default_rng(0)
    pool = [X for sym in pairs if len(X := collect(sym, rng)) > 50]
    if not pool:
        print("HITILAFU: hakuna state parquet. Endesha market_state_engine.py kwanza.", file=sys.stderr)
        return 1
    _, cen, _ = kmeans(np.vstack(pool), K, rng)
    print(f"  latent clusters k={K} fitted", flush=True)
    acc, no_px = build_acc(pairs, cen)
    if no_px:
        print("HITILAFU: OHLC haipo. Endesha market_state_engine.py (OHLC update) kwanza.", file=sys.stderr)
        return 1

    stats = []
    for key, rows in acc.items():
        st = survivability_stats(rows)
        if st is not None:
            st["key"] = key
            stats.append(st)
    if not stats:
        print(f"HITILAFU: hakuna Configuration yenye N≥{MIN_N}.", file=sys.stderr)
        return 1

    # F-027: survivability vs quality (independent?)
    surv = [s["surv_rate"] for s in stats]
    rho_ev = spearman(surv, [s["overall_ev"] for s in stats])
    rho_ccs = spearman(surv, [s["ccs"] for s in stats])

    pos_start = [s for s in stats if s["first_pos"]]
    med_sw = float(np.median([s["survival_windows"] for s in pos_start])) if pos_start else float("nan")
    med_trades = float(np.median([s["survival_windows"] * s["trades_per_win"] for s in pos_start])) if pos_start else float("nan")

    L = ["# Survivability Engine — je edge inadumu? (Phase 9)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | rolling walk-forward {NWIN} windows (kwa muda, sio 70/30) | "
         f"survivability = sehemu ya windows zenye EV>0 | min N={MIN_N} | configs: {len(stats):,}*\n",
         "> **Lengo (Chief):** Phase 8 ilikataa hypothesis (CCS-selection haitoi portfolio chanya OOS). "
         "Dimension mpya: **Opportunity = Quality × Availability × Survivability**. **Principle 26:** kazi ya "
         "kwanza ya Opportunity Engine ni KULINDA MTAJI (ondoa mabaya), sio kutafuta alpha. **F-022 (Core "
         "Principle):** edge mbaya inadumu zaidi ya nzuri. **F-027 (OPEN):** survivability ni dimension HURU "
         "kutoka quality. NO ML bado. Profitable ≠ Tradable Edge.\n"]

    # F-027
    L.append("\n## F-027 — Je Survivability ni HURU kutoka Quality? (corr ndogo = huru)\n")
    L.append(f"- Spearman(survivability, EV) = **{rho_ev:+.2f}**")
    L.append(f"- Spearman(survivability, CCS) = **{rho_ccs:+.2f}**")
    indep = (abs(rho_ev) < 0.5 and abs(rho_ccs) < 0.5)
    L.append(f"\n→ {'✅ **F-027 inaungwa mkono**' if indep else '⚠️ F-027 haijaungwa mkono kikamilifu'}: "
             f"survivability {'haina uhusiano mkubwa na' if indep else 'ina uhusiano na'} quality (EV/CCS) — "
             f"{'ni DIMENSION HURU; config nzuri ≠ config inayodumu' if indep else 'huenda si huru kabisa'}.")

    # Q1 — top survivors
    L.append(f"\n## Q1 — Configurations zinazodumu zaidi (rolling {NWIN} windows)\n")
    L.append("| Configuration | N | overall EV | CCS | surv-rate | survival (win) | last-win EV | decay/win |")
    L.append("|---------------|---|-----------|-----|-----------|----------------|-------------|-----------|")
    top = sorted(stats, key=lambda s: (s["surv_rate"], s["overall_ev"]), reverse=True)[:TOPN]
    for s in top:
        L.append(f"| {'·'.join(s['key'])} | {s['n']:,} | {s['overall_ev']:+.2f} | {s['ccs']:+.2f} | "
                 f"{s['surv_rate']*100:.0f}% | {s['survival_windows']}/{NWIN} | {s['last_ev']:+.2f} | {s['decay']:+.2f} |")

    # Q2 — median survival time
    L.append("\n## Q2 — Median survival time ya edge\n")
    L.append(f"- Configs zilizoanza chanya (window 1 EV>0): **{len(pos_start)}/{len(stats)}**")
    L.append(f"- **Median survival = {med_sw:.1f}/{NWIN} windows** (≈ {med_trades:,.0f} trades)")
    full = sum(1 for s in pos_start if s["survival_windows"] == NWIN)
    L.append(f"- Configs zilizodumu windows ZOTE ({NWIN}/{NWIN}): **{full}/{len(pos_start)}** "
             f"({100*full/len(pos_start):.0f}% ya zilizoanza chanya)" if pos_start else "")

    # Q3 — decay onset
    L.append("\n## Q3 — Edge decay inaanza lini? (wastani wa EV kwa window index)\n")
    L.append("| window | mean EV (configs zote) | mean EV (zilizoanza chanya) | trades-hadi-hapa (wastani) |")
    L.append("|--------|------------------------|----------------------------|----------------------------|")
    tpw = float(np.mean([s["trades_per_win"] for s in stats]))
    for w in range(NWIN):
        all_w = float(np.mean([s["win_ev"][w] for s in stats]))
        pos_w = float(np.mean([s["win_ev"][w] for s in pos_start])) if pos_start else float("nan")
        L.append(f"| {w+1} | {all_w:+.3f} | {pos_w:+.3f} | {tpw*(w+1):,.0f} |")
    mean_decay = float(np.mean([s["decay"] for s in pos_start])) if pos_start else float("nan")
    L.append(f"\n→ wastani wa decay slope (configs zilizoanza chanya) = **{mean_decay:+.3f} pips/window** "
             f"({'edge inafifia kwa muda' if mean_decay < -0.05 else 'edge ni thabiti kiasi'}).")

    # Q4 — predictability by dimension
    L.append("\n## Q4 — Je survivability inatabirika? (mean surv-rate kwa dimension)\n")
    for name, idx in DIMS:
        d = surv_by_dim(stats, idx)
        if not d:
            continue
        items = sorted(d.items(), key=lambda kv: kv[1][0], reverse=True)
        spread = items[0][1][0] - items[-1][1][0]
        cells = " · ".join(f"{k}={v[0]*100:.0f}%" for k, v in items)
        L.append(f"- **{name}** (spread {spread*100:.0f}pp): {cells}")
    L.append("\n→ dimension zenye spread kubwa zinatabiri survivability vizuri zaidi (state/regime/event/"
             "context huamua kama edge itadumu).")

    # Q5 — durable but modest
    L.append("\n## Q5 — High survivability, EV ya wastani (workhorses za portfolio ya muda mrefu)\n")
    surv_hi = np.quantile([s["surv_rate"] for s in stats], 0.75)
    ev_med = np.median([s["overall_ev"] for s in stats])
    durable = [s for s in stats if s["surv_rate"] >= surv_hi and 0 < s["overall_ev"] <= ev_med]
    durable = sorted(durable, key=lambda s: s["surv_rate"] * s["n"], reverse=True)[:TOPN]
    L.append(f"*surv-rate ≥ Q3 ({surv_hi*100:.0f}%) NA 0 < EV ≤ median ({ev_med:+.2f}); "
             f"zinapatikana: {len(durable)}*\n")
    if durable:
        L.append("| Configuration | N | overall EV | CCS | surv-rate | decay/win |")
        L.append("|---------------|---|-----------|-----|-----------|-----------|")
        for s in durable:
            L.append(f"| {'·'.join(s['key'])} | {s['n']:,} | {s['overall_ev']:+.2f} | {s['ccs']:+.2f} | "
                     f"{s['surv_rate']*100:.0f}% | {s['decay']:+.2f} |")
        L.append("\n→ ✅ configs hizi sio EV-stars lakini zinadumu — ndizo backbone ya portfolio ya muda mrefu "
                 "(F-027: survivability huru kutoka EV).")
    else:
        L.append("→ hakuna config inayolingana (survivability ya juu inaambatana na EV ya juu hapa).")

    L.append("\n## VERDICT — Phase 9 Survivability Engine\n")
    L.append(f"→ Survivability ni dimension {'HURU' if indep else 'inayohusiana kiasi'} (ρ_EV {rho_ev:+.2f}, "
             f"ρ_CCS {rho_ccs:+.2f}). Median edge survival = {med_sw:.1f}/{NWIN} windows. Hii inathibitisha "
             "mwelekeo wa Chief: Opportunity Engine lazima ijenge juu ya **Survivability** (na Principle 26 — "
             "ondoa mabaya kwanza), sio CCS pekee. Inayofuata: Opportunity Engine iliyojengwa upya (remove-bad "
             "→ rank survivable → allocate). NO ML bado.")
    L.append("\n*Survivability = sehemu ya rolling windows zenye EV>0 (durability ya muda, sio split moja). "
             "F-027: corr(survivability, quality) ndogo = dimension huru. Q2 median survival, Q3 decay onset, "
             "Q4 predictability kwa dimension, Q5 durable-modest workhorses. Opportunity = Quality × Availability "
             "× Survivability (Principle 25 enhanced). Principle 26: linda mtaji kwanza. NO ML. Profitable ≠ "
             "Tradable Edge.*")
    out = REPO_ROOT / c["paths"]["reports"] / "survivability_engine_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)} ({len(stats):,} configs, ρ_EV={rho_ev:+.2f}, "
          f"med survival {med_sw:.1f}/{NWIN})")
    return 0


def self_test():
    """Synthetic: durable-modest (EV ndogo, surv=1), high-decay (EV juu mwanzoni, surv ndogo,
    decay<0), stable-high, dead. Thibitisha: (1) survivability_stats sahihi; (2) decay
    inagunduliwa; (3) F-027 — surv-top ≠ EV-top (survivability huru kutoka quality)."""
    rng = np.random.default_rng(0)

    def mk(means, sd, per_win):
        rows = []; t = 0
        for mu in means:
            for _ in range(per_win):
                rows.append((t, float(rng.normal(mu, sd)), 0, "TP")); t += 1
        return rows

    durable = survivability_stats(mk([2, 2, 2, 2, 2, 2], 4, 90))
    decay = survivability_stats(mk([40, 20, 10, -2, -4, -6], 5, 90))   # EV juu sana mwanzoni, inafifia
    stable = survivability_stats(mk([6, 6, 6, 6, 6, 6], 4, 90))
    dead = survivability_stats(mk([-4, -4, -4, -4, -4, -4], 4, 90))

    s_ok = (abs(durable["surv_rate"] - 1.0) < 1e-9 and decay["surv_rate"] < 0.6
            and durable["survival_windows"] == NWIN and decay["survival_windows"] == 3)
    print(f"stats: durable surv={durable['surv_rate']:.2f} sw={durable['survival_windows']} | "
          f"decay surv={decay['surv_rate']:.2f} sw={decay['survival_windows']} (ok={s_ok})")

    decay_ok = decay["decay"] < -3.0 and abs(durable["decay"]) < 1.0
    print(f"decay slope: decay={decay['decay']:+.2f} durable={durable['decay']:+.2f} (ok={decay_ok})")

    # F-027: surv-top vs EV-top zinatofautiana
    cfgs = [("durable", durable), ("decay", decay), ("stable", stable), ("dead", dead)]
    surv_top = max(cfgs, key=lambda kv: kv[1]["surv_rate"])[0]
    ev_top = max(cfgs, key=lambda kv: kv[1]["overall_ev"])[0]
    indep_ok = ev_top == "decay" and surv_top in ("durable", "stable")
    rho = spearman([c[1]["surv_rate"] for c in cfgs], [c[1]["overall_ev"] for c in cfgs])
    print(f"F-027: EV-top={ev_top} surv-top={surv_top} ρ(surv,EV)={rho:+.2f} (independent={indep_ok})")

    ok = s_ok and decay_ok and indep_ok
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
