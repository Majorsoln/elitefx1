# P107 Remediation — Implementation Report (transitive purity closed)

*2026-07-07 | IMPLEMENTER-A | Chief ruling (baada ya Audit #6): option **(a) + (c)** | Rules 1-8 |
Surgical — make_decision/make_gate_decision/transition LOGIC haijaguswa | NO ML*

> **P107** Architectural purity shall include **transitive** dependency purity, not only direct imports.
> Baseline (Audit #5): `decision_engine → decision_object → market_state_engine (→ polars)` = transitive
> **FAIL**. Ruling: **(a)** lazy-import market/demo deps kwenye `decision_object`; **(c)** compliance
> test ya transitive graph. Matokeo: **core ya Track A yote transitively PURE.** Format: Rule 8.

---

## Implementation Report

**Option (a) — `decision_object.py` lazy imports (core → pure):**

| Kabla (module-level) | Baada |
|----------------------|-------|
| `import numpy as np` | **imeondolewa**; core inatumia `import math` (stdlib) |
| `from market_state_engine import cfg` | **lazy** — ndani ya `run()` + `main()` |
| `from evidence_snapshot import make_snapshot` | **lazy** — ndani ya `run()` |
| `from evidence_operations import build_tagged_evidence` | **lazy** — ndani ya `run()` |
| `from evidence_set import make_set` | **lazy** — ndani ya `run()` |
| `from frozen import freeze` | **inabaki** (frozen ni stdlib-pure) |

- **Core fix (surgical):** `make_decision` ilitumia `np.isfinite(...)` (line 89) → **`math.isfinite(...)`**
  (stdlib). Ni sehemu PEKEE ya core iliyotumia numpy. LOGIC ile ile (finite check ya `uncertainty`).
- `make_decision` / `make_gate_decision` / `transition` / `_gate_decision_id` / `freeze` = **haziguswi**
  (LOGIC). Zinatumia stdlib (`math`, `hashlib`) + `frozen` tu.
- Market/demo deps zinatumika **TU** kwenye `run()`/`main()` (demo path — inahitaji parquet/data);
  zimefungiwa hapo kama lazy imports. Module-level imports sasa = **stdlib + `frozen` PEKEE.**

**Matokeo:** `decision_object` core = transitively PURE → **Engine + Gate (zinazoimport
decision_object) = transitively PURE.** Chain nzima ya production imefungwa.

**Option (c) — `purity_check.py` (compliance test, P104 gap):**

- Module mpya `src/research/purity_check.py` (stdlib PEKEE; ASCII-safe kwa Windows sweep).
- Inaimport kila module ya core kwenye **subprocess safi** yenye import-guard inayozuia
  `numpy/polars/duckdb/market_state_engine/evidence_*`. Ikapakia → PURE; ImportError ya module
  iliyozuiwa → LEAK.
- **Negative control:** `decision_policy` (impure kwa makusudi) LAZIMA ianguke chini ya guard →
  inathibitisha test si no-op (guard inafanya kazi kweli).
- Imeongezwa kwenye `run_selftests.py` (sweep) → itakimbia kila PR (Rule 2 / P104+P107).

## Self Tests

```text
purity_check.py --self-test:  PASS
  [PURE] frozen · decision_object · decision_engine · integrity_gate ·
         execution_object · decision_repository · broker_adapter        (7/7 core PURE)
  [ctrl:OK] decision_policy  (impure -> imenaswa na guard)

run_selftests.py (FULL SWEEP, na stack):  11/11 PASS
  frozen · decision_object · evidence_snapshot · decision_policy · decision_engine ·
  integrity_gate · execution_object · decision_repository · broker_adapter ·
  purity_check · e2e_paper_demo

Probe ya moja kwa moja (bila market stack): core zote 7 zina-LOAD pure;
decision_object --self-test PASS bila numpy/market (core = math.isfinite + frozen + stdlib).
```

## Known Limitations

1. **`decision_policy` inabaki impure** — inaimport numpy/market module-level. Ni **leaf** (policy
   injected kwa Engine kama argument; Engine haiiimport), kwa hiyo haiathiri purity ya core. Ni
   negative-control kwenye purity_check. Kama Chief anataka policies pia ziwe pure = kazi tofauti.
2. **`run()`/`main()` ya decision_object bado zinahitaji market stack** — kwa makusudi (demo path
   inasoma parquet). Hazitekelezwi na core wala self-test; lazy imports zinapakia TU zikiitwa (PC
   ya Operator). Sikuweza kuendesha data path hapa (R-1).
3. **`math.isfinite` vs `np.isfinite`** — kwa `uncertainty` ya float (Python/numpy scalar) tabia ni
   ile ile (nan/inf → False). Kama snapshot ingeleta array (haifanyi — `uncertainty` ni scalar, P80),
   ingehitaji mabadiliko; scope ya sasa ni scalar tu.
4. **Evidence Layer bado impure** — evidence_* modules zinaimport market module-level. P107 ruling
   ilihusu **core ya Decision/Execution**; Evidence retrofit (kama ilivyokuwa A-4 Evidence) ni uamuzi
   tofauti wa Chief (interface-frozen P90).

## Open Questions

1. **Policies pure?** Je Chief anataka `decision_policy` (na policies zijazo) ziwe transitively pure
   pia (lazy market imports), au zibaki demo-impure (leaf, injected)? Kwa sasa = negative control.
2. **purity_check kwenye CI gate** — je iwe **blocking** (PR inashindwa kama core inavuja) rasmi kwenye
   run_selftests? Sasa ni sehemu ya sweep (11/11); kufanya blocking ni sera ya Chief (Rule 2).
3. **Audit #7** — Chief ata-request re-measure ya P107 graph; purity_check inatoa kipimo cha kiotomatiki
   (Auditor aweza kuendesha badala ya manual graph-walk).

---

*P107 remediation (a+c): decision_object core = lazy market imports + `math.isfinite` → Engine/Gate/
Execution/Repository/Adapter transitively PURE; make_* LOGIC haijaguswa (surgical). purity_check.py =
compliance test (subprocess guard + negative control) kwenye sweep. Full sweep 11/11 PASS. Baseline
FAIL (Audit #5) imefungwa. NO ML. Profitable ≠ Tradable Edge.*
