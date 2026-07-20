"""
KARNADHAR — Briefing agent   (turns the pipeline output into a decision memo)
============================================================================

Pluggable like the news extractor: if `anthropic` + ANTHROPIC_API_KEY are present,
Claude writes a polished executive brief; otherwise a deterministic template fills
the same facts. Either way the *numbers* come from the engine, never invented by
the language model — the LLM only does the wording.
"""

from __future__ import annotations
import os


def _claude_available() -> bool:
    if not os.getenv("ANTHROPIC_API_KEY"):
        return False
    try:
        import anthropic  # noqa: F401
        return True
    except Exception:
        return False


def _template(c: dict) -> str:
    return f"""EXECUTIVE BRIEF  -  Energy Supply-Chain Disruption
{'-' * 60}
1. SIGNAL
   Disruption risk on the {c['corridor'].upper()} corridor crossed the alert
   threshold on {c['alert_day']} - {c['lead_days']} days before the market
   repriced. Peak news severity {c['peak_severity']}/5.

2. PROJECTED IMPACT  (modelled {c['closure_pct']:.0%} closure)
   Brent ${c['brent_usd']:.0f}/bbl (+{c['brent_pct']:.0f}%) | retail fuel ~Rs{c['pump_inr']:.0f}/L
   | GDP drag -{c['gdp_drag_pp']:.2f}pp | crude import bill +${c['import_bill']:.0f}M/day.
   TWIN DEFICIT: +${c['extra_annual_bn']:.0f}bn/yr USD outflow widens the current-account
   deficit to ~{c['cad_stressed']:.1f}% of GDP - a balance-of-payments strain India (a
   trade-deficit economy) cannot sustain, which is what forces demand rationing.

3. RECOMMENDED ACTION  -  crude reroute
   A grade-blind ("fungible") reroute is INFEASIBLE: {c['naive_unrunnable']:.0f} kb/d
   would be sent to refineries that physically cannot run it. KARNADHAR's
   grade-aware reroute is FEASIBLE and protects ${c['yield_saved']:.2f}M/day of
   product yield (~${c['yield_saved']*365:,.0f}M/yr) at ${c['true_cost_delta']:.2f}M/day
   lower true cost. Execute the grade-matched plan.

4. STRATEGIC RESERVE
   ~{c['effective_spr']:.0f} effective days of cover against a {c['gap_pct']:.0%} supply
   gap vs an {c['spr_bridge']:.0f}-day voyage bridge => a {c['spr_margin']:.0f}-day margin.
   {'INITIATE demand-management contingency immediately.' if c['spr_margin'] < 5
    else 'Monitor; margin adequate for a single rotation.'}

Generated end-to-end by KARNADHAR in {c['total_seconds']:.2f}s.
Assumptions explicit and calibratable; figures trace to engine parameters.
"""


def generate_brief(context: dict) -> tuple[str, str]:
    """Return (brief_text, method). method in {'claude','template'}."""
    if not _claude_available():
        return _template(context), "template"

    import anthropic
    client = anthropic.Anthropic()
    prompt = (
        "Write a crisp <200-word executive brief for India's oil-security cell from "
        "these FACTS (do not invent numbers; use only these):\n"
        + "\n".join(f"- {k}: {v}" for k, v in context.items())
    )
    try:
        msg = client.messages.create(
            model="claude-opus-4-8", max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text, "claude"
    except Exception:
        return _template(context), "template"
