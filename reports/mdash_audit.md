# M-DASH AUDIT — "THE GLASS BOX" DASHBOARD CERTIFICATION (M-DASH-QA)

> AUDITOR huru (mtindo wa SCIENTIST-D M3-QA — *endesha mwenyewe, usiamini maandishi*).
> Lengo: certify dashboard ya `dashboard/` KABLA haijatumika kama "kioo cha taasisi" kwa wateja
> wanaokodisha models. Rejea: `docs/DASHBOARD_CHARTER.md`, `docs/DOCTRINE_V2.md §4/§5`.
> Tarehe: 2026-07-20 · Commit ya msingi: `446ba6a` (M-DASH build) juu ya `main`.

---

## VERDICT YA JUMLA: **CERTIFIED-WITH-FIXES**

Kiini cha glass-box kinasimama: **hakuna njia ya kuanzisha/kubadilisha trade** (READ-ONLY halisi),
na **hakuna panel inayobuni namba kutoka hewani** (artifact tupu → "no data"). Roles/leasing,
attestation reproducibility, na ingest idempotency zote zinapita majaribio ya adversarial.

Lakini findings **7** zinabaki — mbili (**F1, F2**) zinagusa moja kwa moja *uso ambao mteja-lessee
anaukagua* (immutability ya audit trail + uadilifu wa namba za attestation). Kwa hivyo:

- **Matumizi ya NDANI (internal monitoring):** RUHUSA sasa hivi.
- **Matumizi ya WATEJA/LEASING (mteja anapewa access ya lessee + attestation):** RUHUSA **BAADA**
  ya F1 + F2 + F3 kurekebishwa. Hizi ndizo zinazoweza kudanganya mteja-taasisi au kuvunja
  "glass box" trust.

Hakuna finding ya kiwango cha **REJECTED**: masharti mawili yasiyojadilika — READ-ONLY (hakuna
trade mutation) na NO-FABRICATION (empty artifact → no-data) — **yote yanashikilia**.

---

## KAZI ILIYOENDESHWA (reproducible)
- `manage.py test` → **9/9 PASS** (`dashboard/`, `pip install Django reportlab`).
- `manage.py ingest --demo` (fixtures) + `manage.py ingest` (artifacts halisi za repo).
- `manage.py runserver` + curl end-to-end: login flow, panels 10/10 → 200, attestation → 200.
- Adversarial probes: `scratchpad/adversarial.py` (loaders) + `scratchpad/http_probe.py` (HTTP).
- Grep ya secrets/`src.research` imports repo-nzima.

---

## VERDICT KWA KILA PANEL

| # | Panel | Verdict | Note |
|---|-------|---------|------|
| 1 | Command Deck | ✅ PASS | KPIs zote zina chanzo; "no data" wazi (heartbeat/perf/score) |
| 2 | Portfolio | ⚠️ PASS* | equity curve inachanganya units kama `pnl_r` haipo — **F2** |
| 3 | Live Actions + Decision Trace | ✅ PASS | trace signal→policy→compliance→fill, kila hatua na `source_ref` |
| 4 | Trust / Compliance | ✅ PASS | score = fails/checks halisi; violation ya demo (#7 max_spread) inaonekana |
| 5 | Model Registry + Attestation | ⚠️ PASS* | WATCH rows zinaanguka (**F4**); attestation haina commit hash (**F6**) |
| 6 | Pair × Strategy Matrix | ✅ PASS | cells zina N/EV/win% + `source_ref`; drill-down 200 |
| 7 | Diagnosis / Alerts | ⚠️ PASS* | alert bila `ts` inapata `now()` fabricated — **F3** |
| 8 | VPS / System Health | ⚠️ PASS* | heartbeat yenye `ts` mbovu → OPERATIONAL ya uongo — **F3** |
| 9 | Research Ledger + Lessons | ✅ PASS | ledger/lessons/reports mirror; report_view traversal-safe |

`*` = inafanya kazi lakini ina finding ya latent (haiharibu demo; itaumiza kwa data halisi/mbovu).

---

## MATOKEO KWA KIGEZO CHA CHARTER

### 1. READ-ONLY (kiini) — **CERTIFIED** ✅
- **Hakuna import ya `src/research`** popote kwenye `dashboard/` (grep clean). Loaders zinasoma
  files tu (jsonl/md/json/parquet). Separation ya V2 §4 imeheshimiwa.
- Kila view ina `@require_GET`. Probe: `POST/PUT/PATCH/DELETE` kwa panels + `attest.json` →
  **405 zote**; `Trade.count()` na `pnl` **hazibadiliki**. (Repro: `http_probe.py`.)
- Hakuna URL yenye jina la mutation (`trade_create/order_create/execute/buy/sell`) — test `c2`.
- Admin ipo lakini internal-ops tu (auth-gated). **HATA MOJA ya trade-init haipo.**

### 2. NO-FABRICATION — **CERTIFIED (kiini)** ✅ + findings za latent
- Artifact zisipokuwepo kabisa → kila loader → `(0, "no data: <path>")`; panels → HTTP 200 na
  neno "no data" (test `test_b`, na runserver real-ingest: paper/alerts/heartbeat = 0 records).
- **HAKUNA panel inayobuni namba** ambazo hazina chanzo. Kila mirror model una `source_ref`.
- Lakini tazama **F2** (unit-mix) na **F3** (fabricated `ts`) hapa chini: si "kubuni namba kutoka
  hewani" bali ni **fallback zinazopotosha** kwenye fields za missing — bado ni ukiukaji wa
  glass-box ("kila namba iaminike").

### 3. INGEST INTEGRITY — **CERTIFIED-WITH-FIXES** ⚠️
- **Idempotent:** re-ingest → counts zile zile (`update_or_create` + natural keys). Test
  `test_a` inathibitisha; nimethibitisha tena kwa mkono. ✅
- **Data mbovu:** loader ina-**crash** kwenye JSON mbovu (**F5**) — kinyume na charter
  "loader inakubali data mbovu bila ku-crash". Athari ndogo (loaders nyingine zinaendelea;
  hakuna partial-corruption inayohifadhiwa) lakini source hiyo inakosa ingest.
- **Counts zinalingana na artifacts:** demo → 10 trades, 1 violation, hash-checks OK. ✅

### 4. ATTESTATION — **CERTIFIED-WITH-FIXES** ⚠️
- **Reproducible:** export mbili → hash ile ile; `generated_at` iko NJE ya payload iliyo-hash
  (determinism). Nimere-compute hash kwa nje ya module: **inalingana** (repro `P7`). ✅
- **Inakaguliwa na mtu wa nje:** canonical JSON (`sort_keys`, separators) + SHA-256. ✅
- **PENGO (F6):** payload haina **git commit hash**. Charter panel 5 + V2 §5.2 zinadai
  "hash + chanzo/**commit** + reproducible". `source_ref` ya performance ni label
  ("derived: Trade mirror"), si commit-pinned. Auditor wa nje hawezi ku-pin repo state halisi.

### 5. ROLES / LEASING — **CERTIFIED** ✅
- **lessee** anaona **model MOJA** aliyokodisha PEKEE. Probe (`http_probe.py`):
  - `STRAT-002` (asiyokodisha): registry/attest.json/attest.pdf → **403 zote**.
  - Panels zote za ndani (deck/portfolio/actions/ledger/matrix/alerts/vps/compliance/audit) → **403**.
  - `attest.json` ya model **yake** → 200, na **haitaji STRAT-002** popote (hakuna cross-leak).
  - Landing yake → lease yake tu (`STRAT-001`), si `STRAT-002`.
- **attestor** → compliance/registry/audit + attestation ya model yoyote; panels za utendaji → 403.
- **anonymous** → 302 → `/login/?next=…`. **Hakuna leak ya kitaasisi.** ✅

### 6. SECRETS — **CERTIFIED** ✅
- Grep repo-nzima: **hakuna** api-key/token/broker-login/private-key hardcoded kwenye `dashboard/`.
- `SECRET_KEY`, DB path, hosts, artifact paths — zote kupitia **env** (V2 §5). ✅
- **F7 (INFO):** default za dev ni insecure (`SECRET_KEY="dev-insecure-…"`, `DEBUG=1`). Env-
  overridable, lakini prod-deploy bila kuweka env ingeweza kuvuja tracebacks/attestation internals.

---

## FINDINGS (kila moja + chanzo + repro)

### F1 — Audit trail immutability HAIJALINDWI kwenye queryset level  · **MEDIUM**
`dashboard/monitor/models.py:187-193` — `AuditEvent.save()/delete()` zinakataa update/delete, LAKINI
`QuerySet.update()` na bulk `.delete()` **hazipiti** hizo methods (Django ORM haiiti `Model.save()`
kwa bulk ops).
- **Repro (`adversarial.py` P6/P6b):**
  `AuditEvent.objects.filter(action='probe').delete()` → ilifuta rekodi; `.filter(...).update(detail='TAMPERED')`
  → ilibadilisha rekodi. Vyote **vilifaulu** bila `ValueError`.
- **Athari:** V2 §5.1 "immutable audit trail" ndiyo *hasa* kile mteja-lessee anakiamini. Immutability
  ni **app-level tu** — code/shell yoyote yenye DB access inaweza kufuta/kubadilisha ushahidi wa nani
  aliangalia attestation. Kwa bidhaa ya kukodisha, hili linavunja "control nzuri".
- **Fix:** DB-level append-only (trigger / grant-revoke UPDATE,DELETE kwa app DB-user), AU custom
  Manager inayozuia `update/delete`, AU write-once store. Kiwango cha chini: **document** kwamba
  immutability ni app-level pekee.

### F2 — Unit-mixing kwenye R-multiple aggregations (currency ↔ R)  · **MEDIUM**
`loaders.py:285` (`rebuild_strategy_perf`) + `views.py:45` (`_equity_series`): `pnl_r` ikiwa `None`,
code inarudi kwenye **currency `pnl`** na kuiingiza kwenye metrics za **R** (`net_r`, `expectancy_r`,
equity curve).
- **Repro (`adversarial.py` P4):** settlement moja `realized_pnl=250` (currency, hakuna `pnl_r`) +
  moja `pnl_r=1.0` → StrategyPerf: `net_r=251.0`, `expectancy_r=125.5`. Namba isiyo na maana
  inayoonyeshwa kama R.
- **Athari:** demo zote zina `pnl_r` → latent; settlement halisi ya kwanza isiyo na `pnl_r`
  itaonyesha equity/expectancy za uongo kwenye **Portfolio, Deck KPI, na attestation `live_performance`**.
  Hii ni namba "yenye chanzo" lakini **semantiki batili** — inavunja glass-box "kila namba iaminike".
- **Fix:** KAMWE usichanganye units — `pnl_r=None` → **exclude** kwenye R-metrics (au onyesha
  "no R data"), weka currency na R **tofauti kabisa**.

### F3 — Timestamp za kubuni (`now()`) kwa `ts` inayokosekana/mbovu  · **LOW-MEDIUM**
`loaders.py:255,267` — `load_alerts`/`load_heartbeat`: `_dt(ts) or datetime.now(...)`.
- **Repro (`adversarial.py` P2/P3):** heartbeat `{"ts":"not-a-date"}` → inahifadhiwa na `ts=now()`
  → VPS panel inaonyesha **OPERATIONAL** (age < 15min) kwa heartbeat yenye data taka; alert bila
  `ts` inapata `now()`.
- **Athari:** VPS/Deck banner (OPERATIONAL/DEGRADED/OFFLINE) hutegemea `ts`. Ku-stamp `now()`
  kunaweza **kuficha feed iliyokufa/stale** — kinyume kabisa na kusudi la panel. Ni fabrication ya
  field ya `ts`.
- **Fix:** kataa/flag rekodi zenye `ts` batili/kukosekana badala ya ku-stamp `now()`.

### F4 — Registry WATCH candidates zinaanguka kimya  · **LOW**
`loaders.py:112-113` — `_ROW` inahitaji **columns 6**; jedwali la WATCH kwenye
`docs/MODEL_REGISTRY.md` lina **5** (`id|class|status|signal|njia`), hivyo `C2-WATCH`, `SWING-WATCH`,
`K4-WATCH` **hazi-ingest kamwe** (ingawa comment ya loader inadai inazishughulikia).
- **Repro:** `ingest` halisi → `ModelVersion` **3 tu** (STRAT-001/002, K4-filter), ilhali
  source-of-truth ina **6**.
- **Athari:** "product catalog" haijakamilika bila dalili. Si fabrication, bali **pengo la
  ukamilifu** la glass-box.
- **Fix:** parse jedwali la 5-column WATCH (au regex inayonyumbulika kwa 5-6 columns).

### F5 — JSON mbovu inasitisha loader (badala ya skip+log)  · **LOW**
`loaders.py:35-37` (`_read_jsonl`) + `load_heartbeat`: mstari mmoja mbovu → `JSONDecodeError`
inayosambaa. Charter §NIDHAMU: "loader inakubali data mbovu bila ku-crash/kupotosha."
- **Repro (`adversarial.py` P1/P2):** paper_log yenye mstari mbovu → `JSONDecodeError`.
- **Athari:** ndogo — loaders nyingine kwenye command zinaendelea; `update_or_create` = hakuna
  partial-corruption inayohifadhiwa; panel inaonyesha stale/no-data kwa source hiyo. Lakini source
  hiyo yote inakosa ingest kwa sababu ya mstari 1.
- **Fix:** skip + log mistari mibovu; endelea.

### F6 — Attestation haina git commit hash  · **LOW**
`attest.py:18-45` (`build_payload`): ina `source_ref` (paths) lakini **hakuna commit hash**.
Charter panel 5 / V2 §5.2 zinadai "hash + chanzo/**commit** + reproducible".
- **Fix:** ingiza `git rev-parse HEAD` (commit ya artifacts) kwenye payload iliyo-hash.

### F7 — Default za dev insecure (SECRET_KEY / DEBUG)  · **INFO**
`settings.py:15-16`: `SECRET_KEY` default = `"dev-insecure-glassbox-key-change-me"`, `DEBUG=1`.
Env-overridable, lakini **fail-open**. Fix: fail-closed kama `SECRET_KEY` haijawekwa wakati
`DEBUG=0`; default `DEBUG=0`.

---

## MAMBO YALIYOTHIBITISHWA KUWA IMARA (hakuna hatua)
- Path traversal kwenye `report_view` (`views.py:240-255`): `reports/../../etc/passwd`,
  URL-encoded, `../../../etc/passwd` → **404 zote** (resolve + `startswith(base)` + `.md` suffix).
- CSRF/auth middleware active; logout ni POST + csrf.
- `attestation` payload ni model-scoped (hakuna cross-model bleed kwenye `build_payload`).
- Charts (`glasschart.js`) ni self-contained (hakuna CDN) — sambamba na charter STACK.

---

## RUHUSA / KATAZO LA MATUMIZI
- ✅ **Internal monitoring:** RUHUSA sasa (findings hazizuii matumizi ya ndani).
- ⛔→✅ **Client/lessee leasing:** ZUIA hadi **F1 (audit immutability)** + **F2 (unit-mix)** +
  **F3 (fabricated ts)** zirekebishwe — hizi zinagusa uso ambao mteja-taasisi anaukagua/anaamini.
- 🔵 **Kabla ya prod-deploy:** shughulikia **F6** (commit hash — attestation ndiyo bidhaa) + **F7**
  (secure defaults). F4/F5 = polish ya ukamilifu/uimara.

---

## APPENDIX — REPRO
```
cd dashboard && pip install "Django>=4.2" reportlab
python manage.py test                       # 9/9
python manage.py migrate && python manage.py ingest --demo
python manage.py bootstrap_roles --demo-users
python manage.py runserver                  # login: internal-demo / internal-demo
# adversarial:
python manage.py shell < scratchpad/adversarial.py     # F1-F6 loaders/attest
ELITEFX_ALLOWED_HOSTS=...,testserver python manage.py shell < scratchpad/http_probe.py  # read-only/roles/traversal
```
(scripts za probe: tazama commit hii / scratchpad ya session ya audit.)
