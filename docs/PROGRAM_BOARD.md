# ELITEFX PROGRAM BOARD

> **Single Source of Truth ya GOVERNANCE.** Chief Quant + Implementer wanaisoma
> HII kwanza kabla ya kuendelea. Ndani: Chief Memory · Project Status · Research
> Ledger · Doctrine Amendments · Approval Log. Doctrine imegawanyika domains mbili:
> **Market** = `ELITEFX_DOCTRINE_V6.9.md`; **Decision** = `ELITEFX DECISION DOCTRINE V5.md`;
> board hii ndiyo state ya mradi.
>
> Workflow (lazima, hakuna kuruka): **Research → Report → Chief Review →
> APPROVED/REJECTED → PROGRAM_BOARD update → Next Phase.**
> Kila kitu: *Evidence → Finding → Doctrine → Approval.* Hakuna "nafikiri" /
> "inaonekana".

*Last updated: 2026-06-30 (Chief: D2 Evidence Sets FULLY APPROVED + amendments — Principle 76 evidence meaning order-independent, lineage separate (set ≠ sequence); Principle 77 decisions operate on Evidence Snapshots not raw objects; Principle 78 OPEN statistical redundancy ≠ identity duplication; Principle 79 Evidence Snapshot = canonical Decision-Layer input; "Set Confidence" → "Set Reliability" until P70; Decision Doctrine → V5; D3 Evidence Snapshots ACTIVE; Decision Families DEFERRED).*

---

## Current Doctrine

Official (TWO DOMAINS):
- `ELITEFX_DOCTRINE_V6.9.md` — **Market** domain (Representation/Taxonomy/Semantics/Geometry; mature, FROZEN)
- `ELITEFX DECISION DOCTRINE V5.md` — **Decision** domain (Evidence Layer: Object + Operations + Sets + Snapshots; then Decision/Risk/Opportunity/Abstention/Sizing/Portfolio/Execution; active frontier)

Status:
- ACTIVE (both)

Superseded:
- V4 … V6.7 (chain)
- V6.8 (superseded by V6.9 + Decision Doctrine V1→…→V5)
- Decision Doctrine V1→V2→V3→V4→V5 (V1 Evidence-first; V2 split; V3 3-layer/immutable/operations; V4 value-object/graph/sets; V5 snapshots/order-independence)
- Patches

---

## Approved Findings

**[F-001] Market States Exist**
Status: APPROVED
Evidence: `market_state_report.md`

**[F-002] State Persistence Exists**
Status: APPROVED
Evidence: `market_state_report.md`

**[F-003] State Age Matters**
Status: APPROVED
Evidence: `state_age_report.md`

**[F-004] State Age Improves Calibration**
Status: APPROVED
Evidence: `state_transition_model_report.md`
Note: age ni **calibrator**, sio predictor (accuracy flat, ECE ↓).

**[F-005] Context Improves Event Quality**
Status: APPROVED
Evidence: `context_value_report.md` *(full-metric re-run pending; matokeo ya
awali: `state_context_value_report.md`, run ya Japhet 2026-06-23)*
Note (uaminifu wa ledger): faida ni **EV-SELECTION, sio prediction** —
median ΔEV chanya (vol +1.26 / spr +0.67 / act +0.59 pips), lakini ΔLogLoss ≈ 0
(P(win) haibadiliki). Hii inaunga mkono Principle 12 (Context = filter). Robustness
inajaribiwa Phase 1.95.

**[F-006] Context Value Generalizes Across Event Families**
Status: APPROVED
Evidence: `context_generalization_report.md`
Note: Context adds value kwa Trend Pullback, Breakout, NA Mean Reversion — kwa
dimensions zote tatu kwa viwango tofauti. Context ≠ Alpha; Context = Opportunity
Filter (Principle 12) sasa ina ushahidi wa kutosha. Q-001 CLOSED.

**[F-007] Volume Bars Increase Information Density**
Status: APPROVED
Evidence: `adaptive_volume_bar_report.md` + `volume_information_report.md`
Summary: Volume bars HAZIBORESHI stability (R-002). Lakini zinaboresha
INFORMATION — state persistence, state age effect, transition predictability
(activity LogLoss 0.84→0.63, acc +12pp), na context utility (18/18 dim×pair).
Kwa hiyo volume bars zinabaki **preferred market representation**. Doctrine V5.3:
*Volume bars exist because they concentrate information; Information Density >
Calendar Uniformity.* Q-003 CLOSED.

**[F-008] Context Is A Ranking Engine**
Status: APPROVED
Evidence: `context_selectivity_report.md`
Summary: Binary context filtering was too permissive (~99% accept). Decile
ranking by context score shows strong monotonic EV improvement (Pullback
D1 −3.16 → D10 +1.29; Breakout −3.80 → −0.32; Mean Reversion −1.58 → +2.29;
3/3 events). Context = ranking system, NOT pass/fail. Drives Principle 13.
Q-005 CLOSED.

**[F-009] Context Sensitivity Is Event-Specific**
Status: APPROVED
Evidence: `event_context_matrix_report.md`
Summary: Events differ in context response (improvement = Top10 EV − All EV).
Tier 1 (Top10 EV>0): Mean Reversion +2.49, Pullback +2.47, Deep Pullback +2.14,
Trend Continuation +2.11. Tier 2 (helps, EV≤~0): Breakout +1.54, Vol Breakout
+1.23, News Shock +0.95. Tier 3 (fails): Vol Expansion −0.15, Pattern Completion
−0.81. Event Library ≠ one block. Outcome research = Tier 1 only. Q-006 CLOSED.
⚠️ Profitable ≠ Tradable Edge (raw pips; no cost model / barrier / walk-forward).

### Event Priority Framework (F-009)

```text
Tier 1 (priority): Mean Reversion · Pullback · Deep Pullback · Trend Continuation
Tier 2 (helps, insufficient): Breakout · Volatility Breakout · News Shock
Tier 3 (ARCHIVED from edge research): Volatility Expansion · Pattern Completion
```

**[F-010] Context Is A Payoff Filter (not a Probability Filter)**
Status: APPROVED
Evidence: `outcome_decomposition_report.md`
Summary: EV decomposed by decile (Tier-1): ΔP(win) D10−D1 ≈ +3pp (small), ΔEV
≈ +4 pips (large). Uplift haitokani na hit-rate bali na payoff size/asymmetry
(4/4 events). Context = Payoff Filter. Doctrine: Context → Better Payoff
Distribution → Higher EV. Q-008 CLOSED.

**[F-011] Tier-1 Has Two Payoff Mechanisms**
Status: APPROVED
Evidence: `outcome_decomposition_report.md`
Summary: Group A Reward Expansion (AvgWin↑): Mean Reversion (ΔAvgWin +3.6),
Deep Pullback (+3.1). Group B Loss Compression (AvgLoss↓): Pullback (ΔAvgLoss
−2.4), Trend Continuation (−2.8). Event Library lazima igawiwe kwa **payoff
mechanism**, sio jina la event.

### Payoff Mechanism Groups (F-011)

```text
Group A — Reward Expansion : Mean Reversion · Deep Pullback
Group B — Loss Compression : Pullback · Trend Continuation
```

**[F-012] Market Opportunity Emerges from Feature Interactions, not Individual Features**
Status: APPROVED
Evidence: `payoff_attribution_report.md` (marginal attribution insufficient)
Summary: Phase 5.6 marginal drivers (volatility ~21, activity ~20) measure
*marginal* attribution, not importance. Market acts as Vol×Activity×Transition×Age
simultaneously; edge may live in the INTERACTION. Single components do NOT explain
opportunity. **Driver ≠ Gatekeeper**: a low-marginal component (e.g. Transition
~11) may be a GATEKEEPER (allows the environment) not a driver. Phase 5.6
conclusion "build Payoff Engine on these components" REJECTED as premature.
Architecture: Interaction Engine inserted (…→Transition→Interaction Engine→Context
Score→Event→Payoff…). Verified by Phase 5.7.

**[F-013] State Age Is a Lifecycle Variable (not a Time Variable)**
Status: APPROVED
Evidence: `component_interaction_report.md` (Transition × Age sequential effect)
Summary: The same Transition flips sign with state age (MR: Thi·4-8 +3.0 vs
Thi·16+ −3.2). Age 12 in Expansion ≠ Age 12 in Compression → age = lifecycle
encoding, not a bare numeric feature. Architecture: State → Age → Transition →
**Lifecycle Stage**. Three component categories: **Drivers** (change payoff, e.g.
volatility) · **Gatekeepers/Routing** (allow setup, e.g. transition) · **Lifecycle
Variables** (decide market stage, e.g. state age). Market = Regime + Lifecycle
Stage + Transition Gate. Context Score → **Market State Vector** (score = output).

**[F-014] Interaction Structure Is Pair-Specific (not Universal)**
Status: APPROVED
Evidence: `interaction_stability_report.md` (0/20 universal across pairs)
Summary: In feature coordinate space (LOW/NORMAL/HIGH cells), no interaction
generalises cross-market (rank consistency <0.3 / modal best <50%). We will NOT
build a rule engine keyed on cell IDs. Q-011 CLOSED.

**[F-015] Latent Market Structures (HYPOTHESIS — OPEN, reframed V5.9)**
Status: OPEN — NOT PROVEN
Evidence: `mechanism_discovery_report.md` supported it on 0/4 events (method rejected)
Summary: WAS "Universal Mechanisms, Local Coordinates". Phase 5.9 imposed a HUMAN
TAXONOMY (Expansion/Compression/…) via rules → verification, not discovery →
violated NO HUMAN MARKET THEORY → **NOT APPROVED**. Reframed: do **latent market
structures** exist when data is left to speak (unsupervised, no labels)? Rule-based
names removed as ground truth. "Mechanism Library" → "Latent State Library".
Decisive test = unsupervised clustering (standardized Euclidean, not cosine) vs
permutation null. Verified by Phase 5.9A → **CONFIRMED as F-016**.

**[F-016] Latent Market Structures Exist Without Human Labeling**
Status: APPROVED
Evidence: `latent_structure_report.md` (k=4 best, EV gap +0.126 vs permutation
null; 3/4 clusters recur across all 9 pairs)
Summary: Unsupervised clustering (no human labels) of Market State Vectors found
real structure above chance, recurring cross-pair. Market architecture, not
feature evidence. Doctrine shift: State-based → **Market Configuration-based
Trading** (a trade is a consequence of a configuration, not a signal). Q-012 CLOSED.
> ⚠️ **Cluster ≠ State**: a cluster is a math grouping. Latent State **Candidate**
> → Validated → Operational. Names only after validation.

**[F-017] Rare States — descriptive (NOT a payoff state)**
Status: **EXPERIMENTAL** (descriptive; H-05 rejected → H-06)
Evidence: `rare_state_analysis.md` (5.10R: rare mean move ≈23.8 vs non-rare ≈26.2
pips, ratio ≈0.91×; spread +12σ, activity −1σ)
Summary: Data shows rare state does NOT carry bigger payoff (Rare = Huge Moves is
FALSE). But spread +12σ → edge can be eaten by execution. **H-05 REJECTED** (rare
= payoff). **H-06 OPENED**: Rare States are EXECUTION RISK states, not payoff
states (Phase 5.12). Per Principle 19, F-017 stays Experimental.

**[F-018] Decision Robustness > Cluster Identity (reframed V5.12)**
Status: APPROVED (methodology)
Evidence: `cluster_robustness_report.md` (ARI ≈ 0.12)
Summary: WAS "Representation Robustness". Algorithm identity is NOT the criterion
(KMeans/GMM/Agglomerative solve different optimizations; low ARI ≠ bad
representation). **Old Principle 18 (Algorithm Independence) REMOVED.** New
Principle 18: a representation is valid if it improves DECISION QUALITY regardless
of algorithm. Evaluation: Representation → Opportunity Quality → EV (Phase 5.13).
Cluster/Representation Robustness (5.11/5.11B) = exploratory only.

**[F-019] The Value Law — Information has value only if it improves Expected Payoff or Decision Quality**
Status: APPROVED (supreme rule)
Evidence: `representation_value_report.md` (Phase 5.13 — representation improved
EV-selection)
Summary: Supreme rule of ELITEFX. Drives Principle 20 (feature competition) and
Principle 21 (selection > prediction — representation lifted EV-selection, not LogLoss).

**[F-020] Trading Edge Emerges from Event × Configuration**
Status: **APPROVED** (was Experimental — upgraded Phase 6)
Evidence: `event_state_interaction_report.md` (4/5 events: EV changes substantially
with latent state; some Event×State beat the event alone)
Summary: Edge lives in Event × Configuration, not Events alone (Pullback inside
State X ≠ inside State Y). Confirmed by Phase 6 Interaction Engine (EV/CI/Win/TB
per Event×latent-state). Acceptance rule: no Event enters Opportunity Engine
without Event × Configuration → Expected Payoff. Q-018 CLOSED.

**[F-021] No Event Possesses Universal Edge**
Status: **APPROVED**
Evidence: `event_state_interaction_report.md` (every event still has negative mean
EV under Event→State alone — pullback/continuation/breakout)
Summary: The event alone is not enough; edge exists only inside a COMPLETE Market
Configuration. Negative event-EV is not failure — it is proof the architecture is
right (we have not yet used Pair, Regime, Direction, Execution). Drives Principle 22
and the redefinition of Market Configuration (= Event + Latent State + Pair + Regime
+ Direction + Execution Context). The atomic trading unit is the **Configuration**,
not the event. Q-019 CLOSED (Configuration confirmed atomic unit).

**[F-022] Bad Configurations Are More Persistent Than Good Configurations**
Status: **CORE PRINCIPLE** (promoted from APPROVED Finding — Phase 8)
Evidence: `configuration_engine_report.md` (train+→+ ≈42% vs train−→− ≈66%) +
`opportunity_engine_report.md` (positive CCS-ranking does NOT survive out-of-sample;
Top 5% by train-CCS = −1.162 in test, worse than trade-all)
Summary: Negative edge persists; positive ranking does not survive OOS. Promoted to
a Core Principle: institutional systems make money by removing bad trades first, not
by finding good ones. Foundation of Principle 26 and the reframed Opportunity Engine
(remove bad → rank → allocate).

**[F-023] Ranking Is the Native Language of the Opportunity Engine**
Status: **APPROVED**
Evidence: `configuration_engine_report.md` (top configurations do not resemble one
another — e.g. EURJPY·MeanReversion·C1·HIGH·SHORT·WIDE vs GBPUSD·TrendContinuation·
C1·LOW·LONG·WIDE)
Summary: No single rule fits the winning configurations; the engine must learn a
**population**, not a rule. The Opportunity Engine ranks (not classifies). Drives
Principle 23.

**[F-024] Confidence Is As Valuable As Expected Payoff**
Status: **APPROVED** (was OPEN — upgraded Phase 7)
Evidence: `confidence_engine_report.md` (Top-25 by EV vs by CCS overlap 10/25;
Spearman ρ ≈ +0.91; high-EV/low-N configs demoted)
Summary: Ranking by CCS materially differs from ranking by EV alone. Expected
Payoff alone misleads; ranking must incorporate confidence interval, persistence,
walk-forward stability, and sample quality (the Configuration Confidence Score,
CCS). Confirms Principle 24. Q-020 CLOSED.

**[F-025] Edge Has Magnitude AND Availability**
Status: **APPROVED**
Evidence: `confidence_engine_report.md` + Chief logic gap (CCS has no Market
Capacity: CCS=5.4 occurring 2×/yr ≠ CCS=3.9 occurring 300×)
Summary: Portfolio return depends on frequency, not magnitude alone. Edge has two
dimensions — Magnitude (strength·confidence) and Availability (frequency) — both
determine portfolio value. Drives Principle 25 and the Opportunity Score
(Quality × Availability). Tested by Phase 8 Opportunity Engine.

**[F-026] State Trajectory May Carry Information (OPEN)**
Status: OPEN — hypothesis (parallel research)
Evidence: conceptual (LOW→NORMAL→HIGH ≠ HIGH→HIGH→HIGH although both end HIGH)
Summary: A state has velocity, not only value. State Direction (trajectory /
momentum) may carry additional predictive information beyond current State Value.
"State Momentum" is a parallel research hypothesis.

**[F-027] Early Edge Quality Does Not Predict Future Edge Persistence**
Status: **APPROVED** (reworded; was REFORMULATED — Phase 10)
Evidence: `edge_drift_report.md` (causal: Spearman(window-1 EV, survival) ≈ +0.03 —
essentially zero; vs Phase 9 whole-sample ρ≈+0.74 which was a same-sample artifact)
Summary: Early performance carries no information about future persistence. The clean
causal test confirms it (ρ≈0.03). Not because edge is bad — because early quality is
not predictive. Forces the more fundamental question (does edge exist at all?) →
Phase 11. Q-024 partially closed (WHY unexplained by environment).

**[F-042] Market Primitives Characterize Ecological Conditions, Not Causal Mechanisms (REJECTED)**
Status: **REJECTED** (Phase 25)
Evidence: `ecology_interaction_report.md` (JS-divergence ≈ 0.000 → ecology does not discriminate
events; ΔBrier ≈ 0, 0/5 events → no calibration value; weighting view → no decision value)
Summary: The ecological-layer-with-value hypothesis is not supported. Ecology is a **background
property** (like weather), not a conditioning/discriminating variable (P56); primitives are
**descriptive metadata** until independent decision value is shown (P57). Primitive Research
PAUSED. The remaining gap is **decision value**, not market structure → Decision Theory turn.

**[F-041] Universal Market Primitives May Underlie Multiple Event Families (REJECTED)**
Status: **REJECTED — current formulation** (Phase 24)
Evidence: `market_primitive_validation_report.md` (event-free construction did NOT reproduce
Compression; most primitives → Equilibrium/Balanced Flow; only Mature Persistence had identity;
precedence lifts ≈ 1.0)
Summary: The *universal causal* primitive hypothesis is not supported. What failed is the
**Universal** primitive layer, not the primitive layer itself → reframed as ecological (F-042).
Chief: do NOT chase the hypothesis (no tuning k/algorithm to revive Compression).

**[F-040] A Shared Semantic Vocabulary May Span Events (OPEN)**
Status: OPEN (Phase 22)
Evidence: `semantic_taxonomy_report.md` (same labels — Compression, Balanced Flow,
High-Volatility Regime — appear across almost all events; cross-pair repetition)
Summary: The same market-language labels recur across different events → possibly **Market
semantics**, not Event semantics; we may be discovering **Universal Market States**. Bigger
than any single alpha (a reusable vocabulary across the Event Library). Tested by Phase 23
(consistency + data-driven recoverability + universality vs event-specific geometry).

**[F-039] Different Events Require Different Geometric Representations for Operational Deployment (APPROVED)**
Status: **APPROVED** (reworded — Phase 21)
Evidence: `representation_operationalization_report.md` (Q4: Nyström OOS silhouette range
0.452 deep_pullback … 0.640 trend_continuation; spread 0.189); `representation_geometry_report.md`
Summary: An operational extension of Principle 38 to geometry. Phase 20 showed events differ in
manifold quality; Phase 21 confirmed the difference persists OOS (deployment), so the choice of
geometry is event-specific. Representation is a family; geometry is part of the per-event choice.

**[F-038] Market Taxonomy Shows Latent Heterogeneity but Is Not Yet Robust**
Status: **PARTIALLY APPROVED** (downgraded — Phase 19)
Evidence: `event_taxonomy_report.md` + `taxonomy_robustness_report.md` (cross-algo ARI
0.08–0.30; best-k unstable 50–67%; 0 robust subtypes)
Summary: Reworded: "Some events exhibit evidence of latent heterogeneity, but the
current taxonomy is not yet robust to representation and clustering methodology."
Specific complexity claims (e.g. breakout k=3) **retracted** — best-k is unstable. The
problem is representation, not necessarily ontology (Principle 42/43); audited in Phase 20.

**[F-037] Some Events Exhibit Latent Sub-Events (PARTIALLY APPROVED)**
Status: **PARTIALLY APPROVED** (was OPEN — Phase 18)
Evidence: `event_taxonomy_report.md` (sub-events for trend_continuation & breakout only;
0/17 subtypes carried positive edge)
Summary: Reworded: "Some Events exhibit statistically distinguishable latent sub-events;
event taxonomy is therefore event-dependent, not universal." Not all events have
sub-events. Taxonomy ≠ alpha (0/17 edge → Principle 40). Robustness pending (Phase 19,
Principle 39).

**[F-036] Market Variables Are Conditional Entities**
Status: **APPROVED**
Evidence: `event_centric_representation_report.md` (activity matters for MR/pullback,
not for breakout; each event has its own informative context set)
Summary: A market variable's information content depends on the governing Event — it
does not exist outside an Event. Terminology: Variable → **Conditional Variable**.
Drives Principle 38 (no universal representation) and the Event Representation Family.

**[F-035] State Variables Derive Meaning Through Events, Not Each Other**
Status: **APPROVED**
Evidence: `representation_interaction_report.md` (Q5: Event×Trajectory ✅, Event×Volatility
✅, Activity×Event ✅; but Age×Transition ❌, Age×Trajectory ❌, Transition×Trajectory ❌)
Summary: Market state variables acquire meaning primarily through interaction with EVENTS,
not with one another. The intuited hierarchy (State→Age→Transition→Trajectory) does not
stand alone; context attaches to an Event. Architecture: Event → Context (each event has
its own). Drives Principle 36/37 and Phase 17 (event-specific representations).

**[F-034] Hierarchical Redundancy Is Expected, Not Uselessness**
Status: **APPROVED**
Evidence: `representation_audit_report.md` (Age↔Persistence 0.82; Transition↔Persistence
1.00 — persistence is a derivative of age)
Summary: High Cramér's V among hierarchical variables (age/persistence/transition)
confirms the ontology (State→Age→Transition→Trajectory), it does not mean the variables
are useless. Drives Principle 34/35 — standalone incremental R² is the wrong test;
interaction/calibration/stability are the right ones (Phase 16).

**[F-033] A Representation Can Fail While Structure Still Exists**
Status: **APPROVED**
Evidence: `contextual_alpha_confirmation_report.md` (0/282 survived FDR using ONE
representation: Event+Pair+Vol+Spread+Session — many doctrine variables untested)
Summary: Failure to validate ≠ absence of alpha. The Phase 14 null is "Current
Representation Failure", not "No Alpha". Drives Principle 33 and Phase 15 (audit the
representation before concluding data/ML/new-ecology is needed).

**[F-032] Context Refinement Raises Apparent Edge AND False-Discovery Risk**
Status: **CONFIRMED** (was APPROVED — confirmed by Phase 14)
Evidence: `contextual_alpha_report.md` (30 "candidates") → `contextual_alpha_
confirmation_report.md` (0 survive FDR) = selection inflation, demonstrated end-to-end
Summary: Adding context increases apparent EV step by step — but also increases the
chance the result is selection, not signal. Phase 13's 30 → Phase 14's 0 after FDR is
the definition of selection inflation. Drives Principles 31/32/33. The Phase 13 objects
are **Contextual Alpha Hypotheses**, NOT alpha.

**[F-030] Edge Existence Is Conditional, Not Universal**
Status: **APPROVED**
Evidence: `event_reality_report.md` (aggregate events 0/5 proven, yet mean_reversion×
EURUSD +0.90 P100, deep_pullback×EURUSD +0.37 P97)
Summary: An edge does not exist for an event universally — only under a specific market
ecology (pair/state/regime/liquidity/execution). Drives Principle 30 and the Contextual
Event reframing. Q-026 CLOSED.

**[F-031] Only Contextual Events Exist (No Universal Events)**
Status: **APPROVED**
Evidence: `event_reality_report.md` (no event has edge across pairs; edge localizes to
EURUSD; MR/DPB directional skill is cost/context-relative)
Summary: Universal events do not exist; only Contextual Events do. Context is part of an
event's IDENTITY, not a filter applied later. Terminology: Event → **Contextual Event**;
Proven Edge → **Candidate Alpha** (until pre-registered OOS). spread = ecology variable.
Architecture: Contextual Event Library.

**[F-029] Edge Decay Is Driven by Market Non-Stationarity (APPROVED)**
Status: **APPROVED** (was OPEN — Phase 11)
Evidence: `edge_reality_report.md` (randomized-time survivors 39 ≫ observed 9 — the
real time-order destroys persistence; aggregate H0 not rejected)
Summary: Edge decay is primarily a consequence of market non-stationarity, not merely
of random sampling. If decay were sampling noise alone, randomizing the time-order
would not change persistence so drastically — but it did (made it larger). The market
itself destroys persistence. Two distinct answers from Phase 11: aggregate edge NOT
proven (H0 stands), AND market is non-stationary. Q-025 CLOSED.

**[F-028] Every Trading Edge Has a Lifecycle**
Status: **APPROVED**
Evidence: `survivability_engine_report.md` (median survival 1/6 windows; ~2% survive
all windows; mean decay slope ≈ −0.87 pips/window; window-1 +4.6 → window-2 −0.6)
Summary: Edge is non-stationary; every edge moves through Birth → Growth → Decay →
Death. This is the project's deepest finding and the reason Phase 8 failed OOS (the
stationary-edge assumption is false). Renames Survivability Engine → **Edge Lifecycle
Engine** and drives Principle 27 (prefer living edges) and Phase 10 (WHY edges die).

---

## Rejected Findings

**[R-001] Activity carries most predictive information**
Status: REJECTED
Reason: Phase 1.8 disproved (Activity = ΔLogLoss ndogo zaidi +2.2%, accuracy ndogo zaidi).
Evidence: `state_transition_model_report.md`
Replacement: *Activity shows strong state-memory but lower predictability;
volatility and spread provide more stable predictive structure.*
(Conflated Signal Strength ↔ Predictability.)

**[R-002] Adaptive Volume Bars Create More Stable States**
Status: REJECTED
Evidence: `adaptive_volume_bar_report.md`
Reason: 0/9 pairs improved kwa volatility; 0/9 pairs improved kwa activity.
Replacement (doctrine): *Volume Bars → Alternative Market Representation;
Status: UNPROVEN.* (Volume Bars HAZIJAFA — swali la INFORMATION ni Phase 2.1.)

---

## Current Phase

Phase: **D3 — Evidence Snapshots** (Decision Science; market-discovery FROZEN)
Name: **Evidence Snapshot (canonical Decision-Layer input)**
Status: ACTIVE (Decision domain)
Owner: Implementer + Chief
Chief Approval: YES
Question: picha ya ushahidi Decision Layer inaiona kwa wakati fulani. (1) snapshot ni nini rasmi? (2)
fields gani? (3) readiness inakokotolewaje? (4) temporal conflict (P74) inaonekana vipi? (5) Decision
Engine itapokea Object/Set/Snapshot? (jibu: Snapshot — P79). NO Decision Engine hadi Evidence Layer
ifungwe. NO ML.

> **D2 Evidence Sets FULLY APPROVED + amendments.** **P76** meaning order-independent (set ≠ sequence;
> "first theorem of Decision Science"), lineage kando. **P77** decisions juu ya **Snapshots**, sio raw
> objects. **P78 OPEN** redundancy ≠ duplication. **P79** **Snapshot = canonical Decision input**.
> "Set Confidence" → "Set Reliability" (P70 OPEN). Decision Doctrine → **V5**. Decision Families
> **DEFERRED**. Architecture: Object→Operations→Set→**Snapshot** ══ Decision→Execution. NO ML.

---

## Completed Phases

- [✓] Phase 0    Data Validation
- [✓] Phase 1    State Engine
- [✓] Phase 1.5  Transition Engine
- [✓] Phase 1.6  State Age
- [✓] Phase 1.7  Context Engine
- [✓] Phase 1.8  Transition Model
- [✓] Phase 1.9  Context Value           (Context = filter, not predictor)
- [✓] Phase 1.95 Context Generalization  (F-006: generalizes across events)
- [✓] Phase 2    Adaptive Volume Bars     (stability REJECTED R-002; information F-007)
- [✓] Phase 2.1  Volume Information Value  (F-007: information density)
- [~] Phase 3    Event Diagnostics        (CONDITIONALLY APPROVED — context metric too permissive)
- [✓] Phase 3.5  Context Selectivity      (F-008: context = ranking engine)
- [✓] Phase 4    Event × Context Matrix   (F-009: context sensitivity event-specific)
- [✓] Phase 5    Triple Barrier Design    (RESOLVED — P(TP) flat explained by F-010)
- [✓] Phase 5.5  Outcome Decomposition    (F-010 payoff filter; F-011 two mechanisms)
- [✓] Phase 5.6  Payoff Attribution       (marginal; conclusion corrected by F-012)
- [✓] Phase 5.7  Component Interaction     (F-012 confirmed 16/16; F-013 discovered)
- [✓] Phase 5.8  Interaction Stability     (F-014 pair-specific; universal rules falsified)
- [✗] Phase 5.9  Mechanism Discovery       (NOT APPROVED — human taxonomy; reworked → 5.9A)
- [✓] Phase 5.9A Latent Structure Discovery (F-016: latent structures exist; k=4)
- [✓] Phase 5.10  Rare State Analysis      (APPROVED; F-017 → Experimental, payoff pending)
- [✗] Phase 5.11  Cluster Robustness       (exploratory only — NOT acceptance criterion)
- [~] Phase 5.10R Rare State Payoff        (H-05 rejected; rare ≠ payoff → H-06)
- [~] Phase 5.11B Representation Robustness (exploratory; superseded by 5.13 Decision Value)
- [✓] Phase 5.13  Representation Value      (F-019; representation improves EV-selection)
- [✓] **PHASE 5 CLOSED** (state/context/payoff/representation foundation complete)
- [✓] Phase 6     Interaction Engine        (F-020 APPROVED edge=Event×Config; F-021 no universal edge)
- [✓] **PHASE 6 CLOSED** (edge = Event × Configuration confirmed)
- [✓] Phase 6.5   Configuration Engine      (atomic unit; F-022 bad-configs-persist; F-023 ranking)
- [✓] **RESEARCH FOUNDATION CLOSED** (states→transitions→age→events→Event×State→Configuration→persistence)
- [✓] Phase 7     Confidence Engine         (CCS; F-024 APPROVED; F-025 Magnitude×Availability; Principle 25)
- [✓] Phase 8     Opportunity Engine        (hypothesis REJECTED; F-022→Core Principle; P26; reframed remove-bad-first)
- [✓] Phase 9     Edge Lifecycle Engine     (F-028 every edge has a lifecycle; edge non-stationary; survivability metric)
- [✓] Phase 10    Edge Drift Engine         (F-027 APPROVED; environment does NOT explain decay; F-029 stochastic?)
- [✓] Phase 11    Edge Reality Test         (H0 not rejected; F-029 APPROVED — market non-stationary)
- [✓] Phase 12    Event Reality Framework   (0/5 universal; EURUSD Candidate Alpha; F-030/F-031; Principle 30)
- [✓] Phase 13    Contextual Alpha Framework (EXPLORATORY; P30/F-030/F-031 confirmed; objects → hypotheses; F-032)
- [✓] Phase 14    Contextual Alpha Confirmation (0/282 survive FDR; F-032 confirmed; Representation Failure)
- [✓] Phase 15    Representation Audit      (standalone insufficient; verdict corrected; variables retained; F-034)
- [✓] Phase 16    Representation Interaction Audit (F-035: Event×context, not context×context; Event=anchor)
- [✓] Phase 17    Event-Centric Representation (FULLY APPROVED; Architecture V6; F-036; Principle 38; Event Representation Family)
- [✓] Phase 18    Event Taxonomy            (F-037 partial, F-038; some events have sub-events; 0/17 edge → P40)
- [✓] Phase 19    Taxonomy Robustness Audit (0 robust subtypes; representation not algorithm-invariant; P41/42/43)
- [✓] Phase 20    Representation Geometry Audit (manifold + robust normalization; P42/43 confirmed; P44; F-039; end of Repr. Discovery Era)
- [✓] Phase 21    Representation Operationalization (APPROVED; representation SURVIVES OOS; F-039 approved; P45/46/47; end of Repr. Engineering Era; "Alpha Era" retracted)
- [✓] Phase 22    Semantic Taxonomy (APPROVED; clusters → market language; vocabulary repeats cross-event; P48/49/50; F-040; R²-drop NOT a failure)
- [✓] Phase 23    Semantic Consistency Audit (APPROVED; Emerging Core Vocabulary; Compression consistent cross-event; P51/52; F-041; Market Primitives; end of Semantic Engineering Era)
- [✓] Phase 24    Market Primitive Validation (APPROVED; F-041 REJECTED; primitives = ecology not causal; P53/54/55; F-042; end of Market Primitive Discovery)
- [✓] Phase 25    Ecology Interaction Framework (APPROVED; F-042 REJECTED; ecology = background property; P56/57; end of Market Understanding Era → Decision Theory)
- [✓] Phase 26    Decision Value Framework (FULLY APPROVED; 0/9 Selection-DV OOS; Prediction≠Decision≠Explanation; P58–62; **END of Chapter One**; doctrine split)

---

## Next Phase Queue

> **Market-discovery FROZEN (Principle 62).** Hakuna Phase ya market. Frontier = **Decision Science (Chapter 2)**.
> Chief amendment: Decision Science **inaanza na Evidence**, sio decisions.

- [✓] Decision Doctrine V1 → V2 → **V3** *(Evidence-first; split; 3-layer immutable object + operations; P63–70)*
- [✓] **D0  Evidence Theory** *(APPROVED — `evidence_object.py`; 3-layer value-object Evidence/lifecycle/sufficiency)*
- [✓] **D1  Evidence Operations** *(APPROVED — `evidence_operations.py`; pure ops; provenance graph; conflict taxonomy; readiness)*
- [✓] **D2  Evidence Sets** *(APPROVED — `evidence_set.py`; collection/identity/dedup; order-invariance; set reliability)*
- [✓] **D3  Evidence Snapshots** *(ACTIVE — `evidence_snapshot.py` + `reports/evidence_snapshot_report.md`; canonical Decision input; temporal conflict; readiness @T)*
- [ ] D4  Decision Families *(BLOCKED/DEFERRED — select/abstain/size/… on Snapshots; after Evidence Layer closed)*
- [ ] D5  Decision Quality *(BLOCKED — per-decision OOS + FDR)*
- [ ] D6  Portfolio Decisions *(BLOCKED — allocation; ranking ≠ allocation)*
- [ ] D7  Live Decision Engine *(BLOCKED — consumes Snapshots; production-agnostic)*
- [ ] P70 Confidence model · P74 Temporal-vs-structural conflict · P78 Redundancy-vs-duplication *(OPEN — design)*
- [ ] Phase 5.12  Liquidity Event Validation *(QUEUED — H-06; market, reopen only if a decision needs it)*
- [ ] ML *(BLOCKED — serves a proven decision, not a representation)*

---

## Open Questions

**Q-001 — Does Context improve more than one Event Family?**
Status: **CLOSED — APPROVED** (F-006)
Evidence: `context_generalization_report.md` (Pullback + Breakout + Mean Reversion)

**Q-002 — Do Volume Bars improve signal quality?**
Status: ANSWERED — stability REJECTED (R-002); INFORMATION APPROVED (F-007)

**Q-003 — Do Volume Bars add INFORMATION (not stability)?**
Status: **CLOSED — APPROVED** (F-007)
Evidence: `volume_information_report.md` (18/18 dim×pair, predictability ∨ context)

**Q-004 — How do the 9 events occur inside context?**
Status: ANSWERED (occurrence mapped) — `event_diagnostics_report.md`
Note: frequency/state/age/transition distributions halali; lakini 'favorable'
metric ilikuwa permissive mno -> Q-005.

**Q-005 — Does Context Meaningfully Filter Events?**
Status: **CLOSED — APPROVED as RANKING** (F-008)
Evidence: `context_selectivity_report.md` (monotonic decile-EV, 3/3 events).
Resolution: Context is a RANKING engine, not a binary filter (Principle 13).

**Q-006 — Which event benefits most from context ranking?**
Status: **CLOSED — APPROVED** (F-009)
Evidence: `event_context_matrix_report.md` (Tier 1: MR/PB/DPB/TC; Top10 EV>0).

**Q-007 — What barrier/vertical and outcome odds for Tier 1 events?**
Status: PARTIAL — `triple_barrier_design_report.md` delivered, BUT P(TP) flat
across context deciles (assumption "context → higher P(TP)" refuted). Phase 5 reopened.

**Q-008 — Does Context Improve Probability or Payoff Distribution?**
Status: **CLOSED — PAYOFF** (F-010)
Evidence: `outcome_decomposition_report.md` (ΔP(win) ≈ +3pp; EV via payoff, 4/4).

**Q-009 — Why does context cause reward expansion / loss compression?**
Status: PARTIAL — `payoff_attribution_report.md` gives MARGINAL drivers
(volatility/activity), but marginal ≠ importance (F-012). Causality needs interactions.

**Q-010 — Is the edge in feature interactions (not single components)?**
Status: **CLOSED — YES** (F-012, confirmed F-013)
Evidence: `component_interaction_report.md` (16/16 joint > marginal; lifecycle effect).

**Q-011 — Do interactions survive cross-market (universal vs local)?**
Status: **CLOSED — LOCAL** (F-014)
Evidence: `interaction_stability_report.md` (0/20 universal). Universal rules do
NOT exist in coordinate space.

**Q-012 — Do natural latent structures exist in market state vectors?** (reframed)
Status: **CLOSED — YES** (F-016)
Evidence: `latent_structure_report.md` (EV gap +0.126 vs null; 3/4 clusters recur).

**Q-013 — What does the rare state do? Does it change payoff?**
Status: PARTIAL — structure done (`rare_state_analysis.md`); PAYOFF pending (5.10R)
Needed: OHLC re-run → signed return/MAE/MFE/triple barrier/holding (F-017 gate).

**Q-014 — Are latent structures algorithm-independent?**
Status: **CLOSED — NO** (F-018 reframes the question)
Evidence: `cluster_robustness_report.md` (ARI 0.12). Reframed: economic meaning,
not cluster identity → **Q-015**.

**Q-015 — Are latent structures representation-robust?**
Status: EXPLORATORY (5.11B) — not an acceptance criterion (F-018 reframed to Decision Robustness)

**Q-016 — Are rare states liquidity / execution-risk events?**
Status: OPEN (H-06; H-05 payoff-state REJECTED)
Needed: Phase 5.12 (spread +12σ, returns flat → execution risk, not payoff).

**Q-017 — Does the latent representation improve decision quality?**
Status: **CLOSED — YES (selection)** (F-019; Phase 5.13)
Evidence: `representation_value_report.md` — improved EV-selection (not LogLoss →
Principle 21: selection > prediction).

**Q-018 — Is the edge in Event × Configuration?**
Status: **CLOSED — YES** (F-020 APPROVED)
Evidence: `event_state_interaction_report.md` — 4/5 events: EV changes substantially
with latent state; some Event×State beat the event alone. Gate to Opportunity Engine.

**Q-019 — Is the Configuration (not the Event) the atomic trading unit?**
Status: **CLOSED — YES** (F-021/F-022; Phase 6.5)
Evidence: `configuration_engine_report.md` — Configuration confirmed as atomic unit;
no component added below it. Configuration = Pair+Event+LatentState+Regime+Direction+
Execution Context.

**Q-020 — Is Confidence as valuable as Expected Payoff (does CCS beat EV-alone ranking)?**
Status: **CLOSED — YES** (F-024 APPROVED; Phase 7)
Evidence: `confidence_engine_report.md` — Top-25 EV vs CCS overlap 10/25; ρ ≈ +0.91.

**Q-021 — Can CCS be turned into a decision system (rank → portfolio) without ML?**
Status: **CLOSED — PARTIALLY (hypothesis rejected)** (Phase 8)
Evidence: `opportunity_engine_report.md` — CCS-selection does NOT make the portfolio
positive OOS (−0.757). Availability (OppScore) beats CCS-alone (3/4 budgets; only
budget-25 positive). Priority queue works without ML. Reframed: remove-bad-first
(F-022/P26) + survivability (Q-023).

**Q-023 — Does configuration survivability exist as an independent dimension, and is it predictable?**
Status: **CLOSED — edge non-stationary; survivability whole-sample-coupled to quality** (F-028; Phase 9)
Evidence: `survivability_engine_report.md` — median survival 1/6 windows; ρ(surv,EV)
≈+0.74 (descriptive). F-028 APPROVED (every edge has a lifecycle); F-027 reformulated
to a causal test (→ Q-024).

**Q-024 — WHY does an edge die, and can death be predicted one window ahead?**
Status: **CLOSED — environment does NOT explain it; death not predictable** (Phase 10)
Evidence: `edge_drift_report.md` — corr(Δenv, ΔEV)≈0; death not predictable one window
ahead (lift ≈ 0); F-027 APPROVED (ρ≈0.03); opened F-029 (stochastic) → Q-025.

**Q-025 — Does a real persistent edge exist beyond random expectation (H1 vs H0)?**
Status: **CLOSED — aggregate H0 not rejected; market non-stationary** (F-029; Phase 11)
Evidence: `edge_reality_report.md` — survivors 9 vs null 4.6 (p=0.050, inside CI);
randomized-time 39 ≫ 9 → non-stationarity. mean_reversion P(obs>random)=100% (subgroup,
not pursued alone). → Q-026.

**Q-026 — Which events have repeatable statistical existence, and under what conditions?**
Status: **CLOSED — none universal; edge is conditional (EURUSD)** (F-030/F-031; Phase 12)
Evidence: `event_reality_report.md` — 0/5 universal; mean_reversion×EURUSD (P100) &
deep_pullback×EURUSD (P97) Candidate Alpha; directional skill cost/context-relative. → Q-027.

**Q-027 — Which context variables are an alpha's IDENTITY vs modifiers, and where in the hierarchy is the alpha born?**
Status: **CLOSED — exploratory only; identity test insufficient** (Phase 13)
Evidence: `contextual_alpha_report.md` — context↑→EV↑ (supports P30); but leave-one-out
≠ identity proof (pair may be proxy); 30 objects = selection/multiple-comparisons. → Q-028.

**Q-028 — Does even one Contextual Alpha Hypothesis survive prospective OOS (pre-registered, FDR-controlled)?**
Status: **CLOSED — NO (0/282 survived); = representation failure** (F-032 confirmed; F-033; Phase 14)
Evidence: `contextual_alpha_confirmation_report.md` — 0 survived BH-FDR. Reframed as
Current Representation Failure (Principle 33), not absence of alpha. → Q-029.

**Q-029 — Has the current representation reached its limit (or is it the bottleneck)?**
Status: **CLOSED (partially) — no STANDALONE incremental contribution; standalone test insufficient** (Phase 15)
Evidence: `representation_audit_report.md` — age/traj/trans/persist add no standalone R²;
redundancy expected (F-034). Verdict corrected (NOT "near limit"). Interaction test → Q-030.

**Q-030 — Do the doctrine variables gain power through INTERACTION / hierarchy / calibration / stability?**
Status: **CLOSED — via Events, not via each other** (F-035; Phase 16)
Evidence: `representation_interaction_report.md` — Event×Trajectory/Volatility/Activity ✅;
context×context (Age×Transition etc.) ❌. Event is the anchor. → Q-031.

**Q-031 — Does each Event have its own context, and should representations be event-specific?**
Status: **CLOSED — YES (Event Representation Family)** (F-036; Principle 38; Phase 17)
Evidence: `event_centric_representation_report.md` — Event is anchor; 5 event-specific
context vars; MR{activity,pair,spread} ≠ Breakout{pair,session,vol,spread}. No universal
representation. → Q-032.

**Q-032 — Does each Event contain latent sub-events with distinct statistical identities?**
Status: **CLOSED — SOME do (event-dependent)** (F-037 partial, F-038; Phase 18)
Evidence: `event_taxonomy_report.md` — trend_continuation (k=4) & breakout (k=3) yes;
others no; 0/17 subtypes had edge (taxonomy ≠ alpha, P40). → Q-033.

**Q-033 — Are the discovered subtypes robust (algorithm-independent, stable, OOS-persistent) or KMeans artifacts?**
Status: **CLOSED — NOT robust; representation not algorithm-invariant** (Principle 41/42/43; Phase 19)
Evidence: `taxonomy_robustness_report.md` — cross-algo ARI 0.08–0.30; best-k unstable;
0 robust subtypes; KMeans split-half 0.97 but cross-algo weak (stable≠true). → Q-034.

**Q-034 — Does the current feature space (geometry) allow a true taxonomy to emerge?**
Status: **CLOSED — YES via robust-normalization + manifold (in-sample)** (P42/43 confirmed; P44; Phase 20)
Evidence: `representation_geometry_report.md` — coordinate separability weak; manifold ARI
0.89–0.99 & silhouette to 0.79; robust > z-score. Representation limitation, not ontology. → Q-035.

**Q-035 — Does the manifold representation operationalize OOS without leakage (Nyström, rolling)?**
Status: **CLOSED — YES, the representation SURVIVES OOS** (Phase 21; F-039 approved; P45)
Evidence: `representation_operationalization_report.md` — Nyström OOS silhouette 0.45–0.64
(survives; not killed by leakage); leak gap +0.19…+0.33 everywhere (in-sample was inflated);
1 full (trend_continuation) / 3 marginal / 1 fail (deep_pullback); operationally (not
statistically) stable. Chief: a surviving representation is a victory, not alpha. → Q-036.

**Q-036 — Are the latent clusters semantically interpretable in market language?**
Status: **CLOSED — YES (interpretability), with a caveat on predictive value** (Phase 22; P46/47/48)
Evidence: `semantic_taxonomy_report.md` — clusters get concrete market labels (Compression,
High-Volatility Regime, Balanced Flow…); vocabulary repeats cross-pair; R²(label) drops vs
cluster IDs. Chief: R²-drop is NOT a failure (Principle 48 — semantics = interpretability, not
prediction). New question: is the vocabulary the same across events? → Q-037 / F-040.

**Q-037 — Is the semantic vocabulary stable and universal (cross-pair, cross-event, data-driven)?**
Status: **CLOSED — EMERGING, not universal** (Phase 23; P51/52; F-041)
Evidence: `semantic_consistency_report.md` — 2/5 labels consistent; **Compression** the only one
truly consistent cross-event; stable under threshold perturbation (ARI ≈ 0.89); data-driven
recoverable (ARI ≈ 0.62, intentionally imperfect — P52). Chief: not "universal" but an **Emerging
Core Vocabulary**; Compression is a **market primitive**, not a label. → Q-038 / F-041.

**Q-038 — Is a market primitive (Compression) a mechanism or a description (cause vs consequence)?**
Status: **CLOSED — DESCRIPTION (ecological), not mechanism** (Phase 24; F-041 rejected; F-042)
Evidence: `market_primitive_validation_report.md` — event-free clustering did not reproduce
Compression; precedence lifts ≈ 1.0 (no prediction). Chief: primitives describe the *environment*
of events (ecology), they do not generate them (P53/54/55). → Q-039 / F-042.

**Q-039 — How do the ecology (primitive) and event layers interact?**
Status: **CLOSED — they don't (ecology is background)** (Phase 25; F-042 rejected; P56/57)
Evidence: `ecology_interaction_report.md` — JS ≈ 0 (ecology does not discriminate events); ΔBrier
≈ 0 (no calibration value); no weighting decision value. Ecology is a background property, not a
conditioning layer. Primitive Research paused. → Q-040 (decision theory).

**Q-040 — Which structure changes a DECISION out-of-sample (not just prediction/explanation)?**
Status: **CLOSED (for the SELECTION decision) — none of 9 variables; the question was too narrow**
(Phase 26; P58/59/60; doctrine split)
Evidence: `decision_value_framework_report.md` — 0/9 Selection-DV OOS despite good PV/XV →
Prediction ≠ Decision ≠ Explanation (P58). Chief: this is "no evidence of **Selection** Decision
Value under the metric used", not "no decision value" (P60 — decision is a family). The gap is
decision theory, not market structure → ELITEFX splits into Market + Decision domains. → Q-041.

**Q-042 — How is the Evidence Object specified (fields, lifecycle, conflict, aggregation, sufficiency)?**
Status: **CLOSED — APPROVED with amendments** (D0; P67–70)
Evidence: `evidence_theory_report.md` — 3-layer object (Claim/Quality/Operational), lifecycle,
sufficiency. Chief amendments: P67 (3 layers), P68 (immutable; aggregation = operation), P69
(decision-ready ≠ trade-ready), P70 OPEN (confidence = model). Bug fixed (coverage ≤1). → Q-043.

**Q-043 — How does evidence MOVE through the system (operations on the immutable object)?**
Status: **CLOSED — APPROVED with amendments** (D1; P71–75)
Evidence: `evidence_operations_report.md` — pure ops (aggregate/filter/merge/expire/split), audit-
trail preserved, immutability (by-convention + freeze), conflict taxonomy, readiness-change. Chief:
transformations pure (P71); provenance = graph (P72); readiness = snapshot (P73); temporal conflict
OPEN (P74); Evidence = value objects (P75). → Q-044.

**Q-044 — What is an Evidence Set, and does it have its own reliability and readiness?**
Status: **CLOSED — APPROVED with amendments** (D2; P76–79)
Evidence: `evidence_set_report.md` — collection keyed by value-object identity; order-invariant
aggregate (set ≠ sequence, P76); dedup by id; set reliability; snapshot readiness. Chief: decisions
operate on snapshots (P77); snapshot = canonical input (P79); redundancy ≠ duplication (P78 OPEN);
"confidence" → "reliability". → Q-045.

**Q-045 — What is an Evidence Snapshot (the canonical Decision-Layer input)?**
Status: OPEN (D3 Evidence Snapshots) — ACTIVE
Needed: `evidence_snapshot_report.md` — snapshot definition (Q1, immutable as-of-T view); fields
(Q2); readiness @T (Q3); temporal conflict P74 (Q4, older-vs-newer, distinct from structural);
canonical input = Snapshot (Q5, P79). Completes the Evidence Layer; Decision Families (D4) unblocks
only after this is approved.

**Q-041 — Does any variable carry decision value under a NON-selection decision (abstention/sizing/…)?**
Status: **DEFERRED** (Chief — until after D0 Evidence Theory; was DQ-1)
Needed: a decision-family value audit (D2) — OOS Decision Value for abstention/sizing/portfolio, not
just selection (Principle 60). Deferred because the decision family is not yet defined; Evidence
Theory (D0) comes first.

**Q-022 — Does state trajectory (momentum) carry information beyond current state?**
Status: OPEN (F-026; after Phase 8)
Needed: state-momentum study — LOW→NORMAL→HIGH vs HIGH→HIGH→HIGH (same endpoint,
different trajectory). Next research hypothesis, parallel to the decision pipeline.

**H-07 — Negative Edge is more stable than Positive Edge.**
Status: **CLOSED — APPROVED → F-022** (Phase 6.5). Confirmed: train-positive→positive
≈42% vs train-negative→negative ≈66%. Bad configurations persist more than good ones.

---

## Doctrine Amendment Log

- 2026-06-23 — V5.2 created (Context first-class; STATE→AGE→TRANSITION→EVENT).
- 2026-06-23 — Age = CALIBRATOR (sio predictor). Finding F amended (R-001).
- 2026-06-23 — Principle 03: Context must prove trading relevance (Prediction ≠ Economic Value).
- 2026-06-23 — Principle 12: **Context Is A Filter** (sio alpha source).
- 2026-06-23 — Volume Bars = Alternative Representation, Status UNPROVEN (R-002 rejected stability).
- 2026-06-24 — **V5.3**: F-006, F-007. Volume Bars = "concentrate information; Information Density > Calendar Uniformity".
- 2026-06-24 — Phase 3 context 'favorable' metric too permissive (~99%); no F-008 yet; Q-005 opened.
- 2026-06-24 — **F-008** Context = Ranking Engine; **Principle 13** (Context Ranking) added to V5.3.
- 2026-06-24 — **V5.4**: F-009 (context sensitivity event-specific); Event Priority Tiers; "Profitable ≠ Tradable Edge"; Phase 5 Triple Barrier (Tier 1).
- 2026-06-24 — Phase 5 REOPENED: P(TP) flat across deciles refutes "context → higher P(TP)". No F-010 yet; Q-008 opened; Phase 5.5 Outcome Decomposition.
- 2026-06-24 — **V5.5**: F-010 (Context = Payoff Filter), F-011 (two payoff mechanisms: Group A reward / Group B loss); Expected Payoff Engine direction; roadmap Outcome→Payoff→Lifecycle→ML.
- 2026-06-25 — **V5.6**: F-012 (interactions, not individual features); Driver ≠ Gatekeeper; Interaction Engine inserted; Payoff Engine FROZEN.
- 2026-06-25 — **V5.7**: F-013 (State Age = Lifecycle Variable); three categories (Driver/Gatekeeper/Lifecycle); Market Lifecycle Model; Context Score → Market State Vector.
- 2026-06-25 — **V5.8**: F-014 (interactions pair-specific; universal rules falsified); F-015 (universal mechanisms, local coordinates — hypothesis); Mechanism Layer; "learns mechanisms, not cells".
- 2026-06-25 — **V5.9**: Phase 5.9 mechanism method REJECTED (human taxonomy = verification, not discovery; NO HUMAN MARKET THEORY). F-015 reframed "Latent Market Structures" (OPEN). Mechanism Library → Latent State Library. Architecture: Latent Structure Discovery (unsupervised).
- 2026-06-26 — **V5.10**: F-016 (latent structures exist, APPROVED); F-017 (rare states, hypothesis); **Principle 18** (algorithm independence); Cluster ≠ State → Latent State Candidate→Validated→Operational; State-based → **Market Configuration-based Trading**. OHLC added to state cache.
- 2026-06-26 — **V5.11**: Principle 18 AMENDED (economic meaning, not cluster identity); **F-018** (representation robustness > cluster identity); **Principle 19** (no finding without payoff/decision-quality impact); F-017 → Experimental; **H-05** (rare states = liquidity events).
- 2026-06-26 — **V5.12** (Trading Science): State Engine v1 APPROVED; old Principle 18 (Algorithm Independence) **REMOVED** → new Principle 18 (Decision Quality > Algorithm Agreement); Principle 19 rewritten (no feature/state/representation survives without improving EV/Decision Quality); F-018 → **Decision Robustness**; **H-05 REJECTED**, **H-06** opened (rare = execution risk); Phase 5.13 Representation Value.
- 2026-06-26 — **V5.13**: **PHASE 5 CLOSED**. F-019 (Value Law); F-020 (Event × Configuration, Experimental); **Principle 20** (feature competition); **Principle 21** (Selection > Prediction); new pipeline (…→ Interaction Engine → Expected Payoff → Opportunity Ranking); acceptance rule (Event × Config → Payoff); Phase 6 Interaction Engine.
- 2026-06-26 — **V5.14**: **PHASE 6 CLOSED**. **F-020 APPROVED** (edge = Event × Configuration, 4/5 events); **F-021** (no Event has universal edge — edge only inside a COMPLETE Market Configuration); **Principle 22** (opportunity = Configuration, never an Event); Market Configuration **redefined** = Event + Latent State + Pair + Regime + Direction + Execution Context (atomic trading unit); **H-07** (negative edge more stable than positive); new acceptance rule (Market Configuration → Expected Payoff, not Indicator → BUY); Phase 6.5 Configuration Engine. ML target appears but not reached.
- 2026-06-26 — **V5.15**: **RESEARCH FOUNDATION CLOSED**. **H-07 → F-022 APPROVED** (bad configurations more persistent than good: train+→+ ≈42% vs train−→− ≈66%); **F-023** (ranking is the native language of the Opportunity Engine — population, not rule); **F-024 OPEN** (confidence as valuable as Expected Payoff); **Principle 23** (rank Configurations, don't classify Trades); **Principle 24** (no ranking by Expected Payoff alone); Configuration = final atomic unit (no component below it); pipeline Configuration → **Confidence Engine** → Opportunity Engine; Phase 7 Confidence Engine (CCS). ML target = Configuration Score.
- 2026-06-27 — **V5.16**: **F-024 APPROVED** (CCS-ranking ≠ EV-ranking; Top-25 overlap 10/25); **F-025 APPROVED** (Edge has Magnitude AND Availability — portfolio return needs frequency, not magnitude alone); **Principle 25** (Opportunity Score = Quality × Availability); **F-026 OPEN** (state trajectory/momentum carries information beyond state value); **Gap 3 CLOSED** (absolute distributions show pair individuality); architecture gains **Portfolio Engine** (Configuration → Confidence → Opportunity → Portfolio; ranking ≠ allocation); Phase 8 Opportunity Engine (CCS → decision, no ML). From knowledge to decision.
- 2026-06-27 — **V5.17**: **Phase 8 hypothesis REJECTED by data** (CCS-selection not positive OOS) → doctrine changes, not data. **F-022 promoted Finding → CORE PRINCIPLE**. **Principle 26** (capital preservation before opportunity discovery — answer "where NOT to trade" first). **Principle 25 enhanced**: Opportunity = Quality × Availability × **Survivability**. **F-027 OPEN** (survivability independent of quality). Opportunity Engine **reframed** (remove bad → rank survivable → allocate). Full architecture (Market Data → … → Confidence → **Survivability** → Opportunity → Portfolio → Execution). Phase 9 Survivability Engine (rolling WF, no ML).
- 2026-06-27 — **V5.18**: **edge non-stationary** (Phase 9: median survival 1 window; ~2% survive all). **Survivability Engine → Edge Lifecycle Engine** (framework; survival = one metric). **F-028 APPROVED** (every trading edge has a lifecycle: birth→growth→decay→death). **F-027 REFORMULATED** ("Early Quality may not predict Future Survivability" — causal, not whole-sample). **Principle 27** (prefer living edges over historically profitable edges). Architecture: Confidence → **Edge Lifecycle** → Opportunity → Portfolio → Execution. Phase 10 Edge Drift Engine (WHY edge dies; no ML — else trained on "historical corpses"). Project reframed as **Adaptive Market Intelligence System**.
- 2026-06-27 — **V5.19**: **F-027 APPROVED** (reworded: "Early Edge Quality does not predict Future Edge Persistence"; causal ρ≈0.03). Environment (ATR/spread/activity) does NOT explain decay. **F-029 OPEN** (edge decay may be stochastic, not deterministic). **Principle 28** (no adaptive system before proving persistent edge beats random expectation). ⚠️ Do not assume a hidden variable before testing edge reality. Architecture: …→ Edge Lifecycle → **Edge Reality Validation** → Opportunity. Phase 11 Edge Reality Test (H1 real vs H0 noise; null/permutation/bootstrap; no ML). Everything (Opportunity v2, ML, Portfolio) BLOCKED until edge proven real.
- 2026-06-28 — **V5.20**: Phase 11 — two questions answered (aggregate edge NOT proven, H0 stands; market IS non-stationary). **F-029 APPROVED** (reworded: "Edge decay is primarily a consequence of market non-stationarity, not merely of random sampling" — randomized-time survivors 39 ≫ observed 9). **Principle 29** (every event is a statistical hypothesis, not a trading signal). mean_reversion-only **rejected** (subgroup / multiple-comparisons). Architecture: Market Data → Event Library → **Event Reality Validation** → Context → Opportunity → Portfolio. Phase 12 Event Reality Framework (prove which events exist: null/perm/bootstrap/Bayesian + pair×event×state + combos; no ML).
- 2026-06-28 — **V5.21** (biggest doctrine change since Phase 1): Phase 12 — aggregate 0/5 universal, but mean_reversion×EURUSD (P100) & deep_pullback×EURUSD (P97). Discovery: **an event is a conditional object, not universal**. **Principle 30** (an event does not exist independently of its market context — context = IDENTITY, not a filter). **F-030** (edge existence is conditional, not universal). **F-031** (only contextual events exist). Terminology: Event → **Contextual Event**; Proven Edge → **Candidate Alpha** (until pre-registered OOS). spread = ecology variable, not just cost. Architecture: **Contextual Event Library**. Phase 13 Contextual Alpha Framework (Contextual Alpha Objects; identity vs modifier; hierarchy; no ML). Mean Reversion Strategy forbidden (subgroup).
- 2026-06-28 — **V5.22**: Phase 13 accepted as **EXPLORATORY only** (P30/F-030/F-031 confirmed). "30 Candidate Alpha" **rejected as alpha** (selection bias; multiple comparisons; UNKNOWN identity; leave-one-out ≠ proof, pair-as-proxy; no mechanism) → **Contextual Alpha Hypothesis / Research Candidates**. **Principle 31** (hypothesis until prospective validation). **Principle 32** (identity = independent explanatory power, not mere association). **F-032** (context refinement raises apparent edge AND false-discovery risk). Terminology: Candidate Alpha → **Contextual Alpha Hypothesis**. Phase 14 Confirmation Framework (pre-register IS → future OOS → Benjamini–Hochberg FDR → exclude UNKNOWN → independent-contribution; no ML).
- 2026-06-28 — **V5.23**: Phase 14 — 282 pre-registered, UNKNOWN excluded, future OOS, BH-FDR → **0 survived**. **F-032 CONFIRMED** (30→0 = selection inflation). Chief reframes: this is **Current Representation Failure**, NOT "No Alpha" — only ONE representation tested (Event+Pair+Vol+Spread+Session). **Principle 33** (failure to validate ⇒ representation failure until proven otherwise). **F-033** (a representation can fail while exploitable structure exists). "More data / new ecology" rejected as premature. Phase 15 Representation Audit (assumptions, missing doctrine vars, incremental info, redundancy, minimal sufficient representation; no ML, no new data).
- 2026-06-28 — **V5.24**: **Phase 15 verdict REJECTED** (Chief): standalone base+variable-moja test ≠ the hierarchical representation the doctrine builds (State→Age→Transition→Trajectory). **Principle 34** (a variable may contribute via interaction/calibration/stability even if standalone predictive contribution is negligible). **Principle 35** (representation quality is not judged solely by predictive gain). **F-034** (redundancy among hierarchical variables is expected, not uselessness — persistence is a derivative of age). Phase 15 conclusion corrected to "no evidence of incremental STANDALONE contribution"; variables NOT removed. Phase 16 Representation Interaction Audit (interactions, hierarchy, Brier calibration, fold-stability, cross-pair transferability, cross-regime robustness; no ML).
- 2026-06-28 — **V5.25**: Phase 16 discovery — Event×Trajectory/Volatility/Activity significant, but context×context (Age×Transition/Trajectory) not. **F-035** (state variables derive meaning through interaction with EVENTS, not with one another). **Principle 36** (Events are the semantic anchors; context acquires value only attached to an Event). **Principle 37** (low S/N markets: evaluate by robust significance + OOS repeatability, not effect size alone). Architecture flipped to **Event → Context** (each event has its own). Phase 16 hierarchy wording corrected (standalone showed nothing; Event-attached hierarchy carries info). Phase 17 Event-Centric Representation (per-event context; minimal event-specific reps; no ML).
- 2026-06-28 — **V6.0** (ELITEFX Architecture V6; major version): Phase 17 FULLY APPROVED — context has no existence of its own; the Event creates the meaning of context. **F-036** (market variables are conditional entities; info content depends on the governing Event; Variable → Conditional Variable). **Principle 38** (no universal market representation; each Event defines its own representation space). Concept **Market Representation → Event Representation Family** (Pullback/Breakout/MR/… each with its own ontology). **F-037 OPEN** (events may contain latent sub-events). Architecture V6: Market → Event Detection → **Event Taxonomy** → Event-Specific Representation → Reality Validation → Opportunity → Portfolio → Execution. ML target = one model per event subtype. Goal: family of event-dependent representations, then family of event-dependent models. Phase 18 Event Taxonomy (no ML).
- 2026-06-28 — **V6.1**: Phase 18 — trend_continuation (k=4) & breakout (k=3) have sub-events; others none; 0/17 subtypes had edge. **F-037 → PARTIALLY APPROVED** (reworded: some events exhibit distinguishable sub-events; taxonomy event-dependent, not universal). **F-038** (market taxonomy is hierarchical and event-specific; different events have different latent complexity). **Principle 39** (market ontology shall never be inferred from a single clustering algorithm). **Principle 40** (a valid market taxonomy is not evidence of tradable alpha). Phase 19 Taxonomy Robustness Audit (KMeans/GMM/Agglomerative ARI/NMI + stability + OOS persistence) BEFORE any OOS edge confirmation; no ML.
- 2026-06-29 — **V6.2**: Phase 19 — 0 robust subtypes (cross-algo ARI 0.08–0.30; best-k unstable 50–67%). Chief: NOT "KMeans artifacts/ontology failure" but "current representation is not algorithm-invariant" (methodology failure). Paradox (KMeans split-half 0.97 yet cross-algo weak) → **Principle 41** (internal stability ≠ external validity). **Principle 42** (robust clustering requires robust representation before robust algorithms). **Principle 43** (algorithm disagreement → audit the representation, not reject the ontology). **F-038 → PARTIALLY APPROVED** (reworded; breakout k=3 retracted). "An algorithm cannot rescue a bad representation." Phase 20 Representation Geometry Audit (separability/normalization/manifold/algo-agreement; no ML).
- 2026-06-30 — **V6.3**: Phase 20 FULLY APPROVED — **end of the Representation Discovery Era**. Coordinate space weak (silhouette ~0.21–0.23, near/below null); robust normalization beats z-score for every event; manifold (Laplacian eigenmaps) strong (ARI up to 0.89–0.99; silhouette ~0.58–0.79). **Principles 42 & 43 CONFIRMED** (promoted proposed → confirmed; direct data support). **Principle 44** (normalization is part of the representation, not preprocessing — robust ≈0.33–0.35 vs z ≈0.22 vs percentile ≈0.17–0.19). **F-039 OPEN** (different events may need different geometries — breakout stayed weak). Careful wording: evidence now **favors representation limitation over ontology limitation** (ontology debate not closed until manifold confirmed OOS). Architecture += **Representation Family / Geometry Selection** (normalization + geometry are choices per event). Phase 21 Representation Operationalization (Nyström OOS, rolling walk-forward stability, leakage quantification; no ML). ~~Alpha Discovery Era opens after OOS-without-leakage passes~~ *(retracted by V6.4)*.
- 2026-06-30 — **V6.4**: Phase 21 **APPROVED** — **end of the Representation Engineering Era**. Representation **SURVIVES OOS** (Nyström silhouette 0.45–0.64, not killed by leakage). Chief: the leak gap is an **expected consequence, NOT the discovery**; the discovery is that the representation survives OOS. Chief **rejects** "the beginning of the Alpha Discovery Era" — premature; **"Alpha Discovery Era" retracted** — we remain in the **Market Understanding Era** (before Edge). **F-039 → APPROVED** (reworded: "Different Events require different geometric representations for operational deployment"; OOS silhouette range 0.452–0.640). **Principle 45** (operational robustness ≠ statistical proof of stability — say "operationally stable"; no hypothesis test of rolling stability). **Principle 46** (a market taxonomy is incomplete until its latent states are semantically interpretable). **Principle 47** (express representations in market language, not cluster identifiers). Architecture += **Semantics** layer (Taxonomy → Semantics → Reality Validation → Edge); discovery stays unsupervised, semantics is a post-hoc interpretation layer (not human theory driving clustering). Phase 22 Semantic Taxonomy (clusters → market language; interpretability/transfer/predictive value; no ML).
- 2026-06-30 — **V6.5**: Phase 22 **APPROVED** — clusters speak market language (Compression, High-Volatility Regime, Balanced Flow…) and the vocabulary repeats across pairs. Chief **corrects the verdict**: the collapse of `R²(label)` is **NOT a semantics failure** — semantics carries **interpretation (understanding)**, the representation carries information (prediction). **Principle 48** (semantic abstraction = interpretability, not necessarily predictive power). **Principle 49** (a market vocabulary must be stable across representations before it becomes doctrine — the profile→label map uses human-designed thresholds, so the vocabulary is not yet self-standing). **Principle 50** (interpretability and predictability are complementary, not interchangeable). **F-040 OPEN** (different events may share a common semantic vocabulary despite different geometries → possibly **Universal Market States**, not Event States — the real discovery). Architecture += **Semantic Consistency** (Semantics → Semantic Consistency → Reality Validation → Edge). No semantic labels in the Opportunity Engine until stable. Phase 23 Semantic Consistency Audit (cross-pair/event consistency; threshold stability; data-driven recoverability; universality vs event-specific geometry; no ML).
- 2026-06-30 — **V6.6**: Phase 23 **APPROVED** — **end of the Semantic Engineering Era**. Chief rewords "Universal Vocabulary" → **"Emerging Core Vocabulary"**: only 2/5 labels consistent; **Compression (Quiet Coil)** is the only one truly consistent cross-pair AND cross-event (within/overall ≈ 0.25); stable under threshold perturbation (ARI ≈ 0.89); data-driven recoverable (ARI ≈ 0.62, intentionally imperfect). **The real discovery:** Compression is not an event/pair/geometry — it is a **market condition** → the architecture inverts to Market → **Market Primitives** → Events → Representations. **Principle 51** (express market knowledge through reusable market primitives, not event-specific labels). **Principle 52** (a semantic system should preserve essential market concepts, not reproduce clustering exactly — the 0.62 ARI is good, not a failure). **F-041 OPEN** (a small set of universal market primitives may underlie multiple event families; candidate: Compression). **Alpha still deferred** with a new reason: unknown whether Compression is a **cause** or a **consequence**. Phase 24 Market Primitive Validation (event-free primitive construction; precedence; transitions; mechanism vs description; no ML).
- 2026-06-30 — **V6.7**: Phase 24 **APPROVED**; **F-041 REJECTED (current formulation)** — first formally closed hypothesis. Event-free construction did NOT reproduce Compression (most primitives → Equilibrium/Balanced Flow; only Mature Persistence had identity); precedence lifts ≈ 1.0. Chief: what failed is the **Universal** primitive layer, not the primitive layer; a primitive **describes the environment** of events, it does not predict/generate them. Transition `Mature Persistence → Balanced Flow` (P≈0.74) → primitives behave like **ecological states**. **Principle 53** (primitives describe the operating environment of events; not assumed to generate events). **Principle 54** (primitives belong to the **ecological layer**, not the event layer). **Principle 55** (ecological description and event prediction are distinct objectives). **F-042 OPEN** (primitives characterize **ecological conditions**, not universal causal mechanisms — replaces F-041). Architecture: Market Ecology → Primitives ‖ Event Families → Representations (two layers). **Alpha PAUSED** (layer interaction unknown). Implementer instruction: **do not chase the hypothesis** (no tuning k/algorithm to revive Compression). Phase 25 Ecology Interaction Framework (event×primitive distribution/representation/calibration/stability/weighting; no ML).
- 2026-06-30 — **V6.8**: Phase 25 **APPROVED**; **F-042 REJECTED** — the ecological-layer-with-value hypothesis failed. JS-divergence ≈ 0.000 (ecology does **not** discriminate events); ΔBrier ≈ 0 (0/5 events — no calibration value); weighting view → no decision value. Chief: ecology is a **background property** (like the weather), not a conditioning variable. Q2's r² ≈ 0.24 **rejected** as mechanical overlap (primitive built from same features). **Principle 56** (market ecology is a background property of the market, not an event discriminator). **Principle 57** (market primitives shall be treated as descriptive metadata unless independent decision value is demonstrated). **Primitive Research PAUSED** (further digging = hypothesis-chasing). **End of the Market Understanding Era** → **Decision Theory** turn: ELITEFX will no longer search for new market structure but for **structure that changes decisions**. Scientific caution: no decision value under current metrics ≠ proven useless. Architecture: Representation → Decision → Execution. Phase 26 Decision Value Framework (PV/DV/XV scoreboard; decision audit; Decision Graph; no ML).
- 2026-06-30 — **V6.9 + DECISION DOCTRINE V1 (THE SPLIT)**: Phase 26 **FULLY APPROVED** — **end of Chapter One**. Scoreboard: **0/9** variables with Selection Decision Value OOS despite good prediction/explanation → **Prediction ≠ Decision ≠ Explanation**. **Principle 58** (the three value dimensions are independent and never interchangeable). **Principle 59** (representations shall influence decisions only through evidence, never directly). **Principle 60** (decision value is decision-specific; failure under one decision ≠ failure under all — Phase 26 tested **selection** only; report wording corrected to "no evidence of **Selection** Decision Value under the metric used"). **Principle 61** (market research and decision theory are separate scientific domains, evolving independently). **Principle 62** (stop expanding market representations once they fail to change decisions). **Doctrine SPLIT** into two domains: **Market Doctrine V6.9** (Representation/Taxonomy/Semantics/Geometry — mature, market-discovery **FROZEN**) and **Decision Doctrine V1** (Evidence/Decision/Risk/Opportunity/Abstention/Sizing/Portfolio/Execution — the new frontier). Architecture: Market → Representation → Evidence → Decision → Execution → Feedback. No new market phases; Decision Science begins. No ML.
- 2026-06-30 — **DECISION DOCTRINE V2 (Evidence-first amendment)**: Chief **APPROVES The Split WITH ONE MAJOR AMENDMENT** — Decision Science is a **consumer** of Market Science, not an extension; the two meet at one object, the **Evidence Object**, which is the contractual **API** between domains. **Principle 63** (evidence is the contractual interface between Market and Decision Science — first principle of the domain). **Principle 64** (Decision Science shall not depend on how evidence was produced, only on its validity and uncertainty — production-agnostic). **Principle 65** (evidence is a first-class object with its own lifecycle, independent of representations). **Principle 66** (every decision must be traceable to explicit evidence objects — institutional auditability). Decision Doctrine restructured **Evidence-first**: **Part 1 Evidence Theory** precedes **Part 2 Decision Theory**. Inter-domain architecture: Market Science (Market→Representation→**Evidence Object**) ══API══ Decision Science (Evidence Object→Decision Engine→Execution→Feedback). Chapter-2 roadmap: **D0 Evidence Theory** → D1 Decision Objects → D2 Decision Families → D3 Decision Quality → D4 Portfolio Decisions → D5 Live Decision Engine. **Decision Family Audit DEFERRED** until after D0. **No Decision Engine until the Evidence Object spec is approved.** D0 delivers `evidence_object.py` (Evidence Object + lifecycle + inverse-variance aggregation + abstain-on-conflict + sufficiency) and `reports/evidence_theory_report.md`. No ML.
- 2026-06-30 — **DECISION DOCTRINE V3 (D0 APPROVED + amendments)**: Chief approves D0 ("best methodology report since we began — for the first time we defined a contract, not tried to prove the market"). Amendments before the doctrine closes: **Principle 67** (every Evidence Object consists of three layers — **Claim** [value/direction/source] + **Evidence Quality** [confidence/uncertainty/support/coverage] + **Operational State** [freshness/conflict/expiry]; the Decision Engine reads categories, not a flat list). **Principle 68** (Evidence Objects are immutable contracts; **aggregation is an external operation**, not part of the object — so Bayesian/Dempster-Shafer/voting can replace inverse-variance without changing the object). **Principle 69** (**decision-ready ≠ trade-ready**; terminology "decision-grade" → "decision-ready"). **Principle 70 OPEN** (confidence should come from an explicit, recalibratable **confidence model**, not be stored as a primitive fact — today's Φ(EV/SE) saturates at large n). **Conflict has a taxonomy** (intra/split-half · cross-pair · cross-timeframe · cross-engine), measured controlling for the other dimensions — not a scalar. D0 coverage bug fixed (coverage ≤1; per-series recency). **D1 Evidence Operations** opened (pure ops on immutable objects: aggregate/filter/merge/expire/split + audit trail + conflict taxonomy + readiness-change); **D2 Decision Families DEFERRED** until Object+Operations are closed. Delivers `evidence_operations.py` + `reports/evidence_operations_report.md`. No Decision Engine yet. No ML.
- 2026-06-30 — **DECISION DOCTRINE V4 (D1 FULLY APPROVED + amendments)**: Chief: "D1 is the first report that no longer talks about Forex — it talks about software architecture." D0+D1 = the formal **Evidence Layer**. **Principle 71** (evidence transformations shall be pure, deterministic and side-effect-free — Evidence behaves like a functional-programming object; the Decision Engine has no side effects). **Principle 72** (provenance shall be a **directed graph**, not a chronological log — aggregate/merge have parents, split has children). **Principle 73** (decision-readiness belongs to an **Evidence Snapshot**, not the immutable object — readiness changes over time; the object does not). **Principle 74 OPEN** (conflict shall distinguish **temporal contradiction** [yesterday bullish vs today bearish] from structural disagreement). **Principle 75** (Evidence Objects are **value objects with immutable identity** — content-derived id; enables dedup, graph nodes, language-independence). Logic gap closed: operations went Evidence→Evidence but never Evidence→**Set**; decisions are made on **Evidence Sets**, not single objects. **D2 Evidence Sets** opened (collection/identity/dedup; order-invariant aggregate; set confidence; snapshot readiness); **Decision Families DEFERRED** until the Evidence Layer is closed. Architecture: Evidence Objects → **Evidence Sets** → Decision → Execution. Delivers `evidence_set.py` + `reports/evidence_set_report.md` (+ value-object id & provenance-graph fields added to `evidence_object`/`evidence_operations`). No Decision Engine yet. No ML.
- 2026-06-30 — **DECISION DOCTRINE V5 (D2 FULLY APPROVED + amendments)**: **Principle 76** (evidence meaning is independent of insertion order — D2's order-invariant aggregate is "the first theorem of Decision Science": a Set is a *mathematical set*, not a sequence; historical lineage is represented separately via the provenance graph → Evidence **Semantics** vs Evidence **History**). **Principle 77** (decisions shall operate on **Evidence Snapshots**, not raw Evidence Objects). **Principle 78 OPEN** (statistical **redundancy ≠ identity duplication** — EURUSD H1 vs H4 are distinct ids but near-identical info; redundancy management still needed). **Principle 79** (the **Evidence Snapshot is the canonical input to the Decision Layer**). Terminology: "Set Confidence" → **"Set Reliability"** until the confidence model (P70) is closed. **D3 Evidence Snapshots** opened (immutable as-of-T view; fields; readiness @T; temporal conflict per P74; canonical input per P79) — this **completes the Evidence Layer** (Object→Operations→Set→Snapshot); **Decision Families DEFERRED** until D3 approved. Delivers `evidence_snapshot.py` + `reports/evidence_snapshot_report.md`. No Decision Engine yet. No ML.

---

## Approval Log

| Date | Item | Decision | By |
|------|------|----------|-----|
| 2026-06-23 | V5.2 doctrine + amendments 1–4 | APPROVED | Chief Quant |
| 2026-06-23 | Age = calibrator; H-01 rejected | APPROVED | Chief Quant |
| 2026-06-23 | F-005 Context improves event quality | APPROVED | Chief Quant |
| 2026-06-23 | Phase 1.95 Context Generalization | APPROVED (start) | Chief Quant |
| 2026-06-23 | Phase 2 Adaptive Volume Bars (design, no ML) | APPROVED (start) | Chief Quant |
| 2026-06-23 | F-006 Context value generalizes; Q-001 CLOSED | APPROVED | Chief Quant |
| 2026-06-23 | R-002 Volume bars → stable states | REJECTED | Chief Quant |
| 2026-06-23 | Phase 2.1 Volume Information Value | APPROVED (next) | Chief Quant |
| 2026-06-24 | F-007 Volume bars increase information density; Q-003 CLOSED | APPROVED | Chief Quant |
| 2026-06-24 | Phase 2 COMPLETE; doctrine V5.3 | APPROVED | Chief Quant |
| 2026-06-24 | Phase 3 Event Diagnostics | APPROVED (start) | Chief Quant |
| 2026-06-24 | Phase 3 Event Diagnostics (delivered) | CONDITIONALLY APPROVED | Chief Quant |
| 2026-06-24 | Phase 3.5 Context Selectivity | APPROVED (next) | Chief Quant |
| 2026-06-24 | F-008 Context = Ranking Engine; Q-005 CLOSED; Principle 13 | APPROVED | Chief Quant |
| 2026-06-24 | Phase 3.5 PASSED; Phase 4 Event × Context Matrix | APPROVED (start) | Chief Quant |
| 2026-06-24 | Phase 4 PASSED; F-009 event-specific sensitivity; Event Tiers; doctrine V5.4 | APPROVED | Chief Quant |
| 2026-06-24 | Phase 5 Triple Barrier (Tier 1 only, design, no ML) | APPROVED (start) | Chief Quant |
| 2026-06-24 | Phase 5 delivered (P(TP) flat by decile) | REOPENED | Chief Quant |
| 2026-06-24 | Phase 5.5 Outcome Decomposition (Tier 1, no ML) | APPROVED (start) | Chief Quant |
| 2026-06-24 | Phase 5.5 PASSED; F-010 Payoff Filter; F-011 two mechanisms; doctrine V5.5 | APPROVED | Chief Quant |
| 2026-06-24 | Phase 5.6 Payoff Attribution; Phase 6 Payoff Engine (queued) | APPROVED (start) | Chief Quant |
| 2026-06-25 | Phase 5.6 APPROVED w/ correction; F-012 interactions; Driver≠Gatekeeper; doctrine V5.6 | APPROVED | Chief Quant |
| 2026-06-25 | Phase 5.7 Component Interaction; Phase 6 Payoff Engine FROZEN | APPROVED (start) | Chief Quant |
| 2026-06-25 | Phase 5.7 APPROVED; F-013 Lifecycle Variable; Market Lifecycle Model; doctrine V5.7 | APPROVED | Chief Quant |
| 2026-06-25 | Phase 5.8 Interaction Stability; Phase 5.9 Market State Vector (queued) | APPROVED (start) | Chief Quant |
| 2026-06-25 | Phase 5.8 APPROVED; F-014 pair-specific (universal rules falsified); F-015 hypothesis; doctrine V5.8 | APPROVED | Chief Quant |
| 2026-06-25 | Phase 5.9 Mechanism Discovery; Phase 6 Mechanism Library (queued) | APPROVED (start) | Chief Quant |
| 2026-06-25 | Phase 5.9 (delivered) — human taxonomy, not discovery | NOT APPROVED (rework) | Chief Quant |
| 2026-06-25 | F-015 reframed "Latent Market Structures" (OPEN); doctrine V5.9 | APPROVED | Chief Quant |
| 2026-06-25 | Phase 5.9A Latent Structure Discovery (unsupervised, no ML) | APPROVED (start) | Chief Quant |
| 2026-06-26 | Phase 5.9A APPROVED; F-016 latent structures exist; F-017 hypothesis; Principle 18; doctrine V5.10 | APPROVED | Chief Quant |
| 2026-06-26 | Phase 5.10 Rare State Analysis + Phase 5.11 Cluster Robustness | APPROVED (start) | Chief Quant |
| 2026-06-26 | Phase 5.10 APPROVED/F-017 Experimental; Phase 5.11 NOT APPROVED; F-018; Principle 18 amended; Principle 19; H-05; doctrine V5.11 | APPROVED | Chief Quant |
| 2026-06-26 | State Engine v1 APPROVED; Rare State descriptive; Cluster Robustness exploratory only | APPROVED | Chief Quant |
| 2026-06-26 | Principle 18 REPLACED (decision quality); Principle 19 rewritten; F-018 Decision Robustness; H-05 REJECTED; H-06; doctrine V5.12 | APPROVED | Chief Quant |
| 2026-06-26 | Phase 5.13 Representation Value | APPROVED (start) | Chief Quant |
| 2026-06-26 | Phase 5.13 APPROVED; PHASE 5 CLOSED; F-019/F-020; Principle 20/21; doctrine V5.13 | APPROVED | Chief Quant |
| 2026-06-26 | Phase 6 Interaction Engine (Event × State) | APPROVED (start) | Chief Quant |
| 2026-06-26 | Phase 6 APPROVED (Scientific Milestone); PHASE 6 CLOSED; F-020 APPROVED; F-021 (no universal edge); Principle 22; Market Configuration redefined; H-07; doctrine V5.14 | APPROVED | Chief Quant |
| 2026-06-26 | Phase 6.5 Configuration Engine (Configuration Objects, no ML) | APPROVED (start) | Chief Quant |
| 2026-06-26 | Phase 6.5 APPROVED; RESEARCH FOUNDATION CLOSED; H-07→F-022; F-023; F-024; Principle 23/24; doctrine V5.15 | APPROVED | Chief Quant |
| 2026-06-26 | Phase 7 Confidence Engine (CCS: EV + Confidence + Persistence + Sample Quality, no ML) | APPROVED (start) | Chief Quant |
| 2026-06-27 | Phase 7 APPROVED; F-024 APPROVED; F-025 (Magnitude×Availability); Principle 25; F-026 OPEN; Gap 3 CLOSED; Portfolio Engine added; doctrine V5.16 | APPROVED | Chief Quant |
| 2026-06-27 | Phase 8 Opportunity Engine (CCS → decision, Quality × Availability, no ML) | APPROVED (start) | Chief Quant |
| 2026-06-27 | Phase 8 APPROVED (hypothesis rejected by data); F-022→Core Principle; Principle 26; Principle 25 +Survivability; F-027 OPEN; Opportunity Engine reframed; doctrine V5.17 | APPROVED | Chief Quant |
| 2026-06-27 | Phase 9 Survivability Engine (rolling walk-forward durability, no ML) | APPROVED (start) | Chief Quant |
| 2026-06-27 | Phase 9 APPROVED; edge non-stationary; F-028 (lifecycle); F-027 REFORMULATED; Survivability→Edge Lifecycle Engine; Principle 27; doctrine V5.18 | APPROVED | Chief Quant |
| 2026-06-27 | Phase 10 Edge Drift Engine (WHY edge dies; causal F-027; no ML) | APPROVED (start) | Chief Quant |
| 2026-06-27 | Phase 10 APPROVED; F-027 APPROVED (early≠future); F-029 OPEN (stochastic decay); Principle 28; Edge Reality Validation; doctrine V5.19 | APPROVED | Chief Quant |
| 2026-06-27 | Phase 11 Edge Reality Test (null/permutation/bootstrap; H1 vs H0; no ML) | APPROVED (start) | Chief Quant |
| 2026-06-28 | Phase 11 APPROVED; H0 not rejected; F-029 APPROVED (non-stationarity); Principle 29; mean_reversion-only rejected; doctrine V5.20 | APPROVED | Chief Quant |
| 2026-06-28 | Phase 12 Event Reality Framework (all events; null/perm/bootstrap/Bayesian; no ML) | APPROVED (start) | Chief Quant |
| 2026-06-28 | Phase 12 APPROVED; 0/5 universal; EURUSD Candidate Alpha; Principle 30; F-030/F-031; Event→Contextual Event; doctrine V5.21 | APPROVED | Chief Quant |
| 2026-06-28 | Phase 13 Contextual Alpha Framework (Contextual Alpha Objects; identity/modifier; no ML) | APPROVED (start) | Chief Quant |
| 2026-06-28 | Phase 13 = EXPLORATORY (P30/F-030/F-031 confirmed); 30 objects → hypotheses; Principle 31/32; F-032; doctrine V5.22 | APPROVED | Chief Quant |
| 2026-06-28 | Phase 14 Contextual Alpha Confirmation (pre-register/OOS/BH-FDR/independent-contribution; no ML) | APPROVED (start) | Chief Quant |
| 2026-06-28 | Phase 14 APPROVED; 0/282 survive FDR; F-032 confirmed; reframed Representation Failure; Principle 33; F-033; doctrine V5.23 | APPROVED | Chief Quant |
| 2026-06-28 | Phase 15 Representation Audit (assumptions/incremental info/redundancy/minimal set; no ML, no data) | APPROVED (start) | Chief Quant |
| 2026-06-28 | Phase 15 verdict REJECTED (standalone≠hierarchy); Principle 34/35; F-034; variables retained; conclusion corrected; doctrine V5.24 | APPROVED | Chief Quant |
| 2026-06-28 | Phase 16 Representation Interaction Audit (interactions/hierarchy/calibration/stability/transfer/robust; no ML) | APPROVED (start) | Chief Quant |
| 2026-06-28 | Phase 16 APPROVED; F-035 (state vars derive meaning via Events); Principle 36/37; Event→Context; doctrine V5.25 | APPROVED | Chief Quant |
| 2026-06-28 | Phase 17 Event-Centric Representation (per-event context; minimal event-specific reps; no ML) | APPROVED (start) | Chief Quant |
| 2026-06-28 | Phase 17 FULLY APPROVED (Architecture Change); ARCHITECTURE V6; F-036; Principle 38; F-037 OPEN; Event Representation Family; doctrine V6.0 | APPROVED | Chief Quant |
| 2026-06-28 | Phase 18 Event Taxonomy (latent sub-events per event; unsupervised; no ML) | APPROVED (start) | Chief Quant |
| 2026-06-28 | Phase 18 APPROVED; F-037 Partial; F-038; Principle 39/40 (taxonomy≠alpha); doctrine V6.1 | APPROVED | Chief Quant |
| 2026-06-28 | Phase 19 Taxonomy Robustness Audit (multi-algorithm + stability + OOS; no ML) | APPROVED (start) | Chief Quant |
| 2026-06-29 | Phase 19 APPROVED; 0 robust subtypes; Principle 41/42/43; F-038 Partial; breakout k=3 retracted; doctrine V6.2 | APPROVED | Chief Quant |
| 2026-06-29 | Phase 20 Representation Geometry Audit (separability/normalization/manifold/algo-agreement; no ML) | APPROVED (start) | Chief Quant |
| 2026-06-30 | Phase 20 FULLY APPROVED; end of Representation Discovery Era; Principle 42/43 CONFIRMED; Principle 44 (normalization = representation); F-039 OPEN; representation limitation favored over ontology; Representation Family/Geometry Selection; doctrine V6.3 | APPROVED | Chief Quant |
| 2026-06-30 | Phase 21 Representation Operationalization (Nyström OOS; rolling walk-forward; leakage quantification; no ML) | APPROVED (start) | Chief Quant |
| 2026-06-30 | Phase 21 APPROVED; representation SURVIVES OOS; end of Representation Engineering Era; F-039 APPROVED; Principle 45/46/47; "Alpha Discovery Era" retracted (still Market Understanding Era); doctrine V6.4 | APPROVED | Chief Quant |
| 2026-06-30 | Phase 22 Semantic Taxonomy (clusters → market language; interpretability/transfer/predictive value; no ML) | APPROVED (start) | Chief Quant |
| 2026-06-30 | Phase 22 APPROVED; clusters speak market language; vocabulary repeats cross-event; Principle 48 (R²-drop NOT a failure)/49/50; F-040 OPEN (Universal Market States?); doctrine V6.5 | APPROVED | Chief Quant |
| 2026-06-30 | Phase 23 Semantic Consistency Audit (cross-pair/event consistency; threshold stability; data-driven; universality; no ML) | APPROVED (start) | Chief Quant |
| 2026-06-30 | Phase 23 APPROVED; Emerging Core Vocabulary (Compression consistent cross-event); Principle 51 (Market Primitives)/52 (preserve concepts not clusters); F-041 OPEN; architecture inverted; end of Semantic Engineering Era; doctrine V6.6 | APPROVED | Chief Quant |
| 2026-06-30 | Phase 24 Market Primitive Validation (event-free primitives; precedence; transitions; mechanism vs description; no ML) | APPROVED (start) | Chief Quant |
| 2026-06-30 | Phase 24 APPROVED; **F-041 REJECTED** (universal causal primitives unsupported); primitives = ecological layer (P53/54/55); F-042 OPEN; architecture Market Ecology→Primitives‖Events; Alpha PAUSED; end of Market Primitive Discovery; doctrine V6.7 | APPROVED | Chief Quant |
| 2026-06-30 | Phase 25 Ecology Interaction Framework (event×primitive distribution/representation/calibration/stability/weighting; no ML) | APPROVED (start) | Chief Quant |
| 2026-06-30 | Phase 25 APPROVED; **F-042 REJECTED** (ecology = background property; JS≈0, ΔBrier≈0); Principle 56/57; Primitive Research PAUSED; END of Market Understanding Era → Decision Theory; doctrine V6.8 | APPROVED | Chief Quant |
| 2026-06-30 | Phase 26 Decision Value Framework (PV/DV/XV scoreboard; decision audit; Decision Graph; no ML) | APPROVED (start) | Chief Quant |
| 2026-06-30 | Phase 26 **FULLY APPROVED**; 0/9 Selection-DV OOS; Prediction≠Decision≠Explanation; Principle 58–62; **END of Chapter One**; doctrine SPLIT into Market Doctrine V6.9 + Decision Doctrine V1; market-discovery FROZEN | APPROVED | Chief Quant |
| 2026-06-30 | Decision Doctrine V1 created (Evidence/Decision/Risk/Opportunity/Abstention/Sizing/Portfolio/Execution); Decision Science begins | APPROVED (start) | Chief Quant |
| 2026-06-30 | The Split APPROVED WITH AMENDMENT (Decision Science = consumer; Evidence Object = API); P63–66; Decision Doctrine V2 (Evidence-first); D0 Evidence Theory start | APPROVED | Chief Quant |
| 2026-06-30 | D0 Evidence Theory APPROVED + amendments (3-layer object P67; immutable + aggregation-as-operation P68; decision-ready≠trade-ready P69; confidence-as-model P70 OPEN; conflict taxonomy); Decision Doctrine V3; D1 Evidence Operations start; D2 DEFERRED | APPROVED | Chief Quant |
| 2026-06-30 | D1 Evidence Operations FULLY APPROVED + amendments (pure transformations P71; provenance graph P72; readiness=snapshot P73; temporal-conflict P74 OPEN; value objects P75); Decision Doctrine V4; D2 Evidence Sets start; Decision Families DEFERRED | APPROVED | Chief Quant |
| 2026-06-30 | D2 Evidence Sets FULLY APPROVED + amendments (order-independence/set≠sequence P76; decisions on snapshots P77; redundancy≠duplication P78 OPEN; snapshot=canonical input P79; confidence→reliability); Decision Doctrine V5; D3 Evidence Snapshots start; Decision Families DEFERRED | APPROVED | Chief Quant |

### Archived (from current edge research)

- Tier 3 events: Volatility Expansion, Pattern Completion (F-009; context fails).
  Not deleted — may return with better representation/context.

### Still BLOCKED (Chief approval required)

- Triple Barrier
- LightGBM
- Random Forest
- Outcome Model

Reason: *Hatutaki ML kutafuta alpha kabla market structure haijathibitishwa.*

---

*Governance kuanzia 2026-06-23: hakuna phase inayoanza bila Chief Approval
hapa juu; hakuna hypothesis iliyokataliwa (Rejected Findings) kurudiwa; doctrine
moja rasmi = V5.2.*
