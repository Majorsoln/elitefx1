# LESSON-018@v1

```yaml
id: LESSON-018@v1
claim: "In the Phase 12 sample, deep-pullback carried positive net expectancy on EURUSD only (+0.37, Bayesian P(edge>0)=97%), against negative expectancy on every other tested pair — an in-sample candidate, not a proven edge."
type: MARKET-CONDITIONAL
evidence:
  - "event_reality_report.md (Phase 12) Q3, deep_pullback kwa pair: EURUSD=+0.37(P97) · USDJPY=-0.44(P5) · GBPUSD=-0.68(P1) · EURJPY=-0.87(P0) · USDCHF=-0.90(P0) · AUDUSD=-1.01(P0) → 'zilizothibitishwa: EURUSD'"
  - "Report ile ile Q1 (aggregate): deep_pullback EV=-0.810 [95% CI -0.94,-0.66], perm p=0.007 dhidi ya null -1.016 — inashinda random-direction LAKINI inabaki hasi net: better-than-random ≠ profitable (Profitable ≠ Tradable Edge)"
counter_evidence:
  - "contextual_alpha_confirmation_report.md (Phase 14): 0/282 zilinusurika OOS+BH-FDR; DPB·EURUSD
    contexts hazikuonekana hata kwenye top-15 za OOS p-value (DPB entries zilizoonekana bora OOS
    zilikuwa USDJPY/USDCAD — carrier tofauti na in-sample); mean EV IS=+1.78 → OOS=-0.97"
  - "Signal hii ni dhaifu kuliko MR×EURUSD kwenye data ile ile (P97 vs P100; +0.37 vs +0.90) — moja
    ya comparisons 30 (events 5 × pairs 6); false positives zinatarajiwa chini ya multiple testing"
validity_conditions: {pair: EURUSD pekee, period: sample ya 2016–2024, bars: volume bars,
  outcome: forward 6 bars NET ya spread, sample: IN-SAMPLE ONLY (discovery data), min N: 300}
review_trigger: "KALI — sawa na LESSON-017: njia PEKEE ya kuondoka CANDIDATE ni pre-registered,
  future-OOS, FDR-controlled test ya hypothesis hii hasa (P31; LESSON-009); matokeo yoyote
  yanalazimisha version mpya; regime shift au data refresh inabatilisha namba; in-sample re-runs
  haziwezi kuipandisha"
when_to_use: pamoja na LESSON-017 kama ushahidi wa Phase 12 kwamba EURUSD ilikuwa carrier pair
  pekee kwenye events MBILI tofauti — hypothesis kuhusu PAIR (ecology yake), si kuhusu events;
  ground truth ya evals (model lazima itofautishe 'beats random null' na 'positive net EV')
when_not_to_use: KAMWE kama trading rule — dhaifu kuliko LESSON-017 kwenye data ile ile na tayari
  sub-contexts zake zimefeli pre-registered OOS; pia usisome aggregate perm p=0.007 kama edge —
  event inabaki net-negative kila mahali isipokuwa EURUSD in-sample
provenance: {finding: F-030/F-031, phase: 12, doctrine: V5.21, principle: P30}
lifecycle: CANDIDATE
```

**Maelezo kwa mwanafunzi:** somo la ziada la lesson hii ni tofauti kati ya maswali mawili ambayo
huchanganywa: 'je, event ina skill dhidi ya random?' (perm p=0.007 — ndiyo kidogo) na 'je, event
ina faida net ya gharama?' (EV=-0.810 — hapana kabisa). Mfumo unaotrade p-values badala ya net
EV unalipa spread kwa hiari.
