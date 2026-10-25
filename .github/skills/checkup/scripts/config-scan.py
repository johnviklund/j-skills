#!/usr/bin/env python3
"""Agent settings that let a tool run without asking, or that hold a secret.

Run from the repo root: python3 config-scan.py
Reads the Claude Code, Codex and Copilot CLI settings files that exist, in the project and for
the user, and prints one line per finding: severity, file and key or line, what it allows, fix.
It never prints a setting's value. Python 3.8+ standard library and git; exits 0.

The secret shapes and the pipe-to-shell and Claude key checks are adapted from ruflo-protector
(hooks/scan.ts, hooks/screen.ts) in https://github.com/ruvnet/ruflo, MIT (THIRD-PARTY-NOTICES.md).
"""
import json
import os
import re
import subprocess
import sys

HOME = os.path.expanduser("~")
CLAUDE_HOME = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(HOME, ".claude")
CODEX_HOME = os.environ.get("CODEX_HOME") or os.path.join(HOME, ".codex")

# (path, kind): project files first, then the user's.
FILES = [
    (".claude/settings.json", "claude"),
    (".claude/settings.local.json", "claude"),
    (os.path.join(CLAUDE_HOME, "settings.json"), "claude"),
    (".codex/config.toml", "codex"),
    (os.path.join(CODEX_HOME, "config.toml"), "codex"),
    (os.path.join(HOME, ".copilot", "settings.json"), "copilot"),
]

# Token shapes with a fixed prefix or structure, so a match is rarely anything but a credential.
# A reference such as $TOKEN or ${TOKEN} never matches.
SECRETS = [
    ("private key", r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    ("AWS access key", r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    ("GitHub token", r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b"),
    ("Slack token", r"\bxox[abprs]-[A-Za-z0-9-]{10,}"),
    ("Google API key", r"\bAIza[0-9A-Za-z_-]{35}\b"),
    ("Anthropic or OpenAI key",
     r"\bsk-(?:(?:ant|proj|svcacct|admin)-[A-Za-z0-9_-]{20,}|(?=[A-Za-z]{0,40}\d)[A-Za-z0-9]{32,})"),
    ("Stripe key", r"\b[rs]k_live_[A-Za-z0-9]{16,}"),
    ("npm token", r"\bnpm_[A-Za-z0-9]{36}\b"),
    ("Hugging Face token", r"\bhf_[A-Za-z0-9]{30,}\b"),
    ("JWT", r"\beyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"),
    ("bearer token", r"\bBearer\s+[A-Za-z0-9._~+/=-]{24,}"),
    ("URL with a password", r"\b[a-z][a-z0-9+.-]{1,20}://[^\s:@/\"'${}]+:[^\s@/\"'${}]{3,}@[^\s/\"']+"),
]
SECRETS = [(label, re.compile(pattern)) for label, pattern in SECRETS]

# curl or wget output piped into a shell, within 200 characters (one command, not a whole file).
PIPE_TO_SHELL = re.compile(r"\b(?:curl|wget)\b[^|\n]{0,200}\|\s*(?:sudo\s+)?(?:ba|z|da)?sh\b")

CODEX_RISKS = {
    ("approval_policy", "never"):
        "Codex runs every command without asking -- fine if chosen; else use on-request",
    ("sandbox_mode", "danger-full-access"):
        "Codex runs without a sandbox -- fine if chosen; else use workspace-write",
}
CODEX_LINE = re.compile(r"""(approval_policy|sandbox_mode)\s*=\s*["']([\w-]+)["']""")


def shown(path):
    return "~" + path[len(HOME):] if path.startswith(HOME + os.sep) else path


def tracked(path):
    """True when git tracks this project-relative path in the current repo."""
    if os.path.isabs(path):
        return False
    try:
        return subprocess.run(["git", "ls-files", "--error-unmatch", "--", path],
                              capture_output=True).returncode == 0
    except OSError:  # no git: treat as untracked
        return False


def json_strings(node, where=""):
    """(key path, string) for every string value in a parsed JSON document."""
    if isinstance(node, dict):
        for key, value in node.items():
            yield from json_strings(value, f"{where}.{key}" if where else str(key))
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from json_strings(value, f"{where}[{i}]")
    elif isinstance(node, str):
        yield where, node


def claude_keys(data):
    """Claude Code settings that pre-approve every tool call of a kind."""
    perms = data.get("permissions") if isinstance(data.get("permissions"), dict) else {}
    if perms.get("defaultMode") == "bypassPermissions":
        yield ("permissions.defaultMode is bypassPermissions: Claude runs every tool without asking"
               " -- fine if chosen; else use default or acceptEdits")
    allow = perms.get("allow") if isinstance(perms.get("allow"), list) else []
    for rule in allow:
        if rule in ("Bash", "Bash(*)"):
            yield (f"permissions.allow has {rule}: every shell command runs without asking"
                   " -- narrow it to prefixes such as Bash(git status:*)")
        if rule in ("WebFetch", "WebFetch(*)"):
            yield (f"permissions.allow has {rule}: every web fetch runs without asking"
                   " -- narrow it to WebFetch(domain:NAME)")
    if data.get("enableAllProjectMcpServers") is True:
        yield ("enableAllProjectMcpServers is true: MCP servers in any repo's .mcp.json start without"
               " asking -- list trusted ones in enabledMcpjsonServers instead")


def scan(path, kind):
    """Finding lines for one file."""
    out = []
    name = shown(path)
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError as e:
        return [f"⚠️ {name}: could not read ({e.strerror})"]

    pieces = None  # (where, text) pairs the text checks run over
    if kind in ("claude", "copilot"):
        try:
            data = json.loads(text) if text.strip() else {}
        except json.JSONDecodeError as e:
            out.append(f"⚠️ {name}: not valid JSON (line {e.lineno}: {e.msg})"
                       " -- the CLI may be ignoring this file; fix the syntax")
        else:
            if isinstance(data, dict):
                if kind == "claude":
                    out += [f"⚠️ {name}: {finding}" for finding in claude_keys(data)]
                pieces = [(f"{name} {where}", value) for where, value in json_strings(data)]
    if kind == "codex":
        section = "top level"
        for n, line in enumerate(text.splitlines(), 1):
            stripped = line.split("#", 1)[0].strip()
            if stripped.startswith("["):
                section = stripped
                continue
            m = CODEX_LINE.match(stripped)
            if m and (m.group(1), m.group(2)) in CODEX_RISKS:
                out.append(f"⚠️ {name}:{n} ({section}): {m.group(1)} = \"{m.group(2)}\": "
                           f"{CODEX_RISKS[(m.group(1), m.group(2))]}")
    if pieces is None:  # TOML, or JSON that did not parse
        pieces = [(f"{name}:{n}", line) for n, line in enumerate(text.splitlines(), 1)]

    is_tracked = tracked(path)
    for where, value in pieces:
        for label, pattern in SECRETS:
            if pattern.search(value):
                if is_tracked:
                    out.append(f"🔴 {where}: holds a secret ({label}) in a file git tracks"
                               " -- remove it from the file and history, and rotate it")
                else:
                    out.append(f"⚠️ {where}: holds a secret ({label})"
                               " -- move it to an environment variable or keychain")
                break  # one secret label per value is enough
        if PIPE_TO_SHELL.search(value):
            out.append(f"⚠️ {where}: pipes downloaded code into a shell"
                       " -- save the script, read it, and run the saved copy")
    return out


def main():
    seen = set()
    read = 0
    findings = []
    for path, kind in FILES:
        if not os.path.isfile(path) or os.path.realpath(path) in seen:
            continue
        seen.add(os.path.realpath(path))
        read += 1
        findings += scan(path, kind)
    if findings:
        print("\n".join(findings))
    elif read:
        print(f"✅ agent settings: nothing risky in {read} file(s)")
    else:
        print("n/a agent settings: no Claude Code, Codex or Copilot CLI settings files found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
