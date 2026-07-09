# Market State Engine v1 — pairs ZOTE × TF ZOTE (PHASE 1, CQ-003)

*2026-07-09 14:46 | TF: H1, H2, H4, D1 | DESEASONALIZED (saa-ya-siku, trailing 60) | vol/activity terciles 0.33/0.67 (~mwaka 1/TF) | spread RANK top 15% (trailing 750) | no-lookahead*

> ⚠️ **STATE LAYER v1 (building blocks) — SIO regime engine ya mwisho.** States ni vipengele; regime za kweli (Compression/Expansion/Transition/Shock) + transitions zinajengwa baadaye. Labels RELATIVE kwa mwaka uliopita (no-lookahead).

## A) State distribution (% ya bars) + persistence (run length)

| Pair | TF | n | vol L/N/H | act L/N/H | spr WIDE | persist v/a/s |
|------|----|---|-----------|-----------|----------|---------------|
| EURUSD | H1 | 61,199 | 32/34/34 | 33/33/33 | 18% | 12/3/6 |
| EURUSD | H2 | 30,780 | 32/34/34 | 33/33/33 | 19% | 10/2/5 |
| EURUSD | H4 | 15,666 | 33/33/34 | 33/33/33 | 16% | 11/2/6 |
| EURUSD | D1 | 2,620 | 34/31/35 | 34/32/35 | 16% | 8/2/7 |
| GBPUSD | H1 | 61,201 | 33/33/34 | 33/33/34 | 19% | 12/3/6 |
| GBPUSD | H2 | 30,778 | 33/33/34 | 33/33/34 | 19% | 11/2/5 |
| GBPUSD | H4 | 15,668 | 33/32/35 | 33/33/34 | 17% | 12/2/6 |
| GBPUSD | D1 | 2,620 | 34/30/36 | 32/32/35 | 13% | 9/3/8 |
| USDJPY | H1 | 61,216 | 33/33/34 | 33/33/34 | 17% | 14/3/7 |
| USDJPY | H2 | 30,783 | 33/33/34 | 33/33/34 | 18% | 12/2/6 |
| USDJPY | H4 | 15,668 | 33/33/34 | 33/33/34 | 16% | 13/2/6 |
| USDJPY | D1 | 2,620 | 33/33/33 | 33/34/34 | 14% | 10/3/6 |
| EURJPY | H1 | 61,214 | 33/33/34 | 33/33/34 | 18% | 13/3/7 |
| EURJPY | H2 | 30,783 | 33/34/33 | 33/33/34 | 19% | 12/2/6 |
| EURJPY | H4 | 15,668 | 33/34/33 | 33/33/34 | 16% | 12/2/6 |
| EURJPY | D1 | 2,620 | 34/31/35 | 33/32/34 | 15% | 8/3/6 |
| USDCAD | H1 | 61,200 | 33/33/34 | 33/33/34 | 18% | 11/3/6 |
| USDCAD | H2 | 30,777 | 32/34/34 | 33/33/34 | 19% | 10/2/5 |
| USDCAD | H4 | 15,665 | 32/33/35 | 33/33/34 | 17% | 10/2/6 |
| USDCAD | D1 | 2,620 | 33/32/35 | 32/34/34 | 14% | 6/3/9 |
| USDCHF | H1 | 61,203 | 32/33/35 | 34/33/33 | 18% | 12/3/6 |
| USDCHF | H2 | 30,782 | 32/33/35 | 34/33/33 | 19% | 10/2/5 |
| USDCHF | H4 | 15,668 | 32/33/35 | 34/33/34 | 17% | 11/2/5 |
| USDCHF | D1 | 2,620 | 30/32/38 | 33/33/34 | 16% | 7/2/5 |
| AUDUSD | H1 | 61,212 | 33/33/34 | 33/33/34 | 18% | 11/3/6 |
| AUDUSD | H2 | 30,783 | 33/32/35 | 33/33/34 | 18% | 10/2/6 |
| AUDUSD | H4 | 15,668 | 33/32/36 | 33/32/34 | 17% | 9/2/6 |
| AUDUSD | D1 | 2,620 | 32/32/36 | 34/32/35 | 15% | 6/2/9 |
| NZDUSD | H1 | 61,212 | 33/34/34 | 34/33/33 | 18% | 11/3/6 |
| NZDUSD | H2 | 30,783 | 32/33/34 | 34/33/33 | 19% | 10/2/5 |
| NZDUSD | H4 | 15,668 | 32/32/35 | 34/33/33 | 18% | 9/2/6 |
| NZDUSD | D1 | 2,620 | 33/31/36 | 34/32/34 | 15% | 7/2/7 |
| EURGBP | H1 | 61,209 | 32/33/35 | 33/33/34 | 19% | 12/3/6 |
| EURGBP | H2 | 30,782 | 32/33/35 | 33/33/34 | 21% | 11/2/5 |
| EURGBP | H4 | 15,668 | 32/32/36 | 33/33/34 | 18% | 12/2/5 |
| EURGBP | D1 | 2,620 | 30/33/37 | 32/33/35 | 14% | 9/3/7 |

## B) ABSOLUTE distributions (pair individuality — GAP 3)

*Terciles huzalisha ~33/33/33 kila pair; hapa ndipo tofauti HALISI za pair zinaonekana.*

| Pair | TF | median ATR (pips) | median spread (pips) | median ticks/bar |
|------|----|-------------------|----------------------|------------------|
| EURUSD | H1 | 13.4 | 0.30 | 3,534 |
| EURUSD | H2 | 19.2 | 0.30 | 7,135 |
| EURUSD | H4 | 27.5 | 0.30 | 14,270 |
| EURUSD | D1 | 75.8 | 0.31 | 93,231 |
| GBPUSD | H1 | 18.3 | 0.90 | 3,780 |
| GBPUSD | H2 | 26.1 | 0.90 | 7,603 |
| GBPUSD | H4 | 37.1 | 0.90 | 14,985 |
| GBPUSD | D1 | 100.6 | 0.90 | 96,742 |
| USDJPY | H1 | 16.6 | 0.40 | 3,681 |
| USDJPY | H2 | 24.1 | 0.40 | 7,376 |
| USDJPY | H4 | 34.7 | 0.41 | 14,528 |
| USDJPY | D1 | 95.7 | 0.42 | 89,823 |
| EURJPY | H1 | 19.6 | 0.70 | 6,331 |
| EURJPY | H2 | 28.0 | 0.75 | 12,682 |
| EURJPY | H4 | 40.0 | 0.77 | 25,140 |
| EURJPY | D1 | 106.1 | 0.75 | 152,423 |
| USDCAD | H1 | 14.9 | 1.20 | 3,051 |
| USDCAD | H2 | 21.3 | 1.19 | 6,131 |
| USDCAD | H4 | 30.3 | 1.19 | 11,999 |
| USDCAD | D1 | 82.8 | 1.18 | 79,833 |
| USDCHF | H1 | 11.5 | 1.00 | 2,258 |
| USDCHF | H2 | 16.5 | 1.00 | 4,568 |
| USDCHF | H4 | 23.5 | 1.00 | 8,990 |
| USDCHF | D1 | 62.2 | 1.05 | 58,812 |
| AUDUSD | H1 | 11.9 | 1.00 | 2,590 |
| AUDUSD | H2 | 17.1 | 1.00 | 5,245 |
| AUDUSD | H4 | 24.3 | 1.00 | 10,432 |
| AUDUSD | D1 | 63.7 | 0.99 | 65,687 |
| NZDUSD | H1 | 11.4 | 1.10 | 2,301 |
| NZDUSD | H2 | 16.4 | 1.10 | 4,631 |
| NZDUSD | H4 | 23.3 | 1.10 | 9,248 |
| NZDUSD | D1 | 60.8 | 1.11 | 58,626 |
| EURGBP | H1 | 9.7 | 0.90 | 3,089 |
| EURGBP | H2 | 13.9 | 0.90 | 6,258 |
| EURGBP | H4 | 19.8 | 0.90 | 12,324 |
| EURGBP | D1 | 54.0 | 0.92 | 81,249 |

---
*STATE v1: deseasonalized (saa) -> states za HALI YA SOKO sio saa. vol/activity = rolling terciles (relative, no-lookahead). spread = RANK-based (tie/aggregation-robust, TF-invariant — inarekebisha GAP 2). Absolute median (pips) = pair individuality (GAP 3). Inayofuata: volume_bars -> regime_transition_report. Metric rasmi = Expected Value (CQ-008).*