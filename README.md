# EliteFX

Mfumo wa kufanya biashara ya forex unaolenga kupita changamoto ya prop firm
(**FTMO**) kwa pairs 9. Maelezo kamili ya mfumo: **[MFUMO.md](MFUMO.md)**.
Jinsi ya kupata/kutumia/kutafsiri data: **[DATA_GUIDE.md](DATA_GUIDE.md)**.

## Muundo wa mradi

```
config/        data_config.yaml, ftmo_config.yaml   (Japhet anaweka values)
src/data/      inspect_raw.py, build_candles.py, quality.py, eda.py, dataset.py
data/          raw / interim / processed   (NJE ya git — iko kwenye PC ya Japhet, ~26GB)
reports/       data_quality_report.md, eda_report.md   (rekodi; push kwa -f)
tests/         test_no_lookahead.py
MFUMO.md       muundo wa mfumo wote (Sehemu 1–9)
DATA_GUIDE.md  how to get / use / interpret data kwa kila eneo
```

> **Data (~26GB) iko kwenye PC ya Japhet, sio kwenye repo.** Code huendeshwa
> locally pale data ilipo; git inahifadhi code, config, na ripoti (muhtasari) tu.
> Data ghafi: Hive-partitioned `data/raw/ticks/symbol=*/year=*/.../day=*`,
> timezone **CE(S)T → UTC** kwenye build.

---

## SEHEMU 1 — Runbook (kusafisha → ripoti)

Endesha kutoka **root ya repo** (`C:\elitefx1`), ndani ya venv. Mfuatano:

**0. Setup (mara moja tu)**
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**1. Safisha outputs za zamani** *(hiari — kwa ujenzi mpya kabisa)*
```
rmdir /s /q data\processed\candles
del /q reports\*.md
```
*(Hii HAIGUSI `data\raw` — ticks ghafi hazifutwi kamwe.)*

**2. Chunguza schema ya raw** *(thibitisha umbo kabla ya kujenga)*
```
python src\data\inspect_raw.py
```

**3. Jenga candles kutoka ticks** *(kusafisha bei + resample TF zote 8)*
```
python src\data\build_candles.py
```
*Kasi/kumbukumbu (data kubwa):*
```
python src\data\build_candles.py --symbol EURUSD --memory-limit 8GB --temp-dir D:\tmp
python src\data\build_candles.py --force-1m          ⟵ jenga upya 1m
```

**4. Ukaguzi wa ubora** → `reports\data_quality_report.md`
```
python src\data\quality.py
```

**5. EDA** → `reports\eda_report.md`
```
python src\data\eda.py
```

**6. Test ya no-lookahead** *(lazima ipite)*
```
python tests\test_no_lookahead.py
```

**7. Push ripoti** *(zime-ignored — lazima `-f`)*
```
git add -f reports\data_quality_report.md reports\eda_report.md
git commit -m "SEHEMU 1: ripoti za quality + eda"
git push
```

---

Lengo la SEHEMU 1: kutoka Dukascopy tick data → candles safi (1m…D1) **bila
lookahead**, zimepimwa (quality + EDA), tayari kwa Model 1 & 2.
