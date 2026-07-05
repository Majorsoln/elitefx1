# Broker Adapter Specification — THE TWO STREAMS MEET (E4, P81/P106)

*2026-07-05 | Deliverable ya kwanza ya E4 (Chief: "E4 Broker Adapter spec — MT5/FTMO interface;
paper-mode kwanza; maswali 8"; E1+E2+E3 CLOSED) | Coding baada ya spec kupitishwa | NO code bado |
NO ML | NO pesa halisi bila Project Director approval*

> **Doctrine V12:** *"MWONGOZO = Operational Manual (mkondo wa mkono); Decision Science = Research
> Architecture (mkondo wa sayansi). **Hazijakutana bado. Zitakutana E4 — Broker Adapter.**"* **P81**
> FTMO = execution constraint (inaingia kupitia Execution Science, si Decision Science). **P92/P107**
> Adapter ndio **mpaka rasmi wa impurity** — external I/O (MT5/files/network) imefungiwa hapa; kila
> kitu upstream (Engine/Gate/Recorder/Repository) kinabaki pure. **Protect capital first** (Master §7.5):
> paper-mode ni default; live inahitaji approval ya Project Director.

---

## Kanuni elekezi (kabla ya maswali 8)

Track A yote (E1→E3) ni **pure**: Engine/Gate/Recorder ni stateless functions; Repository ni state
iliyofungiwa; hakuna kinachogusa dunia ya nje. Lakini biashara halisi inahitaji **MT5, ftmo_config,
account state, fills halisi** — vitu vichafu (impure). **E4 ndio ukuta** kati ya hizo dunia mbili:

```text
DUNIA SAFI (sayansi)                    E4 — BROKER ADAPTER                  DUNIA CHAFU (mkono/MT5)
Engine·Gate·Recorder·Repo   ◀── translates ──▶  (mpaka wa impurity)  ◀──▶  MT5 · ftmo_config · account · fills
   (pure, P97/P107)                     (impure kwa makusudi)               (external, MWONGOZO)
```

**Adapter = mtafsiri (translator), si mwamuzi (decider).** Inabadilisha:
- `ftmo_config.yaml` + account state → **EligibilityConstraints + context** kwa **Gate (E1)** — hii
  ndiyo P81 ikitimizwa (E1 iliweka *interface* ya constraint; E4 inatoa *FTMO constraints* halisi).
- **VALIDATED decision** + sizing → **order** (MT5, paper-mode).
- **broker fills/slippage/rejects** → **ExecutionReport** kwa **Recorder (E2)**.
- **close-fills** → **Settlement record** kwa **Repository (E3)**.

Sentensi ya Adapter: **"chukua config na hali ya akaunti, tengeneza constraints; peleka VALIDATED
kwa broker; rudisha kilichotokea kama objects safi."** Kila kitu kingine ni mipaka ya sentensi hiyo.

### Adapter inafunga loop iliyoanzishwa E1

```text
E1 ilifafanua:  gate(decision, constraints, context) → VALIDATED | REJECTED
E4 inatoa:      constraints ← ftmo_config (CHECK 1-5)      ┐
                context     ← account state (live/paper)   ┘→ FTMO ikitimizwa (P81)
                (MWONGOZO Check 1-5 = E1 eligibility constraints, injected)
```

## Q1 — Adapter responsibilities (NINI inafanya)

| # | Responsibility | Doctrine |
|---|----------------|----------|
| 1 | **Kujenga FTMO EligibilityConstraints** kutoka `ftmo_config.yaml` (CHECK 1-5) + `context` kutoka account state → kwa **Gate (E1)** | **P81**; E1 contract |
| 2 | **Sizing** (DailyRiskBudgetSizer, MWONGOZO §1) → `intended.qty` kwa order/report | E2 Q5 (sizing = E4 path) |
| 3 | **Kutuma order** (VALIDATED decision + sizing) kwa broker — **paper-mode default** | Master §7.5; P89 |
| 4 | **Kuzalisha ExecutionReport** (fills/slippage/rejects) kutoka broker outcome → kwa **Recorder (E2)** | E2 Q7 (report injected) |
| 5 | **Kuzalisha Settlement record** (close-fills → realized PnL) → kwa **Repository (E3)** | E3 (Settlement=object tofauti) |

Hakuna jukumu la sita. Adapter **haiamui** kununua/kutokununua (Policy/Engine), **haihakiki**
eligibility yenyewe (Gate ndiyo inaevaluate constraints; Adapter inazitoa tu), **haihesabu** decision
quality (D8). *Translate, don't decide.*

## Q2 — Adapter boundaries (NINI HAIFANYI — kamwe)

| Boundary | Maana | Doctrine |
|----------|-------|----------|
| ❌ Hakuna decision/eligibility logic | Adapter inatoa constraints + context; **Gate** ndiyo inaevaluate (ELIGIBLE/INELIGIBLE). Adapter haiamui | **P97/Rule 3**; E1 |
| ❌ Hakuna pesa halisi bila approval | `mode=paper` default; `mode=live` inahitaji **Project Director approval artifact** — vinginevyo Adapter **inakataa** | **Master §7.5/§8.2** |
| ❌ Hakuna decision quality/edge | PnL inarekodiwa (Settlement); je ni edge? = **D8** | P69/P87 |
| ❌ Adapter ndio PEKEE inayogusa external | MT5/ftmo_config/network/account — impurity imefungiwa hapa; upstream haigusi | **P92/P107** (Adapter = sanctioned boundary) |
| ❌ Haibadilishi doctrine values | ftmo_config = judgement ya Japhet (si evidence); Adapter inasoma tu, haibuni | V12 (FTMO = judgement) |
| ❌ Hakuna mutation ya objects | Decision/Execution/Settlement zinabaki frozen (A-4); Adapter inaunda mpya | P83/A-4 |

## Q3 — Inputs

| Input | Aina | Sharti |
|-------|------|--------|
| `decision` | Decision Object (VALIDATED) | Kwa order submission (Q1.3). Structural + `lifecycle==VALIDATED` (Q8). |
| `ftmo_config` | dict (kutoka `config/ftmo_config.yaml`) | Kwa constraint building (Q1.1) + sizing (Q1.2). Injected path. |
| `account_state` | dict (live/paper): `{daily_loss, total_dd, open_slots, correlation_exposure, spread_by_pair}` | Kwa `context` ya Gate + worst-case checks (MWONGOZO). |
| `broker` | BrokerClient (injected): `submit(order)` · `fills(order_id)` · `positions()` | MT5 (live) au PaperBroker (simulator). Opaque. |
| `mode` | `"paper"` \| `"live"` | `live` inahitaji approval artifact (Q5/Q8). Default `paper`. |

## Q4 — Outputs

| Output | Kwenda | Muundo |
|--------|--------|--------|
| **EligibilityConstraints** (5) + **context** | Gate (E1) | kila constraint = `{id, check(decision, context)→(verdict, reason)}` (E1 contract) |
| **order** | broker | `{decision_id, side, qty, sl, tp, ...}` (paper au live) |
| **ExecutionReport** | Recorder (E2) | `{status, intended:{side,qty,ref_price}, fills, reject_reason?, as_of}` (E2 Q7 contract) |
| **Settlement record** | Repository (E3) | `{id: settle:…, parent_execution_id, realized_pnl, return, holding_period, costs, as_of}` |

**Constraints ndio output ya msingi ya E4↔E1** (P81): CHECK 1-5 za MWONGOZO zinakuwa constraint
objects (tazama sehemu ya FTMO Constraints hapa chini). Adapter **haiziita** — inazipeleka kwa Gate.

## Q5 — Error handling

| Kesi | Tabia | Kwa nini |
|------|-------|----------|
| `mode=live` bila Project Director approval | **AdapterError** (`live_not_authorized`) — **inakataa kabisa** | **Protect capital first** (RED LINE ya E4) |
| Order **REJECTED** na broker/FTMO check | **SIO error** → ExecutionReport `status=REJECTED` (E2 inashughulikia) | Reject ni outcome halali (E2) |
| Broker connection/timeout | **AdapterError** (`broker_failure`, imerekodiwa) — hakuna report bandia | Adapter haiokoi broker |
| `ftmo_config` invalid (fields muhimu hazipo) | **AdapterError** (`invalid_config`) | Q8 |
| `decision.lifecycle != VALIDATED` | **AdapterError** (`invalid_decision`) | Adapter inatuma VALIDATED pekee |
| Sizing → qty ≤ 0 (bajeti imekwisha) | **SIO error** → hakuna order; constraint ya Gate (daily-budget) ingekuwa imezuia mapema | MWONGOZO §1 (bajeti=0 → hakuna trade) |

## Q6 — Audit / provenance

- **Broker-interaction log** (auditable): `adapter.constraints`, `adapter.submit`, `adapter.fill`,
  `adapter.settle`, na `adapter.refuse_live` (kila jaribio la live bila approval).
- Provenance kamili (mfumo mzima sasa): `Settlement → Execution → Decision(VALIDATED) →
  Decision(PROPOSED) → Snapshot`; constraints zilizotumika + config version zimerekodiwa.
- **ftmo_config version/hash** inarekodiwa kwenye kila order/report → reproducibility ya compliance.

## Q7 — Injection (broker client + config)

- **Dependency injection tupu:** `adapter(decision, ftmo_config, account_state, broker, mode)` — broker
  na config zinapita kama arguments. Hakuna MT5-connection au file-path iliyofichwa ndani ya core.
- **Swappability:** `PaperBroker` (self-test/paper — deterministic, bila pesa) · `MT5Broker` (live,
  gated). Adapter code haiguswi; contract ile ile (`submit/fills/positions`).
- **PaperBroker ndio inaruhusu self-test bila data ya nje (Rule 7)** — simulator inarudisha fills
  za kubuni; hakuna MT5, hakuna network, hakuna pesa.

## Q8 — Validation (structural + gating)

```text
V1  decision ni Decision Object halali + lifecycle == VALIDATED        → invalid_decision
V2  ftmo_config ina fields: account_size, daily_budget_start, max_*,
    max_daily_loss, max_total_dd, correlation_groups                   → invalid_config
V3  account_state ina: daily_loss, total_dd, open_slots, ...           → invalid_context
V4  mode ∈ {paper, live}; mode==live → approval artifact ipo           → live_not_authorized
```

---

## FTMO CONSTRAINTS — MWONGOZO Check 1-5 → E1 EligibilityConstraints (P81)

Hii ndiyo **kiini cha E4**: kila compliance check ya MWONGOZO inakuwa **constraint object** kwa Gate.
Adapter inaijenga kutoka `ftmo_config` + `account_state` (context):

| MWONGOZO Check | Constraint id | `check(decision, context)` → INELIGIBLE kama… |
|----------------|---------------|-----------------------------------------------|
| CHECK 1 Daily Loss Guard | `constraint:daily_loss@v1` | `daily_loss + worst_case ≥ max_daily_loss (500)` |
| CHECK 2 Total DD Guard | `constraint:total_dd@v1` | `total_dd + worst_case ≥ max_total_dd (1000)` |
| CHECK 3 Slot Capacity | `constraint:slots@v1` | `open_slots ≥ max_slots (4)` |
| CHECK 4 Correlation Guard | `constraint:correlation@v1` | `open_in_group(pair) ≥ max_correlated_slots (2)` |
| CHECK 5 Spread Guard | `constraint:spread@v1` | `spread(pair) > max_spread(pair)` |

- **Worst-case daima** (MWONGOZO): Check 1/2 zinahesabu kana kwamba SL zote zilizo wazi zinagongwa —
  constraint inatumia `worst_case` kutoka context.
- Constraints hizi zinapita kwa **Gate (E1)** kama injected list; Gate inaevaluate (AND/veto) →
  VALIDATED au REJECTED. **Adapter haihukumu — inatoa vipimo tu** (P81/P97).
- `ftmo_config` = **judgement ya Japhet** (V12), si evidence — Adapter inasoma tu; Japhet anabadilisha
  values, mfumo unafuata.

## SIZING — DailyRiskBudgetSizer (MWONGOZO §1)

```text
budget = daily_budget_start; slots_remaining = max_slots − open_slots
risk_$ = min(budget_remaining ÷ slots_remaining, max_per_trade)
qty (lot) = risk_$ ÷ (sl_pips × pip_value)         # pip_value: MT5 (live) au config (paper)
```

- `qty` inaingia kwenye `ExecutionReport.intended.qty` (E2 Q5: sizing = E4 path, SIO Decision).
- `budget=0` (bajeti imekwisha) → `qty=0` → hakuna order (Q5).
- Sizing ni **arithmetic ya MWONGOZO**, si decision logic — inaishi Adapter (inahitaji account state).

## PAPER-MODE GATING — Protect capital first (Master §7.5/§8.2)

```text
mode=paper  (DEFAULT)  → PaperBroker (simulator); hakuna pesa halisi; self-test-able
mode=live              → MT5Broker; INAHITAJI Project Director approval artifact;
                         bila artifact → AdapterError(live_not_authorized)  [RED LINE ya E4]
```

Hii ni RED LINE: hakuna njia ya code kufikia pesa halisi bila approval ya wazi ya Project Director.
Mirror ya Master §5 ("hakuna model inayogusa pesa bila proof + Project Director approval").

## SETTLEMENT — production (E3 Settlement record)

- Position inapofungwa (exit execution/close-fill), Adapter inaunda **Settlement record**: inapair
  entry + exit executions (kwa broker position id), inahesabu `realized_pnl/return/holding_period/costs`.
- Inaipeleka **Repository (E3)** kama record ya `kind` mpya (au `execution` yenye settlement fields —
  Open Q). D8 ndiyo inahukumu kama PnL hii ni edge; K6 inajifunza kutoka kwake.

---

## Mchoro wa mwisho (E4 = confluence ya Track A)

```text
                                 ┌───────────────────────────────────────┐
 ftmo_config.yaml ──config────▶  │           BROKER ADAPTER (E4)          │
 account_state   ──context───▶   │  build constraints (CHECK 1-5) ──────────▶ Gate (E1)  [P81]
                                 │  size (DailyRiskBudgetSizer) ─────────────▶ intended.qty
 Decision(VALIDATED) ────────▶   │  submit(order) [paper|live-gated] ───────▶ broker
 broker fills ───────────────▶   │  → ExecutionReport ───────────────────────▶ Recorder (E2)
 broker close ───────────────▶   │  → Settlement ────────────────────────────▶ Repository (E3)
                                 └───────────────────────────────────────┘
                                    impurity imefungiwa hapa (P92/P107)
                                    hakuna pesa bila Project Director (RED LINE)
                                    translate, don't decide (P97)
```

---

## VERDICT — E4 Specification

→ Spec inajibu maswali 8 na inafunga E4 kama **mpaka wa impurity + mtafsiri** kati ya Decision Science
(pure) na MWONGOZO/FTMO/MT5 (external). Inatimiza **P81**: FTMO Check 1-5 → E1 EligibilityConstraints
injected (+ context) → **loop ya E1 imefungwa**. Sizing (MWONGOZO §1) → E2 report. Settlement → E3.
**Paper-mode default; live imezuiwa hadi Project Director** (Protect capital first). Adapter
**haiamui** — inatafsiri tu (P97). Hii ndiyo **mkutano rasmi wa mikondo miwili** (V12) na **mwisho wa
Track A** (E1→E4). Upstream inabaki pure; Adapter ni sanctioned impurity boundary (P92/P107).

**Hakuna code iliyoandikwa.** Implementation baada ya Chief kupitisha spec + Open Questions
(hasa #1 live-gating mechanism na #6 max_spread source).

## Known Limitations

1. **MT5 haipo kwenye mazingira** — live integration haiwezi kujaribiwa hapa; self-test itatumia
   **PaperBroker** (deterministic, bila data ya nje — Rule 7). Live = PC ya Japhet + MT5 + approval.
2. **Adapter ni IMPURE kwa makusudi** — inagusa files/network/MT5. Ni sanctioned boundary (P92/P107);
   Auditor athibitishe kwamba impurity **haivuji** juu (Engine/Gate/Recorder/Repo zibaki pure).
   Constraint/report/settlement **outputs** ni objects safi.
3. **`max_spread` per-pair haipo `ftmo_config.yaml`** — MWONGOZO Check 5 inaihitaji; chanzo kinahitajika
   (Open Q#6).
4. **`pip_value` ya sizing** — live: MT5; paper: config/approx. Precision ya paper-mode ni ya makadirio.
5. **Settlement inahitaji exit/close** — realized PnL haipo hadi position ifungwe; Adapter inapair
   entry+exit (broker position id). Multi-fill/partial-close = engineering detail (Open Q#4).
6. **Live-trading = RED LINE** — spec inaweka gate; utekelezaji wa "approval artifact" (jinsi gani
   kiuhakikiwe) ni uamuzi wa Chief/Project Director (Open Q#1).

## Open Questions (kwa Chief/Project Director — Rule 1)

1. **Live-gating mechanism (RED LINE).** Approval artifact iweje? (a) config flag + credential file
   iliyosainiwa; (b) env var + Project Director token; (c) manual mode kila session. Pendekezo:
   artifact-file yenye Project Director signature + `mode=live` explicit; bila hiyo → refuse. **Uamuzi
   wa Project Director** (Protect capital first).
2. **FTMO constraint granularity** — 5 CHECKs = constraints 5 tofauti (auditable moja moja) au composite?
   Pendekezo: 5 tofauti (E1 Gate inaaudit kila moja; ruling Q4 ya E1 = AND/veto).
3. **Sizing = E4 Adapter au sizing-policy layer (P96-adjacent)?** Kwa sasa nimeiweka Adapter (inahitaji
   account state + config). Chief athibitishe (E2 OQ#4 iliahirishwa hapa).
4. **Settlement = `kind` mpya kwenye Repository au execution+fields?** E3 self-test ina KINDS=(decision,
   execution). Pendekezo: ongeza `kind=settlement` (E3 ruling Q1 = object tofauti) → edit ndogo ya
   `decision_repository.py` (Rule 1: sijaigusa).
5. **account_state source** — nani anaijaza (live: MT5 account; paper: simulator)? Contract yake
   ithibitishwe (fields: daily_loss/total_dd/open_slots/correlation_exposure/spread_by_pair).
6. **max_spread per-pair** — chanzo? (ftmo_config haina). Japhet aiongeze config au itoke MT5 live?

---

*Broker Adapter = impurity boundary + translator (P92/P107); FTMO Check 1-5 → E1 constraints injected
(P81 — loop ya E1 imefungwa); sizing (MWONGOZO §1) → E2 report; Settlement → E3; paper-mode default,
live gated na Project Director (Protect capital first). Translate, don't decide (P97). E4 = mkutano wa
mikondo miwili (V12) + mwisho wa Track A. NO code bado. NO ML. NO pesa halisi bila approval. Profitable
≠ Tradable Edge.*
