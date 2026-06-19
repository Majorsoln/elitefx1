# Condition Scan — EMA200 (data halisi)

*Imezalishwa: 2026-06-18 22:35 | price_vs_ema = (close−EMA200)/EMA200 | win = forward return upande wa trade | NO-lookahead*

> Trend-following: above→LONG, below→SHORT. Win-rate ~0.50 = bahati (hakuna edge); >0.50 thabiti = edge.


## D1  (forward holding = 5 bars)

| Condition | dir | total bars | % ya data | win-rate | mean fwd ret |
|-----------|-----|-----------|-----------|----------|--------------|
| above (pve>0) | LONG | 11,691 | 52.2% | 0.495 | -0.00021 |
| below (pve<0) | SHORT | 10,719 | 47.8% | 0.477 | -0.00050 |
| far_above (>=q70) | LONG | 6,723 | 30.0% | 0.475 | -0.00069 |
| far_below (<=q30) | SHORT | 6,723 | 30.0% | 0.461  ⬅️ | -0.00089 |
| extreme_above (>=q90) | LONG | 2,241 | 10.0% | 0.447  ⬅️ | -0.00159 |
| extreme_below (<=q10) | SHORT | 2,241 | 10.0% | 0.412  ⬅️ | -0.00235 |

## H4  (forward holding = 10 bars)

| Condition | dir | total bars | % ya data | win-rate | mean fwd ret |
|-----------|-----|-----------|-----------|----------|--------------|
| above (pve>0) | LONG | 73,381 | 51.3% | 0.501 | -0.00008 |
| below (pve<0) | SHORT | 69,756 | 48.7% | 0.484 | -0.00015 |
| far_above (>=q70) | LONG | 42,943 | 30.0% | 0.495 | -0.00017 |
| far_below (<=q30) | SHORT | 42,943 | 30.0% | 0.475 | -0.00026 |
| extreme_above (>=q90) | LONG | 14,319 | 10.0% | 0.483 | -0.00037 |
| extreme_below (<=q10) | SHORT | 14,319 | 10.0% | 0.453  ⬅️ | -0.00063 |

## H1  (forward holding = 12 bars)

| Condition | dir | total bars | % ya data | win-rate | mean fwd ret |
|-----------|-----|-----------|-----------|----------|--------------|
| above (pve>0) | LONG | 288,208 | 51.0% | 0.499 | -0.00004 |
| below (pve<0) | SHORT | 276,527 | 49.0% | 0.486 | -0.00006 |
| far_above (>=q70) | LONG | 169,422 | 30.0% | 0.493 | -0.00008 |
| far_below (<=q30) | SHORT | 169,422 | 30.0% | 0.482 | -0.00008 |
| extreme_above (>=q90) | LONG | 56,478 | 10.0% | 0.485 | -0.00016 |
| extreme_below (<=q10) | SHORT | 56,478 | 10.0% | 0.473 | -0.00014 |

---
*Win-rate ni wastani (weighted kwa bars) wa pairs 9. **⬅️** = win-rate inatofautiana na 0.50 kwa ≥0.03 (mshukiwa wa edge — angalia kama thabiti kwa TF/condition zote). Kama zote ~0.50 hata kwenye extremes → trend-following haina edge ya mwelekeo, hata kwa thresholds.*