"""
KARNADHAR — Scenario modeller demo   (Evaluation Focus #3)

Run:  python run_scenarios.py     (from the karnadhar/ folder)

Runs the full library of disruption scenarios through the grade-aware reroute and
the economic cascade, showing how feasibility and cost degrade as more of the map
is cut — including the honest case where even optimal rerouting cannot cover the
gap and demand management becomes mandatory.
"""

from engine.scenarios import SCENARIOS
from engine.optimizer import naive_fungible_plan, grade_aware_plan, evaluate
from engine.cascade import compute_cascade, CascadeParams

LINE = "=" * 92


def run_one(scn):
    crudes = scn.available_crudes()
    naive = evaluate("naive", naive_fungible_plan(scn), scn)
    plan, status = grade_aware_plan(scn)
    smart = evaluate("smart", plan, scn)
    cas = compute_cascade(scn.cascade_closure, CascadeParams())
    yield_prot = round(naive.yield_loss_musd_day - smart.yield_loss_musd_day, 2)
    return crudes, naive, smart, cas, yield_prot


def main():
    print(LINE)
    print("  KARNADHAR SCENARIO MODELLER  -  reroute feasibility & cost across disruptions")
    print(LINE)
    hdr = (f"  {'scenario':<42}{'alts':>5}{'naive':>12}{'KARNADHAR':>16}"
           f"{'unmet':>8}{'yield$':>8}{'SPRmrg':>8}")
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))

    details = []
    for key, scn in SCENARIOS.items():
        crudes, naive, smart, cas, yield_prot = run_one(scn)
        nflag = "FEAS" if naive.feasible else f"INF {naive.unrunnable_kbd + naive.unmet_demand_kbd:.0f}"
        sflag = "FEASIBLE" if smart.feasible else "INFEASIBLE"
        print(f"  {scn.name:<42}{len(crudes):>5}{nflag:>12}{sflag:>16}"
              f"{smart.unmet_demand_kbd:>7.0f}{yield_prot:>8.2f}{smart.spr_margin_days:>7.0f}")
        details.append((scn, crudes, naive, smart, cas, yield_prot))

    print("\n" + LINE)
    print("  WHAT EACH SCENARIO TELLS US")
    print(LINE)
    for scn, crudes, naive, smart, cas, yield_prot in details:
        print(f"\n  {scn.name}")
        print(f"    alternates available : {len(crudes)}  ({', '.join(c.name for c in crudes if c.name not in ('Basrah Light','Basrah Heavy','Arab Light','Arab Medium','Arab Heavy','Murban','Upper Zakum','Qatar Marine'))})")
        print(f"    grade-blind reroute  : {'feasible' if naive.feasible else f'INFEASIBLE ({naive.unrunnable_kbd:.0f} kb/d un-runnable, {naive.unmet_demand_kbd:.0f} kb/d unmet)'}")
        if smart.feasible:
            print(f"    KARNADHAR reroute    : FEASIBLE, ${smart.true_cost_musd_day:.0f}M/day true cost, "
                  f"protects ${yield_prot:.2f}M/day yield")
        else:
            print(f"    KARNADHAR reroute    : CANNOT FULLY COVER - {smart.unmet_demand_kbd:.0f} kb/d unmet "
                  f"=> mandatory demand management / SPR draw")
        print(f"    strategic reserve    : ~{smart.effective_spr_days:.0f}d cover vs {smart.spr_bridge_days:.0f}d bridge "
              f"= {smart.spr_margin_days:+.0f}d margin")

    print("\n" + LINE)
    print("  The engine is not a one-scenario demo: it generalises across chokepoints and")
    print("  supply shocks, and HONESTLY flags when a disruption is too severe to reroute")
    print("  around - which is itself the most decision-useful output.")
    print(LINE)


if __name__ == "__main__":
    main()
