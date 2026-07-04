# KNOWLEDGE GRAPH (K2) — Schema Note kwa Review ya Chief

*Builder: RESEARCHER-K | 2026-07-04 | Status: **DRAFT — inasubiri review ya Chief Quant (Unified)***
*Layer: L2 (`ELITEFX MASTER ARCHITECTURE V1.md` §3.4) | File: `knowledge/graph.json` (GRAPH@v1)*

## Kanuni za ujenzi (zilizofuatwa)

1. **Hakuna node/edge isiyo na rekodi** — kila edge ina field `source` (file ya repo ambako
   uhusiano umeandikwa); nodes zote zinatoka kwenye provenance/evidence/counter_evidence za
   lessons 18 za `LESSON_INDEX.md`. Hakuna kitu kilichobuniwa.
2. **Granularity = kama ilivyoandikwa** — range ids (mf. `principle:P53-P57`, `phase:9-11`)
   zimehifadhiwa jinsi provenance ya lesson ilivyoziandika; normalization ni uamuzi wa Chief (OQ-G2).
3. **Edge types 5 za Master Architecture §3.4 pekee**: `derives-from` · `supports` ·
   `contradicts` · `supersedes` (bado 0 — hakuna @v2 yoyote) · `applies-to`.
4. **counter_evidence → `contradicts` yenye `mode`**: `counter-evidence` (inapinga claim moja kwa
   moja — mf. Phase 14 0/282 dhidi ya LESSON-017/018) au `bounds` (inaweka mipaka bila kubatilisha —
   mf. F-016 dhidi ya LESSON-005). Tofauti hii inafuata LESSON_SPEC corpus rule 3.

## Hali ya sasa (GRAPH@v1)

```text
nodes = 110  (lesson 18 · finding 23 · principle 21 · phase 18 · report 21 · doc 4 · record 2 · domain 3)
edges = 124  (derives-from 78 · supports 34 · contradicts 4 · applies-to 8 · supersedes 0)
self-test:  python3 knowledge/graph_selftest.py  (stdlib pekee, haihitaji data — R-1 mitigation)
            inakagua: unique ids · edge integrity · kila lesson ina provenance edge ·
            lifecycle inalingana na LESSON_INDEX · report/doc files zipo repo
```

## Maswali 5 kwa Chief (yamo pia `graph.json` meta.open_questions_for_chief)

| # | Swali | Pendekezo la RESEARCHER-K |
|---|-------|---------------------------|
| OQ-G1 | Doctrine versions (V5.21, V9, V11…) ziwe nodes? | Hapana kwa v1 — zibaki ndani ya lesson files (compounds/ranges nyingi = bloat); zifikiriwe na K3 |
| OQ-G2 | Principle/phase RANGE ids zigawanywe? | Ndiyo, lakini kwa batch maalum ya kuchimba board definitions — sio kwa kubuni sasa |
| OQ-G3 | `contradicts(mode=bounds)` au edge type mpya `bounds`? | Kubaki na `contradicts`+`mode` (types 5 za §3.4 zisiongezwe bila amendment) |
| OQ-G4 | Ontology ya `domain` nodes (applies-to targets) | Chief aamue taxonomy; v1 ina 3 tu (contract-components, k3-datasets, k4-evals) |
| OQ-G5 | Permanent Truths 12 + Failed Ideas 9 ziingie kama nodes? | Baada ya kuwa lessons (K1 backlog 1–2) — graph isiwe na vitu viwili vya ukweli mmoja |

## Matumizi yaliyokusudiwa (K5 order: EVAL → RAG → SFT)

Retrieval kwa RAG: anzia lesson node → fuata `derives-from` kupata rekodi → `supports` kupata
namba → `contradicts` kupata mipaka. Edges za `applies-to` kati ya lessons (mf. LESSON-009 →
LESSON-017/018 review gate) ndizo zinazofanya corpus kuwa mfumo, sio orodha.
