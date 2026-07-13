# ELITEFX — CHARTER YA MZUNGUKO WA 2 (BEST STRATEGIES)
### "HTF big-picture bias → 15m/30m entries" — strategist-led, discipline-preserved

**Amri ya Project Director (Japhet):** tuanze upya kutafuta strategies BORA. Mtaalamu wa
strategies/entries atumie **features za data + ujuzi wa kutrade**, azingatie **market kwa
picha kubwa (HTF)**, trade ziwe **15m au 30m**, alist **best 10 strategies**, kisha tujue
**kila strategy ina tabia gani kwenye kila pair**.

**Kizuizi kisichoguswa (PD):** STRAT-001 na STRAT-002 **HAZIFUTWI** (`docs/STRATEGIES.md`).
Models zitajengwa juu yake. Mzunguko huu **hauzigusi** — unaongeza tu strategies mpya.

---

## USHAURI WA CHIEF QUANT (jibu la "wewe una ushauri gani?")

Mwelekeo ni **sahihi na wa kitaasisi**. HTF-bias → LTF-entry ndio muundo halisi wa
top-down analysis wanaotumia desks za kweli: **HTF inatoa CONTEXT (upande/regime),
15m/30m inatoa TRIGGER**. Hii ndiyo "hii ni AI si BOT" — kuchambua soko kwa mapana kabla
ya kuingia. Lakini ili tusirudie makosa, nashauri **mambo 4 lazima**:

1. **Jenga 15m/30m states KWANZA.** Kwa sasa tuna H1/H2/H4/D1 tu. Bila states za 15m/30m
   hakuna entry inayoweza kupimwa. Hii ni kazi ya IMPLEMENTER-A kabla strategist hajaanza.

2. **"HTF big-picture" lazima iwe FEATURES zinazohesabika**, si maneno. Tunaifsiri kama:
   HTF trend/slope (H4/D1), HTF regime (vol state), HTF structure (swing highs/lows, S/R),
   HTF momentum, na session. Strategist atumie hizi kama **context-filter ON signals**
   (kama `_mask_context` tuliyojenga) — si post-hoc.

3. **"Best 10" ni HYPOTHESIS-LIST, si PROVEN-LIST.** Mtaalamu anaorodhesha kwa **priors +
   logic ya trading**, kila moja ikiwa na **sheria za wazi zinazoweza kukanushwa**
   (falsifiable): HTF-context + 15m/30m trigger + exit. Hakuna "inaonekana nzuri" — kila
   sheria ni namba. Kisha **kila moja inapita gate ile ile** ya `docs/STRATEGIES.md`.

4. **Utafiti wa tabia-kwa-pair unafanyika TRAIN/VALID PEKEE.** HOLDOUT ni one-shot takatifu.
   Kujua "strategy X ina tabia gani kwenye pair Y" ni kazi ya TRAIN (2016–2022) +
   VALIDATION (2023–2024). Holdout haiguswi mpaka registration imeganda.

**Sababu ya kujiamini:** tuna data (12 pairs, miaka 9), tuna honest harness
(`event_quality_report.episodes`), tuna S1/S2 factory, tuna bootstrap-FDR engine
(B=50k), tuna family-pooled MDE screen, tuna 36 lessons. **Hatukosi mfumo — tunaongeza
mawazo bora ya kimkakati juu ya mfumo uliothibitika.** Hii ni maboresho, si kuanza toka sifuri.

---

## MUUNDO WA MZUNGUKO (S-series, ile ile discipline)

| Hatua | Nini | Nani |
|---|---|---|
| **C2-0** | Jenga states 15m/30m kwa pairs 12 (Hive: symbol/year/tf) | IMPLEMENTER-A |
| **C2-0b** | Tafsiri "HTF big-picture" → HTF feature set (H4/D1 slope, regime, structure, session) | IMPLEMENTER-A + Chief |
| **C2-1** | STRATEGIST-M: list **best 10** HYPOTHESES (HTF-context + 15m/30m trigger + exit), kila moja falsifiable, ranked kwa logic | STRATEGIST-M |
| **C2-2** | Chief review: chagua ambazo ni testable, freeze grid, hakuna leakage | Chief |
| **C2-3** | S1 TRAIN grid-search (2016–2022) kwa hypotheses zilizopita | Operator (engine) |
| **C2-4** | S2 VALIDATION (2023–2024) + BH-FDR + p_boot | Operator/Chief |
| **C2-5** | Tabia-kwa-pair: kwa survivors, chambua tabia kila pair (TRAIN/VALID pekee) | STRATEGIST-M + Chief |
| **C2-6** | Pre-registration FROZEN by commit → HOLDOUT one-shot (token) → PROVEN au FAIL kwa heshima | Chief |
| **C2-7** | PROVEN → ongeza `docs/STRATEGIES.md` + policy; FAIL → LESSON | Chief |

**Gate ya kuingia PROVEN:** kama `docs/STRATEGIES.md` ("GATE YA KUINGIA"). Hakuna mkato.

---

## VILINDWA (havifutwi mzunguko huu)
- `docs/STRATEGIES.md` — STRAT-001/002 + C2-WATCH.
- `docs/lessons/` — lessons 36 (lesson za models).
- Honest harness + S1/S2 factory + bootstrap engine + family-pooled — code takatifu.
- `reports/archive/` — historia yote ya Mzunguko-1 (git mv, si futa).

## HALINA MSIMAMO TENA (fresh slate)
- `reports/` (top-level) — safi kwa ripoti mpya za Mzunguko-2.
