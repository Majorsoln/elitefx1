"""
language.py — sentensi FUPI za scorecard (trade + English rahisi). DETERMINISTIC (hakuna randomness;
input ile ile -> sentensi ile ile). Read-only helper — hakuna data mutation.

DASHBOARD-V2 Awamu 4 (R3): say() = Kiswahili (kama zamani, backward-compat); say_both() = {sw, en}
kwa mistari MIWILI (SW juu, EN chini). English ni rahisi (si jargon).
"""

_STATUS = {
    "HOLDS": "inatoa faida kama ilivyoahidi. Iko salama.",
    "LIFTS": "inatoa faida ZAIDI ya ilivyoahidi. Iko juu ya lengo.",
    "SHRINKS": "inatoa chini ya ilivyoahidi (shrinkage). Angalia.",
    "INSUFFICIENT": "bado haina trades za kutosha kuhukumu (sampuli ndogo).",
    "NO-DATA": "bado haijaanza kutrade (hakuna matokeo).",
}

_STATUS_EN = {
    "HOLDS": "is delivering the profit it promised. It is on track.",
    "LIFTS": "is delivering MORE profit than promised. Above target.",
    "SHRINKS": "is delivering less than promised (shrinkage). Watch it.",
    "INSUFFICIENT": "does not have enough trades to judge yet (small sample).",
    "NO-DATA": "has not started trading yet (no results).",
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


def say_en(topic, **kw):
    """English rahisi (SI jargon) — sambamba na say() ya Kiswahili. DETERMINISTIC."""
    if topic == "status":
        return f"{kw['call']} {_STATUS_EN.get(kw.get('verdict', 'NO-DATA'), _STATUS_EN['NO-DATA'])}"
    if topic == "promise":
        learned, practical = kw.get("learned"), kw.get("practical")
        if learned is None or practical is None:
            return "Promise vs reality cannot be measured yet (not enough data)."
        verb = ("above promise" if practical > learned else
                "below promise" if practical < learned else "on promise")
        return f"Promised {learned:+.2f} pips; delivering {practical:+.2f} — {verb}."
    if topic == "weakness":
        best, worst = kw.get("best"), kw.get("worst")
        if not best and not worst:
            return "The weakness map has no cells with a large enough sample yet."
        parts = []
        if best:
            parts.append(f"Strongest at {best}")
        if worst:
            parts.append(f"weakest at {worst}")
        return "; ".join(parts) + "."
    if topic == "compliance":
        n, fails = kw.get("n", 0), kw.get("fails", 0)
        if n == 0:
            return "No rule checks yet."
        if fails == 0:
            return f"All trades followed the FTMO rules ({n} checks, 0 breaches)."
        return f"{fails} breaches out of {n} checks — see the rules section."
    return ""


def say_both(topic, **kw):
    """R3: rudi {sw, en} kwa mistari MIWILI. DETERMINISTIC (say + say_en)."""
    return {"sw": say(topic, **kw), "en": say_en(topic, **kw)}
