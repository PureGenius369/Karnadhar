"""
KARNADHAR — GDELT client   (Evaluation Focus #1: real-data signal source)
=========================================================================

Pulls coverage-volume timelines from GDELT's free DOC 2.0 API (no key needed) for
disruption queries like "strait of hormuz". Design for a real demo:

  live  -> hit the API (User-Agent + retry/backoff) and CACHE the JSON
  cache -> reuse a previously fetched real series (reproducible)
  representative -> a clearly-labelled reconstruction for offline / rate-limited runs

The caller is always told which source was used, so real vs representative data is
never confused. Run this on your own machine to populate the cache with REAL GDELT
data (shared cloud IPs get rate-limited / 429'd).
"""

from __future__ import annotations
import json, time, hashlib
from pathlib import Path

import requests

GDELT_DOC = "https://api.gdeltproject.org/api/v2/doc/doc"
UA = {"User-Agent": "KARNADHAR-research/0.1 (academic hackathon project)"}

_HERE = Path(__file__).parent
CACHE_DIR = _HERE / "cache"
SNAP_DIR = _HERE / "snapshots"


def _cache_path(params: dict) -> Path:
    key = hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()[:16]
    return CACHE_DIR / f"{key}.json"


def fetch_timeline(query: str, start: str, end: str,
                   mode: str = "timelinevol", retries: int = 3):
    """Return (points, source). points = [{'date':'YYYYMMDD','value':float}, ...].

    start/end are 'YYYYMMDDHHMMSS'. source in {'live','cache','unavailable'}.
    """
    params = dict(query=query, mode=mode, format="json",
                  startdatetime=start, enddatetime=end)
    cp = _cache_path(params)
    if cp.exists():
        return json.loads(cp.read_text())["data"], "cache"

    for attempt in range(retries):
        try:
            r = requests.get(GDELT_DOC, params=params, headers=UA, timeout=30)
            if r.status_code == 200 and r.text.strip().startswith("{"):
                raw = r.json()
                pts = [{"date": p["date"][:8], "value": float(p["value"])}
                       for p in raw["timeline"][0]["data"]]
                CACHE_DIR.mkdir(exist_ok=True)
                cp.write_text(json.dumps({"params": params, "data": pts}, indent=2))
                return pts, "live"
        except Exception:
            pass
        time.sleep(2 + attempt * 2)
    return None, "unavailable"


def load_representative(name: str):
    """Load a labelled representative reconstruction (offline fallback)."""
    blob = json.loads((SNAP_DIR / name).read_text())
    return blob["data"], "representative"


def timeline_with_fallback(query, start, end, representative_file):
    """Try live/cache; if GDELT is unreachable, fall back to the labelled snapshot."""
    pts, source = fetch_timeline(query, start, end)
    if pts is None:
        pts, source = load_representative(representative_file)
    return pts, source
