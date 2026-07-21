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
  insurance; **twin-deficit** reframe → CAD block added to the cascade (0.7% → 6.1%
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
verified for Cloud Run.

## 12 · The second self-audit (judge-grade hardening)
We attacked our own work again, as a hostile judge, and found real defects:
- **Fatal**: a fresh clone crashed — the loader wanted the raw DGCIS `.xls`
  (outside the repo). Fixed with a schema-versioned committed derivation
  (`engine/data/india_refinery_diets.json`) + transparent fallback; CI now runs
  the exact judge path on every push.
- **Artifact**: our own plan showed INFEASIBLE on the Russia scenario — a
  boundary-equal breach (`2.04>2.04`) from a 1e-6 epsilon meeting 0.1-kb/d
  rounding. Fixed with a rounding-aware blend tolerance + regression check.
- **Modeling**: LP blend caps were normalised by the full gap (invalid under
  scarce supply) and used a big-M objective. Replaced with a **two-stage
  lexicographic LP** (max fill, then min cost) with volume-relative blend caps.
- **Honesty metric**: naive "fills" compound-shock gaps with un-runnable crude.
  Added **usable shortfall** (unmet + un-runnable): naive 2,670 vs ours 2,166.
- **Decision layer**: stage-2 **shadow prices** (marginal $/day of one more kb/d
  of each scarce grade — scarcity turns out to be heavy coker feed, the wedge
  priced) and the **VLCC ton-mile cost** of rerouting (+66 tankers on Hormuz).
- Consistency: cascade banner said 40% Hormuz share vs the derived 46%; commodity
  HHI counted "OTHERS" as one supplier; demo script quoted curated-model numbers
  over real-model screens. All reconciled; the two model tiers are now labelled.
Validation now **45/45**, run in CI (engine + production frontend build).

## 13 · Brief-coverage pass (nothing on their list left unbuilt)
Re-read the official problem statement line by line and built what was named
but missing:
- **Red Sea suspension** scenario (brief-named) → the differentiating insight:
  India's crude is Cape-insulated (54 kb/d) while **edible oils take 18%**
  (Black-Sea sunflower via Suez) — commodity-specific arteries, proven.
- **SPR drawdown scheduler** (`engine/spr.py`, brief's "Strategic Reserve
  Optimisation Agent") → hold / bridge / ration verdicts with draw rate,
  depletion % and residual demand-management need (compound shock: RATION —
  2,136 kb/d max draw still leaves ~30 kb/d to demand management).
- **Executive brief in the war-room** (card ⑤) — the pipeline's final product,
  composed engine-side from real numbers; template words, Claude drop-in.
- **EF-3 "testable" made visible**: Brent sensitivity band ($150–$244 at full
  closure) shown in-product, not just in code.
- **Bypass pipelines on the map** (Petroline + ADCOP) — the cascade's 6.5 Mb/d
  nuance drawn where it physically exists.
- Small-volume LP rounding fix (0.01 kb/d granularity) caught by the new Red
  Sea regression check. Validation now **50/50** (later 57/57), in CI.

## 14 · From status display to decision display
The sharpest self-critique yet: the map showed red/green *status* but never the
optimizer's *answer* — the one thing that makes it more than a dashboard. Fixed:
- **Optimizer flows** — every smart-plan allocation is drawn as an animated,
  volume-weighted flow from its source, along its real corridor, into the exact
  refinery it feeds (hover: "Russia → RIL Jamnagar · 657.9 kb/d · LP-assigned").
  Baseline corridors dim to ghosts; the plan carries the picture. Route
  geometry made truthful: chokepoint-free voyages ≥30 days draw via the Cape —
  matching the transit days the LP actually charges.
- **3D globe / 2D map toggle** (runtime projection switch; the isStyleLoaded
  false-negative trap documented in code).
- **Knowledge graph is now an instrument**: wheel-zoom to cursor, pan, drag
  nodes (sim reheats), double-click reset, zoom buttons, labels densify on zoom.
- **Terminal pass**: live ticker tape (scenario · gap · Brent · CAD · reroute ·
  VLCC · SPR · solve-ms), tabular monospace numerals, status LEDs, thin
  scrollbars — Bloomberg grammar without the kitsch.

## 15 · The reroute deep-dive (ranking, defended)
User pushback: red/green lines aren't optimisation; the map must *rank the best
routes and prove why*, and two bugs (white popup, tangled lines) had to go.
- **Bugs**: MapLibre popups forced to the dark theme (default white hid our light
  text); flows bowed into per-flow arcs so parallel corridors fan into a readable
  ribbon instead of a straight-line tangle.
- **Deep-dive page**: selecting a disruption opens a full-screen decision view —
  alternative corridors ranked #1..N, each with a self-defending justification,
  BINDING/slack tag, LP marginal value, and the refineries it feeds; click a
  corridor and it isolates on the map (`focusSource` flow-filter) with a live
  derivation panel; long-tail (<1% of gap) collapses; a severed-corridors section
  shows the bigger suppliers that were cut.
- **Ranking metric** — decided via an adversarial design panel (3 diverse
  proposals + a hostile-judge synthesis). It rejected the two tempting metrics:
  *cheapest-first* and *shadow-price-first* both crown a ~3 kb/d rounding-error
  corridor while burying the 90% lifeline (a scarcity artifact of the LP dual).
  The defensible metric is the LP's own **stage-1 objective — volume committed**
  (secure grade-feasible barrels), cost as the stage-2 tiebreak, with the shadow
  price shown only as a badge on material (≥50 kb/d) binding corridors. The #1
  card self-defends ("+$5/bbl above the cheapest survivor — ranks first on secured
  volume, not price"). Validation now **57/57**, incl. a check that a bigger-volume
  slack corridor outranks a tiny binding one.

## 16 · Calculation audit (adversarial, multi-discipline) + the identity
"Is every calculation correct?" — so we ran a 4-lens adversarial audit (energy
economist, petroleum engineer, macroeconomist, LP/OR) and fixed the confirmed defects:
- **Sanctions were modelled as a global supply shock** (the biggest error). A Russia
  sanction was pushed through the Hormuz cascade → a fictional Brent +71% and CAD
  3.8%. But a sanction REDISTRIBUTES barrels (Russia → China); global Brent barely
  moves. Split the economics by channel: Hormuz = global supply shock (Brent spike);
  **sanction = discount-loss** (India's real cost is the ~$3.5bn/yr Urals discount it
  can no longer capture + the LP re-sourcing premium), CAD 0.7 → 0.8%, not 3.8%; minor
  strait = freight premium. `compute_sanction_impact` + an `economic_impact` dispatcher.
- **Refinery windows were inverted** (certain bug). The derived config gave the
  deep-conversion coker the *narrowest* crude window — Jamnagar (Nelson 21) was barred
  from light-sweet WTI/Saharan while a simple hydroskimmer could run them. Backwards: a
  full coker is the *most* flexible asset. Widened the window monotonically with Nelson
  (deep 14–47 incl. Merey and WTI; simple 28–44). Frees the LP to route open-ocean
  light crude to India's largest refinery in a Hormuz closure — the wedge still holds
  (naive infeasible on sulphur; smart feasible).
- **Macro vintage** made consistent: GDP relabelled to true FY24 ($3,550bn, not the
  FY25 $3,900bn) and baseline CAD to the FY24 0.7% (not 1.2%). The two errors were
  offsetting, so the flagship **6.1%** headline is unchanged — but now internally
  consistent, and the gross-vs-net-imports choice is documented (gross, per the ORF
  USD-outflow framing). Deferred as documented refinements: asphaltene colloidal
  stability (vs linear average) and an asymmetric yield penalty.
- **Identity**: a logo that means something — **the Ashoka Chakra rendered as a
  ship's helm wheel**. *Karnadhar* is the helmsman; India's 24-spoke national wheel
  *is* a wheel; the tricolour rides the four helm handles (saffron, green) and India
  sits at the teal command-centre hub. In the header and as the favicon.
Validation now **62/62** (sanction-channel + vintage checks added), all in CI.
