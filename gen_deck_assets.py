"""
Generate chart images for the pitch deck (dark war-room styling, transparent bg).
Run:  python gen_deck_assets.py     ->  assets/*.png
"""
from __future__ import annotations
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager  # noqa

ASSETS = Path(__file__).parent / "assets"
ASSETS.mkdir(exist_ok=True)

TEAL, AMBER, RED, BLUE = "#5DCAA5", "#F2A623", "#E24B4A", "#3B8BD4"
TEXT, MUT, GRID = "#E8EDF2", "#8B95A3", "#2A3442"


def style_ax(ax):
    ax.set_facecolor("none")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=MUT, labelsize=11)
    ax.yaxis.label.set_color(MUT)
    ax.xaxis.label.set_color(MUT)


# ------------------------------------------------------------------ #
# 1) SIGNAL — real GDELT coverage vs baseline, alert vs market       #
# ------------------------------------------------------------------ #
from engine.signals.gdelt import timeline_with_fallback
from engine.signals.agent import GeopoliticalRiskAgent

pts, src = timeline_with_fallback('"strait of hormuz"', "20250601000000",
                                  "20250630000000", "hormuz_2025_06_representative.json")
bt = GeopoliticalRiskAgent().assess(pts, date(2025, 6, 23))
mu = bt.baseline_mean or 1e-9

# extend the axis to the market day (coverage series may end earlier)
from datetime import timedelta
first = bt.series[0].day
span = (bt.market_day - first).days + 2
days = [first + timedelta(d) for d in range(span)]
by_day = {p.day: p for p in bt.series}
mult = [(by_day[d].volume / mu) if d in by_day else 0 for d in days]
colors = [AMBER if (d in by_day and by_day[d].alerted) else "#33414F" for d in days]

fig, ax = plt.subplots(figsize=(8.6, 3.6), dpi=200)
fig.patch.set_alpha(0)
style_ax(ax)
ax.bar(range(len(days)), mult, color=colors, width=0.72)
ax.set_xticks(range(0, len(days), 2))
ax.set_xticklabels([d.strftime("%b %d") for d in days[::2]], rotation=45,
                   ha="right", fontsize=9, color=MUT)
ax.set_ylabel("news coverage  (x quiet baseline)", fontsize=11)

ai = days.index(bt.alert_day)
mi = days.index(bt.market_day)
ax.axvline(ai, color=TEAL, lw=1.6, ls="--", alpha=.9)
ax.axvline(mi, color=RED, lw=1.6, ls="--", alpha=.9)
ymax = max(mult)
ax.annotate("KARNADHAR ALERT", (ai, ymax * .96), color=TEAL, fontsize=11,
            fontweight="bold", ha="right", xytext=(-6, 0), textcoords="offset points")
ax.annotate("Brent +8% session", (mi, ymax * .82), color=RED, fontsize=11,
            fontweight="bold", ha="left", xytext=(6, 0), textcoords="offset points")
ax.annotate(f"{bt.lead_days}-day lead", ((ai + mi) / 2, ymax * .60), color=TEXT,
            fontsize=13, fontweight="bold", ha="center")
ax.annotate("", xy=(mi, ymax * .55), xytext=(ai, ymax * .55),
            arrowprops=dict(arrowstyle="<->", color=TEXT, lw=1.4))
fig.tight_layout()
fig.savefig(ASSETS / "signal_chart.png", transparent=True, bbox_inches="tight")
plt.close(fig)
print("signal_chart.png  (source:", src + ")")

# ------------------------------------------------------------------ #
# 2) CASCADE — Brent & current-account deficit vs closure severity   #
# ------------------------------------------------------------------ #
from engine.cascade import compute_cascade, CascadeParams

p = CascadeParams()
fracs = [0, 0.25, 0.5, 0.75, 1.0]
rows = [compute_cascade(f, p) for f in fracs]
x = [f * 100 for f in fracs]
brent = [r.brent_usd for r in rows]
cad = [r.stressed_cad_pct_gdp for r in rows]

fig, ax1 = plt.subplots(figsize=(8.6, 3.8), dpi=200)
fig.patch.set_alpha(0)
style_ax(ax1)
ax1.plot(x, brent, color=AMBER, lw=2.6, marker="o", ms=6, label="Brent $/bbl")
ax1.set_xlabel("Strait of Hormuz closure severity (%)", fontsize=11)
ax1.set_ylabel("Brent  ($/bbl)", fontsize=11)
ax1.grid(axis="y", color=GRID, lw=.6, alpha=.6)

ax2 = ax1.twinx()
ax2.set_facecolor("none")
for s in ax2.spines.values():
    s.set_visible(False)
ax2.tick_params(colors=MUT, labelsize=11)
ax2.plot(x, cad, color=RED, lw=2.6, marker="s", ms=6, label="Current-account deficit % GDP")
ax2.fill_between(x, cad, color=RED, alpha=.12)
ax2.set_ylabel("Current-account deficit  (% of GDP)", fontsize=11, color=MUT)

for xi, b in zip(x, brent):
    ax1.annotate(f"${b:.0f}", (xi, b), textcoords="offset points", xytext=(10, -14),
                 ha="left", color=AMBER, fontsize=10, fontweight="bold")
for xi, c in zip(x[2:], cad[2:]):
    ax2.annotate(f"{c:.1f}%", (xi, c), textcoords="offset points", xytext=(-8, 10),
                 ha="right", color=RED, fontsize=10, fontweight="bold")

ax1.annotate("pipeline bypass\nabsorbs a 25% closure", (25, 97), color=TEAL,
             fontsize=10, ha="center", fontweight="bold")
fig.tight_layout()
fig.savefig(ASSETS / "cascade_chart.png", transparent=True, bbox_inches="tight")
plt.close(fig)
print("cascade_chart.png")
