'use client';
import './rafShim';
import { useEffect, useRef, useState } from 'react';

// Knowledge-graph view: supplier -> chokepoint -> refinery relationship web.
// Self-contained canvas force layout (50 nodes / 163 edges — no graph lib).
// Fully interactive: wheel = zoom to cursor, drag empty space = pan,
// drag a node = move it (sim reheats), double-click = reset view.

const COLORS: Record<string, string> = {
  supplier: '#f2a623', chokepoint: '#8b95a3', refinery: '#4b96dc',
};
const EDGE: Record<string, string> = {
  SUPPLIES: 'rgba(93,202,165,0.35)', SHIPS_VIA: 'rgba(139,149,163,0.45)',
  THREATENS: 'rgba(226,75,74,0.55)',
};
const MONO = 'ui-monospace, Consolas, monospace';

type N = { id: string; type: string; label: string; r: number; x: number; y: number; vx: number; vy: number; meta: any };

export default function KgView({ highlightChokepoints }: { highlightChokepoints: string[] }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [kg, setKg] = useState<any>(null);
  const [hover, setHover] = useState<{ n: N; px: number; py: number } | null>(null);
  const view = useRef({ k: 1, x: 0, y: 0 });          // zoom + pan transform
  const alive = useRef(0);                             // physics heat (frames left)

  useEffect(() => { fetch('/karnadhar_kg.json').then((r) => r.json()).then(setKg); }, []);

  useEffect(() => {
    if (!kg || !canvasRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d')!;
    const parent = canvas.parentElement!;

    const nodes: N[] = kg.nodes.map((n: any, i: number) => {
      const r = n.type === 'chokepoint' ? 9
        : n.type === 'refinery' ? Math.max(7, Math.sqrt(n.capacity_kbd || 100) / 3.2)
        : Math.max(4, Math.sqrt(n.available_kbd || 50) / 5.5);
      const a = (i / kg.nodes.length) * Math.PI * 2;
      const rad = n.type === 'chokepoint' ? 60 : n.type === 'refinery' ? 190 : 320;
      return { id: n.id, type: n.type, label: n.label, r, meta: n,
               x: Math.cos(a) * rad, y: Math.sin(a) * rad, vx: 0, vy: 0 };
    });
    const byId = new Map(nodes.map((n) => [n.id, n]));
    const edges = kg.edges.filter((e: any) => byId.has(e.from) && byId.has(e.to));
    alive.current = 1200;
    (window as any).__kg = { view: view.current, nodes };   // debug/verify handle

    // screen <-> world helpers (world = sim coords scaled to fit, then view k/x/y)
    const geom = () => {
      const w = parent.clientWidth, h = parent.clientHeight;
      return { w, h, cx: w / 2, cy: h / 2, base: Math.min(w, h) / 780 };
    };
    const toScreen = (n: N, g: any) => ({
      x: g.cx + view.current.x + n.x * g.base * view.current.k,
      y: g.cy + view.current.y + n.y * g.base * view.current.k,
    });

    const drag: { node: N | null; panning: boolean; lx: number; ly: number } =
      { node: null, panning: false, lx: 0, ly: 0 };

    let raf = 0;
    const step = () => {
      if (alive.current > 0) {
        alive.current--;
        for (let i = 0; i < nodes.length; i++) {
          const a = nodes[i];
          for (let j = i + 1; j < nodes.length; j++) {
            const b = nodes[j];
            let dx = a.x - b.x, dy = a.y - b.y;
            let d2 = dx * dx + dy * dy || 1;
            if (d2 < 90000) {
              const f = 1400 / d2;
              const d = Math.sqrt(d2);
              dx /= d; dy /= d;
              a.vx += dx * f; a.vy += dy * f;
              b.vx -= dx * f; b.vy -= dy * f;
            }
          }
          a.vx -= a.x * 0.0022; a.vy -= a.y * 0.0022;  // gravity to center
        }
        for (const e of edges) {
          const a = byId.get(e.from)!, b = byId.get(e.to)!;
          const dx = b.x - a.x, dy = b.y - a.y;
          const d = Math.sqrt(dx * dx + dy * dy) || 1;
          const want = e.type === 'SHIPS_VIA' ? 110 : 150;
          const f = (d - want) * 0.0035;
          a.vx += (dx / d) * f; a.vy += (dy / d) * f;
          b.vx -= (dx / d) * f; b.vy -= (dy / d) * f;
        }
        for (const n of nodes) {
          if (drag.node === n) { n.vx = 0; n.vy = 0; continue; }  // pinned while dragged
          n.vx *= 0.82; n.vy *= 0.82; n.x += n.vx; n.y += n.vy;
        }
      }

      // draw (always — so pan/zoom stay live after the sim settles)
      const g = geom();
      const dpr = window.devicePixelRatio || 1;
      if (canvas.width !== g.w * dpr) { canvas.width = g.w * dpr; canvas.height = g.h * dpr; }
      canvas.style.width = g.w + 'px'; canvas.style.height = g.h + 'px';
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, g.w, g.h);
      ctx.fillStyle = '#080b10'; ctx.fillRect(0, 0, g.w, g.h);
      const k = view.current.k;

      for (const e of edges) {
        const a = toScreen(byId.get(e.from)!, g), b = toScreen(byId.get(e.to)!, g);
        const hot = e.type === 'THREATENS' && highlightChokepoints.some((c) => e.from === 'chokepoint:' + c);
        ctx.strokeStyle = hot ? 'rgba(226,75,74,0.95)' : EDGE[e.type] || '#333';
        ctx.lineWidth = (e.type === 'SUPPLIES' ? Math.max(0.5, Math.sqrt(e.kbd || 1) / 14)
          : e.type === 'THREATENS' ? Math.max(1, (e.exposure || 0.1) * (hot ? 5 : 3)) : 1) * Math.sqrt(k);
        ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
      }
      const showAll = k > 1.6;                       // zoom in -> every label appears
      for (const n of nodes) {
        const s = toScreen(n, g);
        const rr = n.r * Math.sqrt(k);
        const blocked = n.type === 'chokepoint' && highlightChokepoints.includes(n.label);
        ctx.fillStyle = blocked ? '#e24b4a' : COLORS[n.type];
        ctx.beginPath(); ctx.arc(s.x, s.y, rr, 0, Math.PI * 2); ctx.fill();
        if (blocked) { ctx.strokeStyle = 'rgba(226,75,74,.5)'; ctx.lineWidth = 6; ctx.stroke(); }
        if (showAll || n.type !== 'supplier' || n.r > 6) {
          ctx.fillStyle = '#cbd3dd'; ctx.font = `10px ${MONO}`; ctx.textAlign = 'center';
          ctx.fillText(n.label, s.x, s.y - rr - 4);
        }
      }
      raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);

    // ---------- interaction ----------
    const pick = (mx: number, my: number): N | null => {
      const g = geom();
      let best: N | null = null, bd = 12;
      for (const n of nodes) {
        const s = toScreen(n, g);
        const d = Math.hypot(s.x - mx, s.y - my) - n.r * Math.sqrt(view.current.k);
        if (d < bd) { bd = d; best = n; }
      }
      return best;
    };

    const onWheel = (ev: WheelEvent) => {
      ev.preventDefault();
      const rect = canvas.getBoundingClientRect();
      const mx = ev.clientX - rect.left, my = ev.clientY - rect.top;
      const g = geom();
      const v = view.current;
      const k2 = Math.min(6, Math.max(0.35, v.k * Math.exp(-ev.deltaY * 0.0012)));
      // keep the point under the cursor fixed while zooming
      const wx = (mx - g.cx - v.x) / v.k, wy = (my - g.cy - v.y) / v.k;
      v.x = mx - g.cx - wx * k2;
      v.y = my - g.cy - wy * k2;
      v.k = k2;
    };
    const onDown = (ev: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      const mx = ev.clientX - rect.left, my = ev.clientY - rect.top;
      const n = pick(mx, my);
      if (n) { drag.node = n; alive.current = Math.max(alive.current, 240); }
      else drag.panning = true;
      drag.lx = mx; drag.ly = my;
      canvas.style.cursor = n ? 'grabbing' : 'move';
    };
    const onMove = (ev: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      const mx = ev.clientX - rect.left, my = ev.clientY - rect.top;
      const g = geom(); const v = view.current;
      if (drag.node) {
        drag.node.x += (mx - drag.lx) / (g.base * v.k);
        drag.node.y += (my - drag.ly) / (g.base * v.k);
        drag.lx = mx; drag.ly = my;
        alive.current = Math.max(alive.current, 180);
        setHover({ n: drag.node, px: mx, py: my });
        return;
      }
      if (drag.panning) {
        v.x += mx - drag.lx; v.y += my - drag.ly;
        drag.lx = mx; drag.ly = my;
        return;
      }
      const n = pick(mx, my);
      canvas.style.cursor = n ? 'grab' : 'default';
      setHover(n ? { n, px: mx, py: my } : null);
    };
    const onUp = () => { drag.node = null; drag.panning = false; canvas.style.cursor = 'default'; };
    const onDbl = () => { view.current.k = 1; view.current.x = 0; view.current.y = 0; };

    canvas.addEventListener('wheel', onWheel, { passive: false });
    canvas.addEventListener('mousedown', onDown);
    canvas.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onUp);
    canvas.addEventListener('dblclick', onDbl);
    return () => {
      cancelAnimationFrame(raf);
      canvas.removeEventListener('wheel', onWheel);
      canvas.removeEventListener('mousedown', onDown);
      canvas.removeEventListener('mousemove', onMove);
      window.removeEventListener('mouseup', onUp);
      canvas.removeEventListener('dblclick', onDbl);
    };
  }, [kg, highlightChokepoints]);

  const zoomBtn = (label: string, fn: () => void) => (
    <button onClick={fn} style={{
      width: 30, height: 30, cursor: 'pointer', fontSize: 15, fontFamily: MONO,
      background: 'rgba(8,11,16,.9)', color: '#8b95a3', border: '1px solid #243040',
      borderRadius: 4,
    }}>{label}</button>
  );

  return (
    <div style={{ position: 'absolute', inset: 0 }}>
      <canvas ref={canvasRef} />
      <div style={{ position: 'absolute', top: 10, left: 10, background: 'rgba(8,11,16,.85)', border: '1px solid #1e2733', borderRadius: 6, padding: '8px 10px', fontSize: 11, color: '#8b95a3', lineHeight: 1.7 }}>
        <div style={{ color: '#e8edf2', fontWeight: 700, marginBottom: 2 }}>Knowledge graph — 50 nodes · 163 edges</div>
        <div><span style={{ color: '#f2a623' }}>●</span> supplier&nbsp;&nbsp;<span style={{ color: '#8b95a3' }}>●</span> chokepoint&nbsp;&nbsp;<span style={{ color: '#4b96dc' }}>●</span> refinery</div>
        <div><span style={{ color: '#5dcaa5' }}>—</span> SUPPLIES (real kb/d)&nbsp;&nbsp;<span style={{ color: '#e24b4a' }}>—</span> THREATENS (exposure)</div>
        <div style={{ color: '#5a6472' }}>scroll = zoom · drag = pan · drag a node · double-click = reset</div>
      </div>
      <div style={{ position: 'absolute', right: 12, bottom: 12, display: 'flex', flexDirection: 'column', gap: 6 }}>
        {zoomBtn('+', () => { view.current.k = Math.min(6, view.current.k * 1.35); })}
        {zoomBtn('−', () => { view.current.k = Math.max(0.35, view.current.k / 1.35); })}
        {zoomBtn('⟳', () => { view.current.k = 1; view.current.x = 0; view.current.y = 0; })}
      </div>
      {hover && (
        <div style={{ position: 'absolute', left: hover.px + 14, top: hover.py + 10, background: 'rgba(8,11,16,.95)', border: '1px solid #243040', borderRadius: 6, padding: '7px 10px', fontSize: 11.5, color: '#e8edf2', pointerEvents: 'none', maxWidth: 240 }}>
          <b style={{ color: COLORS[hover.n.type] }}>{hover.n.label}</b>
          <span style={{ color: '#8b95a3' }}> · {hover.n.type}</span>
          {hover.n.type === 'supplier' && (
            <div style={{ color: '#8b95a3', fontFamily: MONO, fontSize: 10.5 }}>{hover.n.meta.grade} · API {hover.n.meta.api} · S {hover.n.meta.sulphur}% · Asph {hover.n.meta.asphaltene}% · {Math.round(hover.n.meta.available_kbd)} kb/d</div>
          )}
          {hover.n.type === 'refinery' && (
            <div style={{ color: '#8b95a3', fontFamily: MONO, fontSize: 10.5 }}>{Math.round(hover.n.meta.capacity_kbd)} kb/d · Nelson {hover.n.meta.nelson} · API {hover.n.meta.api_window?.[0]}–{hover.n.meta.api_window?.[1]} · desulph ≤{hover.n.meta.desulph_limit}%</div>
          )}
        </div>
      )}
    </div>
  );
}
