#!/usr/bin/env python3
"""Print mechanical corrections from local CLI transcripts. Python 3 + git; writes nothing."""
import argparse
from collections import Counter, defaultdict
import json
import os
from pathlib import Path
import subprocess
import time


def records(path):
    try:
        with path.open(encoding='utf-8', errors='replace') as source:
            for line in source:
                try:
                    row = json.loads(line)
                except ValueError:
                    continue  # A running session may have a partial final record.
                if isinstance(row, dict):
                    yield row
    except OSError:
        return


def repo_root():
    result = subprocess.run(['git', 'rev-parse', '--git-common-dir'], capture_output=True, text=True)
    return (Path(result.stdout.strip()).resolve().parent if result.returncode == 0
            else Path.cwd().resolve())


def in_repo(cwd, root):
    path = Path(cwd).resolve()
    return path == root or root / '.worktrees' in path.parents


def claude(rows):
    tool = 'no tool'
    pending = None
    for row in rows:
        if row.get('isSidechain'):
            continue
        content = row.get('message', {}).get('content', [])
        if row.get('type') == 'assistant':
            for block in content if isinstance(content, list) else []:
                if block.get('type') == 'tool_use':
                    tool = block.get('name', 'no tool')
        if row.get('type') != 'user' or row.get('isMeta'):
            continue
        texts = ([content] if isinstance(content, str) else
                 [b.get('text', '') for b in content if b.get('type') == 'text'])
        for text in texts:
            if text.startswith('[Request interrupted by user'):
                pending = f'interrupt · {tool}'
                yield pending, None
            elif text and not text.startswith('<'):
                if pending:
                    yield pending, text
                    pending = None
                tool = 'no tool'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--days', type=int, default=14)  # Two weeks is the default review window.
    parser.add_argument('--all-repos', action='store_true')
    args = parser.parse_args()
    home = Path.home()
    stores = [('claude', Path(os.environ.get('CLAUDE_CONFIG_DIR') or home / '.claude') / 'projects', '*/*.jsonl'),
              ('codex', Path(os.environ.get('CODEX_HOME') or home / '.codex') / 'sessions', '*/*/*/rollout-*.jsonl'),
              ('copilot', home / '.copilot/session-state', '*/events.jsonl')]
    counts = Counter()
    sessions = defaultdict(set)
    redirects, read = [], []
    root = repo_root()
    cutoff = time.time() - args.days * 86400
    for store, folder, pattern in stores:
        total = 0
        for path in sorted(folder.glob(pattern)):
            try:
                if path.stat().st_mtime < cutoff:
                    continue
            except OSError:
                continue
            rows = list(records(path))
            cwd = next((r['cwd'] for r in rows if r.get('cwd')), '')
            if not args.all_repos and (not cwd or not in_repo(cwd, root)):
                continue
            total += 1
            events = claude(rows) if store == 'claude' else []
            for key, text in events:
                if text is None:
                    counts[key] += 1
                    sessions[key].add((store, str(path)))
                else:
                    # One terminal line per redirect, capped at the brief's 200 characters.
                    redirects.append(f'- {store} · {key}: {text[:200].replace(chr(10), " ").replace(chr(13), " ")}')
        read.append(f'{store} {total} file(s)' if folder.is_dir() else f'{store} missing')
    print('stores: ' + ' · '.join(read))
    print('repeats:')
    for key in sorted(counts, key=lambda k: (-len(sessions[k]), -counts[k], k)):
        if len(sessions[key]) >= 2:
            print(f'- {key} · {len(sessions[key])} sessions · {counts[key]} times')
    print(f'once: {sum(len(sessions[k]) == 1 for k in counts)} key(s)')
    print('redirects:')
    print('\n'.join(redirects), end='\n' if redirects else '')


if __name__ == '__main__':
    main()
