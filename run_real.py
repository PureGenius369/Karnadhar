"""
KARNADHAR — real-model reroute demo (naive vs grade-aware) across scenarios.
Run:  python run_real.py
"""
from engine.realmodel import build_refineries, build_crudes
from engine.realopt import naive_plan, grade_plan, evaluate, scenarios

L = "=" * 80


def main():
    refs, crudes = build_refineries(), build_crudes()
    print(L)
    print("  KARNADHAR — reroute on REAL DGCIS diets (general disruption)")
    print(L)
    print(f"  {len(refs)} refineries | {len(crudes)} supplier grades | "
          f"national run {sum(r.capacity_kbd for r in refs):,.0f} kb/d\n")
    hdr = f"  {'scenario':<34}{'gap':>7}{'naive':>10}{'KARNADHAR':>12}{'unmet':>7}{'yield$':>8}"
    print(hdr); print("  " + "-" * (len(hdr) - 2))
    for scn in scenarios().values():
        nv = evaluate("naive", naive_plan(refs, crudes, scn), refs, crudes, scn)
        pl, st = grade_plan(refs, crudes, scn)
        sm = evaluate("smart", pl, refs, crudes, scn)
        nflag = "FEAS" if nv.feasible else f"INF {nv.unrunnable_kbd + nv.unmet_kbd:.0f}"
        sflag = "FEASIBLE" if sm.feasible else "INFEASIBLE"
        yp = round(nv.yield_loss_musd_day - sm.yield_loss_musd_day, 2)
        print(f"  {scn.name:<34}{nv.gap_kbd:>7.0f}{nflag:>10}{sflag:>12}"
              f"{sm.unmet_kbd:>7.0f}{yp:>8.2f}")
    print("\n" + L)
    print("  Disruption is general: chokepoint blocks AND supplier sanctions, each")
    print("  refinery's lost volume taken from its REAL import diet. Naive ignores")
    print("  grade (incl. asphaltene); KARNADHAR keeps every barrel runnable.")
    print(L)


if __name__ == "__main__":
    main()
