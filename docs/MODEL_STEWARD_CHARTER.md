# ELITEFX — MODEL STEWARD — "MWALIMU WA MODELS" (Doctrine V2 §8.2)

> Directive ya PD 2026-07-22: "tuwe na model ambayo itakuwa inafuatilia model zote uzaifu wao
> kulingana na mafunzo yao ... zoezi hilo litakuwa endelevu." MODEL STEWARD = meta-model
> (read-only) inayopima KILA model dhidi ya alichofundishwa, inatoa **ramani ya udhaifu** +
> **ajenda ya kuboresha** iliyopangwa. Si trader — ni mkaguzi/mwalimu wa endelevu.

## LENGO
Kupima **PRACTICAL (halisi) vs LEARNED (alichoahidi backtest)** kwa kila model, kutambua **wapi
udhaifu upo** (pair / regime / session / streak / cost), na kutoa **ajenda ya kuboresha iliyopangwa
kwa athari**. Steward HAITRADE, HAIBADILISHI model, HAIGUSI strategy configs — inasoma tu na kuripoti.
Ni "zoezi endelevu": kila baada ya data mpya (paper/forward) inakua na uwezo zaidi.

## KANUNI (za lazima — nidhamu ya taasisi)
1. **READ-ONLY META-MODEL.** Steward inasoma: `data/paper/paper_log.jsonl` (matokeo halisi + tag
   ya `learned_ev`), `docs/MODEL_REGISTRY.md` (learned/holdout EV per model), `docs/STRATEGIES.md`
   (proof za OOS). HAIANDIKI kwenye artifacts hizi — inaandika `reports/model_steward.md` PEKEE
   (+ JSON summary `reports/model_steward.json`).
2. **PRACTICAL vs LEARNED ni kipimo kikuu.** Kwa kila model: realized R distribution (halisi) dhidi
   ya learned_ev (ahadi). Divergence = practical − learned. Chanya = model inazidi ahadi; hasi =
   inashuka chini ya ahadi (**shrinkage** — Glass Box tayari inaonyesha hii per-trade).
3. **UAMINIFU WA SAMPLE (za lazima):** sasa "practical" = **validation replay**, SIYO forward halisi
   bado. Steward LAZIMA iandike hili wazi kwenye kila ripoti ("SAMPLE: replay/validation, si
   forward — power inakua na forward data"). HAKUNA kudai "model imethibitika forward" bila forward.
4. **ANTI-NOISE:** hakuna hukumu ya "udhaifu" kwa cell yenye N ndogo. Kila kipande cha ramani ya
   udhaifu kina **N** na **CI** (bootstrap ile ile ya golden — reuse, HAIANDIKWI upya). Cell yenye
   N < min_n → "INSUFFICIENT" (si "weak", si "strong"). min_n imewekwa kwenye config, default 30.
5. **HAKUNA SELECTION BIAS mpya** (LESSON-041): Steward inaripoti udhaifu wa model **iliyopo tayari**
   (proven), HAITAFUTI "best cell" kama strategy mpya. Ni diagnostics, si discovery. Ikipata cell
   nzuri ("model inafanya vizuri zaidi kwenye LOW-vol"), hilo ni **HYPOTHESIS** ya kupelekwa kwa
   njia ya kawaida ya registration — SI ruhusa ya kubadilisha model.
6. **ZERO golden/statistic fns kuguswa.** Steward inatumia bootstrap/CI functions zilizopo (import),
   haiandiki statistics mpya. Ikihitaji kipimo kipya → kinaenda kwenye module ya golden kwa
   registration ya Chief, si ndani ya steward.

## RAMANI YA UDHAIFU (weakness map — per model)
Kwa kila model (STRAT-001, STRAT-002, ...) vunja realized-R kwa nyanja hizi, kila cell = {N, mean_R,
CI, practical−learned}:
- **pair** (kama model ina pair >1 baadaye; sasa single-pair).
- **regime** (HTF context: trend/range/compression — kutoka state engine tag kwenye log).
- **session** (Asia/London/NY — kutoka as_of).
- **vol bucket** (LOW/MID/HIGH — atr_rel kama swing_family).
- **streak state** (baada ya W/L mfululizo — muhimu kwa FTMO path-risk; K4 design §5).
- **cost drag** (spread+slippage kama % ya gross — wapi cost inakula edge zaidi).

Kila cell inapata **verdict**: `HOLDS` (practical ≈ learned, CI inagusa learned), `SHRINKS`
(practical < learned, CI chini ya learned), `LIFTS` (practical > learned), `INSUFFICIENT` (N ndogo).

## AJENDA YA KUBORESHA (improvement agenda — ranked)
Toa orodha iliyopangwa kwa **athari inayotarajiwa × uhakika**, kila kipengele:
- **weakness** (cell + verdict + N + divergence).
- **hypothesis** ya sababu (kwa lugha ya trade: "cost inakula edge kwenye HIGH-vol entries").
- **proposed experiment** (design inayotekelezeka kupitia registration ya kawaida — SI auto-apply).
- **expected lift** kama inakadirika + **risk** ya kujaribu.
HAKUNA kipengele kinatekelezwa na Steward. Ni pendekezo kwa Chief/PD (kama SCIENTIST-D).

## OUTPUT
- `reports/model_steward.md`: (A) muhtasari per-model practical-vs-learned; (B) weakness map (jedwali
  per model, kila cell N+CI+verdict); (C) improvement agenda ranked; (D) SAMPLE-HONESTY note +
  data-provenance (commit, log line count, tarehe). Lugha: trade + English rahisi.
- `reports/model_steward.json`: summary ya kimashine (kwa dashboard baadaye kusoma — panel ya §8.2).
- **DASHBOARD HOOK (baadaye):** JSON hii = malighafi ya panel "MODEL HEALTH" kwenye Dashboard-V2.

## SELF-TEST (za lazima)
- **read-only:** run mbili mfululizo → artifacts (paper_log, registry) hazibadiliki (hash sawa).
- **anti-noise:** cell yenye N < min_n → verdict INSUFFICIENT (si weak/strong).
- **provenance:** ripoti ina commit + line-count za log; ikikosekana → fail.
- **honesty tag:** ripoti ina "SAMPLE: replay/validation" note; ikikosekana → fail.
- **determinism:** input ile ile → ripoti ile ile (bootstrap seeded).
- **no-golden-touch:** steward haina definition mpya ya episodes/pvalue (inaimport tu).

## MATOKEO
Zoezi endelevu: kila data mpya → Steward inasasisha ramani ya udhaifu + ajenda. Chief/PD
wanachagua majaribio ya kuboresha kutoka ajenda (kupitia registration). Model zinaboreshwa kwa
**ushahidi**, si hisia. Power inakua kadri forward data inavyoongezeka.
