"""
KARNADHAR — Strategic Reserve drawdown scheduler   (brief: "SPR Optimisation Agent")
====================================================================================

Glass-box decision support for the SPR question policymakers actually face during
a disruption: *at what rate do we draw, for how long, and what remains for the
next shock?*

Basis (explicit, editable):
  * SPR cover is expressed in DAYS OF IMPORTS (matching the engine's 9.5-day
    figure and the brief). Total stock = spr_days x national imports.
  * The window that must be bridged is the reroute's voyage bridge — the extra
    days before re-sourced cargoes actually arrive (from the optimizer).
  * The gap to cover is the honest post-reroute unmet demand (kb/d), not the
    gross disruption — the optimizer already re-sourced everything runnable.

Outputs one of three schedules:
  hold        — reroute covers demand; keep the SPR as insurance.
  bridge      — draw at the unmet rate through the bridge; report depletion %.
  ration      — even max draw cannot cover the gap through the bridge; report
                the sustainable rate AND the residual demand-management need.
"""

from __future__ import annotations
from dataclasses import dataclass

REPLENISH_RATE_KBD = 150.0     # post-crisis refill rate assumption (imports surplus)


@dataclass(frozen=True)
class DrawdownPlan:
    verdict: str                # hold | bridge | ration
    spr_total_kbbl: float       # thousand barrels in reserve
    bridge_days: float          # window the schedule must survive
    unmet_kbd: float            # post-reroute gap to cover
    draw_rate_kbd: float        # recommended draw rate
    cover_days: float           # how long that rate is sustainable
    depletion_pct: float        # % of SPR consumed by the schedule
    demand_mgmt_kbd: float      # residual gap policy must cut (ration only)
    replenish_days: float       # days to refill what was drawn, post-crisis

    def summary(self) -> str:
        if self.verdict == "hold":
            return ("HOLD - reroute covers demand; SPR stays whole as insurance "
                    f"({self.spr_total_kbbl:,.0f} kbbl intact)")
        if self.verdict == "bridge":
            return (f"BRIDGE - draw {self.draw_rate_kbd:,.0f} kb/d for "
                    f"{self.bridge_days:.0f} days ({self.depletion_pct:.0f}% of SPR), "
                    f"refill in ~{self.replenish_days:.0f} days")
        return (f"RATION - max sustainable draw {self.draw_rate_kbd:,.0f} kb/d still "
                f"leaves {self.demand_mgmt_kbd:,.0f} kb/d for demand management "
                f"({self.depletion_pct:.0f}% of SPR consumed)")


def plan_drawdown(unmet_kbd: float, bridge_days: float, imports_kbd: float,
                  spr_days: float = 9.5) -> DrawdownPlan:
    total = spr_days * imports_kbd                      # kbbl
    unmet = max(0.0, unmet_kbd)
    bridge = max(0.0, bridge_days)
    if unmet < 1 or bridge <= 0:
        return DrawdownPlan("hold", round(total), round(bridge, 1), round(unmet, 1),
                            0.0, 999.0, 0.0, 0.0, 0.0)
    full_cover_days = total / unmet
    if full_cover_days >= bridge:
        drawn = unmet * bridge
        return DrawdownPlan(
            "bridge", round(total), round(bridge, 1), round(unmet, 1),
            round(unmet, 1), round(full_cover_days, 1),
            round(drawn / total * 100, 1), 0.0,
            round(drawn / REPLENISH_RATE_KBD, 1))
    even_rate = total / bridge
    return DrawdownPlan(
        "ration", round(total), round(bridge, 1), round(unmet, 1),
        round(even_rate, 1), round(bridge, 1), 100.0,
        round(unmet - even_rate, 1),
        round(total / REPLENISH_RATE_KBD, 1))
