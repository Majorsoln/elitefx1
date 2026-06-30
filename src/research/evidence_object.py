"""
evidence_object.py — DECISION SCIENCE PHASE D0 (Chief Quant).

The Split (V6.9): ELITEFX = Market Science + Decision Science. Chief amendment (Decision Doctrine
V2): Decision Science ni **consumer** wa Market Science; **Evidence Object** ndiyo contract/API
kati ya domains. Decision Science haianzi na decisions — inaanza na **Evidence Theory**.

  Principle 63: Evidence ni contractual interface kati ya Market & Decision Science.
  Principle 64: Decision Science haitegemei JINSI evidence ilivyozalishwa, bali validity + uncertainty.
  Principle 65: Evidence ni first-class object yenye lifecycle yake (huru na representation).
  Principle 66: kila decision lazima itrace kwa explicit evidence objects.

Hii ni **Evidence Object** (data structure + lifecycle + aggregation), SIO Decision Engine.
Hakuna decision-action yoyote hapa (Chief: hakuna Decision Engine hadi spec hii iidhinishwe).

Maswali (Chief, D0):
  Q1. Evidence Object ina fields gani? (value, confidence, uncertainty, support, coverage,
      freshness, conflict, source)
  Q2. Evidence mbili zikipingana, Decision Engine ifanye nini? (contract policy)
  Q3. Evidence inaisha muda lini? (lifecycle: fresh→stale→expired)
  Q4. Evidence ina aggregate vipi? (inverse-variance weighting; closed under aggregation)
  Q5. Decision inahitaji evidence kiasi gani? (sufficiency: min support/confidence/non-expired/low-conflict)

Mbinu: fasili Evidence Object + lifecycle + aggregation + sufficiency; HALAFU instantiate kutoka
real config evidence (event × vol × spread cells: EV, SE, n, recency) ili kuonyesha contract kwa
data halisi. NO decision actions. NO ML.

Reuse: market_state_engine (cfg, pip), latent_structure (state_path), event_library (EVENTS_ALL),
configuration_engine (EVENTS_SET, VERT), context_value (HORIZON), event_taxonomy_engine
(VLEVEL, _runlen), contextual_alpha_engine (_phi).

Output: reports/evidence_theory_report.md
Self-test: python src/research/evidence_object.py --self-test
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
from event_taxonomy_engine import VLEVEL, _runlen
from contextual_alpha_engine import _phi

REPO_ROOT = Path(__file__).resolve().parents[2]
TFS = ["H1", "H2", "H4", "D1"]
TTL_BARS = 2000          # evidence time-to-live (bars) kabla ya expiry
STALE_BARS = 800         # fresh -> stale
MIN_SUPPORT = 100        # sufficiency: min n
MIN_CONF = 0.60          # sufficiency: min confidence P(edge)
CONFLICT_CEIL = 0.35     # sufficiency: max conflict
EPS = 1e-9


# ---------- Evidence Object (first-class; Principle 65) ----------
# THREE LAYERS (Principle 67): Claim · Evidence Quality · Operational State.
# Flat aliases zinabaki kwa convenience; eo["layers"] ndiyo muundo rasmi wa P67.
def _identity(value, unc, support, coverage, source):
    """P75: immutable value-object identity = content hash ya CLAIM+QUALITY+source (sio operational
    state — readiness inabadilika kwa muda, P73, kwa hiyo haijumuishwi kwenye identity)."""
    import hashlib
    key = f"{value:.6f}|{unc:.6f}|{int(support)}|{coverage:.6f}|{source}"
    return hashlib.sha1(key.encode()).hexdigest()[:10]


def make_evidence(value, uncertainty, support, coverage, age_bars, source, conflict=0.0, audit=None,
                  parents=None, op="make"):
    """Construct an Evidence Object (3-layer value object; P67/P75). confidence = Φ(|value|/uncertainty).
    audit = chronological trail (P66); parents+op = provenance GRAPH edges (P72); id = immutable
    value-object identity (P75). Operations huzalisha objects mpya (pure, P71; immutable, P68)."""
    unc = float(max(uncertainty, EPS))
    conf = float(_phi(abs(value) / unc))
    fresh = _freshness(age_bars)
    direction = int(np.sign(value)) if value else 0
    eo = {
        # --- identity + provenance (P75 / P72) ---
        "id": _identity(value, unc, support, coverage, source),
        "parents": list(parents) if parents else [],     # provenance-graph in-edges
        "op": str(op),                                    # producing operation
        # --- flat aliases (convenience) ---
        "value": float(value), "direction": direction, "uncertainty": unc, "confidence": conf,
        "support": int(support), "coverage": float(coverage),
        "freshness": fresh, "age_bars": int(age_bars), "expired": fresh == "expired",
        "conflict": float(conflict), "source": str(source),
        "audit": list(audit) if audit else [f"make_evidence(src={source})"],
    }
    # --- P67: three explicit layers ---
    eo["layers"] = {
        "claim":       {"value": eo["value"], "direction": direction, "source": eo["source"]},
        "quality":     {"confidence": conf, "uncertainty": unc,
                        "support": eo["support"], "coverage": eo["coverage"]},
        "operational": {"freshness": fresh, "age_bars": eo["age_bars"],
                        "expired": eo["expired"], "conflict": eo["conflict"]},
    }
    return eo


def freeze(eo):
    """P68: read-only immutable view ya Evidence Object (operations huzalisha objects mpya)."""
    from types import MappingProxyType
    return MappingProxyType(dict(eo))


def _freshness(age_bars):
    if age_bars > TTL_BARS:
        return "expired"
    if age_bars > STALE_BARS:
        return "stale"
    return "fresh"


def is_expired(eo):
    return eo["freshness"] == "expired"


def aggregate(eos):
    """Q4: combine independent Evidence Objects via inverse-variance weighting. Closed under
    aggregation (rudisha Evidence Object). Conflict = sign-disagreement (uncertainty-weighted).
    NB (Principle 68): aggregation ni OPERATION ya nje juu ya objects immutable — canonical home
    ni evidence_operations.py (D1); hii inabaki kwa demo ya D0."""
    live = [e for e in eos if not is_expired(e)]
    if not live:
        return None
    w = np.array([1.0 / (e["uncertainty"] ** 2 + EPS) for e in live])
    v = np.array([e["value"] for e in live])
    agg_val = float((w * v).sum() / w.sum())
    agg_unc = float(np.sqrt(1.0 / w.sum()))
    # conflict: weighted fraction ya evidence inayopingana na ishara ya aggregate
    s = np.sign(agg_val) if agg_val != 0 else 1.0
    disagree = float((w[(np.sign(v) != s)].sum()) / w.sum())
    support = int(sum(e["support"] for e in live))
    coverage = float(min(1.0, sum(e["coverage"] for e in live)))
    age = int(min(e["age_bars"] for e in live))
    return make_evidence(agg_val, agg_unc, support, coverage, age,
                         source="aggregate(" + ",".join(sorted({e["source"] for e in live})) + ")",
                         conflict=disagree)


def conflict_policy(eo):
    """Q2 (contract-level, SIO Decision Engine): conflicting evidence -> widen uncertainty, lower
    confidence; high unresolved conflict -> default ABSTAIN (capital preservation, P26)."""
    if eo is None:
        return "ABSTAIN (no live evidence)"
    if eo["conflict"] >= CONFLICT_CEIL:
        return "ABSTAIN (high conflict — never silently pick a side)"
    if eo["conflict"] > 0:
        return "PROCEED with widened uncertainty / lowered confidence"
    return "PROCEED (no conflict)"


def decision_ready(eo):
    """Q5: evidence ni DECISION-READY tu juu ya thresholds wazi (P66 trace + P26 default).
    Principle 69: decision-ready ≠ trade-ready (object iko tayari kutumiwa na Decision Engine —
    SIO kwamba biashara ina faida)."""
    if eo is None or is_expired(eo):
        return False, "expired/none"
    if eo["support"] < MIN_SUPPORT:
        return False, f"support {eo['support']}<{MIN_SUPPORT}"
    if eo["confidence"] < MIN_CONF:
        return False, f"confidence {eo['confidence']:.2f}<{MIN_CONF}"
    if eo["conflict"] >= CONFLICT_CEIL:
        return False, f"conflict {eo['conflict']:.2f}≥{CONFLICT_CEIL}"
    return True, "decision-ready"


# alias ya nyuma (kabla ya P69 rename)
sufficient = decision_ready


# ---------- instantiate from real market evidence ----------
def build_cell_evidence(pairs):
    """Kwa kila (event × vol_state × spread_state) cell: Evidence Object kutoka EV/SE/n/recency.
    Per-series-correct: coverage = support / jumla ya eligible bars (population), ≤1; recency =
    bars kutoka mwisho wa series ya occurrence (min across occurrences = freshest)."""
    rows = {}
    total_elig = 0          # jumla ya eligible bars kwenye series zote (population denominator)
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
            spr = df["spr"].to_numpy(); spr = np.where(np.isfinite(spr), spr, 0.0)
            vol = df["volatility_state"].to_list(); sprst = df["spread_state"].to_list()
            n = len(close)
            sig = {e: EVENTS_ALL[e](close, high, low) for e in EVENTS_SET}
            for i in range(n):
                if i + HORIZON >= n or i + VERT >= n:
                    continue
                total_elig += 1
                rec_age = n - i                          # bars kutoka mwisho wa series HII
                for e in EVENTS_SET:
                    d = int(sig[e][i])
                    if d != 0:
                        key = (e, vol[i], "WIDE" if sprst[i] == "WIDE" else "tight")
                        y = float(d * (close[i + HORIZON] - close[i]) - spr[i])
                        rec = rows.setdefault(key, {"y": [], "min_recency": 10 ** 9})
                        rec["y"].append(y)
                        rec["min_recency"] = min(rec["min_recency"], rec_age)
        print(f"  {sym}: cells built", flush=True)
    evid = {}
    for key, rec in rows.items():
        y = np.array(rec["y"], float)
        if len(y) < 20:
            continue
        ev = float(y.mean()); se = float(y.std() / np.sqrt(len(y)) + EPS)
        # conflict = split-half sign disagreement
        half = len(y) // 2
        c = 0.0 if half < 5 else (0.0 if np.sign(y[:half].mean()) == np.sign(y[half:].mean()) else 1.0)
        age = int(rec["min_recency"])               # bars kutoka mwisho wa series ya occurrence freshest
        cov = len(y) / total_elig if total_elig else 0.0   # share ya population (≤1)
        evid[key] = make_evidence(ev, se, len(y), cov, age, source=f"cell:{key[0]}", conflict=c)
    return evid, no_px


def run(pairs, rng):
    c = cfg()
    print("Instantiating Evidence Objects from real market evidence...", flush=True)
    evid, no_px = build_cell_evidence(pairs)
    if no_px:
        print("HITILAFU: state parquet haina OHLC. Endesha market_state_engine.py kwanza.", file=sys.stderr)
        return 1
    if not evid:
        print("HITILAFU: hakuna evidence cells za kutosha.", file=sys.stderr)
        return 1
    return _report(c, pairs, evid)


def _report(c, pairs, evid):
    keys = list(evid)
    fresh = sum(1 for k in keys if evid[k]["freshness"] == "fresh")
    stale = sum(1 for k in keys if evid[k]["freshness"] == "stale")
    expired = sum(1 for k in keys if evid[k]["freshness"] == "expired")
    suff = [(k, *sufficient(evid[k])) for k in keys]
    n_suff = sum(1 for _, ok, _ in suff if ok)

    L = ["# Evidence Theory — fasili Evidence Object (Decision Science D0)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | {len(pairs)} pairs, {len(keys)} evidence cells | "
         f"Evidence Object spec + lifecycle + aggregation | NO Decision Engine | NO ML*\n",
         "> **Principle 63** Evidence = contract kati ya Market & Decision Science. **P64** "
         "production-agnostic. **P65** Evidence = first-class object yenye lifecycle. **P66** kila "
         "decision itrace kwa evidence. Decision Science inaanza na **Evidence**, sio decisions. "
         "Hii ni Evidence Object (data structure), SIO Decision Engine."]

    # Q1 — fields
    L.append("\n## Q1 — Evidence Object: fields\n")
    L.append("| field | maana | mfano (cell evidence) |")
    L.append("|-------|-------|------------------------|")
    ex = evid[keys[0]]
    L.append(f"| value | effect (pips), directionful | {ex['value']:+.3f} |")
    L.append(f"| confidence | P(edge)=Φ(\\|value\\|/uncertainty); reliability, SIO magnitude | {ex['confidence']:.2f} |")
    L.append(f"| uncertainty | standard error | {ex['uncertainty']:.3f} |")
    L.append(f"| support | sample size n | {ex['support']:,} |")
    L.append(f"| coverage | share ya population | {ex['coverage']:.3f} |")
    L.append(f"| freshness | fresh→stale→expired (lifecycle) | {ex['freshness']} |")
    L.append(f"| conflict | sign-instability (split-half) | {ex['conflict']:.2f} |")
    L.append(f"| source | provenance | {ex['source']} |")

    # Q3 — lifecycle
    L.append("\n## Q3 — Evidence lifecycle / expiry\n")
    L.append(f"- TTL = {TTL_BARS} bars (expired), stale > {STALE_BARS} bars.")
    L.append(f"- cells: **fresh {fresh}**, stale {stale}, **expired {expired}** (kati ya {len(keys)}).")
    L.append("- expired evidence **haiwezi** kusogeza decision (P66 inahitaji live trace).")

    # Q4 — aggregation
    L.append("\n## Q4 — Aggregation (inverse-variance; closed under aggregation)\n")
    by_event = {}
    for k in keys:
        by_event.setdefault(k[0], []).append(evid[k])
    L.append("| event | #cells | agg value | agg uncertainty | agg confidence | conflict |")
    L.append("|-------|--------|-----------|-----------------|----------------|----------|")
    for e in sorted(by_event):
        agg = aggregate(by_event[e])
        if agg is None:
            L.append(f"| {e} | {len(by_event[e])} | — (zote expired) | — | — | — |")
            continue
        L.append(f"| {e} | {len(by_event[e])} | {agg['value']:+.3f} | {agg['uncertainty']:.3f} | "
                 f"{agg['confidence']:.2f} | {agg['conflict']:.2f} |")
    L.append("\n*aggregate ni Evidence Object yenyewe (closed): inverse-variance weighted value, "
             "combined uncertainty, summed support, min freshness, conflict = uncertainty-weighted "
             "sign-disagreement.*")
    L.append("\n> ⚠️ **CONFIDENCE SATURATION:** kwa support kubwa (pooled cross-pair, maelfu) SE inakuwa "
             "ndogo sana → confidence = Φ(\\|value\\|/SE) → **1.00** kwa karibu kila aggregate. Kwa hiyo "
             "confidence=1.00 hapa ni artifact ya n kubwa, **SIO** ushahidi wa edge (Principle 58: reliability "
             "≠ magnitude ≠ OOS edge). Sufficiency-by-confidence inahitaji ku-recalibrate-iwa OOS (sio in-sample SE).")

    # Q2 — conflict policy
    L.append("\n## Q2 — Conflict policy (contract-level, SIO Decision Engine)\n")
    L.append(f"- conflict ceiling = {CONFLICT_CEIL}. Sera: conflict → *widen uncertainty / lower "
             "confidence*; conflict ya juu isiyotatuliwa → **ABSTAIN** (P26 capital preservation; "
             "Decision Engine kamwe haichagui upande kimya).")
    L.append("| event | agg conflict | policy |")
    L.append("|-------|--------------|--------|")
    for e in sorted(by_event):
        agg = aggregate(by_event[e])
        cf = f"{agg['conflict']:.2f}" if agg else "—"
        L.append(f"| {e} | {cf} | {conflict_policy(agg)} |")

    # Q5 — sufficiency
    L.append("\n## Q5 — Sufficiency: decision inahitaji evidence kiasi gani?\n")
    L.append(f"- decision-READY tu kama: support ≥ {MIN_SUPPORT} **na** confidence ≥ {MIN_CONF} "
             f"**na** si expired **na** conflict < {CONFLICT_CEIL}.")
    L.append(f"- cells decision-ready: **{n_suff}/{len(keys)}**.")
    grade_neg = sum(1 for k in keys if sufficient(evid[k])[0] and evid[k]["value"] < 0)
    L.append(f"\n> ⚠️ **'Decision-ready' ≠ 'trade-ready' (Principle 69).** Kati ya {n_suff} decision-ready, **{grade_neg}** zina "
             "**value (EV) HASI** — yaani evidence ina ubora wa kutosha KUAMUA, na uamuzi unaoungwa mkono ni "
             "**ABSTAIN / avoid** (P26 capital preservation; F-022 bad-configs-persist), SIO *select/trade*. "
             "Evidence ni decision-READY kwa decision ya ABSTENTION, sio selection.")
    # mifano michache
    L.append("\n| cell | value | conf | support | fresh | conflict | sufficient? |")
    L.append("|------|-------|------|---------|-------|----------|-------------|")
    for k in keys[:12]:
        eo = evid[k]; ok, why = sufficient(eo)
        L.append(f"| {k[0]}×{k[1]}×{k[2]} | {eo['value']:+.2f} | {eo['confidence']:.2f} | {eo['support']:,} | "
                 f"{eo['freshness']} | {eo['conflict']:.2f} | {'✅' if ok else '— ('+why+')'} |")

    # VERDICT
    L.append("\n## VERDICT — D0 Evidence Theory\n")
    L.append(f"→ ✅ **Evidence Object imefafanuliwa kama first-class object** yenye fields 8, lifecycle "
             f"(fresh/stale/expired), aggregation (inverse-variance, closed), conflict policy "
             f"(→abstain), na sufficiency gate. Imeonyeshwa kwa data halisi: {len(keys)} cells, "
             f"{n_suff} decision-ready, {expired} expired. Hii ndiyo **contract/API** (P63) — Decision "
             "Engine itajengwa JUU ya object hii baada ya Chief kuidhinisha spec. **Hakuna Decision "
             "Engine bado** (maagizo ya Chief). NO ML.")
    L.append("\n**Bado Decision Science D0 — hakuna decision-action wala alpha.** Hii ni Evidence "
             "Engineering: kufafanua contract kabla ya kujenga consumer. **Tahadhari:** value zote za "
             "events ni hasi → 'decision-ready' inaunga mkono **abstention**, sio selection; na confidence=1.00 "
             "ni saturation ya n kubwa, sio edge (Principle 58).")

    # HONEST CAVEATS
    L.append("\n## Honest Caveats\n")
    L.append("1. **Confidence = Φ(EV/SE) ni reliability ya in-sample effect, SIO OOS edge** (Phase 14/26 "
             "lesson). Decision-grade hapa = 'evidence ina ubora', SIO 'kuna alpha'.")
    L.append("2. **Sufficiency thresholds (support/confidence/conflict/TTL) ni human choices** — sehemu ya "
             "spec ya kujadiliwa, sio kanuni za asili; zinapaswa ku-calibrate-iwa OOS baadaye.")
    L.append("3. **Conflict = split-half sign disagreement ni proxy rahisi** — haijumuishi cross-pair/"
             "cross-regime conflict wala FDR; ni contract-level placeholder.")
    L.append("4. **Cell evidence inashiriki features na multiple-comparisons hatari** — Evidence Object "
             "haifuti haja ya OOS confirmation; inaipanga tu kwa muundo unaoauditika (P66).")
    L.append("5. **Aggregation inadhani independence** (inverse-variance) — cells za event moja "
             "zinaweza kuwa correlated; combined uncertainty ni optimistic. Itahitaji correlation-aware "
             "aggregation D-baadaye.")

    L.append("\n*Evidence Object: value/confidence/uncertainty/support/coverage/freshness/conflict/source; "
             "lifecycle fresh→stale→expired; inverse-variance aggregation; abstain-on-conflict; sufficiency "
             "gate. Principle 63–66. NO Decision Engine. NO ML. Profitable ≠ Tradable Edge.*")

    out = REPO_ROOT / c["paths"]["reports"] / "evidence_theory_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)} (cells {len(keys)}, decision-ready {n_suff}, expired {expired})")
    return 0


def self_test():
    # (1) confidence monotonic in value/uncertainty
    a = make_evidence(2.0, 1.0, 500, 0.1, 10, "t")
    b = make_evidence(0.2, 1.0, 500, 0.1, 10, "t")
    ok_conf = a["confidence"] > b["confidence"] and 0 <= a["confidence"] <= 1
    print(f"confidence monotonic: strong={a['confidence']:.2f} weak={b['confidence']:.2f} -> {'OK' if ok_conf else 'FAIL'}")

    # (2) lifecycle
    fresh = make_evidence(1.0, 0.3, 200, 0.1, 100, "t")
    stale = make_evidence(1.0, 0.3, 200, 0.1, STALE_BARS + 10, "t")
    exp = make_evidence(1.0, 0.3, 200, 0.1, TTL_BARS + 10, "t")
    ok_life = fresh["freshness"] == "fresh" and stale["freshness"] == "stale" and is_expired(exp)
    print(f"lifecycle: {fresh['freshness']}/{stale['freshness']}/{exp['freshness']} -> {'OK' if ok_life else 'FAIL'}")

    # (3) aggregation reduces uncertainty kwa agreeing evidence
    e1 = make_evidence(1.0, 0.5, 300, 0.1, 10, "a")
    e2 = make_evidence(1.2, 0.5, 300, 0.1, 10, "b")
    agg = aggregate([e1, e2])
    ok_agg = agg["uncertainty"] < e1["uncertainty"] and agg["conflict"] == 0.0
    print(f"aggregation: agg_unc={agg['uncertainty']:.3f} < {e1['uncertainty']:.3f}, conflict={agg['conflict']:.2f} -> {'OK' if ok_agg else 'FAIL'}")

    # (4) conflict detected + policy abstains
    c1 = make_evidence(1.0, 0.3, 300, 0.1, 10, "a")
    c2 = make_evidence(-1.0, 0.3, 300, 0.1, 10, "b")
    aggc = aggregate([c1, c2])
    ok_conf2 = aggc["conflict"] >= CONFLICT_CEIL and "ABSTAIN" in conflict_policy(aggc)
    print(f"conflict policy: conflict={aggc['conflict']:.2f} policy='{conflict_policy(aggc)}' -> {'OK' if ok_conf2 else 'FAIL'}")

    # (5) sufficiency gating
    good = make_evidence(2.0, 0.3, 500, 0.1, 10, "t")     # high conf, high support, fresh
    weak = make_evidence(0.05, 1.0, 30, 0.1, 10, "t")     # low conf, low support
    ok_suff = sufficient(good)[0] and not sufficient(weak)[0] and not sufficient(exp)[0]
    print(f"sufficiency: good={sufficient(good)[0]} weak={sufficient(weak)[0]} expired={sufficient(exp)[0]} -> {'OK' if ok_suff else 'FAIL'}")

    ok = ok_conf and ok_life and ok_agg and ok_conf2 and ok_suff
    print(f"\nSELF-TEST: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    c = cfg()
    return run(c["pairs"], np.random.default_rng(0))


if __name__ == "__main__":
    raise SystemExit(main())
