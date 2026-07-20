"""Admin — internal ops tu (read-mostly; mirror models)."""
from django.contrib import admin

from . import models

for m in (models.Trade, models.DecisionTrace, models.ComplianceCheck, models.StrategyPerf,
          models.ModelVersion, models.PairStrategyCell, models.VpsHeartbeat, models.Alert,
          models.Report, models.LedgerEntry, models.Lesson, models.Lease, models.AuditEvent):
    admin.site.register(m)
