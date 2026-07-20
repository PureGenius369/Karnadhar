// KARNADHAR pitch deck generator — ET AI Hackathon 2026 Phase 2
// Run:  node deck/build_deck.js   (from the karnadhar/ folder)
const pptxgen = require('pptxgenjs');

const BG = '0B0F15', PANEL = '121926', LINE = '243040';
const TEXT = 'E8EDF2', MUT = '93A0B0', DIM = '5A6472';
const TEAL = '5DCAA5', AMBER = 'F2A623', RED = 'E85A58', BLUE = '4B96DC', PURPLE = 'A78BDB';
const F = 'Arial';

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE'; // 13.33 x 7.5
pres.author = 'Team KARNADHAR';
pres.title = 'KARNADHAR — Energy Supply-Chain Resilience';

// ---------- helpers ----------
function slideBase() {
  const s = pres.addSlide();
  s.background = { color: BG };
  return s;
}
function kicker(s, txt, color = TEAL) {
  s.addText(txt.toUpperCase(), {
    x: 0.6, y: 0.38, w: 12.1, h: 0.3, fontFace: F, fontSize: 12, bold: true,
    color, charSpacing: 3, margin: 0,
  });
}
function title(s, txt, opts = {}) {
  s.addText(txt, {
    x: 0.6, y: 0.66, w: opts.w || 12.1, h: 0.85, fontFace: F,
    fontSize: opts.size || 31, bold: true, color: TEXT, margin: 0,
  });
}
function panel(s, x, y, w, h, fill = PANEL) {
  s.addShape('roundRect', {
    x, y, w, h, rectRadius: 0.07, fill: { color: fill },
    line: { color: LINE, width: 0.75 },
  });
}
function stat(s, x, y, w, num, label, color, numSize = 40) {
  s.addText(num, { x, y, w, h: 0.75, fontFace: F, fontSize: numSize, bold: true, color, align: 'center', margin: 0 });
  s.addText(label, { x, y: y + 0.72, w, h: 0.62, fontFace: F, fontSize: 11.5, color: MUT, align: 'center', margin: 0, valign: 'top' });
}
function foot(s, txt) {
  s.addText(txt, { x: 0.6, y: 7.02, w: 12.1, h: 0.3, fontFace: F, fontSize: 9.5, color: DIM, margin: 0 });
}

// ================= 1. TITLE =================
{
  const s = slideBase();
  s.addImage({ path: 'captures/map_hormuz.jpg', x: 6.9, y: 0, w: 6.43, h: 5.09 });
  // gradient-less scrim so text zone stays clean
  s.addShape('rect', { x: 6.9, y: 0, w: 6.43, h: 5.09, fill: { color: BG, transparency: 55 }, line: { type: 'none' } });

  s.addText('ET AI HACKATHON 2026  ·  PHASE 2  ·  PROBLEM #2 — ENERGY SUPPLY-CHAIN RESILIENCE', {
    x: 0.6, y: 0.7, w: 8.5, h: 0.3, fontFace: F, fontSize: 12, bold: true, color: TEAL, charSpacing: 2, margin: 0,
  });
  s.addText('KARNADHAR', {
    x: 0.55, y: 1.35, w: 9.5, h: 1.3, fontFace: F, fontSize: 72, bold: true, color: TEXT, charSpacing: 4, margin: 0,
  });
  s.addText('कर्णधार — the helmsman who steers the ship through the storm', {
    x: 0.6, y: 2.72, w: 8.6, h: 0.4, fontFace: F, fontSize: 15, italic: true, color: MUT, margin: 0,
  });
  s.addText([
    { text: 'India imports 88% of its crude. Nearly half transits one strait.\n', options: { color: TEXT, fontSize: 20, bold: true } },
    { text: 'KARNADHAR is the AI command center that turns a 47-day supply crisis\ninto a decision made in 45 milliseconds — grade-by-grade, refinery-by-refinery.', options: { color: MUT, fontSize: 15 } },
  ], { x: 0.6, y: 3.35, w: 8.3, h: 1.6, fontFace: F, margin: 0, lineSpacing: 24 });

  panel(s, 0.6, 5.55, 12.13, 1.15);
  s.addText([
    { text: 'Mann Sutariya', options: { color: TEXT, bold: true, fontSize: 15 } },
    { text: '   ·   Pandit Deendayal Energy University, Gandhinagar', options: { color: MUT, fontSize: 13 } },
  ], { x: 0.9, y: 5.72, w: 8.0, h: 0.4, fontFace: F, margin: 0 });
  s.addText('Assumptions reviewed with: Lydia Powell (ORF)  ·  Prof. U. K. Bhui (PDEU)', {
    x: 0.9, y: 6.14, w: 10.5, h: 0.35, fontFace: F, fontSize: 12, color: TEAL, margin: 0,
  });
  s.addNotes('Open: India runs on imported crude — 88%. Nearly half sails through a strait 3km wide at its narrowest. In June 2025 the world watched Hormuz almost close. KARNADHAR is our answer: an AI that watches the world, models the shock, and reroutes the country’s crude — in real time.');
}

// ================= 2. PROBLEM =================
{
  const s = slideBase();
  kicker(s, 'The problem');
  title(s, 'One strait can strangle the world’s 3rd-largest oil importer');

  const Y = 1.95, H = 1.75, W = 2.83, GAP = 0.27;
  const cells = [
    ['88%', 'of India’s crude is imported', AMBER],
    ['46%', 'transits the Strait of Hormuz — derived from official trade records, not assumed', RED],
    ['9.5 days', 'of strategic reserve cover — voluntary, vs the IEA’s 90-day norm', BLUE],
    ['+8%', 'Brent in a single session when Hormuz was threatened (June 2025)', TEAL],
  ];
  cells.forEach((c, i) => {
    const x = 0.6 + i * (W + GAP);
    panel(s, x, Y, W, H);
    stat(s, x + 0.1, Y + 0.22, W - 0.2, c[0], c[1], c[2], 34);
  });

  panel(s, 0.6, 4.2, 12.13, 2.3);
  s.addText([
    { text: 'And the real constraint isn’t barrels — it’s dollars.\n', options: { color: TEXT, bold: true, fontSize: 18 } },
    { text: 'India is a twin-deficit economy. A sustained price shock adds ~$190 bn/yr to the import bill, blowing the current-account deficit from 1.2% to over 6% of GDP. Unlike trade-surplus Japan or Korea, India cannot sustain that dollar outflow — which is why unprepared economies take ', options: { color: MUT, fontSize: 14.5 } },
    { text: '47 days longer', options: { color: RED, bold: true, fontSize: 14.5 } },
    { text: ' to stabilise supply (McKinsey). The data to act exists. The intelligence layer to act on it does not.', options: { color: MUT, fontSize: 14.5 } },
  ], { x: 0.95, y: 4.5, w: 11.4, h: 1.75, fontFace: F, margin: 0, lineSpacing: 22 });
  foot(s, 'Sources: DGCIS trade records (May 2025–Apr 2026) · PPAC · ISPRL · EIA · twin-deficit framing reviewed with Lydia Powell, Distinguished Fellow, ORF');
  s.addNotes('Four numbers tell the story. 88% imported. 46% through one strait — and we didn’t copy that number from a report, our system derives it from official customs records. Reserves: 9.5 days, voluntary. And when Hormuz was threatened last June, Brent jumped 8% in one session. The deep problem is the twin deficit — India cannot pay for expensive crude in dollars for long. That’s the insight an ORF Distinguished Fellow validated for us.');
}

// ================= 3. THE WEDGE =================
{
  const s = slideBase();
  kicker(s, 'The insight everyone misses');
  title(s, 'Crude oil is not fungible');

  s.addText([
    { text: 'Every other “resilience dashboard” treats oil as one number: barrels.\n\n', options: { color: MUT, fontSize: 15 } },
    { text: 'Reality: a refinery is an engine tuned to a fuel. ', options: { color: TEXT, fontSize: 16, bold: true } },
    { text: 'A deep-conversion coking refinery built for heavy, sour, asphaltene-rich crude physically cannot run ultra-light condensate — and a simple refinery cannot digest sour crude. When Hormuz closes, the question is not “where do we buy oil?” It is “which exact grade can each of our refineries actually run — and who has it?”', options: { color: MUT, fontSize: 15 } },
  ], { x: 0.6, y: 1.8, w: 6.4, h: 3.0, fontFace: F, margin: 0, lineSpacing: 22 });

  panel(s, 0.6, 5.0, 6.4, 1.7, '10151E');
  s.addText([
    { text: '“That is — you are perfectly right.”\n', options: { color: TEAL, fontSize: 16, italic: true, bold: true } },
    { text: 'Prof. U. K. Bhui, Petroleum Engineering, PDEU — on our refinery-constrained sourcing thesis. His guidance added the SARA dimension (asphaltenes) to our crude model.', options: { color: MUT, fontSize: 12 } },
  ], { x: 0.9, y: 5.2, w: 5.9, h: 1.4, fontFace: F, margin: 0, lineSpacing: 17 });

  // right: three property chips + config contrast
  const px = 7.4, pw = 5.33;
  panel(s, px, 1.8, pw, 2.3);
  s.addText('WHAT DECIDES IF A BARREL IS RUNNABLE', { x: px + 0.3, y: 2.0, w: pw - 0.6, h: 0.3, fontFace: F, fontSize: 11, bold: true, color: DIM, charSpacing: 2, margin: 0 });
  const props = [
    ['API gravity', 'light vs heavy', AMBER],
    ['Sulphur', 'sweet vs sour', RED],
    ['Asphaltene (SARA)', 'coke precursor', TEAL],
  ];
  props.forEach((p, i) => {
    const y = 2.42 + i * 0.52;
    s.addShape('ellipse', { x: px + 0.35, y: y + 0.05, w: 0.22, h: 0.22, fill: { color: p[2] }, line: { type: 'none' } });
    s.addText([
      { text: p[0] + '  ', options: { color: TEXT, bold: true, fontSize: 14 } },
      { text: '— ' + p[1], options: { color: MUT, fontSize: 12.5 } },
    ], { x: px + 0.72, y, w: pw - 1.0, h: 0.36, fontFace: F, margin: 0 });
  });

  panel(s, px, 4.35, pw, 2.35);
  s.addText('SAME COUNTRY, DIFFERENT MACHINES', { x: px + 0.3, y: 4.55, w: pw - 0.6, h: 0.3, fontFace: F, fontSize: 11, bold: true, color: DIM, charSpacing: 2, margin: 0 });
  const rows = [
    ['RIL Jamnagar', 'Nelson 21.1', 'runs almost anything — needs heavy feed', TEAL],
    ['BPCL/HPCL Mumbai', 'Nelson 7.0', 'light, sweeter diet only — sour is a hard limit', RED],
  ];
  rows.forEach((r, i) => {
    const y = 4.95 + i * 0.85;
    s.addText([
      { text: r[0] + '   ', options: { color: TEXT, bold: true, fontSize: 14 } },
      { text: r[1] + '\n', options: { color: r[3], bold: true, fontSize: 13 } },
      { text: r[2], options: { color: MUT, fontSize: 12 } },
    ], { x: px + 0.35, y, w: pw - 0.7, h: 0.8, fontFace: F, margin: 0, lineSpacing: 16 });
  });
  s.addNotes('Here is our wedge. Everyone modeling this problem treats oil as fungible. It is not. Three properties decide whether a refinery can run a barrel — API gravity, sulphur, and asphaltene content, the SARA insight Prof. Bhui gave us. Jamnagar with Nelson complexity 21 can digest nearly anything; Mumbai at Nelson 7 cannot touch sour crude. Any reroute plan that ignores this is fiction.');
}

// ================= 4. WHAT WE BUILT =================
{
  const s = slideBase();
  kicker(s, 'What we built');
  title(s, 'A multi-agent brain: signal → scenario → reroute → brief');

  const stages = [
    ['SIGNAL', 'GDELT news agent +\nlive AIS ship tracking', BLUE],
    ['SCENARIO', 'glass-box economic\ncascade + twin deficit', AMBER],
    ['REROUTE', 'grade-aware LP optimizer\nover real refinery diets', TEAL],
    ['BRIEF', 'executive decision memo,\nnumbers from the engine', RED],
  ];
  const W = 2.62, H = 1.9, GAP = 0.52, Y = 2.1;
  stages.forEach((st, i) => {
    const x = 0.62 + i * (W + GAP);
    panel(s, x, Y, W, H);
    s.addShape('rect', { x, y: Y, w: W, h: 0.12, fill: { color: st[2] }, line: { type: 'none' } });
    s.addText(st[0], { x, y: Y + 0.3, w: W, h: 0.4, fontFace: F, fontSize: 19, bold: true, color: st[2], align: 'center', margin: 0 });
    s.addText(st[1], { x: x + 0.15, y: Y + 0.85, w: W - 0.3, h: 0.9, fontFace: F, fontSize: 12, color: MUT, align: 'center', margin: 0, lineSpacing: 16 });
    if (i < 3) {
      s.addText('→', { x: x + W + 0.03, y: Y + 0.62, w: 0.5, h: 0.6, fontFace: F, fontSize: 30, bold: true, color: DIM, align: 'center', margin: 0 });
    }
  });

  const chips = [
    ['REAL public data — no synthetic signals', BLUE],
    ['Explicit, testable assumptions (every parameter named & editable)', AMBER],
    ['Knowledge graph: supplier → route → chokepoint → refinery (50 nodes, 163 edges)', PURPLE],
    ['LLM writes words, never numbers — engine stays auditable', TEAL],
  ];
  chips.forEach((c, i) => {
    const y = 4.42 + i * 0.52;
    s.addShape('ellipse', { x: 0.75, y: y + 0.07, w: 0.18, h: 0.18, fill: { color: c[1] }, line: { type: 'none' } });
    s.addText(c[0], { x: 1.05, y, w: 7.6, h: 0.35, fontFace: F, fontSize: 14, color: TEXT, margin: 0 });
  });

  panel(s, 9.1, 4.4, 3.63, 2.1, '10151E');
  stat(s, 9.2, 4.62, 3.4, '45 ms', 'end-to-end: signal to executable\nrecommendation', TEAL, 38);
  s.addText('vs the 47-day average for economies without response intelligence', {
    x: 9.35, y: 5.85, w: 3.2, h: 0.55, fontFace: F, fontSize: 10.5, color: DIM, align: 'center', margin: 0,
  });
  s.addNotes('Four specialist agents chained by an orchestrator. The signal layer ingests real GDELT news and real AIS ship positions. The scenario layer is a glass-box economic cascade. The reroute layer is a real linear-programming optimizer over each refinery’s actual diet. And the briefing layer writes the memo — the LLM handles words, never numbers. The whole chain runs in 45 milliseconds.');
}

// ================= 5. REAL DATA =================
{
  const s = slideBase();
  kicker(s, 'The foundation');
  title(s, 'Built on official trade records — not synthetic data');

  const tbl = [
    [
      { text: 'Refinery (port)', options: { bold: true, color: MUT } },
      { text: 'MT/yr', options: { bold: true, color: MUT, align: 'right' } },
      { text: 'Nelson', options: { bold: true, color: MUT, align: 'right' } },
      { text: 'Hormuz exposure', options: { bold: true, color: MUT, align: 'right' } },
      { text: 'Top real suppliers', options: { bold: true, color: MUT } },
    ],
    ['RIL Jamnagar (Sikka + SEZ)', '76.3', '21.1', { text: '43%', options: { color: AMBER, bold: true, align: 'right' } }, 'Russia 35 · Saudi 17 · Iraq 14'],
    ['Nayara Vadinar', '41.7', '11.8', { text: '29%', options: { color: TEAL, bold: true, align: 'right' } }, 'Russia 56 · Iraq 18 · Angola 6'],
    ['IOCL Paradip', '34.8', '12.2', { text: '50%', options: { color: AMBER, bold: true, align: 'right' } }, 'Iraq 24 · Russia 21 · UAE 14'],
    ['HMEL Bathinda (Mundra)', '23.3', '12.5', { text: '52%', options: { color: AMBER, bold: true, align: 'right' } }, 'Russia 32 · Saudi 18 · Iraq 16'],
    ['BPCL/HPCL Mumbai', '23.2', '7.0', { text: '60%', options: { color: RED, bold: true, align: 'right' } }, 'Saudi 25 · UAE 23 · US 21'],
    ['BPCL Kochi', '12.4', '8.0', { text: '54%', options: { color: RED, bold: true, align: 'right' } }, 'Russia 31 · UAE 23 · Iraq 16'],
  ].map((r) => r.map((c) => (typeof c === 'string' ? { text: c, options: { color: TEXT } } : c)));

  s.addTable(tbl, {
    x: 0.6, y: 1.85, w: 8.6, colW: [2.75, 0.85, 0.85, 1.55, 2.6],
    fontFace: F, fontSize: 11.5, color: TEXT, fill: { color: PANEL },
    border: { type: 'solid', color: LINE, pt: 0.5 }, rowH: 0.42, valign: 'middle', margin: 0.06,
  });

  panel(s, 9.5, 1.85, 3.23, 2.0, '10151E');
  stat(s, 9.6, 2.05, 3.0, '46%', 'national Hormuz exposure —\nDERIVED from customs data', AMBER, 40);
  panel(s, 9.5, 4.05, 3.23, 1.6, '10151E');
  stat(s, 9.6, 4.2, 3.0, '10 × 36', 'refineries × supplier grades,\nreal volumes & landed prices', TEAL, 30);

  s.addText('Every refinery’s crude diet, Hormuz dependence, and even its processing limits are grounded in what it actually imported — DGCIS port-wise records, PPAC capacities, public Nelson complexity, crude assay libraries.', {
    x: 0.6, y: 5.6, w: 8.6, h: 1.0, fontFace: F, fontSize: 13.5, color: MUT, margin: 0, lineSpacing: 19,
  });
  foot(s, 'DGCIS “India’s Import by Principal Commodity” May 2025–Apr 2026 · port→refinery mapping · country→grade assay mapping (crudemonitor/BP/ENI)');
  s.addNotes('This table is the heart of our credibility. These are not estimates — this is what each refinery actually imported last year, from official customs records. Vadinar runs 56% Russian crude and is only 29% Hormuz-exposed. Mumbai is 60% exposed. Our headline 46% national exposure is computed from this data — most teams will quote a number from a report; we derive it.');
}

// ================= 6. HEADLINE RESULT =================
{
  const s = slideBase();
  kicker(s, 'The result that matters');
  title(s, 'The “fungible” plan is physically impossible. Ours is not.');

  // naive card
  panel(s, 0.6, 1.95, 5.9, 3.1, '1A1114');
  s.addText('NAIVE  ·  “oil is oil”', { x: 0.9, y: 2.2, w: 5.3, h: 0.35, fontFace: F, fontSize: 13, bold: true, color: MUT, charSpacing: 2, margin: 0 });
  s.addText('INFEASIBLE', { x: 0.9, y: 2.55, w: 5.3, h: 0.7, fontFace: F, fontSize: 40, bold: true, color: RED, margin: 0 });
  s.addText([
    { text: '250 kb/d of ultra-light condensate assigned to deep coking refineries that ', options: { color: MUT, fontSize: 13.5 } },
    { text: 'physically cannot run it', options: { color: RED, bold: true, fontSize: 13.5 } },
    { text: '. A grade failure — not a logistics failure. This is the plan a fungible model would execute.', options: { color: MUT, fontSize: 13.5 } },
  ], { x: 0.9, y: 3.4, w: 5.3, h: 1.5, fontFace: F, margin: 0, lineSpacing: 19 });

  // karnadhar card
  panel(s, 6.85, 1.95, 5.9, 3.1, '0E1A17');
  s.addText('KARNADHAR  ·  grade-aware LP', { x: 7.15, y: 2.2, w: 5.3, h: 0.35, fontFace: F, fontSize: 13, bold: true, color: MUT, charSpacing: 2, margin: 0 });
  s.addText('FEASIBLE', { x: 7.15, y: 2.55, w: 5.3, h: 0.7, fontFace: F, fontSize: 40, bold: true, color: TEAL, margin: 0 });
  s.addText([
    { text: 'Every barrel runnable, sourced, within desulphurisation and asphaltene capacity. Heavy-sour rationed to the cokers (Jamnagar, Paradip); light-sweet routed to simple refineries (Mumbai, Chennai). ', options: { color: MUT, fontSize: 13.5 } },
    { text: 'Executable by a procurement desk.', options: { color: TEAL, bold: true, fontSize: 13.5 } },
  ], { x: 7.15, y: 3.4, w: 5.3, h: 1.5, fontFace: F, margin: 0, lineSpacing: 19 });

  const st = [
    ['$3.15 M/day', 'product yield protected by grade-matching', TEAL],
    ['~$1.15 bn/yr', 'annualised value of that decision quality', AMBER],
    ['1,370 kb/d', 're-sourced across 10 refineries in one solve', BLUE],
  ];
  st.forEach((c, i) => {
    const x = 0.6 + i * 4.13;
    panel(s, x, 5.35, 3.87, 1.45);
    stat(s, x + 0.1, 5.5, 3.67, c[0], c[1], c[2], 26);
  });
  s.addNotes('We ran the same crisis through two planners. The naive planner — price-rational, supply-respecting, but grade-blind — produces a plan where 250,000 barrels a day go to refineries that cannot process them. It is infeasible for a grade reason, which is exactly our thesis. KARNADHAR’s linear program produces a fully feasible plan and protects over 3 million dollars a day of product yield — over a billion dollars a year.');
}

// ================= 7. EARLY WARNING =================
{
  const s = slideBase();
  kicker(s, 'Evaluation focus 1 · disruption signal detection');
  title(s, 'We saw the June 2025 Hormuz crisis 12 days before the market');
  s.addImage({ path: 'assets/signal_chart.png', x: 0.7, y: 1.95, w: 9.4, h: 3.87 });

  panel(s, 10.4, 2.2, 2.33, 3.3, '10151E');
  stat(s, 10.45, 2.45, 2.23, '12 days', 'alert lead over the\nBrent +8% session', TEAL, 30);
  stat(s, 10.45, 3.85, 2.23, '200×', 'peak news coverage vs\nquiet baseline (real GDELT)', AMBER, 30);

  s.addText('Method: 10-day rolling baseline → alert when coverage sustains ≥3× baseline for 2 days. Simple, explainable, testable — and fused with live AIS tanker traffic (congestion flags at chokepoints) for multi-source confirmation.', {
    x: 0.7, y: 6.0, w: 12.0, h: 0.75, fontFace: F, fontSize: 12.5, color: MUT, margin: 0, lineSpacing: 18,
  });
  foot(s, 'Real GDELT DOC 2.0 coverage-volume series, cached 1–14 June 2025 · backtest vs 23 June Brent session · aisstream.io live vessel feed (Malacca verified live)');
  s.addNotes('Our early-warning agent watches global news coverage of every chokepoint. In the real June 2025 data, coverage exploded to 200 times baseline. Our alert rule — deliberately simple and explainable — fired on June 11th, twelve days before the Brent 8% session. And it cross-confirms with live ship-tracking data.');
}

// ================= 8. CASCADE + TWIN DEFICIT =================
{
  const s = slideBase();
  kicker(s, 'Evaluation focus 3 · scenario model fidelity');
  title(s, 'A glass-box cascade — ending in the deficit India cannot pay');
  s.addImage({ path: 'assets/cascade_chart.png', x: 0.65, y: 2.0, w: 8.55, h: 3.66 });

  const st = [
    ['₹125.5/L', 'retail fuel at full closure (+₹25.5)', AMBER],
    ['−1.4 pp', 'GDP drag · +2.0 pp CPI', BLUE],
    ['$191 bn/yr', 'extra import bill in USD', RED],
    ['1.2% → 6.1%', 'current-account deficit, % of GDP', RED],
  ];
  st.forEach((c, i) => {
    const y = 1.95 + i * 1.18;
    panel(s, 9.55, y, 3.18, 1.05, '10151E');
    s.addText(c[0], { x: 9.65, y: y + 0.1, w: 2.98, h: 0.45, fontFace: F, fontSize: 20, bold: true, color: c[2], align: 'center', margin: 0 });
    s.addText(c[1], { x: 9.65, y: y + 0.55, w: 2.98, h: 0.42, fontFace: F, fontSize: 10.5, color: MUT, align: 'center', margin: 0 });
  });

  s.addText('Every parameter is named, sourced and editable; sensitivity is one function call. “The binding constraint is the balance of payments, not the barrels” — the twin-deficit reframe came from our review with ORF.', {
    x: 0.65, y: 6.0, w: 8.6, h: 0.8, fontFace: F, fontSize: 12.5, color: MUT, margin: 0, lineSpacing: 18,
  });
  foot(s, 'Cascade: closure → net shortfall (after Saudi/UAE pipeline bypass) → Brent → import bill → pump price → CPI/GDP → CAD · reviewed with Lydia Powell, ORF');
  s.addNotes('The brief demands explicit, testable assumptions — so our cascade is a glass box. Notice the flat segment: a 25% closure is absorbed by the Saudi and UAE bypass pipelines — the model knows that nuance. At full closure: Brent 190, petrol above 125 rupees, and the number that matters most — the current-account deficit exploding past 6% of GDP. India can’t sustain that dollar outflow. That’s why speed of response is a national-security variable.');
}

// ================= 9. SCENARIO MODELLER =================
{
  const s = slideBase();
  kicker(s, 'Beyond one scenario');
  title(s, 'Block any chokepoint. Sanction any supplier. Model it.');

  const rows2 = [
    ['Hormuz full closure', 'naive: INFEASIBLE (250 kb/d un-runnable)', 'KARNADHAR: FEASIBLE — $3.15M/day yield protected', TEAL],
    ['Hormuz + OPEC+ squeeze', 'even optimal reroute leaves 32 kb/d unmet', 'engine says so honestly → demand management + SPR draw', AMBER],
    ['Russia sanctioned', '1,590 kb/d of discounted crude vanishes', 'feasible reroute at higher cost — India’s new #1 supplier is replaceable, at a price', BLUE],
    ['Hormuz + Russia (compound)', 'the nightmare: 2 of top 3 suppliers gone', 'partial coverage only — quantified shortfall drives rationing policy', RED],
  ];
  rows2.forEach((r, i) => {
    const y = 1.9 + i * 1.22;
    panel(s, 0.6, y, 12.13, 1.08);
    s.addShape('rect', { x: 0.6, y, w: 0.12, h: 1.08, fill: { color: r[3] }, line: { type: 'none' } });
    s.addText(r[0], { x: 0.95, y: y + 0.12, w: 3.6, h: 0.85, fontFace: F, fontSize: 15, bold: true, color: TEXT, margin: 0, valign: 'middle' });
    s.addText(r[1], { x: 4.7, y: y + 0.12, w: 3.9, h: 0.85, fontFace: F, fontSize: 12, color: MUT, margin: 0, valign: 'middle', lineSpacing: 15 });
    s.addText(r[2], { x: 8.75, y: y + 0.12, w: 3.8, h: 0.85, fontFace: F, fontSize: 12, color: MUT, margin: 0, valign: 'middle', lineSpacing: 15 });
  });

  s.addText('An honest engine: when a shock is too severe to reroute around, KARNADHAR quantifies the gap instead of pretending — because “you must cut demand by X” is the most decision-useful output there is.', {
    x: 0.6, y: 6.85, w: 12.1, h: 0.5, fontFace: F, fontSize: 12.5, italic: true, color: TEAL, margin: 0,
  });
  s.addNotes('The engine generalizes. Any chokepoint, any supplier sanction, any combination. And critically — it’s honest. Add an OPEC squeeze on top of Hormuz and even the optimal reroute leaves 32,000 barrels a day unmet. The engine says so, quantified. That honesty is what makes it usable for policy.');
}

// ================= 10. WAR-ROOM =================
{
  const s = slideBase();
  kicker(s, 'Evaluation focus 4 · geospatial intelligence');
  title(s, 'The war-room: India’s energy lifeline, live on one screen');

  s.addImage({ path: 'captures/globe_view.jpg', x: 0.6, y: 1.9, w: 6.31, h: 5.0 });
  s.addShape('rect', { x: 0.6, y: 1.9, w: 6.31, h: 5.0, fill: { type: 'none' }, line: { color: LINE, width: 1 } });

  const feats = [
    ['Live 3D globe', 'true globe projection with real AIS vessels; refineries sized & coloured by real data', TEAL],
    ['Cut vs alive routes', 'every supply corridor recolours the instant a scenario changes', RED],
    ['Knowledge-graph view', 'toggle to the 50-node supplier→strait→refinery graph; threat edges glow per scenario', PURPLE],
    ['Multi-commodity lens', 'same disruption scored across 8 strategic imports — Hormuz hits 53% of LNG too', AMBER],
    ['45 ms', 'scenario click → new national plan on screen', TEAL],
  ];
  feats.forEach((f, i) => {
    const y = 1.95 + i * 1.0;
    s.addShape('ellipse', { x: 7.25, y: y + 0.04, w: 0.2, h: 0.2, fill: { color: f[2] }, line: { type: 'none' } });
    s.addText([
      { text: f[0] + '\n', options: { color: TEXT, bold: true, fontSize: 13.5 } },
      { text: f[1], options: { color: MUT, fontSize: 11.5 } },
    ], { x: 7.58, y, w: 5.15, h: 0.95, fontFace: F, margin: 0, lineSpacing: 15 });
  });
  s.addNotes('This is the product. Next.js and MapLibre over a FastAPI engine. The map you see is live — the red routes are the Gulf corridors dying when Hormuz closes; the green ones are the alternates KARNADHAR is re-routing through. Click a scenario and the entire national plan recomputes in 45 milliseconds. This screenshot shows the Russia-sanction scenario — one cut artery, and the map tells you instantly what changed.');
}

// ================= 11. RIGOR =================
{
  const s = slideBase();
  kicker(s, 'Why you can trust it');
  title(s, 'Validated, evaluated, and reviewed by domain experts');

  panel(s, 0.6, 1.9, 5.9, 4.6);
  s.addText('AUTOMATED VALIDATION', { x: 0.9, y: 2.1, w: 5.3, h: 0.3, fontFace: F, fontSize: 11, bold: true, color: DIM, charSpacing: 2, margin: 0 });
  s.addText('39 / 39', { x: 0.9, y: 2.4, w: 5.3, h: 0.8, fontFace: F, fontSize: 44, bold: true, color: TEAL, margin: 0 });
  s.addText('checks passed — one command, exit-code gated', { x: 0.9, y: 3.2, w: 5.3, h: 0.3, fontFace: F, fontSize: 12, color: MUT, margin: 0 });
  const checks = [
    'wedge holds: naive infeasible for grade reasons, LP optimal',
    'cascade monotonic; bypass nuance; twin-deficit wired',
    'signal alert precedes market repricing on real data',
    'real-diet integrity: 46% exposure, configs sane',
    'engine admits unmet demand under compound shocks',
    'multi-commodity lens generalises (8 imports, one framework)',
  ];
  s.addText(checks.map((c, i) => ({ text: c, options: { bullet: { code: '2713' }, color: MUT, breakLine: i < checks.length - 1 } })),
    { x: 0.95, y: 3.6, w: 5.35, h: 2.7, fontFace: F, fontSize: 12.5, margin: 0, paraSpaceAfter: 8 });

  panel(s, 6.85, 1.9, 5.9, 2.2);
  s.addText('EVALUATION FOCUS — ALL FIVE, COVERED', { x: 7.15, y: 2.1, w: 5.3, h: 0.3, fontFace: F, fontSize: 11, bold: true, color: DIM, charSpacing: 2, margin: 0 });
  const efs = [
    ['EF-1', 'signal lead time: 12 days, real GDELT + AIS'],
    ['EF-2', 'procurement executability: feasible, grade-matched plans'],
    ['EF-3', 'scenario fidelity: explicit, testable, sensitivity-swept'],
    ['EF-4', 'geospatial depth: live routed map, real diets'],
    ['EF-5', 'response time: 45 ms signal → recommendation'],
  ];
  s.addText(efs.map((e, i) => ({
    text: e[0] + '   ' + e[1],
    options: { color: MUT, breakLine: i < efs.length - 1 },
  })), { x: 7.15, y: 2.5, w: 5.4, h: 1.5, fontFace: F, fontSize: 11.5, margin: 0, paraSpaceAfter: 5 });

  panel(s, 6.85, 4.3, 5.9, 2.2, '10151E');
  s.addText('EXPERT REVIEW', { x: 7.15, y: 4.5, w: 5.3, h: 0.3, fontFace: F, fontSize: 11, bold: true, color: DIM, charSpacing: 2, margin: 0 });
  s.addText([
    { text: 'Lydia Powell', options: { color: TEXT, bold: true, fontSize: 13.5 } },
    { text: ' — Distinguished Fellow, ORF: twin-deficit framing; SPR-as-voluntary-insurance; sourcing-first policy sequence.\n', options: { color: MUT, fontSize: 11.5 } },
    { text: 'Prof. U. K. Bhui', options: { color: TEXT, bold: true, fontSize: 13.5 } },
    { text: ' — Petroleum Engg., PDEU: wedge validated (“you are perfectly right”); SARA/asphaltene dimension added on his guidance.', options: { color: MUT, fontSize: 11.5 } },
  ], { x: 7.15, y: 4.85, w: 5.4, h: 1.55, fontFace: F, margin: 0, lineSpacing: 16 });
  s.addNotes('Three layers of trust. A validation suite — 35 assertions about the engine’s behaviour, all green, runnable in one command. Full coverage of the brief’s five evaluation-focus criteria. And two independent domain experts — a Distinguished Fellow at ORF for the economics, and a PDEU petroleum professor for the refining science — reviewed our assumptions.');
}

// ================= 12. BUSINESS =================
{
  const s = slideBase();
  kicker(s, 'Business impact & scalability');
  title(s, 'Incumbents tell you what’s happening. We tell you what to do.');

  s.addText([
    { text: 'Kpler, Vortexa, S&P and Wood Mackenzie built a multi-billion-dollar market selling ', options: { color: MUT, fontSize: 14 } },
    { text: 'monitoring', options: { color: TEXT, bold: true, fontSize: 14 } },
    { text: '. KARNADHAR sells the ', options: { color: MUT, fontSize: 14 } },
    { text: 'decision layer', options: { color: TEAL, bold: true, fontSize: 14 } },
    { text: ' — the feasible, grade-aware action plan — AI-native and India-first.', options: { color: MUT, fontSize: 14 } },
  ], { x: 0.6, y: 1.75, w: 12.1, h: 0.75, fontFace: F, margin: 0, lineSpacing: 20 });

  s.addText('WHO PAYS', { x: 0.6, y: 2.75, w: 5, h: 0.3, fontFace: F, fontSize: 11, bold: true, color: DIM, charSpacing: 2, margin: 0 });
  const buyers = [
    ['Refiners', 'IOCL · BPCL · HPCL · RIL · Nayara'],
    ['Traders', 'desks living on disruption signals'],
    ['Shippers & insurers', 'chokepoint risk = pricing'],
    ['Government', 'PPAC · ISPRL · MoPNG — the anchor'],
  ];
  buyers.forEach((b, i) => {
    const x = 0.6 + (i % 2) * 3.05, y = 3.15 + Math.floor(i / 2) * 1.28;
    panel(s, x, y, 2.85, 1.12);
    s.addText([
      { text: b[0] + '\n', options: { color: TEXT, bold: true, fontSize: 13.5 } },
      { text: b[1], options: { color: MUT, fontSize: 10.5 } },
    ], { x: x + 0.2, y: y + 0.12, w: 2.5, h: 0.9, fontFace: F, margin: 0, lineSpacing: 15 });
  });

  s.addText('THREE AXES OF SCALE', { x: 7.0, y: 2.75, w: 5.5, h: 0.3, fontFace: F, fontSize: 11, bold: true, color: DIM, charSpacing: 2, margin: 0 });
  const axes = [
    ['1 · Segments', 'refiner → trader → insurer → sovereign (same engine, 7 buyer types)', TEAL],
    ['2 · Geography', '50+ import-dependent economies share this exact anatomy — Japan, Korea, Turkey, Philippines…', AMBER],
    ['3 · Commodity', 'demonstrated LIVE in-app: 8 strategic imports screened — LNG, pharma APIs, semiconductors… (Hormuz hits 53% of LNG)', BLUE],
  ];
  axes.forEach((a, i) => {
    const y = 3.15 + i * 1.13;
    panel(s, 7.0, y, 5.73, 0.98);
    s.addText([
      { text: a[0] + '   ', options: { color: a[2], bold: true, fontSize: 13.5 } },
      { text: a[1], options: { color: MUT, fontSize: 11.5 } },
    ], { x: 7.25, y: y + 0.1, w: 5.3, h: 0.8, fontFace: F, margin: 0, valign: 'middle', lineSpacing: 15 });
  });

  s.addText('Model: tiered SaaS — Monitor → Simulate → Orchestrate — plus API licensing. Land commercial desks first (months, not years); the sovereign deployment is the moat and the mission.', {
    x: 0.6, y: 6.75, w: 12.1, h: 0.55, fontFace: F, fontSize: 12.5, color: MUT, margin: 0,
  });
  s.addNotes('Is this a business? The market already pays billions for energy intelligence — Kpler, Vortexa, Wood Mackenzie. But they sell monitoring. We sell the decision. Seven buyer segments, starting with refiners and traders. Fifty-plus import-dependent countries share India’s anatomy. And the engine is commodity-agnostic — crude today, LNG and critical minerals tomorrow.');
}

// ================= 13. CLOSE =================
{
  const s = slideBase();
  s.addImage({ path: 'captures/map_hormuz.jpg', x: 0, y: 0, w: 13.33, h: 10.56, sizing: { type: 'crop', w: 13.33, h: 7.5 } });
  s.addShape('rect', { x: 0, y: 0, w: 13.33, h: 7.5, fill: { color: BG, transparency: 25 }, line: { type: 'none' } });

  s.addText('NEXT 90 DAYS', { x: 0.7, y: 0.6, w: 6, h: 0.3, fontFace: F, fontSize: 12, bold: true, color: TEAL, charSpacing: 3, margin: 0 });
  const road = [
    'Refinery configs calibrated with Prof. Bhui’s written inputs (in progress)',
    'Commercial AIS feed for dense Gulf coverage; Claude-authored live briefs',
    'Pilot conversations: PPAC · ISPRL — the analysis they do in days, in 45 ms',
  ];
  s.addText(road.map((r, i) => ({ text: r, options: { bullet: { code: '2192' }, color: TEXT, breakLine: i < road.length - 1 } })),
    { x: 0.7, y: 1.0, w: 8.5, h: 1.5, fontFace: F, fontSize: 14, margin: 0, paraSpaceAfter: 8 });

  s.addText('India’s energy lifeline has no helmsman for the storm.', {
    x: 0.7, y: 3.4, w: 11.9, h: 0.6, fontFace: F, fontSize: 26, bold: true, color: TEXT, margin: 0,
  });
  s.addText('Now it does.', {
    x: 0.7, y: 4.05, w: 11.9, h: 0.9, fontFace: F, fontSize: 44, bold: true, color: TEAL, margin: 0,
  });

  s.addText([
    { text: 'KARNADHAR', options: { bold: true, color: TEXT, fontSize: 16 } },
    { text: '   ·   Mann Sutariya · PDEU · mannsutaria2605@gmail.com', options: { color: MUT, fontSize: 13 } },
  ], { x: 0.7, y: 6.55, w: 11.9, h: 0.4, fontFace: F, margin: 0 });
  s.addNotes('Close: everything you saw runs today — real data, real signals, provable results, expert-reviewed. India’s energy lifeline has no helmsman for the storm. Now it does. Thank you.');
}

pres.writeFile({ fileName: 'deliverables/KARNADHAR_Deck.pptx' }).then((f) => console.log('WROTE', f));
