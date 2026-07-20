"""
KARNADHAR — Multi-commodity import-resilience module
====================================================

The workshop's own framing: "not only just for crude oil, but any material."
This module generalises the KARNADHAR framework to India's other strategic
imports as a SCREENING tier (crude remains the deep-dive tier with the
grade-aware LP; every other commodity gets the same anatomy):

    import dependence x supplier concentration x chokepoint exposure
    x substitution rigidity  ->  Import Vulnerability Index (IVX, 0-100)

`substitution_rigidity` is the generalisation of the crude-oil "grade" insight:
how locked-in the sourcing is when disrupted —
    pharma APIs  0.90  (regulatory re-qualification takes 12-24 months)
    semiconds    0.85  (qualified fabs, design lock-in)
    crude oil    0.65  (refinery grade compatibility — from OUR deep model)
    LNG          0.55  (regas terminals + term contracts, but spot exists)
    fertiliser   0.50  (seasonal criticality; some product switching)
    coking coal  0.45  (blend flexibility across met coals)
    edible oil   0.35  (palm <-> soy <-> sunflower swap at a price)

Figures are cited public approximations (FY24-25: DGCIS/commerce ministry trade
data, PPAC (energy), FAI (fertiliser), SEA (edible oil), industry reports) —
same explicit-and-editable standard as the rest of the engine. The crude row's
chokepoint exposure (46%) comes from OUR DGCIS-derived model, not a report.
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Commodity:
    key: str
    name: str
    import_dependence: float          # share of national consumption imported
    annual_import_usd_bn: float       # approx annual import bill
    suppliers: dict                   # country -> share of imports
    chokepoints: dict                 # chokepoint -> share of imports transiting
    substitution_rigidity: float      # 0..1 — how locked-in sourcing is
    stockpile_days: float             # strategic/system inventory cover

    @property
    def supplier_hhi(self) -> float:
        """Herfindahl concentration of suppliers (0..1).

        The residual "OTHERS" bucket is excluded: it is many small suppliers,
        not one — counting it as a single supplier would overstate concentration.
        """
        return round(sum(s * s for k, s in self.suppliers.items()
                         if k.upper() != "OTHERS"), 3)

    @property
    def max_chokepoint(self) -> float:
        return max(self.chokepoints.values(), default=0.0)

    @property
    def vulnerability_index(self) -> float:
        """Glass-box IVX 0-100. Weights explicit; stockpile gives up to 30% relief."""
        core = (0.30 * self.import_dependence
                + 0.25 * min(1.0, self.supplier_hhi / 0.5)   # HHI 0.5+ = max concern
                + 0.25 * self.max_chokepoint
                + 0.20 * self.substitution_rigidity)
        relief = 1.0 - 0.30 * min(self.stockpile_days, 90) / 90
        return round(core * relief * 100, 1)

    def affected_share(self, blocked_chokepoints: set, sanctioned: set) -> float:
        """Upper-bound share of imports hit by a disruption (capped at 100%).
        Screening approximation: chokepoint shares + sanctioned-supplier shares."""
        cp = sum(v for k, v in self.chokepoints.items() if k in blocked_chokepoints)
        sup = sum(v for k, v in self.suppliers.items() if k.upper() in sanctioned)
        return round(min(1.0, cp + sup), 3)


COMMODITIES = [
    Commodity("crude_oil", "Crude oil", 0.88, 157.0,
              {"RUSSIA": 0.36, "IRAQ": 0.20, "SAUDI ARAB": 0.13, "U ARAB EMTS": 0.09,
               "U S A": 0.04, "OTHERS": 0.18},
              {"Hormuz": 0.46},                       # DERIVED from our DGCIS model
              0.65, 9.5),
    Commodity("lng", "LNG (natural gas)", 0.48, 13.3,
              {"QATAR": 0.42, "U S A": 0.14, "U ARAB EMTS": 0.11, "ANGOLA": 0.06,
               "OTHERS": 0.27},
              {"Hormuz": 0.53},                       # Qatar + UAE cargoes
              0.55, 3),
    Commodity("pharma_api", "Pharma APIs / KSMs", 0.70, 4.6,
              {"CHINA": 0.70, "OTHERS": 0.30},
              {"Malacca": 0.70},
              0.90, 75),
    Commodity("semiconductors", "Semiconductors", 0.90, 18.0,
              {"CHINA": 0.35, "TAIWAN": 0.18, "KOREA RP": 0.14, "SINGAPORE": 0.12,
               "OTHERS": 0.21},
              {"Malacca": 0.79},
              0.85, 30),
    Commodity("edible_oil", "Edible oils", 0.57, 15.5,
              {"INDONESIA": 0.38, "MALAYSIA": 0.15, "ARGENTINA": 0.12,
               "RUSSIA": 0.09, "UKRAINE": 0.09, "OTHERS": 0.17},
              {"Malacca": 0.53},                      # palm via Malacca
              0.35, 45),
    Commodity("fertiliser", "Fertilisers (urea/DAP/MOP)", 0.35, 10.2,
              {"CHINA": 0.20, "RUSSIA": 0.20, "SAUDI ARAB": 0.15, "MOROCCO": 0.10,
               "OMAN": 0.10, "OTHERS": 0.25},
              {"Hormuz": 0.30, "Malacca": 0.20},
              0.50, 60),
    Commodity("coking_coal", "Coking coal", 0.85, 12.1,
              {"AUSTRALIA": 0.55, "U S A": 0.15, "RUSSIA": 0.15, "OTHERS": 0.15},
              {},                                     # open-ocean routes — no strait
              0.45, 30),
    Commodity("solar_modules", "Solar PV modules/cells", 0.80, 7.0,
              {"CHINA": 0.80, "OTHERS": 0.20},
              {"Malacca": 0.80},
              0.60, 60),
]

BY_KEY = {c.key: c for c in COMMODITIES}


def screen(blocked_chokepoints: set = frozenset(), sanctioned: set = frozenset()):
    """Rank commodities by how hard a disruption hits them."""
    rows = []
    for c in COMMODITIES:
        rows.append({
            "key": c.key, "name": c.name,
            "dependence": c.import_dependence,
            "annual_usd_bn": c.annual_import_usd_bn,
            "hhi": c.supplier_hhi,
            "rigidity": c.substitution_rigidity,
            "stockpile_days": c.stockpile_days,
            "ivx": c.vulnerability_index,
            "affected": c.affected_share(set(blocked_chokepoints), set(sanctioned)),
            "suppliers": c.suppliers, "chokepoints": c.chokepoints,
        })
    return sorted(rows, key=lambda r: -r["affected"])
