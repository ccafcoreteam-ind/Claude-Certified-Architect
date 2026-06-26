"""
Domain 3 · Task 3.4 — Plan mode vs direct execution.

THE BIG IDEA
============
  PLAN MODE: complex tasks — large-scale changes, multiple valid approaches, architectural
  decisions, multi-file modifications. Explore and DESIGN before changing anything.
  Examples: monolith -> microservices; a library migration touching 45+ files; choosing
  between integration approaches with different infrastructure needs.

  DIRECT EXECUTION: simple, well-scoped changes you already understand.
  Examples: a single-file bug fix with a clear stack trace; adding one date-validation
  conditional.

Plan mode prevents costly rework by surfacing dependencies BEFORE you commit. If the
requirements already STATE the complexity, "start direct and switch to plan mode if it
gets hard" is a TRAP (sample Q5) — the complexity isn't hypothetical.

The Explore subagent isolates verbose discovery output and returns summaries, preserving
the main conversation's context during multi-phase tasks.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause, analogy, pitfall


def recommend(files_touched, multiple_approaches, architectural, clear_scope):
    if architectural or multiple_approaches or files_touched >= 5:
        return "PLAN MODE", "Complexity is stated up front; explore & design before changing."
    if clear_scope and files_touched <= 1:
        return "DIRECT EXECUTION", "Simple, well-understood, single-file change."
    return "PLAN MODE (when unsure)", "Cheaper to plan than to rework."


TASKS = [
    ("Restructure monolith into microservices", dict(files_touched=40, multiple_approaches=True,
        architectural=True, clear_scope=False)),
    ("Library migration touching 45+ files", dict(files_touched=45, multiple_approaches=True,
        architectural=False, clear_scope=False)),
    ("Fix a single-file bug with a clear stack trace", dict(files_touched=1,
        multiple_approaches=False, architectural=False, clear_scope=True)),
    ("Add one date-validation conditional", dict(files_touched=1, multiple_approaches=False,
        architectural=False, clear_scope=True)),
]


def main():
    banner("Domain 3 · Task 3.4", "Plan mode vs direct execution")
    concept("Domain 3: Claude Code Configuration & Workflows (20%)",
            "Task 3.4 — Determine when to use plan mode vs direct execution",
            "Architectural/multi-file -> plan; small known fix -> direct")

    h1("A recommender you can reason through")
    for name, feats in TASKS:
        mode, why = recommend(**feats)
        h2(name)
        kv("  signals", ", ".join(f"{k}={v}" for k, v in feats.items()))
        right(f"{mode} — {why}")

    pause("the trap")
    rule()
    h1("The trap answer (sample Q5)")
    wrong("'Start with direct execution and switch to plan mode if it gets hard.' "
          "The complexity is ALREADY stated in the requirements — it's not hypothetical.")
    wrong("'Use direct execution with comprehensive upfront instructions.' Assumes you "
          "already know the right structure without exploring the code.")
    right("Enter plan mode: explore the codebase, understand dependencies, design the "
          "approach BEFORE making changes.")

    rule()
    h1("Two more facts")
    note("- The EXPLORE subagent isolates verbose discovery output and returns summaries, "
         "preserving the main conversation's context during multi-phase tasks.")
    note("- COMBINE the modes: plan mode for investigation, then direct execution to "
         "implement the agreed plan.")

    rule()
    h1("Plain-language analogy & the common confusion")
    analogy('Plan mode is measuring twice before you cut. For a quick trim (a one-line fix) you just cut; for rebuilding the staircase (touches 40 files) you measure, sketch, and check the load-bearing walls first.')
    pitfall("The trap answer is 'start coding and switch to plan mode if it gets hard.' If the prompt already states the complexity (dozens of files, service boundaries), the difficulty is not hypothetical — plan now.")

    tip("If the prompt states the complexity (dozens of files, service boundaries), it's "
        "plan mode NOW — not 'maybe later'.")


if __name__ == "__main__":
    main()
