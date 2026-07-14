# XAUUSD Spread-Quality Check — WAVE-B gold gate

*2026-07-14 19:38 | XAUUSD | TF: 15m, 30m | pip=0.01 | READ-ONLY (HAIBADILISHI config) | charter §6 risk #4*

> Provisional `max_spread_pips: XAUUSD = 60` inahitaji uthibitisho wa data kabla gold iingie S1 ya HC2-03/05/10. Pendekezo la data-driven hapa (~p95) = **pendekezo tu**; Chief/Operator waamue.


## Spread distribution (pips)

| TF | n | median | p90 | p95 | p99 | max | ATR med (pips) | spr_med/ATR | spr_p95/ATR | cost-share@p95 (TP2R) |
|----|---|--------|-----|-----|-----|-----|----------------|-------------|-------------|-----------------------|
| 15m | 241,029 | 35.0 | 58.6 | 71.0 | 108.3 | 907.4 | 188.1 | 0.186 | 0.377 | 18.87% |
| 30m | 120,632 | 35.0 | 58.6 | 71.0 | 107.6 | 858.6 | 277.7 | 0.126 | 0.256 | 12.78% |

## Pendekezo (SI kubadilisha config)

- max_spread ya sasa (provisional): **60** pips
- **Pendekezo la data-driven (~p95 30m, round-5): `XAUUSD: 75`** (p95=71.0; PANDISHA kutoka 60)
- ATR 30m med = 277.7 pips; spr p95 = 71.0 pips → spr p95 ni 25.6% ya ATR (cost-share @TP 2.0R = 12.78%; slip haijajumuishwa — lower bound).

## VERDICT: gold WAVE-B S1 → **SUITABLE**

- cost-share @p95 (TP 2.0R) = 12.78% < 25%.
- Msingi = **30m** (default ya entry; 15m = granularity-only, charter §0.5 cost-trap). HC2-03/05/10 ndizo hypotheses zenye XAUUSD.

## Known Limitations

1. **READ-ONLY** — hakuna config iliyobadilishwa (Chief ruling). Pendekezo tu.
2. **Cost-share = lower bound** (slip haijajumuishwa; spread mara moja kwa trade). Report ya S1 (cost_stress ev_spread_table) ndio hesabu kamili ya EV(Δspread) per cell.
3. **Data iko PC ya Operator (R-1)** — parquet ikikosekana, report inaonyesha coverage gap; self-test = synthetic (bila data ya nje).
4. spr = median per bar (engine); tail intrabar (spikes za news) haionekani hapa — p99 ndio proxy ya karibu zaidi ya tail risk.

*WAVE-B-prep | charter §6 risk #4 | READ-ONLY | Profitable != Tradable Edge.*