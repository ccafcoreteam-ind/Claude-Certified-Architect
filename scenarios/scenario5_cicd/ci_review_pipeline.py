"""
SCENARIO 5 — Claude Code for Continuous Integration (CI/CD)
===========================================================
Claude Code wired into the automated pipeline that runs on every PR: automated reviews,
test generation, and PR feedback — running non-interactively with FEW false positives.
Demonstrates the concepts the exam attaches to this scenario: D3 Claude Code Config,
D4 Prompt Engineering & Structured Output.

In ONE program:
  * non-interactive -p flag; invented flags are distractors (D3 T3.6 / sample Q10)
  * structured JSON output for auto-posting PR comments (D3 T3.6 / D4 T4.3)
  * explicit criteria to cut false positives (D4 T4.1)
  * independent review instance vs self-review (D4 T4.6 / D3 T3.6)
  * multi-pass review for a large PR (D4 T4.6 / sample Q12)
  * report-only-new-findings on re-review; existing-tests-in-context (D3 T3.6)
"""

import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause


REVIEW_SCHEMA = {
    "type": "object",
    "properties": {
        "findings": {"type": "array", "items": {"type": "object", "properties": {
            "file": {"type": "string"}, "line": {"type": "integer"},
            "severity": {"type": "string", "enum": ["critical", "high", "low"]},
            "category": {"type": "string", "enum": ["bug", "security", "style"]},
            "issue": {"type": "string"}, "suggested_fix": {"type": "string"},
            "confidence": {"type": "number"},
        }}}
    },
}


def review_plan(num_files):
    return [f"pass {i+1}: {fn} (local)" for i, fn in
            enumerate([f"file{i+1}.py" for i in range(num_files)])] + \
           [f"pass {num_files+1}: cross-file integration"]


def main():
    banner("Scenario 5", "Claude Code for CI/CD — D3 · D4")
    concept("Scenario 5: Claude Code for Continuous Integration",
            "Automated review · test generation · PR feedback (no human at the keyboard)",
            "Non-interactive, structured, low false-positive")

    h1("Running non-interactively (sample Q10)")
    wrong('claude "Analyze this PR"   # HANGS — waiting for interactive input')
    code('claude -p "Analyze this PR" --output-format json --json-schema review.json',
         "the CI invocation")
    wrong("CLAUDE_HEADLESS / --batch don't exist; stdin redirection doesn't fix the syntax.")
    right("-p / --print = non-interactive: run, print, exit. Plus structured JSON so the "
          "pipeline auto-posts inline PR comments.")

    pause("structured findings")
    rule()
    h1("Structured findings schema (so a bot can post them)")
    code(json.dumps(REVIEW_SCHEMA, indent=2)[:520] + "\n  ...", "review schema")

    pause("false positives")
    rule()
    h1("Cut false positives with explicit criteria (D4 T4.1)")
    wrong('"Report anything that looks off" / "be conservative" — floods the PR with noise; '
          "developers start ignoring the bot entirely.")
    right("REPORT bugs and security issues with severity anchors; SKIP minor style. A noisy "
          "category? Disable it while you improve its prompt.")

    pause("independent review")
    rule()
    h1("Independent review instance, not self-review (D4 T4.6)")
    wrong("Letting the session that GENERATED the code review it — it rubber-stamps its own "
          "reasoning.")
    right("Spin up a FRESH instance with no generation context — it catches more issues.")

    pause("multi-pass")
    rule()
    h1("Large PR (14 files): multi-pass, not one big pass (sample Q12)")
    for step in review_plan(3):   # shape shown with 3 files
        kv("  ", step)
    wrong("One pass over all 14 files → uneven depth, missed bugs, contradictory findings. "
          "A bigger context window does NOT fix attention quality.")
    right("Per-file local passes + one integration pass.")

    rule()
    h1("Re-review discipline (D3 T3.6)")
    note("- On RE-RUN after new commits: include prior findings; instruct Claude to report "
         "only NEW/unaddressed issues → no duplicate comments.")
    note("- For TEST GENERATION: provide existing test files so it doesn't duplicate covered "
         "scenarios; put testing standards & fixtures in CLAUDE.md.")

    tip("-p for non-interactive (the #1 CI gotcha). Structured JSON for auto-posting. "
        "Explicit criteria + fresh-instance review + multi-pass = actionable, low-noise "
        "feedback. That's D3 + D4.")


if __name__ == "__main__":
    main()
