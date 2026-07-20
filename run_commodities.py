"""
KARNADHAR — multi-commodity import-resilience screen.
Run:  python run_commodities.py
"""
from engine.commodities import COMMODITIES, screen

L = "=" * 86


def table(rows, col):
    hdr = f"  {'commodity':<26}{'dep':>5}{'HHI':>6}{'rigid':>7}{'IVX':>6}{col:>10}"
    print(hdr); print("  " + "-" * (len(hdr) - 2))
    for r in rows:
        print(f"  {r['name']:<26}{r['dependence']:>5.0%}{r['hhi']:>6.2f}"
              f"{r['rigidity']:>7.2f}{r['ivx']:>6.1f}{r['affected']:>9.0%}")


def main():
    print(L)
    print("  MULTI-COMMODITY LENS — one framework, every strategic import")
    print(L)
    print(f"  {len(COMMODITIES)} commodities | IVX = glass-box vulnerability index "
          f"(dependence, supplier HHI,\n  chokepoint exposure, substitution rigidity, "
          f"stockpile relief — weights in engine/commodities.py)\n")

    print("  >> BASELINE (no disruption): ranked by structural vulnerability")
    base = sorted(screen(), key=lambda r: -r["ivx"])
    table(base, "affected")

    print("\n  >> WHAT-IF: Strait of Hormuz blocked")
    table(screen({"Hormuz"}), "affected")

    print("\n  >> WHAT-IF: Strait of Malacca blocked")
    table(screen({"Malacca"}), "affected")

    print("\n" + L)
    print("  The insight generalises: Hormuz is not just a crude problem (53% of LNG");
    print("  transits it too), Malacca is India's electronics/pharma artery, and coking")
    print("  coal shows the framework discriminates — 85% import-dependent yet near-zero")
    print("  chokepoint risk (open-ocean routes). Same anatomy, any material.")
    print(L)


if __name__ == "__main__":
    main()
