"""
failure_autopsy.py — AUTOPSY ya candidates walioshindwa S2 (directive ya PD 2026-07-09).

LENGO: "tuna-detect ilipokwama kila moja, tuna-report kizuizi, tunaangalia logic ya kizuizi
kwa mapana" — maarifa ya kushindwa ndiyo malighafi ya mzunguko ujao wa factory.

DATA: TRAIN jsonl (commit ccfbb24) + VALIDATION jsonl yenye p-values (commit e1a0d27) —
zote tayari zimo git history; HOLDOUT HAITUMIKI (SEALED — cells zake hazifunguliwi kamwe).

TAXONOMY YA VIZUIZI (kila cell isiyo-survivor inapata moja):
  B2 MIRAGE        TRAIN EV>0 lakini VALID EV<=0 — "alionekana mzuri in-sample, akafa OOS".
                   Logic: max-order-statistic + non-stationarity (LESSON-001). SIO kwamba
                   soko lilibadilika lazima — mara nyingi hakuwahi kuwa halisi.
  B3a FDR-TAX      VALID EV>0 NA p<0.05 (nominal PASS!) lakini BH-FDR ilimkata — kodi ya
                   multiplicity: alijaribiwa pamoja na 1,938 wenzake. Logic: power inapotea
                   kwa wingi wa hypotheses; remedy = pre-registration ya wachache (LESSON L-c).
  B3b UNDERPOWERED VALID EV>0 lakini p>=0.05 — mwelekeo ulishikilia, sampuli/variance
                   haikutosha kuthibitisha. Remedy: window ndefu, pooling ya familia,
                   variance reduction — SIO kutupwa.
  B4 DEAD          EV<=0 TRAIN NA VALID — mechanism haifanyi kazi kwenye context hiyo.
                   Inazikwa (au inasomwa kwa INVERSION study kama ni hasi kwa nguvu).
  B5 STARVED       Haikufika N>=30 kwenye VALID (filters kali mno kwa miaka 2) — hatuwezi
                   hata kumhukumu. Remedy: filters pana au window ndefu.
  COST-KILLED (tag ya ziada juu ya B2/B4): gross EV (kabla ya costs, approx = net + spread
                   ya pair + slippage) ilikuwa >0 pande zote mbili lakini net <=0 — soko
                   lilimpa kitu, gharama zikamla. Remedy: TF ya juu, entries za limit,
                   sessions za spread nyembamba.

Output: reports/failure_autopsy_report.md
Self-test (bila data): python failure_autopsy.py --self-test
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# median spread za H1 kwa pair (pips) — kutoka reports/market_state_report.md (data halisi)
SPREAD = {"EURUSD": 0.30, "USDJPY": 0.40, "EURJPY": 0.70, "GBPUSD": 0.90, "EURGBP": 0.90,
          "AUDUSD": 1.00, "USDCHF": 1.00, "NZDUSD": 1.10, "USDCAD": 1.20}
SLIP = {"market": 0.1, "stop": 0.3}
STOP_EVENTS = {"jump_off", "breakout_stop", "session_orb", "inside_break", "nr7_break"}
P_NOMINAL = 0.05


def key(r):
    return (r["event"], r["pair"], r["sl_atr"], r["tp_atr"],
            str(r["session_filter"]), str(r["vol_filter"]))


def cost_of(r):
    ent = "stop" if r["event"] in STOP_EVENTS else "market"
    return SPREAD.get(r["pair"], 0.9) + SLIP[ent]


def classify(train, valid):
    """Ainisha kila cell. Rudisha dict key -> dict(blocker, cost_killed, tr, va)."""
    out = {}
    for k, tr in train.items():
        va = valid.get(k)
        if va is not None and va.get("fdr_survivor"):
            out[k] = dict(blocker="SURVIVOR", cost_killed=False, tr=tr, va=va)
            continue
        if va is None:
            out[k] = dict(blocker="B5_STARVED", cost_killed=False, tr=tr, va=None)
            continue
        ev_t, ev_v, p = tr["ev"], va["ev"], va.get("p", 1.0)
        if ev_v > 0 and p < P_NOMINAL:
            b = "B3a_FDR_TAX"
        elif ev_v > 0:
            b = "B3b_UNDERPOWERED"
        elif ev_t > 0:
            b = "B2_MIRAGE"
        else:
            b = "B4_DEAD"
        c = cost_of(tr)
        cost_killed = b in ("B2_MIRAGE", "B4_DEAD") and (ev_t + c > 0) and (ev_v + c > 0)
        out[k] = dict(blocker=b, cost_killed=cost_killed, tr=tr, va=va)
    return out


def load_jsonl(path):
    rows = [json.loads(l) for l in open(path, encoding="utf-8")]
    return {key(r): r for r in rows}


ORDER = ["B3a_FDR_TAX", "B3b_UNDERPOWERED", "B2_MIRAGE", "B4_DEAD", "B5_STARVED"]
MAANA = {
    "B3a_FDR_TAX": "nominal PASS (EV>0, p<0.05) — aliuawa na kodi ya multiplicity, SIO na soko",
    "B3b_UNDERPOWERED": "mwelekeo ulishikilia OOS (EV>0) — power/sampuli haikutosha",
    "B2_MIRAGE": "TRAIN chanya, VALID hasi — in-sample illusion (LESSON-001)",
    "B4_DEAD": "hasi pande zote — mechanism haifanyi kazi kwenye context hiyo",
    "B5_STARVED": "hakufika N=30 kwenye VALID — filters kali mno kwa miaka 2",
}


def run(train_path, valid_path, out_path=None):
    train = load_jsonl(train_path); valid = load_jsonl(valid_path)
    cls = classify(train, valid)
    n_all = len(cls)
    counts = Counter(v["blocker"] for v in cls.values())
    cost_k = sum(1 for v in cls.values() if v["cost_killed"])

    by_event = defaultdict(Counter)
    for v in cls.values():
        by_event[v["tr"]["event"]][v["blocker"]] += 1
        if v["cost_killed"]:
            by_event[v["tr"]["event"]]["COST"] += 1

    L = ["# Failure Autopsy — walioshindwa S2 walikwama WAPI? (directive ya PD)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | cells {n_all} (TRAIN ccfbb24 + VALID e1a0d27) | "
         f"HOLDOUT: SEALED, haitumiki | p-nominal={P_NOMINAL} | costs approx = net + spread(pair) + slip*\n",
         "> **NIDHAMU:** diagnosis hii inatumia TRAIN+VALIDATION tu. Hypothesis yoyote mpya "
         "itakayozaliwa hapa inahitaji OOS MPYA (data ya 2026-05+ / forward) — 2023-24 "
         "imeshatumika kwa selection, HAIWEZI kuthibitisha watoto wake (LESSON-002).\n"]

    L.append("\n## 1) Vizuizi — hesabu kuu\n")
    L.append("| Kizuizi | Cells | % | Maana |")
    L.append("|---------|-------|---|-------|")
    for b in ["SURVIVOR"] + ORDER:
        n = counts.get(b, 0)
        L.append(f"| {b} | {n} | {n/n_all*100:.1f}% | {MAANA.get(b, 'PASS — STRAT-001')} |")
    L.append(f"| *(tag)* COST-KILLED | {cost_k} | {cost_k/n_all*100:.1f}% | gross>0 pande zote, "
             "costs ziliua net — soko lilitoa, gharama zikala |")

    L.append("\n## 2) Kizuizi kwa event (cells)\n")
    evs = sorted(by_event, key=lambda e: -sum(by_event[e][b] for b in ORDER))
    L.append("| event | " + " | ".join(b.split('_')[0] for b in ORDER) + " | COST |")
    L.append("|-------|" + "|".join(["----"] * (len(ORDER) + 1)) + "|")
    for e in evs:
        c = by_event[e]
        L.append(f"| {e} | " + " | ".join(str(c.get(b, 0)) for b in ORDER) + f" | {c.get('COST', 0)} |")

    # 3) top wounded (B3a + B3b) — wagombea wa mzunguko ujao
    L.append("\n## 3) 'Waliojeruhiwa' bora (B3a/B3b — mwelekeo ulishikilia OOS; wagombea wa re-test kwa OOS MPYA)\n")
    wounded = [(k, v) for k, v in cls.items() if v["blocker"] in ("B3a_FDR_TAX", "B3b_UNDERPOWERED")]
    wounded.sort(key=lambda kv: (kv[1]["va"]["p"], -kv[1]["va"]["ev"]))
    L.append("| kizuizi | event | pair | SL | TP | session | vol | VALID EV | p | N(V) | TRAIN EV |")
    L.append("|---------|-------|------|----|----|---------|-----|----------|---|------|----------|")
    for k, v in wounded[:20]:
        tr, va = v["tr"], v["va"]
        L.append(f"| {v['blocker'].split('_')[0]} | {tr['event']} | {tr['pair']} | {tr['sl_atr']} | "
                 f"{tr['tp_atr']} | {tr['session_filter']} | {tr['vol_filter']} | {va['ev']:+.2f} | "
                 f"{va['p']:.4f} | {va['n']} | {tr['ev']:+.2f} |")

    # 4) familia-level pooling view (B3 logic: power) — je familia nzima ina mwelekeo?
    L.append("\n## 4) Familia-pooled view (logic ya B3: power inapotea kwa kugawanya) — "
             "wastani wa VALID EV (cell-level) kwa event\n")
    L.append("| event | cells VALID EV>0 | jumla | wastani VALID EV |")
    L.append("|-------|------------------|-------|------------------|")
    for e in evs:
        vals = [v["va"]["ev"] for v in cls.values() if v["tr"]["event"] == e and v["va"]]
        if not vals:
            continue
        pos = sum(1 for x in vals if x > 0)
        L.append(f"| {e} | {pos} | {len(vals)} | {sum(vals)/len(vals):+.3f} |")

    L.append("\n## 5) Chief analysis (logic ya kila kizuizi kwa mapana) — angalia sehemu ya "
             "CHIEF ANALYSIS iliyoongezwa chini na Chief baada ya kusoma namba.\n")
    L.append("*Autopsy: TRAIN+VALID tu; holdout SEALED. Hypotheses mpya = OOS mpya. "
             "Profitable != Tradable Edge.*")

    out = Path(out_path) if out_path else REPO_ROOT / "reports" / "failure_autopsy_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"Ripoti: {out}")
    print("counts:", dict(counts), "| cost_killed:", cost_k)
    return 0


def self_test():
    """Fixtures ndogo: kila class inapatikana sahihi."""
    def cell(event, pair, ev, p=None, surv=False, n=100):
        r = dict(event=event, pair=pair, sl_atr=1.5, tp_atr=1.5, session_filter=None,
                 vol_filter=None, ev=ev, n=n, win=0.5, pf=1.0, maxdd=1.0, trades_per_day=0.1)
        if p is not None:
            r["p"] = p; r["fdr_survivor"] = surv
        return r

    train = {}; valid = {}
    fx = [  # (jina, train_ev, valid_row|None, expected)
        ("surv", 0.5, cell("nr7_break", "USDCHF", 2.0, p=1e-5, surv=True), "SURVIVOR"),
        ("fdrtax", 0.5, cell("nr7_break", "GBPUSD", 1.0, p=0.01), "B3a_FDR_TAX"),
        ("under", 0.5, cell("nr7_break", "AUDUSD", 0.5, p=0.30), "B3b_UNDERPOWERED"),
        ("mirage", 2.0, cell("bb_fade", "EURUSD", -1.0, p=0.90), "B2_MIRAGE"),
        ("dead", -2.0, cell("jump_off", "USDCAD", -3.0, p=0.99), "B4_DEAD"),
        ("starved", 0.3, None, "B5_STARVED"),
    ]
    pairs_used = ["USDCHF", "GBPUSD", "AUDUSD", "EURUSD", "USDCAD", "NZDUSD"]
    exp = {}
    for (nm, ev_t, va, want), pr in zip(fx, pairs_used):
        evn = va["event"] if va else "second_chance"
        tr = cell(evn, va["pair"] if va else pr, ev_t)
        train[key(tr)] = tr
        if va is not None:
            valid[key(va)] = va
        exp[key(tr)] = want

    cls = classify(train, valid)
    ok = True
    for k, want in exp.items():
        got = cls[k]["blocker"]
        print(f"  {want:18s} -> {got:18s} {'OK' if got == want else 'FAIL'}")
        ok = ok and got == want

    # COST-KILLED tag: DEAD yenye gross>0 pande zote (net -0.5, cost 1.3 kwa USDCAD market)
    tr = cell("mr_zscore", "USDCAD", -0.5)
    va = cell("mr_zscore", "USDCAD", -0.3, p=0.8)
    cls2 = classify({key(tr): tr}, {key(va): va})
    ck = list(cls2.values())[0]
    ck_ok = ck["blocker"] == "B4_DEAD" and ck["cost_killed"] is True
    print(f"  COST-KILLED tag    -> {ck['cost_killed']} (blocker={ck['blocker']}) {'OK' if ck_ok else 'FAIL'}")
    ok = ok and ck_ok

    # run() end-to-end kwenye temp files
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        tp = Path(tmp) / "t.jsonl"; vp = Path(tmp) / "v.jsonl"; op = Path(tmp) / "rep.md"
        tp.write_text("\n".join(json.dumps(r) for r in train.values()), encoding="utf-8")
        vp.write_text("\n".join(json.dumps(r) for r in valid.values()), encoding="utf-8")
        run(tp, vp, out_path=op)
        txt = op.read_text(encoding="utf-8")
        rep_ok = "B3a_FDR_TAX" in txt and "SURVIVOR" in txt and "Familia-pooled" in txt
        print(f"  report end-to-end  -> {rep_ok}")
        ok = ok and rep_ok

    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", default=str(REPO_ROOT / "data/strategies/candidates_train.jsonl"))
    ap.add_argument("--valid", default=str(REPO_ROOT / "data/strategies/candidates_validation.jsonl"))
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    return run(a.train, a.valid)


if __name__ == "__main__":
    raise SystemExit(main())
