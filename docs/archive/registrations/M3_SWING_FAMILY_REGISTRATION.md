# M3-3 — SWING FAMILY #1: nr7_break × D1 × LOW-vol — S2 REGISTRATION (FROZEN by Chief, 2026-07-17)

> Chanzo: ATLAS (TRAIN) + Q4-screen ya auditor (breadth 10/12 pairs NA miaka 7/7 EV+ — combo
> PEKEE iliyofikia viwango vyote viwili; auditor mwenyewe aliiita "umbo la lesson halali").
> Mechanism = compression-continuation @ D1 — familia ile ile ya STRAT-001/002, swing (hoja ya
> PD). Jiometri SL2/TP1 = ile ile ya STRAT-001 (high-win). Kinga ya L-041: **pairs ZOTE 12
> pooled kwa R** (hakuna pair-selection). FROZEN kabla ya kufungua VALIDATION.

## FAMILY SPEC (FROZEN)
| Kipengele | Thamani |
|---|---|
| Event | `nr7_break` (stop, OCO — kama STRAT-001/002; hakuna direction filter) |
| TF | **D1** |
| Context filter | `volatility_state == "LOW"` ya SIGNAL bar (D1 bar yenyewe; trailing/deseasonalized — decidable). UNKNOWN → excluded (Q1) |
| SL × TP | **2.0 × 1.0** (moja tu — top-pooled TRAIN + jiometri ya STRAT-001; hakuna param grid S2) |
| max_hold | 20 bars za D1 (~wiki 4) |
| Costs | spread + slip 0.3 (stop) + **swap** (nights × swap_pips config) |
| Pairs | **ZOTE 12 pooled** (R-normalized streams, mtindo wa `family_pooled` — gold haitawali kwa R-units) |
| TRAIN rejea | pooled N=384, per-pair 10/12 EV+, miaka 7/7 EV+ (atlas; R-pooled itahesabiwa upya na runner) |

## TEST RASMI (S2 VALIDATION 2023-2024)
- Pool R-streams za pairs 12 → stream MOJA ya family (kama family_pooled: _r_normalize + ordering
  kwa ts). Kadirio la N_valid ≈ 110 (384 × 2/7).
- `pvalue_boot` (B=50k, mean_block=3, engine RASMI) juu ya pooled stream; **criterion:
  p_boot < 0.05 NA EV_R > 0** (m=1 — family moja, hakuna FDR budget ya kuchoma).
- p_z sensitivity. VALIDATION ina-consumed kwa family hii. HOLDOUT HAIGUSWI (C2-6 token).

## Matokeo yanayowezekana (yote halali)
- **PASS** → C2-6 freeze → HOLDOUT one-shot (dirisha bikira D1 2025-01→2026-04) → ikipita =
  **STRAT-003** (swing high-win family, trades ~50-55/mwaka portfolio-wide).
- **FAIL** → LESSON; C2-WATCH-style forward-only. Tahadhari za wazi: N_valid ~110 → power ya
  wastani; Q7 (swap band) inabanwa na R-pooling + ukubwa wa per-pair EVs (wengi >>10 pips).
