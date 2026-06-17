#!/usr/bin/env python3
"""
run_all.py — the teaching playlist / smoke test for the whole codebase.

Usage:
  python3 run_all.py                # run EVERYTHING, top to bottom (non-stop)
  python3 run_all.py domain1        # run a domain's demos
  python3 run_all.py scenarios      # run all 6 scenarios
  python3 run_all.py scenario3      # run one scenario
  python3 run_all.py exam           # the 12 sample questions + cheat sheet
  python3 run_all.py --list         # list everything runnable
  python3 run_all.py --check        # smoke-test every file, print PASS/FAIL only

In a live teaching session, drop CCARCH_NONSTOP and run individual files instead so the
[press ENTER] pauses let you talk between steps:
  python3 domains/domain1_orchestration/task1_1_agentic_loop.py
"""

import os
import sys
import glob
import runpy
import io
import contextlib
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent


def discover():
    groups = {}
    for d in sorted(glob.glob(str(ROOT / "domains" / "domain*"))):
        name = pathlib.Path(d).name.split("_")[0]   # domain1..domain5
        groups[name] = sorted(glob.glob(os.path.join(d, "task*.py")))
    for d in sorted(glob.glob(str(ROOT / "scenarios" / "scenario*"))):
        name = pathlib.Path(d).name.split("_")[0]   # scenario1..scenario6
        groups[name] = sorted(glob.glob(os.path.join(d, "*.py")))
    groups["exam"] = [str(ROOT / "exam" / "sample_questions.py"),
                      str(ROOT / "exam" / "prep_exercises.py"),
                      str(ROOT / "exam" / "cheatsheet.py")]
    return groups


def select(groups, arg):
    if arg in (None, "all"):
        order = (["domain%d" % i for i in range(1, 6)]
                 + ["scenario%d" % i for i in range(1, 7)] + ["exam"])
        files = []
        for g in order:
            files += groups.get(g, [])
        return files
    if arg == "domains":
        return sum((groups[g] for g in groups if g.startswith("domain")), [])
    if arg == "scenarios":
        return sum((groups[g] for g in groups if g.startswith("scenario")), [])
    if arg in groups:
        return groups[arg]
    # allow a path fragment
    matches = [f for fs in groups.values() for f in fs if arg in f]
    return matches


def run_file(path):
    sys.argv = [path]
    runpy.run_path(path, run_name="__main__")


def main():
    args = sys.argv[1:]
    groups = discover()

    if args and args[0] == "--list":
        for g, files in groups.items():
            print(g)
            for f in files:
                print("   ", os.path.relpath(f, ROOT))
        return

    if args and args[0] == "--check":
        os.environ["CCARCH_NONSTOP"] = "1"
        os.environ["NO_COLOR"] = "1"
        ok = True
        for f in select(groups, "all"):
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    run_file(f)
                print(f"PASS  {os.path.relpath(f, ROOT)}")
            except Exception as exc:  # noqa: BLE001
                ok = False
                print(f"FAIL  {os.path.relpath(f, ROOT)}  -> {exc}")
        print("\n" + ("ALL PASS" if ok else "SOME FAILED"))
        sys.exit(0 if ok else 1)

    # normal run: non-stop so the whole playlist flows
    os.environ.setdefault("CCARCH_NONSTOP", "1")
    arg = args[0] if args else "all"
    files = select(groups, arg)
    if not files:
        print(f"Nothing matched {arg!r}. Try --list.")
        sys.exit(1)
    for f in files:
        run_file(f)
        print("\n")


if __name__ == "__main__":
    main()
