# D6 IMPLEMENTATION RULES (Rules 1–8) — Operational Specification

*Spec-text ya Chief Quant #1 (D6 implementation authorization, 2026-07-03) | Status:
**operational specification** — SIYO doctrine, SIYO report (uamuzi wa Chief, Decision Doctrine V11
E-2) | Iliwekwa repo kufunga open item ya V10 (SPEC-TEXT).*

> **Numbering:** hizi ni **Rules 1–8**, SIO principle numbers (principle-numbering reconciliation,
> V10: doctrine-of-record = P90–P106; spec-text ya awali iliyokuwa na labels P92–P102 imebadilishwa
> kuwa Rules — rekodi za kihistoria, mf. `reports/decision_engine_report.md`, hazibadilishwi; mapping
> iko `docs/ARCHITECTURE_AUDIT.md`).

---

## Rules

**Rule 1 — No doctrine changes during coding.**
Ukikwama kwenye doctrine wakati wa implementation, **simama** na ulete amendment kwanza (Chief
review). Coding kamwe si mahali pa kubadilisha doctrine.

**Rule 2 — Compliance checklist kila PR.**
Kila PR ya Engine/D-implementation inabeba compliance checklist. Sasa ni: **Auditor 4-point review**
(engine size · forbidden imports · stateless · policy leakage — V10) + **transitive dependency
purity (P107, V11)**.

**Rule 3 — Engine ndogo.**
Logic yoyote ya maamuzi inahamia **Policy** (P97). Engine ikianza kuwa na helpers/business
logic/caches — architecture inapotoka (P103).

**Rule 4 — Engine inajua TU Snapshot · Policy · Decision Object.**
Hakuna Market/Events/State/Representation/Features (P92). Imports za Engine: `decision_object` +
stdlib PEKEE — na kwa P107, purity inapimwa kwenye **dependency graph nzima**, si direct imports tu.

**Rule 5 — Stateless.**
No cache, no globals, no singleton, no memory.

**Rule 6 — Correctness kwanza.**
Hakuna optimization.

**Rule 7 — Self-test kila sehemu.**
Kila hatua ya implementation ina self-test yake (`--self-test`, haihitaji data ya nje).

**Rule 8 — Report format.**
Deliverable ya kila implementation phase:
`Implementation Report → Self Tests → Known Limitations → Open Questions` — **hakuna conclusions**.

---

*Rejea: `reports/decision_engine_specification.md` (maswali 8 ya D6) · Decision Doctrine V10 (D6
CLOSED; numbering reconciliation) · Decision Doctrine V11 (E-2 approval; P107).*

*Profitable ≠ Tradable Edge. Protect capital first.*
