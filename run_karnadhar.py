"""
KARNADHAR — full end-to-end pipeline   (Evaluation Focus #5)

Run:  python run_karnadhar.py     (from the karnadhar/ folder)

One command: a live geopolitical signal triggers a scenario projection, a
grade-aware crude reroute, and an executive brief — timed end-to-end. This is the
"signal -> recommendation" spine the war-room UI renders.
"""

from datetime import date

from engine.signals.gdelt import timeline_with_fallback
from engine.orchestrator import run_pipeline

LINE = "=" * 78
SNAP = "hormuz_2025_06_representative.json"
QUERY = '"strait of hormuz"'
MARKET_DAY = date(2025, 6, 23)

HEADLINES = [
    "Iran's parliament moves to consider closing the Strait of Hormuz",
    "US strikes Iranian nuclear sites as oil markets brace for disruption",
    "Tankers reroute around the Red Sea as Houthi attacks intensify",
]


def main():
    pts, source = timeline_with_fallback(QUERY, "20250601000000", "20250630000000", SNAP)

    print(LINE)
    print("  KARNADHAR - end-to-end pipeline  (signal -> scenario -> reroute -> brief)")
    print(LINE)
    print(f"  signal data: {source}")

    res = run_pipeline(pts, MARKET_DAY, HEADLINES)

    print("\n  PIPELINE STAGES")
    for s in res.stages:
        print(f"    {s.name:12s} {s.seconds*1000:7.1f} ms   {s.summary}")
    print(f"    {'-'*60}")
    print(f"    {'TOTAL':12s} {res.total_seconds*1000:7.1f} ms   signal -> recommendation")

    print("\n" + LINE)
    print(res.brief)
    print(LINE)
    print(f"  EF-5 HEADLINE: signal to executable recommendation in "
          f"{res.total_seconds:.2f}s  vs the 47-DAY average for economies without")
    print(f"  integrated response intelligence (McKinsey, cited in the brief).")
    print(LINE)


if __name__ == "__main__":
    main()
