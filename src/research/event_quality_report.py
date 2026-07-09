"""
event_quality_report.py — Ubora wa ENTRIES: V1 (conditions) vs V2 (episodes). Chief direct.

MCHAKATO (harness MOJA ya haki kwa wote):
  * Episode = position MOJA kwa event x pair (hakuna overlap — fires wakati position
    iko wazi zinarukwa). Hii inaondoa D1 ya Phase 12 (sampuli 351k zinazo-overlap).
  * Entry HONEST ya "next bar": market = OPEN ya bar ijayo; stop = touch ya bar ijayo
    (entry = max(level, open) kwa long — gap-honest).
  * Exit = SL/TP za ATR (default 1.5 ATR / 1.5 ATR) au timeout (24 bars -> close).
    Tie bar (SL na TP ndani ya bar moja) -> SL kwanza (WORST CASE, conservative).
  * COSTS kila trade: spread halisi ya bar ya entry (spr) + slippage (market 0.1 pip,
    stop 0.3 pip). HAKUNA metric bila costs (RED LINE ya S1).
  * SACRED SPLITS: bars za ts >= 2023-01-01 zinaKATWA daima — TRAIN 2016-2022 TU.
    VALIDATION/HOLDOUT hazisomwi na script hii kabisa.

HII NI EXPLORATION (inalisha grid ya S1) — SIO edge claim. Kila namba hapa ni
in-sample TRAIN; uthibitisho = S2 (walk-forward + FDR) na S3 (holdout, mara moja).
LESSON-001/002/029 zinabaki sheria.

Endesha (PC ya data):  python event_quality_report.py            (pairs zote, H1)
                       python event_quality_report.py --tf H4
Output: reports/event_quality_report.md
Self-test (bila data):  python event_quality_report.py --self-test
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

from event_library import EVENTS_ALL
from event_library_v2 import EVENTS_V2, _synthetic

REPO_ROOT = Path(__file__).resolve().parents[2]
TRAIN_END = datetime(2023, 1, 1)     # sacred splits: TRAIN < 2023-01-01 (V+H hazisomwi)
SL_ATR, TP_ATR = 1.5, 1.5            # exit structure ya msingi (S1 ita-grid hizi)
MAX_HOLD = 24                        # timeout (bars)
SLIP_MARKET, SLIP_STOP = 0.1, 0.3    # pips
MIN_N = 30                           # sample ya chini kuripoti row
SESSIONS = (("ASIA", 0, 6), ("LONDON", 7, 11), ("NY", 12, 16), ("LATE", 17, 23))


def _sess(hr):
    for nm, a, b in SESSIONS:
        if a <= hr <= b:
            return nm
    return "LATE"


def _exit_variant(cfg, d, e, a, sl_px, tp_px, h, l, c, i, j_end):
    """Cycle-2 EXIT SCIENCE (H-C2-6): trailing (k×ATR) / breakeven (baada ya +rR) / time (bars).
    Inarudisha (exit_px, exit_bar). Convention ya intrabar = sawa na default (SL/trailing KABLA ya
    TP; tie -> stop). EXPLORATION — default (exit_cfg=None) HAITUMII hii (byte-identical inabaki)."""
    mode = cfg["mode"]
    if mode == "trailing":
        k = cfg.get("k", 1.0); trail = sl_px; best = e
        for j in range(i + 1, j_end + 1):
            best = max(best, h[j]) if d == 1 else min(best, l[j])
            cand = best - d * k * a
            trail = max(trail, cand) if d == 1 else min(trail, cand)
            if (l[j] <= trail) if d == 1 else (h[j] >= trail):
                return trail, j
            if (h[j] >= tp_px) if d == 1 else (l[j] <= tp_px):
                return tp_px, j
        return c[j_end], j_end
    if mode == "breakeven":
        r = cfg.get("r", 1.0); R = abs(e - sl_px); sl_cur = sl_px; moved = False
        for j in range(i + 1, j_end + 1):
            if not moved and ((h[j] >= e + r * R) if d == 1 else (l[j] <= e - r * R)):
                sl_cur = e; moved = True                  # sogeza SL -> entry (breakeven)
            if (l[j] <= sl_cur) if d == 1 else (h[j] >= sl_cur):
                return sl_cur, j
            if (h[j] >= tp_px) if d == 1 else (l[j] <= tp_px):
                return tp_px, j
        return c[j_end], j_end
    if mode == "time":
        end = min(i + cfg.get("bars", j_end - i), j_end)
        for j in range(i + 1, end + 1):
            if (l[j] <= sl_px) if d == 1 else (h[j] >= sl_px):
                return sl_px, j
            if (h[j] >= tp_px) if d == 1 else (l[j] <= tp_px):
                return tp_px, j
        return c[end], end
    raise ValueError(f"exit mode batili: {mode}")


def episodes(out, entry, o, h, l, c, atr, spr, hour, vol=None,
             sl_atr=SL_ATR, tp_atr=TP_ATR, max_hold=MAX_HOLD, exit_cfg=None):
    """Simulisha episodes za event moja. Inarudisha list ya
    (entry_bar, exit_bar, dir, pnl_pips_net, session, vol_state). NO-LOOKAHEAD:
    signal ya bar i -> entry bar i+1; SL/TP zinachunguzwa kuanzia bar ya entry.
    vol = volatility_state ya kila bar (uchambuzi wa soko — market_state_engine).
    exit_cfg (Cycle-2): None = default fixed-exit (BYTE-IDENTICAL); au {"mode": trailing/breakeven/time,...}."""
    n = len(c); trades = []; pos_end = -1
    sig = out.get("sig")
    LL = out.get("long_level"); SS = out.get("short_level")
    for i in range(n - 1):
        if i <= pos_end:
            continue
        d = 0
        if entry == "market":
            if sig[i] == 0:
                continue
            d = int(sig[i]); e = o[i + 1]; cost = spr[i + 1] + SLIP_MARKET
        else:
            ll = LL[i]; ss = SS[i]
            long_hit = np.isfinite(ll) and h[i + 1] >= ll
            short_hit = np.isfinite(ss) and l[i + 1] <= ss
            if long_hit and short_hit:      # OCO ambiguous ndani ya bar moja -> ruka (conservative)
                continue
            if long_hit:
                d = 1; e = max(ll, o[i + 1])
            elif short_hit:
                d = -1; e = min(ss, o[i + 1])
            else:
                continue
            cost = spr[i + 1] + SLIP_STOP
        a = atr[i]
        if not (a > 0):
            continue
        sl_px = e - d * sl_atr * a
        tp_px = e + d * tp_atr * a
        j_end = min(i + 1 + max_hold, n - 1)
        if exit_cfg is None:
            # === DEFAULT fixed-exit (BYTE-IDENTICAL; Cycle-2 exit science HAIGUSI path hii) ===
            exit_px = None; j = j_end
            for j in range(i + 1, j_end + 1):
                hit_sl = (l[j] <= sl_px) if d == 1 else (h[j] >= sl_px)
                hit_tp = (h[j] >= tp_px) if d == 1 else (l[j] <= tp_px)
                if hit_sl:                       # tie -> SL kwanza (worst case)
                    exit_px = sl_px; break
                if hit_tp:
                    exit_px = tp_px; break
            if exit_px is None:
                exit_px = c[j_end]; j = j_end
        else:
            exit_px, j = _exit_variant(exit_cfg, d, e, a, sl_px, tp_px, h, l, c, i, j_end)
        pnl = d * (exit_px - e) - cost
        # vol state ya bar ya SIGNAL (i) — inajulikana wakati wa uamuzi (EP-5 decidability);
        # state ya bar ya entry (i+1) haijulikani hadi bar hiyo ifunge. Session = saa ya entry
        # (ratiba inajulikana ex-ante, si data ya bei).
        vs = str(vol[i]) if vol is not None else "-"
        trades.append((i + 1, j, d, float(pnl), _sess(int(hour[i + 1])), vs))
        pos_end = j
    return trades


def _metrics(pnls):
    p = np.asarray(pnls, float); n = len(p)
    if n == 0:
        return dict(n=0)
    wins = p[p > 0]; losses = p[p <= 0]
    pf = float(wins.sum() / abs(losses.sum())) if losses.sum() < 0 else float("inf")
    return dict(n=n, ev=float(p.mean()), win=float((p > 0).mean()), pf=pf)


def _v1_adapter(fn):
    """V1 signature: fn(close, high, low) -> sig. Funga kwenye API ya V2."""
    return lambda o, h, l, c, tc=None, hour=None: {"sig": fn(c, h, l)}


def all_events():
    """(name, fn, entry, family) kwa V1 (baseline) + V2 — harness ileile kwa wote."""
    evs = []
    for nm, fn in EVENTS_ALL.items():
        evs.append((f"v1:{nm}", _v1_adapter(fn), "market", "V1"))
    for nm, spec in EVENTS_V2.items():
        evs.append((f"v2:{nm}", spec["fn"], spec["entry"], "V2"))
    return evs


def load_pair(sym, tf):
    """Soma state parquet, KATA TRAIN, rudisha arrays (pips). None kama haipo."""
    import polars as pl
    from market_state_engine import pip
    from latent_structure import state_path
    p = state_path(sym, tf)
    if not p.exists():
        return None
    df = pl.read_parquet(p).sort("ts")
    df = df.filter(pl.col("ts") < TRAIN_END)          # sacred splits — daima
    if df.height < 500:
        return None
    pp = pip(sym)
    return dict(
        o=df["o"].to_numpy() / pp, h=df["h"].to_numpy() / pp,
        l=df["l"].to_numpy() / pp, c=df["c"].to_numpy() / pp,
        atr=df["atr"].to_numpy() / pp,
        spr=np.nan_to_num(df["spr"].to_numpy(), nan=0.0),
        tc=df["tc"].to_numpy().astype(float),
        hour=df["ts"].dt.hour().to_numpy(),
        vol=np.asarray(df["volatility_state"].to_list()),
        days=df["ts"].dt.date().n_unique(),
    )


def run(pairs, tf):
    from market_state_engine import cfg
    c_ = cfg()
    agg = {}          # name -> list pnl
    by_pair = {}      # (name, sym) -> list pnl
    by_sess = {}      # (name, sess) -> list pnl
    by_vol = {}       # (name, vol_state) -> list pnl  (uchambuzi wa soko)
    days_tot = 0; pairs_done = []
    for sym in pairs:
        d = load_pair(sym, tf)
        if d is None:
            print(f"  {sym}: state parquet haipo/fupi — naruka", flush=True)
            continue
        days_tot += d["days"]; pairs_done.append(sym)
        for name, fn, entry, fam in all_events():
            out = fn(d["o"], d["h"], d["l"], d["c"], d["tc"], d["hour"])
            trs = episodes(out, entry, d["o"], d["h"], d["l"], d["c"],
                           d["atr"], d["spr"], d["hour"], d["vol"])
            for (_, _, _, pnl, sess, vs) in trs:
                agg.setdefault(name, []).append(pnl)
                by_pair.setdefault((name, sym), []).append(pnl)
                by_sess.setdefault((name, sess), []).append(pnl)
                by_vol.setdefault((name, vs), []).append(pnl)
        print(f"  {sym}: done ({d['days']} siku za TRAIN)", flush=True)
    if not pairs_done:
        print("HITILAFU: hakuna state parquet. Endesha market_state_engine.py kwanza.", file=sys.stderr)
        return 1

    L = ["# Event Quality — entries V1 (conditions) vs V2 (episodes) — TRAIN TU\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | TF={tf} | pairs={len(pairs_done)} | TRAIN < {TRAIN_END:%Y-%m-%d} "
         f"(sacred splits) | exit SL/TP {SL_ATR}/{TP_ATR} ATR, timeout {MAX_HOLD}b, tie->SL | "
         f"costs = spr halisi + slip (mkt {SLIP_MARKET}/stop {SLIP_STOP}) | episode = position 1 kwa event x pair*\n",
         "> **UAMINIFU (Chief):** hii ni EXPLORATION ya TRAIN inayolisha grid ya S1 — SIO edge claim. "
         "Kila namba ni in-sample; uthibitisho = S2 (walk-forward+FDR) na S3 (holdout, mara moja). "
         "LESSON-001/002/029. Profitable != Tradable Edge.\n"]

    # 1) V1 vs V2 aggregate
    L.append("\n## 1) V1 vs V2 — aggregate (pairs zote)\n")
    L.append("| event | N | trades/siku | EV net (pips) | win% | PF |")
    L.append("|-------|---|-------------|---------------|------|----|")
    for name, _, _, fam in all_events():
        m = _metrics(agg.get(name, []))
        if m["n"] < MIN_N:
            L.append(f"| {name} | <{MIN_N} | — | — | — | — |"); continue
        L.append(f"| {name} | {m['n']:,} | {m['n']/max(days_tot,1):.2f} | {m['ev']:+.3f} | "
                 f"{m['win']*100:.1f} | {m['pf']:.2f} |")

    # 2) V2 per pair (top rows)
    L.append("\n## 2) V2 kwa pair (rows za juu kwa EV, min N=30)\n")
    L.append("| event | pair | N | EV net (pips) | win% | PF |")
    L.append("|-------|------|---|---------------|------|----|")
    rows = []
    for (name, sym), pn in by_pair.items():
        if not name.startswith("v2:"):
            continue
        m = _metrics(pn)
        if m["n"] >= MIN_N:
            rows.append((name, sym, m))
    rows.sort(key=lambda r: r[2]["ev"], reverse=True)
    for name, sym, m in rows[:25]:
        L.append(f"| {name} | {sym} | {m['n']:,} | {m['ev']:+.3f} | {m['win']*100:.1f} | {m['pf']:.2f} |")

    # 3) V2 per session
    L.append("\n## 3) V2 kwa session (EV net pips; entry hour ya server time)\n")
    L.append("| event | " + " | ".join(s[0] for s in SESSIONS) + " |")
    L.append("|-------|" + "|".join(["-----"] * len(SESSIONS)) + "|")
    for name, _, _, fam in all_events():
        if fam != "V2":
            continue
        cells = []
        for snm, _, _ in SESSIONS:
            m = _metrics(by_sess.get((name, snm), []))
            cells.append(f"{m['ev']:+.2f} (n={m['n']})" if m["n"] >= MIN_N else "—")
        L.append(f"| {name} | " + " | ".join(cells) + " |")

    # 4) V2 per volatility state (uchambuzi wa soko: entry ndani ya context)
    L.append("\n## 4) V2 kwa VOLATILITY STATE (uchambuzi wa soko — market_state_engine, "
             "deseasonalized, no-lookahead)\n")
    VOLS = ("LOW", "NORMAL", "HIGH")
    L.append("| event | " + " | ".join(VOLS) + " |")
    L.append("|-------|" + "|".join(["-----"] * len(VOLS)) + "|")
    for name, _, _, fam in all_events():
        if fam != "V2":
            continue
        cells = []
        for vs in VOLS:
            m = _metrics(by_vol.get((name, vs), []))
            cells.append(f"{m['ev']:+.2f} (n={m['n']})" if m["n"] >= MIN_N else "—")
        L.append(f"| {name} | " + " | ".join(cells) + " |")
    L.append("\n-> Cell chanya thabiti = event x state filter ya grid ya S1 (mf. 'mr_zscore "
             "NORMAL tu'). Phase 12 Q4 ilionyesha state-dependence; hapa inapimwa kwa "
             "trade structure halisi.")

    L.append("\n## VERDICT (descriptive tu)\n")
    L.append("- Linganisha jozi v1 vs v2 (mf. v1:pullback vs v2:pullback_v2): D1-fix inaonekana kwenye "
             "trades/siku na EV net.\n- Rows za juu za sehemu 2 + sessions bora za sehemu 3 = grid ya "
             "S1 (strategy_lab). HAKUNA row inayoitwa 'strategy' kabla ya S2 (FDR) + S3 (holdout).\n")
    L.append(f"\n*Harness: episode non-overlap, next-bar honest, costs kila trade, TRAIN<{TRAIN_END:%Y-%m-%d}. "
             "Chief direct. Profitable != Tradable Edge.*")

    out = REPO_ROOT / c_["paths"]["reports"] / "event_quality_report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\nRipoti: {out.relative_to(REPO_ROOT)}")
    return 0


# ---------- self-test (bila data) ----------

def self_test():
    """(1) non-overlap; (2) costs -> EV<0 kwenye noise; (3) determinism;
    (4) stop-fill honesty (crafted bars); (5) TRAIN filter; (6) tie->SL."""
    o, h, l, c, tc, hour = _synthetic(n=5000, seed=1)
    atr = np.maximum(h - l, 0.1); spr = np.full(len(c), 1.0)
    ok = True

    # (1)+(3): market event (mr_zscore) mara mbili -> sawa; hakuna overlap
    from event_library_v2 import mr_zscore, breakout_stop
    t1 = episodes(mr_zscore(o, h, l, c), "market", o, h, l, c, atr, spr, hour)
    t2 = episodes(mr_zscore(o, h, l, c), "market", o, h, l, c, atr, spr, hour)
    det = t1 == t2
    nov = all(t1[k + 1][0] > t1[k][1] for k in range(len(t1) - 1))
    print(f"  determinism={det} non-overlap={nov} (n_trades={len(t1)})")
    ok = ok and det and nov and len(t1) > 5

    # (2) noise random walk + costs -> EV negative (hakuna free lunch kwenye harness)
    rng = np.random.default_rng(7); n = 20000
    rw = np.cumsum(rng.normal(0, 2.0, n)) + 10000
    o2 = np.roll(rw, 1); o2[0] = rw[0]
    sp2 = np.abs(rng.normal(0, 1.0, n))
    h2 = np.maximum(o2, rw) + sp2; l2 = np.minimum(o2, rw) - sp2
    atr2 = np.maximum(h2 - l2, 0.5); spr2 = np.full(n, 1.0); hr2 = np.arange(n) % 24
    tn = episodes(mr_zscore(o2, h2, l2, rw), "market", o2, h2, l2, rw, atr2, spr2, hr2)
    evn = float(np.mean([t[3] for t in tn])) if tn else 0.0
    noise_ok = evn < 0
    print(f"  noise+costs: EV={evn:+.3f} (<0: {noise_ok}, n={len(tn)})")
    ok = ok and noise_ok

    # (4) stop-fill honesty: level haijaguswa -> hakuna trade; ikiguswa -> entry >= level (long)
    o3 = np.array([100.0, 100, 100, 100, 100, 100]); c3 = o3.copy()
    h3 = np.array([101.0, 101, 101, 108, 101, 101]); l3 = np.full(6, 99.0)
    atr3 = np.full(6, 2.0); spr3 = np.zeros(6); hr3 = np.zeros(6, int)
    LL = np.array([np.nan, np.nan, 105.0, np.nan, np.nan, np.nan])   # armed bar 2 -> bar 3 h=108 touch
    SS = np.full(6, np.nan)
    ts_ = episodes({"long_level": LL, "short_level": SS}, "stop", o3, h3, l3, c3, atr3, spr3, hr3)
    fill_ok = len(ts_) == 1 and ts_[0][2] == 1
    LL2 = np.array([np.nan, np.nan, 120.0, np.nan, np.nan, np.nan])  # haiguswi kamwe
    ts2 = episodes({"long_level": LL2, "short_level": SS}, "stop", o3, h3, l3, c3, atr3, spr3, hr3)
    nofill_ok = len(ts2) == 0
    print(f"  stop-fill: touch->trade={fill_ok} no-touch->no-trade={nofill_ok}")
    ok = ok and fill_ok and nofill_ok

    # (6) tie bar (SL na TP zote ndani ya bar) -> SL (worst case)
    o4 = np.array([100.0, 100, 100.0, 100]); c4 = o4.copy()
    h4 = np.array([100.5, 100.5, 110.0, 100.5]); l4 = np.array([99.5, 99.5, 90.0, 99.5])
    atr4 = np.full(4, 2.0); spr4 = np.zeros(4); hr4 = np.zeros(4, int)
    sig4 = np.array([0, 1, 0, 0])
    t4 = episodes({"sig": sig4}, "market", o4, h4, l4, c4, atr4, spr4, hr4)
    tie_ok = len(t4) == 1 and t4[0][3] < 0
    print(f"  tie->SL worst-case: {tie_ok} (pnl={t4[0][3]:+.2f})" if t4 else "  tie: HAKUNA trade (FAIL)")
    ok = ok and tie_ok

    # (5) TRAIN filter (polars, bila data halisi)
    import polars as pl
    df = pl.DataFrame({"ts": [datetime(2022, 12, 30), datetime(2023, 6, 1)], "x": [1, 2]})
    cut = df.filter(pl.col("ts") < TRAIN_END)
    train_ok = cut.height == 1 and cut["ts"].max() < TRAIN_END
    print(f"  TRAIN filter: {train_ok}")
    ok = ok and train_ok

    # (7) Cycle-2 EXIT SCIENCE: default BYTE-IDENTICAL (golden hashes zilizonaswa kabla ya mabadiliko);
    # variants (trailing/breakeven/time) zinaendesha + zinatoa matokeo halali.
    import hashlib
    from event_library_v2 import mr_zscore, nr7_break
    o5, h5, l5, c5, tc5, hr5 = _synthetic(n=5000, seed=1)
    atr5 = np.maximum(h5 - l5, 0.1); spr5 = np.full(len(c5), 1.0); vol5 = np.array(["NORMAL"] * len(c5))
    def _gh(trs):
        return hashlib.sha1(repr(trs).encode()).hexdigest()[:16]
    gm = _gh(episodes(mr_zscore(o5, h5, l5, c5), "market", o5, h5, l5, c5, atr5, spr5, hr5, vol5))
    gs = _gh(episodes(nr7_break(o5, h5, l5, c5), "stop", o5, h5, l5, c5, atr5, spr5, hr5, vol5,
                      sl_atr=2.0, tp_atr=1.0))
    byte_id = gm == "28cc2218e7d1c43f" and gs == "872edc444171653e"
    base = mr_zscore(o5, h5, l5, c5)
    tr_tr = episodes(base, "market", o5, h5, l5, c5, atr5, spr5, hr5, vol5, exit_cfg={"mode": "trailing", "k": 1.0})
    tr_be = episodes(base, "market", o5, h5, l5, c5, atr5, spr5, hr5, vol5, exit_cfg={"mode": "breakeven", "r": 1.0})
    tr_ti = episodes(base, "market", o5, h5, l5, c5, atr5, spr5, hr5, vol5, exit_cfg={"mode": "time", "bars": 6})
    variants_ok = len(tr_tr) > 0 and len(tr_be) > 0 and len(tr_ti) > 0
    print(f"  exit-science: default BYTE-IDENTICAL={byte_id} (mr={gm} nr7={gs}); variants tr/be/time run={variants_ok}")
    ok = ok and byte_id and variants_ok

    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default=None)
    ap.add_argument("--tf", default="H1")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    from market_state_engine import cfg
    pairs = [a.symbol] if a.symbol else cfg()["pairs"]
    return run(pairs, a.tf)


if __name__ == "__main__":
    raise SystemExit(main())
