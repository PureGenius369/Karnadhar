"""
KARNADHAR — Scenario library   (Evaluation Focus #3: the disruption scenario modeller)
=====================================================================================

A spread of named disruption scenarios the engine can model, escalating from a
manageable single-chokepoint event to a dual-chokepoint crisis that no reroute can
fully cover. Each uses the same Scenario mechanism (which chokepoints are cut, how
much alternate supply is withheld, the crisis price premium) — so adding a new
'what-if' is one line, exactly what a scenario modeller should allow.
"""

from engine.data import Scenario

SCENARIOS = {
    "hormuz_full": Scenario(
        "Hormuz - full closure",
        disrupted_chokepoints={"Hormuz"},
        scramble_premium_usd=5.0, cascade_closure=1.0),

    "hormuz_opec": Scenario(
        "Hormuz closure + OPEC+ supply squeeze",
        disrupted_chokepoints={"Hormuz"}, alt_supply_factor=0.60,
        scramble_premium_usd=8.0, cascade_closure=1.0),

    "dual_choke": Scenario(
        "Hormuz + Red Sea (dual chokepoint)",
        disrupted_chokepoints={"Hormuz", "Bab-el-Mandeb"},
        scramble_premium_usd=10.0, cascade_closure=1.0),

    "hormuz_war": Scenario(
        "Hormuz closure + extreme war-risk premium",
        disrupted_chokepoints={"Hormuz"}, alt_supply_factor=0.85,
        scramble_premium_usd=15.0, cascade_closure=1.0),
}
