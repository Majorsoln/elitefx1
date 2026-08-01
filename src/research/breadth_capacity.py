"""
breadth_capacity.py — M4-0b: COST STRESS + CAPACITY ya BREADTH (nyongeza ya M4-0, PD 2026-08-01).

KWA NINI: M4-0 imetoa breadth halali (pooled EV_R +0.0526 VALID, p<0.001) LAKINI **cost-thin**:
EV_net FX = +0.91 pips/trade ⇒ breakeven Δspread = **0.91 pip** (KAIROS-1 = 1.92, KAIROS-2 = 2.65).
Charter §4.4 inataka edge ~3-4× gharama. Kabla PD hajapanua `pairs[]` kwenda live, maswali MAWILI
lazima yajibiwe kwa NAMBA, si kwa matumaini:

  **(1) COST:** edge inastahimili nini? EV(Δspread) analytic + mgawanyo wa spread_state (NORMAL vs
      WIDE) wa bar ya ENTRY — je trades za WIDE ndizo zinazokula faida?
  **(2) CAPACITY:** trades ~2,680/mwaka ≈ 10-11/siku kwa pairs 12. Risk-engine ni **lango pekee**
      (max_slots 7 / max_correlated_slots 3, `config/ftmo_config.yaml`). Ni ngapi zitakataliwa
      kweli, na je zinazokataliwa ni BORA au MBAYA kuliko zinazopita?

REUSE-ONLY (ZERO statistic/fill mpya):
  · `cost_stress.ev_spread_table` (EV−Δ analytic) + `cost_stress.spread_split` (NORMAL/WIDE) — R5.
  · `breadth_baseline.pair_stream` (episodes -> _r_normalize -> golden chain ile ile) + `_guard_split`.
  · `family_pooled.pool_streams` (pooling + dedup).
  · **Config HALISI + semantiki HALISI za lango la live:** `live_engine._ftmo_config` /`._corr_group`
    (reservation) na `broker_adapter._groups_of` (check). Hakuna gate mpya iliyobuniwa hapa.
  · `spread_state` inasomwa kutoka state parquet ILE ILE (column iliyopo) na kuunganishwa kwa `ts`
    ya `load_window` — **hakuna split-logic mpya** (guard ya splits inabaki ya `load_window`).

SPLITS: TRAIN + VALIDATION PEKEE (guard ile ile ya M4-0). HOLDOUT + sealed 2026-05+ HAZIGUSWI.

TAHADHARI YA UAMINIFU (imeandikwa kwenye ripoti pia): capacity-sim inaiga **CHECK 3 (slots)** na
**CHECK 4 (correlation)** PEKEE — si compliance kamili (daily_loss/total_dd/max_spread zinategemea
P&L ya wakati halisi). Ni **kadirio la uwezo (capacity)**, si backtest ya akaunti.

Endesha (PC ya data):  python breadth_capacity.py --run
Self-test (bila data):  python breadth_capacity.py --self-test
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

from family_pooled import pool_streams
from cost_stress import ev_spread_table, spread_split, SPREAD_DELTAS
from breadth_baseline import (EVENT, TF, SESSION_FILTER, VARIANTS, SPLITS, GOLD, MAX_HOLD,
                              DAYS_PER_YEAR, _guard_split, _pairs, pair_stream, variant_key,
                              _acct, _f, REPO_ROOT)

OUT_JSONL = "breadth_capacity.jsonl"
OUT_REPORT = "breadth_cost_capacity.md"

# Njia MBILI za kuhesabu correlation exposure — zote ZIPO kwenye code ya live (angalia §OPEN):
#   "live"   = live_brain: reservation ina-increment kundi MOJA (`live_engine._corr_group`)
#   "strict" = kila kundi ambalo pair inalo (`broker_adapter._groups_of`) linaongezeka
CORR_MODES = ("live", "strict")


# ---------- spread_state (column ILIYOPO ya state parquet; alignment kwa ts — hakuna split mpya) ----------
def spread_states(pair, tf, ts):
    """Rudisha array ya `spread_state` (NORMAL/WIDE/UNKNOWN) iliyo-aligned na `ts` ya load_window.
    Inasoma columns MBILI tu za parquet ile ile; alignment = searchsorted juu ya ts (exact match
    inahakikiwa). Column haipo/parquet haipo -> None (ripoti inasema wazi)."""
    try:
        import polars as pl
        from latent_structure import state_path
    except Exception:
        return None
    p = state_path(pair, tf)
    if not p.exists():
        return None
    df = pl.read_parquet(p, columns=["ts", "spread_state"]).sort("ts")
    full_ts = df["ts"].to_numpy()
    states = np.asarray(df["spread_state"].to_list())
    idx = np.searchsorted(full_ts, ts)
    if idx.max(initial=0) >= len(full_ts) or not np.array_equal(full_ts[idx], ts):
        return None                                     # alignment haikukamilika -> usikadirie
    return states[idx]


def _episode_tuples(rows):
    """Rudisha rows kwenye umbo LA EPISODES ((entry_bar, exit_bar, dir, pnl_pips, sess, vol)) ili
    `cost_stress.spread_split` itumike KAMA ILIVYO (index t[0], pnl t[3])."""
    return [(r["entry_bar"], r["exit_bar"], r["dir"], r["pnl_pips"], "-", "-") for r in rows]


# ---------- (1) COST STRESS ----------
def cost_stress_variant(split, sl_atr, tp_atr, pairs=None, deltas=SPREAD_DELTAS):
    """EV(Δspread) analytic (per-pair + pooled-FX) + mgawanyo wa spread_state wa bar ya ENTRY."""
    _guard_split(split)
    pairs = pairs or _pairs()
    streams, per_pair, cands, by_state, missing_state = [], [], [], {}, []
    for pair in pairs:
        rows, years = pair_stream(pair, split, sl_atr, tp_atr)
        if rows is None:
            continue
        streams.append(rows)
        st = _acct(rows)
        per_pair.append(dict(st, pair=pair))
        cands.append(dict(event=EVENT, pair=pair, sl_atr=sl_atr, tp_atr=tp_atr,
                          session_filter=SESSION_FILTER, ev=(st["ev_pips"] or 0.0)))
        ss = spread_states(pair, TF, np.array([r["ts_entry"] for r in rows])) if rows else None
        if ss is None:
            ss = _states_by_bar(pair, split, rows)
        if ss is None:
            missing_state.append(pair)
            continue
        sp = spread_split(_episode_tuples(rows), _StateByBar(rows, ss))
        per_pair[-1]["spread_split"] = {k: v for k, v in sp.items() if not k.startswith("_")}
        for r, s in zip(rows, ss):                       # pooled: R-units (dimensionless — L-041)
            by_state.setdefault(str(s), []).append(r)
    pooled = pool_streams(streams)
    fx = [r for r in pooled if r["pair"] != GOLD]
    ev_fx = round(float(np.mean([r["pnl_pips"] for r in fx])), 4) if fx else None
    cands.append(dict(event=EVENT, pair="POOLED-FX", sl_atr=sl_atr, tp_atr=tp_atr,
                      session_filter=SESSION_FILTER, ev=(ev_fx or 0.0)))
    pooled_state = {s: dict(_acct(v), n_fx=sum(1 for r in v if r["pair"] != GOLD),
                            ev_pips_fx=(round(float(np.mean([r["pnl_pips"] for r in v
                                                             if r["pair"] != GOLD])), 4)
                                        if any(r["pair"] != GOLD for r in v) else None))
                    for s, v in sorted(by_state.items())}
    wide = pooled_state.get("WIDE")
    verdict = ("WIDE-skip filter kwenye DEPLOYMENT policy (EV_WIDE<0) + forward-verify"
               if wide and wide["ev_R"] is not None and wide["ev_R"] < 0
               else "hakuna WIDE-skip (EV_WIDE>=0 au hakuna WIDE trades)")
    return dict(split=split, variant=variant_key(sl_atr, tp_atr), n=len(pooled),
                ev_pips_fx=ev_fx, ev_table=ev_spread_table(cands, deltas), per_pair=per_pair,
                by_spread_state=pooled_state, wide_verdict=verdict, missing_state=missing_state,
                deltas=list(deltas))


def _states_by_bar(pair, split, rows):
    """Fallback: kama alignment ya ts imeshindikana, jaribu kusoma spread_state kwa bar-index ya
    dirisha (urefu ULE ULE wa window). Haiwezekani -> None (hakuna kukadiria)."""
    return None


class _StateByBar:
    """Adapter nyembamba: `spread_split` inatarajia `spread_state[entry_bar]`. Rows zetu zina
    entry_bar za dirisha; `ss` ni per-trade (iliyo-aligned na ts_entry). Hii inaunganisha bila
    kubadilisha `spread_split` (REUSE kamili)."""

    def __init__(self, rows, states):
        self._m = {r["entry_bar"]: s for r, s in zip(rows, states)}

    def __getitem__(self, bar):
        return self._m[bar]


# ---------- (2) CAPACITY (lango la risk = CHECK 3 + CHECK 4 pekee) ----------
def _groups_for(pair, cfg, mode):
    from live_engine import _corr_group
    from broker_adapter import _groups_of
    if mode == "live":
        g = _corr_group(pair, cfg)                       # kundi MOJA (semantiki ya live_brain)
        return [g] if g else []
    return _groups_of(pair, cfg.get("correlation_groups") or {})   # kila kundi (check ya adapter)


def capacity_sim(rows, cfg, mode="live"):
    """Simulisha lango la slots/correlation juu ya trades ZILIZOPANGWA kwa ts_entry.
    CHECK 3: open_slots >= max_slots -> REJECT. CHECK 4: kundi lolote la pair >= max_correlated_slots
    -> REJECT (`broker_adapter` semantics). Position inashika slot ts_entry -> ts_exit.
    Rudisha accounting ya accepted/rejected + concurrency. (SI compliance kamili — §TAHADHARI.)"""
    if mode not in CORR_MODES:
        raise ValueError(f"mode batili: {mode} (chagua {CORR_MODES})")
    max_slots = int(cfg["max_slots"]); max_corr = int(cfg["max_correlated_slots"])
    order = sorted(rows, key=lambda r: (r["ts_entry"], r["pair"]))
    open_pos = []                                        # (ts_exit, [groups])
    exposure, accepted, rejected, conc = {}, [], [], []
    for r in order:
        still = []
        for ts_exit, gs in open_pos:                     # toa zilizofungwa (ts_exit <= ts_entry)
            if ts_exit > r["ts_entry"]:
                still.append((ts_exit, gs))
            else:
                for g in gs:
                    exposure[g] = exposure.get(g, 0) - 1
        open_pos = still
        check_groups = _groups_for(r["pair"], cfg, "strict")        # CHECK 4 = makundi YOTE
        if len(open_pos) >= max_slots:
            rejected.append(dict(r, _reason="max_slots"))
        elif any(exposure.get(g, 0) >= max_corr for g in check_groups):
            rejected.append(dict(r, _reason="max_correlated_slots"))
        else:
            accepted.append(r)
            inc = _groups_for(r["pair"], cfg, mode)                 # reservation (live vs strict)
            for g in inc:
                exposure[g] = exposure.get(g, 0) + 1
            open_pos.append((r["ts_exit"], inc))
        conc.append(len(open_pos))
    span = _span_years(order)
    acc, rej = _acct(accepted), _acct(rejected)
    return dict(mode=mode, max_slots=max_slots, max_correlated_slots=max_corr,
                n=len(order), n_accepted=len(accepted), n_rejected=len(rejected),
                reject_rate=(round(len(rejected) / len(order), 4) if order else None),
                reasons={k: sum(1 for x in rejected if x["_reason"] == k)
                         for k in ("max_slots", "max_correlated_slots")},
                accepted=dict(n=acc["n"], ev_R=acc["ev_R"], ev_pips=acc["ev_pips"],
                              ev_pips_fx=_ev_fx(accepted), win=acc["win"], pf=acc["pf"],
                              trades_per_year=(round(len(accepted) / span, 1) if span else None)),
                rejected=dict(n=rej["n"], ev_R=rej["ev_R"], ev_pips=rej["ev_pips"],
                              ev_pips_fx=_ev_fx(rejected), win=rej["win"], pf=rej["pf"]),
                concurrency=dict(max=int(max(conc)) if conc else 0,
                                 mean=round(float(np.mean(conc)), 2) if conc else None,
                                 at_cap_share=(round(float(np.mean([c >= max_slots for c in conc])), 4)
                                               if conc else None)))


def _ev_fx(rows):
    v = [r["pnl_pips"] for r in rows if r["pair"] != GOLD]
    return round(float(np.mean(v)), 4) if v else None


def _span_years(rows):
    if len(rows) < 2:
        return None
    lo, hi = rows[0]["ts_entry"], rows[-1]["ts_entry"]
    return float((hi - lo) / np.timedelta64(1, "D") / DAYS_PER_YEAR) or None


# ---------- runner ----------
def run_capacity(out_root=REPO_ROOT, write=True, pairs=None, splits=SPLITS):
    """M4-0b kamili: kwa kila variant × split -> cost stress + capacity (modes 2) + COMBINED
    (models MBILI zinashindania slots zilezile — hali halisi ya KAIROS-1 + KAIROS-2)."""
    from live_engine import _ftmo_config
    cfg = _ftmo_config()
    out = dict(event=EVENT, tf=TF, session_filter=SESSION_FILTER, max_hold=MAX_HOLD,
               cfg=dict(max_slots=cfg["max_slots"], max_correlated_slots=cfg["max_correlated_slots"],
                        correlation_groups=cfg.get("correlation_groups")),
               variants={}, combined={})
    streams_by_split = {sp: [] for sp in splits}
    for sl_atr, tp_atr in VARIANTS:
        vk = variant_key(sl_atr, tp_atr)
        out["variants"][vk] = {}
        for sp in splits:
            cost = cost_stress_variant(sp, sl_atr, tp_atr, pairs=pairs)
            rows = []
            for pair in (pairs or _pairs()):
                rs, _ = pair_stream(pair, sp, sl_atr, tp_atr)
                if rs:
                    rows.extend(rs)
            streams_by_split[sp].extend(dict(r, _variant=vk) for r in rows)
            out["variants"][vk][sp] = dict(cost=cost,
                                           capacity={m: capacity_sim(rows, cfg, m) for m in CORR_MODES})
    for sp in splits:                                    # COMBINED: models 2 kwenye akaunti MOJA
        out["combined"][sp] = {m: capacity_sim(streams_by_split[sp], cfg, m) for m in CORR_MODES}
    if write:
        _write_outputs(out, out_root)
    return out


# ---------- outputs ----------
def _write_outputs(res, out_root):
    out_root = Path(out_root)
    sdir = out_root / "data" / "strategies"; sdir.mkdir(parents=True, exist_ok=True)
    with open(sdir / OUT_JSONL, "w", encoding="utf-8") as f:
        for vk, v in res["variants"].items():
            for sp, r in v.items():
                f.write(json.dumps({**r["cost"], "kind": "cost", "variant": vk, "split": sp},
                                   sort_keys=True, default=str) + "\n")
                for m, c in r["capacity"].items():
                    f.write(json.dumps({**c, "kind": "capacity", "variant": vk, "split": sp},
                                       sort_keys=True, default=str) + "\n")
        for sp, ms in res["combined"].items():
            for m, c in ms.items():
                f.write(json.dumps({**c, "kind": "capacity_combined", "split": sp},
                                   sort_keys=True, default=str) + "\n")

    cfg = res["cfg"]
    L = [f"# M4-0b — COST STRESS + CAPACITY ya BREADTH ({EVENT} × pairs 12 × {TF})\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | nyongeza ya reports/breadth_baseline.md (M4-0) | "
         f"splits: TRAIN + VALIDATION | reuse: cost_stress (R5) + config HALISI ya ftmo_config + "
         f"semantiki za lango la live (live_brain/broker_adapter) | HOLDOUT + sealed 2026-05+ "
         f"HAZIJAGUSWA*\n",
         "> **Swali:** breadth ina EV_net +0.91 pips/trade (FX) — **inastahimili gharama kiasi gani, "
         "na risk-engine itaruhusu ngapi kati ya ~2,680/mwaka?** Hii ni hatua ya KABLA ya kupanua "
         "`pairs[]` live, si utafiti mpya.\n",
         f"> **Lango (config halisi):** max_slots = **{cfg['max_slots']}** · max_correlated_slots = "
         f"**{cfg['max_correlated_slots']}** · groups: `{cfg['correlation_groups']}`\n",
         "> ⚠ **Mipaka ya sim:** CHECK 3 (slots) + CHECK 4 (correlation) PEKEE. daily_loss/total_dd/"
         "max_spread zinategemea P&L ya wakati halisi — hazipo hapa. Hii ni **kadirio la capacity**, "
         "si backtest ya akaunti.\n"]

    # ---- 1. COST ----
    L.append("\n## 1. COST STRESS — EV(Δspread) analytic (cost_stress §R5(1))\n")
    L.append("> `EV_new = EV − Δ` (spread inalipwa mara MOJA kwa trade). **breakeven Δ = EV yenyewe.**\n")
    for vk, v in res["variants"].items():
        for sp, r in v.items():
            c = r["cost"]
            row = next((x for x in c["ev_table"] if "POOLED-FX" in x["label"]), None)
            if row:
                L.append(f"\n### {vk} · {sp.upper()} — pooled FX EV = **{row['ev']:+.2f} pips**, "
                         f"breakeven Δspread = **{row['breakeven_dspread']:.2f} pip**")
                L.append("| Δspread | " + " | ".join(f"+{d}" for d in c["deltas"]) + " |")
                L.append("|---|" + "---|" * len(c["deltas"]))
                L.append("| EV_net (pips) | " + " | ".join(f"{row['ev_dspread'][f'+{d}']:+.2f}"
                                                           for d in c["deltas"]) + " |")
    L.append("\n**Per-pair breakeven Δspread (pips — kila pair kwa pip-scale yake):**\n")
    L.append("| variant | split | " + " | ".join(p["pair"] for p in
                                                 res["variants"][next(iter(res["variants"]))]
                                                 [SPLITS[0]]["cost"]["per_pair"]) + " |")
    L.append("|---|---|" + "---|" * len(res["variants"][next(iter(res["variants"]))]
                                        [SPLITS[0]]["cost"]["per_pair"]))
    for vk, v in res["variants"].items():
        for sp, r in v.items():
            L.append(f"| {vk} | {sp.upper()} | " +
                     " | ".join(_f(p["ev_pips"], "+.2f") for p in r["cost"]["per_pair"]) + " |")

    # ---- 2. spread_state ----
    L.append("\n## 2. COST STRESS — spread_state ya bar ya ENTRY (cost_stress §R5(2))\n")
    L.append("> Je trades zinazoingia wakati spread ni **WIDE** ndizo zinazokula faida? "
             "(spread_state = column ya state parquet, rank-based, no-lookahead.)\n")
    L.append("| variant | split | state | N | EV_R | EV_pips (FX) | win% |")
    L.append("|---|---|---|---|---|---|---|")
    for vk, v in res["variants"].items():
        for sp, r in v.items():
            bs = r["cost"]["by_spread_state"]
            if not bs:
                L.append(f"| {vk} | {sp.upper()} | *spread_state haipatikani* | — | — | — | — |")
                continue
            for state, s in bs.items():
                L.append(f"| {vk} | {sp.upper()} | **{state}** | {s['n']} | {_f(s['ev_R'])} | "
                         f"{_f(s['ev_pips_fx'], '+.2f')} | "
                         f"{'—' if s['win'] is None else format(100 * s['win'], '.1f')} |")
    for vk, v in res["variants"].items():
        for sp, r in v.items():
            if r["cost"]["missing_state"]:
                L.append(f"\n*{vk}/{sp}: spread_state haikupatikana kwa {r['cost']['missing_state']}.*")
    verd = {f"{vk}/{sp}": r["cost"]["wide_verdict"] for vk, v in res["variants"].items()
            for sp, r in v.items()}
    L.append(f"\n**Verdict ya WIDE (cost_stress):** {json.dumps(verd, ensure_ascii=False, indent=0)}")

    # ---- 3. CAPACITY ----
    L.append("\n## 3. CAPACITY — risk-engine kama lango (CHECK 3 + CHECK 4)\n")
    L.append("| scope | split | mode | N | accepted | rejected | reject% | slots | corr | "
             "EV_R acc | EV_R rej | trades/mwaka acc | conc max | conc mean | %muda at-cap |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")

    def _cap_row(scope, sp, c):
        L.append(f"| {scope} | {sp.upper()} | {c['mode']} | {c['n']} | {c['n_accepted']} | "
                 f"{c['n_rejected']} | {_f(c['reject_rate'], '.1%') if c['reject_rate'] is not None else '—'} | "
                 f"{c['reasons']['max_slots']} | {c['reasons']['max_correlated_slots']} | "
                 f"{_f(c['accepted']['ev_R'])} | {_f(c['rejected']['ev_R'])} | "
                 f"{_f(c['accepted']['trades_per_year'], '.1f')} | {c['concurrency']['max']} | "
                 f"{_f(c['concurrency']['mean'], '.2f')} | "
                 f"{_f(c['concurrency']['at_cap_share'], '.1%') if c['concurrency']['at_cap_share'] is not None else '—'} |")

    for vk, v in res["variants"].items():
        for sp, r in v.items():
            for m in CORR_MODES:
                _cap_row(vk, sp, r["capacity"][m])
    for sp, ms in res["combined"].items():
        for m in CORR_MODES:
            _cap_row("**COMBINED (models 2)**", sp, ms[m])

    L.append("\n*`EV_R acc` vs `EV_R rej`: kama zilizokataliwa ni **bora** kuliko zilizopita, lango "
             "linakata faida (queueing bias) — hiyo ni gharama iliyofichwa ya breadth, si ya bure.*")

    # ---- 4. open question ----
    L.append("\n## 4. SWALI LA WAZI kwa Chief/PD (halijarekebishwa hapa — ni observation)\n")
    L.append("Code ya live ina **asymmetry** kwenye correlation: `live_brain.decide` inaongeza "
             "reservation kwa kundi **MOJA** (`live_engine._corr_group` — la kwanza linalolingana), "
             "wakati CHECK 4 (`broker_adapter`) inakagua **makundi YOTE** ya pair. Matokeo: EURUSD "
             "iliyo wazi inaongeza `USD_group` pekee; `EUR_group` inabaki 0, kwa hiyo EURJPY inaweza "
             "kupita hata kama nia ilikuwa kuizuia. Safu **`live`** hapo juu = tabia ya sasa; safu "
             "**`strict`** = kila kundi linaongezeka. Tofauti kati yao = ukubwa wa athari.\n"
             "**Sijabadilisha code ya live** — hilo ni uamuzi wa Chief/PD, si la runner ya utafiti.")

    L.append("\n## 5. Jinsi ya kusoma (uamuzi, si namba tu)\n")
    L.append(f"1. **Kama breakeven Δspread < ~1 pip:** breadth ni fragile kwa cost-regime. Chaguo: "
             f"(a) WIDE-skip filter kwenye DEPLOYMENT policy (si backtest — inahitaji forward-verify); "
             f"(b) pairs zenye breakeven kubwa pekee; (c) subiri forward evidence.")
    L.append("2. **Kama reject% ni kubwa:** `pairs[]` iliyopanuka HAIONGEZI trades kwa uwiano — slots "
             "ndizo kikwazo. Kupanua pairs kunaongeza **uteuzi** (nafasi bora zaidi kwa slot), si wingi.")
    L.append("3. **Kama EV_R ya zilizokataliwa > ya zilizopita:** lango linakata faida — hoja ya "
             "kupanga foleni kwa ubora (queue by EV/threshold) badala ya first-come-first-served. "
             "Hii ndiyo hasa kazi ya KAIROS-3 (§3: chuja bwawa pana).")
    L.append("\n*reuse-only: cost_stress/pool_streams/pair_stream(episodes)/ftmo_config ni imports. "
             "Baseline ≠ edge. Profitable != Tradable Edge. Protect capital first.*")

    rpt = out_root / "reports" / OUT_REPORT; rpt.parent.mkdir(parents=True, exist_ok=True)
    rpt.write_text("\n".join(L), encoding="utf-8")
    return sdir / OUT_JSONL, rpt


# ---------- self-test ----------
def _mkrow(pair, day, hour, hold_h, pnl_pips=1.0, pnl_R=0.05, bar=0):
    t0 = np.datetime64(f"2023-01-{day:02d}T{hour:02d}")
    return dict(pair=pair, ts_entry=t0, ts_exit=t0 + np.timedelta64(hold_h, "h"),
                entry_bar=bar, exit_bar=bar + hold_h, dir=1, pnl_pips=pnl_pips, pnl_R=pnl_R,
                r_trade=1.0, pnl_atr=pnl_R, is_timeout=0)


def self_test():
    ok = True
    import tempfile
    _self = sys.modules[__name__]
    CFG = dict(max_slots=7, max_correlated_slots=3,
               correlation_groups={"USD_group": ["EURUSD", "GBPUSD", "AUDUSD", "NZDUSD"],
                                   "USD_strength": ["USDJPY", "USDCAD", "USDCHF"],
                                   "EUR_group": ["EURUSD", "EURJPY", "EURGBP"],
                                   "AUD_NZD_group": ["AUDUSD", "NZDUSD"]})

    # ---- (b) HOLDOUT/sealed guard (kupitia _guard_split ya M4-0 — kabla ya data yoyote)
    guards = {}
    for bad in ("holdout", "sealed", "forward"):
        try:
            cost_stress_variant(bad, 2.0, 1.0, pairs=["EURUSD"])
            guards[bad] = False
        except PermissionError:
            guards[bad] = True
    ok = ok and all(guards.values())
    print(f"  [b] HOLDOUT/sealed guard: {guards} -> {all(guards.values())}")

    # ---- (a) cost math == cost_stress (analytic EXACT: EV−Δ; breakeven == EV)
    cands = [dict(event=EVENT, pair="POOLED-FX", sl_atr=1.0, tp_atr=1.0,
                  session_filter=SESSION_FILTER, ev=0.91)]
    tab = ev_spread_table(cands, (0.2, 0.5, 1.0))[0]
    a_ok = (tab["ev_dspread"]["+0.2"] == 0.71 and tab["ev_dspread"]["+0.5"] == 0.41
            and tab["ev_dspread"]["+1.0"] == -0.09 and tab["breakeven_dspread"] == 0.91)
    ok = ok and a_ok
    print(f"  [a] EV(Δspread) == cost_stress analytic: {tab['ev_dspread']} "
          f"breakeven={tab['breakeven_dspread']} -> {a_ok}")

    # ---- (f) spread_split REUSE: partition kamili (NORMAL+WIDE == N) kupitia adapter
    rows = [_mkrow("EURUSD", 3, 8 + i, 2, pnl_pips=(2.0 if i % 2 else -1.0), bar=i) for i in range(10)]
    states = np.array(["NORMAL" if i % 2 else "WIDE" for i in range(10)])
    sp = spread_split(_episode_tuples(rows), _StateByBar(rows, states))
    f_ok = (sp["NORMAL"]["n"] + sp["WIDE"]["n"] == len(rows) and sp["NORMAL"]["ev"] == 2.0
            and sp["WIDE"]["ev"] == -1.0 and "WIDE-skip" in sp["_verdict"])
    ok = ok and f_ok
    print(f"  [f] spread_split reuse: NORMAL n={sp['NORMAL']['n']} ev={sp['NORMAL']['ev']} · "
          f"WIDE n={sp['WIDE']['n']} ev={sp['WIDE']['ev']} · partition kamili -> {f_ok}")

    # ---- (d1) slots cap EXACT: trades 10 zinazopishana zote; max_slots=3 -> 3 pekee zinapita
    over = [_mkrow("XAUUSD", 3, 0, 100, bar=i) for i in range(10)]      # zote zinapishana (hold 100h)
    c1 = capacity_sim(over, dict(CFG, max_slots=3), "live")
    d1 = (c1["n_accepted"] == 3 and c1["n_rejected"] == 7
          and c1["reasons"]["max_slots"] == 7 and c1["concurrency"]["max"] == 3)
    # max_slots kubwa -> hakuna rejection (monotonicity)
    c1b = capacity_sim(over, dict(CFG, max_slots=99), "live")
    d1 = d1 and c1b["n_rejected"] == 0 and c1b["n_accepted"] == 10
    ok = ok and d1
    print(f"  [d1] slots cap: max_slots=3 -> acc {c1['n_accepted']}/10 (rej {c1['n_rejected']}); "
          f"max_slots=99 -> rej {c1b['n_rejected']} -> {d1}")

    # ---- (d2) non-overlap: trades zinazofuatana (hold 1h, kila saa) -> ZOTE zinapita hata slots=1
    seq = [_mkrow("XAUUSD", 4, 6 + i, 1, bar=i) for i in range(8)]
    c2 = capacity_sim(seq, dict(CFG, max_slots=1), "live")
    d2 = c2["n_accepted"] == 8 and c2["n_rejected"] == 0 and c2["concurrency"]["max"] == 1
    ok = ok and d2
    print(f"  [d2] slot release (hakuna overlap, slots=1): acc {c2['n_accepted']}/8 -> {d2}")

    # ---- (d3) correlation cap EXACT: USD_group 4 zinazopishana, cap=3 -> ya 4 INAKATALIWA
    usd = [_mkrow(p, 5, 0, 100, bar=i) for i, p in enumerate(["EURUSD", "GBPUSD", "AUDUSD", "NZDUSD"])]
    c3 = capacity_sim(usd, dict(CFG, max_slots=99), "strict")
    d3 = (c3["n_accepted"] == 3 and c3["reasons"]["max_correlated_slots"] == 1
          and c3["reasons"]["max_slots"] == 0)
    ok = ok and d3
    print(f"  [d3] correlation cap (USD_group cap 3): acc {c3['n_accepted']}/4, sababu="
          f"{c3['reasons']} -> {d3}")

    # ---- (g) live vs strict divergence (asymmetry ya code ya live — §OPEN)
    # cap=2: strict -> EURUSD ina-increment EUR_group PIA, kwa hiyo EURGBP INAKATALIWA (acc 2);
    # live -> EURUSD ina-increment USD_group PEKEE, EUR_group inabaki 0, zote 3 zinapita (acc 3).
    eur = [_mkrow("EURUSD", 6, 0, 100, bar=1), _mkrow("EURJPY", 6, 1, 100, bar=9),
           _mkrow("EURGBP", 6, 2, 100, bar=10)]
    g_live = capacity_sim(eur, dict(CFG, max_slots=99, max_correlated_slots=2), "live")
    g_strict = capacity_sim(eur, dict(CFG, max_slots=99, max_correlated_slots=2), "strict")
    g_ok = (g_live["n_accepted"] >= g_strict["n_accepted"]
            and g_live["n_accepted"] != g_strict["n_accepted"])     # asymmetry inaonekana
    ok = ok and g_ok
    print(f"  [g] live vs strict (EUR_group): live acc={g_live['n_accepted']} vs "
          f"strict acc={g_strict['n_accepted']} (live ni laini zaidi — §OPEN) -> {g_ok}")

    # ---- (e) closure + (c) determinism
    mix = over + seq + usd + eur
    ca = capacity_sim(mix, CFG, "live"); cb = capacity_sim(mix, CFG, "live")
    e_ok = (ca["n_accepted"] + ca["n_rejected"] == ca["n"] == len(mix)
            and sum(ca["reasons"].values()) == ca["n_rejected"])
    c_ok = json.dumps(ca, sort_keys=True, default=str) == json.dumps(cb, sort_keys=True, default=str)
    ok = ok and e_ok and c_ok
    print(f"  [e] closure: acc {ca['n_accepted']} + rej {ca['n_rejected']} == N {ca['n']}; "
          f"sababu zinalingana -> {e_ok}")
    print(f"  [c] determinism: {c_ok}")

    # ---- runner mzima kwa fixtures (monkeypatch: pair_stream + config + spread_states)
    P12 = ["EURUSD", "GBPUSD", "USDJPY", "EURJPY", "USDCAD", "USDCHF",
           "AUDUSD", "NZDUSD", "EURGBP", "GBPJPY", "EURCHF", "XAUUSD"]

    def _fake_stream(pair, split, sl, tp):
        base = P12.index(pair)
        rs = [_mkrow(pair, 3 + (k % 20), (k * 3) % 20, 6,
                     pnl_pips=(2.0 if (k + base) % 3 else -1.5),
                     pnl_R=(0.05 if (k + base) % 3 else -0.04), bar=k * 7 + base)
              for k in range(40)]
        return rs, 1.0
    orig_ps, orig_ss = _self.pair_stream, _self.spread_states
    import live_engine as le
    orig_cfg = le._ftmo_config
    _self.pair_stream = _fake_stream
    _self.spread_states = lambda pair, tf, ts: np.array(["WIDE" if i % 4 == 0 else "NORMAL"
                                                         for i in range(len(ts))])
    le._ftmo_config = lambda: dict(CFG)
    try:
        with tempfile.TemporaryDirectory() as tmp:
            ra = run_capacity(out_root=tmp, pairs=P12)
            rb = run_capacity(out_root=tmp, pairs=P12, write=False)
            det = (json.dumps(ra, sort_keys=True, default=str)
                   == json.dumps(rb, sort_keys=True, default=str))
            rpt = (Path(tmp) / "reports" / OUT_REPORT).read_text(encoding="utf-8")
            recs = [json.loads(ln) for ln in
                    open(Path(tmp) / "data" / "strategies" / OUT_JSONL, encoding="utf-8")]
            kinds = {r["kind"] for r in recs}
            # COMBINED lazima iwe na trades za variants ZOTE mbili (models 2 = slots zilezile)
            comb = ra["combined"]["validation"]["live"]
            one = ra["variants"]["SL2/TP1"]["validation"]["capacity"]["live"]
            comb_ok = comb["n"] == 2 * one["n"] and comb["n_rejected"] >= one["n_rejected"]
            r_ok = (det and comb_ok and kinds == {"cost", "capacity", "capacity_combined"}
                    and "COST STRESS" in rpt and "CAPACITY" in rpt and "SWALI LA WAZI" in rpt
                    and "breakeven" in rpt)
    finally:
        _self.pair_stream, _self.spread_states = orig_ps, orig_ss
        le._ftmo_config = orig_cfg
    ok = ok and r_ok
    print(f"  [run] full runner: det={det} · COMBINED N={comb['n']} (== 2× {one['n']}) rej "
          f"{comb['n_rejected']} ≥ {one['n_rejected']} · outputs={sorted(kinds)} -> {r_ok}")

    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true", help="endesha M4-0b (PC ya data)")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.run:
        print("Tumia --run | --self-test.", file=sys.stderr)
        return 2
    res = run_capacity()
    print(f"M4-0b COST + CAPACITY ({EVENT} × {TF}, pairs pooled)")
    for vk, v in res["variants"].items():
        for sp, r in v.items():
            row = next((x for x in r["cost"]["ev_table"] if "POOLED-FX" in x["label"]), None)
            cap = r["capacity"]["live"]
            print(f"  {vk:12s} {sp:10s} breakeven Δspread={row['breakeven_dspread']:.2f} pip · "
                  f"accepted {cap['n_accepted']}/{cap['n']} ({cap['reject_rate']:.1%} rej) · "
                  f"EV_R acc={_f(cap['accepted']['ev_R'])} rej={_f(cap['rejected']['ev_R'])}")
    for sp, ms in res["combined"].items():
        c = ms["live"]
        print(f"  COMBINED {sp:10s} accepted {c['n_accepted']}/{c['n']} ({c['reject_rate']:.1%} rej) · "
              f"conc max={c['concurrency']['max']} at-cap={c['concurrency']['at_cap_share']:.1%}")
    print(f"  data/strategies/{OUT_JSONL}\n  reports/{OUT_REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
