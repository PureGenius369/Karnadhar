"""
KARNADHAR — validation suite
============================

Run:  python run_validate.py     (from the karnadhar/ folder)

Automated proof that the core holds. Every check is a falsifiable assertion about
the engine's behaviour — the wedge result, cascade monotonicity, signal lead time,
scenario degradation, real-data integrity, and config derivation sanity. Exits
non-zero if anything fails, so it doubles as a CI gate / pre-submission check.
"""

from __future__ import annotations
import sys
import traceback

PASS, FAIL = 0, 0
SECTION = ""


def section(name: str):
    global SECTION
    SECTION = name
    print(f"\n  {name}")
    print("  " + "-" * 66)


def check(desc: str, cond: bool, detail: str = ""):
    global PASS, FAIL
    mark = "PASS" if cond else "FAIL"
    if cond:
        PASS += 1
    else:
        FAIL += 1
    line = f"    [{mark}] {desc}"
    if detail:
        line += f"  ({detail})"
    print(line)


def main() -> int:
    print("=" * 72)
    print("  KARNADHAR VALIDATION SUITE")
    print("=" * 72)

    # ------------------------------------------------------------------ #
    section("1. THE WEDGE — grade-blind fails for GRADE reasons, ours doesn't")
    from engine.data import HORMUZ_CLOSURE, REFINERIES
    from engine.optimizer import naive_fungible_plan, grade_aware_plan, evaluate

    naive = evaluate("naive", naive_fungible_plan(HORMUZ_CLOSURE), HORMUZ_CLOSURE)
    plan, status = grade_aware_plan(HORMUZ_CLOSURE)
    smart = evaluate("smart", plan, HORMUZ_CLOSURE)

    check("naive (fungible) plan is INFEASIBLE", not naive.feasible)
    check("naive failure is a GRADE failure (un-runnable kb/d > 0)",
          naive.unrunnable_kbd > 0, f"{naive.unrunnable_kbd} kb/d")
    check("naive respects supply (no oversubscription — fair steelman)",
          not naive.oversubscribed)
    check("KARNADHAR plan is FEASIBLE", smart.feasible)
    check("LP solver reports Optimal", status == "Optimal", status)
    check("KARNADHAR protects yield vs naive",
          smart.yield_loss_musd_day < naive.yield_loss_musd_day,
          f"{naive.yield_loss_musd_day} -> {smart.yield_loss_musd_day} $M/day")
    check("honest SPR: effective cover exceeds voyage bridge",
          smart.effective_spr_days > smart.spr_bridge_days,
          f"{smart.effective_spr_days}d vs {smart.spr_bridge_days}d")

    # ------------------------------------------------------------------ #
    section("2. CASCADE — monotonic, testable, twin-deficit wired")
    from engine.cascade import compute_cascade, CascadeParams

    p = CascadeParams()
    rows = [compute_cascade(f, p) for f in (0.0, 0.25, 0.5, 0.75, 1.0)]
    brents = [r.brent_usd for r in rows]
    cads = [r.stressed_cad_pct_gdp for r in rows]
    check("Brent is non-decreasing in closure severity",
          all(b2 >= b1 for b1, b2 in zip(brents, brents[1:])), str(brents))
    check("pipeline bypass absorbs a 25% closure (no price impact)",
          rows[1].brent_usd == p.brent_base_usd)
    check("CAD widens monotonically (twin deficit)",
          all(c2 >= c1 for c1, c2 in zip(cads, cads[1:])), str(cads))
    check("full closure stresses CAD above 5% of GDP",
          rows[-1].stressed_cad_pct_gdp > 5.0, f"{rows[-1].stressed_cad_pct_gdp}%")
    check("zero closure = zero impact (sanity)",
          rows[0].brent_usd == p.brent_base_usd and rows[0].gdp_drag_pp == 0)
    lo = compute_cascade(1.0, CascadeParams(price_sensitivity_usd_per_mbd=5.0)).brent_usd
    hi = compute_cascade(1.0, CascadeParams(price_sensitivity_usd_per_mbd=12.0)).brent_usd
    mid = rows[-1].brent_usd
    check("EF-3 testable: Brent sensitivity band brackets the central estimate",
          lo < mid < hi, f"${lo:.0f} < ${mid:.0f} < ${hi:.0f}")

    # ------------------------------------------------------------------ #
    section("3. SIGNAL — alert leads the market repricing")
    from datetime import date
    from engine.signals.gdelt import timeline_with_fallback
    from engine.signals.agent import GeopoliticalRiskAgent

    pts, src = timeline_with_fallback('"strait of hormuz"', "20250601000000",
                                      "20250630000000",
                                      "hormuz_2025_06_representative.json")
    bt = GeopoliticalRiskAgent().assess(pts, date(2025, 6, 23))
    check("signal data available (enough days for baseline + detection)",
          pts is not None and len(pts) >= 12,
          f"source={src}, {len(pts)} points")
    check("alert was raised", bt.alert_day is not None, str(bt.alert_day))
    check("alert PRECEDES the Brent +8% session", bt.lead_days and bt.lead_days > 0,
          f"{bt.lead_days} days lead")
    check("alert not absurdly early (< 20 days = crisis-driven, not noise)",
          bt.lead_days is not None and bt.lead_days < 20)

    from engine.signals.extract import classify_headlines
    sigs = classify_headlines([
        "Iran's parliament moves to consider closing the Strait of Hormuz",
        "Diplomats signal de-escalation; ceasefire talks reported",
    ])
    check("closure headline scored max severity", sigs[0].severity == 5,
          f"sev={sigs[0].severity}")
    check("de-escalation headline scored low", sigs[1].severity <= 1,
          f"sev={sigs[1].severity}")

    # ------------------------------------------------------------------ #
    section("4. REAL DATA — DGCIS diets, derived configs, general disruption")
    from engine.realmodel import build_refineries, build_crudes, Disruption
    from engine import realopt

    refs = build_refineries()
    crudes = build_crudes()
    national = sum(r.capacity_kbd for r in refs)
    check("10 refineries load from DGCIS records", len(refs) == 10, str(len(refs)))
    check("national run ~5,000 kb/d (matches PPAC reality)",
          4500 < national < 5600, f"{national:,.0f} kb/d")

    hormuz = Disruption("t", blocked_chokepoints={"Hormuz"})
    gap = sum(r.volume_at_risk({"Hormuz"}, set()) for r in refs)
    check("derived national Hormuz exposure in the cited 40-50% band",
          0.40 < gap / national < 0.50, f"{gap/national:.0%}")

    for r in refs:
        if not (r.api_min < r.api_opt < r.api_max):
            check(f"config sane for {r.name}", False,
                  f"{r.api_min}/{r.api_opt}/{r.api_max}")
            break
    else:
        check("every refinery: api_min < api_opt < api_max", True)

    deep = [r for r in refs if r.nelson >= 12]
    simple = [r for r in refs if r.nelson < 9]
    check("deep-conversion refineries accept higher asphaltene than simple ones",
          min(d.max_asphaltene for d in deep) > max(s.max_asphaltene for s in simple))

    nv = realopt.evaluate("n", realopt.naive_plan(refs, crudes, hormuz), refs, crudes, hormuz)
    pl, st, marg = realopt.grade_plan(refs, crudes, hormuz)
    sm = realopt.evaluate("s", pl, refs, crudes, hormuz)
    check("REAL-data Hormuz: naive breaches constraints", not nv.feasible,
          f"{len(nv.breaches)} breaches")
    check("REAL-data Hormuz: KARNADHAR fully feasible", sm.feasible,
          f"unmet={sm.unmet_kbd}")
    check("Hormuz reroute prices the ton-mile effect (extra VLCC-equivalents > 0)",
          sm.extra_vlcc > 10, f"+{sm.extra_vlcc:.0f} VLCCs")
    check("LP duals expose scarce supply (positive shadow prices)",
          len(marg) > 0 and all(m["shadow_kusd_per_kbd"] > 0 for m in marg),
          f"{len(marg)} binding suppliers, top ${marg[0]['shadow_kusd_per_kbd']}k/day/kbd"
          if marg else "none")

    ru = Disruption("t2", sanctioned_countries={"RUSSIA"})
    ru_gap = sum(r.volume_at_risk(set(), {"RUSSIA"}) for r in refs)
    check("supplier sanction works as a disruption axis (Russia gap > 0)",
          ru_gap > 800, f"{ru_gap:.0f} kb/d")
    ru_scn = realopt.scenarios()["russia_sanction"]
    ru_pl, ru_st, _ = realopt.grade_plan(refs, crudes, ru_scn)
    ru_sm = realopt.evaluate("rs", ru_pl, refs, crudes, ru_scn)
    check("Russia sanction: KARNADHAR plan feasible (no boundary-rounding artifact)",
          ru_sm.feasible, f"breaches={len(ru_sm.breaches)}")

    dual = Disruption("t3", blocked_chokepoints={"Hormuz"}, sanctioned_countries={"RUSSIA"})
    check("compound disruption strictly worse than single",
          sum(r.volume_at_risk(dual.blocked_chokepoints, dual.sanctioned_countries)
              for r in refs) > gap)
    du_scn = realopt.scenarios()["hormuz_russia"]
    du_nv = realopt.evaluate("dn", realopt.naive_plan(refs, crudes, du_scn),
                             refs, crudes, du_scn)
    du_pl, _, _ = realopt.grade_plan(refs, crudes, du_scn)
    du_sm = realopt.evaluate("ds", du_pl, refs, crudes, du_scn)
    check("compound shock: naive USABLE shortfall exceeds KARNADHAR's (fake fill exposed)",
          du_nv.usable_short_kbd > du_sm.usable_short_kbd,
          f"{du_nv.usable_short_kbd:.0f} vs {du_sm.usable_short_kbd:.0f} kb/d")

    rs_scn = realopt.scenarios()["red_sea"]
    rs_pl, _, _ = realopt.grade_plan(refs, crudes, rs_scn)
    rs_sm = realopt.evaluate("rss", rs_pl, refs, crudes, rs_scn)
    check("Red Sea suspension (brief-named): India's CRUDE is largely insulated",
          0 < rs_sm.gap_kbd < 0.1 * sm.gap_kbd and rs_sm.feasible,
          f"{rs_sm.gap_kbd:.0f} kb/d vs Hormuz {sm.gap_kbd:.0f} (feasible, small-volume rounding sound)")

    from engine.spr import plan_drawdown
    hz_spr = plan_drawdown(sm.unmet_kbd, sm.spr_bridge_days, national)
    du_spr = plan_drawdown(du_sm.unmet_kbd, du_sm.spr_bridge_days, national)
    check("SPR scheduler (brief-named): holds reserves when reroute covers demand, "
          "rations when it cannot",
          hz_spr.verdict == "hold" and du_spr.verdict in ("ration", "bridge")
          and (du_spr.verdict != "ration" or du_spr.demand_mgmt_kbd > 0),
          f"hormuz={hz_spr.verdict}, compound={du_spr.verdict} "
          f"(demand mgmt {du_spr.demand_mgmt_kbd:.0f} kb/d)")

    # ------------------------------------------------------------------ #
    section("5. SCENARIO LIBRARY — degrades honestly under stress")
    from engine.scenarios import SCENARIOS
    from engine.optimizer import naive_fungible_plan as nfp, grade_aware_plan as gap_plan, evaluate as ev

    h = SCENARIOS["hormuz_full"]
    o = SCENARIOS["hormuz_opec"]
    d2 = SCENARIOS["dual_choke"]
    check("dual chokepoint leaves fewer alternates than single",
          len(d2.available_crudes()) < len(h.available_crudes()),
          f"{len(h.available_crudes())} -> {len(d2.available_crudes())}")
    p1, _ = gap_plan(h); m1 = ev("a", p1, h)
    p2, _ = gap_plan(o); m2 = ev("b", p2, o)
    check("OPEC squeeze forces unmet demand (engine admits its limits)",
          m2.unmet_demand_kbd > 0 and m1.unmet_demand_kbd == 0,
          f"{m1.unmet_demand_kbd} -> {m2.unmet_demand_kbd} kb/d")

    # ------------------------------------------------------------------ #
    section("6. MULTI-COMMODITY — the framework generalises beyond oil")
    from engine.commodities import COMMODITIES, BY_KEY, screen

    check("all vulnerability indices in (0, 100)",
          all(0 < c.vulnerability_index < 100 for c in COMMODITIES),
          f"{len(COMMODITIES)} commodities")
    check("framework discriminates: coking coal high-dependence but ZERO chokepoint",
          BY_KEY["coking_coal"].import_dependence > 0.8
          and BY_KEY["coking_coal"].max_chokepoint == 0.0)
    hz = {r["key"]: r["affected"] for r in screen({"Hormuz"})}
    check("Hormuz is not just a crude problem (LNG hit >= 40%)",
          hz["lng"] >= 0.4 and abs(hz["crude_oil"] - 0.46) < 0.01,
          f"LNG {hz['lng']:.0%}, crude {hz['crude_oil']:.0%}")
    both = {r["key"]: r["affected"] for r in screen({"Hormuz"}, {"RUSSIA"})}
    check("compound disruption never reduces any commodity's affected share",
          all(both[k] >= hz[k] - 1e-9 for k in hz))
    rs = {r["key"]: r["affected"] for r in screen({"Bab-el-Mandeb", "Suez"})}
    check("commodity-specific arteries: Red Sea spares crude but hits edible oils",
          rs["crude_oil"] < 0.10 and rs["edible_oil"] >= 0.15,
          f"crude {rs['crude_oil']:.0%} vs edible oil {rs['edible_oil']:.0%}")

    # ------------------------------------------------------------------ #
    section("7. UI EXPORT — the war-room JSON is complete & consistent")
    import json
    from pathlib import Path
    ui = Path("frontend/public/karnadhar.json")
    check("karnadhar.json exists (run export_ui.py)", ui.exists())
    if ui.exists():
        d = json.loads(ui.read_text())
        check("has all top-level blocks",
              all(k in d for k in ("meta", "refineries", "sources", "routes",
                                   "signal", "scenarios")))
        check("5 scenarios exported (incl. brief-named Red Sea suspension)",
              len(d.get("scenarios", [])) == 5
              and any(s["key"] == "red_sea" for s in d["scenarios"]))
        check("every scenario ships an executive brief + SPR schedule",
              all(len(s.get("brief", [])) >= 5 and "spr" in s
                  and any(ln.startswith("RESERVES") for ln in s["brief"])
                  for s in d.get("scenarios", [])))
        hz = next((s for s in d["scenarios"] if s["key"] == "hormuz"), None)
        check("Hormuz scenario: naive infeasible in export",
              hz is not None and hz["naive"]["feasible"] is False)
        check("Hormuz scenario: smart plan non-empty",
              hz is not None and len(hz["smart"]["plan"]) > 5)
        check("signal lead time exported and positive",
              d["signal"]["lead_days"] and d["signal"]["lead_days"] > 0,
              f"{d['signal']['lead_days']}d, source={d['signal']['source']}")
        check("export carries the decision layer (marginals, VLCC, usable shortfall)",
              hz is not None and "marginals" in hz["smart"]
              and "extra_vlcc" in hz["smart"] and "usable_short" in hz["naive"])
        check("hormuz naive breach lines exported (UI can explain INFEASIBLE)",
              hz is not None and len(hz["naive"].get("breaches", [])) > 0)

    # ------------------------------------------------------------------ #
    print("\n" + "=" * 72)
    total = PASS + FAIL
    print(f"  RESULT: {PASS}/{total} checks passed" + ("" if FAIL == 0 else f"  |  {FAIL} FAILED"))
    print("=" * 72)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        sys.exit(2)
