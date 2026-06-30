"""
semantic_consistency_engine.py — PHASE 23 (Chief Quant).

Phase 22 ilithibitisha (APPROVED): clusters zinaweza kupewa market-language labels
(Compression, High-Volatility Regime, Balanced Flow…) na vocabulary inajirudia cross-pair.
Chief alirekebisha verdict: R²(label) kushuka SI failure ya semantics — semantics inalenga
INTERPRETABILITY, sio prediction (Principle 48). Discovery kubwa: **vocabulary ile ile
inajitokeza kwenye events tofauti** -> labda tunagundua *Universal Market States*, sio Event
States (F-040, OPEN).

LAKINI: ramani ni deterministic na thresholds ni human-designed -> vocabulary BADO
haijajitegemea. Doctrine haiwezi kuifunga hadi iwe STABLE across representations (Principle
49). Phase 23: Semantic Consistency Audit.

Maswali (Chief):
  Q1. Je labels zile zile zinamaanisha profile ile ile kwa pairs ZOTE? (cross-pair)
  Q2. Je "Compression" kwenye Pullback ni sawa na "Compression" kwenye Breakout? (cross-event)
  Q3. Je labels zina stability ukibadilisha thresholds? (perturbation -> ARI)
  Q4. Je labels zinaweza kujengwa DATA-DRIVEN badala ya deterministic rules? (meta-cluster ARI)
  Q5. Je semantic vocabulary inaweza kuwa UNIVERSAL wakati geometry inabaki event-specific?
      (swali muhimu zaidi — F-040)

Mbinu: kusanya per-(pair,event) cluster profiles + labels (reuse Phase 22), global-
standardize, pima dispersion ndani ya kila label (cross-pair, cross-event), perturb
thresholds, na meta-cluster profiles (data-driven) -> linganisha na rule labels. NO ML.

Reuse: semantic_taxonomy_engine (cluster_and_label, semantic_label, FEAT, GENERIC,
distinctiveness, ZTHR), taxonomy_robustness_engine (build_event_xy_ts), latent_structure
(kmeans), cluster_robustness (ari), market_state_engine (cfg).

Output: reports/semantic_consistency_report.md
Self-test: python src/research/semantic_consistency_engine.py --self-test
"""
from __future__ import annotations

import argparse, sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np

from market_state_engine import cfg
from latent_structure import kmeans
from cluster_robustness import ari
from taxonomy_robustness_engine import build_event_xy_ts
from semantic_taxonomy_engine import (cluster_and_label, semantic_label, distinctiveness,
                                      FEAT, GENERIC, ZTHR, CAP)

REPO_ROOT = Path(__file__).resolve().parents[2]
EVENTS_ORDER = ["pullback", "deep_pullback", "trend_continuation", "breakout", "mean_reversion"]
CONS_THR = 0.70       # within-label spread / overall spread chini ya hii = consistent
PERTURB = 0.20        # ±20% kwenye thresholds (Q3)


def _gstd(P):
    """Global standardize matrix ya profiles (kila feature kwa scale sawa)."""
    mu = P.mean(0); sd = P.std(0); sd[sd < 1e-9] = 1.0
    return (P - mu) / sd, mu, sd


def _spread(Pz):
    """RMS distance kwa centroid (dispersion ya seti ya profiles, standardized space)."""
    if len(Pz) < 2:
        return 0.0
    c = Pz.mean(0)
    return float(np.sqrt(((Pz - c) ** 2).sum(1).mean()))


def collect(pairs, rng):
    """Rudisha list ya records: dict(pair,event,label,raw,z,distinct,n)."""
    recs = []
    for sym in pairs:
        d1, _ = build_event_xy_ts([sym])
        for e, (X, y, ts) in d1.items():
            if len(X) < CAP // 2:
                continue
            _, info, _ = cluster_and_label(X, rng)
            for nfo in info:
                if nfo["n"] > 0:
                    recs.append(dict(pair=sym, event=e, label=nfo["label"],
                                     raw=np.asarray(nfo["raw"], float),
                                     z=np.asarray(nfo["z"], float),
                                     distinct=nfo["distinct"], n=nfo["n"]))
        print(f"  collected {sym}", flush=True)
    return recs


def analyze(recs):
    """Compute Q1–Q5 metrics kutoka kwa records."""
    P = np.array([r["raw"] for r in recs])
    Pz, _, _ = _gstd(P)
    for i, r in enumerate(recs):
        r["pz"] = Pz[i]
    labels = sorted({r["label"] for r in recs})
    overall = _spread(Pz)

    # Q1 cross-pair: kwa kila label, dispersion ya per-pair centroids
    # Q2 cross-event: kwa kila label, dispersion ya per-event centroids
    perlabel = {}
    for lab in labels:
        sub = [r for r in recs if r["label"] == lab]
        Pz_lab = np.array([r["pz"] for r in sub])
        within = _spread(Pz_lab)
        # per-pair centroids
        by_pair = defaultdict(list)
        for r in sub:
            by_pair[r["pair"]].append(r["pz"])
        pair_cents = np.array([np.mean(v, 0) for v in by_pair.values()])
        # per-event centroids
        by_evt = defaultdict(list)
        for r in sub:
            by_evt[r["event"]].append(r["pz"])
        evt_cents = np.array([np.mean(v, 0) for v in by_evt.values()])
        perlabel[lab] = dict(
            n=len(sub), n_pairs=len(by_pair), n_events=len(by_evt),
            within=within, ratio=within / overall if overall > 1e-9 else 0.0,
            crosspair=_spread(pair_cents), crossevent=_spread(evt_cents),
            events=sorted(by_evt.keys()))
    return Pz, labels, overall, perlabel


def q3_threshold_stability(recs, rng):
    """Perturb thresholds ±PERTURB -> ARI kati ya base labels na perturbed."""
    base = np.array([_code(r["label"]) for r in recs])
    aris = []
    for dz in (1 - PERTURB, 1 + PERTURB):
        for dt in (1 - PERTURB, 1 + PERTURB):
            new = []
            for r in recs:
                new.append(_code(semantic_label(r["raw"], r["z"],
                                                zthr=ZTHR * dz, trajt=0.15 * dt)))
            aris.append(ari(base, np.array(new)))
    return float(np.mean(aris)), float(np.min(aris))


def q4_data_driven(Pz, recs):
    """Meta-cluster profiles (data-driven) -> ARI na rule labels."""
    rng = np.random.default_rng(23)
    klab = len({r["label"] for r in recs})
    k = max(2, min(klab, len(Pz) - 1))
    meta = kmeans(Pz, k, rng)[0]
    rule = np.array([_code(r["label"]) for r in recs])
    return ari(meta, rule), k


_CODES = {}
def _code(lab):
    return _CODES.setdefault(lab, len(_CODES))


def run(pairs, rng):
    c = cfg()
    if len(pairs) < 2:
        print("HITILAFU: Phase 23 inahitaji pairs ≥2 (cross-pair consistency).", file=sys.stderr)
        return 1
    print("Collecting per-(pair,event) cluster profiles...", flush=True)
    recs = collect(pairs, rng)
    if len(recs) < 6:
        print("HITILAFU: hakuna profiles za kutosha (angalia OHLC/state parquet).", file=sys.stderr)
        return 1
    Pz, labels, overall, perlabel = analyze(recs)
    q3_mean, q3_min = q3_threshold_stability(recs, rng)
    q4_ari, q4_k = q4_data_driven(Pz, recs)
    return _report(c, pairs, recs, labels, overall, perlabel, q3_mean, q3_min, q4_ari, q4_k)


def _report(c, pairs, recs, labels, overall, perlabel, q3_mean, q3_min, q4_ari, q4_k):
    n_evt_total = len({r["event"] for r in recs})
    L = ["# Semantic Consistency Audit — je vocabulary ni stable & universal? (Phase 23)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | {len(pairs)} pairs, {n_evt_total} events, {len(recs)} clusters | "
         f"global-standardized profiles | threshold perturbation ±{PERTURB:.0%} | data-driven meta-cluster | NO ML*\n",
         "> **Principle 48 (Chief):** semantic abstraction = INTERPRETABILITY, sio lazima prediction "
         "(R² kushuka SI failure). **Principle 49:** vocabulary lazima iwe STABLE across representations "
         "kabla ya doctrine. **Principle 50:** interpretability & predictability ni complementary, sio "
         "interchangeable. **F-040 (OPEN):** events zinaweza kushiriki vocabulary moja ya soko licha ya "
         "geometry tofauti (Universal Market States?). NO ML."]

    # Q1 + Q2 — per-label consistency (cross-pair / cross-event)
    L.append("\n## Q1+Q2 — Je label ile ile = profile ile ile? (cross-pair & cross-event)\n")
    L.append(f"*overall between-cluster spread = {overall:.3f} (standardized). within/overall < {CONS_THR} = consistent.*\n")
    L.append("| label | N | #pairs | #events | within-spread | within/overall | cross-pair | cross-event | consistent? |")
    L.append("|-------|---|--------|---------|---------------|----------------|-----------|-------------|-------------|")
    n_consistent = 0
    for lab in sorted(labels, key=lambda x: -perlabel[x]["n"]):
        m = perlabel[lab]
        cons = m["ratio"] < CONS_THR and m["n"] >= 3
        n_consistent += int(cons)
        L.append(f"| {lab} | {m['n']} | {m['n_pairs']} | {m['n_events']} | {m['within']:.3f} | "
                 f"{m['ratio']:.2f} | {m['crosspair']:.3f} | {m['crossevent']:.3f} | {'✅' if cons else '—'} |")
    L.append(f"\n- **Q1/Q2 consistent labels** (within/overall < {CONS_THR}, N≥3): **{n_consistent}/{len(labels)}**")
    # Q2 spotlight: same label across events
    multi_evt = [lab for lab in labels if perlabel[lab]["n_events"] >= 2]
    if multi_evt:
        ex = min(multi_evt, key=lambda x: perlabel[x]["crossevent"])
        L.append(f"- **Q2 spotlight:** label inayoshirikiwa na events nyingi yenye cross-event spread ndogo zaidi: "
                 f"**{ex}** ({perlabel[ex]['n_events']} events: {', '.join(perlabel[ex]['events'])}; "
                 f"cross-event spread {perlabel[ex]['crossevent']:.3f}) → profile inafanana cross-event.")

    # Q3 — threshold stability
    L.append("\n## Q3 — Je labels zina stability ukibadilisha thresholds (±{:.0%})?\n".format(PERTURB))
    L.append(f"- ARI(base, perturbed): **mean {q3_mean:.3f}, min {q3_min:.3f}** (kwa perturbations 4)")
    L.append(f"\n→ {'✅ labels ni stable kwa threshold perturbation (ARI juu)' if q3_min >= 0.6 else '⚠️ labels zinabadilika sana na thresholds (human-designed boundary tete)'}.")

    # Q4 — data-driven recoverability
    L.append("\n## Q4 — Je vocabulary inaweza kujengwa DATA-DRIVEN (sio deterministic rules)?\n")
    L.append(f"- meta-cluster ya profiles (k={q4_k}) vs rule labels: **ARI = {q4_ari:.3f}**")
    L.append(f"\n→ {'✅ rule vocabulary INA-recoverable data-driven (sio arbitrary)' if q4_ari >= 0.5 else '⚠️ rule labels HAZI-recover data-driven — vocabulary inategemea human thresholds'}.")

    # Q5 — universal vocabulary vs event-specific geometry
    L.append("\n## Q5 — Je vocabulary ni UNIVERSAL wakati geometry inabaki event-specific? (F-040)\n")
    shared_consistent = [lab for lab in labels
                         if perlabel[lab]["n_events"] >= max(2, n_evt_total - 1)
                         and perlabel[lab]["ratio"] < CONS_THR and perlabel[lab]["n"] >= 3]
    L.append(f"- core vocabulary (inashirikiwa na ≥{max(2, n_evt_total - 1)}/{n_evt_total} events + consistent): "
             f"**{len(shared_consistent)}** ({', '.join(shared_consistent) if shared_consistent else '—'})")
    L.append(f"- geometry: event-specific (F-039, APPROVED — OOS silhouette range 0.45–0.64)")
    q5 = len(shared_consistent) >= 1 and q3_min >= 0.6 and q4_ari >= 0.5
    L.append(f"\n→ {'✅ DALILI za vocabulary universal juu ya geometry event-specific (F-040 inaungwa mkono)' if q5 else '⚠️ bado: vocabulary haijaonyesha universality thabiti (F-040 haijaungwa mkono kikamilifu)'}.")

    # VERDICT
    L.append("\n## VERDICT — Phase 23 Semantic Consistency Audit\n")
    ok = n_consistent >= max(1, len(labels) // 2) and q3_min >= 0.6 and q4_ari >= 0.5 and len(shared_consistent) >= 1
    if ok:
        L.append(f"→ ✅ **vocabulary ni consistent & ina dalili za universality**: {n_consistent}/{len(labels)} labels "
                 f"consistent cross-pair/event, stable kwa thresholds (ARI min {q3_min:.2f}), recoverable data-driven "
                 f"(ARI {q4_ari:.2f}), na core vocabulary ({len(shared_consistent)}) inashirikiwa cross-event. "
                 "**F-040 inaungwa mkono** (bado OPEN hadi data-driven vocabulary ithibitishwe). Inayofuata: "
                 "Reality Validation ya alpha juu ya semantic states. NO ML bado.")
    else:
        gaps = []
        if n_consistent < max(1, len(labels) // 2): gaps.append("labels nyingi si consistent cross-pair/event")
        if q3_min < 0.6: gaps.append(f"si stable kwa thresholds (ARI min {q3_min:.2f})")
        if q4_ari < 0.5: gaps.append(f"hazirecover data-driven (ARI {q4_ari:.2f})")
        if not shared_consistent: gaps.append("hakuna core vocabulary universal")
        L.append(f"→ ⚠️ **vocabulary BADO haijawa stable/universal**: {', '.join(gaps)}. Per Principle 49, "
                 "haiwezi kuingia doctrine bado; inahitaji data-driven vocabulary + uthibitisho zaidi.")
    L.append("\n**Bado tuko 'Market Understanding Era'** — semantics ya kueleweka ni hatua, sio alpha "
             "(Principle 48/50). Hakuna semantic labels kwenye Opportunity Engine hadi consistency ithibitike.")

    # HONEST CAVEATS
    L.append("\n## Honest Caveats\n")
    L.append("1. **Consistency ya rule labels SI uthibitisho wa universality halisi** — bado tunapima output ya "
             "ramani ya human thresholds. Q4 (data-driven recoverability) ndiyo jaribio gumu zaidi; ndiyo maana "
             "F-040 inabaki OPEN hadi vocabulary ijengwe data-driven kabisa.")
    L.append("2. **'Same profile' inapimwa kwenye standardized FEAT space** — uchaguzi wa features/normalization "
             "unaweza kubadili spread; consistency ni relative kwa representation hii, sio absolute.")
    L.append(f"3. **CONS_THR={CONS_THR}, perturbation ±{PERTURB:.0%} ni human choices.** Verdict ni sensitive kwa "
             "thresholds hizi (ndiyo hoja ya Phase 23 yenyewe — irony imekiriwa).")
    L.append("4. **Universal vocabulary ≠ universal edge (Principle 40/48).** Hata kama 'Compression' ni dhana sawa "
             "cross-event, haimaanishi ina alpha sawa — wala alpha yoyote. Hii ni lugha, sio faida.")
    L.append("5. **Cross-event 'sameness' ya label haisemi clusters ni same OBJECT** — geometry ni event-specific "
             "(F-039). Profile sawa kwenye standardized space ≠ mechanism sawa ya soko.")

    L.append("\n*Global-standardized profiles; within/overall spread; threshold perturbation ARI; data-driven "
             "meta-cluster ARI. Principle 48/49/50. F-040 OPEN. NO ML. Profitable ≠ Tradable Edge.*")

    out = REPO_ROOT / c["paths"]["reports"] / "semantic_consistency_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)} (consistent {n_consistent}/{len(labels)}, "
          f"Q3 min ARI {q3_min:.2f}, Q4 ARI {q4_ari:.2f}, core vocab {len(shared_consistent)})")
    return 0


def self_test():
    rng = np.random.default_rng(23)
    # Jenga records za bandia: labels mbili thabiti (A,B) zinazoshirikiwa na events 2 & pairs 2,
    # kila label ina profile tofauti lakini consistent ndani.
    FEATN = len(FEAT)
    def mk(label, base, pair, event, n=200):
        raw = base + rng.normal(0, 0.03, FEATN)
        z = (raw - 0.5)            # z bandia (consistent na profile)
        return dict(pair=pair, event=event, label=label, raw=raw, z=z,
                    distinct=1.0, n=n)
    profA = np.array([2.0, 1.5, 0.0, 0.2, 1.0, 5.0, 0.0])   # high vol
    profB = np.array([0.0, 0.0, 0.0, 0.05, 0.0, 4.0, 0.0])  # low vol
    recs = []
    for pr in ("P1", "P2"):
        for ev in ("pullback", "breakout"):
            recs.append(mk("LabA", profA, pr, ev))
            recs.append(mk("LabB", profB, pr, ev))

    Pz, labels, overall, perlabel = analyze(recs)
    cons = all(perlabel[l]["ratio"] < CONS_THR for l in labels)
    multi = all(perlabel[l]["n_events"] == 2 and perlabel[l]["n_pairs"] == 2 for l in labels)
    print(f"consistency: labels={labels} ratios={[round(perlabel[l]['ratio'],2) for l in labels]} "
          f"-> {'OK' if cons else 'FAIL'}; cross-pair/event coverage -> {'OK' if multi else 'FAIL'}")

    # Q4: meta-cluster ya profiles za A/B (tofauti sana) -> ARI=1 na rule labels
    _CODES.clear()
    q4_ari, q4_k = q4_data_driven(Pz, recs)
    ok_q4 = q4_ari >= 0.9
    print(f"data-driven recoverability: ARI={q4_ari:.2f} (k={q4_k}) -> {'OK' if ok_q4 else 'FAIL'}")

    # Q3: threshold perturbation kwenye semantic_label halisi (profiles designed)
    _CODES.clear()
    A = np.array([2.0, 1.5, 0.0, 0.2, 1.0, 5.0, 0.0]); zA = np.array([1.5, 1.0, 0, 1.0, 1.0, 0.5, 0])
    B = np.array([0.0, 0.0, 0.0, 0.05, 0.0, 4.0, 0.0]); zB = np.array([-1.5, -1.0, 0, -1.0, 0, -0.2, 0])
    rs = [dict(raw=A, z=zA, label=semantic_label(A, zA)), dict(raw=B, z=zB, label=semantic_label(B, zB))]
    q3_mean, q3_min = q3_threshold_stability(rs, rng)
    ok_q3 = q3_min >= 0.6
    print(f"threshold stability: ARI mean {q3_mean:.2f} min {q3_min:.2f} -> {'OK' if ok_q3 else 'FAIL'}")

    ok = cons and multi and ok_q4 and ok_q3
    print(f"\nSELF-TEST: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    c = cfg()
    return run(c["pairs"], np.random.default_rng(23))


if __name__ == "__main__":
    raise SystemExit(main())
