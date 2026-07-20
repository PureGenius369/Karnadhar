"""
KARNADHAR — FastAPI backend   (serves the war-room UI)
======================================================

Run:  uvicorn api.main:app --reload --port 8000     (from the karnadhar/ folder)

Endpoints
  GET /api/health              liveness
  GET /api/geo                 chokepoints, refineries, crude sources, routes
  GET /api/pipeline            full signal->scenario->reroute->brief result
  GET /api/scenario?closure=.. cascade for a given closure fraction (slider)
"""

from __future__ import annotations
from dataclasses import asdict
from datetime import date

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from engine.data import HORMUZ_CLOSURE
from engine.geo import build_geo
from engine.cascade import compute_cascade, CascadeParams
from engine.signals.gdelt import timeline_with_fallback
from engine.orchestrator import run_pipeline

QUERY = '"strait of hormuz"'
MARKET_DAY = date(2025, 6, 23)
HEADLINES = [
    "Iran's parliament moves to consider closing the Strait of Hormuz",
    "US strikes Iranian nuclear sites as oil markets brace for disruption",
    "Tankers reroute around the Red Sea as Houthi attacks intensify",
]

# fetch the signal series once at startup (live GDELT -> cache -> representative)
SIGNAL_POINTS, SIGNAL_SOURCE = timeline_with_fallback(
    QUERY, "20250601000000", "20250630000000", "hormuz_2025_06_representative.json")

app = FastAPI(title="KARNADHAR API", version="0.1")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def _serialize_pipeline(res) -> dict:
    bt = res.backtest
    mu = bt.baseline_mean or 1e-9
    return {
        "stages": [{"name": s.name, "ms": round(s.seconds * 1000, 1), "summary": s.summary}
                   for s in res.stages],
        "total_ms": round(res.total_seconds * 1000, 1),
        "signal": {
            "source": SIGNAL_SOURCE,
            "alert_day": str(bt.alert_day) if bt.alert_day else None,
            "market_day": str(bt.market_day),
            "lead_days": bt.lead_days,
            "baseline_mean": bt.baseline_mean,
            "alert_threshold": bt.alert_threshold,
            "series": [{"day": str(p.day), "volume": p.volume,
                        "x_baseline": round(p.volume / mu, 1),
                        "probability": round(p.probability, 3), "alerted": p.alerted}
                       for p in bt.series],
        },
        "severity": res.peak_severity,
        "corridor": res.corridor,
        "closure_pct": res.closure_pct,
        "cascade": asdict(res.cascade),
        "procurement": {
            "naive": asdict(res.naive),
            "smart": asdict(res.smart),
            "plan": res.smart_plan,
            "solver_status": res.solver_status,
        },
        "brief": res.brief,
        "brief_method": res.brief_method,
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "signal_source": SIGNAL_SOURCE}


@app.get("/api/geo")
def geo():
    return build_geo(HORMUZ_CLOSURE)


@app.get("/api/pipeline")
def pipeline():
    res = run_pipeline(SIGNAL_POINTS, MARKET_DAY, HEADLINES)
    return _serialize_pipeline(res)


@app.get("/api/scenario")
def scenario(closure: float = Query(1.0, ge=0.0, le=1.0)):
    return asdict(compute_cascade(closure, CascadeParams()))
