# C2-0 — Intraday states (15m/30m) + HTF context (MZUNGUKO-2)

*2026-07-13 23:03 | pairs=12 | TF: 15m, 30m | states: vol/activity (_reg3 deseasonalized, trailing ~mwaka 1) + spread (_rank_wide) + session | NO-LOOKAHEAD (shift(1)/trailing kila mahali — semantiki ya market_state_engine)*

## A) Coverage + sanity (states za 15m/30m)

| Pair | TF | bars | years (coverage) | spread med (pips) | sessions (ASIA/LON/NY/LATE) |
|------|----|------|------------------|-------------------|------------------------------|
| EURUSD | 15m | 251,781 | 2016:24k 2017:24k 2018:24k 2019:24k 2020:24k 2021:24k 2022:24k 2023:24k 2024:24k 2025:24k 2026:8k | 0.30 | 0.30/0.21/0.21/0.28 |
| EURUSD | 30m | 125,897 | 2016:12k 2017:12k 2018:12k 2019:12k 2020:12k 2021:12k 2022:12k 2023:12k 2024:12k 2025:12k 2026:4k | 0.30 | 0.30/0.21/0.21/0.28 |
| GBPUSD | 15m | 251,789 | 2016:24k 2017:24k 2018:24k 2019:24k 2020:24k 2021:24k 2022:24k 2023:24k 2024:24k 2025:24k 2026:8k | 0.90 | 0.30/0.21/0.21/0.28 |
| GBPUSD | 30m | 125,901 | 2016:12k 2017:12k 2018:12k 2019:12k 2020:12k 2021:12k 2022:12k 2023:12k 2024:12k 2025:12k 2026:4k | 0.90 | 0.30/0.21/0.21/0.28 |
| USDJPY | 15m | 251,860 | 2016:24k 2017:24k 2018:24k 2019:24k 2020:24k 2021:24k 2022:24k 2023:24k 2024:24k 2025:24k 2026:8k | 0.40 | 0.30/0.21/0.21/0.28 |
| USDJPY | 30m | 125,933 | 2016:12k 2017:12k 2018:12k 2019:12k 2020:12k 2021:12k 2022:12k 2023:12k 2024:12k 2025:12k 2026:4k | 0.40 | 0.30/0.21/0.21/0.28 |
| EURJPY | 15m | 251,834 | 2016:24k 2017:24k 2018:24k 2019:24k 2020:24k 2021:24k 2022:24k 2023:24k 2024:24k 2025:24k 2026:8k | 0.70 | 0.30/0.21/0.21/0.28 |
| EURJPY | 30m | 125,924 | 2016:12k 2017:12k 2018:12k 2019:12k 2020:12k 2021:12k 2022:12k 2023:12k 2024:12k 2025:12k 2026:4k | 0.74 | 0.30/0.21/0.21/0.28 |
| USDCAD | 15m | 251,779 | 2016:24k 2017:24k 2018:24k 2019:24k 2020:24k 2021:24k 2022:24k 2023:24k 2024:24k 2025:24k 2026:8k | 1.20 | 0.30/0.21/0.21/0.28 |
| USDCAD | 30m | 125,896 | 2016:12k 2017:12k 2018:12k 2019:12k 2020:12k 2021:12k 2022:12k 2023:12k 2024:12k 2025:12k 2026:4k | 1.16 | 0.30/0.21/0.21/0.28 |
| USDCHF | 15m | 251,781 | 2016:24k 2017:24k 2018:24k 2019:24k 2020:24k 2021:24k 2022:24k 2023:24k 2024:24k 2025:24k 2026:8k | 1.00 | 0.30/0.21/0.21/0.28 |
| USDCHF | 30m | 125,902 | 2016:12k 2017:12k 2018:12k 2019:12k 2020:12k 2021:12k 2022:12k 2023:12k 2024:12k 2025:12k 2026:4k | 1.00 | 0.30/0.21/0.21/0.28 |
| AUDUSD | 15m | 251,837 | 2016:24k 2017:24k 2018:24k 2019:24k 2020:24k 2021:24k 2022:24k 2023:24k 2024:24k 2025:24k 2026:8k | 1.00 | 0.30/0.21/0.21/0.28 |
| AUDUSD | 30m | 125,923 | 2016:12k 2017:12k 2018:12k 2019:12k 2020:12k 2021:12k 2022:12k 2023:12k 2024:12k 2025:12k 2026:4k | 1.00 | 0.30/0.21/0.21/0.28 |
| NZDUSD | 15m | 251,803 | 2016:24k 2017:24k 2018:24k 2019:24k 2020:24k 2021:24k 2022:24k 2023:24k 2024:24k 2025:24k 2026:8k | 1.10 | 0.30/0.21/0.21/0.28 |
| NZDUSD | 30m | 125,918 | 2016:12k 2017:12k 2018:12k 2019:12k 2020:12k 2021:12k 2022:12k 2023:12k 2024:12k 2025:12k 2026:4k | 1.10 | 0.30/0.21/0.21/0.28 |
| EURGBP | 15m | 251,828 | 2016:24k 2017:24k 2018:24k 2019:24k 2020:24k 2021:24k 2022:24k 2023:24k 2024:24k 2025:24k 2026:8k | 0.90 | 0.30/0.21/0.21/0.28 |
| EURGBP | 30m | 125,918 | 2016:12k 2017:12k 2018:12k 2019:12k 2020:12k 2021:12k 2022:12k 2023:12k 2024:12k 2025:12k 2026:4k | 0.90 | 0.30/0.21/0.21/0.28 |
| GBPJPY | 15m | 253,738 | 2016:24k 2017:24k 2018:24k 2019:24k 2020:24k 2021:24k 2022:24k 2023:21k 2024:24k 2025:24k 2026:8k | 1.70 | 0.29/0.21/0.21/0.29 |
| GBPJPY | 30m | 126,883 | 2016:12k 2017:12k 2018:12k 2019:12k 2020:12k 2021:12k 2022:12k 2023:10k 2024:12k 2025:12k 2026:4k | 1.71 | 0.29/0.21/0.21/0.29 |
| EURCHF | 15m | 253,803 | 2016:24k 2017:24k 2018:24k 2019:24k 2020:24k 2021:24k 2022:24k 2023:21k 2024:24k 2025:24k 2026:8k | 1.00 | 0.29/0.21/0.21/0.29 |
| EURCHF | 30m | 126,920 | 2016:12k 2017:12k 2018:12k 2019:12k 2020:12k 2021:12k 2022:12k 2023:10k 2024:12k 2025:12k 2026:4k | 1.05 | 0.29/0.21/0.21/0.29 |
| XAUUSD | 15m | 241,029 | 2016:23k 2017:23k 2018:23k 2019:23k 2020:23k 2021:23k 2022:23k 2023:20k 2024:23k 2025:23k 2026:7k | 35.00 | 0.31/0.22/0.22/0.26 |
| XAUUSD | 30m | 120,632 | 2016:11k 2017:11k 2018:11k 2019:11k 2020:11k 2021:11k 2022:11k 2023:10k 2024:11k 2025:11k 2026:3k | 35.00 | 0.31/0.22/0.22/0.26 |

*Sehemu B (HTF context features + uthibitisho wa no-lookahead) inaongezwa na htf_context.py. Self-test evidence: run_selftests.py (intraday_state_engine + htf_context).*
## B) HTF context features (H4/D1 -> 15m/30m; as-of BACKWARD, no-lookahead)

*2026-07-14 06:10 | features: ema_slope/linreg_slope/trend_sign (trend), vol_state/act_state (regime), dist_res_atr/dist_sup_atr (structure, rolling S/R 20 closed bars), rsi14/roc10 (momentum) | join: close_ts=ts+duration, backward*

| Pair | LTF | context bars |
|------|-----|--------------|
| EURUSD | 15m | 251,781 |
| EURUSD | 30m | 125,897 |
| GBPUSD | 15m | 251,789 |
| GBPUSD | 30m | 125,901 |
| USDJPY | 15m | 251,860 |
| USDJPY | 30m | 125,933 |
| EURJPY | 15m | 251,834 |
| EURJPY | 30m | 125,924 |
| USDCAD | 15m | 251,779 |
| USDCAD | 30m | 125,896 |
| USDCHF | 15m | 251,781 |
| USDCHF | 30m | 125,902 |
| AUDUSD | 15m | 251,837 |
| AUDUSD | 30m | 125,923 |
| NZDUSD | 15m | 251,803 |
| NZDUSD | 30m | 125,918 |
| EURGBP | 15m | 251,828 |
| EURGBP | 30m | 125,918 |
| GBPJPY | 15m | 253,738 |
| GBPJPY | 30m | 126,883 |
| EURCHF | 15m | 253,803 |
| EURCHF | 30m | 126,920 |
| XAUUSD | 15m | 241,029 |
| XAUUSD | 30m | 120,632 |

*No-lookahead: self-test ya MTEGO (htf_context [2]) inathibitisha context ya LTF bar HAIONI HTF bar inayoizunguka (future info) — inatumia bar iliyoFUNGWA kabla.*
## C) C2-2a — Infra ya context-aware S1 (WAVE-C2-A: HC2-01/03/06)

*2026-07-14 | IMPLEMENTER-A | strategy_lab.py: context loader + `_mask_context_dir` | ADDITIVE — diff ni insertions-only (142+, 0−); ZERO statistic fns zimeguswa (episodes/_mask_context/pvalue_boot/pool_streams/_r_normalize/bh_fdr byte-identical; golden hashes za event_quality_report PASS)*

**Vipande 2 (kwa spec ya STRATEGIST-M §3 + prompt ya Chief):**

1. **CONTEXT LOADER** — `load_window` sasa inarudisha key MPYA `ctx` (ADDITIVE): dict ya
   arrays za `h4_*`/`d1_*` (zote za context parquet ya `htf_context.py`) SAMBAMBA na o/h/l/c —
   LEFT-join EXACT kwa `ts` (row_index inalinda order ya left frame; join ni kwa ts, si order ya
   rows). Numeric → float64 (null→NaN); state → object. Parquet ikikosekana → `ctx=None` + onyo
   (grids za C1/H1/H4 bila context zinaendelea kama zamani). HAKUNA join mpya ya HTF —
   alignment ni ya htf_context (no-lookahead imekwisha-thibitishwa kwa mtego).
2. **`_mask_context_dir(out, entry, allow_long, allow_short)`** — direction-aware mask MPYA
   sambamba (`_mask_context` HAIJAGUSWA): market `sig=+1` inahitaji `allow_long[i]`, `sig=-1`
   inahitaji `allow_short[i]`; stop `LL[~allow_long]=NaN`, `SS[~allow_short]=NaN`. Decidability
   ILEILE — values za SIGNAL bar i. One-sided (HC2-01) na conditions tofauti kwa long/short
   (HC2-06) zinawezekana.

**Self-test evidence (strategy_lab checks mpya 4 — zote PASS):**

| Check | Nini kinathibitishwa | Matokeo |
|-------|----------------------|---------|
| [10] ctx loader | ts-alignment kwa parquet yenye rows SCRAMBLED (join ni kwa ts); pengo la ts → NaN/None; dtypes (float64/object); missing → None + onyo bila kuvunja | PASS |
| [11] mirror symmetry | swap(allow_long↔allow_short) + flip ya sig/levels → matokeo yana-mirror HASA (market NA stop); inputs haziguswi (copy) | PASS |
| [12] one-sided | `allow_short=all-False` → market haina sig −1; stop SS zote NaN na `episodes()` inatoa trades za long TU (n=646); long leg haijaguswa | PASS |
| [13] decidability trap | mask inatumia value ya SIGNAL bar i: `allow[i]=True` pekee → signal inaishi; `allow[i+1]=True` pekee → signal inakufa | PASS |

**SWEEP: 24/24 PASS** (run_selftests — modules zote, ikiwemo family_pooled AT1–AT8+F1/F2 na
golden byte-identical za event_quality_report). `false_break` ni WAVE-B — HAIJAJENGWA (kwa spec).

## B) HTF context features (H4/D1 -> 15m/30m; as-of BACKWARD, no-lookahead)

*2026-07-15 20:33 | features: ema_slope/linreg_slope/trend_sign (trend), vol_state/act_state (regime), dist_res_atr/dist_sup_atr (structure, rolling S/R 20 closed bars), rsi14/roc10 (momentum) | join: close_ts=ts+duration, backward*

| Pair | LTF | context bars |
|------|-----|--------------|
| EURUSD | H1 | 62,951 |
| GBPUSD | H1 | 62,953 |
| USDJPY | H1 | 62,968 |
| EURJPY | H1 | 62,966 |
| USDCAD | H1 | 62,952 |
| USDCHF | H1 | 62,955 |
| AUDUSD | H1 | 62,964 |
| NZDUSD | H1 | 62,964 |
| EURGBP | H1 | 62,961 |
| GBPJPY | H1 | 63,448 |
| EURCHF | H1 | 63,468 |
| XAUUSD | H1 | 60,436 |

*No-lookahead: self-test ya MTEGO (htf_context [2]) inathibitisha context ya LTF bar HAIONI HTF bar inayoizunguka (future info) — inatumia bar iliyoFUNGWA kabla.*
## B) HTF context features (H4/D1 -> 15m/30m; as-of BACKWARD, no-lookahead)

*2026-07-15 20:34 | features: ema_slope/linreg_slope/trend_sign (trend), vol_state/act_state (regime), dist_res_atr/dist_sup_atr (structure, rolling S/R 20 closed bars), rsi14/roc10 (momentum) | join: close_ts=ts+duration, backward*

| Pair | LTF | context bars |
|------|-----|--------------|
| EURUSD | H1 | 62,951 |
| GBPUSD | H1 | 62,953 |
| USDJPY | H1 | 62,968 |
| EURJPY | H1 | 62,966 |
| USDCAD | H1 | 62,952 |
| USDCHF | H1 | 62,955 |
| AUDUSD | H1 | 62,964 |
| NZDUSD | H1 | 62,964 |
| EURGBP | H1 | 62,961 |
| GBPJPY | H1 | 63,448 |
| EURCHF | H1 | 63,468 |
| XAUUSD | H1 | 60,436 |

*No-lookahead: self-test ya MTEGO (htf_context [2]) inathibitisha context ya LTF bar HAIONI HTF bar inayoizunguka (future info) — inatumia bar iliyoFUNGWA kabla.*