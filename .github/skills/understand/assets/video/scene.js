// Explainer video scene: one beat("id", ...) per beat in script.json, in the same order.
// Replace the example beats below. Each beat places its pictures on the timeline at the words
// that name them: at("word") is the time the voice reaches that word. Keep things on S to carry
// them into later beats of the same chapter. Kit reference: the header of each section of kit.js.
// Build with: python3 SKILL/scripts/build-video.py OUTPUT/video --draft
const { C, beat, node, label, tag, screen, focus, code, arrow, path, circle, bar, rng,
  grow, pop, enter, draw, fill, fade, dim, show, indicate, flow, morph, swap, count, look, home } = K;
const S = {};

beat("hook", ({ at, start }) => {
  // Open on a concrete moment, not a title card.
  S.letter = label("a|", 960, 400, { size: 96, weight: 700 });
  pop(S.letter, start());
  S.wait = label("0.0 s", 960, 540, { size: 72, color: C.red, weight: 700 });
  const t = at("freezes");
  count(S.wait, t, 2.0, at("seconds") - t, (v) => `${v.toFixed(1)} s`);
});

beat("parts", ({ at }) => {
  S.ui = node("Editor", 480, 400);
  S.api = node("Save API", 960, 400, { kind: "main" });
  S.db = node("Database", 1440, 400);
  S.edges = [arrow(S.ui, S.api, "main"), arrow(S.api, S.db)];
  const t = at("three");
  fade(S.letter, t);
  K.tl.to(S.wait, { x: 480 - 960, y: 520 - 540, scale: 0.5, duration: 0.8, ease: K.GLIDE }, t);
  grow(S.ui, t + 0.2);
  indicate(S.wait, at("save"), C.red);
  grow(S.api, at("api"));
  draw(S.edges[0], at("api") + 0.1);
  grow(S.db, at("database"));
  draw(S.edges[1], at("database") + 0.1);
});

beat("flow", ({ at }) => {
  S.doc = tag("whole doc", 480, 290, "plain", 28);
  pop(S.doc, at("whole"));
  look(960, 380, 1.3, at("whole"));
  const t = at("through");
  flow(S.edges, t, at("database") - t);
  K.tl.to(S.doc, { x: 960, duration: at("database") - t, ease: K.GLIDE }, t);
});

beat("change", ({ at }) => {
  const cache = node("Cache", 960, 640, { kind: "new" });
  grow(cache, at("cache"));
  draw(arrow(S.api, cache, "new"), at("cache") + 0.1);
  home(at("cache"));
  S.line = tag("edited lines", 1440, 290, "new", 28);
  morph(S.doc, S.line, at("edited"));
});

beat("close", ({ at }) => {
  K.tl.to(S.wait, { x: -480, y: -300, scale: 1, duration: 0.8, ease: K.GLIDE }, at("one")); // above the editor
  count(S.wait, at("gone"), 0.1, 0.8, (v) => `${v.toFixed(1)} s`, 2.0);
});
