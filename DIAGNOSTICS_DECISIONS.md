# Kwa Nini Tunabadilisha Mtazamo — Maamuzi Yanayotokana na Data

*Hati hii inaeleza **kwa nini** tunabadilisha baadhi ya mawazo ya awali ya mfumo,
kwa kutumia **majibu halisi** ya `reports/feature_diagnostics.md`. Kanuni ya MFUMO:
"Hakuna kinachoenda mbele bila kuthibitishwa kwa data." Diagnostics ndio utekelezaji
wa kanuni hiyo kwa **features** — kabla ya kujenga model.*

---

## 0. Kwanza: je matokeo ni ya kuaminika (sio bugs)?

Kabla ya kubadilisha lolote, tulihakiki kuwa matokeo si artifact ya code:

| Jaribio | Predictive IC | Hit-rate | Maana |
|---------|---------------|----------|-------|
| Signal **uliojengwa** (known) | 0.995 | 0.975 | Code INAGUNDUA signal ikiwepo |
| **Null** (hakuna uhusiano) | 0.001 | 0.4998 | Code haina bias — inatua 0.500 |
| **Data halisi** | ~0.003 | ~0.494 | Hakuna predictive value (halisi) |

- Kama code ingefuta signal kimakosa → jaribio la 1 lingetoa ~0 (lilitoa 0.995).
- Kama code ingekuwa na bias → null ingetoa ≠0.500 (ilitoa 0.4998).
- **Hitimisho:** machinery ni sahihi → matokeo ni ukweli wa soko.
- **Corroboration:** fat tails za GBPUSD (−9.4%) = Brexit (tukio halisi); ACF(r)≈0 vs
  ACF(r²)>0 kwenye hesabu moja huzuia uwezekano wa bug ya `corr`.

---

## 1. Model 1 — Toka Gaussian HMM → **Student-t / vol-standardized**

**Report inasema:** D1 log-returns zina **excess kurtosis > 1 kwa 9/9** — kali sana:
GBPUSD **25.9**, EURGBP 18.0, EURJPY 13.0; skew hasi (crash risk).

**Mtazamo wa awali:** HMM (kwa kawaida Gaussian emissions).

**Kwa nini tubadilishe:** Gaussian inadhani ~99.7% ya data iko ndani ya 3σ. Kwa
kurtosis 25.9, matukio ya 6σ–10σ hutokea mara nyingi kuliko Gaussian inavyoruhusu.
Matokeo: HMM ya Gaussian **itaita kila spike "regime mpya"** → states za uongo,
transitions nyingi za uwongo, regime labels zisizoaminika. Tukijengea Model 2 + R6
(regime exit) juu ya labels mbovu, mfumo wote unayumba.

**Uamuzi:** HATUA 1 (HMM) itumie **Student-t emissions** AU returns zilizo-standardize
kwa **rolling volatility** kabla ya HMM. Regime modeling yenyewe **inabaki** (ona #2).

---

## 2. Model 1 — Regimes ni HALISI (uthibitisho, sio mabadiliko)

**Report inasema:** ACF(r) ≈ 0 (returns hazitabiriki — soko efficient) LAKINI
**ACF(r²) = 0.10–0.16 kwa 9/9** (vol kubwa inafuatwa na vol kubwa).

**Kwa nini ni muhimu:** Kama volatility haingecluster, dhana nzima ya "regimes" na HMM
ingekuwa bure — tungejenga Model 1 bila msingi. **Data imethibitisha regimes zipo.**
Hii ni *kijani* kwa Model 1 (mbinu sahihi), pamoja na onyo la #1 (usisahau tails).

---

## 3. Model 2 — `volume_imbalance` **siyo signal kuu** 🚩

**Report inasema:** kwa bars **250,000+ kwa pair**, predictive IC ≈ 0 (−0.001…+0.006)
na **hit-rate < 0.50 kote**. Contemporaneous +ve tu (inaakisi move ya bar ya **sasa**).

**Mtazamo wa awali (MFUMO Sehemu 1 & 3):** `volume_imbalance` = "order-flow pressure
feature" ya Model 2.

**Kwa nini tubadilishe:** tungejenga embeddings, clustering, na classifier
**zikizunguka feature isiyo na uwezo wa kutabiri.** Hatari mbili:
1. **Complexity ya bure** — kuongeza dimension isiyolipa.
2. **Overfitting** — model ingejifunza *noise* ya imbalance kama ni signal, ikionekana
   nzuri kwenye train lakini ikishindwa OOS (Phase B/OOS zingeikataa baadaye — baada ya
   kupoteza muda mwingi).

**Uamuzi:** Model 2 **isiifanye imbalance signal kuu.** Inaweza kupimwa upya kama:
(a) interaction/non-linear, (b) horizon ndefu, (c) *filter ya confirmation* (sio
predictor), (d) conditional kwa regime. **Bila ushahidi mpya — isitegemewe.**

**Faida ya kugundua sasa:** tumeokoa wiki za kazi na tumezuia "false confidence"
kwenye backtest.

---

## 4. Compliance — Toka static groups → **rolling / net-exposure**

**Report inasema:** correlation **inabadilika** — jozi 3/6 Δ≥0.20 kati ya 2016–2020 na
2021–2026; EURJPY–EURGBP **iligeuza ishara** (−0.08 → +0.18). Pia GBPUSD–EURGBP = −0.64
(kundi moja la "EUR/GBP" lakini kinyume).

**Mtazamo wa awali:** `CORRELATION_GROUPS` za static, update kila robo.

**Kwa nini tubadilishe:** kama correlation inahama (na hata kugeuza ishara), guard ya
groups za kudumu inaweza **kuruhusu exposure hatari** (pairs zilizoanza kuwa correlated)
au **kuzuia trades salama** (pairs zilizoacha kuwa correlated) — kwa kosa.

**Uamuzi (Sehemu 5):** tumia **rolling correlation** au **net-currency exposure**
(dynamic), sio makundi ya kudumu yaliyowekwa kwa mkono.

---

## Muhtasari

| # | Eneo | Mtazamo wa awali | Mtazamo mpya (data-driven) |
|---|------|------------------|----------------------------|
| 1 | Model 1 emissions | Gaussian HMM | **Student-t / vol-standardized** |
| 2 | Model 1 premise | (dhana) regimes zipo | **Imethibitishwa** (ACF r²) |
| 3 | Model 2 feature | imbalance = order-flow signal | **Si signal kuu** (IC≈0) |
| 4 | Compliance corr | static groups | **rolling / net-exposure** |

*Ushahidi wote: `reports/feature_diagnostics.md`. Code: `src/data/feature_diagnostics.py`.*
