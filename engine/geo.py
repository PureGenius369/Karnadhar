"""
KARNADHAR — Geospatial layer   (Evaluation Focus #4: geospatial evidence depth)
==============================================================================

Real-world coordinates for the war-room map: maritime chokepoints, India's
refineries, crude load ports, and the shipping routes that connect them. A route
is flagged 'disrupted' when it passes a chokepoint that is cut in the scenario —
which is what makes the Gulf grades disappear and forces the long alternates.

Coordinates are approximate public locations (load terminals / strait midpoints),
fine for visualisation; swap for exact values as needed.
"""

from __future__ import annotations
from engine.data import REFINERIES, ALL_CRUDES, Scenario, CRUDE_ROUTES

# India west-coast discharge hub (most crude lands here; Sikka/Vadinar area)
INDIA_HUB = {"name": "India (west coast)", "lat": 22.4, "lon": 69.1}

CHOKEPOINTS = {
    "Hormuz":         {"lat": 26.57, "lon": 56.25, "label": "Strait of Hormuz",  "flow_mbd": 20.0},
    "Bab-el-Mandeb":  {"lat": 12.60, "lon": 43.30, "label": "Bab-el-Mandeb",     "flow_mbd": 6.2},
    "Suez":           {"lat": 30.60, "lon": 32.35, "label": "Suez Canal",        "flow_mbd": 5.5},
    "Cape":           {"lat": -34.36,"lon": 18.47, "label": "Cape of Good Hope", "flow_mbd": 5.0},
    "Malacca":        {"lat": 2.50,  "lon": 101.5, "label": "Strait of Malacca", "flow_mbd": 16.0},
}

# refinery name -> (lat, lon)
REFINERY_COORDS = {
    "RIL Jamnagar":   (22.34, 69.85),
    "Nayara Vadinar": (22.28, 69.73),
    "IOCL Paradip":   (20.27, 86.67),
    "MRPL Mangalore": (12.95, 74.83),
    "BPCL Kochi":     (9.97, 76.28),
    "IOCL Panipat":   (29.39, 76.97),
    "HPCL Mumbai":    (19.00, 72.83),
}

# crude origin (load port) coordinates by origin country/region label in data.py
ORIGIN_COORDS = {
    "Iraq":         (29.70, 48.80),
    "Saudi Arabia": (26.64, 50.16),
    "UAE":          (24.20, 52.60),
    "Qatar":        (25.90, 51.60),
    "Russia":       (44.72, 37.79),   # Urals via Novorossiysk (Black Sea)
    "Kazakhstan":   (44.60, 37.90),   # CPC blend, loads at Novorossiysk
    "Angola":       (-7.50, 11.50),
    "Nigeria":      (4.45, 7.17),
    "USA":          (27.80, -97.40),  # US Gulf
    "North Sea":    (60.00, -1.00),
}

# route chokepoints come from data.CRUDE_ROUTES (single source of truth)


def _origin_for(crude) -> dict:
    lat, lon = ORIGIN_COORDS.get(crude.origin, (0.0, 0.0))
    return {"name": crude.origin, "lat": lat, "lon": lon}


def build_geo(scenario: Scenario) -> dict:
    """Everything the map needs, with disruption state applied for the scenario."""
    cut = scenario.disrupted_chokepoints

    chokepoints = [
        {**c, "key": k, "disrupted": k in cut}
        for k, c in CHOKEPOINTS.items()
    ]

    refineries = []
    for r in REFINERIES:
        lat, lon = REFINERY_COORDS[r.name]
        refineries.append({
            "name": r.name, "state": r.state, "lat": lat, "lon": lon,
            "capacity_kbd": r.capacity_kbd, "hormuz_gap_kbd": r.hormuz_gap_kbd,
            "at_risk": r.hormuz_share > 0,
        })

    sources, routes = [], []
    for c in ALL_CRUDES:
        o = _origin_for(c)
        sources.append({"crude": c.name, "origin": c.origin,
                        "lat": o["lat"], "lon": o["lon"],
                        "api": c.api, "sulphur": c.sulphur, "is_sour": c.is_sour})
        wp_keys = list(CRUDE_ROUTES.get(c.name, ()))
        path = [[o["lon"], o["lat"]]]
        for k in wp_keys:
            ck = CHOKEPOINTS[k]
            path.append([ck["lon"], ck["lat"]])
        path.append([INDIA_HUB["lon"], INDIA_HUB["lat"]])
        disrupted = any(k in cut for k in wp_keys)
        routes.append({"crude": c.name, "origin": c.origin, "path": path,
                       "chokepoints": wp_keys, "disrupted": disrupted})

    return {
        "india_hub": INDIA_HUB,
        "chokepoints": chokepoints,
        "refineries": refineries,
        "sources": sources,
        "routes": routes,
    }
