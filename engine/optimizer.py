"""
KARNADHAR — Grade-aware crude rerouting optimizer  (THE WEDGE)
=============================================================

Two planners over the SAME disrupted-supply situation:

  1. naive_fungible_plan()  — a FAIR steelman of "oil is fungible": a price-rational
     buyer that fills each refinery's gap from the cheapest available crude first.
     It RESPECTS supply availability (so it never over-orders a barrel that doesn't
     exist) — its ONLY blind spot is grade. That isolates the wedge: any failure it
     hits is purely a crude-compatibility failure, not a logistics strawman.

  2. grade_aware_plan()     — a linear program that respects what a refinery can
     ACTUALLY run (API window, per-grade sulphur ceiling, desulphurisation blend
     capacity, real supply) and minimises TRUE cost (crude + freight + yield
     penalty), rationing scarce sour crude to the refineries that need it most.

Both plans are scored against the real constraints by the same evaluate(). The gap
— feasible vs infeasible, and yield value protected — is the result that wins the
slide. evaluate() also reports the honest strategic-reserve (SPR) runway.
"""

from __future__ import annotations
from dataclasses import dataclass, field

import pulp

from engine.data import (
    Crude, Refinery, Scenario,
    REFINERIES, SPR_DAYS_COVER, GULF_BASELINE_TRANSIT_DAYS,
    HORMUZ_SUPPLY_FRACTION,
)

FREIGHT_USD_BBL_PER_DAY = 0.04   # illustrative voyage cost; longer routes cost more


# --------------------------------------------------------------------------- #
#  Cost model (explicit and auditable)                                         #
# --------------------------------------------------------------------------- #
def yield_penalty(r: Refinery, c: Crude) -> float:
    """$/bbl value lost when a crude's API sits away from the refinery's optimum.

    A deep-conversion (coking) refinery fed light condensate starves its coker; a
    simple refinery fed heavy crude can't lift the bottoms. Either way you destroy
    product value. Modelled linearly in |API - API_opt|.
    """
    return r.yield_pen_per_api * abs(c.api - r.api_opt)


def crude_price(c: Crude, s: Scenario) -> float:
    """Per-bbl purchase price including the crisis scramble premium."""
    return c.price_usd_bbl + s.scramble_premium_usd


def landed_price(c: Crude, s: Scenario) -> float:
    """Crude + freight (what a *fungible* buyer sees)."""
    return crude_price(c, s) + FREIGHT_USD_BBL_PER_DAY * c.transit_days


def landed_true_cost(r: Refinery, c: Crude, s: Scenario) -> float:
    """Crude + freight + yield penalty (what a refinery economist actually sees)."""
    return landed_price(c, s) + yield_penalty(r, c)


def physically_runnable(r: Refinery, c: Crude) -> bool:
    """Hard configuration limit — true even for a naive buyer."""
    return (r.api_min <= c.api <= r.api_max) and (c.sulphur <= r.crude_max_sulphur)


# --------------------------------------------------------------------------- #
#  Plan container + evaluation                                                 #
# --------------------------------------------------------------------------- #
Plan = dict[str, dict[str, float]]   # refinery_name -> {crude_name -> kbd}


@dataclass
class PlanMetrics:
    label: str
    feasible: bool
    unrunnable_kbd: float                 # volume assigned to refineries that can't run it
    unmet_demand_kbd: float               # lost volume that could NOT be re-sourced at all
    window_breaches: list[str]            # "refinery <- crude" physically un-runnable
    desulph_breaches: list[str]           # refinery blend exceeds desulph capacity
    oversubscribed: dict[str, float]      # crude -> kbd demanded beyond supply (should be 0)
    crude_cost_musd_day: float            # crude bill only ($M/day)
    yield_loss_musd_day: float            # value destroyed by mis-fit slate ($M/day)
    true_cost_musd_day: float             # crude + freight + yield ($M/day)
    avg_transit_days: float
    spr_bridge_days: float                # extra voyage time beyond the Gulf baseline
    effective_spr_days: float             # honest SPR runway vs a partial-supply gap
    spr_margin_days: float                # effective cover minus the bridge


def evaluate(label: str, plan: Plan, scenario: Scenario) -> PlanMetrics:
    avail = {c.name: c.available_kbd * scenario.alt_supply_factor
             for c in scenario.available_crudes()}
    crude_by_name = {c.name: c for c in scenario.available_crudes()}
    ref_by_name = {r.name: r for r in REFINERIES}

    # supply over-subscription (kept as a guard; a fair plan should never trip it)
    grade_demand: dict[str, float] = {}
    for alloc in plan.values():
        for cname, vol in alloc.items():
            grade_demand[cname] = grade_demand.get(cname, 0.0) + vol
    oversub = {g: round(d - avail.get(g, 0.0), 1)
               for g, d in grade_demand.items() if d - avail.get(g, 0.0) > 1e-6}

    window_breaches, desulph_breaches = [], []
    unrunnable = crude_cost = yield_loss = true_cost = 0.0
    transit_weighted = vol_total = 0.0

    for rname, alloc in plan.items():
        r = ref_by_name[rname]
        vol_r = sum(alloc.values())
        blend_sulphur_mass = 0.0
        for cname, vol in alloc.items():
            c = crude_by_name[cname]
            if not physically_runnable(r, c):
                window_breaches.append(f"{rname} <- {cname} ({c.api:.0f} API)")
                unrunnable += vol
            crude_cost += vol * crude_price(c, scenario)
            yield_loss += vol * yield_penalty(r, c)
            true_cost += vol * landed_true_cost(r, c, scenario)
            blend_sulphur_mass += vol * c.sulphur
            transit_weighted += vol * c.transit_days
            vol_total += vol
        if vol_r > 0 and blend_sulphur_mass / vol_r > r.desulph_limit + 1e-6:
            desulph_breaches.append(
                f"{rname} (blend {blend_sulphur_mass/vol_r:.2f}% S > {r.desulph_limit:.2f}% cap)")

    avg_transit = transit_weighted / vol_total if vol_total else 0.0
    spr_bridge = max(0.0, avg_transit - GULF_BASELINE_TRANSIT_DAYS)

    # Honest SPR: the 9.5-day cover is days of TOTAL run, but only HORMUZ_SUPPLY_FRACTION
    # of supply is missing -> reserves stretch further against a partial gap.
    effective_spr = SPR_DAYS_COVER / HORMUZ_SUPPLY_FRACTION
    spr_margin = effective_spr - spr_bridge

    # volume that could not be re-sourced at all (supply too short / no compatible grade)
    unmet = sum(max(0.0, r.hormuz_gap_kbd - sum(plan.get(r.name, {}).values()))
                for r in REFINERIES)

    feasible = ((not oversub) and (not window_breaches)
                and (not desulph_breaches) and unmet < 1.0)

    # kbd * $/bbl = thousand-$/day; /1000 -> $M/day
    return PlanMetrics(
        label=label,
        feasible=feasible,
        unrunnable_kbd=round(unrunnable, 1),
        unmet_demand_kbd=round(unmet, 1),
        window_breaches=window_breaches,
        desulph_breaches=desulph_breaches,
        oversubscribed=oversub,
        crude_cost_musd_day=round(crude_cost / 1000, 2),
        yield_loss_musd_day=round(yield_loss / 1000, 2),
        true_cost_musd_day=round(true_cost / 1000, 2),
        avg_transit_days=round(avg_transit, 1),
        spr_bridge_days=round(spr_bridge, 1),
        effective_spr_days=round(effective_spr, 1),
        spr_margin_days=round(spr_margin, 1),
    )


# --------------------------------------------------------------------------- #
#  Planner 1: naive / fungible  (fair steelman: cheapest-first, grade-blind)   #
# --------------------------------------------------------------------------- #
def naive_fungible_plan(scenario: Scenario) -> Plan:
    """A price-rational but grade-blind buyer. Fills each refinery's gap from the
    cheapest available crude first, drawing down a SHARED supply pool so it never
    buys a barrel that doesn't exist. The only thing it ignores is whether the
    refinery can actually run the grade — which is the whole point."""
    crudes = sorted(scenario.available_crudes(), key=lambda c: landed_price(c, scenario))
    pool = {c.name: c.available_kbd * scenario.alt_supply_factor for c in crudes}

    plan: Plan = {}
    for r in REFINERIES:
        need = r.hormuz_gap_kbd
        alloc: dict[str, float] = {}
        for c in crudes:                      # cheapest first, grade-blind
            if need <= 1e-6:
                break
            take = min(need, pool[c.name])
            if take > 1e-6:
                alloc[c.name] = round(alloc.get(c.name, 0.0) + take, 1)
                pool[c.name] -= take
                need -= take
        plan[r.name] = alloc
    return plan


# --------------------------------------------------------------------------- #
#  Planner 2: grade-aware linear program  (KARNADHAR)                          #
# --------------------------------------------------------------------------- #
def grade_aware_plan(scenario: Scenario) -> tuple[Plan, str]:
    """Minimise total true cost subject to the constraints a refinery economist
    actually faces. Returns (plan, solver_status)."""
    crudes = scenario.available_crudes()
    avail = {c.name: c.available_kbd * scenario.alt_supply_factor for c in crudes}
    cby = {c.name: c for c in crudes}

    prob = pulp.LpProblem("karnadhar_reroute", pulp.LpMinimize)

    # decision vars only for physically runnable (refinery, crude) pairs
    x: dict[tuple[str, str], pulp.LpVariable] = {}
    for r in REFINERIES:
        for c in crudes:
            if physically_runnable(r, c):
                x[(r.name, c.name)] = pulp.LpVariable(
                    f"x_{r.name}_{c.name}".replace(" ", "_"), lowBound=0)

    # objective: FILL as much lost demand as possible (large penalty per unmet bbl),
    # then minimise true cost among max-fill solutions. Degrades gracefully when supply
    # is too short to cover the gap -> returns the best partial reroute, not "infeasible".
    UNMET_PENALTY = 1e6
    prob += (pulp.lpSum(var * landed_true_cost(_ref(rn), cby[cn], scenario)
                        for (rn, cn), var in x.items())
             - UNMET_PENALTY * pulp.lpSum(x.values()))

    # (a) cannot exceed each refinery's Hormuz-lost volume
    for r in REFINERIES:
        terms = [x[(r.name, c.name)] for c in crudes if (r.name, c.name) in x]
        if terms:
            prob += pulp.lpSum(terms) <= r.hormuz_gap_kbd, f"demand_{r.name}"

    # (b) cannot buy more of a grade than is available
    for c in crudes:
        terms = [x[(r.name, c.name)] for r in REFINERIES if (r.name, c.name) in x]
        if terms:
            prob += pulp.lpSum(terms) <= avail[c.name], f"supply_{c.name}"

    # (c) blend-average sulphur within desulphurisation capacity
    for r in REFINERIES:
        terms = [x[(r.name, c.name)] * cby[c.name].sulphur
                 for c in crudes if (r.name, c.name) in x]
        if terms:
            prob += pulp.lpSum(terms) <= r.desulph_limit * r.hormuz_gap_kbd, f"desulph_{r.name}"

    status = prob.solve(pulp.PULP_CBC_CMD(msg=False))

    plan: Plan = {r.name: {} for r in REFINERIES}
    for (rn, cn), var in x.items():
        v = var.value() or 0.0
        if v > 1.0:   # ignore trivial sub-1 kb/d LP splits
            plan[rn][cn] = round(v, 1)
    return plan, pulp.LpStatus[status]


# small helpers ------------------------------------------------------------- #
def _ref(name: str) -> Refinery:
    return next(r for r in REFINERIES if r.name == name)
