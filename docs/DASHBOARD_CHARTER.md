# ELITEFX — INSTITUTIONAL MONITORING DASHBOARD (Django) — "THE GLASS BOX"

> Directive ya PD 2026-07-17: dashboard ya kuona reports, live actions, diagnosis kamili, je kila
> trade sheria zilifuatwa, VPS iko sawa, performance ya kila model, pair×strategy — kwa udhibiti wa
> kitaasisi na **baadaye kukodisha models kwa taasisi nyingine.** Doctrine V2 §4/§5.
> Build kamili (agent mmoja mwenye prompt ya hatua-kwa-hatua). SI phased kama kizuizi.

## DHANA KUU YA UBUNIFU: "GLASS BOX, NOT BLACK BOX"
Taasisi inayokodisha model haaminishwi — **anakagua.** Kila namba kwenye dashboard ina **kiungo cha
chanzo** (trade → decision trace → artifact → commit). Tofauti yetu na wengine si "faida" — ni
**uwazi unaoweza kukaguliwa.** Uso wa dashboard unauza uaminifu huu: safi, mnene wa data lakini
unaosomeka, hisia ya "terminal ya taasisi" (dark theme, monospace kwa namba, hakuna kelele).

## KANUNI ZISIZOJADILIKA (V2)
1. **KIOO, si mkono:** HAKUNA endpoint inayoanzisha/kubadilisha trade. Maamuzi = engine + policy.
2. **Read-only ingest:** inasoma artifacts zilizopo (paper/live logs, reports, registry, ledger,
   monitors). Artifact haipo → "no data", KAMWE si kubuni namba.
3. **Immutable/append-only** kwa audit. **Hakuna secret/broker creds** kwenye repo (env config).
4. **Separation:** `dashboard/` ni tofauti kabisa na `src/research/` (haiendeshi strategy code).

---

## PANELS + UBUNIFU (build kamili)

### 1. COMMAND DECK (landing) — hali ya taasisi kwa jicho moja
- Banner ya **SYSTEM STATUS**: OPERATIONAL / DEGRADED / OFFLINE (kutoka VPS heartbeat + data freshness).
- KPI strip: Equity (paper+live), Net R mwezi huu, Open positions, **COMPLIANCE SCORE** (% trades
  zilizofuata sheria — lengo 100%), Active models, Last heartbeat.
- Mini equity sparkline + "today's actions" ticker.

### 2. PORTFOLIO — utendaji
- Equity curve (paper/live toggle) + rolling metrics: expectancy R, win%, PF, max/current DD,
  Sharpe (kadirio), trades/mwezi. **Monthly returns heatmap** (mwaka × mwezi).
- Per-strategy breakdown (STRAT-001 vs 002) + portfolio-combined.

### 3. LIVE ACTIONS — blotter + **DECISION TRACE** (kiini cha glass-box)
- Jedwali la trades za hivi karibuni (pair, strategy, dir, entry/exit, R, muda, status).
- Kila trade INAFUNGUKA → **decision trace kamili**: signal (event+bar) → policy (select/veto) →
  risk (size, % risk) → compliance (checks zote) → fill (price, spread, slippage). Hii ndiyo
  "glass" — kila hatua ina chanzo.

### 4. TRUST / COMPLIANCE — panel ya kitaasisi (uuzaji wa uaminifu)
- **COMPLIANCE SCORE** kubwa + "N trades, X violations".
- Gauges: FTMO daily-loss headroom, max-loss headroom, no-trade-window adherence, max-spread adherence.
- Per-trade compliance badges (PASS/FAIL + sababu). Violation yoyote = nyekundu, inayoonekana.

### 5. MODEL REGISTRY — "product catalog" ya kukodisha
- Kila model = **kadi**: id, version (v1.0→…), status **lifecycle timeline** (CANDIDATE→PROVEN→
  LIVE→RETIRED), OOS proof (HOLDOUT namba), class, dependencies.
- **LIVE-vs-PROMISED tracker** (killer feature ya uaminifu): live/paper EV imewekwa juu ya
  backtest/holdout expectation + **shrinkage band** — je live inafuata ahadi? Model degradation = flag.
- **ATTESTATION EXPORT**: bonyeza → ripoti ya performance inayoweza kukaguliwa (JSON+PDF/HTML,
  na hash + chanzo/commit) kwa mteja-taasisi. Bidhaa ya kukodisha yenyewe.

### 6. PAIR × STRATEGY MATRIX — analytics ya kuboresha
- Heatmap grid: (pair 12 × strategy/family) → EV / win% / N. Drill-down kwa cell → pair-lessons
  + atlas rows za mazingira (vol/session/mwaka).

### 7. DIAGNOSIS / ALERTS — mfumo unaojiangalia
- Retention drift (winrate_monitor), cost drift (cost_stress), streak warning, model degradation
  (live-vs-promised divergence), data-gap/stale-feed, VPS clock-drift. Severity + timestamp + chanzo.

### 8. VPS / SYSTEM HEALTH
- Heartbeat ya mwisho, uptime, latency, clock-drift, data-feed freshness per pair, disk/mem.
- Status OPERATIONAL/DEGRADED (inalisha Command Deck banner).

### 9. RESEARCH LEDGER + LESSONS — kumbukumbu (uaminifu wa "tunaonyesha kushindwa kwetu")
- EXPERIMENT_LEDGER rendered (kila jaribio + verdict). Lessons 42 library. Reports browser (reports/*.md).

---

## LEASING FOUNDATION (roles/multi-tenancy — msingi, si full SaaS)
- Django auth + roles: **internal** (yote), **attestor** (compliance+registry+attestation), **client/lessee**
  (read-only monitoring ya model MOJA iliyokodishwa + attestation yake — SI research, SI models nyingine).
- Attestation export + audit trail viewer (append-only, filterable) = kile mteja anakagua.

## STACK
- Django (`elitefx_dash/` + app `monitor/`), SQLite (Postgres-ready). DB models = mirror ya artifacts
  (SI trading logic). `ingest` management command. Templates + Chart.js (self-contained, HAKUNA CDN).
  Dark institutional theme (CSS moja, hakuna framework nzito). requirements.txt yake.

## BUILD ORDER (hatua za agent — zote kwenye PR moja; si limitation)
DB models → ingest (fixtures + artifacts halisi) → Command Deck → Portfolio → Live-actions+trace →
Trust/Compliance → Model Registry + LIVE-vs-PROMISED + attestation export → Pair×Strategy →
Diagnosis → VPS → Ledger/Lessons → roles/auth → tests. Fixtures za demo (hakuna live data bado)
zinaonyesha kila panel ikifanya kazi.

## NIDHAMU
- Read-only enforced (hakuna POST inayogusa trading). "No data" badala ya kubuni. Hakuna secret.
  Tests: ingest correctness (fixtures), no-fabrication (artifact tupu→no-data), read-only (hakuna
  trade-mutation endpoint), attestation reproducibility (hash stable). src/research HAIGUSWI.
