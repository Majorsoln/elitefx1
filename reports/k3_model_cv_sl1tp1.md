# M4-2 — GBM CV + threshold sweep (sl1tp1) — **LESSON**

*2026-08-01 20:46 | spec: docs/M4_2_REGISTRATION.md (§3 vigezo VILIVYOSAJILIWA kabla ya model) | data: M4-1 TRAIN PEKEE, rows 1,025,338 | purged+embargoed CV folds 5 | OOF predictions PEKEE | metric = EV_R (SI accuracy/AUC)*

> **Bwawa bila uteuzi:** N=1,025,338 · win=49.25% · EV_R=-0.1019

> **Vigezo (§3):** EV_R > **+0.0526** (breadth VALID) NA trades/mwaka ≥ **890** NA p_boot < 0.05 NA folds ≥ 4/5

> **Baseline ya ndani (nr7_flag-only, bila ML):** N=182,014 · EV_R=-0.1052 · trades/mwaka=26044.4 — ML lazima izidi hii pia, si bwawa lote tu.


## Threshold sweep (OOF)

| top-q | threshold P(win) | N | EV_R | win% | trades/mwaka | p_boot | folds>breadth | c1 EV | c2 N/yr | c3 p | c4 folds | **PASS** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20.000% | 0.5080 | 205,068 | -0.07244 | 50.9 | 29339.4 | 1.0 | 0/5 | ✗ | ✓ | ✗ | ✗ | — |
| 10.000% | 0.5194 | 102,534 | -0.06480 | 51.6 | 14669.7 | 1.0 | 0/5 | ✗ | ✓ | ✗ | ✗ | — |
| 5.000% | 0.5310 | 51,267 | -0.05540 | 52.3 | 7337.4 | 1.0 | 0/5 | ✗ | ✓ | ✗ | ✗ | — |
| 2.000% | 0.5458 | 20,507 | -0.03867 | 53.2 | 2935.0 | 1.0 | 0/5 | ✗ | ✓ | ✗ | ✗ | — |
| 1.000% | 0.5560 | 10,254 | -0.02953 | 53.5 | 1467.6 | 0.983598 | 0/5 | ✗ | ✓ | ✗ | ✗ | — |
| 0.500% | 0.5653 | 5,127 | -0.03513 | 52.9 | 733.8 | 0.95719 | 0/5 | ✗ | ✗ | ✗ | ✗ | — |
| 0.200% | 0.5790 | 2,051 | -0.02805 | 53.0 | 293.7 | 0.796247 | 1/5 | ✗ | ✗ | ✗ | ✗ | — |
| 0.100% | 0.5901 | 1,026 | -0.03982 | 52.2 | 147.0 | 0.79552 | 1/5 | ✗ | ✗ | ✗ | ✗ | — |

## Per-fold EV_R (uthabiti — anti-cherry-picking)

| top-q | fold 0 | fold 1 | fold 2 | fold 3 | fold 4 |
|---|---|---|---|---|---|
| 20.000% | -0.0524 | -0.0502 | -0.0940 | -0.0684 | -0.0955 |
| 10.000% | -0.0496 | -0.0268 | -0.0826 | -0.0701 | -0.0892 |
| 5.000% | -0.0425 | -0.0197 | -0.0591 | -0.0646 | -0.0838 |
| 2.000% | -0.0216 | -0.0128 | -0.0380 | -0.0568 | -0.0612 |
| 1.000% | +0.0054 | -0.0208 | -0.0483 | -0.0527 | -0.0539 |
| 0.500% | -0.0009 | -0.0652 | -0.0243 | -0.0840 | -0.0528 |
| 0.200% | +0.0072 | -0.0800 | -0.0290 | -0.1638 | +0.1031 |
| 0.100% | +0.0410 | -0.1342 | -0.1357 | -0.1849 | +0.2252 |

## VERDICT: **LESSON**

Hakuna threshold iliyotimiza vigezo VYOTE vinne vya §3. Kwa mujibu wa charter §5, hii ni **LESSON** — na **HATUA 2 (LSTM) HAIANZI**.

Kilichoshindikana kwa kila threshold kimeandikwa kwenye safu c1-c4 hapo juu (uwazi: si 'karibu kufaulu' — ni kigezo gani hasa).

## Caveats

1. **CV ndani ya TRAIN pekee.** Hakuna madai ya OOS hapa; VALIDATION haijaguswa.
2. **OOF PEKEE** kwenye sweep — hakuna in-sample prediction inayoingia kwenye namba.
3. **Purge + embargo** zimetumika (labels zinapishana hadi max_hold). Bila hizo, EV yoyote ya CV ingekuwa ya uongo.
4. Threshold sweep juu ya OOF ni **uteuzi**: EV ya threshold iliyochaguliwa ni hot kidogo. Ndiyo maana VALIDATION ni eval MOJA baada ya freeze (registration §4.3-§4.4).
5. Artifact = JSON tree dump; inference = pure-numpy (`score_json`) — live haitegemei LightGBM. Self-test [3] inathibitisha parity.

*Profitable != Tradable Edge. Protect capital first.*