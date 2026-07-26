# ELITEFX — KAIROS EA (MQL5) — "DEPLOY + BACKTEST NDANI YA MT5" (directive ya PD 2026-07-26)

> PD: "tumalize development, deploy kwenye local PC, nione ikifanya kazi kiuhalisia, PIA iwe na uwezo
> wa backtest kwenye MT5 Strategy Tester." KAIROS EA = Expert Advisor ya MQL5 inayotekeleza STRAT-001/002
> ndani ya MT5 yenyewe — Strategy Tester (backtest) + chart (demo/live trading).

## LENGO
Expert Advisor MOJA (MQL5), parameterized, inayotekeleza mkakati uleule uliothibitishwa (nr7 + SL/TP +
no-LATE + ATR14), ili: (1) **backtest ndani ya MT5 Strategy Tester** (chombo cha PD); (2) **trade demo
kwenye chart** (unaona kwenye terminal); (3) baadaye live (akaunti halisi = SAINI YA PD, §9/§3.1b Faza 4).

## STRATEGY (port HALISI kutoka Python — parity ni LAZIMA, GIGO)
Chanzo cha ukweli (soma + port BILA kubadilisha): `src/research/event_library_v2.nr7_break`,
`event_quality_report` (SESSIONS/_sess, SL/TP semantics, wilder_atr), `live_engine.STRATS`.
- **nr7 (compression):** range(bar) = high−low; kama range ≤ MIN(range za bars 7 zilizofungwa) →
  compression. Buy-stop = high(bar) + tick; Sell-stop = low(bar) − tick (OCO — moja ikifika, futa nyingine).
- **no-LATE:** server-hour ya bar ya signal LAZIMA iwe 0–16 (ASIA/LONDON/NY). 17–23 (LATE) = HAKUNA entry.
- **ATR:** Wilder ATR(14). SL/TP kwa ATR ya bar ya entry.
- **Variants (input, si EA mbili):** KAIROS-1 = USDCHF, SL=2.0×ATR, TP=1.0×ATR · KAIROS-2 = USDJPY,
  SL=1.0×ATR, TP=1.0×ATR. (Attach EA kwenye chart husika na weka inputs.)
- **Risk/compliance:** risk-per-trade %, max positions, daily-loss guard (FTMO-style, deterministic).
  Position moja kwa wakati per symbol; magic number per instance.

## PARITY (LAZIMA — vinginevyo ni strategy tofauti)
EA iandike **signal-log** (per closed bar: ts, range, rmin7, nr(bool), atr, session, long_level,
short_level) → faili. Harness ya Python (mpya, ndogo) inalinganisha na `nr7_break`+`wilder_atr`+`_sess`
kwenye bars zilezile → levels/atr/session LAZIMA zifanane (ndani ya tolerance ya rounding). Parity FAIL
= EA si sahihi, hairuhusiwi kusonga.

## MIPAKA
- **Backtest ya MT5 Strategy Tester ≠ Python backtest** (fill/spread/tick data tofauti) → ni CROSS-CHECK,
  si replica. Kigezo: EV chanya + tabia inayolingana kimwelekeo. Tofauti kubwa → chunguza (fill/spread).
- **LIVE (akaunti halisi) = Faza 4:** inahitaji SAINI YA PD (§3.1b/§9). Demo = salama, hakuna saini.
- **IP:** EA hii ina strategy logic (kwa matumizi ya PD/local — IP yake mwenyewe). Conduit-EA isiyo na
  logic (kwa LESSEE, §9) = kazi tofauti ya baadaye. Hazichanganywi.

## AWAMU
1. **EA-1:** KAIROS.mq5 (nr7+no-LATE+ATR14+SL/TP+risk+OCO) + signal-log. Inaandaliwa kwa Strategy Tester
   NA chart. (Agent inaandika .mq5; PD anacompile MetaEditor.)
2. **EA-2:** parity harness (Python) — thibitisha EA signals = Python. + deploy/backtest guide (RUNBOOK).

## MATOKEO
PD anadeploy KAIROS EA kwenye PC: (a) Strategy Tester backtest (anaona matokeo mwenyewe kwenye chombo
chake); (b) demo chart (anaona AI ikitrade kwenye terminal). Parity inahakikisha ni mkakati uleule
uliothibitishwa. Njia → VPS demo → live (saini ya PD).
