"""
Ingest loaders — READ-ONLY mirror ya artifacts → DB (Doctrine V2 §4: kioo, si mkono).

KANUNI: artifact haipo → rudisha (0, "no data: <path>") — KAMWE kubuni namba. Idempotent:
natural keys + update_or_create (re-ingest haina duplicate). Loaders HAZIENDESHI code yoyote
ya src/research — zinasoma files tu (jsonl/md/json/parquet).
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from .models import (Alert, ComplianceCheck, DecisionTrace, LedgerEntry, Lesson, ModelVersion,
                     PairStrategyCell, Report, StrategyPerf, Trade, VpsHeartbeat)

# pair → strategy attribution (kutoka registry provenance; fallback UNKNOWN — haifanyi kubuni)
PAIR2STRAT = {"USDCHF": "STRAT-001", "USDJPY": "STRAT-002"}
STAGES = {"decision": "policy", "execution": "fill", "settlement": "settle"}


def _dt(ts):
    """epoch/ISO → aware datetime (UTC). Batili/garbage → None (F3: KAMWE si now())."""
    if ts is None:
        return None
    try:
        if isinstance(ts, (int, float)):
            return datetime.fromtimestamp(float(ts), tz=timezone.utc)
        return datetime.fromisoformat(str(ts).replace("Z", "+00:00")).astimezone(timezone.utc)
    except (ValueError, OSError, OverflowError):
        return None


def _read_jsonl(path):
    """F5: mstari mbovu wa JSON = SKIP (+hesabu) — loader haicrash (charter §NIDHAMU).
    Rudisha (rows, n_bad)."""
    rows, bad = [], 0
    with open(path, encoding="utf-8") as f:
        for ln in f:
            if not ln.strip():
                continue
            try:
                rows.append(json.loads(ln))
            except json.JSONDecodeError:
                bad += 1
    return rows, bad


def _bad_note(bad, path):
    return f"skipped {bad} bad json line(s): {path}" if bad else None


# ---------- 1) paper/live log → Trade + DecisionTrace + ComplianceCheck ----------

def load_paper_log(path, demo=False):
    path = Path(path)
    if not path.exists():
        return 0, f"no data: {path}"
    recs, bad = _read_jsonl(path)
    src = str(path)
    trades = {}
    pending_traces = []        # (order_id_or_None, seq, stage, record_id, payload)
    n = 0
    for seq, rec in enumerate(recs):
        kind = rec.get("kind", "")
        obj = rec.get("obj", rec)
        rid = str(obj.get("id", f"rec:{seq}"))
        if kind == "execution":
            oid = str(obj.get("order_id", rid))
            tr, _ = Trade.objects.update_or_create(
                trade_id=oid,
                defaults=dict(strategy=PAIR2STRAT.get(str(obj.get("pair", "")).upper(),
                                                      obj.get("strategy", "UNKNOWN")),
                              pair=str(obj.get("pair", "?")).upper(), side=obj.get("side", "?"),
                              qty=obj.get("qty"), entry=obj.get("entry"), sl=obj.get("sl"),
                              tp=obj.get("tp"), status="OPEN" if obj.get("status") == "FILLED"
                              else str(obj.get("status", "OPEN")),
                              opened_at=_dt(obj.get("as_of")), mode=obj.get("mode", "paper"),
                              source_ref=src, is_demo=demo))
            trades[rid] = tr; trades[oid] = tr
            pending_traces.append((tr, seq, "fill", rid, obj))
            n += 1
        elif kind == "settlement":
            key = str(obj.get("id", obj.get("exec_id", "")))
            tr = trades.get(key) or Trade.objects.filter(trade_id=key).first()
            if tr:
                # pnl_r inatoka kwenye artifact PEKEE (no fabrication — broker math si yetu)
                pnl = obj.get("realized_pnl")
                tr.pnl = pnl; tr.pnl_r = obj.get("pnl_r")
                tr.exit = obj.get("exit_price", tr.exit)
                tr.status = "CLOSED"; tr.closed_at = _dt(obj.get("as_of"))
                tr.save()
                pending_traces.append((tr, seq, "settle", rid, obj))
        elif kind == "decision":
            stage = "signal" if "aggregate" in obj else ("compliance" if "eligibility" in obj else "policy")
            pending_traces.append((None, seq, stage, rid, obj))
    # traces: decision records (kabla ya execution) huambatishwa na trade ya karibu inayofuata
    last_free = []
    for tr, seq, stage, rid, obj in pending_traces:
        if tr is None:
            last_free.append((seq, stage, rid, obj)); continue
        for (s2, st2, r2, o2) in last_free:
            DecisionTrace.objects.update_or_create(
                record_id=r2, stage=st2, seq=s2,
                defaults=dict(trade=tr, payload=o2, source_ref=src, is_demo=demo))
            if st2 == "compliance" and isinstance(o2.get("eligibility"), dict):
                elig = o2["eligibility"]
                for rule in list(elig.get("passed", [])):
                    ComplianceCheck.objects.update_or_create(
                        trade=tr, rule=str(rule),
                        defaults=dict(passed=True, detail="gate PASS", source_ref=src, is_demo=demo))
                for rule in list(elig.get("failed", [])):
                    ComplianceCheck.objects.update_or_create(
                        trade=tr, rule=str(rule),
                        defaults=dict(passed=False, detail="gate FAIL", source_ref=src, is_demo=demo))
        last_free = []
        DecisionTrace.objects.update_or_create(
            record_id=rid, stage=stage, seq=seq,
            defaults=dict(trade=tr, payload=obj, source_ref=src, is_demo=demo))
    return n, _bad_note(bad, path)


# ---------- 2) MODEL_REGISTRY.md → ModelVersion ----------

_ROW6 = re.compile(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|"
                   r"\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|\s*$")
_ROW5 = re.compile(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|"
                   r"\s*([^|]*?)\s*\|\s*$")
_EV = re.compile(r"EV\s*([+\-]?\d+(?:\.\d+)?)")
_N = re.compile(r"N\s*=\s*(\d+)")
_HEADERS = {"id", "----"}


def load_model_registry(path, demo=False):
    """F4: jedwali la kawaida (6 col: id|version|class|status|OOS|provenance) NA jedwali la WATCH
    (5 col: id|class|status|signal|njia) yote yana-parse. Header/separator rows zinarukwa."""
    path = Path(path)
    if not path.exists():
        return 0, f"no data: {path}"
    n = 0
    for ln in path.read_text(encoding="utf-8").splitlines():
        m6 = _ROW6.match(ln)
        if m6:
            mid, ver, klass, status, oos, prov = (x.strip().strip("*") for x in m6.groups())
        else:
            m5 = _ROW5.match(ln)
            if not m5:
                continue
            mid, klass, status, oos, prov = (x.strip().strip("*") for x in m5.groups())
            ver = "watch"                                  # WATCH table haina version column
        if mid.lower() in _HEADERS or set(mid) <= {"-"}:
            continue
        ev = _EV.search(oos); nn = _N.search(oos)
        ModelVersion.objects.update_or_create(
            model_id=mid, version=ver,
            defaults=dict(model_class=klass, status=status, oos_proof=oos, provenance=prov,
                          promised_ev=(float(ev.group(1)) if ev else None),
                          promised_n=(int(nn.group(1)) if nn else None),
                          source_ref=str(path), is_demo=demo))
        n += 1
    return n, None


# ---------- 3) EXPERIMENT_LEDGER.md → LedgerEntry ----------

def load_ledger(path, demo=False):
    path = Path(path)
    if not path.exists():
        return 0, f"no data: {path}"
    n = 0; cycle = "?"
    for ln in path.read_text(encoding="utf-8").splitlines():
        if ln.startswith("## "):
            cycle = ln[3:].split("(")[0].strip()
        cells = [c.strip() for c in ln.strip().strip("|").split("|")] if ln.strip().startswith("|") else []
        if len(cells) >= 4 and cells[0] not in ("ID", "") and not set(cells[0]) <= {"-"}:
            report = cells[-1] if ".md" in cells[-1] else ""
            verdict = cells[-2] if ".md" in cells[-1] else cells[-1]
            LedgerEntry.objects.update_or_create(
                cycle=cycle, exp_id=cells[0],
                defaults=dict(title=cells[1], verdict=verdict, report_path=report,
                              source_ref=str(path), is_demo=demo))
            n += 1
    return n, None


# ---------- 4) reports/*.md → Report ; 5) lessons → Lesson ----------

def load_steward(reports_dir):
    """DASHBOARD-V2: soma reports/model_steward.json (READ-ONLY; SI DB ingest — view inasoma live).
    Rudisha (data, note). Haipo/mbovu -> ({}, note) — FAIL-SOFT (scorecard inaonyesha 'no data')."""
    p = Path(reports_dir) / "model_steward.json"
    if not p.exists():
        return {}, f"no data: {p} (endesha src/research/model_steward.py kwanza)"
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return {}, f"invalid: {p} ({type(e).__name__})"
    return data, None


def load_reports(reports_dir, repo_root, demo=False):
    rd = Path(reports_dir)
    if not rd.exists():
        return 0, f"no data: {rd}"
    n = 0
    for p in sorted(list(rd.glob("*.md")) + list((rd / "archive").glob("*.md"))):
        title = p.stem
        try:
            for ln in p.read_text(encoding="utf-8").splitlines()[:5]:
                if ln.startswith("# "):
                    title = ln[2:].strip(); break
        except OSError:
            continue
        Report.objects.update_or_create(
            path=str(p.relative_to(repo_root)),
            defaults=dict(title=title[:290],
                          section="archive" if p.parent.name == "archive" else "reports",
                          source_ref=str(p), is_demo=demo))
        n += 1
    return n, None


def load_lessons(lessons_dir, demo=False):
    ld = Path(lessons_dir)
    if not ld.exists():
        return 0, f"no data: {ld}"
    n = 0
    for p in sorted(ld.glob("LESSON-*.md")):
        txt = p.read_text(encoding="utf-8", errors="replace")
        title = next((ln[2:].strip() for ln in txt.splitlines()[:5] if ln.startswith("# ")), p.stem)
        Lesson.objects.update_or_create(
            lesson_id=p.stem,
            defaults=dict(title=title[:290], body_md=txt[:20000], source_ref=str(p), is_demo=demo))
        n += 1
    return n, None


# ---------- 6) pair×strategy (rmap parquet AU jsonl fixture) ----------

def load_pair_strategy(parquet_path, jsonl_path, demo=False):
    jp = Path(jsonl_path)
    if jp.exists():
        n = 0
        rows, bad = _read_jsonl(jp)
        for r in rows:
            PairStrategyCell.objects.update_or_create(
                pair=r["pair"], strategy=r["strategy"],
                defaults=dict(n=r.get("n", 0), ev=r.get("ev"), win_rate=r.get("win_rate"),
                              context=r.get("context", {}), source_ref=str(jp), is_demo=demo))
            n += 1
        return n, _bad_note(bad, jp)
    pp = Path(parquet_path)
    if not pp.exists():
        return 0, f"no data: {pp} / {jp}"
    try:
        import polars as pl
    except ImportError:
        return 0, f"no data: polars haipo (parquet {pp} haisomeki bila yake)"
    df = pl.read_parquet(pp)
    agg = (df.group_by(["event", "pair"])
             .agg([(pl.col("ev_net") * pl.col("n")).sum().alias("s"),
                   pl.col("n").sum().alias("nn"),
                   (pl.col("win") * pl.col("n")).sum().alias("w")]))
    n = 0
    for r in agg.iter_rows(named=True):
        if not r["nn"]:
            continue
        PairStrategyCell.objects.update_or_create(
            pair=r["pair"], strategy=r["event"],
            defaults=dict(n=int(r["nn"]), ev=round(r["s"] / r["nn"], 4),
                          win_rate=round(r["w"] / r["nn"], 4),
                          context={"source": "rmap_train.parquet (TRAIN atlas)"},
                          source_ref=str(pp), is_demo=demo))
        n += 1
    return n, None


# ---------- 7) alerts.jsonl → Alert ; 8) heartbeat.json → VpsHeartbeat ----------

def load_alerts(path, demo=False):
    """F3: ts batili/inakosekana -> ts=None + message tagged '[invalid/missing ts]' — HAKUNA now()."""
    path = Path(path)
    if not path.exists():
        return 0, f"no data: {path}"
    n = 0; invalid_ts = 0
    rows, bad = _read_jsonl(path)
    for r in rows:
        key = r.get("dedupe_key") or f"{r.get('kind','?')}:{r.get('ts','?')}"
        ts = _dt(r.get("ts"))
        msg = r.get("message", "")
        if ts is None:
            invalid_ts += 1
            msg = "[invalid/missing ts] " + msg           # stale/invalid — inaonekana WAZI
        Alert.objects.update_or_create(
            dedupe_key=key,
            defaults=dict(ts=ts, severity=r.get("severity", "INFO"), kind=r.get("kind", "?"),
                          message=msg[:390], source_ref=str(path), is_demo=demo))
        n += 1
    notes = [x for x in (_bad_note(bad, path),
                         (f"{invalid_ts} alert(s) zenye ts batili (null, si now())" if invalid_ts else None)) if x]
    return n, ("; ".join(notes) or None)


def load_heartbeat(path, demo=False):
    """F3: ts batili -> ts=None (status HAITAKUWA OPERATIONAL). F5: JSON mbovu -> (0, note), si crash."""
    path = Path(path)
    if not path.exists():
        return 0, f"no data: {path}"
    try:
        r = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return 0, f"invalid json (skipped, no crash): {path}"
    ts = _dt(r.get("ts"))                                  # None kama batili — HAKUNA now()
    VpsHeartbeat.objects.update_or_create(
        ts=ts,
        defaults=dict(uptime_s=r.get("uptime_s"), latency_ms=r.get("latency_ms"),
                      clock_drift_ms=r.get("clock_drift_ms"), disk_free_pct=r.get("disk_free_pct"),
                      mem_free_pct=r.get("mem_free_pct"), feed_freshness=r.get("feed_freshness", {}),
                      source_ref=str(path), is_demo=demo))
    return 1, ("stale/invalid ts (null — status si OPERATIONAL)" if ts is None else None)


# ---------- 9) StrategyPerf — derived kutoka Trades zilizo-ingest (artifact-based) ----------

def rebuild_strategy_perf(demo=False):
    """F2: R-metrics kutoka `pnl_r` PEKEE — trade isiyo na pnl_r HAICHANGII net_r/expectancy_r
    (HAKUNA kuchanganya currency na R; unit-mix = namba yenye semantiki batili). Trades za currency-
    only zinahesabiwa kando (note) — curve ya currency ni tofauti, si sehemu ya R-perf."""
    from collections import defaultdict
    all_closed = list(Trade.objects.filter(status="CLOSED").exclude(pnl__isnull=True))
    trades = [t for t in all_closed if t.pnl_r is not None]
    n_no_r = len(all_closed) - len(trades)
    if not trades:
        return 0, ("no data: hakuna closed trades" if not all_closed
                   else f"no data: closed {len(all_closed)} zote hazina pnl_r (R n/a — hakuna unit-mix)")
    buckets = defaultdict(list)
    for t in trades:
        r = t.pnl_r
        period = t.closed_at.strftime("%Y-%m") if t.closed_at else "?"
        buckets[(t.strategy, period, t.mode)].append(r)
        buckets[(t.strategy, "ALL", t.mode)].append(r)
        buckets[("PORTFOLIO", period, t.mode)].append(r)
        buckets[("PORTFOLIO", "ALL", t.mode)].append(r)
    n = 0
    for (strat, period, mode), rs in buckets.items():
        wins = [x for x in rs if x > 0]; losses = [x for x in rs if x <= 0]
        pf = (sum(wins) / abs(sum(losses))) if losses and sum(losses) != 0 else None
        eq = 0.0; peak = 0.0; dd = 0.0
        for x in rs:
            eq += x; peak = max(peak, eq); dd = max(dd, peak - eq)
        StrategyPerf.objects.update_or_create(
            strategy=strat, period=period, mode=mode,
            defaults=dict(n_trades=len(rs), net_r=round(sum(rs), 4),
                          win_rate=round(len(wins) / len(rs), 4),
                          expectancy_r=round(sum(rs) / len(rs), 4),
                          profit_factor=(round(pf, 3) if pf is not None else None),
                          max_dd_r=round(dd, 4),
                          source_ref="derived: Trade mirror (ingest; pnl_r only — F2)", is_demo=demo))
        n += 1
    return n, (f"{n_no_r} closed trade(s) bila pnl_r zimeachwa nje ya R-metrics (F2)" if n_no_r else None)
