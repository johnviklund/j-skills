# understand: the video

Read in step 7 of `SKILL.md`, when the human chose a video in step 2. The video retells the
verified page as a 3Blue1Brown-style animation in the page's own palette: one idea at a time,
shapes that move to show cause and change, each picture landing on the word that names it, and
a calm voice over it. The page stays the source of truth. The video makes no claim the page
does not make, so the page's cites and fidelity pass cover it too.

Everything goes in the output folder's `video/`. `<skill>` is this skill's folder; `<video>` is
that `video/` folder.

## Steps

1. **Script.** Copy `<skill>/assets/video/script.json` to `<video>/`, set `kind` to the story the
   human chose in step 2 (`built` or `feature`), and replace its beats. Done when every beat's
   `say` restates a sentence or figure from the page, every beat has a `show`, and the beats
   read aloud in 45 to 180 seconds: about 110 to 400 words at 150 a minute.
   - A beat is one idea and one picture: 4 to 14 beats. Each `say` is one to three sentences
     under the Rules of `plain`.
   - Follow the arc for the kind; each step is one or more beats:
     - **built**, what a run built: the problem as a user met it; the parts that changed; the
       mechanism moving; each changed screen before then after, unrequested changes named as
       such; what is left open; the one thing to keep, the page's *In short*.
     - **feature**, why, what and how of a feature: one concrete case that shows why it exists;
       what it is, in one picture; how it works, as one diagram that grows beat by beat; a
       worked example with the page's real numbers; its limits; the one thing to keep.
   - **Open on a concrete moment**, a customer, a click, a number, rather than a title card: a
     viewer decides in the first five seconds whether to keep watching, and a moment gives
     them a reason before the name of the thing does.
   - **`show` is the shot list:** what is on screen when the beat ends, and what carries into
     the next beat ("Carries: the axis."). Writing it before the scene makes each picture a
     decision and makes the thread between beats visible; most dull videos are dull because
     every beat starts on an empty stage.
   - Write for the ear. Say what a name does, not its spelling: "the save handler", not
     `handlers/save.ts`. Numbers as people say them: "two seconds".

2. **Scene.** Copy `<skill>/assets/video/scene.py` and `kit.py` to `<video>/`. Write one
   `beat_<id>` method per beat, `-` in an id becoming `_`; the example beats show the kit. Done
   when every beat has a method and each animates what its `show` describes.
   - **Land each picture on its word.** `self.at("towed")` waits until the voice reaches that
     word of the beat's `say`, so a picture arrives as it is named. Cue the noun that names
     the picture ("lost car"), not the number at the end of the phrase; for a change that
     should finish on a word, pass `run_time=self.until("eighty")`, then `pop` the number.
     A word said twice in a beat takes `nth=2`. A picture every two seconds or so keeps
     the eye busy; the build reports any still stretch longer than that.
   - **Carry objects between beats.** Keep objects on `self` and turn one into the next with
     `self.morph(a, b)`, or keep it with `self.clear(keep)`: a dot that becomes a marker on an
     axis tells the viewer how two ideas connect, where a fade to white makes them start
     over. Call `self.clear()` only for a new chapter.
   - **Move the camera to the subject.** `self.look(*mobs)` fills the frame with what the
     sentence is about; `self.home()` returns to the full stage. Both return an animation when
     given `animate=False`, to play beside the change they frame. Set the camera instantly
     only when the stage is empty, right after `clear()`. Dim the boxes outside the shot
     (`set_opacity(0.25)`) so a cropped neighbour reads as context.
   - **Give things weight.** Small parts enter with `pop(...)`; boxes and bars with
     `GrowFromCenter` or `GrowFromEdge(..., rate_func=SETTLE)`, which overshoots a little and
     settles, as real objects do; the camera and morphs use `GLIDE`. Numbers are a
     `counter(...)` that counts as its `tracker` moves; count with `rate_func=linear`, since
     a slow start ticks once after a still frame and reads as a pop. Draw a `NumberLine` with
     `GrowFromEdge(line, LEFT)`, not `Create`, and bring every object in with an animation
     rather than `self.add`: both otherwise appear in one frame, which the build reports as a
     pop.
   - **Motion means something.** A `flow` pulse is data or a request moving; a morph is the same
     thing in a new state; `self.swap(before, after)` is the before/after moment on a
     screenshot, the after pushing the before out, with `focus()` boxing the changed region and
     `tag("unrequested", "risk")` beside it.
   - **Colour keeps the page's meaning:** the kit uses the page's palette and diagram styles,
     navy for structure and the main path, green for new, red for risk or unrequested, gray for
     the rest. Use the kit's names (`BLUE`, `GREEN`, ...), never Manim's own colours. Labels on
     screen stay at three words or fewer; the voice carries the sentences.
   - Screenshots come from the output folder's `screens/`, the same files the page shows:
     `screen("screens/x-after.jpg")`.
   - A captioned video keeps everything above the caption band, the bottom fifth of the frame;
     `look` allows for it.
   - Manim Community Edition API; Text only, never `Tex`, `MathTex` or `DecimalNumber`, so LaTeX
     is not needed.

3. **Draft.** Run `python3 <skill>/scripts/build-video.py <video> --draft`, adding `--silent`
   when the human chose captions. It prints a `motion:` line (share of still frames, holds over
   2 s, pops) and a `WARN` for each hold, pop and late cue, with its time and beat. Open the
   `look:` contact sheet, one still per beat. Done when every still shows its beat's `show`
   whole and legible, nothing overlaps or leaves the frame, and no `WARN` is left.
   - Each pass, name the three worst defects with their timestamps, from the warnings and the
     sheet, fix those three, and rerun. Three at a time keeps each fix checkable; fixing
     everything at once tends to move timing and create new holds.
   - Under about 50% still frames reads as lively; an explainer needs some stillness to read a
     label, so do not chase zero.
   - The voice is cached with its word timings, so a rerun sends nothing to ElevenLabs.

4. **Build and embed.** Run
   `python3 <skill>/scripts/build-video.py <video> --embed <page>`, with `--silent` as in step 3.
   It writes `explainer.mp4`, `explainer.vtt` and `poster.jpg` to `<video>`, and adds a Watch
   section after *In short*, with a nav link. Done when it exits 0 with no `WARN`. Then:
   - Rewrite the section's generic caption to say what the video walks through; a rebuild
     keeps it.
   - Rerun `check-explainer.py`, which now also checks the video files.
   - Open the page in the browser once more and play the first seconds.
   - When the page will be shared as a file (Teams, mail, a shared folder), also run
     `python3 <skill>/scripts/build-video.py <video> --standalone <page>`. It writes
     `<page>-standalone.html` beside the page with a 720p copy of the video inside, about 4 MB
     for two minutes, and renders nothing. The page in git keeps linking the mp4, so its diffs
     stay small; the standalone file is for sending, so leave it out of the commit.

## Voice

The voice is ElevenLabs text-to-speech, used only when the human chose it and
`ELEVENLABS_API_KEY` is set. Each beat's `say`, and its neighbours' for intonation, goes to
ElevenLabs, which returns the time of every word for `self.at`; the build prints how many
characters it sent, which is what the account is billed.
`ELEVENLABS_VOICE_ID` and `ELEVENLABS_MODEL_ID` override the defaults named in the script's
header. With no key, the same build makes a captioned video: the narration shows on screen, timed
at reading pace, with word cues spread evenly over each beat.

## Setup

`build-video.py` finds Manim in the running Python or in its own venv. When it reports Manim
missing, run `python3 <skill>/scripts/build-video.py --setup` once; it installs Manim into
`~/.cache/j-skills/manim-venv`. It needs `ffmpeg` and the cairo and pango libraries from the
system package manager. The build folder and the voice cache live outside the repo, so only the
files in `<video>` are committed.

## Receipt line

`video: <video>/explainer.mp4 · <kind> · <seconds> s · <MB> · <n> beats · <still>% still ·
voiced, <characters> sent | captioned`
