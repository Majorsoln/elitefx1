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
from .access import audit, model_access, panel_access, user_leases, _groups
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
    return render(request, "monitor/deck.html", dict(
        panel="deck", status=status, hb=hb,
        score=score, n_checks=n_checks, n_fails=n_fails,
        open_positions=Trade.objects.filter(status="OPEN").count(),
        active_models=ModelVersion.objects.filter(status__icontains="PROVEN").count()
        + ModelVersion.objects.filter(status__icontains="LIVE").count(),
        perf_all=perf_all, perf_month=perf_month,
        equity_json=json.dumps(dict(labels=labels[-120:], values=eq[-120:])),
        today_actions=Trade.objects.all()[:8],
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
    leases = user_leases(request.user)
    models = ModelVersion.objects.filter(model_id__in=leases)
    return render(request, "monitor/lessee.html", dict(panel="lessee", models=models, leases=leases))
