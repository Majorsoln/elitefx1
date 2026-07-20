"""
GLASS BOX DB models — MIRROR ya artifacts (SI trading logic; Doctrine V2 §4).

Kila model una `source_ref` (path/commit ya artifact chanzo) — kiini cha glass-box: kila namba
kwenye dashboard ina kiungo cha chanzo kinachokaguliwa. `is_demo` inaonyesha demo fixtures WAZI.
AuditEvent ni APPEND-ONLY (save inakataa update). HAKUNA model inayoandika kwenye artifacts.
"""
from django.conf import settings
from django.db import models


class SourcedModel(models.Model):
    """Base: kila rekodi ya mirror ina chanzo + demo flag (hakuna namba bila chanzo)."""
    source_ref = models.CharField(max_length=400, help_text="artifact path / commit ya chanzo")
    is_demo = models.BooleanField(default=False, help_text="demo fixture (SI data halisi)")
    ingested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Trade(SourcedModel):
    """Trade iliyokamilika/wazi kutoka paper/live log (execution+settlement records)."""
    trade_id = models.CharField(max_length=120, unique=True)      # order_id ya log (idempotency key)
    strategy = models.CharField(max_length=40)
    pair = models.CharField(max_length=12)
    side = models.CharField(max_length=6)                          # BUY/SELL
    qty = models.FloatField(null=True)
    entry = models.FloatField(null=True)
    exit = models.FloatField(null=True)
    sl = models.FloatField(null=True)
    tp = models.FloatField(null=True)
    pnl = models.FloatField(null=True)                             # currency/pips (kama log)
    pnl_r = models.FloatField(null=True)                           # R-multiple kama inapatikana
    status = models.CharField(max_length=20, default="OPEN")       # OPEN/CLOSED/REJECTED
    opened_at = models.DateTimeField(null=True)
    closed_at = models.DateTimeField(null=True)
    mode = models.CharField(max_length=10, default="paper")        # paper/live

    class Meta:
        ordering = ["-opened_at"]


class DecisionTrace(SourcedModel):
    """Hatua za decision-chain za trade (signal→policy→risk→compliance→fill) — glass ya kiini."""
    trade = models.ForeignKey(Trade, on_delete=models.CASCADE, related_name="traces", null=True)
    seq = models.IntegerField(default=0)
    stage = models.CharField(max_length=30)                        # signal/policy/risk/compliance/fill
    record_id = models.CharField(max_length=200)                   # id ya record kwenye log
    payload = models.JSONField(default=dict)                       # record kamili (auditable)

    class Meta:
        ordering = ["trade_id", "seq"]
        unique_together = [("record_id", "stage", "seq")]


class ComplianceCheck(SourcedModel):
    """Ukaguzi wa sheria per trade (FTMO daily/max-loss, no-trade-window, max-spread, gate)."""
    trade = models.ForeignKey(Trade, on_delete=models.CASCADE, related_name="checks", null=True)
    rule = models.CharField(max_length=80)
    passed = models.BooleanField()
    detail = models.CharField(max_length=300, blank=True, default="")

    class Meta:
        unique_together = [("trade", "rule")]


class StrategyPerf(SourcedModel):
    """Rolling/monthly performance per strategy (derived WAKATI wa ingest kutoka trades — si live calc)."""
    strategy = models.CharField(max_length=40)
    period = models.CharField(max_length=10)                       # 'YYYY-MM' au 'ALL'
    n_trades = models.IntegerField(default=0)
    net_r = models.FloatField(null=True)
    win_rate = models.FloatField(null=True)
    expectancy_r = models.FloatField(null=True)
    profit_factor = models.FloatField(null=True)
    max_dd_r = models.FloatField(null=True)
    mode = models.CharField(max_length=10, default="paper")

    class Meta:
        unique_together = [("strategy", "period", "mode")]


class ModelVersion(SourcedModel):
    """Kadi ya registry (docs/MODEL_REGISTRY.md mirror): id+version+status+OOS proof+promised EV."""
    model_id = models.CharField(max_length=60)
    version = models.CharField(max_length=20, default="v1.0")
    model_class = models.CharField(max_length=30, default="strategy")
    status = models.CharField(max_length=40)                       # CANDIDATE/PROVEN/LIVE/RETIRED/WATCH/DEAD
    oos_proof = models.CharField(max_length=300, blank=True, default="")
    provenance = models.CharField(max_length=300, blank=True, default="")
    promised_ev = models.FloatField(null=True)                     # holdout/backtest EV (ahadi)
    promised_n = models.IntegerField(null=True)
    shrinkage_lo = models.FloatField(null=True, default=0.35)      # band ya shrinkage (0.35-0.5x)
    shrinkage_hi = models.FloatField(null=True, default=0.5)

    class Meta:
        unique_together = [("model_id", "version")]


class PairStrategyCell(SourcedModel):
    """Heatmap cell: pair × strategy/family → EV / win% / N (+ drill-down context)."""
    pair = models.CharField(max_length=12)
    strategy = models.CharField(max_length=60)
    n = models.IntegerField(default=0)
    ev = models.FloatField(null=True)
    win_rate = models.FloatField(null=True)
    context = models.JSONField(default=dict)                       # atlas rows / lessons refs

    class Meta:
        unique_together = [("pair", "strategy")]


class VpsHeartbeat(SourcedModel):
    """Heartbeat ya VPS (faili la env path): uptime, latency, clock drift, feed freshness."""
    ts = models.DateTimeField()
    uptime_s = models.BigIntegerField(null=True)
    latency_ms = models.FloatField(null=True)
    clock_drift_ms = models.FloatField(null=True)
    disk_free_pct = models.FloatField(null=True)
    mem_free_pct = models.FloatField(null=True)
    feed_freshness = models.JSONField(default=dict)                # pair -> seconds since last tick

    class Meta:
        ordering = ["-ts"]


class Alert(SourcedModel):
    """Diagnosis alerts (monitors: retention drift, cost drift, streak, degradation, data-gap...)."""
    ts = models.DateTimeField()
    severity = models.CharField(max_length=10)                     # INFO/WARN/CRIT
    kind = models.CharField(max_length=60)
    message = models.CharField(max_length=400)
    dedupe_key = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ["-ts"]


class Report(SourcedModel):
    """Reports browser entry (reports/*.md)."""
    path = models.CharField(max_length=300, unique=True)           # relative kwa REPO_ROOT
    title = models.CharField(max_length=300)
    section = models.CharField(max_length=40, default="reports")   # reports/archive


class LedgerEntry(SourcedModel):
    """EXPERIMENT_LEDGER.md mirror: jaribio + verdict + report path."""
    cycle = models.CharField(max_length=40)
    exp_id = models.CharField(max_length=40)
    title = models.CharField(max_length=300)
    verdict = models.CharField(max_length=300)
    report_path = models.CharField(max_length=300, blank=True, default="")

    class Meta:
        unique_together = [("cycle", "exp_id")]


class Lesson(SourcedModel):
    """docs/lessons/LESSON-*.md mirror."""
    lesson_id = models.CharField(max_length=40, unique=True)
    title = models.CharField(max_length=300)
    body_md = models.TextField(blank=True, default="")


class Lease(models.Model):
    """Leasing foundation: lessee-user → model MOJA (read-only monitoring + attestation yake)."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="leases")
    model_id = models.CharField(max_length=60)
    started_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user", "model_id")]


class AuditEvent(models.Model):
    """APPEND-ONLY audit trail (V2 §5.1): kila attestation view/export inarekodiwa. Update = marufuku."""
    ts = models.DateTimeField(auto_now_add=True)
    user = models.CharField(max_length=120)
    action = models.CharField(max_length=60)                       # view_attestation/export_attestation/...
    subject = models.CharField(max_length=200)
    detail = models.CharField(max_length=400, blank=True, default="")

    class Meta:
        ordering = ["-ts"]

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise ValueError("AuditEvent ni append-only — update ni marufuku (V2 §5)")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("AuditEvent ni append-only — delete ni marufuku (V2 §5)")
