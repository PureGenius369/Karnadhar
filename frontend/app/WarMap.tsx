'use client';
import './rafShim';
import { useEffect, useRef } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

const STYLE: any = {
  version: 8,
  projection: { type: 'globe' },
  sky: {
    'sky-color': '#0b1526',
    'horizon-color': '#16263f',
    'fog-color': '#080b10',
    'sky-horizon-blend': 0.5,
    'horizon-fog-blend': 0.5,
    'atmosphere-blend': ['interpolate', ['linear'], ['zoom'], 0, 1, 6, 0.2],
  },
  sources: {
    carto: {
      type: 'raster',
      tiles: [
        'https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
        'https://b.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
      ],
      tileSize: 256,
      attribution: '© CARTO © OpenStreetMap',
    },
  },
  layers: [
    { id: 'bg', type: 'background', paint: { 'background-color': '#080b10' } },
    { id: 'carto', type: 'raster', source: 'carto', paint: { 'raster-opacity': 0.85 } },
  ],
};

const isCut = (chokepoints: string[], source: string, scn: any) =>
  chokepoints.some((c) => (scn?.blocked || []).includes(c)) ||
  (scn?.cut_sources || []).includes(source);

function routeFC(d: any, scn: any): any {
  return {
    type: 'FeatureCollection',
    features: d.routes.map((r: any) => ({
      type: 'Feature',
      geometry: { type: 'LineString', coordinates: r.path },
      properties: { kbd: r.kbd, cut: isCut(r.chokepoints, r.source, scn) },
    })),
  };
}
function srcFC(d: any, scn: any): any {
  return {
    type: 'FeatureCollection',
    features: d.sources.map((s: any) => ({
      type: 'Feature',
      geometry: { type: 'Point', coordinates: [s.lon, s.lat] },
      properties: { ...s, cut: isCut(s.chokepoints, s.source, scn) },
    })),
  };
}
function chokeFC(d: any, scn: any): any {
  return {
    type: 'FeatureCollection',
    features: Object.entries(d.chokepoints).map(([k, c]: any) => ({
      type: 'Feature',
      geometry: { type: 'Point', coordinates: [c.lon, c.lat] },
      properties: { key: k, label: c.label, blocked: (scn?.blocked || []).includes(k) },
    })),
  };
}
function vesselFC(d: any): any {
  return {
    type: 'FeatureCollection',
    features: (d.vessels || []).map((v: any) => ({
      type: 'Feature',
      geometry: { type: 'Point', coordinates: [v.lon, v.lat] },
      properties: { name: v.name, sog: v.sog, src: v.source },
    })),
  };
}
function refFC(d: any): any {
  return {
    type: 'FeatureCollection',
    features: d.refineries.map((r: any) => ({
      type: 'Feature',
      geometry: { type: 'Point', coordinates: [r.lon, r.lat] },
      properties: { ...r, dietStr: Object.entries(r.diet).map(([k, v]) => `${k} ${v}`).join(', ') },
    })),
  };
}

export default function WarMap({ data, scenario }: { data: any; scenario: any }) {
  const ref = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);

  useEffect(() => {
    if (!ref.current) return;
    const m = new maplibregl.Map({
      container: ref.current, style: STYLE, center: [50, 18], zoom: 2.6,
      attributionControl: false,
      canvasContextAttributes: { preserveDrawingBuffer: true },
    });
    map.current = m;
    (window as any).__map = m;
    m.on('error', (e: any) => console.warn('maplibre error:', e?.error?.message || e));
    m.on('load', () => {
      m.addSource('routes', { type: 'geojson', data: routeFC(data, scenario) });
      m.addLayer({
        id: 'routes', type: 'line', source: 'routes',
        layout: { 'line-cap': 'round' },
        paint: {
          'line-width': ['interpolate', ['linear'], ['get', 'kbd'], 0, 0.8, 2500, 4.5],
          'line-color': ['case', ['get', 'cut'], '#e24b4a', '#1d9e75'],
          'line-opacity': ['case', ['get', 'cut'], 0.85, 0.4],
        },
      });
      // Hormuz bypass pipelines (EIA): Saudi Petroline (Abqaiq->Yanbu, ~5 Mb/d)
      // + UAE ADCOP (Habshan->Fujairah, ~1.5 Mb/d) — the cascade's 6.5 Mb/d
      // "bypass" nuance, drawn where it physically exists
      m.addSource('pipes', {
        type: 'geojson', data: {
          type: 'FeatureCollection', features: [
            { type: 'Feature', properties: { name: 'Petroline (Saudi E-W, ~5 Mb/d)' }, geometry: { type: 'LineString', coordinates: [[49.67, 25.94], [38.06, 24.09]] } },
            { type: 'Feature', properties: { name: 'ADCOP (Habshan-Fujairah, ~1.5 Mb/d)' }, geometry: { type: 'LineString', coordinates: [[53.61, 23.75], [56.35, 25.17]] } },
          ],
        } as any,
      });
      m.addLayer({
        id: 'pipes', type: 'line', source: 'pipes',
        paint: { 'line-color': '#3b8bd4', 'line-width': 2, 'line-dasharray': [1.6, 1.2], 'line-opacity': 0.85 },
      });
      m.addSource('sources', { type: 'geojson', data: srcFC(data, scenario) });
      m.addLayer({
        id: 'sources', type: 'circle', source: 'sources',
        paint: {
          'circle-radius': ['interpolate', ['linear'], ['get', 'kbd'], 0, 3, 2500, 9],
          'circle-color': ['case', ['get', 'cut'], '#e24b4a', '#f2a623'],
          'circle-stroke-width': 1, 'circle-stroke-color': '#000',
        },
      });
      m.addSource('chokes', { type: 'geojson', data: chokeFC(data, scenario) });
      m.addLayer({
        id: 'chokes', type: 'circle', source: 'chokes',
        paint: {
          'circle-radius': 7,
          'circle-color': ['case', ['get', 'blocked'], '#e24b4a', '#5a6472'],
          'circle-stroke-width': 2, 'circle-stroke-color': '#fff',
        },
      });
      m.addLayer({
        id: 'choke-labels', type: 'symbol', source: 'chokes',
        layout: { 'text-field': ['get', 'label'], 'text-size': 11, 'text-offset': [0, 1.4], 'text-anchor': 'top' },
        paint: { 'text-color': '#cbd3dd', 'text-halo-color': '#000', 'text-halo-width': 1.5 },
      });
      m.addSource('vessels', { type: 'geojson', data: vesselFC(data) });
      m.addLayer({
        id: 'vessels', type: 'circle', source: 'vessels',
        paint: {
          'circle-radius': 2.6,
          'circle-color': ['case', ['==', ['get', 'src'], 'live'], '#5dcaa5', '#8b95a3'],
          'circle-stroke-width': 0.6, 'circle-stroke-color': '#04150f',
        },
      });
      m.addSource('refs', { type: 'geojson', data: refFC(data) });
      m.addLayer({
        id: 'refs', type: 'circle', source: 'refs',
        paint: {
          'circle-radius': ['interpolate', ['linear'], ['get', 'kbd'], 100, 6, 1500, 22],
          'circle-color': ['interpolate', ['linear'], ['get', 'hormuz'], 0, '#3b8bd4', 0.9, '#e24b4a'],
          'circle-stroke-width': 1.5, 'circle-stroke-color': '#eef2f6', 'circle-opacity': 0.88,
        },
      });

      const pop = new maplibregl.Popup({ closeButton: false, maxWidth: '280px' });
      m.on('mouseenter', 'refs', (e: any) => {
        m.getCanvas().style.cursor = 'pointer';
        const p = e.features[0].properties;
        pop.setLngLat(e.lngLat).setHTML(
          `<div style="font:12px system-ui;color:#e8edf2">
            <b style="color:#5dcaa5">${p.name}</b><br/>
            ${Math.round(p.kbd)} kb/d · Nelson ${p.nelson}<br/>
            <span style="color:#f2a623">Hormuz exposure ${Math.round(p.hormuz * 100)}%</span><br/>
            <span style="color:#9aa4b0">${p.dietStr}</span>
          </div>`).addTo(m);
      });
      m.on('mouseleave', 'refs', () => { m.getCanvas().style.cursor = ''; pop.remove(); });
      m.on('mouseenter', 'sources', (e: any) => {
        m.getCanvas().style.cursor = 'pointer';
        const p = e.features[0].properties;
        pop.setLngLat(e.lngLat).setHTML(
          `<div style="font:12px system-ui;color:#e8edf2">
            <b style="color:#f2a623">${p.source}</b> — ${p.grade}<br/>
            API ${p.api} · S ${p.sulphur}% · Asph ${p.asph}%<br/>
            $${p.price}/bbl · ${Math.round(p.kbd)} kb/d avail
          </div>`).addTo(m);
      });
      m.on('mouseleave', 'sources', () => { m.getCanvas().style.cursor = ''; pop.remove(); });
      m.on('mouseenter', 'vessels', (e: any) => {
        const p = e.features[0].properties;
        pop.setLngLat(e.lngLat).setHTML(
          `<div style="font:11px system-ui;color:#e8edf2"><b>${p.name || 'vessel'}</b> · ${p.sog} kn · AIS ${p.src === 'live' ? 'LIVE' : 'snapshot'}</div>`).addTo(m);
      });
      m.on('mouseleave', 'vessels', () => pop.remove());
    });
    return () => { m.remove(); if (map.current === m) map.current = null; };
  }, [data]);

  useEffect(() => {
    const m = map.current;
    if (!m || !m.getSource('routes')) return;
    (m.getSource('routes') as any).setData(routeFC(data, scenario));
    (m.getSource('sources') as any).setData(srcFC(data, scenario));
    (m.getSource('chokes') as any).setData(chokeFC(data, scenario));
  }, [scenario, data]);

  return <div ref={ref} style={{ position: 'absolute', inset: 0 }} />;
}
