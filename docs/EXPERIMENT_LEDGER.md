# ELITEFX — EXPERIMENT LEDGER (kumbukumbu ya KILA kilichojaribiwa)

> Index rasmi ya kila jaribio + verdict + report. Directive ya PD: "kila tulicho jaribu na report
> zake kuwekwa kwenye kumbukumbu." Hii ndiyo audit trail ya taasisi — hakuna jaribio linalofutwa;
> negatives ni sayansi. (Mzunguko-1 ya Chapter historia: `reports/archive/` — 82 reports.)

## MZUNGUKO-2 (best-strategies hunt: intraday 15m/30m/H1 + HTF context)

| ID | Jaribio | TF | Verdict | Report |
|----|---------|----|---------|--------|
| HC2-01 | ALIGNED-COMPRESSION (nr7 one-sided, trend-aligned) | 30m | **DEAD** (gross hasi -0.234) — L-037 | reports/archive/wave_c2a_s1_train.md |
| HC2-03 | TREND-PULLBACK-RESUME | 30m | S1 EURUSD+ → **S2 FAIL-OOS** (sign-flip) — L-038 | reports/archive/wave_c2a_s2_valid.md |
| HC2-06 | HTF-SR-FADE | 30m | **UNDERPOWERED** (N rare) | reports/archive/wave_c2a_s1_train.md |
| HC2-10 | FAILED-BREAK-SWEEP (false_break) | 30m | S1 **0/20 net** (EUR-crosses gross+, cost-eaten; gold −24.6) — L-039 | reports/archive/wave_c2b_hc210_s1_train.md |
| HB2-06 | SR-FADE @ H1 | H1 | **CLOSED-BY-POWER** (0/40 MIN_N) | reports/archive/wave_c2b_hb206+hb210_s1_train.md |
| HB2-10 | SWEEP @ H1 | H1 | S1 EURCHF gross×2 → **S2 FAIL-OOS** (−1.9) — L-040 | reports/archive/wave_b2_s2_valid.md |
| HM-02 | LONDON-ORB-D1 | 30m | **DEAD** (gross− 5/5) | reports/archive/wave_c2b_hm02+hm05_s1_train.md |
| HM-05 | ALIGNED-SHOCK | 15m | S1 USDJPY net+ → **S2 FAIL-OOS** (−0.6) — L-041 | reports/archive/wave_m_s2_valid.md |

**Muhtasari M2:** hypotheses 8 → **0 proven.** Somo la pamoja: reversion/fade intraday & momentum
single-pair hazishindi gharama/selection-bias. Compression-HTF ndiyo home-ground. Lessons 037-041.

## MZUNGUKO-3 (AI ya mazingira: atlas + pair-lessons + K4 model)

| ID | Jaribio | Verdict | Report |
|----|---------|---------|--------|
| M3-1 | R-MAP behavioral ATLAS (events 21×pairs 12×TF 3, swap, MFE/MAE) | ✅ RAMANI (186k rows) | reports/rmap_atlas.md |
| M3-4 | K4 training dataset (STRAT-001/002, 4,222 trades) | ✅ CERTIFIED-with-fixes | reports/k4_dataset.md |
| M3-QA | Curriculum certification (SCIENTIST-D adversarial) | ✅ vitabu 3 certified; quarantine binding | reports/m3_curriculum_audit.md |
| SWING-1 | nr7×D1×LOW pooled (STRAT-003 candidate) | **S2 FAIL** (power; EV_R +0.067, 9/12 pairs OOS) → SWING-WATCH | reports/swing_family_s2.md |
| M3-5 | K4 entry-quality model v0 (per-strategy) | **NO-LIFT** zote → K4-WATCH — L-042 | reports/k4_model_report.md |

**Muhtasari M3:** atlas + dataset ni assets za kudumu; hunt-mpya SWING = power-limited (WATCH);
model-filter = no-lift v0. Machine iliheshimu criterion mara zote.

## KANUNI YA LEDGER
- Kila jaribio jipya linaongezwa HAPA na verdict + report path siku linapoisha.
- Report za matokeo → `reports/archive/` baada ya verdict (kumbukumbu). Registrations →
  `docs/archive/registrations/`.
- Dashboard (M-DASH) inasoma ledger hii + reports kama chanzo cha "diagnosis" panel.
