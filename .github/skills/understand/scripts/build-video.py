#!/usr/bin/env python3
"""Build an understand explainer video from a video folder holding script.json, scene.py, kit.py.

Steps: lint script.json, narrate each beat (ElevenLabs when ELEVENLABS_API_KEY is set, else
on-screen captions), render scene.py with Manim, lay each beat's voice at the second its beat
starts, and write explainer.mp4, explainer.vtt, poster.jpg into the folder. A contact sheet with
one still per beat goes to the build folder for checking the look.

Usage:
    build-video.py VIDEO_DIR [--silent] [--draft] [--embed PAGE]
    build-video.py --setup            install Manim into ~/.cache/j-skills/manim-venv

    --silent  no voice even when a key is set; narration shows as on-screen captions
    --draft   480p at 15 fps into the build folder only, for checking timing and layout fast
    --embed   put this build in PAGE's Watch section, adding the section after In short when
              missing. Captions go in inline: browsers refuse a caption file next to a page
              opened from disk (tested in Chromium, 2026-10-04)

Needs: Python 3.10+, ffmpeg and ffprobe, and Manim Community Edition (cairo and pango libraries).
Narration: ELEVENLABS_API_KEY; optional ELEVENLABS_VOICE_ID, ELEVENLABS_MODEL_ID. Voice files are
cached by text, voice and model in ~/.cache/j-skills/understand-tts, so a rebuild costs nothing.
Exit code 0 on success, 1 on a failed step, 2 on bad input.
"""
import argparse
import base64
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from html import escape as html_escape

CACHE = pathlib.Path(os.environ.get("XDG_CACHE_HOME", pathlib.Path.home() / ".cache")) / "j-skills"
VENV = CACHE / "manim-venv"
TTS_CACHE = CACHE / "understand-tts"
SKILL = pathlib.Path(__file__).resolve().parent.parent

API = os.environ.get("ELEVENLABS_BASE_URL", "https://api.elevenlabs.io")
# George: a calm, warm narrator from ElevenLabs' default library, available on every account.
VOICE = os.environ.get("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")
# Their most natural long-form model at the time of writing; override per account.
MODEL = os.environ.get("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")

BREATH = 0.6           # quiet after each voiced beat, so beats do not run together
READ_WPS = 2.5         # silent beats: ~150 words a minute, a relaxed reading pace beside motion
MIN_BEAT = 3.0         # a beat shorter than this flashes past before the eye settles
SENTENCE_WORDS = 25    # the plain skill's sentence limit, so narration reads as the page does
LENGTH_OK = (45, 180)  # seconds: under 45 says too little to beat the page, over 180 loses people
VIDEO_WARN = 25_000_000  # bytes: a 26 s 1080p test build was 0.6 MB (2026-10-04); 25 MB leaves
                         # room for 3 minutes with many screenshots
FINAL = ["-r", "1920,1080", "--fps", "30"]
DRAFT = ["-r", "854,480", "--fps", "15"]


def fail(msg, code=1):
    print(f"ERROR   {msg}")
    sys.exit(code)


def run(cmd, what):
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode:
        tail = "\n".join((res.stderr or res.stdout).strip().splitlines()[-25:])
        fail(f"{what} failed (exit {res.returncode}):\n{tail}")
    return res


def manim_python():
    """The interpreter that has Manim: this one, else the skill's venv."""
    for py in (sys.executable, VENV / "bin" / "python"):
        if pathlib.Path(py).exists() and not subprocess.run(
                [str(py), "-c", "import manim"], capture_output=True).returncode:
            return str(py)
    fail(f"Manim not found. Install it with: python3 {__file__} --setup "
         f"(a venv in {VENV}; needs the cairo and pango libraries and ffmpeg)")


def setup():
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            fail(f"{tool} not found; install ffmpeg with the system package manager first")
    run([sys.executable, "-m", "venv", str(VENV)], "creating the venv")
    print(f"installing manim into {VENV} ...")
    run([str(VENV / "bin" / "pip"), "install", "-q", "manim"], "pip install manim")
    ver = run([str(VENV / "bin" / "python"), "-c", "import manim; print(manim.__version__)"],
              "importing manim").stdout.strip()
    print(f"ok      manim {ver} in {VENV}")


def lint(script):
    errors, warnings = [], []
    beats = script.get("beats")
    if not script.get("title"):
        errors.append('script.json: missing "title"')
    if not isinstance(beats, list) or not beats:
        errors.append('script.json: "beats" must be a non-empty list')
        return errors, warnings, []
    seen = set()
    for n, b in enumerate(beats, 1):
        bid, say = b.get("id", ""), (b.get("say") or "").strip()
        if not re.fullmatch(r"[a-z][a-z0-9_-]*", bid):
            errors.append(f"beat {n}: id '{bid}' must be lowercase letters, digits, - or _")
        if bid in seen:
            errors.append(f"beat {n}: id '{bid}' used twice")
        seen.add(bid)
        if not say:
            errors.append(f"beat {bid or n}: empty \"say\"")
        if "—" in say:
            warnings.append(f"beat {bid}: em dash in narration; use a full stop")
        for s in re.split(r"(?<=[.!?])\s+", say):
            if len(s.split()) > SENTENCE_WORDS:
                warnings.append(f"beat {bid}: {len(s.split())}-word sentence: \"{s[:60]}...\"")
    if not 4 <= len(beats) <= 14:
        warnings.append(f"{len(beats)} beats; 4 to 14 keeps one idea per beat at 45-180 s")
    return errors, warnings, beats


def duration(path):
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
               str(path)], f"reading the length of {path.name}").stdout
    return float(out.strip())


def tts(text, prev_text, next_text, key):
    """One beat's voice as mp3, from the cache when the same text, voice and model ran before."""
    digest = hashlib.sha256(f"{VOICE}\n{MODEL}\n{prev_text}\n{text}\n{next_text}".encode()).hexdigest()
    path = TTS_CACHE / f"{digest[:24]}.mp3"
    if path.exists():
        return path, True
    body = {"text": text, "model_id": MODEL}
    # Neighbouring beats let the voice keep one intonation across separately voiced clips.
    if prev_text:
        body["previous_text"] = prev_text
    if next_text:
        body["next_text"] = next_text
    req = urllib.request.Request(
        f"{API}/v1/text-to-speech/{VOICE}?output_format=mp3_44100_128",
        data=json.dumps(body).encode(), method="POST",
        headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            audio = resp.read()
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:300]
        hint = {401: "the key was rejected; check ELEVENLABS_API_KEY",
                404: f"voice {VOICE} not found; set ELEVENLABS_VOICE_ID to a voice on this account",
                422: f"the request was refused; check ELEVENLABS_MODEL_ID ({MODEL}) and the text",
                429: "rate limit or quota reached; wait, or build with --silent"}.get(e.code, "")
        fail(f"ElevenLabs answered {e.code}. {hint}\n{detail}")
    except urllib.error.URLError as e:
        fail(f"ElevenLabs unreachable ({e.reason}); check the network, or build with --silent")
    TTS_CACHE.mkdir(parents=True, exist_ok=True)
    path.write_bytes(audio)
    return path, False


def narrate(beats, voiced, build):
    timings, key = {"voiced": voiced, "beats": {}}, os.environ.get("ELEVENLABS_API_KEY", "")
    paid = 0
    for i, b in enumerate(beats):
        if voiced:
            prev = beats[i - 1]["say"] if i else ""
            nxt = beats[i + 1]["say"] if i + 1 < len(beats) else ""
            audio, cached = tts(b["say"], prev, nxt, key)
            paid += 0 if cached else len(b["say"])
            secs = duration(audio) + BREATH
            timings["beats"][b["id"]] = {"seconds": round(secs, 3), "audio": str(audio)}
        else:
            secs = max(MIN_BEAT, len(b["say"].split()) / READ_WPS + 1.0)
            timings["beats"][b["id"]] = {"seconds": round(secs, 3)}
    (build / "timings.json").write_text(json.dumps(timings, indent=1))
    return timings, paid


def render(video_dir, build, quality):
    py = manim_python()
    media = build / "media"
    env = dict(os.environ, UNDERSTAND_VIDEO_DIR=str(video_dir), UNDERSTAND_BUILD_DIR=str(build),
               PYTHONPATH=str(video_dir), PYTHONDONTWRITEBYTECODE="1")
    cmd = [py, "-m", "manim", "render", str(video_dir / "scene.py"), "Explainer", *quality,
           "--media_dir", str(media), "--disable_caching", "-o", "render", "--progress_bar", "none"]
    res = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if res.returncode:
        msg = "\n".join((res.stderr or res.stdout).strip().splitlines()[-30:])
        fail(f"Manim render failed:\n{msg}")
    found = sorted(media.glob("videos/**/render.mp4"), key=lambda p: p.stat().st_mtime)
    if not found:
        fail(f"Manim finished but wrote no render.mp4 under {media}")
    return found[-1]


def mux(silent_mp4, spans, timings, out):
    if not timings["voiced"]:
        run(["ffmpeg", "-y", "-v", "error", "-i", str(silent_mp4), "-c", "copy",
             "-movflags", "+faststart", str(out)], "writing the video")
        return
    inputs, delays = [], []
    for n, span in enumerate(spans):
        ms = int(span["start"] * 1000)
        inputs += ["-i", timings["beats"][span["id"]]["audio"]]
        delays.append(f"[{n + 1}:a]adelay={ms}|{ms}[a{n}]")
    mix = ";".join(delays) + ";" + "".join(f"[a{n}]" for n in range(len(spans))) + \
        f"amix=inputs={len(spans)}:normalize=0:dropout_transition=0[voice]"
    run(["ffmpeg", "-y", "-v", "error", "-i", str(silent_mp4), *inputs,
         "-filter_complex", mix, "-map", "0:v", "-map", "[voice]", "-c:v", "copy",
         "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(out)],
        "mixing the narration into the video")


def stamp(t):
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{s:06.3f}"


def captions(beats, spans, out):
    """WebVTT with one cue per sentence, each sentence timed by its share of the beat's words."""
    say = {b["id"]: b["say"] for b in beats}
    lines = ["WEBVTT", ""]
    for span in spans:
        sentences = [s for s in re.split(r"(?<=[.!?])\s+", say[span["id"]].strip()) if s]
        words = sum(len(s.split()) for s in sentences) or 1
        t, length = span["start"], span["end"] - span["start"]
        for s in sentences:
            end = t + length * len(s.split()) / words
            lines += [f"{stamp(t)} --> {stamp(end)}", s, ""]
            t = end
    out.write_text("\n".join(lines))


def stills(video, spans, build, poster):
    """poster.jpg from the end of the first beat, and a contact sheet with one still per beat."""
    first = spans[0]
    run(["ffmpeg", "-y", "-v", "error", "-ss", f"{max(0, first['end'] - 0.2):.2f}", "-i",
         str(video), "-frames:v", "1", "-q:v", "4", str(poster)], "writing the poster")
    frames = build / "frames"
    shutil.rmtree(frames, ignore_errors=True)
    frames.mkdir()
    for n, span in enumerate(spans):
        # Just before a beat ends shows everything it built.
        t = max(span["start"], span["end"] - 0.3)
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1",
             "-vf", "scale=640:-2", str(frames / f"{n:02d}.png")], "taking a still")
    cols = 3 if len(spans) > 4 else 2
    rows = -(-len(spans) // cols)
    sheet = build / "contact.jpg"
    run(["ffmpeg", "-y", "-v", "error", "-framerate", "1", "-i", str(frames / "%02d.png"),
         "-vf", f"tile={cols}x{rows}:padding=8:color=0xd3d6d8", "-frames:v", "1", "-q:v", "3",
         str(sheet)], "tiling the contact sheet")
    return sheet


def embed(page, video_dir, out, vtt, title, seconds, voiced):
    """Put this build in the page's Watch section, after In short, adding the section and its
    nav link when missing. A rebuild replaces only the video element, keeping a reworded
    caption."""
    html = page.read_text(encoding="utf-8")
    rel = os.path.relpath(video_dir, page.parent)
    track = base64.b64encode(vtt.read_bytes()).decode()
    element = (f'<video controls preload="metadata" poster="{rel}/poster.jpg">'
               f'<source src="{rel}/{out.name}" type="video/mp4">'
               f'<track kind="captions" srclang="en" label="Captions" '
               f'src="data:text/vtt;base64,{track}"></video>')
    if re.search(r'<section id="video"', html):
        html = re.sub(r'(<section id="video"[\s\S]*?)<video\b[\s\S]*?</video>',
                      lambda m: m.group(1) + element, html, count=1)
    else:
        how = "voiced" if voiced else "with the narration as captions on screen"
        section = (f'\n\n<section id="video">\n  <h2>Watch</h2>\n  <figure class="video">\n'
                   f'    {element}\n    <figcaption>{html_escape(title)}: the same story in '
                   f'{round(seconds)} seconds, {how}.</figcaption>\n  </figure>\n</section>')
        m = re.search(r'<section id="tldr"[\s\S]*?</section>', html)
        if not m:
            fail(f'{page} has no <section id="tldr">; is it an understand explainer?', 2)
        html = html[:m.end()] + section + html[m.end():]
        html = re.sub(r'(<li><a href="#tldr">[^<]*</a></li>)',
                      lambda m: m.group(1) + '\n    <li><a href="#video">Watch</a></li>',
                      html, count=1)
    page.write_text(html, encoding="utf-8")
    print(f"embed: {page} plays {rel}/{out.name} in its Watch section")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("video_dir", nargs="?")
    ap.add_argument("--silent", action="store_true")
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--setup", action="store_true")
    ap.add_argument("--embed", metavar="PAGE")
    args = ap.parse_args()
    if args.setup:
        return setup()
    if not args.video_dir:
        ap.error("VIDEO_DIR is required (the output folder's video/)")
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            fail(f"{tool} not found; install ffmpeg with the system package manager")

    video_dir = pathlib.Path(args.video_dir).resolve()
    for name in ("script.json", "scene.py"):
        if not (video_dir / name).is_file():
            fail(f"{video_dir / name} missing; copy it from {SKILL / 'assets/video'}", 2)
    if not (video_dir / "kit.py").is_file():
        shutil.copy(SKILL / "assets/video/kit.py", video_dir / "kit.py")
        print("copied  kit.py into the video folder")
    try:
        script = json.loads((video_dir / "script.json").read_text())
    except json.JSONDecodeError as e:
        fail(f"script.json is not valid JSON: {e}", 2)
    errors, warnings, beats = lint(script)
    if errors:
        fail("\n        ".join(errors), 2)

    voiced = not args.silent and bool(os.environ.get("ELEVENLABS_API_KEY"))
    if not args.silent and not voiced:
        print("note    ELEVENLABS_API_KEY not set: silent video, narration as on-screen captions")
    build = pathlib.Path(tempfile.gettempdir()) / "understand-video" / \
        hashlib.sha256(str(video_dir).encode()).hexdigest()[:12]
    build.mkdir(parents=True, exist_ok=True)

    timings, paid = narrate(beats, voiced, build)
    raw = render(video_dir, build, DRAFT if args.draft else FINAL)
    spans = json.loads((build / "beats.json").read_text())
    if [s["id"] for s in spans] != [b["id"] for b in beats]:
        fail("beats.json does not match script.json; was construct() overridden in scene.py?")

    out_dir = build if args.draft else video_dir
    out = out_dir / ("draft.mp4" if args.draft else "explainer.mp4")
    mux(raw, spans, timings, out)
    captions(beats, spans, out_dir / ("draft.vtt" if args.draft else "explainer.vtt"))
    sheet = stills(out, spans, build, out_dir / ("draft-poster.jpg" if args.draft else "poster.jpg"))

    total, size = duration(out), out.stat().st_size
    if not LENGTH_OK[0] <= total <= LENGTH_OK[1]:
        warnings.append(f"video is {total:.0f} s; aim for {LENGTH_OK[0]}-{LENGTH_OK[1]} s")
    if size > VIDEO_WARN and not args.draft:
        warnings.append(f"explainer.mp4 is {size // 1_000_000} MB (budget ~{VIDEO_WARN // 1_000_000} MB);"
                        " cut beats or hold still images for less time")
    over = [s["id"] for s in spans
            if s["end"] - s["start"] > timings["beats"][s["id"]]["seconds"] + 0.5]
    if over:
        warnings.append("animation outlasts the narration in beats: " + ", ".join(over) +
                        "; shorten their run_time or add words")
    for w in warnings:
        print(f"WARN    {w}")
    voice = f"voiced ({VOICE}, {MODEL}; {paid} characters sent)" if voiced else "silent, captions on screen"
    print(f"video: {out} · {total:.1f} s · {size // 1000} KB · {len(spans)} beats · {voice}")
    print(f"look:  {sheet}")
    if args.embed and not args.draft:
        embed(pathlib.Path(args.embed).resolve(), video_dir, out, video_dir / "explainer.vtt",
              script["title"], total, voiced)


if __name__ == "__main__":
    main()
