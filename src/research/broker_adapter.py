"""
broker_adapter.py — EXECUTION SCIENCE E4 (P81/P106; Chief-approved spec + rulings Q1-Q6).

THE TWO STREAMS MEET. Broker Adapter = **mpaka wa impurity + mtafsiri** kati ya Decision Science
(pure) na MWONGOZO/FTMO/MT5 (external). Inafunga loop ya E1: MWONGOZO CHECK 1-5 (ftmo_config) →
E1 EligibilityConstraints (5 tofauti) + context (account state) → Gate. Sizing (MWONGOZO §1) →
ExecutionReport → Recorder (E2). Settlement → Repository (E3, kind=settlement).

**PAPER-MODE PEKEE** (Chief E4 impl): `mode=live` = **refuse-stub** (AdapterError) hadi Project
Director athibitishe artifact format. HAKUNA pesa halisi. HAKUNA network (PaperBroker = simulator).

Chief rulings (2026-07-05, E4 spec APPROVED):
  Q1  live-gating = artifact + PD signature + mode=live explicit; bila hiyo REFUSE (PD = final).
  Q2  FTMO CHECK 1-5 = constraints 5 TOFAUTI (kila moja auditable; E1 AND/veto).
  Q3  sizing inaishi Adapter kwa sasa (P96 sizing-policy = baadaye — usifunge design).
  Q4  Settlement = kind=settlement kwenye Repository (decision_repository.py — imefanywa).
  Q5  account_state contract: daily_loss/total_dd/open_slots/correlation_exposure/spread_by_pair.
  Q6  max_spread per-pair = kazi ya Operator (ftmo_config) — spread-constraint inapita kama haipo.

Rules: Rule 3 (Adapter = translator, si decider — Gate ndiyo inaevaluate) · Rule 4 (imports =
execution_object + decision_repository + frozen + stdlib → **transitively PURE**; ftmo_config/broker/
account = INJECTED, si file/network ndani ya core) · Rule 5/6/7. Doctrine: P81 (FTMO=constraint),
P92/P107 (impurity boundary), P97 (translate don't decide), Master §7.5 (Protect capital first).

Self-test: python src/research/broker_adapter.py --self-test  (paper, bila network/pesa)
"""
from __future__ import annotations

import argparse
import hashlib

from frozen import freeze
from execution_object import record as record_execution      # E2 Recorder
import decision_repository as repo                            # E3 (append kind=execution|settlement)

ADAPTER_ID = "adapter:broker@v1"
MODES = ("paper", "live")
# account_state contract (Chief Q5)
ACCOUNT_REQUIRED = ("daily_loss", "total_dd", "open_slots", "correlation_exposure", "spread_by_pair")
# ftmo_config fields muhimu kwa constraints + sizing
CONFIG_REQUIRED = ("max_slots", "max_correlated_slots", "max_daily_loss", "max_total_dd",
                   "daily_budget_start", "max_per_trade", "correlation_groups")


class AdapterError(ValueError):
    """Adapter boundary request batili (structural/gating — SIO outcome; outcome=REJECTED ni E2)."""


# ---------------------------------------------------------------- validation (Q8)
def validate_account_state(account_state):
    if not isinstance(account_state, dict):
        raise AdapterError("invalid_context: account_state si dict")
    missing = [f for f in ACCOUNT_REQUIRED if f not in account_state]
    if missing:
        raise AdapterError(f"invalid_context: account_state inakosa {missing}")
    return account_state


def validate_config(ftmo_config):
    if not isinstance(ftmo_config, dict):
        raise AdapterError("invalid_config: si dict")
    missing = [f for f in CONFIG_REQUIRED if f not in ftmo_config]
    if missing:
        raise AdapterError(f"invalid_config: inakosa {missing}")
    return ftmo_config


# ---------------------------------------------------------------- Q1.1: FTMO CHECK 1-5 → E1 constraints (P81)
def _groups_of(pair, correlation_groups):
    return [g for g, members in correlation_groups.items() if pair in members]


def build_constraints(ftmo_config):
    """MWONGOZO CHECK 1-5 → EligibilityConstraints 5 TOFAUTI (Chief Q2). Kila moja = {id, check} kwa
    E1 contract: check(decision, context) → (ELIGIBLE|INELIGIBLE, reason). Config = thresholds
    (closure); context = live account state (read-time). Adapter HAIzihukumu — Gate ndiyo (P97)."""
    validate_config(ftmo_config)
    cfg = ftmo_config

    def daily_loss(decision, context):                        # CHECK 1 (worst-case: SL zote wazi)
        wc = context.get("worst_case", 0)
        bad = context["daily_loss"] + wc >= cfg["max_daily_loss"]
        return ("INELIGIBLE" if bad else "ELIGIBLE",
                f"daily_loss {context['daily_loss']}+wc{wc} vs {cfg['max_daily_loss']}")

    def total_dd(decision, context):                          # CHECK 2
        wc = context.get("worst_case", 0)
        bad = context["total_dd"] + wc >= cfg["max_total_dd"]
        return ("INELIGIBLE" if bad else "ELIGIBLE",
                f"total_dd {context['total_dd']}+wc{wc} vs {cfg['max_total_dd']}")

    def slots(decision, context):                             # CHECK 3
        bad = context["open_slots"] >= cfg["max_slots"]
        return ("INELIGIBLE" if bad else "ELIGIBLE",
                f"open_slots {context['open_slots']} vs {cfg['max_slots']}")

    def correlation(decision, context):                       # CHECK 4
        pair = context["pair"]
        groups = _groups_of(pair, cfg["correlation_groups"])
        exp = context.get("correlation_exposure", {})
        over = [g for g in groups if exp.get(g, 0) >= cfg["max_correlated_slots"]]
        return ("INELIGIBLE" if over else "ELIGIBLE", f"pair={pair} groups={groups} over={over}")

    def spread(decision, context):                            # CHECK 5 (Q6: max_spread = Operator config)
        pair = context["pair"]
        maxs = cfg.get("max_spread", {})
        if pair not in maxs:
            return ("ELIGIBLE", f"max_spread haijawekwa kwa {pair} (Operator Q6) → pass")
        cur = context["spread_by_pair"].get(pair)
        bad = cur is not None and cur > maxs[pair]
        return ("INELIGIBLE" if bad else "ELIGIBLE", f"spread {cur} vs max {maxs[pair]}")

    return [{"id": "constraint:daily_loss@v1", "check": daily_loss},
            {"id": "constraint:total_dd@v1", "check": total_dd},
            {"id": "constraint:slots@v1", "check": slots},
            {"id": "constraint:correlation@v1", "check": correlation},
            {"id": "constraint:spread@v1", "check": spread}]


def build_context(account_state, pair, worst_case=0):
    """context kwa Gate (E1): live account state + pair + worst_case (SL zote wazi — MWONGOZO)."""
    validate_account_state(account_state)
    ctx = {k: account_state[k] for k in ACCOUNT_REQUIRED}
    ctx["pair"] = pair
    ctx["worst_case"] = worst_case
    return ctx


# ---------------------------------------------------------------- Q1.2: sizing (MWONGOZO §1)
def size(ftmo_config, account_state, sl_pips, pip_value, budget_remaining=None):
    """DailyRiskBudgetSizer (MWONGOZO §1): risk_$ = min(budget_remaining ÷ slots_remaining,
    max_per_trade); qty = risk_$ ÷ (sl_pips × pip_value). Bajeti/slots zikiwa 0 → qty=0 (hakuna trade).
    budget_remaining default = daily_budget_start (mwanzo wa siku)."""
    validate_config(ftmo_config)
    validate_account_state(account_state)
    slots_remaining = ftmo_config["max_slots"] - account_state["open_slots"]
    if slots_remaining <= 0:
        return 0.0
    budget = ftmo_config["daily_budget_start"] if budget_remaining is None else budget_remaining
    risk = min(budget / slots_remaining, ftmo_config["max_per_trade"])
    if risk <= 0 or sl_pips <= 0 or pip_value <= 0:
        return 0.0
    return risk / (sl_pips * pip_value)


# ---------------------------------------------------------------- Q7: PaperBroker (injected simulator)
class PaperBroker:
    """Simulator ya paper-mode: deterministic, HAKUNA network, HAKUNA pesa. Kwa self-test + paper.
    Status inaderivishwa kutoka fill_ratio (inalingana na intended qty) ili E2 Recorder cross-check ipite."""

    def __init__(self, fill_ratio=1.0, slippage=0.0, reject=False):
        self.fill_ratio = fill_ratio
        self.slippage = slippage
        self.reject = reject
        self._n = 0

    def submit(self, order):
        self._n += 1
        oid = f"paper:{self._n}"
        if self.reject:
            return {"order_id": oid, "status": "REJECTED", "fills": [], "reject_reason": "paper: rejected"}
        filled = order["qty"] * self.fill_ratio
        if filled <= 0:
            return {"order_id": oid, "status": "UNFILLED", "fills": []}
        status = "FILLED" if filled >= order["qty"] else "PARTIAL"
        fills = [{"qty": filled, "price": order["ref_price"] + self.slippage, "ts": order["as_of"]}]
        return {"order_id": oid, "status": status, "fills": fills}


# ---------------------------------------------------------------- Q1.3/4: submit → ExecutionReport → Recorder
def to_execution_report(trade, qty, broker_outcome):
    """broker outcome → ExecutionReport (E2 Q7 contract). intended.qty = sizing (E4 path, E2 Q5)."""
    return {"status": broker_outcome["status"],
            "intended": {"side": trade["side"], "qty": qty, "ref_price": trade["ref_price"]},
            "fills": broker_outcome["fills"],
            "reject_reason": broker_outcome.get("reject_reason"),
            "as_of": trade["as_of"],
            "report_ref": broker_outcome.get("order_id")}


def _repo_view(obj):
    """Persistence view (plain) + normalize timestamp→as_of kwa query layer ya E3 (tazama Known Limitations)."""
    view = dict(repo._plain(obj))
    if "as_of" not in view and "timestamp" in view:
        view["as_of"] = view["timestamp"]
    return view


def execute(decision, trade, ftmo_config, account_state, broker, mode="paper",
            live_authorized=False, repo_path=None, versions=None):
    """Adapter flow (paper): gate-mode → size → submit → ExecutionReport → Recorder (E2) → Repository (E3).
    Constraints/context (Gate E1) ni hatua tofauti (build_constraints/build_context) — caller anaita Gate
    KABLA ya execute. Adapter haitumi order kwa decision isiyo VALIDATED (Q8)."""
    if mode not in MODES:
        raise AdapterError(f"invalid_mode: {mode}")
    if mode == "live" and not live_authorized:               # Q1 RED LINE — Project Director gate
        raise AdapterError("live_not_authorized: Project Director approval inahitajika (mode=live refuse-stub)")
    if decision.get("lifecycle") != "VALIDATED":
        raise AdapterError(f"invalid_decision: lifecycle {decision.get('lifecycle')} (VALIDATED pekee)")
    validate_account_state(account_state)
    qty = size(ftmo_config, account_state, trade["sl_pips"], trade["pip_value"])
    if qty <= 0:
        return None                                          # bajeti/slots zimeisha → hakuna order (SIO error)
    order = {"decision_id": decision["id"], "pair": trade["pair"], "side": trade["side"],
             "qty": qty, "ref_price": trade["ref_price"], "as_of": trade["as_of"],
             "sl": trade.get("sl"), "tp": trade.get("tp")}
    outcome = broker.submit(order)
    report = to_execution_report(trade, qty, outcome)
    execution = record_execution(decision, report)           # E2 Execution Object (frozen)
    if repo_path is not None and versions is not None:
        repo.append(repo_path, "execution", _repo_view(execution), versions)
    return execution


# ---------------------------------------------------------------- Q1.5: Settlement (E3 kind=settlement)
def settle(execution, realized_pnl, as_of, ret=None, holding_period=None, costs=None,
           repo_path=None, versions=None):
    """close-fill → Settlement record (E3 kind=settlement). PnL ni FACT iliyorekodiwa; je ni edge? = D8."""
    sid = "settle:" + hashlib.sha1(f"{execution['id']}|{int(as_of)}".encode()).hexdigest()[:10]
    settlement = freeze({"id": sid, "parent_execution_id": execution["id"], "recorder_id": ADAPTER_ID,
                         "pnl": realized_pnl, "return": ret, "holding_period": holding_period,
                         "costs": costs, "as_of": int(as_of)})
    if repo_path is not None and versions is not None:
        repo.append(repo_path, "settlement", _repo_view(settlement), versions)
    return settlement


# ---------------------------------------------------------------- self-tests (Rule 7)
def _cfg():
    return {"max_slots": 4, "max_correlated_slots": 2, "max_daily_loss": 500, "max_total_dd": 1000,
            "daily_budget_start": 400, "max_per_trade": 120,
            "correlation_groups": {"USD_group": ["EURUSD", "GBPUSD"], "EUR_group": ["EURUSD", "EURJPY"]},
            "max_spread": {"EURUSD": 1.5}}


def _acct(daily_loss=0, total_dd=0, open_slots=0, corr=None, spread=None):
    return {"daily_loss": daily_loss, "total_dd": total_dd, "open_slots": open_slots,
            "correlation_exposure": corr or {}, "spread_by_pair": spread or {"EURUSD": 0.8}}


def _decision(lifecycle="VALIDATED", action="ENTER", did="dec:val01"):
    return {"id": did, "action": action, "reason": "t", "evidence_refs": ("snap:1",),
            "policy_id": "policy:t@v1", "parent_decision_id": "dec:prop01", "gate_id": "gate:integrity@v1",
            "lifecycle": lifecycle, "timestamp": 100, "audit": ["mk", "gate"]}


def _trade(pair="EURUSD", side="BUY", qty=100, ref_price=1.2000, sl_pips=20, pip_value=0.1, as_of=100):
    return {"pair": pair, "side": side, "qty": qty, "ref_price": ref_price, "sl_pips": sl_pips,
            "pip_value": pip_value, "as_of": as_of, "sl": 1.1980, "tp": 1.2040}


def _v():
    return {"schema_version": "exec@v1", "doctrine_version": "V12"}


def self_test():
    import os
    import tempfile
    ok_all = True

    # (1) FTMO CHECK 1-5 → constraints 5 TOFAUTI (Q2); E1 contract (id + check callable)
    cons = build_constraints(_cfg())
    ids = [c["id"] for c in cons]
    ok = (len(cons) == 5 and all(callable(c["check"]) for c in cons)
          and ids == ["constraint:daily_loss@v1", "constraint:total_dd@v1", "constraint:slots@v1",
                      "constraint:correlation@v1", "constraint:spread@v1"])
    ok_all &= ok
    print(f"[1] FTMO→5 constraints (E1 contract): ids={len(ids)} callable=all -> {'OK' if ok else 'FAIL'}")

    # (2) constraints evaluate live context: each INELIGIBLE kwa hali husika, ELIGIBLE kwa safi
    d = _decision()
    cmap = {c["id"]: c["check"] for c in cons}
    ctx_ok = build_context(_acct(), "EURUSD", worst_case=50)
    all_elig = all(cmap[i](d, ctx_ok)[0] == "ELIGIBLE" for i in ids)
    v_dl = cmap["constraint:daily_loss@v1"](d, build_context(_acct(daily_loss=460), "EURUSD", worst_case=50))[0]
    v_dd = cmap["constraint:total_dd@v1"](d, build_context(_acct(total_dd=980), "EURUSD", worst_case=50))[0]
    v_sl = cmap["constraint:slots@v1"](d, build_context(_acct(open_slots=4), "EURUSD"))[0]
    v_co = cmap["constraint:correlation@v1"](d, build_context(_acct(corr={"USD_group": 2}), "EURUSD"))[0]
    v_sp = cmap["constraint:spread@v1"](d, build_context(_acct(spread={"EURUSD": 2.0}), "EURUSD"))[0]
    ok = (all_elig and v_dl == "INELIGIBLE" and v_dd == "INELIGIBLE" and v_sl == "INELIGIBLE"
          and v_co == "INELIGIBLE" and v_sp == "INELIGIBLE")
    ok_all &= ok
    print(f"[2] constraints evaluate: all-clean=ELIGIBLE dl/dd/slot/corr/spread=INELIGIBLE -> {'OK' if ok else 'FAIL'}")

    # (3) sizing (MWONGOZO §1): risk=min(400/4,120)=100 → qty=100/(20*0.1)=50; slots full → 0
    q = size(_cfg(), _acct(open_slots=0), sl_pips=20, pip_value=0.1)
    q_full = size(_cfg(), _acct(open_slots=4), sl_pips=20, pip_value=0.1)
    q_cap = size(_cfg(), _acct(open_slots=0), sl_pips=1, pip_value=0.1)     # risk capped 100 → qty=1000
    ok = abs(q - 50.0) < 1e-9 and q_full == 0.0 and abs(q_cap - 1000.0) < 1e-9
    ok_all &= ok
    print(f"[3] sizing (MWONGOZO §1): qty={q} slots-full={q_full} -> {'OK' if ok else 'FAIL'}")

    # (4) execute paper FILLED → Execution Object (E2) + append repo (E3)
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "log.jsonl")
        x = execute(d, _trade(), _cfg(), _acct(), PaperBroker(slippage=0.0002), repo_path=p, versions=_v())
        recs = repo.load(p)
        ok = (x["status"] == "FILLED" and x["parent_decision_id"] == d["id"]
              and abs(x["filled_qty"] - 50.0) < 1e-9 and x["intent"] == "ENTER"
              and len(recs) == 1 and recs[0]["kind"] == "execution" and recs[0]["obj"]["as_of"] == 100)
        ok_all &= ok
        print(f"[4] execute paper FILLED + repo: status={x['status']} qty={x['filled_qty']} repo={len(recs)} -> {'OK' if ok else 'FAIL'}")

        # (5) PARTIAL / REJECTED / qty<=0 → None
        xp = execute(d, _trade(), _cfg(), _acct(), PaperBroker(fill_ratio=0.4))
        xr = execute(d, _trade(), _cfg(), _acct(), PaperBroker(reject=True))
        xn = execute(d, _trade(), _cfg(), _acct(open_slots=4), PaperBroker())    # slots full → qty 0 → None
        ok = xp["status"] == "PARTIAL" and xr["status"] == "REJECTED" and xn is None
        ok_all &= ok
        print(f"[5] outcomes: partial={xp['status']} rejected={xr['status']} no-budget={xn} -> {'OK' if ok else 'FAIL'}")

        # (6) Settlement (Q4) → repo kind=settlement
        s = settle(x, realized_pnl=42.5, as_of=200, repo_path=p, versions=_v())
        recs = repo.load(p)
        ok = (s["parent_execution_id"] == x["id"] and s["pnl"] == 42.5
              and any(r["kind"] == "settlement" for r in recs))
        ok_all &= ok
        print(f"[6] settlement→repo: parent={s['parent_execution_id']==x['id']} pnl={s['pnl']} -> {'OK' if ok else 'FAIL'}")

    # (7) live-gating RED LINE (Q1): mode=live bila approval → AdapterError; invalid decision → error
    try:
        execute(d, _trade(), _cfg(), _acct(), PaperBroker(), mode="live"); g1 = False
    except AdapterError:
        g1 = True
    try:
        execute(_decision(lifecycle="PROPOSED"), _trade(), _cfg(), _acct(), PaperBroker()); g2 = False
    except AdapterError:
        g2 = True
    ok = g1 and g2
    ok_all &= ok
    print(f"[7] RED LINE live-gating: live-refused={g1} non-VALIDATED-blocked={g2} -> {'OK' if ok else 'FAIL'}")

    # (8) Rule 4 purity: imports = execution_object/decision_repository/frozen + stdlib → transitively PURE
    import pathlib
    src = pathlib.Path(__file__).read_text(encoding="utf-8").split("self-tests (Rule 7)")[0]
    imps = [l.strip() for l in src.splitlines()
            if l.strip().startswith(("import ", "from ")) and "broker_adapter" not in l]
    allowed = ("from __future__", "import argparse", "import hashlib", "from frozen",
               "from execution_object", "import decision_repository")
    bad = [i for i in imps if not i.startswith(allowed)]
    leak = ["market_", "num" + "py", "pol" + "ars", "mt5", "MetaTrader", "requests", "socket"]
    leak_imports = [i for i in imps if any(w in i.lower() for w in leak)]
    ok = bad == [] and leak_imports == []
    ok_all &= ok
    print(f"[8] Rule 4 purity (no network/market): bad={bad} leak={leak_imports} -> {'OK' if ok else 'FAIL'}")

    print(f"\nSELF-TEST: {'PASS' if ok_all else 'FAIL'}")
    return 0 if ok_all else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    if ap.parse_args().self_test:
        return self_test()
    print("Broker Adapter (E4) — paper-mode. Constraints/broker/config INJECTED. Tumia --self-test. "
          "Live = refuse-stub (Project Director gate).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
