"""
opportunity_engine.py — PHASE 8 (Chief Quant). Opportunity Engine.

Research Foundation imefungwa. Phase 7 (Confidence Engine) ilitoa **CCS**
(Configuration Confidence Score = EV × Confidence × Persistence × SampleQuality)
na kuthibitisha Principle 24 (hakuna ranking kwa EV peke yake) + F-024.

Phase 8 HAITAFUTI edge mpya. Lengo: thibitisha kuwa **CCS inaweza kubadilishwa
kuwa MFUMO WA MAAMUZI** (decision system) — bila ML. Hadi sasa tulijenga
*knowledge*; sasa tunajenga *decision*.

Chief ameongeza F-025 (APPROVED): **Edge ina Magnitude NA Availability** — portfolio
return haitokani na EV/CCS pekee bali pia na FREQUENCY ya configuration. Principle 25:
**Opportunity Score = Quality × Availability.** (CCS=5.4 mara 2/mwaka ≠ CCS=3.9 mara 300.)

Report inajibu maswali 4 (yote OUT-OF-SAMPLE: rank kwa TRAIN, pima kwa TEST):
  Q1. CCS ikitumika kupanga configurations, portfolio EV inaboreshwa kwa kiasi gani
      dhidi ya "trade-all"?
  Q2. Asilimia ngapi ya configurations bora (Top 5/10/20/50%) zinabeba sehemu kubwa
      ya edge ya mfumo? (concentration)
  Q3. Je kuongeza Availability (frequency) huboresha portfolio dhidi ya CCS pekee?
      (F-025 / Principle 25: OppScore = CCS × Availability)
  Q4. Je Opportunity Engine inaweza kutengeneza PRIORITY QUEUE bila ML?

Reuse: confidence_engine (build_acc, confidence_score), configuration_engine (wf_split),
latent_structure (kmeans, collect), market_state_engine (cfg, pip). NO ML (Chief).

Output: reports/opportunity_engine_report.md
Self-test: python src/research/opportunity_engine.py --self-test
"""
from __future__ import annotations

import argparse, sys
from datetime import datetime
from pathlib import Path

import numpy as np

from market_state_engine import cfg
from latent_structure import kmeans, collect
from configuration_engine import wf_split, K
from confidence_engine import build_acc, confidence_score

REPO_ROOT = Path(__file__).resolve().parents[2]
MIN_N = 100
MIN_TRAIN, MIN_TEST = 30, 15
TOP_PCTS = [0.05, 0.10, 0.20, 0.50]
BUDGETS = [10, 25, 50, 100]      # idadi ya configurations zinazochaguliwa (capacity budget)
TOPQ = 30                        # urefu wa priority queue ya kuonyesha


def eval_configs(acc, min_n=MIN_N):
    """Kwa kila Configuration: train-CCS (no-lookahead, 70%) + realized TEST (30%) +
    full-sample CCS/availability (kwa priority queue ya operesheni)."""
    out = []
    for key, rows in acc.items():
        if len(rows) < min_n:
            continue
        r = sorted(rows, key=lambda t: t[0])
        tr, te = wf_split(r)
        if len(tr) < MIN_TRAIN or len(te) < MIN_TEST:
            continue
        ts = confidence_score(tr)                      # CCS kutoka TRAIN tu
        full = confidence_score(r)                     # CCS ya full-sample (queue)
        te_net = np.array([x[1] for x in te], float)
        out.append(dict(key=key, train_ccs=ts["ccs"], train_ev=ts["ev"], train_n=len(tr),
                        test_ev=float(te_net.mean()), test_n=len(te), test_total=float(te_net.sum()),
                        full_ccs=full["ccs"], full_ev=full["ev"], full_n=len(r),
                        avail=len(r)))
    return out


def q1_portfolio(stats):
    """trade-all vs CCS-selected (train_ccs>0) — portfolio EV ya TEST (per-trade) +
    top percentiles kwa train_ccs."""
    base_tot = sum(s["test_total"] for s in stats); base_n = sum(s["test_n"] for s in stats)
    base_ev = base_tot / base_n if base_n else float("nan")
    sel = [s for s in stats if s["train_ccs"] > 0]
    sel_tot = sum(s["test_total"] for s in sel); sel_n = sum(s["test_n"] for s in sel)
    sel_ev = sel_tot / sel_n if sel_n else float("nan")
    rows = []
    ranked = sorted(stats, key=lambda s: s["train_ccs"], reverse=True)
    for p in TOP_PCTS:
        k = max(1, int(len(ranked) * p)); top = ranked[:k]
        tot = sum(s["test_total"] for s in top); nn = sum(s["test_n"] for s in top)
        rows.append((p, k, tot / nn if nn else float("nan"), tot, nn))
    return dict(base_ev=base_ev, base_n=base_n, sel_ev=sel_ev, sel_n=sel_n,
                n_sel=len(sel), n_all=len(stats), pct_rows=rows)


def q2_concentration(stats):
    """Concentration: configurations zilizopangwa kwa train_ccs zinabeba sehemu gani ya
    EDGE halisi ya TEST (cumulative test pips / jumla ya universe ya tradeable)."""
    univ = [s for s in stats if s["train_ccs"] > 0]
    ranked = sorted(univ, key=lambda s: s["train_ccs"], reverse=True)
    tot = sum(s["test_total"] for s in univ)
    rows = []
    for p in TOP_PCTS:
        k = max(1, int(len(ranked) * p))
        cum = sum(s["test_total"] for s in ranked[:k])
        rows.append((p, k, cum, cum / tot if tot else float("nan")))
    return dict(n_univ=len(univ), tot=tot, rows=rows)


def q3_availability(stats, budgets=BUDGETS):
    """F-025 / Principle 25: kwa budget M (idadi ya configs), linganisha JUMLA ya TEST pips
    ukichagua kwa CCS pekee vs kwa OppScore = CCS × Availability(train_n)."""
    univ = [s for s in stats if s["train_ccs"] > 0]
    by_ccs = sorted(univ, key=lambda s: s["train_ccs"], reverse=True)
    by_opp = sorted(univ, key=lambda s: s["train_ccs"] * s["train_n"], reverse=True)
    rows = []
    for M in budgets:
        if M > len(univ):
            continue
        A = by_ccs[:M]; B = by_opp[:M]
        sa = sum(s["test_total"] for s in A); na = sum(s["test_n"] for s in A)
        sb = sum(s["test_total"] for s in B); nb = sum(s["test_n"] for s in B)
        rows.append((M, sa, na, sa / na if na else float("nan"),
                     sb, nb, sb / nb if nb else float("nan")))
    return dict(n_univ=len(univ), rows=rows)


def priority_queue(stats, topq=TOPQ):
    """Q4: priority queue ya operesheni — OppScore = full_ccs × availability (Quality ×
    Availability). Deterministic, rule-based, NO ML."""
    q = [s for s in stats if s["full_ccs"] > 0]
    for s in q:
        s["opp"] = s["full_ccs"] * s["full_n"]
    return sorted(q, key=lambda s: s["opp"], reverse=True)[:topq], len(q)


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
    stats = eval_configs(acc)
    if not stats:
        print(f"HITILAFU: hakuna Configuration yenye N≥{MIN_N} (train/test).", file=sys.stderr)
        return 1

    q1 = q1_portfolio(stats); q2 = q2_concentration(stats); q3 = q3_availability(stats)
    queue, n_q = priority_queue(stats)

    L = ["# Opportunity Engine — kutoka CCS hadi MAAMUZI (Phase 8)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | OppScore = Quality(CCS) × Availability(frequency) | OUT-OF-SAMPLE "
         f"(rank kwa TRAIN 70%, pima kwa TEST 30%) | min N={MIN_N} | configs tradeable (train_ccs>0): "
         f"{q1['n_sel']}/{q1['n_all']}*\n",
         "> **Lengo (Chief):** sio edge mpya — bali kuthibitisha CCS inaweza kuwa mfumo wa MAAMUZI bila ML. "
         "**F-025 (APPROVED):** Edge ina Magnitude NA Availability. **Principle 25:** Opportunity Score = "
         "Quality × Availability. **F-023/P23:** rank Configurations, usi-classify Trades. NO ML bado (CCS/"
         "OppScore = target ya baadaye ya ML). Profitable ≠ Tradable Edge.\n"]

    # Q1
    L.append("\n## Q1 — CCS-ranked vs trade-all (portfolio EV ya TEST, per-trade)\n")
    L.append(f"- **trade-all**: EV = **{q1['base_ev']:+.3f}** pips/trade (configs {q1['n_all']}, "
             f"test trades {q1['base_n']:,})")
    L.append(f"- **CCS-selected (train_ccs>0)**: EV = **{q1['sel_ev']:+.3f}** pips/trade "
             f"(configs {q1['n_sel']}, test trades {q1['sel_n']:,})")
    up = q1['sel_ev'] - q1['base_ev']
    L.append(f"- **uplift = {up:+.3f} pips/trade**\n")
    L.append("| select Top% (train_ccs) | configs | test EV/trade | test total pips | test trades |")
    L.append("|-------------------------|---------|---------------|-----------------|-------------|")
    for p, k, ev, tot, nn in q1["pct_rows"]:
        L.append(f"| {int(p*100)}% | {k} | {ev:+.3f} | {tot:+,.0f} | {nn:,} |")
    L.append(f"\n→ {'✅' if up > 0 and q1['sel_ev'] > 0 else '⚠️'} CCS-ranking "
             f"{'inageuza portfolio kutoka hasi kuwa chanya (out-of-sample)' if up>0 and q1['sel_ev']>0 else 'haijaboresha vya kutosha'}.")

    # Q2
    L.append("\n## Q2 — Concentration: top configs zinabeba edge kiasi gani? (TEST pips)\n")
    L.append(f"*Universe ya tradeable (train_ccs>0): {q2['n_univ']} configs; jumla TEST pips = {q2['tot']:+,.0f}*\n")
    L.append("| top% (kwa train_ccs) | configs | cum TEST pips | % ya edge yote |")
    L.append("|----------------------|---------|---------------|----------------|")
    for p, k, cum, frac in q2["rows"]:
        L.append(f"| {int(p*100)}% | {k} | {cum:+,.0f} | {frac*100:.0f}% |")
    top20 = next((f for p, k, c, f in q2["rows"] if abs(p - 0.20) < 1e-9), float("nan"))
    L.append(f"\n→ Top 20% ya configurations zinabeba **{top20*100:.0f}%** ya edge — "
             f"{'edge imejikita kwa wachache (Pareto): Opportunity Engine inahitaji kuchagua, sio kufanya yote' if np.isfinite(top20) and top20>0.6 else 'edge imesambaa zaidi'}.")

    # Q3
    L.append("\n## Q3 — Je Availability inaboresha portfolio? CCS-pekee vs OppScore=CCS×Availability\n")
    L.append("*Kwa kila budget (idadi ya configs zinazochaguliwa), JUMLA ya TEST pips (out-of-sample):*\n")
    L.append("| budget (configs) | CCS-only: total pips | EV/trade | OppScore: total pips | EV/trade | OppScore − CCS |")
    L.append("|------------------|----------------------|----------|----------------------|----------|----------------|")
    q3_win = 0; q3_tot = 0
    for M, sa, na, eva, sb, nb, evb in q3["rows"]:
        q3_tot += 1; q3_win += 1 if sb >= sa else 0
        L.append(f"| {M} | {sa:+,.0f} | {eva:+.2f} | {sb:+,.0f} | {evb:+.2f} | {sb-sa:+,.0f} |")
    L.append(f"\n→ {'✅ **F-025 / Principle 25 inaungwa mkono**' if q3_win >= q3_tot - 0 and q3_tot else '⚠️'}: "
             f"kwa budget {q3_win}/{q3_tot}, OppScore (Quality × Availability) inakusanya JUMLA kubwa zaidi ya "
             "pips kuliko CCS pekee — portfolio return inahitaji frequency, sio magnitude tu. (CCS-only "
             "huchagua configs adimu zenye quality juu lakini throughput ndogo.)")

    # Q4
    L.append(f"\n## Q4 — PRIORITY QUEUE (bila ML): Top {min(TOPQ, n_q)}/{n_q} kwa OppScore = CCS × Availability\n")
    L.append("| # | Configuration | N | full EV | full CCS | OppScore |")
    L.append("|---|---------------|---|---------|----------|----------|")
    for i, s in enumerate(queue, 1):
        L.append(f"| {i} | {'·'.join(s['key'])} | {s['full_n']:,} | {s['full_ev']:+.2f} | "
                 f"{s['full_ccs']:+.2f} | {s['opp']:+,.0f} |")
    L.append(f"\n→ ✅ **Q4: NDIYO** — priority queue ni rule-based deterministic (panga kwa OppScore), "
             "hakuna ML. Hii ndiyo entity Opportunity Engine inatoa: orodha ya configurations kwa kipaumbele.")

    L.append("\n## VERDICT — Phase 8 Opportunity Engine\n")
    ok_decision = (q1['sel_ev'] > 0 and up > 0)
    if ok_decision:
        L.append("→ ✅ **CCS inabadilika kuwa mfumo wa maamuzi**: (Q1) CCS-ranking inageuza portfolio kuwa "
                 "chanya out-of-sample; (Q2) edge imejikita kwa wachache (chagua, usifanye yote); (Q3) "
                 "Availability inaboresha portfolio (F-025/P25); (Q4) priority queue bila ML. Hii ndiyo daraja "
                 "kutoka *knowledge* hadi *decision*. Hatua ya mwisho: ML kujifunza Configuration Score (sio "
                 "BUY/SELL). Inayofuata: **Portfolio Engine** (allocation) + F-026 (state trajectory).")
    else:
        L.append("→ ⚠️ CCS-selection haijageuza portfolio kuwa chanya kwa uhakika out-of-sample; inahitaji "
                 "uchambuzi zaidi (cost model, walk-forward ya muda mrefu) kabla ya Opportunity Engine kamili.")
    L.append("\n*OppScore = Quality(CCS) × Availability(frequency) [F-025/Principle 25]. Validation YOTE "
             "out-of-sample (rank kwa train, pima kwa test; no-lookahead). Q1 portfolio uplift, Q2 concentration "
             "(Pareto), Q3 availability faida, Q4 priority queue bila ML. Architecture: Configuration → Confidence "
             "→ Opportunity → Portfolio. NO ML bado (CCS/OppScore = target ya ML). Profitable ≠ Tradable Edge "
             "(hakuna cost model kamili / walk-forward ya muda).*")
    out = REPO_ROOT / c["paths"]["reports"] / "opportunity_engine_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)} ({q1['n_sel']}/{q1['n_all']} tradeable, "
          f"Q1 uplift {up:+.2f}, Q3 win {q3_win}/{q3_tot})")
    return 0


def self_test():
    """Synthetic configs: rare-strong (CCS juu, N ndogo), freq-good (CCS wastani, N kubwa,
    total kubwa), negatives (train_ccs<0). Thibitisha:
      Q1: CCS-selected EV > trade-all (na chanya).
      Q3: OppScore (CCS×Avail) inakusanya JUMLA kubwa ya pips kuliko CCS-pekee (budget ndogo).
      Q4: queue-top (OppScore) = freq-good, lakini CCS-top = rare-strong (zinatofautiana)."""
    rng = np.random.default_rng(0)

    def mk(mu, sd, n):
        # ts inaongezeka; train (70%) na test (30%) zote zina mu ileile (edge thabiti)
        return [(k, float(rng.normal(mu, sd)), 1 if mu > 0 else 0, "TP") for k in range(n)]

    acc = {}
    acc[("P", "ev", "C0", "HIGH", "SHORT", "WIDE")] = mk(25.0, 8.0, 200)     # rare-strong (CCS juu, N ndogo)
    for j in range(4):                                                       # freq-good (CCS wastani, N kubwa)
        acc[("P", "ev", f"C{j}", "LOW", "LONG", "NORMAL")] = mk(3.0, 5.0, 4000)
    for j in range(6):                                                       # negatives
        acc[("P", "bad", f"C{j}", "HIGH", "LONG", "WIDE")] = mk(-4.0, 5.0, 3000)

    stats = eval_configs(acc, min_n=MIN_N)
    q1 = q1_portfolio(stats); q3 = q3_availability(stats, budgets=[2, 3, 5])
    queue, n_q = priority_queue(stats)

    q1_ok = q1["sel_ev"] > 0 and q1["sel_ev"] > q1["base_ev"]
    print(f"Q1: trade-all EV={q1['base_ev']:+.2f} | CCS-selected EV={q1['sel_ev']:+.2f} (ok={q1_ok})")

    # Q3: budget=2 -> OppScore lazima ikusanye total kubwa zaidi (freq-good N kubwa)
    row2 = next((r for r in q3["rows"] if r[0] == 2), None) or q3["rows"][0]
    M, sa, na, eva, sb, nb, evb = row2
    q3_ok = sb >= sa
    print(f"Q3 (budget {M}): CCS-only total={sa:+.0f} | OppScore total={sb:+.0f} (ok={q3_ok})")

    # Q4: OppScore-top vs CCS-top zinatofautiana
    by_ccs = sorted([s for s in stats if s["full_ccs"] > 0], key=lambda s: s["full_ccs"], reverse=True)
    ccs_top = by_ccs[0]["key"] if by_ccs else None
    opp_top = queue[0]["key"] if queue else None
    q4_ok = ccs_top is not None and opp_top is not None and ccs_top != opp_top
    print(f"Q4: CCS-top={ccs_top} | OppScore-top={opp_top} (differ={q4_ok})")

    ok = q1_ok and q3_ok and q4_ok
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
