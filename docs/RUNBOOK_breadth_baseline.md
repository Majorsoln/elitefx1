# RUNBOOK — M4-0 BREADTH BASELINE (nr7 × pairs 12 × H1, pooled)

> **MZUNGUKO-4 hatua 0** (docs/CYCLE4_ML_CHARTER.md §1B/§5/§6.1 + docs/KAIROS_3_SPEC.md §5.3).
> Kusudi: **namba ambayo KAIROS-3 (na ML yote ya M4-1..M4-4) LAZIMA ishinde.** Hii SI hypothesis
> mpya — ni logic ILE ILE iliyothibitika (`nr7_break` × H1 × no-LATE = STRAT-001/002) ikienezwa
> kutoka pairs 2 → **pairs 12 pooled** (chanzo (B) cha nafasi).
> **HOLDOUT (2025-01→2026-04) HAIGUSWI. Dirisha SEALED 2026-05+ (Doctrine §3.1b) HALIGUSWI.**

## Kinachopimwa

| Kipengele | Thamani |
|---|---|
| Event / TF / filter | `nr7_break` (stop, OCO) · **H1** · `session_filter="no-LATE"` · `vol_filter=None` · `max_hold=24` |
| Exit-variants (2) | **SL2.0/TP1.0** (jiometri ya KAIROS-1) · **SL1.0/TP1.0** (jiometri ya KAIROS-2) |
| Pairs | zote za `config/data_config.yaml` (12, XAUUSD ikiwemo) |
| Splits | **TRAIN 2016-2022 + VALIDATION 2023-2024 PEKEE** |
| Hukumu | **POOLED** (LESSON-041): R-normalization ya `family_pooled` → EV_R, EV_pips, N, trades/mwaka, p_boot (engine RASMI), CI90, win%, PF |
| Gharama | spread halisi ya bar ya entry + slippage kwenye **kila** namba (LESSON-039) |

Per-pair inaonyeshwa kama **diagnostics TU** — hakuna best-pair selection popote.

## Hatua (PC yako ya data)

1. `git pull`
2. `cd src\research`
3. `python run_selftests.py` → tegemeo: **SELF-TEST SWEEP: 33/33 PASS**
4. `python breadth_baseline.py --run`  (dakika kadhaa: pairs 12 × variants 2 × splits 2)
5. Commit outputs mbili:
   - `reports/breadth_baseline.md`
   - `data/strategies/breadth_baseline.jsonl`
6. Ripoti kwa Chief: **"tayari M4-0"** + nakili **BASELINE LINE** kutoka kichwa cha ripoti.

Hiari: `--boot-B <N>` (default 10,000) — B ya `pvalue_boot`. Runner ina-cap B yenyewe kwa N kubwa
(RAM ya array (B×N) ya stationary bootstrap); `B_eff` inaripotiwa kwenye jedwali.

## Kitakachotoka (jinsi ya kusoma)

- **BASELINE LINE** (kichwa cha ripoti): `EV_net = X pips/trade (pooled FX), trades/mwaka = Y
  (VALIDATION)` + `EV_R` (currency ya hukumu). Bar inachukuliwa kwa **variant yenye nguvu zaidi
  VALIDATION** — bar ya JUU = conservative kwa challenger.
- **Jedwali la pooled**: kila variant × split (TRAIN/VALIDATION): N · EV_R · CI90 · EV_pips (12) ·
  EV_pips (FX pekee) · trades/mwaka · win% · PF · p_boot · p_z · B_eff.
  `p_boot` hapa ni **descriptive** (baseline, si test iliyosajiliwa) — hakuna dirisha jipya
  lililochomwa; TRAIN/VALIDATION zimeshatumika na utafiti wa nr7.
- **PENDEKEZO la `pairs[]`** (kwa `config/models.yaml`, KAIROS-1/2 multi-pair):
  kanuni **pre-registered, SI ranking** — pair inapendekezwa IKIWA **EV_R > 0 TRAIN NA EV_R > 0
  VALIDATION NA N_valid ≥ 30**. **HAKUNA "top-N kwa EV"** (= max-selection bias, LESSON-041).
  Ripoti inaonyesha (a) zilizopita + snippet ya YAML; (b) zilizokataliwa + **sababu**.
  **Ni PENDEKEZO — PD ndiye anayehariri `config/models.yaml`.** Code haiandiki registry.

## M4-0b — COST STRESS + CAPACITY (baada ya M4-0)

M4-0 ilionyesha breadth halali LAKINI **cost-thin** (EV_net FX +0.91 pips ⇒ breakeven Δspread 0.91
pip). Kabla ya kupanua `pairs[]` live, endesha:

```
cd src\research
python breadth_capacity.py --run
```

Inatoa `reports/breadth_cost_capacity.md` + `data/strategies/breadth_capacity.jsonl`:
1. **EV(Δspread)** analytic (`cost_stress` R5(1)) — pooled FX + per-pair breakeven.
2. **spread_state** ya bar ya ENTRY (R5(2)) — je trades za **WIDE** ndizo zinazokula faida?
   (EV_WIDE < 0 ⇒ pendekezo la WIDE-skip kwenye **deployment policy**, si backtest — inahitaji
   forward-verify.)
3. **CAPACITY** chini ya lango halisi (`config/ftmo_config.yaml`: max_slots 7 / correlated 3):
   accepted vs rejected, sababu, concurrency, na **EV ya zilizokataliwa vs zilizopita** (kama
   zilizokataliwa ni bora, lango linakata faida → hoja ya kupanga foleni kwa ubora = KAIROS-3).
   Safu `live` = tabia ya code ya sasa; `strict` = kila correlation-group inaongezeka (§SWALI LA WAZI).
   **COMBINED** = KAIROS-1 + KAIROS-2 zikishindania slots zilezile (hali halisi).

## Red lines (zilizowekwa kwenye code, si kwenye nia)

- `_guard_split` inarefuse split yoyote isiyokuwa `train`/`validation` **kabla ya kusoma data**
  (self-test: `holdout`/`sealed`/`forward`/`all` → `PermissionError`, `load_window` haiitwi kabisa).
  Red-line iliyopo ya `load_window` (token ya Chief) inabaki juu ya hiyo.
- **Golden HAZIJAGUSWA:** `episodes`, `_mask_context`, `pvalue_boot`, `pvalue_gt0`, `load_window`,
  `_r_normalize`, `pool_streams`, `_boot_ci` ni **imports TU** (ZERO statistic/fill mpya).
- Outputs zinaandika faili **mbili** zilizotajwa pekee (`candidates*.jsonl` hazibadilishwi).

*Baseline ≠ edge. STRAT-001/002 pekee ndizo PROVEN (holdout one-shot). Profitable ≠ Tradable Edge.*

## M4-1 — DATASET ya KAIROS-3 (baada ya M4-0/M4-0b)

```
cd src\research
python k3_dataset.py --build      (dakika kadhaa: pairs 12 × bars zote × dirs 2)
```
Inatoa `data/processed/k3/<pair>.parquet` + `k3_manifest.json` (**nje ya git** — data nzito) na
`reports/k3_dataset.md` (rekodi inayoenda git: manifest, label balance, folds za purged-CV, NaN%).
TRAIN PEKEE (2016-2022) — guard mbili: split-guard + assert `max(ts) < TRAIN_END`.
