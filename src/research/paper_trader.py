"""
paper_trader.py — FORWARD PAPER-TRADING CLI (mkutano wa MWONGOZO na mashine; Chief direct).

Signal yako ya mkono (MWONGOZO) inapita kwenye MASHINE badala ya checklist ya karatasi:
  --signal: Engine(decide) -> Gate(FTMO checks 5) -> Size(MWONGOZO s1) -> paper-fill -> log (E3)
  --close:  Settlement (PnL ya paper) + bajeti ya siku ina-update (win_factor/loss_factor)
  --status: hali ya akaunti ya paper (bajeti, slots, positions wazi)

FORWARD pekee (pre-registered by construction — kila decision inarekodiwa KABLA ya matokeo).
HAKUNA pesa halisi. HAKUNA network. Log: data/paper/paper_log.jsonl (append-only, committed git).
Protocol: docs/RUNBOOK_forward_paper_trading.md. Profitable != Tradable Edge.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import date

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from decision_engine import decide
from integrity_gate import gate
from execution_object import record as record_execution
from broker_adapter import build_constraints, build_context, size, settle, to_execution_report
import decision_repository as repo

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PAPER_DIR = os.path.join(ROOT, "data", "paper")
STATE_F = os.path.join(PAPER_DIR, "account_state.json")
LOG_F = os.path.join(PAPER_DIR, "paper_log.jsonl")
VERSIONS = {"schema_version": "snapshot@v1", "doctrine_version": "V12"}
OPERATOR_POLICY = {"id": "policy:operator-signal@v1",
                   "decide": lambda s: ("SELECT", "manual signal ya Operator (MWONGOZO)")}
# pip size ya bei + thamani ya pip kwa LOT 1.0 (approx za MWONGOZO s1; Known Limitation)
PIP_SIZE = lambda pair: 0.01 if pair.endswith("JPY") else 0.0001
PIP_VALUE = lambda pair: 6.7 if pair.endswith("JPY") else 10.0


def _load_cfg():
    import yaml
    return yaml.safe_load(open(os.path.join(ROOT, "config", "ftmo_config.yaml"), encoding="utf-8"))


def _default_state():
    return {"date": str(date.today()), "daily_profit": 0.0, "daily_loss": 0.0,
            "cum_pnl": 0.0, "peak_pnl": 0.0, "positions": {}, "next_id": 1, "next_sig": 1}


def _load_state():
    os.makedirs(PAPER_DIR, exist_ok=True)
    st = json.load(open(STATE_F, encoding="utf-8")) if os.path.exists(STATE_F) else _default_state()
    if st["date"] != str(date.today()):                      # siku mpya: bajeti/hasara ya siku reset
        st.update({"date": str(date.today()), "daily_profit": 0.0, "daily_loss": 0.0})
    return st


def _save_state(st):
    json.dump(st, open(STATE_F, "w", encoding="utf-8"), indent=1)


def _budget(cfg, st):
    """MWONGOZO HATUA 1: bajeti = start + wf*faida - lf*hasara (floor 0)."""
    b = (cfg["daily_budget_start"] + cfg["win_factor"] * st["daily_profit"]
         - cfg["loss_factor"] * st["daily_loss"])
    return max(0.0, b)


def _acct_view(cfg, st):
    corr = {}
    for p in st["positions"].values():
        for g, pairs in (cfg.get("correlation_groups") or {}).items():
            if p["pair"] in pairs:
                corr[g] = corr.get(g, 0) + 1
    return {"daily_loss": st["daily_loss"], "total_dd": max(0.0, st["peak_pnl"] - st["cum_pnl"]),
            "open_slots": len(st["positions"]), "correlation_exposure": corr,
            "spread_by_pair": {}}


def cmd_signal(a):
    cfg, st = _load_cfg(), _load_state()
    pair, side = a.signal[0].upper(), a.signal[1].upper()
    entry, sl, tp = (float(x) for x in a.signal[2:5])
    ts = int(time.time())
    sl_pips = abs(entry - sl) / PIP_SIZE(pair)
    pip_val = a.pip_value or PIP_VALUE(pair)
    acct = _acct_view(cfg, st)
    budget = _budget(cfg, st)

    sig_n = st.get("next_sig", 1); st["next_sig"] = sig_n + 1
    snap = {"id": f"signal:{pair}:{ts}:{sig_n}", "as_of": ts, "readiness_state": "READY",
            "reliability": 1.0, "uncertainty": 0.0, "temporal_conflict": 0.0,
            "structural_conflict": {}, "aggregate": {"source": "operator", "support": 1}}
    d = decide(snap, OPERATOR_POLICY)
    repo.append(LOG_F, "decision", {**dict(d), "as_of": ts}, VERSIONS)

    qty = size(cfg, acct, sl_pips, pip_val, budget_remaining=budget)   # lots
    risk = qty * sl_pips * pip_val
    g = gate(d, build_constraints(cfg), build_context(acct, pair, worst_case=risk))
    repo.append(LOG_F, "decision", {**dict(g), "as_of": ts}, VERSIONS)
    if g["lifecycle"] != "VALIDATED":
        print(f"REJECTED na Gate: {list(g['eligibility']['failed'])} -> HAKUNA trade (mtaji umelindwa)")
        _save_state(st)
        return 0
    if qty <= 0:
        print("Bajeti/slots zimeisha (MWONGOZO s1) -> HAKUNA trade")
        _save_state(st)
        return 0

    oid = f"paper:{st['next_id']}"
    trade = {"pair": pair, "side": side, "sl_pips": sl_pips, "pip_value": pip_val,
             "ref_price": entry, "as_of": ts, "sl": sl, "tp": tp}
    report = to_execution_report(trade, qty, {"status": "FILLED", "order_id": oid,
                                              "fills": [{"qty": qty, "price": entry, "ts": ts}]})
    x = record_execution(g, report)
    repo.append(LOG_F, "execution", {**{k: x[k] for k in ("id", "status", "parent_decision_id")}, "as_of": int(x["timestamp"]),
                                     "order_id": oid, "pair": pair, "side": side, "qty": qty,
                                     "entry": entry, "sl": sl, "tp": tp}, VERSIONS)
    st["positions"][oid] = {"pair": pair, "side": side, "entry": entry, "sl": sl, "tp": tp,
                            "qty": qty, "pip_value": pip_val, "exec_id": x["id"], "opened": ts}
    st["next_id"] += 1
    _save_state(st)
    print(f"FILLED (paper): {oid} {pair} {side} qty={qty:.2f} lots @ {entry} "
          f"(risk ${risk:.0f}; SL {sl} / TP {tp}; sl_pips {sl_pips:.1f})")
    print(f"Bajeti iliyobaki: ${_budget(cfg, st):.0f} | slots wazi: {len(st['positions'])}/{cfg['max_slots']}")
    return 0


def cmd_close(a):
    cfg, st = _load_cfg(), _load_state()
    oid, price, ts = a.close, float(a.price), int(time.time())
    if oid not in st["positions"]:
        print(f"HITILAFU: position {oid} haipo. --status kuona zilizo wazi.")
        return 1
    p = st["positions"].pop(oid)
    direction = 1 if p["side"] == "BUY" else -1
    pips = direction * (price - p["entry"]) / PIP_SIZE(p["pair"])
    pnl = round(pips * p["pip_value"] * p["qty"], 2)
    if pnl >= 0:
        st["daily_profit"] += pnl
    else:
        st["daily_loss"] += -pnl
    st["cum_pnl"] += pnl
    st["peak_pnl"] = max(st["peak_pnl"], st["cum_pnl"])
    settle({"id": p["exec_id"]}, realized_pnl=pnl, as_of=ts, repo_path=LOG_F, versions=VERSIONS)
    _save_state(st)
    print(f"CLOSED (paper): {oid} {p['pair']} @ {price} -> PnL ${pnl:+.2f} ({pips:+.1f} pips)")
    print(f"Siku: faida ${st['daily_profit']:.2f} / hasara ${st['daily_loss']:.2f} | "
          f"bajeti sasa ${_budget(cfg, st):.0f} | cum ${st['cum_pnl']:+.2f}")
    return 0


def cmd_status():
    cfg, st = _load_cfg(), _load_state()
    _save_state(st)
    acct = _acct_view(cfg, st)
    print(f"PAPER ACCOUNT ({st['date']}) - HAKUNA pesa halisi")
    print(f"  bajeti iliyobaki: ${_budget(cfg, st):.0f} / start ${cfg['daily_budget_start']}")
    print(f"  siku: faida ${st['daily_profit']:.2f} | hasara ${st['daily_loss']:.2f} "
          f"(limit ${cfg['max_daily_loss']})")
    print(f"  cum PnL: ${st['cum_pnl']:+.2f} | drawdown: ${acct['total_dd']:.2f} "
          f"(limit ${cfg['max_total_dd']})")
    print(f"  slots: {len(st['positions'])}/{cfg['max_slots']} | positions:")
    for oid, p in st["positions"].items() or {}.items():
        print(f"    {oid}: {p['pair']} {p['side']} {p['qty']:.2f} @ {p['entry']} SL {p['sl']} TP {p['tp']}")
    if not st["positions"]:
        print("    (hakuna)")
    recs = repo.load(LOG_F)
    print(f"  log: records {len(recs)} | integrity ok={repo.integrity_check(LOG_F)['ok']}")
    return 0


def self_test():
    import tempfile
    global PAPER_DIR, STATE_F, LOG_F
    ok_all = True
    with tempfile.TemporaryDirectory() as tmp:
        PAPER_DIR, STATE_F, LOG_F = tmp, os.path.join(tmp, "s.json"), os.path.join(tmp, "l.jsonl")
        # [1] signal safi -> FILLED + log
        rc = cmd_signal(argparse.Namespace(signal=["EURUSD", "BUY", "1.0850", "1.0830", "1.0910"],
                                           pip_value=None))
        st = _load_state()
        ok = rc == 0 and len(st["positions"]) == 1 and len(repo.load(LOG_F)) == 3
        ok_all &= ok
        print(f"[1] signal->FILLED+log(3) -> {'OK' if ok else 'FAIL'}")
        # [2] close kwa faida -> settlement + bajeti inakua (win_factor)
        oid = next(iter(st["positions"]))
        rc = cmd_close(argparse.Namespace(close=oid, price="1.0900"))
        st = _load_state()
        ok = rc == 0 and st["daily_profit"] > 0 and not st["positions"] and \
            any(r["kind"] == "settlement" for r in repo.load(LOG_F))
        ok_all &= ok
        print(f"[2] close->settlement+profit -> {'OK' if ok else 'FAIL'}")
        # [3] FTMO breach (daily loss karibu na limit) -> Gate REJECTED, hakuna position
        st["daily_loss"] = 499.0
        _save_state(st)
        rc = cmd_signal(argparse.Namespace(signal=["EURUSD", "BUY", "1.0850", "1.0830", "1.0910"],
                                           pip_value=None))
        st = _load_state()
        ok = rc == 0 and len(st["positions"]) == 0
        ok_all &= ok
        print(f"[3] FTMO-breach->Gate REJECTED (mtaji umelindwa) -> {'OK' if ok else 'FAIL'}")
        ok = repo.integrity_check(LOG_F)["ok"]
        ok_all &= ok
        print(f"[4] log integrity -> {'OK' if ok else 'FAIL'}")
    print(f"\nSELF-TEST: {'PASS' if ok_all else 'FAIL'}")
    return 0 if ok_all else 1


def main():
    ap = argparse.ArgumentParser(description="Forward paper-trading (MWONGOZO kupitia mashine)")
    ap.add_argument("--signal", nargs=5, metavar=("PAIR", "SIDE", "ENTRY", "SL", "TP"))
    ap.add_argument("--policy", default="operator-signal")
    ap.add_argument("--pip-value", type=float, dest="pip_value", default=None)
    ap.add_argument("--close", metavar="ORDER_ID")
    ap.add_argument("--price", default=None)
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.signal:
        return cmd_signal(a)
    if a.close:
        if a.price is None:
            print("--close inahitaji --price")
            return 1
        return cmd_close(a)
    if a.status:
        return cmd_status()
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
