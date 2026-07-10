# Market State Engine v1 — pairs ZOTE × TF ZOTE (PHASE 1, CQ-003)

*2026-07-10 22:01 | TF: H1, H2, H4, D1 | DESEASONALIZED (saa-ya-siku, trailing 60) | vol/activity terciles 0.33/0.67 (~mwaka 1/TF) | spread RANK top 15% (trailing 750) | no-lookahead*

> ⚠️ **STATE LAYER v1 (building blocks) — SIO regime engine ya mwisho.** States ni vipengele; regime za kweli (Compression/Expansion/Transition/Shock) + transitions zinajengwa baadaye. Labels RELATIVE kwa mwaka uliopita (no-lookahead).

## A) State distribution (% ya bars) + persistence (run length)

| Pair | TF | n | vol L/N/H | act L/N/H | spr WIDE | persist v/a/s |
|------|----|---|-----------|-----------|----------|---------------|
| XAUUSD | H1 | 58,684 | 33/34/34 | 33/34/33 | 15% | 12/3/9 |
| XAUUSD | H2 | 30,856 | 33/34/34 | 33/34/33 | 17% | 12/3/8 |
| XAUUSD | H4 | 16,043 | 33/33/34 | 33/33/33 | 16% | 10/2/7 |
| XAUUSD | D1 | 3,123 | 34/32/34 | 34/33/33 | 17% | 8/2/5 |

## B) ABSOLUTE distributions (pair individuality — GAP 3)

*Terciles huzalisha ~33/33/33 kila pair; hapa ndipo tofauti HALISI za pair zinaonekana.*

| Pair | TF | median ATR (pips) | median spread (pips) | median ticks/bar |
|------|----|-------------------|----------------------|------------------|
| XAUUSD | H1 | 404.8 | 35.00 | 6,178 |
| XAUUSD | H2 | 567.6 | 35.00 | 11,948 |
| XAUUSD | H4 | 808.1 | 35.00 | 22,914 |
| XAUUSD | D1 | 1991.4 | 35.00 | 138,400 |

---
*STATE v1: deseasonalized (saa) -> states za HALI YA SOKO sio saa. vol/activity = rolling terciles (relative, no-lookahead). spread = RANK-based (tie/aggregation-robust, TF-invariant — inarekebisha GAP 2). Absolute median (pips) = pair individuality (GAP 3). Inayofuata: volume_bars -> regime_transition_report. Metric rasmi = Expected Value (CQ-008).*