# M4-HTF — PRE-REGISTRATION: breadth baseline kwenye H4 na D1 (chanzo C)

> **Imeandikwa 2026-08-01, KABLA ya kuendesha kipimo chochote cha HTF.** Namba zote zilizo hapa
> zinatoka kwenye kazi iliyokwisha kutokea (M4-0, M4-2, C2-WATCH, Swing Family). Mabadiliko ya
> vigezo baada ya kuona matokeo = kuhamisha magoli (charter §4.6 — haramu).

## 1. Kwa nini HTF, na kwa nini SASA

LESSON-045 (M4-2) imeonyesha kwa data ya rows 1M: **taarifa ipo, gharama ndiyo inayoua.** Kikwazo si
uwezo wa kutabiri — ni uwiano **gross-vs-cost**. Hilo lina lever moja ya kimuundo inayojulikana:

> **Spread haibadiliki ukipanda timeframe; move inakua.**

| TF | ATR (kadirio, √muda) | cost (spread+slip) | cost kama % ya risk (1 ATR) |
|---|---|---|---|
| H1 | ~10 pips | ~0.5 | ~5% |
| H4 | ~20 pips | ~0.5 | ~2.5% |
| D1 | ~50 pips | ~0.5 | ~1% |

Ushahidi unaounga mkono (si nadharia tu): mechanism ya compression **tayari ilitoa EV_R chanya mara
MBILI kwenye HTF** — C2-WATCH (H4, EV_R +0.110, p=0.0543) na Swing Family #1 (D1, EV_R +0.067,
p=0.136, pairs 9/12 chanya). **Zote mbili zilianguka kwa POWER, si kwa ishara hasi.** Charter §1C
inaorodhesha TF nyingine kama chanzo (C) cha nafasi; hakuna aliyekipima kwa **breadth pooled**.

## 2. Hii ni NINI — na SI nini

- **NI:** kipimo (measurement) cha logic ILE ILE iliyothibitika (`nr7_break`) kwenye TF nyingine, kwa
  **pairs 12 pooled** (L-041) — sawasawa na M4-0 ilivyofanya kwa H1. Runner ni ULE ULE
  (`breadth_baseline.py --tf H4|D1`); hakuna statistic mpya, hakuna fill mpya.
- **SI:** hypothesis test mpya. `p_boot` ni **descriptive** (kama M4-0) — TRAIN/VALIDATION za H4/D1
  zimeshaguswa na utafiti wa awali (grid ya C2, atlas ya rmap). **Hakuna dirisha jipya linalochomwa.**
- **SI:** re-test ya C2-WATCH wala ya Swing Family. Zile zilikuwa **familia maalum** (H4 cells 4;
  D1 nr7×LOW-vol) zenye madirisha yao yaliyotumika. Hii ni **breadth ya nr7 pooled**, muundo tofauti,
  na inatumia TRAIN+VALIDATION PEKEE.

## 3. Vigezo (pre-registered)

Kwa kila TF ∈ {H4, D1} na kila exit-variant (SL2/TP1, SL1/TP1), pooled pairs 12:

| # | Kipimo | Kizingiti | Kwa nini |
|---|---|---|---|
| 1 | EV_R (VALIDATION, pooled) | **> 0** | msingi |
| 2 | Uthabiti TRAIN→VALID | ishara ISIBADILIKE (zote chanya) | M4-0 ilipita hivyo; ndicho kilichotutofautisha na fails 3/3 za L-041 |
| 3 | **gross/cost** | **≥ 3×** (charter §4.4, `cost_budget`) | ndio hasa kilichoshindikana H1 |
| 4 | breadth ya pairs | **≥ 6/12** pairs EV_R>0 kwenye splits ZOTE MBILI | mechanism-level, si pair moja |
| 5 | trades/mwaka | inaripotiwa, **HAKUNA floor** | HTF ina nafasi chache kwa asili — hilo linatarajiwa, si kosa |

**Tafsiri iliyofungwa mapema:**
- Vigezo 1-4 vyote vimetimia → **HTF-BREADTH ni mgombea**: inaenda kwa PD kwa `pairs[]` + forward,
  na ndiyo msingi wa KAIROS-4 (si KAIROS-3 — hiyo ilikuwa ML).
- Kigezo 3 pekee ndicho kinachokosekana → **thamani ipo lakini ni nyembamba**: WATCH + forward, si live.
- Kigezo 1 au 2 kinakosekana → **LESSON**: lever ya TF haifanyi kazi kwa nr7; chanzo (C) kinafungwa.

## 4. Utaratibu (umefungwa)

1. `python breadth_baseline.py --tf H4` na `--tf D1` — **TRAIN + VALIDATION PEKEE** (guard ileile;
   HOLDOUT + sealed 2026-05+ hazipo kwenye njia hii).
2. Vigezo vya kila TF vinatathminiwa kwa `cost_budget.py` (gross/cost) na jedwali la pooled.
3. Matokeo → ripoti; kama kigezo 1-4 vimetimia, **pre-registration MPYA** inahitajika kwa hatua
   yoyote inayogusa HOLDOUT. Hakuna holdout kwenye hatua hii.

## 5. Vigezo vya kiufundi (vimefungwa kabla, kwa provenance)

| TF | max_hold | session_filter | chanzo cha uamuzi |
|---|---|---|---|
| H1 | 24 | no-LATE | golden default; STRAT-001/002 |
| H4 | 24 | no-LATE | `family_pooled` (C2-WATCH) ilitumia default 24 + no-LATE |
| D1 | 20 | **None** | `swing_family` ilitumia max_hold=20; session filter haina maana kwenye D1 |

vol_filter = None kwa zote (breadth = bila filters za ziada — kama M4-0).
**Swap:** D1 inashikilia wiki kadhaa → swap ni MUHIMU. Haijamo kwenye `episodes`; itashughulikiwa kwa
`cost_budget` (bajeti − swap × nights) na ikihitajika `rmap.apply_swap` kama swing_family ilivyofanya.

## 6. Matokeo yanayowezekana (yote halali)

(i) H4/D1 zinaonyesha gross/cost ≥ 3× na EV_R chanya kwenye splits zote → tumepata njia halali bila
ML kabisa. (ii) EV chanya lakini gross/cost < 3× → WATCH/forward. (iii) Hakuna → chanzo (C)
kinafungwa kwa heshima, na tunabaki na KAIROS-1/2 + breadth ya H1 kwenye broker sahihi.

*Profitable ≠ Tradable Edge. Protect capital first.*
