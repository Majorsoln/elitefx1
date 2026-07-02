# Decision Policy Framework — safu kati ya Decision Object na Engine (Decision Science D5)

*2026-07-02 20:58 | 9 pairs, 5 snapshots, 3 policies | versioned rules: Snapshot→action | NO Decision Engine | NO ML*

> **P85** decisions = permanent history. **P86** cancelled ≠ rejected. **P87** integrity ≠ outcome. **P88** kila decision inareference policy. **P89 (OPEN)** Execution Object. Policy = sheria (versioned) inayotenganisha Object na Engine; Engine ibaki GENERIC. NO Decision Engine (D6).

## Q1 — Policy ni nini?

Policy = **kanuni iliyopewa jina na version** inayomap **Evidence Snapshot (complete context, P80) → action** kutoka decision family (P60). Ni **decision LOGIC**, tofauti na Decision Engine (orchestrator). Engine inaita policy; policy inaamua. NO ML — rule-based tu.

| policy | id (versioned) | tabia |
|--------|----------------|-------|
| capital_preservation | policy:capital_preservation@v1 | ABSTAIN isipokuwa READY + reliability juu sana (P26) |
| conservative | policy:conservative@v1 | SELECT kwa READY+mid; STALE→WAIT |
| aggressive | policy:aggressive@v1 | SELECT kwa READY/STALE+low; INVALID→HEDGE |

## Q2 — Policy ina version?

Ndio — `name@vN`. Kila Decision Object inareference **policy_id kamili** (P88) → maamuzi ni **reproducible** hata tukibadilisha policy baadaye (version mpya = policy_id mpya = decision_id mpya).

## Q3 — Policy inachagua action vipi? (kwenye snapshots halisi)

| snapshot (event) | readiness | reliability | capital_preservation | conservative | aggressive |
|------------------|-----------|-------------|----------------------|--------------|------------|
| breakout | READY | 1.00 | SELECT | SELECT | SELECT |
| deep_pullback | INVALID | 1.00 | ABSTAIN | ABSTAIN | HEDGE |
| mean_reversion | READY | 1.00 | SELECT | SELECT | SELECT |
| pullback | READY | 1.00 | SELECT | SELECT | SELECT |
| trend_continuation | READY | 1.00 | SELECT | SELECT | SELECT |

- action inatoka **readiness_state (P82) + reliability + conflict** — SIO market prediction. Default = ABSTAIN (P26). *value halisi ni hasi → mostly ABSTAIN/AVOID; hii SI alpha (P69).*

## Q4 — Policy inabadilishwa bila kubadilisha Engine?

- snapshot ile ile (`breakout`) → policies tofauti → actions: **capital_preservation=SELECT, conservative=SELECT, aggressive=SELECT**.
- `apply_policy(policy, snapshot)` haibadiliki — policy ime-**inject**-iwa. Engine (D6) itaita `apply_policy` tu; kubadilisha policy hakubadilishi Engine code → **loosely coupled** (P84 refs).

## Q5 — Decision Engine na Policy zinawasiliana vipi?

**Contract (moja tu):**
```text
Engine ── snapshot ──▶ Policy.decide(snapshot) ── (action, reason) ──▶ Engine
Engine ── wraps ──▶ Decision Object { action, policy_id (P88), evidence_refs=[snapshot_id] (P84) }
```
- mfano: `dec:c6d593e09b` action=SELECT, policy_id=policy:capital_preservation@v1, evidence_refs=['snap:a7cb79ec47'].
- Engine haijui LOGIC ya policy; inajua contract tu. Policy haijui Engine. **Fully decoupled.**

## VERDICT — D5 Decision Policy Framework

→ ✅ **Decision Policy imefafanuliwa** kama **versioned rule** (Snapshot→action; Q1/Q2), inayochagua action kutoka readiness+reliability (Q3), **swappable bila kubadilisha Engine** (Q4, dependency injection), yenye **contract moja** ya Engine↔Policy (Q5). Kila Decision inareference policy_id (P88) → reproducible. Sasa Engine (D6) itakuwa **generic orchestrator** tu. **Hakuna Decision Engine bado.** NO ML.

**Bado Decision Science D5 — policies ni rule-based, hazithibitishi alpha.** value halisi ni hasi → maamuzi mengi ni ABSTAIN/AVOID (P26); decision-ready ≠ trade-ready (P69).

## Honest Caveats

1. **Policies ni ILLUSTRATIVE rules, hazijathibitishwa.** Thresholds (HI/MID/LO reliability) ni human choices; hakuna OOS/backtest inayoonyesha policy yoyote ina faida. Ni muundo, sio edge.
2. **'SELECT' HAIMAANISHI trade yenye faida.** reliability = Φ(EV/SE) inayojaa (P70 OPEN); value halisi ni hasi → hata 'SELECT' ingekuwa kwenye EV hasi. Aggressive policy ni ya mfano tu, sio pendekezo.
3. **Policy inatumia snapshot fields tu** (P80) — haiangalii external constraints (P89/P81 OPEN: broker/news/liquidity). Kwa hiyo action ni 'intended', sio 'executable'.
4. **Reproducibility inategemea policy_id + snapshot_id** — kama snapshot inatumia age-shift sare (D3 caveat), reproducibility ni ndani ya mfano huo, sio production event-time.
5. **Hakuna Decision Engine wala Execution (P89 OPEN)** — 'action' ni maamuzi yaliyopangwa; kilichotekelezwa (fills/slippage/rejects) ni Execution Object, bado haipo.

*Decision Policy = versioned rule Snapshot→action; swappable (injection); Engine↔Policy contract = policy.decide(snapshot); decision references policy_id (P88). Rule-based, NO alpha, NO Decision Engine, NO ML. Profitable ≠ Tradable Edge.*