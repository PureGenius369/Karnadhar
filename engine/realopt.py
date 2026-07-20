"""
KARNADHAR — Optimizer over the REAL model   (the wedge, on government data)
==========================================================================

Same two-planner idea, now on real DGCIS refineries/diets and general disruption
(block any chokepoint OR sanction any supplier):

  naive_plan   — grade-blind: fill each refinery's real lost volume from the
                 cheapest available barrels (respects supply; ignores fit).
  grade_plan   — LP that only assigns crude a refinery can actually run
                 (API window, sulphur ceiling, desulph blend cap, ASPHALTENE cap)
                 and re-sources as much as possible at least yield cost.

evaluate() scores any plan against the real constraints, including the honest
strategic-reserve runway.
"""

from __future__ import annotations
from dataclasses import dataclass
import pulp

from engine.realmodel import (
    Crude, Refinery, Disruption, build_refineries, build_crudes,
)

FREIGHT = 0.04
SPR_DAYS = 9.5
GULF_BASELINE_TRANSIT = 6


def landed(c: Crude, d: Disruption) -> float:
    return c.price_usd_bbl + d.scramble_premium_usd + FREIGHT * c.transit_days


def yield_pen(r: Refinery, c: Crude) -> float:
    return r.yield_pen_per_api * abs(c.api - r.api_opt)


def runnable(r: Refinery, c: Crude) -> bool:
    return (r.api_min <= c.api <= r.api_max
            and c.sulphur <= r.max_sulphur
            and c.asphaltene <= r.max_asphaltene + 1e-6)


Plan = dict          # refinery -> {crude: kbd}


@dataclass
class Metrics:
    label: str
    feasible: bool
    gap_kbd: float
    filled_kbd: float
    unmet_kbd: float
    unrunnable_kbd: float
    breaches: list
    crude_cost_musd_day: float
    yield_loss_musd_day: float
    true_cost_musd_day: float
    avg_transit_days: float
    spr_bridge_days: float
    effective_spr_days: float
    spr_margin_days: float


def _gap(refs, d):
    return {r.name: r.volume_at_risk(d.blocked_chokepoints, d.sanctioned_countries)
            for r in refs}


def evaluate(label, plan, refs, crudes, d) -> Metrics:
    rby = {r.name: r for r in refs}
    cby = {c.name: c for c in crudes}
    gap = _gap(refs, d)
    total_gap = sum(gap.values())
    national_run = sum(r.capacity_kbd for r in refs)
    hormuz_frac = total_gap / national_run if national_run else 0.0

    breaches, unrun, filled = [], 0.0, 0.0
    crude_cost = yloss = tcost = tw = vt = 0.0
    for rn, alloc in plan.items():
        r = rby[rn]; blend_s = blend_a = 0.0; vol = sum(alloc.values()); filled += vol
        for cn, v in alloc.items():
            c = cby[cn]
            if not runnable(r, c):
                breaches.append(f"{rn} <- {c.grade} (API {c.api:.0f}/S {c.sulphur}/Asph {c.asphaltene})")
                unrun += v
            crude_cost += v * (c.price_usd_bbl + d.scramble_premium_usd)
            yloss += v * yield_pen(r, c)
            tcost += v * (landed(c, d) + yield_pen(r, c))
            blend_s += v * c.sulphur; blend_a += v * c.asphaltene
            tw += v * c.transit_days; vt += v
        if vol > 0:
            if blend_s / vol > r.desulph_limit + 1e-6:
                breaches.append(f"{rn} desulph {blend_s/vol:.2f}>{r.desulph_limit}")
            if blend_a / vol > r.max_asphaltene + 1e-6:
                breaches.append(f"{rn} asphaltene {blend_a/vol:.1f}>{r.max_asphaltene}")
    unmet = sum(max(0.0, gap[r.name] - sum(plan.get(r.name, {}).values())) for r in refs)
    avg_t = tw / vt if vt else 0.0
    bridge = max(0.0, avg_t - GULF_BASELINE_TRANSIT)
    eff_spr = SPR_DAYS / hormuz_frac if hormuz_frac else 999
    return Metrics(
        label, (not breaches and unmet < 1), round(total_gap, 1), round(filled, 1),
        round(unmet, 1), round(unrun, 1), breaches,
        round(crude_cost / 1000, 2), round(yloss / 1000, 2), round(tcost / 1000, 2),
        round(avg_t, 1), round(bridge, 1), round(eff_spr, 1), round(eff_spr - bridge, 1))


def naive_plan(refs, crudes, d) -> Plan:
    avail = {c.name: c.available_kbd * d.alt_supply_factor for c in d.available(crudes)}
    order = sorted(d.available(crudes), key=lambda c: landed(c, d))
    gap = _gap(refs, d); plan = {}
    for r in refs:
        need = gap[r.name]; alloc = {}
        for c in order:
            if need <= 1e-6:
                break
            take = min(need, avail[c.name])
            if take > 1e-6:
                alloc[c.name] = round(alloc.get(c.name, 0) + take, 1)
                avail[c.name] -= take; need -= take
        plan[r.name] = alloc
    return plan


def grade_plan(refs, crudes, d) -> tuple[Plan, str]:
    av = d.available(crudes)
    avail = {c.name: c.available_kbd * d.alt_supply_factor for c in av}
    cby = {c.name: c for c in av}
    gap = _gap(refs, d)
    prob = pulp.LpProblem("reroute", pulp.LpMinimize)
    x = {(r.name, c.name): pulp.LpVariable(f"x_{i}_{j}", lowBound=0)
         for i, r in enumerate(refs) for j, c in enumerate(av) if runnable(r, c)}
    rby = {r.name: r for r in refs}
    prob += (pulp.lpSum(v * (landed(cby[cn], d) + yield_pen(rby[rn], cby[cn]))
                        for (rn, cn), v in x.items())
             - 1e6 * pulp.lpSum(x.values()))
    for r in refs:
        t = [x[(r.name, c.name)] for c in av if (r.name, c.name) in x]
        if t:
            prob += pulp.lpSum(t) <= gap[r.name]
    for c in av:
        t = [x[(r.name, c.name)] for r in refs if (r.name, c.name) in x]
        if t:
            prob += pulp.lpSum(t) <= avail[c.name]
    for r in refs:
        ts = [x[(r.name, c.name)] * cby[c.name].sulphur for c in av if (r.name, c.name) in x]
        ta = [x[(r.name, c.name)] * cby[c.name].asphaltene for c in av if (r.name, c.name) in x]
        if ts:
            prob += pulp.lpSum(ts) <= r.desulph_limit * gap[r.name]
            prob += pulp.lpSum(ta) <= r.max_asphaltene * gap[r.name]
    st = prob.solve(pulp.PULP_CBC_CMD(msg=False))
    plan = {r.name: {} for r in refs}
    for (rn, cn), v in x.items():
        val = v.value() or 0
        if val > 1:
            plan[rn][cn] = round(val, 1)
    return plan, pulp.LpStatus[st]


# ready-made scenarios on the real model
def scenarios() -> dict:
    return {
        "hormuz": Disruption("Strait of Hormuz closure", blocked_chokepoints={"Hormuz"},
                             scramble_premium_usd=5),
        "hormuz_opec": Disruption("Hormuz + OPEC+ squeeze", blocked_chokepoints={"Hormuz"},
                                  alt_supply_factor=0.6, scramble_premium_usd=8),
        "russia_sanction": Disruption("Russia fully sanctioned", sanctioned_countries={"RUSSIA"},
                                      scramble_premium_usd=6),
        "hormuz_russia": Disruption("Hormuz closure + Russia sanctioned",
                                    blocked_chokepoints={"Hormuz"}, sanctioned_countries={"RUSSIA"},
                                    scramble_premium_usd=12),
    }
