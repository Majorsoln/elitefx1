# LESSON-041@v1

```yaml
id: LESSON-041@v1
claim: "TRAIN best-pair selection is noise-mining at intraday TFs — 3/3 candidates flipped negative
  OOS regardless of margin size (2×, 2×, 3.8× cost). Root cause: kuchagua pair-bora kati ya 4-5
  kwenye TRAIN ni max-selection — expected value ya 'max ya sampuli 5 zenye kelele' iko juu sana
  ya thamani halisi (selection bias), na margin kubwa ya TRAIN mara nyingi NI kelele iliyochaguliwa.
  Design rule kuanzia sasa: S2 pre-registration LAZIMA iwe multi-pair pooled (mechanism-level),
  au isiwe kabisa."
type: RESEARCH
evidence:
  - "Kesi 3/3 za single-pair TRAIN-selection zimegeuka hasi VALIDATION: (1) HC2-03 EURUSD
    (+0.1..+0.4 → -0.12..-1.64); (2) HB2-10 EURCHF (+0.89..+1.42, margin 2×, N=299 → -1.51..-1.94);
    (3) HM-05 USDJPY (+0.57..+1.26, margin 3.8×, N=730, gross-breadth 3/4 pairs, continuation-type
    → -0.59..-0.90, p_boot 0.65-0.72). Hoja ZOTE za 'kwanini huyu ni tofauti' (margin/N/breadth/
    mechanism-type) zilishindwa kutabiri — kwa sababu zote ni sifa za TRAIN (correlated, LESSON-040)."
  - "Muundo wa hesabu: kwa pairs 5 zenye true-EV≈0 na per-pair sampling noise σ, E[max] ≈ +1.16σ —
    'pair-bora ya TRAIN' inaonekana na edge hata kama hakuna edge popote. Ndicho tulichokiona mara 3."
  - "MZUNGUKO-2 jumla: hypotheses 8 kupitia machine (01 dead, 02 dead, 03/10/HB2-10/HM-05 FAIL-OOS,
    06/HB2-06 power) = 0 proven. Machine ilifanya kazi kila mara; HOLDOUT bikira mzunguko mzima."
counter_evidence: "STRAT-001/002 ni pair-specific PROVEN — lakini hazikuchaguliwa kama 'pair-bora ya
  TRAIN pekee': nr7 ilipita VALIDATION NA HOLDOUT kwa pairs mbili tofauti kwa vipindi huru. Bound:
  tatizo si pair-specificity ya strategy ya mwisho; ni SELECTION ya pair kwenye TRAIN kama hatua ya
  mwisho kabla ya test moja."
validity_conditions: intraday event-trigger candidates (15m/30m/H1) selected as best-pair-of-N on
  TRAIN with marginal-to-moderate effects; demonstrated 3/3, MZUNGUKO-2
when_to_use: unapobuni S2 yoyote — kama kilichobaki baada ya TRAIN ni pair MOJA, mechanism
  HAIJAFIKIA kiwango cha S2; rudi kwenye design (mechanism yenye breadth) badala ya kupima max ya
  kelele. Pia: hoja za 'kwanini kesi hii ni tofauti' zikitoka TRAIN tu — zipuuze (zimeshindwa 3/3).
when_not_to_use: si marufuku ya strategies za pair moja zilizopita OOS kamili (STRAT-001/002); si
  hukumu juu ya mechanisms ambazo TRAIN inaonyesha breadth ya pairs nyingi net+ (hizo ndizo
  zinastahili S2 pooled).
provenance: {cycle: MZUNGUKO-2, kesi: [HC2-03-EURUSD, HB2-10-EURCHF, HM-05-USDJPY], stage: S2-VALIDATION-x3}
lifecycle: ACTIVE  # Chief review 2026-07-16
```

**Maelezo kwa mwanafunzi:** Mara tatu tulichagua "pair bora ya TRAIN" na kuipima OOS — mara tatu
ikageuka hasi, bila kujali margin (hata 3.8× ya gharama). Kwa nini? Ukichagua bora kati ya 5 zenye
kelele, "bora" huwa juu kwa +1.16σ hata kama zote ni sifuri kweli — unachokipima ni kelele
uliyoichagua mwenyewe. STRAT-001/002 hazikupatikana hivi: zilipita vipindi viwili huru. Kanuni mpya:
mechanism isiyoonyesha breadth ya pairs nyingi kwenye TRAIN hairuhusiwi S2. Kupima max-ya-kelele ni
kupoteza VALIDATION windows.
