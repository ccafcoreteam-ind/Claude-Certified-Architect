"""
Domain 3 · Task 3.6 — Claude Code in CI/CD pipelines.

THE BIG IDEA
============
Running Claude Code with NO human at the keyboard needs specific flags and context discipline:

  -p / --print                       Non-interactive: process prompt, print, exit.
                                     WITHOUT it, the CI job HANGS forever (sample Q10).
                                     (CLAUDE_HEADLESS and --batch DO NOT EXIST.)
  --output-format json --json-schema Force machine-parseable findings so the pipeline can
                                     auto-post them as inline PR comments.
  CLAUDE.md in CI                    Supplies project context (testing standards, fixture
                                     conventions, review criteria) -> better output.
  Independent review instance        The session that GENERATED code is biased reviewing it;
                                     a fresh instance catches more issues.
  Prior findings on re-review        Include earlier findings; report only NEW/unaddressed
                                     issues -> prevents duplicate comments.
  Existing tests in context          So test generation doesn't duplicate covered scenarios.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause


def main():
    banner("Domain 3 · Task 3.6", "Claude Code in CI/CD")
    concept("Domain 3: Claude Code Configuration & Workflows (20%)",
            "Task 3.6 — Integrate Claude Code into CI/CD pipelines",
            "-p for non-interactive; structured output; independent review")

    h1("The hang (sample Q10) and its fix")
    wrong('claude "Analyze this PR for security issues"   # CI job HANGS waiting for input')
    code('claude -p "Analyze this PR for security issues"  # -p/--print: run, print, exit',
         "the fix")
    wrong("CLAUDE_HEADLESS=true and --batch DON'T EXIST. Redirecting stdin from /dev/null "
          "doesn't address Claude Code's command syntax.")
    right("Use the -p (or --print) flag. It's the documented non-interactive mode.")

    pause("structured output")
    rule()
    h1("Structured output for automated PR comments")
    code('claude -p "Review the diff" \\\n'
         '  --output-format json \\\n'
         '  --json-schema review_schema.json', "machine-parseable findings")
    note("The pipeline parses the JSON and posts each finding as an inline PR comment.")

    rule()
    h1("Context discipline in CI")
    kv("CLAUDE.md in CI", "supplies testing standards, fixtures, review criteria -> better output")
    kv("Independent review instance", "fresh session (no generation bias) catches more issues")
    kv("Prior findings on re-review", "include them; report only NEW/unaddressed -> no dupes")
    kv("Existing tests in context", "so generated tests don't duplicate covered scenarios")

    rule()
    h1("Why a FRESH instance reviews better")
    wrong("Reviewing code in the SAME session that generated it — it carries its own "
          "reasoning and won't question its own decisions.")
    right("Spin up an INDEPENDENT instance with no generation context. (See Task 4.6.)")

    tip("-p / --print = non-interactive (the #1 CI gotcha). --output-format json + "
        "--json-schema = structured findings. Invented flags (CLAUDE_HEADLESS, --batch) "
        "are always distractors — eliminate on sight.")


if __name__ == "__main__":
    main()
