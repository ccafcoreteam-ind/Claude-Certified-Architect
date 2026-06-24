"""
Domain 2 · Task 2.5 — Built-in tools: Read, Write, Edit, Bash, Grep, Glob.

THE BIG IDEA
============
Claude Code ships with built-in tools. The exam tests whether you pick the right one:

  Grep  -> searches file CONTENTS for patterns   (callers of a function, an error string)
  Glob  -> matches file PATHS/names by pattern    (**/*.test.tsx for every test file)
  Read  -> loads a full file's contents           (follow imports after Grep finds entry)
  Write -> writes a complete file                 (new files; rewrite when Edit can't anchor)
  Edit  -> targeted change via UNIQUE text match  (fails if anchor isn't unique)
  Bash  -> runs shell commands                    (build, test, git)

MEMORIZE: Grep = CONTENTS, Glob = file NAMES. Near-guaranteed question pattern.
Incremental exploration beats bulk reading: Grep to find entry points, THEN Read to follow
the threads. Never read every file upfront.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause


TASKS = [
    ("Find every file that calls process_refund()", "Grep",
     "You're searching file CONTENTS for a pattern."),
    ("Find every test file in the project", "Glob",
     "You're matching file NAMES/paths: **/*.test.tsx."),
    ("Open orders.py to follow its imports", "Read",
     "You need the full contents of a known file."),
    ("Create a brand-new module config.py", "Write",
     "Writing a complete new file."),
    ("Change one unique line in auth.py", "Edit",
     "Targeted change via a unique text anchor."),
    ("Run the test suite", "Bash",
     "Shell command: pytest / build / git."),
    ("Rewrite a file where the anchor text appears 5 times", "Read + Write",
     "Edit needs a UNIQUE anchor; when it can't find one, fall back to Read + Write."),
]


def quiz_answer(task):
    return next((ans, why) for t, ans, why in TASKS if t == task)


def main():
    banner("Domain 2 · Task 2.5", "Built-in tools — pick the right one")
    concept("Domain 2: Tool Design & MCP Integration (18%)",
            "Task 2.5 — Select and apply built-in tools (Read, Write, Edit, Bash, Grep, Glob) effectively",
            "Grep=contents, Glob=names; incremental exploration")

    h1("The decision table")
    rows = [
        ("Grep", "searches file CONTENTS", "callers of a function, an error message, imports"),
        ("Glob", "matches file PATHS/names", "files by name/extension, **/*.test.tsx"),
        ("Read", "loads a full file", "follow imports, trace logic after Grep finds entry"),
        ("Write", "writes a complete file", "new files; rewrite when Edit can't anchor"),
        ("Edit", "targeted change via UNIQUE match", "small precise edits (fails if not unique)"),
        ("Bash", "runs shell commands", "build, test, git, scripting"),
    ]
    for name, what, when in rows:
        kv(f"  {name:5}", f"{what:32} -> {when}")

    pause("the quiz")
    rule()
    h1("Pick-the-tool quiz")
    for task, ans, why in TASKS:
        h2(task)
        right(f"{ans}")
        note(f"    {why}")

    rule()
    h1("The contrast you WILL be tested on")
    code("Grep = file CONTENTS  (what's INSIDE files)\n"
         "Glob = file NAMES     (which files EXIST)", "memorize")

    rule()
    h1("Incremental exploration beats bulk reading")
    wrong("Reading every file upfront to 'understand the codebase'. Wasteful; blows context.")
    right("Grep to find entry points -> Read to follow the threads. For wrapper modules: "
          "first identify all exported names, then Grep each across the codebase.")

    tip("Grep = CONTENTS, Glob = NAMES. Edit needs a unique anchor; fallback is Read + Write. "
        "Explore incrementally, never bulk-read.")


if __name__ == "__main__":
    main()
