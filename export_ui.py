"""
KARNADHAR — export the real model to the war-room UI as one JSON.
Run:  python export_ui.py   ->   frontend/public/karnadhar.json
"""
from __future__ import annotations
import json, time
from pathlib import Path
from datetime import date

from engine.realmodel import build_refineries, build_crudes, SUPPLY_HEADROOM
from engine.realopt import naive_plan, grade_plan, evaluate, scenarios, landed, yield_pen
from engine.refdata import country_info, chokepoint_exposure, load_diets
from engine.cascade import compute_cascade, CascadeParams, compute_sanction_impact
from engine.spr import plan_drawdown
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
    o = SRC_COORDS[country]
    grade, api, sul, cps, transit = country_info(country)
    path = [[o[1], o[0]]]
    for k in cps:
        c = CHOKEPOINTS[k]; path.append([c["lon"], c["lat"]])
    if not cps:
        # open-ocean lanes: a chokepoint-free route with a long voyage IS the
        # Cape route (Russia 35d, US Gulf 40d, ...) — draw it that way, matching
        # the transit-day the optimizer charges for it
        if transit >= 30 or o[1] < 20 or o[0] < 0:
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


MATERIAL_KBD = 50.0        # below this, a supplier's shadow price is a scarcity artifact


def compose_routes(scn, refs, crudes, pl, marg, gap_kbd) -> list:
    """Rank the surviving sourcing corridors the LP used to close the gap.

    Metric (validated adversarially): the LP's OWN two-stage objective, per
    corridor — PRIMARY = volume the optimizer committed (stage-1: maximise
    grade-feasible re-sourced barrels), TIEBREAK = effective landed+yield cost
    (stage-2). NOT shadow-price-first (that puts a 3-kb/d scarcity artifact at #1
    and buries the 90% lifeline) and NOT cheapest-first (same failure). The
    shadow price is an annotation on MATERIAL binding corridors only, never the
    sort key. Headline is gap-closure % so the unmet residual stays visible.
    """
    cby = {c.name: c for c in crudes}
    rby = {r.name: r for r in refs}
    shadow = {m["source"].upper(): m for m in marg}
    blocked = scn.blocked_chokepoints
    agg: dict = {}
    for rn, alloc in pl.items():
        r = rby[rn]
        for cn, v in alloc.items():
            if v < 1:
                continue
            a = agg.setdefault(cn, {"kbd": 0.0, "refs": [], "ypen": 0.0})
            a["kbd"] += v
            a["refs"].append({"name": rn, "kbd": round(v, 1), "nelson": r.nelson})
            a["ypen"] += v * yield_pen(r, cby[cn])
    rows = []
    for cn, a in agg.items():
        c = cby[cn]
        cps = list(c.chokepoints)
        if not cps and c.transit_days >= 30:
            via = "Cape of Good Hope"
        elif cps:
            via = " + ".join(cps)
        else:
            via = "open ocean"
        avg_yp = a["ypen"] / a["kbd"] if a["kbd"] else 0.0
        landed_c = landed(c, scn)
        sh = shadow.get(cn.upper())
        avail = sh["avail_kbd"] if sh else None
        material = bool(sh) and (avail or 0) >= MATERIAL_KBD
        rows.append({
            "source": cn.title(), "grade": c.grade,
            "kbd": round(a["kbd"], 1),
            "gap_share": round(a["kbd"] / gap_kbd, 3) if gap_kbd else 0,
            "refineries": sorted(a["refs"], key=lambda x: -x["kbd"]),
            "n_refineries": len(a["refs"]),
            "api": c.api, "sulphur": c.sulphur, "asph": c.asphaltene,
            "price": round(c.price_usd_bbl, 1), "transit_days": c.transit_days,
            "landed": round(landed_c, 1), "yield_pen": round(avg_yp, 2),
            "eff_cost": round(landed_c + avg_yp, 1),
            "via": via, "chokepoints": cps, "residual_risk": bool(cps),
            "cape_immune": (not cps and blocked != set()),
            "tier": "binding" if material else "slack",
            "shadow_kusd": sh["shadow_kusd_per_kbd"] if material else None,
            "avail_kbd": round(avail, 1) if avail else None,
        })
    rows.sort(key=lambda x: (-x["kbd"], x["eff_cost"]))
    min_eff = min((r["eff_cost"] for r in rows if r["kbd"] >= MATERIAL_KBD), default=0)
    for i, row in enumerate(rows):
        row["rank"] = i + 1
        row["long_tail"] = row["gap_share"] < 0.01
        row["why"] = _route_why(row, scn, min_eff)
    return rows


def _route_why(r, scn, min_eff) -> str:
    """Deterministic per-card justification. The #1 card self-defends against the
    'you just sorted by size' attack by naming its cost premium explicitly."""
    blocked = " + ".join(sorted(scn.blocked_chokepoints)) or "disruption"
    sup = " — the single largest grade-feasible corridor that survives" if r["rank"] == 1 else ""
    s = (f"The optimizer committed {r['kbd']:,.0f} kb/d here, closing "
         f"{r['gap_share'] * 100:.0f}% of the {scn.name} gap{sup}. ")
    if not r["chokepoints"]:
        lane = f"the {r['via']}" if r["via"] != "open ocean" else "open ocean (no strait)"
        s += f"It sails {lane} clear of the closure, " if scn.blocked_chokepoints else f"It routes via {lane}, "
    else:
        s += f"It transits {r['via']} (open in this scenario, but chokepoint-exposed), "
    s += f"and its {r['api']:.0f}° / {r['sulphur']}% S / {r['asph']}% asph slate runs at {r['n_refineries']} of 10 refineries. "
    prem = r["eff_cost"] - min_eff
    if r["kbd"] >= MATERIAL_KBD and prem <= 0.1:
        s += f"Landed ${r['landed']}/bbl — the cheapest surviving barrel of real scale. "
    elif prem > 0.1:
        s += (f"Landed ${r['landed']}/bbl (+${prem:.0f}/bbl above the cheapest survivor "
              f"— it ranks first on secured volume, not price). ")
    else:
        s += f"Landed ${r['landed']}/bbl. "
    if r["shadow_kusd"]:
        s += (f"Scarce: one more kb/d is worth ${r['shadow_kusd']}k/day to the system "
              f"(LP shadow price) — buy incremental volume here.")
    elif r["tier"] == "slack":
        s += "Supply slack — more available than the reroute needs; no procurement urgency."
    return s.strip()


def compose_cut_corridors(scn, crudes) -> list:
    """The corridors that DIED in this disruption — shown severed, to prove the
    ranking encodes grade-fit + chokepoint survival, not raw size (e.g. Iraq is
    a bigger supplier than Russia, yet it is CUT at Hormuz)."""
    out = []
    for c in crudes:
        if not scn.is_cut(c) or c.name not in SRC_COORDS:
            continue
        if c.name in scn.sanctioned_countries:
            reason = "sanctioned"
        else:
            hit = sorted(set(c.chokepoints) & scn.blocked_chokepoints)
            reason = f"severed at {' + '.join(hit)}" if hit else "cut"
        out.append({"source": c.name.title(), "grade": c.grade,
                    "kbd": round(c.available_kbd / SUPPLY_HEADROOM, 0), "reason": reason})
    return sorted(out, key=lambda x: -x["kbd"])


def economic_impact(scn, nv, sm, national, hormuz_exposure, russia_kbd, hz_gap) -> dict:
    """Route each scenario to the CORRECT economic channel — the fix for the
    category error of modelling every disruption as a Hormuz global shortfall:

      * Hormuz closed        -> global supply shock (Brent spike; 20 Mb/d of world
                                flow that cannot reach anyone).
      * supplier sanctioned  -> REDISTRIBUTION, not a shortfall: global Brent barely
                                moves; India's cost is the lost supplier discount +
                                the LP re-sourcing premium.
      * minor crude strait   -> freight premium (crude reroutes via the Cape).
    """
    CP = CascadeParams()
    hormuz_blocked = "Hormuz" in scn.blocked_chokepoints
    russia_sanctioned = "RUSSIA" in scn.sanctioned_countries
    discount_bn = 0.0

    if hormuz_blocked:
        closure = min(1.0, hz_gap / national / hormuz_exposure)         # ~1.0 = full Hormuz
        cas = compute_cascade(closure, CP)
        band = (compute_cascade(closure, CascadeParams(price_sensitivity_usd_per_mbd=5.0)).brent_usd,
                compute_cascade(closure, CascadeParams(price_sensitivity_usd_per_mbd=12.0)).brent_usd)
        brent, brent_pct, pump, gdp = cas.brent_usd, cas.brent_change_pct, cas.pump_inr_per_l, cas.gdp_drag_pp
        bill_day, annual_bn, cad = (cas.india_extra_import_bill_musd_day,
                                    cas.extra_annual_import_bill_usd_bn, cas.stressed_cad_pct_gdp)
        channel = "global supply shock - Hormuz carries ~20 Mb/d of irreplaceable world flow"
        if russia_sanctioned:                                          # compound: also lose the discount
            sr = compute_sanction_impact(russia_kbd, sm.yield_loss_musd_day, p=CP)
            bill_day = round(bill_day + sr.india_extra_import_bill_musd_day, 1)
            annual_bn = round(annual_bn + sr.extra_annual_import_bill_usd_bn, 1)
            cad = round(cad + sr.extra_annual_import_bill_usd_bn / CP.india_gdp_usd_bn * 100, 2)
            discount_bn = round(sr.lost_discount_musd_day * 365 / 1000.0, 1)
            channel = "global supply shock (Hormuz) + India's lost Russian discount"
    elif russia_sanctioned:
        sr = compute_sanction_impact(russia_kbd, sm.yield_loss_musd_day, p=CP)
        brent, brent_pct, pump, gdp = sr.brent_usd, sr.brent_change_pct, sr.pump_inr_per_l, sr.gdp_drag_pp
        bill_day, annual_bn, cad = (sr.india_extra_import_bill_musd_day,
                                    sr.extra_annual_import_bill_usd_bn, sr.stressed_cad_pct_gdp)
        band = (brent, brent)
        discount_bn = round(sr.lost_discount_musd_day * 365 / 1000.0, 1)
        channel = "supplier redirect - global supply intact; India loses the Urals discount + a re-sourcing premium"
    else:
        closure = min(1.0, nv.gap_kbd / national / hormuz_exposure)
        cas = compute_cascade(closure, CP)
        brent, brent_pct, pump, gdp = cas.brent_usd, cas.brent_change_pct, cas.pump_inr_per_l, cas.gdp_drag_pp
        bill_day, annual_bn, cad = (cas.india_extra_import_bill_musd_day,
                                    cas.extra_annual_import_bill_usd_bn, cas.stressed_cad_pct_gdp)
        band = (brent, brent)
        channel = "freight premium - crude reroutes via the Cape; global supply intact"

    return {"brent": brent, "brent_pct": brent_pct, "brent_lo": band[0], "brent_hi": band[1],
            "pump": pump, "gdp": gdp, "bill_day": bill_day, "cad_stressed": cad,
            "cad_base": CP.baseline_cad_pct_gdp, "annual_bn": annual_bn,
            "channel": channel, "discount_bn": discount_bn}


def compose_brief(scn, nv, sm, marg, spr, econ, commodities_hit) -> list:
    """Executive brief: engine numbers, template words (the briefing agent's
    output, rendered in the war-room; Claude drop-in writes prose, never numbers)."""
    lines = []
    cut = " + ".join(sorted(scn.blocked_chokepoints) +
                     [c.title() for c in sorted(scn.sanctioned_countries)]) or "none"
    lines.append(f"SITUATION - {scn.name}: {nv.gap_kbd:,.0f} kb/d of import supply cut ({cut}).")
    if sm.feasible:
        reroute = "fully feasible reroute; every barrel grade-matched"
    else:
        reroute = f"partial reroute; honest residual gap {sm.unmet_kbd:,.0f} kb/d"
    if not nv.feasible:
        why = (f"{nv.unrunnable_kbd:,.0f} kb/d un-runnable" if nv.unrunnable_kbd > 0
               else f"{len(nv.breaches)} blend-limit breach(es)")
        naive_note = f"naive plan infeasible ({why})"
    else:
        naive_note = "naive plan feasible but grade-blind"
    short = (f" Usable shortfall {nv.usable_short_kbd:,.0f} -> {sm.usable_short_kbd:,.0f} kb/d."
             if nv.usable_short_kbd > 0 else "")
    lines.append(f"REROUTE - KARNADHAR: {reroute}; {naive_note}.{short} "
                 f"+{sm.extra_vlcc:,.0f} VLCC-equivalents tied up.")
    mat = [m for m in marg if m["avail_kbd"] >= 50]
    if mat:
        top = ", ".join(f"{m['source']} ({m['grade']}, ${m['shadow_kusd_per_kbd']}k/day per kb/d)"
                        for m in mat[:2])
        lines.append(f"PROCUREMENT PRIORITY - secure marginal barrels first: {top} [LP shadow prices].")
    lines.append(f"RESERVES - {spr.summary()}.")
    if econ["discount_bn"] and econ["brent"] < 95:                 # pure sanction — no global shock
        lines.append(f"ECONOMY - {econ['channel']}. Brent ~${econ['brent']:.0f} (redistribution, "
                     f"not a shortfall); India's real cost = lost Urals discount ~${econ['discount_bn']:.1f}bn/yr "
                     f"+ re-sourcing premium -> CAD {econ['cad_base']}% -> {econ['cad_stressed']:.1f}% GDP.")
    else:
        extra = (f"; +${econ['discount_bn']:.1f}bn/yr lost Russian discount on top"
                 if econ["discount_bn"] else "")
        lines.append(f"ECONOMY - {econ['channel']}. Brent ${econ['brent']:.0f} "
                     f"(sensitivity ${econ['brent_lo']:.0f}-{econ['brent_hi']:.0f}), "
                     f"pump ~Rs{econ['pump']:.0f}/L, CAD {econ['cad_base']}% -> {econ['cad_stressed']:.1f}% GDP{extra}.")
    if commodities_hit:
        spill = ", ".join(f"{c['name']} {c['affected']:.0%}" for c in commodities_hit[:2])
        lines.append(f"SPILLOVER - hardest-hit other imports: {spill}.")
    lines.append("SEQUENCE (per ORF review) - re-source first, bridge with SPR, demand-manage last.")
    return lines


def main():
    refs, crudes = build_refineries(), build_crudes()
    raw = load_diets()
    national = sum(r.capacity_kbd for r in refs)
    # DERIVE the national Hormuz exposure from the model itself (no hardcoding)
    hz_gap = sum(r.volume_at_risk({"Hormuz"}, set()) for r in refs)
    hormuz_exposure = hz_gap / national
    # real Russian import volume — the barrels a sanction would strand (discount-loss economics)
    russia_kbd = sum(r.volume_at_risk(set(), {"RUSSIA"}) for r in refs)

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
        pl, st, marg = grade_plan(refs, crudes, scn)
        sm = evaluate("smart", pl, refs, crudes, scn)
        ms = round((time.perf_counter() - t0) * 1000, 1)
        # scenario-aware economics: global shock (Hormuz) vs discount-loss (sanction)
        # vs freight premium (minor strait) — NOT one cascade for all
        econ = economic_impact(scn, nv, sm, national, hormuz_exposure, russia_kbd, hz_gap)
        spr = plan_drawdown(sm.unmet_kbd, sm.spr_bridge_days, national)
        com_hit = [c for c in commodity_screen(scn.blocked_chokepoints,
                                               {s.upper() for s in scn.sanctioned_countries})
                   if c["key"] != "crude_oil" and c["affected"] > 0.05]
        brief = compose_brief(scn, nv, sm, marg, spr, econ, com_hit)
        routes_ranked = compose_routes(scn, refs, crudes, pl, marg, nv.gap_kbd)
        cut_corridors = compose_cut_corridors(scn, crudes)
        cut = [c.name.title() for c in crudes if scn.is_cut(c) and c.name in SRC_COORDS]
        scen_out.append({
            "key": key, "name": scn.name,
            "blocked": list(scn.blocked_chokepoints), "sanctioned": list(scn.sanctioned_countries),
            "cut_sources": cut, "gap_kbd": nv.gap_kbd, "solve_ms": ms,
            "naive": {"feasible": nv.feasible, "unrunnable": nv.unrunnable_kbd,
                      "unmet": nv.unmet_kbd, "usable_short": nv.usable_short_kbd,
                      "yield_loss": nv.yield_loss_musd_day,
                      "true_cost": nv.true_cost_musd_day, "breaches": nv.breaches[:6]},
            "smart": {"feasible": sm.feasible, "unmet": sm.unmet_kbd,
                      "usable_short": sm.usable_short_kbd,
                      "yield_loss": sm.yield_loss_musd_day, "true_cost": sm.true_cost_musd_day,
                      "avg_transit": sm.avg_transit_days, "spr_bridge": sm.spr_bridge_days,
                      "effective_spr": sm.effective_spr_days, "spr_margin": sm.spr_margin_days,
                      "fleet_vlcc": sm.fleet_vlcc, "extra_vlcc": sm.extra_vlcc,
                      "marginals": [m for m in marg if m["avail_kbd"] >= 50][:3],
                      "plan": plan_rows(pl, crudes)},
            "cascade": econ,
            "spr": {"verdict": spr.verdict, "draw_rate_kbd": spr.draw_rate_kbd,
                    "depletion_pct": spr.depletion_pct,
                    "demand_mgmt_kbd": spr.demand_mgmt_kbd,
                    "summary": spr.summary()},
            "brief": brief,
            "routes_ranked": routes_ranked,
            "cut_corridors": cut_corridors,
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
        "meta": {"national_kbd": round(national), "hormuz_exposure": round(hormuz_exposure, 3),
                 "n_refineries": len(refs), "n_grades": len(crudes),
                 "n_commodities": len(commodities), "generated": date.today().isoformat()},
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
