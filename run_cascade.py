"""
KARNADHAR — Scenario cascade demo   (Evaluation Focus #3)

Run:  python run_cascade.py     (from the karnadhar/ folder)

Shows the economic cascade for a Strait of Hormuz disruption, plus a sensitivity
sweep across severities. Every output traces back to an explicit, editable
assumption in engine/cascade.py.
"""

from engine.cascade import compute_cascade, sensitivity_table, CascadeParams

LINE = "=" * 78


def main():
    p = CascadeParams()

    print(LINE)
    print("  SCENARIO CASCADE - Strait of Hormuz disruption  (EF-3: explicit & testable)")
    print(LINE)
    print(f"  Base assumptions: Brent ${p.brent_base_usd}/bbl | Hormuz {p.hormuz_flow_mbd} Mb/d "
          f"| bypass {p.hormuz_bypass_mbd} Mb/d | FX Rs{p.fx_inr_per_usd}/$")
    print(f"  India: imports {p.india_crude_imports_mbd} Mb/d, {p.india_hormuz_share:.0%} via Hormuz "
          f"| SPR cover {p.spr_days_cover} days")

    # headline scenario: full closure
    r = compute_cascade(1.0, p)
    print("\n  >> FULL CLOSURE (100%) cascade:")
    print(f"     net global shortfall : {r.net_global_shortfall_mbd:5.1f} Mb/d  (after pipeline bypass)")
    print(f"     Brent                : ${r.brent_usd:6.1f}/bbl   (+{r.brent_change_pct:.0f}%)")
    print(f"     India import bill     : +${r.india_extra_import_bill_musd_day:,.0f} M/day")
    print(f"     retail pump price     : Rs{r.pump_inr_per_l:.1f}/L  (+Rs{r.pump_change_inr:.1f})")
    print(f"     CPI impact            : +{r.cpi_impact_pp:.2f} pp  (direct fuel; indirect adds more)")
    print(f"     GDP drag              : -{r.gdp_drag_pp:.2f} pp")
    print("\n     -- TWIN DEFICIT (India-specific, per ORF / L. Powell) --")
    print(f"     extra oil bill        : ${r.extra_annual_import_bill_usd_bn:,.0f} bn/yr  "
          f"(${r.monthly_forex_drain_usd_bn:.1f} bn/month USD outflow)")
    print(f"     current-acct deficit  : {p.baseline_cad_pct_gdp:.1f}% -> {r.stressed_cad_pct_gdp:.1f}% of GDP "
          f"(+{r.cad_widening_pct_gdp:.1f}pp) -> rupee / BoP stress")
    print("     => India (a trade-deficit economy) cannot sustain this in USD; rationing")
    print("        becomes unavoidable - the binding constraint is the balance of payments.")

    # sensitivity sweep -> the testable half of EF-3
    print("\n  >> SENSITIVITY SWEEP (vary disruption severity):")
    hdr = f"  {'closure':>8} | {'Brent$':>7} | {'+bill$bn/yr':>11} | {'CAD%GDP':>8} | {'CPI pp':>6} | {'GDP pp':>6}"
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    for row in sensitivity_table(p):
        print(f"  {row.closure_fraction:>7.0%} | {row.brent_usd:>7.0f} | "
              f"{row.extra_annual_import_bill_usd_bn:>11,.0f} | {row.stressed_cad_pct_gdp:>6.1f}% | "
              f"{row.cpi_impact_pp:>6.2f} | -{row.gdp_drag_pp:>5.2f}")

    print("\n" + LINE)
    print("  Every figure above is editable in engine/cascade.py and will be calibrated")
    print("  with a refining/energy expert. KARNADHAR's reroute (run_demo.py) is the")
    print("  mitigation that shortens how long India sits in these numbers.")
    print(LINE)


if __name__ == "__main__":
    main()
