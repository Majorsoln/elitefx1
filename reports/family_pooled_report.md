# Family-Pooled Holdout Test — Build Report (C2-WATCH; design ya SCIENTIST-D)

*2026-07-13 | IMPLEMENTER-A | design-of-record: `reports/family_pooled_design.md` (§1-§8, verbatim) |
Rules 1-8 | REUSE-ONLY (episodes/_mask_context/pvalue_boot ZERO changes; load_window +ts additive) |
NO holdout run (Chief token baada ya referee + screen) | NO ML*

> **Jukumu (design §8.1):** jenga `src/research/family_pooled.py` (runner + acceptance tests AT1-AT8),
> reuse tu. **SIYO** registration wala holdout — hiyo ni Chief (§8.4) baada ya SCIENTIST-D referee
> (§8.2) + AT8 dry-run screen (§8.3). Deliverable = "tayari family-pooled build".

---

## Implementation Report

**Deliverable (code):**

| Faili | Mabadiliko | Design |
|-------|-----------|--------|
| `src/research/family_pooled.py` | **MPYA** — runner + AT1-AT8. `REP_CELLS` (universe FIXED §1); `registration_string`/`_seed_from_registration` (§3.3); `_r_normalize` (R-units §2); `cell_stream` (episodes reuse §3.1); `pool_streams` (union sort ts→pair, dedup §3.2/AT7); `mde_screen` (§4); `run_family` (§3-§6 + AT5 guard); `_write_outputs` (AT6 no-clobber); `_boot_ci` (§6). | §0-§8 |
| `src/research/strategy_lab.py` | `load_window` — **+`ts`** kwenye return dict (cross-pair ordering). **ADDITIVE, non-breaking** (§3.1/§8.1 authorized); callers waliopo hawaguswi. | §3.1/§8.1 |
| `src/research/run_selftests.py` | `family_pooled` imeongezwa kwenye MODULES (sweep). | — |

**REUSE (ZERO changes, design §8.1):** `episodes` · `_mask_context` · `pvalue_boot` · `pvalue_gt0` ·
`_seed_from_key` (hashing pattern) — zote zimeitwa kama-zilivyo, hakuna byte iliyobadilika. Njia ya
`cell_stream` ni SAWASAWA na `strategy_lab.evaluate` (event fn default params → `_mask_context` KWENYE
signals → `episodes`), kisha R-normalization ya §2. Fill rules, byte-identical golden hashes (mr/nr7),
na sweep zote zimebaki intact (regression chini).

**Registration (design §3.3, imefungwa kwa code — Chief atathibitisha wakati wa freeze):**
- reg string: `FAMILY-POOLED-C2WATCH-H4|<cellkey REP-1>|...|<cellkey REP-4>` (cell key = umbo la
  `_seed_from_key`: event|pair|sl|tp|sf|vf) → seed deterministic `_seed_from_registration` (sha1→int,
  hashing ILEILE ya engine). Reproducible bit-kwa-bit (AT3).
- Universe (§1, hakuna selection freedom): REP-1 nr4_inside×GBPJPY 1.5/1.5 · REP-2 nr7_break×EURGBP
  1.5/1.0 · REP-3 nr7_break×EURJPY 1.0/3.0 · REP-4 nr7_break×AUDUSD 1.5/3.0 — zote no-LATE, vol=None.
- Statistic: `pvalue_boot(pooled_R, B=50_000, mean_block=3, seed=reg)`; criterion m=1: `p_boot<0.05
  AND pooled EV_R>0`. Sensitivity (non-gating): p_z (z-test) + p_atr (ATR-units).

**R-normalization (§2):** `pnl_R = pnl_pips / (sl_atr × atr[signal_bar])`, `signal_bar = entry_bar−1`
= EXACTLY quantity `episodes()` inatumia kwa SL. Deployment-consistent (fixed-fractional risk),
pip-scale invariant (AT1). Pooling: union sorted na `ts_entry` (tie → pair alphabetical) — inanasa
same-day cross-pair dependence kwa block resampling.

## Self Tests

`family_pooled.py` acceptance tests **PASS 8/8** (bila data ya nje, Rule 7):

```text
[AT2] R-norm EXACT: forced SL → -(1+cost/R); forced TP → tp/sl - cost/R (match 1e-12)
[AT1] pip-scale invariance (normalization): struct EXACT-invariant · BBB bit-identical · AAA
      residual = closed-form (-SLIP·(1-1/scale)/R) — fixed-slippage DEVIATION (OQ#1)
[AT3] determinism: pvalue_boot bit-identical mara mbili; seed kutoka registration string stable
[AT4] mixture-null size (SCALED sanity; full 20k×B=50k = referee MC): boot≈0.066 ~nominal & ≤ z
[AT5] holdout red-line: run_family(holdout) bila/ na token batili → PermissionError (load_window guard)
[AT6] no-clobber: outputs = family_pooled_c2watch.jsonl + family_pooled_report.md TU; candidates*.jsonl intact
[AT7] dedup: (pair, entry_bar) UNIQUE kwenye pooled stream (assert; pairs 4 tofauti → hakuna dup)
[AT8] dry-run shape: pipeline kamili (VALIDATION fixtures) → result {n, ev_r, p_boot, screen, verdict}

Regression (sweep nzima): SELF-TEST SWEEP 22/22 PASS — ikijumuisha strategy_lab (byte-identical
golden hashes mr=28cc2218/nr7=872edc44 INTACT baada ya load_window +ts), event_quality_report,
+ family_pooled mpya. load_window +ts HAIJAVUNJA caller yoyote.
```

## Known Limitations

1. **AT1 fixed-slippage residual (DEVIATION-with-evidence → OQ#1).** Design §2 inadai pip-scale
   invariance ni "exact". Kwa kweli `episodes()` ina slippage ISIYO-pip-scaled (`SLIP_MARKET`=0.1,
   `SLIP_STOP`=0.3 pip, **const**). Kwa hivyo `cost/R` (na hivyo `pnl_R`) SI bit-identical chini ya
   ×100 scaling — inatofautiana kwa `SLIP·(1-1/scale)/R_trade` EXACTLY (nimehakiki dhidi ya closed-
   form, 1e-9). Nimetenga AT1 kwa **fixed signals** (event fns kama nr7_break zina absolute `tick`
   threshold — SI scale-invariant, property tofauti na madai ya §2). Slippage ni broker-cost halisi
   isiyo-proportional kwa pip — SIYO bug; ni asymmetry ya kimuundo. Rule 1: sijagusa `episodes()`.
   Referee/Chief waamue kama residual hii inakubalika (ni ~0.001 R kwa ATR ya kawaida).
2. **AT4 ni SCALED sanity, si gate.** Full spec (≥20k reps, B=50,000, size ∈ [0.040,0.060] + AR(0.5)
   variant ≤0.08) ni **MC huru ya SCIENTIST-D** (design §5-AT4, §8.2). Self-test yangu (M=500, B=300)
   inaonyesha boot ~nominal & ≤ z (mirror wave1 [8]); B ndogo inavimbisha size kidogo (0.066).
3. **AT8 real dry-run inahitaji data (Operator PC).** Self-test inaendesha pipeline kwa fixtures
   (monkeypatch load_window). VALIDATION halisi (2023-24) → EV_R/sd_R EXACT → §4 screen shrink 0.35
   ni hatua ya §8.3 (Operator + runbook). Screen ikishindwa → hakuna registration (§8.3).
4. **Registration HAIJAFUNGWA.** Constants (B, seed, criterion, verdict semantics, caveats) zimo kwa
   code kutoka design, lakini freeze rasmi = commit ya Chief (§8.4). Sijaendesha holdout.
5. **Verdict semantics (§6) zimo kwenye report generator**, lakini zinatumika tu holdout ikiendeshwa
   (Chief token). PASS = PROVEN-OOS-PROVISIONAL (family); HAIUNDI STRAT-00x, HAIRUHUSU capital.

## Open Questions

1. **AT1 pip-scale "exact" vs fixed-slippage residual (kwa SCIENTIST-D referee/Chief).** Design §2
   inasema invariance ni exact; `episodes()` fixed slippage inaifanya iwe exact-minus-`SLIP·(1-1/
   scale)/R`. Nimetekeleza kama structural-exact + residual-matches-closed-form. Je referee anakubali
   framing hii, au anataka `episodes()` slippage iwe pip-proportional (= change ya engine iliyokaguliwa,
   nje ya jukumu langu — Rule 1)? Napendekeza: kubali (residual ~0.001 R, na ni cost halisi).
2. **Seed kutoka registration string:** nimetumia `sha1(reg)[:12]→int` (hashing ILEILE ya
   `_seed_from_key` lakini juu ya string nzima badala ya cell moja). Design §3.3 inasema "via existing
   `_seed_from_key` hashing" — nafsiri kama hashing-scheme, si function-call moja kwa moja (cell keys 4
   zinaingia kwenye string). Chief athibitishe.
3. **REP-2 tie-break B=50k recompute (§1 note i):** design inaagiza wakati wa registration ku-recompute
   p_boot ya EURGBP pair kwa B=50,000 na kurekodi kama tie-break imethibitishwa/imebadilishwa na finer
   floor (2e-05). Hii ni hatua ya **registration** (Chief §8.4) — runner wangu unatumia REP_CELLS
   zilizofungwa; sijafanya tie-break re-selection (hakuna data + si jukumu la build).
4. **`by`-nothing:** runner inaandika result nzima (pooled series + descriptive record: shares,
   timeout_share, lag-1 ρ, CI) kwenye jsonl + report. Je Chief anataka format tofauti ya rekodi kwa
   registration freeze?

---

*family_pooled = runner ya jaribio MOJA la pre-registered (m=1) kwa C2-WATCH family (design SCIENTIST-D
§0-§8); REUSE tu (episodes/_mask_context/pvalue_boot ZERO changes; load_window +ts additive); R-units
normalization (§2); pooling union-sort (§3); MDE screen (§4); AT1-AT8 PASS 8/8; sweep 22/22 PASS. NO
holdout run (Chief token §8.4). NO ML. Confirmation ≠ discovery (§7). Profitable ≠ Tradable Edge.
Protect capital first.*
