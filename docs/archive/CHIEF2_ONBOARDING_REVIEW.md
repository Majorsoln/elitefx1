# CHIEF QUANT WA PILI — MAPITIO YA KUINGIA + MASWALI KWA CHIEF WA KWANZA

*2026-07-03 | Chief Quant #2 (mpya) | Deliverable: mapitio ya mradi mzima + maswali ya ufafanuzi
kabla ya kushiriki maamuzi yoyote | Hakuna doctrine change, hakuna approval — maswali tu.*

> **STATUS (2026-07-03): MASWALI YOTE YAMEJIBIWA na Chief #1.** Majibu yamerekodiwa rasmi kwenye
> `ELITEFX DECISION DOCTRINE V11.md` (two-Chief governance; P107 kutoka OBS-1; E1 pre-spec rulings;
> scheduling ya P70/P96/P78; alpha philosophy; hygiene E-2/E-3/E-4). Role ya Chief #2 = **Scientific
> Reviewer** (independent challenger; approval ni ya Chief #1 pekee).

> Kwa mujibu wa workflow (PROGRAM_BOARD): *Evidence → Finding → Doctrine → Approval*. Waraka huu ni
> hatua ya kwanza ya Chief #2: kuonyesha nilichokielewa (ili Chief #1 asahihishe uelewa mbovu mapema)
> na kuuliza pale ambapo rekodi haijibu.

---

## 1 — Nilichopitia

- **Doctrine mbili za SSOT:** `ELITEFX DOCTRINE V6.9.md` (Market — FROZEN) na
  `ELITEFX DECISION DOCTRINE V10.md` (Decision — ACTIVE), pamoja na chain ya V1→V10.
- **Governance:** `docs/PROGRAM_BOARD.md` (findings F-001…F-042, Q-001…Q-048, amendment log,
  approval log), `docs/ARCHITECTURE_AUDIT.md` (Audits #2–#4, risks A/R/G),
  `docs/CHIEF_GAP_REVIEW.md` (Audit #1).
- **Code:** `src/research/` (Evidence Layer D0–D3, `decision_object.py`, `decision_policy.py` @v2,
  `decision_engine.py`) na `src/data/`. Self-tests za `decision_engine` na `decision_object`
  **nimeziendesha mwenyewe: PASS** (baada ya kufunga requirements kwenye environment safi).
- **Operesheni ya mkono:** `MWONGOZO.md` + `config/ftmo_config.yaml` (lot sizing kwa bajeti ya siku,
  pre-trade checklist, R1–R7) na `Event Library.md` (Davey 9 entries), `config/data_config.yaml`.
- **Spec/report za D6:** `reports/decision_engine_specification.md` + `decision_engine_report.md`.

## 2 — Uelewa wangu wa hali ya mradi (Chief #1 asahihishe kama nimekosea)

1. **Chapter One imefungwa:** tunajua market vizuri (event-specific representations, latent
   structures, semantics), LAKINI hakuna edge iliyothibitishwa — Phase 11 (aggregate H0 haikukataliwa),
   Phase 14 (0/282 baada ya FDR), Phase 26 (0/9 Selection-DV OOS). Msimamo rasmi: hii ni
   representation/decision-theory gap, sio uthibitisho kwamba alpha haipo (F-033, P60).
2. **Frontier ya sasa = Execution Science (Chapter 3):** E1 Integrity Gate (P105) → E2 Execution
   Object (P89) → E3 Decision Repository (P106) → E4 Broker Adapter; kila moja spec-first + Chief
   phase-start (P91).
3. **Architecture ya Decision domain imefungwa na inalindwa:** Evidence Layer FROZEN (interface —
   P90); Engine = orchestrator functions mbili, stateless, import-pure (P97/P103/P104); logic yote ya
   maamuzi ni ya Policy (P94); RED LINE: reliability ≠ probability hadi P70 ifungwe.
4. **Mikondo miwili ya kazi:** (a) mkondo wa sayansi (research → decision architecture → execution),
   na (b) mkondo wa mkono (MWONGOZO/FTMO $10k: bajeti ya siku, checklist, R1–R7) — uhusiano rasmi
   kati yao haujaandikwa popote nilipoona (swali F-1 hapa chini).
5. **Utamaduni:** hakuna ML; hakuna madai bila evidence; "Profitable ≠ Tradable Edge"; approval ni ya
   Chief pekee; Auditor hakagui zaidi ya compliance; kila mabadiliko yana rekodi.

## 3 — Observation ya kiufundi niliyoipata mwenyewe (kwa Chief #1 + Auditor)

**OBS-1: Import-purity ya Engine ni ya moja kwa moja tu — transitive dependency inavuja Market domain.**
`decision_engine.py` inaimport `decision_object` pekee (safi, self-test [4] PASS). Lakini
`decision_object.py` (line 41) inaimport `market_state_engine` (→ `polars`) kwa demo-instantiation.
Matokeo: Engine **haiwezi hata ku-load** bila Market Science stack nzima (nimeithibitisha kwenye
environment safi — `decision_engine.py --self-test` ilianguka kwa `polars` missing kabla ya kufunga
requirements zote). Self-test [4] na 4-point compliance review vinapima imports za file ya Engine tu,
si za chain. Hii inaonekana kama upanuzi halali wa W-1/P92: je, tunaifunga kwa (a) kuhamisha
demo/market imports kutoka `decision_object.py` kwenda report harness, au (b) kuongeza transitive
import check kwenye compliance tests (P104)? **Sifanyi chochote hadi Chief #1 aamue.**

---

## 4 — MASWALI KWA CHIEF WA KWANZA

### A. Governance ya Chiefs wawili (kipaumbele cha kwanza — kabla sijafanya lolote)

- **A-1.** Doctrine inasema "APPROVED ni la Chief pekee". Sasa tuko Chiefs wawili: je, Chief #2 ana
  mamlaka kamili ya approval, au ni deputy (review + pendekezo; approval ya mwisho ni ya Chief #1)?
  Tukikinzana, nani anavunja tie — na hilo liandikwe wapi (board? doctrine amendment)?
- **A-2.** Je, Chief #2 aandikwe rasmi kwenye governance roles za PROGRAM_BOARD (Chief #1 · Chief #2 ·
  Implementer · Auditor) pamoja na mgawanyo wa scope (mf. Chief #2 = Execution Science, Chief #1 =
  doctrine ya jumla), ili approval log ionyeshe nani aliidhinisha nini?

### B. Execution Science / E1 Integrity Gate (frontier ya sasa)

- **B-1.** Je, **phase-start approval (P91) ya E1** imeshatolewa, au inasubiri? Nani anaandika spec ya
  E1 — Implementer kama D6, na kwa muundo gani (maswali 8 kama D6 spec)?
- **B-2.** **Mipaka ya Integrity Gate vs Engine validation:** Engine tayari inafanya structural
  validation (spec Q8, S1–S5). Gate itakagua NINI zaidi — mfano: enum ya action, refs zipo
  (policy_id/snapshot_id), lifecycle sahihi, risk/compliance constraints? Tunaepukaje kurudia
  validation ile ile layer mbili?
- **B-3.** **FTMO compliance inaishi wapi kwenye architecture?** Checks za MWONGOZO (daily loss guard,
  total DD, slots, correlation, spread) — je, ni sehemu ya Integrity Gate (P105), ni Policy input, au
  ni external execution constraints (P81 OPEN) za Broker Adapter? Jibu hili linaamua kama
  `ftmo_config.yaml` inaingia kwenye Decision domain au inabaki nje.
- **B-4.** **Nani anaandika lifecycle transition PROPOSED→VALIDATED?** Decision Object ni immutable
  (P83) na transitions ni operations — je, Gate inarudisha Decision Object mpya (id ile ile? mpya?),
  au kuna operation ya nje ya lifecycle? (Hii itaamua semantics ya decision history P85.)
- **B-5.** **Ordering ya E-series:** E1→E2→E3→E4 kwa mfuatano mkali, au E3 (Repository) inaweza
  kwenda sambamba na E1 kwa kuwa haitegemei Gate?

### C. Open Principles — kipaumbele

- **C-1.** **P70 (confidence model):** RED LINE inasimama hadi P70 ifungwe, na A-1/R-2 (saturation ya
  Φ(EV/SE)) ni HIGH probability. Je, P70 ifungwe kabla ya E-series kwisha, au inasubiri D8? Una
  preference ya approach, au bado wazi kabisa?
- **C-2.** **P96 (Policy Selection):** Audit inaiita gap kubwa ya architecture iliyobaki (A-5). Je, ni
  phase mpya ya Decision Science (D7?) au inaingia kwenye Execution Science? Nani caller wa sasa
  anayechagua policy kwenye research runs — Japhet kwa mkono?
- **C-3.** **P78 (redundancy ≠ duplication):** evidence correlated inahesabiwa kama huru → set
  reliability optimistic (A-3). Hii inaathiri kila decision ya sasa — ipangiwe phase lini?
- **C-4.** **A-4/R-5 (immutability enforcement — frozen dataclasses):** audit inasema inahitajika
  "kabla ya Execution". Je, hilo ni sharti la kuanza **E2** (Execution Object) au la **E4** (broker
  halisi)?

### D. Research / Edge

- **D-1.** **Mkakati wa alpha:** kwa sasa tunajenga decision/execution architecture bila edge
  iliyothibitishwa. Ni **decision need ipi** ingefungua tena market-discovery (P62)? Kuna picha ya
  "siku alpha itafutwa tena, itafutwa vipi" (mf. kupitia Event Library + Contextual Events chini ya
  pre-registration + FDR kama Phase 14)?
- **D-2.** **Re-runs zinazosubiri data run ya Japhet:** (i) F-005 full-metric re-run (pending tangu
  2026-06-23); (ii) D5 report re-generation kwa policies @v2 (optional, D-1 ya Audit #3). Je, data run
  ijayo izifanye zote mbili, au tuziache (kwa nini)?
- **D-3.** **Q-016/H-06 (rare states = execution risk) iko QUEUED** na sharti lake lilikuwa "reopen
  only if a decision needs it". Sasa tunaingia Execution Science — je, hitaji la execution-risk
  limefika, Phase 5.12 ifufuliwe, au bado?

### E. Operesheni / Infrastructure

- **E-1.** **R-1 Research Infrastructure Risk (HIGH/HIGH):** data ~26GB iko kwenye PC moja (Japhet).
  Kuna mpango wa mitigation zaidi ya `--self-test` (backup ya nje, sample dataset ndogo ya CI,
  checksums za dataset kwa reproducibility)?
- **E-2.** **SPEC-TEXT open item:** matini ya Chief ya D6 Implementation Rules 1–8 bado haiko repo
  (imesalia OPEN kwenye V10). Nani ana-commit, wapi (`docs/`?), na kwa jina gani — ili compliance
  reviews za baadaye zi-cite maandishi kamili?
- **E-3.** **`asset.zip` (root) na `reports/report.zip`:** ni nini hasa ndani yake, na ni sehemu ya
  rekodi (zibaki git) au ni artifacts za muda?
- **E-4.** **Doctrine sprawl (R-6):** pendekezo la Auditor la `doctrine/archive/` linahitaji Chief
  approval. Je, tulipitishe sasa (files 40+ za V-zamani root zinaongeza hatari ya kusoma doctrine
  ya zamani kama ya sasa — hasa kwa AI agents)?

### F. Mkondo wa mkono (MWONGOZO / FTMO)

- **F-1.** **Uhusiano rasmi wa mikondo miwili:** MWONGOZO.md inasema ndiyo "chanzo pekee cha mfumo
  sasa" kwa kucheza kwa mkono — je, mkondo huu ni **operesheni hai** (akaunti ya FTMO inaendeshwa
  sasa kwa mkono) au maandalizi? Na kwenye rekodi, mikondo hii miwili (manual FTMO vs Decision
  Science) inakutana wapi — E4 Broker Adapter ndio lengo la kuunganisha?
- **F-2.** **Values za `ftmo_config.yaml`** (win_factor 0.50, loss_factor 1.00, max_per_trade 120,
  trailing params za R1–R7): kanuni ya chuma inasema "hatubadilishi bila kupima" — je, values hizi za
  awali zenyewe zina backtest evidence mahali fulani, au ni judgment za kuanzia (na hivyo zinasubiri
  kupimwa)?

---

*Nikishapata majibu ya sehemu A (governance), nitaanza kushiriki kikamilifu kwenye mzunguko wa
review. Hakuna nilichokibadilisha kwenye doctrine, code, wala board.*

*Profitable ≠ Tradable Edge. Protect capital first. Seek edge second. Scale only after proof.*
