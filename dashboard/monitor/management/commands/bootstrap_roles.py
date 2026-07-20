"""
`python manage.py bootstrap_roles [--demo-users]` — groups za leasing foundation (V2 §5.4).

Groups: internal / attestor / lessee. --demo-users: watumiaji wa demo (nywila = jina + '-demo')
+ lease ya STRAT-001 kwa lessee-demo. Production: users wanaundwa na admin, si command hii.
"""
from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand

from monitor.models import Lease

GROUPS = ("internal", "attestor", "lessee")


class Command(BaseCommand):
    help = "Unda groups (internal/attestor/lessee); --demo-users kwa demo login."

    def add_arguments(self, parser):
        parser.add_argument("--demo-users", action="store_true")

    def handle(self, *args, **opts):
        for g in GROUPS:
            Group.objects.get_or_create(name=g)
        self.stdout.write("groups: " + ", ".join(GROUPS))
        if opts["demo_users"]:
            for name in GROUPS:
                u, created = User.objects.get_or_create(username=f"{name}-demo")
                if created:
                    u.set_password(f"{name}-demo")
                    u.save()
                u.groups.add(Group.objects.get(name=name))
            lessee = User.objects.get(username="lessee-demo")
            Lease.objects.get_or_create(user=lessee, model_id="STRAT-001")
            self.stdout.write(self.style.SUCCESS(
                "demo users: internal-demo / attestor-demo / lessee-demo (nywila = username); "
                "lessee-demo ana lease ya STRAT-001"))
