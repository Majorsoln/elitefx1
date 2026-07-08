# RUNBOOK — Forward Paper-Trading (mkutano wa MWONGOZO na mashine)

*Chief Quant (Unified) → Operator | 2026-07-07 | Directive ya Project Director; protocol
doctrine-compliant (FORWARD, si replay) | Paper — HAKUNA pesa halisi.*

## Kwa nini FORWARD (na si replay ya historia)

Replay ya 2016–2024 kwa policies illustrative = PnL ya uongo (LESSON-001/002/029; Chapter 1:
0/282 FDR). **Forward** = kila decision inarekodiwa KABLA matokeo hayajajulikana → hakuna lookahead,
hakuna selection bias — **pre-registered by construction**. Matokeo yake ni evidence HALALI, na
rekodi zake (E3) ndizo chakula cha K6/K4 (training data ya kweli).

## Protocol (baada ya `paper_trader.py` kukamilika — IMPLEMENTER-A anajenga)

Kila unapoona signal kwa MWONGOZO wako (badala ya checklist ya mkono):

```bash
# 1. Fungua paper-trade: mashine ina-decide + gate (FTMO) + size + paper-fill + rekodi
python paper_trader.py --signal EURUSD BUY 1.0850 1.0830 1.0910 --policy conservative

# 2. Trade ikifungwa (SL/TP/mkono) — rekodi settlement na PnL halisi ya paper
python paper_trader.py --close <order_id> --price 1.0905

# 3. Hali ya akaunti ya paper (bajeti ya siku, slots, daily loss — MWONGOZO §1)
python paper_trader.py --status
```

**Kila rekodi:** decision→gate→execution→settlement, append-only (`data/paper/paper_log.jsonl`),
committed git (immutable public pre-registration). FTMO checks 5 + DailyRiskBudgetSizer = mashine,
si karatasi.

## Kanuni za tathmini (kabla hazijaanza)

1. Kipindi cha chini kabla ya hitimisho lolote: **siku 20+ za biashara / trades 30+**.
2. Hakuna kubadilisha policy/thresholds katikati bila kurekodi version mpya (P88).
3. Mwisho wa kipindi: Chief anafanya tathmini rasmi (win rate, EV, max DD, FTMO compliance) —
   na hata ikiwa NZURI, bado ni sample ndogo; live inahitaji + uamuzi wa Project Director.
4. ABSTAIN/REJECTED nyingi = mfumo unafanya kazi, si kushindwa.

*Profitable ≠ Tradable Edge. Protect capital first.*
