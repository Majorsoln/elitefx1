# ELITEFX — PROVEN STRATEGY REGISTRY (PERMANENT / IMMUTABLE)

> **STATUS: SACRED.** Hizi strategies zimepita mzunguko kamili wa taasisi
> (TRAIN → VALIDATION → HOLDOUT one-shot + bootstrap-FDR + cost stress).
> Zimethibitishwa OOS. **HAZIFUTWI, HAZIBADILISHWI.** Japhet: "nitakuwana models yake."
> Mzunguko wowote mpya wa research **hauguzi** registry hii — unaongeza tu STRAT mpya
> baada ya kupita gate ile ile ya HOLDOUT one-shot.

---

## STRAT-001 — nr7_break × USDCHF (H1)
- **Signal:** `nr7_break` (bar yenye range nyembamba zaidi ya 7 → OCO stops high+tick / low−tick), edge-trigger + rearm.
- **Timeframe:** H1
- **Risk cfg:** SL2 / TP1, **no-LATE** (hakuna entry ya kuchelewa baada ya trigger bar).
- **Proof:** S3 HOLDOUT one-shot, N=303, **EV +1.92 pips/trade**, p=0.021 (bootstrap, pre-registered cell).
- **Policy id:** `policy:strat001-nr7-usdchf@v1` (`src/research/decision_policy.py:124`).
- **Split:** TRAIN 2016–2022 → VALID 2023–2024 → HOLDOUT 2025-01→2026-04 (dirisha SEALED, one-shot imetumika).

## STRAT-002 — nr7_break × USDJPY (H1)
- **Signal:** `nr7_break`, edge-trigger + rearm.
- **Timeframe:** H1
- **Risk cfg:** SL1 / TP1, **no-LATE**.
- **Proof:** S3b HOLDOUT one-shot, N=327, **EV +2.65 pips/trade**, p=0.029 (bootstrap, pre-registered cell).
- **Policy id:** `policy:strat002-nr7-usdjpy@v1` (`src/research/decision_policy.py:126`).
- **Split:** sawa na STRAT-001; dirisha SEALED, one-shot imetumika.

---

## WATCH / FORWARD-ONLY (si PROVEN, si dead)
- **C2-WATCH — compression-family pooled × H4.** S3-C2 one-shot: **FAIL kwa heshima**
  (p_boot=0.0543 vs 0.05; EV_R **+0.110 chanya**, 4/4 reps chanya — imekosa significance kwa nywele;
  power ilikuwa 0.62 → 38% FAIL hata kama forecast ni sahihi). Dirisha SEALED milele.
  Njia pekee ya kuipandisha: **forward data mpya** (si re-open ya holdout). "Haujathibitika" ≠ "haifanyi kazi".

---

## GATE YA KUINGIA REGISTRY HII (kwa STRAT mpya yoyote)
STRAT mpya inaingia **PROVEN** tu ikipita **zote**:
1. TRAIN grid → VALIDATION (BH-FDR survivor, p_boot < 0.05).
2. Pre-registration FROZEN by commit **KABLA** ya kufungua HOLDOUT.
3. HOLDOUT **one-shot** kwenye dirisha bikira (pre-registered cell PEKEE), token `CHIEF-HOLDOUT-S3`.
4. Honest harness: next-bar fills, stop=touch gap-honest, costs (spread+slippage), episode non-overlap.
5. EV chanya baada ya gharama + p_boot < 0.05 (bootstrap Politis-Romano B=50k).

Hakuna njia ya mkato. Dirisha likishatumika → SEALED milele.
