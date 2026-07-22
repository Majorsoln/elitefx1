"""
model_steward.py — MODEL STEWARD ("mwalimu wa models"; Doctrine V2 §8.2; docs/MODEL_STEWARD_CHARTER.md).

META-MODEL READ-ONLY: inasoma `data/paper/paper_log.jsonl` (matokeo halisi + learned_ev tag) na
kupima KILA model (STRAT-001/002) PRACTICAL (halisi) vs LEARNED (ahadi ya backtest):
  - practical = realized distribution (pips, sawa na unit ya learned_ev) + bootstrap CI (REUSE
    family_pooled._boot_ci — HAKUNA statistic mpya). verdict HOLDS/SHRINKS/LIFTS/INSUFFICIENT.
  - WEAKNESS MAP: vunja kwa session / vol-bucket (atr_rel proxy) / streak-state / cost-drag; kila
    cell {N, mean, CI, divergence, verdict}; N<min_n -> INSUFFICIENT (anti-noise).
  - AGENDA ranked (athari × uhakika): weakness + hypothesis (lugha ya trade) + proposed experiment
    (registration ya kawaida — SI auto-apply) + expected lift/risk.

NIDHAMU (charter): READ-ONLY KWELI — inaandika reports/model_steward.{md,json} PEKEE (HAIGUSI log/
registry/configs). ZERO golden/statistic fns kuguswa (import tu). HAKUNA "best cell = strategy mpya"
(L-041 — ni diagnostics, si discovery). SAMPLE-HONESTY: practical = replay/validation, SI forward.

Endesha:  python model_steward.py [--log <path>] [--min-n 30]
Self-test: python model_steward.py --self-test
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from family_pooled import _boot_ci                       # bootstrap CI ya mean (REUSE — golden)
from event_quality_report import _sess                   # session kutoka hour (REUSE)

REPO_ROOT = Path(__file__).resolve().parents[2]
LOG_F = REPO_ROOT / "data" / "paper" / "paper_log.jsonl"
OUT_MD = REPO_ROOT / "reports" / "model_steward.md"
OUT_JSON = REPO_ROOT / "reports" / "model_steward.json"
SL_ATR = {"STRAT-001": 2.0, "STRAT-002": 1.0}            # kwa vol-proxy (atr = sl_pips / sl_atr)
MIN_N = 30
CI_LEVEL, BOOT_B, SEED = 0.90, 2000, 20260722
SAMPLE_NOTE = ("SAMPLE: replay/validation, si forward halisi bado — power inakua na forward data. "
               "HAKUNA dai la 'model imethibitika forward' bila forward.")


def _hour(as_of):
    try:
        return datetime.fromtimestamp(float(as_of), tz=timezone.utc).hour
    except (TypeError, ValueError, OverflowError, OSError):
        return None


def load_trades(log_path):
    """Read-only: soma paper_log, link execution+settlement kwa order_id -> trades zilizofungwa.
    Rudisha (trades, meta). Kila trade: strategy/pair/learned_ev/pnl_r/pnl_pips/sl_pips/spread/
    slippage/as_of/session. pnl_pips = pnl_r*sl_pips (sl_pips=|entry-sl|, pip-space kama log)."""
    log_path = Path(log_path)
    if not log_path.exists():
        return [], {"error": f"no data: {log_path}"}
    execs, setts, n_lines = {}, {}, 0
    for ln in log_path.read_text(encoding="utf-8").splitlines():
        if not ln.strip():
            continue
        n_lines += 1
        try:
            rec = json.loads(ln)
        except json.JSONDecodeError:
            continue
        o = rec.get("obj", rec); kind = rec.get("kind")
        if kind == "execution" and o.get("status") == "FILLED":
            execs[o.get("order_id")] = o
        elif kind == "settlement":
            setts[o.get("id", o.get("exec_id"))] = o
    trades = []
    for oid, e in execs.items():
        s = setts.get(oid)
        if s is None or s.get("pnl_r") is None:
            continue
        entry, sl = e.get("entry"), e.get("sl")
        if entry is None or sl is None:
            continue
        sl_pips = abs(float(entry) - float(sl))
        pnl_r = float(s["pnl_r"])
        h = _hour(e.get("as_of"))
        trades.append(dict(
            strategy=e.get("strategy", "UNKNOWN"), pair=e.get("pair", "?"),
            learned_ev=e.get("learned_ev"), pnl_r=pnl_r, sl_pips=sl_pips,
            pnl_pips=pnl_r * sl_pips, spread=float(e.get("spread", 0.0)),
            slippage=float(e.get("slippage", 0.0)), as_of=e.get("as_of"),
            session=(_sess(h) if h is not None else "?")))
    meta = dict(n_lines=n_lines, n_exec_filled=len(execs), n_closed=len(trades),
                sha256=hashlib.sha256(log_path.read_bytes()).hexdigest()[:16])
    return trades, meta


# ---------- practical vs learned (REUSE _boot_ci — hakuna statistic mpya) ----------

def cell_verdict(pnl_pips, learned, min_n=MIN_N, seed=SEED):
    """{N, mean, ci, divergence, verdict}. verdict: INSUFFICIENT (N<min_n); HOLDS (CI inagusa learned);
    SHRINKS (CI chini ya learned); LIFTS (CI juu ya learned)."""
    vals = [float(x) for x in pnl_pips]
    n = len(vals)
    if n < min_n:
        mean = round(float(np.mean(vals)), 3) if n else None
        return dict(n=n, mean=mean, ci_lo=None, ci_hi=None,
                    divergence=(round(mean - learned, 3) if (mean is not None and learned is not None) else None),
                    verdict="INSUFFICIENT")
    mean = float(np.mean(vals))
    lo, hi = _boot_ci(vals, level=CI_LEVEL, B=BOOT_B, seed=seed)
    if learned is None:
        verdict = "UNKNOWN-LEARNED"
    elif lo <= learned <= hi:
        verdict = "HOLDS"
    elif hi < learned:
        verdict = "SHRINKS"
    else:
        verdict = "LIFTS"
    return dict(n=n, mean=round(mean, 3), ci_lo=round(lo, 3), ci_hi=round(hi, 3),
                divergence=(round(mean - learned, 3) if learned is not None else None),
                verdict=verdict)


# ---------- weakness map dimensions (derivable kutoka log — no fabrication) ----------

def _vol_bucket(trades):
    """atr_rel proxy = sl_pips / sl_atr(strategy); terciles NDANI ya model -> LOW/MID/HIGH."""
    atr = np.array([t["sl_pips"] / SL_ATR.get(t["strategy"], 1.0) for t in trades])
    if len(atr) < 3:
        return {id(t): "MID" for t in trades}
    q1, q2 = np.quantile(atr, [1 / 3, 2 / 3])
    out = {}
    for t, a in zip(trades, atr):
        out[id(t)] = "LOW" if a <= q1 else ("HIGH" if a > q2 else "MID")
    return out


def _streak_state(trades):
    """State ya kabla-ya-trade (baada ya W/L mfululizo) — sorted kwa as_of per model."""
    ordered = sorted(trades, key=lambda t: (t["as_of"] if t["as_of"] is not None else 0))
    out = {}; run = 0; last = None
    for t in ordered:
        if last is None:
            out[id(t)] = "FRESH"
        elif run >= 2 and last == "L":
            out[id(t)] = "AFTER_2L+"
        elif last == "L":
            out[id(t)] = "AFTER_LOSS"
        else:
            out[id(t)] = "AFTER_WIN"
        res = "W" if t["pnl_r"] > 0 else "L"
        run = run + 1 if res == last else 1
        last = res
    return out


def _cost_bucket(trades):
    """cost drag = (spread+slippage) / |gross_pips|; median-split -> LOW-DRAG/HIGH-DRAG."""
    drag = {}
    for t in trades:
        cost = t["spread"] + t["slippage"]
        gross = abs(t["pnl_pips"]) + cost
        drag[id(t)] = (cost / gross) if gross > 0 else 0.0
    if len(drag) < 2:
        return {k: "LOW-DRAG" for k in drag}, {}
    med = float(np.median(list(drag.values())))
    return {k: ("HIGH-DRAG" if v > med else "LOW-DRAG") for k, v in drag.items()}, \
           {k: round(v, 4) for k, v in drag.items()}


def weakness_map(trades, learned, min_n=MIN_N):
    """Cells kwa dimension: session / vol / streak / cost. Kila cell = cell_verdict."""
    vol = _vol_bucket(trades); streak = _streak_state(trades); cost, _ = _cost_bucket(trades)
    dims = {"session": lambda t: t["session"], "vol": lambda t: vol[id(t)],
            "streak": lambda t: streak[id(t)], "cost": lambda t: cost[id(t)]}
    out = {}
    for dim, keyfn in dims.items():
        buckets = defaultdict(list)
        for t in trades:
            buckets[keyfn(t)].append(t["pnl_pips"])
        out[dim] = {k: cell_verdict(v, learned, min_n) for k, v in sorted(buckets.items())}
    return out


# ---------- improvement agenda (ranked; NI PENDEKEZO — Steward haitekelezi) ----------

_HYP = {
    "cost": ("cost (spread+slippage) inakula edge zaidi kwenye cell hii",
             "cost-aware entry filter au session avoidance (registration ya kawaida)",
             "punguza cost-drag; risk: N inashuka (chagua-kidogo)"),
    "vol": ("edge inashuka kwenye vol bucket hii (atr_rel) — SL/TP geometry haiendani na vol",
            "vol-conditional sizing/exit (S2 pooled multi-pair, L-041 breadth)",
            "match exit na vol; risk: overfit ya bucket moja"),
    "session": ("edge dhaifu kwenye session hii (liquidity/spread ya session)",
                "session filter (kama no-LATE) — pre-registered",
                "kata session dhaifu; risk: trades/mwaka zinapungua"),
    "streak": ("path-dependence: model inashuka baada ya streak (FTMO daily-loss risk, K4 §5)",
               "streak-aware risk throttle (Tabaka-4 sizing, deterministic — SI model change)",
               "linda daily-loss; risk: hakuna EV lift, ni risk-shaping tu"),
}


def build_agenda(models, min_n=MIN_N):
    """Ranked kwa athari(|divergence|×N) × uhakika(N). SHRINKS/dhaifu ndio kipaumbele. + data-gap item."""
    items = []
    for name, m in models.items():
        for dim, cells in m["weakness_map"].items():
            for cell, cv in cells.items():
                if cv["verdict"] in ("SHRINKS",) and cv["divergence"] is not None:
                    impact = abs(cv["divergence"]) * cv["n"]
                    h, exp, risk = _HYP.get(dim, ("udhaifu wa jumla", "registration ya kawaida", "—"))
                    items.append(dict(
                        rank_score=round(impact, 1), model=name, weakness=f"{dim}={cell}",
                        verdict=cv["verdict"], n=cv["n"], divergence=cv["divergence"],
                        hypothesis=h, proposed_experiment=exp, expected_lift="—", risk=risk))
    items.sort(key=lambda x: x["rank_score"], reverse=True)
    # data-gap agenda item (honest): regime dimension inahitaji state tag kwenye engine log
    items.append(dict(rank_score=0.0, model="ALL", weakness="regime dimension haipo kwenye log",
                      verdict="DATA-GAP", n=0, divergence=None,
                      hypothesis="regime (trend/range/compression) haijalog na live_engine bado",
                      proposed_experiment="ongeza HTF regime tag kwenye execution record ya engine "
                      "(additive) ili weakness-map ya regime iwezekane",
                      expected_lift="uwezo mpya wa diagnostics", risk="hakuna (log field additive)"))
    return items


# ---------- run + outputs ----------

def _commit():
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True,
                           text=True, timeout=5)
        return r.stdout.strip() or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def run(log_path=LOG_F, min_n=MIN_N, out_md=OUT_MD, out_json=OUT_JSON, write=True, seed=SEED):
    """Endesha steward (READ-ONLY). Rudisha summary dict. write=False -> hakuna faili (self-test)."""
    trades, meta = load_trades(log_path)
    provenance = dict(commit=_commit(), log=str(Path(log_path)), log_lines=meta.get("n_lines"),
                      log_sha256=meta.get("sha256"), n_closed=meta.get("n_closed"),
                      generated_at=datetime.now(timezone.utc).isoformat(), sample_note=SAMPLE_NOTE)
    models = {}
    by_model = defaultdict(list)
    for t in trades:
        by_model[t["strategy"]].append(t)
    for name, ts in sorted(by_model.items()):
        learned = next((t["learned_ev"] for t in ts if t["learned_ev"] is not None), None)
        overall = cell_verdict([t["pnl_pips"] for t in ts], learned, min_n, seed)
        models[name] = dict(learned_ev=learned, n=len(ts), overall=overall,
                            mean_R=round(float(np.mean([t["pnl_r"] for t in ts])), 4) if ts else None,
                            weakness_map=weakness_map(ts, learned, min_n))
    agenda = build_agenda(models, min_n)
    summary = dict(provenance=provenance, min_n=min_n, models=models, agenda=agenda)
    if write:
        _write_json(summary, out_json)
        _write_md(summary, out_md)
    return summary


def _write_json(summary, out_json):
    Path(out_json).parent.mkdir(parents=True, exist_ok=True)
    Path(out_json).write_text(json.dumps(summary, indent=2, sort_keys=True, default=str), encoding="utf-8")


def _vtag(v):
    return {"HOLDS": "✓ HOLDS", "SHRINKS": "▼ SHRINKS", "LIFTS": "▲ LIFTS",
            "INSUFFICIENT": "· INSUFFICIENT", "UNKNOWN-LEARNED": "? no-learned"}.get(v, v)


def _write_md(summary, out_md):
    p = summary["provenance"]
    L = ["# MODEL STEWARD — practical vs learned + weakness map + agenda\n",
         f"*{p['generated_at'][:19]} UTC · READ-ONLY meta-model (Doctrine V2 §8.2) · min_n={summary['min_n']}*\n",
         f"> **{p['sample_note']}**\n"]
    if not summary["models"]:
        L.append("\n_no data: paper_log haina trades zilizofungwa (endesha live_engine --run kwanza)._")

    L.append("\n## (A) PRACTICAL vs LEARNED (per model)\n")
    L.append("| model | N | learned EV (pips) | practical mean (pips) | 90% CI | divergence | verdict | mean R |")
    L.append("|-------|---|-------------------|-----------------------|--------|------------|---------|--------|")
    for name, m in summary["models"].items():
        o = m["overall"]; ci = (f"[{o['ci_lo']}, {o['ci_hi']}]" if o["ci_lo"] is not None else "—")
        L.append(f"| {name} | {m['n']} | {m['learned_ev']} | {o['mean']} | {ci} | "
                 f"{o['divergence']} | {_vtag(o['verdict'])} | {m['mean_R']} |")

    L.append("\n## (B) WEAKNESS MAP (per model × dimension; kila cell N + CI + verdict)\n")
    for name, m in summary["models"].items():
        L.append(f"\n### {name}\n")
        L.append("| dimension | cell | N | mean (pips) | 90% CI | divergence | verdict |")
        L.append("|-----------|------|---|-------------|--------|------------|---------|")
        for dim, cells in m["weakness_map"].items():
            for cell, cv in cells.items():
                ci = (f"[{cv['ci_lo']}, {cv['ci_hi']}]" if cv["ci_lo"] is not None else "—")
                L.append(f"| {dim} | {cell} | {cv['n']} | {cv['mean']} | {ci} | "
                         f"{cv['divergence']} | {_vtag(cv['verdict'])} |")

    L.append("\n## (C) IMPROVEMENT AGENDA (ranked athari × uhakika — PENDEKEZO, si auto-apply)\n")
    L.append("> Steward HAITEKELEZI. Kila kipengele = hypothesis kwa Chief/PD kupitia registration ya "
             "kawaida (kama SCIENTIST-D). L-041: diagnostics, SI 'best cell = strategy mpya'.\n")
    L.append("| # | model | weakness | N | divergence | hypothesis (trade language) | proposed experiment | risk |")
    L.append("|---|-------|----------|---|------------|-----------------------------|---------------------|------|")
    for i, a in enumerate(summary["agenda"], 1):
        L.append(f"| {i} | {a['model']} | {a['weakness']} ({_vtag(a['verdict'])}) | {a['n']} | "
                 f"{a['divergence']} | {a['hypothesis']} | {a['proposed_experiment']} | {a['risk']} |")

    L.append("\n## (D) SAMPLE-HONESTY + PROVENANCE\n")
    L.append(f"- **{p['sample_note']}**")
    L.append(f"- data: `{p['log']}` · lines={p['log_lines']} · closed-trades={p['n_closed']} · "
             f"sha256={p['log_sha256']}")
    L.append(f"- commit: `{p['commit']}` · generated_at: {p['generated_at']}")
    L.append("- verdict key: HOLDS (CI inagusa learned) · SHRINKS (CI chini ya learned — shrinkage) · "
             "LIFTS (CI juu) · INSUFFICIENT (N<min_n, anti-noise).")
    L.append("\n*Zoezi endelevu: kila data mpya (paper/forward) -> Steward inasasisha ramani + ajenda. "
             "reports/model_steward.json = malighafi ya panel MODEL HEALTH (Dashboard-V2, §8.2).*")
    Path(out_md).parent.mkdir(parents=True, exist_ok=True)
    Path(out_md).write_text("\n".join(L), encoding="utf-8")


# ---------- self-test (synthetic log — bila data ya nje) ----------

def _synth_log(tmp, n_per=40, seed=0):
    """Tengeneza paper_log synthetic kupitia live_engine (format halisi) -> faili la temp."""
    import live_engine as le
    fxs = {"USDCHF": le._fixture(1, n=1500), "USDJPY": le._fixture(2, n=1500)}
    # config yenye headroom kubwa ili trades nyingi zi-fill (weakness map iwe na N)
    cfg = dict(le._ftmo_config(), max_total_dd=1e9, max_daily_loss=1e9, daily_budget_start=1e6,
               max_per_trade=1e5, max_slots=99, max_correlated_slots=99)
    s = []
    le.run(cfg=cfg, sink=s, _loader=le._mk_loader(fxs))
    p = Path(tmp) / "paper_log.jsonl"
    with open(p, "w", encoding="utf-8") as f:
        for rec in s:
            f.write(json.dumps(rec, sort_keys=True, default=str) + "\n")
    return p


def self_test():
    ok = True
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        log = _synth_log(tmp)
        h_before = hashlib.sha256(log.read_bytes()).hexdigest()

        # (a) READ-ONLY: run mbili -> log HAIBADILIKI (hash sawa)
        r1 = run(log_path=log, out_md=Path(tmp) / "s.md", out_json=Path(tmp) / "s.json")
        r2 = run(log_path=log, out_md=Path(tmp) / "s2.md", out_json=Path(tmp) / "s2.json")
        h_after = hashlib.sha256(log.read_bytes()).hexdigest()
        read_only = h_before == h_after
        print(f"  [a] read-only: log hash HAIBADILIKI (2 runs) -> {read_only}")
        ok = ok and read_only

        # (e) DETERMINISM: input ile ile -> summary ile ile (bootstrap seeded)
        det = (json.dumps(r1["models"], sort_keys=True, default=str)
               == json.dumps(r2["models"], sort_keys=True, default=str))
        print(f"  [e] determinism: models bit-identical (bootstrap seeded) -> {det}")
        ok = ok and det

        # (b) ANTI-NOISE: cell yenye N<min_n -> INSUFFICIENT
        cv_small = cell_verdict([0.5] * 10, learned=1.0, min_n=30)
        cv_big = cell_verdict(list(np.random.default_rng(1).normal(0.5, 1, 60)), learned=1.0, min_n=30)
        anti = cv_small["verdict"] == "INSUFFICIENT" and cv_big["verdict"] in ("HOLDS", "SHRINKS", "LIFTS")
        print(f"  [b] anti-noise: N=10->{cv_small['verdict']} N=60->{cv_big['verdict']} -> {anti}")
        ok = ok and anti

        # verdict-logic sanity: learned juu ya CI -> SHRINKS; ndani -> HOLDS; chini -> LIFTS
        base = list(np.random.default_rng(2).normal(0.0, 0.5, 80))
        v_shrink = cell_verdict(base, learned=5.0, min_n=30)["verdict"]      # learned >> practical
        v_hold = cell_verdict(base, learned=0.0, min_n=30)["verdict"]        # learned ndani ya CI
        v_lift = cell_verdict(base, learned=-5.0, min_n=30)["verdict"]       # learned << practical
        vlogic = v_shrink == "SHRINKS" and v_hold == "HOLDS" and v_lift == "LIFTS"
        print(f"  [b2] verdict-logic: learned-high->{v_shrink} learned-mid->{v_hold} learned-low->{v_lift} -> {vlogic}")
        ok = ok and vlogic

        # (c) PROVENANCE: report ina commit + line-count; ikikosekana -> fail
        md = (Path(tmp) / "s.md").read_text(encoding="utf-8")
        prov_ok = ("commit:" in md and f"lines={r1['provenance']['log_lines']}" in md
                   and r1["provenance"]["log_lines"] and r1["provenance"]["commit"])
        print(f"  [c] provenance: commit + line-count kwenye report -> {bool(prov_ok)}")
        ok = ok and bool(prov_ok)

        # (d) HONESTY TAG: report ina "SAMPLE: replay/validation"
        honesty = "SAMPLE: replay/validation" in md and "SAMPLE: replay/validation" in json.dumps(r1, default=str)
        print(f"  [d] honesty-tag: 'SAMPLE: replay/validation' kwenye report -> {honesty}")
        ok = ok and honesty

        # weakness map + agenda zipo (structure)
        m0 = next(iter(r1["models"].values()))
        struct = ({"session", "vol", "streak", "cost"} <= set(m0["weakness_map"])
                  and isinstance(r1["agenda"], list) and any(a["weakness"].startswith("regime")
                                                             for a in r1["agenda"]))
        print(f"  [g] structure: weakness dims {sorted(m0['weakness_map'])} + agenda (regime data-gap) -> {struct}")
        ok = ok and struct

    # (c-fail) log haipo -> load_trades error + hakuna models
    r_empty = run(log_path=Path(tmp) / "gone.jsonl", write=False)
    empty_ok = r_empty["models"] == {} and r_empty["provenance"]["log_lines"] in (None, 0)
    print(f"  [c2] no-data: log haipo -> models={{}} (hakuna kubuni) -> {empty_ok}")
    ok = ok and empty_ok

    # (f) NO-GOLDEN-TOUCH: steward HAI-DEFINE episodes/pvalue*/_boot_ci (import tu) — line-start def
    import re as _re
    src = Path(__file__).read_text(encoding="utf-8")
    no_golden = not _re.search(r"^\s*def\s+(episodes|pvalue\w*|_boot_ci)\b", src, _re.M)
    print(f"  [f] no-golden-touch: hakuna def ya episodes/pvalue/_boot_ci (import tu) -> {no_golden}")
    ok = ok and no_golden

    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default=str(LOG_F))
    ap.add_argument("--min-n", type=int, default=MIN_N)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    res = run(log_path=a.log, min_n=a.min_n)
    if not res["models"]:
        print("MODEL STEWARD: no data (paper_log haina trades zilizofungwa). Endesha live_engine --run.")
        return 0
    print("MODEL STEWARD (READ-ONLY meta-model):")
    for name, m in res["models"].items():
        o = m["overall"]
        print(f"  {name}: N={m['n']} practical={o['mean']} vs learned={m['learned_ev']} pips "
              f"-> {o['verdict']} (mean R={m['mean_R']})")
    print(f"  agenda items: {len(res['agenda'])} | {SAMPLE_NOTE}")
    print(f"  -> reports/model_steward.md + .json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
