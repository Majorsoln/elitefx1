# Metals Support (XAUUSD) — Implementation Report (C2 Addendum)

*2026-07-09 | IMPLEMENTER-A | Chief C2 addendum (2026-07-09) | Rules 1-8 | NO ML*

> **METALS SUPPORT (task a).** Fungua XAUUSD (pip=0.01, quote 2dp) kwenye pip-handling zote za
> repo — bila kuvunja FX. XAG inabaki gated (hakuna data). XAUUSD inaingia GRID_C2 TU baada ya hii
> ku-approve (task b, Chief/Operator). Format: Rule 8.

---

## Implementation Report

**Deliverables (modules zilizoguswa):**

| Faili | Mabadiliko |
|-------|-----------|
| `market_state_engine.py` | `pip()`: XAU-gate iliyokuwa inaraise → **`XAU → 0.01`**; XAG bado inaraise (hakuna data). self-test: pip metals check |
| `paper_trader.py` | `PIP_SIZE`/`PIP_VALUE` (lambda → function): XAU → `0.01` / `1.0`; self-test [5] XAUUSD signal |
| `strat_signal.py` | `_pip_size` (XAU → `0.01`), `_dec` (XAU → `2`); self-test [6] metals |

- **market_state_engine.pip() = chanzo kimoja** — `event_quality_report`/`strategy_lab`/`strength_lab`
  zinaimport `pip` kutoka hapa (load_pair/load_window), kwa hiyo fix moja inazifikia zote (hakuna
  code change kwao — pip transitive).
- **XAUUSD pip = 0.01** (quote 2dp); **pip_value ≈ $1/pip** kwa lot ya 100oz (broker-dependent — tazama
  Known Limitations). Assumption imewekwa wazi.
- **XAG (silver) inabaki gated** (`ValueError`) — hakuna data/testing; metals support = XAU pekee sasa.

## Self Tests — zote PASS

```text
market_state_engine  pip metals: XAUUSD=0.01 · EURUSD=0.0001 · USDJPY=0.01 · XAG-gated=True
paper_trader         [5] XAUUSD: pip=0.01 pip_val=1.0 signal FILLED (qty 0.24 lot, sl_pips 500, risk $120)
strat_signal         [6] metals: XAUUSD pip=0.01 dec=2 (FX intact: EURUSD 0.0001/5, USDJPY 0.01/3)
FULL SWEEP: 18/18 PASS (FX HAIJAVUNJIKA — regression safi)
```

## Known Limitations

1. **pip_value ya XAUUSD = $1/pip (lot 100oz) ni ASSUMPTION** — broker-dependent (contract size + quote
   currency). Sizing halisi ya gold inahitaji pip_value ya broker (MWONGOZO/MT5). Imeandikwa wazi kwenye
   `paper_trader.PIP_VALUE`.
2. **XAUUSD haijaingia config pairs bado** — metals support (pip) imefunguliwa; kuiweka GRID_C2/data ni
   task b (Chief/Operator, baada ya approval). `grid_c2` tayari ni pair-agnostic (itaikubali).
3. **XAG (silver) gated** — hakuna data; pip support = XAU pekee. Kuifungua = kazi tofauti + data.
4. **Gold volatility tofauti na FX** — pip=0.01 ina maana sl_pips kubwa (mf. $5 SL = 500 pips); metrics/
   sizing za gold zitakuwa scale tofauti. S1-C2 backtest ndiyo itathibitisha tabia halisi (data ndiyo hakimu).

## Open Questions

1. **pip_value halisi ya XAUUSD** — Operator/MWONGOZO athibitishe contract size + pip_value ya broker
   (nimeweka $1/pip/100oz kama default). Inaathiri sizing ya gold pekee.
2. **XAUUSD kwenye GRID_C2** — je iongezwe pairs za config sasa (task b) au isubiri backtest ya kwanza?
   Pendekezo: Chief/Operator waamue baada ya approval ya metals support hii.
3. **XAG support** — je ifunguliwe pia (data ikipatikana)? Kwa sasa gated kimakusudi.

---

*Metals support: XAUUSD pip=0.01 (2dp) kwenye market_state_engine/paper_trader/strat_signal; XAG gated;
pip_value=$1/pip/100oz (assumption). FX haijavunjika (sweep 18/18). XAUUSD -> GRID_C2 = task b (baada ya
approval). NO ML. Profitable ≠ Tradable Edge.*
