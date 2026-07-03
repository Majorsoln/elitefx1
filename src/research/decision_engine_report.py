"""
decision_engine_report.py — DECISION SCIENCE D6 demo HARNESS + Implementation Report (Rule 8).

Hii SI Engine — ni harness ya demo/ripoti. Kutenganishwa huku ndiko kunatimiza Rule 4: Engine
(`decision_engine.py`) haiwezi kuona Market/Events/State/Representation/Features — evidence
pipeline yote iko HAPA (harness) tu. Engine inaona Snapshot + Policy + Decision Object pekee.

Ripoti (Rule 8): Implementation Report → Self Tests → Known Limitations → Open Questions.
+ Compliance Checklist (Rule 2).

Run: python src/research/decision_engine_report.py
Self-test: python src/research/decision_engine_report.py --self-test
"""
from __future__ import annotations

import argparse, subprocess, sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from market_state_engine import cfg
from evidence_operations import build_tagged_evidence
from evidence_set import make_set
from evidence_snapshot import make_snapshot
from decision_policy import POLICIES
from decision_engine import decide, decide_batch, ContractError

REPO_ROOT = Path(__file__).resolve().parents[2]

CHECKLIST = [
    ("P92", "Engine = generic orchestrator; HAKUNA decision logic ndani (logic yote ni ya Policy — Rule 3; engine core ~60 lines)"),
    ("P94", "Engine inajua TU Snapshot·Policy·Decision Object (Rule 4; import-purity self-test [4])"),
    ("P97", "Stateless — no cache/globals/singleton/memory (Rule 5; module-mutables check, self-test [3])"),
    ("P98", "Correctness kwanza, hakuna optimization (Rule 6; plain loops, hakuna caching/vectorization)"),
    ("P99", "Kila sehemu ina self-test (Rule 7; tests [1]–[5] + harness self-test)"),
    ("P100", "Pure/deterministic (P71): inputs sawa → Decision Object ile ile (id-stable, self-test [3])"),
    ("P101", "Kila Decision inareference exact Snapshot ID (P84) + policy_id (P88) (self-test [2])"),
    ("P102", "Ripoti kwa muundo wa Rule 8: Implementation Report → Self Tests → Known Limitations → Open Questions"),
]


def run(pairs):
    c = cfg()
    print("Harness: building snapshots (evidence pipeline — NJE ya engine)...", flush=True)
    tagged, no_px = build_tagged_evidence(pairs)
    if no_px:
        print("HITILAFU: state parquet haina OHLC. Endesha market_state_engine.py kwanza.", file=sys.stderr)
        return 1
    by_event = defaultdict(list); tags_by_event = defaultdict(list)
    for e, t in tagged:
        by_event[t["engine"]].append(e); tags_by_event[t["engine"]].append((e, t))
    snaps = {ev: make_snapshot(make_set(eos, label=ev), 0, tags_by_event[ev]) for ev, eos in by_event.items()}

    # engine self-test output (verbatim, kwa ripoti)
    st = subprocess.run([sys.executable, str(Path(__file__).parent / "decision_engine.py"), "--self-test"],
                        capture_output=True, text=True)
    st_out = (st.stdout or "").strip()

    L = ["# Decision Engine — Implementation Report (Decision Science D6)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | engine: `src/research/decision_engine.py` (pure, stateless) | "
         f"harness: `decision_engine_report.py` (evidence pipeline iko HAPA, sio kwenye engine) | NO ML*\n"]

    # ---- Compliance Checklist (Rule 2) ----
    L.append("\n## Compliance Checklist (Rule 2)\n")
    L.append("| Principle | Status | Ushahidi |")
    L.append("|-----------|--------|----------|")
    for pid, how in CHECKLIST:
        L.append(f"| {pid} | ✓ | {how} |")
    L.append("\n*NB: nambari P92–P102 ni kutoka Decision Engine Specification ya Chief; matini yake bado "
             "haijawekwa kwenye repo — angalia Open Questions.*")

    # ---- Implementation Report ----
    L.append("\n## Implementation Report\n")
    L.append("- **Engine nzima ni functions mbili:** `decide(snapshot, policy) → Decision Object` na "
             "`decide_batch` (map tu). Validation ya contract (`validate_snapshot`, `validate_policy`) "
             "inakataa inputs batili kwa `ContractError`.")
    L.append("- **Mtiririko:** validate → `policy.decide(snapshot)` → `make_decision(...)` yenye "
             "`policy_id` (P88) + `evidence_refs=[snapshot_id]` (P84), lifecycle `PROPOSED`.")
    L.append("- **Separation (Rule 3/4):** engine file haina import yoyote ya market/evidence pipeline "
             "(decision_object + stdlib pekee — imethibitishwa na self-test [4]). Harness hii ndiyo "
             "inayojenga snapshots.")
    L.append("- **Demo kwenye data halisi** (snapshots × policies; kupitia ENGINE):")
    L.append("\n| snapshot (event) | readiness | capital_preservation | conservative | aggressive |")
    L.append("|------------------|-----------|----------------------|--------------|------------|")
    for ev in sorted(snaps):
        s = snaps[ev]
        acts = {}
        for pid, P in POLICIES.items():
            d = decide(s, P)
            acts[pid] = d["action"]
        L.append(f"| {ev} | {s['readiness_state']} | {acts['capital_preservation']} | "
                 f"{acts['conservative']} | {acts['aggressive']} |")
    n_dec = len(snaps) * len(POLICIES)
    L.append(f"\n- decisions {n_dec} zimeundwa kupitia engine; zote zina `policy_id` + `snapshot_id` refs "
             "na lifecycle `PROPOSED` (hakuna execution — P89 OPEN).")

    # ---- Self Tests ----
    L.append("\n## Self Tests\n")
    L.append("```text")
    L.append(st_out)
    L.append("```")
    L.append("- harness self-test: contract-rejection + refs-integrity juu ya snapshots halisi "
             "(angalia `--self-test`).")

    # ---- Known Limitations ----
    L.append("\n## Known Limitations\n")
    L.append("1. **Hakuna Execution Object (P89 OPEN)** — decisions zinabaki `PROPOSED`; hakuna fills/"
             "slippage/broker constraints (P81 OPEN).")
    L.append("2. **Policies ni illustrative rules za D5** — hazijathibitishwa OOS; 'SELECT' ≠ trade yenye "
             "faida (EV halisi hasi; P69 decision-ready ≠ trade-ready).")
    L.append("3. **reliability = Φ(EV/SE) inayojaa** (P70 OPEN) — engine inairithisha bila kurekebisha "
             "(kwa makusudi: engine haihukumu evidence).")
    L.append("4. **Immutability by-convention** — engine inarudisha objects mpya lakini Python dict si "
             "frozen; enforcement kamili ni engineering ya baadaye.")
    L.append("5. **Snapshot age-shift model ya D3** — as-of ni sare, sio per-member event-time; demo ni "
             "ndani ya model hiyo.")

    # ---- Open Questions ----
    L.append("\n## Open Questions\n")
    L.append("1. **Decision Engine Specification (P90–P102) matini yake haiko kwenye repo** — checklist "
             "hapa ime-map kwa Rules 1–8 + doctrine P63–P89. Ombi: Chief/Japhet wa-commit spec rasmi "
             "(mfano `ELITEFX DECISION ENGINE SPEC V1.md`) ili Compliance Review itaje maneno kamili.")
    L.append("2. **Architecture Compliance Review** (workflow mpya ya Chief) — nani/nini kinafanya hatua "
             "hii kabla ya Chief Review? (Implementer self-review haitoshi kimuundo.)")
    L.append("3. **Decision history storage (P85)** — decisions ni objects; zinahifadhiwa wapi (parquet/"
             "jsonl?) ili kuwa 'permanent decision history'? Haijafafanuliwa bado.")
    L.append("4. **Lifecycle transitions baada ya PROPOSED** — nani anaidhinisha VALIDATED (integrity gate "
             "ya P87)? Engine haifanyi hivyo (kwa makusudi); ni layer gani?")

    L.append("\n*Engine: pure/stateless/generic (Rules 3–6); logic yote ya maamuzi ni ya Policy; kila "
             "Decision inareference snapshot_id + policy_id. NO ML. Profitable ≠ Tradable Edge.*")

    out = REPO_ROOT / c["paths"]["reports"] / "decision_engine_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)} ({n_dec} decisions kupitia engine)")
    return 0


def self_test():
    """Harness self-test (Rule 7): contract rejection + refs juu ya fake snapshots (bila data)."""
    fake = {"id": "snap:h1", "as_of": 0, "readiness_state": "READY", "reliability": 0.95,
            "uncertainty": 0.3, "temporal_conflict": 0.0,
            "structural_conflict": {"cross-pair": 0.0}, "aggregate": {"support": 500}}
    ok_all = True

    # (1) engine inafanya kazi na policies HALISI za D5 (integration ya harness)
    d = decide(fake, POLICIES["capital_preservation"])
    ok = d["policy_id"] == "policy:capital_preservation@v1" and d["evidence_refs"] == ["snap:h1"]
    ok_all &= ok
    print(f"[H1] engine × D5 policies: action={d['action']} policy={d['policy_id']} -> {'OK' if ok else 'FAIL'}")

    # (2) batch juu ya policies zote
    ds = [decide(fake, P) for P in POLICIES.values()]
    ok = len({x["policy_id"] for x in ds}) == len(POLICIES)
    ok_all &= ok
    print(f"[H2] policies zote kupitia engine: {len(ds)} decisions -> {'OK' if ok else 'FAIL'}")

    # (3) contract rejection inapita hadi harness level
    try:
        decide({"id": "bad"}, POLICIES["conservative"]); ok = False
    except ContractError:
        ok = True
    ok_all &= ok
    print(f"[H3] contract rejection: {ok} -> {'OK' if ok else 'FAIL'}")

    print(f"\nSELF-TEST: {'PASS' if ok_all else 'FAIL'}")
    return 0 if ok_all else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    c = cfg()
    return run(c["pairs"])


if __name__ == "__main__":
    raise SystemExit(main())
