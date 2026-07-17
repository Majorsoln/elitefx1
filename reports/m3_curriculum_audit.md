# M3-QA — CURRICULUM CERTIFICATION AUDIT (SCIENTIST-D)

*2026-07-17 · External reviewer (doctrine-unbound; data-integrity bounds only) · Gate ya charter
`docs/CYCLE3_CHARTER.md` §Curriculum Certification — hati hii ndiyo ruhusa/katazo la M3-5.*

**Mbinu.** Sikuamini self-tests kwa maandishi: nimeziendesha ZOTE mwenyewe (market_state_engine,
intraday_state_engine, htf_context, rmap, k4_dataset — PASS zote kwa run yangu), nimesoma code ya
kila trap kuhakikisha si ya maonyesho, na nimefanya adversarial audit yangu juu ya parquets zote
mbili. Kila namba hapa inazalishwa na `scripts/scientist_d_m3_audit.py` (repo, deterministic).
Hakuna dirisha jipya lililoguswa (vitabu ni TRAIN(+VALID kwa K4) vilivyokwisha-jengwa).

---

## VERDICT KWA MUHTASARI

| Kitabu | Verdict | Sharti kuu |
|---|---|---|
| 1. STATES + HTF context | **CERTIFIED-WITH-FIXES** (S1–S3) | atr_n haipo kwenye state parquet (100% NaN kwenye K4); coverage audit ya pairs 12 bado |
| 2. K4 DATASET | **CERTIFIED-WITH-FIXES** (K1–K5) | hakuna timestamp column → time-aware CV haiwezekani; feature/outcome manifest inahitajika |
| 3. ATLAS / pair-lessons malighafi | **CERTIFIED-WITH-FIXES kama RAMANI** + QUARANTINE list §B (binding kwa lessons) | UNKNOWN=2016-warmup confound (7/20 ya top-20 ya report!); D1 sess_top artifact; breadth ≠ stability |
| **M3-5 model training** | **RUHUSA YA MASHARTI (GO baada ya K-1..K-3)** | fixes ni rebuild deterministic ya dakika — hakuna re-research |

Hakuna kitabu kilichoREJECTED. Msingi wa uaminifu ni imara kuliko nilivyotarajia — hasa K4,
ambayo outcomes zake zina-MATCH artifacts za proven byte-kwa-byte-karibu (§A2.1). Lakini vitabu
vina makosa ya uhariri ambayo, bila kurekebishwa, yangefundisha model uongo maalum (§B, §D).

---

## A. UKAGUZI KWA KITABU

### A1. Kitabu 1 — STATES (market_state_engine + intraday_state_engine + htf_context)

**No-lookahead traps: ZA KWELI, si za maonyesho.** Nimesoma code ya kila trap na kuiendesha:
- `htf_context` [2]/[5]: mtego wa spike — H4 bar inayozunguka LTF bar inapewa spike ya h=+50;
  test in-assert kwamba context ya LTF bar ya ndani ≠ spike NA == bar iliyotangulia, PLUS
  boundary exact (t == close_ts inaruhusiwa) [2b], D1 mid-day [3], H1-ltf variant [5]. Hii ni
  as-of backward join juu ya `close_ts = ts + duration` — mechanism sahihi, na trap ingeshika
  kosa la kweli (join juu ya open-ts ingefeli test). PASS kwa run yangu.
- `k4_dataset` [2b]: decidability EXACT — vol alternating kila bar; assert `vol_state ==
  vol[signal i]` NA `!= vol[entry i+1]` kwa kila trade. Trap halisi. PASS.
- Deseason: `_deseason` ni trailing same-hour mean yenye `shift(1)` (hakuna leo ndani ya
  baseline); intraday surge golden [c]: HIGH%=99% kwenye surge + warmup UNKNOWN — PASS kwa
  run yangu. `_reg3` terciles trailing shift(1).

**Coverage (kutoka vitabu vilivyopo — pairs 2, H1):** d1_*/h4_* NaN ≤ 0.9% (zote chini ya 1%);
UNKNOWN vol/activity zimefungwa 2016 pekee (warmup ya trailing window — by design). Ila:

- **S1 (FIX):** `atr_n` inaahidiwa kama feature ya K4 lakini ni **100% NaN** (`k4_dataset.md`
  jedwali la completeness; sababu: state parquet za H1 hazina column `atr_n` — engine
  inaihesabu lakini haiihifadhi). Ama i-persist kwenye state parquet, ama iondolewe kwenye
  schema ya K4. Kufundisha na column tupu ni kelele isiyo na maana.
- **S2 (FIX/runbook):** coverage audit KAMILI ya charter (NaN% per feature × pair × mwaka,
  pairs 12 × TF) haiwezekani kutoka repo — state parquets ziko PC ya Operator. Ninachokiweza
  kuthibitisha (pairs 2 za K4 + tags za atlas) ni safi. Runbook item ndogo kwa Operator:
  script ya coverage (loop ya `state_path` zote → jedwali) kabla ya kupanua curriculum kwa
  pairs 12. SIYO blocker ya M3-5 (K4 inatumia pairs 2 zilizothibitika).
- **S3 (documentation):** semantiki za session kwa HTF bars: hour ya D1 bar daima 00 →
  session="ASIA" daima (angalia Q2); H4 session = saa ya OPEN ya bar (coarse). Iandikwe
  kwenye kitabu ili lesson-generators wasiitumie vibaya.

### A2. Kitabu 2 — K4 DATASET (4,222 rows; nr7 STRAT-001/002, TRAIN+VALID)

**A2.1 Label integrity: PASS — kiwango cha juu.** Ushahidi:
- Baselines zina-MATCH artifacts za proven kwenye git kwa combos ZOTE 4 (strategy×split):
  STRAT-001 train N=1,607 EV +0.357 win 71.13% == `ccfbb24`; valid N=425 EV +3.068 win 79.29%
  == `e1a0d27`; STRAT-002 train N=1,746 +1.977/58.99% na valid N=444 +4.051/60.59% vivyo hivyo.
  Hii inathibitisha pipeline ya K4 ni ILEILE ya proven (episodes + no-LATE + costs) — outcomes
  si simulation mpya inayoweza kupishana.
- `win == (pnl>0)` kwa rows zote; SL-exits 100% pnl<0; TP-exits 99.96% pnl>0 — exception
  MOJA (STRAT-001/2024: ATR 9.05 pips, TP-hit pnl −0.65) ni TP ndogo kuliko cost — hii ni
  UAMINIFU wa cost model, si bug. `pnl_R × risk == pnl` (max err 0.004 = rounding).
  `mfe_r ≥ 0 ≥ mae_r` na `mfe_r ≥ pnl_R` kwa rows zote. Hakuna duplicate rows (0/4,222).
- HOLDOUT guard: whitelist ya splits + assert `ts < 2025-01-01` (self-test [1]/[1b] — trap
  halisi, inakataa hata `validation` yenye ts za 2025).

**A2.2 Leak hunt (adversarial): CLEAN.** Single-feature AUC dhidi ya `win` (train, kila
strategy, features za mgombea 19): **max AUC = 0.532** (hour). Hakuna feature inayotabiri
kupita kiasi — hakuna leak signature. (Ujumbe wa pili muhimu kwa matarajio: features hizi
kila moja peke yake hazina nguvu — lift ya K4 itatoka kwa MCHANGANYIKO, na itakuwa ya wastani.
Mtu asiitegemee miujiza; §D6.)

**A2.3 Class balance / N per regime / miaka:** win 71%/59% (train) — imbalance ya wastani;
kila mwaka 2016-2024 upo na N 205-270 kwa strategy (hakuna mwaka-pengo); regime cells kuu
zote N≥66. Cells "hazifundishiki bado" (N<30): spread_state=UNKNOWN (19/14 rows),
d1_vol_state="None" (1) — §B.

**FIXES za K4 (kabla ya M3-5 — rebuild deterministic, hakuna re-research):**
- **K-1 (REQUIRED):** ongeza `ts_entry` (na `entry_bar`) kwenye kila row. Bila timestamp:
  (a) non-overlap haiwezi kuthibitishwa KUTOKA kitabu chenyewe (naithibitisha kwa code ya
  episodes, lakini kitabu kinapaswa kujitosheleza); (b) **time-aware/blocked CV ya M3-5
  HAIWEZEKANI** — na CV ya kawaida (random K-fold) juu ya trades zenye serial correlation
  ita-overfit kimya (§D3).
- **K-2 (REQUIRED):** FEATURE MANIFEST — constant `FEATURES = [...]` ndani ya `k4_dataset.py`
  (na kwenye report) inayotenganisha rasmi FEATURES (decidable, signal-bar) na OUTCOMES
  (`pnl_*`, `win`, `exit_type`, `bars_held`, `mfe_*`, `mae_*`, `mfe_peak_bar`). Zote zimo
  kwenye jedwali moja — trainer akikosea kuingiza `mfe_r` kama feature, model "itajua" siku
  za baadaye kwa usahihi wa ajabu na hakuna trap itakayomshika. Loader ya M3-5 i-assert
  dhidi ya manifest.
- **K-3 (REQUIRED):** ondoa `atr_n` (au i-persist engine-side — S1).
- **K-4 (ndogo):** kategoria ya string `"None"` kwenye `d1_vol_state` (row 1) — null-cast
  artifact; itumie null halisi.
- **K-5 (documentation):** cells za §B "hazifundishiki" ziandikwe kwenye kitabu.

### A3. Kitabu 3 — ATLAS (186,512 rows; events 21 × pairs 12 × TF 3 × params 12 × mwaka × vol)

**Muundo na uaminifu wa msingi: PASS.** Breadth za report ninazizalisha upya (nr7×H4×HIGH
10/12 ✓, shock×H4×LOW 10/12 ✓, nr7×D1×LOW 10/12 ✓, lowvol_rev×D1×NORMAL 10/12 ✓). TRAIN-only
guard halisi (PermissionError kwa validation/holdout — self-test [3], nimeiendesha). Swap ndani
ya ev_net inathibitika (drag ya D1 9.2 pips vs H1 4.4 — carry inahesabika kweli). Atlas
inajitangaza "RAMANI, si madai" na haina FDR kwa makusudi — sahihi kimuundo, ILA:

**A3.1 Matokeo ya breadth bila stability ni nusu-ukweli.** Mifano kutoka star-combos za report
(recompute yangu, pooled kwa mwaka):
- `lowvol_reversal×D1×NORMAL` (top-20): breadth 10/12 LAKINI miaka EV+ ni **3/7 tu** —
  2022 (+205 pips!) na 2020 zinabeba kila kitu; 2017/2018/2021 ni −85/−51/−49. Hii si lesson,
  ni bahati ya miaka miwili.
- `nr7_break×H4×HIGH`: breadth 10/12, miaka **4/7** (2016 −15, 2020 −18).
- Kinyume chake `nr7_break×D1×LOW`: breadth 10/12 NA miaka **7/7** EV+, pairs 10/12 chanya
  kwa mpangilio mzuri (GBPJPY +97, EURJPY +53, USDJPY +35, ..., hasi mbili ndogo tu; XAUUSD
  +988 ni units za gold) — hii NDIYO umbo la lesson halali ya ramani.
Charter §pair-lessons tayari inasema "ranked kwa STABILITY si cell moja" — lakini report ya
atlas (ambayo ndiyo watu watasoma) ime-rank kwa BREADTH pekee. FIX A-1: breadth table iongeze
column "miaka EV+ /7" (ipo tayari kwenye parquet — ni aggregation moja).

**A3.2 QUARANTINE — angalia §B (binding).** Kubwa zaidi: rows za `vol_state=UNKNOWN` ni
**2016 PEKEE** (uthibitisho: mwaka pekee wenye UNKNOWN kwenye parquet ni 2016 — 24% ya rows,
28% ya trades za 2016; warmup ya terciles). **7 kati ya 20 za top-20 ya report ni combos za
UNKNOWN** — hizo ni "lessons za 2016 zilizojificha kama regime". Zisiingie kitabu chochote.

**A3.3 Thinness:** 55.7% ya rows zina n<30 (median n=25). Row moja ya atlas SI lesson kamwe —
lessons ni aggregations (event×pair×tf×regime juu ya miaka/params) zenye N ya pamoja + year
count. Rule hii iandikwe kwenye lesson-generator.

---

## B. QUARANTINE LIST (haziingii kitabu cha kufundishia — binding kwa pair-lessons na K4)

| # | Nini | Kwa nini (namba) |
|---|---|---|
| Q1 | Atlas rows/combos ZOTE zenye `vol_state=UNKNOWN` (incl. 7/20 ya top-20 ya report) | UNKNOWN = 2016 pekee (warmup) — regime-label ya uongo, confound kamili na mwaka 2016 |
| Q2 | `sess_top` kwa TF=D1 (rows 53,876) | hour(D1 bar)=00 daima → "ASIA" 100% — artifact, si taarifa; H4 session itumike kwa tahadhari (open-hour ya bar ya masaa 4) |
| Q3 | Row yoyote ya atlas n<30 kama lesson ya pekee (55.7% ya rows; median n=25) | kelele; lessons = aggregations tu (N pamoja + miaka EV+ ≥5/7) |
| Q4 | Combos zenye breadth bila year-stability: `lowvol_reversal×D1×NORMAL` (3/7 miaka; 2022 +205 inabeba), `nr7_break×H4×HIGH` (4/7) na yoyote <5/7 | breadth 10/12 inaficha utegemezi wa mwaka mmoja-mbili |
| Q5 | Exit-lessons kutoka MFE ya trades za SL-exit bila tahadhari | `excursions` inajumuisha bar ya exit NZIMA (high/low baada ya exit intra-bar) → MFE ya walioshindwa ime-inflate — "faida iliyokuwepo" inazidishwa |
| Q6 | K4 regime-cells N<30: spread_state=UNKNOWN (n=19/14), d1_vol_state="None" (n=1) | charter: "haifundishiki bado" — model isijifunze kelele za cell tupu |
| Q7 | D1 swing-lessons zenye \|EV\| ≲ 10 pips | swap model ni symmetric, hakuna weekend-triple, hakuna rate-differential sign — error band ya carry inameza edge za ukubwa huo |

## C. MAPENDEKEZO YA KUBORESHA CURRICULUM (zaidi ya fixes za §A)

1. **A-1:** breadth tables za atlas report ziongeze "miaka EV+ /7" + median-N — stability
   inaonekana papo hapo, na Q4 inajitekeleza yenyewe machoni.
2. **Lesson-generator isome PARQUET (na quarantine §B), kamwe si report ya markdown** —
   report ina UNKNOWN rows kwenye top-20; mtambo unaosoma report utafundisha uongo.
3. **K4 iongeze `pair` disaggregation rasmi ya mafunzo:** strategies 2 zina payoff geometry
   tofauti (SL2/TP1 vs SL1/TP1; baselines 71% vs 59%) — M3-5 itrain per-strategy AU iwe na
   strategy indicator + calibration per strategy; kamwe si pooled bila hilo.
4. **VALID selection-taint iandikwe NDANI ya kitabu cha K4** (§D1) — kila mtumiaji wa baadaye
   aione bila kunikumbuka mimi.
5. **Server-time/DST:** `hour` ni server-time; DST inahamisha London/NY ±1h kwa wiki kadhaa
   kwa mwaka — lesson za hour-level zina jitter; session-level ni imara zaidi. Andika.

## D. HATARI ZA MAFUNZO AMBAZO HAZIKUWA KWENYE CHECKLIST (out-of-the-box — sehemu yangu)

1. **VALID ya K4 ni selection-tainted.** STRAT-001 aliCHAGULIWA kwa VALID 2023-24 (pekee
   1/1,939 wa FDR) — win yake ya VALID 79.3% ni order statistic (holdout halisi: 73.9%).
   STRAT-002 vivyo (kuchaguliwa kutoka B3a ya VALID). Model ya M3-5 iki-tune AU iki-ripotiwa
   "lift" juu ya VALID hii, lift ita-overstate kimuundo. NIDHAMU: model selection = blocked CV
   ndani ya TRAIN pekee; VALID = check MOJA isiyo na tuning; hukumu halisi = forward (M3-6 gate
   tayari ipo). Namba za kutarajia: kama filter inaonyesha +X pips lift kwenye VALID, tarajia
   ~0.35-0.5× ya hiyo mbele (slope ya shrinkage iliyopimwa ya mfumo huu).
2. **Outcome columns ndani ya jedwali la features** (K-2) — hatari #1 ya kiufundi ya M3-5.
   Leak hii haina trap ya kuikamata leo; manifest + assert ndiyo trap.
3. **Serial correlation + random K-fold = leakage ya jirani.** Trades za nr7 zinafuatana kwa
   siku za volatility zinazofanana; random folds zinaweka jirani wa muda kwenye train NA test
   → CV score ya uongo. Blocked CV kwa muda (kwa mwaka au blocks za wiki±purge ya bars 24)
   — inahitaji K-1 (ts).
4. **Accuracy ni metric ya uongo hapa** (baseline 71%/59%): classifier "wote washinda" unapata
   accuracy 71% na thamani 0. Metric rasmi za M3-5 (nitaziweka kwenye design): EV-per-trade ya
   filtered vs unfiltered kwa retention iliyowekwa mapema (mf. 70%/50%), streak-za-hasara
   reduction, EV retention (charter tayari inataja) — zote kwa CI za bootstrap.
5. **Model inaweza kujifunza "mwaka" kupitia proxies** hata bila column ya year (mf. atr_pips
   levels ni regime ya kipindi). Kwa deployment hili ni non-stationarity risk: feature zenye
   maana ya ABSOLUTE level (atr_pips) zibadilishwe na relative/deseasonalized (atr_n — sababu
   nyingine ya S1/K-3 kufanywa vizuri) au model i-check kwa per-year stability ya coefficients.
6. **Matarajio ya lift yawe ya wastani:** max single-feature AUC 0.532; N_train ~1.6-1.7k kwa
   strategy; serial correlation inapunguza effective N. Model sahihi hapa ni logistic yenye
   regularization / tree ya kina 2-3, interpretable, na hypothesis ya kwanza ni "hakuna lift
   ya maana" — kuikataa kwa ushahidi ndiyo mafanikio. Deep nets = hapana (overfit ya uhakika
   kwa N hii).
7. **Atlas top-20 kama chanzo cha hypotheses za M3-3 (Chief):** wingi wa combos ~756
   (event×TF×vol) umeangaliwa bila multiplicity accounting — sahihi kwa RAMANI, lakini Chief
   akichagua hypotheses kutoka top ya jedwali hili, S2-pooled inayofuata inarithi selection
   ile ile ya "max order statistics". Tayari mfumo unajua dawa yake (registration + FDR/RW) —
   nakumbusha tu kwamba breadth+stability screen (Q4) ipunguze orodha KABLA ya kuangalia EV.

## E. RUHUSA / KATAZO (hati ya gate)

**M3-5 inaruhusiwa kuanza ("GO") MARA TU** K-1 (ts_entry), K-2 (feature manifest + assert),
K-3 (atr_n) zitakapotua — rebuild ya k4_dataset ni deterministic na ya dakika chache kwenye PC
ya Operator; hakuna re-research, hakuna dirisha jipya. S1/S2/A-1 na quarantine §B zinabidi
zitue kabla ya **pair-lessons/atlas kuwa kitabu cha model yoyote** (M3-3 hypotheses za Chief
zinaweza kuendelea sasa, na Q4-screen). Bila K-1..K-3, M3-5 ni KATAZO — si kwa sababu data ni
mbovu (siyo), bali kwa sababu mafunzo bila time-CV na bila manifest yatazalisha model
isiyoaminika kwa njia ambazo hazitaonekana mpaka iwe live.

*SCIENTIST-D · Kila namba: `scripts/scientist_d_m3_audit.py` + self-test runs zangu (transcript
ya session) · Vyanzo: k4_dataset.parquet / rmap_train.parquet (working tree, commits `3b13680`/
`a6dcb40`), proven artifacts `ccfbb24`/`e1a0d27`, code `src/research/*` @ `c7ea0ae`.*
