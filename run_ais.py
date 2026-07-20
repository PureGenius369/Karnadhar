"""
KARNADHAR — Maritime / AIS demo   (Evaluation Focus #1 maritime leg)

Run:  python run_ais.py     (from the karnadhar/ folder)

Shows the AIS agent on two chokepoints:
  - Hormuz  : labelled representative snapshot (aisstream has no Gulf receivers)
  - Malacca : LIVE real tankers (dense crowdsourced coverage) — proof the
              ingestion is genuinely real, not faked.
"""

from engine.signals.ais import fetch_ais, traffic_metrics

LINE = "=" * 72
TAGS = {"live": "LIVE aisstream (REAL)", "cache": "cached real AIS",
        "representative": "REPRESENTATIVE snapshot (labelled)", "unavailable": "no data"}


def show(chokepoint, seconds):
    vessels, source = fetch_ais(chokepoint, seconds=seconds)
    m = traffic_metrics(vessels)
    print(f"\n  [{chokepoint}]  source: {TAGS[source]}")
    print(f"    vessels {m['vessel_count']:>3} | mean {m['avg_speed_kn']:>5} kn | "
          f"near-stationary {m['near_stationary']} | congestion: "
          f"{'YES' if m['congestion_flag'] else 'no'}")
    for v in sorted(vessels, key=lambda x: x.get('sog') or 0)[:5]:
        print(f"      {v['name'][:20]:<20} lat={v['lat']:.3f} lon={v['lon']:.3f}  {v['sog']:>5} kn")
    return source


def main():
    print(LINE)
    print("  MARITIME / AIS AGENT  -  chokepoint tanker traffic")
    print(LINE)

    malacca_src = show("Malacca", seconds=15)   # live where coverage exists
    show("Hormuz", seconds=6)                    # representative (Gulf gap)

    print("\n" + LINE)
    if malacca_src in ("live", "cache"):
        print("  ^ Malacca vessels are REAL, live AIS - the pipeline ingests genuine data.")
    print("  Hormuz uses a labelled representative snapshot (aisstream has no Persian")
    print("  Gulf receivers); a commercial feed drops into the SAME client for real Gulf")
    print("  data. Fused with the GDELT news signal = multi-source disruption detection.")
    print(LINE)


if __name__ == "__main__":
    main()
