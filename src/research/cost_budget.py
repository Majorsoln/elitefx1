"""
cost_budget.py — BAJETI YA GHARAMA kwa kila strategy (broker-agnostic).

TATIZO (PD 2026-08-01): "sina commission/swap halisi kwa sababu hii itatumika na **broker tofauti
tofauti**." Sahihi kabisa — na ndiyo maana kufunga commission ya broker mmoja kwenye research
kungekuwa kosa. Suluhisho ni kugeuza swali:

  BADALA YA: "EV yetu ni ngapi kwa gharama za broker X?"   (inahitaji broker maalum)
  TUNAULIZA: "**Strategy hii inaweza kubeba gharama ya ziada kiasi gani kabla haijafa?**"
             (namba MOJA, isiyotegemea broker — kisha broker YEYOTE anapimwa dhidi yake)

Namba hiyo = **COST BUDGET**. Hesabu ni ya cost_stress §R5(1), ambayo tayari ni doctrine:
`EV_new = EV − Δ` (gharama inalipwa mara moja kwa trade) -> **breakeven Δ = EV yenyewe**.

Kwa hiyo bajeti ni EV iliyothibitishwa; na kizingiti cha kweli si kufikia sifuri bali:
  · **SURVIVES**  : EV_after > 0                      (haijafa)
  · **TRADABLE**  : EV_after ≥ ratio_min × cost_total  (doctrine charter §4.4: edge ~3-4× cost)
  · **KAIROS-3 bar**: EV_after ≥ 3.0 pips             (KAIROS_3_SPEC §5.2 — kwa mgombea mpya)

Gharama za broker zinaingia kama **profiles** (`config/broker_costs.yaml` — PD anahariri, hakuna
code): commission (USD/lot round-turn -> pips) + swap (pips/usiku × wastani wa usiku kwa TF).

MUHIMU: hakuna backtest inayoendeshwa upya hapa. `EV_new = EV − Δ` ni **analytic exact** kwa
gharama inayolipwa mara moja kwa trade — ndiyo maana hii ni hesabu, si makadirio ya simulation.

PURE: numpy/yaml pekee; hakuna data ya soko. Self-test: python cost_budget.py --self-test
Ripoti:  python cost_budget.py --report
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CFG = REPO_ROOT / "config" / "broker_costs.yaml"
OUT_REPORT = "cost_budget.md"

# ---------- REGISTRY ya EV zilizothibitishwa (provenance kwa kila namba — hakuna kubuni) ----------
# EV = pips/trade NET ya spread+slippage (gharama zilizomo kwenye research), SI ya commission/swap.
STRATEGIES = {
    "KAIROS-1 (STRAT-001)": dict(ev=1.92, entry="stop_entry", tf="H1", status="PROVEN",
                                 src="HOLDOUT one-shot S3, N=303, p=0.021 — docs/STRATEGIES.md"),
    "KAIROS-2 (STRAT-002)": dict(ev=2.65, entry="stop_entry", tf="H1", status="PROVEN",
                                 src="HOLDOUT one-shot S3b, N=327, p=0.029 — docs/STRATEGIES.md"),
    "breadth pairs-12 (SL1/TP1)": dict(ev=0.91, entry="stop_entry", tf="H1", status="BASELINE",
                                       src="M4-0 pooled VALIDATION FX, N=4934 — reports/breadth_baseline.md"),
    "breadth pairs-9 (SL2/TP1)": dict(ev=1.58, entry="stop_entry", tf="H1", status="BASELINE*",
                                      src="M4-0b --recommended VALIDATION — *selection-hot (kanuni ilitumia VALID)"),
    "breadth pairs-8 (SL1/TP1)": dict(ev=1.78, entry="stop_entry", tf="H1", status="BASELINE*",
                                      src="M4-0b --recommended VALIDATION — *selection-hot"),
}

RATIO_MIN = 3.0          # charter §4.4: edge lazima iwe ~3-4× cost
KAIROS3_BAR = 3.0        # KAIROS_3_SPEC §5.2 (pips/trade) — kwa mgombea MPYA


def load_cfg(path=CFG):
    import yaml
    return yaml.safe_load(open(path, encoding="utf-8"))


def profile_cost(profile, cfg, tf="H1", nights=None):
    """Gharama ya ZIADA (pips/trade) ya profile: commission (USD/lot -> pips) + swap (nights × rate).
    Rudisha dict yenye vipande vyake (uwazi — si namba moja isiyoeleweka)."""
    pv = float(cfg.get("pip_value_per_lot_usd", 10))
    p = cfg["profiles"][profile]
    comm = float(p.get("commission_usd_round_turn", 0.0)) / pv
    n = float(nights if nights is not None else cfg.get("avg_nights_per_trade", {}).get(tf, 0.0))
    swap = float(p.get("swap_pips_per_night", 0.0)) * n
    return dict(profile=profile, commission_pips=round(comm, 3), nights=n,
                swap_pips=round(swap, 3), extra_total=round(comm + swap, 3),
                note=p.get("note", ""))


def evaluate(ev, extra, base_cost, ratio_min=RATIO_MIN, kairos3_bar=KAIROS3_BAR):
    """Tathmini ya strategy moja chini ya gharama ya ziada `extra`.
    budget = EV (breakeven Δ, cost_stress R5(1)); headroom = budget − extra.

    UWIANO wa doctrine (charter §4.4: "Edge lazima iwe ~3-4x cost") unapimwa kwa **GROSS/cost**, si
    net/cost — mfano wa charter ni "+0.5 pip **gross** na cost 1.5 pips = HASARA". GROSS ni sifa ya
    move yenyewe (haibadiliki na commission): `gross = EV_iliyoripotiwa + base_cost`; commission
    inaongeza `cost_total` pekee. net/cost inaripotiwa pia kwa uwazi."""
    ev_after = ev - extra
    cost_total = base_cost + extra
    gross = ev + base_cost                                   # move halisi kabla ya gharama zozote
    ratio_gross = (gross / cost_total) if cost_total > 0 else float("inf")
    ratio_net = (ev_after / cost_total) if cost_total > 0 else float("inf")
    return dict(ev_before=round(ev, 3), extra=round(extra, 3), ev_after=round(ev_after, 3),
                budget=round(ev, 3), headroom=round(ev - extra, 3), gross=round(gross, 3),
                cost_total=round(cost_total, 3), ratio=round(ratio_gross, 2),
                ratio_net=round(ratio_net, 2), survives=bool(ev_after > 0),
                tradable=bool(ratio_gross >= ratio_min and ev_after > 0),
                kairos3_bar=bool(ev_after >= kairos3_bar))


def table(cfg=None, strategies=None, profiles=None):
    """Jedwali kamili: kila strategy × kila profile."""
    cfg = cfg or load_cfg()
    strategies = strategies or STRATEGIES
    profiles = profiles or list(cfg["profiles"])
    base = cfg["base_cost_pips"]
    rows = []
    for name, s in strategies.items():
        for pr in profiles:
            pc = profile_cost(pr, cfg, tf=s["tf"])
            ev = evaluate(s["ev"], pc["extra_total"], float(base[s["entry"]]))
            rows.append(dict(strategy=name, status=s["status"], tf=s["tf"], entry=s["entry"],
                             src=s["src"], **{f"cost_{k}": v for k, v in pc.items()}, **ev))
    return rows


def qualify_broker(commission_usd_round_turn, swap_pips_per_night, strategy, cfg=None, nights=None):
    """**Jaribio la broker YEYOTE** (hii ndiyo kazi halisi ya module): pewa commission na swap ya
    broker, rudisha kama strategy hiyo inabaki hai / tradable kwa doctrine. Hakuna backtest."""
    cfg = cfg or load_cfg()
    s = STRATEGIES[strategy] if isinstance(strategy, str) else strategy
    pv = float(cfg.get("pip_value_per_lot_usd", 10))
    n = float(nights if nights is not None else cfg.get("avg_nights_per_trade", {}).get(s["tf"], 0.0))
    extra = commission_usd_round_turn / pv + swap_pips_per_night * n
    return {**evaluate(s["ev"], extra, float(cfg["base_cost_pips"][s["entry"]])),
            "strategy": (strategy if isinstance(strategy, str) else "custom")}


def max_commission(strategy, cfg=None, nights=None, ratio_min=RATIO_MIN):
    """Commission KUBWA ZAIDI (USD/lot round-turn) inayoruhusiwa ili strategy (a) ibaki hai,
    (b) ibaki tradable kwa doctrine. Hii ndiyo namba ya kumpa broker/lessee moja kwa moja."""
    cfg = cfg or load_cfg()
    s = STRATEGIES[strategy]
    pv = float(cfg.get("pip_value_per_lot_usd", 10))
    base = float(cfg["base_cost_pips"][s["entry"]])
    n = float(nights if nights is not None else cfg.get("avg_nights_per_trade", {}).get(s["tf"], 0.0))
    swap_rate = 0.0                                   # commission pekee (swap = 0 kwenye hesabu hii)
    swap = swap_rate * n
    alive_extra = s["ev"] - swap                                          # EV_after > 0
    # doctrine: gross/(base+extra) >= ratio_min, ambapo gross = ev + base (haibadiliki na commission)
    trad_extra = (s["ev"] + base) / ratio_min - base - swap
    return dict(strategy=strategy, ev=s["ev"], base_cost=base,
                max_extra_alive=round(max(alive_extra, 0.0), 3),
                max_extra_tradable=round(max(trad_extra, 0.0), 3),
                max_commission_usd_alive=round(max(alive_extra, 0.0) * pv, 2),
                max_commission_usd_tradable=round(max(trad_extra, 0.0) * pv, 2))


# ---------- ripoti ----------
def write_report(out_root=REPO_ROOT, cfg=None):
    cfg = cfg or load_cfg()
    rows = table(cfg)
    L = [f"# COST BUDGET — gharama ambayo kila strategy inaweza kubeba (broker-agnostic)\n",
         f"*{datetime.now():%Y-%m-%d %H:%M} | chanzo cha hesabu: `cost_stress` §R5(1) `EV_new = EV − Δ` "
         f"(gharama inalipwa MARA MOJA kwa trade -> breakeven Δ = EV) | profiles: "
         f"`config/broker_costs.yaml` (PD anahariri)*\n",
         "> **Kwa nini faili hii ipo:** mfumo utatumika kwa **brokers tofauti tofauti**, kwa hiyo "
         "commission/swap ya broker mmoja HAIWEKWI kwenye research. Badala yake kila strategy ina "
         "**bajeti** — na broker yeyote anapimwa dhidi yake kwa sekunde.\n",
         "> **Muhimu:** namba za EV hapa chini tayari zime-charge **spread halisi + slippage**. "
         "Hazija-charge **commission wala swap** — hivyo ndivyo research yetu ilivyo. Jedwali hili "
         "linaziba pengo hilo bila kuendesha backtest tena (ni hesabu, si simulation).\n"]

    L.append("\n## 1. Bajeti (breakeven) na kikomo cha commission\n")
    L.append("| strategy | hali | EV (pips) | **bajeti** (Δ inayoua) | commission KUBWA inayoruhusiwa "
             "(hai) | ...(tradable, edge ≥3× cost) |")
    L.append("|---|---|---|---|---|---|")
    for name in STRATEGIES:
        m = max_commission(name, cfg)
        L.append(f"| {name} | {STRATEGIES[name]['status']} | {m['ev']:+.2f} | **{m['ev']:.2f} pips** | "
                 f"${m['max_commission_usd_alive']:.2f}/lot | ${m['max_commission_usd_tradable']:.2f}/lot |")
    L.append("\n*Commission ya \"hai\" = inayoacha EV > 0 (ukingoni). Ya \"tradable\" = inayotimiza "
             f"doctrine (charter §4.4: edge ≥ {RATIO_MIN:g}× gharama jumla). **Tumia ya pili.***")

    L.append("\n## 2. Kila strategy chini ya kila profile\n")
    L.append("| strategy | profile | comm (pips) | swap (pips) | ziada jumla | EV baada | "
             "gross/cost | net/cost | hai? | tradable (≥3× gross)? | ≥3.0 pips? |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        L.append(f"| {r['strategy']} | {r['cost_profile']} | {r['cost_commission_pips']:.2f} | "
                 f"{r['cost_swap_pips']:.2f} | **{r['extra']:.2f}** | **{r['ev_after']:+.2f}** | "
                 f"{r['ratio']:.2f}× | {r['ratio_net']:.2f}× | {'✅' if r['survives'] else '❌'} | "
                 f"{'✅' if r['tradable'] else '❌'} | {'✅' if r['kairos3_bar'] else '❌'} |")

    L.append("\n## 3. Jinsi ya kupima broker MPYA (dakika moja, bila backtest)\n")
    L.append("```python\nfrom cost_budget import qualify_broker\n"
             "qualify_broker(commission_usd_round_turn=7.0, swap_pips_per_night=0.5,\n"
             "               strategy='KAIROS-1 (STRAT-001)')\n```")
    L.append("Au ongeza profile kwenye `config/broker_costs.yaml` na uendeshe upya ripoti hii. "
             "**Hakuna code inayohitajika.**")

    L.append("\n## 4. Jinsi ya kusoma (na tahadhari)\n")
    L.append("1. **Bajeti = EV.** Strategy yenye EV +1.92 inakufa gharama ya ziada ikifika 1.92 "
             "pips/trade. Hakuna sehemu ya kujificha — ni kutoa moja kwa moja.")
    L.append(f"2. **Kubaki hai ≠ kufaa kutradiwa.** Doctrine (charter §4.4) inataka edge ≥ "
             f"{RATIO_MIN:g}× gharama. Safu ya 'tradable' ndiyo ya kutumia kwa uamuzi wa live.")
    L.append("3. **base_cost_pips** (spread+slip iliyomo tayari) ni **kadirio** kwenye config; "
             "inaweza kupimwa HASA kwa data run (spr ipo kwenye state parquet). Uwiano wa edge/cost "
             "unategemea namba hiyo — bajeti na 'hai' HAZITEGEMEI.")
    L.append("4. **Swap ya H1** inategemea usiku wa kila trade; `avg_nights_per_trade` ni kadirio "
             "(rmap.apply_swap inaweza kuhesabu HASA kwa data run).")
    L.append("5. Breadth 9/8 zimewekwa alama `*`: kanuni ya `pairs[]` ilitumia VALIDATION, kwa hiyo "
             "EV yao ni **hot**. Zitendee kama kikomo cha juu, si ahadi.")
    L.append("\n*Profitable != Tradable Edge. Protect capital first.*")

    rpt = Path(out_root) / "reports" / OUT_REPORT
    rpt.parent.mkdir(parents=True, exist_ok=True)
    rpt.write_text("\n".join(L), encoding="utf-8")
    return rpt, rows


# ---------- self-test ----------
def self_test():
    ok = True
    cfg = load_cfg()

    # [1] hesabu ya msingi: EV_new = EV − Δ (cost_stress R5(1)) — EXACT
    e = evaluate(1.92, 0.7, 0.6)
    t1 = (e["ev_after"] == 1.22 and e["budget"] == 1.92 and e["headroom"] == 1.22
          and e["survives"] and e["cost_total"] == 1.3)
    ok = ok and t1
    print(f"  [1] EV_new = EV − Δ exact: 1.92 − 0.70 = {e['ev_after']} · bajeti={e['budget']} -> {t1}")

    # [2] mipaka: Δ == EV -> EV_after == 0 (haiko hai); Δ > EV -> hasi
    z = evaluate(0.91, 0.91, 0.6); n = evaluate(0.91, 1.0, 0.6)
    t2 = z["ev_after"] == 0.0 and not z["survives"] and n["ev_after"] < 0 and not n["survives"]
    ok = ok and t2
    print(f"  [2] mpaka: Δ=EV -> {z['ev_after']} (hai={z['survives']}) · Δ>EV -> {n['ev_after']} -> {t2}")

    # [3] doctrine ratio = GROSS/cost (si net/cost): KAIROS-2 gross=(2.65+0.6)/0.6=5.42x -> tradable;
    # breadth-12 gross=(0.91+0.6)/0.6=2.52x -> HAPANA (chini ya 3x hata bila commission)
    a = evaluate(2.65, 0.0, 0.6)
    b = evaluate(0.91, 0.0, 0.6)
    t3 = (a["tradable"] and not b["tradable"] and abs(a["ratio"] - 5.42) < 0.01
          and abs(b["ratio"] - 2.52) < 0.01 and a["gross"] == 3.25)
    ok = ok and t3
    print(f"  [3] doctrine >=3x (GROSS/cost): KAIROS-2 gross={a['gross']} ratio={a['ratio']}x "
          f"tradable={a['tradable']} · breadth-12 ratio={b['ratio']}x tradable={b['tradable']} -> {t3}")

    # [4] profile -> pips: commission $7/lot = 0.70 pip; swap 0.5 x nights(H1 0.5) = 0.25
    pc = profile_cost("raw_typical", cfg, tf="H1")
    t4 = (pc["commission_pips"] == 0.7 and pc["swap_pips"] == 0.25 and pc["extra_total"] == 0.95)
    ok = ok and t4
    print(f"  [4] profile raw_typical (H1): comm={pc['commission_pips']} swap={pc['swap_pips']} "
          f"jumla={pc['extra_total']} -> {t4}")

    # [5] KIPIMO CHA BROKER: max_commission inarudisha kikomo sahihi (inverse ya evaluate)
    m = max_commission("KAIROS-1 (STRAT-001)", cfg)
    chk_alive = evaluate(1.92, m["max_extra_alive"], 0.6)
    chk_trad = evaluate(1.92, m["max_extra_tradable"], 0.6)
    t5 = (abs(chk_alive["ev_after"]) < 1e-9
          and abs(chk_trad["gross"] - 3.0 * chk_trad["cost_total"]) < 1e-6
          and m["max_commission_usd_tradable"] < m["max_commission_usd_alive"])
    ok = ok and t5
    print(f"  [5] max_commission (KAIROS-1): hai ${m['max_commission_usd_alive']} · tradable "
          f"${m['max_commission_usd_tradable']} · inverse imethibitishwa -> {t5}")

    # [6] qualify_broker: broker halisi -> jibu; commission kubwa inaua breadth lakini si KAIROS-2
    q_breadth = qualify_broker(7.0, 0.5, "breadth pairs-12 (SL1/TP1)", cfg)
    q_k2 = qualify_broker(7.0, 0.5, "KAIROS-2 (STRAT-002)", cfg)
    t6 = (not q_breadth["survives"]) and q_k2["survives"]
    ok = ok and t6
    print(f"  [6] qualify_broker($7,0.5): breadth-12 EV_after={q_breadth['ev_after']} "
          f"(hai={q_breadth['survives']}) · KAIROS-2 {q_k2['ev_after']} (hai={q_k2['survives']}) -> {t6}")

    # [7] jedwali + ripoti + determinism
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        rpt, rows = write_report(tmp, cfg)
        _, rows2 = write_report(tmp, cfg)
        det = json.dumps(rows, sort_keys=True) == json.dumps(rows2, sort_keys=True)
        txt = rpt.read_text(encoding="utf-8")
        t7 = (det and len(rows) == len(STRATEGIES) * len(cfg["profiles"])
              and "COST BUDGET" in txt and "bajeti" in txt and "tradable" in txt
              and all(k in rows[0] for k in ("survives", "tradable", "ratio", "headroom")))
    ok = ok and t7
    print(f"  [7] jedwali {len(rows)} rows ({len(STRATEGIES)} strategies × {len(cfg['profiles'])} "
          f"profiles) · ripoti · det={det} -> {t7}")

    # [8] provenance: kila strategy ina chanzo kilichoandikwa (hakuna namba isiyo na asili)
    t8 = all(s.get("src") and s.get("status") for s in STRATEGIES.values())
    ok = ok and t8
    print(f"  [8] provenance kwa kila EV ({len(STRATEGIES)} strategies): {t8}")

    print("SELF-TEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true", help="andika reports/cost_budget.md")
    ap.add_argument("--broker", nargs=2, type=float, metavar=("COMM_USD", "SWAP_PIPS"),
                    help="pima broker: commission USD/lot round-turn + swap pips/usiku")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.broker:
        cfg = load_cfg()
        print(f"BROKER: commission ${a.broker[0]}/lot round-turn · swap {a.broker[1]} pips/usiku\n")
        for name in STRATEGIES:
            q = qualify_broker(a.broker[0], a.broker[1], name, cfg)
            print(f"  {name:30s} EV {q['ev_before']:+.2f} - ziada {q['extra']:.2f} = "
                  f"**{q['ev_after']:+.2f}** · edge/cost {q['ratio']:.2f}× · "
                  f"hai={'✅' if q['survives'] else '❌'} tradable={'✅' if q['tradable'] else '❌'}")
        return 0
    if not a.report:
        print("Tumia --report | --broker <COMM_USD> <SWAP_PIPS> | --self-test.", file=sys.stderr)
        return 2
    rpt, rows = write_report()
    for name in STRATEGIES:
        m = max_commission(name)
        print(f"  {name:30s} bajeti {m['ev']:.2f} pips · commission kubwa: hai "
              f"${m['max_commission_usd_alive']:.2f} · tradable ${m['max_commission_usd_tradable']:.2f}")
    print(f"  reports/{OUT_REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
