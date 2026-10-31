"""P1 throwaway: run the workflow suite once and map each test (and subtest) to the script
lines and branches it reaches. Usage: python3 run.py <tests-dir> <out-dir>"""
import contextlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent

if os.environ.get("COVMAP_CHILD"):
    import unittest
    import sitecustomize as cov

    real_subtest = unittest.TestCase.subTest

    @contextlib.contextmanager
    def subtest(self, msg=None, **params):
        outer = os.environ["COVMAP_TEST"]
        cov.flush(outer)
        os.environ["COVMAP_TEST"] = f"{outer} [{msg or ''}{params}]"
        try:
            with real_subtest(self, msg, **params):
                yield
        finally:
            cov.flush(os.environ["COVMAP_TEST"])
            os.environ["COVMAP_TEST"] = outer

    unittest.TestCase.subTest = subtest

    class Result(unittest.TextTestResult):
        def startTest(self, test):
            cov.flush("setup")
            os.environ["COVMAP_TEST"] = test.id()
            super().startTest(test)

        def stopTest(self, test):
            cov.flush(test.id())
            os.environ["COVMAP_TEST"] = "between"
            super().stopTest(test)

    suite = unittest.defaultTestLoader.discover(sys.argv[1])
    ok = unittest.TextTestRunner(resultclass=Result, verbosity=1).run(suite).wasSuccessful()
    sys.exit(0 if ok else 1)

tests, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
shutil.rmtree(out, ignore_errors=True)
out.mkdir(parents=True)
env = dict(os.environ, COVMAP_CHILD="1", COVMAP_DIR=str(out), COVMAP_SRC=str(tests.parent),
           COVMAP_TEST="start", PYTHONPATH=os.pathsep.join([str(HERE), os.environ.get("PYTHONPATH", "")]))
code = subprocess.run([sys.executable, __file__, str(tests)], env=env).returncode
sys.exit(code)
