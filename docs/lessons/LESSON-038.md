# LESSON-038@v1

```yaml
id: LESSON-038@v1
claim: "Raw (pre-cost) edge on TRAIN does NOT imply an OOS edge. A signal that is (a) small relative to its cost margin and (b) concentrated on a single pair is a TRAIN artifact until VALIDATION says otherwise — HC2-03 had broad TRAIN gross+ (19/24) but its net edge existed only on EURUSD, and on VALIDATION all 7 pre-registered EURUSD cells flipped NEGATIVE (EV_net -0.12..-1.64, p_boot 0.55-0.97, 0 survivors)."
type: RESEARCH
evidence:
  - "WAVE-C2-A: HC2-03 (trend-pullback) S1 TRAIN — gross+ 19/24 cells, net+ 7 cells (EURUSD PEKEE,
    EV +0.11..+0.41 pips, cost_share 53-80%). Chief C2-4: pre-register cells 7 za EURUSD (TRAIN-selection
    halali) kwa S2. Matokeo S2 VALIDATION (reports/wave_c2a_s2_valid.md): cells ZOTE 7 net-HASI
    (-0.122 hadi -1.643), p_boot 0.554-0.971, BH-FDR k=0 survivors. Sign imegeuka TRAIN(+)→VALID(−)."
  - "Utabiri wa registration ulitimia: 'EVs za TRAIN ndogo + shrinkage (~0.35 slope, SCIENTIST-D) →
    inaweza kukosa significance'. Sio tu ilikosa significance — ilikuwa hasi kabisa (overfitting/noise,
    si edge iliyopungua). cost_share >50% (juu ya kizingiti cha CORE cha STRATEGIST-M §4) ilikuwa red flag."
counter_evidence: "STRAT-001/002 (nr7 H1 OCO) ZILINUSURIKA TRAIN→VALID→HOLDOUT — hivyo mchakato huu
  huthibitisha edge halisi HALISI (si upendeleo dhidi ya kila kitu). Bound: hii ni kuhusu kutafsiri TRAIN
  gross+/net-marginal, si kudai 'kila kitu kinashindwa'."
validity_conditions: general (any TRAIN candidate whose net edge is small vs cost_share and/or concentrated
  on one instrument; demonstrated HC2-03 EURUSD, WAVE-C2-A S2)
when_to_use: unapoona TRAIN candidate yenye (a) EV_net ndogo ikilinganishwa na cost_share (>~50%) au
  (b) net+ kwenye pair MOJA pekee wakati mechanism ni broad — itendee kama SHUKIWA, si survivor. Ruhusu
  VALIDATION (au OOS) iamue; usisherehekee raw gross+ wala pair-single net+. Split-discipline ndio ulinzi.
when_not_to_use: si sababu ya kuruka S2 (S2 ndiyo iliyokamata hii — thamani yake); si kukataa pair-specific
  edges kimsingi (STRAT-001/002 ni pair-specific NA proven) — tofauti ni ukubwa wa edge + uthibitisho wa OOS.
provenance: {cycle: MZUNGUKO-2, wave: WAVE-C2-A, stage: S2-VALIDATION, hypothesis: HC2-03}
lifecycle: ACTIVE  # Chief review 2026-07-14
```

**Maelezo kwa mwanafunzi:** HC2-03 ilikuwa na "raw edge" kwenye TRAIN (gross chanya 19/24) — ilionekana
mechanism halisi. Lakini net-edge ilinusurika kwenye EURUSD tu, ndogo (+0.1..+0.4) na cost_share juu
(>50%). Tulipeleka cells 7 za EURUSD kwenye VALIDATION (S2). Zote **zikageuka hasi** — edge "ilikuwepo"
TRAIN ilikuwa kelele/overfitting, si edge halisi iliyopungua. Somo: gross+ kwenye TRAIN si ushahidi wa
OOS; edge ndogo-kuliko-gharama + iliyojikita pair moja = shukiwa. Split-discipline (VALIDATION kabla ya
HOLDOUT) ndio uliokamata — HOLDOUT haikuguswa. STRAT-001/002 zinabaki (zilinusurika OOS halisi).
