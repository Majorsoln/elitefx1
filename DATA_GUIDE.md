# DATA_GUIDE — EliteFX SEHEMU 1

Mwongozo wa **jinsi ya KUPATA data, KUITUMIA, na KUITAFSIRI** kwa kila eneo la
mfumo. Hii ni daraja kati ya data safi (SEHEMU 1) na watumiaji wake (Model 1,
Model 2, Sizing, Compliance, Trade Mgmt). Imejengwa kutoka matokeo halisi ya
`quality.py` na `eda.py`.

> **Kanuni ya dhahabu:** Pata data **DAIMA kupitia `src/data/dataset.py`** — ndipo
> kanuni za usalama (no-lookahead, no-trade window, liquidity) zinatekelezwa mahali
> pamoja. Usisome Parquet moja kwa moja kwenye code ya model.

---

## A. JINSI YA KUPATA DATA (misingi)

**Mahali:** `data/processed/candles/symbol={PAIR}/tf={TF}.parquet`
**Pairs (9):** EURUSD GBPUSD USDJPY EURJPY USDCAD USDCHF AUDUSD NZDUSD EURGBP
**TF (8):** `1m 5m 15m 30m H1 H2 H4 D1`
**Muda:** 2016-01-04 → 2026-04-30 (UTC). Train **2016–2024**, OOS **2025–2026-04**.

```python
import sys; sys.path.insert(0, "src")
from data.dataset import (load_candles, train_oos_split,
                          shift_for_decision, add_returns, pip_size)

# Pata candles (chujwa kadri unavyohitaji)
df = load_candles("EURUSD", "H1",
                  start="2016-01-01", end="2024-12-31",
                  drop_no_trade=True,        # ondoa rollover (23:00 CET)
                  min_tick_count=4)          # liquidity filter (hiari)

train, oos = train_oos_split(df)             # 2016–2024 vs 2025+
```

### Kanuni 4 za usalama (zinatekelezwa na dataset.py)
1. **NO-LOOKAHEAD** — bar ina label ya `bar_open` (muda wa **kufunguka**). Bar yenye
   `bar_open=T` inajulikana tu baada ya `T + interval`. Kwa uamuzi wa wakati halisi,
   tumia `shift_for_decision(df, by=1)` ili row ya T iwe na bar **iliyofungwa** kabla
   ya T. **Kamwe usitumie bar inayoendelea kuunda.**
2. **NO-TRADE WINDOW** — `drop_no_trade=True` huondoa rollover (23:00 CET, DST-aware
   → 21:00/22:00 UTC). Spread hupanda mara 3+ hapo.
3. **LIQUIDITY** — `min_tick_count=N` huondoa bars zenye ticks chache (kelele). Muhimu
   kwa 1m/5m (entry); si lazima kwa H1+.
4. **UTC** — `bar_open` zote ni UTC. Kwa session/rollover, badilisha → `Europe/Berlin`.

---

## B. KAMUSI YA DATA (maana ya kila column)

| Column | Maana | Tafsiri / matumizi |
|--------|-------|--------------------|
| `bar_open` | Muda wa kufunguka (UTC, naive) | Label ya bar; no-lookahead rejea |
| `open/high/low/close` | OHLC kutoka **bid** | Bei; R-multiples, structure, S/R |
| `tick_count` | Idadi ya ticks kwenye bar | Liquidity proxy; ndogo = kelele/epuka |
| `volume` | `bid_volume + ask_volume` | Activity; trend/breakout confirmation |
| `bid_volume`,`ask_volume` | Jumla kila upande | Order-flow components |
| `volume_imbalance` | `(ask−bid)/(ask+bid)` ∈[−1,1] | +ve = shinikizo la kununua; −ve = kuuza |
| `spread_mean`,`spread_max` | Spread (bei) ndani ya bar | Cost ya backtest |
| `spread_mean_pips`,`spread_max_pips` | Spread kwa **pips** | Linganisha na `max_spread_pips`/pair |

> **Note:** OHLC zinajengwa kutoka **bid** (config `resample.price_for_ohlc`). Spread
> imehifadhiwa kando — usiichanganye na bei. Pip: JPY=0.01, nyingine=0.0001 (`pip_size()`).

---

## C. MATUMIZI KWA KILA ENEO

### SEHEMU 2 — Model 1: Regime Classifier
- **PATA:** `D1, H4, H2, H1` (HTF). `drop_no_trade` si lazima (HTF). Tumia `train_oos_split`.
- **TUMIA:** jenga features (EMA slope, ADX, bei-dhidi-ya-EMA, returns/vol multi-TF,
  **volume confirmation**). Lazima `shift_for_decision` kabla ya kuunganisha TF
  (kuepuka lookahead kati ya timeframes). Volume kubwa = trend; ndogo = range.
- **TAFSIRI:** vol ya kila pair (jedwali D) inatoa muktadha wa "kawaida vs ya juu".

### SEHEMU 3 — Model 2: Entry Engine
- **PATA:** `1m, 5m, 15m, 30m`. **Weka `min_tick_count`** (kelele ya 1m) na
  `drop_no_trade=True`. Entry halisi 15m/30m; muktadha 1m–30m.
- **TUMIA:** windows za microstructure; `volume_imbalance` kama order-flow feature;
  `spread_mean_pips` kuthibitisha entry ina cost nafuu.
- **TAFSIRI:** `volume_imbalance` wastani ≈ 0, symmetric; p05/p95 ≈ ±0.22…±0.41 (jedwali D).
  Thamani nje ya hapo = shinikizo kubwa la upande mmoja.

### SEHEMU 4 — Position Sizing
- **PATA:** `pip_size(symbol)`; `spread_mean_pips` kwa pair (cost); `sl_pips` (kutoka signal).
- **TUMIA:** `lotsize = bajeti_kwa_trade / (sl_pips × pip_value)`. Ongeza spread kama cost.
- **TAFSIRI:** JPY pip=0.01; spread za kila pair (jedwali D) huongeza cost halisi ya entry.

### SEHEMU 5 — Compliance
- **PATA:** spread ya **LIVE** (FTMO) kwa spread-guard; `max_spread_pips` (backtest) kwa
  simulation; `no_trade_window`; correlation matrix (ripoti ya EDA).
- **TUMIA:** spread-guard (kataa spread > kizingiti); correlation-guard.
- **TAFSIRI (muhimu):** `max_spread_pips` ya config ni ya **backtest (Dukascopy)** —
  LIVE ni ya FTMO (pana). 🔴 Correlation halisi inaonyesha **EUR_group ni dhaifu**
  na **USD_group vs USD_strength zina uhusiano hasi mkali** (EURUSD vs USDCHF=−0.77):
  kupanga kwa "sarafu iliyopo" hakukamati net-USD exposure. **Itafanyiwa kazi Sehemu 5.**

### SEHEMU 6 — Trade Management (R1–R7)
- **PATA:** candles za TF ya usimamizi (15m); kokotoa **ATR** kutoka high/low/close.
- **TUMIA:** R3 trailing (ATR×mult); R7 time-stop (`predicted_duration` kwa bars za 15m).
- **TAFSIRI:** R-multiples kutoka `sl`; ATR hubadilika kwa pair/vol (jedwali D).

---

## D. REJEA YA TAFSIRI (namba za EDA)

**Spread (pips) kwa pair** — median (p50) na p95 (1m):

| Pair | p50 | p95 | max_spread (backtest) |
|------|-----|-----|------------------------|
| EURUSD | 0.30 | 0.65 | 1.5 |
| USDJPY | 0.39 | 1.04 | 2.0 |
| EURJPY | 0.72 | 1.81 | 3.0 |
| EURGBP | 0.87 | 1.91 | 3.0 |
| GBPUSD | 0.88 | 1.89 | 3.0 |
| USDCHF | 0.99 | 1.96 | 3.0 |
| AUDUSD | 0.98 | 1.55 | 2.5 |
| NZDUSD | 1.06 | 1.84 | 3.0 |
| USDCAD | 1.15 | 2.08 | 3.5 |

**Volatility (D1, annualized %):** USDCAD 6.81 (chini) · EURGBP 7.11 · EURUSD 7.27 ·
USDCHF 7.45 · EURJPY 8.67 · USDJPY 9.11 · GBPUSD 9.15 · AUDUSD 9.96 · NZDUSD 10.13 (juu).

**Correlation (D1 returns) — muhtasari:** AUDUSD–NZDUSD **+0.85** (kali); USD_group zote
+0.59…0.85; EURUSD–USDCHF **−0.77** (inverse); EUR_group dhaifu (EURJPY–EURGBP +0.06).

**Rollover (no-trade):** 23:00 CET (= 21:00/22:00 UTC kwa DST). Spread avg 2.3–2.9 pips hapo.

**Gaps:** zote ni sikukuu (Christmas Dec 25, New Year). Si data mbovu.

---

## E. KANUNI ZA DHAHABU (fanya / usifanye)

✅ Pata data kupitia `dataset.py` daima.
✅ Tumia `shift_for_decision` kwa features za uamuzi (no-lookahead).
✅ Train kwenye 2016–2024; pima kwenye OOS 2025+ (usichanganye).
✅ Chuja rollover (`drop_no_trade`) na liquidity (`min_tick_count`) kwa entry (1m–30m).
❌ Usitumie bar inayoendelea kuunda kwenye uamuzi wa wakati halisi.
❌ Usichanganye spread ya backtest (Dukascopy) na ya LIVE (FTMO).
❌ Usisome Parquet moja kwa moja kwenye code ya model — pitia dataset.py.
