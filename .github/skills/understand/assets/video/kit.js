// understand video kit for HyperFrames. build-video.py copies this file next to scene.js and
// loads both into a generated index.html, with window.BEATS (each beat's start, end, chapter and
// word times) written before it. Positions are stage pixels: 1920x1080, origin top left.
(function () {
  const C = {
    bg: "#ffffff", ink: "#2c3539", blue: "#003057", sky: "#5b8fa3", green: "#00a758",
    red: "#c8102e", gray: "#707b7c", rule: "#d3d6d8", tint: "#f4f5f6",
  };
  const EDGE = { plain: C.gray, main: C.blue, new: C.green, risk: C.red };
  const FILL = { plain: C.bg, main: C.blue, new: "#eaf6ef", risk: "#fbeef0" };
  const TEXT = { plain: C.blue, main: "#ffffff", new: C.blue, risk: C.red };
  const LEAD = 0.15;   // s: a picture starts this far ahead of its word, so it is moving as it is heard
  const OUTRO = 0.3;   // s: a chapter's pictures fade out over its last 0.3 s, so the cut is soft
  const SETTLE = "back.out(1.6)"; // boxes, bars, screenshots: a visible overshoot that settles
  const SNAP = "back.out(1.2)";   // small things: tags, labels, numbers
  const GLIDE = "power2.inOut";   // camera, morphs, swaps: no overshoot, so orientation is kept
  const NS = "http://www.w3.org/2000/svg";

  const tl = gsap.timeline({ paused: true });
  const scenes = {};
  let cur = null; // { id, beat, cam, layer }
  const norm = (w) => w.toLowerCase().replace(/[^a-z0-9]/g, "");

  // ---- cues -------------------------------------------------------------------------------
  // Time the voice reaches `word` (its nth saying) in the current beat, minus LEAD.
  function at(word, nth = 1) {
    let seen = 0;
    for (const [w, s] of cur.beat.words) if (w === norm(word) && ++seen === nth) return Math.max(0, s - LEAD);
    const said = cur.beat.words.map((w) => w[0]).join(" ");
    throw new Error(`beat ${cur.id}: cue "${word}" (nth ${nth}) is not said; words: ${said}`);
  }
  const start = () => cur.beat.start;
  const end = () => cur.beat.end;

  // ---- things on stage --------------------------------------------------------------------
  function el(tag, cls, css, parent) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    Object.assign(e.style, css || {});
    (parent || cur.cam).appendChild(e);
    return e;
  }
  // Every placed thing carries its box (cx, cy, w, h), which arrows, look and morph read.
  // defineProperty, not assignment: an SVG circle's own cx and cy are read-only getters.
  function box(e, cx, cy, w, h) {
    for (const [k, v] of Object.entries({ cx, cy, w, h })) Object.defineProperty(e, k, { value: v, writable: true, configurable: true });
    return e;
  }

  // A box centred on (x, y). kind: plain | main | new | risk.
  function node(text, x, y, { w = 300, h = 110, kind = "plain", size = 40 } = {}) {
    const e = el("div", "k-node", {
      left: `${x - w / 2}px`, top: `${y - h / 2}px`, width: `${w}px`, height: `${h}px`,
      borderColor: EDGE[kind], background: FILL[kind], color: TEXT[kind], fontSize: `${size}px`,
    });
    e.textContent = text;
    return box(e, x, y, w, h);
  }
  // Free text. align "center" centres it on (x, y); "left" starts it there.
  function label(text, x, y, { size = 34, color = C.ink, weight = 400, align = "center" } = {}) {
    const e = el("div", "k-label", { left: `${x}px`, top: `${y}px`, fontSize: `${size}px`, color, fontWeight: weight });
    e.textContent = text;
    gsap.set(e, { xPercent: align === "center" ? -50 : 0, yPercent: -50 }); // GSAP owns transforms
    return box(e, x, y, 0, size);
  }
  function tag(text, x, y, kind = "new", size = 32) {
    const e = el("div", "k-tag", { left: `${x}px`, top: `${y}px`, fontSize: `${size}px`, color: EDGE[kind],
      background: FILL[kind], borderColor: EDGE[kind] });
    e.textContent = text;
    gsap.set(e, { xPercent: -50, yPercent: -50 });
    return box(e, x, y, 0, size);
  }
  // A screenshot from the output folder's screens/, `w` px wide, centred on (x, y).
  // h is the picture's height at that width; pass it so arrows and focus boxes can use it.
  function screen(path, x, y, { w = 1100, h = 690 } = {}) {
    const e = el("div", "k-screen", { left: `${x - w / 2}px`, top: `${y - h / 2}px`, width: `${w}px`, height: `${h}px` });
    const img = el("img", "", { width: "100%", height: "100%", objectFit: "contain" }, e);
    img.src = `assets/${path}`;
    return box(e, x, y, w, h);
  }
  // A box around a region of a screenshot, in the screenshot's own pixels at its placed size.
  function focus(shot, x, y, w, h, kind = "new") {
    const e = el("div", "k-focus", { left: `${shot.cx - shot.w / 2 + x}px`, top: `${shot.cy - shot.h / 2 + y}px`,
      width: `${w}px`, height: `${h}px`, borderColor: EDGE[kind] });
    return box(e, shot.cx - shot.w / 2 + x + w / 2, shot.cy - shot.h / 2 + y + h / 2, w, h);
  }
  // A code block; lines keep their spaces. Keep it to a few lines that carry the point.
  function code(snippet, x, y, { size = 30, w = 1100 } = {}) {
    const e = el("pre", "k-code", { left: `${x - w / 2}px`, top: `${y}px`, width: `${w}px`, fontSize: `${size}px` });
    e.textContent = snippet.replace(/^\n+|\s+$/g, "");
    gsap.set(e, { yPercent: -50 });
    return box(e, x, y, w, 0);
  }

  // ---- lines ------------------------------------------------------------------------------
  function layer() {
    if (cur.layer) return cur.layer;
    const s = document.createElementNS(NS, "svg");
    s.setAttribute("class", "k-layer");
    s.setAttribute("viewBox", "0 0 1920 1080");
    cur.cam.prepend(s); // under the boxes, so a line never crosses a label
    return (cur.layer = s);
  }
  function shape(tagName, attrs) {
    const e = document.createElementNS(NS, tagName);
    for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
    layer().appendChild(e);
    return e;
  }
  // Arrow from the edge of a to the edge of b facing it; a point is { cx, cy, w: 0, h: 0 }.
  // Its head is a separate triangle that arrives as the line reaches it.
  function arrow(a, b, kind = "plain", { gap = 10, width = 5 } = {}) {
    const dx = b.cx - a.cx, dy = b.cy - a.cy;
    const side = (n, sx, sy) => Math.abs(dx) * (n.h || 1) >= Math.abs(dy) * (n.w || 1)
      ? [n.cx + sx * (n.w / 2 + gap), n.cy] : [n.cx, n.cy + sy * (n.h / 2 + gap)];
    const [x1, y1] = side(a, Math.sign(dx), Math.sign(dy));
    const [x2, y2] = side(b, -Math.sign(dx), -Math.sign(dy));
    const len = Math.hypot(x2 - x1, y2 - y1) || 1, ux = (x2 - x1) / len, uy = (y2 - y1) / len;
    const hl = 22, hw = 12, bx = x2 - ux * hl, by = y2 - uy * hl; // head length and half width, px
    const line = shape("path", { d: `M${x1},${y1} L${bx + ux * 2},${by + uy * 2}`, stroke: EDGE[kind],
      "stroke-width": width, fill: "none", pathLength: 1, "stroke-dasharray": "1 1", "stroke-dashoffset": 1 });
    line.head = shape("polygon", { points: `${x2},${y2} ${bx - uy * hw},${by + ux * hw} ${bx + uy * hw},${by - ux * hw}`,
      fill: EDGE[kind], opacity: 0 });
    line.full = `M${x1},${y1} L${x2},${y2}`;
    return line;
  }
  // A path you draw yourself, such as a brace or a curve: d in stage pixels.
  function path(d, kind = "main", width = 5) {
    return shape("path", { d, stroke: EDGE[kind], "stroke-width": width, fill: "none", pathLength: 1,
      "stroke-dasharray": "1 1", "stroke-dashoffset": 1 });
  }
  function circle(x, y, r, { kind = "main", fill = "none", width = 6 } = {}) {
    return box(shape("circle", { cx: x, cy: y, r, fill, stroke: fill === "none" ? EDGE[kind] : "none",
      "stroke-width": width, opacity: 0 }), x, y, 2 * r, 2 * r);
  }
  function bar(x, y, w, h, kind = "new") {
    const e = shape("rect", { x, y: y - h / 2, width: 0, height: h, fill: kind === "plain" ? C.gray : EDGE[kind] });
    e.full = w;
    return box(e, x + w / 2, y, w, h);
  }

  // Seeded random, so every render draws the same scatter.
  function rng(seed) {
    return () => { seed |= 0; seed = (seed + 0x6d2b79f5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  }

  // ---- motion: each places tweens at absolute time t (from at()) -------------------------
  const grow = (e, t, d = 0.6) => tl.fromTo(e, { scale: 0, opacity: 0, transformOrigin: "50% 50%" }, { scale: 1, opacity: 1, duration: d, ease: SETTLE }, t);
  const pop = (e, t, d = 0.45) => tl.fromTo(e, { scale: 0.4, opacity: 0, transformOrigin: "50% 50%" }, { scale: 1, opacity: 1, duration: d, ease: SNAP }, t);
  // Slide in from a side ("up", "down", "left", "right") by 40 px.
  function enter(e, t, from = "down", d = 0.6) {
    const v = { up: [0, -40], down: [0, 40], left: [-40, 0], right: [40, 0] }[from];
    return tl.fromTo(e, { opacity: 0, x: v[0], y: v[1] }, { opacity: 1, x: 0, y: 0, duration: d, ease: "power3.out" }, t);
  }
  function draw(line, t, d = 0.5) {
    tl.to(line, { attr: { "stroke-dashoffset": 0 }, duration: d, ease: "power2.out" }, t);
    if (line.head) tl.to(line.head, { opacity: 1, duration: 0.15 }, t + d * 0.6);
  }
  const fill = (b, t, d = 0.8, ease = SETTLE) => { tl.set(b, { opacity: 1 }, t); tl.to(b, { attr: { width: b.full }, duration: d, ease }, t); };
  const fade = (e, t, d = 0.35) => tl.to(e, { opacity: 0, duration: d, ease: "power1.in" }, t);
  const dim = (e, t, o = 0.3, d = 0.6) => tl.to(e, { opacity: o, duration: d, ease: GLIDE }, t);
  const show = (e, t, d = 0.6) => tl.to(e, { opacity: 1, duration: d, ease: GLIDE }, t);
  const indicate = (e, t, color = C.sky) => tl.to(e, { scale: 1.08, borderColor: color, duration: 0.3, yoyo: true, repeat: 1, ease: "power2.inOut" }, t);
  // A pulse runs along each arrow in turn: a request or data moving.
  function flow(lines, t, d = 1.2) {
    const ps = lines.map((l) => shape("path", { d: l.full || l.getAttribute("d"), stroke: C.sky, "stroke-width": 10, fill: "none",
      "stroke-linecap": "round", pathLength: 1, "stroke-dasharray": "0.12 1.2", "stroke-dashoffset": 0.12, opacity: 0 }));
    const step = d / ps.length;
    ps.forEach((p, i) => {
      tl.set(p, { opacity: 1 }, t + i * step);
      tl.fromTo(p, { attr: { "stroke-dashoffset": 0.12 } }, { attr: { "stroke-dashoffset": -1.1 }, duration: step * 1.6, ease: "none" }, t + i * step);
      tl.set(p, { opacity: 0 }, t + i * step + step * 1.6);
    });
  }
  // The same thing in a new state: a glides onto b's box and hands over to it.
  function morph(a, b, t, d = 0.8) {
    tl.to(a, { x: b.cx - a.cx, y: b.cy - a.cy, scale: Math.min(b.w / (a.w || b.w), 1.4), opacity: 0, duration: d, ease: GLIDE }, t);
    tl.fromTo(b, { opacity: 0, scale: 0.9 }, { opacity: 1, scale: 1, duration: d * 0.7, ease: GLIDE }, t + d * 0.3);
  }
  // Before/after on one spot: the after pushes the before out to the left.
  function swap(before, after, t, d = 0.8) {
    tl.to(before, { x: -260, opacity: 0, duration: d, ease: GLIDE }, t);
    tl.fromTo(after, { x: 260, opacity: 0 }, { x: 0, opacity: 1, duration: d, ease: GLIDE }, t);
  }
  // Count a number up while its bar or line moves; the text is a function of timeline time.
  function count(e, t, to, d, fmt = (v) => Math.round(v).toLocaleString("en-US"), from = 0) {
    const o = { v: from };
    e.textContent = fmt(from);
    tl.to(e, { opacity: 1, duration: 0.25, ease: "power1.out" }, t); // a fade, so the label never pops in
    tl.to(o, { v: to, duration: d, ease: "none", onUpdate: () => (e.textContent = fmt(o.v)) }, t);
  }
  // Camera: centre (x, y) at zoom z. home() returns to the full stage.
  const look = (x, y, z, t, d = 1.0) => tl.to(cur.cam, { x: (960 - x) * z, y: (540 - y) * z, scale: z, duration: d, ease: GLIDE }, t);
  const home = (t, d = 1.0) => tl.to(cur.cam, { x: 0, y: 0, scale: 1, duration: d, ease: GLIDE }, t);

  // ---- running the scene ------------------------------------------------------------------
  function beat(id, fn) { scenes[id] = fn; }

  function captions() {
    // A captioned video shows each sentence of the narration while it is read.
    const host = document.getElementById("captions");
    if (!host || !window.BEATS_CAPTIONED) return;
    const line = el("div", "k-caption", {}, host);
    for (const [id, b] of Object.entries(window.BEATS)) {
      for (const s of b.sentences) {
        // The old line fades out before the new one fades in, so a swap is never a one-frame jump.
        if (s.start > 0.2) tl.to(line, { opacity: 0, duration: 0.15, ease: "power1.in" }, s.start - 0.15);
        tl.call(() => (line.textContent = s.text), null, s.start);
        tl.fromTo(line, { opacity: 0 }, { opacity: 1, duration: 0.2, immediateRender: false }, s.start);
      }
    }
  }

  function run() {
    const ids = Object.keys(window.BEATS);
    const missing = ids.filter((id) => !scenes[id]);
    if (missing.length) throw new Error(`scene.js has no beat() for: ${missing.join(", ")}`);
    const extra = Object.keys(scenes).filter((id) => !window.BEATS[id]);
    if (extra.length) throw new Error(`scene.js has beat() for ids not in script.json: ${extra.join(", ")}`);
    let chapter = null;
    ids.forEach((id, n) => {
      const b = window.BEATS[id];
      if (b.chapter !== chapter) {
        if (chapter) tl.to(cur.cam, { opacity: 0, duration: OUTRO, ease: "power1.in" }, b.start - OUTRO);
        chapter = b.chapter;
        cur = { cam: document.getElementById(`ch-${chapter}`).firstElementChild, layer: null };
      }
      cur.id = id;
      cur.beat = b;
      scenes[id]({ at, start, end });
    });
    captions();
    tl.seek(0);
    return tl; // index.html registers it as window.__timelines["main"]
  }

  window.K = {
    C, tl, beat, run, at, start, end, node, label, tag, screen, focus, code, arrow, path, circle, bar, rng,
    grow, pop, enter, draw, fill, fade, dim, show, indicate, flow, morph, swap, count, look, home, SETTLE, SNAP, GLIDE,
  };
})();
