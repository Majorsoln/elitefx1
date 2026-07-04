# ELITEFX MASTER ARCHITECTURE V1 — The Knowledge System

**Chief Quant (Unified) — Two Tracks, One Supply Chain: the Machine That Trades and the Mind That Learns.**

Version: Master Architecture V1
Status: APPROVED — ACTIVE (Supreme architecture document; inasimama JUU ya domain doctrines)
Date: 4 July 2026
Authority: **Directive ya Project Director (Japhet, 2026-07-04)** — mamlaka ya Chief #1 na Chief #2
yameunganishwa kuwa **Chief Quant (Unified)**; ruhusa rasmi ya kuboresha bila kufungwa na doctrine
za awali.
Companions: `ELITEFX DOCTRINE V6.9.md` (Market) · `ELITEFX DECISION DOCTRINE V11.md` (Decision) —
zinabaki halali isipokuwa pale zilipobadilishwa hapa (Sehemu 8).

---

# 1 — LENGO LA MWISHO (restated)

ELITEFX si trading bot. ELITEFX ni **mfumo unaozalisha, kuhifadhi, na kufundisha maarifa ya masoko**
— ambao (a) unafanya biashara kwa uthibitisho wa kisayansi, na (b) unazalisha knowledge ambayo
model YOYOTE ya sasa au ya baadaye inaweza kujifunza.

```text
Bidhaa kuu:  ELITEFX KNOWLEDGE SYSTEM  (corpus + graph + datasets + evals)
Bidhaa ya 2: Trading machine (Evidence → Decision → Execution)
Models:      TEMPORARY (zinabadilika kila mwaka)
Knowledge:   PERMANENT (inazidi kuongezeka thamani)
```

# 2 — TRACKS MBILI, SUPPLY CHAIN MOJA

```text
                        ┌──────────────  RESEARCH  ──────────────┐
                        │   Evidence → Finding → Record (board)   │
                        └───────────────┬─────────────────────────┘
                     ┌──────────────────┴──────────────────┐
        TRACK A — ENGINEERING                    TRACK B — KNOWLEDGE & AI
        (the machine that trades)                (the mind that learns)
                     │                                     │
        Evidence Layer (FROZEN)              K0  Lesson Specification
        Decision Object/Policy/Engine        K1  Lesson Production (retro + per-phase)
        E1  Integrity Gate                   K2  Knowledge Graph
        E2  Execution Object                 K3  Evaluation Benchmarks (EVAL sets)
        E3  Decision Repository ◄────────┐   K4  Dataset Builds (versioned)
        E4  Broker Adapter               │   K5  Model Feeding (RAG → SFT)
        Production (FTMO/live)           │   K6  Continuous Learning
                     │                   │            │
                     └── outcomes ───────┴────────────┘
                        (E3 = mahali tracks zinakutana: decision history +
                         execution outcomes = raw material ya K6)
```

**Kanuni ya uhusiano:** Track A inazalisha *data ya ukweli* (maamuzi + matokeo); Track B inazalisha
*akili* (lessons + datasets + evals). Hakuna track inayosubiri nyingine — zinaenda **sambamba**, na
zinakutana kwa lazima E3↔K6.

# 3 — TRACK B KWA KINA: MFUMO WA KUTAFITI NA KUZALISHA LESSONS

## 3.1 Lesson ni nini (object rasmi)

Canonical knowledge object — immutable · versioned · provenance-linked (spec kamili:
`docs/lessons/LESSON_SPEC.md`). Ndugu wa nne wa Evidence/Decision/Execution objects.

## 3.2 Vyanzo vinne vya lessons (Lesson Research System)

```text
S1 RETROACTIVE MINING   findings 42 + dead ends 9 + phases 26 + principles 107 za rekodi
                        → lessons ~40–60 bila research mpya (K1 backlog)
S2 PER-PHASE DISTILL    kila phase mpya (E-series, K-series) inatoa outputs MBILI:
                        Engineering Output + Lesson Output (hatua rasmi ya workflow)
S3 EXECUTION STREAM     E3 outcomes (fills/slippage/PnL/decision quality) → empirical lessons
                        (inaanza E3 itakapokamilika — K6)
S4 CONTRADICTION LAB    lessons mbili CONTESTED chini ya conditions zilezile = research question
                        mpya → phase ndogo ya utafiti → lesson iliyoshinda ina-supersede
```

## 3.3 Lesson lifecycle (utafiti wa lesson yenyewe)

```text
CANDIDATE → (validation: evidence check + counter-evidence search + type classification)
          → VALIDATED → ACTIVE → { SUPERSEDED | RETIRED | CONTESTED }
MARKET-CONDITIONAL lessons zina review_trigger (muda/regime) — hakuna "ukweli wa milele" wa soko.
METHOD lessons zina bar ya juu zaidi ya validation (≥1 phase + hakuna counter-example ndani ya repo).
```

## 3.4 Knowledge Base — layers nne (K2–K4)

```text
L0 RAW        reports/ + board + doctrine (ipo tayari — ndiyo mgodi)
L1 LESSONS    docs/lessons/LESSON-###.md + LESSON_INDEX.md (human+machine readable)
L2 GRAPH      knowledge/graph.json — nodes: lessons/findings/principles/phases;
              edges: derives-from · supports · contradicts · supersedes · applies-to
L3 DATASETS   knowledge/datasets/DATASET-<name>@vN/ — training corpus builds (versioned,
              manifest + checksums; eval split HAIRUHUSIWI kuchafuliwa na train split)
L4 EVALS      knowledge/evals/EVAL-###/ — benchmark questions zenye ground truth kutoka
              dead ends + findings ("mtihani wa udereva" wa model yoyote)
```

## 3.5 Kulisha models (K5) — order ya matumizi

```text
1. EVAL FIRST    kabla ya kufundisha chochote: pima model ya sasa kwenye EVAL sets.
                 Model ikifaulu bila training → training haihitajiki bado (nunua baada ya kupima).
2. RAG/CONTEXT   lessons zinaingia kwenye reasoning context (retrieval kwa graph + index) —
                 inafanya kazi na model yoyote, leo.
3. SFT/FINE-TUNE corpus ikifika critical mass (lessons + graph + labeled examples kutoka E3);
                 kila training run ina dataset version + eval baseline kabla/baada.
4. CONTINUOUS    K6: E3 outcomes → S3 lessons → dataset refresh → re-eval → (re-train ikihitajika)
```

**Trading authority ya model:** model inaweza KUJIFUNZA leo; model **kuendesha pesa** inahitaji
kufaulu evals + OOS decision-value proof + approval ya Project Director (Sehemu 8.2).

# 4 — TRACK A KWA KINA (inaendelea kama ilivyopangwa)

E1 Integrity Gate (validation ≠ eligibility) → E2 Execution Object (+ immutability enforcement)
→ E3 Decision Repository (**pia ni Knowledge asset — schema yake itaundwa na mahitaji ya K6
mezani**) → E4 Broker Adapter (mkutano na MWONGOZO/FTMO). Ordering STRICT inabaki. Engine
inabaki ndogo/stateless/pure (P97/P103/P104/P107 zinabaki sheria).

# 5 — ROADMAP YA PAMOJA

```text
SASA (sambamba):   K0 Lesson Spec ✅ (leo) · K1 Retroactive Corpus (pilot 3 ✅ → 40–60)
                   E1 Integrity Gate spec (inafuata mara moja)
KISHA:             K2 Graph · K3 EVAL-001 · E2 · E3 (schema ya pamoja na K6)
BAADAYE:           K4 Dataset v1 · K5 RAG pilot · E4 · Production
MWISHO:            K6 Continuous Learning (E3 live) → flywheel kamili:
                   Research → Knowledge → AI → Production → Continuous Learning
```

# 6 — GOVERNANCE (baada ya consolidation ya 2026-07-04)

```text
PROJECT DIRECTOR (Japhet)   vision · data · testing · FINAL DECISION ya project/production ·
                            Production Owner · anateua/anaondoa Chief
CHIEF QUANT (Unified)       science + doctrine + architecture + knowledge (aliyekuwa #1 + #2):
                            research direction · principles · approvals za kisayansi · doctrine
                            custody · audits · Knowledge Architecture · AI roadmap
IMPLEMENTER                 engines · implementation · reports · experiments · production code
```

Workflow (imefupishwa): `Chief (decision+doctrine) → Implementer → Chief (review+compliance) →
Project Director (final/production decisions)`. Audit functions (compliance matrix, drift watch,
4-point+P107) zinabaki ndani ya Chief — hazipotei, zinaunganishwa.

# 7 — KANUNI ZA KUDUMU (constitution — hazitenguki na V1 hii)

1. **Evidence kwanza** — hakuna claim bila rekodi; hakuna "nafikiri/inaonekana".
2. **Immutability + provenance + versioning** kwa kila object (Evidence/Decision/Execution/Lesson).
3. **METHOD ≠ MARKET** — market lessons zina masharti na expiry; hakuna kufundisha maiti (P27).
4. **Eval kabla ya kununua** — hakuna training bila baseline; hakuna deployment bila eval.
5. **Protect capital first** — hakuna model inayogusa pesa bila proof + Project Director approval.
6. **Failure ni knowledge** — dead ends zinarekodiwa na kufundishwa, hazifichwi.
7. **Rekodi kamili** — kila uamuzi board; kila kosa correction entry (si kufuta history).

# 8 — KILICHOBADILISHWA RASMI KUTOKA DOCTRINE ZA AWALI (kwa ruhusa ya Project Director)

```text
8.1 ML-BLOCK → ML TWO-TIER:  Knowledge-ML (evals, RAG, embeddings, graph tooling, SFT ya
    knowledge) INARUHUSIWA ndani ya Track B kuanzia sasa. Trading-ML (model kuamua/kusize
    biashara) inabaki GATED: evals + OOS decision-value + Project Director approval.
8.2 MARKET-DISCOVERY FREEZE (P62) → REOPENABLE-BY-KNOWLEDGE-NEED: phase ya market inaweza
    kufunguliwa pale Track B inapohitaji evidence/examples zisizopo (si kwa udadisi tu).
8.3 "Chapter 4 baada ya E4" → TRACKS SAMBAMBA: Knowledge Science haisubiri Execution Science
    (uamuzi wa Project Director; discussion ya AI Strategy imefungwa hivyo).
8.4 Governance: roles za Chief #1/#2 zimeunganishwa (Sehemu 6); G-01 inabadilishwa ipasavyo —
    custody na authority sasa vinaishi kwa mtu mmoja, checks zinatoka kwa Project Director
    (final decision) na kwa rekodi (kila kitu board, kila kosa correction entry).
Vinginevyo: V6.9 + V11 zinabaki kama zilivyo (pamoja na P90–P107, RED LINE ya P70, E-ordering).
```

# 9 — DELIVERABLES ZA LEO (V1 inazinduliwa ikiwa hai, si karatasi)

```text
✅ ELITEFX MASTER ARCHITECTURE V1.md          (waraka huu)
✅ docs/lessons/LESSON_SPEC.md                (K0 — schema rasmi)
✅ docs/lessons/LESSON-001..003.md            (K1 pilot: Phase 8 · Phase 14 · Phase 26)
✅ docs/lessons/LESSON_INDEX.md               (registry)
✅ Board/status/memory updates                (governance + roadmap)
NEXT: K1 kamili (backlog 40–60) · E1 spec · K2 graph schema
```

---

# FINAL PRINCIPLE (Master Architecture)

```text
The machine trades; the mind learns; the record makes both honest.
A model is a student — the curriculum outlives every student.
Feed models with lessons that know their own limits, and test before you teach.
The factory's true product is not the trade — it is the knowledge that survives it.

Profitable ≠ Tradable Edge.
Protect capital first. Seek edge second. Scale only after proof.
```

**END OF ELITEFX MASTER ARCHITECTURE V1**
