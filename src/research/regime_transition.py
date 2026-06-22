"""
regime_transition.py — PHASE 1 (Chief Priority 1). Transition Dynamics = INTENTION.

Market State report ilijibu "LOCATION" (soko liko wapi). Hii inajibu "INTENTION"
(soko linaENDA wapi): transition matrix P(state_t -> state_{t+1}) kwa kila
dimension, pair, na TF.

  P(stay) (diagonal)  = persistence (state ina memory)
  P(escalate)         = LOW->HIGH-er (vol/activity inapanda)
  P(revert)           = HIGH->LOW-er

Inasoma state series ya market_state_engine:
  data/processed/state/symbol=<P>/tf=<TF>.parquet
(Endesha market_state_engine.py KWANZA.)

Output: reports/regime_transition_report.md
Endesha: python src/research/regime_transition.py
         python src/research/regime_transition.py --symbol EURGBP
Self-test: python src/research/regime_transition.py --self-test
"""
from __future__ import annotations

import argparse, sys
from datetime import datetime
from pathlib import Path

import numpy as np
import polars as pl
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config" / "data_config.yaml"
TFS = ["H1", "H2", "H4", "D1"]
DIMS = [("volatility", ["LOW","NORMAL","HIGH"], "volatility_state"),
        ("activity",   ["LOW","NORMAL","HIGH"], "activity_state"),
        ("spread",     ["NORMAL","WIDE"],       "spread_state")]


def cfg():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)

def state_path(sym, tf):
    return REPO_ROOT / cfg()["paths"]["processed"] / "state" / f"symbol={sym}" / f"tf={tf}.parquet"


def transition(states, levels):
    """Rudisha (P, n). P[i][j] = P(next=j | cur=i). Bar-to-bar, bila UNKNOWN."""
    idx = {lv: i for i, lv in enumerate(levels)}
    M = np.zeros((len(levels), len(levels)))
    for a, b in zip(states[:-1], states[1:]):
        if a in idx and b in idx:
            M[idx[a], idx[b]] += 1
    rs = M.sum(1, keepdims=True)
    P = np.divide(M, rs, out=np.zeros_like(M), where=rs > 0)
    return P, int(M.sum())


def _esc_rev(P, levels):
    """escalation = P(kwenda state ya juu zaidi) wastani; revert = kushuka."""
    n = len(levels); esc = rev = stay = 0.0; cnt = 0
    for i in range(n):
        if P[i].sum() == 0:
            continue
        stay += P[i, i]
        esc += P[i, i+1:].sum()
        rev += P[i, :i].sum()
        cnt += 1
    if cnt == 0:
        return 0, 0, 0
    return stay/cnt, esc/cnt, rev/cnt


def joint_seq(df):
    """Joint state code kwa kila bar: vol+act+spr (herufi ya kwanza). None kama UNKNOWN."""
    out = []
    for v, a, s in zip(df["volatility_state"].to_list(),
                       df["activity_state"].to_list(),
                       df["spread_state"].to_list()):
        out.append(None if "UNKNOWN" in (v, a, s) else f"{v[0]}{a[0]}{s[0]}")
    return out


def joint_stats(seq):
    """Rudisha (freq Counter, next Counter-per-state, joint_P_stay, n_trans)."""
    from collections import Counter, defaultdict
    freq = Counter(x for x in seq if x)
    nxt = defaultdict(Counter); stay = 0; tot = 0
    for a, b in zip(seq[:-1], seq[1:]):
        if a and b:
            tot += 1
            if a == b:
                stay += 1
            nxt[a][b] += 1
    return freq, nxt, (stay/tot if tot else 0.0), tot


def run(pairs, tfs):
    miss = []
    rows = {d[0]: [] for d in DIMS}
    joint = []
    for sym in pairs:
        for tf in tfs:
            p = state_path(sym, tf)
            if not p.exists():
                miss.append(f"{sym}/{tf}"); continue
            df = pl.read_parquet(p)
            for dim, levels, col in DIMS:
                P, n = transition(df[col].to_list(), levels)
                rows[dim].append((sym, tf, P, n, levels))
            jf, jn, jstay, jtot = joint_stats(joint_seq(df))
            joint.append((sym, tf, jf, jn, jstay, jtot))
    if all(len(v) == 0 for v in rows.values()):
        print("HITILAFU: hakuna state parquet. Endesha market_state_engine.py kwanza.\n"
              f"  Zilizokosekana: {', '.join(miss[:8])}{'...' if len(miss)>8 else ''}", file=sys.stderr)
        return 1

    L = ["# Regime Transition Report — INTENTION (Phase 1.5, CQ-011)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | P(state_t -> state_t+1) bar-to-bar | chanzo: "
         "market_state_engine state series | no UNKNOWN*\n",
         "> Market State = LOCATION (soko liko wapi). Transition = INTENTION (linaenda wapi). "
         "P(stay) = memory; P(escalate) = kupanda; P(revert) = kushuka. Joint = vol+act+spr pamoja.\n"]
    for dim, levels, _ in DIMS:
        L.append(f"\n## {dim.upper()} — P(from → to) %\n")
        hdr = "| Pair | TF | n | " + " | ".join(f"{a[:1]}→{b[:1]}" for a in levels for b in levels) + \
              " | stay | esc | rev |"
        L.append(hdr)
        L.append("|------|----|---|" + "----|" * (len(levels)**2) + "----|----|----|")
        for sym, tf, P, n, lv in rows[dim]:
            cells = " | ".join(f"{P[i,j]*100:.0f}" for i in range(len(lv)) for j in range(len(lv)))
            stay, esc, rev = _esc_rev(P, lv)
            L.append(f"| {sym} | {tf} | {n:,} | {cells} | {stay*100:.0f} | {esc*100:.0f} | {rev*100:.0f} |")

    # ── JOINT STATE TRANSITION (CQ-011) ──
    L.append("\n## JOINT STATE — vol+act+spr (code: V A S, h.m. LLN = LOW vol, LOW act, NORMAL spr)\n")
    L.append("*Joint P(stay) = soko linabaki kwenye joint state ileile bar inayofuata. n_states = "
             "joint states tofauti zilizoonekana.*\n")
    L.append("| Pair | TF | n_states | joint P(stay) | modal state (freq%) |")
    L.append("|------|----|----------|---------------|---------------------|")
    for sym, tf, jf, jn, jstay, jtot in joint:
        tot = sum(jf.values()) or 1
        modal, mc = jf.most_common(1)[0] if jf else ("—", 0)
        L.append(f"| {sym} | {tf} | {len(jf)} | {jstay*100:.0f}% | {modal} ({mc/tot*100:.0f}%) |")

    # deep-dive: pair ya kipaumbele (EURGBP) — joint states za juu + zinakoenda
    deep = "EURGBP" if any(s == "EURGBP" for s, *_ in joint) else (joint[0][0] if joint else None)
    if deep:
        L.append(f"\n## JOINT deep-dive — {deep} (top joint states + zinakoenda)\n")
        L.append("| TF | joint | freq% | P(stay) | →top (≠self) | →top% |")
        L.append("|----|-------|-------|---------|--------------|-------|")
        for sym, tf, jf, jn, jstay, jtot in joint:
            if sym != deep:
                continue
            tot = sum(jf.values()) or 1
            for st, cnt in jf.most_common(6):
                nx = jn.get(st)
                stay_p = (nx.get(st, 0)/sum(nx.values())) if nx and sum(nx.values()) else 0
                dests = [(b, c) for b, c in nx.most_common() if b != st] if nx else []
                top, tp = (dests[0][0], dests[0][1]/sum(nx.values())) if dests else ("—", 0)
                L.append(f"| {tf} | {st} | {cnt/tot*100:.0f}% | {stay_p*100:.0f}% | {top} | {tp*100:.0f}% |")

    if miss:
        L.append(f"\n*Hazikupatikana (endesha state engine): {len(miss)} pair×TF.*")
    L.append("\n---\n*Per-dim P(stay) = MEMORY; esc/rev = mwelekeo. JOINT inajibu 'state kamili "
             "(vol+act+spr) inaenda wapi' — ndio swali la Chief (HIGH inaweza kuwa LOW→HIGH expansion, "
             "HIGH→HIGH mature, au HIGH→LOW exhaustion). Hii = INTENTION layer. Phase 2: Adaptive "
             "Volume Bars (imejengwa, inasubiri). Metric = EV (CQ-008).*")
    out = REPO_ROOT / cfg()["paths"]["reports"] / "regime_transition_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"Ripoti: {out.relative_to(REPO_ROOT)} | dims={len(DIMS)} joint pairs×TF={len(joint)}")
    return 0


def self_test():
    """Sequence yenye persistence + escalation inayojulikana."""
    levels = ["LOW","NORMAL","HIGH"]
    # LOW inakaa sana, ikibadilika huenda NORMAL; HIGH inarevert NORMAL
    seq = (["LOW"]*10 + ["NORMAL"]*3 + ["HIGH"]*5 + ["NORMAL"]*2) * 50
    P, n = transition(seq, levels)
    stay, esc, rev = _esc_rev(P, levels)
    # LOW->LOW kubwa; HIGH->NORMAL (revert) kubwa
    iL, iN, iH = 0, 1, 2
    print(f"P(LOW->LOW)={P[iL,iL]:.2f} P(LOW->NORMAL)={P[iL,iN]:.2f} P(LOW->HIGH)={P[iL,iH]:.2f}")
    print(f"P(HIGH->HIGH)={P[iH,iH]:.2f} P(HIGH->NORMAL)={P[iH,iN]:.2f} P(HIGH->LOW)={P[iH,iL]:.2f} "
          f"| stay={stay:.2f} esc={esc:.2f} rev={rev:.2f}")
    # INTENTION: persistence kubwa; hakuna jumps LOW<->HIGH moja kwa moja; HIGH inarevert via NORMAL
    ok = (P[iL,iL] > 0.8 and P[iL,iH] == 0 and P[iH,iL] == 0 and P[iH,iN] > 0.1 and stay > 0.5)
    # JOINT: thibitisha joint_seq + joint_stats (df ndogo ya bandia)
    import polars as _pl
    jdf = _pl.DataFrame(dict(
        volatility_state=["LOW","LOW","HIGH","HIGH","UNKNOWN"],
        activity_state=["LOW","LOW","HIGH","NORMAL","LOW"],
        spread_state=["NORMAL","NORMAL","WIDE","WIDE","NORMAL"]))
    js = joint_seq(jdf)
    jf, jn, jstay, jtot = joint_stats(js)
    joint_ok = (js[0] == "LLN" and js[-1] is None and jf["LLN"] == 2
                and abs(jstay - 1/3) < 1e-9)   # transitions: LLN->LLN, LLN->HHW, HHW->HNW
    print(f"joint: seq[0]={js[0]} freq(LLN)={jf['LLN']} P(stay)={jstay:.2f} (tarajio 0.33)")
    ok = ok and joint_ok
    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default=None); ap.add_argument("--tf", default=None, choices=TFS)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    c = cfg()
    pairs = [a.symbol] if a.symbol else c["pairs"]
    tfs = [a.tf] if a.tf else TFS
    return run(pairs, tfs)


if __name__ == "__main__":
    raise SystemExit(main())
