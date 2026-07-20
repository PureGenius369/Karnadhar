"""
KARNADHAR — Scenario cascade model   (Evaluation Focus #3: scenario fidelity)
============================================================================

A *glass-box* economic cascade for a chokepoint disruption:

    closure %  ->  net global supply shortfall (after pipeline bypass)
               ->  Brent price shock
               ->  India crude import-bill increase
               ->  retail pump price (INR/L)
               ->  CPI impact
               ->  GDP drag
               +   strategic-reserve runway

The brief is explicit: *"scenario model fidelity (assumptions must be explicit
and testable)."* So EVERY number below is a single named, editable parameter with
a source note, the maths is transparent (no black box), and `sensitivity_table()`
makes the whole model testable by sweeping the disruption severity. Any value can
be corrected by a domain expert (see outreach: Naiya / PDEU) without touching the
logic.

Illustrative base values (replace with sourced data in Phase 1):
  - World liquids supply ~102 Mb/d (IEA)
  - Hormuz transit ~20 Mb/d; pipeline bypass ~6.5 Mb/d (Saudi Petroline ~5 + UAE Fujairah ~1.5) (EIA)
  - India crude imports ~4.6 Mb/d, ~40% via Hormuz (PPAC)
  - GDP drag ~0.1-0.2 %/yr per sustained +$10/bbl (RBI / MoF range)
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class CascadeParams:
    # --- global oil market ---
    global_supply_mbd: float = 102.0
    hormuz_flow_mbd: float = 20.0
    hormuz_bypass_mbd: float = 6.5            # Saudi Petroline + UAE Fujairah spare capacity
    brent_base_usd: float = 82.0
    # $/bbl added per 1 Mb/d of *net* global shortfall. Linear is a documented
    # simplification (the real curve is convex at extremes) — calibrate with an expert.
    price_sensitivity_usd_per_mbd: float = 8.0

    # --- India fundamentals ---
    india_crude_imports_mbd: float = 4.84   # DGCIS 2024 actual
    india_hormuz_share: float = 0.40
    fx_inr_per_usd: float = 83.5
    litres_per_bbl: float = 159.0
    pump_base_inr_per_l: float = 100.0
    # only the crude component of the pump price moves; taxes & margins are ~fixed
    crude_pass_through: float = 0.45

    # --- macro ---
    cpi_fuel_weight: float = 0.08            # direct fuel + transport-fuel weight in CPI basket
    gdp_drag_pp_per_10usd: float = 0.13      # %GDP per sustained +$10/bbl

    # --- India external vulnerability: the TWIN-DEFICIT problem ----------------
    # Per Lydia Powell (ORF): India, unlike trade-surplus Japan/Korea, cannot
    # sustain USD payment for expensive crude -> current-account + fiscal deficit.
    # The real constraint is the balance of payments, not the barrels.
    india_gdp_usd_bn: float = 3900.0         # ~FY24 nominal GDP
    india_forex_reserves_usd_bn: float = 650.0
    baseline_cad_pct_gdp: float = 1.2        # recent current-account deficit (% GDP)

    # --- strategic reserves ---
    # India's SPR is VOLUNTARY insurance: India is not a full IEA member, so the
    # IEA 90-day reserve mandate does not bind it. 9.5 days is thin, not a floor.
    spr_days_cover: float = 9.5


@dataclass
class CascadeResult:
    closure_fraction: float
    net_global_shortfall_mbd: float
    brent_usd: float
    brent_change_pct: float
    india_extra_import_bill_musd_day: float
    pump_inr_per_l: float
    pump_change_inr: float
    cpi_impact_pp: float
    gdp_drag_pp: float
    extra_annual_import_bill_usd_bn: float
    cad_widening_pct_gdp: float
    stressed_cad_pct_gdp: float
    monthly_forex_drain_usd_bn: float
    spr_days_cover: float


def compute_cascade(closure_fraction: float,
                    p: CascadeParams = CascadeParams()) -> CascadeResult:
    """Run the cascade for a given Hormuz closure fraction (0.0-1.0)."""
    # 1) net global shortfall, after what pipelines can bypass the Strait
    gross_at_risk = p.hormuz_flow_mbd * closure_fraction
    net_short = max(0.0, gross_at_risk - p.hormuz_bypass_mbd)

    # 2) Brent shock (linear in the net shortfall; sensitivity is an explicit parameter)
    brent_delta = net_short * p.price_sensitivity_usd_per_mbd
    brent_new = p.brent_base_usd + brent_delta
    brent_pct = brent_delta / p.brent_base_usd * 100

    # 3) India extra crude import bill:  Mb/d * $/bbl = $M/day
    extra_bill = p.india_crude_imports_mbd * brent_delta

    # 4) retail pump pass-through (INR/L): convert $/bbl -> $/L -> INR/L, dampened
    pump_delta = (brent_delta / p.litres_per_bbl) * p.fx_inr_per_usd * p.crude_pass_through
    pump_new = p.pump_base_inr_per_l + pump_delta

    # 5) CPI impact (percentage points) = pump %change * fuel weight in basket
    pump_pct = pump_delta / p.pump_base_inr_per_l
    cpi_pp = pump_pct * p.cpi_fuel_weight * 100

    # 6) GDP drag (percentage points)
    gdp_pp = (brent_delta / 10.0) * p.gdp_drag_pp_per_10usd

    # 7) TWIN-DEFICIT / balance of payments (the India-specific vulnerability):
    #    the extra crude bill is paid in USD and lands straight on the current
    #    account; India (a trade-deficit economy) cannot sustain it for long.
    extra_annual_bn = p.india_crude_imports_mbd * brent_delta * 365 / 1000.0   # $bn/yr
    cad_widen_pct = extra_annual_bn / p.india_gdp_usd_bn * 100.0               # +pp of GDP
    stressed_cad = p.baseline_cad_pct_gdp + cad_widen_pct
    monthly_drain = p.india_crude_imports_mbd * brent_delta * 30 / 1000.0      # $bn/month

    return CascadeResult(
        closure_fraction=closure_fraction,
        net_global_shortfall_mbd=round(net_short, 2),
        brent_usd=round(brent_new, 1),
        brent_change_pct=round(brent_pct, 1),
        india_extra_import_bill_musd_day=round(extra_bill, 1),
        pump_inr_per_l=round(pump_new, 1),
        pump_change_inr=round(pump_delta, 1),
        cpi_impact_pp=round(cpi_pp, 2),
        gdp_drag_pp=round(gdp_pp, 2),
        extra_annual_import_bill_usd_bn=round(extra_annual_bn, 1),
        cad_widening_pct_gdp=round(cad_widen_pct, 2),
        stressed_cad_pct_gdp=round(stressed_cad, 2),
        monthly_forex_drain_usd_bn=round(monthly_drain, 1),
        spr_days_cover=p.spr_days_cover,
    )


def sensitivity_table(p: CascadeParams = CascadeParams(),
                      fractions=(0.25, 0.50, 0.75, 1.00)) -> list[CascadeResult]:
    """Sweep disruption severity -> the 'testable' half of EF-3."""
    return [compute_cascade(f, p) for f in fractions]
