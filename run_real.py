"""
KARNADHAR — real-model reroute demo (naive vs grade-aware) across scenarios.
Run:  python run_real.py
"""
from engine.realmodel import build_refineries, build_crudes
from engine.realopt import naive_plan, grade_plan, evaluate, scenarios

L = "=" * 96


def main():
    refs, crudes = build_refineries(), build_crudes()
    print(L)
    print("  KARNADHAR - reroute on REAL DGCIS diets (general disruption)")
    print(L)
    print(f"  {len(refs)} refineries | {len(crudes)} supplier grades | "
          f"national run {sum(r.capacity_kbd for r in refs):,.0f} kb/d\n")
    hdr = (f"  {'scenario':<32}{'gap':>7}{'naive short*':>13}{'KARN short':>11}"
           f"{'yield$':>8}{'+VLCC':>7}")
    print(hdr); print("  " + "-" * (len(hdr) - 2))
    results = {}
    for key, scn in scenarios().items():
        nv = evaluate("naive", naive_plan(refs, crudes, scn), refs, crudes, scn)
        pl, st, marg = grade_plan(refs, crudes, scn)
        sm = evaluate("smart", pl, refs, crudes, scn)
        results[key] = (nv, sm, marg)
        yp = round(nv.yield_loss_musd_day - sm.yield_loss_musd_day, 2)
        print(f"  {scn.name:<32}{nv.gap_kbd:>7.0f}"
              f"{nv.usable_short_kbd:>10.0f} {'INF' if not nv.feasible else '   '}"
              f"{sm.usable_short_kbd:>8.0f} {'ok ' if sm.feasible else 'PART'}"
              f"{yp:>7.2f}{sm.extra_vlcc:>7.0f}")
    print("\n  * usable shortfall = unmet + UN-RUNNABLE barrels. The naive plan often")
    print("    'fills' the gap with crude the refinery physically cannot process -")
    print("    KARNADHAR counts only barrels that actually run.")

    nv, sm, marg = results["hormuz"]
    print("\n" + L)
    print("  HORMUZ CLOSURE - what the optimizer itself tells the negotiator")
    print(L)
    print(f"  Naive breaches ({len(nv.breaches)}):")
    for b in nv.breaches[:4]:
        print(f"    - {b}")
    print(f"\n  Tanker reality of the reroute (ton-mile effect):")
    print(f"    average voyage {sm.avg_transit_days:.0f} days (Gulf baseline 6) -> "
          f"fleet {sm.fleet_vlcc:.0f} VLCC-equiv, +{sm.extra_vlcc:.0f} vs baseline")
    print(f"\n  Shadow prices (stage-2 LP duals) - marginal value of ONE more kb/d")
    print(f"  (material suppliers, availability >= 50 kb/d):")
    mat = [m for m in marg if m["avail_kbd"] >= 50]
    for m in mat[:5]:
        print(f"    {m['source']:<14} {m['grade']:<15} ${m['shadow_kusd_per_kbd']:,.1f}k/day")
    niche = len(marg) - len(mat)
    if niche:
        print(f"    (+{niche} niche suppliers binding below 50 kb/d)")
    print("  -> scarcity is in heavy-sour COKER feed, not in barrels: the wedge, priced.")
    print(L)


if __name__ == "__main__":
    main()
