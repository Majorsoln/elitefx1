# ELITEFX — FORWARD TRACK — "USHAHIDI HALISI" (Doctrine §8.1 evergreen + §3.1b)

> Lengo: kugeuza Model Steward kutoka REPLAY → FORWARD halisi. Steward inapata nguvu ya kweli pale
> engine inapoendesha kwenye bars ambazo HAKUNA model aliziona — data inayowasili BAADA ya leo.
> Paper — HAKUNA pesa halisi, HAKUNA saini ya PD inayohitajika (data + paper pekee).

## TATIZO (kwa nini "forward" ya sasa si forward)
`live_engine --run` = replay ya validation split (historia tuliyoitumia). Fills 864 = replay, si
ushahidi mpya. Forward HALISI = bars mpya (2026-07-24+) zinazowasili, decision KABLA ya matokeo —
pre-registered by construction (RUNBOOK_forward_paper_trading: hakuna lookahead/selection bias).

## MPAKA MTAKATIFU (§3.1b — LAZIMA)
- **FORWARD-START = 2026-07-24** (au tarehe ya kuanza). Forward = bars za tarehe HII na kuendelea TU.
- **Dirisha 2026-05 → 2026-07-24 = SEALED** (COMPLETE-EA acceptance). Forward mode **HAITASHUGHULIKIA
  KAMWE** dirisha hili. Guard ngumu: bar yenye as_of < FORWARD-START inakataliwa (si "forward").
- HOLDOUT (2025-01→2026-04) haiguswi (red-line iliyopo).

## AWAMU
### F1 — ENGINE FORWARD-APPEND (inajengeka sasa, bila MT5; inajaribika kwa fixture)
`live_engine --forward`: mode ya incremental —
- Inasoma watermark (as_of ya decision ya mwisho kwenye paper_log) → inashughulikia bars mpya TU
  (as_of > watermark AND as_of >= FORWARD-START). Append-only; resumable; **idempotent** (run mbili
  bila data mpya → hakuna rekodi mpya).
- Guard ya sealed window: as_of < FORWARD-START → SKIP (+ log ya sababu). HOLDOUT red-line inabaki.
- STRAT-001/002 configs HAZIBADILIKI. Fills/costs = episodes (honest, no-look-ahead). Golden 0.

### F2 — MT5 READ-ONLY DATA FEED (inahitaji MT5 kwenye PC ya Operator)
`mt5_data.py`: kuvuta H1 bars za hivi karibuni (USDCHF/USDJPY) kwa **kusoma TU** (MetaTrader5
`copy_rates_*`) → forward data store. HAKUNA trading, HAKUNA order, HAKUNA account-write — market
data pekee. Hii ndiyo nusu SALAMA ya MT5 (order-execution + token + PD-signature = §9.3, baadaye).

## CADENCE (RUNBOOK — baada ya F1+F2)
Kila siku/wiki (Operator): (1) `mt5_data.py` vuta bars mpya → (2) `live_engine --forward` append →
(3) `model_steward.py` (forward practical-vs-learned) → (4) dashboard `ingest` → scorecard inasasishwa.

## KANUNI ZA TATHMINI (RUNBOOK_forward_paper_trading — zinatumika)
- Chini kabisa kabla ya hitimisho: **siku 20+ / trades 30+**. N ndogo mwanzoni — Steward inaandika
  "forward N=x (inakua)".
- Hakuna kubadilisha config katikati bila version mpya. ABSTAIN/REJECTED nyingi = mfumo unafanya kazi.
- Steward SAMPLE-note inabadilika: "replay/validation" → "FORWARD live (N=x, tangu 2026-07-24)" pale
  forward data inapokusanyika. Uaminifu: profitable ≠ tradable edge; N ndogo = si proof.

## MATOKEO
Ushahidi wa kweli wa STRAT-001/002 (forward, pre-registered) unakusanyika kila wiki → Steward + scorecard
zinaonyesha FORWARD performance → msingi wa uamuzi wa live (MT5 §9.3 + PD signature) baadaye.

---

## ROLLOUT (demo → VPS → live; directive ya PD 2026-07-25)
Wakati WOTE hadi Faza 4 = **demo/paper** (read-only market data; hakuna order). Terminal data
HAIGUSWI (copy_rates read-only). Forward store = folda tofauti (data/forward).

| Faza | Mahali | Muda | Inapima | Kigezo cha kusonga |
|------|--------|------|---------|--------------------|
| 1 SOAK | PC (demo) | siku 2–3 | UIMARA WA BOMBA (crash? data? append? dashboard?) — SI faida | bomba safi, logs bila error |
| 2 EXTEND | PC (demo) | wiki 1–2 | forward N inaanza kukua; hakuna tatizo | stable + trades zinaingia |
| 3 VPS | VPS (demo) | mwezi 1 | 24/7 mfululizo; forward N ya maana | uptime + N≥ (siku 20/trades 30) |
| 4 LIVE | VPS (live) | — | — | §9.3 (orders+token) + **SAINI YA PD** + forward imethibitika |

**forward_cycle** = automation inayowezesha Faza 1–3 (amri moja + log; Task Scheduler/cron).
Faza 1 haitahukumu EV (nr7 teule — trades chache). Trades/EV = wiki (Faza 2–3).
