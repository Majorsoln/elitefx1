# M4-2 — GBM CV + threshold sweep (sl2tp1) — **LESSON**

*2026-08-01 20:39 | spec: docs/M4_2_REGISTRATION.md (§3 vigezo VILIVYOSAJILIWA kabla ya model) | data: M4-1 TRAIN PEKEE, rows 1,025,338 | purged+embargoed CV folds 5 | OOF predictions PEKEE | metric = EV_R (SI accuracy/AUC)*

> **Bwawa bila uteuzi:** N=1,025,338 · win=65.96% · EV_R=-0.0470

> **Vigezo (§3):** EV_R > **+0.0328** (breadth VALID) NA trades/mwaka ≥ **854** NA p_boot < 0.05 NA folds ≥ 4/5

> **Baseline ya ndani (nr7_flag-only, bila ML):** N=182,014 · EV_R=-0.0449 · trades/mwaka=26044.4 — ML lazima izidi hii pia, si bwawa lote tu.


## Threshold sweep (OOF)

| top-q | threshold P(win) | N | EV_R | win% | trades/mwaka | p_boot | folds>breadth | c1 EV | c2 N/yr | c3 p | c4 folds | **PASS** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20.000% | 0.6747 | 205,068 | -0.03084 | 67.3 | 29339.4 | 1.0 | 0/5 | ✗ | ✓ | ✗ | ✗ | — |
| 10.000% | 0.6844 | 102,534 | -0.02801 | 67.5 | 14669.7 | 1.0 | 0/5 | ✗ | ✓ | ✗ | ✗ | — |
| 5.000% | 0.6936 | 51,267 | -0.02520 | 67.7 | 7334.9 | 1.0 | 0/5 | ✗ | ✓ | ✗ | ✗ | — |
| 2.000% | 0.7057 | 20,507 | -0.03379 | 66.9 | 2935.0 | 1.0 | 0/5 | ✗ | ✓ | ✗ | ✗ | — |
| 1.000% | 0.7155 | 10,254 | -0.04343 | 66.0 | 1472.2 | 1.0 | 0/5 | ✗ | ✓ | ✗ | ✗ | — |
| 0.500% | 0.7267 | 5,127 | -0.06546 | 64.2 | 741.0 | 1.0 | 1/5 | ✗ | ✗ | ✗ | ✗ | — |
| 0.200% | 0.7447 | 2,051 | -0.05334 | 64.6 | 303.9 | 0.996616 | 3/5 | ✗ | ✗ | ✗ | ✗ | — |
| 0.100% | 0.7584 | 1,026 | -0.07526 | 63.0 | 152.0 | 0.9956 | 2/5 | ✗ | ✗ | ✗ | ✗ | — |

## Per-fold EV_R (uthabiti — anti-cherry-picking)

| top-q | fold 0 | fold 1 | fold 2 | fold 3 | fold 4 |
|---|---|---|---|---|---|
| 20.000% | -0.0269 | -0.0049 | -0.0489 | -0.0434 | -0.0273 |
| 10.000% | -0.0278 | -0.0008 | -0.0551 | -0.0427 | -0.0071 |
| 5.000% | -0.0344 | +0.0118 | -0.0563 | -0.0375 | +0.0096 |
| 2.000% | -0.0541 | +0.0046 | -0.0569 | -0.0280 | +0.0110 |
| 1.000% | -0.0736 | -0.0151 | -0.0186 | -0.0352 | +0.0159 |
| 0.500% | -0.0851 | -0.0580 | -0.0312 | -0.0754 | +0.0536 |
| 0.200% | -0.0788 | -0.1222 | +0.1041 | +0.0892 | +0.1846 |
| 0.100% | -0.0964 | -0.3766 | +0.1877 | +0.0036 | +0.2752 |

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