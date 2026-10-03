# understand: the video

Read in step 7 of `SKILL.md`, when the human chose a video in step 2. The video retells the verified page
as a 3Blue1Brown-style animation in the page's own palette: one idea at a time, shapes that move to show
cause and change, and a calm voice over it. The page stays the source of truth. The video makes
no claim the page does not make, so the page's cites and fidelity pass cover it too.

Everything goes in the output folder's `video/`. `<skill>` is this skill's folder; `<video>` is
that `video/` folder.

## Steps

1. **Script.** Copy `<skill>/assets/video/script.json` to `<video>/` and replace its beats.
   Done when every beat's `say` restates a sentence or figure from the page, and the beats read
   aloud in 45 to 180 seconds: about 110 to 400 words at 150 a minute.
   - A beat is one idea and one picture: 4 to 14 beats. Each `say` is one to three sentences
     under the Rules of `plain`.
   - The arc: open on the question the viewer has; name the parts; show the mechanism moving;
     show the change, before then after, unrequested screen changes named as such; close on the
     one thing to keep, the page's *In short*.
   - Write for the ear. Say what a name does, not its spelling: "the save handler", not
     `handlers/save.ts`. Numbers as people say them: "two seconds".

2. **Scene.** Copy `<skill>/assets/video/scene.py` and `kit.py` to `<video>/`. Write one
   `beat_<id>` method per beat, `-` in an id becoming `_`; the example beats show the kit. Done
   when every beat has a method and each animates what its `say` claims.
   - **Show, then tell.** The picture of a beat appears as its sentence starts. Kit pads each beat
     to its narration, so a method only animates and never waits for the voice.
   - **One thing moves at a time.** Keep objects across beats on `self` and change them with
     `Transform`, `Indicate` or a `flow` pulse along arrows, so the viewer watches one diagram
     grow. `self.clear()` only when the next idea starts fresh.
   - **Motion means something.** A `flow` pulse is data or a request moving; a `Transform` is a
     state change; `self.swap(before, after)` is the before/after moment on a screenshot, with
     `focus()` boxing the changed region and `tag("unrequested", "risk")` beside it.
   - **Colour keeps the page's meaning:** the kit uses the page's palette and diagram styles,
     navy for structure and the main path, green for new, red for risk or unrequested, gray for
     the rest. Use the kit's names (`BLUE`, `GREEN`, ...), never Manim's own colours. Labels on screen stay at three words or
     fewer; the voice carries the sentences.
   - Screenshots come from the output folder's `screens/`, the same files the page shows:
     `screen("screens/x-after.jpg")`.
   - A captioned video keeps everything above the caption band, the bottom fifth of the frame.
   - Manim Community Edition API; Text only, never `Tex` or `MathTex`, so LaTeX is not needed.

3. **Draft.** Run `python3 <skill>/scripts/build-video.py <video> --draft`, adding `--silent`
   when the human chose captions. Open the `look:` contact sheet, one still per beat. Done when
   every still shows its beat's picture whole and legible, nothing overlaps or leaves the frame,
   and no `WARN` says an animation outlasts its narration. Fix and rerun; the voice is cached, so
   a rerun sends nothing to ElevenLabs.

4. **Build and embed.** Run
   `python3 <skill>/scripts/build-video.py <video> --embed <page>`, with `--silent` as in step 3.
   It writes `explainer.mp4`, `explainer.vtt` and `poster.jpg` to `<video>`, and adds a Watch
   section after *In short*, with a nav link. Done when it exits 0. Then:
   - Rewrite the section's generic caption to say what the video walks through; a rebuild
     keeps it.
   - Rerun `check-explainer.py`, which now also checks the video files.
   - Open the page in the browser once more and play the first seconds.

## Voice

The voice is ElevenLabs text-to-speech, used only when the human chose it and
`ELEVENLABS_API_KEY` is set. Each beat's `say`, and its neighbours' for intonation, goes to
ElevenLabs; the build prints how many characters it sent, which is what the account is billed.
`ELEVENLABS_VOICE_ID` and `ELEVENLABS_MODEL_ID` override the defaults named in the script's
header. With no key, the same build makes a captioned video: the narration shows on screen, timed
at reading pace.

## Setup

`build-video.py` finds Manim in the running Python or in its own venv. When it reports Manim
missing, run `python3 <skill>/scripts/build-video.py --setup` once; it installs Manim into
`~/.cache/j-skills/manim-venv`. It needs `ffmpeg` and the cairo and pango libraries from the
system package manager. The build folder and the voice cache live outside the repo, so only the
files in `<video>` are committed.

## Receipt line

`video: <video>/explainer.mp4 · <seconds> s · <MB> · <n> beats · voiced, <characters> sent |
captioned`
