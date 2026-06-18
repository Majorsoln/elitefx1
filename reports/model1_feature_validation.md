# Model 1 — Feature Validation

*Imezalishwa: 2026-06-18 08:19 | rank-IC (Spearman) vs forward returns, no-lookahead | pairs=9 | \|IC\|>0.03 = edge*


## D1

**Directional** (vs forward SIGNED return) — mean IC (n pairs \|IC\|>thr):

| Feature | k=1 | k=5 |
|---------|-----|-----|
| ret | -0.0129 (0) | 0.0002 (5) |
| ema_slope | -0.0174 (3) | -0.0661 (8) |
| price_vs_ema | -0.023 (2) | -0.0673 (7) |

**Strength** (vs \|forward return\|) — mean IC (n pairs \|IC\|>thr):

| Feature | k=1 | k=5 |
|---------|-----|-----|
| vol | 0.1878 (9) | 0.1468 (9) |
| adx | 0.0316 (6) | 0.0135 (6) |

**Confirmation** (signed IC) — mean IC (n pairs \|IC\|>thr):

| Feature | k=1 | k=5 |
|---------|-----|-----|
| volume_imbalance | 0.0133 (1) | -0.0033 (6) |
| tick_count | 0.004 (0) | 0.0161 (4) |

## H4

**Directional** (vs forward SIGNED return) — mean IC (n pairs \|IC\|>thr):

| Feature | k=1 | k=5 |
|---------|-----|-----|
| ret | -0.0172 (1) | 0.0043 (2) |
| ema_slope | -0.0051 (0) | -0.0253 (2) |
| price_vs_ema | -0.0097 (0) | -0.024 (3) |

**Strength** (vs \|forward return\|) — mean IC (n pairs \|IC\|>thr):

| Feature | k=1 | k=5 |
|---------|-----|-----|
| vol | 0.1996 (9) | 0.1959 (9) |
| adx | 0.02 (3) | -0.0086 (5) |

**Confirmation** (signed IC) — mean IC (n pairs \|IC\|>thr):

| Feature | k=1 | k=5 |
|---------|-----|-----|
| volume_imbalance | -0.0002 (0) | -0.0071 (0) |
| tick_count | -0.0295 (3) | 0.001 (0) |

## H2

**Directional** (vs forward SIGNED return) — mean IC (n pairs \|IC\|>thr):

| Feature | k=1 | k=5 |
|---------|-----|-----|
| ret | -0.0306 (4) | -0.0154 (1) |
| ema_slope | -0.0039 (0) | -0.0134 (0) |
| price_vs_ema | -0.009 (0) | -0.0171 (1) |

**Strength** (vs \|forward return\|) — mean IC (n pairs \|IC\|>thr):

| Feature | k=1 | k=5 |
|---------|-----|-----|
| vol | 0.1832 (9) | 0.1909 (9) |
| adx | 0.0226 (3) | 0.01 (3) |

**Confirmation** (signed IC) — mean IC (n pairs \|IC\|>thr):

| Feature | k=1 | k=5 |
|---------|-----|-----|
| volume_imbalance | 0.0009 (0) | -0.0015 (0) |
| tick_count | -0.0103 (1) | -0.0118 (0) |

## H1

**Directional** (vs forward SIGNED return) — mean IC (n pairs \|IC\|>thr):

| Feature | k=1 | k=5 |
|---------|-----|-----|
| ret | -0.0324 (4) | -0.014 (0) |
| ema_slope | -0.0035 (0) | -0.0121 (0) |
| price_vs_ema | -0.0087 (0) | -0.0147 (1) |

**Strength** (vs \|forward return\|) — mean IC (n pairs \|IC\|>thr):

| Feature | k=1 | k=5 |
|---------|-----|-----|
| vol | 0.1851 (9) | 0.1727 (9) |
| adx | 0.031 (3) | 0.0032 (2) |

**Confirmation** (signed IC) — mean IC (n pairs \|IC\|>thr):

| Feature | k=1 | k=5 |
|---------|-----|-----|
| volume_imbalance | 0.002 (0) | 0.0032 (0) |
| tick_count | -0.0053 (0) | -0.0094 (1) |

---
### Tafsiri & methodolojia

- **k=1 ni metric ya msingi (unbiased).** Feature yenye mean IC ~0 na pairs chache zenye \|IC\|>thr = **haina predictive power** → idemote/idrop (kama `volume_imbalance`).
- **Directional** (returns/EMA slope/price-vs-EMA): signed IC + hit-rate. **Strength** (vol/ADX): IC dhidi ya \|return\| = je inatabiri UKUBWA wa move (sio mwelekeo). **Confirmation**: signed IC ≈ 0 kote = haifai Model 1.
- ⚠️ **Bias ya long-horizon:** k=5 ni supportive tu; k≥10 kwa features persistent (price_vs_ema/ema_slope) zina **spurious-regression bias** (tulithibitisha: random walk → IC −0.15 @ k20). Kwa hiyo tumebaki k=1/k=5; **multi-horizon predictive testing definitive = Phase B permutation (Sehemu 7).**