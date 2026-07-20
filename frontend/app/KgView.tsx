'use client';
import './rafShim';
import { useEffect, useRef, useState } from 'react';

// Knowledge-graph view: supplier -> chokepoint -> refinery relationship web.
// Self-contained canvas force layout (50 nodes / 163 edges — no graph lib needed).

const COLORS: Record<string, string> = {
  supplier: '#f2a623', chokepoint: '#8b95a3', refinery: '#4b96dc',
};
const EDGE: Record<string, string> = {
  SUPPLIES: 'rgba(93,202,165,0.35)', SHIPS_VIA: 'rgba(139,149,163,0.45)',
  THREATENS: 'rgba(226,75,74,0.55)',
};

type N = { id: string; type: string; label: string; r: number; x: number; y: number; vx: number; vy: number; meta: any };

export default function KgView({ highlightChokepoints }: { highlightChokepoints: string[] }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [kg, setKg] = useState<any>(null);
  const [hover, setHover] = useState<{ n: N; px: number; py: number } | null>(null);
  const sim = useRef<{ nodes: N[]; edges: any[]; byId: Map<string, N> } | null>(null);

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
    sim.current = { nodes, edges, byId };

    let raf = 0;
    let tick = 0;
    const step = () => {
      tick++;
      // forces: pairwise repulsion + edge springs + center gravity
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
      for (const n of nodes) { n.vx *= 0.82; n.vy *= 0.82; n.x += n.vx; n.y += n.vy; }

      // draw
      const w = parent.clientWidth, h = parent.clientHeight;
      const dpr = window.devicePixelRatio || 1;
      if (canvas.width !== w * dpr) { canvas.width = w * dpr; canvas.height = h * dpr; }
      canvas.style.width = w + 'px'; canvas.style.height = h + 'px';
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, w, h);
      ctx.fillStyle = '#080b10'; ctx.fillRect(0, 0, w, h);
      const cx = w / 2, cy = h / 2;
      const scale = Math.min(w, h) / 780;

      for (const e of edges) {
        const a = byId.get(e.from)!, b = byId.get(e.to)!;
        const hot = e.type === 'THREATENS' && highlightChokepoints.some((c) => e.from === 'chokepoint:' + c);
        ctx.strokeStyle = hot ? 'rgba(226,75,74,0.95)' : EDGE[e.type] || '#333';
        ctx.lineWidth = e.type === 'SUPPLIES' ? Math.max(0.5, Math.sqrt(e.kbd || 1) / 14)
          : e.type === 'THREATENS' ? Math.max(1, (e.exposure || 0.1) * (hot ? 5 : 3)) : 1;
        ctx.beginPath();
        ctx.moveTo(cx + a.x * scale, cy + a.y * scale);
        ctx.lineTo(cx + b.x * scale, cy + b.y * scale);
        ctx.stroke();
      }
      for (const n of nodes) {
        const blocked = n.type === 'chokepoint' && highlightChokepoints.includes(n.label);
        ctx.fillStyle = blocked ? '#e24b4a' : COLORS[n.type];
        ctx.beginPath();
        ctx.arc(cx + n.x * scale, cy + n.y * scale, n.r, 0, Math.PI * 2);
        ctx.fill();
        if (n.type !== 'supplier' || n.r > 6) {
          ctx.fillStyle = '#cbd3dd'; ctx.font = '10px system-ui'; ctx.textAlign = 'center';
          ctx.fillText(n.label, cx + n.x * scale, cy + n.y * scale - n.r - 4);
        }
      }
      if (tick < 1200) raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);

    const onMove = (ev: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      const w = parent.clientWidth, h = parent.clientHeight;
      const cx = w / 2, cy = h / 2, scale = Math.min(w, h) / 780;
      const mx = ev.clientX - rect.left, my = ev.clientY - rect.top;
      let best: N | null = null, bd = 12;
      for (const n of nodes) {
        const d = Math.hypot(cx + n.x * scale - mx, cy + n.y * scale - my) - n.r;
        if (d < bd) { bd = d; best = n; }
      }
      setHover(best ? { n: best, px: mx, py: my } : null);
    };
    canvas.addEventListener('mousemove', onMove);
    return () => { cancelAnimationFrame(raf); canvas.removeEventListener('mousemove', onMove); };
  }, [kg, highlightChokepoints]);

  return (
    <div style={{ position: 'absolute', inset: 0 }}>
      <canvas ref={canvasRef} />
      <div style={{ position: 'absolute', top: 10, left: 10, background: 'rgba(8,11,16,.85)', border: '1px solid #1e2733', borderRadius: 6, padding: '8px 10px', fontSize: 11, color: '#8b95a3', lineHeight: 1.7 }}>
        <div style={{ color: '#e8edf2', fontWeight: 700, marginBottom: 2 }}>Knowledge graph — 50 nodes · 163 edges</div>
        <div><span style={{ color: '#f2a623' }}>●</span> supplier&nbsp;&nbsp;<span style={{ color: '#8b95a3' }}>●</span> chokepoint&nbsp;&nbsp;<span style={{ color: '#4b96dc' }}>●</span> refinery</div>
        <div><span style={{ color: '#5dcaa5' }}>—</span> SUPPLIES (real kb/d)&nbsp;&nbsp;<span style={{ color: '#e24b4a' }}>—</span> THREATENS (exposure)</div>
        <div style={{ color: '#5a6472' }}>edges carry provenance: DGCIS · route mapping · derived</div>
      </div>
      {hover && (
        <div style={{ position: 'absolute', left: hover.px + 14, top: hover.py + 10, background: 'rgba(8,11,16,.95)', border: '1px solid #243040', borderRadius: 6, padding: '7px 10px', fontSize: 11.5, color: '#e8edf2', pointerEvents: 'none', maxWidth: 240 }}>
          <b style={{ color: COLORS[hover.n.type] }}>{hover.n.label}</b>
          <span style={{ color: '#8b95a3' }}> · {hover.n.type}</span>
          {hover.n.type === 'supplier' && (
            <div style={{ color: '#8b95a3' }}>{hover.n.meta.grade} · API {hover.n.meta.api} · S {hover.n.meta.sulphur}% · Asph {hover.n.meta.asphaltene}% · {Math.round(hover.n.meta.available_kbd)} kb/d</div>
          )}
          {hover.n.type === 'refinery' && (
            <div style={{ color: '#8b95a3' }}>{Math.round(hover.n.meta.capacity_kbd)} kb/d · Nelson {hover.n.meta.nelson} · API {hover.n.meta.api_window?.[0]}–{hover.n.meta.api_window?.[1]} · desulph ≤{hover.n.meta.desulph_limit}%</div>
          )}
        </div>
      )}
    </div>
  );
}
