# ELITEFX PROGRAM BOARD

> **Single Source of Truth ya GOVERNANCE.** Chief Quant + Implementer wanaisoma
> HII kwanza kabla ya kuendelea. Ndani: Chief Memory · Project Status · Research
> Ledger · Doctrine Amendments · Approval Log. Doctrine ya kina iko
> `ELITEFX_DOCTRINE_V5.10.md`; board hii ndiyo state ya mradi.
>
> Workflow (lazima, hakuna kuruka): **Research → Report → Chief Review →
> APPROVED/REJECTED → PROGRAM_BOARD update → Next Phase.**
> Kila kitu: *Evidence → Finding → Doctrine → Approval.* Hakuna "nafikiri" /
> "inaonekana".

*Last updated: 2026-06-26 (Chief review: Phase 5.9A APPROVED → F-016; F-017 + Principle 18; Phase 5.10 + 5.11).*

---

## Current Doctrine

Official:
- `ELITEFX_DOCTRINE_V5.10.md`

Status:
- ACTIVE

Superseded:
- V4 … V5.8 (chain)
- V5.9 (superseded by V5.10)
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

**[F-017] Rare States May Carry Disproportionately High Information (HYPOTHESIS)**
Status: OPEN — under test (Phase 5.10)
Evidence: `latent_structure_report.md` (cluster C1 ≈ 1% of bars)
Summary: Institutional quant cares about rare regimes (crash/news/liquidity = 1%
but decisive). Rare states are a research PRIORITY, not noise. Tested by Phase 5.10.

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

Phase: **5.10 + 5.11** (parallel)
Name: **Rare State Analysis + Cluster Robustness**
Status: ACTIVE
Owner: Implementer
Chief Approval: YES
Questions:
- 5.10: rare cluster (C1 ~1%) inafanya nini? signature/composition/duration/exit/
  return distribution (F-017). Trade = market configuration, sio signal.
- 5.11: latent structures ni algorithm-independent? KMeans vs GMM vs Agglomerative,
  ARI agreement (Principle 18). NO ML, NO names.

> Phase 5.9A (Latent Structure Discovery): **APPROVED** → F-016 (latent structures
> exist without human labeling; k=4, 3/4 clusters universal). F-017 opened (rare
> states). Cluster ≠ State (Latent State Candidate). Principle 18 added. Config/
> Opportunity/Payoff engines **BLOCKED** until candidates Validated (5.11/5.12).

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

---

## Next Phase Queue

- [ ] Phase 5.10  Rare State Analysis     *(ACTIVE — F-017; engine ready, report pending data run)*
- [ ] Phase 5.11  Cluster Robustness      *(ACTIVE — Principle 18; engine ready, report pending data run)*
- [ ] Phase 5.12  Latent State Validation *(BLOCKED — Candidate → Validated)*
- [ ] Phase 6     Configuration Engine    *(BLOCKED)*
- [ ] Phase 7     Opportunity Engine      *(BLOCKED)*
- [ ] Phase 8     Payoff Engine           *(BLOCKED)*
- [ ] Phase 9     Machine Learning         *(BLOCKED)*

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

**Q-013 — What does the rare state (C1 ~1%) do?**
Status: OPEN
Needed: Phase 5.10 (`rare_state_analysis.md`) — signature, composition, duration,
exit, return distribution. F-017.

**Q-014 — Are latent structures algorithm-independent?**
Status: OPEN
Needed: Phase 5.11 (`cluster_robustness_report.md`) — KMeans/GMM/Agglomerative,
ARI agreement. Principle 18. Gate to Latent State Validation.

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
