# LESSON-040@v1

```yaml
id: LESSON-040@v1
claim: "Single-pair TRAIN-selection flips OOS repeatedly (2/2 kesi) — na 'cross-TF consistency' ya
  TRAIN si ushahidi huru unaookoa: TF mbili za window ILEILE ya TRAIN zinashiriki price paths zile
  zile (evidence correlated, si confirmation mbili). Ushahidi huru = kipindi kingine cha muda
  (VALIDATION) au mechanism tofauti kweli — kamwe si mtazamo mwingine wa data ile ile."
type: RESEARCH
evidence:
  - "Kesi 1 (LESSON-038): HC2-03 EURUSD — TRAIN net +0.1..+0.4 (pair 1/3) → VALIDATION cells 7/7
    hasi (-0.12..-1.64), 0 survivors."
  - "Kesi 2 (hii): HB2-10 EURCHF @ H1 — TRAIN net +1.42/+0.89 (N=299/303, cost_share 0.50, PF 1.18,
    pair 1/5) NA 'cross-TF consistency' (EURCHF/EURGBP top-2 gross kwenye 30m NA H1) → VALIDATION
    cells 2/2 hasi (-1.94/-1.51), p_boot 0.85/0.80, 0 survivors. Margin kubwa + consistency
    HAZIKUOKOA — kwa sababu 30m na H1 za TRAIN ni bars za miaka ILEILE 2016-2022 (paths zilezile)."
  - "Familia ya sweep-fade (false_break) sasa IMEFUNGWA: 30m pairs zote net-hasi (0/20); H1
    pair-bora TRAIN imefeli OOS. Pamoja na WAVE-A: reversion/fade mechanisms 0/6 OOS mzunguko-2."
counter_evidence: "STRAT-001/002 ni pair-specific NA proven — tofauti: zilipita VALIDATION NA
  HOLDOUT (ushahidi huru wa kweli, vipindi vingine vya muda). Bound: pair-specificity si dhambi;
  TRAIN-only pair-selection ndiyo mtego."
validity_conditions: general (any candidate selected on TRAIN by best-pair with marginal effect;
  demonstrated mara 2, MZUNGUKO-2)
when_to_use: unapoona TRAIN candidate wa pair moja — hata mwenye margin nzuri na 'consistency' za
  ndani ya TRAIN (TF nyingi, triggers jirani) — kumbuka evidence zote za TRAIN zime-correlate.
  Usipande matarajio; VALIDATION pekee ndiyo huru. Kwa design: prefer mechanisms zinazo-generalize
  pairs nyingi TRAIN (kama nr7 H1 ilivyokuwa) kabla ya kupeleka S2.
when_not_to_use: si marufuku ya kupima single-pair candidates kwenye S2 (gharama yake ni ndogo na
  jibu ni la kweli) — ni marufuku ya KUAMINI kabla VALIDATION haijasema; pia si hukumu dhidi ya
  pair-specific strategies zilizopita OOS kamili.
provenance: {cycle: MZUNGUKO-2, waves: [WAVE-C2-A, WAVE-B2], stage: S2-VALIDATION, kesi: [HC2-03-EURUSD, HB2-10-EURCHF]}
lifecycle: ACTIVE  # Chief review 2026-07-15
```

**Maelezo kwa mwanafunzi:** Mara ya pili mfululizo: candidate aliyechaguliwa kwa "pair bora ya TRAIN"
amegeuka hasi kwenye VALIDATION — safari hii hata na margin kubwa (+1.42) na "uthibitisho" wa TF mbili.
Kwa nini consistency ya TF haikusaidia? Kwa sababu 30m na H1 za TRAIN zinaangalia **soko lile lile,
miaka ile ile** — ni picha mbili za tukio moja, si mashahidi wawili. Shahidi huru ni **kipindi kingine
cha muda**. Pia: mechanisms zote za reversion/fade (6) sasa zimefeli OOS mzunguko huu, wakati kila
kilichowahi kuthibitika kwetu (STRAT-001/002, C2-WATCH +EV) ni **breakout/continuation na stop-entry**.
Soko letu linatuambia kitu: fuata continuation.
