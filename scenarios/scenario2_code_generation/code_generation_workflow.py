"""
SCENARIO 2 — Code Generation with Claude Code
=============================================
A team adopting Claude Code for everyday work (generate, refactor, debug, document). This
scenario is about TEAM CONFIGURATION and judgment, not a live agent loop, so the demo walks
through the decisions the exam tests: D3 Claude Code Config, D5 Context & Reliability.

In ONE program:
  * shared vs personal config: what travels via version control (D3 T3.1, T3.2)
  * the "new teammate doesn't get conventions" diagnostic (D3 T3.1)
  * team /review command placement (D3 T3.2 / sample Q4)
  * path-scoped rules for scattered conventions (D3 T3.3 / sample Q6)
  * plan mode vs direct execution (D3 T3.4 / sample Q5)
  * iterative refinement: show-don't-describe, tests-as-feedback (D3 T3.5)

See real example artifacts under domains/domain3_claude_code/examples/.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause, analogy, pitfall


def shared_with_team(path: str) -> bool:
    return not path.strip().startswith("~/")


def plan_or_direct(task: str, files: int, architectural: bool):
    if architectural or files >= 5:
        return "PLAN MODE"
    return "DIRECT EXECUTION"


def main():
    banner("Scenario 2", "Code Generation with Claude Code — D3 · D5")
    concept("Scenario 2: Code Generation with Claude Code",
            "Slash commands · CLAUDE.md · plan mode vs direct execution",
            "Team enablement: what's shared vs personal, and when to plan")

    h1("What travels to teammates (version control) vs stays local")
    for path in [".claude/CLAUDE.md", ".claude/commands/review.md", ".claude/rules/testing.md",
                 "~/.claude/CLAUDE.md", "~/.claude/commands/scratch.md"]:
        kv(f"  {path}", "SHARED via VCS ✓" if shared_with_team(path) else "personal (local) ✗")

    pause("the diagnostic")
    rule()
    h1("Diagnostic: a new teammate clones the repo, Claude ignores team conventions")
    wrong("The conventions were written in ~/.claude/CLAUDE.md (user level) — that never "
          "travels through version control.")
    right("Move them to .claude/CLAUDE.md (project level) so every clone gets them.")

    rule()
    h1("Team /review command (sample Q4)")
    kv("  .claude/commands/review.md", "correct — version-controlled, everyone gets it")
    wrong("~/.claude/commands/ (personal), CLAUDE.md (not for commands), or a "
          "'.claude/config.json commands array' (doesn't exist).")

    pause("path rules")
    rule()
    h1("Scattered conventions → path-scoped rules (sample Q6)")
    note("React components, API handlers, DB models, and test files (next to their code, "
         "everywhere) each need different conventions.")
    right("Use .claude/rules/ with YAML `paths` globs (e.g., paths: ['**/*.test.tsx']). "
          "Applies automatically by file path, regardless of directory.")
    wrong("One monolithic CLAUDE.md (relies on inference) or per-directory CLAUDE.md "
          "(can't follow scattered test files).")

    pause("plan vs direct")
    rule()
    h1("Plan mode vs direct execution (sample Q5)")
    tasks = [
        ("Restructure monolith → microservices", 40, True),
        ("Migrate a library across 45+ files", 45, False),
        ("Fix a single-file bug with a clear stack trace", 1, False),
    ]
    for name, files, arch in tasks:
        kv(f"  {name}", plan_or_direct(name, files, arch))
    wrong("'Start direct, switch to plan if it gets hard' — the complexity is already "
          "STATED; that's a trap.")

    rule()
    h1("Iterative refinement habits (D3 T3.5)")
    note("- Show 2-3 input→output examples instead of prose when results are inconsistent.")
    note("- Write tests first; iterate by pasting the FAILURES as precise feedback.")
    note("- Let Claude interview YOU before building in an unfamiliar area.")
    note("- Batch INTERACTING fixes in one message; sequence INDEPENDENT ones.")

    rule()
    h1("Plain-language analogy & the common confusion")
    analogy('Rolling Claude Code out to a team is like writing the shop playbook: shared rules go on the wall (repo .claude/), personal preferences stay in your own locker (~/.claude/), and you measure before big rebuilds (plan mode).')
    pitfall("The recurring confusion is WHERE config lives and WHO it reaches. Anything in the repo travels to every teammate via git; anything under ~/ stays on your machine. 'Teammate did not get it' almost always means it was personal-scoped.")

    tip("This scenario is judgment about CONFIGURATION SCOPE and WORKFLOW MODE. Shared work "
        "→ repo (.claude/...); personal → ~/.claude/...; complexity stated → plan mode now.")
    note("\nExplore the real files: domains/domain3_claude_code/examples/")


if __name__ == "__main__":
    main()
