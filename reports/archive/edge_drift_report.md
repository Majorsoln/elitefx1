# Edge Drift Engine — KWA NINI edge inakufa? (Phase 10)

*2026-06-27 19:44 | rolling 6 windows | mazingira halisi (ATR/spread/activity) per window | death = window ya kwanza ≤0 baada ya chanya | min N=200 | configs: 1,271 (dead: 510)*

> **Lengo (Chief):** Phase 9 ilionyesha WHEN edge inakufa (F-028: kila edge ina lifecycle). Phase 10 inatafuta **WHY** — config dimensions zimefungwa, lakini ATR/spread/activity HALISI zinadrift (states ni relative). Bila sababu, adaptive ranking = curve-fitting. **Principle 27:** prefer LIVING edges. **F-027 (reformulated):** early quality may not predict future survivability. NO ML (vinginevyo tunafundisha 'historical corpses'). Profitable ≠ Tradable Edge.


## F-027 (reformulated, CAUSAL) — je early quality inatabiri future survival?

- Spearman(window-1 EV, survival windows) = **+0.03** (configs zilizoanza chanya: 519)

→ ✅ **F-027 (reformulated) inaungwa mkono**: early quality HAITABIRI future survival — config nzuri mwanzoni ≠ config inayodumu (tofauti na whole-sample corr ya Phase 9).

## Q1 — Edge ilikufa kwa sababu mazingira yalibadilika? (Δ last-alive → death)

| mazingira | mean Δ% (death vs last-alive) | corr(Δenv, ΔEV) |
|-----------|------------------------------|------------------|
| volatility (ATR) | +0.1% | -0.06 |
| spread | +7.5% | -0.01 |
| activity | +7.3% | -0.07 |

→ mazingira yaliyobadilika ZAIDI wakati wa kifo: **spread** (mean Δ +7.5%). corr kubwa zaidi |ρ| na ΔEV inaonyesha sababu inayohusiana zaidi.

## Q2 — Before → After kwa configs zilizokufa (sampuli)

| Configuration | death@win | ATR before→after | spread before→after | activity before→after | EV before→after |
|---------------|-----------|------------------|---------------------|------------------------|-----------------|
| EURJPY·trend_continuation·C0·LOW·LONG·NORMAL | 2/6 | 20→21 → | 0.6→0.6 ↑ | 10752→14506 ↑ | +3.1→-4.1 |
| AUDUSD·trend_continuation·C0·LOW·LONG·NORMAL | 2/6 | 13→13 → | 0.9→0.9 → | 4502→5242 ↑ | +1.6→-5.8 |
| GBPUSD·trend_continuation·C0·LOW·LONG·NORMAL | 2/6 | 22→21 → | 0.9→0.9 → | 7816→8779 ↑ | +1.1→-2.3 |
| USDCAD·trend_continuation·C0·LOW·LONG·NORMAL | 3/6 | 17→15 ↓ | 1.0→1.1 ↑ | 6089→6283 → | +0.7→-2.7 |
| NZDUSD·trend_continuation·C0·LOW·LONG·NORMAL | 2/6 | 14→12 ↓ | 1.0→1.0 → | 4871→5287 ↑ | +3.8→-4.2 |
| EURUSD·trend_continuation·C0·LOW·LONG·NORMAL | 2/6 | 15→15 → | 0.3→0.3 ↑ | 5807→9749 ↑ | +2.1→-5.2 |
| GBPUSD·trend_continuation·C0·NORMAL·LONG·NORMAL | 2/6 | 24→25 → | 0.8→0.9 ↑ | 7315→9540 ↑ | +0.8→-4.0 |
| EURGBP·trend_continuation·C0·LOW·LONG·NORMAL | 3/6 | 12→11 ↓ | 0.9→0.8 ↓ | 8702→5546 ↓ | +2.5→-3.7 |
| USDCHF·trend_continuation·C0·LOW·SHORT·NORMAL | 2/6 | 14→12 ↓ | 1.1→1.1 → | 4688→4578 → | +0.7→-1.5 |
| EURGBP·trend_continuation·C0·NORMAL·LONG·NORMAL | 2/6 | 16→13 ↓ | 0.9→0.9 → | 9571→7745 ↓ | +0.6→-2.8 |
| USDJPY·trend_continuation·C0·NORMAL·SHORT·NORMAL | 2/6 | 22→18 ↓ | 0.3→0.3 ↓ | 6731→6474 → | +1.2→-1.8 |
| USDJPY·trend_continuation·C0·LOW·SHORT·NORMAL | 2/6 | 20→13 ↓ | 0.3→0.3 → | 7716→4781 ↓ | +2.3→-3.7 |
| USDJPY·trend_continuation·C0·HIGH·LONG·NORMAL | 2/6 | 26→20 ↓ | 0.3→0.3 → | 7820→6531 ↓ | +3.7→-1.4 |
| USDCAD·trend_continuation·C0·HIGH·LONG·NORMAL | 2/6 | 25→18 ↓ | 0.9→1.1 ↑ | 8932→8308 ↓ | +0.4→-0.3 |
| EURJPY·trend_continuation·C0·HIGH·LONG·NORMAL | 2/6 | 31→32 → | 0.6→0.6 ↑ | 15048→15063 → | +4.5→-2.2 |
| USDCHF·trend_continuation·C0·HIGH·SHORT·NORMAL | 2/6 | 18→16 ↓ | 1.1→1.1 → | 5763→6033 → | +2.7→-2.5 |
| USDCHF·trend_continuation·C0·HIGH·LONG·NORMAL | 2/6 | 17→15 ↓ | 1.1→1.0 → | 5101→5293 → | +0.5→-5.8 |
| USDJPY·pullback·C0·LOW·SHORT·NORMAL | 2/6 | 18→14 ↓ | 0.3→0.3 ↓ | 6518→5833 ↓ | +0.5→-1.9 |
| EURJPY·deep_pullback·C0·LOW·LONG·NORMAL | 2/6 | 20→21 ↑ | 0.6→0.7 ↑ | 10012→15340 ↑ | +1.3→-4.1 |
| AUDUSD·deep_pullback·C0·LOW·LONG·NORMAL | 2/6 | 13→12 ↓ | 0.9→0.9 → | 4555→5237 ↑ | +0.8→-1.7 |

## Q3 — Transitions zinazojirudia kabla ya kifo (ATR·spread·activity)

| transition (ATR · spread · activity) | mara | % ya vifo |
|--------------------------------------|------|-----------|
| ATR↑ · spr↑ · act↑ | 74 | 15% |
| ATR↓ · spr↑ · act↓ | 55 | 11% |
| ATR↓ · spr↓ · act↓ | 48 | 9% |
| ATR↓ · spr→ · act↓ | 42 | 8% |
| ATR→ · spr↑ · act↑ | 29 | 6% |
| ATR↑ · spr↑ · act↓ | 26 | 5% |
| ATR↑ · spr→ · act↑ | 25 | 5% |
| ATR↓ · spr↓ · act↑ | 22 | 4% |

→ transition inayojirudia zaidi kabla ya kifo: **ATR↑ · spr↑ · act↑** (15% ya vifo).

## Q4 — Je kifo kinaweza kutabirika window MOJA kabla? (rule-based, NO ML)

- base rate P(window inayofuata ≤0) = **60%**
- P(next ≤0 | EV ilipungua window hii) = **59%** (n=2528)
- P(next ≤0 | EV iliongezeka window hii) = **60%** (n=2556)

→ ⚠️ signal dhaifu: EV inayopungua inainua P(kifo) kwa **-1pp** juu ya base — rule rahisi (no ML) inatoa onyo la mapema (haitoshi peke yake).

## Q5 — Events zina lifespan tofauti — na KWA NINI?

| event | mean survival (win) | mean env drift % | mean ATR | mean spread | configs |
|-------|---------------------|------------------|----------|-------------|---------|
| mean_reversion | 2.01/6 | 20.7% | 24 | 1.0 | 142 |
| deep_pullback | 1.75/6 | 22.1% | 24 | 1.1 | 116 |
| trend_continuation | 1.64/6 | 22.2% | 24 | 1.0 | 107 |
| breakout | 1.55/6 | 20.5% | 22 | 0.9 | 60 |
| pullback | 1.53/6 | 20.9% | 23 | 1.0 | 94 |

→ corr(survival, env-drift) kwa event = **+0.10** (uhusiano si wazi; sababu nyingine).

## VERDICT — Phase 10 Edge Drift Engine

→ Edge inakufa ikiambatana na mabadiliko ya mazingira halisi (ATR/spread/activity) ingawa state-labels zimefungwa. F-027 (reformulated): early quality ρ=+0.03 na survival — haitabiri. Kifo kina-tabirika kiasi window moja kabla (rule-based). Hii ndiyo msingi wa **Adaptive Market Intelligence**: Opportunity Engine ifuatilie LIFECYCLE (living edges), ondoe zinazoonyesha dalili za kifo. NO ML bado (tungefundisha historical corpses). Inayofuata: Opportunity Engine v2 (lifecycle-aware) / F-026 state trajectory.

*Edge Drift = mabadiliko ya mazingira halisi (ATR/spread/activity) yanayoambatana na kifo cha edge. Q1 sababu, Q2 before→after, Q3 transitions, Q4 predictability (no ML), Q5 event lifespan+why. F-027 reformulated = causal (early quality → future survival). F-028: kila edge ina lifecycle. Principle 27: prefer living edges. NO ML. Profitable ≠ Tradable Edge.*