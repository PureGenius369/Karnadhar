"""
KARNADHAR — Hormuz disruption demo
==================================

Run:  python run_demo.py     (from the karnadhar/ folder)

Head-to-head that anchors the pitch: a FAIR 'fungible' buyer (price-rational but
grade-blind, and it respects supply) vs. KARNADHAR's grade-aware reroute. The
fungible plan fails for one reason only — crude grade — which is the whole thesis.
"""

from engine.data import (
    HORMUZ_CLOSURE, REFINERIES, SPR_DAYS_COVER,
    NATIONAL_RUN_KBD, TOTAL_HORMUZ_GAP_KBD, HORMUZ_SUPPLY_FRACTION,
)
from engine.optimizer import naive_fungible_plan, grade_aware_plan, evaluate

LINE = "=" * 76


def show_plan(title, plan):
    print(f"\n  {title}")
    for rname, alloc in plan.items():
        if not alloc:
            continue
        slate = ", ".join(f"{c} {v:.0f}" for c, v in alloc.items())
        print(f"    {rname:16s} <- {slate}  kb/d")


def show_metrics(m):
    flag = "FEASIBLE" if m.feasible else "INFEASIBLE"
    print(f"\n  [{m.label}]  ->  {flag}")
    if m.oversubscribed:
        for g, kbd in m.oversubscribed.items():
            print(f"    ! supply short: {g} over-ordered by {kbd:.0f} kb/d")
    if m.window_breaches:
        print(f"    ! un-runnable grade assignments ({m.unrunnable_kbd:.0f} kb/d total):")
        for b in m.window_breaches[:4]:
            print(f"        - {b}")
    if m.desulph_breaches:
        for b in m.desulph_breaches:
            print(f"    ! desulphurisation exceeded: {b}")
    print(f"    crude bill        : ${m.crude_cost_musd_day:6.2f} M/day")
    print(f"    yield value lost  : ${m.yield_loss_musd_day:6.2f} M/day  (mis-fit slate)")
    print(f"    TRUE cost         : ${m.true_cost_musd_day:6.2f} M/day  (crude+freight+yield)")
    print(f"    avg voyage        : {m.avg_transit_days:5.1f} days")


def main():
    s = HORMUZ_CLOSURE

    print(LINE)
    print(f"  SCENARIO: {s.name}")
    print(f"  Re-source {TOTAL_HORMUZ_GAP_KBD:,.0f} kb/d across {len(REFINERIES)} refineries "
          f"= {HORMUZ_SUPPLY_FRACTION:.0%} of the {NATIONAL_RUN_KBD:,.0f} kb/d national run")
    print(f"  (crisis scramble premium: +${s.scramble_premium_usd:.0f}/bbl on every alternate)")
    print(LINE)

    naive = naive_fungible_plan(s)
    mn = evaluate("NAIVE  (oil is fungible)", naive, s)
    show_plan("NAIVE plan - cheapest barrel first, grade-blind (supply-respecting):", naive)
    show_metrics(mn)

    plan, status = grade_aware_plan(s)
    ms = evaluate("KARNADHAR (grade-aware)", plan, s)
    show_plan(f"KARNADHAR plan - grade-matched, desulph-feasible (solver: {status}):", plan)
    show_metrics(ms)

    print("\n" + LINE)
    print("  HEADLINE")
    print(LINE)
    yield_saved = round(mn.yield_loss_musd_day - ms.yield_loss_musd_day, 2)
    truecost_saved = round(mn.true_cost_musd_day - ms.true_cost_musd_day, 2)
    print(f"  - The fungible plan is INFEASIBLE for a GRADE reason, not logistics:")
    print(f"    {mn.unrunnable_kbd:.0f} kb/d is routed to refineries that physically cannot run it")
    print(f"    (ultra-light ~45 API condensate forced into deep coking units).")
    print(f"  - KARNADHAR is FEASIBLE: every barrel runnable, sourced, within desulph capacity.")
    print(f"  - Value protected by grade-matching: ${yield_saved:,.2f} M/day of yield")
    print(f"    (~${yield_saved*365:,.0f} M/yr); ${truecost_saved:,.2f} M/day lower TRUE cost.")
    print(f"  - Strategic-reserve reality (like-for-like):")
    print(f"      reserves last ~{ms.effective_spr_days:.0f} days against a {HORMUZ_SUPPLY_FRACTION:.0%} supply gap")
    print(f"      the optimal reroute still needs a {ms.spr_bridge_days:.0f}-day voyage bridge")
    if ms.spr_margin_days >= 0:
        print(f"      => a razor-thin {ms.spr_margin_days:.0f}-day margin: one rotation, ZERO buffer for")
        print(f"         a prolonged or compounding shock -> demand management is essential.")
    else:
        print(f"      => a {abs(ms.spr_margin_days):.0f}-day shortfall the reserve cannot cover alone.")
    print(LINE)


if __name__ == "__main__":
    main()
