# WAVE-C2-A — S2 VALIDATION REGISTRATION (FROZEN by Chief)

> **Pre-registration ya S2 (VALIDATION 2023–2024).** Cells zilizochaguliwa na S1 TRAIN
> (selection halali kwenye TRAIN — si post-hoc; VALIDATION haijaguswa). FROZEN kabla ya kufungua
> VALIDATION. Survivors (BH-FDR) → C2-6 freeze → HOLDOUT one-shot. HC2-01 imedondoshwa (dead,
> LESSON-037); HC2-06 ni WATCH (underpowered). S2 hii = **HC2-03 PEKEE, EURUSD PEKEE.**

## Kwa nini EURUSD pekee
S1 TRAIN: HC2-03 ilikuwa na raw edge broad (gross+ 19/24 cells), lakini **net** ilinusurika kwenye
EURUSD tu (spread 0.30 — cost-limited kwenye pairs nyingine). TRAIN-selection ya pair moja ni
halali (ndio kazi ya TRAIN). Ndani ya EURUSD, cells ZOTE zilizokuwa net+ kwenye TRAIN zimeorodheshwa
(hakuna cherry-pick ya cell moja bora — BH-FDR inadhibiti multiple-testing kati yao).

## Cells FROZEN (7) — HC2-03 × EURUSD × 30m
| # | trigger | SL | TP | max_hold | TRAIN EV_net (rejea) |
|---|---------|----|----|----------|----------------------|
| 1 | trend_resume | 1.0 | 3.0 | 32 | +0.410 |
| 2 | trend_resume | 1.5 | 3.0 | 32 | +0.376 |
| 3 | trend_resume | 1.5 | 2.0 | 32 | +0.119 |
| 4 | trend_resume | 1.0 | 2.0 | 32 | +0.108 |
| 5 | rsi2_pullback | 1.0 | 2.0 | 32 | +0.279 |
| 6 | rsi2_pullback | 1.5 | 2.0 | 32 | +0.183 |
| 7 | rsi2_pullback | 1.0 | 3.0 | 32 | +0.167 |

Context (signal-bar i): `allow_long = d1_trend_sign==+1 & h4_trend_sign==+1 & h4_rsi14<70`;
`allow_short` = mirror (rsi>30). NaN → excluded (isfinite guard, kama C2-3).

## Test (RASMI)
- Window: **VALIDATION 2023–2024** (`split="validation"`). HOLDOUT HAIGUSWI (token bado).
- Kila cell: pnl stream (net, costs ndani ya episodes) → `pvalue_boot` (B=50k, mean_block=3, engine
  RASMI ya strategy_lab) → **BH-FDR q=0.10** kati ya cells 7.
- Criterion ya survivor: `p_boot < FDR-threshold` NA `EV_net > 0` (VALIDATION).
- Sensitivity (si decision): p_z (skew-aware) kama strategy_lab write_outputs.

## Matokeo yanayowezekana (yote halali)
- **Survivor(s):** → C2-6 freeze + HOLDOUT one-shot (pre-registered cell PEKEE, token CHIEF-HOLDOUT-S3).
- **Hakuna survivor:** HC2-03 haujathibitika OOS → LESSON; portfolio inabaki STRAT-001/002.
  Tahadhari ya awali: EVs za TRAIN ni ndogo (+0.1..+0.4) + shrinkage (slope ~0.35, SCIENTIST-D) →
  VALIDATION inaweza kuwa chini ya significance. FAIL kwa heshima ni jibu, si kushindwa kwa mchakato.
