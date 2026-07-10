# Market State Engine v1 — pairs ZOTE × TF ZOTE (PHASE 1, CQ-003)

*2026-07-10 20:32 | TF: H1, H2, H4, D1 | DESEASONALIZED (saa-ya-siku, trailing 60) | vol/activity terciles 0.33/0.67 (~mwaka 1/TF) | spread RANK top 15% (trailing 750) | no-lookahead*

> ⚠️ **STATE LAYER v1 (building blocks) — SIO regime engine ya mwisho.** States ni vipengele; regime za kweli (Compression/Expansion/Transition/Shock) + transitions zinajengwa baadaye. Labels RELATIVE kwa mwaka uliopita (no-lookahead).

## A) State distribution (% ya bars) + persistence (run length)

| Pair | TF | n | vol L/N/H | act L/N/H | spr WIDE | persist v/a/s |
|------|----|---|-----------|-----------|----------|---------------|
| EURCHF | H1 | 61,716 | 32/34/34 | 33/33/34 | 18% | 14/2/6 |
| EURCHF | H2 | 31,231 | 32/34/34 | 33/33/34 | 18% | 13/2/5 |
| EURCHF | H4 | 16,179 | 32/34/34 | 33/33/34 | 17% | 10/2/5 |
| EURCHF | D1 | 3,152 | 33/34/33 | 33/32/35 | 14% | 9/2/4 |

## B) ABSOLUTE distributions (pair individuality — GAP 3)

*Terciles huzalisha ~33/33/33 kila pair; hapa ndipo tofauti HALISI za pair zinaonekana.*

| Pair | TF | median ATR (pips) | median spread (pips) | median ticks/bar |
|------|----|-------------------|----------------------|------------------|
| EURCHF | H1 | 9.3 | 1.00 | 2,216 |
| EURCHF | H2 | 13.1 | 1.05 | 4,445 |
| EURCHF | H4 | 18.3 | 1.08 | 8,697 |
| EURCHF | D1 | 42.6 | 1.18 | 52,708 |

---
*STATE v1: deseasonalized (saa) -> states za HALI YA SOKO sio saa. vol/activity = rolling terciles (relative, no-lookahead). spread = RANK-based (tie/aggregation-robust, TF-invariant — inarekebisha GAP 2). Absolute median (pips) = pair individuality (GAP 3). Inayofuata: volume_bars -> regime_transition_report. Metric rasmi = Expected Value (CQ-008).*