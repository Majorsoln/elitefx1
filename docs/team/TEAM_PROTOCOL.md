# TEAM PROTOCOL — ELITEFX Operating System (Master Architecture V1 §6 extension)

*Owner: Chief Quant (Unified) | Directive ya Project Director 2026-07-04 | Status: ACTIVE*

## 1 — Timu (nani anafanya nini)

```text
PROJECT DIRECTOR & OPERATOR (Japhet — binadamu pekee)
   · Pekee mwenye local PC + data (~26GB) — kila kitu kinachohitaji kompyuta halisi ni chake
   · Anaendesha: prompts (kufungua session za agents), scripts (self-tests, runs), commits/pushes
   · Final decision ya project/production
CHIEF QUANT UNIFIED (AI — session hii/warithi wake)
   · Direction + doctrine + architecture + knowledge
   · ANAANDIKA PROMPTS za kila agent (hakuna agent anayeanza bila prompt ya Chief)
   · ANAMPA OPERATOR muongozo mfupi KILA WAKATI: tuko hatua gani · zinabaki zipi · kazi yake ni nini
AGENTS (AI sessions — Operator anafungua kwa prompts za Chief):
   · IMPLEMENTER-A  — Track A: E1–E4 specs/code/self-tests/reports
   · RESEARCHER-K   — Track B: lessons/graph/evals/datasets
   · AUDITOR        — compliance (4-point + P107 dependency graph + drift watch)
```

## 2 — Mfumo wa kumbukumbu (REPO = UBONGO WA PAMOJA)

Kila member ana **memory file yake** `docs/team/memory/MEMORY_<NAME>.md` yenye: identity ·
standing orders · current task · last completed · next steps · open questions. **Kumbukumbu za
mradi mzima**: `PROGRAM_BOARD` (rekodi rasmi) · `PROJECT_MEMORY` (brain) · `CHIEF_STATUS` (live)
· `LESSON_INDEX` (knowledge).

## 3 — Session Ritual (LAZIMA kwa kila agent, kila session)

```text
KUANZA (bootstrap):  1. Soma prompt yako (docs/team/PROMPTS.md — sehemu yako)
                     2. Soma MEMORY yako + CHIEF_STATUS (Current Phase) + board "Last updated"
                     3. Thibitisha kazi na mipaka yako kabla ya kugusa chochote
KUFANYA KAZI:        · Kazi ULIYOPEWA tu; ukikwama kwenye doctrine — simama, uliza Chief (kupitia
                       Operator); hakuna approval — mapendekezo tu
KUFUNGA (close):     1. Update MEMORY yako (last completed / next / open questions)
                     2. Ripoti fupi kwa Operator: nimefanya X · kinachofuata Y · ninahitaji Z
                     3. Commit (kama una repo access) au mpe Operator diff
```

## 4 — Wajibu wa Chief kwa Operator (status duty — LAZIMA kila jibu)

Kila jibu la Chief kwa Operator linaishia na block:

```text
=== STATUS ===
TUKO HAPA:    <hatua ya sasa kwa sentensi 1-2>
IMEKAMILIKA:  <za karibuni>
ZINABAKI:     <3-5 zinazofuata kwa order>
KAZI YAKO:    <Operator afanye nini sasa hivi — amri wazi, copy-paste ikiwezekana>
```

## 5 — Mtiririko wa kazi (nani anaanza nini)

```text
Chief anaamua kazi → anaandika/anasasisha prompt → Operator anafungua agent session na prompt
→ agent anafanya + anafunga (ritual §3) → Operator analeta matokeo/anapush → Chief anareview
→ Chief anasasisha CHIEF_STATUS + memory → STATUS block kwa Operator → kazi inayofuata
```

Data runs (zinahitaji PC): Chief anaandika **runbook** (amri hatua-kwa-hatua) → Operator anaendesha
→ anabandika output → Chief anahitimisha. Rekodi ya kila run: `MEMORY_OPERATOR.md`.
