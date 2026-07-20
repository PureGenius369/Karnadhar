"""
KARNADHAR — Geopolitical signal demo   (Evaluation Focus #1)

Run:  python run_signal.py     (from the karnadhar/ folder)

Backtests the Geopolitical Risk Agent on the June-2025 Strait of Hormuz crisis:
how many days before Brent's +8% single session would KARNADHAR have alerted?
Uses live GDELT if reachable, else a clearly-labelled representative snapshot.
"""

from datetime import date

from engine.signals.gdelt import timeline_with_fallback
from engine.signals.agent import GeopoliticalRiskAgent
from engine.signals.extract import classify_headlines

LINE = "=" * 78
SNAP = "hormuz_2025_06_representative.json"
QUERY = '"strait of hormuz"'
MARKET_DAY = date(2025, 6, 23)   # Brent +8% single session

# representative headlines from the event window (illustrative; live path can pull real)
HEADLINES = [
    "Iran's parliament moves to consider closing the Strait of Hormuz",
    "US strikes Iranian nuclear sites as oil markets brace for disruption",
    "Tankers reroute around the Red Sea as Houthi attacks intensify",
    "Diplomats signal de-escalation; ceasefire talks reported",
]


def main():
    print(LINE)
    print("  GEOPOLITICAL RISK AGENT - Strait of Hormuz, June 2025  (EF-1: lead time)")
    print(LINE)

    pts, source = timeline_with_fallback(
        QUERY, "20250601000000", "20250630000000", SNAP)
    tag = {"live": "LIVE GDELT (real)", "cache": "cached real GDELT",
           "representative": "REPRESENTATIVE snapshot (labelled reconstruction)"}[source]
    print(f"  data source : {tag}")
    print(f"  query       : {QUERY}   (GDELT DOC 2.0, timelinevol)")

    agent = GeopoliticalRiskAgent(baseline_days=10, spike_multiple=3.0, sustain=2)
    bt = agent.assess(pts, MARKET_DAY)

    print(f"  baseline    : mean {bt.baseline_mean}  std {bt.baseline_std}  "
          f"-> alert threshold {bt.alert_threshold} (3x baseline, 2 days sustained)")

    print("\n  coverage signal (bar = coverage volume, vs quiet baseline):")
    hi = max(p.volume for p in bt.series)
    for p in bt.series:
        if p.day < date(2025, 6, 10) or p.day > date(2025, 6, 26):
            continue
        bar = "#" * max(1, int(p.volume / hi * 30))
        mult = p.volume / bt.baseline_mean
        mark = ""
        if p.day == bt.alert_day:
            mark = "  <== ALERT"
        if p.day == MARKET_DAY:
            mark += "  ** Brent +8% session **"
        print(f"    {p.day}  {bar:30s} {mult:5.1f}x base  p={p.probability:0.2f}{mark}")

    print("\n" + LINE)
    print("  RESULT")
    print(LINE)
    if bt.alert_day:
        print(f"  - Alert raised on        : {bt.alert_day}")
        print(f"  - Market repriced on     : {bt.market_day}  (Brent +8% single session)")
        print(f"  - LEAD TIME              : {bt.lead_days} days ahead of the market")
    else:
        print("  - No alert raised in window.")

    print("\n  Headline extraction (structured risk tags):")
    for hs in classify_headlines(HEADLINES):
        print(f"    [sev {hs.severity}/5 | {hs.corridor or '-':10s} | {hs.method:7s}] {hs.headline}")

    print("\n" + LINE)
    if source == "representative":
        print("  NOTE: representative data. Run on a non-rate-limited machine to fetch & cache")
        print("        the REAL GDELT series; the method and lead-time logic are identical.")
    print(LINE)


if __name__ == "__main__":
    main()
