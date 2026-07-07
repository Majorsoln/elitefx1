# RUNBOOK — Paper Validation (mtihani wa kwanza wa mashine nzima)

*Chief Quant (Unified) → Operator (Japhet) | 2026-07-05 | Paper-mode; HAKUNA pesa, HAKUNA network,
HAKUNA data ya 26GB inayohitajika kwa run hii ya kwanza.*

> **Lengo:** kuthibitisha kwamba, kwenye PC yako yenye stack kamili (numpy/polars/duckdb/pyyaml),
> (a) modules zote zinapita self-test, na (b) mnyororo MZIMA unatembea end-to-end
> (Snapshot → Engine → Gate → Broker → Execution → Repository → Settlement).
> Chief ameiendesha kwenye CI: **smoke test PASS.** Sasa i-run kwenye PC yako = uthibitisho halisi.

---

## HATUA 1 — Sync repo (chukua kazi ya karibuni)

```bash
cd <njia-yako>/elitefx1
git checkout main
git pull origin main
```

## HATUA 2 — Andaa mazingira (mara moja tu)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## HATUA 3 — Self-test sweep (thibitisha kila module kwenye stack yako)

**Cross-platform (Windows/Linux/Mac) — amri MOJA:**

```bash
cd src/research
python run_selftests.py
```

**Unatarajia:** `SELF-TEST SWEEP: 10/10 PASS` (inajumuisha na e2e_paper_demo). Ikitokea FAIL
popote — **simama, bandika output kwa Chief.**

> *(NB: usitumie `for ... do ... done` wala `tail` kwenye Windows CMD — ni syntax ya bash/Linux.
> `run_selftests.py` inafanya kazi kila mahali.)*

## HATUA 4 — End-to-end paper smoke test (mnyororo mzima)

```bash
python e2e_paper_demo.py --run
```

**Unatarajia** (scenarios 3):
- **[A]** clean → `FILLED` + `settle pnl=37.5` (trade halali inapita)
- **[B]** akaunti karibu na daily-loss → `gate REJECTED` + `execute REFUSED` (**mtaji umelindwa** ✓)
- **[C]** evidence dhaifu → `ABSTAIN` (hakuna trade)
- Repository: `records: 7`, `integrity_check ... ok=True`
- Mstari wa mwisho: **`SMOKE TEST: PASS ✓`**

## HATUA 5 — Ripoti

Bandika kwa Chief output ya **HATUA 3 (mstari wa mwisho wa kila module)** + **HATUA 4 nzima**.
- Zote PASS → **mashine imethibitishwa kwenye PC yako.** Tunaendelea: Audit #6 → real-data validation.
- Yoyote FAIL → Chief atachunguza; ni tofauti ya mazingira (dependency/OS), si logic (imethibitishwa CI).

---

## Muhimu (mipaka ya run hii)

- Hii ni **smoke test ya wiring** — inathibitisha vipande vinaunganika, **SIO backtest wala edge claim**
  (snapshot ni synthetic, PnL ni ya mfano). *Profitable ≠ Tradable Edge.*
- **Live imezuiwa:** `broker_adapter` `mode=live` = refuse-stub hadi wewe (Project Director) uidhinishe
  artifact ya live (uamuzi wako uliobaki). Run hii ni paper 100%.
- Real-data validation (snapshots kutoka ticks zako halisi) ni **runbook tofauti** — itakuja baada ya
  smoke test hii + Audit #6.

*Protect capital first. Seek edge second. Scale only after proof.*
