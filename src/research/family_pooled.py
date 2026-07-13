"""
family_pooled.py — FAMILY-POOLED HOLDOUT TEST (C2-WATCH; build ya design ya SCIENTIST-D, APPROVED).

Design-of-record: reports/family_pooled_design.md (§1-§8, verbatim). Jukumu langu (§8.1):
JENGA runner + acceptance tests AT1-AT8 kwa REUSE TU — **ZERO changes** kwa episodes / _mask_context /
pvalue_boot; `load_window` imeongezwa `ts` array PEKEE (additive, non-breaking — §3.1/§8.1).

MSINGI (design §0): jaribio MOJA la pre-registered, single-hypothesis (m=1) juu ya dirisha bikira la
H4 2025-01→2026-04:
  H1: familia ya compression-H4 (C2-WATCH), ikitradiwa kama stream MOJA iliyo-risk-normalized kupitia
      cells 4 mechanical, ina EV chanya baada ya costs.
  Criterion: pvalue_boot (engine RASMI, B=50,000) juu ya pooled R-unit series < 0.05 NA pooled EV_R > 0.

Vipande (design):
  §1 Universe FIXED: cells 4 (rep moja kwa group iliyobaki ya C2-WATCH) — hakuna selection freedom.
  §2 Normalization: R-units (pnl_R = pnl_pips / (sl_atr × atr[signal_bar])) — pip-scale invariant,
     deployment-consistent (fixed-fractional risk). Sensitivity: ATR-units (pnl_pips/atr[i]).
  §3 Pooling: union ya streams 4 sorted na ts_entry (tie: pair alphabetical); pvalue_boot(B=50k,
     mean_block=3), seed = _seed kutoka registration string.
  §4 MDE screen (shrink 0.35 conservative tip) — hesabu EXACT wakati wa registration (AT8 dry-run).
  §5 Acceptance tests AT1-AT8 (ZOTE lazima zipite kabla ya freeze; referee = SCIENTIST-D).
  §6 Verdict semantics pre-registered · §7 caveats · §8 sequencing (B-prime).

RED LINE (design §5-AT5): split=holdout inarefuse bila Chief token — inatumia guard ILIYOPO ya
`load_window` (hakuna data-path mpya). USIENDESHE holdout — Chief atatoa token baada ya referee + screen.

Endesha (PC ya data):  python family_pooled.py --split validation           (AT8 dry-run → screen)
                       python family_pooled.py --split holdout --holdout-final <token>   (Chief pekee)
Self-test (bila data): python family_pooled.py --self-test
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

from event_library_v2 import EVENTS_V2, _synthetic
from event_quality_report import episodes, SL_ATR
from strategy_lab import _mask_context, load_window, pvalue_boot, pvalue_gt0, _seed_from_key

REPO_ROOT = Path(__file__).resolve().parents[2]

# ---------- §1 FIXED UNIVERSE (hakuna selection freedom — rep moja kwa group ya C2-WATCH) ----------
# (event × pair · SL/TP · filter); session_filter="no-LATE", vol_filter=None kwa zote (design table §1).
REP_CELLS = (
    dict(event="nr4_inside", pair="GBPJPY", sl_atr=1.5, tp_atr=1.5, session_filter="no-LATE", vol_filter=None),  # REP-1
    dict(event="nr7_break",  pair="EURGBP", sl_atr=1.5, tp_atr=1.0, session_filter="no-LATE", vol_filter=None),  # REP-2
    dict(event="nr7_break",  pair="EURJPY", sl_atr=1.0, tp_atr=3.0, session_filter="no-LATE", vol_filter=None),  # REP-3
    dict(event="nr7_break",  pair="AUDUSD", sl_atr=1.5, tp_atr=3.0, session_filter="no-LATE", vol_filter=None),  # REP-4
)
FAMILY_TF = "H4"
REG_PREFIX = "FAMILY-POOLED-C2WATCH-H4"       # design §3.3 registration string prefix
B_REG = 50_000                                # design §3.3 (referee condition 1; p floor 2e-05)
MEAN_BLOCK = 3                                # engine RASMI (wave1_referee_report.md)
ALPHA = 0.05
SHRINK_TIP = 0.35                             # conservative shrink (design §4)
N_DAYS_WINDOW = 347                           # 2025-01→2026-04 (design §4 N_exp)

# outputs (design §5-AT6 — no-clobber: candidates*.jsonl HAZIGUSWI)
OUT_JSONL = "family_pooled_c2watch.jsonl"
OUT_REPORT = "family_pooled_report.md"

HOLDOUT_TOKEN = "CHIEF-HOLDOUT-S3"            # mirror ya strategy_lab (guard inatumika kupitia load_window)


# ---------- §3.3 seed kutoka registration string (hashing ILEILE kama _seed_from_key) ----------
def registration_string(cells=REP_CELLS):
    """design §3.3: 'FAMILY-POOLED-C2WATCH-H4|' + '|'.join(cell keys). cell key = umbo la
    _seed_from_key (event|pair|sl|tp|sf|vf) — hakuna selection freedom inayobaki kwenye string."""
    keys = ["|".join(str(c.get(k)) for k in
                     ("event", "pair", "sl_atr", "tp_atr", "session_filter", "vol_filter"))
            for c in cells]
    return REG_PREFIX + "|" + "|".join(keys)


def _seed_from_registration(reg):
    """Hashing ILEILE ya _seed_from_key (sha1 → 12 hex → int) juu ya registration string nzima —
    seed deterministic, reproducible bit-kwa-bit (design §3.3 'existing _seed_from_key hashing')."""
    return int(hashlib.sha1(reg.encode()).hexdigest()[:12], 16)


# ---------- §2 R-normalization + §3.1 per-cell stream ----------
def _r_normalize(trades, atr, sl_atr, ts, pair):
    """design §2: kwa kila trade ya episodes (entry_bar, exit_bar, dir, pnl_pips, sess, vs):
      signal_bar i = entry_bar - 1;  R_trade = sl_atr × atr[i]  (SL distance kwa pips — signal-bar
      ATR, exactly quantity episodes() already uses for SL);  pnl_R = pnl_pips / R_trade.
    Inarudisha list ya dict per-trade: ts_entry, pair, pnl_R, pnl_atr (sensitivity), entry_bar,
    exit_bar, dir, r_trade, pnl_pips, is_timeout. atr/pnl viko kwenye pips → pnl_R dimensionless
    (pip-scale invariant, design §2). R_trade>0 imehakikishwa (episodes inatoa trade tu kama a>0)."""
    rows = []
    for (entry_bar, exit_bar, d, pnl_pips, sess, vs) in trades:
        i = entry_bar - 1                                  # signal bar (episodes: a = atr[i])
        r_trade = sl_atr * atr[i]
        if not (r_trade > 0):                              # ulinzi (haipaswi kutokea — episodes a>0)
            continue
        rows.append(dict(ts_entry=ts[entry_bar], pair=pair,
                         pnl_R=pnl_pips / r_trade,
                         pnl_atr=pnl_pips / atr[i],         # §2 sensitivity (ATR-units)
                         entry_bar=int(entry_bar), exit_bar=int(exit_bar), dir=int(d),
                         r_trade=float(r_trade), pnl_pips=float(pnl_pips),
                         is_timeout=int(exit_bar == min(i + 1 + 24, len(atr) - 1))))
    return rows


def cell_stream(cell, data):
    """design §3.1: endesha episodes() kwa rep cell moja (fill rules HAZIGUSWI) → per-trade R rows.
    Njia SAWASAWA na strategy_lab.evaluate (event fn default params → _mask_context KWENYE signals →
    episodes), kisha R-normalization ya §2. `data` = load_window(...) (+ts)."""
    spec = EVENTS_V2[cell["event"]]
    out = spec["fn"](data["o"], data["h"], data["l"], data["c"], data.get("tc"), data.get("hour"))
    out = _mask_context(out, spec["entry"], data["hour"], data.get("vol"),
                        cell["session_filter"], cell["vol_filter"])
    trs = episodes(out, spec["entry"], data["o"], data["h"], data["l"], data["c"],
                   data["atr"], data["spr"], data["hour"], data.get("vol"),
                   sl_atr=cell["sl_atr"], tp_atr=cell["tp_atr"])
    return _r_normalize(trs, data["atr"], cell["sl_atr"], data["ts"], cell["pair"])


# ---------- §3.2 pooling ----------
def pool_streams(streams):
    """design §3.2: pool = union ya streams sorted na entry timestamp; tie (ts sawa) → pair
    alphabetical. design §5-AT7 dedup: (pair, entry_bar) ni UNIQUE (cells = pairs 4 tofauti →
    hakuna trade duplicated by construction; imehakikishwa hapa). Inarudisha pooled rows."""
    pooled = [r for s in streams for r in s]
    pooled.sort(key=lambda r: (r["ts_entry"], r["pair"]))
    seen = set()
    for r in pooled:
        key = (r["pair"], r["entry_bar"])
        assert key not in seen, f"dedup FAIL (AT7): trade duplicated {key}"
        seen.add(key)
    return pooled


def _boot_ci(vals, level=0.90, B=2000, seed=0):
    """90% bootstrap CI ya mean (design §6: verdict inarekodiwa na CI, si binary tu). i.i.d.
    resample ya mean (percentile) — CI ya descriptive, si test statistic (hiyo ni pvalue_boot)."""
    x = np.asarray(vals, float); n = len(x)
    if n < 2:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    means = x[rng.integers(0, n, size=(B, n))].mean(axis=1)
    lo, hi = (1 - level) / 2, 1 - (1 - level) / 2
    return (float(np.quantile(means, lo)), float(np.quantile(means, hi)))


# ---------- §4 MDE / power screen ----------
def mde_screen(ev_r, sd_r, n, shrink=SHRINK_TIP, alpha=ALPHA):
    """design §4: MDE_pooled = z_{1-α} × sd_R/√n (one-sided). Screen PASS kama forecast ya shrunken
    (ev_r × shrink) ≥ MDE. Inarudisha dict (mde, forecast, pass, margin). Hesabu EXACT wakati wa
    registration kutoka series halisi ya R (AT8 dry-run) — table ya design ni two-point approx."""
    from math import sqrt
    z = 1.6448536269514722                                 # Φ^{-1}(0.95)
    mde = z * sd_r / sqrt(max(n, 1))
    forecast = ev_r * shrink
    return dict(mde=mde, forecast=forecast, passes=bool(forecast >= mde and ev_r > 0),
                margin=(forecast / mde if mde > 0 else float("inf")))


# ---------- runner (design §3-§4-§6) ----------
def run_family(split, holdout_token=None, out_root=REPO_ROOT, cells=REP_CELLS, tf=FAMILY_TF,
               B=B_REG, write=True):
    """Pipeline kamili: load_window kwa pairs 4 (guard ya holdout inatumika — AT5) → cell_stream kila
    rep → pool → pvalue_boot (seed=registration) → screen + verdict + CI → outputs (AT6 no-clobber).
    Inarudisha result dict. split='holdout' bila token sahihi → PermissionError (kupitia load_window)."""
    reg = registration_string(cells)
    seed = _seed_from_registration(reg)
    streams, missing = [], []
    for c in cells:
        data = load_window(c["pair"], tf, split, holdout_token)   # AT5 guard iko HAPA (design §5-AT5)
        if data is None:
            missing.append(c["pair"]); continue
        streams.append(cell_stream(c, data))
    pooled = pool_streams(streams)
    pooled_R = np.array([r["pnl_R"] for r in pooled], float)
    pooled_atr = np.array([r["pnl_atr"] for r in pooled], float)
    n = len(pooled_R)
    result = dict(split=split, reg_string=reg, seed=seed, n=n, missing=missing,
                  cells=[dict(c) for c in cells])
    if n >= 2:
        ev_r = float(pooled_R.mean()); sd_r = float(pooled_R.std(ddof=1))
        p_boot = pvalue_boot(pooled_R, B=B, mean_block=MEAN_BLOCK, seed=seed)
        p_z = pvalue_gt0(pooled_R)                          # sensitivity column (design §2/§5)
        p_atr = pvalue_boot(pooled_atr, B=B, mean_block=MEAN_BLOCK, seed=seed)  # ATR-unit sensitivity
        ci = _boot_ci(pooled_R, 0.90, seed=seed)
        rho1 = float(np.corrcoef(pooled_R[:-1], pooled_R[1:])[0, 1]) if n > 2 else float("nan")
        screen = mde_screen(ev_r, sd_r, n)
        verdict = "PASS" if (p_boot < ALPHA and ev_r > 0) else "FAIL"
        shares = {}
        for r in pooled:
            shares[r["pair"]] = shares.get(r["pair"], 0) + 1
        result.update(ev_r=ev_r, sd_r=sd_r, p_boot=p_boot, p_z=p_z, p_atr=p_atr,
                      ci90=ci, rho1=rho1, screen=screen, verdict=verdict,
                      shares={k: v / n for k, v in shares.items()},
                      timeout_share=float(np.mean([r["is_timeout"] for r in pooled])))
    else:
        result.update(ev_r=None, verdict="INSUFFICIENT_N")
    if write:
        _write_outputs(result, pooled, out_root)
    return result


def _write_outputs(result, pooled, out_root):
    """design §5-AT6 no-clobber: andika data/strategies/family_pooled_c2watch.jsonl + reports/
    family_pooled_report.md PEKEE. candidates*.jsonl HAZIGUSWI."""
    out_root = Path(out_root)
    strat_dir = out_root / "data" / "strategies"; strat_dir.mkdir(parents=True, exist_ok=True)
    jl = strat_dir / OUT_JSONL
    with open(jl, "w", encoding="utf-8") as f:
        f.write(json.dumps({k: v for k, v in result.items() if k not in ("cells",)},
                           sort_keys=True, default=str) + "\n")
        for r in pooled:
            rec = dict(r); rec["ts_entry"] = str(rec["ts_entry"])
            f.write(json.dumps(rec, sort_keys=True) + "\n")

    v = result.get("verdict", "—")
    L = [f"# Family-Pooled Holdout Test — C2-WATCH ({result['split'].upper()})\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | design: reports/family_pooled_design.md | TF={FAMILY_TF} | "
         f"m=1 single-hypothesis | reuse-only (episodes/_mask_context/pvalue_boot ZERO changes; "
         f"load_window +ts additive)*\n",
         "> **H1 (pre-registered):** compression-H4 family (cells 4, risk-normalized stream moja) ina "
         "EV chanya net-of-costs. **Criterion:** pvalue_boot(B=50k) < 0.05 NA pooled EV_R > 0 (design §0).\n"]
    L.append("\n## Registration (design §3.3)\n")
    L.append(f"- reg string: `{result['reg_string']}`")
    L.append(f"- seed (deterministic): `{result['seed']}` · B={B_REG} · mean_block={MEAN_BLOCK} · α={ALPHA}")
    L.append(f"- pairs missing (no window): {result['missing'] or 'none'}")
    L.append("\n## Fixed universe (§1)\n")
    L.append("| rep | event | pair | SL | TP | filter |")
    L.append("|-----|-------|------|----|----|--------|")
    for k, c in enumerate(result["cells"], 1):
        L.append(f"| REP-{k} | {c['event']} | {c['pair']} | {c['sl_atr']} | {c['tp_atr']} | "
                 f"{c['session_filter']} |")
    if result.get("ev_r") is not None:
        s = result["screen"]
        L.append("\n## Result (R-units, design §2-§4-§6)\n")
        L.append(f"- pooled N = **{result['n']}** · EV_R = **{result['ev_r']:+.4f}** · sd_R = {result['sd_r']:.4f}")
        L.append(f"- **p_boot = {result['p_boot']:.5f}** (RASMI) · p_z = {result['p_z']:.5f} (sensitivity) · "
                 f"p_atr = {result['p_atr']:.5f} (ATR-unit sensitivity)")
        L.append(f"- 90% bootstrap CI ya EV_R: [{result['ci90'][0]:+.4f}, {result['ci90'][1]:+.4f}]")
        L.append(f"- MDE screen (shrink {SHRINK_TIP}): MDE={s['mde']:.4f} vs forecast={s['forecast']:.4f} → "
                 f"{'PASS' if s['passes'] else 'FAIL'} (margin ×{s['margin']:.2f})")
        L.append(f"- descriptive (NON-gating): shares={ {k: round(x, 2) for k, x in result['shares'].items()} } · "
                 f"timeout_share={result['timeout_share']:.2f} · lag-1 ρ={result['rho1']:+.3f} "
                 f"{'(⚠ >0.3 → engine recheck, referee cond 3)' if abs(result['rho1'])>0.3 else ''}")
        L.append(f"\n## VERDICT (pre-registered §6): **{v}**\n")
        if v == "PASS":
            L.append("→ FAMILY claim = **PROVEN-OOS-PROVISIONAL (family level)**: inaidhinisha forward "
                     "paper-trading ya reps 4 kama stream moja + priority ya R3/R8. HAIUNDI STRAT-00x, "
                     "HAIRUHUSU capital, HAITHIBITISHI pair/cell binafsi (design §6).")
        elif v == "FAIL":
            L.append("→ Family claim inakufa kwenye dirisha hili kwa heshima; C2-WATCH inabaki forward-only "
                     "(path a). HAKUNA re-test ya compression-H4 kwenye 2025-01→2026-04 (design §6).")
    else:
        L.append(f"\n## VERDICT: **{v}** (N<2 — hakuna trades za kutosha kwenye {result['split']}).\n")
    L.append("\n## Caveats (design §7 — verbatim record)\n")
    L.append("1. Confirmation, si discovery (family-era leak §A3-W3) → PROVISIONAL cap + forward gate.")
    L.append("2. Window overlap na STRAT-001/002 proof era → PASS = correlated evidence, si replication huru.")
    L.append("3. VALID estimates ni hot (VALID/TRAIN ~2×) → shrink = measured slope (0.346), si pessimism.")
    L.append("4. One-sided deal: shrink-0.35 truth → power 0.62; FAIL ~38% hata kama forecast ni sahihi.")
    L.append("\n*design: SCIENTIST-D reports/family_pooled_design.md · engine strategy_lab.pvalue_boot "
             "(wave1_referee_report.md) · reuse-only. Profitable != Tradable Edge. Protect capital first.*")
    rpt = out_root / "reports" / OUT_REPORT; rpt.parent.mkdir(parents=True, exist_ok=True)
    rpt.write_text("\n".join(L), encoding="utf-8")
    return jl, rpt


# ---------- fixtures (self-test — bila data ya nje, Rule 7) ----------
def _fixture(pair, seed, n=6000, scale=1.0):
    """Synthetic window (+ts/atr/spr/vol) inayoiga load_window output kwa self-test. scale = pip-scale
    factor (AT1): inazidisha o/h/l/c/atr/spr — R-normalization inapaswa kuwa invariant (design §2)."""
    o, h, l, c, tc, hour = _synthetic(n=n, seed=seed)
    atr = np.maximum(h - l, 0.1)
    spr = np.full(n, 1.0)
    vol = np.array(["NORMAL"] * n)
    ts = np.datetime64("2025-01-01T00") + np.arange(n) * np.timedelta64(4, "h")   # H4 spacing
    if scale != 1.0:
        o, h, l, c, atr, spr = (x * scale for x in (o, h, l, c, atr, spr))
    return dict(o=o, h=h, l=l, c=c, atr=atr, spr=spr, tc=tc, hour=hour, vol=vol, ts=ts, days=250)


def self_test():
    ok_all = True

    # ---- AT2 R-normalization correctness (EXACT): forced SL → -(1+cost/R); forced TP → tp/sl - cost/R
    # crafted market bars: bar1 sig long; ATR known; SL-forced fixture kisha TP-forced fixture.
    from event_quality_report import SLIP_MARKET
    a_val = 2.0
    # SL exit: entry o[1]=100; bar2 drops below SL (100 - 1.5*2 = 97) → exit sl_px; cost = spr+0.1
    o = np.array([100.0, 100.0, 100.0, 100.0]); c = o.copy()
    hSL = np.array([100.2, 100.2, 97.5, 100.2]); lSL = np.array([99.8, 99.8, 96.0, 99.8])
    atr = np.full(4, a_val); spr = np.full(4, 0.5); hour = np.zeros(4, int)
    ts = np.datetime64("2025-01-01") + np.arange(4) * np.timedelta64(4, "h")
    sig = np.array([0, 1, 0, 0])
    trs = episodes({"sig": sig}, "market", o, hSL, lSL, c, atr, spr, hour, sl_atr=1.5, tp_atr=1.5)
    rows = _r_normalize(trs, atr, 1.5, ts, "TEST")
    cost = 0.5 + SLIP_MARKET
    exp_sl = -(1 + cost / (1.5 * a_val))
    at2_sl = len(rows) == 1 and abs(rows[0]["pnl_R"] - exp_sl) < 1e-12
    # TP exit: bar2 rises above TP (100 + 1.5*2 = 103)
    hTP = np.array([100.2, 100.2, 103.5, 100.2]); lTP = np.array([99.8, 99.8, 99.9, 99.8])
    trs2 = episodes({"sig": sig}, "market", o, hTP, lTP, c, atr, spr, hour, sl_atr=1.5, tp_atr=1.5)
    rows2 = _r_normalize(trs2, atr, 1.5, ts, "TEST")
    exp_tp = (1.5 / 1.5) - cost / (1.5 * a_val)
    at2_tp = len(rows2) == 1 and abs(rows2[0]["pnl_R"] - exp_tp) < 1e-12
    at2 = at2_sl and at2_tp
    ok_all &= at2
    print(f"[AT2] R-norm exact: SL={rows[0]['pnl_R']:.6f}(exp {exp_sl:.6f}) TP={rows2[0]['pnl_R']:.6f}"
          f"(exp {exp_tp:.6f}) -> {'OK' if at2 else 'FAIL'}")

    # ---- AT1 pip-scale invariance ya NORMALIZATION (design §2). Signals FIXED (market sig) ili kutenga
    # R-normalization na event re-firing: event fns (nr7_break) zina absolute `tick` threshold — SI
    # pip-scale invariant (property tofauti; SIO madai ya §2). Given trades zilezile: trade STRUCTURE
    # ni EXACT-invariant (touch detection scale-free); pnl_R invariant ISIPOKUWA slippage ISIYO-pip-
    # scaled ya episodes() (SLIP_MARKET/STOP = const pip). DEVIATION-with-evidence (§2 'exact' inasahau
    # fixed slippage — internal na §5-AT2 ambayo cost/R yenyewe si scale-free): residual = -SLIP·
    # (1-1/scale)/R_trade — nahakiki EXACT dhidi ya closed-form. Referee: OQ#1.
    SCALE = 100.0
    b_AAA = _fixture("AAA", 21, n=2000); s_AAA = _fixture("AAA", 21, n=2000, scale=SCALE)
    b_BBB = _fixture("BBB", 22, n=2000)
    sigA = np.zeros(2000, int); sigA[::13] = 1                       # sig FIXED (haitegemei bei/scale)
    sigB = np.zeros(2000, int); sigB[7::17] = -1

    def _mkt_stream(bars, sig, sl_atr, pair):
        trs = episodes({"sig": sig}, "market", bars["o"], bars["h"], bars["l"], bars["c"],
                       bars["atr"], bars["spr"], bars["hour"], None, sl_atr=sl_atr, tp_atr=1.5)
        return _r_normalize(trs, bars["atr"], sl_atr, bars["ts"], pair)

    p_base = pool_streams([_mkt_stream(b_AAA, sigA, 1.5, "AAA"), _mkt_stream(b_BBB, sigB, 1.5, "BBB")])
    p_scl = pool_streams([_mkt_stream(s_AAA, sigA, 1.5, "AAA"), _mkt_stream(b_BBB, sigB, 1.5, "BBB")])
    struct_ok = ([(r["pair"], r["entry_bar"], r["dir"], r["exit_bar"]) for r in p_base]
                 == [(r["pair"], r["entry_bar"], r["dir"], r["exit_bar"]) for r in p_scl])
    resid_ok = True; bbb_ok = True
    for rb, rs in zip(p_base, p_scl):
        if rb["pair"] == "BBB":
            bbb_ok &= (rb["pnl_R"] == rs["pnl_R"])                   # BBB haijaguswa → bit-identical
        else:                                                        # AAA × SCALE (market → SLIP_MARKET)
            exp_resid = -SLIP_MARKET * (1 - 1 / SCALE) / rb["r_trade"]
            resid_ok &= abs((rb["pnl_R"] - rs["pnl_R"]) - exp_resid) < 1e-9
    at1 = struct_ok and resid_ok and bbb_ok and len(p_base) > 8
    ok_all &= at1
    print(f"[AT1] pip-scale (normalization): struct-invariant={struct_ok} BBB-bit-identical={bbb_ok} "
          f"AAA-residual=closed-form={resid_ok} (fixed-slip DEVIATION → OQ#1) -> {'OK' if at1 else 'FAIL'}")

    # ---- AT3 determinism: p bit-identical mara mbili (seed=registration string); seed-stable
    reg = registration_string(); seed = _seed_from_registration(reg)
    pooled_R = np.array([x["pnl_R"] for x in p_base])
    pa = pvalue_boot(pooled_R, B=800, mean_block=3, seed=seed)
    pb = pvalue_boot(pooled_R, B=800, mean_block=3, seed=seed)
    seed_stable = _seed_from_registration(reg) == _seed_from_registration(reg)
    at3 = pa == pb and seed_stable and isinstance(seed, int)
    ok_all &= at3
    print(f"[AT3] determinism: p stable={pa==pb} seed-stable={seed_stable} seed={seed} -> {'OK' if at3 else 'FAIL'}")

    # ---- AT4 mixture-null size (SCALED sanity; full 20k×B=50k = referee MC, design §5-AT4).
    # 4-component two-point mixture, EV=0 kila component, win% + shares za reps; interleaved random;
    # N=341. Nahakiki boot size ~nominal na < z size (mirror wave1 [8]); band pana kwa scaled reps/B.
    winr = (0.729, 0.769, 0.402, 0.522)                              # REP win% (design §1)
    shr = np.array([0.17, 0.35, 0.25, 0.22]); shr = shr / shr.sum()  # shares (design §4)
    rng = np.random.default_rng(4040); M, N, Bc = 500, 341, 300
    rej_b = rej_z = 0
    for m in range(M):
        comp = rng.choice(4, size=N, p=shr)
        x = np.empty(N)
        for k in range(4):                                          # two-point EV=0: win=+(1-w), loss=-w
            mask = comp == k; w = winr[k]
            u = rng.random(mask.sum()) < w
            x[mask] = np.where(u, (1 - w), -w)
        if pvalue_boot(x, B=Bc, seed=7000 + m) < ALPHA:
            rej_b += 1
        if pvalue_gt0(x) < ALPHA:
            rej_z += 1
    size_b, size_z = rej_b / M, rej_z / M
    at4 = 0.015 <= size_b <= 0.085 and size_b <= size_z + 0.02       # ~nominal, si zaidi ya z kwa kiasi
    ok_all &= at4
    print(f"[AT4] mixture-null size (scaled sanity; referee=full MC): boot={size_b:.3f} z={size_z:.3f} "
          f"band[0.015,0.085] -> {'OK' if at4 else 'FAIL'}")

    # ---- AT5 holdout red line: run_family(split=holdout) bila token → PermissionError (load_window guard)
    try:
        run_family("holdout", holdout_token=None, write=False)
        at5 = False
    except PermissionError:
        at5 = True
    try:
        run_family("holdout", holdout_token="wrong", write=False)
        at5 = at5 and False
    except PermissionError:
        at5 = at5 and True
    ok_all &= at5
    print(f"[AT5] holdout red-line (no/wrong token → refuse via load_window): {at5} -> {'OK' if at5 else 'FAIL'}")

    # ---- AT6 no-clobber + AT7 dedup + AT8 dry-run shape: full pipeline kwa fixtures (4 pseudo-pairs)
    # kupitia monkeypatch ya load_window (fixtures badala ya parquet — bila data ya nje, Rule 7).
    import tempfile, os
    _self = sys.modules[__name__]                                   # module HALISI (=__main__ ikiendeshwa)
    fx = {c["pair"]: _fixture(c["pair"], 30 + k) for k, c in enumerate(REP_CELLS)}
    orig = _self.load_window
    _self.load_window = lambda sym, tf, split, token=None: fx.get(sym)
    try:
        with tempfile.TemporaryDirectory() as tmp:
            # sentinel candidates file — AT6 lazima ISIGUSWE
            sdir = Path(tmp) / "data" / "strategies"; sdir.mkdir(parents=True)
            (sdir / "candidates.jsonl").write_text("SENTINEL\n", encoding="utf-8")
            res = run_family("validation", out_root=tmp)             # AT8 dry-run shape (VALIDATION)
            files = sorted(os.listdir(sdir))
            candidates_intact = (sdir / "candidates.jsonl").read_text(encoding="utf-8") == "SENTINEL\n"
            report_written = (Path(tmp) / "reports" / OUT_REPORT).exists()
            jsonl_written = (sdir / OUT_JSONL).exists()
            # AT7 dedup enforced ndani ya pool_streams (assert); AT8 shape: result ina fields
            at8_shape = all(k in res for k in ("n", "ev_r", "p_boot", "screen", "verdict"))
            at67 = (candidates_intact and jsonl_written and report_written
                    and "candidates_c2.jsonl" not in files    # hazizalishwi
                    and res["n"] > 0 and at8_shape)
    finally:
        _self.load_window = orig
    ok_all &= at67
    print(f"[AT6/7/8] no-clobber(candidates intact={candidates_intact}) + outputs({OUT_JSONL},report="
          f"{report_written}) + dedup(pool assert) + dry-run N={res['n']} verdict={res['verdict']} "
          f"-> {'OK' if at67 else 'FAIL'}")

    # ---- reuse purity: episodes/_mask_context/pvalue_boot reused kama-zilivyo; load_window +ts additive
    import inspect
    from strategy_lab import _mask_context as _mc, pvalue_boot as _pb, load_window as _lw
    reuse_ok = (callable(episodes) and callable(_mc) and callable(_pb)
                and "ts=df[\"ts\"].to_numpy()" in inspect.getsource(_lw)   # +ts additive (§8.1)
                and b_AAA.get("ts") is not None)
    ok_all &= reuse_ok
    print(f"[reuse] episodes/_mask_context/pvalue_boot reused (ZERO changes); load_window +ts additive "
          f"-> {'OK' if reuse_ok else 'FAIL'}")

    print(f"\nSELF-TEST: {'PASS' if ok_all else 'FAIL'}")
    return 0 if ok_all else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="validation", choices=["validation", "holdout"],
                    help="validation = AT8 dry-run/screen; holdout = one-shot (Chief token)")
    ap.add_argument("--holdout-final", dest="token", default=None, help="Chief token kwa holdout (§8.4)")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    res = run_family(a.split, a.token)
    print(f"family-pooled {a.split}: N={res['n']} verdict={res.get('verdict')}")
    if res.get("ev_r") is not None:
        print(f"  EV_R={res['ev_r']:+.4f} p_boot={res['p_boot']:.5f} screen={'PASS' if res['screen']['passes'] else 'FAIL'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
