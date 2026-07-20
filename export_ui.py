"""
KARNADHAR — export the real model to the war-room UI as one JSON.
Run:  python export_ui.py   ->   frontend/public/karnadhar.json
"""
from __future__ import annotations
import json, time
from pathlib import Path
from datetime import date

from engine.realmodel import build_refineries, build_crudes
from engine.realopt import naive_plan, grade_plan, evaluate, scenarios, landed
from engine.refdata import country_info, chokepoint_exposure, load_diets
from engine.cascade import compute_cascade, CascadeParams
from engine.signals.gdelt import timeline_with_fallback
from engine.signals.agent import GeopoliticalRiskAgent
from engine.signals.ais import fetch_ais
from engine.commodities import screen as commodity_screen

OUT = Path(__file__).parent / "frontend" / "public" / "karnadhar.json"

INDIA_HUB = {"lat": 22.4, "lon": 69.1}
CHOKEPOINTS = {
    "Hormuz": {"lat": 26.57, "lon": 56.25, "label": "Strait of Hormuz"},
    "Bab-el-Mandeb": {"lat": 12.6, "lon": 43.3, "label": "Bab-el-Mandeb"},
    "Suez": {"lat": 30.6, "lon": 32.35, "label": "Suez Canal"},
    "Cape": {"lat": -34.4, "lon": 18.5, "label": "Cape of Good Hope"},
    "Malacca": {"lat": 2.5, "lon": 101.5, "label": "Strait of Malacca"},
}
REF_COORDS = {
    "RIL Jamnagar": (22.34, 69.85), "Nayara Vadinar": (22.28, 69.73),
    "IOCL Paradip": (20.27, 86.67), "HMEL Bathinda": (30.21, 74.95),
    "BPCL/HPCL Mumbai": (19.0, 72.83), "HPCL Visakhapatnam": (17.69, 83.22),
    "BPCL Kochi": (9.97, 76.28), "MRPL Mangalore": (12.95, 74.83),
    "CPCL Chennai": (13.08, 80.29), "ONGC Mangalore (OMPL)": (12.9, 74.86),
}
SRC_COORDS = {
    "RUSSIA": (44.7, 37.8), "IRAQ": (30.0, 48.0), "SAUDI ARAB": (26.6, 50.0),
    "U ARAB EMTS": (24.5, 54.4), "U S A": (29.3, -94.8), "KUWAIT": (29.1, 48.1),
    "NIGERIA": (4.3, 7.0), "ANGOLA": (-8.8, 13.2), "BRAZIL": (-22.9, -43.2),
    "COLOMBIA": (10.4, -75.5), "OMAN": (23.6, 58.5), "QATAR": (25.9, 51.6),
    "VENEZUELA": (10.5, -64.2), "MEXICO": (19.2, -96.1), "CANADA": (49.0, -123.0),
    "ALGERIA": (36.8, 3.0), "NORWAY": (60.0, 2.0), "EGYPT A RP": (29.9, 32.5),
    "CONGO P REP": (-4.8, 11.8), "GABON": (-0.7, 8.8),
}


def route_path(country):
    """origin -> (chokepoint) -> India, as [lon,lat] pairs."""
    if country not in SRC_COORDS:
        return None
    o = SRC_COORDS[country]; cps = country_info(country)[3]
    path = [[o[1], o[0]]]
    for k in cps:
        c = CHOKEPOINTS[k]; path.append([c["lon"], c["lat"]])
    if not cps:  # open-ocean: bend around the Cape if crossing hemispheres
        if o[1] < 20 or o[0] < 0:
            path.append([CHOKEPOINTS["Cape"]["lon"], CHOKEPOINTS["Cape"]["lat"]])
    path.append([INDIA_HUB["lon"], INDIA_HUB["lat"]])
    return path


def plan_rows(plan, crudes):
    cby = {c.name: c for c in crudes}
    rows = []
    for rn, alloc in plan.items():
        for cn, v in alloc.items():
            rows.append({"refinery": rn, "grade": cby[cn].grade, "source": cn.title(),
                         "kbd": v})
    return rows


def main():
    refs, crudes = build_refineries(), build_crudes()
    raw = load_diets()
    national = sum(r.capacity_kbd for r in refs)

    # geo
    refineries = []
    for r in refs:
        lat, lon = REF_COORDS.get(r.name, (20, 78))
        exp = chokepoint_exposure(raw[r.name]["diet"]).get("Hormuz", 0)
        refineries.append({
            "name": r.name, "lat": lat, "lon": lon, "kbd": r.capacity_kbd,
            "nelson": r.nelson, "hormuz": round(exp, 2), "api_opt": r.api_opt,
            "diet": {k.title(): round(v, 1) for k, v in sorted(
                r.diet_kbd.items(), key=lambda x: -x[1])[:5]}})
    sources = []
    for c in crudes:
        if c.name not in SRC_COORDS:
            continue
        sources.append({"source": c.name.title(), "grade": c.grade,
                        "lat": SRC_COORDS[c.name][0], "lon": SRC_COORDS[c.name][1],
                        "api": c.api, "sulphur": c.sulphur, "asph": c.asphaltene,
                        "price": c.price_usd_bbl, "kbd": c.available_kbd,
                        "chokepoints": list(c.chokepoints)})
    routes = []
    for c in crudes:
        p = route_path(c.name)
        if p:
            routes.append({"source": c.name.title(), "path": p,
                           "chokepoints": list(c.chokepoints), "kbd": c.available_kbd})

    # signal (real GDELT if cached)
    pts, src = timeline_with_fallback('"strait of hormuz"', "20250601000000",
                                      "20250630000000", "hormuz_2025_06_representative.json")
    bt = GeopoliticalRiskAgent().assess(pts, date(2025, 6, 23))
    signal = {"source": src, "alert_day": str(bt.alert_day), "lead_days": bt.lead_days,
              "market_day": str(bt.market_day), "baseline": bt.baseline_mean,
              "series": [{"day": str(p.day), "x": round(p.volume / (bt.baseline_mean or 1), 1),
                          "alerted": p.alerted} for p in bt.series]}

    # scenarios
    scen_out = []
    for key, scn in scenarios().items():
        t0 = time.perf_counter()
        nv = evaluate("naive", naive_plan(refs, crudes, scn), refs, crudes, scn)
        pl, st = grade_plan(refs, crudes, scn)
        sm = evaluate("smart", pl, refs, crudes, scn)
        ms = round((time.perf_counter() - t0) * 1000, 1)
        closure = min(1.0, nv.gap_kbd / national / 0.46)  # gap as frac of Hormuz-max
        cas = compute_cascade(min(1.0, closure), CascadeParams())
        cut = [c.name.title() for c in crudes if scn.is_cut(c) and c.name in SRC_COORDS]
        scen_out.append({
            "key": key, "name": scn.name,
            "blocked": list(scn.blocked_chokepoints), "sanctioned": list(scn.sanctioned_countries),
            "cut_sources": cut, "gap_kbd": nv.gap_kbd, "solve_ms": ms,
            "naive": {"feasible": nv.feasible, "unrunnable": nv.unrunnable_kbd,
                      "unmet": nv.unmet_kbd, "yield_loss": nv.yield_loss_musd_day,
                      "true_cost": nv.true_cost_musd_day, "breaches": nv.breaches[:6]},
            "smart": {"feasible": sm.feasible, "unmet": sm.unmet_kbd,
                      "yield_loss": sm.yield_loss_musd_day, "true_cost": sm.true_cost_musd_day,
                      "avg_transit": sm.avg_transit_days, "spr_bridge": sm.spr_bridge_days,
                      "effective_spr": sm.effective_spr_days, "spr_margin": sm.spr_margin_days,
                      "plan": plan_rows(pl, crudes)},
            "cascade": {"brent": cas.brent_usd, "brent_pct": cas.brent_change_pct,
                        "pump": cas.pump_inr_per_l, "gdp": cas.gdp_drag_pp,
                        "bill_day": cas.india_extra_import_bill_musd_day,
                        "cad_stressed": cas.stressed_cad_pct_gdp,
                        "cad_base": 1.2, "annual_bn": cas.extra_annual_import_bill_usd_bn},
        })

    # vessels: real cached AIS (Malacca live) + labelled Hormuz snapshot
    vessels = []
    for ck in ("Malacca", "Hormuz"):
        vs, vsrc = fetch_ais(ck, seconds=5)
        for v in vs:
            vessels.append({"name": v.get("name") or "vessel", "lat": v["lat"],
                            "lon": v["lon"], "sog": v.get("sog"),
                            "source": "live" if vsrc in ("live", "cache") else "snapshot"})

    # multi-commodity screening baseline (UI recomputes per-scenario shares)
    commodities = commodity_screen()

    data = {
        "meta": {"national_kbd": round(national), "hormuz_exposure": 0.46,
                 "n_refineries": len(refs), "n_grades": len(crudes),
                 "n_commodities": len(commodities), "generated": "2026-07-18"},
        "india_hub": INDIA_HUB, "chokepoints": CHOKEPOINTS,
        "refineries": refineries, "sources": sources, "routes": routes,
        "vessels": vessels, "commodities": commodities,
        "signal": signal, "scenarios": scen_out,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1))
    print(f"wrote {OUT}  ({OUT.stat().st_size//1024} KB)")
    print(f"  {len(refs)} refineries, {len(scen_out)} scenarios, signal={src}")


if __name__ == "__main__":
    main()
