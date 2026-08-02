# ELITEFX — MUUNDO WA MFUMO V3: IDARA NNE (directive ya PD 2026-08-02)

> PD: mfumo una pande nne — **RISK MANAGEMENT · COST MANAGEMENT · STRATEGY MODELS · OPEN-POSITION
> MANAGEMENT**. Models ni IDARA MOJA tu; zinapita kwenye idara nyingine. Hii inachukua nafasi ya
> mtazamo wa "lango moja la risk" (uelewa wangu wa awali ulikuwa mwembamba).

```
                    ┌──────────────────────────────────────────────┐
   bar mpya ───────►│ 3. STRATEGY MODELS  (KAIROS-1..N)            │
                    │    entries · exits · hali ya soko            │
                    └───────────────┬──────────────────────────────┘
                                    │ pendekezo (entry, SL, TP)
                    ┌───────────────▼──────────────────────────────┐
                    │ 2. COST MANAGEMENT                           │
                    │    je trade inaweza kubeba gharama?          │
                    │    lots zinarekebishwa kwa gharama            │
                    └───────────────┬──────────────────────────────┘
                                    │ trade yenye gharama ndani
                    ┌───────────────▼──────────────────────────────┐
                    │ 1. RISK MANAGEMENT                           │
                    │    bajeti ya siku · risk/trade · slots ·      │
                    │    correlation · news on/off                 │
                    └───────────────┬──────────────────────────────┘
                                    │ ruhusa (au REJECT + sababu)
                    ┌───────────────▼──────────────────────────────┐
                    │ EA-CONDUIT → position ipo wazi                │
                    └───────────────┬──────────────────────────────┘
                    ┌───────────────▼──────────────────────────────┐
                    │ 4. OPEN-POSITION MANAGEMENT                   │
                    │    fuatilia · lock-profit · exit mapema ·     │
                    │    session change · news zinazokuja          │
                    └──────────────────────────────────────────────┘
```

## IDARA 1 — RISK MANAGEMENT
**Kazi:** kuhakikisha kila entry inaingia ndani ya kiwango cha risk kilichopangwa.
- **Bajeti ya siku** → **risk per trade** (bajeti ÷ slots zilizobaki, cap = max_per_trade).
- **Ndani ya siku:** +50% ya faida ya siku · −100% ya hasara ya siku (ipo tayari, `_budget`).
- **Kati ya siku (MPYA — PD):** siku iliyopita ikifunga kwa hasara, siku inayofuata inabeba
  **adhabu** ya sehemu ya hasara hiyo (§CARRY hapa chini).
- **Malango:** max_slots · max_correlated_slots · daily_loss · total_dd · max_spread.
- **NEWS TOGGLE:** swichi ya `trade_news: on|off` (config, bila code) — ikizimwa, entries
  zinazokaribia news kubwa zinakataliwa (§4 inatoa data ya news).
- **Toleo la REJECT + SABABU** (ipo tayari) → dashboard.

## IDARA 2 — COST MANAGEMENT
**Kazi:** kabla ya kufungua, thibitisha trade inaweza **kubeba gharama** na bado kutoa faida ndani ya
risk iliyotengwa; kisha **rekebisha lots** kwa gharama.
- **Cost-inclusive sizing** (§SIZING hapa chini) — gharama inaingia kwenye denominator, si kutolewa
  baadaye.
- **Runtime cost-guard:** kutumia **ratio iliyothibitishwa na Idara 3** kwa strategy hii; gharama ya
  SASA (spread ya bar hii + commission + swap) ikishusha ratio chini ya kizingiti, trade
  **HAIFUNGULIWI**. Idara 2 **INATEKELEZA** namba; **HAIZIGUNDUI** (uchambuzi = Idara 3, §UBORA).
- **Actual-vs-assumed tracking:** gharama halisi (fills za EA) dhidi ya iliyodhaniwa → onyo dhana
  zikivunjika.
- Vipengele vya gharama: spread (bar ya entry) + slippage + commission/lot + swap × usiku
  unaotarajiwa (HTF).

## IDARA 3 — STRATEGY MODELS
**Kazi:** chumba cha uchambuzi — entries, exits, hali ya soko. KAIROS-1..N (`config/models.yaml`).
- Utafiti unaendelea hapa (ML + indicators + hali ya soko = "lessons").
- **Vipimo vya model** (scorecard): pips zilizovunwa · **max-DD** · **muda wa trade** · win% ·
  EV/trade · gross/cost. (Steward inafuatilia; DD + time-in-trade zinaongezwa.)

### §UBORA — mfumo wa kupima ubora na ku-OPTIMIZE (PD 2026-08-02: uchambuzi huu ni wa IDARA 3)
Vipimo vitatu, kila kimoja kinajibu swali TOFAUTI. Vyote vinatoka kwenye utafiti (backtest), na
matokeo yake (namba zilizothibitishwa) ndiyo yanayotumiwa na Idara 1/2 wakati wa kutrade.

| Kipimo | Swali | Hesabu | Hulinda |
|---|---|---|---|
| **EV net** | kila trade inaniachia nini? | wastani wa `pnl` (gharama tayari imetolewa) | matokeo |
| **GROSS** | move yenyewe ni kubwa kiasi gani? | `EV net + cost` (aljebra, si kadirio) | — |
| **GROSS ÷ COST** | gharama ikipanda, nitasurvive? | ratio; kizingiti **≥ 3×** | **usalama** |

**Mfano (trades 100, TP+10 / SL−20 / win 72%, cost 0.6):**
```
GROSS = 72(+10) + 28(−20) = +160 pips  →  1.6 pips/trade
COST  = 100 × 0.6         = 60 pips
NET   = 160 − 60          = +100 pips  →  1.0 pip/trade
RATIO = 1.6 ÷ 0.6         = 2.7×
```
Ratio 2.7 = **gharama inaweza kupanda mara 2.7 kabla strategy haijafa**:
| cost | net jumla | hali |
|---|---|---|
| 0.6 | +100 | ✅ |
| 1.2 (×2) | +40 | ⚠️ 60% imeliwa |
| 1.8 (×3) | −20 | ❌ imekufa |

**Kwa nini GROSS si NET kwenye ratio:** gross **haibadiliki** broker akibadilika (ni sifa ya soko);
commission inaongeza cost pekee. Kutumia net/cost = kukata gharama mara mbili.

**Kwa nini ratio inahitajika ingawa gharama ipo kwenye sizing:** sizing ni **uhasibu wa trade moja**
(hasara isivuke risk); ratio ni **kinga ya mfumo**. Strategy mbili zenye sizing sahihi ile ile:
A (gross 3.0, ratio 5.0×) na B (gross 0.8, ratio 1.3×) — zote chanya leo; spread ikipanda 0.4 pips,
A inabaki +2.0, **B inageuka −0.2**. Sizing haikuokoa B; ratio ingeonya mapema.
*Rejea halisi: KAIROS-3 (ML) ilikuwa na gross CHANYA na sizing ingekuwa sahihi — ilikufa kwa ratio
0.3–0.7× (LESSON-045/039).*

**Matumizi ya OPTIMIZE:** ratio ndiyo dira ya kuboresha — TF ipi (H1 2.5× → H4 8.2× → D1 8.7×),
exit-geometry ipi, pairs zipi, broker gani anavumilika (`qualify_broker`/`max_commission`).
- Model HAIAMUI risk wala gharama — inapendekeza tu. Idara 1 na 2 ndizo zinazoamua.

## IDARA 4 — OPEN-POSITION MANAGEMENT
**Kazi:** ufuatiliaji wa karibu wa kila position iliyo wazi.
- **Vitendo:** exit mapema · lock-profit (SL → breakeven/trailing) · punguza ukubwa · shikilia.
- **Vichocheo:** hali ya soko inabadilika · **mabadiliko ya session** (liquidity) · **news
  zinazokuja** · muda umepita bila mwelekeo.
- **Hapa ndipo RL inapokaa** (Mzunguko-4 §2): action-space ndogo, simulator wetu ni honest,
  na kila trade ina exit — kazi ya kutosha.
- Nidhamu: vitendo vyake vinarekodiwa kama decisions (audit) — dashboard inaonyesha "kwa nini
  ilifungwa mapema".

---

## §CARRY — pendekezo la Chief (bajeti kati ya siku)
PD alipendekeza: siku iliyopita ikifunga hasara → siku inayofuata inabeba **50%** ya hasara hiyo.
Kanuni ni sahihi (anti-martingale — punguza risk baada ya hasara). Hatari mbili za utekelezaji:
**(i) mrundikano usio na mwisho** (hasara 5 mfululizo → bajeti 0 milele); **(ii) kutopona**
(hakuna njia ya kurudi juu). Napendekeza **penalty inayoyeyuka + sakafu + dari + nanga ya equity**:

```
penalty_today = decay × penalty_jana + carry × hasara_ya_jana        # decay=0.5, carry=0.5
base          = equity_pct × equity_ya_sasa                          # nanga: 4% ya equity HALISI
budget_today  = clip(base − penalty_today, floor × base, cap × base) # floor=0.25, cap=1.5
budget_today  = min(budget_today, max_daily_loss × 0.8)              # FTMO hard-guard
```
- **decay 0.5:** adhabu inayeyuka nusu kila siku → mfumo unajipona wenyewe (hasara ya juzi ina uzito
  1/4, ya juzi-juzi 1/8...). Hakuna mrundikano usio na mwisho.
- **floor 0.25:** bajeti haishuki chini ya robo — bila hii, streak inaua uwezo wa kupona.
- **cap 1.5:** faida haiongezi risk bila kikomo (kinga dhidi ya "ulevi wa faida").
- **nanga ya equity:** bajeti inakua/inapungua na akaunti yenyewe — inashughulikia FTMO scaling na
  akaunti za wateja (§9) bila kubadilisha config.
- **FTMO hard-guard:** bajeti KAMWE haizidi 80% ya max_daily_loss.
Vigezo VYOTE (decay/carry/floor/cap/equity_pct) → `config/ftmo_config.yaml` (PD anabadilisha bila code).

## §SIZING — pendekezo la Chief (cost-inclusive)
PD alipendekeza: risk $100, gharama $20 → tenga $80 kwa SL. **Mantiki ni sahihi** (gharama ni sehemu
ya hasara). Lakini kutoa $20 kwanza si sahihi kihesabu, kwa sababu **gharama nayo inakua na lots**:
```
HASARA HALISI ikiwa SL inagongwa = lots × (sl_pips + cost_pips) × pip_value
```
Kwa hiyo suluhu KAMILI ni kuweka gharama kwenye **denominator**, si kuitoa kwenye numerator:
```
cost_pips = spread + slippage + commission_per_lot/pip_value + swap_pips × usiku_unaotarajiwa
lots      = risk_$ / ((sl_pips + cost_pips) × pip_value)
```
- Inajirekebisha yenyewe: gharama kubwa → lots ndogo, **bila kurudia hesabu**.
- Hasara halisi ya SL inakuwa **HASA** risk_$ iliyotengwa (si zaidi).
- Mfano: risk $100, SL 16 pips, cost 2 pips, pip_value $10 → lots = 100/(18×10) = **0.56**
  (badala ya 0.62 ya sasa). Hasara ikigongwa SL = 0.56 × 18 × 10 = **$100** ✓.
Kisha **viability gate**: `(tp_pips × p_win_estimate) vs cost_pips` — au rahisi na thabiti zaidi:
`gross_edge_pips ≥ 3 × cost_pips` (LESSON-039 ikitekelezwa **kwa kila trade**, si kwenye utafiti tu).

## HALI YA UTEKELEZAJI (ukweli)
| Idara | Ipo | Inahitajika |
|---|---|---|
| 1 RISK | bajeti ndani ya siku · slots · correlation · reject+sababu | **CARRY** kati ya siku · nanga ya equity · floor/cap · **news toggle** |
| 2 COST | gharama kwenye backtest (episodes) | **cost-inclusive sizing** · runtime cost-guard (ratio ya Idara 3) · actual-vs-assumed |
| 3 MODELS | KAIROS-1/2 · models.yaml · Steward · **§UBORA (EV/gross/ratio, `cost_budget`)** | DD + time-in-trade kwenye scorecard · KAIROS-3+ |
| 4 OPEN-POS | SL/TP zisizobadilika (broker-side) | **IDARA NZIMA** — monitor · lock-profit · session · news · RL |
