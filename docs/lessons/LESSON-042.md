# LESSON-042@v1

```yaml
id: LESSON-042@v1
claim: "An entry-quality model on a PROVEN signal can add NO deployable lift when the environment
  features do not separate that signal's winners from losers — K4 v0 (per-strategy logistic/tree,
  blocked leave-one-year-out CV, TRAIN 2016-2022) returned NO-LIFT for BOTH STRAT-001 (ΔEV_R@70%
  +0.0157, p=0.087, below +0.05R floor) and STRAT-002 (+0.0037, p=0.40). Prediction from certification
  (max single-feature AUC 0.532) was correct: a proven signal is often ALREADY near-uniform in
  per-trade quality — 'filter it smarter' is a hypothesis that must be tested, not assumed."
type: RESEARCH
evidence:
  - "reports/k4_model_report.md: STRAT-001 winner logistic C=0.1 FULL, ΔEV_R@70% +0.0157 R,
    p_boot 0.087 (CI [-0.003, 0.035]), AUC 0.526; STRAT-002 winner tree d2 CORE, ΔEV_R +0.0037,
    p 0.40, AUC 0.503. Criterion §4 (pre-registered): dev>0 & p<0.05 & dev>=+0.05R & ev-ret>=0.9.
    Zote FAIL-TO-REJECT H0. Hakuna freeze, hakuna VALID kuguswa (design §4: CV-FAIL -> LESSON)."
  - "SCIENTIST-D certification (§A2.2/§D6) alitabiri HASA: single-feature AUC max 0.532 -> 'lift
    itakuwa ndogo au sifuri; NO-LIFT ni matokeo halali'. Utabiri wa mkaguzi huru ulitimia."
  - "NUANCE (STRAT-001, si deploy): EV-retention 2.54 (filter iliondoa trades za R-hasi kwa jumla)
    NA loss-streak max 6->4 -> mwelekeo wa manufaa upo, LAKINI per-trade ΔEV_R haitofautishwi na
    kelele kwa N=1,607 (p 0.087, chini ya +0.05R floor). 'Not proven' si 'nothing' -> K4-WATCH."
counter_evidence: "Hii haisemi ML haina thamani kwa mradi milele — v0 ilitumia features za signal-bar
  zilizopo + N~1.6k + interpretable model kwa makusudi (design §D6). v1 yenye features mpya (order-flow,
  cross-pair, regime-transition) ni njia halali LAKINI prior (AUC 0.53) si ya kutia moyo — ittest kwa
  H0 ile ile. Bound: STRAT-001/002 ZENYEWE zinabaki PROVEN + zinatrade bila filter (EV zao ni chanya
  bila K4)."
validity_conditions: entry-quality/trade-filter models on an already-validated signal with weak
  single-feature separation (AUC ~0.5) and moderate N; demonstrated K4 v0, MZUNGUKO-3
when_to_use: kabla ya kudhani 'model itapandisha win rate ya strategy iliyothibitika' — pima
  separation ya features KWANZA (single-feature AUC, mutual info); AUC~0.5 = tarajia NO-LIFT; weka H0
  = hakuna lift na criterion ya EV (si accuracy) KABLA ya CV. Deploy filter TU ikipita floor ya
  kiuchumi + significance kwenye CV blocked-time, si kwa mwelekeo wa streak peke yake.
when_not_to_use: si sababu ya kutupa dataset ya K4 (ni ya thamani kwa uchambuzi + v1); si hukumu
  kwamba STRAT-001 haina filterability KABISA (mwelekeo upo — K4-WATCH, re-test kwa forward/features
  mpya); si sababu ya kuacha STRAT-001/002 (zinatrade bila K4).
provenance: {cycle: MZUNGUKO-3, stage: M3-5-CV, models: [STRAT-001-logistic, STRAT-002-tree], verdict: NO-LIFT}
lifecycle: ACTIVE  # Chief review 2026-07-17
```

**Maelezo kwa mwanafunzi:** tulijenga model ya kuchuja trades bora za STRAT-001/002 (kupandisha win
rate kwa uchambuzi — ndoto ya PD). CV (blocked kwa mwaka, TRAIN pekee) ilirudi **NO-LIFT** kwa zote —
kama mkaguzi alivyotabiri (features peke yake zina AUC 0.53, karibu na bahati). Maana yake: signal ya
nr7 iliyothibitika tayari ina ubora unaokaribia sawa kila trade — features za mazingira tulizonazo
haziwezi kutenga washindi na walioshindwa vya kutosha kulipa. **Hii si kushindwa kwa mfumo — ni sayansi:
tuliuliza swali, tukapata jibu la uaminifu.** STRAT-001 ilionyesha mwelekeo mdogo (retention 2.54,
streak 6->4) lakini chini ya kizingiti -> K4-WATCH, si deploy. STRAT-001/002 zinaendelea kutrade bila
filter (EV zao ni chanya zenyewe). Njia ya v1 (features mpya) ipo lakini prior si ya kutia moyo.
