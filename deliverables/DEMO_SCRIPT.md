# KARNADHAR — Demo Video Script (target ~3:00)

**Setup before recording**
1. `cd karnadhar && python -m uvicorn api.main:app --port 8000` (optional; UI runs from JSON alone)
2. `cd frontend && npm run dev` → open http://localhost:3000 in a maximised browser (dark theme).
3. Second window ready: a terminal at `karnadhar/` (font ~16pt, dark).
4. Recorder: OBS / Xbox Game Bar (Win+G). 1080p. Mic on, quiet room. Speak slowly.

---

## SHOT 1 — The hook (0:00–0:25) · war-room on screen, Hormuz scenario selected
> "India imports 88 percent of its crude oil — and nearly half of it sails through one
> strait: Hormuz. In June 2025 the world watched it almost close. This is KARNADHAR —
> a live 3D globe of India's energy lifeline, and an AI command center that answers
> the question every planning tool dodges: if the strait closes **tomorrow**, what
> exactly should every Indian refinery do?"

*Action: drag the globe slightly (show the curvature), then hover Jamnagar so its
real diet popup shows; the tiny dots at the straits are real AIS vessels. The
bright animated lines ARE the optimizer's plan — you'll say so in Shot 3. If the
globe feels heavy on your recorder, the 2D MAP toggle (top-left) is one click.*

## SHOT 2 — The problem with "oil is oil" (0:25–0:55) · stay on map
> "Most tools treat oil as one number — barrels. But a refinery is an engine tuned to a
> fuel. Jamnagar — Nelson complexity 21 — digests heavy, sour, asphaltene-rich crude.
> Mumbai — complexity 7 — physically cannot. So when the red routes die, the question
> isn't 'where do we buy oil?' It's 'which exact grade can each refinery actually run —
> and who has it?' Everything you see here is built from official customs records —
> every refinery's real diet, real suppliers, real prices. Our 46-percent Hormuz
> exposure isn't quoted from a report. The system derives it."

*Action: point at red Gulf routes converging on Hormuz, then green alternates.*

## SHOT 3 — The result (0:55–1:30) · right panel, card ③
> "Watch the verdict. The naive plan — buy the cheapest barrels — is **infeasible**:
> its blend breaches Visakhapatnam's sulphur limit, and under a Russia sanction it
> sends **two hundred and twenty thousand barrels a day** to refineries that
> physically cannot run them. KARNADHAR's two-stage optimizer is feasible in every
> survivable scenario — and it prices what others ignore: this reroute ties up
> **sixty-six extra supertankers**, and the LP's shadow prices name the scarcest
> barrel — heavy Colombian crude for the coker fleet — worth four thousand dollars
> a day per extra thousand barrels. That's a procurement priority list, derived,
> not opined."

*Action: hover the INFEASIBLE / FEASIBLE cards; point at "+66 VLCC-equiv" and the
"marginal barrel" line; click "Russia fully sanctioned" to show 220 → 0 usable
shortfall; click back to Hormuz. Then point at the MAP:*

> "And you're not reading the plan off a table — you're **looking at it**. Every
> bright line is one LP allocation: Russia's Urals swinging around the Cape of
> Good Hope into Jamnagar — hover it: six hundred fifty-eight thousand barrels a
> day, assigned by the optimizer. The dim lines are yesterday's corridors. The
> red ones are dead. The bright ones are the answer."

## SHOT 3.5 — The ranked deep-dive (1:30–2:00) · click "⤢ Open reroute deep-dive"
> "And it ranks them. This is the procurement decision page — the alternative
> corridors, ordered by the volume the optimizer committed to each. Number one:
> Russia, ninety percent of the gap, Cape-routed, immune to Hormuz. Watch the
> honesty — it says right on the card, *plus five dollars a barrel above the
> cheapest survivor; it ranks first on secured volume, not price.* Click it —"

*Action: click route #1; the map collapses the tangle to Russia's single glowing
artery, the derivation panel fills in.*

> "— and the map isolates just that corridor, with the full derivation: gap closed,
> landed cost, grade slate, the ten refineries it feeds. And look below: the
> **severed** suppliers — Iraq, Saudi, the UAE — all *bigger* than Russia, all cut
> at Hormuz. That's the proof the ranking isn't sorting by size; it's the
> optimizer's own priority, grade-fit and survival built in."

*Action: click route #2 (Colombia) to show a BINDING, shadow-priced corridor, then
"← war-room" to return.*

## SHOT 4 — Early warning (2:00–2:15) · card ①
> "And we're not waiting for the news. KARNADHAR watches global event data — this is
> the real June 2025 series. Coverage exploded to two hundred times baseline. Our
> alert fired on June 11th — **twelve days before** Brent jumped eight percent."

*Action: point at the signal bars and the lead-time line.*

## SHOT 5 — Twin deficit (1:55–2:20) · card ②
> "The cascade is a glass box — every assumption named and testable. Brent at 190.
> Petrol above 125 rupees. But the real constraint — validated with an ORF
> Distinguished Fellow — is the **twin deficit**: 191 billion dollars a year of extra
> outflow India cannot pay in dollars. The binding constraint isn't barrels. It's the
> balance of payments."

## SHOT 6 — Any disruption (2:20–2:40) · click scenarios live
> "And it's not one hard-coded scenario. Sanction Russia — the map recolours, the
> whole national plan re-solves in well under a tenth of a second. Stack Hormuz
> **plus** an OPEC squeeze — and the engine is honest: even the optimal reroute
> leaves a gap, quantified, which is exactly what tells policymakers to trigger
> demand management."

*Action: click "Russia fully sanctioned", pause; click "Hormuz + OPEC+ squeeze".
Then point at card ④ (Multi-commodity lens):*

> "And the framework isn't oil-specific. The same disruption, scored across every
> strategic import — Hormuz isn't just a crude problem: it carries **53 percent of
> India's LNG** too. Malacca? That's the pharma and semiconductor artery."

*Action: click "Red Sea suspension":*

> "Here's the proof it discriminates: suspend the Red Sea — the brief's own
> scenario — and India's crude barely moves, it sails the Cape. But cooking oil
> lights up: eighteen percent, the Black Sea sunflower artery. One engine, any
> material — and it knows the difference. And card ⑤: the executive brief writes
> itself from the engine's numbers — including the SPR scheduler's verdict:
> hold, bridge, or ration, with the exact drawdown rate."

## SHOT 6.5 — Knowledge graph (2:40–2:55) · click "Knowledge graph" toggle (top-right)
> "Under everything sits a knowledge graph — fifty nodes, a hundred and sixty-three
> edges: which supplier ships which grade through which strait to which refinery,
> every edge carrying real volumes and provenance. Watch Hormuz — the red threads
> are exactly who it threatens, and how badly."

*Action: scroll to ZOOM into the Hormuz cluster (labels densify), drag to pan,
grab-and-drag one refinery node, hover it (tooltip shows Nelson/API window),
double-click to reset. Switch back to "Live map" before the next shot.*

## SHOT 7 — Proof & close (2:55–3:15) · switch to terminal
> Run: `python run_validate.py` — let the green checks scroll.
> "Fifty-seven automated checks — every claim falsifiable, re-run in CI on every push.
> Real government data. Two domain experts. India's energy lifeline has no
> helmsman for the storm. Now it does. KARNADHAR."

*(Optional 5s bonus if pacing allows: `python run_demo.py` — the curated
head-to-head where the wedge is worth $3.15M/day of protected yield; say
"and on the stress-test model, the wedge is worth over three million dollars a
day." Keep the two models' numbers separate — real model on screen, curated
demo in terminal.)*

---

**Upload:** YouTube (unlisted is fine if allowed — else public), title
"KARNADHAR — AI Energy Supply-Chain Command Center | ET AI Hackathon 2026".
Keep the link in the submission form AND the GitHub README.
