# ELITEFX — DASHBOARD-V2 ROADMAP — "USER AELEWE MODEL" (requirements only)

> Directive ya PD 2026-07-22: "dashbord inapaswa kuonyesha taarifa zote muhimu na iwe rahisi ku
> interprate, tena iwe lugha rahisi ya trade na English, user anapaswa kujua na kufahamu hali ya
> model katika maamuzi yake yaliyopo na yaliyopita, pia awe na uwezo wa ku filter takwimu
> anayoyataka kirahisi. Hukifika hatua hiyo ya dashboard kuboresha, lete design mpya tujadili
> features na user roles."
>
> **HALI:** Hii ni ROADMAP ya MAHITAJI (requirements) tu. **DESIGN MPYA + majadiliano ya features
> na user-roles YAMEAHIRISHWA** hadi tufike hatua ya kuboresha dashboard (baada ya MODEL STEWARD).
> Hati hii inanasa kile ulichoomba ili tusisahau — SI design ya mwisho.

## KWANINI V2 (gap ya sasa)
Glass Box ya sasa (V1) ni sahihi na certified, lakini imejengwa kwa mtazamo wa **auditor/attestor**
(uthibitisho). Directive mpya inataka mtazamo wa **kuelewa** — user (hata lessee asiye quant)
aelewe model inafanya nini, kwa nini, na ni model gani ya kuamini, kwa lugha rahisi.

## MAHITAJI (requirements — yatajadiliwa kwa design tukifika hapo)

### R1 — Taarifa zote muhimu, mahali pamoja
Panorama moja inayoonyesha: status ya kila model, performance (learned vs practical), trades za
leo + za nyuma, compliance (sheria zimefuatwa?), VPS/heartbeat, pair × strategy. (V1 ina panels 9;
V2 = kuzipanga kwa **kuelewa**, si kwa audit.)

### R2 — Rahisi ku-interpret (si jedwali ghafi)
Kila namba muhimu iwe na maana kwa lugha ya kawaida: mfano badala ya "EV=+1.92R p=0.021" →
"Model hii ilipata wastani wa faida +1.92 kwa kila hatari 1 kwenye majaribio; uwezekano ni bahati
tu ni mdogo (2%)." Rangi/hali (nzuri / angalizo / hatari) badala ya namba peke yake.

### R3 — Lugha mbili: trade + English rahisi
Kila panel iwe na maelezo mafupi kwa **Kiswahili cha trade** na **English rahisi** (toggle au
pamoja). Hakuna jargon bila maelezo. Lengo: user asiye quant aelewe.

### R4 — Hali ya model: MAAMUZI YA SASA na YA NYUMA
User aone: model inafanya maamuzi gani SASA (live actions) NA aweze kupitia maamuzi YA NYUMA
(decision-trace ya trade yoyote iliyopita: kwa nini iliingia, sheria zipi zilipita, matokeo).
"Historia ya maamuzi" iwe rahisi kuvinjari — si kutafuta kwenye log ghafi.

### R5 — Filtering rahisi
User achague anachotaka kirahisi: kwa model, pair, tarehe (leo/wiki/mwezi/holdout), session,
matokeo (W/L), regime. Filter chips/dropdowns — si kuandika query.

### R6 — Roles (yatafafanuliwa kwenye design)
V1 ina roles: internal / attestor / lessee. V2 itapanua/kuboresha — **hili ndilo tutakalojadili
kwenye "design mpya"** (features per role: nani aone nini, lessee aone model zake tu bila IP,
n.k.). MT5 self-registration/token (Doctrine §9) inaingiza role mpya: **self-registered lessee**
anayeunganisha EA kwa token.

### R7 — Model Health panel (kutoka MODEL STEWARD)
Panel inayosoma `reports/model_steward.json`: practical-vs-learned, weakness map, "hali ya model"
kwa rangi. Hii ndiyo inayounganisha Steward na "user aelewe hali ya model."

## MIPAKA (haibadiliki V2)
- V2 inabaki **read-only mirror** (haiendeshi trades — engine ndiyo inatrade).
- Append-only audit + attestation export (V1) HAZIBADILIKI — ni msingi wa leasing.
- Anonymization ya token→model (§9.2) inaheshimiwa — hata monitoring operator haoni "user X = model Y".

## HATUA INAYOFUATA
1. **MODEL STEWARD kwanza** (inatoa data ya R7). ← tunapoanza sasa.
2. Baada ya Steward: **design mpya ya Dashboard-V2** → majadiliano ya features + user roles na PD
   (kama ulivyoagiza). Ndipo R1–R7 zitageuzwa kuwa design halisi + prompts za implementer.
