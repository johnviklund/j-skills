#!/usr/bin/env python3
"""Print mechanical corrections from local CLI transcripts. Python 3 + git; writes nothing."""
import argparse
from collections import Counter, defaultdict
import json
import os
import shlex
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


def command_head(command):
    try:
        parts = shlex.split(command)
    except ValueError:
        parts = command.split()
    # Ignore a leading directory change when identifying the command being denied.
    if parts and parts[0] == 'cd' and '&&' in parts:
        parts = parts[parts.index('&&') + 1:]
    return parts[0] if parts else 'no command'


def codex(rows):
    if any(r.get('type') == 'session_meta' and 'subagent' in r.get('payload', {}).get('source', '')
           for r in rows):
        return
    tool, pending = 'no tool', None
    for row in rows:
        data = row.get('payload', {})
        if row.get('type') == 'response_item' and data.get('type') == 'custom_tool_call':
            tool = data.get('name', 'no tool')
        if row.get('type') != 'event_msg':
            continue
        if data.get('type') == 'turn_aborted' and data.get('reason') == 'interrupted':
            pending = f'interrupt · {tool}'
            yield pending, None
        item = data.get('item', {})
        if data.get('type') == 'item_completed' and item.get('type') == 'UserMessage':
            if pending:
                yield pending, ' '.join(b.get('text', '') for b in item.get('content', []))
                pending = None
            tool = 'no tool'


def copilot(rows):
    requests, pending = {}, None
    for row in rows:
        data = row.get('data', {})
        if row.get('type') == 'permission.requested':
            request = data.get('permissionRequest', {})
            commands = request.get('commands', [])
            requests[data.get('requestId')] = ('denial · ' + request.get('kind', 'unknown') +
                (' · ' + commands[0]['identifier'] if commands else ''))
        if (row.get('type') == 'permission.completed' and
                data.get('result', {}).get('kind', '').startswith('denied') and
                data.get('decisionSource') != 'unattended_fallback'):
            pending = requests.get(data.get('requestId'))
            if pending:
                yield pending, None
        if row.get('type') == 'user.message' and pending:
            yield pending, data.get('content', '')
            pending = None


def claude(rows):
    tool = 'no tool'
    pending = None
    tools = {}
    for row in rows:
        if row.get('isSidechain'):
            continue
        content = row.get('message', {}).get('content', [])
        if row.get('type') == 'assistant':
            for block in content if isinstance(content, list) else []:
                if block.get('type') == 'tool_use':
                    tool = block.get('name', 'no tool')
                    tools[block.get('id')] = (tool, block.get('input', {}))
        if row.get('type') != 'user' or row.get('isMeta'):
            continue
        for block in content if isinstance(content, list) else []:
            result = block.get('content', '')
            if (block.get('type') == 'tool_result' and isinstance(result, str) and
                    result.startswith("The user doesn't want to proceed")):
                name, inputs = tools.get(block.get('tool_use_id'), (tool, {}))
                pending = f'denial · {name}'
                if name == 'Bash':
                    pending += ' · ' + command_head(inputs.get('command', ''))
                yield pending, None
                if 'the user said:' in result:
                    yield pending, result.split('the user said:', 1)[1].strip()
                    pending = None
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
            cwds = [r.get('cwd') if store == 'claude' else
                    r.get('payload', {}).get('cwd') if store == 'codex' and r.get('type') == 'session_meta' else
                    r.get('data', {}).get('context', {}).get('cwd') if store == 'copilot' and r.get('type') == 'session.start'
                    else None for r in rows]
            cwd = next((c for c in cwds if c), '')
            if not args.all_repos and (not cwd or not in_repo(cwd, root)):
                continue
            total += 1
            events = {'claude': claude, 'codex': codex, 'copilot': copilot}[store](rows)
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
