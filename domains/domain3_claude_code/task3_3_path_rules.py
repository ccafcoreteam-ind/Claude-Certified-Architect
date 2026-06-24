"""
Domain 3 · Task 3.3 — Path-specific rules (conditional convention loading).

THE BIG IDEA
============
Rule files in .claude/rules/ carry YAML frontmatter with a `paths` field of glob patterns.
The rule loads ONLY when Claude edits a file that matches — saving tokens and avoiding
irrelevant context.

WHY THIS BEATS directory CLAUDE.md for SCATTERED conventions (sample Q6): test files sit
next to the code they test, ALL OVER the codebase (Button.test.tsx beside Button.tsx). A
directory-bound CLAUDE.md can't cover them all; a single rule with
paths: ["**/*.test.tsx"] applies the testing conventions to EVERY test file regardless of
location — automatically and deterministically.

Analogy: path rules are motion-sensor lights (on exactly where you work). A monolithic
CLAUDE.md is leaving every light in the building on.
"""

import sys, pathlib, fnmatch
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause


# A tiny rule engine: each rule = (name, glob patterns, instruction)
RULES = [
    ("testing.md", ["**/*.test.tsx", "**/*.test.ts"],
     "Test names describe behavior; mock external services; cover empty/error cases first."),
    ("api-conventions.md", ["src/api/**/*"],
     "API handlers use async/await with structured error handling."),
    ("terraform.md", ["terraform/**/*"],
     "Pin provider versions; never hardcode secrets."),
]


def _match(pattern: str, path: str) -> bool:
    # '**' should cross directory boundaries; fnmatch treats '*' greedily enough for the
    # teaching cases when we normalize '**/' to match any prefix.
    if pattern.startswith("**/"):
        tail = pattern[3:]
        return fnmatch.fnmatch(path, tail) or fnmatch.fnmatch(path, "*/" + tail) \
            or fnmatch.fnmatch(path, pattern)
    return fnmatch.fnmatch(path, pattern)


def rules_for(path: str):
    loaded = []
    for name, patterns, instr in RULES:
        if any(_match(p, path) for p in patterns):
            loaded.append((name, instr))
    return loaded


def main():
    banner("Domain 3 · Task 3.3", "Path-specific rules — conventions that follow files")
    concept("Domain 3: Claude Code Configuration & Workflows (20%)",
            "Task 3.3 — Apply path-specific rules for conditional convention loading",
            "YAML frontmatter `paths` globs load rules only where they apply")

    h1("A complete, working rule file")
    code("---\n"
         'paths: ["**/*.test.tsx"]\n'
         "---\n"
         "When writing or editing tests:\n"
         "- Test names describe the behavior being verified\n"
         "- Mock external services; never call real APIs\n"
         "- Cover the empty-input and error cases first", ".claude/rules/testing.md")

    pause("the rule engine")
    rule()
    h1("Watch rules load by file path (simulated engine)")
    edits = [
        "src/components/Button.test.tsx",
        "src/api/orders/handler.ts",
        "terraform/prod/main.tf",
        "README.md",
    ]
    for path in edits:
        loaded = rules_for(path)
        h2(f"editing  {path}")
        if loaded:
            for name, instr in loaded:
                kv(f"  loaded {name}", instr)
        else:
            note("  (no path rules match — no extra context loaded)")

    rule()
    h1("Why this beats a directory CLAUDE.md for scattered conventions (sample Q6)")
    wrong("Per-directory CLAUDE.md: test files are EVERYWHERE next to their code, so no "
          "single directory file can cover them all.")
    wrong("One monolithic CLAUDE.md: relies on the model INFERRING which section applies.")
    wrong("Skills: need manual/optional invocation, not automatic application.")
    right("One .claude/rules/testing.md with paths: ['**/*.test.tsx'] applies to EVERY "
          "test file regardless of location — automatic and deterministic.")

    tip("'Conventions for files spread across many directories, applied automatically' "
        "=> path-scoped rules with glob patterns. It's the motion-sensor light.")


if __name__ == "__main__":
    main()
