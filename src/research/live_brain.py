"""
live_brain.py — CONDUIT BRIDGE Awamu 1 (docs/CONDUIT_BRIDGE_CHARTER.md; Doctrine §9).

UBONGO (Python) = inayoAMUA. EA-conduit (Awamu 2) = inayoTEKELEZA tu. Python HAIWEKI order kamwe
(HAKUNA MetaTrader5 import) — transport = faili za JSON kwenye bridge dir.

  (a) EDGE DECISION: bar ya mwisho ILIYOFUNGWA -> nr7 -> no-LATE (entry bar = inayofuata) -> ATR ya
      signal bar -> SL/TP -> size (DailyRiskBudgetSizer+FTMO) -> compliance (integrity_gate). PASS ->
      PLACE_OCO; FAIL/veto -> hakuna amri + sababu. HAKUNA fill-sim (fills halisi zinatoka EA).
  (b) COMMANDS WRITER: <bridge>/commands.json (atomic tmp+replace; idempotent kwa cmd_id).
  (c) RESULTS INGESTER: <bridge>/results.json(l) -> decision_repository records HALALI (FILLED->
      execution, CLOSED->settlement+pnl) -> append data/paper/paper_log.jsonl (dashboard/steward source).

REUSE PEKEE ya modules zilizopo (nr7_break, _sess/no-LATE, sizer, gate, canonical loader, STRATS) —
ZERO golden kuguswa; STRAT configs HAZIBADILIKI. DEMO PEKEE (§3.1b Faza; live = saini ya PD).

Endesha:  python live_brain.py --cycle [--bridge-dir <dir>]     (ingest results -> edge decide -> commands)
          python live_brain.py --decide | --ingest | --cancel-all
Self-test: python live_brain.py --self-test   (bila MT5 — faili bandia)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

# REUSE ubongo/wiring zilizopo (hakuna logic mpya ya trade)
from live_engine import (STRATS, STRAT_POLICY, TF, LOG_F, _ftmo_config, _acct_state, _acct_view,
                         _budget, _pip_value, _as_of, _canonical_loader, _corr_group,
                         account_state_from_log, models_fingerprint)
import decision_repository as repo
from event_library_v2 import nr7_break
from event_quality_report import _sess
from market_state_engine import pip
from decision_engine import decide
from integrity_gate import gate
from broker_adapter import build_constraints, build_context, size

REPO_ROOT = Path(__file__).resolve().parents[2]
BRIDGE_DEFAULT = str(REPO_ROOT / "data" / "bridge")
BRAIN_VERSIONS = {"schema_version": "live_brain@v1", "doctrine_version": "V2"}
H1_SECONDS = 3600
# magic per strategy (EA inatofautisha instances)
MAGIC = {"STRAT-001": 20260730001, "STRAT-002": 20260730002}


def _now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _digits(pair):
    return 3 if "JPY" in pair.upper() else 5


# ==================== (a) EDGE DECISION ====================

def edge_decision(name, strat, data, cfg, constraints, pair=None, st=None):
    """Uamuzi kwenye UKINGO kwa bar ya mwisho iliyofungwa. Rudisha (command|None, reason).
    pair = pair mahususi (model ina pairs[] — PD 2026-07-30). st = hali HALISI ya akaunti
    (account_state_from_log) — bila hii bajeti/slots ni bandia.
    REUSE: nr7_break, _sess (no-LATE = entry bar i+1), DailyRiskBudgetSizer, integrity_gate.
    ATR = data['atr'][i] (signal bar; parity na live_engine.candidates a=atr[i]). PIP-SPACE -> price."""
    o, h, l_, c = data["o"], data["h"], data["l"], data["c"]
    atr, hour, spr, ts = data["atr"], data["hour"], data["spr"], data["ts"]
    n = len(c)
    if n < 8:
        return None, "insufficient bars"
    pair = pair or strat["pair"]                           # model ina pairs[] (PD 2026-07-30)
    i = n - 1                                              # bar ya mwisho ILIYOFUNGWA = signal bar
    out = nr7_break(o, h, l_, c, data.get("tc"), hour)     # REUSE golden (byte-identical)
    LL, SS = out["long_level"], out["short_level"]
    if not (np.isfinite(LL[i]) and np.isfinite(SS[i])):
        return None, "no nr7 compression (range si nyembamba zaidi ya bars 7)"
    # no-LATE: session ya bar ya ENTRY (i+1) — ratiba ex-ante (H1 -> hour+1). Parity na _mask_context.
    entry_hour = (int(hour[i]) + 1) % 24
    if _sess(entry_hour) == "LATE":
        return None, f"no-LATE veto (entry hour {entry_hour} = LATE)"
    a = float(atr[i])
    if not (a > 0):
        return None, "atr<=0"
    sl_pips = strat["sl_atr"] * a
    ts_epoch = _as_of(ts[i])                               # signal bar open (canonical ts = bucket start)

    # SIGNAL decision (readiness snapshot) — REUSE decide/policy (kama live_engine)
    snap = {"id": f"signal:{name}:{pair}:{ts_epoch}", "as_of": ts_epoch,
            "readiness_state": "READY", "reliability": 1.0, "uncertainty": 0.0,
            "temporal_conflict": 0.0, "structural_conflict": {},
            "aggregate": {"source": name, "support": 1, "learned_ev": strat["learned_ev"]}}
    dsig = decide(snap, STRAT_POLICY)

    # SIZE (DailyRiskBudgetSizer+FTMO) — account view fresh (BRIDGE-1: brain haitunzi state ya cross-bar;
    # daily-state reconstruction kutoka paper_log = awamu ijayo). spread ya bar hii ndani ya context.
    st = _acct_state() if st is None else st                # HALI HALISI inatoka decide_all
    acct = _acct_view(cfg, st)
    acct["spread_by_pair"] = {pair: float(spr[i])}
    qty = size(cfg, acct, sl_pips, _pip_value(pair), budget_remaining=_budget(cfg, st))
    risk = qty * sl_pips * _pip_value(pair)

    # COMPLIANCE (integrity_gate)
    g = gate(dsig, constraints, build_context(acct, pair, worst_case=risk))
    elig = dict(g["eligibility"])
    if g["lifecycle"] != "VALIDATED":
        return None, "gate veto: " + (",".join(elig.get("failed", [])) or "not VALIDATED")
    if qty <= 0:
        return None, "budget/slots=0 -> qty=0"

    # levels PIP-SPACE -> PRICE (canonical o/h/l/c ni price/pip)
    pp = pip(pair); dg = _digits(pair)
    buy_stop = LL[i]; sell_stop = SS[i]
    cmd = dict(
        cmd_id=f"{name}:{pair}:{ts_epoch}", action="PLACE_OCO", strategy=name, symbol=pair,
        magic=MAGIC.get(name), lots=round(float(qty), 2),
        buy_stop=round(float(buy_stop) * pp, dg), sell_stop=round(float(sell_stop) * pp, dg),
        sl_buy=round(float(buy_stop - strat["sl_atr"] * a) * pp, dg),
        tp_buy=round(float(buy_stop + strat["tp_atr"] * a) * pp, dg),
        sl_sell=round(float(sell_stop + strat["sl_atr"] * a) * pp, dg),
        tp_sell=round(float(sell_stop - strat["tp_atr"] * a) * pp, dg),
        bar_ts=ts_epoch,
        expiry_utc=ts_epoch + 2 * H1_SECONDS)             # +1h baada ya bar-close (entry window = bar 1)
    return cmd, "PLACE_OCO"


def decide_all(bridge_dir, cfg=None, loader=None, write=True, log_path=None, now_epoch=None,
               models=None, log_rejections=True):
    """Edge decision kwa MODELS zote x PAIRS zao -> commands.json (PD 2026-07-30).

    - MODELS zote zinatafuta entries kwa uhuru (hakuna kizuizi cha model-level); pairs = zile
      zilizofanya vizuri kwenye utafiti (config/models.yaml, PD anahariri BILA code).
    - RISK MANAGEMENT ndilo LANGO PEKEE: hali HALISI (account_state_from_log) -> bajeti ya siku
      (win_factor/loss_factor) + max_slots/max_correlated_slots. Ikizidi -> REJECT + SABABU.
    - SLOT RESERVATION: amri ikikubaliwa, slots/correlation zinaongezwa PROVISIONALLY ndani ya batch
      ili pendekezo la 8 lisipite wakati max_slots=7 (vinginevyo zote zingepita kwa pamoja).
    """
    cfg = cfg or _ftmo_config()
    constraints = build_constraints(cfg)
    lw = loader or _canonical_loader()
    strats = models or STRATS
    st = account_state_from_log(log_path=log_path or LOG_F, cfg=cfg, now_epoch=now_epoch)
    cmds, reasons, rejects = [], {}, []
    for name, strat in strats.items():
        for pair in strat.get("pairs", [strat.get("pair")]):
            key = f"{name}:{pair}"
            data = lw(pair, TF, "forward")
            if data is None or data.get("ts") is None or len(data["ts"]) == 0:
                reasons[key] = "no data (canonical haipo)"; continue
            cmd, why = edge_decision(name, strat, data, cfg, constraints, pair=pair, st=st)
            reasons[key] = why
            if cmd is None:
                if why not in ("no nr7 compression (range si nyembamba zaidi ya bars 7)",
                               "insufficient bars", "atr<=0"):
                    rejects.append(dict(key=key, name=name, pair=pair, reason=why,
                                        as_of=int(_as_of(data["ts"][-1]))))
                continue
            cmds.append(cmd)
            st["open_slots"] += 1                          # RESERVATION (batch-aware max-open)
            g = _corr_group(pair, cfg)
            st["correlation_exposure"][g] = st["correlation_exposure"].get(g, 0) + 1
    if log_rejections and rejects:
        _log_rejections(rejects, log_path or LOG_F, cfg)
    seq = None
    if write:
        seq = write_commands(bridge_dir, cmds)["seq"]
    return dict(commands=cmds, reasons=reasons, rejects=rejects, seq=seq,
                account=dict(open_slots=st["open_slots"], daily_profit=st["daily_profit"],
                             daily_loss=st["daily_loss"], budget=_budget(cfg, st)))


def _log_rejections(rejects, log_path, cfg):
    """Rekodi ya trade ILIYOKATALIWA + SABABU (PD: 'ina reject execution na inawekwa sababu').
    decision record (REQUIRED: id/as_of/lifecycle) -> paper_log -> dashboard/steward."""
    for r in rejects:
        obj = {"id": f"reject:{r['key']}:{r['as_of']}", "as_of": r["as_of"], "lifecycle": "REJECTED",
               "strategy": r["name"], "pair": r["pair"], "reason": r["reason"],
               "models_config": models_fingerprint(), "mode": "paper"}
        try:
            repo.append(log_path, "decision", obj, BRAIN_VERSIONS)
        except (OSError, repo.RepositoryError) as e:        # log ni diagnostics — isivunje uamuzi
            print(f"  [warn] rejection-log imeshindwa: {type(e).__name__}: {e}", file=sys.stderr)


# ==================== (b) COMMANDS WRITER (atomic + idempotent) ====================

def _atomic_write_json(path, payload):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(str(tmp), str(path))                       # atomic (same filesystem)


def write_commands(bridge_dir, commands, cancel_all=False):
    """Andika <bridge>/commands.json (atomic). Idempotent: seti ile ile ya cmd_id (hai) -> hakuna
    re-write (seq haiongezeki). cancel_all -> CANCEL_ALL (kill-switch, daima inaandika)."""
    path = Path(bridge_dir) / "commands.json"
    existing = None
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            existing = None
    if cancel_all:
        cmds = [{"cmd_id": f"cancel-all:{int(time.time())}", "action": "CANCEL_ALL"}]
    else:
        cmds = list(commands)
        new_ids = sorted(str(c["cmd_id"]) for c in cmds)
        if existing and sorted(str(c.get("cmd_id")) for c in existing.get("commands", [])) == new_ids:
            return existing                               # idempotent no-op (seti hai ile ile)
    seq = (int(existing.get("seq", 0)) + 1) if existing else 1
    payload = {"seq": seq, "issued_utc": _now_iso(), "commands": cmds}
    _atomic_write_json(path, payload)
    return payload


# ==================== (c) RESULTS INGESTER ====================

def _read_results(bridge_dir):
    """Soma <bridge>/results.jsonl (per-event) au results.json (array/obj). Rudisha list ya events."""
    d = Path(bridge_dir)
    evs = []
    jl, js = d / "results.jsonl", d / "results.json"
    if jl.exists():
        for ln in jl.read_text(encoding="utf-8").splitlines():
            ln = ln.strip()
            if not ln:
                continue
            try:
                evs.append(json.loads(ln))
            except Exception:
                pass
    elif js.exists():
        try:
            data = json.loads(js.read_text(encoding="utf-8"))
            evs = data if isinstance(data, list) else data.get("results", [data])
        except Exception:
            evs = []
    return evs


def _event_to_records(e):
    """Event ya EA -> [(kind, obj)] za decision_repository. FILLED/REJECTED/EXPIRED/CANCELLED ->
    execution; CLOSED -> settlement (+pnl). PLACED/nyingine -> [] (ack tu). learned_ev tag."""
    ev = e.get("event"); cmd_id = str(e.get("cmd_id", ""))
    strat = cmd_id.split(":")[0] if ":" in cmd_id else e.get("strategy", "")
    sconf = STRATS.get(strat, {})
    pair = e.get("symbol") or sconf.get("pair")
    lev = sconf.get("learned_ev")
    oid = e.get("order_id")
    ts = int(e.get("ts", 0))
    if oid is None:
        return []
    if ev == "FILLED":
        return [("execution", {
            "id": f"exec:{oid}", "order_id": oid, "pair": pair, "side": e.get("side"),
            "qty": e.get("qty"), "entry": e.get("price"), "sl": e.get("sl"), "tp": e.get("tp"),
            "status": "FILLED", "as_of": ts, "mode": e.get("mode", "paper"),
            "account": e.get("account", "demo"), "strategy": strat, "learned_ev": lev,
            "cmd_id": cmd_id})]
    if ev in ("REJECTED", "EXPIRED", "CANCELLED"):
        return [("execution", {
            "id": f"exec:{oid}", "order_id": oid, "pair": pair, "side": e.get("side"),
            "qty": 0, "entry": None, "status": ev, "as_of": ts, "mode": e.get("mode", "paper"),
            "account": e.get("account", "demo"), "strategy": strat, "learned_ev": lev,
            "reject_reason": e.get("error", ""), "cmd_id": cmd_id})]
    if ev == "CLOSED":
        pnl = round(float(e.get("pnl", 0.0)), 2)
        return [("settlement", {
            "id": oid, "parent_execution_id": f"exec:{oid}", "pnl": pnl, "realized_pnl": pnl,
            "pnl_r": e.get("pnl_r"), "exit_price": e.get("exit_price"), "as_of": ts})]
    return []


def _append_repo(log_path, kind, obj, sink):
    if sink is not None:
        rec = {"repo_id": "live_brain", "kind": kind, "versions": BRAIN_VERSIONS, "obj": obj}
        sink.append(rec); return rec
    return repo.append(log_path, kind, obj, BRAIN_VERSIONS)


def ingest_results(bridge_dir, log_path=LOG_F, sink=None, events=None):
    """Results -> decision_repository log (append data/paper/paper_log.jsonl). Idempotent kwa record id
    (re-ingest -> +0). Rudisha dict(execution, settlement, skipped)."""
    evs = events if events is not None else _read_results(bridge_dir)
    seen = {"execution": set(), "settlement": set()}
    src = (sink if sink is not None else repo.load(log_path))
    for r in src:
        k = r.get("kind")
        if k in seen:
            seen[k].add(r["obj"].get("id"))
    out = {"execution": 0, "settlement": 0, "skipped": 0}
    for e in evs:
        for kind, obj in _event_to_records(e):
            if obj["id"] in seen[kind]:
                out["skipped"] += 1; continue
            _append_repo(log_path, kind, obj, sink)
            seen[kind].add(obj["id"]); out[kind] += 1
    return out


# ==================== self-test (bila MT5 — faili bandia) ====================

def _synth(sig_hour=10, narrow=True, n=40):
    """Canonical-style arrays (PIP-SPACE). narrow -> bar ya mwisho = nyembamba zaidi ya 7 (nr7 fires).
    sig_hour = saa ya signal bar (entry = +1)."""
    rng = np.random.default_rng(7)
    c = np.cumsum(rng.normal(0, 2.0, n)) + 5000.0
    o = c.copy()
    wide = rng.uniform(8.0, 12.0, n)
    h = np.maximum(o, c) + wide
    l_ = np.minimum(o, c) - wide
    if narrow:
        o[-1] = c[-1]; h[-1] = c[-1] + 0.5; l_[-1] = c[-1] - 0.5   # range=1 pip < zote
    hour = np.array([(6 + k) % 24 for k in range(n)], int)
    hour[-1] = sig_hour
    ts = (np.datetime64("2026-08-03T00:00:00") + np.arange(n) * np.timedelta64(1, "h")).astype("datetime64[s]")
    return dict(o=o, h=h, l=l_, c=c, atr=np.full(n, 5.0), spr=np.full(n, 1.0),
                tc=np.full(n, 100.0), hour=hour, vol=np.array(["NORMAL"] * n), ts=ts)


def _loader_from(mapping):
    return lambda sym, tf, split, token=None: mapping.get(sym)


def self_test():
    ok = True
    import tempfile
    cfg = _ftmo_config()
    constraints = build_constraints(cfg)
    strat1 = STRATS["STRAT-001"]

    # (a) EDGE nr7 tail -> PLACE_OCO; levels/SL/TP/lots sahihi
    d = _synth(sig_hour=10, narrow=True)
    cmd, why = edge_decision("STRAT-001", strat1, d, cfg, constraints)
    pp = pip("USDCHF")
    exp_buy = round(float(d["h"][-1] + 0.1) * pp, 5)       # long_level = high+TICK(0.1), pip->price
    exp_sell = round(float(d["l"][-1] - 0.1) * pp, 5)
    a = 5.0
    edge_ok = (cmd is not None and cmd["action"] == "PLACE_OCO" and cmd["symbol"] == "USDCHF"
               and cmd["cmd_id"] == f"STRAT-001:USDCHF:{_as_of(d['ts'][-1])}"   # pair ndani (multi-pair)
               and abs(cmd["buy_stop"] - exp_buy) < 1e-9 and abs(cmd["sell_stop"] - exp_sell) < 1e-9
               and abs(cmd["sl_buy"] - round((d["h"][-1] + 0.1 - 2.0 * a) * pp, 5)) < 1e-9
               and abs(cmd["tp_buy"] - round((d["h"][-1] + 0.1 + 1.0 * a) * pp, 5)) < 1e-9
               and cmd["lots"] > 0 and cmd["magic"] == MAGIC["STRAT-001"]
               and cmd["expiry_utc"] == _as_of(d["ts"][-1]) + 7200)
    print(f"  [a] edge nr7 -> PLACE_OCO (levels/SL/TP/lots) -> {edge_ok}  ({why})")
    ok = ok and edge_ok

    # (b) no-LATE: entry hour = 17 (sig_hour=16) -> hakuna amri
    dl = _synth(sig_hour=16, narrow=True)
    cmdL, whyL = edge_decision("STRAT-001", strat1, dl, cfg, constraints)
    late_ok = (cmdL is None and "no-LATE" in whyL)
    print(f"  [b] no-LATE (entry hour 17) -> hakuna amri -> {late_ok}  ({whyL})")
    ok = ok and late_ok

    # (c) compliance-veto (budget=0) -> hakuna amri + sababu
    cfg0 = dict(cfg, daily_budget_start=0.0, win_factor=0.0)
    cmd0, why0 = edge_decision("STRAT-001", strat1, d, cfg0, build_constraints(cfg0))
    veto_ok = (cmd0 is None and "qty=0" in why0)
    print(f"  [c] compliance/size veto (budget=0) -> hakuna amri -> {veto_ok}  ({why0})")
    ok = ok and veto_ok

    with tempfile.TemporaryDirectory() as tmp:
        # (d) commands atomic + idempotent
        loader = _loader_from({"USDCHF": _synth(10, True), "USDJPY": _synth(11, True)})
        r1 = decide_all(tmp, cfg=cfg, loader=loader)
        seq1 = r1["seq"]
        cpath = Path(tmp) / "commands.json"
        atomic_ok = cpath.exists() and json.loads(cpath.read_text())["seq"] == seq1
        r2 = decide_all(tmp, cfg=cfg, loader=loader)       # data ile ile -> idempotent (seq haiongezeki)
        idem_ok = (json.loads(cpath.read_text())["seq"] == seq1 and len(r1["commands"]) >= 1
                   and len(r2["commands"]) == len(r1["commands"]))
        print(f"  [d] commands atomic + idempotent (seq={seq1} haiongezeki) -> {atomic_ok and idem_ok}")
        ok = ok and atomic_ok and idem_ok

        # (e) ingest FILLED + CLOSED -> repo-valid + idempotent (+0 re-ingest)
        c1 = r1["commands"][0]; oid = "ord-1"
        evs = [
            {"cmd_id": c1["cmd_id"], "event": "FILLED", "order_id": oid, "side": "BUY",
             "price": c1["buy_stop"], "qty": c1["lots"], "sl": c1["sl_buy"], "tp": c1["tp_buy"],
             "ts": c1["bar_ts"] + 3600},
            {"cmd_id": c1["cmd_id"], "event": "CLOSED", "order_id": oid, "pnl": 42.5,
             "pnl_r": 1.0, "exit_price": c1["tp_buy"], "ts": c1["bar_ts"] + 7200},
        ]
        sink = []
        ing1 = ingest_results(tmp, sink=sink, events=evs)
        from decision_repository import REQUIRED
        repo_ok = all(set(REQUIRED[r["kind"]]) <= set(r["obj"]) for r in sink)
        ing2 = ingest_results(tmp, sink=sink, events=evs)   # re-ingest -> +0
        ingest_ok = (ing1["execution"] == 1 and ing1["settlement"] == 1 and repo_ok
                     and ing2["execution"] == 0 and ing2["settlement"] == 0 and ing2["skipped"] == 2
                     and len(sink) == 2)
        # linkage: settlement.id == execution.order_id
        ex = [r["obj"] for r in sink if r["kind"] == "execution"][0]
        se = [r["obj"] for r in sink if r["kind"] == "settlement"][0]
        link_ok = (se["id"] == ex["order_id"] and se["parent_execution_id"] == ex["id"]
                   and ex["strategy"] == "STRAT-001" and ex["learned_ev"] == strat1["learned_ev"])
        print(f"  [e] ingest FILLED+CLOSED repo-valid + idempotent + linkage -> {ingest_ok and link_ok}")
        ok = ok and ingest_ok and link_ok

        # (f) determinism: edge_decision(d) -> command ile ile
        cmdA, _ = edge_decision("STRAT-001", strat1, d, cfg, constraints)
        cmdB, _ = edge_decision("STRAT-001", strat1, d, cfg, constraints)
        det_ok = (json.dumps(cmdA, sort_keys=True) == json.dumps(cmdB, sort_keys=True))
        print(f"  [f] determinism (edge command bit-identical) -> {det_ok}")
        ok = ok and det_ok

    # (g) MIUNDOMBINU (PD 2026-07-30): config nje ya code + state halisi + max-open + rejection log
    import tempfile, yaml as _yaml
    from live_engine import load_models, ConfigError, account_state_from_log
    with tempfile.TemporaryDirectory() as tmp:
        # g1: models.yaml — PD anahariri BILA code (pairs[], enabled, disabled inarukwa)
        y = Path(tmp) / "models.yaml"
        y.write_text(_yaml.safe_dump({"models": {
            "STRAT-001": dict(call_sign="KAIROS-1", enabled=True, pairs=["USDCHF", "USDCAD"],
                              sl_atr=2.0, tp_atr=1.0, learned_ev=1.92, magic=1),
            "KAIROS-9": dict(call_sign="KAIROS-9", enabled=False, pairs=["EURUSD"], sl_atr=1.0,
                             tp_atr=1.0, learned_ev=0.5, magic=9)}}), encoding="utf-8")
        mm = load_models(y)
        cfg_ok = (list(mm) == ["STRAT-001"] and mm["STRAT-001"]["pairs"] == ["USDCHF", "USDCAD"]
                  and mm["STRAT-001"]["pair"] == "USDCHF")
        # g2: validation fail-closed (sl_atr batili)
        bad = Path(tmp) / "bad.yaml"
        bad.write_text(_yaml.safe_dump({"models": {"X": dict(pairs=["EURUSD"], sl_atr=-1, tp_atr=1.0,
                                                             learned_ev=1.0, magic=1)}}), encoding="utf-8")
        try:
            load_models(bad); val_ok = False
        except ConfigError:
            val_ok = True
        # g3: state halisi kutoka log -> bajeti inapungua kwa hasara + open_slots/correlation
        recs = [{"kind": "execution", "obj": {"order_id": "o1", "status": "FILLED", "pair": "USDCHF"}},
                {"kind": "execution", "obj": {"order_id": "o2", "status": "FILLED", "pair": "USDJPY"}},
                {"kind": "settlement", "obj": {"id": "o1", "parent_execution_id": "o1",
                                               "as_of": 1790000000, "pnl": -60.0}}]
        stx = account_state_from_log(cfg=cfg, now_epoch=1790000000, records=recs)
        state_ok = (stx["open_slots"] == 1 and stx["daily_loss"] == 60.0
                    and stx["correlation_exposure"].get("USD_strength") == 1
                    and _budget(cfg, stx) == cfg["daily_budget_start"] - 60.0)
        # g4: MAX-OPEN batch reservation — max_slots=1, models 2 -> amri MOJA tu (nyingine REJECT)
        cfg1 = dict(cfg, max_slots=1, max_correlated_slots=9)
        two = {"M1": dict(pairs=["USDCHF"], sl_atr=2.0, tp_atr=1.0, learned_ev=1.9, magic=1),
               "M2": dict(pairs=["USDCHF"], sl_atr=1.0, tp_atr=1.0, learned_ev=2.6, magic=2)}
        logp = str(Path(tmp) / "log.jsonl")
        r4 = decide_all(str(Path(tmp) / "b4"), cfg=cfg1, loader=lambda p_, t_, s_: d,
                        models=two, log_path=logp, now_epoch=int(_as_of(d["ts"][-1])))
        slots_ok = len(r4["commands"]) == 1 and any("slots" in x["reason"] or "qty=0" in x["reason"]
                                                    or "gate" in x["reason"] for x in r4["rejects"])
        # g5: rejection + SABABU zimeandikwa kwenye log (decision REJECTED, repo-valid)
        rej = [r for r in repo.load(logp) if r["kind"] == "decision"
               and r["obj"].get("lifecycle") == "REJECTED"]
        rej_ok = bool(rej) and all({"id", "as_of", "lifecycle"} <= set(r["obj"]) and r["obj"]["reason"]
                                   for r in rej)
    infra_ok = cfg_ok and val_ok and state_ok and slots_ok and rej_ok
    print(f"  [g] miundombinu: models.yaml(pairs[]/disabled)={cfg_ok} validation-fail-closed={val_ok} "
          f"state-halisi(budget/slots/corr)={state_ok} max-open-reservation={slots_ok} "
          f"rejection+sababu-log={rej_ok} -> {infra_ok}")
    ok = ok and infra_ok

    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--bridge-dir", default=os.environ.get("ELITEFX_BRIDGE_DIR", BRIDGE_DEFAULT))
    ap.add_argument("--decide", action="store_true", help="edge decision -> commands.json")
    ap.add_argument("--ingest", action="store_true", help="results.json(l) -> paper_log")
    ap.add_argument("--cycle", action="store_true", help="ingest results + edge decide (cadence)")
    ap.add_argument("--cancel-all", action="store_true", help="kill-switch: CANCEL_ALL")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    bridge = a.bridge_dir
    if a.cancel_all:
        p = write_commands(bridge, [], cancel_all=True)
        print(f"CANCEL_ALL issued (seq={p['seq']}) -> {bridge}/commands.json")
        return 0
    did = False
    if a.ingest or a.cycle:
        ing = ingest_results(bridge)
        print(f"INGEST: execution={ing['execution']} settlement={ing['settlement']} skipped={ing['skipped']} "
              f"-> {LOG_F}")
        did = True
    if a.decide or a.cycle:
        res = decide_all(bridge)
        print(f"DECIDE (seq={res['seq']}): commands={len(res['commands'])} "
              f"-> {bridge}/commands.json")
        for name, why in res["reasons"].items():
            print(f"  {name}: {why}")
        did = True
    if not did:
        print("Tumia --cycle | --decide | --ingest | --cancel-all | --self-test.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
