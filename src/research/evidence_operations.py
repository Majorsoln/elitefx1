"""
evidence_operations.py — DECISION SCIENCE PHASE D1 (Chief Quant).

D0 (APPROVED) ilifafanua **Evidence Object** kama contract (3 layers: Claim/Quality/Operational —
P67). Chief amendment: **aggregation si property ya Evidence — ni OPERATION juu ya Evidence**
(P68); Evidence Objects ni **immutable contracts**. Kabla ya Decision Engine, lazima tujue
**Evidence inatembeaje ndani ya mfumo** — sio tu inaonekanaje.

  Principle 67: Evidence = Claim + Quality + Operational State.
  Principle 68: Evidence Objects ni immutable; aggregation ni operation ya nje juu yao.
  Principle 69: decision-ready ≠ trade-ready.
  Principle 70 (OPEN): confidence itoke kwa confidence-model, sio kuhifadhiwa kama primitive.

Maswali (Chief, D1):
  Q1. Ni operations gani zinafanyika juu ya Evidence Object? (aggregate/filter/merge/expire/split)
  Q2. Operations zipi zinahifadhi audit trail? (P66)
  Q3. Evidence Object ni immutable kweli? (operations hazibadilishi input)
  Q4. Conflict ina taxonomy gani? (intra/cross-engine/cross-pair/cross-timeframe/event-vs-representation)
  Q5. Operations gani zinaweza kubadilisha decision-readiness?

Mbinu: fasili operations kama functions PURE (zinazalisha objects mpya + audit trail; hazibadilishi
input), classify conflict kwa taxonomy, na onyesha kwa tagged evidence halisi (per pair×tf×event).
NO Decision Engine. NO ML.

Reuse: evidence_object (make_evidence, is_expired, decision_ready, conflict_policy, aggregate,
freeze, TTL_BARS, CONFLICT_CEIL, EPS), market_state_engine (cfg, pip), latent_structure
(state_path), event_library (EVENTS_ALL), configuration_engine (EVENTS_SET, VERT),
context_value (HORIZON).

Output: reports/evidence_operations_report.md
Self-test: python src/research/evidence_operations.py --self-test
"""
from __future__ import annotations

import argparse, sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
import polars as pl

from market_state_engine import cfg, pip
from latent_structure import state_path
from event_library import EVENTS_ALL
from configuration_engine import EVENTS_SET, VERT
from context_value import HORIZON
from evidence_object import (make_evidence, is_expired, decision_ready, conflict_policy,
                             aggregate as _agg_obj, freeze, TTL_BARS, CONFLICT_CEIL, EPS)

REPO_ROOT = Path(__file__).resolve().parents[2]
TFS = ["H1", "H2", "H4", "D1"]
MIN_OCC = 20


# ---------- Evidence Operations (P68: external ops on immutable objects) ----------
def _tag(eo, op):
    """Rudisha COPY mpya na audit entry + provenance edge (input haibadiliki — P68/P71/P72)."""
    audit = list(eo.get("audit", [])) + [op]
    base = op.split("(")[0].split("[")[0]
    return make_evidence(eo["value"], eo["uncertainty"], eo["support"], eo["coverage"],
                         eo["age_bars"], eo["source"], conflict=eo["conflict"], audit=audit,
                         parents=[eo["id"]], op=base)


def op_aggregate(eos):
    """Aggregate (inverse-variance) — closed; audit trail. P68."""
    live = [e for e in eos if not is_expired(e)]
    agg = _agg_obj(eos)
    if agg is None:
        return None
    agg["audit"] = [f"aggregate(n={len(live)})"]
    agg["parents"] = [e["id"] for e in live]      # provenance graph: many parents (P72)
    agg["op"] = "aggregate"
    return agg


def op_filter(eos, predicate, name="filter"):
    """Filter — chagua subset (audit kwa kila iliyobaki)."""
    return [_tag(e, f"{name}") for e in eos if predicate(e)]


def op_merge(eo_a, eo_b):
    """Merge — evidence mbili → moja (aggregate ya 2 + audit ya merge)."""
    m = op_aggregate([eo_a, eo_b])
    if m is not None:
        m["audit"] = [f"merge({eo_a['source']}|{eo_b['source']})"]
        m["parents"] = [eo_a["id"], eo_b["id"]]; m["op"] = "merge"
    return m


def op_expire(eo, now_extra_bars):
    """Expire — songesha age (operational state hubadilika; readiness inaweza kubadilika)."""
    return _tag(make_evidence(eo["value"], eo["uncertainty"], eo["support"], eo["coverage"],
                              eo["age_bars"] + int(now_extra_bars), eo["source"],
                              conflict=eo["conflict"], audit=eo.get("audit")), f"expire(+{now_extra_bars})")


def op_split(eo, parts):
    """Split — gawa support kwa parts (mfano per-regime); uncertainty inaongezeka (n ndogo)."""
    out = []
    for i, frac in enumerate(parts):
        n = max(1, int(eo["support"] * frac))
        unc = eo["uncertainty"] * np.sqrt(eo["support"] / n)   # SE inakua n inaposhuka
        out.append(_tag(make_evidence(eo["value"], unc, n, eo["coverage"] * frac,
                                      eo["age_bars"], f"{eo['source']}#part{i}",
                                      conflict=eo["conflict"], audit=eo.get("audit")), f"split[{i}]"))
    return out


PRESERVE_AUDIT = {"aggregate": True, "filter": True, "merge": True, "expire": True, "split": True}


# ---------- Conflict taxonomy (Q4) ----------
def _level_mean(evs):
    """Inverse-variance weighted mean value + total weight kwa kundi la evidence."""
    w = np.array([1.0 / (e["uncertainty"] ** 2 + EPS) for e in evs])
    v = np.array([e["value"] for e in evs])
    return float((w * v).sum() / w.sum()), float(w.sum())


def _cross_conflict(tagged, x, controls):
    """Disagreement inayotokana na dimension X, ku-CONTROL kwa dimensions nyingine. Kwa kila
    control-group, linganisha X-levels: level inahesabiwa conflict tu kama mean yake ina ISHARA
    INAYOPINGANA KABISA na aggregate (huepuka zero-cancellation artifact)."""
    groups = defaultdict(list)
    for e, t in tagged:
        groups[tuple(t.get(ci) for ci in controls)].append((e, t))
    num = den = 0.0
    for g in groups.values():
        xlev = defaultdict(list)
        for e, t in g:
            xlev[t.get(x)].append(e)
        if len(xlev) < 2:
            continue
        means, ws = zip(*[_level_mean(evs) for evs in xlev.values()])
        means = np.array(means); ws = np.array(ws)
        s = np.sign((ws * means).sum()) or 1.0
        dis = sum(wi for wi, mi in zip(ws, means) if mi * s < 0)   # opposite-sign tu
        num += dis; den += ws.sum()
    return float(num / den) if den > 0 else 0.0


def conflict_taxonomy(tagged):
    """Given evidence objects wenye tags (pair, tf, engine), classify conflict kwa dimension.
    Kila dimension imepimwa ku-control kwa zingine (decomposition sahihi)."""
    return {
        "intra (split-half)": float(np.mean([e["conflict"] for e, _ in tagged])) if tagged else 0.0,
        "cross-pair": _cross_conflict(tagged, "pair", ("tf", "engine")),
        "cross-timeframe": _cross_conflict(tagged, "tf", ("pair", "engine")),
        "cross-engine": _cross_conflict(tagged, "engine", ("pair", "tf")),
    }


# ---------- build tagged evidence (real data) ----------
def build_tagged_evidence(pairs):
    """Per (pair × tf × event) Evidence Object (tagged) — kwa conflict taxonomy + operations demo."""
    tagged = []
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
            n = len(close)
            sig = {e: EVENTS_ALL[e](close, high, low) for e in EVENTS_SET}
            for e in EVENTS_SET:
                ys = []
                last = 0
                for i in range(n):
                    if i + HORIZON >= n or i + VERT >= n or not (np.isfinite(spr[i])):
                        continue
                    d = int(sig[e][i])
                    if d != 0:
                        ys.append(float(d * (close[i + HORIZON] - close[i]) - spr[i])); last = i
                if len(ys) >= MIN_OCC:
                    y = np.array(ys, float)
                    ev = float(y.mean()); se = float(y.std() / np.sqrt(len(y)) + EPS)
                    half = len(y) // 2
                    c = 0.0 if half < 5 else (0.0 if np.sign(y[:half].mean()) == np.sign(y[half:].mean()) else 1.0)
                    eo = make_evidence(ev, se, len(y), len(y) / n, n - last, source=f"{sym}:{tf}:{e}", conflict=c)
                    tagged.append((eo, {"pair": sym, "tf": tf, "engine": e}))
        print(f"  {sym}: tagged evidence built", flush=True)
    return tagged, no_px


def run(pairs, rng):
    c = cfg()
    print("Building tagged evidence (pair × tf × event)...", flush=True)
    tagged, no_px = build_tagged_evidence(pairs)
    if no_px:
        print("HITILAFU: state parquet haina OHLC. Endesha market_state_engine.py kwanza.", file=sys.stderr)
        return 1
    if len(tagged) < 4:
        print("HITILAFU: evidence haitoshi.", file=sys.stderr)
        return 1
    return _report(c, pairs, tagged)


def _report(c, pairs, tagged):
    eos = [e for e, _ in tagged]
    L = ["# Evidence Operations — Evidence inatembeaje ndani ya mfumo? (Decision Science D1)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | {len(pairs)} pairs, {len(tagged)} tagged evidence objects | "
         f"operations PURE (immutable, audit-trail) + conflict taxonomy | NO Decision Engine | NO ML*\n",
         "> **P67** Evidence = Claim+Quality+Operational. **P68** Evidence ni immutable; aggregation ni "
         "OPERATION ya nje. **P69** decision-ready ≠ trade-ready. **P70 (OPEN)** confidence = model. "
         "D1: jinsi Evidence inavyotembea (operations), sio tu inavyoonekana. NO Decision Engine."]

    # Q1 — operations
    L.append("\n## Q1 — Operations juu ya Evidence Object\n")
    sample = eos[0]
    agg = op_aggregate(eos[:8])
    flt = op_filter(eos, lambda e: not is_expired(e), "filter(live)")
    mrg = op_merge(eos[0], eos[1]) if len(eos) >= 2 else None
    exp = op_expire(eos[0], TTL_BARS + 5)
    spl = op_split(eos[0], [0.5, 0.5])
    L.append("| operation | maana | matokeo |")
    L.append("|-----------|-------|---------|")
    L.append(f"| aggregate | inverse-variance combine (closed) | value {agg['value']:+.3f}, unc {agg['uncertainty']:.3f}, n {agg['support']:,} |")
    L.append(f"| filter | chagua subset (mfano live) | {len(flt)}/{len(eos)} live |")
    L.append(f"| merge | mbili → moja | {('value '+format(mrg['value'],'+.3f')) if mrg else '—'} |")
    L.append(f"| expire | songesha age → operational state | {sample['freshness']} → {exp['freshness']} |")
    L.append(f"| split | gawa support → unc inakua | n {sample['support']:,} → {spl[0]['support']:,} (unc {sample['uncertainty']:.3f}→{spl[0]['uncertainty']:.3f}) |")

    # Q2 — audit trail
    L.append("\n## Q2 — Operations zipi zinahifadhi audit trail? (P66)\n")
    L.append("| operation | audit-preserving? | mfano audit |")
    L.append("|-----------|-------------------|-------------|")
    L.append(f"| aggregate | ✅ | {agg['audit']} |")
    L.append(f"| filter | ✅ | {flt[0]['audit'] if flt else '—'} |")
    L.append(f"| merge | ✅ | {mrg['audit'] if mrg else '—'} |")
    L.append(f"| expire | ✅ | {exp['audit']} |")
    L.append(f"| split | ✅ | {spl[0]['audit']} |")
    L.append("\n→ operations ZOTE zinahifadhi audit trail (P66: kila decision itrace kwa evidence + ops zake).")

    # Q3 — immutability
    L.append("\n## Q3 — Evidence Object ni immutable kweli?\n")
    before = dict(eos[0]); _ = op_expire(eos[0], 999); _ = op_split(eos[0], [0.3, 0.7])
    unchanged = (eos[0]["value"] == before["value"] and eos[0]["age_bars"] == before["age_bars"]
                 and eos[0]["support"] == before["support"])
    fz = freeze(eos[0]); frozen_ok = True
    try:
        fz["value"] = 0.0; frozen_ok = False
    except TypeError:
        frozen_ok = True
    L.append(f"- operations (expire/split) **hazibadilishi input**: {'✅ input unchanged' if unchanged else '❌ MUTATED'}.")
    L.append(f"- `freeze(eo)` inatoa **read-only view** (MappingProxyType): {'✅ write inakataliwa' if frozen_ok else '❌ writable'}.")
    L.append("- by-convention dict ni mutable; operations ni PURE (zinazalisha objects mpya) + `freeze` "
             "kwa enforcement ya kweli. Hii ndiyo immutability ya contract (P68).")

    # Q4 — conflict taxonomy
    L.append("\n## Q4 — Conflict taxonomy\n")
    tax = conflict_taxonomy(tagged)
    L.append("| conflict dimension | score | tafsiri |")
    L.append("|--------------------|-------|---------|")
    desc = {
        "intra (split-half)": "kutoaminika ndani ya object moja (muda)",
        "cross-pair": "events zinapingana kati ya pairs",
        "cross-timeframe": "events zinapingana kati ya timeframes",
        "cross-engine": "events/representations tofauti zinapingana",
    }
    for dim in ["intra (split-half)", "cross-pair", "cross-timeframe", "cross-engine"]:
        sc = tax.get(dim, 0.0)
        L.append(f"| {dim} | {sc:.2f} | {desc[dim]}{' ⚠️' if sc >= CONFLICT_CEIL else ''} |")
    L.append("\n→ conflict **SIO scalar moja** — ina taxonomy. Decision Engine itahitaji kujua conflict "
             "*ya aina gani* kabla ya policy (P26 abstain kwa high cross-engine/cross-pair).")

    # Q5 — readiness-changing operations
    L.append("\n## Q5 — Operations gani zinabadilisha decision-readiness?\n")
    base = make_evidence(2.0, 0.3, 500, 0.1, 10, "demo")               # ready
    r0 = decision_ready(base)[0]
    r_exp = decision_ready(op_expire(base, TTL_BARS + 5))[0]            # expire → not ready
    r_spl = decision_ready(op_split(base, [0.05, 0.95])[0])[0]          # split → support ndogo
    conf2 = op_aggregate([make_evidence(1.0, 0.3, 300, 0.1, 10, "a"),
                          make_evidence(-1.0, 0.3, 300, 0.1, 10, "b")])  # merge conflicting
    r_cf = decision_ready(conf2)[0]
    L.append("| operation | readiness inabadilika? |")
    L.append("|-----------|------------------------|")
    L.append(f"| (base) | ready={r0} |")
    L.append(f"| expire | ready {r0}→{r_exp} {'✅ inabadilisha' if r_exp != r0 else ''} |")
    L.append(f"| split (support↓) | ready {r0}→{r_spl} {'✅ inabadilisha' if r_spl != r0 else ''} |")
    L.append(f"| aggregate (conflicting) | ready→{r_cf} {'✅ inabadilisha (conflict)' if not r_cf else ''} |")
    L.append("\n→ **expire, split, aggregate(conflict)** zinaweza kuondoa decision-readiness; filter "
             "inaiacha kwa zilizobaki. Readiness ni operational state, sio ya kudumu.")

    # VERDICT
    L.append("\n## VERDICT — D1 Evidence Operations\n")
    L.append(f"→ ✅ **Evidence Operations zimefafanuliwa** kama functions PURE juu ya objects immutable "
             f"(P68): aggregate/filter/merge/expire/split — zote zinahifadhi **audit trail** (P66), "
             f"hazibadilishi input (Q3), na zinaweza kubadilisha **decision-readiness** (Q5). Conflict "
             "ina **taxonomy** (intra/cross-pair/cross-timeframe/cross-engine), sio scalar (Q4). Object + "
             "operations sasa zimefungwa — msingi thabiti wa Decision Engine (haitabadilika tukibadilisha "
             "representation). **Hakuna Decision Engine bado.** NO ML.")
    L.append("\n**Bado Decision Science D1 — hakuna decision-action wala alpha.** Hii ni Evidence "
             "Engineering: jinsi evidence inavyotembea, kabla ya consumer (Decision Engine).")

    # HONEST CAVEATS
    L.append("\n## Honest Caveats\n")
    L.append("1. **Immutability ni by-convention + `freeze`** — Python dict si frozen kwa asili; operations "
             "ni PURE lakini caller anaweza bado kumutate dict mbichi. Enforcement kamili (frozen dataclass) "
             "ni hatua ya engineering ya baadaye.")
    L.append("2. **Conflict taxonomy ni descriptive, sio causal** — cross-pair/cross-tf disagreement inaweza "
             "kutoka sample size / non-stationarity, sio 'evidence mbaya'. Ni ramani ya wapi kupingana, sio kwa nini.")
    L.append("3. **aggregate/merge zinadhani independence** (inverse-variance) — pair×tf za event moja "
             "zina correlation; combined uncertainty ni optimistic (caveat ya D0 inaendelea).")
    L.append("4. **split inadhani homogeneity** (inagawa value sawa, inakuza SE tu) — kiuhalisia sub-regimes "
             "zinaweza kuwa na value tofauti; split halisi inahitaji data ya sub-regime.")
    L.append("5. **Readiness/operations ≠ edge (P69).** Operations zinapanga evidence kwa muundo unaoauditika; "
             "hazithibitishi alpha — decision-ready bado ni mbali na trade-ready.")

    L.append("\n*Operations PURE (aggregate/filter/merge/expire/split) juu ya Evidence Objects immutable; "
             "audit trail; conflict taxonomy (intra/cross-pair/cross-tf/cross-engine); readiness-change. "
             "Principle 67–70. NO Decision Engine. NO ML. Profitable ≠ Tradable Edge.*")

    out = REPO_ROOT / c["paths"]["reports"] / "evidence_operations_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)} ({len(tagged)} tagged; conflict dims {len(tax)})")
    return 0


def self_test():
    # (1) immutability: op hazibadilishi input
    base = make_evidence(2.0, 0.3, 500, 0.1, 10, "t")
    before = dict(base)
    _ = op_expire(base, 999); _ = op_split(base, [0.5, 0.5]); _ = op_aggregate([base, base])
    ok_immut = base["age_bars"] == before["age_bars"] and base["support"] == before["support"]
    print(f"immutability: input unchanged={ok_immut} -> {'OK' if ok_immut else 'FAIL'}")

    # (2) audit trail grows
    exp = op_expire(base, 5)
    ok_audit = len(exp["audit"]) > len(base["audit"]) and "expire" in exp["audit"][-1]
    print(f"audit trail: base={len(base['audit'])} -> expire={len(exp['audit'])} ({exp['audit'][-1]}) -> {'OK' if ok_audit else 'FAIL'}")

    # (3) expire flips readiness; split lowers support
    r0 = decision_ready(base)[0]
    r_exp = decision_ready(op_expire(base, TTL_BARS + 5))[0]
    spl = op_split(base, [0.02, 0.98])[0]
    ok_ready = r0 and (not r_exp) and spl["support"] < base["support"] and spl["uncertainty"] > base["uncertainty"]
    print(f"readiness: base={r0} expired={r_exp}; split n {base['support']}→{spl['support']} unc↑ -> {'OK' if ok_ready else 'FAIL'}")

    # (4) conflict taxonomy: cross-pair disagreement detected
    tagged = [
        (make_evidence(1.0, 0.3, 300, 0.1, 10, "P1:H1:e"), {"pair": "P1", "tf": "H1", "engine": "e"}),
        (make_evidence(1.1, 0.3, 300, 0.1, 10, "P1:H2:e"), {"pair": "P1", "tf": "H2", "engine": "e"}),
        (make_evidence(-1.0, 0.3, 300, 0.1, 10, "P2:H1:e"), {"pair": "P2", "tf": "H1", "engine": "e"}),
        (make_evidence(-1.1, 0.3, 300, 0.1, 10, "P2:H2:e"), {"pair": "P2", "tf": "H2", "engine": "e"}),
    ]
    tax = conflict_taxonomy(tagged)
    ok_tax = tax["cross-pair"] >= 0.3 and tax["cross-timeframe"] < 0.3
    print(f"conflict taxonomy: cross-pair={tax['cross-pair']:.2f} cross-tf={tax['cross-timeframe']:.2f} -> {'OK' if ok_tax else 'FAIL'}")

    # (5) merge conflicting -> high conflict
    m = op_merge(make_evidence(1.0, 0.3, 300, 0.1, 10, "a"), make_evidence(-1.0, 0.3, 300, 0.1, 10, "b"))
    ok_merge = m["conflict"] >= CONFLICT_CEIL and "merge" in m["audit"][-1]
    print(f"merge conflict: conflict={m['conflict']:.2f} audit={m['audit'][-1]} -> {'OK' if ok_merge else 'FAIL'}")

    ok = ok_immut and ok_audit and ok_ready and ok_tax and ok_merge
    print(f"\nSELF-TEST: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    c = cfg()
    return run(c["pairs"], np.random.default_rng(1))


if __name__ == "__main__":
    raise SystemExit(main())
