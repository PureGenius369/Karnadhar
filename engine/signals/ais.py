"""
KARNADHAR — Maritime / AIS agent   (Evaluation Focus #1 maritime leg + EF-4 map data)
=====================================================================================

Pulls live tanker positions in a chokepoint bounding box from aisstream.io (free
WebSocket feed) and turns them into a traffic/congestion signal that complements
the news signal — exactly the multi-source fusion the brief calls for ("ingests
news feeds, shipping AIS data, ...").

Resilience pattern (same as the GDELT client):
    live  -> connect, collect PositionReports for a few seconds, cache them
    cache -> reuse a previously collected real snapshot
    representative -> labelled fallback so the demo always runs

The API key is read from env AISSTREAM_API_KEY or the git-ignored karnadhar/.env —
it is NEVER hard-coded. Streaming is blocked on shared cloud IPs; run on your own
machine to collect real vessels.
"""

from __future__ import annotations
import os, json, asyncio
from pathlib import Path

_HERE = Path(__file__).parent
CACHE_DIR = _HERE / "cache"
SNAP_DIR = _HERE / "snapshots"
_ENV = _HERE.parents[1] / ".env"          # karnadhar/.env

# [[lat,lon],[lat,lon]] bounding boxes per chokepoint.
# NOTE: aisstream is crowdsourced — coverage is dense at Malacca/Singapore but
# currently absent in the Persian Gulf, so Hormuz uses a labelled representative
# snapshot (a commercial feed drops into the same client for real Gulf data).
CHOKEPOINT_BBOX = {
    "Hormuz":        [[24.0, 54.0], [27.5, 57.5]],
    "Malacca":       [[1.0, 103.0], [2.0, 104.6]],
    "Bab-el-Mandeb": [[11.5, 42.0], [14.0, 44.0]],
}
HORMUZ_BBOX = CHOKEPOINT_BBOX["Hormuz"]   # backward-compat alias


def _load_key() -> str | None:
    k = os.getenv("AISSTREAM_API_KEY")
    if k:
        return k.strip()
    if _ENV.exists():
        for line in _ENV.read_text().splitlines():
            if line.strip().startswith("AISSTREAM_API_KEY"):
                return line.split("=", 1)[1].strip()
    return None


async def _collect(key: str, bbox: list, seconds: int) -> list[dict]:
    import websockets
    vessels: dict[int, dict] = {}
    async with websockets.connect("wss://stream.aisstream.io/v0/stream",
                                  open_timeout=15) as ws:
        await ws.send(json.dumps({"APIKey": key, "BoundingBoxes": [bbox],
                                  "FilterMessageTypes": ["PositionReport"]}))
        deadline = asyncio.get_event_loop().time() + seconds
        while asyncio.get_event_loop().time() < deadline:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=seconds)
            except asyncio.TimeoutError:
                break
            d = json.loads(msg)
            if d.get("MessageType") == "PositionReport":
                m, pr = d["MetaData"], d["Message"]["PositionReport"]
                vessels[m["MMSI"]] = {
                    "mmsi": m["MMSI"], "name": (m.get("ShipName") or "").strip(),
                    "lat": round(m["latitude"], 4), "lon": round(m["longitude"], 4),
                    "sog": pr.get("Sog"),
                }
    return list(vessels.values())


def fetch_ais(chokepoint: str = "Hormuz", seconds: int = 12):
    """Return (vessels, source) for a chokepoint. source in
    {'cache','live','representative','unavailable'}. Tries live aisstream, caches a
    real hit, else falls back to a labelled representative snapshot if one exists."""
    bbox = CHOKEPOINT_BBOX[chokepoint]
    cp = CACHE_DIR / f"ais_{chokepoint.lower()}.json"
    if cp.exists():
        return json.loads(cp.read_text())["vessels"], "cache"

    key = _load_key()
    if key:
        try:
            vessels = asyncio.run(_collect(key, bbox, seconds))
            if vessels:
                CACHE_DIR.mkdir(exist_ok=True)
                cp.write_text(json.dumps(
                    {"chokepoint": chokepoint, "bbox": bbox, "vessels": vessels}, indent=2))
                return vessels, "live"
        except Exception:
            pass

    rep = SNAP_DIR / f"ais_{chokepoint.lower()}_representative.json"
    if rep.exists():
        return json.loads(rep.read_text())["vessels"], "representative"
    return [], "unavailable"


def traffic_metrics(vessels: list[dict]) -> dict:
    """Chokepoint traffic signal: vessel count, mean speed, and how many are
    near-stationary (a build-up of anchored/slow tankers can flag congestion or a
    closure where ships are forced to wait)."""
    speeds = [v["sog"] for v in vessels if isinstance(v.get("sog"), (int, float)) and v["sog"] >= 0]
    avg = sum(speeds) / len(speeds) if speeds else 0.0
    slow = sum(1 for s in speeds if s < 1.0)
    return {"vessel_count": len(vessels),
            "avg_speed_kn": round(avg, 1),
            "near_stationary": slow,
            "congestion_flag": len(vessels) >= 8 and avg < 5.0}
