"""
Domain 3 · Task 3.1 — CLAUDE.md hierarchy, scoping, and modular organization.

THE BIG IDEA
============
CLAUDE.md files are standing instructions Claude Code loads automatically at the start of
every session — the project's operating manual. They live at THREE levels, and the level
decides WHO they apply to:

  User      ~/.claude/CLAUDE.md        everything YOU do, every project     NOT shared
  Project   .claude/CLAUDE.md or root  everyone in this repo                shared (VCS)
  Directory CLAUDE.md in a subfolder   work within that subdirectory        shared, scoped

THE CLASSIC DIAGNOSTIC: a new teammate clones the repo and Claude ignores the team's
conventions. Why? They were written in someone's USER-level file (~/.claude/CLAUDE.md),
which never travels through version control. Fix: move them to PROJECT level.

Also: @import keeps CLAUDE.md modular; .claude/rules/ splits a monolith into topic files;
/memory shows which memory files are currently loaded (first move when behavior is flaky).
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause


def reaches_teammates(location: str) -> bool:
    """Anything inside the repo travels via version control; ~/ stays local."""
    return not location.strip().startswith("~/")


def main():
    banner("Domain 3 · Task 3.1", "CLAUDE.md hierarchy & scoping")
    concept("Domain 3: Claude Code Configuration & Workflows (20%)",
            "Task 3.1 — Configure CLAUDE.md files with appropriate hierarchy, scoping, and modular organization",
            "Level decides WHO the instructions apply to")

    h1("A real project CLAUDE.md is just plain text")
    code("# Project conventions\n"
         "- All currency amounts are stored in cents, never dollars\n"
         "- Every new function needs a matching test\n"
         "- Use British English in customer-facing text\n"
         "- Never modify files in /legacy without asking", "CLAUDE.md")

    rule()
    h1("The three levels")
    rows = [
        ("User", "~/.claude/CLAUDE.md", "everything YOU do, every project", "NO — personal"),
        ("Project", ".claude/CLAUDE.md or root CLAUDE.md", "everyone in this repo", "YES — via VCS"),
        ("Directory", "CLAUDE.md in a subfolder", "work in that subdirectory", "YES — but scoped"),
    ]
    for lvl, loc, applies, shared in rows:
        h2(f"{lvl}: {loc}")
        kv("  applies to", applies)
        kv("  shared with team?", shared)

    pause("the classic diagnostic")
    rule()
    h1("The classic diagnostic question")
    note("A new teammate clones the repo and Claude ignores the team's conventions. Why?")
    for loc in ["~/.claude/CLAUDE.md", ".claude/CLAUDE.md"]:
        ok = reaches_teammates(loc)
        kv(f"  conventions in {loc}", "REACH teammates ✓" if ok else "stay LOCAL ✗ (the bug)")
    wrong("Conventions written in ~/.claude/CLAUDE.md never travel through version control.")
    right("Move them to PROJECT level (.claude/CLAUDE.md or root CLAUDE.md).")

    rule()
    h1("Keeping it modular")
    code("# CLAUDE.md\n@import ./standards/testing.md\n@import ./standards/api.md",
         "@import syntax")
    note("- @import lets each package import only the standards relevant to it.")
    note("- .claude/rules/ is the alternative to one monolith: testing.md, "
         "api-conventions.md, deployment.md (see Task 3.3).")
    note("- /memory shows exactly which memory files are loaded — the first move when "
         "behavior is inconsistent across sessions.")

    tip("User (~/.claude, personal) · Project (repo, shared) · Directory (scoped). "
        "'Teammate doesn't get conventions' => they're at USER level; move to PROJECT.")
    note("\nSee runnable artifacts under domains/domain3_claude_code/examples/.")


if __name__ == "__main__":
    main()
