# Evidence Theory — fasili Evidence Object (Decision Science D0)

*2026-06-30 21:52 | 9 pairs, 40 evidence cells | Evidence Object spec + lifecycle + aggregation | NO Decision Engine | NO ML*

> **Principle 63** Evidence = contract kati ya Market & Decision Science. **P64** production-agnostic. **P65** Evidence = first-class object yenye lifecycle. **P66** kila decision itrace kwa evidence. Decision Science inaanza na **Evidence**, sio decisions. Hii ni Evidence Object (data structure), SIO Decision Engine.

## Q1 — Evidence Object: fields

| field | maana | mfano (cell evidence) |
|-------|-------|------------------------|
| value | effect (pips), directionful | -0.271 |
| confidence | P(edge)=Φ(\|value\|/uncertainty); reliability, SIO magnitude | 0.67 |
| uncertainty | standard error | 0.609 |
| support | sample size n | 8,670 |
| coverage | share ya population | 0.008 |
| freshness | fresh→stale→expired (lifecycle) | expired |
| conflict | sign-instability (split-half) | 1.00 |
| source | provenance | cell:mean_reversion |

## Q3 — Evidence lifecycle / expiry

- TTL = 2000 bars (expired), stale > 800 bars.
- cells: **fresh 30**, stale 0, **expired 10** (kati ya 40).
- expired evidence **haiwezi** kusogeza decision (P66 inahitaji live trace).

## Q4 — Aggregation (inverse-variance; closed under aggregation)

| event | #cells | agg value | agg uncertainty | agg confidence | conflict |
|-------|--------|-----------|-----------------|----------------|----------|
| breakout | 8 | -1.819 | 0.109 | 1.00 | 0.00 |
| deep_pullback | 8 | -0.890 | 0.070 | 1.00 | 0.00 |
| mean_reversion | 8 | -0.221 | 0.072 | 1.00 | 0.31 |
| pullback | 8 | -1.165 | 0.070 | 1.00 | 0.00 |
| trend_continuation | 8 | -1.302 | 0.048 | 1.00 | 0.00 |

*aggregate ni Evidence Object yenyewe (closed): inverse-variance weighted value, combined uncertainty, summed support, min freshness, conflict = uncertainty-weighted sign-disagreement.*

> ⚠️ **CONFIDENCE SATURATION:** kwa support kubwa (pooled cross-pair, maelfu) SE inakuwa ndogo sana → confidence = Φ(\|value\|/SE) → **1.00** kwa karibu kila aggregate. Kwa hiyo confidence=1.00 hapa ni artifact ya n kubwa, **SIO** ushahidi wa edge (Principle 58: reliability ≠ magnitude ≠ OOS edge). Sufficiency-by-confidence inahitaji ku-recalibrate-iwa OOS (sio in-sample SE).

## Q2 — Conflict policy (contract-level, SIO Decision Engine)

- conflict ceiling = 0.35. Sera: conflict → *widen uncertainty / lower confidence*; conflict ya juu isiyotatuliwa → **ABSTAIN** (P26 capital preservation; Decision Engine kamwe haichagui upande kimya).
| event | agg conflict | policy |
|-------|--------------|--------|
| breakout | 0.00 | PROCEED (no conflict) |
| deep_pullback | 0.00 | PROCEED (no conflict) |
| mean_reversion | 0.31 | PROCEED with widened uncertainty / lowered confidence |
| pullback | 0.00 | PROCEED (no conflict) |
| trend_continuation | 0.00 | PROCEED (no conflict) |

## Q5 — Sufficiency: decision inahitaji evidence kiasi gani?

- decision-grade tu kama: support ≥ 100 **na** confidence ≥ 0.6 **na** si expired **na** conflict < 0.35.
- cells decision-grade: **27/40**.

> ⚠️ **'Decision-grade' ≠ 'tradable'.** Kati ya 27 decision-grade, **26** zina **value (EV) HASI** — yaani evidence ina ubora wa kutosha KUAMUA, na uamuzi unaoungwa mkono ni **ABSTAIN / avoid** (P26 capital preservation; F-022 bad-configs-persist), SIO *select/trade*. Evidence ni decision-grade kwa decision ya ABSTENTION, sio selection.

| cell | value | conf | support | fresh | conflict | sufficient? |
|------|-------|------|---------|-------|----------|-------------|
| mean_reversion×UNKNOWN×tight | -0.27 | 0.67 | 8,670 | expired | 1.00 | — (expired/none) |
| breakout×UNKNOWN×tight | -2.62 | 1.00 | 4,036 | expired | 0.00 | — (expired/none) |
| pullback×UNKNOWN×tight | -2.17 | 1.00 | 8,409 | expired | 0.00 | — (expired/none) |
| deep_pullback×UNKNOWN×tight | +0.15 | 0.60 | 8,409 | expired | 0.00 | — (expired/none) |
| trend_continuation×UNKNOWN×tight | -1.49 | 1.00 | 18,481 | expired | 0.00 | — (expired/none) |
| trend_continuation×UNKNOWN×WIDE | -1.35 | 0.92 | 2,415 | expired | 1.00 | — (expired/none) |
| mean_reversion×UNKNOWN×WIDE | -3.12 | 0.98 | 997 | expired | 0.00 | — (expired/none) |
| pullback×UNKNOWN×WIDE | -5.09 | 1.00 | 1,103 | expired | 0.00 | — (expired/none) |
| deep_pullback×UNKNOWN×WIDE | +1.67 | 0.91 | 1,103 | expired | 0.00 | — (expired/none) |
| breakout×UNKNOWN×WIDE | +1.70 | 0.76 | 435 | expired | 0.00 | — (expired/none) |
| pullback×LOW×tight | -0.99 | 1.00 | 96,270 | fresh | 0.00 | ✅ |
| deep_pullback×LOW×tight | -0.83 | 1.00 | 96,270 | fresh | 0.00 | ✅ |

## VERDICT — D0 Evidence Theory

→ ✅ **Evidence Object imefafanuliwa kama first-class object** yenye fields 8, lifecycle (fresh/stale/expired), aggregation (inverse-variance, closed), conflict policy (→abstain), na sufficiency gate. Imeonyeshwa kwa data halisi: 40 cells, 27 decision-grade, 10 expired. Hii ndiyo **contract/API** (P63) — Decision Engine itajengwa JUU ya object hii baada ya Chief kuidhinisha spec. **Hakuna Decision Engine bado** (maagizo ya Chief). NO ML.

**Bado Decision Science D0 — hakuna decision-action wala alpha.** Hii ni Evidence Engineering: kufafanua contract kabla ya kujenga consumer. **Tahadhari:** value zote za events ni hasi → 'decision-grade' inaunga mkono **abstention**, sio selection; na confidence=1.00 ni saturation ya n kubwa, sio edge (Principle 58).

## Honest Caveats

1. **Confidence = Φ(EV/SE) ni reliability ya in-sample effect, SIO OOS edge** (Phase 14/26 lesson). Decision-grade hapa = 'evidence ina ubora', SIO 'kuna alpha'.
2. **Sufficiency thresholds (support/confidence/conflict/TTL) ni human choices** — sehemu ya spec ya kujadiliwa, sio kanuni za asili; zinapaswa ku-calibrate-iwa OOS baadaye.
3. **Conflict = split-half sign disagreement ni proxy rahisi** — haijumuishi cross-pair/cross-regime conflict wala FDR; ni contract-level placeholder.
4. **Cell evidence inashiriki features na multiple-comparisons hatari** — Evidence Object haifuti haja ya OOS confirmation; inaipanga tu kwa muundo unaoauditika (P66).
5. **Aggregation inadhani independence** (inverse-variance) — cells za event moja zinaweza kuwa correlated; combined uncertainty ni optimistic. Itahitaji correlation-aware aggregation D-baadaye.

*Evidence Object: value/confidence/uncertainty/support/coverage/freshness/conflict/source; lifecycle fresh→stale→expired; inverse-variance aggregation; abstain-on-conflict; sufficiency gate. Principle 63–66. NO Decision Engine. NO ML. Profitable ≠ Tradable Edge.*