# C2-0 — Intraday states (15m/30m) + HTF context (MZUNGUKO-2)

*2026-07-13 | IMPLEMENTER-A | PRE-DATA VERSION — sehemu A/B zinajazwa na run za Operator
(`intraday_state_engine.py` inaandika upya report hii na coverage halisi; `htf_context.py`
inaongeza sehemu B). Hapa: muundo + UTHIBITISHO WA NO-LOOKAHEAD (self-test evidence).*

---

## Muundo (kilichojengwa)

| Deliverable | Module | Nini |
|---|---|---|
| D1 | `src/research/intraday_state_engine.py` | ticks → **15m base bars** (time_bucket 15 MIN; o/h/l/c bid, tc, spr=median pips) → **rollup 30m** (semantiki ileile ya engine) → states kwa kila bar: `volatility_state`/`activity_state` (_reg3 deseasonalized, trailing ~mwaka 1) + `spread_state` (_rank_wide) + `session`. Hive: `data/processed/state/symbol=<SYM>/tf={15m,30m}.parquet` (mpangilio wa engine → `state_path()` loaders zote zinafanya kazi). Pairs 12 zote. |
| D2 | `src/research/htf_context.py` | H4/D1 (engine states) → features: **trend** (ema_slope, linreg_slope, trend_sign+deadband) · **regime** (vol/act states) · **structure** (rolling S/R 20 closed bars; dist_res_atr/dist_sup_atr) · **momentum** (rsi14 [reuse wilder_rsi], roc10). **Alignment**: `close_ts = ts + duration(TF)` → `join_asof(..., strategy="backward")` — LTF bar (open t) inapata HTF bar ya MWISHO iliyoFUNGWA ≤ t. Output: `data/processed/context/symbol=<SYM>/tf=<ltf>.parquet` — tayari kwa `_mask_context`-style filter ON signals. |

**Vilindwa:** `market_state_engine.py` HAIJAGUSWA (diff tupu; golden self-test PASS). H1/H2/H4/D1
paths hazikubadilika. Deseason window ya intraday ime-scale kwa samples/siku (SEAS_WIN_INTRA:
15m=240, 30m=120 same-hour samples = **siku 60 za muda halisi**, sawa na engine H1) — bila hii,
baseline ilikuwa ina-adapt ndani ya surge (self-test ilinasa: surge detection 49%→99%).

## UTHIBITISHO WA NO-LOOKAHEAD (self-test evidence — kiini cha C2-0)

```text
intraday_state_engine --self-test  PASS (5):
  [a] 30m rollup == manual aggregation ya 15m (o first/h max/l min/c last/tc sum/spr weighted)
  [b] TRUNCATION INVARIANCE: states za prefix == prefix ya states za full (hakuna future influence)
  [c] deseason: surge halisi HIGH 99% + UNKNOWN warmup (kama golden ya engine)
  [d] session = f(hour ya bar YAKE) — decidable ex-ante (ratiba)
  [e] 30m states schema kamili (OUT_COLS)

htf_context --self-test  PASS (5):
  [1] features sanity: up-trend -> trend_sign=+1; RSI/ROC finite; dist_res/sup >= 0
  [2] **MTEGO WA LEAKAGE**: H4 bar yenye SPIKE (roc +0.968) inamzunguka LTF bar t. Context ya t
      == bar iliyoTANGULIA (roc -0.008) — HAION I spike ✓; baada ya bar kufunga, spike inakuwa
      halali ✓. As-of backward join haitumii bar inayoendelea — imethibitishwa kwa mtego wa wazi.
  [2b] boundary: t == close_ts -> bar iliyofungwa HASA kwenye t inaruhusiwa (closed ≤ t)
  [3] D1: mid-day LTF bar -> context ya bar ya JANA (close_ts = ts+1d)
  [4] determinism + schema kamili (h4_*/d1_* zote)

FULL SWEEP: 24/24 PASS (market_state_engine golden PASS — haijaguswa)
```

## Amri za Operator (kujaza sehemu A/B na data halisi)

```text
1. python src/research/intraday_state_engine.py          # pairs 12 -> 15m/30m states + report sehemu A
2. python src/research/htf_context.py                    # H4/D1 features -> context parquet + sehemu B
   (inahitaji states za H4/D1 za market_state_engine — tayari zipo kwenye PC)
```

Sehemu A itaonyesha kwa kila pair×TF: bar counts, coverage per year, spread median (pips),
session distribution. Sehemu B: context bar counts kwa pair×LTF.

## Known Limitations

1. **Data runs = PC ya Operator** (ticks ~26GB) — hapa ni code + self-tests synthetic (Rule 7).
2. **Deseason ya intraday inatumia hour-of-day grouping** (kama engine) — si minute-of-day; bars 4
   za saa moja (15m) zinashiriki baseline ya saa. Consistent na engine; refinement ni ya baadaye.
3. **Rolling S/R (trailing 20 closed bars)** ni proxy ya structure — fractal-confirmed swings ni
   option ya baadaye (zinahitaji confirmation lag; rolling ni decidable kwa ujenzi).
4. **HTF features hazina UNKNOWN-warmup mask ya wazi** — bars za mwanzo zina NaN (rolling windows);
   consumers (strategist grid) wachuje NaN/UNKNOWN kabla ya filter.
5. **XAUUSD**: pip=0.01 (APPROVED); spr median ya gold itakuwa scale tofauti na FX — sanity check
   ya sehemu A itaionyesha.

## Open Questions

1. **C2-0b feature set** — Chief+STRATEGIST-M wathibitishe kwamba features hizi 9 (trend 3, regime 2,
   structure 2, momentum 2) zinatosha kwa hypotheses 10 za C2-1, au waongeze (mf. day-of-week,
   distance-to-daily-open)? Kuongeza ni additive (schema hairuhusiwi kuvunjika).
2. **H2 kama HTF ya tatu?** Kwa sasa H4+D1 (spec); `htf_features` ni TF-agnostic — H1/H2 ni param.
3. **Trend deadband 0.02 ATR/bar** — default ya kihandisi; strategist anaweza ku-grid.

---

*C2-0: 15m/30m states (semantiki ya market_state_engine, deseason muda-sawa, no-lookahead
truncation-invariant) + HTF context (H4/D1 features, as-of BACKWARD join, mtego wa leakage PASS).
Pairs 12. Sweep 24/24. Engine ya zamani haijaguswa. NO ML. Profitable ≠ Tradable Edge.*
