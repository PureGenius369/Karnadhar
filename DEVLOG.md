# KARNADHAR — Development Log

A record of how this system evolved, including the mistakes we caught in our own work.
(Original-work note: everything here was designed and built during Phase 2 of the
ET AI Hackathon 2026, with AI pair-assistance, on public data.)

## 0 · Strategy
Chose Problem #2 (energy supply-chain resilience) and refused the generic take.
The differentiator: **crude oil is not fungible** — model the reroute the way a
refinery economist would (grade compatibility, transit time, reserve coupling).

## 1 · First engine
Naive-vs-grade-aware planners over a curated 15-grade / 7-refinery model; PuLP LP.

## 2 · The self-audit (turning point)
We stopped and attacked our own result and found 4 flaws — the worst: our "win" came
from supply over-subscription (a strawman), not from grade. Fixes: fair steelman
baseline (cheapest-first, supply-respecting), realistic API windows so grade truly
binds (45-API condensate vs cokers), honest like-for-like SPR math (~22 effective
days vs 18-day bridge), crisis scramble premium. The headline became honest:
**naive infeasible for a grade reason; ours feasible.**

## 3 · Glass-box cascade
closure → net shortfall (after Saudi/UAE pipeline bypass) → Brent → import bill →
pump price → CPI/GDP. Every parameter named; sensitivity one call.

## 4 · Real signals
GDELT client (live + cache + labelled fallback) with an explainable alert rule
(≥3× baseline sustained 2 days). Backtest on the real June-2025 series: alert
June 11 → Brent +8% June 23 = **12-day lead**.

## 5 · Orchestrator
signal → scenario → reroute → brief, timed end-to-end: **~45 ms**. The LLM (optional,
key-gated) writes words only; numbers always come from the engine.

## 6 · "Strong core first" (user's call, correct)
- **Real calibration**: PPAC capacities; 4.84 Mb/d imports (DGCIS 2024); real mix.
- **Scenario library**: route-aware disruption; graceful partial-fill (unmet kb/d).
- **Live AIS**: aisstream client; real vessels verified at Malacca; Gulf gap
  documented honestly (free feed has no Persian-Gulf receivers).

## 7 · Expert reviews
- **Lydia Powell (ORF)**: sourcing-first for India validated; SPR = voluntary
  insurance; **twin-deficit** reframe → CAD block added to the cascade (1.2% → 6.1%
  of GDP at full closure).
- **Prof. U. K. Bhui (PDEU)**, phone: wedge "perfectly right"; API is a *surface*
  property → **SARA/asphaltene** added as a third quality axis; crude-to-chemicals
  ("opportunity crude") noted for roadmap.

## 8 · The breakthrough dataset
Official **DGCIS port-wise import records** (May 2024–Apr 2026) → real per-refinery
diets (Vadinar 56% Russian; Mumbai 60% Hormuz-exposed), realized landed prices, and
a **derived 46% national Hormuz exposure**. Refinery processing limits now *derived*
from each refinery's real diet + public Nelson complexity (expert calibration pending).
Disruption generalised: block any chokepoint AND/OR sanction any supplier.

## 9 · War-room
Next.js 16 + MapLibre command center over exported engine JSON: live routed map,
cut/alive corridors, hover diets, scenario switching (~45 ms recompute).
Hard-won lessons: React 19 StrictMode needs map cleanup; embedded preview surfaces
report `visibilityState=hidden` so rAF never fires → wrote a native-vs-timer rAF
shim (also protects screen recording); MapLibre v5 needs
`canvasContextAttributes.preserveDrawingBuffer` for canvas capture.

## 10 · Validation
`run_validate.py`: falsifiable checks — wedge, cascade monotonicity + bypass
nuance, signal lead, real-diet integrity, honest unmet demand, UI export
consistency. Exit-code gated.

## 11 · Workshop-driven upgrades (final sprint)
From the official Phase-2 workshop (Octave/ET): knowledge-graph visualisation
"earns additional advantage" → built the in-app **KG view** (canvas force layout,
scenario-aware threat edges). "Not only crude oil — any material" → built the
**multi-commodity lens**: 8 strategic imports, glass-box Import Vulnerability
Index, per-scenario affected shares (Hormuz hits 53% of LNG; Malacca is the
pharma/semiconductor artery; coking coal proves the framework discriminates).
Map upgraded to a **true 3D globe** with real AIS vessels. Production build
verified for Cloud Run. Validation now **39/39**.
