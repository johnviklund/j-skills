"""Explainer video scene: one beat_<id> method per beat in script.json, in the same order.

Replace the example beats below. Each method animates only; Kit pads it to its narration.
Cue each picture to the word that names it with self.at("word"); keep objects on self and carry
them into the next beat. Build with: python3 <skill>/scripts/build-video.py <output folder>/video
"""
from manim import *  # noqa: F401,F403  Manim's animations: Create, Transform, Indicate, ...
from kit import *    # noqa: F401,F403  palette, motion and building blocks, see kit.py


class Explainer(Kit):
    def beat_hook(self):
        # Open on a concrete moment, not a title card.
        self.letter = label("a|", size=72, weight="BOLD")
        self.play(pop(self.letter))
        self.wait_n = counter(0, decimals=1, suffix=" s", size=56, color=RED)
        self.wait_n.next_to(self.letter, DOWN, buff=0.6)
        self.at("freezes")
        self.play(pop(self.wait_n))
        self.play(self.wait_n.tracker.animate.set_value(2.0), run_time=self.until("seconds"),
                  rate_func=linear)

    def beat_parts(self):
        self.ui, self.api, self.db = node("Editor"), node("Save API", "main"), node("Database")
        self.parts = row(self.ui, self.api, self.db).shift(UP * 1.2)  # clear of the caption band
        self.edges = [arrow(self.ui, self.api, "main"), arrow(self.api, self.db)]
        self.at("three")
        self.play(FadeOut(self.letter), self.wait_n.animate.scale(0.5).next_to(self.ui, DOWN),
                  GrowFromCenter(self.ui, rate_func=SETTLE))
        self.at("save")
        self.play(Indicate(self.wait_n, color=RED))
        self.at("api")
        self.play(GrowFromCenter(self.api, rate_func=SETTLE), GrowArrow(self.edges[0]))
        self.at("database")
        self.play(GrowFromCenter(self.db, rate_func=SETTLE), GrowArrow(self.edges[1]))

    def beat_flow(self):
        self.doc = VGroup(*(Rectangle(width=0.5, height=0.65, color=GRAY).set_fill(BG, 1)
                            .shift(0.06 * i * (UP + RIGHT)) for i in range(4)))
        self.doc.next_to(self.ui, UP, buff=0.2)
        self.at("whole")
        self.play(pop(self.doc), self.look(self.parts, self.doc, animate=False))
        self.at("through")
        self.play(flow(*self.edges), self.doc.animate.next_to(self.db, UP, buff=0.2),
                  run_time=self.until("database"))

    def beat_change(self):
        cache = node("Cache", "new").next_to(self.api, DOWN, buff=1.0)
        line = Line(LEFT * 0.25, RIGHT * 0.25, color=GREEN, stroke_width=6).move_to(self.doc)
        self.at("cache")
        self.play(GrowFromCenter(cache, rate_func=SETTLE), GrowArrow(arrow(self.api, cache, "new")),
                  self.home())
        self.at("edited")
        self.morph(self.doc, line, run_time=self.until("travel"))

    def beat_close(self):
        self.at("one")
        self.play(self.wait_n.animate.scale(2).next_to(self.ui, UP, buff=0.6))
        self.at("gone")
        self.play(self.wait_n.tracker.animate.set_value(0.1), run_time=0.8, rate_func=linear)
