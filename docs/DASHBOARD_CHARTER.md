# ELITEFX — MONITORING DASHBOARD CHARTER (Django) — "kioo cha taasisi"

> Directive ya PD 2026-07-17: dashboard ya Django kuona reports, live actions, diagnosis kamili,
> je kila trade sheria zilifuatwa, VPS iko sawa, performance ya kila model, pair×strategy analytics
> — kwa udhibiti wa kitaasisi (baadaye: kukodisha models). Doctrine V2 §4/§5.

## KANUNI KUU (zisizojadilika)
1. **READ-ONLY / KIOO:** dashboard HAIAMUI wala HAIBADILISHI trade kamwe (V2 §4). Inasoma
   artifacts tu (decision logs, paper/live outputs, reports, registry, ledger). Maamuzi = engine.
2. **Chanzo cha data = artifacts zilizopo** (hakuna re-compute ya strategy): decision_repository
   outputs, paper_trader logs, reports/*.md, docs/MODEL_REGISTRY + EXPERIMENT_LEDGER, winrate_monitor,
   cost_stress, compliance logs. Dashboard = ingest + present.
3. **Immutable/append-only** kwa audit (V2 §5): dashboard haifuti rekodi; inaonyesha historia.
4. **Separation:** app ya dashboard ni tofauti na src/research (hunts). Dir mpya `dashboard/`.

## ARCHITECTURE (phased)
- **Backend:** Django (project `elitefx_dash/`), SQLite kuanzia (Postgres kwa production).
  Models za DB = mirror ya artifacts (Trade, Decision, ComplianceCheck, ModelVersion, Pair,
  StrategyPerf, VpsHeartbeat, Report). **Ingest layer** (management command `ingest`) inasoma
  artifacts → DB; hakuna business logic ya trading ndani ya Django.
- **Frontend:** Django templates + charts (Chart.js — self-contained). Hakuna framework nzito
  awali.
- **Auth:** Django auth; roles (viewer/attestor/admin) — msingi wa leasing (viewer wa nje = access
  ya monitoring + attestation, si research).

## PANELS (kwa directive ya PD)
| Panel | Kinachoonyeshwa | Chanzo |
|---|---|---|
| **Portfolio** | equity curve, EV, DD, trades/mwezi — STRAT-001/002 (na live/paper toggle) | paper_trader/live logs |
| **Live actions** | trades za hivi karibuni: entry/exit, R, dir, pair, strategy, muda | decision_repository / execution logs |
| **Rule-compliance** | kila trade: FTMO daily/max-loss, no-trade-window, max-spread — PASS/FAIL badge | compliance gate logs |
| **VPS health** | heartbeat ya mwisho, uptime, latency, clock-drift, data-feed status | VPS heartbeat file/endpoint |
| **Model registry** | kila model version: status, OOS proof, performance-attestation, lifecycle | docs/MODEL_REGISTRY + data/registry/*.json |
| **Pair × Strategy grid** | matrix ya EV/win/N kwa kila (pair × strategy) — data ya kuchambua | rmap atlas + live/paper attribution |
| **Reports browser** | reports/*.md + EXPERIMENT_LEDGER (kumbukumbu) — rendered | reports/ + docs/ledger |
| **Diagnosis** | alerts: retention drift (winrate_monitor), cost drift, streak warning, model degradation | monitors |

## PHASES (kila moja = deliverable inayokaguliwa)
- **M-DASH-1 (msingi):** Django project + DB models + `ingest` command (paper_trader + registry +
  ledger + reports) + Portfolio + Live-actions + Reports-browser panels. Read-only. Self-contained.
- **M-DASH-2:** Rule-compliance panel + Diagnosis/alerts (kutoka winrate_monitor/cost_stress) +
  Pair×Strategy grid.
- **M-DASH-3:** VPS heartbeat + Model-registry attestation view + auth/roles (leasing-ready).

## NIDHAMU YA UJENZI
- Dashboard haiendeshi strategy code; ingest inasoma outputs tu (kama artifact haipo → panel
  inaonyesha "no data", si kubuni). Tests za ingest (fixtures). requirements.txt tofauti.
- HAKUNA data ya kweli ya broker/secret kwenye repo. VPS/live endpoints = config (env), si hardcode.
