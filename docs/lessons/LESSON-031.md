# LESSON-031@v1

```yaml
id: LESSON-031@v1
claim: "A capability with irreversible real-world consequences ships as a refuse-stub — it defaults to the safe/paper path and refuses the live path until an explicit named authority enables it."
type: GOVERNANCE
evidence:
  - "broker_adapter_report.md (E4, Q1 RED LINE): mode=live without live_authorized → AdapterError(live_
    not_authorized); paper is the default; live is a refuse-stub until the Project Director authorizes the
    artifact format — real money / network is NOT reachable by default"
  - "broker_adapter_report.md header: 'PAPER-MODE PEKEE — HAKUNA pesa halisi, HAKUNA network'; live-gating
    = Project Director decision (Master Architecture §8.2: model trading authority needs PD approval)"
counter_evidence: "none found (scope: E4 / execution boundary). Bound: a refuse-stub is a safety gate,
  not a validation — refusing live does not make the paper results correct or the edge real (LESSON-029:
  profitable-paper ≠ tradable); it only prevents unauthorized irreversible action"
validity_conditions: general (any interface to irreversible external effects — orders, payments,
  deployments, deletions; demonstrated on the broker/live-trading boundary)
when_to_use: building any bridge to irreversible external action — default to the reversible/simulated
  path, make the live path require an explicit authorization flag tied to a named human authority, and
  fail closed (raise) when that flag is absent; the two streams meet only behind that gate
when_not_to_use: the refuse-stub is not a substitute for proof (an authorized-but-unproven edge is still
  unproven — LESSON-029) nor for correctness testing; it gates AUTHORITY over irreversible action, not validity
provenance: {phase: E4, principle: P81, doctrine: (Master Architecture §8.2 — trading authority = Project Director; Permanent Truth 12)}
lifecycle: CANDIDATE
```

**Maelezo kwa mwanafunzi:** E4 ndipo streams mbili (Decision pure + MWONGOZO/FTMO/MT5) zinakutana —
lakini `mode=live` bila `live_authorized` inaraise; default ni paper, hakuna pesa halisi wala network.
Capability ya matokeo yasiyoweza kutenduliwa inasafiri kama **refuse-stub** hadi mamlaka (Project
Director) iiruhusu. Ni gate ya mamlaka juu ya kitendo kisichotenduliwa — si uthibitisho wa edge.
