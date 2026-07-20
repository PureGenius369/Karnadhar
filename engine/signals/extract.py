"""
KARNADHAR — News signal extraction   (suggested tech: "LLMs for news signal extraction")
=========================================================================================

Pluggable: if the `anthropic` package AND an ANTHROPIC_API_KEY are present, Claude
classifies each headline (severity + threatened corridor/supplier) as structured
JSON. Otherwise a transparent keyword lexicon does it, so the pipeline always runs.
Wiring Claude in is a drop-in upgrade — the interface does not change.
"""

from __future__ import annotations
import os
from dataclasses import dataclass

# severity lexicon (deterministic fallback) ---------------------------------- #
_SEVERITY = {
    "clos": 5, "shut": 5, "blockad": 5, "block": 5, "mine": 5, "seize": 5,
    "attack": 4, "strike": 4, "missile": 4, "drone": 4, "disrupt": 4,
    "sanction": 3, "threat": 3, "tension": 2, "warn": 2, "deploy": 2,
    "talks": 1, "de-escalat": -2, "ceasefire": -3, "diplomat": -1,
}
_CORRIDORS = ["hormuz", "red sea", "bab-el-mandeb", "persian gulf", "suez", "malacca"]


@dataclass
class HeadlineSignal:
    headline: str
    severity: int            # 0-5
    corridor: str | None
    method: str              # "claude" or "keyword"


def _keyword_classify(h: str) -> HeadlineSignal:
    low = h.lower()
    sev = 0
    for kw, s in _SEVERITY.items():
        if kw in low:
            sev = max(sev, s) if s > 0 else sev + s
    sev = max(0, min(5, sev))
    corridor = next((c for c in _CORRIDORS if c in low), None)
    return HeadlineSignal(h, sev, corridor, "keyword")


def _claude_available() -> bool:
    if not os.getenv("ANTHROPIC_API_KEY"):
        return False
    try:
        import anthropic  # noqa: F401
        return True
    except Exception:
        return False


def classify_headlines(headlines: list[str]) -> list[HeadlineSignal]:
    """Return a structured risk signal per headline (Claude if available, else keyword)."""
    if not _claude_available():
        return [_keyword_classify(h) for h in headlines]

    # --- Claude path (drop-in; runs only when a key is configured) ----------- #
    import json, anthropic
    client = anthropic.Anthropic()
    prompt = (
        "For each headline, rate energy-supply disruption SEVERITY 0-5 and name the "
        "threatened shipping corridor if any. Return JSON list of "
        '{"headline","severity","corridor"}.\n\nHeadlines:\n'
        + "\n".join(f"- {h}" for h in headlines)
    )
    msg = client.messages.create(
        model="claude-opus-4-8", max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    try:
        rows = json.loads(msg.content[0].text)
        return [HeadlineSignal(r["headline"], int(r["severity"]),
                               r.get("corridor"), "claude") for r in rows]
    except Exception:
        return [_keyword_classify(h) for h in headlines]
