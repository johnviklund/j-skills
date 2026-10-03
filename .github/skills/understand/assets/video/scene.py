"""Explainer video scene: one beat_<id> method per beat in script.json, in the same order.

Replace the example beats below. Each method animates only; Kit pads it to its narration.
Build with: python3 <skill>/scripts/build-video.py <output folder>/video
"""
from manim import *  # noqa: F401,F403  Manim's animations: Create, Transform, Indicate, ...
from kit import *    # noqa: F401,F403  palette and building blocks, see kit.py


class Explainer(Kit):
    def beat_hook(self):
        # Open on the question, not the answer.
        self.title("Why did saving get slow?", sub="and what changed to fix it")

    def beat_parts(self):
        self.clear()
        self.ui, self.api, self.db = node("Editor"), node("Save API", "main"), node("Database")
        self.parts = row(self.ui, self.api, self.db).shift(UP * 1.2)  # clear of the caption band
        self.edges = [arrow(self.ui, self.api, "main"), arrow(self.api, self.db)]
        self.play(LaggedStart(*(FadeIn(n, shift=UP * 0.2) for n in self.parts), lag_ratio=0.3))
        self.play(*(Create(e) for e in self.edges))

    def beat_flow(self):
        self.play(flow(*self.edges))
        self.play(Indicate(self.api, color=BLUE))

    def beat_change(self):
        cache = node("Cache", "new").next_to(self.api, DOWN, buff=1.0)
        self.play(GrowFromCenter(cache), Create(arrow(self.api, cache, "main")))

    def beat_screens(self):
        # Before/after: self.screen paths are relative to the output folder.
        # before, after = screen("screens/save-before.jpg"), screen("screens/save-after.jpg")
        # self.play(FadeIn(before)); self.swap(before, after)
        # self.play(Create(focus(after, 0.62, 0.08, 0.3, 0.12, "new")))
        self.clear()
        self.play(Write(label("Saving now takes one round trip.", size=40, color=GREEN)))
