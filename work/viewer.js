(() => {
  const canvas = document.querySelector('#tray-view');
  const ctx = canvas?.getContext('2d');
  if (!ctx || !window.trayMesh) return;

  let azimuth = -0.72;
  let elevation = 0.57;
  let exploded = true;
  let lastPointer;

  function draw() {
    const { width, height } = canvas.getBoundingClientRect();
    if (!width || !height) return;
    const ratio = Math.min(devicePixelRatio, 1.5);
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
    const c = Math.cos(azimuth), s = Math.sin(azimuth);
    const ce = Math.cos(elevation), se = Math.sin(elevation);
    const w = canvas.width, h = canvas.height;
    const zoom = Math.min(w / 440, h / 230);
    const rgba = ctx.createImageData(w, h);
    const depth = new Float32Array(w * h).fill(-Infinity);
    for (const part of window.trayMesh) {
      const color = part.color.match(/[a-f\d]{2}/gi).map(value => parseInt(value, 16));
      const points = part.vertices.map(([x, y, z]) => {
        const dx = x - 180, dy = y - 84;
        const flat = s * dx + c * dy;
        const vertical = z + (exploded ? part.lift - 44 : -22);
        return [c * dx - s * dy, ce * vertical + se * flat, se * vertical - ce * flat];
      });
      for (const [i, j, k] of part.triangles) {
        const a = points[i], b = points[j], d = points[k];
        const u = b.map((value, index) => value - a[index]);
        const v = d.map((value, index) => value - a[index]);
        const nx = u[1] * v[2] - u[2] * v[1];
        const ny = u[2] * v[0] - u[0] * v[2];
        const nz = u[0] * v[1] - u[1] * v[0];
        if (nz <= 0.00001) continue;
        const norm = Math.hypot(nx, ny, nz);
        const shade = Math.max(0.37, 0.68 + 0.32 * (-0.3 * nx + 0.75 * ny + 0.55 * nz) / norm);
        const rgb = color.map(value => Math.round(shade * value));
        const x0 = w / 2 + a[0] * zoom, y0 = h / 2 - a[1] * zoom;
        const x1 = w / 2 + b[0] * zoom, y1 = h / 2 - b[1] * zoom;
        const x2 = w / 2 + d[0] * zoom, y2 = h / 2 - d[1] * zoom;
        const den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2);
        if (Math.abs(den) < 1e-8) continue;
        const minX = Math.max(0, Math.floor(Math.min(x0, x1, x2)));
        const minY = Math.max(0, Math.floor(Math.min(y0, y1, y2)));
        const maxX = Math.min(w - 1, Math.ceil(Math.max(x0, x1, x2)));
        const maxY = Math.min(h - 1, Math.ceil(Math.max(y0, y1, y2)));
        for (let y = minY; y <= maxY; y++) {
          for (let x = minX; x <= maxX; x++) {
            const u = ((y1 - y2) * (x + 0.5 - x2) + (x2 - x1) * (y + 0.5 - y2)) / den;
            const v = ((y2 - y0) * (x + 0.5 - x2) + (x0 - x2) * (y + 0.5 - y2)) / den;
            const t = 1 - u - v;
            if (Math.min(u, v, t) < -1e-6) continue;
            const z = a[2] * u + b[2] * v + d[2] * t;
            const index = y * w + x;
            if (z <= depth[index]) continue;
            depth[index] = z;
            rgba.data[index * 4] = rgb[0];
            rgba.data[index * 4 + 1] = rgb[1];
            rgba.data[index * 4 + 2] = rgb[2];
            rgba.data[index * 4 + 3] = 255;
          }
        }
      }
    }
    ctx.putImageData(rgba, 0, 0);
  }

  function rotate(dx, dy) {
    azimuth += dx;
    elevation = Math.max(-1.34, Math.min(1.34, elevation + dy));
    draw();
  }
  canvas.addEventListener('pointerdown', event => {
    canvas.setPointerCapture(event.pointerId);
    lastPointer = [event.clientX, event.clientY];
  });
  canvas.addEventListener('pointermove', event => {
    if (!lastPointer) return;
    rotate((event.clientX - lastPointer[0]) / 115, (event.clientY - lastPointer[1]) / 115);
    lastPointer = [event.clientX, event.clientY];
  });
  for (const event of ['pointerup', 'pointercancel', 'lostpointercapture']) {
    canvas.addEventListener(event, () => { lastPointer = null; });
  }

  const controls = document.querySelector('#viewer-controls');
  controls.addEventListener('click', event => {
    const action = event.target.dataset.view;
    if (!action) return;
    if (action === 'left') return rotate(-0.3, 0);
    if (action === 'right') return rotate(0.3, 0);
    if (action === 'reset') {
      azimuth = -0.72;
      elevation = 0.57;
      return draw();
    }
    exploded = action === 'exploded';
    controls.querySelectorAll('[aria-pressed]').forEach(button => {
      button.setAttribute('aria-pressed', String(button.dataset.view === action));
    });
    draw();
  });
  controls.hidden = false;
  canvas.classList.add('ready');
  new ResizeObserver(draw).observe(canvas);
  draw();
})();
