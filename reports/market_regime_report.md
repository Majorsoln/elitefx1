# Market Regime Report — EURGBP (PHASE 1, CQ-003)

*2026-06-22 13:01 | D1 | no-lookahead rolling (win=252, min=60) | vol/activity terciles 0.33/0.67 | spread WIDE > p85*

Bars: 2693 | 2016-01-04 → 2026-04-30

> Kila bar imeainishwa kwa distribution ya bars ZILIZOPITA tu — hakuna lookahead. Hii ndiyo context ambayo KILA event itasomwa ndani yake (CQ-002/003).

## Mgawanyo wa regime

| Dimension | LOW/NORMAL | NORMAL | HIGH/WIDE | n |
|-----------|-----------|--------|-----------|---|
| volatility | 1298 (49%) | 572 (22%) | 763 (29%) | 2633 |
| activity | 1032 (39%) | 742 (28%) | 859 (33%) | 2633 |
| spread | — | 2244 (85%) | 389 (15%) | 2633 |

## Persistence (avg run length, bars)

- volatility: 14.9 | activity: 3.5 | spread: 12.5

## Regime ya hivi karibuni

- date 2026-04-30: volatility=LOW, activity=HIGH, spread=NORMAL

---
*CQ-003: regime engine ndiyo context layer. No-lookahead (rolling past). Terciles -> LOW/NORMAL/HIGH; spread p85 -> WIDE. Downstream (volume_bars, event_diagnostics) zita-join regime hii. Metric rasmi = Expected Value (CQ-008).*