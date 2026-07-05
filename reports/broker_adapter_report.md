# Broker Adapter — Implementation Report (E4, P81/P106)

*2026-07-05 | IMPLEMENTER-A | Chief rulings Q1-Q6 (E4 spec APPROVED) zimetekelezwa 1:1 |
Spec: `reports/broker_adapter_specification.md` | Rules 1-8 | NO ML | **PAPER-MODE PEKEE** —
HAKUNA pesa halisi, HAKUNA network | Mwisho wa Track A (E1→E4)*

> **THE TWO STREAMS MEET.** E4 = mpaka wa impurity + mtafsiri kati ya Decision Science (pure) na
> MWONGOZO/FTMO/MT5 (external). **Inafunga loop ya E1** (P81): FTMO CHECK 1-5 → E1 constraints +
> context → Gate. Sizing → E2 report. Settlement → E3. Paper-mode; live = refuse-stub (Project
> Director). Translate, don't decide (P97). Format: Rule 8.

---

## Implementation Report

**Deliverables (code):**

| Faili | Mabadiliko | Doctrine |
|-------|-----------|----------|
| `src/research/broker_adapter.py` | **MPYA** — `build_constraints()` (FTMO 5→E1) · `build_context()` · `size()` (MWONGOZO §1) · `PaperBroker` · `execute()` · `settle()` · `AdapterError` | P81/P97/P92/P107; Q1-Q6 |
| `src/research/decision_repository.py` | **Q4** `kind=settlement` (REQUIRED: id/as_of/parent_execution_id/pnl); `integrity_check` sasa inakagua `parent_execution_id` dangling; self-test [5b] mpya | E3; Chief Q4 |
| `src/research/integrity_gate.py` | **Bug-fix (A-4 ripple):** `validate_decision` inakubali `Mapping` (frozen decision, si `dict` tu) + `audit` list/tuple; self-test [8] regression guard | A-4/E2↔E1 |

**Rulings 1:1:**
- **Q1 (RED LINE):** `mode=live` bila `live_authorized` → `AdapterError(live_not_authorized)`. Paper
  ndio default; live = refuse-stub hadi Project Director athibitishe artifact format.
- **Q2:** FTMO CHECK 1-5 → **constraints 5 TOFAUTI** (`daily_loss/total_dd/slots/correlation/spread`),
  kila moja `{id, check(decision, context)→(verdict, reason)}` (E1 contract). Adapter haizihukumu — Gate ndiyo.
- **Q3:** `size()` = DailyRiskBudgetSizer (MWONGOZO §1) ndani ya Adapter → `intended.qty` (E2 Q5 path).
- **Q4:** `kind=settlement` kwenye Repository (edit ndogo + self-test).
- **Q5:** `account_state` contract (daily_loss/total_dd/open_slots/correlation_exposure/spread_by_pair)
  imethibitishwa kwenye Adapter boundary.
- **Q6:** `max_spread` per-pair = kazi ya Operator; spread-constraint **inapita (ELIGIBLE)** kama
  haijawekwa config.

**Flow (paper):** `execute(decision, trade, config, account, broker)` → gate-mode → `size()` →
`PaperBroker.submit()` → `ExecutionReport` → `record()` (E2, frozen) → Repository (E3). Constraints/
context ni hatua tofauti (`build_constraints`/`build_context`) — caller anaita **Gate KABLA ya execute**.

## Self Tests

Zote **PASS**, bila network/pesa/numpy (paper; Rule 7):

```text
broker_adapter.py     PASS (8/8): FTMO→5-constraints · constraints-evaluate · sizing · execute-FILLED+repo
                                  · PARTIAL/REJECTED/no-budget · settlement→repo · RED-LINE-live-gating · Rule-4-purity
decision_repository   PASS (7/7): + [5b] kind=settlement + parent_execution_id integrity
integrity_gate        PASS (8/8): + [8] A-4 frozen-decision accepted (regression guard)
Regression: frozen · decision_object · decision_engine · decision_policy · execution_object → PASS zote
```

**Integration ya kweli (E1↔E4 loop) — PASS:**

```text
1) make_decision → PROPOSED (SELECT/ENTER)
2) build_constraints (FTMO) + build_context → gate() → VALIDATED (ELIGIBLE)
3) execute paper → Execution Object FILLED (qty 60, parent link ✓)
4) FTMO veto (daily_loss juu) → gate() REJECTED (failed: constraint:daily_loss@v1) — trade imezuiwa kabla ya execution
```

**Bugs 2 ZILIZONASWA na integration** (isolated self-tests zilizikosa — thamani ya end-to-end):
1. `integrity_gate.validate_decision` ilitumia `isinstance(dict)` — Decision Objects halisi ni
   **frozen (MappingProxyType)** baada ya A-4; Gate ilikataa kila decision halisi. **Fix:** `Mapping`.
2. `audit` check ilitaka `list` — A-4 freeze → **tuple**. **Fix:** `(list, tuple)`.
   *(Gate self-test ilitumia fake plain-dict, kwa hiyo haikugundua; E4 integration = mahali pa kwanza
   Decision halisi (frozen) ilipita Gate.)*

**P107 (transitive purity):** `broker_adapter` = **transitively PURE** (imethibitishwa: inapakia bila
market/network stack — numpy/polars/duckdb/socket/requests/mt5 blocked). Direct imports =
`execution_object` + `decision_repository` + `frozen` + stdlib. ftmo_config/broker/account = **INJECTED**.

## Known Limitations

1. **MT5/live haipo** — implementation ni PAPER-MODE PEKEE (PaperBroker simulator, deterministic).
   Live path = refuse-stub; utekelezaji wake unasubiri Project Director artifact format (Q1).
2. **`timestamp` vs `as_of` normalization.** Objects za D4/E2 zina `timestamp`; Repository (E3)
   inaindex `as_of`. Adapter's `_repo_view()` inanormaliza (`as_of ← timestamp`) kwenye boundary.
   Ni **naming inconsistency ya E2↔E3** — imeshughulikiwa kwa boundary-normalization; reconciliation
   rasmi (objects zitumie `as_of`, au Repository index `timestamp`) ni Open Q#1.
3. **`max_spread` haipo ftmo_config** (Q6 = Operator) — spread-constraint inapita hadi Japhet aiongeze.
4. **Sizing `pip_value`** — paper: config/approx; live: MT5. Precision ya paper ni makadirio.
5. **Settlement PnL = fact, si edge** — je ni edge? = D8 (per-decision OOS + FDR). E4 inarekodi namba tu.
6. **Gate integration inahitaji numpy** (kupitia decision_object chain) — self-tests za Adapter ni pure,
   lakini pipeline kamili (make_decision→gate) inarithi P107 baseline ya decision_object (remediation
   bado PENDING Chief).

## Open Questions

1. **`timestamp`↔`as_of` reconciliation (E2↔E3).** Objects zitumie `as_of` (badala ya `timestamp`),
   au Repository i-index `timestamp`? Kwa sasa Adapter inanormaliza kwenye boundary. Pendekezo:
   objects zibaki na `timestamp`; Repository ikubali zote mbili (edit ndogo) — usafi zaidi kuliko
   boundary-patch.
2. **Live-gating artifact format (RED LINE)** — Project Director aamue jinsi approval-artifact
   inavyohakikiwa (signature/credential). Live path iko stub hadi hapo.
3. **`worst_case` derivation** — kwa sasa inapita kama context param; nani anaihesabu (SL zote wazi ×
   pip_value)? Pendekezo: Adapter ihesabu kutoka open positions (E4-live) — paper: caller anapitisha.
4. **Full-pipeline demo harness** — je tuandike harness moja (snapshot→…→settlement) kama
   `decision_engine_report.py`? Ingesaidia D8/K6. Pendekezo: baada ya Chief kufunga E4.

---

*Broker Adapter = impurity boundary + translator (P92/P107); FTMO CHECK 1-5 → E1 constraints injected
(P81 — loop imefungwa); sizing (MWONGOZO §1) → E2 report; Settlement → E3 (kind=settlement);
paper-mode PEKEE, live = refuse-stub (Project Director — Protect capital first). Translate, don't
decide (P97). Transitively PURE. Integration E1↔E4 PASS. Self-tests PASS zote (8+7+8 + regression).
Mwisho wa Track A. NO ML. NO pesa halisi. Profitable ≠ Tradable Edge.*
