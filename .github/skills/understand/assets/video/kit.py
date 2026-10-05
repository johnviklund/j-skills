"""understand video kit: the palette, building blocks, motion and beat timing for an explainer video.

Copied next to scene.py by the understand skill; build-video.py renders scene.py with Manim
Community Edition. Uses Text only, never Tex or MathTex, so no LaTeX install is needed.

A scene subclasses Kit and defines one method per beat in script.json: beat id `hook` runs
`beat_hook`. Kit.construct calls them in script order and pads each beat to its narration.
Inside a beat, `self.at("word")` waits until the voice reaches that word, so each picture lands
on the word that names it instead of all at the start of the sentence.
"""
import json
import math
import os
import pathlib
import re
import textwrap

from manim import (DOWN, LEFT, ORIGIN, RIGHT, UP, Arrow, Code, FadeIn, FadeOut, Group,
                   GrowFromCenter, ImageMobject, LaggedStart, Line, MovingCameraScene, Rectangle,
                   ReplacementTransform, RoundedRectangle, ShowPassingFlash, Text, ValueTracker,
                   VGroup, Write, config, smooth)

# The explainer page's palette and diagram styles (assets/explainer.html :root and svg.diagram),
# so the video reads as part of the page: white ground, navy structure, iron text.
BG = "#ffffff"
INK = "#2c3539"     # iron: text
BLUE = "#003057"    # structure and the main path
SKY = "#5b8fa3"     # a pulse moving along an arrow
GREEN = "#00a758"   # new or better
RED = "#c8102e"     # risk or an unrequested change
GRAY = "#707b7c"    # secondary
RULE = "#d3d6d8"    # frames and muted lines
TINT = "#f4f5f6"    # card backgrounds
KIND = {"plain": BLUE, "main": BLUE, "new": GREEN, "risk": RED}
FILL = {"plain": BG, "main": BLUE, "new": "#eaf6ef", "risk": "#fbeef0"}
EDGE = {"plain": GRAY, "main": BLUE, "new": GREEN, "risk": RED}
FONT = "Arial"      # the page's font; fontconfig maps it to Liberation Sans where Arial is absent

LEAD = 0.15         # s: a picture starts this far ahead of its word, so it is moving as it is heard
LATE = 0.5          # s: a cue reached later than this is reported; the eye notices the lag
MIN_VIEW = 6.0      # frame width at the tightest zoom: 2.4x, where 24 px labels stay crisp at 1080p
CAPTION_BAND = 0.2  # bottom fifth of the frame is the caption band in a captioned video

VIDEO_DIR = pathlib.Path(os.environ.get("UNDERSTAND_VIDEO_DIR", "."))
BUILD_DIR = pathlib.Path(os.environ.get("UNDERSTAND_BUILD_DIR", "."))


# Motion. One curve per class of object, so weight reads the same across the film.
def spring(zeta, omega):
    """A damped spring as a rate function: zeta below 1 overshoots, omega sets how fast it settles.
    Pinned to exactly 1 at t=1 so the object ends where it was sent."""
    wd = omega * math.sqrt(1 - zeta ** 2)

    def raw(t):
        return 1 - math.exp(-zeta * omega * t) * (math.cos(wd * t) + zeta * omega / wd * math.sin(wd * t))
    end = raw(1)
    return lambda t: raw(t) + t * (1 - end)


# omega 8 keeps a 0.3 s pop under a quarter of the way after its first frame at 30 fps, so it
# reads as growing; omega 14 jumped half way in one frame and the motion check flagged it as a pop.
SNAP = spring(0.8, 8)     # small things (tags, dots, numbers): quick, ~1% overshoot
SETTLE = spring(0.6, 8)   # boxes, bars and panels: a visible ~9% overshoot that settles
GLIDE = smooth            # the camera and morphs: no overshoot, so orientation is kept


def label(text, size=30, color=INK, weight="NORMAL"):
    return Text(text, font=FONT, font_size=size, color=color, weight=weight)


def node(text, kind="plain", width=2.6, height=1.0):
    """A box with a short label: plain, main (filled navy), new (green) or risk (red)."""
    box = RoundedRectangle(corner_radius=0.06, width=width, height=height, color=KIND[kind],
                           stroke_width=3)
    box.set_fill(FILL[kind], opacity=1)
    ink = BG if kind == "main" else INK
    return VGroup(box, label(text, size=24, color=ink, weight="BOLD").move_to(box))


def row(*nodes, gap=0.9):
    """Nodes left to right, centred on screen."""
    return VGroup(*nodes).arrange(RIGHT, buff=gap)


def column(*nodes, gap=0.6):
    return VGroup(*nodes).arrange(DOWN, buff=gap)


def arrow(a, b, kind="plain"):
    """Edge from box a to box b, picking the facing sides."""
    color = EDGE[kind]
    return Arrow(a.get_critical_point(_side(a, b)), b.get_critical_point(_side(b, a)),
                 buff=0.08, color=color, stroke_width=4 if kind == "main" else 3,
                 max_tip_length_to_length_ratio=0.15)


def _side(a, b):
    dx, dy = (b.get_center() - a.get_center())[:2]
    return (RIGHT if dx > 0 else LEFT) if abs(dx) >= abs(dy) else (UP if dy > 0 else DOWN)


def flow(*arrows, color=SKY):
    """A pulse travelling along the arrows in order: data or a request moving."""
    return LaggedStart(*(ShowPassingFlash(a.copy().set_color(color).set_stroke(width=8),
                                          time_width=0.5) for a in arrows), lag_ratio=0.6)


def pop(*mobjects, lag=0.12):
    """Things spring up from nothing, one after another: the default entrance for small parts."""
    return LaggedStart(*(GrowFromCenter(m, rate_func=SNAP) for m in mobjects), lag_ratio=lag)


def counter(value=0, decimals=0, suffix="", size=40, color=BLUE, weight="BOLD"):
    """A number that counts when its tracker moves: self.play(n.tracker.animate.set_value(80))."""
    tracker = ValueTracker(value)

    def text():
        return f"{tracker.get_value():.{decimals}f}{suffix}"

    def make(t):
        return label(t, size=size, color=color, weight=weight)
    num = make(text())
    num.shown, num.natural = text(), num.height

    def update(m):
        # Rebuild only when the digits change, at the size the number has now, so a pop or a
        # scale on the counter is kept rather than reset to full size every frame.
        t = text()
        if t == m.shown:
            return
        new = make(t)
        natural = new.height
        new.scale(m.height / m.natural if m.natural else 1).move_to(m.get_center())
        m.become(new)
        m.shown, m.natural = t, natural
    num.add_updater(update)
    num.tracker = tracker
    return num


def screen(path, height=5.6):
    """A screenshot from the output folder, with a thin frame. Path is relative to that folder."""
    img = ImageMobject(str(VIDEO_DIR.parent / path)).set_height(height)
    frame = Rectangle(width=img.width, height=img.height, color=RULE, stroke_width=2).move_to(img)
    return Group(img, frame)


def focus(shot, x, y, w, h, kind="new"):
    """A box on a screenshot at fractions of its size: x, y from the top-left corner."""
    img = shot[0]
    left, top = img.get_corner(LEFT + UP)[:2]
    rect = Rectangle(width=w * img.width, height=h * img.height, color=KIND[kind], stroke_width=5)
    return rect.move_to([left + (x + w / 2) * img.width, top - (y + h / 2) * img.height, 0])


def tag(text, kind="new"):
    """A small coloured tag, e.g. NEW or UNREQUESTED, to place next to a screenshot."""
    t = label(text.upper(), size=20, color=BG, weight="BOLD")
    pill = RoundedRectangle(corner_radius=0.1, width=t.width + 0.4, height=t.height + 0.25,
                            color=KIND[kind]).set_fill(KIND[kind], opacity=1)
    return VGroup(pill, t.move_to(pill))


def code(snippet, language="python", size=28):
    """A code card. Keep it to the few lines the narration names."""
    return Code(code_string=textwrap.dedent(snippet).strip("\n"), language=language,
                formatter_style="friendly", add_line_numbers=False,
                paragraph_config={"font_size": size, "font": "Monospace"},
                background="rectangle", background_config={"fill_color": TINT,
                                                           "stroke_color": RULE})


def _norm(word):
    return re.sub(r"[^\w'-]", "", word.lower()).strip("-'")


class Kit(MovingCameraScene):
    def setup(self):
        self.camera.background_color = BG
        self.script = json.loads((VIDEO_DIR / "script.json").read_text())
        timing_file = BUILD_DIR / "timings.json"
        self.timings = json.loads(timing_file.read_text()) if timing_file.exists() else {}
        self.captioned = not self.timings.get("voiced", False)

    # Timing ---------------------------------------------------------------------------------
    def _cue_time(self, cue, nth):
        toks = [_norm(w) for w in cue.split()]
        words = self._words
        hits = [i for i in range(len(words) - len(toks) + 1)
                if [w[0] for w in words[i:i + len(toks)]] == toks]
        if len(hits) < nth:
            have = " ".join(w[0] for w in words) or "(no word timings; run through build-video.py)"
            raise SystemExit(f"beat '{self._beat}': cue '{cue}' (#{nth}) not in its narration. "
                             f"Words: {have}")
        return self._beat_start + words[hits[nth - 1]][1] - LEAD

    def _cue_count(self, cue):
        toks = [_norm(w) for w in cue.split()]
        words = [w[0] for w in self._words]
        return sum(words[i:i + len(toks)] == toks for i in range(len(words) - len(toks) + 1))

    def until(self, cue, nth=1):
        """Seconds from now until the narration reaches `cue`: a run_time that makes a slow
        change (a bar filling, a camera pan) land exactly on the word."""
        return max(self._cue_time(cue, nth) - self.renderer.time, 0.3)

    def at(self, cue, nth=1):
        """Wait until the narration reaches `cue` (a word or phrase of this beat's `say`), so the
        next play() lands on it. Raises with the beat's words when the cue is not in them."""
        gap = self._cue_time(cue, nth) - self.renderer.time
        if gap > 0.02:
            self.wait(gap)
        elif gap < -LATE:
            again = self._cue_count(cue) > nth
            self._late.append(f"'{cue}' {-gap:.1f} s late" +
                              (f"; it is said again later, maybe nth={nth + 1}" if again else ""))

    # Camera ---------------------------------------------------------------------------------
    def look(self, *mobjects, margin=1.3, run_time=1.2, animate=True):
        """Move the camera to fill the frame with these mobjects. Returns the animation when
        animate is False, to play beside another."""
        g = Group(*mobjects)
        aspect = config.frame_width / config.frame_height
        width = min(max(g.width * margin, g.height * margin * aspect, MIN_VIEW), config.frame_width * 1.4)
        centre = g.get_center()
        if self.captioned:  # keep the subject in the part of the frame above the caption band
            centre = centre + DOWN * (width / aspect) * CAPTION_BAND / 2
        anim = self.camera.frame.animate(rate_func=GLIDE, run_time=run_time).set(width=width).move_to(centre)
        return self.play(anim) if animate else anim

    def home(self, animate=False):
        """The camera back to the full frame."""
        anim = self.camera.frame.animate(rate_func=GLIDE).set(width=config.frame_width).move_to(ORIGIN)
        return self.play(anim) if animate else anim

    # Continuity -----------------------------------------------------------------------------
    def morph(self, a, b, run_time=1.0):
        """a becomes b: the same thing in a new state or role. The default way into a new idea."""
        self.play(ReplacementTransform(a, b, rate_func=GLIDE), run_time=run_time)
        return b

    def clear(self, *keep):
        """Clear the stage except `keep`, and bring the camera home. For a new chapter only:
        a carried object (morph, keep) tells the viewer how the ideas connect."""
        stage = [m for m in self.mobjects
                 if m not in self.foreground_mobjects and m not in keep and m is not self.camera.frame]
        anims = [FadeOut(m) for m in stage] + [self.home()]
        self.play(*anims, run_time=0.6)

    def title(self, text, sub=None):
        """Opening card: the question the video answers."""
        t = label(text, size=48, color=BLUE, weight="BOLD")
        group = VGroup(t, label(sub, size=28, color=GRAY)).arrange(DOWN, buff=0.4) if sub else t
        self.play(Write(t))
        if sub:
            self.play(FadeIn(group[1], shift=UP * 0.2))
        return group

    def swap(self, before, after):
        """The before/after moment on a screenshot: the after pushes the before out sideways, so
        the viewer sees one replace the other rather than a blend of both."""
        after.move_to(before).shift(RIGHT * config.frame_width * 1.4)
        self.add(after)
        self.play(before.animate(rate_func=SETTLE).shift(LEFT * config.frame_width * 1.4),
                  after.animate(rate_func=SETTLE).move_to(before.get_center()), run_time=1.0)
        self.remove(before)

    # Driver ---------------------------------------------------------------------------------
    def construct(self):
        beats, spans = self.script["beats"], []
        for beat in beats:
            name = "beat_" + beat["id"].replace("-", "_")
            method = getattr(self, name, None)
            if method is None:
                have = ", ".join(m for m in dir(self) if m.startswith("beat_")) or "none"
                raise SystemExit(f"scene.py has no {name}() for beat '{beat['id']}' "
                                 f"in script.json; beat methods defined: {have}")
            info = self.timings.get("beats", {}).get(beat["id"], {})
            self._beat, self._late = beat["id"], []
            self._words = [(_norm(w), s) for w, s, _ in info.get("words", []) if _norm(w)]
            self._beat_start = start = self.renderer.time
            caption = self._caption(beat["say"]) if self.captioned else None
            method()
            left = info.get("seconds", 0) - (self.renderer.time - start)
            if left > 0.05:
                self.wait(left)
            if caption is not None:
                self.remove(caption)
            spans.append({"id": beat["id"], "start": start, "end": self.renderer.time,
                          "late": self._late})
        (BUILD_DIR / "beats.json").write_text(json.dumps(spans, indent=1))

    def _caption(self, text):
        """Captioned videos carry their narration on screen, at the bottom of the camera's frame
        wherever the camera goes."""
        lines = textwrap.wrap(text, 62)
        cap = VGroup(*(label(line, size=26) for line in lines)).arrange(DOWN, buff=0.12)
        cap.to_edge(DOWN, buff=0.6)  # above a web player's control bar
        back = Rectangle(width=config.frame_width, height=cap.height + 0.4, stroke_width=0)
        back.set_fill(BG, opacity=0.92).move_to(cap)
        template = VGroup(back, Line(back.get_corner(UP + LEFT), back.get_corner(UP + RIGHT),
                                     color=RULE, stroke_width=1.5), cap)
        frame = self.camera.frame

        def pin(m):
            m.become(template.copy().scale(frame.width / config.frame_width, about_point=ORIGIN)
                     .shift(frame.get_center()))
        group = template.copy()
        pin(group)  # place it now: a beat that opens with a wait would show it off-frame
        group.add_updater(pin)
        self.add_foreground_mobject(group)
        return group

    def remove(self, *mobjects):
        for m in mobjects:
            if m in self.foreground_mobjects:
                self.remove_foreground_mobject(m)
        return super().remove(*mobjects)


__all__ = ["Kit", "label", "node", "row", "column", "arrow", "flow", "pop", "counter", "screen",
           "focus", "tag", "code", "spring", "SNAP", "SETTLE", "GLIDE", "BG", "INK", "BLUE", "SKY",
           "GREEN", "RED", "GRAY", "RULE", "TINT"]
