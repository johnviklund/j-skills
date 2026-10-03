"""understand video kit: the palette, building blocks and beat timing for an explainer video.

Copied next to scene.py by the understand skill; build-video.py renders scene.py with Manim
Community Edition. Uses Text only, never Tex or MathTex, so no LaTeX install is needed.

A scene subclasses Kit and defines one method per beat in script.json: beat id `hook` runs
`beat_hook`. Kit.construct calls them in script order and pads each beat to its narration, so a
beat method only animates; it never waits for the voice.
"""
import json
import os
import pathlib
import textwrap

from manim import (DOWN, LEFT, RIGHT, UP, Arrow, Code, FadeIn, FadeOut, Group, ImageMobject,
                   LaggedStart, Line, Rectangle, RoundedRectangle, Scene, ShowPassingFlash, Text, VGroup,
                   Write, config)

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

VIDEO_DIR = pathlib.Path(os.environ.get("UNDERSTAND_VIDEO_DIR", "."))
BUILD_DIR = pathlib.Path(os.environ.get("UNDERSTAND_BUILD_DIR", "."))


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


class Kit(Scene):
    def setup(self):
        self.camera.background_color = BG
        self.script = json.loads((VIDEO_DIR / "script.json").read_text())
        timing_file = BUILD_DIR / "timings.json"
        self.timings = json.loads(timing_file.read_text()) if timing_file.exists() else {}

    def title(self, text, sub=None):
        """Opening card: the question the video answers."""
        t = label(text, size=48, color=BLUE, weight="BOLD")
        group = VGroup(t, label(sub, size=28, color=GRAY)).arrange(DOWN, buff=0.4) if sub else t
        self.play(Write(t))
        if sub:
            self.play(FadeIn(group[1], shift=UP * 0.2))
        return group

    def swap(self, before, after):
        """Cross-fade one screenshot into another in place: the before/after moment."""
        after.move_to(before)
        self.play(FadeOut(before), FadeIn(after), run_time=1.2)

    def clear(self):
        """Fade everything out to start the next idea on an empty stage."""
        stage = [m for m in self.mobjects if m not in self.foreground_mobjects]
        if stage:
            self.play(*(FadeOut(m) for m in stage), run_time=0.6)

    def construct(self):
        voiced = self.timings.get("voiced", False)
        beats, spans = self.script["beats"], []
        for beat in beats:
            name = "beat_" + beat["id"].replace("-", "_")
            method = getattr(self, name, None)
            if method is None:
                have = ", ".join(m for m in dir(self) if m.startswith("beat_")) or "none"
                raise SystemExit(f"scene.py has no {name}() for beat '{beat['id']}' "
                                 f"in script.json; beat methods defined: {have}")
            start = self.renderer.time
            caption = None if voiced else self._caption(beat["say"])
            method()
            target = self.timings.get("beats", {}).get(beat["id"], {}).get("seconds", 0)
            left = target - (self.renderer.time - start)
            if left > 0.05:
                self.wait(left)
            if caption is not None:
                self.remove(caption)
            spans.append({"id": beat["id"], "start": start, "end": self.renderer.time})
        (BUILD_DIR / "beats.json").write_text(json.dumps(spans, indent=1))

    def _caption(self, text):
        """Silent videos carry their narration on screen, two short lines at the bottom."""
        lines = textwrap.wrap(text, 62)
        cap = VGroup(*(label(line, size=26) for line in lines)).arrange(DOWN, buff=0.12)
        cap.to_edge(DOWN, buff=0.6)  # above a web player's control bar
        back = Rectangle(width=config.frame_width, height=cap.height + 0.4, stroke_width=0)
        back.set_fill(BG, opacity=0.92).move_to(cap)
        group = VGroup(back, Line(back.get_corner(UP + LEFT), back.get_corner(UP + RIGHT),
                                  color=RULE, stroke_width=1.5), cap)
        self.add_foreground_mobject(group)
        return group

    def remove(self, *mobjects):
        for m in mobjects:
            if m in self.foreground_mobjects:
                self.remove_foreground_mobject(m)
        return super().remove(*mobjects)


__all__ = ["Kit", "label", "node", "row", "column", "arrow", "flow", "screen", "focus", "tag",
           "code", "BG", "INK", "BLUE", "SKY", "GREEN", "RED", "GRAY", "RULE", "TINT"]
