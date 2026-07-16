# WAVE-B — S1 TRAIN (HM-02+HM-05 grid FROZEN m=36)

*2026-07-16 12:22 | TF=15m/30m | split=TRAIN (2016-2022 PEKEE) | cells=36 | context ON signals (_mask_context_dir, signal-bar i; NaN→excluded) | costs ndani ya episodes (spread+slip) | MIN_N=30*

> **UAMINIFU:** S1 = TRAIN EXPLORATION — hakuna p-value/FDR hapa; namba zote ni in-sample. Uthibitisho = S2 (family-pooled + BH-FDR kwenye VALIDATION) → C2-6 freeze → HOLDOUT one-shot. LESSON-001/002/029. Profitable != Tradable Edge.


## Muhtasari kwa hypothesis

| hypothesis | cells | cells N>=MIN_N | jumla N | EV>0 cells | median EV net | median cost_share |
|------------|-------|----------------|---------|------------|----------------|--------------------|
| HM-02 LONDON-ORB-D1 | 20 | 20 | 24,718 | 0/20 | -2.666 | — |
| HM-05 ALIGNED-SHOCK | 16 | 16 | 13,079 | 4/16 | -1.611 | 3.23 |

## Candidates zenye EV_net>0 (N>=MIN_N; in-sample TRAIN — SI survivors)

| hypothesis | trigger | pair | SL | TP | N | EV net | gross | cost_share | win% | PF | timeout% |
|------------|---------|------|----|----|---|--------|-------|------------|------|----|----------|
| HM-05 | shock_follow | USDJPY | 1.5 | 2.0 | 730 | +1.263 | +1.708 | 0.2606 | 48.9 | 1.215 | 7 |
| HM-05 | shock_follow | USDJPY | 1.0 | 2.0 | 730 | +1.114 | +1.559 | 0.2856 | 39.9 | 1.23 | 4 |
| HM-05 | shock_follow | USDJPY | 1.5 | 3.0 | 725 | +0.709 | +1.155 | 0.3861 | 40.6 | 1.104 | 17 |
| HM-05 | shock_follow | USDJPY | 1.0 | 3.0 | 729 | +0.568 | +1.013 | 0.4395 | 31.4 | 1.102 | 10 |

*Cells chanya: 4/36. Next: S2 = kila hypothesis kama FAMILY moja (pool R, mtindo wa family_pooled) kwenye VALIDATION + BH-FDR (Chief). Grid frozen — hakuna cell mpya baada ya hapa.*