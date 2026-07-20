'use client';
import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';

const WarMap = dynamic(() => import('./WarMap'), { ssr: false });
const KgView = dynamic(() => import('./KgView'), { ssr: false });

const C = {
  bg: '#080b10', panel: '#0f141b', line: '#1e2733', text: '#e8edf2',
  mut: '#8b95a3', teal: '#5dcaa5', amber: '#f2a623', red: '#e24b4a', blue: '#3b8bd4',
  cyan: '#2ec9ff',
};
const MONO = 'ui-monospace, "Cascadia Mono", Consolas, monospace';

const Card = ({ title, children, accent = '#1e2733', led }: any) => (
  <div style={{ background: C.panel, border: `1px solid ${C.line}`, borderLeft: `2px solid ${accent}`, borderRadius: 6, padding: '12px 14px', marginBottom: 12 }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
      <span style={{ fontSize: 10, letterSpacing: 1.2, textTransform: 'uppercase', color: C.mut }}>{title}</span>
      {led && <span style={{ fontSize: 9, fontFamily: MONO, letterSpacing: 1, color: led[1] }}><span className="led-live">●</span> {led[0]}</span>}
    </div>
    {children}
  </div>
);
const Row = ({ k, v, c = '#e8edf2' }: any) => (
  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, padding: '2px 0' }}>
    <span style={{ color: C.mut }}>{k}</span>
    <span style={{ color: c, fontWeight: 600, fontFamily: MONO, fontSize: 12.5 }}>{v}</span>
  </div>
);

export default function Page() {
  const [data, setData] = useState<any>(null);
  const [si, setSi] = useState(0);
  const [view, setView] = useState<'map' | 'graph'>('map');
  const [proj, setProj] = useState<'globe' | 'mercator'>('globe');
  useEffect(() => { fetch('/karnadhar.json').then((r) => r.json()).then(setData); }, []);

  if (!data)
    return <div style={{ height: '100vh', display: 'grid', placeItems: 'center', background: C.bg, color: C.teal, font: '14px system-ui' }}>Loading KARNADHAR…</div>;

  const scn = data.scenarios[si];
  const cas = scn.cascade, sig = data.signal;
  const yieldProt = (scn.naive.yield_loss - scn.smart.yield_loss).toFixed(2);
  const maxX = Math.max(...sig.series.map((p: any) => p.x));

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', background: C.bg, color: C.text, font: '14px system-ui, sans-serif', overflow: 'hidden' }}>
      {/* top bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '9px 18px 7px', borderBottom: `1px solid ${C.line}` }}>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 12 }}>
          <span style={{ fontSize: 20, fontWeight: 800, color: C.teal, letterSpacing: 1 }}>KARNADHAR</span>
          <span style={{ fontSize: 12, color: C.mut }}>India Energy Supply-Chain Resilience — live command center</span>
        </div>
        <div style={{ display: 'flex', gap: 18, fontSize: 12, color: C.mut, fontFamily: MONO }}>
          <span><b style={{ color: C.text }}>{data.meta.national_kbd.toLocaleString()}</b> kb/d run</span>
          <span><b style={{ color: C.amber }}>{Math.round(data.meta.hormuz_exposure * 100)}%</b> via Hormuz*</span>
          <span><b style={{ color: C.text }}>{data.meta.n_refineries}</b> refineries · <b style={{ color: C.text }}>{data.meta.n_grades}</b> grades</span>
        </div>
      </div>
      {/* terminal ticker tape — the active scenario, quantified */}
      <div style={{ display: 'flex', gap: 0, alignItems: 'center', padding: '4px 18px', borderBottom: `1px solid ${C.line}`, background: '#0a0e14', fontFamily: MONO, fontSize: 10.5, letterSpacing: 0.4, whiteSpace: 'nowrap', overflow: 'hidden' }}>
        <span style={{ color: C.red, fontWeight: 700 }}>▮ {scn.name.toUpperCase()}</span>
        {[
          ['GAP', `${scn.gap_kbd.toFixed(0)} KB/D`, C.text],
          ['BRENT', `$${cas.brent} (+${cas.brent_pct}%)`, cas.brent_pct > 0 ? C.red : C.mut],
          ['CAD', `${cas.cad_stressed}% GDP`, cas.cad_stressed > 3 ? C.red : C.mut],
          ['REROUTE', scn.smart.feasible ? 'FEASIBLE' : `PARTIAL −${scn.smart.unmet.toFixed(0)}`, scn.smart.feasible ? C.teal : C.amber],
          ['VLCC', `+${scn.smart.extra_vlcc.toFixed(0)}`, C.amber],
          ['SPR', (scn.spr?.verdict || 'hold').toUpperCase(), scn.spr?.verdict === 'ration' ? C.red : C.teal],
          ['SOLVE', `${scn.solve_ms} MS`, C.cyan],
        ].map(([k, v, c]: any, i) => (
          <span key={i} style={{ marginLeft: 16, color: C.mut }}>{k} <b style={{ color: c }}>{v}</b></span>
        ))}
      </div>

      <div style={{ flex: 1, display: 'flex', minHeight: 0 }}>
        {/* map / knowledge graph */}
        <div style={{ flex: 1, position: 'relative' }}>
          {view === 'map' ? <WarMap data={data} scenario={scn} projection={proj} /> : <KgView highlightChokepoints={scn.blocked} />}
          <div style={{ position: 'absolute', top: 10, right: 10, display: 'flex', gap: 4, background: 'rgba(8,11,16,.85)', border: `1px solid ${C.line}`, borderRadius: 6, padding: 3, zIndex: 5 }}>
            {(['map', 'graph'] as const).map((v) => (
              <button key={v} onClick={() => setView(v)} style={{
                cursor: 'pointer', fontSize: 10.5, fontWeight: 700, padding: '5px 12px', borderRadius: 4,
                fontFamily: MONO, letterSpacing: 0.8, textTransform: 'uppercase',
                border: 'none', background: view === v ? 'rgba(93,202,165,.18)' : 'transparent',
                color: view === v ? C.teal : C.mut,
              }}>{v === 'map' ? 'Live map' : 'Knowledge graph'}</button>
            ))}
          </div>
          {view === 'map' && (
          <div style={{ position: 'absolute', top: 10, left: 10, display: 'flex', gap: 4, background: 'rgba(8,11,16,.85)', border: `1px solid ${C.line}`, borderRadius: 6, padding: 3, zIndex: 5 }}>
            {(['globe', 'mercator'] as const).map((p) => (
              <button key={p} onClick={() => setProj(p)} style={{
                cursor: 'pointer', fontSize: 10.5, fontWeight: 700, padding: '5px 12px', borderRadius: 4,
                fontFamily: MONO, letterSpacing: 0.8, textTransform: 'uppercase',
                border: 'none', background: proj === p ? 'rgba(46,201,255,.15)' : 'transparent',
                color: proj === p ? C.cyan : C.mut,
              }}>{p === 'globe' ? '3D globe' : '2D map'}</button>
            ))}
          </div>
          )}
          {view === 'map' && (
          <div style={{ position: 'absolute', bottom: 10, left: 10, background: 'rgba(8,11,16,.82)', border: `1px solid ${C.line}`, borderRadius: 6, padding: '8px 10px', fontSize: 11, color: C.mut }}>
            <div><span style={{ color: C.cyan, fontWeight: 700 }}>━</span> <b style={{ color: C.cyan }}>optimizer flow</b> — the LP&apos;s plan: source → refinery, width = kb/d (hover any line)</div>
            <div style={{ marginTop: 3 }}><span style={{ color: C.red }}>●</span> cut route / blocked strait &nbsp; <span style={{ color: '#3d7a68' }}>●</span> pre-crisis corridor (dimmed) &nbsp; <span style={{ color: C.blue }}>┅</span> bypass pipeline (6.5 Mb/d)</div>
            <div style={{ marginTop: 3 }}>refinery ● size = capacity, colour = Hormuz exposure (blue→red)</div>
            <div style={{ marginTop: 3, color: '#5a6472' }}>*46% Hormuz exposure derived from real DGCIS import records</div>
          </div>
          )}
        </div>

        {/* right intelligence panel */}
        <div style={{ width: 430, borderLeft: `1px solid ${C.line}`, padding: 14, overflowY: 'auto' }}>
          <div style={{ fontSize: 10, letterSpacing: 1.2, textTransform: 'uppercase', color: C.mut, marginBottom: 8 }}>Disruption scenario</div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 6, marginBottom: 14 }}>
            {data.scenarios.map((s: any, i: number) => (
              <button key={s.key} onClick={() => setSi(i)} style={{
                textAlign: 'left', cursor: 'pointer', fontSize: 11.5, lineHeight: 1.2, padding: '8px 10px', borderRadius: 6,
                border: `1px solid ${i === si ? C.teal : C.line}`, background: i === si ? 'rgba(93,202,165,.12)' : 'transparent',
                color: i === si ? C.teal : C.mut, fontWeight: i === si ? 700 : 500,
              }}>{s.name}</button>
            ))}
          </div>

          <Card title="① Early-warning signal (real GDELT)" accent={C.blue} led={[sig.source === 'live' ? 'LIVE FEED' : 'REAL SERIES · CACHED', C.teal]}>
            <Row k="Alert raised" v={sig.alert_day} c={C.amber} />
            <Row k="Market repriced" v={sig.market_day} />
            <Row k="Lead time" v={`${sig.lead_days} days ahead`} c={C.teal} />
            <div style={{ display: 'flex', alignItems: 'flex-end', gap: 1.5, height: 34, marginTop: 8 }}>
              {sig.series.slice(9, 26).map((p: any, j: number) => (
                <div key={j} title={`${p.day}: ${p.x}× baseline`} style={{ flex: 1, height: `${(p.x / maxX) * 100}%`, background: p.alerted ? C.amber : '#2b3a49', borderRadius: 1 }} />
              ))}
            </div>
            <div style={{ fontSize: 10, color: '#5a6472', marginTop: 3 }}>coverage vs baseline · June 2025 Hormuz crisis</div>
            <div style={{ fontSize: 10.5, color: C.mut, marginTop: 5, paddingTop: 5, borderTop: `1px solid ${C.line}` }}>
              multi-source cross-check: <b style={{ color: '#b6c0cc' }}>{(data.vessels || []).filter((v: any) => v.source === 'live').length} live AIS tracks</b> (Malacca) · Hormuz snapshot · sanctions modelled as a first-class scenario axis
            </div>
          </Card>

          <Card title="② Projected impact + twin deficit" accent={C.red}>
            <Row k="Brent" v={`$${cas.brent}/bbl (+${cas.brent_pct}%)`} c={C.red} />
            {cas.brent_hi > cas.brent_lo && (
              <div style={{ fontSize: 10.5, color: C.mut, margin: '-2px 0 2px' }}>
                sensitivity band ${cas.brent_lo}–${cas.brent_hi} (price-impact 5–12 $/bbl per Mb/d — assumption swept, not asserted)
              </div>
            )}
            <Row k="Retail fuel" v={`~₹${cas.pump}/L`} />
            <Row k="GDP drag" v={`−${cas.gdp} pp`} />
            <Row k="Extra oil bill" v={`$${cas.annual_bn} bn/yr`} c={C.amber} />
            <div style={{ marginTop: 6, paddingTop: 6, borderTop: `1px solid ${C.line}` }}>
              <Row k="Current-acct deficit" v={`${cas.cad_base}% → ${cas.cad_stressed}% GDP`} c={C.red} />
              <div style={{ fontSize: 10.5, color: C.mut, marginTop: 4 }}>India can&apos;t sustain this in USD → rationing forced <i>(validated: L. Powell, ORF)</i></div>
            </div>
          </Card>

          <Card title="③ Reroute — naive vs KARNADHAR" accent={C.teal} led={[`LP · ${scn.solve_ms} MS`, C.cyan]}>
            <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
              <div style={{ flex: 1, background: 'rgba(226,75,74,.08)', border: `1px solid ${C.red}33`, borderRadius: 6, padding: 8 }}>
                <div style={{ fontSize: 10, color: C.mut }}>Naive (fungible)</div>
                <div style={{ fontSize: 15, fontWeight: 800, color: scn.naive.feasible ? C.mut : C.red }}>{scn.naive.feasible ? 'FEASIBLE' : 'INFEASIBLE'}</div>
                <div style={{ fontSize: 11, color: C.mut }}>
                  {scn.naive.unrunnable > 0 ? `${scn.naive.unrunnable.toFixed(0)} kb/d un-runnable` :
                    (!scn.naive.feasible && scn.naive.breaches?.length ? `${scn.naive.breaches.length} blend-limit breach${scn.naive.breaches.length > 1 ? 'es' : ''}` : '')}
                  {scn.naive.unmet > 0 ? ` · ${scn.naive.unmet.toFixed(0)} unmet` : ''}
                </div>
              </div>
              <div style={{ flex: 1, background: 'rgba(93,202,165,.08)', border: `1px solid ${C.teal}44`, borderRadius: 6, padding: 8 }}>
                <div style={{ fontSize: 10, color: C.mut }}>KARNADHAR (grade-aware)</div>
                <div style={{ fontSize: 15, fontWeight: 800, color: scn.smart.feasible ? C.teal : C.amber }}>{scn.smart.feasible ? 'FEASIBLE' : 'PARTIAL'}</div>
                <div style={{ fontSize: 11, color: C.mut }}>{scn.smart.unmet > 0 ? `${scn.smart.unmet.toFixed(0)} kb/d demand cut` : 'all barrels runnable'}</div>
              </div>
            </div>
            <Row k="Gap to re-source" v={`${scn.gap_kbd.toFixed(0)} kb/d`} />
            {scn.naive.usable_short > 0 && (
              <Row k="Usable shortfall (naive → ours)" v={`${scn.naive.usable_short.toFixed(0)} → ${scn.smart.usable_short.toFixed(0)} kb/d`} c={C.teal} />
            )}
            <Row k="Yield value protected" v={`$${yieldProt} M/day`} c={C.teal} />
            {scn.smart.extra_vlcc > 0.5 && (
              <Row k="Extra tankers tied up" v={`+${scn.smart.extra_vlcc.toFixed(0)} VLCC-equiv`} c={C.amber} />
            )}
            <Row k="Reserve runway" v={`~${scn.smart.effective_spr}d vs ${scn.smart.spr_bridge}d bridge`} />
            {scn.smart.spr_margin < 0 && (
              <div style={{ fontSize: 10.5, color: C.amber, marginTop: 3 }}>
                ⚠ voyage bridge exceeds stretched reserves by {Math.abs(scn.smart.spr_margin).toFixed(0)}d — the model
                flags a demand-management window (a finding, not a failure)
              </div>
            )}
            {scn.smart.marginals?.length > 0 && (
              <div style={{ fontSize: 10.5, color: C.mut, marginTop: 5, paddingTop: 5, borderTop: `1px solid ${C.line}` }}>
                marginal barrel (LP shadow price): <b style={{ color: '#b6c0cc' }}>{scn.smart.marginals[0].source} {scn.smart.marginals[0].grade}</b> — 1 extra kb/d saves <b style={{ color: C.teal }}>${scn.smart.marginals[0].shadow_kusd_per_kbd}k/day</b>
              </div>
            )}
            <div style={{ maxHeight: 130, overflowY: 'auto', marginTop: 8, borderTop: `1px solid ${C.line}`, paddingTop: 6 }}>
              {scn.smart.plan.filter((r: any) => r.kbd >= 5).slice(0, 12).map((row: any, j: number) => (
                <div key={j} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, padding: '1px 0', color: C.mut }}>
                  <span style={{ color: '#b6c0cc' }}>{row.refinery}</span>
                  <span>← {row.source} <b style={{ color: C.text }}>{row.kbd.toFixed(1)}</b></span>
                </div>
              ))}
            </div>
          </Card>

          <Card title="⑤ Executive brief — the pipeline's final product" accent={C.blue}>
            {(scn.brief || []).map((ln: string, j: number) => {
              const dash = ln.indexOf(' - ');
              const head = dash > 0 ? ln.slice(0, dash) : '';
              const body = dash > 0 ? ln.slice(dash + 3) : ln;
              return (
                <div key={j} style={{ fontSize: 11.5, lineHeight: 1.45, padding: '2.5px 0', color: C.mut }}>
                  {head && <b style={{ color: '#b6c0cc' }}>{head} · </b>}{body}
                </div>
              );
            })}
            {scn.spr && scn.spr.verdict === 'ration' && (
              <div style={{ fontSize: 10.5, color: C.amber, marginTop: 4 }}>
                SPR scheduler: even max drawdown can&apos;t bridge this — {scn.spr.demand_mgmt_kbd.toFixed(0)} kb/d must come from demand management
              </div>
            )}
            <div style={{ fontSize: 10, color: '#5a6472', marginTop: 6 }}>engine numbers · template words (Claude drop-in via API key writes prose, never numbers)</div>
          </Card>

          <Card title="④ Multi-commodity lens — same disruption, every import" accent={C.amber}>
            {(() => {
              const blocked = new Set(scn.blocked || []);
              const sanc = new Set((scn.sanctioned || []).map((s: string) => s.toUpperCase()));
              const rows = (data.commodities || []).map((c: any) => {
                const cp = Object.entries(c.chokepoints || {}).filter(([k]) => blocked.has(k))
                  .reduce((a, [, v]: any) => a + v, 0);
                const sp = Object.entries(c.suppliers || {}).filter(([k]) => sanc.has(k.toUpperCase()))
                  .reduce((a, [, v]: any) => a + v, 0);
                return { ...c, hit: Math.min(1, cp + sp) };
              }).sort((a: any, b: any) => b.hit - a.hit);
              return rows.slice(0, 6).map((c: any, j: number) => (
                <div key={j} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '2.5px 0' }}>
                  <span style={{ width: 118, fontSize: 11.5, color: '#b6c0cc', flexShrink: 0 }}>{c.name}</span>
                  <div style={{ flex: 1, height: 7, background: '#1a2230', borderRadius: 3, overflow: 'hidden' }}>
                    <div style={{ width: `${c.hit * 100}%`, height: '100%', borderRadius: 3, background: c.hit > 0.45 ? C.red : c.hit > 0.2 ? C.amber : '#3a4a5c' }} />
                  </div>
                  <span style={{ width: 34, fontSize: 11.5, fontWeight: 700, textAlign: 'right', color: c.hit > 0.45 ? C.red : c.hit > 0.2 ? C.amber : C.mut }}>{Math.round(c.hit * 100)}%</span>
                  <span style={{ width: 52, fontSize: 10, color: '#5a6472', textAlign: 'right' }}>IVX {c.ivx}</span>
                </div>
              ));
            })()}
            <div style={{ fontSize: 10, color: '#5a6472', marginTop: 6 }}>share of each import hit by this disruption · IVX = structural vulnerability (0–100) · same engine, any material</div>
          </Card>

          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: C.mut, padding: '2px 4px' }}>
            <span>signal → recommendation</span>
            <span style={{ color: C.teal, fontWeight: 700 }}>{scn.solve_ms} ms · vs 47-day baseline</span>
          </div>
        </div>
      </div>
    </div>
  );
}
