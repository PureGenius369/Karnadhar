"""
KARNADHAR — knowledge-graph export
==================================

The brief's suggested tech includes "Knowledge Graphs (supplier-route-risk-refinery
relationships)". KARNADHAR's real model IS that graph in substance — this exporter
materialises it as a typed property graph so the claim is concrete and inspectable.

Run:  python export_kg.py   ->  engine/data/karnadhar_kg.json

Schema
  nodes: supplier (country+grade), chokepoint, refinery
  edges: SHIPS_VIA   supplier  -> chokepoint   (route dependency)
         SUPPLIES    supplier  -> refinery     (real DGCIS volume, kb/d)
         THREATENS   chokepoint-> refinery     (derived exposure share)
Every edge carries provenance: which dataset it came from.
"""

from __future__ import annotations
import json
from pathlib import Path

from engine.realmodel import build_refineries, build_crudes
from engine.refdata import country_info, chokepoint_exposure, load_diets

OUT = Path(__file__).parent / "engine" / "data" / "karnadhar_kg.json"
OUT_UI = Path(__file__).parent / "frontend" / "public" / "karnadhar_kg.json"


def main():
    refs, crudes = build_refineries(), build_crudes()
    raw = load_diets()
    nodes, edges = [], []

    for c in crudes:
        nodes.append({
            "id": f"supplier:{c.name}", "type": "supplier",
            "label": c.name.title(), "grade": c.grade,
            "api": c.api, "sulphur": c.sulphur, "asphaltene": c.asphaltene,
            "price_usd_bbl": c.price_usd_bbl, "available_kbd": c.available_kbd,
        })
        for ck in c.chokepoints:
            edges.append({"type": "SHIPS_VIA", "from": f"supplier:{c.name}",
                          "to": f"chokepoint:{ck}", "provenance": "route mapping"})

    chokepoints = {ck for c in crudes for ck in c.chokepoints} | {"Cape", "Malacca"}
    for ck in sorted(chokepoints):
        nodes.append({"id": f"chokepoint:{ck}", "type": "chokepoint", "label": ck})

    for r in refs:
        nodes.append({
            "id": f"refinery:{r.name}", "type": "refinery", "label": r.name,
            "capacity_kbd": r.capacity_kbd, "nelson": r.nelson,
            "api_window": [r.api_min, r.api_max],
            "desulph_limit": r.desulph_limit, "max_asphaltene": r.max_asphaltene,
        })
        for country, kbd in r.diet_kbd.items():
            edges.append({"type": "SUPPLIES", "from": f"supplier:{country}",
                          "to": f"refinery:{r.name}", "kbd": kbd,
                          "provenance": "DGCIS May2025-Apr2026"})
        for ck, share in chokepoint_exposure(raw[r.name]["diet"]).items():
            edges.append({"type": "THREATENS", "from": f"chokepoint:{ck}",
                          "to": f"refinery:{r.name}", "exposure": round(share, 3),
                          "provenance": "derived: diet x route"})

    kg = {"schema": {"nodes": ["supplier", "chokepoint", "refinery"],
                     "edges": ["SHIPS_VIA", "SUPPLIES", "THREATENS"]},
          "nodes": nodes, "edges": edges}
    OUT.write_text(json.dumps(kg, indent=1))
    OUT_UI.write_text(json.dumps(kg))   # served to the war-room graph view

    by_type = {}
    for e in edges:
        by_type[e["type"]] = by_type.get(e["type"], 0) + 1
    print(f"wrote {OUT.name}: {len(nodes)} nodes, {len(edges)} edges "
          f"({', '.join(f'{k} {v}' for k, v in by_type.items())})")
    # sample traversal: what does blocking Hormuz threaten?
    hz = [e for e in edges if e["type"] == "THREATENS" and e["from"] == "chokepoint:Hormuz"]
    worst = max(hz, key=lambda e: e["exposure"])
    print(f"sample query — Hormuz THREATENS {len(hz)} refineries; "
          f"highest exposure: {worst['to'].split(':')[1]} ({worst['exposure']:.0%})")


if __name__ == "__main__":
    main()
