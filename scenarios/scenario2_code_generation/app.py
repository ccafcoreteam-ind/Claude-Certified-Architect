"""
SCENARIO 2 app — Code Generation with Claude Code: workflow advisor (FUNCTIONAL)
===============================================================================
A working advisor: describe a change and it decides plan mode vs direct execution, where
the relevant config should live (shared vs personal), which Claude Code mechanism applies
(command / rule / skill), and — for "add a function" requests — generates a stub plus a
matching test per the project conventions. Domain 3 in action.

Run:
  python3 scenarios/scenario2_code_generation/app.py                         # scripted demo
  python3 scenarios/scenario2_code_generation/app.py -i                      # your own tasks
  python3 scenarios/scenario2_code_generation/app.py "migrate the API across 40 files"
"""
import sys, re, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, h1, h2, kv, note, rule, right, tip, code

PLAN_SIGNALS = ["refactor", "migrat", "architect", "restructure", "microservice", "redesign",
                "multiple files", "across", "dozens", "boundaries", "rename", "many files"]
DIRECT_SIGNALS = ["typo", "one line", "single file", "small", "rename a variable",
                  "add a check", "fix the", "bug", "one function"]


def advise(task):
    t = task.lower()
    nfiles = max([int(n) for n in re.findall(r"\b(\d+)\s*files?\b", t)] or [0])
    plan = nfiles >= 5 or any(s in t for s in PLAN_SIGNALS)
    direct = (not plan) and (nfiles == 1 or any(s in t for s in DIRECT_SIGNALS))
    mode = "PLAN MODE" if plan else ("DIRECT EXECUTION" if direct else "PLAN MODE (when unsure)")
    reasons = []
    if nfiles:
        reasons.append(f"{nfiles} file(s) mentioned")
    reasons += [f"signal: '{s}'" for s in PLAN_SIGNALS + DIRECT_SIGNALS if s in t][:3]

    mechanism = None
    if re.search(r"\b(review|lint|checklist|standard)\b", t):
        mechanism = (".claude/commands/<name>.md", "a reusable team slash command (version-controlled)")
    elif re.search(r"\btest|convention|style\b", t):
        mechanism = (".claude/rules/<topic>.md (paths: glob)", "path-scoped conventions that load by file type")
    elif re.search(r"\banaly|explore|generate boilerplate\b", t):
        mechanism = (".claude/skills/<name>/SKILL.md (context: fork)", "an on-demand skill in isolated context")

    scope = ("project (.claude/, shared via version control)"
             if re.search(r"\bteam|everyone|shared|repo\b", t)
             else "personal (~/.claude/) unless the whole team needs it")
    return {"mode": mode, "reasons": reasons or ["no strong signal — default to planning"],
            "mechanism": mechanism, "scope": scope}


def gen_stub(name):
    """Generate a stub + matching test per the repo CLAUDE.md conventions (cents; test required)."""
    fn = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_") or "do_thing"
    stub = (f"def {fn}(amount_cents: int) -> int:\n"
            f'    """TODO: implement {name}. Currency is integer cents, never dollars."""\n'
            f"    raise NotImplementedError\n")
    test = (f"def test_{fn}_handles_zero():\n"
            f"    # every new function needs a matching test (project convention)\n"
            f"    assert {fn}(0) == 0\n")
    return stub, test


def show(task):
    kv("task", task)
    a = advise(task)
    right(f"recommend: {a['mode']}")
    note("    reasons: " + "; ".join(a["reasons"]))
    kv("    config scope", a["scope"])
    if a["mechanism"]:
        kv("    mechanism", f"{a['mechanism'][0]}  ({a['mechanism'][1]})")
    m = re.search(r"add (?:a )?(?:function|helper|util(?:ity)?)\s+(?:called\s+|named\s+|to\s+)?([\w ]+)", task, re.I)
    if m:
        stub, test = gen_stub(m.group(1).strip())
        code(stub + "\n" + test, "generated stub + test")


SAMPLES = [
    "Restructure the monolith into microservices across dozens of files",
    "Fix the off-by-one bug in pager.py (single file, clear stack trace)",
    "Add a team /review command that runs our code-review checklist",
    "Add a function calculate_discount for the cart",
]


def interactive():
    banner("Scenario 2 — Workflow Advisor", "describe a change; 'quit' to exit")
    while True:
        try:
            task = input("\ntask> ").strip()
        except (EOFError, KeyboardInterrupt):
            print(); break
        if task.lower() in ("quit", "exit", "q"):
            break
        if task:
            show(task)


def main():
    args = sys.argv[1:]
    if any(a in ("-i", "--interactive") for a in args) and sys.stdin.isatty():
        interactive(); return
    free = [a for a in args if not a.startswith("-")]
    if free:
        banner("Scenario 2 — Workflow Advisor", "")
        show(" ".join(free)); return
    banner("Scenario 2 — Workflow Advisor (demo)", "plan-vs-direct + config scope, on real tasks")
    for s in SAMPLES:
        h2(s[:60])
        show(s)
    rule()
    tip("Stated complexity (many files / architectural) → plan mode now; small known fix → "
        "direct. Team-wide things live in .claude/ (shared); personal in ~/.claude/. Run -i.")


if __name__ == "__main__":
    main()
