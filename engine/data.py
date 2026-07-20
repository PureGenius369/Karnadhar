"""
KARNADHAR — Domain data layer
=============================

The defensible core rests on ONE refining truth almost every other team misses:
**crude oil is not fungible.** A refinery is configured for a specific crude *slate*
(API gravity = light/heavy, sulphur = sweet/sour, plus the desulphurisation and
coker capacity to handle it). When a chokepoint like the Strait of Hormuz is
disrupted you cannot pour any barrel into any refinery.

This module encodes that reality. Every number is ILLUSTRATIVE but derived from
public references; the *method* is the point, and each assumption is explicit so a
domain expert can correct any single value without breaking the model.

The numbers are deliberately set to the REAL post-Hormuz structure:
  - The abundant alternates are mostly LIGHT SWEET (wrong slate for India's many
    sour/heavy coking refineries) and take 3-6x longer to sail.
  - The only medium-sour alternate (Urals) is supply-constrained.
  - One alternate (CPC Blend, ~45 API condensate) is so light that NO disrupted-case
    refinery can run it as feed -> this is what makes a 'fungible' plan physically
    impossible, for grade reasons, not logistics.

Sources to cite in the deck (swap illustrative values for these as verified):
  - Crude assays (API/sulphur): crudemonitor.ca, BP/ENI/ExxonMobil assay libraries
  - Refinery capacity & config: PPAC (ppac.gov.in), company annual reports
  - Strategic reserves: ISPRL (Vizag 1.33 + Mangalore 1.5 + Padur 2.5 MMT ~= 9.5 days)
  - Chokepoint flows: EIA World Oil Transit Chokepoints (~20 Mb/d via Hormuz)
"""

from __future__ import annotations
from dataclasses import dataclass, field


# --------------------------------------------------------------------------- #
#  Crude grades (the "slate" building blocks)                                  #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Crude:
    name: str
    origin: str
    api: float                # API gravity (deg). Higher = lighter.
    sulphur: float            # wt %. Higher = more sour.
    price_usd_bbl: float      # illustrative landed-ish spot level (crisis-elevated)
    chokepoint: str | None    # primary maritime chokepoint on the route to India
    transit_days: int         # approx voyage days to a west-coast Indian port
    available_kbd: float      # supply realistically available to India (kb/d)

    @property
    def is_sour(self) -> bool:
        return self.sulphur >= 1.0


# Gulf grades — backbone of India's slate; almost all transit the Strait of Hormuz.
GULF_CRUDES = [
    Crude("Basrah Light",   "Iraq",        30.2, 2.90, 82.0, "Hormuz", 7, 700),
    Crude("Basrah Heavy",   "Iraq",        23.7, 3.90, 78.0, "Hormuz", 7, 500),
    Crude("Arab Light",     "Saudi Arabia",32.8, 1.97, 85.0, "Hormuz", 6, 800),
    Crude("Arab Medium",    "Saudi Arabia",30.2, 2.40, 83.0, "Hormuz", 6, 400),
    Crude("Arab Heavy",     "Saudi Arabia",27.0, 2.80, 80.0, "Hormuz", 6, 400),
    Crude("Murban",         "UAE",         40.2, 0.78, 88.0, "Hormuz", 5, 500),
    Crude("Upper Zakum",    "UAE",         34.0, 1.70, 84.0, "Hormuz", 5, 400),
    Crude("Qatar Marine",   "Qatar",       35.8, 1.45, 85.0, "Hormuz", 5, 300),
]

# Non-Hormuz alternates — what you can actually reach when the Strait is cut.
# Prices are crisis-elevated; Urals is discounted (sanctions) but supply-limited.
# CPC Blend (~45 API) is condensate-light: only the lightest-configured refinery
# can run it -> structural grade infeasibility for a fungible buyer.
ALT_CRUDES = [
    Crude("Urals",        "Russia",     31.0, 1.60, 74.0, "Suez", 30, 600),
    Crude("CPC Blend",    "Kazakhstan", 45.0, 0.55, 83.0, "Suez", 28, 250),
    Crude("Girassol",     "Angola",     30.0, 0.33, 85.0, "Cape", 25, 250),
    Crude("ESPO",         "Russia",     34.5, 0.55, 86.0, None,   12, 300),
    Crude("Bonny Light",  "Nigeria",    35.3, 0.15, 88.0, "Cape", 22, 300),
    Crude("WTI Midland",  "USA",        41.5, 0.24, 89.0, None,   40, 500),
    Crude("Brent",        "North Sea",  38.3, 0.37, 90.0, None,   25, 150),
]

ALL_CRUDES = GULF_CRUDES + ALT_CRUDES
CRUDE_BY_NAME = {c.name: c for c in ALL_CRUDES}

# Chokepoints each grade's route to India passes through (ordered origin->India).
# Single source of truth for BOTH disruption logic and the map: a grade is
# unavailable if ANY chokepoint on its route is cut in the scenario.
CRUDE_ROUTES = {
    "Basrah Light": ("Hormuz",), "Basrah Heavy": ("Hormuz",),
    "Arab Light": ("Hormuz",), "Arab Medium": ("Hormuz",), "Arab Heavy": ("Hormuz",),
    "Murban": ("Hormuz",), "Upper Zakum": ("Hormuz",), "Qatar Marine": ("Hormuz",),
    "Urals": ("Suez", "Bab-el-Mandeb"), "CPC Blend": ("Suez", "Bab-el-Mandeb"),
    "Brent": ("Suez", "Bab-el-Mandeb"),
    "Girassol": ("Cape",), "Bonny Light": ("Cape",), "WTI Midland": ("Cape",),
    "ESPO": ("Malacca",),
}


# --------------------------------------------------------------------------- #
#  Refineries (each configured for a specific slate)                           #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Refinery:
    name: str
    state: str
    capacity_kbd: float
    api_min: float            # runnable window low end  (below -> too heavy for config)
    api_max: float            # runnable window high end (above -> too light; units starved)
    crude_max_sulphur: float  # hard limit any single grade may have
    desulph_limit: float      # blend-average sulphur cap = desulphurisation CAPACITY
    api_opt: float            # design-optimum API (yield penalty grows with distance)
    hormuz_share: float       # fraction of normal slate that arrives via Hormuz
    yield_pen_per_api: float  # $/bbl yield penalty per API point away from api_opt

    @property
    def hormuz_gap_kbd(self) -> float:
        """Barrels/day to replace if the Strait of Hormuz is cut."""
        return round(self.capacity_kbd * self.hormuz_share, 1)


# A representative slice of India's fleet, deliberately heterogeneous:
#   - Deep-conversion COKING refineries (Jamnagar, Vadinar, Paradip): built for
#     heavy/sour, big desulph + coker; light condensate STARVES them (low api_max).
#   - Simpler refineries (Panipat, HPCL Mumbai): small desulphurisation -> CANNOT
#     absorb sour crude (low desulph_limit) and need lighter feed (high api_min).
# This heterogeneity is exactly what "oil is fungible" planning ignores.
#
# CAPACITIES are REAL (PPAC installed-capacity, converted MMTPA -> kbd at ~20 kbd/MMTPA):
#   Jamnagar 68.2, Vadinar 20.0, Paradip 15.0, Mangalore 15.0, Kochi 15.5,
#   Panipat 15.0, HPCL-Mumbai 6.5 MMTPA. (India total ~258 MMTPA across 23 refineries.)
# The CONFIG columns (api window, desulph, optimum, Hormuz share, yield pen) are
# modelled/illustrative — these are not publicly disclosed and are the values to
# calibrate with a refining expert.
REFINERIES = [
    #          name             state          cap  amin amax maxS dslf opt  share pen
    Refinery("RIL Jamnagar",   "Gujarat",     1360,  18,  40, 4.0, 3.2, 28, 0.35, 0.70),
    Refinery("Nayara Vadinar", "Gujarat",      400,  20,  39, 3.8, 2.9, 29, 0.30, 0.70),
    Refinery("IOCL Paradip",   "Odisha",       300,  20,  38, 3.6, 3.0, 27, 0.55, 0.80),
    Refinery("MRPL Mangalore", "Karnataka",    300,  24,  42, 2.4, 1.9, 32, 0.65, 0.85),
    Refinery("BPCL Kochi",     "Kerala",       310,  26,  44, 2.0, 1.5, 33, 0.60, 0.90),
    Refinery("IOCL Panipat",   "Haryana",      300,  30,  44, 1.6, 1.2, 35, 0.50, 1.10),
    Refinery("HPCL Mumbai",    "Maharashtra",  130,  30,  46, 1.5, 1.1, 36, 0.60, 1.10),
]

# India's real 2024 crude-import mix (DGCIS / trade data), for context & the deck.
# Note Russia is now #1 (non-Hormuz); the Gulf suppliers (~Hormuz) sum to ~45%.
IMPORT_MIX_2024 = {
    "Russia": 0.363, "Iraq": 0.205, "Saudi Arabia": 0.130, "UAE": 0.090,
    "USA": 0.035, "Others": 0.177,
}


# --------------------------------------------------------------------------- #
#  National aggregates (for honest strategic-reserve maths)                    #
# --------------------------------------------------------------------------- #
NATIONAL_RUN_KBD = sum(r.capacity_kbd for r in REFINERIES)
TOTAL_HORMUZ_GAP_KBD = sum(r.hormuz_gap_kbd for r in REFINERIES)
# Share of TOTAL national crude run that is lost when Hormuz is cut.
HORMUZ_SUPPLY_FRACTION = TOTAL_HORMUZ_GAP_KBD / NATIONAL_RUN_KBD

# ISPRL Phase-I usable cover, expressed in days of *total* national crude run.
SPR_DAYS_COVER = 9.5
# Baseline Gulf voyage (days); alternates benchmarked against this for the SPR bridge.
GULF_BASELINE_TRANSIT_DAYS = 6


# --------------------------------------------------------------------------- #
#  Scenario definition                                                         #
# --------------------------------------------------------------------------- #
@dataclass
class Scenario:
    name: str
    disrupted_chokepoints: set[str] = field(default_factory=set)
    alt_supply_factor: float = 1.0       # haircut on alternate availability (e.g. OPEC+ cut)
    scramble_premium_usd: float = 0.0    # crisis premium added to every available barrel
    cascade_closure: float = 1.0         # Hormuz throughput loss fed to the cascade model

    def available_crudes(self) -> list[Crude]:
        """Grades whose route avoids every disrupted chokepoint."""
        return [c for c in ALL_CRUDES
                if not (set(CRUDE_ROUTES.get(c.name, ())) & self.disrupted_chokepoints)]


HORMUZ_CLOSURE = Scenario(
    name="Strait of Hormuz - sustained disruption",
    disrupted_chokepoints={"Hormuz"},
    alt_supply_factor=1.0,
    scramble_premium_usd=5.0,
)
