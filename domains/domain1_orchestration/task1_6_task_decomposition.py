"""
Domain 1 · Task 1.6 — Task decomposition strategies.

THE BIG IDEA
============
Two decomposition styles, matched to two kinds of work:

  PROMPT CHAINING (fixed sequential pipeline)
    A pre-defined sequence of focused passes. Best for PREDICTABLE multi-aspect work where
    the steps are known up front. Example: code review = analyze each file individually,
    then run ONE cross-file integration pass.

  DYNAMIC ADAPTIVE DECOMPOSITION
    Generate the next subtasks based on what each step discovers. Best for OPEN-ENDED
    investigation where you can't know the steps up front. Example: "add comprehensive
    tests to a legacy codebase" — map structure, find high-impact areas, build a plan that
    adapts as dependencies surface.

Why split big reviews into passes? ATTENTION DILUTION. Asking the model to review 14 files
at once yields uneven depth and contradictory findings (this is sample Q12).
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause


def prompt_chaining_review(files):
    """Fixed pipeline: per-file local pass, then one integration pass."""
    steps = [f"Pass {i+1}: local analysis of {f}" for i, f in enumerate(files)]
    steps.append(f"Pass {len(files)+1}: cross-file integration analysis (all {len(files)} files)")
    return steps


def adaptive_plan(seed_discovery):
    """Dynamic: each discovery spawns the next subtask."""
    plan = ["Map repository structure"]
    if "no tests in payments/" in seed_discovery:
        plan.append("payments/ is high-impact + untested -> prioritize it")
        plan.append("Discovered payments/ imports billing/ -> add billing/ to plan")
        plan.append("Generate tests for payments/ then billing/, adapting as deps surface")
    return plan


def main():
    banner("Domain 1 · Task 1.6", "Task decomposition — chaining vs adaptive")
    concept("Domain 1: Agentic Architecture & Orchestration (27%)",
            "Task 1.6 — Task decomposition strategies",
            "Fixed pipeline (known steps) vs dynamic plan (steps emerge)")

    h1("Prompt chaining — when the steps are known in advance")
    files = ["auth.py", "orders.py", "refunds.py"]
    for s in prompt_chaining_review(files):
        kv("  step", s)
    note("Predictable, multi-aspect work. Each pass gets the model's FULL attention on a "
         "small scope; the final pass catches cross-file issues.")

    pause("adaptive decomposition")
    rule()
    h1("Dynamic adaptive decomposition — when steps emerge from findings")
    for s in adaptive_plan("no tests in payments/"):
        kv("  step", s)
    note("Open-ended investigation: you literally cannot write the step list up front "
         "because each discovery changes the next move.")

    rule()
    h1("Why split big reviews into passes? Attention dilution.")
    wrong("Reviewing 14 files in ONE pass: detailed feedback for some files, superficial "
          "for others, obvious bugs missed, and CONTRADICTORY findings (flag a pattern in "
          "one file, approve identical code in another).")
    right("Per-file passes for consistent local depth + ONE integration pass for cross-file "
          "issues. (This is sample Q12.)")

    tip("Match the pattern to the work: predictable/multi-aspect -> prompt chaining; "
        "open-ended/unknown-steps -> dynamic adaptive. Bigger context windows do NOT fix "
        "attention dilution — splitting passes does.")


if __name__ == "__main__":
    main()
