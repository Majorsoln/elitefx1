# S4 — Strategy Signal Tool + Policies (Implementation Report)

*2026-07-09 | IMPLEMENTER-A | Alpha Engineering S4 (Chief S4 + UPDATE 2026-07-09) | Rules 1-8 |
NO ML | NO pesa halisi | strategies PROVEN-OOS: STRAT-001, STRAT-002*

> **S4 = deploy proven strategies.** `strat_signal.py` inagundua NR7 kwenye bar iliyofunga →
> pending OCO orders (format ya `paper_trader --signal`). Strategy policies (decision_policy.py)
> zinaunganisha strategies kwenye mnyororo E1-E4. EDGE iko kwenye SIGNAL pre-registered + uthibitisho
> wa OOS — SIO policy logic. REUSE nr7_break + wilder_atr (hakuna math mpya). Format: Rule 8.

---

## Implementation Report

**Deliverables:**

| Faili | Nini |
|-------|------|
| `src/research/strat_signal.py` (MPYA) | Signal tool: REGISTRY (STRAT-001 USDCHF SL2/TP1; STRAT-002 USDJPY SL1/TP1; zote nr7+no-LATE) · `pending_orders()` (REUSE nr7_break+wilder_atr) · `load_bars()` (parquet/CSV) · CLI `--pair`/`--all` |
| `src/research/decision_policy.py` | `STRATEGY_POLICIES` (strat001-nr7-usdchf@v1, strat002-nr7-usdjpy@v1) — thin SELECT + provenance; self-test [7] |
| `run_selftests.py` | +strat_signal (sweep 17/17) |

**Design (Chief UPDATE: tool + policy za strategies MBILI):**

- **`pending_orders(o,h,l,c,hour, pair, strat)`** — bars PRICE → PIPS (nr7/atr contract) → `nr7_break`
  (n=7) + `wilder_atr` (14) → bar ya mwisho ikiwa NR7 armed → OCO: buy-stop `long_level`, sell-stop
  `short_level`; SL/TP za ATR (long: SL=entry−sl_atr·ATR, TP=entry+tp_atr·ATR) → PRICE (round 5/3).
- **no-LATE decidable ex-ante:** entry = bar INAYOFUATA (hour+1); ikiwa 17-23 → skip (inalingana na
  strategy_lab filter-on-signal ya Chief). NR7 pending = **bar MOJA tu** (episodes() stop hufill i+1).
- **Output** = amri za `paper_trader.py --signal PAIR SIDE ENTRY SL TP` (Operator anaweka MT5; ikijaza
  → paper_trader endesha decide→gate FTMO→size→fill→log E3).
- **Strategy policies (rahisi — Chief "chagua rahisi, eleza"):** registry TOFAUTI (`STRATEGY_POLICIES`,
  HAIingii `POLICIES` ili demo `run()` isichafuke). Kila policy = `_strategy_select(desc)` deterministic
  → `("SELECT", provenance)`. Mirror ya `OPERATOR_POLICY` ya paper_trader: **edge iko kwenye signal
  (nr7 pre-registered) + OOS proof; policy = provenance wrapper.** Mnyororo E1-E4 uleule.

## Self Tests

`strat_signal.py --self-test` → **PASS** (bars synthetic):

```text
[1] registry (STRAT-001 USDCHF SL2/TP1, STRAT-002 USDJPY SL1/TP1, no-LATE)
[2] NR7 -> OCO (buy: entry>sl, tp>entry; sell: entry<sl, tp<entry); 2 orders
[2b] STRAT-001 SL/TP = 2.0xATR/1.0xATR (ratio 2.00)
[3] no-LATE filter (entry hour 17 -> skip)
[4] non-NR7 bar -> no order
[5] USDJPY pip scaling (entry ~145, 3 decimals)
```

`decision_policy.py --self-test` → **PASS** (+[7] strategy policies: SELECT + policy_id sahihi; SIO
kwenye POLICIES demo).

**Integration ya kweli (S4 → E1-E4) — PASS:** `strat_signal` order (USDCHF BUY 0.89657 / SL 0.881 /
TP 0.90435) → `apply_policy(strat001)` → `gate(FTMO)` → **VALIDATED**. Chain kamili inafanya kazi.

**Regression:** FULL SWEEP **17/17 PASS** (16→17 na strat_signal; hakuna kilichovunjika).

## Known Limitations

1. **NR7 detection inategemea bars sahihi za Operator** — tool inasoma parquet (state format) au CSV;
   ubora wa signal = ubora wa bars (timezone/hour lazima ilingane na TRAIN: server/UTC).
2. **no-LATE inatumia (hour+1)%24** — inadhani bars contiguous za H1. Gaps (weekend/holiday) zinaweza
   kufanya "bar inayofuata" isiwe saa+1 halisi; Operator athibitishe next-bar hour (Open Q#1).
3. **OCO halali bar MOJA** — episodes() semantics: stop hufill bar i+1 pekee. Ikikosa, order i-cancel.
   Tool inasema hivyo; enforcement ni ya Operator/MT5 (au paper_trader baadaye).
4. **Policy = provenance wrapper, si signal logic** — decision ya KUINGIA imefanywa na signal tool
   (nr7). Policy inarudisha SELECT bila kusoma snapshot (kama OPERATOR_POLICY). Sizing/FTMO = E4 chain.
5. **pip_value ni approx (paper_trader)** — sizing halisi kwa lot inahitaji pip_value ya broker (MWONGOZO).
6. **Strategies 2 tu (PROVEN-OOS)** — siblings/cells nyingine zimefungwa (SEALED, S3b). Mpya = OOS mpya.

## Open Questions

1. **Next-bar hour kwa no-LATE** — je tool ifikirie gaps (weekend) au Operator athibitishe? Pendekezo:
   tool inatoa onyo la next-hour; Operator ndiye anayeweka order (anaona ratiba halisi).
2. **OCO kwenye paper_trader** — je paper_trader iongezwe `--oco` (place zote, cancel nyingine ikijaza),
   au Operator ashughulikie kwa mkono? Kwa sasa: mkono. Pendekezo: --oco baadaye (nje ya S4 scope).
3. **Registry-policy moja vs policy-per-strategy** — nilichagua policy-per-strategy (rahisi + provenance
   wazi kwa kila strategy). Kama Chief anataka registry-policy moja (inayochagua kwa pair), nabadilisha.
4. **strat_signal live path** — kwa sasa inasoma files (paper). Live (MT5 API) = E4-adjacent, imezuiwa
   hadi Project Director (RED LINE ya E4).

---

*S4: strat_signal.py (REGISTRY STRAT-001/002 → pending OCO orders kwa format ya paper_trader; REUSE
nr7_break+wilder_atr) + STRATEGY_POLICIES (thin SELECT + provenance, E1-E4 chain). Self-tests PASS;
integration S4→gate VALIDATED; sweep 17/17. Edge = signal pre-registered + OOS proof, si policy logic.
NO ML. NO pesa halisi. Profitable ≠ Tradable Edge. Protect capital first.*
