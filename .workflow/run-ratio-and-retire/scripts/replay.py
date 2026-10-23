"""Replay the run gate over P1's cohort. Read-only; usage: replay.py REPO [REPO...]."""
import importlib.util
from pathlib import Path
import re
import sys

source = Path(__file__).resolve().parents[3] / '.github/skills/workflow/scripts/check-run.py'
spec = importlib.util.spec_from_file_location('check_run', source)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
count = flagged = 0
for repo in sys.argv[1:]:
    for path in sorted(Path(repo).glob('.workflow/*/plan.md')):
        doc = checker.Doc(str(path))
        if not re.match(r'2026-10-(1[7-9]|2\d)', doc.header().get('Created', '')):
            continue
        tickets = checker.parse_tickets(doc)
        if not any((checker.field(t, 'Status')[1] or '').startswith('done @ ') for t in tickets):
            continue
        rep = checker.Report(repo)
        checker.check_run_ratio(doc, tickets, rep)
        count += 1
        flagged += bool(rep.errors or rep.warnings)
        print(f'{Path(repo).name}/{path.parent.name}: ' + ('; '.join(rep.errors + rep.warnings) or 'pass'))
print(f'{count} runs; {flagged} flagged')
