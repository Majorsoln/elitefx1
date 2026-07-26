"""
forward_cycle.py — FORWARD TRACK orchestrator (docs/FORWARD_TRACK_CHARTER.md ROLLOUT).

Cadence nzima ya forward kwa amri MOJA + log ya kila run — kwa SOAK-test (Faza 1: PC demo, siku 2-3,
inapima UIMARA WA BOMBA) na VPS (Faza 3: 24/7). Paper/READ-ONLY — HAITENGENEZI trade logic; inaita TU
CLIs zilizopo kwa subprocess (mt5_data / live_engine / model_steward / dashboard ingest).

Hatua 4 kwa mpangilio:
  (1) mt5_data.py --out <store>            (READ-ONLY MT5 -> forward store <SYMBOL>.npz)
  (2) live_engine.py --forward --data <store>  (F1 append-only, bars mpya TU)
  (3) model_steward.py                     (forward practical-vs-learned -> reports/model_steward.json)
  (4) dashboard/manage.py ingest           (bila --demo -> scorecard inasasishwa)

FAIL-SOFT + fail-fast: hatua ikishindwa -> status=FAIL, zilizobaki SKIPPED, exit-code != 0
(--continue-on-error kuendelea). mt5_data ikishindwa (MT5 down) -> zilizobaki skipped kwa default.
LOG: append data/forward/cycle_log.jsonl. ENV ya MT5 (ELITEFX_MT5_*) inarithiwa na subprocess.

Endesha:  python forward_cycle.py [--store data/forward] [--skip-dashboard] [--continue-on-error]
Self-test: python forward_cycle.py --self-test   (bila MT5/Django — stub subprocess)
Task Scheduler/cron-ready (exit-code != 0 = cycle imeshindwa).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SR = REPO_ROOT / "src" / "research"
DASH = REPO_ROOT / "dashboard"
STORE_DEFAULT = REPO_ROOT / "data" / "forward"
CYCLE_LOG = REPO_ROOT / "data" / "forward" / "cycle_log.jsonl"

STEP_ORDER = ("mt5_data", "live_engine", "model_steward", "dashboard_ingest")
_LE_SUMMARY = re.compile(r"candidates_new=(\d+)\s+FILLED=(\d+)\s+REJECTED=(\d+)")


def _steps(store, skip_dashboard):
    """(name, argv, cwd) kwa hatua 4 — REUSE CLIs zilizopo (sys.executable). store = absolute."""
    steps = [
        ("mt5_data", [sys.executable, "mt5_data.py", "--out", str(store)], SR),
        ("live_engine", [sys.executable, "live_engine.py", "--forward", "--data", str(store)], SR),
        ("model_steward", [sys.executable, "model_steward.py"], SR),
    ]
    if not skip_dashboard:
        steps.append(("dashboard_ingest", [sys.executable, "manage.py", "ingest"], DASH))
    return steps


def _run_step(name, argv, cwd):
    """Subprocess moja (ENV inarithiwa — pamoja na ELITEFX_MT5_*). Rudisha dict ya matokeo."""
    t0 = time.time()
    try:
        p = subprocess.run(argv, cwd=str(cwd), capture_output=True, encoding="utf-8", errors="replace")
        status = "OK" if p.returncode == 0 else "FAIL"
        return dict(status=status, returncode=p.returncode, duration_s=round(time.time() - t0, 3),
                    stdout=p.stdout or "", stderr=p.stderr or "")
    except Exception as e:                                # binary haipo / cwd batili n.k. -> FAIL (fail-soft)
        return dict(status="FAIL", returncode=None, duration_s=round(time.time() - t0, 3),
                    stdout="", stderr=f"{type(e).__name__}: {e}")


def _summary_of(name, stdout):
    """Toa candidates_new/filled/rejected kutoka stdout ya live_engine (kama inapatikana)."""
    if name == "live_engine":
        m = _LE_SUMMARY.search(stdout or "")
        if m:
            return dict(candidates_new=int(m.group(1)), filled=int(m.group(2)),
                        rejected=int(m.group(3)))
    return {}


def _tail(text, n=15):
    lines = [l for l in (text or "").splitlines() if l.strip()]
    return "\n".join(lines[-n:])


def _log(log_path, entry):
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")


def run_cycle(store=STORE_DEFAULT, skip_dashboard=False, continue_on_error=False,
              log_path=CYCLE_LOG, _runner=None):
    """Endesha hatua 4 kwa mpangilio; append kila moja kwenye cycle_log.jsonl. _runner = injection (test).
    Rudisha dict(ok, fail, skipped, results, exit_code)."""
    runner = _runner or _run_step
    results, skipped = [], []
    n_ok = n_fail = 0
    stop = False
    run_ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for name, argv, cwd in _steps(store, skip_dashboard):
        if stop:                                         # fail-fast: hatua zilizobaki = SKIPPED
            skipped.append(name)
            entry = dict(ts=run_ts, step=name, status="SKIPPED", returncode=None,
                         duration_s=0.0, summary={}, error_tail="")
            _log(log_path, entry); results.append(entry)
            continue
        rec = runner(name, argv, cwd)
        entry = dict(ts=run_ts, step=name, status=rec["status"], returncode=rec["returncode"],
                     duration_s=rec["duration_s"], summary=_summary_of(name, rec.get("stdout", "")),
                     error_tail=(_tail(rec.get("stderr", "")) if rec["status"] == "FAIL" else ""))
        _log(log_path, entry); results.append(entry)
        if rec["status"] == "OK":
            n_ok += 1
        else:
            n_fail += 1
            if not continue_on_error:
                stop = True                              # skip zilizobaki (mt5 down -> usiendelee)
    exit_code = 0 if n_fail == 0 else 1
    return dict(ok=n_ok, fail=n_fail, skipped=skipped, results=results, exit_code=exit_code)


def _print_summary(res, log_path):
    le = next((e for e in res["results"] if e["step"] == "live_engine"
               and e["status"] == "OK" and e["summary"]), None)
    cand = le["summary"].get("candidates_new") if le else "?"
    filled = le["summary"].get("filled") if le else "?"
    print(f"FORWARD CYCLE: {res['ok']} OK, {res['fail']} FAIL"
          + (f", {len(res['skipped'])} SKIPPED ({', '.join(res['skipped'])})" if res["skipped"] else "")
          + f" | candidates_new={cand} filled={filled}")
    for e in res["results"]:
        mark = {"OK": "OK ", "FAIL": "FAIL", "SKIPPED": "SKIP"}[e["status"]]
        print(f"  [{mark}] {e['step']} ({e['duration_s']}s)"
              + (f" rc={e['returncode']}" if e["status"] == "FAIL" else ""))
        if e["status"] == "FAIL" and e["error_tail"]:
            print("     " + e["error_tail"].replace("\n", "\n     "))
    print(f"  log: {log_path} (append-only JSONL)")


# ---------- self-test (bila MT5/Django — stub subprocess) ----------

def self_test():
    ok = True
    import tempfile

    def mk_runner(fail_set, calls):
        """Stub ya _run_step: rekodi order; status kwa jina (fail_set); live_engine ana summary."""
        def _r(name, argv, cwd):
            calls.append(name)
            failed = name in fail_set
            out = "FORWARD-APPEND (start=2026-07-24): candidates_new=7 FILLED=2 REJECTED=5 cum_pnl=$3.0" \
                if name == "live_engine" else ""
            return dict(status=("FAIL" if failed else "OK"), returncode=(2 if failed else 0),
                        duration_s=0.01, stdout=out, stderr=("boom traceback" if failed else ""))
        return _r

    tmp = Path(tempfile.mkdtemp())
    store = tmp / "store"

    # (a) ORDER: hatua 4 kwa mpangilio sahihi; live_engine summary imetolewa
    calls, log_a = [], tmp / "a.jsonl"
    ra = run_cycle(store=store, log_path=log_a, _runner=mk_runner(set(), calls))
    le = [e for e in ra["results"] if e["step"] == "live_engine"][0]
    order_ok = (calls == list(STEP_ORDER) and ra["exit_code"] == 0 and ra["fail"] == 0
                and ra["ok"] == 4 and le["summary"].get("candidates_new") == 7
                and le["summary"].get("filled") == 2)
    print(f"  [a] order hatua 4 + live_engine summary(candidates_new=7) -> {order_ok}")
    ok = ok and order_ok

    # (b) FAIL-SOFT: model_steward FAIL -> cycle FAIL + exit!=0 + dashboard SKIPPED (haikuitwa)
    calls, log_b = [], tmp / "b.jsonl"
    rb = run_cycle(store=store, log_path=log_b, _runner=mk_runner({"model_steward"}, calls))
    failsoft_ok = (rb["exit_code"] != 0 and rb["fail"] == 1
                   and rb["skipped"] == ["dashboard_ingest"]
                   and calls == ["mt5_data", "live_engine", "model_steward"])  # dashboard HAIKUITWA
    print(f"  [b] fail-soft: model_steward FAIL -> exit!=0, dashboard SKIPPED, haikuitwa -> {failsoft_ok}")
    ok = ok and failsoft_ok

    # (c) cycle_log.jsonl APPEND: mistari = hatua; schema kamili; run tena -> inaongezeka
    lines = [json.loads(l) for l in open(log_a, encoding="utf-8") if l.strip()]
    need = {"ts", "step", "status", "returncode", "duration_s", "summary", "error_tail"}
    log_ok = len(lines) == 4 and all(need <= set(x) for x in lines)
    run_cycle(store=store, log_path=log_a, _runner=mk_runner(set(), []))     # append tena
    lines2 = [l for l in open(log_a, encoding="utf-8") if l.strip()]
    log_ok = log_ok and len(lines2) == 8
    print(f"  [c] cycle_log.jsonl append (4 -> 8) + schema kamili -> {log_ok}")
    ok = ok and log_ok

    # (d) MT5-FAIL: mt5_data FAIL -> hatua ZOTE zilizobaki SKIPPED (bomba limesimama salama)
    calls, log_d = [], tmp / "d.jsonl"
    rd = run_cycle(store=store, log_path=log_d, _runner=mk_runner({"mt5_data"}, calls))
    mt5_ok = (calls == ["mt5_data"]
              and set(rd["skipped"]) == {"live_engine", "model_steward", "dashboard_ingest"}
              and rd["exit_code"] != 0 and rd["ok"] == 0)
    print(f"  [d] mt5-fail -> zilizobaki ZOTE skipped -> {mt5_ok}")
    ok = ok and mt5_ok

    # (e) --continue-on-error: FAIL -> endelea (hakuna skip); + --skip-dashboard = hatua 3
    calls, log_e = [], tmp / "e.jsonl"
    re_ = run_cycle(store=store, log_path=log_e, continue_on_error=True,
                    _runner=mk_runner({"model_steward"}, calls))
    calls2, log_e2 = [], tmp / "e2.jsonl"
    rs = run_cycle(store=store, log_path=log_e2, skip_dashboard=True, _runner=mk_runner(set(), calls2))
    cont_ok = (re_["skipped"] == [] and calls == list(STEP_ORDER) and re_["fail"] == 1
               and re_["exit_code"] != 0
               and calls2 == ["mt5_data", "live_engine", "model_steward"] and rs["ok"] == 3)
    print(f"  [e] --continue-on-error (hakuna skip) + --skip-dashboard (hatua 3) -> {cont_ok}")
    ok = ok and cont_ok

    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--store", default=None, help="forward store dir (default data/forward)")
    ap.add_argument("--skip-dashboard", action="store_true", help="ruka hatua ya dashboard ingest")
    ap.add_argument("--continue-on-error", action="store_true", help="endelea hata hatua ikishindwa")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    store = (Path(a.store) if a.store else STORE_DEFAULT).resolve()
    res = run_cycle(store=store, skip_dashboard=a.skip_dashboard,
                    continue_on_error=a.continue_on_error)
    _print_summary(res, CYCLE_LOG)
    return res["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
