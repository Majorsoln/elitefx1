/* glasschart.js — chart library ndogo self-contained (vanilla canvas; HAKUNA CDN/dependency).
 * NOTE (deviation-with-reason): charter iliagiza Chart.js file self-contained; env ya build
 * ilizuia network ya CDN (proxy 403) — hii ni mbadala mdogo yenye API: line chart + band + sparkline.
 * Operator anaweza baadaye ku-vendor chart.umd.min.js; templates zinatumia gc.* pekee. */
(function () {
  const CSS = { line: "#35c9a6", grid: "#232a3d", text: "#6b7690", band: "rgba(53,201,166,.12)",
                promise: "#e5b256", bad: "#e0566a" };

  function setup(canvas) {
    const dpr = window.devicePixelRatio || 1;
    const w = canvas.clientWidth || 600, h = canvas.clientHeight || 220;
    canvas.width = w * dpr; canvas.height = h * dpr;
    const ctx = canvas.getContext("2d"); ctx.scale(dpr, dpr);
    return { ctx, w, h };
  }

  function extent(vals) {
    let lo = Math.min(0, ...vals), hi = Math.max(0, ...vals);
    if (lo === hi) { lo -= 1; hi += 1; }
    const pad = (hi - lo) * 0.08; return [lo - pad, hi + pad];
  }

  // Line chart: gc.line(canvas, {labels:[], values:[]}, {promised, bandLo, bandHi})
  window.gc = {
    line(canvas, data, opts) {
      opts = opts || {};
      const { ctx, w, h } = setup(canvas);
      const vals = data.values || [];
      if (!vals.length) { ctx.fillStyle = CSS.text; ctx.font = "12px monospace";
        ctx.fillText("no data", 10, h / 2); return; }
      const extra = [opts.promised, opts.bandLo, opts.bandHi].filter(v => v != null);
      const [lo, hi] = extent(vals.concat(extra));
      const L = 46, B = 22, cw = w - L - 8, chh = h - B - 8;
      const x = i => L + (cw * i) / Math.max(1, vals.length - 1);
      const y = v => 8 + chh - ((v - lo) / (hi - lo)) * chh;
      // gridlines + axis labels
      ctx.strokeStyle = CSS.grid; ctx.fillStyle = CSS.text; ctx.font = "10px monospace";
      for (let g = 0; g <= 4; g++) {
        const gv = lo + ((hi - lo) * g) / 4, gy = y(gv);
        ctx.beginPath(); ctx.moveTo(L, gy); ctx.lineTo(w - 8, gy); ctx.stroke();
        ctx.fillText(gv.toFixed(1), 4, gy + 3);
      }
      // shrinkage band (LIVE-vs-PROMISED)
      if (opts.bandLo != null && opts.bandHi != null) {
        ctx.fillStyle = CSS.band;
        ctx.fillRect(L, y(opts.bandHi), cw, Math.max(1, y(opts.bandLo) - y(opts.bandHi)));
      }
      if (opts.promised != null) {
        ctx.strokeStyle = CSS.promise; ctx.setLineDash([5, 4]);
        ctx.beginPath(); ctx.moveTo(L, y(opts.promised)); ctx.lineTo(w - 8, y(opts.promised)); ctx.stroke();
        ctx.setLineDash([]);
        ctx.fillStyle = CSS.promise; ctx.fillText("promised", w - 64, y(opts.promised) - 4);
      }
      // zero line
      ctx.strokeStyle = CSS.text; ctx.globalAlpha = 0.5;
      ctx.beginPath(); ctx.moveTo(L, y(0)); ctx.lineTo(w - 8, y(0)); ctx.stroke(); ctx.globalAlpha = 1;
      // series
      ctx.strokeStyle = opts.color || CSS.line; ctx.lineWidth = 1.6; ctx.beginPath();
      vals.forEach((v, i) => (i ? ctx.lineTo(x(i), y(v)) : ctx.moveTo(x(0), y(v))));
      ctx.stroke();
      // x labels (mwanzo/kati/mwisho)
      const lab = data.labels || [];
      ctx.fillStyle = CSS.text;
      [0, Math.floor(lab.length / 2), lab.length - 1].forEach(i => {
        if (lab[i] != null) ctx.fillText(String(lab[i]), Math.min(x(i), w - 70), h - 6);
      });
    },
    spark(canvas, values) {
      const { ctx, w, h } = setup(canvas);
      if (!values || !values.length) { ctx.fillStyle = CSS.text; ctx.fillText("no data", 6, h / 2); return; }
      const [lo, hi] = extent(values);
      const x = i => (w * i) / Math.max(1, values.length - 1);
      const y = v => 2 + (h - 4) - ((v - lo) / (hi - lo)) * (h - 4);
      ctx.strokeStyle = values[values.length - 1] >= 0 ? CSS.line : CSS.bad; ctx.lineWidth = 1.4;
      ctx.beginPath(); values.forEach((v, i) => (i ? ctx.lineTo(x(i), y(v)) : ctx.moveTo(0, y(v))));
      ctx.stroke();
    },
  };
})();
