# Validate REAL strategy — Phase B (unified, no-lookahead)

*Imezalishwa: 2026-06-21 09:08 | fade + tp_mean/2ATR-SL/timeout (= deployment) | rolling-q80 threshold (PAST) | R-unit=2ATR | null=random-entry+same-exit, N=3000 | 2025+ HAIJAGUSWA hadi mwisho*

> p = P(fade kwenye bars random + exit ileile ≥ real). p<0.05 = KUCHAGUA extremes kunaongeza edge.

| Pair | Window | n | EV(R) | PF | win% | Phase B p | verdict |
|------|--------|---|-------|----|------|-----------|---------|
| EURGBP | TRAIN 16-24 | 45 | +0.328 | 2.02 | 58% | 0.015 | ✅ edge |
| EURGBP | OOS 25+ | 2 | — | — | — | — | ⚪ n<30 |
| EURUSD | TRAIN 16-24 | 31 | -0.156 | 0.71 | 45% | 0.614 | ❌ HAKUNA |
| EURUSD | OOS 25+ | 0 | — | — | — | — | ⚪ n<30 |

---
*Phase B HALISI: strategy ileile tunayodeploy, null=random-entry+same-exit (inaisolate value ya kuchagua extremes). Rolling threshold = no-lookahead. R-unit=SL (loss=−1R). p iliyoripotiwa ni fraction halisi. ✅ edge inahitaji p<0.05 NA EV>0 — TRAIN na OOS. Hii ndiyo jaribio sahihi: 'kuna edge kweli kwenye tunachocheza?'*