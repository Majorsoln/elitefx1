"""HTTP-level adversarial probes via Django test client."""
from django.test import Client
from django.contrib.auth.models import Group, User
from django.core.management import call_command
from monitor.models import Lease, Trade

call_command("ingest", "--demo", verbosity=0)
for g in ("internal", "attestor", "lessee"):
    Group.objects.get_or_create(name=g)

def mkuser(n, grp=None, lease=None):
    u = User.objects.create_user(n, password="x")
    if grp: u.groups.add(Group.objects.get(name=grp))
    if lease: Lease.objects.create(user=u, model_id=lease)
    return u

R = []

# 1) read-only: try every HTTP verb that mutates on a panel + attestation
c = Client(); c.force_login(mkuser("op1", "internal"))
for verb in ("post", "put", "patch", "delete"):
    r = getattr(c, verb)("/registry/STRAT-001/attest.json")
    R.append(f"{verb.upper()} attest.json -> {r.status_code}")
for verb in ("post", "put", "delete"):
    r = getattr(c, verb)("/actions/")
    R.append(f"{verb.upper()} /actions/ -> {r.status_code}")

# 2) path traversal on report_view
c2 = Client(); c2.force_login(mkuser("op2", "internal"))
for p in ["reports/../../etc/passwd", "reports/../elitefx_dash/settings.py",
          "../../../etc/passwd", "reports/../../dashboard/manage.py",
          "reports%2f..%2f..%2fetc%2fpasswd"]:
    r = c2.get(f"/reports/{p}")
    R.append(f"traversal '{p}' -> {r.status_code}")

# 3) lessee: leak via attestation of non-leased model, and via report/ledger
les = mkuser("cli1", "lessee", lease="STRAT-001")
c3 = Client(); c3.force_login(les)
for url in ["/registry/STRAT-002/attest.json", "/registry/STRAT-002/attest.pdf",
            "/registry/STRAT-002/", "/reports/reports/demo_report_a.md",
            "/matrix/USDCHF/nr7_break/", "/ledger/", "/audit/"]:
    r = c3.get(url)
    R.append(f"lessee GET {url} -> {r.status_code}")

# 4) lessee can reach attest.json of OWN model (expected 200) — does it leak other strat data?
r = c3.get("/registry/STRAT-001/attest.json")
body = r.content.decode()
R.append(f"lessee own attest.json -> {r.status_code}; mentions STRAT-002? {'STRAT-002' in body}")

# 5) unauthenticated
c4 = Client()
for url in ["/registry/STRAT-001/attest.json", "/deck/"]:
    r = c4.get(url)
    R.append(f"anon GET {url} -> {r.status_code} loc={r.get('Location','-')}")

for line in R:
    print(line)
