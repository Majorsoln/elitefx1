# Priority 2 — Exhaustion vs Momentum (rank-IC + EV-curve)

*Imezalishwa: 2026-06-20 21:49 | MR-fade entries (EUR pairs), exit tp_mean, cost imo | rank-IC (Spearman feature vs R) + EV-curve | 2025+ HAIJAGUSWA*

> **rank-IC** ndio metric kuu (robust kuliko endpoint-spread). \|IC\|≥~0.06 thabiti kwa TF + n kubwa = structure halisi. Curve jagged + IC≈0 = NOISE → DROP. Narrative ≠ edge.

## rank-IC (feature vs R) kwa TF

| Feature | D1 IC (n) | H4 IC (n) | H1 IC (n) |
|---------|---|---|---|
| accel | +0.089 (95) | +0.024 (437) | -0.033 (1575) |
| vol_expand | +0.130 (95) | -0.048 (437) | -0.042 (1575) |
| wick_rej *(proxy)* | -0.137 (95) | +0.072 (437) | -0.018 (1575) |
| time_since | +0.132 (93) | +0.020 (436) | -0.052 (1573) |

## EV-curve (Q1–Q5) — H1 (n=1575, baseline EV=+0.002R)

| Feature | Q1 (n) | Q2 | Q3 | Q4 | Q5 |
|---------|--------|----|----|----|----|
| accel | +0.069 (315) | +0.117 (315) | +0.038 (315) | -0.051 (315) | -0.164 (315) |
| vol_expand | +0.077 (315) | +0.240 (315) | -0.066 (315) | +0.012 (315) | -0.254 (315) |
| wick_rej | +0.102 (315) | -0.114 (315) | -0.007 (315) | +0.128 (315) | -0.101 (315) |
| time_since | +0.155 (305) | +0.044 (321) | +0.006 (310) | -0.120 (318) | -0.081 (319) |

---
*rank-IC = Spearman(feature, R) — feature INATENGANISHA winners/losers kama \|IC\| ni meaningful NA thabiti kwa TF. Curve jagged + IC≈0 = noise → DROP (hata kama ina mantiki). EV-curve inaonyeshwa kwa TF yenye n kubwa. wick_rej = PROXY ya rejection (OHLC, sio order flow). Keep features zenye IC thabiti → conditional strategy → OOS.*