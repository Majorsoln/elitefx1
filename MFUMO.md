# MFUMO WA ELITEFX

EliteFX ni mfumo wa kufanya biashara ya forex unaolenga kupita changamoto za
prop firm — hasa **FTMO** — kwa pairs 9 kuu za forex. Mfumo umejengwa kwa
**tabaka (layers)** zinazofuatana: kila tabaka lina kazi moja wazi, na linapokea
matokeo ya tabaka lililo chini yake. Tabaka ya usimamizi wa hatari (**Compliance**)
ina mamlaka ya juu kuliko zote — ikisema "hapana", trade haifunguki, hata kama
signal ni nzuri kiasi gani.

Falsafa ya mfumo ni rahisi: **tunasoma soko kutoka juu kwenda chini.** Tunaanza
na picha kubwa ya siku (D1), tunashuka kuthibitisha mwelekeo (HTF), kisha
tunaingia kwa usahihi kwenye timeframe ndogo (15m/30m). Kila uamuzi unalindwa na
usimamizi wa hatari unaohakikisha hatuvunji sheria za FTMO.

Kipimo pekee cha mafanikio ni **"Pass Rate"**: kati ya maelfu ya simulations
(Monte Carlo), ni mara ngapi tunafikia lengo la faida (+10%) KABLA ya kugonga
kikomo cha hasara (-5% ya siku au -10% jumla). **Lengo: Pass Rate ≥ 60%.**

> **Kanuni kuu ya kazi:** Hakuna kinachoenda mbele bila kuthibitishwa kwa data.
> Tukibadilisha kitu, tunabadilisha **KIMOJA** kwa wakati, kisha tunapima athari.

---

## Ramani ya Mfumo

Tabaka zinazofuatana — kutoka data ghafi hadi trade iliyofunguliwa:

```
  SEHEMU 1   DATA              Dukascopy ticks → candles (D1…15m), safi, bila lookahead
     │
     ▼
  SEHEMU 2   MODEL 1           Regime Classifier (HMM → LightGBM)
     │       (Trend Zone)      → { regime: UP/DOWN/RANGE, confidence }
     │                           "Je, conditions zinaunga mkono biashara leo?"
     ▼
  SEHEMU 3   MODEL 2           Entry Engine (Autoencoder → DBSCAN → LightGBM → RSF)
     │       (Entry 1m–30m)    → signal kamili: entry, sl, tp, duration, confidence
     │                           "Hapa hasa ndiyo entry."
     ▼
  SEHEMU 4   SIZING            DailyRiskBudgetSizer → lotsize
     │                           "Kiasi gani — kwa bajeti ya hatari ya siku?"
     ▼
  SEHEMU 5   COMPLIANCE        Checks 5 (Daily Loss, Total DD, Slots, Corr, Spread)
     │       ⚖ MAMLAKA YA JUU   → RUHUSA au KATAA  "Je, ni salama? Mamlaka ya mwisho."
     ▼
  ═══════════ TRADE INAFUNGULIWA (MT5) ═══════════
     │
     ▼
  SEHEMU 6   TRADE MGMT        R1–R7: breakeven, partial, trail, TP adjust, exits
             (R1–R7)            "Simamia trade hadi exit."

  ───────────────────────────────────────────────────────────────
  SEHEMU 7   UTHIBITISHAJI     Phase A → Phase B → OOS → Monte Carlo (Pass Rate ≥ 60%)
                                Kila signal lazima ipite KABLA ya execution.
  SEHEMU 8   FTMO RULES        Sheria za changamoto (Case Study: $10,000)
  SEHEMU 9   MAJUKUMU          Nani anafanya nini
```

> **ML inatabiri soko (Model 1, 2). Rules zinasimamia pesa (Sizing, Compliance,
> R1–R7).** Mstari huu hauvukwi — ubongo wa ML, mkono wa sheria zilizothibitishwa.

---

## SEHEMU 1 — Data

*Eneo la kuandaa data, kuhakikisha ubora wake, na kuamua itumikeje. Hapa ndipo
data analysis hufanyika.*

- **Chanzo cha mafunzo:** Dukascopy tick data (2016–2024). FTMO MT5 hutumika
  **kuweka trades tu** — kamwe si chanzo cha data ya mafunzo.
- **Pairs 9:** EURUSD, GBPUSD, USDJPY, EURJPY, USDCAD, USDCHF, AUDUSD, NZDUSD, EURGBP.
- **Bars:** Kutoka tick data tunajenga candles za **1m, 5m, 15m, 30m, H1, H2, H4, D1**.
  - **1m–30m** → microstructure ya Model 2 (Entry, Sehemu 3: "1m → 30m").
  - **H1–D1** (pamoja na **H2**) → HTF ya Model 1 (Regime, Sehemu 2).
  - *(5m ni nyongeza ya uchambuzi kujaza pengo la microstructure kati ya 1m na 15m.)*
- **Timezone:** tick data ghafi ni tz-aware (CE(S)T, instant kamili). Tunaibadilisha
  → **UTC** mara moja kwenye ujenzi wa candles; timestamps zote zimehifadhiwa UTC.
  - **HTF day-boundary (D1/H4/H2):** zime-anchor kwa **00:00 CE(S)T** (sio UTC),
    kulingana na FTMO daily reset + rollover. Mfano: D1 inaanza 23:00 UTC (winter) /
    22:00 UTC (summer). Sub-H1 (1m–H1) hazibadiliki (CET offset ni saa kamili).
- **Tick volume:** `bid_vol`/`ask_vol` zinahifadhiwa kama `tick_count`, `bid_volume`,
  `ask_volume`, na `volume_imbalance`. `tick_count` hutumika kama **filter ya liquidity**
  (kuruka nyakati za tick ndogo — rollover/holidays). `volume_imbalance`: ona "Matokeo
  ya diagnostics" hapa chini — **haitabiri** next-bar return (IC≈0). **Si rule** —
  ML inazitumia, hazifungui trade.
- **Uhakiki wa ubora:** Hakuna mapengo (gaps) yasiyoelezeka, hakuna lookahead
  (data ya baadaye haitumiki kwenye uamuzi wa sasa), na **spread halisi kwa kila
  pair** (sio thamani moja kwa zote — JPY pairs zina spread kubwa zaidi).
- **No-trade window (rollover):** EDA imethibitisha spread inapanda mara 3+ wakati
  wa rollover ya broker — saa **23:00 CET** (= 21:00/22:00 UTC kwa DST). Tunaanchor
  kwa **CE(S)T** (broker local), na model haifungui trade dirisha hili.
- **Matokeo ya diagnostics (uthibitisho wa kitakwimu — `reports/feature_diagnostics.md`):**
  Kabla ya kujenga model, tulipima *mali za kitakwimu* za data. Matokeo 4 yanayobadilisha mtazamo:
  1. **Fat tails — Student-t imethibitishwa kwa conditional normality (8/9):** returns
     ghafi zina excess kurtosis hadi 25.9, na sehemu kubwa ni vol-clustering (mixture).
     LAKINI baada ya kustandardize kwa rolling-vol, **8/9 bado zina excess kurtosis > 1**
     (GBPUSD 5.1, EURJPY 6.3, USDJPY 4.1) na tail exceedance 3–6× Gaussian (3σ), ~1000×+ (5σ).
     → **Model 1 itumie vol-standardized returns NA Student-t emissions** (sio pure Gaussian).
  2. **Vol clustering (9/9):** ACF(r)≈0 lakini ACF(r²)=0.10–0.16. → regimes ni **HALISI**;
     **HMM/Model 1 ina msingi wa kitakwimu.**
  3. **`volume_imbalance` haitabiri (250k+ bars/pair):** Predictive IC≈0 (−0.001…+0.006),
     hit-rate < 0.50 kote. Inaakisi move ya bar ya sasa tu (contemporaneous +ve). →
     **Model 2 isiifanye signal kuu** (ona Sehemu 3).
  4. **Correlation inabadilika:** jozi 3/6 Δ≥0.20 kati ya 2016–2020 na 2021–2026 (EURJPY–EURGBP
     inageuza ishara). → Compliance itumie **rolling/net-exposure**, sio groups za static (Sehemu 5).
- **Lengo la sehemu hii:** Kuhakikisha data ni safi na halisi kabla ya kuijengea
  chochote juu yake. Data mbovu = mfumo mbovu.

---

## SEHEMU 2 — Model 1: Regime Classifier (Trend Zone)

*Hii ndiyo model ya kwanza na msingi wa mfumo wote. Inachukua hali ya soko
kutoka D1 hadi H1, kisha inatoa jibu moja: soko liko UP, DOWN, au RANGE — na
kwa uhakika gani. Kila tabaka juu yake (entry, sizing, compliance) inategemea
output ya model hii.*

### Jukumu

Model hii inasuluhisha tatizo ambalo rules za kawaida (EMA200, ADX) haziwezi
kulisuluhisha vizuri: **D1 na HTF nyingi zinaweza kupingana** — H4 inasema bull,
H1 inasema bear, D1 inasema flat. Rules za if/else haziamui vizuri hali hizi.
Model inajifunza kutoka data ya kihistoria ni combination gani zinaongoza kwa
nini.

### Mbinu: Hybrid (HMM → LightGBM)

```
HATUA 1 — HMM (Unsupervised)
  Input:  returns na volatility za D1/H4/H1 (bila lookahead)
  Output: hidden state sequence → {UP, DOWN, RANGE}
  Faida:  HMM inagundua regimes kutoka kwa data yenyewe — bila bias ya mtu.
          Inatupa labels za "halisi" za kihistoria.

HATUA 2 — LightGBM (Supervised)
  Input:  features za D1+HTF (EMA slopes, ADX, hali za kila TF, HMM state, …)
  Output: P(UP), P(DOWN), P(RANGE) — uwezekano wa regime inayokuja
  Faida:  inatabiri regime ya KESHO, sio ya leo.
          HMM output inakuwa feature moja kati ya nyingi.
```

> **Noti ya data (diagnostics, Sehemu 1) — IMETHIBITISHWA:** returns ghafi zina fat
> tails (kurtosis hadi 25.9), na conditional-normality test ilionyesha sehemu kubwa ni
> vol-clustering. LAKINI baada ya kustandardize kwa rolling-vol, **8/9 bado zina excess
> kurtosis > 1** (GBPUSD 5.1, EURJPY 6.3) na tails 3–6× Gaussian → fat tails za kweli
> zinabaki. **Uamuzi:** HATUA 1 itumie **vol-standardized returns NA Student-t emissions**
> (vol-scaling kwa clustering; Student-t kwa residual tails). Vol clustering (ACF r²=
> 0.10–0.16) imethibitisha regimes ni halisi — msingi wa HMM upo bila shaka.

**Kwa nini Hybrid?**
- HMM peke yake inabainisha regime ya **sasa** — haioni mbele.
- LightGBM peke yake inahitaji labels — ukitumia EMA/ADX kama labels, inajifunza
  tu kuiga rule, haina thamani ya ziada.
- Pamoja: HMM inatoa label ya kihistoria (bila bias), LightGBM inajifunza
  kutabiri regime **inayokuja** kutoka kwa pattern ya features za sasa.

### Features za LightGBM (mifano)
- Hali (state) za D1, H4, H2, H1 kwa wakati `t`
- EMA200 slope kwa kila TF
- ADX kwa kila TF
- Bei dhidi ya EMA kwa kila TF (umbali wa asilimia)
- HMM hidden state ya sasa
- HMM transition probability (uwezekano wa kubadilika regime)

### HTF Weight Mechanism

Sio lazima timeframes zote 3 ziwe aligned. LightGBM inajifunza uzito bora
wa kila TF kutoka data — H4 kwa kawaida itakuwa na uzito mkubwa zaidi, H1
mdogo zaidi, lakini hii itaamuliwa na data, sio mkono.

### Matokeo ya Model
```
Output: { regime: "UP" | "DOWN" | "RANGE", confidence: 0.0–1.0 }

Mfano: { regime: "UP", confidence: 0.78 }
→ Hii inamaanisha: "conditions za sasa zinaonyesha UP kwa 78%"
→ Tabaka inayofuata (Entry) inafanya kazi kwa signal za UP tu.
→ Kama confidence < kizingiti (e.g. 0.60), hatufanyi biashara.
```

> **Kanuni:** Model hii **haiamui entry** — inaamua tu "je, conditions zinaunga
> mkono biashara leo?" Entry bado inafanywa na tabaka inayofuata (Sehemu 3).

---

## SEHEMU 3 — Model 2: Entry Intelligence Engine (1m → 30m)

*Model ya pili — inachambua microstructure ya soko kutoka 1m hadi 30m kwa akili
ya scalper wa hali ya juu. Inatambua patterns zinazojulikana NA zisizojulikana.
Entry halisi hufanywa kwenye 15m au 30m, lakini uamuzi unategemea picha kamili
ya 1m–30m.*

### Jukumu

Model 1 ilisema "leo ni siku ya UP" — Model 2 inasema "**hapa hasa ndiyo entry,
kwa bei hii, TP hii, na itachukua muda huu**." Inaunda signal kamili.

### Architecture: Unsupervised Discovery + Supervised Refinement

```
HATUA 1 — Representation Learning (Autoencoder / Transformer Encoder)
  Input:  windows za bei 1m → 30m (candles N za kila TF)
  Output: embedding — vector ndogo inayowakilisha pattern ya soko
  Faida:  model inajifunza "lugha" ya soko yenyewe, bila mwongozo

HATUA 2 — Pattern Discovery (DBSCAN Clustering)
  Input:  embeddings za historia yote (2016–2024)
  Output: makundi ya patterns zinazofanana
          → Zinazojulikana: RETEST, MOMENTUM, BREAKOUT, ...
          → Mpya (hazina jina): PATTERN_07, PATTERN_12, ...
  Faida:  inagundua YOTE — si zilizotajwa tu na mtu

HATUA 3 — Semi-supervised Labeling
  → Makundi yanayolingana na patterns zinazojulikana → weka label
  → Makundi mapya → yabaki kama PATTERN_XX, chunguza baadaye
  → Makundi ya noise → tupa

HATUA 4 — Entry Classifier (LightGBM)
  Input:  embedding + pattern label + hali ya Model 1 +
          session + spread + umbali kutoka S/R levels
  Output: { valid: bool, signal_type: str, confidence: float }

HATUA 5 — Duration Regressor (Random Survival Forest)
  Input:  features sawa + SL/TP distance
  Output: predicted_bars_to_target  →  hii NI R7 Time-Stop
          + probability ya kufika target (tp_probability)
```

> **Noti ya data (diagnostics, Sehemu 1):** `volume_imbalance` **HAITABIRI** next-bar
> return (predictive IC≈0, hit-rate < 0.50 kwa bars 250k+/pair). Inaakisi move ya bar
> ya **sasa** tu. Kwa hiyo **isiwe feature kuu ya HATUA 4.** Inaweza kupimwa upya kama:
> (a) interaction/non-linear, (b) horizon ndefu, (c) *filter ya confirmation* (sio
> predictor), (d) conditional kwa regime — lakini **bila ushahidi mpya, isitegemewe.**

### Output ya Signal (Kamili)

```python
{
  "signal_name":        "RETEST_BULL_H4",    # au "PATTERN_07"
  "signal_source":      "H1 demand zone retest at 149.820",
  "entry":              149.835,
  "sl":                 149.720,
  "tp":                 150.180,
  "predicted_duration": 14,      # bars za 15m → R7 Time-Stop
  "tp_probability":     0.71,    # uwezekano wa kufika TP
  "confidence":         0.83
}
```

Signal hii ndiyo inayopita kwenye tabaka zinazofuata:
Sizing (Sehemu 4) → Compliance (Sehemu 5) → Trade Management (Sehemu 6).

### Target (TP) na Duration — Vinatoka Wapi

Mambo mawili muhimu kwenye signal — **TP** na **predicted_duration** — havikisiwi.
Vinatoka ndani ya Model 2 kwa uchambuzi wa data:

```
TARGET (TP):
  Inatabiriwa kutoka structure ya soko — level inayofuata ya
  significance (S/R, swing high/low), iliyochujwa na embedding ya
  pattern. Si "pips fasta" — ni level halisi ambapo bei inaelekea.

PREDICTED_DURATION → chanzo cha R7 Time-Stop:
  Random Survival Forest (HATUA 5) inatabiri bars ngapi trade
  itachukua kufika target. Hii inatokana na distribution halisi:
    → Kwenye backtest: trades zilizoshinda zilichukua bars NGAPI?
    → predicted_duration ni makadirio ya kila signal binafsi.
    → R7 = predicted_duration × time_stop_multiplier (Sehemu 6).
       Multiplier inawekwa ili R7 ikae karibu na 75th–90th
       percentile ya muda wa trades zinazoshinda.
```

**Mantiki ya R7:** Trade nzuri huelekea target haraka. Ikikaa muda mrefu kuliko
wastani wa zinazoshinda, uwezekano wa kushinda unapungua — edge imeisha. R7
inakata trade hizo "zilizopoa" badala ya kusubiri SL au TP isiyofika.

### Kwa Nini Unsupervised Kwanza?

Supervised learning inaweza tu kujifunza patterns ulizomwambia itafute. DBSCAN
kwenye embeddings inaruhusu kugundua muundo halisi wa soko — ikiwa ni pamoja na
patterns ambazo binadamu hawakuwahi kuzitaja au kuziona. Patterns mpya zilizo na
edge nzuri zinaweza kuwa fursa kubwa zaidi ya zile zinazojulikana.

> **Kanuni:** Patterns mpya (PATTERN_XX) zinachunguzwa kwa Phase A na Phase B
> kama signal yoyote nyingine — haziruhusiwi kwenye execution bila uthibitishaji.

---

## SEHEMU 4 — Position Sizing (DailyRiskBudgetSizer)

*Kuhesabu ukubwa sahihi wa lot kwa kila trade — kutoka bajeti ya hatari ya siku
inayobadilika kulingana na matokeo halisi ya leo.*

### Tatizo Tunalolisuluhisha

Sizing ya kawaida ("hatarisha 1% kwa kila trade") haisaidii kuzuia Daily Loss
ya FTMO kwa njia ya akili. Ukiwa na trades 10 zinazopoteza mfululizo, kila moja
inachukua 1% — unagonga -5% bila ya mfumo kujizuia. **DailyRiskBudgetSizer**
inasuluhisha hili kwa kufanya kikomo cha siku kuwa sehemu ya hesabu ya kila
trade — si geti la mwisho tu.

### Jinsi Inavyofanya Kazi

```
HATUA 1 — Hesabu bajeti ya siku (inasasishwa baada ya kila trade)

  bajeti = daily_budget_start
           + (WIN_FACTOR  × jumla_ya_faida_za_leo)
           − (LOSS_FACTOR × jumla_ya_hasara_za_leo)

  → Ukishinda, bajeti inakua kidogo (unaweza kuchukua nafasi zaidi)
  → Ukipoteza, bajeti inapungua mara moja (lotsize inashuka yenyewe)
  → Bajeti haiwezi kuwa chini ya 0 (hakuna dhambi ya uongo)

HATUA 2 — Gawanya bajeti kwa slots zilizobaki

  bajeti_kwa_trade = min(
      bajeti_iliyobaki ÷ slots_zilizobaki,   # sehemu sawa
      max_per_trade                           # kikomo cha juu
  )

HATUA 3 — Hesabu lotsize kutoka SL ya signal

  lotsize = bajeti_kwa_trade ÷ (sl_pips × pip_value)

  → Kama sl_pips ni kubwa, lotsize ni ndogo (hatari sawa)
  → Kama sl_pips ni ndogo, lotsize ni kubwa (hatari sawa)
  → Pip value inahesabiwa kwa kila pair kwa bei halisi ya wakati huo

HATUA 4 — Piga chini kwenye lot minimum ya broker (0.01 lots)
          Ikiwa hesabu inatoa chini ya minimum, acha signal — sio safe.
```

### Mfano Halisi ($10,000, siku moja)

```
daily_budget_start = $400   win_factor = 0.50   loss_factor = 1.00
max_slots = 4               max_per_trade = $120

09:00 — Trade 1 (EURUSD): SL = 20 pip, sl_value = $20
  bajeti_iliyobaki = $400
  bajeti_kwa_trade = min($400÷4, $120) = $100
  lotsize = $100 ÷ $20 = 0.50 lots  ✓ (inafunguliwa)

10:30 — Trade 1 inapoteza −$80 (SL igongwa kwa 0.40 lots)
  bajeti_iliyobaki = $400 − (1.00 × $80) = $320

11:00 — Trade 2 (USDJPY): SL = 25 pip, sl_value = $23
  bajeti_kwa_trade = min($320÷3, $120) = $106
  lotsize = $106 ÷ $23 = 0.46 lots

13:00 — Trade 2 inashinda +$180
  bajeti_iliyobaki = $320 + (0.50 × $180) = $410
  → Bajeti imekua kidogo kwa sababu ya ushindi

15:00 — Trade 3 (GBPUSD): SL = 30 pip
  bajeti_kwa_trade = min($410÷2, $120) = $120
  lotsize = hesabu kwa pip value ya GBPUSD
```

*Angalia jinsi bajeti inavyobadilika kiotomatiki — mfumo unajilinda bila
maamuzi ya mtu.*

### Faida ya Mbinu Hii Dhidi ya FTMO Rules

| Hali | Fixed 1% Sizing | DailyRiskBudgetSizer |
|------|----------------|----------------------|
| Trades 5 za kupoteza mfululizo | −5% → **Fail** | Bajeti inashuka kila mara → lotsize inapungua → hasara halisi ni chini ya −5% |
| Siku nzuri (faida nyingi) | Lotsize haibadiliki | Bajeti inakua kidogo → chukua nafasi zaidi bila kupita kikomo |
| SL kubwa (25 pip badala ya 15) | Hatari ya ziada | Lotsize inashuka kiotomatiki — hatari inadumu sawa |

### Config (Japhet Anaweka — Sio Mfumo)

```yaml
# ftmo_config.yaml — kwa akaunti ya $10,000
account_size:        10000   # ukubwa wa akaunti
daily_budget_start:    400   # bajeti ya mwanzo (4% ya akaunti)
win_factor:           0.50   # bajeti inakua 50% ya faida
loss_factor:          1.00   # bajeti inapungua 100% ya hasara
max_per_trade:         120   # kikomo cha juu kwa trade moja ($)
max_slots:               4   # trades nyingi zaidi kwa wakati mmoja
max_correlated_slots:    2   # trades nyingi zaidi kwenye correlation group moja
max_daily_loss:        500   # FTMO: 5% ya akaunti
max_total_dd:         1000   # FTMO: 10% ya akaunti
```

> **Kanuni:** Mfumo unafanya hesabu tu. **Japhet anabadilisha values.**
> Hatuanzi kubadilisha `win_factor` au `loss_factor` bila kupima athari kwanza.

---

## SEHEMU 5 — Compliance Engine (Usimamizi wa Hatari)

*Mlinda wa mwisho kabla ya kila entry. Ina mamlaka ya juu kuliko tabaka ZOTE —
hata kama Model 1 na Model 2 zimesema "ndiyo", Compliance inaweza kusema "hapana"
na uamuzi wake ndio wa mwisho.*

### Jukumu

Compliance haijali signal iko nzuri kiasi gani. Inajali swali moja tu:

> **"Kufungua trade hii sasa hivi — je, ni salama kwa akaunti na kwa sheria
> za FTMO?"**

Ikiwa jibu ni "hapana" katika kipengele chochote, trade **haifunguliwi**.
Hakuna mazungumzo, hakuna override.

### Mfumo wa Uamuzi (Sequence — Lazima Ipite Yote)

```
Signal inaomba ruhusa
         │
    ┌────▼────────────────────────────────────┐
    │  CHECK 1 — Daily Loss Guard             │
    │                                         │
    │  Hesabu: drawdown_wa_siku               │
    │    = balance_ya_mwanzo_wa_siku          │
    │      − (balance_ya_sasa + exposure_wote)│
    │                                         │
    │  Je, drawdown_wa_siku + worst_case_loss │
    │     ya trade hii ≥ max_daily_loss?      │
    │                                         │
    │  NDIYO → KATAA. Sababu: Daily Loss      │
    └────┬────────────────────────────────────┘
         │ HAPANA (sawa)
    ┌────▼────────────────────────────────────┐
    │  CHECK 2 — Total Drawdown Guard         │
    │                                         │
    │  Je, drawdown_ya_jumla + worst_case_loss│
    │     ya trade hii ≥ max_total_dd?        │
    │                                         │
    │  NDIYO → KATAA. Sababu: Total DD        │
    └────┬────────────────────────────────────┘
         │ HAPANA (sawa)
    ┌────▼────────────────────────────────────┐
    │  CHECK 3 — Slot Capacity                │
    │                                         │
    │  Je, open_trades ≥ max_slots?           │
    │                                         │
    │  NDIYO → KATAA. Sababu: Max slots       │
    └────┬────────────────────────────────────┘
         │ HAPANA (sawa)
    ┌────▼────────────────────────────────────┐
    │  CHECK 4 — Correlation Guard            │
    │                                         │
    │  Hesabu: corr_open = trades zilizopo    │
    │  zinazoshiriki group ya pair hii        │
    │                                         │
    │  Je, corr_open ≥ max_correlated_slots? │
    │  (max_correlated_slots = manual input)  │
    │                                         │
    │  NDIYO → KATAA. Sababu: Corr. limit    │
    │  HAPANA → RUHUSA (hata kama correlated)│
    └────┬────────────────────────────────────┘
         │ HAPANA (sawa)
    ┌────▼────────────────────────────────────┐
    │  CHECK 5 — Spread Guard                 │
    │                                         │
    │  Je, spread ya sasa > max_spread        │
    │  kwa pair hii (kutoka config)?          │
    │                                         │
    │  NDIYO → KATAA. Sababu: Spread kubwa   │
    └────┬────────────────────────────────────┘
         │ HAPANA (sawa)
         ▼
    ✅  RUHUSA KUTOLEWA — Trade inafunguliwa
```

### Worst-Case Exposure (Jinsi Inavyohesabiwa)

Compliance haangalii tu balance ya sasa — inaangalia **hatari ya juu kabisa
(worst-case)** kama trades zote zilizopo zigonga SL zao wakati mmoja:

```python
exposure_wote = sum(
    abs(open_trade.sl_distance_usd)
    for open_trade in open_trades
)

# Kisha ikiongezwa na hatari ya trade mpya:
total_worst_case = exposure_wote + new_trade.sl_distance_usd

# Daily Loss check:
projected_dd = current_daily_loss + total_worst_case
if projected_dd >= max_daily_loss:
    return KATAA
```

Hii inahakikisha hata kama "dhoruba" ya soko ikitokea na kila SL igongwe,
tuko salama.

### Correlation Guard (Kupunguza — Si Kuzuia Kabisa)

Pairs nyingi za forex zinafuata sawa. Mfano: EURUSD na GBPUSD zote mbili
zinaathiriwa na nguvu ya USD. Ukiwa na trades nyingi za SELL USD wakati mmoja,
hatari inazidika — lakini hii si sababu ya kuzuia kabisa. Tunaweka **kikomo cha
idadi** badala yake — na trader anaweka kikomo hicho mwenyewe.

```python
CORRELATION_GROUPS = {
    "USD_group":      ["EURUSD", "GBPUSD", "AUDUSD", "NZDUSD"],  # USD weakness plays
    "USD_strength":   ["USDJPY", "USDCAD", "USDCHF"],            # USD strength plays
    "EUR_group":      ["EURUSD", "EURJPY", "EURGBP"],
    "AUD_NZD_group":  ["AUDUSD", "NZDUSD"],
}

# Hesabu trades zilizopo kwenye group moja:
corr_open = count(
    t for t in open_trades
    if t.pair in CORRELATION_GROUPS[new_trade.group]
)

# Linganisha na kikomo cha manual:
if corr_open >= max_correlated_slots:
    return KATAA  # tumejaa — subiri moja itoke kwanza
# Vinginevyo: RUHUSA — hata kama trade nyingine iliyopo ni correlated
```

**Mfano (max_correlated_slots = 2):**
- EURUSD BUY open → USD_group: 1/2 → Trade mpya ya GBPUSD BUY: **RUHUSA** (2/2)
- EURUSD BUY + GBPUSD BUY open → USD_group: 2/2 → Trade ya AUDUSD BUY: **KATAA**
- EURUSD BUY + GBPUSD BUY open → USDJPY BUY (USD_strength group): **RUHUSA** (group tofauti)

### Config ya Correlation (Manual Input — Japhet Anaweka)

```yaml
# ftmo_config.yaml — sehemu ya correlation
max_correlated_slots: 2   # trades nyingi zaidi kwenye group moja wakati mmoja
                          # 1 = kali zaidi, 3 = loose, default = 2
```

*Kikomo hiki kinabadilishwa kwenye config tu — sio wakati wa biashara. Thamani
za correlation groups zinahesabiwa kutoka data ya kihistoria na zinasasishwa
kila robo mwaka.*

> **Noti ya data (diagnostics, Sehemu 1):** Correlation **inabadilika kwa muda** —
> jozi 3/6 zilihama Δ≥0.20 kati ya 2016–2020 na 2021–2026, na EURJPY–EURGBP iligeuza
> ishara kabisa (−0.08 → +0.18). Makundi ya static (`USD_group`, `EUR_group` n.k.)
> **hayaakisi data** (k.m. GBPUSD–EURGBP = −0.64). **Ushauri:** badilisha kuwa
> **rolling correlation** au **net-currency exposure** (sasisha kila robo, au dynamic),
> sio makundi ya kudumu yaliyowekwa kwa mkono.

### Logi ya Kila Uamuzi

Compliance inaandika **kila uamuzi** — sio tu "kataa" bali pia "ndiyo" — pamoja
na nambari halisi zilizotumika:

```
[2024-03-04 10:23:41] EURUSD BUY — CHECK 1 PASS (daily_dd=$180, limit=$500)
[2024-03-04 10:23:41] EURUSD BUY — CHECK 2 PASS (total_dd=$320, limit=$1000)
[2024-03-04 10:23:41] EURUSD BUY — CHECK 3 PASS (slots=2/4)
[2024-03-04 10:23:41] EURUSD BUY — CHECK 4 PASS (USD_group: 0/2 corr. slots used)
[2024-03-04 10:23:41] EURUSD BUY — CHECK 5 PASS (spread=1.2, limit=2.5)
[2024-03-04 10:23:41] EURUSD BUY — ✅ APPROVED → sent to execution

[2024-03-04 14:55:12] GBPUSD BUY — CHECK 1 FAIL
  daily_loss_now=$410 + worst_case=$95 = $505 ≥ limit=$500
  → ❌ REJECTED: Daily Loss Guard
```

Logi hii ni muhimu wakati wa kutatua matatizo — unaona kwa nini trade
ilikanushwa au kuruhusiwa.

### Mamlaka ya Compliance

```
┌─────────────────────────────────────────────────────┐
│                  MFUMO WA ELITEFX                   │
│                                                     │
│  Model 1 (Regime) ──┐                               │
│                     ├──▶ Signal ──▶ Sizing ──▶  ┌──┤
│  Model 2 (Entry)  ──┘                           │  │
│                                                 │  │
│  ┌──────────────────────────────────────────┐   │  │
│  │  COMPLIANCE ENGINE                       │◀──┘  │
│  │  (Mamlaka ya juu — haina makubaliano)    │      │
│  └──────────────────────┬───────────────────┘      │
│                         │                          │
│              KATAA ◀────┤────▶ RUHUSA              │
│                         │          │               │
│                         │          ▼               │
│                         │    Execution (MT5)       │
└─────────────────────────────────────────────────────┘
```

> **Kanuni ya chuma:** Compliance haibadilishwi wakati wa biashara.
> Ikiwa unataka kubadilisha kikomo (e.g. max_slots), fanya nje ya masaa ya
> biashara, baada ya kupima athari kwenye backtest.

---

## SEHEMU 6 — Trade Management (R1–R7)

*Mfumo wa kusimamia trade baada ya kufunguliwa — kutoka entry hadi exit.
Kila sheria (R1–R7) ina jukumu lake maalum na inafanya kazi kwa wakati wake.*

### Falsafa

Trade nzuri haihitaji kusimamia kwa mkono sana — lakini inahitaji **mfumo**
unaolinda faida inayokua na kukata hasara zinazokua. R1–R7 ni mfumo huo.
Sheria zinatumika kwa mfuatano wa hali — si kwa wakati mmoja wote.

> **Kanuni ya majaribio:** Tunajaribu kila sheria **PEKE YAKE** kwanza kwenye
> backtest, kisha tunachanganya zile zilizothibitisha faida ya ziada. Hatuanzi
> na zote pamoja — mchanganyiko wa sheria unaofanya vibaya unafichwa na mojawapo
> inayofanya vizuri.

---

### R1 — Breakeven (Kulinda Mtaji)

**Wakati:** Bei ikifika **+1R** (umbali wa SL mara moja upande wa faida)
**Hatua:** Sogeza SL kutoka mahali pa asili hadi **entry price** (± spread)

```
Entry: 1.2000   SL asili: 1.1980 (−20 pip = 1R)   TP: 1.2060 (+3R)

Bei inapofika 1.2020 (+20 pip = +1R):
  SL mpya → 1.2000 (entry)
  Matokeo: trade haiwezi kupoteza pesa tena
           hata kama inashuka, unatoka sifuri sifuri
```

**Kwa nini?** Inabadilisha trade kutoka "inaweza kupoteza" hadi "haiwezi
kupoteza." Hii inaathiri sana pass rate ya FTMO — hasara ndogo nyingi zinaweza
kuzuiwa kabla ya kugonga Daily Loss.

---

### R2 — Partial Exit (Kufunga Sehemu)

**Wakati:** Bei ikifika **+1R** (wakati huo huo na R1)
**Hatua:** Funga **50% ya position** kwa bei ya sasa — acha 50% iendelee

```
Position ya awali: 0.40 lots

Bei = +1R:
  → Funga 0.20 lots (50%) → faida halisi inaingia akaunti
  → Acha 0.20 lots (50%) iendelee kuelekea TP
  → SL ya 0.20 iliyobaki → sogeza hadi entry (R1)

Matokeo:
  Hata kama nusu iliyobaki inarudi entry: umeshinda faida ya nusu
  Kama nusu iliyobaki inafika TP: faida kamili ya nusu + ya kwanza
```

**Kwa nini?** Inafanya winrate dhahiri kuwa kubwa zaidi — unapata faida
kwenye kila trade inayofika +1R, hata kama haikufika TP kamili.

---

### R3 — Trailing Stop (Kufuatilia Faida)

**Wakati:** Bei ikifika **+2R** au zaidi, na trend bado ina nguvu
**Hatua:** SL inasogea kufuata bei kwa umbali uliowekwa (manual input)

```
Mbinu mbili za trailing — Japhet anachagua moja:

MBINU A — Fixed pip trail:
  Bei kila inapopanda X pip → SL inapanda X pip pia
  Mfano: trail_distance = 15 pip
  Bei = 1.2040 → SL = 1.2025
  Bei = 1.2055 → SL = 1.2040  (inafuata)
  Bei ishuke → SL haishuki (inabaki mahali ilipofika)

MBINU B — ATR trail:
  SL = bei_ya_juu_zaidi − (ATR_14 × multiplier)
  Inabadilika kulingana na volatility ya soko
  Faida: inafaa zaidi masoko yenye volatility tofauti
```

```yaml
# ftmo_config.yaml
trailing_method:    "fixed_pip"   # "fixed_pip" au "atr"
trail_distance_pip: 15            # kwa fixed_pip
trail_atr_mult:     1.5           # kwa atr (ATR_14 × 1.5)
trailing_start_r:   2.0           # anza trailing baada ya +2R
```

---

### R4 — Reduce TP (Kupunguza Lengo)

**Wakati:** Model 1 inabadilisha hali ya soko (e.g. UP → RANGE) na trade bado
iko wazi, lakini haijafika TP
**Hatua:** Punguza TP hadi **level ya karibu zaidi** (support/resistance)

```
Trade: EURUSD BUY, entry 1.2000, TP asilimia 1.2060
Bei sasa: 1.2035 (+1.75R)

Model 1 report → regime imebadilika: UP → RANGE
  Uamuzi wa R4: TP mpya → 1.2045 (resistance ya karibu)

Mantiki: soko halitaendelea kuelekea TP ya asili katika RANGE.
         Faida ndogo salama bora kuliko kusubiri TP ya mbali.
```

---

### R5 — Extend TP (Kupanua Lengo)

**Wakati:** Trend ina nguvu ya nje ya kawaida — momentum ya juu, candles kubwa,
breaking ya levels muhimu
**Hatua:** Ongeza TP hadi **level inayofuata** ya significance

```
Trade: USDJPY BUY, entry 149.50, TP asilimia 150.20
Bei = 150.10 (+3.5R), trend ina nguvu, hakuna resistance hadi 150.80

  Uamuzi wa R5: TP mpya → 150.70
  Vigezo vya kuamua:
    - ATR ya H1 bado ni kubwa (momentum ipo)
    - Model 1 confidence ya UP imeongezeka (e.g. 0.78 → 0.85)
    - Hakuna resistance kubwa kabla ya level mpya
```

**Tahadhari:** R5 inatumika mara chache — sio kawaida. Inafanya kazi tu kama
vigezo VYOTE vinatimia, sio moja tu.

---

### R6 — Regime Exit (Kutoka kwa Dharura)

**Wakati:** Model 1 inabadilisha regime **kinyume na trade yako**
**Hatua:** Funga trade **mara moja** — sio kusubiri SL au TP

```
Trade: GBPUSD BUY (regime ilikuwa UP)
Bei sasa: +0.8R (karibu na breakeven lakini haijafika)

Model 1 report → regime: UP → DOWN (confidence: 0.74)

  Uamuzi wa R6: funga mara moja kwa bei ya sasa
  Hasara/faida: chochote bei ipo sasa

Mantiki: edge ya signal ilifuata UP regime. Regime imekwisha —
         edge imekwisha pia. Kuendelea kushikilia ni kucheza bila
         msingi.
```

**Vigezo vya R6 (sio kila mabadiliko ya model):**
```yaml
regime_exit_confidence_threshold: 0.65   # model lazima iwe na uhakika wa kutosha
regime_exit_min_change: true              # lazima regime iwe kinyume — UP→DOWN sio UP→RANGE
```

*Mabadiliko ya UP → RANGE hayafungi trade mara moja (R4 inashughulikia hilo).
Mabadiliko ya UP → DOWN ndiyo yanayofungua R6.*

---

### R7 — Time-Stop (Muda Umekwisha)

**Wakati:** Trade imekaa zaidi ya `predicted_duration` bila kufika TP
**Hatua:** Funga trade — haijalishi bei ipo wapi

```
Signal ya Model 2:
  predicted_duration: 14 bars za 15m  (= saa 3.5)
  tp_probability: 0.71

Trade inafunguliwa 09:00
  R7 time-stop → 12:30 (09:00 + 14 bars × 15m)

12:30 — bei bado iko +0.6R, haijafika TP:
  → Funga. Sababu: R7 Time-Stop.
  Hasara ndogo au faida ndogo — lakini edge imekwisha.
```

**Kwa nini?** Data inaonyesha: trade zinazochukua muda mrefu kuliko wastani
wa trades zinazoshinda — zinashindwa zaidi ya 70% ya wakati. Kushikilia zaidi
ya wakati uliohesabiwa hakusaidii — kunaongeza hatari tu.

```yaml
# ftmo_config.yaml
time_stop_multiplier: 1.2   # R7 = predicted_duration × 1.2 (buffer ndogo)
                             # mfano: pred=14 bars → R7 igonga bar 17
```

---

### Mfumo wa Maamuzi (Kila Bar — 15m)

```
Kila bar mpya inafunguliwa:
         │
    ┌────▼──────────────────────────────┐
    │  Je, bei imefika TP?              │──▶ NDIYO → Funga kwa TP (Faida kamili)
    └────┬──────────────────────────────┘
         │ HAPANA
    ┌────▼──────────────────────────────┐
    │  Je, bei imefika SL?              │──▶ NDIYO → Funga kwa SL (Hasara)
    └────┬──────────────────────────────┘
         │ HAPANA
    ┌────▼──────────────────────────────┐
    │  R6: Je, regime imebadilika       │
    │      kinyume na trade?            │──▶ NDIYO → Funga mara moja (R6)
    └────┬──────────────────────────────┘
         │ HAPANA
    ┌────▼──────────────────────────────┐
    │  R7: Je, muda umepita?            │──▶ NDIYO → Funga mara moja (R7)
    └────┬──────────────────────────────┘
         │ HAPANA
    ┌────▼──────────────────────────────┐
    │  R1/R2: Je, bei = +1R kwanza?    │──▶ NDIYO → Sogeza SL + Funga 50%
    └────┬──────────────────────────────┘
         │ HAPANA (au imeshafanyika)
    ┌────▼──────────────────────────────┐
    │  R3: Je, bei ≥ +2R na trailing?  │──▶ NDIYO → Sasisha trailing SL
    └────┬──────────────────────────────┘
         │ HAPANA
    ┌────▼──────────────────────────────┐
    │  R4/R5: Je, regime/momentum       │──▶ NDIYO → Rekebisha TP
    │         imebadilika?              │
    └────┬──────────────────────────────┘
         │ HAPANA
         ▼
    Subiri bar inayofuata
```

---

### Jedwali la Muhtasari

| Sheria | Wakati | Hatua | Matokeo |
|--------|--------|-------|---------|
| R1 | Bei = +1R | SL → entry | Hakuna hasara tena |
| R2 | Bei = +1R | Funga 50% | Faida halisi inaingia |
| R3 | Bei ≥ +2R | Trailing SL | Faida inafuatwa |
| R4 | Regime → weaker | TP inapungua | Chukua faida ndogo salama |
| R5 | Momentum kali | TP inaongezeka | Faida kubwa zaidi |
| R6 | Regime → kinyume | Funga mara moja | Epuka hasara kubwa |
| R7 | Muda umepita | Funga mara moja | Epuka trade "iliyokufa" |

---

## SEHEMU 7 — Uthibitishaji wa Mfumo (Magereti)

*Jinsi tunavyothibitisha kuwa signal ina edge halisi kabla ya kuitumia.*

Kila signal lazima ipite magereti haya kwa mfuatano. Ikianguka geti lolote,
hairuhusiwi kuendelea.

```
   SIGNAL
     │
     ▼  PHASE A (Gate)      PF ≥ 1.10, trades ≥ 50, miaka 60%+ yenye faida.
     │                       → Je, ina sura ya edge?
     ▼  PHASE B (Permutation) Linganisha na entry za nasibu 10,000. p-value ≤ 0.05?
     │                       → Je, edge ni halisi au ni bahati?
     ▼  OOS (Walk-Forward)   Fundisha 2016–2022, pima 2023–2024 (data isiyoonekana).
     │                       → Je, edge inadumu nje ya sample?
     ▼  MONTE CARLO (FTMO)   Simulations 10,000 za changamoto. Pass Rate ≥ 60%?
     │                       → Je, tutapita FTMO kweli?
     ▼
   TAYARI KWA EXECUTION
```

- **Phase A** inaondoa signals zisizo na sura ya faida.
- **Phase B** inaondoa zile zinazoonekana nzuri kwa bahati tu.
- **OOS** inaondoa zile zilizo-"overfit" kwa historia moja.
- **Monte Carlo** inajibu swali halisi: *Je, tutapita FTMO?*

---

## SEHEMU 8 — Changamoto ya FTMO (Case Study: $10,000)

*Sheria tunazolenga kupita. Tunatumia akaunti ya $10,000 kama mfano wa kufundishia.*

### Phase 1 — Challenge
| Sheria | Maana (kwa $10,000) |
|--------|---------------------|
| Faida lengo: +10% | Fikia $11,000 |
| Hasara ya siku: max 5% | Usipoteze zaidi ya $500 kwa siku MOJA |
| Hasara jumla: max 10% | Usishuke chini ya $9,000 KAMWE |
| Siku za biashara: min 4 | Fanya angalau trade 1 kwenye siku 4 tofauti |
| Muda | Hakuna kikomo cha muda |
| Leverage | 1:100 (Forex) |

### Phase 2 — Verification
| Sheria | Maana (kwa $10,000) |
|--------|---------------------|
| Faida lengo: +5% | Fikia $10,500 |
| Hasara ya siku: max 5% | Sawa na Phase 1 ($500/siku) |
| Hasara jumla: max 10% | Sawa na Phase 1 (si chini ya $9,000) |
| Siku za biashara: min 4 | Sawa na Phase 1 |

### Baada ya Kupita — Funded Account
- **Mgawanyo wa faida:** 80% trader, 20% FTMO (default).
- **Scaling:** baada ya miezi 4 ya faida, akaunti inaweza kuongezwa.
- **Malipo:** kila mwezi au kwa ombi.

### Sheria za Jumla
- **Daily Loss** inahesabiwa kutoka **high-water mark ya siku**, sio balance ya
  usiku. *(Mfano: ukianza siku na $10,200, kikomo chako ni $9,700 — yaani $500
  chini ya peak ya siku hiyo.)*
- **Total DD** inahesabiwa kutoka high-water mark ya akaunti yote.
- Ukivunja kikomo chochote, akaunti **inazuiwa mara moja**.

---

## SEHEMU 9 — Majukumu

| Nani | Jukumu |
|------|--------|
| **Japhet (Owner)** | Maamuzi ya mwisho, kuweka values za FTMO config kwa mkono |
| **Claude Code** | Architect + Implementer: muundo, code, tests, kuripoti. Anamiliki MFUMO.md |
| **Wataalamu washauri** | Ushauri wa nje pale tunapohitaji |

---

*Mwisho wa document. Ukiona eneo limesahaulika au halieleweki, niambie.*
