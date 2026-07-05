# KNOWLEDGE GRAPH (K2) — Schema Note kwa Review ya Chief

*Builder: RESEARCHER-K | v1 2026-07-04 (APPROVED Chief 2026-07-04) · v2 2026-07-05 (inasubiri review)*
*Layer: L2 (`ELITEFX MASTER ARCHITECTURE V1.md` §3.4) | File: `knowledge/graph.json` (GRAPH@v2)*

## Kanuni za ujenzi (zilizofuatwa)

1. **Hakuna node/edge isiyo na rekodi** — kila edge ina field `source` (file ya repo ambako
   uhusiano umeandikwa); nodes zote zinatoka kwenye provenance/evidence/counter_evidence za
   lessons 18 za `LESSON_INDEX.md`. Hakuna kitu kilichobuniwa.
2. **Granularity = kama ilivyoandikwa** — range ids (mf. `principle:P53-P57`, `phase:9-11`)
   zimehifadhiwa jinsi provenance ya lesson ilivyoziandika; normalization ni uamuzi wa Chief (OQ-G2).
3. **Edge types 5 za Master Architecture §3.4 pekee**: `derives-from` · `supports` ·
   `contradicts` · `supersedes` (bado 0) · `applies-to`. OQ-G3 APPROVED: hakuna type mpya bila
   amendment — hivyo lesson→eval ni `applies-to` (note=tested-by-QNN), si type mpya.
4. **counter_evidence → `contradicts` yenye `mode`**: `counter-evidence` (inapinga claim moja kwa
   moja — mf. Phase 14 0/282 dhidi ya LESSON-017/018) au `bounds` (inaweka mipaka bila kubatilisha —
   mf. F-016 dhidi ya LESSON-005). Tofauti hii inafuata LESSON_SPEC corpus rule 3.

## Hali ya sasa (GRAPH@v2, 2026-07-05)

```text
nodes = 111  (lesson 18 · finding 23 · principle 21 · phase 18 · report 21 · doc 4 · record 2 · domain 3 · eval 1)
edges = 135  (derives-from 78 · supports 34 · contradicts 4 · applies-to 19 · supersedes 0)
v2 delta:   +eval:EVAL-001 (L4, ACTIVE) + edges 11 (EVAL-001→k4-evals; 10 lesson→EVAL-001 applies-to)
self-test:  python3 knowledge/graph_selftest.py  (stdlib pekee, haihitaji data — R-1 mitigation)
            inakagua: unique ids · edge integrity · kila lesson ina provenance edge ·
            lifecycle inalingana na LESSON_INDEX · report/doc/eval files zipo repo
```

**Haijaingia bado (kwa makusudi):** lessons 019-026 (batch 4, CANDIDATE) — zitalinkwa graph baada
ya Chief approval, sawa na jinsi EVAL-001 ilisubiri approval kabla ya kulinkwa (uthabiti wa mchakato).

## Rulings za Chief (OQ-G1..G5 — APPROVED 2026-07-04, zote kwa mapendekezo yangu)

| # | Ruling |
|---|--------|
| OQ-G1 | Doctrine versions SIO nodes v1/v2 — zibaki ndani ya lessons (K3 itafikiria) |
| OQ-G2 | Range-ids kugawanywa kwa batch maalum ya board definitions (sio kubuni) |
| OQ-G3 | `contradicts`+`mode` inabaki; hakuna edge type mpya bila amendment ya §3.4 |
| OQ-G4 | Domain taxonomy: anza na 3 zilizopo; Chief ataipanua na K3/K4 mahitaji halisi |
| OQ-G5 | Truths/Failed-Ideas → graph BAADA ya kuwa lessons (single source of truth) |

## Matumizi yaliyokusudiwa (K5 order: EVAL → RAG → SFT)

Retrieval kwa RAG: anzia lesson node → fuata `derives-from` kupata rekodi → `supports` kupata
namba → `contradicts` kupata mipaka. Edges za `applies-to` (lesson→lesson mf. LESSON-009 →
LESSON-017/018 review gate; lesson→`eval:EVAL-001` = "tested-by") ndizo zinazofanya corpus kuwa
mfumo, sio orodha — na zinaunganisha L1 (lessons) na L4 (evals).
