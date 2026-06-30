"""
decision_value_framework_engine.py — PHASE 26 (Chief Quant).

Phase 25: F-042 (primitives = ecological layer yenye thamani ya calibration/weighting)
**REJECTED** — ΔBrier ≈ 0 (0/5), JS ≈ 0 (ecology haibagui events), weighting haina decision
value. Chief: ecology ni **background property** (kama hali ya hewa), sio discriminator.

Mwisho wa **Market Understanding Era**. Lengo jipya la ELITEFX:
  "Hatutatafuta tena structure mpya ya market. Tutatafuta structure inayobadilisha MAAMUZI."

  Principle 56: market ecology ni background property, sio event discriminator.
  Principle 57: primitives ni descriptive METADATA hadi decision value huru ithibitishwe.

Swali jipya (sio prediction, bali DECISION): variable/finding gani imewahi kubadilisha UAMUZI?

Maswali (Chief):
  Q1. Ni variables zipi zimewahi kubadilisha DECISION? (sio prediction)
  Q2. Kwa kila Principle, onyesha decision value yake.
  Q3. Ni findings zipi hazijawahi kubadilisha decision? (ziondolewe)
  Q4. Jenga Decision Graph: Representation → Decision → Execution.
  Q5. Kila variable ipewe score: Prediction Value | Decision Value | Explanation Value.

Mbinu (data-driven kwa variables): kwa kila variable —
  Prediction Value (PV)  = r2_label(outcome | variable levels)           [prediction]
  Decision Value  (DV)   = OOS time-split SELECTION ΔEV: chagua levels zenye train-EV>0,
                            linganisha realized EV (OOS) na "trade-all"                 [DECISION]
  Explanation Value (XV) = distinctiveness ya level-profiles (standardized FEAT)        [understanding]
Q2/Q3 = curated doctrine audit (decision-relevance ya principles/findings). NO ML.

Reuse: ecology_interaction_engine (build_ecology), event_taxonomy_engine (FEAT, r2_label),
market_state_engine (cfg).

Output: reports/decision_value_framework_report.md
Self-test: python src/research/decision_value_framework_engine.py --self-test
"""
from __future__ import annotations

import argparse, sys
from datetime import datetime
from pathlib import Path

import numpy as np

from market_state_engine import cfg
from event_taxonomy_engine import FEAT, r2_label
from ecology_interaction_engine import build_ecology

REPO_ROOT = Path(__file__).resolve().parents[2]
DV_THR = 0.05            # pip — decision value threshold (OOS ΔEV)
PV_THR = 0.02            # r2 — prediction value threshold
XV_THR = 0.50            # distinctiveness — explanation value threshold
TRAIN_FRAC = 0.60


def decision_value(levels, y, frac=TRAIN_FRAC):
    """OOS SELECTION ΔEV: train EV per level → chagua levels EV>0 → realized OOS EV vs trade-all.
    +ve = kujua variable kunaboresha UAMUZI wa kuchagua (sio prediction). Rudisha (ΔEV, coverage)."""
    n = len(y); cut = int(n * frac)
    if cut < 20 or n - cut < 20:
        return 0.0, 0.0
    trl, try_ = levels[:cut], y[:cut]; tel, tey = levels[cut:], y[cut:]
    sel = {L for L in np.unique(trl) if try_[trl == L].mean() > 0}
    if not sel:
        return 0.0, 0.0
    mask = np.isin(tel, list(sel))
    if mask.sum() == 0:
        return 0.0, 0.0
    return float(tey[mask].mean() - tey.mean()), float(mask.mean())


def explanation_value(levels, Xz):
    """Mean (n-weighted) distinctiveness ya level-profiles kwenye standardized FEAT space."""
    tot = 0.0; w = 0
    for L in np.unique(levels):
        m = levels == L; nL = int(m.sum())
        if nL < 10:
            continue
        prof = Xz[m].mean(0)
        tot += nL * float(np.max(np.abs(prof))); w += nL
    return tot / w if w else 0.0


def _bucket(x, edges):
    return np.digitize(x, edges)


def build_variables(df):
    """Rudisha {varname: level_codes (time order)}, Xz (standardized FEAT), y."""
    y = df["y"].to_numpy().astype(float)
    Xraw = np.column_stack([df[f].to_numpy().astype(float) for f in FEAT])
    mu = Xraw.mean(0); sd = Xraw.std(0); sd[sd < 1e-9] = 1.0
    Xz = (Xraw - mu) / sd
    def codes(arr):
        _, c = np.unique(np.asarray(arr), return_inverse=True)
        return c
    age = df["age"].to_numpy().astype(float)
    atr = df["atr"].to_numpy().astype(float)
    qa = np.quantile(atr, [1/3, 2/3])
    variables = {
        "event": codes(df["event"].to_list()),
        "primitive": codes(df["prim"].to_list()),
        "vol": codes(np.round(df["vol"].to_numpy()).astype(int)),
        "activity": codes(np.round(df["act"].to_numpy()).astype(int)),
        "spread": codes(np.round(df["spr"].to_numpy()).astype(int)),
        "trajectory": codes(np.round(df["traj"].to_numpy()).astype(int)),
        "transition": codes(np.round(df["trans"].to_numpy()).astype(int)),
        "age_bucket": _bucket(age, [6, 16]),
        "atr_bucket": _bucket(atr, qa),
    }
    return variables, Xz, y


# ---------- Q2/Q3 curated doctrine audit ----------
# (Decision = ilibadilisha SELECTION/accept-reject/sizing; Explanation/Method = ilibadilisha uelewa/mbinu)
PRINCIPLE_AUDIT = [
    ("P19  No finding without decision-quality impact", "DECISION"),
    ("P21  Selection > Prediction", "DECISION"),
    ("P23  Rank Configurations, don't classify Trades", "DECISION"),
    ("P24  No ranking by Expected Payoff alone", "DECISION"),
    ("P25  Opportunity = Quality × Availability × Survivability", "DECISION"),
    ("P26  Capital preservation before opportunity discovery", "DECISION"),
    ("P40  A valid taxonomy is not alpha", "DECISION (negative — stops trading taxonomy)"),
    ("P57  Primitives are descriptive metadata until decision value", "DECISION (gatekeeper)"),
    ("P38  No universal representation; each Event its own", "EXPLANATION"),
    ("P44  Normalization is part of the representation", "EXPLANATION"),
    ("P46  Taxonomy incomplete until semantically interpretable", "EXPLANATION"),
    ("P48  Semantics = interpretability, not prediction", "EXPLANATION"),
    ("P53  Primitives describe environment, not generate events", "EXPLANATION"),
    ("P56  Market ecology is a background property", "EXPLANATION"),
    ("P18  Decision quality > algorithm agreement", "METHOD"),
    ("P29  Every event is a hypothesis, not a signal", "METHOD"),
    ("P39  Ontology never from one clustering algorithm", "METHOD"),
    ("P45  Operational robustness ≠ statistical stability", "METHOD"),
]
FINDING_AUDIT = [
    ("F-019 Representation improves EV-selection", "DECISION"),
    ("F-020 Edge = Event × Configuration", "DECISION"),
    ("F-022 Bad configurations persist more than good", "DECISION (where-NOT-to-trade)"),
    ("F-025 Edge = Magnitude × Availability", "DECISION"),
    ("F-028 Every edge has a lifecycle", "DECISION"),
    ("F-029 Edge decay = market non-stationarity", "EXPLANATION"),
    ("F-036 Variables are conditional entities", "EXPLANATION"),
    ("F-039 Events need different geometries (deployment)", "EXPLANATION"),
    ("F-040 Shared semantic vocabulary across events", "EXPLANATION"),
    ("F-041 Universal causal primitives", "REJECTED — no decision value"),
    ("F-042 Primitives = ecological conditions", "REJECTED — no decision value"),
    ("F-033 A representation can fail while structure exists", "EXPLANATION"),
]


def run(pairs, rng):
    c = cfg()
    print("Building occurrences for decision-value audit...", flush=True)
    df, info, nbars, no_px = build_ecology(pairs, rng)
    if no_px:
        print("HITILAFU: state parquet haina OHLC. Endesha market_state_engine.py kwanza.", file=sys.stderr)
        return 1
    if df is None or df.height < 200:
        print("HITILAFU: occurrences hazitoshi.", file=sys.stderr)
        return 1
    print(f"  {df.height:,} occurrences", flush=True)
    variables, Xz, y = build_variables(df)
    scores = {}
    for name, lev in variables.items():
        pv = r2_label(y, lev)
        dv, cov = decision_value(lev, y)
        xv = explanation_value(lev, Xz)
        scores[name] = dict(pv=pv, dv=dv, cov=cov, xv=xv, nlev=len(np.unique(lev)))
    return _report(c, pairs, df, scores)


def _report(c, pairs, df, scores):
    L = ["# Decision Value Framework — structure gani inabadilisha MAAMUZI? (Phase 26)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | {len(pairs)} pairs, {df.height:,} occurrences | "
         f"PV=r²(outcome) · DV=OOS selection ΔEV · XV=profile distinctiveness | NO ML*\n",
         "> **Mwisho wa Market Understanding Era.** Lengo jipya: tafuta structure inayobadilisha "
         "**DECISION**, sio market structure mpya. **Principle 56** (ecology = background property). "
         "**Principle 57** (primitives = descriptive metadata hadi decision value huru). DV ndiyo "
         "north star mpya — selection OOS, sio prediction. NO ML."]

    # Q5 + Q1 — scoreboard
    L.append("\n## Q5 + Q1 — Scoreboard: Prediction vs Decision vs Explanation value\n")
    L.append(f"*DV = OOS ΔEV (pip) ya kuchagua levels zenye train-EV>0 vs trade-all. "
             f"DV>{DV_THR} = ina decision value; PV>{PV_THR}; XV>{XV_THR}.*\n")
    L.append("| variable | #levels | PV (predict) | DV (decide, pip) | coverage | XV (explain) | decision? |")
    L.append("|----------|---------|--------------|------------------|----------|--------------|-----------|")
    for name in sorted(scores, key=lambda x: -scores[x]["dv"]):
        s = scores[name]
        dec = s["dv"] > DV_THR
        L.append(f"| {name} | {s['nlev']} | {s['pv']:.3f} | {s['dv']:+.3f} | {s['cov']:.0%} | {s['xv']:.2f} | "
                 f"{'✅' if dec else '—'} |")
    dvars = [n for n in scores if scores[n]["dv"] > DV_THR]
    L.append(f"\n- **Q1 — variables zenye DECISION value** (DV>{DV_THR} pip OOS): "
             f"**{', '.join(dvars) if dvars else 'HAKUNA'}** ({len(dvars)}/{len(scores)}).")
    # axis classification
    L.append("- **Axis classification:**")
    for name in sorted(scores, key=lambda x: -scores[x]["dv"]):
        s = scores[name]
        tags = []
        if s["dv"] > DV_THR: tags.append("Decision")
        if s["pv"] > PV_THR: tags.append("Prediction")
        if s["xv"] > XV_THR: tags.append("Explanation")
        L.append(f"  - `{name}`: {', '.join(tags) if tags else 'none (candidate for removal)'}")

    # Q3 — variables with no decision value
    nodv = [n for n in scores if scores[n]["dv"] <= DV_THR]
    L.append(f"\n## Q3 — Variables/findings ZISIZO na decision value (candidate for removal)\n")
    L.append(f"- variables DV≤{DV_THR}: **{', '.join(nodv) if nodv else '—'}**")
    L.append("- findings REJECTED (no decision value): " +
             ", ".join(f for f, t in FINDING_AUDIT if t.startswith("REJECTED")))

    # Q2 — principle decision audit
    L.append("\n## Q2 — Principle decision-audit (curated)\n")
    L.append("| Principle | Decision value? |")
    L.append("|-----------|-----------------|")
    for p, t in PRINCIPLE_AUDIT:
        L.append(f"| {p} | {t} |")
    ndec = sum(1 for _, t in PRINCIPLE_AUDIT if t.startswith("DECISION"))
    L.append(f"\n- principles zenye decision value: **{ndec}/{len(PRINCIPLE_AUDIT)}** "
             "(zilizobaki ni explanation/method — muhimu kwa uelewa/uadilifu, sio kubadilisha uamuzi moja kwa moja).")

    # Q2b — finding audit
    L.append("\n### Finding decision-audit (curated)\n")
    L.append("| Finding | Decision value? |")
    L.append("|---------|-----------------|")
    for f, t in FINDING_AUDIT:
        L.append(f"| {f} | {t} |")

    # Q4 — Decision Graph
    L.append("\n## Q4 — Decision Graph\n")
    L.append("```text")
    L.append("Representation (Event × Configuration; geometry event-specific)")
    L.append("        │   feeds (variables zenye DV>0):")
    L.append(f"        │     {', '.join(dvars) if dvars else '(hakuna data-driven DV variable bado)'}")
    L.append("        ▼")
    L.append("Decision  (SELECT survivable Configurations: where-NOT-to-trade first → rank → size)")
    L.append("        │   gated by: P19/P21/P23/P24/P25/P26/P40/P57")
    L.append("        ▼")
    L.append("Execution (spread/cost-aware entry; capital preservation first)")
    L.append("```")
    L.append("\n- ecology/primitive (P56/57) ni **background metadata** — hazijaunganishwa kwenye Decision "
             "hadi zionyeshe DV huru.")

    # VERDICT
    L.append("\n## VERDICT — Phase 26 Decision Value Framework\n")
    if dvars:
        L.append(f"→ ✅ **{len(dvars)}/{len(scores)} variables zina DECISION value ya OOS** ({', '.join(dvars)}): "
                 "hizi zinabadilisha selection (where-NOT-to-trade / rank), sio prediction tu. Variables/"
                 "findings zisizo na DV zimeorodheshwa kwa kuondolewa au kushushwa kuwa metadata. Decision Graph "
                 "imejengwa. Inayofuata: **Ecology-/Decision-aware Reality Validation** juu ya DV-variables tu. NO ML.")
    else:
        L.append("→ ⚠️ **HAKUNA variable yenye DECISION value ya OOS chini ya vipimo vya sasa** (DV≤thr kote). Hii "
                 "ni discovery muhimu, sio failure: inathibitisha pengo la **decision theory** — tuna representation "
                 "nzuri lakini bado hakuna variable inayobadilisha uamuzi OOS. Inayofuata: redefine 'decision' "
                 "(sizing/abstention/portfolio), sio variable mpya. NO ML.")
    L.append("\n**Tahadhari ya kisayansi (Chief):** kushindwa kuonyesha decision value chini ya vipimo vya SASA "
             "hakuthibitishi kutokuwa na matumizi yoyote — kunathibitisha tu hakuna ushahidi kama signal/weighting/"
             "calibration ndani ya architecture ya sasa.")

    # HONEST CAVEATS
    L.append("\n## Honest Caveats\n")
    L.append(f"1. **DV ni time-split moja (60/40), sio walk-forward/CV** — ni dalili ya OOS selection, sio "
             "uthibitisho thabiti; coverage ndogo inaweza kuvimbisha ΔEV.")
    L.append("2. **DV haijapitia FDR/multiple-comparisons** — variables 9 zinajaribiwa; DV>0 ya bahati inawezekana "
             "(Principle 40/Phase 14 lesson). Hii ni screening, sio confirmation.")
    L.append("3. **Q2/Q3 principle/finding audit ni CURATED** (judgement ya implementer kutoka ledger), sio "
             "data-derived — ni ramani ya majadiliano, si kipimo.")
    L.append("4. **PV/XV zina overlap na FEAT** — variables nyingi ni features zenyewe, kwa hiyo XV ya juu inaweza "
             "kuwa self-explanation; PV ni descriptive, sio OOS.")
    L.append("5. **DV>0 ≠ tradable edge** — gharama, slippage, capacity, na non-stationarity hazijajumuishwa; "
             "hii ni decision-screening ndani ya research, Profitable ≠ Tradable Edge.")

    L.append("\n*PV=r²(outcome|levels); DV=OOS time-split selection ΔEV; XV=level-profile distinctiveness. "
             "Curated principle/finding audit. Principle 56/57. NO ML. Profitable ≠ Tradable Edge.*")

    out = REPO_ROOT / c["paths"]["reports"] / "decision_value_framework_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)} (DV-variables {len(dvars)}/{len(scores)})")
    return 0


def self_test():
    rng = np.random.default_rng(26)
    n = 4000
    # variable yenye DECISION value: level 'good' (=1) ina +EV thabiti train NA test; level 'bad' (=0) -EV.
    dvar = rng.integers(0, 2, n)
    # outcome: good level +0.6 pip, bad level -0.6 pip + noise (stationary -> OOS selection inafanya kazi)
    y = np.where(dvar == 1, 0.6, -0.6) + rng.normal(0, 1.0, n)
    # noise variable: hakuna uhusiano na y
    nvar = rng.integers(0, 3, n)
    Xz = rng.normal(0, 1, (n, len(FEAT)))

    dv_good, cov = decision_value(dvar, y)
    dv_noise, _ = decision_value(nvar, y)
    pv_good = r2_label(y, dvar); pv_noise = r2_label(y, nvar)
    ok_dv = dv_good > DV_THR and dv_noise <= DV_THR
    ok_pv = pv_good > pv_noise
    print(f"DV: good={dv_good:+.3f} (cov {cov:.0%}) noise={dv_noise:+.3f} -> {'OK' if ok_dv else 'FAIL'}")
    print(f"PV: good={pv_good:.3f} noise={pv_noise:.3f} -> {'OK' if ok_pv else 'FAIL'}")

    # XV: variable inayocarve FEAT (level inahusiana na feature 0) -> XV kubwa kuliko random
    lev = (Xz[:, 0] > 0).astype(int)
    Xz2 = Xz.copy(); Xz2[lev == 1, 0] += 3.0  # level 1 ina profile tofauti sana kwenye feature 0
    xv_struct = explanation_value(lev, (Xz2 - Xz2.mean(0)) / Xz2.std(0))
    xv_rand = explanation_value(rng.integers(0, 2, n), Xz)
    ok_xv = xv_struct > xv_rand and xv_struct > XV_THR
    print(f"XV: structured={xv_struct:.2f} random={xv_rand:.2f} -> {'OK' if ok_xv else 'FAIL'}")

    ok = ok_dv and ok_pv and ok_xv
    print(f"\nSELF-TEST: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    c = cfg()
    return run(c["pairs"], np.random.default_rng(26))


if __name__ == "__main__":
    raise SystemExit(main())
