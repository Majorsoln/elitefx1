"""
live_engine.py — LIVE PAPER ENGINE (docs/LIVE_ENGINE_CHARTER.md; Doctrine V2 §4/§8).

AI MOJA inayoendesha forward (paper): bar-by-bar, per strategy (STRAT-001 USDCHF SL2/TP1 no-LATE H1
+ STRAT-002 USDJPY SL1/TP1 no-LATE H1). Mtiririko (charter §MTIRIRIKO):
  STATE -> nr7_break SIGNAL -> DECISION (decision_engine + policy SELECT/VETO) -> SIZE
  (broker_adapter.DailyRiskBudgetSizer, FTMO config) -> COMPLIANCE (integrity_gate + constraints 5)
  -> EXECUTE (broker_adapter mode=paper) -> LOG (paper_log.jsonl) -> dashboard ingest.

WIRING PEKEE ya modules zilizopo — ZERO golden/statistic/fill fns mpya:
  - Honest fills/costs = `event_quality_report.episodes` (next-bar, tie->SL, spread+slip; BYTE-IDENTICAL).
    Forward loop = replay ya episodes-candidates kwa mpangilio wa ts (episodes yenyewe ni no-look-ahead).
  - no-LATE mask = `strategy_lab._mask_context` (proven). Decision = `decision_engine.decide`,
    compliance = `integrity_gate.gate`, sizing/constraints = `broker_adapter`, log = `decision_repository.append`.
  - LOG schema inalingana HASA na `dashboard/monitor/loaders.py` (decision/execution/settlement records).

NIDHAMU: mode=paper PEKEE (broker_adapter Q1 live=refuse-stub — HAIBADILISHWI). STRAT configs
HAZIBADILIKI. Append-only log. Forward/replay: split='validation' (holdout HAIGUSWI).

Endesha (PC ya data): python live_engine.py --run            (replay validation -> paper_log.jsonl)
Self-test (bila data):  python live_engine.py --self-test
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np

from event_library_v2 import EVENTS_V2
from event_quality_report import episodes, SLIP_STOP
from strategy_lab import _mask_context, load_window
import decision_repository as repo
from decision_engine import decide
from integrity_gate import gate
from broker_adapter import build_constraints, build_context, size
from execution_object import record as record_execution

REPO_ROOT = Path(__file__).resolve().parents[2]
LOG_F = str(REPO_ROOT / "data" / "paper" / "paper_log.jsonl")
VERSIONS = {"schema_version": "live_engine@v1", "doctrine_version": "V2"}
EVENT = "nr7_break"
TF = "H1"
SESSION_FILTER = "no-LATE"

# STRAT configs HASA (docs/STRATEGIES.md) + learned EV (backtest — STEWARD divergence tag, §8.2)
STRATS = {
    "STRAT-001": dict(pair="USDCHF", sl_atr=2.0, tp_atr=1.0, learned_ev=1.92),
    "STRAT-002": dict(pair="USDJPY", sl_atr=1.0, tp_atr=1.0, learned_ev=2.65),
}

# Strategy policy: nr7 signal iliyothibitika = SELECT (K4-filter NO-LIFT -> hakuna veto ya model).
STRAT_POLICY = {"id": "policy:strat-nr7@v1",
                "decide": lambda s: ("SELECT", "nr7_break proven-OOS signal (no K4 filter — L-042)")}


def _pip_value(pair):
    p = pair.upper()
    if p.startswith("XAU"):
        return 1.0
    return 6.7 if p.endswith("JPY") else 10.0


def _ftmo_config():
    """FTMO config (deterministic) = ftmo_config.yaml + max_spread kutoka data_config (charter §FTMO)."""
    import yaml
    cfg = yaml.safe_load(open(REPO_ROOT / "config" / "ftmo_config.yaml", encoding="utf-8"))
    try:
        dc = yaml.safe_load(open(REPO_ROOT / "config" / "data_config.yaml", encoding="utf-8"))
        cfg["max_spread"] = dc.get("max_spread_pips", {})
    except OSError:
        cfg.setdefault("max_spread", {})
    return cfg


def _day(ts_scalar):
    return str(np.datetime64(ts_scalar, "D"))


def _as_of(ts_scalar):
    """datetime64 -> epoch seconds (int) kwa log (dashboard _dt inasoma epoch/ISO)."""
    return int(np.datetime64(ts_scalar, "s").astype("int64"))


def candidates(name, strat, data):
    """Candidate trades za strategy moja (episodes honest — no-look-ahead). Rudisha list ya dict
    zenye entry/exit ts+px, pnl_pips, pnl_r, sl_pips, spread, slip. HAKUNA fill math mpya."""
    o, h, l_, c = data["o"], data["h"], data["l"], data["c"]
    atr, spr, hour, vol, ts = data["atr"], data["spr"], data["hour"], data["vol"], data["ts"]
    spec = EVENTS_V2[EVENT]                                   # nr7_break, entry="stop"
    out = spec["fn"](o, h, l_, c, data.get("tc"), hour)
    out = _mask_context(out, spec["entry"], hour, vol, SESSION_FILTER, None)     # no-LATE (proven)
    trs = episodes(out, spec["entry"], o, h, l_, c, atr, spr, hour, vol,
                   sl_atr=strat["sl_atr"], tp_atr=strat["tp_atr"])
    cands = []
    for (eb, xb, d, pnl, sess, vs) in trs:
        i = eb - 1                                           # signal bar (decidable KABLA ya entry)
        a = atr[i]
        lvl = out["long_level"][i] if d == 1 else out["short_level"][i]
        e = max(lvl, o[eb]) if d == 1 else min(lvl, o[eb])   # entry px = ILE ILE ya episodes (stop)
        cost = float(spr[eb]) + SLIP_STOP
        exit_px = e + d * (pnl + cost)                       # pnl = d*(exit-e)-cost  ->  exit derived
        sl_pips = strat["sl_atr"] * a
        cands.append(dict(
            strategy=name, pair=strat["pair"], dir=int(d), signal_bar=int(i),
            entry_ts=ts[eb], exit_ts=ts[xb], entry_px=round(float(e), 6),
            exit_px=round(float(exit_px), 6),
            sl=round(float(e - d * strat["sl_atr"] * a), 6),
            tp=round(float(e + d * strat["tp_atr"] * a), 6),
            sl_pips=round(float(sl_pips), 4), pnl_pips=round(float(pnl), 4),
            pnl_r=(round(float(pnl / sl_pips), 4) if sl_pips > 0 else None),
            spread=round(float(spr[eb]), 4), slippage=SLIP_STOP, learned_ev=strat["learned_ev"]))
    return cands


def _acct_state():
    return dict(date=None, daily_profit=0.0, daily_loss=0.0, cum_pnl=0.0, peak_pnl=0.0,
                open_slots=0, correlation_exposure={}, spread_by_pair={},
                worst_case=0.0, open_positions=[])


def _acct_view(cfg, st, extra_worst=0.0):
    """context ya integrity_gate (build_context inatarajia keys hizi)."""
    return dict(daily_loss=st["daily_loss"], total_dd=max(0.0, st["peak_pnl"] - st["cum_pnl"]),
                open_slots=st["open_slots"], correlation_exposure=dict(st["correlation_exposure"]),
                spread_by_pair=dict(st["spread_by_pair"]))


def _budget(cfg, st):
    b = (cfg["daily_budget_start"] + cfg["win_factor"] * st["daily_profit"]
         - cfg["loss_factor"] * st["daily_loss"])
    return max(0.0, b)


def _groups_of(pair, groups):
    return [g for g, ps in (groups or {}).items() if pair in ps]


def _settle_due(st, cfg, until_ts, log_path, sink):
    """Funga positions ambazo exit_ts <= until_ts (mpangilio wa ts) — update account + log settlement."""
    st["open_positions"].sort(key=lambda p: p["exit_ts"])
    while st["open_positions"] and st["open_positions"][0]["exit_ts"] <= until_ts:
        p = st["open_positions"].pop(0)
        realized = p["qty"] * p["pnl_pips"] * _pip_value(p["pair"])     # $ (paper)
        st["cum_pnl"] += realized; st["peak_pnl"] = max(st["peak_pnl"], st["cum_pnl"])
        if realized >= 0:
            st["daily_profit"] += realized
        else:
            st["daily_loss"] += -realized
        st["open_slots"] -= 1
        for g in _groups_of(p["pair"], cfg.get("correlation_groups")):
            st["correlation_exposure"][g] = max(0, st["correlation_exposure"].get(g, 0) - 1)
        st["spread_by_pair"].pop(p["pair"], None)
        obj = {"id": p["order_id"], "exec_id": p["order_id"], "parent_execution_id": p["exec_id"],
               "pnl": round(realized, 2),                          # decision_repository REQUIRED (settlement)
               "realized_pnl": round(realized, 2), "pnl_r": p["pnl_r"],   # dashboard loader reads realized_pnl
               "exit_price": p["exit_px"], "as_of": _as_of(p["exit_ts"])}
        _append(log_path, "settlement", obj, sink)


def _append(log_path, kind, obj, sink):
    """repo.append (append-only) au sink ya self-test (list). Rudisha rekodi."""
    if sink is not None:
        rec = {"repo_id": "live_engine", "kind": kind, "versions": VERSIONS, "obj": obj}
        sink.append(rec)
        return rec
    return repo.append(log_path, kind, obj, VERSIONS)


def run(split="validation", log_path=LOG_F, cfg=None, sink=None, pairs=None, policy=STRAT_POLICY,
        _loader=None):
    """Forward paper loop (replay ya split — validation kwa default; HOLDOUT HAIGUSWI). Rudisha summary.
    sink != None -> log kwenye list (self-test), si faili. _loader -> monkeypatch ya load_window."""
    cfg = cfg or _ftmo_config()
    lw = _loader or load_window
    constraints = build_constraints(cfg)
    st = _acct_state()

    # kusanya candidates za strategies zote -> mpangilio wa ENTRY ts (forward)
    cands = []
    strat_items = STRATS.items() if pairs is None else [(n, s) for n, s in STRATS.items() if s["pair"] in pairs]
    for name, strat in strat_items:
        data = lw(strat["pair"], TF, split)
        if data is None or data.get("ts") is None:
            continue
        cands += candidates(name, strat, data)
    cands.sort(key=lambda x: (x["entry_ts"], x["strategy"]))

    n_filled = n_rejected = 0; sig_n = 0
    if sink is None:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
    for cd in cands:
        # 1) funga positions zilizoiva KABLA ya entry hii (accounting sahihi ya slots/daily_loss)
        _settle_due(st, cfg, cd["entry_ts"], log_path, sink)
        # 2) day reset (bajeti/hasara ya siku)
        d = _day(cd["entry_ts"])
        if st["date"] != d:
            st["date"] = d; st["daily_profit"] = 0.0; st["daily_loss"] = 0.0
        sig_n += 1
        ts_epoch = _as_of(cd["entry_ts"])
        # 3) SIGNAL decision (readiness snapshot -> decide)
        snap = {"id": f"signal:{cd['strategy']}:{cd['pair']}:{ts_epoch}:{sig_n}", "as_of": ts_epoch,
                "readiness_state": "READY", "reliability": 1.0, "uncertainty": 0.0,
                "temporal_conflict": 0.0, "structural_conflict": {},
                "aggregate": {"source": cd["strategy"], "support": 1, "learned_ev": cd["learned_ev"]}}
        dsig = decide(snap, policy)
        # aggregate/readiness = signal-stage evidence (dashboard loader: 'aggregate' -> stage 'signal')
        _append(log_path, "decision", {**dict(dsig), "as_of": ts_epoch,
                                       "aggregate": snap["aggregate"], "readiness_state": "READY",
                                       "strategy": cd["strategy"], "pair": cd["pair"]}, sink)
        # 4) SIZE (DailyRiskBudgetSizer — FTMO)
        acct = _acct_view(cfg, st)
        qty = size(cfg, acct, cd["sl_pips"], _pip_value(cd["pair"]), budget_remaining=_budget(cfg, st))
        risk = qty * cd["sl_pips"] * _pip_value(cd["pair"])
        # 5) COMPLIANCE (integrity_gate) — spread ya bar hii ndani ya context
        st["spread_by_pair"][cd["pair"]] = cd["spread"]
        g = gate(dsig, constraints, build_context({**acct, "spread_by_pair": st["spread_by_pair"]},
                                                  cd["pair"], worst_case=risk))
        elig = dict(g["eligibility"])
        elig["passed"] = [ch["constraint_id"] for ch in elig.get("checks", [])
                          if ch["verdict"] == "ELIGIBLE"]
        _append(log_path, "decision", {**{k: v for k, v in dict(g).items() if k != "eligibility"},
                                       "eligibility": elig, "as_of": ts_epoch}, sink)
        order_id = f"paper:{cd['strategy']}:{sig_n}"
        # 6) EXECUTE (paper) au REJECT
        blocked = (g["lifecycle"] != "VALIDATED") or (qty <= 0)
        reason = (",".join(elig["failed"]) if elig.get("failed") else
                  ("budget/slots=0 -> qty=0" if qty <= 0 else ""))
        if blocked:
            n_rejected += 1
            _append(log_path, "execution",
                    {"id": f"exec:{order_id}", "order_id": order_id, "pair": cd["pair"],
                     "side": "BUY" if cd["dir"] == 1 else "SELL", "qty": 0, "entry": None,
                     "sl": cd["sl"], "tp": cd["tp"], "status": "REJECTED", "as_of": ts_epoch,
                     "mode": "paper", "strategy": cd["strategy"], "reject_reason": reason,
                     "spread": cd["spread"], "slippage": cd["slippage"],
                     "learned_ev": cd["learned_ev"]}, sink)
            continue
        # honest execution object (frozen) — REUSE execution_object
        trade = {"pair": cd["pair"], "side": "BUY" if cd["dir"] == 1 else "SELL",
                 "ref_price": cd["entry_px"], "as_of": ts_epoch}
        report = {"status": "FILLED", "intended": {"side": trade["side"], "qty": qty,
                  "ref_price": cd["entry_px"]}, "fills": [{"qty": qty, "price": cd["entry_px"],
                  "ts": ts_epoch}], "reject_reason": None, "as_of": ts_epoch, "report_ref": order_id}
        ex = record_execution(g, report)
        _append(log_path, "execution",
                {"id": f"exec:{order_id}", "order_id": order_id, "parent_decision_id": g["id"],
                 "pair": cd["pair"], "side": trade["side"], "qty": round(qty, 4),
                 "entry": cd["entry_px"], "sl": cd["sl"], "tp": cd["tp"], "status": "FILLED",
                 "as_of": ts_epoch, "mode": "paper", "strategy": cd["strategy"],
                 "spread": cd["spread"], "slippage": cd["slippage"], "learned_ev": cd["learned_ev"],
                 "execution_id": ex["id"]}, sink)
        n_filled += 1
        st["open_slots"] += 1
        for gg in _groups_of(cd["pair"], cfg.get("correlation_groups")):
            st["correlation_exposure"][gg] = st["correlation_exposure"].get(gg, 0) + 1
        st["open_positions"].append(dict(cd, order_id=order_id, exec_id=ex["id"], qty=qty))
    # funga positions zilizobaki
    if cands:
        _settle_due(st, cfg, cands[-1]["exit_ts"] if False else np.datetime64("2999-01-01"),
                    log_path, sink)
    return dict(candidates=len(cands), filled=n_filled, rejected=n_rejected,
                cum_pnl=round(st["cum_pnl"], 2), log=log_path)


# ---------- self-test (synthetic — bila data ya nje) ----------

def _fixture(seed, n=1500, split_start="2023-06-01"):
    """H1 bars synthetic zenye nr7 signals + ts (spacing 1h) ndani ya window ya VALIDATION."""
    from event_library_v2 import _synthetic
    o, h, l_, c, tc, hour = _synthetic(n=n, seed=seed)
    atr = np.maximum(h - l_, 0.1)
    ts = (np.datetime64(split_start) + np.arange(n) * np.timedelta64(1, "h"))
    return dict(o=o, h=h, l=l_, c=c, atr=atr, spr=np.full(n, 1.0), tc=tc,
                hour=(ts.astype("datetime64[h]").astype(int) % 24).astype(int),
                vol=np.array(["NORMAL"] * n), ts=ts, days=n, ctx=None)


def _mk_loader(fxs):
    return lambda sym, tf, split, token=None: fxs.get(sym)


def _index(recs):
    """Panga records kama dashboard loader inavyofanya (link settlement->execution kwa order_id)."""
    trades = {}
    for r in recs:
        o = r["obj"]
        if r["kind"] == "execution":
            trades[o["order_id"]] = dict(o, _closed=False)
    for r in recs:
        o = r["obj"]
        if r["kind"] == "settlement":
            key = o.get("id", o.get("exec_id"))
            if key in trades:
                trades[key].update(pnl=o["realized_pnl"], pnl_r=o.get("pnl_r"),
                                   exit=o.get("exit_price"), _closed=True)
    return trades


def self_test():
    ok = True
    cfg = _ftmo_config()

    # (e) NO-LOOK-AHEAD: nr7_break level kwenye signal bar i haibadiliki na bars > i (truncation-inv)
    fx = _fixture(1)
    spec = EVENTS_V2[EVENT]
    full = spec["fn"](fx["o"], fx["h"], fx["l"], fx["c"], fx["tc"], fx["hour"])
    k = 800
    trunc = spec["fn"](fx["o"][:k], fx["h"][:k], fx["l"][:k], fx["c"][:k], fx["tc"], fx["hour"][:k])
    lvl_ok = np.array_equal(np.nan_to_num(full["long_level"][:k - 1]),
                            np.nan_to_num(trunc["long_level"][:k - 1]))
    print(f"  [e] no-look-ahead: nr7 level[i] truncation-invariant (decidable KABLA ya entry) -> {lvl_ok}")
    ok = ok and lvl_ok

    # (a) FORWARD DETERMINISM: run mbili -> log records bit-identical
    fxs = {"USDCHF": _fixture(1), "USDJPY": _fixture(2)}
    s1, s2 = [], []
    r1 = run(cfg=cfg, sink=s1, _loader=_mk_loader(fxs))
    r2 = run(cfg=cfg, sink=s2, _loader=_mk_loader(fxs))
    import json as _json
    det = _json.dumps(s1, sort_keys=True, default=str) == _json.dumps(s2, sort_keys=True, default=str)
    print(f"  [a] forward determinism: cands={r1['candidates']} filled={r1['filled']} "
          f"rejected={r1['rejected']} bit-identical={det} -> {det and r1 == r2}")
    ok = ok and det and r1 == r2

    # (d) LOG SCHEMA round-trip: records za engine zina keys HASA za dashboard loader
    kinds = {r["kind"] for r in s1}
    execs = [r["obj"] for r in s1 if r["kind"] == "execution"]
    setts = [r["obj"] for r in s1 if r["kind"] == "settlement"]
    decs = [r["obj"] for r in s1 if r["kind"] == "decision"]
    exec_keys = all({"order_id", "pair", "side", "qty", "entry", "sl", "tp", "status", "as_of",
                     "mode"} <= set(e) for e in execs)
    sett_keys = all({"id", "realized_pnl", "pnl_r", "exit_price", "as_of"} <= set(s) for s in setts)
    # REPO REQUIRED (kingekamata 'pnl' iliyokosekana — self-test ilitumia sink, si repo.append):
    from decision_repository import REQUIRED as _REQ
    repo_req = all(set(_REQ[r["kind"]]) <= set(r["obj"]) for r in s1)
    gate_keys = any(isinstance(dd.get("eligibility"), dict)
                    and {"passed", "failed"} <= set(dd["eligibility"]) for dd in decs)
    sig_keys = any("aggregate" in dd for dd in decs)
    linked = _index(s1)
    closed = [t for t in linked.values() if t["_closed"]]
    round_trip = (kinds == {"decision", "execution", "settlement"} and exec_keys and sett_keys
                  and repo_req and gate_keys and sig_keys and len(closed) == r1["filled"]
                  and all(t["mode"] == "paper" for t in linked.values()))
    print(f"  [d] log schema round-trip: kinds={sorted(kinds)} exec/sett/gate/sig keys ok; "
          f"repo-REQUIRED ok={repo_req}; filled trades linked+closed={len(closed)}=={r1['filled']} -> {round_trip}")
    ok = ok and round_trip

    # (b) COMPLIANCE-VETO: max_daily_loss ndogo -> gate REJECTED + ime-log kwa sababu (execution REJECTED)
    cfg_veto = dict(cfg, max_daily_loss=0.01)
    sv = []
    rv = run(cfg=cfg_veto, sink=sv, _loader=_mk_loader(fxs))
    rej_execs = [r["obj"] for r in sv if r["kind"] == "execution" and r["obj"]["status"] == "REJECTED"]
    veto_logged = (rv["filled"] == 0 and rv["rejected"] > 0 and len(rej_execs) == rv["rejected"]
                   and all("daily_loss" in e.get("reject_reason", "") for e in rej_execs)
                   and not any(r["kind"] == "settlement" for r in sv))     # hakuna trade halisi
    print(f"  [b] compliance-veto: rejected={rv['rejected']} filled=0, kila moja ime-log kwa sababu "
          f"(daily_loss); hakuna settlement -> {veto_logged}")
    ok = ok and veto_logged

    # (c) SIZER budget=0 -> qty=0 -> hakuna trade (rejected, hakuna execution FILLED)
    cfg_b0 = dict(cfg, daily_budget_start=0.0, win_factor=0.0)
    sb = []
    rb = run(cfg=cfg_b0, sink=sb, _loader=_mk_loader(fxs))
    filled_execs = [r for r in sb if r["kind"] == "execution" and r["obj"]["status"] == "FILLED"]
    qty0 = (rb["filled"] == 0 and not filled_execs
            and all("qty=0" in r["obj"].get("reject_reason", "")
                    for r in sb if r["kind"] == "execution"))
    print(f"  [c] sizer budget=0 -> qty=0: filled={rb['filled']}(==0) hakuna execution FILLED -> {qty0}")
    ok = ok and qty0

    # mode=paper PEKEE (kila execution) — nidhamu ya charter
    mode_ok = all(r["obj"].get("mode") == "paper" for r in s1 if r["kind"] == "execution")
    print(f"  [f] mode=paper pekee (kila execution) -> {mode_ok}")
    ok = ok and mode_ok

    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true", help="endesha forward paper loop (replay validation)")
    ap.add_argument("--split", default="validation", help="validation (default) | train (replay)")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.run:
        print("Tumia --run (forward paper) | --self-test.", file=sys.stderr)
        return 2
    if a.split == "holdout":
        print("RED LINE: HOLDOUT HAIGUSWI na live_engine (paper forward/replay pekee).", file=sys.stderr)
        return 2
    res = run(split=a.split)
    print(f"LIVE PAPER ENGINE ({a.split}): candidates={res['candidates']} FILLED={res['filled']} "
          f"REJECTED={res['rejected']} cum_pnl=${res['cum_pnl']}")
    print(f"  log: {res['log']} (append-only) -> dashboard ingest (bila --demo)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
