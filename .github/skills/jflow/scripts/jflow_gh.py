"""Issue and pull request mode for jflow.py: the run lives in GitHub comments, not in .jflow/.

Hub replays the marked comments, in posting order, into a temporary git repo whose history
mirrors that order on top of the real code trees, so jflow.py's rules run unchanged.
Standard library, Python 3.9+.
"""
import atexit
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

URL = re.compile(r"https://github\.com/([\w.-]+/[\w.-]+)/issues/(\d+)/?")
MARK = re.compile(r"<!-- jflow:(spec|accepted|notes|receipt|record) v1((?: [a-z]+=[\w.#-]+)*) -->\n?")
# Anyone can comment on a public repo: only the gh user and people with write access steer the run.
WRITE = ("admin", "maintain", "write")
POSTS = {"spec": "spec", "check": "receipt", "accept": "accepted"}
SHA = re.compile(r"[0-9a-f]{7,40}")


def git(repo, *args, **kw):
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True,
                          **kw).stdout.strip()


def api(path, body=None, cwd=None, missing=False):
    """gh api, as parsed JSON; a list endpoint returns every page joined. missing: None on a refusal."""
    write = ["-X", "POST", "--input", "-"] if body is not None else ["--paginate"]
    try:
        p = subprocess.run(["gh", "api", path, *write], capture_output=True, text=True, cwd=cwd,
                           input=None if body is None else json.dumps(body))
    except OSError:
        raise SystemExit("gh not found: install the GitHub CLI for issue and pull request mode")
    if p.returncode:
        if re.search(r"auth login|not logged in|authenticat|bad credentials|HTTP 401", p.stderr, re.I):
            raise SystemExit("gh is not authenticated: run gh auth login")
        if missing and re.search(r"HTTP 40[34]", p.stderr):
            return None
        raise SystemExit("gh api failed: " + (p.stderr.strip().splitlines() or [f"exit {p.returncode}"])[0])
    pages, out, i = [], p.stdout.strip(), 0
    try:  # --paginate prints one JSON document per page
        while i < len(out):
            page, i = json.JSONDecoder().raw_decode(out, i)
            pages.append(page)
            i = len(out) - len(out[i:].lstrip())
    except ValueError:
        raise SystemExit(f"gh api {path}: not JSON")
    return [x for p in pages for x in p] if pages and isinstance(pages[0], list) else (pages or [{}])[0]


def digest(body):
    return hashlib.sha256(body.replace("\r\n", "\n").encode()).hexdigest()


def github_mode(a, repo):
    """A plain slug runs in GitHub mode when the external config or git config says so."""
    def mode(path):
        try:
            return json.loads(Path(path).read_text("utf-8")).get("mode")
        except (OSError, ValueError, AttributeError):
            return None  # seats() reports a bad config file

    if mode(repo / ".jflow/config.json") is not None:
        raise SystemExit(".jflow/config.json cannot set mode: use git config jflow.mode or an external config")
    external = getattr(a, "config", None) or os.environ.get("JFLOW_CONFIG")
    chosen = mode(external) if external else None
    if chosen is None:
        chosen = subprocess.run(["git", "-C", str(repo), "config", "--get", "jflow.mode"],
                                capture_output=True, text=True).stdout.strip() or None
    if chosen not in (None, "jflow", "github"):
        raise SystemExit("mode must be jflow or github")
    return chosen == "github"


def add_args(sub, rec, summ, val):
    """GitHub mode's note command and options."""
    note = sub.add_parser("note", help="GitHub mode: post a builder note to the pull request")
    note.add_argument("slug")
    note.add_argument("--repo", default=".")
    for p in (rec, val, note):
        p.add_argument("--file", help="GitHub mode: the spec, receipt, Accepted lines or note to post")
    for p in (rec, note):
        p.add_argument("--confirmed", action="store_true", help="GitHub mode: the human approved a public write")
    for p in (rec, summ, val, note):
        p.add_argument("--config")


class Hub:
    @classmethod
    def of(cls, a, real, slug):
        """The run's Hub in GitHub mode; None in .jflow/ mode. Refuses a bad slug in both."""
        m = re.fullmatch(r"#(\d+)", a.slug) or URL.fullmatch(a.slug)
        if not m and not slug.match(a.slug):
            raise SystemExit(f"bad slug: {a.slug}")
        if not m and not github_mode(a, real):
            if a.cmd == "note":
                raise SystemExit("note works only in issue and pull request mode")
            return None
        try:
            return cls(a, real, m)
        except subprocess.CalledProcessError as error:
            raise SystemExit("git failed: " + ((error.stderr or "").strip().splitlines() or ["?"])[0])
        except OSError as error:
            raise SystemExit(f"cannot read {error.filename}: {error.strerror}")

    def __init__(self, a, real, m):
        self.real, self.head = real, git(real, "rev-parse", "HEAD")
        info = self.api("repos/" + (m[1] if m and m.re is URL else "{owner}/{repo}"))
        self.nwo, public = info.get("full_name"), info.get("private") is False
        step = getattr(a, "step", None)
        if a.cmd in ("record", "note") and public and not a.confirmed:
            raise SystemExit(f"{self.nwo} is public: ask the human before this GitHub write, then pass --confirmed")
        self.issue = int(m[2] if m.re is URL else m[1]) if m else self.find(a.slug)
        self.slug = f"#{self.issue}" if m else a.slug
        self.pr = self.issue and self.find_pr()
        events, self.trust, self.me = [], {}, None
        for number in filter(None, (self.issue, self.pr)):
            for c in self.api(f"repos/{self.nwo}/issues/{number}/comments?per_page=100"):
                body = (c.get("body") or "").replace("\r\n", "\n")
                mark = MARK.match(body)
                if mark and self.trusted((c.get("user") or {}).get("login")):
                    attrs = dict(x.split("=", 1) for x in mark[2].split())
                    events.append((c["created_at"], c["id"], mark[1], attrs, body[mark.end():], body))
        events.sort(key=lambda e: e[:2])
        specs = [e for e in events if e[2] == "spec"]
        locks = [r.get("spec_sha256") for r in self.records(events) if r.get("step") == "spec"]
        # A spec comment edited, unmarked or deleted after record spec no longer matches the lock.
        if locks and (not specs or digest(specs[-1][5]) != locks[-1]) and step != "spec":
            raise SystemExit(f"the spec comment on #{self.issue} changed after record spec; only jflow spec changes it")
        base = re.search(r"^Base:\s*(\S+)", specs[-1][4], re.M) if specs else None
        base = base[1] if base and SHA.fullmatch(base[1]) else None
        stray = (git(real, "diff", "--cached", "--name-only", "--", ".jflow")
                 + "\n" + (git(real, "diff", "--name-only", f"{base}..HEAD", "--", ".jflow") if base else "")).split()
        if stray:
            raise SystemExit(f"issue and pull request mode keeps no .jflow/ files on the branch: remove {stray[0]}")
        coded = base and git(real, "diff", "--name-only", f"{base}..HEAD", "--", ".", ":(exclude).jflow")
        if not self.pr and (coded or a.cmd == "note" or a.cmd == "record" and step not in ("spec", "accept")):
            raise SystemExit(f"no linked pull request: open a draft PR from branch jflow/{self.issue or '<issue>'}"
                             f" with Refs #{self.issue or '<issue>'} in its body")
        self.text = None
        if a.cmd in ("validate", "record") and a.file:
            if step not in POSTS:
                raise SystemExit("--file goes with spec, check or accept")
            self.text = Path(a.file).read_text("utf-8")
            n = re.match(r"# check-(\d+) ", self.text)
            events.append(("9", 0, POSTS[step], {"sha": self.head, "n": n[1] if n else "0"}, self.text, self.text))
        elif a.cmd == "record" and step in POSTS:
            raise SystemExit(f"record {step} in issue and pull request mode needs --file")
        self.repo, self.run = self.replay(events)

    def api(self, path, body=None, missing=False):
        return api(path, body, cwd=self.real, missing=missing)

    def trusted(self, login):
        if login and login not in self.trust:
            self.me = self.me or self.api("user").get("login")
            perm = login != self.me and self.api(f"repos/{self.nwo}/collaborators/{login}/permission", missing=True)
            self.trust[login] = login == self.me or (perm or {}).get("permission") in WRITE
        return self.trust.get(login, False)

    def find_pr(self):
        """The pull request from branch jflow/<issue>, in this repo or a fork's that references the issue:
        an open one first, then the newest."""
        head = f"jflow/{self.issue}"
        found = self.api(f"repos/{self.nwo}/pulls?state=all&per_page=100&head={self.nwo.split('/')[0]}:{head}")
        if not any(p.get("state") == "open" for p in found):
            for e in self.api(f"repos/{self.nwo}/issues/{self.issue}/timeline?per_page=100"):
                source = (e.get("source") or {}).get("issue") or {}
                if e.get("event") == "cross-referenced" and "pull_request" in source and \
                        (source.get("repository") or {}).get("full_name", self.nwo) == self.nwo:
                    pr = self.api(f"repos/{self.nwo}/pulls/{source['number']}")
                    found += [pr] if (pr.get("head") or {}).get("ref") == head else []
        return max(found, key=lambda p: (p.get("state") == "open", p["number"]))["number"] if found else None

    def find(self, slug):
        """The issue titled 'jflow: <slug>', or None."""
        return min((i["number"] for i in self.api(f"repos/{self.nwo}/issues?state=all&per_page=100")
                    if i.get("title") == f"jflow: {slug}" and "pull_request" not in i), default=None)

    @staticmethod
    def records(events):
        out = []
        for e in (e for e in events if e[2] == "record"):
            try:
                r = json.loads(re.search(r"```json\n(.*?)\n```", e[4], re.S)[1])
            except (TypeError, ValueError):
                raise SystemExit(f"jflow record comment {e[1]} holds no JSON record")
            # Re-recording replaces the check's line.
            out = [x for x in out if not (r.get("step") == "check" == x.get("step") and x.get("n") == r.get("n"))] + [r]
        return out

    def replay(self, events):
        tmp = Path(tempfile.mkdtemp(prefix="jflow-gh-"))
        atexit.register(shutil.rmtree, tmp, True)
        git(tmp, "init", "-q")
        objects = Path(git(self.real, "rev-parse", "--path-format=absolute", "--git-common-dir")) / "objects"
        (tmp / ".git/objects/info/alternates").write_text(f"{objects}\n", "utf-8")
        spec, accepted, notes, receipts, files, parent, checked, done = None, [], [], {}, {}, None, None, False
        now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        for i, (at, _, kind, attrs, body, _) in enumerate(events):
            if kind == "spec":
                spec, done = body, False  # a spec posted after done starts the run again
            elif kind == "accepted":
                accepted += [l for l in body.splitlines() if l.startswith("- ")]
            elif kind == "notes":
                notes.append(body.rstrip("\n") + "\n")
            elif kind == "receipt":
                receipts[attrs.get("n", "0")], checked = body, spec
            records = self.records(events[:i + 1])
            done = done or kind == "record" and records[-1].get("step") == "done"
            if spec is not None:
                text = spec.rstrip("\n") + "\n" + ("\n## Accepted\n" + "\n".join(accepted) + "\n") * bool(accepted)
                files["spec.md"] = re.sub(r"^Status: ready", "Status: done", text, flags=re.M) if done else text
            files.update({"notes.md": "".join(notes), "run.jsonl": "".join(json.dumps(r) + "\n" for r in records),
                          **{f"receipts/check-{n}.md": t for n, t in receipts.items()}})
            if not SHA.fullmatch(attrs.get("sha", "")):
                raise SystemExit(f"jflow comment {events[i][1]} has no commit sha in its marker")
            parent = self.commit(tmp, attrs["sha"], files, parent, now if at == "9" else at)
        # A spec changed after the newest receipt needs every row again: a stand-in file outside
        # .jflow/ makes jflow.py see a change since that check, until the next receipt.
        extra = {".jflow-spec-changed": "the spec changed after the newest check\n"} if receipts and spec != checked else {}
        git(tmp, "update-ref", "HEAD", self.commit(tmp, self.head, files, parent, now, extra))
        run = tmp / ".jflow" / self.slug
        for name, text in files.items():
            (run / name).parent.mkdir(parents=True, exist_ok=True)
            (run / name).write_text(text, "utf-8")
        if (self.real / "PRODUCT.md").exists():
            shutil.copy(self.real / "PRODUCT.md", tmp / "PRODUCT.md")
        return tmp, run

    def commit(self, tmp, sha, files, parent, at, extra=None):
        env = dict(os.environ, GIT_INDEX_FILE=str(tmp / ".git/jflow-index"), GIT_AUTHOR_NAME="jflow",
                   GIT_AUTHOR_EMAIL="jflow@localhost", GIT_COMMITTER_NAME="jflow",
                   GIT_COMMITTER_EMAIL="jflow@localhost", GIT_AUTHOR_DATE=at, GIT_COMMITTER_DATE=at)
        try:
            git(tmp, "read-tree", sha, env=env)
        except subprocess.CalledProcessError:
            raise SystemExit(f"unknown commit {sha} in a jflow comment: fetch the run branch first")
        paths = dict({f".jflow/{self.slug}/{n}": t for n, t in files.items()}, **(extra or {}))
        index = "".join(f"100644 {git(tmp, 'hash-object', '-w', '--stdin', input=t)}\t{n}\n" for n, t in paths.items())
        git(tmp, "update-index", "--add", "--index-info", input=index, env=env)
        tree = git(tmp, "write-tree", env=env)
        return git(tmp, "commit-tree", "--no-gpg-sign", tree, *(["-p", parent] if parent else []), "-m", "jflow", env=env)

    def comment(self, number, kind, body, **attrs):
        attrs = "".join(f" {k}={v}" for k, v in dict(attrs, sha=self.head).items())
        return self.api(f"repos/{self.nwo}/issues/{number}/comments", {"body": f"<!-- jflow:{kind} v1{attrs} -->\n{body}"})

    def post(self, step, entry):
        """Post the step's spec, receipt or Accepted lines, then its record."""
        entry["sha"] = self.head
        if step == "spec" and not self.issue:
            self.issue = self.api(f"repos/{self.nwo}/issues", {
                "title": f"jflow: {self.slug}",
                "body": f"jflow run `{self.slug}`: the spec and its Accepted lines are in the comments."})["number"]
        if step in POSTS:
            extra = {"n": entry["n"]} if step == "check" else {"slug": self.slug} if step == "spec" and \
                not self.slug.startswith("#") else {}
            posted = self.comment(self.pr if step == "check" else self.issue, POSTS[step], self.text, **extra)
            if step == "spec":
                entry["spec_sha256"] = digest(posted.get("body", ""))
        self.comment(self.issue if step in ("spec", "accept") else self.pr, "record",
                     "```json\n" + json.dumps(entry) + "\n```")

    def note(self, path):
        self.comment(self.pr, "notes", Path(path).read_text("utf-8"))
        print(f"posted a jflow note on PR #{self.pr}")

    def tidy(self, n):
        """Point a next decision at comments instead of files."""
        for k in ("command", "blocker", "why"):
            if n[k]:
                n[k] = re.sub(r"\.jflow/\S+/receipts/(check-\d+)\.md", rf"the \1 receipt comment on PR #{self.pr}",
                              n[k]).replace("notes.md", f"the jflow notes on PR #{self.pr}").replace("spec.md", "the spec")
        return n
