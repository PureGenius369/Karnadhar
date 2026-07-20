"""
KARNADHAR — Geopolitical Risk Agent   (Evaluation Focus #1: lead time & accuracy)
================================================================================

Turns a raw GDELT coverage timeline into a disruption-risk signal and answers the
EF-1 question with a number: *how many days before the market repriced would we
have raised the alert?*

Method (transparent and testable):
  - establish a quiet BASELINE from the first N days (mean mu, std sigma)
  - per day, z = (volume - mu) / sigma   ->  probability = logistic(z - z_alert)
  - ALERT when coverage exceeds `spike_multiple * mu` for `sustain` consecutive days
    (a standard, explainable anomaly rule; not a black box)
  - LEAD TIME = market-reaction date  -  alert date
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import date, datetime
import math


def _d(s: str) -> date:
    return datetime.strptime(s, "%Y%m%d").date()


@dataclass
class DayRisk:
    day: date
    volume: float
    z: float
    probability: float
    alerted: bool


@dataclass
class Backtest:
    baseline_mean: float
    baseline_std: float
    alert_threshold: float
    alert_day: date | None
    market_day: date
    lead_days: int | None
    series: list[DayRisk]


class GeopoliticalRiskAgent:
    def __init__(self, baseline_days: int = 10, z_alert: float = 2.0,
                 spike_multiple: float = 3.0, sustain: int = 2):
        self.baseline_days = baseline_days
        self.z_alert = z_alert
        self.spike_multiple = spike_multiple
        self.sustain = sustain

    def assess(self, points: list[dict], market_reaction_on: date) -> Backtest:
        vals = [p["value"] for p in points]
        days = [_d(p["date"]) for p in points]

        base = vals[:self.baseline_days]
        mu = sum(base) / len(base)
        var = sum((v - mu) ** 2 for v in base) / max(1, len(base) - 1)
        sigma = math.sqrt(var) or 1e-6
        threshold = mu * self.spike_multiple

        series: list[DayRisk] = []
        run = 0
        alert_day = None
        for i, v in enumerate(vals):
            z = (v - mu) / sigma
            prob = 1.0 / (1.0 + math.exp(-(z - self.z_alert)))
            is_spike = v >= threshold
            run = run + 1 if is_spike else 0
            alerted = run >= self.sustain
            if alerted and alert_day is None:
                alert_day = days[i - self.sustain + 1]
            series.append(DayRisk(days[i], v, z, prob, alerted))

        lead = (market_reaction_on - alert_day).days if alert_day else None
        return Backtest(round(mu, 3), round(sigma, 3), round(threshold, 3),
                        alert_day, market_reaction_on, lead, series)
