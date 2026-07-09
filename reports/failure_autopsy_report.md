# Failure Autopsy — walioshindwa S2 walikwama WAPI? (directive ya PD)

*2026-07-09 17:47 | cells 2004 (TRAIN ccfbb24 + VALID e1a0d27) | HOLDOUT: SEALED, haitumiki | p-nominal=0.05 | costs approx = net + spread(pair) + slip*

> **NIDHAMU:** diagnosis hii inatumia TRAIN+VALIDATION tu. Hypothesis yoyote mpya itakayozaliwa hapa inahitaji OOS MPYA (data ya 2026-05+ / forward) — 2023-24 imeshatumika kwa selection, HAIWEZI kuthibitisha watoto wake (LESSON-002).


## 1) Vizuizi — hesabu kuu

| Kizuizi | Cells | % | Maana |
|---------|-------|---|-------|
| SURVIVOR | 1 | 0.0% | PASS — STRAT-001 |
| B3a_FDR_TAX | 87 | 4.3% | nominal PASS (EV>0, p<0.05) — aliuawa na kodi ya multiplicity, SIO na soko |
| B3b_UNDERPOWERED | 429 | 21.4% | mwelekeo ulishikilia OOS (EV>0) — power/sampuli haikutosha |
| B2_MIRAGE | 370 | 18.5% | TRAIN chanya, VALID hasi — in-sample illusion (LESSON-001) |
| B4_DEAD | 1052 | 52.5% | hasi pande zote — mechanism haifanyi kazi kwenye context hiyo |
| B5_STARVED | 65 | 3.2% | hakufika N=30 kwenye VALID — filters kali mno kwa miaka 2 |
| *(tag)* COST-KILLED | 324 | 16.2% | gross>0 pande zote, costs ziliua net — soko lilitoa, gharama zikala |

## 2) Kizuizi kwa event (cells)

| event | B3a | B3b | B2 | B4 | B5 | COST |
|-------|----|----|----|----|----|----|
| nr7_break | 86 | 252 | 196 | 86 | 27 | 192 |
| second_chance | 0 | 34 | 64 | 32 | 14 | 23 |
| lowvol_reversal | 0 | 7 | 9 | 92 | 0 | 10 |
| trend_resume | 0 | 0 | 5 | 103 | 0 | 2 |
| mr_zscore | 0 | 20 | 3 | 85 | 0 | 29 |
| bb_fade | 0 | 12 | 4 | 92 | 0 | 24 |
| big_range_mo | 0 | 6 | 0 | 102 | 0 | 5 |
| pullback_v2 | 0 | 4 | 1 | 103 | 0 | 8 |
| engulf_extreme | 0 | 28 | 0 | 80 | 0 | 3 |
| pattern_3lows | 0 | 7 | 0 | 101 | 0 | 11 |
| shock_follow | 1 | 38 | 27 | 6 | 24 | 4 |
| session_orb | 0 | 7 | 25 | 40 | 0 | 5 |
| breakout_stop | 0 | 0 | 2 | 52 | 0 | 0 |
| jump_off | 0 | 0 | 0 | 54 | 0 | 0 |
| inside_break | 0 | 9 | 25 | 14 | 0 | 5 |
| rsi2_pullback | 0 | 5 | 9 | 10 | 0 | 3 |

## 3) 'Waliojeruhiwa' bora (B3a/B3b — mwelekeo ulishikilia OOS; wagombea wa re-test kwa OOS MPYA)

| kizuizi | event | pair | SL | TP | session | vol | VALID EV | p | N(V) | TRAIN EV |
|---------|-------|------|----|----|---------|-----|----------|---|------|----------|
| B3a | nr7_break | USDCHF | 1.5 | 1.0 | no-LATE | None | +2.31 | 0.0002 | 432 | +0.43 |
| B3a | nr7_break | USDJPY | 1.0 | 1.0 | no-LATE | None | +4.05 | 0.0007 | 444 | +1.98 |
| B3a | nr7_break | USDCHF | 2.0 | 1.0 | ['LONDON', 'NY'] | None | +4.29 | 0.0009 | 116 | +3.37 |
| B3a | nr7_break | USDJPY | 1.0 | 1.0 | ['LONDON', 'NY'] | None | +4.76 | 0.0017 | 294 | +1.99 |
| B3a | nr7_break | USDCHF | 2.0 | 1.5 | no-LATE | None | +2.87 | 0.0018 | 399 | +0.74 |
| B3a | nr7_break | USDCHF | 1.5 | 1.0 | ['LONDON', 'NY'] | None | +3.70 | 0.0018 | 117 | +3.27 |
| B3a | nr7_break | USDJPY | 1.0 | 1.0 | None | HIGH | +6.23 | 0.0025 | 261 | +0.52 |
| B3a | nr7_break | EURUSD | 2.0 | 1.5 | no-LATE | None | +3.34 | 0.0026 | 308 | +2.34 |
| B3a | nr7_break | USDJPY | 1.0 | 1.0 | None | None | +2.49 | 0.0033 | 863 | +0.45 |
| B3a | nr7_break | EURUSD | 1.5 | 2.0 | None | None | +2.71 | 0.0039 | 565 | -0.10 |
| B3a | nr7_break | USDCHF | 2.0 | 1.5 | ['LONDON', 'NY'] | None | +4.90 | 0.0040 | 115 | +3.32 |
| B3a | nr7_break | USDJPY | 2.0 | 1.0 | no-LATE | None | +4.56 | 0.0040 | 429 | +1.35 |
| B3a | nr7_break | EURUSD | 1.5 | 1.5 | no-LATE | None | +2.75 | 0.0045 | 317 | +2.52 |
| B3a | nr7_break | EURUSD | 2.0 | 2.0 | None | None | +2.96 | 0.0053 | 537 | -0.06 |
| B3a | nr7_break | USDCHF | 1.0 | 1.5 | ['LONDON', 'NY'] | None | +3.65 | 0.0064 | 116 | +3.10 |
| B3a | nr7_break | GBPUSD | 2.0 | 1.0 | no-LATE | HIGH | +4.68 | 0.0070 | 136 | +2.11 |
| B3a | nr7_break | EURUSD | 1.5 | 1.0 | no-LATE | None | +1.99 | 0.0072 | 334 | +1.99 |
| B3a | nr7_break | EURUSD | 1.5 | 2.0 | no-LATE | None | +3.11 | 0.0072 | 306 | +2.24 |
| B3a | nr7_break | USDJPY | 2.0 | 1.0 | None | None | +3.14 | 0.0083 | 769 | +0.07 |
| B3a | nr7_break | USDCHF | 1.0 | 1.0 | ['LONDON', 'NY'] | None | +2.68 | 0.0088 | 118 | +3.25 |

## 4) Familia-pooled view (logic ya B3: power inapotea kwa kugawanya) — wastani wa VALID EV (cell-level) kwa event

| event | cells VALID EV>0 | jumla | wastani VALID EV |
|-------|------------------|-------|------------------|
| nr7_break | 339 | 621 | +0.761 |
| second_chance | 34 | 130 | -1.396 |
| lowvol_reversal | 7 | 108 | -1.414 |
| trend_resume | 0 | 108 | -2.130 |
| mr_zscore | 20 | 108 | -1.023 |
| bb_fade | 12 | 108 | -1.029 |
| big_range_mo | 6 | 108 | -1.685 |
| pullback_v2 | 4 | 108 | -1.170 |
| engulf_extreme | 28 | 108 | -1.050 |
| pattern_3lows | 7 | 108 | -1.465 |
| shock_follow | 39 | 72 | +0.343 |
| session_orb | 7 | 72 | -2.155 |
| breakout_stop | 0 | 54 | -3.726 |
| jump_off | 0 | 54 | -5.253 |
| inside_break | 9 | 48 | -3.086 |
| rsi2_pullback | 5 | 24 | -1.761 |

## 5) Chief analysis (logic ya kila kizuizi kwa mapana) — angalia sehemu ya CHIEF ANALYSIS iliyoongezwa chini na Chief baada ya kusoma namba.

*Autopsy: TRAIN+VALID tu; holdout SEALED. Hypotheses mpya = OOS mpya. Profitable != Tradable Edge.*
---

# CHIEF ANALYSIS — logic ya kila kizuizi kwa mapana (2026-07-09)

## B3a FDR-TAX (87 cells — 86 ni nr7_break): "waliouawa na hesabu, sio na soko"
Cells 87 zilishinda soko OOS (EV>0, p<0.05 nominal) lakini zikakatwa na kodi ya multiplicity —
kwa sababu tuliwajaribu pamoja na wenzao 1,938, kizingiti cha BH kilipanda juu yao. ANGALIA
muundo wa waliojeruhiwa: karibu WOTE ni **nr7_break + TP 1.0×ATR + no-LATE + USD majors**
(USDCHF/USDJPY/EURUSD) — NDUGU wa moja kwa moja wa STRAT-001. Hii SIYO bahati; ni familia
moja yenye uhai, iliyogawanywa vipande vingi mno vya param, kila kipande kikapoteza power.
LOGIC YA MAPANA: wingi wa hypotheses ni gharama halisi ya takwimu. Uchimbaji ujao lazima
uwe na hypotheses CHACHE, za familia, zilizotajwa mapema.

## B3b UNDERPOWERED (429): "mwelekeo ulishikilia, sampuli haikutosha"
Robo ya grid nzima ilikuwa CHANYA kwenye OOS bila kufikia significance. nr7_break peke yake
= 252. LOGIC: kugawanya familia moja kwenye cells 648 (params × filters) kunazidisha kelele —
kila cell ina N ndogo. REMEDY: (i) pooling ya familia (test moja ya "nr7 inafanya kazi?" badala
ya 648), (ii) grid coarse zaidi (SL/TP chache), (iii) window ndefu za OOS.

## B2 MIRAGE (370): "warembo wa TRAIN waliokufa OOS"
Hii ndiyo LESSON-001 ikipumua: 18.5% ya grid iliangaza in-sample na kuzimika OOS. HAKUNA
remedy — huu ni mfumo UKIFANYA KAZI. Bila S2, tungewapa pesa hawa 370.

## B4 DEAD (1,052 — nusu ya grid): "mechanism isiyofaa kwa context"
Familia zilizokufa KIKAMILIFU kwenye H1 ya majors: **jump_off (54/54), breakout_stop (52/54),
trend_resume (103/108), pullback_v2 (103/108), big_range_mo (102/108), pattern_3lows (101/108)**.
LOGIC YA MAPANA: (a) stop-entry inayokimbiza breakout kwenye H1 ya majors = kununua kwa bei
mbaya zaidi pamoja na umati, huku spread+slippage ikiongezeka — adverse selection safi;
(b) entries za KJ ni za DAILY bars za futures za miaka ya 90-2000; H1 FX majors 2016-2024
ina tabia ya mean-reversion/ranging — trend-following entries hazina mazingira yake hapa.
RULING: familia hizi zina-ARCHIVE kwa evidence (kwa H1 majors) — zinaweza kurudi kwa TF
ya juu (H4/D1) au kwa mazingira mengine, kwa mzunguko mpya wa registration. Kanuni ya
Archived ipo tayari kwenye board ("not deleted — may return with better context").

## B5 STARVED (65): filters kali mno kwa window ya miaka 2 — inaungana na logic ya B3
(kugawanya kupita kiasi). Inafungwa na grid coarse + pooling.

## COST-KILLED tag (324; nr7=192): "soko lilitoa, gharama zikala"
Gross EV chanya pande ZOTE mbili lakini net hasi. Ushahidi wa wazi: nr7 inaishi kwenye pairs
za spread nyembamba (EURUSD 0.3, USDJPY 0.4, USDCHF 1.0) na inakufa USDCAD (1.2)/NZDUSD (1.1).
REMEDIES za mzunguko ujao: (i) H4 variant ya nr7 (ATR kubwa dhidi ya spread ileile — uwiano
wa gharama unashuka nusu), (ii) pairs za spread ya chini tu, (iii) sessions za spread nyembamba.

## HITIMISHO KUU LA AUTOPSY
Soko limesema kwa sauti moja: **mshipa ulio hai kwenye data hii ni COMPRESSION→EXPANSION
(nr7: familia-pooled VALID EV +0.76 juu ya cells 621) na kwa mbali SHOCK-FOLLOW (+0.34).**
Familia nyingine ZOTE zina wastani hasi. Uchimbaji ujao unaelekezwa kwenye mshipa huu:
nr7 variants (H4; NR4; inside+NR7; multi-bar squeeze), shock_follow refinement, kwa
hypotheses CHACHE zilizotajwa mapema, OOS mpya, na FDR ndogo (m=idadi halisi).

*Chief Quant (Unified). Hypotheses mpya = OOS mpya. Profitable != Tradable Edge.*
