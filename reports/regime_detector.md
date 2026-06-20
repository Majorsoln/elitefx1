# Model 1 — Regime Detector (vol × structure)

*Imezalishwa: 2026-06-20 08:28 | regime=vol-state×structure-state (median split) | descriptive, no-lookahead | pairs=9*

> Regime 4: LV/HV (vol) × RANGE/TREND (Efficiency Ratio). Hakuna prediction ya direction — ni muktadha kwa Model 2. Thibitisha: (1) persistence, (2) vol-state magnitude.


## D1 (window=20)

**Mgawanyo wa regime (wastani wa pairs):**

| Regime | % time |
|--------|--------|
| LV-RANGE | 23.8% |
| LV-TREND | 26.2% |
| HV-RANGE | 26.2% |
| HV-TREND | 23.9% |

**Persistence:** P(stay) = **0.798** vs baseline (i.i.d.) 0.251 → ✅ persistent (regime inadumu, sio kelele).

**Vol-state magnitude:** mean \|fwd ret\| HIGH-vol = 0.00450 vs LOW-vol = 0.00327 → **1.37×** ✅ (HIGH-vol = moves kubwa zaidi).

## H4 (window=20)

**Mgawanyo wa regime (wastani wa pairs):**

| Regime | % time |
|--------|--------|
| LV-RANGE | 24.5% |
| LV-TREND | 25.5% |
| HV-RANGE | 25.5% |
| HV-TREND | 24.5% |

**Persistence:** P(stay) = **0.815** vs baseline (i.i.d.) 0.250 → ✅ persistent (regime inadumu, sio kelele).

**Vol-state magnitude:** mean \|fwd ret\| HIGH-vol = 0.00174 vs LOW-vol = 0.00120 → **1.45×** ✅ (HIGH-vol = moves kubwa zaidi).

## H1 (window=24)

**Mgawanyo wa regime (wastani wa pairs):**

| Regime | % time |
|--------|--------|
| LV-RANGE | 25.5% |
| LV-TREND | 24.5% |
| HV-RANGE | 24.5% |
| HV-TREND | 25.5% |

**Persistence:** P(stay) = **0.839** vs baseline (i.i.d.) 0.250 → ✅ persistent (regime inadumu, sio kelele).

**Vol-state magnitude:** mean \|fwd ret\| HIGH-vol = 0.00087 vs LOW-vol = 0.00058 → **1.51×** ✅ (HIGH-vol = moves kubwa zaidi).

---
*Regime detector ni msingi wa Model 1 (DOCTRINE §4). Persistence inathibitisha kujua regime ya SASA kunatoa taarifa ya karibu. Vol-state magnitude inathibitisha edge yetu (vol → ukubwa) kwenye ngazi ya regime. Model 2 itatumia regime kama muktadha (mean-reversion kwenye RANGE, n.k.).*