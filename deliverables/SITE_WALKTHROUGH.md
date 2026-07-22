# KARNADHAR — Site Walkthrough (know what each part does, then talk naturally)

**Don't memorise lines.** Learn what each panel *does* and what it *proves* — then
just describe it in your own words as you click. That always sounds natural, because
it is. This is a map of the screen, not a script.

**A natural order to move through it:** header → the map → pick a scenario → the four
cards on the right (①→⑤) → open the deep-dive → (optional) the knowledge graph →
finish on the validation checks in a terminal.

**One-line summary you can open or close with (in your own words):**
> "KARNADHAR watches for an energy disruption, works out what it does to India, and
> tells every refinery exactly what to buy instead — using real government data."

---

## The header (top bar)
- **Logo + name.** The Ashoka Chakra drawn as a ship's helm wheel — *Karnadhar* means
  the helmsman. India, steered through the storm.
- **Top-right numbers.** India's total refining throughput (~5,000 kb/d), the share that
  comes through Hormuz (**46%** — *derived from real customs data, not quoted*), and how
  many refineries and crude grades the model covers.
- **The ticker strip** (the coloured line under the header). A live one-glance readout of
  the scenario you've picked: the supply gap, Brent price, current-account deficit, whether
  the reroute is feasible, extra tankers needed, the reserve verdict, and how fast it
  solved. *Proves:* it's a live command console, not a slide.

## The map (the "war-room")
This is the picture of India's oil lifeline. What the colours mean:
- **Red lines** = supply routes that *die* under the disruption you picked (cut off at the
  blocked strait).
- **Faint/dim lines** = the normal, pre-crisis shipping corridors (there for context).
- **Bright glowing blue lines** = **the optimizer's actual plan.** Each line runs from a
  supplier, along its real sea route, into the *exact refinery* it now feeds — thickness =
  how many barrels. *This is the key idea: the map shows the answer, not just the problem.*
- **The dots on India** = refineries. Bigger = more capacity; colour blue→red = how
  exposed each one is to Hormuz. Hover one to see its real crude diet.
- **The labelled dots** = the world's chokepoints (Hormuz, Suez, Bab-el-Mandeb, Malacca,
  Cape). They turn red when blocked.
- **Tiny dots near the straits** = real ships, from live AIS tracking data.
- **Blue dashed lines by the Gulf** = the bypass pipelines that can route around Hormuz.
- **Top-left toggles:** **3D globe / 2D map** (2D is lighter and smoother), and
  **Live map / Knowledge graph**.

## The scenario buttons (right panel, top)
Pick the disruption — Hormuz closure, Hormuz + OPEC squeeze, Russia sanctioned, both at
once, or a Red Sea suspension. **Everything on screen re-solves instantly.** *Proves:* it's
general — block any strait, sanction any supplier, any combination.

## Card ① — Early-warning signal
Watches global news coverage of the chokepoints (real GDELT event data). The little bars
are news volume vs a quiet baseline; the alert fired **12 days before** oil actually jumped
in June 2025. *Proves:* it anticipates, it doesn't just react.

## Card ② — Projected impact + twin deficit
The economic consequence — and it's *honest per scenario*. The **"channel" line** tells you
which kind of shock it is: a Hormuz closure is a real global price shock (Brent spikes,
deficit blows out); a Russia sanction is **not** — that oil just goes to China, so India's
real cost is the lost cheap-Russian discount, not a fake price spike. Shows Brent, pump
price, GDP drag, the extra dollar cost, and the current-account deficit. *Proves:* you
understand the economics, not just the barrels.

## Card ③ — Reroute: naive vs KARNADHAR (the core)
Two plans side by side. **Naive** = just buy the cheapest oil → often **INFEASIBLE**,
because it sends crude to refineries that physically can't run it. **KARNADHAR** = the
grade-aware plan → **FEASIBLE**, every barrel runnable. Below that: the gap to cover, how
much shortfall each plan really leaves, the yield value protected, the extra tankers tied
up, the reserve runway, the single most valuable barrel to secure next (the shadow price),
and the actual refinery-by-refinery plan. *Proves:* this is real optimization with the
trade-offs priced.

## Card ④ — Multi-commodity lens
The same disruption scored across **8 strategic imports** (LNG, pharma, semiconductors,
edible oils, fertiliser, coking coal, solar). The bars show how hard each one is hit —
e.g. Hormuz hits 53% of India's LNG too, not just crude. *Proves:* the framework isn't
oil-only; it's any imported material.

## Card ⑤ — Executive brief
The written summary a decision-maker would actually read — situation, the reroute, what to
buy first, the reserve call, the economic hit, the spillover to other imports, and the
policy sequence. The engine writes the numbers; the words are a template. *Proves:* it
ends in a *decision*, not a dashboard.

## The reroute deep-dive (the "⤢ Open reroute deep-dive" button)
This is your strongest section — take your time here. It **ranks the alternative supply
routes #1, #2, #3…** by how much the optimizer relies on each. Every card shows the source,
the volume, the share of the gap it closes, the cost, and whether it's clear of the closure.
**Click any route → the map isolates just that one corridor and the panel on the right
explains exactly why it ranks there.** At the bottom, the **severed suppliers** — Iraq,
Saudi, the UAE, all *bigger* than #1 but cut off at Hormuz — which proves the ranking isn't
just picking the biggest; it understands which oil each refinery can run and which routes
survive. *Proves:* it doesn't just draw lines — it makes and justifies the decision.

## The knowledge graph (top-right toggle)
Flips the map into the relationship web behind everything: suppliers, straits, and
refineries as nodes, and who ships what through where as the links. You can **scroll to
zoom, drag to pan, and drag the nodes around**; when a strait is blocked, the red "threat"
links glow to show exactly who it endangers. *Proves:* the data is a real modelled graph,
not a flat table.

## The proof (in a terminal)
Run `python run_validate.py` — **62 automated checks** go green, and they re-run
automatically every time the code changes. *Proves:* every claim in the demo is tested,
not asserted.

---

## How to sound natural on camera
- Click first, then say what you see — "so here the red routes are the ones that die… and
  these bright blue lines, that's the plan the optimizer worked out." You're narrating,
  not reciting.
- It's fine to pause. A quiet second while the globe turns looks confident.
- You don't have to cover everything. If you truly understand ③ (the reroute) and the
  deep-dive, and you're honest about the data being real — that alone wins.
- Talk to one person, like you're showing a mentor something you're proud of. Because
  you are.
