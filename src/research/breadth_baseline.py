"""
breadth_baseline.py — M4-0: BREADTH BASELINE (docs/CYCLE4_ML_CHARTER.md §1B/§5 + docs/KAIROS_3_SPEC.md §5.3).

KUSUDI (moja tu): kutoa **namba ambayo KAIROS-3 LAZIMA ishinde**. Logic ni ILE ILE iliyothibitika
(`nr7_break` × H1 × no-LATE — STRAT-001/002), imeenezwa kwa **pairs 12** badala ya 2. Hii SI
hypothesis mpya, SI edge claim: ni **kipimo cha baseline** cha chanzo (B) cha nafasi (charter §1B).
ML (HATUA 1-3) lazima izidi hii, si nr7-pairs-2 pekee (charter §5; spec §5.3).

MUUNDO:
  1. Kila pair (hadi 12) × exit-variants MBILI — **SL2.0/TP1.0** (jiometri ya KAIROS-1) na
     **SL1.0/TP1.0** (jiometri ya KAIROS-2) — TF=H1, `nr7_break`, session_filter="no-LATE",
     vol_filter=None, max_hold=24 (default golden). episodes() -> trades zenye **gharama halisi**
     (spread ya bar ya entry + slippage; L-039 RED LINE — hakuna namba bila costs).
  2. **POOLED ndiyo hukumu (L-041):** R-normalization ya `family_pooled._r_normalize` (pnl_R =
     pnl_pips / (sl_atr × atr[signal_bar])) -> `pool_streams` (union sorted na ts_entry) -> EV_R,
     EV_pips, N, trades/mwaka, p_boot (engine RASMI), CI90, win%, PF.
     **HAKUNA best-pair selection.** Per-pair = **diagnostics TU** (yenye tahadhari iliyoandikwa).
  3. **SPLITS: TRAIN + VALIDATION PEKEE.** HOLDOUT (2025-01→2026-04) HAIGUSWI; dirisha SEALED
     (2026-05+, Doctrine §3.1b) haliingii kabisa (guard ya `_guard_split` KABLA ya kusoma data,
     pamoja na red-line iliyopo ya `load_window`).
  4. Output: `reports/breadth_baseline.md` (pooled EV/N/p kwa kila variant + **BASELINE LINE**) +
     `data/strategies/breadth_baseline.jsonl` (rekodi za pair/pooled/rule/baseline).
  5. **PENDEKEZO la `pairs[]`** kwa `config/models.yaml` — kwa **KANUNI, SI ranking**:
     pair inapendekezwa IKIWA `EV_R > 0` kwenye **TRAIN NA VALIDATION** NA `N_valid >= 30`.
     **HAKUNA "top-N kwa EV"** (= max-selection bias, LESSON-041). Ripoti inaonyesha zilizopita NA
     zilizokataliwa + sababu. Ni **PENDEKEZO** — PD ndiye anayehariri models.yaml.

ADDITIVE / REUSE-ONLY: **ZERO statistic/fill mpya**. episodes (golden), _mask_context, pvalue_boot,
pvalue_gt0, load_window, _r_normalize, pool_streams, _boot_ci, _seed_from_registration = **imports TU**
(byte-identical). Kinachoongezwa hapa ni accounting (mean/win%/PF/trades-per-year), runner na ripoti.

Endesha (PC ya data):  python breadth_baseline.py --run
Self-test (bila data):  python breadth_baseline.py --self-test
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

from event_library_v2 import EVENTS_V2
from event_quality_report import episodes
from strategy_lab import load_window, _mask_context, pvalue_boot, pvalue_gt0
from family_pooled import _r_normalize, pool_streams, _boot_ci, _seed_from_registration

REPO_ROOT = Path(__file__).resolve().parents[2]

# ---------- SPEC (FROZEN kwa M4-0 — hakuna tuning; logic = STRAT-001/002 ILE ILE) ----------
EVENT = "nr7_break"
TF = "H1"
SESSION_FILTER = "no-LATE"
VOL_FILTER = None
MAX_HOLD = 24                                  # default golden ya H1 (event_quality_report.MAX_HOLD)
VARIANTS = ((2.0, 1.0), (1.0, 1.0))            # (sl_atr, tp_atr): KAIROS-1 · KAIROS-2 geometry
SPLITS = ("train", "validation")               # HOLDOUT + sealed 2026-05+ HAZIGUSWI (§3.1b)
GOLD = "XAUUSD"                                # pip-scale nje ya FX -> EV_pips ya FX inaripotiwa pia

# engine RASMI (haijabadilishwa — pvalue_boot ya strategy_lab)
B_BOOT = 10_000
MEAN_BLOCK = 3
ALPHA = 0.05
B_MIN = 1_000                                  # p floor 1e-3 — inatosha kwa α=0.05 (baseline descriptive)
MAX_BOOT_CELLS = 2e7                           # ulinzi wa RAM: B×N (idx array ya _stationary_indices)

# kanuni ya pairs[] (pre-registered — SI ranking)
MIN_N_VALID = 30

REG_PREFIX = "BREADTH-BASELINE-M4-0"
DAYS_PER_YEAR = 365.25
OUT_JSONL = "breadth_baseline.jsonl"
OUT_REPORT = "breadth_baseline.md"


def _pairs():
    from market_state_engine import cfg
    return list(cfg()["pairs"])


def variant_key(sl_atr, tp_atr):
    return f"SL{sl_atr:g}/TP{tp_atr:g}"


def _guard_split(split):
    """RED LINE ya M4-0: TRAIN + VALIDATION PEKEE. HOLDOUT (2025-01→2026-04) = one-shot ya gate ya
    mwisho (charter §4.1); dirisha SEALED 2026-05+ (Doctrine §3.1b) halifunguliwi na utafiti.
    Inakataa KABLA ya kusoma data yoyote (juu ya red-line iliyopo ya load_window)."""
    if split not in SPLITS:
        raise PermissionError(
            f"M4-0 BREADTH ni TRAIN+VALIDATION PEKEE — split='{split}' imekataliwa. "
            "HOLDOUT = one-shot ya gate ya mwisho (charter §4.1/§5); sealed 2026-05+ = §3.1b.")


def _reg_string(sl_atr, tp_atr, split):
    """Seed deterministic kutoka spec ya variant (hashing ILEILE ya family_pooled — reuse)."""
    return "|".join([REG_PREFIX, EVENT, TF, SESSION_FILTER, str(VOL_FILTER),
                     variant_key(sl_atr, tp_atr), f"hold{MAX_HOLD}", split])


def boot_B(n, B=B_BOOT):
    """B halisi ya bootstrap: engine ILEILE, lakini _stationary_indices inaunda array (B, N) —
    pooled-12 N inaweza kuwa maelfu. Cap = MAX_BOOT_CELLS (RAM), sakafu = B_MIN. B_eff inaripotiwa."""
    if n < 2:
        return int(B)
    cap = int(MAX_BOOT_CELLS // max(n, 1))          # B inayotosha kwenye RAM kwa N hii
    return int(min(int(B), max(B_MIN, cap)))        # sakafu B_MIN, lakini kamwe zaidi ya B iliyoombwa


# ---------- streams (REUSE: event fn -> _mask_context -> episodes -> _r_normalize) ----------
def pair_stream(pair, split, sl_atr, tp_atr):
    """R-stream ya pair moja kwa variant moja. Njia SAWASAWA na family_pooled.cell_stream /
    swing_family._pair_stream (fill rules HAZIGUSWI). Rudisha (rows, years) au (None, None) kama
    dirisha halipo. years = span halisi ya ts (kwa trades/mwaka)."""
    _guard_split(split)
    data = load_window(pair, TF, split)
    if data is None or data.get("ts") is None:
        return None, None
    spec = EVENTS_V2[EVENT]
    o, h, l_, c = data["o"], data["h"], data["l"], data["c"]
    atr, spr, hour, vol, ts = data["atr"], data["spr"], data["hour"], data.get("vol"), data["ts"]
    out = spec["fn"](o, h, l_, c, data.get("tc"), hour)
    out = _mask_context(out, spec["entry"], hour, vol, SESSION_FILTER, VOL_FILTER)
    trs = episodes(out, spec["entry"], o, h, l_, c, atr, spr, hour, vol,
                   sl_atr=sl_atr, tp_atr=tp_atr, max_hold=MAX_HOLD)
    rows = _r_normalize(trs, atr, sl_atr, ts, pair)
    years = float((ts[-1] - ts[0]) / np.timedelta64(1, "D") / DAYS_PER_YEAR)
    return rows, years


def _acct(rows):
    """Accounting TU (hakuna statistic mpya): N, EV_R, EV_pips, win%, PF juu ya trades ZILIZO-net
    (gharama zimo ndani ya pnl kutoka episodes — L-039)."""
    n = len(rows)
    if n == 0:
        return dict(n=0, ev_R=None, ev_pips=None, win=None, pf=None)
    R = np.array([r["pnl_R"] for r in rows], float)
    P = np.array([r["pnl_pips"] for r in rows], float)
    gain = float(R[R > 0].sum()); loss = float(-R[R < 0].sum())
    return dict(n=n, ev_R=round(float(R.mean()), 4), ev_pips=round(float(P.mean()), 4),
                win=round(float((P > 0).mean()), 4),
                pf=(round(gain / loss, 3) if loss > 0 else None))


def run_variant(split, sl_atr, tp_atr, pairs=None, B=B_BOOT):
    """Pooled breadth run ya variant moja kwenye split moja. POOLED = hukumu (L-041); per-pair =
    diagnostics. Pair bila dirisha -> inarekodiwa `missing` (SI kimya — inaonekana kwenye ripoti)."""
    _guard_split(split)
    pairs = pairs or _pairs()
    streams, per_pair, missing = [], [], []
    rate_sum = 0.0
    for pair in pairs:
        rows, years = pair_stream(pair, split, sl_atr, tp_atr)
        if rows is None:
            missing.append(pair)
            continue
        streams.append(rows)
        st = _acct(rows)
        st.update(pair=pair, years=round(years, 3),
                  trades_per_year=(round(len(rows) / years, 2) if years > 0 else None))
        per_pair.append(st)
        if years > 0:
            rate_sum += len(rows) / years
    pooled = pool_streams(streams)                       # dedup (pair, entry_bar) — AT7 ya family_pooled
    R = np.array([r["pnl_R"] for r in pooled], float)
    n = len(R)
    res = dict(split=split, sl_atr=sl_atr, tp_atr=tp_atr, variant=variant_key(sl_atr, tp_atr),
               pairs_used=[p["pair"] for p in per_pair], missing=missing, per_pair=per_pair,
               trades_per_year=round(rate_sum, 2))
    res.update(_acct(pooled))
    # EV_pips ya FX pekee (bila XAUUSD): pip ya gold (0.01) si pip ya FX — kuchanganya pips
    # kunapotosha ULINGANIFU na KAIROS-1/2 (1.92 / 2.65 pips). SI selection: R-units ndio
    # currency ya hukumu; hii ni column ya pip-scale comparability (imeandikwa mapema).
    P_fx = np.array([r["pnl_pips"] for r in pooled if r["pair"] != GOLD], float)
    res["ev_pips_fx"] = (round(float(P_fx.mean()), 4) if len(P_fx) else None)
    res["n_fx"] = int(len(P_fx))
    if n >= 2:
        seed = _seed_from_registration(_reg_string(sl_atr, tp_atr, split))
        b_eff = boot_B(n, B)
        res.update(seed=seed, B_eff=b_eff,
                   p_boot=round(float(pvalue_boot(R, B=b_eff, mean_block=MEAN_BLOCK, seed=seed)), 6),
                   p_z=round(float(pvalue_gt0(R)), 6))
        lo, hi = _boot_ci(R, 0.90, seed=seed)
        res["ci90_R"] = [round(lo, 4), round(hi, 4)]
    else:
        res.update(seed=None, B_eff=None, p_boot=1.0, p_z=1.0, ci90_R=[None, None])
    return res


# ---------- §5 PENDEKEZO la pairs[] — KANUNI, SI ranking (L-041) ----------
def recommend_pairs(train_per_pair, valid_per_pair, min_n_valid=MIN_N_VALID):
    """KANUNI (pre-registered, SI ranking): pair inapendekezwa IKIWA **EV_R > 0 kwenye TRAIN NA
    EV_R > 0 kwenye VALIDATION NA N_valid >= min_n_valid**. HAKUNA "top-N kwa EV" — hiyo ni
    max-selection bias (LESSON-041, 3/3 zilipinduka OOS). Orodha zinapangwa kwa **alfabeti**, si
    kwa EV, ili hata mpangilio usipendekeze ranking.
    Rudisha (passed, rejected) — kila mmoja list ya dict yenye namba na sababu."""
    tr = {p["pair"]: p for p in train_per_pair}
    va = {p["pair"]: p for p in valid_per_pair}
    passed, rejected = [], []
    for pair in sorted(set(tr) | set(va)):
        t, v = tr.get(pair), va.get(pair)
        reasons = []
        if t is None or t["n"] == 0:
            reasons.append("hakuna trades TRAIN")
        elif t["ev_R"] is None or t["ev_R"] <= 0:
            reasons.append(f"EV_R TRAIN {t['ev_R']:+.4f} <= 0")
        if v is None or v["n"] == 0:
            reasons.append("hakuna trades VALIDATION")
        else:
            if v["ev_R"] is None or v["ev_R"] <= 0:
                reasons.append(f"EV_R VALID {v['ev_R']:+.4f} <= 0")
            if v["n"] < min_n_valid:
                reasons.append(f"N_valid {v['n']} < {min_n_valid}")
        rec = dict(pair=pair,
                   ev_R_train=(t["ev_R"] if t else None), n_train=(t["n"] if t else 0),
                   ev_R_valid=(v["ev_R"] if v else None), n_valid=(v["n"] if v else 0),
                   ev_pips_train=(t["ev_pips"] if t else None),
                   ev_pips_valid=(v["ev_pips"] if v else None))
        if reasons:
            rejected.append(dict(rec, reasons=reasons))
        else:
            passed.append(rec)
    return passed, rejected


def _baseline_line(variants):
    """BASELINE LINE = bar ambayo KAIROS-3 LAZIMA izidi. Variants ni MBILI (m=2) — bar inachukuliwa
    kwa **variant YENYE NGUVU ZAIDI kwenye VALIDATION** (EV_R). Hii SI selection ya edge: kuchagua
    bar ya JUU ni conservative kwa challenger (inafanya kupita kuwe GUMU zaidi). Namba za variant
    zote mbili zinabaki kwenye ripoti."""
    best, best_ev = None, None
    for key, v in variants.items():
        ev = v["splits"]["validation"].get("ev_R")
        if ev is None:
            continue
        if best_ev is None or ev > best_ev:
            best, best_ev = key, ev
    if best is None:
        return dict(variant=None, note="hakuna trades za VALIDATION — baseline haipatikani")
    val = variants[best]["splits"]["validation"]
    return dict(variant=best, split="validation", n=val["n"], ev_R=val["ev_R"],
                ev_pips=val["ev_pips"], ev_pips_fx=val["ev_pips_fx"], n_fx=val["n_fx"],
                trades_per_year=val["trades_per_year"], p_boot=val["p_boot"],
                pairs_used=len(val["pairs_used"]),
                other_variants={k: v["splits"]["validation"].get("ev_R") for k, v in variants.items()})


def run_baseline(out_root=REPO_ROOT, write=True, pairs=None, B=B_BOOT):
    """M4-0 kamili: variants 2 × splits 2 (TRAIN+VALIDATION) -> pooled + per-pair + pairs[]-rule ->
    BASELINE LINE -> outputs. Deterministic (hakuna timestamp ndani ya result)."""
    variants = {}
    for sl_atr, tp_atr in VARIANTS:
        splits = {sp: run_variant(sp, sl_atr, tp_atr, pairs=pairs, B=B) for sp in SPLITS}
        passed, rejected = recommend_pairs(splits["train"]["per_pair"], splits["validation"]["per_pair"])
        variants[variant_key(sl_atr, tp_atr)] = dict(sl_atr=sl_atr, tp_atr=tp_atr, splits=splits,
                                                     pairs_passed=passed, pairs_rejected=rejected)
    result = dict(event=EVENT, tf=TF, session_filter=SESSION_FILTER, vol_filter=VOL_FILTER,
                  max_hold=MAX_HOLD, splits=list(SPLITS), min_n_valid=MIN_N_VALID,
                  variants=variants, baseline=_baseline_line(variants))
    if write:
        _write_outputs(result, out_root)
    return result


# ---------- outputs ----------
def _f(x, spec="+.4f"):
    return "—" if x is None else format(x, spec)


def _write_outputs(res, out_root):
    out_root = Path(out_root)
    sdir = out_root / "data" / "strategies"; sdir.mkdir(parents=True, exist_ok=True)
    jl = sdir / OUT_JSONL
    with open(jl, "w", encoding="utf-8") as f:
        for vk, v in res["variants"].items():
            for sp, r in v["splits"].items():
                for pp in r["per_pair"]:
                    f.write(json.dumps(dict(pp, kind="pair", variant=vk, split=sp), sort_keys=True) + "\n")
                f.write(json.dumps(dict(kind="pooled", variant=vk, split=sp,
                                        **{k: r[k] for k in ("n", "ev_R", "ev_pips", "ev_pips_fx",
                                                             "n_fx", "win", "pf", "trades_per_year",
                                                             "p_boot", "p_z", "ci90_R", "B_eff",
                                                             "seed", "pairs_used", "missing")}),
                                   sort_keys=True, default=str) + "\n")
            f.write(json.dumps(dict(kind="pairs_rule", variant=vk, min_n_valid=res["min_n_valid"],
                                    passed=v["pairs_passed"], rejected=v["pairs_rejected"]),
                               sort_keys=True) + "\n")
        f.write(json.dumps(dict(kind="baseline", **res["baseline"]), sort_keys=True) + "\n")

    b = res["baseline"]
    L = [f"# M4-0 — BREADTH BASELINE ({EVENT} × pairs 12 × {TF}, POOLED)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | charter: docs/CYCLE4_ML_CHARTER.md §1B/§5 · spec: "
         f"docs/KAIROS_3_SPEC.md §5.3 | splits: TRAIN 2016-2022 + VALIDATION 2023-2024 | "
         f"filter: {SESSION_FILTER}, vol={VOL_FILTER}, max_hold={MAX_HOLD} | costs: spread halisi ya bar "
         f"ya entry + slippage (L-039) | engine RASMI: pvalue_boot mean_block={MEAN_BLOCK}, "
         f"seed=hash(registration)*\n",
         "> **HII SI EDGE CLAIM MPYA.** Logic ni ILE ILE iliyothibitika (`nr7_break` × H1 × no-LATE = "
         "STRAT-001/002), imeenezwa tu kutoka pairs 2 → pairs 12 (chanzo (B) cha nafasi, charter §1B). "
         "Kusudi ni **kipimo**: namba ambayo KAIROS-3 (na HATUA 1-3 zote za ML) **LAZIMA izidi**.\n",
         "> **HOLDOUT (2025-01→2026-04) HAIJAGUSWA** na dirisha **SEALED 2026-05+** (Doctrine §3.1b) "
         "haliingii — runner ina-refuse split yoyote isiyokuwa train/validation KABLA ya kusoma data.\n",
         "> **POOLED ndiyo hukumu (LESSON-041).** Per-pair = diagnostics TU; hakuna best-pair selection "
         "popote kwenye faili hii.\n"]

    # ---------- BASELINE LINE ----------
    L.append("\n## BASELINE LINE (bar ya KAIROS-3)\n")
    if b.get("variant") is None:
        L.append(f"> **{b.get('note')}**")
    else:
        L.append(f"> ### KAIROS-3 LAZIMA izidi: **EV_net = {_f(b['ev_pips_fx'], '+.2f')} pips/trade** "
                 f"(pooled FX, N={b['n_fx']}, bila XAUUSD), "
                 f"**trades/mwaka = {_f(b['trades_per_year'], '.1f')}** (VALIDATION).")
        L.append(f">\n> Currency ya hukumu (L-041) = **EV_R = {_f(b['ev_R'])}** (R-units, pooled "
                 f"pairs {b['pairs_used']}). Pips: **{_f(b['ev_pips'], '+.2f')}** (pairs zote, "
                 f"pip-scale ya XAUUSD ndani) · **{_f(b['ev_pips_fx'], '+.2f')}** (FX pekee, N={b['n_fx']} — "
                 f"ndiyo inayolinganishwa na KAIROS-1 +1.92 / KAIROS-2 +2.65).")
        others = " · ".join(f"{k} EV_R={_f(x)}" for k, x in b["other_variants"].items())
        L.append(f">\n> N (VALID) = **{b['n']}** · p_boot = {b['p_boot']} · variant = **{b['variant']}** "
                 f"(variant yenye nguvu zaidi VALIDATION kati ya mbili — bar ya JUU = conservative kwa "
                 f"challenger; zote: {others}).")
        L.append(f">\n> Kwa spec §5.2 ya KAIROS-3 (EV_net ≥ 3.0 pips NA ≥ 3× gharama): bar halisi ya "
                 f"kupita = **max(3.0, {_f(b['ev_pips_fx'], '+.2f')})** pips/trade, NA trades/mwaka "
                 f"≥ {_f(b['trades_per_year'], '.1f')} (breadth haipaswi kupungua).")

    # ---------- pooled per variant ----------
    L.append("\n## Pooled (HUKUMU — L-041) kwa kila exit-variant\n")
    L.append("| variant | split | pairs | N | EV_R | CI90 (R) | EV_pips (12) | EV_pips (FX) | "
             "trades/mwaka | win% | PF | p_boot | p_z | B_eff |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for vk, v in res["variants"].items():
        for sp in res["splits"]:
            r = v["splits"][sp]
            ci = r["ci90_R"]
            ci_s = "—" if ci[0] is None else f"[{ci[0]:+.4f}, {ci[1]:+.4f}]"
            L.append(f"| {vk} | {sp.upper()} | {len(r['pairs_used'])} | {r['n']} | {_f(r['ev_R'])} | {ci_s} | "
                     f"{_f(r['ev_pips'], '+.2f')} | {_f(r['ev_pips_fx'], '+.2f')} | "
                     f"{_f(r['trades_per_year'], '.1f')} | "
                     f"{'—' if r['win'] is None else format(100 * r['win'], '.1f')} | "
                     f"{_f(r['pf'], '.2f')} | {r['p_boot']} | {r['p_z']} | {r['B_eff']} |")
    miss = {f"{vk}/{sp}": v["splits"][sp]["missing"]
            for vk, v in res["variants"].items() for sp in res["splits"] if v["splits"][sp]["missing"]}
    L.append(f"\n*Pairs bila dirisha (hazikuingia pooling): {miss or 'hakuna'}. "
             f"p_boot ni **descriptive** hapa (baseline, si test iliyosajiliwa) — TRAIN/VALIDATION "
             f"zimeshatumika na utafiti wa nr7; hakuna dirisha jipya lililochomwa.*")

    # ---------- per-pair diagnostics ----------
    L.append("\n## Per-pair (DIAGNOSTICS TU — ⚠ SI selection)\n")
    L.append("> ⚠ **TAHADHARI (LESSON-041):** namba hizi HAZITUMIKI kuchagua pair 'bora'. Kuchagua "
             "pair yenye EV kubwa zaidi ya TRAIN ni max-selection bias — ilipinduka hasi OOS 3/3. "
             "Zinaonyeshwa kwa uwazi wa accounting (jumla ya N zao = N ya pooled) na kwa kanuni ya "
             "`pairs[]` hapa chini, ambayo ni **sheria ya sign+N, si ranking**.\n")
    for vk, v in res["variants"].items():
        L.append(f"\n### {vk}\n")
        L.append("| pair | N (train) | EV_R (train) | EV_pips (train) | N (valid) | EV_R (valid) | "
                 "EV_pips (valid) | trades/mwaka (valid) |")
        L.append("|---|---|---|---|---|---|---|---|")
        tr = {p["pair"]: p for p in v["splits"]["train"]["per_pair"]}
        va = {p["pair"]: p for p in v["splits"]["validation"]["per_pair"]}
        for pair in sorted(set(tr) | set(va)):
            t, w = tr.get(pair), va.get(pair)
            L.append(f"| {pair} | {t['n'] if t else 0} | {_f(t['ev_R'] if t else None)} | "
                     f"{_f(t['ev_pips'] if t else None, '+.2f')} | {w['n'] if w else 0} | "
                     f"{_f(w['ev_R'] if w else None)} | {_f(w['ev_pips'] if w else None, '+.2f')} | "
                     f"{_f((w or {}).get('trades_per_year'), '.1f')} |")

    # ---------- pairs[] recommendation ----------
    L.append("\n## PENDEKEZO la `pairs[]` kwa `config/models.yaml` (KAIROS-1/2 multi-pair)\n")
    L.append(f"> **KANUNI (pre-registered, SI ranking):** pair inapendekezwa IKIWA **EV_R > 0 kwenye "
             f"TRAIN** NA **EV_R > 0 kwenye VALIDATION** NA **N_valid ≥ {res['min_n_valid']}**.\n"
             f"> **HAKUNA \"top-N kwa EV\"** (= max-selection bias, LESSON-041). Orodha ni ya "
             f"**alfabeti**, si ya EV — hata mpangilio usipendekeze ranking.\n"
             f"> Hili ni **PENDEKEZO la utafiti. PD ndiye anayehariri `config/models.yaml`** — code "
             f"haiandiki registry.\n")
    for vk, v in res["variants"].items():
        L.append(f"\n### {vk}\n")
        if v["pairs_passed"]:
            L.append("**(a) Zilizopita kanuni:**\n")
            L.append("| pair | EV_R train | EV_R valid | N valid | EV_pips valid |")
            L.append("|---|---|---|---|---|")
            for p in v["pairs_passed"]:
                L.append(f"| {p['pair']} | {_f(p['ev_R_train'])} | {_f(p['ev_R_valid'])} | "
                         f"{p['n_valid']} | {_f(p['ev_pips_valid'], '+.2f')} |")
            L.append(f"\n```yaml\n    pairs:      [{', '.join(p['pair'] for p in v['pairs_passed'])}]"
                     f"   # M4-0 rule: EV_R>0 train NA valid NA N_valid>={res['min_n_valid']}\n```")
        else:
            L.append("**(a) Zilizopita kanuni:** *hakuna* — kanuni haikupitishwa na pair yoyote "
                     "(matokeo halali: breadth haipanuki kwa variant hii).")
        L.append("\n**(b) Zilizokataliwa + sababu:**\n")
        L.append("| pair | EV_R train | EV_R valid | N valid | sababu |")
        L.append("|---|---|---|---|---|")
        for p in v["pairs_rejected"]:
            L.append(f"| {p['pair']} | {_f(p['ev_R_train'])} | {_f(p['ev_R_valid'])} | {p['n_valid']} | "
                     f"{'; '.join(p['reasons'])} |")

    # ---------- caveats ----------
    L.append("\n## Caveats (uwazi)\n")
    L.append("1. **Si edge claim.** Baseline = kipimo cha nafasi za logic iliyopo kwa pairs 12; p_boot "
             "ni descriptive. STRAT-001/002 PEKEE ndizo PROVEN (holdout one-shot) — docs/STRATEGIES.md.")
    L.append("2. **VALIDATION ni ya 2023-2024** na tayari imetumika na utafiti wa nr7 (grid ya S1/S2). "
             "Hakuna dirisha jipya lililofunguliwa hapa; HOLDOUT + sealed 2026-05+ hazijaguswa.")
    L.append("3. **Pips vs R:** XAUUSD ina pip 0.01 — EV_pips ya pairs zote inatawaliwa na gold. "
             "Hukumu = EV_R (dimensionless); safu ya FX-pekee ndiyo inayolinganishwa na KAIROS-1/2.")
    L.append("4. **trades/mwaka** = Σ ya per-pair (n_i / miaka_i) — pairs zinatradiwa SAMBAMBA; "
             "risk-engine (max_slots/correlated) itapunguza idadi halisi inayotekelezwa.")
    L.append("5. **Kanuni ya `pairs[]` haithibitishi pair yoyote OOS.** Ni screen ya sign-consistency "
             "(train NA valid) + N — inapunguza selection bias, HAIIONDOI. Uthibitisho = holdout/forward.")
    L.append(f"6. **B_eff** ya bootstrap inapunguzwa kutoka {B_BOOT:,} kadri N inavyokua (RAM: array "
             f"(B×N) ya _stationary_indices; sakafu {B_MIN:,}). Engine na mean_block hazijabadilika.")
    L.append("\n*reuse-only: episodes/_mask_context/pvalue_boot/load_window/_r_normalize/pool_streams/"
             "_boot_ci ni imports (ZERO changes). Profitable != Tradable Edge. Protect capital first.*")

    rpt = out_root / "reports" / OUT_REPORT; rpt.parent.mkdir(parents=True, exist_ok=True)
    rpt.write_text("\n".join(L), encoding="utf-8")
    return jl, rpt


# ---------- self-test (synthetic — bila data ya nje, Rule 7) ----------
def _fixture(seed, n=3000, start="2016-01-02T00", spr=1.0, price_scale=1.0):
    """H1 bars synthetic + ts (spacing saa 1) + vol_state. spr = spread constant (pips) kwa test ya
    gharama; price_scale = 'gold-like' kwa test ya R-normalization."""
    from event_library_v2 import _synthetic
    o, h, l_, c, tc, hour = _synthetic(n=n, seed=seed)
    o, h, l_, c = (x * price_scale for x in (o, h, l_, c))
    atr = np.maximum(h - l_, 0.1)
    ts = np.datetime64(start) + np.arange(n) * np.timedelta64(1, "h")
    hr = (ts.astype("datetime64[h]").astype(np.int64) % 24).astype(int)
    vol = np.array(["LOW", "NORMAL", "HIGH"])[np.arange(n) % 3]
    return dict(o=o, h=h, l=l_, c=c, atr=atr, spr=np.full(n, float(spr)), tc=tc,
                hour=hr, vol=vol, ts=ts, days=n // 24, ctx=None)


def self_test():
    ok = True
    import tempfile
    _self = sys.modules[__name__]
    orig_lw = _self.load_window
    P12 = ["EURUSD", "GBPUSD", "USDJPY", "EURJPY", "USDCAD", "USDCHF",
           "AUDUSD", "NZDUSD", "EURGBP", "GBPJPY", "EURCHF", "XAUUSD"]
    fx = {p: _fixture(40 + k, price_scale=(100.0 if p == GOLD else 1.0)) for k, p in enumerate(P12)}
    _self.load_window = lambda sym, tf, split, token=None: fx.get(sym)

    # ---- (b) HOLDOUT/sealed guard: refuse KABLA ya kusoma data (load_window haiitwi kabisa)
    called = []
    _self.load_window = lambda sym, tf, split, token=None: (called.append(sym) or fx.get(sym))
    guards = {}
    for bad in ("holdout", "sealed", "forward", "all"):
        try:
            run_variant(bad, 2.0, 1.0, pairs=P12, B=200)
            guards[bad] = False
        except PermissionError:
            guards[bad] = True
    try:
        pair_stream("EURUSD", "holdout", 2.0, 1.0)
        guards["pair_stream"] = False
    except PermissionError:
        guards["pair_stream"] = True
    b_ok = all(guards.values()) and called == [] and "holdout" not in SPLITS
    ok = ok and b_ok
    print(f"  [b] HOLDOUT/sealed guard: {guards} · load_window haikuitwa={called == []} · "
          f"SPLITS={SPLITS} -> {b_ok}")

    # ---- run mmoja wa variant kwa checks zinazofuata
    r = run_variant("validation", 2.0, 1.0, pairs=P12, B=500)

    # ---- (a) pooled math = family_pooled (recompute HURU kwa golden fns; hakuna statistic mpya)
    streams = []
    for p in P12:
        d = fx[p]
        spec = EVENTS_V2[EVENT]
        out = spec["fn"](d["o"], d["h"], d["l"], d["c"], d["tc"], d["hour"])
        out = _mask_context(out, spec["entry"], d["hour"], d["vol"], SESSION_FILTER, VOL_FILTER)
        trs = episodes(out, spec["entry"], d["o"], d["h"], d["l"], d["c"], d["atr"], d["spr"],
                       d["hour"], d["vol"], sl_atr=2.0, tp_atr=1.0, max_hold=MAX_HOLD)
        streams.append(_r_normalize(trs, d["atr"], 2.0, d["ts"], p))
    ref = pool_streams(streams)
    refR = np.array([x["pnl_R"] for x in ref], float)
    seed_ref = _seed_from_registration(_reg_string(2.0, 1.0, "validation"))
    p_ref = round(float(pvalue_boot(refR, B=boot_B(len(refR), 500), mean_block=MEAN_BLOCK, seed=seed_ref)), 6)
    ci_ref = _boot_ci(refR, 0.90, seed=seed_ref)
    a_ok = (r["n"] == len(refR)
            and abs(r["ev_R"] - round(float(refR.mean()), 4)) < 1e-12
            and r["p_boot"] == p_ref
            and abs(r["ci90_R"][0] - round(ci_ref[0], 4)) < 1e-12
            and abs(r["ci90_R"][1] - round(ci_ref[1], 4)) < 1e-12)
    ok = ok and a_ok
    print(f"  [a] pooled math == family_pooled (EV_R={r['ev_R']:+.4f}=={refR.mean():+.4f}, "
          f"p_boot={r['p_boot']}=={p_ref}, CI90 sawa, N={r['n']}) -> {a_ok}")

    # ---- (d) per-pair vs pooled N zinalingana (accounting closure)
    d_ok = (sum(pp["n"] for pp in r["per_pair"]) == r["n"] and len(r["per_pair"]) == 12
            and r["missing"] == [] and r["n"] > 0)
    ok = ok and d_ok
    print(f"  [d] Σ per-pair N ({sum(pp['n'] for pp in r['per_pair'])}) == pooled N ({r['n']}) · "
          f"pairs {len(r['per_pair'])}/12 -> {d_ok}")

    # ---- no-LATE decidability: hakuna trade yenye entry-bar hour ndani ya LATE (17-23)
    from event_quality_report import _sess
    late = [x for x in ref if _sess(int(fx[x["pair"]]["hour"][x["entry_bar"]])) == "LATE"]
    nl_ok = len(ref) > 0 and not late
    ok = ok and nl_ok
    print(f"  [no-LATE] trades {len(ref)}, entries LATE = {len(late)} (==0) -> {nl_ok}")

    # ---- gharama halisi kila namba (L-039): spread ya juu -> EV_pips ndogo kwa EXACTLY Δspread
    fx0 = {p: _fixture(40 + k, spr=0.0, price_scale=(100.0 if p == GOLD else 1.0))
           for k, p in enumerate(P12)}
    fx2 = {p: _fixture(40 + k, spr=2.0, price_scale=(100.0 if p == GOLD else 1.0))
           for k, p in enumerate(P12)}
    _self.load_window = lambda sym, tf, split, token=None: fx0.get(sym)
    r0 = run_variant("validation", 2.0, 1.0, pairs=P12, B=200)
    _self.load_window = lambda sym, tf, split, token=None: fx2.get(sym)
    r2 = run_variant("validation", 2.0, 1.0, pairs=P12, B=200)
    _self.load_window = lambda sym, tf, split, token=None: fx.get(sym)
    cost_ok = (r0["n"] == r2["n"] and abs((r0["ev_pips"] - r2["ev_pips"]) - 2.0) < 1e-9)
    ok = ok and cost_ok
    print(f"  [L-039] costs ndani ya kila namba: EV_pips(spr0)={r0['ev_pips']:+.4f} − "
          f"EV_pips(spr2)={r2['ev_pips']:+.4f} = {r0['ev_pips'] - r2['ev_pips']:.4f} (==2.0) -> {cost_ok}")

    # ---- (e) kanuni ya pairs[]: train-only chanya INAKATALIWA; N_valid<30 INAKATALIWA
    tr_pp = [dict(pair="AAAUSD", n=500, ev_R=0.05, ev_pips=1.0),      # + train, + valid, N ok  -> PASS
             dict(pair="BBBUSD", n=500, ev_R=0.30, ev_pips=9.9),      # + train KUBWA, − valid  -> REJECT
             dict(pair="CCCUSD", n=500, ev_R=-0.02, ev_pips=-1.0),    # − train, + valid        -> REJECT
             dict(pair="DDDUSD", n=500, ev_R=0.04, ev_pips=1.0),      # + / +, lakini N_valid<30-> REJECT
             dict(pair="EEEUSD", n=0, ev_R=None, ev_pips=None)]       # hakuna train            -> REJECT
    va_pp = [dict(pair="AAAUSD", n=120, ev_R=0.03, ev_pips=0.8),
             dict(pair="BBBUSD", n=120, ev_R=-0.01, ev_pips=-0.3),
             dict(pair="CCCUSD", n=120, ev_R=0.09, ev_pips=2.0),
             dict(pair="DDDUSD", n=29, ev_R=0.06, ev_pips=1.5),
             dict(pair="EEEUSD", n=120, ev_R=0.10, ev_pips=3.0)]
    passed, rejected = recommend_pairs(tr_pp, va_pp)
    names = [p["pair"] for p in passed]
    rej = {p["pair"]: p["reasons"] for p in rejected}
    e_ok = (names == ["AAAUSD"]                                        # MMOJA tu anapita
            and "BBBUSD" in rej and any("VALID" in s for s in rej["BBBUSD"])     # train-only -> KATAA
            and "CCCUSD" in rej and any("TRAIN" in s for s in rej["CCCUSD"])
            and "DDDUSD" in rej and any("N_valid" in s for s in rej["DDDUSD"])
            and "EEEUSD" in rej
            and names == sorted(names))                                # alfabeti, si EV-ranking
    # (e2) hakuna top-N: pair yenye EV KUBWA zaidi ya TRAIN (BBBUSD +0.30) HAIPO kwenye passed
    e_ok = e_ok and "BBBUSD" not in names
    ok = ok and e_ok
    print(f"  [e] pairs[]-rule: passed={names} (train-only BBBUSD +0.30 KATAA, N_valid 29 KATAA) "
          f"rejected={sorted(rej)} -> {e_ok}")

    # ---- (c) determinism + full run + outputs + BASELINE LINE
    with tempfile.TemporaryDirectory() as tmp:
        sdir = Path(tmp) / "data" / "strategies"; sdir.mkdir(parents=True)
        (sdir / "candidates.jsonl").write_text("SENTINEL\n", encoding="utf-8")   # no-clobber
        ra = run_baseline(out_root=tmp, pairs=P12, B=400)
        rb = run_baseline(out_root=tmp, pairs=P12, B=400)
        det = json.dumps(ra, sort_keys=True, default=str) == json.dumps(rb, sort_keys=True, default=str)
        intact = (sdir / "candidates.jsonl").read_text(encoding="utf-8") == "SENTINEL\n"
        rpt = (Path(tmp) / "reports" / OUT_REPORT).read_text(encoding="utf-8")
        recs = [json.loads(ln) for ln in open(sdir / OUT_JSONL, encoding="utf-8")]
        kinds = {x["kind"] for x in recs}
        base = ra["baseline"]
        # closure ya rule: kila pair iliyopita INA EV_R>0 pande zote NA N_valid>=30 (hakuna ubaguzi)
        rule_closed = all(p["ev_R_train"] > 0 and p["ev_R_valid"] > 0 and p["n_valid"] >= MIN_N_VALID
                          for v in ra["variants"].values() for p in v["pairs_passed"])
        # ...na kanuni ni EXHAUSTIVE: seti iliyopita == seti inayohesabiwa HURU kutoka per-pair
        # (hakuna cut ya ziada, hakuna top-N iliyofichwa)
        for v in ra["variants"].values():
            tr = {p["pair"]: p for p in v["splits"]["train"]["per_pair"]}
            va = {p["pair"]: p for p in v["splits"]["validation"]["per_pair"]}
            exp = sorted(p for p in set(tr) | set(va)
                         if p in tr and p in va and (tr[p]["ev_R"] or 0) > 0
                         and (va[p]["ev_R"] or 0) > 0 and va[p]["n"] >= MIN_N_VALID)
            rule_closed = rule_closed and exp == [p["pair"] for p in v["pairs_passed"]]
        # kila pair ipo passed AU rejected (hakuna kutoweka kimya)
        cover = all(len(v["pairs_passed"]) + len(v["pairs_rejected"]) == 12
                    for v in ra["variants"].values())
        var_ok = set(ra["variants"]) == {variant_key(*v) for v in VARIANTS} and len(VARIANTS) == 2
        splits_ok = all(set(v["splits"]) == set(SPLITS) for v in ra["variants"].values())
        # ripoti ina rekodi ya splits zilizotumika TU (TRAIN/VALIDATION) — hakuna row ya HOLDOUT
        no_holdout_rows = not any("| HOLDOUT |" in ln or "| SEALED |" in ln for ln in rpt.splitlines())
        c_ok = (det and intact and rule_closed and cover and var_ok and splits_ok and no_holdout_rows
                and kinds == {"pair", "pooled", "pairs_rule", "baseline"}
                and "BASELINE LINE" in rpt and "LAZIMA izidi" in rpt
                and "PENDEKEZO la `pairs[]`" in rpt and "DIAGNOSTICS TU" in rpt
                and base["variant"] in set(ra["variants"]))
    _self.load_window = orig_lw
    ok = ok and c_ok
    print(f"  [c] determinism={det} · no-clobber={intact} · rule-closure={rule_closed} · "
          f"coverage 12/12={cover} · variants={sorted(ra['variants'])} · splits={SPLITS} · "
          f"outputs={sorted(kinds)} · baseline={base['variant']} EV_R={_f(base['ev_R'])} -> {c_ok}")

    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true", help="endesha M4-0 breadth baseline (PC ya data)")
    ap.add_argument("--boot-B", dest="B", type=int, default=B_BOOT, help=f"B ya pvalue_boot (default {B_BOOT})")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.run:
        print("Tumia --run (breadth baseline) | --self-test.", file=sys.stderr)
        return 2
    res = run_baseline(B=a.B)
    b = res["baseline"]
    print(f"M4-0 BREADTH BASELINE ({EVENT} × {TF} × {SESSION_FILTER}, pairs pooled — L-041)")
    for vk, v in res["variants"].items():
        for sp in res["splits"]:
            r = v["splits"][sp]
            print(f"  {vk:12s} {sp:10s} N={r['n']:5d} EV_R={_f(r['ev_R'])} "
                  f"EV_pips={_f(r['ev_pips'], '+.2f')} (FX {_f(r['ev_pips_fx'], '+.2f')}) "
                  f"trades/yr={_f(r['trades_per_year'], '.1f')} p_boot={r['p_boot']}")
        print(f"    pairs[] pendekezo ({vk}): {[p['pair'] for p in v['pairs_passed']] or 'hakuna'}")
    if b.get("variant"):
        print(f"  BASELINE LINE -> KAIROS-3 LAZIMA izidi: EV_net={_f(b['ev_pips_fx'], '+.2f')} pips "
              f"(FX), EV_R={_f(b['ev_R'])}, trades/mwaka={_f(b['trades_per_year'], '.1f')} "
              f"(VALIDATION, variant {b['variant']})")
    print(f"  data/strategies/{OUT_JSONL}\n  reports/{OUT_REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
