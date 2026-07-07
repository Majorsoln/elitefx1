# RUNBOOK — Real-Data Validation (mashine na data yako halisi)

*Chief Quant (Unified) → Operator (Japhet) | 2026-07-07 | Paper-mode; HAKUNA pesa. Hii inahitaji
data yako halisi (states za ticks, ~26GB) — ndiyo mtihani wa kwanza wa mnyororo na evidence HALISI.*

> **Tofauti na paper smoke test:** ile ilitumia snapshot ya kubuni (synthetic). HII inajenga
> **Evidence Snapshots kutoka ticks zako halisi** (njia ileile iliyotumika kwenye reports zote),
> kisha inazipitisha: real evidence → decision → gate → repository.
>
> **⚠️ Tegemeo la uaminifu (Chief):** mfumo utaABSTAIN **mara nyingi** — hiyo ndiyo TABIA SAHIHI
> (doctrine: value halisi ni hasi → protect capital, P26). Hii inathibitisha **MASHINE inafanya
> kazi na evidence halisi**, SIO kwamba ina faida. *Profitable ≠ Tradable Edge.*

---

## HATUA 1 — Sync + hakikisha states zipo

```bash
cd <njia-yako>/elitefx1
git checkout main && git pull origin main
```

Driver inahitaji **state data yenye OHLC** (ndiyo iliyotumika kwenye reports zako). Kama
umeshaijenga (reports zilitoka hapo), ruka HATUA 2. Kama huna uhakika, HATUA 3 itakuambia wazi
(`HITILAFU: state parquet haina OHLC`) — hapo rudi HATUA 2.

## HATUA 2 — (kama inahitajika) Jenga states kutoka ticks

Hii ni **mchakato wako wa kawaida** wa data (uliozalisha reports). Kwa ufupi:

```bash
cd src/research
python market_state_engine.py        # jenga states kutoka ticks (kwa data_config.yaml paths)
```

*(Kama pipeline yako ya states ina hatua zaidi — volume bars, n.k. — endesha kama kawaida hadi
state parquet yenye OHLC iwe tayari.)*

## HATUA 3 — Endesha mnyororo kwa evidence HALISI

```bash
cd src/research
python real_data_paper_run.py --policy conservative
```

Kisha rudia kwa policies mbili zingine (kulinganisha tabia):

```bash
python real_data_paper_run.py --policy capital_preservation
python real_data_paper_run.py --policy aggressive
```

**Unatarajia** (kila run):
- `Snapshots N zimejengwa` — evidence halisi kutoka events zako
- Orodha: kila event → action (**nyingi zitakuwa ABSTAIN** — sahihi)
- `DECISIONS: N` + breakdown (ABSTAIN nyingi, labda SELECT chache kwa aggressive)
- `GATE (kwa SELECT): VALIDATED=.. REJECTED=..` — FTMO eligibility kwa yale yaliyochaguliwa
- `REPOSITORY: records=.. integrity_ok=True` — rekodi halisi zenye provenance → snapshot

## HATUA 4 — Ripoti

Bandika kwa Chief output ya run zote tatu. Chief atatafsiri:
- **ABSTAIN nyingi + integrity ok** → mashine inasoma evidence halisi na kuamua kwa usahihi
  (protect capital). **Real-data validation PASS.**
- **capital_preservation vs conservative vs aggressive** → tofauti ya tabia (aggressive itaSELECT
  zaidi) inaonyesha policy-injection inafanya kazi kwa data halisi.

---

## Muhimu (mipaka)

- Hii ni validation ya **decision machinery kwenye evidence halisi** — SIO backtest, SIO edge claim,
  SIO paper-trading ya mfululizo. Broker/execution wiring ilishathibitishwa (smoke test).
- **Hakuna pesa. Hakuna live.** (`mode=live` = refuse-stub hadi artifact yako.)
- Hatua zinazofuata baada ya hii: (a) **paper-trading run ya mfululizo** (time-ordered snapshots →
  decisions → paper fills → PnL log — runbook tofauti); (b) maamuzi yako 2 (live artifact +
  max_spread); (c) real-data snapshots → **K4 datasets** (Track B: E3 outcomes = training data).

*Protect capital first. Seek edge second. Scale only after proof.*
