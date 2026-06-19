# Trend Structure #2 — Conditioner Interaction

*Imezalishwa: 2026-06-19 18:40 | signal=sign(EMA slope); conditioner quartiles (Q1=chini…Q4=juu) | trend-follow win-rate ndani ya kila Q | no-lookahead | pairs=9*

> Q4 ya ER (trend safi) win >0.55 = trend-following ina edge hapo. win <0.45 = mean-reversion. Zote ~0.50 = conditioner haisaidii.


## D1  (fwd=5, window=10)


**Conditioner: Efficiency Ratio (usafi wa trend)**

| Quartile | total bars | trend-follow win | mean dir ret |
|----------|-----------|------------------|--------------|
| Q1 (chini) | 5,580 | 0.486 | -0.00040 |
| Q2 | 5,580 | 0.482 | -0.00037 |
| Q3 | 5,580 | 0.481 | -0.00029 |
| Q4 (juu) | 5,580 | 0.478 | -0.00071 |

**Conditioner: Volatility**

| Quartile | total bars | trend-follow win | mean dir ret |
|----------|-----------|------------------|--------------|
| Q1 (chini) | 5,580 | 0.472 | -0.00034 |
| Q2 | 5,580 | 0.499 | +0.00000 |
| Q3 | 5,580 | 0.488 | -0.00024 |
| Q4 (juu) | 5,580 | 0.468  ⬅️ | -0.00118 |

## H4  (fwd=10, window=20)


**Conditioner: Efficiency Ratio (usafi wa trend)**

| Quartile | total bars | trend-follow win | mean dir ret |
|----------|-----------|------------------|--------------|
| Q1 (chini) | 35,739 | 0.494 | -0.00007 |
| Q2 | 35,736 | 0.495 | -0.00009 |
| Q3 | 35,739 | 0.489 | -0.00017 |
| Q4 (juu) | 35,743 | 0.493 | -0.00007 |

**Conditioner: Volatility**

| Quartile | total bars | trend-follow win | mean dir ret |
|----------|-----------|------------------|--------------|
| Q1 (chini) | 35,739 | 0.505 | +0.00010 |
| Q2 | 35,736 | 0.491 | -0.00012 |
| Q3 | 35,739 | 0.493 | -0.00006 |
| Q4 (juu) | 35,743 | 0.482 | -0.00033 |

## H1  (fwd=12, window=24)


**Conditioner: Efficiency Ratio (usafi wa trend)**

| Quartile | total bars | trend-follow win | mean dir ret |
|----------|-----------|------------------|--------------|
| Q1 (chini) | 141,130 | 0.493 | -0.00005 |
| Q2 | 141,127 | 0.492 | -0.00005 |
| Q3 | 141,128 | 0.496 | -0.00005 |
| Q4 (juu) | 141,134 | 0.495 | -0.00000 |

**Conditioner: Volatility**

| Quartile | total bars | trend-follow win | mean dir ret |
|----------|-----------|------------------|--------------|
| Q1 (chini) | 141,130 | 0.504 | +0.00003 |
| Q2 | 141,127 | 0.490 | -0.00006 |
| Q3 | 141,128 | 0.497 | -0.00002 |
| Q4 (juu) | 141,134 | 0.485 | -0.00011 |

---
*⬅️ = win ≠ 0.50 kwa ≥0.03. **Cha kuangalia:** je win-rate inabadilika monotonic na quartile ya ER/vol? Q4-ER (trend safi) >0.55 thabiti kwenye TF/pairs → **edge ya kwanza** (trend-following ndani ya trend safi) → Phase B. Q4-ER <0.45 → mean-reversion kwenye trend safi. Zote ~0.50 → conditioner haisaidii.*