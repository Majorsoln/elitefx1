"""
Panels 9 za GLASS BOX — READ-ONLY views (GET pekee; @require_GET kila moja).
HAKUNA endpoint inayoanzisha/kubadilisha trade (V2 §4 — kioo, si mkono). "no data" wazi
badala ya kubuni. Kila panel ina source-refs (glass-box).
"""
import json
from pathlib import Path

from django.conf import settings
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone as djtz
from django.views.decorators.http import require_GET

from . import attest
from django.contrib.auth.decorators import login_required
from .access import audit, lessee_can_see, model_access, panel_access, user_leases, _groups
from .models import (Alert, AuditEvent, ComplianceCheck, DecisionTrace, LedgerEntry, Lesson,
                     ModelVersion, PairStrategyCell, Report, StrategyPerf, Trade, VpsHeartbeat)

STALE_S = 15 * 60          # heartbeat > 15min = DEGRADED; hakuna heartbeat = OFFLINE/no-data


def _compliance_score():
    n = ComplianceCheck.objects.count()
    if not n:
        return None, 0, 0
    fails = ComplianceCheck.objects.filter(passed=False).count()
    return round(100 * (1 - fails / n), 2), n, fails


def _system_status():
    """F3: heartbeat yenye ts=None (batili kwenye artifact) HAIWEZI kuwa OPERATIONAL — freshness
    haithibitiki. Ordering -ts (sqlite: nulls mwisho) -> heartbeat halali ya karibuni inatangulia."""
    hb = VpsHeartbeat.objects.first()
    if hb is None:
        return "NO DATA", None
    if hb.ts is None:
        return "DEGRADED", hb                    # invalid ts — si OPERATIONAL (no-fabrication)
    age = (djtz.now() - hb.ts).total_seconds()
    return ("OPERATIONAL" if age < STALE_S else "DEGRADED"), hb


def _equity_series(mode=None):
    """F2: R-equity kutoka `pnl_r` PEKEE — trade za currency-only HAZIINGII curve ya R
    (hakuna unit-mix). Curve inabaki na label 'R'."""
    qs = Trade.objects.filter(status="CLOSED", pnl_r__isnull=False).order_by("closed_at")
    if mode:
        qs = qs.filter(mode=mode)
    eq, series, labels = 0.0, [], []
    for t in qs:
        eq += t.pnl_r or 0
        series.append(round(eq, 4))
        labels.append(t.closed_at.strftime("%Y-%m-%d") if t.closed_at else "?")
    return labels, series


@require_GET
@panel_access("deck")
def command_deck(request):
    status, hb = _system_status()
    score, n_checks, n_fails = _compliance_score()
    labels, eq = _equity_series()
    perf_all = StrategyPerf.objects.filter(strategy="PORTFOLIO", period="ALL").first()
    month = djtz.now().strftime("%Y-%m")
    perf_month = StrategyPerf.objects.filter(strategy="PORTFOLIO", period=month).first()
    # DASHBOARD-V2 Awamu 2: FLEET rollup — REUSE _scorecard_summary (Awamu 1). Fail-soft steward.
    from .callsigns import CALLSIGNS
    smodels, _prov, steward_note = _steward_models()
    ids = sorted(set(CALLSIGNS) | set(smodels) | set(Trade.objects.values_list("strategy", flat=True)))
    fleet = [_scorecard_summary(i, smodels) for i in ids if i in CALLSIGNS or i in smodels]
    tally = {"green": 0, "yellow": 0, "red": 0}
    for c in fleet:
        tally[c["color"]] = tally.get(c["color"], 0) + 1
    return render(request, "monitor/deck.html", dict(
        panel="deck", status=status, hb=hb,
        score=score, n_checks=n_checks, n_fails=n_fails,
        open_positions=Trade.objects.filter(status="OPEN").count(),
        active_models=ModelVersion.objects.filter(status__icontains="PROVEN").count()
        + ModelVersion.objects.filter(status__icontains="LIVE").count(),
        perf_all=perf_all, perf_month=perf_month,
        equity_json=json.dumps(dict(labels=labels[-120:], values=eq[-120:])),
        today_actions=Trade.objects.all()[:8],
        fleet=fleet, fleet_tally=tally, steward_note=steward_note,
        alerts_count=Alert.objects.count(), alerts_recent=Alert.objects.all()[:5],
        demo=Trade.objects.filter(is_demo=True).exists()))


@require_GET
@panel_access("portfolio")
def portfolio(request):
    mode = request.GET.get("mode")           # paper/live toggle (query param, read-only)
    labels, eq = _equity_series(mode if mode in ("paper", "live") else None)
    strats = sorted({p.strategy for p in StrategyPerf.objects.all()})
    rows = {s: list(StrategyPerf.objects.filter(strategy=s).exclude(period="ALL").order_by("period"))
            for s in strats}
    all_rows = {s: StrategyPerf.objects.filter(strategy=s, period="ALL").first() for s in strats}
    # monthly heatmap: mwaka × mwezi (net_r ya PORTFOLIO) — precomputed rows (template-friendly)
    heat = {}
    for p in StrategyPerf.objects.filter(strategy="PORTFOLIO").exclude(period="ALL"):
        if "-" in p.period:
            y, m = p.period.split("-")
            heat.setdefault(y, {})[int(m)] = p.net_r
    heat_rows = [(y, [heat[y].get(m) for m in range(1, 13)]) for y in sorted(heat)]
    return render(request, "monitor/portfolio.html", dict(
        panel="portfolio", mode=mode or "all",
        equity_json=json.dumps(dict(labels=labels, values=eq)),
        strat_all=all_rows, strat_monthly=rows, heat_rows=heat_rows,
        months=range(1, 13)))


@require_GET
@panel_access("actions")
def live_actions(request):
    trades = Trade.objects.prefetch_related("traces", "checks")[:100]
    return render(request, "monitor/actions.html", dict(panel="actions", trades=trades))


@require_GET
@panel_access("compliance")
def compliance(request):
    score, n_checks, n_fails = _compliance_score()
    by_rule = {}
    for c in ComplianceCheck.objects.all():
        d = by_rule.setdefault(c.rule, dict(n=0, fails=0, pass_pct=0))
        d["n"] += 1; d["fails"] += (0 if c.passed else 1)
    for d in by_rule.values():
        d["pass_pct"] = round(100 * (d["n"] - d["fails"]) / d["n"]) if d["n"] else 0
    violations = ComplianceCheck.objects.filter(passed=False).select_related("trade")
    return render(request, "monitor/compliance.html", dict(
        panel="compliance", score=score, n_checks=n_checks, n_fails=n_fails,
        by_rule=sorted(by_rule.items()), violations=violations,
        trades_with_checks=Trade.objects.prefetch_related("checks")[:50]))


@require_GET
@panel_access("registry")
def registry(request):
    models = ModelVersion.objects.order_by("model_id", "version")
    return render(request, "monitor/registry.html", dict(panel="registry", models=models))


@require_GET
@model_access
def registry_detail(request, model_id):
    versions = list(ModelVersion.objects.filter(model_id=model_id).order_by("version"))
    if not versions:
        raise Http404(f"model '{model_id}' haipo kwenye registry mirror")
    mv = versions[-1]
    perf = StrategyPerf.objects.filter(strategy=model_id, period="ALL").first()
    monthly = StrategyPerf.objects.filter(strategy=model_id).exclude(period="ALL").order_by("period")
    # LIVE-vs-PROMISED: live expectancy dhidi ya promised EV + shrinkage band
    live_pts = [dict(period=p.period, ev=p.expectancy_r) for p in monthly]
    overlay = dict(promised=mv.promised_ev,
                   band_lo=(mv.promised_ev * mv.shrinkage_lo if mv.promised_ev is not None else None),
                   band_hi=(mv.promised_ev * mv.shrinkage_hi if mv.promised_ev is not None else None),
                   live=live_pts)
    degraded = bool(perf and mv.promised_ev is not None and overlay["band_lo"] is not None
                    and perf.expectancy_r is not None and perf.expectancy_r < min(0, overlay["band_lo"]))
    return render(request, "monitor/registry_detail.html", dict(
        panel="registry", mv=mv, versions=versions, perf=perf, monthly=monthly,
        overlay_json=json.dumps(overlay), degraded=degraded,
        lifecycle=["CANDIDATE", "PROVEN", "LIVE", "RETIRED"]))


@require_GET
@model_access
def attestation_json(request, model_id):
    res = attest.attestation(model_id)
    if res is None:
        raise Http404("no data: model haipo")
    data, _ = res
    audit(request, "export_attestation_json", model_id)
    return JsonResponse(data, json_dumps_params={"indent": 2, "sort_keys": True})


@require_GET
@model_access
def attestation_html(request, model_id):
    res = attest.attestation(model_id)
    if res is None:
        raise Http404("no data: model haipo")
    data, _ = res
    audit(request, "view_attestation", model_id)
    return render(request, "monitor/attestation.html", dict(
        panel="registry", model_id=model_id, data=data,
        pretty=json.dumps(data, indent=2, sort_keys=True)))


@require_GET
@model_access
def attestation_pdf(request, model_id):
    res = attest.attestation(model_id)
    if res is None:
        raise Http404("no data: model haipo")
    data, _ = res
    pdf = attest.render_pdf(data)
    audit(request, "export_attestation_pdf", model_id)
    if pdf is None:                       # reportlab haipo — HTML fallback (hiari kwa spec)
        return render(request, "monitor/attestation.html", dict(
            panel="registry", model_id=model_id, data=data,
            pretty=json.dumps(data, indent=2, sort_keys=True), pdf_missing=True))
    resp = HttpResponse(pdf, content_type="application/pdf")
    resp["Content-Disposition"] = f'attachment; filename="attestation_{model_id}.pdf"'
    return resp


@require_GET
@panel_access("matrix")
def matrix(request):
    cells = list(PairStrategyCell.objects.all())
    pairs = sorted({c.pair for c in cells})
    strats = sorted({c.strategy for c in cells})
    grid = {(c.pair, c.strategy): c for c in cells}
    rows = [(p, [grid.get((p, s)) for s in strats]) for p in pairs]
    return render(request, "monitor/matrix.html", dict(panel="matrix", strats=strats, rows=rows))


@require_GET
@panel_access("matrix")
def matrix_cell(request, pair, strategy):
    cell = PairStrategyCell.objects.filter(pair=pair, strategy=strategy).first()
    if cell is None:
        raise Http404("no data: cell haipo")
    lessons = Lesson.objects.all()[:50]
    return render(request, "monitor/matrix_cell.html", dict(
        panel="matrix", cell=cell, lessons=lessons))


@require_GET
@panel_access("alerts")
def alerts(request):
    return render(request, "monitor/alerts.html", dict(panel="alerts", alerts=Alert.objects.all()[:200]))


@require_GET
@panel_access("vps")
def vps(request):
    status, hb = _system_status()
    return render(request, "monitor/vps.html", dict(
        panel="vps", status=status, hb=hb, history=VpsHeartbeat.objects.all()[:50]))


@require_GET
@panel_access("ledger")
def ledger(request):
    cycles = {}
    for e in LedgerEntry.objects.order_by("cycle", "exp_id"):
        cycles.setdefault(e.cycle, []).append(e)
    return render(request, "monitor/ledger.html", dict(
        panel="ledger", cycles=sorted(cycles.items()), lessons=Lesson.objects.order_by("lesson_id"),
        reports=Report.objects.order_by("section", "path")))


@require_GET
@panel_access("ledger")
def report_view(request, path):
    # usalama: files chini ya REPO_ROOT/reports PEKEE (hakuna traversal)
    rel = Path(path)
    base = (settings.REPO_ROOT / "reports").resolve()
    target = (settings.REPO_ROOT / rel).resolve()
    if not str(target).startswith(str(base)) or not target.suffix == ".md":
        raise Http404("path si ya reports/")
    if not target.exists():
        # demo fixtures fallback (fixtures/reports/<name> — rel inaanza na 'reports/')
        fx = (Path(__file__).resolve().parent / "fixtures" / rel)
        if fx.exists():
            target = fx
        else:
            raise Http404(f"no data: {rel}")
    return render(request, "monitor/report_view.html", dict(
        panel="ledger", relpath=str(rel), body=target.read_text(encoding="utf-8", errors="replace")))


@require_GET
@panel_access("audit")
def audit_trail(request):
    return render(request, "monitor/audit.html", dict(panel="audit", events=AuditEvent.objects.all()[:300]))


@require_GET
def lessee_home(request):
    """Landing ya lessee: leases zake + attestation links (read-only). Internal/attestor → deck."""
    if not request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect(settings.LOGIN_URL)
    if _groups(request.user) & {"internal"}:
        return command_deck(request)
    if _groups(request.user) & {"attestor"}:
        return registry(request)
    return lessee_list(request)          # DASHBOARD-V2 Awamu 3: anonymized /my/ (SI lessee.html ya zamani)


# ==================== DASHBOARD-V2 AWAMU 1 — MODEL SCORECARD (INTERNAL) ====================
from . import loaders, language
from .callsigns import CALLSIGNS, to_internal, to_public, public_meta


def _steward_models():
    """(models_dict, note) kutoka reports/model_steward.json (fail-soft)."""
    data, note = loaders.load_steward(settings.ELITEFX_PATHS["reports_dir"])
    return (data.get("models", {}) if data else {}), (data.get("provenance", {}) if data else {}), note


def _status_light(verdict, n_closed):
    """HOLDS/LIFTS -> green; SHRINKS -> red; INSUFFICIENT/no-data -> yellow."""
    if not verdict or n_closed == 0:
        return "yellow", "NO-DATA"
    if verdict in ("HOLDS", "LIFTS"):
        return "green", verdict
    if verdict == "SHRINKS":
        return "red", verdict
    return "yellow", verdict          # INSUFFICIENT / UNKNOWN-LEARNED


def _scorecard_summary(internal_id, smodels):
    """Muhtasari mfupi (kwa list) — call-sign, light, sentensi. Chanzo: steward + Trade mirror."""
    call = to_public(internal_id)
    sm = smodels.get(internal_id, {})
    overall = sm.get("overall", {}) if sm else {}
    n_closed = Trade.objects.filter(strategy=internal_id, status="CLOSED").count()
    color, disp = _status_light(overall.get("verdict"), n_closed)
    return dict(call=call, internal=internal_id, meta=public_meta(call), color=color, display=disp,
                verdict=overall.get("verdict"), practical=overall.get("mean"),
                learned=sm.get("learned_ev"), n_closed=n_closed,
                sentence=language.say("status", call=call, verdict=(disp if disp != "NO-DATA" else "NO-DATA")))


# ---------- DASHBOARD-V2 Awamu 4 (R5): FILTER CHIPS ya section D (server-side, GET-only) ----------
_SESSIONS = ("ASIA", "LONDON", "NY")


def _session_of(dt):
    """UTC hour -> FX session label (ASIA/LONDON/NY/OFF). Mipaka inaakisi research session_of."""
    if dt is None:
        return None
    h = dt.hour
    return "ASIA" if 0 <= h < 7 else "LONDON" if 7 <= h < 13 else "NY" if 13 <= h < 20 else "OFF"


def _filter_closed(closed, request, allow_pair):
    """Chuja closed-trade list kwa GET params (READ-ONLY): result=W|L · session=ASIA|LONDON|NY ·
    from/to=YYYY-MM-DD · pair=<pair> (INTERNAL TU — lessee HANA, §9). Rudi (filtered, total, active)."""
    total = len(closed)
    result = request.GET.get("result")
    session = request.GET.get("session")
    dfrom = (request.GET.get("from") or "").strip()
    dto = (request.GET.get("to") or "").strip()
    pair = (request.GET.get("pair") or "").strip() if allow_pair else ""
    out = closed
    if result in ("W", "L"):
        out = [t for t in out if ("W" if (t.pnl_r or 0) > 0 else "L") == result]
    if session in _SESSIONS:
        out = [t for t in out if _session_of(t.opened_at) == session]
    if dfrom:
        out = [t for t in out if t.closed_at and t.closed_at.strftime("%Y-%m-%d") >= dfrom]
    if dto:
        out = [t for t in out if t.closed_at and t.closed_at.strftime("%Y-%m-%d") <= dto]
    if pair:
        out = [t for t in out if t.pair == pair]
    active = {"result": result if result in ("W", "L") else None,
              "session": session if session in _SESSIONS else None,
              "from": dfrom or None, "to": dto or None, "pair": pair or None}
    return out, total, active


def _chip_qs(active, key, value):
    """Toggle chip -> querystring ikihifadhi filters zingine (drop None/'')."""
    from urllib.parse import urlencode
    params = {k: v for k, v in active.items() if v}
    if params.get(key) == value:
        params.pop(key, None)                    # bofya tena -> zima
    else:
        params[key] = value
    return ("?" + urlencode(params)) if params else "?"


def _filter_chips(active, allow_pair, pairs):
    """Muundo wa chips kwa template (result/session[/pair]) + active-state + any_active (clear)."""
    groups = [
        dict(name="result", label="matokeo / result", chips=[
            dict(label=lbl, active=(active.get("result") == v), qs=_chip_qs(active, "result", v))
            for v, lbl in (("W", "Wins"), ("L", "Losses"))]),
        dict(name="session", label="session", chips=[
            dict(label=s, active=(active.get("session") == s), qs=_chip_qs(active, "session", s))
            for s in _SESSIONS]),
    ]
    if allow_pair and pairs:
        groups.append(dict(name="pair", label="pair (internal)", chips=[
            dict(label=p, active=(active.get("pair") == p), qs=_chip_qs(active, "pair", p))
            for p in pairs]))
    any_active = any(active.get(k) for k in ("result", "session", "from", "to", "pair"))
    return dict(groups=groups, any_active=any_active)


@require_GET
@panel_access("scorecards")
def scorecards_list(request):
    smodels, provenance, note = _steward_models()
    # models zote za registry/callsigns (union) — hata bila steward data (light=yellow)
    ids = sorted(set(CALLSIGNS) | set(smodels)
                 | set(Trade.objects.values_list("strategy", flat=True)))
    cards = [_scorecard_summary(i, smodels) for i in ids if i in CALLSIGNS or i in smodels]
    return render(request, "monitor/scorecards_list.html", dict(
        panel="scorecards", cards=cards, steward_note=note, provenance=provenance))


@require_GET
@panel_access("scorecards")
def scorecard_detail(request, call_sign):
    internal = to_internal(call_sign)
    if internal is None:
        raise Http404(f"call-sign '{call_sign}' haipo")
    smodels, provenance, note = _steward_models()
    sm = smodels.get(internal, {})
    overall = sm.get("overall", {}) if sm else {}
    trades = Trade.objects.filter(strategy=internal)
    closed = list(trades.filter(status="CLOSED").prefetch_related("checks", "traces").order_by("-closed_at"))
    open_t = list(trades.filter(status="OPEN").prefetch_related("checks", "traces"))
    rejected = list(trades.filter(status="REJECTED").prefetch_related("checks"))
    n_closed = len(closed)
    color, disp = _status_light(overall.get("verdict"), n_closed)

    # G) equity curve (R, cumulative — kwa mpangilio wa muda)
    eq, series, labels = 0.0, [], []
    for t in sorted(closed, key=lambda x: (x.closed_at or djtz.now())):
        eq += (t.pnl_r or 0); series.append(round(eq, 4))
        labels.append(t.closed_at.strftime("%Y-%m-%d") if t.closed_at else "?")

    # F) compliance rollup
    checks = ComplianceCheck.objects.filter(trade__strategy=internal)
    n_checks, n_fails = checks.count(), checks.filter(passed=False).count()

    # E) weakness map (kwa rangi) + sentensi (best/worst kwa mean, cells zenye N>=min_n)
    wmap = sm.get("weakness_map", {}) if sm else {}
    best = worst = None; best_v = worst_v = None
    for dim, cells in wmap.items():
        for cell, cv in cells.items():
            if cv.get("verdict") == "INSUFFICIENT" or cv.get("mean") is None:
                continue
            m = cv["mean"]
            if best_v is None or m > best_v:
                best_v, best = m, f"{dim}={cell}"
            if worst_v is None or m < worst_v:
                worst_v, worst = m, f"{dim}={cell}"

    # D) filter chips (R5) — INTERNAL ina pair chip pia. Chuja closed list KABLA ya render.
    d_filtered, d_total, active = _filter_closed(closed, request, allow_pair=True)
    pairs = sorted({t.pair for t in closed})
    ctx = dict(
        panel="scorecards", call=call_sign, internal=internal, meta=public_meta(call_sign),
        color=color, display=disp, sm=sm, overall=overall,
        learned=sm.get("learned_ev"), practical=overall.get("mean"), mean_r=sm.get("mean_R"),
        ci_lo=overall.get("ci_lo"), ci_hi=overall.get("ci_hi"), divergence=overall.get("divergence"),
        say_status=language.say_both("status", call=call_sign, verdict=(disp if disp != "NO-DATA" else "NO-DATA")),
        say_promise=language.say_both("promise", learned=sm.get("learned_ev"), practical=overall.get("mean"),
                                      verdict=overall.get("verdict")),
        say_weakness=language.say_both("weakness", best=best, worst=worst),
        say_compliance=language.say_both("compliance", n=n_checks, fails=n_fails),
        open_trades=open_t, closed_trades=d_filtered[:100], rejected=rejected,
        d_total=d_total, d_shown=len(d_filtered), filters=active,
        filter_chips=_filter_chips(active, allow_pair=True, pairs=pairs),
        n_closed=n_closed, n_open=len(open_t), n_rejected=len(rejected),
        n_checks=n_checks, n_fails=n_fails, weakness_map=wmap,
        equity_json=json.dumps(dict(labels=labels, values=series)),
        steward_note=note, provenance=provenance)
    return render(request, "monitor/scorecard_detail.html", ctx)


# ==================== DASHBOARD-V2 AWAMU 3 — LESSEE VIEW (ANONYMIZED) ====================
# IP-protection (§9): lessee HAONI KAMWE pair (USDCHF/USDJPY), internal id (STRAT-xxx),
# logic/params/features, wala models za wengine. Anaona call-sign + matokeo + hali + sheria TU.
# Defence-in-depth: context ya lessee HAINA Trade object mbichi — dict ANONYMIZED pekee
# (hakuna .pair, hakuna internal id, hakuna record_id ambayo huvuja pair).

# weakness dims salama kwa lessee (ex-ante context — HAKUNA pair kamwe)
_LESSEE_WMAP_DIMS = ("session", "vol", "volatility", "streak", "cost")


def _lessee_card(call_sign, smodels):
    """Muhtasari ANONYMIZED kwa list ya /my/ — call-sign + light + sentensi (HAKUNA internal id)."""
    internal = to_internal(call_sign)                      # server-side pekee (haipiti kwa client)
    sm = smodels.get(internal, {}) if internal else {}
    overall = sm.get("overall", {}) if sm else {}
    n_closed = Trade.objects.filter(strategy=internal, status="CLOSED").count() if internal else 0
    color, disp = _status_light(overall.get("verdict"), n_closed)
    return dict(call=call_sign, meta=public_meta(call_sign), color=color, display=disp,
                n_closed=n_closed,
                sentence=language.say("status", call=call_sign,
                                      verdict=(disp if disp != "NO-DATA" else "NO-DATA")))


def _lessee_scorecard(request, call_sign):
    """Context ANONYMIZED ya scorecard (A-G rahisi) — REUSE hesabu za internal, LAKINI rudisha
    fields zisizovuja: HAKUNA pair, HAKUNA internal id, HAKUNA record_id/logic/params."""
    internal = to_internal(call_sign)                      # server-side pekee
    smodels, provenance, note = _steward_models()
    sm = smodels.get(internal, {}) if internal else {}
    overall = sm.get("overall", {}) if sm else {}
    closed = list(Trade.objects.filter(strategy=internal, status="CLOSED")
                  .prefetch_related("checks", "traces").order_by("-closed_at"))
    n_open = Trade.objects.filter(strategy=internal, status="OPEN").count()
    n_closed = len(closed)
    color, disp = _status_light(overall.get("verdict"), n_closed)

    # G) equity curve (R cumulative) — namba pekee (hakuna pair kwenye labels)
    eq, series, labels = 0.0, [], []
    for t in sorted(closed, key=lambda x: (x.closed_at or djtz.now())):
        eq += (t.pnl_r or 0); series.append(round(eq, 4))
        labels.append(t.closed_at.strftime("%Y-%m-%d") if t.closed_at else "?")

    # F) compliance rollup
    checks = ComplianceCheck.objects.filter(trade__strategy=internal)
    n_checks, n_fails = checks.count(), checks.filter(passed=False).count()

    # E) weakness map — dims salama TU (session/vol/streak/cost); pair-dim (ikitokea) inaondolewa
    wmap = {d: c for d, c in (sm.get("weakness_map", {}) if sm else {}).items()
            if d in _LESSEE_WMAP_DIMS}
    best = worst = None; best_v = worst_v = None
    for dim, cells in wmap.items():
        for cell, cv in cells.items():
            if cv.get("verdict") == "INSUFFICIENT" or cv.get("mean") is None:
                continue
            m = cv["mean"]
            if best_v is None or m > best_v:
                best_v, best = m, f"{dim}={cell}"
            if worst_v is None or m < worst_v:
                worst_v, worst = m, f"{dim}={cell}"

    # D) maamuzi ya nyuma — dicts ANONYMIZED {date, dir, R, result, reason, rules}.
    # reason = hatua zilizopita (signal/gate/fill) — HAKUNA record_id (record_id huvuja pair).
    # Filter chips (R5): session/result/date TU — HAKUNA pair chip (§9 — lessee HANA pair).
    d_filtered, d_total, active = _filter_closed(closed, request, allow_pair=False)
    history = []
    for t in d_filtered[:100]:
        stages = list(dict.fromkeys(t.traces.values_list("stage", flat=True)))
        win = (t.pnl_r or 0) > 0
        history.append(dict(
            date=(t.closed_at.strftime("%Y-%m-%d") if t.closed_at else "—"),
            dir=t.side, R=t.pnl_r, result=("WIN" if win else "LOSS"),
            reason=(" → ".join(stages) if stages else "—"),
            rules=[dict(rule=c.rule, passed=c.passed) for c in t.checks.all()]))

    return dict(
        call=call_sign, meta=public_meta(call_sign), color=color, display=disp,
        learned=sm.get("learned_ev"), practical=overall.get("mean"), mean_r=sm.get("mean_R"),
        ci_lo=overall.get("ci_lo"), ci_hi=overall.get("ci_hi"), divergence=overall.get("divergence"),
        say_status=language.say_both("status", call=call_sign,
                                     verdict=(disp if disp != "NO-DATA" else "NO-DATA")),
        say_promise=language.say_both("promise", learned=sm.get("learned_ev"),
                                      practical=overall.get("mean"), verdict=overall.get("verdict")),
        say_weakness=language.say_both("weakness", best=best, worst=worst),
        say_compliance=language.say_both("compliance", n=n_checks, fails=n_fails),
        weakness_map=wmap, history=history, n_open=n_open, n_closed=n_closed,
        d_total=d_total, d_shown=len(d_filtered), filters=active,
        filter_chips=_filter_chips(active, allow_pair=False, pairs=None),
        n_checks=n_checks, n_fails=n_fails,
        equity_json=json.dumps(dict(labels=labels, values=series)),
        steward_note=note, provenance=provenance)


@require_GET
@login_required
def lessee_list(request):
    """/my/ — orodha ya call-signs za MTEJA (leases zake) TU, kwa status light + sentensi.
    Internal/attestor = call-signs ZOTE (QA). READ-ONLY."""
    g = _groups(request.user)
    if g & {"internal", "attestor"}:
        calls = sorted(CALLSIGNS.values())                 # QA: zote
    else:
        calls = sorted(to_public(m) for m in user_leases(request.user) if m in CALLSIGNS)
    smodels, _prov, note = _steward_models()
    cards = [_lessee_card(c, smodels) for c in calls]
    audit(request, "view_my_models", ",".join(calls) or "-")
    return render(request, "monitor/scorecard_lessee_list.html", dict(
        panel="my", cards=cards, steward_note=note))


@require_GET
@login_required
def lessee_detail(request, call_sign):
    """/my/<call_sign>/ — scorecard ANONYMIZED ya model MMOJA (lease-gated). READ-ONLY."""
    if to_internal(call_sign) is None:
        raise Http404(f"call-sign '{call_sign}' haipo")
    lessee_can_see(request.user, call_sign)                # 403 kama si lease yake (wala internal/attestor)
    ctx = _lessee_scorecard(request, call_sign)
    audit(request, "view_my_scorecard", call_sign)
    return render(request, "monitor/scorecard_lessee.html", dict(panel="my", **ctx))
