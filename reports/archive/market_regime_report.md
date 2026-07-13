# Market Regime Report — pairs ZOTE × TF ZOTE (PHASE 1, CQ-003)

*2026-06-22 15:11 | TF: H1, H2, H4, D1 | DESEASONALIZED kwa saa-ya-siku (trailing 60) | terciles 0.33/0.67 rolling (~mwaka 1/TF) | spread WIDE > p85 | no-lookahead*

> Metrics zime-DESEASONALIZE kabla ya terciles — 'HIGH' = juu ya kawaida ya SAA hiyo, sio tu 'ni mchana'. Labels RELATIVE kwa mwaka uliopita. Hakuna pair/TF iliyopendelewa.

## Volatility & Activity (% ya bars) + persistence (run length)

| Pair | TF | n | vol L/N/H | act L/N/H | spr WIDE | persist v/a/s |
|------|----|---|-----------|-----------|----------|---------------|
| EURUSD | H1 | 61,199 | 32/34/34 | 33/33/33 | 14% | 12/3/8 |
| EURUSD | H2 | 30,780 | 34/32/34 | 33/33/33 | 15% | 10/2/7 |
| EURUSD | H4 | 15,666 | 33/33/34 | 33/33/33 | 85% | 11/2/6 |
| EURUSD | D1 | 2,620 | 35/31/34 | 34/32/35 | 83% | 8/2/6 |
| GBPUSD | H1 | 61,201 | 33/33/34 | 33/34/33 | 16% | 12/3/8 |
| GBPUSD | H2 | 30,778 | 33/34/33 | 33/34/33 | 16% | 11/2/7 |
| GBPUSD | H4 | 15,668 | 32/35/33 | 33/34/33 | 84% | 12/2/6 |
| GBPUSD | D1 | 2,620 | 34/30/36 | 32/32/35 | 83% | 9/3/6 |
| USDJPY | H1 | 61,216 | 34/33/33 | 33/34/33 | 16% | 14/3/8 |
| USDJPY | H2 | 30,783 | 33/34/33 | 33/33/34 | 84% | 12/2/6 |
| USDJPY | H4 | 15,668 | 34/33/33 | 33/33/34 | 84% | 13/2/6 |
| USDJPY | D1 | 2,620 | 33/33/33 | 34/33/34 | 85% | 10/3/6 |
| EURJPY | H1 | 61,214 | 34/33/33 | 33/33/34 | 85% | 13/3/8 |
| EURJPY | H2 | 30,783 | 33/34/33 | 34/33/33 | 16% | 12/2/7 |
| EURJPY | H4 | 15,668 | 34/33/33 | 33/33/34 | 85% | 12/2/6 |
| EURJPY | D1 | 2,620 | 34/31/35 | 32/34/33 | 84% | 8/3/6 |
| USDCAD | H1 | 61,200 | 33/33/34 | 34/33/33 | 84% | 11/3/8 |
| USDCAD | H2 | 30,777 | 34/32/34 | 33/33/34 | 16% | 10/2/7 |
| USDCAD | H4 | 15,665 | 35/32/33 | 33/34/33 | 84% | 10/2/7 |
| USDCAD | D1 | 2,620 | 35/32/33 | 34/32/34 | 83% | 6/3/7 |
| USDCHF | H1 | 61,203 | 32/35/33 | 34/33/33 | 16% | 12/3/7 |
| USDCHF | H2 | 30,782 | 33/32/35 | 33/33/33 | 84% | 10/2/6 |
| USDCHF | H4 | 15,668 | 33/32/35 | 33/34/34 | 16% | 11/2/6 |
| USDCHF | D1 | 2,620 | 30/38/32 | 34/33/33 | 84% | 7/2/5 |
| AUDUSD | H1 | 61,212 | 34/33/33 | 34/33/33 | 84% | 11/3/8 |
| AUDUSD | H2 | 30,783 | 32/33/35 | 33/34/33 | 16% | 10/2/7 |
| AUDUSD | H4 | 15,668 | 33/32/36 | 33/32/34 | 84% | 9/2/7 |
| AUDUSD | D1 | 2,620 | 32/32/36 | 32/34/35 | 84% | 6/2/8 |
| NZDUSD | H1 | 61,212 | 34/34/33 | 33/33/34 | 84% | 11/3/7 |
| NZDUSD | H2 | 30,783 | 33/32/34 | 34/33/33 | 16% | 10/2/7 |
| NZDUSD | H4 | 15,668 | 32/35/32 | 33/33/34 | 84% | 9/2/6 |
| NZDUSD | D1 | 2,620 | 36/31/33 | 34/34/32 | 16% | 7/2/7 |
| EURGBP | H1 | 61,209 | 32/33/35 | 33/33/34 | 84% | 12/3/8 |
| EURGBP | H2 | 30,782 | 32/35/33 | 33/34/33 | 16% | 11/2/6 |
| EURGBP | H4 | 15,668 | 36/32/32 | 34/33/33 | 16% | 12/2/6 |
| EURGBP | D1 | 2,620 | 37/30/33 | 33/35/32 | 16% | 9/3/6 |

---
*DESEASONALIZE (÷ trailing same-hour mean) inaondoa intraday seasonality -> regime ni HALI YA SOKO sio saa. Terciles rolling = no-lookahead, relative kwa mwaka. persistence = avg bars regime inadumu (juu = context thabiti). Downstream zita-join regime hii kwa TF husika. Metric rasmi = Expected Value (CQ-008).*