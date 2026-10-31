"""P1 throwaway: record the script lines and branches a Python process runs.

Active only when COVMAP_DIR is set. Each process writes COVMAP_DIR/<pid>.json at exit with the
test id it inherited in COVMAP_TEST. Only files directly in COVMAP_SRC are recorded.
"""
import atexit
import json
import os
import sys

OUT, SRC = os.environ.get("COVMAP_DIR"), os.environ.get("COVMAP_SRC")
if OUT and SRC:
    mon, E = sys.monitoring, sys.monitoring.events
    TOOL = mon.COVERAGE_ID
    lines, branches = set(), set()

    def target(code):
        return os.path.dirname(code.co_filename) == SRC

    def line_of(code, offset):
        for start, end, line in code.co_lines():
            if start <= offset < end:
                return line
        return None

    def on_line(code, line):
        if not target(code):
            return mon.DISABLE
        lines.add((os.path.basename(code.co_filename), line))
        return mon.DISABLE

    def on_branch(kind):
        def callback(code, src, dst):
            if not target(code):
                return mon.DISABLE
            branches.add((os.path.basename(code.co_filename), line_of(code, src), src, dst, kind))
            return mon.DISABLE
        return callback

    mon.use_tool_id(TOOL, "covmap")
    mon.register_callback(TOOL, E.LINE, on_line)
    mon.register_callback(TOOL, E.BRANCH_LEFT, on_branch("L"))
    mon.register_callback(TOOL, E.BRANCH_RIGHT, on_branch("R"))
    mon.set_events(TOOL, E.LINE | E.BRANCH_LEFT | E.BRANCH_RIGHT)

    count = [0]

    def flush(test=None):
        """Write what ran so far under `test` (default: the inherited id), then start afresh."""
        if lines or branches:
            count[0] += 1
            path = os.path.join(OUT, f"{os.getpid()}-{count[0]}.json")
            with open(path, "w") as f:
                json.dump({"test": test or os.environ.get("COVMAP_TEST", "?"), "lines": sorted(lines),
                           "branches": sorted(branches)}, f)
        lines.clear()
        branches.clear()
        mon.restart_events()

    atexit.register(flush)
