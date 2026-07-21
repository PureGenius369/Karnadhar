'use client';
import { useState } from 'react';
import dynamic from 'next/dynamic';

const WarMap = dynamic(() => import('./WarMap'), { ssr: false });

const C = {
  bg: '#080b10', panel: '#0f141b', line: '#1e2733', text: '#e8edf2',
  mut: '#8b95a3', teal: '#5dcaa5', amber: '#f2a623', red: '#e24b4a',
  blue: '#3b8bd4', cyan: '#2ec9ff',
};
const MONO = 'ui-monospace, "Cascadia Mono", Consolas, monospace';

const Stat = ({ k, v, c = C.text, sub }: any) => (
  <div style={{ padding: '6px 13px', borderRight: `1px solid ${C.line}` }}>
    <div style={{ fontSize: 9, letterSpacing: 1, textTransform: 'uppercase', color: C.mut }}>{k}</div>
    <div style={{ fontSize: 15, fontWeight: 700, color: c, fontFamily: MONO }}>{v}</div>
    {sub && <div style={{ fontSize: 9.5, color: C.mut, fontFamily: MONO }}>{sub}</div>}
  </div>
);

export default function ScenarioDeepDive({ data, scenario, onClose }:
  { data: any; scenario: any; onClose: () => void }) {
  const all = scenario.routes_ranked || [];
  const material = all.filter((r: any) => !r.long_tail);
  const tail = all.filter((r: any) => r.long_tail);
  const cut = scenario.cut_corridors || [];
  const [sel, setSel] = useState(0);
  const [proj, setProj] = useState<'globe' | 'mercator'>('globe');
  const [showTail, setShowTail] = useState(false);
  const shown = showTail ? all : material;
  const r = all[sel];
  const cas = scenario.cascade, sm = scenario.smart;
  const tailKbd = tail.reduce((a: number, x: any) => a + x.kbd, 0);
  const thinGap = scenario.gap_kbd < 100;

  const rc = (rank: number) => rank === 1 ? C.teal : rank === 2 ? C.cyan : rank === 3 ? C.blue : C.mut;

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 50, background: C.bg, color: C.text,
      font: `14px ${MONO}`, display: 'flex', flexDirection: 'column' }}>
      {/* header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '10px 16px', borderBottom: `1px solid ${C.line}`, background: '#0a0e14' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <button onClick={onClose} style={{ cursor: 'pointer', background: 'transparent',
            border: `1px solid ${C.line}`, color: C.mut, borderRadius: 5, padding: '5px 11px',
            fontSize: 12, fontFamily: MONO }}>← war-room</button>
          <div>
            <div style={{ fontSize: 10, letterSpacing: 1.5, color: C.red, fontWeight: 700 }}>▮ DISRUPTION DEEP-DIVE · PROCUREMENT REROUTE</div>
            <div style={{ fontSize: 18, fontWeight: 800, color: C.text, fontFamily: 'system-ui' }}>{scenario.name}</div>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'stretch', border: `1px solid ${C.line}`, borderRadius: 6, overflow: 'hidden' }}>
          <Stat k="Supply cut" v={`${scenario.gap_kbd.toFixed(0)} kb/d`} c={C.red} />
          <Stat k="Re-sourced" v={sm.feasible ? 'FULL' : `−${sm.unmet.toFixed(0)}`} c={sm.feasible ? C.teal : C.amber} sub={`${material.length} material routes`} />
          <Stat k="Brent" v={`$${cas.brent}`} c={C.red} sub={`band $${cas.brent_lo}–${cas.brent_hi}`} />
          <Stat k="CAD" v={`${cas.cad_stressed}%`} c={cas.cad_stressed > 3 ? C.red : C.mut} sub="of GDP" />
          <Stat k="SPR" v={(scenario.spr?.verdict || 'hold').toUpperCase()} c={scenario.spr?.verdict === 'ration' ? C.red : C.teal} />
          <div style={{ padding: '6px 13px' }}>
            <div style={{ fontSize: 9, letterSpacing: 1, textTransform: 'uppercase', color: C.mut }}>Solve</div>
            <div style={{ fontSize: 15, fontWeight: 700, color: C.cyan, fontFamily: MONO }}>{scenario.solve_ms} ms</div>
          </div>
        </div>
      </div>

      {thinGap && (
        <div style={{ padding: '8px 16px', background: 'rgba(242,166,35,.08)', borderBottom: `1px solid ${C.line}`, fontSize: 12, color: '#d7c48f', lineHeight: 1.45 }}>
          <b style={{ color: C.amber }}>Crude is largely insulated here.</b> India&apos;s oil is overwhelmingly Cape-routed, so this disruption severs only {scenario.gap_kbd.toFixed(0)} kb/d of crude — the reroute below is minor and fully covered. The real exposure is in <b>non-crude imports</b> (e.g. Black-Sea edible oils via Suez) — see the Multi-commodity lens in the war-room. A tool that says so plainly is telling the truth, not padding.
        </div>
      )}

      <div style={{ flex: 1, display: 'flex', minHeight: 0 }}>
        {/* LEFT — ranked routes */}
        <div style={{ width: 404, borderRight: `1px solid ${C.line}`, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
          <div style={{ padding: '10px 14px 8px', borderBottom: `1px solid ${C.line}` }}>
            <div style={{ fontSize: 11, letterSpacing: 1, textTransform: 'uppercase', color: C.text, fontWeight: 700 }}>Ranked reroute corridors</div>
            <div style={{ fontSize: 10.5, color: C.mut, marginTop: 3, lineHeight: 1.45 }}>
              ranked by the volume the optimizer <b style={{ color: '#b6c0cc' }}>committed</b> to each corridor — the LP&apos;s stage-1 priority (secure grade-feasible barrels), cost as tiebreak. <span style={{ color: C.teal }}>Click a corridor →</span> it isolates on the map with its derivation.
            </div>
          </div>
          <div style={{ overflowY: 'auto', flex: 1 }}>
            {shown.map((rt: any) => {
              const i = all.indexOf(rt);
              return (
                <button key={rt.rank} onClick={() => setSel(i)} style={{ width: '100%', textAlign: 'left',
                  cursor: 'pointer', display: 'block', padding: '10px 14px', border: 'none',
                  borderBottom: `1px solid ${C.line}`, borderLeft: `3px solid ${i === sel ? rc(rt.rank) : 'transparent'}`,
                  background: i === sel ? 'rgba(46,201,255,.06)' : 'transparent' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 9 }}>
                    <span style={{ fontSize: 16, fontWeight: 800, color: rc(rt.rank), width: 28, fontFamily: MONO }}>#{rt.rank}</span>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 13.5, fontWeight: 700, color: C.text }}>
                        {rt.source} <span style={{ color: C.mut, fontWeight: 400 }}>· {rt.grade}</span>
                        {rt.tier === 'binding' && <span style={{ fontSize: 8.5, fontWeight: 800, color: C.amber, background: 'rgba(242,166,35,.14)', border: `1px solid ${C.amber}55`, borderRadius: 3, padding: '1px 4px', marginLeft: 6, letterSpacing: 0.5 }}>BINDING</span>}
                      </div>
                      <div style={{ fontSize: 10.5, color: C.mut }}>via {rt.via} · {rt.transit_days}d · {rt.n_refineries} refiner{rt.n_refineries === 1 ? 'y' : 'ies'}</div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: 13, fontWeight: 700, color: C.cyan, fontFamily: MONO }}>{rt.kbd.toFixed(0)}</div>
                      <div style={{ fontSize: 9.5, color: C.mut }}>kb/d</div>
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 6 }}>
                    <div style={{ flex: 1, height: 5, background: '#161d28', borderRadius: 3, overflow: 'hidden' }}>
                      <div style={{ width: `${Math.min(100, rt.gap_share * 100)}%`, height: '100%', background: rc(rt.rank), borderRadius: 3 }} />
                    </div>
                    <span style={{ fontSize: 10, color: C.mut, width: 96, textAlign: 'right' }}>{Math.round(rt.gap_share * 100)}% of gap · ${rt.eff_cost}</span>
                  </div>
                  {rt.residual_risk
                    ? <div style={{ fontSize: 9.5, color: C.amber, marginTop: 4 }}>⚠ transits {rt.via} (open now, future exposure)</div>
                    : (scenario.blocked?.length > 0 && <div style={{ fontSize: 9.5, color: C.teal, marginTop: 4 }}>✓ clear of the closure</div>)}
                </button>
              );
            })}
            {tail.length > 0 && (
              <button onClick={() => setShowTail(!showTail)} style={{ width: '100%', cursor: 'pointer', textAlign: 'left', padding: '9px 14px', border: 'none', borderBottom: `1px solid ${C.line}`, background: 'transparent', color: C.mut, fontSize: 11, fontFamily: MONO }}>
                {showTail ? '▾ hide' : '▸ show'} long-tail — {tail.length} corridors, {tailKbd.toFixed(0)} kb/d (each &lt;1% of gap)
              </button>
            )}
            {cut.length > 0 && (
              <div style={{ padding: '10px 14px' }}>
                <div style={{ fontSize: 10, letterSpacing: 1, textTransform: 'uppercase', color: C.red, fontWeight: 700, marginBottom: 6 }}>⊘ Severed corridors ({cut.length})</div>
                <div style={{ fontSize: 10, color: C.mut, marginBottom: 7, lineHeight: 1.4 }}>bigger suppliers than some survivors, yet gone — proof the rank encodes grade-fit + survival, not raw size:</div>
                {cut.slice(0, 6).map((c: any, j: number) => (
                  <div key={j} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, padding: '2px 0', color: '#8b7176' }}>
                    <span style={{ textDecoration: 'line-through', color: '#a97' }}>{c.source} · {c.grade}</span>
                    <span style={{ color: C.red }}>{c.kbd.toFixed(0)} kb/d · {c.reason}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* RIGHT — focused map + derivation */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
          <div style={{ flex: 1, position: 'relative', minHeight: 0 }}>
            {r && <WarMap data={data} scenario={scenario} projection={proj} focusSource={r.source} />}
            <div style={{ position: 'absolute', top: 10, left: 10, display: 'flex', gap: 4, background: 'rgba(8,11,16,.85)', border: `1px solid ${C.line}`, borderRadius: 6, padding: 3 }}>
              {(['globe', 'mercator'] as const).map((p) => (
                <button key={p} onClick={() => setProj(p)} style={{ cursor: 'pointer', fontSize: 10.5, fontWeight: 700, padding: '5px 12px', borderRadius: 4, fontFamily: MONO, textTransform: 'uppercase', border: 'none', background: proj === p ? 'rgba(46,201,255,.15)' : 'transparent', color: proj === p ? C.cyan : C.mut }}>{p === 'globe' ? '3D' : '2D'}</button>
              ))}
            </div>
            {r && (
              <div style={{ position: 'absolute', top: 10, right: 10, background: 'rgba(8,11,16,.9)', border: `1px solid ${rc(r.rank)}55`, borderRadius: 6, padding: '7px 11px', maxWidth: 280 }}>
                <div style={{ fontSize: 11.5, color: C.text }}><b style={{ color: rc(r.rank) }}>#{r.rank}</b> {r.source} → {r.n_refineries} refiner{r.n_refineries === 1 ? 'y' : 'ies'}, {r.kbd.toFixed(0)} kb/d</div>
                <div style={{ fontSize: 10, color: C.mut, marginTop: 2 }}>this corridor isolated · all others dimmed</div>
              </div>
            )}
          </div>

          {/* derivation panel */}
          {r && (
            <div style={{ borderTop: `1px solid ${C.line}`, background: '#0a0e14', padding: '12px 16px', maxHeight: 268, overflowY: 'auto' }}>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginBottom: 7 }}>
                <span style={{ fontSize: 20, fontWeight: 800, color: rc(r.rank), fontFamily: MONO }}>#{r.rank}</span>
                <span style={{ fontSize: 15, fontWeight: 700 }}>{r.source} — {r.grade}</span>
                <span style={{ fontSize: 10.5, color: C.mut, textTransform: 'uppercase', letterSpacing: 1 }}>decision derivation</span>
              </div>
              <div style={{ fontSize: 12.5, color: '#c3ccd6', lineHeight: 1.5, marginBottom: 10 }}>{r.why}</div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(158px, 1fr))', gap: '6px 16px' }}>
                {[
                  ['Gap closed', `${Math.round(r.gap_share * 100)}%`, C.cyan],
                  ['Volume committed', `${r.kbd.toFixed(1)} kb/d`, C.text],
                  ['Landed cost', `$${r.landed}/bbl`, C.text],
                  ['Yield penalty', `$${r.yield_pen}/bbl`, r.yield_pen > 0.6 ? C.amber : C.mut],
                  ['Effective cost', `$${r.eff_cost}/bbl`, C.text],
                  ['Voyage', `${r.transit_days}d via ${r.via}`, C.text],
                  ['Grade slate', `API ${r.api} · S ${r.sulphur}% · Asph ${r.asph}%`, C.mut],
                  ['Chokepoint risk', r.residual_risk ? 'residual' : 'none', r.residual_risk ? C.amber : C.teal],
                  ...(r.shadow_kusd ? [['Marginal value (LP dual)', `$${r.shadow_kusd}k/day/kb·d`, C.amber]] : [['Supply', 'slack — no urgency', C.teal]]),
                ].map(([k, v, c]: any, j) => (
                  <div key={j} style={{ display: 'flex', justifyContent: 'space-between', gap: 8, fontSize: 11.5, borderBottom: `1px solid #131a24`, paddingBottom: 3 }}>
                    <span style={{ color: C.mut }}>{k}</span>
                    <span style={{ color: c, fontWeight: 600, textAlign: 'right' }}>{v}</span>
                  </div>
                ))}
              </div>
              <div style={{ marginTop: 9 }}>
                <span style={{ fontSize: 10, letterSpacing: 1, textTransform: 'uppercase', color: C.mut }}>Refineries this corridor feeds</span>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 5 }}>
                  {r.refineries.map((rf: any, j: number) => (
                    <span key={j} style={{ fontSize: 11, color: '#b6c0cc', background: '#121924', border: `1px solid ${C.line}`, borderRadius: 4, padding: '2px 7px' }}>
                      {rf.name} <b style={{ color: C.cyan }}>{rf.kbd.toFixed(0)}</b>
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
