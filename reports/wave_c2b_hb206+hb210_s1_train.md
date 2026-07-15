# WAVE-B — S1 TRAIN (HB2-06+HB2-10 grid FROZEN m=60)

*2026-07-15 20:34 | TF=H1 | split=TRAIN (2016-2022 PEKEE) | cells=60 | context ON signals (_mask_context_dir, signal-bar i; NaN→excluded) | costs ndani ya episodes (spread+slip) | MIN_N=30*

> **UAMINIFU:** S1 = TRAIN EXPLORATION — hakuna p-value/FDR hapa; namba zote ni in-sample. Uthibitisho = S2 (family-pooled + BH-FDR kwenye VALIDATION) → C2-6 freeze → HOLDOUT one-shot. LESSON-001/002/029. Profitable != Tradable Edge.


## Muhtasari kwa hypothesis

| hypothesis | cells | cells N>=MIN_N | jumla N | EV>0 cells | median EV net | median cost_share |
|------------|-------|----------------|---------|------------|----------------|--------------------|
| HB2-06 HTF-SR-FADE-H1 | 40 | 0 | 348 | — | — | — |
| HB2-10 FAILED-BREAK-SWEEP-H1 | 20 | 20 | 6,638 | 2/20 | -1.323 | 1.06 |

## Candidates zenye EV_net>0 (N>=MIN_N; in-sample TRAIN — SI survivors)

| hypothesis | trigger | pair | SL | TP | N | EV net | gross | cost_share | win% | PF | timeout% |
|------------|---------|------|----|----|---|--------|-------|------------|------|----|----------|
| HB2-10 | false_break | EURCHF | 1.5 | 3.0 | 299 | +1.419 | +2.830 | 0.4984 | 46.2 | 1.178 | 27 |
| HB2-10 | false_break | EURCHF | 1.5 | 2.0 | 303 | +0.888 | +2.296 | 0.6134 | 50.5 | 1.121 | 14 |

*Cells chanya: 2/60. Next: S2 = kila hypothesis kama FAMILY moja (pool R, mtindo wa family_pooled) kwenye VALIDATION + BH-FDR (Chief). Grid frozen — hakuna cell mpya baada ya hapa.*