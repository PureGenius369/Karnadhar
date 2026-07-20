// requestAnimationFrame resilience shim — MUST be imported before maplibre-gl.
//
// MapLibre drives its entire lifecycle (style load -> render -> 'load' event)
// from requestAnimationFrame. Embedded/off-screen surfaces (IDE preview panes,
// some screen-capture pipelines) report document.visibilityState === 'hidden'
// and never deliver frames, so the map silently never paints. This hybrid lets
// the native rAF win whenever frames flow (visible tab: zero behaviour change),
// and falls back to a ~15fps timer when they don't.
if (typeof window !== 'undefined' && !(window as any).__rafShimInstalled) {
  (window as any).__rafShimInstalled = true;
  const native = window.requestAnimationFrame.bind(window);
  const nativeCancel = window.cancelAnimationFrame.bind(window);
  const pending = new Map<number, number>(); // rafId -> timeoutId

  window.requestAnimationFrame = (cb: FrameRequestCallback): number => {
    const id = native((t) => {
      const to = pending.get(id);
      if (to !== undefined) { clearTimeout(to); pending.delete(id); }
      cb(t);
    });
    const to = window.setTimeout(() => {
      if (pending.has(id)) { pending.delete(id); nativeCancel(id); cb(performance.now()); }
    }, 64);
    pending.set(id, to);
    return id;
  };

  window.cancelAnimationFrame = (id: number) => {
    const to = pending.get(id);
    if (to !== undefined) { clearTimeout(to); pending.delete(id); }
    nativeCancel(id);
  };
}
export {};
