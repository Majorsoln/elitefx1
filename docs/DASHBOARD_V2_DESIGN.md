# ELITEFX — DASHBOARD-V2 DESIGN — "MODEL SCORECARD" (design ya kujadili → kujenga)

> Directive ya PD 2026-07-22: "user aelewe hali ya model (maamuzi ya sasa NA ya nyuma), lugha rahisi
> (trade + English), filtering rahisi." PD amekabidhi Chief: metaphor, vipaumbele, na majina.
> Design hii inaboresha Glass Box (V1) → mtazamo wa **KUELEWA** (si audit peke yake). Inabaki
> **read-only mirror** (Doctrine §4 — haiendeshi trade). Mahitaji ya msingi: `DASHBOARD_V2_ROADMAP.md`.

## 0. MAAMUZI YA CHIEF (yaliyokatwa)
- **Metaphor/neno:** **"MODEL SCORECARD"** (KADI YA MODEL). Rangi 🟢 KIJANI (inashikilia ahadi) ·
  🟡 NJANO (angalizo) · 🔴 NYEKUNDU (inashuka) = **status lights** (si "afya ya mgonjwa").
- **Public call-signs (anonymization §9):** STRAT-001 → **KAIROS-1**, STRAT-002 → **KAIROS-2**
  (models zijazo: KAIROS-3, 4…). Internal id (STRAT-001/002) + pair = SIRI ya server. Lessee anaona
  call-sign tu — hajui pair/logic/id.
- **Falsafa ya lugha:** kila namba muhimu ina **sentensi ya tafsiri** (Kiswahili cha trade + English
  rahisi). Hakuna jargon peupe. Mtu asiye quant aelewe kwa sekunde.

## 1. ROLES — nani anaona nini, kwa nini
| Role | Anaona | HAONI | Kwa nini |
|---|---|---|---|
| **PD / Internal** | KILA kitu: models zote (call-sign + internal id + pair), live, compliance, VPS, Steward weakness maps, filtering huru | — | Control kamili + maamuzi ya taasisi |
| **Attestor** | Track-record, attestation (hash+commit), compliance-proof per trade, scorecard | Research/IP internals, params, features | Uthibitisho huru bila kufichua siri |
| **Lessee** | Call-sign(s) zake tu (KAIROS-1/KAIROS-2), scorecard kwa lugha rahisi, matokeo + sheria | IP (logic/features/params), pair, internal id, models za wengine | Uaminifu + kulinda IP + privacy (token §9) |

## 2. MUUNDO (nav — role-aware; inaboresha V1 monitor/context.py nav_panels)
`OVERVIEW` · `SCORECARDS` · `LIVE` · `COMPLIANCE` · `HISTORY` · `MODEL HEALTH (Steward)` · `ATTESTATION`
(lessee: `MY MODELS` pekee — scorecard za call-sign zake).

## 3. MOYO — "MODEL SCORECARD" (kwa KILA model; per model DASHBOARD INAFANYA NINI)
Kila model = kadi moja inayosimulia hadithi nzima:

| # | Sehemu | Inafanya nini (per model) | Chanzo |
|---|---|---|---|
| A | **STATUS BAND** | Call-sign, version, hadhi (PAPER/LIVE), **status light** + sentensi: *"KAIROS-1 inatoa faida kama ilivyoahidi. Iko salama."* | steward.json + registry |
| B | **AHADI vs UHALISIA** | learned EV vs practical + shrinkage bar: *"Iliahidi +1.92 pips; inatoa +3.07 — juu ya ahadi."* | model_steward.json |
| C | **MAAMUZI YA SASA** | Trade hai + kwa nini (signal→policy→size→compliance→fill trace) | paper_log |
| D | **MAAMUZI YA NYUMA** | Kila trade: tarehe/pair*/dir/R/matokeo + *kwa nini iliingia + sheria zilizopita* (glass-box). Filterable. (*pair imefichwa kwa lessee) | paper_log |
| E | **RAMANI YA UDHAIFU** | session/vol/streak/cost kwa rangi: *"Nguvu zaidi NY; inadhoofu kidogo baada ya hasara."* | Steward weakness map |
| F | **UFUATAJI WA SHERIA** | Trade zote zilifuata FTMO? Idadi ya zilizokataliwa + sababu | compliance log |
| G | **MWENENDO WA MUDA** | Equity curve ya model + je inashuka? (degradation) | paper_log |

**Lessee:** A–G zote LAKINI (1) call-sign (KAIROS-1/KAIROS-2), si STRAT-xxx; (2) pair/params/features/logic
HAZIONEKANI; (3) lugha rahisi pekee. Mapping call-sign↔internal = server-side (haipiti kwa client).

## 4. OVERVIEW (Command Deck) — taasisi kwa jicho moja
Models ngapi 🟢/🟡/🔴 · equity ya jumla · compliance OK? · VPS heartbeat · alerts. Bofya → scorecard.

## 5. LUGHA (R3) + FILTERING (R5)
- **Lugha:** kila metric + sentensi ya tafsiri (trade + English), tooltip/toggle.
- **Filtering:** chips — model(call-sign) · pair(internal) · tarehe(leo/wiki/mwezi) · session · W/L ·
  regime. Kila panel inaheshimu filter. Si kuandika query.

## 6. MIPAKA (haibadiliki)
Read-only mirror (§4 — haiendeshi trade). Append-only audit + attestation (V1) HAZIBADILIKI.
Anonymization (call-sign↔internal, token↔lease↔model) = server-side secret (§9.2). Lessee isolation (V1 F-fixes) inabaki.

## 7. VIPAUMBELE VYA UJENZI (Chief — awamu, reuse-first)
1. **AWAMU 1 — MODEL SCORECARD (INTERNAL):** sehemu A–G kwa PD role, kwa data tuliyonayo
   (steward.json + paper_log). Call-sign registry (KAIROS↔STRAT). Ndio moyo — thibitisha ndani.
2. **AWAMU 2 — OVERVIEW (Command Deck):** roll-up ya scorecards (status lights + equity + alerts).
3. **AWAMU 3 — LESSEE VIEW (MY MODELS):** scorecard ile ile LAKINI restricted + anonymized
   (call-sign, IP hidden, token). Reuse ya Awamu 1 — si kujenga upya.
4. **AWAMU 4 — LUGHA + FILTERING hardening:** tafsiri-sentensi + filter chips kila panel.
Sababu: jenga kitengo cha kuelewa (scorecard) kwa data iliyopo → thibitisha → kisha restrict/anonymize
(reuse) → kisha roll-up + polish. Reuse-first, hatari ndogo.

## 8. HATUA
Awamu 1 (Scorecard internal) = prompt ya kwanza ya implementer (docs/team/PROMPTS.md). Kila awamu:
build → Chief review (self-tests + role-smoke) → PR → merge. Design hii = mkataba; features/roles
zimejadiliwa na kukubaliwa na PD (2026-07-22).
