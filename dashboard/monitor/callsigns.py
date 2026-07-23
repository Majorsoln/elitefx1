"""
callsigns.py — anonymization foundation (DASHBOARD-V2 §9): public call-sign <-> internal model id.

Public call-sign (KAIROS-1/2) ndio pekee lessee/attestor wanaona (Awamu 3). Internal id (STRAT-001/002)
+ pair = SIRI ya server — mapping HII haipiti kwa client kamwe (view inaramanisha server-side).
PUBLIC_META ina version/status TU — HAKUNA pair/logic/params (IP protection §9).
"""

CALLSIGNS = {"STRAT-001": "KAIROS-1", "STRAT-002": "KAIROS-2"}   # internal -> public
_INV = {v: k for k, v in CALLSIGNS.items()}                     # public -> internal

# public metadata (call-sign -> {version, status}) — BILA pair/logic/params (anonymization)
PUBLIC_META = {
    "KAIROS-1": {"version": "v1.0", "status": "PAPER"},
    "KAIROS-2": {"version": "v1.0", "status": "PAPER"},
}


def to_public(internal_id):
    """Internal id (STRAT-001) -> public call-sign (KAIROS-1). Isiyojulikana -> yenyewe (fail-open label)."""
    return CALLSIGNS.get(internal_id, internal_id)


def to_internal(call_sign):
    """Public call-sign (KAIROS-1) -> internal id (STRAT-001). Isiyojulikana -> None (404 upstream)."""
    return _INV.get(call_sign)


def public_meta(call_sign):
    return PUBLIC_META.get(call_sign, {"version": "?", "status": "?"})
