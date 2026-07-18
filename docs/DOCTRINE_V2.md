# ELITEFX INSTITUTIONAL DOCTRINE V2 (SUPREME — 2026-07-17)

> **Hadhi:** doctrine kuu ya mradi, inayofupisha na kuchukua nafasi ya nyaraka za awali za
> utawala kwa MSTARI WA JUU (V1 architecture + doctrine za mzunguko zinabaki kwenye archive kama
> kumbukumbu — LESSON-015: kurekebisha si kufuta). Directive ya PD 2026-07-17: "re-doctrine
> mfumo upya" baada ya kuchagua njia A (kujenga juu ya strategies zilizothibitika + models).
> **Lengo la mwisho la taasisi:** kukodisha MODELS zilizothibitishwa kwa taasisi nyingine —
> hivyo nidhamu ya uthibitisho NDIYO bidhaa.

---

## 1. UKWELI WA SASA (state of the institution)

**PROVEN (portfolio rasmi — zinaelekea live):**
- STRAT-001 nr7×USDCHF H1 SL2/TP1 no-LATE — HOLDOUT EV +1.92 p=0.021
- STRAT-002 nr7×USDJPY H1 SL1/TP1 no-LATE — HOLDOUT EV +2.65 p=0.029
- Zinatrade BILA filter (K4 v0 = NO-LIFT, LESSON-042). Paper-trading → FTMO.

**WATCH (forward-accumulating; +EV OOS, power-limited — si dead, si proven):**
- C2-WATCH (compression×H4, +0.110 EV_R), SWING-WATCH (nr7×D1×LOW, +0.067 EV_R, 9/12 pairs),
  K4-WATCH (STRAT-001 filter: streak 6→4, chini ya floor). **Compression-HTF = +EV OOS mara 2.**

**ASSETS za kudumu:** state/HTF/intraday engines (12 pairs), atlas (186k rows), K4 dataset,
honest harness + bootstrap + pooled + blocked-CV, lessons 42.

**NEGATIVES (sayansi halali, zimehifadhiwa):** reversion/fade intraday 0/6; momentum single-pair
3/3 flips; K4 v0 no-lift. Machine iliamua 100% kwa usahihi; HOLDOUT bikira mizunguko yote.

---

## 2. MODEL-VERSIONING PARADIGM (directive ya PD — "kama Claude → Fable 5")

Kila uwezo mpya = **MODEL VERSION** iliyogandishwa, si patch ya moja kwa moja. Muundo:

- **Model = artifact iliyogandishwa** (JSON/params — HAKUNA pickle) + **provenance** (nani, lini,
  data commit hash, config) + **OOS proof** (HOLDOUT/forward attestation) + **semantic version**.
- **Registry:** `docs/MODEL_REGISTRY.md` (na mirror ya machine-readable `data/registry/*.json`).
  Kila entry: id, version, class (strategy | filter | sizing | regime), status
  (CANDIDATE→PROVEN→LIVE→RETIRED), gate-record, performance-attestation, dependencies.
- **Versioning:** vX.Y — Y = re-calibration (data mpya, params ile ile); X = mabadiliko ya
  muundo (features/mechanism). Toleo jipya HALIFUTI la zamani (audit trail); linachukua nafasi
  ya LIVE tu baada ya kupita gate NA kuzidi la sasa kwa OOS/forward.
- **Kila toleo linapita GATE ile ile** (§3). Hakuna toleo linaloenda live bila attestation.
  Hii ndiyo inayofanya model "kukodishika" — mteja anakagua track-record, haaminishwi.

---

## 3. GATE YA ULIMWENGU (universal — hakuna kinachoenda live bila hii)

Kila strategy/model/filter kabla ya LIVE:
1. **Splits takatifu:** TRAIN 2016-2022 → VALIDATION 2023-2024 → HOLDOUT 2025-01→2026-04
   (one-shot, pre-registered, SEALED-per-use).
2. **Pre-registration FROZEN by commit** KABLA ya kufungua dirisha lolote.
3. **Honest harness:** next-bar fills, stop=touch gap-honest, costs = spread(halisi per bar) +
   slippage (0.1 mkt/0.3 stop) + swap (swing). Episode non-overlap.
4. **Statistics:** pooled multi-pair (L-041 anti-selection-bias), pvalue_boot (B=50k, block),
   BH-FDR; criterion + H0 zimefungwa KABLA ya namba.
5. **Model-specific:** blocked-time CV ndani ya TRAIN pekee; VALID = check MOJA; metrics za
   kiuchumi (EV/streak, SI accuracy).
6. **Verdict wowote unaheshimiwa** — FAIL/NO-LIFT ni LESSON halali; hakuna kulazimisha
   (rekodi: C2-WATCH, HC2-03, K4 v0 zote ziliheshimu criterion).

---

## 4. TABAKA ZA MFUMO WA LIVE (deterministic; dashboard ni kioo, si mkono)

| Tabaka | Kazi | Aina |
|---|---|---|
| SIGNAL | strategies proven zinazalisha entries | frozen rules |
| DECISION/POLICY | select/veto per strategy-policy (decision_policy) | deterministic |
| RISK/SIZING | risk-per-trade + max/siku ili streak isivunje FTMO daily/max-loss | algorithm rules |
| COMPLIANCE | kila trade: sheria za FTMO/no-trade-window/max-spread zilifuatwa? (log) | deterministic gate |
| EXECUTION | broker adapter (paper → live) | adapter |
| **MONITORING** | **kioo:** reports, live actions, diagnosis, VPS, model perf, pair×strategy | **read-only** |

**Sheria ngumu ya kitaasisi:** MONITORING/dashboard HAIAMUI trade kamwe. Maamuzi = engine +
policy. Dashboard inasoma artifacts tu (decision logs, paper/live outputs, reports).

---

## 5. UDHIBITI WA KITAASISI (kwa kukodisha models)

Ili model "iuzike/ikodishike" kwa taasisi nyingine, LAZIMA:
1. **Immutable audit trail:** kila decision + trade + rule-check ina rekodi isiyobadilika
   (append-only log; commit hashes).
2. **Attestation:** performance ya kila model version inaweza kukaguliwa na mtu wa nje
   (namba + chanzo + reproducible script — mtindo wa SCIENTIST-D audits).
3. **Rule-compliance proof:** dashboard inaonyesha, per-trade, kwamba sheria zote zilifuatwa
   (hakuna trade nje ya sheria = hakuna). Hii ndiyo "control nzuri" ya PD.
4. **Separation:** research (hunts) vs production (live models) vs monitoring (kioo) —
   mistari mitatu tofauti; leasing inatoa ACCESS ya monitoring + attestation, si code ya research.

---

## 6. KUMBUKUMBU (memory discipline)
- `docs/EXPERIMENT_LEDGER.md` = index ya KILA kitu kilichojaribiwa + verdict + report path.
- Reports za mizunguko zimehifadhiwa `reports/archive/` (si kufutwa — kumbukumbu ya taasisi).
- `docs/lessons/` (42) = elimu ya kudumu. `docs/MODEL_REGISTRY.md` = models rasmi.
- Doctrine za awali → `docs/archive/` (V1 architecture, cycle charters, wave registrations).

---

## 7. NJIA MBELE (njia A ya PD)
Kipaumbele kigeuke kutoka "kuwinda" kwenda "kufikisha + kudhibiti":
(1) LIVE-PATH ya STRAT-001/002 (sizing + compliance + monitoring dashboard);
(2) MODEL REGISTRY + attestation (msingi wa kukodisha);
(3) uwindaji unaendelea kama background (WATCH forward + swing occasional), si kipaumbele.
