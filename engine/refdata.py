"""
KARNADHAR — Real import-data layer   (DGCIS official trade records)
==================================================================

Loads India's ACTUAL crude imports by refinery (port) x source country from the
official DGCIS .xls files, and maps each source country to:
  - a representative crude grade (API gravity, sulphur),
  - its shipping route -> which maritime chokepoints it transits, and
  - approximate voyage days to India.

From this we get, per refinery, its REAL diet, its REAL chokepoint exposure, and
its REAL average crude quality — replacing every illustrative assumption with
government data. A disruption can be a blocked chokepoint (e.g. Hormuz) OR a
sanctioned supplier (e.g. Russia); both are derivable here.

Country -> grade/route is a documented mapping (a country's typical export grade
and the lane its barrels take to India). Note: most non-Gulf crude reaches India
via the open Cape route (no blockable chokepoint), which is why India's chokepoint
risk is concentrated in the Strait of Hormuz — a result that falls straight out of
the real data.
"""

from __future__ import annotations
from pathlib import Path
import json
import pandas as pd

_PKG = Path(__file__).resolve().parent
_PROJECT = _PKG.parent                 # karnadhar/
_ROOT = _PROJECT.parent                # folder holding the .xls files
XLS_FILES = [
    _ROOT / "Petroleum_crude_May2025_to_April2026.xls",   # latest = baseline
    _ROOT / "Petroleum_crude_May2024_toApril_2025.xls",
]
DERIVED_JSON = _PKG / "data" / "india_refinery_diets.json"

# --- port (in the trade data) -> refinery -------------------------------------
PORT_TO_REFINERY = {
    "SIKKA": "RIL Jamnagar",
    "SEZ JAMNAGAR (RELIANCE)": "RIL Jamnagar",
    "VADINAR": "Nayara Vadinar",
    "PARADIP SEA": "IOCL Paradip",
    "MUNDRA": "HMEL Bathinda",
    "MUMBAI SEA": "BPCL/HPCL Mumbai",
    "VISAKHAPATNAM SEA": "HPCL Visakhapatnam",
    "COCHIN SEA": "BPCL Kochi",
    "NEWMANGALORE SEA": "MRPL Mangalore",
    "MANGALORE SEZ": "ONGC Mangalore (OMPL)",
    "CHENNAI SEA": "CPCL Chennai",
}

# --- refinery Nelson Complexity Index (public approx; higher = handles dirtier)
NELSON = {
    "RIL Jamnagar": 21.1, "Nayara Vadinar": 11.8, "IOCL Paradip": 12.2,
    "HMEL Bathinda": 12.5, "MRPL Mangalore": 9.5, "BPCL Kochi": 8.0,
    "BPCL/HPCL Mumbai": 7.0, "HPCL Visakhapatnam": 7.0, "CPCL Chennai": 7.0,
    "ONGC Mangalore (OMPL)": 8.0,
}

# --- source country -> (grade, API, sulphur%, chokepoints transited, voyage days)
# chokepoints = blockable straits ONLY. Cape / open-ocean routes have none.
COUNTRY_INFO = {
    "RUSSIA":      ("Urals",         31.0, 1.60, (),           35),  # Cape route now
    "IRAQ":        ("Basrah",        29.5, 2.90, ("Hormuz",),   7),
    "SAUDI ARAB":  ("Arab Medium",   31.0, 2.40, ("Hormuz",),   6),
    "U ARAB EMTS": ("Murban/Zakum",  37.0, 1.20, ("Hormuz",),   5),
    "U S A":       ("WTI Midland",   41.5, 0.24, (),           40),
    "KUWAIT":      ("Kuwait Export", 31.0, 2.55, ("Hormuz",),   6),
    "NIGERIA":     ("Bonny Light",   35.3, 0.15, (),           22),
    "ANGOLA":      ("Girassol",      30.0, 0.33, (),           25),
    "BRAZIL":      ("Tupi",          29.0, 0.40, (),           30),
    "COLOMBIA":    ("Vasconia",      24.0, 1.00, (),           30),
    "OMAN":        ("Oman Export",   33.0, 1.20, (),            7),  # bypasses Hormuz
    "QATAR":       ("Qatar Marine",  36.0, 1.45, ("Hormuz",),   5),
    "VENEZUELA":   ("Merey",         16.0, 2.50, (),           35),
    "EGYPT A RP":  ("Egypt Blend",   33.0, 1.50, ("Suez",),    12),
    "MEXICO":      ("Maya",          22.0, 3.30, (),           35),
    "CANADA":      ("Cold Lake",     21.0, 3.50, (),           40),
    "ALGERIA":     ("Saharan Blend", 45.0, 0.10, (),           15),
    "CONGO P REP": ("Djeno",         27.0, 0.30, (),           25),
    "GABON":       ("Rabi Light",    33.0, 0.10, (),           25),
    "NORWAY":      ("J. Sverdrup",   28.0, 0.80, (),           25),
}
DEFAULT_INFO = ("Other", 32.0, 1.10, (), 28)
BBL_PER_TON = 7.33

# --- Asphaltene content (wt %) per source grade -------------------------------
# Added on the advice of Dr. Uttam Kumar Bhui (Professor, Petroleum Engineering,
# PDEU), whose field is crude characterization. His point, verbatim in substance:
# "API gravity is a SURFACE property... other composition-level components are
#  also important - the group of components called saturate, aromatic, resin and
#  asphaltene [SARA]... the SARA distribution pattern determines the output."
# Asphaltene is the SARA fraction that most constrains what a refinery can run:
# it is the coke/sludge precursor, so only deep-conversion (high-Nelson, coker)
# refineries can process asphaltene-rich crude. Values are public-assay approx.
ASPHALTENE = {
    "RUSSIA": 2.8, "IRAQ": 3.6, "SAUDI ARAB": 3.0, "U ARAB EMTS": 0.8,
    "U S A": 0.2, "KUWAIT": 3.4, "NIGERIA": 0.5, "ANGOLA": 1.0,
    "BRAZIL": 1.2, "COLOMBIA": 5.0, "OMAN": 1.5, "QATAR": 0.9,
    "VENEZUELA": 11.0, "EGYPT A RP": 2.0, "MEXICO": 10.0, "CANADA": 12.0,
    "ALGERIA": 0.1, "CONGO P REP": 1.0, "GABON": 0.3, "NORWAY": 0.6,
}
DEFAULT_ASPHALTENE = 1.5


def asphaltene(country: str) -> float:
    return ASPHALTENE.get(country.strip().upper(), DEFAULT_ASPHALTENE)


def country_info(country: str):
    return COUNTRY_INFO.get(country.strip().upper(), DEFAULT_INFO)


def _read_one(path: Path) -> pd.DataFrame:
    raw = pd.read_excel(path, engine="xlrd", header=None)
    hdr = raw[raw[0].astype(str).str.strip() == "Commodity"].index[0]
    df = raw.iloc[hdr + 1:].copy()
    df.columns = ["commodity", "country", "port", "unit", "qty", "val_inr", "val_usd"]
    df = df[df["commodity"].astype(str).str.contains("PETROLEUM", na=False)]
    for c in ("qty", "val_inr", "val_usd"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["qty"])
    df["country"] = df["country"].astype(str).str.strip()
    df["port"] = df["port"].astype(str).str.strip()
    df["refinery"] = df["port"].map(lambda p: PORT_TO_REFINERY.get(p, p.title()))
    return df


_FALLBACK_NOTICE_SHOWN = False


def _fallback() -> dict:
    """Committed derivation of the raw DGCIS .xls (same numbers, reproducible).

    The raw government .xls files are large and live outside the repo; the repo
    ships the DERIVED dataset (engine/data/india_refinery_diets.json), written by
    `python -m engine.refdata` from the originals. Anyone cloning the repo gets
    bit-identical model inputs without needing the raw files.
    """
    global _FALLBACK_NOTICE_SHOWN
    if not DERIVED_JSON.exists():
        raise FileNotFoundError(
            f"Neither the raw DGCIS .xls ({XLS_FILES[0].name}) nor the derived "
            f"dataset ({DERIVED_JSON}) is present. Re-clone the repo or run "
            f"`python -m engine.refdata` next to the raw files.")
    if not _FALLBACK_NOTICE_SHOWN:
        print("[refdata] raw DGCIS .xls not found -> using the committed "
              "derived dataset (engine/data/india_refinery_diets.json)")
        _FALLBACK_NOTICE_SHOWN = True
    d = json.loads(DERIVED_JSON.read_text())
    return d if "refineries" in d else {"refineries": d, "national": None}


def load_diets(path: Path = XLS_FILES[0]) -> dict:
    """Return {refinery: {"total_tons", "nelson", "diet": {country: tons}}}.

    Prefers the raw DGCIS .xls when present (author's machine); otherwise falls
    back to the committed derived JSON so a fresh clone runs identically.
    """
    if not path.exists():
        return _fallback()["refineries"]
    df = _read_one(path)
    out: dict = {}
    for ref, g in df.groupby("refinery"):
        diet = g.groupby("country").qty.sum().sort_values(ascending=False)
        out[ref] = {
            "total_tons": float(diet.sum()),
            "nelson": NELSON.get(ref),
            "diet": {c: float(v) for c, v in diet.items()},
        }
    return out


def national_by_country(path: Path = XLS_FILES[0]) -> dict:
    """{country: {tons, usd, price_bbl}} — realized landed price from real values."""
    if not path.exists():
        nat = _fallback()["national"]
        if nat is None:
            raise FileNotFoundError(
                "Derived dataset predates schema 2 (no national table). "
                "Run `python -m engine.refdata` next to the raw .xls once.")
        return nat
    df = _read_one(path)
    out: dict = {}
    for c, g in df.groupby("country"):
        tons = float(g.qty.sum()); usd = float(g.val_usd.sum())
        price = usd / (tons * BBL_PER_TON) if tons > 0 else 0.0
        out[c] = {"tons": tons, "usd": usd,
                  # drop absurd values from tiny re-export rows
                  "price_bbl": round(price, 1) if 20 < price < 160 else None}
    return out


def chokepoint_exposure(diet: dict) -> dict:
    """Share of a refinery's diet transiting each blockable chokepoint."""
    tot = sum(diet.values()) or 1.0
    exp: dict = {}
    for country, tons in diet.items():
        for ck in country_info(country)[3]:
            exp[ck] = exp.get(ck, 0.0) + tons / tot
    return exp


def avg_quality(diet: dict) -> tuple[float, float]:
    """Volume-weighted API and sulphur of a refinery's real diet."""
    tot = sum(diet.values()) or 1.0
    api = sum(country_info(c)[1] * t for c, t in diet.items()) / tot
    sul = sum(country_info(c)[2] * t for c, t in diet.items()) / tot
    return round(api, 1), round(sul, 2)


def build_and_save() -> dict:
    """Derive from the raw .xls and commit the result (schema 2: diets + national).

    This is the reproducibility bridge: the repo ships this JSON, so every run
    (validation, exports, the war-room) works from a fresh clone with no raw files.
    """
    refs = load_diets()
    nat = national_by_country()
    payload = {
        "schema": 2,
        "source_file": XLS_FILES[0].name,
        "note": "Derived from official DGCIS port-wise trade records; "
                "regenerate with `python -m engine.refdata` next to the raw .xls.",
        "refineries": refs,
        "national": nat,
    }
    DERIVED_JSON.parent.mkdir(parents=True, exist_ok=True)
    DERIVED_JSON.write_text(json.dumps(payload, indent=2))
    return refs


if __name__ == "__main__":
    refs = build_and_save()
    nat: dict = {}
    for r in refs.values():
        for c, t in r["diet"].items():
            nat[c] = nat.get(c, 0.0) + t
    gtot = sum(nat.values())
    print("=" * 84)
    print("  REAL REFINERY DIETS  (DGCIS May-2025 to Apr-2026)")
    print("=" * 84)
    print(f"  national: {gtot/1e6:.1f} MT/yr across {len(refs)} refineries\n")
    hdr = f"  {'refinery':<24}{'MT/yr':>7}{'Nelson':>7}{'Hormuz%':>8}{'avgAPI':>7}{'avgS%':>6}  top suppliers"
    print(hdr); print("  " + "-" * (len(hdr)))
    for ref, d in sorted(refs.items(), key=lambda x: -x[1]["total_tons"]):
        if d["total_tons"] / 1e6 < 1:
            continue
        exp = chokepoint_exposure(d["diet"]); api, sul = avg_quality(d["diet"])
        top = ", ".join(f"{c.title()} {t/d['total_tons']*100:.0f}%"
                        for c, t in list(d["diet"].items())[:3])
        nel = d["nelson"] or 0
        print(f"  {ref:<24}{d['total_tons']/1e6:>7.1f}{nel:>7.1f}"
              f"{exp.get('Hormuz',0)*100:>7.0f}%{api:>7.1f}{sul:>6.2f}  {top}")
    print("\n  national Hormuz exposure: "
          f"{sum(t for c,t in nat.items() if 'Hormuz' in country_info(c)[3])/gtot*100:.0f}%")
    print(f"  saved -> {DERIVED_JSON.relative_to(_PROJECT)}")
