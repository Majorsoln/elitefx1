# RUNBOOK — Event Quality (Entries V1 vs V2) — TRAIN 2016-2022

> **Chief direct (2026-07-08).** Utafiti wa ubora wa ENTRIES kwenye data yako ya miaka 9.
> Script inaKATA yenyewe data za ts >= 2023-01-01 (sacred splits) — VALIDATION/HOLDOUT
> hazisomwi kabisa. Hii ni EXPLORATION inayolisha grid ya S1 — SIO edge claim.

## Kilichoboreshwa (muhtasari wa ukaguzi wa Chief)

| Defect ya V1 | Fix ya V2 |
|--------------|-----------|
| D1: events = CONDITIONS (pullback inawaka 334/1000 bars; sampuli zinazo-overlap; spread kila bar → EV negative kila mahali, Phase 12: 0/5) | **Edge-trigger + rearm** (fire kwenye transition tu) + **episode non-overlap** kwenye harness (position 1 kwa event×pair) |
| D2: uaminifu wa KJ ulipotea (Jump Off #3 haipo; #4 close-confirm badala ya stop; #5 percentile ilipotea; #8 volume filter iliondolewa) | `jump_off`, `breakout_stop` (stop-entry halisi, intrabar), `second_chance` (percentile), `lowvol_reversal` (volume filter kwa `tc`) |
| D3: hakuna time-of-day (FX session structure) | `session_orb` (London opening-range breakout) + jedwali la EV kwa session |
| D4: pockets zilizothibitishwa (MR×EURUSD P100, DPB×EURUSD P97) hazikuwa na toleo kali | `mr_zscore` (ATR-stretch) + `trend_resume` (pullback + resumption bar) |
| D5: KJ 9 si ulimwengu wote wa entries (directive ya PD 2026-07-09) | Mbinu 5 MPYA za familia tofauti: `rsi2_pullback` (Connors MR-ndani-ya-trend), `bb_fade` (band re-entry), `engulf_extreme` (price-action kwenye extreme), `inside_break` + `nr7_break` (compression→expansion) — **jumla entries 16, familia 7** |
| Entries hazikuwa zinapimwa NDANI ya uchambuzi wa soko | Jedwali la 4: kila entry × **volatility state** (market_state_engine — deseasonalized, no-lookahead) + jedwali la 3 (sessions). Entry = trigger; context = uchambuzi |
| Outcome ya Phase 12 = forward 6 bars bila trade structure | Harness: SL/TP za ATR (1.5/1.5), timeout 24 bars, tie→SL (worst case), costs = spread halisi + slippage |

## Hatua (PC yako ya data)

1. `git pull`
2. `cd src\research`
3. `python run_selftests.py`  → tegemeo: **SELF-TEST SWEEP: 14/14 PASS**
4. `python event_quality_report.py`  (pairs zote 9, H1; dakika kadhaa)
5. (hiari) `python event_quality_report.py --tf H4`
6. Bandika/commit `reports/event_quality_report.md` → ripoti kwa Chief: **"tayari event quality"**

## Tegemeo la usomaji

- Sehemu 1: jozi `v1:*` vs `v2:*` — trades/siku zinashuka sana, EV net inapaswa kuboreka
  (kutoka −1..−2 pips kuelekea sifuri au juu kwa baadhi).
- Sehemu 2: rows za juu (event×pair) = wagombea wa grid ya S1.
- Sehemu 3: sessions — kama LONDON/NY >> ASIA, session filter inaingia grid ya S1.
- **HAKUNA row inayoitwa "strategy" kabla ya S2 (walk-forward + FDR) na S3 (holdout, mara moja).**

*Profitable ≠ Tradable Edge. Protect capital first.*
