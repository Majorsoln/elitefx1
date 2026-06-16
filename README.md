# EliteFX

Mfumo wa kufanya biashara ya forex unaolenga kupita changamoto ya prop firm
(**FTMO**) kwa pairs 9. Maelezo kamili ya mfumo: **[MFUMO.md](MFUMO.md)**.

## Muundo wa mradi

```
config/        ftmo_config.yaml, data_config.yaml
src/data/      pipeline ya SEHEMU 1 (ingest, resample, quality, sessions)
data/          raw / interim / processed  (NJE ya git — iko kwenye PC ya Japhet)
notebooks/     EDA
reports/       ripoti za ubora wa data
tests/         test_no_lookahead.py n.k.
```

## SEHEMU 1 — Data (kazi inayoendelea)

Lengo: kutoka Dukascopy tick data → candles safi (D1…15m) **bila lookahead**,
tayari kwa Model 1 & 2.

> **Data (26GB) iko kwenye PC ya Japhet, sio kwenye repo.** Code huendeshwa
> locally pale data ilipo; git inahifadhi code, config, na ripoti tu.

Data ghafi iko Hive-partitioned:
`data/raw/ticks/symbol=*/year=*/.../day=*`, timezone **CE(S)T → UTC** kwenye ingest.
