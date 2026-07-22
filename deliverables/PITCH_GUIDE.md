# KARNADHAR — Winning Pitch Guide (3–4 min demo video)

You reached top-10 before but the pitch didn't land. This guide fixes that. The rule:
**state the thesis in the first 15 seconds, let the live product carry the middle,
end on one line — and stop.** Don't explain everything; show the few things that win.

---

## Part A — the 6 delivery rules (read this first)

1. **Lead with the payoff, not the build-up.** Judges decide in the first 20 seconds
   whether you're a winner. Say what KARNADHAR *is* and why it's different immediately.
2. **One number per point.** Not five. "46% through one strait." "12 days early."
   "62 green checks." A pitch drowns when every sentence has three statistics.
3. **Show, don't tell.** The war-room is your proof. Click things. Let motion carry it.
   Silence for 2 seconds while the globe turns is fine — it looks alive.
4. **Practice the exact words 5+ times and TIME it.** Choking = improvising under
   pressure. If the words are memorised, nerves can't derail you. Aim for 3:15, leaving
   buffer under 4:00.
5. **Speak slower than feels natural, and pause between sections.** A held pause reads
   as confidence, not a blank.
6. **End on the tagline and STOP.** "India's energy lifeline has no helmsman for the
   storm. Now it does. KARNADHAR." Then silence. Don't trail off into "yeah, so…".

Voice: calm, certain, a little proud. You built something real — sound like it.

---

## Part B — the script (word-for-word) + what to do on screen

> Target 3:15. Each shot has a **[SAY]** (memorise) and a **[DO]** (screen action).
> Priorities are marked ★ (never cut) and ◇ (cut first if you're over time).

### ★ 0:00–0:20 — Hook  (screen: war-room, 3D globe, Hormuz scenario selected)
**[SAY]** "India imports 88 percent of its crude oil — and nearly half of it sails
through a single strait: Hormuz. Every planning tool treats oil as one number: barrels.
But a refinery is an engine tuned to a fuel. That one fact changes everything — and it's
what KARNADHAR is built on."
**[DO]** Let the globe rotate a touch. Don't rush. The tricolour-chakra logo is top-left.

### ★ 0:20–0:55 — The wedge + the verdict  (screen: right panel, card ③)
**[SAY]** "Close Hormuz, and the naive plan — buy the cheapest barrels — is physically
*impossible*: it sends crude to refineries that cannot run it. KARNADHAR's grade-aware
optimizer produces a plan where every barrel is runnable — sourced, sulphur- and
asphaltene-checked, refinery by refinery. And everything you're seeing is built from
official Indian customs records. Our 46-percent Hormuz exposure isn't quoted from a
report — the system derives it."
**[DO]** Point at INFEASIBLE (red) vs FEASIBLE (teal). Hover Jamnagar's diet popup.

### ★ 0:55–1:35 — The optimization, made visible  (screen: click "⤢ Open reroute deep-dive")
**[SAY]** "And we don't just draw lines — we rank the routes. This is the procurement
decision page: the alternative corridors, ranked by the volume the optimizer commits to
each. Number one — Russia, ninety percent of the gap, routed around the Cape, immune to
Hormuz. Watch the honesty: the card says, in its own words, *plus five dollars a barrel
above the cheapest survivor — it ranks first on secured volume, not price.* Click it—"
**[DO]** Click route #1. The tangle collapses to one glowing artery; the derivation
panel fills in.
**[SAY]** "—and the map isolates that one corridor, with the full derivation. And below,
the *severed* suppliers — Iraq, Saudi, the UAE — all bigger than Russia, all cut at
Hormuz. That proves the ranking isn't sorting by size. It's the optimizer's own priority,
with grade-fit and survival built in."
**[DO]** Point at the severed section. Click "← war-room" to return.

### ★ 1:35–2:05 — Early warning + honest economics  (screen: cards ① then ②)
**[SAY]** "We're not waiting for the news either. KARNADHAR watches global event data —
this is the real June 2025 series. Our alert fired twelve days before Brent jumped eight
percent. And the economics are honest per scenario: a Hormuz closure is a global shock —
Brent to 190, the current-account deficit past six percent of GDP. But sanction Russia
and we do *not* fake a price spike — those barrels redistribute; India's real cost is the
three-and-a-half-billion-dollar Urals discount it loses. Getting that distinction right is
what separates a real energy model from a dashboard."
**[DO]** Point at the 12-day lead on card ①. Click "Russia fully sanctioned"; point at
card ②'s channel line and "Lost Russian discount."

### ◇ 2:05–2:25 — Any disruption + multi-commodity  (screen: click "Red Sea suspension")
**[SAY]** "It's not one hard-coded scenario — block any strait, sanction any supplier,
and the whole national plan re-solves in under a tenth of a second. And it isn't
oil-only: suspend the Red Sea and India's crude barely moves — but cooking oil lights up,
eighteen percent, the Black-Sea artery. One engine, any material."
**[DO]** Click Red Sea; point at card ④ (Edible oils jumping).

### ★ 2:25–3:00 — Proof + close  (screen: terminal, then back to the globe)
**[SAY]** "Real government data. A real optimizer — the same linear programming a refinery
runs. Two domain experts, from ORF and PDEU, reviewed our assumptions. And sixty-two
automated checks prove it, re-run on every push."
**[DO]** In a terminal, run `python run_validate.py`; let the green checks scroll ~3s.
**[SAY]** (back on the globe) "India's energy lifeline has no helmsman for the storm.
Now it does. KARNADHAR."
**[DO]** Stop. Let the last frame hold for a second. End recording.

*If over time, cut the ◇ Red Sea shot first, then trim the early-warning half of the
1:35 shot. Never cut the hook, the wedge verdict, the deep-dive, or the close.*

---

## Part C — Q&A (if it's a live round, rehearse these crisp answers)

- **"Is this real data?"** → "Yes — DGCIS customs records. We *derive* the 46% exposure;
  delete our number and the code re-derives it. It's checked in CI."
- **"Why is Russia #1 if it's cheap, not scarce?"** → "We rank by what the optimizer
  commits — securing volume is the first job in a crisis. The card even says it ranks
  first on secured volume, not price. Shadow-price-first would put a 3-kb/d supplier on
  top and bury the 90% lifeline — a scarcity artifact. We avoid that."
- **"Don't sanctions spike oil prices?"** → "Not globally — the barrels redistribute to
  China. We model that correctly: India's cost is the lost discount, not a world price
  shock. That channel separation is in the engine."
- **"Is the optimizer real?"** → "Yes — a two-stage linear program on PuLP/CBC, the same
  class of math refiners run in Aspen PIMS. Not a heuristic."
- **"What's NOT done?"** (answer confidently) → "Refinery windows are derived from real
  diets and Nelson complexity; we're calibrating them with Prof. Bhui's written inputs.
  And AIS is the free tier — dense Gulf coverage needs a paid feed. Knowing exactly where
  our prototype ends and production begins is deliberate."

---

## Part D — recording logistics

1. `cd karnadhar/frontend && npm run dev` → open **localhost:3000** maximised, dark theme,
   Hormuz scenario selected. If the globe stutters on your recorder, use the **2D MAP**
   toggle — the flows still animate.
2. Second window: a terminal at `karnadhar/`, ~16pt font, dark.
3. Recorder: OBS or Xbox Game Bar (Win+G), 1080p, mic on, quiet room.
4. Do a silent dry-run first (click through every action once) so nothing surprises you.
5. Record in one take if you can; if you fumble, pause 2 seconds and repeat the sentence
   (easy to trim). Speak to one imagined judge, not a crowd.
6. Export MP4. If ≤50 MB, upload directly on Unstop; if larger, put it on Google Drive
   (link-shareable) and paste the link. Also drop the link in the GitHub README top.

**Title:** "KARNADHAR — AI Energy Supply-Chain Command Center | ET AI Hackathon 2026"
