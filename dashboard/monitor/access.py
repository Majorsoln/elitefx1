"""
Roles / leasing foundation (V2 §5.4 separation):
  internal  — panels ZOTE.
  attestor  — compliance + registry + attestation (ukaguzi wa nje).
  lessee    — registry-card + attestation ya model MOJA aliyokodishwa (Lease) PEKEE.
Decorators ni READ-ONLY gatekeeping — hazibadilishi chochote (isipokuwa AuditEvent append).
"""
from functools import wraps

from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required

from .models import AuditEvent, Lease

PANEL_ROLES = {
    # panel-name -> groups zinazoruhusiwa (internal daima)
    "deck": {"internal"},
    "portfolio": {"internal"},
    "actions": {"internal"},
    "compliance": {"internal", "attestor"},
    "registry": {"internal", "attestor"},          # lessee: kupitia leased-model check tofauti
    "matrix": {"internal"},
    "alerts": {"internal"},
    "vps": {"internal"},
    "ledger": {"internal"},
    "audit": {"internal", "attestor"},
}


def _groups(user):
    return set(user.groups.values_list("name", flat=True)) | ({"internal"} if user.is_superuser else set())


def user_leases(user):
    return set(Lease.objects.filter(user=user).values_list("model_id", flat=True))


def panel_access(panel):
    """Decorator ya panel ya jumla: internal (+attestor kwa compliance/registry/audit)."""
    def deco(view):
        @wraps(view)
        @login_required
        def wrapped(request, *args, **kwargs):
            if _groups(request.user) & PANEL_ROLES.get(panel, {"internal"}):
                return view(request, *args, **kwargs)
            raise PermissionDenied(f"role haina access ya panel '{panel}'")
        return wrapped
    return deco


def model_access(view):
    """Decorator ya model-scoped views (registry detail + attestation): internal/attestor = zote;
    lessee = model aliyokodishwa TU (Lease). Attestation views zinarekodiwa AuditEvent (append-only)."""
    @wraps(view)
    @login_required
    def wrapped(request, model_id, *args, **kwargs):
        g = _groups(request.user)
        if not (g & {"internal", "attestor"}) and model_id not in user_leases(request.user):
            raise PermissionDenied("lessee: access ni ya model uliyokodisha PEKEE")
        return view(request, model_id, *args, **kwargs)
    return wrapped


def audit(request, action, subject, detail=""):
    AuditEvent.objects.create(user=request.user.username, action=action,
                              subject=subject, detail=detail[:390])
