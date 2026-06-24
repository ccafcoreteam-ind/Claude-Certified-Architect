#!/usr/bin/env python3
"""
scenarios/run.py — launcher for the six functional scenario apps.

  python3 scenarios/run.py                 # list the scenarios
  python3 scenarios/run.py 1               # run scenario 1's app (scripted demo)
  python3 scenarios/run.py 1 -i            # run it interactively
  python3 scenarios/run.py 6 "Pd $20 to Acme on 3/4/25"   # pass args through

Each scenario's working app lives at scenarios/scenarioN_*/app.py. The original teaching
walkthroughs (the *_*.py files) are still there and unchanged.
"""
import sys, glob, os, runpy, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
APPS = {}
for d in sorted(glob.glob(str(ROOT / "scenario*"))):
    name = os.path.basename(d)
    n = name[len("scenario")]
    app = os.path.join(d, "app.py")
    if os.path.isfile(app):
        APPS[n] = (name, app)

TITLES = {
    "1": "Customer Support Resolution Agent — chat with a gated, hook-guarded agent",
    "2": "Code Generation — plan-vs-direct + config-scope advisor",
    "3": "Multi-Agent Research — decompose a topic, synthesize a cited report",
    "4": "Developer Productivity — real Glob/Grep/Read codebase explorer",
    "5": "Claude Code for CI/CD — static reviewer with structured JSON findings",
    "6": "Structured Data Extraction — parse documents into validated JSON",
}


def usage():
    print("Functional scenario apps:\n")
    for n in sorted(APPS):
        print(f"  {n}  {TITLES.get(n, APPS[n][0])}")
    print("\nUsage: python3 scenarios/run.py <1-6> [-i] [args...]")
    print("Example: python3 scenarios/run.py 1 -i")


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help", "list"):
        usage(); return
    n = args[0]
    if n not in APPS:
        print(f"unknown scenario {n!r}\n"); usage(); sys.exit(1)
    _, app = APPS[n]
    sys.argv = [app] + args[1:]
    runpy.run_path(app, run_name="__main__")


if __name__ == "__main__":
    main()
