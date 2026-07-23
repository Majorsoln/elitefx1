"""
Nav role-awareness (UX fix 2026-07-21): kila role anaona tabs zake TU kwenye nav — lessee
haoni tabs za ndani (zilikuwa zinatoa 403 mbichi akibofya). Read-only; hakuna access-change
(gatekeeping halisi bado iko access.py decorators — hii ni UX layer tu, defence-in-depth).
"""
from .access import PANEL_ROLES, _groups, user_leases

# panel-name -> (url, label) kwa mpangilio wa nav
_NAV = [
    ("deck", "/deck/", "DECK"),
    ("scorecards", "/scorecards/", "SCORECARDS"),
    ("portfolio", "/portfolio/", "PORTFOLIO"),
    ("actions", "/actions/", "ACTIONS"),
    ("compliance", "/compliance/", "COMPLIANCE"),
    ("registry", "/registry/", "REGISTRY"),
    ("matrix", "/matrix/", "MATRIX"),
    ("alerts", "/alerts/", "ALERTS"),
    ("vps", "/vps/", "VPS"),
    ("ledger", "/ledger/", "LEDGER"),
    ("audit", "/audit/", "AUDIT"),
]


def nav(request):
    u = getattr(request, "user", None)
    if not u or not u.is_authenticated:
        return {"nav_panels": [], "is_lessee": False}
    g = _groups(u)
    panels = [dict(name=n, url=url, label=lbl) for (n, url, lbl) in _NAV
              if g & PANEL_ROLES.get(n, {"internal"})]
    is_lessee = not (g & {"internal", "attestor"}) and bool(user_leases(u))
    return {"nav_panels": panels, "is_lessee": is_lessee}
