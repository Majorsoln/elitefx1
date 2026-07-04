# LESSON-017@v1

```yaml
id: LESSON-017@v1
claim: "In the Phase 12 sample, mean-reversion carried positive net expectancy on EURUSD only (+0.90, Bayesian P(edge>0)=100%) while failing in aggregate and on every other pair — an in-sample candidate, not a proven edge."
type: MARKET-CONDITIONAL
evidence:
  - "event_reality_report.md (Phase 12) Q3, mean_reversion kwa pair: EURUSD=+0.90(P100) · AUDUSD=+0.11(P74) · EURJPY=-0.11(P35) · EURGBP=-0.14(P18) · USDCAD=-0.15(P24) · GBPUSD=-0.36(P11) → 'zilizothibitishwa: EURUSD'"
  - "Report ile ile Q1 (aggregate): mean_reversion EV=-0.212 [95% CI -0.34,-0.05], perm p=0.003 dhidi ya null -0.926, Bayesian P(edge>0)=0% — proven events 0/5; pair inabeba kile ambacho aggregate haina (F-030: context = IDENTITY)"
  - "Q4 (state-dependence): MR EV kwa vol state — LOW=-0.68 · NORMAL=+0.20 · HIGH=-0.14; hata ndani ya pair, edge ni state-conditional"
counter_evidence:
  - "contextual_alpha_confirmation_report.md (Phase 14): hypotheses 282 za pre-registered contextual
    → 0 zilinusurika future-OOS + BH-FDR(q=0.1); mean EV IS=+1.78 → OOS=-0.97; sub-context bora ya
    MR·EURUSD (HIGH·NORMAL·ASIAN, OOS p=0.0496) HAIKUNUSURIKA FDR"
  - "V5.21: Mean Reversion Strategy FORBIDDEN (post-hoc subgroup + multiple comparisons) — namba hii
    iligUNDULIWA ndani ya comparisons 30 (events 5 × pairs 6), haikuwa pre-registered"
validity_conditions: {pair: EURUSD pekee, period: sample ya 2016–2024, bars: volume bars,
  outcome: forward 6 bars NET ya spread, sample: IN-SAMPLE ONLY (discovery data), min N: 300}
review_trigger: "KALI — lesson hii inaweza kuondoka CANDIDATE KUPITIA NJIA MOJA TU: pre-registered,
  future-OOS, FDR-controlled test ya hypothesis hii hasa (P31; LESSON-009). Matokeo yoyote ya test
  hiyo (pass AU fail) yanalazimisha version mpya; regime shift au data refresh inabatilisha namba;
  in-sample re-runs HAZIWEZI kuipandisha"
when_to_use: kama mfano wa kanuni F-030 (edge ni conditional, si universal) kwenye reasoning na
  evals — model inayosema 'mean reversion works' bila kutaja pair + status ya in-sample inafeli;
  MR research ikifunguliwa tena kwa uamuzi wa Chief, EURUSD ndiyo hypothesis ya kwanza
  ku-pre-register
when_not_to_use: KAMWE kama trading rule — namba ni in-sample, imechaguliwa post-hoc ndani ya
  comparisons 30, na refined sub-contexts zake tayari zimefeli round moja ya pre-registered OOS;
  V5.21 inakataza MR-only strategy moja kwa moja; pia usiisome kama 'EURUSD ni pair nzuri' kwa
  ujumla — claim ni event×pair mahususi
provenance: {finding: F-030/F-031, phase: 12, doctrine: V5.21, principle: P30}
lifecycle: CANDIDATE
```

**Maelezo kwa mwanafunzi:** hii ni MARKET lesson, si METHOD lesson — ni rekodi ya hali ya soko
kwenye sample moja, yenye tarehe ya kuisha isiyojulikana. Thamani yake ni mbili: (1) ni ushahidi
halisi kwamba edge huishi kwenye context (aggregate 0/5, pair-level chanya); (2) ni mtego wa
kufundishia — inaonekana kama alpha, na Phase 14 ilionyesha kwa nini kuionea imani bila
pre-registered OOS ni kosa (30 candidates → 0).
