# Decision Engine — Implementation Report (Decision Science D6)

*2026-07-03 22:17 | engine: `src/research/decision_engine.py` (pure, stateless) | harness: `decision_engine_report.py` (evidence pipeline iko HAPA, sio kwenye engine) | NO ML*


## Compliance Checklist (Rule 2)

| Principle | Status | Ushahidi |
|-----------|--------|----------|
| P92 | ✓ | Engine = generic orchestrator; HAKUNA decision logic ndani (logic yote ni ya Policy — Rule 3; engine core ~60 lines) |
| P94 | ✓ | Engine inajua TU Snapshot·Policy·Decision Object (Rule 4; import-purity self-test [4]) |
| P97 | ✓ | Stateless — no cache/globals/singleton/memory (Rule 5; module-mutables check, self-test [3]) |
| P98 | ✓ | Correctness kwanza, hakuna optimization (Rule 6; plain loops, hakuna caching/vectorization) |
| P99 | ✓ | Kila sehemu ina self-test (Rule 7; tests [1]–[5] + harness self-test) |
| P100 | ✓ | Pure/deterministic (P71): inputs sawa → Decision Object ile ile (id-stable, self-test [3]) |
| P101 | ✓ | Kila Decision inareference exact Snapshot ID (P84) + policy_id (P88) (self-test [2]) |
| P102 | ✓ | Ripoti kwa muundo wa Rule 8: Implementation Report → Self Tests → Known Limitations → Open Questions |

*NB: nambari P92–P102 ni kutoka Decision Engine Specification ya Chief; matini yake bado haijawekwa kwenye repo — angalia Open Questions.*

## Implementation Report

- **Engine nzima ni functions mbili:** `decide(snapshot, policy) → Decision Object` na `decide_batch` (map tu). Validation ya contract (`validate_snapshot`, `validate_policy`) inakataa inputs batili kwa `ContractError`.
- **Mtiririko:** validate → `policy.decide(snapshot)` → `make_decision(...)` yenye `policy_id` (P88) + `evidence_refs=[snapshot_id]` (P84), lifecycle `PROPOSED`.
- **Separation (Rule 3/4):** engine file haina import yoyote ya market/evidence pipeline (decision_object + stdlib pekee — imethibitishwa na self-test [4]). Harness hii ndiyo inayojenga snapshots.
- **Demo kwenye data halisi** (snapshots × policies; kupitia ENGINE):

| snapshot (event) | readiness | capital_preservation | conservative | aggressive |
|------------------|-----------|----------------------|--------------|------------|
| breakout | READY | SELECT | SELECT | SELECT |
| deep_pullback | INVALID | ABSTAIN | ABSTAIN | HEDGE |
| mean_reversion | READY | SELECT | SELECT | SELECT |
| pullback | READY | SELECT | SELECT | SELECT |
| trend_continuation | READY | SELECT | SELECT | SELECT |

- decisions 15 zimeundwa kupitia engine; zote zina `policy_id` + `snapshot_id` refs na lifecycle `PROPOSED` (hakuna execution — P89 OPEN).

## Self Tests

```text
[1] contract validation: bad-snapshot-blocked=True bad-policy-blocked=True -> OK
[2] refs: snapshot=['snap:t1'] policy=policy:test@v1 -> OK
[3] deterministic + stateless: id-stable=True module-mutables=[] -> OK
[4] engine ignorance: bad-imports=[] forbidden-words=[] -> OK
[5] batch==map + policy-injection: batch-match=True swap-action=WAIT -> OK

SELF-TEST: PASS
```
- harness self-test: contract-rejection + refs-integrity juu ya snapshots halisi (angalia `--self-test`).

## Known Limitations

1. **Hakuna Execution Object (P89 OPEN)** — decisions zinabaki `PROPOSED`; hakuna fills/slippage/broker constraints (P81 OPEN).
2. **Policies ni illustrative rules za D5** — hazijathibitishwa OOS; 'SELECT' ≠ trade yenye faida (EV halisi hasi; P69 decision-ready ≠ trade-ready).
3. **reliability = Φ(EV/SE) inayojaa** (P70 OPEN) — engine inairithisha bila kurekebisha (kwa makusudi: engine haihukumu evidence).
4. **Immutability by-convention** — engine inarudisha objects mpya lakini Python dict si frozen; enforcement kamili ni engineering ya baadaye.
5. **Snapshot age-shift model ya D3** — as-of ni sare, sio per-member event-time; demo ni ndani ya model hiyo.

## Open Questions

1. **Decision Engine Specification (P90–P102) matini yake haiko kwenye repo** — checklist hapa ime-map kwa Rules 1–8 + doctrine P63–P89. Ombi: Chief/Japhet wa-commit spec rasmi (mfano `ELITEFX DECISION ENGINE SPEC V1.md`) ili Compliance Review itaje maneno kamili.
2. **Architecture Compliance Review** (workflow mpya ya Chief) — nani/nini kinafanya hatua hii kabla ya Chief Review? (Implementer self-review haitoshi kimuundo.)
3. **Decision history storage (P85)** — decisions ni objects; zinahifadhiwa wapi (parquet/jsonl?) ili kuwa 'permanent decision history'? Haijafafanuliwa bado.
4. **Lifecycle transitions baada ya PROPOSED** — nani anaidhinisha VALIDATED (integrity gate ya P87)? Engine haifanyi hivyo (kwa makusudi); ni layer gani?

*Engine: pure/stateless/generic (Rules 3–6); logic yote ya maamuzi ni ya Policy; kila Decision inareference snapshot_id + policy_id. NO ML. Profitable ≠ Tradable Edge.*