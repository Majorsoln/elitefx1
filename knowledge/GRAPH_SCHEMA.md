# KNOWLEDGE GRAPH (K2) — Schema Note kwa Review ya Chief

*Builder: RESEARCHER-K | v1-v4 APPROVED (Chief) · v5 = Chief invariant-restore · v6 2026-07-05 (RESEARCHER-K, inasubiri review)*
*Layer: L2 (`ELITEFX MASTER ARCHITECTURE V1.md` §3.4) | File: `knowledge/graph.json` (GRAPH@v6)*

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

## Hali ya sasa (GRAPH@v6, 2026-07-05)

```text
nodes = 159  (lesson 31 · finding 29 · principle 31 · phase 25 · report 31 · doc 4 · record 2 · domain 3 · eval 3)
edges = 191  (derives-from 107 · supports 45 · contradicts 6 · applies-to 33 · supersedes 0)
v2 delta:   +eval:EVAL-001 (ACTIVE) + edges 11 (EVAL-001→k4-evals; 10 lesson→EVAL-001 applies-to)
v3 delta:   +lessons 019-026 (ACTIVE) + provenance zao; 021/022 contradicts (mode=counter-evidence, 0/282 OOS)
v4 delta:   +eval:EVAL-002 (ACTIVE) + edges 8 (→k4-evals + 7 lesson→EVAL-002 applies-to)
v5 delta:   (Chief) +lessons 027-031 (ACTIVE, batch-5 promotion) + provenance nodes 6 — invariant restore
v6 delta:   (RESEARCHER-K juu ya v5) +eval:EVAL-SUITE (→k4-evals; EVAL-001/002 member — OQ-G6) +
            3 edges lesson→EVAL-002 (027/028/029 = T06/T11/T12). 027-031 provenance ya Chief HAIJAGUSWA
            (enrichment supports/contradicts = pendekezo kwa Chief — OQ-G6)
self-test:  python3 knowledge/graph_selftest.py  (stdlib pekee, haihitaji data — R-1 mitigation)
            inakagua: unique ids · edge integrity · kila lesson ina provenance edge ·
            lifecycle inalingana na LESSON_INDEX · report/doc/eval files zipo repo
```

**Invariant (imethibitishwa na Chief 2026-07-05):** graph LAZIMA iwe na kila lesson **ACTIVE**;
CANDIDATE (017/018 OOS-gate + 032-036 batch 6) zinasubiri approval — zinalinkwa zikiapruvishwa.
Lessons zote 31 ACTIVE zimo; 032-036 = pending (self-test inaziorodhesha).

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
