"""
KARNADHAR — Optimizer over the REAL model   (the wedge, on government data)
==========================================================================

Same two-planner idea, now on real DGCIS refineries/diets and general disruption
(block any chokepoint OR sanction any supplier):

  naive_plan   — grade-blind: fill each refinery's real lost volume from the
                 cheapest available barrels (respects supply; ignores fit).
  grade_plan   — two-stage lexicographic LP:
                   stage 1  maximise total re-sourced volume,
                   stage 2  at that volume, minimise landed + yield cost —
                 assigning only crude a refinery can actually run (API window,
                 sulphur ceiling, blend desulph cap, ASPHALTENE cap). Blend caps
                 are enforced relative to the volume actually assigned, so they
                 stay valid even when supply is scarce. Stage-2 duals give the
                 SHADOW PRICE of every scarce grade — what one extra kb/d of a
                 supplier is worth to India, straight from the optimizer.

evaluate() scores any plan against the real constraints, including the honest
strategic-reserve runway and the tanker-fleet (VLCC-equivalent) cost of longer
voyages — rerouting is not free even when barrels exist.
"""

from __future__ import annotations
from dataclasses import dataclass
import pulp

from engine.realmodel import (
    Crude, Refinery, Disruption, build_refineries, build_crudes,
)

FREIGHT = 0.04            # $/bbl per voyage day (long-run average charter cost)
SPR_DAYS = 9.5
GULF_BASELINE_TRANSIT = 6
# Plans are reported at 0.1 kb/d, so scoring uses a rounding-aware tolerance on
# blend averages instead of an exact boundary test (an optimum AT the limit is
# feasible, not a breach).
BLEND_TOL = 0.02
# Tanker math: a VLCC lifts ~2 Mbbl; a round trip is 2x voyage + ~4 port days.
VLCC_BBL = 2_000_000
PORT_DAYS = 4


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
    usable_short_kbd: float      # unmet + un-runnable: the REAL shortfall
    breaches: list
    crude_cost_musd_day: float
    yield_loss_musd_day: float
    true_cost_musd_day: float
    avg_transit_days: float
    spr_bridge_days: float
    effective_spr_days: float
    spr_margin_days: float
    fleet_vlcc: float            # VLCC-equivalents tied up sustaining this plan
    extra_vlcc: float            # ...beyond the Gulf-baseline fleet (ton-mile cost)


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
            if blend_s / vol > r.desulph_limit + BLEND_TOL:
                breaches.append(f"{rn} desulph {blend_s/vol:.2f}>{r.desulph_limit}")
            if blend_a / vol > r.max_asphaltene + BLEND_TOL:
                breaches.append(f"{rn} asphaltene {blend_a/vol:.1f}>{r.max_asphaltene}")
    unmet = sum(max(0.0, gap[r.name] - sum(plan.get(r.name, {}).values())) for r in refs)
    avg_t = tw / vt if vt else 0.0
    bridge = max(0.0, avg_t - GULF_BASELINE_TRANSIT)
    eff_spr = SPR_DAYS / hormuz_frac if hormuz_frac else 999
    # tanker-fleet cost of the plan: longer voyages tie up more ships for the
    # SAME barrels/day (the ton-mile effect a fungible view never prices)
    roundtrip = 2 * avg_t + PORT_DAYS
    fleet = filled * 1000 * roundtrip / VLCC_BBL if filled else 0.0
    base_fleet = filled * 1000 * (2 * GULF_BASELINE_TRANSIT + PORT_DAYS) / VLCC_BBL if filled else 0.0
    return Metrics(
        label, (not breaches and unmet < 1), round(total_gap, 1), round(filled, 1),
        round(unmet, 1), round(unrun, 1), round(unmet + unrun, 1), breaches,
        round(crude_cost / 1000, 2), round(yloss / 1000, 2), round(tcost / 1000, 2),
        round(avg_t, 1), round(bridge, 1), round(eff_spr, 1), round(eff_spr - bridge, 1),
        round(fleet, 1), round(fleet - base_fleet, 1))


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


def _blend_constraints(prob, x, refs, av):
    """Blend quality caps RELATIVE to assigned volume (valid under scarcity)."""
    for r in refs:
        pairs = [(c, x[(r.name, c.name)]) for c in av if (r.name, c.name) in x]
        if not pairs:
            continue
        vol = pulp.lpSum(v for _, v in pairs)
        prob += pulp.lpSum(v * c.sulphur for c, v in pairs) <= r.desulph_limit * vol, \
            f"blendS_{r.name.replace(' ', '_')}"
        prob += pulp.lpSum(v * c.asphaltene for c, v in pairs) <= r.max_asphaltene * vol, \
            f"blendA_{r.name.replace(' ', '_')}"


def grade_plan(refs, crudes, d) -> tuple[Plan, str, list]:
    """Two-stage lexicographic LP. Returns (plan, status, marginals).

    marginals = [{"source", "grade", "shadow_kusd_per_kbd"}] — the stage-2 dual
    value of each BINDING supply constraint: what one extra kb/d of that grade
    would save India per day. Falls out of the LP for free; no extra model.
    """
    av = d.available(crudes)
    avail = {c.name: c.available_kbd * d.alt_supply_factor for c in av}
    cby = {c.name: c for c in av}
    gap = _gap(refs, d)

    def _base(sense):
        prob = pulp.LpProblem("reroute", sense)
        x = {(r.name, c.name): pulp.LpVariable(f"x_{i}_{j}", lowBound=0)
             for i, r in enumerate(refs) for j, c in enumerate(av) if runnable(r, c)}
        for r in refs:
            t = [x[(r.name, c.name)] for c in av if (r.name, c.name) in x]
            if t:
                prob += pulp.lpSum(t) <= gap[r.name], f"gap_{r.name.replace(' ', '_')}"
        for c in av:
            t = [x[(r.name, c.name)] for r in refs if (r.name, c.name) in x]
            if t:
                prob += pulp.lpSum(t) <= avail[c.name], f"sup_{c.name.replace(' ', '_')}"
        _blend_constraints(prob, x, refs, av)
        return prob, x

    rby = {r.name: r for r in refs}

    # stage 1 — how much CAN be re-sourced at all?
    p1, x1 = _base(pulp.LpMaximize)
    p1 += pulp.lpSum(x1.values())
    p1.solve(pulp.PULP_CBC_CMD(msg=False))
    max_fill = pulp.value(p1.objective) or 0.0

    # stage 2 — at that volume, the cheapest feasible assignment
    p2, x = _base(pulp.LpMinimize)
    p2 += pulp.lpSum(v * (landed(cby[cn], d) + yield_pen(rby[rn], cby[cn]))
                     for (rn, cn), v in x.items())
    p2 += pulp.lpSum(x.values()) >= max_fill - 1e-4, "fill_lock"
    st = p2.solve(pulp.PULP_CBC_CMD(msg=False))

    plan = {r.name: {} for r in refs}
    for (rn, cn), v in x.items():
        val = v.value() or 0
        if val > 0.05:
            plan[rn][cn] = round(val, 1)

    # shadow prices of scarce supply (stage-2 duals; <=0 for a <= constraint,
    # so -pi = $k/day saved per extra kb/d made available)
    marginals = []
    for name, con in p2.constraints.items():
        if name.startswith("sup_") and con.pi is not None and con.pi < -1e-6:
            country = name[4:].replace("_", " ")
            c = cby.get(country)
            if c:
                marginals.append({"source": country.title(), "grade": c.grade,
                                  "avail_kbd": round(avail[c.name], 1),
                                  "shadow_kusd_per_kbd": round(-con.pi, 1)})
    marginals.sort(key=lambda m: -m["shadow_kusd_per_kbd"])
    return plan, pulp.LpStatus[st], marginals


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
