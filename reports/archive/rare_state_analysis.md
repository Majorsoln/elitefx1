# Rare State Analysis — market configuration ya cluster nadra (Phase 5.10)

*2026-06-26 17:45 | latent k=4 | rare cluster = C3 (ndogo zaidi) | profile/duration/exit/returns | NO labels za binadamu | rare bars=3,147/983,845*

> **F-017 (Chief):** rare states zinaweza kubeba INFORMATION nyingi (crash/news/liquidity = 1% lakini zinaamua performance). Trade = consequence ya MARKET CONFIGURATION, sio signal. Cluster ≠ State — tunachunguza tabia, hatuipi jina. NO ML.

## 1) Frequency — rare C3 = **0.3%** ya bars

| pair | rate % |
|------|--------|
| EURUSD | 0.3% |
| GBPUSD | 0.3% |
| USDJPY | 0.4% |
| EURJPY | 0.4% |
| USDCAD | 0.3% |
| USDCHF | 0.4% |
| AUDUSD | 0.2% |
| NZDUSD | 0.2% |
| EURGBP | 0.3% |

## 2) Feature signature — rare C3 vs global (mean, per-pair z)

| feature | rare | global | Δ |
|---------|------|--------|---|
| vol_z | +0.22 | -0.04 | +0.26 |
| vol_slope | -0.45 | +0.00 | -0.45 |
| act_z | -0.90 | -0.00 | -0.90 |
| act_slope | -1.00 | -0.00 | -1.00 |
| spr_z | +12.14 | -0.00 | +12.14 |
| transition | +0.63 | +0.60 | +0.04 |
| lifecycle | +0.08 | +0.09 | -0.01 |

## 3) Raw state composition ndani ya rare C3

| dimension | distribution |
|-----------|--------------|
| volatility | LOW 47% · HIGH 30% · NORMAL 24% |
| activity | LOW 72% · HIGH 19% · NORMAL 9% |
| spread | WIDE 97% · NORMAL 3% |

## 4) Duration (run length, bars) + exit distribution

- duration: median **1** | mean 1.5 | p90 3 | max 23 | n_runs 2,056
- exit → C2 58% · C1 34% · C0 7%

## 5) Return distribution (|6-bar move| pips): rare vs non-rare

| set | n | mean | median | p95 | p99 |
|-----|---|------|--------|-----|-----|
| rare | 3,146 | 23.8 | 14.5 | 75 | 143 |
| non-rare | 980,483 | 26.2 | 16.3 | 82 | 156 |

→ rare/non-rare mean move ratio = **0.91×** (— sawa-sawa)

---
*Rare cluster ni MARKET CONFIGURATION, sio jina. F-017: rare states zikiwa na dispersion/return kubwa zaidi = high information. Hatuanzi Opportunity Engine; kwanza tunajua rare state inafanya nini (Configuration thinking). Cluster ≠ State (Latent State CANDIDATE). NO ML, NO human taxonomy. Inayofuata: Cluster Robustness (5.11), Validation (5.12).*