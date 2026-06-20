# Method #2/#13 — Cross-pair Spread Mean-Reversion

*Imezalishwa: 2026-06-20 14:58 | spread=log(A)−log(B), |z|≥2.0, fade | net baada ya cost (miguu 2) | Phase B N=5000 | sub-period | 2025+ HAIJAGUSWA*

> ROBUST = net>0 NA p<0.05 vipindi VYOTE. Stat-arb: corr pairs' spread hu-mean-revert.

| Spread | P1 n | P1 net | P1 p | P2 n | P2 net | P2 p | Hukumu |
|--------|------|--------|------|------|--------|------|--------|
| AUDUSD−NZDUSD | 57 | -0.04372 | 1.000 | 54 | -0.04648 | 1.000 | ❌ |
| EURUSD−GBPUSD | 57 | -0.02789 | 1.000 | 61 | -0.02692 | 1.000 | ❌ |
| AUDUSD−EURUSD | 53 | -0.02761 | 1.000 | 53 | -0.02166 | 1.000 | ❌ |

---
*✅ ROBUST (net>0 + p<0.05 vipindi VYOTE) = spread MR ni edge halisi → inastahili OOS. Stat-arb market-neutral (long A, short B). Cost = miguu 2. **β imekadiriwa kwa rolling OLS (window 60, no-lookahead)** — sio β=1 tena (kritique ya Japhet). Spread = log(A) − β·log(B) (cointegration residual).*