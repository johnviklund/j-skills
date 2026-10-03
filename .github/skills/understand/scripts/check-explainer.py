#!/usr/bin/env python3
"""Check an `understand` explainer before it is committed.

Errors (exit 1): leftover {{placeholders}}; a network-loaded resource; no citations; a citation
whose commit, file or line range does not exist in the repo; a diagram that is not well-formed
SVG or has no viewBox.
Warnings: sentences over the STE-ish limit (25 words), paragraphs over 6 sentences, file size,
diagram shapes outside their viewBox, or a viewBox wider than the text column.

Usage: check-explainer.py <explainer.html> [--repo <git root>]   (default repo: cwd)
"""
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

SENTENCE_WORDS = 25
PARAGRAPH_SENTENCES = 6
SIZE_WARN = 150_000
MAX_DIAGRAM_WIDTH = 760
PROSE_TAGS = {"p", "li", "dd", "td", "summary", "figcaption"}
SKIP_TAGS = {"style", "script", "svg", "code", "pre", "nav"}
REMOTE = [
    (r"<script[^>]*\ssrc=", "<script src>"),
    (r"<link[^>]*rel=[\"']?stylesheet", "<link rel=stylesheet>"),
    (r"<(?:img|source|video|audio|iframe)[^>]*\ssrc=[\"']?https?:", "remote media"),
    (r"@import", "@import"),
    (r"url\(\s*[\"']?https?:", "remote url() in CSS"),
]


class Prose(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.cites, self.blocks, self.stack, self.skip, self.buf = [], [], [], 0, None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and "cite" in (a.get("class") or "").split():
            self.cites.append(a)
        if tag in SKIP_TAGS:
            self.skip += 1
        if tag in PROSE_TAGS and self.buf is None and not self.skip:
            self.buf, self.stack = [], [tag]
        elif self.buf is not None and tag in PROSE_TAGS:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS and self.skip:
            self.skip -= 1
        if self.buf is not None and tag in PROSE_TAGS and self.stack:
            self.stack.pop()
            if not self.stack:
                self.blocks.append(" ".join("".join(self.buf).split()))
                self.buf = None

    def handle_data(self, data):
        if self.buf is not None and not self.skip:
            self.buf.append(data)


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)


def check_cite(repo, a):
    sha, path, lines = a.get("data-sha"), a.get("data-path"), a.get("data-lines")
    label = path or sha or a.get("href", "?")
    if not sha:
        return f"cite {label}: missing data-sha"
    if git(repo, "cat-file", "-e", f"{sha}^{{commit}}").returncode:
        return f"cite {label}: commit {sha} not found"
    if not path:
        return None
    blob = git(repo, "show", f"{sha}:{path}")
    if blob.returncode:
        return f"cite {path}: not in {sha[:10]}"
    if lines:
        m = re.fullmatch(r"(\d+)(?:-(\d+))?", lines)
        if not m:
            return f"cite {path}: bad data-lines '{lines}' (use 12 or 12-30)"
        start, end = int(m.group(1)), int(m.group(2) or m.group(1))
        total = blob.stdout.count("\n") + (0 if blob.stdout.endswith("\n") else 1)
        if not 1 <= start <= end <= total:
            return f"cite {path}:{lines}: outside 1-{total} at {sha[:10]}"
    return None


def check_diagrams(page, errors, warnings):
    """Each <svg class="diagram"> must be well-formed XML with a viewBox; shapes outside the
    viewBox are warned (skipped when the svg uses transforms)."""
    svgs = re.findall(r'<svg\b[^>]*class="[^"]*\bdiagram\b[^"]*"[\s\S]*?</svg>', page)
    for n, svg in enumerate(svgs, 1):
        try:
            root = ET.fromstring(svg)
        except ET.ParseError as exc:
            errors.append(f"diagram {n}: not well-formed SVG ({exc})")
            continue
        box = (root.get("viewBox") or "").replace(",", " ").split()
        if len(box) != 4:
            errors.append(f"diagram {n}: missing viewBox")
            continue
        if "transform=" in svg:
            continue
        x0, y0, w, h = map(float, box)
        if w > MAX_DIAGRAM_WIDTH:
            warnings.append(f"diagram {n}: viewBox {w:g} wide shrinks its labels; keep it <= {MAX_DIAGRAM_WIDTH}")
        for el in root.iter():
            for ax, ay, dx, dy in (("x", "y", "width", "height"), ("cx", "cy", "r", "r"),
                                   ("x1", "y1", None, None), ("x2", "y2", None, None)):
                try:
                    x, y = float(el.get(ax)), float(el.get(ay))
                except (TypeError, ValueError):
                    continue
                x_end = x + float(el.get(dx) or 0) if dx else x
                y_end = y + float(el.get(dy) or 0) if dy else y
                if x < x0 or y < y0 or x_end > x0 + w or y_end > y0 + h:
                    tag = el.tag.split("}")[-1]
                    warnings.append(f"diagram {n}: <{tag}> at ({x:g},{y:g}) leaves the viewBox {' '.join(box)}")
    return len(svgs)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    path = sys.argv[1]
    repo = sys.argv[sys.argv.index("--repo") + 1] if "--repo" in sys.argv else "."
    page = open(path, encoding="utf-8").read()
    errors, warnings = [], []

    for m in re.finditer(r"\{\{[^}]*\}\}", page):
        errors.append(f"placeholder left: {m.group(0)[:60]}")
    live = re.sub(r"<!--[\s\S]*?-->", "", page)
    for pattern, what in REMOTE:
        if re.search(pattern, live, re.I):
            errors.append(f"network-loaded resource: {what}")

    parser = Prose()
    parser.feed(page)
    if not parser.cites:
        errors.append("no citations (a.cite) found")
    errors += [e for e in (check_cite(repo, a) for a in parser.cites) if e]

    for block in parser.blocks:
        sentences = [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])", block) if s.strip()]
        if len(sentences) > PARAGRAPH_SENTENCES:
            warnings.append(f"{len(sentences)} sentences in one block: \"{block[:60]}...\"")
        for s in sentences:
            words = len(s.split())
            if words > SENTENCE_WORDS:
                warnings.append(f"{words}-word sentence: \"{s[:70]}...\"")
    size = len(page.encode("utf-8"))
    if size > SIZE_WARN:
        warnings.append(f"file is {size // 1000} KB (budget ~{SIZE_WARN // 1000} KB)")
    diagrams = check_diagrams(live, errors, warnings)

    for e in errors:
        print(f"ERROR   {e}")
    for w in warnings:
        print(f"WARN    {w}")
    print(f"cites: {len(parser.cites)} checked · diagrams: {diagrams} · errors: {len(errors)} · "
          f"warnings: {len(warnings)} · size: {size // 1000} KB")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
