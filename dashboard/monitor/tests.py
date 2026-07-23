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


class AuditFixTests(TestCase):
    """M-DASH-FIX: repro za auditor (F1-F6) sasa ZINASHINDWA kuvunja mfumo."""

    def test_f1_queryset_immutability(self):
        # repro P6/P6b: bulk update()/delete() zilipita save() — sasa zinakataliwa
        AuditEvent.objects.create(user="qa", action="probe", subject="x")
        with self.assertRaises(ValueError):
            AuditEvent.objects.filter(action="probe").update(detail="TAMPERED")
        with self.assertRaises(ValueError):
            AuditEvent.objects.filter(action="probe").delete()
        with self.assertRaises(ValueError):
            AuditEvent.objects.all().delete()
        ev = AuditEvent.objects.get(action="probe")
        self.assertEqual(ev.detail, "")                      # haikubadilika
        self.assertEqual(AuditEvent.objects.count(), 1)      # haikufutwa

    def test_f2_no_unit_mixing(self):
        # repro P4: settlement currency-only (hakuna pnl_r) + moja yenye pnl_r=1.0
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "log.jsonl"
            recs = [
                {"kind": "execution", "obj": {"id": "exec:qa:1", "order_id": "qa:1", "pair": "EURUSD",
                 "side": "BUY", "status": "FILLED", "as_of": 1767862800, "mode": "paper"}},
                {"kind": "settlement", "obj": {"id": "qa:1", "realized_pnl": 250.0, "as_of": 1767884400}},
                {"kind": "execution", "obj": {"id": "exec:qa:2", "order_id": "qa:2", "pair": "EURUSD",
                 "side": "BUY", "status": "FILLED", "as_of": 1767862900, "mode": "paper"}},
                {"kind": "settlement", "obj": {"id": "qa:2", "pnl_r": 1.0, "realized_pnl": 12.0,
                 "as_of": 1767884500}},
            ]
            p.write_text("\n".join(json.dumps(r) for r in recs))
            loaders.load_paper_log(p)
        n, note = loaders.rebuild_strategy_perf()
        sp = StrategyPerf.objects.get(strategy="UNKNOWN", period="ALL", mode="paper")
        # R-metrics kutoka pnl_r PEKEE: n=1, net_r=1.0, expectancy=1.0 (SI 251/125.5 ya unit-mix)
        self.assertEqual(sp.n_trades, 1)
        self.assertAlmostEqual(sp.net_r, 1.0)
        self.assertAlmostEqual(sp.expectancy_r, 1.0)
        self.assertIn("bila pnl_r", note)                    # excluded inaripotiwa wazi
        # equity series (R) haina trade ya currency-only
        from .views import _equity_series
        labels, series = _equity_series()
        self.assertEqual(len(series), 1)
        self.assertAlmostEqual(series[-1], 1.0)

    def test_f3_no_fabricated_ts(self):
        # repro P2: heartbeat ts batili -> ts=None + status SI OPERATIONAL
        with tempfile.TemporaryDirectory() as tmp:
            hb = Path(tmp) / "hb.json"
            hb.write_text('{"ts": "not-a-date", "uptime_s": 1}')
            n, note = loaders.load_heartbeat(hb)
            self.assertEqual(n, 1)
            self.assertIn("invalid ts", note)
            self.assertIsNone(VpsHeartbeat.objects.first().ts)
            from .views import _system_status
            status, _hb = _system_status()
            self.assertNotEqual(status, "OPERATIONAL")
            # repro P3: alert bila ts -> ts=None + tagged (SI now())
            al = Path(tmp) / "a.jsonl"
            al.write_text('{"kind":"drift","severity":"WARN","message":"x","dedupe_key":"qa-alert"}\n')
            loaders.load_alerts(al)
            a = Alert.objects.get(dedupe_key="qa-alert")
            self.assertIsNone(a.ts)
            self.assertIn("[invalid/missing ts]", a.message)

    def test_f4_watch_table_ingested(self):
        # WATCH table ya columns 5 ina-parse (C2/SWING/K4-WATCH)
        with tempfile.TemporaryDirectory() as tmp:
            md = Path(tmp) / "reg.md"
            md.write_text(
                "| id | version | class | status | OOS proof | provenance |\n"
                "|----|---------|-------|--------|-----------|------------|\n"
                "| STRAT-001 | v1.0 | strategy | PROVEN | HOLDOUT N=303 EV+1.92 | nr7 |\n\n"
                "| id | class | status | signal | njia |\n"
                "|----|-------|--------|--------|------|\n"
                "| C2-WATCH | strategy | WATCH | compression×H4 pooled | forward data |\n"
                "| SWING-WATCH | strategy | WATCH | nr7×D1×LOW pooled | forward 2026-05+ |\n")
            n, _ = loaders.load_model_registry(md)
        self.assertEqual(n, 3)
        self.assertTrue(ModelVersion.objects.filter(model_id="C2-WATCH", version="watch").exists())
        self.assertTrue(ModelVersion.objects.filter(model_id="SWING-WATCH").exists())
        self.assertEqual(ModelVersion.objects.get(model_id="C2-WATCH").oos_proof,
                         "compression×H4 pooled")

    def test_f5_malformed_json_skipped(self):
        # repro P1: mstari mbovu -> skip + note (hakuna crash); mizuri inaendelea ku-ingest
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "bad.jsonl"
            p.write_text('{"kind": "execution", "obj": {broken json\nnot json at all\n'
                         + json.dumps({"kind": "execution", "obj": {"id": "exec:ok:1",
                            "order_id": "ok:1", "pair": "EURUSD", "side": "BUY",
                            "status": "FILLED", "as_of": 1767862800}}) + "\n")
            n, note = loaders.load_paper_log(p)
            self.assertEqual(n, 1)                           # record nzuri ime-ingest
            self.assertIn("skipped 2 bad json", note)
            # heartbeat json mbovu -> (0, note), si crash
            hb = Path(tmp) / "hb.json"
            hb.write_text("not json{{{")
            n2, note2 = loaders.load_heartbeat(hb)
            self.assertEqual(n2, 0)
            self.assertIn("invalid json", note2)

    def test_f6_attestation_has_commit(self):
        call_command("ingest", "--demo", verbosity=0)
        data, canonical = attest.attestation("STRAT-001")
        self.assertIn("repo_commit", data)
        self.assertTrue(len(data["repo_commit"]) >= 7 or data["repo_commit"] == "unknown")
        self.assertIn("repo_commit", canonical)              # NDANI ya hashed payload
        # reproducibility inabaki (commit ile ile ndani ya run)
        data2, _ = attest.attestation("STRAT-001")
        self.assertEqual(data["attestation_hash"], data2["attestation_hash"])


# ==================== DASHBOARD-V2 Awamu 1 — MODEL SCORECARD tests ====================
import tempfile
from django.test import override_settings
from monitor import callsigns, language, loaders as _loaders

_STEWARD_DEMO = {
    "provenance": {"commit": "abc1234def", "sample_note": "SAMPLE: replay/validation, si forward",
                   "log_lines": 100},
    "models": {
        "STRAT-001": {"learned_ev": 1.92, "mean_R": 0.15,
                      "overall": {"n": 40, "mean": 3.07, "ci_lo": 1.2, "ci_hi": 4.9,
                                  "divergence": 1.15, "verdict": "HOLDS"},
                      "weakness_map": {"session": {"NY": {"n": 35, "mean": 4.1, "verdict": "LIFTS"},
                                                   "ASIA": {"n": 10, "mean": -1.0, "verdict": "INSUFFICIENT"}},
                                       "cost": {"HIGH-COST": {"n": 33, "mean": 2.0, "verdict": "HOLDS"}}}},
        "STRAT-002": {"learned_ev": 2.65, "mean_R": -0.3,
                      "overall": {"n": 44, "mean": -1.5, "ci_lo": -3.0, "ci_hi": -0.2,
                                  "divergence": -4.15, "verdict": "SHRINKS"},
                      "weakness_map": {}}},
    "agenda": [],
}


def _write_steward(tmp):
    (Path(tmp) / "model_steward.json").write_text(json.dumps(_STEWARD_DEMO), encoding="utf-8")
    return tmp


class CallsignTests(TestCase):
    def test_a_callsign_round_trip_and_public_meta_no_pair(self):
        self.assertEqual(callsigns.to_public("STRAT-001"), "KAIROS-1")
        self.assertEqual(callsigns.to_internal("KAIROS-1"), "STRAT-001")
        self.assertEqual(callsigns.to_internal("KAIROS-2"), "STRAT-002")
        # round-trip
        for internal in ("STRAT-001", "STRAT-002"):
            self.assertEqual(callsigns.to_internal(callsigns.to_public(internal)), internal)
        # unknown -> None (internal), label passthrough (public)
        self.assertIsNone(callsigns.to_internal("KAIROS-99"))
        # PUBLIC_META has NO pair / logic / params / internal id
        for cs, meta in callsigns.PUBLIC_META.items():
            blob = json.dumps(meta).lower()
            for leak in ("usdchf", "usdjpy", "pair", "strat-", "nr7", "sl_atr", "logic"):
                self.assertNotIn(leak, blob, f"{cs} PUBLIC_META inavuja '{leak}'")
            self.assertEqual(set(meta), {"version", "status"})


class StewardLoaderTests(TestCase):
    def test_b_load_steward_fail_soft(self):
        with tempfile.TemporaryDirectory() as tmp:
            # haipo -> ({}, note)
            data, note = _loaders.load_steward(tmp)
            self.assertEqual(data, {})
            self.assertIn("no data", note)
            # mbovu -> ({}, note) si crash
            (Path(tmp) / "model_steward.json").write_text("not json{{{")
            data2, note2 = _loaders.load_steward(tmp)
            self.assertEqual(data2, {})
            self.assertIn("invalid", note2)
            # halali -> data + no note
            _write_steward(tmp)
            data3, note3 = _loaders.load_steward(tmp)
            self.assertIsNone(note3)
            self.assertIn("STRAT-001", data3["models"])


class ScorecardViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("ingest", "--demo", verbosity=0)

    def _paths_with_steward(self, tmp):
        _write_steward(tmp)
        from django.conf import settings
        return dict(settings.ELITEFX_PATHS, reports_dir=Path(tmp))

    def test_c_status_light_mapping(self):
        from monitor.views import _status_light
        self.assertEqual(_status_light("HOLDS", 40)[0], "green")
        self.assertEqual(_status_light("LIFTS", 40)[0], "green")
        self.assertEqual(_status_light("SHRINKS", 40)[0], "red")
        self.assertEqual(_status_light("INSUFFICIENT", 40)[0], "yellow")
        self.assertEqual(_status_light("HOLDS", 0), ("yellow", "NO-DATA"))     # no closed trades
        self.assertEqual(_status_light(None, 0)[0], "yellow")

    def test_d_scorecard_access_internal_vs_anon_vs_lessee(self):
        with tempfile.TemporaryDirectory() as tmp:
            with override_settings(ELITEFX_PATHS=self._paths_with_steward(tmp)):
                # internal -> 200 (list + detail)
                self.client.force_login(_mk_user("pd", "internal"))
                self.assertEqual(self.client.get("/scorecards/").status_code, 200)
                r = self.client.get("/scorecards/KAIROS-1/")
                self.assertEqual(r.status_code, 200)
                self.assertIn(b"KAIROS-1", r.content)
                self.assertNotIn(b"KAIROS-2", r.content.split(b"internal=")[0])  # detail ni ya moja
                # bad call-sign -> 404
                self.assertEqual(self.client.get("/scorecards/KAIROS-99/").status_code, 404)
                # SHRINKS -> red light kwenye KAIROS-2
                r2 = self.client.get("/scorecards/KAIROS-2/")
                self.assertIn(b"light red", r2.content)
                # POST -> 405 (read-only)
                self.assertEqual(self.client.post("/scorecards/").status_code, 405)
                self.assertEqual(self.client.post("/scorecards/KAIROS-1/").status_code, 405)
        # lessee/attestor -> 403 (Awamu 1 = internal tu)
        self.client.force_login(_mk_user("cli", "lessee", lease="STRAT-001"))
        self.assertEqual(self.client.get("/scorecards/").status_code, 403)
        self.assertEqual(self.client.get("/scorecards/KAIROS-1/").status_code, 403)
        self.client.force_login(_mk_user("att", "attestor"))
        self.assertEqual(self.client.get("/scorecards/").status_code, 403)
        # anon -> 302 login
        self.client.logout()
        r3 = self.client.get("/scorecards/")
        self.assertEqual(r3.status_code, 302)
        self.assertIn("/login/", r3["Location"])

    def test_d2_scorecard_fail_soft_no_steward(self):
        # steward haipo -> list 200 + note; lights NO-DATA (yellow)
        with tempfile.TemporaryDirectory() as tmp:
            with override_settings(ELITEFX_PATHS=dict(__import__("django.conf").conf.settings.ELITEFX_PATHS,
                                                      reports_dir=Path(tmp))):
                self.client.force_login(_mk_user("pd2", "internal"))
                r = self.client.get("/scorecards/")
                self.assertEqual(r.status_code, 200)
                self.assertIn(b"no data", r.content.lower())


class LanguageTests(TestCase):
    def test_e_language_say_deterministic(self):
        s1 = language.say("status", call="KAIROS-1", verdict="HOLDS")
        s2 = language.say("status", call="KAIROS-1", verdict="HOLDS")
        self.assertEqual(s1, s2)
        self.assertIn("KAIROS-1", s1)
        self.assertNotEqual(language.say("status", call="KAIROS-1", verdict="SHRINKS"), s1)
        # promise
        pr = language.say("promise", learned=1.92, practical=3.07, verdict="HOLDS")
        self.assertIn("1.92", pr); self.assertIn("juu ya ahadi", pr)
        self.assertEqual(pr, language.say("promise", learned=1.92, practical=3.07, verdict="HOLDS"))
        # no-data safe
        self.assertTrue(language.say("promise", learned=None, practical=None))
        # weakness deterministic
        w = language.say("weakness", best="session=NY", worst="streak=AFTER_LOSS")
        self.assertEqual(w, language.say("weakness", best="session=NY", worst="streak=AFTER_LOSS"))
        self.assertIn("NY", w)
