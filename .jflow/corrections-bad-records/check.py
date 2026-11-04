"""Proof check: run corrections.py on one malformed transcript beside two good ones."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

SCRIPT = Path('.github/skills/checkup/scripts/corrections.py').resolve()
BAD = {
    'null-message': lambda cwd: [dict(type='user', cwd=cwd, message=None)],
    'string-block': lambda cwd: [dict(type='user', cwd=cwd, message={'content': ['loose text']})],
    'null-command': lambda cwd: [
        dict(type='assistant', cwd=cwd, message={'content': [
            dict(type='tool_use', id='t1', name='Bash', input={'command': None})]}),
        dict(type='user', cwd=cwd, message={'content': [
            dict(type='tool_result', tool_use_id='t1',
                 content="The user doesn't want to proceed with this tool use.")]})],
}


def write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(''.join(json.dumps(row) + '\n' for row in rows))


with tempfile.TemporaryDirectory() as tmp:
    home, repo = Path(tmp) / 'home', Path(tmp) / 'repo'
    repo.mkdir()
    subprocess.run(['git', 'init', '-q', str(repo)], check=True)
    cwd = str(repo.resolve())
    good = [dict(type='assistant', cwd=cwd, message={'content': [
                dict(type='tool_use', id='t1', name='Bash', input={'command': 'rm -rf x'})]}),
            dict(type='user', cwd=cwd, message={'content': [
                dict(type='tool_result', tool_use_id='t1',
                     content="The user doesn't want to proceed with this tool use.")]})]
    projects = home / '.claude/projects/r'
    write(projects / 'a-good.jsonl', good)
    write(projects / 'b-bad.jsonl', BAD[sys.argv[1]](cwd))
    write(projects / 'c-good.jsonl', good)
    env = {k: v for k, v in os.environ.items() if k not in ('CLAUDE_CONFIG_DIR', 'CODEX_HOME')}
    run = subprocess.run([sys.executable, str(SCRIPT)], cwd=repo, env=dict(env, HOME=str(home)),
                         capture_output=True, text=True)
    print(run.stdout, run.stderr[-300:], sep='\n')
    ok = run.returncode == 0 and 'Traceback' not in run.stderr and \
        '2 sessions' in run.stdout and 'denial · Bash' in run.stdout
    print('PASS' if ok else f'FAIL exit {run.returncode}')
    sys.exit(0 if ok else 1)
