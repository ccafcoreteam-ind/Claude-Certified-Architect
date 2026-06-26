"""
Domain 3 · Task 3.5 — Iterative refinement techniques.

THE BIG IDEA
============
Four techniques for progressively improving Claude's output:

  1. CONCRETE input/output examples (2-3): the most effective way to communicate a
     transformation when prose is interpreted inconsistently. Show the exact before -> after.
  2. TEST-DRIVEN iteration: write the test suite first (expected behavior, edge cases,
     performance), then iterate by sharing test FAILURES — precise, objective feedback.
  3. THE INTERVIEW PATTERN: have Claude interview YOU before implementing in an unfamiliar
     domain — surfaces considerations you hadn't anticipated (cache invalidation? failure modes?).
  4. BATCH interacting fixes; SEQUENCE independent ones: if issues interact, describe them
     ALL in one detailed message; independent issues can be fixed one at a time.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause, analogy, pitfall


def message_strategy(issues):
    """issues: list of (name, interacts_with_others?)"""
    interacting = [n for n, inter in issues if inter]
    independent = [n for n, inter in issues if not inter]
    plan = []
    if interacting:
        plan.append(f"ONE detailed message describing together: {interacting} "
                    "(so the fix accounts for interactions)")
    for n in independent:
        plan.append(f"Separate message: {n} (independent, fix one at a time)")
    return plan


def main():
    banner("Domain 3 · Task 3.5", "Iterative refinement techniques")
    concept("Domain 3: Claude Code Configuration & Workflows (20%)",
            "Task 3.5 — Apply iterative refinement techniques for progressive improvement",
            "Examples > prose; tests as feedback; interview; batch-vs-sequence")

    h1("1) Concrete input/output examples beat prose")
    wrong('"Make the dates consistent." (vague — interpreted differently each run)')
    right("Show 2-3 exact transformations:")
    code('"3/4/25"            -> "2025-03-04"\n'
         '"March 4th, 2025"   -> "2025-03-04"\n'
         '"04.03.2025" (EU)   -> "2025-03-04"', "before -> after")

    pause("test-driven")
    rule()
    h1("2) Test-driven iteration")
    note("Write the suite FIRST (expected behavior, edge cases, performance). Then iterate "
         "by pasting the FAILURES — they become precise, objective feedback.")
    code("FAILED test_handles_null_amount: expected null, got 0.0\n"
         "-> 'Fix null handling so missing amounts return null, not 0.0'", "failure as feedback")

    rule()
    h1("3) The interview pattern")
    right("Before building in an unfamiliar domain, ask Claude to interview YOU: "
          "'What's the cache invalidation strategy? What are the failure modes? "
          "What happens on partial writes?' — it surfaces considerations you'd have missed.")

    pause("batch vs sequence")
    rule()
    h1("4) Batch interacting fixes; sequence independent ones")
    issues = [
        ("pagination off-by-one", True),
        ("the sort order depends on pagination", True),
        ("rename a log label", False),
    ]
    for step in message_strategy(issues):
        kv("  plan", step)
    note("Interacting bugs fixed separately can ping-pong; describing them together lets "
         "one fix account for the interaction.")

    rule()
    h1("Plain-language analogy & the common confusion")
    analogy("Teaching by showing, not telling. 'Make the dates consistent' is vague; three before-to-after pairs are a worked example the model can copy exactly — like demonstrating a knot instead of describing it.")
    pitfall('When results are inconsistent, learners add MORE prose instructions. Prose is interpreted differently each run; 2-3 concrete input-to-output examples pin the behavior down far better.')

    tip("Show, don't describe (2-3 examples). Tests-as-feedback. Interview before building "
        "in unfamiliar areas. Interacting issues -> one message; independent -> sequence.")


if __name__ == "__main__":
    main()
