"""
GLASS BOX tests — sheria ngumu za charter (§NIDHAMU):
 (a) ingest correctness (fixtures→DB) + IDEMPOTENT (re-ingest haina duplicate);
 (b) NO-FABRICATION (artifact tupu → "no data", counts 0 — hakuna kubuni);
 (c) READ-ONLY (hakuna trade-mutation endpoint; POST → 405; smoke ya kila panel = 200);
 (d) attestation hash STABLE (reproducible — determinism);
 (e) ROLE ACCESS (lessee = model yake TU; hawezi research/ledger wala models nyingine).
"""
import json
import tempfile
from pathlib import Path

from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.test import TestCase, override_settings

from . import attest, loaders
from .models import (Alert, AuditEvent, ComplianceCheck, DecisionTrace, LedgerEntry, Lease,
                     Lesson, ModelVersion, PairStrategyCell, Report, StrategyPerf, Trade,
                     VpsHeartbeat)

PANELS = ["/deck/", "/portfolio/", "/actions/", "/compliance/", "/registry/", "/matrix/",
          "/alerts/", "/vps/", "/ledger/", "/audit/"]


def _mk_user(name, group=None, lease=None):
    u = User.objects.create_user(name, password="x")
    if group:
        g, _ = Group.objects.get_or_create(name=group)
        u.groups.add(g)
    if lease:
        Lease.objects.create(user=u, model_id=lease)
    return u


class IngestTests(TestCase):
    def test_a_ingest_correctness_and_idempotent(self):
        call_command("ingest", "--demo", verbosity=0)
        counts1 = dict(trades=Trade.objects.count(), traces=DecisionTrace.objects.count(),
                       checks=ComplianceCheck.objects.count(), models=ModelVersion.objects.count(),
                       ledger=LedgerEntry.objects.count(), reports=Report.objects.count(),
                       lessons=Lesson.objects.count(), cells=PairStrategyCell.objects.count(),
                       alerts=Alert.objects.count(), hb=VpsHeartbeat.objects.count(),
                       perf=StrategyPerf.objects.count())
        # fixtures zina data ya kila loader
        for k, v in counts1.items():
            self.assertGreater(v, 0, f"{k}: ingest haikuleta rekodi")
        self.assertEqual(Trade.objects.count(), 10)
        self.assertEqual(ModelVersion.objects.filter(model_id="STRAT-001").count(), 1)
        # attribution + settlement
        t = Trade.objects.get(trade_id="paper:1")
        self.assertEqual(t.strategy, "STRAT-001"); self.assertEqual(t.status, "CLOSED")
        self.assertAlmostEqual(t.pnl, 12.0)
        # demo flag WAZI
        self.assertTrue(all(x.is_demo for x in Trade.objects.all()))
        # violation ya demo (trade #7 max_spread FAIL)
        self.assertEqual(ComplianceCheck.objects.filter(passed=False).count(), 1)
        # IDEMPOTENT: re-ingest → counts zilezile
        call_command("ingest", "--demo", verbosity=0)
        counts2 = dict(trades=Trade.objects.count(), traces=DecisionTrace.objects.count(),
                       checks=ComplianceCheck.objects.count(), models=ModelVersion.objects.count(),
                       ledger=LedgerEntry.objects.count(), reports=Report.objects.count(),
                       lessons=Lesson.objects.count(), cells=PairStrategyCell.objects.count(),
                       alerts=Alert.objects.count(), hb=VpsHeartbeat.objects.count(),
                       perf=StrategyPerf.objects.count())
        self.assertEqual(counts1, counts2, "re-ingest imeleta duplicates")

    def test_b_no_fabrication_empty_artifacts(self):
        # artifacts hazipo kabisa → kila loader inarudisha (0, "no data...") — HAKUNA kubuni
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            for fn, args in [(loaders.load_paper_log, (tmp / "x.jsonl",)),
                             (loaders.load_model_registry, (tmp / "x.md",)),
                             (loaders.load_ledger, (tmp / "x.md",)),
                             (loaders.load_reports, (tmp / "nodir", tmp)),
                             (loaders.load_lessons, (tmp / "nodir",)),
                             (loaders.load_pair_strategy, (tmp / "x.parquet", tmp / "x.jsonl")),
                             (loaders.load_alerts, (tmp / "x.jsonl",)),
                             (loaders.load_heartbeat, (tmp / "x.json",))]:
                n, note = fn(*args)
                self.assertEqual(n, 0)
                self.assertIn("no data", note)
        n, note = loaders.rebuild_strategy_perf()
        self.assertEqual(n, 0); self.assertIn("no data", note)
        self.assertEqual(Trade.objects.count(), 0)
        # panels zinaonyesha "no data" (HTTP 200) badala ya namba za kubuni
        self.client.force_login(_mk_user("op", "internal"))
        for url in ["/deck/", "/actions/", "/matrix/", "/alerts/", "/vps/"]:
            r = self.client.get(url)
            self.assertEqual(r.status_code, 200, url)
            self.assertIn(b"no data", r.content.lower(), url)


class ReadOnlyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("ingest", "--demo", verbosity=0)

    def test_c_panels_smoke_and_no_mutation(self):
        self.client.force_login(_mk_user("op", "internal"))
        for url in PANELS:
            r = self.client.get(url)
            self.assertEqual(r.status_code, 200, f"{url} si 200")
        # drill-downs
        for url in ["/registry/STRAT-001/", "/matrix/USDCHF/nr7_break/",
                    "/reports/reports/demo_report_a.md", "/registry/STRAT-001/attest.html"]:
            self.assertEqual(self.client.get(url).status_code, 200, url)
        # READ-ONLY: POST kwa panels → 405 (require_GET); HAKUNA trade inayobadilika
        n_before = Trade.objects.count()
        pnl_before = list(Trade.objects.values_list("pnl", flat=True))
        for url in PANELS + ["/registry/STRAT-001/attest.json"]:
            r = self.client.post(url, {"pair": "EURUSD", "side": "BUY"})
            self.assertEqual(r.status_code, 405, f"{url} inakubali POST (marufuku V2 §4)")
        self.assertEqual(Trade.objects.count(), n_before)
        self.assertEqual(list(Trade.objects.values_list("pnl", flat=True)), pnl_before)

    def test_c2_no_trade_mutation_url_exists(self):
        # hakuna URL yenye jina la kuanzisha trade (defence-in-depth ya charter)
        from django.urls import get_resolver
        names = {p.name for p in get_resolver().url_patterns[-1].url_patterns if hasattr(p, "name")}
        for banned in ("trade_create", "order_create", "execute", "buy", "sell"):
            self.assertNotIn(banned, names)

    def test_d_attestation_hash_stable(self):
        r1 = attest.attestation("STRAT-001")
        r2 = attest.attestation("STRAT-001")
        self.assertIsNotNone(r1)
        (d1, c1), (d2, c2) = r1, r2
        self.assertEqual(d1["attestation_hash"], d2["attestation_hash"], "hash si stable")
        self.assertEqual(c1, c2)
        # hash inabadilika data ikibadilika (sensitivity — si constant); perf inatumia pnl_r
        t = Trade.objects.filter(strategy="STRAT-001", status="CLOSED").first()
        t.pnl_r = (t.pnl_r or 0) + 1; t.save()
        loaders.rebuild_strategy_perf(demo=True)
        d3, _ = attest.attestation("STRAT-001")
        self.assertNotEqual(d1["attestation_hash"], d3["attestation_hash"])

    def test_d2_attestation_endpoints_and_audit(self):
        self.client.force_login(_mk_user("op", "internal"))
        r = self.client.get("/registry/STRAT-001/attest.json")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.content)
        self.assertIn("attestation_hash", data)
        self.assertTrue(AuditEvent.objects.filter(action="export_attestation_json",
                                                  subject="STRAT-001").exists())
        # append-only: update ya AuditEvent inakataliwa
        ev = AuditEvent.objects.first()
        ev.detail = "tampered"
        with self.assertRaises(ValueError):
            ev.save()
        with self.assertRaises(ValueError):
            ev.delete()


class RoleAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("ingest", "--demo", verbosity=0)

    def test_e_lessee_scoped_access(self):
        lessee = _mk_user("client1", "lessee", lease="STRAT-001")
        self.client.force_login(lessee)
        # model wake: registry detail + attestation = 200
        self.assertEqual(self.client.get("/registry/STRAT-001/").status_code, 200)
        self.assertEqual(self.client.get("/registry/STRAT-001/attest.html").status_code, 200)
        # model MWINGINE → 403
        self.assertEqual(self.client.get("/registry/STRAT-002/").status_code, 403)
        self.assertEqual(self.client.get("/registry/STRAT-002/attest.json").status_code, 403)
        # research/panels za ndani → 403 (SI research, SI models nyingine)
        for url in ["/deck/", "/portfolio/", "/actions/", "/ledger/", "/matrix/",
                    "/alerts/", "/vps/", "/compliance/", "/registry/", "/audit/"]:
            self.assertEqual(self.client.get(url).status_code, 403, url)
        # landing yake inaonyesha lease yake tu
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"STRAT-001", r.content)
        self.assertNotIn(b"STRAT-002", r.content)

    def test_e2_attestor_scope(self):
        att = _mk_user("auditor", "attestor")
        self.client.force_login(att)
        for url in ["/compliance/", "/registry/", "/audit/", "/registry/STRAT-002/attest.html"]:
            self.assertEqual(self.client.get(url).status_code, 200, url)
        for url in ["/deck/", "/portfolio/", "/actions/", "/ledger/", "/matrix/", "/vps/"]:
            self.assertEqual(self.client.get(url).status_code, 403, url)

    def test_e3_anonymous_redirected(self):
        for url in PANELS:
            r = self.client.get(url)
            self.assertEqual(r.status_code, 302, url)
            self.assertIn("/login/", r["Location"])
