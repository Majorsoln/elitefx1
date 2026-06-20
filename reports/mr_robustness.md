# Mean-Reversion — EMA Parameter Robustness

*Imezalishwa: 2026-06-20 08:58 | ROBUST = net>0 + p<0.05 vipindi VYOTE (P1 2016-20, P2 2021-24) | EMA span 50/100/200 | sio optimization*

| Pair | EMA50 | EMA100 | EMA200 | Hukumu |
|------|-------|--------|--------|--------|
| EURUSD | ❌ | ❌ | ✅ | ⚠️ 1/3 (fragile) |
| GBPUSD | ❌ | ❌ | ❌ | ❌ hakuna |
| USDJPY | ❌ | ❌ | ❌ | ❌ hakuna |
| EURJPY | ❌ | ❌ | ❌ | ❌ hakuna |
| USDCAD | ❌ | ❌ | ❌ | ❌ hakuna |
| USDCHF | ❌ | ❌ | ❌ | ❌ hakuna |
| AUDUSD | ❌ | ❌ | ❌ | ❌ hakuna |
| NZDUSD | ❌ | ❌ | ❌ | ❌ hakuna |
| EURGBP | ❌ | ✅ | ✅ | ⚠️ 2/3 (fragile) |

---
*🟢 ROBUST kwa EMA zote = edge halisi, haitegemei EMA200. ⚠️ {1,2}/3 = inategemea EMA fulani → fragile/overfit-risk. ❌ = hakuna mean-reversion (pengine pair inatrend). **Kujibu swali:** kama EURGBP ni 🟢 na pair iliyoshindwa haiamki kwa uthabiti → EMA200 HAIKUWA tatizo; failures ni halisi.*