"""
Domain 1 · Task 1.7 — Session state, resumption, and forking.

THE BIG IDEA
============
  * `--resume <session-name>` continues a SPECIFIC named prior conversation — great for
    multi-day investigations.
  * `fork_session` branches a session into independent explorations from a shared baseline
    — e.g., compare two testing strategies without repeating the shared analysis.
  * STALE CONTEXT is dangerous. If files changed since last session, tell the resumed agent
    EXACTLY which files changed so it re-analyzes only those. If prior tool results are
    largely stale, start FRESH with a structured summary instead — more reliable than
    resuming a session full of outdated facts.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause


def decide(prior_context_valid: bool, files_changed, results_stale: bool, compare: bool):
    if compare:
        return ("fork_session into parallel branches",
                "Explore divergent approaches from one shared baseline.")
    if results_stale:
        return ("Start a NEW session seeded with a structured summary",
                "Resuming a session full of outdated facts is less reliable than a clean "
                "start with validated findings injected.")
    if prior_context_valid and files_changed:
        return (f"--resume the session; list changed files for targeted re-analysis: {files_changed}",
                "Prior context is mostly valid; only the changed files need re-reading.")
    return ("--resume the session as-is", "Nothing material changed.")


def main():
    banner("Domain 1 · Task 1.7", "Session state — resume, fork, or restart")
    concept("Domain 1: Agentic Architecture & Orchestration (27%)",
            "Task 1.7 — Manage session state, resumption, forking",
            "Resume vs fork vs fresh-start (driven by staleness)")

    h1("The three commands / moves")
    code("claude --resume nightly-investigation     # continue a named session\n"
         "fork_session(baseline)                     # branch from a shared analysis\n"
         "# fresh start + injected summary           # when prior results are stale", "cli")

    pause("the decision table")
    rule()
    h1("Decision table (memorize this shape)")
    scenarios = [
        dict(desc="Prior context valid; a few files changed",
             prior_context_valid=True, files_changed=["auth.py", "orders.py"],
             results_stale=False, compare=False),
        dict(desc="Prior tool results largely outdated",
             prior_context_valid=False, files_changed=[],
             results_stale=True, compare=False),
        dict(desc="Want to compare two divergent approaches from one analysis",
             prior_context_valid=True, files_changed=[],
             results_stale=False, compare=True),
    ]
    for sc in scenarios:
        desc = sc.pop("desc")
        move, why = decide(**sc)
        h2(desc)
        right(move)
        note(f"    why: {why}")

    rule()
    h1("Why stale context is dangerous")
    wrong("Resuming a multi-day session whose tool results no longer match the code on disk. "
          "The agent reasons over phantom facts.")
    right("Either (a) resume and explicitly name the changed files for targeted re-analysis, "
          "or (b) start fresh with a structured summary of validated findings.")

    tip("fork_session = same baseline, divergent branches. --resume = continue one thread. "
        "When results are stale, a fresh session + structured summary beats resuming.")


if __name__ == "__main__":
    main()
