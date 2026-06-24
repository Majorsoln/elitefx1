# ELITEFX PROGRAM BOARD

> **Single Source of Truth ya GOVERNANCE.** Chief Quant + Implementer wanaisoma
> HII kwanza kabla ya kuendelea. Ndani: Chief Memory · Project Status · Research
> Ledger · Doctrine Amendments · Approval Log. Doctrine ya kina iko
> `ELITEFX_DOCTRINE_V5.4.md`; board hii ndiyo state ya mradi.
>
> Workflow (lazima, hakuna kuruka): **Research → Report → Chief Review →
> APPROVED/REJECTED → PROGRAM_BOARD update → Next Phase.**
> Kila kitu: *Evidence → Finding → Doctrine → Approval.* Hakuna "nafikiri" /
> "inaonekana".

*Last updated: 2026-06-24 (Chief review: Phase 4 PASSED → F-009; Phase 5 Triple Barrier opened).*

---

## Current Doctrine

Official:
- `ELITEFX_DOCTRINE_V5.4.md`

Status:
- ACTIVE

Superseded:
- V4
- V4.1
- V5.0
- V5.1 (folded into V5.2)
- V5.2 (superseded by V5.3)
- V5.3 (superseded by V5.4)
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

Phase: **5**
Name: **Triple Barrier Design (Tier 1 only)**
Status: ACTIVE
Owner: Implementer
Chief Approval: YES
Question: Tier 1 events: barrier width (0.5/1.0/1.5/2.0σ)? vertical (3/5/10/20
bars)? P(TP)/P(SL)/P(TIME)? je hubadilika kwa context decile? Design tu, NO ML.

> Phase 4 (Event × Context Matrix): **PASSED** → F-009 (context sensitivity is
> event-specific; Tier 1/2/3). ⚠️ Profitable ≠ Tradable Edge.

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

---

## Next Phase Queue

- [ ] Phase 5     Triple Barrier Design   *(ACTIVE — Tier 1 only; engine ready, report pending data run)*
- [ ] Phase 6     Outcome Engine          *(BLOCKED — Chief approval)*
- [ ] Phase 7     Lifecycle Controller    *(BLOCKED)*

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
Status: OPEN
Needed: Phase 5 (`triple_barrier_design_report.md`) — P(TP/SL/TIME) by
barrier×vertical, and shift by context decile. Tier 1 only. Design (no ML).

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
