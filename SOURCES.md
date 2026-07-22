# KARNADHAR — Sources & Attribution

Every input this system uses, with provenance. The design principle throughout was
**real data, honestly labelled** — where a value is a public approximation rather than
a primary record, it is marked as such (and is a single named, editable parameter in code).

---

## Primary data (the real spine)

| Source | What we use it for | Link |
|---|---|---|
| **DGCIS** — Directorate General of Commercial Intelligence & Statistics, Ministry of Commerce & Industry (Govt. of India) | Official **port-wise crude-oil import records** (refinery × source country × quantity × value). This is the backbone: every refinery's real diet, realized landed price, and the **derived 46% Hormuz exposure**. | https://www.dgciskol.gov.in |
| **PPAC** — Petroleum Planning & Analysis Cell, MoPNG | Refinery capacities, consumption, import-dependence (~88%). | https://www.ppac.gov.in |
| **ISPRL** — Indian Strategic Petroleum Reserves Ltd | Strategic reserve cover (~9.5 days), SPR context. | https://www.isprlindia.com |
| **EIA** — U.S. Energy Information Administration | Strait of Hormuz throughput (~20 Mb/d); Hormuz-bypass pipelines — Saudi **Petroline** (~5 Mb/d) + UAE **ADCOP/Fujairah** (~1.5 Mb/d). | https://www.eia.gov (Hormuz & world-oil-transit-chokepoints briefs) |
| **IEA** — International Energy Agency | World liquids supply (~102 Mb/d); the 90-day reserve mandate India sits outside. | https://www.iea.org |
| **GDELT Project** — Global Database of Events, Language & Tone (DOC 2.0 API) | Real **news-coverage-volume series** for the geopolitical early-warning signal; the June 2025 Hormuz backtest. | https://www.gdeltproject.org |
| **aisstream.io** | Live **AIS vessel positions** per chokepoint (free tier). | https://aisstream.io |
| **RBI** — Reserve Bank of India | FY24 current-account deficit ($23.2bn = **0.7% of GDP**); FX (₹/$). | https://www.rbi.org.in |
| **MoSPI** — Ministry of Statistics & Programme Implementation | FY24 nominal GDP (₹295.4 lakh crore ≈ $3,550bn at ₹83.5). | https://www.mospi.gov.in |

## Reference values & assays (public approximations, labelled in code)

| Element | Source |
|---|---|
| Crude **assays** — API gravity, sulphur %, **asphaltene (SARA)** per grade (Urals, Basrah, Arab Medium, Murban, WTI, Bonny Light, Merey, Maya, etc.) | Public producer/monitor assays: **crudemonitor.ca**, BP / ENI / Saudi Aramco / ADNOC assay sheets |
| **Nelson Complexity Index** per Indian refinery (Jamnagar 21.1, Paradip 12.2, …) | Public refinery complexity figures |
| **Urals-to-Brent discount** (~$6/bbl, FY24, narrowed from ~$30 in 2022) | Trade press — Reuters, Bloomberg, S&P Global (Platts) reporting on India's discounted Russian crude |
| **47-day** stabilisation gap for economies without automated rerouting | McKinsey energy-supply-shock analysis (cited in the ET problem statement) |
| June 2025 **US–Iran / Hormuz** escalation; Brent +8% single session | Contemporary market reporting (the backtest event) |
| Multi-commodity import figures (LNG, pharma APIs, semiconductors, edible oils, fertiliser, coking coal, solar PV) | DGCIS / commerce-ministry trade data, FAI (fertiliser), SEA (edible oil), industry reports — screening-tier approximations |

## Expert review (primary, first-hand)

- **Lydia Powell** — Distinguished Fellow, **Observer Research Foundation (ORF)**, Centre for Resources & Energy. Validated the **twin-deficit** framing, SPR-as-voluntary-insurance, and the sourcing-first policy sequence. (Email correspondence during Phase 2.)
- **Prof. Uttam Kumar Bhui** — Professor, Petroleum Engineering, **Pandit Deendayal Energy University (PDEU)**. Crude characterization; confirmed the grade-non-fungibility thesis ("you are perfectly right") and added the **SARA / asphaltene** quality axis. (Phone consultation during Phase 2.)

## Tools & libraries

- **Engine (Python 3.12):** PuLP (CBC linear-programming solver), pandas, xlrd, matplotlib, FastAPI, uvicorn.
- **War-room (Node 20):** Next.js 16, React 19, MapLibre GL 5 (globe projection), TypeScript.
- **Deck / diagrams:** pptxgenjs, matplotlib.
- **Signal / AIS clients:** custom GDELT DOC-2.0 client, aisstream WebSocket client.
- **CI:** GitHub Actions (runs the 62-check validation + production frontend build on every push).
- **Optional LLM layer:** Anthropic Claude (key-gated) writes the executive-brief *prose only* — every number always comes from the engine.

## Problem statement

**ET AI Hackathon 2026 — Phase 2, Problem Statement #2:** *AI-Driven Energy Supply
Chain Resilience for Import-Dependent Economies* (Theme: Supply Chain Intelligence /
Energy Security / Geopolitical Risk).

---

*Provenance note: DGCIS `.xls` files are Government-of-India downloads and are not
redistributed in this repo; the repo ships the schema-versioned **derived** dataset
(`engine/data/india_refinery_diets.json`), regenerable with `python -m engine.refdata`.*
