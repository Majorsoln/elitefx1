"""M-DASH-QA adversarial probes — endeshwa kupitia `manage.py shell`."""
import hashlib, json, tempfile, traceback
from pathlib import Path

from django.core.management import call_command
from monitor import attest, loaders
from monitor.models import AuditEvent, StrategyPerf, Trade, VpsHeartbeat, Alert

R = []
def probe(name):
    def deco(fn):
        try:
            out = fn()
            R.append((name, "OK" if out is True else out))
        except Exception as e:
            R.append((name, f"EXC: {type(e).__name__}: {e}"))
    return deco

# fresh demo ingest baseline
call_command("ingest", "--demo", verbosity=0)

# 1) malformed jsonl -> loader crash?
@probe("P1 malformed paper_log jsonl")
def p1():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "bad.jsonl"
        p.write_text('{"kind": "execution", "obj": {broken json\nnot json at all\n')
        try:
            n, note = loaders.load_paper_log(p)
            return f"handled: n={n} note={note}"
        except Exception as e:
            return f"CRASH: {type(e).__name__}: {e}"

# 2) malformed heartbeat json -> crash? invalid ts -> fabricated now()?
@probe("P2 heartbeat invalid ts / malformed")
def p2():
    out = []
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "hb.json"
        p.write_text('{"ts": "not-a-date", "uptime_s": 1}')
        try:
            n, note = loaders.load_heartbeat(p)
            hb = VpsHeartbeat.objects.order_by("-ts").first()
            out.append(f"invalid-ts: n={n}, latest hb.ts={hb.ts} (fabricated-now? {abs((hb.ts.timestamp()-__import__('time').time()))<60})")
        except Exception as e:
            out.append(f"invalid-ts CRASH: {e}")
        p.write_text('not json{{{')
        try:
            n, note = loaders.load_heartbeat(p)
            out.append(f"malformed: n={n} note={note}")
        except Exception as e:
            out.append(f"malformed CRASH: {type(e).__name__}")
    return " | ".join(out)

# 3) alert bila ts -> fabricated now()?
@probe("P3 alert missing ts")
def p3():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "a.jsonl"
        p.write_text('{"kind":"drift","severity":"WARN","message":"x","dedupe_key":"qa-test-alert"}\n')
        n, note = loaders.load_alerts(p)
        a = Alert.objects.get(dedupe_key="qa-test-alert")
        import time
        return f"n={n}, ts={a.ts} fabricated-now? {abs(a.ts.timestamp()-time.time())<60}"

# 4) mixed pnl_r None + pnl currency -> units mchanganyiko kwenye perf?
@probe("P4 mixed pnl/pnl_r units")
def p4():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "log.jsonl"
        recs = [
            {"kind":"execution","obj":{"id":"exec:qa:1","order_id":"qa:1","pair":"EURUSD","side":"BUY","status":"FILLED","as_of":1767862800,"mode":"paper"}},
            {"kind":"settlement","obj":{"id":"qa:1","realized_pnl":250.0,"as_of":1767884400}},  # currency only, hakuna pnl_r
            {"kind":"execution","obj":{"id":"exec:qa:2","order_id":"qa:2","pair":"EURUSD","side":"BUY","status":"FILLED","as_of":1767862900,"mode":"paper"}},
            {"kind":"settlement","obj":{"id":"qa:2","pnl_r":1.0,"realized_pnl":12.0,"as_of":1767884500}},
        ]
        p.write_text("\n".join(json.dumps(r) for r in recs))
        loaders.load_paper_log(p)
        loaders.rebuild_strategy_perf()
        sp = StrategyPerf.objects.filter(strategy="UNKNOWN", period="ALL").first()
        return f"UNKNOWN perf: n={sp.n_trades} net_r={sp.net_r} expectancy_r={sp.expectancy_r} (250 currency + 1.0 R zimechanganywa?)"

# 5) stale mirror: artifact ikitoweka, re-ingest inaacha data ya zamani DB
@probe("P5 stale mirror after artifact gone")
def p5():
    n_before = Trade.objects.filter(is_demo=True).count()
    with tempfile.TemporaryDirectory() as tmp:
        n, note = loaders.load_paper_log(Path(tmp) / "gone.jsonl")
    n_after = Trade.objects.filter(is_demo=True).count()
    return f"loader='{note}' lakini demo trades DB: {n_before} -> {n_after} (bado zinaonekana panels)"

# 6) AuditEvent append-only bypass kupitia bulk queryset delete
@probe("P6 AuditEvent bulk-delete bypass")
def p6():
    AuditEvent.objects.create(user="qa", action="probe", subject="x")
    n1 = AuditEvent.objects.count()
    try:
        AuditEvent.objects.filter(action="probe").delete()
        n2 = AuditEvent.objects.count()
        return f"BYPASS: bulk delete ilifuta {n1-n2} rekodi (model.delete() haikuitwa)"
    except ValueError:
        return "OK: bulk delete imezuiwa"

# 6b) AuditEvent bulk update bypass
@probe("P6b AuditEvent bulk-update bypass")
def p6b():
    AuditEvent.objects.create(user="qa", action="probe2", subject="x")
    n = AuditEvent.objects.filter(action="probe2").update(detail="TAMPERED")
    ev = AuditEvent.objects.filter(action="probe2").first()
    return f"BYPASS: .update() ilibadilisha {n} rekodi -> detail='{ev.detail}'"

# 7) attestation hash: external verification (recompute bila attest module)
@probe("P7 attestation external verify")
def p7():
    data, canonical = attest.attestation("STRAT-001")
    d = dict(data); h = d.pop("attestation_hash"); d.pop("generated_at")
    recomputed = hashlib.sha256(json.dumps(d, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return f"hash match: {recomputed == h}"

# 8) attestation: je ina commit hash ya provenance?
@probe("P8 attestation commit provenance")
def p8():
    data, _ = attest.attestation("STRAT-001")
    txt = json.dumps(data)
    has_commit = "commit" in txt.lower()
    return f"ina 'commit' provenance field? {has_commit}; keys={sorted(data.keys())}"

for name, res in R:
    print(f"[{name}] {res}")
