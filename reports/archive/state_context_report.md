# State Context Engine — output (Phase 1.7, CQ-012)

*2026-06-23 15:35 | per-bar: state + state_age + P(change|state,age) | online no-lookahead | chanzo: state series*

> Context = { state, age, transition_probability }. pchange imekadiriwa kutoka transitions za NYUMA tu (online). Hii ndiyo layer ya doctrine V5.1: STATE -> STATE AGE -> TRANSITION.

## Coverage (% bars zenye pchange halali) + hazard kwa age (mean pchange)

| Pair | TF | bars | cov vol/act/spr | vol haz 1-3→16+ | act haz 1-3→16+ | spr haz 1-3→16+ |
|------|----|------|-----------------|-----------------|-----------------|-----------------|
| EURUSD | H1 | 62,951 | 97/97/99% | 17→4 | 44→5 | 30→6 |
| EURUSD | H2 | 31,656 | 96/96/99% | 20→4 | 46→3 | 33→4 |
| EURUSD | H4 | 16,104 | 96/96/98% | 16→4 | 49→5 | 33→4 |
| EURUSD | D1 | 2,693 | 88/90/88% | 24→6 | 46→2 | 33→4 |
| GBPUSD | H1 | 62,953 | 97/97/99% | 18→4 | 45→7 | 31→5 |
| GBPUSD | H2 | 31,654 | 96/97/99% | 21→3 | 47→5 | 32→3 |
| GBPUSD | H4 | 16,106 | 96/96/98% | 18→4 | 49→8 | 32→4 |
| GBPUSD | D1 | 2,693 | 88/90/88% | 17→6 | 45→5 | 32→5 |
| USDJPY | H1 | 62,968 | 97/97/99% | 16→4 | 45→6 | 29→4 |
| USDJPY | H2 | 31,659 | 96/97/99% | 18→4 | 48→6 | 33→4 |
| USDJPY | H4 | 16,106 | 96/96/98% | 18→4 | 48→8 | 32→4 |
| USDJPY | D1 | 2,693 | 88/89/89% | 16→4 | 44→11 | 35→5 |
| EURJPY | H1 | 62,966 | 97/97/99% | 16→4 | 44→9 | 31→5 |
| EURJPY | H2 | 31,659 | 96/97/99% | 19→4 | 47→5 | 32→4 |
| EURJPY | H4 | 16,106 | 96/96/98% | 16→4 | 49→9 | 31→4 |
| EURJPY | D1 | 2,693 | 88/90/89% | 24→6 | 44→10 | 33→6 |
| USDCAD | H1 | 62,952 | 97/97/99% | 18→5 | 45→8 | 31→6 |
| USDCAD | H2 | 31,653 | 96/97/99% | 20→5 | 47→5 | 31→4 |
| USDCAD | H4 | 16,103 | 96/96/98% | 16→5 | 48→8 | 31→3 |
| USDCAD | D1 | 2,693 | 88/90/88% | 24→6 | 44→3 | 31→5 |
| USDCHF | H1 | 62,955 | 97/97/99% | 18→4 | 46→9 | 32→7 |
| USDCHF | H2 | 31,658 | 96/97/99% | 20→4 | 47→5 | 32→5 |
| USDCHF | H4 | 16,106 | 96/96/98% | 18→4 | 50→7 | 32→5 |
| USDCHF | D1 | 2,693 | 88/90/89% | 22→5 | 46→12 | 37→6 |
| AUDUSD | H1 | 62,964 | 97/97/99% | 18→5 | 44→6 | 32→6 |
| AUDUSD | H2 | 31,659 | 96/97/99% | 19→5 | 47→4 | 32→4 |
| AUDUSD | H4 | 16,106 | 96/96/98% | 20→5 | 49→7 | 31→3 |
| AUDUSD | D1 | 2,693 | 88/90/88% | 27→4 | 48→4 | 34→4 |
| NZDUSD | H1 | 62,964 | 97/97/99% | 18→5 | 45→10 | 32→6 |
| NZDUSD | H2 | 31,659 | 96/97/99% | 18→4 | 46→5 | 33→4 |
| NZDUSD | H4 | 16,106 | 96/96/98% | 20→4 | 48→8 | 32→3 |
| NZDUSD | D1 | 2,693 | 88/90/88% | 22→5 | 45→8 | 32→4 |
| EURGBP | H1 | 62,961 | 97/97/99% | 17→4 | 45→7 | 30→5 |
| EURGBP | H2 | 31,658 | 96/97/99% | 20→4 | 46→4 | 32→4 |
| EURGBP | H4 | 16,106 | 96/96/98% | 17→3 | 48→7 | 32→3 |
| EURGBP | D1 | 2,693 | 88/89/88% | 15→6 | 46→10 | 32→5 |

---
*State Context Engine = component ya msingi (CQ-012). Output parquet ina state+age+pchange kwa kila dimension, tayari kwa Event Layer & Triple Barrier. pchange ni ONLINE no-lookahead. 'haz 1-3→16+' inaonyesha P(change) inavyobadilika na umri (linganisha na state_age_report). Inayofuata (Phase 1.8): state_transition_model (P(next|state) vs P(next|state,age), LogLoss/Brier). Metric = EV (CQ-008).*