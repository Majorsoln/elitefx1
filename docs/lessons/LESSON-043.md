# LESSON-043 — Steward weakness-map dimensions LAZIMA ziwe EX-ANTE (si outcome-conditioned)

**Tarehe:** 2026-07-22 · **Chanzo:** MODEL STEWARD v0 review (STRAT-001 cost=LOW-DRAG "SHRINKS")

## Tukio
Steward v0 ilipanga agenda #1: *STRAT-001 cost=LOW-DRAG → SHRINKS (mean −2.211, divergence −4.131,
N=212)*, na cost=HIGH-DRAG → LIFTS (mean +8.368, **CI [8.164, 8.566]**). Kwa juu inaonekana ni
udhaifu halisi wa kushughulikia. **SIYO.**

## Kasoro
Dimension ya `cost` ilikuwa: `drag = (spread+slippage) / (|pnl_pips| + cost)`, median-split.
**`pnl_pips` ni MATOKEO ya trade.** Kugawa cells kwa kiasi kinachotokana na matokeo = **conditioning
on the outcome** — kunatengeneza cells za uongo (spurious). Trade huwezi kujua ex-ante itakuwa
LOW-DRAG au HIGH-DRAG kwa sababu inategemea move iliyotokea (ambayo hujui wakati wa entry).

**Ishara ya artifact (tell):** CI ya HIGH-DRAG ilikuwa **ultra-tight [8.164, 8.566]** (half-width
~0.2 pips kwa N=211) — haiwezekani kwa mchanganyiko halisi wa W/L; ni dalili kwamba bucketing
inakata usambazaji wa pnl kwa ukubwa (magnitude), si kwa hali huru. Mean ya jumla +3.066 imepasuliwa
kimitambo kuwa +8.368 / −2.211. "SHRINKS" ile ni nusu ya artifact, SI udhaifu unaotekelezeka.

## Kanuni (ya lazima kwa Steward na diagnostics zote)
1. **Kila dimension ya weakness-map LAZIMA iwe EX-ANTE observable** (inajulikana wakati wa entry):
   session, vol (atr/SL), streak (W/L za nyuma), spread-at-entry, cost-in-pips (absolute). ✓
2. **HAKUNA dimension iliyo function ya outcome** (pnl, realized move, exit) kwenye numerator/
   denominator ya bucketing. Kugawa kwa matokeo = circular; verdict inakuwa artifact. ✗
3. **Tell ya artifact:** CI ndogo isiyo ya kawaida au ±split ya symmetric ya mean ya jumla → shuku
   outcome-conditioning; kagua ufafanuzi wa dimension kabla ya kuamini verdict.
4. Cost-sensitivity SAHIHI: bucket kwa **cost ya absolute (spread+slippage pips) tercile** — huru na
   pnl. Swali halali: "model inashuka lini cost iko juu?" — bila kugawa kwa matokeo.

## Athari
- Agenda #1 ya Steward v0 (cost=LOW-DRAG SHRINKS) **IMEKATALIWA** — ni artifact, si udhaifu. HAKUNA
  action juu yake. STRAT-001/002 zinabaki **HOLDS** (headline sahihi).
- STEWARD-FIX v0.2: badilisha `_cost_bucket` → ex-ante absolute-cost tercile (hakuna pnl kwenye
  denominator). Dimensions nyingine (session/vol/streak) ni ex-ante — safi, zinabaki.
- Kanuni ya jumla: **mwalimu (Steward) naye curriculum yake lazima i-certify** (GIGO) — diagnostics
  zenye contamination zinaweza "kupata" udhaifu wa uongo tukazipatia model tiba ya ugonjwa isiokuwepo.
