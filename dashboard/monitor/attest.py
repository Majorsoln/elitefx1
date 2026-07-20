"""
Attestation export (V2 §5.2) — "bidhaa ya kukodisha yenyewe": performance ya model version
inayoweza kukaguliwa na mtu wa nje. Payload = canonical JSON (sort_keys) + SHA-256 hash.

DETERMINISM: hash inahesabiwa juu ya payload ISIYO na timestamps za ingest/generate — data ya
artifacts pekee → attestation ile ile mara zote (reproducible; test AT-hash). `generated_at`
inaongezwa NJE ya hashed payload.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from .models import ComplianceCheck, ModelVersion, StrategyPerf, Trade


def build_payload(model_id):
    """Canonical attestation payload ya model (kutoka DB mirror — kila field ina chanzo)."""
    versions = list(ModelVersion.objects.filter(model_id=model_id).order_by("version"))
    if not versions:
        return None
    trades = Trade.objects.filter(strategy=model_id, status="CLOSED").order_by("trade_id")
    checks = ComplianceCheck.objects.filter(trade__strategy=model_id)
    perf = StrategyPerf.objects.filter(strategy=model_id).order_by("period", "mode")
    n_checks = checks.count()
    n_fail = checks.filter(passed=False).count()
    payload = {
        "model_id": model_id,
        "versions": [dict(version=v.version, model_class=v.model_class, status=v.status,
                          oos_proof=v.oos_proof, provenance=v.provenance,
                          promised_ev=v.promised_ev, promised_n=v.promised_n,
                          source_ref=v.source_ref, is_demo=v.is_demo) for v in versions],
        "live_performance": [dict(period=p.period, mode=p.mode, n_trades=p.n_trades,
                                  net_r=p.net_r, win_rate=p.win_rate, expectancy_r=p.expectancy_r,
                                  profit_factor=p.profit_factor, max_dd_r=p.max_dd_r,
                                  source_ref=p.source_ref) for p in perf],
        "trades": dict(n_closed=trades.count(),
                       ids_hash=hashlib.sha256(
                           ",".join(t.trade_id for t in trades).encode()).hexdigest()[:16]),
        "compliance": dict(n_checks=n_checks, n_violations=n_fail,
                           score=(round(100 * (1 - n_fail / n_checks), 2) if n_checks else None)),
        "doctrine": "V2 §5: immutable audit trail + attestation + rule-compliance proof",
    }
    return payload


def attestation(model_id):
    """Rudisha (payload_with_hash, canonical_json) au None. Hash = SHA-256 ya canonical payload."""
    payload = build_payload(model_id)
    if payload is None:
        return None
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode()).hexdigest()
    out = dict(payload, attestation_hash=digest,
               generated_at=datetime.now(timezone.utc).isoformat())   # NJE ya hash (determinism)
    return out, canonical


def render_pdf(data):
    """PDF ya attestation (hiari — reportlab ikiwepo; la sivyo rudisha None)."""
    try:
        from io import BytesIO
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas as rl_canvas
    except ImportError:
        return None
    buf = BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=A4)
    y = 800
    c.setFont("Courier-Bold", 14); c.drawString(40, y, f"ELITEFX ATTESTATION — {data['model_id']}"); y -= 24
    c.setFont("Courier", 8)
    for ln in json.dumps(data, indent=1, sort_keys=True).splitlines():
        if y < 40:
            c.showPage(); c.setFont("Courier", 8); y = 800
        c.drawString(40, y, ln[:110]); y -= 10
    c.save()
    return buf.getvalue()
