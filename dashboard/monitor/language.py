"""
language.py — sentensi FUPI za scorecard (trade + English rahisi). DETERMINISTIC (hakuna randomness;
input ile ile -> sentensi ile ile). Read-only helper — hakuna data mutation.
"""

_STATUS = {
    "HOLDS": "inatoa faida kama ilivyoahidi. Iko salama.",
    "LIFTS": "inatoa faida ZAIDI ya ilivyoahidi. Iko juu ya lengo.",
    "SHRINKS": "inatoa chini ya ilivyoahidi (shrinkage). Angalia.",
    "INSUFFICIENT": "bado haina trades za kutosha kuhukumu (sampuli ndogo).",
    "NO-DATA": "bado haijaanza kutrade (hakuna matokeo).",
}


def say(topic, **kw):
    """Sentensi fupi kwa topic:
    - 'status'  : {call, verdict} -> "KAIROS-1 inatoa faida kama ilivyoahidi. Iko salama."
    - 'promise' : {learned, practical, verdict} -> ahadi vs uhalisia
    - 'weakness': {best, worst} -> nguvu/udhaifu kwa lugha ya trade
    - 'compliance': {n, fails} -> sheria
    """
    if topic == "status":
        return f"{kw['call']} {_STATUS.get(kw.get('verdict', 'NO-DATA'), _STATUS['NO-DATA'])}"
    if topic == "promise":
        learned, practical = kw.get("learned"), kw.get("practical")
        if learned is None or practical is None:
            return "Ahadi vs uhalisia haiwezi kupimwa bado (hakuna data ya kutosha)."
        verb = ("juu ya ahadi" if practical > learned else
                "chini ya ahadi" if practical < learned else "sawa na ahadi")
        return f"Iliahidi {learned:+.2f} pips; inatoa {practical:+.2f} — {verb}."
    if topic == "weakness":
        best, worst = kw.get("best"), kw.get("worst")
        if not best and not worst:
            return "Ramani ya udhaifu bado haina cells zenye sampuli ya kutosha."
        parts = []
        if best:
            parts.append(f"Nguvu zaidi {best}")
        if worst:
            parts.append(f"inadhoofu {worst}")
        return "; ".join(parts) + "."
    if topic == "compliance":
        n, fails = kw.get("n", 0), kw.get("fails", 0)
        if n == 0:
            return "Hakuna ukaguzi wa sheria bado."
        if fails == 0:
            return f"Trades zote zilifuata sheria za FTMO ({n} ukaguzi, 0 ukiukaji)."
        return f"{fails} ukiukaji kati ya {n} ukaguzi — angalia sehemu ya sheria."
    return ""
