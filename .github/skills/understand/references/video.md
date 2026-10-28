# understand: the video

Contents: Video question · Steps · HyperFrames, and where understand differs · Voice · Setup · Receipt line

Read in step 7 of `SKILL.md`, when the human chose a video in step 2. The video retells the
verified page as a 3Blue1Brown-style animation in the page's own palette: one idea at a time,
shapes that move to show cause and change, each picture landing on the word that names it, and
a calm voice over it. The page stays the source of truth. The video makes no claim the page
does not make, so the page's cites and fidelity pass cover it too.

Everything goes in the output folder's `video/`. `<skill>` is this skill's folder; `<video>` is
that `video/` folder.

## Video question

Step 2 reads this question; the build steps below apply in step 7.

   - **Video question:** settle it now, so the rest runs without stopping. A video retells the
     page in motion and earns its cost when the story moves: screens changed, or the work spans
     several parts or steps, such as three or more behaviours or tickets, or a flow or states
     to draw. A small fix, a rename or config change, or a page whose point is one fact does not
     fit. When it fits, ask once, lettered, recommending a when `ELEVENLABS_API_KEY` is set and
     b otherwise: a) video with voice, b) video with on-screen captions, c) no video. Each option
     names its cost: roughly how many characters go to ElevenLabs, whether the key is set, and a
     one-time `build-video.py --setup` on a machine that has not built a video. In the same question, numbered,
     ask which story the video tells: 1) built, what the run built, the default for a slug; 2)
     feature, why the feature exists, what it is and how it works, the default for an area. The
     human answers both at once, such as `a1`. `--video` means a, or b without a key, with the
     default story; `--no-video` or no fit means c. With no human to ask, c, and the receipt
     names `understand <target> --video`.

## Steps

1. **Script.** Copy `<skill>/assets/video/script.json` to `<video>/`, set `kind` to the story the
   human chose in step 2 (`built` or `feature`), and replace its beats. Done when every beat's
   `say` restates a sentence or figure from the page, every beat has a `show`, and the beats
   read aloud in 45 to 180 seconds: about 110 to 400 words at 150 a minute.
   - A beat is one idea and one picture: 4 to 14 beats. Each `say` is one to three sentences
     under the Rules of `plain`.
   - **Follow one case through.** Carry one concrete question, record or click from the first
     beat to the last, so each fact the page states is something that happens to it: it meets
     the guard, gets scanned, comes back as the answer. A run of facts, one per beat, reads as
     slides and is hard to follow.
   - Mark `"chapter": true` on two or three beats at most, where the story changes place, such
     as from the system's inside to the screen a user sees. Every new chapter clears the stage,
     and a viewer who sees the stage clear every few seconds loses the thread.
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

2. **Scene.** Copy `<skill>/assets/video/scene.js` to `<video>/`; the build copies `kit.js`
   beside it. Write one `beat("id", ({ at, start }) => { ... })` per beat, in the script's order;
   the example beats show the kit, and each section of `kit.js` opens with what its functions do.
   Done when every beat has a `beat()` and each animates what its `show` describes.
   - **Craft from HyperFrames.** Before the first beat, load the `hyperframes` skill and read
     its `references/motion.md` and `references/types/explainer.md`: eases by role, move and
     hold timings, transitions with a cause, and the picture devices that explain. Before
     drawing a named visual by hand, such as a chart, a code change or a transition, search
     the `hyperframes-registry` skill's catalog for a block. Their numbers set the motion;
     the rules in *HyperFrames, and where understand differs* below win wherever the two differ.
   - **Registry blocks.** A block is a whole 1920×1080 scene with its own timeline; a
     component pastes into a page and does not mount here. List a block on its beat in
     `script.json`: `"blocks": [{"name": "data-chart", "at": "rose", "seconds": 4, "box": [960,
     120, 900, 506]}]`, with `at` the word it starts on and `box` its place in stage pixels;
     `"values"` passes its variables. The build installs it once into `<video>/blocks/`, and
     every rebuild uses that file. Edit it there before the first draft: the page's figures and
     words in place of its sample data, the colours in `kit.js`, Arial in place of its web
     fonts, `assets/gsap.min.js` in place of its CDN script, and text that stays at 28 px or
     more once scaled into its box. A block made for the full frame reads best at full stage
     or half of it.
   - **Land each picture on its word.** `at("towed")` is the time the voice reaches that word
     of the beat's `say`, so `grow(box, at("towed"))` arrives as it is named. Cue the noun that
     names the picture ("lost car"), not the number at the end of the phrase; a change that
     should finish on a word runs from one cue to the next: `count(n, at("rose"), 73.5,
     at("quarters") - at("rose"))`. A word said twice in a beat takes `at("word", 2)`. A landed
     picture holds while it is read; the build reports a still stretch over 3.5 s. Fill one with
     the story's next step or a camera move, never a pulse on something already on screen:
     pulses added to fill time read as twitching.
   - **Place in stage pixels.** The stage is 1920×1080 with the origin top left; `node`,
     `label`, `tag`, `screen` and `code` take a centre point, and each placed thing keeps its
     box, which `arrow`, `morph` and `look` read. Lay a row on a grid before writing numbers,
     as for the page's diagrams: boxes about 300×110, columns about 420 px apart.
   - **Chapters are stages the camera travels.** A beat with `"chapter": true` starts a new
     stage; the previous one fades out over its last 0.3 s. When the case travels, lay its
     stations along one row wider than the frame, about 510 px apart, and follow it with
     `look(x, y, 1, t)`; the build marks the overflow as intended. Keep objects on `S` and carry
     them on with `morph(a, b, t)`, or keep them in place: a card that rides from station to
     station tells the viewer how the steps connect, where a fresh stage makes them start over.
   - **Recorded clips show the real screen moving.** When the page's pictures come from the
     running app or the made-up-data render of `SKILL.md` step 3, record the component doing
     what the beat names. Drive it through the app's own state code with a timed script, timed
     to the word times in the draft build's `timings.json`. Record it in Chrome at 2× scale,
     cropped to the component, and convert it to H.264 in `<video>/clips/`. List it on its beat:
     `"clips": [{"src": "clips/live.mp4", "id": "answer", "at": "panel", "from": 6.8,
     "seconds": 16, "box": [758, 60, 403, 960]}]`, with `from` the point in the recording to
     start at. The kit fades it in and out; zoom in with `K.tl.to(clip("answer"), {x, y,
     scale})` on the part the voice names, about 2×, since the page's player shows the video at
     40%. Say on screen when the data is made up. The build's motion check skips the time a
     clip is on screen, since a recording moves as the product does.
   - **Move the camera to the subject.** `look(x, y, zoom, t)` centres a point and zooms;
     `home(t)` returns to the full stage. Dim the boxes outside the shot (`dim(box, t)`) so a
     cropped neighbour reads as context.
   - **Give things weight.** Small parts enter with `pop`; boxes, bars and screenshots with
     `grow` or `fill`, which overshoot a little and settle, as real objects do; `enter` slides
     a thing in from one side. Numbers `count` up while their bar fills; give every object an
     entrance, since an object with none stays invisible.
   - **Motion means something.** A `flow` pulse is data or a request moving; a `morph` is the
     same thing in a new state; `swap(before, after, t)` is the before/after moment on a
     screenshot, the after pushing the before out, with `focus(shot, x, y, w, h)` boxing the
     changed region and `tag("unrequested", ...)` beside it in `"risk"`.
   - **Colour keeps the page's meaning:** `kind` is `"plain"`, `"main"` (navy, structure and the
     main path), `"new"` (green) or `"risk"` (red); free colours come from `C`, the page's
     palette. Labels on screen stay at three words or fewer; the voice carries the sentences.
   - Screenshots come from the output folder's `screens/`, the same files the page shows:
     `screen("screens/x-after.jpg", 960, 500, { w: 1100, h: 690 })`, with `h` the picture's
     height at that width.
   - A captioned video keeps everything above the caption band, the bottom fifth of the frame.
   - Everything on screen is a function of timeline time: place tweens with the kit or on
     `K.tl` at a cue, and draw scatter with `rng(seed)`, never `Math.random()`, so every render
     is identical.

3. **Draft.** Run `python3 <skill>/scripts/build-video.py <video> --draft`, adding `--silent`
   when the human chose captions. It runs HyperFrames' check first, which stops on a scene error
   with the beat and cue at fault, then prints a `motion:` line (share of still frames, holds
   over 2 s, pops) and a `WARN` for each hold, pop, overlap, overflow and low-contrast text, with
   its time and beat. Open the `look:` contact sheet, one still per beat. Done when every still
   shows its beat's `show` whole and legible, nothing overlaps or leaves the frame, and no `WARN`
   is left.
   - Look at the sheet against `hyperframes`' `references/review.md` §2, *What to look for*.
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

## HyperFrames, and where understand differs

The HyperFrames skills are installed per machine; `checkup` warns when they are missing, with
the install command. Their skill makes a film from a brief. This one retells a checked page, so
these rules win over theirs:

- **The story is `script.json`.** Skip *Story* §2, three storylines and a pick, and the spec
  and storyboard files: the arc in step 1 and the page decide the beats. *Story* §3, the hook,
  and §8, the tells of a generated film, still apply.
- **No music and no sound effects.** The voice is the only sound, or captions carry the words;
  skip *Sound*.
- **No stops.** Skip the work loop's Studio preview before rendering and the desktop-app
  offers; `build-video.py` checks, renders and embeds in one run.
- **`build-video.py` owns the project.** It writes `index.html` with every chapter in one
  file, so ignore the one-scene-per-file rule. Edit `scene.js` and the files in
  `<video>/blocks/`; place blocks through `script.json` and everything else through the kit,
  never as new `data-start` elements in `index.html`.
- **The page's look.** Colours, type and diagram styles come from the page and `kit.js`; skip
  *Look*'s presets and brand steps.
- **Facts.** A block from the registry shows only figures the page states, as every beat does.

## Voice

The voice is ElevenLabs text-to-speech, used only when the human chose it and
`ELEVENLABS_API_KEY` is set. The whole script goes in one request, with a paragraph break
between beats, so it reads as one narration instead of starting and stopping at every beat.
ElevenLabs returns the time of every word, and the build cuts each beat from those times for
`at()`. A change to any `say` voices the whole script again; the build prints how many
characters it sent, which is what the account is billed.
`ELEVENLABS_VOICE_ID` and `ELEVENLABS_MODEL_ID` override the defaults named in the script's
header. With no key, the same build makes a captioned video: the narration shows on screen, timed
at reading pace, with word cues spread evenly over each beat.

## Setup

`build-video.py` renders with the HyperFrames CLI, pinned in the script and run through `npx`,
so it needs Node.js 22 or newer and `ffmpeg`. Run `python3 <skill>/scripts/build-video.py
--setup` once per machine: it fetches the CLI, finds Chrome or downloads one, and caches GSAP,
so a render needs no network. Telemetry stays off. The build folder and the voice cache live
outside the repo, so only the files in `<video>` are committed. The build folder is a HyperFrames
project; the `studio:` line the build prints opens it in the browser preview.

## Receipt line

`video: <video>/explainer.mp4 · <kind> · <seconds> s · <MB> · <n> beats · <still>% still ·
voiced, <characters> sent | captioned`
