"""
KARNADHAR — Real model builder   (the engine's real-data foundation)
====================================================================

Builds the refineries and crude grades the optimizer solves over, entirely from
REAL data:

  * refinery diets, volumes and prices  -> official DGCIS trade records
  * refinery capability (API window, sulphur + asphaltene ceilings)
        -> DERIVED from each refinery's ACTUAL diet + its Nelson complexity.
           A refinery that already runs 1.8% sulphur demonstrably has the
           desulphurisation to do so — the real diet reveals the capability, so
           we no longer guess.
  * crude quality -> API, sulphur AND **asphaltene** (SARA), per Dr. Uttam Bhui
           (PDEU): "API gravity is a surface property... the SARA distribution
           pattern determines the output." Asphaltene is the coke precursor, so
           only deep-conversion (high-Nelson) refineries can digest it.

Disruption is fully general: block ANY chokepoint and/or sanction ANY supplier,
and each refinery's affected volume falls straight out of its real diet.
"""

from __future__ import annotations
from dataclasses import dataclass, field

from engine.refdata import (
    load_diets, national_by_country, country_info, asphaltene, BBL_PER_TON,
)

# tons/yr -> kb/d
def tons_to_kbd(tons: float) -> float:
    return tons * BBL_PER_TON / 365.0 / 1000.0


# how much more of a grade India could realistically buy vs what it buys today
SUPPLY_HEADROOM = 1.6
# crisis premium is applied by the scenario, not baked into the base price


@dataclass(frozen=True)
class Crude:
    name: str            # source country label (the grade it stands for)
    grade: str
    api: float
    sulphur: float
    asphaltene: float
    chokepoints: tuple
    transit_days: int
    price_usd_bbl: float
    available_kbd: float

    @property
    def is_sour(self) -> bool:
        return self.sulphur >= 1.0


@dataclass(frozen=True)
class Refinery:
    name: str
    capacity_kbd: float
    nelson: float
    diet_kbd: dict           # country -> kb/d actually imported (REAL)
    api_opt: float
    api_min: float
    api_max: float
    max_sulphur: float       # single-grade ceiling
    desulph_limit: float     # blend-average ceiling
    max_asphaltene: float    # blend-average ceiling (coke precursor)
    yield_pen_per_api: float

    def volume_at_risk(self, blocked_chokepoints: set, sanctioned: set) -> float:
        """kb/d of THIS refinery's real diet lost to the disruption."""
        lost = 0.0
        for country, kbd in self.diet_kbd.items():
            cps = set(country_info(country)[3])
            if (cps & blocked_chokepoints) or (country in sanctioned):
                lost += kbd
        return round(lost, 1)


def _derive_config(nelson: float, api_opt: float, blend_s: float,
                   max_s_in_diet: float, blend_asph: float) -> dict:
    """Derive processing limits from the REAL diet + Nelson complexity.

    Rules (explicit and expert-calibratable — pending Dr. Bhui's written reply):
      - it already runs its current blend, so its ceilings are >= today's values
      - deep-conversion (high Nelson) => can go very heavy, but CANNOT run a very
        light slate (the coker/vacuum units would be starved) -> tighter api_max
      - simple (low Nelson) => needs lighter, sweeter, low-asphaltene feed
    """
    if nelson >= 12:            # deep conversion, full coker
        api_min, api_span, asph_cap, pen = 18.0, 8.0, 12.0, 0.70
    elif nelson >= 9:           # complex
        api_min, api_span, asph_cap, pen = 24.0, 10.0, 6.0, 0.90
    else:                       # medium / simple
        api_min, api_span, asph_cap, pen = 29.0, 12.0, 3.0, 1.10
    return dict(
        api_min=api_min,
        api_max=round(api_opt + api_span, 1),
        desulph_limit=round(blend_s * 1.15, 2),        # 15% headroom over today
        max_sulphur=round(max_s_in_diet * 1.10, 2),
        max_asphaltene=round(max(asph_cap, blend_asph * 1.2), 1),
        yield_pen_per_api=pen,
    )


def build_refineries(min_mt: float = 1.0) -> list[Refinery]:
    """Real refineries with real diets and derived, data-grounded configs."""
    raw = load_diets()
    out: list[Refinery] = []
    for name, d in raw.items():
        if d["total_tons"] / 1e6 < min_mt:
            continue
        diet_kbd = {c: round(tons_to_kbd(t), 1) for c, t in d["diet"].items()}
        tot = sum(diet_kbd.values()) or 1.0
        api_opt = sum(country_info(c)[1] * v for c, v in diet_kbd.items()) / tot
        blend_s = sum(country_info(c)[2] * v for c, v in diet_kbd.items()) / tot
        blend_a = sum(asphaltene(c) * v for c, v in diet_kbd.items()) / tot
        max_s = max(country_info(c)[2] for c in diet_kbd)
        nelson = d["nelson"] or 8.0
        cfg = _derive_config(nelson, api_opt, blend_s, max_s, blend_a)
        out.append(Refinery(
            name=name, capacity_kbd=round(tot, 1), nelson=nelson,
            diet_kbd=diet_kbd, api_opt=round(api_opt, 1), **cfg))
    return sorted(out, key=lambda r: -r.capacity_kbd)


def build_crudes() -> list[Crude]:
    """Real supplier grades with real volumes + realized landed prices."""
    nat = national_by_country()
    out: list[Crude] = []
    for country, v in nat.items():
        grade, api, sul, cps, transit = country_info(country)
        kbd = tons_to_kbd(v["tons"])
        if kbd < 1:
            continue
        price = v["price_bbl"] or 80.0
        out.append(Crude(
            name=country, grade=grade, api=api, sulphur=sul,
            asphaltene=asphaltene(country), chokepoints=tuple(cps),
            transit_days=transit, price_usd_bbl=price,
            available_kbd=round(kbd * SUPPLY_HEADROOM, 1)))
    return sorted(out, key=lambda c: -c.available_kbd)


@dataclass
class Disruption:
    """A scenario: block chokepoints and/or sanction suppliers."""
    name: str
    blocked_chokepoints: set = field(default_factory=set)
    sanctioned_countries: set = field(default_factory=set)
    scramble_premium_usd: float = 5.0
    alt_supply_factor: float = 1.0

    def is_cut(self, crude: Crude) -> bool:
        return bool(set(crude.chokepoints) & self.blocked_chokepoints) \
            or crude.name in self.sanctioned_countries

    def available(self, crudes: list[Crude]) -> list[Crude]:
        return [c for c in crudes if not self.is_cut(c)]


if __name__ == "__main__":
    refs, crudes = build_refineries(), build_crudes()
    print("=" * 96)
    print("  KARNADHAR REAL MODEL  —  refineries & configs DERIVED from real DGCIS diets + Nelson")
    print("=" * 96)
    h = (f"  {'refinery':<24}{'kb/d':>7}{'Nels':>6}{'APIopt':>7}{'APIwin':>12}"
         f"{'maxS':>6}{'dsulph':>7}{'maxAsph':>8}")
    print(h); print("  " + "-" * (len(h) - 2))
    for r in refs:
        print(f"  {r.name:<24}{r.capacity_kbd:>7.0f}{r.nelson:>6.1f}{r.api_opt:>7.1f}"
              f"{f'{r.api_min:.0f}-{r.api_max:.0f}':>12}{r.max_sulphur:>6.2f}"
              f"{r.desulph_limit:>7.2f}{r.max_asphaltene:>8.1f}")
    print(f"\n  crude grades: {len(crudes)}  (real volumes + realized landed prices)")
    hh = f"  {'source':<16}{'grade':<16}{'API':>6}{'S%':>6}{'Asph%':>7}{'$/bbl':>7}{'avail':>8}  route"
    print(hh); print("  " + "-" * (len(hh) - 2))
    for c in crudes[:12]:
        rt = "/".join(c.chokepoints) if c.chokepoints else "open (Cape)"
        print(f"  {c.name.title():<16}{c.grade:<16}{c.api:>6.1f}{c.sulphur:>6.2f}"
              f"{c.asphaltene:>7.1f}{c.price_usd_bbl:>7.1f}{c.available_kbd:>8.0f}  {rt}")
