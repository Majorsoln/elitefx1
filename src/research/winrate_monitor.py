"""
winrate_monitor.py — WAVE-1 R6: pre-registered win-rate control chart (SCIENTIST-D design; Chief 2026-07-12).

Hatari #1 ya live ni win% decay (structures za TP<SL zina margin ndogo juu ya breakeven). Hii module
inageuza "monitoring ya lazima" kutoka nia kuwa MECHANISM — thresholds zime-pre-register SASA (kabla
forward data haijaongezeka) ili kuondoa majaribu ya ku-re-litigate baada ya drawdowns.

MECHANISM (design verbatim):
  * w_be = breakeven win% kwa costs za sasa (kutoka review: STRAT-001 68.3%, STRAT-002 52.3%).
  * Beta prior kutoka HOLDOUT (a = w_hold*N_hold, b = (1-w_hold)*N_hold) -> posterior mean baada ya
    kila trade ya forward.
  * ALARM (statistical): posterior mean win% < w_be + 1*SE ambapo SE = sqrt(w_be*(1-w_be)/n_roll).
  * THRESHOLDS za utendaji @60-trade rolling (pre-registered):
      STRAT-001: REVIEW < 70.0% · HALT < 66.0%   (zilizotolewa na review/Chief)
      STRAT-002: REVIEW < 54.0% · HALT < 50.0%   (framework ILEILE: review = w_be+1.7pp,
                 halt = w_be-2.3pp — offsets zilezile za STRAT-001 juu ya w_be yake; pre-registered
                 hapa KABLA ya forward data — Chief ata-approve kwenye review ya report hii)
STATUS: OK -> REVIEW (punguza size/kagua) -> HALT (simamisha; uamuzi wa binadamu).

Inasoma results kama sequence ya win/loss (1/0) au kutoka paper log (settlements: pnl>0 = win).
Self-test bila data: python src/research/winrate_monitor.py --self-test
"""
from __future__ import annotations

import argparse
import math
import sys

# REGISTRY (pre-registered SASA; provenance: data_science_review §B-R6 + S3/S3b holdout artifacts)
MONITOR = {
    "STRAT-001": dict(w_be=0.683, w_hold=0.739, n_hold=303, review_lt=0.700, halt_lt=0.660, n_roll=60),
    "STRAT-002": dict(w_be=0.523, w_hold=0.578, n_hold=327, review_lt=0.540, halt_lt=0.500, n_roll=60),
}


def alarm_line(w_be, n_eff):
    """Statistical alarm line: w_be + 1*SE ambapo SE = SE ya POSTERIOR (n_eff = prior N + forward n —
    inapungua data zinavyoongezeka). NB (interpretation ya kihandisi, imeandikwa kwa referee):
    SE ya rolling-60 flat (6.4pp) ingekuwa JUU ya margin ya STRAT-002 (w_hold−w_be = 5.5pp) —
    alarm isingeweza kufikiwa kimuundo hata kwa holdout performance; SE ya posterior inarekebisha:
    kwa data nyingi, kuwa chini ya w_be+ε ni ushahidi halisi wa decay."""
    return w_be + math.sqrt(w_be * (1.0 - w_be) / max(1, n_eff))


def posterior_mean(results, w_hold, n_hold):
    """Beta-Binomial posterior mean ya win% baada ya forward results (1=win, 0=loss).
    Prior kutoka holdout: Beta(a=w_hold*n_hold, b=(1-w_hold)*n_hold)."""
    a = w_hold * n_hold + sum(1 for r in results if r)
    b = (1.0 - w_hold) * n_hold + sum(1 for r in results if not r)
    return a / (a + b)


def rolling_winrate(results, n_roll=60):
    """Win% ya trades za mwisho n_roll (None kama chini ya nusu ya window — underpowered)."""
    if len(results) < max(10, n_roll // 2):
        return None
    tail = results[-n_roll:]
    return sum(1 for r in tail if r) / len(tail)


def check(strat, results):
    """Tathmini status ya strategy kwa forward results (ordered, 1=win/0=loss).
    Rudisha dict: status (OK/REVIEW/HALT/WARMUP) + vipimo vyote (auditable)."""
    cfg = MONITOR[strat]
    post = posterior_mean(results, cfg["w_hold"], cfg["n_hold"])
    line = alarm_line(cfg["w_be"], cfg["n_hold"] + len(results))
    roll = rolling_winrate(results, cfg["n_roll"])
    stat_alarm = post < line
    if roll is None:
        status = "WARMUP"                      # data chache — posterior tu ndiyo inafuatiliwa
        if stat_alarm:
            status = "REVIEW"                  # posterior chini ya alarm line hata kwenye warmup
    elif roll < cfg["halt_lt"]:
        status = "HALT"
    elif roll < cfg["review_lt"] or stat_alarm:
        status = "REVIEW"
    else:
        status = "OK"
    return dict(strategy=strat, status=status, n_forward=len(results),
                rolling_winrate=None if roll is None else round(roll, 4),
                posterior_mean=round(post, 4), alarm_line=round(line, 4),
                statistical_alarm=bool(stat_alarm),
                thresholds=dict(review_lt=cfg["review_lt"], halt_lt=cfg["halt_lt"], n_roll=cfg["n_roll"]),
                w_be=cfg["w_be"], prior=f"Beta kutoka holdout (w={cfg['w_hold']}, N={cfg['n_hold']})")


def results_from_paper_log(path, pair):
    """Forward results kutoka paper log (E3 jsonl): settlements za pair -> 1/0 kwa mpangilio."""
    import decision_repository as repo
    recs = repo.load(path)
    execs = {r["obj"]["id"]: r["obj"] for r in recs if r["kind"] == "execution"
             and r["obj"].get("pair") == pair}
    out = []
    for r in recs:
        if r["kind"] == "settlement" and r["obj"].get("parent_execution_id") in execs:
            out.append(1 if r["obj"].get("pnl", 0) > 0 else 0)
    return out


# ---------- self-test (bila data) ----------
def self_test():
    ok = True

    # [1] registry + framework consistency: STRAT-002 offsets = zile za STRAT-001 juu ya w_be
    c1, c2 = MONITOR["STRAT-001"], MONITOR["STRAT-002"]
    off_rev1 = round(c1["review_lt"] - c1["w_be"], 3)   # +0.017
    off_halt1 = round(c1["halt_lt"] - c1["w_be"], 3)    # -0.023
    t1 = (round(c2["review_lt"] - c2["w_be"], 3) == off_rev1
          and round(c2["halt_lt"] - c2["w_be"], 3) == off_halt1)
    print(f"  [1] framework ileile: offsets rev={off_rev1:+.3f} halt={off_halt1:+.3f} (S1==S2) -> {t1}")
    ok = ok and t1

    # [2] healthy stream (win% ~ holdout, interleaved — hakuna clustering ya bandia) -> OK
    healthy = [1, 1, 1, 0] * 50                          # 75% win kila mahali, 200 trades
    r = check("STRAT-001", healthy)
    t2 = r["status"] == "OK" and not r["statistical_alarm"] and r["rolling_winrate"] >= 0.70
    print(f"  [2] healthy: status={r['status']} roll={r['rolling_winrate']} post={r['posterior_mean']} -> {t2}")
    ok = ok and t2

    # [3] decay -> REVIEW kisha HALT (rolling): 60 za mwisho zina win 65% (<66 halt) baada ya decay
    decayed = [1] * 100 + ([1] * 39 + [0] * 21)          # tail-60: 39/60 = 65%
    r3 = check("STRAT-001", decayed)
    mild = [1] * 100 + ([1] * 41 + [0] * 19)             # tail-60: 41/60 = 68.3% (<70 review, >66)
    r3b = check("STRAT-001", mild)
    t3 = r3["status"] == "HALT" and r3b["status"] == "REVIEW"
    print(f"  [3] decay: 65%->{r3['status']} 68.3%->{r3b['status']} -> {t3}")
    ok = ok and t3

    # [4] statistical alarm: posterior inashuka chini ya w_be+1SE kwa losing streak ndefu (prior nzito)
    streak = [1] * 30 + [0] * 90                          # forward mbaya sana
    r4 = check("STRAT-001", streak)
    t4 = r4["statistical_alarm"] and r4["status"] in ("REVIEW", "HALT")
    print(f"  [4] statistical alarm: post={r4['posterior_mean']} < line={r4['alarm_line']} status={r4['status']} -> {t4}")
    ok = ok and t4

    # [5] warmup: trades chache -> WARMUP (hakuna rolling verdict); alarm ya posterior bado inafanya kazi
    r5 = check("STRAT-002", [1, 0, 1, 1, 0])
    t5 = r5["status"] == "WARMUP" and r5["rolling_winrate"] is None
    print(f"  [5] warmup (n=5): status={r5['status']} -> {t5}")
    ok = ok and t5

    # [6] paper-log adapter (temp log): settlements -> 1/0 sequence
    import tempfile, os
    import decision_repository as repo
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, "log.jsonl")
        v = {"schema_version": "x@v1", "doctrine_version": "V12"}
        repo.append(p, "execution", {"id": "e1", "as_of": 1, "status": "FILLED", "pair": "USDCHF"}, v)
        repo.append(p, "execution", {"id": "e2", "as_of": 2, "status": "FILLED", "pair": "USDCHF"}, v)
        repo.append(p, "execution", {"id": "e3", "as_of": 3, "status": "FILLED", "pair": "USDJPY"}, v)
        repo.append(p, "settlement", {"id": "s1", "as_of": 4, "parent_execution_id": "e1", "pnl": 12.0}, v)
        repo.append(p, "settlement", {"id": "s2", "as_of": 5, "parent_execution_id": "e2", "pnl": -8.0}, v)
        repo.append(p, "settlement", {"id": "s3", "as_of": 6, "parent_execution_id": "e3", "pnl": 5.0}, v)
        res = results_from_paper_log(p, "USDCHF")
        t6 = res == [1, 0]                                # USDCHF pekee, ordered
    print(f"  [6] paper-log adapter: USDCHF results={res} -> {t6}")
    ok = ok and t6

    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Win-rate control chart (R6) — thresholds pre-registered")
    ap.add_argument("--strategy", choices=list(MONITOR), default=None)
    ap.add_argument("--paper-log", dest="log", default=None, help="path ya paper_log.jsonl")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.strategy and a.log:
        pair = "USDCHF" if a.strategy == "STRAT-001" else "USDJPY"
        res = results_from_paper_log(a.log, pair)
        r = check(a.strategy, res)
        for k, v in r.items():
            print(f"  {k}: {v}")
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
