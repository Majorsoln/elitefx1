# ELITEFX — MODEL REGISTRY (rasmi; source of truth ya models zote)

> Doctrine V2 §2. Kila model version = artifact + provenance + OOS proof + status. Hakuna model
> inayoenda LIVE bila gate (V2 §3) + attestation. Toleo jipya halifuti la zamani (audit trail).
> Machine-readable mirror: `data/registry/*.json` (dashboard + attestation zinasoma hapa).

## Status lifecycle: CANDIDATE → PROVEN → LIVE → RETIRED  (au → WATCH / DEAD)

## STRATEGY MODELS

| id | version | class | status | OOS proof | provenance |
|----|---------|-------|--------|-----------|------------|
| STRAT-001 | v1.0 | strategy | **PROVEN → paper** | HOLDOUT N=303 EV+1.92 p=0.021 | nr7×USDCHF H1 SL2/TP1 no-LATE; docs/STRATEGIES.md |
| STRAT-002 | v1.0 | strategy | **PROVEN → paper** | HOLDOUT N=327 EV+2.65 p=0.029 | nr7×USDJPY H1 SL1/TP1 no-LATE; docs/STRATEGIES.md |

## FILTER / MODEL LAYER

| id | version | class | status | OOS proof | provenance |
|----|---------|-------|--------|-----------|------------|
| K4-filter | v0 | filter | **NO-LIFT → K4-WATCH** | CV ΔEV_R@70% +0.016 p=0.087 (chini ya floor) | LESSON-042; reports/k4_model_report.md |

## WATCH (candidates zinazokusanya forward — si registry-live)

| id | class | status | signal | njia |
|----|-------|--------|--------|------|
| C2-WATCH | strategy | WATCH | compression×H4 pooled | forward data |
| SWING-WATCH | strategy | WATCH | nr7×D1×LOW pooled | forward data 2026-05+ |
| K4-WATCH | filter | WATCH | STRAT-001 entry-filter (streak 6→4) | forward / v1 features |

## KANUNI
- Kuongeza model: entry hapa (CANDIDATE) → gate → PROVEN → (baada ya paper/forward) LIVE.
- Kila mabadiliko = commit (immutable). Attestation script inazalisha performance kutoka artifacts.
- Toleo jipya (vX.Y) linaingia kama CANDIDATE; halichukui LIVE mpaka lizidi la sasa kwa OOS/forward.
