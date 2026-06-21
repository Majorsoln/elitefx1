# EliteFX — Mwongozo wa Kucheza kwa Mkono (Lot Sizing + Trade Management)

> Doc hii ndiyo **chanzo pekee** cha mfumo sasa: jinsi ya kupata **lot size**
> kupitia **bajeti ya hatari ya siku**, jinsi ya **kuingiza trade kwa mkono**, na
> jinsi ya **kusimamia trade** (R1–R7) — kama tulivyokubaliana. Values zote
> ziko `config/ftmo_config.yaml` (Japhet anabadilisha; sisi tunasoma tu).
>
> **Kanuni ya chuma:** hatubadilishi value yoyote (win_factor, loss_factor,
> max_per_trade, …) bila kupima athari kwanza.

---

## 0 — Values za sasa (`config/ftmo_config.yaml`, akaunti $10,000)

| Kipengele | Value | Maana |
|-----------|-------|-------|
| `account_size` | 10000 | Ukubwa wa akaunti |
| `daily_budget_start` | 400 | Bajeti ya hatari ya mwanzo wa siku (4% ya akaunti) |
| `win_factor` | 0.50 | Bajeti inakua kwa 50% ya faida halisi |
| `loss_factor` | 1.00 | Bajeti inapungua kwa 100% ya hasara halisi |
| `max_per_trade` | 120 | Kikomo cha juu cha hatari kwa trade moja ($) |
| `max_slots` | 4 | Trades nyingi zaidi wazi kwa wakati mmoja |
| `max_correlated_slots` | 2 | Trades nyingi zaidi kwenye group moja ya correlation |
| `max_daily_loss` | 500 | FTMO: 5% ya akaunti (kikomo cha siku) |
| `max_total_dd` | 1000 | FTMO: 10% ya akaunti (kikomo cha jumla) |

---

## 1 — Lot Size kupitia Bajeti ya Siku (DailyRiskBudgetSizer kwa mkono)

### Wazo

Badala ya "hatarisha 1% kila trade", **bajeti ya hatari ya siku** ndiyo
inayoamua kiasi. Ukipoteza, bajeti inashuka mara moja → lot inayofuata inakuwa
ndogo yenyewe → unajilinda usigonge **−5% ya siku**. Ukishinda, bajeti inakua
kidogo → unaweza kuchukua nafasi zaidi bila kupita kikomo.

### HATUA 1 — Bajeti ya siku (sasisha baada ya KILA trade iliyofungwa)

```
bajeti = daily_budget_start
         + (win_factor  × jumla_ya_faida_za_leo)
         − (loss_factor × jumla_ya_hasara_za_leo)

  → mwanzo wa siku: bajeti = 400
  → kila trade ikifungwa, hesabu upya kwa faida/hasara halisi
  → bajeti haiwezi kushuka chini ya 0
```

### HATUA 2 — Bajeti kwa trade moja

```
bajeti_kwa_trade = min(
    bajeti_iliyobaki ÷ slots_zilizobaki,   # gawanya sawa kwa nafasi zilizobaki
    max_per_trade                           # kikomo cha juu ($120)
)
```
`slots_zilizobaki = max_slots − trades_zilizo_wazi_sasa`.

### HATUA 3 — Lot size kutoka SL

```
lot = bajeti_kwa_trade ÷ (sl_pips × thamani_ya_pip_kwa_lot_1)
```

**Thamani ya pip kwa lot 1.00** (kawaida):
| Aina ya pair | Mfano | Pip 1, lot 1.00 |
|--------------|-------|------------------|
| Quote = USD | EURUSD, GBPUSD, AUDUSD, NZDUSD | ≈ **$10** |
| Quote = JPY | USDJPY, EURJPY | ≈ **$6.7** (inategemea bei; ~1000÷bei) |
| Quote nyingine | USDCAD, USDCHF, EURGBP | hesabu: $10 ÷ bei_ya_quote→USD |

> Kwa usahihi, soma **pip value** moja kwa moja kwenye MT5 (au calculator ya
> broker) kwa pair na lot husika — ndiyo chanzo cha uhakika.

### HATUA 4 — Sawazisha + ukomo

- Piga chini kwa **lot step ya broker** (kawaida 0.01).
- Lot ikitoka **chini ya minimum** (0.01) → **acha trade** (sio salama/haifai).

### Mfano halisi (siku moja, $10,000)

```
daily_budget_start = 400 | win_factor = 0.50 | loss_factor = 1.00
max_slots = 4 | max_per_trade = 120

09:00  Trade 1 — EURUSD, SL = 20 pip
  bajeti = 400 ;  slots zilizobaki = 4
  bajeti_kwa_trade = min(400÷4, 120) = 100
  lot = 100 ÷ (20 × 10) = 0.50 lots          ✓ funguliwa

10:30  Trade 1 inapoteza −$80
  bajeti = 400 − (1.00 × 80) = 320

11:00  Trade 2 — USDJPY, SL = 25 pip (pip≈$6.7)
  slots zilizobaki = 3
  bajeti_kwa_trade = min(320÷3, 120) = 106
  lot = 106 ÷ (25 × 6.7) ≈ 0.63 lots

13:00  Trade 2 inashinda +$180
  bajeti = 320 + (0.50 × 180) = 410

15:00  Trade 3 — GBPUSD, SL = 30 pip
  slots zilizobaki = 2
  bajeti_kwa_trade = min(410÷2, 120) = 120
  lot = 120 ÷ (30 × 10) = 0.40 lots
```

> Angalia: bajeti inashuka ukipoteza, inakua ukishinda — **lot inajirekebisha
> yenyewe**. Hii ndiyo inayozuia kugonga −5% kwa mfululizo wa hasara.

---

## 2 — Kuingiza Trade kwa Mkono (Pre-Trade Checklist)

Kabla ya kufungua trade yoyote (MT5), pitia hatua hizi **kwa mfuatano**. Ikishindwa
hatua yoyote → **usifungue**.

### Andika signal yako (manual input)
```
Pair:        ________   Mwelekeo: BUY / SELL
Entry:       ________
SL:          ________   →  sl_pips = |entry − SL| kwa pip
TP:          ________   →  R = |TP − entry| ÷ |entry − SL|
```

### Compliance kwa mkono (lazima zote zipite)

```
CHECK 1 — Daily Loss Guard
  worst_case = sl_pips × pip_value × lot   (hasara kama SL igongwe)
  hasara_ya_siku_sasa + worst_case  ≥  max_daily_loss (500)?
     NDIYO → KATAA (Daily Loss)

CHECK 2 — Total DD Guard
  drawdown_jumla + worst_case  ≥  max_total_dd (1000)?
     NDIYO → KATAA (Total DD)

CHECK 3 — Slot Capacity
  trades_wazi  ≥  max_slots (4)?
     NDIYO → KATAA (Slots zimejaa)

CHECK 4 — Correlation Guard
  trades_wazi kwenye group ya pair hii  ≥  max_correlated_slots (2)?
     NDIYO → KATAA (Correlation limit)

CHECK 5 — Spread Guard
  spread_ya_sasa  >  max_spread ya pair?
     NDIYO → KATAA (Spread kubwa — subiri)

Zote PASS → hesabu lot (Sehemu 1) → fungua trade.
```

### Correlation groups (rejea ya Check 4)
```
USD_group:     EURUSD, GBPUSD, AUDUSD, NZDUSD     (USD weakness plays)
USD_strength:  USDJPY, USDCAD, USDCHF             (USD strength plays)
EUR_group:     EURUSD, EURJPY, EURGBP
AUD_NZD_group: AUDUSD, NZDUSD
```
*Mfano (limit = 2): EURUSD BUY + GBPUSD BUY = 2/2 USD_group → AUDUSD BUY **KATAA**.
Lakini USDJPY BUY = group tofauti → **RUHUSA**.*

> **Worst-case daima:** Check 1/2 zihesabu kana kwamba SL **zote zilizo wazi**
> zinagongwa pamoja. Hii inakulinda dhidi ya dhoruba ya soko.

---

## 3 — Trade Management (R1–R7)

> Tunatumia sheria kwa **mfuatano wa hali**, sio zote kwa wakati mmoja. Kila bar
> mpya, pitia mtiririko hapa chini.

| Sheria | Wakati | Hatua | Lengo |
|--------|--------|-------|-------|
| **R1** Breakeven | Bei = **+1R** | Sogeza SL → entry (± spread) | Haiwezi kupoteza tena |
| **R2** Partial | Bei = **+1R** | Funga **50%** ya position | Faida halisi inaingia |
| **R3** Trailing | Bei ≥ **+2R** | SL inafuata bei (fixed-pip au ATR) | Faida inafuatwa |
| **R4** Reduce TP | Regime → dhaifu (UP→RANGE) | Punguza TP hadi level ya karibu | Chukua faida ndogo salama |
| **R5** Extend TP | Momentum kali sana | Ongeza TP hadi level inayofuata | Faida kubwa zaidi (nadra) |
| **R6** Regime Exit | Regime → **kinyume** (UP→DOWN) | Funga **mara moja** | Epuka hasara kubwa |
| **R7** Time-Stop | Muda umepita (`predicted × 1.2`) | Funga mara moja | Epuka trade "iliyokufa" |

### Maelezo

- **R1 Breakeven** — bei ikifika +1R, SL → entry. Trade inabadilika kutoka
  "inaweza kupoteza" → "haiwezi kupoteza". Hii inalinda pass-rate ya FTMO.
- **R2 Partial (50%)** — wakati huo huo na R1: funga nusu, acha nusu iendelee.
  Hata nusu ikirudi entry, umeshinda faida ya nusu.
- **R3 Trailing** — anza baada ya **+2R** (`trailing_start_r = 2.0`):
  - *fixed_pip:* SL inafuata kwa `trail_distance_pip = 15`. Bei ikishuka, SL haishuki.
  - *atr:* SL = bei_ya_juu − (ATR_14 × `trail_atr_mult = 1.5`).
- **R4 Reduce TP** — regime ikidhoofika (UP→RANGE), sogeza TP karibu. Soko
  halitafika TP ya mbali kwenye RANGE.
- **R5 Extend TP** — **nadra**. Tu kama vigezo **vyote** vipo: ATR bado kubwa,
  confidence ya regime imeongezeka, hakuna resistance kabla ya level mpya.
- **R6 Regime Exit** — regime ikigeuka **kinyume kabisa** (UP→DOWN) na ina uhakika
  (`regime_exit_confidence_threshold = 0.65`, `regime_exit_min_change = true`):
  funga mara moja. UP→RANGE **haifungui R6** (hiyo ni R4).
- **R7 Time-Stop** — `R7 = predicted_duration × time_stop_multiplier (1.2)`. Trade
  ikikaa zaidi ya muda uliotabiriwa bila kufika TP → funga; edge imekwisha.

### Mtiririko kila bar
```
Bei = TP?  → funga (faida kamili)
Bei = SL?  → funga (hasara)
R6: regime kinyume?      → funga mara moja
R7: muda umepita?        → funga mara moja
R1/R2: bei = +1R (mara ya kwanza)? → SL→entry + funga 50%
R3: bei ≥ +2R?           → sasisha trailing SL
R4/R5: regime/momentum imebadilika? → rekebisha TP
vinginevyo               → subiri bar inayofuata
```

---

## 4 — Kikomo cha FTMO (rejea, akaunti $10,000)

| Sheria | Maana |
|--------|-------|
| Faida lengo: **+10%** | Fikia $11,000 |
| Hasara ya siku: **max 5%** | Usipoteze zaidi ya $500 kwa siku MOJA |
| Hasara jumla: **max 10%** | Usishuke chini ya $9,000 KAMWE |
| Siku za biashara | Fanya angalau trade siku 4 tofauti (kama inahitajika) |
| Daily Loss | Inahesabiwa kutoka **high-water mark ya siku** |
| Total DD | Inahesabiwa kutoka high-water mark ya akaunti |

> Ukivunja kikomo chochote, akaunti **inazuiwa mara moja**. Ndiyo maana
> DailyRiskBudgetSizer + Compliance checks ni za lazima kabla ya kila trade.

---

*Mwisho. Lot sizing (bajeti ya siku) + manual input (pre-trade checklist) +
trade management (R1–R7) — kama tulivyokubaliana. Values: `config/ftmo_config.yaml`.*
