# LESSON SPECIFICATION (K0) — Canonical Knowledge Object

*Master Architecture V1 §3 | Owner: Chief Quant (Unified) | Status: ACTIVE (2026-07-04)*

Lesson = knowledge object **immutable · versioned · provenance-linked**, inayotokana na rekodi ya
mradi (finding/phase/dead-end/execution outcome), iliyoandikwa kwa format ambayo binadamu NA model
wanaweza kujifunza. Ndugu wa nne wa Evidence/Decision/Execution objects (pattern ya P93).

## Schema (fields zote LAZIMA isipokuwa zilizoandikwa optional)

```yaml
id: LESSON-###@vN          # namba ya kudumu + version (P88-style: content change = version mpya)
claim: <sentensi MOJA, English>   # corpus consistency; isiyo na hedging wala hype
type: METHOD | MARKET-CONDITIONAL | GOVERNANCE
evidence:                   # rekodi halisi + NAMBA (si maneno matupu)
  - <report/phase ref: kipimo halisi>
counter_evidence: <lazima itafutwe; "none found (scope: ...)" inakubalika, kutokuwepo si default>
validity_conditions:        # METHOD: "general (demonstrated on ...)"; MARKET: pairs/period/regime/cost
when_to_use: <hali halisi ambazo lesson hii inaongoza uamuzi>
when_not_to_use: <mipaka ya ukweli wake — SEHEMU MUHIMU KULIKO ZOTE (inafundisha reasoning, si rule)>
provenance: {finding: F-###, phase: <#>, doctrine: <V#>, principle: P## }   # angalau moja
lifecycle: CANDIDATE | VALIDATED | ACTIVE | SUPERSEDED | CONTESTED | RETIRED
review_trigger: <optional; LAZIMA kwa MARKET-CONDITIONAL — muda/regime/event inayolazimisha re-check>
supersedes / superseded_by: <optional — ids>
```

## Sheria za corpus

1. **Kamwe usifute** — SUPERSEDED/RETIRED na links; history ni sehemu ya elimu.
2. **METHOD ≠ MARKET** — MARKET lesson bila `validity_conditions` + `review_trigger` = invalid
   (tunakataa kufundisha maiti — P27).
3. **Mgongano**: conditions tofauti = context-dependence (halali, zote zinaishi); conditions
   zilezile = zote CONTESTED → research question (S4 Contradiction Lab).
4. **Value test**: lesson ina thamani ikiwa ina-change design ya kazi ijayo au ina-prevent dead end
   kurudiwa — inapimwa kwa **citations** (specs/reviews/phases zinazoitaja).
5. **Lifecycle gate**: CANDIDATE→VALIDATED inahitaji: evidence refs zipo na zinakaguliwa; counter-
   evidence imetafutwa; type + conditions sahihi. VALIDATED→ACTIVE = kuingizwa INDEX na kutumika.
6. Kila lesson mpya inaingia `LESSON_INDEX.md` (registry) siku ile ile.
