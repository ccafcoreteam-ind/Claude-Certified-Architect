"""
Domain 4 · Task 4.1 — Explicit criteria to reduce false positives.

THE BIG IDEA
============
Vague instructions produce vague judgment. "Check that comments are accurate" invites
noise; "flag comments only when the claimed behavior CONTRADICTS the actual code behavior"
is testable and precise.

  * "Be conservative" / "only report high-confidence findings" does NOT work — general
    modifiers fail to improve precision. SPECIFIC CATEGORICAL criteria do: report bugs and
    security issues; skip minor style and local patterns.
  * FALSE POSITIVES are trust killers: one noisy category undermines confidence in the
    accurate categories too. Tactical move: temporarily DISABLE the noisy category while
    you improve its prompt.
  * SEVERITY needs ANCHORS: define each level with concrete code examples.

Analogy: a guard told "report anything suspicious" floods you with junk. Told "report
propped-open doors after 8pm and unbadged people in the server room," reports become rare
and worth acting on.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause


def main():
    banner("Domain 4 · Task 4.1", "Explicit criteria reduce false positives")
    concept("Domain 4: Prompt Engineering & Structured Output (20%)",
            "Task 4.1 — Design prompts with explicit criteria to improve precision and reduce false positives",
            "Specific categorical criteria > vague modifiers")

    h1("Vague vs precise instruction")
    wrong('"Check that comments are accurate."  (invites noise — every comment is a maybe)')
    right('"Flag a comment ONLY when the claimed behavior contradicts the actual code '
          'behavior."  (testable, precise)')

    pause("why 'be conservative' fails")
    rule()
    h1("Why 'be conservative' fails")
    wrong('"Only report high-confidence findings" / "be conservative" — general modifiers '
          "don't move precision. The model has no concrete boundary to apply.")
    right("Specific CATEGORICAL criteria: REPORT bugs and security issues; SKIP minor style "
          "and purely-local patterns. Now the boundary is decidable.")

    rule()
    h1("False positives are trust killers")
    note("If one category (say, 'style') is noisy, developers start ignoring ALL findings — "
         "even the accurate bug/security categories.")
    right("Tactical move: temporarily DISABLE the noisy category while you improve its "
          "prompt, so it doesn't poison trust in the rest.")

    pause("severity anchors")
    rule()
    h1("Severity needs concrete anchors")
    code("CRITICAL: remote code execution, auth bypass, data loss\n"
         "  e.g., `eval(user_input)`; SQL built by string concatenation\n"
         "HIGH:     crash on common input, unhandled error path\n"
         "  e.g., indexing a list without a length check on user data\n"
         "LOW:      naming, formatting (often SKIP in automated review)",
         "severity rubric with examples")
    right("Anchor each severity level with example code -> consistent classification "
          "across files and runs.")

    tip("Replace vague modifiers with specific categories + severity anchors. A noisy "
        "category? Disable it while you fix it. (This logic powers scenario 5 CI review.)")


if __name__ == "__main__":
    main()
