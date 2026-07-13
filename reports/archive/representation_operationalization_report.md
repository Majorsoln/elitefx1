# Representation Operationalization — je manifold inafanya kazi OOS bila leakage? (Phase 21)

*2026-06-30 15:10 | robust normalization + self-tuning spectral | Nyström OOS extension (NO re-fit) | rolling walk-forward 5 folds | landmarks=700 | NO ML*

> **Principle 44 (Chief):** feature normalization ni SEHEMU ya representation, sio preprocessing. **Principle 42/43 (CONFIRMED).** **F-039 (OPEN):** events tofauti zinaweza kuhitaji geometry tofauti. Phase 21: thibitisha representation inafanya kazi PRODUCTION/OOS bila lookahead (fit kwenye PAST tu, project FUTURE kwa Nyström). NO ML.


## Q1 + Q5 — Nyström OOS fidelity & leakage check

| event | Nyström OOS silhouette (no-leak) | joint-fit silhouette (leak) | leak gap | fidelity ARI | N(OOS) |
|-------|--------------------------------|-----------------------------|----------|--------------|--------|
| pullback | 0.585 | 0.913 | +0.328 | 0.93 | 1,500 |
| deep_pullback | 0.452 | 0.780 | +0.328 | 0.49 | 1,500 |
| trend_continuation | 0.640 | 0.835 | +0.194 | 0.96 | 1,500 |
| breakout | 0.613 | 0.830 | +0.218 | 0.77 | 1,500 |
| mean_reversion | 0.596 | 0.824 | +0.227 | 0.95 | 1,500 |

*(fidelity ARI = je Nyström-projected labels zinakubaliana na fresh clustering ya OOS embedding. leak gap kubwa = joint-fit (leakage) inazidi sana proper-Nyström -> in-sample silhouette ilikuwa imeinuliwa na leakage. Q5: hakuna lookahead — fit kwenye PAST tu.)*

> ⚠️ **HEADLINE — leakage iko KILA event (gap +0.194…+0.328, wastani +0.259).** Silhouette za in-sample/joint-fit (wastani **0.836**, kama zile za Phase 20 ~0.58–0.79) zilikuwa **zimeinuliwa na leakage**. Silhouette za kweli za OOS (no-leak, Nyström) ni wastani **0.577** — **chini kwa ~31%**. Manifold inaishi OOS lakini ni dhaifu kuliko Phase 20 ilivyoonyesha.

## Q2 + Q3 — Rolling walk-forward: je geometry inabaki thabiti future?

| event | rolling silhouette (kila fold→inayofuata) | mean | last fold | thabiti? |
|-------|-------------------------------------------|------|-----------|----------|
| pullback | 0.59 → 0.47 → 0.52 → 0.69 | 0.567 | 0.689 | ✅ |
| deep_pullback | 0.70 → 0.63 → 0.67 → 0.66 | 0.663 | 0.658 | ✅ |
| trend_continuation | 0.71 → 0.72 → 0.71 → 0.74 | 0.721 | 0.744 | ✅ |
| breakout | 0.55 → 0.66 → 0.52 → 0.58 | 0.578 | 0.583 | ✅ |
| mean_reversion | 0.64 → 0.51 → 0.63 → 0.63 | 0.604 | 0.634 | ✅ |

## Q4 — Universal au event-specific? (F-039)

- Nyström OOS silhouette range: **0.452 (deep_pullback) … 0.640 (trend_continuation)** (spread 0.189)

→ ✅ event-specific geometry (F-039 inaungwa mkono): events zinatofautiana sana.

## VERDICT — Phase 21 Representation Operationalization

*Vigezo (wazi): **full** = fidelity>0.6 **na** rolling-mean>0.25 **na** leak-gap<0.20; **marginal** = fidelity+stability zimepita ila leak-gap≥0.20 (in-sample ilikuwa imeinuliwa); **fail** = fidelity≤0.6 ama rolling silhouette imeporomoka.*

| daraja | events |
|--------|--------|
| ✅ full operational | trend_continuation |
| 🟡 marginal (leakage-inflated in-sample) | pullback, breakout, mean_reversion |
| ❌ fail | deep_pullback |

→ ✅ **1/5 fully operational** (**trend_continuation**): Nyström inahifadhi structure, rolling silhouette inabaki juu, **na** leak-gap ndogo (in-sample haikuinuliwa sana). 🟡 **3/5 marginal** (pullback, breakout, mean_reversion): fidelity+stability nzuri lakini leak-gap kubwa → namba zao za in-sample zilikuwa leakage-inflated; zinahitaji landmarks/normalization bora kabla ya kuaminiwa. ❌ **1/5 fail** (deep_pullback).

**Next gate:** rebuild taxonomy + OOS edge confirmation **kwa events za 'full' tu**; marginal/fail zinarudi kwa representation work. **Alpha Discovery Era haijafunguliwa** hadi edge ithibitike (sio geometry tu).

## Honest Caveats (kabla ya hitimisho)

1. **Silhouette ≠ edge (Principle 40).** Phase hii inathibitisha representation ni stable + projectable OOS bila leakage — **haionyeshi alpha hata kidogo.** Geometry nzuri sio edge ya kibiashara.
2. **Hakuna OOS permutation-null baseline.** Phase 20 ililinganisha silhouette na null. Hapa silhouette za OOS (wastani 0.577) hazijaonyeshwa zinashinda null kwenye OOS embedding — fidelity ARI inapima reproducibility, sio umuhimu dhidi ya bahati. Hii ni gap ya next phase.
3. **Stability ni qualitative.** '✅ thabiti' ni threshold rahisi (mean>0.25, last>0.2); folds zinaruka (mfano pullback inashuka hadi 0.47, mean_reversion hadi 0.51) — hakuna formal stability test (variance/trend). Usisome 'thabiti' kama 'constant'.
4. **deep_pullback fidelity ndogo** → Nyström haiwezi kurudisha clustering yake kwa uhakika; weak spot halisi inayounga mkono F-039 (event-specific geometry), sio universal manifold.
5. **Leak-gap ni EXPECTED, sio bug** — ndiyo proper-Nyström inavyofichua leakage. Hoja sio 'gap ipo' bali 'no-leak silhouette bado iko juu kiasi gani' — na kwa events nyingi imeshuka kwenye eneo la wastani.

*Nyström OOS extension (fit PAST landmarks, project FUTURE, no re-fit = no leakage). proper vs joint-fit = leakage inflation. Rolling walk-forward silhouette = stability. Principle 44: normalization = representation. F-039: event-specific geometry. NO ML. Profitable ≠ Tradable Edge.*
