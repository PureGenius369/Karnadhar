"""
KARNADHAR — Orchestrator   (Evaluation Focus #5: end-to-end response time)
=========================================================================

Chains the specialist agents into ONE timed pipeline:

    geopolitical SIGNAL  ->  SCENARIO cascade  ->  procurement REROUTE  ->  BRIEF

Each stage is timed; the total is the EF-5 headline ("signal to recommendation in
X seconds, vs the 47-day baseline McKinsey found for unprepared economies"). The
detected signal severity drives the modelled closure fraction, so the signal really
does trigger the action — this is the agentic spine the war-room UI sits on.
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import date
import time

from engine.data import HORMUZ_CLOSURE, HORMUZ_SUPPLY_FRACTION, Scenario
from engine.signals.agent import GeopoliticalRiskAgent
from engine.signals.extract import classify_headlines
from engine.cascade import compute_cascade, CascadeParams
from engine.optimizer import naive_fungible_plan, grade_aware_plan, evaluate
from engine.briefing import generate_brief

# map peak news severity (0-5) to a modelled chokepoint closure fraction
SEV_TO_CLOSURE = {0: 0.0, 1: 0.10, 2: 0.25, 3: 0.50, 4: 0.75, 5: 1.0}


@dataclass
class Stage:
    name: str
    seconds: float
    summary: str


@dataclass
class PipelineResult:
    stages: list[Stage]
    total_seconds: float
    backtest: object          # signal backtest
    peak_severity: int
    corridor: str
    closure_pct: float
    cascade: object
    naive: object             # PlanMetrics
    smart: object             # PlanMetrics
    smart_plan: dict
    solver_status: str
    brief: str
    brief_method: str


def run_pipeline(signal_points: list[dict], market_day: date, headlines: list[str],
                 scenario: Scenario = HORMUZ_CLOSURE) -> PipelineResult:
    stages: list[Stage] = []
    t_total = time.perf_counter()

    # 1) SIGNAL --------------------------------------------------------------
    t = time.perf_counter()
    agent = GeopoliticalRiskAgent()
    bt = agent.assess(signal_points, market_day)
    sigs = classify_headlines(headlines)
    peak_sev = max((s.severity for s in sigs), default=0)
    corridor = next((s.corridor for s in sigs if s.corridor), "hormuz")
    stages.append(Stage("Signal", time.perf_counter() - t,
                        f"alert {bt.alert_day} ({bt.lead_days}d lead), severity {peak_sev}/5"))

    # 2) SCENARIO ------------------------------------------------------------
    t = time.perf_counter()
    closure = SEV_TO_CLOSURE.get(peak_sev, 1.0)
    cas = compute_cascade(closure, CascadeParams())
    stages.append(Stage("Scenario", time.perf_counter() - t,
                        f"{closure:.0%} closure -> Brent ${cas.brent_usd:.0f} "
                        f"(+{cas.brent_change_pct:.0f}%), GDP -{cas.gdp_drag_pp:.2f}pp"))

    # 3) PROCUREMENT ---------------------------------------------------------
    t = time.perf_counter()
    naive = naive_fungible_plan(scenario)
    m_naive = evaluate("naive", naive, scenario)
    plan, status = grade_aware_plan(scenario)
    m_smart = evaluate("smart", plan, scenario)
    stages.append(Stage("Procurement", time.perf_counter() - t,
                        f"naive infeasible {m_naive.unrunnable_kbd:.0f}kb/d -> "
                        f"grade-aware feasible={m_smart.feasible}"))

    # 4) BRIEFING ------------------------------------------------------------
    t = time.perf_counter()
    yield_saved = round(m_naive.yield_loss_musd_day - m_smart.yield_loss_musd_day, 2)
    ctx = dict(
        corridor=corridor, alert_day=bt.alert_day, lead_days=bt.lead_days,
        peak_severity=peak_sev, closure_pct=closure,
        brent_usd=cas.brent_usd, brent_pct=cas.brent_change_pct,
        pump_inr=cas.pump_inr_per_l, gdp_drag_pp=cas.gdp_drag_pp,
        import_bill=cas.india_extra_import_bill_musd_day,
        extra_annual_bn=cas.extra_annual_import_bill_usd_bn,
        cad_stressed=cas.stressed_cad_pct_gdp,
        naive_unrunnable=m_naive.unrunnable_kbd, yield_saved=yield_saved,
        true_cost_delta=round(m_naive.true_cost_musd_day - m_smart.true_cost_musd_day, 2),
        effective_spr=m_smart.effective_spr_days, spr_bridge=m_smart.spr_bridge_days,
        spr_margin=m_smart.spr_margin_days, gap_pct=HORMUZ_SUPPLY_FRACTION,
        total_seconds=time.perf_counter() - t_total,
    )
    brief, method = generate_brief(ctx)
    stages.append(Stage("Briefing", time.perf_counter() - t, f"executive memo ({method})"))

    total = time.perf_counter() - t_total
    return PipelineResult(stages, total, bt, peak_sev, corridor, closure, cas,
                          m_naive, m_smart, plan, status, brief, method)
