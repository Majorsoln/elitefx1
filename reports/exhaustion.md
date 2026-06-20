# Priority 2 — Exhaustion vs Momentum (Quantile EV Curve)

*Imezalishwa: 2026-06-20 21:30 | MR-fade entries (EUR pairs), exit tp_mean, cost imo | EV(R) per quantile | baseline EV(all)=+0.092R, n=95 | 2025+ HAIJAGUSWA*

> Quantile EV-curve KWANZA (sio threshold). Feature ikionyesha STRUCTURE (EV inabadilika monotonic/wazi kwa quantile) = inatenganisha winners/losers. Narrative gain ≠ edge gain.

| Feature | Q1 EV (n) | Q2 | Q3 | Q4 | Q5 | spread Q5−Q1 |
|---------|-----------|----|----|----|----|--------------|
| accel | -0.160 (19) | +0.335 (19) | -0.163 (19) | +0.297 (19) | +0.148 (19) | +0.308  ⬅️ |
| vol_expand | +0.051 (19) | -0.323 (19) | -0.370 (19) | +0.696 (19) | +0.404 (19) | +0.353  ⬅️ |
| wick_rej *(proxy)* | +0.261 (19) | +0.296 (19) | +0.070 (19) | +0.442 (19) | -0.612 (19) | -0.873  ⬅️ |
| time_since | +0.062 (14) | -0.103 (23) | +0.084 (19) | +0.044 (18) | +0.482 (19) | +0.420  ⬅️ |

---
*baseline EV(all entries) = **+0.092R**. Feature INAONGEZA edge kama quantile fulani ina EV **juu zaidi** ya baseline kwa kiasi (⬅️ = spread Q5−Q1 ≥0.15R). Hapo ndipo tutaweza kuchagua quantiles (mf. Q1-Q2=exhaustion) — BAADAYE, kwa ushahidi. Feature isiyo na structure → DROP (hata kama ina mantiki). wick_rej ni PROXY ya rejection (OHLC, sio order flow). Hatua: keep features zenye structure → conditional strategy → OOS.*