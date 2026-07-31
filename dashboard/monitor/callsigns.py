"""
callsigns.py — anonymization foundation (DASHBOARD-V2 §9): public call-sign <-> internal model id.

Public call-sign (KAIROS-1/2) ndio pekee lessee/attestor wanaona (Awamu 3). Internal id (STRAT-001/002)
+ pair = SIRI ya server — mapping HII haipiti kwa client kamwe (view inaramanisha server-side).
PUBLIC_META ina version/status TU — HAKUNA pair/logic/params (IP protection §9).
"""

def _load_from_yaml():
    """config/models.yaml = CHANZO KIMOJA (PD anahariri BILA code). Haipo/mbovu -> fallback."""
    import os
    from pathlib import Path
    root = Path(os.environ.get("ELITEFX_REPO_ROOT", Path(__file__).resolve().parents[3]))
    p = root / "config" / "models.yaml"
    try:
        import yaml
        doc = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        m = doc.get("models") or {}
        cs = {k: v["call_sign"] for k, v in m.items() if v.get("call_sign")}
        meta = {v["call_sign"]: {"version": str(v.get("version", "v1.0")),
                                 "status": str(v.get("status", "PAPER"))}
                for v in m.values() if v.get("call_sign")}
        return (cs, meta) if cs else (None, None)
    except Exception:
        return None, None


_YAML_CS, _YAML_META = _load_from_yaml()
CALLSIGNS = _YAML_CS or {"STRAT-001": "KAIROS-1", "STRAT-002": "KAIROS-2"}   # internal -> public
_INV = {v: k for k, v in CALLSIGNS.items()}                     # public -> internal

# public metadata (call-sign -> {version, status}) — BILA pair/logic/params (anonymization)
PUBLIC_META = _YAML_META or {
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
