# K4 MODEL v0 — CV REPORT (TRAIN blocked leave-one-year-out; design k4_model_design.md)

*folds=7 (2016-2022) | purge 24h | grid 16 + prune-once | decision=ΔEV_R@70% | boot mb=3 B=10,000 | H0=hakuna lift; criterion §4: dev>0 & p<0.05 & dev>=+0.05R & ev-ret>=0.9*

> **H0 = HAKUNA lift** (design §0). 'NO-LIFT' ni matokeo halali (LESSON), si kushindwa. VALID HAIJAGUSWA hapa (eval MOJA baada ya freeze). Accuracy si decision (marufuku §D).


## STRAT-001

- **winner:** `{'kind': 'logistic', 'C': 0.1, 'fs': 'FULL'}` (pruned: none)
- **ΔEV_R@70% = +0.0157 R** | p_boot=0.08709 (CI [-0.00316, 0.03474]) | EV-retention=2.5368 | pstar=0.67292 | AUC=0.5257 (diagnostic) | N=1607
- loss-streak (max/P95): all=6/3.0 -> filtered=4/3.0
- **VERDICT ya H0: FAIL-TO-REJECT (NO-LIFT)** (criterion §4).

## STRAT-002

- **winner:** `{'kind': 'tree', 'depth': 2, 'min_leaf': 100, 'fs': 'CORE'}` (pruned: none)
- **ΔEV_R@70% = +0.0037 R** | p_boot=0.40186 (CI [-0.02151, 0.02908]) | EV-retention=0.7202 | pstar=0.57426 | AUC=0.5028 (diagnostic) | N=1746
- loss-streak (max/P95): all=7/4.0 -> filtered=9/4.0
- **VERDICT ya H0: FAIL-TO-REJECT (NO-LIFT)** (criterion §4).

*Next: CV-PASS -> Chief ruling -> --freeze (commit) -> --eval-valid (one-shot). CV-FAIL -> LESSON 'no deployable lift v0'. Profitable != Tradable Edge.*