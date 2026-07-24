# LESSON-044 — Anonymization ni per-SURFACE, si per-VIEW (funga KILA route, jaribu 403)

**Tarehe:** 2026-07-22 · **Chanzo:** DASH-V2-A3 review (lessee raw-attestation back-door)

## Tukio
Awamu 3 ilijenga LESSEE VIEW iliyo anonymized vizuri (/my/ — hakuna pair/internal; no-leak tests
PASS). LAKINI routes za ZAMANI zilibaki: `/registry/<model_id>/` + `/registry/<model_id>/attest.{json,
html,pdf}` zinatumia `@model_access` inayompa **lessee** ruhusa ya model aliyoikodi. `attest.build_payload`
inarudisha `"model_id":"STRAT-001"` + Trade records zenye **pair**. Kwa hiyo lessee-demo (lease STRAT-001)
angeweza kufungua `/registry/STRAT-001/attest.json` na kuona internal-id + pair — **anonymization yote
imevunjika kupitia mlango wa nyuma**, ingawa view mpya ilikuwa safi.

## Kanuni (complete mediation / defence-in-depth)
1. **Anonymization/authorization ni sifa ya kila SURFACE (route), si ya view moja mpya.** Kujenga view
   mpya iliyo safi HAKUUlinzi IP kama routes za zamani za role ile ile bado zinafikika.
2. **Funga KILA njia ya data ya role, si tabs/nav tu.** Kuondoa link kwenye nav HAKUTOSHI — route
   ikibaki hai + decorator inaruhusu, ni back-door (URL-guessing, hasa id rahisi kama STRAT-001).
3. **Jaribu NEGATIVE (403), si happy-path tu.** Kila anonymized-role: andika test kwamba route ZOTE za
   zamani zinazoweza kuvuja (registry/attest/api) zinarudisha 403 kwa role huyo — assertNotContains
   haitoshi kama route nyingine bado inatoa payload mbichi.
4. **Superseding decisions zinafuta nia za zamani kwa uwazi.** §5.4 (lessee=leased attestation raw)
   imefutwa na §9 (KAIROS anonymization). Attestation ya lessee itarudi ANONYMIZED (call-sign, hakuna
   pair/internal) — SI raw internal payload.

## Athari
- FIX: `model_access` → internal/attestor TU (ondoa lessee-lease grant). registry + attestation
  zinafungwa kwa lessee (403). Lessee anahudumiwa KIKAMILIFU na /my/ (anonymized).
- Anonymized attestation-by-call-sign (lessee-facing) = kazi ya baadaye (Awamu 4+). Hadi hapo, lessee
  hana raw attestation (usalama > feature).
- Test: lessee → /registry/<internal>/ + /attest.{json,html,pdf} = 403 (negative tests za lazima).
