# KARNADHAR — India's Energy Supply-Chain Command Center

> *Karnadhar (कर्णधार, Sanskrit): the helmsman who steers the ship through the storm.*
> **From a 47-day crisis to a 45-millisecond command.**

Built for the **ET AI Hackathon 2026 — Phase 2**, Problem #2 (*AI-Driven Energy Supply
Chain Resilience for Import-Dependent Economies*), by **Mann Sutariya** (Pandit Deendayal
Energy University).

India imports **88%** of its crude; **46%** of it transits the Strait of Hormuz — a number
this system **derives from official customs records**, not from a report. Strategic
reserves cover ~9.5 days (voluntary — India is outside the IEA's 90-day mandate). When a
chokepoint is threatened, economies without response intelligence take **47 days longer**
to stabilise supply (McKinsey). KARNADHAR compresses signal → executable recommendation
to **45 ms**.

---

## The wedge: crude oil is not fungible

Every generic "resilience dashboard" treats oil as one number: barrels. Reality: a
refinery is an engine tuned to a fuel. Three properties decide whether a barrel is
runnable — **API gravity** (light/heavy), **sulphur** (sweet/sour), and **asphaltene
content** (the SARA dimension, added on the guidance of Prof. U. K. Bhui, Petroleum
Engineering, PDEU). A deep-conversion coker like Jamnagar (Nelson 21.1) digests almost
anything but starves on ultra-light condensate; a simple refinery like Mumbai (Nelson 7)
cannot touch sour crude.

**The headline result:** in a full Hormuz closure, the naive "oil is oil" plan assigns
**250 kb/d to refineries that physically cannot run it** — infeasible for a *grade*
reason. KARNADHAR's grade-aware LP produces a fully feasible national reroute and
protects **$3.15M/day of product yield** (~$1.15bn/yr).

## What it is

```
signal  →  scenario  →  reroute  →  brief
GDELT news +    glass-box economic   grade-aware LP     executive memo —
live AIS ships  cascade + twin       over real DGCIS    LLM writes words,
                deficit              refinery diets     never numbers
```

- **Real data spine** — official DGCIS port-wise import records (May 2024–Apr 2026)
  give every refinery its *actual* crude diet, Hormuz exposure, and realized landed
  prices. PPAC capacities, public Nelson complexity, crude assay libraries.
- **Knowledge graph** — the supplier→route→chokepoint→refinery relationship model,
  materialised as a typed property graph with per-edge provenance
  (`python export_kg.py` → 50 nodes, 163 edges: SHIPS_VIA / SUPPLIES / THREATENS).
- **General disruption model** — block any chokepoint (Hormuz, Bab-el-Mandeb, Suez,
  Malacca, Cape) *and/or* sanction any supplier (e.g. Russia = 1,590 kb/d), in any
  combination.
- **Honest engine** — under compound shocks (Hormuz + OPEC squeeze) even the optimal
  reroute leaves demand unmet; KARNADHAR quantifies the gap instead of pretending.
- **Twin-deficit cascade** — the India-specific vulnerability (reviewed with Lydia
  Powell, Distinguished Fellow, ORF): a full closure adds ~$191bn/yr in USD outflow,
  blowing the current-account deficit from 1.2% → 6.1% of GDP. The binding constraint
  is the balance of payments, not the barrels.
- **Multi-commodity lens** — the framework generalised to 8 strategic imports (LNG,
  pharma APIs, semiconductors, edible oils, fertiliser, coking coal, solar PV) via a
  glass-box Import Vulnerability Index; the same disruption scored across every
  material (`python run_commodities.py` — Hormuz hits 53% of LNG, not just 46% of
  crude; Malacca is the pharma/electronics artery).
- **War-room UI** — Next.js + MapLibre command center on a **true 3D globe**
  projection with real AIS vessels: cut-vs-alive corridors, per-refinery diets on
  hover, a **knowledge-graph view** (toggle), the multi-commodity lens, and scenario
  switching with the full national plan recomputed in ~45 ms.

## Run it

```bash
# 1) Engine (Python 3.12)
pip install -r requirements.txt
python run_validate.py     # 39/39 automated checks — the proof
python run_real.py         # reroute on REAL DGCIS diets, all scenarios
python run_karnadhar.py    # end-to-end pipeline: signal → brief in ~45 ms

# 2) War-room (Node 20+)
python export_ui.py        # engine → frontend/public/karnadhar.json
cd frontend && npm install && npm run dev   # → http://localhost:3000
```

More runnables: `run_demo.py` (wedge head-to-head), `run_cascade.py` (economic cascade +
twin deficit), `run_signal.py` (GDELT 12-day-lead backtest), `run_ais.py` (live AIS),
`run_scenarios.py` (scenario library), `run_commodities.py` (multi-commodity screen),
`export_kg.py` (knowledge graph), `gen_deck_assets.py` (deck charts).

## Repository map

```
karnadhar/
├── engine/
│   ├── refdata.py       # DGCIS loader: port→refinery, country→grade/route, Nelson, asphaltene
│   ├── realmodel.py     # real refineries (configs DERIVED from diet + Nelson) + general Disruption
│   ├── realopt.py       # naive vs grade-aware LP on the real model
│   ├── data.py          # curated 15-grade / 7-refinery model (the original wedge demo)
│   ├── optimizer.py     # wedge optimizer + honest SPR evaluation
│   ├── cascade.py       # glass-box cascade incl. twin-deficit block
│   ├── scenarios.py     # scenario library
│   ├── orchestrator.py  # timed signal→scenario→reroute→brief chain
│   ├── briefing.py      # exec memo (template; Claude drop-in via ANTHROPIC_API_KEY)
│   ├── geo.py           # chokepoints, routes, coordinates
│   └── signals/
│       ├── gdelt.py     # live GDELT client + cache + labelled fallback
│       ├── agent.py     # risk scoring, alert rule, lead-time backtest
│       ├── ais.py       # live aisstream.io client (per-chokepoint bboxes)
│       └── extract.py   # headline classifier (keyword; Claude drop-in)
├── api/main.py          # FastAPI backend
├── frontend/            # Next.js 16 + MapLibre war-room
├── run_*.py             # runnable proofs (see above)
├── run_validate.py      # 35-check validation suite (exit-code gated)
├── export_ui.py         # engine → UI JSON
└── deliverables/        # pitch deck (KARNADHAR_Deck.pptx) + renders
```

## Data provenance (honest by design)

| Element | Status |
|---|---|
| Refinery diets, volumes, landed prices | **Real** — DGCIS official trade records |
| Refinery capacities | **Real** — PPAC |
| National import mix, Hormuz exposure | **Derived from the real records** (46%) |
| Crude assays (API/sulphur/asphaltene) | Public assay values per source grade |
| GDELT signal series | **Real** (cached June 2025); method identical live |
| AIS vessels | **Real live** where coverage exists (Malacca verified); Hormuz snapshot labelled — free feed has no Gulf receivers |
| Refinery processing limits | **Derived** from real diet + Nelson complexity; flagged for expert calibration (in progress with Prof. Bhui) |

## Expert review

- **Lydia Powell** — Distinguished Fellow, ORF Centre for Resources Management:
  twin-deficit framing, SPR-as-voluntary-insurance, sourcing-first policy sequence.
- **Prof. U. K. Bhui** — Petroleum Engineering, PDEU: wedge validated
  (*"That is — you are perfectly right"*), SARA/asphaltene dimension.

## License / secrets

No API keys are committed (`.env` is git-ignored). The aisstream key is free; the
engine runs fully without any key (labelled fallbacks).
