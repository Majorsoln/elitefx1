# COST BUDGET — gharama ambayo kila strategy inaweza kubeba (broker-agnostic)

*2026-08-01 18:21 | chanzo cha hesabu: `cost_stress` §R5(1) `EV_new = EV − Δ` (gharama inalipwa MARA MOJA kwa trade -> breakeven Δ = EV) | profiles: `config/broker_costs.yaml` (PD anahariri)*

> **Kwa nini faili hii ipo:** mfumo utatumika kwa **brokers tofauti tofauti**, kwa hiyo commission/swap ya broker mmoja HAIWEKWI kwenye research. Badala yake kila strategy ina **bajeti** — na broker yeyote anapimwa dhidi yake kwa sekunde.

> **Muhimu:** namba za EV hapa chini tayari zime-charge **spread halisi + slippage**. Hazija-charge **commission wala swap** — hivyo ndivyo research yetu ilivyo. Jedwali hili linaziba pengo hilo bila kuendesha backtest tena (ni hesabu, si simulation).


## 1. Bajeti (breakeven) na kikomo cha commission

| strategy | hali | EV (pips) | **bajeti** (Δ inayoua) | commission KUBWA inayoruhusiwa (hai) | ...(tradable, edge ≥3× cost) |
|---|---|---|---|---|---|
| KAIROS-1 (STRAT-001) | PROVEN | +1.92 | **1.92 pips** | $19.20/lot | $2.40/lot |
| KAIROS-2 (STRAT-002) | PROVEN | +2.65 | **2.65 pips** | $26.50/lot | $4.83/lot |
| breadth pairs-12 (SL1/TP1) | BASELINE | +0.91 | **0.91 pips** | $9.10/lot | $0.00/lot |
| breadth pairs-9 (SL2/TP1) | BASELINE* | +1.58 | **1.58 pips** | $15.80/lot | $1.27/lot |
| breadth pairs-8 (SL1/TP1) | BASELINE* | +1.78 | **1.78 pips** | $17.80/lot | $1.93/lot |

*Commission ya "hai" = inayoacha EV > 0 (ukingoni). Ya "tradable" = inayotimiza doctrine (charter §4.4: edge ≥ 3× gharama jumla). **Tumia ya pili.***

## 2. Kila strategy chini ya kila profile

| strategy | profile | comm (pips) | swap (pips) | ziada jumla | EV baada | gross/cost | net/cost | hai? | tradable (≥3× gross)? | ≥3.0 pips? |
|---|---|---|---|---|---|---|---|---|---|---|
| KAIROS-1 (STRAT-001) | spread_only | 0.00 | 0.00 | **0.00** | **+1.92** | 4.20× | 3.20× | ✅ | ✅ | ❌ |
| KAIROS-1 (STRAT-001) | raw_typical | 0.70 | 0.25 | **0.95** | **+0.97** | 1.63× | 0.63× | ✅ | ❌ | ❌ |
| KAIROS-1 (STRAT-001) | stress | 1.20 | 0.50 | **1.70** | **+0.22** | 1.10× | 0.10× | ✅ | ❌ | ❌ |
| KAIROS-2 (STRAT-002) | spread_only | 0.00 | 0.00 | **0.00** | **+2.65** | 5.42× | 4.42× | ✅ | ✅ | ❌ |
| KAIROS-2 (STRAT-002) | raw_typical | 0.70 | 0.25 | **0.95** | **+1.70** | 2.10× | 1.10× | ✅ | ❌ | ❌ |
| KAIROS-2 (STRAT-002) | stress | 1.20 | 0.50 | **1.70** | **+0.95** | 1.41× | 0.41× | ✅ | ❌ | ❌ |
| breadth pairs-12 (SL1/TP1) | spread_only | 0.00 | 0.00 | **0.00** | **+0.91** | 2.52× | 1.52× | ✅ | ❌ | ❌ |
| breadth pairs-12 (SL1/TP1) | raw_typical | 0.70 | 0.25 | **0.95** | **-0.04** | 0.97× | -0.03× | ❌ | ❌ | ❌ |
| breadth pairs-12 (SL1/TP1) | stress | 1.20 | 0.50 | **1.70** | **-0.79** | 0.66× | -0.34× | ❌ | ❌ | ❌ |
| breadth pairs-9 (SL2/TP1) | spread_only | 0.00 | 0.00 | **0.00** | **+1.58** | 3.63× | 2.63× | ✅ | ✅ | ❌ |
| breadth pairs-9 (SL2/TP1) | raw_typical | 0.70 | 0.25 | **0.95** | **+0.63** | 1.41× | 0.41× | ✅ | ❌ | ❌ |
| breadth pairs-9 (SL2/TP1) | stress | 1.20 | 0.50 | **1.70** | **-0.12** | 0.95× | -0.05× | ❌ | ❌ | ❌ |
| breadth pairs-8 (SL1/TP1) | spread_only | 0.00 | 0.00 | **0.00** | **+1.78** | 3.97× | 2.97× | ✅ | ✅ | ❌ |
| breadth pairs-8 (SL1/TP1) | raw_typical | 0.70 | 0.25 | **0.95** | **+0.83** | 1.54× | 0.54× | ✅ | ❌ | ❌ |
| breadth pairs-8 (SL1/TP1) | stress | 1.20 | 0.50 | **1.70** | **+0.08** | 1.03× | 0.03× | ✅ | ❌ | ❌ |

## 3. Jinsi ya kupima broker MPYA (dakika moja, bila backtest)

```python
from cost_budget import qualify_broker
qualify_broker(commission_usd_round_turn=7.0, swap_pips_per_night=0.5,
               strategy='KAIROS-1 (STRAT-001)')
```
Au ongeza profile kwenye `config/broker_costs.yaml` na uendeshe upya ripoti hii. **Hakuna code inayohitajika.**

## 4. Jinsi ya kusoma (na tahadhari)

1. **Bajeti = EV.** Strategy yenye EV +1.92 inakufa gharama ya ziada ikifika 1.92 pips/trade. Hakuna sehemu ya kujificha — ni kutoa moja kwa moja.
2. **Kubaki hai ≠ kufaa kutradiwa.** Doctrine (charter §4.4) inataka edge ≥ 3× gharama. Safu ya 'tradable' ndiyo ya kutumia kwa uamuzi wa live.
3. **base_cost_pips** (spread+slip iliyomo tayari) ni **kadirio** kwenye config; inaweza kupimwa HASA kwa data run (spr ipo kwenye state parquet). Uwiano wa edge/cost unategemea namba hiyo — bajeti na 'hai' HAZITEGEMEI.
4. **Swap ya H1** inategemea usiku wa kila trade; `avg_nights_per_trade` ni kadirio (rmap.apply_swap inaweza kuhesabu HASA kwa data run).
5. Breadth 9/8 zimewekwa alama `*`: kanuni ya `pairs[]` ilitumia VALIDATION, kwa hiyo EV yao ni **hot**. Zitendee kama kikomo cha juu, si ahadi.

*Profitable != Tradable Edge. Protect capital first.*