# PROJECT_MEMORY.md — ELITEFX Institutional Memory

> **Owner: Chief Quant #2** (Doctrine Custodian — G-01). Ina-update **baada ya kila approval**.
> Hii ni **synthesis** ya kumbukumbu (lessons learned · dead ends · permanent truths · timeline);
> rekodi ya msingi (findings/questions/approvals kamili) inabaki `docs/PROGRAM_BOARD.md`.
> Last updated: 2026-07-03.

---

## 1 — Timeline (eras)

| Kipindi | Era | Kilichotokea |
|---------|-----|--------------|
| 2026-06-23 → 06-30 | **Chapter One — Market Science** (Phases 0–26) | States → Age/Transition → Context → Events → Payoff → Configurations → Confidence/Opportunity → Edge Lifecycle → Reality tests → Representations/Geometry → Semantics → Primitives → Ecology → Decision Value. Mwisho: **Prediction ≠ Decision ≠ Explanation** (0/9 Selection-DV OOS). |
| 2026-06-30 | **THE SPLIT** | Market Doctrine V6.9 (FROZEN — P62) + Decision Doctrine V1; Decision Science inaanza **Evidence-first** (Evidence Object = API kati ya domains — P63). |
| 2026-06-30 → 07-03 | **Decision Architecture Era** (D0–D6) | Evidence Object → Operations → Sets → Snapshots (**EVIDENCE LAYER FROZEN**) → Decision Object → Policy (@v2) → Engine (functions 2, stateless, import-pure). D6 CLOSED = "implementation iliyokataa kuwa ngumu". |
| 2026-07-03 | **Chapter 3 — Execution Science OPENED** | E1 Integrity Gate → E2 Execution Object → E3 Decision Repository → E4 Broker Adapter (spec-first; STRICT ordering). E1 inasubiri Chief Directive. |
| 2026-07-03 | **Governance maturation** | Chief Quant #2 onboarded (Scientific Reviewer → **Doctrine Custodian & Architecture Governor**, G-01); P107 (transitive purity) kutoka OBS-1; doctrine archive; two-Chief structure yenye final authority MOJA. |

---

## 2 — Permanent Truths (doctrine-grade; zimefungwa kwa evidence)

1. **Prediction, Decision, na Explanation ni dimensions huru** — variable inaweza kutabiri na kueleza bila kubadilisha decision (P58; Phase 26).
2. **Edge ni non-stationary; kila edge ina lifecycle** (birth→growth→decay→death) — median survival 1/6 windows; market yenyewe inaua persistence (F-028/F-029).
3. **Bad configurations zinadumu kuliko good** (train−→− ≈66% vs train+→+ ≈42%) → mfumo unaanza kwa **remove-bad-first**, sio find-good-first (F-022 CORE; P26).
4. **Hakuna universal events — context ni IDENTITY ya event**, sio filter ya baadaye (F-030/F-031; edge ilipatikana EURUSD-only kwenye Phase 12).
5. **Context ni payoff filter, sio probability filter** — ΔP(win) ndogo (+3pp), ΔEV kubwa (+4 pips); uplift unatoka payoff asymmetry (F-010; mechanisms mbili: reward expansion / loss compression — F-011).
6. **Edge huishi kwenye Event × Configuration**, kamwe si event pekee (F-020/F-021; atomic unit = Configuration).
7. **Representation inaweza kufeli wakati structure ipo** (F-033) — na **context refinement inaongeza apparent edge NA false-discovery risk pamoja** (F-032: candidates 30 → 0 baada ya BH-FDR).
8. **Early edge quality haitabiri future persistence** (causal ρ≈0.03 — F-027); environment haielezi decay (Phase 10).
9. **Volume bars zinaongeza information density, sio stability** (F-007 vs R-002); Information Density > Calendar Uniformity.
10. **Ranking > classification; selection > prediction** (F-023; P21/P23); confidence ni valuable kama EV (F-024 — CCS).
11. **Direct purity ≠ transitive purity** — dependency graph ndiyo architecture (P107; OBS-1 ya 2026-07-03).
12. **Profitable ≠ Tradable Edge. Protect capital first. Seek edge second. Scale only after proof.**

---

## 3 — Dead Ends (ZISIRUDIWE bila uamuzi mpya wa Chief #1)

| Dead end | Kwa nini ilikufa | Rekodi |
|----------|------------------|--------|
| Human taxonomy kama "mechanism discovery" | Verification, sio discovery (NO HUMAN MARKET THEORY) | Phase 5.9 NOT APPROVED |
| Universal interaction rules (cell-space) | 0/20 zilisurvive cross-market | F-014 |
| Algorithm-independence kama acceptance criterion | ARI ndogo ≠ representation mbaya; decision quality ndiyo kipimo | old P18 REMOVED (V5.12) |
| Rare states = payoff states | ratio ≈0.91× (hakuna payoff kubwa); spread +12σ → execution risk | H-05 REJECTED → H-06 |
| CCS-selection portfolio | OOS −0.757 (haipatikani positive) | Phase 8 hypothesis REJECTED |
| Universal causal primitives (Compression kama mechanism) | event-free construction haikuizalisha; precedence lift ≈1.0 | F-041 REJECTED |
| Ecology yenye decision value | JS≈0; ΔBrier≈0 — background property kama hali ya hewa | F-042 REJECTED |
| Mean-reversion-only strategy | subgroup + multiple comparisons | forbidden (V5.21) |
| "Alpha Discovery Era" declarations | premature — hakuna edge iliyothibitishwa | retracted (V6.4) |

---

## 4 — Lessons Learned (methodology ya taasisi)

1. **Specification-before-code inafanya kazi** — D6 (spec → architecture review → implementation) ilitoa implementation safi zaidi ya mradi.
2. **Contract > proof** — discovery kubwa ya D0 ilikuwa kudefine contract (Evidence Object), sio kuthibitisha market; ya D5 ilikuwa Contract ya Engine–Policy (P94).
3. **Versioning inaokoa provenance** — P88 kesi ya kwanza halisi: report @v1 vs code @v2 bila confusion (Audit #3 D-1).
4. **Same-sample correlation hudanganya** — Phase 9 whole-sample ρ≈+0.74 → Phase 10 causal ρ≈+0.03 (artifact).
5. **Hygiene commits tofauti na research commits** (agizo la Chief, V8).
6. **Self-tests zisizohitaji data** = mitigation ya R-1 (data ~26GB kwenye PC moja).
7. **Kila failure ina reframe sahihi** — "0 survived FDR" si "hakuna alpha" bali "representation failure until proven otherwise" (P33); lakini pia usikimbilie hidden variables (P28).
8. **Wording discipline** — Chief hurekebisha verdicts (mf. "no Selection-DV under the metric used", sio "no decision value"); precision ya lugha ni sehemu ya sayansi.
9. **Doctrine sprawl ni hatari kwa wasomaji wapya (na AI agents)** — root ibaki na SSOT pekee; archive iko `doctrine/archive/`.

---

## 5 — Rekodi za msingi

- Findings/Questions/Amendments/Approvals: `docs/PROGRAM_BOARD.md` (SSOT ya governance)
- Doctrine hai: `ELITEFX DOCTRINE V6.9.md` (Market) · `ELITEFX DECISION DOCTRINE V11.md` (Decision)
- Audits: `docs/ARCHITECTURE_AUDIT.md` · `docs/CHIEF_GAP_REVIEW.md`
- Status hai: `docs/CHIEF_STATUS.md`
