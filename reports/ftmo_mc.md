# FTMO Monte Carlo — calendar-day + cross-pair (SAHIHI)

*Imezalishwa: 2026-06-21 09:08 | pairs: EURGBP, EURUSD | risk 1%/trade | trades=76, trade-days=76 | N=5000 | block=5 siku | TRAIN 2016-2024 (in-sample)*

> Daily-loss = JUMLA ya P&L kwa siku ya kalenda (-5%). Total = -10% static dhidi ya initial. Target +10%. Block ya SIKU = cross-pair corr ya siku ileile inahifadhiwa (fix #3). Hakuna time-limit; cap MAX_DAYS=1000.

## Matokeo (mbinu SAHIHI)

- **FTMO pass-rate: 91.2%**
- median trade-days → pass: 51  (≈ 6.0 miaka kwa ~8 trade-days/mwaka)
- breach breakdown: daily 0.0% | total 8.8% | timeout(no pass) 0.0%

## Kulinganisha: mbinu YA ZAMANI (BUG #2 — per-trade = siku, IID)

- pass-rate ya zamani: 78.2%  → tofauti na sahihi: -13.0 pp
- *Mbinu ya zamani ilikadiria daily-loss kimakosa (trade moja = siku) na ilipuuza cross-pair correlation -> pass-rate isiyoaminika.*

---
*FTMO MC sahihi: P&L kwa SIKU ya kalenda (daily-loss halisi), total static, block ya siku (cross-pair corr). Trades = validate_real (strategy halisi, R-unit=SL). Hii ni IN-SAMPLE: pass-rate ya juu HAITHIBITISHI edge — angalia validate_real OOS + Phase B kwanza. Kama edge haipo (EV≤0), MC ni mazoezi ya nadharia tu.*